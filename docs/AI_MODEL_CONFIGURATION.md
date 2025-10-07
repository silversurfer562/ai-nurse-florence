# AI Model Configuration Guide

**AI Nurse Florence** supports multiple AI providers with easy switching via environment variables.

---

## Quick Start

### Default Setup (Recommended)

```bash
# .env
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-key-here
```

**Why this is the sweet spot:**
- ✅ 64% cheaper than gpt-3.5-turbo ($0.15 vs $0.50 per 1M tokens)
- ✅ Better quality than gpt-3.5-turbo
- ✅ Faster response times
- ✅ Perfect for 95% of use cases

---

## Switching to Claude for Best Quality

When you want the absolute best quality (complex clinical reasoning, critical documentation):

```bash
# .env
AI_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your-key-here
```

**When to use:**
- Complex clinical case analysis
- Final production documentation
- Critical patient safety decisions
- When accuracy matters more than cost

---

## Cost Comparison

### Per 10,000 API Calls (1K input + 500 output tokens)

| Model | Provider | Cost | Speed | Quality | Use Case |
|-------|----------|------|-------|---------|----------|
| **gpt-4o-mini** ⭐ | OpenAI | **$4.50** | ⚡⚡ | 🟢🟢 | **Development/Testing** |
| claude-3-haiku | Anthropic | $8.80 | ⚡⚡ | 🟢🟢 | Alternative dev |
| gpt-3.5-turbo | OpenAI | $12.50 | ⚡ | 🟢 | Deprecated |
| **gpt-4o** ⭐ | OpenAI | **$75.00** | 🟡 | 🟢🟢🟢 | **Production** |
| **claude-3-5-sonnet** ⭐ | Anthropic | **$105.00** | 🟡 | 🟢🟢🟢🟢 | **Best Quality** |
| gpt-4-turbo | OpenAI | $250.00 | 🟡 | 🟢🟢🟢 | Usually not needed |
| claude-3-opus | Anthropic | $525.00 | 🔴 | 🟢🟢🟢🟢 | Rarely needed |

---

## Environment-Specific Configuration

### Development (.env.development)
```bash
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-dev-key
```

**Goal:** Fast iteration, low cost

---

### Staging (.env.staging)
```bash
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4o
OPENAI_API_KEY=your-staging-key
```

**Goal:** Test production-quality responses

---

### Production (.env.production)
```bash
# Option 1: Cost-optimized (recommended initially)
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4o
OPENAI_API_KEY=your-prod-key

# Option 2: Quality-optimized (when you need the best)
AI_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your-prod-key
```

**Goal:** Best balance of cost/quality for real users

---

## How to Switch Models

### Method 1: Environment Variable (Recommended)

```bash
# Switch to Claude for best quality
export AI_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your-key

# Or switch back to OpenAI for cost savings
export AI_PROVIDER=openai
export OPENAI_MODEL=gpt-4o-mini
```

### Method 2: .env File

Edit your `.env` file:

```bash
# Use gpt-4o-mini by default (fast & cheap)
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini

# When you need best quality, uncomment these:
# AI_PROVIDER=anthropic
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Method 3: Railway Dashboard

In Railway environment variables, set:
- `AI_PROVIDER=anthropic`
- `ANTHROPIC_API_KEY=your-key`
- `ANTHROPIC_MODEL=claude-3-5-sonnet-20241022`

**No code deployment needed!** Changes take effect on next app restart.

---

## Model Selection Decision Tree

```
┌─────────────────────────────────┐
│   What are you doing?           │
└─────────────────────────────────┘
               │
               ├─ Development/Testing?
               │  └─> Use: gpt-4o-mini ($4.50/10K calls)
               │
               ├─ Production (normal)?
               │  └─> Use: gpt-4o ($75/10K calls)
               │
               ├─ Critical clinical decisions?
               │  └─> Use: claude-3-5-sonnet ($105/10K calls)
               │
               └─ Cost is no object?
                  └─> Use: claude-3-opus ($525/10K calls)
```

---

## Configuration Reference

### All Available Settings

```bash
# ================================
# AI Provider Selection
# ================================
AI_PROVIDER=openai  # or 'anthropic'

