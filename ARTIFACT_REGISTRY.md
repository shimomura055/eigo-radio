# ARTIFACT_REGISTRY — 記事×CEFRレベルの成果物完成状態

**管理ID: ER-PM-001**
**最終更新: 2026-08-17(ER-003-B1-A2-SPEC-FREEZE-01-R1、SoT内部整合性クリーンアップ)**

記事×CEFRレベルごとの成果物完成状態を一覧化する。値はすべて監査証拠
(commit・manifest・report)に基づく。**推測で埋めた値はない。** 不明な
場合は`NOT_REVIEWED`/`未着手`等、事実に基づく状態を記載する。

`user_quality_status`(試聴品質)と`publication_status`(公開承認)は
必ず分離する(詳細は[PROJECT_INDEX.md](PROJECT_INDEX.md)参照)。

**`PASS`の意味についての注意(2026-08-12追記、ER-003-A2-SCRIPT-FINAL-01で
更新)**: 表内の`PASS`は「現行採用版が該当QAゲート・ユーザー試聴を
通過した」ことを意味する。**Script列**は、ER-003-A2-SCRIPT-FINAL-01
(2026-08-12)でOPEN-31のSHOULD_REVISE候補5件をすべて最終台本へ反映し、
6観点Naturalness QAに合格したことを示す(OPEN-31は`DECIDED / CLOSED`)。
ただし**Podcast組立列**が示すとおり、既存の完成音声はこのscript確定
より前に生成されたものであり、**台本と音声の内容が一致していない**
(音声側は旧文言のまま、[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-35で
再assemble待ちとして追跡中)。
**User Quality列の`PASS**`(A02)は、ER-003-A2-AUDIO-AB-01での通し
試聴による総合判断("A2の完成候補は全体としてOK")を指すが、この判断は
**script確定前の旧音声**に対するものであり、文単位のNaturalness QA
網羅を保証するものでもない。

| Article | Level | Source | Script | Preview | Key Phrase | Full Story | Podcast組立 | User Quality | Publication |
|---|---|---|---|---|---|---|---|---|---|
| A01 | CEFR-B2 | PASS | PASS(自動QA合格。ユーザーによる本文単独の明示承認記録なし) | N/A | N/A | 未生成 | 未生成 | NOT_REVIEWED | NOT_APPROVED |
| A01 | CEFR-B1 | PASS | PASS | PASS | PASS(5件) | PASS | PASS(r2が最終版) | NOT_REVIEWED(部分的な「修正箇所承認」は複数あるが、最終r2版の通し試聴OKは未記録) | NOT_APPROVED |
| A01 | CEFR-A2 | PASS(A2-03独立生成) | **PASS**(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で最終台本確定。旧OPEN-31の3件すべて反映済み、6観点Naturalness QA PASS。[DECISION_LOG.md](DECISION_LOG.md)参照) | PROTOTYPE_BUILT(Cross-level原則反映、ただしPause 0.8秒・Outro最新減衰・Key Phrase 3条件発音・In One Line見出し修正は未反映のER-003-CROSSLEVEL-AUDIO-02版のまま) | PROTOTYPE_BUILT(方式L+Canonicalizationで新規選定5件、機械QA合格。3条件発音方式は未適用) | PROTOTYPE_BUILT(機械QA合格、hallucinationなし) | PROTOTYPE_BUILT(294.2秒、clippingなし)。**再assemble要**(Cross-level最新仕様=Pause0.8秒/Outro最新減衰/Key Phrase3条件/In One Line見出し修正が未反映[OPEN-34]、**かつ2026-08-12のscript確定により台本と不一致[OPEN-35]**) | NOT_REVIEWED | NOT_APPROVED |
| A02 | CEFR-B2 | PASS | PASS(自動QA合格。ユーザーによる本文単独の明示承認記録なし) | N/A | N/A | 未生成 | 未生成 | NOT_REVIEWED | NOT_APPROVED |
| A02 | CEFR-B1 | PASS | PASS | PASS | PASS(5件) | PASS | PASS | **PASS**(ER-003-REPRO-01、2026-08-08) | NOT_APPROVED |
| A02 | CEFR-A2 | PASS(A2-03独立生成) | **PASS**(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で最終台本確定。旧OPEN-31の1件を反映済み。Natural English Sourceとの意味一致を確認の上採用、Naturalness QA PASS。[DECISION_LOG.md](DECISION_LOG.md)参照) | PASS(Cross-level原則反映済み、ER-003-CROSSLEVEL-AUDIO-01) | PASS(3条件発音方式を5件へ適用済み、ER-003-A2-AUDIO-AB-01) | PASS(機械QA合格、hallucinationなし、In One Line見出し修正済み) | PASS(A/B版とも最新Cross-level仕様を全反映、310.5秒[A]/329.3秒[B]、clippingなし)。**ただし2026-08-12のscript確定により台本と不一致、再assemble要(OPEN-35)** | **PASS**\*\*(ER-003-A2-AUDIO-AB-01、2026-08-12。「A2の完成候補は全体としてOK」という通し試聴での総合判断だが、**この音声は script確定前の旧文言を含む**。文単位のNaturalness QA網羅を意味しない) | NOT_APPROVED |
| ADD03 | CEFR-B2 | あり(日本語下書きのみ、英語台本なし) | 該当なし | N/A | N/A | 未生成 | 未生成 | NOT_REVIEWED | NOT_APPROVED |
| ADD03 | CEFR-B1 | PASS | PASS | PASS | PASS(5件) | PASS | PASS | **PASS**(ER-003-REPRO-FINAL、2026-08-09。meaning_3はASR homophone ambiguityとして人間確認済み、TTS音声は正常) | NOT_APPROVED |
| ADD03 | CEFR-A2 | PASS(A2-03独立生成) | **PASS**(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で最終台本確定。旧OPEN-31の1件(Brent原油価格段落の時系列flashback構造)を7/13→7/14の実時系列順へ再構成、新規事実の追加なし、Naturalness QA PASS。[DECISION_LOG.md](DECISION_LOG.md)参照) | PROTOTYPE_BUILT(Cross-level原則反映、ただしPause 0.8秒・Outro最新減衰・Key Phrase 3条件発音・In One Line見出し修正は未反映のER-003-CROSSLEVEL-AUDIO-02版のまま) | PROTOTYPE_BUILT(方式L+Canonicalizationで新規選定5件、機械QA合格。3条件発音方式は未適用。**「Brent crude oil」キーフレーズの根拠文は台本確定後も文言としてそのまま残存**) | PROTOTYPE_BUILT(機械QA合格、hallucinationなし) | PROTOTYPE_BUILT(327.4秒、clippingなし)。**再assemble要**(A01と同じくCross-level最新仕様が未反映[OPEN-34]、**かつ2026-08-12のscript確定により台本と不一致[OPEN-35]**) | NOT_REVIEWED | NOT_APPROVED |

## N3-01: 3ジャンル横展開検証(Hanshin/Health/Household、B1-B/A2、2026-08-17更新)

以下は、Support-based Natural English設計(現行B1正式仕様)・B1-B Direct
Generation・A2 Core Explanatory Logic Preservationを使った、P-seriesとは
別系統の記事群。**PROTOTYPE / N-INCREASE VALIDATION**という位置づけで
制作され、CURRENT_SPEC.mdの現行B1/A2仕様の検証根拠になっている。

**「User Quality」列の注意**: 以下`NOT_REVIEWED`は、機械QA(ASR文字起こし・
波形解析等の技術的検証)は完了しているが、人間による通し試聴(プロジェクト
責任者を含む)がまだ記録されていないことを意味する。「開発者が試聴した」
という意味ではない(2026-08-17 SoT Consistency Cleanupで表現を訂正)。

| Article | Level | Ledger/Fact QA | Full Audio | Root Cause Fix適用状況 | User Quality | Publication |
|---|---|---|---|---|---|---|
| Hanshin | B1-B | PASS/LEDGER_COMPLIANT | 完成(clippingなし) | ROOT-FIX-01のコード変更(trim margin・instruction分離)後、**本番音声は未再生成**(コード変更は今後の新規生成から適用) | `NOT_REVIEWED`(機械QAのみ完了、人間試聴未記録) | NOT_APPROVED |
| Hanshin | A2 | PASS/LEDGER_COMPLIANT | 完成(clippingなし) | 同上。加えてA2 Core Logic Preservation原則は単発regression生成でのみ検証済み(`root_fix_01_regression/hanshin_a2_sidecheck/`)、本番article.mdへの反映は未実施(副作用なしの確認のみが目的だったため) | `NOT_REVIEWED` | NOT_APPROVED |
| Health | B1-B | PASS/LEDGER_COMPLIANT | 完成(clippingなし)。FIX-01でkp4_ja_charon「modeled differences」のinstruction leakageを修正・再assemble済み | 同上(コード変更後の本番再生成は未実施) | `NOT_REVIEWED` | NOT_APPROVED |
| Health | A2 | PASS/LEDGER_COMPLIANT | 完成(clippingなし)。FIX-01でkp4_en「follow-up time」の頭切れを修正・再assemble済み | 同上 | `NOT_REVIEWED` | NOT_APPROVED |
| Household | B1-B | PASS/LEDGER_COMPLIANT | 完成(clippingなし)。FIX-01時点から内容変更なし | 対象外(A2固有の不具合だったためB1-Bは無変更) | `NOT_REVIEWED` | NOT_APPROVED |
| Household | A2 | **REVIEW_REQUIRED**(2026-08-17 SoT Consistency Cleanupで訂正: `household/a2/fact_qa.json`の実際の最終記録値は`PASS`ではなく`REVIEW_REQUIRED`。指摘内容はPoint Two周辺の精度[バナナの追熟段階、ジャガイモ/サツマイモの最適湿度]で、今回の修正対象[fruit/vegetable二分法]の範囲外かつB1の同等表現と同水準と判断し、記録の上で許容[`er003_output/n3_01/household/a2/audit/fix01_fact_checker_acceptance_note.json`参照]。無限再生成はしていない)/LEDGER_COMPLIANT | 完成(clippingなし)。FIX-01でJapanese title のinstruction leakageとfruit/vegetable二分法を手動編集で修正・再assemble済み | **本番article.mdはFIX-01の手動編集版のまま。ER-003-N3-ROOT-FIX-01で正式採用したA2_KAI1_INSTRUCTION(Core Logic Preservation原則入り)による再生成は未実施**(→[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-41) | `NOT_REVIEWED` | NOT_APPROVED |

**Artifact URL**(開発者向け試聴用、非公開): Hanshin/Health/Householdの
各テーマ比較ページ(詳細はER-003-A2-B1-N3-01完了報告・FIX-01完了報告を
参照)。

## 補足

- **A01のCEFR-B2「Source」がPASSとなっている理由**: A01のCEFR-B2は
  ER-003のNatural English Sourceから生成されたテキスト
  (`er003_output/p2/A01/b2_version_raw.md`)であり、ER-002時代の
  破棄された旧台本(`er002_output/A01/script_en.json`)とは別物。
  ER-002旧台本については[HISTORY_INDEX.md](HISTORY_INDEX.md)を参照。
- **「Podcast組立」列**: Intro/Outro/notification等を含む、番組として
  接続済みの完成候補の有無を指す。CEFR-B1のみ存在(3記事とも)。
- **A01 CEFR-B1の`User Quality`が`NOT_REVIEWED`である理由**: A01は
  P8A→P9A→P9A-R1→P9A-R2という段階的な修正プロセスを経ており、各段階で
  個別の「修正箇所承認」は得られているが、**最終版(r2)を通しで試聴し
  「これで良い」と判定した記録は見当たらない**。これはA02・ADD03の
  「初回通し候補をそのままOK」という一括判定とは性質が異なるため、
  同列に`PASS`とはしない。
- **`publication_status`が全記事`NOT_APPROVED`である理由**: 現時点では
  「番組として公開してよい」という明示的な承認判断がいずれの記事・
  レベルについても記録されていない。`user_quality_status: PASS`は
  「試聴した音質・内容に問題がない」ことのみを意味し、公開可否とは
  別の判断であることに注意([PROJECT_INDEX.md](PROJECT_INDEX.md)参照)。

## 参照元

[ER-003-REPRO_BASELINE.md](ER-003-REPRO_BASELINE.md)、
[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)、
[ER-003-B1_P8A-P9A_AUDIT_REPORT.md](ER-003-B1_P8A-P9A_AUDIT_REPORT.md)、
各記事の`audio_validation_main.md`
