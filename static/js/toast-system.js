/**
 * Toast Notification System
 * A modern, animated toast notification system for Django applications
 */

class ToastManager {
    constructor() {
        this.container = null;
        this.toasts = [];
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }

        // Load Django messages on page load
        document.addEventListener('DOMContentLoaded', () => {
            this.loadDjangoMessages();
        });
    }

    /**
     * Load and display Django messages from the hidden div
     */
    loadDjangoMessages() {
        const messagesDiv = document.getElementById('django-messages');
        if (!messagesDiv) return;

        const messagesData = messagesDiv.getAttribute('data-messages');
        if (!messagesData) return;

        try {
            const messages = JSON.parse(messagesData);
            messages.forEach(msg => {
                // Map Django message tags to toast types
                let type = msg.tags || 'info';
                // Handle Django's default tags
                if (type === 'error') type = 'error';
                else if (type === 'warning') type = 'warning';
                else if (type === 'success') type = 'success';
                else if (type === 'info') type = 'info';
                else if (type === 'debug') type = 'info';
                
                this.show(msg.message, type, 5000);
            });
        } catch (e) {
            console.error('Error parsing Django messages:', e);
        }
    }

    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - Toast type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in milliseconds (default: 3000)
     * @param {object} action - Optional action button { label: string, onClick: function }
     */
    show(message, type = 'info', duration = 3000, action = null) {
        const toast = this.createToast(message, type, duration, action);
        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Trigger animation
        setTimeout(() => {
            toast.classList.add('toast-show');
        }, 10);

        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => {
                this.dismiss(toast);
            }, duration);
        }

        return toast;
    }

    /**
     * Create a toast element
     */
    createToast(message, type, duration, action) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        // Get icon based on type
        const icon = this.getIcon(type);

        // Create toast content
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-message">${this.escapeHtml(message)}</div>
                ${action ? `<button class="toast-action-btn">${this.escapeHtml(action.label)}</button>` : ''}
            </div>
            <button class="toast-close" aria-label="Close">&times;</button>
            ${duration > 0 ? '<div class="toast-progress"></div>' : ''}
        `;

        // Add close button handler
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            this.dismiss(toast);
        });

        // Add action button handler
        if (action && action.onClick) {
            const actionBtn = toast.querySelector('.toast-action-btn');
            actionBtn.addEventListener('click', () => {
                action.onClick();
                this.dismiss(toast);
            });
        }

        // Animate progress bar
        if (duration > 0) {
            const progressBar = toast.querySelector('.toast-progress');
            progressBar.style.animation = `toast-progress ${duration}ms linear`;
        }

        return toast;
    }

    /**
     * Get icon for toast type
     */
    getIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    /**
     * Dismiss a toast
     */
    dismiss(toast) {
        toast.classList.add('toast-hide');
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            const index = this.toasts.indexOf(toast);
            if (index > -1) {
                this.toasts.splice(index, 1);
            }
        }, 300);
    }

    /**
     * Dismiss all toasts
     */
    dismissAll() {
        this.toasts.forEach(toast => {
            this.dismiss(toast);
        });
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Convenience methods
     */
    success(message, duration = 3000, action = null) {
        return this.show(message, 'success', duration, action);
    }

    error(message, duration = 5000, action = null) {
        return this.show(message, 'error', duration, action);
    }

    warning(message, duration = 4000, action = null) {
        return this.show(message, 'warning', duration, action);
    }

    info(message, duration = 3000, action = null) {
        return this.show(message, 'info', duration, action);
    }
}

// Create global instance
window.ToastManager = new ToastManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ToastManager;
}

// Made with Bob
