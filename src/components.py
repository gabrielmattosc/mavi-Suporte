"""
Componentes visuais avançados para o sistema Mavi
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from streamlit.components.v1 import html

def render_hero_section():
    """Renderiza a seção hero principal"""
    html("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        text-align: center;
        color: white;
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.3);
    ">
        <h1 style="
            font-size: 3rem;
            font-weight: 700;
            margin: 0 0 1rem 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">🎯 Mavi Suporte</h1>
        
        <p style="
            font-size: 1.3rem;
            margin: 0 0 2rem 0;
            opacity: 0.95;
            font-weight: 300;
        ">Sistema Inteligente de Gestão de Solicitações</p>
        
        <div style="
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 2rem;
        ">
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 1rem 1.5rem;
                border-radius: 10px;
                backdrop-filter: blur(10px);
            ">
                <div style="font-size: 1.5rem; font-weight: 600;">⚡</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Rápido</div>
            </div>
            
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 1rem 1.5rem;
                border-radius: 10px;
                backdrop-filter: blur(10px);
            ">
                <div style="font-size: 1.5rem; font-weight: 600;">🔒</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Seguro</div>
            </div>
            
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 1rem 1.5rem;
                border-radius: 10px;
                backdrop-filter: blur(10px);
            ">
                <div style="font-size: 1.5rem; font-weight: 600;">📊</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Inteligente</div>
            </div>
        </div>
    </div>
    """, height = 400)
def render_stats_cards(stats):
    """Renderiza cards de estatísticas com animações"""
    col1, col2, col3, col4 = st.columns(4)
    
    cards_data = [
        ("📋", "Total", stats.get('total_solicitacoes', 0), "#667eea"),
        ("⏳", "Pendentes", stats.get('pendentes', 0), "#ffc107"),
        ("🔄", "Em Andamento", stats.get('em_andamento', 0), "#17a2b8"),
        ("✅", "Concluídos", stats.get('concluidas', 0), "#28a745")
    ]
    
    for i, (icon, label, value, color) in enumerate(cards_data):
        with [col1, col2, col3, col4][i]:
            st.metric(
                label=f"{icon} {label}",
                value=value,
                help=f"Número de tickets {label.lower()}"
            )

def render_progress_ring(percentage, label, color="#667eea"):
    """Renderiza um anel de progresso animado"""
    fig = go.Figure(data=[go.Pie(
        labels=['Completo', 'Restante'],
        values=[percentage, 100-percentage],
        hole=.7,
        marker_colors=[color, '#f8f9fa'],
        textinfo='none',
        hoverinfo='none',
        showlegend=False
    )])
    
    fig.update_layout(
        annotations=[dict(text=f'{percentage}%', x=0.5, y=0.5, font_size=20, showarrow=False)],
        height=200,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def render_timeline_chart(df):
    """Renderiza gráfico de timeline interativo"""
    if df.empty:
        return None
    
    # Prepara dados para timeline
    df['data_criacao'] = pd.to_datetime(df['data_criacao'])
    df_timeline = df.groupby([df['data_criacao'].dt.date, 'status']).size().reset_index(name='count')
    
    fig = px.line(
        df_timeline,
        x='data_criacao',
        y='count',
        color='status',
        title="📈 Timeline de Tickets",
        color_discrete_map={
            'Pendente': '#ffc107',
            'Em andamento': '#17a2b8',
            'Concluída': '#28a745'
        }
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        title_font_size=18,
        title_x=0.5,
        xaxis_title="Data",
        yaxis_title="Número de Tickets",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    return fig

def render_device_chart(dispositivos_stats):
    """Renderiza gráfico de dispositivos com estilo moderno"""
    if not dispositivos_stats:
        return None
    
    # Prepara dados
    items = list(dispositivos_stats.items())[:8]  # Top 8
    dispositivos, counts = zip(*items)
    
    fig = go.Figure(data=[
        go.Bar(
            y=dispositivos,
            x=counts,
            orientation='h',
            marker=dict(
                color=counts,
                colorscale='Viridis',
                showscale=False
            ),
            text=counts,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="💻 Dispositivos Mais Solicitados",
        title_font_size=18,
        title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        xaxis_title="Quantidade",
        yaxis_title="",
        height=400
    )
    
    return fig

def render_notification_status(email_sent, sms_sent, phone_provided):
    """Renderiza status das notificações com ícones"""
    st.markdown("### 📬 Status das Notificações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_icon = "✅" if email_sent else "❌"
        email_color = "#28a745" if email_sent else "#dc3545"
        email_status = "Enviado" if email_sent else "Falhou"
        
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid {email_color};
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem;">{email_icon}</span>
                <div>
                    <div style="font-weight: 600;">📧 E-mail</div>
                    <div style="color: {email_color}; font-size: 0.9rem;">{email_status}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if phone_provided:
            sms_icon = "✅" if sms_sent else "❌"
            sms_color = "#28a745" if sms_sent else "#dc3545"
            sms_status = "Enviado" if sms_sent else "Falhou"
        else:
            sms_icon = "➖"
            sms_color = "#6c757d"
            sms_status = "Não solicitado"
        
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid {sms_color};
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem;">{sms_icon}</span>
                <div>
                    <div style="font-weight: 600;">📱 SMS</div>
                    <div style="color: {sms_color}; font-size: 0.9rem;">{sms_status}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_ticket_card(ticket_id, position, status):
    """Renderiza card do ticket criado"""
    status_colors = {
        'Pendente': '#ffc107',
        'Em andamento': '#17a2b8',
        'Concluída': '#28a745'
    }
    
    status_color = status_colors.get(status, '#6c757d')
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        animation: ticketPulse 2s ease-in-out;
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🎫</div>
        <h2 style="margin: 0 0 1rem 0;">Ticket Criado!</h2>
        
        <div style="
            display: flex;
            justify-content: space-around;
            margin: 2rem 0;
            flex-wrap: wrap;
            gap: 1rem;
        ">
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 1rem;
                border-radius: 10px;
                backdrop-filter: blur(10px);
                min-width: 120px;
            ">
                <div style="font-size: 1.5rem; font-weight: 700;">#{ticket_id}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Número</div>
            </div>
            
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 1rem;
                border-radius: 10px;
                backdrop-filter: blur(10px);
                min-width: 120px;
            ">
                <div style="font-size: 1.5rem; font-weight: 700;">{position}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Posição</div>
            </div>
            
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 1rem;
                border-radius: 10px;
                backdrop-filter: blur(10px);
                min-width: 120px;
            ">
                <div style="font-size: 1.5rem; font-weight: 700;">⏱️</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">{status}</div>
            </div>
        </div>
        
        <p style="margin: 0; opacity: 0.9;">
            Você receberá atualizações por e-mail sobre o andamento do seu ticket.
        </p>
    </div>
    
    <style>
    @keyframes ticketPulse {{
        0% {{ transform: scale(0.95); opacity: 0; }}
        50% {{ transform: scale(1.02); }}
        100% {{ transform: scale(1); opacity: 1; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def render_loading_animation(text="Carregando..."):
    """Renderiza animação de loading personalizada"""
    st.markdown(f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    ">
        <div style="
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
        "></div>
        <p style="color: #667eea; font-weight: 500;">{text}</p>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

