var requestLogmessages = function() {
    var formData = $('.filters').serialize();

    $.getJSON("/api/logmessages/?" + formData,
        function(data,textStatus,jqXHR) {
            console.log(data);
        }
    );
}

$(window).load(function() {
    $('.filters input, select').change(requestLogmessages);
    $('.filters .search-query').keypress(requestLogmessages);
    requestLogmessages();
});
