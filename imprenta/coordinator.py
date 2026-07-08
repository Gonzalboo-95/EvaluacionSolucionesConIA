"""Orquestación multi-agente con planificación y toma de decisiones (IE5, IE6, IE7, IE8)."""

from enum import Enum
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage

from .agents import ConversationBufferWindowMemory, RAGAgent
from .prompts import QueryIntent, build_user_prompt, get_system_prompt


class TaskStage(str, Enum):
    CLASSIFY = "clasificar"
    RETRIEVE = "recuperar"
    REASON = "razonar"
    ACT = "actuar"
    VERIFY = "verificar"


class IntentRouter:
    """Clasifica la intención informacional de la consulta del operario."""

    TECHNICAL_KEYWORDS = (
        "línea", "linea", "raya", "bandas", "error", "código", "codigo",
        "cabezal", "tinta", "cartucho", "impresión", "impresion", "borroso",
        "atasco", "ruido", "diagnóstico", "diagnostico", "mantenimiento",
    )
    WORKSHOP_KEYWORDS = (
        "orden", "taller", "reparar", "reparación", "reparacion", "urgente",
        "crítico", "critico", "servicio", "técnico", "tecnico", "falla",
    )
    PRODUCTION_KEYWORDS = (
        "a3", "a4", "color", "producción", "produccion", "material", "papel",
        "gigantografía", "gigantografia", "lonas", "volumen", "folletos",
        "equipo", "cola", "trabajo",
    )

    @classmethod
    def classify(cls, question: str) -> QueryIntent:
        lower = question.lower()
        scores = {
            QueryIntent.TECHNICAL: sum(1 for k in cls.TECHNICAL_KEYWORDS if k in lower),
            QueryIntent.WORKSHOP: sum(1 for k in cls.WORKSHOP_KEYWORDS if k in lower),
            QueryIntent.PRODUCTION: sum(1 for k in cls.PRODUCTION_KEYWORDS if k in lower),
        }
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return QueryIntent.GENERAL
        return best


class TaskPlanner:
    """Genera planes multi-etapa adaptados a la intención y condiciones cambiantes (IE7)."""

    @staticmethod
    def build_plan(intent: QueryIntent, question: str) -> List[str]:
        lower = question.lower()
        urgent = any(term in lower for term in ("urgente", "crítico", "critico", "inmediato"))

        if intent == QueryIntent.TECHNICAL:
            steps = [
                "Identificar síntoma y contexto operativo",
                "Recuperar evidencia en manuales internos (FAISS) y fuentes externas",
                "Ejecutar diagnóstico preliminar con herramienta de razonamiento",
                "Proponer plan de acción técnico verificable",
            ]
            if urgent:
                steps.insert(0, "Elevar prioridad: incidente crítico detectado")
            return steps

        if intent == QueryIntent.WORKSHOP:
            priority = "Urgente" if urgent else "Normal/Alta según síntomas"
            return [
                f"Evaluar severidad del incidente (prioridad: {priority})",
                "Consultar historial de conversación para continuidad",
                "Generar orden de trabajo con trazabilidad",
                "Definir pasos de reparación y seguimiento",
            ]

        if intent == QueryIntent.PRODUCTION:
            return [
                "Analizar formato, volumen y calidad requerida",
                "Seleccionar equipo según política interna de imprenta",
                "Recomendar materiales y configuración",
                "Sugerir orden en cola de producción",
            ]

        return [
            "Clasificar requerimiento informacional",
            "Recuperar contexto documental relevante",
            "Razonar con herramientas disponibles",
            "Entregar respuesta estructurada al operario",
        ]


class CoordinatorAgent:
    """
    Agente coordinador que enruta consultas a especialistas simulados
    manteniendo memoria, planificación y orquestación de herramientas.
    """

    AGENT_NAMES = {
        QueryIntent.TECHNICAL: "CanonTechnicalAgent",
        QueryIntent.WORKSHOP: "WorkshopAgent",
        QueryIntent.PRODUCTION: "ProductionAgent",
        QueryIntent.GENERAL: "CoordinatorAgent",
    }

    def __init__(self, rag_agent: RAGAgent) -> None:
        self.rag_agent = rag_agent
        self.memory = rag_agent.memory
        self.execution_log: List[Dict[str, Any]] = []

    @property
    def last_routing(self) -> Optional[Dict[str, Any]]:
        return self.execution_log[-1] if self.execution_log else None

    def ask(self, question: str) -> str:
        intent = IntentRouter.classify(question)
        plan = TaskPlanner.build_plan(intent, question)
        agent_name = self.AGENT_NAMES[intent]

        routing_record = {
            "intent": intent.value,
            "agent": agent_name,
            "plan": plan,
            "stages": [s.value for s in TaskStage],
        }
        self.execution_log.append(routing_record)

        enriched_question = build_user_prompt(
            question=question,
            intent=intent,
            memory_summary=self.memory.summary(),
            plan_steps=plan,
        )

        system_prompt = get_system_prompt(intent)
        return self._invoke_specialist(enriched_question, system_prompt, agent_name)

    def _invoke_specialist(self, question: str, system_prompt: str, agent_name: str) -> str:
        self.memory.add_user_message(question)

        memory_msgs = self.memory.to_human_messages()
        system_msg = HumanMessage(content=f"[{agent_name}]\n{system_prompt}")
        user_msg = HumanMessage(content=question)
        payload = {"messages": [system_msg] + memory_msgs + [user_msg]}

        try:
            result = self.rag_agent.agent.invoke(payload)
        except Exception:
            result = self.rag_agent.agent(payload)

        response = self.rag_agent._extract_response(result)
        self.memory.add_assistant_message(response)
        return response

    def get_orchestration_summary(self) -> str:
        if not self.execution_log:
            return "Sin ejecuciones registradas."
        last = self.execution_log[-1]
        plan_lines = "\n".join(f"  - {step}" for step in last["plan"])
        return (
            f"Última orquestación:\n"
            f"  Agente: {last['agent']}\n"
            f"  Intención: {last['intent']}\n"
            f"  Plan:\n{plan_lines}"
        )
