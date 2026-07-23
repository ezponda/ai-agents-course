# Project 1: Recipe Assistant

In the Workflow Examples chapter, you built a **fixed recipe pipeline** — three LLM calls chained in a strict order. You controlled every step.

Now let's build a **conversational agent** that searches real recipes online, proposes **one** recipe, lets you refine it right in the chat ("another one", "something more Western"), and — when you confirm — builds a shopping list with real price estimates.

The trick that ties it together: the agent returns a small **structured JSON** every turn (`reply`, `recipe`, `build_shopping_list`), and an **IF** node reads that JSON to decide whether to run the price agent. The LLM isn't just chatting — it's **driving the workflow's logic**.

| What you'll learn | Where it comes from |
|---|---|
| **HTTP Request Tool** — fetch live data from APIs | New concept |
| **Fallback strategy** — two tools for the same task | Builds on the Tool Calling chapter |
| **Chat Trigger + Memory** — multi-turn conversation | Builds on the First AI Agent chapter |
| **Structured Output Parser** — force the agent to answer in JSON | New concept |
| **IF branching on the agent's output** — the LLM decides the route | Builds on the Routing pattern |

---

## The Workflow

```
                       output = { reply, recipe, build_shopping_list }
                                    │
┌──────────┐  ┌───────────────┐  ┌─▼─────────┐  true   ┌──────────────┐  ┌─────────────────┐
│ Chat     │─▶│ Recipe Agent  │─▶│ Want      │────────▶│ Shopping     │─▶│ Reply — With    │
│ Trigger  │  │ (+ Output     │  │ Prices?   │         │ List Agent   │  │ Prices          │
│(lastNode)│  │  Parser)      │  │ (IF)      │  false   └──────────────┘  └─────────────────┘
└──────────┘  └───────────────┘  └───────────┘───┐            ┊
        ┌─────────┬──────┬──────┬────────┐        └──▶┌─────────────────┐
   Chat Model  Memory  HTTP  Google  Output           │ Reply — Recipe   │
                     (MealDB)(fallb.) Parser           │ Only             │
                                                       └─────────────────┘
```

Every message you type runs the whole workflow **once**. The **Recipe Agent** searches for a recipe and returns a small JSON: a human-facing `reply`, the clean `recipe` text, and a `build_shopping_list` flag.

The **IF** reads that flag. While you're still choosing — or refining ("give me another one", "something more Western") — the flag is `false`, and the chat just shows the reply. The moment you confirm a recipe **and** ask for prices, the flag flips to `true`, and a **second agent** looks up real grocery prices and builds the shopping list.

No forms, no waiting, no buttons — the whole thing is one natural conversation.

---

**File:** [`10_recipe_assistant.json`](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/10_recipe_assistant.json)

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/10_recipe_assistant.json
> ```
>
> **Download:** {download}`10_recipe_assistant.json <_static/workflows/10_recipe_assistant.json>`

**Credentials needed:** OpenRouter API key + SerpAPI key (both from earlier chapters).

---

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

1. Click **Workflows** → **Add Workflow**
2. Rename it to "Recipe Assistant"

### Step 2: Add the Chat Trigger

1. Add the **When chat message received** node (Chat Trigger). Tip: if you add an **AI Agent** node to an empty canvas first, n8n creates this trigger for you automatically.
2. Open it and check **Options → Response Mode** is **When Last Node Finishes** (the default). That's all it needs here.

### Step 3: Add the AI Agent node

1. Add **AI Agent** → rename to `Recipe Agent`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression): `{{ $json.chatInput }}`
   - Turn ON **Require Specific Output Format** (this adds an output-parser connector at the bottom — you'll use it in Step 8)
   - **System Message** (in Options):
     ```
     You are a friendly recipe assistant. You chat with the user to find ONE recipe they like, then optionally build a shopping list with real prices.

How to search:
- Convert the user's request to a simple English search term (e.g. "quiero pollo" → "chicken").
- Use Recipe Search (TheMealDB) first. Only use Google Search if TheMealDB returns meals: null.

