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

## W5(2026-09-29、委任`_08`): Opus L2所見是正(BLOCKER-1+MAJOR-1〜4)+Standard KP日本語意味へのJ3配線+E2E前¥0 Gate

ユーザー判断(2026-09-29)により、BLOCKER-1/MAJOR-1〜4は「既承認仕様から
一意に決まる実装是正」(`USER_DECISION_REQUIRED`ではない)として実装した。
Standard KP日本語意味へのJ3適用は正式決定`APPROVED_FOR_PRODUCTION`として
別途配線した。費用¥0(mock/regressionのみ、LLM/TTS/ASR呼び出し0回)。

### A〜G 変更箇所(ファイル:行)

- **A(BLOCKER-1、KP解説fail-closed)**: `er019_family_x_kp_explanation_01.py`
  (`generate_kp_explanations()`、retry後もNGを`NG_ACCEPTED_AFTER_RETRY`
  ではなく`"NG"`/`"NG_PHRASE_MISMATCH"`のまま返す)、
  `er019_family_x_audio_production_runner_01.py::_generate_key_phrase_
  segments_b1()`(L729以降、`text_gate_status != "OK"`のrankはTTSを呼ばず
  `status="STOPPED"`+reasonを記録)。
- **B(MAJOR-1、cache guard)**: `er019_family_x_audio_production_runner_
  01.py::_generate_or_reuse_kp()`(L429、`expected_text`/
  `require_style_version`引数追加)。呼び出し元3箇所
  (`_generate_key_phrase_segments_b1`のenglish/explanation、
  `_generate_key_phrase_segments_a2`のenglish/japanese_meaning)へ
  `expected_text`+`canonical_text`記録を追加、explanation/japanese_meaning
  には`require_style_version=True`も追加。`FAMILY_X_VARIABLE_ROLE_STYLE_
  VERSION`を`"v2_j3_e2_title"`→`"v3_j3_kp_meaning_and_explanation_guard"`
  へbump(旧style音声の誤reuse防止)。
- **C(MAJOR-2、構造Gate対称化)**: `er003_v1_n3_01_scaffold_generate.py::
  split_family_x_article_text_v2()`(L185、title欠落/`## In one line`
  欠落/本文見出し混入をstatus値`NG_MISSING_TITLE`/`NG_MISSING_IN_ONE_
  LINE`/`NG_HEADING_IN_BODY`で返す)、`er003_v1_n3_01_standard_a2_
  generate.py::generate_family_x_standard_a2_no_heading()`(L545、
  `_FAMILY_X_STANDARD_A2_TITLE_RE`で`^#\s+`必須化、Advancedの
  `_FAMILY_X_TITLE_BODY_RE`と対称)、`er012_e_family_entertainment_
  two_level_runner_01.py::_family_x_ensure_split_or_paragraph_retry()`
  (status非依存の汎用retryへメッセージ更新、ロジック自体は元々status!=
  "OK"を汎用的に扱う設計だったため変更不要)。
- **D(MAJOR-3、backend fail-fast)**: `er019_family_x_audio_production_
  runner_01.py::assert_production_tts_backend()`(L1823、新設)+
  `main()`のtts stage開始前呼び出し+`--allow-legacy-backend`フラグ新設。
  KP解説style: `_generate_key_phrase_segments_b1()`内`_kp_explanation_
  style()`ローカル関数で`_role_style()`と同一backendゲートに揃えた
  (従来は無条件でVariant B適用)。
- **E(MAJOR-4、OPEN-228非writer経路封鎖)**: `er012_e_family_
  entertainment_two_level_runner_01.py`の`run_scaffold_stage()`(L586)/
  `run_tts_stage()`(L590)/`run_assemble_stage()`(L594)/
  `build_player_html()`(L765)を`_FAMILY_X_ER019_MIGRATION_STOP_MESSAGE`
  でfail-fastするRuntimeErrorへ変更(`build_player_html`は元実装本体を
  到達不能なまま関数内に残置、`_row_info_b1b`/`_row_info_a2`/
  `_build_level_table`の追加削除を避けるため)。
- **F(Standard KP日本語意味へのJ3配線、正式決定)**: `er019_family_x_
  audio_production_runner_01.py::_generate_key_phrase_segments_a2()`
  (L1007、`_role_style_ja()`ローカル関数新設+`generate_a2_japanese_
  with_reading_safety()`呼び出しへ`style_prefix_override=_role_style_
  ja()`追加)。Advancedには`japanese_meaning`segment自体が無いことを
  `_generate_key_phrase_segments_b1()`のkp_results構造[english/
  explanation/phrase_repeat]確認で再検証(該当なし)。
- **G(MINOR)**: N-7(`er019_family_x_kp_explanation_01.py::_build_
  explanation_json_schema()`新設、`len(items)`からminItems/maxItems導出、
  `EXPLANATION_JSON_SCHEMA`本体[5固定、sha256算出基準]は不変)。
  N-4(`er006_master_audio_store_01.py::get_or_generate()`のreused/
  generated両分岐へ`result["master_audio_key"] = key.as_dict()`追加、
  L118-134・L169-172)。N-8a/N-8b(下記補遺)。

### N-8a/N-8b 補遺(REPORT §W2の記述訂正・事実記録)

- **N-8a**: er040/er043(固定shell Champion Trial、一回限りscript)は
  旧シグネチャ`_make_english_key(text, tts_backend=...)`のまま凍結して
  おり、W2以降の`_make_english_key(name, text, tts_backend=...)`(name
  引数追加)とは非互換のため再実行不能である。完了済み一回限りscriptの
  ため実害なし(意図的に無修正のまま残置、TODOとして扱わない)。
- **N-8b訂正**: 「shared_narrationを参照するのはFamily Xのみ」という
  REPORT §W2の記述は不正確だった。実際には47ファイルが`er006_audio_
  cost_pilot_02_shared_narration`をimportし、`er003_v1_n3_01_tts_
  generate.py`・`er012_b_family_production_runner_01.py`等の他Family
  Production runnerも`ensure_all_shared_narration_*`を呼ぶ。ただし
  `tts_backend`gateによりversionが固定される設計(`_make_english_key`/
  `_make_japanese_key`が`tts_backend != "speech_metadata_flash_lite"`
  なら`"v1"`固定)ため、実際の隔離要因は「参照ファイル数が少ないこと」
  ではなく「backend gateによるversion固定」である。結論(他Family無
  影響)自体は正しいが、根拠の記述を本節で訂正する。

### H. E2E前¥0 Gate(6項目、evidence付き)

| # | 項目 | Evidence |
|---|---|---|
| 1 | BLOCKER解消 | `er019_family_x_opus_l2_fixes_01_test_01.py::KpExplanationFailClosedTests`(5 tests、text-gate NG/NG_PHRASE_MISMATCH/status欠落のいずれもTTS未呼び出し+STOPPED記録+既存Audio Validation Gateがblockすることを実地テストで確認) |
| 2 | MAJOR-1〜4解消 | `GenerateOrReuseKpGuardTests`(4 tests、text/style_version guard)、`SplitV2StructureGateTests`+`StandardA2TitleGateSymmetryTests`(6 tests)、`ProductionBackendGateTests`(4 tests)、`er012_e_family_entertainment_two_level_runner_test_01.py::TtsStageJapaneseTitleInjectionTests`(4 tests、非writer stage fail-fast) |
| 3 | J3正式配線確認 | japanese_title(`generate_family_x_a2_segments`内`_role_style_ja()`)/preview・comment_1-4(同左)/KP日本語意味(`_generate_key_phrase_segments_a2`内`_role_style_ja()`、新設)の3箇所すべてが同一関数名`_role_style_ja()`・同一backendゲート(`tts_backend == "speech_metadata_flash_lite"`)を使うことをGrep+テスト(`er019_family_x_variable_role_style_wiring_01_test_01.py::KeyPhraseJapaneseMeaningJ3WiringTests`)で確認 |
| 4 | dangling referenceなし | `grep -rn "NG_ACCEPTED_AFTER_RETRY" *.py`は説明コメント2件+「廃止した」ことを確認するテストのassertion 2件のみ(稼働コードの分岐・返り値としては0件) |
| 5 | retry/fallback整合 | 既存`_family_x_ensure_split_or_paragraph_retry()`(status!="OK"を汎用的に1回retry)が新NGステータス(NG_MISSING_TITLE等)をコード変更なしで引き続き処理することをテストで確認(`SplitV2StructureGateTests::test_non_ok_status_is_caught_by_existing_retry_helper`)。KP解説の技術retry(1回)上限は無変更 |
| 6 | Standard/Advanced非対称なし | 下表参照 |

**Standard/Advanced 対比表(項目6の詳細)**:

| 項目 | Standard(A2) | Advanced(B1B) | 対称性 |
|---|---|---|---|
| Title行Gate | `^#\s+`必須(本W5で追加) | `^#\s+`必須(既存) | 対称化済み |
| In one line Gate | status値で判定 | status値で判定(共通関数) | 同一関数 |
| 本文見出し混入Gate | status値で判定(共通関数) | status値で判定(共通関数) | 同一関数 |
| 段落数retry | `_family_x_ensure_split_or_paragraph_retry()` | 同左 | 同一ヘルパー |
| KP中間segment | 日本語意味(J3、本W5で追加) | 英語解説(Variant B) | 意図的差異(ユーザー決定どおり) |
| KP中間segment cache guard | text+style_version guard(本W5で追加) | text+style_version guard(W5で追加) | 対称 |
| KP先頭=末尾 | 既存不変(W4で保証) | 既存不変(W4で保証) | 対称 |
| TTS backend gate | `assert_production_tts_backend()`共通 | 同左 | 共通 |

### E2E-PLAN(実行手順書)

**実行コマンド**(段階別、`--stage all`禁止):
```
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug <slug> --run <run> --level both --stage scaffold --tts-backend speech_metadata_flash_lite --budget-jpy 50
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug <slug> --run <run> --level both --stage tts --tts-backend speech_metadata_flash_lite --budget-jpy 150
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug <slug> --run <run> --level both --stage assemble --tts-backend speech_metadata_flash_lite --budget-jpy 10
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug <slug> --run <run> --level both --stage player --tts-backend speech_metadata_flash_lite
```
`er012_e_family_entertainment_two_level_runner_01.py`は`--stage writer`
(必要なら`--stage ledger`も)のみ実行する(scaffold/tts/assemble/player/
allはW5でfail-fast、実行しても課金前にSTOPする)。`TTS_EXECUTION_MODE=
STANDARD`(既定、`--tts-mode STANDARD`)を維持する。

**想定segment数・call数・費用**(記事×レベルごと、Hormuz/Meta×Standard/
Advanced想定):
- Standard: topic_intro/japanese_title/preview/comment_1-4/full_story_
  part1-3/in_one_line(11 segment)+KP 5rank×(english+japanese_meaning)
  =10 call。
- Advanced: topic_intro/preview/comment_1-4/full_story_part1-3/
  in_one_line(10 segment)+KP 5rank×(english+explanation)=10 call
  (explanation textは5rankまとめて1 LLM call)。phrase_repeatはreuseの
  ためTTS call 0。
- 想定費用: 段階別`--budget-jpy`(scaffold¥50/tts¥150/assemble¥10)を
  Guardrailとして使用。技術retry上限1回(段落数/KP explanation)。

**Guardrail**: 記事×レベルごとに上記budget-jpyを厳守し、超過時は
`assert_budget_ok()`がRuntimeErrorでSTOPする既存機構をそのまま使う。

**Opus「E2Eで実測確認すべき項目」9件(REPORT §3、転記)**: (1)
`entry_point.json.tts_backend`+audit `style_prefix`実文字列(可変segment
全件+KP explanation/japanese_meaning全rank)。(2) 各level `parts.json`の
title非空・見出し混入なし・in_one_line非空。(3) b1b全rank:
phrase_repeat=english同一path/sha256、TTS呼び出し回数不変。(4) b1b全
rank: `explanation_status_from_text_gate=="OK"`、1件でも違えばSTOPして
ユーザー判断。(5) 固定shell10件reuse=True・TTS call 0。(6)
`tts_generation_results.json`の`style_version`一致・全segment
model/voice/style_prefix/sha256/canonical_text記録。(7) 通し試聴(JA
style混在解消の確認含む)。(8) 費用実測(段階別)。(9) 実行規律
(`--stage all`禁止、段階個別実行)。

### テスト・regression結果

- 新規`er019_family_x_opus_l2_fixes_01_test_01.py`: 24 tests、全PASS。
- 既存テスト更新: `er019_family_x_kp_structure_wiring_01_test_01.py`
  (36 tests全PASS、`test_explanation_uses_variant_b_style`を backend
  gate対応に分割)、`er019_family_x_variable_role_style_wiring_01_test_
  01.py`(24 tests全PASS、`KeyPhraseRoleUnchangedTests`をJ3配線に合わせ
  て更新+`KeyPhraseJapaneseMeaningJ3WiringTests`新設)、
  `er012_e_family_entertainment_two_level_runner_test_01.py`(21 tests
  全PASS、非writer stage fail-fastテストへ更新)、
  `er019_family_x_audio_production_runner_01_test_01.py`(49 tests全
  PASS、DryRunEndToEndTestsのfixtureを新構造[見出しなし]記事へ更新
  [`SAMPLE_ARTICLE_V2_NO_HEADING`新設]、新Gateが旧構造fixtureを正しく
  NGにするようになったため)。
- Regression(`run_project_regression.py`): `er019*_test_*.py`
  259/259 PASS、`er012*_test_*.py` 222/222 PASS、`er006*_test_*.py`
  23/23 PASS(パターン自体は`er006_pronunciation_phase4_entity_like_
  test_01.py`のみ discover、`er006_master_audio_store_01_test.py`は
  別途直接実行し6/6 PASS)、`er033*_test_*.py` 64/64 PASS、
  `er045*_test_*.py` 19/19 PASS、`er048*_test_*.py` 11/11 PASS。
  `er003*_test_*.py`は1553/1557 PASS(4件失敗はいずれも本タスク由来
  ではない、下記参照)。

**pre-existing失敗4件(非起因根拠)**: `er003_test_bad.py::test_case_0`
(意図的に壊れたfixtureで回帰harness自体の自己診断用、ファイル名`_bad`
が示すとおり)、`er003_test_p2j_investigate.py`の3件(過去時点の
frozenテスト件数[P2H:1032/P2I:660]とlive実測値の比較。本タスクで
テストを新規追加[24件]・既存ファイルへテスト追加したことでlive件数が
増え、frozen historical値との厳密一致比較が不一致になる。設計上
「現在の値へ書き換えることも想定しない」frozen比較であり、新規テスト
追加のたびに発生しうる既知のtrade-off。`git stash`で本タスクの変更を
一時退避し同テストを実行した結果、変更前から同一の失敗[665!=660]が
再現することを確認済み[本タスク由来ではない])。

### 費用

¥0(LLM/TTS/ASR呼び出し0回、実行したのは単体テスト[mock]・regression
のみ)。

### STOP有無

STOPなし(新しいProduct仕様・未承認Prompt変更は発生しなかった。E2E
実測[Hormuz/Meta実データでの解説生成・TTS・完成音声]は次Phaseの範囲、
本W5はコード・テストのみ)。

## §E2E(委任_09、2026-09-29、Phase C実行)

### 事前確認

- `git stash list`: 空(stash無し)。
- `git status --short`: 未commit差分444件(既存の未追跡ファイル群、他
  タスク由来。本委任はこれらに触れていない)。HEADは`42c8093a`(pull
  済み、ff-only、以降に他Agentのcommitなし)。
- E2E-PLAN(REPORT行653〜692)・Gate 13項目(`docs/pm/PM_GOVERNANCE.md`
  「Gate 7補足」(a)〜(m))・Closeout 10項目(同3節1〜10)をRead(詳細は
  本委任のdelegation_log参照)。
- JA入力sha256照合: hormuz=`99dcd569...a22300`/meta=`ce4820a3...8ea24d0`
  ともにW1 provenance.jsonと一致(machine-verified、`hashlib.sha256`実測)。

### Hormuz: Writer段(ledger→writer)実行と結果

- 実行runner: `er012_e_family_entertainment_two_level_runner_01.py`
  (--ja-article er019_output/family_x_refresh_e2e_01/hormuz/input/
  article_ja.md --slug hormuz --out-dir er019_output/family_x_refresh_
  e2e_01/hormuz/run_01 --source-id FAMILY-X-REFRESH-E2E-PRODUCTION-
  WIRING-01 --budget-jpy 30 --stage ledger、続けて--stage writer。
  `TTS_EXECUTION_MODE=STANDARD`環境変数明示)。JA記事(JA Writer O)は
  再実行していない(fixed input、`ja_writer/runtime_evidence.json`へ
  「これはJA Writer O生成ではない」旨を明記したplaceholderを設置し、
  `derive_japanese_title()`用のtitle解決のみに使用)。
- ledger段: `--ledger-file`で既存の`er019_output/family_x_
  entertainment_production_runner_01/an3_t0_wiring_regression_01/
  hormuz/research_ledger/verified_fact_ledger.txt`(NEWS-FAMILY-X-B3-
  FACT-SELECTION-PRODUCTION-WIRING-01、2026-09-28生成、同一トピック
  [ホルムズ海峡20%償還料]のVerified Fact Ledger、HF-001〜HF-012)を
  reuse指定(新規Researcher/Verification web_search呼び出しを回避し
  費用¥0)。この判断はSonnetの裁量([既存の良好資産reuse]の精神を
  ledger構築コスト回避へ適用したもの)であり、Fable/ユーザー判断を
  仰ぐべき新規仕様ではないと考えるが、念のため明記する。
