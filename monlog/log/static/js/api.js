var requestLogmessages = function() {
    var formData = $.map($('.filters').serializeArray(), function(n) {
        if (n.value == "") {
            return null;
        }
        return n;
    });

    var url = "/api/logmessages/?" + $.param(formData);
    $.getJSON(url,
        function(data,textStatus,jqXHR) {
            $(".content .table tbody").html(ich.log_messages(data));
        }
    );
}

$(window).load(function() {
    $('.filters input, .filters select').change(requestLogmessages);
    $('.filters .search-query').keypress(requestLogmessages);
    requestLogmessages();
});
