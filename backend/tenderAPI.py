# imports
import os

from flask import Flask, request, json, redirect, session, render_template
from flask import flash
from flaskext.mysql import MySQL
from flask_mail import Mail
import re
from werkzeug.utils import secure_filename
import random

# intializations
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
app.config[
    'UPLOAD_FOLDER'] = '/Users/parthparekh/Documents/Projects/Websites/Tender System/tender/Project Files/static/file/'
app.config['ALLOWED_EXTENSIONS'] = set(['pdf'])

mysql = MySQL()

# configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '12345678'
app.config['MYSQL_DATABASE_DB'] = 'tender_system'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='',
    MAIL_PASSWORD=''
)
mysql.init_app(app)
conn = mysql.connect()
mail = Mail(app)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~User Login & Sign-Up Methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sign_up.html', methods=['GET', 'POST'])
def new_user():
    error = None
    if request.method == 'POST':
        if request.form['inputEmail'] == '' or request.form['inputPassword'] == '' \
                or request.form['inputName'] == '' or request.form['inputContact'] == '':
            error = 'Please enter values.'
        else:
            cur = conn.cursor()
            name = request.form['inputName']
            password = request.form['inputPassword']
            print(password)
            email = request.form['inputEmail']
            contact = request.form['inputContact']
            typeid = request.form['inputUserType']
            typeid = int(typeid)
            cur.callproc('sign_up', (name, password, email, contact, typeid))
            if len(cur.fetchall()) is 0:
                cur = conn.cursor()
                cur.execute('SELECT user_id, user_type FROM tender_system.user WHERE email_id = "' + email + '"')
                temp = cur.fetchone()
                user_id, type_id = int(temp[0]), int(temp[1])
                conn.commit()
                cur.close()
                session['email'] = email
                session['user_id'] = user_id
                session['type'] = type_id
                flash("You have successfully signed up! Please log in to continue.")
                return redirect(location='log_in.html')
            else:
                cur.close()
                error = "You have already signed in. Please log in to continue."
    return render_template('sign_up.html', error=error)


@app.route('/log_in.html', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['inputEmail'] == '' or request.form['inputPassword'] == '':
            error = 'Invalid username or password. Please try again!'
        else:
            cur = conn.cursor()
            email = request.form['inputEmail']
            password = request.form['inputPassword']
            type = request.form['inputUserType']
            print(type)
            cur.execute('SELECT password FROM user WHERE email_id="' + email + '"')
            temp = cur.fetchone()
            if temp is None or len(temp) is 0:
                error = 'Invalid username or password. Please try again!'
            elif password == temp[0]:
                cur.execute('SELECT user_id FROM tender_system.user WHERE email_id = "' + email + '"')
                temp = cur.fetchone()
                user_id = int(temp[0])
                conn.commit()
                cur.close()
                session['email'] = email
                session['user_id'] = user_id
                session['type'] = type
                flash("You have successfully logged in!")
                return render_template('project_page.html')
            else:
                cur.close()

    return render_template('log_in.html', error=error)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Submission of parameters~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route('/submit_parameters.html', methods=['GET', 'POST'])
def upload_file():
    if 'email' not in session:
        return redirect('log_in.html')
    if request.method == 'POST':
        project_id = str(session['project_id'])
        user_id = str(session['user_id'])
        cur = conn.cursor()
        cur.execute('SELECT parameter_name FROM parameter WHERE project_id = "' + str(project_id) + '"')
        parameters = cur.fetchall()
        cur.execute(
            'SELECT tender_id FROM tender WHERE project_id = "' + project_id + '"AND user_id = "' + user_id + '"')
        tender_id = cur.fetchone()[0]
        file_path = "P_" + project_id + "_t_" + str(tender_id) + "_p_"
        for parameter in parameters:
            parameter = str(parameter)
            parameter = parameter[2:len(parameter) - 3]
            print(parameter)
            cur.execute('SELECT parameter_id, parameter_type FROM parameter WHERE parameter_name ="' + parameter + '"')
            id = cur.fetchone()
            if id[1] == 'blob':
                # value = bytearray(request.form[parameter], encoding='utf-8')
                value = request.files[parameter]
                file_name = file_path + str(id[0]) + ".pdf"
                value.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))

                # with open(file_name, mode='wb+') as f:
                #     f.write(value)

                cur.callproc('add_parameter', (tender_id, user_id, id[0], project_id, "static/file/" + file_name))
            else:
                value = request.form[parameter]
                cur.callproc('add_parameter', (tender_id, user_id, id[0], project_id, value))
        conn.commit()
        message = "Thank You for submitting your values. The examiner will decide the final result and let you know!"
        return render_template("project_page.html", message=message)
    else:
        message = "Please try again!"
        return render_template('parameters.html', message=message)


