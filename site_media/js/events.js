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
