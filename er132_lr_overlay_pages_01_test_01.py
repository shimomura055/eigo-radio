# LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_10(Phase B / B3準備): er132_lr_overlay_pages_01(未配線の純module)+配線patchのtest。
# API 0・費用JPY0・LLMなし。run dir・既存Productionコードは書き換えない(patchの適用確認は一時dirのコピーに対してだけ行う)。
# 保存データ(AI島・Word Gacha・猿の手・告げ口心臓等)に依存するtestは、データが無い環境ではskipする(合成ケースは常に実行)。
import ast
import glob
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

import er129_lr_display_reflection_01 as e129
import er132_lr_overlay_pages_01 as m

ROOT = os.path.dirname(os.path.abspath(__file__))
PATCH = os.path.join(ROOT, "docs", "research", "LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01", "patches", "B3_wiring_01.patch")
PATCH_FILES = ["er019_family_x_audio_production_runner_01.py", "er117_z_chunk_wiring_test_01.py", "er019_family_x_listening_page_01.py", "er026_family_z_fiction_production_runner_01.py",
               "er063_family_z_audio_01.py", "er121_family_y_audio_01.py", "er_user_listening_page_common_01.py"]

AI = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01"
WG = "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01"
BAPE = "er019_output/family_x_audio_production_wiring_01/boredom_aggression__run_bape_01"
MP = "er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01"
MELOS_LR0 = "er026_output/family_z_production_e2e_01/melos/run_e2e_06"
TTH = "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01"
Y_LR = "er121_output/family_y_production_01/redelivery_fee/run_tru_ev_y_adv_4b"


def _need(path):
    if not os.path.exists(os.path.join(ROOT, path)):
        pytest.skip(f"stored data not present: {path}")


