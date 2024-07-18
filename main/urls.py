from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('<location>/fill-out/', views.fill_out, name='fill_out'),
    path('<location>/summary/', views.summary, name='summary'),
    path('<location>/configure/', views.configure, name='configurator'),
]