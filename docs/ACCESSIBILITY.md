# Accessibility Guide for AI Nurse Florence

## Overview

AI Nurse Florence is committed to being fully accessible to all users, including those with disabilities. This guide documents the accessibility features implemented and provides testing guidance.

## WCAG 2.1 Compliance

The application follows **WCAG 2.1 Level AA** standards for web accessibility.

## Key Accessibility Features

### 1. ARIA Landmarks and Labels

All major page sections use proper ARIA landmarks:
- **Banner** (`role="banner"`): Main header with navigation
- **Main** (`role="main"`): Primary content area
- **Navigation** (`role="navigation"`): Primary navigation menu
- **Content Info** (`role="contentinfo"`): Footer information
- **Search** (`role="search"`): Search forms on all pages

All interactive elements include descriptive ARIA labels using:
- `aria-label` for standalone elements
- `aria-labelledby` for elements labeled by other elements
- `aria-describedby` for additional descriptive text

### 2. Keyboard Navigation

Full keyboard support throughout the application:
- **Tab**: Navigate forward through interactive elements
- **Shift + Tab**: Navigate backward
- **Enter**: Activate buttons and links
- **Escape**: Close dropdowns and modals
- **Arrow Keys**: Navigate within dropdowns and autocomplete lists

#### Skip Links
Skip links allow keyboard users to bypass repetitive navigation:
- Skip to main content
- Skip to navigation

Skip links are visible when focused (press Tab on page load).

### 3. Voice Dictation

Medical terminology voice input is available on all search fields using the Web Speech API.

**Features:**
- Real-time speech recognition
- Medical abbreviation expansion (DM → Diabetes Mellitus, HTN → Hypertension, etc.)
- Fuzzy matching against known medical terms
- Visual feedback (pulsing microphone icon when listening)
- Browser compatibility detection

**Usage:**
1. Click the microphone icon next to any search field
2. Speak your search query (medical terms, disease names, drug names)
3. The system will automatically correct common medical abbreviations
4. Click the microphone again to stop recording

**Supported Browsers:**
- Chrome/Edge (full support)
- Safari (full support)
- Firefox (not supported - gracefully degrades)

**Available On:**
- Medical Glossary search
- Literature search
- Clinical Trials search
- Disease Info search (DiseaseAutocomplete component)
- Drug Interactions search (DrugAutocomplete component)

### 4. Screen Reader Support

#### Live Regions
Dynamic content is announced to screen readers using `aria-live` regions:
- Search result counts
- Loading states
- Connection status
- Error messages

**Politeness Levels:**
- `polite`: Non-urgent announcements (search results, general status)
- `assertive`: Urgent announcements (errors, critical warnings)

#### Screen Reader Only Content
Additional context is provided to screen reader users using the `.sr-only` CSS class:
- Descriptive labels for icon-only buttons
- Additional instructions for complex interactions
- Status indicators

### 5. Focus Indicators

All interactive elements have visible focus indicators:
- **Default**: 2px blue outline (`#3b82f6`)
- **Offset**: 2px from element
- **Border radius**: 0.25rem

Focus indicators are only shown for keyboard navigation (`:focus-visible`), not mouse clicks.

### 6. Color and Contrast

- All text meets **WCAG AA contrast requirements** (4.5:1 for normal text, 3:1 for large text)
- Information is never conveyed by color alone
- High contrast mode is supported via CSS media queries

### 7. Reduced Motion

For users with motion sensitivity, animations are reduced or removed:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Component-Specific Features

### VoiceDictation Component

**Location:** `frontend/src/components/VoiceDictation.tsx`

**Props:**
- `onTranscript`: Callback when speech is recognized
- `language`: Recognition language (default: 'en-US')
- `continuous`: Continuous recognition mode
- `medicalTerms`: Array of medical terms for fuzzy matching

**Medical Abbreviations Supported:**
- DM → Diabetes Mellitus
- MI → Myocardial Infarction
- CHF → Congestive Heart Failure
- COPD → Chronic Obstructive Pulmonary Disease
- HTN → Hypertension
- PVD → Peripheral Vascular Disease
- CAD → Coronary Artery Disease
- CVA → Cerebrovascular Accident
- TIA → Transient Ischemic Attack
- CKD → Chronic Kidney Disease
- ESRD → End Stage Renal Disease
- GERD → Gastroesophageal Reflux Disease
- IBS → Irritable Bowel Syndrome
- RA → Rheumatoid Arthritis
- OA → Osteoarthritis
- COPD → Chronic Obstructive Pulmonary Disease
- UTI → Urinary Tract Infection
- DVT → Deep Vein Thrombosis
- PE → Pulmonary Embolism
- AFib → Atrial Fibrillation

### ScreenReaderOnly Component

**Location:** `frontend/src/components/ScreenReaderOnly.tsx`

**Components:**
1. **ScreenReaderOnly**: Renders content only for screen readers
2. **LiveRegion**: Announces dynamic content
3. **SkipLink**: Keyboard navigation shortcuts

**Usage Example:**
```tsx
import { LiveRegion, ScreenReaderOnly, SkipLink } from './ScreenReaderOnly';

// Screen reader only text
<ScreenReaderOnly>Additional context for screen reader users</ScreenReaderOnly>

// Live announcements
<LiveRegion politeness="polite">{announceMessage}</LiveRegion>

// Skip links
<SkipLink href="#main-content">Skip to main content</SkipLink>
```

### Keyboard Navigation Hooks

**Location:** `frontend/src/hooks/useKeyboardNavigation.ts`

**Hooks Available:**

