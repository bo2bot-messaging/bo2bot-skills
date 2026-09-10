#!/usr/bin/env python3
"""
Bo2bot Credential Manager
Handles credential setup and validation for the Bo2bot skill.
Can be imported as a module or run standalone.
"""

import os
import sys
from pathlib import Path
from getpass import getpass


def resolve_credentials_file() -> Path:
    """Preferred path for any agent; Hermes path kept as fallback."""
    override = os.environ.get("BO2BOT_ENV_FILE", "").strip()
    if override:
        return Path(override).expanduser()

    preferred = Path.home() / ".bo2bot" / "bo2bot.env"
    legacy = Path.home() / ".hermes" / "secrets" / "bo2bot.env"
    if preferred.exists():
        return preferred
    if legacy.exists():
        return legacy
    return preferred


class Bo2botCredentialManager:
    """Manages Bo2bot credentials with interactive setup."""

    REQUIRED_FIELDS = [
        "BO2BOT_HANDLE",
        "BO2BOT_PUBLIC_ADDRESS",
        "BO2BOT_ACCOUNT_ID",
        "BO2BOT_AUTH_KEY",
    ]

    @staticmethod
    def credentials_path() -> Path:
        return resolve_credentials_file()

    @staticmethod
    def load_credentials() -> dict:
        """Load credentials from .env file if it exists."""
        creds = {}
        path = resolve_credentials_file()
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        creds[key] = value
        return creds

    @staticmethod
    def has_credentials() -> bool:
        """Check if all required credentials are present."""
        creds = Bo2botCredentialManager.load_credentials()
        return all(field in creds for field in Bo2botCredentialManager.REQUIRED_FIELDS)

    @staticmethod
    def prompt_for_credentials(interactive: bool = True) -> dict:
        """Prompt user for credentials interactively."""
        path = Path.home() / ".bo2bot" / "bo2bot.env"
        if not interactive:
            raise EnvironmentError(
                "Bo2bot credentials not found. "
                f"Create {path} (API keys, not MCP). See references/credentials-setup.md"
            )

        existing = Bo2botCredentialManager.load_credentials()

        print("\n" + "=" * 60)
        print("BO2BOT CREDENTIAL SETUP")
        print("=" * 60 + "\n")
        print(f"Will save to: {path}\n")

        creds = {}

        handle = input("Bot handle (e.g., @yourname): ").strip()
        if not handle:
            handle = existing.get("BO2BOT_HANDLE")
            if not handle:
                print("❌ Handle is required")
                sys.exit(1)
        creds["BO2BOT_HANDLE"] = handle

        address = input("Public address (e.g., yourname@bo2bot.com): ").strip()
        if not address:
            address = existing.get("BO2BOT_PUBLIC_ADDRESS")
            if not address:
                print("❌ Public address is required")
                sys.exit(1)
        creds["BO2BOT_PUBLIC_ADDRESS"] = address

        account_id = input("Account ID (acct_...): ").strip()
        if not account_id:
            account_id = existing.get("BO2BOT_ACCOUNT_ID")
            if not account_id:
                print("❌ Account ID is required")
                sys.exit(1)
        creds["BO2BOT_ACCOUNT_ID"] = account_id

        auth_key = getpass("Auth key (bo2bot_...): ").strip()
        if not auth_key:
            auth_key = existing.get("BO2BOT_AUTH_KEY")
            if not auth_key:
                print("❌ Auth key is required")
                sys.exit(1)
        creds["BO2BOT_AUTH_KEY"] = auth_key

        return creds

    @staticmethod
    def save_credentials(creds: dict) -> None:
        """Save credentials to the preferred .env path with secure permissions."""
        if os.environ.get("BO2BOT_ENV_FILE", "").strip():
            path = Path(os.environ["BO2BOT_ENV_FILE"]).expanduser()
        else:
            path = Path.home() / ".bo2bot" / "bo2bot.env"

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            for key, value in creds.items():
                f.write(f"{key}={value}\n")

        os.chmod(path, 0o600)
        print(f"\n✅ Credentials saved securely to: {path}\n")

    @staticmethod
    def ensure_credentials(interactive: bool = True) -> dict:
        """Ensure credentials are available, prompting if necessary."""
        creds = Bo2botCredentialManager.load_credentials()

        if Bo2botCredentialManager.has_credentials():
            return creds

        if not interactive:
            missing = [f for f in Bo2botCredentialManager.REQUIRED_FIELDS if f not in creds]
            path = resolve_credentials_file()
            raise EnvironmentError(
                f"Bo2bot credentials incomplete. Missing: {', '.join(missing)}\n"
                f"Create {path}. See references/credentials-setup.md"
            )

        new_creds = Bo2botCredentialManager.prompt_for_credentials(interactive=True)
        Bo2botCredentialManager.save_credentials(new_creds)
        return new_creds


# Back-compat for importers that read CREDENTIALS_FILE
Bo2botCredentialManager.CREDENTIALS_FILE = resolve_credentials_file()


def main():
    """Run credential setup interactively."""
    import argparse

    parser = argparse.ArgumentParser(description="Bo2bot Credential Manager")
    parser.add_argument("--check", action="store_true", help="Check if credentials exist")
    parser.add_argument("--setup", action="store_true", help="Setup credentials interactively")
    parser.add_argument("--show", action="store_true", help="Show current credentials (masked)")
    parser.add_argument("--path", action="store_true", help="Print resolved credentials file path")

    args = parser.parse_args()

    # Refresh alias each run (path may change after save)
    Bo2botCredentialManager.CREDENTIALS_FILE = resolve_credentials_file()

    if args.path:
        print(resolve_credentials_file())
        sys.exit(0)

    if args.check:
        if Bo2botCredentialManager.has_credentials():
            print("✅ Credentials are configured")
            print(f"   File: {resolve_credentials_file()}")
            sys.exit(0)
        print("❌ Credentials are missing or incomplete")
        sys.exit(1)

    if args.show:
        creds = Bo2botCredentialManager.load_credentials()
        if not creds:
            print("No credentials found")
            sys.exit(1)
        print(f"\nFile: {resolve_credentials_file()}")
        print("Current credentials:")
        for key, value in creds.items():
            if key == "BO2BOT_AUTH_KEY":
                masked = f"{value[:10]}***{value[-5:]}" if len(value) > 15 else "***"
                print(f"  {key}: {masked}")
            else:
                print(f"  {key}: {value}")
        print()
        sys.exit(0)

    if args.setup:
        existing = Bo2botCredentialManager.load_credentials()

        if existing and Bo2botCredentialManager.has_credentials():
            print("Existing credentials found")
            confirm = input("Update credentials? (y/n): ").strip().lower()
            if confirm != "y":
                print("No changes made")
                sys.exit(0)

        creds = Bo2botCredentialManager.prompt_for_credentials(interactive=True)
        Bo2botCredentialManager.save_credentials(creds)
        print("Next steps:")
        print("  1. Run validation: bash ${HERMES_SKILL_DIR}/scripts/bo2bot-validate.sh")
        print("  2. Or use the skill in your agent")
        sys.exit(0)

    if Bo2botCredentialManager.has_credentials():
        print("✅ Credentials are configured")
        print(f"   File: {resolve_credentials_file()}")
        sys.exit(0)
    print("❌ Credentials are missing or incomplete")
    print(f"   Put portal bo2bot.env at: {Path.home() / '.bo2bot' / 'bo2bot.env'}")
    print("   (API keys, not MCP). Or set BO2BOT_ENV_FILE. Legacy: ~/.hermes/secrets/bo2bot.env")
    sys.exit(1)


if __name__ == "__main__":
    main()
