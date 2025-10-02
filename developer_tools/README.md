# Developer Tools

Saved development/testing utilities that are useful but not appropriate for production UI.

## Date: 2025-10-02

## Purpose

These tools provide convenient testing interfaces during development but are removed from production to maintain a professional, focused user experience.

## Tools

### autocomplete-settings-panel.html

A collapsible panel for real-time autocomplete testing with adjustable settings:

- **Debounce Delay** (0-1000ms): Test search responsiveness vs API load
- **Minimum Query Length** (1-10 chars): Test when autocomplete triggers
- **Max Results** (5-50 items): Test dropdown scrolling behavior

**How to Use:**
1. Copy the HTML section into any page that uses `AutocompleteDropdown.js`
2. Copy the JavaScript section into a `<script>` tag
3. The panel appears at the top of the page
4. All changes apply immediately to existing autocomplete instances
5. Remove before deploying to production

**Benefits:**
- No need to edit code to test different settings
- Real-time testing without page reloads
- Saves time during UX optimization
- Visual sliders make it easy to compare settings

**Current Optimal Settings:**
- Debounce: 0ms (instant response)
- Min Query: 3 characters
- Max Results: 15 items

## When to Use

Use these tools during:
- Feature development
- UX optimization
- Performance testing
- User feedback sessions
- A/B testing different settings

Always remove before:
- Production deployments
- User acceptance testing
- Client demos
- Screenshot/documentation creation
