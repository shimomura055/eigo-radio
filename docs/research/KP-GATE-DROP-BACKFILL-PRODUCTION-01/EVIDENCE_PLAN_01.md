# EVIDENCE_PLAN_01: 正式経路での「除外あり->補完発動」「除外0->不発動」の観測計画(委任_03用)

前提: 委任_02(実装・test PASS・API 0)完了後に実施。方式は`KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/EVIDENCE_01.md`(fresh run+既知事例replay、費用¥11.2)と同型。TTS・本文生成は走らせない(KP stageのみ)。

## 1. 観測したい事実(受入条件2〜8への対応)
| # | 事実 | 方法 |
|---|---|---|
| O1 | 除外ありで補完が発動し、件数=実除外件数以下(受入2,5) | replay(後述R群)+freshで自然発生した場合 |
| O2 | 除外0で補完が発動しない・補完API 0(受入3) | fresh(除外0のレベル)でusage logの補完call行=0、`backfill.triggered=false` |
| O3 | 初回が上限未満でも不発動(受入4) | fresh(call2が4件返答かつ除外0のレベル。AI島Adv型) |
| O4 | 補完候補にGate再適用(救済含む)・重複防止(受入5) | R群の候補doc(`backfill.dropped`、各候補のgates)+replayで補完返答に重複句を混ぜたケース |
| O5 | 救済成立を除外に数えない(受入6) | Y再配達Adv/Z melos(救済M1)型。救済済み候補がいる記事でEが救済分を含まない |
| O6 | resume再課金0、HR候補保全(受入6) | 同一コマンド再起動でsha不変・usage行数不変 |
| O7 | actual model_id・Prompt sha・routing(受入8) | 各callの`model_id`(`gpt-6-luna`系、`SUPPORT_MODEL`契約)・`prompt_sha256`(2-V固定値一致)・usage log |
| O8 | 2-Vが除外句/既存句を守るか(件数文言なしで足りるか=新Prompt要否の実測、DESIGN §4) | R群・fresh発動時の補完返答の重複率・先頭N件のGate通過率を記録 |

## 2. 方式
- **fresh(新規run dir・KP stage限定)**: X/Y/Z x Std/Adv の6 level-run。HR候補を保全するため**既存run dirは使わず新run dirにコピー**(`..._run_kpbf_ev_01`)。入力の揃え方・起動コマンドは`EVIDENCE_01.md §1`の表を踏襲(`--stage scaffold --scaffold-only`[X]/`--stages kp`[Y]/`--stage kp`[Z])。各起動前に`tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run> --out <json>`(rc=0確認)。同一run dir 5分内3回起動なし(RESTART_STORM)。起動間隔150秒以上。再起動確認(O6)は各Family 1回。
- **replay(除外を確実に起こす)**: 既知の除外事例の凍結本文+凍結した初回LLM出力(選定・canonicalization 1回目)を、**正式`generate_candidates`**へ注入(`select_fn`/`vocab_call_fn`/`canon_fn`の初回分のみ凍結)。補完call・補完分canonicalization・gloss整合・QA再判定・Redundancy QAは**実LLM**。KPI provenance区分に「replay=凍結入力+実LLM補完」と明記し、freshと混ぜない。
  | case | 本文 | 期待する初回除外 |
  |---|---|---|
  | R1 X AI島Std | `er019_output/.../ai_island_temple__run_ai_01/a2`の凍結fixture(`KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/replay_results/X_ai_island_a2`流用) | validate(`too soon to wave a flag` 6語)+canonicalization(`studied separately`)=E=2 |
  | R2 X UK Std | `uk_train_speaker_playback`の数字除外事例(Trial-02 COMPARISON_02/`runs/uk_train_speaker_playback__a2__p7w5__r1`から凍結) | validate(数値)E>=1 |
  | R3 Y 再配達Std | `Y_redelivery_a2`凍結(`redelivery fee` CMU除外ほか、除外2) | cmu等 E=2 |
  | R4 Y SNS Adv | `Y_sns_b1b`凍結(除外2、救済D1成立1件を含む=救済を数えないことの確認) | E=除外のみ(救済`catches their interest`は数えない) |
  | R5 Z 猿の手Adv | `the_monkeys_paw`の`interferes`(`duplicate_of_top3`、Trial-02 COMPARISON_02:111) | duplicate_of_top3 E>=1(Gate維持の確認) |
  | R6 Z melos Adv | `Z_melos_b1b`凍結(救済M1x2、除外なし) | E=0(救済のみで補完不発動=O5) |
  各caseで凍結元の所在・取得手順を委任_03の最初に確認する(元run dirは読み取り専用で使用)。
- **重複混入ケース(O4)**: R1のreplayで、補完call返答(実LLM)を採取後、同じ返答を`vocab_call_fn`に再注入して現存候補と同一の句を足した変形(API 0)で「重複は捨てる」を確認(実LLM返答そのものは変更しない)。

## 3. 完了判定(DESIGN_READY後の次段階の基準。本委任では実施しない)
- 6 fresh level-runのうち、除外0のレベルで補完API=0(O2)、call2<5件でE=0のレベルがあればO3。自然に除外が出たレベルは補完発動を確認(O1)。
- replay 6件でO1・O4・O5(R4/R6)を確認。R5でGate維持。
- 全run: model_id/prompt sha/routing記録(O7)、resumeでsha不変・usage不変(O6)。
- 2-Vが指示を守らない場合(O8でGate通過率が低い等)は新Prompt(件数1行note)の必要性を**区別報告**(ユーザー原文§4)。

## 4. 安全
- 本番の既存run dir・HR候補は書き換えない。STOP通知はhelperで確認。RESTART_STORM回避(上記)。各プロセスは自分のPIDのみ終了。有料run再起動は委任文が許す回数のみ。
