# Run the Course Locally

Local JupyterLab is the recommended way to execute the course. The notebooks are written in
portable Markdown, so the notes, warnings and collapsible sections render the same way here as they
do in the book, in Colab, on GitHub and in VS Code. No editor extension is needed.

Use **Python 3.12**. The setup below creates an isolated `.venv` in the repository and installs
only the notebook interface. Each notebook installs its own lesson dependencies in its first code
cell.

## macOS and Linux

From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r courses/python_code/requirements-local.txt
python -m jupyter lab courses/python_code/book
```

## Windows PowerShell

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r courses/python_code/requirements-local.txt
python -m jupyter lab courses/python_code/book
```

If PowerShell blocks activation, the environment can be used directly:

```powershell
.\.venv\Scripts\python -m pip install -r courses/python_code/requirements-local.txt
.\.venv\Scripts\python -m jupyter lab courses/python_code/book
```

JupyterLab opens in the browser. Choose a notebook in the file browser and run its cells from top
to bottom. Stop the server with `Ctrl+C` in the terminal.

## Optional: install every course dependency

The default setup avoids downloading frameworks that are not needed for the current lesson. To
prepare the complete environment at once, run:

```bash
python -m pip install -r courses/python_code/requirements.txt
```

This is a larger installation because the RAG lessons include `sentence-transformers` and its
machine-learning dependencies.

## API keys

Notebooks that call a live model ask for an OpenRouter API key with `getpass`; the value is not
written into the notebook. Offline lessons and tests do not need a key. Create one at
[openrouter.ai/keys](https://openrouter.ai/keys).

## Other ways to run a notebook

The relevant toolbar actions above each notebook are:

- **Launch (rocket):** opens a menu with Google Colab, which needs no local setup.
- **Download:** downloads the current `.ipynb` file.
- **GitHub:** opens the source repository.

The published Jupyter Book remains the canonical reading view, and it is the only one with the
course navigation. For running the code, choose on setup rather than on formatting: local
JupyterLab if you want to keep your work in the repository, Colab if you want to start with no
install at all.

## Common issues

| Symptom | Fix |
|---|---|
| Jupyter uses a different Python environment | In JupyterLab, select the kernel from `.venv`, then restart the kernel. |
| `ModuleNotFoundError` after opening a notebook | Run its first setup cell, or install the complete course requirements. |
| The extension reports incompatible dependencies | Reinstall `requirements-local.txt`; the JupyterLab version is pinned deliberately. |
| A live-model cell waits for input | Enter an OpenRouter key, or use the notebook's offline path when it has one. |
