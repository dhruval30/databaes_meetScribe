import os
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ASSEMBLYAI_API_KEY")

aai.settings.api_key = api_key

FILE_URL = 'audio-data/Weekly Package Team Meeting 08-26-19.mp3'
config = aai.TranscriptionConfig(speaker_labels=True)

transcriber = aai.Transcriber()



transcript = transcriber.transcribe(
    FILE_URL,
    config=config
)


with open("trans_with_diarization/diarized_text.txt", "w") as file:
    for utterance in transcript.utterances:
        file.write(f"Speaker {utterance.speaker}: {utterance.text}\n")

print("Transcription saved to transcription.txt")


