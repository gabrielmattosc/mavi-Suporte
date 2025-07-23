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
        # Inicializa a lista de tickets se não existir
        if 'tickets_data' not in st.session_state:
            st.session_state.tickets_data = []
        
        # Inicializa a lista de usuários padrão se não existir
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
        
        # Define as listas como atributos para fácil acesso
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
        """
        Cria um novo ticket e o armazena localmente.
        
        Args:
            dados: Dicionário com os dados do ticket.
        
        Returns:
            ID do ticket criado ou None em caso de erro.
        """
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
        """
        Obtém um ticket pelo ID a partir da lista local.
        """
        try:
            for ticket in self.data_manager.tickets:
                if ticket["ticket_id"] == ticket_id:
                    return ticket
            return None
        except Exception as e:
            st.error(f"Erro ao buscar ticket local: {str(e)}")
            return None

    def listar_tickets(self, filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Lista tickets da memória com filtros opcionais.
        """
        try:
            tickets = self.data_manager.tickets.copy()
            
            if filtros:
                for key, value in filtros.items():
                    if value and value not in ["Todos", "Todas"]:
                        tickets = [t for t in tickets if t.get(key) == value]
            
            # Ordena pela data de criação, do mais novo para o mais antigo
            return sorted(tickets, key=lambda x: x.get("data_criacao", datetime.min), reverse=True)
            
        except Exception as e:
            st.error(f"Erro ao listar tickets locais: {str(e)}")
            return []

    def atualizar_status(self, ticket_id: str, novo_status: str, observacao: str = None) -> bool:
        """
        Atualiza o status de um ticket na lista local.
        """
        try:
            for ticket in self.data_manager.tickets:
                if ticket["ticket_id"] == ticket_id:
                    ticket["status"] = novo_status
                    ticket["data_atualizacao"] = datetime.now()
                    
                    if observacao:
                        observacao_data = {
                            "data": datetime.now(),
                            "texto": observacao,
                            "status_anterior": ticket.get("status"), # Pode ser útil
                            "novo_status": novo_status
                        }
                        if "observacoes" not in ticket:
                            ticket["observacoes"] = []
                        ticket["observacoes"].append(observacao_data)
                    return True
            return False
        except Exception as e:
            st.error(f"Erro ao atualizar ticket local: {str(e)}")
            return False

    def obter_posicao_fila(self, ticket_id: str) -> int:
        """
        Obtém a posição do ticket na fila de pendentes.
        """
        try:
            tickets_pendentes = self.listar_tickets({"status": "Pendente"})
            
            for i, ticket in enumerate(tickets_pendentes):
                if ticket["ticket_id"] == ticket_id:
                    return i + 1
            return 0  # Ticket não encontrado na fila de pendentes
            
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
            
            # Conta dispositivos
            dispositivos_contador = {}
            for ticket in tickets:
                dispositivos = ticket.get("dispositivos", [])
                if isinstance(dispositivos, list): # Se for uma lista
                    for dispositivo in dispositivos:
                        dispositivo = dispositivo.strip()
                        if dispositivo:
                           dispositivos_contador[dispositivo] = dispositivos_contador.get(dispositivo, 0) + 1
            
            # Ordena dispositivos por quantidade
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
        """Inicializa com o gerenciador de dados locais."""
        self.data_manager = data_manager

    def autenticar_usuario(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica um usuário com base nos dados locais.
        """
        try:
            for user in self.data_manager.users:
                if user["username"] == username and user["password"] == password:
                    return user
            return None
        except Exception as e:
            st.error(f"Erro na autenticação local: {str(e)}")
            return None

    def obter_usuario(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtém dados de um usuário pelo username.
        """
        try:
            for user in self.data_manager.users:
                if user["username"] == username:
                    return user
            return None
        except Exception as e:
            st.error(f"Erro ao buscar usuário local: {str(e)}")
            return None

# Instâncias globais (usando cache do Streamlit)
@st.cache_resource
def get_database_managers():
    """
    Obtém instâncias dos gerenciadores de dados locais.
    
    Returns:
        Tupla com (data_manager, ticket_manager, user_manager)
    """
    data_manager = LocalDataManager()
    ticket_manager = TicketManager(data_manager)
    user_manager = UserManager(data_manager)
    
    # Retornando os 3 gerenciadores para corresponder à chamada em app.py
    return data_manager, ticket_manager, user_manager