# Appendix D: Prompt Engineering Basics

This appendix covers practical techniques to write better prompts for your AI workflows. Good prompts lead to more consistent, accurate, and useful responses.

> **Tip:** You don't need to use all these techniques at once. Start simple, and add techniques when you need more control.

**What you'll learn:**
- 6 core prompt engineering techniques
- A hands-on workflow to see the difference
- Ready-to-use templates for common use cases

> **Note:** This appendix covers prompts for Basic LLM Chains and simple AI workflows. For agent-specific techniques (ReAct loops, tool descriptions), see **Appendix E: Prompt Engineering for Agents**.

## Part 1: The Techniques

Here are the core techniques you'll use most often when building AI workflows.

### 1. Role and Context

Tell the AI **who it is** and **what situation** it's in. This shapes the entire response.

**Without role:**
```
Answer the user's question.
```
*Problem: The AI has no idea what kind of answer you want.*

**With role:**
```
You are a customer support agent for an e-commerce store.
You help with orders, returns, and product questions.
Be friendly but concise.
```
*Result: The AI knows its job, scope, and tone.*

**When to use:** Always. Every prompt benefits from context.

### 2. Structured Output

When you need to use the AI's response in later nodes, ask for a **specific format**.

**For routing (single category):**
```
Classify this message into ONE category:
- BILLING
- TECHNICAL  
- GENERAL

Respond with ONLY the category name. No explanations.
```

**For data extraction (JSON):**
```
Extract information from the text.
Return JSON with these exact keys:
- name (string)
- email (string or null)
- issue (string)
```

**When to use:** Whenever the output feeds into another node (routing, conditions, data processing).

### 3. Few-Shot Examples

Show the AI **examples** of what you want. This is one of the most powerful techniques.

```
Summarize support tickets in a standard format.

Example 1:
Input: "I can't log in. I've tried resetting my password."
Output: "[LOGIN] Unable to access account. Password reset attempted."

Example 2:
Input: "When will my order arrive?"
Output: "[SHIPPING] Delivery status inquiry."

Now summarize:
Input: {{ $json.ticket }}
Output:
```

**Why it works:**
- Shows exact format you want
- The AI learns patterns from examples
- More reliable than lengthy explanations

**When to use:** When you need consistent formatting, or when the task is hard to explain but easy to show.

### 4. Chain-of-Thought

For complex decisions, ask the AI to **think step by step** before answering.

```
Determine if this refund should be approved.

Rules:
- Approve if purchased within 30 days AND unused
- Approve if item is defective (any timeframe)
- Deny otherwise

Think through each rule step by step, 
then give your final decision.
```

**Example output:**
```
1. Purchase date: 15 days ago (within 30 days) ✓
2. Item condition: unopened (unused) ✓
3. Defect: not mentioned

Decision: APPROVED (meets 30-day unused rule)
```

**When to use:** Multi-step logic, complex rules, decisions that need explanation.

### 5. Clear Boundaries

Tell the AI what it should **NOT** do. Essential for agents with tools.

```
You are a math tutor.

Rules:
- ALWAYS use the Calculator tool for arithmetic
- NEVER calculate in your head
- If asked about non-math topics, politely redirect
- Keep explanations under 3 sentences
```

**When to use:** 
- Agents with tools (ensure tools are used)
- Sensitive topics (limit scope)
- Production systems (prevent unexpected behavior)

### 6. Edge Case Handling

Tell the AI what to do when input is **unexpected** or **unclear**.

```
Classify customer intent.

Categories: PURCHASE, SUPPORT, FEEDBACK

Edge cases:
- If unclear, choose most likely + add [LOW CONFIDENCE]
- If empty or gibberish, return: UNKNOWN [INVALID]
- If multiple intents, classify the primary one
```

**When to use:** Production workflows. Your workflow won't break on unexpected input.

### Quick Reference

| Technique | When to Use | Key Phrase |
|-----------|-------------|------------|
| **Role & Context** | Always | "You are a..." |
| **Structured Output** | Output feeds other nodes | "Respond with ONLY..." |
| **Few-Shot Examples** | Need consistent format | "Example 1: Input... Output..." |
| **Chain-of-Thought** | Complex logic | "Think step by step..." |
| **Boundaries** | Agents, tools, limits | "NEVER...", "ALWAYS..." |
| **Edge Cases** | Production systems | "If unclear, then..." |

```{note}
For more techniques, see [Anthropic's Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview).
```

---

## Part 2: See It In Action

Let's see how these techniques improve a real prompt, step by step.