1. **useKeyboardNavigation**: Handle keyboard events
```tsx
const ref = useRef<HTMLDivElement>(null);
useKeyboardNavigation(ref, {
  onEnter: () => console.log('Enter pressed'),
  onEscape: () => console.log('Escape pressed'),
  onArrowUp: () => console.log('Arrow up pressed'),
  onArrowDown: () => console.log('Arrow down pressed')
});
```

2. **useFocusTrap**: Trap focus within a container (modals, dropdowns)
```tsx
const modalRef = useRef<HTMLDivElement>(null);
useFocusTrap(modalRef, isModalOpen);
```

3. **useScreenReaderAnnounce**: Programmatically announce to screen readers
```tsx
const announce = useScreenReaderAnnounce();
announce('Search completed with 5 results', 'polite');
```

## Testing Guide

### Automated Testing Tools

1. **axe DevTools** (Chrome/Firefox extension)
   - Install: https://www.deque.com/axe/devtools/
   - Run on each page to detect ARIA issues

2. **Lighthouse** (Chrome DevTools)
   - Open DevTools > Lighthouse tab
   - Run accessibility audit
   - Target score: 95+

3. **WAVE** (WebAIM browser extension)
   - Install: https://wave.webaim.org/extension/
   - Visual feedback on accessibility issues

### Manual Testing

#### Keyboard Navigation Test
1. Load any page
2. Press **Tab** repeatedly
3. Verify:
   - All interactive elements are reachable
   - Focus order is logical
   - Focus indicators are visible
   - Skip links appear at the top

#### Screen Reader Test

**NVDA (Windows - Free):**
1. Download: https://www.nvaccess.org/download/
2. Install and start NVDA
3. Navigate the application using:
   - **H**: Next heading
   - **Tab**: Next interactive element
   - **Arrow keys**: Read content
   - **Insert + F7**: List all landmarks

**JAWS (Windows - Commercial):**
1. Download trial: https://www.freedomscientific.com/products/software/jaws/
2. Similar navigation to NVDA

**VoiceOver (macOS - Built-in):**
1. Enable: System Preferences > Accessibility > VoiceOver
2. Toggle: **Cmd + F5**
3. Navigate using:
   - **Ctrl + Option + Arrow keys**: Navigate elements
   - **Ctrl + Option + H**: Next heading
   - **Ctrl + Option + U**: Open rotor (landmarks, headings, links)

**Testing Checklist:**
- [ ] Page title is announced
- [ ] All headings are properly nested (h1 → h2 → h3)
- [ ] Landmarks are announced (banner, main, navigation, search)
- [ ] Form fields have labels
- [ ] Buttons have descriptive names
- [ ] Links are descriptive (not "click here")
- [ ] Dynamic content changes are announced
- [ ] Error messages are announced

#### Voice Dictation Test
1. Open Medical Glossary page
2. Click microphone icon next to search field
3. Speak: "diabetes mellitus"
4. Verify:
   - Microphone icon pulses
   - Transcript appears in search field
   - Search results update

5. Test medical abbreviations:
   - Speak: "DM" → Should expand to "Diabetes Mellitus"
   - Speak: "HTN" → Should expand to "Hypertension"
   - Speak: "MI" → Should expand to "Myocardial Infarction"

#### High Contrast Mode Test
**Windows:**
1. Settings > Ease of Access > High Contrast
2. Enable any high contrast theme
3. Verify all UI elements are visible

**macOS:**
1. System Preferences > Accessibility > Display
2. Enable "Increase contrast"
3. Verify all UI elements are visible

#### Reduced Motion Test
**Windows:**
1. Settings > Ease of Access > Display
2. Enable "Show animations in Windows"

**macOS:**
1. System Preferences > Accessibility > Display
2. Enable "Reduce motion"

**Verify:**
- Transitions are instant or very short
- No spinning animations
- Page changes don't use smooth scrolling

### Color Contrast Test
Use **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/

Test all text/background combinations:
- Normal text: Minimum 4.5:1
- Large text (18pt+): Minimum 3:1
- UI components: Minimum 3:1

## Known Limitations

1. **Voice Recognition Browser Support:**
   - Not supported in Firefox
   - Requires HTTPS in production
   - May require microphone permissions

2. **Screen Reader Support:**
   - Best tested with NVDA, JAWS, VoiceOver
   - Some features may behave differently across screen readers

3. **Mobile Accessibility:**
   - Voice dictation requires mobile browser support
   - Touch targets should be minimum 44x44px (to be verified)

## Future Enhancements

1. **Mobile Optimization:**
   - Larger touch targets
   - Better mobile screen reader support
   - Improved mobile voice recognition

2. **Additional Voice Features:**
   - Voice navigation ("go to clinical trials")
   - Voice commands ("search for diabetes")
   - Multi-language voice support

3. **Enhanced Screen Reader Support:**
   - More descriptive table announcements
   - Better form validation feedback
   - Improved error recovery

4. **Customization:**
   - User-configurable font sizes
   - High contrast theme toggle
   - Dyslexia-friendly font option

## Resources

- **WCAG 2.1 Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
- **ARIA Authoring Practices**: https://www.w3.org/WAI/ARIA/apg/
- **WebAIM**: https://webaim.org/
- **A11y Project**: https://www.a11yproject.com/
- **Deque University**: https://dequeuniversity.com/

## Support

For accessibility issues or suggestions, please contact the development team or file an issue on GitHub.

---

**Last Updated:** October 2, 2025
**WCAG Version:** 2.1 Level AA
**Testing Status:** Manual testing completed, automated testing in progress
