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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_url = data.get('image_url')
            if not image_url:
                return JsonResponse({'error': 'No image URL provided'}, status=400)
            
            # Check if image URL already exists in the database
            if Face.objects.filter(image_url=image_url).exists():
                existing_face = Face.objects.get(image_url=image_url)
                matches = []
                new_encoding = existing_face.get_encoding()
                
                # Match against database
                for face in Face.objects.exclude(image_url=image_url):
                    stored_encoding = face.get_encoding()
                    distance = face_recognition.face_distance([stored_encoding], new_encoding)[0]
                    if distance < 0.6:  # Threshold for match
                        matches.append({'image_url': face.image_url, 'distance': distance})

                # Retrieve all image URLs from the database
                all_image_urls = [face.image_url for face in Face.objects.all()]
                return JsonResponse({'matches': matches, 'all_image_urls': all_image_urls})

            try:
                # Download image
                response = requests.get(image_url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                else:
                    return JsonResponse({'error': 'Failed to download image'}, status=response.status_code)
            except Exception as e:
                return JsonResponse({'error': 'Error downloading image: {}'.format(str(e))}, status=500)
            
            image_np = np.array(image)

            # Face encodings
            encodings = face_recognition.face_encodings(image_np)
            if not encodings:
                return JsonResponse({'error': 'No faces found in the image'}, status=400)
            
            new_encoding = encodings[0]

            # Match against database
            matches = []
            for face in Face.objects.all():
                stored_encoding = face.get_encoding()
                distance = face_recognition.face_distance([stored_encoding], new_encoding)[0]
                if distance < 0.6:  # Threshold for match
                    matches.append({'image_url': face.image_url, 'distance': distance})

            # Store the new image and encoding
            face = Face(image_url=image_url)
            face.set_encoding(new_encoding)
            face.save()

            # Retrieve all image URLs from the database
            all_image_urls = [face.image_url for face in Face.objects.all()]

            return JsonResponse({'matches': matches, 'all_image_urls': all_image_urls})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    

 