from django.shortcuts import render, redirect
from django.http import JsonResponse

# Create your views here.
def home(request):
    return render(request, "app/index.html")

def search(request):
    query = request.GET.get("q", None)

    if query == None:
        return redirect("/")

    return JsonResponse({"status":"success", "provided query":query})