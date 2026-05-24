import json
import urllib.parse
import urllib.request
from typing import Any, Optional

from langchain.tools import tool

RAG_RETRIEVER: Optional[Any] = None


def set_retriever(retriever: Any) -> None:
    """Configura el retriever FAISS que usarán las herramientas de consulta."""
    global RAG_RETRIEVER
    RAG_RETRIEVER = retriever


def build_tools() -> list:
    """Construye la lista de herramientas disponibles para el agente."""
    return [
        retrieve_manuals,
        search_wikipedia,
        diagnose_symptoms,
        create_work_order,
        recommend_production,
    ]


def _format_documents(documents: list) -> str:
    """Formatea los fragmentos recuperados para ser legibles por el agente."""
    if not documents:
        return ""
    formatted = []
    for doc in documents:
        source = getattr(doc, "metadata", {}).get("source", "sin fuente")
        formatted.append(f"[Fuente: {source}]\n{doc.page_content}")
    return "\n\n".join(formatted)


@tool("retrieve_manuals", return_direct=True)
def retrieve_manuals(query: str) -> str:
    """Recupera información técnica relevante de los manuales y datos indexados en FAISS."""
    if RAG_RETRIEVER is None:
        return "El motor de recuperación no está inicializado."
    documents = RAG_RETRIEVER.get_relevant_documents(query)
    if not documents:
        return "No se encontró información relevante en los manuales o fuentes internas."
    return _format_documents(documents)


@tool("wikipedia_search", return_direct=True)
def search_wikipedia(query: str) -> str:
    """Consulta la API pública de Wikipedia y devuelve un resumen breve del término indicado."""
    if not query.strip():
        return "La consulta para Wikipedia está vacía."
    search_term = urllib.parse.quote(query)
    endpoint = (
        "https://es.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=true"
        f"&explaintext=true&redirects=1&titles={search_term}"
    )
    try:
        with urllib.request.urlopen(endpoint, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        pages = payload.get("query", {}).get("pages", {})
        if not pages:
            return "No se encontró información en Wikipedia para esa consulta."
        page = next(iter(pages.values()))
        extract = page.get("extract", "")
        if not extract:
            return "Wikipedia no devolvió un resumen útil para esa consulta."
        return f"Resumen Wikipedia:\n{extract}"
    except Exception as exc:
        return f"Error al consultar Wikipedia: {exc}"


@tool("diagnose_symptoms", return_direct=True)
def diagnose_symptoms(question: str) -> str:
    """Genera un diagnóstico técnico preliminar basado en síntomas de impresoras Canon."""
    lower = question.lower()
    findings = []

    if any(token in lower for token in ["líneas", "rayas", "strip", "bandas"]):
        findings.append("Posible cabezal sucio o desalineado; revise limpieza de cabezales y realice prueba de inyectores.")
    if any(token in lower for token in ["negro", "color negro", "impresión negra", "cartucho negro"]):
        findings.append("Posible bloqueo parcial en el negro o baja tinta; haga limpieza profunda del cabezal y verifique el nivel de tinta.")
    if any(token in lower for token in ["blanco", "sin imprimir", "no imprime"]):
        findings.append("Podría haber un cabezal obstruido o un problema de alimentación de tinta; ejecute diagnóstico de inyectores y reemplazo de cartuchos si es necesario.")
    if any(token in lower for token in ["calidad", "manchado", "borroso", "descolorido"]):
        findings.append("Verifique el tipo de papel, la configuración de calidad de impresión y realice una alineación de cabezales.")
    if any(token in lower for token in ["ruido", "golpeteo", "atasco", "jam"]):
        findings.append("Revise el camino del papel y el alimentador; limpie sensores y retire restos de papel.")

    if not findings:
        return "No se detectan síntomas identificables automáticamente; utilice la recuperación de manuales o Wikipedia para un análisis más preciso."
    return "Diagnóstico rápido:\n- " + "\n- ".join(findings)


@tool("create_work_order", return_direct=True)
def create_work_order(question: str) -> str:
    """Genera una orden de trabajo técnica con prioridad y estado preliminar."""
    lower = question.lower()
    if any(term in lower for term in ["urgente", "crítico", "inmediato"]):
        priority = "Urgente"
    elif any(term in lower for term in ["alta prioridad", "importante", "recurrente"]):
        priority = "Alta"
    else:
        priority = "Normal"
    order_id = abs(hash(question)) % 10000
    return (
        f"Orden de trabajo creada:\nID: {order_id}\nPrioridad: {priority}\nSolicitud: {question}\nEstado: Pendiente"
    )


@tool("recommend_production", return_direct=True)
def recommend_production(question: str) -> str:
    """Recomienda el equipo y materiales más apropiados para una solicitud de impresión."""
    lower = question.lower()
    if any(token in lower for token in ["gigantografía", "gran formato", "mural", "lonas"]):
        equipo = "Plotter de gran formato"
        consejo = "Use materiales adecuados para gigantografías y verifique el ajuste de impresión a escala."
    elif any(token in lower for token in ["volumen alto", "producción masiva", "folletos", "documentos internos"]):
        equipo = "Impresora láser industrial"
        consejo = "Optimice la cola de producción para trabajos de alto volumen y priorice hojas preimpresas si es posible."
    else:
        equipo = "Canon iX6810"
        consejo = "Para A3 color o trabajos fotográficos, use papel premium y verifique el perfil de color."

    return (
        f"Recomendación de producción:\nEquipo: {equipo}\nConsejo: {consejo}\nResumen del pedido: {question}"
    )
