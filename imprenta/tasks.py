import os
from typing import Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from .agents import ConversationBufferWindowMemory, RAGAgent
from .tools import build_tools, set_retriever

try:
    from langchain.agents import create_agent
except ImportError:
    from langchain.agents import create_react_agent as create_agent

INDEX_DIR = "index_canon"
MODEL_NAME = "gpt-4o"
EMBEDDINGS_MODEL = "text-embedding-3-small"


def _get_env_var(name: str) -> str:
    #Obtiene una variable de entorno obligatoria para instanciar el agente y los embeddings.
    try:
        return os.environ[name]
    except KeyError as exc:
        raise EnvironmentError(f"Variable de entorno obligatoria no definida: {name}") from exc


def _get_openai_api_key() -> str:
    #Retorna la clave de OpenAI desde OPENAI_API_KEY o GITHUB_TOKEN.
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GITHUB_TOKEN")
    if not api_key:
        raise EnvironmentError(
            "Falta la variable de entorno obligatoria OPENAI_API_KEY o GITHUB_TOKEN."
        )
    return api_key


def _get_openai_api_base() -> str | None:
    #Retorna la URL base si existe. Se vuelve opcional para no romper OpenAI nativo.
    return os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")


def build_llm() -> ChatOpenAI:
    #Construye el modelo de lenguaje adaptándose dinámicamente al proveedor.
    api_key = _get_openai_api_key()
    api_base = _get_openai_api_base()
    
    kwargs = {
        "model": MODEL_NAME,
        "api_key": api_key,
        "temperature": 0,
    }
    
    if api_base:
        kwargs["base_url"] = api_base
        
    return ChatOpenAI(**kwargs)


def load_vector_db(index_dir: str = INDEX_DIR) -> FAISS:
    #Carga el índice FAISS local que contiene los fragmentos de documentos.
    
    api_key = _get_openai_api_key()
    api_base = _get_openai_api_base()
    
    kwargs = {
        "model": EMBEDDINGS_MODEL,
        "api_key": api_key,
    }
    if api_base:
        kwargs["base_url"] = api_base
        
    embeddings = OpenAIEmbeddings(**kwargs)
    
    try:
        return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
    except Exception as exc:
        raise RuntimeError(
            "No se encontró el índice FAISS local. Ejecuta primero: python ingesta.py"
        ) from exc


def build_agent_executor() -> RAGAgent:
    #Construye el agente RAG con las herramientas, el retriever y la memoria con ventana.
    vector_db = load_vector_db()
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    set_retriever(retriever)

    tools = build_tools()
    memory = ConversationBufferWindowMemory(k=5)
    llm = build_llm()

    system_prompt = (
        "Eres un asistente técnico de impresión especializado en Canon iX6810. "
        "Usa las herramientas disponibles para consultar manuales, diagnosticar síntomas, crear órdenes de trabajo y recomendar producción. "
        "Sigue el patrón Thought -> Action -> Observation -> Final Answer. "
        "Responde de forma precisa, clara y solo con base en la evidencia disponible. "
        "Si no hay información suficiente, admite que no está seguro y pide más datos."
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        debug=False,
        name="CanonRAGAgent",
    )
    return RAGAgent(agent, memory)