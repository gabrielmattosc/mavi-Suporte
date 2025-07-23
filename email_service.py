"""
Serviço de envio de email para o sistema Mavi Suporte (Streamlit)
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any
import streamlit as st
import os

class EmailService:
    """Serviço para envio de emails"""
    
    def __init__(self, 
                 smtp_server: str,
                 smtp_port: int,
                 sender_email: str,
                 sender_password: str,
                 admin_email: str):
        """Inicializa o serviço de email"""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.admin_email = admin_email
        self.enabled = bool(sender_password and sender_email)

    def _create_html_template(self, titulo: str, conteudo: str, cor_tema: str = "#00D4AA") -> str:
        """Cria template HTML para emails"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .header {{ background: linear-gradient(90deg, {cor_tema}, #00B894); color: white; padding: 30px 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ padding: 30px 20px; }}
                .info-box {{ background: #f8f9fa; border-left: 4px solid {cor_tema}; padding: 15px; margin: 20px 0; border-radius: 0 5px 5px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #e9ecef; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>🎯 Mavi Suporte</h1><p>{titulo}</p></div>
                <div class="content">{conteudo}</div>
                <div class="footer"><p>Este é um email automático do Sistema Mavi Suporte.</p><p>&copy; {datetime.now().year} Mavi Click. Todos os direitos reservados.</p></div>
            </div>
        </body>
        </html>
        """
    
    def enviar_confirmacao_ticket(self, 
                                  email_destinatario: str, 
                                  ticket_id: str, 
                                  posicao_fila: int, 
                                  dados_ticket: Dict[str, Any]) -> bool:
        """Envia email de confirmação de criação de ticket para o USUÁRIO"""
        if not self.enabled:
            return False
        
        try:
            assunto = f"Ticket #{ticket_id} - Confirmação de Solicitação - Mavi Suporte"
            conteudo = f"""
            <p>Olá <strong>{dados_ticket.get('nome', 'Usuário')}</strong>,</p>
            <p>Sua solicitação de suporte foi registrada com sucesso! Abaixo estão os detalhes:</p>
            <div class="info-box">
                <h3>📋 Informações do Ticket</h3>
                <p><strong>ID do Ticket:</strong> #{ticket_id}</p>
                <p><strong>Status:</strong> Pendente</p>
                <p><strong>Posição na Fila:</strong> {posicao_fila}º</p>
                <p><strong>Prioridade:</strong> {dados_ticket.get('prioridade', 'Normal')}</p>
            </div>
            <p><strong>⚠️ Importante:</strong> Guarde o número do seu ticket para futuras consultas.</p>
            <p>Atenciosamente,<br><strong>Equipe Mavi Suporte</strong></p>
            """
            html_content = self._create_html_template("Ticket Criado com Sucesso!", conteudo)
            return self._enviar_email(email_destinatario, assunto, html_content)
        except Exception as e:
            st.error(f"Erro ao enviar email de confirmação: {str(e)}")
            return False
    
    def enviar_atualizacao_status(self, 
                                  email_destinatario: str, 
                                  ticket_id: str, 
                                  novo_status: str, 
                                  observacao: str = None) -> bool:
        """Envia email de atualização de status do ticket para o USUÁRIO"""
        if not self.enabled:
            return False
        
        try:
            assunto = f"Ticket #{ticket_id} - Atualização de Status - Mavi Suporte"
            conteudo = f"""
            <p>Olá,</p>
            <p>O status do seu ticket #{ticket_id} foi atualizado para: <strong>{novo_status}</strong>.</p>
            {f'<div class="info-box"><p><strong>Observações da equipe:</strong></p><p>{observacao}</p></div>' if observacao else ''}
            <p>Atenciosamente,<br><strong>Equipe Mavi Suporte</strong></p>
            """
            html_content = self._create_html_template("Atualização do seu Ticket", conteudo)
            return self._enviar_email(email_destinatario, assunto, html_content)
        except Exception as e:
            st.error(f"Erro ao enviar email de atualização: {str(e)}")
            return False
    
    def enviar_notificacao_admin(self, 
                                 ticket_id: str, 
                                 dados_ticket: Dict[str, Any]) -> bool:
        """Envia notificação para o ADMIN sobre novo ticket"""
        if not self.enabled:
            return False
        
        try:
            assunto = f"🚨 Novo Ticket Criado #{ticket_id} - Prioridade: {dados_ticket.get('prioridade', 'Normal')}"
            conteudo = f"""
            <p>Um novo ticket foi criado no sistema:</p>
            <div class="info-box">
                <p><strong>ID:</strong> #{ticket_id}</p>
                <p><strong>Solicitante:</strong> {dados_ticket.get('nome', 'N/A')} ({dados_ticket.get('email', 'N/A')})</p>
                <p><strong>Prioridade:</strong> {dados_ticket.get('prioridade', 'Normal')}</p>
                <p><strong>Descrição:</strong> {dados_ticket.get('necessidade', 'N/A')}</p>
            </div>
            <p>Acesse o painel administrativo para gerenciar a solicitação.</p>
            """
            html_content = self._create_html_template("Novo Ticket Recebido", conteudo, "#dc3545")
            
            return self._enviar_email(self.admin_email, assunto, html_content)
            
        except Exception as e:
            st.error(f"Erro ao enviar notificação para admin: {str(e)}")
            return False
    
    def _enviar_email(self, destinatario: str, assunto: str, html_content: str) -> bool:
        """Motor de envio de email usando SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = assunto
            message["From"] = self.sender_email
            message["To"] = destinatario
            
            message.attach(MIMEText(html_content, "html"))
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, destinatario, message.as_string())
            
            return True
            
        except Exception as e:
            print(f"FALHA NO ENVIO DE EMAIL: {str(e)}")
            return False

# Instância global do serviço de email
@st.cache_resource
def get_email_service() -> EmailService:
    """
    Obtém a instância do serviço de email a partir das configurações seguras.
    """
    smtp_server, smtp_port, sender_email, sender_password, admin_email = "", 0, "", "", ""
    
    try:
        if hasattr(st, 'secrets'):
            email_config = st.secrets.get("email", {})
            # --- ALTERAÇÃO PRINCIPAL AQUI ---
            smtp_server = "smtp.gmail.com" # Servidor correto para o Gmail
            smtp_port = 587                # Porta padrão
            sender_email = email_config.get('username', '')
            sender_password = email_config.get('password', '')
            admin_email = email_config.get('admin_email', sender_email)
        else:
            # Fallback para variáveis de ambiente
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", 587))
            sender_email = os.getenv("EMAIL_USERNAME", "")
            sender_password = os.getenv("EMAIL_PASSWORD", "")
            admin_email = os.getenv("ADMIN_EMAIL", sender_email)
    except Exception as e:
        print(f"AVISO: Não foi possível carregar as configurações de email. Detalhes: {e}")

    return EmailService(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        sender_email=sender_email,
        sender_password=sender_password,
        admin_email=admin_email
    )
