"""
Rotas da API de gráficos para o sistema Mavi Suporte
"""
from flask import Blueprint, jsonify
from src.routes.auth_routes import admin_required
from src.services.ticket_service import TicketService
import pandas as pd
import plotly.express as px
import plotly.utils
import json


# 1. Cria um novo Blueprint dedicado apenas aos gráficos
graphics_bp = Blueprint('graphics', __name__, url_prefix='/api/graphics')

@graphics_bp.route('/')
@admin_required
def get_all_graphics():
    """
    Endpoint de API que retorna todos os dados dos gráficos para a página de relatórios.
    """
    try:
        ticket_service = TicketService()
        stats = ticket_service.obter_estatisticas()
        tickets = ticket_service.listar_tickets()
        
        if not tickets:
            return jsonify(error="Nenhum dado para gerar gráficos."), 404

        df = pd.DataFrame(tickets)
        df['data_criacao'] = pd.to_datetime(df['data_criacao'])

        # Gráfico de Pizza: Status
        status_counts = df['status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values, names=status_counts.index,
            color_discrete_sequence=['#ffc107', '#17a2b8', '#28a745']
        )

        graph_status_json = json.dumps(fig_status, cls=plotly.utils.PlotlyJSONEncoder)

        # Gráfico de Barras: Dispositivos
        dispositivos_items = list(stats.get('dispositivos_mais_solicitados', {}).items())[:8]
        graph_dispositivos_json = None
        if dispositivos_items:
            dispositivos_df = pd.DataFrame(dispositivos_items, columns=['Dispositivo', 'Quantidade'])
            fig_dispositivos = px.bar(
                dispositivos_df, x='Quantidade', y='Dispositivo', orientation='h',
                color_discrete_sequence=['#00D4AA']
            )
            graph_dispositivos_json = json.dumps(fig_dispositivos, cls=plotly.utils.PlotlyJSONEncoder)

        # Gráfico de Linha: Timeline
        df['data'] = df['data_criacao'].dt.date
        timeline_data = df.groupby('data').size().reset_index(name='quantidade')
        fig_timeline = px.line(
            timeline_data, x='data', y='quantidade', markers=True,
            color_discrete_sequence=['#00B894']
        )
        graph_timeline_json = json.dumps(fig_timeline, cls=plotly.utils.PlotlyJSONEncoder)

        return jsonify({
            'status': graph_status_json,
            'dispositivos': graph_dispositivos_json,
            'timeline': graph_timeline_json
        })

    except Exception as e:
        print(f"Erro na API de gráficos: {e}")
        return jsonify(error="Não foi possível gerar os dados dos gráficos."), 500

