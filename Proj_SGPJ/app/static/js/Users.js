document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('UserEdit');
    const modalAltura = document.querySelector('.modal-content-user');
    const modalTitle = document.getElementById('modal-title');
    const confirmationMessage = document.getElementById('confirmation-message');
    const form = document.getElementById('form-editar-usuario');
    const btnSalvar = document.getElementById('btn-salvar');
    const btnConfirmar = document.getElementById('btn-confirmar');
    const btnCancelar = document.getElementById('btn-cancelar');
    const closeBtn = document.querySelector('.modal-content-user .close');
    const perfilSelect = document.getElementById('edit-perfil-select');
    const perfilinput = document.getElementById('Perfil-input');

    let currentOperation = '';

    // Função para abrir o modal
    function openModal(title, isEditMode, userData) {
        modal.style.display = 'grid';
        modalTitle.textContent = title;
        perfilinput.style.display = 'none'
        perfilSelect.style.display = 'block'

        if (isEditMode) {
          
            // Preencher o formulário com dados do usuário para edição
            document.getElementById('edit-codigo').value = userData.id || '';
            document.getElementById('edit-nome').value = userData.username || '';
            document.getElementById('edit-senha').value = userData.password_hash || '';
            document.getElementById('edit-setor').value = userData.perfil || '';
            form.style.display = 'block';
            confirmationMessage.style.display = 'none';
            currentOperation = 'edit';
        } else {
            form.style.display = 'none';
            confirmationMessage.style.display = 'block';
            currentOperation = 'delete';
            modalAltura.style.height = '20%'
        }
    }

    // Adiciona evento ao botão Adicionar
    document.getElementById('btn-adicionar-user').addEventListener('click', () => {
        openModal('Adicionar Usuário', true, {});
        currentOperation = 'add';
    });

    // Adiciona evento ao botão Editar
    document.getElementById('btn-editar-user').addEventListener('click', () => {
        const userId = document.querySelector('.product-id').value;

         // Verificar se o ID do usuário foi fornecido
        if (userId) {
            // Obter dados da tabela com base no ID do usuário
            const row = document.querySelector(`tr[data-id="${userId}"]`);
            if (row) {
                const userData = {
                    id: row.getAttribute('data-id'),
                    username: row.getAttribute('data-username'),
                    perfil: row.getAttribute('data-perfil')
                };
                console.log(userData);
                openModal('Editar Usuário', true, userData);
            } else {
                console.error('Usuário não encontrado na tabela.');
            }
        } else {
            alert('Insira o id do usuário que deseja alterar')
            console.error('ID do usuário não fornecido.');
        }
    });

    // Adiciona evento ao botão Excluir
    document.getElementById('btn-Excluir-user').addEventListener('click', () => {
        const userId = document.querySelector('.product-id').value.trim();
            if (userId === '') {
                alert('Insira o código do usuário que deseja excluir');
            } else {
                openModal('Excluir Usuário', false, { id: userId });
            }
    });

    // Confirmar exclusão do usuário
    btnConfirmar.addEventListener('click', async() => {
        const userId = document.querySelector('.product-id').value;
        console.log(userId)

        console.log('Removendo usuário:')
            response = await fetch(`/remove_user/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                
            });
        if (response.ok) {
            console.log('Usuário removido com sucesso');
            window.location.href = '/Controle_Acesso';
        } else {
            console.error('Erro ao removido o usuário');
        }
    });

    btnSalvar.addEventListener('click', async (event) => {
        event.preventDefault();

        const userId = document.getElementById('edit-codigo').value;
        const username = document.getElementById('edit-nome').value;
        const password = document.getElementById('edit-senha').value;
        const perfil = document.getElementById('edit-setor').value;
        const perfilSelect = document.getElementById('edit-perfil-select').value;

        console.log(currentOperation);

        if (currentOperation === 'edit') {
            const userData = {
                username: username,
                password: password,
                perfil: perfil
            };
            console.log('Atualizando usuário:', userData)
                response = await fetch(`/update_user/${userId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(userData),
                    
                });
            if (response.ok) {
                console.log('Usuário atualizado com sucesso');
                window.location.href = '/Controle_Acesso';
            } else {
                console.error('Erro ao atualizar o usuário');
            }
                
        } else if (currentOperation === 'add') {
            console.log(currentOperation);
            const userDataAdd = {
                username: username,
                password: password,
                perfil: perfilSelect
            };
            response = await fetch(`/add_user/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userDataAdd),
                
            });
        if (response.ok) {
            console.log('Usuário criado com sucesso');
            window.location.href = '/Controle_Acesso';
        } else {
            console.error('Erro ao criar o usuário');
        }
        }
        modal.style.display = 'none';
    });


    // Fechar o modal
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    btnCancelar.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Fechar o modal quando clicar fora dele
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
