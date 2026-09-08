# OPEN-124-UNTRACKED-FILES-CLASSIFICATION-01 — 古い未追跡ファイルの分類・正体確認

**管理ID: OPEN-124-UNTRACKED-FILES-CLASSIFICATION-01**
**日付: 2026-09-08**
**性質: 読み取り専用の分類作業。削除・移動・commit・`.gitignore`変更は一切実施していない。**

## 0. 用語

- 「未追跡(`??`)」= `git status`でGit管理下に入っていないファイル/ディレクトリ
- 「変更(` M`)」= 既にGit管理下にあり、内容が変更されたファイル
- 本Reportの分類・件数・サイズは`git status --short`実行時点(2026-09-08)のスナップショット

## 1. 件数の照合

`git status --short`の全件: 296行(` M` 5件 + `??` 291件)。

`??` 291件のうち、**本日(2026-09-08)進行中の別タスク**
(`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md`、
`er012_b_family_*.py` 3件、`er012_editorial_b_family_production_phase1_test_01.py`、
`er012_output/editorial_b_family_production_phase1_01/`)の**6件**は
mtimeが本日10:06〜10:40に集中しており、OPEN-124の対象外(進行中タスク別枠)。

**291 − 6 = 285件。OPEN_ITEMS.md OPEN-124行の「285件」と完全一致。**
差分なし(理由推定は不要)。今回発見した本日分の新規ファイルは、この6件の
進行中タスク関連分のみであることをmtime全件確認で検証済み。

対象: **285件(実ファイル数1,003件、合計約2,870MB)**。

## 2. 分類結果(サイズ・件数)

| 分類 | 上位グループ数 | 実ファイル数 | 合計サイズ |
|---|---|---|---|
| (A) 正式成果物(Report/ARTIFACT_REGISTRY等で完成・採用と確認できる) | 86 | 293 | 約520.5MB |
| (B) Trial/diagnostic evidence(Reportで参照されているが正式成果物ではない) | 185 | 648 | 約2,332.5MB |
| (C) Git管理不要の生成物候補(tmp作業ディレクトリ) | 2 | 35 | 約0.3MB |
| (E) 所属管理ID不明(どのReport/SSOTからも参照なし) | 10 | 12 | 約16.5MB |
| (F) commit漏れ候補(上記(A)以外で、参照はあるが未追跡) | 2 | 15 | 約0.4MB |
| **合計** | **285** | **1,003** | **約2,870.1MB** |

**重要な注記**: (A)「正式成果物」は同時に「commit漏れ候補」でもある(正式に
完成・採用されたと記録されているのに未追跡のため)。分類上は識別(何であるか)
と対応(commitすべきか)を分けて記載する。

## 3. 拡張子別サイズ(全1,003ファイル)

| 拡張子 | 件数 | サイズ | 備考 |
|---|---|---|---|
| wav | 212 | 2,623.8MB | **既に`.gitignore`の`*.wav`ルールで対象外**(commit対象にはならない) |
| mp3 | 81 | 174.8MB | `.gitignore`対象外指定なし。ただし既存tracked mp3も29件あり(混在) |
| html | 7 | 44.9MB | player系(音声base64埋め込み推定)。既存tracked html playerも26件あり(混在) |
| webm | 6 | 22.2MB | `.gitignore`対象外指定なし。tracked webmは0件(前例なし) |
| json | 493 | 3.0MB | metadata/audit/QAログ |
| md | 84 | 0.4MB | article本文・review記録 |
| txt | 54 | 0.4MB | prompt等 |
| jsonl | 19 | 0.4MB | append-onlyログ |
| py | 27 | 0.2MB | 診断・生成スクリプト |
| log | 11 | 0.1MB | 実行ログ |
| textgrid, bak | 9 | <0.1MB | MFA alignment出力、editorバックアップ |

**合計2,870.1MBのうち約99.8%(2,865.7MB)がwav/mp3/webm/html(音声・動画・
プレイヤー)で、残り約4.4MBがjson/md/txt/py/log等のテキスト**。wavは既に
`.gitignore`対象外のため実質的な「今後commitするかどうかの判断が必要な
サイズ」は約246MB(mp3+webm+html)。

## 4. 分類の根拠となった主な発見(グループ単位)

### (A) 正式成果物・commit漏れの可能性が高いもの