@app.route('/getProjects.html', methods=['GET'])
def get_projects():
    if 'email' not in session.keys():
        return redirect('log_in.html')
    cur = conn.cursor()
    projects = {}
    cur.execute('SELECT * FROM project')
    temp = cur.fetchall()
    if len(temp) is 0:
        return json.dumps({'message': 'No Projects Found!'})
    else:
        for project in temp:
            projects[project[0]] = project[1]

        return json.dumps(projects)

        # for project in temp:


@app.route('/save_project.html', methods=['POST'])
def save_project():
    project_name = request.form['projectSelector']
    cur = conn.cursor()
    cur.execute("SELECT project_id FROM project WHERE project_name = '" + project_name + "'")
    project_id = cur.fetchone()[0]
    session['project_id'] = project_id
    if int(session['type']) == 1:
        project_id = str(session['project_id'])
        user_id = str(session['user_id'])
        cur.execute("SELECT tender_id FROM tender WHERE project_id ='" + project_id + "'AND user_id ='" + user_id + "'")
        if len(cur.fetchall()) == 0:
            cur.execute("INSERT INTO tender(project_id, user_id) VALUES('" + project_id + "', '" + user_id + "')")
            conn.commit()
        session['first_time'] = 1
        return render_template('parameters.html')
    else:
        return render_template('rate_parameters.html')


@app.route('/getTenders.html', methods=['GET'])
def get_tenders():
    if 'email' not in session:
        return redirect('log_in.html')
    cur = conn.cursor()
    project_id = 1
    tenders = {}
    cur.execute(
        "SELECT tender_id, name FROM tender t, user u WHERE t.user_id = u.user_id AND project_id =" + project_id)
    temp = cur.fetchall()
    if len(temp) is 0:
        return json.dumps({'message': 'No Projects Found!'})
    else:
        for tender in temp:
            tenders[tender[0]] = tender[1]

        return json.dumps(tenders)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Rating of parameters~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@app.route('/logout.html', methods=['GET', 'POST'])
def logout():
    session.clear()
    return render_template('index.html')


@app.route('/getParams.html', methods=['GET', 'POST'])
def get_params():
    param = []
    type = []
    param.append(request.form['parameter1'])
    param.append(request.form['parameter2'])

    project_id = str(session['project_id'])

    curr = conn.cursor()
    curr.execute(
        "SELECT parameter_name, parameter_type FROM parameter WHERE project_id = '" + project_id + "' AND (parameter_id = '" +
        param[
            0] + "'OR parameter_id = '" + param[1] + "')")
    names = curr.fetchall()
    parameter_list = []
    parameters = {}
    param_names = []

    for i in range(2):
        if i == len(names):
            break
        parameter_dict = {}
        tender_list = []
        param_names.append(re.sub('[^A-Za-z0-9\.]+', ' ', names[i][0]))
        type.append(names[i][1])
        curr.execute(
            'SELECT tender_id,value_string FROM value WHERE parameter_id = "' + param[
                i] + '" AND project_id = "' + project_id + '"')
        tenders = curr.fetchall()
        for tender in tenders:
            parameter_dict['tender_id'] = tender[0]
            if type[i] == 'double':
                parameter_dict['value'] = float(tender[1])
            else:
                parameter_dict['value'] = str(tender[1])
            items = list(parameter_dict.items())
            random.shuffle(items)
            tender_list.append(parameter_dict)
            parameter_dict = dict()
        parameters['name'] = param_names[i]
        parameters['value'] = tender_list
        parameter_list.append(parameters)
        parameters = dict()

    json_value = json.dumps(parameter_list)
    return json_value


