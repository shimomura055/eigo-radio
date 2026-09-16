# RESULT_PACKET: PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01(Phase A)

0. **T-0**: FAIL(既知パターン、Preflightと同型。コードフェンス誤検知+「事前指定Grep一覧」を「事前指定Read/Grep一覧」という統合見出しにしたため単独keyword不一致。必須項目6/8 OK・固定ブロックE-1/D-1/G-1/F-1/T-1 OK)。ブロッキングではないため継続。check結果: `docs/pm/delegation_log/PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01.md_check.json`。

## 1. Family別A2生成方式の18項目マトリクス

凡例: ○=Production正式pathで実使用/△=定義のみ・Trial経由・部分的/×=なし。

| # | 項目 | News(通常) | Discovery/Why | Trend Synthesis | Family C(Future Story) | B-Family(Voices) |
|---|---|---|---|---|---|---|
| 1 | Researchの作り方 | ○ `er002_ja_web_research_r3.py`+`vfl01.build_researcher_prompt`(`run_pipeline.py`) | ○ 同一vfl01パターン(`run_discovery_a2.py` L74-76、r3+vfl01) | ○ 同一vfl01パターン(`run_trend_a2.py` L54-58) | ×(Fiction、Research/web_search不使用。`article_config.json`起点、本文は本パイプライン外で事前作成) | △(B1 write_new_theme経路は同一vfl01/r3パターンで実使用済み。A2新規topic用としては未接続) |
| 2 | Verified Fact Ledgerの位置づけ | ○ `verified_fact_ledger.txt`、A2/B1共有(RESEARCH_DIR配下1つ) | ○ 同型 | ○ 同型(News driverからの流用と明記、run_trend_a2.py L8) | 該当なし | △(B1側は共有Ledger機構を実使用、A2固有の入口としては未接続。Preflight項目2) |
| 3 | A2 WriterがLedgerから直接書くか | ○ `generate_article_stage("a2", verified_ledger_text)`→`prod_gen.build_common_block()`+`A2_KAI1_INSTRUCTION` | ○ `s2prod`(Discovery Focus staged production)がLedgerから直接生成 | ○ `writer_mod.run_writer_for_theme(..., editorial_mode="trend_synthesis")`がLedgerから直接生成 | 該当なし(A2本文はarticle_config.json内の別ファイル、本パイプラインでは生成しない) | ×(`main_a2()`にWriter stage無し、L1625-1672確認[Preflight項目3]。`run_writer_adapt()`はTrial専用呼出のみ) |
| 4 | B1完成記事からA2へadaptするか | × | × | × | 該当なし(A2/B1は`article_config.json`内で別々の`article_path`を持ち、互いに翻案する関係ではない。ただしどちらも本パイプライン外で事前作成されるテキストであり、その作成方法自体は本監査の対象コード外) | △(`run_writer_adapt(b1_article_text)`が存在しB1記事のみを入力とする翻案設計。ただしProduction runnerからは未呼出、Trial呼出[`er012_editorial_b_voices_a2_trial02_writer.py`]のみ) |
| 5 | A2/B1でResearch/Ledgerを共有するか | ○ 同一Ledger(1ファイル)をlevel引数だけ変えて再利用 | ○ 同型 | ○ 同型 | 該当なし | △(B1は独自Ledgerを使用済み。A2固有の共有経路は未接続) |
| 6 | Fact Checker | ○ `prod_gen.run_one_pattern()`内蔵、A2/B1双方level非依存で稼働(Cross-level仕様「Fact Safety(共通)」節) | ○ 同一機構 | ○ 同一機構(mode非依存、CURRENT_SPEC「retry/fallback整合」行) | ×(Fiction、Fact Checker非適用) | △(`run_fact_check_a2()`ラッパーは存在しlevel非依存設計だが`main_a2()`から未呼出[Preflight項目4]) |
| 7 | Ledger Deviation | ○ `er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`共通 | ○ 同一機構 | ○ 同一機構 | ×(該当なし) | △(`run_ledger_deviation()`定義済みだが未呼出) |
| 8 | retry/Local Rewrite | ○ Diagnostic Full Retry、mode/level非依存で機能 | ○ 同型 | ○ 同型(prompt再構築しないためmode自動保持) | △(regeneration機構[`purge_segment_outputs`]はTTS再生成用で記事本文retryではない) | ×(呼出経路自体が無いため発火しない) |
| 9 | Family固有QA(Leakage等) | △ Point Overlap QA(lexical_overlap_ratio、A-family共通の重複QA、Family固有ではなくFamily A系列共通) | △ 同上+Layer3 Focus Module(Trial止まり、Production不採用) | △ 同上+Trend Gate 6条件(Trend固有、手動判定) | ○ Story TTS segmentation原則(仕様A、`plan_story_segments()`)+A2 Comment理解ガイド型Contract(仕様B、Family C A2限定) | △(Analytical Leakage Check`run_analytical_leakage_check()`定義済み[B-Family固有QA]だが`main_a2()`未呼出) |
| 10 | Scaffold/Comment | ○ `sc.run_a2_scaffold`/`run_b1_scaffold`(A-family共有module) | ○ 同型 | ○ 同型 | ○ `generate_family_c_a2_comment()`(Family C A2固有Contract、B1は既存B1 Support経路を別途使用) | △(`run_scaffold_a2()`定義済みだが`main_a2()`からはTrialのみ呼出) |
| 11 | Key Phrase | ○ Strategy L+Canonicalization、A2は自身の本文から選定(B1由来の流用なし、CURRENT_SPEC「B1 Key Phrase」節636行と対称) | ○ 同型 | ○ 同型(B1B Key Phrase 5差し替え実績あり) | 該当なし(素材はreuse_from/共有資産のみ、from-scratch生成はスコープ外) | △(`reuse_key_phrases_a2()`はB1 Key Phrase英語ComponentをCOPYする専用関数、新規topicでは動かない[Preflight項目4]) |
| 12 | 日本語タイトル | △ `JAPANESE_TITLES`固定辞書、新規テーマは`tts_gen.JAPANESE_TITLES.update()`で人手登録(CURRENT_SPEC「News Editorial Mode」節、A-Family共通gapとして明記) | △ 同型 | △ 同型 | ○(`article_config.json`の`topic_title`/日本語title textとして記事ごとに供給、固定辞書ではない) | △(`generate_japanese_title()`定義済みの動的関数はあるが、player生成部は`registry.get_editorial_type_a2()["japanese_titles"][A2_THEME_KEY]`という固定辞書引きのみ使用) |
| 13 | TTS | ○ `tts_gen`(共有module) | ○ 同型 | ○ 同型 | ○ `tts_call_for_voice()`(共有Production関数群へ分岐) | △(`run_tts_a2`は`main_a2()`から呼ばれるが前段article/parts自体が固定topic前提) |
| 14 | Assembly | ○ `asm`(`er003_v1_n3_01_assemble.py`、全Family共有) | ○ 同型 | ○ 同型 | ○ 同一module(`assemble_mod`としてimport) | △(`run_assembly_a2`呼出はあるが固定topic前提) |
| 15 | Audio Validation Gate | ○ level="A2"/"B1"共有dict | ○ 同型 | ○ 同型 | ○(共有Gate、Family C固有levelキー不要) | ○(機構自体はlevel非依存、`"B_FAMILY_A2"`キー登録済み。新規topicでも機構自体は使える) |
| 16 | player | ○ 共有player生成関数 | ○ 同型 | ○ 同型 | ○ `write_evidence_player()`(共有機構+Family C用evidence player) | △(`build_player_html_a2`は日本語タイトル固定辞書に依存) |
| 17 | 正式Production entrypoint | △(トピックごとの`run_pipeline.py`/`run_news_a2.py`等、コピー派生スクリプト。統一CLIランナーは無い) | △ 同型(`run_discovery_a2.py`等) | △ 同型(`run_trend_a2.py`等) | ○ `er013_family_c_production_runner_01.py --level a2\|b1`(トピック非依存の統一CLIランナー) | △(`er012_b_family_production_runner_01.py`は統一CLIだが`main_a2()`は固定topic専用、`main_b1_2v()`のみ新規topic対応) |
| 18 | Trial/DEV依存の有無 | ○ 依存なし(driver自体がProduction関数のみimport、per-topic driverはProduction-set扱い) | ○ 同型 | ○ 同型 | ○ 依存なし(Trial script[`er013_family_c_episode_trial_1[012]_*.py`]を一切import・参照しない、CURRENT_SPEC明記) | ×(直近A2 runtime evidenceはTrial driver`er012_b_voices_3v_a2_user_test_01.py`経由。Personalized NewsのA2は未着手) |

