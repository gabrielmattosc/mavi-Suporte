"""
Módulo de relatórios e geração de PDF para o sistema Mavi Suporte (Streamlit)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from database import get_database_managers
from typing import Dict, List, Any, Optional
import base64

class ReportGenerator:
    """Gerador de relatórios e PDFs"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos customizados para o PDF"""
        # Estilo para título principal
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#00D4AA')
        )
        
        # Estilo para subtítulos
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#00B894')
        )
        
        # Estilo para texto normal
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12
        )
    
    def show_reports_page(self):
        """Exibe a página de relatórios"""
        st.subheader("📈 Relatórios e Análises")
        
        # Verifica permissões
        if st.session_state.user['role'] not in ['admin']:
            st.warning("⚠️ Acesso limitado. Algumas funcionalidades são restritas a administradores.")
        
        # Tabs para organizar relatórios
        tab1, tab2, tab3 = st.tabs([
            "📊 Dashboard Avançado",
            "📄 Gerar PDF", 
            "📋 Análises Detalhadas"
        ])
        
        with tab1:
            self.show_advanced_dashboard()
        
        with tab2:
            self.show_pdf_generator()
        
        with tab3:
            self.show_detailed_analysis()
    
    def show_advanced_dashboard(self):
        """Exibe dashboard avançado com gráficos interativos"""
        st.markdown("### 📊 Dashboard Avançado")
        
        _, ticket_manager, _, _ = get_database_managers()
        
        # Obtém dados
        tickets = ticket_manager.listar_tickets()
        stats = ticket_manager.obter_estatisticas()
        
        if not tickets:
            st.info("📊 Nenhum dado disponível para análise. Crie alguns tickets primeiro!")
            return
        
        # Converte para DataFrame
        df = pd.DataFrame(tickets)
        df['data_criacao'] = pd.to_datetime(df['data_criacao'])
        df['data'] = df['data_criacao'].dt.date
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total", stats['total_tickets'])
        with col2:
            st.metric("⏳ Pendentes", stats['pendentes'])
        with col3:
            st.metric("🔄 Em Andamento", stats['em_andamento'])
        with col4:
            st.metric("✅ Concluídos", stats['concluidos'])
        
        # Gráficos interativos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Distribuição por Status")
            
            # Gráfico de pizza interativo
            status_counts = df['status'].value_counts()
            
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Status dos Tickets",
                color_discrete_sequence=['#ffc107', '#17a2b8', '#28a745']
            )
            fig_status.update_layout(height=400)
            
            # Exibe gráfico com callback para detalhes
            selected_status = st.plotly_chart(fig_status, use_container_width=True, key="status_chart")
            
            # Botão para ver detalhes
            if st.button("🔍 Ver Detalhes por Status", key="status_details"):
                st.session_state.show_status_details = True
        
        with col2:
            st.markdown("#### 💻 Top Dispositivos Solicitados")
            
            if stats['dispositivos_mais_solicitados']:
                # Prepara dados dos dispositivos
                dispositivos_items = list(stats['dispositivos_mais_solicitados'].items())[:8]
                
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
                        title="Dispositivos Mais Solicitados",
                        color='Quantidade',
                        color_continuous_scale='Viridis'
                    )
                    fig_dispositivos.update_layout(height=400)
                    
                    st.plotly_chart(fig_dispositivos, use_container_width=True, key="devices_chart")
                    
                    # Botão para ver detalhes
                    if st.button("🔍 Ver Detalhes por Dispositivo", key="device_details"):
                        st.session_state.show_device_details = True
                else:
                    st.info("Nenhum dispositivo solicitado ainda.")
            else:
                st.info("Nenhum dispositivo solicitado ainda.")
        
        # Timeline de tickets
        st.markdown("#### 📅 Timeline de Criação de Tickets")
        
        # Agrupa por data
        timeline_data = df.groupby('data').size().reset_index(name='quantidade')
        
        fig_timeline = px.line(
            timeline_data,
            x='data',
            y='quantidade',
            title='Tickets criados por dia',
            markers=True,
            color_discrete_sequence=['#00D4AA']
        )
        fig_timeline.update_layout(height=300)
        
        st.plotly_chart(fig_timeline, use_container_width=True, key="timeline_chart")
        
        # Botão para ver detalhes da timeline
        if st.button("🔍 Ver Análise Temporal Detalhada", key="timeline_details"):
            st.session_state.show_timeline_details = True
        
        # Análise por prioridade
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⚡ Distribuição por Prioridade")
            
            prioridade_counts = df['prioridade'].value_counts()
            
            fig_prioridade = px.bar(
                x=prioridade_counts.index,
                y=prioridade_counts.values,
                title="Tickets por Prioridade",
                color=prioridade_counts.index,
                color_discrete_map={
                    'Normal': '#6c757d',
                    'Alta': '#ffc107', 
                    'Urgente': '#dc3545'
                }
            )
            fig_prioridade.update_layout(height=300)
            
            st.plotly_chart(fig_prioridade, use_container_width=True, key="priority_chart")
        
        with col2:
            st.markdown("#### 📊 Matriz Status x Prioridade")
            
            # Cria tabela cruzada
            crosstab = pd.crosstab(df['status'], df['prioridade'], margins=True)
            
            st.dataframe(crosstab, use_container_width=True)
        
        # Exibe detalhes se solicitado
        self._show_chart_details()
    
    def _show_chart_details(self):
        """Exibe detalhes dos gráficos quando solicitado"""
        _, ticket_manager, _, _ = get_database_managers()
        
        # Detalhes por status
        if st.session_state.get('show_status_details', False):
            st.markdown("---")
            st.markdown("### 📋 Detalhes por Status")
            
            status_options = ["Pendente", "Em andamento", "Concluída"]
            selected_status = st.selectbox("Selecione o status:", status_options)
            
            tickets_filtrados = ticket_manager.listar_tickets({"status": selected_status})
            
            if tickets_filtrados:
                df_filtrado = pd.DataFrame(tickets_filtrados)
                df_display = df_filtrado[['ticket_id', 'nome', 'prioridade', 'data_criacao']].copy()
                df_display['data_criacao'] = pd.to_datetime(df_display['data_criacao']).dt.strftime('%d/%m/%Y %H:%M')
                df_display.columns = ['ID', 'Nome', 'Prioridade', 'Data']
                
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info(f"Nenhum ticket com status '{selected_status}' encontrado.")
            
            if st.button("❌ Fechar Detalhes", key="close_status"):
                st.session_state.show_status_details = False
                st.rerun()
        
        # Detalhes por dispositivo
        if st.session_state.get('show_device_details', False):
            st.markdown("---")
            st.markdown("### 💻 Detalhes por Dispositivo")
            
            stats = ticket_manager.obter_estatisticas()
            
            if stats['dispositivos_mais_solicitados']:
                dispositivo_selecionado = st.selectbox(
                    "Selecione o dispositivo:",
                    list(stats['dispositivos_mais_solicitados'].keys())
                )
                
                # Filtra tickets que contêm o dispositivo
                todos_tickets = ticket_manager.listar_tickets()
                tickets_dispositivo = [
                    t for t in todos_tickets 
                    if dispositivo_selecionado.lower() in t.get('dispositivos', '').lower()
                ]
                
                if tickets_dispositivo:
                    df_dispositivo = pd.DataFrame(tickets_dispositivo)
                    df_display = df_dispositivo[['ticket_id', 'nome', 'status', 'data_criacao']].copy()
                    df_display['data_criacao'] = pd.to_datetime(df_display['data_criacao']).dt.strftime('%d/%m/%Y %H:%M')
                    df_display.columns = ['ID', 'Nome', 'Status', 'Data']
                    
                    st.dataframe(df_display, use_container_width=True)
                else:
                    st.info(f"Nenhum ticket encontrado para '{dispositivo_selecionado}'.")
            
            if st.button("❌ Fechar Detalhes", key="close_device"):
                st.session_state.show_device_details = False
                st.rerun()
        
        # Detalhes da timeline
        if st.session_state.get('show_timeline_details', False):
            st.markdown("---")
            st.markdown("### 📅 Análise Temporal Detalhada")
            
            tickets = ticket_manager.listar_tickets()
            df = pd.DataFrame(tickets)
            df['data_criacao'] = pd.to_datetime(df['data_criacao'])
            
            # Análise por período
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Tickets por Dia da Semana:**")
                df['dia_semana'] = df['data_criacao'].dt.day_name()
                dia_counts = df['dia_semana'].value_counts()
                st.bar_chart(dia_counts)
            
            with col2:
                st.markdown("**Tickets por Hora do Dia:**")
                df['hora'] = df['data_criacao'].dt.hour
                hora_counts = df['hora'].value_counts().sort_index()
                st.line_chart(hora_counts)
            
            if st.button("❌ Fechar Análise", key="close_timeline"):
                st.session_state.show_timeline_details = False
                st.rerun()
    
    # vvvvvvvvvvv FUNÇÃO ALTERADA vvvvvvvvvvv
    def show_detailed_analysis(self):
        """Exibe análises detalhadas e opções de exportação"""
        st.markdown("### 📋 Análises Detalhadas")
        
        _, ticket_manager, _, _ = get_database_managers()
        
        tickets = ticket_manager.listar_tickets()
        
        if not tickets:
            st.info("📊 Nenhum dado disponível para análise.")
            return
        
        df = pd.DataFrame(tickets)
        df['data_criacao'] = pd.to_datetime(df['data_criacao'])
        
        # Análise de performance
        st.markdown("#### ⏱️ Análise de Performance")
        
        # Tempo médio de resolução (simulado)
        tickets_concluidos = df[df['status'] == 'Concluída']
        
        if not tickets_concluidos.empty:
            # Simula tempo de resolução
            tempo_medio = 2.5  # dias (simulado)
            st.metric("Tempo Médio de Resolução", f"{tempo_medio:.1f} dias")
        else:
            st.info("Nenhum ticket concluído para análise de tempo.")
        
        # Análise de tendências
        st.markdown("#### 📈 Análise de Tendências")
        
        # Tickets por mês
        df['mes'] = df['data_criacao'].dt.to_period('M').astype(str)
        tickets_por_mes = df.groupby('mes').size()
        
        if len(tickets_por_mes) > 1:
            st.line_chart(tickets_por_mes)
            
            # Calcula tendência
            if len(tickets_por_mes) >= 2:
                variacao = tickets_por_mes.iloc[-1] - tickets_por_mes.iloc[-2]
                if variacao > 0:
                    st.success(f"� Aumento de {variacao} tickets no último período")
                elif variacao < 0:
                    st.info(f"📉 Redução de {abs(variacao)} tickets no último período")
                else:
                    st.info("➡️ Número de tickets estável")
        else:
            st.info("Dados insuficientes para análise de tendência.")
        
        # --- SEÇÃO DE EXPORTAÇÃO ATUALIZADA ---
        st.markdown("---")
        st.markdown("#### 📥 Exportar Relatório Completo de Tickets")
        
        # Prepara o DataFrame para exportação
        df_export = df.copy()
        
        # Converte a lista de observações em uma string legível
        if 'observacoes' in df_export.columns:
            df_export['observacoes'] = df_export['observacoes'].apply(
                lambda obs_list: "\n".join([f"{obs.get('data').strftime('%d/%m/%y %H:%M')}: {obs.get('texto', '')}" for obs in obs_list]) if obs_list else ""
            )
        
        # Formata datas para melhor leitura no relatório
        df_export['data_criacao'] = pd.to_datetime(df_export['data_criacao']).dt.strftime('%d/%m/%Y %H:%M:%S')
        if 'data_atualizacao' in df_export.columns:
            df_export['data_atualizacao'] = pd.to_datetime(df_export['data_atualizacao']).dt.strftime('%d/%m/%Y %H:%M:%S')

        col1, col2 = st.columns(2)
        
        with col1:
            # --- BOTÃO DE EXPORTAR PARA EXCEL ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Tickets')
            
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Baixar Relatório em Excel (.xlsx)",
                data=excel_data,
                file_name=f"relatorio_tickets_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col2:
            # --- BOTÃO DE EXPORTAR PARA CSV ---
            # Mantido como opção, substituindo o de JSON
            csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 Baixar Relatório em CSV (.csv)",
                data=csv_data,
                file_name=f"relatorio_tickets_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    # ^^^^^^^^^^^ FIM DA FUNÇÃO ALTERADA ^^^^^^^^^^^
    
    def show_pdf_generator(self):
        """Exibe interface para geração de PDF"""
        st.markdown("### 📄 Gerador de Relatórios PDF")
        
        if st.session_state.user['role'] != 'admin':
            st.error("❌ Apenas administradores podem gerar relatórios PDF.")
            return
        
        # Opções de relatório
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_relatorio = st.selectbox(
                "Tipo de Relatório",
                ["Relatório Completo", "Relatório por Status", "Relatório por Período"]
            )
        
        with col2:
            incluir_graficos = st.checkbox("Incluir Gráficos", value=True)
        
        # Filtros específicos
        filtros = {}
        data_inicio = None
        data_fim = None
        if tipo_relatorio == "Relatório por Status":
            status_filtro = st.selectbox(
                "Status para Filtrar",
                ["Pendente", "Em andamento", "Concluída"]
            )
            filtros["status"] = status_filtro
        elif tipo_relatorio == "Relatório por Período":
            col_a, col_b = st.columns(2)
            with col_a:
                data_inicio = st.date_input("Data Início", value=datetime.now().date() - timedelta(days=30))
            with col_b:
                data_fim = st.date_input("Data Fim", value=datetime.now().date())
        
        # Botão para gerar PDF
        if st.button("📄 Gerar Relatório PDF", use_container_width=True):
            with st.spinner("Gerando relatório PDF..."):
                try:
                    
                    _, _, _, log_manager = get_database_managers()
                    
                    # Gera PDF
                    pdf_buffer = self.generate_pdf_report(
                        tipo_relatorio=tipo_relatorio,
                        filtros=filtros,
                        incluir_graficos=incluir_graficos,
                        data_inicio=data_inicio,
                        data_fim=data_fim
                    )
                    
                    if pdf_buffer:
                        
                        # --- NOVO: Registra o log de sucesso ---
                        log_manager.registrar_log(
                            st.session_state.user['username'],
                            "Geração de Relatório",
                            f"Tipo: {tipo_relatorio}"
                        )                        
                        
                        # Disponibiliza para download
                        st.success("✅ Relatório PDF gerado com sucesso!")
                        filename = f"relatorio_mavi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        st.download_button(
                            label="📥 Baixar Relatório PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ Erro ao gerar relatório PDF.")
                
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatório: {str(e)}")
    
    def generate_pdf_report(self, 
                            tipo_relatorio: str,
                            filtros: Dict[str, Any] = None,
                            incluir_graficos: bool = True,
                            data_inicio: Optional[datetime.date] = None,
                            data_fim: Optional[datetime.date] = None) -> Optional[io.BytesIO]:
        """
        Gera relatório em PDF
        """
        try:
            # Cria buffer para o PDF
            buffer = io.BytesIO()
            
            # Cria documento PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Lista para armazenar elementos do PDF
            story = []
            
            # Título
            story.append(Paragraph("Sistema de Suporte Mavi", self.title_style))
            story.append(Paragraph(f"{tipo_relatorio}", self.subtitle_style))
            story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", self.normal_style))
            story.append(Spacer(1, 20))
            
            # Obtém dados
            _, ticket_manager, _, _ = get_database_managers()
            
            # Aplica filtros de período se necessário
            if data_inicio and data_fim:
                todos_tickets = ticket_manager.listar_tickets()
                tickets = []
                for ticket in todos_tickets:
                    ticket_date = ticket['data_criacao'].date()
                    if data_inicio <= ticket_date <= data_fim:
                        tickets.append(ticket)
            else:
                tickets = ticket_manager.listar_tickets(filtros)
            
            stats = ticket_manager.obter_estatisticas()
            
            # Resumo executivo
            story.append(Paragraph("Resumo Executivo", self.subtitle_style))
            
            resumo_data = [
                ['Métrica', 'Valor'],
                ['Total de Tickets', str(len(tickets))],
                ['Tickets Pendentes', str(len([t for t in tickets if t['status'] == 'Pendente']))],
                ['Tickets em Andamento', str(len([t for t in tickets if t['status'] == 'Em andamento']))],
                ['Tickets Concluídos', str(len([t for t in tickets if t['status'] == 'Concluída']))],
            ]
            
            resumo_table = Table(resumo_data)
            resumo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00D4AA')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(resumo_table)
            story.append(Spacer(1, 20))
            
            # Detalhes dos tickets
            if tickets:
                story.append(Paragraph("Detalhes dos Tickets", self.subtitle_style))
                
                # Prepara dados da tabela
                table_data = [['ID', 'Nome', 'Status', 'Prioridade', 'Data']]
                
                for ticket in tickets[:20]:  # Limita a 20 tickets para não sobrecarregar
                    table_data.append([
                        ticket['ticket_id'],
                        ticket['nome'][:20] + '...' if len(ticket['nome']) > 20 else ticket['nome'],
                        ticket['status'],
                        ticket['prioridade'],
                        ticket['data_criacao'].strftime('%d/%m/%Y')
                    ])
                
                # Cria tabela
                tickets_table = Table(table_data)
                tickets_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00B894')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                
                story.append(tickets_table)
                
                if len(tickets) > 20:
                    story.append(Spacer(1, 10))
                    story.append(Paragraph(f"... e mais {len(tickets) - 20} tickets", self.normal_style))
            
            else:
                story.append(Paragraph("Nenhum ticket encontrado com os filtros aplicados.", self.normal_style))
            
            # Rodapé
            story.append(Spacer(1, 30))
            story.append(Paragraph("Sistema Mavi Suporte - Relatório Automático", self.normal_style))
            story.append(Paragraph("© 2025 Mavi Click. Todos os direitos reservados.", self.normal_style))
            
            # Constrói PDF
            doc.build(story)
            
            # Retorna buffer
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {str(e)}")
            return None

# Instância global do gerador de relatórios
@st.cache_resource
def get_report_generator() -> ReportGenerator:
    """
    Obtém instância do gerador de relatórios
    
    Returns:
        Instância do gerador de relatórios
    """
    return ReportGenerator()