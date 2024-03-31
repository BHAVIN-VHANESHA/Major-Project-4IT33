import re
import pandas as pd
import PyPDF2


def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
            text.encode("utf-8")
    return text


pdf_path = "/home/bhavin/Pictures/Invoices Dataset/shiv1.pdf"
extracted_text = extract_text_from_pdf(pdf_path)


# print(extracted_text)


def clean_text(text):
    cleaned_text = re.sub(r'\s+', ' ', text.strip())
    return cleaned_text


text = extracted_text

# Clean the text
cleaned_text = clean_text(text)
# print(cleaned_text)

with open('raw_data.txt', 'a') as f:
    f.write(cleaned_text)
    f.write('\n\n')

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

description = ", ".join([item[1] for item in product_description])

# Creating a DataFrame for non-repeated data
non_repeated_data = {
    "Bill No": [bill_no],
    "Date": [date],
    "Party Name": [party_name],
    "GSTIN": [gstin],
    "CGST": [cgst],
    "SGST": [sgst],
    "Grand Total": [grand_total],
    "Description": [description]  # Add the combined description
}
non_repeated_df = pd.DataFrame(non_repeated_data)

# Save the data to CSV
non_repeated_df.to_csv(f"bill_{bill_no}.csv", index=False)

# Displaying the DataFrame
print(non_repeated_df)
