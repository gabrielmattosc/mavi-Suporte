"""
Módulo para envio de notificações (email e SMS)
"""
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailNotifier:
    """Classe para envio de notificações por email"""
    
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def enviar_confirmacao_ticket(self, destinatario: str, ticket_id: str, posicao_fila: int) -> bool:
        """Envia email de confirmação de criação do ticket"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Ticket #{ticket_id} - Solicitação de Suporte Mavi'
            msg['From'] = self.sender_email
            msg['To'] = destinatario
            
            # Texto simples
            texto_simples = f"""
Olá!

Sua solicitação de suporte foi registrada com sucesso!

Detalhes do seu ticket:
- Número do ticket: #{ticket_id}
- Posição na fila: {posicao_fila}
- Status: Pendente

Você receberá atualizações sobre o andamento do seu ticket por email.

Atenciosamente,
Equipe de Suporte Mavi
            """
            
            # HTML
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">Mavi Suporte</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Confirmação de Ticket</p>
                  </div>
                  
                  <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #667eea; margin-top: 0;">Ticket Criado com Sucesso!</h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                      <h3 style="margin-top: 0; color: #333;">Detalhes do Ticket</h3>
                      <p><strong>Número:</strong> #{ticket_id}</p>
                      <p><strong>Posição na fila:</strong> {posicao_fila}</p>
                      <p><strong>Status:</strong> <span style="color: #ffc107; font-weight: bold;">Pendente</span></p>
                    </div>
                    
                    <p>Você receberá atualizações sobre o andamento do seu ticket por email.</p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                      <p style="margin: 0; color: #6c757d; font-size: 14px;">
                        Atenciosamente,<br>
                        <strong>Equipe de Suporte Mavi</strong>
                      </p>
                    </div>
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Anexa as versões de texto
            part1 = MIMEText(texto_simples, 'plain', 'utf-8')
            part2 = MIMEText(html, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Envia o email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email de confirmação enviado para {destinatario}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    def enviar_atualizacao_status(self, destinatario: str, ticket_id: str, novo_status: str, observacoes: str = "") -> bool:
        """Envia email de atualização de status do ticket"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Ticket #{ticket_id} - Atualização de Status'
            msg['From'] = self.sender_email
            msg['To'] = destinatario
            
            # Texto simples
            texto_simples = f"""
Olá!

Há uma atualização no seu ticket de suporte:

- Número do ticket: #{ticket_id}
- Novo status: {novo_status}
"""
            
            if observacoes:
                texto_simples += f"- Observações: {observacoes}\n"
            
            texto_simples += """
Atenciosamente,
Equipe de Suporte Mavi
            """
            
            # HTML
            status_color = {
                'Pendente': '#ffc107',
                'Em andamento': '#17a2b8', 
                'Concluída': '#28a745'
            }.get(novo_status, '#6c757d')
            
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">Mavi Suporte</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Atualização de Ticket</p>
                  </div>
                  
                  <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #667eea; margin-top: 0;">Ticket Atualizado</h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                      <h3 style="margin-top: 0; color: #333;">Detalhes da Atualização</h3>
                      <p><strong>Número:</strong> #{ticket_id}</p>
                      <p><strong>Novo Status:</strong> <span style="color: {status_color}; font-weight: bold;">{novo_status}</span></p>
            """
            
            if observacoes:
                html += f"<p><strong>Observações:</strong> {observacoes}</p>"
            
            html += """
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                      <p style="margin: 0; color: #6c757d; font-size: 14px;">
                        Atenciosamente,<br>
                        <strong>Equipe de Suporte Mavi</strong>
                      </p>
                    </div>
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Anexa as versões de texto
            part1 = MIMEText(texto_simples, 'plain', 'utf-8')
            part2 = MIMEText(html, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Envia o email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email de atualização enviado para {destinatario}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de atualização: {str(e)}")
            return False

class SMSNotifier:
    """Classe para envio de notificações por SMS (usando Twilio)"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.client = None
        
        # Tenta importar e inicializar o cliente Twilio
        try:
            from twilio.rest import Client
            if account_sid and auth_token:
                self.client = Client(account_sid, auth_token)
        except ImportError:
            logger.warning("Twilio não está instalado. SMS não estará disponível.")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Twilio: {str(e)}")
    
    def enviar_sms_ticket(self, telefone: str, ticket_id: str, posicao_fila: int) -> bool:
        """Envia SMS de confirmação de criação do ticket"""
        if not self.client:
            logger.warning("Cliente SMS não disponível")
            return False
        
        try:
            mensagem = f"Mavi Suporte: Ticket #{ticket_id} criado. Posição na fila: {posicao_fila}. Você receberá atualizações por email."
            
            message = self.client.messages.create(
                body=mensagem,
                from_=self.from_number,
                to=telefone
            )
            
            logger.info(f"SMS enviado para {telefone}: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {str(e)}")
            return False

