# Proyecto de Agente RAG Canon iX6810 - Evaluación Parcial 3
## Implementación de Observabilidad

**Asignatura:** ISY0101 - Ingeniería de Soluciones con IA  
**Evaluación:** Parcial 3 - Implementación de Observabilidad  
**Fecha:** Julio 2026

---

## 📋 Tabla de Contenidos

1. [Resumen](#resumen)
2. [Nuevos Componentes de Observabilidad](#nuevos-componentes-de-observabilidad)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Cómo Ejecutar](#cómo-ejecutar)
5. [Dashboard de Monitoreo](#dashboard-de-monitoreo)
6. [Análisis de Métricas](#análisis-de-métricas)
7. [Reporte Técnico](#reporte-técnico)
8. [Estructura del Proyecto](#estructura-del-proyecto)

---

## 📌 Resumen

Este proyecto implementa un **sistema integral de observabilidad** para un agente RAG (Retrieval-Augmented Generation) especializado en soporte técnico para la impresora Canon iX6810.

### Objetivos Cumplidos (Evaluación Parcial 3)

✅ **IL3.1** - Implementación de métricas de observabilidad (Precisión, Latencia, Consistencia)  
✅ **IL3.2** - Análisis de registros y trazabilidad mediante logging  
✅ **IL3.3** - Integración de protocolos de seguridad y responsabilidad  
✅ **IL3.4** - Propuestas de mejora basadas en análisis de datos observados  

---

## 🔧 Nuevos Componentes de Observabilidad

### 1. **observability.py** - Sistema de Métricas
- **Clase `MetricsCollector`**: Recolector centralizado de métricas
- **Métricas Capturadas:**
  - Latencia de ejecución (ms)
  - Precisión (tasa de éxito)
  - Consistencia (0-1)
  - Uso de tokens
  - Herramientas ejecutadas
  - Frecuencia de errores

### 2. **agent_monitoring.py** - Integración con Agente
- **Clase `ObservableRAGAgent`**: Wrapper que captura métricas sin modificar código original
- **Clase `MetricsMiddleware`**: Middleware para monitorear herramientas

### 3. **dashboard.py** - Dashboard de Monitoreo
- Visualización en tiempo real con Streamlit
- Gráficos interactivos con Plotly
- KPIs principales
- Tabla de ejecuciones recientes
- Exportación a CSV

### 4. **test_scenarios.py** - Casos de Prueba
- 12 escenarios realistas
- Genera datos de métricas
- Análisis de latencia y tokens
- Validación de consistencia

### 5. **report_generator.py** - Generador de Reporte
- Genera reporte técnico en Markdown
- Análisis estadístico completo
- Recomendaciones de optimización
- Referencias APA

---

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.10+
- pip (gestor de paquetes)
- API Key de OpenAI (para usar el agente real)

### Paso 1: Clonar/Descargar el Proyecto
```bash
cd "c:\Users\Gonsa\OneDrive\Documentos\INGENIERIA DE SOLUCIONES CON INTELIGENCIA ARTIFICIAL_801D_OLS\Evaluacion Parcial 3\Proyecto_ImprentaArtificial"
```

### Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `langchain` - Framework para orquestar agentes
- `langchain-openai` - Integración con GPT-4o
- `faiss-cpu` - Búsqueda semántica
- `streamlit` - Dashboard interactivo
- `plotly` - Gráficos interactivos
- `pandas` - Análisis de datos
- `python-docx` - Generación de documentos

### Paso 3: Configurar Variables de Entorno
```bash
# Crear archivo .env en la raíz del proyecto
setx OPENAI_API_KEY "tu_clave_api"
# o
setx GITHUB_TOKEN "tu_token_github"
```

### Paso 4: Generar Índice FAISS (si no existe)
```bash
python ingesta.py
```

---

## 🎯 Cómo Ejecutar

### Opción 1: Ejecutar Casos de Prueba (Generan Métricas)
```bash
python test_scenarios.py
```

**Salida esperada:**
- 12 ejecuciones de prueba
- Métricas guardadas en `logs/metrics.jsonl`
- Análisis de latencia y consistencia
- Resumen de KPIs

### Opción 2: Ver Dashboard de Monitoreo
```bash
streamlit run dashboard.py
```

El dashboard se abrirá en `http://localhost:8501` con:
- Métricas en tiempo real
- Gráficos de latencia, éxito, tokens
- Tabla de últimas ejecuciones
- Opción de exportar a CSV

### Opción 3: Generar Reporte Técnico
```bash
python -c "from report_generator import generate_technical_report; generate_technical_report()"
```

Genera `Reporte_Evaluacion_Parcial_3.md` con:
- Análisis completo de métricas
- Hallazgos de trazabilidad
- Propuestas de mejora
- Referencias APA

### Opción 4: Usar el Agente Interactivo
```bash
python main.py
```

Inicia CLI interactivo para consultas técnicas.

---

## 📊 Dashboard de Monitoreo

### Características

**KPIs Principales:**
- Total de Ejecuciones
- Tasa de Éxito (%)
- Latencia Promedio (ms)
- Consistencia Promedio (0-1)

**Visualizaciones:**
1. **Latencia a lo largo del tiempo** - Línea con tendencia
2. **Distribución de estados** - Gráfico circular (completado/fallido/parcial)
3. **Uso de tokens** - Área acumulativa
4. **Puntuación de consistencia** - Línea con línea de mínimo aceptable

**Tabla de Detalles:**
- Últimas 20 ejecuciones
- ID, consulta, estado, latencia, tokens, consistencia

---

## 📈 Análisis de Métricas

### Métricas Implementadas (IL3.1 y IL3.2)

#### 1. **Precisión**
```
Fórmula: Ejecuciones Exitosas / Total de Ejecuciones × 100
Rango: 0-100%
Estado Actual: 91.7%
Interpretación: Buena precisión - el agente completa mayoría de tareas exitosamente
```

#### 2. **Latencia**
```
Definición: Tiempo total de ejecución desde solicitud hasta respuesta
Métrica Actual: 631.72 ms promedio
Rango Aceptable: 500-1000 ms
Análisis: Latencia en rango aceptable, con variabilidad (σ = 265.72 ms)
```

#### 3. **Consistencia**
```
Definición: Métrica que mide confiabilidad de ejecuciones
Basada en:
  - Recuperación exitosa: +0 (base)
  - Herramientas ejecutadas: +0.1 (por ejecución)
  - Sin errores: +0 (base)
  - Fallo de recuperación: -0.3
  - Presencia de errores: -0.2

Rango: 0.0 (peor) a 1.0 (perfecto)
Actual: 95.83% promedio
Interpretación: Excelente - prácticamente todas las ejecuciones son consistentes
```

### Análisis de Trazabilidad (IL3.2)

**Archivos de Log Generados:**

1. `logs/agent_execution.log` - Log de todas las ejecuciones
   ```
   2026-07-01 00:24:19 - CanonAgent - INFO - [exec-id] Iniciando ejecución
   2026-07-01 00:24:19 - CanonAgent - INFO - [exec-id] Herramienta ejecutada
   2026-07-01 00:24:20 - CanonAgent - INFO - [exec-id] Ejecución completada
   ```

2. `logs/metrics.jsonl` - Una métrica por línea (formato JSON)
   ```json
   {"execution_id": "...", "query": "...", "status": "completado", "latency_ms": 631.72, ...}
   ```

3. `logs/events.log` - Registro de eventos (generado)

**Puntos de Falla Identificados:**
- Modelo inexistente: Recuperación fallida pero ejecución parcial (consistencia: 0.7)
- Consultas complejas: Latencia > 1000ms (requiere optimización)

---

## 📄 Reporte Técnico

### Descripción
Documento profesional de máximo 5 páginas que incluye:

1. **Resumen Ejecutivo**
   - Objetivos logrados
   - KPIs principales

2. **Análisis de Precisión**
   - Tasa de éxito: 91.7%
   - Ejecuciones: 24 total, 22 exitosas

3. **Análisis de Latencia**
   - Mínima: 300 ms
   - Máxima: 1200 ms
   - Promedio: 631.72 ms
   - Análisis: Aceptable pero con potencial de mejora

4. **Análisis de Consistencia**
   - Promedio: 95.83%
   - Estado: Excelente

5. **Propuestas de Mejora (IL3.4)**
   - Implementar caching (-30% latencia)
   - Optimizar búsqueda FAISS (-20% latencia)
   - Paralelizar herramientas (-25% latencia)
   - Fine-tuning del modelo LLM

6. **Protocolos de Seguridad (IL3.3)**
   - Autenticación con variables de entorno
   - Validación de entrada
   - Criterios éticos implementados
   - Recomendaciones para producción

7. **Conclusiones y Referencias APA**

**Ubicación del Reporte:**
`Reporte_Evaluacion_Parcial_3.md`

---

## 📁 Estructura del Proyecto

```
Proyecto_ImprentaArtificial/
├── agents.py                          # Agente RAG original
├── app.py                            # Aplicación
├── main.py                           # CLI interactivo
├── tasks.py                          # Construcción de agentes
├── tools.py                          # Herramientas disponibles
├── env_utils.py                      # Utilidades de entorno
├── ingesta.py                        # Generador de índice FAISS
│
├── 📊 NUEVOS COMPONENTES DE OBSERVABILIDAD
├── observability.py                  # Sistema de métricas
├── agent_monitoring.py               # Wrapper de agente observable
├── dashboard.py                      # Dashboard Streamlit
├── test_scenarios.py                 # Casos de prueba
├── report_generator.py               # Generador de reportes
│
├── 📁 data/                          # Datos del proyecto
├── 📁 external_sources/              # Documentación técnica
│   └── canon_ix6810_soporte_externo.txt
├── 📁 index_canon/                   # Índice FAISS
│   └── index.faiss
│
├── 📁 logs/                          # 📊 NUEVO - Logs de observabilidad
│   ├── agent_execution.log           # Log completo
│   ├── metrics.jsonl                 # Métricas (JSONL)
│   └── events.log                    # Eventos
│
├── README.md                         # Este archivo
├── requirements.txt                  # Dependencias
├── Reporte_Evaluacion_Parcial_3.md   # 📊 NUEVO - Reporte técnico
└── .env                              # Variables de entorno (no incluir en git)
```

---

## 🔍 Ejemplos de Uso

### Ejemplo 1: Ver Métricas de Pruebas Anteriores
```bash
python test_scenarios.py
# Salida:
# Total de ejecuciones: 24
# Tasa de éxito: 91.7%
# Latencia promedio: 631.72ms
# Consistencia promedio: 95.83%
```

### Ejemplo 2: Abrir Dashboard
```bash
streamlit run dashboard.py
# Se abre en: http://localhost:8501
```

### Ejemplo 3: Revisar Logs
```bash
# Mostrar últimas 20 líneas de ejecución
Get-Content "logs/agent_execution.log" -Tail 20

# Ver todas las métricas
Get-Content "logs/metrics.jsonl"
```

### Ejemplo 4: Analizar Específica Métrica
```python
from observability import get_metrics_collector

collector = get_metrics_collector()
summary = collector.get_summary_metrics()

print(f"Tasa de éxito: {summary['success_rate']:.1%}")
print(f"Latencia promedio: {summary['avg_latency_ms']:.2f}ms")
print(f"Consistencia: {summary['avg_consistency']:.2%}")
```

---

## 📋 Entregables Completados

### ✅ A. Implementación de Métricas (IL3.1, IL3.2)
- [x] Precisión: 91.7% (tasa de éxito)
- [x] Latencia: 631.72 ms (promedio)
- [x] Consistencia: 95.83% (promedio)
- [x] Uso de Recursos: 2,460 tokens totales

### ✅ B. Análisis de Registros y Trazabilidad (IL3.3)
- [x] Logging completo en `logs/agent_execution.log`
- [x] Métricas estructuradas en `logs/metrics.jsonl`
- [x] Identificación de puntos de falla
- [x] Documentación de hallazgos

### ✅ C. Dashboard de Monitoreo (IL2, IL4, IL5)
- [x] Dashboard interactivo en Streamlit
- [x] Gráficos de latencia, éxito, tokens, consistencia
- [x] Tabla de ejecuciones recientes
- [x] Exportación a CSV

### ✅ D. Propuestas de Mejora (IL6, IL7)
- [x] Mejora de latencia (caching, optimización FAISS)
- [x] Mejora de precisión (prompt engineering, fine-tuning)
- [x] Escalabilidad (microservicios, base de datos distribuida)
- [x] Sostenibilidad (monitoreo continuo, alertas)

### ✅ E. Reporte Técnico (IL8, IL9)
- [x] Documento profesional < 5 páginas
- [x] Capturas y gráficos del dashboard
- [x] Lenguaje técnico preciso
- [x] Referencias APA
- [x] Ubicación: `Reporte_Evaluacion_Parcial_3.md`

### ✅ F. Repositorio Digital
- [x] Código fuente completo
- [x] Documentación (este README)
- [x] Evidencia de pruebas (test_scenarios.py)
- [x] Instrucciones de ejecución claras

---

## 🎓 Criterios de Evaluación Cumplidos

| Indicador | Descripción | Estado | Evidencia |
|-----------|-------------|--------|-----------|
| IL3.1 | Métricas de precisión, latencia, consistencia | ✅ | observability.py, test_scenarios.py |
| IL3.2 | Análisis de logs y trazabilidad | ✅ | logs/agent_execution.log, logs/metrics.jsonl |
| IL3.3 | Protocolos de seguridad y responsabilidad | ✅ | agent_monitoring.py, report_generator.py sección 6 |
| IL3.4 | Propuestas de mejora basadas en datos | ✅ | report_generator.py sección 7 |
| IE1 | Implementación técnica completa | ✅ | Todos los módulos |
| IE2 | Documentación clara y coherente | ✅ | README.md, Reporte técnico |
| IE3 | Código limpio y organizado | ✅ | Estructura modular |

---

## 📞 Contacto y Soporte

Para preguntas o problemas:
1. Revisar sección "Cómo Ejecutar" de este README
2. Verificar que todas las dependencias están instaladas: `pip list`
3. Confirmar que la carpeta `logs/` existe y tiene permisos de escritura
4. Revisar `logs/agent_execution.log` para errores detallados

---

## 📝 Notas Adicionales

- **API OpenAI**: Se requiere API key válida para usar el agente completo
- **FAISS Index**: Debe generarse primero con `python ingesta.py`
- **Streamlit**: Dashboard requiere navegador web (abre automáticamente)
- **Métricas**: Se acumulan en `logs/metrics.jsonl` - no limpiar para análisis histórico

---

**Proyecto Completado:** Julio 2026  
**Versión:** 1.0  
**Última Actualización:** 2026-07-01
