import { useState, useEffect } from 'react';
import CareSettingSelector, { type CareSetting } from './CareSettingSelector';

/**
 * Care Setting Onboarding Modal
 *
 * First-run experience that helps nurses select their care setting.
 * Shows only if no setting is selected, ensuring nurses always have context.
 *
 * Design Principles:
 * - Non-dismissible until setting selected (ensures context)
 * - Educational (explains why this matters)
 * - Visual and engaging
 * - Can be re-opened from settings
 */

interface CareSettingModalProps {
  isOpen: boolean;
  onSelect: (setting: CareSetting) => void;
  onClose?: () => void;
  canDismiss?: boolean;
  title?: string;
  subtitle?: string;
}

export default function CareSettingModal({
  isOpen,
  onSelect,
  onClose,
  canDismiss = false,
  title,
  subtitle
}: CareSettingModalProps) {
  const [selectedSetting, setSelectedSetting] = useState<CareSetting | null>(null);

  // Reset selection when modal opens
  useEffect(() => {
    if (isOpen) {
      setSelectedSetting(null);
    }
  }, [isOpen]);

  const handleSelect = (setting: CareSetting) => {
    setSelectedSetting(setting);
  };

  const handleConfirm = () => {
    if (selectedSetting) {
      onSelect(selectedSetting);
      if (onClose) {
        onClose();
      }
    }
  };

  const handleCancel = () => {
    if (canDismiss && onClose) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-8 text-white">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-3xl font-bold mb-2">
                {title || 'Welcome to AI Nurse Florence'}
              </h2>
              <p className="text-primary-100 text-lg">
                {subtitle || 'Let\'s personalize your experience based on where you work'}
              </p>
            </div>
            {canDismiss && onClose && (
              <button
                onClick={handleCancel}
                className="text-white hover:text-primary-200 transition-colors"
                aria-label="Close modal"
              >
                <i className="fas fa-times text-2xl"></i>
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="p-8">
          {/* Explanation */}
          <div className="mb-8 p-6 bg-primary-50 rounded-xl border border-primary-200">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <i className="fas fa-lightbulb text-primary-600 text-xl"></i>
                </div>
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-2">Why does care setting matter?</h3>
                <p className="text-gray-700 mb-3">
                  Documentation needs vary dramatically by care environment. An ICU nurse needs different
                  templates, safety checks, and workflows than a home health nurse—even at the same reading level.
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <i className="fas fa-check text-primary-600 mt-1"></i>
                    <span><strong>Setting-aware templates:</strong> Get documentation prompts relevant to your environment</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <i className="fas fa-check text-primary-600 mt-1"></i>
                    <span><strong>Context-specific safety:</strong> Receive safety considerations appropriate for your setting</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <i className="fas fa-check text-primary-600 mt-1"></i>
                    <span><strong>Workflow optimization:</strong> Templates adapt to your care setting's pace and complexity</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Setting Selector */}
          <div className="mb-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Select your primary care setting:</h3>
            <CareSettingSelector
              value={selectedSetting || undefined}
              onChange={handleSelect}
              mode="card"
              showCharacteristics={true}
            />
          </div>

          {/* Help Text */}
          <div className="text-sm text-gray-500 text-center mb-6">
            <i className="fas fa-info-circle mr-2"></i>
            You can change this anytime from the settings menu or when creating documents
          </div>

          {/* Actions */}
          <div className="flex gap-4 justify-end">
            {canDismiss && onClose && (
              <button
                onClick={handleCancel}
                className="px-6 py-3 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition-colors"
              >
                Skip for now
              </button>
            )}
            <button
              onClick={handleConfirm}
              disabled={!selectedSetting}
              className={`px-8 py-3 rounded-lg font-semibold transition-all ${
                selectedSetting
                  ? 'bg-primary-600 text-white hover:bg-primary-700 shadow-md hover:shadow-lg'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              <i className="fas fa-check mr-2"></i>
              {selectedSetting ? 'Continue with ' + selectedSetting.replace('-', ' ') : 'Select a setting to continue'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Care Setting Quick Switcher
 *
 * Compact component for changing settings from the Layout header
 */
interface CareSettingBadgeProps {
  currentSetting: CareSetting | null;
  onClick: () => void;
  className?: string;
}

export function CareSettingBadge({ currentSetting, onClick, className = '' }: CareSettingBadgeProps) {
  const icons: Record<CareSetting, string> = {
    'icu': 'fa-heart-pulse',
    'med-surg': 'fa-hospital',
    'emergency': 'fa-truck-medical',
    'outpatient': 'fa-user-doctor',
    'home-health': 'fa-house-medical',
    'skilled-nursing': 'fa-bed-pulse'
  };

  const labels: Record<CareSetting, string> = {
    'icu': 'ICU',
    'med-surg': 'Med-Surg',
    'emergency': 'Emergency',
    'outpatient': 'Outpatient',
    'home-health': 'Home Health',
    'skilled-nursing': 'Skilled Nursing'
  };

  const colors: Record<CareSetting, string> = {
    'icu': 'red',
    'med-surg': 'blue',
    'emergency': 'orange',
    'outpatient': 'green',
    'home-health': 'purple',
    'skilled-nursing': 'teal'
  };

  if (!currentSetting) {
    return (
      <button
        onClick={onClick}
        className={`flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors ${className}`}
        aria-label="Set care setting"
      >
        <i className="fas fa-hospital text-gray-600"></i>
        <span className="text-sm font-medium text-gray-700">Set Care Setting</span>
      </button>
    );
  }

  const color = colors[currentSetting];
  const icon = icons[currentSetting];
  const label = labels[currentSetting];

  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-2 bg-${color}-50 hover:bg-${color}-100 border border-${color}-200 rounded-lg transition-colors ${className}`}
      aria-label={`Current care setting: ${label}. Click to change.`}
      title="Click to change care setting"
    >
      <i className={`fas ${icon} text-${color}-600`}></i>
      <span className={`text-sm font-medium text-${color}-900`}>{label}</span>
      <i className="fas fa-chevron-down text-xs text-${color}-600"></i>
    </button>
  );
}
