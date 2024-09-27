import os
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

transcription_data = ""
memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)

def upload_transcription_from_file(file_path):
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
    # model = 'llama3-70b-8192'
    
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

def start_conversation_cli():

    print("\nWelcome to the meeting assistant. Start asking questions about the meeting transcription.")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        user_question = input("You: ")
        if user_question.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break
        response = ask_question(user_question)

        print(f"Assistant: {response}\n")

if __name__ == "__main__":
    transcription_file_path = "sentiment_analysis/diarized_text.txt"
    
    upload_transcription_from_file(transcription_file_path)
    start_conversation_cli()
