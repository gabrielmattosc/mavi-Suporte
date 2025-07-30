"""
Serviço de gerenciamento de produtos (inventário) para o sistema Mavi Suporte
"""
from src.services.database_service import db
from ..models.produto import Produto
from typing import Dict, Any, List

class ProductService:
    """Serviço para operações de produtos"""

    @staticmethod
    def cadastrar_ou_atualizar_produto(nome: str, quantidade: int, descricao: str = "") -> bool:
        """
        Cadastra um novo produto ou atualiza a quantidade de um existente.
        """
        try:
            produto_existente = Produto.query.filter_by(nome=nome).first()
            
            if produto_existente:
                # Se o produto já existe, apenas soma a quantidade
                produto_existente.quantidade += quantidade
                if descricao:
                    produto_existente.descricao = descricao
            else:
                # Se não existe, cria um novo
                novo_produto = Produto(
                    nome=nome,
                    descricao=descricao,
                    quantidade=quantidade
                )
                db.session.add(novo_produto)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao cadastrar/atualizar produto: {str(e)}")
            return False

    @staticmethod
    def decrementar_estoque(nome_produto: str, quantidade_a_remover: int = 1) -> bool:
        """
        Decrementa a quantidade de um produto no estoque.
        Retorna True se a operação for bem-sucedida, False caso contrário (ex: sem estoque).
        """
        try:
            produto = Produto.query.filter_by(nome=nome_produto).first()

            if not produto:
                print(f"Aviso: Tentativa de baixar estoque de produto não cadastrado: {nome_produto}")
                return False # Produto não existe no inventário

            if produto.quantidade < quantidade_a_remover:
                print(f"Aviso: Estoque insuficiente para {nome_produto}. Disponível: {produto.quantidade}, Solicitado: {quantidade_a_remover}")
                return False # Sem estoque suficiente

            produto.quantidade -= quantidade_a_remover
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao decrementar estoque de {nome_produto}: {str(e)}")
            return False

    @staticmethod
    def listar_produtos() -> List[Dict[str, Any]]:
        """Lista todos os produtos cadastrados."""
        try:
            produtos = Produto.query.order_by(Produto.nome.asc()).all()
            return [produto.to_dict() for produto in produtos]
        except Exception as e:
            print(f"Erro ao listar produtos: {str(e)}")
            return []