**The task:** Classify customer support messages into categories (BILLING, TECHNICAL, FEEDBACK, GENERAL).

We'll build 4 versions of the prompt, each one better than the last.

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/08_prompt_engineering_comparison.json
> ```
> 
> **Download:** {download}`08_prompt_engineering_comparison.json <_static/workflows/08_prompt_engineering_comparison.json>`

### Version 1: Basic Prompt

**Prompt:**
```text
Classify this customer message:

{{ $json.message }}
```

**Problem:** The AI doesn't know:
- What categories to use
- How to format the response
- How detailed to be

**Typical output:** Long explanations like *"This message appears to be related to billing because the customer mentions being charged..."*

This is useless for a workflow that needs to route based on the category.

### Version 2: + Role & Structure

**Prompt:**
```text
You are a customer support classifier for an e-commerce company.

Categorize messages into exactly ONE category:
- BILLING (payments, charges, refunds, invoices)
- TECHNICAL (login issues, bugs, how-to questions)
- FEEDBACK (compliments, complaints, suggestions)
- GENERAL (everything else)

Respond with ONLY the category name. No explanations.
```

**Improvements:**
- Clear role and context
- Defined categories with examples
- Explicit output format

**Typical output:** `BILLING`

Much better! But it might still struggle with ambiguous messages.

### Version 3: + Few-Shot Examples

**Prompt:**
```text
You are a customer support classifier for an e-commerce company.

Categorize messages into exactly ONE category:
- BILLING (payments, charges, refunds, invoices)
- TECHNICAL (login issues, bugs, how-to questions)
- FEEDBACK (compliments, complaints, suggestions)
- GENERAL (everything else)

Examples:

Message: "I was charged $50 but my order was only $30"
Category: BILLING

Message: "The app crashes when I try to checkout"
Category: TECHNICAL

Message: "I love your new website design!"
Category: FEEDBACK

Message: "What are your store hours?"
Category: GENERAL

Message: "I need a refund and the website won't load"
Category: BILLING

Respond with ONLY the category name.
```

**Improvements:**
- Examples show exactly what we want
- Last example shows how to handle messages with multiple issues (prioritize BILLING)

**Typical output:** Consistent and handles edge cases better.

### Version 4: + Edge Cases (Production Ready)

**Prompt:**
```text
You are a customer support classifier for an e-commerce company.

Categorize messages into exactly ONE category:
- BILLING (payments, charges, refunds, invoices)
- TECHNICAL (login issues, bugs, how-to questions)
- FEEDBACK (compliments, complaints, suggestions)
- GENERAL (everything else)

Examples:

Message: "I was charged $50 but my order was only $30"
Category: BILLING

Message: "The app crashes when I try to checkout"
Category: TECHNICAL

Message: "I love your new website design!"
Category: FEEDBACK

Message: "What are your store hours?"
Category: GENERAL

Message: "I need a refund and the website won't load"
Category: BILLING

Edge cases:
- If multiple issues, classify by PRIMARY concern (usually first)
- If empty, gibberish, or unrelated: GENERAL [INVALID]
- If uncertain between categories: pick most likely + [LOW CONFIDENCE]

Respond with ONLY the category name (and optional flag).
```

**Improvements:**
- Handles unexpected input gracefully
- Flags uncertain cases for human review
- Won't break your workflow with unexpected output

**Typical output:** `BILLING` or `GENERAL [INVALID]` or `TECHNICAL [LOW CONFIDENCE]`

### Test Messages to Try

Import the workflow and try these messages. Compare how each version handles them:

| Message | Expected | Tests |
|---------|----------|-------|
| "I was charged twice for my order" | BILLING | Clear case |
| "How do I reset my password?" | TECHNICAL | Clear case |
| "Your product is amazing!" | FEEDBACK | Clear case |
| "I need a refund but the site won't load" | BILLING | Multiple issues |
| "asdfghjkl" | GENERAL [INVALID] | Gibberish |
| "Maybe billing? Or technical?" | Any + [LOW CONFIDENCE] | Ambiguous |

---

## Tips for n8n Workflows

1. **Test with pinned data** — Freeze sample inputs and test your prompts before going live

2. **System vs User Message** — Put stable instructions in System Message, dynamic data in User Message

3. **Watch token costs** — Longer prompts (especially with many examples) cost more. Start simple, add complexity only when needed

4. **Version your prompts** — When something works, save it. Small changes can have big effects

5. **Test edge cases** — Try empty input, very long input, multiple languages, and gibberish
