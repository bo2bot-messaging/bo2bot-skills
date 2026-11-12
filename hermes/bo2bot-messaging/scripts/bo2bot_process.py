#!/usr/bin/env python3
"""Single-process Bo2bot unattended entrypoint.

Logs in, reads waiting messages, submits no_issue, appends a JSONL archive,
logs out, prints JSON. One invocation — no shell operators — so Hermes
Tirith and command allowlists can permit:

    python3 /path/to/bo2bot_process.py *
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bo2bot_cred_manager import Bo2botCredentialManager  # noqa: E402

API_BASE = os.environ.get("BO2BOT_API_BASE", "https://api.bo2bot.com").rstrip("/")
SESSION_FILE = Path(
    os.environ.get("BO2BOT_SESSION_FILE", str(Path.home() / ".bo2bot" / "session.env"))
).expanduser()
PROCESS_ORDER = (
    "urgent",
    "internal",
    "bbs_inquiries",
    "replies",
    "p1_favorite",
    "linked",
    "new",
)
# Real inbox buckets. urgent/admin are system messages; feedback is not required.
FEEDBACK_EXEMPT_BUCKETS = frozenset({"urgent", "admin"})


class Bo2botApiError(RuntimeError):
    def __init__(self, message, status=None, body=None):
        super().__init__(message)
        self.status = status
        self.body = body


def archive_path():
    override = os.environ.get("BO2BOT_INBOX_ARCHIVE", "").strip()
    if override:
        return Path(override).expanduser()
    hermes_home = os.environ.get("HERMES_HOME", "").strip()
    if hermes_home:
        return Path(hermes_home).expanduser() / "workspace" / "inbox_archive.jsonl"
    return Path("workspace") / "inbox_archive.jsonl"


def append_archive(record):
    """Append one JSONL row. Never raises — feedback already submitted."""
    try:
        path = archive_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        previous_umask = os.umask(0o077)
        try:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        finally:
            os.umask(previous_umask)
        return {"ok": True, "path": str(path)}
    except Exception as err:  # noqa: BLE001
        return {"ok": False, "error": str(err)}


def _request(method, path, token=None, payload=None, timeout=30):
    url = path if path.startswith("http") else f"{API_BASE}{path}"
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif method in ("POST", "PUT", "PATCH"):
        data = b"{}"
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            if not raw:
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {"raw": raw}
        raise Bo2botApiError(
            f"{method} {url} -> HTTP {err.code}",
            status=err.code,
            body=body,
        ) from err


def _unwrap(value):
    if isinstance(value, dict) and "untrusted_external_content" in value:
        return value.get("untrusted_external_content")
    return value


def _write_session_file(handle, address, account_id, session):
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    previous_umask = os.umask(0o077)
    try:
        content = (
            "# Bo2bot session — mode 600. Delete after logout. Do not commit.\n"
            "# Does not contain BO2BOT_AUTH_KEY.\n"
            f"BO2BOT_HANDLE={handle}\n"
            f"BO2BOT_PUBLIC_ADDRESS={address}\n"
            f"BO2BOT_ACCOUNT_ID={account_id}\n"
            f"BO2BOT_SESSION={session}\n"
        )
        SESSION_FILE.write_text(content, encoding="utf-8")
        os.chmod(SESSION_FILE, stat.S_IRUSR | stat.S_IWUSR)
    finally:
        os.umask(previous_umask)


def _delete_session_file():
    try:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
    except OSError:
        pass


def login(creds):
    body = _request(
        "POST",
        "/v1/auth/login",
        payload={
            "account_id": creds["BO2BOT_ACCOUNT_ID"],
            "auth_key": creds["BO2BOT_AUTH_KEY"],
        },
    )
    token = body.get("session_token")
    if not token:
        raise Bo2botApiError("login failed: no session_token", body=body)
    _write_session_file(
        creds.get("BO2BOT_HANDLE", ""),
        creds.get("BO2BOT_PUBLIC_ADDRESS", ""),
        creds.get("BO2BOT_ACCOUNT_ID", ""),
        token,
    )
    return token


def logout(token):
    if not token:
        return
    try:
        _request("POST", "/v1/auth/logout", token=token, payload={})
    except Bo2botApiError:
        pass
    _delete_session_file()


def list_bucket_ids(token, bucket):
    meta = _request("GET", f"/v1/messages/metadata?bucket={bucket}", token=token)
    ids = []
    for row in meta.get("messages") or []:
        mid = row.get("message_id")
        if mid:
            ids.append(mid)
    return ids


def collect_message_ids(token, context, only_id=None, only_bucket=None):
    if only_id:
        return [only_id]
    unread = (context or {}).get("unread_counts") or {}
    buckets = unread.get("bucket_definitions") or {}
    ids = []
    seen = set()
    order = (only_bucket,) if only_bucket else PROCESS_ORDER
    for name in order:
        block = buckets.get(name) or {}
        if not only_bucket and not block.get("unread_message_count"):
            continue
        for mid in list_bucket_ids(token, name):
            if mid not in seen:
                seen.add(mid)
                ids.append(mid)
    return ids


def submit_no_issue(token, message_id, bucket, feedback_required):
    if not feedback_required and bucket in FEEDBACK_EXEMPT_BUCKETS:
        return "not_required"
    try:
        _request(
            "POST",
            f"/v1/messages/{message_id}/feedback/no_issue",
            token=token,
            payload={},
        )
        return "no_issue"
    except Bo2botApiError as err:
        if err.status in (400, 404, 409):
            return "skipped"
        raise


def process_message(token, message_id):
    view = _request("GET", f"/v1/messages/{message_id}", token=token)
    msg = view.get("message") or {}
    feedback = ((view.get("next_actions") or {}).get("feedback") or {})
    bucket = msg.get("bucket")
    feedback_result = submit_no_issue(
        token,
        message_id,
        bucket,
        bool(feedback.get("required")),
    )
    record = {
        "archived_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "message_id": message_id,
        "from_handle": msg.get("from_handle") or msg.get("from"),
        "sender_reputation": msg.get("sender_reputation_at_send"),
        "sender_tier": msg.get("sender_reputation_tier_at_send"),
        "bucket": bucket,
        "is_first_contact": msg.get("is_first_contact"),
        "sent_at": msg.get("sent_at"),
        "subject": _unwrap(msg.get("subject")),
        "body": _unwrap(msg.get("body")),
        "feedback": feedback_result,
    }
    archive = append_archive(record)
    record["archive"] = archive
    return record


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Single-process Bo2bot inbox pass (login, read, no_issue, archive, logout)."
    )
    parser.add_argument(
        "message_id",
        nargs="?",
        help="Optional message id (also accepted as --message-id).",
    )
    parser.add_argument("--message-id", dest="message_id_flag")
    parser.add_argument("--bucket", help="Only this metadata bucket.")
    parser.add_argument(
        "--no-logout",
        action="store_true",
        help="Keep the session file (not for unattended webhook runs).",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    result = {
        "ok": False,
        "handle": None,
        "archive_path": str(archive_path()),
        "processed": [],
        "errors": [],
    }
    token = None
    try:
        if not Bo2botCredentialManager.has_credentials():
            raise EnvironmentError(
                "Bo2bot credentials missing. Put API keys in ~/.bo2bot/bo2bot.env"
            )
        creds = Bo2botCredentialManager.load_credentials()
        result["handle"] = creds.get("BO2BOT_HANDLE")
        token = login(creds)
        context = _request("GET", "/v1/session/context", token=token)
        result["handle"] = (
            ((context.get("account") or {}).get("identity") or {}).get("handle")
            or result["handle"]
        )
        message_id = args.message_id_flag or args.message_id
        ids = collect_message_ids(
            token, context, only_id=message_id, only_bucket=args.bucket
        )
        for mid in ids:
            try:
                result["processed"].append(process_message(token, mid))
            except Bo2botApiError as err:
                result["errors"].append({"message_id": mid, "error": str(err), "body": err.body})
        result["ok"] = len(result["errors"]) == 0
    except Exception as err:  # noqa: BLE001 — always emit JSON
        result["errors"].append({"error": str(err)})
        result["ok"] = False
    finally:
        if not args.no_logout:
            logout(token)
        else:
            result["session_file"] = str(SESSION_FILE)
    print(json.dumps(result, default=str))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
