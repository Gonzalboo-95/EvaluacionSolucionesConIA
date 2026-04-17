import os
import time
import glob # Importante para leer múltiples archivos
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def preparar_base_datos():
    # Buscamos todos los archivos PDF dentro de la carpeta 'data'
    archivos = glob.glob("data/*.pdf")
    documentos_totales = []
    
    print(f"--- 1. Leyendo {len(archivos)} manuales en carpeta 'data' ---")
    
    for archivo in archivos:
        try:
            loader = PyPDFLoader(archivo)
            documentos_totales.extend(loader.load())
            print(f"Cargado: {archivo}")
        except Exception as e:
            print(f"Error al leer {archivo}: {e}")

    if not documentos_totales:
        print("¡Error! No se encontraron PDFs en la carpeta 'data'.")
        return

    # Segmentación (Chunking) - Bajamos a 800 para que los errores sean más precisos
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    trozos = text_splitter.split_documents(documentos_totales)
    print(f"\nDocumentos divididos en {len(trozos)} fragmentos.")

    # Configuración de Embeddings
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

    # 3. Guardar
    if vector_db:
        vector_db.save_local("index_canon")
        print("\n¡EXITO! Base de datos con 68 manuales guardada.")

if __name__ == "__main__":
    preparar_base_datos()