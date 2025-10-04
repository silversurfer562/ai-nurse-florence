# Naming Convention Standardization Plan

## Current Issues

The codebase has inconsistent naming conventions across frontend and backend:

### Frontend Issues (TypeScript/React)
- **Mixed property names:** Some use `camelCase`, others use `snake_case`
  - Examples: `quick_start` vs `quickStart`, `related_tasks` vs `relatedTasks`
- **JSON data structures:** Inconsistent between files
  - `help-content.json` uses both styles
  - API responses use `snake_case` (Python convention)
  - Frontend components expect `camelCase` (TypeScript convention)

### Backend Issues (Python)
- Generally follows Python conventions (`snake_case`)
- Some inconsistencies in API response formatting

## Recommended Standards

### ✅ Frontend (TypeScript/React)
**Use `camelCase` for:**
- Variable names: `userName`, `currentStep`
- Function names: `handleClick`, `fetchData`
- Component props: `isOpen`, `onClose`
- JSON object keys: `firstName`, `phoneNumber`
- State variables: `selectedTask`, `searchQuery`

**Use `PascalCase` for:**
- Component names: `HelpSystem`, `LanguageSelector`
- Type/Interface names: `HelpSystemProps`, `UserData`

**Use `kebab-case` for:**
- File names: `help-system.tsx`, `language-selector.tsx`
- CSS classes: `btn-primary`, `card-header`

### ✅ Backend (Python)
**Use `snake_case` for:**
- Variable names: `user_name`, `current_step`
- Function names: `get_user_data`, `check_interactions`
- Database column names: `first_name`, `created_at`
- API endpoint paths: `/patient-education`, `/drug-interactions`

**Use `PascalCase` for:**
- Class names: `PatientEducation`, `DrugInteraction`
- Model names: `User`, `ContentSetting`

### 🔄 API Response Transformation

**Decision:** Use `snake_case` in API responses, transform to `camelCase` in frontend

**Why?**
- Backend naturally uses `snake_case` (Python standard)
- Frontend naturally uses `camelCase` (JavaScript/TypeScript standard)
- Clear separation of concerns

**Implementation:**
```typescript
// Frontend: Add response transformer utility
function toCamelCase(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(toCamelCase);
  }
  if (obj !== null && obj.constructor === Object) {
    return Object.keys(obj).reduce((result, key) => {
      const camelKey = key.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
      result[camelKey] = toCamelCase(obj[key]);
      return result;
    }, {} as any);
  }
  return obj;
}

// Use in API calls
const response = await fetch('/api/v1/disease/lookup');
const data = toCamelCase(await response.json());
```

## Cleanup Tasks

### Phase 1: Critical Fixes (High Priority) ⚠️
**Files with build-breaking issues:**
1. ✅ `frontend/src/components/Help/HelpSystem.tsx` - Fixed (quickStart properties)
2. `frontend/src/data/help-content.json` - Standardize to camelCase throughout
3. Any other components importing help-content.json

**Estimated Time:** 2-3 hours

### Phase 2: Frontend Standardization (Medium Priority)
**Convert all frontend JSON/data files to camelCase:**
1. Review all `.json` files in `frontend/src/data/`
2. Update TypeScript interfaces to match
3. Update component code to use camelCase properties
4. Add response transformer for API calls

**Estimated Time:** 1 day

### Phase 3: API Response Consistency (Medium Priority)
**Add transformation layer:**
1. Create API client utility with automatic camelCase conversion
2. Update all API service files to use the utility
3. Update TypeScript types to reflect camelCase
4. Test all API endpoints

**Estimated Time:** 1-2 days

### Phase 4: Backend Consistency Check (Low Priority)
**Audit Python code:**
1. Verify all Python code uses `snake_case` for variables/functions
2. Verify all models use `snake_case` for fields
3. Check API endpoint naming is consistent
4. Document any exceptions with justification

**Estimated Time:** 1 day

## Implementation Plan

### Week 1: Critical & Frontend
- [ ] Fix remaining help-content.json issues
- [ ] Standardize all frontend JSON data files
- [ ] Update TypeScript interfaces
- [ ] Test all affected components

### Week 2: API Layer
- [ ] Create API response transformer utility
- [ ] Update API service files
- [ ] Add TypeScript types for transformed responses
- [ ] Test all API integrations

### Week 3: Backend Audit
- [ ] Review Python code consistency
- [ ] Document naming conventions in CLAUDE.md
- [ ] Update coding standards documentation
- [ ] Final testing and validation

## Files to Update

### High Priority (Breaking Issues)
- [x] `frontend/src/components/Help/HelpSystem.tsx`
- [ ] `frontend/src/data/help-content.json`

### Medium Priority (Consistency)
- [ ] All components importing JSON data
- [ ] All API service files
- [ ] TypeScript type definitions
- [ ] API response models

### Documentation
- [ ] Update CLAUDE.md with naming standards
- [ ] Create frontend coding style guide
- [ ] Create backend coding style guide
- [ ] Add to onboarding documentation

## Testing Strategy

### Before Standardization
1. Take snapshot of all tests passing
2. Document current behavior
3. Create test cases for edge cases

### During Standardization
1. Update tests alongside code changes
2. Run test suite after each file update
3. Verify no regressions

### After Standardization
1. Full test suite must pass
2. Manual testing of all features
3. Code review of changes
4. Update documentation

## Success Criteria

✅ **Complete when:**
- All TypeScript builds without errors
- All tests pass
- No `snake_case` in frontend JSON/data files
- No `camelCase` in Python variable names (except imports)
- API responses consistently use `snake_case`
- Frontend automatically transforms to `camelCase`
- Documentation updated
- Team trained on new standards

## Long-term Maintenance

### Pre-commit Hooks
Add linting rules to enforce naming conventions:
```json
// .eslintrc.json
{
  "rules": {
    "camelcase": ["error", { "properties": "always" }]
  }
}
```

### Code Review Checklist
- [ ] New JSON data uses camelCase (frontend)
- [ ] New Python code uses snake_case
- [ ] API responses use snake_case
- [ ] TypeScript types match camelCase convention
- [ ] No mixed naming in same file

### Documentation
- Naming convention guide in CLAUDE.md
- Examples in each section
- Rationale for decisions
- How to handle edge cases

---

## Quick Reference

| Context | Convention | Example |
|---------|-----------|---------|
| **Frontend Variables** | camelCase | `userName`, `isActive` |
| **Frontend Components** | PascalCase | `HelpSystem`, `UserProfile` |
| **Frontend Files** | kebab-case | `help-system.tsx` |
| **Frontend JSON Keys** | camelCase | `firstName`, `phoneNumber` |
| **Python Variables** | snake_case | `user_name`, `is_active` |
| **Python Classes** | PascalCase | `UserProfile`, `ContentSetting` |
| **Python Files** | snake_case | `disease_service.py` |
| **API Responses** | snake_case | `first_name`, `phone_number` |
| **Database Columns** | snake_case | `created_at`, `user_id` |
| **API Endpoints** | kebab-case | `/patient-education` |
| **CSS Classes** | kebab-case | `btn-primary`, `card-header` |

---

**Status:** Plan created, Phase 1 partially complete (HelpSystem fixed)
**Next Step:** Fix help-content.json to use camelCase consistently
**Owner:** Development Team
**Priority:** Medium (after critical bugs fixed)
**Timeline:** 3 weeks for full implementation
