#!/usr/bin/env -S uv run --script

# /// script
# dependencies = [
#   "openai-agents>=0.0.6",
#   "rich>=13.9.4",
#   "openai>=1.68.2",
#   "pydantic>=2.6.3",
# ]
# ///

"""
LM Studio Local Agent Example with Streaming

This example demonstrates how to create an interactive agent using the OpenAI Agents SDK
with LM Studio as the backend. The agent responds to user queries in an ongoing conversation
with streaming output, using a local LLM model.

Run with:
    uv run lm_studio_agent.py

Then, type your messages and press enter. Type 'exit' to quit.

Note: This script requires LM Studio to be running on http://localhost:1234/v1
"""

import os
import sys
from typing import Optional, AsyncGenerator, Dict, Any, List, Callable, Union
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
from pydantic import BaseModel, Field, SecretStr, ConfigDict, model_validator
from datetime import datetime

# Initialize console for rich output
console = Console()

# Pydantic models for configuration and data structures
class LMStudioSettings(BaseModel):
    """Configuration settings for LM Studio"""
    base_url: str = Field("http://localhost:1234/v1", description="LM Studio API base URL")
    api_key: str = Field("dummy-key", description="API key (dummy for LM Studio)")
    model_name: Optional[str] = Field(None, description="Default model name to use")
    
    @model_validator(mode="after")
    def set_env_vars(self) -> "LMStudioSettings":
        """Set environment variables based on settings"""
        os.environ["OPENAI_API_KEY"] = self.api_key
        os.environ["OPENAI_API_BASE"] = self.base_url
        return self

class StyleConfig(BaseModel):
    """Configuration for terminal output styles"""
    user: str = Field("bold magenta", description="Style for user text")
    assistant: str = Field("white", description="Style for assistant responses")
    error: str = Field("bold red", description="Style for error messages")
    info: str = Field("bold white", description="Style for information messages")
    warning: str = Field("yellow", description="Style for warning messages")
    system: str = Field("bold cyan", description="Style for system messages")
    thinking: str = Field("bold cyan", description="Style for thinking messages")
    spinner: str = Field("bold cyan", description="Style for the spinner animation")

class OpenAIModel(BaseModel):
    """OpenAI model information"""
    id: str = Field(..., description="Model identifier")
    created: Optional[int] = Field(None, description="Creation timestamp")
    object: Optional[str] = Field(None, description="Object type")
    owned_by: Optional[str] = Field(None, description="Model owner")

class OpenAIModelList(BaseModel):
    """List of OpenAI models"""
    object: str = Field(..., description="Object type")
    data: List[OpenAIModel] = Field(..., description="List of available models")

# Base class for tool parameters
class ToolParams(BaseModel):
    """Base class for all tool parameters"""
    model_config = ConfigDict(extra="forbid")

# Example tool parameter classes (can be expanded as you add tools)
class ExecuteCommandParams(ToolParams):
    """Parameters for executing a shell command"""
    command: str = Field(..., description="The command to execute")
    
class FileReadParams(ToolParams):
    """Parameters for reading a file"""
    file_path: str = Field(..., description="Path to the file to read")

# Define structured response types
class CommandResult(BaseModel):
    """Result from executing a command"""
    status: str = Field(..., description="Status of the command execution (success/error)")
    stdout: str = Field("", description="Standard output from the command")
    stderr: str = Field("", description="Standard error from the command")
    returncode: int = Field(0, description="Return code from the command")
    message: Optional[str] = Field(None, description="Additional message if applicable")

class FileContentResult(BaseModel):
    """Result from reading a file"""
    status: str = Field(..., description="Status of the file operation (success/error)")
    content: Optional[str] = Field(None, description="Content of the file if successful")
    message: Optional[str] = Field(None, description="Error message if applicable")
    file_path: Optional[str] = Field(None, description="Path to the file that was read")

# RunContext for dependency injection in system prompts and tools
class RunContext(BaseModel):
    """Context for a single agent run with typed dependencies"""
    deps: Any = Field(None, description="Dependencies for this run")
    retry: int = Field(0, description="Current retry count")

# Create config instances
settings = LMStudioSettings()
styles = StyleConfig()

# Create AsyncOpenAI client configured for LM Studio
openai_client = AsyncOpenAI(
    base_url=settings.base_url,
    api_key=settings.api_key
)

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

