# -*- coding: utf-8 -*-
"""PNPS Stage 1 配線test(E-2。API 0・実HTTP 0)。er006_secondary_asr_01._resolve_unresolved_entity_for_review と呼出側
(最終slot HR package)へのStage 1配線を、実関数(evaluate_attempt_with_cascade_detail)で確認する。
確認: ON/OFFで判定出力が一致 / mockがNoneでもstub動作 / 一般語は調査不呼出 / 否定記録で2回目不呼出 / 統一lookup命中 /
HR queueへ追加キー / Ledger upsert素通し3キーのバイト一致(キー無し呼出) / OFFで旧挙動(Ledger・sidecarバイト一致)。"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import re
import subprocess
import sys

import pytest

import er006_asr_provider_routing_01 as routing
import er006_pronunciation_ledger_01 as L
import er006_secondary_asr_01 as sec

PRE_STAGE1_COMMIT = "3bb71e186"   # Stage 1配線(cb12e2ecd)の直前commit。upsert素通し3キー追加前のLedger moduleを比較基準にする
CAS = "cascade_unresolved_entity"
CANON = "Ottoni and colleagues published a study."
ASR_P = "A Tony and colleagues published a study."
ASR_S = "Otoni and colleagues published a study."
ITEM = {"surface": "Ottoni", "entity_type": "person", "canonical_spelling": "Ottoni", "language_origin": "Italian",
        "expected_pronunciation_ipa": "/oʊˈtoʊni/", "pronunciation_hint": "oh-TOH-nee", "alternate_pronunciations": [],
        "confidence": "medium", "ambiguity_note": ""}
FOUND = {"status": "OK", "items": [ITEM], "citations": ["https://example.test/ottoni"]}
EMPTY = {"status": "OK", "items": [], "citations": []}


class Env:
    def __init__(self, tmp, monkeypatch):
        self.dir = str(tmp)
        self.ledger = os.path.join(self.dir, "ledger.json")
        self.hr = os.path.join(self.dir, "hr.jsonl")
        self.calls = []
        self.research = None
        self.fetches = []
        monkeypatch.setattr(L, "LEDGER_PATH", self.ledger)
        monkeypatch.setattr(sec, "HUMAN_REVIEW_LOG_PATH", self.hr)
        monkeypatch.setattr(routing, "transcribe", lambda *a, **k: (ASR_P, None))
        monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", lambda *a, **k: (ASR_S, None))

        def fake_research(items, *a, **k):
            self.calls.append(items[0]["surface"])
            r = self.research
            if isinstance(r, BaseException):
                raise r
            return copy.deepcopy(r)
        monkeypatch.setattr(sec.pronun_research, "research_pronunciations", fake_research)

        def fake_fetch(url, timeout=5.0, max_bytes=0):
            self.fetches.append(url)
            return "<html><body>Ottoni (oh-TOH-nee) is a name.</body></html>"
        monkeypatch.setattr(sec, "_pron_supply_fetch", fake_fetch)
        # is_safe_url の名前解決だけ、公開IP(例示用)を返すstubにする(実DNS 0。SSRF遮断自体はer097 testで検証済み)
        import socket
        monkeypatch.setattr(socket, "getaddrinfo", lambda host, *a, **k: [(2, 1, 6, "", ("93.184.216.34", 0))])

    def sidecar(self):
        return os.path.join(self.dir, sec.PRON_SUPPLY_NEGATIVE_CACHE_FILENAME)

    def last_slot(self, canon=CANON):
        return sec.evaluate_attempt_with_cascade_detail(
            canon, ASR_P, [], "dummy.wav", cascade_enabled=True, attempt_ctx={"slot": 3, "is_last_slot": True})


@pytest.fixture
def env(tmp_path, monkeypatch):
    return Env(tmp_path, monkeypatch)


JUDGE_KEYS = ("verified", "final_status", "stop_retrying", "human_review_required", "cascade_invoked", "cost_guard_triggered")


def _judgement(r):
    d = {k: r.get(k) for k in JUDGE_KEYS}
    d["steps"] = json.dumps(r.get("steps"), ensure_ascii=False, default=str, sort_keys=True)
    d["classification"] = getattr(r.get("classification"), "classification", None)
    return d


def test_on_off_judgement_identical_and_off_is_legacy(env, monkeypatch):
    env.research = FOUND
    monkeypatch.setattr(sec, "PRON_SUPPLY_STAGE1_ENABLED", True)
    on = env.last_slot()
    led_on = json.load(open(env.ledger, encoding="utf-8"))
    os.remove(env.ledger)
    env.calls.clear()
    monkeypatch.setattr(sec, "PRON_SUPPLY_STAGE1_ENABLED", False)
    off = env.last_slot()
    led_off = json.load(open(env.ledger, encoding="utf-8"))
    assert _judgement(on) == _judgement(off)                       # 判定出力は一致
    assert on["human_review_required"] is True and on["verified"] is False
    # OFFは旧挙動: sidecar無し・追加キー無し・Ledgerに出典ページ照合キー無し
    assert not os.path.exists(env.sidecar())
    for v in off["pronunciation_lookups"].values():
        assert not ({"evidence_tier", "lookup_action", "display_lines_ja"} & set(v))
    assert all("source_page_check_v1" not in e for e in led_off.values())
    # ONはOFFに対し追加キーのみ(既存キーの値は同じ。updated_atは時刻のため除外)
    a, b = on["pronunciation_lookups"]["ottoni"], off["pronunciation_lookups"]["ottoni"]
    for k, v in b.items():
        if k != "updated_at":
            assert a[k] == v, k
    assert {"evidence_tier", "lookup_action", "display_lines_ja"} <= set(a)
    (e_on,), (e_off,) = led_on.values(), led_off.values()
    assert set(e_on) - set(e_off) <= {"evidence_tier", "source_page_check_v1", "evidence"}
    assert ({k: v for k, v in e_on.items() if k in e_off and k != "updated_at"}
            == {k: v for k, v in e_off.items() if k != "updated_at"})


def test_mock_resolver_returning_none_uses_legacy_stub_without_extra(env, monkeypatch):
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda span: None)
    r = env.last_slot()
    v = r["pronunciation_lookups"]["ottoni"]
    assert v["confidence"] == "unconfirmed" and v["ambiguity_note"] == sec._STUB_NOTE_DEFAULT and v["sources"] == []
    assert not ({"evidence_tier", "lookup_action", "display_lines_ja"} & set(v))   # mockの外側でStage 1は動かない
    assert env.calls == [] and not os.path.exists(env.sidecar()) and env.fetches == []


def test_mock_resolver_returning_plain_dict_is_used_as_is(env, monkeypatch):
    info = {"expected_pronunciation_ipa": "/x/", "pronunciation_hint": "x", "confidence": "low", "sources": []}
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda span: dict(info))
    v = env.last_slot()["pronunciation_lookups"]["ottoni"]
    assert v == info and env.calls == []


def test_general_word_span_not_researched(env):
    env.research = FOUND
    for w in ("us", "main story", "one voice"):
        assert sec._resolve_unresolved_entity_for_review(w) is None
        assert sec._stage1_take()["action"] == "SKIP_GENERAL_WORD"
    assert env.calls == [] and not os.path.exists(env.ledger)


def test_general_word_stub_note_and_hr_extra(env, monkeypatch):
    monkeypatch.setattr(sec, "_unresolved_entity_spans", lambda cls: ["main story"])
    env.research = FOUND
    v = env.last_slot()["pronunciation_lookups"]["main story"]
    assert env.calls == []
    assert v["confidence"] == "unconfirmed" and "通常の英語語彙" in v["ambiguity_note"]
    assert v["evidence_tier"] == "GENERAL_WORD_NOT_SEARCHED" and v["lookup_action"] == "SKIP_GENERAL_WORD"


def test_negative_record_skips_second_research(env):
    env.research = EMPTY
    r1 = env.last_slot()
    assert env.calls == ["ottoni"]
    assert os.path.exists(env.sidecar()) and not os.path.exists(env.ledger)       # Ledger本体には何も書かない
    v1 = r1["pronunciation_lookups"]["ottoni"]
    assert v1["confidence"] == "unconfirmed" and v1["ambiguity_note"] == sec._STUB_NOTE_DEFAULT
    r2 = env.last_slot()
    assert env.calls == ["ottoni"]                                                  # 2回目は調査0
    v2 = r2["pronunciation_lookups"]["ottoni"]
    assert "過去に調査したが発音情報は得られなかった" in v2["ambiguity_note"]
    assert v2["evidence_tier"] == "NEGATIVE_SEARCHED_NOT_FOUND" and v2["negative_until"]
    assert _judgement(r1) == _judgement(r2)


def test_transient_failure_not_recorded_negative(env):
    import requests
    env.research = requests.exceptions.ConnectionError("x")
    env.last_slot()
    assert not os.path.exists(env.sidecar())
    env.research = {"status": "FAILED", "http_status": 401}
    env.last_slot()
    assert not os.path.exists(env.sidecar()) and env.calls == ["ottoni", "ottoni"]


def test_unified_lookup_hits_other_type_entry_without_research(env):
    L.upsert(L.LedgerKey("Ottoni", "person"), dict(ITEM, sources=["https://example.test/ottoni"]))
    env.research = FOUND
    v = env.last_slot()["pronunciation_lookups"]["ottoni"]
    assert env.calls == []
    assert v["entity_type"] == "person" and v["same_spelling_other_type"] == "person"
    assert v["lookup_action"] == "USE_LEDGER" and "同一対象かは未確認" in "".join(v["display_lines_ja"])
    assert len(json.load(open(env.ledger, encoding="utf-8"))) == 1                  # 調査用typeの重複entryを作らない


def test_found_registers_cascade_entry_with_source_page_check(env):
    env.research = FOUND
    r = env.last_slot()
    v = r["pronunciation_lookups"]["ottoni"]
    assert env.fetches == ["https://example.test/ottoni"]
    assert v["evidence_tier"] == "PRON_IN_CITED_PAGE" and v["citation_check"]["tier"] == "PRON_IN_CITED_PAGE"
    (e,) = json.load(open(env.ledger, encoding="utf-8")).values()
    assert e["entity_type"] == CAS and e["source_page_check_v1"]["tier"] == "PRON_IN_CITED_PAGE" and "evidence_check" not in e
    env.last_slot()                                                                  # 2回目はLedger命中でAPI/HTTP 0
    assert env.calls == ["ottoni"] and len(env.fetches) == 1


def test_fetch_exception_does_not_break_registration(env, monkeypatch):
    env.research = FOUND

    def boom(url, timeout=5.0, max_bytes=0):
        raise RuntimeError("boom")
    monkeypatch.setattr(sec, "_pron_supply_fetch", boom)
    v = env.last_slot()["pronunciation_lookups"]["ottoni"]
    assert v["expected_pronunciation_ipa"] == "/oʊˈtoʊni/" and v["evidence_tier"] == "UNVERIFIED_AI_OUTPUT"


def test_hr_queue_row_has_additive_keys(env):
    env.research = FOUND
    sec.evaluate_attempt_with_cascade(CANON, ASR_P, [], "dummy.wav", cascade_enabled=True, attempt_ctx={"slot": 3, "is_last_slot": True})
    rows = [json.loads(x) for x in open(env.hr, encoding="utf-8")]
    assert len(rows) == 1
    v = rows[0]["pronunciation_lookups"]["ottoni"]
    assert v["evidence_tier"] and v["display_lines_ja"] and v["lookup_action"] == "RESEARCH"
    for k in ("canonical_spelling", "expected_pronunciation_ipa", "pronunciation_hint", "confidence", "sources"):
        assert k in v                                                                # CURRENT_SPEC 1837 (a)〜(f) 維持


def test_isolated_entry_still_no_info_no_research(env):
    L.upsert(L.LedgerKey("Ottoni", CAS), dict(ITEM, ledger_disabled=True, ledger_disabled_reason="t"))
    env.research = FOUND
    v = env.last_slot()["pronunciation_lookups"]["ottoni"]
    assert env.calls == [] and v["confidence"] == "unconfirmed" and "隔離済み" in v["ambiguity_note"]


def _legacy_ledger_module():
    src = subprocess.run(["git", "show", PRE_STAGE1_COMMIT + ":er006_pronunciation_ledger_01.py"], capture_output=True, check=True).stdout.decode("utf-8")
    if "source_page_check_v1" in src:
        pytest.skip("pre-Stage1 commit unexpectedly contains Stage 1 passthrough")
    spec = importlib.util.spec_from_loader("ledger_legacy_head", loader=None)
    m = importlib.util.module_from_spec(spec)
    sys.modules["ledger_legacy_head"] = m
    exec(compile(src, "ledger_legacy_head.py", "exec"), m.__dict__)
    return m


def test_ledger_upsert_without_new_keys_is_byte_identical_to_pre_stage1(tmp_path, monkeypatch):
    legacy = _legacy_ledger_module()
    monkeypatch.setattr(L.time, "strftime", lambda *a, **k: "2026-10-22T00:00:00")
    calls = [("Ottoni", "person", ITEM), ("Zzqv", CAS, dict(ITEM, canonical_spelling="unknown")),
             ("Melos", CAS, dict(ITEM, ledger_disabled=True, ledger_disabled_reason="x")), ("Ottoni", "person", dict(ITEM, confidence="high"))]
    out = []
    for mod, name in ((legacy, "old.json"), (L, "new.json")):
        p = str(tmp_path / name)
        monkeypatch.setattr(mod, "LEDGER_PATH", p)
        for s, t, it in calls:
            mod.upsert(mod.LedgerKey(s, t), copy.deepcopy(it))
        out.append(open(p, "rb").read())
    assert out[0] == out[1]


def test_ledger_upsert_passthrough_only_when_given_and_not_inherited(tmp_path, monkeypatch):
    monkeypatch.setattr(L, "LEDGER_PATH", str(tmp_path / "l.json"))
    k = L.LedgerKey("Ottoni", CAS)
    L.upsert(k, dict(ITEM, evidence_tier="PRON_IN_CITED_PAGE", source_page_check_v1={"tier": "x"}, evidence=[{"url": "u", "quote": "q"}]))
    e = L.lookup(k)
    assert e["evidence_tier"] == "PRON_IN_CITED_PAGE" and e["source_page_check_v1"] == {"tier": "x"} and e["evidence"]
    L.upsert(k, dict(ITEM))                                                           # キー無し再登録=引き継がない
    e2 = L.lookup(k)
    assert not ({"evidence_tier", "source_page_check_v1", "evidence"} & set(e2))


def test_no_judgement_assignment_reads_stage1_values():
    """Stage 1の値(_stage1_*/pronunciation_lookups)は判定語の代入行に現れない。"""
    src = open("er006_secondary_asr_01.py", encoding="utf-8").read()
    for ln in src.splitlines():
        if re.search(r"result\[\"(verified|final_status|stop_retrying|human_review_required)\"\]\s*=", ln):
            assert "_stage1" not in ln and "pronunciation_lookups" not in ln
