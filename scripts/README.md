sync_env_to_vercel.sh - Usage

This script reads a local env file (default `.env.vercel`) and interactively adds each non-empty VAR=VALUE pair to your Vercel project using the `vercel` CLI.

Requirements:
- `vercel` CLI installed and authenticated (run `vercel login`)
- You have permissions to modify the project's environment variables

Basic usage:

```bash
# Preview environment (default)
./scripts/sync_env_to_vercel.sh .env.vercel preview

# Production environment
./scripts/sync_env_to_vercel.sh .env.production production
```

The script will prompt before adding/updating each variable. Sensitive values are passed over stdin to the `vercel env add` command; they are not echoed or stored by the script.