How to behave in the conversation:
- Present ONE recipe at a time — the best match — never a list. If the search returns several, pick one and say you can suggest another if they prefer.
- After showing a recipe, ALWAYS ask whether they want THIS recipe, a DIFFERENT one, or a SHOPPING LIST with price estimates.
- If the user asks for a different or more specific recipe (e.g. "something more Western", "vegetarian"), search again and propose a new one.
- Only offer the shopping list once you have shown a real recipe.

You ALWAYS answer with these three fields:
- "reply": a SHORT, friendly message the user sees. Introduce the recipe by name and ask the question above. Do NOT paste the full ingredient list or steps here — those go in "recipe".
- "recipe": the full recipe in this exact plain format:
    RECIPE: [name]
    Category: [category] | Cuisine: [cuisine]
    INGREDIENTS:
    - [quantity] [ingredient]
    INSTRUCTIONS:
    1. [step]
  Always keep the CURRENT proposed recipe here, even on later turns. Use an empty string only if you have not proposed a recipe yet.
- "build_shopping_list": true ONLY when the user has confirmed a recipe AND asked for the shopping list or prices. Otherwise false.

Rules:
- Never invent recipes — only present what you find from the tools.
- Include ALL ingredients with exact quantities from the source.
- Output valid JSON only — no markdown code fences, no text before or after.
     ```

### Step 4: Add the Chat Model (sub-node)

1. Click **+ Chat Model** at the bottom of the AI Agent node
2. Select **OpenRouter Chat Model**
3. Choose your credential
4. Model: `openai/gpt-4o-mini`

### Step 5: Add the Memory (sub-node)

1. Click **+ Memory** at the bottom of the AI Agent node
2. Select **Simple Memory** (called *Window Buffer Memory* in older n8n versions)
3. Configure:
   - **Context Window Length**: `10` (remembers last 10 messages)
   - **Session ID**: Custom Key with `{{ $json.sessionId }}`

### Step 6: Add the HTTP Request Tool (sub-node)

1. Click **+ Tool** at the bottom of the AI Agent node
2. Select **HTTP Request Tool**
3. Rename to `Recipe Search`
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `Recipe Search` |
| **Description** | `Search for recipes by name or ingredient on TheMealDB. Input should be a simple English search term like 'chicken' or 'pasta'. Returns recipe details including name, ingredients with quantities, and cooking instructions. If the response contains meals:null, it means no recipes were found — try Google Search instead.` |
| **Method** | `GET` |
| **URL** | `https://www.themealdb.com/api/json/v1/1/search.php` |

5. Toggle ON **Send Query Parameters** and add one parameter:

| Key | Value |
|-----|-------|
| `s` | Click the **✨ button** next to the value field (see note below) |

6. After clicking ✨, n8n creates a `$fromAI()` expression. Edit the description to:
   ```
   The recipe search term in English, a simple food keyword like chicken or pasta
   ```
7. Enable **Optimize Response** to reduce token usage

```{tip}
**The ✨ button:** Hover over the value field of a query parameter — a small sparkle icon (✨) appears. Clicking it tells n8n: "let the AI fill this value." n8n generates a `$fromAI()` expression that the agent fills at runtime.

If you prefer to type the expression manually, switch the value field to **Expression** mode and enter:

    {{ $fromAI('query', 'The recipe search term in English, a simple food keyword like chicken or pasta', 'string') }}
```

### Step 7: Add the SerpAPI Tool (sub-node)

1. Click **+ Tool** at the bottom of the AI Agent node
2. Select **SerpAPI** (you should already have credentials from the First AI Agent chapter)
3. Rename to `Google Search`

### Step 8: Add the Structured Output Parser (sub-node)

