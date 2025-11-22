from flask import Blueprint, jsonify
from models import db, Usuario, Oferta

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/relatorios', methods=['GET'])
def relatorio_admin():
    total_usuarios = Usuario.query.count()
    total_ofertas = Oferta.query.count()
    mais_curtidas = Oferta.query.order_by(Oferta.likes.desc()).limit(5).all()

    top_ofertas = [{
        'id': o.id,
        'titulo': o.titulo,
        'likes': o.likes
    } for o in mais_curtidas]

    return jsonify({
        'total_usuarios': total_usuarios,
        'total_ofertas': total_ofertas,
        'top_ofertas': top_ofertas
    }), 200
