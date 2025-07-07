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
from styles_mavi_updated import apply_custom_styling, get_custom_components
from config.config import app_config, email_config, sms_config
from auth import require_login, show_user_info, has_permission, AuthManager

# Configuração da página
st.set_page_config(
    page_title="Mavi Suporte",
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

def main():
    """Função principal do aplicativo"""
    
    # Verifica se o usuário está logado
    if not require_login():
        return
    
    # Inicializa componentes
    fila_manager, email_notifier, sms_notifier, report_generator = init_components()
    
    # Header customizado
    components = get_custom_components()
    st.markdown(components['header'], unsafe_allow_html=True)
    
    # Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Carrega e exibe o logo da Mavi
        import base64
        import os
        
        logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'mavi.logo.png')
        
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                logo_base64 = base64.b64encode(img_file.read()).decode()
            
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <img src="data:image/png;base64,{logo_base64}" style="height: 60px;" alt="Mavi Logo">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write("🎯 **Logo Mavi**")
    
    # Sidebar para navegação
    with st.sidebar:
        st.title("📋 Menu")
        
        # Opções baseadas nas permissões do usuário
        menu_options = []
        
        if has_permission('create_ticket'):
            menu_options.append("🎫 Nova Solicitação")
        
        if has_permission('view_dashboard'):
            menu_options.append("📊 Dashboard")
        
        if has_permission('view_reports'):
            menu_options.append("📈 Relatórios")
        
        if has_permission('manage_system'):
            menu_options.append("⚙️ Administração")
        
        page = st.selectbox("Selecione uma opção:", menu_options)
        
        # Exibe informações do usuário
        show_user_info()
    
    # Roteamento de páginas
    if page == "🎫 Nova Solicitação":
        page_nova_solicitacao(fila_manager, email_notifier, sms_notifier)
    elif page == "📊 Dashboard":
        page_dashboard(fila_manager)
    elif page == "📈 Relatórios":
        page_relatorios(report_generator)
    elif page == "⚙️ Administração":
        page_administracao(fila_manager, email_notifier)

