# Project 2: Ask Your Data

Build your own "Julius AI" — ask questions in plain English, and an AI agent **writes and runs code** to answer them. The dataset is the top ~953 Spotify songs of 2023.

This is **programmatic tool calling**: instead of building a separate tool for every possible question, you give the agent a **code interpreter** and let it write whatever code each question needs. It's the same idea behind coding agents like Claude Code — one general "run code" tool is more powerful than a hundred narrow ones. (The same pattern works with SQL against a database; here we use a JavaScript interpreter so it runs anywhere with no setup.)

```{note}
**Where this sits on Anthropic's tool-calling map.** Anthropic's engineering guide [*Advanced tool use*](https://www.anthropic.com/engineering/advanced-tool-use) describes four patterns for scaling tool calling. This project is their **Programmatic Tool Calling** (+ **Code Execution**) pattern, in miniature:

| Anthropic pattern | The idea | In this project |
|---|---|---|
| **Programmatic Tool Calling** | The model writes code that does the work, instead of many narrow tool calls | The agent writes JavaScript per question — one `run_javascript` tool replaces a tool per question type |
| **Code Execution** | The code runs in a sandbox; intermediate data never enters the model's context | The ~953 rows live inside the Code Tool — only the `console.log()` line returns to the agent |
| **Tool Use Examples** | Show the model a real example instead of only describing the format | The "Sample (first row)" block in the system prompt — one real row teaches more than paragraphs |
| **Tool Search Tool** | Load tool definitions on demand when there are hundreds | Not needed here — this agent has exactly one tool |

The context saving is the underrated part: ask "what's the average BPM?" and the agent never sees 953 rows — it sees one printed number. Anthropic reports ~37% average token savings on complex tasks with this pattern.
```

You won't write code yourself. Your job is to give the agent the right context (the system prompt), test it with questions, and tighten the prompt when it fails.

The main lesson: **the system prompt is 80% of the work**. You'll see a naive prompt fail, then iterate until the agent reliably answers questions about the data.

| What you'll learn | Where it comes from |
|-------------------|--------------------|  
| **Code interpreter tool** — the agent writes and runs JavaScript | Builds on First AI Agent + Tool Calling (programmatic tool calling) |
| **System prompt engineering** — schema, sample data, and rules | Builds on the Prompt Engineering appendices |

**Workflow in this chapter:**

| File | What it does | GitHub Link |
|------|-------------|-------------|
| `11_ask_your_data.json` | Chat agent that writes + runs JavaScript over the Spotify data | [View](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/11_ask_your_data.json) |

**Credentials needed:** OpenRouter API key (Settings → Credentials).

```{note}
**Why JavaScript and not Python/pandas?** n8n's Python Code tool can't import libraries on n8n Cloud, and the old Pyodide runtime was removed in n8n 2.0 — so `pandas` isn't available out of the box. JavaScript runs everywhere with no setup. The lesson — *give the agent a code interpreter* — is identical; only the language changes. In production you'd often point the same pattern at SQL or a sandboxed Python service.
```

---

## The Dataset

We use the [Most Streamed Spotify Songs 2023](https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023) dataset — ~953 songs, 24 columns.

**Source URL (the tool loads this — a copy hosted in this course's own repo, so it won't move):**
```
https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/data/spotify_2023.csv
```

The `run_javascript` tool fetches the CSV and hands the agent a ready-to-use `data` array. The file lives in this repo at `_static/data/spotify_2023.csv`; the data originally comes from the Kaggle dataset linked above. To point the same workflow at any other dataset, change the `CSV_URL` inside the tool.

The columns fall into three groups:

| Group | Columns | Description |
|-------|---------|-------------|
| **Track info** | `track_name`, `artist(s)_name`, `artist_count`, `released_year`, `released_month`, `released_day` | Song identity and release date |
| **Platform metrics** | `in_spotify_playlists`, `in_spotify_charts`, `streams`, `in_apple_playlists`, `in_apple_charts`, `in_deezer_playlists`, `in_deezer_charts`, `in_shazam_charts` | Popularity across platforms |
| **Audio features** | `bpm`, `key`, `mode`, `danceability_%`, `valence_%`, `energy_%`, `acousticness_%`, `instrumentalness_%`, `liveness_%`, `speechiness_%` | Musical characteristics (0–100 scale) |

### Preview (first 5 rows)

