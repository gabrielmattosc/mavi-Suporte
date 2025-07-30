"""
Rotas de tickets para o sistema Mavi Suporte
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from src.routes.auth_routes import login_required
from src.services.ticket_service import TicketService
from src.services.email_service import email_service
from src.services.log_service import LogService
# --- NOVO: Importa o novo serviço de produtos ---
from src.services.product_service import ProductService

ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/new')
@login_required
def new():
    """Página de nova solicitação"""
    return render_template('new_ticket.html')

@ticket_bp.route('/create', methods=['POST'])
@login_required
def create():
    """Cria um novo ticket com prioridade automática e atualiza o estoque"""
    try:
        # Coleta dados do formulário
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        squad_leader = request.form.get('squad_leader', '').strip()
        # A linha que pegava a prioridade do formulário foi removida
        dispositivos_list = request.form.getlist('dispositivos')
        necessidade = request.form.get('necessidade', '').strip()
        aceita_termos = request.form.get('aceita_termos')
        
        if not all([nome, email, squad_leader, necessidade]) or not dispositivos_list:
            return render_template('new_ticket.html', form_data=request.form)
        
        # --- ALTERAÇÃO PRINCIPAL APLICADA AQUI ---
        # A prioridade agora é determinada automaticamente pela lógica de negócio
        prioridade = TicketService.determinar_prioridade(dispositivos_list)
        
        dados_ticket = {
            "nome": nome, "email": email, "squad_leader": squad_leader,
            "dispositivos": ", ".join(dispositivos_list),
            "necessidade": necessidade, "prioridade": prioridade # Usa a prioridade automática
        }
        
        ticket_id = TicketService.criar_ticket(dados_ticket)
        
        if ticket_id:
            # Atualiza o estoque dos itens solicitados
            for item in dispositivos_list:
                sucesso_baixa = ProductService.decrementar_estoque(item)
                if not sucesso_baixa:
                    flash(f'Aviso: Esse item "{item}". Não é do estoque', 'warning')
                    
            # Registra a ação no log, agora com a prioridade automática
            LogService.registrar_log(
                usuario=session['user']['username'],
                acao="Criação de Ticket",
                detalhes=f"Ticket #{ticket_id} (Prioridade: {prioridade}) criado por {nome}."
            )
            
            posicao_fila = TicketService.obter_posicao_fila(ticket_id)
            
            if email_service.enabled:
                email_service.enviar_confirmacao_ticket(email, ticket_id, posicao_fila, dados_ticket)
                email_service.enviar_notificacao_admin(ticket_id, dados_ticket)
            
            flash(f'Solicitação criada com sucesso! ID do ticket: #{ticket_id}', 'success')
            return redirect(url_for('ticket.success', ticket_id=ticket_id, posicao=posicao_fila))
        else:
            flash('Erro ao criar solicitação. Tente novamente.', 'error')
            return render_template('new_ticket.html', form_data=request.form)
            
    except Exception as e:
        print(f"Erro ao criar ticket: {str(e)}")
        flash('Erro interno do servidor. Tente novamente.', 'error')
        return render_template('new_ticket.html', form_data=request.form)

@ticket_bp.route('/success')
@login_required
def success():
    """Página de sucesso após criar ticket"""
    ticket_id = request.args.get('ticket_id')
    posicao = request.args.get('posicao', 0)
    
    if not ticket_id:
        return redirect(url_for('ticket.new'))
    
    return render_template('ticket_success.html', ticket_id=ticket_id, posicao=posicao)

@ticket_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Página de consulta de ticket por ID ou Email, com paginação."""
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            flash('Por favor, insira um ID de ticket ou um email para pesquisar.', 'warning')
            return redirect(url_for('ticket.search'))
        return redirect(url_for('ticket.search', query=query))

    query = request.args.get('query')
    if not query:
        return render_template('search_ticket.html')

    ticket_service = TicketService()
    ticket_by_id = ticket_service.obter_ticket(query.upper())
    if ticket_by_id:
        return redirect(url_for('ticket.view', ticket_id=ticket_by_id['ticket_id']))

    page = request.args.get('page', 1, type=int)
    tickets_pagination = ticket_service.listar_tickets_por_email_paginado(query.lower(), page=page, per_page=5)
    
    if tickets_pagination and tickets_pagination.items:
        return render_template('search_results.html', pagination=tickets_pagination, query=query)

    flash(f'Nenhum ticket encontrado para "{query}". Verifique os dados e tente novamente.', 'error')
    return redirect(url_for('ticket.search'))


@ticket_bp.route('/view/<ticket_id>')
@login_required
def view(ticket_id):
    """Visualiza um ticket específico"""
    ticket_service = TicketService()
    ticket = ticket_service.obter_ticket(ticket_id.upper())
    
    if not ticket:
        flash('Ticket não encontrado.', 'error')
        return redirect(url_for('ticket.search'))
    
    ticket['posicao_fila'] = 0
    if ticket.get('status') == 'Pendente':
        ticket['posicao_fila'] = ticket_service.obter_posicao_fila(ticket_id)
    
    return render_template('view_ticket.html', ticket=ticket)

@ticket_bp.route('/api/search', methods=['POST'])
@login_required
def api_search():
    """API para buscar ticket"""
    ticket_id = request.form.get('ticket_id', '').strip().upper()
    
    if not ticket_id:
        return jsonify({'success': False, 'message': 'ID do ticket é obrigatório'})
    
    ticket_service = TicketService()
    ticket = ticket_service.obter_ticket(ticket_id)
    
    if ticket:
        return jsonify({
            'success': True, 
            'redirect': url_for('ticket.view', ticket_id=ticket_id)
        })
    else:
        return jsonify({
            'success': False, 
            'message': 'Ticket não encontrado. Verifique o ID e tente novamente.'
        })
