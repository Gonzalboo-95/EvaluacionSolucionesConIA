import os
from dotenv import load_dotenv

from .env_utils import get_openai_api_key
from .tasks import build_agent_executor


def _load_environment() -> None:
    # Usamos override=True para asegurar que tome los datos frescos de tu archivo .env
    load_dotenv(override=True)
    
    get_openai_api_key()


def run_cli() -> None:
    try:
        _load_environment()
        rag_agent = build_agent_executor()
    except Exception as exc:
        print(f"No se pudo iniciar el asistente: {exc}")
        return

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
            texto_limpio = str(respuesta)

            if isinstance(respuesta, dict):
                messages = respuesta.get("messages") or []
                if messages:
                    last_message = messages[-1]
                    if hasattr(last_message, "content"):
                        content = getattr(last_message, "content", "")
                        if isinstance(content, list):
                            texto_limpio = "\n".join(str(item) for item in content)
                        else:
                            texto_limpio = str(content)

            print(f"\nAsistente: {texto_limpio}")
        except Exception as exc:
            print(f"\nError técnico: {exc}")


if __name__ == "__main__":
    run_cli()