# ================================
# OpenAI Configuration
# ================================
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Available OpenAI Models:
#   gpt-4o-mini        ($0.15/$0.60 per 1M tokens) ⭐ Recommended for dev
#   gpt-4o             ($2.50/$10 per 1M tokens)   ⭐ Recommended for prod
#   gpt-4-turbo        ($10/$30 per 1M tokens)     Usually overkill
#   gpt-3.5-turbo      ($0.50/$1.50 per 1M)        Deprecated

# ================================
# Anthropic Claude Configuration
# ================================
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Available Anthropic Models:
#   claude-3-haiku                    ($0.25/$1.25 per 1M) Fast & cheap
#   claude-3-5-sonnet-20241022        ($3/$15 per 1M)      ⭐ Best quality
#   claude-3-opus-20240229            ($15/$75 per 1M)     Exceptional
```

---

## Cost Examples for AI Nurse Florence

### Scenario: 1,000 patient interactions/month

**Average tokens per interaction:**
- Input: 1,500 tokens (patient data, query)
- Output: 800 tokens (AI response)

| Configuration | Monthly Cost | Annual Cost | Quality |
|---------------|-------------|-------------|---------|
| **gpt-4o-mini everywhere** | **$13.50** | **$162** | Good (90% use cases) |
| gpt-4o-mini (dev) + gpt-4o (prod) | $67.50 | $810 | Excellent |
| **gpt-4o everywhere** ⭐ | **$112.50** | **$1,350** | Excellent |
| claude-3-5-sonnet everywhere | $157.50 | $1,890 | Exceptional |

**Recommended approach:**
1. **Start with gpt-4o-mini** ($162/year)
2. Monitor quality metrics
3. **Upgrade to gpt-4o** if quality issues ($1,350/year)
4. **Use Claude** for final production releases ($1,890/year)

---

## Admin Control Philosophy

**Why we use environment configuration instead of code logic:**

1. ✅ **Cost Control** - Admins control budget per environment
2. ✅ **No Surprises** - Code changes won't cause unexpected cost spikes
3. ✅ **Easy Testing** - Test new models in staging before production
4. ✅ **Compliance** - Audit which models are approved
5. ✅ **Flexibility** - Switch models without code deployment

---

## FAQ

### Q: Can I use both providers simultaneously?
**A:** Yes! Set both API keys, then switch between them using `AI_PROVIDER`.

### Q: What happens if both API keys are set?
**A:** The system uses `AI_PROVIDER` to choose. If not set, defaults to OpenAI.

### Q: Can different features use different models?
**A:** Currently no - this is an admin decision, not per-feature. All API calls use the configured model.

### Q: What's the fastest way to switch to Claude?
**A:** Set `AI_PROVIDER=anthropic` in your environment variables. No code changes needed!

### Q: Should I use gpt-4-turbo or claude-3-opus?
**A:** Probably not. Both are very expensive and usually overkill. Start with gpt-4o or claude-3-5-sonnet.

### Q: When should I use Claude over OpenAI?
**A:**
- Complex clinical reasoning
- Long context (200K tokens)
- Better instruction following
- When quality matters more than cost

---

## Getting API Keys

### OpenAI
1. Visit https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy key (starts with `sk-`)
5. Add to `.env`: `OPENAI_API_KEY=sk-...`

### Anthropic Claude
1. Visit https://console.anthropic.com/
2. Sign in or create account
3. Go to API Keys section
4. Create new key
5. Copy key (starts with `sk-ant-`)
6. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

---

## Quick Reference Card

```bash
# COPY-PASTE CONFIGURATIONS

# === Development (Cheapest) ===
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
# Cost: $4.50/10K calls

# === Production (Balanced) ===
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4o
# Cost: $75/10K calls

# === Best Quality (Your Request) ===
AI_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
# Cost: $105/10K calls
```

---

## Related Documentation

- [Configuration Management](../src/utils/config.py) - Implementation details
- [TODO Audit](TODO_AUDIT_2025-10-07.md) - Model selector decision rationale
- [.env.example](../.env.example) - Full configuration template

---

**Last Updated:** 2025-10-07
**Version:** 2.4.2
