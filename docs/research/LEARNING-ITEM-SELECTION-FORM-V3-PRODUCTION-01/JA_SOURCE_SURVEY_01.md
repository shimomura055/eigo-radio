# JA_SOURCE_SURVEY_01 日本語訳・AI選定理由の出所調査(委任_02、2026-10-27、API 0・read-only)

## 1. 結論
- **エンドユーザー提供予定の日本語訳 = 候補doc `kp_candidates.json` の `candidates[].japanese_gloss`**(Key Phrase/Key Wordの日本語意味。gloss整合Gate通過後の値)。新規生成は不要。フォームの `ja_gloss`(= 既存 `meaning_ja`)はこの値の**逐語コピー**(test: `test_form_data_reuses_existing_gloss_and_reason_verbatim`)。
- **AI選定理由 = `candidates[].reason_ja`**。ただし **call1(Prompt 2)は理由を出さない**(`er119_kp_candidates_01.py:342` `reason_ja: ""`)。理由を出すのは call2(`:346`)と補完 backfill(`:490`)のみ。call1候補は「理由なし(仕様)」と明示表示する。
- 仮訳を正式訳にしない: `ja_gloss_status` = `official`(Production正式経路 + `gates.gloss`がALIGNED/HUMAN_RESOLVED + gloss HR待ちなし) / `provisional`(gloss HR待ち・DEV Trial・replay由来) / `missing`(未生成)。

## 2. 項目対応(`DATA_CONTRACT_01.md:13,15,18,23`、`er119_kp_candidates_01.py:249-265,569-573`)
| フォーム項目 | 元項目 | 備考 |
|---|---|---|
| `ja_gloss`(=`meaning_ja`) | `japanese_gloss` | gloss再整合/救済後の値。HR gloss待ち=`flags.gloss_hr_pending`(`er119_kp_candidates_01.py:265`)で`provisional`。HR解消は`op_resolve_gloss`(`er119_kp_human_review_01.py:803-841`、`gates.gloss="HUMAN_RESOLVED"`)で`official`扱い |
| `ja_gloss_status` | `gates.gloss`+`flags.gloss_hr_pending`+`source.kind` | `export_form_data_01.py: gloss_status()` |
| `reason_ja`, `reason_source` | `reason_ja`, `origin` | `ai_call2`/`ai_backfill`/`none_call1_has_no_reason`/`none_placeholder_not_real`(replay fixtureの`replay`文字列は理由として出さない)/`none_not_generated` |
| 文法 | Part 2候補(解説全文は選定後生成) | 現状は全記事 `grammar:[]`=「未生成」と明示(仮データなし) |

## 3. 公開ページで実際に出る日本語意味との同一性
- 元は同じ `japanese_gloss`。ただし各所の最終表示は決定論的派生を挟む(**差異あり。確認事項**):
  - X Standard: 音声は `japanese_gloss`(`er019_family_x_audio_production_runner_01.py:2141` `display_gloss=item["japanese_gloss"]`、`:2924` `JA: {kp['japanese_gloss']}`)、証跡ページは `japanese_gloss_tts`(読み用の規則変換、`er003_key_words_canonicalization.py:246-253,871`、`er003_key_words_gloss_alignment.py:967,1285`)。
  - Y Standard: ページは `japanese_meaning.canonical_text` を優先、無ければ `japanese_gloss`(`er121_family_y_audio_01.py:1504`、`er110_family_y_audio_page_01.py:65`)。
  - Z: TTSは `japanese_gloss_tts or japanese_gloss`(`er063_family_z_audio_01.py:593`)。
  - Advanced(b1b)のKPページは日本語意味ではなく英語解説(P7)。`japanese_gloss`は③本文意味表示/HR gloss用。
- フォームは派生前の `japanese_gloss`(表記上の正)を表示する。「ユーザーが確定した日本語訳」を後工程で固定する対象は、この `japanese_gloss` と、そこから決定論的に派生する `japanese_gloss_tts`/`canonical_text` の整合を要す(並行委任KP-CONFIRMED-CONTENT-PROTECTION-01の保護設計で扱う論点。本委任は変更しない)。

## 4. 記事別の採否(再生成0)
| データ | source.kind | 日本語訳 | AI理由 |
|---|---|---|---|
| ai_island_temple a2/b1b, redelivery a2/b1b, melos a2(`*_prod`) | PRODUCTION_FORMAL_PATH | 全件 `official` | call1=なし(仕様)、call2/backfill=あり |
| monkeys_paw_prod b1b | REPLAY_FROZEN_INITIAL_REAL_BACKFILL | 全8件 `provisional`(replay由来) | call1=なし、call2は`replay`仮文言のため非表示(`none_placeholder_not_real`) |
| monkeys_paw b1b(Trial-02) | DEV_TRIAL | 全11件 `provisional` | Trial-02 `trial_result.json`のcall2 4件の`reason_ja`を再利用(`RESULT_02.md`の選定理由列と同値)、call1=なし |
| ui_check_dummy | UI_CHECK_DUMMY | 旧`meaning_ja`のみ → `provisional`扱い | なし |
