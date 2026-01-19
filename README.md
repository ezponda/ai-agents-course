# AI Agents Course

[![n8n](https://img.shields.io/badge/n8n-workflow%20automation-FF6D5A)](https://n8n.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-agent%20framework-1C3C3C)](https://langchain-ai.github.io/langgraph/)
[![Level](https://img.shields.io/badge/Level-Beginner-brightgreen)](/)

Learn to build AI agents using n8n and LangGraph. No prior experience required.

## Install n8n

### Without Docker

**macOS**
```bash
brew install n8n
```

**Windows / Linux**
```bash
npm install n8n -g
```

Start n8n:
```bash
n8n start
```

### With Docker

```bash
docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

Open `http://localhost:5678` in your browser.

## Import Workflows

1. Open n8n (`http://localhost:5678`)
2. Go to **Workflows** → **Add Workflow**
3. Click **⋮** → **Import from File...**
4. Select the `.json` workflow file
5. Click **Save**

## Troubleshooting

| Issue | Solution |
|-------|----------|
| n8n won't start | Check Node.js v18+ is installed |
| Port in use | `lsof -i :5678` (macOS/Linux) or `netstat -ano \| findstr :5678` (Windows) |
| Import fails | Verify JSON file is valid |

## Resources

- [n8n Docs](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)

## License

[MIT](LICENSE)
