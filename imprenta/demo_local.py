"""Demo local reproducible con arquitectura multi-agente (sin API externa)."""

from types import SimpleNamespace

from imprenta.agents import ConversationBufferWindowMemory, RAGAgent
from imprenta.coordinator import CoordinatorAgent

examples = [
    "La Canon IX6810 imprime con líneas en las hojas, ¿qué puede ser?",
    "Necesito una orden técnica urgente porque el equipo se queda sin tinta y no responde.",
    "Tengo un trabajo A3 color, ¿qué impresora y material debo usar?",
    "El operario dice que hay un ruido extraño y varios atascos de papel seguidos.",
]


class DummyAgent:
    """Agente de prueba que emula respuestas razonadas sin depender de un LLM externo."""

    def invoke(self, payload):
        msgs = payload.get("messages") or []
        last = msgs[-1].content if msgs else ""
        if "## Requerimiento informacional" in last:
            text = last.split("## Requerimiento informacional")[-1].strip().lower()
        else:
            text = last.lower()
        if "lineas" in text or "líneas" in text:
            resp = (
                "Diagnóstico rápido: Las líneas en la impresión suelen indicar boquillas obstruidas o "
                "problemas de alineación del cabezal.\nAcción: realizar una limpieza de inyectores (múltiple), imprimir "
                "una página de prueba y verificar el patrón de alineación.\nSi persiste, programar revisión del cabezal."
            )
        elif "tinta" in text or "urgente" in text:
            resp = (
                "Orden de trabajo creada (prioridad URGENTE).\n"
                "Diagnóstico: nivel de tinta crítico o sensor defectuoso.\n"
                "Acción: comprobar sensores, reemplazar cartuchos y ejecutar ciclo de inicialización."
            )
        elif "a3" in text:
            resp = (
                "Recomendación de producción:\nEquipo: Canon iX6810\n"
                "Material: papel fotográfico premium 260 g/m²\n"
                "Consejo: usar perfiles ICC apropiados para A3 color."
            )
        elif "atascos" in text or "ruido" in text:
            resp = (
                "Diagnóstico rápido: desgaste de rodillos o guía de alimentación.\n"
                "Acción: inspeccionar rodillos, limpiar residuos de papel y lubricar guías."
            )
        else:
            resp = "Respuesta de prueba: consulta procesada por el coordinador multi-agente."

        return {"messages": [SimpleNamespace(content=resp)]}


def main() -> None:
    memory = ConversationBufferWindowMemory(k=5)
    rag = RAGAgent(DummyAgent(), memory)
    coordinator = CoordinatorAgent(rag)

    print("Demo local reproducible - Arquitectura multi-agente (sin API)")
    print("=" * 65)
    for q in examples:
        print(f"\nPregunta: {q}")
        resp = coordinator.ask(q)
        print(f"Respuesta:\n{resp}")
        print(f"\n{coordinator.get_orchestration_summary()}")


if __name__ == "__main__":
    main()
