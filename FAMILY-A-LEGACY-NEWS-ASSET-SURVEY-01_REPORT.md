# FAMILY-A-LEGACY-NEWS-ASSET-SURVEY-01 報告書

管理ID: FAMILY-A-LEGACY-NEWS-ASSET-SURVEY-01(Lane A-3)。
**読み取り専用の事実確認のみ。コード・Prompt・SSOT本体の編集、API呼び出し、
Git操作は一切行っていない。**

対象: Family分類が生まれる前に作られた過去News的記事(阪神/イラン(ホルムズ海峡)/
イギリスSNS門限)から、通常News(Major/Daily News)の実質的ベースを復元できるかの
事実確認。

---

## 0. 対象記事の同定

| 呼称 | 実体 | 分野 | 管理ID系統 |
|---|---|---|---|
| Hanshin | 阪神-広島戦(2026-08-16) | Sports(単発試合結果) | N3-01(`er003_output/n3_01/hanshin/`) |
| Health | 観察研究記事(寿命/健康寿命) | Health | N3-01(`er003_output/n3_01/health/`) |
| Household | 冷蔵庫クリスパー | 生活実用 | N3-01(`er003_output/n3_01/household/`) |
| ADD03 | ホルムズ海峡(イラン情勢) | 国際/安全保障 | P-series、コード内呼称`iran01`(`er003_output/b1_p9a/ADD03/`, `er003_output/b1redesign_audio_01/IRAN01/`等) |
| A02 | 英国SNS門限(16-17歳、深夜0-6時の`digital switch-off period`) | 規制/テック政策 | P-series(`er003_output/b1_p1/A02/`, `er003_output/b1_p9a/A02/`等) |
| A01 | サッカー(参考、News以外だが同系統) | Sports | P-series |

`IRAN01`はコード内の旧呼称であり、実体はADD03(ホルムズ海峡記事)と同一系統
(`er003_v1_iran01_*.py`群がADD03を生成)。`b1redesign_audio_01/IRAN01/`は
そのB1再設計時の中間出力ディレクトリで、最終成果物ではない。

---

## 1〜7. 記事ごとの確認事項

### Hanshin / Health / Household(N3-01系統)

1. **管理ID**: `ER-003-A2-B1-N3-01`(2026-08-17確定)、`ER-003-N3-ROOT-FIX-01`/
   `VERIFY-01`(同日、A2 Core Logic Preservation)。ARTIFACT_REGISTRY.md
   45-68行に状態表あり。
2. **記事構造**: Title / Main Story(part1+part2) / Point One(heading+body) /
   Point Two(heading+body) / In One Line。音声側では
   Preview→Key Phrases→Comment1→Part1→Comment2→Part2→Comment3→
   Point One→Point Two→Comment4→In One Line の11パート構成
   (`er003_output/n3_01/hanshin/b1b/narration/`のファイル一覧で確認)。
   Key Phrase 5件、Comment 4件。B1-B/A2の両レベルとも存在。
   語数(Hanshin B1-B、`length_report.json`): Main Story相当intro 206語+
   Point One 38語+Point Two 35語+In One Line 20語=総299語。
   完成音声尺: Hanshin B1B 274.5秒、Health A2 334.8秒/B1B 313.3秒、
   Household A2 306.3秒/B1B 285.5秒。
3. **Writer/Editor/QA/Audio経路**:
   Writer=`er003_v1_n3_01_articles_generate.py::run_one_pattern()`
   (`COMMON_BLOCK_TEMPLATE`使用)。Support/Key Phrase選定=
   `er003_v1_n3_01_scaffold_generate.py::run_key_phrases()`。TTS=
   `er003_v1_n3_01_tts_generate.py`。Assembly=`er003_v1_n3_01_assemble.py`。
   B1本文生成方式=`B1_B_DIRECT_INSTRUCTION`(Verified Fact Ledgerから直接
   独立生成、B2非経由)。QA=Fact Checker(web検索付き)+Ledger Deviation
   Checker v2+Point Overlap QA(N3-01時点ではPoint-only regenerationは
   まだ存在せず、後日ER-19/20/21で追加・撤回されたため本記事群には無関係)。
