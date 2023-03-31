from flask import Flask, url_for, render_template, request, send_file, session
import os
from pptx import Presentation
from pptx.util import Inches
import collections
import collections.abc
import shutil
import gunicorn
import tempfile
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import re
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thekey'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'tmp'


@app.route('/', methods=['GET', 'POST'])
def index():
    temp_dir = create_temp_dir()
    session['temp_dir'] = temp_dir

    audio_path = os.path.join(temp_dir, 'audio')
    os.mkdir(audio_path)
    session['audio_path'] = audio_path
    session.modified = True

    return render_template('pptx_upload.html')



# Create a new temporary directory for each user's files
def create_temp_dir():
    temp_dir = tempfile.mkdtemp()
    return temp_dir

def empty(folder):                                  # this function emptys the folder
    if os.path.exists(folder):                      # first it checks if the folder exists
        for item in os.listdir(folder):             # then it iterates through every item in the folder
            item_path = os.path.join(folder, item)  # gets the path
            if os.path.isfile(item_path):           # checks if the item is a file
                os.remove(item_path)                # removes file

            elif os.path.isdir(item_path):          # else if folder
                shutil.rmtree(item_path)            # delete folder

# Update the make_pptx() function
@app.route('/make_pptx', methods=['GET', 'POST'])
def make_pptx():
    if request.method == 'POST':
        files = request.files.getlist('file')  # get list of all uploaded files

        # Create a new temporary directory
        temp_dir = session.get('temp_dir')
        audio_path = session.get('audio_path')  

        for file in files:  # iterate through every file
            filename = file.filename
            if filename == '':
                return 'No file selected'

            # save audio files in audio folder
            elif filename.endswith('.mp3') or filename.endswith('.m4a') or filename.endswith('.wav'):
                path = os.path.join(audio_path, filename)
                file.save(path)
                print(f'Audio file saved: {path}')

            # save pptx file
            else:
                pptx_path = os.path.join(temp_dir, filename)
                session['pptx_path'] = pptx_path
                session.modified = True
                file.save(pptx_path)
                print(f'Powerpoint saved: {pptx_path}')

    return 'Files uploaded successfully'
   
        
@app.route('/process_data', methods=['GET', 'POST'])
def process_data():
    temp_dir = session.get('temp_dir')
    pptx_path = session.get('pptx_path')
    audio_path = session.get('audio_path')

    narrated_file = make_narrated_pptx(pptx_path, audio_path, temp_dir)
    session['narrated_file'] = narrated_file
    return render_template('download.html', filename=narrated_file)


@app.route('/download')
def download():
    filename = request.args.get('filename')
    print('Successful download')
    return send_file(filename, as_attachment=True)




def make_narrated_pptx(pptx_path, audio_folder_path, temp_dir):
    print(f'Path for pptx passed to make_narrated_pptx(): {pptx_path}')
    print(f'Path for audio folder passed as: {audio_folder_path}')
    print(f'Temporary directory passed as: {temp_dir}')
    left = top = width = height = Inches(0.2)
    picture_path = r"static/mic.png"
    prs = Presentation(pptx_path)
    audio_folder = fr"{audio_folder_path}"
    slide_number_arr = [] # array with numbers of all slides with audio

    for filename in os.listdir(audio_folder): # go through every audio file
        audio_path = os.path.join(audio_folder, filename) # create path to audio file
        slide_number = int(os.path.splitext(filename)[0]) - 1 # get slide number from audio file name
        slide_number_arr.append(slide_number + 1)
        prs.slides[slide_number].shapes.add_movie(audio_path, # add audio file to slide
                                                    left,top,width,height,
                                                    poster_frame_image=picture_path,
                                                    mime_type='video/unknown')

    narrated_path = os.path.join(temp_dir, 'narrated.pptx')  # Use temporary directory to store the narrated file
    print((f'Final narrated path saved as: {narrated_path}'))
    prs.save(narrated_path)  # save file to path
    apply_changes_to_slide(narrated_path, slide_number_arr)
    return narrated_path



def apply_changes_to_slide(pptx_path, slide_number_arr):

    # Make temporary directory for editing PPTX xml files
    temp_dir = session.get('temp_dir')
    temp_extract_dir = os.path.join(temp_dir, 'extracted_files')
    os.makedirs(temp_extract_dir, exist_ok=True)

    # Extract all files from the original PowerPoint to the temporary folder
    with ZipFile(pptx_path, 'r') as pptx_zip:
        pptx_zip.extractall(temp_extract_dir)

    # Iterate over only the slides that have had audio added
    for slide_number in slide_number_arr:
        slide_filename = fr"ppt/slides/slide{slide_number}.xml"
        slide_file_path = os.path.join(temp_extract_dir, slide_filename)

        with open(slide_file_path, 'r', encoding='utf-8') as file:
            xml_data = file.read()

        # Register all namespaces found in the XML data
        register_all_namespaces(xml_data)

        # Replace this specific piece of text
        xml_data = re.sub('<p:cNvPr id="4"', '<p:cNvPr id="6"', xml_data)

        # Replace the <p:video></p:video> text with new_text xml
        root = ET.fromstring(xml_data)
        parent = root.find('.//p:video/..', {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'})

        new_text = '''
        <p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst><p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="11859" fill="hold"/><p:tgtEl><p:spTgt spid="6"/></p:tgtEl></p:cBhvr></p:cmd></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst><p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq><p:audio><p:cMediaNode vol="80000"><p:cTn id="7" fill="hold" display="0"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:endCondLst><p:cond evt="onStopAudio" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:endCondLst></p:cTn><p:tgtEl><p:spTgt spid="6"/></p:tgtEl></p:cMediaNode></p:audio>'''  # Replace with the given new text

        if parent is not None:
            for elem in parent.findall("p:video", {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}):
                parent.remove(elem)
            new_elements = ET.fromstring("<root xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\">" + new_text + "</root>")
            for elem in new_elements:
                parent.append(elem)
        else:
            print("Video element not found.")

        modified_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + ET.tostring(root, encoding="utf-8", method="xml").decode()

        with open(slide_file_path, 'w', encoding='utf-8') as f:
            f.write(modified_xml)



    # Create a new PowerPoint file with the updated contents
    with ZipFile(pptx_path, 'w') as pptx_zip_modified:
        for root, _, files in os.walk(temp_extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_extract_dir)
                pptx_zip_modified.write(file_path, arcname)

    # Clean up the temporary folders
    shutil.rmtree(temp_extract_dir)

    
def register_all_namespaces(xml_data):
    namespaces = dict([
        node for _, node in ET.iterparse(io.StringIO(xml_data), events=['start-ns'])
    ])
    
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)

  
if __name__ == '__main__':
    app.run(debug = True)