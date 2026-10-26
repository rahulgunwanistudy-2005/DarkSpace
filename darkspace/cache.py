import sqlite3
from pathlib import Path

from darkspace.models import ProviderResult
from darkspace.sample import canonical, digest


class CompletionCache:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS completions (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        self.connection.commit()

    @staticmethod
    def key(payload: dict[str, object], model_digest: str, runtime: str) -> str:
        return digest(
            canonical(
                {
                    "provider": "ollama",
                    "runtime": runtime,
                    "model_digest": model_digest,
                    "schema": "idea-v1",
                    "payload": payload,
                }
            )
        )

    def get(self, key: str) -> ProviderResult | None:
        row = self.connection.execute(
            "SELECT value FROM completions WHERE key = ?", (key,)
        ).fetchone()
        return None if row is None else ProviderResult.model_validate_json(row[0])

    def put(self, key: str, value: ProviderResult) -> None:
        encoded = value.model_dump_json()
        old = self.connection.execute(
            "SELECT value FROM completions WHERE key = ?", (key,)
        ).fetchone()
        if old is not None and old[0] != encoded:
            raise ValueError("Refusing to overwrite an immutable cached completion.")
        self.connection.execute(
            "INSERT OR IGNORE INTO completions (key,value) VALUES (?,?)", (key, encoded)
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
