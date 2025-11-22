from flask import Flask, request, jsonify
from amazon_paapi import AmazonApi
from dotenv import load_dotenv
import os

from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

print("ACCESS_KEY:", os.getenv("ACCESS_KEY"))
print("SECRET_KEY:", os.getenv("SECRET_KEY"))
print("PARTNER_TAG:", os.getenv("PARTNER_TAG"))

app = Flask(__name__)

amazon = AmazonApi(
    key=os.getenv("ACCESS_KEY"),
    secret=os.getenv("SECRET_KEY"),
    tag=os.getenv("PARTNER_TAG"),
    country="BR"
)

@app.route('/produto', methods=['GET'])
def produto():
    asin = request.args.get('asin')
    if not asin:
        return jsonify({'erro': 'ASIN não fornecido'}), 400

    result = amazon.get_items([asin])
    if not result.items:
        return jsonify({'erro': 'Produto não encontrado'}), 404

    item = result.items[0]
    return jsonify({
        'titulo': item.title,
        'imagem': item.image_url,
        'preco': item.list_price,
        'link': item.detail_page_url
    })

if __name__ == '__main__':
    app.run(debug=True)
