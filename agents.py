from typing import Any, Dict, List


class ConversationBufferWindowMemory:
    """Memoria deslizante que preserva solo las interacciones recientes."""

    def __init__(self, k: int = 5) -> None:
        self.k = k
        self.messages: List[Dict[str, str]] = []

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})
        self._truncate()

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})
        self._truncate()

    def _truncate(self) -> None:
        if len(self.messages) > self.k * 2:
            self.messages = self.messages[- self.k * 2 :]

    def summary(self) -> str:
        if not self.messages:
            return "No hay historial de conversación aún."
        formatted = [f"{message['role'].title()}: {message['content']}" for message in self.messages]
        return "\n\n".join(formatted)


class RAGAgent:
    """Agente que orquesta el LLM, herramientas y memoria para consultas técnicas."""

    def __init__(self, agent: Any, memory: ConversationBufferWindowMemory) -> None:
        self.agent = agent
        self.memory = memory

    def ask(self, question: str) -> str:
        if not question.strip():
            return "No se ha indicado ninguna pregunta."

        self.memory.add_user_message(question)
        full_prompt = self._build_prompt(question)

        result = self.agent.invoke({"input": full_prompt})
        if isinstance(result, dict):
            response = result.get("output", result.get("output_text", str(result)))
        else:
            response = str(result)

        self.memory.add_assistant_message(response)
        return response

    def _build_prompt(self, question: str) -> str:
        history = self.memory.summary()
        if history == "No hay historial de conversación aún.":
            return f"Pregunta:\n{question}"
        return f"Historial reciente:\n{history}\n\nPregunta:\n{question}"
