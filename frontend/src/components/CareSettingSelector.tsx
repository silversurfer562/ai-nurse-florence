import { useState, useEffect } from 'react';

/**
 * Care Setting Selector Component
 *
 * Allows nurses to select their current care setting, which contextualizes
 * all documentation, templates, and clinical decision support.
 *
 * Design Principles:
 * - Prominent placement (not buried in settings)
 * - Visual representation of each setting
 * - Persistent across sessions
 * - Easy to change when needed
 * - Shows setting-specific context
 */

export type CareSetting =
  | 'icu'
  | 'med-surg'
  | 'emergency'
  | 'outpatient'
  | 'home-health'
  | 'skilled-nursing';

export interface CareSettingOption {
  value: CareSetting;
  label: string;
  icon: string;
  description: string;
  color: string;
  characteristics: string[];
}

const CARE_SETTINGS: CareSettingOption[] = [
  {
    value: 'icu',
    label: 'Intensive Care Unit (ICU)',
    icon: 'fa-heart-pulse',
    description: 'Critical care, complex monitoring, multisystem support',
    color: 'red',
    characteristics: [
      'Continuous monitoring',
      'Complex medications',
      'Ventilator management',
      'Hemodynamic support',
      'Hourly assessments'
    ]
  },
  {
    value: 'med-surg',
    label: 'Medical-Surgical',
    icon: 'fa-hospital',
    description: 'General medical and post-surgical care',
    color: 'blue',
    characteristics: [
      'Post-operative care',
      'Medication management',
      'Wound care',
      'Patient education',
      'Discharge planning'
    ]
  },
  {
    value: 'emergency',
    label: 'Emergency Department',
    icon: 'fa-truck-medical',
    description: 'Acute care, rapid assessment, stabilization',
    color: 'orange',
    characteristics: [
      'Rapid triage',
      'Acute stabilization',
      'Time-critical interventions',
      'High patient turnover',
      'Crisis management'
    ]
  },
  {
    value: 'outpatient',
    label: 'Outpatient / Clinic',
    icon: 'fa-user-doctor',
    description: 'Ambulatory care, preventive health, chronic disease management',
    color: 'green',
    characteristics: [
      'Health maintenance',
      'Chronic disease management',
      'Patient education',
      'Preventive care',
      'Follow-up visits'
    ]
  },
  {
    value: 'home-health',
    label: 'Home Health',
    icon: 'fa-house-medical',
    description: 'In-home care, caregiver support, independence focus',
    color: 'purple',
    characteristics: [
      'In-home assessments',
      'Caregiver education',
      'Safety evaluation',
      'Resource coordination',
      'Independence support'
    ]
  },
  {
    value: 'skilled-nursing',
    label: 'Skilled Nursing Facility',
    icon: 'fa-bed-pulse',
    description: 'Long-term care, rehabilitation, elder care',
    color: 'teal',
    characteristics: [
      'Rehabilitation focus',
      'Long-term monitoring',
      'Elder care expertise',
      'Quality of life',
      'Family coordination'
    ]
  }
];

interface CareSettingSelectorProps {
  value?: CareSetting;
  onChange: (setting: CareSetting) => void;
  mode?: 'compact' | 'detailed' | 'card';
  showCharacteristics?: boolean;
  className?: string;
}

