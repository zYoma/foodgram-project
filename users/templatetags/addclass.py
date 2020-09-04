from django import template

register = template.Library()

@register.filter 
def addclass(field, css):
    '''Тег для добавления класса виджету формы'''
    return field.as_widget(attrs={"class": css})