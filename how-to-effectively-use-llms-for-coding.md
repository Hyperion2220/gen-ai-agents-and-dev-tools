# How to EFFECTIVELY use LLMs for coding:

## Step 1: Idea honing
Use a conversational LLM to hone in on an idea.

```
Ask me one question at a time so we can develop a thorough, step-by-step spec for this idea. Each question should build on my previous answers, and our end goal is to have a detailed specification I can hand off to a developer. Let’s do this iteratively and dig into every relevant detail. Remember, only one question at a time.

Here’s the idea:  

<IDEA>
```

At the end of the brainstorm (it will come to a natural conclusion):  


```
Now that we’ve wrapped up the brainstorming process, can you compile our findings into a comprehensive, developer-ready specification? Include all relevant requirements, architecture choices, data handling details, error handling strategies, and a testing plan so a developer can immediately begin implementation.
```

This will output a pretty solid and straightforward spec that can be handed off to the planning step. I like to save it as `spec.md` in the repo.

You can use this spec for a number of things. We are doing codegen here, but I have used it to bolster ideas by asking a reasoning model to poke holes in the idea (must go deeper!), to generate a white paper, or to generate a business model. You can pop it into deep research and get a 10k word supporting document in return.

## Step 2: Planning
Take the spec and pass it to a proper reasoning model (o1*, o3*, r1):

### Test-Driven Development

```
Draft a detailed, step-by-step blueprint for building this project. Then, once you have a solid plan, break it down into small, iterative chunks that build on each other. Look at these chunks and then go another round to break it into small steps. Review the results and make sure that the steps are small enough to be implemented safely with strong testing, but big enough to move the project forward. Iterate until you feel that the steps are right sized for this project.

From here you should have the foundation to provide a series of prompts for a code-generation LLM that will implement each step in a test-driven manner. Prioritize best practices, incremental progress, and early testing, ensuring no big jumps in complexity at any stage. Make sure that each prompt builds on the previous prompts, and ends with wiring things together. There should be no hanging or orphaned code that isn't integrated into a previous step.

Make sure and separate each prompt section. Use markdown. Each prompt should be tagged as text using code tags. The goal is to output prompts, but context, etc is important as well.

<SPEC>
```

### Non-Test-Driven Development

```
Draft a detailed, step-by-step blueprint for building this project. Then, once you have a solid plan, break it down into small, iterative chunks that build on each other. Look at these chunks and then go another round to break it into small steps. review the results and make sure that the steps are small enough to be implemented safely, but big enough to move the project forward. Iterate until you feel that the steps are right sized for this project.

From here you should have the foundation to provide a series of prompts for a code-generation LLM that will implement each step. Prioritize best practices, and incremental progress, ensuring no big jumps in complexity at any stage. Make sure that each prompt builds on the previous prompts, and ends with wiring things together. There should be no hanging or orphaned code that isn't integrated into a previous step.

Make sure and separate each prompt section. Use markdown. Each prompt should be tagged as text using code tags. The goal is to output prompts, but context, etc is important as well.

<SPEC>
```

It should output a prompt plan that you can execute with aider, cursor, etc. I like to save this as `prompt_plan.md` in the repo.

I then have it output a `todo.md` that can be checked off.

```
Can you make a `todo.md` that I can use as a checklist? Be thorough.
```
 
You can save it as `todo.md` in the repo.

Your codegen tool should be able to check off the `todo.md` while processing. This is good for keeping state across sessions.

Yay. Plan!

Now you have a robust plan and documentation that will help you execute and build your project.

This entire process will take maybe 15 minutes. It is pretty quick. 

## Step 3: Execution
There are so many options available for execution. The success really depends on how well step 2 went.

I have used this workflow with github workspace, aider, cursor, claude engineer, sweep.dev, chatgpt, claude.ai, etc. It works pretty well with all the tools I have tried, and I imagine it will work well with any codegen tool.

I, however, prefer raw claude and aider:

### Claude
I essentially pair program with claude.ai and just drop each prompt in iteratively. I find that works pretty well. The back and forth can be annoying, but it largely works.

I am in charge of the initial boilerplate code, and making sure tooling is set up correctly. This allows for some freedom, choice, and guidance in the beginning. Claude has a tendency to just output react code - and having a solid foundation with the language, style, and tooling of your choice will help quite a bit.

