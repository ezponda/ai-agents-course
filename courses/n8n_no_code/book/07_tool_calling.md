# Tool Calling: Extending What Agents Can Do

In the previous chapter, you built AI agents that used tools like Calculator and Wikipedia. The agent decided *when* to call each tool based on the user's question. This chapter goes deeper: how do tools actually work, how do you design them well, and how do you keep agents safe?

**What you'll learn:**
- How tool calling works under the hood
- The critical difference between read-only and write tools
- How to write tool descriptions that actually work
- How to use the HTTP Request Tool to call any API with `$fromAI()`
- Guardrails to prevent agents from causing problems
- How to build a complete trip-briefing agent that picks the right tool and ends with human approval

---

## How Tool Calling Works

When you connect tools to an AI Agent node, you're giving the model a menu of capabilities. The model doesn't execute tools directly—it *requests* that a tool be called, and n8n executes it.

### The Loop

This is the same agent loop from the First AI Agent chapter: **Reason → Call Tool → Observe → Repeat or Answer** (also called the **ReAct pattern**).

1. **Reason** — The model reads the user's question and its available tools
2. **Call Tool** — The model outputs which tool to call and with what inputs
3. **Observe** — n8n executes the tool and returns the result to the model
4. **Repeat or Answer** — The model decides if it needs more tools or can answer

### Why It Matters

The model chooses tools based on:
- The **tool name** and **description** you provide
- The **user's question**
- The **system message** instructions

If any of these are unclear, the model may call the wrong tool, call no tool, or hallucinate an answer instead of looking it up.

---

## How the Agent Picks a Tool

When you connect tools to an AI Agent, n8n collects all their descriptions and sends them to the LLM. The model then decides which tool to use—you don't write "if user asks X, use tool Y" logic.

**What the model uses to decide:**

- **Tool descriptions** — What each tool does (the main signal)
- **Tool names** — Short identifiers like `wikipedia`, `calculator`
- **User's question** — What they're asking for
- **System Message** — Extra rules you add (optional)

### What a Tool Looks Like

Every tool has a name, a description, inputs, and outputs:

| Part | Example (Wikipedia) |
|------|---------------------|
| **Name** | `wikipedia` |
| **Description** | "Search Wikipedia for factual information" |
| **Inputs** | `query` (string) |
| **Outputs** | Article text or summary |

The **description** is the most important part—it tells the model when to use the tool.

### Where Descriptions Come From

| Tool type | Description | You write it? |
|-----------|-------------|---------------|
| Built-in (Wikipedia, Calculator) | Hardcoded in the node | No |
| Custom (HTTP Request Tool, Workflow Tool) | Field in the tool's settings | Yes |

```{tip}
For built-in tools, the descriptions are hidden in the code. n8n is open source, so you can see them: [n8n tool source code](https://github.com/n8n-io/n8n/tree/master/packages/%40n8n/nodes-langchain/nodes/tools).

Wikipedia's description is: *"A tool for interacting with and fetching data from the Wikipedia API."*
```

### The System Message: Extra Rules, Not Descriptions

The System Message is for *additional rules*, not for describing tools. Use it when:

- You want to prioritize one tool: *"Always try Wikipedia first"*
- You need to limit usage: *"Call each tool at most twice"*
- You want to prevent actions: *"Never send emails without asking"*

If your tools have clear descriptions, the agent will usually pick correctly without extra help.

---

## Read-Only vs Write Tools

This is the most important distinction in tool design:

| Type | What it does | Risk | Default policy |
|------|--------------|------|----------------|
| **Read-only** | Fetches or calculates data | Low | Allow freely |
| **Write** | Changes something in the real world | High | Require approval |

### Read-Only Tools (Safe)

- Wikipedia lookup
- Calculator
- Weather API
- Database query (SELECT only)
- Web search

These tools only *read* information. If the agent calls them incorrectly, nothing bad happens—you just get wrong or irrelevant data.

### Write Tools (Dangerous)

- Send email
- Create ticket
- Update database
- Post to social media
- Delete file

These tools *change* something. If the agent calls them incorrectly, you could send embarrassing emails, create duplicate tickets, or lose data.

### The Golden Rule

> **If a tool changes something in the real world, it needs human approval before executing.**

### Principle of Least Privilege

Give agents only the tools they need:
- A research assistant only needs read-only tools
- A customer support agent might need write tools, but with approval gates

Start minimal. Add more tools only when necessary.