export default function CareSettingSelector({
  value,
  onChange,
  mode = 'detailed',
  showCharacteristics = true,
  className = ''
}: CareSettingSelectorProps) {
  const [selectedSetting, setSelectedSetting] = useState<CareSetting | undefined>(value);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    setSelectedSetting(value);
  }, [value]);

  const handleSelect = (setting: CareSetting) => {
    setSelectedSetting(setting);
    onChange(setting);
    if (mode === 'compact') {
      setIsExpanded(false);
    }
  };

  const selectedOption = CARE_SETTINGS.find(s => s.value === selectedSetting);

  // Compact mode - dropdown style
  if (mode === 'compact') {
    return (
      <div className={`relative ${className}`}>
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between px-4 py-3 bg-white border-2 border-gray-300 rounded-lg hover:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
          aria-expanded={isExpanded}
          aria-label="Select care setting"
        >
          <div className="flex items-center gap-3">
            {selectedOption ? (
              <>
                <i className={`fas ${selectedOption.icon} text-${selectedOption.color}-600 text-xl`} aria-hidden="true"></i>
                <div className="text-left">
                  <div className="font-semibold text-gray-900">{selectedOption.label}</div>
                  <div className="text-xs text-gray-500">{selectedOption.description}</div>
                </div>
              </>
            ) : (
              <div className="text-gray-500">
                <i className="fas fa-hospital mr-2" aria-hidden="true"></i>
                Select your care setting...
              </div>
            )}
          </div>
          <i className={`fas fa-chevron-${isExpanded ? 'up' : 'down'} text-gray-400`} aria-hidden="true"></i>
        </button>

        {isExpanded && (
          <div className="absolute z-50 w-full mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl max-h-96 overflow-y-auto">
            {CARE_SETTINGS.map((setting) => (
              <button
                key={setting.value}
                type="button"
                onClick={() => handleSelect(setting.value)}
                className={`w-full flex items-start gap-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left ${
                  selectedSetting === setting.value ? `bg-${setting.color}-50 border-l-4 border-${setting.color}-600` : ''
                }`}
                role="option"
                aria-selected={selectedSetting === setting.value}
              >
                <i className={`fas ${setting.icon} text-${setting.color}-600 text-xl mt-1`} aria-hidden="true"></i>
                <div className="flex-1">
                  <div className="font-semibold text-gray-900">{setting.label}</div>
                  <div className="text-sm text-gray-600">{setting.description}</div>
                </div>
                {selectedSetting === setting.value && (
                  <i className="fas fa-check text-green-600 mt-1" aria-hidden="true"></i>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  // Card mode - visual grid
  if (mode === 'card') {
    return (
      <div className={`grid md:grid-cols-2 lg:grid-cols-3 gap-4 ${className}`} role="radiogroup" aria-label="Care setting selection">
        {CARE_SETTINGS.map((setting) => (
          <button
            key={setting.value}
            type="button"
            onClick={() => handleSelect(setting.value)}
            className={`p-6 rounded-xl border-2 transition-all text-left ${
              selectedSetting === setting.value
                ? `border-${setting.color}-600 bg-${setting.color}-50 shadow-lg scale-105`
                : 'border-gray-200 hover:border-gray-400 hover:shadow-md'
            }`}
            role="radio"
            aria-checked={selectedSetting === setting.value}
          >
            <div className="flex items-start justify-between mb-3">
              <div className={`p-3 rounded-lg bg-${setting.color}-100`}>
                <i className={`fas ${setting.icon} text-${setting.color}-600 text-2xl`} aria-hidden="true"></i>
              </div>
              {selectedSetting === setting.value && (
                <i className="fas fa-check-circle text-green-600 text-xl" aria-hidden="true"></i>
              )}
            </div>
            <h3 className="font-bold text-gray-900 mb-1">{setting.label}</h3>
            <p className="text-sm text-gray-600 mb-3">{setting.description}</p>
            {showCharacteristics && (
              <div className="space-y-1">
                {setting.characteristics.slice(0, 3).map((char, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs text-gray-500">
                    <i className="fas fa-circle text-xs opacity-50" aria-hidden="true" style={{ fontSize: '4px' }}></i>
                    {char}
                  </div>
                ))}
              </div>
            )}
          </button>
        ))}
      </div>
    );
  }

  // Detailed mode - list with full details
  return (
    <div className={`space-y-3 ${className}`} role="radiogroup" aria-label="Care setting selection">
      {CARE_SETTINGS.map((setting) => (
        <button
          key={setting.value}
          type="button"
          onClick={() => handleSelect(setting.value)}
          className={`w-full p-5 rounded-lg border-2 transition-all text-left ${
            selectedSetting === setting.value
              ? `border-${setting.color}-600 bg-${setting.color}-50 shadow-md`
              : 'border-gray-200 hover:border-gray-400 hover:shadow-sm'
          }`}
          role="radio"
          aria-checked={selectedSetting === setting.value}
        >
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-lg bg-${setting.color}-100 flex-shrink-0`}>
              <i className={`fas ${setting.icon} text-${setting.color}-600 text-2xl`} aria-hidden="true"></i>
            </div>
            <div className="flex-1">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-bold text-lg text-gray-900">{setting.label}</h3>
                {selectedSetting === setting.value && (
                  <span className={`px-3 py-1 rounded-full text-xs font-medium bg-${setting.color}-600 text-white`}>
                    <i className="fas fa-check mr-1" aria-hidden="true"></i>
                    Active
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 mb-3">{setting.description}</p>
              {showCharacteristics && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {setting.characteristics.map((char, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-xs text-gray-500">
                      <i className={`fas fa-check text-${setting.color}-600 text-xs`} aria-hidden="true"></i>
                      {char}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}

// Export care settings for use in other components
export { CARE_SETTINGS };
