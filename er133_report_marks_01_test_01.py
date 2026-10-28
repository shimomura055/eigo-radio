# LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_11(B-wire): er133_report_marks_01(試聴ページの共通表示部品: ⏸/LR赤/Fallback濃青)のtest。
# API 0・費用JPY0。保存runは読み取りのみ(run dir不変)。ユーザー原文_02 §4・§5・§7: 表示は実際の記録と一致し、制作本文(textContent)・TTS入力には混入しない。
from __future__ import annotations

import html
import json
import os
import re
from html.parser import HTMLParser

import pytest

import er129_lr_display_reflection_01 as e129
import er132_lr_overlay_pages_01 as e132
import er133_report_marks_01 as m
import er_user_listening_page_common_01 as uc

ROOT = os.path.dirname(os.path.abspath(__file__))
AI = os.path.join(ROOT, "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01")
TTH = os.path.join(ROOT, "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01")
WG = os.path.join(ROOT, "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01")


def _need(p):
    if not os.path.isdir(p):
        pytest.skip(f"saved run absent: {p}")


class _Text(HTMLParser):
    """div.script(+chunk-markを除く)のtextContent、ならびにrpt-lr/rpt-fb/chunk-markの個数を集める。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.script, self.counts = [], [], {"lr": 0, "fb": 0, "mark": 0}
        self.cur = None
        self.lr_text, self.fb_text = [], []

    def handle_starttag(self, tag, attrs):
        cls = (dict(attrs).get("class") or "").split()
        self.stack.append((tag, cls))
        if tag == "div" and "script" in cls:
            self.cur = []
        if self.cur is None:     # div.script(台本本体)の中だけ数える(注記は台本の外)
            return
        if "rpt-lr" in cls:
            self.counts["lr"] += 1
        if "rpt-fb" in cls:
            self.counts["fb"] += 1
        if "chunk-mark" in cls:
            self.counts["mark"] += 1

    def handle_endtag(self, tag):
        while self.stack:
            t, cls = self.stack.pop()
            if t == "div" and "script" in cls and self.cur is not None:
                self.script.append(" ".join("".join(self.cur).split()))   # 空白を正規化(⏸の前の区切り空白は台本textContentの空白差。G3の_wsと同じ扱い)
                self.cur = None
            if t == tag:
                break

    def handle_data(self, data):
        in_mark = any("chunk-mark" in c for _t, c in self.stack)
        in_lr = any("rpt-lr" in c for _t, c in self.stack)
        in_fb = any("rpt-fb" in c for _t, c in self.stack)
        in_note = any("rpt-notes" in c for _t, c in self.stack)
        if self.cur is not None and not in_mark:
            self.cur.append(data)
            if in_lr:
                self.lr_text.append(data)
            if in_fb:
                self.fb_text.append(data)


def ws(t):
    return " ".join(t.split())


def parse(h):
    p = _Text()
    p.feed(h)
    return p


# ---------------------------------------------------------------- 描画部品(合成)
def card(cid, text, *, lr=None, fb=None):
    c = {"id": cid, "text": text, "chunk_parent": None, "lr": lr, "fb": fb, "fb_state": "USED" if fb else "NOT_USED", "fixed": False}
    c["_lr_on"], c["_fb_on"] = bool(lr and lr.get("applied")), bool(fb)
    return c


def lr_view(before, after):
    ops = e129.compute_ops(before, after)
    from er131_final_human_report_01 import _op_spans
    return {"before": before, "after": after, "ops": _op_spans(before, after, ops), "reason": "r", "applied": True}


FB = {"style": "ENGLISH_LOCK / ENGLISH_LOCK sha dcd08dca", "from": "通常Style(Role Style(9d905cfe))", "slot": 3, "range": "kp2_en", "human": False, "kind": "ENGLISH_LOCK"}


def test_no_events_means_no_marks_and_byte_identical_to_plain_script_block():
    assert m.marks_for({}, "Hello world.", ids=("x",)) is None
    assert uc.script_block("Hello <b> world.") == "<div class='script'>Hello &lt;b&gt; world.</div>"
    assert uc.script_block("Hello world.", marks=None) == uc.script_block("Hello world.")


def test_lr_red_only_on_changed_words_text_unchanged_and_before_after_in_notes():
    before, after = "The AIs sent to the island had no tasks.", "The AI agents sent to the island had no tasks."
    ev = {"c1": card("c1", after, lr=lr_view(before, after))}
    mk = m.marks_for(ev, after, ids=("c1",), whole=True)
    h = uc.script_block(after, marks=mk)
    p = parse(h)
    assert p.script == [ws(after)] and "".join(p.lr_text) == "AI agents" and p.counts["lr"] == 1 and p.counts["fb"] == 0
    assert "変更前" in h and "変更後" in h and "AIs" in h and "<span class='rpt-lr-before'" in h
    assert "Local Rewrite" in h and "この行の本文全体" in h
    assert "FALLBACK" not in h and "fhr-" not in h


def test_fallback_blue_on_whole_clip_with_style_and_range_note():
    text = "Hope is the thing with feathers."
    ev = {"kp2_en": card("kp2_en", text, fb=FB)}
    h = uc.script_block(text, marks=m.marks_for(ev, text, ids=("kp2_en",), whole=True))
    p = parse(h)
    assert p.script == [ws(text)] and "".join(p.fb_text) == text and p.counts["lr"] == 0
    assert "Fallback" in h and "ENGLISH_LOCK" in h and "Key Phrase 2 英語" in h and "切替元Style" in h


def test_lr_and_fallback_on_same_clip_show_red_inside_blue_with_separate_notes():
    before, after = "He saw the guest at the door.", "He saw the visitor at the door."
    ev = {"c1": card("c1", after, lr=lr_view(before, after), fb=dict(FB, style="英語短文Style(Minimal)"))}
    h = uc.script_block(after, marks=m.marks_for(ev, after, ids=("c1",), whole=True))
    p = parse(h)
    assert p.script == [ws(after)] and "".join(p.fb_text) == after and "".join(p.lr_text) == "visitor"
    assert h.count("rpt-note-lr") == 1 and h.count("rpt-note-fb") == 1             # 双方の変更内容と範囲を識別できる


def test_partial_fallback_in_multichunk_block_colors_only_that_chunk_and_boundary_marks_stay_outside():
    c1, c2, c3 = "First chunk sentence one.", "Second chunk sentence two.", "Third chunk sentence three."
    text = f"{c1} {c2} {c3}"
    ev = {"other_k2": card("other_k2", c2, fb=FB)}
    assert m.marks_for(ev, text, block="full_story_part1") is None   # blockは`<block>`そのもの・`<block>_k<N>`だけを選ぶ。別名は対象外
    ev = {"full_story_part1_k2": card("full_story_part1_k2", c2, fb=FB)}
    mk = m.marks_for(ev, text, block="full_story_part1")
    h = uc.script_block(text, [c1, c2, c3], marks=mk)
    p = parse(h)
    assert p.script == [ws(text)]                                       # ⏸と装飾はtextContentに影響しない
    assert "".join(p.fb_text) == c2 and p.counts["mark"] == 2       # chunk 3個=境界2か所にだけ⏸
    # ⏸はFallbackの青の外
    assert "rpt-fb" in h and re.search(r"</span> <span class='chunk-mark'>", h)
    assert "Full Story Part 1 の Chunk 2" in h and "本文中の該当箇所" in h


def test_unlocated_clip_gets_note_but_no_color_on_a_guessed_position():
    ev = {"c1": card("c1", "text that is not in the page", fb=FB)}
    mk = m.marks_for(ev, "completely different text", ids=("c1",))
    assert mk["blue"] == [] and mk["unlocated"] == ["c1"] and "特定できません" in mk["notes_html"]
    h = uc.script_block("completely different text", marks=mk)
    assert parse(h).counts["fb"] == 0


def test_highlight_tags_and_report_marks_coexist_text_content_unchanged():
    text = "Melos was angry. He ran to the city quickly today."
    s3 = text.index("the city")
    hls = [{"kind": 1, "start": 0, "end": 5, "candidate_id": "kpA", "surface": "Melos"}, {"kind": 3, "start": s3, "end": s3 + 8, "candidate_id": "kpB", "surface": "the city"}]
    h = uc.render_marked_script(text, hls, [17], " " + uc._CHUNK_MARKER_HTML, red=[(0, 5), (s3, s3 + 8)], blue=[(0, 17)])
    p = parse("<div class='script'>" + h + "</div>")
    assert p.script == [ws(text)] and p.counts["mark"] == 1 and p.counts["lr"] >= 2 and p.counts["fb"] >= 1
    assert 'data-hl="kpA"' in h and 'data-hl="kpB"' in h


# ---------------------------------------------------------------- 保存run(実データ)
def test_x_ai_island_lr_marks_match_ledger_and_do_not_touch_run_dir():
    _need(AI)
    before = {}
    for lv, new in (("a2", "AI agents"), ("b1b", "AI systems")):
        ev = m.load_events(AI, lv)
        assert list(ev) == ["full_story_part1_k2"] and ev["full_story_part1_k2"]["_lr_on"] and not ev["full_story_part1_k2"]["_fb_on"]   # LR記録のあるchunk(台帳)
        parts = json.load(open(os.path.join(AI, lv, "parts.json"), encoding="utf-8"))
        ledger = e132.level_ledger(AI, lv, level_dir=os.path.join(AI, lv))
        shown = e132.overlay_text(ledger, parts["part1"], source="parts.json:part1")
        mk = m.marks_for(ev, shown, block="full_story_part1")
        assert mk and mk["unlocated"] == [] and len(mk["red"]) == 1 and shown[mk["red"][0][0]:mk["red"][0][1]] == new and mk["blue"] == []
        h = uc.script_block(shown, marks=mk)
        assert parse(h).script == [ws(shown)] and "".join(parse(h).lr_text) == new
        assert "AIs" in mk["notes_html"] and "Local Rewrite" in mk["notes_html"]       # 変更前の英文も示す
    # 保存run不変(読み取りのみ)
    assert not [f for f in os.listdir(AI) if f.startswith("final_human_report")]


def test_z_tell_tale_heart_fallback_events_and_chunk_boundary_marks_match_records():
    _need(TTH)
    ev = m.load_events(TTH, "b1b")
    assert set(ev) == {"kp2_en"} and ev["kp2_en"]["_fb_on"] and ev["kp2_en"]["fb"]["kind"] == "ENGLISH_LOCK"
    ledger_a = e129.build_lr_ledger(TTH, "a2", only_events=True)       # 表示の元になる台帳そのもの(実記録)と、表示イベントの集合が一致する
    assert set(m.load_events(TTH, "a2")) == {c["clip_id"] for c in ledger_a["clips"] if (c.get("fallback") or {}).get("state") == "USED" or (c.get("lr") or {}).get("adopted_in_final")}
    # ⏸は実chunk planの境界だけ: part2_c1は2 chunk(境界1)、part3_c1も2 chunk(境界1)
    plans = uc.load_chunk_plans(os.path.join(TTH, "b1b", "audit", "chunk_plan_b1b.json"))
    for pid in ("full_story_part2_c1", "full_story_part3_c1"):
        cts = uc.chunk_texts_of_plan(plans[pid])
        assert len(cts) == 2
        h = uc.script_block(plans[pid]["parent_text"], cts)
        assert parse(h).counts["mark"] == 1 and parse(h).script == [ws(plans[pid]["parent_text"])]
    # chunk化していないclip(part1_c1)は⏸なし(chunk記録がないclip・Familyは表示なし)
    assert uc.chunk_texts_of_plan(plans.get("full_story_part1_c1")) == []


def test_word_gacha_adv_lr_you_have_is_red_in_overlaid_display():
    _need(WG)
    ev = m.load_events(WG, "b1b")
    assert ev, "Word Gacha AdvのLR記録(you've→you have)"
    assert list(ev) == ["full_story_part3"]
    cid = "full_story_part3"
    parts = json.load(open(os.path.join(WG, "b1b", "parts.json"), encoding="utf-8"))
    ledger = e132.level_ledger(WG, "b1b", level_dir=os.path.join(WG, "b1b"))
    shown = e132.overlay_text(ledger, parts["part3"], source="parts.json:part3")
    mk = m.marks_for(ev, shown, block=cid)
    assert mk and mk["unlocated"] == [] and len(mk["red"]) == 1 and shown[mk["red"][0][0]:mk["red"][0][1]] == "you have"   # 曲引用符・段落差があっても位置特定できる
    h = uc.script_block(shown, marks=mk)
    assert parse(h).script == [ws(shown)] and "".join(parse(h).lr_text) == "you have"


# ---------------------------------------------------------------- 混入防止(制作本文・TTS入力・Prompt)
def test_report_marks_never_enter_tts_inputs_asr_expected_or_style_prompts_of_saved_runs():
    import er131_final_human_report_01 as m131
    for r in (AI, TTH, WG):
        if not os.path.isdir(r):
            continue
        scan = m131.scan_run_contamination(r)                # TTS入力・ASR正解・Style Prompt・KP/study_text・本文(parts/support)
        assert scan["hits"] == [], scan["hits"][:3]
        for lv in ("a2", "b1b"):
            p = os.path.join(r, lv, "audit", "tts_generation_results.json")
            if os.path.exists(p):
                blob = open(p, encoding="utf-8").read()
                for tok in ("rpt-lr", "rpt-fb", "rpt-note", "chunk-mark", "&#9208;", "⏸"):
                    assert tok not in blob, (r, lv, tok)


def test_er133_reads_only_via_er129_ledger_and_er131_card_and_has_no_adopted_take_rules_of_its_own():
    src = open(os.path.join(ROOT, "er133_report_marks_01.py"), encoding="utf-8").read()
    assert "er129.build_lr_ledger" in src and "er131._card" in src
    assert "attempts_log" not in src and "resolve_adopted_take" not in src      # 独自の採用attempt規則を持たない
    for f in os.listdir(ROOT):
        if f.endswith(".py") and f.startswith(("er003_", "er078_", "er128_")):
            assert "er133_report_marks_01" not in open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read(), f   # TTS/ASR/KP表示はimportしない
