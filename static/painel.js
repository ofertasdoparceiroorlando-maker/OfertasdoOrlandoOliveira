console.log('painel.js está executando');

// Função para carregar os dados usando o token
function carregarDados(token) {
  fetch("http://localhost:5000/ofertas/categorias-mais-engajadas", {
    headers: { Authorization: `Bearer ${token}` }
  })
  .then(res => res.json())
  .then(data => {
    if (!Array.isArray(data)) throw new Error("Resposta da API não é um array");

    const container = document.getElementById('alertas');
    const inputFiltro = document.getElementById('filtroCategoria');
    const botaoLimpar = document.getElementById('limparFiltro');
    const ctx = document.getElementById('graficoCategorias').getContext('2d');

    const totalFavoritos = data.reduce((acc, cat) => acc + cat.favoritos, 0);
    const maxFavoritos = Math.max(...data.map(cat => cat.favoritos));
    const ordenados = data.sort((a, b) => b.favoritos - a.favoritos);

    const icones = {
      Beleza: "💄",
      Esportes: "🏀",
      Moda: "👗",
      Eletrônicos: "📱",
      Casa: "🏠"
    };

    let grafico;

    function atualizarGrafico(dados) {
      if (grafico) grafico.destroy();
      grafico = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: dados.map(cat => cat.nome),
          datasets: [{
            label: 'Favoritos',
            data: dados.map(cat => cat.favoritos),
            backgroundColor: '#ffc107'
          }]
        }
      });
    }

    function renderCards(filtrados) {
      container.innerHTML = '';
      filtrados.forEach(cat => {
        const porcentagem = ((cat.favoritos / totalFavoritos) * 100).toFixed(1);
        const card = document.createElement('div');
        card.classList.add('alert-card');
        if (cat.favoritos === maxFavoritos) {
          card.classList.add('top');
        }
        card.innerHTML = `
          <span>${icones[cat.nome] || "🔥"} ${cat.nome}</span>
          <span>${cat.favoritos} favoritos (${porcentagem}%)</span>
        `;
        container.appendChild(card);
      });
    }

    // Render inicial
    renderCards(ordenados);
    atualizarGrafico(ordenados);

    // Filtro dinâmico
    inputFiltro.addEventListener('input', () => {
      const termo = inputFiltro.value.toLowerCase();
      const filtrados = ordenados.filter(cat =>
        cat.nome.toLowerCase().includes(termo)
      );
      renderCards(filtrados);
      atualizarGrafico(filtrados);
    });

    // Botão limpar
    botaoLimpar.addEventListener('click', () => {
      inputFiltro.value = '';
      renderCards(ordenados);
      atualizarGrafico(ordenados);
    });

    // Exportar CSV
    document.getElementById('exportarCSV').addEventListener('click', () => {
      const linhas = data.map(item => `${item.nome},${item.favoritos}`);
      const csv = 'Categoria,Favoritos\n' + linhas.join('\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'categorias.csv';
      link.click();
    });
  })
  .catch(err => {
    console.error("Erro ao carregar dados:", err);
  });
}

// Se já existe token salvo, usa ele
if (localStorage.getItem('token')) {
  const token = localStorage.getItem('token');
  carregarDados(token);
} else {
  // Faz login e salva token
  fetch("http://localhost:5000/usuarios/login", {
    method: 'POST',
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: 'ofertasdoparceiroorlando@gmail.com',
      senha: 'residencial7068.'
    })
  })
  .then(res => res.json())
  .then(auth => {
    const token = auth.token;
    localStorage.setItem('token', token); // 🔐 salva o token
    carregarDados(token);
  })
  .catch(err => {
    console.error("Erro no login:", err);
  });
}

// Modo escuro
document.addEventListener('DOMContentLoaded', () => {
  const botaoDark = document.getElementById('toggleDark');
  if (botaoDark) {
    botaoDark.addEventListener('click', () => {
      console.log("Botão modo escuro clicado");
      document.body.classList.toggle('dark-mode');
    });
  } else {
    console.warn("Botão toggleDark não encontrado no DOM");
  }
});
