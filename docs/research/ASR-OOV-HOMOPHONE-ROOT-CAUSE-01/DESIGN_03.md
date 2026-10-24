# DESIGN_03 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_03, 2026-10-24) E2WのProduction化設計の補正(Opus条件C OF-OOV-07〜10反映)。**設計のみ・実装0・Production変更0。**

前提資料: `DESIGN_02.md`(E2の受理条件)、`OPUS_REVIEW_02.md`(OF-OOV-07〜11)、`TRIAL_03_RESULT_01.md`(実測)。本書はDESIGN_02 §2の配線案を置き換える(DESIGN_02 §2「新しい呼出点が必要・M1内1ルール」は、Opus条件Cの具体化に従い下記へ更新)。

## 1. 配線(OF-OOV-09の配線案)
- **判定ロジックの置き場**: M1 module(`er006_m1_multi_candidate_01`)の隣接関数として置く(凍結候補`freeze_candidates`・audit・`aggregate_by_ledger_key`を共有)。Trial実装 `trial_direct_ledger_phoneme_01.py`(`judge_e2w`/`whisper_position_check`)がそのまま移植元(数十行+test)。
- **呼出点**: `er006_secondary_asr_01.py` の **er109ブロック(1131〜1142行)の直後**。`if (not verified) and lang == "en" and <E2 active>:` の形で、直前のer109と同じ「既存の全層で不合格のときだけ1回」の位置に置く。`<E2 active>` は **既存の `ortho_scope.is_active_for_run()`(X/Z run scope判定)を再利用** + E2専用の単一flag読取関数(下記)。新しい範囲管理の仕組みは作らない。Family A/B/Cのscopeでは常にFalse=従来コードパス。
- **独立確認**: 同関数内で `wav_path`(`evaluate_attempt_with_cascade_detail` の引数、既に利用可能)を渡し、**既存の `_connected_speech_equivalence_local_asr_text(wav_path)`(faster-whisper small、API 0)** を **E2がPrimary単独で受理候補になったときだけ**1回呼ぶ。Noneまたは空 → 不受理(fail-closed)。新規の本番依存ではない(連結音同値層 2026-09-07承認とKPの3票判定が同関数を使用中)。
- **既に手元にSecondary(Azure)転写がある経路**(forced-secondary・LR v1・A2 fallback): OF-183どおり矛盾時に不受理(不受理方向のみ。Azure転写自体を受理の根拠にはしない)。
- **rollback flag**: er109と同形。E2 module側に `LEDGER_PHONEME_E2_ENABLED`(module定数・既定False=承認前)を置き、読取は `is_active_for_run()` 1関数のみ(flag ∧ X/Z scope)。env/引数/設定dictから変えられない。起動script・`.env`で暗黙ONにしない。DefaultOffIsolation型test(flag未設定でAPI呼出0・出力不変・副作用ファイル0)を付ける。**ユーザーが採用を承認するまで11-7の限定例外を使うか否かもFable判断(Opusは11-7の既定OFF配線を勧めていない=効果ゼロのまま仕組みだけ増えるため)。**
- **ラベル**: 受理は `PASS_WITH_WARNING` + 理由コード `E2_LEDGER_PHONEME_ACCEPT` + Warningラベル(事後試聴対象。Opus論点5)。`NORMALIZED_MATCH`等のPASS系にはしない。
- 既存の再試行/fallback/3回上限/LR/HR Lock/Style Gate/Secondary 1回+cache/Primary#2廃止/PhraseList重みは不変。PASS→NG変化なし(受理を足すだけ)。

## 2. audit(Store再利用制限とtelemetryの共通根拠)
受理時に必ず記録(`asr_judgement.<site>.ledger_phoneme_e2`):
`applied=true`, `version="e2w_v1"`, `scope`("X"/"Z"), `ledger_key`, `updated_at`(Ledger entry), `ipa_raw`, `confidence`, `candidate_set_hash`, `canonical`/`asr`/`pron`(ARPAbet)/`source`(C2_*), `canon_index`, `whisper_state`(AGREE_CANONICAL_SPELLING|AGREE_LEDGER_CMU_PRON)/`whisper_word`/`whisper_model="faster-whisper-small"`/`whisper_text_sha256`(転写自体は保存、位置周辺のみ冗長でない形で)。US/UKラベル(一致した読みのUS/UK)は任意項目(採用後に見る事項)。

