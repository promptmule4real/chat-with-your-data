import langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from werkzeug.utils import secure_filename
import os
import shutil
from flask import url_for, stream_with_context, Response
import time
import json
import logging
from datetime import datetime
import subprocess
from flask import (
    abort,
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
    jsonify,
    Response,
    url_for,
    stream_with_context,
)
from werkzeug.utils import secure_filename
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.debug = True
login_manager = LoginManager(app)
login_manager.login_view = "login"

app.config["UPLOAD_FOLDER"] = "/home/azureuser/cs/data"
app.config["DATA_PATH"] = "/home/azureuser/cs/data"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max-limit
app.config["SECRET_KEY"] = "Abcd@1234!"  # Change this to a random secret key


class User:
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


users = [
    User(id=1, username="admin", password_hash=generate_password_hash("admin")),
    User(id=2, username="matt", password_hash=generate_password_hash("key")),
    User(id=3, username="alwyn", password_hash=generate_password_hash("password1")),
]

DATA_PATH = "/home/azureuser/cs/data"
DB_FAISS_PATH = "vectorstores/db_faiss/"
EMBEDDINGS_DIR = "vectorstores/"


DELETE_KEY = "key"
KEY = "key"
PROCESS_KEY = "key"
DELETE_DIRECTORY_KEY = "key"

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Initialize a global variable to hold the progress state
global_progress_state = {
    "status": "idle",  # Can be "idle", "in_progress", or "completed"
    "progress": 0,  # A percentage representing the progress of the task (0-100)
}

# app.config.from_object('config')  # Import configurations from a separate config file
global_progress_state = {"status": "idle", "progress": 0}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = next((user for user in users if user.username == username), None)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            session['_flashes'] = []  # Clear all flash messages
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    try:
        total_delay = 5  # total delay in seconds
        per_step_delay = total_delay / 5  # five steps in total, equally divided time for each step
        
        # Progress: Log out user
        logout_user()
        flash("User has been logged out.", "info")
        time.sleep(per_step_delay)
        
        # Progress: Starting removal of files
        flash("Beginning file destruction.", "info")
        time.sleep(per_step_delay)
        
        try:
            filenames = os.listdir(app.config["UPLOAD_FOLDER"])
            if not filenames:  # Check if the directory is empty
                flash("The folder is empty, no files to destroy", "info")
            else:
                for filename in filenames:
                    file_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(filename))
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        flash(f'File "{filename}" successfully destroyed', "info")
                    else:
                        flash(f'File "{filename}" not found', "error")
        except Exception as e:
            flash(f"An error occurred while destroying files: {e}", "error")
        
        time.sleep(per_step_delay)
        
        # Progress: Starting removal of directory
        flash("Beginning removal of directory.", "info")
        time.sleep(per_step_delay)
        
        try:
            if os.path.exists(EMBEDDINGS_DIR):
                shutil.rmtree(EMBEDDINGS_DIR, ignore_errors=True)
                flash("Unlearning complete successfully", "success")
            else:
                flash("No Unlearning to do.", "info")
        except Exception as e:
            flash(f"An error occurred while Unlearning: {e}", "error")
        
        time.sleep(per_step_delay)
        
    except Exception as e:
        flash(f"An error occurred during logout: {e}", "error")
    finally:
        return redirect(url_for("login"))



@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    return next((user for user in users if user.id == user_id), None)


@app.route("/")
@login_required
def index():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("index.html", files=files, current_user=current_user)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    global global_progress_state

    if request.method == "POST":
        key = request.form.get("upload_key")
        if not key or key != KEY:
            flash("Invalid UPLOAD key")
            return redirect(request.url)

        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        files = request.files.getlist("file")

        if not files or all(file.filename == "" for file in files):
            flash("No selected file")
            return redirect(request.url)
        global_progress_state = {"status": "in_progress", "progress": 0}

        filecount = 0
        file_errors = []
        for file in files:
            filecount += 1
            global_progress_state["progress"] = 20 + filecount
            if file and file.filename.endswith(".pdf"):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                save_file_info([file.filename])  # Save file info after uploading
            else:
                file_errors.append(file.filename)

        global_progress_state["progress"] = 20 + filecount + 10

        if file_errors:
            flash("Error with files: " + ", ".join(file_errors))
            flash("Allowed file type is PDF")
            return redirect(request.url)
        flash("Upload Complete.", "success")
        global_progress_state = {"status": "completed", "progress": 100}
        return redirect(url_for("index"))
    else:
        flash("Upload FAILED.", "error")
        global_progress_state = {"status": "idle", "progress": 0}
        return render_template("index.html")


@app.route("/progress")
@login_required
def progress():
    global global_progress_state

    def generate():
        while True:
            yield f"data: {json.dumps(global_progress_state)}\n\n"
            time.sleep(1)  # You might want to adjust the sleep time based on your needs

    return Response(generate(), content_type="text/event-stream")


