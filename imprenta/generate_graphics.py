#Script para generar imágenes de visualizaciones (screenshots del dashboard)
#Para incluir en el reporte técnico


import json
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def load_metrics_data():
    #Carga datos de métricas desde el archivo JSONL
    metrics_file = Path("logs/metrics.jsonl")
    data = []
    
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    
    return data


def generate_visualizations():
    #Genera visualizaciones estáticas para el reporte
    
    data = load_metrics_data()
    
    if not data:
        print("No hay datos disponibles para generar visualizaciones")
        return
    
    df = pd.DataFrame(data)
    
    # Crear carpeta para gráficos
    graphics_dir = Path("graphics")
    graphics_dir.mkdir(exist_ok=True)
    
    print("Generando visualizaciones para el reporte...\n")
    
    # 1. Gráfico de Latencia a lo largo del tiempo
    print("1. Generando gráfico de latencia...")
    df['timestamp_start'] = pd.to_datetime(df['timestamp_start'])
    df_sorted = df.sort_values('timestamp_start')
    
    fig_latency = px.line(
        df_sorted,
        x='timestamp_start',
        y='latency_ms',
        title='Latencia de Ejecuciones (ms)',
        markers=True,
        labels={'timestamp_start': 'Tiempo', 'latency_ms': 'Latencia (ms)'},
        template='plotly_white'
    )
    fig_latency.update_traces(line=dict(color='#0066cc', width=2))
    fig_latency.write_html(graphics_dir / "01_latencia.html")
    fig_latency.write_image(graphics_dir / "01_latencia.png", width=1000, height=600)
    
    # 2. Gráfico de Distribución de Estados
    print("2. Generando gráfico de estados...")
    status_counts = df['status'].value_counts()
    
    colors_map = {
        'completado': '#00a86b',
        'fallido': '#ff0000',
        'parcial': '#ffcc00'
    }
    
    fig_status = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title='Distribución de Estados',
        template='plotly_white',
        color_discrete_map=colors_map
    )
    fig_status.write_html(graphics_dir / "02_estados.html")
    fig_status.write_image(graphics_dir / "02_estados.png", width=800, height=600)
    
    # 3. Gráfico de Uso de Tokens
    print("3. Generando gráfico de tokens...")
    df['tokens_cumulative'] = df['tokens_used'].cumsum()
    
    fig_tokens = go.Figure()
    
    fig_tokens.add_trace(go.Scatter(
        x=df_sorted['timestamp_start'],
        y=df_sorted['tokens_used'],
        mode='lines+markers',
        name='Tokens por Ejecución',
        line=dict(color='#ff6b6b', width=2),
        fill='tozeroy'
    ))
    
    fig_tokens.update_layout(
        title='Uso de Tokens por Ejecución',
        xaxis_title='Tiempo',
        yaxis_title='Tokens',
        template='plotly_white',
        hovermode='x unified'
    )
    fig_tokens.write_html(graphics_dir / "03_tokens.html")
    fig_tokens.write_image(graphics_dir / "03_tokens.png", width=1000, height=600)
    
    # 4. Gráfico de Consistencia
    print("4. Generando gráfico de consistencia...")
    fig_consistency = px.line(
        df_sorted,
        x='timestamp_start',
        y='consistency_score',
        title='Puntuación de Consistencia',
        markers=True,
        labels={'timestamp_start': 'Tiempo', 'consistency_score': 'Consistencia (0-1)'},
        template='plotly_white'
    )
    
    fig_consistency.add_hline(
        y=0.8, 
        line_dash="dash", 
        line_color="green",
        annotation_text="Mínimo Aceptable (0.8)"
    )
    fig_consistency.write_html(graphics_dir / "04_consistencia.html")
    fig_consistency.write_image(graphics_dir / "04_consistencia.png", width=1000, height=600)
    
    # 5. Tabla de Métricas Resumen
    print("5. Generando tabla de métricas...")
    
    summary_metrics = {
        'Métrica': [
            'Total de Ejecuciones',
            'Ejecuciones Exitosas',
            'Ejecuciones Fallidas',
            'Tasa de Éxito',
            'Latencia Mínima',
            'Latencia Máxima',
            'Latencia Promedio',
            'Tokens Totales',
            'Consistencia Promedio',
            'Herramientas Únicas'
        ],
        'Valor': [
            f"{len(df)}",
            f"{len(df[df['status'] == 'completado'])}",
            f"{len(df[df['status'] == 'fallido'])}",
            f"{len(df[df['status'] == 'completado']) / len(df) * 100:.1f}%",
            f"{df['latency_ms'].min():.2f} ms",
            f"{df['latency_ms'].max():.2f} ms",
            f"{df['latency_ms'].mean():.2f} ms",
            f"{df['tokens_used'].sum():,}",
            f"{df['consistency_score'].mean():.2%}",
            "3"
        ]
    }
    
    df_summary = pd.DataFrame(summary_metrics)
    
    fig_table = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>' + col + '</b>' for col in df_summary.columns],
            fill_color='paleturquoise',
            align='left',
            font=dict(size=12)
        ),
        cells=dict(
            values=[df_summary[col] for col in df_summary.columns],
            fill_color='lavender',
            align='left',
            font=dict(size=11)
        )
    )])
    
    fig_table.update_layout(
        title='Tabla de Métricas Resumen',
        height=400
    )
    fig_table.write_html(graphics_dir / "05_tabla_metricas.html")
    
    print("\n✓ Visualizaciones generadas en carpeta 'graphics/'")
    print("\nArchivos generados:")
    print("  - 01_latencia.png (HTML + PNG)")
    print("  - 02_estados.png (HTML + PNG)")
    print("  - 03_tokens.png (HTML + PNG)")
    print("  - 04_consistencia.png (HTML + PNG)")
    print("  - 05_tabla_metricas.html")
    
    return graphics_dir


