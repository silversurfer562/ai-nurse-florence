# AI Nurse Florence - Project Context

## Project Overview
AI Nurse Florence is a healthcare application that provides disease information lookup and medical reference capabilities. The application features voice dictation for disease searches and integrates with myGene.info for genetic information.

## Tech Stack
- **Frontend**: React (Vite + TypeScript) - Two frontend directories exist (`frontend/`, `frontend-react/`)
- **Backend**: FastAPI (Python) with async support
- **Database**: SQLAlchemy with SQLite (dev) / PostgreSQL (production)
- **Caching**: Redis for session and API response caching
- **Deployment**: Railway (containerized with Docker)
- **Testing**: pytest for backend, ESLint for frontend
- **Features**: Voice dictation, disease search, myGene.info integration, SBAR wizards, document generation

## Recent Development
- Version 2.3.0
- Redesigned disease information display for professional clinical presentation
- Added voice dictation to disease search
- Integrated myGene.info for genetic data
- Cleaned up dashboard UI (removed stats section, moved disclaimer)
- 132 API endpoints across 18 routers
- Live medical data from FDA, NIH, PubMed, ClinicalTrials.gov

## Key Directories
- `/frontend` - React frontend application (Vite)
- `/frontend-react` - Alternative React frontend with widgets system
- `/routers` - FastAPI route handlers (18 routers)
- `/services` - Backend service layer
- `/models` - SQLAlchemy database models
- `/tests` - Pytest test suite
- `/docs` - Project documentation and planning documents
- `/scripts` - Utility scripts
- Root contains Docker configuration for Railway deployment

## MANDATORY Development Practices

### 1. Testing Protocol
**CRITICAL: Run comprehensive test suite before ANY publish/deploy**

```bash
# Backend tests (REQUIRED before commit/push)
pytest tests/ -v --tb=short

# Frontend linting (REQUIRED for edited files)
cd frontend && npm run lint
# OR
cd frontend-react && npm run lint

# Type checking
cd frontend-react && npm run type-check
```

**Rules:**
- ✅ ALL tests must pass before publishing
- ✅ Fix ALL test failures - no exceptions
- ✅ Run linting on ALL edited files
- ✅ Fix ALL linting errors before commit
- ⚠️ If tests are broken, FIX the tests AND the code
- 📝 Update tests when adding new features

### 2. Publishing Process
When user requests "publish", "deploy", or "release":

1. **Run full test suite**
   ```bash
   pytest tests/ -v
   ```

2. **Lint all edited files**
   - Track which files you modified in the session
   - Run ESLint on each edited frontend file
   - Fix all linting issues

3. **Type check (TypeScript files)**
   ```bash
   cd frontend-react && npm run type-check
   ```

4. **Create git commit** (only if tests pass)
   - Follow conventional commit format
   - Reference issue numbers if applicable

5. **Push to remote** (daily at 6 a.m. or when explicitly requested)

### 3. Documentation Requirements
**CRITICAL: Document ALL new features comprehensively**

For EVERY new feature you must update:

#### A. Code Documentation
```python
# Python: Comprehensive docstrings
def new_feature(param: str) -> dict:
    """
    Brief description of what this does.

    Args:
        param: Description of parameter

    Returns:
        dict: Description of return value

    Raises:
        ValueError: When validation fails

    Example:
        >>> result = new_feature("test")
        >>> print(result)
        {'status': 'success'}
    """
```

```typescript
// TypeScript: JSDoc comments
/**
 * Brief description of component/function
 *
 * @param props - Component props
 * @param props.value - Description of prop
 * @returns JSX element
 *
 * @example
 * ```tsx
 * <NewComponent value="test" />
 * ```
 */
```

#### B. Help Content
- Update in-app help text for new features
- Add tooltips for new UI elements
- Update user-facing documentation

#### C. Planning Documents
Maintain these files (located in project root and `/docs`):
- `COMPREHENSIVE_IMPLEMENTATION_PLAN.md` - Overall project roadmap
- `PROJECT_REVIEW_AND_RECOMMENDATIONS.md` - Status and priorities
- `SESSION_SUMMARY_*.md` - Daily progress summaries
- Feature-specific summaries (e.g., `I18N_IMPLEMENTATION_SUMMARY.md`)

