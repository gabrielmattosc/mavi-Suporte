from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from src.routes.auth_routes import admin_required
from src.services.ticket_service import TicketService
from src.services.auth_service import AuthService
from src.services.log_service import LogService
from src.services.email_service import email_service

"""ADD database import e models no route"""
from src.services.database_service import db
from src.models.produto import Produto

from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def index():
    status_filter = request.args.get('status', 'Todos')
    prioridade_filter = request.args.get('prioridade', 'Todas')
    active_tab = request.args.get('tab', 'tickets')
    try:
        scroll_position = float(request.args.get('scroll', 0))  # aceita valores decimais
    except ValueError:
        scroll_position = 0

    filtros = {}
    if status_filter != 'Todos':
        filtros['status'] = status_filter
    if prioridade_filter != 'Todas':
        filtros['prioridade'] = prioridade_filter

    tickets = TicketService.listar_tickets(filtros)
    stats = TicketService.obter_estatisticas()
    logs = LogService.listar_logs()
    produtos = Produto.query.order_by(Produto.data_cadastro.desc()).all()

    return render_template('admin_dashboard.html', 
                           tickets=tickets, 
                           stats=stats,
                           logs=logs,
                           produtos=produtos,
                           status_filter=status_filter,
                           prioridade_filter=prioridade_filter,
                           active_tab=active_tab,
                           scroll_position=scroll_position)

@admin_bp.route('/ticket/<ticket_id>')
@admin_required
def view_ticket(ticket_id):
    ticket = TicketService.obter_ticket(ticket_id.upper())
    if not ticket:
        flash('Ticket não encontrado.', 'error')
        return redirect(url_for('admin.index'))
    return render_template('admin_ticket_detail.html', ticket=ticket)

@admin_bp.route('/update-status', methods=['POST'])
@admin_required
def update_status():
    ticket_id = request.form.get('ticket_id')
    novo_status = request.form.get('status')
    observacao = request.form.get('observacao', '')
    if not ticket_id or not novo_status:
        flash('Dados incompletos para atualização.', 'error')
        return redirect(url_for('admin.index'))
    sucesso = TicketService.atualizar_status(ticket_id, novo_status, observacao)
    if sucesso:
        LogService.registrar_log(
            usuario=session['user']['username'],
            acao="Atualização de Status",
            detalhes=f"Ticket #{ticket_id} para '{novo_status}'"
        )
        ticket = TicketService.obter_ticket(ticket_id)
        if ticket and 'email' in ticket:
            try:
                enviado = email_service.enviar_atualizacao_status(
                    ticket['email'],
                    ticket_id,
                    novo_status,
                    observacao,
                    ticket['nome']
                )
                email_service.enviar_notificacao_admin(ticket_id, ticket)
                if enviado:
                    flash('E-mail de atualização enviado ao solicitante.', 'info')
                else:
                    flash('Falha ao enviar e-mail ao solicitante.', 'warning')
            except Exception as e:
                flash(f'Erro ao enviar e-mail: {str(e)}', 'warning')
        flash(f'Status do ticket #{ticket_id} atualizado para "{novo_status}".', 'success')
    else:
        flash('Erro ao atualizar status do ticket.', 'error')
    return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))

@admin_bp.route('/api/update-status', methods=['POST'])
@admin_required
def api_update_status():
    try:
        data = request.get_json()
        ticket_id = data.get('ticket_id')
        novo_status = data.get('status')
        observacao = data.get('observacao', '')
        if not ticket_id or not novo_status:
            return jsonify({'success': False, 'message': 'Dados incompletos'})
        sucesso = TicketService.atualizar_status(ticket_id, novo_status, observacao)
        if sucesso:
            LogService.registrar_log(
                usuario=session['user']['username'],
                acao="Atualização de Status (API)",
                detalhes=f"Ticket #{ticket_id} para '{novo_status}'"
            )
            ticket = TicketService.obter_ticket(ticket_id)
            if ticket and 'email' in ticket:
                try:
                    email_service.enviar_atualizacao_status(
                        ticket['email'],
                        ticket_id,
                        novo_status,
                        observacao,
                        ticket['nome']
                    )
                    email_service.enviar_notificacao_admin(ticket_id, ticket)
                except Exception as e:
                    return jsonify({'success': True, 'message': f'Status atualizado, mas erro ao enviar e-mail: {str(e)}'})
            return jsonify({'success': True, 'message': 'Status atualizado com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao atualizar status'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/cadastrar-produto', methods=['POST'])
@admin_required
def cadastrar_produto():
    dispositivos_validos = [
        "Notebook/Laptop",
        "Desktop/PC",
        "Teclado",
        "Mouse",
        "Headset/Fone",
        "Webcam",
        "Licença de software"
    ]

    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    quantidade = request.form.get('quantidade')
    try:
        scroll_position = float(request.form.get('scroll', 0))
    except ValueError:
        scroll_position = 0

    if not nome or not quantidade:
        flash('Nome e quantidade são obrigatórios.', 'error')
        return redirect(url_for('admin.index', tab='produtos', scroll=scroll_position))

    if nome not in dispositivos_validos:
        flash('Produto inválido. Escolha um dispositivo da lista.', 'error')
        return redirect(url_for('admin.index', tab='produtos', scroll=scroll_position))

    try:
        produto_existente = Produto.query.filter_by(nome=nome).first()
        if produto_existente:
            produto_existente.quantidade += int(quantidade)
            if descricao:
                produto_existente.descricao = descricao
            db.session.commit()
            flash('Quantidade do produto atualizada com sucesso!', 'success')
        else:
            produto_existente = Produto(
                nome=nome,
                descricao=descricao,
                quantidade=int(quantidade)
            )
            db.session.add(produto_existente)
            db.session.commit()
            flash('Produto cadastrado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar produto: {str(e)}', 'error')

    return redirect(url_for('admin.index', tab='produtos', scroll=scroll_position))


@admin_bp.route('/users')
@admin_required
def users():
    """Gerenciamento de usuários"""
    # Esta funcionalidade pode ser expandida futuramente
    flash('Funcionalidade de gerenciamento de usuários em desenvolvimento.', 'info')
    return redirect(url_for('admin.index'))

@admin_bp.route('/reports')
@admin_required
def reports():
    """Configurações do sistema"""
    flash('Funcionalidade de configurações em desenvolvimento.', 'info')
    return redirect(url_for('admin.index'))

@admin_bp.route('/settings')
@admin_required
def settings():
    """Configurações do sistema"""
    flash('Funcionalidade de configurações em desenvolvimento.', 'info')
    return redirect(url_for('admin.index'))
