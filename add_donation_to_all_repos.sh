#!/bin/bash
# Script to add donation button to all GitHub repos

STRIPE_LINK="https://link.elearningevolve.com/self-pay"

echo "=== Adding Donation Button to All GitHub Repos ==="
echo ""
echo "This script will:"
echo "  1. Create .github/FUNDING.yml in each repo"
echo "  2. Add donation section to README.md"
echo ""
read -p "Enter path to directory containing your GitHub repos: " REPOS_DIR

if [ ! -d "$REPOS_DIR" ]; then
    echo "Error: Directory not found: $REPOS_DIR"
    exit 1
fi

# Donation section for README
DONATION_SECTION='
---

<h2 align="center">💝 Support This Project</h2>

<p align="center">
<strong>If you find this project helpful, please consider supporting it:</strong>
</p>

<p align="center">
<a href="'$STRIPE_LINK'" target="_blank">
<img src="https://img.shields.io/badge/Support%20via%20Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white" alt="Support via Stripe" height="50" width="300">
</a>
</p>

<p align="center">
<a href="'$STRIPE_LINK'" target="_blank">
<strong>👉 Click here to support via Stripe 👈</strong>
</a>
</p>

---
'

count=0
EXCLUDE_REPOS=("movie_cleaner")  # Repos to skip (already have donation button)

for repo in "$REPOS_DIR"/*/; do
    if [ -d "$repo/.git" ]; then
        repo_name=$(basename "$repo")
        
        # Skip excluded repos
        skip_repo=0
        for exclude in "${EXCLUDE_REPOS[@]}"; do
            if [ "$repo_name" = "$exclude" ]; then
                skip_repo=1
                break
            fi
        done
        
        if [ $skip_repo -eq 1 ]; then
            echo ""
            echo "Skipping: $repo_name (already has donation button)"
            continue
        fi
        
        echo ""
        echo "Processing: $repo_name"
        
        # Create .github directory and FUNDING.yml
        mkdir -p "$repo/.github"
        echo "custom: ['$STRIPE_LINK']" > "$repo/.github/FUNDING.yml"
        echo "  ✓ Created .github/FUNDING.yml"
        
        # Add to README if it exists
        if [ -f "$repo/README.md" ]; then
            # Check if donation section already exists
            if ! grep -q "Support This Project" "$repo/README.md"; then
                # Add after first --- separator or after title
                python3 << PYTHON
with open("$repo/README.md", "r") as f:
    lines = f.readlines()

# Find insertion point (after intro, before TOC or first section)
insert_idx = 50  # Default: after intro
for i, line in enumerate(lines[:100]):
    if line.strip() == "---" and i > 20:
        insert_idx = i + 1
        break
    if line.startswith("##") and i > 10:
        insert_idx = i
        break

# Insert donation section
donation_lines = """$DONATION_SECTION""".split("\n")
new_lines = lines[:insert_idx] + donation_lines + lines[insert_idx:]

with open("$repo/README.md", "w") as f:
    f.writelines(new_lines)
PYTHON
                echo "  ✓ Added donation section to README.md"
            else
                echo "  ⚠ Donation section already exists in README.md"
            fi
        else
            echo "  ⚠ No README.md found - skipping README update"
        fi
        
        count=$((count + 1))
    fi
done

echo ""
echo "=== Complete ==="
echo "Processed $count repositories"
echo ""
echo "Next steps:"
echo "  1. Review changes in each repo"
echo "  2. Commit and push:"
echo "     cd <repo>"
echo "     git add .github/FUNDING.yml README.md"
echo "     git commit -m 'Add donation button'"
echo "     git push"
