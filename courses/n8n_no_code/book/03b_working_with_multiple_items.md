# Working with Multiple Items

Every workflow you've built so far quietly relied on one idea: data in n8n travels as a **list of items**. Most of the time you didn't have to think about it — one chat message in, one answer out. But the moment you handle *several things at once* — a batch of reviews, a page of tickets, a list of contacts — that list becomes the whole game.

This short chapter makes the item model explicit. It's pure n8n (no AI), because this is **foundational plumbing** that every later workflow sits on top of. Get it once and the rest of the course stops feeling like magic.

| What you'll learn | Where it comes from |
|---|---|
| **One item vs. many items** — and why n8n runs a node once *per item* | Deepens Core Concepts ([Core Concepts](03_core_concepts)) |
| **A list inside one item vs. many items** — the distinction that trips everyone up | New |
| **Split Out** — turn one item's array into many items | New node |
| **Filter** — drop the items you don't want | New node |
| **Aggregate** — collapse many items back into one | New node |
| **Merge** — join two branches | Builds on Parallelization ([Parallelization](04c_parallelization)) |
| **Loop Over Items** — and when a loop is *unnecessary* | New node |
| **Batching & rate limits** — be kind to APIs | Sets up [Reliable Tools and Sub-workflows](07b_reliable_tools_and_subworkflows) & Going Live |

**Workflow in this chapter:**

| File | What it does | GitHub Link |
|------|-------------|-------------|
| `19_multiple_items_reviews.json` | One item with 5 reviews → Split Out → Filter → Aggregate | [View](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/19_multiple_items_reviews.json) |

**Requirements:** just n8n. **No credentials, no AI, no API key** — the data is typed straight into the workflow.

---

## One item, or many? The distinction that matters

In n8n, data always moves as a **list of items**. Each item is a little box of JSON. A node runs **once for every item in the list** and passes its results on as a new list. That's the entire model — but there's one subtlety that causes 90% of early confusion:

> **A list *inside* one item is not the same as many items.**

Picture five product reviews. There are two completely different ways they can sit in n8n:

```
(A) ONE item that contains an array          (B) FIVE items, one review each
┌───────────────────────────────┐            ┌──────────────┐
│ {                             │            │ { product…,  │  item 1
│   reviews: [ r1, r2, r3, r4, r5 ] │  ──▶     │   rating: 5 }│
│ }                             │            ├──────────────┤
└───────────────────────────────┘            │ { rating: 2 }│  item 2
        1 item                                ├──────────────┤
   $json.reviews is the array                 │ { rating: 4 }│  item 3
                                              └──────────────┘  … 5 items
                                                $json is ONE review
```

Why it matters: a node runs **once per item**. In shape **(A)** an AI Agent or HTTP node fires **once** and sees all five reviews jammed together. In shape **(B)** it fires **five times**, once per review — perfect when you want to score, classify, or send each one on its own.

The node that converts **(A) → (B)** is **Split Out**. The node that converts **(B) → (A)** is **Aggregate**. Knowing which shape you're in — and how to switch — is the skill.

```{tip}
**How to read the shape at a glance.** Every node's output panel shows an **item count** in the corner (e.g. *5 items*) and a **Table / JSON / Schema** toggle. If you see one item with an array field, you're in shape (A). If you see many rows, you're in shape (B). Watching that number change as data flows is the fastest way to understand any workflow.
```

---

## The Workflow

```
Execute ──▶ One item, a list inside ──▶ Split Out ──▶ Filter ──▶ Aggregate
(Manual)    (Set: reviews = [ …5… ])    reviews      rating≤3   back to 1 item
              1 item                     5 items      3 items    1 item
```

Watch the **item count** under each node — it's the whole lesson in one number:

- **One item, a list inside (Set / Edit Fields)** — builds a single item whose `reviews` field is an array of 5 reviews. *Output: 1 item.*
- **Split Out** — splits that array into individual items. *Output: 5 items* — now `$json` is one review.
- **Filter** — keeps only reviews with `rating ≤ 3` (the ones worth following up). *Output: 3 items.*
- **Aggregate** — collapses the survivors back into a single item (a list you can hand to one email, one agent, one report). *Output: 1 item.*

**File:** [`19_multiple_items_reviews.json`](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/19_multiple_items_reviews.json)

