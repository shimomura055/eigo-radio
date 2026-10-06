# -*- coding: utf-8 -*-
"""OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01 委任_01b: Trial対象セット構築(決定論、LLM不使用、gold非変更、Trial専用)。
記事文は labels_merged.json(逐語)から index で取得し、Ledger本文は verified_fact_ledger.txt から逐語取得する。"""
import json, re, sys, os
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(ROOT, "..", ".."))
LABELS = os.path.join(BASE, "er052_output", "open233_prod_e2e_02", "labels", "labels_merged.json")
LEDGERS = {"MUSE": os.path.join(BASE, "er019_output", "meta", "run_03", "ledger", "verified_fact_ledger.txt"),
           "HF": os.path.join(BASE, "er019_output", "family_x_refresh_e2e_01", "hormuz", "run_03", "ledger", "verified_fact_ledger.txt")}
STATES = ["AVAILABLE", "STOPPED", "PAUSED", "INCREASED", "DECREASED", "UNCHANGED", "STARTED", "ENDED", "EXPANDED", "NARROWED", "NOT_MENTIONED", "UNCLEAR"]
PAIRS = [["AVAILABLE", "STOPPED"], ["AVAILABLE", "PAUSED"], ["INCREASED", "DECREASED"], ["STARTED", "ENDED"], ["EXPANDED", "NARROWED"]]
COMPARES = ["SAME", "REVERSED", "NOT_MENTIONED", "UNCLEAR"]

# C. Ledger側正解の事前登録(Fable代理。委任_01aの語彙近似とは独立判断。basisはLedger本文の逐語部分文字列で、起動時に存在を検証する)
FACTS = {
 "MUSE-HC-012": ("STOPPED", True, "機能を当面ロールバックした", "ロールバック=撤回→STOPPED。「当面」の一時性からPAUSEDも許容(PAUSED/STOPPEDは逆転扱いしない)", ["STOPPED", "PAUSED"]),
 "HF-009": ("UNCHANGED", True, "ほどなく発表前に近い高い水準へ戻った", "一時縮小→高水準へ復帰=実質変化なし。一時縮小の記述は忠実文として許容", ["UNCHANGED"]),
 "HF-007": ("ENDED", True, "置き換えると投稿した", "20%案が投資案件へ置換=案の終了", ["ENDED"]),
 "HF-002": ("STARTED", True, "償還を求めると投稿した", "20%償還の提案が開始された(提案の出現)", ["STARTED"]),
 "HF-011": ("INCREASED", True, "1.7％上昇し", "Brent先物の上昇", ["INCREASED"]),
 "HF-003": ("UNCHANGED", False, "具体的制度設計は示されなかった", "状態変化なし(未提示)。方向性なし", ["UNCHANGED"]),
 "MUSE-HC-004": ("UNCHANGED", False, "散髪の予約、在庫確認", "機能説明。方向性なし", ["UNCHANGED"]),
 "MUSE-HC-006": ("UNCHANGED", False, "テストを実施した", "テスト実施の記述。状態の増減反転ではない。方向性なし", ["UNCHANGED"]),
 "MUSE-HC-010": ("UNCHANGED", False, "懸念を示した", "懸念表明。方向性なし", ["UNCHANGED"]),
 "MUSE-HC-013": ("UNCHANGED", False, "圧倒的に肯定的", "反応の記述。方向性なし", ["UNCHANGED"]),
}
def ledger_line(fid):
    path = LEDGERS["MUSE" if fid.startswith("MUSE") else "HF"]
    for ln in open(path, encoding="utf-8"):
        if f"] {fid}:" in ln:
            return ln.strip()
    raise SystemExit("ledger line not found: " + fid)
LEDGER_TEXT = {f: ledger_line(f) for f in FACTS}
for f, v in FACTS.items():
    assert v[2] in LEDGER_TEXT[f], ("basis not in ledger", f)
LAB = json.load(open(LABELS, encoding="utf-8"))["labels"]
def lab(i):
    return LAB[i]["claim"].split("|dup")[0]
