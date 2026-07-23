# The Reflection Pattern

This chapter reveals a key insight: **AI agents are just automated loops**.

We'll implement the same task two ways — showing how the agent automates what you can build manually.

---

## What is Reflection?

The **Reflection pattern** is a loop where the AI:
1. **Generates** an output
2. **Critiques** its own output
3. **Refines** based on the critique
4. **Repeats** until satisfied

```
┌─────────────────────────────────────────────────────────────────────┐
│                        REFLECTION LOOP                              │
│                                                                     │
│    ┌──────────┐      ┌──────────┐      ┌──────────┐                │
│    │ GENERATE │─────▶│ CRITIQUE │─────▶│  REFINE  │                │
│    │          │      │          │      │          │                │
│    │  Draft   │      │  Check   │      │   Fix    │                │
│    │  output  │      │  issues  │      │  issues  │                │
│    └──────────┘      └────┬─────┘      └────┬─────┘                │
│                           │                 │                       │
│                           │ Issues?         │                       │
│                           │                 │                       │
│                      No ──┴── Yes ──────────┘                       │
│                           │                 ▲                       │
│                           ▼                 │                       │
│                    ┌──────────┐             │                       │
│                    │  OUTPUT  │      (repeat if needed)            │
│                    └──────────┘                                     │
└─────────────────────────────────────────────────────────────────────┘
```

