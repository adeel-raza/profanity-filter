#!/usr/bin/env python3
"""
Simple script to login to Hugging Face
"""

import sys
from huggingface_hub import login

print("=" * 60)
print("Hugging Face Login")
print("=" * 60)
print()
print("You need a Hugging Face token.")
print("Get one at: https://huggingface.co/settings/tokens")
print()
print("1. Go to: https://huggingface.co/settings/tokens")
print("2. Click 'New token'")
print("3. Name it (e.g., 'deploy-token')")
print("4. Select 'Write' permissions")
print("5. Copy the token")
print()

# Check if token provided as argument
if len(sys.argv) > 1:
    token = sys.argv[1]
    print("Using token from command line...")
    try:
        login(token=token)
        print()
        print("✓ Login successful!")
        print()
        print("You can now run:")
        print("  python3 auto_deploy.py")
        print()
        sys.exit(0)
    except Exception as e:
        print()
        print(f"✗ Login failed: {e}")
        print()
        sys.exit(1)

# Interactive login
print("Then paste it below (or press Ctrl+C to cancel):")
print()

try:
    login()
    print()
    print("✓ Login successful!")
    print()
    print("You can now run:")
    print("  python3 auto_deploy.py")
    print()
except KeyboardInterrupt:
    print()
    print("\nLogin cancelled.")
    sys.exit(0)
except Exception as e:
    print()
    print(f"✗ Login failed: {e}")
    print()
    print("Alternative: Use token directly:")
    print("  python3 login_hf.py YOUR_TOKEN_HERE")
    print()
    print("Or use CLI command:")
    print("  hf auth login")
    print()
    sys.exit(1)

