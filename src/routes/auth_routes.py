"""
Rotas de autenticação para o sistema Mavi Suporte
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.services.auth_service import AuthService
from src.services.log_service import LogService

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
        
        # A função autenticar_usuario agora apenas verifica as credenciais
        user = AuthService.autenticar_usuario(username, password)
        
        if user:
            # --- CORREÇÃO APLICADA AQUI ---
            # A sessão do usuário é definida aqui para garantir o login
            session['user'] = user
            # O log de sucesso é registrado aqui também
            LogService.registrar_log(username, "Login bem-sucedido")
            
            flash(f'Bem-vindo, {user["username"]}!', 'success')
            return redirect(url_for('dashboard.home'))
        else:
            # O AuthService já registra a tentativa de login falhada
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    try:
        username = session.get('user', {}).get('username', 'Desconhecido')
        LogService.registrar_log(username, "Logout")
    except Exception as e:
        print(f"Erro ao registrar log de logout: {e}")
    
    session.clear()
    
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

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
        
        if session.get('user', {}).get('role') != 'admin':
            flash('Você não tem permissão para acessar esta página.', 'error')
            return redirect(url_for('dashboard.home'))
        
        return view(**kwargs)
    
    wrapped_view.__name__ = view.__name__
    return wrapped_view
