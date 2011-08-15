from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import render_to_response
from django.utils.http import urlencode
from django.template import RequestContext
# The system will display a "Show all" link on the change list only if the                                  
# total result count is less than or equal to this setting.                                                                                                  
MAX_SHOW_ALL_ALLOWED = 200


# Changelist settings                                                                                                                                        
ALL_VAR = 'all'
ORDER_VAR = 'o'
ORDER_TYPE_VAR = 'ot'
PAGE_VAR = 'p'
SEARCH_VAR = 'q'
TO_FIELD_VAR = 't'
IS_POPUP_VAR = 'pop'
ERROR_FLAG = 'e'

class ResultObject(object):
    def __init__(self,result,link):
        self.result = result
        self.link = link

class ReportChangeList(object):
    def __init__(self,results,request):
        self.results = results
        self.result_headers = {}
        self.list_per_page = 50
        # Get search parameters from the query string.                                                                                                       
        self.params = dict(request.GET.items()) 
        try:
            self.page_num = int(request.GET.get(PAGE_VAR, 0))
        except ValueError:
            self.page_num = 0
        self.show_all = ALL_VAR in request.GET
        self.base_url = ''

    def get_query_string(self, new_params=None, remove=None):
        if new_params is None: new_params = {}
        if remove is None: remove = []
        p = self.params.copy()
        for r in remove:
            for k in p.keys():
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        return '?%s' % urlencode(p)


    def construct_the_base_url(self):
        # Consctruct New URL
        get_parameter = self.params.copy()
        if get_parameter.has_key('o'):
            del get_parameter['o']

        if get_parameter.has_key('osc'):
            if self.params.get('osc') == 'asc':
                get_parameter['osc'] = 'desc'
            else:
                get_parameter['osc'] = 'asc'
        else:
            get_parameter['osc']='asc'

        self.base_url = '?' + urlencode(get_parameter)

    def default_result_header(self,result_headers):
        self.result_headers = []
        # Create the default one first
        id = 0
        for header in result_headers:
            temp_dict= {}
            temp_dict['value'] = header
            temp_dict['class']= ''
            temp_dict['url'] = self.base_url + '&o=%s'% (id)
            self.result_headers.append(temp_dict)
            id = id + 1
    
    def order_the_results(self):       
        # Change the config of the report headers for the template according to the chosen column to sort
        column_id = self.params.get('o','')
        column_order = self.params.get('osc','')
        if column_order:
            result_dict = self.result_headers[int(column_id)]
            result_dict['class'] = 'sorted %sending' % (column_order)
            if column_order == 'asc':
                self.result_list = sorted(self.result_list, key=lambda result: result[int(column_id)])
                result_dict['order'] = 'desc'
            else:
                self.result_list = sorted(self.result_list, key=lambda result: result[int(column_id)], reverse=True)
                result_dict['order'] = 'asc'

    def get_results(self, result_headers):
        paginator = Paginator(self.results, self.list_per_page)

        result_count = paginator.count
        can_show_all = result_count <= MAX_SHOW_ALL_ALLOWED
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.                                                                                                   
        if (self.show_all and can_show_all) or not multi_page:
            from copy import copy
            result_list = copy(self.results)
        else:
            try:
                result_list = paginator.page(self.page_num+1).object_list
            except InvalidPage:
                result_list = ()

        # Create base url and default result headers
        self.construct_the_base_url()       
        self.default_result_header(result_headers)

        self.result_count = result_count
        self.result_list = result_list
        self.order_the_results()
        self.can_show_all = can_show_all
        self.multi_page = multi_page


        # Get the number of objects, with admin filters applied.                                                                                           
        result_count = paginator.count
        self.paginator = paginator



def convert_dict_to_report_format(query_dict):
    return 

def generate_filter_methods_for_dynamic_query_generation(report_filter_elements, **kwargs):
    ''' Filter is in this format - 'created_on=2010-05-14,created_on=2010-05-15' '''
    
    use_inside_django_filter = {}
    if report_filter_elements:
        report_filter_elements = report_filter_elements.split(',')
        for filter_element in report_filter_elements:
            (key,value) = filter_element.split('=')
            use_inside_django_filter[str(key)] = str(value)

    use_inside_django_filter.update(kwargs)
    return use_inside_django_filter

def created_description_for_annotated_time_graph(graph_headers):
     from django.template.defaultfilters import slugify

     description = {}

     # Construct description from graph headers field of reporting tools
     graph_headers_tuple = eval(graph_headers)

     variables = []

     for graph_header in graph_headers_tuple:

         # Graph header should be of the format - (1, 'Integer', 'Total Visits')
         description[slugify(graph_header[2])] = graph_header[1:3]

         # Push the variable into the variables list so it can be used while setting the data
         variables.append( (graph_header[0],slugify(graph_header[2])) )

     return (description,variables)

def create_data_table_for_annotated_time_graph(result, variables):
         from datetime import datetime 
         # The first variable has to be date
         first_variable = variables[0]         

         # Format the date in string - since all data has to be string
         formatted_date = datetime.strptime(result[first_variable[0]], '%Y-%m-%d %H:%M:%S')

         other_variables = variables[1:]
         temp_dict = {}
         temp_dict[first_variable[1]] = formatted_date
         for variable in other_variables:
             temp_dict[variable[1]] = result[variable[0]]
         return temp_dict

################################################################## Custom Methods Come Here #########################################################

def _datetime_iterator(from_date,to_date):
    from datetime import timedelta, datetime
    if from_date:
        from_date = datetime.strptime(from_date,'%Y-%m-%d')
    else:
        from_date = datetime.strptime('2010-05-01', '%Y-%m-%d')
    if to_date:
        to_date = datetime.strptime(to_date,'%Y-%m-%d')
    else:
        to_date = datetime.today() + timedelta(days =1 )
    while from_date <= to_date:
        yield from_date
        from_date = from_date + timedelta(days=1)
    return


