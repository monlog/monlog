function setCookie(cookieName,value,exdays) {
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + exdays);
    var c_value = escape(value) + ((exdays==null) ? "" : "; expires="+exdate.toUTCString());
    document.cookie = cookieName + "=" + c_value;
}

function getCookie(cookieName) {
    var i,x,y,ARRcookies = document.cookie.split(";");
    for (i=0; i < ARRcookies.length; i++) {
        x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
        y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
        x=x.replace(/^\s+|\s+$/g,"");

        if (x == cookieName) {
            return unescape(y);
        }
    }
}
