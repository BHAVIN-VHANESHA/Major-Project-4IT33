import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import cv2
import pandas as pd
import numpy as np
import easyocr

app = Flask(__name__)
app.secret_key = "super secret key"  # Set a secret key for session management

directory = '/home/bhavin/PycharmProjects/Major-Project-4IT33/static/uploads'
if not os.path.exists(directory):
    os.makedirs(directory)
    print("Directory created successfully")
else:
    pass
    # print("Directory already exists")

UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Flask route to show landing page
@app.route('/')
def home():
    return render_template('index.html')


# Flask route to upload image
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash("No selected file")
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('static', app.config['UPLOAD_FOLDER'], filename))
        flash('Image uploaded successfully')
        return redirect(url_for('display', filename=filename))
    else:
        flash('Upload file of supported image format')
        return redirect(request.url)


# Flask route to extract and display annotated image
@app.route('/display/<filename>', methods=['GET', 'POST'])
def display(filename):
    filepath = os.path.join('static', app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('File not found')
        return redirect(url_for('home'))

    image = cv2.imread(filepath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Perform OCR on the image
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(gray)

    # Highlighting the text
    for detection in result:
        top_left = tuple(map(int, detection[0][0]))
        bottom_right = tuple(map(int, detection[0][2]))
        text = detection[1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 1
        color = (255, 0, 0)  # BGR color format
        cv2.rectangle(image, top_left, bottom_right, color, font_thickness)
        # cv2.putText(image, text, top_left, font, font_scale, color, font_thickness)

    # Save the annotated image
    annotated_filename = 'annotated_' + filename
    cv2.imwrite(os.path.join('static', app.config['UPLOAD_FOLDER'], annotated_filename), image)

    # Provide the path to the annotated image in the response
    return render_template('display.html', original=filename, annotated=annotated_filename,
                           extracted_texts=[detection[1] for detection in result])


# Flask route to handle label and value submission
@app.route('/submit_label_value', methods=['POST'])
def submit_label_value():
    labels = request.form.getlist('label')
    values = request.form.getlist('value')
    print(labels)
    print(values)

    df = pd.DataFrame(data=values, columns=labels)
    print(df)
    return df


if __name__ == '__main__':
    app.run(debug=True)
