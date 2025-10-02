# Care Setting Framework - UX Mockups

**Visual Guide to User Experience**

---

## Header Badge (Always Visible)

```
┌─────────────────────────────────────────────────────────────┐
│  🏥 AI Nurse Florence - Clinical Decision Support          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Logo] AI Nurse Florence                  [🫀 ICU ▼]     │
│         Clinical Decision Support           [🏠 Home]      │
│                                             [🌐 English]    │
│                                             [? Help]        │
│                                             [● Connected]   │
└─────────────────────────────────────────────────────────────┘
```

**Care Setting Badge States:**

**No Setting Selected:**
```
┌───────────────────────┐
│ 🏥 Set Care Setting   │
└───────────────────────┘
```

**ICU Selected:**
```
┌──────────────┐
│ 🫀 ICU   ▼  │  ← Red background
└──────────────┘
```

**Med-Surg Selected:**
```
┌────────────────────┐
│ 🏥 Med-Surg   ▼   │  ← Blue background
└────────────────────┘
```

**Home Health Selected:**
```
┌──────────────────────┐
│ 🏠 Home Health  ▼   │  ← Purple background
└──────────────────────┘
```

---

## First-Run Onboarding Modal

```
╔═══════════════════════════════════════════════════════════════╗
║  Welcome to AI Nurse Florence                                 ║
║  Let's personalize your experience based on where you work    ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ 💡 Why does care setting matter?                        │ ║
║  │                                                          │ ║
║  │ Documentation needs vary dramatically by care           │ ║
║  │ environment. An ICU nurse needs different templates,    │ ║
║  │ safety checks, and workflows than a home health nurse.  │ ║
║  │                                                          │ ║
║  │ ✓ Setting-aware templates                              │ ║
║  │ ✓ Context-specific safety                              │ ║
║  │ ✓ Workflow optimization                                │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  Select your primary care setting:                           ║
║                                                               ║
║  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐  ║
║  │      🫀        │ │      🏥        │ │      🚑        │  ║
║  │      ICU       │ │   Med-Surg     │ │   Emergency    │  ║
║  │                │ │                │ │                │  ║
║  │ Critical care  │ │ General care   │ │ Acute care     │  ║
║  │ Continuous     │ │ Post-operative │ │ Rapid triage   │  ║
║  │ monitoring     │ │ Medication mgmt│ │ Stabilization  │  ║
║  └────────────────┘ └────────────────┘ └────────────────┘  ║
║                                                               ║
║  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐  ║
║  │      👨‍⚕️        │ │      🏠        │ │      🛏️        │  ║
║  │  Outpatient    │ │  Home Health   │ │ Skilled Nursing│  ║
║  │                │ │                │ │                │  ║
║  │ Preventive care│ │ In-home care   │ │ Rehabilitation │  ║
║  │ Chronic disease│ │ Caregiver      │ │ Long-term care │  ║
║  │ management     │ │ support        │ │ Elder care     │  ║
║  └────────────────┘ └────────────────┘ └────────────────┘  ║
║                                                               ║
║  ℹ️ You can change this anytime from the settings menu       ║
║                                                               ║
║                            [Continue with ICU]               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Care Setting Quick Switcher (Compact Mode)

**Clicking header badge opens dropdown:**

```
┌──────────────┐
│ 🫀 ICU   ▼  │ ← Current setting
└──────────────┘
       ↓ (click)

┌─────────────────────────────────────────────┐
│ 🫀 ICU                                  ✓  │ ← Selected (red highlight)
│ Critical care, complex monitoring          │
├─────────────────────────────────────────────┤
│ 🏥 Med-Surg                                │
│ General medical and post-surgical care      │
├─────────────────────────────────────────────┤
│ 🚑 Emergency                               │
│ Acute care, rapid assessment               │
├─────────────────────────────────────────────┤
│ 👨‍⚕️ Outpatient                             │
│ Ambulatory care, preventive health         │
├─────────────────────────────────────────────┤
│ 🏠 Home Health                             │
│ In-home care, caregiver support            │
├─────────────────────────────────────────────┤
│ 🛏️ Skilled Nursing                         │
│ Long-term care, rehabilitation             │
└─────────────────────────────────────────────┘
```

---

## Document Wizard with Care Setting Context

### SBAR Wizard - ICU Setting

```
┌─────────────────────────────────────────────────────────────┐
│  Create SBAR Report                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ℹ️ Creating SBAR for ICU care setting               │  │
│  │ Templates optimized for critical care documentation  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Focus Areas (ICU Default):                                │
│  ☑ Hemodynamic stability                                   │
│  ☑ Ventilator settings                                     │
│  ☑ Continuous monitoring                                   │
│  ☑ Device management                                       │
│  ☑ Lab values                                              │
│                                                             │
│  Complexity Level: ● High                                  │
│  Documentation Timeframe: Hourly                           │
│  Include Vitals: ✓                                         │
│  Include Labs: ✓                                           │
│                                                             │
│  [Generate SBAR Report]                                    │
└─────────────────────────────────────────────────────────────┘
```

### SBAR Wizard - Home Health Setting

```
┌─────────────────────────────────────────────────────────────┐
│  Create SBAR Report                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ℹ️ Creating SBAR for Home Health care setting       │  │
│  │ Templates optimized for in-home care documentation   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Focus Areas (Home Health Default):                        │
│  ☑ Home safety assessment                                  │
│  ☑ Caregiver competency                                    │
│  ☑ Resource coordination                                   │
│  ☑ Independence support                                    │
│  ☑ Fall risk in home environment                           │
│                                                             │
│  Complexity Level: ● Moderate                              │
│  Documentation Timeframe: Weekly visits                    │
│  Include Vitals: ✓                                         │
│  Include Labs: ✗                                           │
│  Include Caregiver Education: ✓                            │
│                                                             │
│  [Generate SBAR Report]                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Dashboard with Care Setting Context