def njs_traffic_analysis(filter):
    from niche_job_sites.models import Tracking
    from datetime import datetime

    results = []
    result_headers = ['Date', 'Total Traffic', 'Browser Traffic']
    kwargs = generate_filter_methods_for_dynamic_query_generation(filter)
    q_results = Tracking.objects.filter(**kwargs).values('for_date','total_traffic','browser_traffic')
    for q_result in q_results:
        temp_list = []
        temp_list.append(q_result['for_date'].strftime('%Y-%m-%d %H:%M:%S'))
        temp_list.append(int(q_result['total_traffic']))
        temp_list.append(int(q_result['browser_traffic']))
        results.append(temp_list)

    return results

def report_based_on_tag(filter):
    ''' Filter should a tag name like advertising-sales '''
    from rjobs.models import JobITagMembership
    from tagging.models import ITag
    from recordstory.models import EventTracker
    (tag,from_date,to_date) = filter.split(',')
    job_itags = JobITagMembership.objects.filter(tag=ITag.objects.exists(tag))
    results = []
    for job_itag in job_itags:
        temp_results = []
        job = job_itag.rjob
        total_visits = EventTracker.objects.filter(created_on__gte=from_date,created_on__lte=to_date,label='visit',action=job.code).count()
        total_upgrades = EventTracker.objects.filter(created_on__gte=from_date,created_on__lte=to_date,label='upgrade',action=job.code).count()
        s = "%s,%s,https://www.peoplelex.com%s,%s,%d,%d" % (job.name.replace(',',' '),str(job.created_on),job.get_public_jobs_url(),job.postedby.personal_email,total_visits,total_upgrades)
        results.append(s.split(","))
    return results



def job_posting_analysis(filter):

    from recordstory.models import EventTracker
    from rjobs.models import RecruiterJob    
    from django.db.models import Count
    from datetime import datetime

    kwargs = generate_filter_methods_for_dynamic_query_generation(filter, label='visit')
    upgrade_events = EventTracker.objects.filter(**kwargs).values('action').annotate(Count('label')).order_by('-label__count')[:50]

    results = []
    for event in upgrade_events:
        job_code = event['action']
        rjob = RecruiterJob.objects.get(code=job_code)
        total_visits_for_that_job_on_that_day = event['label__count']
        total_visits_for_the_job = EventTracker.objects.filter(action=job_code, label='visit').count()
        associated_tags = rjob.get_assigned_tags()
        if rjob.postedby.personal_email == 'resumes@peoplelex.net':
            job_type = 'CJP'
        else:
            job_type = 'Normal'            
        if rjob.city:
            city = rjob.city.name
        else:
            city = ''
        tags = ','.join(map(lambda x:x.tag.name, associated_tags))
        job_posted_on_date = datetime.strptime(str(rjob.created_on.date()),'%Y-%m-%d')

        temp_list = []
        temp_list.append(job_type)
        temp_list.append(int(total_visits_for_the_job))
        temp_list.append(rjob.name)
        temp_list.append(str(job_posted_on_date))
        temp_list.append(city)
        temp_list.append(tags)

#        temp_list ="%s,%d, <a href='https://www.peoplelex.com%s'>%s</a>,%s,%s,%s" % (job_type,int(total_visits_for_the_job), rjob.get_public_jobs_url(), rjob.name,job_posted_on_date,city,tags)
        
        results.append(temp_list)    

    return results


def it_and_software_tag_report(filter):
    from rjobs.models import JobITagMembership
    from tagging.models import ITag
    from recordstory.models import EventTracker
    if not filter:
        return  _default_day_report('it-&-software')
    else:
        results = []
        top_tag = ITag.objects.get(name='it-&-software', is_public=True, is_toplevel=True)
        ch_tags=top_tag.get_children()
        ch_tags.append(top_tag)
        for c_tag in ch_tags:
            kwargs = generate_filter_methods_for_dynamic_query_generation(filter,tag=c_tag)
            itag_jobs = JobITagMembership.objects.filter(**kwargs)
            tag_visits = 0
            tag_upgrades = 0
            for job in itag_jobs:
                job=job.rjob
                kwargs = generate_filter_methods_for_dynamic_query_generation(filter,action='label',label=job.code)
                job_visits = EventTracker.objects.filter(**kwargs).count()
                job_upgrades = EventTracker.objects.filter(**kwargs).count()
                
                tag_visits = job_visits+tag_visits
                tag_upgrades = job_upgrades+tag_upgrades
            s="%s,%s,%s,%s,%s" %(c_tag.name,len(itag_jobs),tag_visits,tag_upgrades,filter)    
            results.append(s.split(","))
        return results

def _default_day_report(top_level_tag_name):    
    from rjobs.models import JobITagMembership
    from tagging.models import ITag
    from recordstory.models import EventTracker
    from datetime import datetime,timedelta
    now=datetime.now()
    today=now.today()
    yday=today-timedelta(days=1)
    
    results = []
    top_tag = ITag.objects.get(name=top_level_tag_name, is_public=True, is_toplevel=True)
    ch_tags=top_tag.get_children()
    ch_tags.append(top_tag)
    for c_tag in ch_tags:
#        kwargs = generate_filter_methods_for_dynamic_query_generation(filter,tag=c_tag)
        itag_jobs = JobITagMembership.objects.filter(tag=c_tag,created_on__gt=yday)
        tag_visits = 0
        tag_upgrades = 0
        for job in itag_jobs:
            job=job.rjob
            #kwargs = generate_filter_methods_for_dynamic_query_generation(filter,action='label',label=job.code)
            job_visits = EventTracker.objects.filter(action='label',label=job.code,created_on__gt=yday).count()
            job_upgrades = EventTracker.objects.filter(action='label',label=job.code,created_on__gt=yday).count()
            
            tag_visits = job_visits+tag_visits
            tag_upgrades = job_upgrades+tag_upgrades
        s="%s,%s,%s,%s,%s" %(c_tag.name,len(itag_jobs),tag_visits,tag_upgrades,today)    
        results.append(s.split(","))
    return results

