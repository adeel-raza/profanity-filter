# Connect Hugging Face Space to GitHub

This guide will help you connect your Hugging Face Space to your GitHub repository for automatic updates.

## Method 1: Connect via Hugging Face Web Interface (Easiest)

### Step 1: Go to Your Space Settings

1. Go to your Space: `https://huggingface.co/spaces/YOUR_USERNAME/video-profanity-filter`
2. Click on the **"Files and versions"** tab (or **"Settings"** tab)
3. Look for **"Repository"** or **"GitHub"** section

### Step 2: Connect to GitHub

1. In the Space settings, find **"Repository"** or **"Connect to GitHub"** option
2. Click **"Connect to GitHub"** or **"Link GitHub repository"**
3. You'll be asked to authorize Hugging Face to access your GitHub
4. Select your repository: `adeel-raza/profanity-filter`
5. Select branch: `main`
6. Set root directory: `/` (root of repository)
7. Click **"Connect"** or **"Save"**

### Step 3: Verify Connection

- After connecting, Hugging Face will automatically pull from GitHub
- Any push to the `main` branch will trigger a rebuild
- Check the **"Logs"** tab to see the build progress

## Method 2: Manual Git Setup (Advanced)

If you prefer to use Git directly:

### Step 1: Clone Your Space

```bash
# Install Git LFS (Large File Storage) if not already installed
# On Ubuntu/Debian: sudo apt install git-lfs
# On macOS: brew install git-lfs

# Initialize Git LFS
git lfs install

# Clone your Space (replace YOUR_USERNAME)
git clone https://huggingface.co/spaces/YOUR_USERNAME/video-profanity-filter
cd video-profanity-filter
```

### Step 2: Add GitHub as Remote

```bash
# Add your GitHub repo as a remote
git remote add github https://github.com/adeel-raza/profanity-filter.git

# Or if you prefer SSH:
# git remote add github git@github.com:adeel-raza/profanity-filter.git
```

### Step 3: Pull from GitHub and Push to HF

```bash
# Pull latest from GitHub
git pull github main

# Push to Hugging Face
git push origin main
```

## Method 3: Use Hugging Face CLI

```bash
# Make sure you're logged in
hf auth login

# Clone your Space
hf repo clone YOUR_USERNAME/video-profanity-filter --repo-type space

# Add GitHub remote
cd video-profanity-filter
git remote add github https://github.com/adeel-raza/profanity-filter.git

# Pull from GitHub
git pull github main

# Push to Hugging Face
git push origin main
```

## Automatic Updates

Once connected:

1. **Make changes** in your local repository
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. **Hugging Face will automatically**:
   - Detect the push
   - Pull the latest code
   - Rebuild the Space
   - Deploy the updated app

## Troubleshooting

### Space not updating?
- Check the **"Logs"** tab in your Space for errors
- Verify the GitHub connection in Space settings
- Make sure you're pushing to the `main` branch
- Check that root directory is set correctly (`/`)

### Build fails?
- Check that all required files are in the repository
- Verify `requirements.txt` exists (not `requirements_hf.txt`)
- Check that `app.py` is in the root directory
- Review build logs for specific errors

### Connection issues?
- Re-authorize Hugging Face to access GitHub
- Check GitHub repository permissions
- Verify the repository name is correct

## Quick Reference

**Your GitHub Repo:** `https://github.com/adeel-raza/profanity-filter`  
**Your HF Space:** `https://huggingface.co/spaces/YOUR_USERNAME/video-profanity-filter`

**After connecting, any push to GitHub will auto-update your Space!**

