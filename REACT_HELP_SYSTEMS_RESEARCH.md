# React Help Systems Research - AI Nurse Florence

**Date**: September 30, 2025
**Purpose**: Research and recommendations for React-based help systems, tooltips, and onboarding tours
**Status**: Research Complete - Ready for Implementation

## Executive Summary

This document provides comprehensive research on React help system components including tooltips, product tours, and guided onboarding experiences. Based on 2025 best practices and current library landscape, we provide recommendations for AI Nurse Florence's future React implementation.

---

## 1. React Tooltip Libraries (2025)

### Overview
Tooltips are small pop-ups that display additional information when users hover over, focus on, or click an element. They enhance UX by providing context without cluttering the interface - critical for medical applications where clarity is paramount.

### Top React Tooltip Libraries

#### 1.1 react-tooltip ⭐ RECOMMENDED
**Version**: 5.29.1 (Latest - 3 months ago)
**GitHub Stars**: Highly popular
**License**: MIT
**Best For**: General-purpose tooltips with minimal setup

**Key Features:**
- Lightweight and simple to use
- Data attribute-driven (can add tooltips via HTML attributes)
- Supports multiple positioning options
- Accessible out of the box
- Works with both class and functional components

**Installation:**
```bash
npm install react-tooltip
```

**Basic Usage:**
```jsx
import { Tooltip } from 'react-tooltip';

function MedicationButton() {
  return (
    <>
      <button
        data-tooltip-id="med-tooltip"
        data-tooltip-content="Check for drug interactions">
        Check Interactions
      </button>
      <Tooltip id="med-tooltip" />
    </>
  );
}
```

**Advanced Features:**
```jsx
<Tooltip
  id="advanced-tooltip"
  place="top"
  effect="solid"
  delayShow={500}
  className="custom-tooltip"
  clickable={true}
/>
```

**Why Choose For Medical App:**
- ✅ Easy to implement quickly
- ✅ Low bundle size impact
- ✅ Active maintenance
- ✅ Good accessibility support
- ✅ Works well with existing vanilla JS (can migrate gradually)

---

#### 1.2 Material UI Tooltip
**Best For**: Applications already using Material UI design system

**Key Features:**
- Robust customization
- Excellent accessibility (WCAG compliant)
- Consistent with Material Design principles
- Built-in animations and transitions

**Installation:**
```bash
npm install @mui/material @emotion/react @emotion/styled
```

**Usage:**
```jsx
import Tooltip from '@mui/material/Tooltip';

function SbarButton() {
  return (
    <Tooltip
      title="Generate SBAR report with AI assistance"
      placement="top"
      arrow>
      <button>Create SBAR</button>
    </Tooltip>
  );
}
```

**Customization:**
```jsx
import { styled } from '@mui/material/styles';
import Tooltip, { tooltipClasses } from '@mui/material/Tooltip';

const MedicalTooltip = styled(({ className, ...props }) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(({ theme }) => ({
  [`& .${tooltipClasses.tooltip}`]: {
    backgroundColor: '#1e3a8a',
    color: 'white',
    fontSize: 13,
    maxWidth: 300,
  },
}));
```

**Why Choose For Medical App:**
- ✅ Professional, clinical appearance
- ✅ Excellent accessibility
- ✅ Highly customizable
- ❌ Requires Material UI (large bundle if not already using)

---

#### 1.3 @tippyjs/react (Tippy.js)
**Best For**: Complex tooltip requirements with animations

**Key Features:**
- Highly customizable and performant
- Supports interactive tooltips (clickable content)
- Rich animation options
- Can contain HTML content, not just text

**Installation:**
```bash
npm install @tippyjs/react
```

**Usage:**
```jsx
import Tippy from '@tippyjs/react';
import 'tippy.js/dist/tippy.css';

function DrugInteractionButton() {
  return (
    <Tippy content={
      <div>
        <strong>Drug Interaction Checker</strong>
        <p>AI-powered analysis of medication combinations</p>
        <ul>
          <li>Detects major interactions</li>
          <li>Provides clinical recommendations</li>
          <li>Evidence-based warnings</li>
        </ul>
      </div>
    }
    interactive={true}
    placement="right">
      <button>Check Interactions</button>
    </Tippy>
  );
}
```

