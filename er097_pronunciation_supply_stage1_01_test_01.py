# -*- coding: utf-8 -*-
"""er097 Stage 1 純関数のtest(API 0・実HTTP 0・実Ledger/Production file 無接触。取得はmock)。"""
import copy
import datetime as dt
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er097_pronunciation_supply_stage1_01 as s1  # noqa: E402

NOW = dt.datetime(2026, 10, 22, 12, 0, 0)


def E(surface, etype="cascade_unresolved_entity", **kw):
    d = {"surface": surface, "entity_type": etype, "canonical_spelling": kw.pop("canonical_spelling", surface),
         "expected_pronunciation_ipa": kw.pop("ipa", "/x/"), "pronunciation_hint": kw.pop("hint", "ex"),
         "confidence": kw.pop("confidence", "low"), "sources": kw.pop("sources", ["https://e.example/a"]),
         "updated_at": kw.pop("updated_at", "2026-09-01T00:00:00")}
    d.update(kw)
    return d


# ---------------- 1. 否定記録
def test_outcome_transient_never_negative():
    for r, ex in [(None, None), ({"status": "CREDENTIAL_REQUIRED"}, None), ({"status": "FAILED", "http_status": 429}, None),
                  ({"status": "OK"}, None), ({"status": "OK", "items": "x"}, None), ({"status": "OK", "items": []}, RuntimeError())]:
        o = s1.classify_research_outcome(r, ex)
        assert o == s1.OUTCOME_TRANSIENT
        assert s1.build_negative_record("Foo", o, now=NOW) is None


def test_outcome_not_found_and_found():
    assert s1.classify_research_outcome({"status": "OK", "items": []}) == s1.OUTCOME_NOT_FOUND
    # itemが1件でもあれば現行どおりLedgerへ登録される(次回は命中扱い)ためFOUND。弱さは階層表示で区別する
    assert s1.classify_research_outcome({"status": "OK", "items": [{"expected_pronunciation_ipa": "", "pronunciation_hint": " "}]}) == s1.OUTCOME_FOUND
    assert s1.classify_research_outcome({"status": "OK", "items": [{"pronunciation_hint": "ab-C"}]}) == s1.OUTCOME_FOUND
    assert s1.build_negative_record("Foo", s1.OUTCOME_FOUND, now=NOW) is None


def test_negative_record_ttl_60_days_and_key_is_entity_type_free():
    rec = s1.build_negative_record(" Canelé ", s1.OUTCOME_NOT_FOUND, now=NOW)
    assert rec["key"] == "canele" and rec["ttl_days"] == 60
    assert rec["negative_until"] == "2026-12-21T12:00:00"
    assert s1.negative_status(rec, now=NOW + dt.timedelta(days=59)) == s1.NEG_ACTIVE
    assert s1.negative_status(rec, now=NOW + dt.timedelta(days=60)) == s1.NEG_EXPIRED
    assert s1.negative_status(None, now=NOW) == s1.NEG_ABSENT


def test_negative_invalidated_by_new_entry_or_human_approval():
    rec = s1.build_negative_record("Foo", s1.OUTCOME_NOT_FOUND, now=NOW)
    newer = E("foo", "person", updated_at="2026-10-23T00:00:00")
    assert s1.negative_status(rec, now=NOW + dt.timedelta(days=1), ledger_entries=[newer]) == s1.NEG_INVALIDATED
    older = E("foo", "person", updated_at="2026-10-01T00:00:00")
    assert s1.negative_status(rec, now=NOW + dt.timedelta(days=1), ledger_entries=[older]) == s1.NEG_ACTIVE
    appr = E("foo", "person", human_approved=True, updated_at="2026-01-01T00:00:00")
    assert s1.negative_status(rec, now=NOW + dt.timedelta(days=1), ledger_entries=[appr]) == s1.NEG_INVALIDATED
    ja = E("foo", "ja_reading_katakana", updated_at="2026-10-23T00:00:00")   # 日本語読みでは無効化しない
    assert s1.negative_status(rec, now=NOW + dt.timedelta(days=1), ledger_entries=[ja]) == s1.NEG_ACTIVE
    dis = E("foo", "person", updated_at="2026-10-23T00:00:00", ledger_disabled=True)
    assert s1.negative_status(rec, now=NOW + dt.timedelta(days=1), ledger_entries=[dis]) == s1.NEG_ACTIVE


