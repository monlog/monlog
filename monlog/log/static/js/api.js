var requestLogMessages = function() {
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

$(document).ready(function() {
    $('.filters input, .filters select').change(requestLogMessages);
    $('.filters .search-query').keypress(requestLogMessages);
    $('form.filters').submit(function(event){
        requestLogMessages();
        event.preventDefault();
    });
    requestLogMessages();
});
