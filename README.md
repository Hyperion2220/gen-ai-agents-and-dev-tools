# Gen AI Agent Dev Tools and Helper Docs

The purpose of this repo is to collect tools and helper docs I've created.  The goal is to save time by documenting proven and useful patterns.  Additionally I want to have a collection of dev tools to effectively create gen ai agents with ease. 

## Table of Contents

Docker Deployments:
- [Run OpenWeb UI & Ollama Locally with Docker Desktop](open-webui-ollama-docker.md)
- [Run Fooocus Locally with Docker Desktop](Fooocus.md)

Ubuntu Deployments:
- [Run OpenWeb UI & Ollama Locally with Ubuntu](open-webui-ollama.md)

Windows Deployments:  
- [How to Install ComfyUI & Manager on Windows 11](how-to-install-comfyui-and-manager-windows.md)

Gen AI Agents & Dev Tools:
- [How to Effectively use LLMs for Coding](how-to-effectively-use-llms-for-coding.md)
- [Web Shark - Crawl and extract websites and API documentation for LLM context](https://github.com/Hyperion2220/webShark/blob/main/README.md)

Gen AI Agent Workflow (high level):
Idea Honing
- Use a local (free) LLM model to iterate on an idea and output a developer-ready specification in spec.md file.
- The spec.md file should contain a list of all high level dependancies such as Astral UV, Pydantic, LangGraph, Bedrock Converse API, etc.

Planning
- Use a local (free) reasoning LLM model to create a step-by-step blueprint in LLM prompt format. Output to a prompt_plan.md file.
- Use a local (free) reasoning LLM model to create a todo.md. The execution LLM can check off the todo.md while processing. This is good for keeping state across sessions.
- Use Web Shark to scrape and gather all the required code and API documentation for the LLM to referenece (prevents online misinformation and code hallucination).
- Use Repomix to consolodate all code examples (other AI Bots with features or tools you want to incorpoate, for example) and scraped API documentation.  This creates a single .xml file that's ideal for the LLM to add to context.

Execution
- Use a local (free) reasoning LLM model to create a step-by-step blueprint in LLM prompt format and output to a prompt_plan.md file.



## License

This project is open source and available under the [License](license.md). Feel free to use it in your projects, but please adhere to its terms.
