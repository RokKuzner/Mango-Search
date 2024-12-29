from . import views
from django.urls import path

urlpatterns = [
  path('static/js', views.js, name='javascript'),
  path('static/css', views.css, name='css'),
  path('static/logo', views.logo, name='logo'),
  path('static/favicon', views.favicon, name='favicon'),
  path('static/icons', views.icons, name='icons'),
]