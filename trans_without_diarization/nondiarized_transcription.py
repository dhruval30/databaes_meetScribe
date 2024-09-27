from transformers import pipeline
from pydub import AudioSegment

pipe = pipeline("automatic-speech-recognition", model="fractalego/personal-speech-to-text-model")

audio = AudioSegment.from_file("audio-data/Weekly Package Team Meeting 08-26-19.mp3")

chunk_length_ms = 10 * 1000  # 10 seconds

chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

with open("trans_without_diarization/transcription_without_diarization.txt", "w") as f:
    for i, chunk in enumerate(chunks):
        chunk.export("trans_without_diarization/temporary_chunk.wav", format="wav")
        
        result = pipe("trans_without_diarization/temporary_chunk.wav")
        f.write(f"{result['text']}")
        print(f"Transcribed Chunk {i + 1}: {result['text']}")