**Update relevant planning docs after completing features:**
```markdown
## [Feature Name] - Completed [Date]

### Implementation Summary
- What was built
- Key technical decisions
- API endpoints added
- Frontend components created

### Testing
- Test coverage added
- Test results

### Documentation
- Code documentation: ✅
- Help content: ✅
- API docs: ✅
```

### 4. Code Quality Standards

#### Naming Conventions
- Python: `snake_case` for functions/variables, `PascalCase` for classes
- TypeScript: `camelCase` for functions/variables, `PascalCase` for components/classes
- Files: `kebab-case.ts` or `snake_case.py`

#### Error Handling
```python
# Python: Specific exceptions with context
try:
    result = await service.fetch_data()
except HTTPException as e:
    logger.error(f"API error: {e.detail}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise HTTPException(status_code=500, detail="Internal error")
```

```typescript
// TypeScript: Proper error typing
try {
  const result = await api.fetchData();
} catch (error) {
  if (error instanceof ApiError) {
    console.error('API error:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

#### Security Practices
- ⚠️ **NEVER** store PHI (Protected Health Information) in database
- ✅ Session-only storage for patient data
- ✅ Validate all user inputs
- ✅ Use parameterized queries (SQLAlchemy ORM)
- ✅ Sanitize outputs
- ✅ HIPAA-aware design patterns

### 5. Git Workflow
```bash
# Commit message format (Conventional Commits)
<type>(<scope>): <description>

# Types: feat, fix, docs, style, refactor, test, chore
# Examples:
feat(disease-search): add voice dictation support
fix(api): handle timeout errors in PubMed service
docs(readme): update deployment instructions
test(wizards): add integration tests for SBAR wizard


### 6. Performance Guidelines
- Use Redis caching for external API calls
- Implement pagination for large datasets
- Lazy load heavy components
- Optimize database queries (use indexes)
- Monitor with prometheus metrics