def test_store_roundtrip_atomic_and_corrupt_is_safe(tmp_path):
    p = str(tmp_path / "neg" / "n.json")
    st = s1.NegativeCacheStore(p)
    assert st.get("Foo") is None
    assert st.put(s1.build_negative_record("Foo", s1.OUTCOME_NOT_FOUND, now=NOW)) is True
    assert st.put(None) is False
    assert st.get("foo ")["key"] == "foo"
    assert not os.path.exists(p + ".tmp")
    assert st.invalidate("FOO") is True and st.get("foo") is None
    with open(p, "w", encoding="utf-8") as f:
        f.write("{broken")
    assert st.get("foo") is None   # 破損=記録なし(従来どおり調査する安全側)


def test_store_does_not_touch_ledger_file(tmp_path):
    led = tmp_path / "ledger.json"
    led.write_text(json.dumps({"a": E("zz")}), encoding="utf-8")
    before = s1.sha256_file(str(led))
    st = s1.NegativeCacheStore(str(tmp_path / "neg.json"))
    st.put(s1.build_negative_record("Foo", s1.OUTCOME_NOT_FOUND, now=NOW))
    assert s1.sha256_file(str(led)) == before


# ---------------- 2. 統一lookup (取りこぼし再現)
def test_lookup_old_key_would_miss_person_entry_but_unified_hits():
    led = {"p1": E("Katz", "person", confidence="high")}
    e, meta = s1.unified_lookup(led, "katz")
    assert e is not None and meta["picked_entity_type"] == "person"


def test_lookup_melos_muse_never_returns_japanese_reading():
    # 実Ledger(melos/muse)の構造: ja_reading_katakana + cascade_unresolved_entity が同綴り
    led = {"ja": E("melos", "ja_reading_katakana", confidence="high", ipa="", hint="", sources=[]),
           "en": E("melos", confidence="low", ipa="mˈiːləs", hint="MEE-lahs")}
    e, meta = s1.unified_lookup(led, "Melos")
    assert e["entity_type"] == "cascade_unresolved_entity" and meta["excluded"] == {"ja_reading_katakana": 1}
    only_ja = {"ja": led["ja"]}
    assert s1.unified_lookup(only_ja, "melos")[0] is None   # 日本語読みだけなら英語発音は未登録扱い(従来の調査経路を維持)


def test_lookup_ranking_and_exclusions():
    led = {"a": E("Foo", "person", confidence="low"),
           "b": E("foo", "place", confidence="high"),
           "c": E("foo", "organization", confidence="high", ledger_disabled=True),
           "d": E("foo", "product", confidence="high", canonical_spelling="cascade")}   # 無関係canonical混入
    e, meta = s1.unified_lookup(led, "FOO")
    assert e["entity_type"] == "place"
    assert meta["excluded"] == {"ledger_disabled": 1, "canonical_unrelated": 1}
    led["a"]["human_approved"] = True
    assert s1.unified_lookup(led, "foo")[0]["entity_type"] == "person"   # 人間承認が最上位


def test_lookup_is_read_only_and_never_mutates():
    led = {"a": E("Foo", "person")}
    snap = copy.deepcopy(led)
    s1.unified_lookup(led, "foo")
    assert led == snap


# ---------------- 3. 一般語除外
@pytest.mark.parametrize("span,expected", [
    ("main story", True), ("one voice", True), ("another voice", True), ("us", True), ("plus", True), ("mini", True),
    ("toteme", False), ("khaite", False), ("stephen reicher", False), ("lindberg", False), ("altuzarra", False),
    ("byus", False), ("melos", False), ("muse", False), ("", False)])
def test_general_word_rule_on_observed_spans(span, expected):
    assert s1.is_general_word_span(span) is expected


def test_general_word_requires_cmu_and_zipf_with_injected_fns():
    assert s1.is_general_word_span("foo bar", cmu_has=lambda t: True, zipf=lambda t: 5.0) is True
    assert s1.is_general_word_span("foo bar", cmu_has=lambda t: t == "foo", zipf=lambda t: 5.0) is False
    assert s1.is_general_word_span("foo bar", cmu_has=lambda t: True, zipf=lambda t: 3.9 if t == "bar" else 6) is False


# ---------------- 6. 統合判断
def _decide(span, led, neg=None):
    return s1.decide_span_action(span, led, neg, now=NOW)


