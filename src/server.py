from langchain_google_genai import ChatGoogleGenerativeAI
from data_ingestion import DataIngestion

class LLM:
    def __init__(self):
        self.llm = self.initialize_llm()

    def initialize_llm(self, model_name="gemini-2.5-flash", max_tokens=None):
        # Initialize the Google Generative AI model with desired parameters
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            max_tokens=max_tokens,
            timeout=None,
            max_retries=2,
        )
    
    def call(self, prompt, context=None, chat_history=[], image_urls=None, input_files=None, *args, **kwargs):
        try:
            # Call the model with the provided prompt and context
            messages = self.format_messages(prompt, context, chat_history)
            response = self.llm.predict_messages(
                messages=messages,
                image_urls=image_urls,
                input_files=input_files,
                *args,
                **kwargs
            )
            self.update_history(chat_history, prompt, response)
            return response
        except Exception as e:
            raise Exception(f"Failed to call LLM: {str(e)}")

    def format_messages(self, prompt, context=None, chat_history=[]):
        try:
            # Format the messages for the chat model
            messages = []
            for i, (user_msg, bot_msg) in enumerate(chat_history):
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": bot_msg})
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            return messages
        except Exception as e:
            raise Exception(f"Failed to format messages: {str(e)}")
    
    def update_history(self, chat_history, user_msg, bot_msg):
        # Update the chat history with the latest interaction
        try:
            chat_history.append((user_msg, bot_msg))
            return chat_history
        except Exception as e:
            raise Exception(f"Failed to update chat history: {str(e)}")
    
    def retrieve_context(self, query, top_k=5):
        # Placeholder for context retrieval logic
        try:
            data_ingestion = DataIngestion()
            context = data_ingestion.pc.similarity_search(query, top_k=top_k)
            return context
        except Exception as e:
            raise Exception(f"Failed to retrieve context: {str(e)}")
    
    def retrieve_chat_history(self, user_id, chat_id="default_chat"):
        # Placeholder for chat history retrieval logic
        try:
            if not user_id:
                raise Exception("User ID is required to retrieve chat history")
            return []
        except Exception as e:
            raise Exception(f"Failed to retrieve chat history: {str(e)}")