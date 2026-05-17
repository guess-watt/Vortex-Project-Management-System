/**
 * Professional Dark Mode Theme System
 * Handles theme switching, localStorage persistence, and Chart.js integration
 */

(function() {
    'use strict';

    const THEME_KEY = 'theme';
    const THEME_DARK = 'dark';
    const THEME_LIGHT = 'light';
    const THEME_EVENT = 'themeChanged';

    /**
     * Get the current theme from localStorage or system preference
     * @returns {string} 'dark' or 'light'
     */
    function getTheme() {
        // Check localStorage first
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme === THEME_DARK || savedTheme === THEME_LIGHT) {
            return savedTheme;
        }

        // Fall back to system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return THEME_DARK;
        }

        return THEME_LIGHT;
    }

    /**
     * Apply theme to the document
     * @param {string} theme - 'dark' or 'light'
     */
    function applyTheme(theme) {
        const html = document.documentElement;
        
        if (theme === THEME_DARK) {
            html.setAttribute('data-theme', THEME_DARK);
        } else {
            html.removeAttribute('data-theme');
        }

        // Save to localStorage
        localStorage.setItem(THEME_KEY, theme);

        // Update toggle button icon if it exists
        updateToggleButton(theme);

        // Dispatch custom event for Chart.js and other components
        const event = new CustomEvent(THEME_EVENT, {
            detail: { theme: theme }
        });
        window.dispatchEvent(event);
    }

    /**
     * Update the theme toggle button icon
     * @param {string} theme - Current theme
     */
    function updateToggleButton(theme) {
        const toggleButton = document.getElementById('theme-toggle');
        if (toggleButton) {
            if (theme === THEME_DARK) {
                toggleButton.innerHTML = '☀️';
                toggleButton.setAttribute('aria-label', 'Switch to light mode');
                toggleButton.setAttribute('title', 'Switch to light mode');
            } else {
                toggleButton.innerHTML = '🌙';
                toggleButton.setAttribute('aria-label', 'Switch to dark mode');
                toggleButton.setAttribute('title', 'Switch to dark mode');
            }
        }
    }

    /**
     * Toggle between dark and light themes
     */
    function toggleTheme() {
        const currentTheme = getTheme();
        const newTheme = currentTheme === THEME_DARK ? THEME_LIGHT : THEME_DARK;
        applyTheme(newTheme);
    }

    /**
     * Initialize theme system
     */
    function initTheme() {
        // Apply initial theme
        const theme = getTheme();
        applyTheme(theme);

        // Set up toggle button click handler
        const toggleButton = document.getElementById('theme-toggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', toggleTheme);
        }

        // Listen for system theme changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            // Modern browsers
            if (mediaQuery.addEventListener) {
                mediaQuery.addEventListener('change', (e) => {
                    // Only update if user hasn't manually set a preference
                    if (!localStorage.getItem(THEME_KEY)) {
                        applyTheme(e.matches ? THEME_DARK : THEME_LIGHT);
                    }
                });
            } 
            // Older browsers
            else if (mediaQuery.addListener) {
                mediaQuery.addListener((e) => {
                    if (!localStorage.getItem(THEME_KEY)) {
                        applyTheme(e.matches ? THEME_DARK : THEME_LIGHT);
                    }
                });
            }
        }
    }

    /**
     * Get Chart.js color scheme based on current theme
     * @returns {object} Color configuration for Chart.js
     */
    function getChartColors() {
        const theme = getTheme();
        
        if (theme === THEME_DARK) {
            return {
                textColor: '#e0e0e0',
                gridColor: 'rgba(224, 224, 224, 0.1)',
                backgroundColor: [
                    'rgba(74, 144, 226, 0.6)',
                    'rgba(40, 167, 69, 0.6)',
                    'rgba(255, 193, 7, 0.6)',
                    'rgba(220, 53, 69, 0.6)',
                    'rgba(13, 202, 240, 0.6)',
                    'rgba(108, 117, 125, 0.6)',
                    'rgba(111, 66, 193, 0.6)',
                    'rgba(253, 126, 20, 0.6)'
                ],
                borderColor: [
                    'rgba(74, 144, 226, 1)',
                    'rgba(40, 167, 69, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)',
                    'rgba(13, 202, 240, 1)',
                    'rgba(108, 117, 125, 1)',
                    'rgba(111, 66, 193, 1)',
                    'rgba(253, 126, 20, 1)'
                ]
            };
        } else {
            return {
                textColor: '#212529',
                gridColor: 'rgba(0, 0, 0, 0.1)',
                backgroundColor: [
                    'rgba(13, 110, 253, 0.6)',
                    'rgba(25, 135, 84, 0.6)',
                    'rgba(255, 193, 7, 0.6)',
                    'rgba(220, 53, 69, 0.6)',
                    'rgba(13, 202, 240, 0.6)',
                    'rgba(108, 117, 125, 0.6)',
                    'rgba(111, 66, 193, 0.6)',
                    'rgba(253, 126, 20, 0.6)'
                ],
                borderColor: [
                    'rgba(13, 110, 253, 1)',
                    'rgba(25, 135, 84, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)',
                    'rgba(13, 202, 240, 1)',
                    'rgba(108, 117, 125, 1)',
                    'rgba(111, 66, 193, 1)',
                    'rgba(253, 126, 20, 1)'
                ]
            };
        }
    }

    /**
     * Update Chart.js default colors based on theme
     */
    function updateChartDefaults() {
        // Check if Chart.js is loaded
        if (typeof Chart !== 'undefined') {
            const colors = getChartColors();
            
            // Update Chart.js defaults
            Chart.defaults.color = colors.textColor;
            Chart.defaults.borderColor = colors.gridColor;
            
            // Update scale defaults
            if (Chart.defaults.scale) {
                Chart.defaults.scale.grid.color = colors.gridColor;
                Chart.defaults.scale.ticks.color = colors.textColor;
            }
        }
    }

    // Initialize theme when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }

    // Update Chart.js defaults when theme changes
    window.addEventListener(THEME_EVENT, updateChartDefaults);

    // Export functions for external use
    window.themeSystem = {
        getTheme: getTheme,
        applyTheme: applyTheme,
        toggleTheme: toggleTheme,
        getChartColors: getChartColors,
        THEME_DARK: THEME_DARK,
        THEME_LIGHT: THEME_LIGHT,
        THEME_EVENT: THEME_EVENT
    };

})();

