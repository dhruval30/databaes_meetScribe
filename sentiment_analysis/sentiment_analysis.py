import pandas as pd
from transformers import pipeline

classifier_sentiment = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=False)

user_dialogues = pd.read_csv('sentiment_analysis/diarized_text.csv')

def analyze_sentiment(dialogue):
    return classifier_sentiment(dialogue)

user_dialogues['Sentiment Scores'] = user_dialogues['Dialogue'].apply(analyze_sentiment)

sentiment_df = user_dialogues['Sentiment Scores'].apply(pd.Series)

result_df = pd.concat([user_dialogues], axis=1)

result_df.to_csv('sentiment_analysis/sentiment_analysis_results.csv', index=False)

print(result_df)


