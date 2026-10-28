# LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_09(Phase B / B5): er131_final_human_report_01(未配線の読取専用CLI)のtest。
# 採用attempt判定はer129へ委譲(er131に独自規則なし)・LR/Fallback重複・記録欠落・A/B/C・混入防止5層。API 0・費用JPY0。
# 保存run依存のtestはデータが無い環境ではskip(合成ケースは常に実行)。run dirは書き換えない(前後sha一致を固定)。
import ast
import glob
import hashlib
import json
import os
import re

import pytest

import er129_lr_display_reflection_01 as e129
import er131_final_human_report_01 as m

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "er131_final_human_report_01.py")
X = "er019_output/family_x_audio_production_wiring_01"
Z = "er026_output/family_z_production_e2e_01"
Y = "er121_output/family_y_production_01"
RUNS = {
    "ai": f"{X}/ai_island_temple__run_form_prod_01",
    "wg": f"{X}/word_gacha__run_wg_01",
    "melos": f"{Z}/melos/run_e2e_06",
    "paw": f"{Z}/the_monkeys_paw/run_sf_prod_01",
    "tth": f"{Z}/the_tell_tale_heart/run_reselect_01",
    "y1": f"{Y}/redelivery_fee/run_01",
    "x16": f"{X}/coffee_prices__run_tru_ev_x_adv_16",
    "xja": f"{X}/coffee_prices__run_tru_ev_x_std_6",
    "zdlg": f"{Z}/the_monkeys_paw/run_tru_ev_z_adv_2",
}
PUBLIC = ["user_test/family_x_ai_island_form_01", "user_test/family_x_word_gacha_01", "user_test/family_z_melos_02",
          "user_test/family_z_monkeys_paw_01", "user_test/family_z_tell_tale_heart_reselect_01", "user_test/family_y_production_redelivery_fee_01",
          "user_test/family_y_production_redelivery_fee_02", "user_test/family_y_production_redelivery_fee_03"]


def _need(rel):
    if not os.path.exists(os.path.join(ROOT, rel)):
        pytest.skip(f"stored data not present: {rel}")


def _model(key, lv):
    rd = RUNS[key]
    _need(rd + f"/{lv}/audit/tts_generation_results.json")
    return m.build_model(os.path.join(ROOT, rd), lv, rd.split("/")[0] and ("Y" if "er121" in rd else "Z" if "er026" in rd else "X"))


def _card(model, cid):
    return next(c for c in model["cards"] if c["id"] == cid)


# ------------------------------------------------------------------ 合成ledger(採用take判定はer129が出した結果をそのまま使う)
def _clip(cid, *, fb_state="NOT_USED", kind="NORMAL", lr=None, warnings=(), style_name=None, source="derived", slot=None, verdict="PASS"):
    take = {"source": source, "kind": kind, "style_name": style_name or ("ROLE_STYLE" if kind == "NORMAL" else kind), "style_sha": "ab" * 32,
            "from_style_sha": "cd" * 32, "slot": slot, "status": "OK"}
    c = {"clip_id": cid, "role": "FULL_STORY", "chunk_parent": None, "warnings": list(warnings), "adopted_take": take, "overlap": None, "text_parity": None,
         "fallback": {"state": fb_state, "used": fb_state == "USED", "adopted_style": style_name if fb_state == "USED" else None,
                      "from_style": "ROLE_STYLE(cdcdcdcd)" if fb_state == "USED" else None, "slot": slot, "kind": kind}, "verdict": verdict, "lr": None}
    if fb_state == "UNKNOWN":
        c["adopted_take"] = None
    if lr:
        before, after = lr
        c["lr"] = {"before": before, "after": after, "adopted_in_final": True, "superseded_by_human": False, "reason": "because", "source": "local_rewrite_recovery"}
        c["_ops"] = e129.compute_ops(before, after)
    return c


def test_adoption_decision_is_delegated_to_er129_not_reimplemented():
    """採用take・Fallback有無はer129の台帳が唯一。entry直下fallback_used=Trueでも、台帳がNOT_USEDならFallbackにしない(AI島Std型)。"""
    c = _clip("full_story_part1_k2", lr=("The AIs sent.", "The AI agents sent."))
    card = m._card(c, {"fallback_used": True, "canonical_text": "The AIs sent."})
    assert card["fb_state"] == "NOT_USED" and card["fb"] is None
    assert any("Fallbackとして表示しません" in x for x in card["history"])
    html = m.render_card(card)
    assert "fhr-fb-block" not in html and "Fallback 発動なし" in html
    src = open(SRC, encoding="utf-8").read()
    assert "er129.build_lr_ledger" in src
    assert "hashlib" not in src and "attempt_audio_sha" not in src   # attempt sha照合等の独自規則を持たない
    tree = ast.parse(src)
    names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert not names & {"resolve_adopted_take", "_derive_from_attempt_files", "classify_adopted_take"}


