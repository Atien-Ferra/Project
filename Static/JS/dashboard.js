$(document).ready(function() {
    // Fetch and initialize tasks from the API
    fetchTasks();

    // Initialize progress
    updateProgress();

    // File upload handling - submit form on file selection
    $('#fileUpload').on('change', function() {
        const file = this.files[0];
        if (file) {
            // Check file type
            const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                                 'text/plain', 'image/png', 'image/jpeg', 'image/gif'];
            if (!allowedTypes.includes(file.type)) {
                alert('Invalid file type. Please upload PDF, DOCX, TXT, or image files.');
                return;
            }
            
            // Submit the form
            $('#uploadForm').submit();
        }
    });

    // Modal handling
    const modal = document.getElementById("taskModal");
    const backdrop = document.getElementById("taskModalBackdrop");
    const taskTitleInput = document.getElementById("taskTitleInput");

    // Hide modal on page load
    if (modal) modal.style.display = "none";
    if (backdrop) backdrop.style.display = "none";

    function openModal() {
        modal.style.display = "flex";
        backdrop.style.display = "block";
        taskTitleInput.value = "";
        taskTitleInput.focus();
    }

    function closeModal() {
        modal.style.display = "none";
        backdrop.style.display = "none";
        taskTitleInput.value = "";
    }

    // Open modal button
    $('#openTaskModal').text('Add a Task');
    $('#openTaskModal').on('click', openModal);

    // Close modal buttons
    $('#closeTaskModal').on('click', closeModal);
    $('#cancelTaskModal').on('click', closeModal);
    $(backdrop).on('click', closeModal);

    // Save task button
    $('#saveTaskBtn').on('click', function() {
        const title = taskTitleInput.value.trim();
        if (title) {
            createTask(title);
            closeModal();
        } else {
            alert('Please enter a task title.');
        }
    });

    // Escape key to close modal
    $(document).on('keydown', function(e) {
        if (e.key === "Escape") closeModal();
    });

    // Fetch all tasks from the API
    function fetchTasks() {
        fetch('/api/tasks')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    $('#tasksContainer').empty();
                    if (data.tasks && data.tasks.length > 0) {
                        data.tasks.forEach(task => {
                            addTaskToDOM(task);
                        });
                        $('.empty-state').hide();
                    } else {
                        $('.empty-state').show();
                    }
                    updateProgress();
                }
            })
            .catch(error => console.error('Error fetching tasks:', error));
    }

    // Add a task to the DOM with event listeners
    function addTaskToDOM(task) {
        const taskId = task._id;
        const taskHtml = `
            <div class="card mb-2 task-item" id="task-${taskId}">
                <div class="card-body py-2">
                    <div class="form-check">
                        <input class="form-check-input task-checkbox" type="checkbox" id="check-${taskId}" ${task.done ? 'checked' : ''}>
                        <label class="form-check-label" for="check-${taskId}">${task.title}</label>
                        <button type="button" class="btn-close float-end delete-task" data-task-id="${taskId}"></button>
                    </div>
                </div>
            </div>
        `;
        $('#tasksContainer').append(taskHtml);
        
        // Add event listeners
        $(`#check-${taskId}`).on('change', function() {
            toggleTask(taskId);
            updateProgress();
        });
        $(`.delete-task[data-task-id="${taskId}"]`).on('click', function() {
            deleteTask(taskId);
        });
    }

    // Create a new task via API
    function createTask(title) {
        const csrfToken = document.getElementById('csrfToken').value;
        fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ title: title })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addTaskToDOM({
                    _id: data.task_id,
                    title: data.title,
                    done: data.done
                });
                $('.empty-state').hide();
                updateProgress();
            } else {
                alert('Error adding task: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error adding task:', error);
            alert('Error adding task. Please try again.');
        });
    }

    // Delete a task via API
    function deleteTask(taskId) {
        const csrfToken = document.getElementById('csrfToken').value;
        fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $(`#task-${taskId}`).remove();
                updateProgress();
                if ($('.task-item').length === 0) {
                    $('.empty-state').show();
                }
            } else {
                alert('Error deleting task: ' + data.error);
            }
        })
        .catch(error => console.error('Error deleting task:', error));
    }

    // Toggle task completion via API
    function toggleTask(taskId) {
        const csrfToken = document.getElementById('csrfToken').value;
        fetch(`/api/tasks/${taskId}/toggle`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $(`#check-${taskId}`).prop('checked', data.done);
            } else {
                alert('Error updating task: ' + data.error);
            }
        })
        .catch(error => console.error('Error updating task:', error));
    }

    // Create a new task via API
    function createTask(title) {
        const csrfToken = document.getElementById('csrfToken').value;
        fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ title: title })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addTaskToDOM({
                    _id: data.task_id,
                    title: data.title,
                    done: data.done
                });
                $('.empty-state').hide();
                updateProgress();
            } else {
                alert('Error adding task: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error adding task:', error);
            alert('Error adding task. Please try again.');
        });
    }

    // Delete a task via API
    function deleteTask(taskId) {
        const csrfToken = document.getElementById('csrfToken').value;
        fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $(`#task-${taskId}`).remove();
                updateProgress();
                if ($('.task-item').length === 0) {
                    $('.empty-state').show();
                }
            } else {
                alert('Error deleting task: ' + data.error);
            }
        })
        .catch(error => console.error('Error deleting task:', error));
    }

    // Toggle task completion via API
    function toggleTask(taskId) {
        const csrfToken = document.getElementById('csrfToken').value;
        fetch(`/api/tasks/${taskId}/toggle`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $(`#check-${taskId}`).prop('checked', data.done);
            } else {
                alert('Error updating task: ' + data.error);
            }
        })
        .catch(error => console.error('Error updating task:', error));
    }

    // Create a new task via API
    function createTask(title) {
        const csrfToken = document.getElementById('csrfToken').value;
        fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ title: title })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addTaskToDOM({
                    _id: data.task_id,
                    title: data.title,
                    done: data.done
                });
                $('.empty-state').hide();
                updateProgress();
    
                // NEW: refresh notifications
                fetchAndRenderNotifications();
            } else {
                alert('Error adding task: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error adding task:', error);
            alert('Error adding task. Please try again.');
        });
    }

    // Delete a task via API
    function deleteTask(taskId) {
        const csrfToken = document.getElementById('csrfToken').value;
        fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $(`#task-${taskId}`).remove();
                updateProgress();
                if ($('.task-item').length === 0) {
                    $('.empty-state').show();
                }
    
                // NEW: refresh notifications
                fetchAndRenderNotifications();
            } else {
                alert('Error deleting task: ' + data.error);
            }
        })
        .catch(error => console.error('Error deleting task:', error));
    }

    // Toggle task completion via API
   function toggleTask(taskId) {
    const csrfToken = document.getElementById('csrfToken').value;
    fetch(`/api/tasks/${taskId}/toggle`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            $(`#check-${taskId}`).prop('checked', data.done);
            if ($('.task-checkbox:checked').length === $('.task-item').length) {
                updateStreak();
            }

            // NEW: refresh notifications
            fetchAndRenderNotifications();
        } else {
            alert('Error updating task: ' + data.error);
        }
    })
    .catch(error => console.error('Error updating task:', error));
}

    function updateProgress() {
        const totalTasks = $('.task-item').length;
        const completedTasks = $('.task-checkbox:checked').length;
        const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
        
        $('.progress-bar').css('width', progress + '%').attr('aria-valuenow', progress);
        $('.progress-percent').text(Math.round(progress) + '%');
        $('.tasks-completed').text(`${completedTasks} of ${totalTasks} tasks completed`);
        
        // Update streak if all tasks completed
        if (completedTasks === totalTasks && totalTasks > 0) {
            updateStreak();
        }
    }

    function updateStreak() {
        // Send a request to the backend to increment the user's streak
        const csrfToken = document.getElementById('csrfToken').value;
        fetch('/api/increment-streak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the displayed streak
                const currentStreak = parseInt($('.streak-days').text()) || 0;
                $('.streak-days').text(data.streak + ' days');
            }
        })
        .catch(error => console.error('Error updating streak:', error));
    }

    // Initialize empty state
    if ($('.task-item').length === 0) {
        $('.empty-state').show();
        $('.tasks-section').hide();
    }
});

