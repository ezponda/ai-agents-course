# Reliable Tools and Sub-workflows

In [Tool Calling](07_tool_calling) you gave an agent a tool and let it decide when to use it. That's the fun part. This chapter is the **grown-up** part: how to make a tool you'd actually trust in production — one that talks to a real API, checks who's asking, enforces the rules in code, and asks a human before doing anything expensive.

The whole idea in one line:

> **The AI handles ambiguity. The workflow controls the deterministic rules.**

We'll build up in five moves:

1. Make a **deterministic** HTTP request (run it yourself, no AI).
2. **Validate and normalise** its inputs.
3. Wrap the deterministic logic in a **reusable sub-workflow**.
4. Expose that one **safe, high-level** sub-workflow to the agent as a tool.
5. Require **human approval** for the high-impact call.

| What you'll learn | Where it comes from |
|---|---|
| **Deterministic HTTP** — verbs, headers, body, credentials, pagination, timeouts, error codes | Deepens the HTTP tool ([Tool Calling](07_tool_calling), [Daily Digest](project_4_daily_digest)) |
| **Safe vs. unsafe `$fromAI()`** — what the model may and may not control | Deepens [Tool Calling](07_tool_calling) |
| **Sub-workflows** — explicit inputs, validation and credentials kept *inside* | New nodes |
| **Call n8n Workflow Tool** — expose one safe tool instead of many risky ones | New node |
| **Ownership checks** — verify the caller is allowed *before* acting | New |
| **Native tool approval** vs. content approval | Deepens [Human in the Loop](04d_human_in_the_loop) |

**Workflows in this chapter:**

| File | What it does | GitHub Link |
|------|-------------|-------------|
| `20_cancel_appointment_subworkflow.json` | The safe callee: validate → exists? → ownership → write → structured result | [View](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/20_cancel_appointment_subworkflow.json) |
| `21_agent_cancels_via_tool.json` | The agent that calls it as one safe tool, approval-ready | [View](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/21_agent_cancels_via_tool.json) |

**Requirements:** an **OpenRouter API key** and **n8n 2.6+** (native human review for AI tool calls; Data Tables need 1.113+). One Data Table, `appointments`. No other credentials.

---

## Move 1 — a deterministic HTTP request (before any AI)

Before you *ever* let an agent call an API, call it yourself in a plain **HTTP Request** node and get it working. An agent that wraps a broken request just fails more creatively. Here's the production checklist for that node.

| Setting | What to know (non-technical) |
|---|---|
| **Method** | `GET` reads data; `POST` creates; `PATCH` updates; `DELETE` removes. Reads are safe to retry; writes are not (Move 5). |
| **Headers** | Extra info sent with the request (e.g. `Content-Type: application/json`). Usually set for you. |
| **Body** | The JSON you send on a `POST`/`PATCH` — the data you want to create or change. |
| **Authentication** | Pick **Predefined** (Google, Slack…) or **Generic Credential** (API key header, Bearer token). **Store the key as an n8n Credential — never paste it in the URL.** |
| **Pagination** (Options) | Big lists come in **pages**. Turn on pagination so n8n fetches page after page automatically instead of only the first 20 results. |
| **Timeout** (Options) | How long to wait before giving up. Set one (e.g. 10s) so a hung API can't freeze your workflow forever. |

**Reading the response — the status code tells you what happened:**

| Code | Meaning | What to do |
|---|---|---|
| `200` | OK | Carry on |
| `401` | Unauthenticated | Your credential is missing or wrong |
| `403` | Forbidden | Authenticated, but not *allowed* to do this (a permissions problem) |
| `404` | Not found | Wrong URL or the record doesn't exist |
| `429` | Too many requests | You hit the **rate limit** — slow down, wait, retry (see [Production Reliability](appendix_b2_production_reliability)) |
| `500` | Server error | Their fault, not yours — retry later |

```{tip}
**Credentials live in n8n, not in the workflow.** When you create an HTTP credential, n8n stores the secret encrypted and only injects it at run time. That means you can share or export a workflow **without** leaking your keys — and the AI, which only ever sees the workflow, never sees the secret.
```

---

## Move 2 — safe vs. unsafe `$fromAI()`

