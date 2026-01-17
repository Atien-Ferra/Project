/**
 * Login Page JavaScript
 * =====================
 * This file handles login form validation and UX improvements:
 * - Client-side validation before form submission
 * - Loading state on submit button
 * - Email format validation
 * 
 * Note: Actual authentication is handled server-side for security.
 * This client-side validation is for better UX only.
 */

$(document).ready(function() {
    
    // ============================================
    // FORM VALIDATION
    // ============================================
    
    /**
     * Handle login form submission
     * Validates required fields before allowing submission
     */
    $("form").on("submit", function(event) {
        // Get form values
        const email = $("#email").val().trim();
        const password = $("#password").val();
        
        // Check if email is provided
        if (!email) {
            event.preventDefault();
            showValidationError("Please enter your email address.");
            $("#email").focus();
            return false;
        }
        
        // Basic email format validation
        if (!isValidEmail(email)) {
            event.preventDefault();
            showValidationError("Please enter a valid email address.");
            $("#email").focus();
            return false;
        }
        
        // Check if password is provided
        if (!password) {
            event.preventDefault();
            showValidationError("Please enter your password.");
            $("#password").focus();
            return false;
        }
        
        // All validation passed - show loading state
        const submitBtn = $(this).find('button[type="submit"]');
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Signing In...');
        submitBtn.prop('disabled', true);
    });
    
    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    
    /**
     * Validate email format using regex
     * 
     * @param {string} email - Email address to validate
     * @returns {boolean} True if email format is valid
     */
    function isValidEmail(email) {
        // Basic email regex pattern
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email);
    }
    
    /**
     * Show a validation error message
     * Creates an alert at the top of the form
     * 
     * @param {string} message - Error message to display
     */
    function showValidationError(message) {
        // Remove any existing error messages
        $('.validation-error-alert').remove();
        
        // Create error alert
        const errorHtml = `
            <div class="alert alert-danger alert-dismissible fade show validation-error-alert mb-3" role="alert">
                <i class="bi bi-exclamation-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Insert at top of form
        $('form').prepend(errorHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            $('.validation-error-alert').fadeOut(300, function() {
                $(this).remove();
            });
        }, 5000);
    }
    
    // ============================================
    // UX ENHANCEMENTS
    // ============================================
    
    /**
     * Clear validation errors when user starts typing
     */
    $('#email, #password').on('input', function() {
        $('.validation-error-alert').fadeOut(200, function() {
            $(this).remove();
        });
    });
    
    /**
     * Handle Enter key on email field to move to password
     */
    $('#email').on('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            $('#password').focus();
        }
    });
});
