document.addEventListener('DOMContentLoaded', function () {
    const modalElement = document.getElementById('buscarCNPJModal');
    const modalInstance = new bootstrap.Modal(modalElement);

    // Verifica se o modal já foi aberto antes
    if (!sessionStorage.getItem('modalExibido')) {
        // Abre o modal automaticamente
        modalInstance.show();
        // Marca o modal como exibido
        sessionStorage.setItem('modalExibido', 'true');
    }

    // Adiciona o evento ao formulário de busca
    document.getElementById('buscarCNPJForm').addEventListener('submit', function (event) {
        event.preventDefault(); // Previne o envio padrão do formulário

        const cnpj = document.getElementById('inputCNPJ').value.trim();

        if (!cnpj) {
            alert('Por favor, insira um CNPJ.');
            return;
        }

        // Apenas recarrega a página como se estivesse "filtrando" os processos
        window.location.reload();
    });
});
