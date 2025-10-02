/**
 * Help System - Vanilla JavaScript Version
 *
 * Provides comprehensive help interface with:
 * - Floating help button
 * - Slide-out drawer with tabs
 * - Searchable tasks and FAQs
 * - Quick start guide
 */

class HelpSystem {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.isOpen = false;
        this.activeTab = 'quickstart';
        this.searchQuery = '';
        this.selectedTask = null;
        this.helpContent = null;

        this.loadHelpContent();
    }

    async loadHelpContent() {
        try {
            const response = await fetch('/static/data/help-content.json');
            this.helpContent = await response.json();
            this.render();
        } catch (error) {
            console.error('Failed to load help content:', error);
            // Fallback: render with minimal content
            this.helpContent = { tasks: [], faqs: [], tooltips: {}, quickStart: { title: 'Help', welcome: 'Loading...', steps: [] } };
            this.render();
        }
    }

    render() {
        if (!this.container || !this.helpContent) return;

        this.container.innerHTML = `
            <!-- Floating Help Button -->
            <button
                id="help-button"
                class="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg transition-all duration-200 hover:scale-110 z-50"
                aria-label="Open Help"
            >
                <i class="fas ${this.isOpen ? 'fa-times' : 'fa-question'} text-xl"></i>
            </button>

            <!-- Help Drawer -->
            <div id="help-drawer" class="fixed inset-0 z-40 ${this.isOpen ? '' : 'hidden'}" style="pointer-events: ${this.isOpen ? 'auto' : 'none'};">
                <!-- Backdrop -->
                <div class="absolute inset-0 bg-black bg-opacity-50 transition-opacity" id="help-backdrop"></div>

                <!-- Drawer Panel -->
                <div class="absolute right-0 top-0 h-full w-full md:w-2/3 lg:w-1/2 xl:w-2/5 bg-white shadow-2xl overflow-hidden flex flex-col transform transition-transform duration-300 ${this.isOpen ? 'translate-x-0' : 'translate-x-full'}">
                    ${this.renderDrawerContent()}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    renderDrawerContent() {
        return `
            <!-- Header -->
            <div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <i class="fas fa-life-ring text-2xl"></i>
                        <h2 class="text-2xl font-bold">Help & Guide</h2>
                    </div>
                    <button id="close-help" class="text-white hover:bg-blue-600 rounded-full p-2 transition-colors">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>

                <!-- Search -->
                <div class="relative">
                    <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-blue-300"></i>
                    <input
                        type="text"
                        id="help-search"
                        placeholder="Search for help..."
                        value="${this.searchQuery}"
                        class="w-full pl-10 pr-4 py-3 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-300"
                    />
                </div>
            </div>

            <!-- Tabs -->
            <div class="border-b border-gray-200 bg-gray-50">
                <div class="flex">
                    <button data-tab="quickstart" class="tab-button flex-1 px-4 py-3 text-sm font-medium transition-colors ${this.activeTab === 'quickstart' ? 'text-blue-600 border-b-2 border-blue-600 bg-white' : 'text-gray-600 hover:text-gray-900'}">
                        <i class="fas fa-rocket mr-2"></i>Quick Start
                    </button>
                    <button data-tab="tasks" class="tab-button flex-1 px-4 py-3 text-sm font-medium transition-colors ${this.activeTab === 'tasks' ? 'text-blue-600 border-b-2 border-blue-600 bg-white' : 'text-gray-600 hover:text-gray-900'}">
                        <i class="fas fa-tasks mr-2"></i>Tasks
                    </button>
                    <button data-tab="faq" class="tab-button flex-1 px-4 py-3 text-sm font-medium transition-colors ${this.activeTab === 'faq' ? 'text-blue-600 border-b-2 border-blue-600 bg-white' : 'text-gray-600 hover:text-gray-900'}">
                        <i class="fas fa-question-circle mr-2"></i>FAQ
                    </button>
                </div>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto p-6" id="help-content">
                ${this.renderTabContent()}
            </div>

            <!-- Footer -->
            <div class="border-t border-gray-200 bg-gray-50 p-4 text-center text-sm text-gray-600">
                <p>Need more help? <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Contact Support</a></p>
            </div>
        `;
    }

    renderTabContent() {
        if (this.activeTab === 'quickstart') {
            return this.renderQuickStart();
        } else if (this.activeTab === 'tasks') {
            return this.selectedTask ? this.renderTaskDetail() : this.renderTaskList();
        } else if (this.activeTab === 'faq') {
            return this.renderFAQ();
        }
        return '';
    }

    renderQuickStart() {
        const qs = this.helpContent.quickStart;
        return `
            <div class="space-y-6">
                <div>
                    <h3 class="text-2xl font-bold text-gray-900 mb-2">${qs.title}</h3>
                    <p class="text-gray-600 mb-6">${qs.welcome}</p>
                </div>

                ${qs.steps.map((step, index) => `
                    <div class="flex space-x-4">
                        <div class="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                            ${index + 1}
                        </div>
                        <div class="flex-1">
                            <h4 class="font-semibold text-gray-900 mb-1">${step.title}</h4>
                            <p class="text-gray-600 text-sm">${step.description}</p>
                        </div>
                    </div>
                `).join('')}

                <div class="mt-8 bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
                    <p class="text-sm text-blue-900">
                        <i class="fas fa-lightbulb mr-2"></i>
                        <strong>Tip:</strong> Click on the "Tasks" tab to see step-by-step guides for specific workflows.
                    </p>
                </div>
            </div>
        `;
    }

    renderTaskList() {
        const filteredTasks = this.helpContent.tasks.filter(task =>
            task.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
            task.description.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
            task.category.toLowerCase().includes(this.searchQuery.toLowerCase())
        );

        return `
            <div class="space-y-4">
                ${this.searchQuery ? `<p class="text-sm text-gray-600 mb-4">Found ${filteredTasks.length} task${filteredTasks.length !== 1 ? 's' : ''}</p>` : ''}
                ${filteredTasks.map(task => `
                    <button
                        data-task-id="${task.id}"
                        class="task-button w-full text-left bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-500 hover:shadow-md transition-all"
                    >
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <h4 class="font-semibold text-gray-900 mb-1">${task.title}</h4>
                                <p class="text-sm text-gray-600 mb-2">${task.description}</p>
                                <span class="inline-block bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded">${task.category}</span>
                            </div>
                            <i class="fas fa-chevron-right text-gray-400 ml-4"></i>
                        </div>
                    </button>
                `).join('')}
                ${filteredTasks.length === 0 && this.searchQuery ? `<p class="text-gray-500 text-center py-8">No tasks found matching "${this.searchQuery}"</p>` : ''}
            </div>
        `;
    }

    renderTaskDetail() {
        const task = this.helpContent.tasks.find(t => t.id === this.selectedTask);
        if (!task) return '';

        return `
            <div>
                <button id="back-to-tasks" class="text-blue-600 hover:text-blue-700 mb-4 flex items-center">
                    <i class="fas fa-arrow-left mr-2"></i>Back to tasks
                </button>

                <h3 class="text-2xl font-bold text-gray-900 mb-2">${task.title}</h3>
                <p class="text-gray-600 mb-6">${task.description}</p>

                <!-- Steps -->
                <div class="space-y-6 mb-8">
                    <h4 class="font-semibold text-gray-900 text-lg">Step-by-Step Guide</h4>
                    ${task.steps.map(step => `
                        <div class="border-l-4 border-blue-600 pl-4">
                            <div class="flex items-start space-x-3 mb-2">
                                <div class="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">${step.step}</div>
                                <div class="flex-1">
                                    <h5 class="font-semibold text-gray-900">${step.title}</h5>
                                    <p class="text-gray-700 text-sm mt-1">${step.instruction}</p>
                                    ${step.tip ? `
                                        <div class="mt-2 bg-yellow-50 border-l-2 border-yellow-400 p-2 rounded text-xs">
                                            <i class="fas fa-lightbulb text-yellow-600 mr-1"></i>
                                            <strong>Tip:</strong> ${step.tip}
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <!-- Benefits -->
                <div class="mb-8">
                    <h4 class="font-semibold text-gray-900 text-lg mb-3">Benefits</h4>
                    <ul class="space-y-2">
                        ${task.benefits.map(benefit => `
                            <li class="flex items-start space-x-2 text-sm text-gray-700">
                                <i class="fas fa-check-circle text-green-600 mt-0.5"></i>
                                <span>${benefit}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>

                <!-- Troubleshooting -->
                ${task.troubleshooting && task.troubleshooting.length > 0 ? `
                    <div>
                        <h4 class="font-semibold text-gray-900 text-lg mb-3">Troubleshooting</h4>
                        <div class="space-y-3">
                            ${task.troubleshooting.map(item => `
                                <div class="bg-gray-50 p-3 rounded">
                                    <p class="font-medium text-gray-900 text-sm mb-1">
                                        <i class="fas fa-exclamation-triangle text-orange-500 mr-2"></i>
                                        ${item.problem}
                                    </p>
                                    <p class="text-gray-700 text-sm ml-6">${item.solution}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderFAQ() {
        const filteredFAQs = this.helpContent.faqs.filter(faq =>
            faq.question.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
            faq.answer.toLowerCase().includes(this.searchQuery.toLowerCase())
        );

        return `
            <div class="space-y-4">
                ${this.searchQuery ? `<p class="text-sm text-gray-600 mb-4">Found ${filteredFAQs.length} question${filteredFAQs.length !== 1 ? 's' : ''}</p>` : ''}
                ${filteredFAQs.map(faq => `
                    <details class="bg-white border border-gray-200 rounded-lg group">
                        <summary class="cursor-pointer p-4 hover:bg-gray-50 transition-colors flex items-start justify-between list-none">
                            <div class="flex-1 pr-4">
                                <h4 class="font-semibold text-gray-900 mb-1">${faq.question}</h4>
                                <span class="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">${faq.category}</span>
                            </div>
                            <i class="fas fa-chevron-down text-gray-400 transition-transform group-open:rotate-180"></i>
                        </summary>
                        <div class="px-4 pb-4 text-sm text-gray-700 border-t border-gray-100 pt-3">
                            ${faq.answer}
                        </div>
                    </details>
                `).join('')}
                ${filteredFAQs.length === 0 && this.searchQuery ? `<p class="text-gray-500 text-center py-8">No FAQs found matching "${this.searchQuery}"</p>` : ''}
            </div>
        `;
    }

    attachEventListeners() {
        // Help button
        const helpButton = document.getElementById('help-button');
        if (helpButton) {
            helpButton.addEventListener('click', () => this.toggle());
        }

        // Close button and backdrop
        const closeButton = document.getElementById('close-help');
        const backdrop = document.getElementById('help-backdrop');
        if (closeButton) closeButton.addEventListener('click', () => this.close());
        if (backdrop) backdrop.addEventListener('click', () => this.close());

        // Search
        const searchInput = document.getElementById('help-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                this.updateContent();
            });
        }

        // Tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                this.activeTab = button.dataset.tab;
                this.selectedTask = null;
                this.searchQuery = '';
                this.render();
            });
        });

        // Task buttons
        document.querySelectorAll('.task-button').forEach(button => {
            button.addEventListener('click', () => {
                this.selectedTask = button.dataset.taskId;
                this.updateContent();
            });
        });

        // Back to tasks button
        const backButton = document.getElementById('back-to-tasks');
        if (backButton) {
            backButton.addEventListener('click', () => {
                this.selectedTask = null;
                this.updateContent();
            });
        }
    }

    updateContent() {
        const contentDiv = document.getElementById('help-content');
        if (contentDiv) {
            contentDiv.innerHTML = this.renderTabContent();
            this.attachEventListeners(); // Reattach for new content
        }
    }

    toggle() {
        this.isOpen = !this.isOpen;
        this.render();
    }

    open() {
        this.isOpen = true;
        this.render();
    }

    close() {
        this.isOpen = false;
        this.render();
    }
}

// Global function to toggle help (called from footer link)
function toggleHelpSystem() {
    if (window.helpSystem) {
        window.helpSystem.toggle();
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.helpSystem = new HelpSystem('help-system-container');
    });
} else {
    window.helpSystem = new HelpSystem('help-system-container');
}
