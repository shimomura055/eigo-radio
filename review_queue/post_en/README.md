# Post-EN Review Queue(ChatGPT向けの読み方)

英語記事(Advanced / Standard)が完成した後、**Risk Flagger**(RF)が「人間が確認した方がよい文」を候補として列挙した結果の置き場です。
RFは合否判定をしません。記事を書き換えません。生産を止めません。ここにあるのは**候補一覧**で、本物の問題かどうかを判断するのはHuman Review(あなた)です。

## まず見るファイル
1. `index.jsonl` : 1行=1回のRF実行(記事×Level)。追記専用。`queue_path` がこのディレクトリからの相対パス。
2. `<article_id>/<article_level>__<run_id>/queue.md` : 人間向けに整形した候補一覧。
3. 同ディレクトリの `queue.json` : 同じ内容の機械可読版(下記schema)。

## Level
- `b1b` = Advanced(完成したAdvanced英文)
- `a2` = Standard(Advancedから簡略化して作った完成Standard英文。主目的は「簡略化でFactの意味が壊れていないか」の検出)

## queue.json の主なフィールド
- `status`: `OK`(4条件すべて成功) / `PARTIAL`(一部の条件が失敗) / `RF_UNAVAILABLE`(RFが実行できなかった。この場合 `reason` を見る。候補0件は「問題なし」ではない)
- `issues[]`: 候補。1文=1件(複数モデル・複数条件の検出は1件に統合し、`detected_by[]` に誰が何の確信度で出したかを残す)
  - `issue_id`, `article_id`, `article_level`, `article_sha256`, `run_id`, `timestamp`
  - `sentence_id`(`s1`,`s2`,…。記事を分割した文の番号。`inputs/sentences.json` と対応), `sentence_text`
  - `context.before/after`: 前後の最大2文(確認の補助。LLMには渡していない)
  - `related_fact_ids` と `facts[]`: 根拠として挙げられた台帳Fact(本文つき)
  - `flag_reasons[]`: 確認してほしい理由(type と、人間向けの確認質問)
  - `detected_by[]`: `model_key`(luna / gemini35fl)・`model_id`・`condition`(A3 / A4)・`confidence`・`raw_flag_source`(`raw/` 内の生応答ファイル)
  - `confidence`: 検出元の中の最大値
- `conditions[]`: 4条件(Luna A3/A4、Gemini A3/A4)それぞれの成否・トークン・費用
- `model_stats`: model別の件数(A3/A4フラグ数、重複なし件数、A3とA4の重なり、0件記事など)
- `unlocated_flags[]`: 文IDに対応づけられなかったフラグ(現状は常に空)
- `producer` / `run_label`: 入力の由来(`trial_fixture` は開発用fixture由来で、Production初回記事ではない)記録用。判定には使わない

`review_state`(人間の判定状態)はこのQueueには持ちません。判定はHuman Review側で保持します。

## 補助ディレクトリ
- `inputs/sentences.json` : RFが見た文ID付きの記事全文。`inputs/ledger.txt` : RFに渡した完全台帳。
- `raw/` : 各条件の生API応答(JSONL)。再現・監査用。

## 注意
- 文IDは本Queue専用の分割(`splitter_version` を確認)で振られており、過去のTrial検証の文IDとは一致しません。照合は `sentence_text` で行ってください。
- Queue保存に失敗した場合は、記事のoutput dir内の `risk_flagger_fallback/` に同じ内容が残ります。
