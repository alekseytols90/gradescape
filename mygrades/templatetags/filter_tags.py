from django import template

register = template.Library()


@register.filter(name='index')
def index(data, index):
    print(data[index]['data'].items())
    return data[index]['data']

@register.filter
def hash(h, key):
    return h[key]