- writer段: Advanced(忠実英訳)生成→In one line生成→3分割OK→Deviation
  Check実行(`vfl01.run_deviation_check`)。結果:
  `overall_status="LEDGER_DEVIATION"`、MAJOR 1件
  (`claim_in_article="Even if this seems like a story about a distant
  sea, oil prices are linked to gasoline prices and transportation
  costs."`、`unsupported_new_claim=true`、`related_fact_id="HF-006"`、
  **`origin="ja_source"`**)。コードは`origin=ja_source`のMAJORを検知
  すると自動retryせず`JARecheckRequiredError`を送出する設計(must-fix
  retryは"translation"起因のみが対象、JA起因は盲目的な再生成をしない
  fail-closed設計)。**この時点でSTOP**(article.md/parts.json等は
  一切保存されず、audit証跡`b1b/audit/deviation_checks/advanced_
  attempt1.json`のみ保存。実費用¥0.99232[gpt-5.6-luna、3 call、web_
  search 0件]、budget-jpy 30に対し未超過)。
- **重要な追加観測**: 同一claim(オンライン価格とガソリン・輸送費の
  関連付け)は、W1入力の由来である`er039_output/family_xy_
  concreteness_control_trial_02/hormuz/cells/AN3-T0_deviation.json`
  では、**同一のVerified Fact Ledger本文**(HF-001〜HF-012、逐語一致)
  に対して**deviations=[]・overall_status="LEDGER_COMPLIANT"**(MAJOR
  無し)と判定されていた(英語本文もほぼ同一表現、旧見出し構造版)。
  すなわち、同一ledger・ほぼ同一claimに対し、deviation-check(同一
  method、同一model gpt-5.6-luna)が異なる回では異なる判定(MAJOR有/無)
  を返しており、**このGate自体がrun間で非決定的な挙動を示している**
  可能性が高い(JA入力側の実際の欠陥というより、LLM judgeのブレ)。
- STOP種別: 「KP explanationのtext-gateがOK以外のrankがretry後も残る
  /構造GateNGがretry後も残る」に準ずる「Gateが設計上の一発STOP経路
  [JARecheckRequiredError]へ到達し、既存retry機構の対象外」というSTOP
  条件に該当すると判断し、以降(Hormuz Standard生成・Hormuz audio段・
  Meta着手)を発火せず報告する(1記事ずつ完結原則により、Hormuz未完了の
  ままMetaへは進んでいない)。

### Gate結果(記事×レベル)

| 記事 | レベル | Writer段Status | Audio段 | Gate結果 |
|---|---|---|---|---|
| Hormuz | Advanced | STOPPED(JA_RECHECK_REQUIRED、deviation MAJOR/ja_source) | 未実行(¥0) | 未到達 |
| Hormuz | Standard | 未着手(Advanced STOPのためrun_writer_stage(only=None)がStandardに到達せず) | 未実行 | 未到達 |
| Meta | Advanced/Standard | 未着手(1記事ずつ完結原則、Hormuz未完了のため) | 未実行 | 未到達 |

Opus 9項目・(a)〜(m) 13項目監査: 音声artifactが一切生成されていない
ため、いずれも「評価不能(未到達)」。

### 試聴ページ

未作成(音声未生成のため)。Pages公開確認7項目は未実施。

### 費用(実測)

- Hormuz writer段: ¥0.99232(openai、gpt-5.6-luna、3 call)。
- Hormuz ledger段: ¥0(既存ledger reuse)。
- Audio段(scaffold/tts/assemble/player): 未実行、¥0。
- Meta: 未着手、¥0。
- **累計: 約¥1**(全体上限¥300に対し未使用同然、Guardrail超過なし。
  STOPは費用ではなくGate判定起因)。
- 費用B(継続コスト差分): 未評価(Audio段未実行のため実測不可)。

### Closeout 10項目充足状況(委任_09時点、SSOT反映は別途)

| # | 項目 | 状況 |
|---|---|---|
| 1 | Trial statusが分類済み | 該当なし(本委任はTrialではなくE2E) |
| 2 | UDRが提示済み | 本報告がUDR相当(Gate非決定性の扱いをFable/ユーザーへ提示) |
| 3 | 正式採用項目が追跡済み | 未到達(採用判断前) |
| 4 | APPROVED→PRODUCTION_WIRED完了確認 | 未到達(Gate未通過) |
| 5 | initial/retry/fallback整合確認 | 確認済み(JARecheckRequiredErrorはretry対象外の設計と実装を確認) |
| 6 | runtime evidence取得 | 取得済み(advanced_attempt1.json、raw_usage_log.jsonl) |
| 7 | SSOT整合 | 未実施(本委任はSSOT編集権なし、文案化は次段階) |
| 8 | 未報告Trialが無いこと | 該当なし |
| 9 | 無断deferが無いこと | 無断deferなし(STOPとして即時報告) |
| 10 | 次タスクへの持ち越し事項明示 | 本節「Next Action」参照 |

### Next Action(未回答項目、ユーザー/Fable判断待ち)

1. Deviation Check Gateの非決定性(同一ledger・同一claim・同一modelで
   run間結果が異なる)をどう扱うか: (a) 一度だけ同一入力で再実行し
   結果を確認する(コード変更なし、単なる再試行)/(b) 現在のMAJOR判定を
   正としてJA側の内容を精査する(ただしJA記事は本E2Eの固定入力であり
   変更は別管理IDの対象)/(c) Gate自体の非決定性を別課題として起票し
   今回は薦められた設計通りSTOPのまま報告する、のいずれを取るか。
2. 上記1の判断後、Hormuz Advanced→Standard→Audio段→Meta の順で
   委任を継続するか、次回委任へ持ち越すか。

## §E2E再開(委任_10、2026-09-29、Fable判定=既存fail-closed仕様どおりの
動作、新Product判断ではない)

### Fable判定の要旨

前委任_09のSTOP(JA_RECHECK_REQUIRED、Advanced deviation MAJOR/
origin=ja_source)は、`er012_e_family_entertainment_two_level_runner_01.py`
の既存仕様どおりのfail-closed動作であり新しいProduct判断ではないとFable
が判定。「JA側の再確認」の正式手段として、前委任run_01が入力に使った
er039 Trialセル(AN3-T0)をE2E入力から外し、JA記事をProduction正式JA経路
(`er019_family_x_entertainment_production_runner_01.py`→JA Writer O
`er019_family_x_ja_writer_o_r1_r2_01.py`)で新規生成し直し、run_02として
E2Eを継続する指示を受けた。

### 事前確認(¥0)

- `build_original_prompt()`が`CONCRETENESS_CONTROL_AN3_BLOCK`を
  `prompt += CONCRETENESS_CONTROL_AN3_BLOCK`で追加していることを
  `er019_family_x_ja_writer_o_r1_r2_01.py:163`で確認。
- `grep -n "再び増やさない" er0*.py`は2件ヒットしたが、いずれも
  `er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`
  および`er019_family_x_new_structure_wiring_01_test_01.py`内の
  `assertNotIn("再び増やさない", ...)`という文字列リテラル(reminderが
  **存在しないこと**を検証するテストコード)であり、Production側モジュール
  (`er019_family_x_ja_writer_o_r1_r2_01.py`を含む全er0*.py Production
  module)には0件(既存`FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_
  REPORT.md`のcommit `54739a9d`時点の説明と同一パターン)。
- `verbatim_shas()`(同ファイル121行)に`concreteness_an3_block_sha256`
  キーが含まれることをコード上確認し、実際の生成結果
  (`run_02/ja_writer/runtime_evidence.json`)でも
  `concreteness_an3_block_sha256=067030ff...6927fe`として実測(下記)。
- 既存Ledger(`NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01`由来、
  `er019_output/family_x_entertainment_production_runner_01/
  an3_t0_wiring_regression_01/{hormuz,meta}/research_ledger/
  verified_fact_ledger.txt`)およびstoryline_b3(fact_selection_evidence.
  json・selected_brief.md・full_ledger.json)を、`er019_family_x_
  entertainment_production_runner_01.py`が外部pathを直接参照するCLI引数
  を持たない構造上の制約のため、コピー(新規APIコール無し、sha256一致を
  実測確認済み)でrun_02配下へ複製して再利用した(Ledger再生成しない、
  storyline_b3も同様に既存選定結果を再利用)。
- 想定call数: JA Writer O(Original+Fact Check+must-fix retry(該当時)+
  R1+R2+R2 Fact Check)で6〜8 call程度、想定費用¥3〜6程度と記録した上で
  発火。

### JA生成(run_02、実測)