def industry_based_report(filter):
    from tagging.models import ITag
    from rjobs.models import RecruiterJob
    from datetime import timedelta
    from recordstory.models import EventTracker
    selected_tag = ITag.objects.exists(filter)            
    selected_tag_filter = [selected_tag]
    selected_tag_filter.extend(ITag.objects.get_public_child_tags(selected_tag))
    selected_tag_filter_set = set(selected_tag_filter)

    from_date = '2010-07-09'
    to_date = '2010-07-14'
    date_iter = _datetime_iterator(from_date,to_date)    
    current_date = date_iter.next()
    results_list = []
    while current_date:
        # This is how the report should look like
        # Date, Overall Visits,Total Visits for tag, CJP Visits, Normal Visits, Simply Hired, Juju, Others
        
        temp_list = []        
        from_date = current_date
        to_date = current_date + timedelta(days=1)
        total_events_qs = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date, label='visit')
        temp_list.append(from_date)
        temp_list.append(total_events_qs.count())        
        cjp_visits_for_tag = 0
        normal_visits_for_tag = 0
        total_visits_for_tag = 0        
        visits_from_simply_hired = 0
        visits_from_juju = 0
        visits_from_others = 0
        for event in total_events_qs:
            job_code = event.action
            job = RecruiterJob.objects.get(code=job_code)        
            tags_assigned_to_job = map(lambda x:x.tag,job.assigned_tags)            
            if selected_tag_filter_set & set(tags_assigned_to_job):
                if job.postedby.personal_email == 'resumes@peoplelex.net':
                    cjp_visits_for_tag = cjp_visits_for_tag + 1
                else:
                    normal_visits_for_tag = normal_visits_for_tag + 1                
                if event.category == 'simply-hired':
                    visits_from_simply_hired = visits_from_simply_hired + 1
                elif event.category == 'juju':
                    visits_from_juju = visits_from_juju + 1
                elif event.category == 'Unkown':
                    visits_from_others = visits_from_others + 1
                else:
                    visits_from_others = visits_from_others + 1                     
        temp_list.append(cjp_visits_for_tag + normal_visits_for_tag)
        temp_list.append(cjp_visits_for_tag)
        temp_list.append(normal_visits_for_tag)
        temp_list.append(visits_from_simply_hired)
        temp_list.append(visits_from_juju)
        temp_list.append(visits_from_others)
        results_list.append(temp_list)
        try:        
            current_date = date_iter.next()
        except StopIteration:
            return results_list


def testing_mega_traffic_report(filter):
    from recordstory.models import EventTracker 
    from rjobs.models import RecruiterJob
    from datetime import datetime, timedelta    

    if filter:
        (from_date,to_date) = filter.split(',')
    else:
        # If no filter is mentioned show the last seven days
        (from_date,to_date) = ('2010-05-20','2010-05-27')
           

    results_list = []    
    date_iter = _datetime_iterator(from_date,to_date)
    data_list = []
    current_date = date_iter.next()
    
    while current_date:
        temp_list = []        
        from_date = current_date
        to_date = current_date + timedelta(days=1)       
        temp_list.append(str(from_date))
        
        # No of premium users
        from premium.models import PremiumPlanMembership
        premiums_on_that_day = PremiumPlanMembership.objects.filter(created_on__gte=from_date, created_on__lte=to_date)
        # Total Premiums for that day
        temp_list.append(int(premiums_on_that_day.count()))
        
        # Total clicks according to Traffic acquisition tracker
        from recordstory.models import TrafficAcquisitionTracker
        total_click_traffic = TrafficAcquisitionTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date).count()
        temp_list.append(int(total_click_traffic))
        
        # Traffic from simply hired        
        simply_hired_traffic = TrafficAcquisitionTracker.objects.filter(source='simply-hired', created_on__gte=from_date, created_on__lte=to_date)[0].clicks
        temp_list.append(int(simply_hired_traffic))
        
        # Traffic from juju
        juju_traffic = TrafficAcquisitionTracker.objects.filter(source='juju', created_on__gte=from_date, created_on__lte=to_date)[0].clicks
        temp_list.append(int(juju_traffic))
        
        # Traffic from oodle
        try:
            oodle_traffic = TrafficAcquisitionTracker.objects.filter(source='oodle', created_on__gte=from_date, created_on__lte=to_date)[0].clicks
            temp_list.append(int(oodle_traffic))
        except Exception,e:
            temp_list.append(0)
        
        jobs_posted_on_range = RecruiterJob.objects.filter(created_on__gte=from_date, created_on__lte=to_date)
        job_visit_events = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date, label='visits')
        cjp_jobs_posted = jobs_posted_on_range.filter(postedby__personal_email='resumes@peoplelex.net')
        normal_jobs_posted = jobs_posted_on_range.exclude(postedby__personal_email='resumes@peoplelex.net')        
        # Current Date
