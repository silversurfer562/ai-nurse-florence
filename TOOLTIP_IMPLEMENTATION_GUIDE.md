# Tooltip Implementation Guide - AI Nurse Florence

**Date**: September 30, 2025
**Purpose**: Standardize tooltip implementation across all pages for consistent user experience

## Overview

Tooltips have been implemented in the SBAR Wizard and should be added to all interactive elements across the application. This guide provides standards and examples.

## Tooltip CSS Component

A reusable tooltip CSS file has been created at `/static/css/tooltips.css`

### To Use in Any Page:

```html
<head>
    <!-- Add to your existing stylesheets -->
    <link rel="stylesheet" href="/static/css/tooltips.css">
</head>
```

## Basic Tooltip Structure

```html
<div class="tooltip">
    <button class="your-button-classes">
        Button Text
    </button>
    <span class="tooltiptext">This is the helpful tooltip text that appears on hover</span>
</div>
```

## Tooltip Best Practices

### When to Add Tooltips:
1. **Action Buttons** - Explain what happens when clicked
2. **Navigation Controls** - Describe where the user will go
3. **AI Features** - Clarify what the AI will do
4. **Icons** - Explain icon meaning (especially if not obvious)
5. **Dropdowns/Selects** - Describe purpose and options
6. **Safety Features** - Highlight important warnings or checks

### When NOT to Add Tooltips:
1. **Self-explanatory text buttons** - If button says "Save", tooltip saying "Save" is redundant
2. **Labels** - Field labels should be clear without tooltips
3. **Decorative elements** - Don't add tooltips to non-interactive elements

### Tooltip Text Guidelines:
1. **Be concise** - 1-2 sentences maximum
2. **Action-oriented** - Start with verbs when possible
3. **Explain benefit** - Tell user why they'd use this
4. **Avoid jargon** - Unless necessary for clinical context
5. **No redundancy** - Don't repeat what's already visible

## Page-by-Page Tooltip Recommendations

### 1. index.html (Main Dashboard)

#### Header Controls
```html
<!-- Language Selector -->
<div class="tooltip">
    <select id="languageSelector" class="border border-gray-300 rounded-lg px-3 py-2...">
        <option value="en">English</option>
        ...
    </select>
    <span class="tooltiptext">Select your preferred language for the interface</span>
</div>

<!-- Connection Status -->
<div class="tooltip">
    <div id="connectionStatus" class="flex items-center...">
        <div class="w-3 h-3 bg-gray-400 rounded-full pulse-dot"></div>
        <span class="text-sm text-gray-600 font-medium">Connecting...</span>
    </div>
    <span class="tooltiptext">Real-time connection status to AI services</span>
</div>
```

#### Feature Buttons
```html
<!-- Clinical Workspace -->
<div class="tooltip">
    <button onclick="openDedicatedInterface('clinical-workspace.html')"
            class="clinical-feature-btn...">
        <div class="text-center">
            <i class="fas fa-th-large text-3xl mb-3"></i>
            <h3 class="font-bold text-lg mb-2">Clinical Workspace</h3>
            <p class="text-sm opacity-90">Integrated clinical tools dashboard</p>
        </div>
    </button>
    <span class="tooltiptext">Access all clinical tools and features in one unified workspace</span>
</div>

<!-- SBAR Wizard -->
<div class="tooltip">
    <button onclick="openDedicatedInterface('sbar-wizard.html')"
            class="clinical-feature-btn...">
        ...
    </button>
    <span class="tooltiptext">Create structured SBAR reports with AI assistance for patient handoffs</span>
</div>

<!-- Drug Interactions -->
<div class="tooltip">
    <button onclick="openDedicatedInterface('drug-interactions.html')"
            class="clinical-feature-btn...">
        ...
    </button>
    <span class="tooltiptext">Check for dangerous drug interactions and get safety recommendations</span>
</div>

<!-- Disease Lookup -->
<div class="tooltip">
    <button onclick="openDedicatedInterface('disease-lookup.html')"
            class="clinical-feature-btn...">
        ...
    </button>
    <span class="tooltiptext">Search evidence-based disease information from authoritative medical databases</span>
</div>

<!-- Dosage Calculator -->
<div class="tooltip">
    <button onclick="openWizardInterface('dosage_calculation')"
            class="clinical-feature-btn...">
        ...
    </button>
    <span class="tooltiptext">Calculate safe medication dosages based on patient weight and parameters</span>
</div>
```

### 2. drug-interactions.html

