#!/usr/bin/env -S uv run --script

# /// script
# dependencies = [
#   "openai-agents>=0.0.6",
#   "rich>=13.9.4",
#   "openai>=1.68.2",
# ]
# ///

"""
LM Studio Local Agent Example with Streaming

This example demonstrates how to create an interactive agent using the OpenAI Agents SDK
with LM Studio as the backend. The agent responds to user queries in an ongoing conversation
with streaming output, using a local LLM model.

Run with:
    uv run lm_studio_basic_agent.py

Then, type your messages and press enter. Type 'exit' to quit.

Note: This script requires LM Studio to be running on http://localhost:1234/v1
"""

import os
import sys
from typing import Optional, AsyncGenerator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
import asyncio
from openai import AsyncOpenAI
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
SPINNER_STYLE = "bold cyan"  # New style for the spinner

# Define thinking phrases
THINKING_PHRASES = [
    "Pondering...",
    "Noodling...", 
    "Scheming...",
    "Conjuring....",
    "Executing..."
]

def create_lm_agent() -> Agent:
    """Creates an LM Studio agent using the default model from LM Studio."""
    instructions = """
    You are a helpful, accurate, and concise AI assistant.
    
    Respond to queries in a conversational, friendly tone while prioritizing factual information.
    Provide structured answers when appropriate.
    
    When you don't know something or aren't sure:
    - Clearly state your uncertainty
    - Avoid making up facts or speculating
    - Suggest related areas you can help with instead
    
    Keep responses focused and relevant to the user's question.
    When handling coding questions, include practical examples when helpful.
    
    For complex topics, break down your explanation into simpler parts.
    """
    return Agent(
        name="LocalAssistant",
        instructions=instructions,
        model="default",
    )

async def run_lm_agent(prompt: str, agent: Agent, model_name: str) -> AsyncGenerator[str, None]:
    """Streams an LM response for the given prompt using the provided agent."""
    global conversation_history
    
    # Add the user's message to the conversation history
    conversation_history.append({"role": "user", "content": prompt})
    
    # Check if conversation history is getting too long
    if len(conversation_history) > 20:  # Arbitrary limit, adjust as needed
        # Keep the most recent conversations
        conversation_history = conversation_history[-20:]
        console.print(f"[{WARNING_STYLE}]Conversation history trimmed to prevent token limit issues.[/{WARNING_STYLE}]")
    
    # Create messages array with system instructions and full conversation history
    messages = [{"role": "system", "content": agent.instructions}]
    messages.extend(conversation_history)
    
    try:
        stream = await openai_client.chat.completions.create(
            model=model_name,  # Use the provided model name instead of agent.model
            messages=messages,
            stream=True
        )
        
        assistant_response = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                assistant_response += content
                yield content
        
        # After streaming is complete, add the assistant's response to the conversation history
        conversation_history.append({"role": "assistant", "content": assistant_response})
    except Exception as e:
        console.print(f"[{ERROR_STYLE}]Error in API call: {str(e)}[/{ERROR_STYLE}]")
        yield f"Error: {str(e)}"

async def generate_response(prompt: str, agent: Agent, model_name: str):
    """Generates a full response while showing the thinking indicator."""
    full_response = ""
    start_time = time.time()
    
    # Select a random thinking phrase
    thinking_phrase = random.choice(THINKING_PHRASES)
    
    # Use Rich's Live display to show continuously updating content
    with Live("", refresh_per_second=16) as live:
        # Update elapsed time
        elapsed_seconds = int(time.time() - start_time)
        
        # Simple spinner animation using characters
        spinner_chars = "|/-\\"
        spinner = spinner_chars[elapsed_seconds % len(spinner_chars)]
        
        # Update the display with styled spinner and thinking phrase
        styled_text = Text()
        styled_text.append(spinner, style=SPINNER_STYLE)
        styled_text.append(" ")
        styled_text.append(thinking_phrase, style=THINKING_STYLE)
        styled_text.append(f" ({elapsed_seconds}s)")
        live.update(styled_text)
        
        try:
            async for chunk in run_lm_agent(prompt, agent, model_name):
                full_response += chunk
                # Continue updating the spinner and elapsed time
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
    
    try:
        # First check if LM Studio is available and get models
        try:
            response = await openai_client.models.list()
            if not response.data:
                console.print(Panel(f"[{ERROR_STYLE}]Error: No models available in LM Studio[/{ERROR_STYLE}]"))
                console.print(f"[{WARNING_STYLE}]Please ensure you have at least one model loaded in LM Studio[/{WARNING_STYLE}]")
                sys.exit(1)
                
            # Get the first model name
            model_name = response.data[0].id
            
            # Create the agent
            agent = create_lm_agent()
            
            # Display connection status and model name with requested formatting
            console.print(Panel(
                f"[{SYSTEM_STYLE}]LM Studio:[/{SYSTEM_STYLE}] [{INFO_STYLE}]Connected[/{INFO_STYLE}]\n"
                f"[{SYSTEM_STYLE}]Model:[/{SYSTEM_STYLE}] [{INFO_STYLE}]{model_name}[/{INFO_STYLE}]", 
                border_style="green"
            ))
        except Exception as e:
            console.print(Panel(
                f"[{SYSTEM_STYLE}]LM Studio:[/{SYSTEM_STYLE}] [{ERROR_STYLE}]Disconnected[/{ERROR_STYLE}]\n"
                f"[{ERROR_STYLE}]Error: {str(e)}[/{ERROR_STYLE}]",
                border_style="red"
            ))
            console.print(f"[{WARNING_STYLE}]Please make sure LM Studio is running with the server enabled on port 1234[/{WARNING_STYLE}]")
            sys.exit(1)
        
        # Start the interactive conversation loop
        while True:
            try:
                # Display user input prompt
                console.print("\n> ", end="", style=USER_STYLE)
                
                # Get user input asynchronously
                user_input = await asyncio.to_thread(input, "")
                user_input = user_input.strip()
                
                # Check for exit commands
                if user_input.lower() in ["exit", "quit"]:
                    console.print("\nExiting...")
                    break
                elif user_input.lower() in ["clear", "reset"]:
                    conversation_history.clear()  # Use clear() instead of reassigning
                    console.print("[bold cyan]Conversation history cleared.[/bold cyan]")
                    continue
                
                # Generate the full response first while showing thinking indicator
                full_response = await generate_response(user_input, agent, model_name)
                
                # Once done, display the bullet point and the full response
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
