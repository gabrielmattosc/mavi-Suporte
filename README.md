🎯 Mavi Suporte - Sistema Inteligente de Gestão de Solicitações
Um sistema moderno e completo para gerenciamento de solicitações de suporte, desenvolvido com Streamlit. Oferece uma interface intuitiva, autenticação de usuários e um conjunto robusto de funcionalidades para otimizar o fluxo de trabalho de suporte.

✨ Principais Funcionalidades
Sistema de Tickets: Criação de tickets com IDs únicos, fila inteligente com prioridades (Normal, Alta, Urgente) e rastreamento completo do ciclo de vida.

Autenticação Segura: Sistema de login com dois níveis de acesso (Administrador e Usuário), senhas criptografadas e controle de permissões por perfil.

Dashboard e Relatórios: Painel interativo com métricas em tempo real, gráficos dinâmicos (distribuição de status, timeline, etc.) e relatórios exportáveis em HTML, CSV e Excel.

Notificações Multicanal: Envio de notificações automáticas por:

E-mail: Templates HTML profissionais via Gmail.

SMS: Integração opcional com Twilio.

WhatsApp: Envio automatizado de mensagens via PyWhatKit.

Design Moderno: Interface com gradientes, cards com sombras suaves e componentes animados, garantindo uma experiência de uso agradável e responsiva para desktop e mobile.

Painel Administrativo Completo: Área protegida para gestão de tickets, análise de usuários e configurações gerais do sistema, incluindo um seletor para ocultar/exibir colunas na tabela de dados.

🚀 Instalação e Execução
Pré-requisitos
Python 3.8+

Conta Gmail (para notificações por e-mail)

Conta Twilio (opcional, para SMS)

1. Clone e Instale as Dependências
Bash

# Clone o projeto
git clone <seu-repositorio>
cd mavi_suporte

# Instale as dependências
pip install -r requirements.txt
2. Configure as Variáveis de Ambiente
Copie o arquivo .env.example para .env e adicione suas credenciais do Gmail e, opcionalmente, do Twilio.

Snippet de código

# Configuração do Gmail
MAVI_EMAIL=seu.email@gmail.com
MAVI_EMAIL_PASSWORD=sua_senha_de_app_gmail

# Configuração do Twilio (Opcional)
TWILIO_ACCOUNT_SID=seu_account_sid
TWILIO_AUTH_TOKEN=seu_auth_token
TWILIO_FROM_NUMBER=+5511999999999
3. Execute o Sistema
Bash

streamlit run app_with_auth.py
O sistema estará disponível em: http://localhost:8501

🔐 Acesso ao Sistema
O sistema possui dois níveis de acesso pré-configurados:

Administrador:

Login: admin

Senha: admin123

Permissões: Acesso total a todas as funcionalidades.

Usuário Padrão:

Login: teste

Senha: teste123

Permissões: Acesso limitado para criar e acompanhar as próprias solicitações.

📄 Licença
Este projeto está sob a licença MIT.

Desenvolvido por Gabriel Mattos