| グループ | 件数/サイズ | 根拠 |
|---|---|---|
| `er003_output/n3_01/{hanshin,health,household}/{a2,b1b}/assembled/` | 12件/364.6MB | `ARTIFACT_REGISTRY.md`にPASS/REVIEW_REQUIRED記載、本番article対応の完成音声 |
| `er006_output/pool_pilot_01/pool_n8_airport_line/` | 85件/145.9MB | `DECISION_LOG.md`の`ER-008-N8-*`系列(15〜24)で詳細記録、Pool Topic No.8完成・ユーザーへArtifact提供済み。**ただし`POOL_TOPIC_MASTER.md`のNo.8列は現在も`PLANNED`のまま**(本タスクの範囲外の別の不整合として観測のみ、修正はしていない) |
| `er011_output/open112_trend_theme2_b_final_audio_rerun_04/` | 60件/26.5MB | commit `44d1abf`(本日)で`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`が「Theme2 B1 rerun_04正式採用」と記録済みだが、**同commitは音声ファイル自体を含んでいない**(SSOT記載のみ先行、実データ未commit) |
| `er002_output/A01/v1_1a/`、`v1_2m_j1/`、`v1_2m_r1/`、`v1_2m_r2/` | 134件/0.34MB | `.gitignore`内の既存コメントで「er002_output/配下は原則Git追跡する」と明記された方針に反して未追跡 |
| `ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md`、`ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md` | 2件/0.08MB | Report本体そのもの。OPEN_ITEMS.md OPEN-124行が既知項目として明記 |

### (B) Trial/diagnostic evidence(代表例)

- `er003_output/{p1,p1b,p2,p2d,p2e,p2f}/` + `er003_v1_p2*.py`(280+5件、約1.8MB): ER-003初期開発フェーズ(P1/P1B/P2)。`ARTIFACT_REGISTRY.md`/`HISTORY_INDEX.md`/複数ER-003 Reportで参照される歴史的段階のテキストのみ(wav/mp3なし)。後続フェーズ(STRUCT/SPOKEN-FIRST等)に置き換えられた可能性が高いが削除はしていない
- `er003_output/{a2_audio_01,a2_audio_02,a2_audio_ab_01,b1_scaffold_audio_01/02/03,crosslevel_audio_02,novel_audio_01,novel_audio_02,b1redesign_audio_01,b1_p9a,b1_p4c}/`: 各`ER-003-*-AUDIO-*_REPORT.md`系列で参照される反復試行版(数字違いの複数世代)。合計約1,235MB。既にaudit/metadata側は大半がGit追跡済みで、`assembled/`(音声実体)のみ未追跡という一貫パターンを確認
- `er003_output/n3_01/root_fix_01_regression/`(8件、約21KB): `ARTIFACT_REGISTRY.md`/`DECISION_LOG.md`に明記「regression検証のみ、本番article.mdには未反映」
- `er005_output/{cost_baseline_01,e2e_tts_cost_quality_01,audio_validation_robustness_02}/`: 対応するER-005 Report群で参照
- `er006_output/pool_pilot_01/{pool_n18_notifications_specfix_v2,pool_n18_notifications_specfix_v2_ec_a_precision_21r,pool_n9_tip_screens/human_review_mp3}/`: ER-011/OPEN-112/ER-010系Reportで参照される反復試行版・Human Review試聴用evidence
- `er009_output/*` + `er009_*.py`(約20件、0.4MB未満): `DECISION_LOG.md`の`ER-009-N1-*`系列(02〜14)・`ER-009-JA-FOREIGN-TOKEN-GATE-01`で参照
- `er011_output/{no18_tight_speech_only_removal_trial_15,open117_keyphrase_tilde_gate_recheck_01,assembly_headroom_wiring_01}/`、関連`*_run.log`: 対応するER-011/OPEN-117/OPEN-113 Reportで参照

### (C) Git管理不要の生成物候補

- `er006_output/_adhoc_verify_tmp/`、`er006_output/_test_debug_tmp/`(35件、0.28MB): ディレクトリ名自体が一時作業を明示。どのReportからも参照なし

### (E) 所属管理ID不明(どのReport/SSOTからも参照が見つからなかったもの)

