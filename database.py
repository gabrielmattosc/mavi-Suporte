from datetime import datetime
import random, string

class LocalDataManager:
    def __init__(self):
        # Dados em memória
        self.tickets = []
        self.users = [
            {"username": "admin", "password": "admin123", "email": "admin@maviclick.com", "role": "admin", "data_criacao": datetime.now()},
            {"username": "teste", "password": "teste123", "email": "teste@maviclick.com", "role": "user", "data_criacao": datetime.now()}
        ]

data_manager = LocalDataManager()

class TicketManager:
    def __init__(self):
        self.data_manager = data_manager

    def _generate_ticket_id(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def criar_ticket(self, dados):
        ticket_id = self._generate_ticket_id()
        ticket = {
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
        self.data_manager.tickets.append(ticket)
        return ticket_id

    def obter_ticket(self, ticket_id):
        for t in self.data_manager.tickets:
            if t['ticket_id'] == ticket_id:
                return t
        return None

    def listar_tickets(self, filtros=None):
        items = list(self.data_manager.tickets)
        if filtros:
            for k, v in filtros.items():
                items = [t for t in items if t.get(k) == v]
        return sorted(items, key=lambda x: x['data_criacao'], reverse=True)

    def atualizar_status(self, ticket_id, novo_status, observacao=None):
        t = self.obter_ticket(ticket_id)
        if not t: return False
        t['status'] = novo_status
        t['data_atualizacao'] = datetime.now()
        if observacao:
            obs = {"data": datetime.now(), "texto": observacao, "status": novo_status}
            t['observacoes'].append(obs)
        return True

    def obter_posicao_fila(self, ticket_id):
        pendentes = [t for t in self.data_manager.tickets if t['status']=="Pendente"]
        fila = sorted(pendentes, key=lambda x: x['data_criacao'])
        for i, t in enumerate(fila,1):
            if t['ticket_id']==ticket_id:
                return i
        return 0

    def obter_estatisticas(self):
        total = len(self.data_manager.tickets)
        pend = len([t for t in self.data_manager.tickets if t['status']=='Pendente'])
        andam = len([t for t in self.data_manager.tickets if t['status']=='Em andamento'])
        concl = len([t for t in self.data_manager.tickets if t['status']=='Concluída'])
        disp = {}
        for t in self.data_manager.tickets:
            for d in t['dispositivos'].split(','):
                d = d.strip()
                disp[d] = disp.get(d,0) + 1
        return {"total_tickets": total, "pendentes": pend, "em_andamento": andam, "concluidos": concl, "dispositivos_mais_solicitados": disp}

class UserManager:
    def __init__(self):
        self.data_manager = data_manager

    def autenticar(self, username, password):
        for u in self.data_manager.users:
            if u['username']==username and u['password']==password:
                return u
        return None

# Instâncias únicas
ticket_manager = TicketManager()
user_manager = UserManager()