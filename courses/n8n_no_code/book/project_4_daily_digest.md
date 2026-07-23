# Project 4: Daily Digest

Every project so far waited for **you** — you opened a chat, uploaded a photo, submitted a form. This one is different: it **runs on its own**, on a schedule, with no human in the loop.

Every morning a **Schedule Trigger** wakes the workflow, it pulls the day's top tech stories, an agent reads them (and can dig into one), writes a short **briefing**, and saves it. You wake up to a digest you never asked for — the "agent that works while you sleep."

And there's a reason this sits right before **Deploy to Production**: a chat you can test on your laptop, but a *scheduled* agent only fires when n8n is actually **running 24/7**. This is the project that turns deployment from "nice to have" into a real need.

| What you'll learn | Where it comes from |
|---|---|
| **Schedule Trigger** — run a workflow on a timer, no human | New node (a new kind of trigger) |
| **Proactive agents** — the agent starts the work, not you | New concept |
| **HTTP Request** — pull live data from a free public API | Builds on the HTTP tool (Project 1) |
| **Agent + a tool over fetched data** — summarize, dig deeper on demand | Builds on First AI Agent |
| **Data Tables** — save each run's output | Builds on Project 3 |

**Workflow in this chapter:**

| File | What it does | GitHub Link |
|------|-------------|-------------|
| `18_daily_digest.json` | Schedule → fetch top stories → agent writes a briefing → save it | [View](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/18_daily_digest.json) |

**Requirements:** an **OpenRouter API key** and **n8n 1.113+** (Data Tables). No other credentials — Hacker News' API is free and needs no key.

---

## Why a Proactive (Scheduled) Agent?

So far every agent has been **reactive**: it sits idle until you talk to it. That's most of what people build — but it's only half the picture.

A **proactive** agent flips it around: *it* starts the work, on a schedule, and hands you the result. You don't ask "what's new today?" — the briefing is already waiting. Think monitoring, daily reports, reminders, "watch this and tell me if it changes." A huge share of real-world automation is this shape, and none of it involves a chat window.

The piece that makes it possible is a new kind of trigger — the **Schedule Trigger** — which fires the workflow on a timer (every morning, every hour, every Monday) instead of waiting for a message.

```{important}
**A scheduled workflow only runs when n8n is running.** On your laptop, it fires only while n8n is open — and it must be **published/active**, not a draft. To have it truly run every morning, n8n has to live on a server that's always on. That's exactly what the next project, **Deploy to Production**, is for. Building a proactive agent is what makes deployment finally *matter*.
```

For testing, you don't wait for the clock: you click **Execute workflow** to run it on demand and see the same result.

---

## The Workflow

```
Every morning ──▶ Get Top Stories ──▶ Briefing Writer ──▶ Save Briefing
(Schedule       (HTTP: Hacker News)   (Agent)              (Data Table)
 Trigger)                                  ┊ sub-nodes
                                   ┌───────┴────────┐
                              Chat Model       Story Details
                                             (HTTP tool, on demand)
```

- **Every morning (Schedule Trigger)** — fires the workflow daily at 08:00 (no human needed).
- **Get Top Stories (HTTP Request)** — calls the free Hacker News search API and gets today's front-page stories as JSON.
- **Briefing Writer (AI Agent)** — reads the list, picks the notable ones, and writes a short briefing. It can call **Story Details** to look deeper into a single story.
- **Story Details (HTTP Request tool)** — fetches one story's discussion by its `objectID`; the agent decides when to use it.
- **Save Briefing (Data Table)** — appends today's briefing (with a timestamp) to the `briefings` table.