```
┌─────────────────────────────────────────────────────────────┐
│  🫀 ICU                                           [Change]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Welcome to AI Nurse Florence                              │
│  Clinical Decision Support for ICU Nurses                  │
│                                                             │
│  Quick Actions:                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│  │ 📋 SBAR      │ │ 💊 Drug      │ │ 📚 Literature │      │
│  │    Report    │ │    Check     │ │    Search     │      │
│  │              │ │              │ │               │      │
│  │ Critical care│ │ IV drug      │ │ Evidence-     │      │
│  │ handoff      │ │ interactions │ │ based ICU     │      │
│  └──────────────┘ └──────────────┘ └──────────────┘      │
│                                                             │
│  ICU-Specific Resources:                                   │
│  • Hemodynamic Monitoring Guidelines                       │
│  • Ventilator Management Protocols                         │
│  • Critical Care Medication Reference                      │
│  • Sepsis Early Recognition Tools                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Patient Education with Setting Context

### ICU Patient Education

```
┌─────────────────────────────────────────────────────────────┐
│  Create Patient Education Material                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ℹ️ ICU care setting detected                              │
│  Optimizing for critical care patient education            │
│                                                             │
│  Topic: Mechanical Ventilation                             │
│                                                             │
│  Reading Level: 8th grade (ICU Default)                    │
│  ┌─────────────┬─────────────┬─────────────┐              │
│  │ 5th grade   │ 6th grade   │ 8th grade ● │              │
│  └─────────────┴─────────────┴─────────────┘              │
│                                                             │
│  Focus Areas (ICU):                                        │
│  ☑ Equipment explanation (ventilator, monitors)           │
│  ☑ What to expect during ICU stay                         │
│  ☑ Family visitation policies                             │
│  ☑ Communication with intubated patients                  │
│  ☑ ICU-acquired weakness prevention                       │
│                                                             │
│  Format:                                                   │
│  ○ Quick Reference (1 page)                               │
│  ● Detailed Guide (2-3 pages)                             │
│  ○ Family Education Packet                                │
│                                                             │
│  [Generate Education Material]                             │
└─────────────────────────────────────────────────────────────┘
```

### Home Health Patient Education

```
┌─────────────────────────────────────────────────────────────┐
│  Create Patient Education Material                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ℹ️ Home Health care setting detected                      │
│  Optimizing for in-home patient & caregiver education      │
│                                                             │
│  Topic: Medication Management at Home                      │
│                                                             │
│  Reading Level: 5th grade (Home Health Default)           │
│  ┌─────────────┬─────────────┬─────────────┐              │
│  │ 5th grade ● │ 6th grade   │ 8th grade   │              │
│  └─────────────┴─────────────┴─────────────┘              │
│                                                             │
│  Focus Areas (Home Health):                                │
│  ☑ Home medication organization                            │
│  ☑ Caregiver administration instructions                   │
│  ☑ When to call the nurse/doctor                          │
│  ☑ Medication safety at home                              │
│  ☑ Emergency contact information                           │
│                                                             │
│  Include:                                                  │
│  ☑ Patient Education                                       │
│  ☑ Caregiver Education (separate section)                 │
│  ☑ Visual aids / pictures                                  │
│  ☑ Large print option                                      │
│                                                             │
│  Format:                                                   │
│  ● Patient + Caregiver Guide (3-4 pages)                  │
│  ○ Quick Reference Card                                    │
│  ○ Visual Guide with Pictures                             │
│                                                             │
│  [Generate Education Material]                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Setting-Specific Safety Considerations

