from django.shortcuts import render
from django.shortcuts import redirect


def page_not_found(request, exception):
    return render(request, "404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "500.html", status=500)


def redirect_recipes(request):
    return redirect('index_url', permanent=True)