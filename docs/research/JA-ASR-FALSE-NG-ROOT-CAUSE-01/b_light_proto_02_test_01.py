# b_light_proto_02 のtest (DEV/API 0)。再現: PYTHONUTF8=1 .venv/Scripts/python.exe -m pytest docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/b_light_proto_02_test_01.py -q
# v1 test の基準は緩めず全件引き継ぎ + M-3(複数atom)/F-B・Secondary表記の負例/R-1/R-3/R-4/R-7/R-8/M-2 を追加。
import glob, os, socket, sys
import pytest

sys.path.insert(0, ".")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b_light_proto_02 as B

META = {"engine": "azure", "wav_sha256": "deadbeef", "model_id": "azure-stt-test"}
C = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
TAIL = "。その奥に潜む岩の上着の秘密。"
S_OK = "杉野氏は8900本超" + TAIL            # 値は正しいが読み(杉野)は原稿と違う Azure 実転写
S_WELL = "月の詩は8900本超" + TAIL
C2 = "売上は1,200円で利益は3,500円です"
S2 = "売上は1200円で利益は3500円です"


@pytest.fixture(autouse=True)
def _no_net(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("API0 violation")
    monkeypatch.setattr(socket.socket, "connect", boom)


def j(c, p, s, **k):
    return B.composite_judge(c, p, s, META, **k)


# ---- 救済(正例): 月題の実転写 ----
def test_moon_garble_digit_split_with_reading_ok_is_rescued():
    r = j(C, "月の氏は8000900本超" + TAIL, S_OK)
    assert r.equal and r.label == B.COMPOSITE_LABEL
    assert B.W_FROM_SECONDARY in r.warnings and B.W_GARBLE_EXPLAINED in r.warnings


def test_moon_garble_digit_plus_kanji_is_rescued():
    r = j(C, "月のシワ、8000九百本超" + TAIL, S_OK)
    assert r.equal and B.W_GARBLE_EXPLAINED in r.warnings


def test_alpha_mode_does_not_rescue_garble():
    r = j(C, "月の氏は8000900本超" + TAIL, S_OK, allow_explained_garble=False)
    assert not r.equal and r.blocked_by == "primary_secondary_value_contradiction" and r.protected


@pytest.mark.parametrize("p", [
    "月のしわ、89,000本超" + TAIL, "月のしわ、89000本超" + TAIL, "月のしわ、八万九千本超" + TAIL, "月のしわ、8万9千本超" + TAIL,
    "月のしわ、8800本超" + TAIL, "月のしわ、千九百本超" + TAIL, "月野詩は8000句800本超え" + TAIL,
])
def test_value_contradiction_is_not_rescued_even_if_secondary_equals_script(p):
    r = j(C, p, S_OK)
    assert not r.equal and r.protected, (p, r.why)


@pytest.mark.parametrize("p", ["月のすわ、8000900本超" + TAIL, "月の巣は8000900本超" + TAIL, "月のしば、8000900本超" + TAIL,
                               "月のし、8000900本超" + TAIL, "月のしわし、8000900本超" + TAIL])
def test_reading_difference_is_not_rescued(p):
    r = j(C, p, S_OK)
    assert not r.equal and r.blocked_by == "primary_reading", (p, r.why)


@pytest.mark.parametrize("c,p,s", [
    ("三日待った", "三日間待った。", "3日待った。"), ("三日待った", "3日待った", "3日待った"),
    ("二十歳になった", "20歳になった", "20歳になった"), ("十月一日に会う", "10月1日に会う", "10月1日に会う"),
])
def test_irregular_reading_values_are_excluded(c, p, s):
    r = j(c, p, s)
    assert not r.equal and r.blocked_by == "A4a_irregular_reading"


def test_secondary_only_correct_primary_reading_wrong_is_not_rescued():
    r = j(C, "月野詩は8,900本超え" + TAIL, S_WELL)
    assert not r.equal and r.blocked_by == "primary_reading"


def test_primary_only_correct_secondary_value_wrong_is_not_rescued():
    r = j(C, "月のしわ、8,900本超" + TAIL, "月のしわ、8800本超" + TAIL)
    assert not r.equal and r.blocked_by == "secondary_value" and r.protected


def test_both_wrong_is_not_rescued():
    assert not j(C, "月のしわ、8800本超" + TAIL, "月のしわ、8800本超" + TAIL).equal


def test_primary_8800_secondary_8900_is_contradiction():
    r = j(C, "月のしわ、8800本超" + TAIL, S_OK)
    assert not r.equal and r.blocked_by == "primary_secondary_value_contradiction"


def test_negation_difference_blocks():
    assert not j("三人は行かない", "3人は行く", "3人は行かない").equal
    assert not j("彼女は来ない", "彼女は来る", "彼女は来ない").equal


def test_secondary_empty_or_none_blocks():
    assert j(C, "月の氏は8000900本超" + TAIL, None).blocked_by == "secondary_unavailable"
    assert j(C, "月の氏は8000900本超" + TAIL, "  ").blocked_by == "secondary_unavailable"


def test_primary_missing_numeric_run_blocks():
    r = j(C, "月の氏は本超" + TAIL, S_OK)
    assert not r.equal and r.blocked_by == "primary_value_missing"


def test_unit_mismatch_blocks():
    assert not j(C, "月の氏は8000900冊超" + TAIL, S_OK).equal


def test_comma_formatted_primary_number_is_not_explained():
    assert B.explain_garble("8,000,900", 8900) is None


def test_no_value_atoms_is_not_applicable():
    r = j("月のしわが多い", "月の詩が多い", "月のしわが多い")
    assert not r.equal and r.blocked_by == "not_applicable"


def test_primary_value_equal_and_reading_ok_is_composite_pass():
    r = j(C, "月野氏は八千九百本超、その奥に潜む岩の上着の秘密。", S_OK)
    assert r.equal and B.W_GARBLE_EXPLAINED not in r.warnings


# ---- R-3: 断片説明は観測形に限定 ----
@pytest.mark.parametrize("run,target,ok", [
    ("8000900", 8900, True), ("8000九百", 8900, True), ("8000800", 8900, False), ("89000", 8900, False),
    ("0900", 900, False), ("8900", 8900, False), ("80", 8900, False), ("1200300", 1500, False), ("1000500", 1500, True),
    ("1000200", 1200, True), ("9000", 8900, False),
    # R-3 追加: 前断片は d*10^k のみ(12000|300 は不可)、3断片は不可、前断片が漢数字だけ/万を含む形も不可
    ("12000300", 12300, False), ("100200300", 100500, False), ("1000200300", 1500, False), ("10000200", 10200, True),
    ("80九百", 980, False), ("12000三百", 12300, False), ("8000九万", 98000, False), ("8000900", 8800, False),
])
def test_explain_garble_boundaries_r3(run, target, ok):
    assert (B.explain_garble(run, target) is not None) == ok


def test_three_fragment_digit_run_is_never_explained_until_real_example():
    # 3断片の総和が一致し位取りも重ならない構成でも無効(実例が出るまで)
    assert B.explain_garble("10002000300", 3300 + 0) is None
    assert B.explain_garble("100020003", 3000 + 3000 + 3) is None


# ---- M-3: 複数atom ----
def test_multi_atom_both_correct_primary_equal_is_pass():
    assert j(C2, "売上は1,200円で利益は3,500円です", S2).equal


def test_multi_atom_first_explained_second_contradiction_is_not_rescued():
    r = j(C2, "売上は1000200円で利益は4,500円です", S2)
    assert not r.equal and r.blocked_by == "primary_secondary_value_contradiction" and r.protected


def test_multi_atom_first_contradiction_second_explained_is_not_rescued():
    r = j(C2, "売上は1,300円で利益は3000五百円です", S2)
    assert not r.equal and r.protected


def test_multi_atom_first_explained_second_equal_is_pass():
    r = j(C2, "売上は1000200円で利益は3,500円です", S2)
    assert r.equal and B.W_GARBLE_EXPLAINED in r.warnings and r.listen_required


def test_multi_atom_both_explained_is_pass_with_listen():
    r = j(C2, "売上は1000200円で利益は3000五百円です", S2)
    assert r.equal and r.listen_required and len(r.audit["explained_spans"]) == 2


def test_multi_atom_second_garble_sum_mismatch_is_not_rescued():
    assert not j(C2, "売上は1,200円で利益は3000200円です", S2).equal       # 3000+200 != 3500


@pytest.mark.parametrize("s", [
    "売上は3500円で利益は1200円です",                 # 順序入替(Secondary)
    "売上は1200円です",                              # Secondary値不足
    "売上は1200円で利益は3500円で費用は100円です",     # Secondary値過剰
    "売上は1200円で利益は3500円と3500円です",
    "売上は1200円で利益は3,600円です",                 # 2個目の値違い
])
def test_multi_atom_secondary_sequence_or_value_mismatch_is_not_rescued(s):
    r = j(C2, "売上は1000200円で利益は3,500円です", s)
    assert not r.equal, s


def test_multi_atom_same_counter_repeated():
    C3 = "1,200円と1,200円を払う"
    assert j(C3, "1000200円と1000200円を払う", "1200円と1200円を払う").equal
    assert j(C3, "1000200円と1,200円を払う", "1200円と1200円を払う").equal
    assert not j(C3, "1000200円と1000500円を払う", "1200円と1200円を払う").equal      # 2個目 1000+500=1500
    assert not j(C3, "1000500円と1000200円を払う", "1200円と1200円を払う").equal      # 1個目 1000+500=1500
    assert not j(C3, "1000200円を払う", "1200円と1200円を払う").equal                # Primary側の2個目が欠落(MISSING)
    assert not j(C3, "1000200円と1000200円を払う", "1200円を払う").equal              # Secondary値不足


def test_multi_atom_primary_swapped_order_is_not_rescued():
    assert not j(C2, "利益は3,500円で売上は1000200円です", S2).equal


def test_multi_atom_primary_extra_number_is_not_rescued():
    assert not j(C2, "売上は1000200円で利益は3,500円です。費用は100円", S2).equal


def test_value_guard_is_positional_not_set_based():
    # 設計メモ: value_guard は位置照合(順序入替でDIFF)。proto は更に atom列を二重化して照合する
    import er078_asr_value_guard_01 as vg
    assert vg.value_guard(C2, "売上は3500円で利益は1200円です", "ja").kind == vg.DIFF
    assert vg.value_guard("3人と5人", "5人と3人", "ja").kind == vg.DIFF


# ---- F-B / Secondary表記の負例 (Opus 事前登録不足) ----
@pytest.mark.parametrize("c,p,s", [
    ("売上は1,200円です", "売上は1000200円です", "売上はせんにひゃく円です"),        # SecondaryかなN数詞
    ("売上は1,200円です", "売上は1000200円です", "売上は千にひゃく円です"),
    ("売上は8,900円です", "売上は8000900円です", "売上は8000 900円です"),           # Secondary空白run(900だけが値atom)
    ("売上は8,900円です", "売上は8000900円です", "売上は8万900円です"),             # Secondary万
    ("売上は8,900円です", "売上は8000900円です", "売上は8万9千円です"),
    ("売上は8,900円です", "売上は8000 900円です", "売上は8900円です"),             # Primary空白run
    ("売上は8,900円です", "売上は8000万900円です", "売上は8900円です"),             # Primary万含み
    ("売上は8,900円です", "売上は8万900円です", "売上は8900円です"),
    ("売上は8,900円です", "売上は８０００　９００円です", "売上は8900円です"),       # Primary全角+全角空白run
    ("売上は8,900円です", "売上は8000九万円です", "売上は8900円です"),
])
def test_fb_and_secondary_notation_negatives(c, p, s):
    r = j(c, p, s)
    assert not r.equal, (p, s, r.why)


def test_fullwidth_digits_are_digit_notation_not_a_bypass():
    # 全角数字はNFKCで通常の数字表記。値が正しい場合だけ通る(値違いは通らない)
    assert j("売上は8,900円です", "売上は８０００９００円です", "売上は８９００円です").equal
    assert not j("売上は8,900円です", "売上は８０００８００円です", "売上は８９００円です").equal
    assert not j("売上は8,900円です", "売上は８０００９００円です", "売上は８８００円です").equal


@pytest.mark.parametrize("c,s", [
    ("みっつ買った", "みっつ買った"), ("十分待った", "十分待った"), ("一月に行く", "一月に行く"),
])
def test_r4_kana_numeral_or_ambiguous_atoms_are_not_applicable(c, s):
    r = j(c, c, s)
    assert not r.equal and r.blocked_by in ("R4_atom_notation", "not_applicable", "A4a_irregular_reading")


def test_r4_secondary_kana_numeral_atom_blocks_composite():
    r = j("売上は1,200円で犬が3匹います", "売上は1000200円で犬が3匹います", "売上は1200円で犬がさんびきいます")
    assert not r.equal
    r2 = j("売上は1,200円で犬が3匹います", "売上は1000200円で犬が3匹います", "売上は1200円で犬がみっつです")
    assert not r2.equal and r2.blocked_by == "R4_atom_notation"


# ---- R-1 / R-2: 警告 + 試聴必須 ----
def test_r1_secondary_reading_conflict_warns_and_requires_listening():
    r = j(C, "月の氏は8000900本超" + TAIL, S_OK)
    assert r.equal and B.W_SECONDARY_READING_CONFLICT in r.warnings and B.W_LISTEN_REQUIRED in r.warnings and r.listen_required
    assert r.audit["secondary_reading_conflict"] is True


def test_r1_veto_mode_blocks():
    r = j(C, "月の氏は8000900本超" + TAIL, S_OK, secondary_reading_conflict="veto")
    assert not r.equal and r.blocked_by == "secondary_reading_conflict"


def test_r2_garble_requires_listening_even_without_secondary_conflict():
    r = j(C, "月のしわ、8000900本超" + TAIL, "月のしわ、8900本超" + TAIL)
    assert r.equal and B.W_GARBLE_EXPLAINED in r.warnings and r.listen_required and B.W_SECONDARY_READING_CONFLICT not in r.warnings


def test_no_listen_requirement_when_everything_equal():
    r = j(C, "月のしわ、8,900本超" + TAIL, "月のしわ、8900本超" + TAIL)
    assert r.equal and not r.listen_required and B.W_LISTEN_REQUIRED not in r.warnings


# ---- M-1: 読み規則v2依存の明示 ----
def test_reading_rule_v2_is_recorded_in_audit_and_strict_option_differs():
    r = j(C, "月の氏は8000900本超" + TAIL, S_OK)
    assert r.audit["reading_rule"] == B.READING_RULE_V2 and "proto_reading_compare_02" in B.READING_RULE_V2
    rs = j(C, "月の氏は8000900本超" + TAIL, S_OK, reading_rule="strict")
    assert not rs.equal                       # 同音異字(氏は→しわ)はv2読み規則に依存して初めて通る
    assert j(C, "月のしわ、8000900本超" + TAIL, "月のしわ、8900本超" + TAIL, reading_rule="strict").equal


# ---- R-7 / M-2: 監査・fail-closed ----
def test_r7_audit_fields():
    r = j(C, "月の氏は8000900本超" + TAIL, S_OK)
    a = r.audit
    assert a["reading_source"] == "primary" and a["value_source"] == "secondary" and a["composite_contributed"] is True
    assert a["secondary_engine"] == "azure" and a["secondary_wav_sha256"] == "deadbeef" and a["secondary_transcript"] == S_OK
    assert a["explained_spans"] and a["explained_spans"][0]["primary_run"] == "8000900"


def test_m2_secondary_provenance_missing_is_fail_closed():
    for meta in (None, {}, {"engine": "azure"}, {"wav_sha256": "x"}):
        r = B.composite_judge(C, "月の氏は8000900本超" + TAIL, S_OK, meta)
        assert not r.equal and r.blocked_by == "secondary_provenance_missing"


def _entry(flag_audit=True):
    r = j(C, "月の氏は8000900本超" + TAIL, S_OK)
    au = dict(r.audit)
    aj = {"state": "PASS_WITH_WARNING", "label": r.label, "warnings": list(r.warnings), "composite": au}
    return {"asr_judgement": aj}


def test_m2_composite_audio_out_of_scope_or_flag_off_is_blocked_before_rejudge():
    e = _entry()
    assert B.composite_contributed(e["asr_judgement"])
    for scope in ("A", "B", "C", None, "x"):
        d = B.composite_reuse_decision(e, True, scope)
        assert d.blocked and d.reason == "COMPOSITE_AUDIO_OUT_OF_SCOPE_OR_FLAG_OFF" and not d.rejudged
    d = B.composite_reuse_decision(e, False, "X")
    assert d.blocked and not d.rejudged


def test_m2_in_scope_flag_on_rejudges_with_stored_secondary():
    e = _entry()
    for scope in B.SCOPE_ALLOWED:
        d = B.composite_reuse_decision(e, True, scope)
        assert not d.blocked and d.rejudged


def test_m2_missing_stored_provenance_is_fail_closed():
    for k in ("secondary_transcript", "secondary_engine", "secondary_wav_sha256", "primary_transcript", "canonical_text"):
        e = _entry()
        e["asr_judgement"]["composite"].pop(k)
        d = B.composite_reuse_decision(e, True, "X")
        assert d.blocked and d.reason == "COMPOSITE_PROVENANCE_MISSING", k
    e = _entry(); e["asr_judgement"].pop("composite")
    assert B.composite_reuse_decision(e, True, "X").blocked           # 警告/ラベルだけ残っていても fail-closed


def test_m2_rejudge_ng_with_changed_rules_blocks_even_if_not_protected():
    e = _entry()
    e["asr_judgement"]["composite"]["secondary_transcript"] = "杉野氏は8800本超" + TAIL
    d = B.composite_reuse_decision(e, True, "Z")
    assert d.blocked and d.reason.startswith("COMPOSITE_REJUDGE_NG")


def test_m2_non_composite_entries_are_untouched():
    assert not B.composite_reuse_decision({"asr_judgement": {"state": "PASS", "label": "EXACT_MATCH"}}, False, "A").blocked
    assert not B.composite_reuse_decision({}, False, None).blocked


def test_m2_inherited_judgement_is_also_checked():
    e = _entry()
    e2 = {"asr_judgement": {"state": "PASS"}, "asr_judgement_inherited": e["asr_judgement"]}
    assert B.composite_reuse_decision(e2, False, "X").blocked


# ---- R-8: フック①の事前判定を最終判定へ流用できない ----
def test_r8_precheck_result_has_no_final_judgement_attributes():
    pr = B.precheck_composite(C, "月の氏は8000900本超" + TAIL)
    assert isinstance(pr, B.PrecheckResult) and pr.may_call_secondary
    for attr in ("equal", "label", "warnings", "audit"):
        assert not hasattr(pr, attr)


def test_r8_precheck_meta_is_rejected_by_composite_judge():
    r = B.composite_judge(C, "月の氏は8000900本超" + TAIL, S_OK, {"precheck": True, "engine": "azure", "wav_sha256": "x"})
    assert not r.equal and r.blocked_by == "precheck_not_final"


def test_r8_precheck_true_but_actual_secondary_wrong_is_still_ng():
    p = "月の氏は8000900本超" + TAIL
    assert B.precheck_composite(C, p).may_call_secondary
    assert not j(C, p, "杉野氏は8800本超" + TAIL).equal            # 実Secondaryの値が違えば事前判定が真でも最終NG
    assert not j(C, p, "杉野氏は本超" + TAIL).equal


def test_precheck_false_when_primary_contradiction_or_reading_differs():
    assert not B.precheck_composite(C, "月のしわ、8800本超" + TAIL).may_call_secondary
    assert not B.precheck_composite(C, "月のすわ、8000900本超" + TAIL).may_call_secondary


# ---- 隔離 ----
def test_production_modules_do_not_import_prototype():
    hits = []
    for f in glob.glob("*.py"):
        if f.startswith("b_light"):
            continue
        try:
            t = open(f, encoding="utf8").read()
        except Exception:
            continue
        if "b_light_proto" in t:
            hits.append(f)
    assert hits == []


def test_prototype_has_no_network_or_llm_imports():
    src = open(B.__file__, encoding="utf8").read()
    for bad in ("openai", "requests", "azure.", "anthropic", "urllib.request", "httpx"):
        assert f"import {bad}" not in src, bad


def test_deterministic():
    a = [j(C, "月の氏は8000900本超" + TAIL, S_OK).why for _ in range(3)]
    assert len(set(a)) == 1
    b = [tuple(j(C, "月の氏は8000900本超" + TAIL, S_OK).warnings) for _ in range(3)]
    assert len(set(b)) == 1
