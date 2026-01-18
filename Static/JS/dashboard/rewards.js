/**
 * Rewards System Module
 * =====================
 * Handles checking, displaying, and notifying about user rewards.
 */

/**
 * Check for new rewards and show notifications
 * Called after task completion to see if user earned any badges
 */
function checkAndShowRewards() {
    const csrfToken = window.DashboardCSRF ? window.DashboardCSRF.getCsrfToken() : '';

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
        $('.toast-container').fadeOut(500, function () {
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

// Export for use by other modules
window.DashboardRewards = {
    checkAndShowRewards,
    showRewardNotification,
    fetchRewards,
    updateRewardsDisplay
};
