# Pattern 4: Human-in-the-Loop

**What you will build:** A support ticket arrives. The AI drafts a reply, then the workflow pauses and waits for a human to review and approve before sending.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Manual Trigger │────▶│   Edit Fields   │────▶│  LLM: Draft     │────▶│  ⏸️ Wait Node   │────▶│  Output: Send   │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                                                                              │
                                                                        Human reviews
                                                                        & approves
```

**New node:** **Wait** — pauses the workflow until an external signal resumes it.

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/04_human_in_the_loop.json
> ```
>
> **Download:** {download}`04_human_in_the_loop.json <_static/workflows/04_human_in_the_loop.json>`

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

1. Click **Workflows** → **Add Workflow**
2. Rename it to "Human-in-the-Loop Practice"

### Step 2: Add the trigger and input

1. Add **Manual Trigger**
2. Add **Edit Fields** → rename to `Input — Support Ticket`
3. Add three String fields:

| Name | Value |
|------|-------|
| `ticket_subject` | `Urgent: Need refund for duplicate charge` |
| `ticket_body` | `Hi, I was charged twice for order #12345. The second charge of $89.99 appeared yesterday. Please refund ASAP as this is causing overdraft fees. Thanks, Maria` |
| `customer_email` | `maria@example.com` |

### Step 3: Add the Draft LLM

1. Add **Basic LLM Chain** → rename to `Step 1 — Draft Response`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression):
     ```
     Subject: {{ $json.ticket_subject }}
     Body:
     {{ $json.ticket_body }}
     Customer: {{ $json.customer_email }}

     Draft the reply:
     ```
3. Add System Message:
   ```
   You are a customer support agent.
   Draft a professional email reply.

   Rules:
   - Acknowledge the issue with empathy
   - Confirm specific details (order #, amount)
   - Explain the refund process and timeline
   - Apologize for the inconvenience
   - Keep under 150 words

   Output ONLY the email body (no subject line).
   ```
4. Add your Chat Model

### Step 4: Store the draft

1. Add **Edit Fields** → rename to `Store Draft + Status`
2. Add five fields:
   - `draft_response`: `{{ $json.text }}`
   - `customer_email`: `{{ $node['Input — Support Ticket'].json.customer_email }}`
   - `ticket_subject`: `{{ $node['Input — Support Ticket'].json.ticket_subject }}`
   - `status`: `pending_approval`
   - `drafted_at`: `{{ $now.format('yyyy-MM-dd HH:mm') }}`

### Step 5: Add the Wait node

1. Add **Wait** → rename to `Wait — Human Approval`
2. Configure:
   - **Resume**: `On Webhook Call`
   - **Webhook Suffix** (in Options): `{{ $execution.id }}`

### Step 6: Add the Output node

1. Add **Edit Fields** → rename to `Output — Approved Response`
2. Add fields:
   - `final_response`: `{{ $node['Store Draft + Status'].json.draft_response }}`
   - `send_to`: `{{ $node['Store Draft + Status'].json.customer_email }}`
   - `subject`: `Re: {{ $node['Store Draft + Status'].json.ticket_subject }}`
   - `status`: `approved_and_sent`
3. Enable **Keep Only Set**

### Step 7: Test

1. Click **Execute Workflow** — it pauses at Wait
2. Click the **Wait node** → copy the **Test URL**
3. Open that URL in your browser → workflow resumes

::::

### Meet the Node: Wait

This pattern introduces a new node: **Wait**.

| Property | Description |
|----------|-------------|
| **Purpose** | Pauses workflow execution until resumed |
| **How it works** | Stops the workflow, waits for an external signal to continue |
| **Use cases** | Human approval, waiting for external events, timed delays |

**Resume Methods:**
| Method | Description |
|--------|-------------|
| **Webhook** | Resume when a specific URL is called (for approvals) |
| **On a specific date** | Resume at a scheduled time |
| **After time interval** | Resume after X minutes/hours |

In this workflow, we use **Webhook** mode: the workflow pauses until someone calls the approval URL.

**See the **Node Toolbox** appendix for full documentation.**

### What Problem This Solves

AI-generated content should often be reviewed before taking action. A support reply, a customer email, or a social media post might need human approval before sending. This pattern drafts the content with AI, then **pauses** for a human to review and approve.

**Why this matters:**
- Prevents embarrassing AI mistakes from reaching customers
- Gives humans control over final decisions
- Required in many industries (legal, healthcare, finance)