ITEMS = []
def mk(iid, role, source, fixture, fid, sent, art, cmp_, label, origin, repeat=1, note="", acc=None):
    d = FACTS[fid]
    ITEMS.append({"id": iid, "role": role, "source": source, "fixture": fixture, "fact_id": fid, "ledger_fact_text": LEDGER_TEXT[fid],
        "article_sentence": sent, "expected_ledger_state": d[0], "acceptable_ledger_states": d[4], "has_direction": d[1],
        "ledger_basis_verbatim": d[2], "ledger_rationale": d[3], "expected_article_state": art, "expected_compare": cmp_,
        "acceptable_compare": acc or [cmp_], "label": label, "origin": origin, "repeat": repeat, "note": note})
# A-4 忠実(状態変化語あり): (labels idx, fact_id上書き, article_state)
FS = [(0,"HF-009","UNCHANGED"),(8,"HF-009","UNCHANGED"),(55,"HF-009","UNCHANGED"),(56,"HF-009","UNCHANGED"),(54,"HF-009","UNCHANGED"),
 (111,"HF-009","UNCHANGED"),(112,"HF-009","UNCHANGED"),(14,"HF-009","UNCHANGED"),(9,"HF-009","DECREASED"),(59,"HF-009","DECREASED"),
 (80,"HF-007","ENDED"),(12,"HF-007","ENDED"),(13,"HF-007","ENDED"),(60,"HF-002","STARTED"),(113,"HF-002","STARTED"),
 (3,"HF-003","UNCHANGED"),(53,"HF-003","UNCHANGED"),(1,"HF-003","UNCHANGED"),(48,"MUSE-HC-012","STOPPED"),(74,"MUSE-HC-012","PAUSED"),
 (81,"HF-011","INCREASED")]
for n, (i, fid, st) in enumerate(FS, 1):
    L = LAB[i]
    note = "" if L["fact_id"] in (fid, "MUSE-HC-012") or fid == L["fact_id"] else f"labels上のfact_id={L['fact_id']}を本文内容に合わせ{fid}へ補正"
    if st == "DECREASED":
        note += "一時縮小を述べる文(Ledgerに'一時的に上げ幅を縮小'あり)。SAME/UNCLEARを許容"
    mk(f"F-{n:02d}", "faithful_state", "labels_merged.json#%d" % i, L["run"], fid, lab(i), st, "SAME", "忠実", "新9 run ラベル問題なし", 1, note,
       ["SAME", "UNCLEAR"] if st == "DECREASED" else None)
# A-1 HC-012 同fact・状態言及なし(ラベル問題なし、重複文は1件へ)
used = {lab(i) for i, _, _ in FS} | {lab(66), lab(96), lab(103)}
seen = set(); n = 0
for i, L in enumerate(LAB):
    c = lab(i)
    if L["fact_id"] == "MUSE-HC-012" and c not in used and c not in seen and L["true_problem"] == "N":
        seen.add(c); n += 1
        mk(f"N-{n:02d}", "same_fact_not_mentioned", "labels_merged.json#%d" % i, L["run"], "MUSE-HC-012", c, "NOT_MENTIONED", "NOT_MENTIONED", "忠実", "新9 run HC-012紐づき(ラベル問題なし)", 1,
           "HC-012に紐づくが状態変化(撤回/復元)を述べない文")
# A-1/A-2/A-3 真の方向反転gold・曖昧(repeat 3)
mk("G-01", "gold_reversal", "labels_merged.json#66", LAB[66]["run"], "MUSE-HC-012", lab(66), "AVAILABLE", "REVERSED", "真の反転", "HC-012今回実例(ラベル重大、新9 run meta_run03_advanced)", 3, "restored系。Ledgerはロールバック")
mk("G-02", "gold_reversal", "design_open233_self_recovery_flow_01.md:1707 / SAFETY_CRITICAL_CLAIM_DEFS safety_A5 A5-0", "safety_A5(meta)", "MUSE-HC-012",
   "They also temporarily put back the feature in which humans handled the calls.", "AVAILABLE", "REVERSED", "真の反転", "gold A5-0(重大)", 3, "時期・経過の創作型(一度消えて戻った出来事にする)。方向(撤回→復活)としても反転")
