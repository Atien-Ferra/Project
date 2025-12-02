$(document).ready(function() {
    // Initialize progress
    updateProgress();

    // File upload handling - submit form on file selection
    $('#fileUpload').on('change', function() {
        const file = this.files[0];
        if (file) {
            // Check file type
            const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                                 'text/plain', 'image/png', 'image/jpeg', 'image/gif'];
            if (!allowedTypes.includes(file.type)) {
                alert('Invalid file type. Please upload PDF, DOCX, TXT, or image files.');
                return;
            }
            
            // Submit the form
            $('#uploadForm').submit();
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

 const openBtn = document.getElementById("openTaskModal");
  const modal = document.getElementById("taskModal");
  const backdrop = document.getElementById("taskModalBackdrop");
  const closeBtn = document.getElementById("closeTaskModal");
  const cancelBtn = document.getElementById("cancelTaskModal");
  const newTask = document.getElementById("newTask");
  const taskTitleInput = document.getElementById("taskTitleInput");

  function openModal(prefill) {
    modal.style.display = "grid";
    backdrop.style.display = "block";
    if (prefill) taskTitleInput.value = prefill;
    taskTitleInput.focus();
  }
  function closeModal() {
    modal.style.display = "none";
    backdrop.style.display = "none";
  }

  openBtn.addEventListener("click", () => openModal(newTask.value.trim()));
  document.getElementById("addFirstTask")?.addEventListener("click", () => openModal(""));

  closeBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);
  backdrop.addEventListener("click", closeModal);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });