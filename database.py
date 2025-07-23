"""
Módulo de gerenciamento de dados LOCAIS para o sistema Mavi Suporte
"""
import streamlit as st
from datetime import datetime
import string
import random
from typing import Dict, List, Optional, Any

class LocalDataManager:
    """Gerenciador de dados em memória usando st.session_state."""
    
    def __init__(self):
        """Inicializa os dados de tickets e usuários na sessão do Streamlit."""
        if 'tickets_data' not in st.session_state:
            st.session_state.tickets_data = []
        
        if 'users_data' not in st.session_state:
            st.session_state.users_data = [
                {
                    "username": "admin",
                    "password": "admin123", # Em produção, usar hash
                    "email": "admin@maviclick.com",
                    "role": "admin",
                    "data_criacao": datetime.now()
                },
                {
                    "username": "teste",
                    "password": "teste123", # Em produção, usar hash
                    "email": "teste@maviclick.com",
                    "role": "user",
                    "data_criacao": datetime.now()
                }
            ]
        
        self.tickets = st.session_state.tickets_data
        self.users = st.session_state.users_data

class TicketManager:
    """Gerenciador de operações de tickets (local)."""
    
    def __init__(self, data_manager: LocalDataManager):
        """Inicializa com o gerenciador de dados locais."""
        self.data_manager = data_manager

    def _generate_ticket_id(self) -> str:
        """Gera um ID único de 8 caracteres para o ticket."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def criar_ticket(self, dados: Dict[str, Any]) -> Optional[str]:
        """Cria um novo ticket e o armazena localmente."""
        try:
            ticket_id = self._generate_ticket_id()
            
            ticket_data = {
                "ticket_id": ticket_id,
                "nome": dados.get("nome"),
                "email": dados.get("email"),
                "squad_leader": dados.get("squad_leader"),
                "dispositivos": dados.get("dispositivos"),
                "necessidade": dados.get("necessidade"),
                "prioridade": dados.get("prioridade", "Normal"),
                "status": "Pendente",
                "data_criacao": datetime.now(),
                "data_atualizacao": datetime.now(),
                "observacoes": []
            }
            
            self.data_manager.tickets.append(ticket_data)
            return ticket_id
            
        except Exception as e:
            st.error(f"Erro ao criar ticket localmente: {str(e)}")
            return None

    def obter_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Obtém um ticket pelo ID a partir da lista local."""
        try:
            for ticket in self.data_manager.tickets:
                if str(ticket.get("ticket_id")) == str(ticket_id):
                    return ticket
            return None
        except Exception as e:
            st.error(f"Erro ao buscar ticket local: {str(e)}")
            return None

    def listar_tickets(self, filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Lista tickets da memória com filtros opcionais."""
        try:
            tickets = self.data_manager.tickets.copy()
            
            if filtros:
                for key, value in filtros.items():
                    if value and value not in ["Todos", "Todas"]:
                        tickets = [t for t in tickets if t.get(key) == value]
            
            return sorted(tickets, key=lambda x: x.get("data_criacao", datetime.min), reverse=True)
            
        except Exception as e:
            st.error(f"Erro ao listar tickets locais: {str(e)}")
            return []

    # vvvvvvvvvvv FUNÇÃO CORRIGIDA vvvvvvvvvvv
    def atualizar_status(self, ticket_id: str, novo_status: str, observacao: str = None) -> bool:
        """
        Atualiza o status de um ticket e adiciona uma observação com o status atual.
        """
        try:
            for ticket in self.data_manager.tickets:
                if str(ticket.get("ticket_id")) == str(ticket_id):
                    ticket["status"] = novo_status
                    ticket["data_atualizacao"] = datetime.now()
                    
                    if observacao:
                        # A CORREÇÃO ESTÁ AQUI: Adicionamos a chave "status" ao dicionário
                        observacao_data = {
                            "data": datetime.now(),
                            "texto": observacao,
                            "status": novo_status  # <-- Chave adicionada!
                        }
                        if "observacoes" not in ticket:
                            ticket["observacoes"] = []
                        ticket["observacoes"].append(observacao_data)
                    return True
            return False
        except Exception as e:
            st.error(f"Erro ao atualizar ticket local: {str(e)}")
            return False
    # ^^^^^^^^^^^ FIM DA FUNÇÃO CORRIGIDA ^^^^^^^^^^^

    def obter_posicao_fila(self, ticket_id: str) -> int:
        """
        Obtém a posição do ticket na fila de pendentes, ordenando
        corretamente do mais antigo para o mais novo.
        """
        try:
            todos_os_tickets = self.data_manager.tickets.copy()
            tickets_pendentes = [t for t in todos_os_tickets if t.get("status") == "Pendente"]
            
            fila_correta = sorted(
                tickets_pendentes, 
                key=lambda x: x.get("data_criacao", datetime.min), 
                reverse=False
            )
            
            for i, ticket in enumerate(fila_correta):
                if str(ticket.get("ticket_id")) == str(ticket_id):
                    return i + 1
                    
            return 0
            
        except Exception as e:
            st.error(f"Erro ao obter posição na fila: {str(e)}")
            return 0

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas dos tickets armazenados localmente."""
        try:
            tickets = self.listar_tickets()
            stats = {
                "total_tickets": len(tickets),
                "pendentes": len([t for t in tickets if t.get("status") == "Pendente"]),
                "em_andamento": len([t for t in tickets if t.get("status") == "Em andamento"]),
                "concluidos": len([t for t in tickets if t.get("status") == "Concluída"]),
                "dispositivos_mais_solicitados": {}
            }
            
            dispositivos_contador = {}
            for ticket in tickets:
                dispositivos_str = ticket.get("dispositivos", "")
                if isinstance(dispositivos_str, str):
                    dispositivos_lista = [d.strip() for d in dispositivos_str.split(',') if d.strip()]
                    for dispositivo in dispositivos_lista:
                        dispositivos_contador[dispositivo] = dispositivos_contador.get(dispositivo, 0) + 1
            
            stats["dispositivos_mais_solicitados"] = dict(
                sorted(dispositivos_contador.items(), key=lambda item: item[1], reverse=True)
            )
            return stats
            
        except Exception as e:
            st.error(f"Erro ao obter estatísticas: {str(e)}")
            return {"total_tickets": 0, "pendentes": 0, "em_andamento": 0, "concluidos": 0, "dispositivos_mais_solicitados": {}}

class UserManager:
    """Gerenciador de operações de usuários (local)."""
    
    def __init__(self, data_manager: LocalDataManager):
        self.data_manager = data_manager

    def autenticar_usuario(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica um usuário com base nos dados locais."""
        try:
            for user in self.data_manager.users:
                if user["username"] == username and user["password"] == password:
                    return user
            return None
        except Exception as e:
            st.error(f"Erro na autenticação local: {str(e)}")
            return None

    def obter_usuario(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtém dados de um usuário pelo username."""
        try:
            for user in self.data_manager.users:
                if user["username"] == username:
                    return user
            return None
        except Exception as e:
            st.error(f"Erro ao buscar usuário local: {str(e)}")
            return None

@st.cache_resource
def get_database_managers():
    """Obtém instâncias dos gerenciadores de dados locais."""
    data_manager = LocalDataManager()
    ticket_manager = TicketManager(data_manager)
    user_manager = UserManager(data_manager)
    return data_manager, ticket_manager, user_manager