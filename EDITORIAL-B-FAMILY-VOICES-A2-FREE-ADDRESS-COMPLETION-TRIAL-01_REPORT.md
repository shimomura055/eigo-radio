# EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-01_REPORT

管理ID: EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-01(Lane B)
実行: sonnet-worker(read-onlyでStep 1のみ実施、Step 2以降は未実施)

## 結論(先出し)

Step 1の事実確認の結果、**A2固有の新規判断が複数必要**と判明したため、
Step 2(A2記事生成)・Step 3(音声)には進まず、ここで
`USER_DECISION_REQUIRED`としてSTOPする。API呼び出し・費用発生はゼロ
(¥0)。既存ファイルの変更・SSOT編集・Git操作は一切行っていない。

## 1. A2版が未完成であることの確認

- `er012_output/editorial_b_family_production_phase1_02/`(Phase 1、
  ユーザー承認済みB1B完成版)配下は `audit/` `b1b/` `player.html`
  `voice_b_attempt_review.html` のみで、`a2/`ディレクトリは存在しない
  (`find er012_output -iname "*a2*" -path "*free_address*"` 0件、
  `b1b/article.md`はB1本文のみ)。
- `er012_output`配下を横断grepしても、このトピック(One Office, Two
  Ideas of a Place to Work / フリーアドレス vs 固定席)のA2版成果物は
  0件。→ A2版はまだ着手されていないことを確認。

## 2. 既存B1/B-Family仕様(Phase 1)の要点

