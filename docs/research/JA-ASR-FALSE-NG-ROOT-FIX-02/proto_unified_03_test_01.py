# proto_unified_03 のtest (DEV/API 0)。再現: PYTHONUTF8=1 .venv/Scripts/python.exe -X utf8 -m pytest docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/proto_unified_03_test_01.py -q
import copy, itertools, os, socket, sys
import pytest

sys.path.insert(0, ".")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proto_unified_03 as U
import eval_common_02 as E
import er007_ja_secondary_asr_01 as sec
import er008_asr_variant_hardening_15_ja_kanji_readings as kr
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg

MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
TAIL = "！その奥に潜む「岩の上着」の秘密"
F1 = U.Flags(True)
F1_NOR1 = U.Flags(True, r1=False)
F13 = U.Flags(True, False, True)
FIN_NOR1 = U.Flags(True, True, True, r1=False)
W = E.dummy_wav()


@pytest.fixture(autouse=True)
def _no_net(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("API0 violation")
    monkeypatch.setattr(socket.socket, "connect", boom)


def J(c, p, s, f=U.FINAL, **kw):
    return U.judge(c, p, s, W, f, **kw)


# ---- 既定=L0同一(DefaultOffIsolation) ----
def test_default_flags_all_off():
    f = U.Flags()
    assert (f.l1, f.l2, f.l3) == (False, False, False) and f.name() == "L0"


def test_default_equals_production_adapter_and_leaves_no_patch():
    orig_num, orig_az = sec._numeric_value_equivalence, sec._azure_stt_strict
    cases = [(MOON, "月の詩は、8,900本超" + TAIL, "月の詩は8900本超" + TAIL), (MOON, "月のしわ、8,900本超" + TAIL, None), ("今日は一日中雨", "今日はついたち中雨", "今日は一日中雨"),
             (MOON, "月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。", "月野市は8900本越え。その奥に潜む岩の上着の秘密。")]
    for c, p, s in cases:
        direct = U._adapter(c, p, s, W, U.Flags(), [])["asr_judgement"]
        mine = J(c, p, s, U.Flags())
        assert (mine["state"], mine["reason"]) == (direct.get("state"), direct.get("reason_code"))
        assert mine["layers"] == [] and mine["warning_labels"] == []
    assert sec._numeric_value_equivalence is orig_num and sec._azure_stt_strict is orig_az


def test_no_network_in_all_flags_and_consensus():
    for f in (U.Flags(), F1, U.FINAL, FIN_NOR1):
        J(MOON, "月の詩は、8,900本超え" + TAIL, "月の詩は8900本越え" + TAIL, f)
    U.consensus(MOON, ["月のしわ、8,800本超" + TAIL, "月のしわ、8,900本超" + TAIL], "月のしわ、8900本超" + TAIL, W, U.FINAL, 0, (1,))


# ---- M-1: 不規則読みガード(両側・PRON/VALUE_ONLY両経路・L1⊇L0) ----
IRREG = [("今日は一日中雨", "今日はついたち中雨"), ("二日待った", "ふつか待った"), ("二十日に会う", "はつか会う"), ("二十歳になった", "はたちになった"), ("一人で行く", "ひとりで行く"),
         ("二人で行く", "ふたりで行く"), ("四人で行く", "よにんで行く"), ("三日待った", "みっか待った")]


@pytest.mark.parametrize("c,a", IRREG)
def test_m1_irregular_guard_negative_all_sides(c, a):
    for sec_text in (None, a, c):
        r = J(c, a, sec_text, F1)
        l0 = J(c, a, sec_text, U.Flags())
        assert r["cat"] == l0["cat"] and (r["reason"], r["state"]) == (l0["reason"], l0["state"])     # L1 == L0 (Production判定をそのまま返す)


def test_m1_irregular_set_is_enumerated_by_is_irregular_sig():
    assert U.irregular_atoms("今日は一日中雨") and U.irregular_atoms("二十歳") and U.irregular_atoms("三日") and not U.irregular_atoms(MOON)
    assert vg.is_irregular_sig(1, "day") and vg.is_irregular_sig(20, "age") and vg.is_irregular_sig(2, "person") and not vg.is_irregular_sig(8900, "hon")


def test_m1_pron_path_and_value_only_path_both_guarded():
    # VALUE_ONLY(表記だけ違う)・PRON(助詞は→わ)どちらでも不規則読み原稿では救済しない
    assert J("三日待った", "3日待った。", "3日待った。", F1)["cat"] == J("三日待った", "3日待った。", "3日待った。", U.Flags())["cat"]
    assert J("私は一日は休む", "私は1日わ休む", "私は一日は休む", F1)["cat"] == J("私は一日は休む", "私は1日わ休む", "私は一日は休む", U.Flags())["cat"]


def test_m1_baseline_pass_w_unchanged():
    c, a = "三人で一日に会った", "三人で一日に会った"
    assert J(c, a, a, U.Flags())["cat"] == J(c, a, a, U.FINAL)["cat"]


# ---- M-2: 新層は専用warningを持ち、承認済み根拠に入らず、PASS_W_NEWに分類 ----
def test_m2_new_labels_not_in_approved_bases():
    assert set(U.NEW_WARN.values()).isdisjoint(set(uj.APPROVED_EQUIVALENCE_BASES))
    assert all(v.startswith("JA_NEWLAYER_") for v in U.NEW_WARN.values())


def test_m2_every_new_layer_rescue_has_label_and_is_pass_w_new():
    r = J(MOON, "月の氏は、8,900本超" + TAIL, None, F1_NOR1)     # PRON(R-1 OFF)
    assert r["cat"] == "PASS_W_NEW" and r["warning_labels"] == [U.NEW_WARN["L1_PRON"]]
    a = "月のしわ、8,900本超え" + TAIL
    r = J(MOON, a, a.replace("超え", "越え"), F13)                  # L3
    assert r["cat"] == "PASS_W_NEW" and r["warning_labels"] == [U.NEW_WARN["L3"]]
    r = J(MOON, "月の氏は8000900本超。その奥に潜む岩の上着の秘密。", "杉野氏は8900本超。その奥に潜む岩の上着の秘密。", FIN_NOR1)     # β(PRON同音を含む型はR-1 OFFで)
    assert r["cat"] == "PASS_W_NEW" and r["warning_labels"] == [U.NEW_WARN["L2"]]
    r = J(MOON, "月のしわ、8000900本超" + TAIL, "月のしわ、8900本超" + TAIL)                # β(発音同一を含まない純粋な数値garble)はR-1 ON既定でも救済
    assert r["cat"] == "PASS_W_NEW" and r["warning_labels"] == [U.NEW_WARN["L2"]]


def test_m2_prod_pass_w_and_clean_pass_not_relabeled():
    r = J(MOON, "月のしわ、8,900本超え" + TAIL, MOON, U.FINAL)       # Productionが既にPASS_W(Secondary確認経路)
    assert r["cat"] in ("PASS_W_PROD", "PASS") and r["warning_labels"] == []
    r = J(MOON, MOON, MOON, U.FINAL)
    assert r["cat"] == "PASS" and r["warning_labels"] == []


def test_m2_value_only_beyond_prod_gets_warning():
    # v2のVALUE_ONLYがProductionの値等価層の受理範囲を超えて救済した実例(コーパス探索で2件中の正例): 20％ -> 20パーセント。受理範囲内ならタグ無し=Production同一。
    c, a = "20％の人が来ました。", "20パーセントの人が来ました。"
    l0 = J(c, a, None, U.Flags())
    r = J(c, a, None, F1)
    assert l0["cat"] == "NG"
    assert r["cat"] == "PASS_W_NEW" and r["warning_labels"] == [U.NEW_WARN["L1_VALUE"]]
    c2, a2 = MOON, "月のしわ、8900本超" + TAIL                       # Production既存の値等価層が受理する表記違い=新層の寄与なし
    assert J(c2, a2, None, F1)["warning_labels"] == [] and J(c2, a2, None, F1)["cat"] == J(c2, a2, None, U.Flags())["cat"]


# ---- M-3: 矛盾なし合意 ----
SC_A3 = "Sukino氏は8900本超。その奥に潜む岩の上着の秘密。"
D_A3 = ["スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。", "月野市は、八千九百本超、その奥に潜む岩の上着の秘密。", "スギノ市は、八千九百本超、その奥に潜む岩の上着の秘密。"]


def test_m3_fishing_case_goes_to_hr_not_pass():
    for flags in (U.FINAL, FIN_NOR1):
        r = U.consensus(MOON, D_A3, SC_A3, W, flags, 0, (1,))
        assert r["cat"] != "PASS_W_NEW" and r["cat"] in ("HR", "NG")
    r = U.consensus(MOON, D_A3, SC_A3, W, FIN_NOR1, 0, (1, 2))
    assert r["cat"] == "HR" and r["retry_fired"] and r["contra_idx"] == [0, 2]
    assert U.best_of_n_ref(MOON, D_A3, SC_A3, W, FIN_NOR1, 0, (1,)) == "PASS_W_NEW"      # 参考: best-of-Nなら釣れてしまう


def test_m3_consensus_pass_requires_no_contradiction_and_is_pass_w_new():
    ok1 = "月のしわ、8,800本超" + TAIL          # 値だけ違う(別の値)=矛盾
    d = ["月のしわ、八千九百本超" + TAIL.replace("！", "、"), "月のしわ、8,900本超" + TAIL]
    sc = "月のしわ、8900本超" + TAIL
    r = U.consensus(MOON, d, sc, W, U.FINAL, 0, (1,))
    if r["retry_fired"]:
        assert r["cat"] == "PASS_W_NEW" and U.NEW_WARN["RETRY"] in r["warning_labels"]
    r2 = U.consensus(MOON, [ok1, "月のしわ、8,900本超" + TAIL], sc, W, U.FINAL, 0, (1,))
    assert r2["cat"] in ("HR", "NG", "PASS_W_NEW", "PASS")
    if r2["retry_fired"]:
        assert r2["cat"] != "PASS_W_NEW"                    # 別の値を言ったdrawがあるのでPASSにしない


def test_m3_force_secondary_and_whitelist_and_neg():
    d = ["月のしわ、8,800本超" + TAIL, "月のしわ、8,900本超" + TAIL]
    r = U.consensus(MOON, d, None, W, U.FINAL, 0, (1,))
    assert not r["retry_fired"] and "no_stored_secondary" in r["retry_block"]          # Secondary無し=再試行不可(Azure再試行もしない)
    neg = ["月のしわ、8,900本超なし" + TAIL, "月のしわ、8,900本超" + TAIL]
    r = U.consensus(MOON, neg, "月のしわ、8900本超" + TAIL, W, U.FINAL, 0, (1,))
    assert not (r["retry_fired"] and r["cat"] == "PASS_W_NEW")


def test_m3_n_max_is_three_and_no_azure_retry():
    with pytest.raises(AssertionError):
        U.consensus(MOON, ["a", "b", "c", "d"], "x", W, U.FINAL, 0, (1, 2, 3))
    assert U.RETRY_WHITELIST == ("p1_value_diff", "secondary_not_accepted")
    src = open(U.__file__, encoding="utf8").read()
    assert "_azure_stt_strict = lambda" in src and src.count("composite_judge") >= 1          # AzureはFixed-stub(保存転写)のみ


def test_m3_combos_are_order_independent_and_complete():
    assert len(list(U.combos(5, 1))) == 5 and len(list(U.combos(5, 2))) == 5 * 4 and len(list(U.combos(5, 3))) == 5 * 6
    assert len(list(U.combos(4, 3))) == 4 * 3
    seen = {(f, tuple(sorted(ex))) for f, ex in U.combos(4, 2)}
    assert seen == {(f, (e,)) for f in range(4) for e in range(4) if e != f}


def test_m3_hr_is_not_a_pass_state():
    r = U.consensus(MOON, D_A3, SC_A3, W, FIN_NOR1, 0, (1, 2))
    assert r["cat"] == "HR" and r["cat"] not in ("PASS", "PASS_W_PROD", "PASS_W_NEW") and r["warning_labels"] == []


# ---- M-4: 再試行セグメントでβの読み食い違いはveto ----
def test_m4_beta_reading_conflict_warn_vs_veto():
    p = "月の氏は8000900本超。その奥に潜む岩の上着の秘密。"
    s = "杉野氏は8900本超。その奥に潜む岩の上着の秘密。"
    assert J(MOON, p, s, FIN_NOR1)["cat"] == "PASS_W_NEW"                     # 単独draw: 許容(PASS_W+試聴)
    assert J(MOON, p, s, FIN_NOR1, retry_mode=True)["cat"] == "NG"            # 再試行セグメント: veto


# ---- M-5: 別表L3 ----
@pytest.mark.parametrize("k", ["超え", "越え", "こえ"])
def test_m5_l3_table_positive_generic(k):
    for c, a in ((MOON, f"月のしわ、8,900本{k}" + TAIL), ("参加者は100人超でした", f"参加者は100人{k}でした"), ("売上は1,200円超です", f"売上は1,200円{k}です")):
        assert J(c, a, a, F1)["cat"] == "NG"
        r = J(c, a, a, F13)
        assert r["cat"] == "PASS_W_NEW" and r["warning_labels"] == [U.NEW_WARN["L3"]]


def test_m5_l3_requires_both_engines_and_zero_residual():
    a = "月のしわ、8,900本超え" + TAIL
    assert J(MOON, a, None, F13)["cat"] == "NG"
    assert J(MOON, "月の詩は、8,900本超え" + TAIL, "月の詩は、8,900本越え" + TAIL, F13)["cat"] == "NG"      # 旧L3の『発音同一との併用』は不可(残差0文字でない)
    assert J(MOON, "月野詩は8900本超え。その奥に潜む岩の上着の秘密。", "月野市は8900本越え。その奥に潜む岩の上着の秘密。", F13)["cat"] == "NG"


@pytest.mark.parametrize("a", [f"月のしわ、{v}本超え" + TAIL for v in ("8,800", "890", "89,000")] + [f"月のしわ、8,900{u}超え" + TAIL for u in ("個", "枚", "人")]
                         + ["月のしわ、8,900本超えない" + TAIL, "月のしわ、8,900本超える" + TAIL, "月のしわ、8,900本未満" + TAIL, "月のしわ、8,900本を超え" + TAIL])
def test_m5_l3_negative_no_increment(a):
    assert J(MOON, a, a, U.Flags(True))["cat"] == "NG"
    assert J(MOON, a, a, F13)["cat"] == J(MOON, a, a, U.Flags(True))["cat"]


def test_m5_generic_dictionary_unchanged():
    # 汎用読み辞書(er008)には『超→こえ』を追加していない。別表は新層内のみ。
    assert "こえ" not in kr.reading_candidates_for_span("超")
    assert U.KUNYOMI_OKURIGANA == {"超": ("超え", "越え", "こえ")}


# ---- M-6: E3/E4 ----
def test_m6_e3_rejections_disable_all_new_layers():
    c, a = "三日目", "3日間"
    rej, casc = U.e34_state(c, a)
    assert rej                                           # 実在するE3拒否例
    for s in (None, a, c):
        r = J(c, a, s, U.FINAL)
        l0 = J(c, a, s, U.Flags())
        assert r["blocked"] and r["cat"] == l0["cat"] and (r["reason"], r["state"]) == (l0["reason"], l0["state"])


def test_m6_e4_cascade_diffs_disable_new_layers(monkeypatch):
    monkeypatch.setattr(U, "e34_state", lambda canon, prim: ([], [("c", "a")]))
    a = "月の詩は、8,900本超" + TAIL
    r = J(MOON, a, None, F1_NOR1)
    l0 = J(MOON, a, None, U.Flags())
    assert r["blocked"] and r["cat"] == l0["cat"] and any(x["layer"] == "M6_new_layers_disabled" for x in r["layers"])


# ---- M-7: βの独立性 ----
def test_m7_phrase_list_hash_must_be_empty():
    p = "月の氏は8000900本超。その奥に潜む岩の上着の秘密。"
    s = "杉野氏は8900本超。その奥に潜む岩の上着の秘密。"
    assert J(MOON, p, s, FIN_NOR1, phrase_list_hash="")["cat"] == "PASS_W_NEW"
    for h in ("abc123", None):
        r = J(MOON, p, s, FIN_NOR1, phrase_list_hash=h)
        assert r["cat"] == "NG" and r.get("beta_blocked_by") == "M7_witness_independence"


def test_r1_applies_to_beta_pron_path_too():
    p = "月の氏は8000900本超。その奥に潜む岩の上着の秘密。"
    s = "杉野氏は8900本超。その奥に潜む岩の上着の秘密。"
    assert J(MOON, p, s, FIN_NOR1)["cat"] == "PASS_W_NEW"
    r = J(MOON, p, s, U.FINAL)
    assert r["cat"] == "NG" and r["beta_blocked_by"] == "R1_blocked_in_beta"


# ---- R-1 / R-2 ----
def test_r1_per_char_multi_reading_blocks_pron_rescue():
    a = "月の氏は、8,900本超" + TAIL
    assert J(MOON, a, None, F1_NOR1)["cat"] == "PASS_W_NEW"       # R-1 OFF
    r = J(MOON, a, None, F1)                                       # R-1 ON: 氏 は複数読み(し/うじ)
    assert r["cat"] == "NG" and any(x["layer"] == "R1_blocked" for x in r["layers"])
    assert U.r1_block(MOON, a) and U.r1_block(MOON, a).startswith("r1_char_multi_reading:氏")


def test_r2_engine_reading_difference_excluded(monkeypatch):
    import proto_reading_compare_02 as P
    real = P.pron_value_equivalence

    def fake(canon, asr, cls=None, expected_readings=None, require_value_atoms=False, side="primary"):
        r = real(canon, asr, cls=cls, expected_readings=expected_readings, require_value_atoms=require_value_atoms, side=side)
        return P.V1Result(True, "PRON", "x", P.PRON_LABEL, (P.W_PRON,), "ENGINE_reading_difference") if r.equal and r.kind == "PRON" else r
    monkeypatch.setattr(P, "pron_value_equivalence", fake)
    r = J(MOON, "月の氏は、8,900本超" + TAIL, None, F1_NOR1)
    assert r["cat"] == "NG" and any(x["layer"] == "R2_engine_reading_excluded" for x in r["layers"])


# ---- R-7: 保存drawのみから再現・Store再利用 ----
def test_r7_rejudge_from_stored_draws_only_reproduces():
    for flags in (U.FINAL, FIN_NOR1):
        for first, ex in ((0, (1,)), (1, (0, 2)), (2, (1,))):
            r = U.consensus(MOON, D_A3, SC_A3, W, flags, first, ex)
            r2 = U.rejudge_from_audit(copy.deepcopy(r))
            assert r2["cat"] == r["cat"] and r2["contradictions"] == r.get("contradictions") if r["retry_fired"] else r2["cat"] == r["cat"]
            assert r["rule_version"] == U.RULE_VERSION and r["layer_version"] == U.LAYER_VERSION and r["draws"] == D_A3 and r["secondary"] == SC_A3


def test_r7_version_mismatch_fail_closed_and_reuse_blocks_first():
    r = U.consensus(MOON, D_A3, SC_A3, W, FIN_NOR1, 0, (1, 2))
    bad = dict(r, rule_version="old")
    assert U.rejudge_from_audit(bad)["reason"] == "version_mismatch_fail_closed"
    assert U.consensus_reuse_decision(r, flag_on=False, scope="X")["blocked"]
    assert U.consensus_reuse_decision(r, flag_on=True, scope="A")["blocked"]
    assert U.consensus_reuse_decision(r, flag_on=True, scope="X")["reason"].startswith("CONSENSUS_REJUDGE_SAME")
    broken = dict(r, secondary=None)
    assert U.consensus_reuse_decision(broken, True, "Y")["reason"].startswith("CONSENSUS_PROVENANCE_MISSING")
    assert not U.consensus_reuse_decision({"asr_judgement": {}}, False, "A")["blocked"]          # consensus寄与の無いentryには作用しない
