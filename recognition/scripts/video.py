import moviepy.editor as mp
from pydub import AudioSegment
import noisereduce as nr
import numpy as np
import os

def convert_path_to_unix_style(path):
    return path.replace("C:\\", "/mnt/c/").replace("\\", "/")

def extract_audio_from_video(video_path):
    video = mp.VideoFileClip(video_path)
    audio_path = "extracted_audio.wav"
    video.audio.write_audiofile(audio_path)
    return audio_path

def reduce_noise(audio_path):
    audio = AudioSegment.from_wav(audio_path)
    samples = np.array(audio.get_array_of_samples())
    reduced_noise_samples = nr.reduce_noise(y=samples, sr=audio.frame_rate)
    reduced_noise_audio = AudioSegment(
        reduced_noise_samples.tobytes(),
        frame_rate=audio.frame_rate,
        sample_width=audio.sample_width,
        channels=audio.channels
    )
    cleaned_audio_path = "cleaned_audio.wav"
    reduced_noise_audio.export(cleaned_audio_path, format="wav")
    return cleaned_audio_path

def combine_audio_with_video(video_path, cleaned_audio_path):
    video = mp.VideoFileClip(video_path)
    cleaned_audio = mp.AudioFileClip(cleaned_audio_path)
    final_video = video.set_audio(cleaned_audio)
    output_path = "final_output_video.mp4"
    final_video.write_videofile(output_path)
    return output_path

def main(video_path):
    unix_video_path = convert_path_to_unix_style(video_path)
    audio_path = extract_audio_from_video(unix_video_path)
    cleaned_audio_path = reduce_noise(audio_path)
    final_video_path = combine_audio_with_video(unix_video_path, cleaned_audio_path)
    print(f"Final video saved at: {final_video_path}")

if __name__ == "__main__":
    video_path = "/face_recognition_project/Video_1.Frontal.MOV" 
    main(video_path)


#  isme 91 csv files hain. 
# inke H column me 2 logon ki conversation  hai 
# is conversation me dono person ke name and country mention hai wo extract karne hain chatgpt api use karke