**Why Choose For Medical App:**
- ✅ Can display complex medical information in tooltips
- ✅ Interactive tooltips (clickable links to resources)
- ✅ Rich formatting for clinical data
- ❌ Slightly larger bundle size
- ❌ More complex API

---

#### 1.4 Floating UI (formerly Popper.js)
**Best For**: Building custom tooltip systems from scratch

**Key Features:**
- Maximum control and flexibility
- Framework-agnostic core
- Powers many other tooltip libraries
- Smart positioning algorithms

**When To Use:**
- Need complete control over tooltip behavior
- Building a custom design system
- Other libraries don't meet specific requirements

**Why For Medical App:**
- ✅ Ultimate flexibility for unique clinical workflows
- ✅ Can build HIPAA-compliant tooltip systems
- ❌ More development time required
- ❌ Need to build accessibility features yourself

---

#### 1.5 Chakra UI Tooltip
**Best For**: Chakra UI users

**Installation:**
```bash
npm install @chakra-ui/react @emotion/react @emotion/styled framer-motion
```

**Usage:**
```jsx
import { Tooltip } from '@chakra-ui/react';

<Tooltip label="Calculate safe dosage" placement="top" hasArrow>
  <button>Dosage Calculator</button>
</Tooltip>
```

---

#### 1.6 Radix UI Tooltip
**Best For**: Unstyled, accessible components with full control

**Key Features:**
- Completely unstyled (you provide all CSS)
- Maximum accessibility (WCAG AAA compliant)
- Lightweight
- Full keyboard support

**Installation:**
```bash
npm install @radix-ui/react-tooltip
```

**Usage:**
```jsx
import * as Tooltip from '@radix-ui/react-tooltip';

<Tooltip.Provider>
  <Tooltip.Root>
    <Tooltip.Trigger asChild>
      <button>SBAR Wizard</button>
    </Tooltip.Trigger>
    <Tooltip.Portal>
      <Tooltip.Content className="medical-tooltip">
        Create structured SBAR reports
        <Tooltip.Arrow />
      </Tooltip.Content>
    </Tooltip.Portal>
  </Tooltip.Root>
</Tooltip.Provider>
```

**Why Choose For Medical App:**
- ✅ Maximum accessibility for healthcare compliance
- ✅ Complete style control
- ✅ Very lightweight
- ❌ Must style everything yourself

---

## 2. Product Tour & Onboarding Libraries

### Why Product Tours Matter for Medical Apps
- Guide new nurses through complex clinical workflows
- Reduce training time and errors
- Highlight critical safety features
- Ensure compliance with clinical protocols

### Top Product Tour Libraries (2025)

#### 2.1 React Joyride ⭐ RECOMMENDED FOR MEDICAL
**GitHub Stars**: 5.1k+
**License**: MIT
**Best For**: Comprehensive, step-by-step guided tours

**Key Features:**
- React-first design with component-driven logic
- Fine-grained control over tour behavior
- Spotlight/masking to focus user attention
- Callback system for tracking user progress
- Highly customizable styling
- Keyboard navigation support
- Mobile-responsive

**Installation:**
```bash
npm install react-joyride
```

**Basic Medical Workflow Example:**
```jsx
import Joyride from 'react-joyride';
import { useState } from 'react';

function SbarTutorial() {
  const [run, setRun] = useState(false);

  const steps = [
    {
      target: '#patient-info',
      content: 'Start by entering patient identification and location',
      disableBeacon: true,
    },
    {
      target: '#situation-field',
      content: 'Describe the current clinical situation. Use the AI Enhance button to convert informal notes to professional language.',
    },
    {
      target: '#medication-field',
      content: '⚠️ IMPORTANT: Click "Check Interactions" to screen for dangerous drug combinations before proceeding.',
      placement: 'bottom',
    },
    {
      target: '#priority-suggest',
      content: 'AI can suggest priority level (STAT/URGENT/ROUTINE) based on vital signs and assessment.',
    },
    {
      target: '#complete-button',
      content: 'When finished, click Complete to generate your SBAR report for handoff.',
    },
  ];

  return (
    <>
      <button onClick={() => setRun(true)}>
        Start Tutorial
      </button>

      <Joyride
        steps={steps}
        run={run}
        continuous={true}
        showSkipButton={true}
        showProgress={true}
        styles={{
          options: {
            primaryColor: '#3b82f6',
            zIndex: 10000,
          },
          tooltip: {
            fontSize: 14,
          },
        }}
        callback={(data) => {
          const { status } = data;
          if (status === 'finished' || status === 'skipped') {
            setRun(false);
          }
        }}
      />
    </>
  );
}
```

