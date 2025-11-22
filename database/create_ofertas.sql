CREATE TABLE ofertas (
    id SERIAL PRIMARY KEY,
    titulo TEXT,
    imagem TEXT,
    preco TEXT,
    link_afiliado TEXT,
    loja TEXT,
    categoria TEXT,
    destaque BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
