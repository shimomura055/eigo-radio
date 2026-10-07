# 2026-10-07 OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 委任_03(集計・事前登録判定・人間確認パック、¥0)

管理ID: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01(委任_03)

(以下、Fableから受領した委任文の保存。TTS・有料API実行なし。)

## 並行タスク
なし(評価者A/B/C+rollback_Xは完了)。直前commit 35abe7fc。API禁止。SSOT編集なし。評価JSONの書き換え禁止。

## 事前指定Read
- `docs/pm/control_checker_polysemy_trial_01/preregistration_01.md`(合否規則、人間確認対象の定義)、`plan_01.md` §2(要判断事項: themeの渡し方(a)、rep10 Note位置(d))
- `er052_output/open233_control_checker_polysemy_trial_01/eval/_private/MAP_ccp.json`(本委任で開封。全員分出揃い+Fable指示。開封時刻を記録)、`eval/articles/*.json`(18)、`eval/rollback_x/*.json`(10)、`runs/RUN_CHECK.md`、`runs/cost_summary.json`、`runs/note_reach_verbatim.json`、`provenance.json`
- `docs/pm/b3_trial_01/aggregate_b3.py`(関数流用可)、`er052_output/open233_b3_trial_01/eval/SUMMARY_STAGE2.md`(V0基準: 重大0/12、軽微0.58/記事)、`er052_output/open233_ng_root_cause_01/eval/SUMMARY_RCA.md`(E2E_02従来版: 重大0/5、軽微1.40/記事(全工程)・0.60(最終))
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §91/§92(過去Rollback 12本の正/曖/誤内訳)
- `docs/pm/control_checker_polysemy_trial_01/human_review_pack_template.md`

## 作業
1. 集計 `eval/aggregate_ccp.json` + `eval/SUMMARY_CCP.md`: 事前登録①〜⑦を数値で(①Rollback JA R2/EN前/EN最終、X判定と記事評価者判定を併記・不一致列挙、累積(過去12+今回10)の正/曖/誤と95%上限 ②重大あり記事数 ③Gate STOP 2/18 ④不要Rewrite率(before_was_ng=false/unclear割合) ⑤Rewrite由来の新規重大/軽微 ⑥原価 ⑦JAのみ残存NG件数)。軽微NGは「HC-012 Rollback曖昧」を分離して含む/除くを両方、V0 0.58/E2E_02従来0.60〜1.40と対比。テーマ別(meta/hormuz/space_weapons/sewer/ai_control)、ai_control jb9k要約、評価者別。事前登録の総合判定(PASS/CONDITIONAL/FAIL/INCOMPLETE)を機械的に適用し、人間確認前の暫定と明記。
2. 人間確認パック `eval/HUMAN_REVIEW_PACK.md`(テンプレ準拠、15〜20分で判定可): (a) Rollback10件(JA R2/EN最終該当文、台帳HC-012原文、固定Note本文、X判定とA/B/C判定、質問 正/曖/誤)。(b) 重大寄り境界(評価Cai_control「AIが外へ流れ出した事実も報告されていません」、評価Bのs9dk認証情報流出元、他notesの『重大』『境界』)、質問 重大/軽微/問題なし。(c) Rewrite由来の変更(gj99、4mjq、kfuf限定文削除ほか)の前後文、質問 改善/中立/悪化。(d) rep10のNote位置不良の影響。各ブロックに記入欄。
3. plan §2(a)(themeを内容で渡した件)の影響評価: TRIAL-04 Control/E2E_02がパス文字列を渡していたなら、当時のWriterはテーマ文をどう受けたか(topic.txtを読んだのか文字列のまま使ったのか)をwrapper/runnerコードで確認し、比較への影響を事実で1〜2行。
4. `docs/pm/ACTIVE_TASK.md` 固定ヘッダ(EVALUATED・人間確認待ち)+末尾1行、`docs/pm/RESULT_PACKET.md` 上書き(12行以内)。
5. T-0: 本委任文を `docs/pm/delegation_log/2026-10-07_OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01_03.md` へ保存+check.json。評価者A/B/C/Xの委任文(要旨再構成)も `_eval_A.md` 等で保存。
6. Git: 個別add(`eval/articles`、`eval/rollback_x`、`eval/aggregate_ccp.json`、`eval/SUMMARY_CCP.md`、`eval/HUMAN_REVIEW_PACK.md`、delegation_log本件。`_private/`除外)。commit「OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 委任_03: 盲検評価集計(18記事: 重大0・Rollback誤0/10[累積0/22])、事前登録判定(暫定X)、人間確認パック、¥0」+ trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`。push origin main。

## 報告
20行以内: ①〜⑦の数値、Rollback累積と95%上限、軽微(Rollback曖昧除く/含む)とV0・E2E_02従来との対比、テーマ別要点、評価者効果、暫定総合判定と根拠、人間確認パックの件数(a〜d)と所在、theme渡し方の影響、commit hash・push結果、check結果、raw URL(SUMMARY_CCP.md、HUMAN_REVIEW_PACK.md)。

## 実行コマンド全文(実施記録)
- `PYTHONUTF8=1 python docs/pm/control_checker_polysemy_trial_01/tools/aggregate_eval_ccp.py`(--引数なし、絶対パスでなくrepo相対、集計)
- `PYTHONUTF8=1 python docs/pm/control_checker_polysemy_trial_01/tools/build_summary_ccp.py`
- `PYTHONUTF8=1 python docs/pm/control_checker_polysemy_trial_01/tools/build_pack_ccp.py`
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-07_OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01_03.md --json-out docs/pm/delegation_log/2026-10-07_OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01_03_check.json`

## SSOT追記文
なし(SSOT編集は本委任の範囲外)。
