# Appendix A: Node Toolbox

This chapter is a **reference guide** for the core nodes used in AI workflows. 

**How to use this chapter:**
- Don't read it cover-to-cover
- Come back here when you need details about a specific node
- Use it alongside the Workflow Examples and AI Agent Examples chapters

For each node, you will find:
- What problem it solves
- Key parameters to understand
- What the output looks like
- Common mistakes to avoid

---

## 1. Manual Trigger

**What it solves:** Starts the workflow when you click "Execute Workflow" in the editor.

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| (none) | Manual Trigger has no configuration |

### Output

An empty item: `{ }`

This is normal. Triggers start the flow but do not produce data. The next node (usually Set/Edit Fields) creates the initial data.

### Common Mistake

**Expecting data from the trigger.** Manual Trigger outputs an empty object. Use Edit Fields to create your input data.

**Docs:** [Manual Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.manualworkflowtrigger/)

---

## 1b. Chat Trigger (Optional)

**What it solves:** Provides a chat interface for conversational workflows. Use it when you want multi-turn conversations instead of single executions.

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Public** | Whether the chat is accessible without authentication |
| **Initial Messages** | Welcome messages shown when chat opens |

### Output

The user's message appears in the `chatInput` field:

```json
{ "chatInput": "What is the capital of France?" }
```

**Note:** When Chat Trigger connects to an AI Agent, the agent's response appears in the `output` field (not `text`). See the Expression Cheat Sheet at the end of this appendix for the full list of AI node output field names.

### Connection Requirement

Chat Trigger must connect directly to a root AI node (AI Agent or LLM Chain). It cannot connect to a Set node first.

### Common Mistake

**Connecting to the wrong node.** Chat Trigger needs a direct connection to an agent or chain node for the chat interface to work.

**Docs:** [Chat Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.chattrigger/)

---

## 2. Edit Fields (Set)

**What it solves:** Creates, renames, or modifies data fields. Use it to define input data or save intermediate results.

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Name** | The field name to create or modify |
| **Value** | Fixed text or an expression like `{{ $json.text }}` |
| **Type** | String, Number, Boolean (usually String) |
| **Keep Only Set** | When ON, removes all other fields |

### Fixed vs Expression

| Mode | When to use |
|------|-------------|
| **Fixed** | Type a literal value (e.g., `AI in healthcare`) |
| **Expression** | Reference data from another node (e.g., `{{ $json.text }}`) |

### Output

Items with your fields added. Example:

- **Input:** `{ }`
- **Configuration:** Set `topic` = "AI in healthcare"
- **Output:** `{ "topic": "AI in healthcare" }`

### Common Mistake

**Accidentally enabling "Keep Only Set."** This removes all previous fields. Only enable it when you explicitly want to reset the data.

**Docs:** [Edit Fields (Set) Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.set/)

---

## 3. Chat Model Provider

**What it solves:** Provides an AI model (the "brain") for LLM Chain nodes to use. It does not process data directly.

### Available Providers

| Provider | Node Name | What it offers |
|----------|-----------|----------------|
| **OpenRouter** | OpenRouter Chat Model | Access to many models via one API (recommended) |
| **OpenAI** | OpenAI Chat Model | GPT-4, GPT-3.5, etc. |
| **Google Gemini** | Google Gemini Chat Model | Gemini models (free tier available but limited) |

### Option 1: OpenRouter (Recommended)

