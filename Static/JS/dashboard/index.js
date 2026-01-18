/**
 * Dashboard JavaScript - Main Entry Point
 * ========================================
 * This script runs after the DOM is fully loaded. It acts as the "orchestrator"
 * for all modular JavaScript components, ensuring they are initialized in the 
 * correct order.
 */

$(document).ready(function () {

    // ============================================
    // MODULE INITIALIZATION
    // ============================================
    // Each module is checked for existence before calling its init method.
    // This allows for independent loading and prevents errors if a script fails to load.

    // 1. Setup UI components (Modals & Upload forms)
    if (window.DashboardModal) {
        window.DashboardModal.initModal();
    }

    if (window.DashboardUpload) {
        window.DashboardUpload.initUpload();
    }

    // 2. Setup event listeners (Notifications)
    if (window.DashboardNotifications) {
        window.DashboardNotifications.initDismissHandler();
    }

    // 3. Initial Data Fetching
    // We fetch tasks first as other UI elements (progress, empty states) 
    // depend on the task list being populated.
    if (window.DashboardTasks) {
        // fetchTasks() will trigger progress updates and empty state checks on success
        window.DashboardTasks.fetchTasks();
    }

    // 4. Update UI State
    if (window.DashboardProgress) {
        window.DashboardProgress.updateProgress();
    }

    // 5. Fetch Gamification Data
    if (window.DashboardRewards) {
        window.DashboardRewards.fetchRewards();
    }

    /**
     * Helper: Initial Empty State Check
     * This handles the initial visual state before the first AJAX fetch completes.
     */
    if ($('.task-item').length === 0) {
        $('.empty-state').show();
    }
});
