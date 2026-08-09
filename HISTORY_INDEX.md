# HISTORY_INDEX — 過去の実施履歴索引

**管理ID: ER-PM-001**
**最終更新: 2026-08-09**

過去に何を実施し、何が成功・失敗・却下されたかを時系列で索引化する。
詳細本文は全文コピーせず、詳細レポートへリンクする。

| 日付 | 管理ID | 対象 | 実施内容 | 結果 | 採用/却下 | 詳細レポート | commit |
|---|---|---|---|---|---|---|---|
| 2026-07-18 | ER-002-S3-B1(Batch-B1) | A01(サッカー) | CEFR無指定の台本でgemini-2.5-pro-preview-tts音声を生成 | 生成成功、Dynamics3処理済み | `HISTORICAL`(後に否定的評価で破棄) | `er002_output/A01/manifest.json` | `ed0f786` |
| 2026-07-18 | ER-002-S3-B1(Batch-B1) | A02(SNS門限) | 同上(voice=Charon) | 生成成功 | `HISTORICAL`(後に否定的評価で破棄) | `er002_output/A02/manifest.json` | `ed0f786` |
| 2026-07-19 | ER-002-S3-B1 | A01 | ユーザーが本文音声を最後まで試聴・評価 | 否定的("台本は事実の羅列に近く、切り口が弱い") | `REJECTED` | `er002_output/A01/user_evaluation.json` | `ed0f786` |
| 2026-07-19 | ER-002-S3-B1 | A02 | ユーザーが本文音声を最後まで試聴・評価 | 否定的("記事選定と台本内容の両方が不十分") | `REJECTED` | `er002_output/A02/user_evaluation.json` | `ed0f786` |
| 2026-07-xx | ER-002-v1.1B | A01 | 台本改訂版(v1.1B)を生成、ユーザーがA/B比較試聴 | "さらに悪化した"としてIn One Line開始時点で試聴中断 | `REJECTED` | `er002_output/A01/v1_1b_c1/user_evaluation.json` | `f90b399` |
| 2026-07-18〜 | ER-002-S3-C2/S2 | A04(Meta Muse、無関係な技術記事) | Aoede/Charon両声でTTS+Dynamics3+AB比較 | 生成成功だがユーザー評価は`pending_user_listening`のまま未完了 | `HISTORICAL`(現行3記事とは無関係) | `er002_output/A04/{aoede,charon}/manifest.json` | `7742945` |
| 2026-07-20 | ER-003-P2 | 全記事 | Natural English Source方式を正式採用(B2/B1/A2独立生成の基準原稿) | 確定 | `DECIDED` | [er003_v1_p1b_natural_source_spec.md](er003_v1_p1b_natural_source_spec.md) | `45c48ee` |
| 2026-07-26頃 | ER-003-B1-P5A | A01 | 日本語TTSエンジンの候補調査(Google Cloud TTS/Azure/Amazon Polly) | **Azure・Pollyは利用可否確認のみ、実際のTTS生成テストは未実施**。GCPのみ次段階(P5B)で実生成テストへ進んだ | `HISTORICAL`(Azure/Pollyは比較検討の対象止まり) | HANDOFF内P5節 | `ffe9cc9` |
| 2026-07-26頃 | ER-003-B1-P5B〜P5C | A01 | Google Cloud TTS(Neural2-B)で実際に音声生成しテスト | ユーザー試聴で機械的・誤読("何が"→"なんが")と判定 | `REJECTED` | HANDOFF内P5節 | `0fe94eb`, `8193e0b`, `e2b75b7` |
| 2026-07-xx | ER-003-B1-P3R〜P3Z | A01 | 日本語ナレーション内に英語Key Phraseを直接埋め込む方式を検証 | 技術的停止を繰り返し、最終的に不採用 | `REJECTED` | HANDOFF内P3節 | `e5a9c4e`〜`4cc21a8` |
| 2026-07-xx | ER-003-P2I | B2 Key Words | 方式L/P/Uの比較実験、方式Lを標準採用 | Lが標準方式に | `DECIDED` | [ER-003-P2I_decision_record.md](er003_output/p2i/ER-003-P2I_decision_record.md) | `e33f227` |
| 2026-08-06 | ER-003-B1-P7A | A01 | Gemini 3.1 Preview単一call検証 | 誤読解消を確認、モデル採用 | `DECIDED`(ADOPTED) | ER-003-B1-P7A実行報告 | `b4f871f` |
| 2026-08-07 | ER-003-B1-P7C | A01 | 英語Key Phrase Component差し替え検証 | ポーズズレのバグ発見、修正 | `PASS`(修正後) | ER-003-B1_HANDOFF.md | `b32c6e7` |
| 2026-08-07 | ER-003-B1-P8A | A01 | Preview+本編 通し試聴版生成 | PROTOTYPE生成、P7C無音バグ発覚 | `PASS`(バグ修正後再生成) | HANDOFF | `a1018a9`, `c5aaf2c` |
| 2026-08-07 | ER-003-B1-P9A/R1/R2 | A01 | 完成版音声組み立て、3回の修正(異常無音短縮、Outro音量、notification2の"two"欠落) | 最終r2版まで到達 | `PASS`(ただしエピソード全体最終承認は未取得) | ER-003-B1-P8A-P9A_AUDIT_REPORT.md | `dcc6d8a`〜`d2aa9e6` |
| 2026-08-08 | ER-003-KP-01/02/02-R1 | Key Phrase全体 | Canonicalization新設→最小十分原則→意味保持・Traceability再定義 | 3段階で確定 | `DECIDED` | チャット内実行報告(3件) | `e607d26`, `8856264`, `5a94db0` |
| 2026-08-08 | ER-003-REPRO-01 | A02(SNS規制) | B1本文・Key Phrase・Preview・Full Story・Podcast組立を一括生成 | 初回通し候補をユーザーがそのままOK | `PASS` | ER-003-REPRO-01実行報告 | `a70736d`, `0a0a7f7` |
| 2026-08-08〜09 | ER-003-REPRO-02 | ADD03(ホルムズ海峡) | 同上、meaning_3でASR homophone ambiguity発見 | 初回通し候補をユーザーがそのままOK(meaning_3含む) | `PASS` | ER-003-REPRO-FINAL章(Baseline文書) | `1b62a20`, `c4a762c` |
| 2026-08-09 | ER-003-A2-00 | CEFR-A2全体 | A2既存仕様の監査(20項目) | 仕様は1件も存在しないことを確認、生成元に関する矛盾を発見・提示 | `DECIDED`(監査完了、仕様自体はTBD) | [ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md) | `dd9e40c` |
| 2026-08-09 | ER-003-B2-AUDIT-01 | CEFR-B2全体 | B2音声成果物の再監査、ER-002時代の実績発掘 | 「B2まで音声完了してB1へ」という理解は誤りと確定 | `DECIDED`(監査完了) | [ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md) | `276b9eb` |
| 2026-08-09 | ER-PM-001 | プロジェクト全体 | Knowledge Management体制の再編(本文書群の新設) | 6文書体制を確立 | `DECIDED` | 本文書群 | (本コミット) |

## 参照元

[DECISION_LOG.md](DECISION_LOG.md)、[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)、
`ER-003-B1_HANDOFF.md`(P3〜P6系の詳細な試行錯誤ログ)
