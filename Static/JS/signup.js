$(document).ready(function() {
    // Simple form validation before submit
    $('#signupForm').on('submit', function(e) {
        const password = $('#password').val();
        const confirmPassword = $('#confirm_password').val();
        
        if (password !== confirmPassword) {
            e.preventDefault();
            alert('Passwords do not match!');
            return false;
        }
        
        if (password.length < 6) {
            e.preventDefault();
            alert('Password must be at least 6 characters long');
            return false;
        }
        
        if (!$('#terms').is(':checked')) {
            e.preventDefault();
            alert('Please accept the terms and conditions');
            return false;
        }
    }); 

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