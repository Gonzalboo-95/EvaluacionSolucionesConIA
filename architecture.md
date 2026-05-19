# Diagrama de Arquitectura

A continuación se presenta el diagrama de arquitectura del sistema (Mermaid) y una breve explicación de los componentes.

```mermaid
flowchart LR
  subgraph Ingest
    A[Manuales PDF (data/)] --> B[procesar_manuales.py]
    C[Documentos externos (external_sources/)] --> B
    B --> D[Chunking & Embeddings (800/150)]
    D --> E[FAISS index (index_canon/)]
  end

  subgraph Query
    U[Operario / CLI] --> F[app.py (Retriever + Prompt)]
    F --> G[Retriever: top-k docs]
    G --> H[Prompt RAG (context assembly)]
    H --> I[LLM (gpt-4o)]
    I --> F
  end

  E --> G
  env[[.env (local, ignored)]] -.-> F
```

Componentes:
- `data/`: manuales PDF internos.
- `external_sources/`: fuentes externas de apoyo.
- `procesar_manuales.py`: ingesta, chunking y generación de embeddings.
- `index_canon/`: índice FAISS persistido localmente.
- `app.py`: interfaz de consulta, recuperación y ensamblaje de prompt RAG.
- `.env`: archivo local con credenciales (debe permanecer fuera del repositorio).

Este diagrama puede exportarse a formatos de imagen o integrarse en el informe final.
