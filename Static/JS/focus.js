/**
 * Focus Session Timer JavaScript
 * ==============================
 * Handles the study timer logic, including:
 * - Pomodoro, Short Break, and Long Break modes
 * - Countdown management
 * - Visual progress tracking
 * - Sound/Notifications
 */

$(document).ready(function () {
    // Timer State
    let timerInterval = null;
    let timeLeft = 0; // In seconds
    let currentMode = 'pomodoro';
    let isRunning = false;
    let initialTime = 0;

    // Timer Settings from DOM
    const $focusCard = $('.focus-card');
    const sessionLength = parseInt($focusCard.data('session-length')) || 25;
    const breakLong = parseInt($focusCard.data('break-long')) || 15;

    // Mode Durations (in minutes)
    const MODES = {
        'pomodoro': sessionLength,
        'short_break': 5,
        'long_break': breakLong
    };

    // Descriptions
    const MODE_DESCRIPTIONS = {
        'pomodoro': `Stay focused for ${sessionLength} minutes`,
        'short_break': 'Refresh for 5 minutes',
        'long_break': `Take a deep ${breakLong}-minute rest`
    };

    // DOM Elements
    const $timerDisplay = $('#timerDisplay');
    const $startBtn = $('#startTimerBtn');
    const $pauseBtn = $('#pauseTimerBtn');
    const $resetBtn = $('#resetTimerBtn');
    const $modeButtons = $('.focus-mode-btn');
    const $progressBar = $('#timerProgressBar');

    /**
     * Initialize the timer with a specific mode
     * @param {string} mode - The mode key from MODES
     */
    function initTimer(mode) {
        clearInterval(timerInterval);
        isRunning = false;
        currentMode = mode;
        timeLeft = MODES[mode] * 60;
        initialTime = timeLeft;

        updateDisplay();
        updateUI();

        $startBtn.show();
        $pauseBtn.hide();
    }

    /**
     * Format time and update the display
     */
    function updateDisplay() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        const formattedTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        $timerDisplay.text(formattedTime);

        // Update document title to show countdown
        if (isRunning) {
            document.title = `(${formattedTime}) Focus Flow`;
        } else {
            document.title = 'Dashboard • Focus Flow';
        }

        // Update progress bar
        const progress = ((initialTime - timeLeft) / initialTime) * 100;
        $progressBar.css('width', progress + '%');
    }

    /**
     * Update UI elements based on current mode
     */
    function updateUI() {
        $modeButtons.removeClass('active');
        $(`.focus-mode-btn[data-mode="${currentMode}"]`).addClass('active');

        // Update mode description
        $('#modeDescription').text(MODE_DESCRIPTIONS[currentMode]);
    }

    /**
     * Start the countdown
     */
    function startTimer() {
        if (isRunning) return;

        isRunning = true;
        $startBtn.hide();
        $pauseBtn.show();

        timerInterval = setInterval(() => {
            timeLeft--;
            updateDisplay();

            if (timeLeft <= 0) {
                completeSession();
            }
        }, 1000);
    }

    /**
     * Pause the countdown
     */
    function pauseTimer() {
        clearInterval(timerInterval);
        isRunning = false;
        $startBtn.show();
        $pauseBtn.hide();
        document.title = 'Dashboard • Focus Flow';
    }

    /**
     * Reset the timer to initial state
     */
    function resetTimer() {
        initTimer(currentMode);
    }

    /**
     * Handle session completion
     */
    function completeSession() {
        clearInterval(timerInterval);
        isRunning = false;

        // Simple alert (could be replaced with a sound or custom modal)
        alert(`${currentMode === 'pomodoro' ? 'Focus Session' : 'Break'} complete!`);

        // Record session to backend (if endpoint exists)
        if (currentMode === 'pomodoro') {
            logSession();
        }

        resetTimer();
    }

    /**
     * Log the completed session to the backend
     */
    function logSession() {
        const csrfToken = $('meta[name="csrf-token"]').attr('content');
        const taskId = $('#timerTaskId').val() || null;

        fetch('/api/focus/log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                mode: currentMode,
                duration: MODES[currentMode],
                taskId: taskId
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Session logged successfully');
                    // Refresh tasks list and stats if a task was completed
                    if (taskId && window.DashboardTasks) {
                        window.DashboardTasks.fetchTasks();
                    }
                    // Refresh streak display if it changed
                    if (data.streak !== undefined) {
                        $('.streak-days').text(data.streak + ' days');
                    }
                }
            })
            .catch(err => console.error('Error logging session:', err));
    }

    // Event Listeners
    $startBtn.on('click', startTimer);
    $pauseBtn.on('click', pauseTimer);
    $resetBtn.on('click', resetTimer);

    $modeButtons.on('click', function () {
        const mode = $(this).data('mode');
        if (confirm('Change mode? Current progress will be lost.')) {
            initTimer(mode);
        }
    });

    // Initialize with Pomodoro
    initTimer('pomodoro');
});
