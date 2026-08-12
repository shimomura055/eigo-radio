# ARTIFACT_REGISTRY — 記事×CEFRレベルの成果物完成状態

**管理ID: ER-PM-001**
**最終更新: 2026-08-12(ER-003-A2-SPEC-FREEZE-01)**

記事×CEFRレベルごとの成果物完成状態を一覧化する。値はすべて監査証拠
(commit・manifest・report)に基づく。**推測で埋めた値はない。** 不明な
場合は`NOT_REVIEWED`/`未着手`等、事実に基づく状態を記載する。

`user_quality_status`(試聴品質)と`publication_status`(公開承認)は
必ず分離する(詳細は[PROJECT_INDEX.md](PROJECT_INDEX.md)参照)。

| Article | Level | Source | Script | Preview | Key Phrase | Full Story | Podcast組立 | User Quality | Publication |
|---|---|---|---|---|---|---|---|---|---|
| A01 | CEFR-B2 | PASS | PASS(自動QA合格。ユーザーによる本文単独の明示承認記録なし) | N/A | N/A | 未生成 | 未生成 | NOT_REVIEWED | NOT_APPROVED |
| A01 | CEFR-B1 | PASS | PASS | PASS | PASS(5件) | PASS | PASS(r2が最終版) | NOT_REVIEWED(部分的な「修正箇所承認」は複数あるが、最終r2版の通し試聴OKは未記録) | NOT_APPROVED |
| A01 | CEFR-A2 | PASS(A2-03独立生成) | PASS(A2-03確定版。ただし"The referee then added more time."→"The game went into added time."の修正が未反映、[DECISION_LOG.md](DECISION_LOG.md)参照) | PROTOTYPE_BUILT(Cross-level原則反映、ただしPause 0.8秒・Outro最新減衰・Key Phrase 3条件発音・In One Line見出し修正は未反映のER-003-CROSSLEVEL-AUDIO-02版のまま) | PROTOTYPE_BUILT(方式L+Canonicalizationで新規選定5件、機械QA合格。3条件発音方式は未適用) | PROTOTYPE_BUILT(機械QA合格、hallucinationなし) | PROTOTYPE_BUILT(294.2秒、clippingなし)。**再assemble要**(Cross-level最新仕様=Pause0.8秒/Outro最新減衰/Key Phrase3条件/In One Line見出し修正が未反映) | NOT_REVIEWED | NOT_APPROVED |
| A02 | CEFR-B2 | PASS | PASS(自動QA合格。ユーザーによる本文単独の明示承認記録なし) | N/A | N/A | 未生成 | 未生成 | NOT_REVIEWED | NOT_APPROVED |
| A02 | CEFR-B1 | PASS | PASS | PASS | PASS(5件) | PASS | PASS | **PASS**(ER-003-REPRO-01、2026-08-08) | NOT_APPROVED |
| A02 | CEFR-A2 | PASS(A2-03独立生成) | PASS(A2-03確定版、修正保留中の項目なし) | PASS(Cross-level原則反映済み、ER-003-CROSSLEVEL-AUDIO-01) | PASS(3条件発音方式を5件へ適用済み、ER-003-A2-AUDIO-AB-01) | PASS(機械QA合格、hallucinationなし、In One Line見出し修正済み) | **PASS**(A/B版とも最新Cross-level仕様を全反映、310.5秒[A]/329.3秒[B]、clippingなし) | **PASS**(ER-003-A2-AUDIO-AB-01、2026-08-12。「A2の完成候補は全体としてOK」、B版=約135WPMを速度方針として採用) | NOT_APPROVED |
| ADD03 | CEFR-B2 | あり(日本語下書きのみ、英語台本なし) | 該当なし | N/A | N/A | 未生成 | 未生成 | NOT_REVIEWED | NOT_APPROVED |
| ADD03 | CEFR-B1 | PASS | PASS | PASS | PASS(5件) | PASS | PASS | **PASS**(ER-003-REPRO-FINAL、2026-08-09。meaning_3はASR homophone ambiguityとして人間確認済み、TTS音声は正常) | NOT_APPROVED |
| ADD03 | CEFR-A2 | PASS(A2-03独立生成) | PASS(A2-03確定版) | PROTOTYPE_BUILT(Cross-level原則反映、ただしPause 0.8秒・Outro最新減衰・Key Phrase 3条件発音・In One Line見出し修正は未反映のER-003-CROSSLEVEL-AUDIO-02版のまま) | PROTOTYPE_BUILT(方式L+Canonicalizationで新規選定5件、機械QA合格。3条件発音方式は未適用) | PROTOTYPE_BUILT(機械QA合格、hallucinationなし) | PROTOTYPE_BUILT(327.4秒、clippingなし)。**再assemble要**(A01と同じくCross-level最新仕様が未反映) | NOT_REVIEWED | NOT_APPROVED |

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