```html
<!-- Search Button -->
<div class="tooltip">
    <button id="checkInteractions" class="px-6 py-3 bg-blue-600...">
        <i class="fas fa-search mr-2"></i>Check Interactions
    </button>
    <span class="tooltiptext">Search for interactions between selected medications using AI analysis</span>
</div>

<!-- Clear Button -->
<div class="tooltip">
    <button onclick="clearMedications()" class="px-4 py-2 bg-gray-500...">
        <i class="fas fa-times mr-2"></i>Clear All
    </button>
    <span class="tooltiptext">Remove all medications and start a new interaction check</span>
</div>

<!-- Add Medication Input -->
<div class="tooltip tooltip-bottom">
    <input type="text" id="drugInput"
           placeholder="Type medication name..."
           class="flex-1 p-3...">
    <span class="tooltiptext">Start typing to see medication suggestions. Press Enter or click Add to include in check.</span>
</div>
```

### 3. disease-lookup.html

```html
<!-- Search Button -->
<div class="tooltip">
    <button onclick="searchDisease()" class="px-6 py-3 bg-blue-600...">
        <i class="fas fa-search mr-2"></i>Search Disease
    </button>
    <span class="tooltiptext">Search authoritative medical databases for disease information and evidence</span>
</div>

<!-- View Details Button (in results) -->
<div class="tooltip">
    <button onclick="viewDiseaseDetails('diabetes')" class="text-blue-600...">
        <i class="fas fa-info-circle mr-1"></i>View Details
    </button>
    <span class="tooltiptext">See comprehensive information including symptoms, treatments, and clinical trials</span>
</div>
```

### 4. dosage-calculator.html

```html
<!-- Calculate Button -->
<div class="tooltip">
    <button onclick="calculateDosage()" class="px-6 py-3 bg-green-600...">
        <i class="fas fa-calculator mr-2"></i>Calculate Dosage
    </button>
    <span class="tooltiptext">Calculate safe medication dosage based on patient parameters and drug guidelines</span>
</div>

<!-- Clear Button -->
<div class="tooltip">
    <button onclick="clearForm()" class="px-4 py-2 bg-gray-500...">
        <i class="fas fa-redo mr-2"></i>Reset
    </button>
    <span class="tooltiptext">Clear all fields and start a new dosage calculation</span>
</div>

<!-- Weight Unit Toggle -->
<div class="tooltip">
    <select id="weightUnit" class="border border-gray-300...">
        <option value="kg">kg</option>
        <option value="lb">lb</option>
    </select>
    <span class="tooltiptext">Select weight measurement unit for accurate dosage calculation</span>
</div>
```

### 5. chat.html (Clinical Chat Interface)

```html
<!-- Send Message Button -->
<div class="tooltip">
    <button id="sendBtn" class="px-6 py-3 bg-blue-600...">
        <i class="fas fa-paper-plane"></i>
    </button>
    <span class="tooltiptext">Send your clinical question to AI assistant for evidence-based guidance</span>
</div>

<!-- Clear Chat Button -->
<div class="tooltip">
    <button onclick="clearChat()" class="px-4 py-2 bg-gray-500...">
        <i class="fas fa-trash-alt mr-2"></i>Clear Chat
    </button>
    <span class="tooltiptext">Delete conversation history and start fresh discussion</span>
</div>

<!-- Export Chat Button -->
<div class="tooltip">
    <button onclick="exportChat()" class="px-4 py-2 bg-green-600...">
        <i class="fas fa-download mr-2"></i>Export
    </button>
    <span class="tooltiptext">Download chat transcript as text file for your records</span>
</div>
```

### 6. care-plan-wizard.html

```html
<!-- Previous Step Button -->
<div class="tooltip">
    <button id="prevBtn" class="px-4 py-2 bg-gray-200...">
        <i class="fas fa-arrow-left mr-2"></i>Previous
    </button>
    <span class="tooltiptext">Return to previous step. Your progress is automatically saved.</span>
</div>

<!-- Next Step Button -->
<div class="tooltip">
    <button id="nextBtn" class="px-6 py-2 bg-blue-600...">
        Next<i class="fas fa-arrow-right ml-2"></i>
    </button>
    <span class="tooltiptext">Continue to next step. Required fields must be completed.</span>
</div>

<!-- Save Draft Button -->
<div class="tooltip">
    <button onclick="saveDraft()" class="px-4 py-2 bg-blue-50...">
        <i class="fas fa-save mr-2"></i>Save Draft
    </button>
    <span class="tooltiptext">Save care plan to browser storage to resume later on this computer</span>
</div>
```

### 7. clinical-workspace.html

```html
<!-- Quick Action Buttons -->
<div class="tooltip">
    <button onclick="newPatient()" class="px-4 py-2 bg-green-600...">
        <i class="fas fa-user-plus mr-2"></i>New Patient
    </button>
    <span class="tooltiptext">Start new patient documentation workflow</span>
</div>

<div class="tooltip">
    <button onclick="openTemplates()" class="px-4 py-2 bg-purple-600...">
        <i class="fas fa-file-medical mr-2"></i>Templates
    </button>
    <span class="tooltiptext">Access clinical documentation templates and forms</span>
</div>
```

## Common Tooltip Patterns

