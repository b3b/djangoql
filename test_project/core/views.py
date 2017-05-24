import json

from django.contrib.auth.models import Group, User
from django.shortcuts import render_to_response
from django.views.decorators.http import require_GET

from djangoql.exceptions import DjangoQLError
from djangoql.queryset import apply_search
from djangoql.schema import DjangoQLSchema


class UserQLSchema(DjangoQLSchema):
    include = (User, Group)

    def get_saved_queries(self, model, user):
        generated_queries = [{'label': "department {}".format(n),
                              'q': 'is_active = True and ' +
                              'groups.name = "department{}"'.format(n)}
                             for n in range(1, 33)]
        return [
            {'q': 'first_name in ("Alice", "Bob")'},
            {'label': 'new staff 2017', 'q':
             'is_staff = True and date_joined >= "2017-01-01" ' +
             'and date_joined < "2018-01-01"'},
            {'label': 'departments',
             'q': 'is_active = True and groups.name ~ "department"'},
        ] + generated_queries


@require_GET
def completion_demo(request):
    q = request.GET.get('q', '')
    error = ''
    query = User.objects.all().order_by('username')
    if q:
        try:
            query = apply_search(query, q, schema=UserQLSchema)
        except DjangoQLError as e:
            query = query.none()
            error = str(e)
    return render_to_response('completion_demo.html', {
        'q': q,
        'error': error,
        'search_results': query,
        'introspections': json.dumps(UserQLSchema(query.model).as_dict()),
    })
