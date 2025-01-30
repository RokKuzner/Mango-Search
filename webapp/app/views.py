from django.shortcuts import render, redirect
from django.http import JsonResponse
import requests
import urllib.parse

api_url = "http://api:5000"
api_search_url = api_url + "/search?q="

# Create your views here.
def home(request):
    return render(request, "app/index.html")

def search(request):
    query = request.GET.get("q", None)

    if not query:
        return redirect("/")
    
    # Get the results via api
    api_full_request_url = api_search_url+urllib.parse.quote(query)
    res = requests.get(api_full_request_url)
    results = res.json()["result"]

    return render(request, "app/search.html", {
        "query":query,
        "results":results,
    })