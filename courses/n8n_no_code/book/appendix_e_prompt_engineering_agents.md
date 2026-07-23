# Appendix E: Prompt Engineering for Agents

AI Agents work differently than Basic LLM Chains. Instead of one prompt → one response, agents **loop**: they think, act, observe, and repeat until done. This changes how you write prompts.

This appendix covers:
- How the agent loop works (and why it matters)
- Writing tool descriptions that actually get used
- A system prompt template you can copy

Read Appendix D first—the basics still apply here.

---

## How Agents Think: The ReAct Loop

When you use the AI Agent node, here's what happens behind the scenes:

```
┌─────────────────────────────────────────┐
│  USER: "What's the population of the   │
│         capital of France?"            │
├─────────────────────────────────────────┤
│  THINK:  I need the capital first.     │
│  ACT:    Wikipedia("capital of France")│
│  OBSERVE: Paris                        │
├─────────────────────────────────────────┤
│  THINK:  Now I need Paris population.  │
│  ACT:    Wikipedia("Paris population") │
│  OBSERVE: 2.1 million                  │
├─────────────────────────────────────────┤
│  THINK:  I have the answer.            │
│  FINAL:  The population is 2.1 million │
└─────────────────────────────────────────┘
```

**Why this matters for n8n:**
- The agent decides when to use tools and when to stop
- If your prompt is unclear, the agent might loop endlessly or skip tools entirely
- Good system prompts guide the agent through this loop efficiently

---

## Tool Descriptions

In n8n, each tool has a description field. This isn't just documentation—it's how the agent decides whether to use the tool.

**Bad description:**
```
Wikipedia search
```
*Problem: The agent doesn't know WHEN to use it.*

**Good description:**
```
Search Wikipedia for factual information about people, places, 
historical events, or scientific concepts. Use when you need 
verified encyclopedic knowledge. Returns article summaries.
```

**The key rule:** Tell the agent **when** to use the tool, not just what it does.

| Tool | Bad | Good |
|------|-----|------|
| Calculator | "Does math" | "Use for ANY arithmetic. Never calculate manually." |
| HTTP Request | "Makes API calls" | "Fetch data from external APIs when you need real-time information." |

---

## System Prompt Template

Copy this and adapt it for your agent:

```
You are [ROLE]. Your goal is [GOAL].

Tools available:
- Calculator: Use for ANY arithmetic. Never calculate manually.
- Wikipedia: Use for factual questions about people, places, events.

Think before acting. Use tools when you need external information, and stop when the task is complete. Never invent facts. Keep answers under 5 sentences. If you're unsure, say so.
```

**What makes this work:**
- Role and goal are explicit, like in Appendix D
- Tool guidance tells the agent WHEN to use each one
- "Stop when complete" prevents the agent from looping when it shouldn't
- Constraints are specific, not vague ("under 5 sentences" vs "be concise")

---

## Common Mistakes

| Mistake | What happens | Fix |
|---------|--------------|-----|
| "Be helpful" | Agent doesn't know its scope | "Answer questions about [TOPIC]" |
| No tool guidance | Agent ignores tools or guesses | "Use Calculator for ANY math" |
| No stop condition | Agent doesn't stop | "Stop when you have a final answer" |
| Too many rules | Agent gets confused | Keep to 5-7 instructions max |
| "Think step by step" alone | Agent rambles | Combine with "then give your final answer" |
