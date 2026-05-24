import os
from typing import Any

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from agents import ConversationBufferWindowMemory, RAGAgent
from tools import build_tools, set_retriever

INDEX_DIR = "index_canon"
MODEL_NAME = "gpt-4o"
EMBEDDINGS_MODEL = "text-embedding-3-small"


def _get_env_var(name: str) -> str:
    """Obtiene una variable de entorno obligatoria para instanciar el agente y los embeddings."""
    try:
        return os.environ[name]
    except KeyError as exc:
        raise EnvironmentError(f"Variable de entorno obligatoria no definida: {name}") from exc


def build_llm() -> ChatOpenAI:
    """Construye el modelo de lenguaje con configuración estricta y temperatura fija."""
    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=_get_env_var("GITHUB_TOKEN"),
        openai_api_base=_get_env_var("OPENAI_API_BASE"),
        temperature=0,
    )


def load_vector_db(index_dir: str = INDEX_DIR) -> FAISS:
    """Carga el índice FAISS local que contiene los fragmentos de documentos.

    Si el índice no existe, el usuario debe ejecutar primero `python ingesta.py`.
    """
    embeddings = OpenAIEmbeddings(
        model=EMBEDDINGS_MODEL,
        openai_api_key=_get_env_var("GITHUB_TOKEN"),
        openai_api_base=_get_env_var("OPENAI_API_BASE"),
    )
    try:
        return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
    except Exception as exc:
        raise RuntimeError(
            "No se encontró el índice FAISS local. Ejecuta primero: python ingesta.py"
        ) from exc


def build_agent_executor() -> RAGAgent:
    """Construye el agente RAG con las herramientas, el retriever y la memoria con ventana."""
    vector_db = load_vector_db()
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    set_retriever(retriever)

    tools = build_tools()
    memory = ConversationBufferWindowMemory(k=5)
    llm = build_llm()

    system_prompt = (
        "Eres un asistente técnico de impresión especializado en Canon iX6810. "
        "Sigue el patrón Thought -> Action -> Observation -> Final Answer. "
        "Responde sólo en base a las herramientas y la información recuperada. "
        "Si no hay evidencia suficiente, admite desconocimiento explícitamente."
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        debug=True,
    )
    return RAGAgent(agent, memory)
