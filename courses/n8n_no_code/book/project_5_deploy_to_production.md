# Project 5: Deploy to Production

Your workflows work locally. This project takes a simple AI chat workflow and deploys it to a server so it runs 24/7 — anyone with the link can chat with your AI.

**What you'll do:**
1. Build a minimal chat workflow (Chat Trigger → LLM → Output)
2. Deploy it to Railway (~$5/month)
3. Share the chat link with anyone

**What you'll learn:**
- How to deploy n8n to a cloud server
- How to publish workflows for production
- How to configure `WEBHOOK_URL` so the chat works publicly

---

## The Workflow

The simplest useful production workflow: a chat interface powered by an LLM. Users type a question, the LLM answers, and the response appears in the chat.

```
┌───────────────────────┐     ┌────────────────┐     ┌────────┐
│ When chat message      │────▶│ Answer         │────▶│ Output │
│ received (Chat Trigger)│     │ Question (LLM) │     │        │
└───────────────────────┘     └────────────────┘     └────────┘
                                     ┊
                               OpenRouter Chat Model
```

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/13_deploy_to_production.json
> ```
>
> **Download:** {download}`13_deploy_to_production.json <_static/workflows/13_deploy_to_production.json>`

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

Create a new workflow and name it **Deploy to Production**.

### Step 2: Add a Chat Trigger

Add a **When chat message received** node and configure it:

| Parameter | Value |
|-----------|-------|
| **Public** | ON |
| **Response Mode** | When Last Node Finishes |

### Step 3: Add a Basic LLM Chain

Add a **Basic LLM Chain** node:

| Parameter | Value |
|-----------|-------|
| **Prompt Type** | Define below |
| **Text** | `{{ $json.chatInput }}` |

System message:
```
You are a helpful assistant. Answer the user's question in 2-3 sentences. Be concise and accurate.
```

### Step 4: Add the Chat Model

Add an **OpenRouter Chat Model** (or your preferred provider) and connect it to the LLM Chain.

| Parameter | Value |
|-----------|-------|
| **Model** | `openai/gpt-4o-mini` |

### Step 5: Add Output node

Add an **Edit Fields (Set)** node and configure it:

| Name | Type | Value |
|------|------|-------|
| `output` | String | `{{ $json.text }}` |

The Chat Trigger expects the last node to have a field called `output`. The LLM Chain outputs `text`, so this node renames it.

### Step 6: Connect everything

**When chat message received** → **Answer Question** → **Output**

::::

---

## Test Locally First

Before deploying, make sure the workflow works on your machine.

1. Open the workflow in the editor
2. Click the **Chat** button in the bottom-right corner
3. Type a question:

```
What is n8n?
```

You should see the LLM's response in the chat window. If this works, you're ready to deploy.

```{note}
The Chat Trigger creates two URLs: a **test URL** (works only in the editor) and a **production URL** (works only when the workflow is published on a server). Locally, you test using the Chat button.
```

---

## Option A: Deploy on Railway

[Railway](https://railway.com/) is a cloud platform that deploys n8n in one click. It costs **~$5/month minimum** (Hobby plan — includes $5 of usage credits). No server management needed. See [Railway pricing](https://railway.com/pricing) for current details.

### Step 1: Create a Railway account

Go to [railway.com](https://railway.com/) and sign up (GitHub login works). At the time of writing, new accounts get a one-time **$5 trial credit** — enough to run n8n for roughly a month before paying anything.

### Step 2: Deploy n8n from template

1. Go to [railway.com/deploy/n8n](https://railway.com/deploy/n8n)
2. Click **Deploy Now**
3. Railway creates a project with n8n + a PostgreSQL database automatically
4. Wait 2–3 minutes for the deployment to finish

### Step 3: Open your n8n instance

Once deployed, Railway gives you a public URL like `your-app.up.railway.app`. Click it to open your n8n instance. Create your admin account on first login.

### Step 4: Set the Webhook URL

This is the most important production setting. Without it, n8n generates URLs pointing to `localhost` and the chat won't be accessible from outside.

1. In Railway, click on your n8n service
2. Go to **Variables**
3. Add (or verify) this environment variable:

| Variable | Value |
|----------|-------|
| `WEBHOOK_URL` | `https://your-app.up.railway.app/` |

Replace `your-app.up.railway.app` with your actual Railway URL. **Include the trailing slash.**

Railway will redeploy automatically after adding the variable.

### Step 5: Import and configure the workflow

1. In your Railway n8n instance, go to **Workflows** → **Import from URL**
2. Paste the import URL:
   ```
   https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/13_deploy_to_production.json
   ```
3. Configure the **OpenRouter Chat Model** node with your API credential

### Step 6: Publish the workflow

