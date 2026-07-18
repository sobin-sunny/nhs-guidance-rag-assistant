"""
STEP 2 OF RAG: RETRIEVAL + GENERATION  (the part that answers questions)
========================================================================

This is the shared "engine" used by both the command line and the web app.

When a user asks a question, it does three things - the classic RAG loop:

    1. RETRIEVE  - find the chunks most relevant to the question (from FAISS)
    2. AUGMENT   - paste those chunks into a carefully written prompt
    3. GENERATE  - ask the local language model to answer USING ONLY those chunks

The prompt is deliberately strict: the model must answer only from the supplied
guidance and must say so honestly when the answer is not there. That is the
single most important safeguard against an AI "making things up" - which matters
enormously when the subject is public guidance people may act on.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

from langchain_huggingface import HuggingFaceEmbeddings  # noqa: E402
from langchain_community.vectorstores import FAISS       # noqa: E402


# This is our "prompt engineering". Every instruction here is a deliberate
# design choice you can defend in an interview:
#   - "Use ONLY the context"        -> stops the model inventing answers
#   - "If not in the context, say so"-> honest, safe behaviour
#   - "Quote the source"            -> makes every answer auditable
PROMPT_TEMPLATE = """You are a careful assistant that answers questions about \
NHS guidance documents. Follow these rules exactly:

1. Answer using ONLY the guidance passages provided below.
2. If the passages do not contain the answer, reply: "I could not find this in \
the provided guidance." Do not guess or use outside knowledge.
3. Keep the answer clear and plain. Where useful, mention which document the \
information came from.

Guidance passages:
---------------------
{context}
---------------------

Question: {question}

Answer:"""


class RagEngine:
    """Loads the search index once, then answers many questions."""

    def __init__(self):
        self._embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        self._store = self._load_store()
        self._llm = self._try_load_llm()

    def _load_store(self):
        index_file = config.VECTORSTORE_DIR / "index.faiss"
        if not index_file.exists():
            raise FileNotFoundError(
                "No search index found. Build it first with:\n"
                "   python ingest/build_index.py"
            )
        # allow_dangerous_deserialization is safe here: WE created this file.
        return FAISS.load_local(
            str(config.VECTORSTORE_DIR),
            self._embeddings,
            allow_dangerous_deserialization=True,
        )

    def _try_load_llm(self):
        """Connect to the local Ollama model if it is running.

        If it is not running, we return None and fall back to showing the raw
        retrieved passages. The app never crashes just because the LLM is off.
        """
        try:
            from langchain_ollama import OllamaLLM
            llm = OllamaLLM(
                model=config.OLLAMA_MODEL,
                base_url=config.OLLAMA_BASE_URL,
                temperature=0,  # 0 = factual and repeatable, not creative
            )
            llm.invoke("ok")  # quick ping to confirm it responds
            return llm
        except Exception:
            return None

    @property
    def llm_available(self) -> bool:
        return self._llm is not None

    def retrieve(self, question: str):
        """STAGE 1 - find the most relevant chunks for this question."""
        return self._store.similarity_search(question, k=config.TOP_K)

    def answer(self, question: str) -> dict:
        """Full RAG loop. Returns the answer plus its supporting sources."""
        sources = self.retrieve(question)
        context = "\n\n".join(
            f"[{d.metadata.get('source_file', '?')}, "
            f"page {d.metadata.get('page', '?')}]\n{d.page_content}"
            for d in sources
        )

        if self._llm is None:
            # Search-only fallback - still genuinely useful, and honest.
            text = ("The local service is not running. The most relevant "
                    "passages from the guidance are shown below. Start the "
                    "local service to receive a full written answer.")
            return {"answer": text, "sources": sources, "used_llm": False}

        prompt = PROMPT_TEMPLATE.format(context=context, question=question)
        text = self._llm.invoke(prompt)
        return {"answer": text.strip(), "sources": sources, "used_llm": True}
