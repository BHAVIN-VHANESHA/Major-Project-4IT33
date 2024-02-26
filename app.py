from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw
import pytesseract
import pandas as pd
import cv2


app = Flask(__name__)


# Function to extract text from image and draw bounding boxes
def extract_text_and_draw_boxes(image_path):
    image = Image.open(image_path)
    text_boxes = pytesseract.image_to_boxes(image)

    # Draw bounding boxes on the image
    draw = ImageDraw.Draw(image)
    for box in text_boxes.splitlines():
        box_data = box.split(' ')
        draw.rectangle([int(box_data[1]), image.height - int(box_data[4]),
                        int(box_data[3]), image.height - int(box_data[2])],
                       outline="red", width=2)

    # Save the image with bounding boxes
    output_image_path = 'output_with_boxes.jpg'
    image.save(output_image_path)

    # Extract text from the image
    extracted_text = pytesseract.image_to_string(image)

    return extracted_text, output_image_path


# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    try:
        # Save the uploaded file
        file.save(file.filename)
        # Extract text from the uploaded image and draw bounding boxes
        extracted_text, output_image_path = extract_text_and_draw_boxes(file.filename)

        return jsonify({'success': 'Text extracted and bounding boxes drawn.',
                        'text': extracted_text, 'image_with_boxes': output_image_path})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'})


@app.route('/download/csv', methods=['GET'])
def download_csv():
    df = pd.DataFrame([extracted_text.split('\n')], columns=['Extracted Text'])
    df.to_csv('extracted_text.csv', index=False)
    return send_file('extracted_text.csv', as_attachment=True)


@app.route('/download/excel', methods=['GET'])
def download_excel():
    df = pd.DataFrame([extracted_text.split('\n')], columns=['Extracted Text'])
    df.to_excel('extracted_text.xlsx', index=False)
    return send_file('extracted_text.xlsx', as_attachment=True)


@app.route('/download/pdf', methods=['GET'])
def download_pdf():
    df = pd.DataFrame([extracted_text.split('\n')], columns=['Extracted Text'])
    df.to_html('extracted_text.html', index=False)
    # Convert HTML to PDF
    pdfkit.from_file('extracted_text.html', 'extracted_text.pdf')
    return send_file('extracted_text.pdf', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
