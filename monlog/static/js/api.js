var streamingMode = true;
var timeoutTime = 5000;
var displayedIds;
var lastDisplayedDatetime;

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

var getFormData = function() {
    return $.map($('.filters').serializeArray(), function(n) {
        if (n.value == "") {
            return null;
        }
        return n;
    });
};



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
    displayedIds = newDisplayedIds;

    lastDisplayedDatetime = ISODateString(new Date());
};

var updateLogTable = function(data) {
    displayLogMessages(data);
};

var requestLogMessages = function(formData,callback) {
    $("#loading_indicator").fadeIn(300);

    var url = "/api/logmessages/?" + $.param(formData);
    $.getJSON(url, function(data,textStatus,jqXHR) {
        callback(data);
        $("#loading_indicator").fadeOut(300);
    });
};

var handleTimeout = function() {
    if (streamingMode) {
        // Auto update table
        requestLogMessages(getFormData(),updateLogTable);
    } else {
        // Make request and show notice
    }
    window.setTimeout(handleTimeout,timeoutTime);
};

$(document).ready(function() {
    var updateHandler = function() { requestLogMessages(getFormData(),updateLogTable); };
    $('.filters input, .filters select').change(updateHandler);

    requestLogMessages(getFormData(),updateLogTable);
    window.setTimeout(handleTimeout,timeoutTime);
});
