/**
 * Dashboard JavaScript
 * ====================
 * This file handles all dashboard functionality including:
 * - Task management (create, toggle, delete)
 * - Progress tracking
 * - Notifications
 * - Rewards system
 * - File upload handling
 * 
 * CSRF Protection:
 * All POST/PATCH/DELETE requests include CSRF token from either:
 * 1. Hidden input field with id="csrfToken"
 * 2. Meta tag with name="csrf-token"
 */

$(document).ready(function() {
    
    // ============================================
    // CSRF TOKEN HANDLING
    // ============================================
    
    /**
     * Get CSRF token from the page
     * Checks hidden input first, then meta tag as fallback
     * 
     * @returns {string} CSRF token value
     */
    function getCsrfToken() {
        // Try to get from hidden input (set in modal form)
        const hiddenInput = document.getElementById('csrfToken');
        if (hiddenInput) {
            return hiddenInput.value;
        }
        
        // Fallback to meta tag (set in base.html)
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.content;
        }
        
        console.warn('CSRF token not found!');
        return '';
    }
    
    // ============================================
    // INITIALIZATION
    // ============================================
    
    /**
     * Initialize the dashboard when page loads:
     * 1. Fetch existing tasks from server
     * 2. Update progress bar
     * 3. Fetch user rewards
     */
    fetchTasks();
    updateProgress();
    fetchRewards();

    // ============================================
    // FILE UPLOAD HANDLING
    // ============================================
    
    /**
     * Handle file selection for quiz generation
     * When user selects a file:
     * 1. Validate the file type
     * 2. Auto-submit the form if valid
     */
    $('#fileUpload').on('change', function() {
        const file = this.files[0];
        
        if (file) {
            // Define allowed MIME types for quiz documents
            const allowedTypes = [
                'application/pdf',                                                    // PDF files
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // DOCX files
                'text/plain',                                                         // TXT files
                'image/png',                                                          // PNG images
                'image/jpeg',                                                         // JPEG images
                'image/gif'                                                           // GIF images
            ];
            
            // Check if file type is allowed
            if (!allowedTypes.includes(file.type)) {
                alert('Invalid file type. Please upload PDF, DOCX, TXT, or image files.');
                return;
            }
            
            // Submit the form to generate quiz
            // The server will extract text and generate questions
            $('#uploadForm').submit();
        }
    });

    // ============================================
    // MODAL HANDLING
    // ============================================
    
    // Get references to modal elements
    const modalElement = document.getElementById("taskModal");
    const taskTitleInput = document.getElementById("taskTitleInput");

    /**
     * Open the Add Task modal
     * - Shows the modal using Bootstrap API
     * - Clears any previous input
     */
    $('#openTaskModal').on('click', function() {
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
    $('#saveTaskBtn').on('click', function() {
        const title = taskTitleInput ? taskTitleInput.value.trim() : "";
        
        if (title) {
            createTask(title);
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
    $('#taskTitleInput').on('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            $('#saveTaskBtn').click();
        }
    });

    // ============================================
    // TASK API FUNCTIONS
    // ============================================

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
                    updateProgress();
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
        $(`#check-${taskId}`).on('change', function() {
            toggleTask(taskId);
        });
        
        $(`.delete-task[data-task-id="${taskId}"]`).on('click', function() {
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
        const csrfToken = getCsrfToken();
        
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

    /**
     * Delete a task via API
     * Removes task from database and DOM
     * 
     * @param {string} taskId - The MongoDB ObjectId of the task
     */
    function deleteTask(taskId) {
        const csrfToken = getCsrfToken();
        
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
                $(`#task-${taskId}`).fadeOut(300, function() {
                    $(this).remove();
                    
                    // Update progress bar
                    updateProgress();
                    
                    // Show empty state if no tasks left
                    if ($('.task-item').length === 0) {
                        $('.empty-state').show();
                    }
                });
                
                // Refresh notifications in case task had related notifications
                fetchAndRenderNotifications();
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
        const csrfToken = getCsrfToken();
        
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
                updateProgress();
                
                // Refresh notifications
                fetchAndRenderNotifications();
                
                // Check if user earned any new rewards
                checkAndShowRewards();
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

    // ============================================
    // PROGRESS TRACKING
    // ============================================

    /**
     * Update the progress bar and stats display
     * Calculates completion percentage based on checked tasks
     */
    function updateProgress() {
        // Count total and completed tasks
        const totalTasks = $('.task-item').length;
        const completedTasks = $('.task-checkbox:checked').length;
        
        // Calculate percentage (avoid division by zero)
        const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
        
        // Update progress bar width
        $('.progress-bar').css('width', progress + '%').attr('aria-valuenow', progress);
        
        // Update percentage text
        $('.progress-percent').text(Math.round(progress) + '%');
        
        // Update tasks completed text
        $('.tasks-completed').text(`${completedTasks} of ${totalTasks} tasks completed`);
    }

    // ============================================
    // REWARDS SYSTEM
    // ============================================

    /**
     * Check for new rewards and show notifications
     * Called after task completion to see if user earned any badges
     */
    function checkAndShowRewards() {
        const csrfToken = getCsrfToken();
        
        fetch('/api/rewards/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // CSRF protection
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.new_rewards && data.new_rewards.length > 0) {
                // Show notification for each new reward
                data.new_rewards.forEach(reward => {
                    showRewardNotification(reward);
                });
                
                // Refresh the rewards display
                fetchRewards();
            }
        })
        .catch(error => {
            console.error('Error checking rewards:', error);
        });
    }

    /**
     * Display a toast notification for a new reward
     * Shows the reward name, description, and points earned
     * 
     * @param {Object} reward - Reward object with name, description, points, icon
     */
    function showRewardNotification(reward) {
        // Create toast HTML
        const toast = `
            <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1100;">
                <div class="toast show bg-success text-white" role="alert">
                    <div class="toast-header bg-success text-white">
                        <strong class="me-auto">🏆 New Reward!</strong>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        <strong>${reward.name}</strong><br>
                        ${reward.description}<br>
                        <span class="badge bg-warning text-dark mt-2">+${reward.points} points</span>
                    </div>
                </div>
            </div>
        `;
        
        // Add toast to page
        $('body').append(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            $('.toast-container').fadeOut(500, function() {
                $(this).remove();
            });
        }, 5000);
    }

    /**
     * Fetch all rewards earned by the user
     * Updates the rewards display panel
     */
    function fetchRewards() {
        fetch('/api/rewards')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateRewardsDisplay(data.rewards, data.total_points);
                }
            })
            .catch(error => {
                console.error('Error fetching rewards:', error);
            });
    }

    /**
     * Update the rewards display panel
     * Shows earned badges and total points
     * 
     * @param {Array} rewards - Array of reward objects
     * @param {number} totalPoints - User's total points
     */
    function updateRewardsDisplay(rewards, totalPoints) {
        // Only update if rewards container exists
        if ($('#rewardsContainer').length) {
            // Update total points
            $('#totalPoints').text(totalPoints);
            
            // Build badges HTML
            if (rewards && rewards.length > 0) {
                const badgesHtml = rewards.map(r => {
                    // Determine badge color based on tier
                    let badgeClass = 'bg-primary';  // Bronze = primary/blue
                    if (r.tier === 'gold') {
                        badgeClass = 'bg-warning text-dark';
                    } else if (r.tier === 'silver') {
                        badgeClass = 'bg-secondary';
                    }
                    
                    return `
                        <span class="badge ${badgeClass} me-1 mb-1" title="${r.description}">
                            ${r.icon} ${r.name}
                        </span>
                    `;
                }).join('');
                
                $('#rewardsBadges').html(badgesHtml);
            } else {
                $('#rewardsBadges').html('<span class="text-muted small">Complete tasks to earn rewards!</span>');
            }
        }
    }

    // ============================================
    // EMPTY STATE HANDLING
    // ============================================
    
    // Show empty state if no tasks exist
    if ($('.task-item').length === 0) {
        $('.empty-state').show();
    }
});


