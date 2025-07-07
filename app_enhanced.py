import io
import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import sys

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import FilaManager
from notifications import EmailNotifier, SMSNotifier
from reports import ReportGenerator
from styles_mavi_updated import apply_custom_styling
from components import *
from config.config import app_config, email_config, sms_config

# Configuração da página
st.set_page_config(
    page_title="Mavi Suporte",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplica estilos customizados
apply_custom_styling()

# Inicializa componentes
@st.cache_resource
def init_components():
    """Inicializa os componentes do sistema"""
    fila_manager = FilaManager(app_config.fila_file)
    email_notifier = EmailNotifier(
        email_config.smtp_server,
        email_config.smtp_port,
        email_config.sender_email,
        email_config.sender_password
    )
    sms_notifier = SMSNotifier(
        sms_config.account_sid,
        sms_config.auth_token,
        sms_config.from_number
    )
    report_generator = ReportGenerator(
        app_config.fila_file,
        app_config.relatorios_dir
    )
    return fila_manager, email_notifier, sms_notifier, report_generator

# Inicializa componentes
fila_manager, email_notifier, sms_notifier, report_generator = init_components()

def main():
    """Função principal do aplicativo"""
    
    # Hero section
    render_hero_section()
    
    # Sidebar para navegação
    with st.sidebar:
        st.markdown("### 🧭 Navegação")
        page = st.selectbox(
            "Escolha uma opção:",
            ["🎫 Nova Solicitação", "📊 Dashboard", "📈 Relatórios", "⚙️ Administração"],
            label_visibility="collapsed"
        )
        
        # Estatísticas rápidas na sidebar
        st.markdown("---")
        st.markdown("### 📊 Resumo Rápido")
        stats = fila_manager.obter_estatisticas()
        
        st.metric("Total", stats['total_solicitacoes'])
        st.metric("Pendentes", stats['pendentes'])
        st.metric("Concluídos", stats['concluidas'])
    
    # Roteamento de páginas
    if page == "🎫 Nova Solicitação":
        page_nova_solicitacao()
    elif page == "📊 Dashboard":
        page_dashboard()
    elif page == "📈 Relatórios":
        page_relatorios()
    elif page == "⚙️ Administração":
        page_administracao()

def page_nova_solicitacao():
    """Página para criar nova solicitação com design aprimorado"""
    st.markdown("## 📝 Nova Solicitação de Suporte")
    
    # Instruções com design moderno
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0 0 0.5rem 0; color: #667eea;">💡 Como funciona</h4>
        <p style="margin: 0; color: #6c757d;">
            Preencha o formulário abaixo e receba um número de ticket único. 
            Você será notificado por e-mail sobre todas as atualizações do seu chamado.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("suporte_form", clear_on_submit=True):
        # Seção de informações pessoais
        st.markdown("### 👤 Informações Pessoais")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Nome Completo *",
                placeholder="Digite seu nome completo",
                help="Nome completo do solicitante"
            )
            
            email = st.text_input(
                "E-mail *",
                placeholder="seu.email@empresa.com",
                help="E-mail para receber notificações"
            )
        
        with col2:
            squad_leader = st.text_input(
                "Squad Leader *",
                placeholder="Nome do seu squad leader",
                help="Responsável pela sua equipe"
            )
            
            telefone = st.text_input(
                "Telefone",
                placeholder="+55 (11) 99999-9999",
                help="Opcional: Para receber notificações por SMS"
            )
        
        st.markdown("---")
        
        # Seção da solicitação
        st.markdown("### 🎯 Detalhes da Solicitação")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            data_solicitacao = st.date_input(
                "Data da Solicitação",
                value=date.today(),
                help="Data em que a solicitação está sendo feita"
            )
        
        with col2:
            prioridade = st.selectbox(
                "Prioridade",
                ["Normal", "Alta", "Urgente"],
                help="Selecione a prioridade da sua solicitação"
            )
        
        with col3:
            # Placeholder para futuras expansões
            st.write("")
        
        dispositivos = st.multiselect(
            "Dispositivos/Serviços Solicitados *",
            app_config.dispositivos_opcoes,
            help="Selecione um ou mais itens necessários"
        )
        
        necessidade = st.text_area(
            "Descrição Detalhada da Necessidade *",
            placeholder="Descreva detalhadamente sua necessidade, incluindo:\n• Contexto da solicitação\n• Urgência\n• Impacto no trabalho\n• Qualquer informação adicional relevante",
            height=120,
            help="Quanto mais detalhes, melhor poderemos atendê-lo"
        )
        
        st.markdown("---")
        
        # Termos e envio
        col1, col2 = st.columns([3, 1])
        
        with col1:
            aceita_termos = st.checkbox(
                "Aceito que meus dados sejam utilizados para processamento da solicitação e comunicação sobre o ticket",
                help="Seus dados serão utilizados apenas para o processamento desta solicitação"
            )
        
        with col2:
            submitted = st.form_submit_button(
                "🚀 Criar Ticket",
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            # Validação
            campos_obrigatorios = [nome, email, squad_leader, dispositivos]
            if not all(campos_obrigatorios) or not aceita_termos:
                st.error("❌ Por favor, preencha todos os campos obrigatórios (*) e aceite os termos.")
                return
            
            # Validação de email básica
            if "@" not in email or "." not in email:
                st.error("❌ Por favor, insira um e-mail válido.")
                return
            
            # Animação de loading
            with st.spinner("🎫 Criando seu ticket..."):
                # Prepara dados
                dados_solicitacao = {
                    'data_solicitacao': data_solicitacao.strftime("%Y-%m-%d"),
                    'nome': nome,
                    'email': email,
                    'telefone': telefone,
                    'squad_leader': squad_leader,
                    'dispositivos': ', '.join(dispositivos),
                    'necessidade': necessidade,
                    'prioridade': prioridade
                }
                
                # Adiciona à fila
                ticket_id = fila_manager.adicionar_solicitacao(dados_solicitacao)
                posicao_fila = fila_manager.obter_posicao_fila(ticket_id)
            
            # Renderiza card do ticket
            render_ticket_card(ticket_id, posicao_fila, "Pendente")
            
            # Progress bar animado
            progress_percentage = max(0, min(100, 100 - (posicao_fila / app_config.max_fila_size * 100)))
            st.progress(progress_percentage / 100)
            st.caption(f"📍 Sua posição na fila: {posicao_fila} de {app_config.max_fila_size}")
            
            # Envio de notificações
            with st.spinner("📧 Enviando notificações..."):
                # Email
                email_enviado = email_notifier.enviar_confirmacao_ticket(
                    email, ticket_id, posicao_fila
                )
                
                # SMS (se telefone fornecido)
                sms_enviado = False
                if telefone:
                    sms_enviado = sms_notifier.enviar_sms_ticket(
                        telefone, ticket_id, posicao_fila
                    )
            
            # Status das notificações
            render_notification_status(email_enviado, sms_enviado, bool(telefone))
            
            # Próximos passos
            st.markdown("""
            <div style="
                background: #e7f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 10px;
                padding: 1.5rem;
                margin: 1rem 0;
            ">
                <h4 style="color: #0066cc; margin: 0 0 1rem 0;">📋 Próximos Passos</h4>
                <ul style="margin: 0; color: #004499;">
                    <li>Guarde o número do seu ticket: <strong>#{}</strong></li>
                    <li>Você receberá atualizações por e-mail</li>
                    <li>Acompanhe o status no Dashboard</li>
                    <li>Em caso de urgência, entre em contato com seu Squad Leader</li>
                </ul>
            </div>
            """.format(ticket_id), unsafe_allow_html=True)

def page_dashboard():
    """Dashboard com visualizações aprimoradas"""
    st.markdown("## 📊 Dashboard de Suporte")
    
    # Obtém estatísticas
    stats = fila_manager.obter_estatisticas()
    
    # Cards de estatísticas animados
    render_stats_cards(stats)
    
    st.markdown("---")
    
    # Gráficos lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Evolução dos Tickets")
        df_completo = fila_manager.obter_dados_completos()
        
        if not df_completo.empty:
            timeline_fig = render_timeline_chart(df_completo)
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True)
        else:
            st.info("📊 Dados insuficientes para gerar gráfico de timeline")
    
    with col2:
        st.markdown("### 💻 Dispositivos Populares")
        if stats['dispositivos_mais_solicitados']:
            device_fig = render_device_chart(stats['dispositivos_mais_solicitados'])
            if device_fig:
                st.plotly_chart(device_fig, use_container_width=True)
        else:
            st.info("📊 Nenhum dispositivo solicitado ainda")
    
    st.markdown("---")
    
    # Tabela de tickets com filtros
    st.markdown("### 🎫 Tickets Recentes")
    
    if not df_completo.empty:
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Status",
                ["Todos"] + df_completo['status'].unique().tolist()
            )
        
        with col2:
            prioridade_filter = st.selectbox(
                "Prioridade", 
                ["Todas"] + df_completo['prioridade'].unique().tolist()
            )
        
        with col3:
            limit = st.selectbox("Mostrar", [10, 25, 50, 100])
        
        # Aplica filtros
        df_filtrado = df_completo.copy()
        
        if status_filter != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == status_filter]
        
        if prioridade_filter != "Todas":
            df_filtrado = df_filtrado[df_filtrado['prioridade'] == prioridade_filter]
        
        # Ordena e limita
        df_display = df_filtrado.sort_values('data_criacao', ascending=False).head(limit)
        
        # Seleciona colunas para exibição
        colunas_exibicao = ['id', 'nome', 'dispositivos', 'status', 'prioridade', 'data_criacao']
        df_show = df_display[colunas_exibicao].copy()
        
        # Renomeia colunas
        df_show.columns = ['🎫 ID', '👤 Nome', '💻 Dispositivos', '📊 Status', '⚡ Prioridade', '📅 Data']
        
        st.dataframe(df_show, use_container_width=True, height=400)
    else:
        st.info("📋 Nenhum ticket registrado ainda")

