import { useState, useEffect, useCallback } from 'react';
import type { CareSetting } from '../components/CareSettingSelector';

/**
 * Care Setting Context Hook
 *
 * Manages care setting state with smart persistence:
 * - Session storage for workflow persistence
 * - Local storage for cross-session defaults
 * - Context propagation to all document creation
 *
 * Design Philosophy:
 * - Settings persist across page reloads (same session)
 * - Settings remembered across sessions (convenience)
 * - Easy to override when needed
 * - Cascades to all clinical workflows
 */

const SESSION_STORAGE_KEY = 'ai-nurse-florence-care-setting-session';
const LOCAL_STORAGE_KEY = 'ai-nurse-florence-care-setting-default';

interface CareSettingContext {
  careSetting: CareSetting | null;
  setCareSetting: (setting: CareSetting) => void;
  clearCareSetting: () => void;
  isSettingSelected: boolean;
  getSettingLabel: () => string;
  getSettingIcon: () => string;
}

export function useCareSettings(): CareSettingContext {
  const [careSetting, setCareSetting] = useState<CareSetting | null>(null);

  // Initialize from storage on mount
  useEffect(() => {
    // Priority 1: Check session storage (current session)
    const sessionSetting = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (sessionSetting) {
      setCareSetting(sessionSetting as CareSetting);
      return;
    }

    // Priority 2: Check local storage (remembered default)
    const defaultSetting = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (defaultSetting) {
      setCareSetting(defaultSetting as CareSetting);
      // Also set in session storage
      sessionStorage.setItem(SESSION_STORAGE_KEY, defaultSetting);
    }
  }, []);

  const handleSetCareSetting = useCallback((setting: CareSetting) => {
    // Update state
    setCareSetting(setting);

    // Persist to both storages
    sessionStorage.setItem(SESSION_STORAGE_KEY, setting);
    localStorage.setItem(LOCAL_STORAGE_KEY, setting);

    // Log for debugging
    console.log(`[Care Setting] Updated to: ${setting}`);
  }, []);

  const handleClearCareSetting = useCallback(() => {
    setCareSetting(null);
    sessionStorage.removeItem(SESSION_STORAGE_KEY);
    // Keep local storage for default - only clear session
  }, []);

  const getSettingLabel = useCallback(() => {
    if (!careSetting) return 'No Setting Selected';

    const labels: Record<CareSetting, string> = {
      'icu': 'ICU',
      'med-surg': 'Med-Surg',
      'emergency': 'Emergency',
      'outpatient': 'Outpatient',
      'home-health': 'Home Health',
      'skilled-nursing': 'Skilled Nursing'
    };

    return labels[careSetting] || careSetting;
  }, [careSetting]);

  const getSettingIcon = useCallback(() => {
    if (!careSetting) return 'fa-hospital';

    const icons: Record<CareSetting, string> = {
      'icu': 'fa-heart-pulse',
      'med-surg': 'fa-hospital',
      'emergency': 'fa-truck-medical',
      'outpatient': 'fa-user-doctor',
      'home-health': 'fa-house-medical',
      'skilled-nursing': 'fa-bed-pulse'
    };

    return icons[careSetting] || 'fa-hospital';
  }, [careSetting]);

  return {
    careSetting,
    setCareSetting: handleSetCareSetting,
    clearCareSetting: handleClearCareSetting,
    isSettingSelected: careSetting !== null,
    getSettingLabel,
    getSettingIcon
  };
}

/**
 * Care Setting-Aware API Helper
 *
 * Automatically includes care setting context in API requests
 */
export function useCareSettingAPI() {
  const { careSetting } = useCareSettings();

  const buildAPIParams = useCallback((baseParams: Record<string, any> = {}) => {
    if (careSetting) {
      return {
        ...baseParams,
        care_setting: careSetting
      };
    }
    return baseParams;
  }, [careSetting]);

  return {
    buildAPIParams,
    careSetting
  };
}

/**
 * Document Template Selector Hook
 *
 * Provides setting-specific template defaults
 */