**要約**: News/Discovery/Trend(A-Family系列)は、Research/Ledger/Fact Checker/Ledger Deviation/retry/Scaffold/Key Phrase/TTS/Assembly/Gate/playerの全10項目以上でほぼ完全に共通のProduction primitiveを共有し、A2/B1をLedgerから独立生成する統一パターンを持つ(entrypointだけがトピックごとのコピー派生scriptで、真の意味での統一CLIランナーは無い)。Family CはResearch/Ledgerを使わない(Fiction)特殊系列だが、Assembly/Gate/TTS等の下流共有primitiveは完全に共通利用しており、統一CLIランナー(`--level`分岐)を持つ点でNews系列より進んでいる。B-Family(Voices)のA2は、Writer本体(項目3)・Fact Checker(6)・Ledger Deviation(7)・Family固有QA(9)・Scaffold(10)・Key Phrase(11)・Key Phrase正式接続・Trial依存(18)の計7項目で×または最も弱い△であり、他Familyと比べ明確にA2 E2E経路が未成熟(Preflightの結論と整合)。

## 2. eigo-radioとして共通化できる部分

- Research→Verified Fact Ledger作成(`er002_ja_web_research_r3.py`+`er003_v1_en_direct_vfl_01_generate.py`のvfl01パターン)は、事実ベースFamily(News/Discovery/Trend、および将来のPersonalized News)に共通の正式primitiveとして既に確立している。
- 「Ledger(level非依存で1つ)→level別独立Writer」という入力contractは、A-Family全体で共通設計。この対称性(A2/B1が同格でLedgerから独立生成)自体をFamily非依存の一般原則として扱ってよい。
- Fact Checker/Ledger Deviation Checkerは、生成済みテキストのみを操作しprompt再構築を行わないためlevel/mode/Family非依存で機能する共通QA層(News Editorial Mode節ですでに明記済みの設計原則)。B-FamilyのA2 wrapper(`run_fact_check_a2`)も同じ思想でlevel非依存設計になっている。
- retry/Local Rewrite(Diagnostic Full Retry)は生成済みテキストへの追加diagnostic sectionのみで、mode/Family非依存の共通機構。
- TTS/ASR安全機構(`er003_audio_tts_asr_safety.py`、Human Review Lock`er011_human_review_lock_01.py`、Pronunciation Ledger)・Assembly(`er003_v1_n3_01_assemble.py`)・Audio Validation Gate(level-keyed dict、拡張可能)・player生成は、News/Discovery/Trend/Family C/B-Familyの全てで実際に共有・再利用されている最も成熟した共通primitive。
- Key Phrase選定機構(Strategy L+Canonicalization)自体は共通。ただし「選定元テキスト」はlevelごとの自分自身の本文であるべき(B1 Key Phrase節がA2からの流用を否定している対称原則)。
- 日本語タイトル供給は、「英語タイトルの直訳を人手作成し実行時に登録する」という運用手順自体はFamily非依存で共通の正式initial path(News Editorial Mode節・B-Family両方で同一パターン)。ただし現在の実装は両Familyとも固定辞書(`JAPANESE_TITLES`/`registry`辞書)への手動追記という実装詳細に依存しており、これは共通化・一般化(呼び出し時にtopic固有の日本語タイトル文字列を引数/configとして渡す方式へ)すべき実装上のgapである(Family C の`article_config.json`供給方式が既にこの一般化形に近い)。

