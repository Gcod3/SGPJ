document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('toggleButton');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    toggleButton.addEventListener('click', function () {
        sidebar.classList.toggle('collapsed');

        // Ajusta o margin-left do conteúdo principal com base no estado do sidebar
        if (sidebar.classList.contains('collapsed')) {
            mainContent.style.marginLeft = '10px'; // Mantém espaço para o botão e ícones
            mainContent.style.transform = 'translateX(50px)'; 
        } else {
            mainContent.style.transform = 'translateX(100px)'; // Espaço padrão quando o sidebar está expandido
            mainContent.style.transition = '0.3s';
        }
    });
});

// Função para exibir notificações
function showNotification(message) {
    const toastEl = document.getElementById('liveToast');
    const toastBody = toastEl.querySelector('.toast-body');
    toastBody.textContent = message;
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// Exemplo de uso ao clicar em um link de monitoramento
document.querySelectorAll('.dropdown-item').forEach(link => {
    link.addEventListener('click', function(event) {
        if (event.target.textContent.includes('Monitorar Processo')) {
            event.preventDefault();
            showNotification('Monitoramento do processo iniciado.');
        }
    });
});
