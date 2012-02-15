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
        console.log($(".filters").serialize());
    });
    requestLogmessages();
});