```{note}
**What if you have many tools?**

This course uses 2-3 tools per agent. In production systems with 10+ tools, new challenges appear: the agent may pick the wrong tool, calls become slow and expensive, or tools from different domains interfere with each other.

Common solutions:
- **Tool Search**: Retrieve only relevant tools per request (instead of loading all 50)
- **Programmatic Tool Calling**: Agent writes code that calls multiple tools in batch, returns only the result
- **Universal Code Runner**: One powerful Code node instead of many small tools (n8n's Code node is exactly this)
- **Router → Specialists**: Split into multiple focused agents (e.g., Support Agent, Billing Agent) with isolated tool sets — this is the [Multi-Agent Systems](10_multi_agent_systems) chapter
- **Tool Use Examples**: Add example calls inside tool descriptions to improve parameter accuracy

For implementation details, see [Anthropic's Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use).
```

---

## Writing Good Descriptions

For custom tools (HTTP Request Tool, Workflow Tool), you write the description in the **tool node's Description field**—not in the System Message.

A good description tells the model *when* to use the tool and *when not to*:

```
Use this tool when [specific situation].
Do NOT use when [counter-situation].
Input: [what it needs]
Output: [what it returns]
```

```{tip}
**Write it for a new hire.** Anthropic's guidance is blunt: *"Provide extremely detailed descriptions. This is by far the most important factor in tool performance."* Aim for **3-4 sentences** and describe the tool the way you'd explain it to a new teammate — what it does, when to use it, when **not** to, and what goes in and out.

**The boundary test:** if you can't say in one sentence *why the agent would pick tool A over tool B*, their descriptions overlap and the agent will guess. Sharpen them until the boundary is obvious.
```

### Examples

**Bad description:**
```
Searches Wikipedia.
```

