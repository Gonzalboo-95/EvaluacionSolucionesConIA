"""Protocolos de seguridad y uso responsable del agente (IE11)."""

import re
from dataclasses import dataclass
from typing import Optional


MAX_QUERY_LENGTH = 2000
BLOCKED_PATTERNS = [
    r"(?i)\b(api[_-]?key|token|password|contraseña|secreto)\b",
    r"(?i)\b(hackear|exploit|bypass\s+seguridad)\b",
    r"(?i)\b(datos\s+personales|rut\s*[:=]|correo\s*[:=])\b",
]

ETHICAL_DISCLAIMER = (
    "Aviso: Este asistente apoya decisiones técnicas con base documental. "
    "No reemplaza la supervisión humana ni procedimientos de seguridad del taller. "
    "Verifique siempre con un técnico certificado antes de intervenciones críticas."
)


@dataclass
class SecurityValidationResult:
    allowed: bool
    sanitized_query: str
    reason: Optional[str] = None


def sanitize_input(query: str) -> SecurityValidationResult:
    """Valida y sanitiza la entrada del operario antes de procesarla."""
    if not query or not query.strip():
        return SecurityValidationResult(False, "", "La consulta está vacía.")

    cleaned = query.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)

    if len(cleaned) > MAX_QUERY_LENGTH:
        return SecurityValidationResult(
            False,
            cleaned[:MAX_QUERY_LENGTH],
            f"La consulta excede el límite de {MAX_QUERY_LENGTH} caracteres.",
        )

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, cleaned):
            return SecurityValidationResult(
                False,
                cleaned,
                "La consulta contiene contenido no permitido por políticas de privacidad y seguridad.",
            )

    return SecurityValidationResult(True, cleaned)


def append_ethical_notice(response: str) -> str:
    """Añade aviso de uso responsable a la respuesta del agente."""
    if ETHICAL_DISCLAIMER in response:
        return response
    return f"{response}\n\n---\n{ETHICAL_DISCLAIMER}"