/**
 * Helper function to create a Chart.js chart with theme support
 * Usage: createThemedChart(ctx, config)
 * 
 * Example:
 * const ctx = document.getElementById('myChart').getContext('2d');
 * const chart = createThemedChart(ctx, {
 *     type: 'bar',
 *     data: { ... },
 *     options: { ... }
 * });
 */
function createThemedChart(ctx, config) {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return null;
    }

    // Apply theme colors to the config
    const colors = window.themeSystem.getChartColors();
    
    // Apply colors to datasets if they exist
    if (config.data && config.data.datasets) {
        config.data.datasets.forEach((dataset, index) => {
            if (!dataset.backgroundColor) {
                dataset.backgroundColor = colors.backgroundColor[index % colors.backgroundColor.length];
            }
            if (!dataset.borderColor) {
                dataset.borderColor = colors.borderColor[index % colors.borderColor.length];
            }
        });
    }

    // Create the chart
    const chart = new Chart(ctx, config);

    // Listen for theme changes and update the chart
    window.addEventListener(window.themeSystem.THEME_EVENT, function() {
        const newColors = window.themeSystem.getChartColors();
        
        // Update dataset colors
        if (chart.data && chart.data.datasets) {
            chart.data.datasets.forEach((dataset, index) => {
                dataset.backgroundColor = newColors.backgroundColor[index % newColors.backgroundColor.length];
                dataset.borderColor = newColors.borderColor[index % newColors.borderColor.length];
            });
        }

        // Update chart options
        if (chart.options.scales) {
            Object.keys(chart.options.scales).forEach(scaleKey => {
                const scale = chart.options.scales[scaleKey];
                if (scale.ticks) {
                    scale.ticks.color = newColors.textColor;
                }
                if (scale.grid) {
                    scale.grid.color = newColors.gridColor;
                }
            });
        }

        // Update legend colors
        if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
            chart.options.plugins.legend.labels.color = newColors.textColor;
        }

        // Update the chart
        chart.update();
    });

    return chart;
}

// Made with Bob