| ファイル | サイズ | 備考 |
|---|---|---|
| `er006_output/pool_pilot_01/adoption_audit_01/review_data.json`+`review_html/` | 16.27MB | 生成元と推定される4本の`.py`スクリプト(`er006_pool_adoption_audit_01_*.py`)はGit追跡済みだが、スクリプト自体もこの出力自体もどのReportからも参照されていない。`ER-006-POOL-ADOPTION-AUDIT-01_diff.md`という類似名のファイルは存在するが内容は別トピック(pool_benches/subscriptions/startups)で無関係 |
| `notification/universfield-new-notification-07-210334.mp3` | 0.06MB | 外部素材と推定されるSFXファイル。参照なし |
| `scratch_comment_2.mp3`、`scratch_tail.txt`、`trial07.log`、`trial08.log`、`test_stderr.log`、`word_ts_check.json` | 各0.1MB未満 | ファイル名自体がscratch/trial/test系。参照なし |
| `er011_output/25_full_regression.log` | 0.02MB | mtimeは2026-09-04だが対応するReportの特定に至らず |

### (F) commit漏れ候補(所属は明確、未追跡)

- `test_writer_api.py`(1KB): `DECISION_LOG.md`/`ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01_REPORT.md`で参照
- `er010_output/no9_function_word_reduction_production_wiring_27/runtime_evidence/`(14件、0.37MB): `DECISION_LOG.md`のPRODUCTION_WIRED記載を裏付けるruntime evidence

## 5. `M`(変更・5件)の扱い

| ファイル | 変更内容 | 種別 |
|---|---|---|
| `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl` | 1行追加 | Human Review Queue(append-only) |
| `er006_output/master_audio_store_01/manifest.json` | 720行追加 | Master Audio Store manifest |
| `er006_output/master_audio_store_01/reuse_telemetry.jsonl` | 117行追加 | 再利用テレメトリ(append-only) |
| `er006_output/pronunciation_ledger_01/ledger.json` | 30行追加 | Pronunciation Ledger |
| `er011_output/attempt_history.jsonl` | 1,585行追加 | TTS試行履歴(append-only) |

全て**追記のみ(削除・上書きなし)**、既存安全機構(Retry Cascade/Master Audio
Store/Pronunciation Ledger/Human Review Lock)の副作用ログ。mtimeは
2026-09-07〜09-08で、一部(`reuse_telemetry.jsonl`10:42、`attempt_history.jsonl`
10:47)は本日進行中の別タスク(er012 phase1)の実行時間帯と重なる。
OPEN-124の「285件の古い未追跡ファイル」には含まれない別項目であり、通常の
Production運用ログとして**commitに適した低リスクな変更**と判断できるが、
実際のcommitは本タスクの範囲外(読み取り専用)のため実施していない。

## 6. 次アクション候補(提案のみ、実行なし)

1. **`.gitignore`追加候補**: `*.mp3`/`*.webm`および`assembled/**/player*.html`を
   `*.wav`と同様に対象外にするか検討(既存29件のmp3・26件のhtml playerは
   既にtracked済みで前例が割れているため、方針統一が必要)。**判断が割れる
   ため、削除・.gitignore変更を伴う対応は`USER_DECISION_REQUIRED`とする**
2. **commit漏れ候補のcommit案**: 上記(A)5グループ+(F)2グループ(計約521MB、
   うち大半はwav/mp3で.gitignore方針次第で対象範囲が変わる)。特に
   `er011_output/open112_trend_theme2_b_final_audio_rerun_04/`は「正式採用」と
   既にSSOTに明記済みのため優先度が高い
3. **削除候補(実行しない、提案のみ)**: (C)の2 tmpディレクトリ(0.28MB)、
   (E)所属不明の10件(16.5MB、うち`adoption_audit_01`が大半)。特に
   `adoption_audit_01`はサイズが16MBあり生成元スクリプトも追跡済みのため、
   削除前に旧担当への出自確認が望ましい。**削除は`USER_DECISION_REQUIRED`**
4. **(B)Trial/diagnostic evidence(約2,332MB)**: 削除するか歴史的記録として
   残すかはユーザー判断が必要(`USER_DECISION_REQUIRED`候補)。多くは既に
   audit/metadata側がGit追跡済みで、`assembled/`音声実体のみ未追跡という
   一貫パターン
5. **観測のみ(対応不要・本タスク範囲外)**: `POOL_TOPIC_MASTER.md`のNo.8
   (Airport Line)列が`PLANNED`のまま、実際は完成・ユーザー提供済みという
   ドキュメント不整合を発見。修正は別タスクとして起票が必要

## 7. 使用したコマンド(再現用)

`git status --short`、`git diff --stat -- <file>`、`git show --name-only`、
`git check-ignore -v`、`git ls-files`、`grep -rl`(各種`*.md`ファイル横断)、
`find`/`stat`/`du`(サイズ集計)。削除・移動・編集・`.gitignore`変更・
`git add`/`commit`は一切実行していない。