// ============================================
// NOTIFICATIONS SYSTEM
// ============================================

/**
 * Render notifications in the notification bar
 * Creates DOM elements for each notification
 * 
 * @param {Array} notifications - Array of notification objects
 */
function renderNotifications(notifications) {
    // Remove any existing notification bar
    const existingAlert = document.querySelector('.alert.alert-info[data-notification-bar="1"]');
    if (existingAlert) {
        existingAlert.remove();
    }

    // Don't render if no notifications
    if (!notifications || notifications.length === 0) {
        return;
    }

    // Find the container to insert notifications into
    const wrapper = document.querySelector('.py-4');
    if (!wrapper) return;

    // Create the alert container
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-info alert-dismissible fade show';
    alertDiv.setAttribute('role', 'alert');
    alertDiv.setAttribute('data-notification-bar', '1');

    // Create list for notifications
    const ul = document.createElement('ul');
    ul.className = 'mb-0';

    // Add each notification to the list
    notifications.forEach(n => {
        const li = document.createElement('li');

        // Determine notification text based on type
        let text = '';
        if (n.type === 'task_due') {
            const payload = n.payload || {};
            const title = payload.title || 'Task';
            const done = !!payload.done;
            
            if (done) {
                text = `✅ Task "${title}" is done.`;
            } else {
                text = `⏰ Task "${title}" still needs to be done.`;
            }
        } else if (n.type === 'daily_checkin') {
            text = "📅 Don't forget your daily check-in!";
        } else if (n.type === 'streak_warning') {
            text = "⚠️ Warning: Your streak is at risk!";
        } else if (n.type === 'reward_earned') {
            const payload = n.payload || {};
            text = `🏆 You earned: ${payload.name || 'a reward'}!`;
        } else {
            text = '📢 You have a notification.';
        }

        // Add text node
        li.appendChild(document.createTextNode(text + ' '));

        // Add dismiss button
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn-close dismiss-notification';
        btn.setAttribute('aria-label', 'Close');
        btn.dataset.notificationId = n._id;

        li.appendChild(btn);
        ul.appendChild(li);
    });

    alertDiv.appendChild(ul);

    // Insert at the top of the content area
    wrapper.insertBefore(alertDiv, wrapper.firstChild);
}

