/**
 * Signup Page JavaScript
 * ======================
 * This file handles signup form validation and UX improvements:
 * - Client-side form validation before submission
 * - Password strength indicator
 * - Real-time password confirmation matching
 * 
 * Note: Server-side validation is also performed for security.
 * This client-side validation is for better UX only.
 */

$(document).ready(function() {
    
    // ============================================
    // FORM VALIDATION
    // ============================================
    
    /**
     * Handle signup form submission
     * Validates all fields before allowing form to submit
     * 
     * Validation checks:
     * 1. Passwords match
     * 2. Password meets minimum length (8 characters)
     * 3. Terms and conditions accepted
     */
    $('#signupForm').on('submit', function(e) {
        // Get password values
        const password = $('#password').val();
        const confirmPassword = $('#confirm_password').val();
        
        // Check if passwords match
        if (password !== confirmPassword) {
            e.preventDefault();  // Stop form submission
            showValidationError('Passwords do not match!');
            $('#confirm_password').focus();
            return false;
        }
        
        // Check password minimum length
        // Note: Server requires 8 characters, matching that here
        if (password.length < 8) {
            e.preventDefault();
            showValidationError('Password must be at least 8 characters long');
            $('#password').focus();
            return false;
        }
        
        // Check terms acceptance
        if (!$('#terms').is(':checked')) {
            e.preventDefault();
            showValidationError('Please accept the terms and conditions');
            $('#terms').focus();
            return false;
        }
        
        // All validation passed, form will submit normally
        // Show loading state on submit button
        const submitBtn = $(this).find('button[type="submit"]');
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Creating Account...');
        submitBtn.prop('disabled', true);
    });
    
    // ============================================
    // PASSWORD STRENGTH INDICATOR
    // ============================================
    
    /**
     * Show password strength as user types
     * Updates the strength indicator in real-time
     */
    $('#password').on('input', function() {
        const password = $(this).val();
        const strength = calculatePasswordStrength(password);
        updatePasswordStrengthDisplay(strength);
    });
    
    /**
     * Calculate password strength score
     * 
     * Scoring criteria:
     * +1 - At least 8 characters
     * +1 - Contains both lowercase and uppercase letters
     * +1 - Contains at least one number
     * +1 - Contains at least one special character
     * 
     * @param {string} password - The password to evaluate
     * @returns {number} Strength score from 0-4
     */
    function calculatePasswordStrength(password) {
        let strength = 0;
        
        // Check minimum length
        if (password.length >= 8) {
            strength++;
        }
        
        // Check for mixed case letters
        if (password.match(/[a-z]/) && password.match(/[A-Z]/)) {
            strength++;
        }
        
        // Check for numbers
        if (password.match(/\d/)) {
            strength++;
        }
        
        // Check for special characters
        if (password.match(/[^a-zA-Z\d]/)) {
            strength++;
        }
        
        return strength;
    }
    
    /**
     * Update the password strength indicator display
     * 
     * @param {number} strength - Strength score from 0-4
     */
    function updatePasswordStrengthDisplay(strength) {
        // Define strength labels and colors
        const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const strengthClasses = ['danger', 'warning', 'info', 'primary', 'success'];
        
        // Get the strength indicator element (add this to your HTML if not present)
        const $indicator = $('#passwordStrength');
        
        if ($indicator.length) {
            // Update text
            $indicator.text(strengthLabels[strength] || '');
            
            // Update color class
            $indicator
                .removeClass('text-danger text-warning text-info text-primary text-success')
                .addClass('text-' + (strengthClasses[strength] || 'muted'));
        }
        
        // Also update the password input border color for visual feedback
        const $passwordInput = $('#password');
        $passwordInput
            .removeClass('border-danger border-warning border-info border-primary border-success')
            .addClass('border-' + (strengthClasses[strength] || 'secondary'));
    }
    
    // ============================================
    // CONFIRM PASSWORD MATCHING
    // ============================================
    
    /**
     * Check password match as user types in confirm field
     * Provides real-time feedback
     */
    $('#confirm_password').on('input', function() {
        const password = $('#password').val();
        const confirmPassword = $(this).val();
        
        // Only show feedback if user has typed something
        if (confirmPassword.length > 0) {
            if (password === confirmPassword) {
                // Passwords match - show success
                $(this).removeClass('border-danger').addClass('border-success');
                $('#confirmPasswordFeedback').text('Passwords match!').removeClass('text-danger').addClass('text-success');
            } else {
                // Passwords don't match - show error
                $(this).removeClass('border-success').addClass('border-danger');
                $('#confirmPasswordFeedback').text('Passwords do not match').removeClass('text-success').addClass('text-danger');
            }
        } else {
            // Clear feedback when field is empty
            $(this).removeClass('border-danger border-success');
            $('#confirmPasswordFeedback').text('');
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
        
        // Create error alert
        const errorHtml = `
            <div class="alert alert-danger alert-dismissible fade show validation-error-alert" role="alert">
                <i class="bi bi-exclamation-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Insert at top of form
        $('#signupForm').prepend(errorHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            $('.validation-error-alert').fadeOut(300, function() {
                $(this).remove();
            });
        }, 5000);
    }
});
