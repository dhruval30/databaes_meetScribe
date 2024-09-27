import pandas as pd
from transformers import pipeline
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import numpy as np

classifier_sentiment = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
user_dialogues = pd.read_csv('sentiment_analysis/diarized_text.csv')

def analyze_sentiment(dialogue):
    scores = classifier_sentiment(dialogue)
    return {score['label']: score['score'] for score in scores[0]} 

user_dialogues['Sentiment Scores'] = user_dialogues['Dialogue'].apply(analyze_sentiment)

sentiments_df = pd.json_normalize(user_dialogues['Sentiment Scores'])

user_dialogues = pd.concat([user_dialogues, sentiments_df], axis=1)
user_dialogues['Dialogue Index'] = user_dialogues.groupby('Speaker').cumcount() + 1
user_dialogues.to_csv('sentiment_analysis/sentiment_analysis_with_all_scores.csv', index=False)


unique_speakers = user_dialogues['Speaker'].unique()


for speaker in unique_speakers:
    speaker_data = user_dialogues[user_dialogues['Speaker'] == speaker]
    

    plt.figure(figsize=(10, 6))
    
    for sentiment in sentiments_df.columns:
        x = speaker_data['Dialogue Index']
        y = speaker_data[sentiment]
        
        if len(x) > 3:  
            x_smooth = np.linspace(x.min(), x.max(), 300)  
            spline = make_interp_spline(x, y, k=3)  
            y_smooth = spline(x_smooth)
            
            plt.plot(x_smooth, y_smooth, label=f'{sentiment}')  
        else:
            plt.plot(x, y, label=f'{sentiment}', marker='o')  

    plt.title(f'Sentiment Progression for {speaker}')
    plt.xlabel('Dialogue Index')
    plt.ylabel('Sentiment Score')
    plt.ylim(0, 1) 
    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.tight_layout()
    
    plt.savefig(f'sentiment_images/sentiment_progress_{speaker}.png')  
    
    plt.close()  
