document.addEventListener('DOMContentLoaded', () => {
    // Selecione o ícone de filtro pelo ID
    const filterIcon = document.getElementById('filterIcon');

    // Adicione um evento de clique ao ícone
    filterIcon.addEventListener('click', () => {
        // Selecione os elementos com as classes .filter e .apply-filter
        const row = document.querySelector('.filter-row');

        // Alterna a classe .hidden para ocultar ou mostrar os elementos
        if (row) {
            row.classList.toggle('hidden');
        }
    });
});
