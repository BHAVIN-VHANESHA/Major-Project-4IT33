import csv
import os
import time
import spacy
import random
from spacy.training.example import Example


# Function to read data from CSV file and convert it into training and testing data
def convert_csv_to_training_data(file_path, split_ratio=0.8):
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            label = row['LABELS']
            value = row['VALUES']
            start_idx = 0
            end_idx = len(value)
            entities = [(start_idx, end_idx, label)]
            example = (value, {"entities": entities})
            data.append(example)
    random.shuffle(data)  # Shuffle the data
    # print(data)
    split_index = int(len(data) * split_ratio)
    training_data = data[:split_index]
    # print(f'TRAINING DATA: {training_data}')
    testing_data = data[split_index:]
    # print(f'TESTING DATA: {testing_data}')
    return training_data, testing_data


# File path where the data is stored
DATA_FILE = '/home/bhavin/PycharmProjects/Major-Project-4IT33/ner_data.csv'

# Start measuring the time
start_time = time.time()

# Convert CSV data into training and testing data
TRAIN_DATA, TEST_DATA = convert_csv_to_training_data(DATA_FILE)

# Initialize spaCy model
nlp = spacy.blank("en")

# Create a blank NER model
ner = nlp.add_pipe("ner")

# Add custom labels to the NER model
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable other pipelines
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]

# Training the NER model
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    for itn in range(100):
        random.shuffle(TRAIN_DATA)
        losses = {}
        examples = []
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        nlp.update(examples, drop=0.5, losses=losses)
        # print("Losses at iteration {}: {}".format(itn, losses))


# Test the trained model and calculate accuracy
correct_predictions = 0
total_predictions = 0

for text, annotations in TEST_DATA:
    doc = nlp(text)
    predicted_entities = [(ent.text, ent.label_) for ent in doc.ents]
    # print(predicted_entities)
    for start, end, label in annotations.get("entities"):
        total_predictions += 1
        if (text[start:end], label) in predicted_entities:
            correct_predictions += 1

# Calculate accuracy
accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
print("Accuracy: {:.2%}".format(accuracy))

# Stop measuring the time
end_time = time.time()

# Calculate the execution time
execution_time = end_time - start_time
# print("Execution time: {:.2f} seconds".format(execution_time))

# Get the size of the file
file_size = os.path.getsize(DATA_FILE)
# print("File size: {:.2f} KB".format(file_size / 1024))  # Convert bytes to KB

# Save the trained NER model to disk
ner_model_output_dir = "/home/bhavin/PycharmProjects/Major-Project-4IT33/NER_Training_Model"
nlp.to_disk(ner_model_output_dir)