def test_build_model_uses_er129_ledger(monkeypatch, tmp_path):
    called = {}

    def fake(run_dir, level, **kw):
        called["args"] = (run_dir, level, kw.get("only_events"))
        return {"clips": [_clip("a", fb_state="USED", kind="FALLBACK_MINIMAL_EN", style_name="FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]")], "results_sha256": "x"}
    monkeypatch.setattr(e129, "build_lr_ledger", fake)
    monkeypatch.setattr(m, "load_entries", lambda *a, **k: {"a": {"text": "Hello there."}})
    model = m.build_model(str(tmp_path), "a2", "X")
    assert called["args"][2] is False          # 全clip(Role網羅)
    assert model["cards"][0]["fb_state"] == "USED"


def test_lr_red_and_plain_text_recovers_original():
    c = _clip("k2", lr=("The AIs sent to the island. It was fine.", "The AI agents sent to the island. It was fine."))
    card = m._card(c, {})
    html = m.render_card(card)
    assert 'class="fhr-lr-after">AI agents</span>' in html and 'class="fhr-lr-before">AIs</span>' in html
    assert "AIs → AI agents" in html and m.LABEL_LR_NOTE in html
    # 装飾を除いた素の本文は元の文と一致(装飾と実英文の混同なし)
    spans = [o["after_span"] for o in card["lr"]["ops"] if o["after_span"]]
    assert re.sub(r"<[^>]+>", "", m._spans_html(card["lr"]["after"], spans, "x")) == card["lr"]["after"]


def test_overlap_blue_block_contains_red_words_and_notes():
    c = _clip("full_story_part2_c3", fb_state="USED", kind="FALLBACK_MINIMAL_EN", style_name="FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]",
              lr=("Every guest got a cup.", "Every customer got a cup."))
    html = m.render_card(m._card(c, {}))
    blk = re.search(r'<div class="fhr-fb-block">(.*?)</div></div>', html, re.S) or re.search(r'<div class="fhr-fb-block">(.*)', html, re.S)
    assert blk and "fhr-lr-after" in blk.group(1)                       # 青区間内に赤語句
    assert m.STYLE_JA["FALLBACK_MINIMAL_EN"] in html and m.LABEL_FB_FROM in html and "範囲:" in html
    assert html.count(m.LABEL_FB_NOTE) == 1                              # 注記は1回(重複描画しない)
    assert m.LABEL_LR_NOTE in html


def test_unknown_take_is_kiroku_nashi_not_hatsudo_nashi_and_no_blue():
    c = _clip("full_story_part1_c10", fb_state="UNKNOWN", lr=("their guest left", "their visitor left"), warnings=["RECORD_INCOMPLETE:adopted_take"])
    card = m._card(c, {})
    html = m.render_card(card)
    assert "Fallback 記録なし" in html and "Fallback 発動なし" not in html and "fhr-fb-block" not in html
    assert "断定しません" in html


def test_style_record_conflict_is_text_warning_not_blue():
    c = _clip("y_voice_1", warnings=["STYLE_RECORD_CONFLICT:x"], source="human_approval")
    card = m._card(c, {"fallback_used": True, "canonical_text": "Hello."})
    html = m.render_card(card)
    assert "記録衝突(採用attemptはrole Style)" in html and "fhr-fb-block" not in html and "Fallback 発動なし" in html


def test_human_superseded_lr_is_not_red():
    c = _clip("y_voice_1")
    c["lr"] = {"before": "a redelivery.", "after": "a repeat delivery.", "adopted_in_final": False, "superseded_by_human": True, "reason": None, "source": "x"}
    card = m._card(c, {"canonical_text": "a redelivery."})
    html = m.render_card(card)
    assert "fhr-lr-after" not in html and "最終音声に反映なし" in html


def test_skipped_and_fixed_are_not_gaps():
    c = _clip("topic_intro")
    card = m._card(c, {"status": "SKIPPED_NOT_SELECTED"})
    assert card["fb_state"] == "SKIPPED" and not card["gaps"]
    fx = _clip("welcome", source="fixed_asset")
    card2 = m._card(fx, {})
    assert card2["fixed"] and "対象外(固定殻/固定MP3" in m.render_card(card2)