## 3. Family固有で残す部分

- Editorial構造(11パート[News/Discovery/Trend] vs 5区切りHook/Voice A/Voice B/Tension/Closing[B-Family] vs Story-segment構造[Family C])。
- Voice/persona構成(B-Family複数Voice、Family C narrator+character voice)とその一人称Writer原則。
- Comment/Scaffold**役割定義**(C1〜C4等)は起源が共通でも、**実際のprompt文言**はFamily固有(Family C「理解ガイド型」Contract、B-Family Comment Contract、標準A2 Comment Contract)。
- Family固有QA: Analytical Leakage Check(B-Family、多人称一人称Voiceの分析的漏洩検知)、Trend Gate 6条件・Editorial Type Routing 2軸判定(A-Family News系列)、Story TTS segmentation原則(Family C、Fiction本文のsegment分割)。
- Fact Safety variant: B-Family 3V Fact Safety保守版ゲート(一人称Voice特有のcertainty/causality判定)は他Familyには存在しない・必要ない。
- Story origin: Family Cのみ Research/Ledgerを使わない(Fiction、事前作成テキストが前提)。

## 4. B1→A2翻案が共通方式か否か(結論+根拠)

**結論: 共通方式ではない。**

根拠: News/Discovery/Trend(3系列、最も成熟しruntime evidence件数も最多)は全てLedger→A2 Writer直接生成であり、B1完成記事への依存が構造的に存在しない(A2生成コード`generate_article_stage("a2", verified_ledger_text)`はB1記事を一切引数に取らない)。Family Cもarticle_config.json内でA2/B1が別々の`article_path`を持ち、互いに翻案する構造ではない。B1→A2翻案(`run_writer_adapt(b1_article_text)`)が存在するのはB-Family(Voices)のみであり、しかもProduction runner(`main_a2()`)からは一度も呼び出されていないTrial専用関数(呼出元は`er012_editorial_b_voices_a2_trial02_writer.py`のみ)。よって「A2はB1完成記事から翻案する」は、eigo-radio全体の共通設計ではなく、B-Family Voicesの中でも未配線のTrial的な一手法に過ぎない。

