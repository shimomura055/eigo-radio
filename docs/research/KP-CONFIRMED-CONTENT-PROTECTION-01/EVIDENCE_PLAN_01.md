# EVIDENCE_PLAN_01: Family別runtime evidence計画(KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01、2026-10-27)

目的: 「確定レコードを置いて後続工程を実走し、確定後の英語・日本語訳・区分・解説が変化しない」ことを**既存Production経路**で示す(USER_02 ④、PRODUCTION_WIRED受入条件の根拠)。1記事ずつ・Family別。見積<=¥10/Family(承認済みScope内、案件見積300円以下=都度承認不要、`sandwich` 7-7)。日次1,000円内。分割で境界を回避しない。

## 1. 共通の流れ(各Family・各レベルStd/Adv)
1. 既存のKP確定済みrun(または候補doc既存の直近run)を**コピー**して作業用run dirを作る(新規記事生成はしない)。公開物・既存runは更新しない。
2. 確定レコードを置く: HR CLI経路(`select`相当)で生成(origin=hr_cli)。X/Y/Zのうち1ケースはフォーム形payload(v2風)を`confirm --from-form`で取込。
3. **変更試行(API 0)**: 各工程直前にartifactを意図的にずらす(英語1語/訳/assets copy)->Gateが止まることを実走で記録(rc=3 + `confirmed_content_issue.json`)。`confirm-restore`で復元後に再実行して通ること。
4. **正常系の後続実走**: tts(KPセグメント。Master Audio Store再利用で原則API 0〜数円)・gate・assemble・pages(・page_verify=Z)・Part 1/Part 2(Adv)を実際に通し、`verify_selection_matches_outputs`(JA検査込み)がPASS、最終ページHTMLに確定英語・確定訳・(Adv)文法解説全文が表示されること、`content_sha256`が全工程の前後で同一であることを記録。
5. **resume / regenerate-stage / STALE**: (a)同コマンド再実行(resume)で生成関数呼出0・内容不変 (b)Y/Zは`--regenerate-stage kp_<lv>`で候補生成0・内容不変 (c)本文を意味不変の空白差で変更(STALE発火)-> 確定表現が全て一致で再バインド、生成関数呼出0 (d)本文のKP表現を1語変更-> BLOCK+修正案(確定値不変)。
6. **Part 2(Adv)**: 文法レコードあり。STEPB prompt sha/MODELをプロセス内でpatchして`finalize_stage`を実走 -> 解説生成呼出0(モック計測)、`part2_result.json`の`explanation_md`==レコード。Part 1訳poolを変えた場合は`CONFIRMED_CONTENT_ISSUE`(再生成しない)。
7. LR: 既存LR発火済み実例(Z `audio_text_deviation`を持つ既存run)でKP segmentが非対象であること、確定KPの出現位置との重なり警告が記録されること。

## 2. Family別対象と見積
| Family | 対象(既存の確定済みrunをcopy) | 有料の可能性 | 見積 |
|---|---|---|---|
| X(Entertainment News等) | 直近のX Std/Adv Production run(`er019_output/`配下、KP review確定済み、例: AI島寺院 run_ai_01) | KP TTS再生成が起きた場合のみ(Master Store再利用で通常0)、Part 2 Step Bは凍結で0 | <=¥10 |
| Y(Voices) | Y正式Production直近run(`FAMILY-Y-PRODUCTION-LAUNCH-01`系、再配達/SNS年齢) | 同上 | <=¥10 |
| Z(Fiction) | 直近のZ正式run(猿の手 `FAMILY-Z-MONKEYS-PAW-PRODUCTION-01`等) | 同上。`_gloss_person_gate`の変更試行はモックfactory(実API 0) | <=¥10 |
| 合計 | | | <=¥30(各案件<=¥10、日次内) |
- 事前: 各runで`tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run> --out <json>`(rc=3なら停止)。TTS_EXECUTION_MODE=STANDARD、`--budget`指定、再生成は差分のみ(既存再利用優先)。
- 実走コマンドは委任_03で確定(既存各runnerの`--stage`指定。Zは`--stages provision_shell,gate,assemble,pages,page_verify`を1起動、OPEN-480)。

## 3. 保存先
`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/evidence/<family>_<slug>_<level>/`(各: `confirmed_selection.json`、変更試行ごとの`confirmed_content_issue.json`、`before/after content_sha256`一覧、実走stdout要約、`verify_selection_matches_outputs`出力、最終HTMLの該当抜粋)。+ 実走の費用は`raw_usage_log.jsonl`集計を`evidence_summary.json`へ。詳細ログ全文は貼らずパスで参照(既存ER-*_REPORT.md構造に従う)。

## 4. PRODUCTION_WIREDの受入条件(Family別、案)
(1)通常正規経路でレコード生成+G0〜G4が配線、(2)変更試行の全ケースがBLOCK、(3)正常系の後続実走PASSかつ`content_sha256`不変、(4)resume/regenerate/STALEで不変、(5)Part 2(Adv)で解説凍結、(6)A/B/C不変(isolation test+golden)、(7)旧run互換、(8)既存Gate無変更、(9)SSOT/Git反映。判定はFable。