@app.route('/rateParameters.html', methods=['GET', 'POST'])
def rate_parameters():
    if request.method == 'POST':
        project_id = str(session['project_id'])
        cur = conn.cursor()
        # if the no of tenders is stored in the session itself,
        # then the below query has no use , hence commented
        cur.execute('SELECT tender_id FROM tender WHERE project_id = "' + project_id + '"')
        tenders = cur.fetchall()
        no_of_tenders = len(tenders)
        # no_of_tenders = session['no_of_tenders']                                                                                                           # number of tenders for a particular project which can be extracted from session
        for i in range(1, 3):  # for 2 parameters per page
            parameter_id = request.form[
                'parameter' + str(
                    i) + "_id"]  # extract the parameter id value for tags parameter1 and parameter2 in HTML page(give "values" of these tags as the parameter id  of that parameter
            for j in range(1, no_of_tenders + 1):
                tender_id = request.form['tender' + str(j)]
                rating = request.form['tender' + str(j) + '_rating']
                result = cur.execute(
                    'UPDATE value SET value_rating = "' + rating + '" WHERE parameter_id = "' + parameter_id + '" AND tender_id = "' + tender_id + '"')
                if result == 0:
                    return "no"
        conn.commit()
        return "yes"


@app.route('/calculateScore.html', methods=[
    'GET'])  # for calculating final scores, a separate button "Calculate Scores" can be provided on the html page for the examiner
def calculate_scores():
    cur = conn.cursor()
    project_id = str(session['project_id'])
    cur.execute('SELECT tender_id FROM tender WHERE project_id = "' + project_id + '"')
    tenders = cur.fetchall()
    for tender in tenders:
        cur.execute('SELECT parameter_id,value_rating FROM value WHERE tender_id = "' + str(tender[0]) + '"')
        parameters = cur.fetchall()
        sum = 0
        for parameter in parameters:
            cur.execute('SELECT weight FROM parameter WHERE parameter_id = "' + str(
                parameter[0]) + '"')  # taking the weight from parameter table to calculate weighted average
            weight = cur.fetchone()
            sum = sum + weight[0] * int(parameter[1])
        final_score = sum / len(parameters)
        cur.execute(
            'UPDATE tender SET final_rating = "' + str(final_score) + '" WHERE tender_id = "' + str(tender[0]) + '"')
    conn.commit()
    return "yes"


@app.route('/selectWinner.html', methods=['GET'])
def select_winner():
    cur = conn.cursor()
    project_id = str(session['project_id'])
    cur.execute('SELECT MAX(final_rating) FROM tender  WHERE project_id = "' + project_id + '"')
    rating = cur.fetchone()
    cur.execute('UPDATE tender AS t  SET selected = "YES" WHERE t.final_rating = "' + str(rating[0]) + '"')
    cur.execute('UPDATE tender AS t  SET selected = "NO" WHERE t.final_rating <> "' + str(rating[0]) + '"')

    cur.execute('SELECT tender_id,selected FROM tender WHERE project_id = "' + project_id + '"')
    tenders = cur.fetchall()
    # for tender in tenders:
    #     if tender[1] == "":
    #         cur.execute('UPDATE tender SET selected = "NO" WHERE tender_id = "' + str(tender[0]) + '"')
    conn.commit()
    cur.execute(
        "SELECT name, final_rating FROM user AS u, tender AS t WHERE t.user_id = u.user_id AND t.selected = 'YES'")
    user = cur.fetchone()
    if len(user) == 2:
        return str(user[0]) +" with the rating of " +  str(user[1])
    else:
        return "No One"


@app.route('/getParameters.html', methods=['POST'])
def get_parameters():
    if 'email' not in session:
        return redirect('log_in.html')

    cur = conn.cursor()
    project_id = session['project_id']

    cur.callproc('get_parameters_by_project', (project_id,))
    parameters = cur.fetchall()
    dict = {}

    for parameter in parameters:
        parameter_dict = {}
        cur.execute('SELECT tender_id,value_string FROM value WHERE parameter_id = "' + str(parameter[0]) + '"')
        tenders = cur.fetchall()
        for tender in tenders:
            parameter_dict[tender[0]] = tender[1]
        dict[parameter[1]] = parameter_dict
    return json.dumps(dict)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost')
