import pandas as pd
import spacy
from sklearn_crfsuite import CRF
from sklearn.model_selection import train_test_split
from sklearn_crfsuite.metrics import flat_f1_score

# Step 1: Load Data from CSV
csv_file = r"/home/bhavin/PycharmProjects/Major-Project-4IT33/ner_data.csv"
data = pd.read_csv(csv_file)

# Step 2: Annotation (Assuming manual annotation)
annotations = []
for label, value in zip(data['label'], data['values']):
    annotations.append({label: value})

# Step 3: Feature Engineering
nlp = spacy.load('/home/bhavin/PycharmProjects/Major-Project-4IT33/NER_Training_Model')


def extract_features(text):
    doc = nlp(text)
    features = []
    for token in doc:
        features.append(token.vector)  # Word embeddings
    return features


invoice_features = [extract_features(text) for text in data['values']]

# Step 4: Model Selection
crf_model = CRF(algorithm='lbfgs',
                c1=0.1,
                c2=0.1,
                max_iterations=100,
                all_possible_transitions=True)

# Step 5: Model Training
X_train, X_test, y_train, y_test = train_test_split(invoice_features, annotations, test_size=0.2, random_state=42)
crf_model.fit(X_train, y_train)

# Step 6: Evaluation
y_pred = crf_model.predict(X_test)
y_test_flat = [item for sublist in y_test for item in sublist]
y_pred_flat = [item for sublist in y_pred for item in sublist]
f1_score = flat_f1_score(y_test_flat, y_pred_flat, average='weighted')
print("F1-score:", f1_score)

# Step 7: Iterative Improvement
# Experiment with different hyperparameters or features and retrain the model
# Example:
# crf_model = CRF(algorithm='lbfgs', c1=0.2, c2=0.2, max_iterations=200, all_possible_transitions=True)
# crf_model.fit(X_train, y_train)
# Evaluate the updated model
# Perform further iterations until satisfactory performance is achieved