/**
 * Render the notification bar from an array of notifications.
 * @param {Array} notifications
 */
function renderNotifications(notifications) {
    // Remove any existing alert
    const existingAlert = document.querySelector('.alert.alert-info[data-notification-bar="1"]');
    if (existingAlert) {
        existingAlert.remove();
    }

    if (!notifications || notifications.length === 0) {
        return; // nothing to render
    }

    // Build HTML for the notification bar
    const wrapper = document.querySelector('.py-4');
    if (!wrapper) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-info alert-dismissible fade show';
    alertDiv.setAttribute('role', 'alert');
    alertDiv.setAttribute('data-notification-bar', '1');

    const ul = document.createElement('ul');
    ul.className = 'mb-0';

    notifications.forEach(n => {
        const li = document.createElement('li');

        let text = '';
        if (n.type === 'task_due') {
            const payload = n.payload || {};
            const title = payload.title || 'Task';
            const done = !!payload.done;
            if (done) {
                text = `Task "${title}" is done.`;
            } else {
                text = `Task "${title}" still needs to be done.`;
            }
        } else if (n.type === 'daily_checkin') {
            text = "Don't forget your daily check-in!";
        } else if (n.type === 'streak_warning') {
            text = "Warning: Your streak is at risk!";
        } else {
            text = 'You have a notification.'; // fallback
        }

        li.appendChild(document.createTextNode(text + ' '));

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn-close dismiss-notification';
        btn.setAttribute('aria-label', 'Close');
        btn.dataset.notificationId = n._id;

        li.appendChild(btn);
        ul.appendChild(li);
    });

    alertDiv.appendChild(ul);

    // Insert alert at the top of .py-4, before other content
    wrapper.insertBefore(alertDiv, wrapper.firstChild);
}

