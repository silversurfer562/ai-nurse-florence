# TODO Audit - October 6, 2025

**Purpose:** Review all TODOs in codebase and determine which are still relevant given:
- New evergreen documentation standards
- Current feature set
- Project priorities

---

## Summary

**Total TODOs Found:** 38 across codebase
**Status Breakdown:**
- ✅ **Obsolete/Replaced by Documentation:** 8 TODOs
- 🔄 **Still Relevant - Medium Priority:** 12 TODOs
- ⭕ **Not Needed Yet - Future Feature:** 18 TODOs

---

## ✅ OBSOLETE - Remove These (Replaced by Documentation Standard)

### 1. Documentation-related TODOs
**File:** `src/utils/swagger_enhancements.py:58-60, 88-90`
```python
# TODO: Add clinical examples to schema
# TODO: Enhanced documentation for healthcare workflows
# TODO: Professional authentication schemas
```

**Status:** ✅ **REMOVE** - Documentation is now handled by evergreen docstrings
**Action:** Delete these TODOs, add docstrings instead

### 2. Export utilities TODOs
**File:** `src/utils/__init__.py:7-9`
```python
# TODO: Export utility functions and classes
# TODO: Add conditional imports for optional dependencies
# TODO: Implement graceful degradation patterns
```

**Status:** ✅ **REMOVE** - Already implemented via conditional imports pattern
**Action:** Delete TODOs, module already follows best practices

---

## 🔄 STILL RELEVANT - Medium Priority (Keep & Track)

### 1. Patient Documents - FDA Integration
**File:** `routers/patient_documents.py:186`
```python
# TODO: Integrate with FDA OpenFDA API
```

**Status:** 🔄 **KEEP** - Feature enhancement
**Priority:** Medium
**Effort:** 3-6 hours
**Notes:** Currently uses fallback data, FDA API would improve accuracy

### 2. PDF Merging
**File:** `routers/patient_documents.py:515`
```python
# TODO: Implement PDF merging using PyPDF2 or similar
```

**Status:** 🔄 **KEEP** - Feature enhancement
**Priority:** Low
**Effort:** 2-3 hours
**Notes:** Nice-to-have for combining multiple patient documents

### 3. HTML Preview
**File:** `routers/patient_education_documents.py:175`
```python
html_preview_url=None,  # TODO: Implement HTML preview
```

**Status:** 🔄 **KEEP** - UX improvement
**Priority:** Low
**Effort:** 2-4 hours
**Notes:** Allow preview before PDF generation

### 4. Risk Assessment Service
**File:** `src/routers/clinical_decision_support.py:66-72`
```python
# TODO: Integrate with risk assessment service
# TODO: Implement assessment-specific logic
# TODO: Return structured risk scores
```

**Status:** 🔄 **KEEP** - Core feature
**Priority:** High
**Effort:** 1-2 days
**Notes:** Part of clinical decision support - important for medical accuracy

### 5. Rate Limiting
**File:** `src/routers/api.py:32`
```python
# TODO: Implement rate limiting configuration
```

**Status:** 🔄 **KEEP** - Production readiness
**Priority:** Medium
**Effort:** 2-3 hours
**Notes:** Prevent API abuse, already has infrastructure (RateLimitMiddleware warning)

### 6. Missing Routers
**File:** `src/routers/__init__.py:172`
```python
# TODO: Implement these routers when needed:
#   - conversation.py: Chat/conversation history
#   - users.py: User management
#   - med_check.py: Medication checking
#   - educational.py: Educational content management
```

**Status:** 🔄 **KEEP** - Documented as future work
**Priority:** Low (already documented)
**Effort:** Varies per router
**Notes:** Good as-is, clear documentation of what's missing

---

## ⭕ NOT NEEDED YET - Future Feature (Keep but Low Priority)

### 1. ChatGPT Store Integration (8 TODOs)
**Files:**
- `src/routers/chatgpt_store.py:32-52`
- `src/utils/chatgpt_store.py:30-56`

**TODOs:**
- GPT-optimized clinical interventions
- Professional license validation
- Institution validation
- JWT token validation
- Nursing license verification

**Status:** ⭕ **KEEP BUT DEFER** - Future monetization feature
**Priority:** Very Low (not current roadmap)
**Effort:** 2-3 weeks full implementation
**Notes:** ChatGPT Store integration is a future business opportunity, not current priority

### 2. UI Router React Integration (6 TODOs)
**File:** `src/routers/ui.py:34-58`

**TODOs:**
- Template rendering with React components
- Clinical workflow context
- Progressive enhancement fallbacks
- SBAR wizard template
- Multi-step workflow interface

**Status:** ⭕ **KEEP BUT DEFER** - Server-side rendering not needed
**Priority:** Very Low
**Notes:** Frontend is already React-based, SSR not a priority

### 3. Clinical Workflow Middleware
**File:** `src/routers/api.py:33`
```python
# TODO: Add middleware for clinical workflows
```

**Status:** ⭕ **DEFER** - Not clear what this means
**Priority:** Low
**Effort:** Unknown
**Notes:** Needs requirements definition first

---

## Recommended Actions

### Immediate (This Session)

1. **Delete Obsolete TODOs** (8 TODOs)
   - Files: `swagger_enhancements.py`, `utils/__init__.py`
   - Replace with docstrings where needed
   - Time: 15 minutes

2. **Convert Relevant TODOs to Self-Improvement Checklists**
   - Files: `patient_documents.py`, `clinical_decision_support.py`
   - Move to evergreen checklist format
   - Time: 30 minutes

### Near-term (Next 1-2 Sessions)

3. **Implement High-Priority TODOs**
   - Risk Assessment Service integration
   - Rate limiting configuration
   - Time: 4-6 hours

4. **Track Medium-Priority in Notion**
   - FDA OpenFDA integration
   - PDF merging
   - HTML preview
   - Time: Track in Notion database

### Long-term (Backlog)

5. **ChatGPT Store Integration** - Defer until business need
6. **UI Router SSR** - Defer indefinitely (not needed)

---

## Updated TODO Count by Priority

| Priority | Count | Action |
|----------|-------|--------|
| ✅ Delete | 8 | Remove from codebase |
| 🔴 High | 4 | Implement soon (Risk Assessment, Rate Limiting) |
| 🟡 Medium | 4 | Track in Notion (FDA API, PDF merge, HTML preview) |
| 🟢 Low | 4 | Documented, no action needed (Missing routers) |
| ⭕ Defer | 18 | Keep but don't prioritize (ChatGPT Store, SSR) |

---

## Files Requiring Updates

### Clean up (remove TODOs):
1. `src/utils/swagger_enhancements.py` - Remove 6 TODOs, add docstrings
2. `src/utils/__init__.py` - Remove 3 TODOs

### Convert to Checklist Format:
1. `routers/patient_documents.py` - Add improvement checklist
2. `src/routers/clinical_decision_support.py` - Add improvement checklist
3. `routers/patient_education_documents.py` - Add improvement checklist

### Keep As-Is (already good):
1. `src/routers/__init__.py` - Clear documentation of missing routers
2. `src/routers/chatgpt_store.py` - Future feature, well-documented
3. `src/routers/ui.py` - SSR feature, not priority

---

**Next Step:** Delete obsolete TODOs and convert relevant ones to improvement checklists

**Created:** 2025-10-06
