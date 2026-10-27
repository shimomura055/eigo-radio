# LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_07(Phase B / B0+B2): er129_lr_display_reflection_01(未配線の純module)のtest。
# W2 test計画 U1-U8 + Opus M-1〜M-6の再現ケース。API 0・費用JPY0・LLMなし。run dirは書き換えない(前後sha一致をtestで固定)。
# 保存データ(AI島・Y E-1・告げ口心臓等)に依存するtestは、データが無い環境ではskipする(合成ケースは常に実行)。
import hashlib
import json
import os

import pytest

import er129_lr_display_reflection_01 as m

ROOT = os.path.dirname(os.path.abspath(__file__))
AI = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01"


def _need(path):
    if not os.path.exists(os.path.join(ROOT, path)):
        pytest.skip(f"stored data not present: {path}")


# ------------------------------------------------------------------ U1 位置特定 / M-1 / M-2
def _op(before, after):
    ops = m.compute_ops(before, after)
    return ops, m._lw(before)


def test_u1_unique_hit_replace():
    before = "The AIs sent to the island had no set tasks. They were ready."
    after = "The AI agents sent to the island had no set tasks. They were ready."
    ops, lb = _op(before, after)
    assert len(ops) == 1 and ops[0]["kind"] == "replace"
    assert ops[0]["core_before_text"] == "AIs" and ops[0]["core_after_text"] == "AI agents"
    loc = m.locate_op("After a day. " + before + " The end.", ops[0], lb)
    assert loc["status"] == "OK" and loc["state"] == "BEFORE"


def test_u1_zero_hit_is_unlocatable_and_multiple_hit_is_ambiguous():
    before = "He looked at the AIs sent to the island."
    after = "He looked at the AI agents sent to the island."
    ops, lb = _op(before, after)
    assert m.locate_op("Completely different sentence here.", ops[0], lb)["status"] == "UNLOCATABLE"
    dup = before + " " + before   # 同一文が2回: k=4でも一意にならない
    assert m.locate_op(dup, ops[0], lb)["status"] == "AMBIGUOUS"


def test_u1_curly_quote_and_contraction_display_side_spelling_kept():
    before = "If you've felt tired, rest. Then go on."
    after = "If you have felt tired, rest. Then go on."
    ops, lb = _op(before, after)
    disp = "Intro. If you’ve felt tired, rest. Then go on."   # 表示側は曲アポストロフィ
    loc = m.locate_op(disp, ops[0], lb)
    assert loc["status"] == "OK"
    out = m.apply_overlay(disp, [(ops[0], loc["h"], loc["state"])])
    assert out == "Intro. If you have felt tired, rest. Then go on."


def test_u1_insert_and_delete_are_normalized_to_replace_not_stop():
    # M-2: LR 7 Gateは語の挿入・削除を許す。隣接一致語を取り込みreplaceへ正規化する
    b1, a1 = "The plan was a proposed 20% charge today.", "The plan was a 20% charge today."          # delete
    b2, a2 = "He took the road home alone.", "He took the long road home alone."                    # insert
    for b, a, kind in ((b1, a1, "delete"), (b2, a2, "insert")):
        ops, lb = _op(b, a)
        assert len(ops) == 1 and ops[0]["kind"] == kind
        assert ops[0]["before_tokens"] and ops[0]["after_tokens"] and ops[0]["before_tokens"] != ops[0]["after_tokens"]   # 隣接語を取り込みreplace化
        loc = m.locate_op("Lead sentence. " + b + " Tail sentence.", ops[0], lb)
        assert loc["status"] == "OK"
        out = m.apply_overlay("Lead sentence. " + b + " Tail sentence.", [(ops[0], loc["h"], loc["state"])])
        assert out == "Lead sentence. " + a + " Tail sentence."


def test_u1_punctuation_difference_does_not_stop():
    before = "So, let's start; it was early, and the AIs left."
    after = "So, let's start; it was early, and the AI agents left."
    ops, lb = _op(before, after)
    disp = "So let's start. It was early and the AIs left."     # 句読点が異なる表示側
    loc = m.locate_op(disp, ops[0], lb)
    assert loc["status"] == "OK"