`$fromAI()` ([Tool Calling](07_tool_calling)) lets the model fill in a value at run time — great for the *ambiguous* parts of a request (which city? which record?). But some values must **never** come from the model. The rule:

| The model MAY provide… | The model must NEVER provide… |
|---|---|
| A search term, a question | **Credentials / API keys** |
| Which record to look up (an id it was shown) | **The base URL** (it could point the tool anywhere) |
| A short, low-risk field | **User or tenant identity** (`customer_id`) — that comes from a trusted identity source |
| | **Permission-sensitive fields** (role, `is_admin`, price, `status`) |
| | **The whole request body** (an unrestricted body is a blank cheque) |
| | **Hard business rules** ("never refund more than paid") — those live in code |

The test is simple: *what's the worst thing that happens if the model gets this value wrong or is tricked into a bad value?* If the answer is "it charges the wrong card" or "it reads another customer's data", that value does **not** belong in `$fromAI()`. Hardcode it, take it from a trusted identity source, or enforce it in a node.

```{warning}
**A Code tool that runs model-written code (like the [Ask Your Data](project_2_ask_your_data) interpreter) is the extreme case of this.** Letting the model generate and `eval` code is powerful but hands it a very sharp tool — treat it as a **security boundary**: run it with least privilege, never near real credentials or write access, and prefer a **fixed sub-workflow** (below) whenever the operation is known in advance. Most "tools" don't need arbitrary code — they need one safe, specific action.
```

---

## Moves 3 & 4 — a reusable sub-workflow, exposed as one safe tool

Here's the key architectural move. Instead of giving the agent three raw Data Table tools (find, update, delete) and *hoping* it uses them correctly, you build **one** deterministic sub-workflow — `cancel_appointment` — that does the whole job safely, and expose just that.

```
AI Agent
   │  calls one tool: cancel_appointment(appointment_id)
   ▼
cancel_appointment  (a normal n8n sub-workflow — no AI inside)
   ├─ validates the inputs         (required fields; action must be 'cancel')
   ├─ checks the appointment EXISTS (else returns not_found)
   ├─ checks the caller OWNS it     (else returns denied)
   ├─ performs the write            (credentials live here)
   └─ returns a small structured result { status, message }  — on EVERY path
```

Why this is better: the agent can't skip the ownership check, can't invent a `status`, can't run an action you didn't allow, and never touches the credentials — because none of that is exposed to it. The AI decides *what the customer wants*; the sub-workflow decides *what is allowed*. Every path returns `{status, message}` — `ok`, `denied`, `not_found`, or `invalid` — so the agent always knows what happened.

**Files:** [`20_cancel_appointment_subworkflow.json`](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/20_cancel_appointment_subworkflow.json) (the callee) and [`21_agent_cancels_via_tool.json`](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/21_agent_cancels_via_tool.json) (the caller).

