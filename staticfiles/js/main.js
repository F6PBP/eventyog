function openModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';  // Show modal (set to flex)
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';  // Hide modal
}

// Close modal when clicking on 'data-dismiss' buttons
document.querySelectorAll('[data-dismiss="modal"]').forEach(button => {
    button.addEventListener('click', function () {
        const modal = this.closest('[role="dialog"]');
        closeModal(modal.id);
    });
});
