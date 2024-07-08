#from django.http import HttpResponse
from django.shortcuts import render

def homepage(request):
   # return HttpResponse("Hello world! Pidor.")
   return render(request, 'home.html')

def about(request):
    # return HttpResponse("That's about page.")
    return render(request, 'about.html')