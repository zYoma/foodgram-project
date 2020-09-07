
def purchases_processor(request):
    """ Колличество рецептов в списке покупок для отображения в шапке сайта. """
    if request.user.is_authenticated:
        purchases_count =  request.user.shopping_lists.count()
    else:
        purchases_count = len(request.session.get('shopping_list', []))

    return {'purchases_count': purchases_count}
