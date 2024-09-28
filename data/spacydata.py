import spacy

nlp = spacy.load('en_core_web_sm')
def get_text_data():
    with open('transcription.txt', 'r', encoding='utf-8') as file:
        text_data = file.read()
    return text_data

doc = nlp(get_text_data())
for ent in doc.ents:
    print(ent.text, ent.label_)

get_text_data()
