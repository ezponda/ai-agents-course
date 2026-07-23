# Pattern 1: Prompt Chaining

**What you will build:** You have a beef lasagna recipe. The workflow will simplify it for beginners, adapt it for kids, and generate a shopping list — one step at a time, where each step builds on the previous result.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Manual Trigger │────▶│   Edit Fields   │────▶│  Basic LLM #1   │────▶│  Basic LLM #2   │──...
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

**New node:** None — this pattern uses only nodes you already know (Edit Fields, Basic LLM Chain). The difference is chaining **multiple** LLM calls in sequence.

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/01_prompt_chaining.json
> ```
>
> **Download:** {download}`01_prompt_chaining.json <_static/workflows/01_prompt_chaining.json>`

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: Create a new workflow

1. Click **Workflows** → **Add Workflow**
2. Rename it to "Prompt Chaining Practice"

### Step 2: Add the trigger

1. Click the **+** button on the canvas
2. Search for **Manual Trigger** → click to add
3. This starts your workflow when you click "Execute Workflow"

### Step 3: Add input data (Edit Fields)

1. Click **+** on the right side of Manual Trigger
2. Search for **Edit Fields** (or "Set") → add it
3. Rename the node to `Input — Recipe`
4. Add two String fields:

| Name | Value |
|------|-------|
| `recipe_name` | `Classic Beef Lasagna` |
| `recipe` | `Ingredients:\n- 500g ground beef\n- 1 onion, finely diced\n- 3 cloves garlic, minced\n- 800g canned crushed tomatoes\n- 2 tbsp tomato paste\n- 1 tsp dried oregano\n- 1 tsp dried basil\n- Salt and pepper to taste\n- 250g lasagna sheets\n- 500g ricotta cheese\n- 1 egg\n- 300g shredded mozzarella\n- 50g grated parmesan\n- Fresh basil for garnish\n\nInstructions:\n1. Brown the ground beef in a large skillet over medium-high heat. Drain excess fat.\n2. Sauté the onion and garlic until translucent. Add crushed tomatoes, tomato paste, oregano, basil, salt, and pepper. Simmer for 20 minutes.\n3. Mix ricotta, egg, and half the parmesan in a bowl.\n4. Preheat oven to 375°F (190°C).\n5. Layer in a 9x13 baking dish: sauce, lasagna sheets, ricotta mixture, mozzarella. Repeat 3 times.\n6. Top with remaining sauce and mozzarella.\n7. Cover with foil and bake 25 minutes. Remove foil, bake 15 more minutes until golden.\n8. Let rest 10 minutes before serving. Garnish with fresh basil.` |

### Step 4: Add Step 1 — Simplify Recipe (Basic LLM Chain)

1. Click **+** on the right side of Edit Fields
2. Search for **Basic LLM Chain** → add it
3. Rename to `Step 1 — Simplify Recipe`
4. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt (User Message)** — click the field, switch to Expression mode with `{{ }}`:
     ```
     Recipe: {{ $json.recipe_name }}

     {{ $json.recipe }}

     Simplify this recipe for a beginner cook.
     ```
5. Scroll down to **Chat Messages** → click **Add Message**:
   - Type: `System`
   - Message:
     ```
     You are a cooking instructor for beginners.
     Simplify the recipe into clear, easy-to-follow steps.

     Rules:
     - Use simple language (no cooking jargon)
     - Explain any technique briefly (e.g., "sauté" → "cook in a pan, stirring often")
     - Keep all original ingredients
     - Number every step clearly
     - Output ONLY the simplified recipe
     ```
6. Add the Chat Model:
   - Click **+ Chat Model** at the bottom of the node
   - Select **OpenRouter Chat Model** (or OpenAI, Google, etc.)
   - Choose your credential
   - Model: `openai/gpt-4o-mini` (or `deepseek/deepseek-chat-v3-0324:free`)

### Step 5: Add Store Simplified Recipe (Edit Fields)

1. Click **+** on the right side of Step 1
2. Add **Edit Fields** → rename to `Store Simplified Recipe`
3. Add one String field:
   - Name: `simplified_recipe`
   - Value (Expression mode): `{{ $json.text }}`

### Step 6: Add Step 2 — Adapt for Kids (Basic LLM Chain)

1. Click **+** on the right side of Store Simplified Recipe
2. Add **Basic LLM Chain** → rename to `Step 2 — Adapt for Kids`
3. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression mode):
     ```
     Simplified recipe:
     {{ $json.simplified_recipe }}

     Adapt this for kids.
     ```
4. Add System Message:
   ```
   You are a family cooking expert.
   Adapt the simplified recipe so it is fun and safe for kids aged 5–10 to help make.

   Rules:
   - Suggest milder alternatives for strong flavors (e.g., less garlic, skip pepper)
   - Add fun names for steps (e.g., "Squish the cheese mix!")
   - Flag any step that needs adult help (hot oven, sharp knives)
   - Adjust portions for a family with kids
   - Output ONLY the kid-friendly recipe
   ```
5. Connect the same Chat Model (it should auto-connect, or drag from the existing one)

### Step 7: Add Store Kid-Friendly Recipe (Edit Fields)

1. Click **+** → Add **Edit Fields** → rename to `Store Kid-Friendly Recipe`
2. Add field:
   - Name: `kid_friendly_recipe`
   - Value (Expression): `{{ $json.text }}`

### Step 8: Add Step 3 — Shopping List (Basic LLM Chain)

1. Click **+** → Add **Basic LLM Chain** → rename to `Step 3 — Shopping List`
2. Configure:
   - **Source for Prompt**: `Define below`
   - **Prompt** (Expression):
     ```
     Recipe:
     {{ $json.kid_friendly_recipe }}

     Create a shopping list.
     ```
3. Add System Message:
   ```
   You are a helpful shopping assistant.
   Create a shopping list from the recipe.

   Rules:
   - Group items by store section (Produce, Dairy, Meat, Pantry)
   - Include quantities
   - Skip items most kitchens already have (salt, pepper, olive oil)
   - Add a "Check at home first" section for common pantry items
   - Output ONLY the shopping list
   ```

### Step 9: Add Output — Shopping List (Edit Fields)

1. Click **+** → Add **Edit Fields** → rename to `Output — Shopping List`
2. Add field:
   - Name: `shopping_list`
   - Value (Expression): `{{ $json.text }}`
3. Enable **Keep Only Set** to clean up the output

### Step 10: Test your workflow

1. Click **Execute Workflow**
2. Click each node to see its output
3. Compare the simplified recipe vs. the kid-friendly version vs. the shopping list

**Tip:** After the first successful run, **Pin** the output of Step 1 to avoid API calls while you work on later steps.

::::

### Nodes in This Pattern

This pattern uses nodes you already know from Quick Start:

| Node | What it does |
|------|--------------|
| **Manual Trigger** | Starts the workflow when you click "Execute Workflow" |
| **Edit Fields (Set)** | Creates or transforms data fields |
| **Basic LLM Chain** | Sends a prompt to an AI model and returns the response |

The difference here: we chain **multiple** Basic LLM Chains in sequence, where each uses the previous one's output.

### What Problem This Solves

Breaking a complex task into smaller steps improves quality. Instead of asking an LLM to "simplify this recipe, adapt it for kids, and make a shopping list" in one shot, you ask it to: (1) simplify the recipe, (2) adapt for kids, (3) generate a shopping list. Each step builds on the previous result, and each output is a clearly different format.

### Node-by-Node Walkthrough

<div style="overflow: auto; max-height: 250px; border: 1px solid #ddd; border-radius: 4px; padding: 10px; margin-bottom: 15px; background: #f8f8f8;">
<pre style="margin: 0; white-space: pre;">
┌──────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐     ┌──────────────────────────┐
│   Manual Trigger │────▶│    Input — Recipe      │────▶│  Step 1 — Simplify     │────▶│  Store Simplified Recipe │
└──────────────────┘     └────────────────────────┘     └────────────────────────┘     └──────────────────────────┘
                                                                                                    │
        ┌───────────────────────────────────────────────────────────────────────────────────────────┘
        ▼
┌────────────────────────┐     ┌──────────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│  Step 2 — Adapt Kids   │────▶│  Store Kid-Friendly Recipe   │────▶│  Step 3 — Shopping List │────▶│  Output — Shopping List │
└────────────────────────┘     └──────────────────────────────┘     └────────────────────────┘     └────────────────────────┘
</pre>
</div>

| Node | Type | What it does |
|------|------|-------------|
| **Run: Prompt Chaining** | Manual Trigger | Starts the workflow |
| **Input — Recipe** | Set | Creates fields: `recipe_name`, `recipe` |
| **Step 1 — Simplify Recipe** | Basic LLM Chain | Simplifies the recipe for beginners → outputs `text` |
| **Store Simplified Recipe** | Set | Saves `{{ $json.text }}` as `simplified_recipe` |
| **Step 2 — Adapt for Kids** | Basic LLM Chain | Adapts for kids using `{{ $json.simplified_recipe }}` → outputs `text` |
| **Store Kid-Friendly Recipe** | Set | Saves `{{ $json.text }}` as `kid_friendly_recipe` |
| **Step 3 — Shopping List** | Basic LLM Chain | Generates shopping list using `{{ $json.kid_friendly_recipe }}` → outputs `text` |
| **Output — Shopping List** | Set | Saves `{{ $json.text }}` as `shopping_list` (uses `keepOnlySet` to remove other fields) |

**Sub-node:** One `OpenRouter Chat Model` is shared by all three LLM Chain nodes (connected via dotted lines).

### Prompts Used

Each step uses a different **role** and **rules**. This is why chaining works better than one big prompt.

**Step 1 — Simplify Recipe:**
```
System: You are a cooking instructor for beginners.
Simplify the recipe into clear, easy-to-follow steps.

