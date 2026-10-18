# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_13(Stage 1b 3記事の人手品質評価(ブラインド)+5記事最終集計+案1/案2/案1+2の分類草案+最終報告書草案(ユーザー§10の順1〜7)。**JPY0・有料API呼出0**)。日付: 2026-10-18(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 評価・集計・文書作成(read-only+文書/SSOT追記)。Production・Prompt・harness・Trial成果dirの変更0。
- 到達上限Status: `TRIAL_EVALUATED_CLASSIFICATION_DRAFT_PENDING_OPUS_C_AND_FABLE`。分類の最終決定はFable(Opus条件Cレビュー後)、Production採用判断はユーザーのみ。VALIDATED≠Production採用。
- 禁止: 有料実行/Trial再実行/任意A streaming_price(Fable決定: 打切り。任意A上限54の引上げはユーザー予算変更に当たるため行わない。Coffee3件+inbound3件=6件で検出漏れ0を根拠とし、streaming未実施と件数の限界を報告に明記)/品質条件の緩和/Production実装・配線/Prompt改変の提案をProduction変更として実施すること(提案は文書に留める)。
- 固定ブロック: **E-1**(評価手順=STAGE_1A_EVAL_01 §1〜§6の手順+TRIAL_DESIGN_03 §8の是正(ラベルのマスク/R-07全方式同一基準/M2c↔M3c差はB3揺らぎ/unmet内訳/新設計列R-B7)に厳密に従う)/**D-1**(不適用)/**G-1**(変更ファイルのみ明示add、禁止操作同前、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。commit同時1件: 他のcommit作業なしをstagedで確認)/**F-1**(費用数値は既存の実測集計(`aggregate_1b_all.*`・`_analysis_1b_a*.json`・STAGE_1A_RESULTS/CORRECTION・OPTIONAL_A_RESULTS)のみ引用。新しい推定値を作らない)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_13.md`へ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT13.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記)。
- 使用モデル: 評価はSonnet自身の人手相当判定(LLM API呼出なし)。使用モデル名(自分)を報告に記載。

## Fable決定(記録用)
- 任意A: Coffee 3件+inbound 3件(計6件×{上限なし,上限付き})で検出漏れ0、費用32.226/54。streaming_priceは残枠21.774に対しinbound実績21.344で超過リスクがあるため**打切り**(枠引上げはしない)。限界(n=6、inbound F05は弱い注入でAMBIGUOUS)を明記。
- 評価者は単一(Sonnet)、n=1/記事であることを全ての判定に付記。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\STAGE_1A_EVAL_01.md`(手順の正本。§1判定手順と限界/§2構成差3段階/§3品質一対比較/§4 R-07/§5 Verifier再現性/§6受入条件暫定判定/追補)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\TRIAL_DESIGN_03.md` §8(L66-76)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\STAGE_1B_RESULTS_01.md`(全文)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\STAGE_1A_CORRECTION_01.md`・`STAGE_1A_RESULTS_01.md`(§5〜§10)・`OPTIONAL_A_RESULTS_01.md`
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_DESIGN-FIX-1B_USER.md` §7〜§10(L110-197)、および元指示(`…_委任_01.md`または`…_USER.md`の初回版)の受入条件§7(Grep `受入条件`)
- 1b成果: `er082_output/rlct_trial_01/{streaming_price,openai_copyright,central_bank_mortgage}/<方式>/result.json`(selected_storyline/brief/verdicts)。**ブラインド**: 記事ごとにM0を基準開示、M0b/M0p/M1/M2/M3は伏せラベル(乱数順)で読み、判定記録後に`blind_key`を開示(1aと同じ)。ラベル「【独立検証前の編集仮説】」は読む前にマスク。
- `C:\Users\tensh\eigo-radio\docs\pm\OPUS_FINDINGS_LEDGER.md`(OF-RLCT-RB-01〜09の行。評価が各Findingにどう応えたかを「EVIDENCED/OPEN」で更新)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `OPEN-403|OPEN-409|OPEN-410|OPEN-411`→評価結果の要旨を各1行(新規起票しない)。
- `DECISION_LOG.md`: 末尾に委任_13エントリ(評価完了・分類草案=Fable判定待ち)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: OF-RLCT-RB-*行のStatus更新。
- 新規: `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/STAGE_1B_EVAL_01.md`(1a EVALと同じ章立て)、`TRIAL_FINAL_REPORT_DRAFT_01.md`(下記構成)。

## 作業(順序)
A. T-0。B. 1b 3記事のブラインド評価(1a手順): 構成差3段階/品質一対比較(一貫性・事実整合・面白さ)/R-07 中心FactのAMBIGUOUS断定(全方式同一基準、留保表現の有無、人手)/REJECTED Fact混入/ラベル件数(方式別、記録のみ)/Verifier再現性の事実整理(F07等の既知欠陥、方式間遷移)/既知誤判定(Coffee F12、inbound F12)の原因・影響・最終採用有無の記録。`STAGE_1B_EVAL_01.md`に記録(ブラインド鍵・判定前推測の一致率も)。
C. 5記事最終集計(新設計列R-B7): 5記事×{M0,M0b,M1,M2,M3}(M0pは参考列)の費用表(検索ツール呼出・クエリ数・LLM費用・Web検索手数料を別列、再選定/確認パス費用を分離、本番換算の対M0削減額・率)、記事別符号、合計。案1の検索上限3回の有効性=ソフト上限到達件数・検索回数差・verdict遷移で記述し「検索削減=上限の効果」と断定しない。実質削減額=確認パス・再選定費用込み。
D. 受入条件(元指示§7)の5記事判定表(充足/条件付/不充足、根拠path)。
E. 分類草案: 案1(M1)/案2(M2)/案1+2(M3)を REJECTED / VALIDATED / USER_DECISION_REQUIRED に分類する**草案と根拠**(費用効果の大きさ・符号の分散・品質条件・既知欠陥・n=5の限界)。Fableが最終決定するため「草案」と明記。
F. `TRIAL_FINAL_REPORT_DRAFT_01.md`: ユーザー§10の順=1.5記事×4方式のコスト削減比較表/2.B3品質への影響/3.AMBIGUOUS・REJECTEDの扱いが適切になったか/4.案1の検索上限3回の実際の有効性/5.再選定・確認パスを含む実質削減額/6.各案のTrial Status(草案)/7.ユーザーに必要な採否判断。末尾に「限界と注記」(n=5・単一評価者・Verifierばらつき・任意A縮小・1a/1bの符号差・1bと並行MEYのreview_queue誤検知)と「費用総括」(1a 212.80+補正20.009+1b 212.123+任意A 32.226=Trial累計477.158/1,040、区分別上限との対比)。
G. SSOT→commit→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_13.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_13.md_check.json`
- ブラインド鍵生成(1aで使ったscriptがあれば再利用。例): `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er082_rlct_blind_key_01.py --root C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01 --articles streaming_price,openai_copyright,central_bank_mortgage --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\_blind_key_1b_13.json`(無ければ同等の新規scriptを`docs/research/.../`配下に作成。LLM呼出なし)
- 5記事集計: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er082_rlct_trial_01_aggregate.py --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\aggregate_final_5_13.md`(委任_09〜11と同じ一時root方式で5記事をコピー。新設計列=Coffee M2/M3+inbound M2c/M3c+1b M2/M3、旧inbound M2/M3は参考行。aggregateが列分けに対応しない場合は`_final_5_13.json`を別scriptで作成し、数値は既存json由来のみ)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`(実在script名に置換)

## SSOT追記文(要点)
- OPEN-403/410: 「1b評価完了・5記事集計・分類草案(…)。Fable最終判定・Opus条件Cレビュー待ち。VALIDATEDはProduction採用を意味しない」。
- DECISION_LOG: 同旨+任意A打切り(Fable決定)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 委任_13+_check.json、STAGE_1B_EVAL_01.md、TRIAL_FINAL_REPORT_DRAFT_01.md、`aggregate_final_5_13.*`/`_final_5_13.json`/`_blind_key_1b_13.json`、OPEN_ITEMS.md、DECISION_LOG.md、REPORT_LEDGER.md、OPUS_FINDINGS_LEDGER.md。msg: `FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_13: Stage 1b人手ブラインド評価+5記事最終集計(新設計列)+案1/案2/案1+2分類草案+最終報告書草案(JPY0、任意A打切り記録、Fable判定・Opus条件C待ち)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT13.md`)
4行: (1)整合(評価手順=1a EVAL・§8是正の適用箇所)(2)Production到達経路=なし(3)成果物とcommit sha、5記事比較表の要約(方式別合計費用・対M0削減額/率・符号)、R-07結果(方式別件数)、REJECTED混入、ラベル件数、受入条件表の要約、分類草案と根拠(各案1〜3行)(4)撤去/残置。`判定整合:`・`判断候補:`(Fable判定に必要な論点のみ)・T-0 check・自己チェック(有料0/成果dir不変/ブラインド遵守)。
