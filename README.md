# AI Agents Course

[![n8n](https://img.shields.io/badge/n8n-workflow%20automation-FF6D5A)](https://n8n.io/)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-3776AB?logo=python&logoColor=white)](https://python.org/)
[![n8n Level](https://img.shields.io/badge/n8n-Beginner-brightgreen)](https://ezponda.github.io/ai-agents-course/)
[![Python Track](https://img.shields.io/badge/Python-Code--first-blue)](https://ezponda.github.io/ai-agents-course/python/)

## 📚 Course

Choose the visual course if you want to learn the concepts without code, or the Python course if
you want to inspect and implement the mechanisms yourself.

**[View the n8n Course →](https://ezponda.github.io/ai-agents-course/)** — build AI agents visually, with no code or prior experience required.

**[View the Python Course →](https://ezponda.github.io/ai-agents-course/python/)** — build the agent loop yourself, then progress to PydanticAI, LangGraph, and production patterns.

| Course | For | Prerequisites | What you will build | Format |
|--------|-----|---------------|---------------------|--------|
| **[n8n No-Code](https://ezponda.github.io/ai-agents-course/)** | Beginners and automation practitioners | None | Visual workflows and agents with tools, memory, RAG, guardrails, evals, and seven projects | Jupyter Book + downloadable n8n workflows |
| **[Python AI Agents](https://ezponda.github.io/ai-agents-course/python/)** | Python users who want to understand agent internals | Basic Python | The raw agent loop, typed agents, RAG, MCP, evals, LangGraph, deployment patterns, and capstone projects | 41 notebooks (37 executable), local JupyterLab + Colab |

## Course Materials

### n8n No-Code Course

The n8n course is available as a Jupyter Book:

- **Book location:** `courses/n8n_no_code/book/`
- **Live site:** [ezponda.github.io/ai-agents-course](https://ezponda.github.io/ai-agents-course/)

**Course chapters:**
1. What is an AI Agent? — Workflows vs agents
2. Setup — Install and run n8n locally
3. Quick Start — Build your first AI workflow from scratch
4. Core Concepts — Data flow, expressions, debugging
5. Workflow Examples — Prompt chaining, routing, parallelization, human-in-the-loop
6. Reflection Pattern — Self-improving loops (manual vs agent)
7. First AI Agent — Build agents with tools and memory
8. Tool Calling — How agents use tools safely
9. Guardrails & Safety — Prompt injection and output validation
10. RAG — Teach your AI to search your own documents

**Projects:** Recipe Assistant · Ask Your Data · Expense Assistant · Daily Digest · Deploy to Production · Connect Your App · Salon Booking Assistant

**Appendices:** Node Toolbox · Going Live · Specialized AI Nodes · Prompt Engineering (Basics & Agents) · Resources

### Python Code Course

The code counterpart, as a Jupyter Book:

- **Book location:** `courses/python_code/book/`
- **Live site:** [ezponda.github.io/ai-agents-course/python](https://ezponda.github.io/ai-agents-course/python/)

Model-agnostic (one `MODEL` variable via OpenRouter) and executable in local JupyterLab or Colab.
Local JupyterLab is recommended because it renders the course's MyST notes and dropdowns. The
course assumes basic Python, but no previous experience building AI agents.

**Course blocks:**
1. Pure Python Core — Model calls, structured output, the tool loop, workflow patterns, memory,
   a coding agent, context engineering, and an agent harness
2. PydanticAI — Typed agents, tools, dependency injection, guardrails, offline testing, evals,
   RAG, MCP, and debugging
3. LangGraph — State graphs, persistence, human approval, cyclic reflection, multi-agent
   systems, agentic RAG, long-term memory, and reliability
4. Production & Projects — FastAPI, streaming, application integration, durable execution, and
   framework selection

**Projects:** Coding Agent · Agent Harness · Knowledge Agent · Data Analyst Agent · Smart
Onboarding · Atlas Resumable Coworker

See `courses/python_code/README.md` for the full 41-notebook outline.

## Run the Python Course Locally

macOS/Linux quick start with Python 3.12 and an isolated environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r courses/python_code/requirements-local.txt
python -m jupyter lab courses/python_code/book
```

This installs JupyterLab with MyST rendering. Each notebook installs its lesson dependencies in
its first code cell. See the complete [macOS, Linux, and Windows instructions](courses/python_code/book/local_setup.md),
including troubleshooting and the optional full dependency install.

## Build the Books Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Build a book
make build-n8n        # n8n course
make build-python     # Python course

# Or directly:
jupyter-book build courses/n8n_no_code/book
jupyter-book build courses/python_code/book
```

The built HTML lands in each course's `book/_build/html/`.

## Install n8n

### With Docker (Recommended)

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

### Without Docker

**macOS**
```bash
brew install n8n
n8n start
```

**Windows / Linux**
```bash
npm install n8n -g
n8n start
```

Open `http://localhost:5678` in your browser.

## Import Workflows

1. Open n8n (`http://localhost:5678`)
2. Go to **Workflows** → **Add Workflow**
3. Click **⋮** → **Import from File...**
4. Select the `.json` workflow file from `courses/n8n_no_code/book/_static/workflows/`
5. Click **Save**

## Repository Structure

```
ai-agents-course/
├── courses/
│   ├── n8n_no_code/
│   │   ├── book/                      # Jupyter Book source (served at site root)
│   │   │   ├── _config.yml
│   │   │   ├── _toc.yml
│   │   │   ├── *.md                   # Chapter pages (MyST Markdown)
│   │   │   └── _static/
│   │   │       └── workflows/         # Example workflow JSONs
│   │   └── check_references.py        # Reference/consistency checker
│   └── python_code/
│       ├── book/                      # Jupyter Book source (served at /python/)
│       │   ├── _config.yml
│       │   ├── _toc.yml
│       │   ├── local_setup.md          # Local JupyterLab instructions
│       │   └── *.ipynb                 # Course notebooks
│       ├── README.md
│       ├── requirements-local.txt      # JupyterLab + MyST interface
│       └── requirements.txt           # supported ranges for running the notebooks
├── .github/
│   └── workflows/
│       └── deploy-book.yml            # Builds both books → GitHub Pages
├── Makefile
├── requirements.txt
└── README.md
```

## Resources

- [n8n Docs](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [Jupyter Book Docs](https://jupyterbook.org/)

## License

[MIT](LICENSE)