**Advanced Features:**
```jsx
const steps = [
  {
    target: '#critical-alert',
    content: (
      <div>
        <h3>🚨 Critical Safety Feature</h3>
        <p>This button checks for major drug interactions that could harm patients.</p>
        <strong>Always use before administering new medications.</strong>
      </div>
    ),
    disableOverlayClose: true, // Force user to click Next
    spotlightClicks: true, // Allow clicking on highlighted element
    locale: {
      next: 'I understand',
      back: 'Go back',
    },
  },
];
```

**Tracking Tour Completion:**
```jsx
function handleJoyrideCallback(data) {
  const { status, type, index, action } = data;

  if (status === 'finished') {
    // Record that user completed tour
    localStorage.setItem('sbar_tutorial_completed', 'true');
    analytics.track('Tutorial Completed', { workflow: 'SBAR' });
  }

  if (type === 'step:after') {
    // Track which step user is on
    analytics.track('Tutorial Step Viewed', {
      step: index + 1,
      action: action
    });
  }
}
```

**Why Choose For Medical App:**
- ✅ React-first, component-driven approach
- ✅ Excellent for complex multi-step workflows
- ✅ Masking helps focus on safety-critical features
- ✅ Can track user progress and completion
- ✅ Highly customizable for clinical branding
- ✅ Active maintenance and community support

---

#### 2.2 Driver.js
**Best For**: Lightweight, framework-agnostic solution

**Key Features:**
- Very small bundle size (~5KB gzipped)
- Framework-agnostic (works with vanilla JS too)
- Beautiful default styling
- Easy to trigger on-demand
- No dependencies

**Installation:**
```bash
npm install driver.js
```

**Usage in React:**
```jsx
import { driver } from "driver.js";
import "driver.js/dist/driver.css";
import { useEffect } from 'react';

function QuickTour() {
  useEffect(() => {
    const driverObj = driver({
      showProgress: true,
      steps: [
        {
          element: '#drug-search',
          popover: {
            title: 'Drug Interaction Checker',
            description: 'Search for medications to check for dangerous interactions'
          }
        },
        {
          element: '#check-button',
          popover: {
            title: 'Run Analysis',
            description: 'AI analyzes your medication list for safety concerns',
            side: "left",
            align: 'start'
          }
        },
      ]
    });

    // Auto-start tour for first-time users
    if (!localStorage.getItem('tour_seen')) {
      driverObj.drive();
      localStorage.setItem('tour_seen', 'true');
    }
  }, []);

  return <button onClick={() => driverObj.drive()}>Show Tour</button>;
}
```

**Highlighting Single Element:**
```jsx
const highlightCriticalFeature = () => {
  const driverObj = driver();

  driverObj.highlight({
    element: '#critical-warning',
    popover: {
      title: '⚠️ Safety Alert',
      description: 'Major drug interaction detected - review before proceeding',
      side: 'top',
    }
  });
};
```

**Why Choose For Medical App:**
- ✅ Very lightweight (fast loading)
- ✅ Can use immediately without React refactor
- ✅ Beautiful out-of-the-box design
- ✅ Great for highlighting critical safety features
- ❌ Less React-specific features than Joyride
- ❌ Less fine-grained control over tour flow

---

#### 2.3 Reactour
**GitHub Stars**: 3.9k+
**Best For**: Masking functionality to dim background

**Key Features:**
- Strong visual masking (dims everything except current step)
- Good for focusing user attention
- Customizable styling
- Keyboard navigation

**Installation:**
```bash
npm install @reactour/tour
```

