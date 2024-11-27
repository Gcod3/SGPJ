document.addEventListener('DOMContentLoaded', async function () {
    try {
        // Fazendo a requisição para obter os compromissos
        const response = await fetch(`/get_compromissos`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Checando se a resposta foi bem-sucedida
        if (!response.ok) {
            throw new Error('Erro ao buscar compromissos');
        }

        // Processa a resposta
        const data = await response.json();
        console.log("Compromissos recebidos:", data);

        // Obtenha a data atual
        const currentDate = new Date();

        // Recupera compromissos notificados do localStorage
        const notifiedCompromissos = JSON.parse(localStorage.getItem('notifiedCompromissos')) || {};

        // Itera pelos compromissos e verifica se está a 30 ou 15 minutos de distância
        data.compromissos.forEach((compromisso) => {
            // Extrai a data de início do compromisso
            const compromissoInicio = new Date(compromisso.Inicio);

            // Calcula a diferença de tempo entre o compromisso e a hora atual em minutos
            const diffMinutes = Math.floor((compromissoInicio - currentDate) / (1000 * 60)); // Diferença em minutos

            // Verifica se o compromisso já foi notificado para o tempo atual
            if (!notifiedCompromissos[compromisso.id_compromisso]) {
                notifiedCompromissos[compromisso.id_compromisso] = { notified30: false, notified15: false };
            }

            // Verifica se faltam 30 minutos e ainda não foi notificado
            if (diffMinutes < 30 && !notifiedCompromissos[compromisso.id_compromisso].notified30) {
                const message = `Seu compromisso "${compromisso.titulo}" começa em 30 minutos (às ${compromisso.Inicio}).`;
                showNotification(message);
                notifiedCompromissos[compromisso.id_compromisso].notified30 = true; // Marca como notificado

            // Verifica se faltam 15 minutos e ainda não foi notificado
            } if (diffMinutes < 15 && !notifiedCompromissos[compromisso.id_compromisso].notified15) {
                const message = `Seu compromisso "${compromisso.titulo}" começa em 15 minutos (às ${compromisso.Inicio}).`;
                showNotification(message);
                notifiedCompromissos[compromisso.id_compromisso].notified15 = true; // Marca como notificado
            }
        });

        // Salva o status de notificação no localStorage
        localStorage.setItem('notifiedCompromissos', JSON.stringify(notifiedCompromissos));

    } catch (error) {
        console.error('Erro ao buscar compromissos:', error);
    }
});
function showNotification(message) {
    var toastElement = document.getElementById('liveToast');
    var toastBody = toastElement.querySelector('.toast-body');
    toastBody.textContent = message;
    var toast = new bootstrap.Toast(toastElement);
    toast.show();
}