@app.route("/process", methods=["POST"])
@login_required
def process_directory():
    print("In Embeddings Process.")
    flash("In Process Directory...", "success")
    global global_progress_state
    flash("Beginning Embedding Process...", "success")

    key = request.form.get("process_key")  # Note the change here
    if not key or key != KEY:
        flash("Invalid PROCESS key for processing the directory/files")
        return redirect(request.url)
    try:
        flash("Loading Data...", "success")
        # Update the global progress state to indicate that the task has started
        global_progress_state = {"status": "in_progress", "progress": 0}

        loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()

        global_progress_state["progress"] = 20
        flash("Data Loaded...", "success")

        # Extracting the file names from the documents list
        processed_files = [
            doc.metadata.get("name")
            for doc in documents
            if doc.metadata.get("name") is not None
        ]

        if not documents:
            flash("No files in the Data Directory to process", "error")
            return redirect(url_for("index"))
        global_progress_state["progress"] = 40
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        texts = text_splitter.split_documents(documents)
        valid_documents = [
            doc for doc in texts if isinstance(doc, langchain.schema.document.Document)
        ]

        for i, doc in enumerate(texts):
            print(f"Index {i}: {type(doc)}")
            if isinstance(doc, str):
                print(f"String content at index {i}: {doc}")
        # Debug texts
        flash("Text Splitting Complete...", "success")

        if not texts:
            flash("No texts to process", "error")
            return redirect(url_for("index"))

        flash("Embeddings begun...", "success")
        # Original - fully functional
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )

        flash("Embeddings complete...", "success")
        global_progress_state["progress"] = 60

        db = FAISS.from_documents(texts, embeddings)
        db.save_local(DB_FAISS_PATH)

        flash("Storage complete...", "success")
        global_progress_state["progress"] = 80

        save_file_info(processed_files)  # Save file info after processing

        print("Data Processing Complete.")

        flash("Directory Embeddings Processing Complete.", "success")
        global_progress_state = {"status": "completed", "progress": 100}
        return redirect(url_for("index"))
    except Exception as e:
        print(f"An error occurred: {e}")
        flash("Directory Embeddings Processing FAILED.", "error")
        global_progress_state = {"status": "idle", "progress": 0}
        return jsonify(success=False, message=f"An error occurred: {e}"), 500


@app.route("/delete_files", methods=["POST"])  # Update as necessary to match your HTML
@login_required
def delete_files():  # Update function name to match route
    global global_progress_state
    flash("Beginning removal of files.", "success")
    key = request.form.get("delete_key")
    filenames = request.form.getlist(
        "filenames[]"
    )  # ensure that filenames[] is used to get a list

    if not key or key != DELETE_KEY:
        return jsonify(success=False, message="Invalid DELETE key"), 400

    if not filenames:
        return jsonify(success=False, message="Filename is required"), 400

    for filename in filenames:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(filename))
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'File "{filename}" successfully deleted', "success")
        else:
            flash(f'File "{filename}" not found', "error")

    return redirect(url_for("index"))


@app.route("/delete_directory", methods=["POST"])
@login_required
def delete_directory():
    global global_progress_state
    flash("Embedding Reset Begun...", "success")
    key = request.form.get("delete_directory_key")
    if not key or key != DELETE_DIRECTORY_KEY:
        flash("Invalid UNLEARN key", "error")
        return redirect(url_for("index"))

    try:
        if os.path.exists(EMBEDDINGS_DIR):
            shutil.rmtree(EMBEDDINGS_DIR, ignore_errors=True)
            flash("UNLEARNing Complete Successfully", "success")
        else:
            flash("Nothing Previously Learned", "success")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"An error occurred while UNLEARNING: {e}", "error")

    return redirect(url_for("index"))


@app.route("/get_file_info", methods=["GET"])
@login_required
def get_file_info():
    try:
        with open("chat-data-files-info.json", "r") as f:
            data = json.load(f)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify({"files": []})


def save_file_info(file_names):
    data = {"files": []}
    try:
        with open("chat-data-files-info.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        pass

    for file_name in file_names:
        data["files"].append(
            {"name": file_name, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        )

    with open("chat-data-files-info.json", "w") as f:
        json.dump(data, f)

# Protected URL path (change to an actual secure path in production)
SECRET_PATH = '/secret-restart'
LOG_DIR_BASE = './ACTIVE_LOGS'

@app.route(SECRET_PATH, methods=['POST'])
def restart_chainlit():
    try:
        # It’s better to add an authentication check here
        if not request.is_authenticated:
            abort(401)

        chainlit_pid = subprocess.getoutput("pgrep -f 'chainlit run deploy.py -w'")
        data_manager_pid = subprocess.getoutput("pgrep -f 'python3 dataManager.py'")

        if chainlit_pid.isdigit():
            subprocess.run(['kill', '-9', chainlit_pid])
        else:
            logging.warning(f"No chainlit process found: {chainlit_pid}")

        if data_manager_pid.isdigit():
            subprocess.run(['kill', '-9', data_manager_pid])
        else:
            logging.warning(f"No dataManager process found: {data_manager_pid}")

        return jsonify(success=True, message="Processes have been restarted.")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