class LMAgent:
    """LM Studio Agent with Pydantic-style system prompts"""
    
    def __init__(
        self, 
        name: str = "LocalAssistant",
        system_prompt: Optional[str] = None,
        deps_type: Any = None,
        model: str = "default"
    ):
        self.name = name
        self.static_system_prompt = system_prompt
        self.dynamic_system_prompts = []
        self.deps_type = deps_type
        self.model = model
        self.tools = []
        
    def system_prompt(self, func: Callable) -> Callable:
        """Decorator to add a dynamic system prompt function"""
        self.dynamic_system_prompts.append(func)
        return func
        
    def tool(self, func: Callable) -> Callable:
        """Decorator to add a tool that requires context"""
        self.tools.append(func)
        return func
        
    def tool_plain(self, func: Callable) -> Callable:
        """Decorator to add a tool that doesn't require context"""
        self.tools.append(func)
        return func
        
    def get_full_system_prompt(self, ctx: Optional[RunContext] = None) -> str:
        """Generate the complete system prompt by combining static and dynamic prompts"""
        prompts = []
        
        # Add static system prompt if provided
        if self.static_system_prompt:
            prompts.append(self.static_system_prompt)
            
        # Add all dynamic system prompts
        for prompt_func in self.dynamic_system_prompts:
            if 'ctx' in prompt_func.__code__.co_varnames:
                # Function expects context
                if ctx is not None:
                    prompts.append(prompt_func(ctx))
                else:
                    # Create empty context if needed
                    empty_ctx = RunContext()
                    prompts.append(prompt_func(empty_ctx))
            else:
                # Function doesn't need context
                prompts.append(prompt_func())
                
        return "\n\n".join(prompts)
    
    def create_agent(self) -> Agent:
        """Creates an OpenAI Agents SDK agent with the current system prompt"""
        return Agent(
            name=self.name,
            instructions=self.get_full_system_prompt(),
            model=self.model,
        )

