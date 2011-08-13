def recordlog(request):
    from screencapture.models import Movement
    from urlparse import urlparse
    from django.http import Http404

    if request.GET.has_key('no_exp'):
        return {'run_experiment':'False'}

    if request.GET.has_key('show_video'):
        try:
            movement = Movement.objects.get(id=request.GET['show_video'])
        except Movement.DoesNotExist:
            raise Http404

        web_url = movement.full_url
        list_of_events =  list(eval(movement.tale.strip('[').strip(']')))
        no_of_records = Movement.objects.filter(user_email = movement.user_email).count()

        import StringIO
        output = StringIO.StringIO()
        output.write('E = new Event.Replay();\n')
        total_time = 0
        for event_dict in list_of_events:
            total_time += int(event_dict['time'])
            output.write("E.addEvent(new Event.Replayable('%s','%s',%s,%s,new Date().getTime() + %s,'%s','',''));\n" % (event_dict['type'],
                                                                                        event_dict['target'],
                                                                                        event_dict['mouseX'],
                                                                                        event_dict['mouseY'],
                                                                                        event_dict['time'],
                                                                                        event_dict['href'],
                                                                                        ))
            output.write('E.replayEvents();\n')
        output_string = output.getvalue()
        output.close()
        return {'output_string':output_string,'run_experiment':'False', 'ip_address': movement.ip, 'total_time':total_time/100/60, 'no_of_records':no_of_records, 'logged_in_user':movement.user_email}
    else:
        return {'run_experiment':'True'}