def page_relatorios():
    """Página de relatórios aprimorada"""
    st.markdown("## 📈 Relatórios e Análises")
    
    # Tabs para organizar relatórios
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "📈 Gráficos", "📄 Exportar"])
    
    with tab1:
        # Relatório geral
        relatorio_geral = report_generator.gerar_relatorio_geral()
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_data = [
            ("📋", "Total de Tickets", relatorio_geral['total_tickets']),
            ("⏳", "Pendentes", relatorio_geral['pendentes']),
            ("🔄", "Em Andamento", relatorio_geral['em_andamento']),
            ("✅", "Concluídos", relatorio_geral['concluidos'])
        ]
        
        for i, (icon, label, value) in enumerate(metrics_data):
            with [col1, col2, col3, col4][i]:
                st.metric(f"{icon} {label}", value)
        
        # Tempo médio de resolução
        st.markdown("### ⏱️ Performance")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Tempo Médio de Resolução",
                f"{relatorio_geral['tempo_medio_resolucao_horas']:.1f} horas"
            )
        
        with col2:
            # Taxa de conclusão
            total = relatorio_geral['total_tickets']
            concluidos = relatorio_geral['concluidos']
            taxa_conclusao = (concluidos / total * 100) if total > 0 else 0
            st.metric("Taxa de Conclusão", f"{taxa_conclusao:.1f}%")
        
        # Top dispositivos
        if relatorio_geral['dispositivos_mais_solicitados']:
            st.markdown("### 🏆 Top 10 Dispositivos Mais Solicitados")
            
            top_dispositivos = list(relatorio_geral['dispositivos_mais_solicitados'].items())[:10]
            
            for i, (dispositivo, count) in enumerate(top_dispositivos, 1):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{i}. {dispositivo}**")
                with col2:
                    st.write(f"{count} solicitações")
    
    with tab2:
        st.markdown("### 📊 Gerar Gráficos Interativos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Gráfico de Status", use_container_width=True):
                with st.spinner("Gerando gráfico..."):
                    try:
                        # Obtém dados e gera gráfico diretamente
                        df_completo = fila_manager.obter_dados_completos()
                        if not df_completo.empty:
                            status_counts = df_completo['status'].value_counts()
                            
                            import plotly.express as px
                            fig = px.pie(
                                values=status_counts.values,
                                names=status_counts.index,
                                title="📊 Distribuição de Tickets por Status",
                                color_discrete_map={
                                    'Pendente': '#ffc107',
                                    'Em andamento': '#17a2b8',
                                    'Concluída': '#28a745'
                                }
                            )
                            
                            fig.update_layout(
                                font=dict(size=14),
                                title_font_size=18,
                                showlegend=True
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("📊 Nenhum dado disponível para gráfico")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
            
            if st.button("📈 Gráfico Timeline", use_container_width=True):
                with st.spinner("Gerando gráfico..."):
                    try:
                        df_completo = fila_manager.obter_dados_completos()
                        if not df_completo.empty:
                            # Prepara dados para timeline
                            df_completo['data_criacao'] = pd.to_datetime(df_completo['data_criacao'])
                            df_timeline = df_completo.groupby([df_completo['data_criacao'].dt.date, 'status']).size().reset_index(name='count')
                            
                            import plotly.express as px
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
                                yaxis_title="Número de Tickets"
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("📈 Nenhum dado disponível para timeline")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
        
        with col2:
            if st.button("💻 Gráfico de Dispositivos", use_container_width=True):
                with st.spinner("Gerando gráfico..."):
                    try:
                        stats = fila_manager.obter_estatisticas()
                        if stats['dispositivos_mais_solicitados']:
                            # Prepara dados
                            items = list(stats['dispositivos_mais_solicitados'].items())[:8]  # Top 8
                            dispositivos, counts = zip(*items)
                            
                            import plotly.graph_objects as go
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
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("💻 Nenhum dispositivo solicitado ainda")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
            
            if st.button("📄 Relatório Completo", use_container_width=True):
                with st.spinner("Gerando relatório completo..."):
                    try:
                        resultado = report_generator.gerar_relatorio_completo()
                        st.success("✅ Relatório completo gerado!")
                        
                        if os.path.exists(resultado['relatorio_html']):
                            with open(resultado['relatorio_html'], 'rb') as f:
                                st.download_button(
                                    "📄 Baixar Relatório HTML",
                                    f.read(),
                                    file_name=f"relatorio_mavi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                    mime="text/html",
                                    use_container_width=True
                                )
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
    
    with tab3:
        st.markdown("### 📥 Exportar Dados")
        
        df_completo = fila_manager.obter_dados_completos()
        
        if not df_completo.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Exportar CSV
                csv = df_completo.to_csv(index=False)
                st.download_button(
                    "📊 Baixar CSV",
                    csv,
                    file_name=f"tickets_mavi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Exportar Excel
                try:
                    excel_buffer = io.BytesIO()
                    df_completo.to_excel(excel_buffer, index=False)
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        "📈 Baixar Excel",
                        excel_buffer.getvalue(),
                        file_name=f"tickets_mavi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except ImportError:
                    st.info("📝 Excel export requer openpyxl")
            
            # Informações sobre os dados
            st.markdown("### 📋 Informações dos Dados")
            st.write(f"**Total de registros:** {len(df_completo)}")
            if not df_completo.empty:
                st.write(f"**Período:** {df_completo['data_criacao'].min()} a {df_completo['data_criacao'].max()}")
        else:
            st.info("📋 Nenhum dado para exportar")

def page_administracao():
    """Página de administração aprimorada"""
    st.markdown("## ⚙️ Administração do Sistema")
    
    # Autenticação
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 2rem 0;
        ">
            <h3 style="color: #667eea; margin: 0 0 1rem 0;">🔐 Acesso Restrito</h3>
            <p style="color: #6c757d; margin: 0;">Esta área é restrita a administradores do sistema.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            senha = st.text_input("🔐 Senha de Administrador", type="password")
            if st.button("Entrar", use_container_width=True):
                if senha == "mavi2024":  # Senha para demonstração
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        return
    
    # Interface de administração
    tab1, tab2, tab3, tab4 = st.tabs(["🎫 Tickets", "📊 Dados", "⚙️ Config", "👤 Usuários"])
    
    with tab1:
        st.markdown("### 🎫 Gerenciamento de Tickets")
        
        df_completo = fila_manager.obter_dados_completos()
        
        if not df_completo.empty:
            # Filtros avançados
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status_filter = st.selectbox(
                    "Status",
                    ["Todos", "Pendente", "Em andamento", "Concluída"]
                )
            
            with col2:
                prioridade_filter = st.selectbox(
                    "Prioridade",
                    ["Todas", "Normal", "Alta", "Urgente"]
                )
            
            with col3:
                # Filtro por data
                data_inicio = st.date_input("Data início", value=None)
            
            with col4:
                data_fim = st.date_input("Data fim", value=None)
            
            # Aplica filtros
            df_filtrado = df_completo.copy()
            
            if status_filter != "Todos":
                df_filtrado = df_filtrado[df_filtrado['status'] == status_filter]
            
            if prioridade_filter != "Todas":
                df_filtrado = df_filtrado[df_filtrado['prioridade'] == prioridade_filter]
            
            # Exibe tabela filtrada
            st.dataframe(df_filtrado, use_container_width=True, height=400)
            
            # Atualização em lote
            st.markdown("### 🔄 Atualização de Status")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ticket_id = st.selectbox("Ticket ID", df_completo['id'].tolist())
            
            with col2:
                novo_status = st.selectbox("Novo Status", ["Pendente", "Em andamento", "Concluída"])
            
            with col3:
                observacoes = st.text_input("Observações")
            
            with col4:
                if st.button("✅ Atualizar", use_container_width=True):
                    if fila_manager.atualizar_status(ticket_id, novo_status, observacoes):
                        st.success("✅ Status atualizado!")
                        
                        # Notificação por email
                        ticket_data = df_completo[df_completo['id'] == ticket_id].iloc[0]
                        email_notifier.enviar_atualizacao_status(
                            ticket_data['email'], ticket_id, novo_status, observacoes
                        )
                        
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar!")
        else:
            st.info("📋 Nenhum ticket encontrado")
    
    with tab2:
        st.markdown("### 📊 Análise de Dados")
        
        df_completo = fila_manager.obter_dados_completos()
        
        if not df_completo.empty:
            # Estatísticas avançadas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Tickets", len(df_completo))
                st.metric("Usuários Únicos", df_completo['email'].nunique())
            
            with col2:
                # Tickets por dia (média)
                df_completo['data_criacao'] = pd.to_datetime(df_completo['data_criacao'])
                tickets_por_dia = df_completo.groupby(df_completo['data_criacao'].dt.date).size()
                media_diaria = tickets_por_dia.mean() if not tickets_por_dia.empty else 0
                st.metric("Média Diária", f"{media_diaria:.1f}")
                
                # Squad Leaders mais ativos
                squad_counts = df_completo['squad_leader'].value_counts()
                top_squad = squad_counts.index[0] if not squad_counts.empty else "N/A"
                st.metric("Top Squad Leader", top_squad)
            
            with col3:
                # Exportação
                csv = df_completo.to_csv(index=False)
                st.download_button(
                    "📥 Exportar CSV",
                    csv,
                    file_name=f"admin_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Backup
                if st.button("💾 Backup", use_container_width=True):
                    backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    df_completo.to_csv(f"data/{backup_file}", index=False)
                    st.success(f"✅ Backup criado: {backup_file}")
        else:
            st.info("📊 Nenhum dado disponível")
    
    with tab3:
        st.markdown("### ⚙️ Configurações do Sistema")
        
        # Configurações de email
        with st.expander("📧 Configurações de E-mail"):
            st.code(f"""
Servidor SMTP: {email_config.smtp_server}
Porta: {email_config.smtp_port}
E-mail remetente: {email_config.sender_email}
Status: {'✅ Configurado' if email_config.sender_password else '❌ Não configurado'}
            """)
        
        # Configurações de SMS
        with st.expander("📱 Configurações de SMS"):
            st.code(f"""
Provedor: Twilio
Account SID: {sms_config.account_sid[:10]}... (oculto)
Status: {'✅ Configurado' if sms_config.account_sid else '❌ Não configurado'}
            """)
        
        # Configurações da aplicação
        with st.expander("🔧 Configurações da Aplicação"):
            st.code(f"""
Arquivo da fila: {app_config.fila_file}
Diretório de relatórios: {app_config.relatorios_dir}
Tamanho máximo da fila: {app_config.max_fila_size}
Dispositivos disponíveis: {len(app_config.dispositivos_opcoes)}
            """)
        
        # Ações de sistema
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Limpar Cache", use_container_width=True):
                st.cache_resource.clear()
                st.success("✅ Cache limpo!")
        
        with col2:
            if st.button("📊 Recarregar Dados", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.rerun()
    
    with tab4:
        st.markdown("### 👤 Gestão de Usuários")
        
        df_completo = fila_manager.obter_dados_completos()
        
        if not df_completo.empty:
            # Usuários mais ativos
            user_stats = df_completo.groupby('email').agg({
                'id': 'count',
                'data_criacao': 'max',
                'nome': 'first'
            }).rename(columns={'id': 'total_tickets', 'data_criacao': 'ultimo_ticket'})
            
            user_stats = user_stats.sort_values('total_tickets', ascending=False)
            
            st.markdown("#### 🏆 Usuários Mais Ativos")
            st.dataframe(user_stats.head(10), use_container_width=True)
            
            # Squad Leaders
            squad_stats = df_completo.groupby('squad_leader').agg({
                'id': 'count',
                'email': 'nunique'
            }).rename(columns={'id': 'total_tickets', 'email': 'usuarios_unicos'})
            
            squad_stats = squad_stats.sort_values('total_tickets', ascending=False)
            
            st.markdown("#### 👥 Squad Leaders")
            st.dataframe(squad_stats, use_container_width=True)
        else:
            st.info("👤 Nenhum usuário registrado ainda")

if __name__ == "__main__":
    main()