**File:** [`18_daily_digest.json`](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/18_daily_digest.json)

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/18_daily_digest.json
> ```
>
> **Download:** {download}`18_daily_digest.json <_static/workflows/18_daily_digest.json>`

```{important}
**Setup:** create a Data Table named `briefings` with two **String** columns: `date` and `briefing`. The Save Briefing node points to it by name, so there's nothing else to select. *Shortcut:* in the create dialog choose **Import CSV** and upload {download}`briefings_template.csv <_static/data/briefings_template.csv>` to create the columns at once.
```

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow
Click **Workflows → Add Workflow**, rename it "Daily Digest".

### Step 2: Add the Schedule Trigger
1. Add **Schedule Trigger** → rename to `Every morning`.
2. Set the rule: **Trigger Interval** = `Days`, **Trigger at Hour** = `8`. (Fires daily at 08:00.)

### Step 3: Add the HTTP Request (get the stories)
1. Add **HTTP Request** → rename to `Get Top Stories`.
2. **Method**: `GET`. **URL**:
   ```
   https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=10
   ```
   This returns `{ hits: [ { title, url, points, num_comments, objectID } ] }`.

### Step 4: Add the AI Agent
1. Add **AI Agent** → rename to `Briefing Writer`.
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression):
     ```
     Here are today's top Hacker News stories (JSON):
     {{ JSON.stringify($json.hits) }}
     ```
   - **System Message** (in Options): paste the prompt from the "System Prompt" section below.

### Step 5: Add the Chat Model
1. **+ Chat Model** → **OpenRouter Chat Model**, your credential, model `openai/gpt-4o-mini`.

### Step 6: Add the "Story Details" tool
1. On the agent, **+ Tool → HTTP Request** → rename `Story Details`.
2. **URL** (Expression):
   ```
   {{ 'https://hn.algolia.com/api/v1/items/' + $fromAI('story_id', 'The objectID of the story to look into', 'string') }}
   ```
3. Turn on **Optimize Response** (trims the big JSON). **Description**:
   ```
   Fetches the full details and top comments of ONE Hacker News story by its objectID. Use it once, on the most interesting story, to add depth.
   ```

### Step 7: Create the Data Table + Save node
1. **Overview → Data Tables → Create Data Table** named `briefings`, with columns `date` and `briefing` (both **String**).
2. Add a **Data Table** node → rename `Save Briefing`. Select `briefings`. **Operation**: `Insert Row`. Map:

| Column | Value (Expression) |
|--------|--------------------|
| `date` | `{{ $now.format('yyyy-MM-dd HH:mm') }}` |
| `briefing` | `{{ $json.output }}` |

### Step 8: Connect
```
Every morning → Get Top Stories → Briefing Writer → Save Briefing
(Chat Model and Story Details connect to the agent as sub-nodes)
```

::::

### Node-by-Node Walkthrough

| Node | Type | What it does |
|------|------|-------------|
| **Every morning** | Schedule Trigger | Fires the workflow daily at 08:00 — no human |
| **Get Top Stories** | HTTP Request | Pulls today's front-page stories from Hacker News (JSON) |
| **Briefing Writer** | AI Agent | Reads the stories, writes the briefing, may open one for depth |
| **Save Briefing** | Data Table (Insert) | Appends the briefing + timestamp to `briefings` |

**Sub-nodes of the agent:**

| Sub-node | Type | Purpose |
|----------|------|---------|
| **OpenRouter Chat Model** | Chat Model | The agent's brain |
| **Story Details** | HTTP Request tool | Fetches one story's discussion on demand (agent decides) |

### Data Flow

```
08:00 → Every morning fires
    ↓
Get Top Stories → { hits: [ {title:"...", url:"...", points:412, objectID:"39..."}, ... ] }
    ↓
Briefing Writer (input: the JSON list):
  - picks the 3-4 notable stories
  - (optional) calls Story Details(objectID="39...") to read the discussion of the top one
  → { output: "☕ Morning briefing\n- ... — why it matters ...\nToday's theme: ..." }
    ↓
Save Briefing → inserts { date: "2026-03-15 08:00", briefing: "☕ Morning briefing ..." } into `briefings`
```

::::{dropdown} 🔍 Key insight
:color: info

- **No one asked.** The Schedule Trigger starts everything — the agent works before you're awake. That's the whole point of a proactive agent.
- **The heavy list stays out of the model's context on the second turn.** If the agent opens a story with *Story Details*, only that one story's data comes back — not the whole feed again.
- **Same building blocks, new trigger.** It's still an agent with a tool that saves to a Data Table — only the *trigger* changed. That's the lesson: swap the trigger, get a completely different kind of app.

::::

---

## The System Prompt

The agent gets a JSON list of stories and turns it into a skimmable briefing. The system message defines the format and — importantly — tells it to use the deeper-dive tool *sparingly*.

### Briefing Writer — System Message

```
You write a short, friendly "morning briefing" from a list of today's top Hacker News stories. The list arrives as JSON — each story has: title, url, points, num_comments, objectID.

What to do:
1. Pick the 3-4 most notable stories — prefer AI, startups and software engineering; skip low-signal ones.
2. For each, write ONE line: a plain-English title, then a short "why it matters".
3. You MAY use the Story Details tool ONCE, on the single most interesting story (pass its objectID), to skim its discussion and add a sharper insight. Use it sparingly — never more than once.
4. End with a one-line "Today's theme:" summarising the mood.

