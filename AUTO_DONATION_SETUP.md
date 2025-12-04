# Automatic Donation Button Setup for Future Repos

## Quick Setup (Choose One Method)

### Method 1: Git Template (Recommended - Automatic)

Run this once:
```bash
bash ~/.git_template_setup.sh
```

**How it works:**
- Creates a git template directory
- Every new `git init` or `git clone` automatically includes donation button
- Works automatically - no manual steps needed!

### Method 2: Manual Script (Run After Each New Repo)

After creating a new repo:
```bash
cd /path/to/new/repo
~/.setup_new_repo.sh
```

Or use the alias:
```bash
newrepo
```

### Method 3: Add to Shell Profile (Semi-Automatic)

Add to `~/.bashrc` or `~/.zshrc`:
```bash
source ~/.bashrc_donation_setup
```

Then after each `git init` or `git clone`, run:
```bash
newrepo
```

## What Gets Added

1. **`.github/FUNDING.yml`** - May create GitHub sponsor button
2. **README.md donation section** - Large, visible button (always works)

## Files Created

- `~/.git_template_setup.sh` - One-time setup script
- `~/.setup_new_repo.sh` - Script to run for each new repo
- `~/.bashrc_donation_setup` - Shell integration (optional)

## Recommended Approach

**Use Method 1 (Git Template)** - It's the most automatic!

Just run `bash ~/.git_template_setup.sh` once, and all future repos
will automatically have the donation button setup!
