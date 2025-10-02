import { useState } from 'react';
import { useCareSettings } from '../hooks/useCareSettings';
import CareSettingModal from './CareSettingModal';
import type { CareSetting } from './CareSettingSelector';

/**
 * Care Setting Context Banner
 *
 * Displays current care setting context in wizards and document creation flows.
 * Provides quick access to change settings without leaving the workflow.
 */

interface CareSettingContextBannerProps {
  /** Custom message to display (optional) */
  message?: string;
  /** Show change button (default: true) */
  showChangeButton?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Variant style */
  variant?: 'info' | 'compact' | 'prominent';
}

export default function CareSettingContextBanner({
  message,
  showChangeButton = true,
  className = '',
  variant = 'info'
}: CareSettingContextBannerProps) {
  const { careSetting, getSettingLabel, getSettingIcon, setCareSetting } = useCareSettings();
  const [showModal, setShowModal] = useState(false);

  // Don't render if no care setting is selected
  if (!careSetting) {
    return (
      <div className={`p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded-r-lg ${className}`}>
        <div className="flex items-start gap-3">
          <i className="fas fa-info-circle text-yellow-600 text-xl mt-0.5"></i>
          <div className="flex-1">
            <p className="font-semibold text-yellow-900 mb-1">No Care Setting Selected</p>
            <p className="text-sm text-yellow-800 mb-2">
              Select your care setting to get optimized templates and documentation for your environment.
            </p>
            <button
              onClick={() => setShowModal(true)}
              className="text-sm font-medium text-yellow-900 underline hover:text-yellow-700"
            >
              Select Care Setting Now
            </button>
          </div>
        </div>
        <CareSettingModal
          isOpen={showModal}
          onSelect={(setting: CareSetting) => {
            setCareSetting(setting);
            setShowModal(false);
          }}
          onClose={() => setShowModal(false)}
          canDismiss={true}
        />
      </div>
    );
  }

  const settingColors: Record<CareSetting, { bg: string; border: string; text: string; icon: string }> = {
    'icu': {
      bg: 'bg-red-50',
      border: 'border-red-500',
      text: 'text-red-900',
      icon: 'text-red-600'
    },
    'med-surg': {
      bg: 'bg-blue-50',
      border: 'border-blue-500',
      text: 'text-blue-900',
      icon: 'text-blue-600'
    },
    'emergency': {
      bg: 'bg-orange-50',
      border: 'border-orange-500',
      text: 'text-orange-900',
      icon: 'text-orange-600'
    },
    'outpatient': {
      bg: 'bg-green-50',
      border: 'border-green-500',
      text: 'text-green-900',
      icon: 'text-green-600'
    },
    'home-health': {
      bg: 'bg-purple-50',
      border: 'border-purple-500',
      text: 'text-purple-900',
      icon: 'text-purple-600'
    },
    'skilled-nursing': {
      bg: 'bg-teal-50',
      border: 'border-teal-500',
      text: 'text-teal-900',
      icon: 'text-teal-600'
    }
  };

  const colors = settingColors[careSetting];

  // Compact variant - minimal space
  if (variant === 'compact') {
    return (
      <>
        <div className={`flex items-center gap-2 px-3 py-2 ${colors.bg} border-l-2 ${colors.border} rounded ${className}`}>
          <i className={`fas ${getSettingIcon()} ${colors.icon}`} aria-hidden="true"></i>
          <span className={`text-sm font-medium ${colors.text}`}>
            {getSettingLabel()}
          </span>
          {showChangeButton && (
            <button
              onClick={() => setShowModal(true)}
              className={`text-xs ${colors.text} opacity-75 hover:opacity-100 underline ml-auto`}
            >
              Change
            </button>
          )}
        </div>
        <CareSettingModal
          isOpen={showModal}
          onSelect={(setting: CareSetting) => {
            setCareSetting(setting);
            setShowModal(false);
          }}
          onClose={() => setShowModal(false)}
          canDismiss={true}
        />
      </>
    );
  }

  // Prominent variant - attention-grabbing
  if (variant === 'prominent') {
    return (
      <>
        <div className={`p-6 ${colors.bg} border-2 ${colors.border} rounded-xl shadow-md ${className}`}>
          <div className="flex items-start gap-4">
            <div className={`flex-shrink-0 w-12 h-12 ${colors.bg} border-2 ${colors.border} rounded-lg flex items-center justify-center`}>
              <i className={`fas ${getSettingIcon()} ${colors.icon} text-2xl`} aria-hidden="true"></i>
            </div>
            <div className="flex-1">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className={`text-sm font-medium ${colors.text} opacity-75 mb-1`}>Care Setting</p>
                  <h3 className={`text-xl font-bold ${colors.text}`}>{getSettingLabel()}</h3>
                </div>
                {showChangeButton && (
                  <button
                    onClick={() => setShowModal(true)}
                    className={`px-4 py-2 border-2 ${colors.border} ${colors.text} rounded-lg hover:bg-white transition-colors font-medium text-sm`}
                  >
                    Change Setting
                  </button>
                )}
              </div>
              <p className={`text-sm ${colors.text} opacity-90`}>
                {message || 'Templates and documentation optimized for your care environment'}
              </p>
            </div>
          </div>
        </div>
        <CareSettingModal
          isOpen={showModal}
          onSelect={(setting: CareSetting) => {
            setCareSetting(setting);
            setShowModal(false);
          }}
          onClose={() => setShowModal(false)}
          canDismiss={true}
        />
      </>
    );
  }

  // Default 'info' variant - balanced information display
  return (
    <>
      <div className={`p-4 ${colors.bg} border-l-4 ${colors.border} rounded-r-lg ${className}`}>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <i className={`fas ${getSettingIcon()} ${colors.icon} text-xl mt-0.5`} aria-hidden="true"></i>
            <div>
              <p className={`font-semibold ${colors.text} mb-1`}>
                {message || `Creating document for ${getSettingLabel()} care setting`}
              </p>
              <p className={`text-sm ${colors.text} opacity-90`}>
                Templates optimized for your care environment
              </p>
            </div>
          </div>
          {showChangeButton && (
            <button
              onClick={() => setShowModal(true)}
              className={`text-sm font-medium ${colors.text} underline hover:no-underline whitespace-nowrap`}
            >
              Change Setting
            </button>
          )}
        </div>
      </div>
      <CareSettingModal
        isOpen={showModal}
        onSelect={(setting: CareSetting) => {
          setCareSetting(setting);
          setShowModal(false);
        }}
        onClose={() => setShowModal(false)}
        canDismiss={true}
      />
    </>
  );
}

/**
 * Inline Care Setting Indicator
 *
 * Small inline display of current care setting (for use in headings, etc.)
 */
interface CareSettingInlineProps {
  className?: string;
}

export function CareSettingInline({ className = '' }: CareSettingInlineProps) {
  const { careSetting, getSettingLabel, getSettingIcon } = useCareSettings();

  if (!careSetting) return null;

  const settingColors: Record<CareSetting, string> = {
    'icu': 'text-red-600',
    'med-surg': 'text-blue-600',
    'emergency': 'text-orange-600',
    'outpatient': 'text-green-600',
    'home-health': 'text-purple-600',
    'skilled-nursing': 'text-teal-600'
  };

  return (
    <span className={`inline-flex items-center gap-2 font-semibold ${settingColors[careSetting]} ${className}`}>
      <i className={`fas ${getSettingIcon()}`} aria-hidden="true"></i>
      <span>{getSettingLabel()}</span>
    </span>
  );
}
