$(document).ready(function() {
    $('#signupForm').on('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            name: $('#name').val(),
            email: $('#email').val(),
            password: $('#password').val(),
            confirm_password: $('#confirm_password').val(),
            terms: $('#terms').is(':checked')
        };

        // Client-side validation
        if (formData.password !== formData.confirm_password) {
            showError('Passwords do not match');
            return;
        }

        if (formData.password.length < 6) {
            showError('Password must be at least 6 characters long');
            return;
        }

        if (!formData.terms) {
            showError('Please accept the terms and conditions');
            return;
        }

        // Submit form
        $.ajax({
            type: 'POST',
            url: '/signup',
            data: formData,
            success: function(response) {
                window.location.href = '/dashboard';
            },
            error: function(xhr) {
                showError(xhr.responseJSON?.error || 'An error occurred');
            }
        });
    });

    function showError(message) {
        $('#errorAlert').remove();
        $('<div class="alert alert-danger" id="errorAlert">' + message + '</div>')
            .insertBefore('#signupForm');
    }

    // Password strength indicator
    $('#password').on('input', function() {
        const password = $(this).val();
        const strength = calculatePasswordStrength(password);
        updatePasswordStrength(strength);
    });

    function calculatePasswordStrength(password) {
        let strength = 0;
        if (password.length >= 6) strength++;
        if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
        if (password.match(/\d/)) strength++;
        if (password.match(/[^a-zA-Z\d]/)) strength++;
        return strength;
    }

    function updatePasswordStrength(strength) {
        const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const strengthClass = ['danger', 'warning', 'info', 'primary', 'success'];
        
        $('#passwordStrength').text(strengthText[strength] || '');
        $('#passwordStrength').removeClass('text-danger text-warning text-info text-primary text-success')
            .addClass('text-' + strengthClass[strength]);
    }
});