def test_u1_tts_normalization_digit_words_do_not_cause_unlocatable():
    # M-1: LR before文はTTS正規化後(数字語化/数字化)、表示は正規化前。anchorが数字/数詞を含んでも数詞を数字へ寄せて一致させる
    before = "Act 2 brought an unexpected turn. The AIs left early."
    after = "Act 2 brought an unexpected turn. The AI agents left early."
    ops, lb = _op(before, after)
    disp = "Act Two brought an unexpected turn. The AIs left early."
    assert m.locate_op(disp, ops[0], lb)["status"] == "OK"
    # 人名発音置換のようにanchor語が表示側に無い場合は片側anchorへ縮退して位置特定する
    b2 = "Zhu-ee Smith said the AIs left."
    a2 = "Zhu-ee Smith said the AI agents left."
    ops2, lb2 = _op(b2, a2)
    assert m.locate_op("Xu Smith said the AIs left.", ops2[0], lb2)["status"] == "OK"


def test_u1_multiple_edits_apply_backwards():
    before = "The AIs left. Later the boss came. The AIs returned."
    after = "The AI agents left. Later the boss came. The AI agents returned."
    ops, lb = _op(before, after)
    assert len(ops) == 2
    disp = "Intro. " + before
    placed = []
    for o in ops:
        loc = m.locate_op(disp, o, lb)
        assert loc["status"] == "OK"
        placed.append((o, loc["h"], loc["state"]))
    assert m.apply_overlay(disp, placed) == "Intro. " + after


# ------------------------------------------------------------------ U2 overlay
def test_u2_empty_ops_is_byte_identical_and_overlay_idempotent():
    text = "Nothing changes here. Really."
    assert m.apply_overlay(text, []) == text
    before, after = "The AIs left.", "The AI agents left."
    ops, lb = _op(before, after)
    d1 = "Intro. " + before
    loc = m.locate_op(d1, ops[0], lb)
    once = m.apply_overlay(d1, [(ops[0], loc["h"], loc["state"])])
    loc2 = m.locate_op(once, ops[0], lb)          # 反映済み表示文: AFTER状態として検出され、再適用しても変わらない
    assert loc2["status"] == "OK" and loc2["state"] == "AFTER"
    assert m.apply_overlay(once, [(ops[0], loc2["h"], loc2["state"])]) == once


def test_u2_original_text_is_never_mutated_and_reverse_restores():
    before, after = "The AIs left.", "The AI agents left."
    ops, lb = _op(before, after)
    d1 = "Intro. " + before
    snap = d1
    loc = m.locate_op(d1, ops[0], lb)
    out = m.apply_overlay(d1, [(ops[0], loc["h"], loc["state"])])
    assert d1 == snap and out != d1
    assert out.replace("AI agents", "AIs") == d1


# ------------------------------------------------------------------ U3 4経路(合成entry)
def _x_entry(*, canonical, tts_text, rewritten, extra=None, **kw):
    e = {"status": "OK", "text": tts_text, "canonical_text": canonical, "canonical_text_before_local_rewrite": canonical,
         "local_rewrite_recovery": {"status": "RESOLVED_BY_LOCAL_REWRITE", "canonical_text": canonical,
                                    "selection": {"selected": {"id": "1", "rewritten_segment": rewritten, "changed_span_before": "AIs",
                                                               "changed_span_after": "AI agents", "rationale": "natural"}},
                                    "retts_result": {"text": tts_text}}}
    e.update(kw)
    e.update(extra or {})
    return e


def _mk_level(tmp_path, entries, parts=None, sel=None):
    lv = tmp_path / "run" / "a2"
    (lv / "audit").mkdir(parents=True)
    (lv / "audit" / "tts_generation_results.json").write_text(json.dumps({"segments": entries}), encoding="utf-8")
    if parts is not None:
        (lv / "parts.json").write_text(json.dumps(parts), encoding="utf-8")
    if sel is not None:
        (lv / "audit" / "confirmed_selection.json").write_text(json.dumps(sel), encoding="utf-8")
    return str(tmp_path / "run"), "a2"


