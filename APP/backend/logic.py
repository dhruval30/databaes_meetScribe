import os
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
import json

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["http://localhost:5501", "http://127.0.0.1:5501"]}}, supports_credentials=True)

# In-memory storage for now; switch to a database in production
chat_history = []

transcription_data = ""
memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)

def upload_transcription_from_file(file_path):
    """Reads the transcription from a file."""
    global transcription_data
    try:
        with open(file_path, 'r') as file:
            transcription_data = file.read()
            print("Transcription uploaded successfully from file.")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"An error occurred while reading the file: {str(e)}")

def ask_question(user_question):
    """Send the user's question to the language model."""
    global transcription_data, memory

    if not transcription_data:
        raise ValueError("No transcription data found. Please upload the transcription first.")

    system_prompt = """
    You are a helpful conversational assistant with knowledge about a specific meeting transcription. 
    The user will ask questions about the meeting transcription. Your task is to:
    
    - Extract clear, actionable points from the meeting transcription.
    - Provide responses in a natural language, conversational style.
    """

    groq_api_key = os.getenv("GROQ_API_KEY")
    model = 'llama3-8b-8192'
    
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=f"{system_prompt}\n\nMeeting Transcription:\n{transcription_data}"),
            MessagesPlaceholder(variable_name="chat_history"),  
            HumanMessagePromptTemplate.from_template("{human_input}")
        ]
    )

    conversation = LLMChain(llm=groq_chat, prompt=prompt, verbose=False, memory=memory)
    raw_response = conversation.predict(human_input=user_question)
    
    # Save chat history
    chat_history.append({"user_message": user_question, "bot_response": raw_response})
    save_chat_history()
    
    return raw_response  # Returning raw response as plain text

def save_chat_history():
    with open('chat_history.json', 'w') as f:
        json.dump(chat_history, f)

def load_chat_history():
    global chat_history
    if os.path.exists('chat_history.json'):
        with open('chat_history.json', 'r') as f:
            chat_history = json.load(f)

@app.route('/upload-transcription', methods=['POST'])
def upload_transcription():
    """API to upload a transcription file from the frontend."""
    global transcription_data

    if 'transcription' not in request.files:
        return jsonify({"error": "No transcription file found."}), 400

    file = request.files['transcription']

    try:
        transcription_data = file.read().decode('utf-8')
        return jsonify({"message": "Transcription uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Error reading the file: {str(e)}"}), 500

@app.route('/ask-question', methods=['POST'])
def handle_question():
    """API to handle questions from the frontend."""
    data = request.json
    user_question = data.get('question')

    if not user_question:
        return jsonify({"error": "No question provided."}), 400

    try:
        response = ask_question(user_question)
        return jsonify({"response": response}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

if __name__ == "__main__":
    load_chat_history()  
    app.run(host="0.0.0.0", port=5001, debug=True)
