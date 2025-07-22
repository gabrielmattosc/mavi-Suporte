"""
Módulo de gerenciamento de banco de dados MongoDB para o sistema Mavi Suporte
"""
import pymongo
from pymongo import MongoClient
from datetime import datetime
import string
import random
from typing import Dict, List, Optional, Any
import streamlit as st

class MongoDBManager:
    """Gerenciador de conexão e operações com MongoDB"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", database_name: str = "mavi_suporte"):
        """
        Inicializa a conexão com MongoDB
        
        Args:
            connection_string: String de conexão MongoDB
            database_name: Nome do banco de dados
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            
            # Testa a conexão
            self.client.admin.command('ping')
            
            # Coleções
            self.tickets_collection = self.db.tickets
            self.users_collection = self.db.users
            
            # Cria índices para otimização
            self._create_indexes()
            
            # Inicializa usuários padrão
            self._init_default_users()
            
        except Exception as e:
            st.error(f"Erro ao conectar com MongoDB: {str(e)}")
            # Fallback para dados em memória se MongoDB não estiver disponível
            self._use_memory_fallback()
    
    def _create_indexes(self):
        """Cria índices para otimização de consultas"""
        try:
            # Índices para tickets
            self.tickets_collection.create_index("ticket_id", unique=True)
            self.tickets_collection.create_index("email")
            self.tickets_collection.create_index("status")
            self.tickets_collection.create_index("data_criacao")
            
            # Índices para usuários
            self.users_collection.create_index("username", unique=True)
            self.users_collection.create_index("email", unique=True)
            
        except Exception as e:
            print(f"Aviso: Erro ao criar índices: {str(e)}")
    
    def _init_default_users(self):
        """Inicializa usuários padrão do sistema"""
        default_users = [
            {
                "username": "admin",
                "password": "admin123",  # Em produção, usar hash
                "email": "admin@maviclick.com",
                "role": "admin",
                "data_criacao": datetime.now()
            },
            {
                "username": "teste",
                "password": "teste123",  # Em produção, usar hash
                "email": "teste@maviclick.com",
                "role": "user",
                "data_criacao": datetime.now()
            }
        ]
        
        for user in default_users:
            try:
                # Verifica se o usuário já existe
                existing_user = self.users_collection.find_one({"username": user["username"]})
                if not existing_user:
                    self.users_collection.insert_one(user)
            except Exception as e:
                print(f"Aviso: Erro ao criar usuário {user['username']}: {str(e)}")
    
    def _use_memory_fallback(self):
        """Usa armazenamento em memória como fallback"""
        if 'tickets_data' not in st.session_state:
            st.session_state.tickets_data = []
        if 'users_data' not in st.session_state:
            st.session_state.users_data = [
                {
                    "username": "admin",
                    "password": "admin123",
                    "email": "admin@maviclick.com",
                    "role": "admin",
                    "data_criacao": datetime.now()
                },
                {
                    "username": "teste",
                    "password": "teste123",
                    "email": "teste@maviclick.com",
                    "role": "user",
                    "data_criacao": datetime.now()
                }
            ]
        self.use_memory = True
    
    def _generate_ticket_id(self) -> str:
        """Gera um ID único para o ticket"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class TicketManager:
    """Gerenciador de tickets"""
    
    def __init__(self, db_manager: MongoDBManager):
        self.db_manager = db_manager
    
    def criar_ticket(self, dados: Dict[str, Any]) -> str:
        """
        Cria um novo ticket
        
        Args:
            dados: Dicionário com os dados do ticket
            
        Returns:
            ID do ticket criado
        """
        # Gera ID único
        ticket_id = self.db_manager._generate_ticket_id()
        
        # Prepara dados do ticket
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
        
        try:
            if hasattr(self.db_manager, 'use_memory'):
                # Usa armazenamento em memória
                st.session_state.tickets_data.append(ticket_data)
            else:
                # Usa MongoDB
                self.db_manager.tickets_collection.insert_one(ticket_data)
            
            return ticket_id
            
        except Exception as e:
            st.error(f"Erro ao criar ticket: {str(e)}")
            return None
    
    def obter_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém um ticket pelo ID
        
        Args:
            ticket_id: ID do ticket
            
        Returns:
            Dados do ticket ou None se não encontrado
        """
        try:
            if hasattr(self.db_manager, 'use_memory'):
                # Busca em memória
                for ticket in st.session_state.tickets_data:
                    if ticket["ticket_id"] == ticket_id:
                        return ticket
                return None
            else:
                # Busca no MongoDB
                return self.db_manager.tickets_collection.find_one({"ticket_id": ticket_id})
                
        except Exception as e:
            st.error(f"Erro ao buscar ticket: {str(e)}")
            return None
    
    def listar_tickets(self, filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Lista tickets com filtros opcionais
        
        Args:
            filtros: Dicionário com filtros (status, prioridade, etc.)
            
        Returns:
            Lista de tickets
        """
        try:
            if hasattr(self.db_manager, 'use_memory'):
                # Filtra dados em memória
                tickets = st.session_state.tickets_data.copy()
                
                if filtros:
                    for key, value in filtros.items():
                        if value and value != "Todos" and value != "Todas":
                            tickets = [t for t in tickets if t.get(key) == value]
                
                return sorted(tickets, key=lambda x: x.get("data_criacao", datetime.now()), reverse=True)
            else:
                # Busca no MongoDB
                query = {}
                if filtros:
                    for key, value in filtros.items():
                        if value and value != "Todos" and value != "Todas":
                            query[key] = value
                
                return list(self.db_manager.tickets_collection.find(query).sort("data_criacao", -1))
                
        except Exception as e:
            st.error(f"Erro ao listar tickets: {str(e)}")
            return []
    
    def atualizar_status(self, ticket_id: str, novo_status: str, observacao: str = None) -> bool:
        """
        Atualiza o status de um ticket
        
        Args:
            ticket_id: ID do ticket
            novo_status: Novo status
            observacao: Observação opcional
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            update_data = {
                "status": novo_status,
                "data_atualizacao": datetime.now()
            }
            
            if observacao:
                observacao_data = {
                    "data": datetime.now(),
                    "texto": observacao,
                    "status": novo_status
                }
            
            if hasattr(self.db_manager, 'use_memory'):
                # Atualiza em memória
                for ticket in st.session_state.tickets_data:
                    if ticket["ticket_id"] == ticket_id:
                        ticket.update(update_data)
                        if observacao:
                            if "observacoes" not in ticket:
                                ticket["observacoes"] = []
                            ticket["observacoes"].append(observacao_data)
                        return True
                return False
            else:
                # Atualiza no MongoDB
                update_query = {"$set": update_data}
                
                if observacao:
                    update_query["$push"] = {"observacoes": observacao_data}
                
                result = self.db_manager.tickets_collection.update_one(
                    {"ticket_id": ticket_id},
                    update_query
                )
                return result.modified_count > 0
                
        except Exception as e:
            st.error(f"Erro ao atualizar ticket: {str(e)}")
            return False
    
    def obter_posicao_fila(self, ticket_id: str) -> int:
        """
        Obtém a posição do ticket na fila
        
        Args:
            ticket_id: ID do ticket
            
        Returns:
            Posição na fila (1-based)
        """
        try:
            # Lista tickets pendentes ordenados por data de criação
            tickets_pendentes = self.listar_tickets({"status": "Pendente"})
            
            for i, ticket in enumerate(tickets_pendentes):
                if ticket["ticket_id"] == ticket_id:
                    return i + 1
            
            return 0  # Ticket não encontrado ou não está pendente
            
        except Exception as e:
            st.error(f"Erro ao obter posição na fila: {str(e)}")
            return 0
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas dos tickets
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            tickets = self.listar_tickets()
            
            stats = {
                "total_tickets": len(tickets),
                "pendentes": len([t for t in tickets if t.get("status") == "Pendente"]),
                "em_andamento": len([t for t in tickets if t.get("status") == "Em andamento"]),
                "concluidos": len([t for t in tickets if t.get("status") == "Concluída"]),
                "dispositivos_mais_solicitados": {}
            }
            
            # Conta dispositivos mais solicitados
            for ticket in tickets:
                dispositivos = ticket.get("dispositivos", "")
                if dispositivos:
                    for dispositivo in dispositivos.split(", "):
                        dispositivo = dispositivo.strip()
                        if dispositivo:
                            stats["dispositivos_mais_solicitados"][dispositivo] = \
                                stats["dispositivos_mais_solicitados"].get(dispositivo, 0) + 1
            
            # Ordena dispositivos por quantidade
            stats["dispositivos_mais_solicitados"] = dict(
                sorted(stats["dispositivos_mais_solicitados"].items(), 
                      key=lambda x: x[1], reverse=True)
            )
            
            return stats
            
        except Exception as e:
            st.error(f"Erro ao obter estatísticas: {str(e)}")
            return {
                "total_tickets": 0,
                "pendentes": 0,
                "em_andamento": 0,
                "concluidos": 0,
                "dispositivos_mais_solicitados": {}
            }

class UserManager:
    """Gerenciador de usuários"""
    
    def __init__(self, db_manager: MongoDBManager):
        self.db_manager = db_manager
    
    def autenticar_usuario(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica um usuário
        
        Args:
            username: Nome de usuário
            password: Senha
            
        Returns:
            Dados do usuário se autenticado, None caso contrário
        """
        try:
            if hasattr(self.db_manager, 'use_memory'):
                # Busca em memória
                for user in st.session_state.users_data:
                    if user["username"] == username and user["password"] == password:
                        return user
                return None
            else:
                # Busca no MongoDB
                return self.db_manager.users_collection.find_one({
                    "username": username,
                    "password": password  # Em produção, usar hash
                })
                
        except Exception as e:
            st.error(f"Erro na autenticação: {str(e)}")
            return None
    
    def obter_usuario(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtém dados de um usuário
        
        Args:
            username: Nome de usuário
            
        Returns:
            Dados do usuário ou None se não encontrado
        """
        try:
            if hasattr(self.db_manager, 'use_memory'):
                # Busca em memória
                for user in st.session_state.users_data:
                    if user["username"] == username:
                        return user
                return None
            else:
                # Busca no MongoDB
                return self.db_manager.users_collection.find_one({"username": username})
                
        except Exception as e:
            st.error(f"Erro ao buscar usuário: {str(e)}")
            return None

# Instâncias globais (usando cache do Streamlit)
@st.cache_resource
def get_database_managers():
    """
    Obtém instâncias dos gerenciadores de banco de dados
    
    Returns:
        Tupla com (db_manager, ticket_manager, user_manager)
    """
    db_manager = MongoDBManager()
    ticket_manager = TicketManager(db_manager)
    user_manager = UserManager(db_manager)
    
    return db_manager, ticket_manager, user_manager