| track_name | artist(s)_name | artist_count | released_year | streams | bpm | key | mode | danceability_% |
|---|---|---|---|---|---|---|---|---|
| Seven (feat. Latto) (Explicit Ver.) | Latto, Jung Kook | 2 | 2023 | 141381703 | 125 | B | Major | 80 |
| LALA | Myke Towers | 1 | 2023 | 133716286 | 92 | C# | Major | 71 |
| vampire | Olivia Rodrigo | 1 | 2023 | 140003974 | 138 | F | Major | 51 |
| Cruel Summer | Taylor Swift | 1 | 2019 | 800840817 | 170 | A | Major | 55 |
| WHERE SHE GOES | Bad Bunny | 1 | 2023 | 303236322 | 144 | A | Minor | 65 |

**Gotchas the agent must know (they go in the system prompt):**
- Every value in `data` is a **string** — even `streams` — so the agent must convert with `Number(...)` before doing math.
- Some keys have **special characters**: use bracket notation — `row['artist(s)_name']`, `row['danceability_%']`.
- `in_deezer_playlists` and `in_shazam_charts` may be empty.
- There is **no genre column** and **no song duration column** — the agent should say so instead of inventing one.

---

## The Workflow

One workflow, three nodes:

```
┌──────────────────────┐     ┌──────────────────┐     ┌──────────┐
│ When chat message    │────▶│ Data Analyst     │────▶│ Output   │
│ received             │     │ Agent            │     │          │
└──────────────────────┘     └──────────────────┘     └──────────┘
                                      ┊ sub-nodes
                             ┌────────┴────────┐
                             ┊                 ┊
                        Chat Model      run_javascript (Code Tool)
```

- **Chat Trigger** — the user types questions naturally
- **AI Agent** — turns the question into JavaScript, calls the tool, interprets the result, answers in plain English
- **run_javascript (Code Tool)** — the **code interpreter**: it **loads** the rows into a `data` array (a CSV here, for simplicity — a database query in real life), **runs** the JavaScript the agent wrote, and **returns** only what the code printed with `console.log()`

**File:** [`11_ask_your_data.json`](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/11_ask_your_data.json)

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/11_ask_your_data.json
> ```
>
> **Download:** {download}`11_ask_your_data.json <_static/workflows/11_ask_your_data.json>`

```{important}
The agent does **not** load or parse the data — the tool does that once and exposes a `data` array. The agent only writes the analysis. This removes a whole class of failures (file loading, encoding, CSV parsing) and lets the lesson stay on prompt engineering.
```

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

1. Click **Workflows** → **Add Workflow**
2. Rename it to "Ask Your Data (Spotify)"

### Step 2: Add the Chat Trigger

1. Add **Chat Trigger** (search for "When chat message received"). Tip: if you add an **AI Agent** node to an empty canvas first, n8n creates this trigger for you automatically.
2. In Options, set **Response Mode** to `When Last Node Finishes`

### Step 3: Add the AI Agent

1. Add **AI Agent** → rename to `Data Analyst Agent`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression): `{{ $json.chatInput }}`
   - Open **Options** → add **System Message** (paste the full prompt from the "Final System Prompt" section below)

### Step 4: Add the Chat Model (sub-node)

1. Click **+ Chat Model** at the bottom of the AI Agent node
2. Select **OpenRouter Chat Model** (or OpenAI, etc.)
3. Choose your credential and a current low-cost model (e.g. `openai/gpt-4o-mini`)

### Step 5: Add the Code Tool (the interpreter)

1. Click **+ Tool** at the bottom of the AI Agent node → select **Code Tool**
2. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `run_javascript` |
| **Description** | `Runs JavaScript to analyze the Spotify dataset. The dataset is already loaded as 'data' (an array of ~953 song objects). Write JS that computes the answer and prints it with console.log(). Returns whatever you console.log(). Do not fetch or load anything.` |
| **Language** | `JavaScript` |

3. Replace the JavaScript with this wrapper. It loads the CSV once, then runs the agent's code against the `data` array and returns the printed output:

```javascript
// run_javascript — a tiny code interpreter.
// The agent writes JavaScript; we run it over the Spotify data and return ONLY
// what the code prints with console.log(). Three real steps: LOAD, RUN, RETURN.

// 1) Get the code the agent wrote (it arrives in the variable `query`).
let code = (typeof query !== 'undefined' && query) ? String(query) : '';
if (!code) {
  try { const item = $input.first().json; code = item.query || item.code || item.input || ''; } catch (e) {}
}