export function useCareSettingTemplates() {
  const { careSetting } = useCareSettings();

  const getTemplateDefaults = useCallback((documentType: string) => {
    if (!careSetting) {
      return getGenericDefaults(documentType);
    }

    // Setting-specific templates
    const templates: Record<CareSetting, Record<string, any>> = {
      'icu': {
        'sbar': {
          focus: 'Hemodynamic stability, ventilator settings, continuous monitoring',
          complexity: 'high',
          includeVitals: true,
          includeLabs: true,
          timeframe: 'hourly'
        },
        'nursing-note': {
          assessmentDepth: 'comprehensive',
          systemsReview: ['neurological', 'cardiovascular', 'respiratory', 'renal'],
          includeDevices: true
        },
        'patient-education': {
          readingLevel: '8th grade',
          focus: 'critical care procedures, equipment, monitoring'
        }
      },
      'med-surg': {
        'sbar': {
          focus: 'Post-op status, pain management, mobility, wound care',
          complexity: 'moderate',
          includeVitals: true,
          includeLabs: false,
          timeframe: 'shift'
        },
        'nursing-note': {
          assessmentDepth: 'focused',
          systemsReview: ['pain', 'mobility', 'wound', 'elimination'],
          includeDevices: false
        },
        'patient-education': {
          readingLevel: '6th grade',
          focus: 'self-care, medication, wound care, activity'
        }
      },
      'emergency': {
        'sbar': {
          focus: 'Chief complaint, triage level, interventions, disposition',
          complexity: 'high',
          includeVitals: true,
          includeLabs: true,
          timeframe: 'real-time'
        },
        'nursing-note': {
          assessmentDepth: 'rapid',
          systemsReview: ['chief complaint', 'stability', 'interventions'],
          includeDevices: true
        },
        'patient-education': {
          readingLevel: '5th grade',
          focus: 'discharge instructions, red flags, follow-up'
        }
      },
      'outpatient': {
        'sbar': {
          focus: 'Chronic disease management, preventive care, education',
          complexity: 'low',
          includeVitals: false,
          includeLabs: false,
          timeframe: 'visit'
        },
        'nursing-note': {
          assessmentDepth: 'wellness-focused',
          systemsReview: ['health maintenance', 'chronic conditions'],
          includeDevices: false
        },
        'patient-education': {
          readingLevel: '6th grade',
          focus: 'prevention, chronic disease management, lifestyle'
        }
      },
      'home-health': {
        'sbar': {
          focus: 'Home safety, caregiver support, independence, resources',
          complexity: 'moderate',
          includeVitals: true,
          includeLabs: false,
          timeframe: 'weekly'
        },
        'nursing-note': {
          assessmentDepth: 'holistic',
          systemsReview: ['functional status', 'safety', 'caregiver', 'resources'],
          includeDevices: true
        },
        'patient-education': {
          readingLevel: '5th grade',
          focus: 'home safety, caregiver education, emergency contacts',
          includeCaregiver: true
        }
      },
      'skilled-nursing': {
        'sbar': {
          focus: 'Functional status, rehabilitation progress, quality of life',
          complexity: 'moderate',
          includeVitals: true,
          includeLabs: false,
          timeframe: 'daily'
        },
        'nursing-note': {
          assessmentDepth: 'rehabilitation-focused',
          systemsReview: ['mobility', 'ADLs', 'cognition', 'nutrition'],
          includeDevices: true
        },
        'patient-education': {
          readingLevel: '5th grade',
          focus: 'rehabilitation goals, safety, family involvement'
        }
      }
    };

    return templates[careSetting][documentType] || getGenericDefaults(documentType);
  }, [careSetting]);

  return {
    getTemplateDefaults,
    careSetting
  };
}

function getGenericDefaults(documentType: string) {
  const generic: Record<string, any> = {
    'sbar': {
      focus: 'Patient status and care needs',
      complexity: 'moderate',
      includeVitals: true,
      includeLabs: false,
      timeframe: 'shift'
    },
    'nursing-note': {
      assessmentDepth: 'standard',
      systemsReview: ['general'],
      includeDevices: false
    },
    'patient-education': {
      readingLevel: '6th grade',
      focus: 'general health information'
    }
  };

  return generic[documentType] || {};
}
