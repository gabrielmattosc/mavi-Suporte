"""
Serviço de email para o sistema Mavi Suporte
Adaptado do código original do Streamlit
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any

class EmailService:
    """Serviço para envio de emails"""
    
    def __init__(self):
        """Inicializa o serviço de email a partir de variáveis de ambiente."""
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        
        # Lê o e-mail do remetente e do admin do ficheiro .env
        # Se não encontrar, usa o seu e-mail como padrão.
        self.email_usuario = os.getenv("EMAIL_USER", "")
        self.admin_email = os.getenv("ADMIN_EMAIL", "")
        self.email_senha = os.getenv("EMAIL_PASSWORD", "")
        
        self.enabled = bool(self.email_senha and self.email_usuario)

    def enviar_confirmacao_ticket(self, email_destino: str, ticket_id: str, 
                                  posicao_fila: int, dados_ticket: Dict[str, Any]) -> bool:
        """Envia email de confirmação para o usuário"""
        if not self.enabled:
            return False
        
        try:
            assunto = f"✅ Ticket #{ticket_id} - Solicitação Recebida - Mavi Suporte"
            
            corpo_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(90deg, #00D4AA, #00B894); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .ticket-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #00D4AA; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                    .status-badge {{ background: #ffc107; color: #000; padding: 5px 10px; border-radius: 15px; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎫 Mavi Suporte</h1>
                        <h2>Solicitação Recebida com Sucesso!</h2>
                    </div>
                    
                    <div class="content">
                        <p>Olá <strong>{dados_ticket['nome']}</strong>,</p>
                        
                        <p>Sua solicitação de suporte foi recebida e está sendo processada pela nossa equipe.</p>
                        
                        <div class="ticket-info">
                            <h3>📋 Informações do Ticket</h3>
                            <p><strong>ID do Ticket:</strong> #{ticket_id}</p>
                            <p><strong>Status:</strong> <span class="status-badge">Pendente</span></p>
                            <p><strong>Posição na Fila:</strong> {posicao_fila}º</p>
                            <p><strong>Prioridade:</strong> {dados_ticket['prioridade']}</p>
                            <p><strong>Data de Criação:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                        </div>
                        
                        <div class="ticket-info">
                            <h3>💻 Dispositivos/Serviços Solicitados</h3>
                            <p>{dados_ticket['dispositivos']}</p>
                        </div>
                        
                        <div class="ticket-info">
                            <h3>📝 Descrição da Necessidade</h3>
                            <p>{dados_ticket['necessidade']}</p>
                        </div>
                        
                        <p>Atenciosamente,<br><strong>Equipe Mavi Suporte</strong></p>
                    </div>
                    
                    <div class="footer">
                        <p>Este é um email automático. Por favor, não responda.</p>
                        <p>© {datetime.now().year} Mavi Click - Sistema de Suporte</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._enviar_email(email_destino, assunto, corpo_html)
            
        except Exception as e:
            print(f"Erro ao enviar email de confirmação: {str(e)}")
            return False
    
    def enviar_notificacao_admin(self, ticket_id: str, dados_ticket: Dict[str, Any]) -> bool:
        """Envia notificação para o admin sobre novo ticket"""
        if not self.enabled:
            return False
        
        try:
            # --- ALTERAÇÃO APLICADA AQUI ---
            # Usa a variável self.admin_email lida do .env
            email_admin = self.admin_email
            assunto = f"🔔 Novo Ticket #{ticket_id} - Mavi Suporte"
            
            corpo_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(90deg, #00D4AA, #00B894); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .ticket-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔔 Mavi Suporte - Admin</h1>
                        <h2>Novo Ticket Criado</h2>
                    </div>
                    
                    <div class="content">
                        <p>Um novo ticket foi criado no sistema:</p>
                        
                        <div class="ticket-info">
                            <h3>📋 Detalhes do Ticket #{ticket_id}</h3>
                            <p><strong>Solicitante:</strong> {dados_ticket['nome']}</p>
                            <p><strong>Email:</strong> {dados_ticket['email']}</p>
                            <p><strong>Prioridade:</strong> {dados_ticket['prioridade']}</p>
                            <p><strong>Descrição:</strong> {dados_ticket['necessidade']}</p>
                        </div>
                        
                        <p><strong>Acesse o sistema para gerenciar este ticket.</strong></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._enviar_email(email_admin, assunto, corpo_html)
            
        except Exception as e:
            print(f"Erro ao enviar notificação para admin: {str(e)}")
            return False
    
    def _enviar_email(self, email_destino: str, assunto: str, corpo_html: str) -> bool:
        """Método privado para enviar email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"Mavi Suporte <{self.email_usuario}>"
            msg['To'] = email_destino
            msg['Subject'] = assunto
            
            html_part = MIMEText(corpo_html, 'html', 'utf-8')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_usuario, self.email_senha)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            return False

# Instância global do serviço
email_service = EmailService()