**Good description (in the tool's Description field):**
```
Use when the user asks about facts: people, places, historical events.
Do NOT use for opinions or recent news.
Input: search query (string)
Output: article summary
```

**Bad description:**
```
Sends an email.
```

**Good description:**
```
Use ONLY when user explicitly asks to send a message.
Do NOT use to "draft" or "prepare" — ask first if unsure.
Input: recipient, subject, body
WARNING: Cannot be undone.
```

### Test Your Descriptions

If the agent picks the wrong tool, improve the description—don't add complex logic to the System Message.

| Prompt | Expected tool |
|--------|---------------|
| "Who invented the telephone?" | Wikipedia |
| "What's 15% of 340?" | Calculator |
| "Send a thank-you email to John" | Send Email |
| "Help me write an email" | Draft Email (not Send) |

## HTTP Request Tool: Calling Any API

The built-in tools (Wikipedia, Calculator, SerpAPI) cover common tasks. But what if you need to call a recipe database, a weather service, or your company's internal API?

The **HTTP Request Tool** is an AI tool sub-node that lets agents call any URL. Unlike the regular HTTP Request node (which runs once in a fixed workflow), the HTTP Request Tool is **controlled by the agent** — the agent decides *when* to call it and *what values to fill in*.

### Configuration

| Setting | Purpose |
|---------|---------|
| **Name** | Short identifier the agent sees (e.g., `Recipe Search`) |
| **Description** | When to use it and what it returns — **this is the most important part** |
| **Method** | GET, POST, etc. |
| **URL** | The API endpoint |
| **Query Parameters** | Dynamic values the agent fills in using `$fromAI()` |

### How `$fromAI()` Works

`$fromAI()` is a special function that tells the AI model: "you need to provide a value for this parameter." You use it inside query parameter values (or headers, body fields) to make them dynamic.

**Example:** To search an API by keyword, set up a query parameter with key `q` and value:

```
{{ $fromAI('query', 'The search term', 'string') }}
```

The agent reads this definition, looks at the user's question, and decides what value to fill in. If the user asks "I want chicken recipes", the agent fills `query` with `chicken`, producing:

```
GET https://api.example.com/search?q=chicken
```

The function takes three arguments:

| Argument | Meaning | Example |
|----------|---------|---------|
| `key` | Parameter name (the agent sees this) | `'query'` |
| `description` | What value to provide | `'A simple keyword like chicken or pasta'` |
| `type` | Data type | `'string'`, `'number'`, `'boolean'`, `'json'` |

### The ✨ Button

The easiest way to add `$fromAI()` is with the **✨ button**. Hover over a parameter's value field — a small sparkle icon appears. Click it, and n8n generates the `$fromAI()` expression for you. Then edit the description so the agent knows what to provide.

### Writing Descriptions for HTTP Tools

The same rules from the previous section apply. The description should tell the agent *when* to call the API and *what it returns*:

**Bad:**
```
Searches for recipes.
```

**Good:**
```
Search for recipes by name or ingredient on TheMealDB.
Input: a simple English search term like 'chicken' or 'pasta'.
Returns recipe details including name, ingredients, and instructions.
If the response contains meals:null, no recipes were found.
```

```{tip}
You'll build a complete HTTP Request Tool workflow in **Project 1: Recipe Assistant**, connecting an agent to a real recipe API with a fallback search strategy.
```

::::{dropdown} 🛠️ Try it: how much does the `$fromAI` description matter?
:color: secondary

The `description` you give `$fromAI()` is the same idea as a tool description — it tells the model what to put in that slot. Try the three states on an HTTP Request Tool (here a weather tool calling `https://wttr.in/<city>?format=j1`) and watch what the agent sends, in the agent's **Logs**:

**1. Described (recommended)** — the model fills it cleanly, even from "¿qué tiempo hace en Lisboa?" → `Lisbon`:
```
https://wttr.in/{{ $fromAI('city', 'The destination city in English, e.g. Lisbon or Paris', 'string') }}
```

**2. Bare placeholder (you do the work in the System Message)** — no description on the parameter:
```
https://wttr.in/{{ $fromAI('query') }}
```
Then add a rule to the agent's System Message:
```
When you call get_weather, pass ONLY the destination city name in English — no extra words, no "weather in", just the city (e.g. "Lisbon").
```
It works, but it's more fragile: sometimes the model sends "weather in Lisbon" and the URL breaks.

**3. Removed (a fixed call)** — delete `$fromAI` and hardcode the city:
```
https://wttr.in/Lisbon
```
Now the agent **can't change the city** — it always returns Lisbon. This is no longer agentic; it's a plain, fixed request.

**Takeaway:** describing the parameter (state 1) moves the work from your prompt into the tool, where the model handles it reliably — exactly like writing a good tool description. State 2 still works but leans on the system prompt; state 3 stops being agentic. The parameter's description is doing real work.
::::

---

## Guardrails

Even with good descriptions, agents can misbehave. The Guardrails & Safety chapter covers this topic in depth. Here are the essentials:

- **Max Iterations:** Set to 5-10 in AI Agent → Settings (gear icon). Prevents infinite loops.
- **System Message rules:** Add explicit limits like "Call Wikipedia at most twice per question" and "If a tool fails, explain the error and stop."
- **Approval gates:** For write tools (send email, create ticket), add a **Wait node** before the action so a human reviews the output first.

### Principle of Least Privilege

Give agents only the tools they need:
- A research assistant only needs read-only tools
- A customer support agent might need write tools, but with approval gates

Start minimal. Add more tools only when necessary.

---

## Putting It Together: Trip Briefing Agent

This workflow demonstrates everything we've learned in one place:
- An agent that **calls a real API** with the HTTP Request Tool (`get_weather`)
- An agent that **picks the right tool** between similar ones (Wikipedia for stable facts vs Google Search for current info)
- All tools **read-only**, plus an **approval gate** before the brief could be sent

**The idea:** you give the agent a destination and it prepares a short trip brief — the weather, a couple of must-see sights, and anything happening right now — then a human approves it.

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Manual Trigger  │────▶│  Input: Request  │────▶│   AI Agent       │
└──────────────────┘     └──────────────────┘     │ (Trip Briefing)  │
                                                  └──────────────────┘
                                                          │
                          ┌───────────────────┬───────────┴───────────┐
                          │                   │                       │
                    [get_weather]        [Wikipedia]            [Google Search]
                   (HTTP, $fromAI)     (stable facts)         (current info)
                          │
                          ▼
                ┌──────────────────┐
                │  ⏸️ WAIT for     │
                │    Approval      │
                └──────────────────┘
                          │
                    Human approves
                          │
                          ▼
                ┌──────────────────┐
                │  Output: brief    │
                │  (approved)       │
                └──────────────────┘
```

### The Mission

1. User names a destination
2. Agent gets the **weather** (live API, via `get_weather`)
3. Agent looks up **stable facts** (main sights) with Wikipedia
4. Agent searches **current info** (events this week) with Google Search
5. **Human reviews and approves** the brief

**Note:** This workflow stops at approval. In production, after the Wait you would connect a real send action (e.g., email or chat). The pattern is always: AI prepares → human approves → system sends.

---

### Import the Workflow

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/09_tool_calling_trip_briefing.json
> ```
>
> **Download:** {download}`09_tool_calling_trip_briefing.json <_static/workflows/09_tool_calling_trip_briefing.json>`

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create the workflow

1. Click **Workflows** → **Add Workflow**
2. Rename to "Trip Briefing Agent"

### Step 2: Add trigger and input

1. Add **Manual Trigger** → rename to `Run: Trip Briefing`
2. Add **Edit Fields** → rename to `Input — Trip Request`
3. Add one field:

| Name | Value |
|------|-------|
| `request` | `I'm visiting Lisbon this weekend. Give me a short trip brief: the weather, a couple of must-see sights, and anything happening right now.` |

### Step 3: Add the AI Agent

1. Add **AI Agent** → rename to `Trip Briefing Agent`
2. Set **Source for Prompt** to `Define below`, and **Prompt** (Expression mode): `{{ $json.request }}`
3. In **Options**, set the **System Message**:
   ```
   You are a Trip Briefing assistant. The user names a destination (and sometimes dates) and you prepare a short, practical trip brief.

   You have three tools:
   - get_weather: live weather for a city. Use it whenever the user wants the weather or what to pack.
   - Wikipedia: established background facts (history, main sights, geography) that rarely change. Use it for general "tell me about" knowledge.
   - Google Search: current, time-sensitive info (events this week, opening hours, ticket prices, recent news). Use it when the answer depends on what is happening NOW.

   Rules:
   - Choose the RIGHT tool: stable facts -> Wikipedia; current/this-week info -> Google Search; weather -> get_weather.
   - Do NOT invent opening hours, prices or dates. If it is time-sensitive, search.
   - Final answer: a short brief of 4-6 bullets (weather, 2-3 things to see, 1 current tip).
   ```
4. In **Options**, set **Max Iterations** to `8`.

```{note}
Since n8n **v1.82** the AI Agent has a single type — the **Tools Agent** — and it requires **at least one tool** connected. If an older tutorial tells you to pick an "agent type", that menu no longer exists.
```

### Step 4: Add the Chat Model and the tools

1. **+ Chat Model** → **OpenRouter Chat Model** → choose your credential and a current low-cost model
2. **+ Tool** → **HTTP Request** → rename it to `get_weather`, and configure:
   - **Description** (this is what the model reads):
     ```
     Get the current weather for a city. Input: the destination city name in English (for example "Lisbon"). Returns temperature, conditions, humidity and wind. Use this when the user asks about the weather or what to pack. Do NOT use it for opening hours, events, prices or general facts.
     ```
   - **Method**: `GET`
   - **URL** (Expression — use the ✨ button to insert `$fromAI`):
     ```
     https://wttr.in/{{ $fromAI('city', 'The destination city name in English, e.g. Lisbon or Paris', 'string') }}
     ```
   - **Send Query Parameters**: ON → add `format` = `j1`
   - **Optimize Response**: ON
3. **+ Tool** → **Wikipedia** (no credentials)
4. **+ Tool** → **SerpAPI** → rename it to `Google Search` (free key at [serpapi.com](https://serpapi.com))

### Step 5: Add the approval gate

1. Add **Wait** → rename to `Wait — Approval`
2. Set **Resume**: `On Webhook Call`
3. In Options, set **Webhook Suffix**: `{{ $execution.id }}`

### Step 6: Add the output

1. Add **Edit Fields** → rename to `Output — Approved`
2. Add two fields:

| Name | Value |
|------|-------|
| `trip_brief` | `{{ $('Trip Briefing Agent').item.json.output }}` |
| `status` | `approved` |

3. Enable **Keep Only Set**

### Step 7: Test

1. Click **Execute Workflow**
2. Open the **Trip Briefing Agent** node → **Logs** to see which tool it chose and with what input
3. The run **pauses** at `Wait — Approval` → click the node, copy the **Test URL**, open it to approve

::::

### What's in the Workflow

| Node | What it does |
|------|-------------|
| **Run: Trip Briefing** | Manual Trigger — starts the workflow |
| **Input — Trip Request** | Provides the destination request |
| **Trip Briefing Agent** | Chooses tools and writes the brief |
| **get_weather** | HTTP Request Tool → live weather (wttr.in), city filled by `$fromAI` |
| **Wikipedia** | Stable background facts (read-only) |
| **Google Search** | Current, time-sensitive info via SerpAPI (read-only) |
| **Wait — Approval** | Pauses until a human approves |
| **Output — Approved** | The final brief, marked `approved` |

### Test It

Try requests that force the agent to pick different tools:

| Request | What happens |
|---------|-------------|
| `What's the weather in Lisbon this weekend?` | `get_weather` only |
| `Tell me about the history of the Belém Tower` | Wikipedia (stable fact) |
| `What concerts are on in Lisbon this weekend?` | Google Search (current info) |
| `Trip brief for Lisbon this weekend` | all three tools |

### The Key Pattern

```
User request → Agent picks tools (read-only) → Brief created → WAIT → Human approves → Ready to send
```

The agent researches freely because every tool is read-only. The brief is gated behind the Wait node before it could be sent. In production you'd connect a real send action after approval.

```{note}
**Native approval (newer n8n).** This workflow gates the *whole brief* with a Wait node — simple and credential-free. Recent n8n versions also offer a **Human review** step directly on a tool's connector: when a review-enabled tool is called, the run pauses and asks you to approve or deny that specific tool call (via Slack, Telegram, Gmail, etc.). Use the per-tool review when only *some* actions are risky; use the Wait gate when you want to approve the final result.
```

---

## Debugging Tool Calls

When tools don't work as expected, check these in order:

| Problem | What to check | Fix |
|---------|---------------|-----|
| Agent doesn't use any tool | Is the description clear? | Add "Use this tool when..." |
| Agent uses wrong tool | Are descriptions overlapping? | Add "Do NOT use when..." |
| Agent calls tool repeatedly | Is it getting useful results? | Check tool output, improve query |
| Agent ignores tool output | Is system message too restrictive? | Adjust instructions |
| Tool returns error | Are credentials set up? | Check Settings → Credentials |

### Debug Checklist

1. **Click the Agent node** → look at the "Steps" in the output panel
2. **Check which tools were called** and with what inputs
3. **Read the tool outputs** — did they return useful data?
4. **Look at the final answer** — did the agent use the tool output?

---

## MCP: Connecting to External Tool Servers (Optional)

**MCP** (Model Context Protocol) is a standard for connecting AI agents to external tools. Instead of building tools inside n8n, you can connect to tools hosted elsewhere.

n8n has native MCP support with three nodes:

| Node | What it does |
|------|-------------|
| **MCP Client Tool** | Connect your AI Agent to tools from an external MCP server |
| **MCP Client** | Use MCP tools in regular workflows (not agents) |
| **MCP Server Trigger** | Expose your n8n workflows as tools for other MCP clients |

### When to Use MCP

- You want to use tools from services like Notion, Slack, or custom APIs that provide MCP endpoints
- You want to expose your n8n workflows as tools for Claude Desktop, Cursor, or other MCP clients
- You're building a system where multiple AI applications share the same tools

### Example: Connecting to an MCP Server

1. Add **MCP Client Tool** as a sub-node to your AI Agent
2. Configure the **SSE Endpoint** URL of the MCP server
3. Set authentication if required
4. Choose which tools to expose to the agent (All or Selected)

The agent can now use tools from that external server.

```{note}
MCP is powerful but adds complexity. For this course, the built-in tools (Wikipedia, Calculator, HTTP Request) are sufficient. Explore MCP when you need tools that aren't available natively in n8n.

**Learn more:** [n8n MCP Documentation](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolmcp/)
```

---

## Summary

| Concept | Key Point |
|---------|----------|
| **Tool calling** | Model requests tools; n8n executes them |
| **ReAct loop** | Reason → Call Tool → Observe → Repeat or Answer |
| **Read-only tools** | Safe to use freely (Wikipedia, Calculator) |
| **Write tools** | Need human approval (send email, create ticket) |
| **Descriptions** | "Use when... / Do NOT use when..." format |
| **HTTP Request Tool** | Call any API with `$fromAI()` — the agent fills in parameter values at runtime |
| **Guardrails** | Max iterations, system message rules, approval gates |
| **MCP** | Standard for connecting to external tool servers |

---

## Next Steps

The **Guardrails & Safety** chapter goes deeper into safety patterns, including input validation, output filtering, and comprehensive safety checklists for production agents.

The **Node Toolbox** appendix provides reference documentation for all nodes covered in this course.
