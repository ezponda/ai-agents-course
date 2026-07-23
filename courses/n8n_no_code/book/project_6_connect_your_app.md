# Project 6: Connect Your App

In the prototyping class you build front ends in **Lovable** or **Replit**. In this course you've built agents in n8n. This project is the bridge between the two: instead of using n8n's built-in chat box, you'll expose your agent as a **webhook** and call it from your own app.

This is how real products are built — a custom front end talking to a back end over HTTP. Your n8n workflow becomes the "brain"; your Lovable/Replit app becomes the "face".

| What you'll learn | Where it comes from |
|-------------------|--------------------|
| **Webhook Trigger** — receive requests from any app | Builds on Going Live (Appendix B) |
| **Respond to Webhook** — send a custom JSON answer back | New node |
| **The contract** — the exact shape of what's sent and returned | The core idea of this project |
| **Memory by `session_id`** — multi-turn chat from your own UI | Builds on First AI Agent |

```{note}
You will **not** hand-write front-end code. You'll define the *contract* (what your app sends, what n8n returns) and let Lovable or Claude write the ~10 lines of `fetch()` for you. Knowing the contract is the skill; the code is generated.
```

---

## The Workflow

A request comes in from your app. An AI Agent answers (remembering the conversation by `session_id`), n8n logs it, and **Respond to Webhook** sends a clean JSON answer back to your app.

```
   Your app (Lovable / Replit)                        n8n
┌────────────────────────────┐        ┌──────────────────────────────────────────┐
│ fetch(POST /webhook/chat)   │───────▶│  Webhook ──▶ AI Agent ──┬─▶ Respond to    │
│ { message, session_id }     │        │                         │     Webhook     │
│                             │◀───────│                         └─▶ Log Entry      │
│ data.reply                  │        │             (sub-nodes: Chat Model, Memory)│
└────────────────────────────┘        └──────────────────────────────────────────┘
```

