import requests
import time
import shutil
import os
import tempfile
import moviepy.editor as mp

API_KEY = '3cf8fc27af3f160bfe9f65a5dbd01ecf'

# API endpoints
UPLOAD_ENDPOINT = 'https://api.audo.ai/v1/upload'
NOISE_REMOVAL_ENDPOINT = 'https://api.audo.ai/v1/remove-noise'
STATUS_ENDPOINT = 'https://api.audo.ai/v1/remove-noise/{job_id}/status'
BASE_DOWNLOAD_URL = 'https://api.audo.ai/v1'

def upload_file(file_path):
    with open(file_path, 'rb') as file:
        response = requests.post(UPLOAD_ENDPOINT, headers={'x-api-key': API_KEY}, files={'file': file})
        response.raise_for_status()
        return response.json()['fileId']

def remove_noise(file_id):
    response = requests.post(NOISE_REMOVAL_ENDPOINT, headers={'x-api-key': API_KEY, 'Content-Type': 'application/json'}, json={'input': file_id})
    response.raise_for_status()
    return response.json()['jobId']

def check_status(job_id):
    while True:
        response = requests.get(STATUS_ENDPOINT.format(job_id=job_id), headers={'x-api-key': API_KEY})
        response.raise_for_status()
        status_json = response.json()
        print('Job status response:', status_json)
        
        if status_json.get('state') == 'succeeded':
            return status_json['downloadPath']
        elif status_json.get('state') == 'failed':
            raise RuntimeError('Noise removal job failed')
        
        print('Job still processing, waiting for 10 seconds...')
        time.sleep(10)

def download_file(download_path, output_path):
    download_url = BASE_DOWNLOAD_URL + download_path
    response = requests.get(download_url, headers={'x-api-key': API_KEY}, stream=True)
    response.raise_for_status()
    with open(output_path, 'wb') as file:
        shutil.copyfileobj(response.raw, file)

def main(input_file, output_file):
    start_time = time.time()
    
    print('Extracting audio from video...')
    video = mp.VideoFileClip(input_file)
    audio_path = tempfile.mktemp(suffix='.wav')
    video.audio.write_audiofile(audio_path)

    print('Uploading audio file...')
    file_id = upload_file(audio_path)
    print(f'✅ File uploaded. File ID: {file_id}')

    print('Removing noise from audio...')
    job_id = remove_noise(file_id)
    print(f'✅✅ Noise removal job started. Job ID: {job_id}')

    print('Checking job status...')
    download_path = check_status(job_id)
    print(f'✅✅✅ Noise removal completed. Download Path: {download_path}')

    cleaned_audio_path = tempfile.mktemp(suffix='.wav')
    print('Downloading cleaned audio file...')
    download_file(download_path, cleaned_audio_path)
    print(f'🔥 💫 🔥 Cleaned audio file saved to: {cleaned_audio_path}')

    print('Replacing audio in video with cleaned audio...')
    cleaned_audio = mp.AudioFileClip(cleaned_audio_path)
    final_video = video.set_audio(cleaned_audio)
    
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac')
    
    end_time = time.time()
    print(f'Final video with cleaned audio saved to: {output_file}')
    print(f'Time taken: {end_time - start_time:.2f} seconds')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Remove background noise from video.')
    parser.add_argument('input_file', type=str, help='Path to the input video file.')
    parser.add_argument('output_file', type=str, help='Path to save the output video file.')
    args = parser.parse_args()

    main(args.input_file, args.output_file)
