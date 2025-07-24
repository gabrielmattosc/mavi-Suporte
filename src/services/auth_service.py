"""
Serviço de autenticação para o sistema Mavi Suporte
"""
from typing import Optional, Dict, Any
from src.services.database_service import User

class AuthService:
    """Serviço para operações de autenticação"""
    
    @staticmethod
    def autenticar_usuario(username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica um usuário"""
        try:
            user = User.query.filter_by(username=username, password=password).first()
            return user.to_dict() if user else None
        except Exception as e:
            print(f"Erro na autenticação: {str(e)}")
            return None
    
    @staticmethod
    def obter_usuario(username: str) -> Optional[Dict[str, Any]]:
        """Obtém dados de um usuário pelo username"""
        try:
            user = User.query.filter_by(username=username).first()
            return user.to_dict() if user else None
        except Exception as e:
            print(f"Erro ao buscar usuário: {str(e)}")
            return None
    
    @staticmethod
    def criar_usuario(dados: Dict[str, Any]) -> bool:
        """Cria um novo usuário"""
        try:
            # Verifica se o usuário já existe
            if User.query.filter_by(username=dados['username']).first():
                return False
            
            if User.query.filter_by(email=dados['email']).first():
                return False
            
            user = User(
                username=dados['username'],
                password=dados['password'],  # Em produção, usar hash
                email=dados['email'],
                role=dados.get('role', 'user')
            )
            
            from src.services.database_service import db
            db.session.add(user)
            db.session.commit()
            
            return True
            
        except Exception as e:
            from src.services.database_service import db
            db.session.rollback()
            print(f"Erro ao criar usuário: {str(e)}")
            return False

