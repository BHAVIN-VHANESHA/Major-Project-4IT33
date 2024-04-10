import pandas as pd
from faker import Faker
import random

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Initialize Faker to generate fake data
fake = Faker()

# Generate fake company names
company_names = [fake.company() for _ in range(100)]  # Adjust the number as needed


# Function to generate random bill numbers
def generate_bill_number():
    return random.randint(1, 10000)


# Function to generate random bill dates
def generate_bill_date():
    return fake.date_between(start_date='-2y', end_date='today').strftime('%d-%m-%Y')


# Generate fake data
data = []
for _ in range(1000):  # Adjust the number of rows you want to generate
    product_name = fake.random_element(elements=(
        'BROMEL FIX TYPE–1', 'BROMEL FIX TYPE–2', 'BROMEL FIX TYPE-3', 'BLOCK JOINING MOTAR', 'EPOXY REGULAR(1 KG)',
        'WHITE SBR(1 LTR)', 'WHITE SBR(5 LTR)', 'EPOXY REGULAR(5 KG)', 'SPARKAL SILVER', 'SPARKAL GOLDEN',
        'SPARKAL COPPER'))
    hsn_code = 382450
    qty = random.randint(1, 1000)
    rate = random.randint(50, 2000)
    amount = qty * rate
    bill_no = generate_bill_number()
    bill_date = generate_bill_date()
    buyer_name = random.choice(company_names)  # Randomly select company name

    data.append([product_name, hsn_code, qty, rate, amount, bill_no, bill_date, buyer_name])

# Create a DataFrame
df = pd.DataFrame(data,
                  columns=['Product_Name', 'HSN_Code', 'Qty', 'Rate', 'Amount', 'Bill_No', 'Bill_Date', 'Buyer_Name'])

# Save the generated data to a CSV file
df.to_csv('generated_data.csv', index=False)

# Display the first few rows of the generated data
print(df.head())
