import glob
import os
import time
from typing import Any, List

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

INDEX_DIR = "index_canon"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
EMBEDDINGS_MODEL = "text-embedding-3-small"


def _validate_pdf(path: str) -> bool:
    """Verifica que el archivo tenga el encabezado PDF correcto."""
    try:
        with open(path, "rb") as file:
            return file.read(5) == b"%PDF-"
    except OSError:
        return False


def _load_documents() -> List[Any]:
    """Carga documentos internos y externos con su metadata de fuente."""
    documents: List[Any] = []
    internal_files = glob.glob("data/*.pdf")
    external_files = glob.glob("external_sources/**/*.*", recursive=True)

    print(f"Cargando {len(internal_files)} manuales internos y {len(external_files)} fuentes externas...")

    for path in internal_files:
        if not _validate_pdf(path):
            print(f"Archivo inválido omitido: {path}")
            continue
        loader = PyPDFLoader(path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = path
        documents.extend(docs)
        print(f"Manual cargado: {path}")

    for path in external_files:
        try:
            loader = TextLoader(path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = path
            documents.extend(docs)
            print(f"Fuente externa cargada: {path}")
        except Exception as exc:
            print(f"No se pudo cargar fuente externa {path}: {exc}")

    return documents


def _build_embeddings() -> OpenAIEmbeddings:
    """Crea el modelo de embeddings usando la clave obligatoria de entorno."""
    api_key = os.environ["GITHUB_TOKEN"]
    api_base = os.environ["OPENAI_API_BASE"]
    return OpenAIEmbeddings(
        model=EMBEDDINGS_MODEL,
        openai_api_key=api_key,
        openai_api_base=api_base,
    )


def build_faiss_index(index_dir: str = INDEX_DIR) -> None:
    """Procesa los manuales y fuentes externas y persiste el índice FAISS localmente."""
    documents = _load_documents()
    if not documents:
        raise RuntimeError("No se encontraron documentos para indexar. Agrega datos en data/ o external_sources/.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Documentos divididos en {len(chunks)} fragmentos.")

    embeddings = _build_embeddings()
    vector_db = None
    batch_size = 50

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        print(f"Procesando lote {start} a {min(start + batch_size, len(chunks))}...")
        if vector_db is None:
            vector_db = FAISS.from_documents(batch, embeddings)
        else:
            vector_db.add_documents(batch)
        time.sleep(0.5)

    if vector_db is None:
        raise RuntimeError("No se pudo crear el índice FAISS.")

    vector_db.save_local(index_dir)
    print(f"Índice FAISS guardado en {index_dir}.")


if __name__ == "__main__":
    build_faiss_index()