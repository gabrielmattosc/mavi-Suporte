"""
Módulo de estilos customizados para Streamlit
"""

def get_custom_css():
    """Retorna CSS customizado inspirado no design da Maviclick"""
    return """
    <style>
    /* Importa fontes do Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e configurações gerais */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header customizado */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Logo styling */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    /* Formulário */
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    /* Campos do formulário */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > div {
        border-radius: 8px !important;
        border: 2px solid #e9ecef !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Labels dos campos */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stMultiSelect > label,
    .stDateInput > label {
        font-weight: 600 !important;
        color: #495057 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Botão principal */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Mensagens de sucesso */
    .stSuccess {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3) !important;
    }
    
    /* Mensagens de erro */
    .stError {
        background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }
    
    /* Cards de estatísticas */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.12);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin: 0;
    }
    
    .stat-label {
        color: #6c757d;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div > div > div {
        background-color: #667eea !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
    }
    
    /* Tabelas */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
    }
    
    /* Métricas */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 4px solid #667eea;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .form-container {
            padding: 1.5rem;
        }
        
        .stat-number {
            font-size: 2rem;
        }
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Esconder elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Customizar a barra de progresso */
    .stProgress .st-bo {
        background-color: #e9ecef;
    }
    
    /* Estilo para containers de métricas */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e9ecef;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Estilo para expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Estilo para tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: 1px solid #e9ecef;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    </style>
    """

def get_custom_components():
    """Retorna componentes HTML customizados"""
    return {
        'header': """
        <div class="main-header fade-in">
            <h1>🎯 Mavi Suporte</h1>
            <p>Sistema Inteligente de Gestão de Solicitações</p>
        </div>
        """,
        
        'form_container_start': '<div class="form-container fade-in">',
        'form_container_end': '</div>',
        
        'stat_card': lambda number, label: f"""
        <div class="stat-card fade-in">
            <div class="stat-number">{number}</div>
            <div class="stat-label">{label}</div>
        </div>
        """
    }

def apply_custom_styling():
    """Aplica o CSS customizado ao Streamlit"""
    import streamlit as st
    st.markdown(get_custom_css(), unsafe_allow_html=True)

