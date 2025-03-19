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
- [Web Shark - Crawl and extract websites and API documentation for LLM context](https://github.com/Hyperion2220/webShark/blob/main/README.md)
- [Repomix - Pack your codebase into AI-friendly formats](https://repomix.com)

Gen AI Agent Workflow:
Idea Honing
- Use a local (free) LLM model to iterate on an idea and output a developer-ready specification in spec.md file.
```
Ask me one question at a time so we can develop a thorough, step-by-step spec for this idea.
Each question should build on my previous answers, and our end goal is to have a detailed specification I can hand off to a developer.
Let’s do this iteratively and dig into every relevant detail. Remember, only one question at a time.
Here is the <IDEA>
```
- At the end of the idea honing process, ask the LLM to output to a spec.md file.  This should contain a list of all high level dependancies such as Astral UV, Pydantic, LangGraph, Bedrock Converse API, etc.
```
Now that we’ve wrapped up the brainstorming process, can you compile our findings into a comprehensive, developer-ready specification?
Include all relevant requirements, architecture choices, data handling details, error handling strategies, and a testing plan so a developer can immediately begin implementation and output in markdown format.
```

Planning
- Use a local (free) reasoning LLM model to create a step-by-step blueprint in LLM prompt format. Output to a prompt_plan.md file.
```
Draft a detailed, step-by-step blueprint for building this project. Then, once you have a solid plan, break it down into small, iterative chunks that build on each other.
Look at these chunks and then go another round to break it into small steps. review the results and make sure that the steps are small enough to be implemented safely, but big enough to move the project forward.
Iterate until you feel that the steps are right sized for this project.

From here you should have the foundation to provide a series of prompts for a code-generation LLM that will implement each step.
Prioritize best practices, and incremental progress, ensuring no big jumps in complexity at any stage. Make sure that each prompt builds on the previous prompts, and ends with wiring things together.
There should be no hanging or orphaned code that isn't integrated into a previous step.

Make sure and separate each prompt section. Use markdown. Each prompt should be tagged as text using code tags.
The goal is to output prompts, but context, etc is important as well.
```
- Use a local (free) reasoning LLM model to create a todo.md. The execution LLM can check off the todo.md while processing. This is good for keeping state across sessions.
```
Create a `todo.md` that I can use as a checklist. Be thorough.
```
- Use Web Shark to scrape and gather all the required code and API documentation found in the spec.md file for the LLM to referenece (prevents online misinformation and code hallucination).
- Use Repomix to consolodate code examples, scraped API documentation, the spec.md and todo.md.  This creates a single .xml file that's ideal for the LLM to use as context.
- Add a repomix.config.json file to the crawled output directory.  This provides instruction to Repomix on how to handle the files.
```bash
docker run -v "C:\Users\Dallas\developer\myProjects\webShark\crawler_output:/app" -it --rm ghcr.io/yamadashy/repomix
```
- This process will output a repomix-output.xml with all of the project data in a single file for the LLM to consume.   

Execution
- Use a heavy hitting thinking LLM model such as Sonnet 3.7 or 3.7 MAX with Cursor or Aider.
- Add the repomix-output.xml as context to the Agent/Architect
- Feed the Agent/Architect one prompt at a time from the prompt_plan.md (what happens if you just give it the whole file??).
- Test every change.  If it fails, ensure it has the repomix-output.xml in context and reference the specific API or code example as needed.
- Rinse and repeat






## License

This project is open source and available under the [License](license.md). Feel free to use it in your projects, but please adhere to its terms.
