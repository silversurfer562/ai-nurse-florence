/**
 * Reusable Autocomplete Dropdown Component
 *
 * Provides a consistent, accessible autocomplete experience across the application.
 * Features:
 * - Keyboard navigation (Arrow keys, Enter, Escape)
 * - Debounced search
 * - Click-outside-to-close
 * - Customizable rendering
 * - Already-selected item tracking
 */

class AutocompleteDropdown {
    constructor(config) {
        // Required config
        this.inputElement = config.inputElement;
        this.dropdownElement = config.dropdownElement;
        this.fetchResults = config.fetchResults; // async function(query) => array
        this.onSelect = config.onSelect; // function(item, index)

        // Optional config
        this.renderItem = config.renderItem || this.defaultRenderItem.bind(this);
        this.getItemKey = config.getItemKey || ((item) => item.id || item);
        this.minQueryLength = config.minQueryLength || 3;
        this.debounceMs = config.debounceMs !== undefined ? config.debounceMs : 0;
        this.maxResults = config.maxResults || 15;
        this.selectedItems = config.selectedItems || [];
        this.placeholder = config.placeholder || 'No results found';

        // Internal state
        this.currentResults = [];
        this.selectedIndex = -1;
        this.debounceTimer = null;
        this.isLoading = false;

        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Input change - trigger search
        this.inputElement.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            this.handleInput(query);
        });

        // Keyboard navigation
        this.inputElement.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });

        // Focus - show dropdown if there are results
        this.inputElement.addEventListener('focus', () => {
            if (this.currentResults.length > 0 && this.inputElement.value.length >= this.minQueryLength) {
                this.show();
            }
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.inputElement.contains(e.target) && !this.dropdownElement.contains(e.target)) {
                this.hide();
            }
        });
    }

    handleInput(query) {
        clearTimeout(this.debounceTimer);

        // Check for real-time settings updates from global config
        const currentMinLength = window.autocompleteSettings?.minQueryLength || this.minQueryLength;
        const currentDebounce = window.autocompleteSettings?.debounceMs || this.debounceMs;

        if (query.length < currentMinLength) {
            this.hide();
            return;
        }

        this.debounceTimer = setTimeout(async () => {
            await this.search(query);
        }, currentDebounce);
    }

    async search(query) {
        this.isLoading = true;
        this.showLoading();

        try {
            const results = await this.fetchResults(query);
            const currentMaxResults = window.autocompleteSettings?.maxResults || this.maxResults;
            this.currentResults = results.slice(0, currentMaxResults);
            this.selectedIndex = -1;
            this.render();
            this.show();
        } catch (error) {
            console.error('Autocomplete search error:', error);
            this.showError(error.message);
        } finally {
            this.isLoading = false;
        }
    }

    handleKeydown(e) {
        if (!this.isVisible()) return;

        const items = this.dropdownElement.querySelectorAll('.autocomplete-item:not([data-disabled])');

        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1);
                this.updateSelection(items);
                break;

            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection(items);
                break;

            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0 && this.currentResults[this.selectedIndex]) {
                    const item = this.currentResults[this.selectedIndex];
                    const isDisabled = this.isItemSelected(item);
                    if (!isDisabled) {
                        this.selectItem(item, this.selectedIndex);
                    }
                }
                break;

            case 'Escape':
                e.preventDefault();
                this.hide();
                break;
        }
    }

    updateSelection(items) {
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('bg-blue-100');
                item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            } else {
                item.classList.remove('bg-blue-100');
            }
        });
    }

    selectItem(item, index) {
        this.onSelect(item, index);
        this.hide();
    }

    isItemSelected(item) {
        const key = this.getItemKey(item);
        return this.selectedItems.some(selectedItem => this.getItemKey(selectedItem) === key);
    }

    render() {
        if (this.currentResults.length === 0) {
            this.showEmpty();
            return;
        }

        this.dropdownElement.innerHTML = this.currentResults
            .map((item, index) => this.renderItem(item, index, this.isItemSelected(item)))
            .join('');

        // Add click handlers
        this.dropdownElement.querySelectorAll('.autocomplete-item').forEach((element, index) => {
            element.addEventListener('click', () => {
                const item = this.currentResults[index];
                if (!this.isItemSelected(item)) {
                    this.selectItem(item, index);
                }
            });
        });
    }

    defaultRenderItem(item, index, isSelected) {
        return `
            <div class="autocomplete-item px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 transition-colors ${isSelected ? 'opacity-50 bg-gray-50' : ''}"
                 data-index="${index}"
                 ${isSelected ? 'data-disabled="true"' : ''}>
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <p class="font-medium ${isSelected ? 'text-gray-500' : 'text-gray-900'}">
                            ${typeof item === 'string' ? item : item.display || item.name || item.label}
                        </p>
                        ${isSelected ? '<p class="text-xs text-gray-400 mt-1"><i class="fas fa-check mr-1"></i>Already selected</p>' : ''}
                    </div>
                    <i class="fas ${isSelected ? 'fa-check text-gray-400' : 'fa-arrow-right text-blue-500'}"></i>
                </div>
            </div>
        `;
    }

    showLoading() {
        this.dropdownElement.innerHTML = `
            <div class="px-4 py-6 text-center text-gray-500">
                <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                <p class="text-sm">Searching...</p>
            </div>
        `;
        this.show();
    }

    showEmpty() {
        this.dropdownElement.innerHTML = `
            <div class="px-4 py-6 text-center text-gray-500">
                <i class="fas fa-search-minus text-2xl mb-2"></i>
                <p class="text-sm">${this.placeholder}</p>
            </div>
        `;
        this.show();
    }

    showError(message) {
        this.dropdownElement.innerHTML = `
            <div class="px-4 py-6 text-center text-red-500">
                <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                <p class="text-sm">Error loading results</p>
                <p class="text-xs mt-1">${message}</p>
            </div>
        `;
        this.show();
    }

    show() {
        this.dropdownElement.classList.remove('hidden');
    }

    hide() {
        this.dropdownElement.classList.add('hidden');
        this.selectedIndex = -1;
    }

    isVisible() {
        return !this.dropdownElement.classList.contains('hidden');
    }

    // Public methods for external control
    updateSelectedItems(items) {
        this.selectedItems = items;
        if (this.currentResults.length > 0) {
            this.render();
        }
    }

    clear() {
        this.inputElement.value = '';
        this.currentResults = [];
        this.selectedIndex = -1;
        this.hide();
    }

    destroy() {
        clearTimeout(this.debounceTimer);
        // Note: We don't remove event listeners as they're on elements that might be reused
        // In a production app, you'd want to track and remove these listeners
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AutocompleteDropdown;
}
