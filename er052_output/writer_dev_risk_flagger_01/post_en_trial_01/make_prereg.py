# -*- coding: utf-8 -*-
import json, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post_en_common import *
man = load_manifest(); est = json.load(open(os.path.join(HERE, "cost_estimate_post_en_01.json"), encoding="utf-8"))
sh3, sh4 = A.sha(A.antenna_system(3)), A.sha(A.antenna_system(4))
L1 = ["# PREREGISTRATION_01: WRITER-DEV-RISK-FLAGGER-POST-EN-TRIAL-01(Trial/DEV、2026-10-10、委任_01 Phase 1)", "",
"Phase 1(API費用JPY0)完了。費用見積が JPY100 以内のためFable判断どおりPhase 2へ進む。Productionコード・detectors・antenna_trial_01 は無変更。",
"", "## 1. 目的", "A3+A4 Risk Flaggerを『英訳後・音声化前』に置いた場合に、最終的にユーザーへ届く英語本文のFact RiskをHuman Review候補として拾えるかを、既存英語稿(FACTLOCK-ASTRA-E2E-TRIAL-01)で観察する。Trialのみ。Production実装・採否判断はしない。Risk FlaggerはCheckerではない(STOPしない・PASS/FAIL判定しない・自動Rewriteしない)。",
"", "## 2. 使用稿(11本)と台帳", "", "| Unit | Theme | 経路 | 区分 | 入力sha256 | 元path | 台帳 / Fact数 |", "|---|---|---|---|---|---|---|"]
for u in man["units"]:
    lg = man["ledgers"][u["ledger"]]
    L1.append("| %s | %s | %s | %s | `%s` | `%s` | `%s` sha `%s` / %d |" % (u["unit"], u["theme"], u["route"], u["status"], u["input_sha256"][:16], u["source_path"].split("factlock_astra_e2e_trial_01/")[1], lg["path"].split("factlock_astra_e2e_trial_01/")[1], lg["sha256"][:12], lg["parsed_facts"]))
