from django import template
import logging

register = template.Library()
logger = logging.getLogger('MYAPP')

#<a href="?{% url_replace request 'page' paginator.next_page_number %}">

@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()

@register.simple_tag
def session_replace(request, field, value):
    session = request.session
    session[field] = value
    return request.GET.urlencode()

@register.simple_tag
def session_delete(request, field):
    session = request.session
    del session[field]
    logging.error(session[field])
    return request.GET.urlencode()