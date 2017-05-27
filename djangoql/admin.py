from __future__ import unicode_literals

import json

from django.conf.urls import url
from django.contrib import admin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError, ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from .compat import text_type
from .exceptions import DjangoQLError
from .models import Query
from .queryset import apply_search
from .schema import DjangoQLSchema


class DjangoQLSearchMixin(object):
    search_fields = ('_djangoql',)  # just a stub to have search input displayed
    djangoql_completion = True
    djangoql_schema = DjangoQLSchema
    djangoql_syntax_help_template = 'djangoql/syntax_help.html'

    def get_search_results(self, request, queryset, search_term):
        use_distinct = False
        if not search_term:
            return queryset, use_distinct
        try:
            return (
                apply_search(queryset, search_term, self.djangoql_schema),
                use_distinct,
            )
        except (DjangoQLError, ValueError, FieldError) as e:
            msg = text_type(e)
        except ValidationError as e:
            msg = e.messages[0]
        queryset = queryset.none()
        messages.add_message(request, messages.WARNING, msg)
        return queryset, use_distinct

    @property
    def media(self):
        media = super(DjangoQLSearchMixin, self).media
        if self.djangoql_completion:
            media.add_js((
                'djangoql/js/lib/lexer.js',
                'djangoql/js/completion.js',
                'djangoql/js/completion_admin.js',
            ))
            media.add_css({'': (
                'djangoql/css/completion.css',
                'djangoql/css/completion_admin.css',
            )})
        return media

    def get_urls(self):
        custom_urls = []
        if self.djangoql_completion:
            custom_urls += [
                url(
                    r'^introspect/$',
                    self.admin_site.admin_view(self.introspect),
                    name='%s_%s_djangoql_introspect' % (
                        self.model._meta.app_label,
                        self.model._meta.model_name,
                    ),
                ),
                url(
                    r'^save-djangoql-query/$',
                    self.admin_site.admin_view(self.save_djangoql_query),
                    name='%s_%s_djangoql_save_query' % (
                        self.model._meta.app_label,
                        self.model._meta.model_name,
                    ),
                ),
                url(
                    r'^djangoql-syntax/$',
                    TemplateView.as_view(
                        template_name=self.djangoql_syntax_help_template,
                    ),
                    name='djangoql_syntax_help',
                ),
            ]
        return custom_urls + super(DjangoQLSearchMixin, self).get_urls()

    def introspect(self, request):
        response = self.djangoql_schema(self.model,
                                        user=request.user).as_dict()
        return HttpResponse(
            content=json.dumps(response, indent=2),
            content_type='application/json; charset=utf-8',
        )

    def save_djangoql_query(self, request):
        """
        Redirect to the Query creation page
        """
        path = reverse('admin:djangoql_query_add')
        params = request.GET.copy()
        # prefill the model field
        params['model'] = ContentType.objects.get_for_model(self.model).id
        # popup mode is set by default
        if '_popup' not in params:
            params['_popup'] = '1'
        return HttpResponseRedirect(path + "?" + params.urlencode())


@admin.register(Query)
class QueryAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ('label', 'short_text', 'model', 'user', 'is_private')
    raw_id_fields = ('user',)
    readonly_fields = ('edited',)
    ordering = ('-edited',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(QueryAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['user'].initial = request.user
        return form

    def short_text(self, obj):
        return truncatechars(obj.text, 50)
    short_text.short_description = _('Query text')