Click **Publish** in the top-right corner of the editor. This is essential — the Chat Trigger only serves its production URL when the workflow is published (a draft only runs when you click *Execute*).

### Step 7: Open the chat in your browser

Once published, click on the **When chat message received** node and copy the **Production URL**. Open it in any browser — you should see a chat interface. Type a question and get an answer from the LLM.

**Share this link with anyone** — they can chat with your AI without installing anything.

### Step 8: Check Execution History

In your Railway n8n instance, go to **Left sidebar → Executions**. You should see each chat message listed as a successful execution.

---

## Option B: n8n Cloud

[n8n Cloud](https://n8n.io/cloud/) is n8n's official hosted service. It's the easiest option — no deployment, no configuration.

| | Details |
|---|---|
| **Price** | From ~€20/month (Starter plan, [see pricing](https://n8n.io/pricing/)) |
| **Includes** | Execution limits vary by plan |
| **Setup** | Sign up → start building |
| **Webhook URL** | Configured automatically |

### How to use it

1. Sign up at [n8n.io/cloud](https://n8n.io/cloud/)
2. Import the workflow using the same URL
3. Configure your API credential
4. Publish the workflow
5. Click the **When chat message received** node and copy the **Production URL** — open it in your browser

The advantage of n8n Cloud: no `WEBHOOK_URL` to configure, no server to maintain, automatic updates. The disadvantage: it's the most expensive option, and execution limits may matter for high-traffic workflows.

---

## Option C: VPS + Docker (Advanced)

If you're comfortable with Linux and the terminal, you can run n8n on any VPS (Virtual Private Server) using Docker Compose. Providers like Hetzner ($4/mo), DigitalOcean ($6/mo), or Oracle Cloud (free tier) work well.

This involves:
- Setting up a server with Docker
- Running n8n with `docker compose up -d`
- Configuring a reverse proxy (Caddy or Nginx) for HTTPS
- Setting `WEBHOOK_URL` to your domain

It's the cheapest long-term option and gives you full control, but requires server administration knowledge that is outside the scope of this course.

n8n provides a complete guide: [n8n Docker Compose setup](https://docs.n8n.io/hosting/installation/docker/).

---

## What to Watch Out For

| Topic | What to know |
|-------|-------------|
| **Chat URL** | The Chat Trigger generates a public URL when the workflow is active. Copy it from the node — don't guess the path. |
| **WEBHOOK_URL** | Must be set on Railway/VPS so n8n generates the correct public URLs. n8n Cloud sets it automatically. |
| **Publish the workflow** | The workflow must be published. Without it, the Chat Trigger doesn't expose its production URL. |
| **Credentials** | API keys are stored per n8n instance. After deploying, you need to re-enter them on the server. |
| **Execution History** | Your primary debugging tool in production. Check it in **Left sidebar → Executions** after the first chat message. |
| **Costs** | Railway: ~$5/mo. n8n Cloud: from ~€20/mo. LLM API calls are billed separately by your provider. |
| **`output` field** | The Chat Trigger expects the last node to have a field called `output`. If you use a Basic LLM Chain (which outputs `text`), add a Set node to rename it. |
| **Public endpoint = open to anyone** | If the chat is public, anyone with the URL can use it — and every message costs you LLM tokens. For a real deployment, consider adding authentication (Webhook node supports Basic Auth or Header Auth) or placing the endpoint behind a proxy with rate limiting. |
| **Want your own UI?** | This deploys n8n's built-in chat. To call the agent from your own Lovable/Replit front end instead, see [Project 6: Connect Your App](project_6_connect_your_app) (webhook + JSON contract). |

---

## Comparison

| | Railway | n8n Cloud | VPS + Docker |
|---|---|---|---|
| **Cost** | ~$5/mo minimum | From ~€20/mo | $4–12/mo |
| **Setup** | 5 min (template) | 2 min (sign up) | 30–60 min |
| **WEBHOOK_URL** | Set manually | Automatic | Set manually |
| **Server management** | No | No | Yes |
| **Execution limits** | None (your server) | Varies by plan | None (your server) |
| **Best for** | This course | Non-technical users | Production at scale |

---

## Summary

You've taken a workflow from your laptop to a public server. The key concepts:

1. **Chat Trigger creates a public URL** — anyone with the link can chat with your AI
2. **Workflows must be published** — click *Publish* in the top-right corner
3. **`WEBHOOK_URL` must be set** — so n8n generates correct public URLs (except on n8n Cloud)
4. **Credentials are per instance** — re-enter API keys after deploying
5. **Execution History is your debugger** — check it after the first production message

Any workflow from this course that uses a Chat Trigger or Webhook can be deployed the same way. Configure your credentials, set `WEBHOOK_URL`, click *Publish*, and you're live.