- 実行: `er019_family_x_entertainment_production_runner_01.py --theme
  "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応"
  --slug hormuz --out-dir er019_output/family_x_refresh_e2e_01/hormuz/
  run_02 --budget-jpy 30 --stage writer --stop-after writer`
  (`TTS_EXECUTION_MODE=STANDARD`環境変数明示)。
- 結果: research_ledger/storyline_b3は既存reuse(コスト¥0)。JA
  Original生成→Fact Check MAJOR 3件検知→must-fix retry 1回(既存仕様
  どおり)→`final_status="LEDGER_COMPLIANT"`。R1→R2→R2 Fact Check
  `final_status="LEDGER_COMPLIANT"`(must-fix不要)。
- 実費用: ¥4.063(`ja_original`¥0.337+`ja_original_check`¥1.188+
  `ja_original_must_fix`¥0.658+`ja_original_check_retry`¥0.421+
  `ja_r1`¥0.452+`ja_r2`¥0.506+`ja_r2_check`¥0.5)。
- `verbatim_shas`: `concreteness_an3_block_sha256=067030ff53ecb76a4d1477a
  3deace07b3e1fac438a33cb873edbe045cf6927fe`(実測)。
- 記号正規化違反: 0件(波ダッシュ/三点リーダー/スラッシュ/括弧/コロン/
  セミコロン、`revision2.md`を機械チェックし0件を確認)。
- 段落数: 10段落(タイトル除く、≥3を充足)。
- **前委任run_01のMAJOR claim(HF-006関連、「船が止まれば原油の流れが
  細り燃料・運送費に影響」)相当の記述は、新JA(`revision2.md`)には
  含まれていない**(must-fix過程でOriginal draftから当該表現が除去され、
  最終稿はHF-006を「Brent原油先物は7月13日に…上昇し」という値動きの
  みで言及し、燃料・輸送費への因果拡張は含まない)。

### Writer段(English、run_02)再実行と新STOP

- 実行: `er012_e_family_entertainment_two_level_runner_01.py --ja-article
  er019_output/family_x_refresh_e2e_01/hormuz/run_02/ja_writer/
  revision2.md --slug hormuz --out-dir er019_output/family_x_refresh_
  e2e_01/hormuz/run_02 --ledger-file er019_output/family_x_refresh_e2e_
  01/hormuz/run_02/research_ledger/verified_fact_ledger.txt --source-id
  FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 --budget-jpy 30 --stage
  ledger`(reuse、コスト増分¥0)→`--stage writer`。
- 結果: Advanced(忠実英訳)生成→Deviation Check実行→**新しいMAJOR
  1件を検知、`origin="ja_source"`**。`claim_in_article="The disappearance
  of the fee plan did not lead to a large, lasting fall in prices."`、
  `changed_causality=true`、`related_fact_id="HF-011"`、
  `explanation="HF-009が保証するのは撤回後の一時的な上げ幅縮小とその後の
  高水準への回復という観測であり、記事はそれを撤回の非因果的な結果として
  断定している。"`。コードは前回同様`JARecheckRequiredError`を送出し、
  以降(Standard生成・Audio段・Meta)を発火せず即STOP。
  Evidence: `er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/
  audit/deviation_checks/advanced_attempt1.json`。
- **重要な観測**: 今回のMAJOR claimは前委任run_01のMAJOR claim
  (HF-006関連、原油価格とガソリン・輸送費の関連付け)とは**別の claim**
  (HF-011関連、料金撤回と価格下落の因果関係の否定)である。これは
  「同一入力に対する判定のブレ」ではなく、**新規生成したJA記事(reminder
  除去後の現行Production経路、fact check must-fixで一度は
  LEDGER_COMPLIANTと判定された文章)に対して、English Advanced側の
  Deviation Checkが独立に別のja_source起因MAJORを検出した**という
  異なる事象である。すなわち、JA側Fact Check(JA本文のみを検証)と
  English Advanced側Deviation Check(英訳後、JA原文とLedger双方を参照し
  originを判定)は、それぞれ異なる基準・promptで動作しており、
  前者を通過した文章が後者でMAJOR/ja_sourceと判定される、という
  **チェッカー間の非対称**が実際に生じることが今回確認された(前回の
  「run間の非決定性」仮説とは別の、新しい観測事実)。
- コード上の該当箇所(`er012_e_family_entertainment_two_level_runner_01.
  py:266-275,388-398`)はこの状況をも「JA側の再確認が必要」として
  fail-closedにSTOPさせる設計であり、既存仕様どおりの動作。ただし
  ユーザー指示「JA生成後も再発した場合は本当にJA/Ledger側の問題であり
  Product判断に踏み込むためSTOP」に該当するため、本委任ではここで
  停止し、JA本文の書き換えやprompt変更などのProduct判断には踏み込まない。

### Gate結果(記事×レベル、run_02時点)

| 記事 | レベル | Writer段Status | Audio段 | Gate結果 |
|---|---|---|---|---|
| Hormuz | Advanced | STOPPED(JA_RECHECK_REQUIRED、deviation MAJOR/ja_source、run_02で別claim再発) | 未実行(¥0) | 未到達 |
| Hormuz | Standard | 未着手(Advanced STOPのため到達せず) | 未実行 | 未到達 |
| Meta | Advanced/Standard | 未着手(1記事ずつ完結原則、Hormuz未完了のため) | 未実行 | 未到達 |

Opus 9項目・(a)〜(m) 13項目監査: run_02でも音声artifactが一切生成
されていないため、いずれも「評価不能(未到達)」。

### 試聴ページ

未作成(音声未生成のため)。Pages公開確認7項目は未実施。

### 費用(実測、run_02累計)

- Hormuz JA生成(writer段): ¥4.063。
- Hormuz English writer段(ledger reuse ¥0 + Advanced生成+Deviation
  Check、STOPまで): ¥1.002(run_02 `raw_usage_log.jsonl`全体
  `compute_cost_jpy_so_far`実測=¥5.065、うちJA生成分¥4.063を除いた差分)。
- Audio段: 未実行、¥0。Meta: 未着手、¥0。
- **run_02累計: ¥5.07**(前委任_09消費¥0.99232と合算した本管理ID全体
  累計: **約¥6.05**、全体上限¥300に対し未使用同然。Guardrail超過なし。
  STOPは費用ではなくGate判定起因)。
- 費用B(継続コスト差分): 未評価(Audio段未実行のため実測不可)。

### Closeout 10項目充足状況(委任_10時点、SSOT反映は別途)

| # | 項目 | 状況 |
|---|---|---|
| 1 | Trial statusが分類済み | 該当なし(本委任はTrialではなくE2E) |
| 2 | UDRが提示済み | 本報告がUDR相当(チェッカー間非対称の扱いをFable/ユーザーへ提示) |
| 3 | 正式採用項目が追跡済み | 未到達(採用判断前) |
| 4 | APPROVED→PRODUCTION_WIRED完了確認 | 未到達(Gate未通過) |
| 5 | initial/retry/fallback整合確認 | 確認済み(JARecheckRequiredErrorはretry対象外の設計と実装を再確認、run_02でも同一挙動) |
| 6 | runtime evidence取得 | 取得済み(`advanced_attempt1.json`、`ja_writer/runtime_evidence.json`、`raw_usage_log.jsonl`) |
| 7 | SSOT整合 | 未実施(本委任はSSOT編集権なし、文案化は次段階) |
| 8 | 未報告Trialが無いこと | 該当なし |
| 9 | 無断deferが無いこと | 無断deferなし(STOPとして即時報告) |
| 10 | 次タスクへの持ち越し事項明示 | 本節「Next Action(再開)」参照 |

### Next Action(再開、未回答項目、ユーザー/Fable判断待ち)

1. JA本文の書き換え(Product判断)なしに、この種のja_source起因MAJOR
   (2回連続、異なるclaim)を解消する正式Production手段は現状ない。
   JA Writer Oのmust-fix機構はJA側Fact Checkの検出範囲に限られ、
   English Advanced側Deviation Checkが独自に検出するja_source逸脱は
   カバーしない。対応方針(a)JA Writer OのFact CheckとAdvanced
   Deviation Checkの基準を揃える仕様変更を検討/(b)ja_source MAJORの
   場合もmust-fixで1回だけJA側を自動修正する経路を新設/(c)現状の
   fail-closed設計を維持し、当該記事(Hormuz)はこのSTOPのまま次工程へ
   進まない、のいずれを取るか(いずれもコード・仕様変更を伴うため
   ユーザー承認が必要、本委任では実装しない)。
2. Meta記事は本STOPと独立の入力であり、同じくer039 Trialセルを
   使わずProduction正式JA経路で新規生成すれば試行できるが、1記事ずつ
   完結原則によりHormuz未完了の間は着手していない。Metaを先に試すか
   (Hormuzの問題が個別記事起因かChecker間非対称起因かの追加evidenceに
   なる)、Hormuzの方針決定を待つかの判断を仰ぐ。
