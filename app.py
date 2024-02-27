from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import urllib.request
import os
import cv2
from PIL import Image
import easyocr
import numpy as np
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt


app = Flask(__name__)
app.secret_key = 'learn@flask'
# ''' Directory to save images
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure the directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# '''

''' Directory to save selected text images
SAVE_DIR = 'selected_texts'
# Ensure the directory exists
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)
# '''


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash("No selected file")
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Image loaded')
        return render_template('index.html', filename=filename)
    else:
        flash('upload file of image format')
        return redirect(request.url)


@app.route('/display/<filename>')
def display(filename):
    return redirect(url_for('static', filename='uploads' + filename), code=301)

    # image = cv2.imdecode(np.frombuffer(file.read(), dtype=np.uint8), cv2.IMREAD_COLOR)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #
    # # Perform OCR on the image
    # reader = easyocr.Reader(['en'], gpu=False)
    # result = reader.readtext(image)

    ''' Highlighting the text
    for detection in result:
        top_left = tuple(map(int, detection[0][0]))  # Ensure coordinates are integers
        bottom_right = tuple(map(int, detection[0][2]))  # Ensure coordinates are integers
        text = detection[1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        color = (255, 0, 0)  # BGR color format
        cv2.rectangle(image, top_left, bottom_right, color, font_thickness)
        cv2.putText(image, text, top_left, font, font_scale, color, font_thickness)
    print(result)  # '''

    ''' Get the original image size
    height, width = image.shape[:2]
    # Create a window with the original image size
    cv2.namedWindow("Original Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Original Image", width, height)
    # Display the original image
    cv2.imshow("Original Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()  # '''


''' Download route for PDF
@app.route('/download/pdf')
def download_pdf():
    return send_file('ocr_result.pdf', as_attachment=True)
# '''


''' Download route for CSV
@app.route('/download/csv')
def download_csv():
    return send_file(os.path.join(SAVE_DIR, 'ocr_result.csv'), as_attachment=True)
# '''


''' Download route for Excel
@app.route('/download/excel')
def download_excel():
    df = pd.read_csv(os.path.join(SAVE_DIR, 'ocr_result.csv'))
    excel_io = BytesIO()
    excel_writer = pd.ExcelWriter(excel_io, engine='xlsxwriter')
    df.to_excel(excel_writer, index=False)
    excel_writer.save()
    excel_io.seek(0)
    return send_file(excel_io, attachment_filename='ocr_result.xlsx', as_attachment=True)
# '''


if __name__ == '__main__':
    app.run(debug=True)
