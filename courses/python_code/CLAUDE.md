# Python Course - Claude Code Context

This file helps Claude Code maintain consistency when editing the student-facing Python AI Agents course.

## Quick Reference

**Build command:** `make build-python` (or `make clean-python && make build-python`)
**Book source:** `courses/python_code/book/*.ipynb`
**Book config:** `courses/python_code/book/_config.yml`
**Table of contents:** `courses/python_code/book/_toc.yml`
**Static assets:** `courses/python_code/book/_static/`
**Dependencies:** `courses/python_code/requirements.txt`
**Output:** `courses/python_code/book/_build/html/`
**Live URL:** `https://ezponda.github.io/ai-agents-course/python/`

When changing files under `_static/`, prefer a clean build so Sphinx recopies CSS/JS:

```bash
jupyter-book build courses/python_code/book --all
```

## Audience

Beginner-to-intermediate Python learners who want to understand and build AI agents in code.

Assume the learner can read simple Python, but do not assume production AI experience. The course should make agents feel mechanical and inspectable: messages, tool calls, state, traces, evals, and deployment.

## Course Arc

The Python course is the code counterpart of `courses/n8n_no_code/`.

| Block | Main tool | Teaching purpose |
|-------|-----------|------------------|
| 0 - Pure Python core | raw `openai` SDK | The agent loop by hand: model calls, structured output, tools, workflows, reflection, memory, coding agents, context engineering, and a small agent harness |
| 1 - PydanticAI | `pydantic-ai` | Typed agents: tools, dependency injection, memory, guardrails, testing, evals, RAG, MCP, debugging |
| 2 - LangGraph | `langgraph` + `langchain` | State, graph control flow, persistence, interrupts, cycles, multi-agent, agentic RAG, reliability |
| 3 - Production | `fastapi` + clients | Agent as an API, app integration, projects, durable approvals and effects, framework/tool selection |

Use `_toc.yml` as the source of truth for ordering. If notebook counts, block ranges, or titles change, update `courses/python_code/README.md` and the root `README.md` when relevant.

## Design Decisions

### 1. Colab-first

Every notebook should work in Google Colab and locally in Jupyter.

- Include an "Open in Colab" link near the top.
- Install notebook-specific dependencies in the first executable cell.
- Avoid requiring local files unless the notebook writes or downloads them itself.
- Avoid long-running servers inside Colab; write service files with `%%writefile` and explain how to run them locally or on a host.
- Keep cells runnable top-to-bottom after a fresh runtime restart.

Colab URL pattern:

```markdown
https://colab.research.google.com/github/ezponda/ai-agents-course/blob/main/courses/python_code/book/{notebook_name}.ipynb
```

### 2. Model-agnostic through OpenRouter

The teaching default is the official `openai` SDK pointed at OpenRouter.

Keep the pattern:

```python
MODEL = "meta-llama/llama-3.3-70b-instruct"
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
```

For PydanticAI notebooks, keep the v2 pattern:

```python
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

MODEL_NAME = "meta-llama/llama-3.3-70b-instruct"
model = OpenAIChatModel(
    MODEL_NAME,
    provider=OpenAIProvider(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    ),
)
```

For LangChain/LangGraph notebooks, keep:

```python
from langchain_openai import ChatOpenAI

MODEL_NAME = "meta-llama/llama-3.3-70b-instruct"
llm = ChatOpenAI(
    model=MODEL_NAME,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
```

Do not casually replace OpenRouter with provider-specific SDKs. If a direct provider call is needed, explain why and keep the main path model-agnostic.

### 3. Secrets

- Never hard-code API keys.
- Use `OPENROUTER_API_KEY` for model calls.
- Read keys with `getpass.getpass(...)` in notebooks.
- Mention Colab Secrets as an optional path, but do not require it.
- Production examples should read `OPENROUTER_API_KEY`, `MODEL_NAME`, and `AGENT_API_KEY` from environment variables.

### 4. Framework versions

Respect `courses/python_code/requirements.txt`.

Current verified families:

| Area | Package pattern |
|------|-----------------|
| Raw calls | `openai>=2,<3` |
| PydanticAI | `pydantic-ai-slim[openai]>=2.0,<3.0` |
| Evals | `pydantic-evals>=2.0,<3.0` |
| LangGraph | `langgraph>=1.2,<2.0` |
| LangChain | `langchain>=1.3,<2.0`, `langchain-openai>=1.3,<2.0` |
| RAG | `sentence-transformers>=3.0,<6` |
| MCP server | `fastmcp>=2.0,<3.0` |
| Production | `fastapi>=0.115`, `uvicorn>=0.30`, `gradio>=5,<6` |

