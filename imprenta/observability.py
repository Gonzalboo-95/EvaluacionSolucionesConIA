#Sistema de Observabilidad y Métricas para el Agente RAG Canon iX6810
#Proporciona trazabilidad completa de la ejecución del agente


import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading


class ExecutionStatus(Enum):
    #Estados posibles de una ejecución de agente
    STARTED = "iniciado"
    PROCESSING = "procesando"
    COMPLETED = "completado"
    FAILED = "fallido"
    PARTIAL = "parcial"


@dataclass
class MetricSnapshot:
    #Captura de una métrica en un momento específico
    timestamp: str
    latency_ms: float
    status: str
    tokens_used: Optional[int] = None
    tools_called: int = 0
    retrieval_success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentExecutionMetrics:
    #Métricas completas de una ejecución del agente
    execution_id: str
    query: str
    timestamp_start: str
    status: ExecutionStatus
    latency_ms: float = 0.0
    tokens_used: int = 0
    tools_executed: List[str] = field(default_factory=list)
    retrieval_chunks: int = 0
    retrieval_success: bool = True
    response_length: int = 0
    consistency_score: float = 0.0
    error_message: Optional[str] = None
    timestamp_end: Optional[str] = None
    memory_usage_mb: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'status': self.status.value if isinstance(self.status, ExecutionStatus) else self.status
        }


