# Quick Transfer Steps - Repository Owner Guide

This is a condensed, actionable checklist for the repository owner to execute the transfer to Deep Study AI organization.

## Prerequisites (Do First)

### 1. Create Deep Study AI GitHub Organization
- Go to: https://github.com/organizations/new
- Choose a name: `DeepStudyAI`, `deep-study-ai`, or `deepstudyai`
- Set email: patrickroebuck@pm.me
- Choose plan: Free (upgrade later if needed)
- Complete organization profile

### 2. Backup Critical Data
```bash
# Clone repository locally
git clone https://github.com/silversurfer562/ai-nurse-florence
cd ai-nurse-florence

# Export GitHub secrets (manual: note them down from Settings → Secrets)
# List current secrets:
# - OPENAI_API_KEY
# - NCBI_API_KEY (if set)
# - RAILWAY_TOKEN (if set)
# - Any deployment secrets

# Save deployment URLs:
# - Railway deployment URL
# - Webhook URLs
# - OAuth callback URLs
```

## Transfer Execution (Quick Steps)

### Step 1: Transfer Repository
1. Go to: https://github.com/silversurfer562/ai-nurse-florence/settings
2. Scroll to "Danger Zone"
3. Click **"Transfer"**
4. Enter new owner: `DeepStudyAI` (or your chosen org name)
5. Type repository name: `ai-nurse-florence`
6. Click **"I understand, transfer this repository"**
7. ✅ Wait for transfer confirmation

### Step 2: Immediate Post-Transfer Actions
1. **Reconfigure GitHub Actions Secrets**:
   - Go to: https://github.com/DeepStudyAI/ai-nurse-florence/settings/secrets/actions
   - Add back all secrets:
     - `OPENAI_API_KEY`
     - `NCBI_API_KEY`
     - Other deployment secrets

2. **Verify Repository Settings**:
   - Check: https://github.com/DeepStudyAI/ai-nurse-florence/settings
   - Confirm: Public visibility
   - Verify: Branch protection on `main` (if desired)

3. **Test GitHub Actions**:
   - Go to: Actions tab
   - Trigger a workflow (or wait for next push)
   - Verify: Workflows run successfully

### Step 3: Reconnect External Services

#### Railway Deployment
1. Log in to Railway: https://railway.app
2. Select your project
3. Go to Settings → Connect Repository
4. Reconnect to: `DeepStudyAI/ai-nurse-florence`
5. Redeploy to verify

#### Update Webhooks (if any)
1. Check: https://github.com/DeepStudyAI/ai-nurse-florence/settings/hooks
2. Update any webhook URLs that reference the old repository

### Step 4: Update Documentation
Run these commands in your local repository:

```bash
cd ai-nurse-florence

# Update git remote
git remote set-url origin https://github.com/DeepStudyAI/ai-nurse-florence.git

# Pull any changes made during transfer
git pull origin main

# Remove transition notices (optional - can keep for transparency)
# Edit README.md to remove the transition notice at the top if desired

git add .
git commit -m "docs: complete repository transfer to Deep Study AI organization"
git push origin main
```

### Step 5: Verification Checklist
- [ ] Repository accessible at: https://github.com/DeepStudyAI/ai-nurse-florence
- [ ] Old URL redirects properly
- [ ] GitHub Actions working (check latest run)
- [ ] Railway deployment operational
- [ ] Health endpoint responding: https://[your-deployment]/api/v1/health
- [ ] All secrets configured
- [ ] Documentation updated

## If Something Goes Wrong

### Rollback Option
- Contact GitHub Support within 30 days to reverse the transfer
- Keep local backup until stable

### Common Issues

**Issue**: GitHub Actions failing  
**Fix**: Check that all secrets are reconfigured

**Issue**: Railway deployment broken  
**Fix**: Reconnect repository in Railway settings

**Issue**: Webhooks not working  
**Fix**: Update webhook URLs in external services

## Post-Transfer (Optional)

### Clean Up Transition Notices
Once transfer is stable, you can optionally remove or update the transition notices in:
- `README.md` (line 3-4)
- `CONTRIBUTING.md` (lines 6-7)

Or keep them for transparency about the project's evolution.

### Update External References
- Social media links
- Website links
- Documentation on other platforms
- Email signatures

## Quick Command Reference

```bash
# Update local git remote after transfer
git remote set-url origin https://github.com/DeepStudyAI/ai-nurse-florence.git

# Verify remote
git remote -v

# Pull from new location
git pull origin main

# Clone from new location
git clone https://github.com/DeepStudyAI/ai-nurse-florence
```

## Timeline Estimate
- **Prep**: 30 minutes (create org, backup data)
- **Transfer**: 5 minutes (actual transfer)
- **Post-transfer**: 1-2 hours (reconnect services, verify)
- **Total**: 2-3 hours for complete transition

## Support
Questions? Issues?
- Email: patrickroebuck@pm.me
- Create issue: https://github.com/DeepStudyAI/ai-nurse-florence/issues

---

**See Also**:
- [TRANSFER_GUIDE.md](./TRANSFER_GUIDE.md) - Detailed comprehensive guide
- [ORGANIZATIONAL_TRANSITION.md](./ORGANIZATIONAL_TRANSITION.md) - Full transition plan
- [NOTICE.md](./NOTICE.md) - Public benefit mission

*Last Updated: October 16, 2025*
