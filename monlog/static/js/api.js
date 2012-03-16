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
        // Remove all empty form fields from serialization
        if (n.value == "") {
            return null;
        }
        return n;
    });
};



var displayLogMessages = function(data) {
    var newDisplayedIds = [];

    // Flag every old entry with old-class property
    $.each(data['objects'], function(i, el) {
        if (typeof displayedIds == 'undefined' || $.inArray(el['id'], displayedIds) !== -1) {
            // this is an old log message
            el['old'] = true;
        }
        newDisplayedIds.push(el['id']);
    });

    // Apply data to ICanHaz templates
    $(".content .table tbody").html(ich.log_messages(data));
    displayedIds = newDisplayedIds;

    $('#refresh_notice').hide();
    lastDisplayedDatetime = ISODateString(new Date());
};


var updateLogTable = function(data) {
    // Handles a full request, i.e. a non-refresh request
    // Full requests happen every timeoutTime in streaming mode,
    // and whenever you change filters or click the refresh notice otherwise

    // When this function is called we do not want to highlight new entries
    $('.content table').removeClass('was-refreshed');

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
    // Highlight new entries
    $('.content table').addClass('was-refreshed');
    displayLogMessages(data);
};

var toggleStreamingMode = function(enable) {
    console.log("toggleStreamingMode:", enable);
    if (typeof enable == "undefined") {
        // we want to end up with the inverse of the current streaming mode
        enable = ! streamingMode;
    }
    if (enable != streamingMode) {
        // actually toggle streaming mode
        if (enable) {
            $("#collapse-form").addClass("non-expanded");
            $("#streaming").removeClass("streaming-deactivated");
            $("#streaming").html("Streaming");
        } else {
            $("#collapse-form").removeClass("non-expanded");
            $("#streaming").addClass("streaming-deactivated");
            $("#streaming").html("Streaming paused");
        }
        streamingMode = enable;
    }
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
});
