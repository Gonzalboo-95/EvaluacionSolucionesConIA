from types import SimpleNamespace
from .agents import ConversationBufferWindowMemory, RAGAgent

examples = [
    "La Canon IX6810 imprime con líneas en las hojas, ¿qué puede ser?",
    "Necesito una orden técnica urgente porque el equipo se queda sin tinta y no responde.",
    "Tengo un trabajo A3 color, ¿qué impresora y material debo usar?",
    "El operario dice que hay un ruido extraño y varios atascos de papel seguidos.",
]


class DummyAgent:
    #Agente de prueba que emula respuestas razonadas sin depender de un LLM externo.

    def invoke(self, payload):
        #Extraemos la última mensaje del usuario
        msgs = payload.get("messages") or []
        last = msgs[-1].content if msgs else ""
        text = last.lower()
        if "lineas" in text or "líneas" in text:
            resp = (
                "Diagnóstico rápido: Las líneas en la impresión suelen indicar boquillas obstruidas o "
                "problemas de alineación del cabezal.\nAcción: realizar una limpieza de inyectores (múltiple), imprimir "
                "una página de prueba y verificar el patrón de alineación.\nSi persiste, programar revisión del cabezal."
            )
        elif "tinta" in text:
            resp = (
                "Diagnóstico rápido: nivel de tinta crítico o sensor de tinta defectuoso.\nAcción: comprobar "
                "sensores, reemplazar cartuchos y ejecutar ciclo de inicialización.\nGenerar orden de trabajo si el equipo no responde."
            )
        elif "a3" in text:
            resp = (
                "Recomendación: Para A3 color en imprenta, Canon iX6810 es adecuada para tiradas pequeñas;\nuse "
                "papel fotográfico de alta resolución y perfiles de color ICC apropiados."
            )
        elif "atascos" in text or "ruido" in text:
            resp = (
                "Diagnóstico rápido: desgaste de rodillos o guía de alimentación.\nAcción: inspeccionar rodillos, "
                "limpiar residuos de papel y lubricar guías; si hay ruido metálico, detener y revisar componentes internos."
            )
        else:
            resp = "Respuesta de prueba: no hay suficiente contexto en el mensaje de prueba."

        #Envolvemos en el mismo formato que devuelve un LLM: lista de mensajes con 'content'
        return {"messages": [SimpleNamespace(content=resp)]}


def main() -> None:
    memory = ConversationBufferWindowMemory(k=5)
    agent = DummyAgent()
    rag = RAGAgent(agent, memory)

    print("Demo local reproducible (no requiere claves API)")
    print("=" * 60)
    for q in examples:
        print(f"\nPregunta: {q}")
        resp = rag.ask(q)
        print(f"Respuesta:\n{resp}")


if __name__ == "__main__":
    main()
 