> **Import via URL** (both, one at a time):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/20_cancel_appointment_subworkflow.json
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/21_agent_cancels_via_tool.json
> ```
>
> **Download:** {download}`20_cancel_appointment_subworkflow.json <_static/workflows/20_cancel_appointment_subworkflow.json>` · {download}`21_agent_cancels_via_tool.json <_static/workflows/21_agent_cancels_via_tool.json>`

```{important}
**Setup:** create a Data Table named `appointments` with **String** columns `id`, `date`, `time`, `service`, `client_name`, `customer_id`, `status`. Add a test row (e.g. `id=1`, `customer_id=alice`, `status=booked`). Import the sub-workflow first and save it, then import the caller and, in the tool node, select the sub-workflow.
```

::::{dropdown} 🛠️ Build the sub-workflow from scratch
:color: secondary

### Step 1: New workflow + trigger
**Add Workflow** → name it `cancel_appointment`. Add an **Execute Sub-workflow Trigger** (the *When called* node). Set the input mode to *Using fields below* and define three inputs: `customer_id`, `appointment_id`, `action` (all String). *These are the tool's contract — the only things a caller can pass.*

### Step 2: Validate required fields (IF)
Add an **IF** node → `Required fields present?`: `{{ $json.customer_id }}` **is not empty** AND `{{ $json.appointment_id }}` **is not empty**. The **false** branch → an **Edit Fields** node `Return: invalid (missing)` → `{ status: "invalid", message: "customer_id and appointment_id are both required." }`.

### Step 3: Allow-list the action (IF)
On the **true** branch add an **IF** → `Action allowed?`: `{{ $json.action }}` **equals** `cancel`. The **false** branch → `Return: invalid (action)` → `{ status: "invalid", message: "Unsupported action. Only 'cancel' is accepted." }`. *An allow-list means an unknown action is refused by default.*

### Step 4: Look it up — and handle "not found"
Add a **Data Table** node → `Find appointment`, **Get Row(s)**, table `appointments`, filter `id` **equals** `{{ $('When called').item.json.appointment_id }}`. In its **Settings**, turn **Always Output Data ON** so the workflow keeps going even when no row matches. Then an **IF** → `Appointment found?`: `{{ $json.id }}` **is not empty**. **False** → `Return: not_found` → `{ status: "not_found", message: "No appointment was found with that id." }`.

### Step 5: The ownership check (IF)
On the **found** branch add an **IF** → `Caller owns it?`: `{{ $json.customer_id }}` (from the fetched row) **equals** `{{ $('When called').item.json.customer_id }}` (from the trusted input). **False** → `Return: denied` → `{ status: "denied", … }`. *A caller can only touch their own appointment.*

### Step 6: Do the write + return
On the **owned** branch add a **Data Table** → `Apply change (cancel)`, **Update Row(s)**, filter by `id`, set `status` = `cancelled`. Then `Return: done` → `{ status: "ok", message: "Appointment … was cancelled." }`.
::::

### Node-by-Node — the sub-workflow

| Node | Type | What it does |
|------|------|-------------|
| **When called** | Execute Sub-workflow Trigger | Receives the explicit inputs `customer_id`, `appointment_id`, `action` |
| **Required fields present?** | IF | Rejects the call (`invalid`) if a required field is missing |
| **Action allowed?** | IF | Allow-list — only `cancel` proceeds; anything else is `invalid` |
| **Find appointment** | Data Table (Get, *Always Output Data*) | Looks up the row by `id`; still emits an item when nothing matches |
| **Appointment found?** | IF | If no row, returns `not_found` |
| **Caller owns it?** | IF | **Ownership check** — the row's `customer_id` must match the caller's, else `denied` |
| **Apply change (cancel)** | Data Table (Update) | Performs the write — only if allowed |
| **Return: done / denied / not_found / invalid** | Edit Fields | Every path returns a structured `{ status, message }` |

```{important}
**The identity is not the model's to choose.** In the tool's input mapping, `appointment_id` comes from `$fromAI(...)` (the ambiguous part) and `action` is fixed to `cancel`, but **`customer_id` is supplied by the caller from a trusted identity source** — *not* `$fromAI`. That single decision is what stops one customer cancelling another's booking. The ownership check in the sub-workflow is only meaningful when this `customer_id` is trustworthy.
```

---

## Move 5 — human approval (and what it is *not*)

For a high-impact action you often want a person in the loop. n8n gives you **two** distinct shapes — don't confuse them:

| Shape | When | How |
|---|---|---|
| **Approve generated content** | The AI *drafts* something (an email, a reply) and a human okays it before it's sent | A **Wait** node in a normal workflow ([Human in the Loop](04d_human_in_the_loop)) |
| **Approve an agent's tool call** | The agent *wants to run a risky tool* (cancel, refund, delete) and a human okays that specific call | **Native human review** on the tool (n8n **2.6+**) — the agent pauses and sends an Approve/Deny request (Slack/Telegram/Gmail/Chat) before the tool runs |

```{important}
**The caller here is "approval-ready", not already gated.** It has no review channel wired yet. To require human review on the `cancel_appointment` tool (n8n **2.6+**):

1. Open the **AI Agent's tool connector**.
2. Open the **Tools Panel**.
3. Add **Human Review**.
4. Select a **review channel** (Slack / Telegram / Gmail / n8n Chat).
5. **Connect the gated tool** to it.

