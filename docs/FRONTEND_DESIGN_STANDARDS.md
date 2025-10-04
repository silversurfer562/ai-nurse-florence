# AI Nurse Florence: Frontend Design Standards

This document outlines the UI/UX design standards and best practices for the AI Nurse Florence frontend application.

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
