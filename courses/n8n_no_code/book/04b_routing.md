# Pattern 2: Routing

**What you will build:** A support ticket arrives. The workflow classifies it (refund, order status, or general support) and sends it to a specialist prompt that writes the appropriate reply.

```
                                                 ┌─────────────────────────┐
                                            ┌───▶│ Refund Specialist       │
┌─────────────────┐     ┌─────────────────┐ │    └─────────────────────────┘
│  Manual Trigger │────▶│ Router — Choose │─┼───▶│ Order Status Specialist │
└─────────────────┘     │ Route           │ │    └─────────────────────────┘
                        └─────────────────┘ └───▶│ Support Specialist      │
                                                 └─────────────────────────┘
```

**New node:** **Switch** — checks a value and sends data to the matching branch.

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/02_routing.json
> ```
> 
> **Download:** {download}`02_routing.json <_static/workflows/02_routing.json>`

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

1. Click **Workflows** → **Add Workflow**
2. Rename it to "Routing Practice"

### Step 2: Add the trigger and input

1. Add **Manual Trigger**
2. Add **Edit Fields** → rename to `Input — Support Ticket`
3. Add two String fields:

| Name | Value |
|------|-------|
| `ticket_subject` | `Refund request — charged twice` |
| `ticket_body` | `Hi team,\nI was charged twice for order #A-10492.\nPlease refund the extra charge. I can provide a screenshot if needed.\nThanks,\nJamie` |

### Step 3: Add the Router (Basic LLM Chain)

1. Add **Basic LLM Chain** → rename to `Router — Choose Route`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression):
     ```
     Subject: {{ $json.ticket_subject }}
     Body:
     {{ $json.ticket_body }}

     Route label:
     ```
3. Add System Message:
   ```
   You route customer support tickets.

   Choose exactly ONE route label, lowercase, no punctuation:
   - refund
   - order_status
   - support

   Return ONLY the label.
   ```
4. Add your Chat Model

### Step 4: Add Store Route (Edit Fields)

1. Add **Edit Fields** → rename to `Store Route`
2. Add field:
   - Name: `route`
   - Value (Expression): `{{ $json.text.trim() }}`

### Step 5: Add the Switch node

1. Add **Switch** → rename to `Switch — Route`
2. Set **Mode**: Rules
3. Add 3 rules:

| Rule | Value 1 | Operation | Value 2 | Output Name |
|------|---------|-----------|---------|-------------|
| 1 | `{{ $json.route }}` | Equals | `refund` | refund |
| 2 | `{{ $json.route }}` | Equals | `order_status` | order_status |
| 3 | `{{ $json.route }}` | Equals | `support` | support |

### Step 6: Add the Specialist LLMs (one per branch)

For each Switch output, add a **Basic LLM Chain**:

**Refund Specialist:**
- Prompt (Expression):
  ```
  Subject: {{ $node['Input — Support Ticket'].json.ticket_subject }}
  Body:
  {{ $node['Input — Support Ticket'].json.ticket_body }}

  Write the reply:
  ```
- System:
  ```
  You are a customer support specialist for refunds.
  Write a short, professional reply.

  Rules:
  - Acknowledge the issue
  - Ask for any missing info (only if needed)
  - Explain next steps and expected timeline
  - Keep it under 120 words

  Output ONLY the reply.
  ```

**Order Status Specialist:**
- Same prompt structure
- System:
  ```
  You are a customer support specialist for order status.
  Write a short, professional reply.

  Rules:
  - Confirm you are checking the order
  - Ask for order number if missing
  - Provide what you can and what you still need
  - Keep it under 120 words

  Output ONLY the reply.
  ```

**Support Specialist:**
- Same prompt structure
- System:
  ```
  You are a general customer support specialist.
  Write a short, professional reply.

  Rules:
  - Clarify the problem
  - Ask 1–2 targeted questions (only if needed)
  - Offer a next step
  - Keep it under 120 words

  Output ONLY the reply.
  ```

### Step 7: Add Output nodes

For each specialist, add **Edit Fields** with:
- `reply`: `{{ $json.text }}`
- `route`: the branch name (e.g., `refund`)
- Enable **Keep Only Set**

### Step 8: Test

1. Click **Execute Workflow**
2. Check which branch received data (only one should have output)

