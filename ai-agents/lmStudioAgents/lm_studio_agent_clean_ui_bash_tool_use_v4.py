#!/usr/bin/env -S uv run --script

# /// script
# dependencies = [
#   "openai-agents>=0.0.6",
#   "rich>=13.9.4",
#   "openai>=1.68.2",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""
LM Studio Local Agent Example with Streaming

This example demonstrates how to create an interactive agent using the OpenAI Agents SDK
with LM Studio as the backend. The agent responds to user queries in an ongoing conversation
with streaming output, using a local LLM model.

Run with:
    uv run lm_studio_agent_clean_ui_bash_tool_use_v4.py

Then, type your messages and press enter. Type 'exit' to quit.

Note: This script requires LM Studio to be running on http://localhost:1234/v1
"""

import os
import sys
import json
import subprocess
import base64
from typing import AsyncGenerator, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import asyncio
from openai import AsyncOpenAI, RateLimitError
from agents import Agent
import time
import random
from rich.live import Live

# Initialize console for rich output
console = Console()

# Initialize conversation history
conversation_history = []

# LM Studio configuration
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"

# Set environment variables for OpenAI API
os.environ["OPENAI_API_KEY"] = "dummy-key"
os.environ["OPENAI_API_BASE"] = LM_STUDIO_BASE_URL

# Create AsyncOpenAI client configured for LM Studio
openai_client = AsyncOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key=os.environ["OPENAI_API_KEY"]
)

# Define color styles that work well in Windows terminals
USER_STYLE = "bold magenta"  
ASSISTANT_STYLE = "white"
ERROR_STYLE = "bold red"
INFO_STYLE = "bold white"
WARNING_STYLE = "yellow"
SYSTEM_STYLE = "bold cyan"
THINKING_STYLE = "bold cyan"
SPINNER_STYLE = "bold cyan"
WELCOME_STYLE = "bold magenta"

# Define API parameters
API_TEMPERATURE = 0.1
API_MAX_TOKENS_INITIAL = 4096
API_MAX_TOKENS_FOLLOWUP = 1024
API_TIMEOUT_INITIAL = 60    
API_TIMEOUT_FOLLOWUP = 60
# Additional OpenAI API parameters
API_TOP_P = 0.95
API_FREQUENCY_PENALTY = 1.1  # Number between -2.0 and 2.0
API_PRESENCE_PENALTY = 0.5   # Number between -2.0 and 2.0
API_N = 1  # Must be exactly 1 as per OpenAI API requirements
API_PARALLEL_TOOL_CALLS = True
API_TOOL_CHOICE = "auto"  # Can be "auto", "required", or "none"

# Interface messages
WELCOME_MESSAGE = "Master, would you like to code? You will be pleased."

# Define thinking phrases
THINKING_PHRASES = [
    "Pondering...",
    "Formulating...",
    "Noodling...",
    "Plotting...", 
    "Scheming...",
    "Unraveling...",
    "Manifesting...",
    "Conjuring....",
    "Processing...",
    "Executing..."
]

# Tool definitions following OpenAI API format
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a new file with the specified content",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to create"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "replace_text",
            "description": "Replace text in a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "search_text": {
                        "type": "string",
                        "description": "Text to search for"
                    },
                    "replace_text": {
                        "type": "string",
                        "description": "Text to replace with"
                    }
                },
                "required": ["file_path", "search_text", "replace_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "insert_line",
            "description": "Insert a line at a specific position in a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "line_number": {
                        "type": "integer",
                        "description": "Line number to insert at (1-based)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to insert"
                    }
                },
                "required": ["file_path", "line_number", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a bash command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_file",
            "description": "View the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to view"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "describe_image",
            "description": "Analyze and describe the contents of an image using the LM Studio vision model",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file to analyze"
                    }
                },
                "required": ["image_path"]
            }
        }
    }
]

def find_file(file_path: str) -> Dict[str, Any]:
    """Find a file by name, with fuzzy matching if exact match not found."""
    # First check if the path exists as provided
    if os.path.exists(file_path):
        return {
            "status": "found",
            "file_path": file_path,
            "message": f"File found: {file_path}"
        }
    
    # Get the base name and directory from the path
    directory = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    
    # If no directory was specified, try current directory first
    if not directory:
        try:
            # Check current directory
            cwd = os.getcwd()
            cwd_path = os.path.join(cwd, base_name)
            if os.path.exists(cwd_path):
                return {
                    "status": "found",
                    "file_path": cwd_path,
                    "message": f"File found in current directory: {cwd_path}"
                }
            
            # If not found in current directory, use current directory for search
            directory = cwd
        except Exception as e:
            console.print(f"[{ERROR_STYLE}]Error accessing current directory: {str(e)}[/{ERROR_STYLE}]")
            directory = "."
    else:
        # Use the provided directory
        directory = directory or "."
    
    try:
        files = os.listdir(directory)
        matches = [f for f in files if f.startswith(base_name)]
        
        if not matches:
            matches = [f for f in files if base_name.lower() in f.lower()]
        
        if matches:
            if len(matches) == 1:
                matched_path = os.path.join(directory, matches[0])
                return {
                    "status": "found",
                    "file_path": matched_path,
                    "message": f"Found similar file: {matched_path}"
                }
            return {
                "status": "suggestions",
                "suggestions": matches,
                "message": f"Multiple possible matches found: {', '.join(matches)}"
            }
        
        abs_directory = os.path.abspath(directory)
        return {
            "status": "not_found",
            "message": f"No files matching '{base_name}' found in directory: {abs_directory}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error searching for files: {str(e)}"
        }

def create_file(file_path: str, content: str) -> Dict[str, Any]:
    """Create a new file with the specified content."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {
            "status": "success", 
            "message": f"File created at {file_path}",
            "content": content
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def replace_text(file_path: str, search_text: str, replace_text: str) -> Dict[str, Any]:
    """Replace text in a file."""
    try:
        file_result = find_file(file_path)
        
        if file_result["status"] == "found":
            actual_path = file_result["file_path"]
            with open(actual_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if search_text not in content:
                return {"status": "error", "message": f"Text '{search_text}' not found in {actual_path}"}

            new_content = content.replace(search_text, replace_text)
            with open(actual_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return {
                "status": "success", 
                "message": f"Replaced '{search_text}' with '{replace_text}' in {actual_path}",
                "updated_content": new_content,
                "file_path": actual_path
            }
        elif file_result["status"] == "suggestions":
            return {
                "status": "error",
                "message": f"File '{file_path}' not found. Did you mean one of these? {', '.join(file_result['suggestions'])}"
            }
        return {"status": "error", "message": file_result["message"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def insert_line(file_path: str, line_number: int, content: str) -> Dict[str, Any]:
    """Insert a line at a specific position in a file."""
    try:
        file_result = find_file(file_path)
        
        if file_result["status"] == "found":
            actual_path = file_result["file_path"]
            with open(actual_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if line_number < 1 or line_number > len(lines) + 1:
                return {"status": "error", "message": f"Invalid line number: {line_number}. File has {len(lines)} lines."}

            lines.insert(line_number - 1, content if content.endswith('\n') else content + '\n')
            updated_content = ''.join(lines)
            
            with open(actual_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            return {
                "status": "success", 
                "message": f"Inserted line at position {line_number} in {actual_path}",
                "updated_content": updated_content,
                "file_path": actual_path
            }
        elif file_result["status"] == "suggestions":
            return {
                "status": "error",
                "message": f"File '{file_path}' not found. Did you mean one of these? {', '.join(file_result['suggestions'])}"
            }
        return {"status": "error", "message": file_result["message"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def execute_command(command: str) -> Dict[str, Any]:
    """Execute a bash command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        message = f"Command executed successfully: '{command}'" if result.returncode == 0 else f"Command failed with return code {result.returncode}: '{command}'"

        return {
            "status": "success" if result.returncode == 0 else "error",
            "message": message,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def view_file(file_path: str) -> Dict[str, Any]:
    """View the contents of a file."""
    try:
        # Use find_file to locate the file
        file_result = find_file(file_path)
        
        if file_result["status"] == "not_found":
            return {"status": "error", "message": f"File not found: {file_path}"}
        
        if file_result["status"] == "suggestions":
            suggestions_str = ", ".join(file_result["suggestions"])
            return {"status": "error", "message": f"File not found. Did you mean one of: {suggestions_str}?"}
        
        # Read the file contents
        with open(file_result["file_path"], 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": f"Error viewing file: {str(e)}"}

def describe_image(image_path: str) -> Dict[str, Any]:
    """Describe the contents of an image using the LM Studio vision model."""
    try:
        # Use find_file to locate the image
        file_result = find_file(image_path)
        
        if file_result["status"] == "not_found":
            # Ask the user for the exact path
            console.print(f"[{INFO_STYLE}]Image file not found: {image_path}[/{INFO_STYLE}]")
            console.print(f"[{INFO_STYLE}]Please provide the exact path to the image:[/{INFO_STYLE}]")
            return {
                "status": "path_needed",
                "message": f"Image file not found: {image_path}. Please provide the exact path to the image."
            }
        
        if file_result["status"] == "suggestions":
            suggestions_str = ", ".join(file_result["suggestions"])
            console.print(f"[{INFO_STYLE}]Image file not found. Did you mean one of: {suggestions_str}?[/{INFO_STYLE}]")
            console.print(f"[{INFO_STYLE}]Please provide the exact path to the image:[/{INFO_STYLE}]")
            return {
                "status": "path_needed",
                "suggestions": file_result["suggestions"],
                "message": f"Image file not found. Did you mean one of: {suggestions_str}? Please provide the exact path to the image."
            }
        
        actual_path = file_result["file_path"]
        
        # The find_file function already checks existence, but double-check to be safe
        if not os.path.exists(actual_path):
            console.print(f"[{INFO_STYLE}]Error: Image file '{actual_path}' not found.[/{INFO_STYLE}]")
            console.print(f"[{INFO_STYLE}]Please provide the exact path to the image:[/{INFO_STYLE}]")
            return {
                "status": "path_needed",
                "message": f"Error: Image file '{actual_path}' not found. Please provide the exact path to the image."
            }
            
        # Get the file size and check if it's reasonable
        file_size = os.path.getsize(actual_path) / (1024 * 1024)  # Size in MB
        console.print(f"[{INFO_STYLE}]Image file size: {file_size:.2f} MB[/{INFO_STYLE}]")
        
        if file_size > 4:
            return {"status": "error", "message": f"Error: Image file is too large ({file_size:.2f} MB). Please use an image smaller than 20MB."}
        
        # Determine the correct MIME type based on file extension
        file_extension = os.path.splitext(actual_path)[1].lower()
        mime_type_map = {
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        mime_type = mime_type_map.get(file_extension, 'image/jpeg')  # Default to jpeg if unknown
        
        # Read and encode the image
        with open(actual_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            
        console.print(f"[{INFO_STYLE}]Successfully encoded image, length: {len(encoded_string)} characters[/{INFO_STYLE}]")

        # Construct the message with the image data
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this image and tell me what you see."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{encoded_string}",
                        "detail": "high"
                    }
                }
            ]
        }

        # Create a clean message history for the vision request (without including previous images)
        # This prevents context window overload when describing multiple images
        text_only_history = []
        for msg in conversation_history:
            # Only include text messages in the history for the vision request
            if isinstance(msg.get("content", ""), str):
                text_only_history.append(msg)
            elif isinstance(msg.get("content", []), list):
                # For messages with content as a list (like previous vision requests)
                # Only include the text part, not the image data
                new_content = [item for item in msg["content"] if item.get("type") == "text"]
                if new_content:
                    text_only_copy = msg.copy()
                    text_only_copy["content"] = new_content
                    text_only_history.append(text_only_copy)
        
        # Use the filtered conversation history
        all_messages = text_only_history + [message]
        
        console.print(f"[{INFO_STYLE}]Sending vision request to LM Studio...[/{INFO_STYLE}]")

        # Create a synchronous client for this specific call
        from openai import OpenAI
        sync_client = OpenAI(
            base_url=LM_STUDIO_BASE_URL,
            api_key="dummy-key"
        )
        
        # Call the OpenAI ChatCompletion API via LM Studio
        response = sync_client.chat.completions.create(
            model="local-model",  # LM Studio uses the currently loaded model
            messages=all_messages,
            max_tokens=600,
            temperature=0.7,
        )
        
        console.print(f"[{INFO_STYLE}]Received vision response from LM Studio[/{INFO_STYLE}]")
        
        description = response.choices[0].message.content
        
        # Add a simplified version of the message to the conversation history
        # This avoids storing the full base64 image data in the history
        simplified_user_msg = {
            "role": "user", 
            "content": f"Describe the image: {actual_path}"
        }
        conversation_history.append(simplified_user_msg)
        
        # Add the assistant's response to the conversation history
        conversation_history.append({
            "role": "assistant",
            "content": description
        })
        
        return {"status": "success", "description": description}

    except Exception as e:
        console.print(f"[{ERROR_STYLE}]Error in vision processing: {str(e)}[/{ERROR_STYLE}]")
        return {"status": "error", "message": f"An error occurred: {str(e)}"}

# Map tool names to their implementations
TOOL_MAP = {
    "create_file": create_file,
    "replace_text": replace_text,
    "insert_line": insert_line,
    "execute_command": execute_command,
    "view_file": view_file,
    "describe_image": describe_image
}

def execute_tool_call(tool_call) -> str:
    """Execute a tool call and return the result as a string."""
    try:
        tool_name = tool_call["function"]["name"]
        if tool_name not in TOOL_MAP:
            return json.dumps({"status": "error", "message": f"Unknown tool: {tool_name}"})
        
        args = json.loads(tool_call["function"]["arguments"])
        result = TOOL_MAP[tool_name](**args)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error executing tool: {str(e)}"})

def create_lm_agent() -> Agent:
    """Creates an LM Studio agent using the default model from LM Studio."""
    # Define instructions for the AI model
    system_prompt = """
    You are a helpful, accurate, and concise AI assistant designed to assist users with file manipulation, image description, command execution, and general queries.

    ### Tool Usage
    - You have access to tools for file manipulation, image description, and command execution.
    - Available tools include:
      - `create_file`: Create new files with specified content. Default to the current working directory.   
      - `replace_text`: Replace text within existing files. 
      - `insert_line`: Insert a line at a specific position in a file. 
      - `view_file`: Display the contents of a file. 
      - `execute_command`: Execute system commands. 
      - `describe_image`: Describe the image in detail.
    - Always use the appropriate tool for the requested task.
    - Provide clear and concise explanations of what you're doing and why when using tools.

    ### Command Execution
    - Be cautious with commands that might modify the system.
    - Adapt command syntax to the user's operating system. Initially, assume Windows unless told otherwise.
    - For Windows systems, use standard Command Prompt commands:
      - `del` for deleting files (not `rm` or `Remove-Item`)
      - `dir` for listing directory contents (not `ls`)
      - `copy` for copying files (not `cp`)
      - `move` for moving files (not `mv`)
      - `mkdir` for creating directories (not `md`)
      - `rmdir` for removing directories (not `rd`)
      - `type` for displaying file contents (not `cat`)
      - `echo` for printing text
    - These commands work reliably in both Command Prompt and PowerShell environments.

    ### Conversation Style
    - Respond in a friendly, conversational tone.
    - Prioritize factual, accurate information in your responses.
    - Keep answers focused and relevant to the user's question.
    - Use structured answers (e.g., lists, steps) when appropriate.
    - For coding questions, include practical examples when helpful.
    - Break down complex topics into simpler, digestible parts.

    ### Handling Uncertainty
    - If you don't know something or aren't sure:
      - Clearly state your uncertainty.
      - Avoid making up facts or speculating.
      - Suggest related areas where you can provide assistance instead.

    ### Response Format
    - When answering questions about file contents, follow these steps:
      1. Use the appropriate tool (e.g., view_file) to access the file
      2. Process the information internally without displaying the raw file contents
      3. Provide a direct answer that addresses the user's question
      4. DO NOT write code snippets that simulate what the tools already do
    - Respond in natural language, not with code blocks, unless specifically asked for code examples.
    """
    # Create and return an Agent object with the specified parameters
    return Agent(
        name="LocalAssistant",
        instructions=system_prompt,
        model="default",
    )

async def run_lm_agent(prompt: str, agent: Agent, model_name: str) -> AsyncGenerator[str, None]:
    """Streams an LM response for the given prompt using the provided agent."""
    global conversation_history
    
    conversation_history.append({"role": "user", "content": prompt})
    
    if len(conversation_history) > 50:
        conversation_history = conversation_history[-50:]
        console.print(f"[{WARNING_STYLE}]Conversation history trimmed to prevent token limit issues.[/{WARNING_STYLE}]")
    
    system_message = {"role": "system", "content": agent.instructions}
    messages = [system_message] + conversation_history
    
    try:
        stream = await openai_client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True,
            temperature=API_TEMPERATURE,
            max_tokens=API_MAX_TOKENS_INITIAL,
            timeout=API_TIMEOUT_INITIAL,
            tools=TOOLS,
            tool_choice=API_TOOL_CHOICE,
            top_p=API_TOP_P,
            frequency_penalty=API_FREQUENCY_PENALTY,
            presence_penalty=API_PRESENCE_PENALTY,
            n=API_N,
            parallel_tool_calls=API_PARALLEL_TOOL_CALLS
        )
        
        assistant_response = ""
        tool_calls = []
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                assistant_response += content
                yield content
            
            if chunk.choices[0].delta.tool_calls:
                for tool_call_delta in chunk.choices[0].delta.tool_calls:
                    if tool_call_delta.index >= len(tool_calls):
                        tool_calls.extend([{} for _ in range(tool_call_delta.index - len(tool_calls) + 1)])
                    
                    if not tool_calls[tool_call_delta.index]:
                        tool_calls[tool_call_delta.index] = {
                            "id": tool_call_delta.id,
                            "type": "function",
                            "function": {"name": "", "arguments": ""}
                        }
                    
                    if tool_call_delta.function.name:
                        tool_calls[tool_call_delta.index]["function"]["name"] = tool_call_delta.function.name
                    if tool_call_delta.function.arguments:
                        tool_calls[tool_call_delta.index]["function"]["arguments"] += tool_call_delta.function.arguments
        
        if assistant_response:
            conversation_history.append({"role": "assistant", "content": assistant_response})
        
        if tool_calls:
            conversation_history.append({
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls
            })
            
            for tool_call in tool_calls:
                if tool_call.get("function", {}).get("name"):
                    # Always show a minimal notification that a tool is being used
                    yield f"\n[Using {tool_call['function']['name']}...]\n"
                    
                    try:
                        args = json.loads(tool_call["function"]["arguments"])
                        result = TOOL_MAP[tool_call["function"]["name"]](**args)
                        
                        # Special handling for image description - display the result to the user
                        if tool_call["function"]["name"] == "describe_image":
                            if result.get("status") == "success":
                                yield f"\n{result['description']}\n"
                            elif result.get("status") == "path_needed":
                                # When image is not found, display message to user asking for the exact path
                                if "suggestions" in result:
                                    suggestions_str = ", ".join(result["suggestions"])
                                    yield f"\nImage file not found. Did you mean one of: {suggestions_str}?\nPlease provide the exact path to the image.\n"
                                else:
                                    yield f"\n{result['message']}\n"
                        
                        tool_response = {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(result)
                        }
                        conversation_history.append(tool_response)
                        
                    except Exception as e:
                        conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps({"status": "error", "message": str(e)})
                        })
                        yield f"\nError executing tool: {str(e)}\n"
            
            follow_up_stream = await openai_client.chat.completions.create(
                model=model_name,
                messages=[system_message] + conversation_history,
                stream=True,
                temperature=API_TEMPERATURE,
                max_tokens=API_MAX_TOKENS_FOLLOWUP,
                timeout=API_TIMEOUT_FOLLOWUP,
                tools=TOOLS,
                tool_choice=API_TOOL_CHOICE,
                top_p=API_TOP_P,
                frequency_penalty=API_FREQUENCY_PENALTY,
                presence_penalty=API_PRESENCE_PENALTY,
                n=API_N,
                parallel_tool_calls=API_PARALLEL_TOOL_CALLS
            )
            
            follow_up_response = ""
            async for chunk in follow_up_stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    follow_up_response += content
                    yield content
            
            if follow_up_response:
                conversation_history.append({"role": "assistant", "content": follow_up_response})
                
    except RateLimitError as e:
        console.print(f"[{ERROR_STYLE}]Rate limit exceeded: {str(e)}[/{ERROR_STYLE}]")
        yield "Rate limit exceeded. Please wait a moment before trying again."
    except Exception as e:
        console.print(f"[{ERROR_STYLE}]Error in API call: {str(e)}[/{ERROR_STYLE}]")
        yield f"Error: {str(e)}"

async def generate_response(prompt: str, agent: Agent, model_name: str):
    """Generates a full response while showing the thinking indicator."""
    full_response = ""
    start_time = time.time()
    
    thinking_phrase = random.choice(THINKING_PHRASES)
    
    with Live("", refresh_per_second=16) as live:
        elapsed_seconds = int(time.time() - start_time)
        spinner_chars = "|/-\\"
        spinner = spinner_chars[elapsed_seconds % len(spinner_chars)]
        
        styled_text = Text()
        styled_text.append(spinner, style=SPINNER_STYLE)
        styled_text.append(" ")
        styled_text.append(thinking_phrase, style=THINKING_STYLE)
        styled_text.append(f" ({elapsed_seconds}s)")
        live.update(styled_text)
        
        try:
            async for chunk in run_lm_agent(prompt, agent, model_name):
                full_response += chunk
                elapsed_seconds = int(time.time() - start_time)
                spinner = spinner_chars[elapsed_seconds % len(spinner_chars)]
                styled_text = Text()
                styled_text.append(spinner, style=SPINNER_STYLE)
                styled_text.append(" ")
                styled_text.append(thinking_phrase, style=THINKING_STYLE)
                styled_text.append(f" ({elapsed_seconds}s)")
                live.update(styled_text)
        except Exception as e:
            console.print(f"[{ERROR_STYLE}]Error generating response: {str(e)}[/{ERROR_STYLE}]")
            return f"Error: {str(e)}"
    
    return full_response

async def main():
    """Runs the interactive LM Studio agent in a streaming conversation loop."""
    global conversation_history
    
    # Define available commands
    COMMANDS = {
        "help": "Display this list of available commands",
        "clear or reset": "Clear the conversation history",
        "save": "Save the current conversation to conversation_history.json",
        "load": "Load a previously saved conversation from conversation_history.json",
        "exit or quit": "Exit the program",
    }
    
    # File path for saving/loading conversation
    CONVERSATION_FILE = "conversation_history.json"
    
    try:
        try:
            response = await openai_client.models.list()
            if not response.data:
                console.print(Panel(f"[{ERROR_STYLE}]Error: No models available in LM Studio[/{ERROR_STYLE}]"))
                console.print(f"[{WARNING_STYLE}]Please ensure you have at least one model loaded in LM Studio[/{WARNING_STYLE}]")
                sys.exit(1)
                
            model_name = response.data[0].id
            agent = create_lm_agent()
            
            console.print(Panel(
                f"[{SYSTEM_STYLE}]LM Studio:[/{SYSTEM_STYLE}] [{INFO_STYLE}]Connected[/{INFO_STYLE}]\n"
                f"[{SYSTEM_STYLE}]Model:[/{SYSTEM_STYLE}] [{INFO_STYLE}]{model_name}[/{INFO_STYLE}]\n"
                f"[{SYSTEM_STYLE}]Settings:[/{SYSTEM_STYLE}] [{INFO_STYLE}]" + 
                f"Temperature: {API_TEMPERATURE}, " +
                f"Max Tokens: {API_MAX_TOKENS_INITIAL}/{API_MAX_TOKENS_FOLLOWUP}, " +
                f"Top-p: {API_TOP_P}, " +
                f"Freq Penalty: {API_FREQUENCY_PENALTY}, " +
                f"Pres Penalty: {API_PRESENCE_PENALTY}[/{INFO_STYLE}]",
                border_style="green"
            ))
            
            console.print(Panel(
                f"[{WELCOME_STYLE}]{WELCOME_MESSAGE}[/{WELCOME_STYLE}]\n\n"
                f"[{INFO_STYLE}]This agent has the following capabilities:[/{INFO_STYLE}]\n"
                f"• File operations (create, view, modify)\n"
                f"• Command execution\n"
                f"• [bold]Vision capabilities[/bold] (describe images)",
                border_style="magenta"
            ))
            
        except Exception as e:
            console.print(Panel(
                f"[{SYSTEM_STYLE}]LM Studio:[/{SYSTEM_STYLE}] [{ERROR_STYLE}]Disconnected[/{ERROR_STYLE}]\n"
                f"[{ERROR_STYLE}]Error: {str(e)}[/{ERROR_STYLE}]",
                border_style="red"
            ))
            console.print(f"[{WARNING_STYLE}]Please make sure LM Studio is running with the server enabled on port 1234[/{WARNING_STYLE}]")
            sys.exit(1)
        
        while True:
            try:
                console.print("\n> ", end="", style=USER_STYLE)
                user_input = await asyncio.to_thread(input, "")
                user_input = user_input.strip()
                
                # Check for help command
                if user_input.lower().startswith("help"):
                    console.print("\n[bold cyan]Available Commands:[/bold cyan]")
                    for cmd, desc in COMMANDS.items():
                        console.print(f"- [cyan]{cmd}[/cyan]: {desc}")
                    console.print("\n[bold]Note:[/bold] For tool usage, ask the assistant directly (e.g., 'create a file')")
                    continue
                
                # Check for save command
                if user_input.lower() == "save":
                    try:
                        with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
                            json.dump(conversation_history, f, indent=2)
                        console.print(f"[bold cyan]Conversation saved to {CONVERSATION_FILE}[/bold cyan]")
                    except Exception as e:
                        console.print(f"[{ERROR_STYLE}]Error saving conversation: {str(e)}[/{ERROR_STYLE}]")
                    continue
                
                # Check for load command
                if user_input.lower() == "load":
                    try:
                        if os.path.exists(CONVERSATION_FILE):
                            with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
                                loaded_history = json.load(f)
                            conversation_history = loaded_history
                            console.print(f"[bold cyan]Conversation loaded from {CONVERSATION_FILE}[/bold cyan]")
                        else:
                            console.print(f"[{WARNING_STYLE}]No saved conversation found at {CONVERSATION_FILE}[/{WARNING_STYLE}]")
                    except Exception as e:
                        console.print(f"[{ERROR_STYLE}]Error loading conversation: {str(e)}[/{ERROR_STYLE}]")
                    continue
                
                # Existing command checks
                if user_input.lower() in ["exit", "quit"]:
                    console.print("\nExiting...")
                    break
                elif user_input.lower() in ["clear", "reset"]:
                    conversation_history.clear()
                    console.print("[bold cyan]Conversation history cleared.[/bold cyan]")
                    continue
                
                full_response = await generate_response(user_input, agent, model_name)
                console.print("• ", end="", style=ASSISTANT_STYLE)
                console.print(full_response, style=ASSISTANT_STYLE)
                
            except Exception as e:
                console.print(Panel(f"[{ERROR_STYLE}]Error during conversation: {str(e)}[/{ERROR_STYLE}]"))
                break
    
    except KeyboardInterrupt:
        console.print("\nExiting...")
    except Exception as e:
        console.print(Panel(f"[{ERROR_STYLE}]Error: {str(e)}[/{ERROR_STYLE}]"))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())