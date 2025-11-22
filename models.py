from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db 
from datetime import datetime

class Oferta(db.Model):
    __tablename__ = 'oferta'  # ✅ Isso resolve o problema

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)  # 👈 esse campo precisa existir
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(255))
    loja = db.Column(db.String(100))
    link_afiliado = db.Column(db.String(255))
    link = db.Column(db.String(255))
    categoria = db.Column(db.String(100))
    destaque = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer, default=0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    categoria_id = db.Column(db.Integer)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    senha_hash = db.Column(db.String(128))
    token = db.Column(db.String(32))

    @property
    def senha(self):
        raise AttributeError("Senha não pode ser lida diretamente.")

    @senha.setter
    def senha(self, senha_plana):
        self.senha_hash = generate_password_hash(senha_plana)

    def verificar_senha(self, senha_plana):
        return check_password_hash(self.senha_hash, senha_plana)

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    oferta_id = db.Column(db.Integer, db.ForeignKey('oferta.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    autor = db.relationship('Usuario')
    oferta = db.relationship('Oferta')

class Favorito(db.Model):
    __tablename__ = 'favoritos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    oferta_id = db.Column(db.Integer, db.ForeignKey('oferta.id'), nullable=False)
    data_favorito = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos (opcional, mas útil)
    usuario = db.relationship('Usuario', backref='favoritos')
    oferta = db.relationship('Oferta', backref='favoritos')


