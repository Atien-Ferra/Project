/**
 * Update Password Page JavaScript
 * ================================
 * This file handles password update form validation:
 * - Validates current password field (when logged in)
 * - Validates new password requirements
 * - Confirms password match
 * - Password strength indicator
 * 
 * This page is used in two contexts:
 * 1. Logged-in user changing password (has current_password field)
 * 2. Password reset via token (no current_password field)
 */

$(document).ready(function() {
    
    // ============================================
    // CONFIGURATION
    // ============================================
    
    /**
     * Minimum password length required
     * Must match server-side validation (8 characters)
     */
    const MIN_PASSWORD_LENGTH = 8;
    
    /**
     * Check if this is the logged-in flow (has current password field)
     * or the reset token flow (no current password field)
     */
    const isLoggedInFlow = $("#current_password").length > 0;
    
    // ============================================
    // FORM VALIDATION
    // ============================================
    
    /**
     * Handle password update form submission
     * Validates all fields before allowing form to submit
     */
    $("form").on("submit", function(event) {
        // Get form values
        const currentPassword = isLoggedInFlow ? $("#current_password").val() : null;
        const newPassword = $("#new_password").val();
        const confirmPassword = $("#confirm_password").val();
        
        // Validate current password (only for logged-in flow)
        if (isLoggedInFlow && !currentPassword) {
            event.preventDefault();
            showValidationError("Please enter your current password.");
            $("#current_password").focus();
            return false;
        }
        
        // Validate new password is provided
        if (!newPassword) {
            event.preventDefault();
            showValidationError("Please enter a new password.");
            $("#new_password").focus();
            return false;
        }
        
        // Validate password length
        if (newPassword.length < MIN_PASSWORD_LENGTH) {
            event.preventDefault();
            showValidationError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`);
            $("#new_password").focus();
            return false;
        }
        
        // Validate confirm password is provided
        if (!confirmPassword) {
            event.preventDefault();
            showValidationError("Please confirm your new password.");
            $("#confirm_password").focus();
            return false;
        }
        
        // Validate passwords match
        if (newPassword !== confirmPassword) {
            event.preventDefault();
            showValidationError("New password and confirmation do not match.");
            $("#confirm_password").focus();
            return false;
        }
        
        // All validation passed - show loading state
        const submitBtn = $(this).find('button[type="submit"]');
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Updating...');
        submitBtn.prop('disabled', true);
    });
    
    // ============================================
    // PASSWORD STRENGTH INDICATOR
    // ============================================
    
    /**
     * Show password strength as user types
     */
    $('#new_password').on('input', function() {
        const password = $(this).val();
        const strength = calculatePasswordStrength(password);
        updatePasswordStrengthDisplay(strength);
    });
    
    /**
     * Calculate password strength score
     * 
     * @param {string} password - Password to evaluate
     * @returns {number} Strength score from 0-4
     */
    function calculatePasswordStrength(password) {
        let strength = 0;
        
        // +1 for minimum length
        if (password.length >= MIN_PASSWORD_LENGTH) {
            strength++;
        }
        
        // +1 for mixed case
        if (password.match(/[a-z]/) && password.match(/[A-Z]/)) {
            strength++;
        }
        
        // +1 for numbers
        if (password.match(/\d/)) {
            strength++;
        }
        
        // +1 for special characters
        if (password.match(/[^a-zA-Z\d]/)) {
            strength++;
        }
        
        return strength;
    }
    
    /**
     * Update password strength display
     * 
     * @param {number} strength - Strength score from 0-4
     */
    function updatePasswordStrengthDisplay(strength) {
        const labels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const classes = ['danger', 'warning', 'info', 'primary', 'success'];
        
        const $indicator = $('#passwordStrength');
        if ($indicator.length) {
            $indicator
                .text(labels[strength] || '')
                .removeClass('text-danger text-warning text-info text-primary text-success')
                .addClass('text-' + (classes[strength] || 'muted'));
        }
    }
    
    // ============================================
    // PASSWORD CONFIRMATION MATCHING
    // ============================================
    
    /**
     * Check password match as user types
     */
    $('#confirm_password').on('input', function() {
        const newPassword = $('#new_password').val();
        const confirmPassword = $(this).val();
        
        if (confirmPassword.length > 0) {
            if (newPassword === confirmPassword) {
                $(this).removeClass('is-invalid').addClass('is-valid');
            } else {
                $(this).removeClass('is-valid').addClass('is-invalid');
            }
        } else {
            $(this).removeClass('is-invalid is-valid');
        }
    });
    
    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    
    /**
     * Show a validation error message
     * Creates an alert at the top of the form
     * 
     * @param {string} message - Error message to display
     */
    function showValidationError(message) {
        // Remove any existing error messages
        $('.validation-error-alert').remove();
        
        // Create error alert HTML
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
    
    /**
     * Clear validation errors when user starts typing
     */
    $('#current_password, #new_password, #confirm_password').on('input', function() {
        $('.validation-error-alert').fadeOut(200, function() {
            $(this).remove();
        });
    });
});
