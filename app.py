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

# Inicializa componentes
fila_manager, email_notifier, sms_notifier, report_generator = init_components()

def main():
    """Função principal do aplicativo"""
    
    # Header customizado
    components = get_custom_components()
    st.markdown(components['header'], unsafe_allow_html=True)
    
    # Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("https://i.imgur.com/L84xeQI.png", width=300)
        except:
            st.write("🎯 **Logo Mavi**")
    
    # Sidebar para navegação
    with st.sidebar:
        st.title("📋 Menu")
        page = st.selectbox(
            "Selecione uma opção:",
            ["🎫 Nova Solicitação", "📊 Dashboard", "📈 Relatórios", "⚙️ Administração"]
        )
    
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
    """Página para criar nova solicitação"""
    st.markdown(get_custom_components()['form_container_start'], unsafe_allow_html=True)
    
    st.subheader("📝 Nova Solicitação de Suporte")
    st.write("Preencha os dados abaixo para criar sua solicitação:")
    
    with st.form("suporte_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            data_solicitacao = st.date_input(
                "📅 Data da Solicitação",
                value=date.today(),
                help="Data em que a solicitação está sendo feita"
            )
            
            nome = st.text_input(
                "👤 Nome Completo",
                placeholder="Digite seu nome completo"
            )
            
            email = st.text_input(
                "📧 E-mail",
                placeholder="seu.email@empresa.com"
            )
            
            telefone = st.text_input(
                "📱 Telefone (opcional)",
                placeholder="+55 (11) 99999-9999",
                help="Para receber notificações por SMS"
            )
        
        with col2:
            squad_leader = st.text_input(
                "👥 Squad Leader",
                placeholder="Nome do seu squad leader"
            )
            
            prioridade = st.selectbox(
                "⚡ Prioridade",
                ["Normal", "Alta", "Urgente"],
                help="Selecione a prioridade da sua solicitação"
            )
            
            dispositivos = st.multiselect(
                "💻 Dispositivos/Serviços Solicitados",
                app_config.dispositivos_opcoes,
                help="Selecione um ou mais itens"
            )
        
        necessidade = st.text_area(
            "📋 Descrição Detalhada da Necessidade",
            placeholder="Descreva detalhadamente sua necessidade, incluindo contexto e urgência...",
            height=100
        )
        
        # Checkbox para aceitar termos
        aceita_termos = st.checkbox(
            "Aceito que meus dados sejam utilizados para processamento da solicitação"
        )
        
        submitted = st.form_submit_button("🚀 Enviar Solicitação")
        
        if submitted:
            if not all([nome, email, squad_leader, dispositivos]) or not aceita_termos:
                st.error("❌ Por favor, preencha todos os campos obrigatórios e aceite os termos.")
            else:
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
                
                # Exibe sucesso
                st.success(f"✅ Solicitação criada com sucesso!")
                
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
                        email, ticket_id, posicao_fila
                    )
                    
                    # SMS (se telefone fornecido)
                    sms_enviado = False
                    if telefone:
                        sms_enviado = sms_notifier.enviar_sms_ticket(
                            telefone, ticket_id, posicao_fila
                        )
                
                # Status das notificações
                if email_enviado:
                    st.info("📧 E-mail de confirmação enviado!")
                else:
                    st.warning("⚠️ Não foi possível enviar o e-mail. Verifique as configurações.")
                
                if telefone and sms_enviado:
                    st.info("📱 SMS de confirmação enviado!")
                elif telefone and not sms_enviado:
                    st.warning("⚠️ Não foi possível enviar o SMS.")
    
    st.markdown(get_custom_components()['form_container_end'], unsafe_allow_html=True)

def page_dashboard():
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
        # Mostra os 10 mais recentes
        df_recentes = df_completo.sort_values('data_criacao', ascending=False).head(10)
        
        # Seleciona colunas para exibição
        colunas_exibicao = ['id', 'nome', 'dispositivos', 'status', 'prioridade', 'data_criacao']
        df_display = df_recentes[colunas_exibicao].copy()
        
        # Renomeia colunas
        df_display.columns = ['ID', 'Nome', 'Dispositivos', 'Status', 'Prioridade', 'Data']
        
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Nenhum ticket registrado ainda.")

def page_relatorios():
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

def page_administracao():
    """Página de administração"""
    st.subheader("⚙️ Administração do Sistema")
    
    # Senha de administrador (simples)
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        senha = st.text_input("🔐 Senha de Administrador", type="password")
        if st.button("Entrar"):
            if senha == "mavi2024":  # Senha simples para demonstração
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
        return
    
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

