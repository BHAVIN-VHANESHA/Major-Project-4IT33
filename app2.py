from flask import Flask, render_template, request, send_file
import cv2
import easyocr
import os
import csv
import numpy as np
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Directory to save selected text images
SAVE_DIR = 'selected_texts'
# Ensure the directory exists
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


# Home route
@app.route('/')
def home():
    return render_template('index.html')


# OCR route
@app.route('/upload', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    image = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Perform OCR on the image
    result = reader.readtext(image)

    # Save selected text images and create OCR result CSV
    # selected_texts = []
    # for i, (bbox, text, score) in enumerate(result):
    #     selected_text_image_path = os.path.join(SAVE_DIR, f'selected_text_{i}.png')
    #     cv2.imwrite(selected_text_image_path,
    #                 cv2.cvtColor(image[bbox[0][1]:bbox[2][1], bbox[0][0]:bbox[2][0]], cv2.COLOR_RGB2BGR))
    #     selected_texts.append({'Text': text, 'Score': score, 'Image_Path': selected_text_image_path})

    # Write OCR result to CSV
    csv_filename = 'ocr_result.csv'
    csv_path = os.path.join(SAVE_DIR, csv_filename)
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Text', 'Score', 'Image_Path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    return render_template('result.html', result=result, csv_filename=csv_filename)


# Download route for PDF
@app.route('/download/pdf')
def download_pdf():
    return send_file('ocr_result.pdf', as_attachment=True)


# Download route for CSV
@app.route('/download/csv')
def download_csv():
    return send_file(os.path.join(SAVE_DIR, 'ocr_result.csv'), as_attachment=True)


# Download route for Excel
@app.route('/download/excel')
def download_excel():
    df = pd.read_csv(os.path.join(SAVE_DIR, 'ocr_result.csv'))
    excel_io = BytesIO()
    excel_writer = pd.ExcelWriter(excel_io, engine='xlsxwriter')
    df.to_excel(excel_writer, index=False)
    excel_writer.save()
    excel_io.seek(0)
    return send_file(excel_io, attachment_filename='ocr_result.xlsx', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
