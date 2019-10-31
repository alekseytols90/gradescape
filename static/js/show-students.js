var student_id = $("#student_id");
var row = undefined;
var counter = 0;

$(document).ready(function() {
    $("#show-students tbody").empty();
        var show_students = $("#show-students");
        console.log(show_students);
        show_students.DataTable({
            "processing": true,
            "serverSide": false,
            "ajax": {
                "url": SHOW_STUDENTS,
                dataSrc: "",
            },
            "columns": [
                {
                    "title": "ID",
                    "data": "id",
                    render: function(row){
                        return `<a href="/assignment/student-assignment/${row}">${row}</a>`
                    }
                },
                {
                    "title": "First Name",
                    "data": "first_name",
                },
                {
                    "title": "Last Name",
                    "data": "last_name",
                },
                {
                    "title": "Curriculum",
                    "data": "curriculum",
                },
                {
                    "title": "Subject",
                    "data": "subject",
                },
                {
                    "title": "Status",
                    "render": function(data, type, row){
                        return `<p>${row.status[row.id-1]}</p>`
                    }
                },
            ],
        });
});
