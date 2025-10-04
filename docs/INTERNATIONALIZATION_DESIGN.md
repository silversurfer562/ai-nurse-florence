# Internationalization (i18n) Design Specification

**Document Version:** 1.0
**Last Updated:** 2025-10-02
**Status:** Active Technical Specification
**Scope:** AI Nurse Florence - Multi-language Support Architecture

---

## Table of Contents

1. [Overview](#overview)
2. [Language Detection & Selection](#language-detection--selection)
3. [Document Language Selection](#document-language-selection)
4. [Supported Languages](#supported-languages)
5. [Implementation Architecture](#implementation-architecture)
6. [User Workflows](#user-workflows)
7. [Technical Specifications](#technical-specifications)
8. [Testing Requirements](#testing-requirements)

---

## 1. Overview

AI Nurse Florence provides comprehensive multi-language support for both the application interface and generated patient documents. The system supports 16 languages and implements intelligent auto-detection with user override capabilities.

### Design Principles

1. **Automatic Detection** - System detects and applies user's browser language
2. **User Control** - Nurses can set their preferred interface language
3. **Patient-Centric** - Easy language selection for each patient document
4. **Smart Defaults** - Document language defaults to nurse's interface language
5. **Persistence** - User preferences saved across sessions

### Two-Language System

The application maintains two distinct language contexts:

| Language Type | Purpose | Scope | Controlled By |
|--------------|---------|-------|---------------|
| **Interface Language** | Application UI (menus, buttons, labels) | Global | Settings → Language |
| **Document Language** | Patient documents (education, discharge instructions) | Per-document | Form language selector |

---

## 2. Language Detection & Selection

### Automatic Detection

**Initial Load Behavior:**
```
1. Check localStorage for saved preference ('i18nextLng')
   ↓
2. If not found, detect from browser navigator.language
   ↓
3. If not supported, check HTML lang attribute
   ↓
4. Fallback to English (en) if all detection fails
```

**Detection Priority (Implemented):**
```typescript
detection: {
  order: ['localStorage', 'navigator', 'htmlTag'],
  caches: ['localStorage'],
  lookupLocalStorage: 'i18nextLng',
}
```

### User Interface Language Selection

**Location:** Settings → Language → Interface Language

**Features:**
- Visual language selector with country flags
- Current language prominently displayed
- Instant application (no page reload required)
- Persisted to localStorage
- Affects all UI text immediately

**Implementation:**
- Uses `react-i18next` for UI translations
- Loads translations from `/locales/{lang}/translation.json`
- Supports React Suspense for async loading

---

## 3. Document Language Selection

### Design Specification

#### Default Behavior

**Patient document language defaults to the nurse's interface language.**

This ensures documents are generated in the language the nurse is working in, providing:
- Automatic and convenient workflow for monolingual practices
- Consistency between interface and generated documents
- Reduced cognitive load (no language context switching)

#### Override Capability

**Nurses must be able to select a patient's preferred language for each document.**

Language selection requirements:
- **Easily accessible** on each document generation form
- **Per-document selection** (not a global setting)
- **Pre-populated** with nurse's interface language as default
- **Quick to change** for multilingual patient populations

#### Settings Page Purpose

**Settings → Language configures the nurse's own GUI/interface language.**

This setting:
- Controls menus, buttons, and all application text
- Becomes the **default** for document generation
- Does **NOT** globally control patient document language
- Persists across sessions

### Implementation Design

#### Workflow Example

```
Scenario: English-speaking nurse treating Spanish-speaking patient

1. Nurse sets interface language to English in Settings
   → Application displays in English

2. Nurse navigates to Patient Education wizard
   → Language selector defaults to English (nurse's language)

3. Nurse changes language selector to Spanish
   → Document will generate in Spanish for patient

4. Nurse generates document
   → Patient receives Spanish education material
   → Nurse continues working in English interface

5. Next patient (English-speaking)
   → Language selector defaults back to English
   → Quick generation without language change
```

#### Technical Approach

**Hook-Based Language Management:**
```typescript
// Provides nurse's interface language as default
const { documentLanguage } = useDocumentLanguage();

// Each form includes language selector
<LanguageAutocomplete
  value={formData.language || documentLanguage}  // Default to nurse's language
  onChange={(lang) => setFormData({ ...formData, language: lang })}
  placeholder="Select patient's preferred language..."
/>
```

**Key Characteristics:**
- Language selection is **per-document session**
- Not globally saved (resets to default for each new document)
- Uses `useDocumentLanguage()` hook for default value
- Easy override via dropdown/autocomplete selector

### User Experience

#### For Monolingual Nurses

**Scenario:** Nurse and all patients speak same language (e.g., English)

```
✅ Benefits:
- No action needed for language selection
- Documents automatically generate in English
- Cleaner workflow, fewer clicks
- Language selector can be ignored
```

#### For Multilingual Practices

**Scenario:** Nurse speaks English, serves English and Spanish patients

```
✅ Benefits:
- Quick access to language selection on every form
- Defaults to English (saves time for English-speaking patients)
- Easy override to Spanish for Spanish-speaking patients
- No need to navigate to Settings repeatedly
- Per-patient language flexibility
```

#### User Flow Diagram

```
┌─────────────────────────────────────────┐
│  Nurse logs in                          │
│  → Auto-detects browser language (EN)   │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Settings → Language (Optional)         │
│  → Nurse sets interface language (EN)   │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Patient Education Form                 │
│  → Language defaults to EN              │
│  → Nurse changes to ES for patient      │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Generate Document                      │
│  → Patient receives Spanish document    │
│  → Nurse continues in English UI        │
└─────────────────────────────────────────┘
```

---

## 4. Supported Languages

### Language Matrix

| Code | Language | Native Name | Primary Region | Status |
|------|----------|-------------|----------------|--------|
| en | English | English | United States | ✅ Complete |
| es | Spanish | Español | Latin America | ✅ Complete |
| zh | Chinese (Mandarin) | 中文 | China | ✅ Complete |
| hi | Hindi | हिन्दी | India | ✅ Complete |
| ar | Arabic | العربية | Middle East | ✅ Complete |
| pt | Portuguese | Português | Brazil, Portugal | ✅ Complete |
| bn | Bengali | বাংলা | Bangladesh, India | ✅ Complete |
| ru | Russian | Русский | Russia | ✅ Complete |
| ja | Japanese | 日本語 | Japan | ✅ Complete |
| pa | Punjabi | ਪੰਜਾਬੀ | India, Pakistan | ✅ Complete |
| de | German | Deutsch | Germany | ✅ Complete |
| ko | Korean | 한국어 | Korea | ✅ Complete |
| fr | French | Français | France, Canada | ✅ Complete |
| vi | Vietnamese | Tiếng Việt | Vietnam | ✅ Complete |
| it | Italian | Italiano | Italy | ✅ Complete |
| tl | Tagalog | Tagalog | Philippines | ✅ Complete |

**Total Languages:** 16

### Language Selection Criteria

Languages selected based on:
1. **Healthcare Demographics** - Most common languages in US healthcare settings
2. **Global Reach** - Major world languages by speaker population
3. **Medical Translation Availability** - Reliable medical terminology resources
4. **Community Need** - Languages requested by healthcare partners

---

## 5. Implementation Architecture

### Frontend Architecture

#### i18n Configuration
**File:** `frontend/src/i18n.ts`

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpBackend from 'i18next-http-backend';

i18n
  .use(HttpBackend)              // Load translations from /locales
  .use(LanguageDetector)         // Auto-detect user language
  .use(initReactI18next)         // React integration
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'es', 'zh', 'hi', 'ar', 'pt', 'bn', 'ru',
                    'ja', 'pa', 'de', 'ko', 'fr', 'vi', 'it', 'tl'],
    interpolation: {
      escapeValue: false,        // React already escapes
    },
    backend: {
      loadPath: '/locales/{{lng}}/translation.json',
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },
    react: {
      useSuspense: true,
    },
  });

export default i18n;
```

#### Document Language Hook
**File:** `frontend/src/hooks/useDocumentLanguage.ts`

```typescript
import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

const STORAGE_KEY = 'documentLanguage';

export function useDocumentLanguage() {
  const { i18n } = useTranslation();

  // Initialize with stored preference or fallback to UI language
  const [documentLanguage, setDocumentLanguageState] = useState<string>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored || i18n.language || 'en';
  });

  // Sync with localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, documentLanguage);
  }, [documentLanguage]);

  const setDocumentLanguage = (language: string) => {
    setDocumentLanguageState(language);
  };

  const resetToUILanguage = () => {
    setDocumentLanguageState(i18n.language);
  };

  const clearDocumentLanguage = () => {
    localStorage.removeItem(STORAGE_KEY);
    setDocumentLanguageState(i18n.language);
  };

  return {
    documentLanguage,
    setDocumentLanguage,
    resetToUILanguage,
    clearDocumentLanguage,
  };
}
```

**Purpose:**
- Provides default document language (nurse's interface language)
- Manages persistence across sessions
- Allows programmatic language updates

#### Language Components

**LanguageSelector Component**
- Used in Settings for interface language selection
- Grid display with country flags
- Instant language switching

**LanguageAutocomplete Component**
- Used in document forms for patient language selection
- Searchable dropdown with all supported languages
- Auto-suggests as user types
- Displays language in native script

### Backend Architecture

#### API Language Support

**Document Generation Endpoints:**
```python
@router.post("/patient-education/generate")
async def generate_patient_education(
    diagnosis: str,
    language: str = Query("en", description="Document language code"),
    reading_level: str = Query("middle", description="Reading level"),
    # ... other parameters
):
    """
    Generate patient education document in specified language.

    Args:
        language: ISO 639-1 language code (en, es, zh, etc.)

    Returns:
        Document content in requested language
    """
    # Language-specific content generation
    content = await generate_content(
        diagnosis=diagnosis,
        language=language,
        reading_level=reading_level
    )

    return {
        "content": content,
        "language": language,
        "format": "pdf"
    }
```

**Language Parameter Pattern:**
- All document generation endpoints accept `language` parameter
- Default to 'en' if not specified
- Validate against supported languages list
- Return language code in response for verification

#### Translation Services

**Medical Term Translation:**
- MeSH (Medical Subject Headings) multilingual support
- ICD-10 code translations
- Medication name translation via RxNorm
- Anatomical term translation

**Content Translation Strategy:**
1. **Template-Based** (Preferred)
   - Pre-translated templates for common conditions
   - Language-specific medical terminology
   - Culturally appropriate health literacy

2. **Dynamic Translation** (Fallback)
   - API-based translation for rare conditions
   - Human-reviewed medical translations
   - Quality assurance checks

---

## 6. User Workflows

### Workflow 1: First-Time User Setup

```
Step 1: User opens application
→ System detects browser language (e.g., Spanish)
→ UI displays in Spanish automatically

Step 2: (Optional) User adjusts interface language
→ Navigate to Settings → Language
→ Select preferred language (e.g., English)
→ UI switches to English immediately

Step 3: User generates first patient document
→ Navigate to Patient Education
→ Language selector defaults to English (user's interface language)
→ User can change to patient's language if different
→ Generate document
```

### Workflow 2: Multilingual Practice

```
Scenario: Emergency Department with diverse patient population

Nurse Interface Language: English

Patient 1 (English-speaking):
→ Patient Education form opens
→ Language defaults to English ✓
→ Generate document in English

Patient 2 (Spanish-speaking):
→ Patient Education form opens
→ Language defaults to English
→ Nurse changes to Spanish
→ Generate document in Spanish

Patient 3 (Mandarin-speaking):
→ Patient Education form opens
→ Language defaults to English
→ Nurse changes to Chinese (zh)
→ Generate document in Mandarin

Patient 4 (English-speaking):
→ Patient Education form opens
→ Language defaults to English ✓
→ Generate document in English
```

**Key Point:** Language resets to nurse's default (English) for each new patient, requiring explicit override only when patient language differs.

### Workflow 3: Settings Management

```
Settings → Language Page Structure:

┌─────────────────────────────────────────┐
│ Interface Language                      │
│ ─────────────────────────────────────── │
│ Current: English                        │
│ [Language Selector Dropdown]            │
│                                         │
│ Controls: Menus, buttons, all UI text  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Supported Languages (16 Total)         │
│ ─────────────────────────────────────── │
│ 🇺🇸 English    🇪🇸 Spanish             │
│ 🇨🇳 Chinese    🇮🇳 Hindi               │
│ 🇸🇦 Arabic     🇵🇹 Portuguese           │
│ [... all 16 languages with flags]      │
└─────────────────────────────────────────┘

Note: Patient document language is selected
      per-document in generation forms.
```

---

## 7. Technical Specifications

### Frontend Integration

#### Usage in Components

```typescript
// Example: Patient Education Component
import { useTranslation } from 'react-i18next';
import { useDocumentLanguage } from '../hooks/useDocumentLanguage';

export default function PatientEducation() {
  const { t } = useTranslation();  // UI translations
  const { documentLanguage } = useDocumentLanguage();  // Default doc language
  const [formData, setFormData] = useState({
    language: documentLanguage,  // Initialize with default
  });

  return (
    <div>
      <h1>{t('patientEducation.title')}</h1>  {/* UI text in nurse's language */}

      <LanguageAutocomplete
        value={formData.language}
        onChange={(lang) => setFormData({ ...formData, language: lang })}
        placeholder={t('patientEducation.selectLanguage')}
      />
    </div>
  );
}
```

#### Translation Keys Structure

**File:** `/locales/{lang}/translation.json`

```json
{
  "common": {
    "appName": "AI Nurse Florence",
    "loading": "Loading...",
    "error": "Error",
    "save": "Save",
    "cancel": "Cancel"
  },
  "patientEducation": {
    "title": "Patient Education",
    "selectLanguage": "Select patient's preferred language",
    "generateButton": "Generate Document",
    "downloadPDF": "Download PDF"
  },
  "settings": {
    "language": {
      "interfaceLanguage": "Interface Language",
      "currentLanguage": "Current Language",
      "selectLanguage": "Select Language"
    }
  }
}
```

### Backend Integration

#### Language Validation

```python
from typing import Literal

SUPPORTED_LANGUAGES = Literal[
    "en", "es", "zh", "hi", "ar", "pt", "bn", "ru",
    "ja", "pa", "de", "ko", "fr", "vi", "it", "tl"
]

def validate_language(language: str) -> str:
    """Validate and normalize language code."""
    supported = [
        "en", "es", "zh", "hi", "ar", "pt", "bn", "ru",
        "ja", "pa", "de", "ko", "fr", "vi", "it", "tl"
    ]

    lang = language.lower().strip()

    if lang not in supported:
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Supported languages: {', '.join(supported)}"
        )

    return lang
```

#### Document Generation with Language

```python
async def generate_patient_education(
    diagnosis: str,
    language: str,
    reading_level: str,
    format: str = "pdf"
) -> Dict[str, Any]:
    """
    Generate patient education document in specified language.

    Implementation:
    1. Validate language code
    2. Load language-specific template
    3. Translate medical terms
    4. Generate content at appropriate reading level
    5. Format as PDF/DOCX/TXT
    """

    # Validate language
    language = validate_language(language)

    # Load template for language
    template = load_template(
        template_type="patient_education",
        language=language,
        reading_level=reading_level
    )

    # Translate medical terminology
    diagnosis_translated = translate_medical_term(
        term=diagnosis,
        target_language=language
    )

    # Generate content
    content = await generate_content(
        template=template,
        diagnosis=diagnosis_translated,
        language=language
    )

    # Format document
    document = format_document(
        content=content,
        format=format,
        language=language
    )

    return {
        "document": document,
        "language": language,
        "diagnosis": diagnosis_translated
    }
```

### Data Storage

#### localStorage Schema

```typescript
// Browser localStorage keys

interface LocalStorageSchema {
  // UI language (managed by i18next)
  i18nextLng: string;  // e.g., "en", "es"

  // Document language default (managed by useDocumentLanguage)
  documentLanguage: string;  // e.g., "en", "es"

  // Example values:
  // i18nextLng: "en" → Nurse's interface in English
  // documentLanguage: "en" → Documents default to English
}
```

**Persistence Rules:**
- `i18nextLng`: Persists across sessions, affects all UI
- `documentLanguage`: Persists as default, can be overridden per-document
- Both update immediately on change
- Clear on logout (optional, based on security requirements)

---

## 8. Testing Requirements

### Functional Testing

#### Language Detection Tests

```typescript
describe('Language Detection', () => {
  it('should detect browser language on first load', () => {
    // Mock navigator.language = 'es'
    // Verify UI displays in Spanish
  });

  it('should use localStorage language if available', () => {
    // Set localStorage.i18nextLng = 'fr'
    // Verify UI displays in French
  });

  it('should fallback to English if language unsupported', () => {
    // Mock navigator.language = 'xy' (unsupported)
    // Verify UI displays in English
  });
});
```

#### Document Language Tests

```typescript
describe('Document Language Selection', () => {
  it('should default to nurse interface language', () => {
    // Set UI language to Spanish
    // Open Patient Education form
    // Verify language selector shows Spanish
  });

  it('should allow per-document override', () => {
    // Set UI language to English
    // Open form, change language to Chinese
    // Verify document generates in Chinese
    // Open new form
    // Verify language resets to English
  });

  it('should validate language code in API', () => {
    // Send invalid language code
    // Verify error response
  });
});
```

#### Settings Tests

```typescript
describe('Settings - Language Management', () => {
  it('should display current interface language', () => {
    // Navigate to Settings → Language
    // Verify current language displayed correctly
  });

  it('should change interface language immediately', () => {
    // Change language in Settings
    // Verify UI updates without refresh
  });

  it('should persist language preference', () => {
    // Change language
    // Refresh page
    // Verify language persists
  });
});
```

### User Acceptance Testing

#### Test Scenarios

**Scenario 1: Monolingual Nurse**
```
Precondition: Nurse speaks only English
Steps:
1. Login → UI auto-detects English ✓
2. Generate patient document → Defaults to English ✓
3. Complete workflow without language changes ✓
Expected: Seamless experience, no language interaction needed
```

**Scenario 2: Bilingual Nurse**
```
Precondition: Nurse speaks English & Spanish
Steps:
1. Login → UI in English ✓
2. Patient 1 (English): Generate document in English ✓
3. Patient 2 (Spanish): Change language to Spanish → Generate ✓
4. Patient 3 (English): Language resets to English ✓
Expected: Quick language switching per patient
```

**Scenario 3: Language Preference Change**
```
Steps:
1. Login → UI in English
2. Settings → Change to Spanish ✓
3. Verify all UI updates to Spanish ✓
4. Generate document → Defaults to Spanish ✓
5. Override to Chinese for patient → Generates in Chinese ✓
6. Next document → Resets to Spanish default ✓
Expected: Settings change affects UI and document defaults
```

### Accessibility Testing

- [ ] Screen reader support for language selectors
- [ ] Keyboard navigation for language dropdown
- [ ] ARIA labels for language options
- [ ] RTL (Right-to-Left) support for Arabic
- [ ] Font rendering for non-Latin scripts (Chinese, Arabic, Hindi)

### Performance Testing

- [ ] Translation file lazy loading
- [ ] Language switching response time (<100ms)
- [ ] Memory usage with multiple languages loaded
- [ ] Bundle size impact per language

---

## Implementation Checklist

### Phase 1: Core Infrastructure ✅
- [x] i18n configuration with auto-detection
- [x] Language selector components
- [x] Translation file structure
- [x] localStorage persistence

### Phase 2: Document Language Management ✅
- [x] useDocumentLanguage hook
- [x] Settings page language section
- [x] Default language logic

### Phase 3: Form Integration 🔄
- [x] Patient Education language selector
- [ ] Discharge Instructions language selector
- [ ] Medication Guide language selector
- [ ] SBAR Report language selector
- [ ] Care Plan language selector

### Phase 4: Backend Integration
- [ ] Language validation utilities
- [ ] Template loading by language
- [ ] Medical term translation service
- [ ] Document generation with language support

### Phase 5: Testing & QA
- [ ] Automated tests for language detection
- [ ] API endpoint language validation tests
- [ ] User acceptance testing scenarios
- [ ] Accessibility compliance verification

---

## Maintenance & Updates

### Adding New Languages

**Process:**
1. Update `supportedLngs` array in `i18n.ts`
2. Create translation file: `/locales/{code}/translation.json`
3. Add language to Settings display with flag
4. Add to backend `SUPPORTED_LANGUAGES` list
5. Create/obtain medical terminology translations
6. Test document generation
7. Update documentation

### Translation Updates

**Workflow:**
1. Identify missing or incorrect translations
2. Update JSON files in `/locales/{lang}/`
3. Test in application
4. Deploy via standard release process

### Quality Assurance

- Native speaker review for medical accuracy
- Cultural appropriateness assessment
- Reading level verification
- Medical terminology validation against standards (ICD-10, MeSH)

---

## References

### External Documentation

- [react-i18next Documentation](https://react.i18next.com/)
- [i18next Language Detector](https://github.com/i18next/i18next-browser-languageDetector)
- [WCAG 2.1 Language of Page](https://www.w3.org/WAI/WCAG21/Understanding/language-of-page.html)
- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

### Internal Documentation

- Language detection: [`frontend/src/i18n.ts`](../frontend/src/i18n.ts)
- Document language hook: [`frontend/src/hooks/useDocumentLanguage.ts`](../frontend/src/hooks/useDocumentLanguage.ts)
- Settings implementation: [`frontend/src/pages/Settings.tsx`](../frontend/src/pages/Settings.tsx)
- Patient Education: [`frontend/src/pages/PatientEducation.tsx`](../frontend/src/pages/PatientEducation.tsx)

### Related Specifications

- [LANGUAGE_SETTINGS_REFACTOR.md](../LANGUAGE_SETTINGS_REFACTOR.md) - Implementation details
- [COMPREHENSIVE_IMPLEMENTATION_PLAN.md](../COMPREHENSIVE_IMPLEMENTATION_PLAN.md) - Overall project roadmap
- [I18N_IMPLEMENTATION_SUMMARY.md](../I18N_IMPLEMENTATION_SUMMARY.md) - Translation infrastructure

---

**Document Status:** Living Document - Update as requirements evolve
**Review Schedule:** Quarterly or upon major feature additions
**Owner:** Development Team
**Stakeholders:** Clinical Staff, UX Team, Product Management