CANON = "The AIs sent to the island had no tasks. They were ready to explore."
REWR = "The AI agents sent to the island had no tasks. They were ready to explore."
PARTS = {"part1": "Intro sentence here. " + CANON + " Closing line of the part."}


def test_u3a_initial_route_x_form(tmp_path):
    run, lv = _mk_level(tmp_path, {"full_story_part1_k2": _x_entry(canonical=CANON, tts_text=REWR, rewritten=REWR,
                                                                  chunk_tts={"parent_id": "full_story_part1"})}, PARTS)
    L = m.build_lr_ledger(run, lv)
    c = L["clips"][0]
    assert c["verdict"] == m.V_PASS and c["changed_spans"][0]["after"] == "AI agents"
    assert "AI agents" in c["_display_after"] and c["display"]["source"] == "parts.json:part1"
    assert c["lr"]["reason"] == "natural" and c["lr"]["adopted_in_final"] is True


def test_u3b_resume_form_rewritten_segment_only(tmp_path):
    # M-4 resume形: `rewritten_segment`のみ(changed_span・rationale・7 gateなし)。差分は記録でなくbefore/afterのトークンから再計算する
    e = {"status": "OK", "text": REWR, "canonical_text": CANON, "canonical_text_before_local_rewrite": CANON,
         "local_rewrite_recovery": {"status": "RESOLVED_BY_LOCAL_REWRITE", "resumed_without_llm": True,
                                    "selection": {"selected": {"rewritten_segment": REWR}}}}
    run, lv = _mk_level(tmp_path, {"seg": e}, {"part1": PARTS["part1"]})
    c = m.build_lr_ledger(run, lv)["clips"][0]
    assert c["verdict"] == m.V_PASS
    assert c["changed_spans"][0]["before"] == "AIs" and c["changed_spans"][0]["after"] == "AI agents"
    assert "LR_REASON_UNAVAILABLE" in c["warnings"] and c["lr"]["source"].startswith("resumed")


def test_u3c_human_approval_restores_original_no_overlay(tmp_path):
    e = _x_entry(canonical=CANON, tts_text=CANON, rewritten=REWR, extra={m.er020.HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG: True,
                                                                         "adopted_attempt_audio_path": "nonexistent/a_attempt5.wav"})
    run, lv = _mk_level(tmp_path, {"seg": e}, {"part1": PARTS["part1"]})
    c = m.build_lr_ledger(run, lv)["clips"][0]
    assert c["verdict"] == m.V_PASS_SUPERSEDED and c["lr"]["adopted_in_final"] is False
    assert c["lr"]["superseded_by_human"] is True and c["changed_spans"] == []
    assert "_display_after" not in c                                  # 表示は原文のまま
    # ASR正解の参照点はer020.resolve_expected_text_after_local_rewrite(原文を返す)
    assert m.er020.resolve_expected_text_after_local_rewrite(e, CANON)[0] == CANON


def test_u3d_z_form_audio_text_after_is_tts_input(tmp_path):
    canon = "his friend warned. After their guest left, Herbert joked,"
    after = "his friend warned. After their visitor left, Herbert joked,"
    e = {"status": "OK", "text": canon, "canonical_text": canon,        # Z: entry["text"]は表示形。TTS入力=audio_text_after
         "audio_text_deviation": {"canonical_text_before_local_rewrite": canon, "audio_text_after": after, "diff_summary": "replace: 'guest' -> 'visitor'"}}
    run, lv = _mk_level(tmp_path, {"full_story_part1_c10": e})
    c = m.build_lr_ledger(run, lv)["clips"][0]
    assert c["verdict"] == m.V_PASS and c["display"]["source"] == "entry.canonical_text"
    assert c["changed_spans"][0]["after"] == "visitor" and c["lr"]["source"] == "audio_text_deviation"