4. **現行Production基盤との関係**: **同一コード**。`er003_v1_n3_01_articles_
   generate.py::COMMON_BLOCK_TEMPLATE`は、Pool Pilot(No.9/No.18等、
   `er006_pool_pilot_01_writer.run_writer_for_theme`経由)・Theme 2・
   Discovery/Whyの4層Trial(`er011_open112_a_family_4layer_prompt_trial_05.py`が
   Layer1+2を本ファイルからそのままimport)まで、現在に至るまで唯一の
   Production Writer共通テンプレートとして使われ続けている
   (DECISION_LOG.md 5981行・6316行で確認)。`er003_v1_n3_01_scaffold_
   generate.py::run_key_phrases()`のKey Phrase Redundancy QA retryロジックも
   現行仕様(DECISION_LOG.md 6431行)。つまりHanshin/Health/Householdを
   作った"エンジン"は、現在Family A/Bで使われているエンジンそのもの。
5. **通常Newsとして再利用可能な部分**: (a) Main Story/Point One/Point Two/
   In One Lineという4-slot構造(現行`OPEN-112-NEWS-MODE-DESIGN-08`の
   「A Family Common Skeleton」と完全一致)。(b) Point Balance目標範囲
   (30-60語/許容25-70語、3ジャンルで検証済み)。(c) Spoken-first Number
   Treatment(Importance/Exactness 2軸)。(d) Fact Safety標準
   (単一Ledger→Fact Checker→Ledger Deviation Check)。(e) B1-B Direct
   Generation方式そのもの。(f) Point Notification/semantic heading等の
   音声実装。これらは現行CURRENT_SPEC.mdに`DECIDED`として残っており、
   News記事にもそのまま適用可能。
6. **DESIGN-08との差分**: DESIGN-08の新規部分はLayer 3「News Focus
   Module」(Major/Daily variant、Trend Synthesis variant)であり、
   Hanshin/Health/HouseholdはこのLayer 3が**存在しない時代**の生成物
   (2026-08-17生成、Storytelling First/No Jargon/Evidence-bounded
   Interpretation原則も未実装時期、DECISION_LOG.md 7503行で確認)。
   構造(Layer1+2)は一致するが、News固有の視点付与(なぜ今日ニュースか/
   次に見るべきこと等)を明示的に強制する仕組みは当時なかった。
   DESIGN-08 §11ではHanshin相当のtopic_package(阪神タイガース)を
   Major/Daily Trial候補として名指しで挙げている(read-only確認のみ、
   生成未実施)。
7. **obsolete仕様の混入**: 確認された範囲では無し。B1-B Direct Generation・
   A2 Core Logic Preservationは、まさにこの記事群で検証・採用された
   現行仕様そのもの。ただしStorytelling First等の後発原則は未反映のまま
   (ユーザー決定により遡及修正しないことが確定済み、DECISION_LOG.md
   PM-CLOSEOUT-CONSOLIDATION-07)。

### ADD03(ホルムズ海峡/イラン情勢)

1. **管理ID**: `ER-003-REPRO-02`/`ER-003-REPRO-FINAL`(2026-08-08〜09)。
2. **記事構造**: Hanshin等と同じ11パート構成(Preview/Key Phrases/Comment1-4/
   Full Story Part1-2/Point One-Two/In One Line)。Key Phrase 5件、
   Comment 4件、`assembled/`に複数バージョン(v1〜v4、音量/Key Phrase修正の
   イテレーション)が残る。
3. **Writer/Editor/QA/Audio経路**: Writer=`er003_v1_iran01_articles_
   generate.py`/`er003_v1_iran01_b1_generate.py`/`er003_v1_iran01_a2_
   generate.py`(記事専用の一回性[one-off]スクリプト)。Key Phrase=
   `er003_v1_iran01_a2_kp_retry.py`等。Audio=`er003_v1_iran01_b1_audio_
   generate.py`/`_a2_audio_generate.py`/`_audio_fix.py`。
   **B1本文の生成方式はB1-A(B2から派生)**であり、これは2026-08-16/17に
   B1-B Direct Generationへ置き換えられ**廃止された旧方式**
   (DECISION_LOG.md「B1-B Direct Generationを採用し、B2の別段階生成を
   廃止」エントリ)。