### Action Buttons
```html
<!-- Pattern: Action + Benefit -->
<span class="tooltiptext">Calculate safe dosage based on patient parameters</span>
<span class="tooltiptext">Search authoritative medical databases for evidence</span>
<span class="tooltiptext">Export report as text file to your computer</span>
```

### Navigation Buttons
```html
<!-- Pattern: Where + What Happens -->
<span class="tooltiptext">Return to previous step. Progress is saved automatically.</span>
<span class="tooltiptext">Continue to next step. Complete required fields first.</span>
<span class="tooltiptext">Return to main dashboard and feature selection</span>
```

### AI Features
```html
<!-- Pattern: What AI Does + Expected Result -->
<span class="tooltiptext">AI converts informal notes to professional SBAR format</span>
<span class="tooltiptext">AI analyzes medications for dangerous interactions</span>
<span class="tooltiptext">AI suggests priority level based on vital signs</span>
```

### Safety/Warning Features
```html
<!-- Pattern: Warning + Action Required -->
<span class="tooltiptext">⚠️ Major drug interaction detected. Review recommendations before proceeding.</span>
<span class="tooltiptext">🚨 Critical alert requires immediate attention</span>
```

## Tooltip Variants

### Small Tooltips (for icons)
```html
<div class="tooltip tooltip-sm">
    <i class="fas fa-info-circle"></i>
    <span class="tooltiptext">Additional information</span>
</div>
```

### Large Tooltips (for complex explanations)
```html
<div class="tooltip tooltip-lg">
    <button>Complex Feature</button>
    <span class="tooltiptext">This feature analyzes multiple factors including vital signs, lab values, and clinical history to provide comprehensive assessment recommendations.</span>
</div>
```

### Bottom Tooltips (for top-of-page elements)
```html
<div class="tooltip tooltip-bottom">
    <button>Header Button</button>
    <span class="tooltiptext">Tooltip appears below button instead of above</span>
</div>
```

## Implementation Checklist

For each HTML page, add tooltips to:

- [ ] **Navigation buttons** (Previous, Next, Home, Back)
- [ ] **Primary action buttons** (Search, Submit, Calculate, Generate)
- [ ] **Secondary actions** (Clear, Reset, Cancel, Delete)
- [ ] **Save/Export buttons** (Save Draft, Download, Export, Print)
- [ ] **AI feature buttons** (Enhance, Check, Suggest, Analyze)
- [ ] **Icon-only buttons** (especially if icon meaning not obvious)
- [ ] **Dropdowns/selects** (if purpose not immediately clear)
- [ ] **Help/info icons**
- [ ] **Toggle switches** (if not self-explanatory)
- [ ] **Quick action shortcuts**

## Testing Tooltips

After implementation, verify:

1. ✅ Tooltips appear on hover (not click)
2. ✅ Tooltip text is readable (not cut off)
3. ✅ Tooltip doesn't block other important content
4. ✅ Tooltip positioning is appropriate (top/bottom)
5. ✅ Tooltip text is concise and helpful
6. ✅ Tooltip adds value (not redundant with button text)
7. ✅ Tooltip works on both desktop and tablet

## Priority Implementation Order

1. **High Priority** - Complete these first:
   - index.html (main dashboard)
   - sbar-wizard.html (already done ✅)
   - drug-interactions.html
   - disease-lookup.html

2. **Medium Priority**:
   - dosage-calculator.html
   - chat.html
   - care-plan-wizard.html

3. **Lower Priority**:
   - clinical-workspace.html
   - clinical-assessment-optimizer.html
   - api-test.html

## Example: Complete Button with Tooltip

```html
<!-- Before: No tooltip -->
<button onclick="submitForm()" class="px-6 py-3 bg-blue-600 text-white rounded-lg">
    <i class="fas fa-check mr-2"></i>
    Submit Assessment
</button>

<!-- After: With tooltip -->
<div class="tooltip">
    <button onclick="submitForm()" class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
        <i class="fas fa-check mr-2"></i>
        Submit Assessment
    </button>
    <span class="tooltiptext">Submit completed assessment for review and documentation in patient record</span>
</div>
```

## Mobile Considerations

On mobile devices, tooltips may not work well (no hover state). Consider:

1. Making button text descriptive enough to stand alone
2. Using aria-label attributes for screen readers
3. Potentially showing tooltips on tap/click for mobile
4. Ensuring critical information isn't ONLY in tooltips

## Accessibility

Always include:

```html
<div class="tooltip">
    <button aria-label="Descriptive action text">
        Button Text
    </button>
    <span class="tooltiptext" role="tooltip">Tooltip text</span>
</div>
```

## Next Steps

1. Add tooltip CSS to all HTML pages
2. Systematically add tooltips following priority order
3. Test tooltip positioning and text clarity
4. Get user feedback on tooltip helpfulness
5. Refine tooltip text based on common user questions

---

**Questions or Suggestions?**
Update this guide as you discover better tooltip patterns or user preferences.
