# -*- coding: utf-8 -*-
"""Trial B 結果集計(read-only、API無し、費用0)。trial_b_results_01.json -> trial_b_summary_01.json + 表のmarkdown。"""
import io, json, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er058_trial_b_intentional_misread_01 as tb

OUT = os.path.join(ROOT, "er058_output", "trial_abc")
r = json.load(open(os.path.join(OUT, "trial_b_results_01.json"), encoding="utf-8"))
clips = [c for c in r["clips"].values() if "asr" in c]
SRC = ["primary", "azure", "local_medium", "azure_pl"]

STRICT = {"EXACT_MATCH", "NORMALIZED_MATCH", "TRANSCRIPT_STYLE_NORMALIZED_MATCH", "NUMERIC_EQUIVALENCE_MATCH"}
lenient_only = []
for c in clips:
    # Secondary候補(azure/azure_pl/local_medium)は現行SCGと同じ厳格PASS集合(EXACT/NORMALIZED系)のみをPASSとする。
    # Primaryはvalidatorのshould_passそのまま(PHONETIC_MATCH等を含む)。
    for sname, jj in c["judge"].items():
        jj["pass_lenient"] = jj["pass"]
        if sname != "primary" and jj["pass"] and jj["cls"] not in STRICT:
            jj["pass"] = False
            lenient_only.append((c["clip_id"], sname, jj["cls"], c["asr"][sname]["text"]))
for c in clips:
    # 話された形(spoken)と一致する転写か(= ASRが実際に誤読形を聴いたか)
    c["heard_spoken"] = {}
    for s, v in c["asr"].items():
        j = tb.classify(c["lang"], c["spoken"], v["text"])
        c["heard_spoken"][s] = j["pass"]
    c["ground"] = None
    if c["kind"] == "misread":
        main3 = [c["heard_spoken"].get(s) for s in ("primary", "azure", "local_medium")]
        fails = [s for s in ("primary", "azure", "local_medium") if not c["judge"][s]["pass"]]
        if c["base"] == "ja_min2":
            # 紹介/照会は同音(しょうかい)。音声は原稿と区別不能で、誤読ではない(検出不能かつ無害)。誤PASS集計から除外。
            c["ground"] = "homophone_no_audio_difference"
        elif any(main3) and fails:
            c["ground"] = "confirmed_misread"          # 話した形をASRが聴いた(原稿と不一致のASRあり)
        elif fails:
            c["ground"] = "divergence_evidence"        # 原稿と不一致のASRがある(話した形と一致する転写は無い)
        elif any(main3):
            c["ground"] = "confirmed_misread_same_text_readings"
        else:
            c["ground"] = "unverified(全ASRが原稿形)"
def flow(c):
    j = c["judge"]
    if j["primary"]["pass"]:
        return "ADOPT_P"
    if j["azure"]["pass"]:
        return "ADOPT_S"
    return "REJECT"


for c in clips:
    c["flow"] = flow(c)

summary = {"by_type": {}, "overall": {}}
lines = []


def rate(n, d):
    return f"{n}/{d}" + (f" ({100*n/d:.0f}%)" if d else "")


mis = [c for c in clips if c["kind"] == "misread"]
ctl = [c for c in clips if c["kind"] == "control"]
conf = [c for c in mis if c["ground"] in ("confirmed_misread", "divergence_evidence", "confirmed_misread_same_text_readings")]
lines.append("### 全体(Primary=validator should_pass、Secondary候補=厳格PASS集合[EXACT/NORMALIZED/TRANSCRIPT_STYLE_NORMALIZED/NUMERIC_EQUIVALENCE]のみPASS)")
lines.append("緩い基準(should_passのみ)ではPASSだが厳格集合ではNGとなったSecondary候補転写: " + "; ".join(f"{a}/{b}={d}「{e}」" for a, b, d, e in lenient_only))
lines.append("| 指標 | 件数 |")
lines.append("|---|---|")
lines.append(f"| clip総数(誤読/対照) | {len(clips)} ({len(mis)}/{len(ctl)}) |")
lines.append(f"| 誤読のうち誤読の証拠あり(ASRが誤読形を聴いた/原稿と不一致のASRあり/同形異音。以下「確認済み誤読」) | {len(conf)}/{len(mis)} |")
lines.append(f"| 誤読のうち全ASRが原稿形で転写(未確定)+同音除外 | {len(mis)-len(conf)} |")
for s in SRC:
    pool = [c for c in conf if s in c["judge"]]
    fp = [c for c in pool if c["judge"][s]["pass"]]
    poolc = [c for c in ctl if s in c["judge"]]
    fn = [c for c in poolc if not c["judge"][s]["pass"]]
    lines.append(f"| 誤PASS率(確認済み誤読, {s}) | {rate(len(fp), len(pool))} |")
    lines.append(f"| 誤NG率(対照, {s}) | {rate(len(fn), len(poolc))} |")
    summary["overall"][s] = {"false_pass": [len(fp), len(pool)], "false_ng_control": [len(fn), len(poolc)]}
