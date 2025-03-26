# LM Studio Local Agents

## Project Summary

These agents demonstrate how to leverage local language models through LM Studio as alternatives to cloud-based AI services, providing a way to build interactive AI assistants that run entirely on your local machine.

## Installation

1. Clone or download this repository.
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) 
> UV is THE modern package manager for Python.

macos + linux
```bash
brew install uv
```

windows
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Ensure LM Studio Server is running with a loaded model.


## Usage

**Basic Agents:**
```bash
   uv run lm_studio_agent_simple_ui.py # - A simple implementation with basic UI formatting
```

**Advanced Agents:**
```bash
   uv run lm_studio_agent_enhanced_ui_tool_use.py # - Enhanced UI version with tool use capabilities
   uv run lm_studio_agent_clean_ui_bash_tool_use.py # - Version with bash and tool use support
   uv run lm_studio_agent_clean_ui_bash_tool_use_v2.py # - Version with improved bash and tool use support
   uv run lm_studio_agent_clean_ui_bash_tool_use_v3.py # - Version with additional improvements and stability enhancements
   uv run lm_studio_agent_clean_ui_bash_tool_use_v4.py # - Latest version with image description capabilities
```

**Image Description Utility:**
```bash
   uv run image_describe.py # - Standalone utility for testing image description with LM Studio
```

## Features

1. **Setup**:
   - Configures an `AsyncOpenAI` client to communicate with LM Studio at `http://localhost:1234/v1`.
   - Sets environment variables for the OpenAI API key (using a dummy key) and base URL.
   - Initializes a `rich` console for enhanced terminal output.
   - Defines tools for file and system operations

2. **Agent Creation**:
   - Defines a local agent (`LocalAssistant`) with customizable instructions to ensure helpful, accurate, and concise responses.
   - Supports structured answers, coding examples, and clear uncertainty statements when applicable.
   - Configures tools for file management and command execution

3. **Conversation Management**:
   - Type `help` to see a list of available commands and their descriptions.
   - Save and load conversation history to/from JSON files by typing `save` or `load`.
   - Clear the conversation history by typing `clear` or `reset`.
   - Exit the session by typing `exit` or `quit`.

4. **Conversation Loop**:
   - Checks if LM Studio is running and retrieves the first available model.
   - Displays connection status and model information in a styled panel.
   - Prompts the user for input with a styled prompt.
   - Streams the agent's response with proper styling.
   - Displays tool execution results when tools are used.
   - Handles interruptions (e.g., Ctrl+C) and errors gracefully.

5. **Tool Execution**:
   - Processes tool calls from the agent and executes the requested operations.
   - Available tools:
     - `create_file`: Create new files with specified content
     - `replace_text`: Replace text in existing files
     - `insert_line`: Insert a line at a specific position in a file
     - `view_file`: Display the contents of a file
     - `execute_command`: Execute system commands
     - `describe_image`: Analyze and describe the contents of an image file (v4 only)
   - Continues the conversation with follow-up responses after tool execution.

6. **File Operations**:
   - Supports creating, viewing, and modifying files with fuzzy file matching.
   - Handles file path resolution and directory creation.
   - Automatically checks current working directory when a file isn't found.
   - Provides detailed error messages for file operation failures.

7. **Image Processing** (v4 only):
   - Analyzes images using the vision capabilities of local LLMs in LM Studio.
   - Supports various image formats (JPEG, PNG).
   - Intelligently searches for image files in the current directory if not found at the specified path.
   - Prompts for the exact path if an image cannot be located.

## Example Interaction

LM Studio: Connected
Model: my-local-model
Settings: Temperature: 0.7, Max Tokens: 4096/1000

Available tools:
- create_file: Create a new file with the specified content
- replace_text: Replace text in a file
- insert_line: Insert a line at a specific position in a file
- execute_command: Execute a bash command
- view_file: View the contents of a file
- describe_image: Analyze and describe the contents of an image file (v4 only)

Master, would you like to code? You will be pleased.

> Can you create a simple Python hello world script for me?

• I'll create a simple Python hello world script for you.

[Using create_file...]
I've created a file named "hello_world.py" with a simple Hello World output. You can run it using the command "python hello_world.py".

## Testing

The project includes a test script to verify the functionality of the LM Studio agent implementation:

```bash
uv run pytest test_lm_studio_agent.py -v
```

The test script (`test_lm_studio_agent.py`) includes tests for:
- File operations (finding, creating, viewing, modifying files)
- Command execution
- Agent creation and configuration
- LM Studio connection (requires LM Studio running)
- Streaming response functionality (verifies that responses are properly streamed in chunks)
- Image description capabilities (v4 only, requires a model with vision capabilities)

The tests are designed to be modular:
- File operation and command execution tests run independently without requiring LM Studio
- LM Studio-dependent tests use a shared pytest fixture that checks connectivity once
- Tests automatically skip with informative messages if dependencies are not available

You can skip tests that require LM Studio by setting the environment variable `SKIP_LM_STUDIO_TESTS`.

## Documentation

- [OpenAI API Reference](https://platform.openai.com/docs/api-reference/introduction)
- [LM Studio OpenAI Compatibility API](https://lmstudio.ai/docs/app/api/endpoints/openai)
- [Astral UV Dependency Management](https://docs.astral.sh/uv/)