class MetricsCollector:
    #Recolector centralizado de métricas del agente
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar logging
        self.logger = self._setup_logger()
        
        # Almacenamiento de métricas
        self.metrics: List[AgentExecutionMetrics] = []
        self.current_execution: Optional[AgentExecutionMetrics] = None
        self.lock = threading.Lock()
        
        # Rutas de archivos
        self.metrics_file = self.log_dir / "metrics.jsonl"
        self.events_file = self.log_dir / "events.log"
        
        # Cargar métricas previas
        self._load_existing_metrics()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura el sistema de logging"""
        logger = logging.getLogger("CanonAgent")
        logger.setLevel(logging.DEBUG)
        
        # Manejador para archivo
        fh = logging.FileHandler(self.log_dir / "agent_execution.log")
        fh.setLevel(logging.DEBUG)
        
        # Manejador para consola
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger
    
    def _load_existing_metrics(self) -> None:
        #Carga métricas existentes del archivo
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            # Reconvertir el estado
                            data['status'] = ExecutionStatus(data['status'])
                            metric = AgentExecutionMetrics(**data)
                            self.metrics.append(metric)
                self.logger.info(f"Cargadas {len(self.metrics)} métricas previas")
            except Exception as e:
                self.logger.warning(f"No se pudieron cargar métricas previas: {e}")
    
    def start_execution(self, query: str) -> str:
        #Inicia una nueva ejecución del agente
        import uuid
        execution_id = str(uuid.uuid4())
        
        now = datetime.now().isoformat()
        self.current_execution = AgentExecutionMetrics(
            execution_id=execution_id,
            query=query,
            timestamp_start=now,
            status=ExecutionStatus.STARTED,
        )
        
        self.logger.info(f"[{execution_id}] Iniciando ejecución con query: {query[:100]}")
        return execution_id
    
    def record_tool_call(self, execution_id: str, tool_name: str, 
                         duration_ms: float, success: bool = True, 
                         error: Optional[str] = None) -> None:
        #Registra la ejecución de una herramienta
        if self.current_execution and self.current_execution.execution_id == execution_id:
            self.current_execution.tools_executed.append(tool_name)
            self.logger.info(
                f"[{execution_id}] Herramienta '{tool_name}' ejecutada en {duration_ms:.2f}ms "
                f"{'[OK]' if success else '[FAIL]'}"
            )
            if error:
                self.logger.error(f"[{execution_id}] Error en {tool_name}: {error}")
    
    def record_retrieval(self, execution_id: str, chunks_retrieved: int, 
                        success: bool = True, latency_ms: float = 0.0) -> None:
        #Registra la recuperación de documentos
        if self.current_execution and self.current_execution.execution_id == execution_id:
            self.current_execution.retrieval_chunks = chunks_retrieved
            self.current_execution.retrieval_success = success
            self.logger.info(
                f"[{execution_id}] Recuperación: {chunks_retrieved} chunks en {latency_ms:.2f}ms"
            )
    
    def record_tokens(self, execution_id: str, tokens: int) -> None:
        #Registra el uso de tokens
        if self.current_execution and self.current_execution.execution_id == execution_id:
            self.current_execution.tokens_used = tokens
            self.logger.debug(f"[{execution_id}] Tokens utilizados: {tokens}")
    
    def end_execution(self, execution_id: str, response: str, 
                     status: ExecutionStatus = ExecutionStatus.COMPLETED,
                     error: Optional[str] = None) -> None:
        #Finaliza una ejecución del agente
        if self.current_execution and self.current_execution.execution_id == execution_id:
            now = datetime.now().isoformat()
            start_time = datetime.fromisoformat(self.current_execution.timestamp_start)
            end_time = datetime.fromisoformat(now)
            
            self.current_execution.timestamp_end = now
            self.current_execution.status = status
            self.current_execution.response_length = len(response)
            self.current_execution.error_message = error
            
            # Calcular latencia
            self.current_execution.latency_ms = (
                (end_time - start_time).total_seconds() * 1000
            )
            
            # Calcular consistencia (basada en presencia de herramientas y recuperación)
            consistency_score = self._calculate_consistency()
            self.current_execution.consistency_score = consistency_score
            
            # Guardar métrica
            with self.lock:
                self.metrics.append(self.current_execution)
                self._save_metric(self.current_execution)
            
            self.logger.info(
                f"[{execution_id}] Ejecución completada en {self.current_execution.latency_ms:.2f}ms "
                f"con estado: {status.value}"
            )
            
            self.current_execution = None
    
    def _calculate_consistency(self) -> float:
    
        #Calcula puntuación de consistencia basada en:
        #- Recuperación exitosa
        #- Herramientas ejecutadas
        #- Ausencia de errores
        if not self.current_execution:
            return 0.0
        
        score = 1.0
        
        # Deducir por fallo de recuperación
        if not self.current_execution.retrieval_success:
            score -= 0.3
        
        # Deducir por errores
        if self.current_execution.error_message:
            score -= 0.2
        
        # Añadir puntos por herramientas ejecutadas
        if self.current_execution.tools_executed:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _save_metric(self, metric: AgentExecutionMetrics) -> None:
        #Guarda una métrica en el archivo JSONL
        try:
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(metric.to_dict()) + '\n')
        except Exception as e:
            self.logger.error(f"Error guardando métrica: {e}")
    
    def get_summary_metrics(self) -> Dict[str, Any]:
        #Devuelve resumen de métricas agregadas
        if not self.metrics:
            return {
                'total_executions': 0,
                'success_rate': 0.0,
                'avg_latency_ms': 0.0,
                'total_tokens': 0,
                'avg_consistency': 0.0,
            }
        
        completed = [m for m in self.metrics if m.status == ExecutionStatus.COMPLETED]
        failed = [m for m in self.metrics if m.status == ExecutionStatus.FAILED]
        
        total_latency = sum(m.latency_ms for m in self.metrics)
        total_tokens = sum(m.tokens_used for m in self.metrics)
        avg_consistency = (
            sum(m.consistency_score for m in self.metrics) / len(self.metrics)
            if self.metrics else 0.0
        )
        
        return {
            'total_executions': len(self.metrics),
            'completed': len(completed),
            'failed': len(failed),
            'success_rate': len(completed) / len(self.metrics) if self.metrics else 0.0,
            'avg_latency_ms': total_latency / len(self.metrics) if self.metrics else 0.0,
            'total_tokens': total_tokens,
            'avg_consistency': avg_consistency,
            'total_tools_executions': sum(len(m.tools_executed) for m in self.metrics),
            'unique_tools': set(
                tool for m in self.metrics for tool in m.tools_executed
            ),
        }
    
    def get_recent_metrics(self, n: int = 10) -> List[Dict[str, Any]]:
        #Devuelve las N métricas más recientes
        return [m.to_dict() for m in self.metrics[-n:]]
    
    def export_metrics_csv(self, filename: str = "metrics_export.csv") -> str:
        #Exporta métricas a CSV para análisis externo
        import csv
        
        filepath = self.log_dir / filename
        try:
            with open(filepath, 'w', newline='') as f:
                if self.metrics:
                    fieldnames = self.metrics[0].to_dict().keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for metric in self.metrics:
                        writer.writerow(metric.to_dict())
            self.logger.info(f"Métricas exportadas a {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"Error exportando métricas: {e}")
            return ""


# Instancia global del colector
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    #Obtiene la instancia singleton del colector de métricas
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
