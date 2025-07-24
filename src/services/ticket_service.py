"""
Serviço de gerenciamento de tickets para o sistema Mavi Suporte
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.services.database_service import db, Ticket, TicketObservacao, generate_ticket_id

class TicketService:
    """Serviço para operações de tickets"""
    
    @staticmethod
    def criar_ticket(dados: Dict[str, Any]) -> Optional[str]:
        """Cria um novo ticket"""
        try:
            ticket_id = generate_ticket_id()
            
            # Verifica se o ID já existe (improvável, mas seguro)
            while Ticket.query.filter_by(ticket_id=ticket_id).first():
                ticket_id = generate_ticket_id()
            
            ticket = Ticket(
                ticket_id=ticket_id,
                nome=dados.get("nome"),
                email=dados.get("email"),
                squad_leader=dados.get("squad_leader"),
                dispositivos=dados.get("dispositivos"),
                necessidade=dados.get("necessidade"),
                prioridade=dados.get("prioridade", "Normal"),
                status="Pendente"
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            return ticket_id
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar ticket: {str(e)}")
            return None
    
    @staticmethod
    def obter_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
        """Obtém um ticket pelo ID"""
        try:
            ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            return ticket.to_dict() if ticket else None
        except Exception as e:
            print(f"Erro ao buscar ticket: {str(e)}")
            return None
    
    @staticmethod
    def listar_tickets(filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Lista tickets com filtros opcionais"""
        try:
            query = Ticket.query
            
            if filtros:
                if filtros.get('status') and filtros['status'] not in ["Todos", "Todas"]:
                    query = query.filter(Ticket.status == filtros['status'])
                if filtros.get('prioridade') and filtros['prioridade'] not in ["Todos", "Todas"]:
                    query = query.filter(Ticket.prioridade == filtros['prioridade'])
            
            tickets = query.order_by(Ticket.data_criacao.desc()).all()
            return [ticket.to_dict() for ticket in tickets]
            
        except Exception as e:
            print(f"Erro ao listar tickets: {str(e)}")
            return []
    
    @staticmethod
    def atualizar_status(ticket_id: str, novo_status: str, observacao: str = None) -> bool:
        """Atualiza o status de um ticket"""
        try:
            ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            
            if not ticket:
                return False
            
            ticket.status = novo_status
            ticket.data_atualizacao = datetime.utcnow()
            
            if observacao:
                obs = TicketObservacao(
                    ticket_id=ticket.id,
                    texto=observacao,
                    status=novo_status
                )
                db.session.add(obs)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar ticket: {str(e)}")
            return False
    
    @staticmethod
    def obter_posicao_fila(ticket_id: str) -> int:
        """Obtém a posição do ticket na fila de pendentes"""
        try:
            ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            
            if not ticket or ticket.status != 'Pendente':
                return 0
            
            # Conta quantos tickets pendentes foram criados antes deste
            tickets_anteriores = Ticket.query.filter(
                Ticket.status == 'Pendente',
                Ticket.data_criacao < ticket.data_criacao
            ).count()
            
            return tickets_anteriores + 1
            
        except Exception as e:
            print(f"Erro ao obter posição na fila: {str(e)}")
            return 0
    
    @staticmethod
    def obter_estatisticas() -> Dict[str, Any]:
        """Obtém estatísticas dos tickets"""
        try:
            total_tickets = Ticket.query.count()
            pendentes = Ticket.query.filter_by(status='Pendente').count()
            em_andamento = Ticket.query.filter_by(status='Em andamento').count()
            concluidos = Ticket.query.filter_by(status='Concluída').count()
            
            # Dispositivos mais solicitados
            tickets = Ticket.query.all()
            dispositivos_contador = {}
            
            for ticket in tickets:
                if ticket.dispositivos:
                    dispositivos_lista = [d.strip() for d in ticket.dispositivos.split(',') if d.strip()]
                    for dispositivo in dispositivos_lista:
                        dispositivos_contador[dispositivo] = dispositivos_contador.get(dispositivo, 0) + 1
            
            dispositivos_mais_solicitados = dict(
                sorted(dispositivos_contador.items(), key=lambda item: item[1], reverse=True)
            )
            
            return {
                "total_tickets": total_tickets,
                "pendentes": pendentes,
                "em_andamento": em_andamento,
                "concluidos": concluidos,
                "dispositivos_mais_solicitados": dispositivos_mais_solicitados
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {str(e)}")
            return {
                "total_tickets": 0,
                "pendentes": 0,
                "em_andamento": 0,
                "concluidos": 0,
                "dispositivos_mais_solicitados": {}
            }

