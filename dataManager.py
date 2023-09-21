import langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings

from langchain.vectorstores import FAISS
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import shutil
from flask import url_for, stream_with_context, Response
import time
import json
from datetime import datetime


DATA_PATH = '/home/azureuser/Llama2-hf/data'
DB_FAISS_PATH = "vectorstores/db_faiss/"
EMBEDDINGS_DIR = "vectorstores/"

app = Flask(__name__)
app.debug = True

app.config['UPLOAD_FOLDER'] = '/home/azureuser/Llama2-hf/data'
app.config['DATA_PATH'] = '/home/azureuser/Llama2-hf/data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max-limit
app.secret_key = 'supersecretkey'

DELETE_KEY = 'key'
KEY = 'key'
PROCESS_KEY = 'key'
DELETE_DIRECTORY_KEY = 'key'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize a global variable to hold the progress state
global_progress_state = {
    "status": "idle",  # Can be "idle", "in_progress", or "completed"
    "progress": 0  # A percentage representing the progress of the task (0-100)
}

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)


from flask import jsonify
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global global_progress_state

    if request.method == 'POST':
        key = request.form.get('upload_key')  
        if not key or key != KEY:
            flash('Invalid UPLOAD key')
            return redirect(request.url)
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        files = request.files.getlist('file')
        
        if not files or all(file.filename == '' for file in files):
            flash('No selected file')
            return redirect(request.url)
        global_progress_state = {"status": "in_progress", "progress": 0}
 
        filecount = 0
        file_errors = []
        for file in files:
            filecount += 1
            global_progress_state['progress'] = 20 + filecount
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                save_file_info([file.filename])  # Save file info after uploading
            else:
                file_errors.append(file.filename)
        
        global_progress_state['progress'] = 20 + filecount + 10
        
        if file_errors:
            flash('Error with files: ' + ', '.join(file_errors))
            flash('Allowed file type is PDF')
            return redirect(request.url)
        flash("Upload Complete.", "success")
        global_progress_state = {"status": "completed", "progress": 100}
        return redirect(url_for('index'))
    else:
        flash("Upload FAILED.", "error")
        global_progress_state = {"status": "idle", "progress": 0}
        return render_template('index.html')

@app.route('/progress')
def progress():
    global global_progress_state
    def generate():
        while True:
            yield f"data: {json.dumps(global_progress_state)}\n\n"
            time.sleep(1)  # You might want to adjust the sleep time based on your needs

    return Response(generate(), content_type='text/event-stream')


@app.route('/process', methods=['POST'])
def process_directory():
    print("In Embeddings Process.")
    flash('In Process Directory...', 'success')
    global global_progress_state
    flash('Beginning Embedding Process...', 'success')

    key = request.form.get('process_key')  # Note the change here
    if not key or key != KEY:
        flash('Invalid PROCESS key for processing the directory/files')
        return redirect(request.url)
    try:
        flash('Loading Data...', 'success')
        # Update the global progress state to indicate that the task has started
        global_progress_state = {"status": "in_progress", "progress": 0}
   
        loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        
        global_progress_state['progress'] = 20
        flash('Data Loaded...', 'success')
        
        # Extracting the file names from the documents list
        processed_files = [doc.metadata.get('name') for doc in documents if doc.metadata.get('name') is not None]

        if not documents:
            flash('No files in the Data Directory to process', 'error')
            return redirect(url_for('index'))
        global_progress_state['progress'] = 40        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        
        texts = text_splitter.split_documents(documents)
        valid_documents = [doc for doc in texts if isinstance(doc, langchain.schema.document.Document)]
        
        for i, doc in enumerate(texts):
            print(f"Index {i}: {type(doc)}")
            if isinstance(doc, str):
                print(f"String content at index {i}: {doc}")

        
        # Debug texts
        flash('Text Splitting Complete...', 'success')

        if not texts:
            flash('No texts to process', 'error')
            return redirect(url_for('index'))

        flash('Embeddings begun...', 'success')
        # Original - fully functional
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})

        flash('Embeddings complete...', 'success')
        global_progress_state['progress'] = 60

        db = FAISS.from_documents(texts, embeddings)
        db.save_local(DB_FAISS_PATH)

        flash('Storage complete...', 'success')
        global_progress_state['progress'] = 80

        save_file_info(processed_files)  # Save file info after processing
        
        print("Data Processing Complete.")
        
        flash("Directory Embeddings Processing Complete.", "success")
        global_progress_state = {"status": "completed", "progress": 100}
        return redirect(url_for('index'))
    except Exception as e:
            print(f"An error occurred: {e}")
            flash("Directory Embeddings Processing FAILED.", "error")
            global_progress_state = {"status": "idle", "progress": 0}
            return jsonify(success=False, message=f"An error occurred: {e}"), 500


@app.route('/delete_files', methods=['POST'])  # Update as necessary to match your HTML
def delete_files():  # Update function name to match route
    global global_progress_state
    flash("Beginning removal of files.", "success")
    key = request.form.get('delete_key')
    filenames = request.form.getlist('filenames[]')  # ensure that filenames[] is used to get a list

    if not key or key != DELETE_KEY:
        return jsonify(success=False, message='Invalid DELETE key'), 400

    if not filenames:
        return jsonify(success=False, message='Filename is required'), 400

    for filename in filenames:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'File "{filename}" successfully deleted', 'success')
        else:
            flash(f'File "{filename}" not found', 'error')

    return redirect(url_for('index'))

@app.route('/delete_directory', methods=['POST'])
def delete_directory():
    global global_progress_state
    flash('Embedding Reset Begun...', 'success')
    key = request.form.get('delete_directory_key')
    if not key or key != DELETE_DIRECTORY_KEY:
        flash('Invalid DELETE EMBEDDINGS key', 'error')
        return redirect(url_for('index'))
    
    try:
        shutil.rmtree(EMBEDDINGS_DIR, ignore_errors=True)
        flash('Embeddings successfully DESTROYED', 'success')
        
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred while destroying the Embeddings: {e}', 'error')
    
    return redirect(url_for('index'))

@app.route('/get_file_info', methods=['GET'])
def get_file_info():
    try:
        with open('chat-data-files-info.json', 'r') as f:
            data = json.load(f)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify({"files": []})

def save_file_info(file_names):
    data = {"files": []}
    try:
        with open('chat-data-files-info.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        pass

    for file_name in file_names:
        data["files"].append({"name": file_name, "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    
    with open('chat-data-files-info.json', 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)