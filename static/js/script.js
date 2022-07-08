function unlock_btn(id) {
    var BUTTON_ID = 'submit_btn'
    var val = document.getElementById(id).value;
    if (val.length > 0) {
        document.getElementById(BUTTON_ID).removeAttribute('disabled');
    }
    else{
        document.getElementById(BUTTON_ID).setAttribute('disabled');
    }
}