var pendingData;
var lastDisplayedDatetime;
// if refresh requests return more than this, we don't know exact number of new messages
var maxObjects = 20;
var refreshTimeout = 5000;

// ISO 8601 date format function from:
// https://developer.mozilla.org/en/Core_JavaScript_1.5_Reference:Global_Objects:Date#Example:_ISO_8601_formatted_dates
function ISODateString(d){
  function pad(n){return n<10 ? '0'+n : n}
  return d.getUTCFullYear()+'-'
      + pad(d.getUTCMonth()+1)+'-'
      + pad(d.getUTCDate())+'T'
      + pad(d.getUTCHours())+':'
      + pad(d.getUTCMinutes())+':'
      + pad(d.getUTCSeconds())+'Z'
}

var requestLogMessages = function(update) {
    var formData = $.map($('.filters').serializeArray(), function(n) {
        if (n.value == "") {
            return null;
        }
        return n;
    });

    if (! update) { // this is a refresh request, so we should only match new log messages
        if (typeof lastDisplayedDatetime !== 'undefined') {
            formData.push({ 'name': 'datetime__gte', 'value': lastDisplayedDatetime });
        }
    }

    var url = "/api/logmessages/?" + $.param(formData);
    $.getJSON(url,
        function(data,textStatus,jqXHR) {
            if (update) {
                $(".content .table tbody").html(ich.log_messages(data));
                lastDisplayedDatetime = ISODateString(new Date());
                $('#refresh_notice').hide();
            } else {
                pendingData = data;
                var count = data['objects'].length;
                if (count > 0) {
                    if (count >= maxObjects) {
                        count = count + "+";
                    }
                    $('#refresh_notice').html(ich.refresh_notice_template({ 'count': count }));
                    $('#refresh_notice').show();
                }
                window.setTimeout(function() { requestLogMessages(false); }, refreshTimeout);
            }
        }
    );
}

$(document).ready(function() {
    var updateHandler = function() { requestLogMessages(true); };
    $('.filters input, .filters select').change(updateHandler);
    $('.filters .search-query').keypress(updateHandler);
    $('form.filters').submit(function(event){
        requestLogMessages(true);
        event.preventDefault();
    });
    requestLogMessages(true);
    window.setTimeout(function() { requestLogMessages(false); }, refreshTimeout);
});
