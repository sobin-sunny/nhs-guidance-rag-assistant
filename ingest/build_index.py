"""
STEP 1 OF RAG: INGESTION  (run this once, whenever your documents change)
=========================================================================

This script turns a folder of PDFs into a searchable "vector store".

Think of it like building the index at the back of a textbook, except instead
of matching words, it matches *meaning*. Later, when you ask a question, we can
instantly pull out the handful of passages most relevant to it.

The four stages below are the whole of RAG ingestion:
    1. LOAD    - read the raw text out of each PDF
    2. CHUNK   - cut that text into bite-sized, overlapping pieces
    3. EMBED   - turn each piece into a vector (a list of numbers = its meaning)
    4. STORE   - save all those vectors in a FAISS index we can search fast

Run it with:   python ingest/build_index.py
"""

import sys
from pathlib import Path

# Make sure we can import config.py from the project root
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

from langchain_community.document_loaders import PyPDFLoader          # noqa: E402
from langchain_text_splitters import RecursiveCharacterTextSplitter  # noqa: E402
from langchain_huggingface import HuggingFaceEmbeddings              # noqa: E402
from langchain_community.vectorstores import FAISS                   # noqa: E402


def load_documents():
    """STAGE 1 - LOAD: read every PDF in the guidance folder into memory."""
    pdf_paths = sorted(config.GUIDANCE_DIR.glob("*.pdf"))
    if not pdf_paths:
        print(f"No PDFs found in {config.GUIDANCE_DIR}.")
        print("Drop some NHS guidance PDFs in there and run this again.")
        sys.exit(1)

    docs = []
    for path in pdf_paths:
        print(f"  Loading {path.name} ...")
        # PyPDFLoader gives us one 'document' per page, and it records the
        # source filename and page number in each page's metadata. We keep that
        # metadata because it is what lets us show citations later.
        pages = PyPDFLoader(str(path)).load()
        for page in pages:
            page.metadata["source_file"] = path.name
        docs.extend(pages)
    print(f"  Loaded {len(docs)} pages from {len(pdf_paths)} PDF(s).")
    return docs


def chunk_documents(docs):
    """STAGE 2 - CHUNK: split pages into smaller overlapping passages.

    Why overlap? So a sentence that happens to fall on a chunk boundary is not
    cut in half and lost. The overlap means important context appears in two
    neighbouring chunks, which makes retrieval more reliable.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        # It tries to split on paragraph breaks first, then sentences, then
        # words - so chunks stay as readable and self-contained as possible.
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"  Split into {len(chunks)} chunks "
          f"(~{config.CHUNK_SIZE} chars each, {config.CHUNK_OVERLAP} overlap).")
    return chunks


def build_vectorstore(chunks):
    """STAGES 3 & 4 - EMBED + STORE.

    The embedding model reads each chunk and outputs a vector. FAISS (a library
    from Meta for fast similarity search) stores those vectors so that, given a
    new question vector, it can find the closest chunks in milliseconds - even
    across millions of them.
    """
    print(f"  Loading embedding model: {config.EMBEDDING_MODEL}")
    print("  (first run downloads it once, then it works fully offline)")
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)

    print("  Embedding chunks and building the FAISS index ...")
    store = FAISS.from_documents(chunks, embeddings)

    config.VECTORSTORE_DIR.mkdir(exist_ok=True)
    store.save_local(str(config.VECTORSTORE_DIR))
    print(f"  Saved searchable index to {config.VECTORSTORE_DIR}")


def main():
    print("\nBuilding the NHS guidance search index")
    print("=" * 45)
    docs = load_documents()
    chunks = chunk_documents(docs)
    build_vectorstore(chunks)
    print("\nDone. You can now ask questions with:")
    print("   streamlit run app/streamlit_app.py     (web interface)")
    print("   python app/ask.py \"your question\"      (command line)\n")


if __name__ == "__main__":
    main()