def test_decide_priority_and_legacy_invariant(tmp_path):
    neg = s1.NegativeCacheStore(str(tmp_path / "n.json"))
    # 旧lookup命中(cascade entry・発音情報つき)は必ずUSE_LEDGER、RESEARCHにならない
    led = {"a": E("toteme")}
    assert _decide("toteme", led, neg)["action"] == s1.ACTION_USE_LEDGER
    # 隔離entry(旧: 命中扱い・再調査なし)
    led = {"a": E("plus", ledger_disabled=True, canonical_spelling="cascade")}
    d = _decide("plus", led, neg)
    assert d["action"] == s1.ACTION_SKIP_ISOLATED and d["general_word"] is True
    # 発音情報の無い有効entryのみ(旧: 命中扱い)
    led = {"a": E("khaite", ipa="", hint="")}
    assert _decide("khaite", led, neg)["action"] == s1.ACTION_USE_LEDGER
    # 未登録の一般語
    assert _decide("main story", {}, neg)["action"] == s1.ACTION_SKIP_GENERAL
    # 未登録の固有名詞 -> 調査
    assert _decide("Altuzarra", {}, neg)["action"] == s1.ACTION_RESEARCH
    # 日本語読みだけ -> 調査(従来どおり)
    led = {"j": E("altuzarra", "ja_reading_katakana", ipa="", hint="")}
    assert _decide("altuzarra", led, neg)["action"] == s1.ACTION_RESEARCH


def test_decide_negative_cache_flow(tmp_path):
    neg = s1.NegativeCacheStore(str(tmp_path / "n.json"))
    assert _decide("Zorbax", {}, neg)["action"] == s1.ACTION_RESEARCH
    o = s1.classify_research_outcome({"status": "OK", "items": []})
    neg.put(s1.build_negative_record("Zorbax", o, now=NOW))
    d = _decide("zorbax", {}, neg)
    assert d["action"] == s1.ACTION_SKIP_NEGATIVE and d["negative"]["key"] == "zorbax"
    # 一時失敗は保存されない
    o2 = s1.classify_research_outcome({"status": "FAILED"})
    assert neg.put(s1.build_negative_record("Quuxly", o2, now=NOW)) is False
    assert _decide("Quuxly", {}, neg)["action"] == s1.ACTION_RESEARCH
    # 期間後は再調査
    d = s1.decide_span_action("zorbax", {}, neg, now=NOW + dt.timedelta(days=61))
    assert d["action"] == s1.ACTION_RESEARCH and d["negative_status"] == s1.NEG_EXPIRED
    # 新登録で即無効
    led = {"n": E("zorbax", "person", updated_at="2026-10-23T00:00:00", ipa="/z/", hint="zor-bax")}
    assert s1.decide_span_action("zorbax", led, neg, now=NOW + dt.timedelta(days=2))["action"] == s1.ACTION_USE_LEDGER


# ---------------- 5. V1' 引用実在確認 (fetch は mock)
OK_URL = "https://dict.example/ottoni"


def _fetch_map(m):
    def f(url, timeout, max_bytes):
        v = m.get(url)
        if isinstance(v, Exception):
            raise v
        return v
    return f


ENTRY = E("Ottoni", "person", ipa="/oʊˈtoʊni/", hint="oh-TOH-nee", sources=[OK_URL])
HTML = "<html><script>var Ottoni='oh-TOH-nee'</script><body><p>Ottoni is pronounced <b>oh-TOH-nee</b>.</p></body></html>"


def test_verify_pron_in_page_and_script_content_is_ignored():
    r = s1.verify_citations(ENTRY, _fetch_map({OK_URL: HTML}), url_ok=lambda u: True)
    assert r["tier"] == s1.TIER_PRON_IN_PAGE
    only_script = "<script>Ottoni oh-TOH-nee</script><p>nothing here</p>"
    r = s1.verify_citations(ENTRY, _fetch_map({OK_URL: only_script}), url_ok=lambda u: True)
    assert r["tier"] == s1.TIER_UNVERIFIED


