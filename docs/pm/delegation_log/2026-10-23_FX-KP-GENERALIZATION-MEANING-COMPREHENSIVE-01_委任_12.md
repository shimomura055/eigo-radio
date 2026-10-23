FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_12-POSSESSIVE-PLACEHOLDER-RECLASSIFY-AND-HEADWORD-ORIGIN-20261023

# 記録+read-only確認(API 0・コード変更0)。ユーザー指摘を受け、監査の「所有者誤りNG」3件の分類をFableが訂正する。あわせて見出し語の人称placeholderの出所を確認。

## 1. ユーザー指摘(2026-10-23、逐語で `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_05.md` に保存)
1. 所有者誤り： reach for someone's wallet →「他人の財布に手を伸ばす」（本文では自分の財布を出して支払う）
2. 所有者誤り： apply one's findings →「人の研究結果を当てはめる」（本来は自分の研究結果）

この２つよくわかりませんが。

reach for someone's wallet

なら他人の財布に手を伸ばす、でいいんじゃない。

比喩的な意味なのか、直接的な意味なのかはわかりませんが、後者なら問題ないと思いますが。

本文で云々は関係ないでしょ？

apply one's findings →「人の研究結果を当てはめる」も同様、何がいいたいの？

## 2. Fable訂正(逐語で `AUDIT_01/FABLE_VERIFICATION_02.md` に保存)
- 判定の訂正: 見出し語(Key Phraseの正規形)に対する日本語意味としては、「reach for someone's wallet→人の/誰かの財布に手を伸ばす」は**正しい訳**(辞書慣習: someone's=他者、one's=主語自身)。「apply one's findings→人の研究結果を当てはめる」は慣習上は「自分の」が標準だが、本文(We can't apply **its** findings=研究の結果)では「研究/他者の結果」が実態であり、どちらも許容範囲。よって、Std生成の誤り(所有者誤りNG)と分類した3出力(Trial_03: G0 reach「人の財布」、G3 reach「誰かの財布」、G3 apply「人の研究結果」)は**NGから外し、「見出し語の人称placeholder不整合(生成器の誤りではない)」として別掲**する。Std確定NG(第3回、各120出力)は **G0=2(字義訳: an unseen clock×2)、G2=1(字義訳: draw a line「はっきりと線を引く」)、G3=0**。
- Adv「59/60」の唯一のNG(reach rep1 "to move your hand toward another person's wallet to take or use it")も、見出し語 "someone's" に忠実な出力であり、Std/Advは互いに整合している。問題は見出し語が本文の指示対象(your wallet=自分の財布)と一致していないこと。したがって「Std誤り→Adv波及 1/5」は「見出し語不整合→Std/Advが揃って見出し語に従った1件」に訂正し、Std意味生成の誤りに起因するAdv NGは**0件**とする。
- 本文との関係の整理: Std意味で本文が関係するのは「字義/比喩のどちらの語義か」の選択だけ。所有者(自分/他人)は見出し語自身が決めるべきもので、見出し語の正規化(canonicalization)が "your wallet"→"someone's wallet" と置いた場合、意味は見出し語どおり「他人の財布」になる。本文の意味(自分の財布)を伝えたいなら見出し語を "reach for one's wallet" にするのが正しい(記事Bの実際のKPは `reach for one's wallet` であることを確認済み: 委任_08報告)。
- 残る実質的な問題は2種類: (a)比喩表現の字義訳(an unseen clock、draw a line「線を引く」)、(b)見出し語の人称placeholder(one's/someone's/the)が本文の指示対象と一致していないケース(Trial KP集合内で確認)。

## 3. read-only確認(推測で埋めない)
- Trial_02/03のKP集合定義(`er112_kp_gm_kpset_02.py` 等、`er112_output/kp_gm_trial_0*/` のKP定義)で、`reach for someone's wallet`・`apply one's findings` の見出し語がどこから来たか(Trial_01の選定出力/既存記事のKP/手作成)と、本文の指示対象(your wallet、its findings)を記録。
- Production側のcanonicalization(A-1 規則5: him/her/me/us→someone、this/that→a/an。`er105_kp_fulltext_selector_01.py`、`WIRING_DESIGN_01.md`)で、所有格 my/your/his/her/its/their がどう正規化される規定か(one's/someone's/the のいずれか、本文の指示対象[主語自身か他者か]を考慮するか)をfile:lineで確認。規定が無い/曖昧なら「不明/規定なし」と記す。記事Bの実KP `reach for one's wallet` がどの規則で one's になったかも確認。
- 結果を `AUDIT_01/HEADWORD_PLACEHOLDER_01.md` に。改善提案は書かない(事実のみ)。

## 4. 更新・Git
- `AUDIT_01/AUDIT_SUMMARY_01.md`・`STD_AUDIT_01.md`・`ADV_AUDIT_01.md` 末尾に「Fable訂正(2026-10-23、ユーザー指摘反映)」節を追加(元表は残す)。OPEN-474に1行。DECISION_LOGに1行。
- 委任文逐語保存 `..._委任_12.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py ...`、MARKER一致)。
- secret scan 0件→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。
## 5. 禁止
コード変更0。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。他agentの行を編集しない。完了したらcommit hash・HEADWORD_PLACEHOLDER_01の要点(出所・規定の有無)のみ報告。