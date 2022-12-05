from flask import Flask, url_for, render_template, request, send_file
import os
from pptx import Presentation
from pptx.util import Inches
import shutil
import gunicorn

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thekey'
app.config['UPLOAD_FOLDER'] = 'tmp'


root = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
narrated_path = str()


@app.route('/make_pptx', methods=['GET', 'POST'])
def make_pptx():
    global pptx_path
    if request.method == 'POST': 
        files = request.files.getlist('file') # get list of all uploaded files
        audio_path = os.path.join(root, 'audio') # make path to folder with all audio files
        if not os.path.exists(audio_path): # if the folder doesn't exist already, make it
            os.mkdir(audio_path)

        for file in files: # iterate through every file
            filename = file.filename
            if filename == '':
                return 'No file selected'
            
            # save audio files in audio folder
            elif filename.endswith('.mp3') or filename.endswith('.m4a') or filename.endswith('.wav'):
                path = os.path.join(audio_path, filename)
                file.save(path)

            # save pptx file
            else:
                pptx_path = os.path.join(root, filename)
                file.save(pptx_path)

        narrated_file = make_narrated_pptx(pptx_path, audio_path) # create narrated file

    return send_file(narrated_file, as_attachment=True) # download narrated.pptx file


@app.route('/', methods=['GET', 'POST'])
def index():
    delete(root) # empty the tmp folder
    return render_template('pptx_upload.html')



def make_narrated_pptx(pptx_path, audio_folder_path):
    left = top = width = height = Inches(0.2)
    picture_path = r"static/mic.png"
    prs = Presentation(fr"{pptx_path}")
    audio_folder = fr"{audio_folder_path}"

    for filename in os.listdir(audio_folder): # go through every audio file
        audio_path = os.path.join(audio_folder, filename) # create path to audio file
        file_number = int(os.path.splitext(filename)[0]) - 1 # get slide number from audio file name
        prs.slides[file_number].shapes.add_movie(audio_path, # add audio file to slide
                                                    left,top,width,height,
                                                    poster_frame_image=picture_path,
                                                    mime_type='video/unknown')
    
    narrated_path = os.path.join(app.config['UPLOAD_FOLDER'], 'narrated.pptx') # make path to narrated pptx file
    prs.save(narrated_path) # save file to path
    return narrated_path
    


def delete(folder): # this function deletes everything inside the folder, but not the folder itself
    if os.path.exists(folder): # first it checks if the folder exists
        for item in os.listdir(folder): # then it iterates through every item in the folder
            item_path = os.path.join(folder, item) # gets the path
            if os.path.isfile(item_path): # checks if the item is a file
                os.remove(item_path) # removes file

            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)


  
if __name__ == '__main__':
    app.run(debug = True)