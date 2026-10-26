# EVIDENCE_01: 救済フロー配線後のruntime evidence(X/Y/Z × Standard/Advanced、KP stage限定)+既知事例replay

KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02 / 2026-10-26 / 到達上限Status=EVIDENCE_COLLECTED(Family別)。**PRODUCTION_WIRED判定はFable**。
機械可読版=`evidence_01.json`。fresh候補ファイル=`evidence_runs/fresh_candidates/`、replay=`replay_results/`、起動ログ=`evidence_runs/*.log`、stop確認=`stop_check_02_*.json`。
KPI provenance: fresh=production_formal_path(各Family正式runnerのKP stage、新規run dir、TTS/本文生成なし) / replay=synthetic入力(凍結本文+凍結LLM出力[選定・canonicalization 1回目])+実LLM(gloss整合・救済後のgloss強制再整合・QA再判定)を正式`generate_candidates`経由で実行。

## 1. 起動コマンド全文(`--help`で引数確定。いずれもKP stageのみ。TTS/本文生成は走らない)
| Family | 新規run dir(入力は既存runの複製で揃えた) | コマンド |
|---|---|---|
| X | `er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_kprescue_ev_01`(source `er019_output/uk_train_speaker_playback/run_kprescue_ev_01`=run_nws_02のarticle.md複製、support texts複製) | `.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug uk_train_speaker_playback --run run_kprescue_ev_01 --level both --stage scaffold --scaffold-only kp --budget-jpy 40` |
| Y | `er121_output/family_y_production_01/redelivery_fee/run_kprescue_ev_01`(translate/・text/はrun_01の複製) | `.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_kprescue_ev_01 --stages kp --theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json --approved-budget-jpy 40 --tts-execution-mode STANDARD` |
| Z | `er026_output/family_z_production_e2e_01/melos/run_kprescue_ev_01`(writer/r2.md・std.mdはrun_fzcw_e1_01の複製) | `.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story melos --slug melos --run run_kprescue_ev_01 --stage kp --mode real --approved-budget-jpy 40 --tts-execution-mode STANDARD` |

起動時刻(UTC): X 09:55:52 → Y 10:00:47 → Z 10:02:28 → replay 10:08:35 → 再起動確認 X 10:11:26 / Y 10:13:59 / Z 10:16:36。各run dirは5分内3回なし(各2回)。各起動前に`stop_scope_check_01.py`(rc=0、`stop_check_02_*.json`)。rc=4はKP Human Review待機(設計どおり。失敗ではない)。
**規律からの逸脱(自己申告)**: Z初回起動はY初回起動の101秒後(委任文の「起動間隔150秒以上」を下回った)。別run dir・別Familyで、RESTART_STORM(同一run 5分3回)・STOP・rate limit等の実害は観測されていない(全起動rc=4/正常)。他の起動間隔は150秒以上。

## 2. fresh run結果(Family×レベル)
Standard=A2(a2)/Advanced=B1(b1b)。KP段はStd/Advで共通の`generate_candidates`をレベル別に1回ずつ実行(Std/Advの差は後段)。

