# Appendix C: Specialized AI Nodes

This appendix covers **specialized AI nodes** that solve specific tasks more efficiently than the general-purpose AI Agent.

**The key insight:** Before reaching for the AI Agent, ask yourself: *"Is there a node built specifically for this task?"*

| Task | Use this node | Not AI Agent |
|------|---------------|---------------|
| Classify text into categories | Text Classifier | |
| Detect positive/negative sentiment | Sentiment Analysis | |
| Extract structured data from text | Information Extractor | |
| Summarize long documents | Summarization Chain | |
| Answer questions about documents | Question and Answer Chain | |

**Why use specialized nodes?**
- Simpler to configure (no tools, no memory)
- More predictable outputs
- Built-in output branches for routing

```{note}
AI Agent and Basic LLM Chain are covered in the [Node Toolbox](appendix_a_node_toolbox) appendix.
```

---

## 1. Text Classifier

**What it solves:** Routes incoming text to different branches based on categories you define. Think of it as an AI-powered Switch node.

### Example: Support Ticket Router

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INPUT                                                                      │
│  ─────                                                                      │
│  "The screen freezes when I click the submit button"                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │ Text Classifier │
                          │                 │
                          │ Categories:     │
                          │ • Bug Report    │
                          │ • Feature Req   │
                          │ • Billing       │
                          └─────────────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               ▼                    ▼                    ▼
        ┌───────────┐        ┌───────────┐        ┌───────────┐
        │ Bug Report│        │Feature Req│        │  Billing  │
        │  (branch) │        │  (branch) │        │  (branch) │
        └───────────┘        └───────────┘        └───────────┘
              ✓
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Input Prompt** | The text to classify (e.g., `{{ $json.text }}`) |
| **Categories** | List of categories, each with a name and description |

### Options

| Option | Description |
|--------|-------------|
| **Allow Multiple Classes To Be True** | Enables multiple categories to match simultaneously |
| **When No Clear Match** | "Discard Item" (default) or "Output on Extra 'Other' Branch" |
| **System Prompt Template** | Custom instructions using `{categories}` placeholder |
| **Enable Auto-Fixing** | Automatically fixes model output formatting errors |

### Category Configuration

Each category needs a **name** and **description**:

| Category | Description |
|----------|-------------|
| `bug_report` | User reports something broken or not working |
| `feature_request` | User wants new functionality added |
| `billing` | Questions about payments, invoices, refunds |

**Tip:** Better descriptions = better accuracy. Be specific about what each category includes.

### Output

Data flows to the matching category branch:

```json
{ "category": "bug_report" }
```

### Common Mistake

**Too many categories.** Each category you add reduces accuracy. Start with 2-4 categories and only add more if needed.

**Docs:** [Text Classifier](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.text-classifier/)

::::{dropdown} 🔧 Under the hood: This node is a Basic LLM Chain + Structured Output Parser
:color: secondary

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│    Input     │────▶│  Basic LLM   │────▶│   Structured │────▶│  Switch  │
│    Text      │     │    Chain     │     │ Output Parser│     │  (route) │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────┘
                            │
                            ▼
                     System Prompt +
                     Format Instructions
