# Jev API docs調査メモ

取得日時: 2026-09-24 (JST)。鍵は一切使わずcurlのみで取得(`https://www.jevai.org`は
robots.txt上クロール許可、`User-Agent: *` / `Allow: /`)。

## 重要な注記(未確認ではなく確認できた事実として記録)

`https://www.jevai.org` のページ内テキスト(サイト共通ヘッダー、JSON埋め込み文字列)に
以下の文言が存在する:

> "A community for Jev model playbooks and shared usage — not the official
> product site. Official website: here"

および 404ページのメタ情報に:

> "...around Jev AI. Not the official TypeSafe AI product site."

つまり `www.jevai.org` は **Jev/TypeSafe AI社の公式サイトではなく、コミュニティサイト**
であることがページ自身の記述から確認できた。ただしAPIドキュメント
(`/docs`, `/jev-api`)はこのコミュニティサイト自身がホストする実働API
(`https://www.jevai.org/api/v1/decisions`)の仕様として書かれており、
ユーザー提示の接続仕様(Base URL/Endpoint/Auth/Content-Type/Response形式/
32 KiB上限)と完全に一致した。委任文で明示された正確なURL・endpointへ
接続する指示のため、この事実確認のみ行い接続試行自体は継続した
(Open Item候補として報告、STOP条件には非該当)。

## 取得ページ

1. `https://www.jevai.org/sitemap.xml` (200, 94620 bytes) — `/docs`, `/jev-api`
   等のURL一覧を確認。
2. `https://www.jevai.org/docs` (200, 92480 bytes) — Next.js SSRページ。
   本文中にAPI仕様のHTML断片とNext.js RSCペイロード(JSON文字列)の両方が
   含まれる。
3. `https://www.jevai.org/jev-api` (200, 82220 bytes) — Playground/使用例
   ページ。UI文言としてscore typeの詳細仕様(レベル数上限・0始まりindex・
   確率加重平均)を含む。

## 確認できた項目(逐語引用、HTMLエンティティはデコード済み)

- Base URL / Auth: "All calls are POST to https://www.jevai.org. Do not use
  http or the apex host. Off-site clients send `Authorization: Bearer` with
  a personal key from /agent/keys."
- Body size: "Body size is capped at 32 KiB. Responses are { code, message,
  data }. code 0 is success. Treat probabilities as signals, not
  authorization."
- Native Decisions endpoint: "No preset fits. Send your own state plus
  choice, noul, or score questions." → "POST /api/v1/decisions. Required:
  state, questions. Optional: model (Jev identifier only). Typical decision:
  per question in answers."
- Native questions: "POST /api/v1/decisions accepts model, state, and
  questions. Only Jev identifiers are allowed, such as typesafe-ai/jev. Do
  not call /chat/completions. Each question is choice, score, or noul."
  - "choice: pick one option from criteria. Returns choice, probabilities,
    confidence."
  - "score: ordered levels. Returns score, probabilities, optional legend."
  - "noul: probability of yes. Returns noul between 0 and 1."
- score type詳細(Playgroundフォームヘルプ文言): "Fill in 2–10 levels,
  ordered low to high. Scores start at 0." / "Array of 2–10 descriptive
  levels, ordered low to high. Level numbers start at 0. The returned score
  is a probability-weighted average and can land between levels. Three
  levels are 0–2, not 1–3."
- questions/idフィールド: "questions[id]: One typed judgment. Put the full
  meaning in instructions, not in the ID." / "instructions: string / object
  / array. The complete question." / "criteria: depends on type. Choice
  options, Score levels, or optional Noul true/false descriptions."
- Response(Playground UI表記、rawなREST応答と表現が異なる可能性あり):
  "A run returns result and elapsedMs. result.answers is keyed by the same
  question IDs you sent."
- 除外パラメータ: "temperature, top_p, max_tokens and stream are not
  Playground fields."
- セキュリティ注記: "Keep irreversible actions behind your own human
  approval. Do not send passwords, API keys, or unrelated private data."

## 確認できなかった項目(推測実装しない、「不明」のまま扱う)

- **rate limit**(ヘッダ名・上限値・時間窓): ドキュメント本文に
  "rate limit" "429" "Retry-After" 等の記述が見つからなかった
  (grep結果ヒットなし)。→ 実接続時にHTTPヘッダを実測し、無ければ「不明」
  と記録する。
- **usage・課金・pricing情報**: 上記docsページ内に「pricing」という語は
  サイト共通フッターのメニュー項目文言("footer":{"pricing":"Pricing"})
  としてのみ存在し、API応答内のusage/token/costフィールドの仕様は見つから
  なかった。→ 実接続時にresponse bodyへ`usage`等のキーが含まれるか実測し、
  無ければ「Jev cost UNKNOWN」と記録する。
- **score応答の完全なworked example**(数値付きJSON)は見つからなかった
  (choiceタイプの完全example[refund]のみ確認、score/nоulの完全response
  exampleはdocsに掲載なし)。→ 実接続で実測し、`jev_probe.json`へ記録する。
- 公式(非コミュニティ)Jevサイトの実体・仕様差分は未確認(本タスクの
  接続対象外、Open Item候補として報告のみ)。

## 本Trialでの設計判断(docsに基づく、推測を最小化)

- `criteria`は2〜10レベルの制約があるため、Luna等の1〜10スケールに近づける
  ため10レベル("Level 1"〜"Level 10")のscore questionとして設計する。
  返るscoreは0始まりのprobability-weighted average(0〜9の連続値)である
  ため、`predicted_score_1_10 = raw_score + 1`の線形変換を適用する
  (docsの"Level numbers start at 0"に基づく)。この変換は各candidateへ
  一様に適用するため、Top20順位(相対順位)には影響しない。
- `model`フィールドは省略する(委任文指定どおり、サービス側defaultを使用)。
