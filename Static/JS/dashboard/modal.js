/**
 * Modal Handling Module
 * =====================
 * Handles the Add Task modal functionality.
 */

/**
 * Initialize modal handling
 * Sets up event listeners for opening, closing, and submitting the modal
 */
function initModal() {
    // Get references to modal elements
    const modalElement = document.getElementById("taskModal");
    const taskTitleInput = document.getElementById("taskTitleInput");

    /**
     * Open the Add Task modal
     * - Shows the modal using Bootstrap API
     * - Clears any previous input
     */
    $('#openTaskModal').on('click', function () {
        if (modalElement && taskTitleInput) {
            taskTitleInput.value = "";
            // Get or create Bootstrap modal instance
            const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
            modal.show();
        }
    });

    /**
     * Clear input when modal is shown and focus
     */
    if (modalElement) {
        modalElement.addEventListener('shown.bs.modal', function () {
            if (taskTitleInput) {
                taskTitleInput.focus();
            }
        });

        // Clear input when modal is hidden
        modalElement.addEventListener('hidden.bs.modal', function () {
            if (taskTitleInput) {
                taskTitleInput.value = "";
            }
        });
    }

    /**
     * Handle Save Task button click
     * Validates input and creates new task
     */
    $('#saveTaskBtn').on('click', function () {
        const title = taskTitleInput ? taskTitleInput.value.trim() : "";

        if (title) {
            if (window.DashboardTasks) {
                window.DashboardTasks.createTask(title);
            }
            // Close modal using Bootstrap API
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        } else {
            alert('Please enter a task title.');
        }
    });

    /**
     * Handle Enter key in task input field
     * Allows user to press Enter to save task
     */
    $('#taskTitleInput').on('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            $('#saveTaskBtn').click();
        }
    });
}

// Export for use by other modules
window.DashboardModal = { initModal };
