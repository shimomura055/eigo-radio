# TRIAL_REPORT_01: FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01 委任_01 (2026-10-16)

性質: Trial(Offline、Trial専用dir)。**Trial結果はProduction採用ではない。Coffee現行Prompt/style profile不変。採用はユーザーのAPPROVED_FOR_PRODUCTION判断。**
主観評価(速度・ポーズ・自然さ・明瞭性)は**未実施(ユーザー試聴待ち)**。本書の数値は「数値上の傾向」であり、「試聴合格」ではない。

## 1. 確認結果(API 0)

- 管理ID/ユーザー指示原文: `docs/pm/delegation_log/2026-10-16_FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01_USER.md`(委任文全文 `_01.md`、T-0 check=PASS)。
- 対象原稿(現行Production正本、read-only): `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/b1b/audit/tts_generation_results.json` の `key_phrases.<rank>.explanation.explanation_text`(5本、逐語。`audit/plan.json`にも保存)。
  1. time lag: a delay between a change happening and its effect being seen or felt
  2. show up: to become visible or noticeable in a place or situation
  3. come down: to become lower, especially in price or amount
  4. pump one's fist: to raise a closed hand in the air to show excitement or victory
  5. hold on: to wait or pause before doing something
- Productionで実際に送信されるStyle: `er019_family_x_audio_production_runner_01.py:1020-1036`(`_kp_explanation_style`)→`style_profile_mod.resolve_role_style("coffee_n01_r2_p3_e1", ROLE_KP_EXPLANATION_EN, "b1b", base)`→`er019_family_x_style_profile_01.py:67-72`のP3_TEXT(141文字、sha256 `a8aaec59...e677acc`、profile記録 `audit/style_profile.json`)。完成音声側の記録 `style_prefix` も同文字列。
- **P0照合**: 解決関数の戻り値とユーザー指定P0は**完全一致**(`audit/plan.json` style_check.identical=true、前後に付加される文言なし、Pronunciation hints_applied=false[5本とも])。不一致時の「ユーザー指定文字列優先」は発動せず。
- TTS経路: Production leaf `generate_key_phrase_explanation_en_verified`(`er019_family_x_audio_production_runner_01.py:727-742`)→`repro01.generate_narration_snippet_verified_strict`(`er003_v1_repro01_main_generate.py:197-`)→`p9a.generate_narration_snippet`(tts_backend=`speech_metadata_flash_lite`、model `gemini-3.8-flash-lite-tts`、Aoede、`TTS_EXECUTION_MODE=STANDARD`で同期)。trim=`KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS=0.30`(`er003_v1_repro01_main_generate.py:649`)。max_attempts=`KP_EXPLANATION_MAX_ATTEMPTS=3`。
- ASR/QA経路(Productionと同一leaf内): Primary OpenAI(`KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT`)→`secondary_asr.evaluate_attempt_with_cascade`(統一judge、`enable_non_latin_cascade=True`)→長さ検査→disfluency QA(`disfluency_qa=True`)。本Trialは**leaf関数そのものを呼ぶ**ため同一。
- 既存完成音声(参照、read-only、上書きなし): `.../b1b/narration/kp{1..5}_explanation_en.wav`(Production 5本、P0と同一Promptの別take)。
- 既存資産の再利用確認(T-2追記): (1)差分再生成=不要(40 clipは全て新規Style条件のため全件新規生成が本Trialの設計) (2)Master Store等の音声再利用cache: 本leaf(p9a.generate_narration_snippet)は参照しない(0件) (3)`--budget-jpy 40`を明示 (4)想定外の全再生成ではない(計画どおり40 clip)。

## 2. 費用見積(API 0、実行前)

単価(`er058_output/unified_all_roles_production_wiring_01/RUNTIME_EVIDENCE_06.md:113`): TTS JPY0.062/clip、OpenAI Primary ASR JPY0.0094/call、Azure Secondary JPY0.0444/秒(cascade発動時のみ)。
- 期待(全40 clipが初回合格): 40 x (0.062+0.0094) = **JPY 2.86**。
- 悪化(約30%がNGで平均1.3 attempt、Secondary 5秒): 約JPY 4.5〜6。
- 最悪(全clipが3 attempt、毎回Secondary 5秒): 120 x (0.062+0.0094+0.222) = **約JPY 35** (< 上限JPY 40)。よって(t1)非該当。

## 3. 実行

