import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

###############################################

#from pydub import AudioSegment
#import io
#import os
#from google.cloud import speech
#from google.cloud.speech import enums
#from google.cloud.speech import types
#import wave
#from google.cloud import storage

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '''
    <html>
    <h1>Hello World</h1>
    <p>click <a href="/upload">here</a> to upload.</p>
    </html>
    '''

@app.route('/upload')
def upload_file():
    return '''
    <html>
   <body>
      <form action = "http://localhost:5000/uploader" method = "POST" 
         enctype = "multipart/form-data">
         <input type =file name=file accept=video/*>
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

#def mp3_to_wav(audio_file):
#    if audio_file.split('.')[1] == "mp3":
#        sound = AudioSegment.from_mp3(audio_file)
#        audio_file = audio_file.split('.')[0] + ".wav"
#        sound.export(audio_file, format="wav")

if __name__ == "__main__":
    app.run(debug=True)