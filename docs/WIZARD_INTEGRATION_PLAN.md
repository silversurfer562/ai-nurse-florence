# Wizard Integration Plan - Care Setting Framework

**Date:** October 2, 2025
**Status:** 📋 Planning Complete, Ready for Implementation
**Objective:** Integrate Care Setting Framework into all document generation wizards

---

## Table of Contents

1. [Overview](#overview)
2. [Wizard Inventory](#wizard-inventory)
3. [Integration Strategy](#integration-strategy)
4. [Implementation Steps](#implementation-steps)
5. [Testing Plan](#testing-plan)
6. [Rollout Strategy](#rollout-strategy)

---

## Overview

### Goal

Integrate the Care Setting Framework into all document generation wizards to provide:
- **Setting-specific template defaults**
- **Visual context indicators** showing current care setting
- **Automatic API parameter injection** for care_setting
- **Smart validation** based on care environment

### Success Criteria

- ✅ All wizards display current care setting
- ✅ Template defaults adapt to selected setting
- ✅ API calls include care_setting parameter
- ✅ Users can override setting if needed
- ✅ Setting persists through multi-step workflows
- ✅ No regression in existing functionality

---

## Wizard Inventory

### Identified Wizards (7 Total)

| Wizard | File | Current Status | Priority | Complexity |
|--------|------|----------------|----------|------------|
| **SBAR Wizard** | `SbarWizard.js` | Legacy JS | HIGH | Medium |
| **Patient Education** | `PatientEducationWizard.js` | Legacy JS | HIGH | Low |
| **Enhanced Patient Ed** | `EnhancedPatientEducationWizard.js` | Legacy JS | HIGH | Medium |
| **Discharge Instructions** | `DischargeInstructionsWizard.js` | Legacy JS | MEDIUM | Medium |
| **Medication Guide** | `MedicationGuideWizard.js` | Legacy JS | MEDIUM | Low |
| **Incident Report** | `IncidentReportWizard.js` | Legacy JS | LOW | Low |
| **Base Wizard** | `BaseWizard.js` | Legacy JS | N/A | N/A (shared) |

### Classification by Care Setting Relevance

**High Relevance (Priority 1):**
- ✅ SBAR Wizard - Different focus areas per setting
- ✅ Patient Education - Reading level and content vary by setting
- ✅ Discharge Instructions - Home vs facility instructions differ

**Medium Relevance (Priority 2):**
- ⚠️ Medication Guide - Safety considerations vary
- ⚠️ Incident Report - Setting-specific incident types

**Low Relevance (Priority 3):**
- ℹ️ Base Wizard - Shared functionality (update if needed)

---

## Integration Strategy

### Approach: Gradual Enhancement

We'll use a **non-breaking, additive approach**:

1. **Preserve existing functionality** - All wizards continue to work without care setting
2. **Add care setting awareness** - Wizards detect and use care setting when available
3. **Provide visual context** - Show current care setting in wizard header
4. **Apply smart defaults** - Use setting-specific templates when setting is selected
5. **Allow overrides** - Users can change setting or customize templates

### Technical Pattern

Each wizard will follow this pattern:

```javascript
// 1. Import care setting hooks
import { useCareSettings, useCareSettingTemplates } from '../../hooks/useCareSettings';

// 2. Get care setting context
const { careSetting, getSettingLabel, getSettingIcon } = useCareSettings();
const { getTemplateDefaults } = useCareSettingTemplates();

// 3. Load setting-specific defaults
useEffect(() => {
  if (careSetting) {
    const defaults = getTemplateDefaults('sbar'); // or 'patient-education', etc.
    setFormData(prevData => ({
      ...prevData,
      ...defaults
    }));
  }
}, [careSetting]);

// 4. Show care setting context in UI
<div className="mb-4 p-3 bg-blue-50 rounded-lg">
  <i className={`fas ${getSettingIcon()} mr-2`}></i>
  Creating document for <strong>{getSettingLabel()}</strong> care setting
  <button onClick={() => /* open care setting modal */}>Change</button>
</div>

// 5. Include in API calls
const apiParams = {
  ...formData,
  care_setting: careSetting
};
```

---

## Implementation Steps

### Phase 1: High Priority Wizards (Week 1)

#### Step 1.1: SBAR Wizard Integration

**File:** `frontend/src/components/wizards/SbarWizard.js`

**Changes:**

1. **Import care setting hooks**
```javascript
import { useCareSettings, useCareSettingTemplates } from '../../hooks/useCareSettings';
```

2. **Add care setting state**
```javascript
const { careSetting, getSettingLabel, getSettingIcon } = useCareSettings();
const { getTemplateDefaults } = useCareSettingTemplates();
```

3. **Load setting-specific defaults**
```javascript
useEffect(() => {
  if (careSetting) {
    const defaults = getTemplateDefaults('sbar');
    setFormData(prevData => ({
      ...prevData,
      focusAreas: defaults.focus || prevData.focusAreas,
      complexity: defaults.complexity || prevData.complexity,
      timeframe: defaults.timeframe || prevData.timeframe,
      includeVitals: defaults.includeVitals ?? prevData.includeVitals,
      includeLabs: defaults.includeLabs ?? prevData.includeLabs
    }));
  }
}, [careSetting]);
```

4. **Add visual context indicator**
```javascript
{careSetting && (
  <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <i className={`fas ${getSettingIcon()} text-blue-600`}></i>
        <span className="text-sm text-gray-700">
          Creating SBAR for <strong>{getSettingLabel()}</strong> care setting
        </span>
      </div>
      <button
        onClick={() => setShowCareSettingModal(true)}
        className="text-sm text-blue-600 hover:text-blue-800 underline"
      >
        Change Setting
      </button>
    </div>
  </div>
)}
```

5. **Include in API call**
```javascript
const generateSBAR = async () => {
  const response = await fetch('/api/v1/sbar/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...formData,
      care_setting: careSetting
    })
  });
};
```

**Expected Outcome:**
- SBAR wizard shows current care setting
- ICU defaults: High complexity, hourly timeframe, includes labs
- Home Health defaults: Moderate complexity, weekly timeframe, includes caregiver notes

**Testing Checklist:**
- [ ] Select ICU setting → Verify high complexity default
- [ ] Select Home Health → Verify caregiver education included
- [ ] Generate SBAR → Verify care_setting in API call
- [ ] Switch setting mid-workflow → Verify templates update

---

#### Step 1.2: Patient Education Wizard Integration

**File:** `frontend/src/components/wizards/PatientEducationWizard.js`

**Changes:**

1. **Import care setting hooks**
2. **Load setting-specific reading level**
```javascript
useEffect(() => {
  if (careSetting) {
    const defaults = getTemplateDefaults('patient-education');
    setReadingLevel(defaults.readingLevel || '6th grade');
    setIncludeCaregiver(defaults.includeCaregiver || false);
  }
}, [careSetting]);
```

3. **Setting-specific focus areas**
```javascript
const getFocusOptions = () => {
  if (!careSetting) return defaultFocusOptions;

  const settingFocus = {
    'icu': ['Equipment explanation', 'ICU procedures', 'Family communication'],
    'home-health': ['Home safety', 'Caregiver education', 'Emergency contacts'],
    'emergency': ['Discharge instructions', 'Red flags', 'Follow-up care'],
    // ... etc
  };

  return settingFocus[careSetting] || defaultFocusOptions;
};
```

4. **Caregiver education toggle**
```javascript
{careSetting === 'home-health' && (
  <div className="form-group">
    <label>
      <input
        type="checkbox"
        checked={includeCaregiver}
        onChange={(e) => setIncludeCaregiver(e.target.checked)}
      />
      Include separate caregiver education section
    </label>
  </div>
)}
```

**Expected Outcome:**
- ICU: 8th grade reading level default
- Home Health: 5th grade reading level, caregiver section enabled
- Emergency: 5th grade reading level, focus on red flags

**Testing Checklist:**
- [ ] ICU → Verify 8th grade default
- [ ] Home Health → Verify caregiver checkbox appears
- [ ] Emergency → Verify red flags in focus options
- [ ] API call includes care_setting

---

#### Step 1.3: Discharge Instructions Wizard Integration

**File:** `frontend/src/components/wizards/DischargeInstructionsWizard.js`

**Changes:**

1. **Setting-specific discharge focus**
```javascript
const getDischargeChecklist = () => {
  const checklists = {
    'icu': [
      'Critical care equipment removal timeline',
      'Step-down unit expectations',
      'Warning signs requiring readmission',
      'Follow-up with specialists'
    ],
    'med-surg': [
      'Wound care instructions',
      'Activity restrictions',
      'Medication schedule',
      'Follow-up appointments'
    ],
    'home-health': [
      'Home safety modifications',
      'Caregiver responsibilities',
      'Equipment delivery and setup',
      'Next home visit schedule'
    ],
    'emergency': [
      'Red flags requiring immediate return',
      'Primary care follow-up within 24-48 hours',
      'Medication prescriptions to fill',
      'Activity recommendations'
    ]
  };

  return checklists[careSetting] || checklists['med-surg'];
};
```

2. **Setting-specific follow-up timeframes**
```javascript
const getFollowUpGuidance = () => {
  const guidance = {
    'icu': 'Follow up with specialist within 1 week',
    'med-surg': 'Follow up with primary care within 1-2 weeks',
    'emergency': 'Follow up within 24-48 hours or as directed',
    'home-health': 'Next home visit scheduled',
    'outpatient': 'Follow up as scheduled',
    'skilled-nursing': 'Ongoing monitoring by facility staff'
  };

  return guidance[careSetting];
};
```

**Expected Outcome:**
- Different discharge checklists per setting
- Appropriate follow-up timeframes
- Setting-specific safety warnings

---

### Phase 2: Medium Priority Wizards (Week 2)

#### Step 2.1: Medication Guide Wizard

**File:** `frontend/src/components/wizards/MedicationGuideWizard.js`

**Changes:**

1. **Setting-specific medication safety**
```javascript
const getSafetyConsiderations = () => {
  const safety = {
    'icu': [
      'IV medication administration in critical care',
      'Continuous infusion monitoring',
      'High-alert medication protocols'
    ],
    'home-health': [
      'Proper medication storage at home',
      'Caregiver administration training',
      'When to call for medication questions'
    ],
    'skilled-nursing': [
      'Medication administration record (MAR)',
      'Scheduled medication times',
      'Medication disposal procedures'
    ]
  };

  return safety[careSetting] || [];
};
```

**Expected Outcome:**
- ICU: Focus on IV medications and high-alert drugs
- Home Health: Focus on caregiver training and storage
- Outpatient: Focus on self-administration

---

#### Step 2.2: Incident Report Wizard

**File:** `frontend/src/components/wizards/IncidentReportWizard.js`

**Changes:**

1. **Setting-specific incident categories**
```javascript
const getIncidentCategories = () => {
  const categories = {
    'icu': ['Device malfunction', 'Line/tube dislodgement', 'Hemodynamic event'],
    'med-surg': ['Fall', 'Medication error', 'Wound complication'],
    'home-health': ['Fall in home', 'Caregiver error', 'Equipment failure'],
    'emergency': ['Patient elopement', 'Violent behavior', 'Critical delay'],
    'skilled-nursing': ['Fall', 'Skin integrity', 'Behavioral incident']
  };

  return categories[careSetting] || categories['med-surg'];
};
```

**Expected Outcome:**
- Setting-appropriate incident types
- Relevant reporting fields per setting

---

### Phase 3: Base Wizard Updates (If Needed)

#### Step 3.1: Review BaseWizard.js

**File:** `frontend/src/components/wizards/BaseWizard.js`

**Analysis:**
- Check if BaseWizard provides shared functionality
- If yes, consider adding care setting awareness to base class
- If no, skip this step

**Potential Enhancement:**
```javascript
// Add care setting props to BaseWizard if it's a parent component
export default function BaseWizard({
  showCareSettingContext = true,
  ...otherProps
}) {
  const { careSetting, getSettingLabel } = useCareSettings();

  return (
    <div>
      {showCareSettingContext && careSetting && (
        <CareSettingContextBanner />
      )}
      {/* Rest of wizard */}
    </div>
  );
}
```

---

## Testing Plan

### Unit Tests

**Test Care Setting Hook Integration:**

```javascript
describe('SBAR Wizard with Care Setting', () => {
  it('loads ICU defaults when ICU setting is selected', () => {
    sessionStorage.setItem('ai-nurse-florence-care-setting-session', 'icu');

    render(<SbarWizard />);

    expect(screen.getByText(/Creating SBAR for.*ICU/i)).toBeInTheDocument();
    expect(screen.getByLabelText('Complexity')).toHaveValue('high');
    expect(screen.getByLabelText('Include Labs')).toBeChecked();
  });

  it('loads Home Health defaults when Home Health setting is selected', () => {
    sessionStorage.setItem('ai-nurse-florence-care-setting-session', 'home-health');

    render(<SbarWizard />);

    expect(screen.getByText(/Creating SBAR for.*Home Health/i)).toBeInTheDocument();
    expect(screen.getByLabelText('Complexity')).toHaveValue('moderate');
    expect(screen.getByLabelText('Include Caregiver Notes')).toBeInTheDocument();
  });

  it('includes care_setting in API call', async () => {
    sessionStorage.setItem('ai-nurse-florence-care-setting-session', 'icu');

    render(<SbarWizard />);
    fireEvent.click(screen.getByText('Generate SBAR'));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          body: expect.stringContaining('"care_setting":"icu"')
        })
      );
    });
  });
});
```

### Integration Tests

**Test Complete Workflow:**

```javascript
describe('End-to-End Care Setting Workflow', () => {
  it('persists care setting through multi-step document creation', async () => {
    // 1. User selects care setting
    render(<CareSettingModal isOpen={true} onSelect={mockSelect} />);
    fireEvent.click(screen.getByText('ICU'));

    // 2. Navigate to SBAR wizard
    const { rerender } = render(<SbarWizard />);

    // 3. Verify setting persists
    expect(screen.getByText(/ICU/i)).toBeInTheDocument();

    // 4. Generate document
    fireEvent.click(screen.getByText('Generate SBAR'));

    // 5. Navigate to Patient Education wizard
    rerender(<PatientEducationWizard />);

    // 6. Verify setting still persists
    expect(screen.getByText(/ICU/i)).toBeInTheDocument();
  });
});
```

### Manual Testing Checklist

**For Each Wizard:**

- [ ] **No Care Setting Selected**
  - [ ] Wizard works without care setting (backward compatible)
  - [ ] Default values load correctly
  - [ ] No care setting banner displayed

- [ ] **ICU Care Setting**
  - [ ] ICU-specific defaults load
  - [ ] Care setting banner shows "ICU"
  - [ ] Template complexity is "high"
  - [ ] API call includes `care_setting: "icu"`

- [ ] **Home Health Care Setting**
  - [ ] Home Health defaults load
  - [ ] Caregiver options appear (where relevant)
  - [ ] Reading level defaults to 5th grade
  - [ ] API call includes `care_setting: "home-health"`

- [ ] **Setting Switch Mid-Workflow**
  - [ ] Click "Change Setting" button
  - [ ] Modal opens
  - [ ] Select different setting
  - [ ] Templates update to new setting
  - [ ] Workflow continues without errors

---

## Rollout Strategy

### Phase 1: Soft Launch (Week 1-2)

**Target:** Internal testing only

1. Deploy to development environment
2. Test all wizards with each care setting
3. Verify API integration
4. Fix any bugs found

**Success Criteria:**
- All wizards work with care setting
- No regressions in existing functionality
- API calls include care_setting parameter

---

### Phase 2: Beta Launch (Week 3)

**Target:** Select beta users

1. Deploy to staging environment
2. Invite 10-20 beta testers (mix of care settings)
3. Collect feedback on template defaults
4. Monitor usage analytics

**Success Criteria:**
- Positive user feedback
- Template defaults are appropriate
- No critical bugs
- Setting persistence works reliably

---

### Phase 3: Production Launch (Week 4)

**Target:** All users

1. Deploy to production
2. Monitor error rates
3. Track care setting usage
4. Collect user feedback

**Success Criteria:**
- <1% error rate
- >80% of users select care setting
- Template defaults reduce customization time
- Positive user satisfaction scores

---

## Monitoring & Analytics

### Metrics to Track

**User Behavior:**
- Care setting selection rate
- Most common settings by user
- Setting switch frequency
- Time to first document (with vs without care setting)

**Template Usage:**
- Default acceptance rate (users keep defaults vs customize)
- Most customized fields by setting
- Template effectiveness scores

**Technical Metrics:**
- API response times with care_setting parameter
- Error rates by care setting
- Wizard completion rates

### Analytics Dashboard

```javascript
// Track care setting selection
analytics.track('care_setting_selected', {
  setting: careSetting,
  wizard: 'sbar',
  timestamp: Date.now()
});

// Track template customization
analytics.track('template_customized', {
  setting: careSetting,
  wizard: 'sbar',
  field: 'complexity',
  defaultValue: 'high',
  userValue: 'moderate'
});

// Track wizard completion
analytics.track('wizard_completed', {
  setting: careSetting,
  wizard: 'sbar',
  duration: timeSpent,
  defaultsKept: fieldsUsingDefaults.length,
  defaultsChanged: fieldsCustomized.length
});
```

---

## Risk Mitigation

### Potential Risks

**Risk 1: Breaking Existing Workflows**
- **Mitigation:** Preserve all existing functionality, make care setting optional
- **Test:** Extensive regression testing without care setting selected

**Risk 2: Inappropriate Template Defaults**
- **Mitigation:** Beta testing with nurses from each care setting
- **Test:** User feedback surveys, template customization tracking

**Risk 3: Performance Impact**
- **Mitigation:** Care setting hooks are lightweight, use local storage
- **Test:** Performance benchmarks before/after integration

**Risk 4: User Confusion**
- **Mitigation:** Clear visual indicators, educational onboarding
- **Test:** User testing sessions, feedback collection

---

## Success Metrics

### Short-Term (1 Month)

- ✅ >80% of active users select a care setting
- ✅ <5 minutes average time to first document creation
- ✅ >70% of users keep default templates (indicates good defaults)
- ✅ <1% error rate in wizard workflows

### Medium-Term (3 Months)

- ✅ >90% care setting selection rate
- ✅ Positive user satisfaction (4+/5 rating)
- ✅ Reduced support tickets about template customization
- ✅ Epic integration testing successful

### Long-Term (6 Months)

- ✅ Care setting becomes core part of user workflow
- ✅ Template defaults require minimal customization
- ✅ Setting-specific features drive user engagement
- ✅ Epic auto-detection implemented and working

---

## Documentation Updates

### User-Facing Documentation

- [ ] Update user guide with care setting instructions
- [ ] Create video tutorial on selecting care settings
- [ ] Add FAQ about care settings
- [ ] Update wizard documentation with setting-specific guidance

### Developer Documentation

- [ ] Update component documentation
- [ ] Add care setting integration examples
- [ ] Document template default schema
- [ ] Update API documentation with care_setting parameter

---

## Conclusion

This plan provides a structured approach to integrating the Care Setting Framework into all document generation wizards. The phased rollout minimizes risk while ensuring thorough testing and user feedback.

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 1 implementation (SBAR, Patient Education, Discharge Instructions)
3. Test thoroughly in development
4. Proceed to beta launch

---

**Status:** 📋 Plan Complete - Ready for Implementation
**Estimated Timeline:** 4 weeks to production
**Priority:** HIGH (Epic Integration Dependency)