def test_legacy_family_fallback_presence_only_and_unreadable(tmp_path):
    lv = tmp_path / "a2" / "audit"
    lv.mkdir(parents=True)
    (lv / "tts_generation_results.json").write_text(json.dumps({"segments": {
        "s1": {"text": "Hi.", "attempts_log": [{"attempt": 1}], "fallback_used": True, "path": "x.wav"},
        "s2": {"text": "Yo.", "attempts_log": [{"attempt": 1}], "fallback_used": False, "path": "y.wav"},
        "s3": {"text": "No log.", "path": "z.wav"}}}), encoding="utf-8")
    model = m.build_model(str(tmp_path), "a2", "A")
    st = {c["id"]: c["fb_state"] for c in model["cards"]}
    assert st == {"s1": "USED", "s2": "NOT_USED", "s3": "UNREADABLE"}
    html = m.render_report(model, slug="legacy", run_name="r", date="2026-10-28")
    assert "Fallbackの有無のみ" in html and "表示不可" in html and "記録なし(既存Familyは有無のみ)" in html
    assert m.LABEL_LR_NOTE not in html and "LR 記録形式なし" in html


# ------------------------------------------------------------------ 混入防止 層1: 双方向AST import
def _imports(path):
    t = ast.parse(open(path, encoding="utf-8").read())
    out = set()
    for n in ast.walk(t):
        if isinstance(n, ast.Import):
            out |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module.split(".")[0])
    return out


def test_layer1_er131_imports_only_stdlib_and_er129():
    imps = _imports(SRC)
    local = {i for i in imps if os.path.exists(os.path.join(ROOT, i + ".py"))}
    assert local == {"er129_lr_display_reflection_01"}, local
    for i in imps:
        assert not any(i.startswith(p) for p in m.FORBIDDEN_IMPORT_PREFIXES), i


def test_layer1_no_other_module_imports_er131():
    offenders = []
    for p in glob.glob(os.path.join(ROOT, "*.py")):
        if os.path.basename(p).startswith("er131_final_human_report_01") or os.path.basename(p) in ("er133_report_marks_01.py", "er133_report_marks_01_test_01.py"):
            continue   # 委任_11: er133(試聴ページ共通表示部品)はer131のcard生成(_card/_spans_html)を部品として流用する唯一の利用者
        try:
            if "er131_final_human_report_01" in _imports(p):
                offenders.append(os.path.basename(p))
        except SyntaxError:
            continue
    assert offenders == []
    for p in glob.glob(os.path.join(ROOT, "tools", "*.py")):
        try:
            assert "er131_final_human_report_01" not in _imports(p)
        except SyntaxError:
            continue


def test_layer1_not_in_e2e_stages():
    for f in ("er026_family_z_production_e2e_01.py", "er121_family_y_runner_01.py"):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            assert "er131" not in open(p, encoding="utf-8").read()


# ------------------------------------------------------------------ 層2: run dir不変
def _tree_sha(d):
    h = {}
    for root, _dd, files in os.walk(d):
        for fn in files:
            p = os.path.join(root, fn)
            h[p] = (os.path.getsize(p), hashlib.sha256(open(p, "rb").read()).hexdigest())
    return h


def test_layer2_run_dir_unchanged_by_generation(tmp_path):
    _need(RUNS["ai"] + "/a2/audit/tts_generation_results.json")
    rd = os.path.join(ROOT, RUNS["ai"])
    keep = {k: v for k, v in _tree_sha(rd).items() if not k.lower().endswith((".wav", ".mp3"))}
    files = m.generate(rd, "X", out_root=str(tmp_path / "out"), slug="ai_island_temple", date="2026-10-28")
    assert len(files) == 2 and all(os.path.isfile(f) for f in files)
    after = {k: v for k, v in _tree_sha(rd).items() if not k.lower().endswith((".wav", ".mp3"))}
    assert keep == after


# ------------------------------------------------------------------ 層3: 出力先制約
@pytest.mark.parametrize("bad", ["user_test/x", "user_test/family_z_melos_02/y", "er019_output/a/b", "er026_output", "a/user_test/b"])
def test_layer3_out_dir_refused(bad, tmp_path):
    assert m.check_out_dir(os.path.join(ROOT, bad)) is not None
    with pytest.raises(PermissionError):
        m.generate(str(tmp_path), "X", out_root=os.path.join(ROOT, bad))