Rules:
- Use simple language (no cooking jargon)
- Explain any technique briefly (e.g., "sauté" → "cook in a pan, stirring often")
- Keep all original ingredients
- Number every step clearly
- Output ONLY the simplified recipe
```

**Step 2 — Adapt for Kids:**
```
System: You are a family cooking expert.
Adapt the simplified recipe so it is fun and safe for kids aged 5–10 to help make.

Rules:
- Suggest milder alternatives for strong flavors (e.g., less garlic, skip pepper)
- Add fun names for steps (e.g., "Squish the cheese mix!")
- Flag any step that needs adult help (hot oven, sharp knives)
- Adjust portions for a family with kids
- Output ONLY the kid-friendly recipe
```

**Step 3 — Shopping List:**
```
System: You are a helpful shopping assistant.
Create a shopping list from the recipe.

Rules:
- Group items by store section (Produce, Dairy, Meat, Pantry)
- Include quantities
- Skip items most kitchens already have (salt, pepper, olive oil)
- Add a "Check at home first" section for common pantry items
- Output ONLY the shopping list
```

**Why this works:** Each step has a focused role (instructor → family expert → shopping assistant), specific constraints, and ends with "Output ONLY..." to prevent extra commentary. Each step produces a visibly different output format.

### Data Flow

```
INPUT                          OUTPUT
─────                          ──────
Trigger: { }
    ↓
