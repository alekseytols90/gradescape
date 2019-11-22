$(document).ready(function() {
    //https://stackoverflow.com/a/30578065
    var filterSelectOptions = function($select, callback) {
        var options = null,
            dataOptions = $select.data('options');

        if (typeof dataOptions === 'undefined') {
            options = [];
            $select.children('option').each(function() {
                var $this = $(this);
                options.push({value: $this.val(), text: $this.text()});
            });
            $select.data('options', options);
        } else {
            options = dataOptions;
        }

        $select.empty();

        $.each(options, function(i) {
            var option = options[i];
            if(callback(option)) {
                $select.append(
                    $('<option/>').text(option.text).val(option.value)
                );
            }
        });
    };

    $("#id_semester").change(function(e){ 
        var sem = $(this).val();
        if (sem == "1") {
            filterSelectOptions($("#id_quarter"), function(e) {
                return e.value == "1" || e.value == "2"; });
        } else if (sem == "2") {
            filterSelectOptions($("#id_quarter"), function(e) { 
                return e.value == "3" || e.value == "4"; });
        }
        $("#id_quarter").change();
    });
    $("#id_quarter").change(function(e){ 
        var q = $(this).val();
        if (q == "1") {
            filterSelectOptions($("#id_week"), function(e) { 
                return parseInt(e.value) >= 1 && parseInt(e.value) <= 9; });
        } else if (q == "2") {
            filterSelectOptions($("#id_week"), function(e) { 
                return parseInt(e.value) >= 10 && parseInt(e.value) <= 18; });
        } else if (q == "3") {
            filterSelectOptions($("#id_week"), function(e) { 
                return parseInt(e.value) >= 19 && parseInt(e.value) <= 27; });
        } else if (q == "4") {
            filterSelectOptions($("#id_week"), function(e) { 
                return parseInt(e.value) >= 28 && parseInt(e.value) <= 36; });
        }
    });
    $("#id_semester").change();
});