/**
 * Fetch notifications from the server and render them
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

/**
 * Handle notification dismiss button clicks
 * Uses event delegation since notifications are dynamically added
 */
$(document).on("click", ".dismiss-notification", function(e) {
    e.preventDefault();
    e.stopPropagation();

    const $btn = $(this);

    // Prevent double-clicks
    if ($btn.data("dismissing")) {
        return;
    }
    $btn.data("dismissing", true);

    const notificationId = $btn.data("notification-id");
    
    // Get CSRF token
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfMeta ? csrfMeta.content : (document.getElementById('csrfToken')?.value || '');

    const $li = $btn.closest("li");
    const $alert = $btn.closest(".alert.alert-info");

    // Optimistically remove this notification from the DOM
    if ($li.length) {
        $li.fadeOut(200, function() {
            $(this).remove();
            
            // If no more notifications, remove the whole alert box
            if ($alert.length && $alert.find("li").length === 0) {
                $alert.fadeOut(200, function() {
                    $(this).remove();
                });
            }
        });
    }

    // Send dismiss request to server
    fetch(`/api/notifications/dismiss/${notificationId}`, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrfToken  // CSRF protection
        }
    })
    .then(async (res) => {
        if (!res.ok) {
            console.warn("Failed to dismiss notification:", notificationId);
        }
    })
    .catch(err => {
        console.error('Dismiss error:', err);
    })
    .finally(() => {
        $btn.data("dismissing", false);
    });
});