I will then use a tool like repomix (https://github.com/yamadashy/repomix) to iterate when things get stuck (more about that later).

The workflow is like this:

- set up the repo (boilerplate, uv init, cargo init, etc)
- paste in prompt into claude
- copy and paste code from claude.ai into IDE
- run code, run tests, etc
- …  
- if it works, move on to next prompt
- if it doesn’t work, use repomix to pass the codebase to claude to debug
- rinse repeat ✩₊˚.⋆☾⋆⁺₊✧

### Aider
Aider is fun and weird to use. I find that it slots in well to the output of step 2. I can get really far with very little work.

The workflow is essentially the same as above but instead of pasting into claude, I am pasting the prompts into aider.

Aider will then “just do it” and I get to play cookie clicker.

**An aside:** Aider does really great benchmarking of new models for codegen in their LLM leaderboards. I find it to be a really great resource for seeing how effective new models are.

Testing is nice with aider, because it can be even more hands off as aider will run the test suite and debug things for you.

The workflow is like this:

- set up the repo (boilerplate, uv init, cargo init, etc)
- start aider
- paste prompt into aider
- watch aider dance ♪┏(・o･)┛♪
- aider will run tests, or you can run app to verify
- if it works, move on to next prompt
- if it doesn’t work, Q&A with aider to fix
- rinse repeat ✩₊˚.⋆☾⋆⁺₊✧

### Results
I have built so so many things using this workflow: scripts, expo apps, rust cli tools, etc. It has worked across programming languages, and contexts. I do like it.

If you have a small or large project that you are procrastinating on, I would recommend giving it a shot. You will be surprised how far you can get in a short amount of time.

My hack to-do list is empty because I built everything. I keep thinking of new things and knocking them out while watching a movie or something. For the first time in years, I am spending time with new programming languages and tools. This is pushing me to expand my programming perspective.



## Non-greenfield:  Iteration, incrementally
Sometimes you don’t have greenfield, and instead need to iterate or do increment work on an established code base.

For this I have a slightly different method. It is similar to above, but a bit less “planning based.” The planning is done per task, not for the entire project.

### Get context
I think everyone who is knee-deep in AI dev has a different tool for this, but you need something to grab your source code and efficiently jam it into the LLM.

I currently use a tool called repomix. I have a task collection defined in my global `~/.config/mise/config.toml` that allows me to do various things with my code base (https://mise.jdx.dev/).

Here is the LLM task list:
- `LLM:clean_bundles`           Generate LLM bundle output file using repomix
- `LLM:copy_buffer_bundle`      Copy generated LLM bundle from output.txt to system clipboard for external use
- `LLM:generate_code_review`    Generate code review output from repository content stored in output.txt using LLM generation
- `LLM:generate_github_issues`  Generate GitHub issues from repository content stored in output.txt using LLM generation
- `LLM:generate_issue_prompts`  Generate issue prompts from repository content stored in output.txt using LLM generation
- `LLM:generate_missing_tests`  Generate missing tests for code in repository content stored in output.txt using LLM generation
- `LLM:generate_readme`         Generate README.md from repository content stored in output.txt using LLM generation

I generate an `output.txt` that has the context from my code base. If I am blowing through tokens, and it is too big - I will edit the generate command to ignore parts of the code base that are not germane to this task.

One thing really nice about mise is that the tasks can be redefined and overloaded in the working directory’s `.mise.toml`. I can use a different tool to dump/pack the code, and as long as it generates an `output.txt` I can use my LLM tasks. This is helpful when various codebases differ so much. I regularly override the repomix step to include broader ignore patterns, or just use a more effective tool to do the packing.

Once the `output.txt` is generated, I pass it to the LLM command to do various transformations and then save those as a markdown file.

Ultimately, the mise task is running this: `cat output.txt | LLM -t readme-gen > README.md` or `cat output.txt | LLM -m claude-3.5-sonnet -t code-review-gen > code-review.md`. This isn’t super complicated. the LLM command is doing the heavy lifting (supporting different models, saving keys, and using prompt templates).

For example, if I need a quick review and fix of test coverage I would do the following:

#### Claude
- go to the directory where the code lives
- run `mise run LLM:generate_missing_tests`
- look at the generated markdown file (`missing-tests.md`)
- grab the full context for the code: `mise run LLM:copy_buffer_bundle`
- paste that into claude along with the first missing test “issue”
- copy the generated code from claude into my ide.
- …  
- run tests
- rinse repeat ✩₊˚.⋆☾⋆⁺₊✧

#### Aider
- go to the directory where the code lives
- run aider (always make sure you are on a new branch for aider work)
- run `mise run LLM:generate_missing_tests`
- look at the generated markdown file (`missing-tests.md`)
- paste the first missing test “issue” into aider
- watch aider dance ♪┏(・o･)┛♪
- …  
- run tests
- rinse repeat ✩₊˚.⋆☾⋆⁺₊✧

This is a pretty good way to incrementally improve a code base. It has been super helpful to do small amounts of work in a big code base. I have found that I can do any sized tasks with this method.

### Prompt magic
These quick hacks work super well to dig into places where we can make a project more robust. It is super quick, and effective.

Here are some of my prompts that I use to dig into established code bases:

#### Code review
```
You are a senior developer. Your job is to do a thorough code review of this code. You should write it up and output markdown. Include line numbers, and contextual info. Your code review will be passed to another teammate, so be thorough. Think deeply  before writing the code review. Review every part, and don't hallucinate.
```

#### GitHub Issue generation
*(I need to automate the actual issue posting!)*  
```
You are a senior developer. Your job is to review this code, and write out the top issues that you see with the code. It could be bugs, design choices, or code cleanliness issues. You should be specific, and be very good. Do Not Hallucinate. Think quietly to yourself, then act - write the issues. The issues will be given to a developer to executed on, so they should be in a format that is compatible with github issues
```

#### Missing tests
```
You are a senior developer. Your job is to review this code, and write out a list of missing test cases, and code tests that should exist. You should be specific, and be very good. Do Not Hallucinate. Think quietly to yourself, then act - write the issues. The issues  will be given to a developer to executed on, so they should be in a format that is compatible with github issues
```