> **Import via URL** (in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/19_multiple_items_reviews.json
> ```
>
> **Download:** {download}`19_multiple_items_reviews.json <_static/workflows/19_multiple_items_reviews.json>`

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Step 1: New workflow + Manual Trigger
**Workflows → Add Workflow**, rename it "Working with Multiple Items". Add a **Manual Trigger** (the *When clicking 'Execute'* node).

### Step 2: Make one item with a list inside
Add an **Edit Fields (Set)** node → rename `One item, a list inside`. Add one field:
- **Name:** `reviews`  **Type:** `Array`
- **Value** (switch to Expression, the `=` toggle):
  ```
  {{ [
    { "product": "Wireless Mouse", "rating": 5, "text": "Fast and comfortable." },
    { "product": "Wireless Mouse", "rating": 2, "text": "Stopped connecting." },
    { "product": "USB-C Hub",      "rating": 4, "text": "Solid, runs warm." },
    { "product": "USB-C Hub",      "rating": 1, "text": "Died on day two." },
    { "product": "Laptop Stand",   "rating": 3, "text": "Wobbles at full height." }
  ] }}
  ```
  Execute it. The output panel shows **1 item** with a `reviews` array.

### Step 3: Split Out
Add a **Split Out** node → set **Fields To Split Out** = `reviews`. Execute. The count jumps to **5 items**; each `$json` is now one review (`product`, `rating`, `text`).

### Step 4: Filter
Add a **Filter** node → rename `Keep low ratings (<= 3)`. Condition: `{{ $json.rating }}` **is less than or equal to** `3` (Number). Execute → **3 items** remain.

### Step 5: Aggregate
Add an **Aggregate** node → **Aggregate: All Item Data** (into one list). Execute → **1 item** whose `data` array holds the two low-rated reviews.

### Step 6: Connect
```
Execute → One item, a list inside → Split Out reviews → Keep low ratings → Aggregate
```
::::

### Node-by-Node Walkthrough

| Node | Type | Item count out | What it does |
|------|------|----------------|-------------|
| **One item, a list inside** | Edit Fields (Set) | **1** | Builds one item; `reviews` is an array of 5 |
| **Split Out reviews** | Split Out | **5** | One item per review — `$json` becomes a single review |
| **Keep low ratings (<= 3)** | Filter | **3** | Drops the items that don't match; keeps `rating ≤ 3` |
| **Aggregate back to one item** | Aggregate | **1** | Collapses the survivors into a single list |

---

## Data Flow — watch the count

```
One item, a list inside   →  { reviews: [r1,r2,r3,r4,r5] }              (1 item)
        ↓ Split Out reviews
5 separate items          →  {product:'Wireless Mouse', rating:5, …}   (item 1)
                             {product:'Wireless Mouse', rating:2, …}   (item 2)
                             {product:'USB-C Hub',      rating:4, …}   (item 3)
                             {product:'USB-C Hub',      rating:1, …}   (item 4)
                             {product:'Laptop Stand',   rating:3, …}   (item 5)
        ↓ Filter (rating <= 3)
3 items                   →  {rating:2 …}   {rating:1 …}   {rating:3 …}   (all ≤ 3 survive)
        ↓ Aggregate (all item data)
1 item                    →  { data: [ {rating:2…}, {rating:1…}, {rating:3…} ] }   (1 item)
```

::::{dropdown} 🔍 Key insight: per-item execution is automatic
:color: info

You never wrote a loop. After **Split Out**, *every* downstream node ran **once per review** on its own — Filter checked each rating, and if you'd put an AI Agent there it would have scored each review separately. n8n loops **for** you across items. That's why **Split Out** is so powerful: it turns "do this to the list" into "do this to each one" with no code.

And **Aggregate** is the undo: when you're done treating things individually and need *one* result (one email, one summary, one row), you collapse back to a single item.
::::

---

## Loop Over Items — and when you *don't* need it

Here's the surprise for anyone coming from spreadsheets or scripts: **most of the time you do not write a loop in n8n.** Because nodes already run once per item, a chain like `Split Out → HTTP Request → Set` calls the API once for each item automatically. No loop node required.

So when *is* the **Loop Over Items** node (formerly "Split In Batches") actually useful? Three honest cases:

| Use Loop Over Items when… | Why |
|---|---|
| You must process items **in batches** (e.g. 10 at a time) | An API rejects large bursts; batching respects its **rate limit** |
| Each round **depends on the previous** one | True sequential logic that per-item execution can't express |
| You need a **pause between batches** | Add a **Wait** node inside the loop to slow down and avoid `429 Too Many Requests` |

```
Loop Over Items (batch size 10)
   │  ┌───────────── loop ─────────────┐
   ├─▶│ HTTP Request → Wait 2s          │──┐
   │  └─────────────────────────────────┘  │ (repeats per batch)
   └─▶ done ──▶ continue                 ◀──┘
```

```{tip}
**When a loop is unnecessary:** if you just want to "do X to every item", **don't** add a Loop Over Items node — wire the items straight through and let n8n's per-item execution handle it. Reach for the loop only for **batching, rate-limit pacing, or genuinely sequential** work.
```

```{important}
**Batching and rate limits.** Public APIs cap how many calls you can make per second/minute. If you Split Out 500 rows and fire 500 requests at once, you'll get **429 Too Many Requests** and lose data. Two fixes: (1) **Loop Over Items** with a small batch size + a **Wait** node between batches, or (2) the HTTP Request node's own **Batching** option (in *Options → Batching*: items per batch + interval). You'll meet the production side of this — **Retry**, **Retry-After**, back-off — in *[Production Reliability](appendix_b2_production_reliability): Production Reliability*.
```

---

## A note on Merge

You already met **Merge** in *Parallelization* ([Parallelization](04c_parallelization)). It's the other half of the item toolkit: where **Aggregate** collapses *one* stream into a single item, **Merge** joins *two* streams. Common modes:

| Merge mode | Use it to… |
|---|---|
| **Append** | Stack two lists into one longer list |
| **Combine → By Position** | Pair item 1 with item 1, item 2 with item 2… |
| **Combine → By Matching Fields** | Join on a key (like a spreadsheet VLOOKUP), e.g. match `product` |

Rule of thumb: **Aggregate = many-into-one on a single branch. Merge = two branches into one.**

---

## Test It / What to Observe

### 1. Run it and watch the number
Click **Execute workflow**, then click each node left to right and read the **item count** in the output panel: **1 → 5 → 3 → 1**. That single changing number *is* the item model.

### 2. Flip the shape back and forth
Click **Split Out** (5 items, one review each) then **Aggregate** (1 item, a list). Toggle the output between **Table** and **JSON** to see the same data in both shapes.

### 3. Change the filter, change the count
Edit the Filter to `rating >= 4`. Re-run: now the count after Filter reflects the *good* reviews instead. The downstream Aggregate follows automatically.

---

## Try It Yourself

### Exercise: One summary line per product
Starting from the workflow above, produce **one item per product** (not per review) that reports the product name and its **average rating**.

Hints: after **Split Out**, use an **Aggregate** node set to *group* — or a **Summarize** node — to group by `product` and average the `rating` field. (The **Summarize** node is purpose-built for "group by X, average/count/min/max Y", like a pivot table.)

**Done when:** the final output has **3 items** — Wireless Mouse, USB-C Hub, Laptop Stand — each with an `average rating`.

::::{dropdown} 🛠️ Solution
:color: secondary

Replace the Filter + Aggregate with a single **Summarize** node after **Split Out**:

- **Fields to Summarize:** `rating` → aggregation **Average**
- **Fields to Split By:** `product`

Execute. Summarize groups the 5 reviews by `product` and outputs **3 items**, each with the product and its average rating (e.g. Wireless Mouse → 3.5, USB-C Hub → 2.5, Laptop Stand → 3). 

Why this works: **Summarize** is "group-by + aggregate" in one node — the no-code version of a spreadsheet pivot table. It replaces what would otherwise be a Loop Over Items plus manual math. Reach for it whenever you catch yourself about to loop just to compute a per-group total or average.
::::

---

## Summary

| Concept | What you learned |
|---------|------------------|
| **Item model** | Data is a list of items; a node runs **once per item**, automatically |
| **Array-in-item vs. many items** | A list inside one item ≠ many items — the source of most early confusion |
| **Split Out** | One item's array → many items (do something to *each*) |
| **Filter** | Drop items that don't match a rule |
| **Aggregate** | Many items → one item (a list) |
| **Summarize** | Group-by + average/count in one node (no loop) |
| **Merge** | Join two branches (Append / By Position / By Matching Fields) |
| **Loop Over Items** | Only for batching, rate-limit pacing, or truly sequential work |
| **Batching & 429** | Split + Wait or the HTTP Batching option to respect rate limits |

**Key ideas:**
- Watch the **item count** under each node — it tells you the data shape.
- **Split Out → do-per-item → Aggregate** is the everyday pattern.
- Don't add a loop just to "do X to each item" — n8n already does.

**Docs:**
- [Split Out](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.splitout/)
- [Aggregate](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.aggregate/)
- [Filter](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.filter/)
- [Summarize](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.summarize/)
- [Merge](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.merge/)
- [Loop Over Items](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.splitinbatches/)
- [Looping in n8n](https://docs.n8n.io/flow-logic/looping/)