```

**Internal System Prompt:**
```text
Please classify the text provided by the user into one of the following categories: 
{categories}, and use the provided formatting instructions below. 
Don't explain, and only output the json.
```

The node uses a Zod schema to enforce JSON output where each category becomes a boolean field.

**Source:** [TextClassifier.node.ts](https://github.com/n8n-io/n8n/blob/master/packages/%40n8n/nodes-langchain/nodes/chains/TextClassifier/TextClassifier.node.ts)

::::

---

## 2. Sentiment Analysis

**What it solves:** Determines if text is positive, neutral, or negative. Useful for monitoring brand mentions, filtering feedback, or routing customer messages.

### Example: Review Analyzer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INPUT                                                                      │
│  ─────                                                                      │
│  "This product exceeded my expectations! Highly recommend."                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────┐
                        │ Sentiment Analysis│
                        └───────────────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               ▼                    ▼                    ▼
        ┌───────────┐        ┌───────────┐        ┌───────────┐
        │  Positive │        │  Neutral  │        │  Negative │
        │  (branch) │        │  (branch) │        │  (branch) │
        └───────────┘        └───────────┘        └───────────┘
              ✓
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Text to Analyze** | The input text (e.g., `{{ $json.review }}`) |

### Options

| Option | Description |
|--------|-------------|
| **Sentiment Categories** | Default: Positive, Neutral, Negative (customizable) |
| **Include Detailed Results** | Adds confidence scores (model estimates, not precise metrics) |
| **System Prompt Template** | Custom instructions using `{categories}` placeholder |
| **Enable Auto-Fixing** | Automatically fixes model output formatting errors |

### Custom Categories

You can customize the sentiment categories for more granular analysis:

```
Very Positive, Positive, Neutral, Negative, Very Negative
```

Or add domain-specific categories:

```
Excited, Happy, Neutral, Disappointed, Angry
```

### Output

Data flows to the matching sentiment branch:

```json
{ "category": "positive" }
```

With detailed results enabled:

```json
{ 
  "category": "positive",
  "confidence": 0.92
}
```

**Note:** Confidence scores are model-generated estimates, not precise measurements.

### Common Mistake

**Ignoring context.** Sarcasm and irony can fool sentiment analysis. If your use case involves nuanced text, add context in the System Prompt. Also, set model temperature to 0 for consistent results.

**Docs:** [Sentiment Analysis](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.sentimentanalysis/)

::::{dropdown} 🔧 Under the hood: This node is a Basic LLM Chain + Structured Output Parser
:color: secondary

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│    Input     │────▶│  Basic LLM   │────▶│   Structured │────▶│  Switch  │
│    Text      │     │    Chain     │     │ Output Parser│     │  (route) │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────┘
                            │
                            ▼
                     System Prompt +
                     Format Instructions
```

**Internal System Prompt:**
```text
You are highly intelligent and accurate sentiment analyzer. 
Analyze the sentiment of the provided text. 
Categorize it into one of the following: {categories}. 
Use the provided formatting instructions. Only output the JSON.
```

The node outputs a Zod schema with three fields:
- `sentiment`: enum matching the categories
- `strength`: 0-1 score for intensity
- `confidence`: 0-1 score for certainty

