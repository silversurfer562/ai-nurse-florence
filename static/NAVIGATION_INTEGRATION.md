# Florence Navigation System - Integration Guide

The unified navigation system provides:
- **Global Navigation Bar** with back-to-dashboard button
- **Breadcrumb Navigation** showing current location
- **Quick Access Menu** for fast tool switching (Alt+N)
- **Keyboard Shortcuts** for power users
- **Mobile-Responsive** design

## Quick Integration

Add these two lines to the `<head>` section of any HTML page:

```html
<link rel="stylesheet" href="/static/css/florence-navigation.css">
<script src="/static/js/florence-navigation.js"></script>
```

That's it! The navigation will automatically initialize when the page loads.

## Full Integration Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Tool - AI Nurse Florence</title>

    <!-- Existing styles -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

    <!-- ADD NAVIGATION SYSTEM -->
    <link rel="stylesheet" href="/static/css/florence-navigation.css">
    <script src="/static/js/florence-navigation.js"></script>
</head>
<body class="bg-gray-50">
    <!-- Navigation automatically injected here by florence-navigation.js -->

    <!-- Your page content -->
    <main class="max-w-7xl mx-auto px-4 py-6">
        <h1>Your Tool Content</h1>
        <!-- ... -->
    </main>
</body>
</html>
```

## Features

### 1. Global Navigation Bar
- Sticky top navigation
- Back to Dashboard button (except on index.html)
- Current page title with icon
- Quick Access button
- Help button
- Mobile hamburger menu

### 2. Breadcrumb Navigation
- Shows hierarchical location
- Clickable breadcrumb trail
- Automatically generated from page config
- Hidden on home page

### 3. Quick Access Menu
- Floating overlay with all tools
- Searchable list
- Grouped by category (Wizards, Tools)
- Keyboard shortcut: `Alt+N`
- Current page highlighted

### 4. Keyboard Shortcuts
- `Alt+N` - Open Quick Access Menu
- `Escape` - Close menus
- `Shift+?` - Open Help (coming soon)

### 5. Mobile Responsive
- Hamburger menu on mobile
- Touch-friendly buttons
- Responsive layout

## Adding a New Page

To add a new page to the navigation system, edit `florence-navigation.js`:

```javascript
// In the FlorenceNav.pages object, add:
'your-new-page.html': {
    title: 'Your Tool Name',
    icon: 'fa-your-icon',  // FontAwesome icon class
    category: 'wizards',   // 'wizards', 'tools', or 'main'
    breadcrumb: ['Dashboard', 'Category', 'Your Tool'],
    badge: 'NEW'           // Optional badge
}
```

## Customization

### Change Colors
Edit `florence-navigation.css` to customize:
- Navigation bar gradient: `.florence-nav-bar`
- Quick menu colors: `.florence-quick-menu`
- Hover states: `.florence-quick-item:hover`

### Add More Categories
Edit `renderQuickMenuItems()` in `florence-navigation.js`:

```javascript
const categories = {
    'wizards': { title: 'Clinical Wizards', icon: 'fa-magic', color: 'purple' },
    'tools': { title: 'Clinical Tools', icon: 'fa-tools', color: 'blue' },
    'reports': { title: 'Reports', icon: 'fa-chart-bar', color: 'green' }  // NEW
};
```

## Accessibility

The navigation system includes:
- ARIA labels for screen readers
- Keyboard navigation support
- Focus visible indicators
- Semantic HTML structure

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

**Navigation not appearing?**
- Check browser console for errors
- Ensure Tailwind CSS and Font Awesome are loaded
- Verify file paths are correct

**Quick menu not opening?**
- Check for JavaScript conflicts
- Ensure no other scripts override `Alt+N` shortcut
- Try clicking the "Tools" button instead

**Mobile menu not working?**
- Check viewport meta tag is present
- Ensure Tailwind CSS is loaded
- Try clearing cache

## Example Pages

See these pages for working examples:
- `/static/sbar-wizard-react.html` (with integration)
- `/static/index.html` (home page without breadcrumbs)

## What's Next?

Future enhancements planned:
- Help system integration
- User preferences (save menu state)
- Recent tools list
- Favorites/pinning
- Dark mode toggle
