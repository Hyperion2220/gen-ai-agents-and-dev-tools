#!/usr/bin/env -S uv run --script

# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "python-dotenv>=1.0.0",
#   "rich>=13.7.0",
# ]
# ///

"""
AI Agent using Claude 3.7 Sonnet with file manipulation and command execution tools.
"""
import os
import sys
import json
import time
import subprocess
from typing import Dict, List, Any, Optional, Callable
from dotenv import load_dotenv
import anthropic
from rich.console import Console
from rich.panel import Panel

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.expanduser("~"), ".env"))

# Get API key from environment
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print("Error: ANTHROPIC_API_KEY not found in environment variables.")
    sys.exit(1)

# Initialize Claude client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL = "claude-3-7-sonnet-20250219"

# Tool definitions
TOOLS = [
    {
        "name": "create_file",
        "description": "Create a new file with the specified content",
        "input_schema": {
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
    },
    {
        "name": "replace_text",
        "description": "Replace text in a file",
        "input_schema": {
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
    },
    {
        "name": "insert_line",
        "description": "Insert a line at a specific position in a file",
        "input_schema": {
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
    },
    {
        "name": "execute_command",
        "description": "Execute a bash command",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to execute"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "view_file",
        "description": "View the contents of a file",
        "input_schema": {
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
]

# Tool implementations
def create_file(file_path: str, content: str) -> Dict[str, Any]:
    """Create a new file with the specified content."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"File created at {file_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def replace_text(file_path: str, search_text: str, replace_text: str) -> Dict[str, Any]:
    """Replace text in a file."""
    try:
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if search_text not in content:
            return {"status": "error", "message": f"Text '{search_text}' not found in {file_path}"}

        new_content = content.replace(search_text, replace_text)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return {"status": "success", "message": f"Replaced '{search_text}' with '{replace_text}' in {file_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def insert_line(file_path: str, line_number: int, content: str) -> Dict[str, Any]:
    """Insert a line at a specific position in a file."""
    try:
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if line_number < 1 or line_number > len(lines) + 1:
            return {"status": "error", "message": f"Invalid line number: {line_number}. File has {len(lines)} lines."}

        lines.insert(line_number - 1, content if content.endswith('\n') else content + '\n')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return {"status": "success", "message": f"Inserted line at position {line_number} in {file_path}"}
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

        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def view_file(file_path: str) -> Dict[str, Any]:
    """View the contents of a file."""
    try:
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Token usage functions
def get_token_usage(response, response_time=None):
    """Extract token usage information from Claude API response."""
    output_tokens = response.usage.output_tokens
    
    # Calculate tokens per second if response_time is provided
    tokens_per_second = None
    if response_time is not None and response_time > 0:
        tokens_per_second = output_tokens / response_time
    
    return {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": output_tokens,
        "tokens_per_second": tokens_per_second,
        "total_tokens": response.usage.input_tokens + output_tokens
    }

def display_token_usage(console, usage):
    """Display token usage information in a compact horizontal format with a blue box."""
    # Format tokens per second if available
    tps_display = ""
    if usage.get("tokens_per_second") is not None:
        tps_display = f" | Speed: [bold red]{usage['tokens_per_second']:.2f} t/s[/bold red]"
    
    console.print(Panel(
        f"[green]Token Usage:[/green] Input: [bold cyan]{usage['input_tokens']:,}[/bold cyan] | "
        f"Output: [bold magenta]{usage['output_tokens']:,}[/bold magenta]"
        f"{tps_display} | "
        f"Total: [bold yellow]{usage['total_tokens']:,}[/bold yellow]",
        border_style="blue",
        expand=False
    ))

# Map tool names to their implementations
TOOL_MAP = {
    "create_file": create_file,
    "replace_text": replace_text,
    "insert_line": insert_line,
    "execute_command": execute_command,
    "view_file": view_file
}

def execute_tool_call(tool_call) -> Dict[str, Any]:
    """Execute a tool call and return the result."""
    try:
        tool_name = tool_call.name
        function_args = tool_call.input

        if not tool_name or tool_name not in TOOL_MAP:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}

        # Execute the tool
        result = TOOL_MAP[tool_name](**function_args)
        return result
    except Exception as e:
        return {"status": "error", "message": f"Error executing tool: {str(e)}"}

def run_agent():
    """Run the agent in an interactive loop."""
    console = Console()

    # Define the system prompt separately
    system_prompt = """You are an AI assistant with access to tools for file manipulation and command execution.
You can help users create, modify, and view files, as well as execute commands.
Always use the appropriate tool for the task at hand.
Be careful when executing commands that might modify the system.
Provide clear explanations of what you're doing and why.

IMPORTANT: When executing commands on Windows systems, use standard Windows Command Prompt commands:
- Use 'del' for deleting files (NOT 'rm' or 'Remove-Item')
- Use 'dir' for listing directory contents (NOT 'ls')
- Use 'copy' for copying files (NOT 'cp')
- Use 'move' for moving files (NOT 'mv')
- Use 'mkdir' for creating directories (NOT 'md')
- Use 'rmdir' for removing directories (NOT 'rd')
- Use 'type' for displaying file contents (NOT 'cat')
- Use 'echo' for printing text

These standard Windows commands work reliably in both Command Prompt and PowerShell environments.
Always adapt your command syntax to the operating system the user is running."""

    # Initialize messages without the system message
    messages = []

    console.print(Panel.fit("AI Agent initialized. Type 'exit' to quit.", title="Claude Agent", border_style="green"))
    console.print("\n[bold]Available tools:[/bold]")
    for tool in TOOLS:
        console.print(f"- [cyan]{tool['name']}[/cyan]: {tool['description']}")
    console.print()

    while True:
        user_input = console.input("[bold green]You:[/bold green] ")
        if user_input.lower() in ['exit', 'quit']:
            console.print("[yellow]Exiting agent.[/yellow]")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            with console.status("[bold blue]Thinking...[/bold blue]"):
                # Start timing the response
                start_time = time.time()
                response = client.messages.create(
                    model=MODEL,
                    system=system_prompt,  # Pass system prompt as a separate parameter
                    messages=messages,
                    tools=TOOLS,
                    max_tokens=4096
                )
                # Calculate response time
                response_time = time.time() - start_time

            # Get token usage from the response with timing information
            usage = get_token_usage(response, response_time)

            assistant_message = {"role": "assistant", "content": response.content[0].text}

            # Handle tool calls if present
            if hasattr(response, 'content') and response.content:
                # Check if any content block is a tool_use type
                has_tool_calls = any(
                    hasattr(content_item, 'type') and content_item.type == 'tool_use'
                    for content_item in response.content
                )

                if has_tool_calls:
                    # Extract text content (if any)
                    text_content = next((item.text for item in response.content
                                        if hasattr(item, 'type') and item.type == 'text'), "")

                    if text_content:
                        console.print(f"\n[bold purple]AI:[/bold purple] {text_content}")

                    # Create assistant content array more directly
                    assistant_content = []
                    for item in response.content:
                        if item.type == 'text':
                            assistant_content.append({"type": "text", "text": item.text})
                        elif item.type == 'tool_use':
                            assistant_content.append({
                                "type": "tool_use",
                                "id": item.id,
                                "name": item.name,
                                "input": item.input
                            })

                    # Add the assistant message with tool use to the conversation history
                    messages.append({"role": "assistant", "content": assistant_content})

                    # Extract and process tool calls
                    tool_calls = [item for item in response.content
                                if hasattr(item, 'type') and item.type == 'tool_use']

                    # Execute each tool call and add the results to the conversation
                    for tool_call in tool_calls:
                        tool_name = tool_call.name  # Access name directly on the tool_use block
                        console.print(f"\n[bold yellow]Executing tool:[/bold yellow] {tool_name}")
                        result = execute_tool_call(tool_call)

                        # Format the result for display
                        if result["status"] == "success":
                            if "content" in result:
                                console.print(Panel(result["content"], title="File Content", border_style="green"))
                            else:
                                console.print(f"\n[green]Result:[/green] {result.get('message', '')}")
                                if "stdout" in result and result["stdout"]:
                                    console.print(Panel(result["stdout"], title="Output", border_style="blue"))
                        else:
                            console.print(f"\n[red]Error:[/red] {result.get('message', '')}")
                            if "stderr" in result and result["stderr"]:
                                console.print(Panel(result["stderr"], title="Error Output", border_style="red"))

                        # Add tool result to messages as a user message with tool_result content
                        messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": tool_call.id,
                                "content": json.dumps(result)
                            }]
                        })

                    # Get a follow-up response from the assistant
                    with console.status("[bold blue]Getting follow-up...[/bold blue]"):
                        # Start timing the follow-up response
                        follow_up_start_time = time.time()
                        follow_up = client.messages.create(
                            model=MODEL,
                            system=system_prompt,  # Pass system prompt as a separate parameter
                            messages=messages,
                            tools=TOOLS,
                            max_tokens=4096
                        )
                        # Calculate follow-up response time
                        follow_up_response_time = time.time() - follow_up_start_time

                    # Get token usage from the follow-up response with timing information
                    follow_up_usage = get_token_usage(follow_up, follow_up_response_time)

                    # Extract text from the follow-up response
                    follow_up_text = next((item.text for item in follow_up.content
                                        if hasattr(item, 'type') and item.type == 'text'), "")

                    # Create a simple text-only assistant message for the follow-up
                    assistant_message = {"role": "assistant", "content": follow_up_text}
                    messages.append(assistant_message)
                    console.print(f"\n[bold purple]AI:[/bold purple] {follow_up_text}")

                    # Display combined token usage
                    total_output_tokens = usage["output_tokens"] + follow_up_usage["output_tokens"]
                    total_response_time = (response_time if response_time else 0) + (follow_up_response_time if follow_up_response_time else 0)
                    
                    # Calculate combined tokens per second
                    total_tokens_per_second = None
                    if total_response_time > 0:
                        total_tokens_per_second = total_output_tokens / total_response_time
                    
                    total_usage = {
                        "input_tokens": usage["input_tokens"] + follow_up_usage["input_tokens"],
                        "output_tokens": total_output_tokens,
                        "tokens_per_second": total_tokens_per_second,
                        "total_tokens": usage["total_tokens"] + follow_up_usage["total_tokens"]
                    }
                    display_token_usage(console, total_usage)
                else:
                    # No tool calls, just regular text response
                    text_content = next((item.text for item in response.content
                                        if hasattr(item, 'type') and item.type == 'text'), "")

                    assistant_message = {"role": "assistant", "content": text_content}
                    messages.append(assistant_message)
                    console.print(f"\n[bold purple]AI:[/bold purple] {text_content}")

                    # Display token usage
                    display_token_usage(console, usage)

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    run_agent()