### ICU Safety Checks

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ ICU Safety Considerations                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Critical care-specific safety checks for this patient:    │
│                                                             │
│  🫀 Hemodynamic Monitoring:                                │
│    • Verify arterial line calibration                      │
│    • Check vasopressor titration limits                    │
│    • Monitor cardiac rhythm continuously                   │
│                                                             │
│  🫁 Respiratory Support:                                   │
│    • Confirm ventilator settings match orders              │
│    • Verify endotracheal tube placement                    │
│    • Check oxygen saturation alarms                        │
│                                                             │
│  💊 Medication Safety:                                     │
│    • Double-check high-alert medication doses              │
│    • Verify IV pump programming                            │
│    • Assess for drug-drug interactions                     │
│                                                             │
│  🧠 Neurological:                                          │
│    • Perform hourly neurological assessments               │
│    • Monitor for delirium (CAM-ICU)                        │
│    • Assess sedation level (RASS score)                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Home Health Safety Checks

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ Home Health Safety Considerations                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Home environment-specific safety checks:                  │
│                                                             │
│  🏠 Home Safety Assessment:                                │
│    • Check for fall hazards (rugs, cords, lighting)        │
│    • Assess stair safety and handrails                     │
│    • Verify emergency exit accessibility                   │
│                                                             │
│  👨‍👩‍👧 Caregiver Competency:                                │
│    • Verify caregiver can perform required tasks           │
│    • Assess caregiver stress/burnout                       │
│    • Confirm caregiver knows when to call for help         │
│                                                             │
│  💊 Medication Management:                                 │
│    • Check medication storage (temperature, light)         │
│    • Verify patient/caregiver understands regimen          │
│    • Assess for medication errors or confusion             │
│                                                             │
│  📱 Communication & Resources:                             │
│    • Ensure patient has working phone                      │
│    • Verify emergency contact information                  │
│    • Confirm access to community resources                 │
│                                                             │
│  🚨 Emergency Preparedness:                                │
│    • Discuss when to call 911                              │
│    • Review signs/symptoms requiring immediate care        │
│    • Ensure caregiver knows patient's medical history      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Mobile Experience

### Mobile Header (Responsive)

```
┌─────────────────────┐
│ 🏥 AI Nurse Florence│
│ ┌─────────────────┐ │
│ │ 🫀 ICU      ▼  │ │
│ └─────────────────┘ │
│ [☰ Menu]           │
└─────────────────────┘
```

### Mobile Care Setting Selector (Stacked)

```
┌─────────────────────────────┐
│ Select Care Setting         │
├─────────────────────────────┤
│ ┌─────────────────────────┐ │
│ │      🫀                 │ │
│ │      ICU                │ │
│ │ Critical care, complex  │ │
│ │ monitoring ✓            │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │      🏥                 │ │
│ │   Med-Surg              │ │
│ │ General medical care    │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │      🚑                 │ │
│ │   Emergency             │ │
│ │ Acute care, rapid       │ │
│ └─────────────────────────┘ │
│                             │
│ [Continue]                  │
└─────────────────────────────┘
```

---

## Analytics Dashboard (Admin View - Future)

```
┌─────────────────────────────────────────────────────────────┐
│  Care Setting Usage Analytics                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Total Users: 1,247          Active This Week: 892         │
│                                                             │
│  Care Setting Distribution:                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Med-Surg        ████████████████████ 35% (437)       │  │
│  │ ICU             ████████████████ 25% (312)           │  │
│  │ Emergency       ████████████ 20% (249)               │  │
│  │ Home Health     ████████ 12% (150)                   │  │
│  │ Outpatient      ████ 5% (62)                         │  │
│  │ Skilled Nursing ██ 3% (37)                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Most Common Documents by Setting:                         │
│  ┌──────────────┬─────────────┬──────────────────────┐    │
│  │ Setting      │ Top Document│ Avg. Creation Time   │    │
│  ├──────────────┼─────────────┼──────────────────────┤    │
│  │ ICU          │ SBAR Report │ 3.2 minutes          │    │
│  │ Med-Surg     │ Patient Ed  │ 2.8 minutes          │    │
│  │ Emergency    │ SBAR Report │ 2.1 minutes (fastest)│    │
│  │ Home Health  │ Care Plan   │ 4.5 minutes          │    │
│  └──────────────┴─────────────┴──────────────────────┘    │
│                                                             │
│  Setting Switch Frequency: 2.3 switches per week avg.     │
│  (Indicates float nurses or multi-setting users)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Color Legend

| Setting | Color | Hex Code | Usage |
|---------|-------|----------|-------|
| ICU | Red | `#DC2626` | Badges, highlights, borders |
| Med-Surg | Blue | `#2563EB` | Badges, highlights, borders |
| Emergency | Orange | `#EA580C` | Badges, highlights, borders |
| Outpatient | Green | `#16A34A` | Badges, highlights, borders |
| Home Health | Purple | `#9333EA` | Badges, highlights, borders |
| Skilled Nursing | Teal | `#0D9488` | Badges, highlights, borders |

---

## Accessibility Notes

All mockups include:
- ✅ ARIA labels for screen readers
- ✅ Keyboard navigation support
- ✅ High contrast mode compatibility
- ✅ Color + icon + text (not color alone)
- ✅ Focus indicators on all interactive elements

---

**These mockups represent the target UX for the Care Setting Framework.**
**All core components are implemented and ready for integration.**
