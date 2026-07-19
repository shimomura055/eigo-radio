# ER-002 記事生成 正式仕様(ER-002-v1.2M-R4-FINALIZE)

管理ID: ER-002-v1.2M-R4-FINALIZE
決定日: 2026-07-19

## 1. 正式採用したもの

ER-002-v1.2M-R4で比較検証した「条件L」(1テーマにつきwriterを1回実行し、
阪神マスターと同程度の読み上げ分量に収める長さ指示を追加する方式)を、
ER-002の正式な記事生成仕様として採用する。

| 項目 | 内容 |
|---|---|
| writer実行回数 | 1テーマにつき1回(バッチ生成はしない) |
| model | `gpt-5.6-sol` |
| reasoning effort | `high` |
| API | OpenAI Responses API |
| Web検索 | writer自身が組み込みWeb検索ツールを使用し、検索語・検索回数・参照情報・切り口を自ら判断する |
| 出力形式 | 自由Markdown(Structured Outputは使わない) |
| ポイント構造 | レベル3(`###`)見出しをちょうど2つ |
| 長さ指示 | R3のwriter promptに、長さ指示3文だけを追加する |
| fact checker | R3から一切変更しない(独立したResponses API実行、Web検索必須、Structured Output、JSONスキーマ検証) |

## 2. 使用するコード

- `er002_ja_article_generation.py` — 正式採用モジュール(読み上げ文字数の正規化、長さ指示付きプロンプト構築、技術的失敗のみの再試行ゲート、診断分類)
- `er002_ja_web_research_r3.py` — writer本体呼び出し・独立fact checkerロジック(R3から不変)
- `er002_v1_2m_length_spec.json` — 読み上げ文字数の基準値・許容範囲(単一の情報源)
- `er002_v1_2m_generate_article.py` — 正式な記事生成の実行スクリプト(1テーマ1writer実行のみ、バッチ/LBモードは存在しない)

### 実行方法

```
.venv/Scripts/python.exe er002_v1_2m_generate_article.py <topic_id> <topic>
```

例:

```
.venv/Scripts/python.exe er002_v1_2m_generate_article.py A01 "2026年ワールドカップ準決勝のイングランド対アルゼンチン"
```

成果物は `er002_output/v1_2m_article_generation/<topic_id>/` に保存される。

## 3. 読み上げ文字数の計測仕様

`spoken_text_char_count` は次の手順で計測する(`er002_ja_article_generation.py`の
`compute_spoken_text_char_count`)。

1. OpenAI Responses APIの応答が持つcitation annotation(`start_index`/`end_index`)を使い、引用表示部分を文字位置ベースで除去する
2. Markdown記号(見出し・強調・コード・リンク構文など)を除去する
3. URL・HTMLタグを除去する
4. Unicode NFKC正規化を行う
5. 空白・改行・タブをすべて除去する
6. 残った文字数を`len()`で数える(句読点は含める)

citation annotationを取得できない場合は、推測で本文を削らず
`COUNT_EXTRACTION_UNCERTAIN`として扱う(引用でない括弧書きなどを誤って
削除しないため)。

### 基準値・許容範囲(`er002_v1_2m_length_spec.json`)

| 項目 | 値 |
|---|---|
| 阪神マスターの読み上げ文字数 | 697字 |
| 許容下限(下限85%) | 592字 |
| 許容上限(上限115%) | 802字 |

将来この基準値を変更する場合は、`er002_v1_2m_length_spec.json`を
再計算・上書きするだけでよい(コード中の数値を探して書き換える必要はない)。

## 4. fact checkerの扱い

- R3で使用したfact checkerのプロンプト・判定ロジックは変更していない。
- 判定は `PASS` / `REVIEW_REQUIRED` / `FAIL` の3値を維持する。
- `FAIL`の記事は採用成果物として扱わない。
- `REVIEW_REQUIRED`を自動的に`PASS`へ読み替えることはしない
  (`er002_ja_article_generation.FACT_CHECK_INCLUDE_VERDICTS = ("PASS", "REVIEW_REQUIRED")`
  であり、`REVIEW_REQUIRED`は「レビュー対象として含める」であって
  「PASSとみなす」ではない)。

## 5. 自動再生成を行わないもの

次を理由とした自動再生成は、今回の仕様には含めない(初回遵守率を維持する設計):

- 文字数超過・不足
- 構造不適合(Point数が2でない)
- fact-QAが`REVIEW_REQUIRED`または`FAIL`
- 記事の面白さ・切り口への不満

再試行するのは、通信エラー・タイムアウト・応答本文取得不可といった
技術的失敗のみ、最大1回。

## 6. 不採用: 条件LB(複数記事同時生成)

ER-002-v1.2M-R4では、3テーマを1回のwriter実行で同時生成する「条件LB」も
比較検証したが、**正式仕様として採用しなかった**。

理由:

- 条件LBのA01(2026年W杯準決勝)で、独立fact checkerにより明確な事実矛盾
  (トゥヘル監督が「守勢に回った判断を悔やんだ」という記述が、本人が
  実際の会見で繰り返し「後悔はない」と明言した事実と矛盾)が検出され、
  `FAIL`となった。
- 1記事あたりのwriter実行を独立させる条件Lのほうが、運用上の障害分離
  (1テーマの失敗が他テーマに影響しない)の観点でも優れると判断した。

条件LBのコードは、実験の再現性のために `er002_ja_web_research_r4.py` と
`er002_v1_2m_r4_generate.py`(`lb`サブコマンド)にのみ残しており、
**正式な記事生成フローからは一切呼び出されない**。今後これらのファイルを
本番経路から呼び出さないこと。

## 7. 実験記録(参考)

- `er002_output/v1_2m_r4/condition_l/` — 条件Lの実API生成結果(A01/A02/ADD03)
- `er002_output/v1_2m_r4/condition_lb/` — 条件LBの実API生成結果(参考、A01はFAILのため不採用)
- `er002_output/v1_2m_r4/ER-002-v1.2M-R4_user_review.md` — R3・条件L・条件LBの比較レビュー
- `er002_v1_2m_r4_generate.py` / `er002_v1_2m_r4_preflight.py` — R4比較実験用スクリプト(実験記録、通常運用では使用しない)