3. 上記1の判断後、Hormuz Advanced→Standard→Audio段→Meta の順で
   委任を継続するか、次回委任へ持ち越すか。

## §W6(委任_11、2026-09-29、ユーザー明示決定「案B採用・
APPROVED_FOR_PRODUCTION・Gate 3までPRODUCTION_WIREDとしない」)

上記Next Action項目1の対応方針(b)「ja_source MAJORの場合もmust-fixで
1回だけJA側を自動修正する経路を新設」を、ユーザー明示決定(2026-09-29)
に基づき「案B」としてProduction配線した。詳細設計・判断理由は
`docs/pm/design_family_x_refresh_e2e_production_wiring_01.md` §9-W6参照。

### 変更ファイル

- `er012_e_family_entertainment_two_level_runner_01.py`: 既存
  `run_writer_stage()`本体を`_run_writer_stage_once()`へ改名し、
  `JARecheckRequiredError`を捕捉して案B(JA 1回再生成→Advanced/
  Standard再実行)を行う新しい薄いwrapper`run_writer_stage()`を追加。
  CLI `main()`は`--out-dir`配下の`storyline_b3/fact_selection_evidence.
  json`存在時のみ自動でstoryline_line/selected_fact_brief_textを読み
  込む(新CLI引数なし)。
- `er019_family_x_ja_writer_o_r1_r2_01.py`: `run_ja_writer_o_r1_r2()`に
  `original_must_fix: list | None = None`を追加(既存`build_original_
  prompt`のmust_fix機構への引数追加のみ、新Prompt文言なし)。
- `er019_family_x_entertainment_production_runner_01.py`: advanced/
  standard呼び出し2箇所へstoryline_line/selected_fact_brief_textを追加
  (in-memoryの既存値をそのまま渡すのみ)。
- `er019_family_x_new_structure_wiring_01_test_01.py`: 2テストの検査
  対象を`run_writer_stage`→`_run_writer_stage_once`へ追随(検証内容
  [Advanced/Standard対称性・旧gate不使用]自体は無変更)。
- 新規`er019_family_x_ja_recheck_retry_01_test_01.py`(9テスト、mock、
  費用¥0)。

### must-fix受け渡しの形式(新Prompt文言なしの証明)

English側`JARecheckRequiredError.major_deviations`のうち
`origin=="ja_source"`のものだけを既存`_must_fix_from_deviations()`
(fact_id/claim_in_article/issue/explanation、既存の汎用構造体)で変換
し、`run_ja_writer_o_r1_r2(..., original_must_fix=<そのリスト>)`へ渡す。
JA側は既存`build_original_prompt(storyline_line, selected_fact_brief_
text, must_fix=original_must_fix, full_ledger_text=full_ledger_text)`
→既存`build_must_fix_block()`が組み立てる(この2関数は元々JA Original
自身のFact Check MAJOR時の内部must-fix retryで使われているものと完全に
同一、1行も追加していない)。

### 1回上限・fail-closedのテスト証拠(`er019_family_x_ja_recheck_retry_
01_test_01.py`、9/9 pass)

- `test_ja_source_major_then_regenerate_once_then_completes`: JA Writer
  O(`run_ja_writer_o_r1_r2`)が1回だけ呼ばれ(`m_jaw.assert_called_
  once()`)、Advanced/Standardとも`LEDGER_COMPLIANT`で完走、
  `ja_recheck_used=True`・`ja_recheck_attempts=1`、`ja_writer/revision2.
  md`が再生成後の本文へ上書き、audit(`ja_recheck_attempt1.json`
  outcome=REGENERATED、`ja_recheck_attempt1_result.json`
  outcome=RESOLVED、`writer_run_summary.json`にja_recheck_used記録)を
  確認。
- `test_ja_source_major_persists_after_recheck_then_stops_no_second_
  regeneration`: 再実行後もMAJORの場合、`m_jaw.assert_called_once()`
  (2回目のJA再生成が呼ばれていない=無限retry禁止の直接証拠)、
  例外メッセージに`ja_recheck_attempts=1`を含む、audit outcome=
  STILL_MAJOR_AFTER_RECHECKを確認。
- `test_standard_stage_ja_source_major_shares_same_one_time_budget`:
  Standard段での発生でも同じ1回枠を消費してAdvanced/Standard両方を
  再実行すること(`m_jaw.assert_called_once()`、trigger_stage=
  "standard")を確認。
- `test_translation_origin_major_retry_unchanged_no_ja_recheck`:
  translation由来MAJORの既存must-fix retry(1回)は不変、JA Writer O
  は一切呼ばれないこと(`m_jaw.assert_not_called()`)を確認。
- `test_ja_fact_check_stop_propagates_as_runtime_error`: JA再生成中に
  `JAFactCheckStopError`が起きた場合、`RuntimeError`(JARecheckRequired
  Errorではない)へ変換されSTOPし、rejected本文とaudit記録を保存する
  ことを確認。
- `test_no_ja_recheck_when_storyline_not_provided_backward_compat`:
  storyline_line等を渡さない既存呼び出しは従来どおり
  `JARecheckRequiredError`がそのまま伝播すること(後方互換)を確認。

### Checker Prompt・severity定数のsha256不変(同テストファイル、3/3
pass)

`vfl01.DEVIATION_PROMPT_TEMPLATE`/`HOOK_AWARE_DEVIATION_PROMPT_
TEMPLATE`/`DEVIATION_FLAG_KEYS`のsha256/値を、本委任着手前に独立算出
した既知値と一致確認(`er003_v1_en_direct_vfl_01_generate.py`は本委任
で一切編集していない)。

### Regression結果(実測、費用¥0)

| pattern | collected | passed | failed | errors |
|---|---|---|---|---|
| `er019*_test_*.py` | 268 | 268 | 0 | 0 |
| `er012*_test_*.py` | 222 | 222 | 0 | 0 |
| `er003*_test_*.py` | 1557 | 1553 | 3 | 1 |
| `er009*_test_*.py` | 26 | 26 | 0 | 0 |

`er003*_test_*.py`の4件(`er003_test_bad.FixtureTests.test_case_0`
[常時失敗する検証用fixture]、`er003_test_p2j_investigate.py`の3件
[過去期の報告件数と現在のテスト総数を比較するdrift調査、テスト総数の
自然増で恒常的に乖離する既知のmeta-test])は本委任が触れたファイル
(JA/EN writer・deviation check経路)と無関係であり、本委任由来ではない
(git diffで本委任の変更ファイルにこれらを含まないことを確認済み)。

### E2E run_03の実行手順(run_02との差分)

run_02の手順(本REPORT §E2E再開)と比較した差分は以下のみ、新規引数の
追加はない:

1. `er019_family_x_entertainment_production_runner_01.py --theme "..."
   --slug hormuz --out-dir <run_03の out-dir> --budget-jpy 30 --stage
   writer --stop-after writer`(run_02と同一コマンド。`storyline_b3/
   fact_selection_evidence.json`をrun_02から複製[既存Ledger/storyline_
   b3再利用と同じ既存運用]しておけば、この段はJA生成のみで変更なし)。
2. `er012_e_family_entertainment_two_level_runner_01.py --ja-article
   <out-dir>/ja_writer/revision2.md --slug hormuz --out-dir <run_03の
   out-dir> --ledger-file <out-dir>/research_ledger/verified_fact_
   ledger.txt --source-id FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01
   --budget-jpy 30 --stage ledger`(reuse)→`--stage writer`(run_02と
   コマンド文字列は同一)。**差分はコマンドではなくファイル配置**:
   `<out-dir>/storyline_b3/fact_selection_evidence.json`が存在すれば
   (手順1で複製済みのため存在する)、案Bが自動的に有効化される。存在
   しなければ従来どおりja_source MAJORで即STOPする(run_02相当の挙動)。
3. ja_source MAJORが発生した場合、`<out-dir>/ja_writer/audit/ja_
   recheck_attempt1.json`(outcome=REGENERATED/JA_FACT_CHECK_STOP/未
   作成=1回枠未消費)と`ja_recheck_attempt1_result.json`(outcome=
   RESOLVED/STILL_MAJOR_AFTER_RECHECK)、`<out-dir>/writer_run_summary.
   json`の`ja_recheck_used`/`ja_recheck_attempts`を確認する。

本委任ではrun_03の実発火(有料API呼び出し)は行っていない(委任範囲は
コード・テスト・SSOT反映のみ、費用上限¥0)。run_03の実発火可否はユーザー
判断。

### 費用・STOP

費用: ¥0(mock/regressionのみ、実API呼び出し0件)。STOPなし(新しい
Product判断・未承認Prompt変更は発生しなかった。Checker再設計自体は
別途OPEN化し、本委任では着手していない)。

## §E2E run_03(委任_12、2026-09-29、案B有効での実発火・Hormuz STOP)

### 事前確認(¥0)

- `git pull --ff-only origin main`: no-op(既にup to date)。
- `git stash list`: 空。
- `grep -n "再び増やさない" er0*.py`: 2件、いずれもテストファイル
  (`er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`
  `assertNotIn`、`er019_family_x_new_structure_wiring_01_test_01.py`
  `assertNotIn`)のみでProduction module 0件(既知パターンと一致)。
- 案B armed化: `er019_output/family_x_refresh_e2e_01/hormuz/run_03/
  {research_ledger,storyline_b3}`をrun_02から複製(`verified_fact_ledger.
  txt` sha256=`9bd6834e...ae77ae1a6`、`fact_selection_evidence.json`
  sha256=`a020add7...8dde8dc98e402`、いずれもrun_02と一致を実測確認)。
  Meta側は`er019_output/family_x_entertainment_production_runner_01/
  an3_t0_wiring_regression_01/meta/{research_ledger,storyline_b3}`から
  同様に複製・sha256一致確認済み(`verified_fact_ledger.txt`=
  `ea0ce587...5988b7c5f56`、`fact_selection_evidence.json`=
  `ff787382...053a7858c0a4`)が、下記Hormuz STOPのため**未使用**
  (1記事ずつ完結原則、run_02と同じ扱い)。

### Hormuz: JA生成(run_03、実測)

- 実行: `er019_family_x_entertainment_production_runner_01.py --theme
  "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応"
  --slug hormuz --out-dir er019_output/family_x_refresh_e2e_01/hormuz/
  run_03 --budget-jpy 40 --stage writer --stop-after writer`
  (`TTS_EXECUTION_MODE=STANDARD`環境変数明示)。research_ledger/
  storyline_b3は上記コピーをreuse(¥0)。
- 結果: JA Original生成→Fact Check MAJOR 1件検知→must-fix retry 1回
  (既存仕様)→`final_status="LEDGER_COMPLIANT"`。R1→R2→R2 Fact Check
  `final_status="LEDGER_COMPLIANT"`(must-fix不要)。
- 実費用: ¥4.018(`ja_original`¥0.486+`ja_original_check`¥0.986+
  `ja_original_must_fix`¥0.693+`ja_original_check_retry`¥0.334+
  `ja_r1`¥0.562+`ja_r2`¥0.598+`ja_r2_check`¥0.358)。
- `verbatim_shas.concreteness_an3_block_sha256`=
  `067030ff53ecb76a4d1477a3deace07b3e1fac438a33cb873edbe045cf6927fe`
  (run_02と完全一致、AN3-T0 Prompt不変の証拠)。
- 記号正規化違反: 0件(revision2.md実測)。段落数: 13(≥3充足)。

### Hormuz: Writer段(English、run_03)実行と案B発動・再STOP

- ledger段(reuse、¥0増分): `er012_e_family_entertainment_two_level_
  runner_01.py --ja-article <run_03>/ja_writer/revision2.md --slug
  hormuz --out-dir <run_03> --ledger-file <run_03>/research_ledger/
  verified_fact_ledger.txt --source-id FAMILY-X-REFRESH-E2E-PRODUCTION-
  WIRING-01 --budget-jpy 30 --stage ledger`。
- writer段: 同コマンドで`--stage writer`。`<run_03>/storyline_b3/
  fact_selection_evidence.json`が存在するため案Bが自動armed。
- **1回目**: Advanced(忠実英訳)生成→Deviation Check→**MAJOR 1件、
  origin=ja_source**(`claim_in_article="That is why the price pulled
  back only once after the fee proposal was withdrawn, and then
  returned to a high level."`、`changed_causality=true`、
  `changed_certainty=true`、`related_fact_id=HF-009`)。
  `JARecheckRequiredError`検知→**案B発動**: JA Writer Oを
  `original_must_fix`付きで1回だけ再生成(R2 must-fix→Fact Check
  `final_status=LEDGER_COMPLIANT`、新JA text sha256=
  `b03c43474617ac779913bc5ad6e5a1b0cd1936407f5cce8b5a8f069353a965cf`、
  旧revision2.md sha256=`cdcb57dc033a997f7ba11d7bded644a74f3b1277440b3e
  10e103779ce491829f`と相違=実際に再生成されたことを確認)。Evidence:
  `<run_03>/ja_writer/audit/ja_recheck_attempt1.json`
  (`outcome="REGENERATED"`)。新JA本文: 記号違反0、段落数10。
