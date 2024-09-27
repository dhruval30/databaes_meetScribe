import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
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

load_dotenv()

app = Flask(__name__)

# Configure CORS to allow specific origins and handle preflight requests
CORS(app, resources={r"/*": {"origins": ["http://localhost:5500", "http://127.0.0.1:5500"]}}, supports_credentials=True)

# Global variables to store transcription data and conversation memory
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
    Use the provided transcription to answer questions about the meeting. 
    Keep track of the conversation context, and maintain a coherent conversation across multiple questions.
    If specific details are missing, provide general insights based on the transcription's content and context.
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
    response = conversation.predict(human_input=user_question)
    
    return response

# API Endpoint to Upload Transcription
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

# API Endpoint to Ask Question
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
    app.run(host="0.0.0.0", port=5001, debug=True)
