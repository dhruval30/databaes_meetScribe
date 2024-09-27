import spacy

# Load spaCy's English model
nlp = spacy.load('en_core_web_sm')

# Function to read text data from a file and return it
def get_text_data():
    with open('transcription.txt', 'r', encoding='utf-8') as file:
        text_data = file.read()
    return text_data

# Optionally process the text to extract named entities
doc = nlp(get_text_data())

# Extract entities such as dates, people, numbers, etc.
for ent in doc.ents:
    print(ent.text, ent.label_)

get_text_data()
