from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import truncatechars
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .compat import user_model_label


class QueryManager(models.Manager):

    def for_model(self, model, user=None):
        model_type = ContentType.objects.get_for_model(model)
        return Query.objects.filter(Q(model=model_type) & (
            Q(is_private=False) | Q(user=user)))


@python_2_unicode_compatible
class Query(models.Model):
    """
    A model for storing DjangoQL saved queries
    """

    label = models.CharField(_("Label"), max_length=150, blank=True)
    text = models.TextField(_('Query'))
    model = models.ForeignKey(ContentType, verbose_name=_('Related model'),
                              on_delete=models.CASCADE,)
    user = models.ForeignKey(user_model_label, verbose_name=_("User"),
                             on_delete=models.CASCADE)
    is_private = models.BooleanField(
        _('Is private'), default=True,
        help_text=_('Show query only to the selected user'))
    edited = models.DateTimeField(_('Last edition time'), auto_now=True)
    objects = QueryManager()

    class Meta:
        verbose_name = _('DjangoQL query')
        verbose_name_plural = _('DjangoQL queries')
        ordering = ['label']

    def __str__(self):
        return truncatechars(self.label or self.text, 50)

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self.__str__()
        super(Query, self).save(*args, **kwargs)
