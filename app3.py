from flask import Flask, render_template, request, redirect, url_for
import os
from PIL import Image
import easyocr
import numpy as np
import matplotlib.pyplot as plt


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def extract_text(image_path):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    return result


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            extracted_text = extract_text(file_path)
            return render_template('index2.html', filename=filename, extracted_text=extracted_text)
    return render_template('index2.html')


@app.route('/extract_specific_text', methods=['POST'])
def extract_specific_text():
    data = request.get_json()
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], data['filename'])
    image = Image.open(image_path)
    regions = data['regions']
    selected_text = []
    for region in regions:
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        cropped_image = image.crop((x, y, x + w, y + h))
        cropped_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_cropped.jpg')
        cropped_image.save(cropped_image_path)
        text = extract_text(cropped_image_path)
        selected_text.append({'label': region['label'], 'value': text[0][1]})
    return {'selected_text': selected_text}


if __name__ == '__main__':
    app.run(debug=True)
