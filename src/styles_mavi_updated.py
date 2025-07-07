"""
Módulo de estilos customizados para Streamlit - Atualizado com tema escuro e azul neon
"""
import streamlit as st

def get_custom_css():
    """Retorna CSS customizado com tema escuro e azul neon, inspirado no logo Mavi"""
    return """
    <style>
    /* Importa fontes do Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Cores do novo tema */
    :root {
        --neon-blue: #00BFFF;
        --component-dark: #1A1A1A;
        --text-neon: #00BFFF;
        --text-secondary: #CCCCCC;
    }
    
    /* Reset e configurações gerais */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: var(--background-dark);
        color: var(--text-secondary);
    }
    
    /* Header customizado - O estilo para 'header' é definido aqui */
    .main-header {
        background: var(--component-dark);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: var(--text-neon);
        border: 1px solid var(--border-color);
        box-shadow: 0 0 20px rgba(0, 191, 255, 0.2);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 0 10px var(--neon-blue);
    }
    
    /* Formulário */
    .form-container {
        background: var(--component-dark);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    /* Campos do formulário com fundo branco e borda neon */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 2px solid var(--border-color) !important;
        background-color: var(--white) !important;
        color: #000000 !important; /* Texto preto dentro do input */
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        box-shadow: 0 0 8px 3px rgba(0, 191, 255, 0.3) !important;
    }
    
    /* Labels dos campos */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stMultiSelect > label,
    .stDateInput > label {
        font-weight: 600 !important;
        color: var(--text-neon) !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Botão principal */
    .stButton > button {
        background: linear-gradient(135deg, var(--neon-blue) 0%, #008ecc 100%) !important;
        color: var(--white) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 15px rgba(0, 191, 255, 0.4) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 25px rgba(0, 191, 255, 0.6) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: var(--component-dark);
        border-right: 1px solid var(--border-color);
    }
    
    /* Esconder elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """

def get_custom_components():
    """Retorna componentes HTML customizados com o tema escuro e azul neon"""
    # CORREÇÃO: Adicionando a chave 'header' que estava faltando.
    return {
        'header': """
        <div class="main-header fade-in">
            <h1>🎯 Mavi Suporte</h1>
            <p>Sistema Inteligente de Gestão de Solicitações</p>
        </div>
        """,
        'form_container_start': '<div class="form-container fade-in">',
        'form_container_end': '</div>',
        'error_message': lambda message: f"""
        <div style="background: linear-gradient(135deg, #00BFFF 0%, #00BFFF 100%); 
                    color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <strong>❌ Erro:</strong> {message}
        </div>
        """,
    }

def apply_custom_styling():
    """Aplica o CSS customizado ao Streamlit"""
    st.markdown(get_custom_css(), unsafe_allow_html=True)