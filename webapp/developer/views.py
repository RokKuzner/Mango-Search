from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "developer/dev_index.html")

def request_website_indexing(request):
    return render(request, "developer/request_website_indexing.html")