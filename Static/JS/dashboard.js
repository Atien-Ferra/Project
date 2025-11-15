$(document).ready(function() {
    // Initialize progress
    updateProgress();

    // File upload handling
    $('#fileUpload').on('change', function() {
        const file = this.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            $.ajax({
                url: '/dashboard',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    window.location.href = '/quiz';
                },
                error: function(xhr) {
                    alert('Error uploading file: ' + (xhr.responseJSON?.error || 'Unknown error'));
                }
            });
        }
    });

    // Add task functionality
    $('#addTaskBtn').on('click', function() {
        const taskText = $('#newTask').val().trim();
        if (taskText) {
            addTask(taskText);
            $('#newTask').val('');
            updateProgress();
        }
    });

    function addTask(text) {
        const taskId = 'task-' + Date.now();
        const taskHtml = `
            <div class="card mb-2 task-item" id="${taskId}">
                <div class="card-body py-2">
                    <div class="form-check">
                        <input class="form-check-input task-checkbox" type="checkbox" id="check-${taskId}">
                        <label class="form-check-label" for="check-${taskId}">${text}</label>
                        <button type="button" class="btn-close float-end delete-task" data-task-id="${taskId}"></button>
                    </div>
                </div>
            </div>
        `;
        $('#tasksContainer').append(taskHtml);
        
        // Add event listeners for new task
        $(`#check-${taskId}`).on('change', updateProgress);
        $(`.delete-task[data-task-id="${taskId}"]`).on('click', function() {
            $(`#${taskId}`).remove();
            updateProgress();
        });
    }

    function updateProgress() {
        const totalTasks = $('.task-item').length;
        const completedTasks = $('.task-checkbox:checked').length;
        const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
        
        $('.progress-bar').css('width', progress + '%').attr('aria-valuenow', progress);
        $('.progress-percent').text(Math.round(progress) + '%');
        $('.tasks-completed').text(`${completedTasks} of ${totalTasks} tasks completed`);
        
        // Update streak if all tasks completed
        if (completedTasks === totalTasks && totalTasks > 0) {
            updateStreak();
        }
    }

    function updateStreak() {
        // In a real app, this would call the backend
        const currentStreak = parseInt($('.streak-days').text()) || 0;
        $('.streak-days').text(currentStreak + 1 + ' days');
    }

    // Initialize empty state
    if ($('.task-item').length === 0) {
        $('.empty-state').show();
        $('.tasks-section').hide();
    }
});