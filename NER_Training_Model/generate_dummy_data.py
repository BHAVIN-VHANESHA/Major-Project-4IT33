import csv
import os
import random
from faker import Faker

# Initialize Faker for generating dummy data
fake = Faker()

# Define the file path where the data will be stored
DATA_FILE = '/home/bhavin/PycharmProjects/Major-Project-4IT33/ner_data.csv'

# Check if the file exists, if not, create it
if os.path.isfile(DATA_FILE) and os.path.getsize(DATA_FILE) == 0:
    # File exists but is empty, write column names
    with open(DATA_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['LABELS', 'VALUES'])
elif not os.path.isfile(DATA_FILE):
    # File doesn't exist, create it and write column names
    with open(DATA_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['LABELS', 'VALUES'])


# Function to generate dummy invoice data and append it to the CSV file
def generate_dummy_invoice_data(file_path, num_invoices):
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for _ in range(num_invoices):
            invoice_number = fake.random_number(digits=6)
            buyer_name = fake.name()
            buyer_address = fake.address()
            pin = fake.zipcode()
            date_issued = fake.date()
            product = fake.words()
            quantity = random.randint(1, 100)
            price = fake.random_number(digits=2)
            subtotal = quantity * price
            grand_total = subtotal + fake.random_number(digits=2)
            bank_name = fake.company()
            account_no = fake.random_number(digits=9)
            date_due = fake.date()
            shop_name = fake.company()
            buyer_email = fake.email()
            amount = fake.random_number(digits=2)

            writer.writerow(['INVOICE NO:', invoice_number])
            writer.writerow(['BILL TO', buyer_name])
            writer.writerow(['DATE ISSUED:', date_issued])
            writer.writerow(['PRODUCT NAME', product])
            writer.writerow(['QTY', quantity])
            writer.writerow(['PRICE', f'$ {price}'])
            writer.writerow(['GRAND TOTAL', f'$ {grand_total}'])
            writer.writerow(['DATE DUE', date_due])


# Generate dummy invoice data points
generate_dummy_invoice_data(DATA_FILE, 500)