def test_verify_quote_name_only_and_failures_are_unverified_not_rejected():
    e = dict(ENTRY, evidence=[{"url": OK_URL, "quote": "Ottoni is pronounced oh-TOH-nee"}])
    assert s1.verify_citations(e, _fetch_map({OK_URL: HTML}), url_ok=lambda u: True)["tier"] == s1.TIER_QUOTE_VERIFIED
    assert s1.verify_citations(ENTRY, _fetch_map({OK_URL: "<p>Ottoni was born in 1970</p>"}), url_ok=lambda u: True)["tier"] == s1.TIER_NAME_IN_PAGE
    for bad in (None, TimeoutError("t")):
        r = s1.verify_citations(ENTRY, _fetch_map({OK_URL: bad}), url_ok=lambda u: True)
        assert r["tier"] == s1.TIER_UNVERIFIED and r["checked"] == 1   # 例外を伝播させず未検証として残す
    assert s1.verify_citations(dict(ENTRY, sources=[]), _fetch_map({}), url_ok=lambda u: True)["tier"] == s1.TIER_NO_SOURCE


def test_verify_fabricated_quote_not_in_page_is_not_verified():
    e = dict(ENTRY, evidence=[{"url": OK_URL, "quote": "Ottoni is officially pronounced aw-TAW-nee"}])
    r = s1.verify_citations(e, _fetch_map({OK_URL: HTML}), url_ok=lambda u: True)
    assert r["tier"] == s1.TIER_PRON_IN_PAGE   # 偽引用はQUOTE_VERIFIEDにならない(発音表記の実在までに留まる)


def test_verify_limits_and_unsafe_urls():
    calls = []

    def f(url, timeout, max_bytes):
        calls.append((url, timeout, max_bytes))
        return "<p>nothing</p>"
    many = dict(ENTRY, sources=[f"https://e{i}.example/x" for i in range(10)])
    r = s1.verify_citations(many, f, url_ok=lambda u: True)
    assert len(calls) == s1.FETCH_MAX_URLS and r["checked"] == s1.FETCH_MAX_URLS
    assert all(c[1] == s1.FETCH_TIMEOUT_SEC and c[2] == s1.FETCH_MAX_BYTES for c in calls)
    calls.clear()
    r = s1.verify_citations(dict(ENTRY, sources=["http://127.0.0.1/x", "file:///etc/passwd", "ftp://a/b"]), f)
    assert calls == [] and r["tier"] == s1.TIER_UNVERIFIED


def test_is_safe_url_with_injected_resolver():
    pub = lambda h: ["93.184.216.34"]
    assert s1.is_safe_url("https://example.com/a", resolver=pub)
    for h, ip in [("l", "127.0.0.1"), ("p", "10.0.0.5"), ("p2", "192.168.1.1"), ("ll", "169.254.169.254"), ("v6", "::1")]:
        assert not s1.is_safe_url(f"http://{h}/", resolver=lambda _h, ip=ip: [ip])
    assert not s1.is_safe_url("gopher://example.com/", resolver=pub)
    assert not s1.is_safe_url("https://example.com/", resolver=lambda h: [])
    assert not s1.is_safe_url("https://example.com/", resolver=lambda h: ["93.184.216.34", "10.0.0.1"])   # 1つでも内部宛なら遮断


# ---------------- 4. HR表示 (追加キーのみ・既存キー不変)
def test_hr_display_is_additive_and_labels():
    info = dict(ENTRY)
    snap = copy.deepcopy(info)
    x = s1.hr_display(info, action=s1.ACTION_USE_LEDGER, lookup_meta={"picked_entity_type": "person"})
    assert info == snap and x["evidence_tier"] == s1.TIER_UNVERIFIED and x["lookup_entity_type"] == "person"
    assert any("根拠階層" in l for l in x["display_lines_ja"])
    assert set(x).isdisjoint(set(info)) or all(k not in info for k in x)   # 既存キーと衝突しない
    neg = s1.build_negative_record("foo", s1.OUTCOME_NOT_FOUND, now=NOW)
    n = s1.hr_display(None, action=s1.ACTION_SKIP_NEGATIVE, negative=neg)
    assert n["evidence_tier"] == s1.TIER_NEGATIVE and "調査済み・未取得" in "".join(n["display_lines_ja"]) and n["negative_until"]
    g = s1.hr_display(None, action=s1.ACTION_SKIP_GENERAL)
    assert g["evidence_tier"] == s1.TIER_GENERAL
    v = s1.hr_display(info, action=s1.ACTION_USE_LEDGER, verification={"tier": s1.TIER_PRON_IN_PAGE, "checked": 1})
    assert v["evidence_tier"] == s1.TIER_PRON_IN_PAGE and v["citation_check"]["checked"] == 1
    assert s1.evidence_tier(dict(info, human_approved=True)) == s1.TIER_HUMAN
    assert s1.evidence_tier(dict(info, sources=[])) == s1.TIER_NO_SOURCE


