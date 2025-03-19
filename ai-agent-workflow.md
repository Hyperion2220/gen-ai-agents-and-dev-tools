# AI Agent Workflow

## Idea Honing
- Use a local (free) LLM model to iterate on an idea and output a developer-ready specification in `spec.md` file.

---

Let's collaboratively develop a detailed specification for my project. I will provide answers to your questions one at a time, and I encourage you to ask follow-up questions that build on my previous responses. 

The goal is to create a comprehensive document that I can hand off to a developer, covering all relevant requirements, architecture choices, data handling details, error handling strategies, and a testing plan.

Please start by asking a specific question about the project idea, and ensure that each question encourages me to provide detailed information. After each response, feel free to ask for clarification or additional details as needed. Let's work iteratively to refine the specification until it is ready for implementation.

- At the end of the idea honing process, ask the LLM to output to a spec.md file.  This should contain a list of all high level dependencies such as Astral UV, Pydantic, LangGraph, Bedrock Converse API, etc.

## Compilation of Findings
Now that we've wrapped up the brainstorming process, can you compile our findings into a comprehensive, developer-ready specification? 

Please include the following sections in markdown format:
- **Relevant Requirements**: List all functional and non-functional requirements.
- **Architecture Choices**: Describe the architecture, including any frameworks or technologies to be used.
- **Data Handling Details**: Outline how data will be managed, including storage and retrieval methods.
- **Error Handling Strategies**: Specify how errors will be managed and reported.
- **Testing Plan**: Provide a detailed testing strategy, including unit tests, integration tests, and any tools to be used.

---

## Planning
- Use a local (free) reasoning LLM model to create a step-by-step blueprint in LLM prompt format. Output to a `prompt_plan.md` file.

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

## Web Scraping and Consolidation
- Use Web Shark to scrape and gather all the required code and API documentation found in the `spec.md` file for the LLM to reference (prevents online misinformation and code hallucination).
- Use Repomix website or Docker to consolidate code examples, scraped API documentation, the `spec.md`, and `todo.md`. This creates a single `.xml` file that's ideal for the LLM to use as context.
- Add a `repomix.config.json` file to the crawled output directory. This provides instruction to Repomix on how to handle the files.

```bash
docker run -v "C:\Users\Dallas\developer\myProjects\webShark\crawler_output:/app" -it --rm ghcr.io/yamadashy/repomix
```

- This process will output a `repomix-output.xml` with all of the project data in a single file for the LLM to consume.   

## Execution
- Use a heavy-hitting thinking LLM model such as Sonnet 3.7 or 3.7 MAX with Cursor or Aider.
- Add the `repomix-output.xml` as context to the Agent/Architect.
- Feed the Agent/Architect one prompt at a time from the `prompt_plan.md` (what happens if you just give it the whole file??).
- Test every change. If it fails, ensure it has the `repomix-output.xml` in context and reference the specific API or code example as needed.
- Rinse and repeat.
