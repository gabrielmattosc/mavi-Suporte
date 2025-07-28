"""
Sistema de Suporte Mavi - Flask
Aplicação principal do sistema de gerenciamento de tickets
"""
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template
from flask_cors import CORS
from src.services.database_service import init_database
from src.routes.auth_routes import auth_bp
from src.routes.ticket_routes import ticket_bp
from src.routes.admin_routes import admin_bp
from src.routes.dashboard_routes import dashboard_bp
from src.routes.graphic_routes import graphics_bp
from src.routes.export_routes import export_bp
def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__, 
                template_folder='src/templates',
                static_folder='src/static')
    
    # Configurações
    app.config['SECRET_KEY'] = 'mavi-suporte-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Habilita CORS
    CORS(app)
    
    # Inicializa banco de dados
    init_database(app)
    
    # Registra blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(ticket_bp, url_prefix='/tickets')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(graphics_bp, url_prefix='/graphic')
    app.register_blueprint(export_bp)
    
    # Rota principal
    @app.route('/')
    def index():
        return render_template('login.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

