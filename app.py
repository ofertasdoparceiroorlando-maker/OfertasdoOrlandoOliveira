
import os
import sys
from flask import Flask, render_template, redirect, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# 🔐 Carrega variáveis de ambiente
load_dotenv()

# 🔧 Ajusta o path do projeto
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 🚀 Inicializa o app Flask
app = Flask(__name__, static_folder="static", template_folder="templates")

# ⚙️ Configurações do Flask a partir do .env
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///meubanco.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = os.getenv("FLASK_ENV") == "development"

# 🔌 Inicializa extensões
from extensions import db
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# 📦 Registra os blueprints
from routes.ofertas import ofertas_bp
from routes.usuarios import usuarios_bp
from routes.admin import admin_bp
from routes.produto import produto_bp

app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
app.register_blueprint(ofertas_bp, url_prefix="/ofertas")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(produto_bp, url_prefix="/produto")

# 📤 Serviço de envio ao Telegram
from services.telegram import enviar_mensagem, enviar_foto

# 🧪 Rotas de teste do bot
@app.route("/bot/enviar")
def bot_enviar():
    enviar_mensagem("Mensagem enviada pelo Flask ✅")
    return "Mensagem enviada ao Telegram!"

@app.route("/bot/enviar-dinamico")
def bot_enviar_dinamico():
    msg = request.args.get("msg", "Mensagem padrão ✅")
    enviar_mensagem(msg)
    return f"Mensagem enviada: {msg}"

# 🖼️ Rota para o painel HTML
@app.route("/painel")
def painel():
    return render_template("painel.html")

# 🌍 Rota raiz
@app.route("/")
def home():
    return redirect("/painel")

# 🏁 Executa o app (Railway/Render/Heroku usam PORT do ambiente)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
