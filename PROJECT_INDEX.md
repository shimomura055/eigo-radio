# PROJECT_INDEX — eigo-radio プロジェクト知識の入口

**管理ID: ER-PM-001**
**最終更新: 2026-08-22(ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01、POOL_TOPIC_MASTER.md参照追加)**

このファイルは、プロジェクトについて何かを知りたいときに「まずどこを見るか」を
示す入口です。個別レポート・commit・Git履歴を毎回横断監査しなくても、
以下の表から正式な参照先へ1〜2ホップで辿り着けることを目的としています。

## 参照先マップ

| 知りたいこと | 正式参照先 |
|---|---|
| 現在のサービス仕様(番組構成、Preview/Key Phrase/Full Story等) | [CURRENT_SPEC.md](CURRENT_SPEC.md) |
| **現在のLaunch対象レベル** | **A2 / B1の2レベル**(`LAUNCH_SCOPE: IN`)。**B2は`LAUNCH_SCOPE: OUT_OF_INITIAL_SCOPE`**(廃止ではなく、future expansion candidate / internal comparison・reference / historical experiment・referenceとして保持)。詳細は[CURRENT_SPEC.md](CURRENT_SPEC.md)のCEFR節冒頭`LAUNCH_SCOPE`注記、[DECISION_LOG.md](DECISION_LOG.md)のER-003-B1-B2-SCOPE-FIX-01 Decision Bを参照(2026-08-17) |
| B1の現行仕様(独立生成Natural Spoken News English、Voice構成、Key Phrase等) | [CURRENT_SPEC.md](CURRENT_SPEC.md) の「B1(独立生成Natural Spoken News English)」節(2026-08-17〜、`DECIDED`。B1はB2と同一テキストを共有せず、同一LedgerからB1専用Writerで独立生成する)。**CEFR比較表のB1列は`HISTORICAL`(P-series専用)であり現行仕様ではない** |
| A2の現行仕様(Core Explanatory Logic Preservation含む) | [CURRENT_SPEC.md](CURRENT_SPEC.md) の CEFR-A2構造・音声仕様節 |
| CEFR A2/B1/B2の条件(語彙・文長・語数等) | [CURRENT_SPEC.md](CURRENT_SPEC.md) の CEFR節・CEFR-A2構造・音声仕様節(A2は`DECIDED`。CEFR比較表のB1列・B2列はP-series記事の`HISTORICAL`記録。B2は`LAUNCH_SCOPE: OUT_OF_INITIAL_SCOPE`の参照情報)。検証の経緯・却下案は[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)(`HISTORICAL`) |
| サービス仕様と実装Hardeningの違い | サービス仕様(番組の聞こえ方・記事の作られ方)は[CURRENT_SPEC.md](CURRENT_SPEC.md)本体、実装Hardening(TTS/ASRの内部実装の堅牢化、サービス仕様は不変)は[CURRENT_SPEC.md](CURRENT_SPEC.md)の「Audio Implementation Detail」節+[DECISION_LOG.md](DECISION_LOG.md)の`[Implementation Hardening]`区分エントリを参照。両者は混同しない |
| A2/B1/B2共通の音声品質原則(Preview原則、Key Phrase発音、Pause、Outro等) | [CURRENT_SPEC.md](CURRENT_SPEC.md) の Cross-level仕様節 |
| Key Phrase仕様(方式L、Canonicalization等) | [CURRENT_SPEC.md](CURRENT_SPEC.md) の Key Phrase節 |
| TTS仕様(model/voice/single call等) | [CURRENT_SPEC.md](CURRENT_SPEC.md) の Preview/Full Story節 |
| 音声組み立て・編集順序・MFA/ASR運用 | [CURRENT_SPEC.md](CURRENT_SPEC.md) の Audio Assembly / QA節 |
| なぜその仕様になったか(採用理由・比較した選択肢) | [DECISION_LOG.md](DECISION_LOG.md) |
| 未確定事項・技術的負債・Blocking issue | [OPEN_ITEMS.md](OPEN_ITEMS.md) |
| 各記事×CEFRレベルの完成状況(スクリプト/音声/試聴/公開) | [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md) |
| Pool Topic(Evergreen記事)20件の母集団・生成状況 | [POOL_TOPIC_MASTER.md](POOL_TOPIC_MASTER.md) |
| 過去に何を試して何が採用/却下されたか | [HISTORY_INDEX.md](HISTORY_INDEX.md) |
| 現在の作業場所・直近のTask・次にやること | [ER-003-B1_HANDOFF.md](ER-003-B1_HANDOFF.md)(役割は「直近の作業再開用」のみ、仕様の一次情報源ではない) |
| 用語の意味・紛らわしい表記の区別 | 本ファイルの[用語集](#用語集terminology)節 |

## この6文書＋HANDOFFの役割

| 文書 | 役割 | やらないこと |
|---|---|---|
| PROJECT_INDEX(本書) | 入口。参照先の地図 | 仕様・決定・履歴そのものは書かない |
| CURRENT_SPEC | 現在有効な正式仕様のみ | 経緯・比較検討・却下案は書かない |
| DECISION_LOG | 確定した意思決定と理由 | 未決事項は書かない(→OPEN_ITEMS) |
| OPEN_ITEMS | 検討中・候補・未確定・技術的負債 | 確定済み仕様は書かない(→CURRENT_SPEC) |
| ARTIFACT_REGISTRY | 記事×CEFRレベルごとの成果物完成状態 | 仕様や理由は書かない |
| HISTORY_INDEX | 過去に何をして何が成功/失敗/却下されたかの索引 | 詳細本文はコピーせず、詳細レポートへリンクする |
| HANDOFF | 直近の作業再開専用(現在地・直近完了Task・作業中Task・次Action・blocker・最新commit) | 仕様のコピーは行わない。仕様はCURRENT_SPECへのリンクで参照する |

個別のdecision record・audit report・handoff・manifest・commitは、
証拠・詳細資料として引き続き保持する(削除しない)。ただし、質問への
**一次回答元**は上記6文書＋HANDOFFとする。

## 質問への回答手順(推奨)

1. PROJECT_INDEX(本書)で参照先を特定
2. CURRENT_SPEC / ARTIFACT_REGISTRY / OPEN_ITEMS を確認
3. 必要なら DECISION_LOG で「なぜ」を確認
4. 必要なら HISTORY_INDEX で過去の試行錯誤を確認
5. それでも不足する場合のみ、詳細レポート原本を参照
6. さらに不足する場合のみ、Git/コードを直接確認

## 状態ラベル(全文書共通)

| ラベル | 意味 |
|---|---|
| `DECIDED` | 正式採用済み |
| `UNDER_REVIEW` | 現在検討中 |
| `CANDIDATE` | 候補だが検討開始前、または比較対象 |
| `TBD` | まだ仕様が存在しない |
| `DEPRECATED` | 以前採用したが現在は廃止 |
| `REJECTED` | 検証して不採用 |
| `HISTORICAL` | 過去実績として残すが現行仕様ではない |

「たぶん採用」「以前使った」「承認済みらしい」のような曖昧な状態表現は使わない。

## 成果物の状態は2軸で分離する

| 軸 | 値 | 意味 |
|---|---|---|
| `user_quality_status` | `PASS` / `FAIL` / `NOT_REVIEWED` | ユーザーが試聴し、音質・内容として問題なしと判断したか |
| `publication_status` | `NOT_APPROVED` / `APPROVED` / `PUBLISHED` | 番組として公開してよいとユーザーが正式に判断したか |

「試聴OK」(quality PASS)と「公開承認」(publication APPROVED)は別の判断であり、
混同しない。詳細は[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)参照。

## 用語集(TERMINOLOGY)

紛らわしい・過去に混同が発生した用語を明確化する。

| 表記 | 意味 | 混同しやすい対象 |
|---|---|---|
| `CEFR-A2` / `CEFR-B1` / `CEFR-B2` | 言語難易度レベル(現行ER-003パイプライン) | ER-002の実行バッチ名と衝突 |
| `Batch-B1` / `Batch-B2` / `Batch-B3` | ER-002-S3実験の実行バッチ番号(`er002_s3_config.py`)。Batch-B1=A01+A02、Batch-B2=A03+A06、Batch-B3=A04+A05。**CEFRとは無関係** | `CEFR-B1`/`CEFR-B2` |
| `levels.py`のA2/B1/B2 | `generate_test.py`/`tts_test.py`という、"English Your Way"とは**無関係な別番組**(LEO/MAYA対話形式)専用の参照値 | `CEFR-A2`/`CEFR-B1`/`CEFR-B2`の正式仕様 |
| 記事ID `A01`/`A02`/`ADD03` | 現行ER-003で制作中の3記事(サッカー/SNS規制/ホルムズ海峡) | ER-002の記事ID`A01`/`A02`/`A04`(A01・A02は同トピックだが台本内容は別物、A04は無関係な別記事) |
| `A04`(ER-002) | Meta "Muse Image" AI機能撤去に関する技術記事。現行3記事とは**無関係** | 現行記事群の一部だと誤認しないこと |
| `user_quality_status` | 試聴品質の合否 | `publication_status`(公開可否) |
| `Dynamics3` | ER-002で使用していたダイナミックレンジ圧縮処理。**現行ER-003のB1組み立てでは明示的に不使用**(scalar RMS gainのみ、`er003_b1_p9a_audio.py`にコメントで明記) | ER-003でも使われていると誤認しないこと |
| `B1-A` / `B1-B` | B1のNews本文生成方式を比較した際の試作ラベル。B1-A=B2から派生させる方式(不採用)、B1-B=Verified Fact Ledgerから直接生成する方式(採用、現行方式)。**現行仕様は単に「B1」と呼び、B1-Bというラベルはコード内の実装名として残る** | B1-A/B1-Bという用語自体を現行の公式な番組レベル名だと誤認しないこと(公式には`CEFR-B1`) |
| 記事ID `Hanshin`/`Health`/`Household`(N3-01) | ER-003-A2-B1-N3-01で新規制作した3ジャンル横展開検証用の記事(PROTOTYPE / N-INCREASE VALIDATION)。P-seriesの`A01`/`A02`/`ADD03`とは別の記事群 | P-series記事群と同一の完成度・承認状態だと誤認しないこと(N3記事は機械QA完了、人間による通し試聴は未記録、外部ユーザー未検証。詳細は[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)・[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-36参照) |

今後の文書では、単独の`B1`/`B2`だけで意味が曖昧になる場合、必ず
`CEFR-B1`/`Batch-B1`のように明示する。

## 参照元

本再編(ER-PM-001)の詳細な監査根拠は、既存の各audit/decision文書
(下記6文書内でリンク)を参照。
