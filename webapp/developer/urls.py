from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('request-website-indexing', views.RequestWebsiteIndexingView.as_view(), name='request website indexing'),
    path('get-last-website-index-time', views.get_last_website_index_time, name='get last website index time'),
]