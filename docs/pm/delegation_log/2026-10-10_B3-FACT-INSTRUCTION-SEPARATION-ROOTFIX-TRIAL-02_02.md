# 委任_02: Phase 2a 是正反映→事前登録確定→B3系有料腕の実行→評価(B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02、2026-10-10)

範囲: Opus是正(A1-A7, U1)の実装・selftest、PREREGISTRATION_02確定(freeze)、D-plus 18 / Separate-call(Luna) 18 / 役割宣言のみ 18 の有料実行、評価、Blind目視、報告。E9(M10)は本委任で実行しない(Lane A C2編集中ファイルを読まないため。Phase 2bで実施)。
禁止の遵守: git操作(add/commit/checkout/stash)なし、Production code・Production Prompt・CURRENT_SPEC・SSOT・ACTIVE_TASK.md・RESULT_PACKET.mdは未編集。書き込みは er052_output/b3_rootfix_trial_02/・本ログ・docs/pm/RESULT_PACKET_B3SEP2_02.md のみ。実行は `.venv\Scripts\python.exe -X utf8`(リポジトリルートをcwdにして実行。cwdが違うとcost logger内のimportが失敗する)。
モデル: 実行層=Sonnet。Trial対象=gpt-6-luna(Sol未使用)。

## 実施
1. 是正実装: `b3r2_rank_01.py`(A1数字境界/NFKC、A2抽出拡張[月のみ・日のみ・四半期・時刻・合成数・ISO・日付範囲・票数・事件番号・名称内番号・通貨前置]、A3代替規則=台帳全体に欄が無い場合のみFact本文で比較+概念束ね[同表記/同Fact主数字・単位/包含]、Storyline表記の取り込み)、`b3r2_sepcall_01.py`(STEP6_RULES単一ソース化)、`b3r2_make_dplus_01.py`(dplus/roleonly生成、U1削除、attempts_log添付)、`b3r2_driver_01.py`(有料b3-dplus/b3-roleonly/sep・frozen・sha assert・cap guard)、`b3r2_eval_01.py`。DESIGN_REVIEW §3を訂正。selftest ALL_PASS(34項目)。
2. PREREGISTRATION_02.md確定→`frozen_b3r2_02.json`(prereg・module・入力のsha)。有料run毎に照合。
3. 有料実行: 各腕のhormuz rep1を3並列で先行→実測再見積(D-plus 0.70/call→12.5、Sep 0.29→5.1、役割宣言のみ 0.42→7.6、いずれも高位の2倍未満)→残りを7プロセス並列。実費JPY31.68(cap 60内)。
4. 評価: `b3r2_eval_01.py`→`eval/`。Blind目視を対応表を開く前に実施。M11は既存`b3_annotation_check_01.py`を無改変で適用。
5. 報告: `er052_output/b3_rootfix_trial_02/RESULT_2A_01.md`、`HUMAN_CHECK_B3R2_01.md`、`docs/pm/RESULT_PACKET_B3SEP2_02.md`。

## 事前登録からの逸脱・開示
- D-det抽出規則はfreeze前にC0 9テーマの既存注記検査判定と見比べて複数回修正(GT比較値は既知値)。
- freeze後に評価scriptを1箇所修正(STOP行の`latency_seconds`欠落でKeyError。指標定義は不変)。
- STOP runの応答本文は保存していない。再実行・Prompt修正・検証器変更なし。
- `cl.install`が`er003_b1_p3u_audio`系を内部import(read-only)。委任文が禁じる4ファイルは読んでいない。作業中、git statusに他agent(Lane A C2)の変更(er019 audio/entertainment production runner等)が見えたが、中身は読んでいない。

## 判定
D-det=VALIDATED_PENDING_M10 / D-plus=REJECTED(機械分類、M7 STOP・M9) / Sep(Luna)=REJECTED・Sol未実施 / 役割宣言のみ=VALIDATED(no-harm)。いずれもTrial限定、APPROVED_FOR_PRODUCTIONではない。

## 新仕様候補(未実装・報告のみ)
(a) 検証器の`DUPLICATE`を同roleなら黙って畳む (b) Storyline表記の紐付けを`numeric_value`経由にする(central_bankの25bp周辺落ち) (c) number_ranksのsurface範囲を組立済みFact行にする (d) 既存注記検査の`annotator`許容値。

## 未解決
U2/U3の内容(委任文に記載なし)。Phase 2b(E9)のrunner方針。
