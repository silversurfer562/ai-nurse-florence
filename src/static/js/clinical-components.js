/**
 * AI Nurse Florence - Clinical React Components
 * Following Conditional Imports Pattern from coding instructions
 * Graceful degradation when React unavailable
 */

// Conditional React loading following coding instructions pattern
const hasReact = typeof React !== 'undefined' && typeof ReactDOM !== 'undefined';

/**
 * Clinical Decision Support Widget
 * Main component for evidence-based nursing interventions
 */
class ClinicalDecisionWidget {
    constructor(container, apiBase = '/api/v1') {
        this.container = container;
        this.apiBase = apiBase;
        this.init();
    }

    async init() {
        if (hasReact) {
            this.renderReactComponent();
        } else {
            this.renderFallbackForm();
        }
    }

    renderReactComponent() {
        // TODO: Implement React-based clinical decision widget
        // TODO: Add form validation and state management
        // TODO: Integrate with clinical decision support API

        const placeholder = React.createElement('div', { className: 'clinical-widget' },
            React.createElement('h3', null, 'Evidence-Based Nursing Interventions'),
            React.createElement('p', null, 'TODO: Implement React clinical decision widget')
        );

        ReactDOM.render(placeholder, this.container);
    }

    renderFallbackForm() {
        // Graceful degradation following coding instructions pattern
        this.container.innerHTML = `
            <div class="clinical-widget">
                <h3>Evidence-Based Nursing Interventions</h3>
                <p><em>Enhanced React interface loading... Using simplified form.</em></p>

                <form id="clinical-form">
                    <input type="text" placeholder="Patient condition" required>
                    <select>
                        <option value="moderate">Moderate Severity</option>
                        <option value="severe">Severe</option>
                    </select>
                    <button type="submit">Get Interventions</button>
                </form>

                <div class="clinical-disclaimer">
                    Educational use only - not medical advice. Clinical judgment required.
                </div>
            </div>
        `;

        // TODO: Add form submission handler
        // TODO: Integrate with API endpoints
        // TODO: Display results in fallback format
    }
}

/**
 * SBAR Wizard Component
 * Multi-step workflow for clinical communication
 */
class SBARWizard {
    constructor(container, apiBase = '/api/v1') {
        this.container = container;
        this.apiBase = apiBase;
        this.init();
    }

    async init() {
        if (hasReact) {
            this.renderReactWizard();
        } else {
            this.renderFallbackWizard();
        }
    }

    renderReactWizard() {
        // TODO: Implement React SBAR wizard
        // TODO: Multi-step form with progress indicator
        // TODO: Situation, Background, Assessment, Recommendation steps

        const placeholder = React.createElement('div', { className: 'sbar-wizard' },
            React.createElement('h3', null, 'SBAR Report Wizard'),
            React.createElement('p', null, 'TODO: Implement React SBAR wizard')
        );

        ReactDOM.render(placeholder, this.container);
    }

    renderFallbackWizard() {
        // Fallback SBAR form
        this.container.innerHTML = `
            <div class="sbar-wizard">
                <h3>SBAR Report Generation</h3>
                <p><em>Multi-step wizard requires enhanced interface.</em></p>

                <form>
                    <textarea placeholder="Situation" rows="3"></textarea>
                    <textarea placeholder="Background" rows="3"></textarea>
                    <textarea placeholder="Assessment" rows="3"></textarea>
                    <textarea placeholder="Recommendation" rows="3"></textarea>
                    <button type="submit">Generate SBAR Report</button>
                </form>
            </div>
        `;

        // TODO: Add SBAR generation logic
        // TODO: Format report output
        // TODO: Clinical validation
    }
}

// Initialize components when DOM is ready following coding instructions
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Clinical Decision Widgets
    const clinicalWidgets = document.querySelectorAll('[data-clinical-widget="decision-support"]');
    clinicalWidgets.forEach(widget => {
        new ClinicalDecisionWidget(widget);
    });

    // Initialize SBAR Wizards
    const sbarWizards = document.querySelectorAll('[data-clinical-widget="sbar-wizard"]');
    sbarWizards.forEach(wizard => {
        new SBARWizard(wizard);
    });

    // Log React availability for debugging
    console.log('AI Nurse Florence Clinical Components initialized');
    console.log('React available:', hasReact);
});

