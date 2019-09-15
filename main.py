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
import base64
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums

filepath = "C:/Users/aryan/Data/Trump.mp4"
output_filepath = "C:/Users/aryan/Data"
bucketname = "gs://biasengine/"

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
        extract_audio(f.filename)
        upload_to_bucket(f.filename)
        sample_long_running_recognize("gs://biasengine/videos/"+f.filename.split('.')[0]+".wav")

        return f.filename + " uploaded succssfully!"
    else:
        return "Failed!"

def extract_audio(file_name):
    #command = "ffmpeg -i C:/Users/aryan/Data/Trump.mp4 C:/Users/aryan/Data/Trump.wav"
    command = "ffmpeg -i " + file_name + " " + file_name.split('.')[0] + ".wav"
    subprocess.call(command, shell=True)

def upload_to_bucket(file_name):
    #command = "gsutil cp C:/Users/aryan/Data/Trump.wav gs://biasengine/videos/"
    command = "gsutil cp " + file_name.split('.')[0] + ".wav gs://biasengine/videos/"
    subprocess.call(command, shell=True)

def upload_to_bucket_txt():
    command = "gsutil cp Result.txt gs://biasengine/text/"
    subprocess.call(command, shell=True)

def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getnchannels()
        channels = wave_file.getnchannels()
        return frame_rate, channels

def sample_recognize(local_file_path):
    """
    Transcribe a short audio file using synchronous speech recognition

    Args:
      local_file_path Path to local audio file, e.g. /path/audio.wav
    """

    client = speech_v1.SpeechClient()

    # local_file_path = 'resources/brooklyn_bridge.raw'

    # The language of the supplied audio
    language_code = "en-US"

    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 44100

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        "encoding": encoding,
    }
    with io.open(local_file_path, "rb") as f:
        content = f.read()
    audio = {"content": content}

    response = client.recognize(config, audio)
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        print(u"Transcript: {}".format(alternative.transcript))


def sample_long_running_recognize(storage_uri):
    """
    Transcribe long audio file from Cloud Storage using asynchronous speech
    recognition

    Args:
      storage_uri URI for audio file in Cloud Storage, e.g. gs://[BUCKET]/[FILE]
    """

    client = speech_v1.SpeechClient()

    # storage_uri = 'gs://cloud-samples-data/speech/brooklyn_bridge.raw'

    # Sample rate in Hertz of the audio data sent
    #for file_name in os.listdir("C:/Users/aryan/Data"):
    #    with wave.open(file_name, "rb") as wave_file:
    #        sample_rate_hertz = wave_file.getframeate()
    sample_rate_hertz = 44100

    # The language of the supplied audio
    language_code = "en-US"

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "sample_rate_hertz": sample_rate_hertz,
        "language_code": language_code,
        "encoding": encoding,
    }
    audio = {"uri": storage_uri}

    operation = client.long_running_recognize(config, audio)

    print(u"Waiting for operation to complete...")
    response = operation.result()

    transcript = ''
    f = open("Result.txt", "w+")
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        _str = u"Transcript: {}".format(alternative.transcript)
        print(_str)
        f.write(_str)

    upload_to_bucket_txt()
    f.close()

if __name__ == "__main__":

    app.run(debug=True)
    #upload_to_bucket()
    #sample_long_running_recognize("gs://biasengine/videos/Trump.wav")
    #sample_recognize("C:/Users/aryan/Data/Trump2.wav")