def test_module_does_not_import_production_judgement_modules():
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "er097_pronunciation_supply_stage1_01.py"), encoding="utf-8").read()
    for banned in ("er006_secondary_asr", "er078_", "er094_", "er006_m1_multi", "er006_pronunciation_ledger"):
        assert f"import {banned}" not in src and f"from {banned}" not in src


# ---------------- 5b. default_fetch (http_getはmock)
class _Resp:
    def __init__(self, code=200, headers=None, body=b""):
        self.status_code, self.headers, self._b = code, headers or {"Content-Type": "text/html"}, body

    def iter_content(self, n):
        for i in range(0, len(self._b), n):
            yield self._b[i:i + n]


def test_default_fetch_size_cap_redirect_and_content_type():
    ok = lambda u: True
    big = _Resp(body=b"a" * 100000)
    assert len(s1.default_fetch("https://x/a", 1, 1000, http_get=lambda u, t: big, url_ok=ok)) == 1000
    assert s1.default_fetch("https://x/a", http_get=lambda u, t: _Resp(404), url_ok=ok) is None
    assert s1.default_fetch("https://x/a", http_get=lambda u, t: _Resp(headers={"Content-Type": "application/pdf"}, body=b"x"), url_ok=ok) is None
    hops = []

    def g(u, t):
        hops.append(u)
        return _Resp(302, {"Location": "/b"}) if u.endswith("/a") else _Resp(body=b"<p>hi</p>")
    assert s1.default_fetch("https://x/a", http_get=g, url_ok=ok) == "<p>hi</p>" and hops == ["https://x/a", "https://x/b"]
    loop = lambda u, t: _Resp(302, {"Location": u})
    assert s1.default_fetch("https://x/a", http_get=loop, url_ok=ok) is None            # redirect上限
    # redirect先が内部宛なら遮断(各hopで再検査)
    ssrf = lambda u, t: _Resp(302, {"Location": "http://127.0.0.1/"}) if "x" in u and "127" not in u else _Resp(body=b"secret")
    assert s1.default_fetch("https://x/a", http_get=ssrf, url_ok=lambda u: "127.0.0.1" not in u) is None


# ---------------- 7. resolve_span_for_review (全副作用を注入)
class _World:
    def __init__(self, ledger=None, research=None, raises=None):
        self.ledger, self.research, self.raises = ledger if ledger is not None else {}, research, raises
        self.research_calls, self.upserts = [], []

    def loader(self):
        return self.ledger

    def research_fn(self, span):
        self.research_calls.append(span)
        if self.raises:
            raise self.raises
        return self.research

    def upsert_fn(self, span, item):
        self.upserts.append((span, item))
        e = dict(item, surface=span, entity_type="cascade_unresolved_entity")
        e.setdefault("canonical_spelling", span)
        self.ledger[f"id{len(self.ledger)}"] = e
        return e


def _run(w, span, neg=None, fetch=None):
    return s1.resolve_span_for_review(span, ledger_loader=w.loader, research_fn=w.research_fn, upsert_fn=w.upsert_fn,
                                      neg_store=neg, now=NOW, fetch=fetch, url_ok=lambda u: True)


def test_resolver_general_word_and_isolated_never_call_research(tmp_path):
    w = _World()
    r = _run(w, "main story")
    assert r["action"] == s1.ACTION_SKIP_GENERAL and r["info"] is None and not r["research_called"] and w.research_calls == []
    assert r["extra"]["evidence_tier"] == s1.TIER_GENERAL
    w2 = _World({"a": E("plus", ledger_disabled=True, canonical_spelling="cascade")})
    r = _run(w2, "plus")
    assert r["action"] == s1.ACTION_SKIP_ISOLATED and w2.research_calls == [] and r["extra"]["evidence_tier"] == s1.TIER_GENERAL