## 3. Master Audio Store再利用制限(OF-OOV-10。設計のみ)
Master Audio StoreはA/B/Cとも共有(`er078_reuse_value_guard_01.guard_entry`)。X/Zで受理した音声がA/B/Cやrollback後、およびLedger entryが変わった後に流入しないよう、**er109の `OUT_OF_SCOPE_BLOCK_REASON` と同じ形**で次の2つのブロックを `guard_entry` に足す(配置: er109 UKUSブロックの直後、`kp_vote_gate_follows` 早期returnより前)。`asr_judgement` と `asr_judgement_inherited` の**両方**・全site(primary/secondary/KP票)を見る。

| ブロック理由コード(案) | 条件 | 備考 |
|---|---|---|
| `LEDGER_PHONEME_E2_AUDIO_OUT_OF_SCOPE` | E2が合否に寄与した音声(`ledger_phoneme_e2.applied` または label/warning が `E2_LEDGER_PHONEME_ACCEPT`)∧ `not e2_scope.is_active_for_run()`(A/B/C・flag False=rollback後) | 寄与の検出は**fail-closed**(`applied`はあるがauditが壊れている/欠落でも寄与ありとみなす)。再生成へ回る(再生成費用が出る=er109 rollbackと同じ) |
| `LEDGER_PHONEME_E2_LEDGER_ENTRY_CHANGED` | E2寄与あり ∧ audit内 `ledger_key` の**現行Ledger entry**が (a) 存在しない (b) `ledger_disabled` (c) confidence が medium 未満 (d) `sources` が空 (e) `canonical_spelling != surface` (f) `updated_at` / `ipa_raw` が auditと不一致 (g) 現行Ledgerを読めない(読込失敗) | 無効化・更新・削除のいずれでもブロック。fail-closed。「更新=読みが同じでも`updated_at`が変われば再確認」とし、再確認はE2/E2W再判定(API 0・ローカルWhisperは再利用不要=wavが手元なら転写キャッシュ)で行うか、再生成に回すかは実装委任でFableが判断 |

- audit に `ledger_key` を必ず残す(上記2つの判定と、採用後telemetry[`aggregate_by_ledger_key`]の両方で使う)。
- 検証test案: (1)E2寄与entryはscope外でblocked (2)scope内flag Trueでpass (3)flag FalseでX/Z内もblocked (4)Ledger entry削除/disabled/updated_at変更/confidence low化でblocked (5)E2寄与なしの既存entryは作用しない (6)asr_judgement_inherited側にだけ印があっても検出 (7)audit欠落/壊れはblocked。

## 4. 採用後に見る事項(Opus: 採用後に見ればよい事項の転記)
別候補の読み(kewl型)経由の受理件数と除外可否(承認済み原則#52の変更になるためユーザー判断)/同じ語の複数回出現/confidence low許容(meink型)/US・UKラベル/Ledger登録ごとの `E2_ACCEPTABLE_PAIRS` 自動再生成/最初のN件の事後試聴結果/**別件: Azureが全文単位で判定するため崩れやすい問題(Primary非PASS 68行中31行がNG_BOTH)。Azure削減効果はE2より大きい可能性があり別管理IDとして検討の価値あり**(`ROOT_CAUSE_01.md` §4・Opus論点)。

## 5. 撤去・残置の確認
- 撤去すべき旧ルール/旧検査: なし(Production無変更)。Trial module内: E2W判定の `uncertain_no_agreement` 受理経路と `not_provided` 受理は `judge_e2w` では通らない(`judge_direct` は比較用E2単独として残置。採用候補ではない)。
- 採用時に必要: DESIGN_02 §2の旧記述(E2をM1内1ルール、Whisper『非矛盾』)は本書で置き換え済み。
