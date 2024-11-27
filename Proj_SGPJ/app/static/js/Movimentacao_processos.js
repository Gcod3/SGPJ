document.querySelectorAll('.abrirModal').forEach(function(element) {
    element.addEventListener('click', function () {
        // Exibe o modal
        const modal = new bootstrap.Modal(document.getElementById('acaoModal'));
        modal.show();

        // Obtém o ID do processo a partir do atributo 'data-processo-id'
        const processoId = this.getAttribute('data-processo-id');
        console.log(processoId);  // Verifique se o ID está correto

        // Carregar os responsáveis já atribuídos ao abrir o modal
        carregarResponsaveis(processoId);

        // Fechar o modal programaticamente (se necessário)
        var modalEl = document.getElementById('acaoModal');
        modalEl.addEventListener('hidden.bs.modal', function () {
            console.log("Modal fechado");

            // Remove a classe "show" e garante que o modal não esteja visível
            modalEl.classList.remove('show');
            modalEl.style.display = 'none';

            // Remove a classe 'modal-open' do body
            document.body.classList.remove('modal-open');
            
            // Remove o backdrop (fundo escuro)
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
        });

        // Armazene o processoId para ser usado mais tarde ao adicionar o responsável
        window.processIdGlobal = processoId; // Armazena o id do processo globalmente
    });
});

// Função para carregar os responsáveis e preencher a tabela
function carregarResponsaveis(processoId) {
    fetch(`/responsaveis_processo/${processoId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Erro ao carregar responsáveis.");
            }
            return response.json();
        })
        .then(resposta => {
            // Acessa o array de responsáveis dentro da chave 'responsaveis'
            const responsaveis = resposta.responsaveis;
            console.log(responsaveis);  // Exibe o formato real da resposta

            const tabela = document.getElementById('usuariosAtribuidos').querySelector('tbody');
            tabela.innerHTML = ''; // Limpa a tabela antes de preencher

            if (Array.isArray(responsaveis)) {  // Verifica se responsaveis é realmente um array
                responsaveis.forEach(resp => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${resp.nome}</td>
                        <td>
                            <button class="btn btn-danger btn-sm" onclick="removerResponsavel(${resp.id}, '${processoId}')">Remover</button>
                        </td>
                    `;
                    tabela.appendChild(row);
                });
            } else {
                console.error("A resposta não contém um array de responsáveis:", responsaveis);
            }
        })
        .catch(error => {
            console.error("Erro ao carregar responsáveis:", error);
        });
}

// Evento para adicionar responsável ao processo
document.getElementById('adicionarResponsavel').addEventListener('click', function () {
    const selectResponsavel = document.getElementById('responsavelAcao');
    const responsavelId = selectResponsavel.value; // Valor selecionado no dropdown
    const processoId = window.processIdGlobal; // Recupera o id do processo global

    console.log({ responsavelId, processoId }); // Verifique os valores

    if (responsavelId && processoId) {
        fetch(`/adicionar_responsavel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                id_processo: processoId, 
                id_responsavel: responsavelId 
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    console.error("Erro ao adicionar responsável:", errorData);
                    throw new Error(errorData.error || "Erro ao adicionar responsável.");
                });
            }
            return response.json();
        })
        .then(data => {
            console.log(data.message || "Responsável adicionado com sucesso!");
            carregarResponsaveis(processoId); // Atualiza a tabela de responsáveis
        })
        .catch(error => {
            console.error("Erro ao adicionar responsável:", error);
        });
    } else {
        alert("Por favor, selecione um responsável e um processo.");
    }
});

// Função para remover responsável do processo
function removerResponsavel(responsavelId, processoId) {
    console.log(`Tentando remover responsável com ID: ${responsavelId}`);
    event.preventDefault(); // Adicione isto

    if (confirm("Tem certeza de que deseja remover este responsável?")) {
        // Envia a requisição DELETE para o backend
        fetch(`/remover_responsavel/${responsavelId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id_processo: processoId }) // Passa o processo_id para a remoção
        })
        .then(response => {
            if (!response.ok) {
                console.error("Erro ao remover responsável. Status: ", response.status);
                throw new Error("Erro ao remover responsável.");
            }
            return response.json();
        })
        .then(data => {
            console.log("Responsável removido com sucesso:", data);

            // Atualiza a tabela de responsáveis sem fechar o modal
            carregarResponsaveis(processoId);
        })
        .catch(error => {
            console.error("Erro ao remover responsável:", error);
        });
    }
}
