import os
from dotenv import load_dotenv

from tasks import build_agent_executor


def _load_environment() -> None:
    load_dotenv()
    required = ["GITHUB_TOKEN", "OPENAI_API_BASE"]
    missing = [name for name in required if name not in os.environ]
    if missing:
        raise EnvironmentError(
            "Faltan variables de entorno obligatorias: " + ", ".join(missing)
        )


def run_cli() -> None:
    _load_environment()
    rag_agent = build_agent_executor()

    print("\n" + "=" * 45)
    print("SISTEMA NUEVA IMAGEN - AGENTE RAG CON MEMORIA LIMITADA")
    print("--- Usa 'historial' para ver el contexto acumulado y 'salir' para terminar ---")
    print("=" * 45)

    while True:
        try:
            pregunta = input("\nOperario: ").strip()
        except EOFError:
            print("\nSaliendo del sistema.")
            break

        if not pregunta:
            continue
        if pregunta.lower() in ["salir", "exit"]:
            break
        if pregunta.lower() in ["historial", "historia", "memoria"]:
            print(f"\nHistorial de conversaciones:\n{rag_agent.memory.summary()}")
            continue

        try:
            respuesta = rag_agent.ask(pregunta)
            print(f"\n{respuesta}")
        except Exception as exc:
            print(f"\nError técnico: {exc}")


if __name__ == "__main__":
    run_cli()