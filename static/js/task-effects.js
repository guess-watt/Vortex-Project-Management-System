/**
 * Task Completion Effects System
 * Handles confetti animations, success messages, and sound effects when tasks are completed
 */

(function() {
    'use strict';

    // Track completed tasks in this session to prevent duplicate confetti
    const completedInSession = new Set();

    // Sound toggle state (stored in localStorage)
    let soundEnabled = localStorage.getItem('taskSoundEnabled') !== 'false';

    /**
     * Initialize the task effects system
     */
    function init() {
        updateSoundToggleButton();
        setupSoundToggle();
        setupTaskStatusHandlers();
    }

    /**
     * Setup sound toggle button functionality
     */
    function setupSoundToggle() {
        const soundToggle = document.getElementById('sound-toggle');
        if (soundToggle) {
            soundToggle.addEventListener('click', function() {
                soundEnabled = !soundEnabled;
                localStorage.setItem('taskSoundEnabled', soundEnabled);
                updateSoundToggleButton();
            });
        }
    }

    /**
     * Update sound toggle button icon
     */
    function updateSoundToggleButton() {
        const soundToggle = document.getElementById('sound-toggle');
        if (soundToggle) {
            soundToggle.textContent = soundEnabled ? '🔔' : '🔕';
            soundToggle.setAttribute('aria-label', soundEnabled ? 'Disable sound' : 'Enable sound');
        }
    }

    /**
     * Setup task status change handlers (checkboxes and dropdowns)
     */
    function setupTaskStatusHandlers() {
        // Handle checkbox changes (for task lists)
        document.addEventListener('change', function(e) {
            if (e.target.classList.contains('task-status-checkbox')) {
                handleTaskStatusChange(e.target);
            }
        });

        // Handle dropdown changes (for task detail views)
        document.addEventListener('change', function(e) {
            if (e.target.classList.contains('task-status-dropdown')) {
                handleTaskStatusChange(e.target);
            }
        });
    }

    /**
     * Handle task status change via AJAX
     */
    function handleTaskStatusChange(element) {
        const taskId = element.dataset.taskId;
        const newStatus = element.type === 'checkbox' 
            ? (element.checked ? 'done' : 'not_started')
            : element.value;
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value 
            || getCookie('csrftoken');

        // Send AJAX request
        fetch(`/tasks/${taskId}/update-status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `status=${newStatus}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Trigger effects if status is 'done' and not already completed in this session
                if (newStatus === 'done' && !completedInSession.has(taskId)) {
                    completedInSession.add(taskId);
                    triggerCompletionEffects(element);
                }
                
                // Update UI
                updateTaskUI(element, newStatus, data.status);
            } else {
                console.error('Failed to update task status:', data.error);
                // Revert the change
                if (element.type === 'checkbox') {
                    element.checked = !element.checked;
                }
            }
        })
        .catch(error => {
            console.error('Error updating task status:', error);
            // Revert the change
            if (element.type === 'checkbox') {
                element.checked = !element.checked;
            }
        });
    }

    /**
     * Trigger all completion effects (confetti, message, sound, animation)
     */
    function triggerCompletionEffects(element) {
        // Fire confetti
        fireConfetti();
        
        // Show success message
        showSuccessMessage();
        
        // Play sound if enabled
        if (soundEnabled) {
            playSuccessSound();
        }
        
        // Animate the task card
        animateTaskCard(element);
    }

    /**
     * Fire confetti animation
     */
    function fireConfetti() {
        if (typeof confetti === 'undefined') {
            console.warn('Confetti library not loaded');
            return;
        }

        // Create a burst of confetti
        const count = 200;
        const defaults = {
            origin: { y: 0.7 },
            zIndex: 9999
        };

        function fire(particleRatio, opts) {
            confetti(Object.assign({}, defaults, opts, {
                particleCount: Math.floor(count * particleRatio)
            }));
        }

        // Multiple bursts for a more impressive effect
        fire(0.25, {
            spread: 26,
            startVelocity: 55,
        });
        fire(0.2, {
            spread: 60,
        });
        fire(0.35, {
            spread: 100,
            decay: 0.91,
            scalar: 0.8
        });
        fire(0.1, {
            spread: 120,
            startVelocity: 25,
            decay: 0.92,
            scalar: 1.2
        });
        fire(0.1, {
            spread: 120,
            startVelocity: 45,
        });
    }

    /**
     * Show floating success message
     */
    function showSuccessMessage() {
        const message = document.createElement('div');
        message.className = 'task-success-message';
        message.innerHTML = 'Task Completed! 🎉';
        document.body.appendChild(message);

        // Trigger animation
        setTimeout(() => {
            message.classList.add('show');
        }, 10);

        // Remove after animation
        setTimeout(() => {
            message.classList.remove('show');
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 2000);
    }

    /**
     * Play success sound using Web Audio API
     */
    function playSuccessSound() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            // Create a pleasant "ding" sound
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(600, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.2);
        } catch (error) {
            console.warn('Could not play success sound:', error);
        }
    }

    /**
     * Animate the task card with scale-up effect
     */
    function animateTaskCard(element) {
        // Find the closest task card/row
        const taskCard = element.closest('.task-card') 
            || element.closest('tr') 
            || element.closest('.list-group-item')
            || element.closest('.card');

        if (taskCard) {
            taskCard.classList.add('task-completed-animation');
            
            // Remove animation class after it completes
            setTimeout(() => {
                taskCard.classList.remove('task-completed-animation');
            }, 600);
        }
    }

    /**
     * Update task UI after status change
     */
    function updateTaskUI(element, newStatus, statusDisplay) {
        // Update badge if present
        const taskCard = element.closest('.task-card') 
            || element.closest('tr') 
            || element.closest('.list-group-item');

        if (taskCard) {
            const badge = taskCard.querySelector('.badge');
            if (badge) {
                // Remove old status classes
                badge.classList.remove('bg-success', 'bg-warning', 'bg-secondary');
                
                // Add new status class
                if (newStatus === 'done' || newStatus === 'completed') {
                    badge.classList.add('bg-success');
                } else if (newStatus === 'pending') {
                    badge.classList.add('bg-warning');
                } else {
                    badge.classList.add('bg-secondary');
                }
                
                // Update text
                badge.textContent = statusDisplay;
            }
        }
    }

    /**
     * Get CSRF token from cookie
     */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose public API for manual triggering if needed
    window.TaskEffects = {
        triggerCompletion: function(taskId) {
            if (!completedInSession.has(taskId)) {
                completedInSession.add(taskId);
                triggerCompletionEffects(null);
            }
        },
        setSoundEnabled: function(enabled) {
            soundEnabled = enabled;
            localStorage.setItem('taskSoundEnabled', enabled);
            updateSoundToggleButton();
        }
    };
})();

// Made with Bob