def test_u3e_without_final_adoption_still_works_and_unknown_is_not_a_stop_of_lr_location(tmp_path):
    # final_adoption(委任_06)が無い旧entry: 採用take不明でもLR位置特定・三者一致は成立し、take=UNKNOWNは別項目の警告として出る
    run, lv = _mk_level(tmp_path, {"seg": _x_entry(canonical=CANON, tts_text=REWR, rewritten=REWR)}, {"part1": PARTS["part1"]})
    c = m.build_lr_ledger(run, lv)["clips"][0]
    assert c["verdict"] == m.V_PASS
    assert c["adopted_take"] is None and c["fallback"]["state"] == "UNKNOWN" and "RECORD_INCOMPLETE:adopted_take" in c["warnings"]


def test_u3f_unlocatable_display_is_stop_verdict_not_exception(tmp_path):
    run, lv = _mk_level(tmp_path, {"seg": _x_entry(canonical=CANON, tts_text=REWR, rewritten=REWR, canonical_text_is_other=1)},
                        {"part1": "Totally unrelated display text."})
    e = json.loads((tmp_path / "run" / "a2" / "audit" / "tts_generation_results.json").read_text(encoding="utf-8"))
    e["segments"]["seg"]["canonical_text"] = "Another unrelated canonical text."
    (tmp_path / "run" / "a2" / "audit" / "tts_generation_results.json").write_text(json.dumps(e), encoding="utf-8")
    c = m.build_lr_ledger(run, lv)["clips"][0]
    assert c["verdict"] == m.V_UNLOCATABLE


# ------------------------------------------------------------------ U4 三者一致
def test_u4_parity_pass_and_injected_mismatches():
    disp = "Intro. " + REWR + " End."
    ok = m.check_text_parity(disp, REWR, REWR, [m._lw("AI agents")])
    assert ok["verdict"] == "PASS"
    # 表示を旧文へ戻す(overlay漏れ)→ V2不一致
    old = m.check_text_parity("Intro. " + CANON + " End.", REWR, REWR, [m._lw("AI agents")])
    assert old["verdict"] == "MISMATCH_V2"
    # TTS入力を差替え(別文) → V3不一致
    v3 = m.check_text_parity(disp, "Something else entirely. Nothing alike here at all.", REWR, [m._lw("AI agents")])
    assert v3["verdict"] == "MISMATCH_V3"
    # ASR正解が旧文(resolverが原文を返す異常) → V3不一致
    assert m.check_text_parity(disp, REWR, CANON, [m._lw("AI agents")])["verdict"] in ("MISMATCH_V3", "MISMATCH_V1", "MISMATCH_V2")


def test_u4_tts_normalization_difference_outside_lr_sentence_is_pass_normalized():
    disp = "Costs rose 20%. The AI agents left. Done today."
    tts = "Costs rose twenty percent now. The AI agents left. Done today."
    r = m.check_text_parity(disp, tts, tts, [m._lw("AI agents")])
    assert r["verdict"] in ("PASS", "PASS_NORMALIZED")
    # LR変更文の側が欠落している場合は許さない
    bad = m.check_text_parity("Costs rose 20%. The AIs left. Done today.", "Costs rose 20%. The AI agents left. Done today.",
                              "Costs rose 20%. The AI agents left. Done today.", [m._lw("AI agents")])
    assert bad["verdict"].startswith("MISMATCH")


# ------------------------------------------------------------------ U5 / M-3 / M-6 重なり
def _clip_for_overlap(before, after):
    ops = m.compute_ops(before, after)
    return {"lr": {"before": before, "after": after, "adopted_in_final": True}, "_ops": ops}


