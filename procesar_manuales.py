import os
import time
import glob  # Importante para leer múltiples archivos
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def es_pdf_valido(ruta):
    try:
        with open(ruta, "rb") as f:
            header = f.read(5)
        return header == b"%PDF-"
    except Exception:
        return False


def preparar_base_datos():
    manuales = glob.glob("data/*.pdf")
    externos = glob.glob("external_sources/**/*.*", recursive=True)
    documentos_totales = []

    print(f"--- 1. Leyendo {len(manuales)} manuales internos en carpeta 'data' ---")
    for archivo in manuales:
        if not es_pdf_valido(archivo):
            print(f"Archivo inválido o no es un PDF correcto, se omite: {archivo}")
            continue
        try:
            loader = PyPDFLoader(archivo)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = archivo
            documentos_totales.extend(docs)
            print(f"Cargado interno: {archivo}")
        except Exception as e:
            print(f"Error al leer {archivo}: {e}")

    print(f"--- 2. Leyendo {len(externos)} fuentes externas en carpeta 'external_sources' ---")
    for archivo in externos:
        try:
            loader = TextLoader(archivo, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = archivo
            documentos_totales.extend(docs)
            print(f"Cargado externo: {archivo}")
        except Exception as e:
            print(f"Error al leer {archivo}: {e}")

    if not documentos_totales:
        print("¡Error! No se encontraron documentos en 'data' ni en 'external_sources'.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    trozos = text_splitter.split_documents(documentos_totales)
    print(f"\nDocumentos divididos en {len(trozos)} fragmentos.")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.environ.get("GITHUB_TOKEN"),
        openai_api_base="https://models.inference.ai.azure.com"
    )
    
    lote_size = 50
    vector_db = None

    for i in range(0, len(trozos), lote_size):
        sub_lote = trozos[i:i + lote_size]
        print(f"Procesando fragmentos del {i} al {min(i + lote_size, len(trozos))}...")
        
        try:
            if vector_db is None:
                vector_db = FAISS.from_documents(sub_lote, embeddings)
            else:
                vector_db.add_documents(sub_lote)
            time.sleep(1)
        except Exception as e:
            print(f"Error en el lote {i}: {e}")
            time.sleep(5)

    if vector_db:
        vector_db.save_local("index_canon")
        print(f"\n¡EXITO! Base de datos con {len(documentos_totales)} documentos internos y externos guardada.")

if __name__ == "__main__":
    preparar_base_datos()