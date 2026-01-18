/**
 * Forgot Password Page JavaScript
 * ================================
 * This file handles the password reset request form:
 * - Email validation before submission
 * - Real-time email format feedback
 * - Loading state during submission
 * 
 * Security Note:
 * The server always responds with the same message whether the email
 * exists or not, to prevent email enumeration attacks.
 */

$(document).ready(function() {
    
    // ============================================
    // FORM VALIDATION
    // ============================================
    
    /**
     * Handle forgot password form submission
     * Validates email before allowing form to submit
     */
    $('#forgotPasswordForm, form').on('submit', function(e) {
        const email = $('#email').val().trim();
        
        // Validate email is provided
        if (!email) {
            e.preventDefault();
            showValidationError('Please enter your email address.');
            $('#email').focus();
            return false;
        }
        
        // Validate email format
        if (!isValidEmail(email)) {
            e.preventDefault();
            showValidationError('Please enter a valid email address.');
            $('#email').focus();
            return false;
        }
        
        // All validation passed - show loading state
        const submitBtn = $(this).find('button[type="submit"]');
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Sending...');
        submitBtn.prop('disabled', true);
    });
    
    // ============================================
    // REAL-TIME VALIDATION
    // ============================================
    
    /**
     * Validate email format when user leaves the field
     * Provides immediate feedback on email validity
     */
    $('#email').on('blur', function() {
        const email = $(this).val().trim();
        
        if (email) {
            if (!isValidEmail(email)) {
                // Invalid email - show error styling
                $(this).addClass('is-invalid').removeClass('is-valid');
            } else {
                // Valid email - show success styling
                $(this).addClass('is-valid').removeClass('is-invalid');
            }
        } else {
            // Empty field - remove validation styling
            $(this).removeClass('is-invalid is-valid');
        }
    });
    
    /**
     * Clear validation styling when user starts typing
     */
    $('#email').on('input', function() {
        $(this).removeClass('is-invalid is-valid');
        $('.validation-error-alert').fadeOut(200, function() {
            $(this).remove();
        });
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
        // Standard email regex pattern
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    /**
     * Show a validation error message
     * Creates an alert above the form
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
});
