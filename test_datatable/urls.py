from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('init_db/', views.init_db, name='init_db'),
]