::::

### Meet the Node: Switch

This pattern introduces a new node: **Switch**.

| Property | Description |
|----------|-------------|
| **Purpose** | Routes data to different branches based on conditions |
| **How it works** | Checks a value and sends data to the matching output |
| **Multiple outputs** | Each condition creates a separate output branch (solid line) |

**Configuration:**
1. **Mode:** Choose "Rules" for condition-based routing
2. **Data Type:** Usually "String" when routing on text values
3. **Value 1:** The field to check, e.g., `{{ $json.route }}`
4. **Operation:** Usually "Equals" for exact matching
5. **Value 2:** The value to match, e.g., `refund`

Add more rules to create more branches. The Switch sends data only to the branch where the condition matches.

**See the **Node Toolbox** appendix for full documentation.**

### What Problem This Solves

Different inputs need different handling. A support ticket about refunds should go to a refund specialist prompt, while an order status question goes elsewhere. Routing uses an LLM to classify the input, then a Switch node sends it down the right path.

### Node-by-Node Walkthrough

<div style="overflow: auto; max-height: 300px; border: 1px solid #ddd; border-radius: 4px; padding: 10px; margin-bottom: 15px; background: #f8f8f8;">
<pre style="margin: 0; white-space: pre;">
┌──────────────────┐     ┌────────────────────────┐     ┌──────────────────────┐     ┌───────────────┐     ┌────────────────┐
│   Manual Trigger │────▶│ Input — Support Ticket │────▶│  Router — Classify   │────▶│  Store Route  │────▶│ Switch — Route │───┐
└──────────────────┘     └────────────────────────┘     └──────────────────────┘     └───────────────┘     └────────────────┘   │
                                                                                                                                │
        ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        ├────▶┌─────────────────────────────┐────▶┌───────────────────────┐
        │     │   Refund Specialist         │     │   Output — Refund     │
        │     └─────────────────────────────┘     └───────────────────────┘
        │
        ├────▶┌─────────────────────────────┐────▶┌───────────────────────┐
        │     │   Order Status Specialist   │     │   Output — Order      │
        │     └─────────────────────────────┘     └───────────────────────┘
        │
        └────▶┌─────────────────────────────┐────▶┌───────────────────────┐
              │   Support Specialist        │     │   Output — Support    │
              └─────────────────────────────┘     └───────────────────────┘
</pre>
</div>

| Node | Type | What it does |
|------|------|-------------|
| **Run: Ticket Routing** | Manual Trigger | Starts the workflow |
| **Input — Support Ticket** | Set | Creates fields: `ticket_subject`, `ticket_body` |
| **Router — Choose Route** | Basic LLM Chain | Classifies ticket → outputs `text` (e.g., `refund`) |
| **Store Route** | Set | Saves `{{ $json.text.trim() }}` as `route` |
| **Switch — Route** | Switch | Checks `{{ $json.route }}` and sends to one branch |
| **Refund Specialist — Draft Reply** | Basic LLM Chain | Writes refund-specific reply → outputs `text` |
| **Order Status Specialist — Draft Reply** | Basic LLM Chain | Writes order status reply → outputs `text` |
| **Support Specialist — Draft Reply** | Basic LLM Chain | Writes general support reply → outputs `text` |
| **Output — Refund Reply** | Set | Saves `{{ $json.text }}` as `reply`, adds `route: "refund"` |
| **Output — Order Status Reply** | Set | Saves `{{ $json.text }}` as `reply`, adds `route: "order_status"` |
| **Output — Support Reply** | Set | Saves `{{ $json.text }}` as `reply`, adds `route: "support"` |

### Prompts Used

**Router — Choose Route (the classifier):**
```
System: You route customer support tickets.

Choose exactly ONE route label, lowercase, no punctuation:
- refund
- order_status
- support

Return ONLY the label.
```

**Why this works:** The prompt forces clean output (lowercase, no punctuation, ONLY the label) so the Switch node can match exactly.

**Refund Specialist:**
```
System: You are a customer support specialist for refunds.
Write a short, professional reply.

Rules:
- Acknowledge the issue
- Ask for any missing info (only if needed)
- Explain next steps and expected timeline
- Keep it under 120 words

Output ONLY the reply.
```

