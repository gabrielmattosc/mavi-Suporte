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

class EmailService:
    """Serviço para envio de emails"""
    
    def __init__(self, 
                 smtp_server: str = "smtp.gmail.com",
                 smtp_port: int = 587,
                 sender_email: str = "gabriel@maviclick.com",
                 sender_password: str = ""):
        """
        Inicializa o serviço de email
        
        Args:
            smtp_server: Servidor SMTP
            smtp_port: Porta SMTP
            sender_email: Email remetente
            sender_password: Senha do email remetente
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.enabled = bool(sender_password)  # Só ativa se tiver senha
    
    def _create_html_template(self, titulo: str, conteudo: str, cor_tema: str = "#00D4AA") -> str:
        """
        Cria template HTML para emails
        
        Args:
            titulo: Título do email
            conteudo: Conteúdo HTML do email
            cor_tema: Cor tema do email
            
        Returns:
            HTML completo do email
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(90deg, {cor_tema}, #00B894);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: bold;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .info-box {{
                    background: #f8f9fa;
                    border-left: 4px solid {cor_tema};
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 0 5px 5px 0;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 5px 12px;
                    border-radius: 15px;
                    font-size: 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .status-pendente {{ background: #ffc107; color: #000; }}
                .status-andamento {{ background: #17a2b8; color: white; }}
                .status-concluida {{ background: #28a745; color: white; }}
                .priority-normal {{ background: #6c757d; color: white; }}
                .priority-alta {{ background: #ffc107; color: #000; }}
                .priority-urgente {{ background: #dc3545; color: white; }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    border-top: 1px solid #e9ecef;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background: linear-gradient(90deg, {cor_tema}, #00B894);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin: 20px 0;
                }}
                @media (max-width: 600px) {{
                    .grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Mavi Suporte</h1>
                    <p>{titulo}</p>
                </div>
                <div class="content">
                    {conteudo}
                </div>
                <div class="footer">
                    <p>Este é um email automático do Sistema Mavi Suporte.</p>
                    <p>&copy; 2025 Mavi Click. Todos os direitos reservados.</p>
                    <p>Para suporte, entre em contato: gabriel@maviclick.com</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def enviar_confirmacao_ticket(self, 
                                email_destinatario: str, 
                                ticket_id: str, 
                                posicao_fila: int, 
                                dados_ticket: Dict[str, Any]) -> bool:
        """
        Envia email de confirmação de criação de ticket
        
        Args:
            email_destinatario: Email do usuário
            ticket_id: ID do ticket
            posicao_fila: Posição na fila
            dados_ticket: Dados completos do ticket
            
        Returns:
            True se enviado com sucesso
        """
        if not self.enabled:
            return False
        
        try:
            assunto = f"Ticket #{ticket_id} - Confirmação de Solicitação - Mavi Suporte"
            
            # Conteúdo do email
            conteudo = f"""
            <p>Olá <strong>{dados_ticket.get('nome', 'Usuário')}</strong>,</p>
            
            <p>Sua solicitação de suporte foi registrada com sucesso! Abaixo estão os detalhes:</p>
            
            <div class="info-box">
                <h3>📋 Informações do Ticket</h3>
                <div class="grid">
                    <div>
                        <p><strong>ID do Ticket:</strong> #{ticket_id}</p>
                        <p><strong>Status:</strong> <span class="status-badge status-pendente">Pendente</span></p>
                        <p><strong>Posição na Fila:</strong> {posicao_fila}º</p>
                    </div>
                    <div>
                        <p><strong>Prioridade:</strong> 
                            <span class="status-badge priority-{dados_ticket.get('prioridade', 'normal').lower()}">
                                {dados_ticket.get('prioridade', 'Normal')}
                            </span>
                        </p>
                        <p><strong>Data de Criação:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                    </div>
                </div>
            </div>
            
            <div class="info-box">
                <h3>👤 Seus Dados</h3>
                <p><strong>Nome:</strong> {dados_ticket.get('nome', 'N/A')}</p>
                <p><strong>Email:</strong> {dados_ticket.get('email', 'N/A')}</p>
                <p><strong>Squad Leader:</strong> {dados_ticket.get('squad_leader', 'N/A')}</p>
            </div>
            
            <div class="info-box">
                <h3>💻 Solicitação</h3>
                <p><strong>Dispositivos/Serviços:</strong></p>
                <p>{dados_ticket.get('dispositivos', 'N/A')}</p>
                <p><strong>Descrição:</strong></p>
                <p style="background: #e9ecef; padding: 10px; border-radius: 5px;">
                    {dados_ticket.get('necessidade', 'N/A')}
                </p>
            </div>
            
            <div class="info-box">
                <h3>📋 Próximos Passos</h3>
                <ol>
                    <li><strong>Análise:</strong> Nossa equipe analisará sua solicitação</li>
                    <li><strong>Processamento:</strong> Você será contatado conforme a prioridade</li>
                    <li><strong>Atendimento:</strong> Acompanhe o status através do sistema</li>
                </ol>
            </div>
            
            <p><strong>⚠️ Importante:</strong> Guarde o número do seu ticket (<strong>#{ticket_id}</strong>) para futuras consultas.</p>
            
            <p>Atenciosamente,<br>
            <strong>Equipe Mavi Suporte</strong></p>
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
        """
        Envia email de atualização de status do ticket
        
        Args:
            email_destinatario: Email do usuário
            ticket_id: ID do ticket
            novo_status: Novo status do ticket
            observacao: Observação opcional
            
        Returns:
            True se enviado com sucesso
        """
        if not self.enabled:
            return False
        
        try:
            assunto = f"Ticket #{ticket_id} - Atualização de Status - Mavi Suporte"
            
            # Mapeia status para cores
            status_colors = {
                "Pendente": "#ffc107",
                "Em andamento": "#17a2b8", 
                "Concluída": "#28a745"
            }
            
            cor_status = status_colors.get(novo_status, "#6c757d")
            
            # Conteúdo específico por status
            if novo_status == "Concluída":
                status_message = """
                <div class="info-box" style="border-left-color: #28a745;">
                    <h3>🎉 Ticket Concluído!</h3>
                    <p>Sua solicitação foi finalizada com sucesso. Esperamos que tenha atendido às suas expectativas.</p>
                    <p>Se precisar de mais alguma coisa, não hesite em criar um novo ticket.</p>
                </div>
                """
            elif novo_status == "Em andamento":
                status_message = """
                <div class="info-box" style="border-left-color: #17a2b8;">
                    <h3>🔧 Ticket em Andamento</h3>
                    <p>Nossa equipe está trabalhando na sua solicitação. Você será notificado quando houver novas atualizações.</p>
                </div>
                """
            else:
                status_message = """
                <div class="info-box">
                    <h3>📋 Status Atualizado</h3>
                    <p>O status do seu ticket foi atualizado. Acompanhe as mudanças através do sistema.</p>
                </div>
                """
            
            conteudo = f"""
            <p>Olá,</p>
            
            <p>Seu ticket foi atualizado. Veja os detalhes abaixo:</p>
            
            <div class="info-box">
                <h3>📋 Atualização do Status</h3>
                <p><strong>Ticket:</strong> #{ticket_id}</p>
                <p><strong>Novo Status:</strong> 
                    <span class="status-badge" style="background: {cor_status}; color: white;">
                        {novo_status}
                    </span>
                </p>
                <p><strong>Data da Atualização:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                
                {f'<p><strong>Observações:</strong></p><p style="background: #e9ecef; padding: 10px; border-radius: 5px;">{observacao}</p>' if observacao else ''}
            </div>
            
            {status_message}
            
            <p>Atenciosamente,<br>
            <strong>Equipe Mavi Suporte</strong></p>
            """
            
            html_content = self._create_html_template("Atualização do Ticket", conteudo, cor_status)
            
            return self._enviar_email(email_destinatario, assunto, html_content)
            
        except Exception as e:
            st.error(f"Erro ao enviar email de atualização: {str(e)}")
            return False
    
    def enviar_notificacao_admin(self, 
                               ticket_id: str, 
                               dados_ticket: Dict[str, Any]) -> bool:
        """
        Envia notificação para o admin sobre novo ticket
        
        Args:
            ticket_id: ID do ticket
            dados_ticket: Dados do ticket
            
        Returns:
            True se enviado com sucesso
        """
        if not self.enabled:
            return False
        
        try:
            assunto = f"🚨 Novo Ticket #{ticket_id} - Mavi Suporte"
            
            # Cor baseada na prioridade
            prioridade = dados_ticket.get('prioridade', 'Normal')
            cor_prioridade = {
                'Normal': '#6c757d',
                'Alta': '#ffc107', 
                'Urgente': '#dc3545'
            }.get(prioridade, '#6c757d')
            
            conteudo = f"""
            <p>Um novo ticket foi criado no sistema:</p>
            
            <div class="info-box">
                <h3>🎫 Informações do Ticket</h3>
                <div class="grid">
                    <div>
                        <p><strong>ID:</strong> #{ticket_id}</p>
                        <p><strong>Prioridade:</strong> 
                            <span class="status-badge" style="background: {cor_prioridade}; color: white;">
                                {prioridade}
                            </span>
                        </p>
                    </div>
                    <div>
                        <p><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                        <p><strong>Status:</strong> Pendente</p>
                    </div>
                </div>
            </div>
            
            <div class="info-box">
                <h3>👤 Dados do Solicitante</h3>
                <p><strong>Nome:</strong> {dados_ticket.get('nome', 'N/A')}</p>
                <p><strong>Email:</strong> {dados_ticket.get('email', 'N/A')}</p>
                <p><strong>Squad Leader:</strong> {dados_ticket.get('squad_leader', 'N/A')}</p>
            </div>
            
            <div class="info-box">
                <h3>💻 Solicitação</h3>
                <p><strong>Dispositivos:</strong> {dados_ticket.get('dispositivos', 'N/A')}</p>
                <p><strong>Descrição:</strong></p>
                <p style="background: #e9ecef; padding: 10px; border-radius: 5px;">
                    {dados_ticket.get('necessidade', 'N/A')}
                </p>
            </div>
            
            <p><strong>⚡ Ação necessária:</strong> Acesse o painel administrativo para processar este ticket.</p>
            
            <p style="text-align: center;">
                <a href="#" class="button">🔧 Acessar Painel Admin</a>
            </p>
            """
            
            html_content = self._create_html_template("Novo Ticket Criado", conteudo, "#dc3545")
            
            return self._enviar_email("gabriel@maviclick.com", assunto, html_content)
            
        except Exception as e:
            st.error(f"Erro ao enviar notificação para admin: {str(e)}")
            return False
    
    def _enviar_email(self, destinatario: str, assunto: str, html_content: str) -> bool:
        """
        Envia email usando SMTP
        
        Args:
            destinatario: Email do destinatário
            assunto: Assunto do email
            html_content: Conteúdo HTML do email
            
        Returns:
            True se enviado com sucesso
        """
        try:
            # Cria mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = assunto
            message["From"] = self.sender_email
            message["To"] = destinatario
            
            # Adiciona conteúdo HTML
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Cria contexto SSL
            context = ssl.create_default_context()
            
            # Conecta e envia
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, destinatario, message.as_string())
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            return False

# Instância global do serviço de email
@st.cache_resource
def get_email_service() -> EmailService:
    """
    Obtém a instância do serviço de email
    
    Returns:
        Instância do serviço de email
    """
    # Tenta obter senha do email das variáveis de ambiente ou secrets
    email_password = ""
    
    # Verifica se há configuração de secrets no Streamlit
    try:
        if hasattr(st, 'secrets') and 'email' in st.secrets:
            email_password = st.secrets.email.get('password', '')
    except:
        pass
    
    # Se não encontrou nas secrets, tenta variável de ambiente
    if not email_password:
        import os
        email_password = os.getenv('MAIL_PASSWORD', '')
    
    return EmailService(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email="gabriel@maviclick.com",
        sender_password=email_password
    )