Style: concise and skimmable, like a good newsletter. Short bullets, plain text. No preamble such as "Here is your briefing" — output the briefing directly.
```

### Why it works

| Element | Why it matters |
|---------|---------------|
| **"the list arrives as JSON"** | Tells the agent to expect the structured feed (it does — via the prompt expression) |
| **"pick the 3-4 most notable"** | Turns a raw feed into an editor's selection, not a dump |
| **"one line: title + why it matters"** | A tight, consistent format the reader can scan in seconds |
| **"use Story Details ONCE… sparingly"** | Keeps the agent from calling the tool ten times and bloating context/cost |
| **"output the briefing directly"** | No "Here is your briefing" preamble — clean output to save |

The prompt (the user message) is just the data: `{{ JSON.stringify($json.hits) }}` — the stories from the HTTP node, handed to the agent as text.

---

## Test Scenarios

You don't have to wait until 08:00 — run it on demand.

### 1. Run it now
Click **Execute workflow** (top of the canvas). The Schedule Trigger fires immediately for testing.
**Expected:** a briefing appears at the end, and a new row lands in the `briefings` Data Table.

### 2. Watch the agent think
Open **Briefing Writer → Logs**. You'll see:
- the list of stories it received,
- (sometimes) a call to **Story Details** with one `objectID` — the agent chose to dig into that story,
- the final briefing it wrote.

**What to notice:** on a slow-news day it may skip the tool entirely; on a big-story day it opens one. That *decision* is the agent doing its job.

### 3. Check the table
Open **Data Tables → `briefings`**. Each run adds a row with a timestamp and the briefing text — your history builds up over days.

### 4. Make it real (optional)
**Publish** the workflow (top-right). Now it will fire every morning at 08:00 — *if n8n is running*. On your laptop that means "while n8n is open"; to have it truly run daily, deploy it (Project 5).

> **Non-deterministic:** the stories change every run, and which one the agent opens varies. That's expected — re-run it and the briefing changes with the news.

---

## What to Observe + Key Takeaways

**1. Nobody pressed a button.** The Schedule Trigger starts the whole thing. This is the mental shift: an agent doesn't have to wait for you — it can run on its own and hand you the result.

**2. Swap the trigger, get a new app.** The insides are familiar — an agent with a tool that writes to a Data Table. Only the **trigger** changed (Schedule instead of Chat). That one swap turns a chatbot into an autonomous worker.

**3. The agent still decides.** It chooses which stories matter and whether to open one for depth. A dumb "summarize everything" script couldn't; the agent edits.

**4. A schedule needs a live server.** Drafts and closed laptops don't fire. This is the honest reason the next project is **Deploy to Production** — a proactive agent is the first thing you *must* deploy to actually use.

**5. Data Tables give it a memory across days.** Each morning appends a row. Over a week you've got a searchable archive of briefings — with zero credentials.

---

## Try It Yourself

### Challenge 1: Your topic, your source
Swap Hacker News for a feed you care about. Either change the HTTP URL (many sites expose JSON/RSS), or add an **RSS Read** node pointing at a blog's feed, and update the agent's prompt to match. 

**Done when:** the briefing covers your topic, not tech news.

### Challenge 2: Deliver it, don't just store it
Instead of only saving to the table, send the briefing somewhere. Easiest with no Google account: a **Telegram** bot (free bot token) or the **Send Email (SMTP)** node.

**Done when:** you receive the briefing in your chosen channel after a run.

### Challenge 3: A weekly wrap-up
Add a second workflow: a **Schedule Trigger** (weekly) that reads the `briefings` table for the last 7 days and asks the agent to write a "week in review" from them.

**Done when:** a Monday run produces one summary of the week's briefings.

### Challenge 4: Only alert me when it matters
Add a rule: after writing the briefing, the agent also returns `important: true/false` (was there a genuinely big story?). Use an **IF** so it only delivers on important days — a true monitor, not a daily nag.

**Done when:** a quiet day is skipped and a big-news day is delivered.

### Challenge 5: Two schedules
Give it a morning run and an evening run with different prompts ("what's new" vs "wrap up the day"). One workflow, two Schedule Triggers.

**Done when:** you get a different flavour of briefing morning and evening.

## Summary

| Concept | What You Learned |
|---------|------------------|
| **Schedule Trigger** | Run a workflow on a timer — the agent starts itself, no human |
| **Proactive agents** | The "it works while you sleep" pattern: pull, process, deliver |
| **HTTP Request** | Pull live data from a free public API (no key) into your workflow |
| **Agent + on-demand tool** | Summarize a feed, and let the agent dig deeper only when it's worth it |
| **Data Tables** | Append each run's output to build a persistent archive |
| **Deploy matters now** | A schedule only fires on a live server — the bridge to Project 5 |

**Key ideas:**
- `{{ JSON.stringify($json.hits) }}` — hand the fetched list to the agent as its prompt
- `$fromAI('story_id', …)` inside the tool URL — the agent supplies which story to open
- **Trigger Interval: Days / Trigger at Hour: 8** — the daily schedule
- A scheduled workflow must be **published** and running to fire on its own

**Docs:**
- [Schedule Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/)
- [HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [Data Tables](https://docs.n8n.io/data-tables/)
- [Hacker News Search API](https://hn.algolia.com/api)