| Family | レベル | 候補数/auto可 | (i)救済発火 | (iv)同引数再起動 | (v)外側retry | (vi) Z SRC D1・人称整合 | 備考 |
|---|---|---|---|---|---|---|---|
| X | a2(Std) | 7 / 7 | **なし(経路到達は確認)** | sha不変・API 0 | 0回(outer=1) | n/a(X) | Gate除外0 |
| X | b1b(Adv) | 6 / 6 | なし(経路到達) | sha不変・API 0 | 0回 | n/a | `is due to be shared`は有限助動詞`is`の完全文で正しく除外(救済しない) |
| Y | a2(Std) | 5 / 5 | なし(経路到達) | sha不変・API 0 | 0回 | n/a(Yは従来どおり未接続) | `redelivery fee`はCMU未登録で除外(分解救済しない=ユーザー表どおり) |
| Y | b1b(Adv) | 8 / 7 | **自然発火2件**: `it can’t be helped`→`can’t be helped`(選定段・慣用句の核IDIOM_CORE_WITHOUT_IT、辞書見出し`it can't be helped`)、`takes steps`(canonicalization段REVERT_SURFACE。LLMのkey`take steps`は最終Gate不合格→表層形を維持) | sha不変・API 0 | 0回(n_auto=7≥3。`rescued_not_auto`=1件[`takes steps`]だがn_auto≥3のためretry不要) | n/a | `takes steps`はgloss再整合REALIGNED、QA再判定=NOT_REJUDGED(LLMが再び`take steps`を返しkey不一致)→auto不可=HRでのみ採用可。R3の予想どおり |
| Z | a2(Std) | 7 / 6 | なし(経路到達) | sha不変・API 0 | 0回 | **適用確認**: 全候補`gates.src_d1=PASS`、人称整合関数を接続 | 1件`instead of demanding one`はQA FAIL(救済と無関係の既存Gate判定。REVIEW_REQUIRED) |
| Z | b1b(Adv) | 6 / 6 | なし(経路到達) | sha不変・API 0 | 0回 | **適用確認**: 全候補`src_d1=PASS` | - |

- (ii) actual model_id/routing/Prompt sha: 選定call1/call2・canonicalization・gloss・Redundancy QA・QA再判定すべて`gpt-6-luna`(現行routing契約`SUPPORT_MODEL`、process=B1_SUPPORT/A2_SUPPORT、本番ラインのモデルは無変更)。`prompt_sha256`(Prompt 2/2-V)は6 level-runすべて固定値と一致(`prompt_sha256_unchanged=true`)。canonicalization/gloss/QA再判定のtemplate・schema・developer messageは無変更(`git diff HEAD`が`er003_key_words_canonicalization.py`・`er119_kp_prompt_2v_01.py`・`er003_key_words_gloss_alignment.py`で空)。
- (iii) doc単位provenance(R2): 6件とも`rescue_provenance`あり(`lexicon_sha256=5ec8f3ae…`=コード固定値と一致、`lexicon_status=ok`、`rescue_enabled=true`、`schema=kp_rescue_v1`、`denylist_pin=5582e366…`)。救済候補は`rescue`メタ(codes・selection/canonicalization・validator_args_sha256・gloss・qa)と`flags.rescued`・`rescue_note`付き。`candidates_sha256`は全件自己整合。
- (iv) resume: 3Familyとも同一コマンドを150秒以上後に再起動し、`kp_candidates.json`のsha256不変・usageログ行数不変(X 11→11、Y 13→13、Z 12→12)=再計算なし・API 0(`evidence_runs/x_launch2.log`/`y_launch2.log`/`z_launch2.log`、rc=4で待機に戻る)。
- AI島run_ai_01のHR候補は不変(固定fixtureのresume統合test、候補ファイルバイト不変、実run側の`candidates_sha256`がfixtureと一致)。

