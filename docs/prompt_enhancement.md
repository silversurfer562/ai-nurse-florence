# Prompt Enhancement

The application includes a prompt enhancement system to improve user queries and provide better responses.

## Overview

The prompt enhancement system analyzes user prompts and:

1. **Enhances unclear prompts** - Adds context or specificity to vague prompts
2. **Asks clarifying questions** - Returns a 422 status with a clarification question when a prompt is too vague
3. **Leaves good prompts unchanged** - Preserves well-formed prompts

## How It Works

The system uses rule-based matching to:
- Detect vague or incomplete prompts
- Enhance prompts based on the service being used
- Generate appropriate clarification questions

## API Response Format

When clarification is needed, endpoints return a 422 Unprocessable Entity status with:

```json
{
  "detail": {
    "needs_clarification": true,
    "clarification_question": "What specific medical topic would you like information about?",
    "original_prompt": "help"
  }
}
```

When a prompt is enhanced, the normal response includes enhancement info:

```json
{
  "text": "The summary content...",
  "prompt_enhanced": true,
  "original_prompt": "diabetes",
  "enhanced_prompt": "Provide a clinical summary of diabetes including key symptoms, diagnostic criteria, and treatment approaches"
}
```

## Handling in Frontend Applications

Frontend applications should:

1. Check for 422 status codes
2. Display the clarification question to the user
3. Allow the user to refine their query
4. Optionally show when a prompt was enhanced

## Services Using Prompt Enhancement

- `/summarize/chat` - Enhances text summarization prompts
- `/v1/disease` - Enhances disease lookup queries

## Example Usage

```javascript
async function fetchData(endpoint, prompt) {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });

  if (response.status === 422) {
    const data = await response.json();
    if (data.detail?.needs_clarification) {
      // Show clarification UI
      return { needsClarification: true, question: data.detail.clarification_question };
    }
  }

  const data = await response.json();
  return data;
}
```