## Development Guidelines
1. **Code References**: Use markdown link syntax for file references: [filename.ts](path/to/filename.ts) or [filename.ts:42](path/to/filename.ts#L42)
2. **Git Workflow**: Main branch is `main` - use this for PRs
3. **Docker**: Frontend is built in Docker for Railway deployment
4. **Healthcare Context**: This is a medical reference application - maintain professional, clinical presentation standards

## Common Tasks
- Disease information display and search functionality
- Voice input integration
- Genetic information lookup via myGene.info
- UI/UX improvements for clinical workflow
- SBAR wizard workflows
- Document generation (discharge instructions, medication guides, etc.)

## Important Notes
- Maintain professional medical presentation standards
- Ensure HIPAA-aware design patterns - **NEVER store patient data in database**
- Voice dictation is a key accessibility feature
- Session-only storage for all patient information
- Comprehensive test coverage is mandatory

## Testing Infrastructure
- **Backend**: pytest with async support, fixtures in `tests/conftest.py`
- **Frontend**: ESLint for code quality, TypeScript for type safety
- **Test markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- **Coverage**: Aim for >80% code coverage on new features

## Reference Documents
Key planning documents to review/update:
- `COMPREHENSIVE_IMPLEMENTATION_PLAN.md` - Feature roadmap
- `PROJECT_REVIEW_AND_RECOMMENDATIONS.md` - Current priorities
- `ARCHIVE_PLAN.md` - File cleanup strategy
- Feature summaries in root directory (e.g., `I18N_IMPLEMENTATION_SUMMARY.md`, `PDF_GENERATION_SUMMARY.md`)

## Document Consolidation Plan
Based on previous conversations, there are multiple planning documents that overlap:
- Merge deployment guides and update as changes are made at least once a day starting at 5 a.m.(RAILWAY-DEPLOYMENT.md, RAILWAY-DEPLOYMENT-CLEAN.md, PRODUCTION_DEPLOYMENT.md)
- Consolidate phase completion documents (PHASE_3_*.md, PHASE_4_*.md) into main roadmap
- Archive outdated status documents after extracting relevant information

---

## Railway Environment Strategy (CRITICAL)

### Production Environment (v2.3.0+)
**Purpose:** Stable, production-ready application for end users

**Deployment Rules:**
- ⛔ **NEVER deploy to production during work-hours** (publish before 8 AM or after 6 PM unless it's required because of and interption of services to nurses)
- ⛔ **NEVER deploy to production without thorough testing in development first**
- ✅ **ONLY deploy to production** during business hours when monitoring is possible
- ✅ **ALL tests must pass** before production deployment
- ✅ **Manual verification required** after deployment
- ✅ **Leave production STABLE** - minimal changes only

**When to Deploy to Production:**
- After features have been tested in development environment
- During non-business hours (not from 8 AM - 6 PM preferred unless an interuption of services to nurse happens)
- When you can monitor the deployment and respond to issues
- After webhook notifications are confirmed working
- Only for bug fixes, security updates, or approved new features

### Development Environment (v2.4.0-dev)
**Purpose:** Active development, testing, and experimentation

**Deployment Rules:**
- ✅ **USE DEVELOPMENT for all new work** starting after production is stable at v2.3.0
- ✅ **Deploy to development FIRST** - test thoroughly before considering production
- ✅ **Deploy to development at ANY time** (including early morning sessions)
- ✅ **Breaking changes allowed** in development
- ✅ **Experimental features** go here first
- ✅ **Rapid iteration** encouraged

**Development Workflow:**
```bash
# Switch to development environment
railway environment development

# Make changes, test locally
# ... development work ...

# Deploy to development for testing
railway up --detach --environment development

# Monitor and verify
railway logs --environment development

# Once stable and tested, consider production deployment
# (but only during business hours)
```

### Time-Based Deployment Guidelines

**Early Morning Sessions (5 AM - 8 AM):**
- ✅ Work on features and bug fixes
- ✅ Commit code to git
- ✅ Deploy to **DEVELOPMENT environment ONLY**
- ⛔ **DO NOT deploy to production**
- ✅ Test in development environment
- ✅ Document issues found for later production deployment

**Business Hours (8 AM - 6 PM):**
- ✅ Deploy to production only if needed
- ✅ Monitor deployments actively
- ✅ Respond to webhook notifications
- ✅ Verify functionality after deployment

**Evening/Night (after 6 PM):**
- ✅ Work on features and bug fixes
- ✅ Commit code to git
- ✅ Deploy to **DEVELOPMENT environment ONLY**
- ⛔ **DO NOT deploy to production** unless critical emergency

### Emergency Production Deployments

**ONLY deploy to production during business hours if:**
1. Critical security vulnerability discovered
2. Application completely down/broken for users
3. Data integrity issue affecting user safety
4. Explicitly requested by user

**Emergency Procedure:**
1. Document the emergency clearly
2. Test fix in development first (if time permits)
3. Deploy to production with detailed commit message
4. Monitor deployment completion
5. Verify fix is working
6. Document incident and resolution
7. Use the last stable build from git as a last resort if the errors can't be rapidly fixed.

---

## Deployment Verification Checklist

### Before Pushing to Production

1. **Environment Check**
   ```bash
   railway status
   # Verify: Environment: production
   ```

2. **Time Check**
   - Current time is between 8 AM - 6 PM? Only deploy if required by a loss of service. If that happens 
   - Current time is outside hours? ⛔ Deploy to development instead

3. **Testing Complete**
   - [ ] All pytest tests passing
   - [ ] Frontend linting clean
   - [ ] Tested in development environment
   - [ ] No breaking changes
   - [ ] Documentation updated

4. **Deployment Method**
   - Prefer: `git push origin main` (traceable, reproducible)
   - Avoid: `railway up` (uploads local files, less reproducible)

5. **Post-Deployment Verification**
   ```bash
   # Wait 2-3 minutes for deployment

   # Check version
   curl https://ainurseflorence.com/api/v1/health | jq '.version'

   # Verify key endpoints
   curl https://ainurseflorence.com/api/v1/disease/lookup?q=diabetes
   curl https://ainurseflorence.com/api/v1/genes/search?q=BRCA1

   # Check webhook notification received (if configured)
   ```

### After Deployment Completes

1. **Verify in Browser**
   - [ ] Open https://ainurseflorence.com
   - [ ] Check version number in UI
   - [ ] Test one feature that was changed
   - [ ] Verify no translation key placeholders showing
   - [ ] Check browser console for errors

2. **Check Railway Logs**
   ```bash
   railway logs --environment production
   # Look for errors or warnings
   ```

3. **Webhook Notification**
   - [ ] Received deployment success notification (email/Discord/Slack)
   - [ ] Health checks passed in notification

4. **Document Deployment**
   - Update relevant planning documents
   - Note any issues encountered
   - Record deployment time and version

---

## Common Deployment Issues & Solutions

### Issue: Translation Keys Showing (e.g., "common.appName")
**Symptom:** UI shows `common.appName` instead of "AI Nurse Florence"

**Cause:** Frontend translations not rebuilt or not deployed

**Solution:**
```bash
cd frontend
npm run build
git add frontend/dist frontend/public/locales
git commit -m "fix: rebuild frontend with updated translations"
git push origin main
```

### Issue: API 500 Errors After Deployment
**Symptom:** Frontend shows "Error 500" when calling API

**Cause:** Backend function signature mismatch (like clinical trials status parameter)

**Solution:**
1. Check Railway logs for specific error
2. Identify mismatched parameters or function calls
3. Fix backend code to match API contract
4. Test in development first
5. Deploy fix to production during business hours

### Issue: Multiple Deployments Queued
**Symptom:** Railway shows 2-3 deployments in progress

**Cause:** Running both `railway up` and `git push` close together

**Solution:**
- Use **either** `git push` **or** `railway up`, not both
- For production: prefer `git push` (more reliable)
- For development: `railway up --environment development` is fine for speed
- Wait for one deployment to complete before triggering another

### Issue: Deployment Stuck or Taking Too Long
**Symptom:** Railway deployment shows "Building" for >5 minutes

**Cause:** Frontend build failing, Docker build failing, or Railway issue

**Solution:**
1. Check Build Logs in Railway dashboard
2. Look for npm errors or Docker errors
3. Test build locally:
   ```bash
   cd frontend && npm run build
   docker build -t test .
   ```
4. Fix build errors and redeploy

### Issue: Old Version Still Showing After Deployment
**Symptom:** API health check shows old version number

**Cause:** Deployment hasn't completed yet or failed silently

**Solution:**
1. Wait 3-5 minutes for deployment to complete
2. Check Railway dashboard for deployment status
3. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
4. Check if deployment failed in Railway logs
5. Redeploy if necessary

---

## Lessons Learned (Updated from Sessions)

### Session: 2025-10-02 - Clinical Trials Bug & Deployment Strategy

**What Went Wrong:**
1. Deployed to production at 6 AM without testing in development first
2. Clinical trials API had parameter mismatch (status parameter not supported)
3. Multiple deployments triggered confusion (railway up + git push)
4. Translation updates didn't show immediately (deployment delay)

**What We Learned:**
1. ✅ **Always deploy to development first**, especially during early morning sessions
2. ✅ **Verify API parameter compatibility** between frontend and backend
3. ✅ **Use one deployment method at a time** - prefer git push for production
4. ✅ **Wait for deployment completion** before verifying (2-3 minutes typical)
5. ✅ **Test critical user paths** after deployment (disease search, clinical trials, etc.)

**Best Practices Established:**
- Production deployments only during business hours (8 AM - 6 PM)
- Development environment for all morning work sessions
- Test in development → Verify → Deploy to production (during business hours)
- Monitor Railway webhook notifications for deployment status
- Verify translation files are rebuilt before deploying frontend changes

---

## Quick Reference: Railway Commands

```bash
# Check current environment
railway status

# Switch to development
railway environment development

# Switch to production
railway environment production

# Deploy to current environment
railway up --detach

# Deploy to specific environment
railway up --detach --environment development
railway up --detach --environment production

# View logs
railway logs
railway logs --environment development

# Check deployment status
railway deployments

# View environment variables
railway variables

# Get public URL
railway domain
```

---

**Last Updated:** 2025-10-02
**Current Production Version:** 2.3.0
**Current Development Version:** 2.4.0-dev (when created)