def test_u5_t1_phrase_overlap_recomputed_as_pure_function():
    before = "The mayor made an initial proposal for a plan. Then he left."
    after = "The mayor made an early proposal for a plan. Then he left."
    sel = {"items": [{"candidate_id": "p1", "display_phrase": "initial proposal", "used_form": "initial proposal", "key_phrase": "initial proposal"}]}
    ov = m.check_confirmed_overlap(_clip_for_overlap(before, after), sel, None, {"level_text": before})
    assert ov["T1"]["status"] == "STOP" and ov["T1"]["hits"][0]["candidate_id"] == "p1"
    # 重なりが無い確定項目ではPASS
    sel2 = {"items": [{"candidate_id": "p2", "display_phrase": "then he left", "used_form": "then he left", "key_phrase": "then he left"}]}
    ov2 = m.check_confirmed_overlap(_clip_for_overlap(before, after), sel2, None, {"level_text": before})
    assert ov2["T1"]["status"] == "PASS"


def test_u5_t2_is_one_sentence_not_whole_segment():
    # M-6: T2の「変更文」=変更箇所を含む1文。segment全体で比べると同一segment内の他文の確定項目で常時STOPになってしまう
    before = "The AIs left early today. A different sentence has the phrase carry over inside it. Final line."
    after = "The AI agents left early today. A different sentence has the phrase carry over inside it. Final line."
    sel = {"items": [{"candidate_id": "p9", "display_phrase": "carry over", "used_form": "carry over", "key_phrase": "carry over",
                      "source_sentence": "A different sentence has the phrase carry over inside it."}]}
    ov = m.check_confirmed_overlap(_clip_for_overlap(before, after), sel, None, {"level_text": before})
    assert ov["T2"]["status"] == "PASS"                                  # 変更文(1文目)は確定項目の出典文ではない
    sel2 = {"items": [{"candidate_id": "p8", "display_phrase": "left early", "used_form": "left early", "key_phrase": "left early",
                       "source_sentence": "The AIs left early today."}]}
    ov2 = m.check_confirmed_overlap(_clip_for_overlap(before, after), sel2, None, {"level_text": before})
    assert ov2["T2"]["status"] == "STOP"                                 # 変更文が確定項目の出典文
    ov3 = m.check_confirmed_overlap(_clip_for_overlap(before, after), {"items": []}, ["The AIs left early today."], {"level_text": before})
    assert ov3["T1"]["status"] == "SKIPPED"                              # 確定項目なし(未確定)はT1-T2とも判定対象外=偽STOPにしない


def test_u5_t3_numbers_judged_on_display_side_text_and_entities():
    # M-6: T3は表示側(正規化前)テキストで判定。TTS正規化後は数字が語化され見逃す
    ov = m.check_confirmed_overlap(_clip_for_overlap("The fee was 20% last year.", "The fee was 30% last year."), {"items": [{"candidate_id": "x", "display_phrase": "zzz", "used_form": "zzz", "key_phrase": "zzz"}]}, None, {"level_text": ""})
    assert ov["T3"]["status"] == "STOP" and ov["T3"]["numbers"]
    ent = m.check_confirmed_overlap(_clip_for_overlap("Water came. Melos drank deeply.", "Water came. He drank deeply."), {"items": [{"candidate_id": "x", "display_phrase": "zzz", "used_form": "zzz", "key_phrase": "zzz"}]}, None,
                                    {"entities": ["Melos"], "level_text": "Melos ran. Melos fell. Water came. He drank deeply."})
    assert ent["T3"]["status"] == "PASS" and "entity_pronoun_substitution" in ent["T3"]["flags"]    # 全文に残る人名: PASS+flag
    gone = m.check_confirmed_overlap(_clip_for_overlap("Water came. Melos drank deeply.", "Water came. He drank deeply."), {"items": [{"candidate_id": "x", "display_phrase": "zzz", "used_form": "zzz", "key_phrase": "zzz"}]}, None,
                                     {"entities": ["Melos"], "level_text": "Water came. He drank deeply."})
    assert gone["T3"]["status"] == "STOP"                                                        # 全文から消える: STOP
    nofact = m.check_confirmed_overlap(_clip_for_overlap("Water came. Melos drank deeply.", "Water came. He drank deeply."), None, None, None)
    assert nofact["T3"].get("entity_check") == "SKIPPED_NO_FACT_TABLE" and nofact["T3"]["status"] == "PASS"   # 偽STOPにしない


