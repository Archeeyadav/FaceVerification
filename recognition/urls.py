from django.urls import path
from .views import face_recognition_api, extract_first_frame

urlpatterns = [
    path("api/recognize/", face_recognition_api, name="face_recognition_api"),
    path('api/frame/', extract_first_frame, name='extract_first_frame'),


]
