# TODO Audit - October 7, 2025

**Generated:** 2025-10-07
**Purpose:** Comprehensive audit of TODO, FIXME, XXX, and HACK comments in codebase
**Scope:** Python backend and TypeScript/React frontend (excluding node_modules, archive, dist)

**Summary:**
- **Total TODOs:** 78 (76 Python + 2 TypeScript)
- **Status:** Most are deferred features from FUTURE_FEATURES.md
- **Priority Distribution:** See categories below

---

## High Priority (Recommend Implementation)

### Backend API & Services

#### 🔴 Patient Documents - Drug Interactions
**File:** `routers/patient_documents.py`
- `TODO: Integrate with FDA OpenFDA API` - Drug interaction checking
- `TODO: Implement PDF merging using PyPDF2 or similar` - Multi-page document assembly
- **Effort:** 4-6 hours
- **Impact:** Critical patient safety feature
- **Dependencies:** FDA OpenFDA API key, PyPDF2 library
- **Note:** Currently listed in FUTURE_FEATURES.md

#### 🔴 Clinical Decision Support
**File:** `src/routers/clinical_decision_support.py`
- `TODO: Integrate with risk assessment service` - Risk scoring integration
- `TODO: Implement assessment-specific logic` - Different assessment types
- `TODO: Return structured risk scores` - Standardized response format
- **Effort:** 6-8 hours
- **Impact:** Core clinical feature, already has risk assessment service implemented
- **Dependencies:** Existing risk assessment service (already implemented)
- **Status:** HIGH PRIORITY - Infrastructure exists, just needs integration

#### 🔴 Rate Limiting
**File:** `src/routers/api.py`
- `TODO: Implement rate limiting configuration` - API protection
- **File:** `src/middleware/rate_limit.py` (referenced in FUTURE_FEATURES.md)
- **Effort:** 2-3 hours
- **Impact:** Production readiness, prevent abuse
- **Dependencies:** Token bucket algorithm implementation
- **Note:** Already listed as Critical in FUTURE_FEATURES.md

---

## Medium Priority (Can Be Deferred)

### Frontend Components

#### 🟡 MedicationTemplate Enhancements
**File:** `frontend/src/components/MedicationTemplate.tsx`
- `TODO: In real implementation, categorize into serious vs common` - Side effect severity categorization
- `TODO: Parse severity from text` - Automated severity detection
- **Effort:** 3-4 hours
- **Impact:** Better patient education quality
- **Dependencies:** Side effect classification algorithm

#### 🟡 Patient Education
**File:** `routers/patient_education_documents.py`
- `TODO: Implement HTML preview` - Preview before PDF generation
- **Effort:** 3-4 hours
- **Impact:** Better UX
- **Note:** Already listed in FUTURE_FEATURES.md as "HTML Preview Before PDF"

#### 🟡 UI Router Implementation
**File:** `src/routers/ui.py`
- `TODO: Implement template rendering with React components`
- `TODO: Add clinical workflow context`
- `TODO: Progressive enhancement fallbacks`
- `TODO: Implement SBAR wizard template`
- `TODO: Multi-step workflow interface`
- `TODO: React component integration`
- **Effort:** 8-12 hours total
- **Impact:** Enhanced UI capabilities
- **Status:** UI routes may be superseded by current React frontend architecture

---

## Low Priority / Deferred

### ChatGPT Store Integration (18 TODOs)

**Status:** ⭕ DEFERRED - Per FUTURE_FEATURES.md decision
**Rationale:** Focus on core medical features first, defer until market validation
**Files Affected:**
- `src/routers/chatgpt_store.py` (6 TODOs)
- `src/utils/chatgpt_store.py` (6 TODOs)
- `src/services/chatgpt_store_service.py` (6 TODOs)

**Features:**
- Professional license validation
- JWT authentication
- Institution integration
- Custom clinical pathways per organization
- Professional verification database

**Estimated Total Effort:** 40-60 hours
**Decision:** Not implementing until product-market fit established

---

### Service Placeholders (Future Implementation)

#### 🟢 Drug Database Service
**File:** `src/services/drug_database_service.py`
- `TODO: Implement interaction lookup from database`
- **Effort:** 3-4 hours
- **Note:** Offline database exists, API integration would be enhancement

#### 🟢 Prompt Enhancement Service
**File:** `src/services/prompt_enhancement.py`
- `TODO: Implement enhance_prompt function for query clarification`
- `TODO: Add medical terminology normalization`
- `TODO: Create clarification question generation`
- `TODO: Add vague query detection patterns`
- **Effort:** 10-15 hours
- **Impact:** Better AI responses
- **Priority:** Enhancement, not critical

