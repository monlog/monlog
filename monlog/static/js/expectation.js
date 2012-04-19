
var expectation_editmode = true;


function showExpectationEditMode() {
    $('.edit-mode').show();
    $('.view-mode').hide();
    $('.multiple_select').find('select').removeAttr('disabled');
    expectation_editmode = !expectation_editmode;
}

function hideExpectationEditMode() {
    $('.edit-mode').hide();
    $('.view-mode').show();
    $('.multiple_select').find('select').attr('disabled','disabled');
    expectation_editmode = !expectation_editmode;
}

function toggleExpectationEditMode() {
    if (expectation_editmode) {
        hideExpectationEditMode();
    } else {
        showExpectationEditMode();
    }
}

$(document).ready(function() {
    hideExpectationEditMode();
});