def test_resolver_found_registers_once_and_second_call_is_ledger_hit():
    item = {"canonical_spelling": "Altuzarra", "expected_pronunciation_ipa": "/x/", "pronunciation_hint": "al-too-ZAH-rah", "confidence": "low"}
    w = _World(research={"status": "OK", "items": [item], "citations": ["https://e.example/p"]})
    r = _run(w, "altuzarra", fetch=lambda u, t, m: "<p>Altuzarra al-too-ZAH-rah</p>")
    assert r["research_called"] and r["outcome"] == s1.OUTCOME_FOUND and r["info"]["sources"] == ["https://e.example/p"]
    assert w.upserts[0][1]["evidence_tier"] == s1.TIER_PRON_IN_PAGE and r["info"]["evidence_check"]["checked"] == 1
    r2 = _run(w, "altuzarra")
    assert r2["action"] == s1.ACTION_USE_LEDGER and not r2["research_called"] and len(w.research_calls) == 1


def test_resolver_not_found_writes_negative_then_skips(tmp_path):
    neg = s1.NegativeCacheStore(str(tmp_path / "n.json"))
    w = _World(research={"status": "OK", "items": [], "citations": []})
    r = _run(w, "Zorbax", neg)
    assert r["outcome"] == s1.OUTCOME_NOT_FOUND and r["negative_written"] and r["info"] is None and w.upserts == []
    r2 = _run(w, "zorbax", neg)
    assert r2["action"] == s1.ACTION_SKIP_NEGATIVE and len(w.research_calls) == 1
    assert r2["extra"]["evidence_tier"] == s1.TIER_NEGATIVE and "調査済み・未取得" in "".join(r2["extra"]["display_lines_ja"])


def test_resolver_transient_never_stored(tmp_path):
    neg = s1.NegativeCacheStore(str(tmp_path / "n.json"))
    for research, raises in [({"status": "FAILED", "http_status": 500}, None), ({"status": "CREDENTIAL_REQUIRED"}, None), (None, OSError("net"))]:
        w = _World(research=research, raises=raises)
        r = _run(w, "Zorbax", neg)
        assert r["outcome"] == s1.OUTCOME_TRANSIENT and not r["negative_written"] and neg.get("zorbax") is None and w.upserts == []
        assert _run(w, "Zorbax", neg)["research_called"] is True        # 次回は再調査(一時失敗を抑止しない)
    w = _World(raises=ValueError("cost logger not initialised"))
    with pytest.raises(ValueError):                                       # transient_exceptions以外は揉み消さない
        _run(w, "Zorbax", neg)


def test_resolver_disabled_after_upsert_hides_info():
    w = _World(research={"status": "OK", "items": [{"canonical_spelling": "unknown", "pronunciation_hint": "uh"}], "citations": []})
    w.upsert_fn = lambda span, item: dict(item, surface=span, ledger_disabled=True)
    r = _run(w, "Qwertyx")
    assert r["info"] is None and r["research_called"]


def test_resolver_no_judgement_outputs():
    # 戻り値に判定語彙(final_status/verified/classification/should_pass等)を含まない
    w = _World()
    r = _run(w, "main story")
    blob = json.dumps(r, ensure_ascii=False, default=str)
    for k in ("final_status", "verified", "should_pass", "classification", "human_review_required", "stop_retrying"):
        assert k not in blob


# ================= 委任_04 [E-1b] Opus反映 (S1-03/04/05/07/08)
# ---------------- S1-03: 補助機能の例外は従来動作へ。調査APIの例外は素通し
class _BoomStore:
    def get(self, surface):
        raise RuntimeError("get boom")

    def put(self, rec):
        raise RuntimeError("put boom")


def test_s103_negative_store_exceptions_fall_back_to_legacy_behaviour():
    w = _World(research={"status": "OK", "items": [], "citations": []})
    r = _run(w, "Zorbax", _BoomStore())                       # get例外=記録なし扱い=調査する / put例外=書込なしで続行
    assert r["research_called"] and r["outcome"] == s1.OUTCOME_NOT_FOUND and r["negative_written"] is False and r["info"] is None
    assert "negative_until" not in r["extra"]                 # 書けていないので「再調査しない」とは表示しない
    assert w.research_calls == ["Zorbax"]