**Order Status Specialist:**
```
System: You are a customer support specialist for order status.
Write a short, professional reply.

Rules:
- Confirm you are checking the order
- Ask for order number if missing
- Provide what you can and what you still need
- Keep it under 120 words

Output ONLY the reply.
```

**Support Specialist:**
```
System: You are a general customer support specialist.
Write a short, professional reply.

Rules:
- Clarify the problem
- Ask 1–2 targeted questions (only if needed)
- Offer a next step
- Keep it under 120 words

Output ONLY the reply.
```

### Key Expression: Accessing Earlier Node Data

The specialist nodes need the original ticket data, but they come after the Switch. They use this expression pattern:

```
{{ $node['Input — Support Ticket'].json.ticket_subject }}
{{ $node['Input — Support Ticket'].json.ticket_body }}
```

This accesses data from a specific earlier node by name. Useful when you need to "reach back" past intermediate nodes.

### Data Flow

```
INPUT                          OUTPUT
─────                          ──────
Trigger: { }
    ↓
Support Ticket: { ticket_subject, ticket_body }
    ↓
Router LLM: { text: "refund" }
    ↓
Store Route: { text: "refund", route: "refund" }
    ↓
Switch: routes to ONE branch based on {{ $json.route }}
    ↓
[Refund Specialist]: { text: "Dear Jamie, I apologize..." }
    ↓                 (accesses original ticket via $node['Input — Support Ticket'])
Output — Refund Reply: { reply: "Dear Jamie, I apologize...", route: "refund" }
```

**Note:** The original `ticket_subject` and `ticket_body` are NOT passed through the Switch. The Specialist nodes access them using `$node['Input — Support Ticket'].json`.

### What to Observe

1. Click **Router — Choose Route** → see the classification in `text` (e.g., `refund`)
2. Click **Store Route** → see `route` field added
3. Click **Switch — Route** → only ONE output branch has data
4. Click the active specialist node → see the tailored reply

::::{dropdown} 🔍 How does the Switch node route data? See the branching
:color: info

The Switch node checks a field value and sends data to **only one** matching branch:

```
                         ┌─────────────────────────────────────────────┐
                         │ DATA BEFORE SWITCH                          │
                         │ {                                           │
                         │   "text": "refund",                         │
                         │   "route": "refund"                         │
                         │ }                                           │
                         │                                             │
                         │ ⚠️ Note: ticket_subject and ticket_body     │
                         │ are NOT here! They're accessed via          │
                         │ $node['Input — Support Ticket'].json        │
                         └─────────────────────────────────────────────┘
                                              │
                                              ▼
                                    ┌───────────────────┐
                                    │      SWITCH       │
                                    │                   │
                                    │  Checks: route    │
                                    │  Value: "refund"  │
                                    └───────────────────┘
                                     /        |        \
                                    /         |         \
                         "refund"  /    "order_status"   \  "support"
                                  /           |           \
                                 ▼            ▼            ▼
                    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
                    │ ✅ HAS DATA      │ │ ❌ EMPTY     │ │ ❌ EMPTY     │
                    │                  │ │              │ │              │
                    │ {                │ │    { }       │ │    { }       │
                    │  "text":         │ │              │ │              │
                    │    "refund",     │ │  No match,   │ │  No match,   │
                    │  "route":        │ │  no data     │ │  no data     │
                    │    "refund"      │ │  flows here  │ │  flows here  │
                    │ }                │ │              │ │              │
                    └──────────────────┘ └──────────────┘ └──────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │ Refund           │
                    │ Specialist LLM   │
                    │                  │
                    │ Uses expression: │
                    │ $node['Input —   │
                    │ Support Ticket'] │
                    │ .json.ticket_body│
                    └──────────────────┘
```

**Key insights:** 
- Only ONE branch receives data — the others are empty
- The original `ticket_subject` and `ticket_body` are NOT in the Switch data
- Specialist nodes "reach back" to get original data using `$node['Input — Support Ticket'].json`

::::

---

**Where this goes next:** routing picks *one* predefined branch. When you need the AI to *dynamically* decide which specialists to run, in what order, and then combine their results, that is the **orchestrator-workers** pattern in the [Multi-Agent Systems](10_multi_agent_systems) chapter — where a sub-agent is just an agent used as a tool.