# Create the LM agent with base system prompt
lm_agent = LMAgent(
    name="LocalAssistant",
    system_prompt="""
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
)

# Add dynamic system prompts
@lm_agent.system_prompt
def add_greeting_style() -> str:
    """Add a specific greeting style to the system prompt"""
    return "Be helpful and concise when responding to user questions."

async def run_lm_agent(prompt: str, agent: Agent, model_name: str) -> AsyncGenerator[str, None]:
    """Streams an LM response for the given prompt using the provided agent."""
    stream = await openai_client.chat.completions.create(
        model=model_name,  # Use the provided model name instead of agent.model
        messages=[
            {"role": "system", "content": agent.instructions},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

async def generate_response(prompt: str, agent: Agent, model_name: str):
    """Generates a full response while showing the thinking indicator."""
    full_response = ""
    start_time = time.time()
    
    # Select a random thinking phrase
    thinking_phrase = random.choice(THINKING_PHRASES)
    
    # Use Rich's Live display to show continuously updating content
    with Live("", refresh_per_second=16) as live:
        while not full_response.endswith("\n\n") and len(full_response) < 2:
            # Update elapsed time
            elapsed_seconds = int(time.time() - start_time)
            
            # Simple spinner animation using characters
            spinner_chars = "|/-\\"
            spinner = spinner_chars[elapsed_seconds % len(spinner_chars)]
            
            # Update the display with styled spinner and thinking phrase
            styled_text = Text()
            styled_text.append(spinner, style=styles.spinner)
            styled_text.append(" ")
            styled_text.append(thinking_phrase, style=styles.thinking)
            styled_text.append(f" ({elapsed_seconds}s)")
            live.update(styled_text)
            
            # Add a small delay for the animation
            await asyncio.sleep(0.05)
            
            # Try to collect response chunks
            try:
                async for chunk in run_lm_agent(prompt, agent, model_name):
                    full_response += chunk
                    # Continue updating the spinner and elapsed time
                    elapsed_seconds = int(time.time() - start_time)
                    spinner = spinner_chars[elapsed_seconds % len(spinner_chars)]
                    styled_text = Text()
                    styled_text.append(spinner, style=styles.spinner)
                    styled_text.append(" ")
                    styled_text.append(thinking_phrase, style=styles.thinking)
                    styled_text.append(f" ({elapsed_seconds}s)")
                    live.update(styled_text)
            except Exception:
                # If there's an error collecting chunks, we'll continue showing the animation
                # until we get a meaningful response
                pass
    
    return full_response

# Example tool implementation functions as decorated methods
@lm_agent.tool_plain
async def execute_command(params: ExecuteCommandParams) -> CommandResult:
    """Execute a shell command and return the result with stdout and stderr"""
    try:
        process = await asyncio.create_subprocess_shell(
            params.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        return CommandResult(
            status="success" if process.returncode == 0 else "error",
            stdout=stdout.decode(),
            stderr=stderr.decode(),
            returncode=process.returncode
        )
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e),
            returncode=-1,
            message=f"Exception during execution: {str(e)}"
        )

@lm_agent.tool_plain
async def read_file(params: FileReadParams) -> FileContentResult:
    """Read a file and return its contents with proper error handling"""
    try:
        if not os.path.exists(params.file_path):
            return FileContentResult(
                status="error", 
                message=f"File not found: {params.file_path}"
            )
            
        async with asyncio.TaskGroup() as tg:
            task = tg.create_task(asyncio.to_thread(
                lambda: open(params.file_path, "r").read()
            ))
        
        file_content = task.result()
        return FileContentResult(
            status="success",
            content=file_content,
            file_path=params.file_path
        )
    except Exception as e:
        return FileContentResult(
            status="error",
            message=f"Error reading file: {str(e)}"
        )

async def main():
    """Runs the interactive LM Studio agent in a streaming conversation loop."""
    try:
        # First check if LM Studio is available and get models
        try:
            response = await openai_client.models.list()
            
            # Parse response with Pydantic model
            model_list = OpenAIModelList(object=response.object, data=[
                OpenAIModel(id=model.id, created=model.created, object=model.object, owned_by=model.owned_by)
                for model in response.data
            ])
            
            if not model_list.data:
                console.print(Panel(f"[{styles.error}]Error: No models available in LM Studio[/{styles.error}]"))
                console.print(f"[{styles.warning}]Please ensure you have at least one model loaded in LM Studio[/{styles.warning}]")
                sys.exit(1)
                
            # Get the first model name
            model_name = model_list.data[0].id
            
            # Update settings with the detected model
            settings.model_name = model_name
            
            # Create the agent
            agent = lm_agent.create_agent()
            
            # Display connection status and model name with requested formatting
            console.print(Panel(
                f"[{styles.system}]LM Studio:[/{styles.system}] [{styles.info}]Connected[/{styles.info}]\n"
                f"[{styles.system}]Model:[/{styles.system}] [{styles.info}]{model_name}[/{styles.info}]", 
                border_style="green"
            ))
            
            # Display the startup greeting
            console.print("\n• ", end="", style=styles.assistant)
            console.print("Master, would you like to code? You will be pleased.", style=styles.assistant)
            
        except Exception as e:
            console.print(Panel(
                f"[{styles.system}]LM Studio:[/{styles.system}] [{styles.error}]Disconnected[/{styles.error}]\n"
                f"[{styles.error}]Error: {str(e)}[/{styles.error}]",
                border_style="red"
            ))
            console.print(f"[{styles.warning}]Please make sure LM Studio is running with the server enabled on port 1234[/{styles.warning}]")
            sys.exit(1)
        
        # Start the interactive conversation loop
        while True:
            try:
                # Display user input prompt
                console.print("\n> ", end="", style=styles.user)
                
                # Get user input asynchronously
                user_input = await asyncio.to_thread(input, "")
                user_input = user_input.strip()
                
                # Check for exit commands
                if user_input.lower() in ["exit", "quit"]:
                    console.print("\nExiting...")
                    break
                
                # Generate the full response first while showing thinking indicator
                full_response = await generate_response(user_input, agent, model_name)
                
                # Once done, display the bullet point and the full response
                console.print("• ", end="", style=styles.assistant)
                console.print(full_response, style=styles.assistant)
                
            except Exception as e:
                console.print(Panel(f"[{styles.error}]Error during conversation: {str(e)}[/{styles.error}]"))
                break
    
    except KeyboardInterrupt:
        console.print("\nExiting...")
    except Exception as e:
        console.print(Panel(f"[{styles.error}]Error: {str(e)}[/{styles.error}]"))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())