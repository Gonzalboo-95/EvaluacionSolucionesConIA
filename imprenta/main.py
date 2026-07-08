import os
from dotenv import load_dotenv

from .agent_monitoring import ObservableRAGAgent
from .env_utils import get_openai_api_key
from .security import append_ethical_notice, sanitize_input
from .tasks import build_agent_executor


def _load_environment() -> None:
    load_dotenv(override=True)
    get_openai_api_key()


def run_cli() -> None:
    try:
        _load_environment()
        coordinator = build_agent_executor()
        agent = ObservableRAGAgent(coordinator, enable_metrics=True)
    except Exception as exc:
        print(f"No se pudo iniciar el asistente: {exc}")
        return

    print("\n" + "=" * 55)
    print("IMPRENTA NUEVA IMAGEN - AGENTE MULTI-ESPECIALISTA CON RAG")
    print("Comandos: historial | orquestacion | metricas | salir")
    print("=" * 55)

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
            print(f"\nHistorial de conversaciones:\n{agent.memory.summary()}")
            continue
        if pregunta.lower() in ["orquestacion", "orquestación", "plan"]:
            print(f"\n{coordinator.get_orchestration_summary()}")
            continue
        if pregunta.lower() in ["metricas", "métricas", "metrics"]:
            summary = agent.get_metrics_summary()
            print(f"\nResumen de observabilidad:\n{summary}")
            continue

        validation = sanitize_input(pregunta)
        if not validation.allowed:
            print(f"\nConsulta rechazada: {validation.reason}")
            continue

        try:
            respuesta = agent.ask(validation.sanitized_query)
            respuesta = append_ethical_notice(str(respuesta))
            print(f"\nAsistente: {respuesta}")
        except Exception as exc:
            print(f"\nError técnico: {exc}")


if __name__ == "__main__":
    run_cli()