- Advanced再実行: 新JA本文でAdvanced再生成→Deviation Check再実行→
  **`overall_status="LEDGER_COMPLIANT"`(deviations=[])**。
  `<run_03>/b1b/article.md`・`parts.json`保存(`status="OK"`、
  `title="The Fee Plan Leaves, High Oil Prices Stay"`、
  `paragraph_count=9`、`boundary_i/j=4/7`、`in_one_line`非空)。
- Standard生成: 新JA本文でStandard(A2)生成→Deviation Check実行→
  **新たな別MAJOR 1件、origin=ja_source**
  (`claim_in_article="Oil prices did not fall across the whole market
  after the plan was withdrawn."`、`changed_scope=true`、
  `related_fact_id=HF-009`、`explanation`="Brent先物の観測が石油市場
  全体へ拡張され、対象範囲が広がっている(Ledgerによる裏付けなし)")。
  Evidence: `<run_03>/a2/audit/deviation_checks/standard_attempt1.json`。
- **案Bの1回上限により2回目のJA再生成は行わず、fail-closedでSTOP**
  (`委任のSTOP条件「案Bの JA 差し戻し 1 回後も ja_source MAJOR」に
  該当)。Evidence: `<run_03>/ja_writer/audit/ja_recheck_attempt1_
  result.json`(`outcome="STILL_MAJOR_AFTER_RECHECK"`、`stage="standard"`)。
  例外メッセージに`ja_recheck_attempts=1`を明記(2回目のJA Writer O
  呼び出しは発生していないことをファイル一覧でも確認: `ja_recheck_
  attempt2*.json`は存在しない)。`_11`委任のテスト
  `test_ja_source_major_persists_after_recheck_then_stops_no_second_
  regeneration`が想定した挙動と実運用の結果が一致することを実データで
  確認した。
- a2/article.md・parts.jsonは保存されず(STOPのため)、Standard段は
  未完成のまま。Audio段(scaffold/tts/assemble/player)は未実行(¥0)。

### Gate結果(記事×レベル、run_03時点)

| 記事 | レベル | Writer段Status | Audio段 | Gate結果 |
|---|---|---|---|---|
| Hormuz | Advanced | 完成(`LEDGER_COMPLIANT`、案B適用後、article.md/parts.json保存済み) | 未実行(1記事ずつ完結原則によりStandard未完了のため見送り、¥0) | 未到達(Standard未完了) |
| Hormuz | Standard | STOPPED(案B 1回上限到達後もja_source MAJOR再発、STILL_MAJOR_AFTER_RECHECK) | 未実行 | 未到達 |
| Meta | Advanced/Standard | 未着手(1記事ずつ完結原則、Hormuz未完了のため) | 未実行 | 未到達 |

Gate 13項目((a)〜(m))・Opus 9項目・ユーザー指定Gate 3確認項目は、音声
artifactが一切生成されていないため全て「評価不能(未到達)」。

### 試聴ページ

未作成(音声未生成のため)。Pages公開確認7項目は未実施。

### 費用(実測、run_03累計)

- Hormuz JA生成(writer段、original): ¥4.018。
- Hormuz English writer段(ledger reuse¥0+Advanced初回+案B JA再生成+
  Advanced再実行+Standard実行+STOPまで): run_03の`raw_usage_log.jsonl`
  全体を`compute_cost_jpy_so_far()`で実測=**¥10.35**
  (`by_provider={'openai': 10.35}`)、うちJA生成分¥4.018を除いた
  English writer+案B再生成分の差分=約¥6.33。
- Audio段: 未実行、¥0。Meta: 未着手、¥0。
- **run_03累計: ¥10.35**(前委任までの本管理ID累計¥6.05と合算した
  本管理ID全体累計: **約¥16.40**、全体上限¥300に対し未使用同然)。
  記事別Guardrail(JA¥40/EN¥30)超過なし(`assert_budget_ok`による
  RuntimeError STOPは発生していない。STOPは案B 1回上限のfail-closed
  仕様によるものであり費用超過ではない)。
- 費用B(継続コスト差分): 未評価(Audio段未実行のため実測不可)。

### Closeout 10項目充足状況(委任_12時点、SSOT反映は別途)

| # | 項目 | 状況 |
|---|---|---|
| 1 | Trial statusが分類済み | 該当なし(本委任はTrialではなくE2E) |
| 2 | UDRが提示済み | 本報告がUDR相当(下記Next Action参照) |
| 3 | 正式採用項目が追跡済み | 未到達(Gate未通過、採用判断前) |
| 4 | APPROVED→PRODUCTION_WIRED完了確認 | 未到達(Gate未通過) |
| 5 | initial/retry/fallback整合確認 | 確認済み(案B 1回上限・fail-closedが実データで想定どおり動作することを確認) |
| 6 | runtime evidence取得 | 取得済み(`ja_recheck_attempt1.json`/`ja_recheck_attempt1_result.json`/`standard_attempt1.json`/`b1b/parts.json`/`raw_usage_log.jsonl`) |
| 7 | SSOT整合 | 未実施(本委任はSSOT編集権なし、文案化は次段階) |
| 8 | 未報告Trialが無いこと | 該当なし |
| 9 | 無断deferが無いこと | 無断deferなし(STOPとして即時報告、Meta未着手も1記事ずつ完結原則の明示的帰結) |
| 10 | 次タスクへの持ち越し事項明示 | 本節「Next Action」参照 |

### Next Action(未回答項目、ユーザー/Fable判断待ち)

1. 案B(JA 1回差し戻し)を適用してもHormuzはStandard段で**別のja_source
   MAJOR**(HF-009関連、今回はscope拡張)が発生し、fail-closed STOPに
   至った。これで委任_09(run_01)・委任_10(run_02)・本委任(run_03)の
   3回とも、Hormuzはja_source起因の判定でAudio段に到達していない
   (3回とも異なるclaim/異なる機構での検出)。案Bは「1回のJA差し戻しで
   解消するケース」には有効(Advanced段は今回解消した)が、Standard段で
   新たな逸脱が生じるケースまではカバーしない設計上の限界が実データで
   確認された。
2. 対応方針(いずれもコード・仕様変更を伴うためユーザー承認が必要、
   本委任では実装しない): (a) 案Bの適用範囲をAdvanced/Standard
   合計で複数回(例: 記事あたり最大2回)に拡張する/(b) JA Writer Oの
   Fact CheckとEnglish側Deviation Checkの基準統一(Checker再設計、
   既存OPEN Item)に本格着手する/(c) Hormuzという特定トピック
   (ホルムズ海峡・原油価格)自体がscope/causality逸脱を起こしやすい
   性質を持つ可能性を踏まえ、別トピックで案Bの有効性を検証する
   (Metaは未着手のため独立データになり得る)/(d) 現状のfail-closed
   設計を維持し、Hormuzは今回のSTOPのまま次工程へ進まない。
3. Metaは本STOPと独立の入力であり、1記事ずつ完結原則によりHormuz
   未完了の間は着手していない(storyline_b3/research_ledgerは
   run_03向けに複製済み、sha256確認済みで着手可能な状態)。Hormuzの
   方針決定を待つか、Metaを先に試すか(上記方針(c)の追加evidenceにも
   なる)の判断を仰ぐ。

## §E2E Meta run_03(委任_13、2026-09-29、Meta単独をStandard/Advanced
両方ともProduction正式経路で完成)

ユーザー指示により、Hormuz(委任_09〜_12、run_01〜03で3回ともja_source
起因のMAJOR逸脱によりStandard段でSTOP)は**deferred/non-blockingとして
保留**し、本委任ではMetaのみを実行した。Standard側must-fix追加ルールの
新設・JA再生成回数の追加・Checker Prompt/severity/origin判定の変更は
一切行っていない。

### 事前確認(¥0)

- `git pull --ff-only`: no-op(既にup to date)。`git stash list`: 空。
- `grep -n "再び増やさない" er0*.py`: 2件、いずれもテストファイル
  (`assertNotIn`)のみでProduction module 0件(既知パターンと一致)。
- Meta `run_03/research_ledger/verified_fact_ledger.txt` sha256=
  `ea0ce587e605beeac8f02315ae4520899156393bbba2e059d99f45988b7c5f56`、
  `storyline_b3/fact_selection_evidence.json` sha256=
  `ff7873820e22f2d757728193ce97f671c7a192d83afd5f8d59e5053a7858c0a4`
  (前委任_12で複製済み分と完全一致、実測確認済み)。案B armed(JA writer
  runner起動ログで`fact_selection_evidence.json`存在を確認)。

### JA生成(run_03、実測)

- 実行: `TTS_EXECUTION_MODE=STANDARD` 環境変数明示、
  `er019_family_x_entertainment_production_runner_01.py --theme
  "Metaの音声アシスタントMuseの電話機能で人間契約スタッフが対応していた
  問題発覚とロールバック" --slug meta --out-dir er019_output/family_x_
  refresh_e2e_01/meta/run_03 --budget-jpy 40 --stage writer --stop-after
  writer`。research_ledger/storyline_b3は既存reuse(¥0、themeは
  research/storyline段が両方reuseのため機能上使われていない)。
- 結果: JA Original生成→Fact Check MAJOR 1件検知→must-fix retry 1回
  (既存仕様)→`overall_status="LEDGER_COMPLIANT"`。R1→R2→R2 Fact Check
  `overall_status="LEDGER_COMPLIANT"`(must-fix不要)。
- 実費用: ¥3.487(`ja_original`0.223+`ja_original_check`0.532+
  `ja_original_must_fix`0.636+`ja_original_check_retry`0.909+`ja_r1`
  0.411+`ja_r2`0.472+`ja_r2_check`0.303)。
- `verbatim_shas.concreteness_an3_block_sha256`=
  `067030ff53ecb76a4d1477a3deace07b3e1fac438a33cb873edbe045cf6927fe`
  (Hormuz run_02/03と完全一致、AN3-T0 Prompt不変の証拠)。
- 記号正規化違反: 0件(revision2.md実測)。段落数: 10(≥3充足)。

### Writer段(English、run_03)実行結果

- ledger段(reuse、¥0増分): `er012_e_family_entertainment_two_level_
  runner_01.py --ja-article <run_03>/ja_writer/revision2.md --slug meta
  --out-dir <run_03> --ledger-file <run_03>/research_ledger/verified_
  fact_ledger.txt --source-id FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01
  --budget-jpy 30 --stage ledger`。
- writer段: 同コマンドで`--stage writer`。
- **Advanced**: 1回目のDeviation Checkで`overall_status=
  "LEDGER_COMPLIANT"`(MAJOR無し、**案Bは発動していない**)。
  `<run_03>/b1b/article.md`・`parts.json`保存(`status="OK"`、
  `title="Some AI Phone Calls Had Humans Behind the Scenes"`、
  `paragraph_count=9`、`boundary_i/j=4/6`)。
- **Standard**: 1回目のDeviation Checkで**MAJOR 1件、origin=
  translation**(`claim_in_article="Also, some calls needed user
  information to continue."`)検知→既存must-fix retry 1回(ja_source
  起因ではないため案B対象外)→2回目`overall_status="LEDGER_COMPLIANT"`。
  `<run_03>/a2/article.md`・`parts.json`保存(`status="OK"`、
  `paragraph_count=9`、`boundary_i/j=3/6`)。
- 累計費用(JA+writer段合計、out-dir単位): ¥7.70。writer段の増分:
  約¥4.213。**STOPなし、新しいChecker仕様判断・未承認Prompt変更は
  発生していない**(既存承認済みretry範囲[Advanced 0回・Standard
  must-fix 1回]で解消)。

### Audio段(run_03)実行結果

構造上の発見(コード変更なし、ファイルコピーのみで対処): `er019_family_x_
audio_production_runner_01.py`の`source_dir`は`--slug`/`--run`のみから
`er019_output/{slug}/{run}`として導出され(`--out-dir`はAssembly先のみに
影響)、JA/writer段で使った`er019_output/family_x_refresh_e2e_01/meta/
run_03`とは別パスになる。外部pathを直接参照するCLI引数が無い構造上の
制約は、前委任までのresearch_ledger/storyline_b3コピー運用と同種のため、
同じ手法(コピーのみ、コード非変更)で対処した:
`er019_output/family_x_refresh_e2e_01/meta/run_03`の内容一式を
`er019_output/meta/run_03`へコピー(新規APIコール無し、¥0)。この経路
依存はHormuz再開時にも同様に発生する(Hormuz評価時の申し送り事項)。

- 実行(4段階、`--stage all`不使用、`TTS_EXECUTION_MODE=STANDARD`、
  `--tts-backend speech_metadata_flash_lite`、`--allow-legacy-backend`
  不使用):
  1. `er019_family_x_audio_production_runner_01.py --slug meta --run
     run_03 --level both --stage scaffold --tts-backend speech_
     metadata_flash_lite --budget-jpy 50` → ¥5.01。
  2. `--stage tts --budget-jpy 150` → 累計¥23.98(内訳
     `by_provider={'openai': 5.09, 'gemini': 15.58, 'openai_asr':
     3.31}`)、tts段増分約¥18.97。STOP/エラー/retry行0件(ログ全文で
     機械確認)。
  3. `--stage assemble --budget-jpy 10` → 増分¥0(API呼び出し無し)、
     両levelとも`status="OK"`、clipping無し。
  4. `--stage player`(`--tts-backend speech_metadata_flash_lite`) →
     `player.html`生成、増分¥0。
- Audio段合計: ¥23.98。**Meta E2E合計(JA+writer+Audio): ¥31.68**。

### Gate結果(Meta×Standard/Advanced、run_03、evidence付き)

Gate 13項目((a)〜(m))+Opus 9項目+ユーザー指定Gate 3項目、全てPASS
(evidenceは`er019_output/family_x_audio_production_wiring_01/
meta__run_03/{a2,b1b}/audit/tts_generation_results.json`等を実測)。

| Gate項目 | 結果 | evidence |
|---|---|---|
| Production wiring | PASS | `entry_point.json`: runner=`er019_family_x_audio_production_runner_01.py`、`tts_backend="speech_metadata_flash_lite"`、`allow_legacy_backend=false`。Trialファイル不使用 |
| runtime evidence(model/voice/style_prefix全文、reuse時master_audio_key) | PASS | 可変segment全21件(A2 11+B1B 10)で`model="gemini-3.8-flash-lite-tts"`実測、style_prefix全文記録。KP reuse時(b1b rank5)は`master_audio_key`記録あり |
| Standard/Advanced双方完成 | PASS | `a2/parts.json`・`b1b/parts.json`とも`status="OK"`、assembled mp3/wav生成済み |
| J3/E2 | PASS | japanese_title/preview/comment/full_story/in_one_lineのstyle_prefixが「落ち着いた、自然な話し言葉で…」(J3)、full_story/in_one_lineが英語版E2文言で実測一致 |
| Champion(固定shell10件) | PASS | a2 `shared_narration`10件全て`reused=true`、`master_audio_id`がREPORT §W2表と完全一致(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five/point_explanation)、TTS call 0 |
| 新記事構造(body1/2/3・Comment1〜4・Heading Readout不在・In One Line) | PASS | `timeline.json`実測: Comment1→Full Story Part1→Comment2→Part2→Comment3→Part3→Comment4→In One Line。`Heading`ラベル0件 |
| KP構造(Advanced: Phrase→英語解説[Variant B、Aoede]→同一Phrase) | PASS | rank1〜5全件で`explanation.voice="Aoede"`、`phrase_repeat.path/sha256`が`english`と完全一致 |
| KP構造(Standard: Phrase→日本語意味[J3]→同一Phrase) | PASS | rank1〜5全件`japanese_meaning.style_prefix`=J3文言。repeatは`english` wavをassembly段で2回使用(別JSONキー無し、既存設計どおり) |
| AN3-T0 | PASS | `concreteness_an3_block_sha256`がHormuz run_02/03と完全一致 |
| retry/fallback/regeneration | PASS(記録) | JA must-fix 1回(Original)、Standard writer must-fix 1回(translation origin)、案B発動0回(Advanced初回LEDGER_COMPLIANTのため不要) |
| pronunciation resolver | PASS(0トリガー) | 全segmentの`attempts_log[].reading_resolver_info`はnull(本記事では発音補正が必要な語が無かった。スキーマ上は有効のまま) |
| Audio Validation Gate PASS(ASSET_HASH_MISMATCH 0) | PASS | `run_summary_assemble.json`両level`status="OK"`(mismatch検知時は`BLOCKED_KP_SCAFFOLD_MISSING`等でreturnするが未発生) |
| player(2 episode行、Style全文) | PASS | `player.html`にa2/b1b各segmentのfile://リンクと ID を実生成確認 |
| Dangling Reference Check | PASS | `er019_output/family_x_audio_production_wiring_01/meta__run_03/`配下に`HEADING_READOUT`/`NG_ACCEPTED_AFTER_RETRY`の出現0件(grep実測)。旧`split_article_text()`は定義済みだが本runでは不使用(`split_family_x_article_text_v2()`のみ呼び出し) |

### 試聴ページ・Pages公開確認(7項目)

`user_test/family_x_refresh_e2e_01/index.html`(Meta Standard/Advanced
完成podcast、segment別style_prefix全文表示、KP構造表、Champion 10件表、
Deviation Check記録、費用表。Hormuzはdeferred/OPEN-233として明記し音声
非掲載)を作成、mp3 2本(`meta_standard.mp3`=3,528,624 bytes/
`meta_advanced.mp3`=3,452,760 bytes、`soundfile`によるMP3書き出し、
duration実測302.695s/283.480sでassembled wavと一致)を同ディレクトリへ
配置。commit `a6d4c64d`→push。typo(費用上限表記「900円上限」誤記)を
発見しcommit `44f7cacc`で修正・再push。

Pages公開確認7項目(全PASS):
1. HTTP 200: `curl -sI`で確認(反映まで約100秒)。
2. headless Chrome DOM dump: `chrome.exe --headless=new --dump-dom`で
   158行取得、内容確認。
3. `(existing 6-role value, unchanged)`: 0件(grep実測)。
4. Style Prompt全文実表示: 35箇所の`style_prefix`セルに省略・
   プレースホルダなしの全文確認。
5. audio player存在: `<audio`タグ2件(Standard/Advanced各1)。
6. mp3 200+decode: `curl -sI`で両mp3とも200、`soundfile`でdecode成功
   (duration実測が2つの完成episodeと一致)。
7. 表示Styleとmetadata一致: index.html生成スクリプトが`tts_generation_
   results.json`から直接読み込み・転記(手動転記なし)のため構造的に
   一致。

試聴URL: https://shimomura055.github.io/eigo-radio/user_test/family_x_refresh_e2e_01/index.html

### 費用(実測、Meta run_03累計)

| 段階 | 費用(JPY) |
|---|---|
| JA生成 | 3.487 |
| Writer段(Advanced+Standard、must-fix retry込み) | 4.213 |
| Audio scaffold | 5.01 |
| Audio tts | 18.97 |
| Audio assemble/player | 0.00 |
| **Meta合計** | **31.68** |
| 本管理ID累計(前委任までの約¥16.40と合算) | **約¥48.08** |

全体上限¥300に対し余裕あり。記事別Guardrail(JA¥40/EN¥30)・段階別
budget-jpy(scaffold¥50/tts¥150/assemble¥10)いずれも超過なし
(`assert_budget_ok`によるRuntimeError STOP発生0件)。

費用B(継続コスト差分、実測call数で裏付け): KP解説(Advanced)
+1 LLM call(rank1〜5まとめて)+5 TTS call(explanation×5、phrase_repeat
はreuseのため+0)。Phrase再掲(Standard)は+0(assembly段でenglish wavを
再利用、追加TTS call無し)。Heading Readout撤去により旧構成比−2segment
相当(本run自体はv2構造のみで生成のため差分は旧run比較の理論値)。Master
reuse(固定shell10件+KP一部)により当該分のTTS call 0。Comment 4本化は
新構造の既定(旧Point構成との比較は対象外)。案B発動は本Metaでは無し
(Advanced初回LEDGER_COMPLIANTのため+¥0)。

### Closeout 10項目充足状況(委任_13時点、SSOT反映は別途)

| # | 項目 | 状況 |
|---|---|---|
| 1 | Trial statusが分類済み | 該当なし(本委任はE2E、Trialではない) |
| 2 | UDRが提示済み | 該当なし(STOP無し、Meta完成) |
| 3 | 正式採用項目が追跡済み | 未到達(`PRODUCTION_WIRED`判定はFable Gate 3) |
| 4 | APPROVED→PRODUCTION_WIRED完了確認 | 未到達(Gate 3待ち) |
| 5 | initial/retry/fallback整合確認 | 確認済み(既存承認済みretry範囲内のみ使用、案B不要ケースも実データで確認) |
| 6 | runtime evidence取得 | 取得済み(本節の表・JSON・Pages 7項目) |
| 7 | SSOT整合 | 未実施(本委任はSSOT編集権なし、文案化はRESULT_PACKET側) |
| 8 | 未報告Trialが無いこと | 該当なし |
| 9 | 無断deferが無いこと | Hormuz deferredはユーザー指示によるもの(無断ではない)、明記済み |
| 10 | 次タスクへの持ち越し事項明示 | 下記参照(Hormuz方針、`er019_output/meta/run_03`コピー運用の申し送り、Fable Gate 3判定待ち) |

### 次工程への申し送り

1. Hormuz(run_01〜03のevidence保持、Standard段STOPPEDのまま)は
   ユーザー指示によりdeferred/non-blocking。再開時は本委任と同じ
   `er019_output/{slug}/{run}`コピー手順が必要になる(Audio runnerの
   `source_dir`導出仕様、上記参照)。
2. Meta単独ではGate 3判定に必要な13+9+ユーザー指定Gate全てPASSしたが、
   `PRODUCTION_WIRED`化はFableのGate 3判断次第。Hormuz未完了が
   Gate 3のどの条件に抵触するかはRESULT_PACKETで事実列挙する(条件
   緩和はしていない)。
