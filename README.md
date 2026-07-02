# AI Agents Course

[![n8n](https://img.shields.io/badge/n8n-workflow%20automation-FF6D5A)](https://n8n.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![Level](https://img.shields.io/badge/Level-Beginner-brightgreen)](/)

## 📚 Course

**[View the n8n Course →](https://ezponda.github.io/ai-agents-course/)** — build AI agents with n8n, no code, no prior experience required.

**[View the Python Course →](https://ezponda.github.io/ai-agents-course/python/)** — the same ideas in code: the raw agent loop, then PydanticAI and LangGraph.

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

**Projects:** Recipe Assistant · Ask Your Data · Smart Onboarding · Deploy to Production

**Appendices:** Node Toolbox · Going Live · Specialized AI Nodes · Prompt Engineering (Basics & Agents) · Resources

### Python Code Course

The code counterpart, as a Jupyter Book:

- **Book location:** `courses/python_code/book/`
- **Live site:** [ezponda.github.io/ai-agents-course/python](https://ezponda.github.io/ai-agents-course/python/)

Colab-first and model-agnostic (one `MODEL` variable via OpenRouter). Four blocks
— pure-Python core → PydanticAI → LangGraph → production — plus capstone projects.
See `courses/python_code/README.md` for the full chapter list.

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
│   │   │   ├── *.ipynb                # Chapter notebooks
│   │   │   └── _static/
│   │   │       └── workflows/         # Example workflow JSONs
│   │   └── check_references.py        # Reference/consistency checker
│   └── python_code/
│       ├── book/                      # Jupyter Book source (served at /python/)
│       │   ├── _config.yml
│       │   ├── _toc.yml
│       │   └── *.ipynb                # Chapter notebooks (runnable)
│       ├── README.md
│       └── requirements.txt           # pinned deps for running the notebooks
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
