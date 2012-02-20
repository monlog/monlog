var requestLogmessages = function() {
    var formData = $.map($('.filters').serializeArray(), function(n) {
        if (n.value == "") {
            return null;
        }
        return n;
    });
    
    var url = "/api/logmessages/?" + $.param(formData);
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