## 3. 既知事例replay(正式`generate_candidates`経由。選定LLM・canonicalization 1回目=凍結fixture、実LLM=gloss整合・強制再整合・QA再判定)
| case | 入力 | 結果 | 実LLM call(stage別) | 実費(logged) |
|---|---|---|---|---|
| X_ai_island_a2(AI島Std本文) | call1 1回目=`studied separately`/`too soon to wave a flag`/`removing one memory`、2回目=6語句を除外 | **`too soon to wave a flag`(6語)は救済されず**attempt 1がINVALID(語数理由)→機械診断で再選定→attempt 2 PASS(短縮救済しない=ユーザー表どおり)。`studied separately`→`study separately`は救済不要の通常フロー(区分1是正済み)でauto可 | gloss newgen 1 | ¥0.42 |
| Y_redelivery_a2 | `it can’t be helped`(選定段)/`redelivery fee`(CMU) | `it can’t be helped`→**`can’t be helped`に救済**(IDIOM_CORE_WITHOUT_IT、auto可、HR候補表に`RESCUED`旗+`rescue_note`)。`redelivery fee`は1回目でCMU理由によりINVALID→2回目で除外(分解救済しない) | gloss newgen 1 | ¥0.22 |
| Y_sns_b1b | `catch their interest`(本文は`catches their interest`) | **D1再アンカーで`catches their interest`に救済**(REANCHOR_D1、auto可、旗付き) | gloss newgen 1 | ¥0.22 |
| Z_melos_b1b(r3本文) | `rose above`(LLM key`rise above the other voices`)、`held out`(LLM key`hold out one's hands`) | **M1窓内再導出で`rise above`/`hold out`に救済**(REDERIVE_M1_WINDOW。本文外の語`the other voices`/`one's hands`は捨てる)。gloss強制再整合=REALIGNED、QA再判定=PASS(key一致)、`reverify_persisted_rescue`=ok(保存引数でvalidator再実行)、Z SRC D1=PASS、auto可 | gloss newgen 1 + 強制再整合 1 + QA再判定 1 | ¥0.85 |

replay合計 ¥1.71。HRありはHR候補表(`rescue_note`/旗列)に反映、HRなしは`auto_eligible`が規則どおり決まる(M1=QA PASSでauto、revert=NOT_REJUDGEDでauto不可)ことを確認。

## 4. R3: QA再判定のkey一致率(revert/M1別)
| code | 再判定PASS | NOT_REJUDGED(key不一致) | FAIL |
|---|---|---|---|
| REDERIVE_M1_WINDOW | 2 | 0 | 0 |
| REVERT_SURFACE | 0 | 1 | 0 |

標本数は小さい(自然発生は稀)が、Opus予想どおり**revertでは一致率≈0**(LLMが同じ入力に対し前回と同じ原形化keyを返す)。revertのQA callは結果的にauto採用に寄与しない=**revertではQA callを省く案**: 節約は救済1件あたり約¥0.16(Yの1 callの実測)で量産原価への影響は軽微(記事セット当たり約¥0.3未満)。**本委任では変更しない**(Opus R3の報告のみ)。Fable判断候補(判断軸: 費用僅少、revert救済は常にHRでのみ採用という事実の受容可否)。

## 5. 未検証/制約(Family別)
- X/Z: freshの自然発生の救済は0件(各2 level-run)。Xはreplay(`studied separately`は通常フロー、`too soon to wave a flag`は非救済)、Zはreplay(M1×2)で救済経路を確認。**Xの救済発火(救済形が候補表に載る)の実run証拠は無い**(Xの既知事例はいずれも区分1是正で通常フローに戻ったため、Xの正式runnerで救済が必要になる自然事例が得られなかった)。X正式runnerの`generate_candidates`経由(共通moduleで同一コード)の到達は確認済み。
- Y: 自然発火2件(選定段の慣用句の核・revert)で最も実証が厚い。Yの選定段慣用句の核とreplayのD1も確認。
- 本委任でTTS以降は未実施(対象外)。HRあり/なしの最終確定(finalize→TTS)までのE2Eは対象外。HRなし経路(declare-absent+auto)の自動確定は`auto_select`が`auto_eligible`で決める既存仕組みで、救済候補は`rescue_auto_ok`を満たすときだけauto(testとreplay)。
- 旧kp_fn経路(er062:1364/er121旧アダプタ)は救済が発火しない(M2)。freshのX/Y/Z runはいずれも`generate_candidates`経由の正式経路(`rescue_provenance`あり=文脈内で生成された証拠)。
- `too soon to wave a flag`(6語)は救済されないまま(ユーザー表『6語以上を意味のない短縮で救済しない』のFable解釈=Opus論点5で承認範囲内)。
