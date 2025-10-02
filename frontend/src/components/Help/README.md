# Help System Documentation

## Overview

The Help System provides comprehensive, task-oriented guidance for nurses and healthcare providers using AI Nurse Florence. It's designed to be intuitive, searchable, and contextual.

## Architecture

### Components

1. **HelpSystem** (`HelpSystem.tsx`)
   - Main help interface with slide-out drawer
   - Three tabs: Quick Start, Tasks, FAQ
   - Search functionality across all content
   - Responsive design for mobile and desktop

2. **HelpTooltip** (`HelpTooltip.tsx`)
   - Contextual inline help tooltips
   - Appears on hover
   - Positioned automatically (top/bottom/left/right)

3. **InfoTooltip** (`HelpTooltip.tsx`)
   - Small info icon with tooltip
   - Use next to form labels

### Data Structure

**Help Content** (`src/data/help-content.json`)
```json
{
  "tasks": [...],        // Step-by-step task guides
  "faqs": [...],         // Frequently asked questions
  "tooltips": {...},     // Contextual tooltip text
  "quickStart": {...}    // Getting started guide
}
```

## Usage

### Adding the Help System to Your Application

```tsx
import { HelpSystem } from './components/Help';

function App() {
  return (
    <div>
      {/* Your app content */}
      <HelpSystem />
    </div>
  );
}
```

The floating help button appears in the bottom-right corner automatically.

### Adding Tooltips to Forms

```tsx
import { InfoTooltip } from './components/Help';

<label>
  Patient Language <InfoTooltip content="Choose the language your patient understands best" />
</label>
```

### Adding New Help Content

#### 1. Add a New Task

Edit `src/data/help-content.json`:

```json
{
  "tasks": [
    {
      "id": "unique-task-id",
      "title": "Task Name",
      "category": "Category Name",
      "description": "Brief description",
      "steps": [
        {
          "step": 1,
          "title": "Step title",
          "instruction": "What to do",
          "tip": "Helpful tip (optional)"
        }
      ],
      "benefits": [
        "Benefit 1",
        "Benefit 2"
      ],
      "troubleshooting": [
        {
          "problem": "Common problem",
          "solution": "How to fix it"
        }
      ]
    }
  ]
}
```

#### 2. Add a New FAQ

```json
{
  "faqs": [
    {
      "id": "unique-faq-id",
      "question": "The question?",
      "answer": "The answer.",
      "category": "Category Name"
    }
  ]
}
```

#### 3. Add a Tooltip

```json
{
  "tooltips": {
    "field-name": "Helpful explanation"
  }
}
```

## Content Writing Guidelines

### Task Guides

- **Be task-oriented**: Title should start with a verb (Generate, Check, Create)
- **Be specific**: "Generate Patient Education Document" not "Use the Education Tool"
- **Number steps**: Keep to 3-7 steps
- **Add tips**: Include practical insights nurses will find helpful
- **Show benefits**: Explain the value (time saved, better outcomes, etc.)
- **Anticipate problems**: Add common issues and solutions

### FAQs

- **Use natural language**: Write questions as users would ask them
- **Be concise**: Answer in 2-3 sentences
- **Link when needed**: Reference other help content for details
- **Stay current**: Update as features change

### Tooltips

- **Be brief**: One sentence maximum
- **Be helpful**: Explain WHY, not just WHAT
- **Use plain language**: Avoid jargon
- **Be encouraging**: Positive tone

## Design Principles

1. **Task-Oriented**: Organized by what nurses want to accomplish
2. **Searchable**: Full-text search across all content
3. **Progressive Disclosure**: Summary → Details → Full guide
4. **Contextual**: Help where users need it
5. **Professional**: Clean, uncluttered interface
6. **Accessible**: Keyboard navigation, ARIA labels
7. **Mobile-Friendly**: Responsive design

## Future Enhancements

Placeholders are in the code for:

1. **Video Tutorials**
   - Embedded how-to videos
   - Screen recordings for complex workflows

2. **Interactive Walkthroughs**
   - Step-by-step overlays
   - Highlight UI elements as you guide users

3. **Context-Aware Help**
   - Detect current page/task
   - Show relevant help automatically

4. **Analytics**
   - Track most-viewed help topics
   - Identify areas needing better documentation

5. **Multi-Language Support**
   - Translate help content to match patient education languages

## Technical Notes

- Built with React + TypeScript
- Uses Tailwind CSS for styling
- Font Awesome for icons
- No external dependencies beyond React
- Fully self-contained help content in JSON

## Content Maintenance

### Review Schedule

- **Monthly**: Check for outdated information
- **After feature releases**: Update relevant help content
- **Quarterly**: Review analytics (when implemented)
- **Annually**: Comprehensive content audit

### Who Updates What

- **Developers**: Technical troubleshooting, system requirements
- **Clinical Team**: Workflow guidance, best practices, benefits
- **Support Team**: FAQs based on user questions
- **Product Manager**: Overall content strategy, priorities

## Accessibility

The help system follows WCAG 2.1 AA standards:

- Keyboard navigation (Tab, Enter, Escape)
- ARIA labels for screen readers
- Sufficient color contrast
- Focus indicators
- Semantic HTML

## Performance

- Help content loads asynchronously
- Search is client-side (instant)
- Drawer animates smoothly
- Minimal bundle size impact

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Full support (responsive)

## Questions?

Contact the development team or submit an issue in the project repository.