## 5. 提案するA2 E2E設計(Phase 3)

**優先順位に沿った設計案(実装はPhase Bで別途委任、本委任では未実装)**:

1. **既存共通primitiveの再利用箇所**: Research/Ledger(B1 write_new_theme経路が既に使用中のLedgerをlevel非依存のまま再利用、Personalized Newsは新規Research不要)/Fact Checker(`run_fact_check_a2`)/Ledger Deviation Checker(`run_ledger_deviation`)/Analytical Leakage Check(`run_analytical_leakage_check`)/TTS・ASR安全機構/Assembly/Audio Validation Gate(`B_FAMILY_A2`キー既存)/player/Human Review Lock — これらは全てB-Family A2向けに**既に level非依存で実装済み**であり、コード変更なしで`main_a2()`系の新規stageから呼び出すだけで再利用できる。
2. **共通化する入口・contract(新設が必要な部分)**:
   - 日本語タイトル: 固定辞書引き(`A2_THEME_KEY`)をやめ、`article_config.json`方式(Family C)に倣い、記事ごとに人手作成した直訳文字列をrunner呼び出し時のconfig/引数として渡す方式へ一般化する(Family非依存の共通contract候補)。
   - Key Phrase: `reuse_key_phrases_a2()`(B1 KP dirからのcopy専用)をやめ、A-Family標準と同じ「A2自身の確定本文からStrategy L+Canonicalizationで選定する」経路へ一般化する。
3. **Family固有moduleに残すもの**: B-Family A2固有のVoice/persona Writer instruction(新設が必要、後述)、Comment Contract文言(既存`registry.COMMENT_ROLES`のB-Family版は流用可)、Analytical Leakage Check・3V Fact Safetyゲート(既存のまま)。
4. **除去する固定依存**: `A2_SOURCE_DIR`固定パス、`reuse_approved_a2_assets()`のsha256突合による単一トピック拒否ロジック(新規topic用の入口では使わない。既存free_addressトピックの音声化専用パスとしては維持してよい)。
5. **Personalized Newsへの適用手順**: 既存B1(2V)Ledgerをそのまま再利用(Research再実行なし)→新設するB-Family A2 Writer(Ledger直接、後述)で新規A2記事生成→Fact Checker→Ledger Deviation Checker→Analytical Leakage Check(既存関数、必要ならretry)→Comment Contract→Key Phrase(A2自身の本文から選定)→日本語タイトル(人手直訳、config渡し)→TTS→Assembly→Audio Validation Gate→Human Review Lock→player。
6. **Production Wiring Checklist充足計画**: 新規topic A2正式初回経路=新設Writer stage/retry・fallback=既存Diagnostic Full Retry相当の適用/Fact Checker・Ledger Deviation=既存wrapper呼出/Family固有QA=Analytical Leakage Check呼出/Comment・Scaffold=既存Contract呼出/Key Phrase=A2自身の本文から再選定/日本語タイトル=config供給/TTS以降=既存共有機構そのまま/runtime evidence=Personalized Newsで新規取得/regression=下記/CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS整合=Phase B実装後に反映/Production Wiring Checklist各項目はPhase B完了時に個別チェックする。
7. **regression対象**: `er012_b_family_voices_writer_generic_01_test_01.py`、`er012_b_family_variable_voice_count_test_01.py`、`er013_family_c_production_test_01.py`(Family C側は変更しないため無影響確認用)、既存B-Family全テスト(`er012*_test_*.py`)、project-wide regression実行。
8. **想定コスト**: ユーザー正式決定によりコスト最小化は優先事項ではないが、目安としてPersonalized News Ledger再利用によりResearch費用¥0、Writer/QA/TTS/Assembly実測は既存2V B1事例(¥140.39)と同程度〜やや高い水準を想定(Family固有QA[Leakage]retryの発火有無に依存)。

