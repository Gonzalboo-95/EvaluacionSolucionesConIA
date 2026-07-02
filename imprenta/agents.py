from typing import Any, Dict, List

from langchain_core.messages import HumanMessage


class ConversationBufferWindowMemory:
    #Memoria deslizante que preserva solo las interacciones recientes.

    def __init__(self, k: int = 5) -> None:
        self.k = k
        self.messages: List[Dict[str, str]] = []

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})
        self._truncate()

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})
        self._truncate()

    def to_human_messages(self) -> List[HumanMessage]:
        #Exporta la memoria como una lista de HumanMessage para pasar al agente.

        
        msgs: List[HumanMessage] = []
        for m in self.messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            prefix = "Usuario: " if role == "user" else "Asistente: "
            msgs.append(HumanMessage(content=f"{prefix}{content}"))
        return msgs

    def _truncate(self) -> None:
        if len(self.messages) > self.k * 2:
            self.messages = self.messages[- self.k * 2 :]

    def summary(self) -> str:
        if not self.messages:
            return "No hay historial de conversación aún."
        formatted = [f"{message['role'].title()}: {message['content']}" for message in self.messages]
        return "\n\n".join(formatted)


class RAGAgent:
    #Agente que orquesta el LLM, herramientas y memoria para consultas técnicas.

    def __init__(self, agent: Any, memory: ConversationBufferWindowMemory) -> None:
        self.agent = agent
        self.memory = memory

    def ask(self, question: str) -> str:
        if not question.strip():
            return "No se ha indicado ninguna pregunta."

        self.memory.add_user_message(question)
        # Construimos una lista de mensajes: prompt del sistema (si aplica), memoria y la pregunta actual.
        memory_msgs = self.memory.to_human_messages()
        system_msg = HumanMessage(content=self._system_instruction())
        user_msg = HumanMessage(content=question)

        # Pasamos la lista de mensajes al agente para una integración más natural con chat-based agents.
        payload = {"messages": [system_msg] + memory_msgs + [user_msg]}

        # Algunos factories esperan invocation vía invoke, otros permiten llamada directa.
        try:
            result = self.agent.invoke(payload)
        except Exception:
            result = self.agent(payload)
        response = self._extract_response(result)

        self.memory.add_assistant_message(response)
        return response

    def _build_prompt(self, question: str) -> str:
        history = self.memory.summary()
        if history == "No hay historial de conversación aún.":
            return (
                "Responde en español, de forma clara y técnica. "
                "Si puedes usar una herramienta para consultar manuales, diagnosticar o recomendar, hazlo. "
                f"Pregunta:\n{question}"
            )
        return (
            "Responde en español, de forma clara y técnica. "
            "Si puedes usar una herramienta para consultar manuales, diagnosticar o recomendar, hazlo. "
            f"Historial reciente:\n{history}\n\nPregunta:\n{question}"
        )

    def _system_instruction(self) -> str:
        #Instrucción de sistema usada en los mensajes enviados al agente.
        return (
            "Eres un asistente técnico especializado en Canon iX6810 para un entorno de imprenta. "
            "Tu tarea es resolver consultas técnicas reales, no saludar de forma genérica. "
            "Usa las herramientas disponibles para consultar manuales, diagnosticar síntomas, crear órdenes de trabajo y recomendar producción. "
            "Sigue un razonamiento breve y práctico: identifica el problema, revisa evidencia, propone una acción concreta y finaliza con una recomendación útil. "
            "Responde siempre en español, de forma precisa, clara y basada en evidencia. "
            "Si la información no es suficiente, dilo explícitamente y pide los datos faltantes."
        )

    def _extract_response(self, result: Any) -> str:
        if isinstance(result, dict):
            messages = result.get("messages")
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, "content"):
                    content = getattr(last_message, "content", "")
                    if isinstance(content, list):
                        return self._format_professional_response("\n".join(str(item) for item in content))
                    return self._format_professional_response(str(content))
            return self._format_professional_response(result.get("output", result.get("output_text", str(result))))

        if hasattr(result, "content"):
            return self._format_professional_response(str(result.content))

        if isinstance(result, list) and result:
            last_message = result[-1]
            if hasattr(last_message, "content"):
                return self._format_professional_response(str(last_message.content))

        return self._format_professional_response(str(result))

    def _format_professional_response(self, content: str) -> str:
        text = content.strip()
        if not text:
            return "No se pudo generar una respuesta útil con la información disponible."

        if "Diagnóstico rápido:" in text:
            return (
                "Resumen técnico:\n"
                f"{text}\n\n"
                "Acción recomendada: revisar el estado del cabezal de impresión, limpiar los inyectores y verificar la alineación antes de continuar con un servicio mayor."
            )

        return text
