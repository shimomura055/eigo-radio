# ER-003-EN-DIRECT-AB-01 実行報告(A02 英語直接生成 A/Bテスト)

**管理ID: ER-003-EN-DIRECT-AB-01**
**実施日: 2026-08-12**
**ステータス: `PROTOTYPE / EXPERIMENT`(Production仕様は変更していない。採否はユーザー判断待ち)**

## A. Executive Summary

A/B生成は**両方とも成功**した(技術的失敗・構造不適合なし、再試行0回)。
勝者はまだ決めない。ただし独立fact checkerの結果は明確に非対称だった。

- **A版(現行方式、既存Natural English Source)**: fact check `REVIEW_REQUIRED`(軽微な解釈上のニュアンス2件、事実矛盾なし)
- **B版(英語直接生成、新規実験)**: fact check **`FAIL`**(一次情報源と明確に矛盾する事実誤り2件を検出)

B版は文体面(フック・リズム・master方式のセンスの転写)でA版に劣らない、
むしろ一部で優れている側面が見られた一方、**事実精度で明確な問題**が
確認された。詳細はD・E節を参照。

## B. A版

- **source file**: `er003_output/p1b/A02/natural_source_approved.md`(既存、今回無修正。
  `er003_output/a2_p1_r3/A02/master_en_natural_source_approved.md`とbyte-for-byte一致を確認済み)
- **word count**: 418語(`er003_output/p1b/A02/translation_metrics.json`記録値、
  および独自の正規表現カウントで再検証し一致を確認)
- **fact status**: `REVIEW_REQUIRED`(`er003_output/p1b/A02/fidelity_qa.json`、
  P1B時点の日英fidelity QA。矛盾ではなく解釈上のニュアンス変化2件・主体の
  明示1件を指摘。詳細はD節)

## C. B版

### 実prompt差分(R4「条件L」からの変更点、この2つのみ)

| 項目 | R4(Production、日本語出力) | B版(実験、英語出力) |
|---|---|---|
| developer message | `日本語の記事を作成してください。` | `英語の記事を作成してください。` |
| user prompt本文(instruction) | 不変(R3テンプレート) | **不変**(R3テンプレートを一字一句同一のまま使用) |
| 長さ指示(末尾3文) | 阪神マスター文字数基準(697字、592〜802字) | A版Natural English Source語数基準(418語、355〜481語、soft target)。日本語の文字数制約を英語へ機械的に転用せず、この実験用に新規作成 |
| 阪神master入力 | 全文(日本語) | **全文(日本語、不変)**。英語masterは新規作成していない |
| Web検索 | `tools=[{"type":"web_search"}]` | 不変 |
| 事前Facts/concise brief | 渡していない | 不変(渡していない) |

- **model**: `gpt-5.6-sol`
- **reasoning effort**: `high`
- **API**: `responses.create`(Responses API)
- **Web検索**: writer呼び出し内で3回(検索クエリはモデル自身が判断。
  `er003_output/en_direct_ab_01/A02/writer_sources.json`に参照ソース記録)
- **word count**: 410語(soft target 355〜481語の範囲内)
- **fact status**: **`FAIL`**(独立fact checker、Web検索6回。詳細はD節)
- **再試行有無**: **なし**。writer・fact checkerとも1回の呼び出しで完了
  (`content_attempt_count: 1`、技術的失敗・構造不適合・Web検索未使用は
  いずれも発生しなかった)

## D. Fact QA(A/B主要fact比較)

**A版(REVIEW_REQUIRED、矛盾なし)**:
- 「During those hours」が自動再生・おすすめフィードにも係るため、これらが
  午前0時〜6時限定であるかのように読める(日本語原文は時間帯を明示せず)
- 「produced」が試行結果との因果関係をやや強く読ませる
- 利用時間をずらした主体を「some teenagers」と明示(日本語原文は主体不特定)

**B版(FAIL、一次情報源と矛盾する事実誤り2件)**:
1. **矛盾**: 冒頭で「午前0時になると自動再生・パーソナライズドフィードが
   止まる」ように描写しているが、公式資料(gov.uk fact sheet)では、これら
   の機能は夜間の時間帯制限とは別に、**時間帯に関係なくデフォルトで無効化**
   される。時間的な描写が制度内容と矛盾する
2. **矛盾**: 「309 families」が夜間制限(9時〜7時)を試したかのように書いて
   いるが、309人は4条件合計の試行参加者全体の数であり、**夜間制限群は
   実際には81人**だった