// 2) LOAD THE DATA. For SIMPLICITY we download the CSV here and turn it into an
//    array of row objects called `data`. In a real project this step would be a
//    DATABASE QUERY instead — the idea is identical: get the rows, then run code.
const CSV_URL = 'https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/data/spotify_2023.csv';
const csvText = String(await this.helpers.httpRequest({ url: CSV_URL, json: false }));

function parseCSV(text) {
  const rows = [];
  let row = [], field = '', inQ = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQ) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') { inQ = false; }
      else { field += c; }
    } else {
      if (c === '"') { inQ = true; }
      else if (c === ',') { row.push(field); field = ''; }
      else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; }
      else if (c === '\r') { /* ignore */ }
      else { field += c; }
    }
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  return rows;
}

const matrix = parseCSV(csvText);
const headers = matrix[0];
const data = matrix.slice(1)
  .filter(r => r.length === headers.length)
  .map(r => { const o = {}; headers.forEach((h, i) => { o[h] = r[i]; }); return o; });

// 3) RUN the agent's code, capturing whatever it prints with console.log().
const logs = [];
const console = { log: (...a) => logs.push(a.map(x => (typeof x === 'object' ? JSON.stringify(x) : String(x))).join(' ')) };

try {
  eval(code);
} catch (e) {
  // The code failed. Instead of a bare error, hand the agent what it needs to
  // FIX ITSELF: the real column names and one sample row. This is the reflection
  // pattern — the agent reads this and rewrites its code on the next try.
  const keys = data.length ? Object.keys(data[0]) : [];
  return 'ERROR: ' + e.message +
    '\nAvailable columns: ' + keys.join(', ') +
    '\nSample row: ' + JSON.stringify(data[0]) +
    "\nReminder: all values are strings (use Number(...)); use bracket notation for keys with symbols, e.g. row['danceability_%'].";
}

return logs.length ? logs.join('\n') : '(no output — remember to console.log() your final answer)';
```

### Step 6: Add Output

1. Add **Edit Fields** → rename to `Output`
2. Add field: `output` (Expression) = `{{ $json.output }}`

### Step 7: Connect the main nodes

```
When chat message received → Data Analyst Agent → Output
```

### Step 8: Test

1. Click **Chat** in the workflow UI
2. Ask: "Which song has the most streams?"
3. Open the **Data Analyst Agent** → Logs to watch it write JavaScript, call the tool, and answer

::::

### Node-by-Node Walkthrough

| Node | Type | What it does |
|------|------|-------------|
| **When chat message received** | Chat Trigger | Receives the user's question via the chat UI |
| **Data Analyst Agent** | AI Agent | Writes JavaScript, calls the Code Tool, interprets the result |
| **Output** | Set | Saves `{{ $json.output }}` as `output` for the chat response |

**Sub-nodes (dotted lines to the Agent):**

| Sub-node | Type | Purpose |
|----------|------|--------|
| **OpenRouter Chat Model** | Chat Model | Provides the LLM |
| **run_javascript** | Code Tool | The interpreter: loads `data` once, runs the agent's JS, returns its `console.log` |

### Data Flow

```
INPUT                          AGENT ACTIONS                        OUTPUT
─────                          ─────────────                        ──────
Chat: { chatInput: "Which song has the most streams?" }
    ↓
Agent:
  1. Writes JavaScript:
     const top = data.reduce((m, r) => Number(r.streams) > Number(m.streams) ? r : m);
     console.log(`${top.track_name} by ${top['artist(s)_name']} — ${Number(top.streams).toLocaleString()} streams`);
  2. Calls run_javascript → the tool runs it against `data` → returns the printed line
  3. Interprets the result and writes a plain English answer
    ↓
Output: { output: "The most-streamed song is 'Blinding Lights' by The Weeknd, with ~3.7 billion streams." }
```

---

## The System Prompt

This is the core of the project. The system prompt is what makes the agent work — or fail. You'll iterate through three versions, testing each one, to see why each piece matters.

### V1: The Naive Prompt

Paste this into the agent's System Message and try the three test questions below:

```
You are a data analyst. Answer questions about Spotify data.
```

**Test questions for V1:**
1. "Which song has the most streams?"
2. "How many songs did Bad Bunny release?"
3. "What's the average BPM?"

**What you'll see go wrong:**
- The agent doesn't know the data is in a `data` array → it tries to fetch or invent data
- It guesses key names → uses `row.artist` instead of `row['artist(s)_name']`
- It treats `streams` as a number → wrong results (string comparison)
- It invents fields like `genre` or `duration` that don't exist

The agent has the interpreter but no context. It's like hiring an analyst and handing them an unlabeled spreadsheet.

### V2: Add the Schema

Tell the agent exactly what it's working with. Replace the system message and re-run the same three questions:

```
You are a data analyst. You answer questions about a Spotify dataset by writing JavaScript.

