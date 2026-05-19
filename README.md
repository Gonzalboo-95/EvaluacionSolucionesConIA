# Maestro imprentero : Asistente RAG para Canon iX6810

En este proyecto implementamos un CHATBOT para resolver dudas sobre la impresora Canon iX6810.
Utilizamos una base de datos vectorial construida con manuales y fuentes externas de soporte.

## Especificaciones Técnicas
- LLM: GPT-4o (GitHub Models API)
- **Embeddings:** text-embedding-3-small
- **Segmentación:** Chunks de 800 caracteres / Overlap 150
- **Lógica de Recuperación:** 3 fragmentos por consulta (k=3)

## Fuentes de datos
- `data/`: Manuales PDF internos de la Canon iX6810.
- `external_sources/`: Referencias externas y artículos técnicos para enriquecer las respuestas.
- `index_canon/`: Índice local FAISS generado por `procesar_manuales.py`.

## Arquitectura
1. `procesar_manuales.py`: carga datos internos y externos, los divide en fragmentos y genera embeddings.
2. `index_canon/`: almacena la base vectorial local para recuperaciones rápidas.
3. `app.py`: recupere los datos relevantes, arma el prompt RAG y consulta al LLM.

Diagrama de flujo:

```text
[Manuales PDF internos] \
                          +-> [Segmentación + Embeddings] -> [FAISS index] -> [Retriever] -> [Prompt RAG] -> [LLM]
[Documentos externos]   /
```

## Organización del Proyecto
- `app.py`: Interfaz de consulta y pipeline RAG.
- `procesar_manuales.py`: Pipeline de ingesta y vectorización por lotes.
- `data/`: Repositorio de manuales PDF.
- `external_sources/`: Artículos técnicos y referencias externas.
- `index_canon/`: Base de datos vectorial persistente.

## Cómo ejecutar
1. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Crea un archivo `.env` con tu token:
   ```bash
   GITHUB_TOKEN=tu_token_aqui
   ```
3. Genera el índice vectorial:
   ```bash
   python procesar_manuales.py
   ```
4. Inicia el chatbot:
   ```bash
   python app.py
   ```

## Mejoras aplicadas
- Se agregó soporte para fuentes externas mediante `external_sources/`.
- Se mejoró el prompt para usar tanto manuales internos como documentación externa.
- Se añadió una sección de arquitectura y flujo de datos.
- `.env` está listado en `.gitignore` para proteger credenciales.
- `index_canon/` también se ignora como artefacto generado.

Desarrollado por Jose, Martin y Gonzalo - Duoc UC