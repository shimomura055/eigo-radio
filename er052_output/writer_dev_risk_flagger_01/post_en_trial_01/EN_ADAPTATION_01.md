# EN_ADAPTATION_01: 英語入力への適応(最小差分)

## (a) 文分割
既存の `run_flagger_01._split_sentences`(P3/P4のarm_new_en英語稿ですでに使用済み)を**変更せず**そのまま使用。見出し行(#, ##)も1文として残る。入力は `post_en_trial_01/inputs/*.md`(固定コピー)。文IDと本文は各 `flags/<level>/<unit>_<theme>.json` の `sentences` に保存。
既知の限界(変更はしない。仕様追加禁止のため): 分割規則は `(?<=[.!?])\s+` で、`.”` `!”` のように閉じ引用符が間に入ると文が分割されず次の文と1つの文IDにまとまる。このため一部の文IDは2文以上を含む(例: U08 s25、X10 s5)。Flag対象文を読む際は該当文IDの全文を確認する必要がある。

## (b) A3/A4 prompt: 差分ゼロ
`prompts_flagger.COMMON_HEAD` に既に『台帳は日本語、記事の文は英語や日本語のことがあります。』とある。したがって『入力記事は英語であり台帳(日本語)と照合する』旨の注記を**追加しない**(Fable補足の『日本語記事を前提にしている箇所があれば』の条件に該当しない)。重大定義・候補化条件・出力形式・確信度方針は一切変更していない。

| 項目 | sha256 |
|---|---|
| 実使用 A3 system prompt (`antenna_prompts.antenna_system(3)`) | `9d9950428419c3af824cc5b8676a4b564f96aeb87657c547d418cc86ef3538e9` |
| 元のANTENNA-TRIAL-01 A3 | `9d9950428419c3af824cc5b8676a4b564f96aeb87657c547d418cc86ef3538e9`(同一。ANTENNA PREREGISTRATIONの値と照合) |
| 実使用 A4 system prompt | `c87b95e5bcf1b5c266b8978c5688849eb339a6087efbcaf56bb7399ed128ef01` |
| 元のANTENNA-TRIAL-01 A4 | `c87b95e5bcf1b5c266b8978c5688849eb339a6087efbcaf56bb7399ed128ef01`(同一) |
| 現行D2 (`prompts_flagger.d2_system()`) | `b8dacc147009a13bea886d5d97d387fc5ff06171d878fcae7fdddbd18fd6d405` |
| `antenna_prompts.py` ファイルsha256 | `f62c026b767eeed3c4eb4dcf6405c1946b2579a00686e3fb05be48230bf74bf5` |
| `prompts_flagger.py` ファイルsha256 | `730bc55f7ff1a8186e5555c431c75b2f67dc45951bb32315935b99ff15973e0c` |

userメッセージ(`prompts_flagger.build_user`): `{facts:[{fact_id,text}], sentences:[{sid,text,before:'',after:''}]}` のJSON。Fact textは日本語台帳のブロック全文(scope/conditions/notes等を含む)、sentencesは英語。ラベル・Checker指摘・既知例名は一切渡さない。
モデル: gpt-6.1-sol / reasoning effort=medium(ANTENNA-TRIAL-01と同一)。
Production/detectors/antenna_trial_01 配下は無変更(importのみ)。
