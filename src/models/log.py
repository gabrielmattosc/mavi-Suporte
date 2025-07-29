"""
Modelo de Log para o sistema Mavi Suporte
"""
from datetime import datetime
# Importa a instância 'db' central do seu serviço de base de dados
from ..services.database_service import db

class Log(db.Model):
    """Modelo para registrar logs de atividade."""
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(150), nullable=False)
    acao = db.Column(db.String(150), nullable=False)
    detalhes = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        """Converte o objeto Log para um dicionário."""
        return {
            'id': self.id,
            'usuario': self.usuario,
            'acao': self.acao,
            'detalhes': self.detalhes,
            'timestamp': self.timestamp
        }
