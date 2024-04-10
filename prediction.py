import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold
from datetime import datetime

# Step 1: Load the CSV data into a pandas DataFrame
df = pd.read_csv('generated_data.csv')

# Step 2: Data Preprocessing
# Convert 'Bill_Date' to datetime
df['Bill_Date'] = pd.to_datetime(df['Bill_Date'], format='%d-%m-%Y')

# Step 3: Label Encoding for Buyer_Name
label_encoder = LabelEncoder()
df['Buyer_Name_Encoded'] = label_encoder.fit_transform(df['Buyer_Name'])

# Extract month and year from 'Bill_Date'
df['Month'] = df['Bill_Date'].dt.month
df['Year'] = df['Bill_Date'].dt.year

# Step 4: Train models for each product
qty_models = {}
name_model = RandomForestClassifier()
buyer_model = RandomForestClassifier()  # Assuming you have a model for buyer name prediction as well

for product_name, data in df.groupby('Product_Name'):
    # Model for quantity prediction
    X_qty = data[['Year', 'Month', 'Buyer_Name_Encoded']]
    y_qty = data['Qty']
    qty_model = RandomForestRegressor()
    qty_model.fit(X_qty, y_qty)
    qty_models[product_name] = qty_model

    # Model for product name prediction
    X_name = data[['Year', 'Month', 'Buyer_Name_Encoded']]
    y_name = data['Product_Name']
    name_model.fit(X_name, y_name)

    # Model for buyer name prediction
    X_buyer = data[['Year', 'Month']]
    y_buyer = data['Buyer_Name_Encoded']
    buyer_model.fit(X_buyer, y_buyer)

# Step 5: Prediction for each product
current_month = datetime.now().month
current_year = datetime.now().year
predictions = {}

for product_name, qty_model in qty_models.items():
    # Predict quantity for each product
    encoded_buyer = label_encoder.transform(['Thompson Ltd'])  # Encode 'Buyer_X'
    next_month_qty = qty_model.predict([[current_year, current_month + 1, encoded_buyer[0]]])

    # Predict product name for each product
    next_month_name = name_model.predict([[current_year, current_month + 1, encoded_buyer[0]]])

    # Predict buyer name for each product
    next_month_buyer = label_encoder.inverse_transform(buyer_model.predict([[current_year, current_month + 1]]))

    # Decode the encoded buyer back to the original buyer name
    decoded_buyer = label_encoder.inverse_transform(encoded_buyer)[0]

    predictions[product_name] = {'Qty': next_month_qty[0], 'Product_Name': next_month_name[0],
                                 'Buyer_Name': next_month_buyer[0]}

# Step 6: Display predictions along with buyer names
print("Predictions for each product:")
for product_name, prediction in predictions.items():
    print(f"Product Name: {product_name}\nPredicted Quantity: {prediction['Qty']}\nPredicted Product Name: {prediction['Product_Name']}\nPredicted Buyer Name: {prediction['Buyer_Name']}\n")

# Step 7: Evaluate models using cross-validation
# For quantity prediction
mse_scores = []
for product_name, qty_model in qty_models.items():
    X_qty = df[df['Product_Name'] == product_name][['Year', 'Month', 'Buyer_Name_Encoded']]
    y_qty = df[df['Product_Name'] == product_name]['Qty']
    if len(X_qty) >= 5:  # Check if there are enough samples for cross-validation
        try:
            kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            mse_score = -cross_val_score(qty_model, X_qty, y_qty, cv=kf, scoring='neg_mean_squared_error').mean()
        except ValueError:  # Fall back to regular KFold if StratifiedKFold fails
            kf = KFold(n_splits=5, shuffle=True, random_state=42)
            mse_score = -cross_val_score(qty_model, X_qty, y_qty, cv=kf, scoring='neg_mean_squared_error').mean()
        mse_scores.append(mse_score)
    else:
        print(f"Not enough samples for cross-validation for product: {product_name}")

if len(mse_scores) > 0:
    mse_qty_mean = sum(mse_scores) / len(mse_scores)
else:
    mse_qty_mean = None

# For product name prediction
if len(df) >= 5:  # Check if there are enough samples for cross-validation
    try:
        kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        name_scores = cross_val_score(name_model, df[['Year', 'Month', 'Buyer_Name_Encoded']], df['Product_Name'], cv=kf, scoring='accuracy')
        name_accuracy_mean = name_scores.mean()
    except ValueError:  # Fall back to regular KFold if StratifiedKFold fails
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        name_scores = cross_val_score(name_model, df[['Year', 'Month', 'Buyer_Name_Encoded']], df['Product_Name'], cv=kf, scoring='accuracy')
        name_accuracy_mean = name_scores.mean()
else:
    print("Not enough samples for cross-validation for product name prediction")
    name_accuracy_mean = None

# For buyer name prediction
if len(df) >= 5:  # Check if there are enough samples for cross-validation
    try:
        kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        buyer_scores = cross_val_score(buyer_model, df[['Year', 'Month']], df['Buyer_Name_Encoded'], cv=kf, scoring='accuracy')
        buyer_accuracy_mean = buyer_scores.mean()
    except ValueError:  # Fall back to regular KFold if StratifiedKFold fails
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        buyer_scores = cross_val_score(buyer_model, df[['Year', 'Month']], df['Buyer_Name_Encoded'], cv=kf, scoring='accuracy')
        buyer_accuracy_mean = buyer_scores.mean()
else:
    print("Not enough samples for cross-validation for buyer name prediction")
    buyer_accuracy_mean = None

print("Mean Squared Error for quantity prediction:", mse_qty_mean)
print("Accuracy for product name prediction:", name_accuracy_mean)
print("Accuracy for buyer name prediction:", buyer_accuracy_mean)