OpenRouter gives you access to 400+ models with one API key. Sign up at [openrouter.ai](https://openrouter.ai/) — no credit card required for free models.

**Free models (no cost):**

| Model | ID in OpenRouter | Best for |
|-------|------------------|----------|
| DeepSeek V3 | `deepseek/deepseek-chat-v3-0324:free` | General use, coding |
| DeepSeek R1 | `deepseek/deepseek-r1-zero:free` | Reasoning tasks |
| Llama 4 Maverick | `meta-llama/llama-4-maverick:free` | General use |

**Fast & cheap (pay per use):**

| Model | ID in OpenRouter | Price per 1M tokens |
|-------|------------------|---------------------|
| DeepSeek V3 | `deepseek/deepseek-chat` | $0.25 / $0.38 |
| GPT-4o Mini | `openai/gpt-4o-mini` | $0.15 / $0.60 |
| Claude Haiku 3.5 | `anthropic/claude-3.5-haiku` | $0.80 / $4.00 |

**Most powerful:**

| Model | ID in OpenRouter | Price per 1M tokens |
|-------|------------------|---------------------|
| Claude Opus 4.5 | `anthropic/claude-opus-4.5` | $15 / $75 |
| Claude Sonnet 4 | `anthropic/claude-sonnet-4` | $3 / $15 |
| GPT-4o | `openai/gpt-4o` | $2.50 / $10 |

**Tip:** Start with `deepseek/deepseek-chat-v3-0324:free` for learning — it's free and has no strict rate limits.

### Option 2: Google AI Studio (Free but limited)

Google offers free access but with strict daily limits (20-50 requests/day as of January 2026).

| Model | ID in n8n | Best for |
|-------|-----------|----------|
| Flash Lite | `models/gemini-flash-lite-latest` | Highest free quota |
| Flash | `models/gemini-flash-latest` | Better quality |

**How to get your free API key:**

1. Go to [aistudio.google.com](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click **Get API Key** → **Create API Key**
4. Copy the key and use it in n8n

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Credential** | Your API key (stored in Credentials) |
| **Model** | Which model to use (copy ID from tables above) |
| **Temperature** | Creativity: 0 = focused, 1 = creative (optional) |
| **Max Tokens** | Maximum response length (optional) |

### Connection Type

Chat Model nodes connect with a **dotted line** to LLM Chain nodes. This indicates a capability relationship, not data flow.

One Chat Model can serve multiple LLM Chain nodes.

### Output

None visible. The model is used by connected LLM Chain nodes.

### Common Mistake

**"No credentials" error.** Create a credential with your API key before using this node. Go to the node, click the credential dropdown, and select "Create New Credential."

**Docs:** [AI and LLM Nodes Overview](https://docs.n8n.io/integrations/builtin/cluster-nodes/)

---

## 4. Basic LLM Chain

**What it solves:** Sends a prompt to an AI model and returns the response. This is the core "AI call" in your workflow.

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Source for Prompt** | Where the prompt comes from (see below) |
| **Prompt (User Message)** | The prompt — what you want the AI to do |
| **Chat Model** | Connection to a Chat Model provider (dotted line) |

### Source for Prompt (Important)

This dropdown controls where the node gets the user's message:

| Setting | When to use |
|---------|-------------|
| **Define below** | Most workflows (Manual Trigger, webhooks, Edit Fields) |
| **Connected Chat Trigger Node** | Only when a Chat Trigger is directly connected |

**Common error:** If you import a workflow and see **"No prompt specified"**, change this setting to **"Define below"**.

### System Message vs User Message

Configure these in the **Chat Messages** section at the bottom of the node:

| Field | What goes here | Example |
|-------|----------------|--------|
| **System** | How the AI should behave | "You are a professional editor. Be concise." |
| **User** | What you want done (can also use Prompt field above) | "Summarize this: {{ $json.article }}" |

### Output

The AI response appears in a field called `text`:

```json
{ "text": "Here is the summary..." }
```

Use `{{ $json.text }}` in the next node to access this response.

### Common Mistakes

**"No prompt specified" error.** The "Source for Prompt" is set to "Connected Chat Trigger Node" but no Chat Trigger exists. Change it to "Define below".

**Forgetting to connect a Chat Model.** The node fails without a model. Check for the dotted line connection.

**Docs:** [Basic LLM Chain](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.chainllm/)

---

## 5. Switch

**What it solves:** Routes data to different branches based on conditions. Think of it as if/else logic.

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Value** | The field to check (e.g., `{{ $json.route }}`) |
| **Operation** | How to compare: Equals, Contains, etc. |
| **Rules** | List of conditions, each leading to an output branch |
| **Fallback Output** | Where data goes if no rules match |

### How Routing Works

1. An LLM classifies input and outputs a label (e.g., `refund`, `support`)
2. A Set node stores that label in a field called `route`
3. The Switch node checks `{{ $json.route }}` against rules:
   - If equals `refund` → Output 1
   - If equals `support` → Output 2
   - Fallback → Output 3

### Output

Data goes to **only one branch** — the first rule that matches. Other branches show empty output.

### Common Mistake

**Case sensitivity.** If the LLM outputs `Refund` but your rule checks for `refund`, it will not match.

**Docs:** [Switch Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.switch/)

---

## 6. Merge

**What it solves:** Combines data from multiple input branches into a single output.

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Mode** | How to combine inputs (see table below) |

### Combine Modes

| Mode | What it does | When to use |
|------|-------------|-------------|
| **Combine by Position** | Merges item 1 from A with item 1 from B | Most AI workflows |
| **Append** | Puts all items into a single list | When you want separate items |
| **Keep Key Matches** | Joins items by a matching field | When items share an ID |

**Recommendation:** Start with "Combine by Position" for AI workflows.

### Output (Combine by Position)

If Branch A outputs: `{ "sentiment": "positive" }`  
And Branch B outputs: `{ "facts": ["fact1"] }`

Merged output:
```json
{ "sentiment": "positive", "facts": ["fact1"] }
```

### What Happens with Mismatched Item Counts

If Branch A has 3 items and Branch B has 2 items:
- Items 1 and 2 are merged
- Item 3 from Branch A is dropped

**Solution:** Ensure parallel branches produce the same number of items.

### Common Mistake

**Field name collisions.** If both branches have a field with the same name, one overwrites the other. Use Set nodes to rename fields before merging.

**Docs:** [Merge Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.merge/)

---

## 7. AI Agent

**What it solves:** Lets an AI decide which tools to use and when. Unlike Basic LLM Chain (which runs once), the AI Agent can loop: call a tool, read the result, then decide to call another tool or finish.

### How It Differs from Basic LLM Chain

| Feature | Basic LLM Chain | AI Agent |
|---------|-----------------|----------|
| **Execution** | Single call | Loop until done |
| **Tools** | None | Can use Wikipedia, Calculator, HTTP, etc. |
| **Decision-making** | You control flow | Agent decides what to do |
| **Complexity** | Simple | More powerful, less predictable |

### Sub-Node Connections (Dotted Lines)

AI Agent uses **sub-nodes** connected via dotted lines:

| Sub-node | Purpose |
|----------|---------|
| **Chat Model** | The AI brain (required) |
| **Tools** | Actions the agent can take (optional) |
| **Memory** | Enables multi-turn conversation continuity (optional) |

### Common Tool Sub-Nodes

| Tool | What it does | Needs credentials? |
|------|--------------|-------------------|
| **Calculator** | Deterministic math | No |
| **Wikipedia** | Look up factual information | No |
| **SerpAPI** | Live web search | Yes |
| **HTTP Request** | Call any API | Depends on API |

### Memory Sub-Node

Connect **Simple Memory** to enable conversation history:
- The agent remembers what was said in previous turns
- Set a **Session ID** to separate different conversation threads
- Use with Chat Trigger for the best multi-turn experience

### Output

The agent's final response appears in the `output` field:

```json
{ "output": "Based on my research, here is what I found..." }
```

### Common Mistake

**Not defining tool boundaries.** Without clear instructions, agents may call tools unnecessarily or get stuck in loops. Be specific about when to use each tool.

**Docs:** [AI Agent Node](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/)

---

## 8. HTTP Request

**What it solves:** Connects to any API that doesn't have a native n8n integration. Essential for accessing external services, webhooks, and custom APIs.

### Example: Calling a Weather API

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Edit Fields    │────▶│  HTTP Request   │────▶│  Process Data   │
│  city = "Paris" │     │  GET weather API│     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        { "temp": 18,
                          "condition": "sunny" }
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Method** | GET, POST, PUT, DELETE, etc. |
| **URL** | The API endpoint (can use expressions) |
| **Authentication** | None, API Key, OAuth2, etc. |
| **Headers** | Custom headers (Content-Type, Authorization) |
| **Body** | Data to send (for POST/PUT requests) |

### Common Authentication Methods

| Method | How to configure |
|--------|------------------|
| **API Key in Header** | Add header: `Authorization: Bearer YOUR_KEY` |
| **API Key in Query** | Add to URL: `?api_key=YOUR_KEY` |
| **Basic Auth** | Use Authentication dropdown → Basic Auth |

### Sending JSON Data (POST)

For POST requests with JSON body:

1. Set **Method** to POST
2. Add header: `Content-Type: application/json`
3. Set **Body Content Type** to JSON
4. Add your JSON in the body field

### Output

The API response appears in `$json`:

```json
{
  "temp": 18,
  "condition": "sunny",
  "humidity": 65
}
```

Access nested data with `{{ $json.temp }}` or `{{ $json.condition }}`.

### Common Mistakes

**Forgetting Content-Type header.** Many APIs require `Content-Type: application/json` for POST requests.

**URL encoding issues.** Use expressions carefully — special characters in URLs may need encoding.

**Not handling errors.** Enable "Continue on Fail" if you want the workflow to continue when the API returns an error.

**Docs:** [HTTP Request Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)

---

## Quick Reference: All Nodes

| Node | Purpose | Key Output |
|------|---------|------------|
| **Manual Trigger** | Start workflow manually | Empty `{ }` |
| **Chat Trigger** | Chat interface for conversations | `{ "chatInput": "..." }` |
| **Edit Fields (Set)** | Create or modify data | Your defined fields |
| **Chat Model Provider** | Provide AI model | None (capability) |
| **Basic LLM Chain** | Call AI, get response | `{ "text": "..." }` |
| **Switch** | Route based on conditions | Data in one branch |
| **Merge** | Combine parallel branches | Combined fields |
| **AI Agent** | AI with tools, loops until done | `{ "output": "..." }` |
| **HTTP Request** | Call any external API | API response JSON |
| **SerpAPI** | Google Search tool for agents (sub-node) | Agent processes results internally |
| **Simple Memory** | Enable conversation history (sub-node) | None (capability) |
| **Calculator / Wikipedia** | Tool sub-nodes for agents | Tool-specific output |

---

## Expression Cheat Sheet

Copy-paste these patterns when building workflows.

### Basic Expressions

| I want to... | Expression |
|--------------|------------|
| Get a field from the previous node | `{{ $json.fieldName }}` |
| Get a nested field | `{{ $json.user.name }}` |
| Get an array item | `{{ $json.items[0] }}` |
| Combine text with data | `Write about {{ $json.topic }}` |

### Reference Other Nodes

| I want to... | Expression |
|--------------|------------|
| Get data from a specific node | `{{ $node["Node Name"].json.field }}` |
| Get data from the first node | `{{ $node["Edit Fields"].json.topic }}` |

### Default Values (Fallbacks)

The `||` operator means "or" — if the left side is empty/null/undefined, use the right side instead.

| I want to... | Expression |
|--------------|------------|
| Use a default if field is empty | `{{ $json.name || "Anonymous" }}` |
| Use a default for testing | `{{ $json.input || "test value" }}` |

### Common AI Workflow Patterns

| After this node... | Access with... |
|--------------------|----------------|
| **Edit Fields (Set)** | `{{ $json.yourFieldName }}` |
| **Basic LLM Chain** | `{{ $json.text }}` |
| **AI Agent** | `{{ $json.output }}` |
| **Chat Trigger** | `{{ $json.chatInput }}` and `{{ $json.sessionId }}` |

### Text Manipulation

| I want to... | Expression |
|--------------|------------|
| Trim whitespace | `{{ $json.text.trim() }}` |
| Lowercase | `{{ $json.text.toLowerCase() }}` |
| Uppercase | `{{ $json.text.toUpperCase() }}` |
| Get first N characters | `{{ $json.text.slice(0, 100) }}` |

### Debugging Tips

1. **Expression not working?** Check you're in Expression mode (not Fixed)
2. **Field not found?** Check exact spelling in Output Panel → JSON view
3. **Getting undefined?** The field name is case-sensitive
4. **Need to see raw data?** Use `{{ JSON.stringify($json) }}` temporarily
