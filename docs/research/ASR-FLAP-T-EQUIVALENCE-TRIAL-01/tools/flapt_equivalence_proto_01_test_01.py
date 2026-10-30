# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_01: Trial case table (API 0)。実行: .venv\Scripts\python.exe -m pytest <this file> -q
# 期待値は設計判断(DESIGN_01.md 5節)。『不整合な出力を期待値としてassertしない』: 反例はNO_RESCUE/REQUIRES_EXTRA_EVIDENCEを期待する。
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pytest
import flapt_equivalence_proto_01 as fl

R, N, X, NA = "RESCUE", "NO_RESCUE", "REQUIRES_EXTRA_EVIDENCE", "NOT_APPLICABLE"
# (id, group, canonical, asr, expected, note)
CASES = [
    # --- 正例(flap-T同音: 語中・強勢母音後・無強勢母音前) ---
    ("P01", "positive", "latter", "Ladder", R, "実データ FX4⑨ vocab(8判定NG)"),
    ("P02", "positive", "metal", "medal", R, "指定ケース"),
    ("P03", "positive", "betting", "bedding", R, "指定ケース"),
    ("P04", "positive", "atom", "Adam", R, "指定ケース"),
    ("P05", "positive", "waiting", "wading", R, "指定ケース"),
    ("P06", "positive", "coating", "coding", R, "指定ケース"),
    ("P07", "positive", "Bertie", "Birdie", R, "実データ FZ The Open Window(Bertie, why do you bound?)"),
    ("P08", "positive", "The latter option is cheaper.", "The ladder option is cheaper.", R, "文脈つき(1:1置換のみ)"),
    ("P09", "positive", "ladder", "latter", R, "逆方向(canonical=d綴り)。両側flap環境なら対称に救済"),
    ("P10", "positive", "bitter", "bidder", R, "追加"),
    ("P11", "positive", "tutor", "Tudor", R, "追加"),
    ("P12", "positive", "rated", "raided", R, "語末dは両語同一、語中のみT/D差"),
    # --- 反例(救済してはならない) ---
    ("N01", "counter", "ten", "den", N, "語頭(flapなし)。指定反例"),
    ("N02", "counter", "time", "dime", N, "語頭。指定反例"),
    ("N03", "counter", "putting", "pudding", N, "canonicalがAH/UHの2読み(P-01 strict)。母音差の可能性を残すため非救済"),
    ("N04", "counter", "heartbeat", "heartbead", N, "複合語(T+B, 非flap)。非語はCMU未登録で判定不能=非救済"),
    ("N05", "counter", "eaten", "Eden", N, "音節的n(声門閉鎖化)でflapにならない"),
    ("N06", "counter", "water", "wader", N, "母音が異なる(AO vs EY)=子音以外の差"),
    ("N07", "counter", "letter", "leader", N, "母音が異なる(EH vs IY)"),
    ("N08", "counter", "battle", "paddle", N, "t/d以外の子音差(B/P)"),
    ("N09", "counter", "party", "pardy", N, "R直後(v1は保守的に非対象。CMU上pardyは未登録でも非救済)"),
    ("N10", "counter", "attack", "Adak", N, "T直前が無強勢母音・直後が強勢母音(aspirated T, flapなし)"),
    ("N17", "counter", "alter", "alder", N, "T/Dの前がL(子音)=flap環境でない(CMU上の実在語ペア)"),
    ("N18", "counter", "Burton", "burden", N, "音節的n(T/D+AH0 N)=声門閉鎖化しやすくflapにならない"),
    ("N11", "counter", "feed", "feet", N, "語末(flapなし)"),
    ("N12", "counter", "latter", "later", N, "別語(音素差 T/D以外: L EY1 T ER0)"),
    ("N13", "counter", "The latter option is cheaper.", "The ladder option is cheaper today.", NA, "挿入を含む(1:1置換のみ対象)"),
    ("N14", "counter", "The latter option is cheaper.", "The ladder option is cheap.", N, "flap差に加え別語差(cheaper/cheap)=全差分がflapでないので非救済(NOT_APPLICABLE相当でも可)"),
    ("N15", "counter", "total", "toad all", NA, "1:2(1語⇔2語)は対象外(多語同音はPNMH層の担当)"),
    ("N16", "counter", "metal", "mettle", N, "音素同一=既存homophone層の担当。flap層は発火しない(二重救済防止)"),
    # --- 母音差が残りうる核(AY/AW): 自動救済しない ---
    ("X01", "vowel_sensitive", "writer", "rider", X, "指定。CMUは母音同一(AY1)=辞書だけでは区別不能 -> 自動救済せず追加証拠要(従来どおりNG)"),
    ("X02", "vowel_sensitive", "title", "tidal", X, "実データ(AKB48 b1b)。AY核"),
    ("X03", "vowel_sensitive", "Wright", "ride", N, "語末(flapなし)でN"),
    # --- 判定不能 ---
    ("U01", "unresolved", "Zorbo", "Zorpo", N, "CMU未登録=判定不能=非救済(fail-closed)"),
]


@pytest.mark.parametrize("cid,group,canon,asr,expected,note", CASES)
def test_case(cid, group, canon, asr, expected, note):
    r = fl.evaluate(canon, asr)
    if expected == N:
        assert r.decision in (N, NA), (cid, r.decision, r.reason)     # 非救済(NG維持)であれば NO_RESCUE/NOT_APPLICABLE のどちらでも可
    else:
        assert r.decision == expected, (cid, r.decision, r.reason)


def test_voice_scope_fail_closed():
    assert fl.voice_applicable("Aoede") is False                      # 既定=空集合
    assert fl.voice_applicable(None, frozenset({"Aoede"})) is False   # Voice不明
    assert fl.voice_applicable("Aoede", frozenset({"Aoede"})) is True
    assert fl.voice_applicable("Fenrir", frozenset({"Aoede"})) is False


def test_dump_case_table():
    rows = []
    for cid, group, canon, asr, expected, note in CASES:
        r = fl.evaluate(canon, asr)
        ok = (r.decision in (N, NA)) if expected == N else (r.decision == expected)
        rows.append(dict(id=cid, group=group, canonical=canon, asr=asr, expected=expected, actual=r.decision, reason=r.reason, ok=ok, note=note))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "case_results_01.json")
    json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    assert all(x["ok"] for x in rows)
