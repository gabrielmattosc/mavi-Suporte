from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_session import Session
from email_service import get_email_service
from reports import ReportGenerator
from database import ticket_manager, user_manager
from io import BytesIO
from functools import wraps
import plotly.express as px
import pandas as pd

app = Flask(__name__)
app.secret_key = 'mudesecret'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Decorator de login
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u = user_manager.autenticar(request.form['username'], request.form['password'])
        if u:
            session['user'] = u
            return redirect(url_for('home'))
        flash('Credenciais inválidas','danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    stats = ticket_manager.obter_estatisticas()
    return render_template('home.html', stats=stats, user=session['user'])

@app.route('/ticket/new', methods=['GET','POST'])
@login_required
def new_ticket():
    if request.method=='POST':
        dados = {
            'nome': request.form['nome'],
            'email': request.form['email'],
            'squad_leader': request.form['squad_leader'],
            'dispositivos': request.form.getlist('dispositivos'),
            'necessidade': request.form['necessidade'],
            'prioridade': request.form['prioridade']
        }
        dados['dispositivos'] = ', '.join(dados['dispositivos'])
        tid = ticket_manager.criar_ticket(dados)
        pos = ticket_manager.obter_posicao_fila(tid)
        email_svc = get_email_service()
        if email_svc.enabled:
            email_svc.enviar_confirmacao_ticket(dados['email'], tid, pos, dados)
            email_svc.enviar_notificacao_admin(tid, dados)
        return redirect(url_for('view_ticket', ticket_id=tid))
    return render_template('new_ticket.html')

@app.route('/ticket/<ticket_id>')
@login_required
def view_ticket(ticket_id):
    t = ticket_manager.obter_ticket(ticket_id)
    if not t:
        flash('Ticket não encontrado','warning')
        return redirect(url_for('home'))
    pos = ticket_manager.obter_posicao_fila(ticket_id) if t['status']=='Pendente' else None
    return render_template('view_ticket.html', ticket=t, pos=pos)

@app.route('/dashboard')
@login_required
def dashboard():
    stats = ticket_manager.obter_estatisticas()
    tickets = ticket_manager.listar_tickets()
    df = pd.DataFrame(tickets)
    fig = None
    if not df.empty:
        df['data'] = pd.to_datetime(df['data_criacao']).dt.date
        timeline = df.groupby('data').size().reset_index(name='qtd')
        fig = px.line(timeline, x='data', y='qtd', title='Tickets por Dia')
        fig = fig.to_html(full_html=False)
    return render_template('dashboard.html', stats=stats, chart=fig)

@app.route('/reports/pdf')
@login_required
def download_pdf():
    rg = ReportGenerator()
    buf = rg.generate_pdf_report('Relatório Completo')
    return send_file(buf, download_name='relatorio.pdf', as_attachment=True)

@app.route('/admin')
@login_required
def admin():
    if session['user']['role']!='admin':
        flash('Acesso negado','danger')
        return redirect(url_for('home'))
    tickets = ticket_manager.listar_tickets()
    return render_template('admin.html', tickets=tickets)

@app.route('/admin/ticket/<ticket_id>/status', methods=['POST'])
@login_required
def update_status(ticket_id):
    if session['user']['role']!='admin':
        flash('Acesso negado','danger'); return redirect(url_for('home'))
    novo = request.form['status']
    obs = request.form.get('observacao')
    ticket_manager.atualizar_status(ticket_id, novo, obs)
    return redirect(url_for('admin'))

if __name__=='__main__':
    app.run(debug=True)