from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import Oferta, Comentario, Usuario, db
from schemas import ComentarioSchema
from pydantic import ValidationError
from models import Favorito
from extensions import db
from datetime import datetime
from services.alertas import verificar_alerta_categoria
print(" Arquivo ofertas.py foi carregado")

ofertas_bp = Blueprint('ofertas_bp', __name__)

# 🔍 Listar todas as ofertas (com filtro opcional)
@ofertas_bp.route('/', methods=['GET'])
def listar_ofertas():
    categoria = request.args.get('categoria')
    query = Oferta.query
    if categoria:
        query = query.filter_by(categoria=categoria)
    ofertas = query.order_by(Oferta.data_criacao.desc()).all()

    resultado = [{
        'id': o.id,
        'titulo': o.titulo,
        'descricao': o.descricao,
        'preco': o.preco,
        'imagem': o.imagem,
        'link_afiliado': o.link_afiliado,
        'loja': o.loja,
        'categoria': o.categoria,
        'destaque': o.destaque,
        'likes': o.likes,
        'data_criacao': o.data_criacao.strftime('%d/%m/%Y %H:%M')
    } for o in ofertas]

    return jsonify(resultado)

# 🆕 Criar nova oferta com validação
@ofertas_bp.route('/', methods=['POST'])
@jwt_required()
def cadastrar_oferta():
    print("🚀 Rota cadastrar_oferta foi chamada")

    claims = get_jwt()
    if not claims.get("admin"):
        return jsonify({"erro": "Acesso negado"}), 403

    dados = request.get_json()

    campos_obrigatorios = ['titulo', 'descricao', 'preco', 'imagem', 'link_afiliado', 'loja', 'categoria']
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            return jsonify({'erro': f'O campo \"{campo}\" é obrigatório.'}), 400

    nova = Oferta(**{
        **dados,
        'destaque': dados.get('destaque', False),
        'likes': dados.get('likes', 0)
    })

    db.session.add(nova)
    db.session.commit()

    return jsonify({
        'mensagem': 'Oferta criada com sucesso!',
        'id': nova.id,
        'titulo': nova.titulo,
        'descricao': nova.descricao,
        'preco': nova.preco,
        'imagem': nova.imagem,
        'link_afiliado': nova.link_afiliado,
        'loja': nova.loja,
        'categoria': nova.categoria,
        'destaque': nova.destaque,
        'likes': nova.likes,
        'data_criacao': nova.data_criacao.strftime('%d/%m/%Y %H:%M')
    }), 201

# ✏️ Editar oferta
@ofertas_bp.route('/editar/<int:id>', methods=['PUT'])
@jwt_required()
def editar_oferta(id):
    claims = get_jwt()
    if not claims.get("admin"):
        return jsonify({"erro": "Acesso negado"}), 403

    dados = request.get_json()
    oferta = Oferta.query.get(id)

    if not oferta:
        return jsonify({"erro": "Oferta não encontrada"}), 404

    oferta.titulo = dados['titulo']
    oferta.descricao = dados['descricao']
    oferta.preco = dados['preco']
    oferta.link = dados['link']
    db.session.commit()

    return jsonify({"mensagem": "Oferta atualizada com sucesso!"}), 200

