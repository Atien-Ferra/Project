$(document).ready(function() {
    let currentQuestion = 1;
    const totalQuestions = 5;
    let userAnswers = {};

    // Initialize quiz
    updateProgress();

    // Answer selection
    $('.answer-option').on('click', function() {
        const questionId = $(this).closest('.question-card').data('question-id');
        const answerId = $(this).data('answer-id');
        
        // Remove selected class from all options in this question
        $(this).closest('.question-card').find('.answer-option').removeClass('selected');
        // Add selected class to clicked option
        $(this).addClass('selected');
        
        // Store answer
        userAnswers[questionId] = answerId;
        
        // Update progress
        updateProgress();
        
        // Auto-advance to next question after delay
        setTimeout(() => {
            if (questionId < totalQuestions) {
                showQuestion(questionId + 1);
            }
        }, 500);
    });

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

    // Submit quiz
    $('#submitQuiz').on('click', function() {
        if (Object.keys(userAnswers).length === totalQuestions) {
            submitQuiz();
        } else {
            alert('Please answer all questions before submitting.');
        }
    });

    function showQuestion(questionNum) {
        $('.question-card').removeClass('active');
        $(`#question-${questionNum}`).addClass('active');
        currentQuestion = questionNum;
        updateNavigation();
    }

    function updateProgress() {
        const answered = Object.keys(userAnswers).length;
        const progress = (answered / totalQuestions) * 100;
        
        $('.quiz-progress-bar').css('width', progress + '%');
        $('.progress-text').text(`${answered}/${totalQuestions} answered`);
        
        // Update submit button state
        $('#submitQuiz').prop('disabled', answered !== totalQuestions);
    }

    function updateNavigation() {
        $('.prev-btn').prop('disabled', currentQuestion === 1);
        $('.next-btn').prop('disabled', currentQuestion === totalQuestions);
        $('.question-indicator').text(`Question ${currentQuestion} of ${totalQuestions}`);
    }

    function submitQuiz() {
        $.ajax({
            url: '/quiz',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(userAnswers),
            success: function(response) {
                showResults(response);
            },
            error: function(xhr) {
                alert('Error submitting quiz: ' + (xhr.responseJSON?.error || 'Unknown error'));
            }
        });
    }

    function showResults(results) {
        const score = results.score;
        const total = results.total;
        const percentage = Math.round((score / total) * 100);
        
        const resultsHtml = `
            <div class="card shadow-sm mb-4">
                <div class="card-body text-center">
                    <h3 class="h5 mb-3">Quiz Completed!</h3>
                    <div class="display-4 text-${percentage >= 70 ? 'success' : 'danger'} mb-2">
                        ${percentage}%
                    </div>
                    <p class="text-secondary">You scored ${score} out of ${total} questions correctly.</p>
                    <div class="mt-4">
                        <a href="/dashboard" class="btn btn-outline-secondary me-2">Back to Dashboard</a>
                        <button class="btn btn-dark retry-quiz">Retry Quiz</button>
                    </div>
                </div>
            </div>
        `;
        
        $('.quiz-container').html(resultsHtml);
        
        $('.retry-quiz').on('click', function() {
            location.reload();
        });
    }

    // Initialize first question
    showQuestion(1);
});