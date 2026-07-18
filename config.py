"""
Central settings for the NHS Guidance RAG Assistant.

Everything you might want to tweak lives here, so you never have to hunt
through the code. Each setting has a plain-English comment explaining what it
does and why the value was chosen.
"""

from pathlib import Path

# --- Folders -----------------------------------------------------------------
ROOT = Path(__file__).parent
GUIDANCE_DIR = ROOT / "data" / "guidance"      # put your source PDFs here
VECTORSTORE_DIR = ROOT / "vectorstore"          # the searchable index is saved here

# --- Chunking ----------------------------------------------------------------
# A long PDF is split into smaller "chunks" before it is searched. Too big and
# the model gets waffle; too small and it loses context. ~1000 characters with
# a 150-character overlap is a well-tested middle ground for guidance documents.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# --- Embeddings --------------------------------------------------------------
# The embedding model turns text into numbers ("vectors") so we can find
# passages by meaning, not just keywords. This one is small, free, runs offline,
# and is a solid default. It downloads once (~90 MB) then works with no internet.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# --- Retrieval ---------------------------------------------------------------
# How many of the most relevant chunks to feed the model for each question.
TOP_K = 4

# --- Language model (local + free via Ollama) --------------------------------
# Ollama runs an open model on your own computer. Nothing leaves the machine,
# which is the right default for anything touching sensitive data.
# Install Ollama from https://ollama.com then run:  ollama pull llama3.2
OLLAMA_MODEL = "llama3.2"
OLLAMA_BASE_URL = "http://localhost:11434"

# If Ollama is not running, the app still works in "retrieval-only" mode:
# it shows you the exact passages that answer the question, just without the
# model writing them up into prose. Handy as a fallback during a live demo.
