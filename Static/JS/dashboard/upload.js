/**
 * File Upload Handling Module
 * ===========================
 * Handles file selection and validation for quiz generation.
 */

/**
 * Initialize file upload handling
 * Sets up event listener for file selection
 */
function initUpload() {
    /**
     * Handle file selection for quiz generation
     * When user selects a file:
     * 1. Validate the file type
     * 2. Auto-submit the form if valid
     */
    $('#fileUpload').on('change', function () {
        const file = this.files[0];

        if (file) {
            // Define allowed MIME types for quiz documents
            const allowedTypes = [
                'application/pdf',                                                    // PDF files
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // DOCX files
                'text/plain',                                                         // TXT files
                'image/png',                                                          // PNG images
                'image/jpeg',                                                         // JPEG images
                'image/gif'                                                           // GIF images
            ];

            // Check if file type is allowed
            if (!allowedTypes.includes(file.type)) {
                alert('Invalid file type. Please upload PDF, DOCX, TXT, or image files.');
                return;
            }

            // Submit the form to generate quiz
            // The server will extract text and generate questions
            $('#uploadForm').submit();
        }
    });
}

// Export for use by other modules
window.DashboardUpload = { initUpload };
