"""
Módulo de estilos customizados para Streamlit - Versão Atualizada com cores da imagem de referência
"""

def get_custom_css():
    """Retorna CSS customizado inspirado na imagem de referência"""
    return """
    <style>
    /* Importa fontes do Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e configurações gerais */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
    }
    
    /* Header customizado */
    .main-header {
        background: linear-gradient(135deg, #168da6 0%, #0f7a94 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(22, 141, 166, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 400;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 2px;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
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
        border-color: #168da6 !important;
        box-shadow: 0 0 0 3px rgba(22, 141, 166, 0.1) !important;
    }
    
    /* Labels dos campos */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stMultiSelect > label,
    .stDateInput > label {
        font-weight: 500 !important;
        color: #495057 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Botão principal */
    .stButton > button {
        background: linear-gradient(135deg, #168da6 0%, #0f7a94 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(22, 141, 166, 0.3) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(22, 141, 166, 0.4) !important;
        background: linear-gradient(135deg, #0f7a94 0%, #168da6 100%) !important;
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
        background: linear-gradient(135deg, #168da6 0%, #0f7a94 100%) !important;
        border-radius: 10px !important;
    }
    
    /* Cards de estatísticas */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #168da6;
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.12);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 600;
        color: #168da6;
        margin: 0;
    }
    
    .stat-label {
        color: #6c757d;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div > div > div {
        background-color: #168da6 !important;
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
        border-top: 4px solid #168da6;
    }
    
    /* Caixas de conteúdo inspiradas na imagem */
    .content-box {
        background: #168da6;
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(22, 141, 166, 0.2);
    }
    
    .content-box h3 {
        color: white;
        font-weight: 500;
        margin-bottom: 1rem;
        text-align: center;
        font-size: 1.2rem;
        letter-spacing: 1px;
    }
    
    .content-box ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .content-box li {
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        font-weight: 300;
    }
    
    .content-box li:last-child {
        border-bottom: none;
    }
    
    .content-box li:before {
        content: "•";
        color: white;
        font-weight: bold;
        display: inline-block;
        width: 1em;
        margin-left: -1em;
    }
    
    /* Títulos principais */
    h1, h2, h3 {
        color: #168da6 !important;
        font-weight: 400 !important;
        letter-spacing: 1px !important;
    }
    
    /* Subtítulos */
    .stSubheader {
        color: #168da6 !important;
        font-weight: 500 !important;
        border-bottom: 2px solid #168da6;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Login container */
    .login-container {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 8px 40px rgba(22, 141, 166, 0.15);
        border: 1px solid #e9ecef;
        margin: 2rem 0;
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
        
        .content-box {
            padding: 1.5rem;
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
        border-left: 4px solid #168da6;
    }
    
    /* Estilo para expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #168da6 0%, #0f7a94 100%);
        color: white !important;
        border-radius: 8px;
        font-weight: 500;
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
        color: #168da6;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #168da6 0%, #0f7a94 100%);
        color: white;
    }
    
    /* Estilo para selectbox */
    .stSelectbox > div > div {
        border-color: #168da6 !important;
    }
    
    /* Estilo para checkbox */
    .stCheckbox > label > div {
        background-color: #168da6 !important;
    }
    
    /* Estilo para radio buttons */
    .stRadio > div {
        color: #168da6 !important;
    }
    </style>
    """

def get_custom_components():
    """Retorna componentes HTML customizados"""
    return {
        'header': """
        <div class="main-header fade-in">
            <h1>🎯 MAVI SUPORTE</h1>
            <p>Sistema Inteligente de Gestão de Solicitações</p>
        </div>
        """,
        
        'form_container_start': '<div class="form-container fade-in">',
        'form_container_end': '</div>',
        
        'login_container_start': '<div class="login-container fade-in">',
        'login_container_end': '</div>',
        
        'content_box': lambda title, items: f"""
        <div class="content-box fade-in">
            <h3>{title}</h3>
            <ul>
                {''.join([f'<li>{item}</li>' for item in items])}
            </ul>
        </div>
        """,
        
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

