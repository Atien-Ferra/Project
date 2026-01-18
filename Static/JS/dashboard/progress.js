/**
 * Progress Tracking Module
 * ========================
 * Handles progress bar updates based on task completion.
 */

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

    // Update progress bar width - use specific ID to avoid affecting timer progress bar
    $('#taskProgressBar').css('width', progress + '%').attr('aria-valuenow', progress);

    // Update percentage text
    $('.progress-percent').text(Math.round(progress) + '%');

    // Update tasks completed text
    $('.tasks-completed').text(`${completedTasks} of ${totalTasks} tasks completed`);
}

// Export for use by other modules
window.DashboardProgress = { updateProgress };