wrong_adopt = [c for c in conf if c["flow"] != "REJECT"]
wrong_by_sec = [c for c in conf if c["flow"] == "ADOPT_S"]
ctl_rej = [c for c in ctl if c["flow"] == "REJECT"]
lines.append(f"| 統一フロー: 確認済み誤読の誤採用(Primary or Azure PASS) | {rate(len(wrong_adopt), len(conf))} |")
lines.append(f"| うちPrimaryがNG→SecondaryのPASSで誤採用(Secondary起因) | {len(wrong_by_sec)} |")
lines.append(f"| 統一フロー: 対照(正しい発話)の不採用(再生成対象) | {rate(len(ctl_rej), len(ctl))} |")
summary["overall"]["flow"] = {"wrong_adopt": len(wrong_adopt), "wrong_by_secondary": len(wrong_by_sec), "n_confirmed": len(conf),
                              "control_rejected": len(ctl_rej), "n_control": len(ctl)}

for lang in ("en", "ja"):
    lines.append(f"\n### 型別({lang})。誤PASS = 確認済み誤読で原稿に対しPASS判定。表記: 誤PASS/確認済み誤読(母数)")
    lines.append("| 型 | 誤読clip | 確認済み | Primary誤PASS | Azure誤PASS | Azure+PL誤PASS | local誤PASS | 統一フロー誤採用 | 対照 | 対照誤NG(P/A/L) | 対照フロー不採用 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    types = []
    for c in clips:
        if c["lang"] == lang and c["type"] not in types:
            types.append(c["type"])
    for t in types:
        m = [c for c in mis if c["lang"] == lang and c["type"] == t]
        cf = [c for c in m if c["ground"] in ("confirmed_misread", "divergence_evidence", "confirmed_misread_same_text_readings")]
        ct = [c for c in ctl if c["lang"] == lang and c["type"] == t]

        def fpc(s):
            pool = [c for c in cf if s in c["judge"]]
            return rate(sum(1 for c in pool if c["judge"][s]["pass"]), len(pool))

        def fnc(s):
            pool = [c for c in ct if s in c["judge"]]
            return f"{sum(1 for c in pool if not c['judge'][s]['pass'])}/{len(pool)}"
        lines.append(f"| {t} | {len(m)} | {len(cf)} | {fpc('primary')} | {fpc('azure')} | {fpc('azure_pl')} | {fpc('local_medium')} | "
                     f"{sum(1 for c in cf if c['flow']!='REJECT')}/{len(cf)} | {len(ct)} | P{fnc('primary')} A{fnc('azure')} L{fnc('local_medium')} | "
                     f"{sum(1 for c in ct if c['flow']=='REJECT')}/{len(ct)} |")

lines.append("\n### clip別詳細(原稿 / 話した文 / 各ASR転写→判定)")
lines.append("| clip | 種別 | 原稿 | 話した文 | Primary | Azure | Azure+PL | local medium | フロー | 確認 |")
lines.append("|---|---|---|---|---|---|---|---|---|---|")


def cell(c, s):
    if s not in c["asr"]:
        return "-"
    t = (c["asr"][s]["text"] or "").replace("|", "/")
    j = c["judge"][s]
    return f"{t} [{'PASS' if j['pass'] else 'NG'}:{j['cls'][:14]}]"


for c in sorted(clips, key=lambda x: (x["lang"], x["type"], x["clip_id"])):
    lines.append(f"| {c['clip_id']} | {c['kind']} | {c['canonical']} | {c['spoken']} | {cell(c,'primary')} | {cell(c,'azure')} | {cell(c,'azure_pl')} | {cell(c,'local_medium')} | {c['flow']} | {c['ground'] or ''} |")

# 誤PASS事例
lines.append("\n### 誤PASS事例(確認済み誤読で、いずれかのASRが原稿に対しPASS)")
ex = []
for c in conf:
    for s in SRC:
        if s in c["judge"] and c["judge"][s]["pass"]:
            ex.append((c["clip_id"], s, c["canonical"], c["spoken"], c["asr"][s]["text"], c["judge"][s]["cls"], c["flow"]))
for e in ex:
    lines.append(f"- {e[0]} / {e[1]}: 原稿「{e[2]}」 話した「{e[3]}」 転写「{e[4]}」 判定={e[5]} フロー={e[6]}")
summary["false_pass_examples"] = ex
summary["unverified_misreads"] = [(c["clip_id"], c["spoken"], {s: v["text"] for s, v in c["asr"].items()}) for c in mis if str(c["ground"]).startswith(("unverified", "homophone"))]

# JA C1(entity_like)除外を外した場合
lines.append("\n### 日本語: Primary NGの内訳とC1(entity_like)")
for c in [x for x in clips if x["lang"] == "ja" and x["kind"] == "misread"]:
    jp, ja = c["judge"]["primary"], c["judge"]["azure"]
    lines.append(f"- {c['clip_id']}: Primary={'PASS' if jp['pass'] else 'NG'}({jp['cls']}, entity_like={jp['entity_like']}) / Azure={'PASS' if ja['pass'] else 'NG'}({ja['cls']}) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外")
json.dump(summary, open(os.path.join(OUT, "trial_b_summary_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(os.path.join(OUT, "trial_b_tables_01.md"), "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
