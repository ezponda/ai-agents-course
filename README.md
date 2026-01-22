# AI Agents Course

[![n8n](https://img.shields.io/badge/n8n-workflow%20automation-FF6D5A)](https://n8n.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-agent%20framework-1C3C3C)](https://langchain-ai.github.io/langgraph/)
[![Level](https://img.shields.io/badge/Level-Beginner-brightgreen)](/)

Learn to build AI agents using n8n and LangGraph. No prior experience required.

## Course Materials

### n8n No-Code Course

The n8n course is available as a Jupyter Book:

- **Book location:** `courses/n8n_no_code/book/`
- **GitHub Pages:** (deployed automatically on push to main)

**Chapters:**
1. Introduction — What is n8n
2. Setup — Install and run n8n locally
3. Core Concepts — Triggers, nodes, data flow, debugging
4. Node Toolbox — Essential nodes for AI workflows
5. Workflow Examples — Chaining, routing, parallelization

## Build the Book Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Build the n8n book
make build-n8n

# Or directly:
jupyter-book build courses/n8n_no_code/book
```

The built HTML will be in `courses/n8n_no_code/book/_build/html/`.

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
4. Select the `.json` workflow file from `courses/n8n_no_code/01_intro_patterns/workflows/`
5. Click **Save**

## Repository Structure

```
ai-agents-course/
├── courses/
│   └── n8n_no_code/
│       ├── book/              # Jupyter Book source
│       │   ├── _config.yml
│       │   ├── _toc.yml
│       │   └── *.ipynb        # Chapter notebooks
│       ├── 01_intro_patterns/
│       │   └── workflows/     # Example workflow JSONs
│       └── images/
├── .github/
│   └── workflows/
│       └── deploy-book.yml    # GitHub Pages deployment
├── Makefile
├── requirements.txt
└── README.md
```

## Resources

- [n8n Docs](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Jupyter Book Docs](https://jupyterbook.org/)

## License

[MIT](LICENSE)
