"""
Rotas do dashboard para o sistema Mavi Suporte
"""
from flask import Blueprint, render_template, jsonify, session
from src.routes.auth_routes import login_required, admin_required
from src.services.ticket_service import TicketService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/home')
@login_required
def home():
    """Página inicial do dashboard"""
    try:
        ticket_service = TicketService()
        stats = ticket_service.obter_estatisticas()
        
        recent_tickets = []
        if session.get('user', {}).get('role') == 'admin':
            all_tickets = ticket_service.listar_tickets()
            recent_tickets = all_tickets[:5]
        
        return render_template('home.html', stats=stats, recent_tickets=recent_tickets)
    except Exception as e:
        print(f"Erro ao carregar a página inicial: {e}")
        empty_stats = {'total_tickets': 0, 'pendentes': 0, 'em_andamento': 0, 'concluidos': 0}
        return render_template('home.html', error="Não foi possível carregar os dados da página inicial.", stats=empty_stats)

@dashboard_bp.route('/stats')
@admin_required
def stats():
    """
    Página de estatísticas e relatórios (apenas admin).
    Esta rota agora apenas renderiza a estrutura da página.
    Os gráficos são carregados pela API em graphics_routes.py.
    """
    try:
        ticket_service = TicketService()
        stats = ticket_service.obter_estatisticas()
        
        metricas = {
            'total_tickets': stats.get('total_tickets', 0),
            'pendentes': stats.get('pendentes', 0),
            'em_andamento': stats.get('em_andamento', 0),
            'concluidos': stats.get('concluidos', 0)
        }
        
        return render_template('reports.html', stats=metricas)
    except Exception as e:
        print(f"Erro ao carregar a página de relatórios: {e}")
        return render_template('reports.html', error="Não foi possível carregar os dados dos relatórios.")

@dashboard_bp.route('/api/metrics')
@login_required
def api_metrics():
    """API para obter métricas atualizadas"""
    ticket_service = TicketService()
    stats = ticket_service.obter_estatisticas()
    return jsonify(stats)

# Importa session no final para evitar import circular
from flask import session

