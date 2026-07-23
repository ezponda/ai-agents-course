# RAG: Teaching AI Your Data

LLMs are trained on public internet data. They don't know about:
- Your company's internal documents
- Yesterday's meeting notes
- Your product manual
- Any private information

**RAG** (Retrieval-Augmented Generation) solves this. It lets your AI search your documents and use what it finds to answer questions.

The classic analogy (IBM Research): it's the difference between a **closed-book and an open-book exam**. A plain LLM answers from memory and — like an over-confident new hire — will guess rather than admit it doesn't know. RAG hands it the open book: the relevant pages from *your* documents, so it answers from the source instead of from memory.

```
WITHOUT RAG                              WITH RAG
──────────                               ────────

User: "What's our refund policy?"        User: "What's our refund policy?"
                                                        │
         │                                              ▼
         ▼                               ┌─────────────────────────────┐
    ┌─────────┐                          │  Search your documents...   │
    │   LLM   │                          │  Found: refund_policy.pdf   │
    └─────────┘                          └─────────────────────────────┘
         │                                              │
         ▼                                              ▼
"I don't have access to                  ┌─────────────────────────────┐
 your company's policies."               │   LLM + your document       │
                                         └─────────────────────────────┘
                                                        │
                                                        ▼
                                         "Our refund policy allows
                                          returns within 30 days..."
```

**In this course, think of RAG as a Tool** — just like Calculator or Wikipedia. Your agent can call it when it needs facts from your documents.

| | Memory | RAG |
|--|--------|-----|
| **Purpose** | Remember conversation history | Retrieve knowledge from files |
| **When used** | Every message (automatic) | When agent needs specific info |
| **Data source** | Previous messages | Your indexed documents |

RAG is not chat memory. Memory keeps track of "what did the user say earlier?" RAG answers "what do my documents say about this?"

---

## Lexical Search vs Semantic Search

There are two fundamentally different ways to search text:

| | Lexical Search | Semantic Search |
|--|----------------|-----------------|
| **How it works** | Matches exact words | Matches meaning |
| **Also called** | Keyword search, full-text search | Vector search, similarity search |
| **Strength** | Fast, precise for exact terms | Understands synonyms, context |
| **Weakness** | Misses synonyms and related concepts | Can miss exact matches (IDs, codes) |

### The Vocabulary Mismatch Problem

Lexical search has a fundamental flaw: people use different words for the same thing.

```
YOUR DOCUMENTS SAY:                    USER SEARCHES FOR:
───────────────────                    ──────────────────

"Return items within 30 days           "refund policy"
 for a full credit."
                                              │
"Contact customer care for                    │
 assistance with exchanges."                  ▼

                              ┌─────────────────────────┐
                              │    LEXICAL SEARCH       │
                              │                         │
                              │  "refund" ≠ "return"    │
                              │  "policy" ≠ "credit"    │
                              │                         │
                              │      ❌ NO MATCH        │
                              └─────────────────────────┘

The document ANSWERS the question, but the WORDS don't match.
```

This is called the **vocabulary mismatch problem**. Real examples:

| User searches for... | Document says... | Lexical finds it? |
|---------------------|------------------|-------------------|
| "laptop" | "notebook computer" | No |
| "car issues" | "vehicle problems" | No |
| "how to cancel" | "termination process" | No |
| "cheap flights" | "budget airfare" | No |

### Semantic Search Solves This

Semantic search converts text to numbers that represent **meaning**, not just words.

```
USER QUERY: "refund policy"         YOUR DOCUMENTS:
           ↓                        ───────────────
    [meaning vector]                "Return items within 30 days" → [meaning vector]
           ↓                        "Contact customer care..."    → [meaning vector]
           ↓                        "Shipping takes 3-5 days"     → [meaning vector]
           ↓
           └──────────────┐
                          ▼
              ┌─────────────────────────┐
              │   SEMANTIC SEARCH       │
              │                         │
              │  Compare meanings...    │
              │                         │
              │  ✓ "Return items..."    │  ← closest meaning
              │  ✗ "Contact customer.." │
              │  ✗ "Shipping takes..."  │
              └─────────────────────────┘
```

