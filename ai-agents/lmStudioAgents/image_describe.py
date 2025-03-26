#!/usr/bin/env -S uv run --script

# /// script
# dependencies = [
#   "openai-agents>=0.0.6",
#   "rich>=13.9.4",
#   "openai>=1.68.2",
#   "python-dotenv>=1.0.0",
# ]
# ///

from openai import OpenAI
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LM Studio configuration
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"

# Set environment variables for OpenAI API
os.environ["OPENAI_API_KEY"] = "dummy-key"  # LM Studio doesn't need a real API key
os.environ["OPENAI_API_BASE"] = LM_STUDIO_BASE_URL

# Create OpenAI client configured for LM Studio
client = OpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key="dummy-key"  # LM Studio doesn't need a real API key
)

def check_model_capabilities():
    """Check if the current model in LM Studio supports vision capabilities"""
    try:
        # Try to get model information
        models = client.models.list()
        print("Available models:")
        for model in models.data:
            print(f"- {model.id}")
        return True
    except Exception as e:
        print(f"Error checking model capabilities: {str(e)}")
        return False

def send_text_message(message):
    """Send a simple text message to test the LM Studio connection"""
    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=[{"role": "user", "content": message}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def send_message_with_vision(messages, image_path):
    """
    Sends a message to the agent including an image and prompts for vision analysis.
    
    Note: This function assumes your LM Studio model supports vision capabilities.
    Not all local models have vision capabilities.

    Args:
        messages (list): A list of previous messages in the conversation history.
                         Each message is a dictionary with 'role' and 'content' keys.
        image_path (str): The path to the image file on your system.

    Returns:
        str: The agent's response as text, or an error message if something went wrong.
    """
    try:
        # Check if the image file exists
        if not os.path.exists(image_path):
            return f"Error: Image file '{image_path}' not found."
            
        # Get the file size and check if it's reasonable
        file_size = os.path.getsize(image_path) / (1024 * 1024)  # Size in MB
        print(f"Image file size: {file_size:.2f} MB")
        
        if file_size > 4:
            return f"Error: Image file is too large ({file_size:.2f} MB). Please use an image smaller than 4MB."
        
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            
        print(f"Successfully encoded image, length: {len(encoded_string)} characters")

        # Construct the message with the image data
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this image and tell me what you see."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_string}",
                        "detail": "high"
                    }
                }
            ]
        }

        # Combine the new message with the existing conversation history
        all_messages = messages + [message]
        
        print("Sending request to LM Studio...")

        # Call the OpenAI ChatCompletion API via LM Studio
        response = client.chat.completions.create(
            model="local-model",  # LM Studio uses the currently loaded model
            messages=all_messages,
            max_tokens=500,
            temperature=0.7
        )
        
        print("Received response from LM Studio")
        
        return response.choices[0].message.content

    except FileNotFoundError:
        return "Error: Image file not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage
if __name__ == "__main__":
    print("Testing LM Studio connection...")
    
    # Check if LM Studio is running and what models are available
    check_model_capabilities()
    
    # Test with a simple text message first
    print("\nTesting text completion...")
    text_response = send_text_message("Hello, can you help me with some information?")
    print(f"Text response: {text_response}")
    
    # Ask if the user wants to try vision
    try_vision = input("\nDo you want to try vision capabilities? (y/n): ").lower()
    
    if try_vision == 'y':
        # Example conversation history (can be empty for a new conversation)
        conversation = []
        
        # Path to your image file
        image_file_path = input("Enter the path to your image file: ")
        
        # Send the message with the image
        print("\nSending image for analysis...")
        response = send_message_with_vision(conversation, image_file_path)
        
        # Print the response
        print("\nAgent Response:" + "-" * 29)
        print(response)
    else:
        print("Vision test skipped.")
        
    print("\nDone!")