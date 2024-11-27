document.addEventListener('DOMContentLoaded', () => {

    // Função para carregar os usuários nos selects
    async function listarUsuarios(selectResponsavel) {
        try {
            const response = await fetch(`/get_user`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                const users = data.users;

                console.log('Dados dos usuários:', users); 

                // Limpar o conteúdo do select
                selectResponsavel.innerHTML = '<option value="">Selecione um responsável</option>';

                // Verificar se é um array de usuários
                if (Array.isArray(users)) {
                    // Preencher o select com os usuários
                    users.forEach(user => {
                        const option = document.createElement('option');
                        option.value = user.id; // O valor será o id do usuário
                        option.textContent = user.username; // O texto será o username
                        selectResponsavel.appendChild(option); // Adiciona a opção ao select
                    });
                } else {
                    console.error('Esperado um array de usuários, mas recebeu:', users);
                }
            } else {
                console.error('Erro ao buscar os usuários');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
        }
    }

    // Função para atribuir o valor selecionado ao console
    function atribuirValorSelecionado(selectResponsavel) {
        const selectedValue = selectResponsavel.value;
        const selectedText = selectResponsavel.options[selectResponsavel.selectedIndex].text;

        if (selectedValue) {
            console.log(`Usuário selecionado: ID = ${selectedValue}, Nome = ${selectedText}`);
        } else {
            console.log('Nenhum usuário selecionado.');
        }
    }

    // Identificar os selects de responsável
    const selectsResponsavel = document.querySelectorAll('#responsavelAcao, #responsavelAcaoModal');

    // Carregar os dados de usuários para cada select encontrado
    selectsResponsavel.forEach(select => {
        listarUsuarios(select);
        select.addEventListener('change', () => atribuirValorSelecionado(select));
    });

});
