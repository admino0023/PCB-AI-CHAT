"""
rag_engine.py
-------------
Retrieval-Augmented Generation layer of the PCB AI Assistant.

Responsibility:
    Build (and cache) a FAISS vector store from the electronics
    knowledge base in `docs/` (PCB inspection manuals, soldering
    guides, IPC standards, datasheets), then answer a defect query
    by retrieving relevant chunks and asking a local LLM to explain
    cause / repair / precautions grounded in that context.

Design notes:
    - Uses the same stack as the existing ESP32 chatbot project:
      LangChain + HuggingFace embeddings + FAISS + Ollama LLM.
    - Vector store build is expensive (embeddings for every doc chunk),
      so it's wrapped so it only runs once per process
      (see `get_or_build_vectorstore`). In a Streamlit app, wrap the
      call site with `@st.cache_resource` instead of the flag below.
"""

from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

DOCS_DIR = "docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama3"  # any text model you've pulled with `ollama pull llama3`

RAG_PROMPT = ChatPromptTemplate.from_template(
    """You are an electronics repair and quality-control assistant.

Use ONLY the context below to answer. If the context doesn't contain
the answer, say the manual doesn't cover it and recommend manual
inspection — do not make up standards or numbers.

Context:
{context}

Defect / Question:
{question}

Answer with:
- Cause
- Repair Steps
- Inspection Method
- Precautions
"""
)

_vectorstore_cache: Optional[FAISS] = None


def _format_docs(docs) -> str:
    return "\n\n".join(d.page_content for d in docs)


def build_vectorstore(docs_dir: str = DOCS_DIR) -> FAISS:
    """
    Load every .txt file in docs_dir, chunk it, embed it, and build a
    FAISS index. Re-run this whenever docs/ changes.

    Note: to also ingest PDFs (e.g. real IPC standards, datasheets),
    swap TextLoader for PyPDFLoader per-file, or use
    `langchain_community.document_loaders.PyPDFDirectoryLoader`.
    """
    docs_path = Path(docs_dir)
    if not docs_path.exists() or not any(docs_path.glob("*.txt")):
        raise FileNotFoundError(
            f"No .txt files found in '{docs_dir}/'. Add your PCB manuals, "
            "soldering guides, and IPC notes there first."
        )

    loader = DirectoryLoader(docs_dir, glob="*.txt", loader_cls=TextLoader,
                              loader_kwargs={"encoding": "utf-8"})
    raw_docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(raw_docs)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return FAISS.from_documents(chunks, embeddings)


def get_or_build_vectorstore(docs_dir: str = DOCS_DIR) -> FAISS:
    """Process-level cache so the vector store is built only once."""
    global _vectorstore_cache
    if _vectorstore_cache is None:
        _vectorstore_cache = build_vectorstore(docs_dir)
    return _vectorstore_cache


def query_knowledge_base(question: str, k: int = 3, model: str = LLM_MODEL) -> str:
    """
    Retrieve the top-k relevant chunks for `question` and ask the LLM
    to produce a grounded explanation (cause / repair / inspection /
    precautions).

    Args:
        question: a defect name or free-text question,
                  e.g. "Missing Resistor" or "What is a cold solder joint?"
        k: number of chunks to retrieve.
        model: Ollama text model name.

    Returns:
        The LLM's answer text.
    """
    vectorstore = get_or_build_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    llm = Ollama(model=model)

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain.invoke(question)


if __name__ == "__main__":
    # Quick manual test:
    #   python rag_engine.py "Missing Resistor"
    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "What is a solder bridge?"
    print(f"Query: {q}\n")
    print(query_knowledge_base(q))
