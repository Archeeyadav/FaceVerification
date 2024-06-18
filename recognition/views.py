from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from PIL import Image
from io import BytesIO
import face_recognition
import numpy as np
from .models import Face
import os
import shutil
import tempfile
import cv2
import time

@csrf_exempt
def face_recognition_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image_url = data.get("image_url")
            if not image_url:
                return JsonResponse({"error": "No image URL provided"}, status=400)

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

            all_image_urls = [face.image_url for face in Face.objects.all()]

            return JsonResponse({"matches": matches, "all_image_urls": all_image_urls})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def extract_first_frame(request):
    if request.method == "POST":
        video_file = request.FILES.get("video")
        if not video_file:
            return JsonResponse({"error": "No video file uploaded."}, status=400)

        num_copies = int(request.POST.get("num_copies", 10))
        start_time = time.time()
        # Save the video file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_video:
            for chunk in video_file.chunks():
                temp_video.write(chunk)
            temp_video_path = temp_video.name

        copies_directory = tempfile.mkdtemp()
        for i in range(1, num_copies + 1):
            copy_path = os.path.join(copies_directory, f"copy_{i}.mp4")
            shutil.copyfile(temp_video_path, copy_path)

        # Extract the first frame from each copy
        for i in range(1, num_copies + 1):
            copy_path = os.path.join(copies_directory, f"copy_{i}.mp4")
            cap = cv2.VideoCapture(copy_path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                cv2.imwrite(f"first_frame_copy_{i}.jpg", frame)
            else:
                return JsonResponse(
                    {"error": f"Failed to extract first frame from copy_{i}.mp4"},
                    status=400,
                )

        end_time = time.time()
        # Delete temporary files and directory
        os.unlink(temp_video_path)
        shutil.rmtree(copies_directory)

        duration = end_time - start_time
        return JsonResponse(
            {
                "message": f"First frames extracted and saved from {num_copies} copies. Time taken: {duration:.2f} seconds"
            }
        )