mk("G-03", "gold_reversal", "委任_60 重大期待(合成、HF-009に比較を付けた例) / sensor_quality_01.md C表D61合成", "合成(委任_60)", "HF-009",
   "After the plan was withdrawn, oil prices fell.", "DECREASED", "REVERSED", "真の反転", "委任_60 重大期待の明確な方向反転(比較系)", 3,
   "Ledger=UNCHANGED(高水準へ復帰)に対しDECREASEDは固定ペア外。goldは重大扱い。機械比較がUNCLEAR(判断不能)でも許容として別計上", ["REVERSED", "UNCLEAR"])
mk("G-04", "ambiguous", "labels_merged.json#108 / 委任_46 K16", LAB[108]["run"], "HF-009", lab(108), "UNCLEAR", "UNCLEAR", "曖昧", "K16(ラベル重大・時期型。方向反転でなく『継続中の出来事が一度消えて戻った』創作)", 3,
   "方向ペアに当たらない時期型。UNCLEAR(判断不能)が適切で、REVERSEDとして誤検出しないことも確認", ["UNCLEAR", "SAME"])
mk("G-05", "ambiguous", "委任_46_result K19 / 委任_60 例(QUALITY)", "hormuz(委任_46)", "HF-009",
   "Just after the charge plan disappeared, prices began to fall. Soon, however, they returned to a high level.", "UNCLEAR", "UNCLEAR", "曖昧", "K19(QUALITY、比較系の過剰判定例)", 3,
   "一時下落→復帰でLedgerの『一時縮小→復帰』と概ね整合。SAME/UNCLEARを許容(REVERSEDは誤検出)", ["SAME", "UNCLEAR"])
mk("G-06", "ambiguous", "labels_merged.json#96 (同文#103)", LAB[96]["run"], "MUSE-HC-012", lab(96), "UNCLEAR", "UNCLEAR", "曖昧",
   "ラベル問題なしだがG-01(restored)と近接した表現", 3, "『changed...back to how it was before』は撤回とも復活とも読める。AI揺れ確認用。SAME/UNCLEARを許容", ["UNCLEAR", "SAME"])
# A-5 非該当(方向性なしfact)
for n, (i, fid) in enumerate([(43, "MUSE-HC-004"), (93, "MUSE-HC-013"), (44, "MUSE-HC-010"), (36, "MUSE-HC-006"), (71, "MUSE-HC-006")], 1):
    mk(f"ND-{n:02d}", "non_directional", "labels_merged.json#%d" % i, LAB[i]["run"], fid, lab(i), "NOT_MENTIONED", "NOT_MENTIONED", "忠実", "新9 run(ラベル問題なし)", 1,
       "状態変化を含まないfactに紐づく文。方向性なし(has_direction=false)のため比較不要が期待")
# B. 人工反転文(決定論): (元表現, 置換後, 置換後の記事側state)。最初に成立した1規則のみ適用。LLM不使用。
RULES = [("pulled back", "restored", "AVAILABLE"), ("put the human-call feature back on hold", "put the human-call feature back in service", "AVAILABLE"),
 ("would drop", "would launch", "STARTED"), ("left the stage", "took the stage", "STARTED"), ("suddenly appeared", "suddenly disappeared", "ENDED"),
 ("The rise", "The drop", "DECREASED"), ("was withdrawn", "was reinstated", "STARTED"), ("The fee plan vanished", "The fee plan appeared", "STARTED"),
 ("# The Fee Plan Leaves", "# The Fee Plan Arrives", "STARTED"), ("briefly gave up", "briefly added", "INCREASED"), ("briefly lost", "briefly added", "INCREASED"),
 ("did not fall", "fell", "DECREASED"),
 ("restored", "rolled back", "STOPPED"), ("resumed", "suspended", "PAUSED"), ("increased", "decreased", "DECREASED"), ("expanded", "narrowed", "NARROWED"),
 ("started", "stopped", "ENDED"), ("reinstated", "withdrew", "ENDED"), ("raised", "lowered", "DECREASED"), ("extended", "shortened", "NARROWED"), ("added", "removed", "DECREASED")]
