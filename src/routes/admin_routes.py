"""
Rotas de administração para o sistema Mavi Suporte
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from src.routes.auth_routes import admin_required
from src.services.ticket_service import TicketService
from src.services.auth_service import AuthService
from src.services.log_service import LogService
from src.services.email_service import email_service
# --- NOVO: Importa o serviço de produtos ---
from src.services.product_service import ProductService

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@admin_required
def index():
    """Página principal de administração com todas as abas."""
    try:
        # Parâmetros para manter o estado da página (aba ativa e scroll)
        status_filter = request.args.get('status', 'Todos')
        prioridade_filter = request.args.get('prioridade', 'Todas')
        active_tab = request.args.get('tab', 'tickets')
        scroll_position = request.args.get('scroll', 0)

        # Filtros para a aba de tickets
        filtros = {}
        if status_filter != 'Todos':
            filtros['status'] = status_filter
        if prioridade_filter != 'Todas':
            filtros['prioridade'] = prioridade_filter

        # Busca todos os dados necessários para o painel
        tickets = TicketService.listar_tickets(filtros)
        stats = TicketService.obter_estatisticas()
        logs = LogService.listar_logs()
        produtos = ProductService.listar_produtos()

        return render_template('admin_dashboard.html', 
                               tickets=tickets, 
                               stats=stats,
                               logs=logs,
                               produtos=produtos,
                               status_filter=status_filter,
                               prioridade_filter=prioridade_filter,
                               active_tab=active_tab,
                               scroll_position=scroll_position)
    except Exception as e:
        print(f"Erro ao carregar o dashboard de admin: {e}")
        flash("Ocorreu um erro ao carregar o painel de administração.", "error")
        # Retorna um template de erro ou a página com valores vazios para não quebrar
        return render_template('admin_dashboard.html', tickets=[], stats={}, logs=[], produtos=[], error=True)


@admin_bp.route('/ticket/<ticket_id>')
@admin_required
def view_ticket(ticket_id):
    """Visualiza ticket específico (admin)"""
    ticket = TicketService.obter_ticket(ticket_id.upper())
    if not ticket:
        flash('Ticket não encontrado.', 'error')
        return redirect(url_for('admin.index'))
    return render_template('admin_ticket_detail.html', ticket=ticket)

@admin_bp.route('/update-status', methods=['POST'])
@admin_required
def update_status():
    """Atualiza status de um ticket"""
    ticket_id = request.form.get('ticket_id')
    novo_status = request.form.get('status')
    observacao = request.form.get('observacao', '')
    
    if not ticket_id or not novo_status:
        flash('Dados incompletos para atualização.', 'error')
        return redirect(url_for('admin.index', tab='atualizar'))
    
    sucesso = TicketService.atualizar_status(ticket_id, novo_status, observacao)
    
    if sucesso:
        LogService.registrar_log(
            usuario=session['user']['username'],
            acao="Atualização de Status",
            detalhes=f"Ticket #{ticket_id} para '{novo_status}'"
        )
        flash(f'Status do ticket #{ticket_id} atualizado para "{novo_status}".', 'success')
        # Lógica de envio de email
        ticket = TicketService.obter_ticket(ticket_id)
        if ticket and email_service.enabled:
            email_service.enviar_atualizacao_status(
                ticket['email'], ticket_id, novo_status, observacao, ticket['nome']
            )
    else:
        flash('Erro ao atualizar status do ticket.', 'error')
    
    return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))

@admin_bp.route('/cadastrar-produto', methods=['POST'])
@admin_required
def cadastrar_produto():
    """Cadastra um novo produto ou atualiza a quantidade de um existente."""
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    quantidade_str = request.form.get('quantidade')
    scroll_position = request.form.get('scroll', 0)

    if not nome or not quantidade_str:
        flash('Nome e quantidade são obrigatórios.', 'error')
        return redirect(url_for('admin.index', tab='produtos', scroll=scroll_position))

    try:
        quantidade = int(quantidade_str)
        if quantidade <= 0:
            flash('A quantidade deve ser um número positivo.', 'error')
            return redirect(url_for('admin.index', tab='produtos', scroll=scroll_position))

        sucesso = ProductService.cadastrar_ou_atualizar_produto(nome, quantidade, descricao)
        
        if sucesso:
            flash('Produto salvo com sucesso!', 'success')
            LogService.registrar_log(
                usuario=session['user']['username'],
                acao="Cadastro/Update de Produto",
                detalhes=f"Produto: {nome}, Quantidade adicionada: {quantidade}"
            )
        else:
            flash('Erro ao salvar o produto.', 'error')

    except ValueError:
        flash('A quantidade deve ser um número válido.', 'error')
    except Exception as e:
        flash(f'Erro ao cadastrar produto: {str(e)}', 'error')

    return redirect(url_for('admin.index', tab='produtos', scroll=scroll_position))


@admin_bp.route('/users')
@admin_required
def users():
    """Gerenciamento de usuários"""
    flash('Funcionalidade de gerenciamento de usuários em desenvolvimento.', 'info')
    return redirect(url_for('admin.index'))

@admin_bp.route('/reports')
@admin_required
def reports():
    """Redireciona para a página de relatórios principal"""
    return redirect(url_for('dashboard.reports_page'))

@admin_bp.route('/settings')
@admin_required
def settings():
    """Configurações do sistema"""
    flash('Funcionalidade de configurações em desenvolvimento.', 'info')
    return redirect(url_for('admin.index'))