The dataset is already loaded as an array called `data` (~953 song objects). Write JS over `data` and print the answer with console.log().

Keys (all values are strings):
track_name, artist(s)_name, artist_count, released_year, released_month, released_day,
in_spotify_playlists, in_spotify_charts, streams, in_apple_playlists, in_apple_charts,
in_deezer_playlists, in_deezer_charts, in_shazam_charts, bpm, key, mode,
danceability_%, valence_%, energy_%, acousticness_%, instrumentalness_%, liveness_%, speechiness_%
```

**What improves:** the agent uses the real key names and prints with `console.log()`.

**What still breaks:** it forgets that values are strings (so `streams` math is wrong), forgets bracket notation for keys like `artist(s)_name`, and sometimes invents an answer for a missing field. Try "What's the most popular genre?" — it may make something up.

### V3: Add Sample Data + Rules

The final version adds three things:

1. **Sample data** — one real row so the agent sees the exact shape and that values are strings
2. **Explicit rules** — convert with `Number()`, bracket notation, say-so-if-missing
3. **Output format** — always `console.log()` a readable sentence

Replace the system message one more time and re-run all three questions, plus "What's the most popular genre?". This is the version that works.

---

### Final System Prompt

This is the exact system message used in the workflow.

**Data Analyst Agent — System Message:**
```
You are a data analyst. You answer questions about a Spotify dataset by writing JavaScript.

You have one tool: run_javascript. The dataset is ALREADY loaded inside it as a variable `data` — an array of ~953 song objects. You do NOT load any file or fetch anything. You write JavaScript that analyzes `data` and prints the answer with console.log().

## The `data` array
Each element is an object. ALL values are strings — convert numbers with Number(...). Keys:
- track_name, artist(s)_name, artist_count, released_year, released_month, released_day
- in_spotify_playlists, in_spotify_charts, streams  (streams is a large number stored as a string)
- in_apple_playlists, in_apple_charts, in_deezer_playlists, in_deezer_charts, in_shazam_charts
- bpm, key, mode, danceability_%, valence_%, energy_%, acousticness_%, instrumentalness_%, liveness_%, speechiness_%

Use bracket notation for keys with special characters: row['artist(s)_name'], row['danceability_%'].

## Sample (first row)
{ "track_name": "Seven (feat. Latto) (Explicit Ver.)", "artist(s)_name": "Latto, Jung Kook", "artist_count": "2", "released_year": "2023", "streams": "141381703", "bpm": "125", "key": "B", "mode": "Major", "danceability_%": "80" }