4. **現行Production基盤との関係**: **一部同一・一部置換済み**。Key Phrase
   選定関数(`er003_b1_p2_keywords.py`の`load_prompt_template/build_user_
   message/make_selector_fn`)はA2/B1双方で現在も共有・再利用されている
   (DECISION_LOG.md 6371行・6431行)。しかしADD03専用のWriter/Audio
   scriptそのものは、DECISION_LOG.md 5711行で「P-series・IRAN01・SING01等、
   既にHISTORICAL化済みの完成テーマ向けスクリプト」と明記され、Human
   Review Cost Guard等の新しい安全機構の配線対象からも意図的に除外
   されている(現行Production経路はN3-01/pool_pilot_01系のみを対象)。
5. **通常Newsとして再利用可能な部分**: (a) 音声構造(11パート、Preview
   語言語=日本語のみ、Key Phrase発話順序等)はCURRENT_SPEC.mdに現在も
   `DECIDED`として残る仕様の起源そのもの(ER-003-A2-STRUCT-02〜04、
   ER-003-A2-SPEC-FREEZE-01)。(b) 国際情勢という複数ソース・
   CONTESTED/SINGLE-SOURCE区分を要する題材のため、DESIGN-08 §11は
   「イラン_アメリカ_情勢」のtopic_packageをTrend Synthesis候補として
   名指し(read-onlyのみ、生成未実施)。
6. **DESIGN-08との差分**: Hanshinと同様Layer 3不在の時代の生成物。
   加えてB1生成方式自体が現行B1-B Direct Generationと異なる(旧B1-A方式)。
7. **obsolete仕様の混入**: **あり**。B1本文生成方式がB1-A(B2派生、廃止済み)。
   Writer/Audioスクリプト自体もDECISION_LOG.mdで明示的にHISTORICAL
   (legacy/one-off)と分類済み。構造仕様(音声side)は現行と一致するが、
   本文生成のコードパスはそのまま再利用できない。

### A02(英国SNS門限)

1. **管理ID**: `ER-003-REPRO-01`(2026-08-08)。
2. **記事構造**: ADD03と同じ11パート構成。B1完成音声=`ER-003-REPRO-01`で
   ユーザーが初回通し候補をそのままPASS、User Quality PASS(ARTIFACT_
   REGISTRY.md 39行)。Main Story本文(master_en_natural_source_
   approved.md)は「Today's Late-Night Scrolling Points」という記事固有の
   セクション見出しの下にPoint One/Twoを置く構成で、現行の汎用見出し
   (単純に「Point One」)とは若干異なる装飾が入っている。
3. **Writer/Editor/QA/Audio経路**: ADD03と同系統。Writer=
   `er003_v1_p1b_natural_source_spec.md`方式(Natural English Source→
   CEFR別生成)。B1は同じくB1-A(廃止済み旧方式)。
4. **現行Production基盤との関係**: ADD03と同じく、専用Writer/Audio
   scriptはHISTORICAL。Key Phrase選定関数・音声構造仕様は現行と共有。
5. **通常Newsとして再利用可能な部分**: A02はUK政策/規制という「単一起点
   イベント」の典型例であり、DESIGN-08 §4のMode判定基準(単一起点質問)に
   照らすとMAJOR_DAILY相当の題材。構造・Point Balance原則の起源としての
   価値はADD03と同様。
6. **DESIGN-08との差分**: Hanshin/ADD03と同様Layer 3不在時代の生成物。
7. **obsolete仕様の混入**: ADD03と同様、B1-A方式(廃止済み)。

---

## 8. 結論: PARTIAL

**YES/PARTIAL/NOの判定: PARTIAL**

根拠:

- **構造面(Layer 1+2)は「復元」ではなく「継続」**: Hanshin/Health/
  Householdを生成した`er003_v1_n3_01_articles_generate.py::
  COMMON_BLOCK_TEMPLATE`は、現在もFamily A/Bの唯一のProduction Writer
  共通テンプレートとして使われ続けている。DESIGN-08の「A Family Common
  Skeleton」(Main Story/Point One/Point Two/In One Line)はこのファイル
  由来であり、実装として既に存在・稼働中。この部分はゼロから設計する
  必要がない。
- **News固有の視点付与層(Layer 3)は存在しない**: Major/Daily・Trend
  Synthesisという2モード区分、Mode判定基準、Counter-signal/limitation
  ルール等は、Hanshin/ADD03/A02のいずれの生成時点にも存在しなかった
  (DESIGN-08は今回初めて設計、実装・Trialは未実施)。従来のNews記事は
  「Newsとして特別扱いされたPromptブロック」を経ずに、汎用Writer
  templateだけで書かれていた。
- **B1本文生成コードパスに新旧混在**: N3-01(Hanshin等)はB1-B Direct
  Generation(現行仕様)、P-series(ADD03/A02)はB1-A(B2派生、廃止済み)。
  ADD03/A02のWriter/Audio専用scriptはDECISION_LOG.mdで明示的に
  HISTORICAL/legacy分類済みであり、直接呼び出しの対象外。
- 以上より、「過去News資産から通常Newsの実質的ベースを復元できるか」は、
  **構造・原則・QAの大部分については復元不要(既に現役)だが、News固有の
  Focus Module層は新規設計が必要**という意味でPARTIAL。

---

## 9. 提案(実行しない、報告のみ)

**ゼロから設計すべきか、既存News資産を正式化・整理すべきか**という問いに
対しては、**既存資産の正式化(部分的)を推奨**。ゼロからの再設計は、
既に現役のLayer1+2エンジン・QA機構を再発明することになり非効率。

正式化する場合の最小作業案(実行しない、列挙のみ):

1. **Reference implementation候補**: Hanshin(N3-01)をMajor/Daily News構造の
   reference、ADD03またはA02のTopic Package(`topic_package_イラン_
   アメリカ_情勢_*.py`)をTrend Synthesis構造検討のreferenceとする
   (DESIGN-08 §11で既に候補提示済み)。ただしADD03/A02自体の完成
   article.md/音声は本文生成コードパスがB1-A(廃止済み)のため、
   reference本文としてそのまま採用せず、あくまで「音声構造・題材選定の
   参考」に限定する。
2. **CURRENT_SPECへ書き起こす候補**: (a) DESIGN-08のLayer 3設計
   (Major/Daily・Trend Synthesisの2 variant、Mode判定基準、Point Role
   固定化しない方針)を、Trial実施・ユーザー承認を経た上でCURRENT_SPECへ
   追加。(b) 「N3-01 = A Family Common Skeletonの実装起源」という事実
   関係の記録漏れがあれば追記(現状DECISION_LOG.md 6316行に記述あり、
   CURRENT_SPEC本体への明記有無は未確認、追加確認要)。
3. **除外すべきobsolete部分**: (a) ADD03/A02のB1本文生成方式(B1-A、
   B2派生)は再利用しない。(b) P-series専用Writer/Audio script
   (`er003_v1_iran01_*.py`等)は「参考にはするが直接呼び出さない」
   既存方針(DECISION_LOG.md 5711行)を維持。(c) Storytelling First/
   No Jargon/Evidence-bounded Interpretation等の後発原則は、遡及適用
   しないという既存ユーザー決定を維持したまま、新規News生成時のみ
   現行COMMON_BLOCK_TEMPLATE経由で自動適用される(コード変更不要)。
4. **Gap(DESIGN-08 §10で既指摘、再確認のみ)**: Diagnostic Full Retry・
   Ledger Deviation Checkerの語彙にNews/Trend固有の失敗パターン
   (evidence listing・trend overclaim・weak counter-signal等)が存在
   しない。News系Production化前に拡張要否をユーザー判断する必要がある
   (既存Gap、今回新たな指摘ではない)。

以上はいずれも提案であり、本タスクでは実装・Trial・SSOT編集を一切
行っていない。
