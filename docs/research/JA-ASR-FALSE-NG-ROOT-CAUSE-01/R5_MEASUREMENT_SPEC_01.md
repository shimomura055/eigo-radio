# R5_MEASUREMENT_SPEC_01(Production側の計測・S転写保存の仕様。Opus R-5。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_08、2026-10-25)
**本書は仕様のみ。実装は07A(`er078_*`/`er007_*`のF1+F2適用)commit後の別委任**(Fable判断)。本委任ではProductionコードを変更しない。目的: (1) 07AのF1が新たに生む誤NGの頻度、(2) βの対象型(Primaryの数値崩れ)の実頻度、(3) βを将来採用する場合の前提(S転写等の保存)を、**API 0・新flag 0・既存挙動不変**で貯める。

## 1. 計測すること(指標)
| ID | 指標 | 分母 | 取得元(既存) |
|---|---|---|---|
| M1 | JA attempt数、うち`p1_value_diff`件数(率) | JA判定したattempt(role・family別) | `asr_judgement.reason_code`(`er078_asr_unified_judge_01.py`のaudit。attempts_log/`tts_generation_results.json`) |
| M2 | `final_gate_value_diff`件数(率)とそのうち『F1が新規に作ったNG』(F1適用前ならREADING_MATCH PASSだったもの) | JA attempt | 同上+F1適用前判定の再計算(API 0。保存Primary転写を旧規則で再判定) |
| M3 | 値差NG(M1+M2)のPrimary側崩れ型の内訳: **A=断片連結で説明可能(precheck真)**、B=桁欠落・値矛盾、C=Primary読み不一致、D=その他。`b_light_proto_02.analyze_primary_values`/`precheck_composite`相当をAPI 0で保存Primary転写へ適用 | M1+M2 | 保存Primary転写・原稿 |
| M4 | M3-Aの『読みもv2読み規則で成立する』件数(= βがSecondary次第で成立しうる件数)と、うち`strict`読みでも成立する件数 | M3-A | 同上 |
| M5 | Azureが呼ばれた値差NG(P3経路)での**S転写保存率**(後述§2の欠落ゼロを確認) | Azure呼出attempt | `asr_judgement.secondary` |
| M6 | a1型(Primary読み不一致)/a2型(桁欠落)/a3型(断片連結)の頻度(M3のC/B/A) | M1+M2 | M3と同一 |
| M7 | HR Lock(`human_review_queue`)に至った値差NGの割合 | M1+M2 | `human_review_queue.jsonl` |
注: P1が`p1_value_diff`でAzureを呼ばずに打ち切る場合、**S転写は存在しない**。したがってM3〜M6は**Primary転写だけで型を分類**し、Secondaryの値一致(βの必須条件)は測れない。βが実際に何件を救うかは、フック①でAzureを呼ぶ『有料の実測』でしか出ないため、本計測はその前段(対象型の頻度)に留める。

## 2. 保存すること(S転写保存の仕様。βの前提条件でもある)
Secondary(Azure)を呼んだattemptで次を**`asr_judgement.secondary`**(既存dict、`er078_asr_unified_judge_01.py:479`の`secondary`)に必ず残す:
| 項目 | 現状 | 要求 |
|---|---|---|
| `text`(S転写) | 保存済(`:663` `audit["secondary"].update(text=stext, ...)`) | 維持。空・None時も`text`キーと`error`を残す |
| `engine` | 保存済(`ctx.engine`) | 維持 |
| `model_id` | **`steps`側にのみ**(`er007_ja_secondary_asr_01.py:284` `azure-speech-stt`) | `secondary.model_id`にも複写 |
| `audio_sha256`(wav sha) | `ctx.wav_sha256`がある場合のみ`audit["audio_sha256"]`(`:498-499`) | Secondary呼出時は`ctx.sha()`の値を**必ず**記録(`nosha:`プレースホルダは記録せず欠落扱い) |
| Primary転写 | 保存済(`primary.text`) | 維持 |
| 原稿(canonical) | attempt recordにあり | `asr_judgement.canonical_text`として判定時点の値を複写(再利用時の再判定が原稿の版違いを検知できるように) |
**保存の書込み失敗・欠落は計測も配線(β)も止めない**が、`asr_judgement.secondary.provenance_complete=false`を立て、fail-closed(βの再利用判定・composite判定が`COMPOSITE_PROVENANCE_MISSING`/`secondary_provenance_missing`で拒否)。保存先=既存のattempts_log/`tts_generation_results.json`(新しい証跡置き場は作らない。計測集計結果は既存の`er0XX_output/`構造または`ER-*_REPORT.md`へ)。

## 3. fail-closedの条件
1. S転写・engine・wav sha256のいずれかが無い→計測行は`provenance_complete=false`として別集計(M5の欠落率)。βの判定・再利用では常に拒否。
2. 計測処理の例外は**判定結果に影響させない**(try/exceptで握りつぶすのではなく、計測は判定の**後**に行い、失敗は`measurement_error`として記録のみ。判定・retry・HR Lock・attempt数は不変)。
3. 計測は**既定ON/OFFを新設しない**(判定を変えないread-only記録のため新flagは不要)。ただし保存項目の追加は`audit`のスキーマ追加であり、既存の再利用・registry・`asr_judgement_inherited`が未知キーを無視することを確認するテストを含める。

## 4. 集計script仕様(API 0)
`r5_ja_value_diff_report_01.py`(07A後の別委任で作成。置き場=`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/`)。
- 入力: リポジトリ内の`tts_generation_results*.json`・`attempts/*.json`・`human_review_queue.jsonl`(`collect_unknown_pool_02.py`と同じ機械列挙、選別なし)。
- 処理: attemptごとに(canonical, primary, `reason_code`, secondary有無, S転写)を取り出し、M1〜M7を算出。M3は`b_light_proto_02`の`analyze_primary_values`/`precheck_composite`を**importして**使う(Production関数も同様にimport、複製しない)。F1新規NG(M2)は、同じ入力を『F1適用前の判定』(pin版スナップショット)と『現行』で再判定して差分を数える。
- 出力: 件数表(family別・role別・日付別)、M3型別の全件列挙(原稿・Primary・S有無・理由)、`provenance_complete=false`の一覧。決定的(タイムスタンプなし)、socket guard(API 0)。
- 判定への利用: **判定基準ではなく頻度の開示**。目安の読み方(Fableへの材料): M3-A(断片連結で説明可能)が観察窓内で0〜1件なら、βは当面実害が出ない低優先、複数件ならフック①の有料実測(Azure呼出、約0.27円/件)を検討。

## 5. 配線時のtest項目(別委任)
- 保存項目の追加が既存判定(state・reason_code・warnings・attempt数)を変えない(前後比較。既存771+493件で判定変化0)。
- `provenance_complete`が欠落時にfalse、揃っていればtrue。
- Azure不呼出attempt(P1打ち切り・Primary PASS)では`secondary`のS転写が`None`のまま(捏造しない)。
- 計測の例外が判定・retry・HR Lockに波及しない。
- A/B/Cのattemptの保存形式が変わらない(27-7: 対象はX/Y/Z)。

## 6. 範囲外
βの配線(フック3点・flag)、OPEN-523/524の是正、γ(第3エンジン)、L2865と実装の不一致の是正(別件)。いずれも本書では扱わない。
