from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    """
    docstring
    """
    return HttpResponse("<h1 align=\"center\">This is the home page</h1>")