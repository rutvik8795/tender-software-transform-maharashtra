/**
 * Created by parthparekh on 16/04/17.
 */
parameter1 = $("#parameter1_id").text();
type1 = $("#type1").text();

parameter2 = $("#parameter2_id").text();
type2 = $("#type2").text();

function getParams() {
    parameter1 = $("#parameter1_id").text();

    parameter2 = $("#parameter2_id").text();
    data = {
        'parameter1': parameter1,
        'parameter2': parameter2
    };

    $.ajax({
        type: 'post',
        url: '/getParams.html',
        data: data,
        dataType: 'json',
        success: function (result) {
            console.log(result);
            var tender_list1 = result[0].value;
            var tender_list2 = result[1].value;
            $("#table1_name").text(result[0].name);
            $("#table2_name").text(result[1].name);
            populateTables(tender_list1, "#t1_body", 1);
            populateTables(tender_list2, '#t2_body', 2);
        }
    });
}


function populateTables(tender_list, t_body, t_no) {
    var count = 1;
    for (var i in tender_list) {
        console.log('btn_' + t_no + tender_list[i].tender_id);

        if (typeof tender_list[i].value == 'string') {
            $(t_body).append('<tr><td>' + count + '</td>' +
                '<td id="tender' + tender_list[i].tender_id + '">' + tender_list[i].tender_id + '</td>' +
                '<td><button class="btn btn-info" id="btn_' + t_no + tender_list[i].tender_id + '">View File</button></td>' +
                '<td><select id="tender' + tender_list[i].tender_id + 'rating">' +
                '<option>1</option>' +
                '<option>2</option>' +
                '<option>3</option>' +
                '<option>4</option>' +
                '<option>5</option>' +
                '</select></td></tr>');


        }
        else {
            $(t_body).append('<tr><td>' + count + '</td>' +
                '<td id="tender' + tender_list[i].tender_id + '">' + tender_list[i].tender_id + '</td>' +
                '<td>' + tender_list[i].value + '</td>' +
                '<td><select id="tender' + tender_list[i].tender_id + 'rating">' +
                '<option>1</option>' +
                '<option>2</option>' +
                '<option>3</option>' +
                '<option>4</option>' +
                '<option>5</option>' +
                '</select></td></tr>');
        }
        count = count + 1;
    }
}

function viewFile() {
    $("#t2_body").on('click', '#btn_21', function () {
        console.log("View File button called");
        PDFObject.embed("../static/img/SC Codes and Outputs.pdf");
    });
    $("#t2_body").on('click', '#btn_22', function () {
        console.log("View File button called");
        PDFObject.embed("../static/img/SC Codes and Outputs.pdf");
    });

    $('#t1_body').on('click', '#btn_11', function () {
        console.log("View File button called");
        PDFObject.embed("../static/img/SC Codes and Outputs.pdf");
    });
    $("#t1_body").on('click', '#btn_12', function () {
        console.log("View File button called");
        PDFObject.embed("../static/img/SC Codes and Outputs.pdf");
    });
}

$("#next_btn").click(function () {
    $('#previous_btn').removeAttr('disabled');
    if (parameter1 >= 14) {
        $(this).button('disabled', true);
    }
    else {
        parameter1 = parseInt(parameter1) + 2;
        parameter2 = parseInt(parameter2) + 2;
        $("#parameter1_id").text(parameter1);
        $("#parameter2_id").text(parameter2);

        $("#t1_body").empty();
        $("#t2_body").empty();

        getParams();
    }
});


$("#previous_btn").click(function () {
    if (parameter1 < 2) {
        $(this).button('disabled', true);
    }
    else {
        parameter1 = parseInt(parameter1) - 2;
        parameter2 = parseInt(parameter2) - 2;

        $("#parameter1_id").text(parameter1);
        $("#parameter2_id").text(parameter2);

        $("#t1_body").empty();
        $("#t2_body").empty();
        getParams();
    }
});

getParams();
viewFile();