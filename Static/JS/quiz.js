/**
 * Quiz Page JavaScript
 * ====================
 * This file handles all quiz functionality including:
 * - Question navigation (next/previous buttons)
 * - Answer selection with visual feedback
 * - Progress bar tracking
 * - Form submission via AJAX
 * - Results display in a Bootstrap modal
 * 
 * CSRF Protection:
 * All POST requests include the CSRF token from either:
 * 1. Hidden input with name="csrf_token" in the form
 * 2. Meta tag with name="csrf-token" in the head
 */

$(document).ready(function() {
    
    // ============================================
    // CSRF TOKEN HANDLING
    // ============================================
    
    /**
     * Get CSRF token from the page
     * Required for all POST/PUT/DELETE requests
     * 
     * @returns {string} The CSRF token value
     */
    function getCsrfToken() {
        // First try the form's hidden input
        const formInput = document.querySelector('input[name="csrf_token"]');
        if (formInput) {
            return formInput.value;
        }
        
        // Fallback to meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.content;
        }
        
        console.warn('CSRF token not found!');
        return '';
    }
    
    // ============================================
    // CONFIGURATION & STATE
    // ============================================
    
    /**
     * Total number of questions in the quiz
     * Calculated by counting .question-card elements in the DOM
     * This is set dynamically from the server-rendered template
     */
    const totalQuestions = $('.question-card').length;
    
    /**
     * Current question number (1-based index)
     * Tracks which question the user is currently viewing
     */
    let currentQuestion = 1;
    
    /**
     * Flag to prevent double-submission of the form
     */
    let isSubmitting = false;

    // ============================================
    // INITIALIZATION
    // ============================================
    
    /**
     * Initialize quiz on page load
     * - Set up progress bar
     * - Ensure first question is visible
     */
    updateProgress();
    
    // Make sure only the first question is shown initially
    $('.question-card').removeClass('active');
    $('.question-card').first().addClass('active');
    
    // ============================================
    // ANSWER SELECTION
    // ============================================
    
    /**
     * Handle click on answer option cards
     * 
     * When user clicks anywhere on an answer option div:
     * 1. Remove 'selected' styling from all other options
     * 2. Add 'selected' styling to clicked option
     * 3. Check the hidden radio button for form submission
     * 
     * This provides a better UX than clicking tiny radio buttons
     */
    $('.answer-option').on('click', function() {
        // Get the container holding all answers for this question
        const container = $(this).closest('.answers-container');
        
        // Remove selection styling from all options in this question
        container.find('.answer-option').removeClass('selected');
        
        // Add selection styling to the clicked option
        $(this).addClass('selected');
        
        // Check the radio button inside this option
        // This ensures the answer is captured when form is submitted
        $(this).find('input[type="radio"]').prop('checked', true);
    });

    // ============================================
    // QUESTION NAVIGATION
    // ============================================
    
    /**
     * Handle "Next" button click
     * 
     * Moves to the next question if:
     * - User has selected an answer for current question
     * - There are more questions remaining
     */
    $('.next-btn').on('click', function() {
        // Get the current question card
        const currentCard = $(this).closest('.question-card');
        
        // Check if user selected an answer
        const selectedAnswer = currentCard.find('input[type="radio"]:checked');
        
        // Require answer before proceeding
        if (selectedAnswer.length === 0) {
            alert('Please select an answer before continuing.');
            return;
        }
        
        // Hide current question (remove 'active' class)
        currentCard.removeClass('active');
        
        // Show next question (add 'active' class)
        currentCard.next('.question-card').addClass('active');
        
        // Update question counter
        currentQuestion++;
        
        // Update progress bar
        updateProgress();
        
        // Scroll to top of question for better UX
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    /**
     * Handle "Previous" button click
     * 
     * Goes back to the previous question
     * No validation needed - user can go back freely
     */
    $('.prev-btn').on('click', function() {
        // Get the current question card
        const currentCard = $(this).closest('.question-card');
        
        // Hide current question
        currentCard.removeClass('active');
        
        // Show previous question
        currentCard.prev('.question-card').addClass('active');
        
        // Update question counter
        currentQuestion--;
        
        // Update progress bar
        updateProgress();
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // ============================================
    // PROGRESS TRACKING
    // ============================================
    
    /**
     * Update the progress bar and question indicator
     * 
     * Called whenever user navigates between questions
     * Shows progress as percentage of questions viewed
     */
    function updateProgress() {
        // Calculate progress percentage
        const progress = (currentQuestion / totalQuestions) * 100;
        
        // Update progress bar width (CSS transition handles animation)
        $('#quizProgress').css('width', progress + '%');
        
        // Update question number display (e.g., "3 / 5")
        $('#currentQuestion').text(currentQuestion);
    }

    // ============================================
    // FORM SUBMISSION
    // ============================================
    
    /**
     * Handle quiz form submission
     * 
     * Process:
     * 1. Prevent default form submission (page reload)
     * 2. Collect all answers from the form
     * 3. Send to server via AJAX
     * 4. Display results in modal
     * 
     * Server response format:
     * {
     *   score: number,       // Correct answers count
     *   total: number,       // Total questions
     *   percentage: number,  // Score as percentage
     *   passed: boolean      // True if >= 60%
     * }
     */
    $('#quizForm').on('submit', function(e) {
        // Prevent normal form submission
        e.preventDefault();
        
        // Prevent double submission
        if (isSubmitting) {
            return;
        }
        isSubmitting = true;
        
        // Create FormData from the form
        // This automatically includes all input fields
        const formData = new FormData(this);
        
        // Get CSRF token
        const csrfToken = getCsrfToken();
        
        // Show loading state on submit button
        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.html();
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Submitting...');
        submitBtn.prop('disabled', true);
        
        /**
         * Send quiz answers to the server
         * 
         * The server will:
         * 1. Retrieve the user's current questions
         * 2. Compare submitted answers with correct answers
         * 3. Calculate score and percentage
         * 4. Update user stats (quizzes_taken, tasks_done if passed)
         * 5. Check for new rewards
         * 6. Delete the uploaded quiz file
         */
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                // Note: Don't set Content-Type when sending FormData
                // The browser will set it with the correct boundary
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            // Check for HTTP errors
            if (!response.ok) {
                throw new Error('Server returned ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            // Display results in modal
            showResults(data);
        })
        .catch(error => {
            console.error('Error submitting quiz:', error);
            alert('An error occurred while submitting the quiz. Please try again.');
            
            // Reset submit button
            submitBtn.html(originalText);
            submitBtn.prop('disabled', false);
            isSubmitting = false;
        });
    });

    // ============================================
    // RESULTS DISPLAY
    // ============================================
    
    /**
     * Display quiz results in a Bootstrap modal
     * 
     * Shows:
     * - Pass/fail icon and message
     * - Score (e.g., "4/5")
     * - Percentage with color coding
     * - Link back to dashboard
     * 
     * @param {Object} data - Server response containing results
     * @param {number} data.score - Number of correct answers
     * @param {number} data.total - Total number of questions
     * @param {number} data.percentage - Score as percentage (0-100)
     * @param {boolean} data.passed - True if user passed (>= 60%)
     */
    function showResults(data) {
        const passed = data.passed;
        const percentage = data.percentage;
        
        // Set emoji icon based on pass/fail
        // 🎉 = celebration for passing
        // 😔 = sad face for failing
        $('#resultIcon').text(passed ? '🎉' : '😔');
        
        // Set title text
        $('#resultTitle').text(passed ? 'Congratulations!' : 'Keep Trying!');
        
        // Set message with appropriate encouragement
        if (passed) {
            $('#resultMessage').text('Great job! You passed the quiz and earned progress toward your goals!');
        } else {
            $('#resultMessage').text('You need 60% to pass. Don\'t worry - review the material and try again!');
        }
        
        // Display score (e.g., "4/5")
        $('#scoreDisplay').text(data.score + '/' + data.total);
        
        // Display percentage with color coding
        // Green = passed, Red = failed
        $('#percentageDisplay')
            .text(percentage + '%')
            .removeClass('text-success text-danger')
            .addClass(passed ? 'text-success' : 'text-danger');
        
        // Create and show the Bootstrap modal
        // data-bs-backdrop="static" in HTML prevents closing by clicking outside
        const resultsModal = document.getElementById('resultsModal');
        const modal = new bootstrap.Modal(resultsModal, {
            backdrop: 'static',  // Prevent closing by clicking outside
            keyboard: false      // Prevent closing with Escape key
        });
        modal.show();
    }
});