**Usage:**
```jsx
import { TourProvider, useTour } from '@reactour/tour';

const steps = [
  {
    selector: '.vital-signs',
    content: 'Enter patient vital signs here. AI will analyze for critical values.',
  },
  {
    selector: '.assessment-field',
    content: 'Document your physical assessment findings.',
  },
];

function App() {
  return (
    <TourProvider steps={steps}>
      <YourMedicalApp />
    </TourProvider>
  );
}

function TourButton() {
  const { setIsOpen } = useTour();
  return <button onClick={() => setIsOpen(true)}>Start Guide</button>;
}
```

**Why Choose For Medical App:**
- ✅ Strong masking prevents accidental clicks during training
- ✅ Good for safety-critical workflows
- ❌ Less maintained than React Joyride
- ❌ Smaller community

---

#### 2.4 React Shepherd
**Wrapper for Shepherd.js** (~10K stars on main library)

**Key Features:**
- Based on mature Shepherd.js library
- Tether positioning (smart placement)
- Theme support
- Exit conditions

**Installation:**
```bash
npm install react-shepherd
```

---

#### 2.5 Intro.js React
**Best For**: Simple tours and in-app hints/tooltips

**Key Features:**
- Dual-purpose: Tours and contextual hints
- Simple API
- Good documentation

**Installation:**
```bash
npm install intro.js intro.js-react
```

---

#### 2.6 Walktour
**Best For**: Guided walkthroughs with minimal configuration

**Key Features:**
- Simple setup
- Good defaults
- Keyboard navigation

**Installation:**
```bash
npm install walktour
```

---

## 3. React Joyride vs Driver.js: Detailed Comparison

### When to Choose React Joyride

**Use React Joyride If:**
- ✅ Building full React application
- ✅ Need component-driven logic and state management
- ✅ Require fine-grained control over tour behavior
- ✅ Want to track user progress through analytics
- ✅ Need complex conditional tour flows
- ✅ Building multi-step onboarding for complex clinical workflows

**Example Scenario:**
"Creating a comprehensive onboarding tour for SBAR wizard that adapts based on user role (RN, LPN, MD), tracks completion, and requires users to interact with certain safety features before proceeding."

---

### When to Choose Driver.js

**Use Driver.js If:**
- ✅ Want lightweight, minimal bundle impact
- ✅ Need framework-agnostic solution (works with vanilla JS pages)
- ✅ Want beautiful default styling without customization
- ✅ Need to trigger tours on-demand quickly
- ✅ Highlighting specific elements without full tour
- ✅ Want fast implementation without React refactor

**Example Scenario:**
"Adding quick feature highlights to existing vanilla JS pages, or spotlighting a new critical safety feature immediately when user opens drug interaction checker."

---

### Side-by-Side Comparison

| Feature | React Joyride | Driver.js |
|---------|---------------|-----------|
| **Bundle Size** | ~20KB | ~5KB |
| **React Integration** | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐ Works but not native |
| **Customization** | ⭐⭐⭐⭐⭐ Extensive | ⭐⭐⭐⭐ Good defaults |
| **Ease of Setup** | ⭐⭐⭐⭐ Moderate | ⭐⭐⭐⭐⭐ Very easy |
| **State Management** | ⭐⭐⭐⭐⭐ Full control | ⭐⭐⭐ Basic |
| **Analytics Tracking** | ⭐⭐⭐⭐⭐ Detailed callbacks | ⭐⭐⭐ Basic events |
| **Mobile Support** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good |
| **Accessibility** | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐ Good |
| **Visual Polish** | ⭐⭐⭐⭐ Very good | ⭐⭐⭐⭐⭐ Excellent |
| **Learning Curve** | Moderate | Easy |
| **Active Maintenance** | ⭐⭐⭐⭐⭐ Very active | ⭐⭐⭐⭐⭐ Very active |
| **Community Size** | Large | Growing |

---

## 4. Best Practices for Medical App Onboarding (2025)

### 4.1 Keep Tours Simple and Concise
- ❌ Don't overwhelm users with too many steps
- ✅ Focus on 5-7 key features per tour
- ✅ Allow users to skip or exit anytime
- ✅ Save progress if tour is interrupted

### 4.2 Highlight Most Important Features First
**Priority Order for Medical Apps:**
1. **Safety Features** (drug interaction checker, allergy alerts)
2. **Critical Workflows** (SBAR communication, patient handoff)
3. **Time-Saving Tools** (AI text enhancement, templates)
4. **Documentation** (how to save, export, print)
5. **Advanced Features** (analytics, custom settings)

