/**
 * Dashboard JavaScript - Main Entry Point
 * ========================================
 * This file initializes all dashboard modules and coordinates their setup.
 * 
 * Modules:
 * - csrf.js: CSRF token handling
 * - tasks.js: Task CRUD operations
 * - progress.js: Progress bar updates
 * - rewards.js: Rewards system
 * - notifications.js: Notification handling
 * - modal.js: Add task modal
 * - upload.js: File upload for quiz
 */

$(document).ready(function () {

    // ============================================
    // INITIALIZATION
    // ============================================

    /**
     * Initialize all dashboard modules
     */

    // Initialize modal handling
    if (window.DashboardModal) {
        window.DashboardModal.initModal();
    }

    // Initialize file upload
    if (window.DashboardUpload) {
        window.DashboardUpload.initUpload();
    }

    // Initialize notification dismiss handler
    if (window.DashboardNotifications) {
        window.DashboardNotifications.initDismissHandler();
    }

    // Fetch existing tasks from server
    if (window.DashboardTasks) {
        window.DashboardTasks.fetchTasks();
    }

    // Update progress bar
    if (window.DashboardProgress) {
        window.DashboardProgress.updateProgress();
    }

    // Fetch user rewards
    if (window.DashboardRewards) {
        window.DashboardRewards.fetchRewards();
    }

    // ============================================
    // EMPTY STATE HANDLING
    // ============================================

    // Show empty state if no tasks exist
    if ($('.task-item').length === 0) {
        $('.empty-state').show();
    }
});
