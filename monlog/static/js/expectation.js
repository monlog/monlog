
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

var longdescSize = function() {
    var content_width = $("#form-wrapper").outerWidth(true);
    $(".long_desc").css("width", content_width);
};

var displayLogMessages = function(data) {
    // Apply data to ICanHaz templates
    $(".content .table tbody").html(ich.log_messages(data));

    $('#refresh_notice').hide();
    lastDisplayedDatetime = ISODateString(new Date());

    // updates width of pre content
    longdescSize();
};


var updateLogTable = function(data) {
    // Called when streaming mode is enabled
    displayLogMessages(data);
};

var requestExpectationMessages = function(expectation,callback) {
    $("#loading_indicator").fadeIn(300);

    var url = "/api/expectationmessages/?limit=5&expectation=" + expectation;
    $.getJSON(url, function(data,textStatus,jqXHR) {
        callback(data);
        $("#loading_indicator").fadeOut(300);
    });
};


$(document).ready(function() {

    if (expId >= 0)
        requestExpectationMessages(expId,updateLogTable);

    // resize pre content
    longdescSize();
    $(window).resize(longdescSize);
});