3. (補助的な指摘)Ofcomのデフォルト効果を「自動的な習慣を中断できる」と
   一般化する記述、および「produced the clearest sleep benefits」という
   因果的な言い切りは、それぞれの調査の実際の範囲(模擬環境での実験、
   小規模で自己選択的な質的パイロット)を超えた解釈である

**重点確認事項(旧"would not open at first"問題の再発有無)**: B版の本文には
"would not open"に相当する表現は無く、その字面上の問題は再発していない。
ただし、**同じ「制度の適用範囲・タイミング」という種類の精度問題が、
別の形(自動再生・フィードの無効化タイミングの誤り)で新たに発生した**。
これは単純な表現上の巧拙ではなく、Web検索から得た情報を要約・構成する
過程で生じた事実精度の問題であり、A版のP1B fidelity QAが指摘した
ニュアンス変化より深刻度が高いと判断する。

## E. Quality QA(9観点、A/B並列)

詳細な根拠は比較Artifact(F節)にも掲載。要約:

| # | 観点 | A版 | B版 |
|---|---|---|---|
| 1 | Fact accuracy | REVIEW_REQUIRED、矛盾なし | **FAIL**、矛盾2件 |
| 2 | Meaning precision | 軽微な解釈のずれ | 制度理解に影響する誤り |
| 3 | Grammar | 良好 | 良好(差なし) |
| 4 | Idiomaticity | 自然 | 自然、やや文学的な装飾が多い |
| 5 | News narration naturalness | 一貫して報道文調 | 冒頭に事実に基づかない場面描写(「11:59 p.m.、10代がクリップを見ている」)を追加。ニュース原稿としては脚色寄り |
| 6 | Editorial engagement | 手堅い導入 | 導入のフックとテーゼ文がより強い |
| 7 | Master-style transfer | 概要→2ポイント→一言、という構成は転写されている | 短い断定的な一文を積み重ねる阪神masterのリズムが、A版よりも色濃く再現されている |
| 8 | Point differentiation | Point One=試行の実用性、Point Two=デフォルトの心理効果。明確に異なる切り口 | 同じ2つの切り口(順序が逆)。差別化の程度は同等 |
| 9 | Downstream(B1/A2)適性 | 既にB1/A2のSourceとして本番採用実績あり | 事実誤り2件の訂正・再検証なしにそのまま下流へ渡すのはリスクがある |

**このタスクの最重要目的への回答**: 「日本語を経由する価値が本当にあるか」
という問いに対し、今回1回の実験では**部分的に「価値がある」という結果**
になった。編集センスの転写(観点6・7)はB版がA版と同等かそれ以上に見える
一方、**事実精度(観点1・2・9)ではA版が明確に優位**だった。日本語を経由する
2段階方式(現行フロー)は、fact checkerが独立して2回検証する機会
(条件Lのwriter直後+P1Bのfidelity QA)を持つのに対し、B版は英語生成+
fact check1回のみで、今回はそのfact checkがまさに問題を検出した形になった。

## F. 比較Artifact

ユーザーが直接読める比較ページ(A/B全文・fact QA詳細・9観点表)を作成した。

**URL**: https://claude.ai/code/artifact/cf0ca678-7798-425d-8b21-7d0c115ab2e6

リポジトリ内の原本: `er003_output/en_direct_ab_01/A02/comparison.html`

A/B本文の直前には「Version A」「Version B」というラベルのみを表示し、
生成方式の説明や優劣を示唆する文言は本文の前に置いていない(生成条件の
詳細は本文の後、ページ下部の「Generation conditions」節にのみ記載)。

## G. OPEN-35

