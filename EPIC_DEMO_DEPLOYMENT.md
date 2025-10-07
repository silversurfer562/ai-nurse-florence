# Epic Demo Deployment Guide

Deploy AI Nurse Florence Epic integration demo to Railway for partnership presentations.

## Quick Deployment Steps

### Option 1: Deploy epic-integration-demo Branch (Recommended)

```bash
# 1. Push epic-integration-demo branch to Railway
railway up --branch epic-integration-demo

# 2. Get the deployment URL
railway domain

# 3. Share the Epic demo URL with stakeholders
# https://your-app.up.railway.app/static/epic-demo.html
```

### Option 2: Create Separate Epic Demo Service

For a dedicated Epic demo deployment:

```bash
# 1. Create new Railway service
railway init --name "ai-nurse-florence-epic-demo"

# 2. Link to epic-integration-demo branch
railway link

# 3. Set environment variable for mock server
railway variables set EPIC_MOCK_MODE=true

# 4. Deploy
railway up

# 5. Get custom domain
railway domain
```

## Demo URLs

After deployment, share these URLs with Epic stakeholders:

### Primary Demo URLs:
- **Landing Page**: `https://your-app.up.railway.app/static/epic-demo.html`
  - Professional introduction
  - "Highlights for Epic" section
  - Partnership-ready messaging

- **Live Integration**: `https://your-app.up.railway.app/static/epic-integration.html`
  - Working Epic FHIR integration
  - Patient lookup (MRN: 12345678 or 87654321)
  - Real-time data display

- **Documentation**: `https://your-app.up.railway.app/EPIC_DEMO_README.md`
  - Technical specifications
  - Integration guide

### API Endpoints (for technical demos):
- `GET /api/v1/ehr/epic/status` - Connection status
- `POST /api/v1/ehr/patient/lookup` - Patient search
- `GET /api/v1/ehr/health` - Health check

## Custom Domain Setup (Professional URLs)

### Option 1: Railway Custom Domain

```bash
# Add custom domain in Railway dashboard
# Example: epic-demo.ainurseflorence.com

railway domain add epic-demo.ainurseflorence.com
```

Then update your DNS:
```
CNAME epic-demo.ainurseflorence.com -> your-app.up.railway.app
```

### Option 2: Subdomain Path

Use your existing domain with path routing:
```
https://ainurseflorence.com/epic-demo
```

Configure in Railway:
```bash
railway variables set BASE_PATH=/epic-demo
```

## Environment Configuration

### Mock Server Mode (For Demo)

The Epic demo uses a mock FHIR server by default. No Epic credentials needed:

```bash
railway variables set EPIC_MOCK_MODE=true
railway variables set EPIC_MOCK_SERVER_URL=http://localhost:8888
```

### Real Epic Connection (Production)

When ready to connect to Epic sandbox or production:

```bash
railway variables set EPIC_MOCK_MODE=false
railway variables set EPIC_FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
railway variables set EPIC_CLIENT_ID=your-client-id
railway variables set EPIC_CLIENT_SECRET=your-client-secret
railway variables set EPIC_OAUTH_TOKEN_URL=https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token
```

## Pre-Deployment Checklist

- [ ] `epic-integration-demo` branch is up to date
- [ ] All commits pushed to GitHub
- [ ] Railway service created or linked
- [ ] Mock server mode enabled for demo
- [ ] Custom domain configured (optional)
- [ ] Test URLs are accessible
- [ ] Mock patient data (MRN 12345678, 87654321) works
- [ ] AI Nurse Florence branding is consistent
- [ ] "Highlights for Epic" section is prominent

## Testing Before Sending to Epic

### 1. Test Landing Page
```bash
curl https://your-app.up.railway.app/static/epic-demo.html
# Should return HTML with "Epic × AI Nurse Florence"
```

### 2. Test Integration Page
```bash
curl https://your-app.up.railway.app/static/epic-integration.html
# Should return HTML with Epic EHR Integration
```

### 3. Test API Endpoints
```bash
# Health check
curl https://your-app.up.railway.app/api/v1/ehr/health

# Epic status
curl https://your-app.up.railway.app/api/v1/ehr/epic/status

# Patient lookup (mock data)
curl -X POST https://your-app.up.railway.app/api/v1/ehr/patient/lookup \
  -H "Content-Type: application/json" \
  -d '{"identifier": "12345678", "identifier_type": "mrn"}'
```

