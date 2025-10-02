# Help System Integration Guide

Quick guide to adding the Help System to AI Nurse Florence pages.

## Step 1: Import the Help System

For React/TypeScript pages:

```tsx
import { HelpSystem } from '../components/Help';

function YourPage() {
  return (
    <div>
      {/* Your page content */}

      {/* Add help system - it floats in bottom-right */}
      <HelpSystem />
    </div>
  );
}
```

For HTML pages (like wizards):

```html
<!-- Add at end of body, before closing </body> tag -->
<div id="help-system-root"></div>

<script type="module">
  import { HelpSystem } from '/static/components/Help/HelpSystem.js';
  import { createRoot } from 'react-dom/client';

  const root = createRoot(document.getElementById('help-system-root'));
  root.render(<HelpSystem />);
</script>
```

## Step 2: Add Contextual Tooltips

```tsx
import { InfoTooltip } from '../components/Help';

<label>
  Diagnosis <InfoTooltip content="Type at least 3 characters of the disease name" />
</label>
```

## Step 3: Update Footer Links

Change "Documentation" to "Help":

```html
<!-- Before -->
<a href="/docs">Documentation</a>

<!-- After -->
<a href="#" onclick="openHelpSystem()">Help</a>

<script>
function openHelpSystem() {
  // Help system opens automatically when button clicked
  // Or programmatically: window.dispatchEvent(new Event('openHelp'));
}
</script>
```

## Examples

### Patient Education Wizard

```html
<!DOCTYPE html>
<html>
<body>
  <!-- Wizard content -->

  <!-- Footer -->
  <footer>
    <a href="/" class="hover:underline">
      <i class="fas fa-home mr-1"></i> Home
    </a> |
    <a href="#" onclick="event.preventDefault()" class="hover:underline ml-4">
      <i class="fas fa-question-circle mr-1"></i> Help
    </a>
  </footer>

  <!-- Help System -->
  <div id="help-root"></div>
  <script type="module">
    import { HelpSystem } from '/static/components/Help/index.js';
    // Mount help system
  </script>
</body>
</html>
```

### Dashboard (React)

```tsx
import { HelpSystem } from './components/Help';

export default function Dashboard() {
  return (
    <div>
      {/* Dashboard content */}

      {/* Help system (floats in corner) */}
      <HelpSystem />
    </div>
  );
}
```

## Best Practices

1. **Add HelpSystem once per page** - It's a singleton floating button
2. **Use InfoTooltip sparingly** - Only for fields that need clarification
3. **Keep tooltip text brief** - One sentence maximum
4. **Test on mobile** - Help drawer is responsive
5. **Update help content** - When features change, update help-content.json

## Troubleshooting

**Help button not showing?**
- Check that HelpSystem is rendered
- Check z-index conflicts (help is z-50)
- Check console for errors

**Search not working?**
- Verify help-content.json is loading
- Check browser console for import errors

**Tooltips not appearing?**
- Check that Font Awesome is loaded
- Verify Tailwind CSS is available
- Check hover events aren't blocked

## Need Help?

The Help System is self-documenting! Click the help button to see the Quick Start guide and full task documentation.
