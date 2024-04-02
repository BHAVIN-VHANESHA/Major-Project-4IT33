import json
import re
import time
import spacy
import random
from spacy.training.example import Example


def convert_json_to_training_data(file_path, split_ratio=0.8):
    data = []
    with open(file_path, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
        for entry in json_data:
            text = entry['text']
            entities = []
            for entity in entry['entities']:
                start = entity['start']
                end = entity['end']
                label = entity['label']
                entities.append((start, end, label))
            example = (text, {"entities": entities})
            data.append(example)
    random.shuffle(data)  # Shuffle the data
    split_index = int(len(data) * split_ratio)
    training_data = data[:split_index]
    testing_data = data[split_index:]
    return training_data, testing_data


def trim_entity_spans(data):
    """Remove leading and trailing whitespace from entity spans."""
    cleaned_data = []
    for text, annotations in data:
        entities = annotations['entities']
        valid_entities = []
        for start, end, label in entities:
            while start < len(text) and text[start].isspace():
                start += 1
            while end > start and text[end - 1].isspace():
                end -= 1
            valid_entities.append((start, end, label))
        cleaned_data.append((text.strip(), {'entities': valid_entities}))
    return cleaned_data


# File path where the data is stored
DATA_FILE = '/home/bhavin/PycharmProjects/Major-Project-4IT33/ner_data.json'

# Start measuring the time
start_time = time.time()

# Convert JSON data into training and testing data
TRAIN_DATA, TEST_DATA = convert_json_to_training_data(DATA_FILE)

# Clean training and testing data
TRAIN_DATA = trim_entity_spans(TRAIN_DATA)
TEST_DATA = trim_entity_spans(TEST_DATA)

# Initialize spaCy model
nlp = spacy.blank("en")

# Create the NER component
ner = nlp.add_pipe("ner")
ner.cfg['hidden_depth'] = 3

# Add custom labels to the NER model
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable other pipelines during training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]

# Training the NER model
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    for itn in range(100):
        random.shuffle(TRAIN_DATA)
        losses = {}
        for text, annotations in TRAIN_DATA:
            example = Example.from_dict(nlp.make_doc(text), annotations)
        nlp.update([example], drop=0.5, losses=losses)
        print("Losses at iteration {}: {}".format(itn, losses))


# Test the trained model and calculate accuracy
correct_predictions = 0
total_predictions = 0

for text, annotations in TEST_DATA:
    doc = nlp(text)
    predicted_entities = {(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents}
    gold_entities = set((start, end, label) for start, end, label in annotations.get("entities"))
    correct_predictions += len(predicted_entities & gold_entities)
    total_predictions += len(gold_entities)

# Calculate accuracy
accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
print("Accuracy: {:.2%}".format(accuracy))

# Stop measuring the time
end_time = time.time()

# Calculate the execution time
execution_time = end_time - start_time
print("Execution time: {:.2f} seconds".format(execution_time))

# Save the trained NER model to disk
ner_model_output_dir = "/home/bhavin/PycharmProjects/Major-Project-4IT33/NER_Training_Model"
nlp.to_disk(ner_model_output_dir)