The words "refund" and "return" are different, but their **meanings** are close — so semantic search finds the match.

---

## Embeddings: How Semantic Search Works

How does semantic search know that "refund" and "return" are related? Through **embeddings**.

An **embedding** is a list of numbers (called a "vector") that captures the meaning of text. Think of it as translating words into coordinates on a map.

```
TEXT                              EMBEDDING (simplified)
────                              ─────────────────────
"king"                     →      [0.2, 0.8, 0.1, ...]
"queen"                    →      [0.2, 0.8, 0.3, ...]
"apple"                    →      [0.9, 0.1, 0.2, ...]
```

Notice: "king" and "queen" have similar numbers because they're related concepts. "apple" is completely different.

### Similar Meanings = Close Vectors

Imagine a map where related concepts cluster together:

```
                    ▲
                    │
         "queen" ●  │  ● "king"
                    │
        "princess" ●│● "prince"
                    │
    ────────────────┼────────────────▶
                    │
                    │      ● "apple"
                    │  ● "banana"
                    │      ● "orange"
                    │

    Royalty clusters together.    Fruits cluster together.
    Far apart from each other.
```

When you search for "monarch", the system:
1. Converts "monarch" to a vector
2. Finds vectors closest to it on the map
3. Returns "king" and "queen" — even though the word "monarch" doesn't appear anywhere

### Who Creates the Embeddings?

