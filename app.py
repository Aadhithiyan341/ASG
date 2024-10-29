from flask import Flask, render_template, request, redirect, send_file, flash
from werkzeug.utils import secure_filename
from helpers.audio_processing import extract_audio, generate_subtitles, write_srt_file
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For flashing messages

# Set upload and subtitle directories
UPLOAD_FOLDER = 'uploads/'
SUBTITLE_FOLDER = 'subtitles/'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SUBTITLE_FOLDER'] = SUBTITLE_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SUBTITLE_FOLDER, exist_ok=True)

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part in the request')
        return redirect('/')
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect('/')
    
    if file and allowed_file(file.filename):
        # Secure the file name to avoid issues
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract audio and generate subtitles
        audio_path = extract_audio(file_path)
        subtitle_text = generate_subtitles(audio_path)
        
        # Write subtitle text to .srt file
        srt_path = write_srt_file(subtitle_text, filename)

        # Serve the generated subtitle file for download
        return send_file(srt_path, as_attachment=True)

    else:
        flash('Invalid file format. Please upload a valid video file (mp4, avi, mov, mkv).')
        return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
