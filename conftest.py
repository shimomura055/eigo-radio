# -*- coding: utf-8 -*-
"""pytest共通fixture(ASR-HOMOPHONE 委任_04、Opus should-fix): 各test前後で er109 の run scope が None であること(scope漏れの検出)。
er109_xz_scope_01 が無い環境では何もしない。unittest(run_project_regression.py)側は er109_xz_scope_01_test_01.Base が同じ検査を行う。"""
import pytest


@pytest.fixture(autouse=True)
def _er109_scope_must_be_clean():
    try:
        import er109_xz_scope_01 as xz
    except Exception:  # noqa: BLE001
        yield
        return
    assert xz.current_scope() is None, "前のtestからer109 scopeが漏れている"
    yield
    assert xz.current_scope() is None, "このtestがer109 scopeを残した"
