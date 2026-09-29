# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 REPORT

本REPORTはPhase B(実装)の各Wave(W1, W2, W3, ...)ごとに追記される。
本セクションはW2のみを記録する(他Waveは別Sonnetが後で追記)。

## §W2 固定フレーズChampionのProduction Master Store正式登録

委任: `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_02.md`
設計根拠: `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md` §3(c)、§5

### 対応表(phrase→candidate→source→style→key/version→manifest entry)

| phrase | candidate/take | source wav | source sha256(先頭16桁) | style_prefix_used(逐語) | model/voice | 新style_instruction_version | master_audio_id(Production) |
|---|---|---|---|---|---|---|---|
| welcome | A(現行Master継続、新規登録なし) | - | - | "natural, clear, conversational"(不変) | gemini-3.8-flash-lite-tts/Charon | v2_flash_lite_short_style(不変) | aa130472d437ac80b7cdd474(既存) |
| preview_intro | C | er043 candC/shell/narration/preview_intro.wav | 69beef4047c13aaa | "natural, clear, conversational" | 同上 | v3_champion_2026_09_29 | b81f7fe5eb7a223fdeba29c9 |
| key_phrases_intro | C | er043 candC/.../key_phrases_intro.wav | a21e1242a987b206 | "natural, clear, conversational" | 同上 | v3_champion_2026_09_29 | 65a088023aff7bfdcfa3fafc |
| full_story_intro | C | er043 candC/.../full_story_intro.wav | 327b86d46f26e4dd | "natural, clear, conversational, unhurried pace, with a brief pause before continuing" | 同上 | v3_champion_2026_09_29 | b64fcd4ccaccae84fdf29930 |
| num_one | C | er043 candC/.../num_one.wav | a3a4e9883b9f81a7 | "measured, matter-of-fact delivery, consistent energy and tempo for every word, plain falling pitch at the end, spoken as a flat statement, not a question" | 同上 | v3_champion_2026_09_29 | e8fd9762bb314d5d19d0943f |
| num_two | B | er043 candB/.../num_two.wav | f612e4308037cb24 | "calm, steady, declarative tone, even volume and pace across the set, ending each word with a clear falling pitch, stated plainly, never rising like a question" | 同上 | v3_champion_2026_09_29 | 2c500e101c40aee9a89c4a1d |
| num_three | B take1 | er047 num_three_styleB/take1/narration/num_three.wav | 052f4cba47ff5b5b | 同num_two(B系統、source JSON上でcandidate_style_system="B"一致確認済み) | 同上 | v3_champion_2026_09_29 | 52a4759afa0c76dc747e8743 |
| num_four | C | er043 candC/.../num_four.wav | 6cb9d3a146049bcf | 同num_one(C系統) | 同上 | v3_champion_2026_09_29 | 8f755bf41f9a1bd145bc6eed |
| num_five | B take1 | er047 num_five_styleB/take1/narration/num_five.wav | 7bd81d17b43ca11d | 同num_two(B系統) | 同上 | v3_champion_2026_09_29 | b5c0f38798d0c1739645a771 |
| point_explanation(JA) | B | er043 candB/.../point_explanation.wav | 725e334cd97170fc | "自然な抑揚をつけて、はっきりと落ち着いた調子で話す" | gemini-3.8-flash-lite-tts/Charon(JA) | v3_champion_2026_09_29 | 90c38d7c67f98b9d6e5cb601 |

canonical_textは全件、Production `FIXED_ENGLISH_TEXTS`/`FIXED_JAPANESE_TEXTS_A2_ONLY`
(`er006_audio_cost_pilot_02_shared_narration.py`)と逐語一致(自動検証:
`er048_..._test_01.py::SourceJsonVerbatimMatchTests`、
`RegistrationsMatchSharedNarrationTests::test_no_stop_problems`)。
由来commit: er043系 `7f01bad1`、er047系(num_three/num_five take1) `fa37cd85`。

### 実装(最小diff)

- `er006_audio_cost_pilot_02_shared_narration.py`: `SHELL_CHAMPION_STYLE_BY_PHRASE_EN`
  (8 English phrase別style文言)・`SHELL_CHAMPION_STYLE_JA_POINT_EXPLANATION_B`・
  新version定数`SHELL_CHAMPION_STYLE_INSTRUCTION_VERSION = "v3_champion_2026_09_29"`
  を追加。`_resolve_shell_english_style_prefix_override`/`_make_english_key`に
  `name`引数を追加し、welcomeのみ旧`v2_flash_lite_short_style`+FALLBACK[0]を
  継続、それ以外はChampion mapを参照するよう分岐。`_make_japanese_key`は
  Flash-Lite backend時のみversionをChampion版へbump(JA側は
  `generate_charon_japanese`にstyle_prefix_override引数が無いため、style
  文言自体のruntime適用は引き続きスコープ外、Opus L2論点として下記に明記)。
- `er006_master_audio_store_01.py`: `register_precomputed(key, source_audio_path,
  qa_evidence)`を追加(既存`get_or_generate`は無変更、TTS生成パスを経由しない
  read-only登録専用の最小追加関数、既存entryがあればSKIPPEDでidempotent)。
- 新規`er048_fixed_shell_champion_master_registration_01.py`(登録スクリプト、
  `--dry-run`/`--apply`)・`_test_01.py`(11 test)。

### manifest前後(証拠)

| | entry数 | sha256 |
|---|---|---|
| 実行前 | 346 | `9070cb818999596e59bb8ec8a417999738dfba9ff0658857dfa5aa6629be888b` |
| 実行後(1回目apply) | 355 | `f6e734e7a400d943a05bebd57c7552bd04ecd602eaa2cd8f82b279bc3c2c0ef5` |
| 実行後(2回目apply、idempotent確認) | 355 | `f6e734e7a400d943a05bebd57c7552bd04ecd602eaa2cd8f82b279bc3c2c0ef5`(不変) |

`git diff --stat -- er006_output/master_audio_store_01/manifest.json`:
`939 insertions(+), 0 deletions(-)`(追加行のみ、既存346 entryへの削除・書換
なし)。

### 配線確認(¥0、TTS呼び出し0回)

`shared_narration.ensure_all_shared_narration_b1()`/`ensure_all_shared_narration_a2()`を、
`voice01.generate_charon_english`/`generate_charon_japanese`を「呼ばれたら
AssertionError」にmockした状態で実行し、welcome含む全10 phraseが
`reused=True`で完了することを確認(実TTS呼び出し0回)。welcomeは既存
Production Master(`aa130472d437ac80b7cdd474`)を継続reuse、他9件は本タスクで
登録した新master_audio_idをreuseした。

Family Z(`er026_family_z_fiction_production_runner_01.py`)は
`er006_audio_cost_pilot_02_shared_narration`をimportしておらず(Grep確認済み)、
現時点でこの共通Masterを参照するのはFamily X(`er019_family_x_audio_
production_runner_01.py`)のみ。したがって「共通Masterとして全Familyが
新Championをreuseする」という設計意図に対する他Familyへの副作用は現時点で
無い(将来Family Zがshared_narration経由の固定phraseを採用すれば自動的に
この新Championを参照する設計になっている)。

### テスト・regression結果

