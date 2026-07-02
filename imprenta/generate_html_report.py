#Generador de Reporte HTML con Visualizaciones
#Crea un reporte HTML interactivo sin dependencias externas complejas


import json
from pathlib import Path
from datetime import datetime
import statistics


def load_metrics():
    #Carga métricas del archivo JSONL
    metrics_file = Path("logs/metrics.jsonl")
    data = []
    
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    return data


def generate_html_report():
    #Genera reporte HTML con tablas y gráficos ASCII
    
    data = load_metrics()
    
    if not data:
        print("No hay datos disponibles")
        return None
    
    # Preparar datos
    latencies = [m['latency_ms'] for m in data]
    tokens = [m['tokens_used'] for m in data]
    consistency = [m['consistency_score'] for m in data]
    statuses = {}
    for m in data:
        status = m.get('status', 'unknown')
        statuses[status] = statuses.get(status, 0) + 1
    
    # Calcular estadísticas
    stats = {
        'total': len(data),
        'success': statuses.get('completado', 0),
        'failed': statuses.get('fallido', 0),
        'partial': statuses.get('parcial', 0),
        'latency_min': min(latencies),
        'latency_max': max(latencies),
        'latency_avg': statistics.mean(latencies),
        'latency_median': statistics.median(latencies),
        'latency_stdev': statistics.stdev(latencies) if len(latencies) > 1 else 0,
        'tokens_total': sum(tokens),
        'tokens_avg': statistics.mean(tokens),
        'consistency_avg': statistics.mean(consistency),
        'consistency_min': min(consistency),
        'consistency_max': max(consistency),
    }
    
    # Crear HTML
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Observabilidad - Canon Agent</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        h1, h2 {{ color: #0066cc; }}
        .metric-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .kpi {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .kpi-item {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .kpi-value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .kpi-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        th {{
            background: #0066cc;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background: #f9f9f9;
        }}
        .status-completado {{
            background: #d4edda;
            color: #155724;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        .status-fallido {{
            background: #f8d7da;
            color: #721c24;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        .status-parcial {{
            background: #fff3cd;
            color: #856404;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        .chart {{
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
        }}
        .bar {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}
        .bar-label {{
            width: 150px;
            font-weight: bold;
        }}
        .bar-fill {{
            background: #0066cc;
            height: 30px;
            display: flex;
            align-items: center;
            color: white;
            padding-left: 10px;
            border-radius: 4px;
            min-width: 2%;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>📊 Reporte de Observabilidad</h1>
    <p>Agente RAG Canon iX6810 - Evaluación Parcial 3</p>
    <p>Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="kpi">
        <div class="kpi-item">
            <div class="kpi-label">Total de Ejecuciones</div>
            <div class="kpi-value">{stats['total']}</div>
        </div>
        <div class="kpi-item" style="background: linear-gradient(135deg, #00a86b 0%, #00cc7a 100%);">
            <div class="kpi-label">Tasa de Éxito</div>
            <div class="kpi-value">{stats['success']/stats['total']*100:.1f}%</div>
        </div>
        <div class="kpi-item" style="background: linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%);">
            <div class="kpi-label">Latencia Promedio</div>
            <div class="kpi-value">{stats['latency_avg']:.0f}ms</div>
        </div>
        <div class="kpi-item" style="background: linear-gradient(135deg, #ffa500 0%, #ffb700 100%);">
            <div class="kpi-label">Consistencia</div>
            <div class="kpi-value">{stats['consistency_avg']:.0%}</div>
        </div>
    </div>
    
    <div class="metric-card">
        <h2>📈 Distribución de Estados</h2>
        <div class="chart">
            <div class="bar">
                <div class="bar-label">Completado</div>
                <div class="bar-fill" style="width: {stats['success']/stats['total']*100:.0f}%; background: #00a86b;">
                    {stats['success']} ({stats['success']/stats['total']*100:.1f}%)
                </div>
            </div>
            <div class="bar">
                <div class="bar-label">Fallido</div>
                <div class="bar-fill" style="width: {stats['failed']/stats['total']*100:.0f}%; background: #ff6b6b;">
                    {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)
                </div>
            </div>
            <div class="bar">
                <div class="bar-label">Parcial</div>
                <div class="bar-fill" style="width: {stats['partial']/stats['total']*100:.0f}%; background: #ffa500;">
                    {stats['partial']} ({stats['partial']/stats['total']*100:.1f}%)
                </div>
            </div>
        </div>
    </div>
    
    <div class="metric-card">
        <h2>⏱️ Análisis de Latencia</h2>
        <table>
            <tr>
                <th>Métrica</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Latencia Mínima</td>
                <td><strong>{stats['latency_min']:.2f} ms</strong></td>
            </tr>
            <tr>
                <td>Latencia Máxima</td>
                <td><strong>{stats['latency_max']:.2f} ms</strong></td>
            </tr>
            <tr>
                <td>Latencia Promedio</td>
                <td><strong>{stats['latency_avg']:.2f} ms</strong></td>
            </tr>
            <tr>
                <td>Mediana</td>
                <td><strong>{stats['latency_median']:.2f} ms</strong></td>
            </tr>
            <tr>
                <td>Desviación Estándar</td>
                <td><strong>{stats['latency_stdev']:.2f} ms</strong></td>
            </tr>
        </table>
    </div>
    
    <div class="metric-card">
        <h2>🔑 Consumo de Tokens</h2>
        <table>
            <tr>
                <th>Métrica</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Total de Tokens</td>
                <td><strong>{stats['tokens_total']:,}</strong></td>
            </tr>
            <tr>
                <td>Promedio por Consulta</td>
                <td><strong>{stats['tokens_avg']:.0f}</strong></td>
            </tr>
            <tr>
                <td>Costo Estimado (GPT-4o)</td>
                <td><strong>${stats['tokens_total']/1000*0.01:.4f}</strong></td>
            </tr>
        </table>
    </div>
    
    <div class="metric-card">
        <h2>✓ Consistencia</h2>
        <table>
            <tr>
                <th>Métrica</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Consistencia Promedio</td>
                <td><strong>{stats['consistency_avg']:.2%}</strong></td>
            </tr>
            <tr>
                <td>Mínima</td>
                <td><strong>{stats['consistency_min']:.2%}</strong></td>
            </tr>
            <tr>
                <td>Máxima</td>
                <td><strong>{stats['consistency_max']:.2%}</strong></td>
            </tr>
            <tr>
                <td>Estado</td>
                <td><span class="status-completado">{'Excelente' if stats['consistency_avg'] >= 0.9 else 'Bueno' if stats['consistency_avg'] >= 0.8 else 'Aceptable'}</span></td>
            </tr>
        </table>
    </div>
    
    <div class="metric-card">
        <h2>📋 Últimas 10 Ejecuciones</h2>
        <table>
            <tr>
                <th>Consulta</th>
                <th>Estado</th>
                <th>Latencia</th>
                <th>Tokens</th>
                <th>Consistencia</th>
            </tr>
"""
    
    # Agregar últimas 10 ejecuciones
    for exec_data in data[-10:]:
        status_class = f"status-{exec_data.get('status', 'unknown')}"
        html_content += f"""
            <tr>
                <td title="{exec_data.get('query', 'N/A')}">{exec_data.get('query', 'N/A')[:50]}...</td>
                <td><span class="{status_class}">{exec_data.get('status', 'unknown')}</span></td>
                <td>{exec_data.get('latency_ms', 0):.0f} ms</td>
                <td>{exec_data.get('tokens_used', 0)}</td>
                <td>{exec_data.get('consistency_score', 0):.1%}</td>
            </tr>
"""
    
    html_content += """
        </table>
    </div>
    
    <div class="footer">
        <p>Reporte generado automáticamente por el sistema de observabilidad</p>
        <p>Para más información, ejecutar: streamlit run dashboard.py</p>
    </div>
</body>
</html>
"""
    
    # Guardar HTML
    output_file = Path("reporte_observabilidad.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✓ Reporte HTML generado: {output_file}")
    print(f"✓ Abre en navegador para visualizar")
    
    return output_file


if __name__ == "__main__":
    generate_html_report()
