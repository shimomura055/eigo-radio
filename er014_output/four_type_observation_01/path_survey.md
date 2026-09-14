# Step 0: Trend Synthesis / Discovery Focus S2 / Voices 正式Production path 下調べ

(EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01共通、News記事担当Sonnetが¥0で実施。
後続3記事[Trend/Discovery/Voices]の委任で再利用可能。実行は行っていない。)

| Editorial Type | スクリプト/関数 | editorial_mode/level | 状態(CURRENT_SPEC) | 根拠行番号 |
|---|---|---|---|---|
| Trend Synthesis | `er006_pool_pilot_01_writer.py::run_writer_for_theme()`(Production Writer正式初回経路)→`er003_v1_n3_01_articles_generate.py::run_one_pattern()`。`editorial_mode="trend_synthesis"`を手動指定 | 手動指定のみ(自動判定なし)、mode文字列は現状`"trend_synthesis"`のみ既知 | `PRODUCTION_WIRED` | CURRENT_SPEC.md:755-761 |
| Discovery Focus S2 | `er003_discovery_focus_staged_production_01.py`(新規モジュール)、opt-in `editorial_mode="discovery_focus_staged"`(`er003_v1_n3_01_articles_generate.EDITORIAL_TYPE_MODULE_BLOCKS`へ登録)。既存`run_one_pattern`(News Major/Daily/Trend Synthesis/現行Discovery非staged)は無変更 | opt-in、Focus解決→Stage1 Main Story+QA→...の正式処理順あり | `PRODUCTION_WIRED`(2026-09-13、FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01) | CURRENT_SPEC.md:861-914 |
| B-Family Voices | `er012_b_family_editorial_type_registry_01.py`(`get_editorial_type_a2()`)・`er012_b_family_voices_a2_production_01.py`・`er012_b_family_production_runner_01.py`(`level="a2"`分岐) | 標準は2 Voices(Voice A/B=Algieba/Erinome、5区切り: Hook/Voice A/Voice B/Tension/Closing) | `PRODUCTION_WIRED`(2026-09-09) | CURRENT_SPEC.md:637-658 |

## Voices: 2 Voices可否と根拠(重要)

- **標準(2 Voices)は`PRODUCTION_WIRED`**。B1/A2いずれも物理構造は5区切り(Hook/Voice A/Voice B/Tension/Closing)、Voice A=Algieba/Voice B=Erinome/Narrator見出し=Aoede。Production Runner(`er012_b_family_production_runner_01.py`)はこの2 Voices経路のみを配線済み(根拠: CURRENT_SPEC.md:648-658)。
- **3 Voices(Voice1/2/3=Algieba/Erinome/Schedar)はTrialで`VALIDATED`、ユーザーは`APPROVED_FOR_PRODUCTION`まで承認済みだが「**`PRODUCTION_WIRED`ではない**」(未配線)**。配線に必要な5項目(registry可変voice数シグネチャ・Gate辞書point_three登録・Comment 3V Contract化・mode/level命名・Schedar本採用格上げ承認)が未実装(根拠: CURRENT_SPEC.md:658、行内「3V」表)。
- したがって「Voices記事」を正式Productionで生成する場合、現行配線済みなのは**2 Voices版のみ**。3 Voicesを使いたい場合はProduction配線(未承認範囲の実装)が別途必要になり、本観測タスクの「新仕様Trial禁止」方針に反するため、Voices記事は2 Voicesで生成するのが正式path準拠となる。

## 付記: Research/Ledger供給に関する共通の注意(Trend/Discovery/News共通)

News担当の調査で判明した点(Trend Synthesis/Discovery Focus S2にも共通する制約): Writerへ渡す
Verified Fact Ledgerの**自動Research供給経路はCURRENT_SPEC上`USER_DECISION_REQUIRED`のまま未配線**
(既存自動Research pipelineの出力形式とN3-01 Ledger形式の互換性が未検証、CURRENT_SPEC.md:760)。
正式initial pathは「既存の承認済みLedgerをファイルとしてそのまま使う」(手動供給)であり、
**新規の実世界Topicに対して正式Production経路だけでVerified Fact Ledgerを新規に作る自動化された
手順は存在しない**。Trend Synthesis/Discovery Focus S2で新規テーマを生成する場合も、同じ制約に
直面する可能性が高い(後続3記事の担当Sonnetは着手前にこの点を確認すること)。
