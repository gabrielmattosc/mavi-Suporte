"""
Configurações do sistema de suporte Mavi
"""
import os
from dataclasses import dataclass
from typing import List

@dataclass
class EmailConfig:
    """Configurações de email"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = os.getenv("MAVI_EMAIL", "seuemail@gmail.com")
    sender_password: str = os.getenv("MAVI_EMAIL_PASSWORD", "suasenha")
    
@dataclass
class SMSConfig:
    """Configurações de SMS (Twilio)"""
    account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    from_number: str = os.getenv("TWILIO_FROM_NUMBER", "")

@dataclass
class AppConfig:
    """Configurações gerais da aplicação"""
    data_dir: str = "data"
    fila_file: str = "data/fila.csv"
    relatorios_dir: str = "data/relatorios"
    max_fila_size: int = 100
    dispositivos_opcoes: List[str] = None
    
    def __post_init__(self):
        if self.dispositivos_opcoes is None:
            self.dispositivos_opcoes = [
                "Fones de ouvido",
                "Teclado", 
                "Mouse",
                "Notebook",
                "Bateria do notebook",
                "Monitor",
                "Upgrade de hardware",
                "Instalação de software",
                "Manutenção preventiva",
                "Suporte técnico remoto",
                "Configuração de rede"
            ]

# Instâncias globais das configurações
email_config = EmailConfig()
sms_config = SMSConfig()
app_config = AppConfig()

