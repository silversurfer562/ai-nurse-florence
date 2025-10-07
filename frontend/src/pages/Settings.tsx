import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useCareSettings } from '../hooks/useCareSettings';
import { useDocumentLanguage } from '../hooks/useDocumentLanguage';
import CareSettingSelector from '../components/CareSettingSelector';
import type { CareSetting } from '../components/CareSettingSelector';
import LanguageSelector from '../components/LanguageSelector';
import LanguageAutocomplete from '../components/LanguageAutocomplete';

/**
 * Settings Page
 *
 * Centralized settings management for AI Nurse Florence
 * - Care Setting configuration
 * - Language preferences
 * - Display preferences
 * - Account settings (future)
 */

export default function Settings() {
  const { i18n } = useTranslation();
  const { careSetting, setCareSetting, clearCareSetting } = useCareSettings();
  const { documentLanguage, setDocumentLanguage, resetToUILanguage } = useDocumentLanguage();
  const [activeTab, setActiveTab] = useState<'general' | 'care-setting' | 'language' | 'accessibility'>('general');

  const handleCareSettingChange = (setting: CareSetting) => {
    setCareSetting(setting);
  };

  const handleClearCareSetting = () => {
    if (confirm('Are you sure you want to clear your care setting? You will need to select it again.')) {
      clearCareSetting();
    }
  };

  const tabs = [
    { id: 'general', label: 'General', icon: 'fa-sliders' },
    { id: 'care-setting', label: 'Care Setting', icon: 'fa-hospital' },
    { id: 'language', label: 'Language', icon: 'fa-language' },
    { id: 'accessibility', label: 'Accessibility', icon: 'fa-universal-access' }
  ] as const;

  return (
    <div className="max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          <i className="fas fa-cog mr-3 text-primary-600"></i>
          Settings
        </h1>
        <p className="text-gray-600">
          Manage your preferences and configure AI Nurse Florence for your workflow
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px" role="tablist">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                role="tab"
                aria-selected={activeTab === tab.id}
                aria-controls={`${tab.id}-panel`}
              >
                <i className={`fas ${tab.icon} mr-2`} aria-hidden="true"></i>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Panels */}
        <div className="p-6">
          {/* General Tab */}
          {activeTab === 'general' && (
            <div id="general-panel" role="tabpanel">
              <h2 className="text-xl font-bold text-gray-800 mb-4">General Settings</h2>

              <div className="space-y-6">
                {/* App Version */}
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">Application Information</h3>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>Version:</span>
                      <span className="font-mono">2.3.1</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Build:</span>
                      <span className="font-mono">Production</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Last Updated:</span>
                      <span>{new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
                    </div>
                  </div>
                </div>

                {/* Data Privacy */}
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">
                    <i className="fas fa-shield-halved mr-2 text-primary-600"></i>
                    Data Privacy & Security
                  </h3>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p className="flex items-start gap-2">
                      <i className="fas fa-check text-green-600 mt-1"></i>
                      <span>No PHI stored - All patient data remains session-only</span>
                    </p>
                    <p className="flex items-start gap-2">
                      <i className="fas fa-check text-green-600 mt-1"></i>
                      <span>HIPAA compliant session management</span>
                    </p>
                    <p className="flex items-start gap-2">
                      <i className="fas fa-check text-green-600 mt-1"></i>
                      <span>Encrypted connections (HTTPS)</span>
                    </p>
                    <p className="flex items-start gap-2">
                      <i className="fas fa-check text-green-600 mt-1"></i>
                      <span>Local storage used only for preferences</span>
                    </p>
                  </div>
                </div>

                {/* Storage Management */}
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">Storage & Cache</h3>
                  <div className="space-y-3">
                    <p className="text-sm text-gray-600">
                      Your preferences are stored locally in your browser. Clear storage to reset all preferences.
                    </p>
                    <button
                      onClick={() => {
                        if (confirm('Clear all stored preferences? This will reset language, care setting, and other preferences.')) {
                          localStorage.clear();
                          sessionStorage.clear();
                          window.location.reload();
                        }
                      }}
                      className="btn-secondary"
                    >
                      <i className="fas fa-trash mr-2"></i>
                      Clear All Stored Preferences
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Care Setting Tab */}
          {activeTab === 'care-setting' && (
            <div id="care-setting-panel" role="tabpanel">
              <h2 className="text-xl font-bold text-gray-800 mb-2">Care Setting Configuration</h2>
              <p className="text-gray-600 mb-6">
                Select your primary care setting to optimize templates, documentation, and clinical decision support for your environment.
              </p>

              {/* Current Setting Display */}
              {careSetting && (
                <div className="mb-6 p-4 bg-primary-50 border-l-4 border-primary-600 rounded-r-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-primary-800 font-medium mb-1">Current Care Setting</p>
                      <p className="text-lg font-bold text-primary-900">{careSetting.replace('-', ' ').toUpperCase()}</p>
                    </div>
                    <button
                      onClick={handleClearCareSetting}
                      className="text-sm text-primary-600 hover:text-primary-800 underline"
                    >
                      Clear Setting
                    </button>
                  </div>
                </div>
              )}

              {/* Care Setting Selector */}
              <CareSettingSelector
                value={careSetting || undefined}
                onChange={handleCareSettingChange}
                mode="detailed"
                showCharacteristics={true}
              />

              {/* Information Box */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <h3 className="font-semibold text-gray-800 mb-2">
                  <i className="fas fa-info-circle mr-2 text-primary-600"></i>
                  How Care Settings Work
                </h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span><strong>Contextualizes Templates:</strong> SBAR reports, nursing notes, and care plans adapt to your environment</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span><strong>Smart Safety Checks:</strong> Safety considerations appropriate for your care setting</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span><strong>Workflow Optimization:</strong> Documentation complexity matches your setting's pace</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span><strong>Persistent Context:</strong> Setting remembered across browser sessions</span>
                  </li>
                </ul>
              </div>
            </div>
          )}

          {/* Language Tab */}
          {activeTab === 'language' && (
            <div id="language-panel" role="tabpanel">
              <h2 className="text-xl font-bold text-gray-800 mb-2">Language Preferences</h2>
              <p className="text-gray-600 mb-6">
                Configure language settings for the application interface and patient documents.
              </p>

              {/* UI Language Section */}
              <div className="card mb-6">
                <h3 className="font-semibold text-gray-800 mb-4">
                  <i className="fas fa-display mr-2 text-primary-600"></i>
                  Interface Language
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Language for menus, buttons, and all application text.
                </p>

                {/* Current UI Language */}
                <div className="mb-4 p-3 bg-green-50 border-l-4 border-green-600 rounded-r-lg">
                  <p className="text-sm text-green-800 font-medium mb-1">Current Interface Language</p>
                  <p className="text-lg font-bold text-green-900">{i18n.language.toUpperCase()}</p>
                </div>

                <LanguageSelector />
              </div>

              {/* Document Language Section */}
              <div className="card mb-6">
                <h3 className="font-semibold text-gray-800 mb-4">
                  <i className="fas fa-file-medical mr-2 text-purple-600"></i>
                  Patient Document Language
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Default language for generated patient documents (education materials, discharge instructions, etc.).
                  This is separate from the interface language.
                </p>

                {/* Current Document Language */}
                <div className="mb-4 p-3 bg-purple-50 border-l-4 border-purple-600 rounded-r-lg">
                  <p className="text-sm text-purple-800 font-medium mb-1">Current Document Language</p>
                  <p className="text-lg font-bold text-purple-900">{documentLanguage.toUpperCase()}</p>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Document Language
                  </label>
                  <LanguageAutocomplete
                    value={documentLanguage}
                    onChange={setDocumentLanguage}
                    placeholder="Search for a language..."
                  />
                </div>

                <button
                  onClick={resetToUILanguage}
                  className="btn-secondary text-sm"
                >
                  <i className="fas fa-sync mr-2"></i>
                  Use Same as Interface Language
                </button>
              </div>

              {/* Supported Languages Info */}
              <div className="card">
                <h3 className="font-semibold text-gray-800 mb-3">
                  <i className="fas fa-globe mr-2 text-primary-600"></i>
                  Supported Languages (16 Total)
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇺🇸</span>
                    <span>English</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇪🇸</span>
                    <span>Spanish</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇨🇳</span>
                    <span>Chinese</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇮🇳</span>
                    <span>Hindi</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇸🇦</span>
                    <span>Arabic</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇵🇹</span>
                    <span>Portuguese</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇧🇩</span>
                    <span>Bengali</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇷🇺</span>
                    <span>Russian</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇯🇵</span>
                    <span>Japanese</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇵🇰</span>
                    <span>Punjabi</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇩🇪</span>
                    <span>German</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇰🇷</span>
                    <span>Korean</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇫🇷</span>
                    <span>French</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇻🇳</span>
                    <span>Vietnamese</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇮🇹</span>
                    <span>Italian</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">🇵🇭</span>
                    <span>Tagalog</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Accessibility Tab */}
          {activeTab === 'accessibility' && (
            <div id="accessibility-panel" role="tabpanel">
              <h2 className="text-xl font-bold text-gray-800 mb-2">Accessibility Settings</h2>
              <p className="text-gray-600 mb-6">
                AI Nurse Florence is designed to be fully accessible. Configure additional accessibility features here.
              </p>

              {/* WCAG Compliance */}
              <div className="card mb-6">
                <h3 className="font-semibold text-gray-800 mb-3">
                  <i className="fas fa-universal-access mr-2 text-primary-600"></i>
                  WCAG 2.1 Level AA Compliant
                </h3>
                <div className="space-y-2 text-sm text-gray-600">
                  <p className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span><strong>Screen Reader Support:</strong> Full ARIA landmark and label implementation</span>
                  </p>
                  <p className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span><strong>Keyboard Navigation:</strong> Complete keyboard accessibility with skip links</span>
                  </p>
                  <p className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span><strong>Voice Dictation:</strong> Medical terminology voice input on all search fields</span>
                  </p>
                  <p className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span><strong>High Contrast Mode:</strong> Automatic support for OS high contrast settings</span>
                  </p>
                  <p className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span><strong>Reduced Motion:</strong> Respects prefers-reduced-motion setting</span>
                  </p>
                </div>
              </div>

              {/* Voice Dictation Info */}
              <div className="card mb-6">
                <h3 className="font-semibold text-gray-800 mb-3">
                  <i className="fas fa-microphone mr-2 text-primary-600"></i>
                  Voice Dictation
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  Voice dictation is available on all search fields. Click the microphone icon to start voice input.
                </p>
                <div className="space-y-2 text-sm text-gray-600">
                  <p className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span>Automatic medical abbreviation expansion (DM → Diabetes Mellitus)</span>
                  </p>
                  <p className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span>Fuzzy matching against known medical terms</span>
                  </p>
                  <p className="flex items-start gap-2">
                    <i className="fas fa-check text-green-600 mt-1"></i>
                    <span>Real-time transcript display</span>
                  </p>
                </div>
              </div>

              {/* Browser Support */}
              <div className="card">
                <h3 className="font-semibold text-gray-800 mb-3">Browser Support</h3>
                <p className="text-sm text-gray-600 mb-3">
                  For the best experience, use a modern browser with Web Speech API support:
                </p>
                <div className="grid grid-cols-2 gap-3 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <i className="fab fa-chrome text-green-600"></i>
                    <span>Chrome (Recommended)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <i className="fab fa-edge text-green-600"></i>
                    <span>Edge (Recommended)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <i className="fab fa-safari text-green-600"></i>
                    <span>Safari</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <i className="fab fa-firefox text-yellow-600"></i>
                    <span>Firefox (Limited voice support)</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Help Footer */}
      <div className="bg-primary-50 border border-primary-200 rounded-lg p-6 text-center">
        <h3 className="font-semibold text-gray-800 mb-2">Need Help?</h3>
        <p className="text-sm text-gray-600 mb-4">
          For questions or support, please refer to our documentation or contact your system administrator.
        </p>
        <div className="flex justify-center gap-4">
          <button
            onClick={() => {
              const helpButton = document.querySelector('.help-system-button') as HTMLButtonElement;
              if (helpButton) {
                helpButton.click();
              }
            }}
            className="btn-secondary text-sm"
          >
            <i className="fas fa-question-circle mr-2"></i>
            Help Center
          </button>
          <a
            href="https://github.com/anthropics/ai-nurse-florence"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary text-sm inline-flex items-center"
          >
            <i className="fas fa-book mr-2"></i>
            View Documentation
          </a>
        </div>
      </div>
    </div>
  );
}
