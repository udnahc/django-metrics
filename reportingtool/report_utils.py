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


