/*
 * api.js - Monlog 2012
 *
 * Events that triggers an api request:
 * - StreamingMode enabled
 *      Repopulate table when timeout is triggered
 *      updateLogTable(data)
 * - StreamingMode disabled
 *      Request api to check for new entries, notify user if that's the case
 *      displayRefreshNotice(data)
 * - Manual Refresh when StreamingMode is disabled
 *      User clicks the link in the notifcation. Repopulate entry table and highlight new entries.
 *      manualRefreshTriggered(data)
*/

var pendingData;
var timeoutTime = 5000;
var lastDisplayedDatetime;

// These variables is related to lazyloading
var messagesPerPage = 25;
var nextOffset = 0;
var messagesTotal = 0;

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
        // Remove all empty form fields from serialization
        if (n.value == "") {
            return null;
        }
        return n;
    });
};



var displayLogMessages = function(data) {
    // Apply data to ICanHaz templates
    $(".content .table tbody").html(ich.log_messages(data));

    $('#refresh_notice').hide();
    lastDisplayedDatetime = ISODateString(new Date());

    // Save data needed for lazyloading
    nextOffset = messagesPerPage;
    messagesTotal = data['meta']['total_count'];
    // updates width of pre content
    longdescSize();
};


var updateLogTable = function(data) {
    // Called when streaming mode is enabled
    displayLogMessages(data);
};

var displayRefreshNotice = function(data) {
    // Called every timeoutTime ms when streaming mode is disabled
    var count = data['objects'].length;
    var maxObjects = 20;

    if (count > 0) {
        if (count >= maxObjects) {
            count = maxObjects + "+";
        }
        $('#refresh_notice').html(ich.refresh_notice_template({ 'count': count }));
        $('#refresh_notice').show();
    }
};

var manualRefreshTriggered = function(data) {
    // This function is called when refresh notice link is clicked
    // Streaming mode disabled
    displayLogMessages(data);
};

var lazyloadAppend = function(data) {
    // Append data to already populated table
    $(".content .table tbody").append(ich.log_messages(data));
    nextOffset += messagesPerPage;
    // updates width of pre content
    longdescSize();
};

var requestLogMessages = function(formData,callback) {

    if (typeof expectationMode !== 'undefined') {
        if (expectationName == null) return;
        var url = "/api/expectationmessages/?limit=" + messagesPerPage + "&expectation_name=" + expectationName;
    } else {
        var url = "/api/logmessages/?limit=" + messagesPerPage + "&" + $.param(formData);
    }

    $("#loading_indicator").fadeIn(300);
    $.getJSON(url, function(data,textStatus,jqXHR) {
        callback(data);
        $("#loading_indicator").fadeOut(300);
    });
};

var lazyloadTrigger = function() {
    // Called when trigger element is in view port
    if (!streamingMode &&
    typeof lastDisplayedDatetime !== 'undefined' &&
    nextOffset <= messagesTotal) {
        formMap = getFormData();
        // Only older data is requested
        formMap.push({ 'name': 'add_datetime__lte', 'value': lastDisplayedDatetime });
        // Add offset so that the next page is loaded
        formMap.push({ 'name': 'offset', 'value': nextOffset });
        requestLogMessages(formMap, lazyloadAppend);
    }
};

var handleTimeout = function() {
    if (streamingMode) {
        // Auto update table
        requestLogMessages(getFormData(), function(data) {
            if (streamingMode) {
                // We need to make sure we haven't left streamingMode
                updateLogTable(data);
            }
        });
    } else {
        // Make request and show notice
        formMap = getFormData();
        if (typeof lastDisplayedDatetime !== 'undefined') {
            // Add lastDisplayedDatetime to only recieve the new entries since last update
            formMap.push({ 'name': 'add_datetime__gte', 'value': lastDisplayedDatetime });
        }

        requestLogMessages(formMap,displayRefreshNotice);
    }

    // Set new timeout
    window.setTimeout(handleTimeout,timeoutTime);
};

var delay = (function() {
    var timer = 0;
    return function(callback, ms) {
        window.clearTimeout (timer)
        timer = window.setTimeout(callback, ms);
    };
})();

var longdescSize = function() {
    var content_width = $("#form-wrapper").outerWidth(true);
    $(".long_desc").css("width", content_width);
};

$(document).ready(function() {
    var updateHandler = function() { requestLogMessages(getFormData(),updateLogTable); };
    $('.filters input, .filters select').change(updateHandler);

    $('.search-query').keyup(function() {
        delay(updateHandler,500)
    });
    $('form.filters').submit(function(event){
        updateHandler();
        event.preventDefault();
    });

    var manualUpdate = function() { requestLogMessages(getFormData(),manualRefreshTriggered); };
    $('#refresh_notice').bind('click', manualUpdate);

    requestLogMessages(getFormData(),updateLogTable);
    window.setTimeout(handleTimeout,timeoutTime);
    // resize pre content
    longdescSize();
    $(window).resize(longdescSize);
});
