function reload_page(){
    window.location.reload()
}

$("#student-assignments").click(function(){
    var student = $("#student_id").val();

    checked = [];
    $("input:checkbox[name=exempt]:checked").each(function(){
        checked.push($(this).val());
    });

    query_params = "?checked="+checked;
    console.log(query_params)

    $.ajax({
        url: '/api/v1/exempt-student/'+student+'/'+query_params,
        success: function(){
            alert("student have been exempted");
            reload_page();
        },
        error: function(){
            alert("something went wrong");
        }
    })
})



