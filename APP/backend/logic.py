import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5501", "http://127.0.0.1:5501"]}}, supports_credentials=True)

# Set max token length for chunking
MAX_TOKENS_PER_CHUNK = 1000  
transcription_chunks = []
memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)

# Ensure the uploads folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ======== HELPER FUNCTIONS ========

def chunk_text(text, max_tokens):
    """Chunk the transcription data based on token size."""
    chunks = []
    while len(text) > max_tokens:
        chunk = text[:max_tokens]
        text = text[max_tokens:]
        chunks.append(chunk)
    chunks.append(text)  # Append the last chunk
    return chunks

def upload_transcription_and_sentiments_from_csv(file_path):
    global transcription_chunks

    try:
        df = pd.read_csv(file_path)
        
        # Ensure all required columns are present; if not, fill with default values
        required_columns = ["Speaker", "Dialogue", "anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0.0  # Default value for missing sentiment columns
        
        # Prepare the transcription data with sentiments
        transcription_data = ""
        for index, row in df.iterrows():
            dialogue = row["Dialogue"]
            speaker = row["Speaker"]
            sentiment_summary = (f"Anger: {row['anger']}, Disgust: {row['disgust']}, "
                                 f"Fear: {row['fear']}, Joy: {row['joy']}, Neutral: {row['neutral']}, "
                                 f"Sadness: {row['sadness']}, Surprise: {row['surprise']}")
            transcription_data += f"{speaker}: {dialogue}\nSentiments: {sentiment_summary}\n\n"
        
        # Split the transcription data into manageable chunks
        transcription_chunks = chunk_text(transcription_data, MAX_TOKENS_PER_CHUNK)
        
        print(f"Transcription and sentiments uploaded successfully. Split into {len(transcription_chunks)} chunks.")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"An error occurred while reading the CSV file: {str(e)}")


def feed_chunks_to_model():
    """Feeds the transcription chunks to the language model."""
    global transcription_chunks, memory

    if not transcription_chunks:
        raise ValueError("No transcription data found. Please upload the transcription first.")
    
    # Set up the language model
    groq_api_key = os.getenv("GROQ_API_KEY")
    model = 'llama3-8b-8192'
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)

    for i, chunk in enumerate(transcription_chunks):
        print(f"Feeding chunk {i + 1}/{len(transcription_chunks)} to the model...")

        # Define the system prompt
        system_prompt = f"""
        You are a helpful conversational assistant. Here is part {i + 1} of a meeting transcription, including sentiment information.
        Use this information to build context for answering questions about the meeting:
        {chunk}
        """
        
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_prompt),
                MessagesPlaceholder(variable_name="chat_history")
            ]
        )

        # Feed the chunk to the model
        LLMChain(llm=groq_chat, prompt=prompt, verbose=False, memory=memory)

    print("All chunks have been fed to the model. You can now start asking questions.")

def ask_question(user_question):
    """Sends a question to the language model and returns the response."""
    global memory

    groq_api_key = os.getenv("GROQ_API_KEY")
    model = 'llama3-8b-8192'
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)

    system_prompt = """
    You are a helpful conversational assistant with knowledge about a specific meeting transcription and its associated sentiment scores. 
    Use the provided transcription and sentiment information to answer questions about the meeting. 
    Keep track of the conversation context, and maintain a coherent conversation across multiple questions.
    """

    # Define the prompt for the conversation
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),  
            HumanMessagePromptTemplate.from_template("{human_input}")
        ]
    )

    conversation = LLMChain(llm=groq_chat, prompt=prompt, verbose=False, memory=memory)
    response = conversation.predict(human_input=user_question)
    
    return response

# ======== API ROUTES ========

@app.route('/upload-transcription', methods=['POST'])
def upload_transcription():
    """API to upload and process the transcription CSV file."""
    if 'transcription' not in request.files:
        return jsonify({"error": "No transcription file found."}), 400

    file = request.files['transcription']
    
    # Validate the file format
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

    try:
        # Save the file to the uploads folder
        csv_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(csv_file_path)

        # Process the CSV file
        upload_transcription_and_sentiments_from_csv(csv_file_path)
        feed_chunks_to_model()
        
        return jsonify({"message": "Transcription and sentiments uploaded and processed successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Error processing the file: {str(e)}"}), 500

@app.route('/ask-question', methods=['POST'])
def handle_question():
    """API to handle user questions."""
    data = request.json
    user_question = data.get('question')

    if not user_question:
        return jsonify({"error": "No question provided."}), 400

    try:
        response = ask_question(user_question)
        return jsonify({"response": response}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

# ======== MAIN ========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