- `er048_fixed_shell_champion_master_registration_01_test_01.py`: 11/11 PASS
  (canonical_text/style_prefix_used逐語一致、model/voice不変、旧version
  非衝突、additive-only+idempotent登録、reuse時TTS 0回、welcome不変)。
- `er006_audio_cost_pilot_02_shared_narration_test.py`: 6/6 PASS(既存5件中
  4件を本タスクの引数追加[`_make_english_key`/
  `_resolve_shell_english_style_prefix_override`にname追加]に伴い理由
  コメント付きで更新、新規1件[Champion style map全体カバレッジ]追加)。
- `run_project_regression.py --pattern "er006*_test*.py"`: 23/23 PASS。
- `run_project_regression.py --pattern "er033*_test*.py"`: 64/64 PASS。
- `run_project_regression.py --pattern "er019*_test*.py"`: 164/167 PASS、
  3件FAIL。全て本タスク(W2)に起因しない(下記STOP該当なし節参照)。
  `er019_family_x_variable_role_style_wiring_01_test_01.py`
  (`ShellFixedPhraseUnaffectedTests`、本タスクの影響で壊れた唯一のテスト)
  のみ理由コメント付きで更新し、13/13 PASSへ復帰させた。

### 費用(A、一回限り)

¥0(TTS/ASR呼び出し0回、既存Trial出力の登録・reuseドライランのみ)。
上限¥5に対し実績¥0。

### STOP該当なし / 既知の限界・Opus L2論点

- STOP該当: なし(canonical_text/style文言の不一致は検出されなかった)。
- 既知の限界(意図的スコープ外、Opus L2要確認): point_explanation(JA)は
  `generate_charon_japanese`に`style_prefix_override`引数が無いため、
  Champion style文言("自然な抑揚を…")は**cache hit(reuse)経路でのみ**
  実際の音声と対応する。万一登録済み音声が失われ、cache miss経路で
  再生成される場合、`style_instruction_version`はbumpされているにも
  関わらず、生成される音声は旧来のJAPANESE_STYLE_PREFIX(または
  minimal instruction)のままになる、という理論上の不整合が残る
  (`generate_charon_japanese`へのstyle override機構新設は本タスクの
  スコープ外、TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01時点からの
  既知の制約を踏襲)。実運用上は本タスクでの登録によりcache missは
  発生しない設計(削除禁止のProduction Store)。
- shell層のversion bump(`SHELL_CHAMPION_STYLE_INSTRUCTION_VERSION`)の
  影響範囲: `_make_english_key`/`_resolve_shell_english_style_prefix_override`
  のシグネチャ変更(`name`引数追加)に伴い、既存テスト2ファイル
  (`er006_audio_cost_pilot_02_shared_narration_test.py`、
  `er019_family_x_variable_role_style_wiring_01_test_01.py`)の一部
  assertionを更新した(理由コメント付き、上記regression結果参照)。
  Trial専用の凍結スクリプト(`er040_*`/`er043_*`、旧シグネチャで
  `_make_english_key(text, tts_backend=...)`を直接呼んでいる)は
  今回のシグネチャ変更で動作しなくなるが、これらは既に完了済みTrialの
  一回限りrunner scriptであり、`run_project_regression.py`の対象
  patternにも含まれないため、本タスクでは意図的に無修正とした
  (Opus L2判断待ち、必要なら別途修正)。
- 並行W3タスク(`er019_family_x_audio_production_runner_01.py`他4ファイル)
  との差分競合はなし(本タスクではこれらのファイルを一切編集していない、
  `git status --porcelain`で確認)。W3側の作業起因と見られる一時的な
  regression失敗2件・`FamilyAUnchangedTest`1件(いずれも本タスクの変更
  ではなく、W3の未commit差分の存在自体が原因)は、W3がcommitすれば
  自然に解消される見込み(前例: 直近のTTS-VARIABLE-ROLE-STYLE task参照)。

---

## §W1 新記事構造(途中Heading廃止・忠実英訳・段落境界3分割・Comment1〜4・Heading Readout撤去)のProduction配線

