
# Proyecto Imprenta Artificial 3 — EXAMEN ISY0101

Agente multi-especialista con RAG híbrido para soporte técnico Canon iX6810 en **Imprenta Nueva Imagen**.


## Arquitectura

- **CoordinatorAgent** — clasifica, planifica y enruta consultas
- **CanonTechnicalAgent** — diagnóstico técnico + RAG interno/externo
- **WorkshopAgent** — órdenes de trabajo con priorización
- **ProductionAgent** — recomendaciones de equipo y materiales
- **MemoryStore** — memoria deslizante (k=5) para buena continuidad
- **ObservableRAGAgent** — métricas de precisión, latencia y consistencia

## Componentes técnicos

- LangChain + GPT-4o
- FAISS (RAG: `data/` interno + `external_sources/` externo)
- Wikipedia API (fuente externa complementaria)
- Streamlit dashboard de observabilidad

## Instalación

```bash
pip install -r requirements.txt
```

Configure en `.env` o variables de entorno:

```bash
OPENAI_API_KEY=tu_clave
# opcional: OPENAI_API_BASE=https://...
```

## Ejecución

```bash
# Demo sin API (recomendado para verificar instalación)
python -m imprenta.demo_local

# Construir índice RAG (requiere API key)
python -m imprenta.ingesta

# Agente interactivo con observabilidad y seguridad
python run_agent.py

# Generar métricas de prueba
python -m imprenta.test_scenarios

# Dashboard
streamlit run imprenta/dashboard.py
```

## Estructura del proyecto

```
Proyecto_ImprentaArtificial3/
├── COLAB_EXAMEN.ipynb               # Notebook de entrega
├── docs/
├── data/                            # Fuentes internas RAG
├── external_sources/                # Fuentes externas RAG
├── imprenta/
│   ├── agents.py                    # RAGAgent + memoria
│   ├── coordinator.py               # Multi-agente + planificación
│   ├── prompts.py                     # Prompts estructurados 
│   ├── security.py                  # Protocolos seguridad 
│   ├── tools.py                     # Herramientas consulta/escritura/razonamiento
│   ├── tasks.py                     # Factory del agente
│   ├── observability.py             # Métricas 
│   ├── agent_monitoring.py          # Wrapper observable
│   ├── dashboard.py                 # Dashboard Streamlit
│   └── test_scenarios.py            # Escenarios de prueba
├── logs/                            # Trazabilidad 
└── requirements.txt
```
## Referencias

- LangChain: https://python.langchain.com/docs/
- OpenAI API: https://platform.openai.com/docs/api-reference
- FAISS: https://faiss.ai/