### 4.3 Use Clear, Professional Language
```jsx
// ❌ Bad
content: "Click here to make it better"

// ✅ Good
content: "Click 'Enhance with AI' to convert informal notes into professional SBAR format using medical terminology"
```

### 4.4 Provide Context for Medical Decisions
```jsx
{
  target: '#priority-level',
  content: (
    <div>
      <h4>Setting Communication Priority</h4>
      <ul>
        <li><strong>STAT:</strong> Life-threatening, immediate response needed</li>
        <li><strong>URGENT:</strong> Requires attention within 1 hour</li>
        <li><strong>ROUTINE:</strong> Can wait for regular rounds</li>
      </ul>
      <p className="text-sm text-gray-600">AI can suggest priority based on vital signs and assessment.</p>
    </div>
  ),
}
```

### 4.5 Guide Users Toward Next Steps
```jsx
callback: (data) => {
  const { status } = data;

  if (status === 'finished') {
    // Show next action
    showNotification({
      title: "Tutorial Complete! 🎉",
      message: "Ready to create your first SBAR report? Click the SBAR Wizard to begin.",
      action: {
        label: "Start SBAR Wizard",
        onClick: () => navigate('/sbar-wizard')
      }
    });
  }
}
```

### 4.6 Make Tours Discoverable
```jsx
// Always-visible help button
<button
  onClick={() => startTour()}
  className="fixed bottom-4 right-4 bg-blue-600 text-white p-3 rounded-full shadow-lg">
  <i className="fas fa-question-circle"></i>
  <span className="sr-only">Help & Tutorial</span>
</button>

// First-time user auto-start
useEffect(() => {
  const hasSeenTour = localStorage.getItem('sbar_tour_seen');
  if (!hasSeenTour) {
    setTimeout(() => setRunTour(true), 1000); // Delay so page loads first
  }
}, []);
```

### 4.7 Track and Improve
```jsx
const trackTourStep = (stepIndex, stepData, action) => {
  analytics.track('Onboarding Step', {
    tour: 'SBAR Wizard',
    step: stepIndex + 1,
    stepTitle: stepData.content.substring(0, 50),
    action: action, // 'next', 'back', 'skip', 'close'
    timestamp: new Date().toISOString(),
  });
};

// Analyze which steps users skip or struggle with
// Improve tour based on data
```

---

## 5. Recommendations for AI Nurse Florence

### 5.1 Short-Term (Current Vanilla JS Pages)

**Recommended: Driver.js**

**Why:**
- Can implement immediately without React refactor
- Very lightweight (fast loading)
- Beautiful default styling matches clinical aesthetic
- Easy to add to existing pages

**Implementation Plan:**
```javascript
// Add to existing HTML pages
<script src="https://cdn.jsdelivr.net/npm/driver.js@1.0.1/dist/driver.js.iife.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/driver.js@1.0.1/dist/driver.css">

<script>
const driver = window.driver.js.driver;

const driverObj = driver({
  showProgress: true,
  showButtons: ['next', 'previous', 'close'],
  steps: [
    { element: '#med-search', popover: { title: 'Search Medications', description: '...' }},
    { element: '#check-btn', popover: { title: 'Check Interactions', description: '...' }},
  ]
});

// Trigger on help button click
document.getElementById('help-btn').addEventListener('click', () => {
  driverObj.drive();
});
</script>
```

**Pages to Add Driver.js Tours:**
1. ✅ drug-interactions.html - Medication search and interaction checking
2. ✅ disease-lookup.html - Disease search and viewing details
3. ✅ dosage-calculator.html - Dosage calculation workflow
4. ✅ sbar-wizard.html - SBAR creation process (already has tooltips, add tour)

---

### 5.2 Long-Term (React Migration)

**Recommended: React Joyride**

**Why:**
- Best-in-class for complex React applications
- Full control over tour behavior and styling
- Excellent for multi-step clinical workflows
- Strong community and active maintenance
- Can track user progress and completion

