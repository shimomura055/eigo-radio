# RESULT_PACKET_N5Q_01 (KP-N5-PHRASE-COVERAGE-AUDIT-01 委任_01、2026-10-31、OPEN-631)

要約: 調査のみ・Production変更0・API ¥7.44(個別Cap ¥15)。判定=現行方式「改善候補あり」(N5本体の一般化・意味判定は変更不要)。詳細=`docs/research/KP-N5-PHRASE-COVERAGE-AUDIT-01/AUDIT_01.md`(表§2・分類§5・判定§6・判断候補§8)、証跡=同`ev01/`。

5表現(公開済みAdvanced=旧方式[N5配線前]の選定UI候補には全て無し。N5現行はM10 untidi_b1b、同一本文sha一致):
- put away ★: 抽出✕(P7 0/5・B1 0/4)。N5に入れるとC・easy・keep(L3 SAME)だが難易度/順位/上限7で落ちやすい。
- in the way ★: 旧✕。N5現行M10で補完P7経由により最終候補12件に到達(再現性低、通常P7 0/5・B1 0/4)。
- force away: 抽出✕。N5 SELがF(3/3)=妥当な除外。
- leave out: 単体は抽出✕。拾われた`working things left out`はSELでF。単体を入れればC・keep。
- in sight: 抽出はB1 1/4のみ。入ればC・keep(L3 SAME)。

(1) 既存仕様整合: ユーザー原文`docs/pm/delegation_log/2026-10-31_LEARNING-ITEM-QUALITY-TRIO-01_USER.md:70-127`(:115・:117)、`er138_kp_n5_generalization_01.py:47,308-310,354,950,1307`、`er105_kp_fulltext_selector_01.py:61`(条件5)、`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02_USER.md:69`、`er125_kp_rescue_production_01.py:42,526-527`、`er119_kp_human_review_01.py:540`と照合。
(2) 未承認機能の既定値: 本委任でProductionに入る未承認機能は0(コード・Prompt無変更、変更は`docs/`配下のみ。`git diff origin/main --stat`で確認)。診断用の「条件5除去」変種は`ev01/run_diag_no_easy_exclusion.py`内のメモリ上置換のみで、Production経路から呼ばれない。
(3) 失敗終了時の最終成果物: 失敗終了なし(完了)。最終成果物=`docs/research/KP-N5-PHRASE-COVERAGE-AUDIT-01/AUDIT_01.md`と`ev01/`。目的(N5を含む現行方式が5表現・他表現を適切に評価しているかの把握、原文§3)に適合(5表現の追跡表・4区分分類・判定・判断候補を提示。5表現を必ず選定させる実装は行っていない)。
(4) 撤去・残置した規則: 撤去0・残置0(新規規則・検査・testなし)。Grep: `git status --short`のコード変更0件。

判定整合: 重大NG=なし

原因仮説ブロック(QDC材料): 仮説=抽出段の条件5が主因 → 反証/再現=条件5除去診断で in the way(P7 2/3・B1 3/3)・in sight(B1 2/3)は抽出、put away・leave out・force awayは0/6のまま(条件5だけでは不十分=第2要因は未特定)。仮説2=N5が落としている → 反証=強制投入でSEL C・L3 SAMEが4/5、force awayのみF。仮説3=pick上限の位置依存 → 再現=強制投入r1でkeep13中6件が難易度ラベル+入力順で落ちた(M10実プールは7件で未発動)。gets heated=救済QA再判定のkey不一致(旧記録・M10・公式関数replayの3/3)。次の一手の候補(改善見込みの自己評価): J3(救済QA再判定の不具合修正、見込み高・低リスク・Gate変更のためFable判断→Opus条件A相当レビュー後)、J1/J2(要Offline Trial→ユーザー判断、中)。

費用: ¥7.44(`ev01/cost_summary.json`)。M10既存記録(¥7.85)は再利用のみで含まない。
判断候補: J1(抽出条件5とSEL方針の整合、分類D)・J2(pick選定基準、分類D)・J3(救済QA再判定の不具合、不具合=修正へ進む、Gate変更でFable判断)・J4(Comment 4 JA訳→OPEN-630追加案)。環境注意: C:ドライブ空き約0.8GB(フルworktreeがENOSPC、sparse checkoutで実施)。