# ------------------------------------------------------------------ U6 採用take解決
def test_u6_priority_human_over_everything():
    e = {"status": "OK", m.er020.HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG: True, "adopted_attempt_audio_path": "none/x_attempt5.wav",
         "final_adoption": {"style_mode": "FALLBACK", "depth": 0, "ordinal": 1, "source": "tts_attempt"}, "reused": True}
    t = m.resolve_adopted_take(e, None, None, seg_id="s")
    assert t["source"] == "human_approval" and t["human_superseded_lr"] is True


def test_u6_store_reuse_and_final_adoption_and_mismatch():
    reuse = {"status": "OK", "reused": True, "final_adoption": {"source": "store_reuse", "style_mode": "FALLBACK", "depth": 0, "ordinal": None,
                                                                "sent_style_sha": m.ENGLISH_LOCK_STYLE_SHA, "style_name": "ENGLISH_LOCK"}}
    t = m.resolve_adopted_take(reuse, None, None, seg_id="kp2_en")
    assert t["source"] == "store_reuse" and t["kind"] == m.KIND_ENGLISH_LOCK
    fa = {"status": "OK", "language": "en", "final_adoption": {"depth": 0, "ordinal": 3, "slot": "③", "style_mode": "FALLBACK",
                                                               "sent_style_sha": "a" * 64, "attempt_audio_sha": "b" * 64, "source": "tts_attempt"}}
    bp_ok = {"blocks": {"0": {"attempts": {"3": {"verified": True}}}}}
    bp_bad = {"blocks": {"0": {"attempts": {"3": {"verified": False}}}}}
    t_ok = m.resolve_adopted_take(fa, bp_ok, None, seg_id="comment_1")
    assert t_ok["source"] == "final_adoption" and t_ok["status"] == "OK" and t_ok["kind"] == m.KIND_MINIMAL_EN
    t_bad = m.resolve_adopted_take(fa, bp_bad, None, seg_id="comment_1")
    assert t_bad["status"] == m.V_RECORD_MISMATCH
    # BlockProgressが無い/旧形(block欠落)は突合不能として通す(記録欠落でなくnote)
    assert m.resolve_adopted_take(fa, None, None, seg_id="comment_1")["status"] == "OK"
    assert m.resolve_adopted_take(fa, {"blocks": {}}, None, seg_id="comment_1")["status"] == "OK"


def test_u6_old_records_kp_en_fallback_log_naming_inversion_not_read():
    # W1 DR-6: KP_ENのfallback_attempts_logは前段(命名逆転)。ENGLISH_LOCK段(english_lock_attempts_log)だけを採用根拠にする
    e = {"status": "OK", "fallback_used": True, "fallback_attempts_log": [{"attempt": 1, "verified": True}],
         "english_lock_attempts_log": [{"attempt": 1, "verified": False}, {"attempt": 2, "verified": True}]}
    t = m.resolve_adopted_take(e, None, None, seg_id="kp1_en")
    assert t["kind"] == m.KIND_ENGLISH_LOCK and t["how"] == "english_lock_attempts_log.verified"
    no_lock = {"status": "OK", "fallback_used": True, "fallback_attempts_log": [{"attempt": 1, "verified": True}]}
    assert m.is_unknown(m.resolve_adopted_take(no_lock, None, None, seg_id="kp1_en"))


def test_u6_unknown_not_adopted_fixed_asset_and_dialogue():
    assert m.is_unknown(m.resolve_adopted_take({"status": "OK", "fallback_used": True}, None, None, seg_id="comment_1"))
    na = m.resolve_adopted_take({"status": "STOPPED", "fallback_attempts_log": [{"verified": False}]}, None, None, seg_id="x")
    assert na["status"] == "NOT_ADOPTED" and not m.is_unknown(na)
    fixed = m.resolve_adopted_take({"status": "OK", "reused": True, "tts_backend": "existing_master", "style": {"fallback_used": False}}, None, None, seg_id="welcome")
    assert fixed["kind"] == m.KIND_NORMAL and fixed["source"] == "fixed_asset"
    dlg = m.resolve_adopted_take({"status": "OK", "dialogue_tts": {"policy": "fz_ctx_v1", "final_mode": "legacy_fallback", "final_attempt_n": 3}}, None, None, seg_id="c2")
    assert dlg["kind"] == m.KIND_LEGACY_DIALOGUE
    same = m.resolve_adopted_take({"status": "OK", "dialogue_tts": {"policy": "legacy", "final_mode": "legacy_fallback", "final_attempt_n": 3}}, None, None, seg_id="c2")
    assert same["kind"] == m.KIND_NORMAL           # Style不変の再試行はFallback表示しない(原文6-B)