#        temp_list.append(str(current_date))
        # Total Jobs Posted
        temp_list.append(jobs_posted_on_range.count())        
        # Total CJP Jobs Posted
        temp_list.append(cjp_jobs_posted.count())        
        # Total Normal Jobs Posted
        temp_list.append(jobs_posted_on_range.count() - cjp_jobs_posted.count() )        
        # Total Day 1 visits
        count_1_day = EventTracker.objects.extra(
                               tables={'rjobs_recruiterjob':'rjobs_recruiterjob'}, 
                               where=['''rjobs_recruiterjob.code=recordstory_eventtracker.action and 
                                         rjobs_recruiterjob.created_on > %s and rjobs_recruiterjob.created_on < %s and
                                         recordstory_eventtracker.created_on > %s and recordstory_eventtracker.created_on < %s
                                         '''], 
                               params=[from_date, (from_date + timedelta(1)), from_date, (from_date + timedelta(1))]).count()
        temp_list.append(count_1_day)        
        # CJP count 
        cjp_count_1_day = EventTracker.objects.extra(
                               tables={'rjobs_recruiterjob':'rjobs_recruiterjob'}, 
                               where=['''rjobs_recruiterjob.code=recordstory_eventtracker.action and 
                                         rjobs_recruiterjob.created_on > %s and rjobs_recruiterjob.created_on < %s and
                                         recordstory_eventtracker.created_on > %s and recordstory_eventtracker.created_on < %s 
                                         and rjobs_recruiterjob.postedby_id = 169284
                                         '''], 
                               params=[from_date, (from_date + timedelta(1)), from_date, (from_date + timedelta(1))]).count()
        temp_list.append(cjp_count_1_day)                
        # Normal count  day
        normal_count_1_day = count_1_day - cjp_count_1_day
        temp_list.append(normal_count_1_day)
        
        # Total Day 2 to 7 visits
        count_2_7_day = EventTracker.objects.extra(
                               tables={'rjobs_recruiterjob':'rjobs_recruiterjob'}, 
                               where=['''rjobs_recruiterjob.code=recordstory_eventtracker.action and 
                                         rjobs_recruiterjob.created_on > %s and rjobs_recruiterjob.created_on < %s and
                                         recordstory_eventtracker.created_on > %s and recordstory_eventtracker.created_on < %s
                                         '''], 
                               params=[(from_date - timedelta(7)), from_date, from_date, (from_date + timedelta(1))]).count()                           
        temp_list.append(count_2_7_day)
       
        # CJP count 
        cjp_count_2_7_day = EventTracker.objects.extra(
                               tables={'rjobs_recruiterjob':'rjobs_recruiterjob'}, 
                               where=['''rjobs_recruiterjob.code=recordstory_eventtracker.action and 
                                         rjobs_recruiterjob.created_on > %s and rjobs_recruiterjob.created_on < %s and
                                         recordstory_eventtracker.created_on > %s and recordstory_eventtracker.created_on < %s 
                                         and rjobs_recruiterjob.postedby_id = 169284
                                         '''], 
                              params=[(from_date - timedelta(7)), from_date, from_date, (from_date + timedelta(1))]).count()
        temp_list.append(cjp_count_2_7_day)                
        # Normal count 1 day
        normal_count_2_7_day = count_2_7_day - cjp_count_2_7_day        
        temp_list.append(normal_count_2_7_day)        
        # Total Day greater than 7 visits
        count_7_day = EventTracker.objects.extra(
                               tables={'rjobs_recruiterjob':'rjobs_recruiterjob'}, 
                               where=['''rjobs_recruiterjob.code=recordstory_eventtracker.action and 
                                         rjobs_recruiterjob.created_on < %s and
                                         recordstory_eventtracker.created_on > %s and recordstory_eventtracker.created_on < %s
                                         '''], 
                               params=[(from_date - timedelta(7)), from_date, (from_date + timedelta(1))]).count()



        temp_list.append(count_7_day)
        # CJP count 
        cjp_count_7_day = EventTracker.objects.extra(
                               tables={'rjobs_recruiterjob':'rjobs_recruiterjob'}, 
                               where=['''rjobs_recruiterjob.code=recordstory_eventtracker.action and 
                                         rjobs_recruiterjob.created_on < %s and
                                         recordstory_eventtracker.created_on > %s and recordstory_eventtracker.created_on < %s 
                                         and rjobs_recruiterjob.postedby_id = 169284
                                         '''], 
                               params=[(from_date - timedelta(7)), from_date, (from_date + timedelta(1))]).count()
        temp_list.append(cjp_count_7_day)        
        # Normal count 1 day
        normal_count_7_day = count_7_day - cjp_count_7_day        
        temp_list.append(normal_count_7_day)
        
        
        results_list.append(temp_list)

        try:        
            current_date = date_iter.next()
        except StopIteration:
            return results_list

def industry_based_report_v1(filter):
    from datetime import timedelta
    from recordstory.models import EventTracker
    from rjobs.models import RecruiterJob
    from rjobs.models import JobITagMembership
    from tagging.models import ITag
    from recordstory.report_utils import _datetime_iterator    
    
    filter_strings = filter.split(',')
    filter = filter_strings[0]
    from_date = filter_strings[1]
    to_date = filter_strings[2]
    child_tags = filter_strings[3]  

    selected_tag = ITag.objects.exists(filter)
    selected_tag_filter = [(selected_tag.id,selected_tag.name)]
    if child_tags == 'yes':
        selected_tag_filter.extend(ITag.objects.get_child_tags(selected_tag))    
    date_iter = _datetime_iterator(from_date,to_date)
    current_date = date_iter.next()
    results_list = []
    while current_date:
        temp_list = []
        from_date = current_date
        to_date = current_date + timedelta(days=1)     
        total_events_qs = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date, label='visit')
        total_jobs_posted = RecruiterJob.objects.filter(created_on__gte=from_date, created_on__lte=to_date)        
        temp_list.append(str(from_date))
        temp_list.append(total_events_qs.count())
        temp_list.append(total_jobs_posted.count())        
        ''' Jobs posted by type '''
        cjp_jobs_posted = 0
        normal_jobs_posted = 0
        total_jobs_posted = 0        
        ''' End of Jobs posted by type '''
        ''' Visits by job type Analysis '''
        cjp_visits_for_tag = 0
        normal_visits_for_tag = 0
        total_visits_for_tag=0
        ''' End of Visits by Job Type Analysis '''        
        ''' Upgrades by Job Tag Analysis '''
        cjp_upgrades = 0
        normal_upgrades = 0
        total_upgrades_for_tag = 0
        ''' End of Upgrades by Job Type Analysis '''       
        ''' Visits by source analysis '''
        total_visits = 0
        simply_hired_visits=0
        cjp_jobs_verified = 0
        total_jobs_verified = 0
        juju_visits=0
        oodle_visits=0
        other_visits=0
        ''' End of visits by job source analysis '''        
        for tag in selected_tag_filter:
            common_where_clause = ''' recordstory_eventtracker.label = '%s' and
                                                                    recordstory_eventtracker.action = rjobs_recruiterjob.code and
                                                                    rjobs_jobitagmembership.rjob_id = rjobs_recruiterjob.id and
                                                                    rjobs_jobitagmembership.tag_id = '%s' and 
                                                                    recordstory_eventtracker.created_on > '%s' and 
                                                                    recordstory_eventtracker.created_on < '%s' '''                                                                    
            common_select_clause = ['rjobs_jobitagmembership','rjobs_recruiterjob']            
            common_visit_where_clause = common_where_clause % ('visit',tag[0], str(from_date), str(to_date))            
            common_update_where_clause = common_where_clause % ('upgrade',tag[0], str(from_date), str(to_date))
            common_cjp_visit_where_clause = '''%s and rjobs_recruiterjob.postedby_id = 169284 ''' % (common_visit_where_clause)
            common_cjp_upgrade_where_clause = '''%s and rjobs_recruiterjob.postedby_id = 169284 ''' % (common_update_where_clause)     
            cjp_visit_events_for_this_tag = EventTracker.objects.extra( tables = common_select_clause, where =  [ common_cjp_visit_where_clause]).values('id').count()
            total_visit_events_for_this_tag = EventTracker.objects.extra(tables = common_select_clause, where = [common_visit_where_clause]).values('id').count()            
            total_jobs_posted_from_tag = JobITagMembership.objects.filter(rjob__created_on__gte=from_date, rjob__created_on__lte=to_date,tag__id = tag[0]).select_related('rjob','itag').count()
            total_cjp_jobs_posted_from_tag = JobITagMembership.objects.filter(rjob__postedby__user__id=169284,rjob__created_on__gte=from_date, rjob__created_on__lte=to_date,tag__id = tag[0]).select_related('rjob','itag').count()            
            total_cjp_upgrades = EventTracker.objects.extra(tables = common_select_clause, where =  [common_cjp_upgrade_where_clause]).values('id').count()            
            total_upgrades = EventTracker.objects.extra(tables = common_select_clause, where =  [common_update_where_clause]).values('id').count()            
