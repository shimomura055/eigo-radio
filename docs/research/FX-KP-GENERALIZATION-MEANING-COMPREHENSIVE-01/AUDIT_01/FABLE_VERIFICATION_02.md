# FABLE_VERIFICATION_02: 所有者誤りNG3件の分類訂正(ユーザー指摘2026-10-23反映、委任_12 §2の逐語保存)

- 判定の訂正: 見出し語(Key Phraseの正規形)に対する日本語意味としては、「reach for someone's wallet→人の/誰かの財布に手を伸ばす」は**正しい訳**(辞書慣習: someone's=他者、one's=主語自身)。「apply one's findings→人の研究結果を当てはめる」は慣習上は「自分の」が標準だが、本文(We can't apply **its** findings=研究の結果)では「研究/他者の結果」が実態であり、どちらも許容範囲。よって、Std生成の誤り(所有者誤りNG)と分類した3出力(Trial_03: G0 reach「人の財布」、G3 reach「誰かの財布」、G3 apply「人の研究結果」)は**NGから外し、「見出し語の人称placeholder不整合(生成器の誤りではない)」として別掲**する。Std確定NG(第3回、各120出力)は **G0=2(字義訳: an unseen clock×2)、G2=1(字義訳: draw a line「はっきりと線を引く」)、G3=0**。
- Adv「59/60」の唯一のNG(reach rep1 "to move your hand toward another person's wallet to take or use it")も、見出し語 "someone's" に忠実な出力であり、Std/Advは互いに整合している。問題は見出し語が本文の指示対象(your wallet=自分の財布)と一致していないこと。したがって「Std誤り→Adv波及 1/5」は「見出し語不整合→Std/Advが揃って見出し語に従った1件」に訂正し、Std意味生成の誤りに起因するAdv NGは**0件**とする。
- 本文との関係の整理: Std意味で本文が関係するのは「字義/比喩のどちらの語義か」の選択だけ。所有者(自分/他人)は見出し語自身が決めるべきもので、見出し語の正規化(canonicalization)が "your wallet"→"someone's wallet" と置いた場合、意味は見出し語どおり「他人の財布」になる。本文の意味(自分の財布)を伝えたいなら見出し語を "reach for one's wallet" にするのが正しい(記事Bの実際のKPは `reach for one's wallet` であることを確認済み: 委任_08報告)。
- 残る実質的な問題は2種類: (a)比喩表現の字義訳(an unseen clock、draw a line「線を引く」)、(b)見出し語の人称placeholder(one's/someone's/the)が本文の指示対象と一致していないケース(Trial KP集合内で確認)。

