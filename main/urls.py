from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('main/', views.main, name='main'),
    path('<location>/fill-out/', views.fill_out, name='fill_out'),
    path('<location>/summary/', views.summary, name='summary'),
    path('<location>/summary/pdf/', views.summary_pdf, name='summary_pdf'),
    path('configurator/', views.configurator, name='configurator'),
]
