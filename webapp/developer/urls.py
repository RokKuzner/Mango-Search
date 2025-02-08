from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('request-website-indexing', views.request_website_indexing, name='request website indexing'),
    path('get-last-website-index-time', views.get_last_website_index_time, name='get last website index time'),
]