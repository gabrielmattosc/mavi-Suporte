"""
Módulo de autenticação para o sistema Mavi Suporte
"""

import streamlit as st
import hashlib

class AuthManager:
    """Gerenciador de autenticação"""
    
    def __init__(self):
        # Usuários do sistema
        self.users = {
            'teste': {
                'password': self._hash_password('teste123'),
                'role': 'user',
                'name': 'Usuário Teste',
                'permissions': ['create_ticket']
            },
            'admin': {
                'password': self._hash_password('admin123'),
                'role': 'admin',
                'name': 'Administrador',
                'permissions': ['create_ticket', 'view_dashboard', 'view_reports', 'manage_system']
            }
        }
    
    def _hash_password(self, password):
        """Hash da senha usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Autentica um usuário"""
        if username in self.users:
            hashed_password = self._hash_password(password)
            if self.users[username]['password'] == hashed_password:
                return True
        return False
    
    def get_user_info(self, username):
        """Retorna informações do usuário"""
        if username in self.users:
            user_info = self.users[username].copy()
            del user_info['password']  # Remove a senha das informações retornadas
            return user_info
        return None
    
    def has_permission(self, username, permission):
        """Verifica se o usuário tem uma permissão específica"""
        user_info = self.get_user_info(username)
        if user_info:
            return permission in user_info['permissions']
        return False
    
    def login_user(self, username):
        """Faz login do usuário na sessão"""
        user_info = self.get_user_info(username)
        if user_info:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = user_info['role']
            st.session_state.user_name = user_info['name']
            st.session_state.user_permissions = user_info['permissions']
            return True
        return False
    
    def logout_user(self):
        """Faz logout do usuário"""
        for key in ['logged_in', 'username', 'user_role', 'user_name', 'user_permissions']:
            if key in st.session_state:
                del st.session_state[key]
    
    def is_logged_in(self):
        """Verifica se há um usuário logado"""
        return st.session_state.get('logged_in', False)
    
    def get_current_user(self):
        """Retorna informações do usuário atual"""
        if self.is_logged_in():
            return {
                'username': st.session_state.get('username'),
                'role': st.session_state.get('user_role'),
                'name': st.session_state.get('user_name'),
                'permissions': st.session_state.get('user_permissions', [])
            }
        return None
    
    def require_permission(self, permission):
        """Decorator para verificar permissões"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.is_logged_in():
                    st.error("❌ Você precisa estar logado para acessar esta funcionalidade.")
                    return None
                
                current_user = self.get_current_user()
                if permission not in current_user['permissions']:
                    st.error("❌ Você não tem permissão para acessar esta funcionalidade.")
                    return None
                
                return func(*args, **kwargs)
            return wrapper
        return decorator

def show_login_page():
    """Exibe a página de login"""
    from styles_updated import get_custom_components
    import base64
    import os
    
    components = get_custom_components()
    
    # Carrega e codifica o logo
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'mavi.logo.png')
    logo_base64 = ""
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode()
    
    # Header com logo
    if logo_base64:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <img src="data:image/png;base64,{logo_base64}" style="height: 80px; margin-bottom: 1rem;" alt="Mavi Logo">
            <h3 style="color: #00BFFF; margin-bottom: 3rem; font-weight: 300;">Sistema de Gestão de Solicitações</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1 style="color: #168da6; margin-bottom: 2rem; font-weight: 400; letter-spacing: 2px;">🎯 MAVI SUPORTE</h1>
            <h3 style="color: #00BFFF; margin-bottom: 3rem; font-weight: 300;">Sistema de Gestão de Solicitações</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Container centralizado para o login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(components['login_container_start'], unsafe_allow_html=True)
        
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input(
                "👤 Usuário",
                placeholder="Digite seu usuário"
            )
            
            password = st.text_input(
                "🔒 Senha",
                type="password",
                placeholder="Digite sua senha"
            )
            
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            
            if submitted:
                auth_manager = AuthManager()
                
                if not username or not password:
                    st.error("❌ Por favor, preencha todos os campos.")
                elif auth_manager.authenticate(username, password):
                    auth_manager.login_user(username)
                    st.success("✅ Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")
        
        # Informações de acesso
        st.markdown("---")
        st.markdown("**👥 Usuários de Teste:**")
        st.markdown("""
        - **Usuário:** `teste` | **Senha:** `teste123` (Acesso limitado - apenas criação de tickets)
        - **Usuário:** `admin` | **Senha:** `admin123` (Acesso completo)
        """)
        
        st.markdown(components['login_container_end'], unsafe_allow_html=True)

def show_user_info():
    """Exibe informações do usuário logado"""
    auth_manager = AuthManager()
    current_user = auth_manager.get_current_user()
    
    if current_user:
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**👤 Usuário:** {current_user['name']}")
            st.markdown(f"**🎭 Perfil:** {current_user['role'].title()}")
            
            if st.button("🚪 Logout", use_container_width=True):
                auth_manager.logout_user()
                st.rerun()

def require_login():
    """Verifica se o usuário está logado"""
    auth_manager = AuthManager()
    if not auth_manager.is_logged_in():
        show_login_page()
        return False
    return True

def has_permission(permission):
    """Verifica se o usuário atual tem uma permissão específica"""
    auth_manager = AuthManager()
    current_user = auth_manager.get_current_user()
    if current_user:
        return permission in current_user['permissions']
    return False