- `er012_b_family_editorial_type_registry_01.py`(2026-09-08
  `APPROVED_FOR_PRODUCTION`確定4項目を集約):
  - `VOICE_ASSIGNMENT = {"voice_a": "Algieba", "voice_b": "Erinome",
    "narrator": "Aoede"}`(fallback: Schedar/Sulafat)
  - 物理構造: `SECTION_LABELS = ("hook", "voice_a", "voice_b",
    "tension", "closing")` の5区切り
  - Tension slot見出し: "Where the Difference Comes From"
  - Key Phrase位置: `after_preview`(現状維持)
  - Voices Comment Contract 1〜4(FINALIZE-11確定版、全文を
    `registry`へ転記済み。Comment役割定義は日本語で書かれた
    LLM instructionだが、`er012_b_family_production_runner_01.py`
    は`voice01.generate_charon_english()`でこれを呼び出しており、
    **実際に発話されるComment本文はCharon(英語)**であることを
    コード上確認(現行B1日本語使用範囲ルール「Key Phraseの日本語訳
    のみ日本語」と整合)。
- `er012_b_family_production_runner_01.py`はB1B専用にhard-codeされて
  おり、level引数・A2分岐は一切存在しない(`ARTICLE_PATH`/`OUT_B1_DIR`
  等が固定)。
- `er012_b_family_voices_production_01.py::split_five_voice_sections()`
  等も5区切り構造専用の固定パーサーで、levelパラメータなし。

## 3. 既存A2 Production仕様の要点(CURRENT_SPEC.md L197-347)

- 全体構造は「Preview→Key Phrases→Comment1→Full Story Part1→Comment2
  →Full Story Part2→Comment3→Point One→Point Two→Comment4→In One Line」
  の11パート固定(`DECIDED`、ER-003-A2-STRUCT-02〜04)。B-Family の
  Hook/Voice A/Voice B/Tension/Closingとは物理構造そのものが異なる。
- voice: 「Aoede(A2、および旧P-series B1)。**現行B1はCharon**」
  (CURRENT_SPEC.md L413)。A2はEnglish/Japaneseとも**単一Aoede声**で
  発話する設計(Point semantic heading行: 「A2も見出し・本文とも
  既存の単一Aoede構成を維持する」)。
- Comment言語: 「日本語のComment/解説文(**A2 Comment1〜4**・Preview・
  japanese_title、B1 Support等)では、制作内部ラベルを使わない」
  (CURRENT_SPEC.md L329)= **A2のComment 1〜4は日本語**が現行仕様。
  実データでも確認: `er011_output/open112_trend_theme2_b_final_
  audio_rerun_04/a2/a2_support_texts.json`のcomment_1〜4は日本語
  テキスト(Shift-JISベースの文字化け無しでコードから復号し日本語
  であることを確認)。
- 生成元: 「Verified Fact Ledgerから直接1回のWriter呼び出しで
  A2本文を生成する(B1/B2本文を入力にしない)」(CURRENT_SPEC.md
  L234、B1本文生成方式節と対称)。**A2本文はB1本文からの変換・
  簡略化ではなく独立生成が既定原則**。

## 4. 再利用可否の表

| 項目 | 既存A2仕様から自明に流用可か | 理由 |
|---|---|---|
| A2語彙・文長方針(11語以下目安等) | 可 | 定性的方針でジャンル非依存、Writer promptへそのまま適用可能 |
| Fact Safety 3段QA(Fact Checker→Ledger Deviation) | 可 | Cross-level共通仕様、B-Family runnerも`vfl01.run_deviation_check`を既に使用 |
| Key Phrase選定方式(Strategy L等) | 可 | Cross-level共通仕様、B-Family Phase 1も同方式のデータを再利用中 |
| Naturalness QA(6観点) | 可(方針のみ、大規模自動化は元々未実装) | 既存A2/B1とも同水準 |
| Pause定数・SFX規則等 | 可 | Cross-level共通仕様として既にB-Family runnerが踏襲 |
| **全体構造(11パート）→B-Family(5区切り+Comment Contract)への対応** | **不可・要判断** | 物理構造が別物。A2 Writerは11パート専用に設計されており、B-Family固有構造への適用方法(役割対応の定義)が未定義 |
| **Voice A/B本文のA2化方針** | **不可・要判断** | 「B1本文をA2へ翻案(簡略化リライト)」か「Ledgerから独立A2生成」かが未決定。標準A2原則は独立生成だが、Voice A/Voice Bは一人称の主観的語りであり、既存の「Verified Fact LedgerからB1/A2をそれぞれ独立生成」という報道記事向けモデルがそのまま当てはまるか自体が未検証(B-Family用A2 Writerが存在しない) |
| **A2でのvoice割当(Comment/Voice A/B/Narrator)** | **不可・要判断** | 標準A2は英日とも単一Aoede声。B-Familyは指示により2V(Algieba/Erinome)+Narrator(Aoede)を維持する必要があり、Comment(現行B1はCharon英語、標準A2は日本語)をどの声・どの言語で読ませるか(Aoede単一化して2V破棄/2V維持でCharon英語のままA2化/2V維持しつつComment用に別途Aoede日本語を追加、等)が未決定 |
| **A2でのTension/Closingの扱い** | **不可・要判断** | 標準A2 11パートにTension/Closingという概念自体が存在しない。役割対応・語数目安が未定義 |
| **A2でのVoice本文長** | **不可・要判断** | 標準A2は「総語数を削らない」方針だが、これはNews Full Story/Points向けの原則。Voice A/Voice Bの一人称語り本文にそのまま適用してよいか(Cognitive Load Reductionの再構成方針とVoiceの語り口調の両立)は未検証 |
| **Comment Contract(FINALIZE-11)のA2適用** | **不可・要判断** | FINALIZE-11確定版はB1(Charon英語)向けに検証済み。標準A2は日本語Comment。同じ役割定義をどちらの言語・声で出力させるか、既存確定Contract本文(日本語instruction)をそのまま流用してよいかは未検証 |

追加判断が必要な項目が6件(全体構造対応/Voice本文化方針/voice割当/
Tension・Closing扱い/Voice本文長/Comment Contract適用言語)ある
ため、Step 2以降(記事生成・音声生成)は実施せず、ここでSTOPする。

## 5. USER_DECISION_REQUIRED候補(要約)

1. B-Family(5区切り+Comment Contract)構造を、A2の「11パート固定
   構造」へどう対応させるか(11パートへ組み替えるのか、5区切り構造
   のままA2言語・声規約だけ適用する新Editorial Type専用A2仕様を
   新設するのか)。
2. Voice A/Voice B本文のA2版は「B1本文の翻案(リライト)」か
   「Ledgerからの独立A2生成」か。
3. B-Family A2でComment 1〜4はどの声・どの言語で読ませるか
   (2V[Algieba/Erinome]+Narrator[Aoede]は維持する前提で、Comment
   はCharon英語のまま/Aoede日本語化/その他)。
4. Tension slot・ClosingのA2版での役割・分量方針。
5. Voice A/Voice B本文のA2版の目標語数・文長。
6. Comment Contract(FINALIZE-11)確定文言をA2へそのまま使うか、
   A2専用の役割文言を新設するか。

## 6. 未実施事項

Step 2(A2記事生成)・Step 3(音声生成・Assembly)・Step 4(Status整理)
は、上記USER_DECISION_REQUIREDの解消待ちのため未実施。コード変更・
ファイル生成・API呼び出しは一切なし。