#            ''' No point of continuing if there is no job tagged '''
#            if total_jobs_posted_from_tag == 0:
#                print 'No point in pursuing ', tag
#                continue
#            else:
#                print 'Total jobs posted ', total_jobs_posted_from_tag                
            ''' Jobs posted by type '''            
            total_jobs_posted = total_jobs_posted + total_jobs_posted_from_tag
            cjp_jobs_posted = cjp_jobs_posted + total_cjp_jobs_posted_from_tag
            ''' End of Jobs posted by type '''       
            
            ''' Visits by job type Analysis '''            
            cjp_visits_for_tag = cjp_visits_for_tag + cjp_visit_events_for_this_tag
            total_visits_for_tag= total_visits_for_tag + total_visit_events_for_this_tag
            ''' End of Visits by Job Type Analysis '''
            
            ''' Upgrades by Job Tag Analysis '''
            cjp_upgrades = cjp_upgrades + total_cjp_upgrades
            total_upgrades_for_tag= total_upgrades_for_tag + total_upgrades
            ''' End of Upgrades by Job Type Analysis '''
            
            ''' Visits by source analysis '''
#            total_visits = total_visits + EventTracker.objects.extra(tables = common_select_clause, where =  [ common_visit_where_clause]).values('id').count()
            simply_hired_visits = simply_hired_visits + EventTracker.objects.extra(tables = common_select_clause, where =  [ '''%s and recordstory_eventtracker.category='simply-hired' ''' % (common_visit_where_clause)]).values('id').count()
            juju_visits =  juju_visits + EventTracker.objects.extra(tables = common_select_clause, where =  [ '''%s and recordstory_eventtracker.category='juju' ''' % (common_visit_where_clause)]).values('id').count()
            oodle_visits = oodle_visits + EventTracker.objects.extra(tables = common_select_clause,where =  [ '''%s and recordstory_eventtracker.category='oodle' ''' % (common_visit_where_clause)]).values('id').count()
            ''' End of visits by job source analysis '''   

            ''' CJP Jobs Verified '''
            try:
                cjp_jobs_verified = cjp_jobs_verified  + int(EventTracker.objects.get(category='CJP Jobs Verified',action=tag[1], created_on__gte=from_date,created_on__lte=to_date).label)
            except Exception,e:
                cjp_jobs_verified = 0


            ''' Total Jobs Verified '''
            try:
                total_jobs_verified = total_jobs_verified + int(EventTracker.objects.get(category='Jobs Verified', action=tag[1],created_on__gte=from_date, created_on__lte=to_date).label)
            except Exception,e:
                total_jobs_verified = 0

        total_normal_jobs_posted = total_jobs_posted - cjp_jobs_posted
        total_normal_visits_for_tag =  total_visits_for_tag - cjp_visits_for_tag
        normal_upgrades = total_upgrades_for_tag - cjp_upgrades
        other_visits = total_visits_for_tag - (simply_hired_visits + juju_visits + oodle_visits)        
        temp_list.append(int(total_jobs_posted))
        temp_list.append(cjp_jobs_posted)
        temp_list.append(cjp_jobs_verified)
        temp_list.append(total_jobs_verified)
        temp_list.append(total_normal_jobs_posted)        
        temp_list.append(total_visits_for_tag)
        temp_list.append(cjp_visits_for_tag)
        temp_list.append(total_normal_visits_for_tag)        
        temp_list.append(total_upgrades)
        temp_list.append(cjp_upgrades)
        temp_list.append(normal_upgrades)        
        temp_list.append(simply_hired_visits)
        temp_list.append(juju_visits)
        temp_list.append(oodle_visits)
        temp_list.append(other_visits)        
        results_list.append(temp_list)
        try:        
            current_date = date_iter.next()
        except StopIteration:
                return results_list