**New node:** **Respond to Webhook** — lets you return a custom response (here, JSON with the agent's reply) instead of n8n's default.

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/16_connect_your_app.json
> ```
>
> **Download:** {download}`16_connect_your_app.json <_static/workflows/16_connect_your_app.json>`

**Credentials needed:** OpenRouter API key (Settings → Credentials).

---

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

1. Click **Workflows** → **Add Workflow**
2. Rename it to "Connect Your App"

### Step 2: Add the Webhook trigger

1. Add **Webhook** (search for "Webhook")
2. Configure:

| Parameter | Value |
|-----------|-------|
| **HTTP Method** | `POST` |
| **Path** | `chat` |
| **Respond** | `Using 'Respond to Webhook' Node` |

The Webhook gives you a **Test URL** and a **Production URL** — the same Test/Production split you saw in Appendix B. Your app sends a JSON body; n8n receives it under `{{ $json.body }}`.

### Step 3: Add the AI Agent

1. Add **AI Agent** → rename to `AI Agent`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression): `{{ $json.body.message }}`
   - **System Message** (in Options):
     ```
     You are a helpful assistant embedded in a web app.

     Rules:
     - Answer the user's message clearly and concisely (2-4 sentences unless asked for more).
     - Use the conversation history to handle follow-up questions.
     - If you don't know something, say so — don't invent facts.
     ```
3. Add a **Chat Model** sub-node → **OpenRouter Chat Model** → model `openai/gpt-4o-mini`

### Step 4: Add Memory (keyed by session_id)

1. Click **+ Memory** on the AI Agent → **Simple Memory**
2. Configure:
   - **Session ID Type**: `Custom Key`
   - **Session Key** (Expression): `{{ $json.body.session_id }}`
   - **Context Window Length**: `10`

This is the same memory idea as the chat agents — but the session now comes from *your app*, not n8n's chat box. Send the same `session_id` for a given conversation and the agent remembers it.

### Step 5: Add Respond to Webhook

1. Add **Respond to Webhook**
2. Configure:
   - **Respond With**: `JSON`
   - **Response Body** (Expression):
     ```
     {{ { "reply": $json.output, "session_id": $('Webhook').item.json.body.session_id } }}
     ```

This is the JSON your app receives back.

### Step 6: Add a Log Entry (optional but recommended)

1. Add **Edit Fields** → rename to `Log Entry`
2. Enable **Keep Only Set** and add:

| Name | Value (Expression) |
|------|--------------------|
| `received_at` | `{{ $now.format('yyyy-MM-dd HH:mm') }}` |
| `user_id` | `{{ $('Webhook').item.json.body.user_id }}` |
| `message` | `{{ $('Webhook').item.json.body.message }}` |
| `reply` | `{{ $json.output }}` |
| `status` | `responded` |

This prepares one log row per request. In production you'd connect a **Google Sheets** or database node here (same idea as Project 3's logging challenge).

### Step 7: Connect the nodes

```
Webhook → AI Agent → Respond to Webhook
                   → Log Entry
```

The AI Agent has **two** outgoing connections: one to Respond to Webhook (sends the answer back) and one to Log Entry (records it).

### Step 8: Test from the terminal first

Before wiring a front end, prove the contract works. Click **Listen for Test Event** on the Webhook, then run:

```bash
curl -X POST "http://localhost:5678/webhook-test/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is n8n?", "session_id": "demo-1"}'
```

You should get back `{"reply": "...", "session_id": "demo-1"}`.

::::

## The Contract

This is the heart of the project. A **contract** is the agreement between your app and n8n: what your app sends, and what n8n sends back. Get this right and the two sides can be built independently.

**Your app sends (request body):**

| Field | Required | What it is |
|-------|----------|------------|
| `message` | Yes | The text the person typed |
| `session_id` | Yes | A stable ID for the conversation (so memory works) |
| `user_id` | No | Who the user is (handy for logging/personalization) |

```json
{
  "message": "What are your opening hours?",
  "session_id": "user-42-conversation-7",
  "user_id": "user-42"
}
```

**n8n sends back (response body):**

```json
{
  "reply": "We're open Monday to Friday, 9am to 6pm.",
  "session_id": "user-42-conversation-7"
}
```

**Why `session_id` matters:** memory is keyed on it. Send the *same* `session_id` for every message in one conversation and the agent remembers the thread. Use a *new* one for a new conversation. Your app decides what that ID is (often the logged-in user plus a chat ID).

That's the entire contract. Everything else — buttons, styling, login — lives in your app and never touches n8n.

---

## The Front-End Side (you don't write this by hand)

Your app needs to do three things: send the request, wait for the response, show `reply`. That's about ten lines of JavaScript:

```javascript
const res = await fetch("https://YOUR-N8N-URL/webhook/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: userMessage,      // what the person typed
    session_id: sessionId,     // keep this stable per conversation
    user_id: currentUser.id    // optional
  })
});
const data = await res.json();
console.log(data.reply);       // the agent's answer
```

**You don't memorize or write this.** In Lovable or Replit, paste the contract from above and ask:

> *"When the user sends a chat message, POST it to `https://YOUR-N8N-URL/webhook/chat` as JSON with `message`, `session_id`, and `user_id`. Then show `reply` from the JSON response in the chat window."*

Lovable (or Claude) writes the `fetch()` for you. Your job is to give it the **contract** — the URL and the field names — which you now own because you built the n8n side.

```{tip}
Use the **Production URL** (from the Webhook node, after you **Publish** the workflow) in your deployed app. The **Test URL** only works while the editor is open with "Listen for Test Event" active — fine for the first `curl` test, not for a real app.
```

---

## Node-by-Node Walkthrough

| Node | Type | What it does |
|------|------|-------------|
| **Webhook** | Webhook Trigger | Receives the POST from your app; body is under `{{ $json.body }}` |
| **AI Agent** | AI Agent | Answers `{{ $json.body.message }}`, remembers by `session_id` → `output` |
| **Respond to Webhook** | Respond to Webhook | Returns `{ reply, session_id }` as JSON to your app |
| **Log Entry** | Set | Prepares one log row per request (connect Sheets/DB in production) |

**Sub-nodes (dotted lines to the AI Agent):**

| Sub-node | Type | Purpose |
|----------|------|---------|
| **OpenRouter Chat Model** | Chat Model | The agent's brain |
| **Simple Memory** | Memory | Remembers the conversation, keyed by `{{ $json.body.session_id }}` |

### System Message

```
You are a helpful assistant embedded in a web app.

Rules:
- Answer the user's message clearly and concisely (2-4 sentences unless asked for more).
- Use the conversation history to handle follow-up questions.
- If you don't know something, say so — don't invent facts.
```

Keep it simple here — the focus of this project is the *connection*, not the agent. Once the bridge works, you can swap in any agent from this course (a RAG document assistant, a tool-using research agent, even the multi-agent orchestrator) behind the exact same webhook contract.

