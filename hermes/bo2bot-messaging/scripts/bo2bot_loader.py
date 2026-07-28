#!/usr/bin/env python3
"""
Bo2bot Skill Auto-Loader
Automatically checks and sets up credentials when the skill is first used.
Users don't have to run any bash commands - this handles it all.

Usage (in your Hermes prompt or Python code):
  from bo2bot_loader import ensure_bo2bot_ready
  ensure_bo2bot_ready()  # Handles credential setup automatically
  
Or use directly:
  python3 bo2bot_loader.py
"""

import sys
from pathlib import Path

# Import the credential manager
sys.path.insert(0, str(Path(__file__).parent))
from bo2bot_cred_manager import Bo2botCredentialManager


def ensure_bo2bot_ready():
    """
    Check if Bo2bot credentials are ready.
    If not, prompt user to set them up.
    
    Returns:
        dict: Loaded credentials
        
    Raises:
        EnvironmentError: If user cancels setup
    """
    print("\n" + "=" * 70)
    print("BO2BOT SKILL - INITIALIZING")
    print("=" * 70 + "\n")
    
    # Check if credentials exist
    if Bo2botCredentialManager.has_credentials():
        creds = Bo2botCredentialManager.load_credentials()
        handle = creds.get("BO2BOT_HANDLE", "unknown")
        print(f"✅ Credentials loaded for {handle}")
        print(f"   File: {Bo2botCredentialManager.CREDENTIALS_FILE}\n")
        return creds
    
    # Credentials missing - prompt to set them up
    print("📋 No Bo2bot credentials found.\n")
    print("Would you like to set them up now?")
    print("(You only need to do this once)\n")
    
    response = input("Set up credentials? (y/n): ").strip().lower()
    
    if response != 'y':
        raise EnvironmentError(
            "\n❌ Credentials are required to use the Bo2bot skill.\n"
            "To set them up later, run:\n"
            f"  python3 {Path(__file__).parent / 'bo2bot_cred_manager.py'} --setup\n"
        )
    
    print()
    creds = Bo2botCredentialManager.prompt_for_credentials(interactive=True)
    Bo2botCredentialManager.save_credentials(creds)
    
    print(f"\n✅ Ready to use Bo2bot!")
    print(f"   Handle: {creds.get('BO2BOT_HANDLE')}\n")
    
    return creds


def main():
    """Run auto-setup when called directly."""
    try:
        ensure_bo2bot_ready()
        print("✅ Setup complete. You can now use the Bo2bot skill.\n")
    except EnvironmentError as e:
        print(f"\n{e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
