"""
Rotas para exportação de dados para o sistema Mavi Suporte
"""
from flask import Blueprint, send_file
from src.routes.auth_routes import admin_required
from src.services.ticket_service import TicketService
from datetime import datetime
import pandas as pd
import io

# 1. Cria um novo Blueprint dedicado apenas à exportação
export_bp = Blueprint('export', __name__, url_prefix='/export')

@export_bp.route('/excel')
@admin_required
def export_excel():
    """
    Gera e envia um ficheiro Excel com todos os dados dos tickets.
    """
    try:
        ticket_service = TicketService()
        tickets = ticket_service.listar_tickets()

        if not tickets:
            return "Nenhum ticket para exportar.", 404

        # Converte para DataFrame
        df = pd.DataFrame(tickets)

        # Prepara o DataFrame para um relatório limpo
        df_export = df.copy()
        
        # Formata a coluna de observações para ser legível
        if 'observacoes' in df_export.columns:
            df_export['observacoes'] = df_export['observacoes'].apply(
                lambda obs_list: "\n".join([
                    f"{obs.get('data').strftime('%d/%m/%Y %H:%M')}: {obs.get('texto', '')} (Status: {obs.get('status', 'N/A')})" 
                    for obs in obs_list
                ]) if obs_list else ""
            )
        
        # Formata as datas
        df_export['data_criacao'] = pd.to_datetime(df_export['data_criacao']).dt.strftime('%d/%m/%Y %H:%M:%S')
        df_export['data_atualizacao'] = pd.to_datetime(df_export['data_atualizacao']).dt.strftime('%d/%m/%Y %H:%M:%S')

        # Reordena e renomeia as colunas para o relatório final
        colunas_map = {
            'ticket_id': 'ID do Ticket', 'nome': 'Nome do Solicitante', 'email': 'Email',
            'squad_leader': 'Squad Leader', 'dispositivos': 'Dispositivos',
            'necessidade': 'Descrição', 'prioridade': 'Prioridade', 'status': 'Status',
            'data_criacao': 'Data de Criação', 'data_atualizacao': 'Última Atualização',
            'observacoes': 'Histórico de Observações'
        }
        # Garante que apenas as colunas desejadas estão no export, e na ordem certa
        df_export = df_export[[key for key in colunas_map if key in df_export.columns]]
        df_export.rename(columns=colunas_map, inplace=True)

        # Cria um ficheiro Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Relatorio_Tickets')
        output.seek(0)

        # Envia o ficheiro para o utilizador
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'relatorio_mavi_suporte_{datetime.now().strftime("%Y-%m-%d")}.xlsx'
        )

    except Exception as e:
        print(f"Erro ao exportar para Excel: {e}")
        return "Ocorreu um erro ao gerar o relatório.", 500
