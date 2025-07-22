# 🎯 Sistema de Suporte Mavi - Streamlit

Sistema moderno de gerenciamento de tickets de suporte desenvolvido com Streamlit, MongoDB e design responsivo.

## ✨ Funcionalidades

### 🎫 **Gestão de Tickets**
- ✅ Criação de solicitações com formulário intuitivo
- ✅ Consulta de tickets por ID
- ✅ Acompanhamento de status em tempo real
- ✅ Sistema de filas com posicionamento
- ✅ Persistência de dados do formulário

### 🔐 **Sistema de Autenticação**
- ✅ Login com diferentes níveis de acesso
- ✅ **Admin**: Acesso total ao sistema
- ✅ **Usuário**: Criação e consulta de tickets
- ✅ **Público**: Acesso limitado sem login

### 📊 **Dashboard e Relatórios**
- ✅ Gráficos interativos com Plotly
- ✅ Estatísticas em tempo real
- ✅ Análise de tendências
- ✅ Geração de relatórios PDF
- ✅ Exportação de dados (CSV/JSON)

### 📧 **Notificações por Email**
- ✅ Confirmação automática de tickets
- ✅ Notificações de mudança de status
- ✅ Alertas para administradores
- ✅ Templates HTML responsivos

### 🎨 **Design Moderno**
- ✅ Layout responsivo com cores da Mavi
- ✅ Logo integrado em todas as páginas
- ✅ Interface intuitiva e moderna
- ✅ Componentes customizados

## 🚀 Como Executar

### 📋 **Pré-requisitos**
- Python 3.8+
- MongoDB (opcional - usa fallback em memória)

### 🔧 **Instalação**

1. **Clone ou extraia o projeto**
```bash
cd mavi_suporte_streamlit
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure o email (opcional)**
```bash
# Crie um arquivo .streamlit/secrets.toml
[email]
password = "sua_senha_do_email"
```

4. **Execute a aplicação**
```bash
streamlit run app.py
```

5. **Acesse no navegador**
```
http://localhost:8501
```

## 👥 **Contas de Teste**

### 🔑 **Credenciais**
- **Admin**: `admin` / `admin123`
- **Usuário**: `teste` / `teste123`
- **Público**: Clique em "Acesso Público"

### 🎯 **Permissões**

| Funcionalidade | Admin | Usuário | Público |
|---|---|---|---|
| Criar Tickets | ✅ | ✅ | ✅ |
| Consultar Tickets | ✅ | ✅ | ✅ |
| Dashboard | ✅ | ✅ | ✅ |
| Relatórios PDF | ✅ | ❌ | ❌ |
| Gerenciar Tickets | ✅ | ❌ | ❌ |
| Administração | ✅ | ❌ | ❌ |

## 📁 **Estrutura do Projeto**

```
mavi_suporte_streamlit/
├── app.py                 # Aplicação principal
├── database.py           # Gerenciamento de dados
├── admin.py              # Módulo administrativo
├── email_service.py      # Serviço de email
├── reports.py            # Geração de relatórios
├── requirements.txt      # Dependências
├── mavi.logo.png        # Logo da empresa
├── .streamlit/
│   └── config.toml      # Configurações do Streamlit
└── README.md            # Esta documentação
```

## 🔧 **Configurações**

### 📧 **Email**
Para ativar o envio de emails, configure:

1. **Via secrets.toml**:
```toml
[email]
password = "sua_senha_app_gmail"
```

2. **Via variável de ambiente**:
```bash
export MAIL_PASSWORD="sua_senha_app_gmail"
```

### 🗄️ **Banco de Dados**
- **MongoDB**: Conecta automaticamente em `mongodb://localhost:27017/`
- **Fallback**: Usa armazenamento em memória se MongoDB não estiver disponível

## 🎨 **Personalização**

### 🎨 **Cores da Mavi**
- **Verde Principal**: `#00D4AA`
- **Verde Escuro**: `#00B894`
- **Verde Claro**: `#00E5BB`

### 🖼️ **Logo**
- Substitua `mavi.logo.png` pelo logo desejado
- Formato recomendado: PNG com fundo transparente
- Dimensões: 300px de largura

## 📊 **Funcionalidades Avançadas**

### 📈 **Dashboard Interativo**
- Gráficos de pizza para status
- Gráficos de barras para dispositivos
- Timeline de criação de tickets
- Análise por prioridade
- Detalhes expandíveis ao clicar

### 📄 **Relatórios PDF**
- Relatório completo
- Relatório por status
- Relatório por período
- Incluir/excluir gráficos
- Download automático

### 🔍 **Análises Detalhadas**
- Performance de atendimento
- Tendências temporais
- Exportação de dados
- Métricas customizadas

## 🚀 **Deploy**

### 🌐 **Streamlit Cloud**
1. Faça upload do projeto para GitHub
2. Conecte com Streamlit Cloud
3. Configure secrets para email
4. Deploy automático

### 🐳 **Docker**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

### ☁️ **Heroku**
```bash
# Procfile
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

## 🔧 **Solução de Problemas**

### ❌ **Problemas Comuns**

1. **MongoDB não conecta**
   - Sistema usa fallback em memória automaticamente
   - Verifique se MongoDB está rodando na porta 27017

2. **Email não envia**
   - Configure a senha do email nas secrets
   - Use senha de app do Gmail (não a senha normal)

3. **Logo não aparece**
   - Verifique se `mavi.logo.png` está na raiz do projeto
   - Formato deve ser PNG, JPG ou similar

4. **Erro de dependências**
   - Execute: `pip install -r requirements.txt`
   - Use Python 3.8 ou superior

## 📞 **Suporte**

Para suporte técnico:
- **Email**: gabriel@maviclick.com
- **Sistema**: Crie um ticket através da própria aplicação

## 📄 **Licença**

© 2025 Mavi Click. Todos os direitos reservados.

---

**Desenvolvido com ❤️ usando Streamlit**

