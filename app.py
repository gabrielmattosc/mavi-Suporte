"""
Sistema de Suporte Mavi - Streamlit
Aplicação principal do sistema de gerenciamento de tickets
"""
import base64
from io import BytesIO
from tkinter import Image
import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from database import get_database_managers
from admin import show_admin_page
from email_service import get_email_service
from reports import get_report_generator
from typing import Dict, Any
from PIL import Image as PilImage

# Configuração da página
st.set_page_config(
    page_title="Mavi Suporte",
    page_icon="mavi.logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para o layout moderno da Mavi
def apply_custom_css():
    """Aplica CSS customizado com as cores da Mavi"""
    st.markdown("""
    <style>
    /* Cores principais da Mavi */
    :root {
        --mavi-green: #00D4AA;
        --mavi-dark-green: #00B894;
        --mavi-light-green: #00E5BB;
        --mavi-bg: #f8f9fa;
        --mavi-text: #2c3e50;
    }
    
    /* Header customizado */
    .main-header {
        background: linear-gradient(90deg, var(--mavi-green), var(--mavi-dark-green));
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Logo container */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1rem 0;
    }
    
    /* Cards customizados */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid var(--mavi-green);
        margin: 0.5rem 0;
    }
    
    /* Formulário */
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Botões customizados */
    .stButton > button {
        background: linear-gradient(90deg, var(--mavi-green), var(--mavi-dark-green));
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, var(--mavi-dark-green), var(--mavi-green));
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--mavi-light-green), var(--mavi-green));
    }
    
    /* Métricas */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Alertas de sucesso */
    .success-alert {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Tabelas */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Progress bar customizada */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--mavi-green), var(--mavi-dark-green));
    }
    
    /* Esconder elementos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header {
            padding: 0.5rem;
        }
        
        .form-container {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """Exibe o cabeçalho principal"""
# --- CARREGAMENTO DA IMAGEM E CONVERSÃO ---
try:
    # Use o novo nome 'PilImage' para abrir o arquivo
    img = PilImage.open("mavi.logo.png")
    
    # O resto do seu código continua igual
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

except FileNotFoundError:
    st.error("Arquivo 'mavi.logo.png' não encontrado. Verifique se o nome e o local estão corretos.")
    st.stop()


# --- CÓDIGO PARA CENTRALIZAR A IMAGEM COM HTML/CSS ---
st.markdown(f"""
<div style="display: flex; justify-content: center;">
    <img src="data:image/png;base64,{img_str}" alt="Mavi Logo" width="300">
</div>
""", unsafe_allow_html=True)

def init_session_state():
    """Inicializa o estado da sessão"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Início"

def show_login_page():
    """Exibe a página de login"""
    show_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Usuário", placeholder="Digite seu usuário")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            
            col_a, col_b = st.columns(2)
            with col_a:
                login_button = st.form_submit_button("Entrar", use_container_width=True)
            
            if login_button and username and password:
                # Obtém gerenciadores
                _, _, user_manager = get_database_managers()
                
                # Autentica usuário
                user = user_manager.autenticar_usuario(username, password)
                
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success(f"✅ Bem-vindo, {user['username']}!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_navigation():
    """Exibe a navegação lateral de forma reativa."""
    with st.sidebar:
        st.markdown(f"### 👋 Olá, {st.session_state.user['username']}!")
        
        pages = []
        if st.session_state.user['role'] == 'admin':
            pages = [
                "🏠 Início", "🎫 Nova Solicitação", "🔍 Consultar Ticket",
                "📊 Dashboard", "📈 Relatórios", "⚙️ Administração"
            ]
        elif st.session_state.user['role'] == 'user': 
            pages = ["🏠 Início", "🎫 Nova Solicitação", "🔍 Consultar Ticket"]
        
        try:
            current_page_index = pages.index(st.session_state.current_page)
        except ValueError:
            current_page_index = 0
            st.session_state.current_page = pages[0]
            
        selected_page = st.selectbox(
            "📋 Navegação", pages, index=current_page_index, key="navigation"
        )
        
        if selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
        **Perfil:** {st.session_state.user['role'].title()}  
        **Email:** {st.session_state.user['email']}
        """)
        
        if st.button("🚪 Sair", use_container_width=True):
            # --- CORREÇÃO APLICADA AQUI ---
            # Define quais chaves são relacionadas ao login do usuário
            keys_to_delete = ['authenticated', 'user', 'current_page']
            
            # Apaga apenas as chaves de login, preservando o "banco de dados"
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.rerun()
            # --- FIM DA CORREÇÃO ---

def show_home_page():
    """Exibe a página inicial com ações rápidas baseadas no perfil."""
    show_header()
    
    # --- Seção 1: Estatísticas Rápidas (permanece igual) ---
    _, ticket_manager, _ = get_database_managers()
    stats = ticket_manager.obter_estatisticas()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #00D4AA;">📋</h3>
            <h2>{stats['total_tickets']}</h2>
            <p>Total de Tickets</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #ffc107;">⏳</h3>
            <h2>{stats['pendentes']}</h2>
            <p>Pendentes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #17a2b8;">🔄</h3>
            <h2>{stats['em_andamento']}</h2>
            <p>Em Andamento</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #28a745;">✅</h3>
            <h2>{stats['concluidos']}</h2>
            <p>Concluídos</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---") # Adiciona um separador visual

    # --- Seção 2: Ações Rápidas (Lógica Corrigida e Integrada) ---
    # CORREÇÃO: A verificação agora usa st.session_state.user['role'], 
    # que é a forma correta segundo o seu sistema de login.

    # Exibição para o usuário ADMIN
    if st.session_state.user['role'] == 'admin':
        st.markdown("### 🚀 Ações Rápidas (Admin)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎫 Criar Novo Ticket", use_container_width=True, key='home_admin_new_ticket'):
                st.session_state.current_page = "🎫 Nova Solicitação"
                st.rerun()
        
        with col2:
            if st.button("🔍 Consultar Ticket", use_container_width=True, key='home_admin_consult_ticket'):
                st.session_state.current_page = "🔍 Consultar Ticket"
                st.rerun()
        
        with col3:
            if st.button("📊 Ver Dashboard", use_container_width=True, key='home_admin_dashboard'):
                st.session_state.current_page = "📊 Dashboard"
                st.rerun()
                
        # Informações completas para o admin
        st.markdown("### ℹ️ Sobre o Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **Sistema de Suporte Mavi**
            
            - ✅ Criação de tickets
            - ✅ Acompanhamento em tempo real
            - ✅ Relatórios e estatísticas
            - ✅ Notificações por email
            - ✅ Interface moderna e responsiva
            """)
        
        with col2:
            st.success("""
            **Como Usar:**
            
            1. 🎫 Crie uma nova solicitação
            2. 📧 Receba confirmação por email
            3. 🔍 Acompanhe o status do ticket
            4. 📊 Visualize estatísticas no dashboard
            5. ✅ Receba notificação quando concluído
            """)

    # Exibição para o usuário comum ('user')
    elif st.session_state.user['role'] == 'user':
        st.markdown("### 🚀 Ações Rápidas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎫 Criar Novo Ticket", use_container_width=True, key='home_user_new_ticket'):
                st.session_state.current_page = "🎫 Nova Solicitação"
                st.rerun()
        
        with col2:
            if st.button("🔍 Consultar Ticket", use_container_width=True, key='home_user_consult_ticket'):
                st.session_state.current_page = "🔍 Consultar Ticket"
                st.rerun()
                
        # Informações simplificadas para o usuário
        st.markdown("### ℹ️ Sobre o Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **Sistema de Suporte Mavi**
            
            - ✅ Criação de tickets
            - ✅ Acompanhamento em tempo real
            - ✅ Notificações por email
            - ✅ Interface moderna e responsiva
            """)
        
        with col2:
            st.success("""
            **Como Usar:**
            
            1. 🎫 Crie uma nova solicitação
            2. 📧 Receba confirmação por email
            3. 🔍 Acompanhe o status do ticket
            4. ✅ Receba notificação quando concluído
            """)

def show_new_ticket_page():
    """Exibe a página de nova solicitação"""
    st.subheader("🎫 Nova Solicitação de Suporte")
    
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # Dispositivos disponíveis
    dispositivos_opcoes = [
        "Notebook/Laptop",
        "Desktop/PC",
        "Teclado",
        "Mouse",
        "Headset/Fone",
        "Webcam",
        "Acesso VPN",
        "Software específico",
        "Licença de software",
        "Acesso ao Cubo",
        "Suporte técnico geral",
        "Bases",
        "Banco de Dados",
        "Outros"
    ]
    
    with st.form("ticket_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "👤 Nome Completo *",
                placeholder="Digite seu nome completo",
                value=st.session_state.get('form_nome', '')
            )
            
            email = st.text_input(
                "📧 E-mail *",
                placeholder="seu.email@empresa.com",
                value=st.session_state.get('form_email', '')
            )
            
            squad_leader = st.text_input(
                "👥 Squad Leader *",
                placeholder="Nome do seu squad leader",
                value=st.session_state.get('form_squad_leader', '')
            )
            
            prioridade = st.selectbox(
                "⚡ Prioridade *",
                ["Normal", "Alta", "Urgente"],
                index=["Normal", "Alta", "Urgente"].index(st.session_state.get('form_prioridade', 'Normal'))
            )
            
            dispositivos = st.multiselect(
                "💻 Dispositivos/Serviços Solicitados *",
                dispositivos_opcoes,
                default=st.session_state.get('form_dispositivos', [])
            )
        
        necessidade = st.text_area(
            "📋 Descrição Detalhada da Necessidade *",
            placeholder="Descreva detalhadamente sua necessidade, incluindo contexto e urgência...",
            height=120,
            value=st.session_state.get('form_necessidade', '')
        )
        
        aceita_termos = st.checkbox(
            "Aceito que meus dados sejam utilizados para processamento da solicitação *",
            value=st.session_state.get('form_aceita_termos', False)
        )
        
        submitted = st.form_submit_button("🚀 Enviar Solicitação", use_container_width=True)
        
        if submitted:
            # Salva dados no session_state para persistência
            st.session_state.form_nome = nome
            st.session_state.form_email = email
            st.session_state.form_squad_leader = squad_leader
            st.session_state.form_prioridade = prioridade
            st.session_state.form_dispositivos = dispositivos
            st.session_state.form_necessidade = necessidade
            st.session_state.form_aceita_termos = aceita_termos
            
            # Validação
            if not all([nome, email, squad_leader, dispositivos]) or not aceita_termos:
                st.error("❌ Por favor, preencha todos os campos obrigatórios e aceite os termos.")
            else:
                # Cria o ticket
                _, ticket_manager, _ = get_database_managers()
                
                dados_ticket = {
                    "nome": nome,
                    "email": email,
                    "squad_leader": squad_leader,
                    "dispositivos": ", ".join(dispositivos),
                    "necessidade": necessidade,
                    "prioridade": prioridade
                }
                
                ticket_id = ticket_manager.criar_ticket(dados_ticket)
                
                if ticket_id:
                    posicao_fila = ticket_manager.obter_posicao_fila(ticket_id)
                    
                    # Envia emails
                    email_service = get_email_service()
                    
                    if email_service.enabled:
                        # Email para o usuário
                        email_enviado = email_service.enviar_confirmacao_ticket(
                            email, ticket_id, posicao_fila, dados_ticket
                        )
                        
                        # Email para o admin
                        admin_notificado = email_service.enviar_notificacao_admin(
                            ticket_id, dados_ticket
                        )
                    else:
                        email_enviado = False
                        admin_notificado = False
                    
                    # Limpa o formulário
                    for key in ['form_nome', 'form_email', 'form_squad_leader', 
                               'form_prioridade', 'form_dispositivos', 'form_necessidade', 
                               'form_aceita_termos']:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.success("✅ Solicitação criada com sucesso!")
                    
                    # Exibe informações do ticket
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("🎫 Ticket", f"#{ticket_id}")
                    with col_b:
                        st.metric("📍 Posição na Fila", posicao_fila)
                    with col_c:
                        st.metric("⏱️ Status", "Pendente")
                    
                    # Progress bar
                    if posicao_fila > 0:
                        progress_value = max(0, min(1, (10 - posicao_fila) / 10))
                        st.progress(progress_value)
                        st.caption(f"Sua solicitação está na posição {posicao_fila} da fila")
                    
                    # Status dos emails
                    if email_service.enabled:
                        if email_enviado:
                            st.info("📧 Email de confirmação enviado!")
                        else:
                            st.warning("⚠️ Não foi possível enviar o email de confirmação")
                        
                        if admin_notificado:
                            st.info("🔔 Administrador notificado!")
                    else:
                        st.info("📧 Configure a senha do email para ativar notificações automáticas")
                    
                else:
                    st.error("❌ Erro ao criar solicitação. Tente novamente.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_search_ticket_page():
    """Exibe a página de consulta de ticket"""
    st.subheader("🔍 Consultar Ticket")
    
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.write("Digite o ID do seu ticket para consultar o status:")
        
        ticket_id = st.text_input(
            "🎫 ID do Ticket",
            placeholder="Ex: ABC12345",
            help="O ID do ticket foi enviado por email quando você criou a solicitação"
        ).upper()
        
        if st.button("🔍 Consultar", use_container_width=True):
            if ticket_id:
                _, ticket_manager, _ = get_database_managers()
                ticket = ticket_manager.obter_ticket(ticket_id)
                
                if ticket:
                    st.success(f"✅ Ticket #{ticket_id} encontrado!")
                    
                    # Informações do ticket
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**Informações do Ticket:**")
                        st.write(f"**ID:** #{ticket['ticket_id']}")
                        st.write(f"**Status:** {ticket['status']}")
                        st.write(f"**Prioridade:** {ticket['prioridade']}")
                        st.write(f"**Data:** {ticket['data_criacao'].strftime('%d/%m/%Y %H:%M')}")
                    
                    with col_b:
                        st.markdown("**Dados do Solicitante:**")
                        st.write(f"**Nome:** {ticket['nome']}")
                        st.write(f"**Email:** {ticket['email']}")
                        st.write(f"**Squad Leader:** {ticket['squad_leader']}")
                    
                    # Detalhes da solicitação
                    st.markdown("**Dispositivos/Serviços:**")
                    st.write(ticket['dispositivos'])
                    
                    st.markdown("**Descrição:**")
                    st.write(ticket['necessidade'])
                    
                    # Observações (se houver)
                    if ticket.get('observacoes'):
                        st.markdown("**Observações:**")
                        for obs in ticket['observacoes']:
                            st.write(f"- {obs['data'].strftime('%d/%m/%Y %H:%M')}: {obs['texto']}")
                    
                    # Posição na fila (se pendente)
                    if ticket['status'] == 'Pendente':
                        posicao = ticket_manager.obter_posicao_fila(ticket_id)
                        if posicao > 0:
                            st.info(f"📍 Posição na fila: {posicao}º")
                
                else:
                    st.error("❌ Ticket não encontrado. Verifique o ID e tente novamente.")
            else:
                st.warning("⚠️ Por favor, digite o ID do ticket.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard_page():
    """Exibe a página do dashboard"""
    st.subheader("📊 Dashboard de Suporte")
    
    _, ticket_manager, _ = get_database_managers()
    
    # Estatísticas
    stats = ticket_manager.obter_estatisticas()
    tickets = ticket_manager.listar_tickets()
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total de Tickets", stats['total_tickets'])
    with col2:
        st.metric("⏳ Pendentes", stats['pendentes'])
    with col3:
        st.metric("🔄 Em Andamento", stats['em_andamento'])
    with col4:
        st.metric("✅ Concluídos", stats['concluidos'])
    
    # Gráficos
    if stats['total_tickets'] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Status dos Tickets")
            
            # Gráfico de pizza para status
            status_data = {
                'Status': ['Pendentes', 'Em Andamento', 'Concluídos'],
                'Quantidade': [stats['pendentes'], stats['em_andamento'], stats['concluidos']]
            }
            
            fig_status = px.pie(
                values=status_data['Quantidade'],
                names=status_data['Status'],
                color_discrete_sequence=['#ffc107', '#17a2b8', '#28a745']
            )
            fig_status.update_layout(height=400)
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            st.subheader("💻 Top 5 Dispositivos")
            
            if stats['dispositivos_mais_solicitados']:
                # Gráfico de barras para dispositivos
                dispositivos_items = list(stats['dispositivos_mais_solicitados'].items())[:5]
                
                if dispositivos_items:
                    dispositivos_df = pd.DataFrame(
                        dispositivos_items,
                        columns=['Dispositivo', 'Quantidade']
                    )
                    
                    fig_dispositivos = px.bar(
                        dispositivos_df,
                        x='Quantidade',
                        y='Dispositivo',
                        orientation='h',
                        color_discrete_sequence=['#00D4AA']
                    )
                    fig_dispositivos.update_layout(height=400)
                    st.plotly_chart(fig_dispositivos, use_container_width=True)
                else:
                    st.info("Nenhum dispositivo solicitado ainda.")
            else:
                st.info("Nenhum dispositivo solicitado ainda.")
        
        # Timeline de tickets (se houver dados suficientes)
        if len(tickets) > 1:
            st.subheader("📅 Timeline de Criação de Tickets")
            
            # Agrupa tickets por data
            df_tickets = pd.DataFrame(tickets)
            df_tickets['data'] = pd.to_datetime(df_tickets['data_criacao']).dt.date
            timeline_data = df_tickets.groupby('data').size().reset_index(name='quantidade')
            
            fig_timeline = px.line(
                timeline_data,
                x='data',
                y='quantidade',
                title='Tickets criados por dia',
                color_discrete_sequence=['#00D4AA']
            )
            fig_timeline.update_layout(height=300)
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Tabela de tickets recentes
        st.subheader("🕒 Tickets Recentes")
        
        if tickets:
            # Prepara dados para exibição
            df_display = pd.DataFrame(tickets)
            df_display = df_display[['ticket_id', 'nome', 'status', 'prioridade', 'data_criacao']].head(10)
            df_display['data_criacao'] = pd.to_datetime(df_display['data_criacao']).dt.strftime('%d/%m/%Y %H:%M')
            df_display.columns = ['ID', 'Nome', 'Status', 'Prioridade', 'Data']
            
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("Nenhum ticket registrado ainda.")
    
    else:
        st.info("📊 Nenhum dado disponível ainda. Crie alguns tickets para ver as estatísticas!")

def main():
    """Função principal da aplicação"""
    # Aplica CSS customizado
    apply_custom_css()
    
    # Inicializa estado da sessão
    init_session_state()
    
    # Verifica autenticação
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Exibe navegação
    show_navigation()
    
    # Roteamento de páginas
    if st.session_state.current_page == "🏠 Início":
        show_home_page()
    elif st.session_state.current_page == "🎫 Nova Solicitação":
        show_new_ticket_page()
    elif st.session_state.current_page == "🔍 Consultar Ticket":
        show_search_ticket_page()
    elif st.session_state.current_page == "📊 Dashboard":
        show_dashboard_page()
    elif st.session_state.current_page == "📈 Relatórios":
        report_generator = get_report_generator()
        report_generator.show_reports_page()
    elif st.session_state.current_page == "⚙️ Administração":
        show_admin_page()

if __name__ == "__main__":
    main()

