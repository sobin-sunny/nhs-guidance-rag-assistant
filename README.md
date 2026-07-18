# NHS Guidance Assistant : A Retrieval-Augmented Generation (RAG) prototype

A chat assistant over public NHS guidance documents.
It answers plain English questions from a user using **only** the source documents and shows
the exact source (document and page) behind every answer. It runs **entirely on
your own machine, for free**. 

There are no API keys, no cloud, and no data leaving the
device in this prototype design.

> **Status:** working prototype, built as a portfolio project to demonstrate the
> modern GenAI engineering stack : retrieval-augmented generation, embeddings,
> vector search, LangChain orchestration, and prompt engineering which are applied to a
> realistic public-sector use case. A one-page
> [design & governance note](NHS_RAG_Assistant_Design_Note.pdf) sets out how it
> would be productionised and governed responsibly.
>
> **Not affiliated with or endorsed by the NHSBSA.** The sample documents are
> genuine public NHSBSA guidance included only to make the demo realistic; see
> [`data/guidance/README.md`](data/guidance/README.md).

---

## Why this project

The value of an assistant like this is in giving **trusted, current, citable**
answers from official documents and not in a language model's general knowledge.
Retrieval Augmented Generation (RAG) is the pattern that delivers exactly that,
and grounding every answer in retrieved source text is the single biggest
safeguard against a model inventing information people might act on. 

---

## What is RAG, in one paragraph?

A language model on its own only knows what it was trained on, and it will
hallucinate if asked about something it does not know. RAG fixes
that: before the model answers, we **retrieve** the most relevant passages from
a trusted document set and hand them to the model, instructing it to answer
**only** from those passages. The result is grounded, checkable, and far less
likely to invent things.

---

## How it works

```
  STEP 1 — INGESTION (run once)              STEP 2 — ANSWERING (every question)
  
    PDFs                                     Your question                  
      ↓  load                                 ↓  embed the question         
    pages of text                            find the closest chunks         
      ↓  chunk (~1000 chars)                   ↓  (FAISS similarity search)  
    overlapping passages                     paste them into a strict prompt
      ↓  embed (MiniLM)                        ↓                             
    vectors (lists of numbers)               local model writes the answer   
      ↓  store                                 ↓  using ONLY those passages  
    FAISS vector index  ──────────────────▶  answer + sources shown          
```

**The jargon, translated:**

| Term | Plain meaning |
|---|---|
| **Embedding** | Turning text into a list of numbers that captures its *meaning*, so similar ideas end up close together. |
| **Vector database (FAISS)** | A store of those number-lists that finds the closest matches to a query in milliseconds. |
| **Chunking** | Cutting long documents into small, overlapping pieces so retrieval is precise. |
| **Retrieval** | Fetching the few most relevant chunks for a question. |
| **Prompt engineering** | Carefully wording the model's instructions — here, "answer only from these passages, and admit it if the answer isn't there." |
| **LangChain** | The library that wires these pieces together. |
| **RAG** | The whole loop: retrieve relevant text, then generate an answer grounded in it. |

---

## Project structure

```
nhs-rag-assistant/
├── config.py                 # all settings, with plain-English comments
├── requirements.txt          # the libraries to install
├── LICENSE                   # MIT
├── data/guidance/            # source PDFs (real public NHSBSA guidance)
├── ingest/
│   └── build_index.py        # STEP 1: builds the searchable index
├── app/
│   ├── rag_engine.py         # the shared RAG engine (retrieve + generate)
│   ├── ask.py                # STEP 2a: command-line interface
│   └── streamlit_app.py      # STEP 2b: web interface
└── vectorstore/              # the saved index (generated locally)
```

---

## Setup

**1. Install Python libraries** (Windows PowerShell shown; use the equivalent on Mac/Linux)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**2. (Recommended) Install the free local model — [Ollama](https://ollama.com)**

```powershell
ollama pull llama3.2
```

Ollama runs quietly in the background at `http://localhost:11434`.

> **No Ollama?** The app still runs — it shows the relevant source passages
> instead of a written answer, and never crashes if the model is unavailable.

---

## Running it

```powershell
# Build the index (re-run whenever the documents change)
python ingest\build_index.py

# Web interface (best for demos)
streamlit run app\streamlit_app.py

# Or the command line
python app\ask.py "How much does an HRT prescription prepayment certificate cost?"
```

---

## Design choices worth noting

- **Grounded and honest.** The assistant answers only from the source guidance
  and explicitly says when an answer is not present without any guess. This
  behaviour comes straight from the prompt in `app/rag_engine.py`.
- **Transparent.** Every answer shows its source document and page, so any
  output can be checked and challenged.
- **Private by design.** All processing is on-device; no data leaves the machine.
- **Robust.** If the local model is unavailable, it degrades gracefully to
  retrieval-only rather than failing.
- **Clean separation.** Configuration, ingestion, the RAG engine, and the
  interfaces are cleanly separated so each part is easy to test and change.

---

## Skills demonstrated

RAG architecture · LangChain orchestration · embeddings & semantic search ·
FAISS vector store (same idea as Pinecone/Milvus, run locally) · prompt
engineering · responsible-AI design (grounding, citations, privacy) · clean,
testable Python structure.

See the [design & governance note](NHS_RAG_Assistant_Design_Note.pdf) for how
this prototype would scale to production on the cloud (Docker, MLflow, CI/CD,
managed vector store) with responsible-AI governance aligned to ISO/IEC 42001.

---

## Licence

MIT — see [LICENSE](LICENSE).
