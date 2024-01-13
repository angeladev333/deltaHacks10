from flask import Flask, request, render_template
from moviepy.editor import VideoFileClip
import speech_recognition as sr
import os

from get_theme import theme_prompts

app = Flask(__name__)

uploads_dir = os.path.join(app.instance_path, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return 'No video file part', 400

    video = request.files['video']
    theme = request.form['theme']
    theme_prompt = "Ensure a professional tone, with appropriate marketing music"

    if video.filename == '':
        return 'No selected file', 400

    if video:
        video_path = os.path.join(uploads_dir, video.filename)
        video.save(video_path)

        # extract audio from video
        video_clip = VideoFileClip(video_path)
        audio_path = video_path + '.wav'
        video_clip.audio.write_audiofile(audio_path)

        # transcribe audio to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            try:
                transcript = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                return 'Speech recognition could not understand audio', 500
            except sr.RequestError as e:
                return f'Could not request results from Google Speech Recognition service; {e}', 500

        # TODO: do sentiment analysis on transcript (:eyes) combined with the theme prompt
        if theme in theme_prompts:
            theme_prompt = theme_prompts[theme]

        return render_template('result.html', transcript=transcript, video_filename=os.path.relpath(video_path, uploads_dir), theme_prompt=theme_prompt)

        # meis amis


if __name__ == '__main__':
    app.run(debug=False)