def _j(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def _tree_sha(base, names):
    out = {}
    for n in names:
        p = os.path.join(ROOT, base, n)
        out[n] = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None
    return out


# ============================================================ 合成: overlay / 例外
def _clip(cid, before, after, source, verdict=e129.V_PASS, adopted=True):
    return {"clip_id": cid, "verdict": verdict, "lr": {"before": before, "after": after, "adopted_in_final": adopted}, "display": {"source": source}}


BEFORE = "The AIs sent to the island had no set tasks. They were ready."
AFTER = "The AI agents sent to the island had no set tasks. They were ready."
DISPLAY = "Day one. " + BEFORE + " The end."


def test_overlay_empty_ledger_returns_same_object():
    assert m.overlay_text(None, DISPLAY, source="parts.json:part1") is DISPLAY
    assert m.overlay_text({"clips": []}, DISPLAY, source="parts.json:part1") is DISPLAY
    assert m.overlay_text({"clips": [_clip("c", BEFORE, AFTER, "parts.json:part2")]}, DISPLAY, source="parts.json:part1") is DISPLAY   # 別unit


def test_overlay_applies_replace_is_idempotent_and_keeps_original():
    led = {"clips": [_clip("c", BEFORE, AFTER, "parts.json:part1")]}
    out = m.overlay_text(led, DISPLAY, source="parts.json:part1")
    assert out == "Day one. " + AFTER + " The end."
    assert DISPLAY == "Day one. " + BEFORE + " The end."            # 原本不変
    assert m.overlay_text(led, out, source="parts.json:part1") == out   # 反映済み(AFTER)なら何もしない(冪等)


def test_overlay_by_clip_id_for_entry_source_and_stop_verdict_is_not_silently_original():
    led = {"clips": [_clip("full_story_part2_c1", BEFORE, AFTER, m.ENTRY_SOURCE)]}
    assert m.display_text_of_clip(led, "full_story_part2_c1", BEFORE).startswith("The AI agents")
    assert m.display_text_of_clip(led, "other_clip", BEFORE) == BEFORE
    bad = {"clips": [_clip("c", BEFORE, AFTER, "parts.json:part1", verdict=e129.V_UNLOCATABLE)]}
    with pytest.raises(m.LROverlayError):
        m.overlay_text(bad, DISPLAY, source="parts.json:part1")
    miss = {"clips": [_clip("c", BEFORE, AFTER, "parts.json:part1")]}
    with pytest.raises(m.LROverlayError):                              # 表示本文に位置が無い=黙って原文のまま通さない
        m.overlay_text(miss, "Completely different text without the phrase at all here.", source="parts.json:part1")


def test_overlay_level_units_copies_parts_and_support_only_changed_keys():
    led = {"clips": [_clip("full_story_part1_k2", BEFORE, AFTER, "parts.json:part1"),
                     _clip("y_voice_1", BEFORE, AFTER, "parts.json:segments.y_voice_1"),
                     _clip("comment_1", BEFORE, AFTER, "b1_support_texts.json:comment_1")]}
    parts = {"title": "T", "part1": DISPLAY, "part2": "keep", "segments": {"y_voice_1": DISPLAY, "y_voice_2": "keep2"}}
    support = {"comment_1": DISPLAY, "comment_2": "keep3"}
    p2, s2 = m.overlay_level_units(led, parts, support)
    assert "AI agents" in p2["part1"] and "AI agents" in p2["segments"]["y_voice_1"] and "AI agents" in s2["comment_1"]
    assert p2["part2"] == "keep" and p2["segments"]["y_voice_2"] == "keep2" and s2["comment_2"] == "keep3"
    assert "AIs" in parts["part1"] and "AIs" in parts["segments"]["y_voice_1"] and "AIs" in support["comment_1"]   # 入力不変
    p3, s3 = m.overlay_level_units({"clips": []}, parts, support)
    assert p3 is parts and s3 is support                                  # LR 0=同一object(byte同一)


def test_overlay_highlight_units_changed_and_unchanged():
    led = {"clips": [_clip("full_story_part1_k2", BEFORE, AFTER, "parts.json:part1")]}
    units = [{"key": "full_story_part1", "texts": [DISPLAY], "joiner": " "}, {"key": "full_story_part2", "texts": ["x y z"], "joiner": " "}]
    out = m.overlay_highlight_units(led, units)
    assert out is not units and "AI agents" in out[0]["texts"][0] and out[1] is units[1] and "AIs" in units[0]["texts"][0]
    assert m.overlay_highlight_units({"clips": []}, units) is units
    assert m.overlay_highlight_units(None, units) is units


# ============================================================ 混入検知(公開物の禁止語)
@pytest.mark.parametrize("text,expected", [
    ("<div class='fhr-lr'>x</div>", "fhr_class"),
    ('<span class="a fhr-fb">x</span>', "fhr_class"),
    (".fhr-lr{color:#c00}", "fhr_css"),
    ("warning_labels: LR_REWRITTEN", "LR_REWRITTEN"),
    ("LR_APPLIED", "LR_APPLIED"),
    ("FALLBACK_APPLIED", "FALLBACK_APPLIED"),
    ("FALLBACK_MINIMAL_EN", "FALLBACK_MINIMAL"),
    ("Style: ENGLISH_LOCK", "ENGLISH_LOCK"),
    ("LEGACY_DIALOGUE", "LEGACY_DIALOGUE"),
    ("instruction_type=minimal_fallback", "minimal_fallback"),
    ("Local Rewrite採用(音声は原稿から変更: replace 'Melos' -> 'He')", "note_local_rewrite"),
    ("Fallback発動", "note_lr_fallback_jp"),
])
def test_public_leak_hits_detects_each_forbidden_form(text, expected):
    assert expected in m.public_leak_hits(text)
    with pytest.raises(m.LRDisplayConsistencyStop):
        m.assert_no_public_leak(text)


def test_public_leak_hits_clean_text_and_none():
    clean = "<div class='script'>The AI agents sent to the island had no set tasks. Voice: Charon / Style: calm</div><table class='kp'></table>"
    assert m.public_leak_hits(clean) == [] and m.public_leak_hits("") == [] and m.public_leak_hits(None) == []
    m.assert_no_public_leak(clean)


# ============================================================ 未配線の確認(Production/既存moduleからimportされない)
# 委任_11(B-wire): 設計上の配線先(三者一致Gate=X/Y/Z assemble入口、overlay=ページ描画)だけを許可する
ER132_ALLOWED_USERS = ("er019_family_x_audio_production_runner_01.py", "er019_family_x_listening_page_01.py", "er121_family_y_audio_01.py",
                       "er063_family_z_audio_01.py", "er026_family_z_fiction_production_runner_01.py",
                       "er133_report_marks_01_test_01.py", "er130_gate_wiring_mock_e2e_01_test_01.py")   # 後2つ=配線後のtest(importはtest内)


def test_er132_is_not_imported_by_any_existing_module():
    offenders = []
    for p in glob.glob(os.path.join(ROOT, "*.py")):
        n = os.path.basename(p)
        if n.startswith("er132_") or n in ER132_ALLOWED_USERS:
            continue
        try:
            tree = ast.parse(open(p, encoding="utf-8").read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            if any(x == "er132_lr_overlay_pages_01" for x in names):
                offenders.append(n)
    assert offenders == [], offenders   # 配線patch(未適用)以外にimport元が無い=既定動作不変


def test_er132_top_level_imports_are_stdlib_only():
    tree = ast.parse(open(os.path.join(ROOT, "er132_lr_overlay_pages_01.py"), encoding="utf-8").read())
    top = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    mods = {a.name.split(".")[0] for n in top if isinstance(n, ast.Import) for a in n.names} | {n.module.split(".")[0] for n in top if isinstance(n, ast.ImportFrom)}
    assert mods <= {"__future__", "os", "re", "typing"}, mods     # er129/er020/er128は遅延import(公開ページ検査に重いimportを強いない)


# ============================================================ 三者一致Gate(実データ)
def test_gate_unwired_is_always_abnormal_for_lr_run_and_wired_passes_ai_island():
    _need(AI)
    for lv in ("a2", "b1b"):
        res = m.evaluate_text_parity(AI, lv)                 # rendered_display=None=overlay未配線の呼出
        assert res["status"] == m.STATUS_DISPLAY_CONSISTENCY and res["problems"][0]["code"] == "DISPLAY_NOT_OVERLAID"
        with pytest.raises(m.LRDisplayConsistencyStop) as ei:
            m.assert_text_parity(AI, lv)
        assert ei.value.status == "BLOCKED_LR_DISPLAY_CONSISTENCY"
        summ = m.blocked_summary(ei.value)
        assert summ["status"] == "BLOCKED_LR_DISPLAY_CONSISTENCY" and summ["hr_queue"] is False        # HRキューへ入れない
        ok = m.assert_text_parity(AI, lv, rendered_display=m.rendered_display_units(AI, lv))
        assert ok["status"] == "OK" and ok["checked"] and ok["checked"][0]["verdict"].startswith("PASS")
        assert m.assemble_gate_summary(AI, lv) is None        # 配線済み(overlay済み描画unitを渡す)ならPASS=通過


def test_gate_detects_display_left_at_original_text():
    _need(AI)
    orig = {}
    for lv, new in (("a2", "AI agents"), ("b1b", "AI systems")):
        parts = _j(f"{AI}/{lv}/parts.json")
        orig = {"parts.json:part1": parts["part1"]}            # overlayしない原文のまま描画した場合
        assert "AIs" in parts["part1"] and new not in parts["part1"]
        res = m.evaluate_text_parity(AI, lv, rendered_display=orig)
        assert res["status"] == m.STATUS_DISPLAY_CONSISTENCY, res
        assert res["problems"][0]["code"] in ("MISMATCH_V1", "MISMATCH_V2")


def test_gate_z_stop_cls_and_status_attr():
    _need(MP)

    class FamilyZLRDisplayConsistencyStop(RuntimeError):
        pass

    with pytest.raises(FamilyZLRDisplayConsistencyStop) as ei:
        m.assert_text_parity(MP, "a2", stop_cls=FamilyZLRDisplayConsistencyStop)   # overlay未配線の呼出=異常側
    assert ei.value.status == m.STATUS_DISPLAY_CONSISTENCY and ei.value.problems
    rendered = m.rendered_display_units(MP, "a2")
    assert m.z_assemble_gate(MP, "a2", FamilyZLRDisplayConsistencyStop)["status"] == "OK"
    assert rendered


# ============================================================ mock integration(X/Y/Z、API 0。Production呼出は変えず、er132の関数を直接呼ぶ)
def _x_overlay(run, lv):
    parts = _j(f"{run}/{lv}/parts.json")
    sup_name = "b1_support_texts.json" if lv == "b1b" else "a2_support_texts.json"
    support = _j(f"{run}/{lv}/{sup_name}") if os.path.exists(os.path.join(ROOT, run, lv, sup_name)) else {}
    led = m.level_ledger(os.path.join(ROOT, run), lv)
    p2, s2 = m.overlay_level_units(led, parts, support)
    return parts, p2, support, s2, led


@pytest.mark.parametrize("lv,new,gone", [("a2", "AI agents", "AIs"), ("b1b", "AI systems", "AIs")])
def test_mock_x_ai_island_std_adv_display_becomes_lr_after_and_parity_passes(lv, new, gone):
    _need(AI)
    names = ["parts.json", f"{lv}/parts.json", f"{lv}/audit/tts_generation_results.json", f"{lv}/audit/confirmed_selection.json"]
    before = _tree_sha(AI, names)
    parts, p2, _s, _s2, led = _x_overlay(AI, lv)
    assert new in p2["part1"] and gone not in re.findall(r"[A-Za-z']+", p2["part1"])
    assert p2["part1"].replace(new, gone) == parts["part1"]           # 変更はLR 1語の箇所だけ(逆置換で原文と一致)
    assert p2["part2"] == parts["part2"] and p2["part3"] == parts["part3"]
    assert m.assert_text_parity(os.path.join(ROOT, AI), lv, rendered_display=m.rendered_display_units(os.path.join(ROOT, AI), lv))["status"] == "OK"
    assert _tree_sha(AI, names) == before                              # 原本・保存結果・確定内容は不変


def test_mock_x_ai_island_highlights_resolve_on_overlaid_display_units():
    _need(AI)
    sel = _j(f"{AI}/b1b/audit/confirmed_selection.json") if os.path.exists(os.path.join(ROOT, AI, "b1b", "audit", "confirmed_selection.json")) else None
    if not sel:
        pytest.skip("confirmed_selection.json absent")
    import er019_family_x_audio_production_runner_01 as R
    import er_learning_highlight_01 as hl
    spec_ok = R.x_display_spec(os.path.join(ROOT, AI), "b1b")
    if not spec_ok:
        pytest.skip("display_spec absent (no highlights)")
    parts, p2, _s, _s2, _led = _x_overlay(AI, "b1b")
    kp_dir = os.path.join(ROOT, AI, "b1b", "key_phrases")
    rec = R._er128().load_record(kp_dir)
    src = R.x_source_dir_of(os.path.join(ROOT, AI))
    article = R.load_text(f"{src}/b1b/article.md")
    cands = R.load_json(f"{kp_dir}/kp_candidates.json")
    res = hl.resolve_highlights(article, cands, hl.items_from_record(rec), R.x_display_units(p2), lr_rebound=True)
    assert res["status"] == "OK", res.get("issues")
    # 描画と解決が同じ文字列(overlay後)であること(HL_DISPLAY_UNIT_MISMATCH相当の確認)
    texts = {u["key"]: u["texts"][0] for u in R.x_display_units(p2)}
    assert "AI systems" in texts["full_story_part1"]


def test_mock_x_word_gacha_adv_display_you_have():
    _need(WG)
    parts, p2, *_ = _x_overlay(WG, "b1b")
    assert "you have" in p2["part3"] and p2["part3"] != parts["part3"]
    assert m.assert_text_parity(os.path.join(ROOT, WG), "b1b", rendered_display=m.rendered_display_units(os.path.join(ROOT, WG), "b1b"))["status"] == "OK"


def test_mock_z_monkeys_paw_std_display_visitor_and_gate():
    _need(MP)
    run = os.path.join(ROOT, MP)
    led = m.level_ledger(run, "a2")
    clips = [c for c in led["clips"] if c["verdict"] == e129.V_PASS and c["lr"]]
    assert [c["clip_id"] for c in clips] == ["full_story_part1_c10"]
    data = _j(f"{MP}/a2/audit/tts_generation_results.json")
    ct = data["segments"]["full_story_part1_c10"]["canonical_text"]
    shown = m.display_text_of_clip(led, "full_story_part1_c10", ct)
    assert shown != ct and "visitor" in shown and "guest" in ct and "guest" not in re.findall(r"[a-z]+", shown)
    res = m.assert_text_parity(run, "a2", rendered_display=m.rendered_display_units(run, "a2"))
    assert res["status"] == "OK"
    assert [c for c in led["clips"] if c["clip_id"] == "full_story_part1_c10"][0]["fallback"]["state"] == "UNKNOWN"   # 記録欠落(B2 §5(b))は別項目。三者一致Gateは表示一致だけを見る


def test_mock_y_lr_adopted_display_note():
    _need(Y_LR)
    parts = _j(f"{Y_LR}/b1b/parts.json")
    led = m.level_ledger(os.path.join(ROOT, Y_LR), "b1b")
    sup = _j(f"{Y_LR}/b1b/support_texts.json") if os.path.exists(os.path.join(ROOT, Y_LR, "b1b", "support_texts.json")) else {}
    p2, s2 = m.overlay_level_units(led, parts, sup)
    assert p2 is not parts and "note" in p2["segments"]["y_voice_1"] and "notice" in parts["segments"]["y_voice_1"]
    assert m.assert_text_parity(os.path.join(ROOT, Y_LR), "b1b", rendered_display=m.rendered_display_units(os.path.join(ROOT, Y_LR), "b1b"))["status"] == "OK"


@pytest.mark.parametrize("run,lv", [(BAPE, "a2"), (BAPE, "b1b"), (MELOS_LR0, "a2"), (MELOS_LR0, "b1b"), (TTH, "a2"), (TTH, "b1b")])
def test_mock_lr_zero_runs_are_unchanged_and_gate_passes_even_unwired(run, lv):
    _need(run)
    r = os.path.join(ROOT, run)
    led = m.level_ledger(r, lv)
    assert not any(c.get("lr") for c in led["clips"])                  # LR 0
    if os.path.exists(os.path.join(r, lv, "parts.json")):
        parts = _j(f"{run}/{lv}/parts.json")
        sup_name = "b1_support_texts.json" if lv == "b1b" else "a2_support_texts.json"
        support = _j(f"{run}/{lv}/{sup_name}") if os.path.exists(os.path.join(r, lv, sup_name)) else {}
        p2, s2 = m.overlay_level_units(led, parts, support)
        assert p2 is parts and s2 is support                           # byte同一(同一object)
        assert json.dumps(p2, sort_keys=True) == json.dumps(parts, sort_keys=True)
    assert m.rendered_display_units(r, lv) == {}
    assert m.evaluate_text_parity(r, lv)["status"] == "OK"             # LR 0はoverlay未配線の呼出でも通る(新たな停止を作らない)
    assert m.assemble_gate_summary(r, lv) is None


# ============================================================ 混入検知(保存run実測 / 公開ページ実測)
def _scan_run_strings(run_rel, lv):
    """TTS入力・ASR期待文・Style Prompt・KP表示・study_text・表示本文の文字列を集めて禁止語を数える。"""
    base = os.path.join(ROOT, run_rel, lv)
    hits = []
    rp = os.path.join(base, "audit", "tts_generation_results.json")
    if os.path.exists(rp):
        data = json.load(open(rp, encoding="utf-8"))
        for sid, e, _ in e129._iter_entries(data):
            info = e129._lr_info(e, e.get("canonical_text") if isinstance(e.get("canonical_text"), str) else (e.get("text") or ""))
            vals = {"text": e.get("text"), "canonical_text": e.get("canonical_text"), "instruction": e.get("instruction"),
                    "asr_expected": (info or {}).get("asr_expected"),
                    "style_prefix": (e.get("style_prefix") or {}).get("head200") if isinstance(e.get("style_prefix"), dict) else e.get("style_prefix")}
            for k, v in vals.items():
                if isinstance(v, str) and m.public_leak_hits(v):
                    hits.append((lv, sid, k, m.public_leak_hits(v)))
    for fn in ("parts.json", "b1_support_texts.json", "a2_support_texts.json", "support_texts.json"):
        p = os.path.join(base, fn)
        if os.path.exists(p):
            for _path, s in e129._string_leaves(json.load(open(p, encoding="utf-8"))):
                if m.public_leak_hits(s):
                    hits.append((lv, fn, _path, m.public_leak_hits(s)))
    kp = os.path.join(base, "key_phrases", "keywords_canonicalized.json")
    if os.path.exists(kp):
        for _path, s in e129._string_leaves(json.load(open(kp, encoding="utf-8"))):
            if m.public_leak_hits(s):
                hits.append((lv, "kp", _path, m.public_leak_hits(s)))
    for p in glob.glob(os.path.join(base, "study_text", "*.md")) + glob.glob(os.path.join(ROOT, run_rel, "study_text", "*.md")):
        if m.public_leak_hits(open(p, encoding="utf-8", errors="ignore").read()):
            hits.append((lv, p, "study_text", m.public_leak_hits(open(p, encoding="utf-8", errors="ignore").read())))
    return hits


@pytest.mark.parametrize("run", [AI, WG, BAPE, MP, MELOS_LR0, TTH, Y_LR])
def test_stored_runs_have_no_lr_fallback_note_in_tts_asr_style_kp_study_text(run):
    _need(run)
    hits = []
    for lv in ("a2", "b1b"):
        hits += _scan_run_strings(run, lv)
    assert hits == [], hits[:5]


def test_overlay_output_itself_never_contains_forbidden_words_on_real_runs():
    for run in (AI, WG, MP):
        _need(run)
    for run, lv in ((AI, "a2"), (AI, "b1b"), (WG, "b1b")):
        _p, p2, _s, s2, _l = _x_overlay(run, lv)
        for _path, s in e129._string_leaves(p2) + e129._string_leaves(s2):
            assert m.public_leak_hits(s) == []


def _published_pages():
    out = []
    for p in glob.glob(os.path.join(ROOT, "user_test", "*", "*.html")):
        n = os.path.basename(p)
        d = os.path.basename(os.path.dirname(p))
        if n in ("index.html", "standard.html", "advanced.html") and not d.startswith(("hr_",)) and "/hr_" not in p.replace("\\", "/"):
            out.append(p)
    return sorted(out)


def test_public_page_scan_flags_exactly_the_known_publication_mismatches():
    pages = _published_pages()
    if not pages:
        pytest.skip("user_test pages absent")
    flagged = {os.path.relpath(p, ROOT).replace("\\", "/"): m.public_leak_hits(open(p, encoding="utf-8", errors="ignore").read()) for p in pages}
    flagged = {k: v for k, v in flagged.items() if v}
    known = {"user_test/family_z_melos_01/advanced.html", "user_test/family_z_monkeys_paw_01/standard.html"}   # 既公開4件のうちZ注記(LR横断監査W4。B7の是正対象)
    assert set(flagged) <= known, flagged
    for k in set(flagged) & known:
        assert "note_local_rewrite" in flagged[k]                       # 検出器が実在の混入(Z公開ページのLR注記)を捕捉できる


# ============================================================ 配線(委任_11 B-wire: B3 patchを適用済みの作業ツリー)
def _src(f):
    return open(os.path.join(ROOT, f), encoding="utf-8").read()


def test_wired_sources_compile_and_gate_runs_before_style_gates_and_overlay_at_each_render_site():
    for f in ("er019_family_x_audio_production_runner_01.py", "er019_family_x_listening_page_01.py", "er121_family_y_audio_01.py",
              "er063_family_z_audio_01.py", "er026_family_z_fiction_production_runner_01.py", "er_user_listening_page_common_01.py"):
        compile(_src(f), f, "exec")
    xr = _src("er019_family_x_audio_production_runner_01.py")
    for lv in ("b1b", "a2"):
        i = xr.index(f'_er132.assemble_gate_summary(theme_out_dir, "{lv}", not_rendered_clip_ids=_er132.X_NOT_RENDERED_CLIP_IDS)')
        j = xr.index(f'_style_profile_gate_blocked_summary(theme_out_dir, out_dir, "{lv}")', i)
        assert i < j                                                      # 三者一致Gate→M3/Style Gateの順(W2 §5-3)
    assert "_er132.overlay_level_dir_units(level_dir, parts, support)" in xr and "lr_rebound = lr_rebound or (_parts_disp is not parts)" in xr
    y = _src("er121_family_y_audio_01.py")
    assert y.index("_er132.assemble_gate_summary(theme_out_dir, level)") < y.index("gate = y_style_gate(theme_out_dir, level, style_profile)")
    assert "overlay_highlight_units" in y and 'display_text_of_clip(_lr, "topic_intro"' in y
    z = _src("er063_family_z_audio_01.py")
    assert z.count("display_text_of_clip(_lr, cid") == 2                  # build_page_rows と full_story_display_units(2式を同じoverlayに揃える)
    zr = _src("er026_family_z_fiction_production_runner_01.py")
    assert zr.index("_er132.z_assemble_gate(") < zr.index("m.a63.run_assembly(ctx.out_dir, lv, inp[\"story_clips\"]")
    xl = _src("er019_family_x_listening_page_01.py")
    assert 'display_text_of_clip(_lr, "topic_intro", info["text"])' in xl     # X topic_introは表示=採用音声(Fable補足(2))


def test_wired_z_old_lr_notes_replaced_by_report_marks_and_voice_style_kept():
    z = _src("er063_family_z_audio_01.py")
    assert "Local Rewrite採用" not in z                                # 旧「LR採用」注記2か所(row["notes"])は撤去
    assert 'row["marks"] = _rm.marks_for(' in z and 'row["chunk_texts"]' in z   # 共通表示部品(LR赤・Fallback濃青・⏸)へ置換
    assert "Voice: {_esc(r['voice'])} / Style: {_esc(r['style'])}" in z      # Voice:表示は維持
    assert "TTS方式" in z and 'row["notes"].append(f"{_label}適用' in z      # TTS方式・減速注記は維持
    assert "FamilyZLRDisplayConsistencyStop(FamilyZAudioStop)" in z
    pv = _src("er063_family_z_page_verify_01.py")
    assert 'text.count("Voice:")' in pv and '"TTS方式" in text' in pv       # page_verifyが見る文字列は変わらず出力される(偽NGにならない)


def test_wired_x_listing_page_shows_lr_rows_in_red_not_hidden_and_has_no_audience_split():
    t = _src("er019_family_x_listening_page_01.py")
    assert "audience: str" not in t and "AUDIENCE_PUBLIC" not in t           # build_pageにaudience引数なし=出し分けしない(ユーザー原文_02 §4)
    assert "LR_REWRITTEN" in t and "color:#c00000" in t                       # 事後試聴リストのLR行は非表示にせず赤で表示
    assert "_rm.marks_for(" in t and "uc.script_block(info[\"text\"], _cts, highlights=hls or None, marks=_mk)" in t


def test_check_page_public_no_longer_forbids_report_marks_and_has_no_html_leak_check():
    import er_user_listening_page_common_01 as uc
    page_path = os.path.join(ROOT, "user_test", "family_x_word_gacha_01", "index.html")
    if not os.path.exists(page_path):
        pytest.skip("page absent")
    html = open(page_path, encoding="utf-8").read()
    levels = ("Standard", "Advanced")
    res = uc.check_page(html, levels=levels, audience="public")
    assert "no_lr_fallback_note_in_public" not in res["checks"] and "no_chunk_marker_in_public" not in res["checks"]
    marked = html.replace("</body>", "<p><span class='rpt-lr'>x</span> <span class='chunk-mark'>&#9208;</span></p></body>")
    assert uc.check_page(marked, levels=levels, audience="public")["overall"] == res["overall"]   # 試聴ページHTMLへの⏸/赤/青は混入扱いにしない(Fable補足(1))


XSTD_TOPIC = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_tru_ev_x_std_2"


def test_x_topic_intro_lr_is_connected_to_clip_overlay_and_japanese_title_is_recorded_not_rendered():
    """Fable補足(2): Xのページが`Today's topic is {title}.`として表示するtopic_introのLRは、表示源をclip overlayへ接続(表示=採用音声)。
    表示しない`japanese_title`は三者一致の対象外として`not_rendered`に記録(STOPしない)。"""
    _need(XSTD_TOPIC)
    r = os.path.join(ROOT, XSTD_TOPIC)
    ledger = m.level_ledger(r, "a2")
    parts = json.load(open(os.path.join(r, "a2", "parts.json"), encoding="utf-8"))
    tmpl = f"Today's topic is {parts['title']}."
    shown = m.display_text_of_clip(ledger, "topic_intro", tmpl)
    assert shown != tmpl and "Today's subject is" in shown                   # LR後の英文(採用音声)を表示
    rendered = m.rendered_display_units(r, "a2")
    assert m.evaluate_text_parity(r, "a2", rendered_display=rendered, not_rendered_clip_ids=m.X_NOT_RENDERED_CLIP_IDS)["status"] == "OK"
    assert m.assemble_gate_summary(r, "a2", not_rendered_clip_ids=m.X_NOT_RENDERED_CLIP_IDS) is None
    assert m.X_NOT_RENDERED_CLIP_IDS == ("japanese_title",)
    # japanese_titleにLRがあっても停止せずnot_renderedへ記録される(合成)
    res = m.evaluate_text_parity(r, "a2", rendered_display=rendered, not_rendered_clip_ids=("topic_intro",))
    assert res["status"] == "OK" and [x["clip_id"] for x in res["not_rendered"]] == ["topic_intro"]
