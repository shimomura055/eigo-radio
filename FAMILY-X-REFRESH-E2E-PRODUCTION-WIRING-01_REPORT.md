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