---

## Data Flow

```
REQUEST (from your app)
───────────────────────
POST /webhook/chat
{ "message": "What is n8n?", "session_id": "demo-1", "user_id": "u1" }
    ↓
Webhook: { body: { message, session_id, user_id }, headers, ... }
    ↓
AI Agent (reads body.message, loads memory for session_id): { output: "n8n is a workflow automation tool..." }
    ↓                                   ↘
Respond to Webhook                       Log Entry
{ "reply": "n8n is a workflow            { received_at, user_id, message,
   automation tool...",                    reply, status: "responded" }
  "session_id": "demo-1" }
    ↓
RESPONSE (back to your app)
───────────────────────────
{ "reply": "n8n is a workflow automation tool...", "session_id": "demo-1" }
```

**Key point:** the Webhook body arrives under `$json.body`, not `$json` directly — that's why the agent reads `{{ $json.body.message }}` and the memory key is `{{ $json.body.session_id }}`.

---

## What to Watch Out For

A webhook is a **public endpoint** — anyone with the URL can call it, and every call costs you LLM tokens. Before sharing it, apply the hardening from the **Guardrails & Safety** chapter ("Exposing an Agent to Real Users").

| Topic | What to do |
|-------|-----------|
| **Cost cap** | Set **Max Iterations** on the agent (5-10) and keep `contextWindowLength` modest. A public endpoint with no limits is an open invoice. |
| **Authentication** | The Webhook node supports **Header Auth** or **Basic Auth** (Authentication dropdown). Add a shared secret your app sends, so random visitors can't call it. |
| **Don't trust the input** | Treat `message` as untrusted text — the prompt-injection rules from Guardrails apply. Never let the agent act on instructions hidden inside a user message or a retrieved document. |
| **Validate `session_id`** | If a user can set their own `session_id`, they could read another conversation's memory. Derive it server-side (e.g. logged-in user ID) where it matters. |
| **CORS** | If the browser blocks the request, you may need to allow your app's domain. n8n exposes webhook CORS settings; your app's host (Lovable/Replit) usually handles this for you. |

This is the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) in miniature: **LLM01 Prompt Injection** and **LLM10 Unbounded Consumption** are exactly the two risks a public agent endpoint faces first.

```{note}
**Want your own UI instead of n8n's chat box?** That's this project. If you only need a quick public chat without a custom front end, the **Deploy to Production** project (n8n's built-in chat) is simpler.
```

---

## Try It Yourself

1. **Wire it to a real Lovable/Replit app.** Build a tiny chat page, give it the contract, and let the AI write the `fetch()`. Send a few messages with the same `session_id` and confirm memory works.

2. **Challenge — add an intent router.** Drop the **Routing** pattern between the Webhook and the agent: classify the message (e.g. `question` vs `support`) and send each to a different agent or system message. The contract your app sees doesn't change at all.

3. **Challenge — make it a real assistant.** Swap the plain agent for the **RAG document assistant** from the RAG chapter (Vector Store as a tool). Now your app answers from *your* documents — same webhook, same contract.

4. **Challenge — log to Google Sheets.** Replace the Log Entry node with a **Google Sheets** node (like Project 3). You now have a record of every conversation your app has.

5. **Harden it.** Add Header Auth to the Webhook and have your app send the secret. Confirm a request without the secret is rejected.

---

## Summary

| Concept | What You Learned |
|---------|------------------|
| **Webhook Trigger** | Receive requests from any app; the body arrives under `$json.body` |
| **Respond to Webhook** | Return a custom JSON answer your app can read |
| **The contract** | Define what's sent (`message`, `session_id`, `user_id`) and returned (`reply`) — then both sides can be built independently |
| **Memory by `session_id`** | Multi-turn conversations driven by your app, not n8n's chat box |
| **You own the contract, AI writes the code** | The skill is the contract; the `fetch()` is generated by Lovable/Claude |
| **Public endpoint hardening** | Cost cap, auth, untrusted input — the Guardrails chapter applied |

**Key insight:** your n8n agent and your app are two halves of one product, joined by a tiny JSON contract. Once that contract is clear, you can rebuild either side without touching the other — and any agent from this course drops in behind the same webhook.

This is the natural end of the course: you can now build an agent **and** put it behind your own interface.

**Docs:**
- [Webhook node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [Respond to Webhook node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/)
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)
