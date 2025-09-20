# Quick Deployment Checklist

## Pre-deployment

- [ ] Fork this repository to your GitHub account
- [ ] Get an OpenAI API key from https://platform.openai.com/api-keys
- [ ] Create a Vercel account at https://vercel.com

## Vercel Deployment

1. **Import Project**
   - Go to Vercel Dashboard
   - Click "New Project"
   - Import from GitHub (select this repo)

2. **Configure Environment Variables**
   ```
   API_BEARER=your-chosen-api-key
   OPENAI_API_KEY=your-openai-api-key-here
   CORS_ORIGINS=https://your-project.vercel.app
   JWT_SECRET_KEY=a-very-secure-random-string-here
   ```

3. **Deploy**
   - Click "Deploy"
   - Wait for build to complete

4. **Test**
   - Visit https://your-project.vercel.app/health
   - Visit https://your-project.vercel.app/docs for API documentation

## Post-deployment

- [ ] Test all endpoints work
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring/logging
- [ ] Configure production database if needed

## Troubleshooting

If deployment fails:
1. Check Vercel build logs
2. Verify environment variables are set
3. Check that all required files are present in repo
4. Ensure Python dependencies are compatible

For issues, check the DEPLOYMENT.md file for detailed troubleshooting.