"""
Rotas de autenticação para o sistema Mavi Suporte
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')
        
        user = AuthService.autenticar_usuario(username, password)
        
        if user:
            session['user'] = user
            flash(f'Bem-vindo, {user["username"]}!', 'success')
            return redirect(url_for('dashboard.home'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.before_app_request
def load_logged_in_user():
    """Carrega o usuário logado em todas as requisições"""
    user_id = session.get('user')
    
    if user_id is None:
        session['user'] = None
    else:
        session['user'] = user_id

def login_required(view):
    """Decorator para exigir login"""
    def wrapped_view(**kwargs):
        if session.get('user') is None:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    
    wrapped_view.__name__ = view.__name__
    return wrapped_view

def admin_required(view):
    """Decorator para exigir permissões de admin"""
    def wrapped_view(**kwargs):
        if session.get('user') is None:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        
        if session['user']['role'] != 'admin':
            flash('Você não tem permissão para acessar esta página.', 'error')
            return redirect(url_for('dashboard.home'))
        
        return view(**kwargs)
    
    wrapped_view.__name__ = view.__name__
    return wrapped_view

