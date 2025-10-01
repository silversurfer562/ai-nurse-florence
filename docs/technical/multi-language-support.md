# Multi-Language Support Documentation

## Overview

AI Nurse Florence now supports multiple languages for both the user interface and API responses. This enables healthcare professionals worldwide to use the application in their preferred language.

## Supported Languages

| Language | Code | UI Support | API Support | Translation Method |
|----------|------|------------|-------------|-------------------|
| English | `en` | ✅ Complete | ✅ Native | N/A (source language) |
| Spanish | `es` | ✅ Complete | ✅ Available | DeepL/Google Translate API |
| French | `fr` | 🚧 Partial | ✅ Available | DeepL/Google Translate API |
| German | `de` | 🚧 Partial | ✅ Available | DeepL/Google Translate API |
| Italian | `it` | 🚧 Partial | ✅ Available | DeepL/Google Translate API |
| Portuguese | `pt` | 🚧 Partial | ✅ Available | DeepL/Google Translate API |
| Chinese (Simplified) | `zh-CN` | ✅ Complete | ✅ Available | DeepL/Google Translate API |

## Architecture

### Backend Translation Service

Located at: `src/services/translation_service.py`

**Features:**
- Multiple translation backend support (DeepL, Google Translate)
- Automatic fallback strategy
- Language code normalization
- Medical context awareness
- Caching for efficiency

**Usage Example:**
```python
from src.services.translation_service import translate_text

result = await translate_text(
    text="The patient has hypertension",
    target_language="es",
    source_language="en",
    context="clinical"
)

print(result["translated_text"])  # "El paciente tiene hipertensión"
print(result["method"])  # "deepl" or "google"
print(result["success"])  # True
```

### Frontend i18n System

Located at: `static/js/i18n.js`

**Features:**
- Auto-detection of browser language
- Local storage persistence
- Dynamic page translation
- String interpolation support
- Fallback to English

**Usage Example:**
```javascript
// Initialize
await window.i18n.init();

// Get translation
const title = window.i18n.t('disease_lookup.title');
// Returns: "Disease Information Lookup" (en) or "疾病信息查询" (zh-CN)

// Change language
await window.i18n.changeLanguage('zh-CN');

// Translate entire page
window.i18n.translatePage();
```

**HTML Usage:**
```html
<!-- Text content -->
<h1 data-i18n="common.app_name">AI Nurse Florence</h1>

<!-- Placeholder text -->
<input data-i18n="chat.placeholder" placeholder="Type your clinical question...">

<!-- Title attribute -->
<button data-i18n-title="common.save">💾</button>
```

## API Translation Support

### Chat API

**Endpoint:** `POST /api/v1/chat`

**Request:**
```json
{
  "message": "What are the signs of sepsis?",
  "language": "zh-CN",
  "context": "clinical"
}
```

**Response:**
```json
{
  "response": "败血症的迹象包括...",
  "language": "zh-CN",
  "timestamp": "2025-10-01T12:00:00Z"
}
```

### Disease Lookup API

**Endpoint:** `GET /api/v1/disease/lookup?q=diabetes&language=es`

**Response:**
```json
{
  "query": "diabetes",
  "description": "La diabetes es una enfermedad crónica...",
  "symptoms": ["Sed excesiva", "Micción frecuente", "Fatiga"],
  "disease_name": "Diabetes Mellitus",
  "language": "es"
}
```

### Translation Quality

- **Medical terminology:** Preserved and accurately translated
- **Context awareness:** Clinical context maintained across translations
- **Abbreviations:** Standard medical abbreviations preserved (e.g., BP, HR, RR)
- **Dosages:** Numerical values and units preserved

## Configuration

### Setting Up Translation API Keys

For production deployment with high-quality translations:

**Option 1: DeepL API (Recommended for medical content)**
```bash
export DEEPL_API_KEY="your-deepl-api-key"
```

**Option 2: Google Translate API**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `DEEPL_API_KEY` | DeepL translation API key | Optional (recommended) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Cloud credentials | Optional |

If no API keys are configured, the system will return English responses with a warning logged.

## Translation Files

### Location
`static/translations/{language_code}.json`

### Structure
```json
{
  "common": {
    "app_name": "AI Nurse Florence",
    "loading": "Loading...",
    "error": "Error"
  },
  "navigation": {
    "home": "Home",
    "dashboard": "Dashboard"
  },
  "chat": {
    "title": "Clinical Chat Assistant",
    "placeholder": "Type your clinical question..."
  }
}
```

### Adding a New Language

1. **Create translation file:**
   ```bash
   cp static/translations/en.json static/translations/fr.json
   ```

