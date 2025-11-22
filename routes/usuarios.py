import csv
from io import StringIO
from flask import Response
import secrets
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models import Usuario, Favorito, Oferta

# ✅ Defina o blueprint ANTES de usar
usuarios_bp = Blueprint('usuarios', __name__)

# ✅ Agora você pode usar o blueprint normalmente
@usuarios_bp.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    # Exemplo de lógica de cadastro
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'erro': 'Email já cadastrado'}), 400

    novo_usuario = Usuario(email=email, senha=senha)
    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'}), 201

@usuarios_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    usuario = Usuario.query.filter_by(email=dados['email']).first()

    if not usuario or not usuario.verificar_senha(dados['senha']):
        return jsonify({'erro': 'Credenciais inválidas'}), 401

    is_admin = usuario.email == "ofertasdoparceiroorlando@gmail.com"
    token = create_access_token(
        identity=str(usuario.id),
        additional_claims={"admin": is_admin}
    )

    return jsonify({'token': token}), 200


@usuarios_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404

    return jsonify({
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email
    }), 200

@usuarios_bp.route('/favoritos', methods=['GET'])
@jwt_required()
def listar_favoritos():
    usuario_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    favoritos_paginados = Favorito.query.filter_by(usuario_id=usuario_id)\
        .order_by(Favorito.data_favorito.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    resultado = []
    for favorito in favoritos_paginados.items:
        oferta = favorito.oferta
        if not oferta:
            continue

        resultado.append({
            'id': oferta.id,
            'titulo': oferta.titulo,
            'imagem': oferta.imagem,
            'loja': oferta.loja,
            'link_afiliado': oferta.link_afiliado,
            'link': oferta.link,
            'preco': oferta.preco,
            'favorito_id': favorito.id,
            'data_favorito': favorito.data_favorito.strftime('%d/%m/%Y %H:%M:%S')
        })

    return jsonify({
        'pagina': favoritos_paginados.page,
        'total_paginas': favoritos_paginados.pages,
        'total_favoritos': favoritos_paginados.total,
        'favoritos': resultado
    }), 200

@usuarios_bp.route('/favoritos/<int:oferta_id>', methods=['DELETE'])
@jwt_required()
def desfavoritar(oferta_id):
    usuario_id = get_jwt_identity()
    ...
    favorito = Favorito.query.filter_by(usuario_id=usuario_id, oferta_id=oferta_id).first()
    if not favorito:
        return jsonify({'mensagem': 'Favorito não encontrado.'}), 404

    db.session.delete(favorito)

    oferta = Oferta.query.get(oferta_id)
    if oferta and oferta.likes > 0:
        oferta.likes -= 1

    db.session.commit()
    return jsonify({'mensagem': 'Oferta desfavoritada com sucesso!'}), 200

@usuarios_bp.route('/favoritos/<int:oferta_id>', methods=['POST'])
@jwt_required()
def favoritar(oferta_id):
    usuario_id = get_jwt_identity()

    favorito_existente = Favorito.query.filter_by(usuario_id=usuario_id, oferta_id=oferta_id).first()
    if favorito_existente:
        return jsonify({'mensagem': 'Oferta já favoritada.'}), 400

    novo_favorito = Favorito(usuario_id=usuario_id, oferta_id=oferta_id)
    db.session.add(novo_favorito)
    print("Favorito salvo:", novo_favorito)

    oferta = Oferta.query.get(oferta_id)
    if oferta:
        oferta.likes += 1

        comentarios = Comentario.query.filter_by(oferta_id=oferta.id).count()

        # 🔥 Ativar destaque apenas se ainda não estiver ativo
        if oferta.likes >= 10 and comentarios >= 5 and not oferta.destaque:
            oferta.destaque = True

    db.session.commit()
    return jsonify({'mensagem': 'Oferta favoritada com sucesso!'}), 201

@usuarios_bp.route('/favoritos/<int:oferta_id>/existe', methods=['GET'])
@jwt_required()
def verificar_favorito(oferta_id):
    usuario_id = get_jwt_identity()
    favorito = Favorito.query.filter_by(usuario_id=usuario_id, oferta_id=oferta_id).first()
    return jsonify({'favoritado': bool(favorito)}), 200

@usuarios_bp.route('/estatisticas', methods=['GET'])
@jwt_required()
def estatisticas():
    total_usuarios = Usuario.query.count()
    total_ofertas = Oferta.query.count()
    total_favoritos = Favorito.query.count()

    ofertas_destaque = Oferta.query.filter_by(destaque=True).all()
    ofertas_mais_curtidas = Oferta.query.order_by(Oferta.likes.desc()).limit(5).all()

    destaque_serializado = [{
        'id': o.id,
        'titulo': o.titulo,
        'likes': o.likes,
        'destaque': o.destaque
    } for o in ofertas_destaque]

    mais_curtidas_serializado = [{
        'id': o.id,
        'titulo': o.titulo,
        'likes': o.likes
    } for o in ofertas_mais_curtidas]

    return jsonify({
        'total_usuarios': total_usuarios,
        'total_ofertas': total_ofertas,
        'total_favoritos': total_favoritos,
        'ofertas_destaque': destaque_serializado,
        'ofertas_mais_curtidas': mais_curtidas_serializado
    }), 200
@usuarios_bp.route('/meus-favoritos', methods=['GET'])
@jwt_required()
def meus_favoritos():
    usuario_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    favoritos_paginados = Favorito.query.filter_by(usuario_id=usuario_id)\
        .order_by(Favorito.data_favorito.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    resultado = []
    for favorito in favoritos_paginados.items:
        oferta = favorito.oferta
        if not oferta:
            continue
        resultado.append({
            'id': oferta.id,
            'titulo': oferta.titulo,
            'imagem': oferta.imagem,
            'loja': oferta.loja,
            'link_afiliado': oferta.link_afiliado,
            'link': oferta.link,
            'preco': oferta.preco,
            'favorito_id': favorito.id,
            'data_favorito': favorito.data_favorito.strftime('%d/%m/%Y %H:%M:%S')
        })

    return jsonify({
        'pagina': favoritos_paginados.page,
        'total_paginas': favoritos_paginados.pages,
        'total_favoritos': favoritos_paginados.total,
        'favoritos': resultado
    }), 200
@usuarios_bp.route('/ofertas-filtradas', methods=['GET'])
@jwt_required()
def ofertas_filtradas():
    loja = request.args.get('loja')
    categoria_id = request.args.get('categoria_id', type=int)
    data_min = request.args.get('data_min')
    data_max = request.args.get('data_max')

    query = Oferta.query

    if loja:
        query = query.filter(Oferta.loja.ilike(f'%{loja}%'))
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    if data_min:
        query = query.filter(Oferta.data_criacao >= data_min)
    if data_max:
        query = query.filter(Oferta.data_criacao <= data_max)

    ofertas = query.order_by(Oferta.likes.desc()).limit(20).all()

    resultado = [{
        'id': o.id,
        'titulo': o.titulo,
        'loja': o.loja,
        'likes': o.likes,
        'destaque': o.destaque
    } for o in ofertas]

    return jsonify({'ofertas_filtradas': resultado}), 200
@usuarios_bp.route('/top-usuarios', methods=['GET'])
@jwt_required()
def top_usuarios():
    favoritos_por_usuario = db.session.query(
        Favorito.usuario_id,
        db.func.count(Favorito.id).label('total_favoritos')
    ).group_by(Favorito.usuario_id)\
     .order_by(db.desc('total_favoritos'))\
     .limit(5).all()

    resultado = []
    for usuario_id, total in favoritos_por_usuario:
        usuario = Usuario.query.get(usuario_id)
        if usuario:
            resultado.append({
                'usuario_id': usuario_id,
                'nome': usuario.nome,
                'total_favoritos': total
            })

    return jsonify({'top_usuarios': resultado}), 200
@usuarios_bp.route('/relatorio-favoritos', methods=['GET'])
@jwt_required()
def relatorio_favoritos():
    data_inicio = request.args.get('inicio')
    data_fim = request.args.get('fim')

    if not data_inicio or not data_fim:
        return jsonify({'erro': 'Informe as datas inicio e fim no formato YYYY-MM-DD'}), 400

    favoritos = Favorito.query.filter(
        Favorito.data_favorito >= data_inicio,
        Favorito.data_favorito <= data_fim
    ).order_by(Favorito.data_favorito.desc()).all()

    resultado = []
    for fav in favoritos:
        oferta = fav.oferta
        if not oferta:
            continue
        resultado.append({
            'favorito_id': fav.id,
            'data_favorito': fav.data_favorito.strftime('%d/%m/%Y %H:%M:%S'),
            'usuario_id': fav.usuario_id,
            'oferta_id': oferta.id,
            'titulo': oferta.titulo,
            'loja': oferta.loja,
            'likes': oferta.likes
        })

    return jsonify({
        'total_favoritos': len(resultado),
        'periodo': {
            'inicio': data_inicio,
            'fim': data_fim
        },
        'favoritos': resultado
    }), 200
@usuarios_bp.route('/exportar-categorias', methods=['GET'])
@jwt_required()
def exportar_categorias():
    # Dados fictícios — substitua por consulta real ao banco
    dados = [
        {'categoria': 'Eletrônicos', 'favoritos': 42, 'comentarios': 18},
        {'categoria': 'Moda', 'favoritos': 28, 'comentarios': 12},
        {'categoria': 'Casa', 'favoritos': 19, 'comentarios': 9},
        {'categoria': 'Beleza', 'favoritos': 24, 'comentarios': 15},
        {'categoria': 'Esportes', 'favoritos': 31, 'comentarios': 20},
    ]

    # Gerar CSV em memória
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Categoria', 'Favoritos', 'Comentários'])
    for linha in dados:
        writer.writerow([linha['categoria'], linha['favoritos'], linha['comentarios']])

    # Retornar como resposta HTTP
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename='categorias.csv')
    return response
@usuarios_bp.route('/verificar-alertas', methods=['GET'])
@jwt_required()
def verificar_alertas():
    verificar_alerta_categoria()
    return jsonify({'status': 'Alertas verificados'}), 200
