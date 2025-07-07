"""
Módulo para geração de relatórios
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
from typing import Dict, List, Tuple
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ReportGenerator:
    """Gerador de relatórios da fila de suporte"""
    
    def __init__(self, fila_file: str, relatorios_dir: str):
        self.fila_file = fila_file
        self.relatorios_dir = relatorios_dir
        self.ensure_reports_dir()
    
    def ensure_reports_dir(self):
        """Garante que o diretório de relatórios existe"""
        if not os.path.exists(self.relatorios_dir):
            os.makedirs(self.relatorios_dir)
    
    def carregar_dados(self) -> pd.DataFrame:
        """Carrega os dados da fila"""
        df = pd.read_csv(self.fila_file)
        
        # Converte datas
        df['data_criacao'] = pd.to_datetime(df['data_criacao'], errors='coerce')
        df['data_solicitacao'] = pd.to_datetime(df['data_solicitacao'], errors='coerce')
        df['data_conclusao'] = pd.to_datetime(df['data_conclusao'], errors='coerce')
        
        return df
    
    def gerar_relatorio_geral(self) -> Dict:
        """Gera relatório geral com estatísticas principais"""
        df = self.carregar_dados()
        
        # Estatísticas básicas
        total_tickets = len(df)
        pendentes = len(df[df['status'] == 'Pendente'])
        em_andamento = len(df[df['status'] == 'Em andamento'])
        concluidos = len(df[df['status'] == 'Concluída'])
        
        # Tempo médio de resolução (apenas para tickets concluídos)
        df_concluidos = df[df['status'] == 'Concluída'].copy()
        if not df_concluidos.empty:
            df_concluidos['tempo_resolucao'] = (df_concluidos['data_conclusao'] - df_concluidos['data_criacao']).dt.total_seconds() / 3600  # em horas
            tempo_medio_resolucao = df_concluidos['tempo_resolucao'].mean()
        else:
            tempo_medio_resolucao = 0
        
        # Dispositivos mais solicitados
        dispositivos_lista = []
        for _, row in df.iterrows():
            if pd.notna(row['dispositivos']):
                dispositivos_lista.extend([d.strip() for d in str(row['dispositivos']).split(',')])
        
        dispositivos_count = pd.Series(dispositivos_lista).value_counts().head(10)
        
        # Tickets por período (últimos 30 dias)
        data_limite = datetime.now() - timedelta(days=30)
        df_recentes = df[df['data_criacao'] >= data_limite]
        tickets_por_dia = df_recentes.groupby(df_recentes['data_criacao'].dt.date).size()
        
        return {
            'total_tickets': total_tickets,
            'pendentes': pendentes,
            'em_andamento': em_andamento,
            'concluidos': concluidos,
            'tempo_medio_resolucao_horas': round(tempo_medio_resolucao, 2),
            'dispositivos_mais_solicitados': dispositivos_count.to_dict(),
            'tickets_por_dia': tickets_por_dia.to_dict()
        }
    
    def gerar_grafico_status(self) -> str:
        """Gera gráfico de distribuição por status"""
        df = self.carregar_dados()
        
        # Conta tickets por status
        status_counts = df['status'].value_counts()
        
        # Cria gráfico com plotly
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribuição de Tickets por Status",
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
        
        # Salva o gráfico
        filename = f"status_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.relatorios_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def gerar_grafico_dispositivos(self) -> str:
        """Gera gráfico dos dispositivos mais solicitados"""
        df = self.carregar_dados()
        
        # Processa dispositivos
        dispositivos_lista = []
        for _, row in df.iterrows():
            if pd.notna(row['dispositivos']):
                dispositivos_lista.extend([d.strip() for d in str(row['dispositivos']).split(',')])
        
        dispositivos_count = pd.Series(dispositivos_lista).value_counts().head(10)
        
        # Cria gráfico
        fig = px.bar(
            x=dispositivos_count.values,
            y=dispositivos_count.index,
            orientation='h',
            title="Top 10 Dispositivos Mais Solicitados",
            labels={'x': 'Quantidade de Solicitações', 'y': 'Dispositivo'}
        )
        
        fig.update_layout(
            font=dict(size=12),
            title_font_size=18,
            height=500
        )
        
        # Salva o gráfico
        filename = f"dispositivos_top10_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.relatorios_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def gerar_grafico_timeline(self) -> str:
        """Gera gráfico de timeline dos tickets"""
        df = self.carregar_dados()
        
        # Filtra últimos 30 dias
        data_limite = datetime.now() - timedelta(days=30)
        df_recentes = df[df['data_criacao'] >= data_limite]
        
        if df_recentes.empty:
            return None
        
        # Agrupa por dia
        tickets_por_dia = df_recentes.groupby([
            df_recentes['data_criacao'].dt.date,
            'status'
        ]).size().reset_index(name='count')
        
        # Cria gráfico
        fig = px.line(
            tickets_por_dia,
            x='data_criacao',
            y='count',
            color='status',
            title="Timeline de Tickets (Últimos 30 dias)",
            labels={'data_criacao': 'Data', 'count': 'Número de Tickets'}
        )
        
        fig.update_layout(
            font=dict(size=12),
            title_font_size=18,
            xaxis_title="Data",
            yaxis_title="Número de Tickets"
        )
        
        # Salva o gráfico
        filename = f"timeline_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.relatorios_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def gerar_relatorio_completo(self) -> Dict[str, str]:
        """Gera relatório completo com todos os gráficos"""
        relatorio = self.gerar_relatorio_geral()
        
        # Gera gráficos
        graficos = {
            'status': self.gerar_grafico_status(),
            'dispositivos': self.gerar_grafico_dispositivos(),
            'timeline': self.gerar_grafico_timeline()
        }
        
        # Gera relatório em HTML
        html_content = self._gerar_html_relatorio(relatorio, graficos)
        
        # Salva relatório HTML
        filename = f"relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.relatorios_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return {
            'relatorio_html': filepath,
            'graficos': graficos,
            'dados': relatorio
        }
    
    def _gerar_html_relatorio(self, dados: Dict, graficos: Dict) -> str:
        """Gera HTML do relatório completo"""
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de Suporte Mavi</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 30px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .stat-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    border-left: 4px solid #667eea;
                }}
                .stat-number {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }}
                .stat-label {{
                    color: #6c757d;
                    margin-top: 5px;
                }}
                .section {{
                    margin: 40px 0;
                }}
                .section h2 {{
                    color: #667eea;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Relatório de Suporte Mavi</h1>
                    <p>Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h2>Resumo Executivo</h2>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-number">{dados['total_tickets']}</div>
                                <div class="stat-label">Total de Tickets</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">{dados['pendentes']}</div>
                                <div class="stat-label">Pendentes</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">{dados['em_andamento']}</div>
                                <div class="stat-label">Em Andamento</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">{dados['concluidos']}</div>
                                <div class="stat-label">Concluídos</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">{dados['tempo_medio_resolucao_horas']:.1f}h</div>
                                <div class="stat-label">Tempo Médio de Resolução</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Dispositivos Mais Solicitados</h2>
                        <ul>
        """
        
        for dispositivo, count in list(dados['dispositivos_mais_solicitados'].items())[:5]:
            html += f"<li><strong>{dispositivo}:</strong> {count} solicitações</li>"
        
        html += """
                        </ul>
                    </div>
                    
                    <div class="section">
                        <p><em>Para visualizações interativas detalhadas, consulte os arquivos de gráficos gerados separadamente.</em></p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