## Rules
1. All values are strings — convert with Number(row['streams']) before doing math.
2. Use bracket notation for keys with special characters: row['artist(s)_name'], row['danceability_%'].
3. ALWAYS print the final answer with console.log() as a short, readable sentence — never the raw array.
4. If a question cannot be answered with these fields, say so clearly (there is no genre column and no song-duration column).
5. Keep the code simple and correct. Do NOT fetch anything — `data` is already loaded.
```

### Verify it works

After pasting the final prompt, click **Chat** and ask: "Which song has the most streams?"

Check these in the n8n UI:
1. Click **Data Analyst Agent** → expand the execution details
2. You should see the **JavaScript** the agent generated (the `run_javascript` tool call)
3. You should see the **printed output** returned from the tool
4. The chat should show a **plain English answer**, not raw code or an array

If you see all four, the workflow is working correctly.

### Key Takeaway

The system prompt went from 1 line to ~25. Each addition fixed a real failure mode:

| What we added | What it fixed |
|---------------|---------------|
| "`data` array is already loaded" | Agent stopped trying to fetch/invent data |
| Key list | Agent used the right field names |
| "all values are strings" + `Number()` | Agent stopped doing string math on `streams` |
| Sample row | Agent saw the exact shape and types |
| Bracket-notation rule | Fixed keys like `artist(s)_name`, `danceability_%` |
| "say so clearly" rule | Agent stops inventing answers for missing fields |
| `console.log()` rule | Agent returns a readable answer, not a raw array |

**The system prompt IS the engineering.** The workflow itself is just three nodes.

---

## Example Questions

Try these in the chat to see the agent in action. They're ordered by difficulty.

### Simple Lookups

| Question | What the agent does |
|----------|--------------------|
| "Which song has the most streams?" | Converts `streams` to numeric, finds the max, returns track name + artist |
| "How many songs did Bad Bunny release?" | Filters `artist(s)_name` containing "Bad Bunny", counts rows |
| "List all songs released in January 2023" | Filters by `released_year == 2023` and `released_month == 1` |

### Aggregations

| Question | What the agent does |
|----------|--------------------|
| "What's the average BPM of songs in Major vs Minor mode?" | Groups by `mode`, computes `bpm.mean()` |
| "Which artist appears most often in the dataset?" | Splits `artist(s)_name` by comma, counts occurrences |
| "What's the average danceability of the top 50 most-streamed songs?" | Sorts by streams, takes top 50, computes mean of `danceability_%` |

### Interesting Analysis

| Question | What the agent does |
|----------|--------------------|
| "Is there a correlation between danceability and streams?" | Computes correlation coefficient between `danceability_%` and `streams` |
| "What month has the most song releases?" | Groups by `released_month`, counts, finds the max |
| "Show me the top 5 most energetic songs with low acousticness" | Filters `acousticness_% < 20`, sorts by `energy_%`, takes top 5 |

### Edge Cases (things that fail or need creativity)

| Question | What should happen |
|----------|-------------------|
| "What's the most popular genre?" | No `genre` column — the agent should say so |
| "How long is the average song?" | No `duration` column — the agent should recognize this |
| "Which song was #1 on Spotify?" | The `in_spotify_charts` column doesn't directly mean rank #1 — needs interpretation |
| "Compare Taylor Swift and Drake" | Requires filtering by artist name (substring match), then comparing metrics |

---

## What to Observe + Key Takeaways

After running several questions, here's what to notice:

**1. The system prompt is 80% of the work**

The workflow is just three nodes. All the intelligence comes from the system prompt — the schema, the sample data, the rules. If you change the dataset, you only need to update the prompt.

**2. Schema + sample data > long instructions**

Showing the agent 5 rows of real data teaches it more than paragraphs of instructions. The agent sees data types, value ranges, and formatting issues directly.

**3. The agent retries on errors**

If the generated code crashes (e.g., wrong column name), the agent sees the error message and writes corrected code. This is the reflection pattern from the Reflection Pattern chapter — happening naturally inside the agent loop.

**4. Some questions can't be answered**

A good agent says "I can't answer that with this data" instead of making something up. The rule "say so clearly" in the system prompt makes this reliable.

**5. This pattern works with ANY CSV**

The workflow is generic. Swap the CSV URL, update the schema and sample data in the system prompt, and you have a data analyst for any dataset.

---

## Try It Yourself

### Challenge 1: Use Your Own Data

1. Find a CSV dataset you care about (Kaggle is a good source)
2. Host it at a public URL (or a raw GitHub link)
3. In the `run_javascript` tool, change `CSV_URL` to your file
4. Update the system prompt: the key list, the sample row, and the rules for your data's quirks
5. Test with progressively harder questions

### Challenge 2: Multi-Dataset Agent

Give the tool a **second** CSV (e.g. a 2024 Spotify dataset) — load both into `data2023` and `data2024`. Update the system prompt to describe both, then ask questions that span them:
- "Which artists appear in both the 2023 and 2024 datasets?"
- "How did average BPM change between 2023 and 2024?"

### Challenge 3: Add Guardrails

The interpreter runs whatever JavaScript the agent writes — a real risk. Add rules to the system prompt (and, for real safety, checks in the tool wrapper) to keep the agent to analysis only:
- No network calls beyond the dataset that's already loaded
- No writing files or touching the workflow's other data
- Only read and compute over `data`

This connects back to the **Guardrails & Safety** chapter: the system prompt is one layer; a deterministic check in the wrapper (e.g. reject code containing `import`, `require`, `fetch`) is the stronger one.

### Challenge 4: Better Error Messages

When the agent's code throws, the tool returns the error text. Add a rule to the system prompt: "If your code errors, read the message, fix the code, and try again — don't give up after one attempt." Compare how the agent behaves with and without this rule (this is the reflection loop, happening inside the agent).
