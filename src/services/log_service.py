"""
Serviço de gerenciamento de logs para o sistema Mavi Suporte
"""
from datetime import datetime
from typing import List, Dict, Any
# Importa apenas a instância 'db' no topo do ficheiro
from src.services.database_service import db

class LogService:
    """Serviço para operações de logs"""

    @staticmethod
    def registrar_log(usuario: str, acao: str, detalhes: str = ""):
        """
        Cria e salva uma nova entrada de log no banco de dados.
        """
        # --- CORREÇÃO: Importa o modelo 'Log' dentro da função ---
        # Isto quebra o ciclo de importação e garante que o modelo já existe.
        from src.models.log import Log
        
        try:
            novo_log = Log(
                usuario=usuario,
                acao=acao,
                detalhes=detalhes,
                timestamp=datetime.utcnow()
            )
            db.session.add(novo_log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao registrar log: {str(e)}")

    @staticmethod
    def listar_logs() -> List[Dict[str, Any]]:
        """
        Lista todos os logs do banco de dados, ordenados do mais recente para o mais antigo.
        """
        # --- CORREÇÃO: Importa o modelo 'Log' dentro da função ---
        from src.models.log import Log

        try:
            # Busca todos os logs e ordena pela data/hora em ordem decrescente
            logs = Log.query.order_by(Log.timestamp.desc()).all()
            # Converte cada objeto Log para um dicionário antes de retornar
            return [log.to_dict() for log in logs]
        except Exception as e:
            print(f"Erro ao listar logs: {str(e)}")
            return []