def upgrade_report(filter):
    from recordstory.models import EventTracker
    from rjobs.models import RecruiterJob
    results = []
    
    upgrade_events = EventTracker.objects.filter(label='upgrade').order_by('-created_on')
    for upgrade_event in upgrade_events:
        temp_list = []
        temp_list.append(upgrade_event.created_on)        
        job_code = upgrade_event.action        
        rjob = RecruiterJob.objects.get(code=job_code)
        temp_list.append(upgrade_event.email)
        temp_list.append('https://www.peoplelex.com%s' % rjob.get_public_jobs_url())
        temp_list.append(rjob.postedby.personal_email)
        temp_list.append(rjob.city.name)
        temp_list.append(rjob.created_on)
        temp_list.append(','.join(map(lambda x:(x.tag.name).replace(',', ' '),rjob.assigned_tags)))
        results.append(temp_list)
    return results

def recruiters_for_tag(filter):
    from rjobs.models import RecruiterITagMembership
    from tagging.models import ITag
    from datetime import timedelta, datetime
    (tag,from_date,to_date) = filter.split(',')    
    date_iter = _datetime_iterator(from_date,to_date)
    tag_object = ITag.objects.exists(tag)
    current_date = date_iter.next()
    results_list = []
    while current_date:
        temp_list = []
        from_date = current_date
        to_date = current_date + timedelta(days=1)     
        count_of_recruiters_added = RecruiterITagMembership.objects.filter(created_on__gte=from_date, created_on__lte=to_date,tag=tag_object).count()
        total_count_of_recruiters_added = RecruiterITagMembership.objects.filter(created_on__gte=from_date, created_on__lte=to_date).count()
        total_recruiters_tagged_in_all = RecruiterITagMembership.objects.filter(tag=tag_object).count()
        temp_list.append(str(from_date))
        temp_list.append(count_of_recruiters_added)
        temp_list.append(total_count_of_recruiters_added)
        temp_list.append(total_recruiters_tagged_in_all)
        results_list.append(temp_list)
        try:        
            current_date = date_iter.next()
        except StopIteration:
            return results_list

def top_50_jobs_for_day(filter):
    from recordstory.models import EventTracker
    from rjobs.models import RecruiterJob
    from django.db.models import Count
    from datetime import datetime, timedelta

    (from_date, to_date) = filter.split(',')
    upgrade_events = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date,label='visit').values('action').annotate(Count('label')).order_by('-label__count')[:25]
    results_list = []
    for event in upgrade_events:
        temp_list = []
        job_code = event['action']
        rjob = RecruiterJob.objects.get(code=job_code)
        total_visits_for_that_job_on_that_day = event['label__count']
        total_visits_for_the_job = EventTracker.objects.filter(action=job_code, label='visit').count()
        associated_tags = rjob.get_assigned_tags()
        if rjob.postedby.personal_email == 'resumes@peoplelex.net':
            job_type = 'CJP'
        else:
            job_type = 'Normal'            
        if rjob.city:
            city = rjob.city.name
        else:
            city = ''
        tags = ','.join(map(lambda x:x.tag.name, associated_tags))
        job_posted_on_date = datetime.strptime(str(rjob.created_on.date()),'%Y-%m-%d')
        s = '%s,%s,%s, https://www.peoplelex.com%s,%s,%s,%s' % (job_type,total_visits_for_that_job_on_that_day, total_visits_for_the_job, rjob.get_public_jobs_url(),job_posted_on_date ,city,tags)
        temp_list = s.split(',')
        results_list.append(temp_list)
    return results_list


def upgrade_traffic_details(filter):
    from recordstory.models import EventTracker
    from rjobs.models import RecruiterJob
    events_generating_upgrades = EventTracker.objects.filter(label='upgrade').order_by('-created_on')
    tags_dict = {'untagged':0}
    results = []
    for event in events_generating_upgrades:
        rjob = RecruiterJob.objects.get(code=event.action)
        if rjob.postedby.personal_email=='resumes@peoplelex.net':
            job_type = 'CJP'
        else:
            job_type = 'Normal'
    
        total_tags = []
        tags = rjob.get_assigned_tags()
        for tag in tags:
            total_tags.append(tag.tag.name)
        total_tags_in_string = ' '.join(total_tags)
        job_url = 'https://www.peoplelex.com%s' % (rjob.get_public_jobs_url())
        visits = EventTracker.objects.filter(action=rjob.code, label='visit').count()
    
        from datetime import datetime    
        results_string = '%s,%s,%s,%s,%s, %s,%s' % (visits,rjob.city,job_type, rjob.name.replace(","," "), datetime.strptime(str(event.created_on.date()), '%Y-%m-%d'), job_url,total_tags_in_string )
        temp_dict = results_string.split(",")
        results.append(temp_dict)
    return results

# def report_on_upgrade_event(filter):
#         from recordstory.models import EventTracker
#         top_level_tag_dictionary = {'untagged':1}
#         show_signup_form = EventTracker.objects.filter(category='Upgrade Interest',action='Show Signup Form')
#         for string in show_signup_form:
#             xx_string = string.label
#             from rjobs.models import RecruiterJob
#             from tagging.models import ITag
#             from rjobs.models import JobITagMembership
#             rjob = RecruiterJob.objects.get(code=xx_string)
#             top_level_assigned_tags = []
#             for job_tag in rjob.get_assigned_tags():
#                 if job_tag.tag.is_toplevel and job_tag.tag.is_public:
#                     top_level_assigned_tags.append(job_tag)
#             #top_level_assigned_tags = filter(lambda x:x.tag.is_toplevel,rjob.get_assigned_tags())
#             if top_level_assigned_tags:
#                 tag_name = top_level_assigned_tags[0].tag.name
#                 if top_level_tag_dictionary.has_key(tag_name):
#                     top_level_tag_dictionary[tag_name] = top_level_tag_dictionary[tag_name] + 1
#                 else:
#                     top_level_tag_dictionary[tag_name] = 1
#             else:
#                 top_level_tag_dictionary['untagged'] = top_level_tag_dictionary['untagged'] + 1
#         from recordstory.models import EventTracker
#         print top_level_tag_dictionary
#         total_visits = 0


