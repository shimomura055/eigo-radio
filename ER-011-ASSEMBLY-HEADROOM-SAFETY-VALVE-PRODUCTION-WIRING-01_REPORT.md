# ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01 実行報告

## 1. 結論

OPEN-115(A2/B1 Assembly最終段のヘッドルーム不在)について、ユーザーが2026-09-06に
対策案(最終段ヘッドルーム安全弁+診断性改善)を`APPROVED_FOR_PRODUCTION`と決定した
ことを受け、`er003_v1_n3_01_assemble.py::stage_assemble_a2`/`stage_assemble_b1`
(初回・retry・reassembly・regenerationが共有する唯一のProduction関数、
`er006_pool_pilot_01_audio.py`量産経路含む)へ`PRODUCTION_WIRED`まで配線した。

新規単体テスト6件・既存Assembly関連回帰36件・プロジェクト全体regression
(collected=2081、2078 PASS)がいずれもPASSし、Trial-13 A2(実際にクリッピング
assertで停止していた実データ)で安全弁が発火し初めて完成音声を生成できることを
確認、No.18 A2(peak 0.933、閾値以下)では再Assembly結果がsha256完全一致すること
(安全弁が閾値以下では何もしないこと)を確認した。

## 2. 何が問題だったか

A2/B1 Assemblyの各segmentは、24kHz mono・gain適用直後の時点で
`compute_gain_for_target_rms(max_peak=0.95)`によりpeak<=0.95に制限される。しかし
直後に実行される`mono_24k_to_stereo_target()`(24kHz→48kHzへの`resample_poly`
アップサンプリング)はゲイン制御の外にあり、音声内容(語頭の破裂音・強勢等)に
依存して最大+8.9%程度のオーバーシュートを起こす(実測: Trial-13 A2の
`Point One`で0.95000→1.03502)。`assemble_with_timeline()`は`np.concatenate`のみ
(重ね合わせ無し)のため、完成ミックス全体のpeakは常にseq中いずれかのpieceの
peakと一致する。このオーバーシュートが原因で、`er002_common.py::write_wav_float`
のクリッピング防止assertが発火し、完成音声が1本も書き出せない実障害がTrial-13で
発生した。過去のA2 assemble完了14本のうち3本が既に0.95上限付近に達しており、
構造的に再発しうる状態であることも計測-16で確定していた(詳細:
`OPEN-112-TREND-THEME2-B-A2-PEAK-MEASUREMENT-16_REPORT.md`)。

## 3. 何を変更したか

`er003_v1_n3_01_assemble.py`のみを変更(Production対象は1ファイル)。

1. **`apply_headroom_safety_valve(assembled, seq)`(新設関数)**: 完成ミックスの
   peakが`HEADROOM_PEAK_THRESHOLD`(既定0.98)を超えたときだけ、エピソード全体へ
   一律スカラーgain(`閾値/peak`)を掛けて閾値以内へ収める(相対バランス不変)。
   閾値以下なら渡された配列をそのまま返す(byte同一)。原因piece(seq中の最大
   peak piece)を特定して報告に含める。安全弁適用後もpeak>1.0が残る異常時は、
   `write_wav_float()`のassertより前に、原因pieceを含む`RuntimeError`
   (`ASSEMBLY_HEADROOM_SAFETY_VALVE_INSUFFICIENT`)で停止する。
2. **`stage_assemble_a2`/`stage_assemble_b1`への配線**: それぞれ1箇所ずつ
   `apply_headroom_safety_valve()`を呼び出す。`gain_report.json`・`timeline.json`・
   新設`headroom_report.json`はいずれも`write_wav_float()`より前に書き出す
   (書き出し失敗時にも診断証跡が残るよう順序を変更)。`run_summary_assemble.json`
   にも`headroom_safety_valve`キーとして同じ内容を記録する。
3. **`CURRENT_SPEC.md`記述の訂正**: 283行目付近「音量調整」の
   「Preview/Bodyは無調整のアンカー」という記述が実装(Bodyも他segmentと同様に
   gain適用、Previewのみ無調整)と一致していなかったため訂正し、本安全弁の仕様
   (閾値・記録・例外)を新規行として追記した。

`max_peak`(0.95)自体・`mono_24k_to_stereo_target()`等の共通関数・LUFS
mastering導入・Preview経路への個別上限追加はいずれも変更していない(非採用、
ユーザー承認範囲外・影響範囲最小化のため)。

## 4. 何が改善されるか

- Trial-13 A2のような「resample overshootで0.95上限をわずかに超え、assertで
  完成音声が1本も残らない」事故が、通常時は安全弁により未然に防がれる。
- 安全弁が発火した場合でも「静かに救済」せず、適用有無・適用前後peak・
  スカラー値・原因pieceを`headroom_report.json`/`run_summary_assemble.json`へ
  必ず記録するため、品質担当者が事後に確認できる。
- 診断ファイルの書き出し順序変更により、万一`write_wav_float()`が失敗しても
  `gain_report.json`/`timeline.json`/`headroom_report.json`は既に残っており、
  原因調査が容易になる。
- `CURRENT_SPEC.md`の記述誤りが訂正され、実装との乖離が解消された。

## 5. リスクや注意点

- 安全弁が発火するケース(頻度は稀、過去14本中0本が1.0超だったが3本が0.95付近)
  では、エピソード全体の音量がわずかに下がる(閾値0.98へ収める一律スケール、
  相対バランスは維持)。これは無音のクリッピングを防ぐための意図的なトレードオフ。
- `max_peak`(0.95)自体は変更していないため、resample overshootそのものの発生は
  引き続き起こりうる。今回の対策は「起きた場合に安全側に倒す」ものであり、
  overshoot発生自体を予防するものではない(将来的な予防策の要否は別途検討)。
