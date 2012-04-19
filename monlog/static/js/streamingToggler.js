var streamingMode = typeof getCookie("streamingModeActive") == "undefined" ? true : getCookie("streamingModeActive");

var toggleStreamingMode = function(enable) {
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
            // collapse all expanded detail rows
            $("table tbody .details .in").collapse('hide');
        } else {
            $("#collapse-form").removeClass("non-expanded");
            $("#streaming").addClass("streaming-deactivated");
            $("#streaming").html("Streaming paused");
        }
        setCookie("streamingModeActive", enable, 365);
        streamingMode = enable;
    }
};

$(document).ready(function() {
    $("#severity-checkboxes").hide();
    $("#collapse-form").on('show', function() {
        toggleStreamingMode(false);
    });
    $("#collapse-form").on('hide', function() {
        toggleStreamingMode(true);
    });
    if (streamingMode == "false") {
        $("#collapse-form").collapse('show');
    }
});