// Mobile-responsive component behavior
class MobileResponsiveHandler {
    constructor() {
        this.isMobile = window.innerWidth <= 768;
        this.touchStartX = 0;
        this.touchEndX = 0;
        this.init();
    }

    init() {
        // Listen for window resize to update mobile state
        window.addEventListener('resize', () => {
            this.isMobile = window.innerWidth <= 768;
            this.updateComponentsForMobile();
        });

        // Add touch gesture support
        this.addTouchGestures();

        // Initialize mobile-optimized components
        this.updateComponentsForMobile();
    }

    addTouchGestures() {
        // Swipe navigation for mobile
        document.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        });

        document.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipeGesture();
        });
    }

    handleSwipeGesture() {
        const swipeThreshold = 50;
        const diff = this.touchStartX - this.touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left - next section
                this.navigateToNextSection();
            } else {
                // Swipe right - previous section
                this.navigateToPreviousSection();
            }
        }
    }

    navigateToNextSection() {
        const tabs = document.querySelectorAll('.nav-tab, .tab-btn');
        const activeTab = document.querySelector('.nav-tab.active, .tab-btn.active');
        if (activeTab && tabs.length > 1) {
            const currentIndex = Array.from(tabs).indexOf(activeTab);
            const nextTab = tabs[currentIndex + 1] || tabs[0];
            nextTab.click();
        }
    }

    navigateToPreviousSection() {
        const tabs = document.querySelectorAll('.nav-tab, .tab-btn');
        const activeTab = document.querySelector('.nav-tab.active, .tab-btn.active');
        if (activeTab && tabs.length > 1) {
            const currentIndex = Array.from(tabs).indexOf(activeTab);
            const prevTab = tabs[currentIndex - 1] || tabs[tabs.length - 1];
            prevTab.click();
        }
    }

    updateComponentsForMobile() {
        // Adjust chat interface for mobile
        this.optimizeChatForMobile();

        // Optimize forms for mobile
        this.optimizeFormsForMobile();

        // Adjust modals for mobile
        this.optimizeModalsForMobile();
    }

    optimizeChatForMobile() {
        const chatContainer = document.getElementById('chatMessages');
        if (chatContainer && this.isMobile) {
            chatContainer.style.height = 'calc(100vh - 200px)';

            // Add pull-to-refresh for chat
            let startY = 0;
            chatContainer.addEventListener('touchstart', (e) => {
                startY = e.touches[0].pageY;
            });

            chatContainer.addEventListener('touchmove', (e) => {
                const currentY = e.touches[0].pageY;
                if (currentY > startY + 50 && chatContainer.scrollTop === 0) {
                    // Trigger refresh
                    this.refreshChat();
                }
            });
        }
    }

    optimizeFormsForMobile() {
        if (this.isMobile) {
            // Increase input sizes for better touch interaction
            const inputs = document.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                if (!input.style.minHeight) {
                    input.style.minHeight = '44px';
                }
            });

            // Add autocomplete off for better mobile experience
            const textInputs = document.querySelectorAll('input[type="text"], input[type="email"]');
            textInputs.forEach(input => {
                input.setAttribute('autocomplete', 'off');
                input.setAttribute('autocorrect', 'off');
                input.setAttribute('autocapitalize', 'off');
            });
        }
    }

    optimizeModalsForMobile() {
        const modals = document.querySelectorAll('.modal, [role="dialog"]');
        modals.forEach(modal => {
            if (this.isMobile) {
                modal.style.width = '95vw';
                modal.style.height = 'auto';
                modal.style.maxHeight = '90vh';
                modal.style.overflow = 'auto';
            }
        });
    }

    refreshChat() {
        // Implement chat refresh logic
        console.log('Refreshing chat...');
    }
}

// Initialize mobile responsive handler
const mobileHandler = new MobileResponsiveHandler();

// TODO: Add error handling for component failures
// TODO: Implement progressive enhancement patterns
// TODO: Add accessibility features (WCAG compliance)