Now when the agent decides to cancel, the workflow **pauses** and a person sees exactly which tool and which arguments — and clicks Approve or Deny. (Exact labels vary by version — if your screen differs, check the current docs; the *shape* is what matters.)
```

```{warning}
**Approval confirms intent — it is not security.** A human clicking "Approve" does **not** replace authentication, authorisation, validation, or your hard business rules. Those must run in the sub-workflow **regardless** of the click. Approval is a *last* gate for high-impact actions, layered on top of the code-level checks — never instead of them. (That's why the ownership check runs even after approval.)
```

---

## Test It / What to Observe

### 1. Cancel your own appointment
Open the chat (the caller workflow). Ask to cancel appointment `1` (owned by `alice`, with the demo `customer_id` set to `alice`). The assistant confirms, then — once you've wired a review channel — **pauses** for your OK. Approve → the sub-workflow runs its checks, updates the row, and returns `status: ok`.

### 2. Try to cancel someone else's
Change the demo `customer_id` (the tool's `customer_id` mapping) to `bob` and ask to cancel appointment `1`. **Expected:** the sub-workflow returns `status: denied` — the model never got to touch the row. *That's the ownership check doing its job.*

### 3. Cancel one that doesn't exist
Ask to cancel appointment `999`. **Expected:** `status: not_found` — thanks to *Always Output Data* on the lookup, the workflow reaches the `not_found` branch instead of silently stopping.

```{important}
**This is an educational workflow.** The look-up-then-write here is **not** safe against two people cancelling at the same instant (a race condition). Making writes truly safe — idempotency, atomic operations — is the job of [Production Reliability](appendix_b2_production_reliability).
```

---

## Try It Yourself

### Exercise: add a second safe action
Extend the sub-workflow to also **reschedule** (not just cancel). Add `new_date` and `new_time` inputs and add `reschedule` to the **allow-list**; when `action = 'reschedule'`, update those columns instead of `status`. Keep the **validation**, **exists**, and **ownership** checks exactly as they are — they should protect *every* action.

**Done when:** a customer can reschedule *their own* appointment, a reschedule of someone else's still returns `denied`, an unknown action still returns `invalid`, and the agent still calls just **one** tool.

::::{dropdown} 🛠️ Solution sketch
:color: secondary

- Add `new_date`, `new_time` to the **Execute Sub-workflow Trigger** inputs.
- In **Action allowed?**, accept `cancel` **or** `reschedule` (an IF with an OR, or a **Switch** on `action`).
- After **Caller owns it?** (owned branch), branch on `{{ $('When called').item.json.action }}`: `cancel` → the update you already have; `reschedule` → a **Data Table Update** that sets `date` = `{{ $('When called').item.json.new_date }}` and `time` = `{{ $('When called').item.json.new_time }}`.
- Both paths end at a `Return: done`.

The validation, exists, and ownership checks sit **before** the branch, so they guard cancel *and* reschedule with no duplication — one gate, every action. That's the payoff of putting rules in the workflow instead of the prompt.
::::

---

## Summary

| Concept | What you learned |
|---------|------------------|
| **Deterministic HTTP first** | Get the request working yourself — verbs, headers, body, auth, pagination, timeouts, status codes — before an agent wraps it |
| **Credentials in n8n** | Secrets are stored encrypted and injected at run time; the model never sees them |
| **Safe `$fromAI()`** | The model fills ambiguous values only — never credentials, URLs, identity, permission fields, whole bodies, or hard rules |
| **Sub-workflow** | Explicit inputs, validation and credentials kept *inside*, a structured result on every path |
| **One safe tool** | Expose one high-level `cancel_appointment` instead of several raw operations |
| **Ownership check** | Verify the caller owns the record *before* acting — only meaningful with a trusted identity |
| **Native tool approval** | Pause for a human on high-impact calls (n8n 2.6+) — on top of, not instead of, code checks |

**Key ideas:**
- *The AI handles ambiguity; the workflow controls the deterministic rules.*
- Identity comes from a **trusted identity source**, never from `$fromAI()`.
- Approval confirms **intent** — it is not authentication, authorisation, or validation.

**Docs:**
- [HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [HTTP Request credentials](https://docs.n8n.io/integrations/builtin/credentials/httprequest/)
- [Pagination](https://docs.n8n.io/code/cookbook/http-node/pagination/)
- [Sub-workflows](https://docs.n8n.io/flow-logic/subworkflows/)
- [Execute Sub-workflow](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executeworkflow/)
- [Call n8n Workflow Tool](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolworkflow/)
- [Human-in-the-loop for AI tool calls](https://docs.n8n.io/advanced-ai/human-in-the-loop-tools/)
