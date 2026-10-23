FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_11-FABLE-AUDIT-VERIFICATION-RECORD-20261023

# 記録のみ(API 0・コード変更0)。KP Trial監査(委任_10)に対するFable独立確認の結果を保存し、分類の確定を反映。あわせてUDR #162の不要化整理。Git。

## 0. 読むもの
`docs/pm/ACTIVE_TASK.md`(line 2、KP行)、`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/AUDIT_01/{AUDIT_SUMMARY_01,ADV_AUDIT_01,STD_AUDIT_01,CONSISTENCY_01}.md`、`TRIAL_03/FABLE_BLIND_RESULT_03.md`、`docs/pm/USER_DECISION_REGISTER_01.md`(#162、#157、#164、#171)。

## 1. Fable独立確認(2026-10-23、逐語で `AUDIT_01/FABLE_VERIFICATION_01.md` に保存)
- 生データ照合(Grep): Trial_02 results.jsonl 行10/167/174/181=`reach for someone's wallet` G0 gloss「人の財布に手を伸ばす」、行174のAdv出力に "another person's wallet" を確認(59/60の唯一のNG=Std誤り起因、同入力のrep2/rep3はPASS)。Trial_03 results.jsonl 行60/177/194=`an unseen clock` G0「目に見えない時計」、行412=同gloss入力のAdv "a hidden sense of time that affects when something happens or changes"(字義「時計」を引き継がず、G2/G3入力の "hidden process…"(行416/418)よりやや曖昧だが合格圏)。監査の主要数値(A 1/5、B 0/1、draw a line 字義 G0 2/5・G2 1/5・G3 0/5、Std FAIL 3/1/2)と一致。
- Fableによる分類の確定(監査で推定扱いだった箇所): (1)`reach for someone's wallet` の「人の財布」(G0)・「誰かの財布」(G3)は**いずれも文法・意味関係NG(所有者誤り: someone's=本文では自分の)**に統一(字義訳ではない。財布に手を伸ばす動作自体は本文の用法に合う)。よってStd確定表: G0=字義訳2(`an unseen clock`×2)+文法・意味関係1(reach)=3 / G2=字義訳1(`draw a line`「はっきりと線を引く」)=1 / G3=文法・意味関係2(`apply one's findings`「人の研究結果」、reach「誰かの財布」)=2。語義誤認・その他・原因不明=各0。(2)`settle at`「～で落ち着く」(G0 rep2)は**△(用語性欠落、NGではない)**に確定(日本語の相場表現としても通用するため)。よって△: G0=1、G2=3、G3=4。(3)FABLE_BLIND_RESULT_03の「G0=3 KP」は境界を含む表記で、確定FAIL出力3件は2 KP(reach 1、unseen clock 2)に訂正。
- 過去報告との差: Fableのユーザー向け報告で用いた「G0 誤り3(+境界1)」は確定で「誤り3、△1」。「0/120伝染」は分母の誤り(正=誤りgloss入力1件中0件、薄い入力2件中0件)。Std誤り→Adv波及は難例で1/5(約2割)、通常で0/1。「59/60」はOpus確定gold基準、Sonnet暫定は45/60(14件差、主にcore基準の偽陽性)。
- 未判明として残すもの(推測で埋めない): Opus個別判定ログ無し(集計のみ)/Std G3「25〜26/26」の未特定1件/E0@G2・G3「22」の母集団の厳密な同定/Trial_03 G3 draw a line rep2は欠損補修の再実行出力/DEV E0は1KP/callでProduction(5KP/call)とバイト同一ではない(PROMPT_SHA256未記録)/「伝染0」は実行層目視のみ(独立Judge・gold・rep2なし)。

## 2. 更新
- `AUDIT_01/STD_AUDIT_01.md` と `AUDIT_SUMMARY_01.md` の該当表に「Fable確定(2026-10-23)」列または注記を追加(元の推定表記は残す)。
- OPEN-474: 監査完了・Fable確認済み・UDR #171保留中、の1行。
- UDR #162(旧『開いた窓』決定論的パッチ案の保留): 「不要化(2026-10-23 PM整理: 修正版B[UDR #164]で再制作しユーザーPASS[UDR #157]により代替。再質問不要)」に更新。DECISION_LOGに1行。
- ACTIVE_TASK KP行: `TRIAL_AUDIT_DONE_FABLE_VERIFIED(UDR #171保留)`。
- 委任文逐語保存 `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_11.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py ...`、MARKER一致確認。toolが見つからない場合は `Glob docs/pm/tools/*` で探し、無ければ手で全文逐語保存)。
- Git: secret scan(0件)→`git diff --cached --name-status`(他agentのstaged変更を巻き込まない)→`git commit --only -- <path…>`→`git push origin HEAD:main`。
## 3. 禁止
コード変更0。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。他agentの行を編集しない。完了したらcommit hash・pathのみ報告。