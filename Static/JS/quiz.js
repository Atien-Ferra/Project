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

    // Submit quiz form
    $('#quizForm').on('submit', function(e) {
        // Check if all questions answered
        const answered = $('input[type="radio"]:checked').length;
        if (answered !== totalQuestions) {
            e.preventDefault();
            alert('Please answer all questions before submitting.');
            return false;
        }
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
    }

    function updateNavigation() {
        $('.prev-btn').prop('disabled', currentQuestion === 1);
        $('.next-btn').prop('disabled', currentQuestion === totalQuestions);
        $('.question-indicator').text(`Question ${currentQuestion} of ${totalQuestions}`);
    }

    // Initialize first question
    showQuestion(1);
});