def report_on_upgrade_event(filter):
        from recordstory.models import EventTracker
        from tagging.models import ITag
        from rjobs.models import RecruiterJob
        from datetime import timedelta, datetime
        (tag,from_date,to_date) = filter.split(",")
        date_iter = _datetime_iterator(from_date,to_date)
        tag_object = ITag.objects.exists(tag)
        current_date = date_iter.next()
        results_list = []
        while current_date:
            show_signup_widget_count = 0
            close_signup_widget_count = 0
            temp_list = []
            from_date = current_date
            to_date = current_date + timedelta(days=1)     
            show_signup_events = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date,category='Upgrade Interest',action='Show Signup Form')
            for event in show_signup_events:
                rjob_tags = map(lambda x:x.tag,RecruiterJob.objects.get(code=event.label).get_assigned_tags())
                if tag_object in rjob_tags:
                    show_signup_widget_count = show_signup_widget_count + 1
            
            show_signup_events = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date,category='Upgrade Interest',action='Close Signup Form')
            for event in show_signup_events:
                rjob_tags = map(lambda x:x.tag,RecruiterJob.objects.get(code=event.label).get_assigned_tags())
                if tag_object in rjob_tags:
                    close_signup_widget_count = close_signup_widget_count + 1 
            
            temp_list.append(str(from_date))
            temp_list.append(show_signup_widget_count)
            temp_list.append(close_signup_widget_count)
            results_list.append(temp_list)
            try:        
                current_date = date_iter.next()
            except StopIteration:
                return results_list

def report_on_upgrade_event(filter):
        from recordstory.models import EventTracker
        from tagging.models import ITag
        from rjobs.models import RecruiterJob
        from datetime import timedelta
        (tag,from_date,to_date) = filter.split(",")
        date_iter = _datetime_iterator(from_date,to_date)
        tag_object = ITag.objects.exists(tag)
        current_date = date_iter.next()
        results_list = []
        while current_date:
            overall_show_signup_count = 0
            overall_close_widget_count = 0

            show_signup_widget_count = 0
            cjp_show_signup_widget_count = 0
            normal_show_signup_widget_count = 0

            close_signup_widget_count = 0
            cjp_close_signup_widget_count = 0
            normal_close_signup_widget_count = 0

            temp_list = []
            from_date = current_date
            to_date = current_date + timedelta(days=1)     
            show_signup_events = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date,category='Upgrade Interest',action='Show Signup Form')
            
            overall_show_signup_count = show_signup_events.count()
            for event in show_signup_events:
                rjob_tags = map(lambda x:x.tag,RecruiterJob.objects.get(code=event.label).get_assigned_tags())
                if tag_object in rjob_tags:
                    show_signup_widget_count = show_signup_widget_count + 1
                    if RecruiterJob.objects.get(code=event.label).postedby.personal_email == 'resumes@peoplelex.net':
                        cjp_show_signup_widget_count = cjp_show_signup_widget_count + 1
                    else:
                        normal_show_signup_widget_count = normal_show_signup_widget_count + 1
            
            show_signup_events = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date,category='Upgrade Interest',action='Close Signup Form')
            overall_close_widget_count = show_signup_events.count()
            for event in show_signup_events:
                rjob_tags = map(lambda x:x.tag,RecruiterJob.objects.get(code=event.label).get_assigned_tags())
                if tag_object in rjob_tags:
                    close_signup_widget_count = close_signup_widget_count + 1 
                    if RecruiterJob.objects.get(code=event.label).postedby.personal_email == 'resumes@peoplelex.net':
                        cjp_close_signup_widget_count = cjp_close_signup_widget_count + 1
                    else:
                        normal_close_signup_widget_count = normal_close_signup_widget_count + 1

            
            temp_list.append(str(from_date))
            temp_list.append(overall_show_signup_count)
            temp_list.append(overall_close_widget_count)
            temp_list.append(overall_show_signup_count - overall_close_widget_count)
            temp_list.append(show_signup_widget_count)
            temp_list.append(cjp_show_signup_widget_count)
            temp_list.append(normal_show_signup_widget_count)
            temp_list.append(close_signup_widget_count)
            temp_list.append(cjp_close_signup_widget_count)
            temp_list.append(normal_close_signup_widget_count)
            results_list.append(temp_list)
            try:        
                current_date = date_iter.next()
            except StopIteration:
                return results_list


def upgrade_interest_detail_report(filter):
        from recordstory.models import EventTracker
        from tagging.models import ITag
        from rjobs.models import RecruiterJob
        from datetime import timedelta
        (tag,from_date,to_date) = filter.split(",")
        date_iter = _datetime_iterator(from_date,to_date)
        tag_object = ITag.objects.exists(tag)
        current_date = date_iter.next()
        results_list = []
        while current_date:
            temp_list = []
            from_date = current_date
            to_date = current_date + timedelta(days=1)     
            show_signup_events = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date,category='Upgrade Interest',action='Show Signup Form')
            
            overall_show_signup_count = show_signup_events.count()
            for event in show_signup_events:
                rjob_tags = map(lambda x:x.tag,RecruiterJob.objects.get(code=event.label).get_assigned_tags())
                if tag_object in rjob_tags:
                    show_signup_widget_count = show_signup_widget_count + 1
                    if RecruiterJob.objects.get(code=event.label).postedby.personal_email == 'resumes@peoplelex.net':
                        cjp_show_signup_widget_count = cjp_show_signup_widget_count + 1
                    else:
                        normal_show_signup_widget_count = normal_show_signup_widget_count + 1
            
            show_signup_events = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date,category='Upgrade Interest',action='Close Signup Form')
            overall_close_widget_count = show_signup_events.count()
            for event in show_signup_events:
                rjob_tags = map(lambda x:x.tag,RecruiterJob.objects.get(code=event.label).get_assigned_tags())
                if tag_object in rjob_tags:
                    close_signup_widget_count = close_signup_widget_count + 1 
                    if RecruiterJob.objects.get(code=event.label).postedby.personal_email == 'resumes@peoplelex.net':
                        cjp_close_signup_widget_count = cjp_close_signup_widget_count + 1
                    else:
                        normal_close_signup_widget_count = normal_close_signup_widget_count + 1

            
            temp_list.append(str(from_date))
            temp_list.append(overall_show_signup_count)
            temp_list.append(overall_close_widget_count)
            temp_list.append(overall_show_signup_count - overall_close_widget_count)
            temp_list.append(show_signup_widget_count)
            temp_list.append(cjp_show_signup_widget_count)
            temp_list.append(normal_show_signup_widget_count)
            temp_list.append(close_signup_widget_count)
            temp_list.append(cjp_close_signup_widget_count)
            temp_list.append(normal_close_signup_widget_count)
            results_list.append(temp_list)
            try:        
                current_date = date_iter.next()
            except StopIteration:
                return results_list


