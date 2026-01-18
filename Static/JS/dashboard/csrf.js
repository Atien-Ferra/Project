/**
 * CSRF Token Handling Module
 * ==========================
 * Provides CSRF token retrieval for secure API calls.
 */

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

// Export for use by other modules
window.DashboardCSRF = { getCsrfToken };