### Node-by-Node Walkthrough

<div style="overflow: auto; max-height: 250px; border: 1px solid #ddd; border-radius: 4px; padding: 10px; margin-bottom: 15px; background: #f8f8f8;">
<pre style="margin: 0; white-space: pre;">
┌──────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│   Manual Trigger │────▶│ Input — Support Ticket │────▶│  Step 1 — Draft        │────▶│  Store Draft + Status  │
└──────────────────┘     └────────────────────────┘     └────────────────────────┘     └────────────────────────┘
                                                                                                │
                                                                                                ▼
                                                                                       ┌────────────────────────┐
                                                                                       │  ⏸️ Wait — Approval    │
                                                                                       │     (pauses here)      │
                                                                                       └────────────────────────┘
                                                                                                │
                                                                                          Human approves
                                                                                                │
                                                                                                ▼
                                                                                       ┌────────────────────────┐
                                                                                       │  Output — Approved     │
                                                                                       │  Response              │
                                                                                       └────────────────────────┘
</pre>
</div>

| Node | Type | What it does |
|------|------|-------------|
| **Run: Human Approval** | Manual Trigger | Starts the workflow |
| **Input — Support Ticket** | Set | Creates fields: `ticket_subject`, `ticket_body`, `customer_email` |
| **Step 1 — Draft Response** | Basic LLM Chain | Generates reply draft → outputs `text` |
| **Store Draft + Status** | Set | Saves draft, sets `status: "pending_approval"`, and records `drafted_at` timestamp |
| **Wait — Human Approval** | Wait | Pauses workflow until approval webhook is called |
| **Output — Approved Response** | Set | Formats final output with `status: "approved_and_sent"` |

### Prompt Used

**Step 1 — Draft Response:**
```
System: You are a customer support agent.
Draft a professional email reply.

Rules:
- Acknowledge the issue with empathy
- Confirm specific details (order #, amount)
- Explain the refund process and timeline
- Apologize for the inconvenience
- Keep under 150 words

Output ONLY the email body (no subject line).
```

### How to Resume the Wait Node

The Wait node in **webhook mode** creates a unique URL for this execution.

**To test (resume manually):**
1. Run the workflow — it pauses at the Wait node
2. Click the **Wait node**
3. Copy the **Test URL** from the right panel
4. Open that URL in your browser — workflow resumes

**In production:** Send the webhook URL to Slack/Email with an "Approve" button. When clicked, the workflow continues.

### Data Flow

```
INPUT                          OUTPUT
─────                          ──────
Trigger: { }
    ↓
Support Ticket: { ticket_subject, ticket_body, customer_email }
    ↓
Draft LLM: { text: "Dear Maria, I sincerely apologize..." }
    ↓
Store Draft: { 
  draft_response: "Dear Maria, I sincerely apologize...",
  customer_email: "maria@example.com",
  ticket_subject: "Urgent: Need refund...",
  status: "pending_approval",
  drafted_at: "2025-01-25 14:30"
}
    ↓
⏸️ PAUSE — workflow waits here
    ↓
(human opens Test URL in browser)
    ↓
Output: { 
  final_response: "Dear Maria, I sincerely apologize...",
  send_to: "maria@example.com",
  subject: "Re: Urgent: Need refund...",
  status: "approved_and_sent"
}
```

**Note:** The `drafted_at` field uses `{{ $now.format('yyyy-MM-dd HH:mm') }}` — a built-in expression to record when the draft was created. This helps reviewers know if a draft is fresh or has been waiting for hours.

### What to Observe

1. Click **Step 1 — Draft Response** → see the AI-generated reply
2. Click **Store Draft + Status** → see `status: "pending_approval"` and `drafted_at` timestamp
3. Notice the workflow **pauses** at the Wait node
4. Copy Test URL, open in browser → workflow continues
5. Click **Output** → see `status: "approved_and_sent"`

### Production Integration Ideas

| Integration | How to implement |
|-------------|-----------------|
| **Slack approval** | Before Wait: send draft to Slack with interactive buttons. Button calls webhook. |
| **Email approval** | Send draft email with "Approve" link that calls the webhook URL |
| **Dashboard** | Store draft in database, show in admin panel with Approve/Reject buttons |

The Wait node's webhook URL can include the execution ID (`{{ $execution.id }}`) to route approvals to the correct paused workflow.