管理ID: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`(委任`_04`、2026-09-29)。
設計書: `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md` §3(a)(b)・
§4、実施内容は同設計書§9-W1に追記。

### 変更ファイル・行数(`git diff --stat HEAD -- "er0*.py"`)

| ファイル | 変更 | 概要 |
|---|---|---|
| `er003_v1_n3_01_advanced_adaptation_generate.py` | +225 | Family X忠実英訳Prompt定数(`FAMILY_X_FAITHFUL_TRANSLATION_INSTRUCTION`等、er045逐語転記)、`generate_family_x_faithful_translation()`、`generate_family_x_in_one_line()`を追加。既存`ADVANCED_*`/`generate_advanced_adaptation()`は無変更 |
| `er003_v1_n3_01_scaffold_generate.py` | +81 | `split_family_x_article_text_v2()`追加(段落境界の決定論的3分割、er045と同一アルゴリズム)。既存`split_article_text()`(Family A本体が現役利用)は無変更 |
| `er003_v1_n3_01_standard_a2_generate.py` | +128 | Family X見出し廃止Standard(A2)Prompt(`FAMILY_X_STANDARD_A2_NO_HEADING_PROMPT`)、`generate_family_x_standard_a2_no_heading()`を追加。既存`STANDARD_A2_PROMPT_V5`/`generate_standard_a2()`は無変更 |
| `er012_e_family_entertainment_two_level_runner_01.py` | +127 | `run_writer_stage()`のAdvanced/Standard生成呼び出しを新関数へ切替、段落数retryヘルパー`_family_x_ensure_split_or_paragraph_retry()`新設 |
| `er012_e_family_entertainment_two_level_runner_test_01.py` | 更新 | 新関数のmockへ切替(fixtureをheadingなし構造へ変更) |
| `er019_family_x_audio_plan_01.py` | +83 | `split_family_x_article_text_v2()`(scaffold実装への薄いwrapper)、`reconstruct_family_x_article_text_v2()`、`FAMILY_X_B1_SEGMENT_ORDER_V2`/`FAMILY_X_A2_SEGMENT_ORDER_V2`(heading sub-segmentなし)を追加。旧関数・旧定数は無変更のまま残置 |
| `er019_family_x_audio_production_runner_01.py` | 154行差分 | Heading Readout sub-segment生成(B1B/A2両方)を撤去、本文3segmentを単一loopで生成、`build_segment_plan()`/`run_plan_stage()`/`run_theme_scaffold()`をv2 split・v2 segment順序へ切替、player row builderのheading分岐を削除 |
| `er019_family_x_audio_production_runner_01_test_01.py` | 更新 | heading前提の2テストをHeading不在確認へ更新 |
| `er019_family_x_flash_lite_role_style_wiring_02_test_01.py` | 更新 | fixtureへpart2/part3追加、heading呼び出し不在の確認へ更新 |
| `er019_family_x_variable_role_style_wiring_01_test_01.py` | 更新 | fixtureへpart2/part3追加(挙動assertionは無変更) |
| `er019_family_x_pointless_01_test_01.py` | 更新 | `FAMILY_A_FILES_MUST_BE_UNCHANGED`から本タスクで正式変更対象になった2ファイルを除外(理由コメント付き) |
| `er019_family_x_new_structure_wiring_01_test_01.py`(新規) | 約400行 | 本W1専用の新規テスト(31件) |

### Prompt sha256同一性(er045 Trialからの逐語転記)

| 定数 | sha256 |
|---|---|
| `FAMILY_X_FAITHFUL_TRANSLATION_INSTRUCTION` | `10836469880e11be082d19b92d6529b24fb76a224473e4228add840747aa6616`(er045一致) |
| `FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE` | `4a81f2d5c65073b4975e20cfb7799c8be128bd6020979d6ce0767978cb6f28b7`(er045 v2一致) |
| `FAMILY_X_TRANSLATOR_DEVELOPER` | `0883c2a32b5171d345fa352d532477895f9741af43dc515bf387d4fc2a21f1d9`(er045一致) |

`ADVANCED_VOCAB_RULE_V2_BLOCK`・`build_must_fix_block()`は既存Production資産をそのまま
呼び出す(コピペしない)。Standard(A2)側の見出し廃止Prompt
(`FAMILY_X_STANDARD_A2_NO_HEADING_PROMPT`)は、**er045等のTrialで一度も
実測検証されていない新規文言**である(er045はAdvanced/CEFR-B1レベルの
忠実英訳のみを検証、Standard/A2レベルの見出し廃止Promptは今回が初出)。
見出し依存部分のみをFamily X承認済み文言(段落保持指示)へ機械的に置換し、
CEFR A2簡略化ルール本文(`STANDARD_A2_NEW_VOCAB_BLOCK`含む)は一字も
変更していないが、この置換文言自体はE2E実行結果を見てからFable/ユーザーが
内容を確認することを推奨する(Opus L2論点、後述)。

### v2 split一致証拠(er045実出力との比較)

`er019_family_x_new_structure_wiring_01_test_01.py::V2SplitMatchesEr045OutputTests`
にて、`er045_output/family_x_no_heading_segmentation_trial_01/{hormuz,meta}/
trial_translation.json`(実際のタイトル・本文)+`trial_in_one_line.json`から
再構成した全文を`sc.split_family_x_article_text_v2()`へ通し、`trial_split.json`
(er045の`deterministic_three_way_split()`実行結果)とpart1/part2/part3・
word_countsが**完全一致**することを確認した(Hormuz: 8段落、Meta: 10段落、
いずれもstatus=OK)。

### OPEN-228 gate到達不能の証明

- `sc.split_article_text()`(旧、###見出し2つ+Main Story段落数2未満で
  RuntimeError)は無変更のまま残置(Family A本体が現役利用、
  `test_old_split_article_text_gate_still_exists_unmodified_for_family_a`)。
- `run_writer_stage()`(Family X唯一のProduction呼び出し元)は、AST解析で
  `sc.split_article_text(`を一切呼んでいないことを確認
  (`test_run_writer_stage_family_x_path_never_calls_old_split_article_text`)。
- 新v2 splitは見出し自体が存在しない構造のため、旧gateの直接原因だった
  「Main Story(見出し前)の段落数2未満」という状況が構造的に発生しない
  (`test_v2_split_does_not_raise_for_two_paragraph_intro`)。

### Advanced/Standardの段落数不足時の分岐(対称性)

`_family_x_ensure_split_or_paragraph_retry()`(新設ヘルパー)を
Advanced・Standard両方の分岐が同一呼び出し(2箇所、ソース上で確認)で使う。
挙動: (1) 初回生成結果をv2 splitへ通す、(2) `paragraph_count<3`なら
段落保持を強調したmust-fixで1回だけ再生成、(3) それでも3分割不能なら
`RuntimeError`(STOP、既存Deviation Check retryとは独立した別retry軸)。
Standard側はDeviation Check経由のmust-fix再生成後にも同じ`paragraph_count<3`
チェックを行い、不足なら追加retryせず即STOPする(既存retry上限を守る)。
単体テスト3件(`ParagraphCountRetrySymmetryTests`)でOK/1回retry成功/
それでもSTOPの3ケースを確認。

### JA入力検証表(hormuz/meta × (a)〜(e))

| 検証項目 | Hormuz | Meta |
|---|---|---|
| (a) sha256(`AN3-T0_ja.md`) | `99dcd56967c7f2a2d86416e132a4590939d01851a9024e79d63029e2a7a22300` | `ce4820a365d8620a19897fe98af58cd107f999a0f5dc7d1f7fc6f62cb8ea24d0` |
| (b) Prompt同一構成 | 一致(下記根拠) | 一致(下記根拠) |
| (c) `AN3-T0_deviation.json` | `LEDGER_COMPLIANT` | `LEDGER_COMPLIANT` |
| (d) SYMBOL_PREVENTION違反数 | 0件 | 0件 |
| (e) 本文段落数(v2 split対象) | 9段落(≥3) | 11段落(≥3) |

(b)根拠: `er039_output/.../AN3-T0_ja.md`は`er037_family_xy_concreteness_control_trial_01.py`
(commit `42f63319`、2026-09-28 17:25:08)が生成した`AN_r2.md`をreuseしたもの
(`reused_ja=true`)。この生成時刻は、reminder追加commit`1f47ff72`
(18:58:24)・reminder削除commit`54739a9d`(21:37:05)の**いずれよりも前**。
`git diff 42f63319 HEAD -- er019_family_x_ja_writer_o_r1_r2_01.py`は
`CONCRETENESS_CONTROL_AN3_BLOCK`定数追加のみで、`REVISION_INSTRUCTIONS`
(r1/r2)・`build_original_prompt()`の既存部分は無変更。er037は
`jaw.build_original_prompt()`(Production関数、直接import)+
`PATTERNS_A["A3"]+"\n"+PATTERNS_N["N2"]`(現行`CONCRETENESS_CONTROL_AN3_BLOCK`
と一字一句同一のテキスト)を使用しており、実質的に現行Production
`build_original_prompt()`が生成するPromptと同一構成。reminder文字列
「再び増やさない」は現在・生成時ともに0件(grep確認)。**すべての項目を
満たすため、E2E JA入力として採用可**と判定した。E2E入力配置先(元ファイル
不変・コピーのみ): `er019_output/family_x_refresh_e2e_01/{hormuz,meta}/
input/article_ja.md`+`provenance.json`(sha256・生成commit・検証結果を記録)。

### テスト・regression結果

| 対象 | 結果 |
|---|---|
| `er019_family_x_new_structure_wiring_01_test_01.py`(新規) | 31/31 PASS |
| `run_project_regression.py --pattern "er019*_test_*.py"` | 192/192 PASS(旧166+新31、既存2件の期待値をHeading不在へ更新済み) |
| `run_project_regression.py --pattern "er012*_test_*.py"` | 219/219 PASS |
| `run_project_regression.py --pattern "er003*_test_*.py"` | 1553/1557 PASS(4件失敗、後述の理由でW1非起因) |
| `run_project_regression.py --pattern "er045*_test_*.py"` | 19/19 PASS |
| `run_project_regression.py --pattern "er033*_test_*.py"` | 64/64 PASS |
| `run_project_regression.py --pattern "er048*_test_*.py"` | 11/11 PASS |

er003の4件失敗(`er003_test_p2j_investigate.py`3件・`er003_test_bad.py`1件)は、
`er003_test_*.py`(アンダースコア命名規則、本タスクで一切編集していないファイル群)
内のテスト件数を過去commit時点の固定件数(P2H:1032/P2I:660)と再集計比較する
「調査」テストであり、本タスクが変更した`er003_v1_n3_01_*.py`系ファイルとは
無関係(グロブパターンが異なる別名前空間、対象ファイルは一切touchしていない)。
件数drift自体は既存のtest infra課題(OPEN-209「test infraのmock-drift構造
リスク」と同種のcounting fragility)であり、W1の変更に起因しない。
`er003_test_bad.py`はディスク上に実体が存在しない合成fixtureで、本タスクとは
無関係。

### 費用

¥0(LLM/TTS/ASR呼び出し0回。実行したのは単体テスト[mock]・`certutil -hashfile`・
`git log`/`git diff`のみ)。

### Opus L2論点(レビュー依頼)

1. **Standard(A2)見出し廃止Promptの未検証性**: `FAMILY_X_STANDARD_A2_NO_HEADING_PROMPT`
   はer045等のTrialで一度も実測されていない新規文言(既存承認済みCEFR-A2簡略化
   ルール本文は無変更、見出し依存部分のみ機械的置換)。E2E実行結果(次Phase)を
   見てから内容を確認することを推奨。
2. **h3 validator置換の他Family非影響**: `vfl01.run_writer_with_technical_retry()`
   (h3構造Gate、Family A本体・News等多数が共有利用)は一切変更せず、Family X専用の
   別retryループ(`generate_family_x_faithful_translation`/
   `generate_family_x_standard_a2_no_heading`内に独立実装)を新設した。共有primitive
   自体への変更はゼロ(grep確認: `run_writer_with_technical_retry`の呼び出し元は
   引き続き10ファイル超、いずれも無変更)。
3. **旧gate(h3見出し2つ前提のsplit/検証)の残置**: `sc.split_article_text()`・
   `plan.split_family_x_article_text()`(旧、heading1/body2等)・
   `FAMILY_X_B1_SEGMENT_ORDER`/`A2_SEGMENT_ORDER`(旧、heading込み)は削除せず
   全て残置した(Family A本体・後方互換確認テストが依存するため)。Family Xの
   実行経路(`run_writer_stage`/`build_segment_plan`/`run_plan_stage`/
   `run_theme_scaffold`/`generate_family_x_b1/a2_segments`/
   `stage_assemble_family_x_b1/a2`)からは新v2関数・v2定数のみを呼ぶよう配線した。
4. **`er019_family_x_pointless_01_test_01.py`のFamily A無変更guardの更新**:
   `er003_v1_n3_01_scaffold_generate.py`(Family A本体が`split_article_text()`を
   現役利用、今回`split_family_x_article_text_v2()`を追加したため差分が発生)と
   `er012_e_family_entertainment_two_level_runner_01.py`(唯一の呼び出し元が
   Family X entertainment runnerであることをgrep確認済み、本来「Family A」対象
   ではなかった)の2ファイルを、理由コメント付きで一覧から除外した。設計書
   §3(a)が明示的に許可・想定した変更であることをOpus L2へ確認依頼する。

### STOP有無

STOPなし(E2E実発火[Hormuz/Meta完成音声]は次Phaseの範囲、本W1はコード・
テスト・JA入力検証のみ、費用¥0の制約を遵守)。

## §W4 Key Phrase 音声構造(Standard/Advanced共通骨格)のProduction配線

委任: `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_06.md`
設計根拠: CURRENT_SPEC.md「Key Phrase 音声構造(Standard/Advanced共通骨格)」
節(2026-09-29 `APPROVED_FOR_PRODUCTION`)・「Advanced Key Phrase 英語解説
(text仕様)」節

### 1. 現状確認(配線前)

| レベル | segment列(配線前) | 末尾Phrase | 参照wav | 生成関数/cache/Master key |
|---|---|---|---|---|
| Standard(a2) | phrase_en → japanese_meaning → phrase_en(反復) | あり | `kp{rank}_en.wav`と同一(in-memory reuse) | `_generate_key_phrase_segments_a2`(role "english"/"japanese_meaning")、共有`p9a.build_key_phrase_block()`が末尾を先頭と同一配列で組立(新規生成なし) |
| Advanced(b1b、配線前) | phrase_en → japanese_meaning(Charon) → phrase_en(反復) | あり | 同上 | `_generate_key_phrase_segments_b1`(role "english"/"japanese")、同じ共有`p9a.build_key_phrase_block()` |

**判明した事実**: 末尾Phraseの「反復」構造自体は、Standard/Advanced
いずれも既に共有Production資産`er003_b1_p9a_audio.py::build_key_phrase_block()`
(Family A/B/C/News/Z等が共有する既存関数、無変更)が実装済みであり、
`english_component_samples`という同一in-memory配列を先頭・末尾の両方へ
渡しているだけで、末尾専用の新規wav生成・別TTS callは元々発生していない
(付帯条件「先頭と末尾が同一canonical text・同一正式音源になること」は
Standard側では配線前から既に満たされていた)。**Standard(a2)はこの事実
により無変更**(決定どおり)。Advancedは中間部分(旧: 日本語意味/Charon)
のみを英語解説へ差し替える。

### 2. 変更ファイル

- `er019_family_x_kp_explanation_01.py`(新規): Advanced Key Phrase英語解説
  (explanation_en)のtext生成。Prompt/schema/語数上限(15語)は
  KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02(er041)の`APPROVED_
  FOR_PRODUCTION`仕様を逐語転記。QA validator(語数上限・新規Fact混入
  検知)をNG→技術retry(合計最大1回、parse失敗retryと排他)として実装。
  Model Routing Contract新規process`KEY_PHRASE_ADVANCED_EXPLANATION`
  (=既存`SUPPORT_MODEL`と同じ`gpt-5.6-luna`、新規モデル追加なし)。
- `er006_model_routing_contract_01.py`: 上記processを`PROCESS_MODEL_MAP`
  へ1行追加(既存process無変更)。
- `er033_tts_flash_lite_family_x_styles_01.py`: `KEY_PHRASE_EXPLANATION_EN`
  定数を新設(Variant B「clear, precise, at a measured pace, without
  dragging」、KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-
  TRIAL-04[er046]の逐語転記)。
- `er019_family_x_audio_production_runner_01.py`:
  - `generate_key_phrase_explanation_en_verified()`新設(Family X runner
    専用。共有資産`er003_v1_n3_01_tts_generate.py`は無変更のまま維持
    ——`er019_family_x_pointless_01_test_01.py::FamilyAUnchangedTest`が
    同ファイルのgit working tree diff=0を機械的に強制しているため、
    新関数は本runner自身に配置した)。内部は`repro01.generate_narration_
    snippet_verified_strict()`(Trial-02/-04で検証済みの呼び出しパターン
    をそのまま踏襲)。
  - `_generate_key_phrase_segments_b1()`(Advanced専用、関数名は歴史的経緯
    により"_b1"のままだが実体はb1bレベル): 中間roleを"japanese"から
    "explanation"へ変更。末尾Phraseは新規generateせず、`en_r`(先頭の
    "english"role結果)をそのまま`dict()`複製した`phrase_repeat`role
    として記録(`phrase_repeat_source="same_as_first"`)。
  - `_resolve_kp_explanations_text()`新設: 5件(4+1構成)まとめて1 callで
    解説を生成し、run単位のtext cache(`key_phrase_explanations_text`、
    canonical phraseの並びが前回runと完全一致する場合のみreuse)を持つ。
  - `load_family_x_b1_sources()`: `key_phrase_meanings[rank]`の読込元を
    `kp{rank}_ja_charon.wav`から`kp{rank}_explanation_en.wav`へ変更
    (dict key名`key_phrase_meanings`自体は、共有`er003_v1_n3_01_
    assemble.py::build_b1_key_phrase_blocks()`がこの名前をハードコード
    参照するため無変更のまま維持、共有assemble関数自体は一切変更しない)。
  - `_row_info_family_x()`/`_build_level_table()`: Advanced(b1b)のKey
    Phrase行に解説textを表示し、audio tupleを3要素
    (phrase_en, explanation_en, phrase_en[先頭と同一path])にして反復を
    明示。Standard(a2)側の行構成は無変更。

### 3. 経路別の先頭=末尾証明

`kp_results[rank]["phrase_repeat"]`は常に`dict(en_r)`(先頭"english"role
結果の複製)であり、"english"role側がどの経路(cache hit/miss・
Master Audio Store reuse・fallback[English lock]・解説側のSTOPPED)を
辿っても、`phrase_repeat.path`/`sha256`/`canonical_text`は必ず`english.path`
/`sha256`/`canonical_text`と同一になる(生成段で複製するのではなく、
既存resultをそのまま参照するため、構造的に分岐しようがない)。単体test
(`test_phrase_repeat_is_same_path_and_sha256_as_first`/
`test_phrase_repeat_identical_even_when_explanation_stopped`/
`test_phrase_repeat_identical_when_english_used_fallback_path`)で
cache hit/miss・fallback・解説側STOPPEDの3経路を実際に再現し確認。

### 4. 量産コスト(B)

Advanced 1記事あたりの追加: LLM解説生成 call = **1回**(4+1構成5件
まとめて1 callのため、KP件数[5]分の個別callにはならない。parse/QA
NG時のみ技術retryで最大+1回)。TTS explanation segment = KP件数分
(例5、rankごとに1回)。**Phrase再掲のTTS callは0**(`en_r`の複製のみ、
`test_english_phrase_tts_called_exactly_once_per_rank`で
`ensure_key_phrase_english_component`呼び出し回数がrank数と一致し
2倍にならないことを実証)。Standard側の追加callは0(無変更)。

### 5. テスト/regression結果(すべてmock、実LLM/TTS呼び出し0回、費用¥0)

- `er019_family_x_kp_structure_wiring_01_test_01.py`(新規、35件): 全PASS
  (Prompt/Style逐語性sha256照合、QA validator、技術retry[parse/QA、
  合計上限1回の相互排他を含む]、Model Routing Contract違反時fail-closed、
  Advanced組立構造[english/explanation/phrase_repeat、旧japaneseなし]、
  先頭=末尾の3経路確認、TTS/LLM呼び出し回数、text cache reuse、
  `_generate_or_reuse_kp`のrole="explanation"でのcache hit/miss、
  player行[Advanced 3-tuple/Standard 2-tuple不変])。
- 既存`er019_family_x_flash_lite_role_style_wiring_02_test_01.py`の
  `test_b1_key_phrase_segments_receive_tts_backend`を、Advanced中間role
  変更(japanese→explanation)に追従させて更新(tts_backend伝播という
  検証意図は無変更、fixtureへ`display_phrase`/`source_sentence`を追加)。
- `run_project_regression.py --pattern "er019*_test_*.py"`: collected=232
  passed=232 failed=0 errors=0(`er019_family_x_pointless_01_test_01.
  FamilyAUnchangedTest`含め全PASS、Family A/共有資産への意図しない差分
  なしを再確認)。
- `--pattern "er030*_test.py"`(実ファイル名が`_test.py`のため実行時に
  pattern末尾を補正): collected=71 passed=71。
- `--pattern "er033*_test_*.py"`: collected=64 passed=64。
- `--pattern "er041*_test_*.py"`: collected=13 passed=13。
- `--pattern "er042*_test_*.py"`: collected=16 passed=16。
- `--pattern "er046*_test_*.py"`: collected=21 passed=21。
- `--pattern "er048*_test_*.py"`: collected=11 passed=11。
- pre-existing失敗: 0件(全patternでfailed=0 errors=0、W4起因のregression
  なし)。

### Prompt/Style sha256

- `kp_explanation_gen.PROMPT_SHA256` =
  `c3d3734b760af258b86020002ef8a1ab63e16633a72bdab45019ca5b7be6fa7e`
  (DEVELOPER_MESSAGE+USER_TEMPLATE_HEADER+USER_TEMPLATE_FOOTER+JSON
  Schemaの結合文字列から算出。er041の同一定数から独立に再算出した値と
  test上で一致することを確認済み[逐語性の機械的証拠])。
- Variant B style文字列: `clear, precise, at a measured pace, without
  dragging`(`fl_styles.KEY_PHRASE_EXPLANATION_EN` == er046
  `VARIANT_STYLES["B"]`、test上で逐語一致確認済み)。
- 音声voice: Aoede(`shared_narration.ensure_key_phrase_english_component`
  のMasterAudioKeyが`speaker_voice="Aoede"`固定であることを既存コードで
  確認。解説音声は`repro01.generate_narration_snippet_verified_strict`
  経由でlanguage="en"の既定voice[`p9a.VOICE_NAME`]を使い、Trial-02/-04
  と同じ呼び出しパターンのため同じくAoede)。

### Opus L2論点(レビュー依頼)

1. **`key_phrase_meanings`という変数名/parts keyの意味的乖離**:
   共有`er003_v1_n3_01_assemble.py::build_b1_key_phrase_blocks()`が
   このkey名をハードコード参照するため、Advanced(b1b)ではこのkeyの
   中身が実際には「英語解説(explanation_en)」であり「日本語意味」では
   ない状態になった(共有関数自体は無変更の代償として生じた意味的
   乖離)。コード中に理由コメントは付与済みだが、将来の保守者が誤解する
   リスクをどう評価するか判断を仰ぐ。
2. **run単位text cache(`key_phrase_explanations_text`)の粒度**:
   5件バッチ生成という性質上、1件でもcanonical phraseが変われば全件
   再生成する設計(部分reuse不可)にした。retry/Local Rewriteで一部の
   Key Phraseだけ差し替わるケースが将来発生した場合、全件再生成
   (追加LLM call 1回)が許容範囲かどうかの判断を仰ぐ。
3. **QA NGの扱い(NG_ACCEPTED_AFTER_RETRY)**: 技術retry(1回)後もQA
   NGが残った場合、Gate/STOPはせずそのまま音声生成へ進める設計にした
   (既存のKey Phrase Set Redundancy QA等とは異なりHuman Review連携は
   未実装)。Production初回配線としてこの挙動で妥当か判断を仰ぐ。
4. **Model Routing Contractへの新規process追加**: 共有SSOT
   `er006_model_routing_contract_01.py`(全Production工程が参照)へ
   `KEY_PHRASE_ADVANCED_EXPLANATION`を追加した(既存`SUPPORT_MODEL`と
   同値、他processは無変更)。additiveな1行追加のみだが、共有Contract
   ファイルへの変更である点をOpus L2へ確認依頼する。

### 費用

¥0(LLM/TTS呼び出し0回。実行したのは単体テスト[mock]のみ)。

### STOP有無

STOPなし(E2E実測[Hormuz/Meta実データでの解説生成・TTS・完成音声]は
次Phaseの範囲、本W4はコード・テストのみ)。

## Opus L2 設計レビュー所見(2026-09-29、逐語保存、反映はユーザー判断待ち)

Status: 所見受領・未反映。BLOCKER 1 / MAJOR 4 / MINOR 9。E2E 発火可否・是正の実施はユーザー判断(PM_GOVERNANCE 11 節、Opus 後の Sonnet 自動再実行禁止)。

### Opus L2 設計レビュー: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W1〜W4)

read-only。コード・SSOT・一時ファイルの編集なし、テスト/TTS/ASR実行なし、¥0。

#### 1. 総括

**推奨: 是正後発火(BLOCKER 1件 + MAJOR 4件。いずれも小さくmock検証可能、追加費用¥0)**

W1〜W4の中核主張は実機コードで裏が取れました。特に以下は「問題なし」と確認済みです。

- **KP 先頭=末尾の同一性(W4の最重要論点)は構造的に保証されている**。共有 `er003_b1_p9a_audio.py:440-445 build_key_phrase_block()` が `english_component_samples` という同一in-memory配列を先頭と末尾の両方へ連結しており、`er003_v1_n3_01_assemble.py:665-674 build_b1_key_phrase_blocks()` / `:863-874 build_a2_key_phrase_blocks()` の両方がこれを呼ぶ。Assembly段で wav を1回読んで2回使うだけなので、retry / fallback / cache hit / Master reuse / 解説STOPPED のどの経路でも先頭と末尾が食い違う余地がない。W4が追加した `phrase_repeat`(`er019_family_x_audio_production_runner_01.py:744-746`、`dict(en_r)` の複製)は監査記録上の明示であり、TTS call を増やさない。Standard 無変更も妥当。
- **v2 split の二重実装drift(W1論点2)は無い**。`er019_family_x_audio_plan_01.py:147-153` は `sc.split_family_x_article_text_v2()` への薄いwrapperで、実装は `er003_v1_n3_01_scaffold_generate.py:185-243` の1箇所のみ。Writer段(`er012_e_..._runner_01.py:302,308,398,492`)とAudio段(runner `:210,322`)は同一関数を同一text(article.md)に適用する決定論処理なので一致する。
- **A2 Prompt の差分は機械置換のみ(W1論点1)**。`er003_v1_n3_01_standard_a2_generate.py:510-532` を `:147-169` (V5) と逐語比較した結果、差分は (a) 構造保持行の `the two "### " sections,` 削除、(b) `STANDARD_A2_SECTION_PRESERVE_SENTENCE` → `FAMILY_X_STANDARD_A2_NO_HEADING_PRESERVE_SENTENCE` の2箇所のみ。`STANDARD_A2_NEW_VOCAB_BLOCK` を含むA2簡略化ルール本文は1文字も変わっていない。ARM3(「may reorder, merge, or reshape paragraphs」)との矛盾も**無い**——新経路のStandard入力は `generate_advanced_adaptation()` ではなく忠実英訳(`:526-553` で「same number of paragraphs / Do not merge, split, or reorder」を明示)であり、旧Advanced adaptationは呼ばれない(`er012_e_..._runner_01.py:351,451`)。
- **段落数retryのStandard/Advanced対称性**は単一ヘルパー `_family_x_ensure_split_or_paragraph_retry()`(`er012_e_..._runner_01.py:293-315`)を2箇所(`:365-366`, `:461-462`)から同一に呼んでおり対称。Deviation must-fix後の再チェックも両側対称(`:398-404` / `:492-498`)。
- **W2の他Family波及は実質的に無い**(ただし報告の根拠は誤り。下記 MINOR N-8b)。`_make_english_key`/`_make_japanese_key` は `tts_backend != "speech_metadata_flash_lite"` なら version を `"v1"` に固定する(`er006_audio_cost_pilot_02_shared_narration.py:181-186, 210-211`)。flash_lite を渡す呼び出し元は Family X runner のみ(grep確認)なので、Family A/B/Cの固定shell音声は不変。
- **Model Routing Contract追加は additive かつ fail-closed**(`er006_model_routing_contract_01.py:109`、`require_model` は未知processを例外化 `:124-126`)。共有Contractへの1行追加として妥当。

#### 2. 所見一覧

##### BLOCKER-1: KP英語解説の QA NG が Gate も STOP も Human Review も通らず音声化・episode採用される(W4論点3)

- **根拠**: `er019_family_x_kp_explanation_01.py:283-298` — QA NG は retry 1回後 `NG_ACCEPTED_AFTER_RETRY` として**そのまま採用**。さらに (a) 初回で parse 失敗して retry を使い切った場合は QA retry が一切行われず status は `"NG"` のまま(`:287` の `and not retried_for_parse`)、(b) `NG_PHRASE_MISMATCH` 時は `english_explanation=None`(`:275-276`)。runner 側は `er019_family_x_audio_production_runner_01.py:726` で `explanation_text = explanation_row.get("english_explanation") or ""` として**空文字のままTTSへ渡し**、`:734-736` で status を記録するだけで分岐しない。
- **影響**: QA NG の内容は「語数15超」または「**phrase/source_sentence に無い固有名詞・数値の混入(=新規Fact)**」(`:143-158`)。この解説音声は Verified Fact Ledger の deviation check を一度も通らない新規英語コンテンツであり、NGを無視するのは他工程の扱い(deviation MAJOR→retry1回→なおMAJORならSTOP、`er012_e_..._runner_01.py:413-422`)および「安全≠成功」原則と非整合。空文字TTSは最終的に STOPPED→Audio Validation Gate で落ちる見込みだが、fail-closed の位置が遅く、無駄な課金と不明瞭な失敗になる。
- **最小是正案**(どちらか): (1) コード修正=text-gate status が OK 以外の rank は TTS を呼ばず、`kp_results[rank]["explanation"]` に `status="STOPPED"` + reason を記録する(既存 `verify_episode_audio_validation_gate` が `kp{rank}_explanation=STOPPED` で assembly をblockし、既存 `record_human_approval()` 経路で人間承認も可能)。(2) コードを触らないなら、E2E手順に**必須Gate**として「assembly実行前に `audit/tts_generation_results.json` の全 rank で `explanation_status_from_text_gate == "OK"` を確認、1件でも違えばSTOPしてユーザー判断」を明文化する。
- **E2E前に必要**: **はい**(1か2のいずれか)。

##### MAJOR-1: KP解説音声の cache が text guard も style_version guard も持たず、再runで text と音声が食い違う

- **根拠**: `er019_family_x_audio_production_runner_01.py:421-428 _generate_or_reuse_kp()` は status=="OK" + ファイル存在のみで reuse し、`expected_text` 相当の比較をしない(W3で可変segmentに入れた `:409-414` のガードが KP には意図的に非適用)。解説textは LLM 生成なので**phrase が1件変わると5件まとめて再生成**(`:684-696`)され、変わっていない rank の解説文も文面が変わり得る。その一方で音声は旧wavが reuse され、`:734` で `expl_r["explanation_text"] = explanation_text`(新text)に上書きされる。`_segment_asset_hash_stale()`(`er003_v1_n3_01_assemble.py:207-217`)は「記録sha256 vs 実ファイル」しか見ないため検知不能で、player 表示(`runner:1531-1536`)も新textを表示する。
- 併せて W3論点4の答え: `style_version` 不一致時に explanation は**再生成されない**(`_generate_or_reuse_kp` はこの値を見ない)。KEY_PHRASE_EXPLANATION_EN は Family X 固有の可変role styleなので、将来 style を変えても旧音声が黙って残る。
- **影響**: retry / Local Rewrite / `--stage tts` 再実行時に「audit・player上のtextと実音声が異なる」episode が Gate を通過する。OPEN-226 の冪等性ガード未実装(設計書§5-2 Guardrail 4)と同じ穴。
- **最小是正案**: `_generate_or_reuse_kp()` に `expected_text` 引数を追加し、role="explanation" では cached の `text`/`canonical_text` と `explanation_text` の一致を要求、加えて `cached.get("style_version") != FAMILY_X_VARIABLE_ROLE_STYLE_VERSION` なら reuse しない(可変segmentと同一の判定に揃える)。既存テスト `er019_family_x_kp_structure_wiring_01_test_01.py:391-427` が現挙動を固定しているため同時更新が必要。english role(used_form変化)も同様に guard すると望ましい(既存の限界の解消)。
- **E2E前に必要**: **はい**(修正しない場合は「tts stage 再実行時に b1b の `kp*_explanation_en.wav` と `key_phrase_explanations_text` を必ず破棄する」を必須運用として明記)。

##### MAJOR-2: Standard(A2) の構造Gateが Advanced より弱く、`# ` 欠落時に title が空のまま通過する

- **根拠**: Advanced は `_FAMILY_X_TITLE_BODY_RE = ^#\s+(.+?)\s*\n\n(.+)$`(`er003_v1_n3_01_advanced_adaptation_generate.py:579,600-603`)で `# ` を必須にしているが、Standard は `strip_title()`(先頭行が非空か)だけ(`er003_v1_n3_01_standard_a2_generate.py:573-574, 315-319`)。`split_family_x_article_text_v2()` は `^#\s+` に一致しなければ `title=""`・`body_start=0` とし、**title行を本文第1段落に含めたまま status OK を返す**(`er003_v1_n3_01_scaffold_generate.py:191-213`)。その結果 topic_intro が `"Today's topic is ."`(runner `:850`)、ASR期待部分文字列も空(`first_words("",3)`)になり、機械Gateに引っかからないまま音声化される。
- 併せて: (a) `## In one line` 欠落時は `split_v2` が RuntimeError を投げるが `_family_x_ensure_split_or_paragraph_retry()` は捕まえないので、retryせず課金後にクラッシュ停止する。(b) **本文中の markdown 見出しを検査する機械チェックがどこにも無い**。`detect_prohibited_symbols()`(`er003_audio_tts_asr_safety.py:1026-1076`)は `#` を対象にしておらず、`tts_safe_en/news_en` も除去しない(`er003_v1_n3_01_tts_generate.py:702-714, 778-779`)ため、混入した `### ...` は ASR不一致→3 attempt消費→STOPPED という高コストな失敗になる(ユーザー決定「途中Heading廃止」に対する機械的保証がゼロ)。
- **最小是正案**: `generate_family_x_standard_a2_no_heading()` のparse gateを Advanced と対称化する——`^#\s+` の title行、`## In one line` の存在、本文中に見出し行が無いこと、の3点を満たさなければ 1回retry。可能なら同じ3点を `split_family_x_article_text_v2()` に status として持たせ、両レベルで共通化するのが最小かつ効果的。
- **E2E前に必要**: **はい**(少なくとも Standard 側の `^#\s+` 必須化。残りは plan stage 出力の目視Gateで代替可)。

##### MAJOR-3: E2E は `--tts-backend speech_metadata_flash_lite` 必須だが CLI既定は legacy。しかも解説styleだけ backend gate が無い

- **根拠**: `er019_family_x_audio_production_runner_01.py:1707-1713` の既定は `structured_separation`。既定のままだと (a) 固定shell は version `"v1"` の旧キー=Champion未使用、(b) `_role_style()` / `_role_style_ja()` / `_role_style_slower()` は全て None を返し J3/E2/A2連結が無効(`:551-553, 796-798, 805-816, 827-830`)、(c) しかし **KP解説だけは `style_prefix_override=fl_styles.KEY_PHRASE_EXPLANATION_EN` を無条件に渡す**(`:733`)ため Variant B が legacy モデルへ適用される(er046 未検証の組み合わせ)。結果として「どの承認仕様にも一致しない半新規episode」が全Gateを通過する。
- **影響**: CLIフラグ1個の抜けで¥150〜250を無駄にし、かつ間違ったepisodeを試聴・承認しかねない。
- **最小是正案**: 解説styleも `_role_style` と同じ backend gate に揃える(対称化)か、runnerで tts stage 開始前に backend を明示チェックして記録/停止する。加えてE2E手順書に実行コマンド全文(`--tts-backend speech_metadata_flash_lite`、`--stage` 個別、`--budget-jpy` 段階値)を固定記載し、Gate項目として `entry_point.json.tts_backend` と audit の `style_prefix` 実値を突き合わせる。
- **E2E前に必要**: **はい**(コード修正 or 手順+Gate明文化のいずれか)。

##### MAJOR-4: OPEN-228 gate は `er012_e` runner の非writer stage経由で今も到達可能(到達不能証明はwriter段限定)

- **根拠**: `er012_e_family_entertainment_two_level_runner_01.py:556-557 run_scaffold_stage()` → `sc.run_theme_scaffold()` → `er003_v1_n3_01_scaffold_generate.py:886 split_article_text(article_text)`(旧h3見出し2つ必須gate、無変更で残置)。同runner の `main()` は `--stage scaffold/tts/assemble/player/all` でこの legacy A-Family 経路(`run_tts_stage` → `tts_gen.run_theme`)を呼ぶ(`:880-893`)。新構造(見出しなし)のarticle.mdでは確実に RuntimeError になり、しかも `--stage all` では **writer段の課金後**に落ちる。
- **影響**: W1報告の「OPEN-228到達不能」は `run_writer_stage` に限った話で、同じrunnerの他stageは新構造と非互換のまま残っている。運用トラップであり、OPEN-228 を CLOSED にする根拠としても不十分。
- **最小是正案**: `er012_e` の scaffold/tts/assemble/player stage を fail-fast にする(「Family Xは `er019_family_x_audio_production_runner_01.py` を使う」旨のRuntimeError)か `--stage` の choices を `ledger/writer` に限定する。あわせて2runnerの実行順をE2E手順書に明記し、OPEN-228のclose文面に「旧gateは残置、Family X新経路からは到達しない(er012_eの非writer stageは封鎖済み)」と書けるようにする。
- **E2E前に必要**: **はい**(最低でも実行手順の明文化。コード封鎖が望ましい)。

##### MINOR(E2E実測/後追いで可)

- **N-1(W1論点1の残り)**: 置換文言自体の出力品質はTrial未検証。E2Eで段落数保持・見出し不在・In one line保持・平均文長を実測確認すれば足りる。設計上の不整合は検出されず。
- **N-2**: 段落retryのmust-fixは `build_must_fix_block()`(`er003_v1_n3_01_standard_a2_generate.py:243-258`)を流用するため、ヘッダが「Verified Fact Ledger 照合で見つかったFact Safety問題」と宣言され、explanation が Standard 側でも「the Japanese article と同じ段落構造を保て」と指示する(`er012_e_..._runner_01.py:318-327`)。Standardモデルは日本語記事を見ないので指示が不整合。発生頻度は低く、文言修正のみ。
- **N-3**: Standard の KP 中間(japanese_meaning)は `style_prefix_override` を渡していない(`runner:951-956`)ため既定の長文 JAPANESE_STYLE_PREFIX のまま。W3 が japanese_title を J3 へ統一した理由(同一記事内のJA style混在)がそのまま残っている。ユーザー決定のJ3適用範囲外の可能性があるため仕様確認事項として提示し、E2Eの通し試聴で違和感を確認。
- **N-4(横断論点: runtime evidence)**: 可変segment・KP解説は `style_prefix`(override時は実文字列)・`model`・`voice`・`sha256`・`canonical_text` が揃う(`er003_b1_p9a_audio.py:286-301`)。一方 **Master Store reuse 経路(固定shell10件・KP english 5件)の返り値は status/path/reused/master_audio_id/qa_evidence のみ**で model/voice/style/canonical_text を含まない(`er006_master_audio_store_01.py:115-133`)。追跡は `master_audio_id` → `manifest.json` の join が必要で、manifest も style_instruction_id/version までで style 全文は持たない。Gate 13 の「全segmentで追跡可能」は**joinを前提に限り充足**。改善するなら reuse 返り値に `key.as_dict()` を1行追加。
- **N-5**: `_segment_missing_mandatory_disfluency_qa()`(`er003_v1_n3_01_assemble.py:192-196`)は `kp{rank}_explanation` を必須対象に含まない(`*_english` とレベル別listのみ)。実際には `disfluency_qa=True` で生成されるので証跡自体はある。また Family X は `required_structure=None` で gate を呼ぶ(`runner:1006`)ため構造完全性(rankごとsub-entry 3件)は未強制。後追い強化候補。
- **N-6**: point_explanation(JA)のChampion styleがcache hit経路のみ有効、という W2 の既知限界は Store削除禁止の前提で許容可。E2Eでは `reused=True` の実測確認で足りる。
- **N-7**: `EXPLANATION_JSON_SCHEMA` が minItems/maxItems=5 固定(`er019_family_x_kp_explanation_01.py:99-101`)で、`attempt()` は `len(parsed["explanations"]) != len(items)` を parse失敗扱いにする(`:255-256`)。KP件数が5以外になった場合、retry消費後 `ExplanationGenerationError` で tts stage 中断。`len(items)` から導出するか事前assertを推奨。
- **N-8a**: er040/er043 の凍結Trialスクリプトは旧シグネチャ `_make_english_key(text, tts_backend=...)` のまま動かなくなる(W2で意図的に無修正)。完了済み一回限りscriptなので許容だが、「再実行不能になった」ことをREPORT/SSOTに事実として残すこと(TODOとして残さない)。
- **N-8b**: W2報告の「shared_narration を参照するのはFamily Xのみ」は不正確(47ファイルがimportし、`er003_v1_n3_01_tts_generate.py`・`er012_b_family_production_runner_01.py` 等のProduction runnerも `ensure_all_shared_narration_*` を呼ぶ)。実際の隔離要因は `tts_backend` gate による version 固定。結論(他Family無影響)は正しいので、**根拠の記述だけ訂正**すべき(将来この誤った前提に依拠するリスクを避けるため)。
- **N-9**: player の `voice` 表示が level で一律(b1b=Charon)で、本文Aoede segmentも "Charon" と表示される(`runner:1503`)。既存からの表示上の不正確さ、音声には影響なし。

#### 3. E2E で実測確認すべき項目(Gate追加推奨)

1. `entry_point.json.tts_backend == "speech_metadata_flash_lite"`、かつ audit の `style_prefix` が J3/E2/A2連結/Variant B の**実文字列**であること(可変segment全件+KP explanation全rank)。
2. 各level `parts.json`: `title` 非空 / part1 が title文を含まない / `paragraph_count>=3` / 本文に `#` 始まり行が無い / `in_one_line` 非空。Standardのtitleが空でないことは特に必須(MAJOR-2)。
3. b1b 全rank: `key_phrases[rank].phrase_repeat.path/sha256 == key_phrases[rank].english.path/sha256`、narration に末尾Phrase用の別wavが存在しないこと、`ensure_key_phrase_english_component` 呼び出しが rank数と一致(TTS 2倍化なし)。
4. b1b 全rank: `explanation_status_from_text_gate == "OK"`、語数<=15、`new_fact_tokens` 0件。1件でも違えば **STOP してユーザー判断**(BLOCKER-1の運用代替)。
5. 固定shell 10件: `reused=True`、`master_audio_id` が W2表の9件(+welcomeは既存 `aa130472d437ac80b7cdd474`)と一致、TTS call 0。
6. `tts_generation_results.json` の `style_version == "v2_j3_e2_title"`、全segmentに model/voice/style_prefix/sha256/canonical_text。reuse経路は `master_audio_id` → manifest join で model/voice/version を確認(N-4)。
7. 通し試聴: A2 の JA style混在(title/preview/comment=J3 vs KP meaning=既定, N-3)、Advanced KP の phrase→英語解説→phrase の間(内部pause)が自然か、In One Line の長さ・一文性、Comment1〜4 が新3分割の内容と整合しているか(設計書§5-1項7の未解決点)。
8. 費用: 段階別 `--budget-jpy` 実測、KP解説 LLM call=**1/記事**、explanation TTS=rank数、Phrase再掲TTS=**0**、Heading Readout撤去による -2 segment/記事。
9. 実行規律: `--stage all` 禁止・段階個別実行(設計書§5-2)。MAJOR-1未修正で tts stage を再実行する場合は b1b の `kp*_explanation_en.wav` と `key_phrase_explanations_text` を事前破棄。MAJOR-4未修正なら `er012_e` は `--stage writer` のみで実行。

#### 4. 追加探索で見つけた論点(上記に含めた新規分)

- MAJOR-3(backend既定と解説styleの非対称)、MAJOR-4(OPEN-228の残存到達経路)、MAJOR-2(Standard構造Gateの弱さ・in-body heading無検査)、N-4(reuse経路のruntime evidence欠落)、N-7(schema 5件固定)、N-8b(W2根拠の事実誤り)は、委任された6論点には含まれていなかった追加発見です。
- W4論点1(`key_phrase_meanings` の意味的乖離)・論点2(run単位text cacheの粒度)・論点4(Contract 1行追加)は、単体では実害なしと判断します。ただし論点1は MAJOR-1(text/audio drift)と組み合わさると「keyの名前も中身も追跡しづらい」状態になるため、MAJOR-1の是正時に `explanation_text` を canonical text として明示記録することを併せて推奨します。論点2(1件変化で5件再生成、+1 call)はコスト影響が小さく許容可ですが、MAJOR-1の guard が無いと「textだけ更新・音声は旧」という形で害になるため、guard追加が前提です。

Production採用可否(`APPROVED_FOR_PRODUCTION`)および有料E2Eの発火判断は人間ユーザーのみが行うものであり、本レビューは判断材料の提示までです。実装・修正には着手していません。