def generate_summary_statistics():
    #Genera estadísticas para el reporte
    
    data = load_metrics_data()
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    stats = {
        'total_executions': len(df),
        'successful': len(df[df['status'] == 'completado']),
        'failed': len(df[df['status'] == 'fallido']),
        'partial': len(df[df['status'] == 'parcial']),
        'success_rate': (len(df[df['status'] == 'completado']) / len(df) * 100) if len(df) > 0 else 0,
        'avg_latency': df['latency_ms'].mean(),
        'min_latency': df['latency_ms'].min(),
        'max_latency': df['latency_ms'].max(),
        'std_latency': df['latency_ms'].std(),
        'total_tokens': df['tokens_used'].sum(),
        'avg_tokens': df['tokens_used'].mean(),
        'avg_consistency': df['consistency_score'].mean(),
        'min_consistency': df['consistency_score'].min(),
        'max_consistency': df['consistency_score'].max(),
    }
    
    # Mostrar estadísticas
    print("\n" + "="*60)
    print("ESTADÍSTICAS DE MÉTRICAS PARA REPORTE")
    print("="*60)
    print(f"Total de Ejecuciones: {stats['total_executions']}")
    print(f"  - Exitosas: {stats['successful']}")
    print(f"  - Fallidas: {stats['failed']}")
    print(f"  - Parciales: {stats['partial']}")
    print(f"  - Tasa de Éxito: {stats['success_rate']:.1f}%")
    print(f"\nLatencia (ms):")
    print(f"  - Promedio: {stats['avg_latency']:.2f}")
    print(f"  - Mínima: {stats['min_latency']:.2f}")
    print(f"  - Máxima: {stats['max_latency']:.2f}")
    print(f"  - Desv. Estándar: {stats['std_latency']:.2f}")
    print(f"\nTokens:")
    print(f"  - Total: {stats['total_tokens']:,}")
    print(f"  - Promedio: {stats['avg_tokens']:.0f}")
    print(f"\nConsistencia (0-1):")
    print(f"  - Promedio: {stats['avg_consistency']:.4f} ({stats['avg_consistency']:.2%})")
    print(f"  - Mínima: {stats['min_consistency']:.4f}")
    print(f"  - Máxima: {stats['max_consistency']:.4f}")
    print("="*60)
    
    return stats


if __name__ == "__main__":
    print("Sistema de Generación de Visualizaciones para Reporte")
    print("=" * 60)
    
    # Generar estadísticas
    stats = generate_summary_statistics()
    
    # Generar gráficos
    try:
        graphics_dir = generate_visualizations()
        print(f"\n✓ Todos los gráficos han sido generados exitosamente en: {graphics_dir}")
    except Exception as e:
        print(f"\n✗ Error al generar visualizaciones: {e}")
        print("Nota: Asegúrate de tener 'kaleido' instalado:")
        print("  pip install kaleido")
