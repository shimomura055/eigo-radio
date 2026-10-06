## 管理ID
OPEN-233-LEDGER-CLARITY-P-TRIAL-01(委任_01b: 評価表の修正(M-e)とFact安全性検査ツール(M-d)・JA逐語率ツールの実装、Phase 1準備、¥0)

## 性質/到達上限Status/禁止事項
性質: DEVツール実装(新規/既存DEVツールの更新のみ)。到達上限: 実装・自己テスト報告。禁止: 既存Production file変更/有料API/SSOT編集/git/Trial実行。並行委任_01aが書く `er052_open233_ledger_clarity_pprime_dev_01.py`、`er052_output/open233_ledger_clarity_p_trial_01/tests/*`、`docs/pm/ledger_clarity_p_trial/01a_run_procedure.md`、`docs/pm/ACTIVE_TASK.md` には触らない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1: 該当なし(¥0)。T-0: 本委任文を `docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_01b.md` に**逐語**保存(要約禁止、見出し名不変)し `python docs/pm/tools/check_delegation_prompt.py --file <パス> --json-out <同名_check.json>`。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
「④Factそのものの安全性: 新しいFactの追加/原資料にない主体・因果・時系列/否定・肯定の反転/数字・日付・固有名の変化/原資料より強い断定を作っていないこと(必須条件)」「②記事のエンターテイメント性: 説明的すぎ・台帳逐語コピー・ストーリー性・テンポ・硬さの比較」。Opus条件A判定(B)の必須修正M-d・M-eを本委任で反映。

## 事前指定Read一覧
- `docs/pm/ledger_clarity_p_trial/00d_eval_template.md`(49行、修正対象)
- `docs/pm/ledger_clarity_p_trial/00c_before_evidence.md`(50行。Before 5 runのHC-012型分布、Entertainment基準値、JA逐語率0.1518の定義)
- `er052_output/open233_ledger_clarity_p_trial_01/tools/ledger_diff_p01.py`(160行、regex流用元)
- `er019_output/meta/run_03/ledger/verified_fact_ledger.txt` と同dir `research_ledger/fact_ledger_draft.json`・verification JSON(Before、フィールド構造確認)

## 事前指定Grep一覧+追記位置・更新位置の手順
1. **M-e 評価表修正** `00d_eval_template.md`: 「/8 seed」等のn>1前提をn=1(After 1 chain)に直す。Beforeは「同topic meta 5 run(e2e_02)のHC-012型分布: 復元型3/5、うち重大ラベルY 1件」を参照値として明記。①HC-012型の行に「After台帳にHC-012相当fact(人間コンシェルジュ機能の取り下げ/停止に関する記述)が無い場合=INCONCLUSIVE(評価不能、成功扱いにしない)」を追記。④の判定基準を「Before/After集合差0」から「After各fact内部の整合+原資料接地+改行0+否定語・因果語の増加なし+変更factの原資料照合全件」に書き換え。②の逐語コピー率は「JA側(ja_writer/original.md または R2 vs 台帳txt、12文字連続一致率、Before=0.1518)」を主指標にし、EN 8語指標は参考に格下げ。副作用観測項目に「claim長文化により数字・日付がfactに増え、precheck(number_only)/再分類で『台帳一致』になりやすくなる→候補数・重大数の変化」を追加。「本TrialのChecker結果をS1・precheck4種除外等の承認根拠に流用しない」を注記。
2. **M-d Fact安全性ツール** `er052_output/open233_ledger_clarity_p_trial_01/tools/fact_safety_p01.py`(新規): 入力=After台帳txt+After draft JSON+After verification JSON、Before台帳txt(類似候補用)。出力JSON+MD: (a)各factの claim/notes_for_writer/conditions 中の数値・日付・固有名が、同factの numeric_value/date_or_period/subject またはVerificationの引用source文字列(フィールド名はverification JSONを確認)に含まれるか(未接地トークン一覧) (b)否定語・因果語の件数を、Beforeの類似fact(トークンJaccard上位1件)と比較し増加分を表示 (c)全フィールドの改行(`\n`)件数 (d)claim文字数・平均・Before平均との比 (e)M4: claim行の括弧・番号・否定語・因果語がBefore類似factに無いもの (f)notes_for_writer値内の「順序:」「語義:」書き出しの有無(任意規則の遵守確認) (g)txt書式: 非ASCIIキー行・ブロック内空行(precheck `TAG_LINE`相当のregexを複製) 。**合否判定はしない**(材料のみ)。regexは `ledger_diff_p01.py` から流用。
3. **JA逐語率ツール** `er052_output/open233_ledger_clarity_p_trial_01/tools/ja_copy_rate_p01.py`(新規): 入力=JA原稿md+台帳txt、12文字連続一致率(00cと同定義。scratchpadの`ent_metrics_before.py`があれば定義を合わせる)。Before値(original.md=0.1518)を再現できることを確認。
4. **Before基準値(Opus任意)**: Before台帳の改行件数・claim平均文字数・notes_for_writer平均文字数を `fact_safety_p01.py` をBefore自身に適用して測り、結果を `er052_output/open233_ledger_clarity_p_trial_01/phase0/before_ledger_stats.json` に保存。
5. 自己テスト: fact_safety をBefore台帳(After=Before指定)で走らせ落ちないこと、ja_copy_rate がBefore値を再現すること。

## 実行コマンド全文
- `python er052_output/open233_ledger_clarity_p_trial_01/tools/fact_safety_p01.py --after-txt er019_output/meta/run_03/ledger/verified_fact_ledger.txt --after-draft <draft json> --after-verif <verification json> --before-txt er019_output/meta/run_03/ledger/verified_fact_ledger.txt --out er052_output/open233_ledger_clarity_p_trial_01/phase0/before_ledger_stats`
- `python er052_output/open233_ledger_clarity_p_trial_01/tools/ja_copy_rate_p01.py --ja er019_output/meta/run_03/ja_writer/original.md --ledger er019_output/meta/run_03/ledger/verified_fact_ledger.txt`
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_01b.md --json-out docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_01b_check.json`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目、10行以内)
(1)修正・作成ファイルのパス・行数 (2)Before基準値(改行件数・claim平均文字数・notes平均文字数・JA逐語率再現値) (3)verification JSONの引用sourceフィールド名(あれば) (4)自己テスト結果 (5)T-0結果
