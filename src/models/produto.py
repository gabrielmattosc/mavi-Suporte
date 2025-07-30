"""
Modelo de Produto para o sistema Mavi Suporte
"""
from datetime import datetime
from ..services.database_service import db

class Produto(db.Model):
    """Modelo de produto"""
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'quantidade': self.quantidade,
            'data_cadastro': self.data_cadastro
        }