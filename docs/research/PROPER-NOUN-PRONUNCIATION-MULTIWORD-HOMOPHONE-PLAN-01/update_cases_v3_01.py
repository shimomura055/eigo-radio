"""PNMH-PLAN-01 委任_03(API 0): TRIAL_CASES_01.json へユーザー判断(2026-10-22)を反映。既存30件はそのまま、`after_v3`(V8+ストレス無視)を追加し、
v2計画書にだけあった追加ケース(BI1/BI2/NX1/CS1-3/RS1/H1)と v3新規(BI3/PH1/PH2)をJSON化。期待値の意味: PASS=救済すべき / NOT_PASS=救済してはならない / KEEP=現行判定維持"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import proto_multiword_span_01 as P
val = P.val
import er006_secondary_asr_01 as sec
def judge(c, a):
    r = val.classify_asr_match(c, a)
    if r.should_pass: return "PASS(" + r.classification + ")"
    if sec.is_entity_like_mismatch(r) or sec.is_homophone_candidate_mismatch(r):
        lab = sec._step_alternate_pass(r)
        if lab: return "PASS(" + lab + ")"
    return "NOT_PASS(" + r.classification + ")"
path = os.path.join(HERE, "TRIAL_CASES_01.json")
cases = json.load(open(path, encoding="utf8"))
cases = [c for c in cases if c["id"] not in {"BI1","BI2","NX1","CS1","CS2","CS3","RS1","H1","BI3","PH1","PH2"}]  # 冪等
S = "The service is called %s now."
new = [
 ("BI1", "Bi-us型(ユーザー判断: NG維持)", S % "bias", S % "Bi-us", "NOT_PASS", "ユーザー判断2026-10-22『Bi-us型は現行仕様に従いNG維持』。CURRENT_SPEC.md:454整合。V8ガード(2字token bi は機能語集合外)で非救済", "v2計画§3-1b"),
 ("BI2", "実データ(runtime evidence: 実音声の誤発音)", "byUs is pronounced bias.", "BAUS is pronounced Bi-us.", "NOT_PASS", "CURRENT_SPEC.md:454 runtime_evidence_x.json。byus→baus(OOV)が残るため救済なし", "v2計画§3-1b"),
 ("NX1", "数字ゲート例外の共存(要審査)", "byUs has two apps.", "Buy us has to apps.", "REVIEW", "two→toの同音扱いは1:1でも現行PASS。n:m同音と共存するPASSが新規になる点を目視審査(v2 R-04a)", "v2計画§3-1b"),
 ("CS1", "connected-speech迂回(他の内容語差が残る)", "Please check this stuff with byUs now.", "Please check this tough with buy us now.", "NOT_PASS", "他差分(stuff→tough)が残る→従来評価でNG", "v2計画§3-1b"),
 ("CS2", "connected-speech迂回(K7実例型)", "Walk uphill slowly with byUs.", "Walk a pill slowly with buy us.", "NOT_PASS", "uphill→a pill が残る", "v2計画§3-1b"),
 ("CS3", "固有名詞差混在", "Melos met byUs today.", "Mellow s met buy us today.", "NOT_PASS", "Melos→Mellow s は辞書外+文字読みで非救済", "v2計画§3-1b"),
 ("RS1", "単純n:m正例の周辺文", "He said the byUs team won the match.", "He said the buy us team won the match.", "PASS", "音素一致(ストレス差のみ)", "v2計画§3-1b"),
 ("H1", "既存の穴(Tse→sea。U5未決: 悪化させない・是正しない)", "Kristie Tse spoke first.", "Kristie Sea spoke first.", "KEEP", "現行でPASS(entity_like∧homophone_candidateで全variant一致)。U5はユーザー未回答→是正せず悪化させない", "v2計画§3-1b"),
 ("BI3", "既知の残存(機能語by: bias⇔by us)", S % "bias", S % "by us", "PASS", "音素は同一(B AY1 AH0 S)。『発音が同じなら単語数・綴りでNGにしない』に沿う。ただし区切って読まれた場合との区別は音素列だけでは不可(DESIGN_OPTIONS §4-3の限界)。Trial層Cで要審査", "v3新規"),
 ("PH1", "音素相違=NG(ユーザー判断)", S % "byUs", S % "buy us on", "NOT_PASS", "音素が異なる実際の誤発音/追加語はNG", "v3新規"),
 ("PH2", "音素相違=NG(ストレス差ではなく音素差)", S % "byUs", S % "buy a", "NOT_PASS", "buy a=B AY1 AH0 に終端Sなし", "v3新規"),
]
for cid, kind, c, a, exp, basis, origin in new:
    cases.append(dict(id=cid, kind=kind, canonical=c, asr=a, expect=exp, label_basis=basis, origin=origin, stage="O+P"))
for c in cases: c["before"] = judge(c["canonical"], c["asr"])
P.install_proto()
val.__dict__["PROTO_MULTIWORD"] = lambda c, a: P.multiword_span_equivalent_v3(c, a)
for c in cases:
    c["after_v3"] = judge(c["canonical"], c["asr"])
    exp = c["expect"]
    if exp == "PASS": c["ok_v3"] = c["after_v3"].startswith("PASS")
    elif exp == "NOT_PASS": c["ok_v3"] = c["after_v3"].startswith("NOT_PASS")
    elif exp == "REVIEW": c["ok_v3"] = c["after_v3"] == "PASS(HOMOPHONE_MATCH_NUMBER_EXCEPTION)"   # 要審査: v2事前測定値と一致することのみ確認(合否判断は目視)
    else: c["ok_v3"] = c["after_v3"] == c["before"]
    c.pop("after", None) if False else None
json.dump(cases, open(path, "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1)
print(len(cases), "cases; NG(v3):", [c["id"] for c in cases if not c["ok_v3"]])
for c in cases: print("|", c["id"], "|", c["expect"], "|", c["before"], "|", c.get("after", ""), "|", c["after_v3"], "|", "OK" if c["ok_v3"] else "**NG**")
