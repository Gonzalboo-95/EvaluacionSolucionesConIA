
# Informe Técnico del Proyecto de Agente para Canon iX6810

## Resumen
Este proyecto desarrolla un agente funcional orientado a la Canon iX6810 para un entorno de imprenta.
El sistema integra consultas técnicas, memoria de conversación, recuperación semántica y toma de decisiones dentro de un flujo organizacional.

## Componentes y frameworks
- `langchain`: framework base para orquestar el agente y la recuperación de contexto.
- `langchain_openai`: acceso a LLM GPT-4o para razonamiento y generación de respuestas.
- `FAISS`: motor de recuperación semántica que indexa los manuales y las fuentes externas.
- `dotenv`: gestión de credenciales de forma segura.
- `langchain`
- `langchain-community`
- `langchain-openai`
- `faiss-cpu`
- `pypdf`
- `python-dotenv`
- `openai`

## Arquitectura del agente
El sistema se compone de:
- `CoordinatorAgent`: cerebro central que clasifica solicitudes y coordina agentes especializados.
- `CanonTechnicalAgent`: experto en diagnóstico y mantenimiento de la Canon iX6810.
- `WorkshopAgent`: gestiona órdenes de reparación y prioriza fallas técnicas.
- `ProductionAgent`: administra decisiones de trabajo de imprenta, elección de equipo y materiales.
- `MemoryStore`: guarda el historial de conversación y entrega contexto relevante para continuidad.
- `RAG Chain`: recupera contexto de documentos y combina memoria con la consulta actual.

## Descripción
- **Coordinador Principal**: recibe la consulta, clasifica el tipo y enruta al agente especializado.
- **Agente Técnico Canon iX6810**: consulta la base de conocimiento, usa memoria y responde con diagnóstico y plan.
- **Agente de Taller Técnico**: genera órdenes de trabajo y prioriza reparaciones.
- **Agente de Producción de Imprenta**: recomienda equipo, materiales y cola de impresión.
- **Recuperación semántica**: utiliza FAISS para extraer fragmentos relevantes de manuales y documentos técnicos.
- **Memoria**: mantiene el historial reciente para asegurar continuidad en flujos prolongados.

## Procesos de memoria y recuperación de contexto
- La memoria de contenido se mantiene en `MemoryStore`, con un resumen de las interacciones recientes.
- El flujo de consultas técnicas incluye tanto la memoria como el contexto recuperado de FAISS.
- Esto asegura continuidad en tareas prolongadas y evita respuestas inconexas.

## Planificación y toma de decisiones
El agente incorpora planificación explícita en cada especializada:
- El agente técnico define una secuencia de verificación de síntomas, consulta documental, recomendación y seguimiento.
- El agente de taller genera un plan de acción que incluye priorización, orden de trabajo y derivación.
- El agente de producción decide el equipo más adecuado y sugiere materiales y orden de operación.

## Ejemplos de decisiones adaptativas
1. Si un operario indica "imprime con líneas", el agente técnico recomienda limpieza de cabezales y realiza diagnóstico inicial.
2. Si se solicita "equipo urgente" o "falla crítica", el taller técnico genera una orden con prioridad urgente.
3. Si el trabajo es "A3 color", el agente de producción sugiere Canon iX6810 y materiales de alta calidad.

## Justificación de componentes
- `LangChain` se utiliza para integrar herramientas de consulta, escritura y razonamiento con un flujo modular.
- `FAISS` es el motor adecuado para recuperación semántica de manuales y documentación técnica.
- La separación en agentes especializados refuerza la autonomía y clarifica las responsabilidades del sistema.
- `MemoryStore` y la inclusión de contexto reciente garantizan continuidad en flujos prolongados, un criterio clave de la evaluación.

## Cómo ejecutar
1. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Genera el índice vectorial:
   ```bash
   python ingesta.py
   ```
3. Ejecuta el agente CLI:
   ```bash
   python main.py
   ```
4. Ejecuta los casos de ejemplo:
   ```bash
   python demo_cases.py
   ```

## Referencias APA
- LangChain. (2025). LangChain Documentation. https://www.langchain.com
- OpenAI. (2024). Chat completions API. https://platform.openai.com/docs/api-reference/chat
- FAISS. (2024). Facebook AI Similarity Search. https://github.com/facebookresearch/faiss