1. Click the **output parser** connector at the bottom of the Recipe Agent (it appeared when you turned on *Require Specific Output Format*)
2. Select **Structured Output Parser** → rename to `Recipe Format`
3. Configure:
   - **Schema Type**: `Generate From JSON Example`
   - **JSON Example** — copy and paste:
     ```json
     {
  "reply": "Here's a great option — Chicken Handi (Indian). Would you like this recipe, a different one, or a shopping list with price estimates?",
  "recipe": "RECIPE: Chicken Handi\nCategory: Chicken | Cuisine: Indian\nINGREDIENTS:\n- 500g chicken\n- 2 onions\n- 3 tomatoes\nINSTRUCTIONS:\n1. Sauté the onions\n2. Add spices and chicken\n3. Simmer with tomatoes",
  "build_shopping_list": false
}
     ```
   - Turn ON **Auto-Fix Format**. This adds a **Model** connector on the parser — connect the **same OpenRouter Chat Model** to it (drag from the model node to the parser's Model input). If the agent ever answers with slightly broken JSON, n8n repairs it with one extra LLM call.

n8n reads this example and forces the agent to answer with exactly these fields. From now on, `{{ $json.output }}` is an **object**, so you can read `{{ $json.output.build_shopping_list }}`.

### Step 9: Add the IF node

1. Add **IF** → rename to `Want Prices?`
2. Add one condition:
   - **Left Value** (Expression): `{{ $json.output.build_shopping_list }}`
   - **Type**: `Boolean`
   - **Operation**: `is true`

The **true** branch runs when the agent set `build_shopping_list` to `true`; the **false** branch otherwise.

### Step 10: Add the Shopping List Agent (true branch)

1. From the **true** output of the IF node, add **AI Agent** → rename to `Shopping List Agent`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression): `{{ $json.output.recipe }}`
   - Leave **Require Specific Output Format** OFF (a plain text list is fine)
   - **System Message** (in Options):
     ```
     You are a shopping assistant that creates shopping lists with real prices.

From the recipe provided, create a complete shopping list with current US grocery prices.

Steps:
1. Extract the ingredient list from the recipe
2. Search for current grocery prices — batch multiple ingredients into ONE search query (e.g. "grocery store prices chicken breast tomatoes onions")
3. Use at most 2 searches total to conserve API usage
4. For any ingredient you cannot find a price for, estimate based on your knowledge and mark it with ≈

Format:
## Shopping List

### Produce
- [quantity] [item] — ~$[price]

### Meat / Fish
- [quantity] [item] — ~$[price]

### Dairy
- [quantity] [item] — ~$[price]

### Pantry
- [quantity] [item] — ~$[price]

---
**Estimated Total: ~$[total]**

Budget Tips:
- [tip 1]
- [tip 2]

Rules:
- Include exact quantities from the recipe
- Skip items most kitchens already have (salt, pepper, cooking oil)
- Group items by store section
- Mark searched prices with $ and estimated prices with ≈$
- Output ONLY the shopping list — no recipe repetition
     ```
3. Add **Chat Model** sub-node (OpenRouter, `openai/gpt-4o-mini`)
4. Add **SerpAPI** tool sub-node → rename to `Price Search`

### Step 11: Add the reply nodes (Edit Fields / Set)

In *When Last Node Finishes* mode, the chat shows whatever the last node puts in `output`. Add one **Edit Fields (Set)** node at the end of each branch, each with a single String field named `output`:

**Reply — With Prices** (after Shopping List Agent):
```
{{ $('Recipe Agent').first().json.output.recipe + '\n\n---\n\n' + $json.output }}
```