## 6. 実装対象ファイル・Production entrypoint(設計上の予定、Phase B用)

- `er012_b_family_voices_writer_generic_01.py`: B-Family A2 Writer instruction新設(CEFR-A2簡略化ルールを一人称Voice物語へ適用する新規Prompt、既存A2_KAI1_INSTRUCTION[News]・B1_B_DIRECT_INSTRUCTION[B1]とは別に新設する必要がある)。
- `er012_b_family_production_runner_01.py`: 新規`main_a2_2v()`(仮称、`main_b1_2v()`の`write_new_theme`stageと対称構造)追加。既存`main_a2()`(free_address専用)は無変更のまま維持。
- `er012_b_family_voices_a2_production_01.py`: `reuse_key_phrases_a2()`をB1 KP dir依存から「A2自身の本文から選定」へ変更する新関数、`generate_japanese_title()`をconfig引数経由で呼び出す配線変更。
- `er012_b_family_editorial_type_registry_01.py`: 日本語タイトルの固定辞書引きをやめconfig供給へ変更する場合の影響箇所。

## 7. Personalized Newsへの適用計画

- **Ledger再利用**: 既存B1(2V)成果物のResearch/Ledger(`er014_output/four_type_observation_01/voices/`または`run2_clean/`のLedger)をそのまま再利用し、A2用の新規Research実行はしない(level非依存で正式再利用可能という結論に基づく)。
- **Leakage QA適用**: 既存B1側の残存Analytical Leakage flag(voice_b/tension、3attempt上限到達後も残存)を、A2側へ無条件に継承・許容しない。A2は新設Writerで独立生成するテキストであるため、A2生成後に既存`run_analytical_leakage_check()`を独立に実行し、その結果(0件ならそのまま採用、残存flagが出た場合は既存corrective retry機構[最大3attempt]を適用したうえで、なお残る場合はB1と同様にUSER_DECISION_REQUIRED候補として記録する、既存B1/3V仕様と同型の扱い)に従う。

## 8. 実装可否Gate判定

3条件(そのまま実装可の要件)を個別判定:

- (a) 既に承認済みの共通方式が明確か: **×**。「Ledger→A2 Writer直接生成」という**アーキテクチャパターン**はA-Family系列で共通方式として明確だが、それをB-Family Voices(一人称Voice物語という全く異なるEditorial構造)へ適用するための**具体的なCEFR-A2 Writer Prompt**は、既存承認済みAPPROVED_FOR_PRODUCTION仕様として存在しない(既存の唯一のB-Family A2 runtime evidence[free_addressトピック]は、承認済みB1記事の翻案結果であり、Ledgerから直接書かれたA2 Voice物語の前例がない)。
- (b) 今回はその未配線部分を接続するだけか: **×**。単純な配線接続ではなく、新しいPrompt(B-Family A2 Voice Writer instruction)の新規作成を要する。
- (c) 新しい記事品質原則や生成方式の採用判断を必要としないか: **×**。必要とする(下記STOP該当理由参照)。

**→ 3条件中0/3で「そのまま実装可」の要件を満たさない。STOP(設計案提示)に該当する。**

**STOP該当理由(該当する条件)**:
- 「新しいPrompt原則が必要」: B-Family A2 Voice物語のCEFR-A2簡略化Writer instructionは前例が無く新規作成が必要。
- 「既存承認済み仕様を変更する必要」: CURRENT_SPEC.md 668行のKey Phrase仕様(「選定はB1 Phase 1と同一」)は、A2がB1と語彙を共有する[翻案由来の]前提に立っており、A2がLedgerから独立生成される場合はこの前提が崩れるため、既存APPROVED_FOR_PRODUCTION仕様の変更(Key Phrase選定元をB1同一からA2自身の本文へ変更)を伴う。
- 「Family共通仕様を新設する必要」: 日本語タイトル供給方式の固定辞書→config供給への一般化は、News/B-Family双方に影響する共通仕様変更に相当する。

## 9. Dangling Reference Check

