# How to Add Donation Button to All GitHub Repos

## Quick Method: Copy These Files

### 1. Create `.github/FUNDING.yml` in each repo:

**File:** `.github/FUNDING.yml`

**Content:**
```yaml
custom: ['https://link.elearningevolve.com/self-pay']
```

### 2. Add to README.md in each repo:

Add this section (preferably near the top, after intro):

```markdown
---

<h2 align="center">💝 Support This Project</h2>

<p align="center">
<strong>If you find this project helpful, please consider supporting it:</strong>
</p>

<p align="center">
<a href="https://link.elearningevolve.com/self-pay" target="_blank">
<img src="https://img.shields.io/badge/Support%20via%20Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white" alt="Support via Stripe" height="50" width="300">
</a>
</p>

<p align="center">
<a href="https://link.elearningevolve.com/self-pay" target="_blank">
<strong>👉 Click here to support via Stripe 👈</strong>
</a>
</p>

---
```

## Automated Method: Use the Script

Run this script to add to all repos at once:

```bash
bash /tmp/add_donation_to_all_repos.sh
```

Or manually for each repo:

```bash
# In each repo directory:
mkdir -p .github
echo "custom: ['https://link.elearningevolve.com/self-pay']" > .github/FUNDING.yml

# Add to README.md (copy the section above)
# Then commit and push:
git add .github/FUNDING.yml README.md
git commit -m "Add donation button"
git push
```

## Via GitHub Web Interface

### For FUNDING.yml:
1. Go to repo on GitHub
2. Click "Add file" → "Create new file"
3. Name: `.github/FUNDING.yml`
4. Paste: `custom: ['https://link.elearningevolve.com/self-pay']`
5. Commit

### For README:
1. Go to README.md
2. Click "Edit" (pencil icon)
3. Add the donation section (copy from above)
4. Commit

That's it! Repeat for each repo.
