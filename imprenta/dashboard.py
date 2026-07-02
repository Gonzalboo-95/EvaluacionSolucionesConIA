
#Dashboard de Monitoreo del Agente Canon iX6810
#Visualiza métricas de observabilidad en tiempo real


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import json

# Configuración de página
st.set_page_config(
    page_title="Dashboard - Canon Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-metric {
        color: #00a86b;
    }
    .warning-metric {
        color: #ffa500;
    }
    .error-metric {
        color: #ff0000;
    }
</style>
""", unsafe_allow_html=True)


def load_metrics_data():
    #Carga datos de métricas desde el archivo JSONL
    metrics_file = Path("logs/metrics.jsonl")
    data = []
    
    if metrics_file.exists():
        try:
            with open(metrics_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
        except Exception as e:
            st.error(f"Error cargando métricas: {e}")
    
    return data


def calculate_metrics(data: list) -> dict:
    #Calcula métricas agregadas
    if not data:
        return {
            'total_executions': 0,
            'success_rate': 0,
            'avg_latency': 0,
            'total_tokens': 0,
            'avg_consistency': 0,
            'unique_tools': 0,
        }
    
    df = pd.DataFrame(data)
    
    # Calcular métricas
    completed = len(df[df['status'] == 'completado'])
    failed = len(df[df['status'] == 'fallido'])
    total = len(df)
    
    success_rate = (completed / total * 100) if total > 0 else 0
    avg_latency = df['latency_ms'].mean() if 'latency_ms' in df.columns else 0
    total_tokens = df['tokens_used'].sum() if 'tokens_used' in df.columns else 0
    avg_consistency = df['consistency_score'].mean() if 'consistency_score' in df.columns else 0
    
    # Contar herramientas únicas
    unique_tools = set()
    if 'tools_executed' in df.columns:
        for tools in df['tools_executed']:
            if isinstance(tools, list):
                unique_tools.update(tools)
    
    return {
        'total_executions': total,
        'completed': completed,
        'failed': failed,
        'success_rate': success_rate,
        'avg_latency': avg_latency,
        'total_tokens': total_tokens,
        'avg_consistency': avg_consistency,
        'unique_tools': len(unique_tools),
    }


def plot_latency_over_time(data: list):
    #Gráfico de latencia a lo largo del tiempo
    if not data:
        st.info("No hay datos de latencia disponibles")
        return
    
    df = pd.DataFrame(data)
    df['timestamp_start'] = pd.to_datetime(df['timestamp_start'])
    df = df.sort_values('timestamp_start')
    
    fig = px.line(
        df,
        x='timestamp_start',
        y='latency_ms',
        title='Latencia de Ejecuciones (ms)',
        markers=True,
        labels={'timestamp_start': 'Tiempo', 'latency_ms': 'Latencia (ms)'},
        template='plotly_white'
    )
    
    fig.update_traces(line=dict(color='#0066cc', width=2))
    st.plotly_chart(fig, use_container_width=True)


def plot_success_rate(data: list):
    #Gráfico de tasa de éxito
    if not data:
        st.info("No hay datos de ejecución disponibles")
        return
    
    df = pd.DataFrame(data)
    status_counts = df['status'].value_counts()
    
    colors_map = {
        'completado': '#00a86b',
        'fallido': '#ff0000',
        'iniciado': '#ffa500',
        'procesando': '#0066cc',
        'parcial': '#ffcc00'
    }
    
    colors = [colors_map.get(status, '#808080') for status in status_counts.index]
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title='Distribución de Estados de Ejecución',
        template='plotly_white',
        color_discrete_sequence=colors
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_tokens_usage(data: list):
    #Gráfico de uso de tokens
    if not data:
        st.info("No hay datos de tokens disponibles")
        return
    
    df = pd.DataFrame(data)
    df['timestamp_start'] = pd.to_datetime(df['timestamp_start'])
    df = df.sort_values('timestamp_start')
    
    # Calcular uso acumulativo
    df['tokens_cumulative'] = df['tokens_used'].cumsum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp_start'],
        y=df['tokens_used'],
        mode='lines+markers',
        name='Tokens por Ejecución',
        line=dict(color='#ff6b6b', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title='Uso de Tokens',
        xaxis_title='Tiempo',
        yaxis_title='Tokens',
        template='plotly_white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_consistency_score(data: list):
    #Gráfico de consistencia a lo largo del tiempo
    if not data:
        st.info("No hay datos de consistencia disponibles")
        return
    
    df = pd.DataFrame(data)
    df['timestamp_start'] = pd.to_datetime(df['timestamp_start'])
    df = df.sort_values('timestamp_start')
    
    fig = px.line(
        df,
        x='timestamp_start',
        y='consistency_score',
        title='Puntuación de Consistencia (0-1)',
        markers=True,
        labels={'timestamp_start': 'Tiempo', 'consistency_score': 'Consistencia'},
        template='plotly_white'
    )
    
    fig.add_hline(y=0.8, line_dash="dash", line_color="green", 
                  annotation_text="Mínimo aceptable (0.8)")
    
    st.plotly_chart(fig, use_container_width=True)


def show_detailed_metrics(data: list):
    #Muestra tabla detallada de últimas ejecuciones
    if not data:
        st.info("No hay datos disponibles")
        return
    
    df = pd.DataFrame(data)
    
    # Seleccionar columnas relevantes
    display_columns = [
        'execution_id', 'query', 'timestamp_start', 'status',
        'latency_ms', 'tokens_used', 'consistency_score'
    ]
    
    available_columns = [col for col in display_columns if col in df.columns]
    df_display = df[available_columns].tail(20).copy()
    
    # Formatear
    if 'latency_ms' in df_display.columns:
        df_display['latency_ms'] = df_display['latency_ms'].apply(lambda x: f"{x:.2f}ms")
    
    if 'timestamp_start' in df_display.columns:
        df_display['timestamp_start'] = pd.to_datetime(df_display['timestamp_start']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    if 'consistency_score' in df_display.columns:
        df_display['consistency_score'] = df_display['consistency_score'].apply(lambda x: f"{x:.2%}")
    
    st.dataframe(df_display, use_container_width=True)


def main():
    # Header
    st.title("📊 Dashboard de Observabilidad")
    st.subheader("Agente RAG Canon iX6810 - Sistema de Monitoreo")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Opciones")
        refresh_rate = st.slider("Frecuencia de actualización (segundos)", 5, 60, 10)
        show_raw_data = st.checkbox("Mostrar datos brutos", value=False)
        export_metrics = st.button("📥 Exportar Métricas a CSV")
    
    # Cargar datos
    data = load_metrics_data()
    metrics = calculate_metrics(data)
    
    # KPIs principales
    st.markdown("### 📈 Indicadores Clave de Desempeño (KPIs)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Ejecuciones",
            metrics['total_executions'],
            delta=f"{metrics['completed']} exitosas"
        )
    
    with col2:
        st.metric(
            "Tasa de Éxito",
            f"{metrics['success_rate']:.1f}%",
            delta_color="off" if metrics['success_rate'] >= 80 else "inverse"
        )
    
    with col3:
        st.metric(
            "Latencia Promedio",
            f"{metrics['avg_latency']:.2f}ms",
            delta="ms" if metrics['avg_latency'] > 0 else None
        )
    
    with col4:
        st.metric(
            "Consistencia Promedio",
            f"{metrics['avg_consistency']:.2%}",
            delta_color="off" if metrics['avg_consistency'] >= 0.8 else "inverse"
        )
    
    # Análisis de Precisión y Latencia
    st.markdown("### 🎯 Análisis de Precisión y Latencia")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Latencia", "Éxito", "Tokens", "Consistencia"])
    
    with tab1:
        plot_latency_over_time(data)
    
    with tab2:
        plot_success_rate(data)
    
    with tab3:
        plot_tokens_usage(data)
    
    with tab4:
        plot_consistency_score(data)
    
    # Tabla detallada
    st.markdown("### 📋 Últimas Ejecuciones (20 más recientes)")
    show_detailed_metrics(data)
    
    # Datos brutos
    if show_raw_data:
        st.markdown("### 🔍 Datos Brutos (JSON)")
        if data:
            st.json(data[-5:])  # Últimas 5 ejecuciones
    
    # Exportar
    if export_metrics:
        from .observability import get_metrics_collector
        collector = get_metrics_collector()
        filepath = collector.export_metrics_csv()
        st.success(f"✓ Métricas exportadas a: {filepath}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Leyenda de Estados:**
    - 🟢 Completado: Ejecución exitosa
    - 🔴 Fallido: Error en la ejecución
    - 🟡 Procesando: Ejecución en progreso
    - 🟠 Iniciado: Ejecución iniciada
    - 🟠 Parcial: Ejecución completada parcialmente
    """)


if __name__ == "__main__":
    main()