- No.18 A2の元の指示対象パス(`pool_n18_notifications_specfix_v2/a2`)は、
  本タスクとは無関係な先行タスク(ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-
  PRODUCTION-WIRING-23、2026-09-04)のコード変更以降、再Assemblyされていない
  古い版であることが判明した(再現するとKey Phrase blockが伸び、byte不一致に
  なる。本タスクの変更とは無関係)。Wiring-23自身がbyte-for-byte一致を確認済み
  の最新資産(`pool_n18_notifications_specfix_v2_ec_a_precision_21r/a2`)を
  正しい回帰対象として代わりに使用した(詳細は6節・DECISION_LOG.md該当エントリ
  参照)。

## 6. 変更ファイル

- [er003_v1_n3_01_assemble.py](er003_v1_n3_01_assemble.py)(Production変更本体)
- [er011_assembly_headroom_safety_valve_production_wiring_01_test_01.py](er011_assembly_headroom_safety_valve_production_wiring_01_test_01.py)(新規テスト、6件)
- [CURRENT_SPEC.md](CURRENT_SPEC.md)(283行目訂正+新規行追加)
- [DECISION_LOG.md](DECISION_LOG.md)(新規エントリ`ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01`)
- [OPEN_ITEMS.md](OPEN_ITEMS.md)(OPEN-115を`RESOLVED / PRODUCTION_WIRED`へ更新)

## 7. テスト結果

- 新規`er011_assembly_headroom_safety_valve_production_wiring_01_test_01.py`: 6件全PASS
  (peak<=閾値でbyte同一/peak>閾値で一律gain・記録/適用後も1.0超で`RuntimeError`/
  write前にaudit証跡存在/`stage_assemble_a2`・`stage_assemble_b1`それぞれ1箇所配線)。
- 既存Assembly関連回帰(`er011_no18_tight_speech_and_trim030_production_wiring_23_test_01.py`・
  `er008_n8_qa_hardening_21_gate_test_01.py`・`er008_a2_slowdown_invariant_19_test_01.py`・
  `er008_audio_validation_gate_05_test.py`、計36件)全PASS。
- プロジェクト全体regression(`run_project_regression.py`、collected=2081): 2078 PASS・
  3 failed。3件は`er003_test_p2j_investigate`(OPEN-77既知のprefix別集計meta-testバグ)で、
  `git stash push -- er003_v1_n3_01_assemble.py`で本タスクの変更を一時退避しても同一の
  3件が失敗することを確認し、本タスク以前から存在する既知の無関係failureと判定した。

## 8. Runtime evidence

1. **Trial-13 A2**(`er011_output/open112_trend_theme2_b_full_audio_trial_13/a2/`)を
   修正後の`stage_assemble_a2()`で`--assemble-only`実行(narration再生成なし、
   新規TTS/ASR課金0)。安全弁が発火し、`headroom_report.json`へ
   `{"threshold": 0.98, "peak_before": 1.0350189, "cause_piece": "Point One",
   "cause_piece_peak": 1.0350189, "applied": true, "scalar": 0.94684262,
   "peak_after": 0.98}`を記録、完成音声(duration 372.146秒、peak 0.98、
   clipping無し)を`assembled/English_Your_Way_A2_OPEN112_TREND_THEME2_B_FULL_AUDIO_TRIAL_13.wav`
   として初めて生成した(OPEN-115発見時点では書き出し不能だった)。原因pieceは
   計測-16の実測(`Point One`)と一致。B1側は本タスクと無関係なKey Phrase 3件
   (Human Review Lock STOPPED、OPEN-116管轄)でGate Blockedのまま(変更していない)。
2. **No.18 A2の閾値以下regression**: `pool_n18_notifications_specfix_v2_ec_a_precision_21r/a2`
   (peak 0.93346、duration 351.824秒、ER-011-NO18-...-23でbyte-for-byte一致確認済みの
   最新資産)のnarration/key_phrases/audit(tts_generation_results.json)を
   `er011_output/assembly_headroom_wiring_01/n18_a2_regress/`へコピーし、修正後の
   `stage_assemble_a2()`を実行。結果はduration 351.824秒・peak 0.93346・
   `headroom_safety_valve.applied=false`、出力wavのsha256
   `97034b358e082271b87d67b42e1ecbfb3f4d4180058e1b1bd2d4508efc71e7f9`が
   ユーザー承認済み資産と完全一致した(安全弁が閾値以下では何もしないことを実データで確認)。

## 9. Gate 3チェックリスト充足状況

- Production正式初回経路への配線: 充足(`stage_assemble_a2`/`stage_assemble_b1`、
  `er006_pool_pilot_01_audio.py`量産経路含む唯一の共有関数へ1箇所ずつ)。
- retry/fallback/regenerationとの整合: 充足(単一関数のため自動的に整合、
  単体テストで1箇所配線を固定)。
- DEV/Trial-onlyではないこと: 充足(Production本体ファイルのみ変更)。
- Production runtimeでの実発火: 充足(Trial-13 A2で実発火・完成音声生成)。
- 必要testのPASS: 充足(新規6件・既存回帰36件・全体2078/2081)。
- runtime evidence: 充足(8節)。
- CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS: 充足。
- Git反映: 充足(10節)。
- approved specとProduction挙動の一致: 充足(閾値0.98・記録必須・RuntimeError化を
  指示どおり実装、`max_peak`変更・共通関数改修・LUFS導入・Preview個別上限は
  指示どおり不採用)。

## 10. Git

変更ファイルのみファイル名指定でstage・commit・push(詳細はコミットログ参照)。
