function run_experiment() {
    E = new Event.Replay();
    E.observe();
    window.onunload = function()
    {
        E.stopObserving();
        E.sendEvents();
    }

}

function gup( name ) {

    name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
    var regexS = "[\\?&]"+name+"=([^&#]*)";
    var regex = new RegExp( regexS );
    var results = regex.exec( window.location.href );
    if( results == null )
        return "";
     else
         return results[1];

}

function refresh_page() {
    location.reload(true)
}

function sleep(naptime){
    naptime = naptime * 1000;
    var sleeping = true;
    var now = new Date();
    var alarm;
    var startingMSeconds = now.getTime();
    while(sleeping){
        alarm = new Date();
        alarmMSeconds = alarm.getTime();
        if(alarmMSeconds - startingMSeconds > naptime){ sleeping = false; }
    }
}


function record_event(category,action,label) {
    url = '/record_event/';
    ajax = new Ajax.Request(url, { method:  'post', parameters: {category: category, action:action, label:label }})
}

function record_event_before_submit(category,action,label,form_name) {
    url = '/record_event/';
    ajax = new Ajax.Request(
        url, {
            method: 'post',
            parameters: {category: category, action:action, label:label },
            onComplete: function(transporting){
                $(form_name).submit();
            }

        })
}