def test_s103_store_tmp_unique_and_cleaned_even_when_replace_fails(tmp_path, monkeypatch):
    p = str(tmp_path / "n.json")
    st = s1.NegativeCacheStore(p)
    monkeypatch.setattr(os, "replace", lambda a, b: (_ for _ in ()).throw(OSError("replace failed")))
    with pytest.raises(OSError):
        st.put(s1.build_negative_record("Foo", s1.OUTCOME_NOT_FOUND, now=NOW))
    assert os.listdir(tmp_path) == []                         # 一時fileを残さない
    monkeypatch.undo()
    names = []
    real_replace = os.replace

    def spy(a, b):
        names.append(os.path.basename(a))
        return real_replace(a, b)
    monkeypatch.setattr(os, "replace", spy)
    st.put(s1.build_negative_record("A", s1.OUTCOME_NOT_FOUND, now=NOW))
    st.put(s1.build_negative_record("B", s1.OUTCOME_NOT_FOUND, now=NOW))
    assert len(set(names)) == 2 and all(str(os.getpid()) in n and n.endswith(".tmp") for n in names)   # 呼出ごとに別名(pid+uuid)


def test_s103_corrupt_record_shape_is_ignored(tmp_path):
    p = tmp_path / "n.json"
    p.write_text(json.dumps({"zorbax": "not-a-dict", "other": 5}), encoding="utf-8")
    st = s1.NegativeCacheStore(str(p))
    assert st.get("zorbax") is None
    assert s1.decide_span_action("zorbax", {}, st, now=NOW)["action"] == s1.ACTION_RESEARCH


def test_s103_verify_and_display_exceptions_do_not_break_registration(monkeypatch):
    item = {"canonical_spelling": "Altuzarra", "pronunciation_hint": "al-too-ZAH-rah", "confidence": "low"}
    w = _World(research={"status": "OK", "items": [item], "citations": ["https://e.example/p"]})
    monkeypatch.setattr(s1, "verify_citations", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("v boom")))
    r = _run(w, "altuzarra", fetch=lambda u, t, m: "x")
    assert r["info"] is not None and "evidence_tier" not in w.upserts[0][1] and "evidence_check" not in w.upserts[0][1]
    monkeypatch.setattr(s1, "hr_display", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("d boom")))
    w2 = _World(research={"status": "OK", "items": [item], "citations": []})
    r2 = _run(w2, "altuzarra")
    assert r2["info"] is not None and r2["extra"] == {}      # 表示キーなし=従来のHR表示


def test_s103_research_api_exception_still_propagates_and_general_check_failure_researches():
    w = _World(raises=KeyError("cost logger"))
    with pytest.raises(KeyError):
        _run(w, "Zorbax")
    boom = lambda t: (_ for _ in ()).throw(ImportError("no wordfreq"))
    assert s1.decide_span_action("main story", {}, None, now=NOW, cmu_has=boom)["action"] == s1.ACTION_RESEARCH   # 判定不能=従来どおり調査


def test_s103_is_safe_url_any_exception_is_false():
    def boom(_h):
        raise RuntimeError("dns")
    assert s1.is_safe_url("https://example.com/", resolver=boom) is False
    assert s1.is_safe_url(None) is False and s1.is_safe_url("http://[bad") is False


# ---------------- S1-04: 調査用type entryを先に処理
def test_s104_research_type_entry_takes_precedence_over_other_type():
    # 調査用typeが隔離されていれば、別typeの有効entry(情報あり)があっても従来どおり「隔離=None」
    led = {"a": E("foo", ledger_disabled=True, canonical_spelling="cascade"), "b": E("foo", "person", confidence="high")}
    assert _decide("foo", led)["action"] == s1.ACTION_SKIP_ISOLATED
    # 調査用type有効(情報なしでも)=従来の命中扱いで返す
    led = {"a": E("foo", ipa="", hint=""), "b": E("foo", "person", confidence="high")}
    d = _decide("foo", led)
    assert d["action"] == s1.ACTION_USE_LEDGER and d["entry"]["entity_type"] == s1.RESEARCH_ENTITY_TYPE
    # 調査用typeがなく別typeに情報あり -> 別typeを採用
    assert _decide("foo", {"b": E("foo", "person")})["entry"]["entity_type"] == "person"


def test_s104_step3_is_limited_to_research_type():
    # 発音情報の無い別typeのentryだけ: 旧実装(lookupは調査用keyのみ)は調査していた -> 同じく調査する
    assert _decide("Altuzarra", {"p": E("altuzarra", "person", ipa="", hint="")})["action"] == s1.ACTION_RESEARCH
    # 別typeの隔離entryだけ: 旧lookupは命中しなかった -> 調査する
    assert _decide("Altuzarra", {"p": E("altuzarra", "person", ledger_disabled=True)})["action"] == s1.ACTION_RESEARCH


