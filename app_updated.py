import os
from flask import Flask, render_template, request, session
import re
import PyPDF2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as se

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def clean_text(text):
    cleaned_text = re.sub(r'\s+', ' ', text.strip())
    return cleaned_text


def save_text_to_file(text):
    with open("raw_data.txt", "a") as f:
        f.write(text)
        f.write('\n\n')


def process_invoice(cleaned_text):
    # Finding Patterns
    bill_no_pattern = r"BILL NO : (\d+)"
    bill_match = re.search(bill_no_pattern, cleaned_text)
    bill_no = bill_match.group(1) if bill_match else None
    # print(bill_no)

    date_pattern = r"DATE : (\d{2}-\d{2}-\d{4})"
    date_match = re.search(date_pattern, cleaned_text)
    date = date_match.group(1) if date_match else None
    # print(date)

    party_name_pattern = r"PARTY'S NAME :- (\w+ \w+)"
    party_match = re.search(party_name_pattern, cleaned_text)
    party_name = party_match.group(1).strip() if party_match else None
    # print(party_name)

    gst_pattern = r"GST :- ([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{1}Z[0-9A-Z]{1})"
    gst_match = re.search(gst_pattern, cleaned_text)
    gst = gst_match.group(1).strip() if gst_match else None
    # print(gst)

    gstin_pattern = r"GSTIN :- ([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{1}Z[0-9A-Z]{1})"
    gstin_match = re.search(gstin_pattern, cleaned_text)
    gstin = gstin_match.group(1).strip() if gst_match else None
    # print(gstin)

    cgst_pattern = r"CGST @ \d+% (\d+)"
    cgst_match = re.search(cgst_pattern, cleaned_text)
    cgst = cgst_match.group(1) if cgst_match else None
    # print(cgst)

    sgst_pattern = r"SGST @ \d+% (\d+)"
    sgst_match = re.search(sgst_pattern, cleaned_text)
    sgst = sgst_match.group(1) if sgst_match else None
    # print(sgst)

    grand_total_pattern = r"Grand Total (\d+,\d+\.\d+)"
    grand_total_match = re.search(grand_total_pattern, cleaned_text)
    grand_total = grand_total_match.group(1) if grand_total_match else None
    # print(grand_total)

    product_pattern = r"\. (.+?) (\d+) (\d+) (\d+) (\d+)"
    product_match = re.findall(product_pattern, cleaned_text)
    product_description = product_match if product_match else None
    # print(product_description)

    # To display df without truncation
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    user_df = pd.DataFrame(product_description, columns=["Product_Name", "HSN_Code", "Qty", "Rate", "Amount"])
    user_df["Bill_No"] = int(bill_no)
    user_df["Bill_Date"] = date
    user_df["Buyer_Name"] = party_name
    user_df["Qty"] = user_df["Qty"].astype(int)
    user_df["Rate"] = user_df["Rate"].astype(int)
    user_df["Amount"] = user_df["Amount"].astype(int)
    temp_product_df = user_df.copy()
    # print(product_df)

    product_name = ", ".join([item[0] for item in product_description])
    hsn_code = ", ".join([item[1] for item in product_description])
    qty = ", ".join([item[2] for item in product_description])
    rate = ", ".join([item[3] for item in product_description])
    amount = ", ".join([item[4] for item in product_description])

    data = {
        "Bill_No": [bill_no],
        "Bill_Date": [date],
        "Seller_GST_No": [gstin],
        "Buyer_Name": [party_name],
        "Buyer_GST_No": [gst],
        "Product_Name": [product_name],
        "HSN_Code": [hsn_code],
        "Qty": [qty],
        "Rate": [rate],
        "Amount": [amount],
        "CGST(9%)": [cgst],
        "SGST(9%)": [sgst],
        "Grand_Total": [grand_total]
    }
    temp_raw_df = pd.DataFrame(data)
    # print(temp_raw_df)
    return temp_product_df, temp_raw_df


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index_updated.html')


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("index_updated.html", message="No file part")
        files = request.files.getlist("file")
        for file in files:
            if file.filename == "":
                return render_template("index_updated.html", message="No selected file")
            if file:
                text = extract_text_from_pdf(file)
                cleaned_text = clean_text(text)
                save_text_to_file(cleaned_text)
                temp_product_df, temp_raw_df = process_invoice(cleaned_text)

                if not temp_product_df.empty and not temp_raw_df.empty:
                    # Save product DataFrame to CSV
                    if not os.path.isfile("product_data.csv") or os.stat("product_data.csv").st_size == 0:
                        temp_product_df.to_csv("product_data.csv", index=False)  # Write DataFrame with headers
                    else:
                        temp_product_df.to_csv("product_data.csv", mode='a', header=False, index=False)
                    # Save summary DataFrame to CSV
                    if not os.path.isfile("summary_data.csv") or os.stat("summary_data.csv").st_size == 0:
                        temp_raw_df.to_csv("summary_data.csv", index=False)  # Write DataFrame with headers
                    else:
                        temp_raw_df.to_csv("summary_data.csv", mode='a', header=False, index=False)
                    message = f"File '{file.filename}' uploaded successfully"
                    return render_template("dashboard.html")
                else:
                    message = f"Failed to extract data from the invoice '{file.filename}'"
                    return render_template("index_updated.html", message=message)


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    # Read CSV file into DataFrame
    df = pd.read_csv("product_data.csv")

    # Perform data analysis and create plots
    # Example plots
    plt.figure(figsize=(10, 6))
    se.histplot(df['Qty'], bins=20, kde=True)
    plt.title('Quantity Distribution')
    plt.xlabel('Quantity')
    plt.ylabel('Frequency')
    plt.tight_layout()

    # Pass the plots as images to the HTML template
    return render_template('dashboard.html', hist_plot=hist_plot)


if __name__ == "__main__":
    app.run(debug=True)
