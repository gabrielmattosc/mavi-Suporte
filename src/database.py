"""
Módulo para gerenciamento de dados da fila de suporte
"""
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class FilaManager:
    """Gerenciador da fila de suporte"""
    
    def __init__(self, fila_file: str):
        self.fila_file = fila_file
        self.ensure_data_dir()
        self.init_fila_file()
    
    def ensure_data_dir(self):
        """Garante que o diretório de dados existe"""
        data_dir = os.path.dirname(self.fila_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def init_fila_file(self):
        """Inicializa o arquivo da fila se não existir"""
        if not os.path.exists(self.fila_file):
            df = pd.DataFrame(columns=[
                'id', 'data_criacao', 'data_solicitacao', 'nome', 'email', 
                'telefone', 'squad_leader', 'dispositivos', 'necessidade', 
                'status', 'prioridade', 'data_conclusao', 'observacoes'
            ])
            df.to_csv(self.fila_file, index=False)
    
    def adicionar_solicitacao(self, dados: Dict) -> str:
        """Adiciona uma nova solicitação à fila"""
        df = pd.read_csv(self.fila_file)
        
        # Gera ID único
        ticket_id = str(uuid.uuid4())[:8].upper()
        
        # Prepara dados da nova solicitação
        nova_linha = {
            'id': ticket_id,
            'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_solicitacao': dados.get('data_solicitacao', datetime.now().strftime("%Y-%m-%d")),
            'nome': dados.get('nome', ''),
            'email': dados.get('email', ''),
            'telefone': dados.get('telefone', ''),
            'squad_leader': dados.get('squad_leader', ''),
            'dispositivos': dados.get('dispositivos', ''),
            'necessidade': dados.get('necessidade', ''),
            'status': 'Pendente',
            'prioridade': dados.get('prioridade', 'Normal'),
            'data_conclusao': '',
            'observacoes': ''
        }
        
        # Adiciona à fila
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        df.to_csv(self.fila_file, index=False)
        
        return ticket_id
    
    def obter_posicao_fila(self, ticket_id: str) -> int:
        """Obtém a posição na fila de um ticket específico"""
        df = pd.read_csv(self.fila_file)
        df_pendentes = df[df['status'] == 'Pendente'].reset_index(drop=True)
        
        try:
            posicao = df_pendentes[df_pendentes['id'] == ticket_id].index[0] + 1
            return posicao
        except IndexError:
            return -1
    
    def obter_estatisticas(self) -> Dict:
        """Obtém estatísticas da fila"""
        df = pd.read_csv(self.fila_file)
        
        total_solicitacoes = len(df)
        pendentes = len(df[df['status'] == 'Pendente'])
        em_andamento = len(df[df['status'] == 'Em andamento'])
        concluidas = len(df[df['status'] == 'Concluída'])
        
        # Estatísticas por dispositivo
        dispositivos_stats = {}
        for _, row in df.iterrows():
            dispositivos = str(row['dispositivos']).split(', ')
            for dispositivo in dispositivos:
                if dispositivo and dispositivo != 'nan':
                    dispositivos_stats[dispositivo] = dispositivos_stats.get(dispositivo, 0) + 1
        
        return {
            'total_solicitacoes': total_solicitacoes,
            'pendentes': pendentes,
            'em_andamento': em_andamento,
            'concluidas': concluidas,
            'dispositivos_mais_solicitados': dispositivos_stats
        }
    
    def obter_dados_completos(self) -> pd.DataFrame:
        """Retorna todos os dados da fila"""
        return pd.read_csv(self.fila_file)
    
    def atualizar_status(self, ticket_id: str, novo_status: str, observacoes: str = ""):
        """Atualiza o status de um ticket"""
        df = pd.read_csv(self.fila_file)
        mask = df['id'] == ticket_id
        
        if mask.any():
            df.loc[mask, 'status'] = novo_status
            if observacoes:
                df.loc[mask, 'observacoes'] = observacoes
            if novo_status == 'Concluída':
                df.loc[mask, 'data_conclusao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            df.to_csv(self.fila_file, index=False)
            return True
        return False

