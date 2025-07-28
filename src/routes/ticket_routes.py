"""
Rotas de tickets para o sistema Mavi Suporte
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from src.routes.auth_routes import login_required
from src.services.ticket_service import TicketService
from src.services.email_service import email_service

ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/new')
@login_required
def new():
    """Página de nova solicitação"""
    return render_template('new_ticket.html')

@ticket_bp.route('/create', methods=['POST'])
@login_required
def create():
    """Cria um novo ticket"""
    try:
        # Coleta dados do formulário
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        squad_leader = request.form.get('squad_leader', '').strip()
        prioridade = request.form.get('prioridade', 'Normal')
        dispositivos_list = request.form.getlist('dispositivos')
        necessidade = request.form.get('necessidade', '').strip()
        aceita_termos = request.form.get('aceita_termos')
        
        # Validação
        if not all([nome, email, squad_leader, necessidade]) or not dispositivos_list or not aceita_termos:
            flash('Por favor, preencha todos os campos obrigatórios e aceite os termos.', 'error')
            return render_template('new_ticket.html')
        
        # Prepara dados do ticket
        dados_ticket = {
            "nome": nome,
            "email": email,
            "squad_leader": squad_leader,
            "dispositivos": ", ".join(dispositivos_list),
            "necessidade": necessidade,
            "prioridade": prioridade
        }
        
        # Cria o ticket
        ticket_service = TicketService()
        ticket_id = ticket_service.criar_ticket(dados_ticket)
        
        if ticket_id:
            # Obtém posição na fila
            posicao_fila = ticket_service.obter_posicao_fila(ticket_id)
            
            # Envia emails se configurado
            if email_service.enabled:
                email_service.enviar_confirmacao_ticket(
                    email, ticket_id, posicao_fila, dados_ticket
                )
                email_service.enviar_notificacao_admin(
                    ticket_id, dados_ticket
                )
            
            flash(f'Solicitação criada com sucesso! ID do ticket: #{ticket_id}', 'success')
            return redirect(url_for('ticket.success', ticket_id=ticket_id, posicao=posicao_fila))
        else:
            flash('Erro ao criar solicitação. Tente novamente.', 'error')
            return render_template('new_ticket.html')
            
    except Exception as e:
        print(f"Erro ao criar ticket: {str(e)}")
        flash('Erro interno do servidor. Tente novamente.', 'error')
        return render_template('new_ticket.html')

@ticket_bp.route('/success')
@login_required
def success():
    """Página de sucesso após criar ticket"""
    ticket_id = request.args.get('ticket_id')
    posicao = request.args.get('posicao', 0)
    
    if not ticket_id:
        return redirect(url_for('ticket.new'))
    
    return render_template('ticket_success.html', ticket_id=ticket_id, posicao=posicao)

@ticket_bp.route('/search')
@login_required
def search():
    """Página de consulta de ticket"""
    return render_template('search_ticket.html')

@ticket_bp.route('/view/<ticket_id>')
@login_required
def view(ticket_id):
    """Visualiza um ticket específico"""
    ticket_service = TicketService()
    ticket = ticket_service.obter_ticket(ticket_id.upper())
    
    if not ticket:
        flash('Ticket não encontrado. Verifique o ID e tente novamente.', 'error')
        return redirect(url_for('ticket.search'))
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Adiciona a posição na fila diretamente ao dicionário do ticket
    # para que o template possa acedê-la facilmente.
    ticket['posicao_fila'] = 0
    if ticket.get('status') == 'Pendente':
        ticket['posicao_fila'] = ticket_service.obter_posicao_fila(ticket_id)
    
    # Agora só precisamos de passar o objeto 'ticket'
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
