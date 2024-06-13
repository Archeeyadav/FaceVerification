from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from PIL import Image
from io import BytesIO
import face_recognition
import numpy as np
from .models import Face
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
from django.conf import settings
from urllib.parse import urljoin
import uuid


@csrf_exempt
def face_recognition_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image_url = data.get("image_url")
            if not image_url:
                return JsonResponse({"error": "No image URL provided"}, status=400)

            # Check if image URL already exists in the database
            if Face.objects.filter(image_url=image_url).exists():
                existing_face = Face.objects.get(image_url=image_url)
                matches = []
                new_encoding = existing_face.get_encoding()

                # Match against database
                for face in Face.objects.exclude(image_url=image_url):
                    stored_encoding = face.get_encoding()
                    distance = face_recognition.face_distance(
                        [stored_encoding], new_encoding
                    )[0]
                    if distance < 0.6:  # Threshold for match
                        matches.append(
                            {"image_url": face.image_url, "distance": distance}
                        )

                # Retrieve all image URLs from the database
                all_image_urls = [face.image_url for face in Face.objects.all()]
                return JsonResponse(
                    {"matches": matches, "all_image_urls": all_image_urls}
                )

            try:
                # Download image
                response = requests.get(image_url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                else:
                    return JsonResponse(
                        {"error": "Failed to download image"},
                        status=response.status_code,
                    )
            except Exception as e:
                return JsonResponse(
                    {"error": "Error downloading image: {}".format(str(e))}, status=500
                )

            image_np = np.array(image)

            # Face encodings
            encodings = face_recognition.face_encodings(image_np)
            if not encodings:
                return JsonResponse(
                    {"error": "No faces found in the image"}, status=400
                )

            new_encoding = encodings[0]

            # Match against database
            matches = []
            for face in Face.objects.all():
                stored_encoding = face.get_encoding()
                distance = face_recognition.face_distance(
                    [stored_encoding], new_encoding
                )[0]
                if distance < 0.6:  # Threshold for match
                    matches.append({"image_url": face.image_url, "distance": distance})

            # Store the new image and encoding
            face = Face(image_url=image_url)
            face.set_encoding(new_encoding)
            face.save()

            # Retrieve all image URLs from the database
            all_image_urls = [face.image_url for face in Face.objects.all()]

            return JsonResponse({"matches": matches, "all_image_urls": all_image_urls})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import status


class HandleAllMethods(APIView):
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get(self, request, *args, **kwargs):
        data = {
            "method": "GET",
            "query_params": request.query_params.dict(),
        }
        print(data)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = {
            "method": "POST",
            "body": request.data,
        }
        print(data)

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        data = {
            "method": "PUT",
            "body": request.data,
        }
        print(data)

        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        data = {
            "method": "PATCH",
            "body": request.data,
        }
        print(data)

        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        data = {
            "method": "DELETE",
        }
        print(data)
        return Response(data, status=status.HTTP_200_OK)



# import json
# import cv2
# import numpy as np
# import face_recognition
# from PIL import Image
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Face  # Adjust the import based on your actual project structure
# from django.core.files.storage import FileSystemStorage

# @csrf_exempt
# def face_recognition_api(request):
#     if request.method == 'POST':
#         try:
#             # Handle the uploaded file (video)
#             video_file = request.FILES.get('video')
#             if not video_file:
#                 return JsonResponse({'error': 'No video file provided'}, status=400)
            
#             # Save the video file to a temporary location
#             fs = FileSystemStorage()
#             video_path = fs.save('temp_video.mp4', video_file)
#             video_path = fs.path(video_path)

#             # Extract the first frame
#             output_image_path = 'first_frame.jpg'
#             if not extract_first_frame(video_path, output_image_path):
#                 return JsonResponse({'error': 'Failed to extract first frame from video'}, status=500)

#             # Read the extracted frame
#             with open(output_image_path, 'rb') as img_file:
#                 image = Image.open(img_file)
#                 image_np = np.array(image)

#             # Face encodings
#             encodings = face_recognition.face_encodings(image_np)
#             if not encodings:
#                 return JsonResponse({'error': 'No faces found in the image'}, status=400)
            
#             new_encoding = encodings[0]

#             # Check if image URL already exists in the database
#             if Face.objects.filter(image_url=output_image_path).exists():
#                 existing_face = Face.objects.get(image_url=output_image_path)
#                 matches = []
#                 new_encoding = existing_face.get_encoding()

#                 # Match against database
#                 for face in Face.objects.exclude(image_url=output_image_path):
#                     stored_encoding = face.get_encoding()
#                     distance = face_recognition.face_distance([stored_encoding], new_encoding)[0]
#                     if distance < 0.6:  # Threshold for match
#                         matches.append({'image_url': face.image_url, 'distance': distance})

#                 # Retrieve all image URLs from the database
#                 all_image_urls = [face.image_url for face in Face.objects.all()]
#                 return JsonResponse({'matches': matches, 'all_image_urls': all_image_urls})

#             # Store the new image and encoding
#             face = Face(image_url=output_image_path)
#             face.set_encoding(new_encoding)
#             face.save()

#             # Retrieve all image URLs from the database
#             all_image_urls = [face.image_url for face in Face.objects.all()]

#             return JsonResponse({'matches': matches, 'all_image_urls': all_image_urls})
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=405)

# def extract_first_frame(video_path, output_image_path):
#     # Open the video file
#     cap = cv2.VideoCapture(video_path)
    
#     # Check if the video opened successfully
#     if not cap.isOpened():
#         print(f"Error opening video file: {video_path}")
#         return False
    
#     # Read the first frame
#     ret, frame = cap.read()
    
#     if ret:
#         # Save the first frame as a JPEG file
#         cv2.imwrite(output_image_path, frame)
#         print(f"First frame saved as: {output_image_path}")
#     else:
#         print("Error reading first frame.")
#         return False
    
#     # Release the video capture object
#     cap.release()
#     return True
