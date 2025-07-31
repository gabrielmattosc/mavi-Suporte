"""
Rotas de administração para o sistema Mavi Suporte
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from src.routes.auth_routes import admin_required
from src.services.ticket_service import TicketService
from src.services.log_service import LogService
from src.services.product_service import ProductService
from src.services.email_service import email_service

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@admin_required
def index():
    """Página principal de administração com todas as abas."""
    try:
        status_filter = request.args.get('status', 'Todos')
        prioridade_filter = request.args.get('prioridade', 'Todas')
        active_tab = request.args.get('tab', 'tickets')
        scroll_position = request.args.get('scroll', 0)

        filtros = {}
        if status_filter != 'Todos':
            filtros['status'] = status_filter
        if prioridade_filter != 'Todas':
            filtros['prioridade'] = prioridade_filter

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
        flash(f"Erro ao carregar o painel de administração: {e}", "error")
        return render_template('admin_dashboard.html', error=True, tickets=[], stats={}, logs=[], produtos=[])


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

        sucesso = ProductService.cadastrar_ou_atualizar_produto(
            nome=nome, 
            quantidade=quantidade, 
            descricao=descricao, 
            modificado_por=session['user']['username']
        )
        
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

# --- NOVA ROTA PARA ATUALIZAR A QUANTIDADE DO PRODUTO ---
@admin_bp.route('/product/update-quantity', methods=['POST'])
@admin_required
def update_product_quantity():
    """Atualiza a quantidade de um produto."""
    produto_id = request.form.get('produto_id')
    nova_quantidade_str = request.form.get('quantidade')
    scroll_position = request.form.get('scroll', 0)

    if not produto_id or not nova_quantidade_str:
        flash('Dados inválidos para atualização de quantidade.', 'error')
        return redirect(url_for('admin.index', tab='produtos', scroll=scroll_position))

    try:
        nova_quantidade = int(nova_quantidade_str)
        if nova_quantidade < 0:
            flash('A quantidade não pode ser negativa.', 'error')
            return redirect(url_for('admin.index', tab='produtos', scroll=scroll_position))

        sucesso = ProductService.atualizar_quantidade_produto(
            produto_id=int(produto_id),
            nova_quantidade=nova_quantidade,
            modificado_por=session['user']['username']
        )

        if sucesso:
            flash('Quantidade do produto atualizada com sucesso!', 'success')
            LogService.registrar_log(
                usuario=session['user']['username'],
                acao="Update de Quantidade de Produto",
                detalhes=f"Quantidade do produto ID #{produto_id} alterada para {nova_quantidade}"
            )
        else:
            flash('Erro ao atualizar a quantidade do produto.', 'error')

    except ValueError:
        flash('A quantidade deve ser um número válido.', 'error')
    except Exception as e:
        flash(f'Erro ao atualizar quantidade: {str(e)}', 'error')

    return redirect(url_for('admin.index', tab='produtos', scroll=scroll_position))

@admin_bp.route('/product/<int:product_id>/history')
@admin_required
def view_product_history(product_id):
    """Exibe a página com o histórico de descrições de um produto."""
    produto = ProductService.obter_produto_com_historico(product_id)
    if not produto:
        flash("Produto não encontrado.", "error")
        return redirect(url_for('admin.index', tab='produtos'))
    
    return render_template('product_description_history.html', produto=produto)

# --- NOVA ROTA PARA EDITAR A DESCRIÇÃO ATUAL ---
@admin_bp.route('/product/<int:product_id>/edit-description', methods=['POST'])
@admin_required
def edit_current_description(product_id):
    """Edita a descrição atual de um produto."""
    nova_descricao = request.form.get('descricao')
    if not nova_descricao:
        flash("A nova descrição não pode estar vazia.", "error")
        return redirect(url_for('admin.view_product_history', product_id=product_id))

    sucesso = ProductService.editar_descricao_atual(
        produto_id=product_id,
        nova_descricao=nova_descricao,
        modificado_por=session['user']['username']
    )

    if sucesso:
        flash("Descrição atualizada com sucesso.", "success")
        LogService.registrar_log(
            usuario=session['user']['username'],
            acao="Edição de Descrição de Produto",
            detalhes=f"Descrição do produto ID #{product_id} foi alterada."
        )
    else:
        flash("Erro ao atualizar a descrição.", "error")
    
    return redirect(url_for('admin.view_product_history', product_id=product_id))

# --- NOVA ROTA PARA EDITAR UMA DESCRIÇÃO DO HISTÓRICO ---
@admin_bp.route('/product/history/edit/<int:history_id>', methods=['POST'])
@admin_required
def edit_history_description(history_id):
    """Edita uma entrada do histórico de descrições."""
    nova_descricao = request.form.get('descricao_historico')
    produto_id = request.form.get('produto_id')

    if not nova_descricao:
        flash("A descrição do histórico não pode estar vazia.", "error")
        return redirect(url_for('admin.view_product_history', product_id=produto_id))

    sucesso = ProductService.editar_descricao_historico(history_id, nova_descricao)

    if sucesso:
        flash("Entrada do histórico atualizada com sucesso.", "success")
        LogService.registrar_log(
            usuario=session['user']['username'],
            acao="Edição de Histórico de Produto",
            detalhes=f"Entrada de histórico ID #{history_id} foi editada."
        )
    else:
        flash("Erro ao atualizar a entrada do histórico.", "error")
    
    return redirect(url_for('admin.view_product_history', product_id=produto_id))


@admin_bp.route('/product/history/delete/<int:history_id>', methods=['POST'])
@admin_required
def delete_description_history(history_id):
    """Apaga uma entrada do histórico de descrições e reverte o estoque."""
    produto_id = request.form.get('produto_id')
    sucesso = ProductService.deletar_entrada_historico(history_id)

    if sucesso:
        flash("Entrada do histórico apagada e estoque revertido com sucesso.", "success")
        LogService.registrar_log(
            usuario=session['user']['username'],
            acao="Exclusão de Histórico de Produto",
            detalhes=f"Entrada de histórico ID #{history_id} apagada e estoque revertido."
        )
    else:
        flash("Erro ao apagar a entrada do histórico.", "error")
    
    return redirect(url_for('admin.view_product_history', product_id=produto_id))

# --- NOVA ROTA ADICIONADA AQUI ---
@admin_bp.route('/product/<int:product_id>/revert', methods=['POST'])
@admin_required
def revert_description(product_id):
    """Reverte a descrição atual de um produto para a última do histórico."""
    sucesso = ProductService.reverter_descricao_atual(product_id, session['user']['username'])

    if sucesso:
        flash("Descrição revertida para a versão anterior com sucesso.", "success")
        LogService.registrar_log(
            usuario=session['user']['username'],
            acao="Reversão de Descrição de Produto",
            detalhes=f"Descrição do produto ID #{product_id} foi revertida."
        )
    else:
        flash("Não foi possível reverter a descrição. O produto pode não ter um histórico ou a descrição já é a mais antiga.", "warning")
    
    return redirect(url_for('admin.view_product_history', product_id=product_id))

# --- ROTAS ADICIONAIS ---
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