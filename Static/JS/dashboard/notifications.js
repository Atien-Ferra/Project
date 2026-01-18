/**
 * Notifications System Module
 * ===========================
 * Handles fetching, rendering, and dismissing notifications.
 */

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
 * Initialize notification dismiss handler
 * Uses event delegation since notifications are dynamically added
 */
function initDismissHandler() {
    $(document).on("click", ".dismiss-notification", function (e) {
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
        const csrfToken = window.DashboardCSRF ? window.DashboardCSRF.getCsrfToken() : '';

        const $li = $btn.closest("li");
        const $alert = $btn.closest(".alert.alert-info");

        // Optimistically remove this notification from the DOM
        if ($li.length) {
            $li.fadeOut(200, function () {
                $(this).remove();

                // If no more notifications, remove the whole alert box
                if ($alert.length && $alert.find("li").length === 0) {
                    $alert.fadeOut(200, function () {
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
}

// Export for use by other modules
window.DashboardNotifications = {
    renderNotifications,
    fetchAndRenderNotifications,
    initDismissHandler
};