This pattern is validated by research — the [**Self-Refine paper**](https://arxiv.org/abs/2303.17651) (Madaan et al., 2023) shows it improves task performance by ~20% on average.

**How is this different from Prompt Chaining?** Prompt chaining is predefined steps that always run the same way. Reflection is *adaptive iteration based on feedback* — the loop continues until the output meets criteria.

**Key insight:** This is exactly what AI agents do internally. The agent node just automates this loop for you.

---

## The Challenge: Constrained Product Description

To demonstrate reflection, we need a task that LLMs typically fail on the first try. Writing with **multiple hard constraints** is perfect:

| Constraint | Requirement |
|------------|-------------|
| **Sentences** | Exactly 3 |
| **Words** | 25–30 total |
| **Keyword** | Contains "sound" exactly twice |
| **Forbidden** | Does NOT contain "music" or "audio" |

**Product:** Wireless Bluetooth Headphones

Try asking ChatGPT to do this in one shot — it almost always fails at least one constraint. This is why reflection matters.

---

## Two Approaches, One Pattern

We'll implement the same reflection loop two ways:

| Version | Who controls the loop? | Best for |
|---------|------------------------|----------|
| **V1: Loop with Exit** | You design the loop | When you need full control |
| **V2: AI Agent** | AI decides when to stop | When you want simplicity |

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/05_reflection_pattern.json
> ```
>
> **Download:** {download}`05_reflection_pattern.json <_static/workflows/05_reflection_pattern.json>`

Both versions are in the same workflow. Each has its own trigger — run them separately and compare!

---

## Version 1: Loop with Exit Condition

You design a workflow that **loops until the constraints pass** (or hits a maximum of 5 iterations).

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                    LOOP                                              │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐      │
│  │ Generate/     │──▶│   Validate    │──▶│ Parse Result  │──▶│  If Done?     │──┬──▶│ Output
│  │ Refine (LLM)  │   │    (LLM)      │   │    (Set)      │   │(pass OR max)  │  │   │
│  └───────────────┘   └───────────────┘   └───────────────┘   └───────────────┘  │   │
│         ▲                                                            │ No       │   │
│         │                                                            ▼          │   │
│         │                                                    ┌───────────────┐  │   │
│         └────────────────────────────────────────────────────│ Prepare Refine│  │   │
│                              (loop back)                     └───────────────┘  │   │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

**Pros:** Full control, predictable behavior, easy to debug
**Cons:** More complex to build

::::{dropdown} 🛠️ Build V1 (Loop) from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

1. Click **Workflows** → **Add Workflow**
2. Rename it to "Reflection Pattern — V1 Loop"

### Step 2: Add the trigger and input

1. Add **Manual Trigger** → rename to `Run: V1 Loop`
2. Add **Edit Fields** → rename to `Input — Product (V1)`
3. Add four fields:

| Name | Type | Value |
|------|------|-------|
| `product` | String | `Wireless Bluetooth Headphones` |
| `constraints` | String | `- Exactly 3 sentences`<br>`- 25–30 words total`<br>`- Contains the word "sound" exactly twice`<br>`- Does NOT contain the words "music" or "audio"` |
| `iteration` | Number | `0` |
| `draft` | String | (leave empty) |

### Step 3: Add Generate/Refine (Basic LLM Chain)

1. Add **Basic LLM Chain** → rename to `Generate/Refine (V1)`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression mode):
     ```
     Product: {{ $('Input — Product (V1)').first().json.product }}

     Constraints:
     {{ $json.constraints }}

     {{ $json.draft ? 'Previous draft:\n' + $json.draft + '\n\nImprove the draft to fix the issues.' : 'Write the product description:' }}
     ```
3. Add System Message:
   ```
   You are a product copywriter.

   Write a product description that meets ALL the constraints exactly.
   Count words carefully. Output ONLY the description.
   ```
4. Add your Chat Model (OpenRouter, OpenAI, etc.)

### Step 4: Add Store Draft (Edit Fields)

1. Add **Edit Fields** → rename to `Store Draft (V1)`
2. Add three fields:

| Name | Type | Value (Expression) |
|------|------|---------------------|
| `draft` | String | `{{ $json.text }}` |
| `constraints` | String | `{{ $('Input — Product (V1)').first().json.constraints }}` |
| `iteration` | Number | `{{ $if($('Parse Validation (V1)').isExecuted, $('Parse Validation (V1)').first().json.iteration, 0) + 1 }}` |

**Why `$if(...isExecuted, ...)`?** The LLM chain only outputs `{ text }` — it doesn't pass through `iteration`. So Store Draft must read it from Parse Validation (a later node in the loop). On the **first** iteration Parse Validation hasn't run yet, so we use n8n's `$if($('node').isExecuted, value, default)` to return `0` when it hasn't executed, or the previous iteration's value when it has.

### Step 5: Add Validate (Basic LLM Chain)

1. Add **Basic LLM Chain** → rename to `Validate (V1)`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression):
     ```
     Draft:
     {{ $json.draft }}

     Constraints:
     {{ $json.constraints }}

     Validation report:
     ```
3. Add System Message:
   ```
   You are a strict validator.

   Check the draft against EACH constraint:
   1. Count sentences (must be exactly 3)
   2. Count words (must be 25–30)
   3. Count occurrences of "sound" (must be exactly 2)
   4. Check for forbidden words "music" or "audio" (must have 0)

   Return a JSON object:
   {
     "sentences": <number>,
     "words": <number>,
     "sound_count": <number>,
     "has_forbidden": <true/false>,
     "all_pass": <true/false>,
     "issues": ["list of issues if any"]
   }

   Return ONLY the JSON.
   ```
4. Connect the same Chat Model

### Step 6: Add Parse Validation (Edit Fields)

1. Add **Edit Fields** → rename to `Parse Validation (V1)`
2. Add six fields:

| Name | Type | Value (Expression) |
|------|------|---------------------|
| `draft` | String | `{{ $('Store Draft (V1)').first().json.draft }}` |
| `constraints` | String | `{{ $('Store Draft (V1)').first().json.constraints }}` |
| `iteration` | Number | `{{ $('Store Draft (V1)').first().json.iteration }}` |
| `validation_json` | String | `{{ $json.text }}` |
| `all_pass` | Boolean | `{{ /"all_pass"\s*:\s*true/.test($json.text) }}` |
| `done` | Boolean | `{{ /"all_pass"\s*:\s*true/.test($json.text) \|\| $('Store Draft (V1)').first().json.iteration >= 5 }}` |

The `done` field combines both exit conditions: constraints passed **or** max iterations reached. This avoids needing a second If node.

### Step 7: Add If Done? (If node)

1. Add **If** → rename to `If Done?`
2. Configure the condition:
   - **Value 1**: `{{ $json.done }}` (Expression)
   - **Operation**: `equals`
   - **Value 2**: `true` (Boolean)

### Step 8: Add Output (V1) — True branch

1. From the **True** output of If Done?, add **Edit Fields** → rename to `Output (V1)`
2. Add three fields:

| Name | Type | Value (Expression) |
|------|------|---------------------|
| `final_description` | String | `{{ $json.draft }}` |
| `iterations` | Number | `{{ $json.iteration }}` |
| `approach` | String | `{{ $json.all_pass ? 'V1: Loop with Exit Condition' : 'V1: Loop (max iterations reached)' }}` |

3. Enable **Keep Only Set**

### Step 9: Add Prepare Refine (Edit Fields) — loop back

1. From the **False** output of If Done?, add **Edit Fields** → rename to `Prepare Refine (V1)`
2. Add three fields:

| Name | Type | Value (Expression) |
|------|------|---------------------|
| `draft` | String | `{{ $json.draft }}` |
| `constraints` | String | `{{ $json.constraints }}` |
| `iteration` | Number | `{{ $json.iteration }}` |

3. **Connect the output of Prepare Refine back to Generate/Refine (V1)** — this creates the loop!

### Step 10: Test

1. Click **Execute Workflow**
2. Watch the loop iterate until constraints pass (or max 5)
3. Check how many iterations it took

::::

### Meet the Node: If (Conditional)

The **If** node checks a condition and sends data to one of two outputs.

| Property | Description |
|----------|-------------|
| **Purpose** | Route data based on a condition |
| **Outputs** | True branch (top) and False branch (bottom) |
| **Common use** | Exit loops, handle errors, route by value |

In V1, we use one If node that combines both checks:
- **If Done?** — checks if `done` is true, where `done = all_pass OR iteration >= 5`
  - **True branch:** constraints passed or max iterations reached → Output
  - **False branch:** keep refining → loop back

### Parsing the Validation Result

The Validate LLM returns JSON like `{"all_pass": true, ...}`. We need to extract the `all_pass` value for the If node.

Instead of complex JSON parsing, we use a **regex test** in an expression:

```
{{ /"all_pass"\s*:\s*true/.test($json.text) }}
```

This returns `true` if the LLM said all constraints passed, `false` otherwise.

**Regex breakdown:**
| Part | Matches |
|------|---------|
| `"all_pass"` | The literal field name with quotes |
| `\s*` | Zero or more whitespace characters |
| `:` | The colon separator |
| `\s*` | Zero or more whitespace characters |
| `true` | The literal value `true` |

**Why this works:**
- The LLM is instructed to output ONLY JSON
- We just need to know if `all_pass` is `true` — no need to parse the full object
- The `\s*` parts handle any whitespace around the colon (e.g., `"all_pass": true`, `"all_pass":true`)

### How the Loop Works

The key to looping in n8n: **connect the output of a node back to an earlier node**.

```
Generate/Refine ◄──────────────────────────────────┐
     │                                             │
     ▼                                             │
  Validate                                         │
     │                                             │
     ▼                                             │
  Parse Result (Set)                               │
     │  (computes: done = all_pass OR iter >= 5)   │
     ▼                                             │
  If Done? ───Yes──▶ Output                        │
     │                                             │
     No                                            │
     │                                             │
     ▼                                             │
  Prepare Refine ──────────────────────────────────┘
```

**How is the max-iteration guardrail built?** Instead of a separate If node, the `done` field in Parse Result combines both conditions: `all_pass OR iteration >= 5`. A single If node routes to Output when done, or loops back to keep refining. The Output node uses a conditional expression to report whether constraints passed or the max was hit.

### Node-by-Node Walkthrough (V1)

| Node | Type | What it does |
|------|------|-------------|
| **Run: V1 Loop** | Manual Trigger | Starts Version 1 |
| **Input — Product (V1)** | Set | Creates `product`, `constraints`, `iteration=0`, `draft=""` |
| **Generate/Refine (V1)** | Basic LLM Chain | Generates or refines based on whether `draft` is empty |
| **Store Draft (V1)** | Set | Saves draft and increments iteration |
| **Validate (V1)** | Basic LLM Chain | Checks constraints, returns JSON |
| **Parse Validation (V1)** | Set | Extracts `all_pass` boolean using regex test, computes `done` |
| **If Done?** | If | Routes to Output if `done` (pass or max), else loops back |
| **Prepare Refine (V1)** | Set | Formats data for next iteration |
| **Output (V1)** | Set | Returns `final_description`, `iterations`, `approach` |

---

## Version 2: AI Agent

The simplest to build: let the agent handle the loop.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              AI AGENT                                        │
│                                                                              │
│    ┌─────────────────────────────────────────────────────────────────┐      │
│    │                    INTERNAL LOOP                                │      │
│    │                                                                 │      │
│    │   ┌──────────┐      ┌──────────────┐      ┌──────────┐         │      │
│    │   │  THINK   │─────▶│ Call Tool:   │─────▶│  CHECK   │         │      │
│    │   │          │      │  Validator   │      │          │         │      │
│    │   │ "Draft   │      │ (JavaScript) │      │ "all_pass │──No────┤      │
│    │   │  a desc" │      │              │      │  true?"  │         │      │
│    │   └──────────┘      └──────────────┘      └────┬─────┘         │      │
│    │         ▲                                      │               │      │
│    │         │                                      │ Yes           │      │
│    │         └──────────────────────────────────────┘               │      │
│    │                                                                 │      │
│    └─────────────────────────────────────────────────────────────────┘      │
│                                                                              │
│    ┌─────────────┐                                                          │
│    │  Validator  │ ◄── JavaScript tool that checks constraints              │
│    │    Tool     │                                                          │
│    └─────────────┘                                                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Pros:** Simplest to build, agent adapts strategy
**Cons:** Less predictable, may take more iterations

::::{dropdown} 🛠️ Build V2 (Agent) from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

1. Click **Workflows** → **Add Workflow**
2. Rename it to "Reflection Pattern — V2 Agent"

### Step 2: Add the trigger and input

1. Add **Manual Trigger** → rename to `Run: V2 Agent`
2. Add **Edit Fields** → rename to `Input — Product (V2)`
3. Add two fields:

| Name | Type | Value |
|------|------|-------|
| `product` | String | `Wireless Bluetooth Headphones` |
| `constraints` | String | `- Exactly 3 sentences`<br>`- 25–30 words total`<br>`- Contains the word "sound" exactly twice`<br>`- Does NOT contain the words "music" or "audio"` |

### Step 3: Add the AI Agent

1. Add **AI Agent** → rename to `Reflection Agent (V2)`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression mode):
     ```
     Product: {{ $json.product }}

     Constraints:
     {{ $json.constraints }}

     Write a product description that meets ALL constraints. After writing, use the Validator tool to check it. Keep refining until all constraints pass.
     ```
3. Click **Options** → Add **System Message**:
   ```
   You are a product copywriter who writes precise descriptions.

   Process:
   1. Write a draft description
   2. Use the Validator tool to check it (send ONLY the description text)
   3. Read the issues list in the Validator response to see what failed
   4. Revise the draft to fix those specific issues
   5. Validate again — repeat until all_pass is true
   6. Return ONLY the final description

   Rules:
   - Do NOT count words yourself — rely on the Validator tool
   - Send ONLY the description to the Validator (no extra text like "Here is my draft:")
   - Call the Validator at most 5 times
   - When all_pass is true, return ONLY the final description
   ```

### Step 4: Add the Chat Model (sub-node)

1. Click **+ Chat Model** at the bottom of the Agent node
2. Select **OpenRouter Chat Model** (or OpenAI, Google, etc.)
3. Choose your credential
4. Model: `openai/gpt-4o-mini` (or similar)

### Step 5: Add the Validator Tool (Code Tool)

1. Click **+ Tool** at the bottom of the Agent node
2. Select **Code Tool**
3. Configure:
   - **Name**: `Validator`
   - **Description**: `Validates a product description against constraints. Input: the description text only (no extra text). Returns JSON with: sentences (count), words (count), sound_count, has_forbidden, all_pass (true/false), and issues (list of specific problems to fix).`
   - **Language**: `JavaScript`
   - **JavaScript Code**:
     ```javascript
     // Get the raw input from the agent
     const item = $input.first().json;

     // Try common field names (varies by n8n version)
     let description = '';
     for (const key of ['query', 'input', 'chatInput', 'action_input']) {
       if (item[key]) {
         description = String(item[key]).trim();
         break;
       }
     }

     // Fallback: use the first non-empty string value
     if (!description) {
       for (const [k, v] of Object.entries(item)) {
         if (typeof v === 'string' && v.trim()) {
           description = v.trim();
           break;
         }
       }
     }

     // Count sentences (split by . ! ?)
     const sentences = description.split(/[.!?]+/).filter(s => s.trim());
     const sentenceCount = sentences.length;

     // Count words
     const words = description.split(/\s+/).filter(w => w);
     const wordCount = words.length;

     // Count "sound" occurrences (case insensitive, whole word)
     const soundMatches = description.toLowerCase().match(/\bsound\b/g) || [];
     const soundCount = soundMatches.length;

     // Check for forbidden words
     const hasForbidden = /\b(music|audio)\b/i.test(description);

     // Build issues list
     const issues = [];
     if (sentenceCount !== 3) issues.push(`Sentences: ${sentenceCount} (need exactly 3)`);
     if (wordCount < 25 || wordCount > 30) issues.push(`Words: ${wordCount} (need 25-30)`);
     if (soundCount !== 2) issues.push(`"sound" count: ${soundCount} (need exactly 2)`);
     if (hasForbidden) issues.push('Contains forbidden word: "music" or "audio"');

     const allPass = issues.length === 0;

     return [{
       json: {
         input_received: description.slice(0, 200),
         sentences: sentenceCount,
         words: wordCount,
         sound_count: soundCount,
         has_forbidden: hasForbidden,
         all_pass: allPass,
         issues: allPass ? ['All constraints passed!'] : issues
       }
     }];
     ```

### Step 6: Add Output (Edit Fields)

1. Add **Edit Fields** → rename to `Output (V2)`
2. Add two fields:

| Name | Type | Value (Expression) |
|------|------|---------------------|
| `final_description` | String | `{{ $json.output }}` |
| `approach` | String | `V2: AI Agent with Validator Tool` |

3. Enable **Keep Only Set**

### Step 7: Test

1. Click **Execute Workflow**
2. Click the **Agent node** to see its internal tool calls
3. Watch how it writes, validates, and refines automatically

::::

### The Validator Tool

Instead of using an LLM to validate, V2 uses a **JavaScript Code tool** — a function the agent can call:

```javascript
// Get the raw input from the agent
const item = $input.first().json;

// Try common field names (varies by n8n version)
let description = '';
for (const key of ['query', 'input', 'chatInput', 'action_input']) {
  if (item[key]) {
    description = String(item[key]).trim();
    break;
  }
}

// Count sentences, words, keyword occurrences...
const sentences = description.split(/[.!?]+/).filter(s => s.trim());
const words = description.split(/\s+/).filter(w => w);
const soundCount = (description.toLowerCase().match(/\bsound\b/g) || []).length;
const hasForbidden = /\b(music|audio)\b/i.test(description);

const issues = [];
if (sentences.length !== 3) issues.push(`Sentences: ${sentences.length} (need exactly 3)`);
// ... more constraint checks ...

return [{
  json: {
    input_received: description.slice(0, 200),  // debug: see what was received
    all_pass: issues.length === 0,
    issues
  }
}];
```

(Full code with all four constraint checks is in Step 5 above.)

**Why a JavaScript tool instead of an LLM?**
- **Faster:** No API call needed
- **Cheaper:** No tokens used
- **Accurate:** Code counts exactly right (LLMs often miscount)

**Key concept:** The agent doesn't "know" how to count — it *delegates* all validation to the tool. The LLM orchestrates; the code validates.

**Debugging tip:** The `input_received` field shows exactly what text the Validator received. If the agent sends extra text like "Here is my draft:", the word count will be wrong. Check this field in the Agent node's tool call logs.

### Node-by-Node Walkthrough (V2)

| Node | Type | What it does |
|------|------|-------------|
| **Run: V2 Agent** | Manual Trigger | Starts Version 2 |
| **Input — Product (V2)** | Set | Creates `product` and `constraints` |
| **Reflection Agent (V2)** | AI Agent | Writes, validates, refines in a loop |
| **Validator Tool** | Code Tool | JavaScript function that checks constraints |
| **Output (V2)** | Set | Returns `final_description` and `approach` |

**Sub-nodes connected to the Agent:**
- **OpenRouter (V2)** — the LLM brain
- **Validator Tool** — the constraint checker

### Prompt Used (V2)

**System Message:**
```
You are a product copywriter who writes precise descriptions.

Process:
1. Write a draft description
2. Use the Validator tool to check it (send ONLY the description text)
3. Read the issues list in the Validator response to see what failed
4. Revise the draft to fix those specific issues
5. Validate again — repeat until all_pass is true
6. Return ONLY the final description

Rules:
- Do NOT count words yourself — rely on the Validator tool
- Send ONLY the description to the Validator (no extra text like "Here is my draft:")
- Call the Validator at most 5 times
- When all_pass is true, return ONLY the final description
```

Notice: the system message describes the reflection loop explicitly — including how to use the Validator's feedback. The agent follows the same pattern we built manually in V1!

---

## The Insight: Agents Are Automated Loops

Compare what each version automates:

| Version | You design... | n8n handles... | AI handles... |
|---------|---------------|----------------|---------------|
| **V1: Loop** | The loop structure, exit condition | Looping, iteration count | Text generation |
| **V2: Agent** | The goal and tools | Everything | The entire loop |

The agent node automates the same Generate → Critique → Refine loop you built by hand in V1.

```{note}
**Terminology: Evaluator-Optimizer.** Some sources call this the **Evaluator-Optimizer** pattern — a separate evaluator judges the output while an optimizer refines it. V1 uses a dedicated Validate LLM, V2 uses a JavaScript Code tool. Pure "reflection" where the *same* LLM critiques its own output is a special case of this broader pattern.
```

---

## When to Use Reflection

Reflection adds latency and cost. Use it strategically:

| Use Reflection when... | Skip Reflection when... |
|------------------------|-------------------------|
| Constraints are strict and measurable | Task is simple or one-shot |
| First-pass accuracy is typically low | Real-time / low-latency required |
| Output quality matters more than speed | Constraints are fuzzy or subjective |
| You can define a clear validator | No clear "done" criteria exists |

### V1 vs V2: Which Approach?

| Situation | Best approach |
|-----------|---------------|
| You need full control over each step | V1: Loop |
| You want to debug exactly what's happening | V1: Loop |
| Task is ambiguous, you want AI to adapt | V2: Agent |
| You want the simplest implementation | V2: Agent |

**General rule:** Start with V2 (agent). If you need more control or debugging, build V1.

---

## Try It Yourself

1. **Run both versions** on the same product
2. **Compare:** How many iterations did each take? Which produced the best output?
3. **Change the constraints:** Make them harder (e.g., exactly 27 words) and run again
4. **Observe the agent:** In V2, click the agent node to see its internal tool calls

**Challenge:** Modify V1 to allow up to 10 iterations. Does it ever need that many?

---

## Key Takeaways

1. **Reflection = Generate → Critique → Refine → Repeat**
2. **You can build the loop manually** (V1) or **let the agent handle it** (V2)
3. **Agents are not magic** — they automate the same loop you can build by hand
4. **Always include guardrails** (max iterations) to prevent infinite loops
5. **Code tools are useful** when you need precise validation (LLMs miscount)

**Next:** In the **First AI Agent** chapter, we'll explore more agent capabilities — memory, multiple tools, and conversation.
