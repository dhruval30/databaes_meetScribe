# Database_meetScribe

After sitting through one too many endless meetings, we figured: why not let an AI take notes, summarize the chaos, and even tell us who's slacking?

## Painfully Managed Setup

This project has been through quite a journey. I've lost track of the exact dependencies required to get everything working smoothly. If you're brave enough to run this on another machine, please be prepared for a wild ride.

Getting everything set up might involve additional configuration due to specific dependencies that might be missing or outdated.

## Features

- **Speaker Diarization**: Automatically tracks who’s talking (no more "who said that?" confusion).
- **Context-Aware Summaries**: Turns hours of conversation into bite-sized, meaningful summaries.
- **Action Point Extraction**: Pulls out tasks, so your "to-do" list basically writes itself.
- **Sentiment Analysis**: Get the emotional tone of the conversation.

---

## Key Dependencies and Special Mentions

This project leverages several advanced models and APIs, which are integral to its core functionality. Special mention goes to the following:

### Hugging Face Models

- **ASR Model**: This project uses the `fractalego/personal-speech-to-text-model` from Hugging Face for automatic speech recognition (ASR). The model is instantiated as follows:

    ```python
    pipe = pipeline("automatic-speech-recognition", model="fractalego/personal-speech-to-text-model")
    ```

- **Sentiment Analysis Model**: For emotion detection and sentiment analysis, the project uses the Hugging Face `j-hartmann/emotion-english-distilroberta-base` model, which provides a comprehensive breakdown of emotions in the analyzed text:

    ```python
    classifier_sentiment = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
    ```

### LLaMA

The project integrates the LLaMA3 model for generating conversational responses based on the transcription and sentiment data. This is done through the `LLMChain` from LangChain, which allows for prompt-based conversation handling.

### Gemma

These models play a role in advanced natural language understanding and generation.

### LangChain

LangChain provides the core infrastructure for connecting the LLMs with the conversational prompts and managing context across interactions.

### Cohere API

This API is used for additional language processing tasks, such as embedding generation and topic extraction.

### SpaCy

For any underlying natural language processing tasks like tokenization and lemmatization, SpaCy has been incorporated into the project.

---

## Final Thoughts

If you've made it this far, you're likely as determined as we were. meetScribe started off as a fun hackathon project—we wanted to explore AI’s capabilities. 

Be warned: running this on your machine might require a bit of patience. But once it's up and running, you'll never look at meeting minutes the same way again.

Good luck! And thank you!
