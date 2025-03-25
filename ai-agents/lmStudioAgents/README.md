Below is a README for the provided Python script that outlines its features, functionality, and usage instructions.

---

# LM Studio Local Agent Example with Streaming and Tools

## Project Summary

This repository contains a collection of Python scripts that implement AI agents for interfacing with local language models running in LM Studio. The scripts demonstrate different approaches and features for building interactive conversational agents:

1. **Basic Implementation Files:**
   - `lm_studio_agent_simple_ui.py` - A simple implementation with basic UI formatting

2. **Advanced Implementation Files:**
   - `lm_studio_agent_enhanced_ui_tool_use.py` - Enhanced UI version with tool use capabilities
   - `lm_studio_agent_clean_ui_bash_tool_use.py` - Version with bash and tool use support
   - `lm_studio_agent_clean_ui_bash_tool_use_v2.py` - Latest version with improved bash and tool use support

These agents demonstrate how to leverage local language models through LM Studio as alternatives to cloud-based AI services, providing a way to build interactive AI assistants that run entirely on your local machine.

### Run Commands

To run each version of the agent, use the following commands:

```bash
# Basic implementations
uv run lm_studio_agent_simple_ui.py

# Advanced implementations
uv run lm_studio_agent_enhanced_ui_tool_use.py
uv run lm_studio_agent_clean_ui_bash_tool_use.py
uv run lm_studio_agent_clean_ui_bash_tool_use_v2.py
```

Make sure LM Studio is running with at least one model loaded before executing any of these commands.

## Features

- **Interactive Chat Interface**: Engage in a continuous conversation with a local AI assistant by typing messages and receiving streaming responses in real-time. The agent maintains conversation history, allowing for contextual follow-up questions.
- **Streaming Output**: Responses from the agent are streamed character-by-character, providing a smooth and dynamic user experience.
- **Rich Terminal Formatting**: Utilizes the `rich` library to display styled text, including colored prompts, status panels, and error messages that work well across platforms (e.g., Windows terminals).
- **Local LLM Integration**: Connects to LM Studio running on `http://localhost:1234/v1` to use a locally hosted language model, avoiding reliance on external APIs.
- **Error Handling**: Gracefully handles connection issues, missing models, rate limits, and runtime errors with informative messages.
- **Customizable Agent Instructions**: The agent's behavior is defined by concise, friendly, and factual instructions, which can be modified as needed.
- **Model Detection**: Automatically detects and uses the first available model from LM Studio, with feedback on the connection status and model name.
- **Conversation Commands**: Type `exit` or `quit` to cleanly terminate the conversation loop. Use `clear` or `reset` to start a fresh conversation while keeping the connection active.
- **Response Control**: Configurable temperature (0.7) and maximum token limit settings with separate values for initial (4096) and follow-up (1000) responses.
- **Timeout Protection**: Configurable timeout settings with separate values for initial (30-second) and follow-up responses.
- **Clean Tool Result Display**: Tools execute with minimal notifications that don't overwhelm the user with raw data, showing only "[Using tool_name...]" indicators when tools are used.
- **Enhanced Response Format Instructions**: The agent is specifically instructed to use tools internally and provide concise natural language answers rather than writing code that simulates tool functionality.
- **Customizable Welcome Message**: Displays a configurable welcome message that can be easily modified through constants at the top of the file.
- **Higher Token Limits**: Increased maximum token limit to 4096 for initial responses, allowing for more complex reasoning and longer conversations.
- **Token Usage Management**: The "clear" command resets the conversation history, effectively freeing up the token usage back to baseline.
- **Visual Style Customization**: Colors and styles are defined as constants at the top of the file for easy customization of the interface appearance.
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
Settings: Temperature: 0.7, Max Tokens: 4096/1000

Available tools:
- create_file: Create a new file with the specified content
- replace_text: Replace text in a file
- insert_line: Insert a line at a specific position in a file
- execute_command: Execute a bash command
- view_file: View the contents of a file

Master, would you like to code? You will be pleased.

> Can you create a simple Python hello world script for me?
• I'll create a simple Python hello world script for you.

[Using create_file...]

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
- API parameters like temperature, max tokens, and timeouts can be easily configured by modifying the constants at the top of the file.
- The welcome message displayed on startup can be customized by changing the `WELCOME_MESSAGE` constant.
- The visual styles and colors used throughout the interface can be modified by changing the style constants.
- This is an example implementation—feel free to extend the agent's instructions or functionality for your use case.
- By default, the agent is configured for Windows command execution; this can be modified in the agent instructions.

## License

This project is provided as-is for educational purposes. No specific license is applied.

---

Let me know if you'd like to adjust or expand this README further!
