import os
import pandas as pd
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

transcription_chunks = []
memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)

MAX_TOKENS_PER_CHUNK = 1000  

def chunk_text(text, max_tokens):
    chunks = []
    while len(text) > max_tokens:
        chunk = text[:max_tokens]
        text = text[max_tokens:]
        chunks.append(chunk)
    chunks.append(text) 
    return chunks

def upload_transcription_and_sentiments_from_csv(file_path):
    global transcription_chunks

    try:
        df = pd.read_csv(file_path)
        
        required_columns = ["Speaker", "Dialogue", "anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in the CSV.")
        
        transcription_data = ""
        for index, row in df.iterrows():
            dialogue = row["Dialogue"]
            speaker = row["Speaker"]
            sentiment_summary = (f"Anger: {row['anger']}, Disgust: {row['disgust']}, "
                                 f"Fear: {row['fear']}, Joy: {row['joy']}, Neutral: {row['neutral']}, "
                                 f"Sadness: {row['sadness']}, Surprise: {row['surprise']}")
            transcription_data += f"{speaker}: {dialogue}\nSentiments: {sentiment_summary}\n\n"
        
        transcription_chunks = chunk_text(transcription_data, MAX_TOKENS_PER_CHUNK)
        
        print(f"Transcription and sentiments uploaded successfully. Split into {len(transcription_chunks)} chunks.")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"An error occurred while reading the CSV file: {str(e)}")

def feed_chunks_to_model():
    global transcription_chunks, memory

    if not transcription_chunks:
        raise ValueError("No transcription data found. Please upload the transcription first.")
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    model = 'llama3-8b-8192'
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)

    for i, chunk in enumerate(transcription_chunks):
        print(f"Feeding chunk {i + 1}/{len(transcription_chunks)} to the model...")

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

        LLMChain(llm=groq_chat, prompt=prompt, verbose=False, memory=memory)

    print("All chunks have been fed to the model. You can now start asking questions.\n")

def ask_question(user_question):
    """Function to ask questions about the transcription context with conversation history."""
    global memory

    groq_api_key = os.getenv("GROQ_API_KEY")
    model = 'llama3-8b-8192'
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)

    system_prompt = """
    You are a helpful conversational assistant with knowledge about a specific meeting transcription and its associated sentiment scores. 
    Use the provided transcription and sentiment information to answer questions about the meeting. 
    Keep track of the conversation context, and maintain a coherent conversation across multiple questions.
    """

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

def start_conversation_cli():
    """Start a conversation in the CLI after all chunks have been fed."""
    print("\nWelcome to the meeting assistant. Start asking questions about the meeting transcription and sentiments.")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        user_question = input("You: ")
        if user_question.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break
        response = ask_question(user_question)
        print(f"Assistant: {response}\n")

if __name__ == "__main__":

    transcription_file_path = "sentiment_analysis/sentiment_analysis_with_all_scores.csv"
    
    upload_transcription_and_sentiments_from_csv(transcription_file_path)
    feed_chunks_to_model()
    start_conversation_cli()
