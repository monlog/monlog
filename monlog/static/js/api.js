var pendingData;
var displayedIds;
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

var displayLogMessages = function(data) {
    var newDisplayedIds = [];
    $.each(data['objects'], function(i, el) {
        if (typeof displayedIds == 'undefined' || $.inArray(el['id'], displayedIds) !== -1) {
            // this is an old log message
            el['old'] = true;
        }
        newDisplayedIds.push(el['id']);
    });
    $(".content .table tbody").html(ich.log_messages(data));
    lastDisplayedDatetime = ISODateString(new Date());
    displayedIds = newDisplayedIds;
    $('#refresh_notice').hide();
};

var requestLogMessages = function(update, was_refresh) {
    var formData = $.map($('.filters').serializeArray(), function(n) {
        if (n.value == "") {
            return null;
        }
        return n;
    });

    if (was_refresh) {
        $('.content table').addClass('was-refreshed');
    } else if (update) {
        $('.content table').removeClass('was-refreshed');
    }

    if (! update) { // this is a refresh request, so we should only match new log messages
        if (typeof lastDisplayedDatetime !== 'undefined') {
            formData.push({ 'name': 'add_datetime__gte', 'value': lastDisplayedDatetime });
        }
    } else {
        $("#loading_indicator").fadeIn(300);
    }

    var url = "/api/logmessages/?" + $.param(formData);
    $.getJSON(url,
        function(data,textStatus,jqXHR) {
            if (update) {
                displayLogMessages(data, true);
                $("#loading_indicator").fadeOut(300);
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
};

var refreshClickHandler = function(event) {
    requestLogMessages(true, true);
    $('#refresh_notice').hide();
};

var delay = (function() {
    var timer = 0;
    return function(callback, ms) {
        window.clearTimeout (timer)
        timer = window.setTimeout(callback, ms);
    };
})();

$(document).ready(function() {
    var updateHandler = function() { requestLogMessages(true, false); };
    $('.filters input, .filters select').change(updateHandler);

    // needs a timeout so it doesn't trigger a search for every key press right away
    $('.search-query').keyup(function() {
        delay(updateHandler,100) 
    });
    $('form.filters').submit(function(event){
        requestLogMessages(true, false);
        event.preventDefault();
    });
    $('#refresh_notice').bind('click', refreshClickHandler);
    requestLogMessages(true, false);
    window.setTimeout(function() { requestLogMessages(false, false); }, refreshTimeout);
});
