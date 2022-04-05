from django import template
from django.urls import reverse_lazy
register = template.Library()


@register.simple_tag(takes_context=True)
def get_url(context, action, obj=None):
    '''
    example 1  " get_url 'list' "
    example 2  " get_url 'create' "
    example 3  " get_url 'detail' obj  "
    the first argument is action create or list or detail or update or delete
    the second argument is a model object
    the name of url pattern so as to work
    app:model-create
    app:model-update
    app:model-delete
    app:model-detail
    '''
    model = context['model']
    lower_name = model.__name__.lower()
    app = model._meta.app_label
    url_string = '{}:{}-{}'.format(app, lower_name, action)
    if obj:
        lower_name = obj.__class__.__name__.lower()
        app = obj._meta.app_label
        url_string = '{}:{}-{}'.format(app, lower_name, action)
        url = reverse_lazy(url_string, kwargs={'pk': obj.pk})
    if not obj:
        url_string = '{}:{}-{}'.format(app, lower_name, action)
        url = reverse_lazy(url_string)
    return url


@register.simple_tag(takes_context=True)
def get_template_name(context, *args):
    model = context['model']
    app = model._meta.app_label
    lower_name = model.__name__.lower()
    template_name = "{}/partials/{}_list_partial.html".format(app,lower_name)
    return template_name