**Migration Strategy:**
1. **Phase 1:** Convert high-traffic pages to React (index, drug-interactions, sbar-wizard)
2. **Phase 2:** Implement React Joyride tours for converted pages
3. **Phase 3:** Add role-based tours (RN, LPN, MD have different workflows)
4. **Phase 4:** Implement analytics tracking to improve tours

**Example React Component Structure:**
```jsx
// src/components/tours/SbarTour.jsx
import Joyride from 'react-joyride';
import { useState, useEffect } from 'react';

export function SbarTour() {
  const [run, setRun] = useState(false);

  const steps = [
    {
      target: '#patient-info',
      content: 'Start by entering patient identification',
      disableBeacon: true,
    },
    // ... more steps
  ];

  useEffect(() => {
    const hasSeenTour = localStorage.getItem('sbar_tour_completed');
    if (!hasSeenTour) {
      setRun(true);
    }
  }, []);

  const handleJoyrideCallback = (data) => {
    const { status } = data;
    if (status === 'finished' || status === 'skipped') {
      localStorage.setItem('sbar_tour_completed', 'true');
      setRun(false);
    }
  };

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showSkipButton
      showProgress
      callback={handleJoyrideCallback}
      styles={{
        options: {
          primaryColor: '#3b82f6',
          zIndex: 10000,
        },
      }}
    />
  );
}
```

---

### 5.3 Hybrid Approach (Recommended)

**Best of Both Worlds:**

1. **Use Driver.js Now** for existing vanilla JS pages
   - Quick wins with minimal refactoring
   - Improve user onboarding immediately
   - Low implementation cost

2. **Plan React Joyride** for future React conversion
   - More powerful for complex workflows
   - Better state management
   - Richer analytics

3. **Consistent Experience**
   - Use same color schemes in both
   - Similar step structure and language
   - Unified "Help" button placement

---

## 6. Implementation Checklist

### For Each Page Needing Help System:

- [ ] **Identify Key User Journeys**
  - What are the most common tasks?
  - Where do users get confused?
  - What are safety-critical features?

- [ ] **Design Tour Steps**
  - Maximum 7 steps per tour
  - Start with most important feature
  - End with clear next action

- [ ] **Choose Appropriate Library**
  - Vanilla JS → Driver.js
  - React → React Joyride
  - Simple tooltips → react-tooltip

- [ ] **Implement Tracking**
  - Tour starts
  - Step progression
  - Completions and skips
  - Time spent on each step

- [ ] **Test Thoroughly**
  - Desktop and mobile
  - Different browsers
  - Different user roles
  - Accessibility (keyboard navigation, screen readers)

- [ ] **Gather Feedback**
  - Are tours helpful?
  - Are steps clear?
  - Is anything missing?

---

## 7. Code Examples for Common Scenarios

### 7.1 Auto-Start Tour for First-Time Users

```jsx
import { useState, useEffect } from 'react';
import Joyride from 'react-joyride';

function FirstTimeUserTour() {
  const [run, setRun] = useState(false);

  useEffect(() => {
    const tourCompleted = localStorage.getItem('app_tour_completed');
    const userSessionCount = parseInt(localStorage.getItem('session_count') || '0');

    // Show tour on first session only
    if (!tourCompleted && userSessionCount === 0) {
      setTimeout(() => setRun(true), 1500); // Delay for page load
    }

    localStorage.setItem('session_count', (userSessionCount + 1).toString());
  }, []);

  const handleCallback = (data) => {
    if (data.status === 'finished' || data.status === 'skipped') {
      localStorage.setItem('app_tour_completed', 'true');
      setRun(false);
    }
  };

  return (
    <Joyride
      run={run}
      steps={steps}
      continuous
      callback={handleCallback}
    />
  );
}
```

---

### 7.2 Context-Sensitive Tours (Show Different Tours Based on User Role)

```jsx
function RoleBasedTour({ userRole }) {
  const steps = userRole === 'RN' ? rnSteps :
                userRole === 'LPN' ? lpnSteps :
                mdSteps;

  return <Joyride steps={steps} />;
}

// Registered Nurse tour emphasizes documentation
const rnSteps = [
  {
    target: '#sbar-wizard',
    content: 'Use SBAR for patient handoffs and shift reports',
  },
  {
    target: '#care-plan',
    content: 'Document nursing interventions in care plans',
  },
];

// Licensed Practical Nurse tour emphasizes tasks
const lpnSteps = [
  {
    target: '#vital-signs',
    content: 'Record and monitor patient vital signs',
  },
  {
    target: '#medication-admin',
    content: 'Document medication administration',
  },
];

// Medical Doctor tour emphasizes decision support
const mdSteps = [
  {
    target: '#clinical-trials',
    content: 'Search for relevant clinical trials for patients',
  },
  {
    target: '#literature',
    content: 'Access latest medical research from PubMed',
  },
];
```

