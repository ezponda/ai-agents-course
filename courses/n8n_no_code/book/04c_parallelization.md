# Pattern 3: Parallelization

**What you will build:** A customer email arrives. Three branches analyze it simultaneously — one extracts facts, one detects sentiment, one drafts a reply — then a final LLM combines everything into one informed response.

```
                        ┌─────────────────┐
                   ┌───▶│ LLM: Facts      │───┐
┌─────────────────┐│    └─────────────────┘   │    ┌─────────────────┐
│  Manual Trigger │┼───▶│ LLM: Sentiment  │───┼───▶│     Merge       │────▶ ...
└─────────────────┘│    └─────────────────┘   │    └─────────────────┘
                   └───▶│ LLM: Draft      │───┘
                        └─────────────────┘
```

```{note}
**Not true parallel execution.** Despite the visual layout, n8n executes branches **sequentially** (A, then B, then C), not simultaneously. True parallel execution would require sub-workflows with webhook triggers — significantly more complex to set up. 

This pattern is still valuable for **code organization** and **clarity**, even without the speed benefit of real parallelization.
```

**New node:** **Merge** — combines data from multiple branches into one.

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/03_parallelization.json
> ```
> 
> **Download:** {download}`03_parallelization.json <_static/workflows/03_parallelization.json>`

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

1. Click **Workflows** → **Add Workflow**
2. Rename it to "Parallelization Practice"

### Step 2: Add the trigger and input

1. Add **Manual Trigger**
2. Add **Edit Fields** → rename to `Input — Customer Email`
3. Add two String fields:

| Name | Value |
|------|-------|
| `email_subject` | `Can't access my account after password reset` |
| `email_body` | `Hello,\nI reset my password twice but I still can't log in. It says 'invalid token'.\nI'm trying to access my invoices before end of day.\nCan you help?\n— Sam` |

### Step 3: Connect to three parallel branches

From the Input node, drag THREE connections to create branches:

**Branch A — Extract Facts:**
1. Add **Basic LLM Chain** → rename to `Branch A — Extract Facts`
2. Prompt (Expression):
   ```
   Subject: {{ $json.email_subject }}
   Body:
   {{ $json.email_body }}

   JSON:
   ```
3. System:
   ```
   Extract key facts from the email.
   Return STRICT JSON with keys:
   customer_name, issue, deadline, requested_action, missing_info (array).
   Return JSON only.
   ```

**Branch B — Sentiment & Urgency:**
1. Add **Basic LLM Chain** → rename to `Branch B — Sentiment & Urgency`
2. Same prompt structure
3. System:
   ```
   Classify sentiment and urgency.
   Return STRICT JSON with keys:
   sentiment (positive|neutral|negative), urgency (low|medium|high), risk_flags (array).
   Return JSON only.
   ```

**Branch C — Draft Reply:**
1. Add **Basic LLM Chain** → rename to `Branch C — Draft Reply`
2. Prompt (Expression):
   ```
   Subject: {{ $json.email_subject }}
   Body:
   {{ $json.email_body }}

   Reply:
   ```
3. System:
   ```
   Draft a helpful customer support email reply.
   Rules:
   - Friendly and concise
   - Ask for missing info only if needed
   - Offer 1–2 concrete next steps
   - Under 140 words

   Output ONLY the reply text.
   ```

### Step 4: Add Store nodes after each branch

For each LLM, add **Edit Fields** with **Keep Only Set** enabled:
- Branch A: store `facts_json` = `{{ $json.text }}`
- Branch B: store `sentiment_json` = `{{ $json.text }}`
- Branch C: store `draft_reply` = `{{ $json.text }}`

### Step 5: Merge the branches

1. Add **Merge** node → rename to `Merge A+B`
   - Mode: **Combine by Position**
   - Connect Store Facts (input 1) and Store Sentiment (input 2)

2. Add another **Merge** → rename to `Merge (A+B)+C`
   - Connect Merge A+B (input 1) and Store Draft Reply (input 2)

### Step 6: Add the Finalize LLM

1. Add **Basic LLM Chain** → rename to `Finalize — One Improved Reply`
2. Prompt (Expression):
   ```
   facts_json:
   {{ $json.facts_json }}

   sentiment_json:
   {{ $json.sentiment_json }}

   draft_reply:
   {{ $json.draft_reply }}

   Final reply:
   ```
3. System:
   ```
   You are a senior support agent.
   You will receive:
   - facts_json (extracted facts)
   - sentiment_json (sentiment & urgency)
   - draft_reply (initial draft)

   Task:
   1) Improve the draft to match urgency and include any critical missing info questions.
   2) Keep it under 160 words.
   3) Output ONLY the final reply text.
   ```