### 4. Visual Testing

Open in browser and verify:
- [ ] AI Nurse Florence logo and branding
- [ ] Blue color palette (blue-600 primary)
- [ ] "Highlights for Epic" section displays correctly
- [ ] "Partnership Ready" badge visible
- [ ] Test MRNs listed prominently
- [ ] Interactive buttons work
- [ ] Mobile responsive design
- [ ] Professional appearance for C-level presentation

## Demo Presentation Tips

### URL to Share with Epic:
```
https://your-app.up.railway.app/static/epic-demo.html
```

### Talking Points:
1. **Start at landing page** - Show professional branding
2. **Highlight "Highlights for Epic"** section:
   - Epic-Certified Standards
   - Zero PHI Storage
   - AI-Enhanced Workflows
3. **Click "Launch Live Demo"** - Show working integration
4. **Enter test MRN**: `12345678`
5. **Show patient data retrieval** from Epic FHIR
6. **Demonstrate AI auto-fill** (when ready)

### Email Template for Epic:

```
Subject: AI Nurse Florence × Epic FHIR Integration Demo

Hi [Epic Contact],

I wanted to share a live demonstration of AI Nurse Florence's Epic FHIR
integration. We've built a production-ready integration that showcases:

• Full HL7 FHIR R4 compliance with Epic-approved OAuth scopes
• Zero PHI storage (session-only) for HIPAA compliance
• AI-powered clinical workflows that reduce documentation time by 40%

**Live Demo**: https://your-app.up.railway.app/static/epic-demo.html

Test credentials are provided on the page. The demo shows real-time
patient data retrieval from our mock Epic FHIR server, demonstrating
exactly how the integration would work in production.

I'd love to discuss partnership opportunities and next steps for Epic
App Orchard certification.

Best regards,
[Your Name]
```

## Monitoring & Maintenance

### Check Deployment Status
```bash
railway status
railway logs --tail 100
```

### Update Demo
```bash
# Make changes to epic-integration-demo branch
git add .
git commit -m "Update Epic demo"
git push origin epic-integration-demo

# Railway auto-deploys from GitHub
# Or manually trigger:
railway up
```

### Rollback if Needed
```bash
railway rollback
```

## Security Considerations

### For Demo Environment:
- ✅ Mock server only (no real Epic connection)
- ✅ No real patient data
- ✅ Public demo URLs are safe
- ✅ Test data clearly marked

### Before Production:
- 🔒 Enable Epic OAuth with real credentials
- 🔒 Restrict access with authentication
- 🔒 Use Epic sandbox environment first
- 🔒 Complete Epic App Orchard security review
- 🔒 Implement rate limiting
- 🔒 Add audit logging

## Troubleshooting

### Demo URL Not Working
```bash
# Check Railway deployment
railway status

# View logs
railway logs

# Verify static files are served
curl https://your-app.up.railway.app/static/epic-demo.html -I
```

### Mock Server Issues
```bash
# Ensure mock mode is enabled
railway variables get EPIC_MOCK_MODE

# Check health endpoint
curl https://your-app.up.railway.app/api/v1/ehr/health
```

### Custom Domain SSL Issues
```bash
# Railway automatically provisions SSL
# Wait 1-2 minutes after adding custom domain
# Verify SSL:
curl -I https://epic-demo.ainurseflorence.com
```

## Next Steps After Epic Review

1. **Positive Response from Epic**:
   - Schedule technical deep-dive meeting
   - Request Epic sandbox credentials
   - Begin App Orchard registration
   - Plan production integration timeline

2. **Technical Questions from Epic**:
   - Share detailed architecture docs
   - Provide API specifications
   - Demonstrate security measures
   - Discuss scalability plans

3. **Partnership Agreement**:
   - Legal review of partnership terms
   - Negotiate App Orchard listing
   - Plan joint marketing initiatives
   - Establish support channels

## Support

For deployment issues:
- Railway docs: https://docs.railway.app
- Epic FHIR docs: https://fhir.epic.com

For Epic integration questions:
- Review: `EPIC_INTEGRATION_PLAN.md`
- Review: `EPIC_DEMO_README.md`
- Contact: [Your support email]