/**
 * Fetch notifications from the backend and render them.
 */
function fetchAndRenderNotifications() {
    fetch('/api/notifications')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderNotifications(data.notifications || []);
            } else {
                console.warn('Failed to fetch notifications:', data.error);
            }
        })
        .catch(err => {
            console.error('Error fetching notifications:', err);
        });
}

const csrfMeta = document.querySelector('meta[name="csrf-token"]');
const csrfHeaderToken = csrfMeta ? csrfMeta.content : null;

$(document).on("click", ".dismiss-notification", function (e) {
    e.preventDefault();
    e.stopPropagation();

    const $btn = $(this);

    if ($btn.data("dismissing")) {
        return;
    }
    $btn.data("dismissing", true);

    const notificationId = $btn.data("notification-id");
    const csrfToken = csrfHeaderToken || document.getElementById('csrfToken')?.value || '';

    const $li = $btn.closest("li");
    const $alert = $btn.closest(".alert.alert-info");

    console.log("Dismissing notification", notificationId);

    // Optimistically remove this notification row
    if ($li.length) {
        $li.remove();
    }

    // If no more notifications, remove the whole alert box
    if ($alert.length && $alert.find("li").length === 0) {
        $alert.remove();
    }

    fetch(`/api/notifications/dismiss/${notificationId}`, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(async (res) => {
        if (!res.ok) {
            // Log, but do NOT show any alert
            console.warn(
                "Non-2xx response when dismissing notification",
                notificationId,
                "status:", res.status
            );
            try {
                const data = await res.json();
                console.warn("Dismiss error body:", data);
            } catch (e) {
                console.warn("Could not parse dismiss error JSON");
            }
        } else {
            console.log("Dismiss success", notificationId);
        }
    })
    .catch(err => {
        // Also just log, no alert
        console.error('Dismiss error:', err);
    })
    .finally(() => {
        $btn.data("dismissing", false);
    });
});