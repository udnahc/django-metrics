from screencapture.models import Movement 
from django.http import HttpResponse


def view_record_movement(request):
    try:
        import simplejson
    except ImportError:
        try:
            import json as simplejson
        except ImportError:
            try:
                from django.utils import simplejson
            except:
                raise "Requires either simplejson, Python 2.6 or django.utils!"

    ip = request.META['REMOTE_ADDR']
    project = 1

    user_email = ''
    if request.user.is_authenticated():
        user_email = request.user.email
    ip = request.META['REMOTE_ADDR']
    full_url = ''

    post_keys = simplejson.loads(request.POST.keys()[0])
    if post_keys.has_key('location'):
        if post_keys['location'].has_key('href'):
            full_url =  post_keys['location']['href']

    if post_keys.has_key('events'):
        tale = post_keys['events']

        tale = post_keys['events']


    if not full_url:
        full_url = request.META.get('HTTP_REFERER')
        
    if not tale:
        return 'True'

    movement_object = Movement.objects.create_tale(project=1,ip=ip,full_url=full_url,user_email=user_email, tale=str(tale), total_time=1000)
    return HttpResponse('True')
