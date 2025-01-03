from django.http import HttpResponse, JsonResponse
from webapp.settings import BASE_DIR
import os
import datetime

STATIC_URL = os.path.join(BASE_DIR, "static")
JAVASCRIPT_URL = os.path.join(STATIC_URL, "javascript")
CSS_URL = os.path.join(STATIC_URL, "css")
ICONS_URL = os.path.join(STATIC_URL, "icons")

MEDIA_URL = os.path.join(BASE_DIR, "media")
AVATARS_URL = os.path.join(MEDIA_URL, "avatars")


# Views
def js(request):
    file = request.GET.get('file', None)
    file_name = f"{file}.js"

    file_path = os.path.join(JAVASCRIPT_URL, f"{file}.js")
    file_path = os.path.realpath(file_path) #Normailize the file_path

    #If file doesn't exist or it's outside the javascript folder
    if os.path.exists(file_path) == False or file_path.startswith(JAVASCRIPT_URL) == False:
        response = JsonResponse({"message": "the file doesn't exists or the requested file is outside static folder"})
        response['Content-Type'] = 'application/json'
        return response

    # Open the file in binary mode
    with open(file_path, "rb") as f:
        # Create an HttpResponse object
        response = HttpResponse(f.read(), content_type="text/javascript")

        # Set the Content-Disposition header
        response["Content-Disposition"] = f"inline; filename={file_name}"

        return response
    
def css(request):
    file = request.GET.get('file', None)
    file_name = f"{file}.css"

    file_path = os.path.join(CSS_URL, f"{file}.css")
    file_path = os.path.realpath(file_path) #Normailize the file_path

    #If file doesn't exist or it's outside the css folder
    if os.path.exists(file_path) == False or file_path.startswith(CSS_URL) == False:
        response = JsonResponse({"message": "the file doesn't exists or the requested file is outside static folder"})
        response['Content-Type'] = 'application/json'
        return response

    # Open the file in binary mode
    with open(file_path, "rb") as f:
        # Create an HttpResponse object
        response = HttpResponse(f.read(), content_type="text/css")

        # Set the Content-Disposition header
        response["Content-Disposition"] = f"inline; filename={file_name}"

        return response

def logo(request):
    file_path = os.path.join(ICONS_URL, "mango_logo.png")
    file_name = "friendface_logo.png"

    with open(file_path, "rb") as f:
        # Create an HttpResponse object
        response = HttpResponse(f.read(), content_type=f"image/png")

        # Set the Content-Disposition header
        response["Content-Disposition"] = f"inline; filename={file_name}"

        return response

def favicon(request):
    file_path = os.path.join(ICONS_URL, "favicon.ico")
    file_name = "favicon.ico"

    with open(file_path, "rb") as f:
        # Create an HttpResponse object
        response = HttpResponse(f.read(), content_type=f"image/vnd.microsoft.icon")

        # Set the Content-Disposition header
        response["Content-Disposition"] = f"inline; filename={file_name}"

        return response

def icons(request):
    file = request.GET.get('file', None)
    file_name = file

    file_path = os.path.join(ICONS_URL, file)
    file_path = os.path.realpath(file_path) #Normailize the file_path

    #If file doesn't exist or it's outside the icons folder
    if os.path.exists(file_path) == False or file_path.startswith(ICONS_URL) == False:
        response = JsonResponse({"message": "the file doesn't exists or the requested file is outside static folder"})
        response['Content-Type'] = 'application/json'
        return response
    
    #Get file extension
    not_important, file_extension = os.path.splitext(file_path)

    if file_extension == ".jpg":
        file_extension = ".jpeg"

    # Open the image in binary mode
    with open(file_path, "rb") as f:
        # Create an HttpResponse object
        response = HttpResponse(f.read(), content_type=f"image/{file_extension[1:]}")

        # Set the Content-Disposition header
        response["Content-Disposition"] = f"inline; filename={file_name}"

        return response