### Step 7: Add Output

1. Add **Edit Fields** → rename to `Output — Final Reply`
2. Store `final_reply` = `{{ $json.text }}`
3. Enable **Keep Only Set**

### Step 8: Test

1. Click **Execute Workflow**
2. Check the merged output contains all three fields

::::

### Meet the Node: Merge

This pattern introduces a new node: **Merge**.

| Property | Description |
|----------|-------------|
| **Purpose** | Combines data from multiple branches into one |
| **Multiple inputs** | Receives data from 2+ parallel branches |
| **Output** | One combined item (or list) with all fields |

**Key Modes:**
| Mode | What it does |
|------|--------------|
| **Combine by Position** | Pairs items by index (1st + 1st, 2nd + 2nd). Best when each branch outputs one item. |
| **Combine by Fields** | Matches items by a common field value |
| **Append** | Puts all items into one list |

In this workflow, we use **Combine by Position** because each branch outputs exactly one item.

**See the **Node Toolbox** appendix for full documentation.**

### What Problem This Solves

Some tasks have independent parts that can be analyzed separately. Analyzing a customer email for facts, sentiment, and drafting a reply are independent—they don't need each other's results. Splitting them into branches keeps your workflow organized, and you can combine the results at the end for a final, informed response.

### Node-by-Node Walkthrough

<div style="overflow: auto; max-height: 300px; border: 1px solid #ddd; border-radius: 4px; padding: 10px; margin-bottom: 15px; background: #f8f8f8;">
<pre style="margin: 0; white-space: pre;">
┌──────────────────┐     ┌────────────────────────┐
│   Manual Trigger │────▶│ Input — Customer Email │───┬────▶┌─────────────────────────┐────▶┌───────────────────┐────┐
└──────────────────┘     └────────────────────────┘   │     │  Branch A — Facts       │     │    Store Facts    │    │
                                                      │     └─────────────────────────┘     └───────────────────┘    │
                                                      │                                                              │
                                                      ├────▶┌─────────────────────────┐────▶┌───────────────────┐    ├────▶┌─────────────┐────▶┌─────────────────┐────▶┌────────────────────┐────▶┌────────────────────────┐
                                                      │     │  Branch B — Sentiment   │     │  Store Sentiment  │    │     │  Merge A+B  │     │  Merge (A+B)+C  │     │ Finalize — Reply   │     │  Output — Final Reply  │
                                                      │     └─────────────────────────┘     └───────────────────┘    │     └─────────────┘     └─────────────────┘     └────────────────────┘     └────────────────────────┘
                                                      │                                                              │
                                                      └────▶┌─────────────────────────┐────▶┌───────────────────┐────┘
                                                            │  Branch C — Draft       │     │   Store Draft     │
                                                            └─────────────────────────┘     └───────────────────┘
</pre>
</div>

| Node | Type | What it does |
|------|------|-------------|
| **Run: Parallelization** | Manual Trigger | Starts the workflow |
| **Input — Customer Email** | Set | Creates fields: `email_subject`, `email_body` |
| **Branch A — Extract Facts** | Basic LLM Chain | Extracts facts as JSON → outputs `text` |
| **Store Facts** | Set | Saves `{{ $json.text }}` as `facts_json` |
| **Branch B — Sentiment & Urgency** | Basic LLM Chain | Analyzes sentiment → outputs `text` |
| **Store Sentiment** | Set | Saves `{{ $json.text }}` as `sentiment_json` |
| **Branch C — Draft Reply** | Basic LLM Chain | Drafts initial reply → outputs `text` |
| **Store Draft Reply** | Set | Saves `{{ $json.text }}` as `draft_reply` |
| **Merge A+B** | Merge | Combines `facts_json` + `sentiment_json` (mode: Combine by Position) |
| **Merge (A+B)+C** | Merge | Adds `draft_reply` to the combined data |
| **Finalize — One Improved Reply** | Basic LLM Chain | Uses all three fields → outputs `text` |
| **Output — Final Reply** | Set | Saves `{{ $json.text }}` as `final_reply` |

### Prompts Used

**Branch A — Extract Facts:**
```
System: Extract key facts from the email.
Return STRICT JSON with keys:
customer_name, issue, deadline, requested_action, missing_info (array).
Return JSON only.
```

**Branch B — Sentiment & Urgency:**
```
System: Classify sentiment and urgency.
Return STRICT JSON with keys:
sentiment (positive|neutral|negative), urgency (low|medium|high), risk_flags (array).
Return JSON only.
```

