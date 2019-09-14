import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

###############################################

from pydub import AudioSegment
import io
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import wave
from google.cloud import storage
import subprocess

filepath = "C:/Users/aryan/Data/Trump.mp4"
output_filepath = "C:/Users/aryan/Data"
bucketname = "callsaudiofiles"

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
    <h1>Hello World</h1>
    <p>click <a href="/upload">HERE</a> to upload.</p>
    </html>
    '''

@app.route('/upload')
def upload_file():
    # Remember to change audio/* to video/*
    return '''
    <html>
   <body>
      <form action = "http://localhost:5000/uploader" method = "POST" 
         enctype = "multipart/form-data">
         <input type =file name=file accept=audio/*> 
         <input type = "submit"/>
      </form>
   </body>
</html>
'''

@app.route('/uploader', methods = ['GET', 'POST'])
def uploaded_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return f.filename + " uploaded succssfully!"
    else:
        return "Failed!"

def extract_audio(audio_file_name):
    command = "ffmpeg -i " + audio_file_name + " C:/Users/aryan/Data/Trump.wav"
    subprocess.call(command, shell=True)


if __name__ == "__main__":
   # app.run(debug=True)
    extract_audio("C:/Users/aryan/Data/Trump.mp4")
    #for audio_file_name in os.listdir(filepath):
    #    transcript = google_transcribe("C:/Users/aryan/Data/Trump.wav")
    #    transcript_filename = "C:/Users/aryan/Data/Trump.txt"
    #    write_transcript(transcript_filename, transcript)