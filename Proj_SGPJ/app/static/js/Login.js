document.addEventListener('DOMContentLoaded', () => {
    const btnEntrar = document.querySelector('.btn-entrar');

    console.log(btnEntrar);

    btnEntrar.addEventListener('click', async (event) => {
        event.preventDefault();

        const username = document.getElementById('input-username').value;
        const password = document.getElementById('input-password').value;

        const userData = {
            username: username,
            password: password
        };
        console.log('Login do usuário:', userData)
            response = await fetch(`/Entrar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
                
            });
        if (response.ok) {
            console.log('Login realizado com sucesso');
            window.location.href = '/todosprocessos';
        } else {
            console.error('Erro ao realizar login');
            alert('Dados incorretos')
        }


    });



});