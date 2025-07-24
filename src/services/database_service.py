"""
Serviço de gerenciamento de banco de dados para o sistema Mavi Suporte
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random
from typing import Dict, List, Optional, Any

db = SQLAlchemy()

def init_database(app):
    """Inicializa o banco de dados com a aplicação Flask"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        # Cria usuários padrão se não existirem
        create_default_users()

class User(db.Model):
    """Modelo de usuário"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'data_criacao': self.data_criacao
        }

class Ticket(db.Model):
    """Modelo de ticket"""
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(8), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    squad_leader = db.Column(db.String(100), nullable=False)
    dispositivos = db.Column(db.Text, nullable=False)
    necessidade = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(20), nullable=False, default='Normal')
    status = db.Column(db.String(20), nullable=False, default='Pendente')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com observações
    observacoes = db.relationship('TicketObservacao', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'nome': self.nome,
            'email': self.email,
            'squad_leader': self.squad_leader,
            'dispositivos': self.dispositivos,
            'necessidade': self.necessidade,
            'prioridade': self.prioridade,
            'status': self.status,
            'data_criacao': self.data_criacao,
            'data_atualizacao': self.data_atualizacao,
            'observacoes': [obs.to_dict() for obs in self.observacoes]
        }

class TicketObservacao(db.Model):
    """Modelo de observações do ticket"""
    __tablename__ = 'ticket_observacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'texto': self.texto,
            'status': self.status,
            'data': self.data
        }

def create_default_users():
    """Cria usuários padrão se não existirem"""
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            password='admin123',  # Em produção, usar hash
            email='admin@maviclick.com',
            role='admin'
        )
        
        test_user = User(
            username='teste',
            password='teste123',  # Em produção, usar hash
            email='teste@maviclick.com',
            role='user'
        )
        
        db.session.add(admin_user)
        db.session.add(test_user)
        db.session.commit()

def generate_ticket_id() -> str:
    """Gera um ID único de 8 caracteres para o ticket"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

