# Where n8n Fits

You've now learned the whole toolkit — prompts, the four workflow patterns, reflection, agents with tools and memory, guardrails, RAG, even multi-agent orchestration. Before you put it to work in the Projects, one honest question rounds out the theory: **when is n8n the right tool, and when should you reach for something else?**

The "something else" is usually a **coding agent** — Claude Code, Codex, and their kin: AI agents that live in a developer's environment and write and run their own code. People often feel these are simply "more powerful" than n8n. That's partly true and partly a category error. This chapter gives you a durable way to tell which tool fits which job — and *why* — so you carry a clear mental model into everything you build next.

---

## Three Ways to See the Same Line

The boundary between n8n and a coding agent can be drawn at three depths. Each is correct; the deeper ones explain the shallower ones.

**1. The quick version — predictable vs. open-ended.** n8n shines when the work is a *predictable, repeatable flow*. When the task is genuinely open-ended, with no fixed recipe, it starts to strain.

**2. The sharper version — can you name the systems and the steps?** If you can say in advance *which* services are involved and *what* happens at each step ("new form response → look up the customer → post to Slack"), that's an n8n job. If the task has to **work out its own steps** as it goes, that points to a coding agent.

**3. The real mechanism — is there a verifiable feedback loop?** This is the truest cut. A coding agent is at its strongest when it can **check its own work and self-correct**: write something, run it, read the error, fix it, repeat — against something that tells it the truth (a test that passes, output that's clearly right or wrong). Coding is the gold-standard agent task precisely *because* that loop is built in. Where no such loop exists, the extra power has nothing to push against.

---

## What Makes Coding Agents So Powerful

Think of the difference this way.

An **n8n agent** works from a well-stocked toolbox: a large but fixed set of building blocks — send email, read a sheet, call this API — that you wire together. It's fast, legible, and reliable *for the jobs those blocks cover*.

A **coding agent** doesn't pick from a toolbox. It can **write a brand-new tool on the spot, run it, see what happened, and rewrite it** — in a real working environment with files and a terminal.

```
        n8n                                    Coding agent
   ─────────────                          ───────────────────

   Pick from a fixed toolbox              Write a tool, run it,
   and wire it together:                  see what happened, fix it:

   ┌──────┐┌──────┐┌──────┐                  write ─▶ run ─▶ check
   │ Email││ Sheet││ API  │                    ▲              │
   └──────┘└──────┘└──────┘                    └──── fix ◀─────┘

   Reliable for known jobs                Open-ended; proves its own work
```

Three things make that loop potent:

- **Code is a universal action.** Instead of choosing from a menu, the agent expresses what it wants as code it can run — composing, looping, and even orchestrating many tools at once by writing a few lines instead of calling them one at a time. (Tested across 17 different models, acting through runnable code rather than a fixed menu [raised success rates by up to ~20%](https://arxiv.org/abs/2402.01030).)
- **It verifies by running.** It doesn't *guess* whether the work is right — it runs it. Frontier coding agents can take a real software bug, write a fix, run the project's tests, and keep going until they pass, resolving the large majority of such real-world issues.
- **It works in a real environment.** Files, a terminal, and the ability to handle data far larger than fits in a single prompt. A terminal alone lets it do almost anything a computer can — install a tool, transform a file, run a program — which is why its ceiling sits so much higher than any fixed set of blocks. (Claude for Excel, for example, edits spreadsheets with thousands of rows by *writing code* to do it — rather than trying to read every row into the conversation.)

That combination — write-and-run, verify, real workspace — is the power people sense. It isn't a bigger brain. It's a tighter loop with reality.

---

## When to Use Which

| Reach for n8n when… | Reach for a coding agent when… |
|---|---|
| You can name the systems and the steps in advance | The task has to work out its own steps |
| It must run unattended — on a schedule, a webhook, a form | It's a one-off or exploratory build you supervise |
| It connects known services (email, sheets, CRM, databases) | It needs to write and run its own code over files or data |
| You need it observable, governed, and owned by a non-coder | Success is proven by running something until it's right |
| Predictability matters more than open-ended capability | Open-ended capability matters more than predictability |

### The two classic wrong-tool mistakes

- **Forcing open-endedness into n8n.** A sprawling forty-node canvas trying to handle every variation of messy input, branches stacked on branches. If your workflow looks like that, you haven't found a clever n8n trick — you've outgrown the tool *for that task*.
- **Using a coding agent for what should be a durable integration.** A clever script that quietly does a job no one can see running, schedule reliably, or maintain. That trades ownership and observability for power the task never needed.

---

## They Compose, Not Compete

"Which is more powerful?" misses how the two actually fit together. A coding agent is great at **building**; n8n is great at **running**.

- A coding agent can *build the thing you then run in n8n* — it could scaffold a workflow, or write the kind of ~10-line `fetch()` you'll use in **Project 6** to connect an app. You describe the contract; the AI writes the code. That is a coding agent doing exactly what it's best at.
- n8n, in turn, can call an LLM — or a whole agent — as **one governed step** inside a reliable, scheduled, observable pipeline.

The strongest real systems often use both: the coding agent does the open-ended building, and n8n runs the result, day after day, where people can see it.

---

## What n8n Is Genuinely Best At

It would be easy to read all this as "coding agents win." They don't — not at the job you came here to do. The moment a task needs to run *reliably, connected, and unattended*, n8n's strengths are precisely the ones a raw coding agent lacks:

- **It runs on its own** — triggers, schedules, webhooks, forms. Nobody has to be watching.
- **It speaks to everything** — hundreds of integrations are the connective tissue between your tools.
- **You can see every run** — execution history shows what happened, when, and why it failed.
- **It's governable** — human-in-the-loop approvals and predefined rules keep an agent inside the lines.
- **A non-coder can own it** — build it, read it, fix it, and hand it to a colleague. That is rare, and it is the whole point.

For an enormous class of real, valuable work — the connected, repeatable, must-not-fail kind — n8n isn't a compromise. It's the right tool, and you can now own it end to end.

---

## Try It Yourself: Which Tool?

For each task, decide **n8n or coding agent** before you read the answer. Use the rule: *can you name the systems and the steps?*

| Task | Reach for… | Why |
|------|-----------|-----|
| Every morning, summarize yesterday's payments and post it to Slack | **n8n** | Named systems, fixed steps, must run unattended on a schedule |
| Sort a messy folder of 200 mystery PDFs into a spreadsheet of totals | **Coding agent** | It has to work out its own steps over files — and can verify as it goes |
| When a contact form arrives, classify the message and route it to the right inbox | **n8n** | Known trigger and steps; the AI classification is just one node |
| Prototype a small app, try a few approaches, get the tests passing | **Coding agent** | Open-ended build, proven by running it until the tests pass |
| Weekly: check 5 vendor APIs, flag price changes, email procurement | **n8n** | Scheduled, known systems, repeatable — and must not fail |
| "Build me that vendor-check workflow" | **Both** | The coding agent *builds* it; n8n *runs* it — compose, don't choose |

If a task made you hesitate, that hesitation is the signal: you're near the line, and the deciding question is whether the work has a way to **check itself**.

---

## The Line Keeps Moving

Treat everything here as *today's* practical boundary, not a permanent border. n8n keeps gaining agentic capability — beyond the multi-agent orchestration you built here, it now plugs into outside tools through a shared standard and can grade its own agents with built-in evaluations. Coding agents, meanwhile, are gaining the durability they lacked: one can now pick up a software ticket, write the fix, run the tests, and open a pull request on its own, unattended inside an automated pipeline — the same verify-by-running loop from earlier, now running without anyone watching. The two are growing toward each other.

So don't memorize a fixed rule. Keep the *question* instead:

> **Reach for n8n when you can name the systems and the steps. Reach for a coding agent when the task has to write and run its own code to figure itself out.**

**The takeaway:** the question was never which tool is more powerful. It's which one fits the task in front of you — and you can now answer that, *and* build the n8n side yourself.

Next, the **Projects** put all of this to work end to end — pick whichever one fits what you want to build.

```{note}
**Want to pull a thread?** On why the feedback loop matters: Anthropic's [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents), the source of this course's patterns. On the line moving: [Claude Code in GitHub Actions](https://code.claude.com/docs/en/github-actions) shows a coding agent doing exactly that — turning an issue into a pull request, unattended, inside CI.
```