L1 += ["", "詳細は INVENTORY_01.md / LEDGER_COMPLETENESS_01.md。全台帳でexpected=regex=parsed(PASS)。駆動時にも各セルで再assertする。",
"", "## 3. Flagger条件(ANTENNA-TRIAL-01から意味変更なし)", "",
"- A3 = `antenna_prompts.antenna_system(3)` sha256 `%s`(実使用版 = 元のANTENNA版、差分ゼロ。英語注記追加なし)" % sh3,
"- A4 = `antenna_prompts.antenna_system(4)` sha256 `%s`(同上)" % sh4,
"- A3/A4は累積設計(A4はA3の条件を含む)。Union = 同一(記事, 文ID)をA3/A4で重複除去(A3の出力 ∪ A4の出力)。",
"- A5/A6は使用しない。強制TopN禁止。0件許容。confidenceの新閾値は追加しない(全Flagを保存・報告。Human Review候補への採否はユーザーが判断)。重大定義は変更しない。自動Rewrite・再生成・記事STOPなし。",
"- モデル gpt-6.1-sol / effort=medium / Responses API / 1セル1呼び出し。価格は `er005_output/cost_baseline_01/pricing_snapshot.json` 登録値、USD/JPY=160。",
"- 再試行: 既存run_llmの形式再呼び出し1回+通信エラー2回まで(従来と同一)。それ以外のセル単位の再実行は同条件で最大1回、記録する。異常な再試行は禁止。",
"- 並列: 22セル(11本×A3/A4)を独立process並列(各セルは別ファイルに書込み、費用台帳は追記のみ)。",
"", "## 4. Union規則・集計定義(事前登録)", "",
"- sentence-level Flag総数 = A3件数 + A4件数。A3/A4 overlap = 同一(記事, 文ID)をA3とA4の両方がFlagした数。Union総数 = sentence-levelのユニーク(記事, 文ID)数。",
"- typeが異なっても同一(記事, 文ID)は1件にまとめ、両typeとconfidence(A3値/A4値)を併記する。",
"- 意味上の問題単位 = 同一の意味問題を複数文で指摘している場合は1件に束ねる(束ねた場合は束ね方を明記)。束ねはClaudeの機械的提案であり、有用/不要の最終ラベルは確定しない(ユーザー確認用)。",
"- 1記事あたり平均候補数 = Union総数 / 11、および意味上の問題単位数 / 11。同一テーマの複数稿(U03/X10、U02/X09、U07/X11)は別記事として数える。『8テーマ(U01-U08)のみ』の値も併記する。",
"", "## 5. 既知例対応表(事前登録。どの文IDか。旧Checkerを正解教師にしない)", "", "| 既知例 | Unit | 文ID(INVENTORY_01.md §3) | 備考 |", "|---|---|---|---|",
"| OpenAI actor drift | X11 | s7 | 『They also say the models' output copied or put articles together in new ways, and removed copyright management information.』 最重要。B1回復前STOP稿 |",
"| OpenAI(対照) | U07 | s11(主体OpenAI明示) / s1(見出しscope拡張。旧Checkがja_sourceでSTOPした点) | U07にはactor driftは無い |",
"| Semiconductor 不在断定(境界・過剰Flag確認) | U08 | s25(2文が1IDに結合) | ユーザー判断: 問題視するほどではない |",
"| Hormuz Brent→oil prices | X09 | s2, s13(U02には不在。U02 s27は正しい限定) | 本文に不在の稿(U02)は『検出できなかった』扱いにしない |",
"| Space 地球を吹き飛ばす | X10 | s5(U03には不在) | U03のs13/s33は別系統の不在断定(新規扱い) |",
"| BYD In One Line条件落ち | U05 | s27 | 台帳 BYD-RECALL-07系の『極端な場合に部品が外れた場合』条件の欠落 |",
"", "## 6. 費用", "",
"| 項目 | JPY |", "|---|---|", "| 見積 中央値(22呼び出し) | %.2f |" % est["total_central_jpy"], "| 見積 高位(入力+25%%・出力3倍) | %.2f |" % est["total_high_jpy"],
"| 新規呼び出し停止の累計上限(中央値の1.5倍) | %.2f |" % est["cap_total_jpy"], "| 1セル上限(MAX_CELL) | 8.00 |",
"| 参考: ANTENNA-TRIAL-01実測 | A3 1.919/call(max 2.883), A4 2.201/call(max 3.032)。入力は英語token数で補正(`cost_estimate_post_en_01.json`) |",
"", "見積 JPY%.2f <= JPY100 のため、Fable指示どおりPhase 2へ進む。累計が %.2f に達したら新規呼び出しを停止する。" % (est["total_central_jpy"], est["cap_total_jpy"]),
"", "## 7. STOP条件(固定)", "",
"英語稿所在/意味が想定と違う(→今回該当: 所在差異を INVENTORY_01.md §2 に記録し、Fable規則『既知例が別稿にのみ実在する場合は追加』に従い3本追加して続行。ユーザー判断用に報告)/ STOP稿が回収できない(該当なし)/ 台帳Fact件数不一致(該当なし)/ 判定仕様を変えないとA3/A4を英語に適用できない(該当なし)/ 新しい重大な仕様候補の発見 / 費用が見積から大きく逸脱 / Productionコード変更が必要 / 未承認仕様の参照が必要。",
"", "## 8. 出力先", "`er052_output/writer_dev_risk_flagger_01/post_en_trial_01/`: inputs/, flags/A3|A4/<unit>_<theme>.json, results/, logs/, cost_ledger_post_en_01.jsonl, cost_estimate_post_en_01.json, manifest_post_en_01.json, INVENTORY_01.md, LEDGER_COMPLETENESS_01.md, EN_ADAPTATION_01.md, PREREGISTRATION_01.md(本書)。Phase 3で RESULT_01.md / HUMAN_REVIEW_POST_EN_01.md を追加。"]
open(os.path.join(HERE, "PREREGISTRATION_01.md"), "w", encoding="utf-8").write("\n".join(L1) + "\n")
