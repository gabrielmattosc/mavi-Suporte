"""
Sistema de notificações para o Mavi Suporte
Suporta e-mail, SMS via Twilio e WhatsApp via PyWhatKit
"""
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa módulo WhatsApp
try:
    from .whatsapp_sender import enviar_notificacao_whatsapp
    WHATSAPP_DISPONIVEL = True
except ImportError:
    WHATSAPP_DISPONIVEL = False
    logging.warning("PyWhatKit não disponível. Notificações WhatsApp desabilitadas.")

# Configurações
MAVI_EMAIL = os.getenv('MAVI_EMAIL', 'gabriel@maviclick.com')
MAVI_EMAIL_PASSWORD = os.getenv('MAVI_EMAIL_PASSWORD', '')

class NotificationManager:
    """Gerenciador de notificações multi-canal"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def criar_template_email_html(self, ticket_id, nome, status, posicao_fila=None, observacoes=None):
        """Cria template HTML responsivo para e-mail"""
        
        # Cores baseadas no status
        cores_status = {
            'Pendente': {'cor': '#ffc107', 'emoji': '⏳'},
            'Em andamento': {'cor': '#17a2b8', 'emoji': '🔄'},
            'Concluída': {'cor': '#28a745', 'emoji': '✅'}
        }
        
        info_status = cores_status.get(status, {'cor': '#6c757d', 'emoji': '📋'})
        
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mavi Suporte - Ticket #{ticket_id}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 2rem;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2rem;
                    font-weight: 700;
                }}
                .content {{
                    padding: 2rem;
                }}
                .ticket-info {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                    border-left: 4px solid {info_status['cor']};
                }}
                .status-badge {{
                    display: inline-block;
                    background: {info_status['cor']};
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 20px;
                    font-weight: 600;
                    font-size: 0.9rem;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 1.5rem;
                    text-align: center;
                    color: #6c757d;
                    font-size: 0.9rem;
                }}
                @media (max-width: 600px) {{
                    .container {{
                        margin: 0;
                        border-radius: 0;
                    }}
                    .header, .content, .footer {{
                        padding: 1rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Mavi Suporte</h1>
                    <p style="margin: 0; opacity: 0.9;">Sistema Inteligente de Gestão de Solicitações</p>
                </div>
                
                <div class="content">
                    <h2>Olá, {nome}! 👋</h2>
                    
                    <p>Temos uma atualização sobre seu ticket de suporte:</p>
                    
                    <div class="ticket-info">
                        <h3 style="margin-top: 0; color: #333;">
                            {info_status['emoji']} Ticket #{ticket_id}
                        </h3>
                        
                        <p><strong>Status:</strong> 
                            <span class="status-badge">{status}</span>
                        </p>
                        
                        {f'<p><strong>Posição na fila:</strong> {posicao_fila}</p>' if posicao_fila else ''}
                        
                        {f'<p><strong>Observações:</strong><br>{observacoes}</p>' if observacoes else ''}
                        
                        <p><strong>Data/Hora:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                    </div>
                    
                    <p>Continuaremos acompanhando seu ticket e você receberá novas atualizações por e-mail.</p>
                    
                    <p>Se tiver dúvidas, entre em contato conosco.</p>
                </div>
                
                <div class="footer">
                    <p><strong>Mavi Suporte</strong><br>
                    Sistema Inteligente de Gestão de Solicitações</p>
                    
                    <p>Este é um e-mail automático. Por favor, não responda.</p>
                    
                    <p style="font-size: 0.8rem; margin-top: 1rem;">
                        © 2025 Mavi. Todos os direitos reservados.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def enviar_email(self, destinatario, assunto, ticket_id, nome, status, posicao_fila=None, observacoes=None):
        """Envia e-mail de notificação com template HTML"""
        
        if not MAVI_EMAIL_PASSWORD:
            self.logger.warning("Senha de e-mail não configurada")
            return False
            
        try:
            # Cria mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = f"Mavi Suporte <{MAVI_EMAIL}>"
            msg['To'] = destinatario
            
            # Versão texto simples
            texto_simples = f"""
Olá, {nome}!

Atualização do seu ticket de suporte:

Ticket: #{ticket_id}
Status: {status}
{f'Posição na fila: {posicao_fila}' if posicao_fila else ''}
{f'Observações: {observacoes}' if observacoes else ''}
Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

Obrigado por usar o Mavi Suporte!

---
Este é um e-mail automático. Por favor, não responda.
Mavi Suporte - Sistema Inteligente de Gestão de Solicitações
            """
            
            # Versão HTML
            html_content = self.criar_template_email_html(
                ticket_id, nome, status, posicao_fila, observacoes
            )
            
            # Anexa ambas as versões
            part1 = MIMEText(texto_simples, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Envia e-mail
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(MAVI_EMAIL, MAVI_EMAIL_PASSWORD)
                server.send_message(msg)
            
            self.logger.info(f"E-mail enviado para {destinatario}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar e-mail: {str(e)}")
            return False
    
    def enviar_whatsapp(self, numero, ticket_id, nome, status, posicao_fila=None):
        """Envia notificação WhatsApp usando PyWhatKit"""
        
        if not WHATSAPP_DISPONIVEL:
            self.logger.warning("WhatsApp não disponível")
            return {'sucesso': False, 'mensagem': 'WhatsApp não configurado'}
        
        if not numero:
            return {'sucesso': False, 'mensagem': 'Número não fornecido'}
        
        try:
            resultado = enviar_notificacao_whatsapp(
                numero, ticket_id, nome, status, posicao_fila
            )
            
            if resultado['sucesso']:
                self.logger.info(f"WhatsApp enviado para {numero}")
            else:
                self.logger.error(f"Falha no WhatsApp: {resultado.get('erro', 'Erro desconhecido')}")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro no envio WhatsApp: {str(e)}")
            return {'sucesso': False, 'erro': str(e)}
    
    def enviar_sms_twilio(self, numero, mensagem):
        """Envia SMS usando Twilio (método original mantido)"""
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_number = os.getenv('TWILIO_FROM_NUMBER')
            
            if not all([account_sid, auth_token, from_number]):
                self.logger.warning("Credenciais Twilio não configuradas")
                return False
            
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(
                body=mensagem,
                from_=from_number,
                to=numero
            )
            
            self.logger.info(f"SMS Twilio enviado para {numero}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar SMS Twilio: {str(e)}")
            return False
    
    def notificar_ticket_criado(self, email, telefone, whatsapp, ticket_id, nome, posicao_fila):
        """Envia notificações para ticket criado"""
        
        resultados = {
            'email': False,
            'whatsapp': False,
            'sms': False
        }
        
        # E-mail
        if email:
            resultados['email'] = self.enviar_email(
                email,
                f"Ticket #{ticket_id} criado - Mavi Suporte",
                ticket_id,
                nome,
                "Pendente",
                posicao_fila
            )
        
        # WhatsApp
        if whatsapp and WHATSAPP_DISPONIVEL:
            resultado_whats = self.enviar_whatsapp(
                whatsapp, ticket_id, nome, "Pendente", posicao_fila
            )
            resultados['whatsapp'] = resultado_whats['sucesso']
        
        # SMS Twilio (se telefone fornecido e diferente do WhatsApp)
        if telefone and telefone != whatsapp:
            mensagem_sms = f"Mavi Suporte: Ticket #{ticket_id} criado. Status: Pendente. Posição: {posicao_fila}. Você receberá atualizações por e-mail."
            resultados['sms'] = self.enviar_sms_twilio(telefone, mensagem_sms)
        
        return resultados
    
    def notificar_atualizacao_status(self, email, whatsapp, ticket_id, nome, novo_status, observacoes=None):
        """Envia notificações para atualização de status"""
        
        resultados = {
            'email': False,
            'whatsapp': False
        }
        
        # E-mail
        if email:
            resultados['email'] = self.enviar_email(
                email,
                f"Ticket #{ticket_id} atualizado - {novo_status}",
                ticket_id,
                nome,
                novo_status,
                observacoes=observacoes
            )
        
        # WhatsApp
        if whatsapp and WHATSAPP_DISPONIVEL:
            resultado_whats = self.enviar_whatsapp(
                whatsapp, ticket_id, nome, novo_status
            )
            resultados['whatsapp'] = resultado_whats['sucesso']
        
        return resultados

# Instância global
notification_manager = NotificationManager()