def test_layer3_run_dir_inside_refused_and_cli_rc(tmp_path):
    assert m.check_out_dir(str(tmp_path / "run" / "out"), str(tmp_path / "run")) is not None
    assert m.check_out_dir(os.path.join(ROOT, "final_human_report", "X", "s", "r"), str(tmp_path)) is None
    assert m.main(["--run", str(tmp_path), "--family", "X", "--out-root", os.path.join(ROOT, "user_test", "zz_fhr")]) == 2
    assert not os.path.exists(os.path.join(ROOT, "user_test", "zz_fhr"))


def test_layer3_public_indexes_do_not_link_report():
    for d in glob.glob(os.path.join(ROOT, "user_test", "*", "index.html")) + [os.path.join(ROOT, "user_test", "index.html")]:
        if os.path.exists(d):
            assert "final_human_report" not in open(d, encoding="utf-8", errors="replace").read(), d


# ------------------------------------------------------------------ 層4: 混入0件(保存run実測)
@pytest.mark.parametrize("key", ["ai", "tth", "wg", "melos", "paw", "y1"])
def test_layer4_no_fhr_tokens_in_tts_asr_style_kp_scripts(key):
    _need(RUNS[key] + "/a2")
    r = m.scan_run_contamination(os.path.join(ROOT, RUNS[key]))
    assert r["tts_input"][0] > 0 and r["asr_expected"][0] > 0                    # 走査対象が実在した
    assert r["hits"] == [], r["hits"][:3]


def test_layer4_no_fhr_tokens_in_public_html_and_check_spec():
    dirs = [os.path.join(ROOT, d) for d in PUBLIC if os.path.isdir(os.path.join(ROOT, d))]
    if not dirs:
        pytest.skip("no public html")
    r = m.scan_public_html(dirs)
    assert r["files"] > 0 and r["hits"] == [], r["hits"][:3]


def test_layer4_generated_report_would_fail_public_check_and_style_tokens_absent_from_source_texts():
    c = _clip("k2", fb_state="USED", kind="FALLBACK_MINIMAL_EN", lr=("a guest", "a visitor"))
    page = m.render_report({"family": "X", "level": "a2", "run_dir": "r", "cards": [m._card(c, {})], "parents_skipped": [], "legacy": False},
                           slug="s", run_name="r", date="2026-10-28")
    assert m.check_page_fhr_contamination(page)          # 公開pageに入ったら検査がNGにする
    assert m.check_page_fhr_contamination("<html><body><p>Hello</p></body></html>") == []
    assert "#c00000" in page and "#0a2a6b" in page and page.count("<!--FINAL_HUMAN_REPORT-->") == 1 and 'name="robots"' in page


# ------------------------------------------------------------------ 層5: check_page(public)追加検査仕様(配線は統合commit)
def test_layer5_check_spec_detects_each_token():
    for t in m.FHR_TOKENS:
        assert m.check_page_fhr_contamination(f"<p>{t}</p>")
    # 委任_15(B10) D5: 旧規則fhr_color_pair(赤+濃青の併存=NG)は撤去(試聴ページの赤/濃青表示=USER_02 §4と矛盾するため)
    assert m.check_page_fhr_contamination("<style>a{color:#c00000}b{color:#0a2a6b}</style>") == []


def test_b10_d5_listening_page_marks_pass_but_stray_notes_and_tokens_block():
    import er133_report_marks_01 as m133
    page = ("<html><body><div class='script'>Hello <span class='rpt-lr' style='color:#c00000'>x</span> <span class='rpt-fb' style='color:#0a2a6b'>y</span></div>"
            "<div class='rpt-notes'><div class='rpt-note rpt-note-fb' style='color:#0a2a6b'><b>Fallback 適用</b><br>適用Style: 英語短文Style(Minimal) / 切替元Style: ROLE</div>"
            "<div class='rpt-note rpt-note-lr'>Local Rewrite発動(最終採用音声に反映)</div></div><p>tail</p></body></html>")
    assert m.check_page_fhr_contamination(page) == []
    assert m.check_page_fhr_contamination(page.replace("<p>tail</p>", "<p>切替元Style: ROLE</p>")) == ["切替元Style:"]
    assert m.check_page_fhr_contamination(page.replace("Hello", "LR_APPLIED Hello"))
    assert m.check_page_fhr_contamination(page.replace("<p>tail</p>", "<p class='fhr-card'>t</p>"))
    assert m.check_page_fhr_contamination("<!--FINAL_HUMAN_REPORT-->" + page)
    assert m133.CLASS_NOTES == "rpt-notes"            # 除外対象classはer133の定数と同一


