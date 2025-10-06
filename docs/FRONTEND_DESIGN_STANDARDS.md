# AI Nurse Florence: Frontend Design Standards

This document outlines the UI/UX design standards and best practices for the AI Nurse Florence frontend application.

## Color Palette

### Brand Colors

**Primary (Blue)**
- Main: `#2563eb` / `primary-600`
- Use for: Primary CTAs, links, active states, main navigation
- Tailwind: `bg-primary-600`, `text-primary-600`, `border-primary-600`

**Secondary (Maroon)**
- Main: `#991b1b` / `secondary-500`
- Classic: `#800020` / `secondary-600` (hover states)
- Use for: Secondary CTAs, section headers, card accents, hover states, interactive elements
- Tailwind: `bg-secondary-500`, `text-secondary-600`, `border-secondary-500`

**Accent (Gold)**
- Classic: `#d4af37` / `accent-500`
- Light: `#fbbf24` / `accent-400`
- Use for: Badges, "Featured" labels, achievement indicators, small highlights
- **Use sparingly** - accent color only, not for large areas
- Tailwind: `bg-accent-500`, `text-accent-600`, `border-accent-400`

### Status/Medical Colors

**Emergency/Error (Red)**
- Color: `#dc2626` / `medical-emergency`
- **RESERVED FOR**: Error messages, critical alerts, warning icons/text ONLY
- Do NOT use for: Buttons, backgrounds, decorative elements
- Tailwind: `text-medical-emergency`, `border-medical-emergency`

**Urgent (Orange)**
- Color: `#f59e0b` / `medical-urgent`
- Use for: Urgent notifications, time-sensitive alerts
- Tailwind: `bg-medical-urgent`, `text-medical-urgent`

**Routine/Success (Green)**
- Color: `#10b981` / `medical-routine`
- Use for: Success messages, completed states, routine status
- Tailwind: `bg-medical-routine`, `text-medical-routine`

**Info (Cyan)**
- Color: `#3b82f6` / `medical-info`
- Use for: Informational messages, tooltips
- Tailwind: `bg-medical-info`, `text-medical-info`

### Color Usage Guidelines

**Visual Hierarchy:**
1. **Primary CTA**: Blue (`primary-600`)
2. **Secondary CTA**: Maroon (`secondary-500`)
3. **Accent/Badge**: Gold (`accent-500`) - small touches only
4. **Emergency**: Red (`medical-emergency`) - warnings/errors only
5. **Success**: Green (`medical-routine`)

**DO:**
- ✅ Use maroon for most interactive elements (links, buttons, hover states)
- ✅ Use gold sparingly for special designations (badges, "Verified", achievements)
- ✅ Reserve red exclusively for errors, warnings, and critical alerts
- ✅ Use blue for primary navigation and main CTAs
- ✅ Combine blue + maroon for gradients in headers/hero sections

**DON'T:**
- ❌ Use red for decorative purposes or non-critical elements
- ❌ Use gold for large backgrounds (overwhelming)
- ❌ Mix emergency red with maroon in same component (visual confusion)
- ❌ Use gold for primary or secondary CTAs

**Example Combinations:**
```tsx
// Primary button (blue)
<button className="bg-primary-600 hover:bg-primary-700 text-white">
  Submit Assessment
</button>

// Secondary button (maroon)
<button className="bg-secondary-500 hover:bg-secondary-600 text-white">
  View Details
</button>

// Badge with gold accent
<span className="bg-accent-50 text-accent-700 border border-accent-400">
  ⭐ Featured
</span>

// Error message (red - reserved use)
<div className="border-l-4 border-medical-emergency bg-red-50 text-red-800">
  ⚠️ Critical: Patient allergy detected
</div>

// Maroon section header
<h2 className="text-secondary-600 border-b-2 border-secondary-500">
  Patient Summary
</h2>
```

### CSS Variables (for non-Tailwind usage)

```css
/* Brand */
--primary-color: #2563eb;           /* Blue */
--secondary-color: #991b1b;         /* Maroon */
--secondary-dark: #800020;          /* Dark maroon */
--accent-color: #d4af37;            /* Gold */
--accent-light: #fbbf24;            /* Light gold */

/* Status */
--error-color: #dc2626;             /* Red - warnings only */
--success-color: #16a34a;           /* Green */
--warning-color: #ca8a04;           /* Orange */
--info-color: #0891b2;              /* Cyan */
```

---

## Layout Standards

### Responsive Grid Layouts for Dense Content

When displaying dense, information-rich content (such as clinical trial results, drug interactions, or patient education materials), use a **2-column grid layout** on wide screens that gracefully collapses to single column on mobile.

**Design Rationale:**
- Dense medical information is easier to scan and compare when displayed side-by-side
- Reduces vertical scrolling on desktop displays
- Improves information density without sacrificing readability
- Provides better use of screen real estate on modern wide monitors

**Implementation Pattern:**

```tsx
// Clinical Trials Results Example
<div className="grid lg:grid-cols-2 gap-4 lg:items-start">
  {items.map((item, index) => (
    <div key={index} className="card h-full">
      {/* Card content */}
    </div>
  ))}
</div>
```

