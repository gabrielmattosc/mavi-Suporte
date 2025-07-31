"""
Serviço de gerenciamento de produtos (inventário) para o sistema Mavi Suporte
"""
from src.services.database_service import db
from ..models.produto import Produto, ProdutoDescricaoHistorico
from typing import Dict, Any, List
from datetime import datetime

class ProductService:
    """Serviço para operações de produtos"""

    @staticmethod
    def cadastrar_ou_atualizar_produto(nome: str, quantidade: int, descricao: str, modificado_por: str) -> bool:
        """
        Cadastra um novo produto ou atualiza um existente, salvando o histórico.
        """
        try:
            produto_existente = Produto.query.filter_by(nome=nome).first()
            
            if produto_existente:
                # Cria um registo de histórico para esta adição de stock
                historico = ProdutoDescricaoHistorico(
                    produto_id=produto_existente.id,
                    descricao_antiga=produto_existente.descricao,
                    quantidade_adicionada=quantidade,
                    modificado_por=modificado_por
                )
                db.session.add(historico)
                
                produto_existente.quantidade += quantidade
                produto_existente.descricao = descricao
            else:
                novo_produto = Produto(nome=nome, descricao=descricao, quantidade=quantidade)
                db.session.add(novo_produto)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao cadastrar/atualizar produto: {str(e)}")
            return False

    # --- NOVO MÉTODO PARA EDITAR A DESCRIÇÃO ATUAL ---
    @staticmethod
    def editar_descricao_atual(produto_id: int, nova_descricao: str, modificado_por: str) -> bool:
        """
        Edita a descrição atual de um produto, salvando a versão antiga no histórico.
        """
        try:
            produto = Produto.query.get(produto_id)
            if not produto or produto.descricao == nova_descricao:
                return False

            historico = ProdutoDescricaoHistorico(
                produto_id=produto.id,
                descricao_antiga=produto.descricao or " ",
                quantidade_adicionada=0, # Edição de texto não altera quantidade
                modificado_por=modificado_por
            )
            db.session.add(historico)

            produto.descricao = nova_descricao
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao editar descrição atual: {str(e)}")
            return False

    # --- NOVO MÉTODO PARA EDITAR UMA DESCRIÇÃO DO HISTÓRICO ---
    @staticmethod
    def editar_descricao_historico(history_id: int, nova_descricao: str) -> bool:
        """
        Edita o texto de uma entrada específica do histórico de descrições.
        """
        try:
            historico = ProdutoDescricaoHistorico.query.get(history_id)
            if not historico:
                return False
            
            historico.descricao_antiga = nova_descricao
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao editar descrição do histórico: {str(e)}")
            return False
        
    # --- NOVO MÉTODO PARA ATUALIZAR APENAS A QUANTIDADE ---
    @staticmethod
    def atualizar_quantidade_produto(produto_id: int, nova_quantidade: int, modificado_por: str) -> bool:
        """
        Atualiza a quantidade de um produto específico e registra a alteração no histórico.
        """
        try:
            produto = Produto.query.get(produto_id)
            if not produto:
                return False

            quantidade_antiga = produto.quantidade
            diferenca = nova_quantidade - quantidade_antiga
            
            # Só cria um histórico se a quantidade realmente mudou
            if diferenca != 0:
                historico = ProdutoDescricaoHistorico(
                    produto_id=produto.id,
                    descricao_antiga=f"Alteração de estoque manual de {quantidade_antiga} para {nova_quantidade}",
                    quantidade_adicionada=diferenca,
                    modificado_por=modificado_por
                )
                db.session.add(historico)

            produto.quantidade = nova_quantidade
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar quantidade do produto: {str(e)}")
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
                # Mesmo sem estoque, não retornamos False para não impedir a criação do ticket,
                # mas a falha será notificada ao admin.
                return False 

            produto.quantidade -= quantidade_a_remover
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao decrementar estoque de {nome_produto}: {str(e)}")
            return False

    @staticmethod
    def reverter_descricao_atual(produto_id: int, modificado_por: str) -> bool:
        """
        Reverte a descrição atual de um produto para a última entrada do histórico
        e também subtrai a quantidade de estoque que foi adicionada nessa entrada.
        """
        try:
            produto = Produto.query.get(produto_id)
            if not produto:
                return False

            # Encontra a entrada mais recente no histórico
            ultimo_historico = ProdutoDescricaoHistorico.query.filter_by(produto_id=produto.id)\
                .order_by(ProdutoDescricaoHistorico.data_modificacao.desc()).first()

            if not ultimo_historico:
                # Se não há histórico, não há para onde reverter.
                return False

            # --- NOVA LÓGICA DE REVERSÃO DE ESTOQUE ---
            # Subtrai a quantidade que foi adicionada naquela transação específica
            produto.quantidade -= ultimo_historico.quantidade_adicionada
            # Garante que a quantidade não fique negativa
            if produto.quantidade < 0:
                produto.quantidade = 0

            # Define a descrição atual do produto como a descrição antiga do último histórico
            produto.descricao = ultimo_historico.descricao_antiga
            
            # Remove a entrada do histórico que acabámos de usar para a reversão
            db.session.delete(ultimo_historico)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Erro ao reverter descrição e estoque: {str(e)}")
            return False
    
    @staticmethod
    def deletar_entrada_historico(history_id: int) -> bool:
        """
        Apaga uma entrada do histórico e reverte a adição de quantidade ao produto.
        """
        try:
            historico = ProdutoDescricaoHistorico.query.get(history_id)
            if not historico:
                return False

            produto = historico.produto
            if produto:
                # Subtrai a quantidade que foi adicionada naquela transação
                produto.quantidade -= historico.quantidade_adicionada
                if produto.quantidade < 0:
                    produto.quantidade = 0
            
            db.session.delete(historico)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar entrada do histórico: {str(e)}")
            return False

    @staticmethod
    def obter_produto_com_historico(produto_id: int) -> Dict[str, Any]:
        """Obtém um produto e seu histórico de descrições."""
        produto = Produto.query.get(produto_id)
        return produto.to_dict() if produto else None

    @staticmethod
    def listar_produtos() -> List[Dict[str, Any]]:
        """Lista todos os produtos cadastrados."""
        produtos = Produto.query.order_by(Produto.nome.asc()).all()
        return [produto.to_dict() for produto in produtos]