- 手順: `TTS_EXECUTION_MODE=STANDARD er080_coffee_kp_pacing_trial_01.py --prompt-set all --execute --budget-jpy 40`。実行前 stop_scope_check rc=0(`audit/stop_check_pre_run.json`)。1回のみ実行、再起動なし。
- 隔離: HR queue / semantic telemetry / pronunciation ledger はTrial dir内へ差し替え(`audit/isolated_state/`、HR queue 0件)。Master Store・Production出力dirへの書込なし。
- **逸脱(shared state)**: Production leaf内部の `review_lock.append_attempt_history_event` が `er011_output/attempt_history.jsonl`(共有file)へ**40行を追記**した(theme_id=p0〜p7、segment_id=kp{1-5}_explanation_en、2026-10-16T08:14〜08:17、事前隔離の対象に入れ損ねた)。実行前後のsha256差分に出ており(`audit/shared_state_sha_{before,after}.json`、`run_summary.json`)、他委任の並行追記も含まれるため差分の全量は本Trial由来ではない。Productionの既存記事(coffee_prices等)の行は変更なし(追記のみ)。当該40行は自分では削除・編集していない(並行委任との競合を避けるため)。扱いはFable判断。

## 4. 生成成否(8 Prompt x 5本 = 40 clip)

**40/40 初回attempt合格(ASR verified=True、NORMALIZED_MATCH、Secondary呼出0、HR該当0)**。TTS呼出 40、失敗 0、再試行 0。`audit/clip_results.jsonl`。

| 候補 | KP1 | KP2 | KP3 | KP4 | KP5 |
|---|---|---|---|---|---|
| P0〜P7(全て) | OK(1回) | OK(1回) | OK(1回) | OK(1回) | OK(1回) |

## 5. 指標(`metrics.json`、手法=`er080_coffee_kp_pacing_metrics_01.py`冒頭docstring)

手法: RMS(20ms窓/10ms hop)、発話フレーム=clip内p95 dB-35dB超、文中ポーズ=発話の最初〜最後の間の80ms以上の無音、**文末無音=最後の発話以降**(Production trim余白0.30sを含む)。WPM=語数/発話区間x60。既存Productionに文中ポーズ専用の計測関数は無く新設(閾値は全clip共通で固定)。

### 5.1 候補別5本平均(数値上の傾向のみ)

| 候補 | 全長(s) | WPM(発話区間) | 文中ポーズ数 | 文中ポーズ計(s) | 最長(s) | 200ms以上の数 | 文末無音(s) |
|---|---|---|---|---|---|---|---|
| P0(現行Prompt新規) | 4.78 | 144 | 2.0 | 0.33 | 0.21 | 0.6 | 0.25 |
| P1 | 4.59 | 150 | 0.6 | 0.14 | 0.14 | 0.4 | 0.22 |
| P2 | 4.81 | 142 | 1.4 | 0.26 | 0.21 | 0.6 | 0.26 |
| P3 | 4.54 | 153 | 1.6 | 0.22 | 0.15 | 0.2 | 0.25 |
| P4 | 5.14 | 131 | 2.4 | 0.36 | 0.20 | 0.4 | 0.27 |
| P5 | 4.91 | 139 | 1.4 | 0.31 | 0.26 | 0.8 | 0.25 |
| P6 | 4.74 | 143 | 1.8 | 0.34 | 0.21 | 0.8 | 0.24 |
| P7 | 4.35 | 159 | 1.0 | 0.16 | 0.13 | 0.2 | 0.25 |
| 既存Production完成音声(参照) | 4.85 | 140 | 2.2 | 0.30 | 0.17 | 0.2 | 0.26 |

### 5.2 clip別(全長s / WPM / 文中ポーズ数-計s / 文末無音s)

| 候補 | KP1 | KP2 | KP3 | KP4 | KP5 |
|---|---|---|---|---|---|
| P0 | 5.48/155/2-0.38/0.19 | 5.30/126/3-0.51/0.29 | 4.96/108/1-0.32/0.24 | 4.64/190/2-0.25/0.26 | 3.50/141/2-0.21/0.28 |
| P1 | 5.88/146/1-0.26/0.25 | 4.92/134/1-0.11/0.19 | 4.00/130/1-0.33/0.13 | 5.02/174/0-0.00/0.26 | 3.12/164/0-0.00/0.29 |
| P2 | 5.24/164/1-0.25/0.26 | 5.70/117/2-0.27/0.27 | 4.42/124/1-0.34/0.26 | 5.08/172/1-0.11/0.28 | 3.60/135/2-0.35/0.25 |
| P3 | 5.78/147/1-0.19/0.25 | 4.66/145/2-0.23/0.29 | 4.40/122/2-0.33/0.22 | 4.90/175/2-0.24/0.27 | 2.96/174/1-0.09/0.24 |
| P4 | 6.24/137/1-0.09/0.25 | 5.10/132/1-0.11/0.28 | 4.56/116/5-0.78/0.25 | 5.98/143/2-0.27/0.28 | 3.84/125/3-0.53/0.28 |
| P5 | 5.86/146/2-0.26/0.23 | 5.06/133/1-0.27/0.29 | 4.74/114/1-0.46/0.26 | 5.40/160/2-0.48/0.27 | 3.48/140/1-0.09/0.20 |
| P6 | 5.50/156/2-0.55/0.26 | 5.08/133/2-0.26/0.29 | 4.04/130/1-0.33/0.10 | 5.50/157/2-0.40/0.27 | 3.58/139/2-0.17/0.26 |
| P7 | 5.74/149/0-0.00/0.24 | 4.10/169/0-0.00/0.26 | 3.96/139/3-0.56/0.25 | 4.60/188/1-0.11/0.23 | 3.34/148/1-0.15/0.28 |
| 既存Prod参照 | 5.78/149/1-0.12/0.26 | 4.92/137/2-0.17/0.26 | 4.52/121/3-0.61/0.27 | 5.28/164/2-0.31/0.27 | 3.76/126/3-0.29/0.23 |

