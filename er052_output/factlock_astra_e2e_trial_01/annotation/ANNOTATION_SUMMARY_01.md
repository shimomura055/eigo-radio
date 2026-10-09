# ANNOTATION_SUMMARY_01(FACTLOCK-ASTRA-E2E-TRIAL-01 委任_10 更新、2026-10-09)

委任_09版(旧表)は `ANNOTATION_SUMMARY_01_prev09.md` に保存。数値は annotation/check/, out/merged/, final/, audit/ の実測。AMBIG=AMBIGUOUS台帳IDへの紐付けあり(運用明確化(c)でWARN+`ambiguous_fact`フラグ。評価時は別集計)。

## 1 10テーマ表

| テーマ | B3版 | 単独A | 単独B | 統合 | final | inputs配線 | G0実照合 | 事実数 | 中核/周辺 | cap_dropped | ambiguous_fact(統合) | 分割一致率 | 中核Jaccard | 判定線(0.8/0.67) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| byd_recall | v1 | PASS | PASS | PASS | 有 | 済 | PASS | 1 | 3/0 | 0 | - | 1.00 | 1.00 | 超え |
| central_bank_mortgage | v1 | PASS | PASS | PASS | 有 | 済 | PASS | 6 | 5/5 | 4 | - | 0.80 | 1.00 | 超え |
| hormuz | v2 | PASS | PASS | PASS | 有 | 済 | PASS | 4 | 4/4 | 4 | - | 1.00 | 1.00 | 超え |
| inbound_tourism | v1 | FAIL(c_numbers) +AMBIG | FAIL(c_numbers) +AMBIG | 未統合(単独PASSが2本揃わず) | 無 | 無 | - | - | - | - | - | - | - | - |
| meta | v1 | PASS | PASS | PASS | 有 | 済 | PASS | 3 | 0/0 | 0 | - | 1.00 | n/a | 超え(中核0件でJaccard算出不能) |
| openai_copyright | v1 | PASS | PASS | PASS | 有 | 済 | PASS | 1 | 3/0 | 0 | - | 1.00 | 1.00 | 超え |
| semiconductor_earnings | v1 | PASS +AMBIG | PASS +AMBIG | PASS | 有 | 済 | PASS | 1 | 3/4 | 4 | {'1': ['F1']} | 1.00 | 1.00 | 超え |
| small_bag | v1 | PASS | PASS | PASS | 有 | 済 | PASS | 3 | 1/0 | 0 | - | 1.00 | 1.00 | 超え |
| space_weapons | v1 | PASS | PASS | PASS | 有 | 済 | PASS | 5 | 1/0 | 0 | - | 1.00 | 1.00 | 超え |
| streaming_price | v2 | PASS +AMBIG | PASS +AMBIG | PASS | 有 | 済 | PASS | 1 | 4/5 | 3 | {'1': ['F01', 'F07']} | 1.00 | 1.00 | 超え |

- G0実照合は `g0_real_annotation_01/g0_summary.json`(runner `run --g0-only`、実注記)。hormuz・streaming_priceは注記も統合もB3 v2(`stage_r/<slug>/storyline_b3_v2/`)が基準で、inputsには v2 の原B3/原JSON+`input_manifest.json`(凍結sha LF値)を置いた。
- inbound_tourism: 再注記(v1-brief, 台帳ID `F01`形式)の単独検査はA・Bとも c_numbers FAIL。(c)でb_ledger_mappingはPASS(AMBIG)になったが、c_numbers FAILが残る。内訳はA=`8`(Storyline「8月単月」)の分類漏れ+台帳ID括弧`（F01）`内の数字誤検出、B=概念重複2件+`2026`分類漏れ+同ID誤検出。`ID_RE`が連字符なしID(F01)を除外できないため括弧内IDの数字(01,02,03,06)を分類漏れと誤検出(検査script側の欠陥候補。IDマスク修正だけではA・Bとも別の実FAILが残る=スクラッチ実測。要Fable判断)。統合しない。

## 2 (c)(d)(e) 運用明確化の記録(Fable判断、2026-10-09)

- (c) AMBIGUOUS台帳IDの紐付けは許容+`ambiguous_fact`フラグ(WARN)。NOT_VERIFIED/REJECTED等は従来どおりFAIL。事前登録(PREREGISTRATION v2.2 5-12)と整合。正本は `stage_r/SPEC_V2_CLARIFICATIONS.md` (c)。ユーザーが覆した場合は該当3テーマ(inbound_tourism / semiconductor_earnings / streaming_price)を除外。
- (d) 注記者が許可Writeでなく Bash `cat >` で自分の reply.md を書いた件: 他パス接触0・隔離維持のため採用。既存監査scriptのVIOLATIONは許可済みWrite/返却ツールと自プロンプトパスの禁止語該当による誤判定で、補助監査(AUDIT_SUMMARY.md)の結果を正とする。
- (e) 「・」行頭への【事実N】挿入は検査PASS・仕様§2に反しないため許容。
- 仕様sha256はLF正規化後の値を正とし、CRLF生バイト値は併記(runner g0.json の spec_sha256 に raw / lf_normalized を併記)。

## 3 (c)反映による検査結果の変化(単独検査)

| テーマ | 注記者 | 旧(委任_09) | 新(委任_10) | 備考 |
|---|---|---|---|---|
| semiconductor_earnings | A | FAIL(b) | PASS +AMBIG | 同一返答、(c)のみで変化 |
| semiconductor_earnings | B | FAIL(b) | PASS +AMBIG | 同一返答、(c)のみで変化 |
| streaming_price | A | FAIL(b)/STOP | PASS +AMBIG | 再注記(B3 v2)。旧はv1(B=STOP) |
| streaming_price | B | FAIL(b)/STOP | PASS +AMBIG | 再注記(B3 v2)。旧はv1(B=STOP) |
| inbound_tourism | A | FAIL(b,c) | FAIL(c_numbers) +AMBIG | 再注記。b解消、c残 |
| inbound_tourism | B | FAIL(b,c) | FAIL(c_numbers) +AMBIG | 再注記。b解消、c残 |

## 4 Bash使用注記者(委任_09監査 annotation/audit/audit_all.json の v1ラウンド分)

- byd_recall__B, central_bank_mortgage__B, inbound_tourism__B, meta__B, openai_copyright__A, openai_copyright__B, small_bag__A, space_weapons__A, space_weapons__B(計9本)。
- 採用済み統合6テーマで該当: byd(B), central_bank_mortgage(B), meta(B), openai_copyright(A,B), small_bag(A), space_weapons(A,B)。(d)により採用。
- 委任_10時点で再注記済みの hormuz / streaming_price / inbound_tourism のA/B(計6本)は transcript が未保存のため、本版では**未監査**(呼び出し側が transcript.jsonl 保存後に監査する。手順は RUN_ANNOTATION.md 末尾)。ディレクトリ上の transcript.jsonl は旧ラウンド(v1)のもの。
