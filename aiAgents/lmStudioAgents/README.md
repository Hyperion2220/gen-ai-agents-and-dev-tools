Below is a README for the provided Python script that outlines its features, functionality, and usage instructions.

---

# LM Studio Local Agent Example with Streaming and Tools

This repository contains a Python script demonstrating how to create an interactive AI agent using the OpenAI Agents SDK with LM Studio as the local backend. The agent leverages a local large language model (LLM) running in LM Studio, providing streaming responses to user queries in an ongoing, interactive conversation with file manipulation and command execution capabilities.

## Features

- **Interactive Chat Interface**: Engage in a continuous conversation with a local AI assistant by typing messages and receiving streaming responses in real-time. The agent maintains conversation history, allowing for contextual follow-up questions.
- **Streaming Output**: Responses from the agent are streamed character-by-character, providing a smooth and dynamic user experience.
- **Rich Terminal Formatting**: Utilizes the `rich` library to display styled text, including colored prompts, status panels, and error messages that work well across platforms (e.g., Windows terminals).
- **Local LLM Integration**: Connects to LM Studio running on `http://localhost:1234/v1` to use a locally hosted language model, avoiding reliance on external APIs.
- **Error Handling**: Gracefully handles connection issues, missing models, rate limits, and runtime errors with informative messages.
- **Customizable Agent Instructions**: The agent's behavior is defined by concise, friendly, and factual instructions, which can be modified as needed.
- **Model Detection**: Automatically detects and uses the first available model from LM Studio, with feedback on the connection status and model name.
- **Conversation Commands**: Type `exit` or `quit` to cleanly terminate the conversation loop. Use `clear` or `reset` to start a fresh conversation while keeping the connection active.
- **Response Control**: Configurable temperature (0.7) and maximum token limit (1000) to control response randomness and length.
- **Timeout Protection**: Built-in 30-second timeout to prevent hanging on slow responses.
- **Tool Functionality**: Includes tools for file manipulation and command execution:
  - `create_file`: Create new files with specified content
  - `replace_text`: Replace text in existing files
  - `insert_line`: Insert a line at a specific position in a file
  - `view_file`: Display the contents of a file
  - `execute_command`: Execute system commands
- **Fuzzy File Matching**: Intelligently finds files with similar names when exact matches are not found
- **Conversation Management**: Save and load conversation history to/from JSON files
- **Visual Thinking Indicators**: Shows animated "thinking" indicators with random phrases during processing
- **Help Command**: Type `help` to see a list of available commands and their descriptions
- **Windows Command Support**: Uses Windows-friendly commands by default when executing system commands

## Functionality

The script performs the following:

1. **Setup**:
   - Configures an `AsyncOpenAI` client to communicate with LM Studio at `http://localhost:1234/v1`.
   - Sets environment variables for the OpenAI API key (using a dummy key) and base URL.
   - Initializes a `rich` console for enhanced terminal output.
   - Defines tools for file and system operations

2. **Agent Creation**:
   - Defines a local agent (`LocalAssistant`) with customizable instructions to ensure helpful, accurate, and concise responses.
   - Supports structured answers, coding examples, and clear uncertainty statements when applicable.
   - Configures tools for file management and command execution

3. **Conversation Loop**:
   - Checks if LM Studio is running and retrieves the first available model.
   - Displays connection status and model information in a styled panel.
   - Prompts the user for input with a styled prompt.
   - Processes commands like `help`, `save`, `load`, `clear`, `reset`, `exit`, and `quit`.
   - Streams the agent's response with proper styling.
   - Displays tool execution results when tools are used.
   - Handles interruptions (e.g., Ctrl+C) and errors gracefully.

4. **Tool Execution**:
   - Processes tool calls from the agent and executes the requested operations.
   - Provides feedback on tool execution status and results.
   - Continues the conversation with follow-up responses after tool execution.

5. **File Operations**:
   - Supports creating, viewing, and modifying files with fuzzy file matching.
   - Handles file path resolution and directory creation.
   - Provides detailed error messages for file operation failures.

## Prerequisites

- **LM Studio**: Must be installed and running locally with the server enabled on `http://localhost:1234/v1`. Ensure at least one model is loaded.
- **Python**: Version 3.8 or higher.
- **Dependencies**: Install via `uv` (a Python package manager) or manually with `pip`. Required packages:
  - `openai-agents>=0.0.6`
  - `rich>=13.9.4`
  - `openai>=1.68.2`

## Installation

1. Clone or download this repository.
2. Ensure LM Studio is running with a loaded model.
3. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
## Usage

1. Run the script using `uv`:
   ```bash
   uv run lm_studio_agent_bash_and_tool_use.py
   ```
2. Once started, the script will:
   - Confirm the connection to LM Studio and display the active model.
   - Display available tools.
   - Prompt you to type a message.

3. Interact with the agent:
   - Type your query and press Enter.
   - Watch the agent's response stream in real-time.
   - Use available commands:
     - Type `help` to see a list of available commands.
     - Type `exit` or `quit` to end the session.
     - Type `clear` or `reset` to start a new conversation.
     - Type `save` to save the current conversation to a file.
     - Type `load` to load a previously saved conversation.
   - Request file operations or command execution in natural language.

## Example Interaction

```
LM Studio: Connected
Model: my-local-model
Settings: Temperature: 0.7, Max Tokens: 1000

Available tools:
- create_file: Create a new file with the specified content
- replace_text: Replace text in a file
- insert_line: Insert a line at a specific position in a file
- execute_command: Execute a bash command
- view_file: View the contents of a file

> Can you create a simple Python hello world script for me?
• I'll create a simple Python hello world script for you.

Calling tool: create_file
Tool result: {
  "status": "success",
  "message": "File created at hello_world.py",
  "content": "print(\"Hello, World!\")"
}

I've created a file named "hello_world.py" with a simple Hello World program. You can run it using the command "python hello_world.py" to see the output.
```

## Troubleshooting

- **"No models available"**: Ensure LM Studio is running and a model is loaded.
- **"Disconnected" error**: Verify LM Studio is active on `http://localhost:1234/v1`.
- **Dependency issues**: Confirm all required packages are installed correctly.
- **File operation errors**: Check file paths and permissions if file operations fail.
- **Command execution issues**: Ensure commands are compatible with your operating system.

## Notes

- The script assumes LM Studio is configured with its default server settings.
- The agent uses the first model listed by LM Studio; modify `model_name` in the code if you need a specific model.
- This is an example implementation—feel free to extend the agent's instructions or functionality for your use case.
- By default, the agent is configured for Windows command execution; this can be modified in the agent instructions.

## License

This project is provided as-is for educational purposes. No specific license is applied.

---

Let me know if you'd like to adjust or expand this README further!
