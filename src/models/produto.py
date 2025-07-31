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

    # Novo relacionamento para o histórico de descrições
    historico_descricao = db.relationship('ProdutoDescricaoHistorico', backref='produto', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'quantidade': self.quantidade,
            'data_cadastro': self.data_cadastro,
            'historico_descricao': [h.to_dict() for h in self.historico_descricao]
        }

class ProdutoDescricaoHistorico(db.Model):
    """Modelo para guardar o histórico de descrições de um produto."""
    __tablename__ = 'produto_descricao_historico'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    
    # Guarda a quantidade que foi adicionada nesta transação específica.
    quantidade_adicionada = db.Column(db.Integer, nullable=False, default=0)
    descricao_antiga = db.Column(db.Text, nullable=True) # Permite nulo para o primeiro cadastro
    modificado_por = db.Column(db.String(150), nullable=False)
    data_modificacao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'quantidade_adicionada': self.quantidade_adicionada,
            'descricao_antiga': self.descricao_antiga,
            'modificado_por': self.modificado_por,
            'data_modificacao': self.data_modificacao
        }