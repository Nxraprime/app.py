from flask import Flask, render_template_string, request, send_file
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# Key for encryption and decryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Directory to save files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# HTML, CSS, and JavaScript for black-themed site
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure File Sharing App</title>
    <style>
        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        header, footer {
            background-color: #1e1e1e;
            color: #ffffff;
            padding: 20px;
            text-align: center;
        }
        footer h3 {
            font-weight: normal;
            font-size: 1.2em;
        }
        main {
            padding: 20px;
            text-align: center;
        }
        h1 {
            color: #ffffff;
        }
        input[type="file"], input[type="submit"] {
            padding: 10px;
            margin: 10px;
            background-color: #333;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        ul li a {
            color: #00aaff;
            text-decoration: none;
        }
        ul li a:hover {
            color: #ff6347;
        }
    </style>
</head>
<body>
    <header>
        <h1>Secure File Sharing</h1>
        <h2>Developed by Amal Raju</h2>
    </header>
    <main>
        <h2>Upload a File</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="submit" value="Upload">
        </form>
        
        <h2>Download Files</h2>
        {% if files %}
            <ul>
                {% for file in files %}
                    <li><a href="/download/{{ file }}">{{ file }}</a></li>
                {% endfor %}
            </ul>
        {% else %}
            <p>No files available</p>
        {% endif %}
    </main>
    <footer>
        <h3>Developed by Amal Raju</h3>
    </footer>
</body>
</html>
"""

# Route for homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Upload file
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Encrypt file
            file_data = file.read()
            encrypted_data = cipher_suite.encrypt(file_data)
            
            # Save encrypted file
            with open(filepath, 'wb') as f:
                f.write(encrypted_data)

    # List files available for download
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string(html_template, files=files)

# Route to download file
@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Decrypt file
    with open(filepath, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = cipher_suite.decrypt(encrypted_data)

    # Save decrypted file temporarily for download
    temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"decrypted_{filename}")
    with open(temp_filepath, 'wb') as f:
        f.write(decrypted_data)
    
    return send_file(temp_filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(host='172.20.10.7', port=5000, debug=True)

