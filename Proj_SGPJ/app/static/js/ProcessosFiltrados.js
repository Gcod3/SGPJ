document.querySelector('.btn-apply-filter').addEventListener('click', function() {
    const tipoBusca = document.querySelector('#tipobusca').value;
    const valorFiltro = document.querySelector('#filter-input').value;
    const page = 1;  // Começa com a página 1 ao aplicar um novo filtro
    const perPage = 30;

    if (tipoBusca && valorFiltro) {
        fetchProcessos(tipoBusca, valorFiltro, page);
    }
});

function fetchProcessos(tipoBusca, valorFiltro, page) {
    fetch(`/filtrar-processos`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tipoBusca, valorFiltro, page })
    })
    .then(response => response.json())
    .then(data => {
        updateTable(data.processos);
        updatePagination(data.page, data.total_pages, tipoBusca, valorFiltro);
    })
    .catch(error => console.error('Erro:', error));
}

function updateTable(processos) {
    const tableBody = document.querySelector('.table tbody');
    tableBody.innerHTML = '';  // Limpar a tabela

    if (processos.length > 0) {
        processos.forEach(processo => {
            const row = `
                <tr>
                    <td>${processo.codigo}</td>
                    <td>${processo.classificacoes[0]?.nome || 'Desconhecido'}</td>
                    <td>${processo.partes[1]?.nome || 'Desconhecido'}</td>
                    <td>${processo.status}</td>
                    <td>
                        <div class="dropdown">
                            <button class="btn btn-primary dropdown-toggle" type="button" id="dropdownMenuButton" data-bs-toggle="dropdown" aria-expanded="false">
                                Ações
                            </button>
                            <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                                <li><a class="dropdown-item" href="/detalhes/${processo.codigo}">Detalhes</a></li>
                                <li><a class="dropdown-item" href="#" onclick="showNotification('Monitoramento do processo: ${processo.codigo}')">Monitorar Processo</a></li>
                            </ul>
                        </div>
                    </td>
                </tr>
            `;
            tableBody.insertAdjacentHTML('beforeend', row);
        });
    } else {
        tableBody.innerHTML = '<tr><td colspan="5">Nenhum processo encontrado.</td></tr>';
    }
}

function updatePagination(currentPage, totalPages, tipoBusca, valorFiltro) {
    const paginationDiv = document.querySelector('.pagination');
    paginationDiv.innerHTML = '';  // Limpar a paginação existente

    if (totalPages > 1) {
        if (currentPage > 1) {
            paginationDiv.innerHTML += `<a href="#" data-page="${currentPage - 1}">&laquo; Anterior</a>`;
        }

        for (let i = 1; i <= totalPages; i++) {
            if (i >= currentPage - 4 && i <= currentPage + 4) {
                paginationDiv.innerHTML += `<a href="#" data-page="${i}" class="${i === currentPage ? 'active' : ''}">${i}</a>`;
            }
        }

        if (currentPage < totalPages) {
            paginationDiv.innerHTML += `<a href="#" data-page="${currentPage + 1}">Mais &raquo;</a>`;
        }

        // Adicionar eventos de clique para os links de paginação
        paginationDiv.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                const newPage = parseInt(this.getAttribute('data-page'));
                fetchProcessos(tipoBusca, valorFiltro, newPage);
            });
        });
    }
}