# ---------------- S1-05: 別type採用の注記
def test_s105_other_type_note_in_display():
    led = {"p": E("Katz", "person", confidence="high")}
    r = s1.resolve_span_for_review("katz", ledger_loader=lambda: led, research_fn=lambda s: pytest.fail("no research"),
                                   upsert_fn=lambda *a: None, neg_store=None, now=NOW)
    assert any("同綴りの別entry(type=person)の情報。同一対象かは未確認" in l for l in r["extra"]["display_lines_ja"])
    assert r["extra"]["same_spelling_other_type"] == "person"
    same_type = s1.hr_display(E("Katz"), action=s1.ACTION_USE_LEDGER)
    assert "same_spelling_other_type" not in same_type and not any("別entry" in l for l in same_type["display_lines_ja"])


# ---------------- S1-07: 語境界・短い表記・ae
def test_s107_word_boundary_matching():
    fm = lambda t: _fetch_map({OK_URL: t})
    assert s1.verify_citations(ENTRY, fm("<p>Bottonix oh-TOH-nee</p>"), url_ok=lambda u: True)["tier"] == s1.TIER_UNVERIFIED   # ottoniは語の途中
    assert s1.verify_citations(ENTRY, fm("<p>Ottoni's oh-TOH-nee</p>"), url_ok=lambda u: True)["tier"] == s1.TIER_PRON_IN_PAGE
    assert s1.verify_citations(ENTRY, fm("<p>Ottoni oh-TOH-neeeee</p>"), url_ok=lambda u: True)["tier"] == s1.TIER_NAME_IN_PAGE  # 発音表記も語境界


def test_s107_short_pron_forms_are_not_used():
    e = E("Ottoni", "person", ipa="", hint="oh-no", sources=[OK_URL])          # 正規化後4文字 -> 照合に使わない
    assert s1.verify_citations(e, _fetch_map({OK_URL: "<p>Ottoni says oh no</p>"}), url_ok=lambda u: True)["tier"] == s1.TIER_NAME_IN_PAGE
    e5 = E("Ottoni", "person", ipa="", hint="oh-toni", sources=[OK_URL])       # 5文字は使う
    assert s1.verify_citations(e5, _fetch_map({OK_URL: "<p>Ottoni = oh-toni</p>"}), url_ok=lambda u: True)["tier"] == s1.TIER_PRON_IN_PAGE


def test_s107_ipa_marks_and_ae_letters():
    e = E("Ottoni", "person", ipa="/oʊˈtoʊni/", hint="", sources=[OK_URL])
    assert s1.verify_citations(e, _fetch_map({OK_URL: "<p>Ottoni [oʊˈtoʊni]</p>"}), url_ok=lambda u: True)["tier"] == s1.TIER_PRON_IN_PAGE
    ae = E("Ægir", "person", ipa="/ˈaɪɡɪr/", hint="EYE-gir", sources=[OK_URL])
    assert s1.verify_citations(ae, _fetch_map({OK_URL: "<p>Ægir (EYE-gir)</p>"}), url_ok=lambda u: True)["tier"] == s1.TIER_PRON_IN_PAGE
    assert s1._words("Ægir Malmö Žižek") == "ægir malmo zizek"


# ---------------- S1-08: 全体ON/OFF(全ON/全OFFのみ)
def test_s108_single_flag_all_off_has_zero_side_effects():
    calls = []
    r = s1.resolve_span_for_review("Zorbax", ledger_loader=lambda: calls.append("L"), research_fn=lambda s: calls.append("R"),
                                   upsert_fn=lambda *a: calls.append("U"), neg_store=_BoomStore(), now=NOW, fetch=lambda *a: calls.append("F"),
                                   enabled=False)
    assert calls == [] and r["action"] == s1.ACTION_DISABLED and r["info"] is None and r["extra"] == {} and not r["research_called"]


def test_s108_module_constant_controls_default(monkeypatch):
    monkeypatch.setattr(s1, "PRON_SUPPLY_STAGE1_ENABLED", False)
    w = _World()
    assert _run(w, "main story")["action"] == s1.ACTION_DISABLED
    monkeypatch.setattr(s1, "PRON_SUPPLY_STAGE1_ENABLED", True)
    assert _run(w, "main story")["action"] == s1.ACTION_SKIP_GENERAL


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