---

### 7.3 Conditional Steps Based on User Actions

```jsx
import Joyride, { ACTIONS, EVENTS, STATUS } from 'react-joyride';

function SmartTour() {
  const [stepIndex, setStepIndex] = useState(0);
  const [steps, setSteps] = useState(initialSteps);

  const handleCallback = (data) => {
    const { action, index, status, type } = data;

    if (type === EVENTS.STEP_AFTER) {
      // User clicked on the drug interaction checker
      if (index === 2 && userClickedInteractionButton) {
        // Add bonus step explaining results
        const newSteps = [...steps];
        newSteps.splice(3, 0, {
          target: '#interaction-results',
          content: 'Great! These results show potential drug interactions. Always review before administration.',
        });
        setSteps(newSteps);
      }

      setStepIndex(index + (action === ACTIONS.PREV ? -1 : 1));
    }
  };

  return (
    <Joyride
      stepIndex={stepIndex}
      steps={steps}
      callback={handleCallback}
    />
  );
}
```

---

### 7.4 Highlighting Critical Safety Feature

```jsx
import { driver } from "driver.js";

function highlightDrugSafetyFeature() {
  const driverObj = driver({
    showProgress: false,
    showButtons: ['next'],
    steps: [
      {
        element: '#drug-interaction-checker',
        popover: {
          title: '🚨 Safety Alert',
          description: 'Always check for drug interactions before administering new medications. This AI-powered feature can prevent serious adverse events.',
          side: 'left',
          align: 'start',
        },
        popoverClass: 'safety-critical-popover',
      },
    ],
  });

  driverObj.drive();
}

// Trigger when user is about to administer medication
document.getElementById('administer-btn').addEventListener('click', (e) => {
  const interactionCheckRun = sessionStorage.getItem('interaction_checked');

  if (!interactionCheckRun) {
    e.preventDefault();
    highlightDrugSafetyFeature();
  }
});
```

---

### 7.5 Progress Tracking and Analytics

```jsx
function TrackedTour() {
  const handleCallback = (data) => {
    const { type, index, status, action } = data;

    // Track when tour starts
    if (type === EVENTS.TOUR_START) {
      analytics.track('Tour Started', {
        tour_name: 'SBAR Wizard Tutorial',
        user_id: userId,
        timestamp: new Date().toISOString(),
      });
    }

    // Track each step view
    if (type === EVENTS.STEP_AFTER) {
      analytics.track('Tour Step Completed', {
        tour_name: 'SBAR Wizard Tutorial',
        step_number: index + 1,
        step_title: steps[index].title,
        action: action, // 'next', 'back', 'skip'
        time_on_step: calculateTimeOnStep(index),
      });
    }

    // Track completion
    if (status === STATUS.FINISHED) {
      analytics.track('Tour Completed', {
        tour_name: 'SBAR Wizard Tutorial',
        total_time: calculateTotalTime(),
        completion_rate: '100%',
      });
    }

    // Track skip/abandonment
    if (status === STATUS.SKIPPED) {
      analytics.track('Tour Skipped', {
        tour_name: 'SBAR Wizard Tutorial',
        last_step_viewed: index + 1,
        completion_rate: `${((index + 1) / steps.length * 100).toFixed(0)}%`,
      });
    }
  };

  return <Joyride steps={steps} callback={handleCallback} />;
}
```

---

## 8. Accessibility Considerations for Medical Apps

### WCAG Compliance Requirements:

1. **Keyboard Navigation**
   - ✅ All tours must be navigable via keyboard
   - ✅ Escape key should close/skip tour
   - ✅ Tab/Shift+Tab to navigate buttons

2. **Screen Reader Support**
   - ✅ Use proper ARIA labels
   - ✅ Announce tour step changes
   - ✅ Describe interactive elements

