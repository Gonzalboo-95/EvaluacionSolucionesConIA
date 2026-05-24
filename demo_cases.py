from tasks import build_agent_executor

examples = [
    "La Canon IX6810 imprime con líneas en las hojas, ¿qué puede ser?",
    "Necesito una orden técnica urgente porque el equipo se queda sin tinta y no responde.",
    "Tengo un trabajo A3 color, ¿qué impresora y material debo usar?",
    "El operario dice que hay un ruido extraño y varios atascos de papel seguidos.",
]

if __name__ == "__main__":
    rag_agent = build_agent_executor()
    print("Demo de casos de uso del agente RAG")
    print("=" * 50)
    for pregunta in examples:
        print(f"\nPregunta: {pregunta}")
        try:
            respuesta = rag_agent.ask(pregunta)
            print(f"Respuesta:\n{respuesta}")
        except Exception as exc:
            print(f"Error al procesar la pregunta: {exc}")