# ------------------------------------------------------------------ 保存run: 期待値は実測(委任文・W4 §3-3・B2 §3-5)
def _counts(model):
    return sum(1 for c in model["cards"] if c.get("lr") and c["lr"].get("applied")), sum(1 for c in model["cards"] if c["fb_state"] == "USED")


def test_real_ai_island_std_adv_lr_red_no_fallback():
    for lv, word in (("a2", "AI agents"), ("b1b", "AI systems")):
        mo = _model("ai", lv)
        assert _counts(mo) == (1, 0)
        c = _card(mo, "full_story_part1_k2")
        assert c["lr"]["ops"][0]["before_text"] == "AIs" and c["lr"]["ops"][0]["after_text"] == word and c["fb_state"] == "NOT_USED"
        assert f'fhr-lr-after">{word}</span>' in m.render_card(c)


def test_real_word_gacha_adv_lr_one():
    mo = _model("wg", "b1b")
    assert _counts(mo) == (1, 0)
    c = _card(mo, "full_story_part3")
    assert c["lr"]["ops"][0]["before_text"] == "you've" and "you have" in c["lr"]["ops"][0]["after_text"]


def test_real_melos_02_no_lr_no_fallback():
    assert _counts(_model("melos", "b1b")) == (0, 0)


def test_real_monkeys_paw_std_lr_and_fallback_unknown():
    mo = _model("paw", "a2")
    c = _card(mo, "full_story_part1_c10")
    assert c["lr"]["applied"] and c["lr"]["ops"][0]["before_text"] == "guest" and c["lr"]["ops"][0]["after_text"] == "visitor"
    assert c["fb_state"] == "UNKNOWN" and "Fallback 記録なし" in m.render_card(c)          # 採用take UNKNOWN=記録なし


def test_real_y_e1_human_approved_original_audio():
    for lv in ("a2", "b1b"):
        mo = _model("y1", lv)
        c = _card(mo, "y_voice_1")
        assert c["lr"]["superseded_by_human"] and not c["lr"]["applied"] and c["fb_state"] == "NOT_USED"
        assert _counts(mo) == (0, 0)
    c = _card(_model("y1", "a2"), "y_voice_1")
    assert "記録衝突(採用attemptはrole Style)" in m.render_card(c)


def test_real_tell_tale_heart_adv_kp2_english_lock_only():
    std, adv = _model("tth", "a2"), _model("tth", "b1b")
    assert _counts(std) == (0, 0) and _counts(adv) == (0, 1)
    c = _card(adv, "kp2_en")
    assert c["fb"]["kind"] == "ENGLISH_LOCK" and c["text"] == "mock" and "dcd08dca" in c["fb"]["style"]
    html = m.render_card(c)
    assert "fhr-fb-block" in html and "ENGLISH_LOCK" in html


def test_real_tru_ev_overlap_ja_and_z_dialogue():
    mo = _model("x16", "b1b")
    c = _card(mo, "in_one_line")
    assert c["lr"]["applied"] and c["fb_state"] == "USED"
    html = m.render_card(c)
    assert html.index("fhr-fb-block") < html.index("fhr-lr-after")                      # 青区間内に赤語句
    ja = _model("xja", "a2")
    fbs = [c for c in ja["cards"] if c["fb_state"] == "USED"]
    assert len(fbs) == 1 and "日本語短文Style(Minimal)" in fbs[0]["fb"]["style"]
    z = _model("zdlg", "b1b")
    fbz = [c for c in z["cards"] if c["fb_state"] == "USED"]
    assert len(fbz) == 1 and "従来Dialogue" in fbz[0]["fb"]["style"]
    skipped = [c for c in mo["cards"] if c["fb_state"] == "SKIPPED"]
    assert skipped and not any(c["gaps"] for c in skipped)


def test_generate_writes_standard_and_advanced_with_marker(tmp_path):
    _need(RUNS["tth"] + "/a2/audit/tts_generation_results.json")
    files = m.generate(os.path.join(ROOT, RUNS["tth"]), "Z", out_root=str(tmp_path), slug="the_tell_tale_heart", date="2026-10-28")
    names = sorted(os.path.basename(f) for f in files)
    assert names == ["advanced.html", "standard.html"]
    assert all("<!--FINAL_HUMAN_REPORT-->" in open(f, encoding="utf-8").read() for f in files)
    idx = m.write_index(str(tmp_path))
    assert "standard.html" in open(idx, encoding="utf-8").read()