# ❌ Deletar oferta
@ofertas_bp.route('/deletar/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar_oferta(id):
    claims = get_jwt()
    if not claims.get("admin"):
        return jsonify({"erro": "Acesso negado"}), 403

    oferta = Oferta.query.get(id)

    if not oferta:
        return jsonify({"erro": "Oferta não encontrada"}), 404

    db.session.delete(oferta)
    db.session.commit()

    return jsonify({"mensagem": "Oferta deletada com sucesso!"}), 200

# ❤️ Curtir oferta (PATCH)
@ofertas_bp.route('/<int:id>/like', methods=['PATCH'])
def curtir_oferta(id):
    oferta = Oferta.query.get_or_404(id)
    oferta.likes += 1
    db.session.commit()
    return jsonify({'likes': oferta.likes})

# ❤️ Curtir oferta (POST)
@ofertas_bp.route('/<int:oferta_id>/like', methods=['POST'])
def registrar_like(oferta_id):
    oferta = Oferta.query.get(oferta_id)
    if not oferta:
        return jsonify({'erro': 'Oferta não encontrada'}), 404
    oferta.likes += 1
    db.session.commit()
    return jsonify({'mensagem': 'Oferta curtida com sucesso!', 'likes': oferta.likes})

# 💬 Listar comentários da oferta
@ofertas_bp.route('/<int:oferta_id>/comentarios', methods=['GET'])
def listar_comentarios(oferta_id):
    comentarios = Comentario.query.filter_by(oferta_id=oferta_id).order_by(Comentario.data_criacao.desc()).all()
    resultado = [{
        'id': c.id,
        'texto': c.texto,
        'autor': c.autor.nome,
        'data': c.data_criacao.strftime('%d/%m/%Y %H:%M')
    } for c in comentarios]
    return jsonify(resultado)

# 📝 Comentar oferta com validação
@ofertas_bp.route('/<int:oferta_id>/comentarios', methods=['POST'])
@jwt_required()
def comentar_oferta(oferta_id):
    dados = request.get_json()
    print("🚀 Função comentar_oferta foi chamada")
    print("Dados recebidos:", dados)
    print("Texto:", dados.get("texto"))

    try:
        comentario = ComentarioSchema(**dados)
    except ValidationError as e:
        print("Erro de validação:", e.json())
        return jsonify({"erro": "Validação falhou", "detalhes": e.errors()}), 422

    usuario_id = get_jwt_identity()
    novo = Comentario(
        texto=comentario.texto,
        autor_id=usuario_id,
        oferta_id=oferta_id,
        data_criacao=datetime.utcnow()
    )
    db.session.add(novo)
    db.session.commit()

    return jsonify({
        "mensagem": "Comentário salvo com sucesso!",
        "comentario": {
            "id": novo.id,
            "texto": novo.texto,
            "autor_id": novo.autor_id,
            "oferta_id": novo.oferta_id,
            "data_criacao": novo.data_criacao.strftime('%d/%m/%Y %H:%M')
        }
    }), 201

@ofertas_bp.route('/criar', methods=['POST'])
@jwt_required()
def criar_oferta():
    claims = get_jwt()
    if not claims.get("admin"):
        return jsonify({"erro": "Acesso negado"}), 403

    dados = request.get_json()
    nova_oferta = Oferta(
        titulo=dados['titulo'],
        descricao=dados['descricao'],
        preco=dados['preco'],
        link=dados['link'],
        usuario_id=get_jwt_identity()
    )
    db.session.add(nova_oferta)
    db.session.commit()

    return jsonify({'mensagem': 'Oferta criada com sucesso!'}), 201

@ofertas_bp.route('/favoritar/<int:id_oferta>', methods=["POST"])
@jwt_required()
def favoritar_oferta(id_oferta):
    usuario_id = get_jwt_identity()

    favorito = Favorito(
        usuario_id=usuario_id,
        oferta_id=id_oferta,
        data_favorito=datetime.utcnow()
    )

    db.session.add(favorito)
    db.session.commit()

    return jsonify({'mensagem': 'Oferta favoritada com sucesso!'}), 201

@ofertas_bp.route('/verificar-alertas', methods=['GET'])
@jwt_required()
def verificar_alertas():
    verificar_alerta_categoria()
    return jsonify({'status': 'Alertas verificados'}), 200

@ofertas_bp.route('/categorias-mais-engajadas', methods=['GET'])
@jwt_required()
def categorias_mais_engajadas():
    LIMITE_FAVORITOS = 50

    categorias = [
        {'nome': 'Eletrônicos', 'favoritos': 42},
        {'nome': 'Moda', 'favoritos': 55},
        {'nome': 'Casa', 'favoritos': 30},
        {'nome': 'Beleza', 'favoritos': 61},
        {'nome': 'Esportes', 'favoritos': 61},
    ]

    categorias_ordenadas = sorted(categorias, key=lambda c: c['favoritos'], reverse=True)

    return jsonify(categorias_ordenadas), 200
