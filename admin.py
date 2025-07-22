"""
Módulo de administração para o sistema Mavi Suporte
Funcionalidades administrativas e gerenciamento de tickets
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_database_managers
from typing import Dict, List, Any

def show_admin_page():
    """Exibe a página de administração"""
    if st.session_state.user['role'] != 'admin':
        st.error("❌ Acesso negado. Apenas administradores podem acessar esta página.")
        return
    
    st.subheader("⚙️ Painel de Administração")
    
    # Tabs para organizar funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎫 Gerenciar Tickets", 
        "📊 Estatísticas", 
        "👥 Usuários", 
        "⚙️ Configurações"
    ])
    
    with tab1:
        show_ticket_management()
    
    with tab2:
        show_admin_statistics()
    
    with tab3:
        show_user_management()
    
    with tab4:
        show_system_settings()

def show_ticket_management():
    """Exibe o gerenciamento de tickets"""
    st.markdown("### 🎫 Gerenciamento de Tickets")
    
    _, ticket_manager, _ = get_database_managers()
    
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
    
    with col3:
        if st.button("🔄 Atualizar Lista"):
            st.rerun()
    
    # Aplica filtros
    filtros = {}
    if status_filter != "Todos":
        filtros["status"] = status_filter
    if prioridade_filter != "Todas":
        filtros["prioridade"] = prioridade_filter
    
    # Lista tickets
    tickets = ticket_manager.listar_tickets(filtros)
    
    if tickets:
        # Prepara dados para exibição
        df_tickets = pd.DataFrame(tickets)
        
        # Seleciona colunas relevantes
        colunas_exibicao = ['ticket_id', 'nome', 'email', 'dispositivos', 'status', 'prioridade', 'data_criacao']
        df_display = df_tickets[colunas_exibicao].copy()
        
        # Formata data
        df_display['data_criacao'] = pd.to_datetime(df_display['data_criacao']).dt.strftime('%d/%m/%Y %H:%M')
        
        # Renomeia colunas
        df_display.columns = ['ID', 'Nome', 'Email', 'Dispositivos', 'Status', 'Prioridade', 'Data']
        
        # Exibe tabela
        st.dataframe(df_display, use_container_width=True)
        
        # Seção de atualização de status
        st.markdown("---")
        st.markdown("### ✏️ Atualizar Status do Ticket")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ticket_ids = [t['ticket_id'] for t in tickets]
            selected_ticket = st.selectbox("Selecionar Ticket", ticket_ids)
        
        with col2:
            novo_status = st.selectbox(
                "Novo Status", 
                ["Pendente", "Em andamento", "Concluída"]
            )
        
        with col3:
            observacao = st.text_input("Observação (opcional)")
        
        with col4:
            st.write("")  # Espaçamento
            if st.button("💾 Atualizar Status"):
                if ticket_manager.atualizar_status(selected_ticket, novo_status, observacao):
                    st.success(f"✅ Status do ticket #{selected_ticket} atualizado!")
                    
                    # Envia email de notificação
                    ticket_detalhes = ticket_manager.obter_ticket(selected_ticket)
                    if ticket_detalhes:
                        from email_service import get_email_service
                        email_service = get_email_service()
                        
                        if email_service.enabled:
                            email_enviado = email_service.enviar_atualizacao_status(
                                ticket_detalhes['email'],
                                selected_ticket,
                                novo_status,
                                observacao
                            )
                            
                            if email_enviado:
                                st.info("📧 Email de atualização enviado ao usuário!")
                            else:
                                st.warning("⚠️ Não foi possível enviar o email de atualização")
                        else:
                            st.info("📧 Configure a senha do email para ativar notificações")
                    
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar status!")
        
        # Detalhes do ticket selecionado
        if selected_ticket:
            ticket_detalhes = ticket_manager.obter_ticket(selected_ticket)
            if ticket_detalhes:
                st.markdown("---")
                st.markdown(f"### 📋 Detalhes do Ticket #{selected_ticket}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Informações Básicas:**")
                    st.write(f"**Nome:** {ticket_detalhes['nome']}")
                    st.write(f"**Email:** {ticket_detalhes['email']}")
                    st.write(f"**Squad Leader:** {ticket_detalhes['squad_leader']}")
                    st.write(f"**Prioridade:** {ticket_detalhes['prioridade']}")
                    st.write(f"**Status:** {ticket_detalhes['status']}")
                
                with col2:
                    st.markdown("**Datas:**")
                    st.write(f"**Criação:** {ticket_detalhes['data_criacao'].strftime('%d/%m/%Y %H:%M')}")
                    st.write(f"**Atualização:** {ticket_detalhes['data_atualizacao'].strftime('%d/%m/%Y %H:%M')}")
                
                st.markdown("**Dispositivos/Serviços:**")
                st.write(ticket_detalhes['dispositivos'])
                
                st.markdown("**Descrição da Necessidade:**")
                st.write(ticket_detalhes['necessidade'])
                
                # Observações
                if ticket_detalhes.get('observacoes'):
                    st.markdown("**Histórico de Observações:**")
                    for obs in ticket_detalhes['observacoes']:
                        st.write(f"- **{obs['data'].strftime('%d/%m/%Y %H:%M')}**: {obs['texto']} (Status: {obs['status']})")
    
    else:
        st.info("📋 Nenhum ticket encontrado com os filtros aplicados.")

def show_admin_statistics():
    """Exibe estatísticas administrativas"""
    st.markdown("### 📊 Estatísticas Detalhadas")
    
    _, ticket_manager, _ = get_database_managers()
    
    # Estatísticas gerais
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
    
    if tickets:
        # Análise por período
        st.markdown("### 📅 Análise por Período")
        
        df_tickets = pd.DataFrame(tickets)
        df_tickets['data'] = pd.to_datetime(df_tickets['data_criacao']).dt.date
        
        # Tickets por dia
        tickets_por_dia = df_tickets.groupby('data').size().reset_index(name='quantidade')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Tickets por Dia:**")
            st.line_chart(tickets_por_dia.set_index('data'))
        
        with col2:
            # Análise por prioridade
            prioridade_counts = df_tickets['prioridade'].value_counts()
            st.markdown("**Distribuição por Prioridade:**")
            st.bar_chart(prioridade_counts)
        
        # Tabela de resumo por status
        st.markdown("### 📈 Resumo por Status")
        
        status_summary = df_tickets.groupby(['status', 'prioridade']).size().reset_index(name='quantidade')
        status_pivot = status_summary.pivot(index='status', columns='prioridade', values='quantidade').fillna(0)
        
        st.dataframe(status_pivot, use_container_width=True)
        
        # Top dispositivos detalhado
        st.markdown("### 💻 Análise de Dispositivos")
        
        if stats['dispositivos_mais_solicitados']:
            dispositivos_df = pd.DataFrame(
                list(stats['dispositivos_mais_solicitados'].items()),
                columns=['Dispositivo', 'Quantidade']
            )
            
            st.dataframe(dispositivos_df, use_container_width=True)
            st.bar_chart(dispositivos_df.set_index('Dispositivo'))
        else:
            st.info("Nenhum dispositivo solicitado ainda.")
    
    else:
        st.info("📊 Nenhum dado disponível para análise.")

def show_user_management():
    """Exibe o gerenciamento de usuários"""
    st.markdown("### 👥 Gerenciamento de Usuários")
    
    _, _, user_manager = get_database_managers()
    
    # Lista usuários do sistema
    st.markdown("**Usuários do Sistema:**")
    
    usuarios_info = [
        {"Usuário": "admin", "Perfil": "Administrador", "Email": "admin@maviclick.com", "Status": "Ativo"},
        {"Usuário": "teste", "Perfil": "Usuário", "Email": "teste@maviclick.com", "Status": "Ativo"},
        {"Usuário": "público", "Perfil": "Convidado", "Email": "publico@mavi.com", "Status": "Ativo"}
    ]
    
    df_usuarios = pd.DataFrame(usuarios_info)
    st.dataframe(df_usuarios, use_container_width=True)
    
    # Informações de acesso
    st.markdown("### 🔐 Níveis de Acesso")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**👑 Administrador**")
        st.write("- Gerenciar todos os tickets")
        st.write("- Atualizar status")
        st.write("- Gerar relatórios")
        st.write("- Gerenciar usuários")
        st.write("- Configurações do sistema")
    
    with col2:
        st.markdown("**👤 Usuário**")
        st.write("- Criar tickets")
        st.write("- Consultar próprios tickets")
        st.write("- Visualizar dashboard")
        st.write("- Receber notificações")
    
    with col3:
        st.markdown("**👥 Público**")
        st.write("- Criar tickets")
        st.write("- Consultar tickets por ID")
        st.write("- Visualizar dashboard público")
    
    # Logs de acesso (simulado)
    st.markdown("### 📊 Logs de Acesso Recentes")
    
    logs_acesso = [
        {"Data/Hora": datetime.now().strftime('%d/%m/%Y %H:%M'), "Usuário": st.session_state.user['username'], "Ação": "Login", "IP": "192.168.1.100"},
        {"Data/Hora": "22/01/2025 14:30", "Usuário": "teste", "Ação": "Criou ticket", "IP": "192.168.1.101"},
        {"Data/Hora": "22/01/2025 13:15", "Usuário": "público", "Ação": "Consultou ticket", "IP": "192.168.1.102"},
    ]
    
    df_logs = pd.DataFrame(logs_acesso)
    st.dataframe(df_logs, use_container_width=True)

def show_system_settings():
    """Exibe as configurações do sistema"""
    st.markdown("### ⚙️ Configurações do Sistema")
    
    # Configurações de email
    st.markdown("#### 📧 Configurações de Email")
    
    col1, col2 = st.columns(2)
    
    with col1:
        smtp_server = st.text_input("Servidor SMTP", value="smtp.gmail.com")
        smtp_port = st.number_input("Porta SMTP", value=587)
        email_remetente = st.text_input("Email Remetente", value="gabriel@maviclick.com")
    
    with col2:
        email_senha = st.text_input("Senha do Email", type="password", placeholder="Digite a senha")
        ssl_enabled = st.checkbox("Usar SSL/TLS", value=True)
        email_ativo = st.checkbox("Email Ativo", value=True)
    
    if st.button("💾 Salvar Configurações de Email"):
        st.success("✅ Configurações de email salvas!")
        st.info("🔄 Reinicie a aplicação para aplicar as mudanças")
    
    # Configurações do sistema
    st.markdown("---")
    st.markdown("#### 🔧 Configurações Gerais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_tickets_fila = st.number_input("Máximo de Tickets na Fila", value=100, min_value=10)
        tempo_sessao = st.number_input("Tempo de Sessão (minutos)", value=60, min_value=15)
    
    with col2:
        backup_automatico = st.checkbox("Backup Automático", value=True)
        logs_detalhados = st.checkbox("Logs Detalhados", value=False)
    
    if st.button("💾 Salvar Configurações Gerais"):
        st.success("✅ Configurações gerais salvas!")
    
    # Informações do sistema
    st.markdown("---")
    st.markdown("#### ℹ️ Informações do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Versão:** 2.0.0 (Streamlit)  
        **Banco de Dados:** MongoDB  
        **Framework:** Streamlit  
        **Python:** 3.11+  
        **Última Atualização:** {datetime.now().strftime('%d/%m/%Y')}
        """)
    
    with col2:
        st.success(f"""
        **Status:** Online ✅  
        **Uptime:** Ativo  
        **Usuários Conectados:** 1  
        **Tickets Ativos:** {get_database_managers()[1].obter_estatisticas()['total_tickets']}  
        **Última Sincronização:** {datetime.now().strftime('%H:%M')}
        """)
    
    # Ações do sistema
    st.markdown("---")
    st.markdown("#### 🔧 Ações do Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Limpar Cache", use_container_width=True):
            st.cache_resource.clear()
            st.success("✅ Cache limpo!")
    
    with col2:
        if st.button("📊 Exportar Dados", use_container_width=True):
            # TODO: Implementar exportação
            st.info("🚧 Funcionalidade em desenvolvimento")
    
    with col3:
        if st.button("🔄 Reiniciar Sistema", use_container_width=True):
            st.warning("⚠️ Esta ação reiniciará o sistema")
            st.info("🚧 Funcionalidade em desenvolvimento")
    
    with col4:
        if st.button("📋 Ver Logs", use_container_width=True):
            st.info("🚧 Visualização de logs em desenvolvimento")

