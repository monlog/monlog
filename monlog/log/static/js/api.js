var requestLogmessages = function() {
    var formData = $('.filters').serialize();
    var url = "/api/logmessages/?" + formData;
    console.log(url);
    $.getJSON(url,
        function(data,textStatus,jqXHR) {
            console.log(data);
        }
    );
}

$(window).load(function() {
    $('.filters input, .filters select').change(requestLogmessages);
    $('.filters .search-query').keypress(requestLogmessages);
    requestLogmessages();
});
