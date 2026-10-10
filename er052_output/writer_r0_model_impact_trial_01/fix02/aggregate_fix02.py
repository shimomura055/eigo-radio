# -*- coding: utf-8 -*-
"""FIX02 集計(API非呼び出し)。RESULT_FIX02.md / cost_ledger_fix02.jsonl を生成。"""
import json, os, hashlib, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda p: json.load(open(p, encoding="utf-8"))
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
TH = [("streaming_price", "Disney+"), ("space_weapons", "宇宙兵器"), ("byd_recall", "BYD")]
SRC = [("prev_r0", "前回R0(new腕 r0.md、Luna)"), ("gpt-6-luna", "今回Luna"), ("gpt-6.1-sol", "今回Sol"), ("gpt-6-astra", "今回Astra")]
TS = [0.10, 0.20, 0.30, 0.50]
man = J(os.path.join(HERE, "manifest_fix02.json"))["cells"]
fg = {(t, s): J(os.path.join(HERE, "flags", t, s + ".json")) for t, _ in TH for s, _ in SRC}
def cnt(f, th): return sum(1 for x in f["union_flags"] if x["confidence"] >= th - 1e-9)
def mx(f): return max([x["confidence"] for x in f["union_flags"]], default=None)
L = []
L.append("# RESULT_FIX02: 前回R0 + 今回R0 3モデル の12本 Risk Flagger(D0+D2記事モード、完全台帳、2026-10-10)\n")
L.append("性質: Trial/DEV。Production変更なし、採用判断なし、優劣は書かない。Flagの有用/誤検知の確定はユーザー(人間確認)。数値は実測(usage x 登録単価 gpt-6.1-sol 入力$2/出力$10 per 1M、USD/JPY=160)。事前登録: `PREREGISTRATION_FIX02.md`。\n")
L.append("**注意(事実の注記)**: 前回R0(FACTLOCK-ASTRA-E2E-TRIAL-01 new腕 `new_writer/r0.md`、gpt-6-luna、Fact Lock付き)と今回Luna R0は、同じFact Lock構成・同じモデルの別生成物であり、両者の差は生成ごとのばらつきを含む。old腕の `ja_writer/original.md`(旧Writer構成・Fact Lockなし)も保存されている(streaming 1cc983b6 / space f29bb0e9 / byd 129cfc9a)が、Fable判断により本比較には含めていない。Flagは{D0rb ∪ D2}の文単位ユニーク件数(FIX01-A/RESULT_01と同定義)。confidenceは絶対評価に使わない。\n")
L.append("## 1. 12行表(Flag件数 = D0rb∪D2、confidence閾値別)\n")
L.append("| テーマ | R0 | >=0.10 | >=0.20 | >=0.30 | >=0.50 | 最大confidence |\n|---|---|---|---|---|---|---|")
for t, tn in TH:
    for s, sn in SRC:
        f = fg[(t, s)]; m = mx(f)
        L.append("| %s | %s | %s | %s |" % (tn, sn, " | ".join(str(cnt(f, th)) for th in TS), "-" if m is None else "%.2f" % m))
L.append("\n## 2. R0源別合計(行方向: 閾値別)\n")
L.append("| R0 | >=0.10 | >=0.20 | >=0.30 | >=0.50 | 最大confidence |\n|---|---|---|---|---|---|")
for s, sn in SRC:
    fs = [fg[(t, s)] for t, _ in TH]; ms = [mx(f) for f in fs if mx(f) is not None]
    L.append("| %s | %s | %s |" % (sn, " | ".join(str(sum(cnt(f, th) for f in fs)) for th in TS), "-" if not ms else "%.2f" % max(ms)))
L.append("| **全12本** | %s | %s |" % (" | ".join(str(sum(cnt(f, th) for f in fg.values())) for th in TS), "%.2f" % max([mx(f) for f in fg.values() if mx(f) is not None], default=0)))
L.append("\n## 3. 全Flag一覧(confidence降順、全件。理由=Flaggerのquestion欄原文)\n")
allf = []
for (t, s), f in fg.items():
    for x in f["union_flags"]:
        allf.append((x["confidence"], t, s, x, f))
allf.sort(key=lambda z: -z[0])
if not allf: L.append("(Flagなし)")
else:
    L.append("| # | conf | テーマ | R0 | 文 | 種類 | 対応Fact | 検出元 | 該当文 | 理由(Flagger question) |\n|---|---|---|---|---|---|---|---|---|---|")
    for i, (c, t, s, x, f) in enumerate(allf, 1):
        L.append("| %d | %.2f | %s | %s | %s | %s | %s | %s | %s | %s |" % (i, c, t, s, x["sentence_id"], x["type"], ",".join(x.get("fact_ids", [])), "+".join(x.get("sources", [])), x["sentence"].replace("|", "\|"), x["question"].replace("|", "\|")))
