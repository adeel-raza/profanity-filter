# Quick Login Guide

## Method 1: Use CLI (Recommended)

```bash
cd "/home/adeel/Link to html/wp_local/movie_cleaner"
source venv/bin/activate
hf auth login
```

Then paste your token when prompted.

## Method 2: Use Python Script

```bash
cd "/home/adeel/Link to html/wp_local/movie_cleaner"
source venv/bin/activate
python3 login_hf.py
```

Or with token directly:
```bash
python3 login_hf.py YOUR_TOKEN_HERE
```

## Get Your Token

1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it (e.g., "deploy-token")
4. Select "Write" permissions
5. Copy the token

## After Login

Once logged in, deploy with:
```bash
python3 auto_deploy.py
```