When framework docs move, verify against the pinned course versions before changing lesson code. Do not use removed PydanticAI v1 names such as `OpenAIModel`; use `OpenAIChatModel`, `result.output`, and `output_type`.

## Notebook Contract

Each notebook should have:

1. A top-level `# Title`.
2. A short "**What you will build:**" opening that names the concrete artifact or skill.
3. A Colab/local run note.
4. A first setup cell that installs only the dependencies needed for that notebook.
5. A clear mental model before framework abstraction.
6. Runnable code cells that build the idea incrementally.
7. A small "try it yourself", exercise, or challenge section when useful.
8. A "Common issues" dropdown for notebooks that call models, tools, MCP, servers, or external services.
9. A short "What's next" close when the transition matters.

Prefer this teaching rhythm:

1. Show the problem.
2. Build the mechanism in plain Python or the smallest possible framework surface.
3. Inspect the messages, state, tool calls, traces, or outputs.
4. Add the reliability habit: validation, guardrail, test, eval, timeout, budget, or trace.
5. Connect it to the next notebook or to the n8n equivalent.

## Terminology

Use these terms consistently:

| Term | Meaning in this course |
|------|------------------------|
| LLM call | A single stateless request/response with a model |
| Augmented LLM | An LLM call wired to retrieval, tools, or memory; the building block under workflows and agents |
| Workflow | Engineer-owned sequence/graph of LLM calls and tools |
| Agent | Model-owned loop that chooses tools and next steps dynamically |
| Tool call | Structured request from the model that the runtime dispatches to code |
| Observation | Tool result fed back to the model |
| Memory | Conversation/state explicitly supplied by the program, not something the API remembers automatically |
| Guardrail | A check that prevents or corrects unsafe, invalid, or off-task behavior |
| Eval | A repeatable measurement of agent quality across cases |
| Trace | The recorded run: messages, tool calls, observations, timing, cost, and errors |
| Checkpointer | LangGraph persistence layer that lets a run resume from saved state |
| Store | LangGraph long-term memory interface across threads/sessions |
| MCP | Model Context Protocol; a standard way to expose tools/resources/prompts to agent hosts |

## Style

- Course language is English.
- Use plain, direct prose. Define jargon before relying on it.
- Keep the voice practical and reassuring: "here is the mechanism", then "here is why it matters".
- Prefer small tables for comparisons and failure modes.
- Use code comments sparingly, only where they clarify a non-obvious teaching point.
- Avoid broad marketing language. The notebook should teach by doing.
- Avoid repeating cost warnings everywhere; one focused warning in setup/deploy contexts is enough.
- Use the established dropdown icons as navigation labels: `🛠️` for practice/solutions, `🔧` for troubleshooting/under-the-hood notes, and `🔍` for inspection/reference. Avoid extra decorative emoji in normal prose.

## Code Habits

- Keep examples deterministic where possible: `temperature=0` for demos, tests, evals, structured output, and tool routing.
- Always surface tool errors to the model or the learner; do not swallow exceptions into empty strings.
- Put hard caps on loops: max turns, max retries, recursion limits, timeouts, or budgets.
- Prefer plain Python checks over LLM judges when the requirement is objective.
- Use typed structures (`BaseModel`, `TypedDict`, dataclasses, `Literal`) when the shape matters.
- For generated app/server files, keep secrets in environment variables.
- For notebooks that use `await`, avoid `run_sync` inside an already-running notebook event loop.
- For RAG examples, make retrieval inspectable: show chunks, scores, retrieved passages, and failure/rewrite paths.
- For LangGraph examples, make control flow visible: draw or describe nodes, edges, router conditions, interrupt/resume state, and stop paths.
- For MCP examples, separate the concept clearly: local Python function, MCP server, MCP client/toolset, and agent consuming that tool.

## Cross-course Mapping

When useful, map Python notebooks back to the no-code course:

| Python topic | n8n counterpart |
|--------------|-----------------|
| `00_what_is_an_agent` | `01a_what_is_an_agent` |
| `04_workflow_patterns` | `04a`-`04d` workflow patterns |
| `05_reflection_and_hitl` | `05_reflection_pattern`, `04d_human_in_the_loop` |
| `07_build_a_coding_agent` | Coding-agent concepts behind Claude Code/OpenAI Codex |
| `15_guardrails_and_validation` | `08_guardrails_safety` |
| `17_knowledge_agent_rag` | `09_rag`, `project_2_ask_your_data` |
| `26_multi_agent_supervisor` | `10_multi_agent_systems` |
| `30_deploy_fastapi` | `project_5_deploy_to_production` |
| `31_connect_your_app` | `project_6_connect_your_app` |

Do not force the mapping into every page. Use it when it reduces cognitive load.

## File Naming Conventions

| Category | Pattern | Example |
|----------|---------|---------|
| Course notebooks | `NN_name.ipynb` | `03_tool_use_from_scratch.ipynb` |
| Inserted notebooks | `NNb_name.ipynb` | `15b_testing_agents.ipynb` |
| Projects | `NN_project_name.ipynb` or `NNb_project_name.ipynb` | `32_project_data_analyst.ipynb` |
| Appendices | `appendix_name.ipynb` | `appendix_prompt_engineering.ipynb` |

Numbering intentionally leaves gaps. Do not renumber existing notebooks unless the user explicitly asks; it breaks links, Colab URLs, and student references.

## If You Add, Rename, or Delete a Notebook

Update all relevant places:

1. `courses/python_code/book/_toc.yml` - `file:` entry without `.ipynb`.
2. `courses/python_code/README.md` - contents, block counts, and descriptions.
3. Root `README.md` - only if the public course summary changes.
4. Cross-references in other notebooks.
5. Colab links inside the notebook itself.

Then run:

```bash
make build-python
```

For static asset changes, run:

```bash
jupyter-book build courses/python_code/book --all
```

## Common Edits

**Add a notebook:**

1. Create the `.ipynb` under `courses/python_code/book/`.
2. Add it to `_toc.yml` in the right block.
3. Start with title, "What you will build", Colab link, and setup cell.
4. Use the course's OpenRouter pattern unless the lesson is intentionally offline.
5. Add a "Common issues" dropdown if the notebook uses external APIs, frameworks, MCP, deploy, RAG, or server code.
6. Update `courses/python_code/README.md`.
7. Run `make build-python`.

**Update framework code:**

1. Check `courses/python_code/requirements.txt`.
2. Verify the exact API against the pinned major version.
3. Update install cells and prose together.
4. Prefer one migration note in the relevant notebook or README over scattered warnings.
5. Run the changed notebook cells when practical, then build the book.

**Add a project:**

1. Name the user-facing deliverable clearly.
2. Include at least one real reliability mechanism: guardrail, eval, test, timeout, trace, auth, or cost cap.
3. Show a minimal success criterion the learner can verify.
4. Keep secrets out of generated files.
5. Add troubleshooting for the likely failure modes.

**Fix a broken link:**

```bash
rg "old-url-or-stem" courses/python_code/book
```

Update all references, then rebuild.

## Validation

Minimum check:

```bash
make build-python
```

Useful local checks:

```bash
python3 -m pip install -r courses/python_code/requirements.txt
rg "OpenAIModel|OPENAI_API_KEY" courses/python_code/book
rg "result\\.data" courses/python_code/book
```

These `rg` checks are quick smoke tests for common drift:

- `OpenAIModel` usually means old PydanticAI v1 API.
- `OPENAI_API_KEY` may be valid for direct OpenAI examples, but this course normally uses `OPENROUTER_API_KEY`.
- `result.data` can be correct for FastMCP client results; if it appears in PydanticAI agent results, use `result.output` instead.

## TODO List on Commits

The n8n Claude context documents a repo-local `TODO.md` workflow. If you are creating a git commit and `TODO.md` exists at the repo root, read it before committing and surface pending tasks to the user. Do not create or modify `TODO.md` unless the user asks.

## Do Not

- Do not convert the course into a general ML/deep-learning curriculum.
- Do not add multi-language examples unless the lesson specifically needs them.
- Do not hide the agent loop behind a framework before the learner has seen the mechanism.
- Do not make every notebook depend on a paid model.
- Do not add unchecked long-running loops or public unauthenticated endpoints.
- Do not edit n8n workflows from Python-course changes unless the cross-course mapping truly requires it.