def report_on_upgrade_interest(filter):
        from recordstory.models import EventTracker
        from tagging.models import ITag
        from rjobs.models import RecruiterJob
        from datetime import timedelta
        (tag,from_date,to_date) = filter.split(",")
        tag_object = ITag.objects.exists(tag)
        results_list = []
        total_iterations = 0

        temp_list = []
        total_iterations = total_iterations + 1
        common_where_clause = ''' recordstory_eventtracker.category= '%s' and recordstory_eventtracker.label = rjobs_recruiterjob.code and rjobs_jobitagmembership.rjob_id = rjobs_recruiterjob.id and rjobs_jobitagmembership.tag_id = '%s' and  recordstory_eventtracker.created_on > '%s' and recordstory_eventtracker.created_on < '%s' '''
        common_select_clause = ['rjobs_jobitagmembership','rjobs_recruiterjob']
        common_visit_where_clause = common_where_clause % ('Upgrade Interest',tag_object.id, from_date, to_date)
        total_visit_events_for_this_tag = EventTracker.objects.extra(tables = common_select_clause, where = [common_visit_where_clause]).values('label').distinct()
        total_open_widget = 0
        total_close_widget = 0
        total_visits = 0

        for event in total_visit_events_for_this_tag:
             temp_list = []
             rjob = RecruiterJob.objects.get(code=event['label'])
             total_open_widget = EventTracker.objects.filter(category='Upgrade Interest', action='Show Signup Form', created_on__gte=from_date, created_on__lte=to_date, label=rjob.code).count()
             total_close_widget = EventTracker.objects.filter(category='Upgrade Interest', action='Close Signup Form',created_on__gte=from_date, created_on__lte=to_date, label=rjob.code).count()
             total_visits = EventTracker.objects.filter(label='visit', action=rjob.code, created_on__gte=from_date, created_on__lte=to_date).count()
#             temp_list.append(str(current_date))
             temp_list.append("http://www.peoplelex.com%s" % (rjob.get_public_jobs_url()))
             temp_list.append(rjob.created_on)
             temp_list.append(rjob.postedby.personal_email)
             temp_list.append(rjob.name)
             temp_list.append(total_open_widget)
             temp_list.append(total_close_widget)
             temp_list.append(total_visits)
             results_list.append(temp_list)
        return results_list


def upgrade_percentage(filter):
    from datetime import timedelta
    from recordstory.models import EventTracker
    from tagging.models import ITag
    from rjobs.models import RecruiterJob
    from premium.models import PremiumPlanMembership
    (from_date,to_date) = filter.split(",")
    date_iter = _datetime_iterator(from_date,to_date)
    current_date = date_iter.next()
    results_list = []
    while current_date:
        temp_list = []
        from_date = current_date
        to_date = current_date + timedelta(days=1)     
        total_events = EventTracker.objects.filter(created_on__gte=from_date, created_on__lte=to_date, label='visit').count()
        total_premiums = PremiumPlanMembership.objects.filter(created_on__gte=from_date, created_on__lte=to_date).count()
        premium_percentage = 0.0
        premium_percentage = 100 * (float(total_premiums)/float(total_events))
        temp_list.append(current_date)
        temp_list.append(total_premiums)
        temp_list.append(total_events)
        temp_list.append(premium_percentage)
        results_list.append(temp_list)
        try:        
            current_date = date_iter.next()
        except StopIteration:
            return results_list


def city_wise_traffic_to_tag(filter):
    from django.db import connection
    if not filter:
        return []
    (tag, from_date, to_date) = filter.split(',')
    from tagging.models import ITag
    tag_id = ITag.objects.exists(tag).id
    cursor = connection.cursor()
    query = '''
                select 
                count(*),clocation_city.name, clocation_state.name
                from 
                recordstory_eventtracker, rjobs_recruiterjob,rjobs_jobitagmembership, clocation_city, clocation_state
                where
                recordstory_eventtracker.label = 'visit' 
                and
                rjobs_jobitagmembership.tag_id = %s
                and                                                          
                recordstory_eventtracker.created_on > %s
                and                                                     
                recordstory_eventtracker.created_on < %s
                and                                                                                        
                recordstory_eventtracker.action = rjobs_recruiterjob.code 
                and                                      
                rjobs_jobitagmembership.rjob_id = rjobs_recruiterjob.id
                and
                clocation_city.id = rjobs_recruiterjob.city_id
                and
                clocation_state.id = rjobs_recruiterjob.state_id
                group by
                clocation_city.name,
                clocation_state.name
                order by
                count(*);
            '''
    cursor.execute(query,[tag_id,from_date,to_date])
    results = cursor.fetchall()
    result_set = []
    for result in results:
        result_set.append(list(result))
    return result_set



def test_report(filter):
    result_set = []
    result_set.append(['1','2'])
    result_set.append(['3', '4'])
    return result_set


def _request_param_get(request,key):
    return request.GET.get(key, None)

def _request_param_post(request,key):
    return request.POST.get(key, None)


def response(template, params={}, request=None):
    return render_to_response(template, params, context_instance=RequestContext(request))


