"""
Componentes visuais avançados para o sistema Mavi - Atualizado com tema escuro e azul neon
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from streamlit.components.v1 import html

# Nova paleta de cores
NEON_BLUE = "#00BFFF"
BACKGROUND_DARK = "#000000"
COMPONENT_DARK = "#1A1A1A"
TEXT_NEON = "#00BFFF"
TEXT_SECONDARY = "#CCCCCC"
WHITE = "#FFFFFF"

def render_hero_section():
    """Renderiza a seção hero principal com tema escuro e azul neon"""
    html(f"""
    <div style="
        background: {COMPONENT_DARK};
        padding: 3rem 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        text-align: center;
        color: {WHITE};
        border: 1px solid {NEON_BLUE};
        box-shadow: 0 0 30px rgba(0, 191, 255, 0.2);
    ">
        <h1 style="
            font-size: 3rem;
            font-weight: 700;
            margin: 0 0 1rem 0;
            color: {TEXT_NEON};
            text-shadow: 0 0 10px {NEON_BLUE};
        ">🎯 Mavi Suporte</h1>
        
        <p style="
            font-size: 1.3rem;
            margin: 0;
            opacity: 0.9;
            color: {TEXT_SECONDARY};
            font-weight: 400;
        ">Sistema Inteligente de Gestão de Solicitações</p>
    </div>
    """, height=250)

def render_stats_cards(stats_data):
    """Renderiza cards de estatísticas com tema escuro"""
    cols = st.columns(len(stats_data))
    
    for i, (col, (title, value, icon, color)) in enumerate(zip(cols, stats_data.items())):
        with col:
            html(f"""
            <div style="
                background: {COMPONENT_DARK};
                padding: 2rem 1.5rem;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.5);
                border-left: 5px solid {NEON_BLUE};
                text-align: center;
                transition: transform 0.3s ease;
                margin: 1rem 0;
            " onmouseover="this.style.transform='translateY(-5px)'" 
               onmouseout="this.style.transform='translateY(0)'">
                
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: {NEON_BLUE}; margin: 0.5rem 0;">{value}</div>
                <div style="color: {TEXT_SECONDARY}; font-size: 1rem; font-weight: 500; text-transform: uppercase;">{title}</div>
            </div>
            """, height=200)

def render_priority_gauge(priority_counts):
    """Renderiza gauge de prioridades com tema escuro"""
    total = sum(priority_counts.values())
    if total == 0:
        st.info("Nenhum dado de prioridade para exibir.")
        return
        
    value = (priority_counts.get('Alta', 0) + priority_counts.get('Crítica', 0)) / total * 100

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Tickets de Alta Prioridade (%)", 'font': {'color': TEXT_NEON, 'size': 16}},
        gauge = {
            'axis': {'range': [None, 100], 'tickcolor': TEXT_SECONDARY},
            'bar': {'color': NEON_BLUE},
            'bgcolor': COMPONENT_DARK,
            'borderwidth': 2,
            'bordercolor': TEXT_SECONDARY,
            'steps': [
                {'range': [0, 50], 'color': '#2a2a2a'},
                {'range': [50, 100], 'color': '#3a3a3a'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }))
    
    fig.update_layout(
        height=300,
        font={'color': TEXT_SECONDARY, 'family': "Inter"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

def render_timeline_chart(df):
    """Renderiza gráfico de timeline com tema escuro"""
    if df.empty:
        st.info("Nenhum dado disponível para o gráfico de timeline.")
        return
    
    df['data_abertura'] = pd.to_datetime(df['data_abertura'])
    timeline_data = df.groupby(df['data_abertura'].dt.date).size().reset_index(name='quantidade')
    
    fig = px.line(timeline_data, x='data', y='quantidade', title='Timeline de Abertura de Tickets', markers=True)
    
    fig.update_traces(line_color=NEON_BLUE, marker_color=WHITE, marker_size=8, line_width=3)
    
    fig.update_layout(
        plot_bgcolor=COMPONENT_DARK,
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter",
        font_color=TEXT_NEON,
        xaxis=dict(gridcolor='#444444'),
        yaxis=dict(gridcolor='#444444'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def render_status_distribution(status_counts):
    """Renderiza gráfico de pizza de status com tema escuro"""
    if not status_counts:
        st.info("Nenhum dado disponível para distribuição de status.")
        return
    
    colors = [NEON_BLUE, '#0099cc', '#007799', '#005566', '#cccccc']
    
    fig = px.pie(
        values=list(status_counts.values()),
        names=list(status_counts.keys()),
        title='Distribuição por Status',
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12, textfont_color=WHITE)
    
    fig.update_layout(
        font_family="Inter",
        font_color=TEXT_NEON,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor=COMPONENT_DARK,
        height=400,
        legend_font_color=TEXT_SECONDARY
    )
    st.plotly_chart(fig, use_container_width=True)

def render_footer():
    """Renderiza rodapé com tema escuro"""
    html(f"""
    <div style="
        background: {COMPONENT_DARK};
        color: {TEXT_SECONDARY};
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        border-top: 2px solid {NEON_BLUE};
    ">
        <h3 style="margin: 0 0 0.5rem 0; font-size: 1.5rem; color: {TEXT_NEON};">Mavi Suporte</h3>
        <p style="margin: 0; opacity: 0.8;">
            © 2024 Mavi. Todos os direitos reservados.
        </p>
    </div>
    """, height=150)

# As outras funções de renderização (device_top10, notification_panel, etc.)
# podem ser adaptadas de forma semelhante, substituindo as cores antigas
# pela nova paleta (NEON_BLUE, COMPONENT_DARK, etc.).