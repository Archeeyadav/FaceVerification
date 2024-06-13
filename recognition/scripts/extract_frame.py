import os
import cv2
import shutil
import tempfile
import time
import argparse

def extract_first_frame(video_path, num_copies=10):
    start_time = time.time()
    
    # Save the video file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_video:
        with open(video_path, 'rb') as f:
            temp_video.write(f.read())
        temp_video_path = temp_video.name

    copies_directory = tempfile.mkdtemp()

    for i in range(1, num_copies + 1):
        copy_path = os.path.join(copies_directory, f"copy_{i}.mp4")
        shutil.copyfile(temp_video_path, copy_path)

    for i in range(1, num_copies + 1):
        copy_path = os.path.join(copies_directory, f"copy_{i}.mp4")
        cap = cv2.VideoCapture(copy_path)
        ret, frame = cap.read()
        cap.release()
        if ret:
            cv2.imwrite(f"first_frame_copy_{i}.jpg", frame)
        else:
            print(f"Failed to extract first frame from copy_{i}.mp4")
            return

    end_time = time.time()

    os.unlink(temp_video_path)
    shutil.rmtree(copies_directory)

    duration = end_time - start_time
    print(f"✅ First frames extracted and saved from {num_copies} copies. Time taken: {duration:.2f} seconds")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract first frame from video copies.')
    parser.add_argument('video_path', type=str, help='Path to the video file')
    parser.add_argument('--num_copies', type=int, default=10, help='Number of copies to create')

    args = parser.parse_args()
    extract_first_frame(args.video_path, args.num_copies)
