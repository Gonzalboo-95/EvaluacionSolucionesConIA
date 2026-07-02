import time
import random
from typing import List, Tuple
from .observability import get_metrics_collector, ExecutionStatus


class TestScenario:
    #Define un escenario de prueba
    
    def __init__(self, query: str, expected_status: ExecutionStatus = ExecutionStatus.COMPLETED,
                 latency_ms: float = 500, tokens: int = 100, tools: List[str] = None,
                 retrieval_success: bool = True, error: str = None):
        self.query = query
        self.expected_status = expected_status
        self.latency_ms = latency_ms
        self.tokens = tokens
        self.tools = tools or []
        self.retrieval_success = retrieval_success
        self.error = error


def run_test_scenarios():
    #Ejecuta una serie de escenarios de prueba para generar datos de métricas
    
    collector = get_metrics_collector()
    
    # Definir escenarios de prueba
    scenarios = [
        # Escenarios de éxito
        TestScenario(
            query="¿Cómo limpio los cabezales de la Canon iX6810?",
            latency_ms=450,
            tokens=85,
            tools=["search_technical_manual"],
            retrieval_success=True
        ),
        TestScenario(
            query="La impresora hace ruido extraño en el motor",
            latency_ms=1200,
            tokens=150,
            tools=["search_technical_manual", "create_work_order"],
            retrieval_success=True
        ),
        TestScenario(
            query="¿Qué tipo de tinta debo usar para documentos legales?",
            latency_ms=300,
            tokens=70,
            tools=["search_technical_manual"],
            retrieval_success=True
        ),
        TestScenario(
            query="Necesito diagnosticar líneas en los documentos impresos",
            latency_ms=890,
            tokens=120,
            tools=["search_technical_manual", "diagnostic_check"],
            retrieval_success=True
        ),
        TestScenario(
            query="¿Cuál es el procedimiento de mantenimiento preventivo?",
            latency_ms=650,
            tokens=110,
            tools=["search_technical_manual"],
            retrieval_success=True
        ),
        # Escenarios con recuperación parcial
        TestScenario(
            query="Especificaciones técnicas completas del modelo",
            latency_ms=520,
            tokens=95,
            tools=["search_technical_manual"],
            retrieval_success=True
        ),
        TestScenario(
            query="Configuración de red avanzada",
            latency_ms=780,
            tokens=130,
            tools=["search_technical_manual"],
            retrieval_success=True
        ),
        # Escenario con fallo
        TestScenario(
            query="Información sobre modelo inexistente XYZ9999",
            expected_status=ExecutionStatus.PARTIAL,
            latency_ms=400,
            tokens=60,
            tools=[],
            retrieval_success=False,
            error="No se encontraron documentos relevantes"
        ),
        # Escenarios variados
        TestScenario(
            query="¿Cuál es el consumo de tinta por página?",
            latency_ms=350,
            tokens=75,
            tools=["search_technical_manual"],
            retrieval_success=True
        ),
        TestScenario(
            query="Cómo cambiar el cartucho de tinta",
            latency_ms=600,
            tokens=105,
            tools=["search_technical_manual", "create_work_order"],
            retrieval_success=True
        ),
        TestScenario(
            query="¿Puedo usar tinta de terceros?",
            latency_ms=420,
            tokens=90,
            tools=["search_technical_manual"],
            retrieval_success=True
        ),
        TestScenario(
            query="Código de error E02-4000",
            latency_ms=950,
            tokens=140,
            tools=["search_technical_manual", "diagnostic_check"],
            retrieval_success=True
        ),
    ]
    
    print("\n" + "=" * 60)
    print("EJECUTANDO CASOS DE PRUEBA DE OBSERVABILIDAD")
    print("=" * 60)
    
    results = []
    
    for idx, scenario in enumerate(scenarios, 1):
        print(f"\n[{idx}/{len(scenarios)}] Ejecutando: {scenario.query[:60]}...")
        
        # Iniciar ejecución
        exec_id = collector.start_execution(scenario.query)
        
        # Simular tiempo de procesamiento
        time.sleep(scenario.latency_ms / 1000.0)
        
        # Registrar herramientas
        for tool in scenario.tools:
            tool_duration = random.uniform(100, 500)
            collector.record_tool_call(exec_id, tool, tool_duration, success=True)
        
        # Registrar recuperación
        chunks = 3 if scenario.retrieval_success else 0
        retrieval_time = random.uniform(200, 500)
        collector.record_retrieval(
            exec_id,
            chunks_retrieved=chunks,
            success=scenario.retrieval_success,
            latency_ms=retrieval_time
        )
        
        # Registrar tokens
        collector.record_tokens(exec_id, scenario.tokens)
        
        # Generar respuesta simulada
        response = f"Respuesta a: {scenario.query[:50]}..."
        
        # Finalizar ejecución
        collector.end_execution(
            exec_id,
            response,
            status=scenario.expected_status,
            error=scenario.error
        )
        
        results.append({
            'query': scenario.query,
            'status': scenario.expected_status.value,
            'latency_ms': scenario.latency_ms,
            'tokens': scenario.tokens
        })
        
        print(f"  ✓ Completado - Latencia: {scenario.latency_ms}ms, Tokens: {scenario.tokens}")
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    summary = collector.get_summary_metrics()
    
    print(f"Total de ejecuciones: {summary['total_executions']}")
    print(f"Ejecuciones exitosas: {summary['completed']}")
    print(f"Ejecuciones fallidas: {summary['failed']}")
    print(f"Tasa de éxito: {summary['success_rate']:.1%}")
    print(f"Latencia promedio: {summary['avg_latency_ms']:.2f}ms")
    print(f"Tokens totales utilizados: {summary['total_tokens']}")
    print(f"Consistencia promedio: {summary['avg_consistency']:.2%}")
    print(f"Total de llamadas a herramientas: {summary['total_tools_executions']}")
    print(f"Herramientas únicas utilizadas: {len(summary['unique_tools'])}")
    
    print("\n" + "=" * 60)
    print("ANÁLISIS DE PUNTUACIÓN DE CONSISTENCIA")
    print("=" * 60)
    print("""
Métrica de Consistencia:
- Basada en: recuperación exitosa, herramientas ejecutadas, ausencia de errores
- Rango: 0.0 a 1.0
- Interpretación:
  * 1.0: Ejecución perfecta (todas las herramientas, recuperación exitosa)
  * 0.8+: Excelente (mínimo aceptable para producción)
  * 0.5-0.7: Aceptable (algunos errores pero funciona)
  * <0.5: Deficiente (múltiples problemas)
    """)
    
    print("\n" + "=" * 60)
    print("ANÁLISIS DE LATENCIA")
    print("=" * 60)
    
    latencies = [r['latency_ms'] for r in results]
    print(f"Latencia mínima: {min(latencies):.2f}ms")
    print(f"Latencia máxima: {max(latencies):.2f}ms")
    print(f"Latencia promedio: {sum(latencies)/len(latencies):.2f}ms")
    print(f"Desviación estándar: {_calculate_std_dev(latencies):.2f}ms")
    
    print("""
    
Recomendaciones por Latencia:
- <500ms: Excelente rendimiento ✓
- 500-1000ms: Aceptable para la mayoría de casos
- >1000ms: Requiere optimización
    """)
    
    print("\n" + "=" * 60)
    print("ANÁLISIS DE CONSUMO DE TOKENS")
    print("=" * 60)
    
    print(f"Tokens totales: {summary['total_tokens']}")
    print(f"Promedio por consulta: {summary['total_tokens'] / summary['total_executions']:.0f}")
    print(f"Costo estimado (GPT-4o): ${estimate_token_cost(summary['total_tokens']):.4f}")
    
    print("\n✓ Pruebas completadas. Los datos han sido guardados en logs/metrics.jsonl")
    print("✓ Ejecuta 'streamlit run dashboard.py' para visualizar el dashboard")


def _calculate_std_dev(values: List[float]) -> float:
    #Calcula desviación estándar
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5


def estimate_token_cost(tokens: int, model: str = "gpt-4o") -> float:
    #Estima el costo en dólares basado en tokens
    # Precios aproximados (pueden variar)
    prices = {
        'gpt-4o': {'input': 0.005 / 1000, 'output': 0.015 / 1000},
        'gpt-4': {'input': 0.03 / 1000, 'output': 0.06 / 1000},
        'gpt-3.5': {'input': 0.0005 / 1000, 'output': 0.0015 / 1000},
    }
    
    price_info = prices.get(model, prices['gpt-4o'])
    # Asumir 50/50 split entre input y output
    cost = (tokens / 2) * price_info['input'] + (tokens / 2) * price_info['output']
    return cost


if __name__ == "__main__":
    run_test_scenarios()
