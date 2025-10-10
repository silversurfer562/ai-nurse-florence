/**
 * Care Setting Framework
 * Personalizes AI Nurse Florence based on clinical care environment
 */

const CareSettings = {
    // Care setting definitions with your existing color palette
    SETTINGS: {
        'icu': {
            id: 'icu',
            name: 'ICU',
            fullName: 'Intensive Care Unit',
            description: 'Critical care, hemodynamic monitoring, ventilator management',
            icon: 'fa-heartbeat',
            color: 'red',
            bgClass: 'bg-red-100',
            textClass: 'text-red-700',
            borderClass: 'border-red-400',
            badgeBg: 'bg-red-600',
            badgeText: 'text-white'
        },
        'medsurg': {
            id: 'medsurg',
            name: 'Med-Surg',
            fullName: 'Medical-Surgical',
            description: 'General floor nursing, post-surgical care, medical conditions',
            icon: 'fa-hospital',
            color: 'blue',
            bgClass: 'bg-blue-100',
            textClass: 'text-blue-700',
            borderClass: 'border-blue-400',
            badgeBg: 'bg-blue-600',
            badgeText: 'text-white'
        },
        'emergency': {
            id: 'emergency',
            name: 'Emergency',
            fullName: 'Emergency Department',
            description: 'Triage, trauma, rapid assessment, high-acuity patients',
            icon: 'fa-ambulance',
            color: 'orange',
            bgClass: 'bg-orange-100',
            textClass: 'text-orange-700',
            borderClass: 'border-orange-400',
            badgeBg: 'bg-orange-600',
            badgeText: 'text-white'
        },
        'outpatient': {
            id: 'outpatient',
            name: 'Outpatient',
            fullName: 'Outpatient Clinic',
            description: 'Clinic visits, preventive care, chronic disease management',
            icon: 'fa-clinic-medical',
            color: 'green',
            bgClass: 'bg-green-100',
            textClass: 'text-green-700',
            borderClass: 'border-green-400',
            badgeBg: 'bg-green-600',
            badgeText: 'text-white'
        },
        'homehealth': {
            id: 'homehealth',
            name: 'Home Health',
            fullName: 'Home Health',
            description: 'In-home visits, patient education, caregiver support',
            icon: 'fa-home',
            color: 'navy',
            bgClass: 'bg-navy-100',
            textClass: 'text-navy-700',
            borderClass: 'border-navy-400',
            badgeBg: 'bg-navy-600',
            badgeText: 'text-white',
            customColors: {
                bg100: '#e6f0ff',
                text700: '#1e3a8a',
                border400: '#60a5fa',
                bg600: '#1e40af'
            }
        },
        'snf': {
            id: 'snf',
            name: 'Skilled Nursing',
            fullName: 'Skilled Nursing Facility',
            description: 'Long-term care, rehabilitation, functional assessments',
            icon: 'fa-procedures',
            color: 'teal',
            bgClass: 'bg-teal-100',
            textClass: 'text-teal-700',
            borderClass: 'border-teal-400',
            badgeBg: 'bg-teal-600',
            badgeText: 'text-white'
        }
    },

    /**
     * Get current care setting from localStorage
     * @returns {Object|null} Setting object or null
     */
    getCurrentSetting() {
        const settingId = localStorage.getItem('careSettingId');
        return settingId ? this.SETTINGS[settingId] : null;
    },

    /**
     * Set current care setting
     * @param {string} settingId - Setting ID (e.g., 'icu', 'medsurg')
     */
    setCurrentSetting(settingId) {
        if (this.SETTINGS[settingId]) {
            localStorage.setItem('careSettingId', settingId);
            // Dispatch custom event for reactive components
            window.dispatchEvent(new CustomEvent('careSettingChanged', {
                detail: { setting: this.SETTINGS[settingId] }
            }));
            return true;
        }
        return false;
    },

    /**
     * Check if user has selected a care setting
     * @returns {boolean}
     */
    hasSelectedSetting() {
        return localStorage.getItem('careSettingId') !== null;
    },

    /**
     * Clear current care setting
     */
    clearSetting() {
        localStorage.removeItem('careSettingId');
        window.dispatchEvent(new CustomEvent('careSettingChanged', {
            detail: { setting: null }
        }));
    },

    /**
     * Inject custom color CSS for non-Tailwind colors (e.g., navy)
     */
    injectCustomColorCSS() {
        if (document.getElementById('customColorCSS')) return;

        const style = document.createElement('style');
        style.id = 'customColorCSS';
        style.textContent = `
            .bg-navy-100 { background-color: #dbeafe !important; }
            .text-navy-700 { color: #1e40af !important; }
            .border-navy-400 { border-color: #3b82f6 !important; }
            .bg-navy-600 { background-color: #1e40af !important; }
        `;
        document.head.appendChild(style);
    },

    /**
     * Show first-run onboarding modal
     * @param {Function} onSelect - Callback when setting is selected
     */
    showOnboardingModal(onSelect) {
        this.injectCustomColorCSS(); // Inject navy colors
        if (document.getElementById('careSettingModal')) return; // Already showing

        const modal = document.createElement('div');
        modal.id = 'careSettingModal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            animation: fadeIn 0.3s ease;
        `;

        modal.innerHTML = `
            <div style="background: white; border-radius: 12px; padding: 32px; max-width: 700px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3); animation: slideUp 0.3s ease;">
                <div style="text-align: center; margin-bottom: 24px;">
                    <i class="fas fa-hospital-user" style="color: #6366f1; font-size: 48px; margin-bottom: 16px;"></i>
                    <h2 style="margin: 0; font-size: 28px; font-weight: 700; color: #111827;">Welcome to AI Nurse Florence</h2>
                    <p style="color: #6b7280; margin-top: 12px; font-size: 16px;">Let's personalize your experience. Where do you work?</p>
                </div>

                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 24px;">
                    ${Object.values(this.SETTINGS).map(setting => `
                        <div class="setting-option" data-setting-id="${setting.id}" style="cursor: pointer; padding: 20px; border: 2px solid #e5e7eb; border-radius: 8px; transition: all 0.2s ease; background: white;">
                            <div style="display: flex; align-items: start; gap: 12px;">
                                <div style="width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;" class="${setting.badgeBg}">
                                    <i class="fas ${setting.icon} ${setting.badgeText}" style="font-size: 20px;"></i>
                                </div>
                                <div style="flex: 1;">
                                    <div style="font-weight: 700; color: #111827; margin-bottom: 4px; font-size: 16px;">${setting.fullName}</div>
                                    <div style="font-size: 13px; color: #6b7280; line-height: 1.4;">${setting.description}</div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <div style="background: #f3f4f6; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
                    <div style="display: flex; align-items: start; gap: 12px;">
                        <i class="fas fa-info-circle" style="color: #6366f1; margin-top: 2px;"></i>
                        <div style="flex: 1;">
                            <p style="margin: 0; font-size: 14px; color: #374151; line-height: 1.5;">
                                <strong>This personalizes your clinical workflows.</strong><br>
                                You can change this anytime from the header menu.
                            </p>
                        </div>
                    </div>
                </div>

                <div style="text-align: center;">
                    <button id="skipSettingBtn" style="background: white; color: #6b7280; border: 1px solid #d1d5db; padding: 10px 20px; border-radius: 6px; font-weight: 500; cursor: pointer; font-size: 14px;">
                        Skip for now
                    </button>
                </div>
            </div>

            <style>
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideUp {
                    from { transform: translateY(20px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                .setting-option:hover {
                    border-color: #6366f1 !important;
                    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15) !important;
                    transform: translateY(-2px);
                }
            </style>
        `;

        document.body.appendChild(modal);

        // Add click handlers for each setting option
        document.querySelectorAll('.setting-option').forEach(option => {
            option.addEventListener('click', () => {
                const settingId = option.dataset.settingId;
                this.setCurrentSetting(settingId);
                modal.remove();
                if (onSelect) onSelect(this.SETTINGS[settingId]);
            });
        });

        // Skip button
        document.getElementById('skipSettingBtn').addEventListener('click', () => {
            modal.remove();
            if (onSelect) onSelect(null);
        });
    },

    /**
     * Inject care setting badge into page header
     * @param {string} headerSelector - CSS selector for header element
     */
    injectHeaderBadge(headerSelector = 'header') {
        this.injectCustomColorCSS(); // Ensure custom colors are loaded

        const setting = this.getCurrentSetting();
        if (!setting) return;

        const header = document.querySelector(headerSelector);
        if (!header) return;

        // Remove existing badge if present
        const existingBadge = document.getElementById('careSettingBadge');
        if (existingBadge) existingBadge.remove();

        // Create badge container
        const badgeContainer = document.createElement('div');
        badgeContainer.id = 'careSettingBadge';
        badgeContainer.style.cssText = 'display: flex; align-items: center; gap: 8px;';

        badgeContainer.innerHTML = `
            <div class="${setting.badgeBg} ${setting.badgeText}" style="padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 6px; cursor: pointer;" id="settingBadgeBtn">
                <i class="fas ${setting.icon}"></i>
                <span>${setting.name}</span>
                <i class="fas fa-chevron-down" style="font-size: 10px; opacity: 0.8;"></i>
            </div>
        `;

        // Find title div and insert badge after it
        const titleDiv = header.querySelector('div > div');
        if (titleDiv && titleDiv.parentElement) {
            titleDiv.parentElement.appendChild(badgeContainer);
        }

        // Add click handler to show setting switcher
        document.getElementById('settingBadgeBtn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.showSettingSwitcher(e.target.closest('div'));
        });
    },

    /**
     * Show setting switcher dropdown
     * @param {HTMLElement} anchorElement - Element to position dropdown near
     */
    showSettingSwitcher(anchorElement) {
        // Remove existing dropdown
        const existing = document.getElementById('settingSwitcherDropdown');
        if (existing) {
            existing.remove();
            return;
        }

        const currentSetting = this.getCurrentSetting();
        const dropdown = document.createElement('div');
        dropdown.id = 'settingSwitcherDropdown';
        dropdown.style.cssText = `
            position: absolute;
            top: ${anchorElement.offsetTop + anchorElement.offsetHeight + 8}px;
            right: 20px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            z-index: 9999;
            min-width: 280px;
            padding: 8px;
            animation: fadeIn 0.2s ease;
        `;

        dropdown.innerHTML = `
            <div style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb; margin-bottom: 8px;">
                <div style="font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em;">Care Setting</div>
            </div>
            ${Object.values(this.SETTINGS).map(setting => `
                <div class="setting-dropdown-item" data-setting-id="${setting.id}" style="padding: 10px 12px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 10px; ${currentSetting?.id === setting.id ? 'background: #f3f4f6;' : ''}">
                    <div class="${setting.badgeBg} ${setting.badgeText}" style="width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                        <i class="fas ${setting.icon}"></i>
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #111827; font-size: 14px;">${setting.fullName}</div>
                        <div style="font-size: 12px; color: #6b7280;">${setting.name}</div>
                    </div>
                    ${currentSetting?.id === setting.id ? '<i class="fas fa-check text-indigo-600"></i>' : ''}
                </div>
            `).join('')}
            <div style="border-top: 1px solid #e5e7eb; margin-top: 8px; padding-top: 8px;">
                <div id="clearSettingBtn" style="padding: 10px 12px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 10px; color: #6b7280; font-size: 14px;">
                    <i class="fas fa-times-circle"></i>
                    <span>Clear setting</span>
                </div>
            </div>
        `;

        document.body.appendChild(dropdown);

        // Click handlers
        dropdown.querySelectorAll('.setting-dropdown-item').forEach(item => {
            item.addEventListener('mouseenter', () => item.style.background = '#f9fafb');
            item.addEventListener('mouseleave', () => {
                const isActive = item.dataset.settingId === currentSetting?.id;
                item.style.background = isActive ? '#f3f4f6' : 'white';
            });
            item.addEventListener('click', () => {
                const settingId = item.dataset.settingId;
                this.setCurrentSetting(settingId);
                dropdown.remove();
                window.location.reload(); // Reload to apply changes
            });
        });

        document.getElementById('clearSettingBtn').addEventListener('click', () => {
            this.clearSetting();
            dropdown.remove();
            window.location.reload();
        });

        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', function closeDropdown(e) {
                if (!dropdown.contains(e.target)) {
                    dropdown.remove();
                    document.removeEventListener('click', closeDropdown);
                }
            });
        }, 100);
    },

    /**
     * Get setting-specific content variant
     * @param {Object} variants - Object with setting IDs as keys
     * @returns {any} Content for current setting or default
     */
    getVariant(variants) {
        const setting = this.getCurrentSetting();
        if (!setting || !variants[setting.id]) {
            return variants.default || null;
        }
        return variants[setting.id];
    },

    /**
     * Initialize care setting framework
     * @param {Object} options - Configuration options
     */
    init(options = {}) {
        const {
            showOnboardingIfNew = true,
            injectBadge = true,
            headerSelector = 'header',
            onSettingSelected = null
        } = options;

        // Show onboarding modal if first visit
        if (showOnboardingIfNew && !this.hasSelectedSetting()) {
            setTimeout(() => {
                this.showOnboardingModal(onSettingSelected);
            }, 500);
        }

        // Inject header badge if setting exists
        if (injectBadge && this.hasSelectedSetting()) {
            setTimeout(() => {
                this.injectHeaderBadge(headerSelector);
            }, 100);
        }
    }
};

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CareSettings;
}