STRICT = {"MUSE-HC-012", "HF-007", "HF-002", "HF-011"}  # Ledger stateが固定ペアを持つfact
base = [it for it in ITEMS if it["role"] == "faithful_state"]
synth = []
for it in base:
    for a, b, st in RULES:
        if a in it["article_sentence"] and len(synth) < 20:
            s = it["article_sentence"].replace(a, b, 1)
            strict = it["fact_id"] in STRICT
            synth.append((it, s, st, strict, a, b)); break
for n, (it, s, st, strict, a, b) in enumerate(synth, 1):
    mk(f"S-{n:02d}", "synthetic_reversal", f"synthetic_reversal_01.py(元={it['id']}、置換『{a}』→『{b}』)", it["fixture"], it["fact_id"], s, st, "REVERSED", "人工反転", "決定論置換(LLM不使用、Trial専用)", 1,
       f"元文: {it['article_sentence']} / " + ("Ledger stateと固定ペアを成す反転" if strict else "Ledger=UNCHANGED等で固定ペア外。REVERSED/UNCLEARを許容(UNCLEAR=判断不能として別計上)"),
       None if strict else ["REVERSED", "UNCLEAR"])
    ITEMS[-1]["original_item_id"] = it["id"]
# E. 出力
from collections import Counter
cnt = Counter(it["role"] for it in ITEMS); lab_cnt = Counter(it["label"] for it in ITEMS)
calls = sum(it["repeat"] for it in ITEMS)
out = {"purpose": "OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01 Trial対象セット(事前登録、委任_01b、Trial専用・gold非変更)",
 "enums": {"result_state": STATES, "direction_pairs": PAIRS, "expected_compare": COMPARES, "note": "PAUSED vs STOPPEDは一時性の差で逆転扱いしない"},
 "fact_registry": {f: {"ledger_text": LEDGER_TEXT[f], "expected_ledger_state": v[0], "acceptable_ledger_states": v[4], "has_direction": v[1], "basis_verbatim": v[2], "rationale": v[3]} for f, v in FACTS.items()},
 "summary": {"items": len(ITEMS), "by_role": dict(cnt), "by_label": dict(lab_cnt), "total_calls_estimate": calls,
  "repeat3_items": [it["id"] for it in ITEMS if it["repeat"] == 3]},
 "items": ITEMS}
json.dump(out, open(os.path.join(ROOT, "testset_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
RN = {"gold_reversal": "真の反転(gold)", "faithful_state": "忠実(状態変化語あり)", "same_fact_not_mentioned": "忠実(HC-012同fact・状態言及なし)",
      "synthetic_reversal": "人工反転", "non_directional": "非該当(方向性なしfact)", "ambiguous": "曖昧"}
md = ["# Trial対象セット 内訳(委任_01b、事前登録)", "", "| 区分 | 項目数 | 合計call(項目数xrepeat) |", "|---|---|---|"]
for r in RN:
    md.append(f"| {RN[r]} | {cnt[r]} | {sum(i['repeat'] for i in ITEMS if i['role'] == r)} |")
md += [f"| **合計** | {len(ITEMS)} | {calls} |", "", f"label別: {dict(lab_cnt)}", "", "## 人工反転 一覧", "", "| id | 元 | 置換 | 記事文 | 厳密/許容 |", "|---|---|---|---|---|"]
for i in ITEMS:
    if i["role"] == "synthetic_reversal":
        md.append(f"| {i['id']} | {i['original_item_id']} | {i['source'].split('置換')[1].rstrip(')')} | {i['article_sentence']} | {'厳密' if len(i['acceptable_compare']) == 1 else 'REVERSED/UNCLEAR許容'} |")
md += ["", "## repeat=3", "", ", ".join(it["id"] for it in ITEMS if it["repeat"] == 3), "", "詳細(Ledger本文逐語・根拠・enum)は testset_01.json。"]
open(os.path.join(ROOT, "testset_01.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print(dict(cnt), dict(lab_cnt), "items", len(ITEMS), "calls", calls)
