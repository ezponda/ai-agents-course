# Python AI Agents — Code Course

The **code** counterpart of the no-code n8n course (`../n8n_no_code/`). Teaches AI agents in
Python, from the raw agent loop up to LangGraph, all runnable in Google Colab.

> **Live:** [ezponda.github.io/ai-agents-course/python](https://ezponda.github.io/ai-agents-course/python/).
> Every push to `main` rebuilds and republishes it via `.github/workflows/deploy-book.yml`.
> Build locally with `make build-python`. When you change anything under `_static/` (CSS/JS), use a
> clean build so Sphinx recopies it: `jupyter-book build courses/python_code/book --all`.

## The arc

| Block | Tool | What you learn |
|-------|------|----------------|
| **0 · Pure Python core** | raw `openai` SDK | What an agent *is*: the loop by hand, workflows, memory — then how a real **coding agent** and **context engineering** work. "This is how Claude Code works." |
| **1 · PydanticAI** | `pydantic-ai` | The clean, typed agent: tools, memory, guardrails, offline testing, evals — up to the **knowledge agent (RAG)**. |
| **2 · LangGraph** | `langgraph` + `langchain` | State, graphs, persistence, human-in-the-loop, multi-agent. The visual model. |
| **3 · Production** | `fastapi` | Deploy as code, connect your app, projects, "which tool when". |

## Design decisions

- **Model-agnostic via one variable.** Every notebook has a single `MODEL = "..."` the student
  changes. The spine is the **OpenAI Chat Completions format via OpenRouter** (one key, any model —
  Claude / GPT / Gemini / Llama), chosen for durability and continuity with the n8n course.
- **Colab-first.** Each notebook is self-contained (installs its own deps, downloads its own data)
  and carries an "Open in Colab" badge.
- **Language: English** (same as the n8n book).

## Contents (37 notebooks)

Numbering leaves gaps on purpose — the tens digit is the block, and remaining gaps (`09`, `29`)
are headroom for future notebooks without renumbering.

- **Block 0** — `00`–`08` (9): what an agent is, setup, structured output, the raw tool loop,
  workflow patterns, reflection + human-in-the-loop, memory, **building a coding agent** (`07`),
  **context engineering** (`08`).
- **Block 1** — `10`–`19` (12): raw↔PydanticAI Rosetta, first agent, tools (incl. a real wttr.in
  tool), typed output + DI, memory, guardrails (incl. read/write tool safety), **offline testing
  with `TestModel`/`FunctionModel`** (`15b`), evals + observability + error-analysis, the knowledge
  agent (RAG), **using** an MCP server (`18`), **building** an MCP server with FastMCP (`18b`),
  debugging agents.
- **Block 2** — `20`–`28` (9): agent-as-graph Rosetta, StateGraph, the agent loop as a graph,
  persistence, human-in-the-loop, cyclic reflection, multi-agent, self-corrective RAG, long-term
  memory (the Store).
- **Block 3** — `30`–`33` (5): deploy with FastAPI + streaming, connect your app, the **capstone
  project** (Data Analyst Agent — code-execution tool + memory + guardrails + eval), a second
  project (**Smart Onboarding**, `32b`), "which tool when".
- **Appendices** — prompt engineering, resources.

Most notebooks carry a `🔧 Common issues (and fixes)` troubleshooting dropdown.

## Versions — last verified

The framework code was written and API-verified against these versions (mid-2026). Pins cap at the
next major to avoid a breaking release landing mid-lesson. See `requirements.txt`.

| Package | Verified | Pin |
|---------|----------|-----|
| `openai` | 2.x | `>=2,<3` |
| `pydantic-ai-slim[openai]` | **2.5** | `>=2.0,<3.0` |
| `pydantic-evals` | 2.5 | `>=2.0,<3.0` |
| `langchain` / `langgraph` / `langchain-openai` | 1.3 / 1.2 / 1.3 | `>=1.x,<2.0` |
| `sentence-transformers` (RAG) | 5.x | `>=3,<6` |

> **Note on PydanticAI:** the course uses the v2 API (`OpenAIChatModel`, `result.output`,
> `output_type`). `OpenAIChatModel` is the forward-compatible name (the v1-only spelling was the now
> removed `OpenAIModel`). When a future major lands, re-verify and bump deliberately — don't let pip
> pick it mid-lesson.

See `../../plan_curso_python_agents_2026-07-01.html` at the repo root for the full plan.
