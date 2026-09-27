# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01_REPORT

## Phase 0: SSOT反映+配線設計(2026-09-27)

性質: ¥0。API呼び出し0件。Production code変更0件。SDK更新0件。実装は
次Phase(本REPORT末尾のGate 3チェックリスト参照)。

### 背景

ユーザーは2026-09-27、Gemini 3.8 Flash-Lite TTS(`gemini-3.8-flash-lite-
tts`、`speech_metadata`構造化方式)のProduction採用を正式決定した
(Family Xから段階導入、Status `VALIDATED` → `APPROVED_FOR_PRODUCTION`。
`PRODUCTION_WIRED`ではない)。詳細な決定内容・比較材料は`TTS-GEMINI-3.8-
FLASH-LITE-NEXT-TRIAL-01_REPORT.md`(§14-§23)および`docs/pm/flash_lite_
production_adoption_packet_01.md`(A〜I)を参照。本Phaseはこの決定を
SSOTへ反映し、Production配線の詳細設計を行った。

### 実施内容

1. **SSOT反映**: `CURRENT_SPEC.md`(「Gemini 3.8 Flash-Lite TTS」行を
   `APPROVED_FOR_PRODUCTION`へ更新、`PRODUCTION_WIRED`未到達・Family X
   先行・A/B/C対象外・Z別判断・6-role初期仕様を明記)、`DECISION_LOG.md`
   (新規エントリ、ユーザー決定16項目の必須確認事項を記録)、
   `OPEN_ITEMS.md`(OPEN-201をGate 3配線追跡へ切替、Production採用可否の
   USER_DECISION_REQUIREDを解除)、`docs/pm/REPORT_LEDGER.md`(新規管理
   ID行)。
2. **配線設計書**: `docs/pm/design_flash_lite_family_x_wiring_01.md`
   新規作成(a〜kの11節、Family X実関数チェーンの特定、retry/fallback/
   regenerationの同一関数経由確認、pronunciation resolver統合設計、
   role別style定数の位置、SDK導入計画、model routing、regression
   fixture化、公平cost比較計画、rate limit確認計画、実装Phase分割案)。

### 主要な設計上の発見(次Phase実装の前提として重要)

- `generate_charon_english`/`generate_english_segment_with_fallback`/
  `generate_a2_japanese_with_fallback`/`generate_charon_japanese`は
  **Family A/B/C(legacy)からも呼ばれる共有関数**であるため、内部を
  無条件でspeech_metadata方式へ置き換えると「Family X先行、A/B/C対象外」
  というユーザー決定に反してlegacy Familyの挙動まで変わってしまう。
  対策として、既存の`enable_pronunciation_resolver=True`(Family X
  runnerのみが明示的に渡す既存パターン)と同型の、新規opt-in引数
  (`tts_backend`)を追加する設計とした(設計書§a-3)。
- `er006_model_routing_contract_01.require_provider("TTS", ...)`は
  現状どのProduction call siteからも呼ばれておらず未配線であることを
  Grepで確認した(設計書§g)。TTS routing契約の構造自体を変える必要は
  ない。
- Pronunciation resolverは英語側(style_prefixへのhint注入)・日本語側
  (text自体への表記置換)で仕組みが異なり、英語側はspeech_metadata.
  styleへの移行と矛盾しない(text不変の原則を保ったまま)。日本語側は
  speech_metadata方式と無関係な層のため変更不要(設計書§c)。
- `_generate_a2_japanese_minimal_instruction()`は上記4共有関数と異なる
  独立コードパスであり、fallback対応のためこのヘルパーにも個別に
  opt-in分岐が必要(見落としやすい箇所として設計書§bに明記)。

### USER_DECISION候補(新規、設計書末尾に詳細)

1. A2 6% slowdown post-processの適用方針(そのまま適用して実測するか、
   A2は別Phaseへ先送りするか)。
2. 公平な1回完成cost比較(新規記事での実測)の実施タイミングと承認範囲。
3. rate limit確認(Phase 3の逐次運用)の報告粒度。

### Gate 3チェックリスト(空欄、次Phase以降で1件ずつ埋める)

| # | 項目 | 状態 |
|---|---|---|
| 1 | Production正式初回pathへのspeech_metadata方式実装 | 未着手 |
| 2 | retry・fallback・regenerationでの同一実装経由 | 未着手 |
| 3 | Human Review Lockとの整合 | 未着手 |
| 4 | Pronunciation・Reading Resolverとの統合 | 未着手(設計は完了、実装は次Phase) |
| 5 | voice指定 | 未着手(設計は完了、変更不要と判断) |
| 6 | role別style正式仕様化(6-role) | 未着手(定数モジュール新設が必要) |
| 7 | A2 6% slowdown post-processとの関係 | 未着手(USER_DECISION候補あり) |
| 8 | ASR validation流用 | 未着手(設計は完了、変更不要と判断) |
| 9 | cost ledger・telemetry正式統合 | 未着手(設計は完了、既存cl.segment_contextで自動記録される見込み) |
| 10 | SDK 2.25.0 Production `.venv`導入 | 未着手 |
| 11 | フル回帰(3300+件規模) | 未着手 |
| 12 | 実際のmodel_id・routing runtime evidence | 未着手(設計は完了、result["model"]既存フィールド流用) |
| 13 | rate limit・concurrency確認 | 未着手 |
| 14 | Act One型digit読みのregression fixture化 | 未着手 |
| 15 | 現行モデルとの公平な1回完成cost比較 | 未着手(USER_DECISION候補あり) |
| 16 | rollback可能性確認 | 設計完了(2段階rollback案: SDK pin戻し+tts_backend切替) |

### STOP該当

無し(Phase 0の範囲はSSOT反映+設計のみ、コード変更・API呼び出しを
伴わない)。

### 参照

`docs/pm/flash_lite_production_adoption_packet_01.md`、`TTS-GEMINI-3.8-
FLASH-LITE-NEXT-TRIAL-01_REPORT.md`(§14-§23)、`docs/pm/design_flash_
lite_family_x_wiring_01.md`、`DECISION_LOG.md`本管理ID冒頭エントリ、
`OPEN_ITEMS.md` OPEN-201。
