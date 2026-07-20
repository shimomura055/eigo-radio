# ER-003 Natural English Source 正式仕様(ER-003-P2 Part A)

管理ID: ER-003-P2
確定日: 2026-07-20

## 1. 正式採用したもの

ER-003-P1B(固定構造付き自然英訳)の方式を、日本語記事を英語ポッドキャスト原稿へ変換する内部基準原稿「Natural English Source」の正式な生成条件として確定する。

| 項目 | 内容 |
|---|---|
| 入力 | 条件Lで承認済みの日本語記事(reading_copy.md) |
| translator実行回数 | 1テーマにつき1回(バッチ生成はしない) |
| model | `gpt-5.6-sol` |
| reasoning effort | `high` |
| API | OpenAI Responses API |
| Web検索 | なし |
| 英語マスター | なし |
| CEFR・語彙・文長・語数制約 | なし |
| 出力形式 | 自由Markdown(Structured Outputは使わない) |
| 固定構造 | `## Today's {テーマ表現} Points` / `### Point One: {切り口}` / `### Point Two: {切り口}` / `## In One Line` |
| 構造再試行 | 構造不適合時のみ、同一条件で最大1回 |
| 内容品質理由の再翻訳 | 行わない |
| 事後QA | 独立した日英整合性QA(PASS/REVIEW_REQUIRED/FAIL) |
| 最終判断 | ユーザー |

Natural English Sourceは商品としてのC1版ではなく、B2・B1・A2の各レベル版を独立して生成するための内部基準原稿である。

## 2. 承認内容

### A01: 2026年ワールドカップ準決勝のイングランド対アルゼンチン

P1Bのraw本文のうち、次の2見出しのみを軽微修正した。他の本文・タイトル・導入・数字・固有名詞・出来事の順序は一切変更していない。

| 変更前 | 変更後 | 理由 |
|---|---|---|
| `Point One: Messi Wasn't the Scorer—He Was the Finisher` | `Point One: Messi Wasn't the Scorer—He Was the Creator` | "finisher"は実際に得点を決める選手という意味に聞こえ、本文(得点はしていない)と衝突するため |
| `Point Two: One Team Substituted to Defend; the Other, to Win` | `Point Two: One Team Substituted to Defend; the Other, to Attack` | "to win"は元の日本語「攻める交代」より含意が強いため |

### A02: 英国の未成年向け夜間SNS設定

P1B本文をそのままNatural English Sourceとして採用(byte-for-byte一致)。fidelity QAの注意事項(因果表現の強まり、自動再生/おすすめフィードの時間帯範囲の解釈差、最長文61語)は`natural_source_approval.json`に記録し、本文は自動修正していない。

### ADD03: ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応

P1B本文をそのままNatural English Sourceとして採用(byte-for-byte一致)。

## 3. 保存場所

各記事の`er002/er003`出力ディレクトリ配下(`er003_output/p1b/<TOPIC>/`)に、P1Bの生の成果物を上書きせず新規保存した。

- `natural_source_approved.md` — 確定本文
- `natural_source_approval.json` — 承認記録(差分・理由・sha256・引き継ぎQA注意事項)
- `natural_source_sha256.txt` — 確定本文のsha256(1行)

## 4. 試行成果物の保存改善

今後、構造再試行が発生した場合は、失敗した試行の本文・生応答・構造判定も含めて全attemptを保存する(`attempt_N_raw_response.json` / `attempt_N_article.md` / `attempt_N_structure_check.json`)。

既存のP1B実行(A01・A02はいずれも初回構造ゲート不合格→1回再試行)では、初回失敗時の本文は保存されていなかった。これを事後的に再生成・推測・復元することはしない。該当する`natural_source_approval.json`には`ATTEMPT_1_BODY_NOT_PRESERVED_IN_LEGACY_P1B_RUN`と明記している。

保存仕様の改善は、ER-003-P2以降の新規実行(B2 adapter等)にのみ適用する。
