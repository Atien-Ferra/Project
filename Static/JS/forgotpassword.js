$(document).ready(function() {
    // Simple email validation before submit
    $('#forgotPasswordForm').on('submit', function(e) {
        const email = $('#email').val().trim();
        
        if (!isValidEmail(email)) {
            e.preventDefault();
            alert('Please enter a valid email address');
            return false;
        }
    });

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Real-time email validation
    $('#email').on('blur', function() {
        const email = $(this).val().trim();
        if (email && !isValidEmail(email)) {
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });
});