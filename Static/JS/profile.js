/**
 * Profile Page JavaScript
 * =======================
 * This file handles the user profile page functionality:
 * - Toggling between view and edit modes for study preferences
 * - Saving updated preferences via AJAX
 * - CSRF token handling for secure form submission
 * 
 * Study Preferences:
 * - Session Length: How long each study session should be (minutes)
 * - Break Length: How long breaks should be (minutes)
 * - Preferred Difficulty: Easy/Medium/Hard quiz difficulty
 */

$(document).ready(function() {
    
    // ============================================
    // CSRF TOKEN HANDLING
    // ============================================
    
    /**
     * Get CSRF token from the page
     * Required for POST requests to pass Flask-WTF validation
     * 
     * @returns {string} The CSRF token value
     */
    function getCsrfToken() {
        // Try form hidden input first
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
    // ELEMENT REFERENCES
    // ============================================
    
    // Buttons for controlling edit mode
    const editButton = $("#editButton");      // Triggers edit mode
    const saveButton = $("#saveButton");      // Saves changes
    const cancelButton = $("#cancelButton");  // Cancels edit mode
    
    // Session Length elements (view text and edit input)
    const sessionLengthText = $("#sessionLengthText");
    const sessionLengthInput = $("#sessionLengthInput");
    
    // Break Length elements (view text and edit input)
    const breakLengthText = $("#breakLengthText");
    const breakLengthInput = $("#breakLengthInput");
    
    // Difficulty elements (view text and edit select dropdown)
    const preferredDifficultyText = $("#preferredDifficultyText");
    const preferredDifficultyInput = $("#preferredDifficultyInput");

    // ============================================
    // EDIT MODE TOGGLE
    // ============================================
    
    /**
     * Enter edit mode
     * - Hides text displays
     * - Shows input fields
     * - Shows Save/Cancel buttons
     */
    editButton.on("click", function() {
        // Hide text displays, show inputs for session length
        sessionLengthText.addClass("d-none");
        sessionLengthInput.removeClass("d-none");
        
        // Hide text displays, show inputs for break length
        breakLengthText.addClass("d-none");
        breakLengthInput.removeClass("d-none");
        
        // Hide text displays, show inputs for difficulty
        preferredDifficultyText.addClass("d-none");
        preferredDifficultyInput.removeClass("d-none");
        
        // Toggle button visibility
        editButton.addClass("d-none");
        saveButton.removeClass("d-none");
        cancelButton.removeClass("d-none");
    });

    /**
     * Cancel edit mode (discard changes)
     * - Hides input fields
     * - Shows text displays (with original values)
     * - Shows Edit button
     */
    cancelButton.on("click", function() {
        // Reset input values to original text values
        sessionLengthInput.val(parseInt(sessionLengthText.text()));
        breakLengthInput.val(parseInt(breakLengthText.text()));
        
        // Hide inputs, show text displays
        sessionLengthInput.addClass("d-none");
        sessionLengthText.removeClass("d-none");
        
        breakLengthInput.addClass("d-none");
        breakLengthText.removeClass("d-none");
        
        preferredDifficultyInput.addClass("d-none");
        preferredDifficultyText.removeClass("d-none");
        
        // Toggle button visibility
        editButton.removeClass("d-none");
        saveButton.addClass("d-none");
        cancelButton.addClass("d-none");
    });

    // ============================================
    // FORM SUBMISSION
    // ============================================
    
    /**
     * Handle profile update form submission
     * Sends preferences to server via AJAX POST request
     */
    $("#update-profile-form").on("submit", function(event) {
        // Prevent default form submission (page reload)
        event.preventDefault();
        
        // Get CSRF token
        const csrfToken = getCsrfToken();
        
        // Serialize form data (includes all input fields)
        const formData = $(this).serialize();
        
        // Show loading state on save button
        const originalSaveText = saveButton.html();
        saveButton.html('<span class="spinner-border spinner-border-sm me-1"></span> Saving...');
        saveButton.prop('disabled', true);
        
        /**
         * Send AJAX request to update preferences
         * 
         * The server expects:
         * - studyPrefs.sessionLengthMins: number
         * - studyPrefs.breakLongMins: number
         * - studyPrefs.preferredDifficulty: "easy" | "medium" | "hard"
         */
        $.ajax({
            url: "/profile",
            method: "POST",
            data: formData,
            headers: {
                'X-CSRFToken': csrfToken  // CSRF protection
            },
            success: function(response) {
                // Update text displays with new values
                sessionLengthText
                    .text(sessionLengthInput.val() + " minutes")
                    .removeClass("d-none");
                sessionLengthInput.addClass("d-none");
                
                breakLengthText
                    .text(breakLengthInput.val() + " minutes")
                    .removeClass("d-none");
                breakLengthInput.addClass("d-none");
                
                // Get the display text for selected difficulty
                const selectedDifficulty = preferredDifficultyInput.find(":selected").text();
                preferredDifficultyText
                    .text(selectedDifficulty)
                    .removeClass("d-none");
                preferredDifficultyInput.addClass("d-none");
                
                // Toggle button visibility back to view mode
                editButton.removeClass("d-none");
                saveButton.addClass("d-none");
                cancelButton.addClass("d-none");
                
                // Show success message (optional)
                showToast('Preferences saved successfully!', 'success');
            },
            error: function(xhr, status, error) {
                console.error('Error updating preferences:', error);
                alert("An error occurred while updating preferences. Please try again.");
            },
            complete: function() {
                // Reset save button state
                saveButton.html(originalSaveText);
                saveButton.prop('disabled', false);
            }
        });
    });
    
    // ============================================
    // UTILITY FUNCTIONS
    // ============================================
    
    /**
     * Show a toast notification
     * Creates a Bootstrap toast with the given message
     * 
     * @param {string} message - Message to display
     * @param {string} type - 'success', 'error', or 'info'
     */
    function showToast(message, type) {
        const bgClass = type === 'success' ? 'bg-success' : 
                        type === 'error' ? 'bg-danger' : 'bg-info';
        
        const toast = `
            <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1100;">
                <div class="toast show ${bgClass} text-white" role="alert">
                    <div class="toast-body d-flex justify-content-between align-items-center">
                        ${message}
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(toast);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            $('.toast-container').fadeOut(300, function() {
                $(this).remove();
            });
        }, 3000);
    }
});
