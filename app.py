import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

#Configuración del modelo
llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=os.environ.get("GITHUB_TOKEN"),
    openai_api_base="https://models.inference.ai.azure.com",
    temperature=0
)

#Cargar BD con credenciales de GitHub
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.environ.get("GITHUB_TOKEN"),
    openai_api_base="https://models.inference.ai.azure.com"
)
vector_db = FAISS.load_local("index_canon", embeddings, allow_dangerous_deserialization=True)
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

#Diseño del Prompt
template = """Eres el experto técnico de Imprenta Nueva Imagen. 
Usa la siguiente información del manual para responder la duda del operario sobre la Canon iX6810.
Si la respuesta no está en el texto, di que no tienes esa información específica.

Contexto:
{context}

Pregunta: {question}
Respuesta técnica:"""

prompt = ChatPromptTemplate.from_template(template)

#Pipeline
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("\n" + "="*45)
print("SISTEMA NUEVA IMAGEN - CHATBOT PARA CANON IX6810")
print("--- Maestro imprentero listo para consultas ---")
print("="*45)

while True:
    pregunta = input("\nImprentero: ")
    if pregunta.lower() in ["salir", "exit"]: break
    try:
        respuesta = rag_chain.invoke(pregunta)
        print(f"\nAsistente Nueva Imagen: {respuesta}")
    except Exception as e:
        print(f"\nDetalle técnico: {e}")