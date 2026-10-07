# human_review_pack (OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01) テンプレ

ユーザー確認用。V0/V3/V5/V6 の記事を全文収録する。対象は meta・hormuz の b1w1(JA=revision2、EN=b1b)。PM側が評価完了後に `<<...>>` を実ファイル本文で置換して `er052_output/open233_b3_trial_01/eval/HUMAN_REVIEW_PACK.md` に出力する(記事本文を要約・加工しない)。判定(重大/軽微)は単独評価で人間確認前である旨を冒頭に書く。

## 収録対象(8記事 x JA/EN = 16本文 + 8 brief)
| # | テーマ | 条件 | run(b1w1) |
|---|---|---|---|
| 1-4 | meta | V0 / V3 / V5 / V6 | `er052_output/open233_b3_trial_01/runs/meta/nb/<V>/b1/w1/` |
| 5-8 | hormuz | V0 / V3 / V5 / V6 | `er052_output/open233_b3_trial_01/runs/hormuz/nb/<V>/b1/w1/` |

## raw URL規約
- 形式: `https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<repo相対パス>`(例 `.../er052_output/open233_b3_trial_01/runs/meta/nb/V3/b1/w1/ja_writer/revision2.md`)
- commit・push済みのファイルのみURLを載せる(未pushを載せない)。各記事ブロックの見出し直下に brief / JA / EN の3 URLを列挙する。

## 記事ブロック(#1〜#8を同形式で繰り返す。順序は meta V0,V3,V5,V6 → hormuz V0,V3,V5,V6)
### #<n> <slug> <V> (b1w1)
- brief: <raw URL> / JA(revision2): <raw URL> / EN(b1b): <raw URL>
- 評価(単独評価): ①JA 重大<a>/軽微<b>、②EN 重大<c>/軽微<d>、退行 重大<e>/軽微<f>、★ <fact_id>=<label>…
- 該当NG(あれば id・該当文): <<ng_items抜粋>>
- brief_review: 主体等省略文数 <n>、別fact限定語連結 <有/無>、未提示明記 <有/無/n/a>

#### selected_brief.md 全文
<<selected_brief.md 全文>>

#### 日本語(ja_writer/revision2.md)全文
<<revision2.md 全文>>

#### English(b1b/article.md)全文
<<article.md 全文>>

## 末尾(PM記入)
- ユーザーへの確認依頼: 各記事を読み、事実の取り違え・不自然さを感じた箇所と、構造条件(V0/V3/V5/V6)の読み味の差を教えてください(Production採用の判断ではない)。
- Production変更: なし / API費用: ¥0(評価のみ)
