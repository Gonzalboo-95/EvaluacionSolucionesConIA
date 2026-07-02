#Integración de Observabilidad con el Agente RAG

import time
from typing import Any, Dict, Optional
from .observability import get_metrics_collector, ExecutionStatus


class ObservableRAGAgent:
    #Wrapper alrededor del RAGAgent que captura métricas de observabilidad.
  
    
    def __init__(self, agent: Any, enable_metrics: bool = True):
        self.agent = agent
        self.enable_metrics = enable_metrics
        self.metrics_collector = get_metrics_collector() if enable_metrics else None
    
    def ask(self, question: str) -> str:
        #Ejecuta ask con captura de métricas.

        if not self.enable_metrics:
            return self.agent.ask(question)
        
        # Iniciar ejecución
        execution_id = self.metrics_collector.start_execution(question)
        start_time = time.time()
        
        try:
            # Envolver la llamada original
            response = self._execute_with_monitoring(execution_id, question)
            
            # Registrar éxito
            end_time = time.time()
            self.metrics_collector.end_execution(
                execution_id,
                response,
                status=ExecutionStatus.COMPLETED
            )
            
            return response
            
        except Exception as e:
            # Registrar fallo
            self.metrics_collector.end_execution(
                execution_id,
                "",
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
            raise
    
    def _execute_with_monitoring(self, execution_id: str, question: str) -> str:
        
        #Ejecuta la pregunta y captura información de herramientas y recuperación.
        
        start_retrieval = time.time()
        
        # Ejecutar el agente
        response = self.agent.ask(question)
        
        # Estimar tokens 
        estimated_tokens = len(question.split()) + len(response.split())
        self.metrics_collector.record_tokens(execution_id, estimated_tokens)
        
        # Registrar recuperación 
        retrieval_time = (time.time() - start_retrieval) * 1000
        
        self.metrics_collector.record_retrieval(
            execution_id,
            chunks_retrieved=3, 
            success=True,
            latency_ms=retrieval_time
        )
        
        return response
    
    @property
    def memory(self):
    
        return self.agent.memory
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        #Devuelve resumen de métricas recolectadas

        if not self.enable_metrics:
            return {}
        return self.metrics_collector.get_summary_metrics()


class MetricsMiddleware:

    
    def __init__(self, metrics_collector):
        self.metrics_collector = metrics_collector
    
    def before_tool_call(self, execution_id: str, tool_name: str) -> Dict[str, Any]:
        #Llamado antes de ejecutar una herramienta
        return {
            'tool_name': tool_name,
            'start_time': time.time(),
            'execution_id': execution_id,
        }
    
    def after_tool_call(self, context: Dict[str, Any], 
                       success: bool = True, error: Optional[str] = None) -> None:
        #Llamado después de ejecutar una herramienta
        duration_ms = (time.time() - context['start_time']) * 1000
        
        self.metrics_collector.record_tool_call(
            execution_id=context['execution_id'],
            tool_name=context['tool_name'],
            duration_ms=duration_ms,
            success=success,
            error=error
        )
