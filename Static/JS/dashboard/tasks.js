/**
 * Task Management Module
 * ======================
 * Handles task CRUD operations and DOM updates.
 */

/**
 * Fetch all tasks from the server
 * Called on page load to populate the task list
 */
function fetchTasks() {
    fetch('/api/tasks')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Clear existing tasks in the DOM
                $('#tasksContainer').empty();

                if (data.tasks && data.tasks.length > 0) {
                    // Add each task to the DOM
                    data.tasks.forEach(task => {
                        addTaskToDOM(task);
                    });
                    // Hide the "no tasks" message
                    $('.empty-state').hide();
                } else {
                    // Show the "no tasks" message
                    $('.empty-state').show();
                }

                // Update the progress bar
                if (window.DashboardProgress) {
                    window.DashboardProgress.updateProgress();
                }
            }
        })
        .catch(error => {
            console.error('Error fetching tasks:', error);
        });
}

/**
 * Add a task to the DOM
 * Creates the HTML structure for a task card
 * 
 * @param {Object} task - Task object with _id, title, done properties
 */
function addTaskToDOM(task) {
    const taskId = task._id;

    // Build the task card HTML
    // - Checkbox for marking complete
    // - Label showing task title
    // - Delete button
    const taskHtml = `
        <div class="card mb-2 task-item ${task.done ? 'task-completed' : ''}" id="task-${taskId}">
            <div class="card-body py-2">
                <div class="form-check d-flex align-items-center">
                    <input class="form-check-input task-checkbox me-3" 
                           type="checkbox" 
                           id="check-${taskId}" 
                           ${task.done ? 'checked' : ''}>
                    <label class="form-check-label flex-grow-1" for="check-${taskId}">
                        ${task.title}
                    </label>
                    <button type="button" 
                            class="btn btn-outline-danger btn-sm delete-task" 
                            data-task-id="${taskId}"
                            title="Delete task">
                        ✕
                    </button>
                </div>
            </div>
        </div>
    `;

    // Append to the tasks container
    $('#tasksContainer').append(taskHtml);

    // Attach event listeners to the new task elements
    // Using specific selectors to avoid duplicate handlers
    $(`#check-${taskId}`).on('change', function () {
        toggleTask(taskId);
    });

    $(`.delete-task[data-task-id="${taskId}"]`).on('click', function () {
        deleteTask(taskId);
    });
}

/**
 * Create a new task via API
 * Sends POST request to create task in database
 * 
 * @param {string} title - The task title
 */
function createTask(title) {
    const csrfToken = window.DashboardCSRF ? window.DashboardCSRF.getCsrfToken() : '';

    fetch('/api/tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  // CSRF protection
        },
        body: JSON.stringify({ title: title })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add the new task to the DOM
                addTaskToDOM({
                    _id: data.task_id,
                    title: data.title,
                    done: data.done
                });

                // Hide empty state message
                $('.empty-state').hide();

                // Update progress bar
                if (window.DashboardProgress) {
                    window.DashboardProgress.updateProgress();
                }
            } else {
                alert('Error adding task: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error adding task:', error);
            alert('Error adding task. Please try again.');
        });
}

/**
 * Delete a task via API
 * Removes task from database and DOM
 * 
 * @param {string} taskId - The MongoDB ObjectId of the task
 */
function deleteTask(taskId) {
    const csrfToken = window.DashboardCSRF ? window.DashboardCSRF.getCsrfToken() : '';

    fetch(`/api/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrfToken  // CSRF protection
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove task from DOM with animation
                $(`#task-${taskId}`).fadeOut(300, function () {
                    $(this).remove();

                    // Update progress bar
                    if (window.DashboardProgress) {
                        window.DashboardProgress.updateProgress();
                    }

                    // Show empty state if no tasks left
                    if ($('.task-item').length === 0) {
                        $('.empty-state').show();
                    }
                });

                // Refresh notifications in case task had related notifications
                if (window.DashboardNotifications) {
                    window.DashboardNotifications.fetchAndRenderNotifications();
                }
            } else {
                alert('Error deleting task: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error deleting task:', error);
        });
}

/**
 * Toggle task completion status via API
 * This is the ONLY place where streak is updated for tasks
 * The backend handles the streak increment to avoid double-counting
 * 
 * @param {string} taskId - The MongoDB ObjectId of the task
 */
function toggleTask(taskId) {
    const csrfToken = window.DashboardCSRF ? window.DashboardCSRF.getCsrfToken() : '';

    fetch(`/api/tasks/${taskId}/toggle`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  // CSRF protection
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update checkbox state
                $(`#check-${taskId}`).prop('checked', data.done);

                // Update task card styling (completed tasks have different background)
                if (data.done) {
                    $(`#task-${taskId}`).addClass('task-completed');
                } else {
                    $(`#task-${taskId}`).removeClass('task-completed');
                }

                // Update streak display from server response
                // The server calculates the correct streak value
                if (data.streak !== undefined) {
                    $('.streak-days').text(data.streak + ' days');
                    $('.stats-streak').text(data.streak + ' days');
                }

                // Update progress bar
                if (window.DashboardProgress) {
                    window.DashboardProgress.updateProgress();
                }

                // Refresh notifications
                if (window.DashboardNotifications) {
                    window.DashboardNotifications.fetchAndRenderNotifications();
                }

                // Check if user earned any new rewards
                if (window.DashboardRewards) {
                    window.DashboardRewards.checkAndShowRewards();
                }
            } else {
                alert('Error updating task: ' + data.error);
                // Revert checkbox state on error
                $(`#check-${taskId}`).prop('checked', !$(`#check-${taskId}`).prop('checked'));
            }
        })
        .catch(error => {
            console.error('Error updating task:', error);
        });
}

// Export for use by other modules
window.DashboardTasks = {
    fetchTasks,
    addTaskToDOM,
    createTask,
    deleteTask,
    toggleTask
};
