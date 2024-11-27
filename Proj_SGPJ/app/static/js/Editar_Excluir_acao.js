let linhaSelecionada; // Variável para armazenar a linha selecionada

function abrirModal(linha) {
    // Armazena a linha selecionada
    linhaSelecionada = linha;

    // Captura os dados da linha e preenche os campos do modal
    document.getElementById("tipoInput").value = linha.cells[0].innerText;

    // Preencher o select de responsável
    const responsavel = linha.cells[1].innerText;
    const selectResponsavel = document.getElementById("responsavelAcaoModal");
    const optionsResponsavel = selectResponsavel.getElementsByTagName("option");

    // Encontrar o option correspondente ao responsável
    for (let option of optionsResponsavel) {
        if (option.textContent === responsavel) {
            selectResponsavel.value = option.value;
            break;
        }
    }

    // Preencher o campo de data
    document.getElementById("dataInput").value = linha.cells[2].innerText;
    document.getElementById("comentarioInput").value = linha.cells[3].innerText;

    // Preencher o select de status
    const status = linha.cells[4].innerText;
    const selectStatus = document.getElementById("statusAcaoModal");
    selectStatus.value = status; // Já que o value é o texto do status

    // Obter o ID da ação associada (armazenado na linha como atributo data-acao-id)
    const acaoId = linha.getAttribute('data-acao-id');

    // Limpar a lista de anexos existente
    const anexosLista = document.getElementById("anexosLista");
    anexosLista.innerHTML = '';

    // Fazer uma requisição para buscar os documentos associados
    fetch(`/documentos/${acaoId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Erro ao carregar anexos.");
            }
            return response.json();
        })
        .then(documentos => {
            // Preencher a lista com os anexos
            documentos.forEach(doc => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.id = `anexo-${doc.id}`;  // Adiciona o id do anexo para facilitar a exclusão
            
                // Adiciona o nome do arquivo, link para download e o botão de exclusão
                li.innerHTML = `
                    ${doc.nome_arq} 
                    <a href="/download/${doc.id}" class="btn btn-link btn-sm">Baixar</a>
                    <button class="btn btn-danger btn-sm" onclick="excluirAnexo(${doc.id})">Excluir</button>
                `;
            
                anexosLista.appendChild(li);
            });
        })
        .catch(error => {
            console.error("Erro ao carregar anexos:", error);
            const li = document.createElement('li');
            li.className = 'list-group-item text-danger';
            li.textContent = "Erro ao carregar anexos.";
            anexosLista.appendChild(li);
        });

    // Abre o modal
    new bootstrap.Modal(document.getElementById('editModal')).show();
}


function salvarEdicao() {
    // Obter o valor do ID do responsável
    const responsavelId = document.getElementById("responsavelAcaoModal").value;
    // Obter o nome do responsável
    const responsavelNome = document.querySelector(`#responsavelAcaoModal option[value="${responsavelId}"]`).textContent;

    const tipo = document.getElementById("tipoInput").value;
    const data = document.getElementById("dataInput").value;
    const comentario = document.getElementById("comentarioInput").value;
    const status = document.getElementById("statusAcaoModal").value;

    if (!tipo || !responsavelId || !data || !comentario || !status) {
        alert("Por favor, preencha todos os campos.");
        return;
    }

    // Envia os dados para o backend
    const formData = new FormData();
    formData.append("tipo", tipo);
    formData.append("responsavel", responsavelId);  // Envia o ID do responsável
    formData.append("data", data);
    formData.append("comentario", comentario);
    formData.append("status", status);

    fetch(`/alterar_acao/${linhaSelecionada.getAttribute('data-acao-id')}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recarrega a página para garantir que os dados corretos sejam exibidos
            location.reload();
        } else {
            alert('Erro ao salvar a edição: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro ao salvar a edição:', error);
    });

    // Fecha o modal
    bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
}



function excluirLinha() {

     // Confirma a exclusão
    if (!confirm("Tem certeza que deseja excluir esta ação?")) {
        return;
    }

    // Obtém o ID da ação
    const acaoId = linhaSelecionada.getAttribute('data-acao-id');
    
    if (!acaoId) {
        alert("ID da ação não encontrado!");
        return;
    }

    // Faz a chamada para o backend
    fetch(`/excluir_acao/${acaoId}`, {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            alert("Ação excluída com sucesso!");
            // Remove a linha selecionada
            linhaSelecionada.remove();
        } else {
            return response.json().then(data => {
                alert(data.message || "Erro ao excluir a ação.");
            });
        }
    })
    .catch(error => {
        console.error("Erro ao excluir a ação:", error);
        alert("Erro ao excluir a ação. Consulte o console para mais detalhes.");
    })
    .finally(() => {
        // Fecha o modal mesmo em caso de erro
        bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
    });

    // Remove a linha selecionada
    linhaSelecionada.remove();

    // Fecha o modal
    bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
}

function excluirAnexo(anexoId) {
    // Confirmar se o usuário realmente quer excluir
    if (confirm('Tem certeza que deseja excluir este anexo?')) {
        fetch(`/excluir_anexo/${anexoId}`, {
            method: 'DELETE',  // Usar DELETE para exclusão
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Se a exclusão for bem-sucedida, removemos o anexo da lista no frontend
                const anexoElement = document.getElementById(`anexo-${anexoId}`);
                if (anexoElement) {
                    anexoElement.remove();
                }
                alert('Anexo excluído com sucesso!');
            } else {
                alert('Erro ao excluir o anexo: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erro ao excluir o anexo:', error);
            alert('Houve um erro ao tentar excluir o anexo.');
        });
    }
}