Embedding models (like OpenAI's `text-embedding-3-small`) are trained on massive amounts of text to learn these meaning-relationships. You don't need to understand how they work — just know that:

- Same embedding model must be used for indexing AND querying
- Different models produce different vectors (not compatible)
- Embedding API calls have a cost (but much cheaper than LLM calls)

---

## Vector Stores: A Database for Meanings

A **vector store** is a database optimized for storing and searching embeddings.

```
TRADITIONAL DATABASE                   VECTOR STORE
────────────────────                   ────────────

┌────────────────────────┐             ┌────────────────────────┐
│  ID  │  Text           │             │  ID  │  Text  │ Vector │
├──────┼─────────────────┤             ├──────┼────────┼────────┤
│  1   │  "Return items  │             │  1   │  ...   │ [0.2,  │
│      │   within 30..." │             │      │        │  0.8]  │
│  2   │  "Contact us at │             │  2   │  ...   │ [0.5,  │
│      │   support@..."  │             │      │        │  0.3]  │
└──────┴─────────────────┘             └──────┴────────┴────────┘

Search: WHERE text LIKE '%refund%'     Search: Find vectors closest to
Result: Nothing found                          [0.2, 0.7] ("refund policy")
                                       Result: Document 1 (closest match)
```

The vector store doesn't look for matching words — it finds documents whose *meaning* is closest to your query.

---

## The RAG Pipeline

RAG has two stages that run at different times:

| Stage | When it runs | What it does |
|-------|-------------|--------------|
| **Indexing** | Once (or when docs change) | Load → Chunk → Embed → Store |
| **Query** | Every user question | Embed query → Search → Answer |

You don't re-index your documents every time someone asks a question.

### Stage 1: Indexing (Build Your Knowledge Base)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Your Docs  │───▶│   Chunker   │───▶│  Embeddings │───▶│Vector Store │
│  (PDF, txt) │    │(split text) │    │(text→vector)│    │  (save)     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Stage 2: Query (Answer Questions)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │───▶│  Embeddings │───▶│Vector Store │───▶│     LLM     │
│   Question  │    │(query→vector)│   │  (search)   │    │  (answer)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                             │
                                             ▼
                                      Top 3 relevant
                                         chunks
```

The LLM receives your question *plus* the relevant document chunks. Now it can answer accurately using **only** the provided context.

**In n8n,** both stages can live in the same workflow using two triggers: a Form Trigger for uploading documents (indexing) and a Chat Trigger for queries. We'll do exactly this in the hands-on example below.

---

## Why Chunking Matters

Why not just send the entire document to the LLM?

**1. Context window limits.** LLMs can only process a limited amount of text at once (16K–200K tokens depending on the model). 500 pages of docs won't fit.

**2. Cost.** More tokens = higher cost. Sending 3 relevant chunks is much cheaper than sending 500 pages.

**3. Focus.** When LLMs receive too much text, they miss important details buried in irrelevant content. Smaller, focused chunks lead to better answers.

```
SEND EVERYTHING                         RAG
───────────────                         ───

500 pages → LLM                         500 pages → search → 3 chunks → LLM

Expensive, slow, unfocused              Cheap, fast, accurate
LLM may miss page 47                    LLM gets exactly what it needs
```

---

## Chunking Strategies

How you split documents affects retrieval quality. Bad chunks = bad answers.

### The Chunking Trade-off

```
Too Small (50 chars)           Just Right (300-800)           Too Large (2000+ chars)
────────────────────           ────────────────────           ──────────────────────

"Returns within"               "Return items within           "Return items within 30
                                30 days with receipt            days with receipt...
"30 days with"                  for full refund.               [+ long paragraph about
                                Exchanges available             shipping, store hours,
"receipt for full"              within 60 days."                etc.]"

Lost context                   Complete thought                Too much noise
Fragments don't make sense     Focused and searchable          Irrelevant info retrieved
```

### Chunk Overlap

Overlap prevents cutting sentences in half at chunk boundaries.

```
WITHOUT OVERLAP                         WITH OVERLAP (25%)
───────────────                         ──────────────────

Chunk 1: "Our refund policy allows"     Chunk 1: "Our refund policy allows
Chunk 2: "returns within 30 days."                returns within 30 days."
                                        Chunk 2: "returns within 30 days.
"returns" is cut off from                         A receipt is required
 "refund policy"                                  for all returns."
```

**Typical settings:** Chunk size 400–1000 characters, overlap 10–25%.

### Chunking Strategies Comparison

| Strategy | How it works | Best for |
|----------|--------------|----------|
| **Recursive** | Split by paragraphs, then sentences, then words | Most documents (recommended) |
| **Fixed size** | Split every N characters | Simple, predictable |
| **By section** | Split at headers (##, ###) | Markdown, structured docs |

n8n's **Recursive Character Text Splitter** is the most versatile — it tries to keep paragraphs together, then sentences, then words.

---

## RAG Components in n8n

n8n provides nodes for each step of the RAG pipeline:

| Component | n8n Node | What it does |
|-----------|----------|-------------|
| **Document Loader** | Default Data Loader, GitHub, Google Drive | Reads your files |
| **Text Splitter** | Recursive Character Text Splitter | Breaks docs into chunks |
| **Embeddings** | Google Gemini, OpenAI, Ollama | Converts text to vectors |
| **Vector Store** | Simple Vector Store, Supabase, Pinecone, Qdrant | Stores and searches vectors |

### Vector Store Options

| Option | Persistence | Best for |
|--------|-------------|----------|
| **Simple Vector Store** | Lost on restart | Learning, quick tests |
| **Supabase** | Persistent | Production with PostgreSQL |
| **Pinecone** | Persistent | Large-scale, managed |
| **Qdrant** | Persistent | Self-hosted, open source |

For this course, we'll use **Simple Vector Store** — it works immediately without any external database setup.

> **Warning: Simple Vector Store Limitations**
>
> - **Not persistent**: Data is stored in memory and **lost when n8n restarts**
> - **Shared access**: All users on the same n8n instance can access the stored data
> - **Not for production**: Use a proper vector database (Supabase, Pinecone, Qdrant) for real applications

### Vector Store as Agent Tool

Since n8n 1.74, you can connect a Vector Store directly to an AI Agent as a **tool**. The agent decides when to search it — just like Calculator or SerpAPI:

```
AI AGENT
  Tools available:
  ├── Calculator
  ├── SerpAPI
  └── Vector Store (as Tool)  ◀── searches your indexed documents
```

Set the Vector Store to mode **"Retrieve Documents (as Tool for AI Agent)"** and give it a good description so the agent knows when to use it. This is the approach we'll use in the hands-on below.

**Docs:** [RAG in n8n](https://docs.n8n.io/advanced-ai/rag-in-n8n/)

---

## Hands-On: Document Chat with RAG

Let's put everything together. We'll build a bot that lets you **upload a PDF** and then chat with its contents. The bot answers using *only* the uploaded document — not the LLM's training data.

We provide a sample PDF — the **DataLearn Employee Handbook** (5 pages of company policies, benefits, and procedures) — but you can upload any text-based PDF.

**One workflow, two paths:**

```
LEFT SIDE (upload & index)                     RIGHT SIDE (chat)
──────────────────────────                     ──────────────────

┌──────────────┐  ┌───────────┐                ┌─────────────┐  ┌───────────┐  ┌──────────┐
│ Upload       │─▶│ Vector    │                │Chat Trigger │─▶│ AI Agent  │─▶│ Output   │
│ Document     │  │ Store     │                │             │  │           │  │          │
│ (Form)       │  │ (Insert)  │                └─────────────┘  └───────────┘  └──────────┘
└──────────────┘  └───────────┘                                     ┊
                   ┊ sub-nodes                                ┌────┼─────────────┐
                   ┊                                          ┊    ┊             ┊
             ┌─────┴─────┐                              ┌──────┐ ┌──────┐ ┌───────────┐
       ┌──────────┐ ┌─────────┐                         │Model │ │Memory│ │Vector     │
       │Embeddings│ │ Loader  │                         │      │ │      │ │Store      │
       │ Gemini   │ │(Binary) │                         └──────┘ └──────┘ │(Retrieve) │
       └──────────┘ │+ Split  │                                           └───────────┘
                    └─────────┘                                              ┊
                                                                       ┌──────────┐
                                                                       │Embeddings│
                                                                       │ Gemini   │
                                                                       └──────────┘
```

Both sides share the same `memoryKey: "doc_store"`. You upload a document once (left), then chat as many times as you want (right).

```{important}
**Index first, in the same session.** The Simple Vector Store keeps data in memory, shared by `memoryKey`. The upload side (Form) and the chat side run as **separate executions** — so you must upload the document **before** chatting, and if n8n restarts the store is empty until you upload again.
```

**File:** [`14_rag_faq_bot.json`](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/14_rag_faq_bot.json)

> **Import via URL** (copy and paste in n8n → Import from URL):
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/14_rag_faq_bot.json
> ```
>
> **Download:** {download}`14_rag_faq_bot.json <_static/workflows/14_rag_faq_bot.json>`

### Sample PDF

Download the DataLearn Employee Handbook to use with this workflow:

> **Download:** {download}`datalearn_employee_handbook.pdf <_static/data/datalearn_employee_handbook.pdf>`
>
> Or copy the direct URL to download it manually:
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/data/datalearn_employee_handbook.pdf
> ```

### Embedding Credentials

These workflows use **Google Gemini Embeddings** (`text-embedding-004`), which is free. (A newer `gemini-embedding-001` also works — just make sure you use the **same** model on both sides.)

**Setup:** Get a free API key from [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key) → add it in n8n: Settings → Credentials → Google Gemini (PaLM) Api.

**Important:** The same embeddings model must be used on both sides. Mixing models produces incorrect results.

::::{dropdown} 🛠️ Build this workflow from scratch (step-by-step)
:color: secondary

### Part A: Indexing side (upload and index a document)

**Step 1:** Add **Form Trigger** → rename to `Upload Document (Form)`. Configure:

| Parameter | Value |
|-----------|-------|
| **Form Title** | `Upload Document` |
| **Form Description** | `Upload a PDF or text file to create a searchable knowledge base.` |

Add one form field:

| Field Label | Field Type | Accept File Types | Required |
|-------------|-----------|-------------------|----------|
| `Document` | `File` | `.pdf,.txt,.md` | Yes |

In **Options**:
- Respond With: `Text`
- Form Submitted Text: `Document uploaded and indexed successfully! You can now open the Chat in n8n to ask questions.`

**Step 2:** Add **Simple Vector Store** → rename to `Vector Store — Insert`

| Parameter | Value |
|-----------|-------|
| Mode | `Insert Documents` |
| Memory Key | `doc_store` |
| Clear Store | Enabled |

**Step 3:** Add sub-nodes to the Vector Store:
- **Embedding** connector → **Embeddings Google Gemini** (model: `text-embedding-004`)
- **Document** connector → **Default Data Loader** → set **Type of Data** to `Binary` → inside it, **Text Splitter** connector → **Recursive Character Text Splitter** (Chunk Size: `400`, Overlap: `100`)

**Step 4:** Connect: Upload Document (Form) → Vector Store — Insert

### Part B: Chat side (ask questions)

**Step 5:** Add **Chat Trigger** (When chat message received). In Options: Response Mode → `When Last Node Finishes`

**Step 6:** Add **AI Agent** → rename to `AI Agent — Document Assistant`
- Source for Prompt: `Define below`
- Prompt (Expression): `{{ $json.chatInput }}`
- System Message (in Options):

```
You are a helpful document assistant.

Rules:
- ALWAYS search the document knowledge base before answering.
- Answer ONLY based on the information found in the uploaded document.
- If the document does not contain the answer, say: "I don't have that information in the uploaded document."
- Keep answers concise and friendly.
- Do not make up information.
```

**Step 7:** Add sub-nodes to the AI Agent:
- **Chat Model** → **OpenRouter Chat Model** (model: `openai/gpt-4o-mini`)
- **Memory** → **Window Buffer Memory** (Session Key: `{{ $json.sessionId }}`, Context Window: `10`)
- **Tool** → **Simple Vector Store** → rename to `Vector Store — Search`
  - Mode: `Retrieve Documents (as Tool for AI Agent)`
  - Memory Key: `doc_store`
  - Tool Description: `Knowledge base containing the uploaded document. Use this to answer any question about the document content.`
  - Add **Embeddings Google Gemini** sub-node (same model: `text-embedding-004`)

**Step 8:** Add **Edit Fields** → rename to `Output — Chat Response`
- Field: `output` = `{{ $json.output }}` (must be named `output` for Chat Trigger)

**Step 9:** Connect: Chat Trigger → AI Agent → Output

::::

### How to Use

1. **Publish the workflow** (click *Publish* in the top-right corner) — this makes the Form Trigger URL accessible on its production URL
2. Open the **Form Trigger URL** (click on the Form Trigger node to see it) and upload a PDF
3. After the form confirms success, click the **Chat** button in n8n to ask questions
4. The data stays in memory as long as n8n is running — upload again if n8n restarts

```{tip}
For quick testing without publishing: click **Test URL** in the Form Trigger node — this exposes a temporary URL that uses your current draft, no Publish needed.
```

```{note}
**Troubleshooting:** if the agent says *"I don't have that information"* for something that **is** in the document, you almost certainly haven't indexed it in this session — re-open the Form and upload again (the Simple Vector Store is emptied on restart). Also check both Embeddings nodes use the **same** model.
```

### System Message

```
You are a helpful document assistant.

Rules:
- ALWAYS search the document knowledge base before answering.
- Answer ONLY based on the information found in the uploaded document.
- If the document does not contain the answer, say: "I don't have that information in the uploaded document."
- Keep answers concise and friendly.
- Do not make up information.
```

**Why "ONLY based on the uploaded document"?** Without this rule, the LLM falls back to its training data and may invent answers. This is the most important RAG guardrail.

### What to Test (with the Employee Handbook)

| Question | Expected behavior |
|----------|-------------------|
| `What is the remote work policy?` | Answers from document: "Up to 3 days/week, Tue/Thu mandatory..." |
| `How many vacation days do I get?` | Answers from document: "25 working days per year..." |
| `What is the learning budget?` | Answers from document: "1,500 EUR per year..." |
| `What is the best pizza in Madrid?` | Should say it doesn't have that info in the document |
| `Do we get stock options?` | Answers from document: "Staff level and above, 4-year vesting..." |

---

## Moving to Production

The Simple Vector Store above loses data when n8n restarts. To make it persistent, replace the two Simple Vector Store nodes with a persistent option (Supabase, Pinecone, Qdrant — see the table in [RAG Components](#rag-components-in-n8n) above). The rest of the workflow stays exactly the same — same embeddings, same agent, same system message.

```{note}
**Beyond this course.** Production RAG usually adds a few upgrades you'll hear about: **hybrid search** (semantic + keyword, to catch exact IDs and rare terms), **reranking** (a second model re-orders the retrieved chunks for relevance), and **agentic RAG** (the agent reformulates the query or searches several times). You can also expose a knowledge base over **MCP** so other apps share it. The pattern in this chapter is the foundation they all build on.
```

---

---

## RAG vs Fine-Tuning vs Long Context

There are other ways to give LLMs custom knowledge. When should you use RAG?

| Approach | How it works | Best for |
|----------|--------------|----------|
| **RAG** | Search docs at query time | Facts that change, large doc collections |
| **Fine-tuning** | Retrain the model on your data | Teaching new skills or style |
| **Long context** | Paste entire docs in the prompt | Small, static documents |

### When to Choose RAG

```
                        Use RAG when:
                        ─────────────
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ✓ Documents change frequently (policies, product info)        │
│  ✓ Too many documents to fit in one prompt                     │
│  ✓ You need citations ("where did this answer come from?")     │
│  ✓ Different users need access to different documents          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

                        DON'T use RAG when:
                        ──────────────────
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ✗ You have just 1-2 small documents (paste in prompt instead) │
│  ✗ You want to change HOW the model writes (fine-tune instead) │
│  ✗ The info is already in the model's training data            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common RAG Challenges

RAG isn't magic. Here are common issues and how to handle them:

| Challenge | What happens | Solution |
|-----------|--------------|----------|
| **Wrong chunks retrieved** | Semantic search finds unrelated text | Improve chunking, add metadata filters |
| **Answer not in docs** | LLM hallucinates an answer anyway | Add "only answer from context" instruction |
| **Chunks too small** | Missing context around the answer | Increase chunk size or overlap |
| **Chunks too large** | Irrelevant text included | Decrease chunk size |
| **Outdated embeddings** | New docs not searchable | Re-run indexing pipeline |
| **Slow queries** | Vector search takes too long | Use faster vector store, reduce chunk count |

```{warning}
**RAG fails *silently*.** When retrieval misses, you don't get an error — you get a fluent, confident answer that is subtly wrong. That's why you should test with a document whose answers you already know, and keep the "answer only from context" rule below.
```

### Try It: make retrieval fail on purpose

A great way to *feel* RAG's limits (using the Employee Handbook from the hands-on):

- **Missing data** — ask `What is the best pizza in Madrid?` → the agent should say it's not in the document (good — the guardrail working).
- **Vocabulary mismatch** — the doc says "annual leave" but you ask about "time off" or "PTO" → watch whether retrieval still finds it. Usually it does (that's semantic search), which is the whole point.
- **Chunk too small** — re-index with a tiny chunk size and no overlap, then ask a question whose answer spans two sentences → it may now miss.

### Hallucination Prevention

Even with RAG, LLMs may invent answers when the context doesn't contain the information. Add this to your system prompt:

```
Answer ONLY based on the provided context.
If the answer is not in the context, say "I don't have information about that."
Do not make up information.
```

### When Semantic Search Fails

Semantic search has blind spots — it can miss:

| What it misses | Example | Solution |
|----------------|---------|----------|
| **Exact IDs/codes** | "Order #12345" | Add keyword search (hybrid) |
| **Acronyms** | "What does HIPAA mean?" | Expand acronyms in docs |
| **Very specific terms** | Technical jargon | Ensure terms appear in the document |

For production systems, **hybrid search** (semantic + lexical) plus **reranking** often works best.

---

## Summary

| Concept | Key Point |
|---------|----------|
| **RAG** | Retrieval-Augmented Generation — search your docs, then answer |
| **Lexical vs Semantic** | Keyword matching vs meaning matching |
| **Vocabulary mismatch** | Why keyword search fails ("refund" ≠ "return") |
| **Embeddings** | Convert text to vectors that capture meaning |
| **Vector Store** | Database optimized for similarity search |
| **Context Window** | LLMs can only process limited text — RAG retrieves what's relevant |
| **Chunking** | Split docs into searchable pieces (500-1000 tokens typical) |
| **Overlap** | Prevents losing context at chunk boundaries (10-20%) |

**Key insight:** RAG makes LLMs useful for your private data without retraining. Instead of stuffing everything into the prompt (expensive, slow, unfocused), you search for relevant chunks and send only those.
