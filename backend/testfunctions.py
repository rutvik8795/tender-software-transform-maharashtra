from flask import Flask, request, json, redirect, session,render_template
from flaskext.mysql import MySQL
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint


# intializations
app = Flask(__name__)
mysql = MySQL()

# configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'rutvik123'
app.config['MYSQL_DATABASE_DB'] = 'tender_system'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL= True,
    MAIL_USERNAME='',
    MAIL_PASSWORD=''
)
mysql.init_app(app)
conn = mysql.connect()
mail = Mail(app)


cur = conn.cursor()
cur.execute('select parameter_name from parameter')
temp= cur.fetchall()
for parameter in temp:
    parameter = str(parameter)
    parameter = parameter[2:len(parameter) - 3]
    print(parameter)


cur = conn.cursor()
cur.callproc('get_parameters_by_project', (1))
parameters = cur.fetchall()
for parameter in parameters:
    print(parameter[0])