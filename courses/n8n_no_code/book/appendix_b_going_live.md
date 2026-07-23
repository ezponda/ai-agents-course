# Appendix B: Going Live

Your workflows work in Test mode. This appendix shows how to make them run automatically —
and what to do when things go wrong.

**When to read this:**
- You've built workflows and want them to run on their own
- You're about to share a workflow with someone (webhook URL, scheduled job)
- You want to know what happens when a workflow fails

---

## From Test to Production

Every workflow you've built uses **Manual Trigger**. You click a button, it runs. In the real world, nobody clicks a button — workflows need to start on their own.

**Publishing a workflow** means clicking *Publish* in the top-right corner of the editor. Once published, the workflow's trigger fires automatically (on a schedule, when a webhook receives data, etc.). Until you publish, your draft only runs when you click *Execute Workflow* manually.

### Execution Types

| Type | When it runs | Where you see results |
|------|-------------|------------------------|
| **Manual** | You click "Execute Workflow" | Output Panel (live) |
| **Production** | Trigger fires automatically | Execution History |

To see past production runs: **Left sidebar → Executions**.

---

## Schedule Trigger

**New node: Schedule Trigger** — runs your workflow on a timer.

### Meet the Node

| Parameter | Description |
|-----------|-------------|
| **Trigger Interval** | How often: Every minute, hour, day, week, month, or cron |
| **Hour / Minute** | When exactly (e.g., 9:00 AM) |

**Example:** "Run every day at 9 AM."

**Docs:** [Schedule Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/)

---

### Workflow: Scheduled Email Analysis

This takes the Parallelization workflow (Pattern 3) and replaces Manual Trigger with Schedule Trigger. Everything else stays the same — one node swap, and it runs by itself.

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/going_live_schedule.json
> ```
>
> **Download:** {download}`going_live_schedule.json <_static/workflows/going_live_schedule.json>`

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

Start from the Parallelization workflow (`03_parallelization.json`).

### Step 1: Delete the Manual Trigger node

Select the **Run: Parallelization** node and delete it.

### Step 2: Add Schedule Trigger

Add a **Schedule Trigger** node and configure it:

| Parameter | Value |
|-----------|-------|
| **Trigger Interval** | Days |
| **Days Between Triggers** | 1 |
| **Trigger at Hour** | 9 |
| **Trigger at Minute** | 0 |

### Step 3: Connect

Connect **Schedule Trigger** → **Input — Customer Email**.

That's it — one node swap.

::::

### Data Flow

```
┌──────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│ Schedule Trigger  │────▶│ Input —      │────▶│ Branch A — Facts    │──┐
│ (daily, 9 AM)    │     │ Customer     │  ┌──│ Branch B — Sentiment│  ├─▶ Merge ─▶ Finalize ─▶ Output
└──────────────────┘     │ Email        │  │  │ Branch C — Draft    │──┘
                         └──────────────┘  │  └─────────────────────┘
                                           └──────────────────────────┘
```

### What to observe

- Publish the workflow (click *Publish* in the top-right)
- Wait for the scheduled time (or set the interval to "every minute" for testing)
- Check **Execution History** — the workflow ran without you clicking anything

```{note}
In a real setup, the Input node would be replaced by a Gmail Trigger or IMAP node that fetches actual emails. We keep the hardcoded input so the workflow runs without external credentials.
```

---

## Webhook Trigger

**New node: Webhook** — runs your workflow when an external service sends a request.

### Meet the Node

| Parameter | Description |
|-----------|-------------|
| **HTTP Method** | GET or POST (usually POST for receiving data) |
| **Path** | The URL path (e.g., `analyze`) |
| **Authentication** | None, Basic Auth, Header Auth |

**Docs:** [Webhook Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)

---

### The most important concept: Test URL vs Production URL

| | Test URL | Production URL |
|---|----------|----------------|
| **When it works** | Only while editor is open + “Listen for Test Event” | Only when workflow is published |
| **URL format** | `/webhook-test/your-path` | `/webhook/your-path` |
| **Use for** | Development and debugging | Real integrations |
| **Shows output in** | Output Panel (live) | Execution History |

---

### Workflow: Webhook Email Analyzer

Same Parallelization workflow but with a Webhook Trigger. Students test it with curl or any HTTP tool.

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/going_live_webhook.json
> ```
>
> **Download:** {download}`going_live_webhook.json <_static/workflows/going_live_webhook.json>`

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

Start from the Parallelization workflow (`03_parallelization.json`).

### Step 1: Delete the Manual Trigger node

Select the **Run: Parallelization** node and delete it.

### Step 2: Add Webhook node

Add a **Webhook** node and configure it:

| Parameter | Value |
|-----------|-------|
| **HTTP Method** | POST |
| **Path** | `analyze` |

### Step 3: Connect

Connect **Webhook** → **Input — Customer Email**.

### Step 4: Update the Input node

Change the **Input — Customer Email** fields from fixed values to expressions that read from the webhook body:

| Field | Mode | Expression |
|-------|------|------------|
| `email_subject` | Expression | `{{ $json.body.subject }}` |
| `email_body` | Expression | `{{ $json.body.body }}` |

::::

### Data Flow

```
┌──────────────────┐     ┌──────────────┐
│ Webhook Trigger  │────▶│ Input —      │────▶ (same as before)
│ POST /analyze    │     │ Customer     │
└──────────────────┘     │ Email        │
                         └──────────────┘
```

### How to test

1. Open the workflow in the editor
2. Click the **Webhook** node and click **Listen for Test Event**
3. In a terminal, run:

```bash
curl -X POST "http://localhost:5678/webhook-test/analyze" \
  -H "Content-Type: application/json" \
  -d '{"subject": "Can'\''t access my account", "body": "I reset my password twice..."}'
```

4. The workflow executes and you see the results in the Output Panel

---

## When Things Go Wrong — Error Handling

Three levels, from simplest to most robust.

---

### 1. See what failure looks like

Change the model name to `nonexistent-model` in any workflow. Run it. Open **Execution History** and look at the red failed execution.

Execution History shows:
- Which node failed
- The error message
- The data at that point

This is your primary debugging tool.

---

### 2. Error Workflow — get notified when something breaks

An **Error Workflow** is a separate workflow that runs automatically when any other workflow fails.

#### Workflow: Error Notifier

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/going_live_error.json
> ```
>
> **Download:** {download}`going_live_error.json <_static/workflows/going_live_error.json>`

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create new workflow

Create a new workflow and name it **Error Notifier**.

### Step 2: Add Error Trigger

Add an **Error Trigger** node. No configuration needed — it fires when a linked workflow fails.

### Step 3: Add Edit Fields (Format Error Info)

Add an **Edit Fields (Set)** node and configure these fields:

| Name | Mode | Value |
|------|------|-------|
| `workflow_name` | Expression | `{{ $json.execution.workflowData.name }}` |
| `error_message` | Expression | `{{ $json.execution.error.message }}` |
| `failed_at` | Expression | `{{ $json.execution.startedAt }}` |

### Step 4: Add Edit Fields (Output)

Add another **Edit Fields (Set)** node. Enable **Keep Only Set** and pass through the three fields:

| Name | Mode | Value |
|------|------|-------|
| `workflow_name` | Expression | `{{ $json.workflow_name }}` |
| `error_message` | Expression | `{{ $json.error_message }}` |
| `failed_at` | Expression | `{{ $json.failed_at }}` |

### Step 5: Connect all three nodes

**Error Trigger** → **Format Error Info** → **Output**

::::

#### Data Flow

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────┐
│ Error Trigger    │────▶│ Format Error     │────▶│ Output       │
│                  │     │ Info             │     │              │
└──────────────────┘     └──────────────────┘     └──────────────┘
```

- **Error Trigger** fires when a linked workflow fails
- **Format Error Info** extracts `workflow_name`, `error_message`, and `failed_at`
- **Output** stores the formatted error info with **Keep Only Set** enabled
- In production: replace Output with a Slack, Email, or Discord node to get actual notifications

#### How to link it

Go to any workflow → **Settings** (gear icon) → **Error Workflow** → select **Error Notifier**.

Now when that workflow fails, the Error Notifier runs automatically.

---

### 3. Continue On Error — don’t let one node kill the whole workflow

This is a per-node setting. Open any node → **Settings** tab → **On Error** → select **Continue Using Error Output**.

**Example:** If the sentiment analysis LLM times out, the rest of the workflow still runs with facts + draft (just without sentiment).

This is useful when some branches are nice-to-have but not critical. The workflow continues with whatever data it has.

---

## Production Checklist

A reusable reference for taking any workflow to production.

| Step | Check |
|------|-------|
| 1 | Replace Manual Trigger with a real trigger (Schedule, Webhook, or App trigger) |
| 2 | Create an Error Workflow and link it in Settings |
| 3 | If using Webhook: test with the **Production URL** (not Test URL) |
| 4 | Set **Max Iterations** on all AI Agent nodes (5–10) |
| 5 | Publish the workflow (click *Publish* in the top-right) |
| 6 | Check **Execution History** after the first automatic run |
| 7 | Verify credentials are stored in n8n’s credential system |

---

## Deploying n8n

Everything so far runs on your computer. When you close n8n Desktop, your workflows stop. To run them 24/7, you need n8n running on a server.

There are three main options:

| Option | Cost | Setup time | You manage the server? |
|--------|------|-----------|------------------------|
| **n8n Cloud** | From ~€20/mo ([see pricing](https://n8n.io/pricing/)) | 2 min | No |
| **Railway** | ~$5/mo minimum ([see pricing](https://railway.com/pricing)) | 5 min | No |
| **VPS + Docker** | $4–12/mo | 30–60 min | Yes |

### What Changes in Production

When n8n runs on a server instead of your laptop, two things change:

1. **Webhook URLs become public.** Your local `http://localhost:5678/webhook/...` becomes `https://your-domain.com/webhook/...` — accessible from anywhere.

2. **Workflows must be published.** Click *Publish* in the top-right corner. Triggers (Schedule, Webhook, Chat) only fire in production when the workflow is published — drafts only run on manual execute.

### Hands-on Deployment

**Project 5: Deploy to Production** walks you through deploying a workflow step by step — Railway (recommended for this course) and n8n Cloud. See [](project_5_deploy_to_production) for the full guide.

### Going Further

| Resource | Link |
|----------|------|
| n8n hosting options | [docs.n8n.io/hosting](https://docs.n8n.io/hosting/) |
| Docker Compose setup | [docs.n8n.io/hosting/installation/docker](https://docs.n8n.io/hosting/installation/docker/) |
| n8n Cloud | [n8n.io/cloud](https://n8n.io/cloud/) |
| Railway n8n template | [railway.com/deploy/n8n](https://railway.com/deploy/n8n) |
| Environment variables | [docs.n8n.io/hosting/configuration/environment-variables](https://docs.n8n.io/hosting/configuration/environment-variables/) |