**Key Tailwind CSS Classes:**
- `grid lg:grid-cols-2` - Creates 2-column grid on large screens (lg breakpoint: 1024px+)
- `gap-4` - Consistent spacing between grid items (1rem/16px)
- `lg:items-start` - Aligns items to top of grid cells for clean alignment
- `h-full` - Makes cards fill available height for visual consistency

**Responsive Breakpoints:**
- **Mobile/Tablet (< 1024px)**: Single column, stacked layout
- **Desktop (≥ 1024px)**: 2-column side-by-side layout

**When to Use:**
- ✅ Clinical trial search results
- ✅ Drug interaction results (when showing multiple medications)
- ✅ Literature search results
- ✅ Patient education material lists
- ✅ Any dense, card-based content with 3+ items

**When NOT to Use:**
- ❌ Single item display
- ❌ Simple forms or input sections
- ❌ Navigation menus
- ❌ Dashboard widgets (use dashboard-specific grid)

### Card Design Standards

**Standard Card Structure:**

```tsx
<div className="card hover:shadow-lg transition-shadow h-full">
  {/* Card content with consistent padding and spacing */}
</div>
```

**Card Specifications:**
- Base class: `card` (defined in global CSS)
- Hover effect: `hover:shadow-lg` for interactive cards
- Smooth transitions: `transition-shadow` for polished feel
- Full height: `h-full` when used in grids

## Component Standards

### Autocomplete Components

**Design Pattern:**
- Minimum 2 characters to trigger search
- Instant/0ms debounce for medical terms (feels responsive)
- Dropdown max height: `max-h-80` (20rem/320px)
- Item padding: `px-5 py-3` for comfortable touch targets
- Font size: `text-base` for readability
- Icon spacing: `mr-3` for visual hierarchy

**Example:**
```tsx
<div className="grid lg:grid-cols-2 gap-4 lg:items-start">
  {suggestions.map((item, index) => (
    <div className="px-5 py-3 cursor-pointer">
      <i className="fas fa-heartbeat text-base mr-3"></i>
      <span className="text-base">{item}</span>
    </div>
  ))}
</div>
```

### External Links

**Standard Pattern:**
```tsx
<a
  href={url}
  target="_blank"
  rel="noopener noreferrer"
  className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center"
>
  <i className="fas fa-external-link-alt mr-2"></i>
  View Full Details on [External Site]
</a>
```

**Requirements:**
- Always use `target="_blank"` for external links
- Include `rel="noopener noreferrer"` for security
- Add external link icon (`fa-external-link-alt`)
- Use descriptive link text (avoid generic "More..." or "Click here")

## Accessibility Standards

### Color-Coded Status Badges

Use semantic colors for status indicators:

```tsx
const statusColor =
  status.includes('recruiting') ? 'bg-green-100 text-green-800' :
  status.includes('active') ? 'bg-blue-100 text-blue-800' :
  status.includes('completed') ? 'bg-gray-100 text-gray-800' :
  'bg-yellow-100 text-yellow-800';
```

**Status Color Palette:**
- 🟢 **Green** (`bg-green-100 text-green-800`) - Active/Recruiting/Available
- 🔵 **Blue** (`bg-blue-100 text-blue-800`) - Active but not recruiting
- ⚫ **Gray** (`bg-gray-100 text-gray-800`) - Completed/Closed
- 🟡 **Yellow** (`bg-yellow-100 text-yellow-800`) - Pending/Suspended

## Translation Standards

All user-facing text must use i18n translation keys:

```tsx
// ✅ Correct
<h2>{t('clinicalTrials.results.title')}</h2>

// ❌ Wrong
<h2>Clinical Trials Results</h2>
```

**Translation Key Naming Convention:**
- `[feature].[section].[element]`
- Example: `clinicalTrials.searchSection.statusOptions.all`

## CSS Utility Classes

### Spacing Standards
- **Gap between grid items**: `gap-4` (16px)
- **Margin bottom for sections**: `mb-4` or `mb-6`
- **Card padding**: Built into `card` class
- **Content padding**: `p-3` for nested content boxes

### Typography
- **Headings**: `text-2xl font-bold` (results titles)
- **Subheadings**: `text-xl font-bold` (card titles)
- **Body**: `text-base` (default)
- **Small text**: `text-sm` (hints, helper text)

## Performance Considerations

### Image and Icon Loading
- Use Font Awesome icons for consistency
- Lazy load images when applicable
- Optimize icon sizing (`text-base`, `text-sm`)

### Grid Performance
- Limit initial render to reasonable number (10-20 items)
- Implement pagination for large result sets
- Use `key={index}` for stable list rendering

## Version History

- **v2.4.2** (2025-10-04): Added 2-column grid layout standard for dense content
- Initial standards documented

## Related Documentation

- [Developer Guide](./developer_guide.md) - Backend architecture and API integration
- [CONTRIBUTING.md](../CONTRIBUTING.md) - General contribution guidelines
- [Tooltip Implementation Guide](../TOOLTIP_IMPLEMENTATION_GUIDE.md) - Tooltip patterns
- [i18n Quick Start](../QUICK_START_I18N.md) - Translation setup

---

*These standards ensure consistent, accessible, and maintainable frontend code across the AI Nurse Florence application.*
