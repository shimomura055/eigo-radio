# BUDGET_LOG_01 — FAMILY-Y-VOICE1-MALE7-TRIAL-01(JST 2026-10-26)

費用は `tools/ym7_cost_01.py`(`docs/pm/tools/daily_dev_cost_01.py`の単価で `er121_output/family_y_voice1_male7_trial_01/cost_log_*.jsonl` のみ換算、USD/JPY=daily_dev_cost_01既定)。未換算行0。
全起動で `TTS_EXECUTION_MODE=STANDARD`、起動前に `tools/stop_scope_check_01.py`(rc=0、結果は `logs/stop_check_*.json`)。DESIGN_01 sha256=`1e8dec1ccd4bd9461a1b128e7449cb2911fac89114b3b097ed74e1c6e49b3f11`(生成前に固定、完了時点でも一致)。

## 起動ごと(時刻は `logs/launch_times.txt`)
| # | 起動時刻 | process(plan・batch) | 担当take | 実費(円、cost_log換算) |
|---|---|---|---|---|
| 1 | 14:53:50 | Phase 1 batch1 | 21 | 48.1 |
| 2 | 14:56:46 | Phase 1 batch2 | 21 | 44.5 |
| 3 | 14:59:38 | Phase 1 batch3 | 22 | 33.1 |
| 4 | 15:22:55 | Phase 1 batch3 slice13:22 逆順(尾部前倒し) | 9 | 15.0 |
| 5 | 15:27:09 | Phase 1 batch3 slice8:13 逆順 | 5 | 13.5 |
| 6 | 15:30:45 | Phase 1 batch2 slice13:21 逆順 | 8 | 7.2 |
| 小計 | | **Phase 1: 64 take(新規5Voice 60 + Algieba対照4)** | | **161.4** |
| 7 | 15:45:53 | Phase 2 batch1 | 7 | 24.0 |
| 8 | 15:49:37 | Phase 2 batch2 | 8 | 23.4 |
| 9 | 15:53:26 | Phase 2 batch3 | 7 | 20.6 |
| 10 | 15:57:22 | Phase 2 batch4 | 7 | 17.9 |
| 11 | 16:00:46 | Phase 2 batch5 | 7 | 11.8 |
| 12 | 16:11:36 | Phase 2 batch5 slice4:7 逆順 | 3 | 6.5 |
| 13 | 16:15:15 | Phase 2 batch4 slice4:7 逆順 | 3 | 5.6 |
| 14 | 16:18:30 | Phase 2 batch3 slice4:7 逆順 | 3 | 4.7 |
| 小計 | | **Phase 2: 36 take(Puck/Orus/Algieba各12)** | | **114.7** |
| 合計 | | **100 take(目的の100 takeに加え重複2 take、下記)** | | **276.13** |

- 同一run 5分以内の起動は最大2回(14起動すべて直前の起動から172秒以上=150秒以上を満たす。最短は#1→#2の176s・#2→#3の172s)。再起動(失敗後の再実行)は0回。rc≠0終了0回。
- 共有台帳への書込: 本Trialのcostは本Trial専用の`cost_log_*.jsonl`のみ(正式経路が`er011_output/attempt_history.jsonl`等へ追記する場合の行数は別途`git diff --stat`で確認、本委任由来の追記は未確認=RESULT_PACKET参照)。
- 実費の内訳(概数): Gemini TTS+ASR(whisper系`openai_asr`)+retry時のAzure/OpenAI補助。fallback(minimal_fallback)へ落ちたtakeのcostも含む。

## 費用の評価
- 見積(DESIGN_01 §5-4): Phase 1 約150円・Phase 2最大約84円・合計最大約234円 → 実績 **276.13円**(Phase 1 161.4 / Phase 2 114.7)。
- **Guardrail 250円を26.1円(+10.5%)超過、案件300円は未超過**。超過の原因(把握済み): Phase 2対象に含めた**Algieba(現行Voice 1)がRepetition QAで毎回旗が立ち再生成が続く**(fresh take最終OK率 6/16=38%、平均main attempt 2.31回/take+fallback)ため、Phase 2のAlgieba 12 takeが見積(2.34円/take)の約3〜4倍かかった。Puck(1.21 attempt/take)・Orus(1.33)は見積どおり。
- Guardrail超過後の継続条件(承認済みscope内・原因把握済み・異常retryでない・残作業明確・追加費用が合理的・QCD上の便益明確)を確認: (a)事前固定の停止規則どおりのPhase 2で新規の仕様追加なし (b)Algieba retryはProduction retry/fallback規則どおり(独自のretry拡大・Gate回避なし) (c)Phase 2完了後の追加生成なし。暴走疑いなし(大量API・無意味なretry loop・scope外処理なし)。

## 事故・重複(開示)
- 尾部前倒しのため、旧コード(`--reverse`・着手済みskipなし)で動いていたforward processと、後から起動した逆順processが同一takeを重複生成した:
  1. Phase 1 `a2 body3 Iapetus take1`: 片方OK・片方STOPPED(minimal_fallback)で`result.json`は最後に書いた側(STOPPED)。attempt wavは両processのもの(attempt1〜5)が1ディレクトリに混在。→ attemptは独立なTTS 1 drawとして有効なためsample集計(unit=attempt)には全て含め、take単位の最終status集計ではSTOPPED(保守側=Iapetusの率を下げる側)として扱った。
  2. Phase 2 `a2 body2 Algieba take4`: 両方OK、attempt1〜3(混在)。同様にsampleは全て有効、takeはOK。
  - 影響: 無駄な追加TTS 約5生成(約8円)。判定への影響は、(1)の1 takeがIapetusの最終OK率(9/12)を保守側へ1 take動かす(OKと数えれば10/12=83%でも§7-4の0.9未満=不変)のみ。
  - 是正: 以後の逆順起動は`--reverse`(着手済みskip)で重複を防ぐ設計に変更済みだが、forward側が旧コードだったためforward側のskipは効かなかった。原因はforward processのframe位置を過小評価して尾部slicesを近づけたこと。
