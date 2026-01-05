$(document).ready(function() {
    let currentQuestion = 1;
    const totalQuestions = 5;

    // Initialize quiz
    updateProgress();

    // Navigation
    $('.next-btn').on('click', function() {
        if (currentQuestion < totalQuestions) {
            showQuestion(currentQuestion + 1);
        }
    });

    $('.prev-btn').on('click', function() {
        if (currentQuestion > 1) {
            showQuestion(currentQuestion - 1);
        }
    });

    // Track answer selection for progress updates
    $('input[type="radio"]').on('change', function() {
        updateProgress();
    });

    // Submit quiz form (via AJAX so we can show results nicely)
    $('#quizForm').on('submit', function(e) {
        e.preventDefault();
        // Check if all questions answered
        const answered = $('input[type="radio"]:checked').length;
        if (answered !== totalQuestions) {
            alert('Please answer all questions before submitting.');
            return false;
        }

        const form = this;
        const formData = new FormData(form);
        // Get CSRF token from meta tag if available, fallback to hidden input
        let csrf = document.querySelector('meta[name="csrf-token"]') ? document.querySelector('meta[name="csrf-token"]').content : '';
        if (!csrf) {
            const t = form.querySelector('input[name="csrf_token"]');
            csrf = t ? t.value : '';
        }

        fetch('/quiz', {
            method: 'POST',
            body: formData,
            headers: csrf ? { 'X-CSRFToken': csrf } : {}
        })
        .then(res => res.json())
        .then(data => {
            if (data && typeof data.percentage !== 'undefined') {
                alert(`Score: ${data.score}/${data.total} (${data.percentage}%). ${data.passed ? 'Passed!' : 'Not passed.'}`);
                // redirect back to dashboard or refresh
                window.location.href = '/dashboard';
            } else {
                alert('Unexpected response from the server.');
            }
        })
        .catch(err => {
            console.error(err);
            alert('Error submitting quiz. Please try again.');
        });
    });

    function showQuestion(questionNum) {
        $('.question-card').removeClass('active');
        $(`#question-${questionNum}`).addClass('active');
        currentQuestion = questionNum;
        updateNavigation();
    }

    function updateProgress() {
        const answered = $('input[type="radio"]:checked').length;
        const progress = (answered / totalQuestions) * 100;
        
        $('.quiz-progress-bar').css('width', progress + '%');
        $('.progress-text').text(`${answered}/${totalQuestions} answered`);
        // enable submit when all answered
        $('#submitQuiz').prop('disabled', answered !== totalQuestions);
    }

    function updateNavigation() {
        $('.prev-btn').prop('disabled', currentQuestion === 1);
        $('.next-btn').prop('disabled', currentQuestion === totalQuestions);
        $('.question-indicator').text(`Question ${currentQuestion} of ${totalQuestions}`);
    }

    // Initialize first question
    showQuestion(1);
});