**Source:** [SentimentAnalysis.node.ts](https://github.com/n8n-io/n8n/blob/master/packages/%40n8n/nodes-langchain/nodes/chains/SentimentAnalysis/SentimentAnalysis.node.ts)

::::

---

## 3. Information Extractor

**What it solves:** Pulls structured data from unstructured text. Replaces complex regex patterns with natural language descriptions.

### Example: Resume Parser

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INPUT                                                                      │
│  ─────                                                                      │
│  "John Smith is a software engineer with 5 years of experience.            │
│   He currently works at Tech Corp earning $95,000 annually.                 │
│   Contact: john.smith@email.com"                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────┐
                      │  Information Extractor  │
                      │                         │
                      │  Schema:                │
                      │  • name (string)        │
                      │  • years_exp (number)   │
                      │  • salary (number)      │
                      │  • email (string)       │
                      └─────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  OUTPUT                                                                     │
│  ──────                                                                     │
│  {                                                                          │
│    "name": "John Smith",                                                    │
│    "years_exp": 5,                                                          │
│    "salary": 95000,                                                         │
│    "email": "john.smith@email.com"                                          │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Text** | The input text to extract from (e.g., `{{ $json.text }}`) |
| **Schema Type** | How to define the output structure (see below) |

### Schema Type Options

| Option | Description |
|--------|-------------|
| **From Attribute Descriptions** | Define attributes manually with name, type, and description |
| **Generate From JSON Example** | Provide a sample JSON; n8n infers the schema (all fields treated as mandatory) |
| **Define using JSON Schema** | Write a full JSON Schema for complete control |

### Defining Attributes (Recommended)

When using "From Attribute Descriptions", define each field:

| Name | Type | Description |
|------|------|-------------|
| `name` | String | Person's full name |
| `salary` | Number | Annual salary without currency symbol or commas |
| `email` | String | Email address if present, null otherwise |

**Tip:** The description tells the AI exactly what to look for and how to format it. Be specific.

### Options

| Option | Description |
|--------|-------------|
| **System Prompt Template** | Custom instructions for the extraction |

### Output

A JSON object with your defined attributes:

```json
{
  "output": {
    "name": "John Smith",
    "years_exp": 5,
    "salary": 95000,
    "email": "john.smith@email.com"
  }
}
```

### Common Mistake

**Vague descriptions.** "Get the salary" is worse than "Extract the annual salary as a number without currency symbols or commas." Specificity improves accuracy.

**Docs:** [Information Extractor](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.information-extractor/)

::::{dropdown} 🔧 Under the hood: This node is a Basic LLM Chain + Structured Output Parser
:color: secondary

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Input     │────▶│  Basic LLM   │────▶│   Structured │────▶  JSON
│    Text      │     │    Chain     │     │ Output Parser│      Output
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     System Prompt +
                     Zod Schema from
                     your attributes
```

The node dynamically creates a Zod schema from your attribute definitions, then uses `StructuredOutputParser` (with optional `OutputFixingParser` for auto-correction) to enforce the JSON format.

The system prompt template is customizable, and the node automatically appends format instructions based on your schema.

**Source:** [InformationExtractor.node.ts](https://github.com/n8n-io/n8n/blob/master/packages/%40n8n/nodes-langchain/nodes/chains/InformationExtractor/InformationExtractor.node.ts)

::::

---

## 4. Summarization Chain

**What it solves:** Condenses long text into shorter summaries. Handles documents that exceed the model's context window by chunking.

### Example: Article Summarizer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INPUT                                                                      │
│  ─────                                                                      │
│  [5,000 word article about climate change policies...]                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────┐
                      │  Summarization Chain    │
                      │                         │
                      │  Method: Map Reduce     │
                      └─────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  OUTPUT                                                                     │
│  ──────                                                                     │
│  "The article discusses three major climate policies proposed in 2025:     │
│   carbon taxation, renewable energy subsidies, and emission caps.           │
│   Key findings suggest carbon taxation is most effective but faces          │
│   political resistance..."                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Data to Summarize** | Source of the text (see options below) |

### Data Source Options

| Option | Description |
|--------|-------------|
| **Use Node Input (JSON)** | Takes text from a JSON field in the input |
| **Use Node Input (Binary)** | Takes text from a binary file |
| **Use Document Loader** | Connects to a Document Loader sub-node |

### Chunking Strategy

When using Node Input, configure how to split long text:

| Strategy | Description |
|----------|-------------|
| **Simple (Define Below)** | Set Characters Per Chunk and Chunk Overlap manually |
| **Advanced** | Connect a Text Splitter sub-node for more control |

### Summarization Methods (Add via Options)

| Method | How it works | Best for |
|--------|--------------|----------|
| **Stuff** | Sends all text at once | Short documents (< 4000 tokens) |
| **Map Reduce** | Summarizes chunks in parallel, then combines | Long documents (recommended) |
| **Refine** | Iteratively improves summary with each chunk | Maximum accuracy |

### Customizable Prompts

| Prompt | Description |
|--------|-------------|
| **Individual Summary Prompt** | Instructions for summarizing each chunk (must include `{text}`) |
| **Final Prompt to Combine** | Instructions for the final summary (must include `{text}`) |

### Output

```json
{ "text": "The article discusses three major climate policies..." }
```

### Common Mistake

**Using Stuff for long documents.** If your text exceeds the model's context window, the node will fail. Use Map Reduce or Refine instead.

**Docs:** [Summarization Chain](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.chainsummarization/)

::::{dropdown} 🔧 Under the hood: This node uses LangChain's loadSummarizationChain
:color: secondary

Unlike the previous nodes, Summarization Chain is **not** a simple Basic LLM Chain wrapper. It uses LangChain's `loadSummarizationChain` function which implements complex strategies:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STUFF (simple)                                                             │
│  ───────────────                                                            │
│  All text ───▶ Single LLM call ───▶ Summary                                 │
│                                                                             │
│  (This one CAN be replicated with Basic LLM Chain)                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  MAP REDUCE (complex)                                                       │
│  ────────────────────                                                       │
│                                                                             │
│  Chunk 1 ───▶ LLM ───▶ Summary 1 ─┐                                         │
│  Chunk 2 ───▶ LLM ───▶ Summary 2 ─┼───▶ LLM ───▶ Final Summary              │
│  Chunk 3 ───▶ LLM ───▶ Summary 3 ─┘                                         │
│                                                                             │
│  (Multiple parallel LLM calls + combining logic)                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  REFINE (iterative)                                                         │
│  ──────────────────                                                         │
│                                                                             │
│  Chunk 1 ───▶ LLM ───▶ Summary v1                                           │
│                            │                                                │
│  Chunk 2 + Summary v1 ───▶ LLM ───▶ Summary v2                              │
│                                         │                                   │
│  Chunk 3 + Summary v2 ───────────────▶ LLM ───▶ Final Summary               │
│                                                                             │
│  (Sequential LLM calls that build on each other)                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Source:** [ChainSummarizationV2.node.ts](https://github.com/n8n-io/n8n/blob/master/packages/%40n8n/nodes-langchain/nodes/chains/ChainSummarization/V2/ChainSummarizationV2.node.ts)

::::

---

## 5. Question and Answer Chain

**What it solves:** Answers questions based on your documents. This is the core node for RAG (Retrieval-Augmented Generation) workflows.

### Example: PDF Q&A System

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SETUP PHASE (run once)                                                     │
│  ─────────────────────                                                      │
│                                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   PDF    │───▶│ Text Splitter│───▶│  Embeddings  │───▶│ Vector Store │  │
│  │  Loader  │    │   (chunks)   │    │              │    │  (Pinecone)  │  │
│  └──────────┘    └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  QUERY PHASE (each question)                                                │
│  ───────────────────────────                                                │
│                                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Question │───▶│   Q&A Chain  │◀───│ Vector Store │◀───│  Embeddings  │  │
│  │          │    │              │    │  (retriever) │    │              │  │
│  └──────────┘    └──────────────┘    └──────────────┘    └──────────────┘  │
│                         │                                                   │
│                         ▼                                                   │
│                  ┌──────────────┐                                           │
│                  │    Answer    │                                           │
│                  │  (grounded   │                                           │
│                  │  in docs)    │                                           │
│                  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Required Sub-Nodes

Q&A Chain requires several connected components:

| Sub-node | Purpose |
|----------|---------|
| **Chat Model** | Generates answers (required) |
| **Retriever** | Fetches relevant document chunks (required) |

The Retriever connects to a **Vector Store** which needs **Embeddings**.

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Prompt** | The user's question (e.g., `{{ $json.question }}`) |

### Retriever Configuration

On the Vector Store (in Retriever mode):

| Parameter | Description |
|-----------|-------------|
| **Limit** | Number of chunks to retrieve (e.g., 4-10) |
| **Reranking** | Optional: connect a reranker to improve relevance |

### Output

```json
{ 
  "text": "According to the document, the return policy allows returns within 30 days..."
}
```

### Common Mistakes

**Mismatched embeddings.** The embeddings model used to store documents must match the one used for retrieval. If you indexed with OpenAI embeddings, you must query with OpenAI embeddings.

**Too few or too many chunks.** Start with 4 chunks. Too few = missing context. Too many = noise dilutes relevance.

```{note}
For a complete RAG tutorial, see the [RAG chapter](09_rag).
```

**Docs:** [Question and Answer Chain](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.chainretrievalqa/)

---

## Quick Reference

| Node | Input | Output | Use When |
|------|-------|--------|----------|
| **Text Classifier** | Text | Category + branch | Routing based on content type |
| **Sentiment Analysis** | Text | Sentiment + branch | Detecting positive/negative tone |
| **Information Extractor** | Text | Structured JSON | Parsing unstructured data |
| **Summarization Chain** | Long text | Short summary | Condensing documents |
| **Q&A Chain** | Question + docs | Answer | Answering from your data |

---

## When to Use AI Agent Instead

Use **AI Agent** when you need:

- **Tools** — The AI needs to call APIs, search the web, or use calculators
- **Memory** — Multi-turn conversations that remember context
- **Dynamic decisions** — The AI needs to choose what to do based on the situation
- **Multiple steps** — Tasks that require reasoning through several actions

Use **specialized nodes** when:

- The task is **single-purpose** (classify, extract, summarize)
- You need **predictable outputs** with specific formats
- You want **simpler workflows** without tool configuration
- You're building **pipelines** where each step has a clear function
