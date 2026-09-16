# 委任文: PERSONALIZED-NEWS-A2-E2E-PREFLIGHT-01

## 管理ID

`PERSONALIZED-NEWS-A2-E2E-PREFLIGHT-01`

**並行タスクあり(重要)**: 別のsonnet-workerが`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-02`(er014_output/user_test_news_2ep_01配下、SSOT追記、git commit/push)を実行中。衝突回避のため本タスクでは **git操作を一切行わない**(commit/push/add/stash/fetch/merge禁止)、**`docs/pm/ACTIVE_TASK.md`を触らない**、SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)・コード・Prompt・出力dirを一切変更しない。書き込みは`docs/pm/RESULT_PACKET_PN_A2_PREFLIGHT.md`(新規)と`docs/pm/delegation_log/PERSONALIZED-NEWS-A2-E2E-PREFLIGHT-01.md`(+`_check.json`)の3ファイルのみ。

## 性質/到達上限Status/禁止事項

- 性質: Personalized News(topic `Is personalized news good for us?`)のA2記事・音声を新規作成する前に、「新規topicのResearch/Writer→A2記事→Scaffold→TTS→Assembly→Audio Validation Gate→player」を**正式Production経路だけ**でE2E完走できるかを**read-onlyで事実確認**する。実装・生成・API実行は行わない。
- 到達Status(いずれか1つ): `E2E_READY`(下記全条件を確認できた場合のみ)/`PARTIAL`(一部のみ正式配線)/`USER_DECISION_REQUIRED`(新仕様・Production改修が必要)。「たぶん通る」でE2E_READY判定しない。
- 禁止: コード変更、Prompt変更、新runner作成、新A2記事生成、API実行、TTS実行、Trial開始、B1記事からの手作業変換、DEV scriptによる代替E2E、git操作、ACTIVE_TASK/SSOT変更。

## STOP条件

A2新規topic正式入口がない/正式pathとTrial・DEV pathが混在/Writer→Audioの接続が未配線/新しいProduction改修が必要/新仕様判断が必要/CURRENT_SPECと実装が不一致/runtime evidence不足でE2E_READYを断定できない場合、その時点で判定を確定し報告する(実装・Trial・記事生成へ進まない)。

## 固定ブロック

- E-1: 同一ファイル再読禁止。
- D-1: Grep→該当行範囲Read、全文Readは構造把握に必須の場合のみ。
- G-1: git出力は本タスクでは使わない。
- F-1: transcript退避不要。
- T-1: 事前指定Read/Grep一覧に従い、一覧外の追加Readは理由をRESULT_PACKETに1行記録。
- T-0: 本ファイルを`docs/pm/delegation_log/PERSONALIZED-NEWS-A2-E2E-PREFLIGHT-01.md`へ保存し
  `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`
  を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。

## 事前指定Read一覧

- `er012_b_family_production_runner_01.py`: Grep `^def main|stage|level ==|write_new_theme|writer_adapt|b1_article|adapt|argparse|add_argument`→`main_a2()`本体(L1300〜末尾のうち該当範囲)と`main_b1_2v()`のstage定義のみRead
- `er012_b_family_voices_a2_production_01.py`: L147-186(adapt Writer入力仕様)、L545-581(Key Phrase再利用の入力元)、Grep `ledger|voice_attribution|research`
- `er012_b_voices_3v_a2_user_test_01.py`: Grep `^def |import er012|main_a2|writer_adapt|stage`→Trial driverと正式runnerの関係
- Personalized News成果物dir(Grepで特定): `run_result*.json`/`*summary*.json`/`fact_check*.json`/`comment_contract*.json`/`ledger*`のGrep `status|verdict|model|attempt|final`のみ
- `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`: 上記Grepの該当行のみ
- `er011_human_review_lock_01.py`/Audio Validation Gate module: Grep `B_FAMILY_A2|audio_gate_level|def `→A2 Gate levelの存在確認のみ
- `docs/pm/RESULT_PACKET_VOICES_A2.md` L5-12

## 事前指定Grep一覧

`Is personalized news good for us`(files_with_matches, er012_output配下)、
`EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01|B-Family.*A2|Voices A2|writer_adapt|翻案|main_a2|level="a2"|OPEN-151|write_new_theme`(CURRENT_SPEC.md)、
`EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01|USER-TEST-VOICES-A2-MINIMAL-01|OPEN-151`(DECISION_LOG.md)、
`personalized.news`(-i、全体、files_with_matchesで所在特定)、
`run_writer_adapt\(|prepare_a2\(`(全体)、
`B_FAMILY_A2`(er003_v1_n3_01_assemble.py / er011_human_review_lock_01.py)。

## 実行コマンド全文

```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PERSONALIZED-NEWS-A2-E2E-PREFLIGHT-01.md --json-out docs\pm\delegation_log\PERSONALIZED-NEWS-A2-E2E-PREFLIGHT-01.md_check.json
```

## SSOT

本タスクではSSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)への追記は行わない(read-only preflight)。

## Git

本タスクではgit操作を一切行わない(commit/push/add/stash/fetch/merge禁止、G-1)。

## 報告

`docs/pm/RESULT_PACKET_PN_A2_PREFLIGHT.md`へ、実ファイル名・関数名・行番号付きで以下14項目を報告する: (0)T-0結果 (1)Personalized News既存成果物の正式path (2)既存Ledger再利用可否 (3)A2新規topic Writer正式入口の有無 (4)Writer前半Production wiring状況 (5)Audio後半Production wiring状況 (6)retry/fallback/regeneration整合 (7)Trial/DEV依存の有無 (8)runtime evidenceの有無 (9)Dangling Reference Check結果 (10)現在Status (11)不足項目 (12)次に必要なユーザー判断 (13)PM Gate確認 (14)無変更証跡/事前指定外Read(理由付き)。
