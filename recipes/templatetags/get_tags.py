from django import template

register = template.Library()

@register.filter 
def get_tags(request, tag):
    '''функция формирует значение для атрибута tag.
       Необходимо для работы фильтрации по тегам.
    '''
    if 'tag' in request.GET:
        t = request.GET.get('tag')
        t = t.split('__')
        if not tag in t:
            t.append(tag)
        else:
            t.remove(tag)

        if '' in t:
            t.remove('')

        result = '__'.join(t)
        return result

    return tag