#### 🟢 Model Selector Service
**Files:**
- `src/services/model_selector.py`
- `services/model_selector.py`
- `TODO: Implement model selection logic (GPT-4 vs GPT-4o)`
- `TODO: Add context analysis for clinical vs general queries`
- `TODO: Include cost optimization strategies`
- `TODO: Add model performance tracking`
- `TODO: Add actual API availability check when GPT-5 is released`
- **Effort:** 8-12 hours
- **Impact:** Cost optimization
- **Priority:** Enhancement for production scale

#### 🟢 Document Authoring Service
**File:** `src/services/document_authoring_service.py`
- `TODO: Implement SBAR generation logic`
- `TODO: Add clinical validation`
- `TODO: Format according to healthcare standards`
- `TODO: Implement care plan generation`
- `TODO: Add evidence-based interventions`
- `TODO: Include assessment criteria`
- **Effort:** 12-16 hours
- **Note:** SBAR already has frontend wizard, may just need backend integration

---

## Testing TODOs (Test Infrastructure)

### Test Placeholders
**Files:**
- `tests/__init__.py` (3 TODOs)
- `tests/test_react_components.py` (4 TODOs)
- `tests/test_chatgpt_integration.py` (4 TODOs)

**Status:** ⭕ Test infrastructure placeholders
**Note:** These are empty test file templates, not critical path
**Effort:** 20-30 hours for full test coverage
**Priority:** Low - implement as features are developed

---

## Model & Infrastructure Placeholders

### Missing Router Implementations
**File:** `src/routers/__init__.py`
- `TODO: Implement these routers when needed:`
  - `conversation.py` - Chat/conversation history
  - `users.py` - User management (beyond basic auth)
  - `med_check.py` - Medication checking workflows
  - `educational.py` - Educational content management
- **Status:** Documented placeholders for future features
- **Effort:** 6-10 hours each
- **Priority:** As user demand emerges
- **Note:** Already tracked in FUTURE_FEATURES.md

### Model Infrastructure
**File:** `src/models/__init__.py`
- `TODO: Export Pydantic schemas and SQLAlchemy models`
- `TODO: Add model factory functions`
- `TODO: Implement async SQLAlchemy patterns`
- **Status:** Infrastructure improvements
- **Effort:** 6-8 hours
- **Priority:** Low - current implementation works

---

## Scripts & Utilities

### Notion Sync Script
**File:** `scripts/sync_todos_to_notion.py`
- Contains "TODO" in documentation strings (not actual TODO items)
- Script purpose: Parse TODO items from markdown files
- **Status:** No action needed

---

## Summary by Category

### Critical (Immediate Action Recommended)
1. **Clinical Decision Support Integration** (6-8 hours) - Infrastructure exists
2. **Rate Limiting Configuration** (2-3 hours) - Production readiness
3. **FDA Drug API Integration** (4-6 hours) - Patient safety

**Total Critical Effort:** 12-17 hours

### Medium Priority (Next Sprint)
1. **MedicationTemplate Enhancements** (3-4 hours)
2. **HTML Preview Feature** (3-4 hours)
3. **UI Router Completion** (8-12 hours)

**Total Medium Effort:** 14-20 hours

### Deferred (Per FUTURE_FEATURES.md)
1. **ChatGPT Store Integration** (40-60 hours) - Deferred until market validation
2. **Test Infrastructure** (20-30 hours) - Implement as features develop
3. **Service Enhancements** (30-40 hours) - Performance optimizations

**Total Deferred Effort:** 90-130 hours

---

## Recommendations

### Immediate Next Steps (This Week)
1. ✅ **Clinical Decision Support Integration** - High impact, infrastructure ready
2. ✅ **Rate Limiting** - Production requirement
3. ✅ **FDA Drug API** - Patient safety critical

### Next Sprint (1-2 Weeks)
1. MedicationTemplate side effect categorization
2. HTML preview feature for documents
3. Complete UI router implementations if still needed

### Quarterly Planning
1. Evaluate ChatGPT Store integration based on user demand
2. Implement comprehensive test coverage
3. Service optimization (prompt enhancement, model selection)

---

## Cross-Reference with Existing Documentation

This audit aligns with:
- **[FUTURE_FEATURES.md](FUTURE_FEATURES.md)** - Most TODOs already tracked here
- **[TODO_AUDIT_2025-10-06.md](TODO_AUDIT_2025-10-06.md)** - Previous audit (1 day ago)
- **[DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)** - Release planning

**Key Finding:** Most TODO comments are already properly tracked in FUTURE_FEATURES.md. The audit confirms our documentation is up-to-date and comprehensive.

---

## Notes

- **Code Quality:** TODOs are well-documented with clear context
- **Documentation:** Most items already tracked in FUTURE_FEATURES.md
- **Priority Alignment:** Deferred items match strategic decisions
- **Technical Debt:** Minimal - most TODOs are feature placeholders, not fixes

**Last Updated:** 2025-10-07
