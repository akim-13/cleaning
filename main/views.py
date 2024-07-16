from django.http import HttpResponse

def index(request):
    return HttpResponse("This should be a registration/login page.")