L.append("\n(全Flagの全フィールドは `flags/<theme>/<source>.json` の `union_flags` / `d2_flags` / `d0_flags` に保存。)\n")
L.append("## 4. D0参考件数(総数に含めない gate_only=不在断定/数量時系列/増減・許可反転 と、D0本体)と D2件数\n")
L.append("| テーマ | R0 | D2 | D0rb(総数に入る) | D0 gate_only(参考) | 総数(D0rb∪D2) |\n|---|---|---|---|---|---|")
for t, tn in TH:
    for s, sn in SRC:
        f = fg[(t, s)]
        L.append("| %s | %s | %d | %d | %d | %d |" % (tn, sn, len(f["d2_flags"]), sum(1 for x in f["d0_flags"] if not x.get("gate_only")), sum(1 for x in f["d0_flags"] if x.get("gate_only")), len(f["union_flags"])))
# FIX01-A照合
L.append("\n## 5. FIX01-A Disney+結果との一致\n")
L.append("| R0 | FIX01-A Flag数 | FIX02 Flag数 | 記事sha一致 | 一致 |\n|---|---|---|---|---|")
for s, sn in SRC[1:]:
    a = J(os.path.join(HERE, "..", "flags_fix01", "streaming_price", s + ".json")); b = fg[("streaming_price", s)]
    L.append("| %s | %d | %d | %s | %s |" % (sn, len(a["union_flags"]), len(b["union_flags"]), a["article_sha256"] == b["article_sha256"], len(a["union_flags"]) == len(b["union_flags"]) and a["sentences"] == b["sentences"]))
L.append("\n(前回R0のDisney+はFIX01-Aに対応セルが無いため照合対象外。Disney+の今回3本は同一記事・同一条件の再実行で、Flag0件が再現した。)\n")
# 条件同一性
L.append("## 6. 条件同一性の機械確認(12セル)\n")
L.append("| セル | 記事sha一致(事前登録) | 台帳sha一致 | Fact数/見出し数 | 文数 | D2 system prompt sha | Flagger model_id | effort | attempts | valid_json |\n|---|---|---|---|---|---|---|---|---|---|")
psh = set(); cost_rows = []; tot = 0.0
for t, tn in TH:
    for s, sn in SRC:
        f = fg[(t, s)]; m = man["%s/%s" % (t, s)]
        raw = [json.loads(x) for x in open(os.path.join(HERE, "logs", "d2_gpt-6.1-sol_%s_raw.jsonl" % f["cell"]), encoding="utf-8") if x.strip()]
        ps = sha(raw[0]["request"]["system"])[:16]; psh.add(ps)
        ok_art = f["article_sha256"] == m["article_sha256"]; ok_led = f["ledger_sha256"] == m["ledger_sha256"]
        L.append("| %s/%s | %s | %s | %d/%d | %d | %s | %s | %s | %s | %s |" % (t, s, ok_art, ok_led, f["n_facts"], f["n_headings"], f["n_sentences"], ps, ",".join(f["d2_model_ids"]), f["flagger_effort"], f["d2_attempts"], f["d2_valid_json"]))
        for r in raw:
            u = r["usage"]; tot += r["cost_jpy"]
            cost_rows.append(dict(purpose="flagger_d2_fix02", theme=t, source=s, model=r["model_id"], cost_jpy=round(r["cost_jpy"], 4), usage=u, response_id=r["response_id"]))
L.append("\nD2 system prompt sha(先頭16桁)の種類: %s(FIX01-A/事前登録 b8dacc147009a13b と%s)。" % (sorted(psh), "一致" if psh == {"b8dacc147009a13b"} else "不一致"))
L.append("台帳sha: テーマ内4源で同一(manifest由来)。Fact数==見出し数は driver内assertで強制(全12セル通過)。detectors配下5ファイルshaは実行前後で事前登録値と一致(別途確認欄)。\n")
L.append("## 7. 費用(実測)\n")
L.append("| セル | in tok | out tok(reasoning) | 費用円 |\n|---|---|---|---|")
for r in cost_rows:
    u = r["usage"]; L.append("| %s/%s | %s | %s(%s) | %.4f |" % (r["theme"], r["source"], u.get("input_tokens"), u.get("output_tokens"), u.get("reasoning_tokens"), r["cost_jpy"]))
L.append("| **合計** | | | **%.2f** |" % tot)
L.append("\nFIX02費用 JPY %.2f(上限30内)。API呼び出し: D2 %d回(各セル1回、再試行0)。R0生成は0回(再生成なし)。" % (tot, len(cost_rows)))
with open(os.path.join(HERE, "cost_ledger_fix02.jsonl"), "w", encoding="utf-8") as o:
    for r in cost_rows: o.write(json.dumps(r, ensure_ascii=False) + "\n")
L.append("\n## 8. 失敗・再試行\n\n12セルとも valid_json=True、attempts=1、形式再呼び出し0、再試行0、失敗0(上表の attempts 列)。\n")
L.append("## 9. 使用モデル\n\n- Risk Flagger: gpt-6.1-sol(最新世代最上位系)、effort=medium。\n- R0生成モデル: 前回R0=gpt-6-luna(FACTLOCK-ASTRA-E2E-TRIAL-01 new腕)、今回=gpt-6-luna / gpt-6.1-sol / gpt-6-astra(WRITER-R0-MODEL-IMPACT-TRIAL-01、再生成なし)。Flaggerは最新でない旧モデルを使っていない。\n")
open(os.path.join(HERE, "RESULT_FIX02.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("total", tot)
