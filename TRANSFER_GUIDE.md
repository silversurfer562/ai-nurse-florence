# Repository Transfer Guide - Moving to Deep Study AI Organization

## Overview

This guide documents the process for transferring the AI Nurse Florence repository from the personal GitHub account (`silversurfer562`) to the official Deep Study AI organization account on GitHub.

## Purpose

As outlined in [NOTICE.md](./NOTICE.md), AI Nurse Florence is developed and maintained by Deep Study AI, LLC as a public benefit technology initiative. Transferring the repository to an organizational account will:

1. **Establish Clear Ownership**: Reflect the corporate ownership by Deep Study AI, LLC
2. **Improve Credibility**: Organizational accounts provide better visibility and trust for open-source healthcare projects
3. **Enable Team Collaboration**: Facilitate better access control and team management
4. **Support Long-term Sustainability**: Ensure the project remains accessible even with personnel changes

## Pre-Transfer Checklist

Before initiating the transfer, ensure the following:

- [ ] **Create Deep Study AI GitHub Organization** (if not already exists)
  - Organization name suggestions: `DeepStudyAI`, `deep-study-ai`, or `deepstudyai`
  - Set organization email: patrickroebuck@pm.me (or dedicated organization email)
  - Configure organization profile with Deep Study AI, LLC information

- [ ] **Backup Critical Information**
  - Export GitHub Issues and Pull Requests (if any)
  - Document any GitHub Actions secrets that need to be reconfigured
  - Save deployment webhook URLs (Railway, etc.)

- [ ] **Update External Services**
  - Railway deployment settings
  - CI/CD pipeline configurations
  - Domain name DNS settings (if applicable)
  - OAuth applications and API callbacks

- [ ] **Notify Stakeholders**
  - Inform any external contributors or users about the transfer
  - Update social media links and references
  - Notify healthcare professional users if applicable

## Transfer Process

### Step 1: Create Deep Study AI Organization

1. Go to GitHub and create a new organization
2. Choose organization type: **Free** (or Pro for additional features)
3. Set organization details:
   - **Name**: `DeepStudyAI` (or preferred variant)
   - **Contact email**: patrickroebuck@pm.me
   - **Organization type**: Company
   - **About**: "Deep Study AI, LLC - Advancing healthcare through responsible AI technology"

### Step 2: Initiate Repository Transfer

1. Navigate to repository settings: https://github.com/silversurfer562/ai-nurse-florence/settings
2. Scroll to the "Danger Zone" section
3. Click "Transfer" button
4. Enter the new owner: `DeepStudyAI` (or chosen organization name)
5. Type the repository name to confirm: `ai-nurse-florence`
6. Click "I understand, transfer this repository"

### Step 3: Post-Transfer Configuration

After transfer is complete:

1. **Update Repository Settings**
   - Verify repository visibility (should remain Public)
   - Update repository description if needed
   - Configure branch protection rules for `main` branch
   - Set up team permissions

2. **Reconfigure GitHub Actions**
   - Go to Settings → Secrets and variables → Actions
   - Add required secrets:
     - `OPENAI_API_KEY`
     - `NCBI_API_KEY` (optional)
     - Any deployment-related secrets
   - Verify workflows run successfully

3. **Update Deployment Services**
   - **Railway**: Update GitHub integration to point to new organization
   - **Domain/DNS**: Update any custom domain configurations
   - **Webhooks**: Reconfigure webhook URLs if needed

4. **Update External References**
   - Update links in any external documentation
   - Update GitHub Sponsors settings (if applicable)
   - Update social media and marketing materials

### Step 4: Update Repository Documentation

After transfer, update the following files with new repository URLs:

- [x] `README.md` - Update GitHub Sponsors link
- [x] `CONTRIBUTING.md` - Update repository references
- [x] `NOTICE.md` - Add note about organizational ownership
- [x] Documentation in `docs/` directory
- [x] Any deployment scripts with hardcoded repository URLs

## Post-Transfer Verification

1. **Test Repository Access**
   - Clone from new URL: `git clone https://github.com/DeepStudyAI/ai-nurse-florence`
   - Verify all documentation renders correctly
   - Check that all links work properly

2. **Test CI/CD Pipeline**
   - Trigger a test workflow run
   - Verify builds complete successfully
   - Check that deployments work as expected

3. **Verify External Integrations**
   - Test Railway deployment
   - Verify health check endpoints
   - Confirm API functionality

4. **Update Local Git Remotes**
   - For existing contributors, update remote URL:
     ```bash
     git remote set-url origin https://github.com/DeepStudyAI/ai-nurse-florence
     ```

## Repository URL Changes

| Type | Old URL | New URL |
|------|---------|---------|
| Repository | `https://github.com/silversurfer562/ai-nurse-florence` | `https://github.com/DeepStudyAI/ai-nurse-florence` |
| Clone HTTPS | `https://github.com/silversurfer562/ai-nurse-florence.git` | `https://github.com/DeepStudyAI/ai-nurse-florence.git` |
| Clone SSH | `git@github.com:silversurfer562/ai-nurse-florence.git` | `git@github.com:DeepStudyAI/ai-nurse-florence.git` |

**Note**: GitHub automatically sets up redirects from the old repository URL to the new one, so existing clones will continue to work temporarily. However, it's best practice to update remote URLs.

## Rollback Plan

If issues arise during transfer:

1. The original owner can request the repository back from GitHub Support
2. External services can be pointed back to the old URL if needed
3. Keep a backup of the repository locally until transfer is stable

## Important Notes

- **GitHub automatically sets up redirects**: Old repository URLs will redirect to the new location
- **Stars and forks are preserved**: All social proof remains intact
- **Issues and PRs are preserved**: Complete history is maintained
- **GitHub Actions history is preserved**: But secrets must be reconfigured
- **Deploy keys and webhooks**: Will need to be reconfigured manually

## Support and Questions

For questions about this transfer process:

- **Email**: patrickroebuck@pm.me
- **GitHub Issues**: Create an issue in this repository before transfer
- **Organization Contact**: Deep Study AI, LLC

## Timeline

Recommended transfer timeline:

1. **Week 1**: Create organization, backup data, notify stakeholders
2. **Week 2**: Perform transfer, update configurations
3. **Week 3**: Verify all systems, update documentation
4. **Week 4**: Monitor for issues, complete final updates

---

*This guide is part of the transition to organizational ownership for the AI Nurse Florence project by Deep Study AI, LLC.*

*Last Updated: October 16, 2025*
