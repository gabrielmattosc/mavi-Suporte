"""
Rotas do dashboard para o sistema Mavi Suporte
"""
from flask import Blueprint, render_template, jsonify
from src.routes.auth_routes import login_required, admin_required
from src.services.ticket_service import TicketService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/home')
@login_required
def home():
    """Página inicial do dashboard"""
    # Obtém estatísticas
    stats = TicketService.obter_estatisticas()
    
    # Obtém tickets recentes para admin
    recent_tickets = []
    if hasattr(session, 'user') and session.get('user', {}).get('role') == 'admin':
        recent_tickets = TicketService.listar_tickets()[:5]  # Últimos 5 tickets
    
    return render_template('home.html', stats=stats, recent_tickets=recent_tickets)

@dashboard_bp.route('/stats')
@admin_required
def stats():
    """Página de estatísticas (apenas admin)"""
    stats = TicketService.obter_estatisticas()
    tickets = TicketService.listar_tickets()
    
    # Prepara dados para gráficos
    status_data = {
        'labels': ['Pendentes', 'Em Andamento', 'Concluídos'],
        'values': [stats['pendentes'], stats['em_andamento'], stats['concluidos']],
        'colors': ['#ffc107', '#17a2b8', '#28a745']
    }
    
    # Top 5 dispositivos mais solicitados
    dispositivos_data = {
        'labels': list(stats['dispositivos_mais_solicitados'].keys())[:5],
        'values': list(stats['dispositivos_mais_solicitados'].values())[:5]
    }
    
    # Timeline de tickets (últimos 30 dias)
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    timeline_data = defaultdict(int)
    cutoff_date = datetime.now() - timedelta(days=30)
    
    for ticket in tickets:
        ticket_date = ticket['data_criacao']
        if isinstance(ticket_date, str):
            # Se for string, converte para datetime
            try:
                ticket_date = datetime.fromisoformat(ticket_date.replace('Z', '+00:00'))
            except:
                continue
        
        if ticket_date >= cutoff_date:
            date_key = ticket_date.strftime('%Y-%m-%d')
            timeline_data[date_key] += 1
    
    timeline_labels = sorted(timeline_data.keys())
    timeline_values = [timeline_data[date] for date in timeline_labels]
    
    return render_template('dashboard_stats.html', 
                         stats=stats,
                         tickets=tickets,
                         status_data=status_data,
                         dispositivos_data=dispositivos_data,
                         timeline_labels=timeline_labels,
                         timeline_values=timeline_values)

@dashboard_bp.route('/api/metrics')
@login_required
def api_metrics():
    """API para obter métricas atualizadas"""
    stats = TicketService.obter_estatisticas()
    return jsonify(stats)

# Importa session no final para evitar import circular
from flask import session

