# 委任_01: Phase 1 事実調査・原因特定・根本対策設計・Trial計画(B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01、2026-10-10)

範囲: read-only。課金API 0件。Production code/Prompt/CURRENT_SPEC変更なし。git操作(add/commit/checkout/stash)なし(Lane A 委任_07が並行してmain/branchを操作中のため)。
書込み: `er052_output/b3_fact_instruction_separation_trial_01/`(新規)、本ログ、`docs/pm/RESULT_PACKET_B3SEP_01.md`のみ。ACTIVE_TASK.md / RESULT_PACKET.md / SSOTは未編集。

## 実施内容
1. B3生成経路の再構成(Researcher→Verification→Ledger text→B3→Writer R0→Fact Lock)をファイル:関数:行で表化(INVESTIGATION_01.md 1節)。
2. 5問題テーマ+正常系4テーマの混入文を1件ずつ逆追跡(`trace_5themes.json`、`INVESTIGATION_01.md` 2節)。
3. 設計意図の確認(DECISION_LOG L9573-9575 / L20123、`docs/pm/b3_brief_structure_hypothesis_01.md`、Researcher Prompt L161、Fact Lock R0規則4、注記仕様v2 §2)。
4. 根本対策候補A'/B/C/D/Eの設計(DESIGN_01.md)。¥0予備検証(Dのreplay)を実施。
5. Trial計画・事前登録・費用見積(PREREGISTRATION_01.md)。
6. STOP候補判定(PREREGISTRATION_01.md 5節)。

## 実行したローカルスクリプト(全てAPI不使用、`py -I`、repo rootから実行)
- `analyze_ledgers_01.py` → `ledger_stats_01.json|md`
- `verify_ledger_provenance_01.py` → `ledger_provenance_check_01.json`(Stage R新規6テーマで台帳notes==Researcher draft notes 52/52、ambiguity_noteの出所確認)
- `build_trace_5themes_01.py` → `trace_5themes.json`(命令文10件=5問題テーマ、正常系0件)
- `preview_armD_01.py` → `armD_preview_summary_01.json`、`armD_preview_01/`(9/9で`parse_brief_md`・`dryrun_annotate`成功、Fact行内命令形パターン0)
- `trace_5themes_01.py` → `trace_candidates_raw_01.json`(命令文候補の自動スキャン。最終の正本は`trace_5themes.json`)
- 備考: 初回実行時に`trace_candidates_raw_01.json`と`ledger_stats_01.*`をrepo rootへ誤出力したため、新規ディレクトリへ移動しスクリプトの出力先を修正した(いずれも本委任で作成したuntrackedファイルのみ、既存ファイルには触れていない)。

## 主要事実
- 混入10件の由来: notes_for_writer 8(逐語3/言い換え4/未選定factのnotes転用推定1)、Verifier由来ambiguity_note 1、B3新規 1。Research/Ledger段階で新規追加された文はなし。
- B3 Prompt(er019 L68)はnotes/ambiguity_noteの扱いを一切指示していない。Writer R0は台帳を読まずbriefのみ読む。R1/R2はbriefを見ない。
- B3導入前はWriterが台帳全文(notes込み)を直接読んでいた。B3導入(2026-09-26)でnotes経路が仕様未定義のまま切断された。混在を規定する仕様は見つからず「バグ/副作用」と判定。ただしFact Lock R0規則4と注記仕様v2は混在を前提にした規則を持つ。
- 第一候補=案D(B3は選ぶだけ、briefは台帳claimから決定論assemble、notesは制約ブロックへ決定論転記)。次点=A'(Prompt変更+制約決定論転記)。両者とも追加LLM call 0。
- 費用見積: 基本約¥18〜22(B3実測平均¥0.50×36 call)、Cap ¥40案。任意E9(R0 10 call)約¥3(推定)。

## Fable判断が必要な点
RESULT_PACKET_B3SEP_01.md 7節参照。Opus条件A(新構造設計)の独立レビューが必要。

## 未実施・限界
Trial未実施。旧凍結4テーマのResearcher draft JSONは現存せず(規則+他6テーマの100%一致からの推定)。命令文判定は手作業。Writer出力品質への影響は未測定。