def test_u6_same_style_retry_is_not_fallback_via_attempt_json(tmp_path):
    d = tmp_path / "narration"
    (d / "attempts").mkdir(parents=True)
    wav = d / "seg.wav"
    wav.write_bytes(b"RIFFfake-audio")
    sha = hashlib.sha256(b"RIFFfake-audio").hexdigest()
    instr = "calm voice"
    (d / "attempts" / "seg_attempt3_minimalfallback.json").write_text(json.dumps(
        {"attempt_number": 3, "route": "minimal_fallback", "sha256": sha, "instruction_text": instr}), encoding="utf-8")
    e = {"status": "OK", "path": str(wav), "sha256": sha,
         "style_profile": {"expected_base_sha256": hashlib.sha256(instr.encode()).hexdigest()}}
    t = m.resolve_adopted_take(e, None, None, seg_id="seg")
    assert t["how"] == "attempt_file_sha_match" and t["kind"] == m.KIND_NORMAL   # sha一致=Styleが変わらない
    e2 = dict(e, style_profile={"expected_base_sha256": "0" * 64})
    assert m.resolve_adopted_take(e2, None, None, seg_id="seg")["kind"] == m.KIND_MINIMAL_EN


def test_u6_english_lock_constant_matches_production_constant():
    try:
        import er003_v1_repro01_main_generate as repro01
    except Exception:   # noqa: BLE001
        pytest.skip("repro01 not importable")
    assert hashlib.sha256(repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION.encode("utf-8")).hexdigest() == m.ENGLISH_LOCK_STYLE_SHA


# ------------------------------------------------------------------ U7 run dirを書き換えない / U8 純module
def _tree_sha(base):
    h = hashlib.sha256()
    for dp, dn, fn in sorted(os.walk(base)):
        dn.sort()
        for f in sorted(fn):
            p = os.path.join(dp, f)
            h.update(os.path.relpath(p, base).encode())
            h.update(m._file_sha(p).encode())
    return h.hexdigest()


def test_u7_run_dir_is_not_modified_by_ledger_derivation():
    _need(AI + "/a2/audit/tts_generation_results.json")
    # narration配下(wav)は巨大なので、audit配下+parts.json+support textsを対象にshaを固定する
    def snap():
        out = {}
        for lv in ("a2", "b1b"):
            for rel in ("parts.json", "audit"):
                p = os.path.join(ROOT, AI, lv, rel)
                out[(lv, rel)] = _tree_sha(p) if os.path.isdir(p) else m._file_sha(p)
        return out
    before = snap()
    for lv in ("a2", "b1b"):
        m.build_lr_ledger(os.path.join(ROOT, AI), lv)
    assert snap() == before


def test_u8_no_production_module_imports_er129():
    # 未配線(既定動作不変): Production/他moduleからimportされていない
    offenders = []
    for f in os.listdir(ROOT):
        if f.endswith(".py") and f not in ("er129_lr_display_reflection_01.py", "er129_lr_display_reflection_01_test_01.py", "er130_adopted_take_classifier_01.py", "er130_adopted_take_classifier_01_test_01.py"):
            try:
                with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
                    if "er129_lr_display_reflection_01" in fh.read():
                        offenders.append(f)
            except OSError:
                pass
    assert offenders == []


