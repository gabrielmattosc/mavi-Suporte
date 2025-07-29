"""
Modelos de Ticket e TicketObservacao para o sistema Mavi Suporte
"""
from datetime import datetime
# Importa a instância 'db' central do seu serviço de base de dados
from ..services.database_service import db

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
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
