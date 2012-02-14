function collectFormSeverities() {
    var selectedSeverities = [];
    $('input:checkbox[name=severity]:checked').each(
        function(index) {
            selectedSeverities.push($(this).val());
        }
    );
    return selectedSeverities;
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
        collectFormSeverities();
    });
    requestLogmessages();
    collectFormSeverities();
});
