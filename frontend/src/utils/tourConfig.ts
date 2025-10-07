/**
 * Shared configuration for react-joyride tours across all wizards
 * Ensures consistent accessibility and UX
 */

export const tourConfig = {
  // Show progress indicator
  showProgress: true,

  // Show skip button
  showSkipButton: true,

  // Continue through steps
  continuous: true,

  // Custom button labels for clarity
  locale: {
    back: 'Back',
    close: 'Close',
    last: 'Finish',
    next: 'Next',
    skip: 'Skip tour',
  },

  // Consistent styling
  styles: {
    options: {
      primaryColor: '#d4af37', // Accent gold color
      zIndex: 10000,
      arrowColor: '#fff',
    },
    buttonNext: {
      outline: 'none',
      backgroundColor: '#d4af37',
    },
    buttonBack: {
      outline: 'none',
      marginRight: '10px',
    },
    buttonSkip: {
      color: '#6b7280',
    },
  },
};

/**
 * Accessibility-enhanced Quick Start button props
 */
export const getQuickStartButtonProps = (wizardName: string, showPulse: boolean = false) => ({
  className: `help-button px-3 py-2 bg-accent-500 text-white rounded-lg hover:bg-accent-600 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2 transition-all text-sm ${
    showPulse ? 'animate-pulse' : ''
  }`,
  title: 'Quick tour - Press ESC anytime to exit, use arrow keys to navigate',
  'aria-label': `Start quick tour of ${wizardName} (use arrow keys to navigate, ESC to exit)`,
});