[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-35を確認したところ、「3記事とも音声は
未再生成」という**事実**は記録済みだったが、「夜間にまとめて処理したいため
意図的に保留している」という**理由**は前回監査時点で未記録だった
(前回[ER-003-JP-STYLE-AUDIT-01_REPORT.md](ER-003-JP-STYLE-AUDIT-01_REPORT.md)
9節で報告済み)。

今回、ご指示に基づきOPEN-35へ以下の一文のみを追記した(仕様変更ではなく
記録の追記):

> **ユーザーDecision(2026-08-12): 音声最新化は実施する方針で確定済みだが、
> 夜間にまとめて処理したいため、日中は意図的に保留中。**

OPEN-35のステータス(`TBD`)は変更していない。**CLOSEしていない。**

## H. 非変更確認

- **CURRENT_SPEC.md**: 無変更
- **Production prompt**(`er002_ja_article_generation.py`・`er002_ja_web_research_r3.py`等): 無変更。
  今回のB版生成は新規の独立スクリプト`er003_v1_en_direct_ab_01_generate.py`
  から、これらのモジュールの関数を読み取り専用でimportして使用した
- **R4既存成果物**(`er002_output/v1_2m_r4/condition_l/`等): 無変更、上書きなし
- **ER-003-P1B**・**`reading_copy.md → Natural English Source`**変換フロー: 無変更
- **B1/A2生成**: 実施していない
- **Key Phrase生成**: 実施していない
- **TTS・音声assemble・WPM調整・Pause/Outro変更**: 実施していない
- **新規Topic**: 使用していない(既存A02のTopicのみ)
- **英語master**: 新規作成していない(阪神masterを日本語のまま使用)
- **A版本文**: 修正していない

## I. 次のDecision(3択、ユーザー判断待ち)

1. B方式を次のADD03検証へ進める
2. B方式を修正して再テストする(例: fact checker FAILを踏まえ、事実精度を
   高める調整を加えた上で再実験)
3. 現行A方式(日本語経由の2段階方式)を維持する

今回の1回限りの実験結果からは、**B方式の事実精度に明確な課題があった**
ため、上記2または3の方向が妥当ではないかと考えられるが、最終判断は
ユーザーに委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_en_direct_ab_01_generate.py`(新規) | B版生成用の独立実験スクリプト。R4のProduction関数を読み取り専用でimportするのみ |
| `er003_output/en_direct_ab_01/A02/raw_article.md`(新規) | B版生成結果本文 |
| `er003_output/en_direct_ab_01/A02/writer_request_metadata.json`(新規) | B版writer呼び出し条件・実測値 |
| `er003_output/en_direct_ab_01/A02/writer_sources.json`(新規) | B版writerが参照した情報源 |
| `er003_output/en_direct_ab_01/A02/fact_qa.json`(新規) | B版独立fact checker結果 |
| `er003_output/en_direct_ab_01/A02/diagnostics.json`(新規) | B版構造・語数診断 |
| `er003_output/en_direct_ab_01/A02/comparison.html`(新規) | A/B比較Artifact原本 |
| `er003_output/en_direct_ab_01/A02/audit/`(新規) | prompt全文・API応答詳細等の監査証跡 |
| [OPEN_ITEMS.md](OPEN_ITEMS.md) | OPEN-35へ夜間保留の理由を追記(G節) |

## 受入条件23項目

| # | 条件 | 結果 |
|---|---|---|
| 1 | A02を対象にしている | PASS |
| 2 | A版は既存Natural English Sourceをそのまま使用している | PASS(B節) |
| 3 | B版は日本語阪神master全文を使用している | PASS(C節) |
| 4 | B版はwriter自身がWeb検索している | PASS(3回、C節) |
| 5 | B版へ事前Factsを渡していない | PASS(C節) |
| 6 | B版のdeveloper messageは英語出力指定へ変更されている | PASS(C節) |
| 7 | user instructionは原則R4の日本語原文を維持している | PASS(C節、instruction本文は一字一句不変) |
| 8 | 英語masterを新規作成していない | PASS(H節) |
| 9 | B版は英語を直接生成している | PASS |
| 10 | Point見出しが2つ存在する | PASS(h3_count=2) |
| 11 | B版独立fact checkerを実行している | PASS(D節) |
| 12 | A/B双方のfact状態を比較できる | PASS(D節) |
| 13 | A/B双方のword countを提示している | PASS(A=418、B=410) |
| 14 | 9観点の比較QAを実施している | PASS(E節) |
| 15 | ユーザー比較用Artifactを作成している | PASS(F節) |
| 16 | B1/A2/TTS/audioは生成していない | PASS(H節) |
| 17 | Production仕様を変更していない | PASS(H節) |
| 18 | OPEN-35をCLOSEしていない | PASS(G節) |
| 19 | OPEN-35の夜間まとめ処理による意図的保留が記録されている | PASS(G節) |
| 20 | 実行時のモデル・API・reasoning effort・Web検索有無を記録している | PASS(C節) |
| 21 | 再試行があった場合は回数・理由を記録している | PASS(再試行0回、C節) |
| 22 | 変更ファイル/新規Artifact一覧を提示している | PASS(上表) |
| 23 | Git操作を行った場合はcommit/push状態を報告している | 本報告の末尾を参照 |
