from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from gtts import gTTS
import speech_recognition as sr
from moviepy.editor import *
import os
from pydub import AudioSegment

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULT_FOLDER'] = 'results/'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        tts = gTTS(text=text, lang='en')
        mp3_audio_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio.mp3')
        wav_audio_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio.wav')
        output_video_filename = os.path.join(app.config['RESULT_FOLDER'], 'output.mp4')
        
        tts.save(mp3_audio_filename)
        
        # Convert MP3 to WAV
        sound = AudioSegment.from_mp3(mp3_audio_filename)
        sound.export(wav_audio_filename, format="wav")

        r = sr.Recognizer()
        with sr.AudioFile(wav_audio_filename) as source:
            audio = r.record(source)
        try:
            transcription = r.recognize_google(audio)
        except sr.UnknownValueError:
            transcription = "Could not understand audio"
        except sr.RequestError as e:
            transcription = f"Could not request results; {e}"
        
        duration = len(transcription) / 10   
        avatar = ImageClip('avatar.png').set_duration(duration)
        mouth = ImageClip('mouth.png').set_duration(duration)
        final_clip = CompositeVideoClip([avatar, mouth.set_position(('center', 'bottom'))])
        
        audio_clip = AudioFileClip(wav_audio_filename)
        final_clip = final_clip.set_audio(audio_clip)
        final_clip.write_videofile(output_video_filename, fps=30)
        
        return redirect(url_for('result'))
    return render_template('index.html')

@app.route('/result')
def result():
    return send_from_directory(app.config['RESULT_FOLDER'], 'output.mp4')

if __name__ == "__main__":
    app.run(debug=True)