def page_nova_solicitacao(fila_manager, email_notifier, sms_notifier):
    """Página para criar nova solicitação em formato de funil"""
    st.markdown(get_custom_components()['form_container_start'], unsafe_allow_html=True)
    
    st.subheader("📝 Nova Solicitação de Suporte")
    st.write("Preencha os dados abaixo para criar sua solicitação:")

    # Inicializa o estado do funil
    if 'form_step' not in st.session_state:
        st.session_state.form_step = 0

    # Define os passos do funil
    steps = [
        "Informações Pessoais",
        "Detalhes da Solicitação",
        "Confirmação"
    ]

    # Exibe o progresso
    st.progress((st.session_state.form_step + 1) / len(steps), text=f"Passo {st.session_state.form_step + 1} de {len(steps)}: {steps[st.session_state.form_step]}")

    with st.form("suporte_form", clear_on_submit=False):
        if st.session_state.form_step == 0:
            st.write("### 1. Suas Informações")
            st.session_state.data_solicitacao = st.date_input(
                "📅 Data da Solicitação",
                value=st.session_state.get('data_solicitacao', date.today()),
                help="Data em que a solicitação está sendo feita"
            )
            st.session_state.nome = st.text_input(
                "👤 Nome Completo",
                placeholder="Digite seu nome completo",
                value=st.session_state.get('nome', '')
            )
            st.session_state.email = st.text_input(
                "📧 E-mail",
                placeholder="seu.email@empresa.com",
                value=st.session_state.get('email', '')
            )
            st.session_state.telefone = st.text_input(
                "📱 Telefone (opcional)",
                placeholder="+55 (11) 99999-9999",
                help="Para receber notificações por SMS",
                value=st.session_state.get('telefone', '')
            )
            if st.form_submit_button("Próximo"): # type: ignore
                if not st.session_state.nome or not st.session_state.email:
                    st.error("❌ Por favor, preencha Nome Completo e E-mail.")
                else:
                    st.session_state.form_step = 1
                    st.rerun()

        elif st.session_state.form_step == 1:
            st.write("### 2. Detalhes da Solicitação")
            st.session_state.squad_leader = st.text_input(
                "👥 Squad Leader",
                placeholder="Nome do seu squad leader",
                value=st.session_state.get('squad_leader', '')
            )
            st.session_state.prioridade = st.selectbox(
                "⚡ Prioridade",
                ["Normal", "Alta", "Urgente"],
                index=["Normal", "Alta", "Urgente"].index(st.session_state.get('prioridade', 'Normal')),
                help="Selecione a prioridade da sua solicitação"
            )
            st.session_state.dispositivos = st.multiselect(
                "💻 Dispositivos/Serviços Solicitados",
                app_config.dispositivos_opcoes,
                default=st.session_state.get('dispositivos', []),
                help="Selecione um ou mais itens"
            )
            st.session_state.necessidade = st.text_area(
                "📋 Descrição Detalhada da Necessidade",
                placeholder="Descreva detalhadamente sua necessidade, incluindo contexto e urgência...",
                height=100,
                value=st.session_state.get('necessidade', '')
            )
            col_prev, col_next = st.columns(2)
            with col_prev:
                if st.form_submit_button("Anterior"): # type: ignore
                    st.session_state.form_step = 0
                    st.rerun()
            with col_next:
                if st.form_submit_button("Próximo"): # type: ignore
                    if not st.session_state.squad_leader or not st.session_state.dispositivos:
                        st.error("❌ Por favor, preencha Squad Leader e selecione os Dispositivos/Serviços Solicitados.")
                    else:
                        st.session_state.form_step = 2
                        st.rerun()

        elif st.session_state.form_step == 2:
            st.write("### 3. Confirmação")
            st.write(f"**Data da Solicitação:** {st.session_state.data_solicitacao.strftime('%Y-%m-%d')}")
            st.write(f"**Nome Completo:** {st.session_state.nome}")
            st.write(f"**E-mail:** {st.session_state.email}")
            st.write(f"**Telefone:** {st.session_state.telefone if st.session_state.telefone else 'Não informado'}")
            st.write(f"**Squad Leader:** {st.session_state.squad_leader}")
            st.write(f"**Prioridade:** {st.session_state.prioridade}")
            st.write(f"**Dispositivos/Serviços:** {', '.join(st.session_state.dispositivos)}")
            st.write(f"**Descrição:** {st.session_state.necessidade}")

            st.session_state.aceita_termos = st.checkbox(
                "Aceito que meus dados sejam utilizados para processamento da solicitação",
                value=st.session_state.get('aceita_termos', False)
            )

            col_prev, col_submit = st.columns(2)
            with col_prev:
                if st.form_submit_button("Anterior"): # type: ignore
                    st.session_state.form_step = 1
                    st.rerun()
            with col_submit:
                submitted = st.form_submit_button("🚀 Enviar Solicitação")

                if submitted:
                    if not st.session_state.aceita_termos:
                        st.error("❌ Por favor, aceite os termos para enviar a solicitação.")
                    else:
                        # Prepara dados
                        dados_solicitacao = {
                            'data_solicitacao': st.session_state.data_solicitacao.strftime("%Y-%m-%d"),
                            'nome': st.session_state.nome,
                            'email': st.session_state.email,
                            'telefone': st.session_state.telefone,
                            'squad_leader': st.session_state.squad_leader,
                            'dispositivos': ', '.join(st.session_state.dispositivos),
                            'necessidade': st.session_state.necessidade,
                            'prioridade': st.session_state.prioridade
                        }
                        
                        # Adiciona à fila
                        ticket_id = fila_manager.adicionar_solicitacao(dados_solicitacao)
                        posicao_fila = fila_manager.obter_posicao_fila(ticket_id)
                        
                        # Exibe sucesso com destaque
                        st.balloons()
                        st.success(f"✅ Solicitação criada com sucesso!")
                        
                        # Container destacado para o ticket
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 20px;
                            border-radius: 15px;
                            margin: 20px 0;
                            text-align: center;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                        ">
                            <h2 style="margin: 0; font-size: 28px;">🎫 TICKET GERADO</h2>
                            <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">#{}</h1>
                            <p style="margin: 0; font-size: 18px; opacity: 0.9;">Guarde este número para acompanhar sua solicitação</p>
                        </div>
                        """.format(ticket_id), unsafe_allow_html=True)
                        
                        # Métricas do ticket
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🎫 Ticket", f"#{ticket_id}")
                        with col2:
                            st.metric("📍 Posição na Fila", posicao_fila)
                        with col3:
                            st.metric("⏱️ Status", "Pendente")
                        
                        # Progress bar
                        progress_value = min(posicao_fila / app_config.max_fila_size, 1.0)
                        st.progress(1 - progress_value)
                        st.caption(f"Sua solicitação está na posição {posicao_fila} da fila")
                        
                        # Envio de notificações
                        with st.spinner("📧 Enviando notificações..."):
                            # Email
                            email_enviado = email_notifier.enviar_confirmacao_ticket(
                                st.session_state.email, ticket_id, posicao_fila
                            )
                            
                            # SMS (se telefone fornecido)
                            sms_enviado = False
                            if st.session_state.telefone:
                                sms_enviado = sms_notifier.enviar_sms_ticket(
                                    st.session_state.telefone, ticket_id, posicao_fila
                                )
                        
                        # Status das notificações com ícones e cores
                        st.markdown("### 📬 Status das Notificações")
                        
                        col_email, col_sms = st.columns(2)
                        
                        with col_email:
                            if email_enviado:
                                st.markdown("""
                                <div style="
                                    background: #d4edda;
                                    border: 1px solid #c3e6cb;
                                    color: #155724;
                                    padding: 15px;
                                    border-radius: 8px;
                                    text-align: center;
                                ">
                                    <h4 style="margin: 0;">📧 E-mail</h4>
                                    <p style="margin: 5px 0 0 0;"><strong>✅ Enviado com sucesso!</strong></p>
                                    <small>Verifique sua caixa de entrada</small>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style="
                                    background: #f8d7da;
                                    border: 1px solid #f5c6cb;
                                    color: #721c24;
                                    padding: 15px;
                                    border-radius: 8px;
                                    text-align: center;
                                ">
                                    <h4 style="margin: 0;">📧 E-mail</h4>
                                    <p style="margin: 5px 0 0 0;"><strong>❌ Falha no envio</strong></p>
                                    <small>Verifique as configurações</small>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col_sms:
                            if st.session_state.telefone:
                                if sms_enviado:
                                    st.markdown("""
                                    <div style="
                                        background: #d4edda;
                                        border: 1px solid #c3e6cb;
                                        color: #155724;
                                        padding: 15px;
                                        border-radius: 8px;
                                        text-align: center;
                                    ">
                                        <h4 style="margin: 0;">📱 SMS</h4>
                                        <p style="margin: 5px 0 0 0;"><strong>✅ Enviado com sucesso!</strong></p>
                                        <small>Mensagem enviada para o celular</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                    <div style="
                                        background: #f8d7da;
                                        border: 1px solid #f5c6cb;
                                        color: #721c24;
                                        padding: 15px;
                                        border-radius: 8px;
                                        text-align: center;
                                    ">
                                        <h4 style="margin: 0;">📱 SMS</h4>
                                        <p style="margin: 5px 0 0 0;"><strong>❌ Falha no envio</strong></p>
                                        <small>Erro ao enviar SMS</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style="
                                    background: #e2e3e5;
                                    border: 1px solid #d6d8db;
                                    color: #383d41;
                                    padding: 15px;
                                    border-radius: 8px;
                                    text-align: center;
                                ">
                                    <h4 style="margin: 0;">📱 SMS</h4>
                                    <p style="margin: 5px 0 0 0;"><strong>➖ Não solicitado</strong></p>
                                    <small>Telefone não informado</small>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Limpa o estado do formulário para uma nova solicitação
                        st.session_state.form_step = 0
                        for key in ['data_solicitacao', 'nome', 'email', 'telefone', 'squad_leader', 'prioridade', 'dispositivos', 'necessidade', 'aceita_termos']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()

    st.markdown(get_custom_components()['form_container_end'], unsafe_allow_html=True)

def page_dashboard(fila_manager):
    """Página do dashboard com estatísticas"""
    st.subheader("📊 Dashboard de Suporte")
    
    # Obtém estatísticas
    stats = fila_manager.obter_estatisticas()
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📋 Total de Tickets",
            stats['total_solicitacoes'],
            help="Número total de solicitações registradas"
        )
    
    with col2:
        st.metric(
            "⏳ Pendentes",
            stats['pendentes'],
            help="Tickets aguardando atendimento"
        )
    
    with col3:
        st.metric(
            "🔄 Em Andamento",
            stats['em_andamento'],
            help="Tickets sendo processados"
        )
    
    with col4:
        st.metric(
            "✅ Concluídos",
            stats['concluidas'],
            help="Tickets finalizados"
        )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Status dos Tickets")
        if stats['total_solicitacoes'] > 0:
            chart_data = pd.DataFrame({
                'Status': ['Pendentes', 'Em Andamento', 'Concluídos'],
                'Quantidade': [stats['pendentes'], stats['em_andamento'], stats['concluidas']]
            })
            st.bar_chart(chart_data.set_index('Status'))
        else:
            st.info("Nenhum ticket registrado ainda.")
    
    with col2:
        st.subheader("💻 Dispositivos Mais Solicitados")
        if stats['dispositivos_mais_solicitados']:
            dispositivos_df = pd.DataFrame(
                list(stats['dispositivos_mais_solicitados'].items())[:5],
                columns=['Dispositivo', 'Quantidade']
            )
            st.bar_chart(dispositivos_df.set_index('Dispositivo'))
        else:
            st.info("Nenhum dispositivo solicitado ainda.")
    
    # Tabela de tickets recentes
    st.subheader("🕒 Tickets Recentes")
    df_completo = fila_manager.obter_dados_completos()
    
    if not df_completo.empty:
        # Controles de visualização
        col_controls1, col_controls2 = st.columns([3, 1])
        
        with col_controls1:
            st.write("**Configurações de Visualização:**")
        
        with col_controls2:
            # Botão para esconder/mostrar colunas
            if 'show_column_selector' not in st.session_state:
                st.session_state.show_column_selector = False
            
            if st.button("🔧 Configurar Colunas", key="toggle_columns"):
                st.session_state.show_column_selector = not st.session_state.show_column_selector
        
        # Seletor de colunas (aparece/desaparece)
        if st.session_state.show_column_selector:
            st.markdown("**Selecione as colunas para exibir:**")
            
            # Todas as colunas disponíveis
            colunas_disponiveis = {
                'id': 'ID',
                'nome': 'Nome',
                'email': 'E-mail',
                'telefone': 'Telefone',
                'squad_leader': 'Squad Leader',
                'dispositivos': 'Dispositivos',
                'necessidade': 'Necessidade',
                'status': 'Status',
                'prioridade': 'Prioridade',
                'data_criacao': 'Data Criação',
                'data_solicitacao': 'Data Solicitação',
                'data_conclusao': 'Data Conclusão',
                'observacoes': 'Observações'
            }
            
            # Colunas padrão selecionadas
            if 'selected_columns' not in st.session_state:
                st.session_state.selected_columns = ['id', 'nome', 'dispositivos', 'status', 'prioridade', 'data_criacao']
            
            # Checkboxes para seleção de colunas
            cols_per_row = 4
            col_keys = list(colunas_disponiveis.keys())
            
            for i in range(0, len(col_keys), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col_key in enumerate(col_keys[i:i+cols_per_row]):
                    if j < len(cols):
                        with cols[j]:
                            is_selected = col_key in st.session_state.selected_columns
                            if st.checkbox(colunas_disponiveis[col_key], value=is_selected, key=f"col_{col_key}"):
                                if col_key not in st.session_state.selected_columns:
                                    st.session_state.selected_columns.append(col_key)
                            else:
                                if col_key in st.session_state.selected_columns:
                                    st.session_state.selected_columns.remove(col_key)
            
            # Botões de ação rápida
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("✅ Selecionar Todas", key="select_all"):
                    st.session_state.selected_columns = list(colunas_disponiveis.keys())
                    st.rerun()
            with col_btn2:
                if st.button("❌ Desmarcar Todas", key="deselect_all"):
                    st.session_state.selected_columns = []
                    st.rerun()
            with col_btn3:
                if st.button("🔄 Padrão", key="default_columns"):
                    st.session_state.selected_columns = ['id', 'nome', 'dispositivos', 'status', 'prioridade', 'data_criacao']
                    st.rerun()
        
        # Mostra os 10 mais recentes
        df_recentes = df_completo.sort_values('data_criacao', ascending=False).head(10)
        
        # Seleciona colunas para exibição baseado na seleção do usuário
        if 'selected_columns' in st.session_state and st.session_state.selected_columns:
            colunas_exibicao = [col for col in st.session_state.selected_columns if col in df_recentes.columns]
        else:
            colunas_exibicao = ['id', 'nome', 'dispositivos', 'status', 'prioridade', 'data_criacao']
        
        if colunas_exibicao:
            df_display = df_recentes[colunas_exibicao].copy()
            
            # Renomeia colunas para exibição
            rename_map = {
                'id': 'ID',
                'nome': 'Nome',
                'email': 'E-mail',
                'telefone': 'Telefone',
                'squad_leader': 'Squad Leader',
                'dispositivos': 'Dispositivos',
                'necessidade': 'Necessidade',
                'status': 'Status',
                'prioridade': 'Prioridade',
                'data_criacao': 'Data Criação',
                'data_solicitacao': 'Data Solicitação',
                'data_conclusao': 'Data Conclusão',
                'observacoes': 'Observações'
            }
            
            df_display.columns = [rename_map.get(col, col) for col in df_display.columns]
            
            st.dataframe(df_display, use_container_width=True)
        else:
            st.warning("⚠️ Nenhuma coluna selecionada para exibição.")
    else:
        st.info("Nenhum ticket registrado ainda.")

def page_relatorios(report_generator):
    """Página de relatórios"""
    st.subheader("📈 Relatórios e Análises")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("🔧 Gerar Relatórios")
        
        if st.button("📊 Gerar Relatório Completo", use_container_width=True):
            with st.spinner("Gerando relatório..."):
                try:
                    resultado = report_generator.gerar_relatorio_completo()
                    
                    st.success("✅ Relatório gerado com sucesso!")
                    
                    # Links para download
                    if os.path.exists(resultado['relatorio_html']):
                        with open(resultado['relatorio_html'], 'rb') as f:
                            st.download_button(
                                "📄 Baixar Relatório HTML",
                                f.read(),
                                file_name=f"relatorio_mavi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                mime="text/html"
                            )
                    
                    # Exibe gráficos se existirem
                    for nome, caminho in resultado['graficos'].items():
                        if caminho and os.path.exists(caminho):
                            st.markdown(f"**{nome.title()}:** [Visualizar]({caminho})")
                
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatório: {str(e)}")
        
        if st.button("📊 Gráfico de Status", use_container_width=True):
            with st.spinner("Gerando gráfico..."):
                try:
                    caminho = report_generator.gerar_grafico_status()
                    if caminho:
                        st.success("✅ Gráfico gerado!")
                        st.markdown(f"[Visualizar Gráfico]({caminho})")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        if st.button("💻 Gráfico de Dispositivos", use_container_width=True):
            with st.spinner("Gerando gráfico..."):
                try:
                    caminho = report_generator.gerar_grafico_dispositivos()
                    if caminho:
                        st.success("✅ Gráfico gerado!")
                        st.markdown(f"[Visualizar Gráfico]({caminho})")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    with col1:
        st.subheader("📋 Dados Gerais")
        
        # Estatísticas gerais
        relatorio_geral = report_generator.gerar_relatorio_geral()
        
        # Exibe métricas
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("📊 Total de Tickets", relatorio_geral['total_tickets'])
            st.metric("⏳ Pendentes", relatorio_geral['pendentes'])
        
        with col_b:
            st.metric("🔄 Em Andamento", relatorio_geral['em_andamento'])
            st.metric("✅ Concluídos", relatorio_geral['concluidos'])
        
        with col_c:
            st.metric(
                "⏱️ Tempo Médio (horas)",
                f"{relatorio_geral['tempo_medio_resolucao_horas']:.1f}"
            )
        
        # Top dispositivos
        if relatorio_geral['dispositivos_mais_solicitados']:
            st.subheader("🏆 Top 5 Dispositivos")
            top_dispositivos = list(relatorio_geral['dispositivos_mais_solicitados'].items())[:5]
            
            for i, (dispositivo, count) in enumerate(top_dispositivos, 1):
                st.write(f"{i}. **{dispositivo}**: {count} solicitações")

def page_administracao(fila_manager, email_notifier):
    """Página de administração"""
    st.subheader("⚙️ Administração do Sistema")
    
    # Interface de administração
    tab1, tab2, tab3 = st.tabs(["🎫 Gerenciar Tickets", "📊 Dados", "⚙️ Configurações"])
    
    with tab1:
        st.subheader("Gerenciamento de Tickets")
        
        df_completo = fila_manager.obter_dados_completos()
        
        if not df_completo.empty:
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(
                    "Filtrar por Status",
                    ["Todos", "Pendente", "Em andamento", "Concluída"]
                )
            
            with col2:
                prioridade_filter = st.selectbox(
                    "Filtrar por Prioridade",
                    ["Todas", "Normal", "Alta", "Urgente"]
                )
            
            # Aplica filtros
            df_filtrado = df_completo.copy()
            
            if status_filter != "Todos":
                df_filtrado = df_filtrado[df_filtrado['status'] == status_filter]
            
            if prioridade_filter != "Todas":
                df_filtrado = df_filtrado[df_filtrado['prioridade'] == prioridade_filter]
            
            # Exibe tabela
            st.dataframe(df_filtrado, use_container_width=True)
            
            # Atualização de status
            st.subheader("Atualizar Status")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ticket_id = st.selectbox("Ticket ID", df_completo['id'].tolist())
            
            with col2:
                novo_status = st.selectbox("Novo Status", ["Pendente", "Em andamento", "Concluída"])
            
            with col3:
                observacoes = st.text_input("Observações")
            
            with col4:
                if st.button("Atualizar"):
                    if fila_manager.atualizar_status(ticket_id, novo_status, observacoes):
                        st.success("✅ Status atualizado!")
                        
                        # Envia notificação por email
                        ticket_data = df_completo[df_completo['id'] == ticket_id].iloc[0]
                        email_notifier.enviar_atualizacao_status(
                            ticket_data['email'], ticket_id, novo_status, observacoes
                        )
                        
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar status!")
        else:
            st.info("Nenhum ticket encontrado.")
    
    with tab2:
        st.subheader("Exportar Dados")
        
        df_completo = fila_manager.obter_dados_completos()
        
        if not df_completo.empty:
            # Botão de download CSV
            csv = df_completo.to_csv(index=False)
            st.download_button(
                "📥 Baixar dados em CSV",
                csv,
                file_name=f"tickets_mavi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Estatísticas
            st.subheader("Estatísticas dos Dados")
            st.write(f"**Total de registros:** {len(df_completo)}")
            st.write(f"**Período:** {df_completo['data_criacao'].min()} a {df_completo['data_criacao'].max()}")
        else:
            st.info("Nenhum dado para exportar.")
    
    with tab3:
        st.subheader("Configurações do Sistema")
        
        st.write("**Configurações de E-mail:**")
        st.code(f"""
Servidor SMTP: {email_config.smtp_server}
Porta: {email_config.smtp_port}
E-mail remetente: {email_config.sender_email}
        """)
        
        st.write("**Configurações da Aplicação:**")
        st.code(f"""
Arquivo da fila: {app_config.fila_file}
Diretório de relatórios: {app_config.relatorios_dir}
Tamanho máximo da fila: {app_config.max_fila_size}
        """)
        
        if st.button("🔄 Limpar Cache"):
            st.cache_resource.clear()
            st.success("✅ Cache limpo!")

if __name__ == "__main__":
    main()



