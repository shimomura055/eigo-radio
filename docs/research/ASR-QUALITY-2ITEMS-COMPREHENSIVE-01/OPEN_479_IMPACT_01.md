# OPEN-479 影響分析 01 (委任_06 T-1、API 0・コード変更0)

結論: **gate不通過 (STOP、修正せずFableへ)**。理由2点。(1) 指定の1行修正は共有関数`er012_b...generate_voice_body_wide_margin`を直すため Family B/C Production(point_one/point_two、Family C body)の挙動も変える(27-7範囲外)。(2) replayで判定結果(verified/state)の変化は0件だが、PNAP/RET以外の層(Tier3)による監査ラベル変化が会話clip 66件中1件ある(厳密にはgate(i)(ii)不成立)。推奨=Z scope限定の修正(下記)。

## 1. segment_id / judge_role 参照層 (会話clipで None -> FULL_STORY に変わった時の影響)
Z会話clipの`full_story_part{n}_c{k}`は`er020_tts_retry_local_rewrite_01.py:136`のパターンで FULL_STORY に解決される(narrator clipは既に解決済み)。
| 層 | file:line | None -> FULL_STORY での変化 | 承認仕様上の期待 |
|---|---|---|---|
| Tier1 数値等価early-exit | er006_preprod_hardening_01_validation.py:1350-1357 (classify_asr_match) | 数値/通貨/年等のみの差を NUMERIC_EQUIVALENCE_MATCH で受理 | 5role適用(EN-ASR-SEMANTIC-EQUIVALENCE Phase A、2026-09-27承認)。会話clipでは現状不適用 |
| Tier3 plural/entity corroboration | er006_secondary_asr_01.py:1020-1026 | UNCERTAINのplural_only/entity_onlyをAzure共有cache経由でcorroborate | 5role適用(Phase B)。replayで1件の警告ラベル変化(下記) |
| 統一judge role | er006_secondary_asr_01.py:1181,1215 / er078_asr_unified_judge_01.py:459 | 監査recordのroleのみ(判定ロジックは参照せず) | PNAP/RETの前提 |
| PNAP role gate | er103_proper_noun_alarm_policy_01.py:336 | ROLE_NOT_APPLICABLE -> 評価対象に(今回の修正目的) | X/Z正式経路で有効(UDR #168) |
| RET (entity table relabel) | er103_proper_noun_alarm_policy_01.py:435 (role引数) | PNAP評価経由でのみ到達 | 同上 |
| secondary_accept classify / 非ラテンKP層 | er006_secondary_asr_01.py:1090,1193 | Tier1がSecondary転写にも適用 / 非ラテンはKP限定(会話は不発) | Tier1と同じ |
| connected speech | er006_secondary_asr_01.py:947付近 | `enable_connected_speech_equivalence_layer`引数で独立制御、segment_id非依存(変化なし) | - |
| HR Lock / queue | er011_human_review_lock_01.py:315,364,482 | leaf側で`derive_segment_key(out_path)`を自前導出済み(変化なし) | - |

## 2. 意図的省略か
- er012_b:553のsegment_id不在はFamily B Phase 1初版(1a7f00810、2026-09-08)から。後日(2026-10-12 Z Opus M6)`er020:133-136`で「Z Part内Dialogue clipをFULL_STORYと認識する後方互換追加」が入っており、Zでは会話clipにも5role適用が意図されていた。意図的にroleを外した設計決定はDECISION_LOG/CURRENT_SPECのGrepで見つからない(OPEN-479は新規検出)。**意図的でない(漏れ)** と判断。
- ただし該当関数は共有: 呼出元 er012_b_family_production_runner_01.py:349(Family B Voice A/B body)・er013_family_c_production_runner_01.py:508(Family C)・er063:849,853(Z会話)・a2 slowdown wrapper。Z以外の呼出元は現状 role=None。

## 3. replay (API 0、`er103_output/ret_prod_z_evidence_01/open479_replay_01.py`、結果`open479_replay_before.json`)
対象: Z完成run 36ファイル(mock/STALE/backup/preserve除外)の会話clip。
- Level1(primary判定 val.evaluate_attempt、segment_id None vs 解決): 重複除去129 attempt -> **変化0**
- Level2(全層、Azureは保存済みSecondary転写で置換、is_last_slot=False固定=HR/Perplexity呼出なし): 66ユニーク最終attempt、baseline(None)が保存stateを再現=65/66(1件はLedger状態差で再現不一致)。変化2件:
  - 『開いた窓』a2 full_story_part3_c2(`Birdie, why do you bound?` / Secondary `Bertie`): state PASS_WITH_WARNING のまま、Tier3(entity_only)がPrimaryで受理、警告 SECONDARY_CONFIRMED -> SECONDARY_CORROBORATED、Secondary呼出の有無のみ変化。**verified/state不変**。
  - 同 b1b part3_c2: layers に tier3 が増えるのみ(secondary unavailable維持、verdict不変)。再現不一致の1件。
- PASS->NG / NG->PASS = 0件。PNAP/RET受理以外の変化=警告ラベル/監査layers 2件(いずれもTier3、承認済みFULL_STORY仕様の通常動作)。
- 限界: PNAP/RET発火は実run(Ledger/entity table/supply状態依存)でないと決定論replay不可。STOPPED clip(c14)は保存Secondary転写なし。

## 4. gate判定と推奨
- gate: (i)不成立(Tier3ラベル変化2件)、(ii)不成立、(iii)成立(意図的省略なし)。厳密にはSTOP。さらに共有関数のためB/Cへ波及。
- 推奨案(Fable判断): **er012_b:553で`segment_id`を X/Z run scope内(`er109_xz_scope_01.is_active_for_run()`)のときだけ渡す**。B/C(scope外)は完全に従来どおり(DefaultOff同型)。Zではnarratorと同じTier1/Tier3/PNAP/RETが会話にも適用され、これはer020:133-136の意図およびUDR #168受入条件1(X/Z双方で有効)に整合。Tier3ラベル変化(verdict不変)を承認範囲とみなせるかをFableが判断。厳密に避けたい場合の代替=PNAP/RET用の別引数`pnap_segment_id`を`evaluate_attempt_with_cascade_detail`に追加(er006の編集が増える)。
- 修正は未実施(コード変更0、有料run 0、費用0円)。