3. **Color Contrast**
   - ✅ Ensure 4.5:1 contrast ratio minimum
   - ✅ Don't rely on color alone for meaning
   - ✅ Use icons + text for warnings

4. **Focus Management**
   - ✅ Focus should move to tour popover
   - ✅ Return focus to trigger element when closed
   - ✅ Prevent focus from leaving tour during active step

**Example Accessible Tour:**
```jsx
<Joyride
  steps={steps}
  styles={{
    options: {
      ariaLabelledBy: 'tour-title',
    },
  }}
  locale={{
    skip: <span aria-label="Skip tour">Skip</span>,
    next: <span aria-label="Next step">Next</span>,
    back: <span aria-label="Previous step">Back</span>,
    close: <span aria-label="Close tour">Close</span>,
    last: <span aria-label="Finish tour">Finish</span>,
  }}
  disableOverlayClose={false}  // Allow Escape key
  spotlightClicks={true}  // Allow interaction with highlighted elements
/>
```

---

## 9. Mobile Responsiveness

### Best Practices:

1. **Adjust Tooltip Placement**
   ```jsx
   const steps = [
     {
       target: '#feature',
       placement: window.innerWidth < 768 ? 'bottom' : 'right',
       content: 'Feature description...',
     },
   ];
   ```

2. **Larger Touch Targets**
   ```jsx
   styles={{
     buttonNext: {
       padding: '12px 24px',  // Larger for touch
       fontSize: '16px',
     },
   }}
   ```

3. **Simplified Steps on Mobile**
   ```jsx
   const steps = isMobile ? mobileSteps : desktopSteps;

   const mobileSteps = [
     // Fewer, more focused steps for small screens
   ];
   ```

4. **Test on Real Devices**
   - iPhone SE (small screen)
   - iPad (tablet)
   - Android phones (various sizes)

---

## 10. Summary & Action Items

### Immediate Actions (Next 30 Days):

1. **Add Driver.js to Existing Pages**
   - [drug-interactions.html](static/drug-interactions.html) - Priority 1
   - [disease-lookup.html](static/disease-lookup.html) - Priority 2
   - [dosage-calculator.html](static/dosage-calculator.html) - Priority 3

2. **Implement Basic Tours**
   - 5-7 steps per page
   - Focus on safety features first
   - Add "Help" button to each page

3. **Gather Baseline Metrics**
   - How many users complete tours?
   - Which steps are skipped most?
   - Where do users drop off?

### Medium-Term (3-6 Months):

1. **Begin React Migration**
   - Start with most-used pages
   - Implement React Joyride
   - Maintain feature parity with vanilla JS

2. **Implement Advanced Features**
   - Role-based tours
   - Conditional steps
   - Progress tracking
   - A/B testing different tour flows

3. **Accessibility Audit**
   - WCAG 2.1 AA compliance
   - Screen reader testing
   - Keyboard navigation verification

### Long-Term (6-12 Months):

1. **Full React Application**
   - All pages converted to React
   - Unified state management
   - Comprehensive tour system

2. **Advanced Analytics**
   - Tour completion rates by user role
   - Correlation between tours and feature adoption
   - Personalized tour recommendations

3. **Continuous Improvement**
   - Regular user feedback
   - Tour content updates
   - Performance optimization

---

## 11. Resources & Links

### Documentation:
- [React Joyride Docs](https://react-joyride.com/)
- [Driver.js Documentation](https://driverjs.com/)
- [react-tooltip Docs](https://react-tooltip.com/)
- [Material UI Tooltip](https://mui.com/material-ui/react-tooltip/)

### Community:
- React Joyride GitHub Issues
- Driver.js GitHub Discussions
- Stack Overflow tags: `react-joyride`, `driverjs`

### Related Guides:
- [TOOLTIP_IMPLEMENTATION_GUIDE.md](TOOLTIP_IMPLEMENTATION_GUIDE.md)
- [SBAR_WIZARD_AI_ENHANCEMENTS.md](SBAR_WIZARD_AI_ENHANCEMENTS.md)

---

**Last Updated**: September 30, 2025
**Next Review**: December 2025
**Maintained By**: Development Team
