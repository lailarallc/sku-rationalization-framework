"""The prod guard sits in front of the scoring Postgres read.

`src.scoring.db.connect()` (used by run_scoring.py and scripts/calibrate.py)
targets localhost:5432 -- a `fly proxy` tunnel to production when one is open.
This test fakes a flyctl listener and asserts nothing connects.
"""

import pytest

from src.scoring import db, prod_guard


def test_connect_refuses_fly_tunnel(monkeypatch, tmp_path):
    monkeypatch.delenv("ALLOW_PROD_DB", raising=False)
    monkeypatch.setenv("POSTGRES_PASSWORD", "unused")
    monkeypatch.setattr(prod_guard, "_listener", lambda port: "flyctl")
    monkeypatch.setattr(db.psycopg2, "connect", lambda *a, **kw: pytest.fail("connected"))
    with pytest.raises(prod_guard.ProdDatabaseError):
        db.connect(tmp_path / "missing.env")
