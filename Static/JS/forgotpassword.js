$(document).ready(function() {
    $('#forgotPasswordForm').on('submit', function(e) {
        e.preventDefault();
        
        const email = $('#email').val().trim();
        
        if (!isValidEmail(email)) {
            showMessage('Please enter a valid email address', 'error');
            return;
        }

        // Show loading state
        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.text();
        submitBtn.prop('disabled', true).text('Sending...');

        $.ajax({
            url: '/forgotpassword',
            type: 'POST',
            data: { email: email },
            success: function(response) {
                showMessage('If the email exists, a reset link has been sent.', 'success');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 3000);
            },
            error: function(xhr) {
                showMessage('An error occurred. Please try again.', 'error');
                submitBtn.prop('disabled', false).text(originalText);
            }
        });
    });

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function showMessage(message, type) {
        $('#messageAlert').remove();
        const alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
        $(`<div class="alert ${alertClass} alert-dismissible fade show" id="messageAlert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`).insertBefore('#forgotPasswordForm');
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