- 共通primitive(Fact Checker/Ledger Deviation/TTS・ASR安全機構/Assembly/Gate/player/Human Review Lock)は、いずれも正式Productionコード内(`er003_v1_n3_01_assemble.py`等の共有module)に実在し、複数Family(News/Discovery/Trend/Family C/B-Family B1)の初回pathから実際に参照されている(retry/fallbackだけに孤立した定義ではない)。
- `run_writer_adapt()`(B-Family A2翻案)は、Production初回pathからは参照されておらず、Trial driver(`er012_editorial_b_voices_a2_trial02_writer.py`)からのみ参照されている。Production側がこのTrial定義を暗黙に参照している箇所は無い(Preflight項目9で確認済み、本委任で再確認)。
- `generate_japanese_title()`(動的関数)はB-Family A2 module内に実在するが、Production player生成部からは呼び出されておらず(固定辞書引きのみ使用)、宙に浮いた未接続関数(dangling)である。Phase Bでの配線対象。
- `reuse_key_phrases_a2()`はB1 KP dirへの依存を前提とした専用関数であり、新規topic用の一般的なKey Phrase選定経路としては機能しない(構造的に単一トピック[free_address]専用)。

## 10. SSOT更新結果

- `docs/pm/PM_GOVERNANCE.md`: 18節「Family横断共通化原則」新設(旧17節の直後、変更履歴の直前)。
- `docs/pm/PM_BRIEF.md`: 「実装方針の優先順位(2026-09-17更新)」節新設(「委任文標準(D-2)」節の直前)。
- `DECISION_LOG.md`: `PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01`エントリ新設(「参照元」節の直前、索引にも追加)。
- `OPEN_ITEMS.md`: 変更なし(A2 E2E gapはOpen Item化しない、委任文の指示どおり)。
- `CURRENT_SPEC.md`: 変更なし(設計案がPhase Bで承認・実装された後に反映する方針のとおり)。

## 11. Git commit/push

コミット後に追記(下記参照)。

## 12. 到達Status

**`USER_DECISION_REQUIRED`**(実装可否Gate判定=STOP、3条件中0/3)。

## 13. 未決事項・ユーザーに必要な判断

(1) **B-Family A2の生成方式選択**: 横断監査の結果、eigo-radio共通設計は「Ledger→A2 Writer直接生成」だが、これをPersonalized News(B-Family Voices)へ適用するには新しいCEFR-A2 Voice Writer Promptの新規作成が必要になる。選択肢:
   - (a) **共通パターンに合わせる(Ledger直接、推奨)**: 他Familyとの共通性・保守性を最優先するユーザー原則に最も整合する。ただし新規Prompt設計・検証Trialが必要(工数増、既存B1→A2翻案より実装量が多い)。
   - (b) B1→A2翻案を今回に限り採用する: 実装量は少ないが、ユーザーは既に前回この案を「実装量が少ないという理由だけでは採用しない」と明確に却下しており、横断監査の結果(共通方式ではない)を踏まえるとさらに採用根拠が弱まった。
   - (c) 両方を評価するTrialを先に実施してから判断する: 新規Prompt(a)の小規模Trialと、既存翻案(b)の実記事化のどちらが記事品質・作業量の面で妥当か、Personalized News以外の別トピックで比較してから決める。
   推奨: (a)。ただしユーザー原則「品質・Production整合・共通性優先、コスト制約は理由にしない」との整合性が最も高い一方、新規Prompt設計自体の内容(どこまでNews型簡略化ルールを流用するか)は別途ユーザー確認が必要。
(2) **Key Phrase選定方式の変更承認**: 既存APPROVED_FOR_PRODUCTION仕様(668行、B1と同一選定)を、A2独立生成に伴い「A2自身の本文から選定」へ変更してよいか。
(3) **日本語タイトル供給方式の一般化承認**: 固定辞書(`JAPANESE_TITLES`/`registry`辞書)方式を、Family C型のconfig供給方式へ統一・一般化してよいか(News側にも影響する共通仕様変更)。

## 14. 無変更証跡・事前指定外Read

`git status --porcelain CURRENT_SPEC.md OPEN_ITEMS.md er0*.py` = 空(下記コミット前に実行・確認)。

事前指定外Read(理由付き): `er013_family_c_production_01.py`(全体構造把握のため関数一覧Grep後、Research/Ledger位置づけ確認目的でヘッダ部を追加確認)、`er013_family_c_production_runner_01.py`(`build_segments_for_level`/`load_article_paragraphs`本体、A2/B1のarticle_path独立性を確認するため)、`CURRENT_SPEC.md`586-1124行(A2関連複数節、事前指定の節一覧に対応する行範囲をまとめてRead、範囲外の逸脱なし)。