**Reply — Recipe Only** (from the **false** output of the IF node):
```
{{ $json.output.recipe ? $json.output.recipe + '\n\n' + $json.output.reply : $json.output.reply }}
```
(Show the recipe followed by the short reply; if there's no recipe yet, just the reply.)

### Step 12: Connect the main nodes

```
Chat Trigger → Recipe Agent → Want Prices?
    Want Prices? (true)  → Shopping List Agent → Reply — With Prices
    Want Prices? (false) → Reply — Recipe Only
```

::::

## The Agent

### What Is an API Endpoint?

An **API endpoint** is a specific URL that returns data when you call it. Think of it as a vending machine: you press a button (the URL + parameters), and it gives you a specific product (JSON data).

```
You (n8n)                          API Server
─────────                          ──────────
  GET /search?s=chicken   ──────▶  TheMealDB
                          ◀──────  { meals: [...] }
```

The **HTTP Request Tool** in n8n lets an agent call any API endpoint.

### TheMealDB: A Free Recipe API

[TheMealDB](https://www.themealdb.com/api.php) is a free recipe database. No API key needed — the test key `1` is built into the URL.

| Endpoint | URL | What it returns |
|----------|-----|----------------|
| **Search by name** | `.../search.php?s=chicken` | Full recipes matching the term |
| **Random recipe** | `.../random.php` | One random recipe |
| **Filter by category** | `.../filter.php?c=Seafood` | Recipe names in a category |
| **Filter by cuisine** | `.../filter.php?a=Italian` | Recipe names from a cuisine |

All URLs start with `https://www.themealdb.com/api/json/v1/1/`.

**Key details:**
- Results come inside a `"meals"` array
- If nothing is found, `"meals"` is `null` (not an empty array)
- Ingredients and measures are stored as 20 numbered pairs (`strIngredient1`/`strMeasure1` through `strIngredient20`/`strMeasure20`)

### Two Tools, One Strategy

The agent has **two search tools** — a primary and a fallback:

| Tool | Type | When the agent uses it |
|------|------|----------------------|
| **Recipe Search** | HTTP Request → TheMealDB | First choice — structured data, free, no key |
| **Google Search** | SerpAPI | Fallback — if TheMealDB has no results |

TheMealDB has ~300 recipes with clean, structured JSON. But it doesn't have every recipe. SerpAPI searches Google and can find any recipe, but the results are unstructured web pages.

The system message tells the agent: **"Always try TheMealDB first. Only use Google if TheMealDB returns no results."** This is a **fallback strategy** — a common pattern in production systems.

### HTTP Request Tool with `$fromAI()`

Until now, your agents used built-in tools (Calculator, Wikipedia, SerpAPI). The **HTTP Request Tool** lets an agent call any URL — opening the door to thousands of public APIs.

The agent needs to fill in the search term dynamically. We use `$fromAI()` — a special function that tells the AI model: "you need to provide a value for this parameter."

In the HTTP Request Tool, we set:
- **URL**: `https://www.themealdb.com/api/json/v1/1/search.php` (static, no query string)
- **Send Query Parameters**: ON
- **Key**: `s` — **Value**: `$fromAI('query', 'The recipe search term in English...', 'string')`

When the user asks "I want chicken", the agent fills in the value and the tool calls:
```
GET https://www.themealdb.com/api/json/v1/1/search.php?s=chicken
```

The `$fromAI()` function takes three arguments:

| Argument | Meaning | Example |
|----------|---------|---------|
| `key` | Parameter name (the agent sees this) | `'query'` |
| `description` | What value to provide | `'A simple food keyword like chicken or pasta'` |
| `type` | Data type | `'string'` |

```{tip}
The system prompt tells the agent to **translate the user's request to English** before searching (e.g. "quiero pollo" → `chicken`). This ensures TheMealDB gets a valid search term regardless of what language the user types in.
```

**Docs:** [HTTP Request Tool](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolhttprequest/)

### Memory

The **Simple Memory** node (formerly *Window Buffer Memory*) stores the last 10 messages of the conversation. This is what lets the user **refine** a recipe across turns: "give me another one", "something more Western" — the agent remembers what it already proposed.

### Structured Output: making the agent answer in JSON

Here's the new idea in this project. By default, an agent answers with **free text** — a paragraph. But we don't just want a paragraph: we want the workflow to *decide* whether to build a shopping list. A plain paragraph is hard for an IF node to reason about.

So we force the agent to answer in a fixed **JSON shape**. Two things make this happen:

1. On the AI Agent node, turn on **Require Specific Output Format** (`hasOutputParser`).
2. Connect a **Structured Output Parser** sub-node (we named it **Recipe Format**) and give it an **example** of the JSON we want.

**Recipe Format — example JSON** (Schema Type: *Generate From JSON Example*):

```json
{
  "reply": "Here's a great option — Chicken Handi (Indian). Would you like this recipe, a different one, or a shopping list with price estimates?",
  "recipe": "RECIPE: Chicken Handi\nCategory: Chicken | Cuisine: Indian\nINGREDIENTS:\n- 500g chicken\n- 2 onions\n- 3 tomatoes\nINSTRUCTIONS:\n1. Sauté the onions\n2. Add spices and chicken\n3. Simmer with tomatoes",
  "build_shopping_list": false
}
```

From this example, n8n infers the schema and forces every answer into the same three fields:

| Field | Purpose |
|-------|---------|
| `reply` | A **short** friendly message shown in the chat (recipe name + the question) |
| `recipe` | The **full** recipe text, kept for the Shopping List Agent |
| `build_shopping_list` | `true` only when the user confirmed a recipe **and** asked for prices |

```{important}
With a parser attached, `{{ $json.output }}` is no longer a string — it's an **object**. That's the whole point: now the IF can read `{{ $json.output.build_shopping_list }}` and route on it. (Without the parser, `$json.output` would be a plain string and there would be nothing structured to branch on.)
```

```{tip}
**Auto-Fix Format** is turned ON in the parser. Small models sometimes answer with stray text or slightly broken JSON. When that happens, n8n makes one extra LLM call to repair the answer into the right shape — that's why the parser also has a **Chat Model** connected to it. It's the safety net that keeps the workflow robust across model updates. (To keep the JSON easy to produce, we ask for a **short** `reply` and put the long recipe only in `recipe` — one big text field instead of two.)
```

### System Message

**Recipe Agent System Message:**

```
You are a friendly recipe assistant. You chat with the user to find ONE recipe they like, then optionally build a shopping list with real prices.

How to search:
- Convert the user's request to a simple English search term (e.g. "quiero pollo" → "chicken").
- Use Recipe Search (TheMealDB) first. Only use Google Search if TheMealDB returns meals: null.

How to behave in the conversation:
- Present ONE recipe at a time — the best match — never a list. If the search returns several, pick one and say you can suggest another if they prefer.
- After showing a recipe, ALWAYS ask whether they want THIS recipe, a DIFFERENT one, or a SHOPPING LIST with price estimates.
- If the user asks for a different or more specific recipe (e.g. "something more Western", "vegetarian"), search again and propose a new one.
- Only offer the shopping list once you have shown a real recipe.

You ALWAYS answer with these three fields:
- "reply": a SHORT, friendly message the user sees. Introduce the recipe by name and ask the question above. Do NOT paste the full ingredient list or steps here — those go in "recipe".
- "recipe": the full recipe in this exact plain format:
    RECIPE: [name]
    Category: [category] | Cuisine: [cuisine]
    INGREDIENTS:
    - [quantity] [ingredient]
    INSTRUCTIONS:
    1. [step]
  Always keep the CURRENT proposed recipe here, even on later turns. Use an empty string only if you have not proposed a recipe yet.
- "build_shopping_list": true ONLY when the user has confirmed a recipe AND asked for the shopping list or prices. Otherwise false.

Rules:
- Never invent recipes — only present what you find from the tools.
- Include ALL ingredients with exact quantities from the source.
- Output valid JSON only — no markdown code fences, no text before or after.
```

---

## From JSON to Branching: the Shopping List

### One message = one execution

This is the mental model that makes everything click: **every message you type in the chat runs the whole workflow from the top.** The "conversation" isn't one long run — it's many short runs, stitched together by **Memory**.

So the Recipe Agent produces its JSON **on every turn**:

- Turn 1 — *"I want a chicken recipe"* → `build_shopping_list: false`. The IF sends you the reply. You're looking at a recipe.
- Turn 2 — *"give me another one"* → `build_shopping_list: false`. New recipe, same false. Refine as many times as you like.
- Turn 3 — *"yes, add the shopping list"* → `build_shopping_list: true`. Now the IF fires the true branch.

The agent is acting as a **router**: its `build_shopping_list` flag tells the workflow when to move on.

### Stage 2: the IF

The **Want Prices?** node reads one boolean:

```
{{ $json.output.build_shopping_list }}
```

`true` → Shopping List Agent. `false` → straight to `Reply — Recipe Only`, which shows the recipe followed by the agent's short `reply`.

### Why "When Last Node Finishes" (and not streaming)

The Chat Trigger has three response modes. Here we use **When Last Node Finishes** (`lastNode`), because we **post-process** the agent's answer: we branch on it, and sometimes run a second agent, before deciding what the chat should show. In `lastNode` mode, whatever the **last** node writes to `output` is what the chat displays — so both `Reply` nodes end by writing an `output` field.

(*Streaming* mode, where the agent types its answer straight into the chat, only works when the agent's raw reply **is** the final message. Since our agent returns JSON that we still need to route on, streaming doesn't fit here. The video guion covers all three modes in detail.)

### Stage 3: Shopping List with Real Prices

When `build_shopping_list` is `true`, a **second AI Agent** builds the list. Unlike the Recipe Agent, it has a single tool — **SerpAPI** (Google Search) — and **no output parser** (a plain text list is fine here).

| | Recipe Agent | Shopping List Agent |
|--|---|---|
| **Task** | Find & refine a recipe, decide the route | Compile a priced shopping list |
| **Output** | JSON (`reply`, `recipe`, `build_shopping_list`) | Plain text (the list) |
| **Tools** | HTTP (TheMealDB) + SerpAPI fallback | SerpAPI (price lookups) |

Its input is the recipe field from the previous node:

```
{{ $json.output.recipe }}
```

The agent batches ingredient searches to conserve API calls (one search for "grocery prices chicken tomatoes onions" instead of one per ingredient). Ingredients it cannot price are marked with `≈` (estimated).

**Shopping List Agent System Message:**

```
You are a shopping assistant that creates shopping lists with real prices.

From the recipe provided, create a complete shopping list with current US grocery prices.

Steps:
1. Extract the ingredient list from the recipe
2. Search for current grocery prices — batch multiple ingredients into ONE search query (e.g. "grocery store prices chicken breast tomatoes onions")
3. Use at most 2 searches total to conserve API usage
4. For any ingredient you cannot find a price for, estimate based on your knowledge and mark it with ≈

Format:
## Shopping List

### Produce
- [quantity] [item] — ~$[price]

### Meat / Fish
- [quantity] [item] — ~$[price]

### Dairy
- [quantity] [item] — ~$[price]

### Pantry
- [quantity] [item] — ~$[price]

---
**Estimated Total: ~$[total]**

Budget Tips:
- [tip 1]
- [tip 2]

Rules:
- Include exact quantities from the recipe
- Skip items most kitchens already have (salt, pepper, cooking oil)
- Group items by store section
- Mark searched prices with $ and estimated prices with ≈$
- Output ONLY the shopping list — no recipe repetition
```

### The `$json` gotcha, again

The Shopping List Agent **overwrites** `$json.output` with its own answer (the list, a string). So by the time we reach `Reply — With Prices`, `$json.output` no longer holds the recipe object. To rebuild the final message, we reach back to the Recipe Agent **by name**:

```
{{ $('Recipe Agent').first().json.output.recipe + '\n\n---\n\n' + $json.output }}
```

"Take the recipe from the Recipe Agent's output object, add a separator, then add the shopping list the previous node just produced."

---

## Node-by-Node Walkthrough

| Node | Type | What it does |
|------|------|-------------|
| **When chat message received** | Chat Trigger | Opens the chat; provides `chatInput` and `sessionId`. Response Mode: *When Last Node Finishes* |
| **Recipe Agent** | AI Agent (+ Output Parser) | Searches for a recipe and returns `{ reply, recipe, build_shopping_list }` |
| **Want Prices?** | IF | Routes on the boolean `{{ $json.output.build_shopping_list }}` |
| **Shopping List Agent** | AI Agent | Builds a priced shopping list from `{{ $json.output.recipe }}` |
| **Reply — With Prices** | Set | Combines recipe + shopping list into `output` |
| **Reply — Recipe Only** | Set | Shows the recipe + the agent's short `reply` as `output` |

**Sub-nodes of the Recipe Agent (dotted lines):**

| Sub-node | Type | Purpose |
|----------|------|---------|
| **OpenRouter Chat Model** | Chat Model | The agent's brain (`openai/gpt-4o-mini`) |
| **Simple Memory** | Memory | Last 10 messages, keyed by `{{ $json.sessionId }}` — enables refinement across turns |
| **Recipe Search** | HTTP Request Tool | TheMealDB search, query filled via `$fromAI()` |
| **Google Search** | SerpAPI | Fallback when TheMealDB returns `meals: null` |
| **Recipe Format** | Structured Output Parser | Forces the agent to answer in the `{ reply, recipe, build_shopping_list }` shape (Auto-Fix ON) |

**Sub-nodes of the Shopping List Agent:**

| Sub-node | Type | Purpose |
|----------|------|---------|
| **OpenRouter Chat Model (Prices)** | Chat Model | Its own model connection |
| **Price Search** | SerpAPI | Looks up current grocery prices |

---

## Data Flow

```
INPUT                                OUTPUT
─────                                ──────
Chat: { chatInput: "I want a chicken recipe", sessionId: "abc123" }
    ↓
Recipe Agent (with the Output Parser):
  1. Calls Recipe Search (TheMealDB) with s=chicken
  2. Picks ONE recipe and writes the JSON
  → { output: { reply: "Here's Chicken Handi ... want this, another, or a shopping list?",
                recipe: "RECIPE: Chicken Handi ...",
                build_shopping_list: false } }
    ↓
Want Prices? (IF): {{ $json.output.build_shopping_list }} is false → false branch
    ↓
Reply — Recipe Only: { output: recipe + reply }   → the chat shows it
```

Now you answer **"yes, with the shopping list"** — a *new* run of the same workflow:

```
Chat: { chatInput: "yes, with the shopping list", sessionId: "abc123" }
    ↓
Recipe Agent (remembers the recipe via Memory):
  → { output: { reply: "Great, here's your shopping list!",
                recipe: "RECIPE: Chicken Handi ...",
                build_shopping_list: true } }
    ↓
Want Prices? (IF): true branch
    ↓
Shopping List Agent (input: {{ $json.output.recipe }}):
  1. Calls Price Search (1-2 batched searches)
  → { output: "## Shopping List ..." }
    ↓
Reply — With Prices: { output: recipe + "---" + shopping list }   → the chat shows it
```

::::{dropdown} 🔍 See detailed data transformation at each step
:color: info

```
┌──────────────────────┐         ┌──────────────────────────────┐
│ Chat Trigger         │────────▶│ Recipe Agent (+ Output Parser)│
└──────────────────────┘         └──────────────────────────────┘
        │                                   │
        ▼                                   ▼
{ "chatInput": "I want a          { "output": {
  chicken recipe",                    "reply": "Here's Chicken Handi ...",
  "sessionId": "abc123" }             "recipe": "RECIPE: Chicken Handi ...",
                                      "build_shopping_list": false } }
                                            │
                                            ▼  IF reads $json.output.build_shopping_list
                                 ┌──────────────────────────┐
                                 │ Shopping List Agent      │ (only on the "true" turn)
                                 └──────────────────────────┘
                                            │  ⚠️ here $json.output is the LIST (a string),
                                            ▼     not the recipe object anymore
                                 { "output": "## Shopping List\n### Produce ..." }
```

**Key insights:**
- With a **Structured Output Parser** attached, `$json.output` is an **object**, not a string. That's why the IF can read `$json.output.build_shopping_list` and the Shopping List Agent can read `$json.output.recipe`.
- The **Shopping List Agent** replaces `$json.output` with its own string answer. To get the recipe back for the final message, `Reply — With Prices` references the agent by name: `$('Recipe Agent').first().json.output.recipe`.
- Because the Chat Trigger is in **When Last Node Finishes** mode, whatever the last node puts in `output` is what the chat shows. Both `Reply` nodes end by writing `output`.

::::

---

## Full Circle: From Fixed Chain to Smart Agent

Compare what you built in the Prompt Chaining section with this project:

| | Prompt Chaining (Ch. 4) | This Project |
|--|---------------------------|-------------|
| **Recipe source** | Hard-coded in the Input node | Fetched live from the internet |
| **Step order** | Fixed: Step 1 → Step 2 → Step 3 | Agent decides the order |
| **Choosing a recipe** | None — one fixed recipe | Conversational: propose, refine, confirm |
| **Shopping list** | Always generated | Agent decides via `build_shopping_list` |
| **Prices** | LLM guesses | Agent searches for real grocery prices |
| **Error handling** | None — fails if input is bad | Fallback from TheMealDB to Google |
| **Memory** | None — single execution | Remembers the conversation across turns |
| **Routing** | None | IF reads the agent's structured output |
| **Input** | One hard-coded request | Interactive chat |

---

## Test Scenarios

Run these in order and expand the agent's execution details between runs. Open the Recipe Agent's output to watch the JSON (`reply` / `recipe` / `build_shopping_list`) change turn by turn.

| # | You type | What should happen |
|---|----------|--------------------|
| 1 | `I want a chicken recipe` | TheMealDB hit; the agent proposes **one** recipe and asks if you want it, another, or the shopping list. `build_shopping_list` is `false` |
| 2 | (same chat) `Give me a more Western one` | The agent searches again and proposes a different recipe — no restart needed. Still `false` |
| 3 | (same chat) `Perfect, add the shopping list with prices` | `build_shopping_list` flips to `true`; the IF's true branch runs the Shopping List Agent |
| 4 | `How do I make Spanish fabada asturiana?` | TheMealDB returns `meals: null` → the agent falls back to Google Search (check the tool order in the logs) |
| 5 | `Quiero algo con pescado` | The agent translates to English (`fish`) before searching — the system message told it to |
| 6 | `I want a recipe for pencils` | Not a real dish. The "never invent" rule should stop it from making one up, but exactly *how* it refuses isn't pinned down — a great place to see prompt engineering in action (Challenge 2 / the video shows how to shape it) |

**What to observe:** the conversation feels like a normal chat, but under the hood every turn produces a JSON that the IF uses to route. The recipe is proposed and refined for free (turns 1-2); the expensive price search only fires when you explicitly confirm (turn 3).

---

## Try It Yourself

### Challenge 1: Random Recipe Tool

Add a third tool to the Recipe Agent using TheMealDB's random endpoint:

```
https://www.themealdb.com/api/json/v1/1/random.php
```

This takes no parameters — it returns one random recipe. Update the system message so the agent uses this tool when the user says "surprise me" or "pick something random."

**Done when:** saying "surprise me" triggers the random endpoint and the agent proposes that recipe.

### Challenge 2: Add a "difficulty" field to the JSON

Extend the Structured Output Parser's example so the agent also returns a `difficulty` field (`easy` / `medium` / `hard`), and mention it in the system message. Then add a second condition to the IF (or a Switch) that reacts to it.

**Done when:** the Recipe Agent's output includes a `difficulty` field you can read as `{{ $json.output.difficulty }}`.

### Challenge 3: Real Prices with Spoonacular API

Replace LLM-estimated prices with real ingredient prices using the [Spoonacular API](https://spoonacular.com/food-api) (free tier: 50 points/day).

**Endpoints:**
- Search: `GET https://api.spoonacular.com/food/ingredients/search?query={name}&number=1&apiKey=KEY`
- Price: `GET https://api.spoonacular.com/food/ingredients/{id}/information?amount=1&unit=piece&apiKey=KEY`

The price comes back in US cents (`estimatedCost.value`). The free tier allows ~24 ingredient lookups per day.

**Tip:** Have the agent look up prices for only the 3-5 most expensive ingredients and estimate the rest — this keeps API usage low.

**Done when:** the shopping list includes at least 3 real prices from Spoonacular.

---

## Summary

| Concept | What You Learned |
|---------|------------------|
| **HTTP Request Tool** | Agents can call any web API using `$fromAI()` to let the AI fill in parameters |
| **Fallback strategy** | Use a reliable API first, fall back to a broader search if needed |
| **Chat Trigger + Memory** | Build interactive, multi-turn conversations that refine across turns |
| **Structured Output Parser** | Force the agent to answer in a fixed JSON shape — `$json.output` becomes an object |
| **IF on the agent's output** | Let the LLM drive the workflow: route on `{{ $json.output.build_shopping_list }}` |
| **`$('Node').first().json.output.field`** | Reference a previous node's output, even after another node overwrote `$json` |

**Key expressions:**
- `{{ $json.chatInput }}` — the user's message from Chat Trigger
- `{{ $json.output }}` — the agent's answer (a **string** without a parser, an **object** with one)
- `{{ $json.output.build_shopping_list }}` — a field of the parsed JSON (drives the IF)
- `{{ $json.output.recipe }}` — the recipe field, fed into the Shopping List Agent
- `{{ $('Recipe Agent').first().json.output.recipe }}` — reference a specific node's output by name

**Docs:**
- [HTTP Request Tool](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolhttprequest/)
- [Chat Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.chattrigger/)
- [Structured Output Parser](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.outputparserstructured/)
- [Simple Memory (Window Buffer)](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.memorybufferwindow/)
- [TheMealDB API](https://www.themealdb.com/api.php)
