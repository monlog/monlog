function collectValuesFromCheckboxes(name) {
    var selected = [];
    $('input:checkbox[name=' + name + ']:checked').each(
        function(index) {
            selected.push($(this).val());
        }
    );
    return selected;
}

function collectValuesFromSelectList(id) {
    var selected = [];
    $(id + ' :selected').each(
        function(index) {
            selected.push($(this).text());
        }
    );
    return selected;
}

function requestLogmessages() {
    $.get("http://localhost:8000/api/logmessages/",{ "format" : "json" },
        function(data,textStatus,jqXHR) {
            console.log(data);
        }
    );
}

$(window).load(function() {
    $(".filters input, select").change(function() {
        // Do something when input changes
    });
    requestLogmessages();
});
