"""
Serviço de gerenciamento de banco de dados para o sistema Mavi Suporte
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

# 1. Cria a ÚNICA instância do banco de dados para toda a aplicação
db = SQLAlchemy()

# 2. Importa todos os modelos DEPOIS de criar a instância 'db'
#    Isto permite que os modelos usem a instância 'db' correta.
from ..models.user import User
from ..models.ticket import Ticket, TicketObservacao
from ..models.log import Log
from ..models.produto import Produto

def init_database(app):
    """Inicializa o banco de dados com a aplicação Flask"""
    db.init_app(app)
    
    with app.app_context():
        # db.create_all() agora sabe sobre User, Ticket, e Log através das importações
        db.create_all()
        create_default_users()

def create_default_users():
    """Cria usuários padrão se não existirem, com senhas hasheadas."""
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            password='admin123',
            email='admin@maviclick.com',
            role='admin'
        )
        test_user = User(
            username='teste',
            password='teste123',
            email='teste@maviclick.com',
            role='user'
        )
        db.session.add(admin_user)
        db.session.add(test_user)
        db.session.commit()

def generate_ticket_id() -> str:
    """Gera um ID único de 8 caracteres para o ticket"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