**Branch C — Draft Reply:**
```
System: Draft a helpful customer support email reply.
Rules:
- Friendly and concise
- Ask for missing info only if needed
- Offer 1–2 concrete next steps
- Under 140 words

Output ONLY the reply text.
```

**Finalize — One Improved Reply:**
```
System: You are a senior support agent.
You will receive:
- facts_json (extracted facts)
- sentiment_json (sentiment & urgency)
- draft_reply (initial draft)

Task:
1) Improve the draft to match urgency and include any critical missing info questions.
2) Keep it under 160 words.
3) Output ONLY the final reply text.
```

### Example JSON Outputs

**Branch A (facts_json):**
```json
{
  "customer_name": "Sam",
  "issue": "Can't log in after password reset, invalid token error",
  "deadline": "end of day",
  "requested_action": "Help accessing invoices",
  "missing_info": []
}
```

**Branch B (sentiment_json):**
```json
{
  "sentiment": "negative",
  "urgency": "high",
  "risk_flags": ["access issue", "time-sensitive", "repeated attempts"]
}
```

### Data Flow

```
INPUT                          OUTPUT
─────                          ──────
Trigger: { }
    ↓
Customer Email: { email_subject, email_body }
    ↓ ↓ ↓ (splits into 3 branches — executed sequentially)
    
Branch A: { text: '{"customer_name":"Sam",...}' }
    ↓
Store Facts: { facts_json: '{"customer_name":"Sam",...}' }

Branch B: { text: '{"sentiment":"negative","urgency":"high",...}' }
    ↓
Store Sentiment: { sentiment_json: '{"sentiment":"negative",...}' }

Branch C: { text: "Hi Sam, I understand..." }
    ↓
Store Draft Reply: { draft_reply: "Hi Sam, I understand..." }
    
    ↓ (merge all three)
After Merge: { facts_json, sentiment_json, draft_reply }
    ↓
Finalize LLM: { text: "Dear Sam, I sincerely apologize..." }
    ↓
Final Output: { final_reply: "Dear Sam, I sincerely apologize..." }
```

### What to Observe

1. Click **Input — Customer Email** → see the starting data
2. Click each **Branch** node → see different analyses running on the same input
3. Click **Merge (A+B)+C** → switch to JSON view to see all three fields combined
4. Click **Finalize** → see how the final LLM uses `{{ $json.facts_json }}`, `{{ $json.sentiment_json }}`, and `{{ $json.draft_reply }}`

::::{dropdown} 🔍 How does Merge combine branches? See the data flow
:color: info

The Merge node waits for all branches to complete, then combines their outputs into one item.

**Important:** Despite the visual layout, n8n runs branches **sequentially** (A → B → C), not in parallel.

```
                    ┌─────────────────────────────────┐
                    │        INPUT (same for all)     │
                    │ { "email_subject": "Help!",     │
                    │   "email_body": "Can't login" } │
                    └─────────────────────────────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     ▼              ▼              ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │  Branch A    │ │  Branch B    │ │  Branch C    │
            │  (Facts)     │ │  (Sentiment) │ │  (Draft)     │
            │  runs 1st    │ │  runs 2nd    │ │  runs 3rd    │
            └──────────────┘ └──────────────┘ └──────────────┘
                     │              │              │
                     ▼              ▼              ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ {            │ │ {            │ │ {            │
            │  "facts_json"│ │  "sentiment_ │ │  "draft_     │
            │  : "{...}"   │ │   json":     │ │   reply":    │
            │ }            │ │   "{...}"    │ │   "Hi Sam.." │
            │              │ │ }            │ │ }            │
            └──────────────┘ └──────────────┘ └──────────────┘
                     │              │              │
                     └──────────────┼──────────────┘
                                    ▼
                          ┌─────────────────┐
                          │      MERGE      │
                          │  (Combine by    │
                          │   Position)     │
                          └─────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │         MERGED OUTPUT           │
                    │ {                               │
                    │   "facts_json": "{...}",        │
                    │   "sentiment_json": "{...}",    │
                    │   "draft_reply": "Hi Sam..."    │
                    │ }                               │
                    │                                 │
                    │ ✅ All three fields combined!   │
                    └─────────────────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │ Finalize LLM    │
                          │ uses ALL fields │
                          └─────────────────┘
```

**Key insight:** Even though execution is sequential, the pattern is valuable for organizing independent analyses. The Merge node combines all results so the final LLM can use all the information.

::::