### 5.3 数値上の傾向(主観評価ではない)

- **文末無音は全候補でほぼ同じ(0.22〜0.27s)**: Production trim余白(0.30s)の影響が支配的で、Promptによる差は見られない。改善対象は文中ポーズのみ。
- 文中ポーズ(数・合計)が少ない: P1(0.6回/0.14s)、P7(1.0回/0.16s)、P3(1.6回/0.22s)。P0は2.0回/0.33s。P4(2.4回/0.36s)は増加方向、P6・P5・P2はP0と同程度。
- 速度(WPM): P7 159、P3 153、P1 150が速い(P0 144比で+6〜+15)。P4 131が最も遅い。P2 142・P5 139・P6 143はP0付近。ユーザー指示は「速度変更は控えめ」のため、P7(+15 WPM)は「通常ニュース朗読へ近づく」側に寄る可能性があり試聴確認が必要。
- 数値上の上位候補(主観未確認): **P1**(文中ポーズが最少、速度は控えめに上昇)、**P3**(ポーズ減・最長ポーズも短い・速度は中程度に上昇)、**P7**(ポーズ減だが速度上昇が最大)。
- 安定性: 5本で一貫した傾向は限定的。P1は5本中4本でP0以下の文中ポーズ数だがKP1は同数前後。P7はKP3でポーズ3回(P0は1回)と逆転。KP別のWPM差(108〜190)は語長・原稿差が支配的。
- **注意(ノイズ)**: 各セルは1 takeのみ。既存Production(P0と同一Prompt・別take)とP0新規の差(WPM 140 vs 144、文中ポーズ2.2 vs 2.0)がtake間ばらつきの目安で、±5 WPM・±1ポーズ程度の差は有意と言えない。ノイズ基準の追加takeはユーザー承認なしに実施しない(禁止)。

## 6. ASR/QA結果

40 clipとも: Primary(openai_asr)のみ・分類 NORMALIZED_MATCH・length_ok・disfluency検査実施(checked=true)・Secondary(Azure)呼出0・Human Review該当0・attempt 1回。clip別のASR text・判定は `audit/clip_results.jsonl`。全clipのASR文字列は原稿と大小文字・句読点以外一致。

## 7. 費用・呼出

TTS 40 call(失敗0、再試行0)、Primary ASR 40 call、Secondary 0。実費(推定、単価x回数。leafはcost loggerへ記録しない既知の事象 RUNTIME_EVIDENCE_06 D1): **約JPY 2.86**(見積期待値と一致、上限JPY 40の約7%)。API実費の請求照合は未実施(推定値)。
使用モデル: TTS `gemini-3.8-flash-lite-tts`(ユーザー固定条件=現行Production同一。25節の「最新モデル原則」の例外=ユーザー指示§2。最新か否かの比較はしていない)、Voice Aoede、ASR=Primary OpenAI(現行Production既定)。

## 8. Trial Status案

- 全体: 8 Prompt x 5本の比較が成立し(40/40 QA通過)、試聴ページ提示済み=`VALIDATED`(改善候補として評価可能)。ただし**採否は主観評価(ユーザー試聴)が必要なため `USER_DECISION_REQUIRED`**(Production反映なし)。
- 候補別(数値上): P1/P3/P7=改善方向の数値(主観未確認)、P0=基準、P2/P5/P6=P0と同程度、P4=ポーズ増・遅い方向(数値上は改善効果なし)。REJECTEDの確定はしない(主観評価前)。

## 9. ユーザー判断事項

1. 試聴ページで8候補x5本を聞き比べ、採用候補(または現状維持)を選ぶ。採用する場合のみ別途 APPROVED_FOR_PRODUCTION → Production Wiring。
2. 追加検証(同一Promptの追加take、上位候補の絞り込み再Trial)が必要かの判断(本Trialでは実施しない)。

## 10. 試聴ページ

`https://shimomura055.github.io/eigo-radio/user_test/coffee_kp_pacing_trial_01/`(Pages反映確認結果は §11)。

## 11. Gate 7 URL確認

(push後に記入)
