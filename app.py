import os
import sys
from flask import Flask, send_from_directory, render_template
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Blueprints e extensões
from extensions import db
from routes.ofertas import ofertas_bp
from routes.usuarios import usuarios_bp
from routes.admin import admin_bp
from models import Favorito, Usuario, Oferta, Comentario

# 🔧 Ajusta o path do projeto
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 🔐 Carrega variáveis de ambiente
load_dotenv()

# 🚀 Inicializa o app Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔌 Inicializa extensões
jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)

# 📦 Registra os blueprints
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
app.register_blueprint(ofertas_bp, url_prefix='/ofertas')
app.register_blueprint(admin_bp, url_prefix='/admin')

# 🖼️ Rota para o painel HTML
@app.route('/painel')
def painel():
    return render_template('painel.html')

# 🏁 Executa o app
if __name__ == '__main__':
    app.run(debug=True)
