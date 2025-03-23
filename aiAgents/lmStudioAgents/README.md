Below is a README for the provided Python script that outlines its features, functionality, and usage instructions.

---

# LM Studio Local Agent Example with Streaming

This repository contains a Python script demonstrating how to create an interactive AI agent using the OpenAI Agents SDK with LM Studio as the local backend. The agent leverages a local large language model (LLM) running in LM Studio, providing streaming responses to user queries in an ongoing, interactive conversation.

## Features

- **Interactive Chat Interface**: Engage in a continuous conversation with a local AI assistant by typing messages and receiving streaming responses in real-time.
- **Streaming Output**: Responses from the agent are streamed character-by-character, providing a smooth and dynamic user experience.
- **Rich Terminal Formatting**: Utilizes the `rich` library to display styled text, including colored prompts, status panels, and error messages that work well across platforms (e.g., Windows terminals).
- **Local LLM Integration**: Connects to LM Studio running on `http://localhost:1234/v1` to use a locally hosted language model, avoiding reliance on external APIs.
- **Error Handling**: Gracefully handles connection issues, missing models, and runtime errors with informative messages.
- **Customizable Agent Instructions**: The agent's behavior is defined by concise, friendly, and factual instructions, which can be modified as needed.
- **Model Detection**: Automatically detects and uses the first available model from LM Studio, with feedback on the connection status and model name.
- **Exit Commands**: Type `exit` or `quit` to cleanly terminate the conversation loop.

## Functionality

The script performs the following:

1. **Setup**:
   - Configures an `AsyncOpenAI` client to communicate with LM Studio at `http://localhost:1234/v1`.
   - Sets environment variables for the OpenAI API key (using a dummy key) and base URL.
   - Initializes a `rich` console for enhanced terminal output.

2. **Agent Creation**:
   - Defines a local agent (`LocalAssistant`) with customizable instructions to ensure helpful, accurate, and concise responses.
   - Supports structured answers, coding examples, and clear uncertainty statements when applicable.

3. **Conversation Loop**:
   - Checks if LM Studio is running and retrieves the first available model.
   - Displays connection status and model information in a styled panel.
   - Prompts the user for input with a magenta "You: " label.
   - Streams the agent's response with a green "Assistant: " label.
   - Handles interruptions (e.g., Ctrl+C) and errors gracefully.

4. **Streaming Responses**:
   - Uses asynchronous streaming to fetch and display the agent's responses incrementally, enhancing interactivity.

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
   uv run lm_studio_basic_agent.py
   ```
2. Once started, the script will:
   - Confirm the connection to LM Studio and display the active model.
   - Prompt you to type a message.

3. Interact with the agent:
   - Type your query and press Enter.
   - Watch the agent's response stream in real-time.
   - Type `exit` or `quit` to end the session.

## Example Interaction

```
LM Studio: Connected
Model: my-local-model

You: What is Python?
Assistant: Python is a high-level, interpreted programming language known for its readability and versatility. It’s widely used in web development, data science, automation, and more. Would you like an example of a simple Python script?
```

## Troubleshooting

- **"No models available"**: Ensure LM Studio is running and a model is loaded.
- **"Disconnected" error**: Verify LM Studio is active on `http://localhost:1234/v1`.
- **Dependency issues**: Confirm all required packages are installed correctly.

## Notes

- The script assumes LM Studio is configured with its default server settings.
- The agent uses the first model listed by LM Studio; modify `model_name` in the code if you need a specific model.
- This is an example implementation—feel free to extend the agent's instructions or functionality for your use case.

## License

This project is provided as-is for educational purposes. No specific license is applied.

---

Let me know if you'd like to adjust or expand this README further!