# E_hormuz 評価(OPEN-233-NOTE-TRANSFER-MATRIX-TRIAL-01 委任_C2)

単独判定・人間確認なし。基準=eval_rubric.md。T0M0 rep1は `rep1_failed_a1` を採用標本とした。T2M0 rep1は対象外(追補待ち)。

| 記事 | ①JA 重大/軽微 | ②EN 重大/軽微 | 退行 重大/軽微 | ★fact | 保留 |
|---|---|---|---|---|---|
| T0M0 rep1 | 0/1 | 0/1 | 0/0 | HF-007 correct / HF-009 ambiguous | 0 |
| T0M0 rep2 | 0/0 | 1/0 | 0/0 | HF-007 correct / HF-009 correct | 1 |
| T0M1 rep1 | 0/0 | 0/0 | 0/0 | HF-007 correct / HF-009 correct | 1 |
| T0M1 rep2 | 0/0 | 0/0 | 0/0 | HF-007 correct / HF-009 correct | 1 |
| T1M0 rep1 | 0/0 | 0/0 | 0/0 | HF-007 correct / HF-009 correct | 1 |
| T1M0 rep2 | 0/1 | 0/1 | 0/0 | HF-007 correct / HF-009 ambiguous | 1 |
| T1M1 rep1 | 0/2 | 0/2 | 0/1 | HF-007 correct / HF-009 correct | 0 |
| T1M1 rep2 | 0/0 | 0/0 | 0/0 | HF-007 correct / HF-009 correct | 1 |
| T2M0 rep2 | 0/0 | 0/0 | 0/0 | HF-007 correct / HF-009 correct | 1 |
| T2M1 rep1 | 0/1 | 0/1 | 0/1 | HF-007 correct / HF-009 correct | 0 |
| T2M1 rep2 | 0/2 | 0/2 | 0/1 | HF-007 correct / HF-009 correct | 0 |

## 重大NG(1件)
- hormuz-T0M0r2-01 (ENのみ): EN: 「Mr. Trump posted that for all cargo passing through the Strait of Hormuz, the United States would seek payment equal to 20 percent of the cost of providing safety and security.」(台帳は全貨物への償還率20%(算定基礎は未明記)。ENは「安全確保費用の20%相当」と読め、20%の対象が貨物から費用へ入れ替わる。JA「安全と警備を提供する費用として、二十パーセントの償還を求める」は正しい。同記事ENは直後に算定方法の未提示を書き、内部でも不整合)

## 補足
- 軽微の主類型: (a)価格の「一時的な上げ幅縮小」が「価格下落/縮む」に読める(HF-009 ambiguous 2記事)、(b)台帳「示されなかった」を「未決定/白紙」に強めた(T1M1r1,T2M1r1,T2M1r2。いずれもR0は正しく退行)、(c)「もっと大きな不安」の重み比較(T1M1r1,T2M1r2)。
- 判定保留は各JSONのpending参照(多くはno_ng寄り、T1M0r1のEN曖昧のみminor寄り)。
- ng_items全文は eval/articles/hormuz_*.json。

## 追補(委任_D1、2026-10-07): T2M0 rep1(停止枠の再実行成果)
単独判定・人間確認なし。記事本文を先に判定し、その後に条件ラベルを記録。既存本文は不変。

| 記事 | ①JA 重大/軽微 | ②EN 重大/軽微 | 退行 重大/軽微 | ★fact | 保留 |
|---|---|---|---|---|---|
| T2M0 rep1 | 0/0 | 0/0 | 0/0 | HF-007 correct / HF-008 correct / HF-009 correct / HF-011 correct | 2 |

- 台帳HF-002/003/006/007/009/011と整合(提案は7/13、撤回・置換は7/14、価格は一時縮小後に回復、撤回との因果は断定しない)。
- 保留2件(いずれもno_ng寄り): 償還案を「料金案」と呼称、EN末尾One lineの「tensions kept oil prices high」。詳細は articles/hormuz_T2M0_rep1.json。