Recipe: { recipe_name, recipe }
    ↓
Step 1 LLM: { text: "1. Cook the beef in a large pan..." }
    ↓
Store Simplified: { simplified_recipe: "1. Cook the beef..." }
    ↓
Step 2 LLM: { text: "🧑‍🍳 Kid-Friendly Lasagna!\n1. Squish the cheese mix!..." }
    ↓
Store Kid-Friendly: { kid_friendly_recipe: "🧑‍🍳 Kid-Friendly Lasagna!..." }
    ↓
Step 3 LLM: { text: "🛒 SHOPPING LIST\n\nMeat:\n- 500g ground beef..." }
    ↓
Final Output: { shopping_list: "🛒 SHOPPING LIST\n\nMeat:..." }
```

### What to Observe

1. Click **Input — Recipe** → see the original recipe
2. Click **Step 1 — Simplify Recipe** → see the beginner-friendly version (same dish, simpler language)
3. Click **Step 2 — Adapt for Kids** → see the kid-friendly version (fun names, safety notes, milder flavors)
4. Click **Step 3 — Shopping List** → see a completely different format (grouped shopping list)

::::{dropdown} 🔍 Why do we need "Store" nodes? See the data transformation
:color: info

When a Basic LLM Chain runs, it **replaces** the previous data with only its output. This diagram shows what happens:

```
 STEP 1: Input                    STEP 2: LLM simplifies recipe      STEP 3: Store saves it
┌─────────────────────┐          ┌─────────────────────┐             ┌─────────────────────┐
│ Input — Recipe      │─────────▶│ Step 1 — Simplify   │────────────▶│ Store Simplified    │
│                     │          │ (Basic LLM Chain)   │             │ Recipe (Edit Fields) │
└─────────────────────┘          └─────────────────────┘             └─────────────────────┘
         │                                │                                   │
         ▼                                ▼                                   ▼
┌─────────────────────┐          ┌─────────────────────┐             ┌─────────────────────┐
│ {                   │          │ {                   │             │ {                   │
│   "recipe_name":    │          │   "text":           │             │   "text":           │
│     "Classic Beef   │          │     "1. Cook the    │             │     "1. Cook the    │
│      Lasagna",      │          │      beef in a      │             │      beef...",      │
│   "recipe":         │          │      large pan..."  │             │   "simplified_      │
│     "Ingredients:   │          │ }                   │             │    recipe":         │
│      ..."           │          │                     │             │     "1. Cook the    │
│ }                   │          │ ⚠️ recipe_name and  │             │      beef..."       │
│                     │          │ recipe are GONE!    │             │ }                   │
│                     │          │                     │             │                     │
│                     │          │                     │             │ 💡 Store adds       │
│                     │          │                     │             │ "simplified_recipe" │
└─────────────────────┘          └─────────────────────┘             └─────────────────────┘
```

**Key insight:** 
- The LLM outputs only `{ "text": "..." }` — original fields are lost
- The Store node adds `simplified_recipe` to save the result with a meaningful name
- Step 2 only needs `{{ $json.simplified_recipe }}` so it works without the original fields
- This workflow is designed so each step only needs the previous step's output

**Why this pattern?** Each LLM step has a focused task. Step 2 doesn't need `recipe_name` or the original `recipe` — it only needs the simplified version to adapt for kids.

::::
