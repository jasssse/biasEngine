import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

###############################################

from pydub import AudioSegment
import io
import os
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import wave
from google.cloud import storage

filepath = "C:/Users/aryan/Data/"
output_filepath = "C:/Users/aryan/Data"
bucketname = "callsaudiofiles"

app = Flask(__name__)

@app.route('/')
def hello_world():
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

#########################################

def mp3_to_wav(audio_file):
    print("Converting____________________________-")
    if audio_file.split('.')[1] == "mp3":
        sound = AudioSegment.from_mp3(audio_file)
        audio_file = audio_file.split('.')[0] + ".wav"
        sound.export(audio_file, format="wav")

def stereo_to_mono(audio_file):
    sound = AudioSegment.from_wav(audio_file)
    sound = sound.set_channels(1)
    sound.export(audio_file, format="wav")

def frame_rate_channel(audio_file):
    with wave.open(audio_file, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate, channels

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

def delete_blob(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

def google_transcribe(audio_file):
    file_name = filepath + audio_file
    mp3_to_wav(file_name)

    frame_rate, channels = frame_rate_channel(file_name)

    if channels> 1:
        stereo_to_mono(file_name)

    bucket_name = bucketname
    source_file_name = filepath + audio_file
    destination_blob_name = audio_file

    upload_blob(bucket_name, source_file_name, destination_blob_name)

    gcs_uri = 'gs://' + bucketname + '/' + audio_file
    transcript = ''

    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=frame_rate,
    language_code='en-US')

    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)

    for result in response.results:
        transcript += result.alternatives[0].transcript

    delete_blob(bucket_name, destination_blob_name)
    return transcript

def write_transcript(transcript_filename, transcript):
    f = open(output_filepath + transcript_filename,"w+")
    f.write(transcript)
    f.close()

if __name__ == "__main__":
    #app.run(debug=True)
    for audio_file_name in os.listdir(filepath):
        transcript = google_transcribe(audio_file_name)
        transcript_filename = audio_file_name.split('.')[0] + "txt"
        write_transcript(transcript_filename, transcript)