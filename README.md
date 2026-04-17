# Maestro imprentero : Asistente RAG para Canon iX6810

En este proyecto implementamos un CHATBOT para resolver dudas sobre la impresora Canon iX6810.
Utilizamos una base de datos vectorial contruida con manuales y mas de 65 guías de errores.

## Especificaciones Técnicas
- LLM: GPT-4o (GitHub Models API)
- **Embeddings:** text-embedding-3-small
- **Segmentación:** Chunks de 800 caracteres / Overlap 150
- **Lógica de Recuperación:** 3 fragmentos por consulta (k=3)

## Organización del Proyecto
- `app.py`: Interfaz de consulta , cueerpo principal del chatbot.
- `procesar_manuales.py`: Pipeline de ingesta y vectorización por lotes.
- `data/`: Repositorio de manuales PDF.
- `index_canon/`: Base de datos vectorial persistente.

Desarrollado por Jose, Martin y Gonzalo - Duoc UC*