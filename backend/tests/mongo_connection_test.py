import os
import sys
from pathlib import Path

from pymongo import MongoClient


def _load_dotenv_fallback(dotenv_path: Path) -> None:
    """Minimal .env loader (KEY=VALUE, ignores comments/blank lines)."""
    try:
        for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
    except Exception:
        # If parsing fails, just proceed with existing environment variables.
        return


def _safe_print(*args, **kwargs) -> None:
    """Avoid UnicodeEncodeError on some Windows terminals."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        safe_args = [str(a).encode("utf-8", errors="replace").decode("utf-8") for a in args]
        print(*safe_args, **kwargs)


def main() -> int:
    backend_dir = Path(__file__).resolve().parents[1]
    dotenv_path = backend_dir / ".env"

    if dotenv_path.exists():
        try:
            from dotenv import load_dotenv  # type: ignore

            load_dotenv(dotenv_path)
        except Exception:
            _load_dotenv_fallback(dotenv_path)

    mongo_uri = (os.getenv("MONGO_URI") or os.getenv("MONGODB_URI") or "").strip()
    mongo_db = (os.getenv("MONGO_DB") or "").strip()

    if not mongo_uri:
        _safe_print("MONGO_URI is not set. Add it to backend/.env or set it in the environment.")
        return 2

    # Keep this short so failures are quick and obvious.
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        msg = "MongoDB connection OK (ping succeeded)."
        if mongo_db:
            # Optional: verify we can list collections on the configured DB
            # (this may require appropriate permissions on Atlas)
            db = client[mongo_db]
            try:
                _ = db.list_collection_names()
                msg += f" DB access OK for '{mongo_db}'."
            except Exception as e:  # permissions/network can vary
                msg += f" DB access check skipped/failed for '{mongo_db}': {type(e).__name__}"

        _safe_print(msg)
        return 0

    except Exception as e:
        _safe_print("MongoDB connection FAILED:")
        _safe_print(f"  {type(e).__name__}: {e}")
        _safe_print("Tips:")
        _safe_print("  - Ensure the URI is correct (mongodb+srv://... for Atlas).")
        _safe_print("  - For Atlas: add your IP to Network Access (or allow 0.0.0.0/0 temporarily).")
        _safe_print("  - Confirm username/password and DB user permissions.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
