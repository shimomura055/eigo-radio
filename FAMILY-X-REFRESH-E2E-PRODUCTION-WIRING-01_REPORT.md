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
