from django.shortcuts import render
from django.views import View
import requests

api_url = "http://api:5000"
api_request_website_index_url = api_url + "/request_website_index"
api_get_last_website_index_time = api_url + "/get_last_website_index_time"

# Create your views here.
def home(request):
    return render(request, "developer/dev_index.html")

class RequestWebsiteIndexingView(View):
    request_success = None
    request_message = ""

    def post(self, request):
        post_data =  request.POST.dict()

        if "url_to_index" not in post_data:
            return render(request, "developer/request_website_indexing.html", {"request_success": False, "request_message": "URL was not provided"})
        
        # Request website index via the api
        res = requests.post(api_request_website_index_url, json={"url":str(post_data["url_to_index"])})
        res_json = res.json()

        if res.status_code != 200:
            self.request_message = res_json["display_msg"]
            self.request_success = False
        else:
            self.request_message = "Success! Your website will be indexed shortly!"
            self.request_success = True
        
        return render(request, "developer/request_website_indexing.html", {"request_success": self.request_success, "request_message": self.request_message})
    def get(self, request):
        return render(request, "developer/request_website_indexing.html", {"request_success": None})
    
def get_last_website_index_time(request):
    request_success = None
    request_message = ""

    if request.method == "POST":
        post_data =  request.POST.dict()

        if "url" not in post_data:
            return render(request, "developer/get_last_website_index_time.html", {"request_success": False, "request_message": "URL was not provided"})
        
        # Request website index time via the api
        res = requests.get(api_get_last_website_index_time, json={"url":str(post_data["url"])})
        res_json = res.json()

        if res.status_code != 200:
            request_message = res_json["display_msg"]
            request_success = False
        else:
            request_message = f"Your website was indexed at: {res_json["index_time"]}"
            request_success = True
        
        return render(request, "developer/get_last_website_index_time.html", {"request_success": request_success, "request_message": request_message})
    elif request.method == "GET":
        return render(request, "developer/get_last_website_index_time.html", {"request_success": None})