2. **Translate content:**
   Edit `fr.json` and translate all strings to French

3. **Update i18n.js:**
   Add language to `supportedLanguages` object:
   ```javascript
   'fr': { name: 'French', native: 'Français', flag: '🇫🇷' }
   ```

4. **Update translation service:**
   Add to `LANGUAGE_INFO` in `src/services/translation_service.py`:
   ```python
   "fr": {"name": "French", "native": "Français", "flag": "🇫🇷"}
   ```

5. **Test:**
   ```javascript
   await window.i18n.changeLanguage('fr');
   ```

## Frontend Integration Examples

### Language Selector Component

```html
<select id="language-selector" onchange="changeLanguage(this.value)">
  <option value="en">English</option>
  <option value="es">Español</option>
  <option value="zh-CN">简体中文</option>
</select>

<script>
async function changeLanguage(lang) {
  await window.i18n.changeLanguage(lang);
  window.i18n.translatePage();

  // Also update API calls
  updateApiLanguage(lang);
}

function updateApiLanguage(lang) {
  // Store for future API requests
  localStorage.setItem('api_language', lang);
}
</script>
```

### Making API Calls with Language

```javascript
async function searchDisease(query) {
  const language = window.i18n.getCurrentLanguage();

  const response = await fetch(
    `/api/v1/disease/lookup?q=${encodeURIComponent(query)}&language=${language}`
  );

  return await response.json();
}
```

## Testing

### Backend Tests

```python
import pytest
from src.services.translation_service import translate_text

@pytest.mark.asyncio
async def test_english_to_spanish():
    result = await translate_text(
        "Patient has chest pain",
        target_language="es"
    )
    assert result["success"] == True
    assert "dolor" in result["translated_text"].lower()

@pytest.mark.asyncio
async def test_english_to_chinese():
    result = await translate_text(
        "High blood pressure",
        target_language="zh-CN"
    )
    assert result["success"] == True
```

### Frontend Tests

```javascript
// Test i18n initialization
await window.i18n.init();
assert(window.i18n.getCurrentLanguage() === 'en');

// Test translation
const translation = window.i18n.t('common.loading');
assert(translation === 'Loading...');

// Test language change
await window.i18n.changeLanguage('zh-CN');
const chineseTranslation = window.i18n.t('common.loading');
assert(chineseTranslation === '加载中...');
```

## Performance Considerations

### Caching
- Translation results are cached to minimize API calls
- UI translations are loaded once and stored in memory
- Language preference is persisted in localStorage

### API Rate Limits
- DeepL Free: 500,000 characters/month
- DeepL Pro: Pay per character
- Google Translate: Pay per character

### Optimization Tips
1. Pre-translate common responses
2. Use caching for frequently translated content
3. Batch translation requests when possible
4. Consider using a translation memory system for medical terms

## Troubleshooting

### Translation Not Working

**Check logs:**
```bash
tail -f logs/florence.log | grep translation
```

**Common issues:**
- API key not configured
- Invalid language code
- Network connectivity to translation service
- Rate limit exceeded

### UI Not Translating

**Check console:**
```javascript
console.log(window.i18n.translations);
console.log(window.i18n.getCurrentLanguage());
```

**Common fixes:**
- Ensure i18n.js is loaded before other scripts
- Check translation file exists for language
- Verify data-i18n attributes are correct
- Call `translatePage()` after dynamic content changes

## Best Practices

1. **Always provide fallback:** English should be the fallback for all missing translations
2. **Medical accuracy:** Review machine translations with medical professionals
3. **Cultural sensitivity:** Consider cultural differences in medical communication
4. **Test thoroughly:** Test all languages with native speakers when possible
5. **Document limitations:** Clearly indicate machine-translated content
6. **Regular updates:** Keep translation files synchronized with new features

## Future Enhancements

- [ ] Add Traditional Chinese (zh-TW) support
- [ ] Add Arabic (ar) support for right-to-left text
- [ ] Implement translation memory for consistency
- [ ] Add crowdsourced translation improvements
- [ ] Support for dialectical variations
- [ ] Voice input/output in multiple languages
- [ ] Real-time translation in chat interface

## Resources

- [DeepL API Documentation](https://www.deepl.com/docs-api)
- [Google Translate API Documentation](https://cloud.google.com/translate/docs)
- [Medical Translation Best Practices](https://www.atanet.org/certification/medical-translation/)
- [WCAG Internationalization Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/)

## Support

For translation issues or requests for new languages:
- Email: support@florence-ai.org
- GitHub Issues: [Report a translation issue](https://github.com/silversurfer562/ai-nurse-florence/issues/new)