def test_u8_audit_output_strips_internal_keys_and_is_deterministic(tmp_path):
    run, lv = _mk_level(tmp_path, {"seg": _x_entry(canonical=CANON, tts_text=REWR, rewritten=REWR)}, {"part1": PARTS["part1"]})
    L = m.build_lr_ledger(run, lv)
    p1 = m.write_ledger_audit(L, str(tmp_path / "out" / "a.json"))
    p2 = m.write_ledger_audit(m.build_lr_ledger(run, lv), str(tmp_path / "out" / "b.json"))
    d = json.loads(open(p1, encoding="utf-8").read())
    assert "_display_after" not in json.dumps(d) and "_ops" not in json.dumps(d)
    assert open(p1, encoding="utf-8").read() == open(p2, encoding="utf-8").read()


# ------------------------------------------------------------------ 実データ(保存LR entry)
def test_real_ai_island_derives_ai_agents_and_ai_systems():
    # R-7: AI島Std/AdvでLR記録から`AI agents`/`AI systems`が(特別扱いコードなしで)自動導出される
    _need(AI + "/a2/audit/tts_generation_results.json")
    for lv, exp in (("a2", "AI agents"), ("b1b", "AI systems")):
        L = m.build_lr_ledger(os.path.join(ROOT, AI), lv)
        c = [x for x in L["clips"] if x["clip_id"] == "full_story_part1_k2"][0]
        assert c["verdict"] == m.V_PASS and c["changed_spans"][0] == {**c["changed_spans"][0], "before": "AIs", "after": exp}
        assert exp in c["_display_after"]
        # Fallback表示は誤らない: 最終採用=LRブロックの通常Style(未採用の元③をFallbackと表示しない)
        assert c["fallback"]["state"] == "NOT_USED" and c["adopted_take"]["how"] == "attempt_file_sha_match"
        assert c["overlap"]["T1"]["status"] == "PASS" and c["overlap"]["T2"]["status"] == "PASS" and c["overlap"]["T3"]["status"] == "PASS"


def test_real_tell_tale_heart_adv_kp2_en_is_english_lock():
    p = "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01"
    _need(p + "/b1b/audit/tts_generation_results.json")
    L = m.build_lr_ledger(os.path.join(ROOT, p), "b1b")
    c = [x for x in L["clips"] if x["clip_id"] == "kp2_en"][0]
    assert c["fallback"]["state"] == "USED" and c["fallback"]["adopted_style"] == "ENGLISH_LOCK"    # Zの既存style_actualはK2と誤同定していた


def test_real_y_e1_human_adopted_attempt_is_role_style_with_record_conflict_warning():
    p = "er121_output/family_y_production_01/redelivery_fee/run_01"
    _need(p + "/a2/audit/tts_generation_results.json")
    c = m.build_lr_ledger(os.path.join(ROOT, p), "a2")["clips"]
    c = [x for x in c if x["clip_id"] == "y_voice_1"][0]
    assert c["verdict"] == m.V_PASS_SUPERSEDED and c["lr"]["adopted_in_final"] is False and c["adopted_take"]["source"] == "human_approval"
    assert c["adopted_take"]["how"] == "human_attempt_file"


STORED = [
    "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/a2",
    "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/b1b",
    "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/b1b",
    "er026_output/family_z_production_e2e_01/melos/run_e2e_02/b1b",
    "er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/a2",
    "er121_output/family_y_production_01/redelivery_fee/run_01/a2",
    "er121_output/family_y_production_01/redelivery_fee/run_01/b1b",
]


@pytest.mark.parametrize("lvdir", STORED)
def test_real_stored_lr_entries_have_no_false_stop(lvdir):
    _need(lvdir + "/audit/tts_generation_results.json")
    L = m.build_lr_ledger("", "", results_path=lvdir + "/audit/tts_generation_results.json")
    lr_clips = [c for c in L["clips"] if c.get("lr")]
    assert lr_clips
    for c in lr_clips:
        assert c["verdict"] in (m.V_PASS, m.V_PASS_SUPERSEDED), (lvdir, c["clip_id"], c["verdict"], c.get("display"), c.get("text_parity"))
