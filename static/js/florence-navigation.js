/**
 * AI Nurse Florence - Unified Navigation System
 * Provides consistent navigation across all pages with breadcrumbs,
 * quick access menu, and mobile responsiveness.
 *
 * Usage: Include this file and call FlorenceNav.init() on page load
 */

const FlorenceNav = {
    // Navigation configuration - maps page filenames to display info
    pages: {
        'index.html': {
            title: 'Dashboard',
            icon: 'fa-home',
            category: 'main',
            breadcrumb: ['Dashboard']
        },
        'sbar-wizard-react.html': {
            title: 'SBAR Wizard (React)',
            icon: 'fa-react',
            category: 'wizards',
            breadcrumb: ['Dashboard', 'Wizards', 'SBAR (React)'],
            badge: 'NEW'
        },
        'sbar-wizard.html': {
            title: 'SBAR Wizard',
            icon: 'fa-comments-medical',
            category: 'wizards',
            breadcrumb: ['Dashboard', 'Wizards', 'SBAR']
        },
        'care-plan-wizard.html': {
            title: 'Care Plan Wizard',
            icon: 'fa-clipboard-check',
            category: 'wizards',
            breadcrumb: ['Dashboard', 'Wizards', 'Care Plan']
        },
        'drug-interactions.html': {
            title: 'Drug Interactions',
            icon: 'fa-pills',
            category: 'tools',
            breadcrumb: ['Dashboard', 'Tools', 'Drug Interactions']
        },
        'disease-lookup.html': {
            title: 'Disease Lookup',
            icon: 'fa-search-plus',
            category: 'tools',
            breadcrumb: ['Dashboard', 'Tools', 'Disease Lookup']
        },
        'dosage-calculator.html': {
            title: 'Dosage Calculator',
            icon: 'fa-calculator',
            category: 'wizards',
            breadcrumb: ['Dashboard', 'Wizards', 'Dosage Calculator']
        },
        'clinical-workspace.html': {
            title: 'Clinical Workspace',
            icon: 'fa-laptop-medical',
            category: 'tools',
            breadcrumb: ['Dashboard', 'Tools', 'Clinical Workspace']
        },
        'clinical-assessment-optimizer.html': {
            title: 'Assessment Optimizer',
            icon: 'fa-brain',
            category: 'tools',
            breadcrumb: ['Dashboard', 'Tools', 'Assessment Optimizer']
        },
        'chat.html': {
            title: 'Clinical Chat',
            icon: 'fa-comments',
            category: 'tools',
            breadcrumb: ['Dashboard', 'Tools', 'Clinical Chat']
        }
    },

    currentPage: null,
    quickMenuOpen: false,

    /**
     * Initialize navigation system
     */
    init() {
        this.currentPage = this.getCurrentPageName();
        this.injectNavigationBar();
        this.injectBreadcrumbs();
        this.injectQuickAccessMenu();
        this.setupKeyboardShortcuts();
        this.setupMobileMenu();
    },

    /**
     * Get current page filename
     */
    getCurrentPageName() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'index.html';
        return filename;
    },

    /**
     * Get page configuration
     */
    getPageConfig(pageName) {
        return this.pages[pageName] || {
            title: 'AI Nurse Florence',
            icon: 'fa-nurse',
            category: 'main',
            breadcrumb: ['Unknown']
        };
    },

    /**
     * Inject global navigation bar at top of page
     */
    injectNavigationBar() {
        const config = this.getPageConfig(this.currentPage);
        const isHomePage = this.currentPage === 'index.html';

        const navHTML = `
            <nav id="florenceGlobalNav" class="florence-nav-bar bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-lg sticky top-0 z-40">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex items-center justify-between h-14">
                        <!-- Logo and Title -->
                        <div class="flex items-center space-x-4">
                            ${!isHomePage ? `
                                <a href="index.html" class="flex items-center space-x-2 hover:opacity-80 transition-opacity" title="Return to Dashboard">
                                    <i class="fas fa-arrow-left text-sm"></i>
                                    <span class="hidden sm:inline text-sm font-medium">Dashboard</span>
                                </a>
                                <span class="text-blue-300">|</span>
                            ` : ''}
                            <div class="flex items-center space-x-2">
                                <i class="fas ${config.icon}"></i>
                                <span class="font-semibold">${config.title}</span>
                                ${config.badge ? `<span class="bg-yellow-400 text-blue-900 text-xs font-bold px-2 py-0.5 rounded-full">${config.badge}</span>` : ''}
                            </div>
                        </div>

                        <!-- Navigation Controls -->
                        <div class="flex items-center space-x-4">
                            <!-- Quick Access Button -->
                            <button
                                onclick="FlorenceNav.toggleQuickMenu()"
                                class="flex items-center space-x-2 px-3 py-1.5 bg-blue-500 hover:bg-blue-400 rounded-lg transition-colors"
                                title="Quick Access (Alt+N)"
                            >
                                <i class="fas fa-th"></i>
                                <span class="hidden md:inline text-sm">Tools</span>
                            </button>

                            <!-- Help Button -->
                            <button
                                onclick="FlorenceNav.openHelp()"
                                class="flex items-center space-x-2 px-3 py-1.5 bg-indigo-500 hover:bg-indigo-400 rounded-lg transition-colors"
                                title="Help (Shift+?)"
                            >
                                <i class="fas fa-question-circle"></i>
                                <span class="hidden md:inline text-sm">Help</span>
                            </button>

                            <!-- Mobile Menu Toggle -->
                            <button
                                onclick="FlorenceNav.toggleMobileMenu()"
                                class="md:hidden p-2 hover:bg-blue-500 rounded-lg"
                                id="florenceMobileMenuBtn"
                            >
                                <i class="fas fa-bars"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Mobile Menu (Hidden by default) -->
                <div id="florenceMobileMenu" class="hidden md:hidden bg-blue-700 border-t border-blue-500">
                    <div class="px-4 py-3 space-y-2">
                        <a href="index.html" class="block px-3 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                            <i class="fas fa-home mr-2"></i>Dashboard
                        </a>
                        <a href="sbar-wizard-react.html" class="block px-3 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                            <i class="fab fa-react mr-2"></i>SBAR Wizard
                        </a>
                        <a href="drug-interactions.html" class="block px-3 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                            <i class="fas fa-pills mr-2"></i>Drug Interactions
                        </a>
                        <a href="care-plan-wizard.html" class="block px-3 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                            <i class="fas fa-clipboard-check mr-2"></i>Care Plan
                        </a>
                    </div>
                </div>
            </nav>
        `;

        // Insert at the beginning of body
        document.body.insertAdjacentHTML('afterbegin', navHTML);
    },

    /**
     * Inject breadcrumb navigation
     */
    injectBreadcrumbs() {
        const config = this.getPageConfig(this.currentPage);

        if (this.currentPage === 'index.html') {
            return; // No breadcrumbs on home page
        }

        const breadcrumbHTML = `
            <div class="florence-breadcrumbs bg-white border-b border-gray-200 shadow-sm">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
                    <nav class="flex items-center space-x-2 text-sm">
                        ${config.breadcrumb.map((crumb, index) => {
                            const isLast = index === config.breadcrumb.length - 1;
                            const isFirst = index === 0;

                            if (isLast) {
                                return `<span class="text-gray-700 font-semibold">${crumb}</span>`;
                            } else if (isFirst) {
                                return `
                                    <a href="index.html" class="text-blue-600 hover:text-blue-800 hover:underline">
                                        <i class="fas fa-home mr-1"></i>${crumb}
                                    </a>
                                    <i class="fas fa-chevron-right text-gray-400 text-xs"></i>
                                `;
                            } else {
                                return `
                                    <span class="text-gray-500">${crumb}</span>
                                    <i class="fas fa-chevron-right text-gray-400 text-xs"></i>
                                `;
                            }
                        }).join('')}
                    </nav>
                </div>
            </div>
        `;

        // Insert after navigation bar
        const navBar = document.getElementById('florenceGlobalNav');
        if (navBar) {
            navBar.insertAdjacentHTML('afterend', breadcrumbHTML);
        }
    },

    /**
     * Inject quick access floating menu
     */
    injectQuickAccessMenu() {
        const quickMenuHTML = `
            <div id="florenceQuickMenu" class="florence-quick-menu fixed inset-0 bg-black bg-opacity-50 z-50 hidden" onclick="FlorenceNav.closeQuickMenu(event)">
                <div class="absolute top-16 right-4 bg-white rounded-lg shadow-2xl w-96 max-w-full max-h-[80vh] overflow-y-auto" onclick="event.stopPropagation()">
                    <!-- Header -->
                    <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-t-lg">
                        <div class="flex items-center justify-between">
                            <h3 class="font-bold text-lg">Quick Access</h3>
                            <button onclick="FlorenceNav.closeQuickMenu()" class="hover:bg-blue-500 p-1 rounded">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <p class="text-blue-100 text-xs mt-1">Jump to any tool or wizard</p>
                    </div>

                    <!-- Search -->
                    <div class="p-3 border-b border-gray-200">
                        <div class="relative">
                            <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                            <input
                                type="text"
                                id="florenceQuickSearch"
                                placeholder="Search tools..."
                                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                onkeyup="FlorenceNav.filterQuickMenu(this.value)"
                            >
                        </div>
                    </div>

                    <!-- Tools List -->
                    <div id="florenceQuickMenuList" class="p-2">
                        ${this.renderQuickMenuItems()}
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', quickMenuHTML);
    },

    /**
     * Render quick menu items grouped by category
     */
    renderQuickMenuItems() {
        const categories = {
            'wizards': { title: 'Clinical Wizards', icon: 'fa-magic', color: 'purple' },
            'tools': { title: 'Clinical Tools', icon: 'fa-tools', color: 'blue' },
            'main': { title: 'Main', icon: 'fa-home', color: 'gray' }
        };

        let html = '';

        Object.entries(categories).forEach(([categoryKey, category]) => {
            const items = Object.entries(this.pages)
                .filter(([_, config]) => config.category === categoryKey)
                .sort((a, b) => a[1].title.localeCompare(b[1].title));

            if (items.length === 0) return;

            html += `
                <div class="mb-3">
                    <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide px-2 mb-2 flex items-center">
                        <i class="fas ${category.icon} mr-2"></i>
                        ${category.title}
                    </div>
                    ${items.map(([filename, config]) => `
                        <a
                            href="${filename}"
                            data-page-title="${config.title.toLowerCase()}"
                            class="florence-quick-item flex items-center justify-between p-3 rounded-lg hover:bg-gray-100 transition-colors ${this.currentPage === filename ? 'bg-blue-50 border-l-4 border-blue-500' : ''}"
                        >
                            <div class="flex items-center space-x-3">
                                <div class="w-10 h-10 bg-gradient-to-br from-${category.color}-500 to-${category.color}-600 rounded-lg flex items-center justify-center text-white">
                                    <i class="fas ${config.icon}"></i>
                                </div>
                                <div>
                                    <div class="font-medium text-gray-800">${config.title}</div>
                                    ${this.currentPage === filename ? '<div class="text-xs text-blue-600 font-semibold">Current Page</div>' : ''}
                                </div>
                            </div>
                            ${config.badge ? `<span class="bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full">${config.badge}</span>` : ''}
                        </a>
                    `).join('')}
                </div>
            `;
        });

        return html;
    },

    /**
     * Toggle quick access menu
     */
    toggleQuickMenu() {
        const menu = document.getElementById('florenceQuickMenu');
        if (menu.classList.contains('hidden')) {
            menu.classList.remove('hidden');
            this.quickMenuOpen = true;
            // Focus search input
            setTimeout(() => {
                document.getElementById('florenceQuickSearch')?.focus();
            }, 100);
        } else {
            this.closeQuickMenu();
        }
    },

    /**
     * Close quick access menu
     */
    closeQuickMenu(event) {
        if (event) {
            event.stopPropagation();
        }
        const menu = document.getElementById('florenceQuickMenu');
        menu.classList.add('hidden');
        this.quickMenuOpen = false;
        // Clear search
        const search = document.getElementById('florenceQuickSearch');
        if (search) {
            search.value = '';
            this.filterQuickMenu('');
        }
    },

    /**
     * Filter quick menu items by search term
     */
    filterQuickMenu(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        const items = document.querySelectorAll('.florence-quick-item');

        items.forEach(item => {
            const title = item.getAttribute('data-page-title');
            if (title.includes(term)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    },

    /**
     * Toggle mobile menu
     */
    toggleMobileMenu() {
        const menu = document.getElementById('florenceMobileMenu');
        menu.classList.toggle('hidden');
    },

    /**
     * Setup mobile menu
     */
    setupMobileMenu() {
        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            const menu = document.getElementById('florenceMobileMenu');
            const btn = document.getElementById('florenceMobileMenuBtn');

            if (!menu.classList.contains('hidden') &&
                !menu.contains(e.target) &&
                !btn.contains(e.target)) {
                menu.classList.add('hidden');
            }
        });
    },

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Alt+N: Open quick menu
            if (e.altKey && e.key === 'n') {
                e.preventDefault();
                this.toggleQuickMenu();
            }

            // Escape: Close quick menu
            if (e.key === 'Escape' && this.quickMenuOpen) {
                this.closeQuickMenu();
            }

            // Shift+?: Open help
            if (e.shiftKey && e.key === '?') {
                e.preventDefault();
                this.openHelp();
            }
        });
    },

    /**
     * Open help (placeholder - will be implemented with help system)
     */
    openHelp() {
        // For now, open a simple alert
        // Will be replaced with actual help system
        alert('Help System Coming Soon!\n\nKeyboard Shortcuts:\n• Alt+N: Quick Access Menu\n• Shift+?: Help\n• Escape: Close Menus');
    }
};

// Auto-initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => FlorenceNav.init());
} else {
    FlorenceNav.init();
}
