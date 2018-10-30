from django import template

register = template.Library()


#<a href="?{% url_replace request 'page' paginator.next_page_number %}">

@register.simple_tag
def url_replace(request, field, value):

    dict_ = request.GET.copy()

    dict_[field] = value

    return dict_.urlencode()