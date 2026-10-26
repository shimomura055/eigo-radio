# BUDGET_PLAN_01 — Family Z 文脈・感情付きTTS Production Wiring 費用・時間計画

管理ID: FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01(Phase 0)。**本委任の費用=JPY 0(API 0)**。
**300円判定: 案件全体の見積(Phase 2、期待約48円・保守約60円・天井約75円)は全て300円以下=Fable自律枠(7-7)。300円超見込みなし。**
上限¥200(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。

使用単価は全て出典付き(推定値は使わない。未確認は『未確認』)。日次(JST 2026-10-26): 本委任開始前の既使用 約123円+並行案件A実費(Cap 150)/1,000円。

## 1. 6区分(ユーザー原文§5)— Family Z専用のコスト増

出典コード:
- T1=`docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/BUDGET_LOG_01.md`(実費。委任_04表)。T2=同`EVAL_01.md` §4。
- T3=`er118_output/fz_full_episode_trial_01/raw_usage_log.jsonl`(Trial実測、provider別token)。
- P1=`er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/{cost_log.jsonl,e2e_stage_log.jsonl}`。P2=同`melos/run_e2e_06/…`。
- N1=`er118_output/fz_full_episode_trial_01/*/*/llm/emotion_notes.json`の`cost_jpy`。
- 単価式=`er118_fz_dialogue_context_tts_trial_01.py:574〜581`(USD/JPY 160、TTS入力$1.0/M・出力$20/M、`gemini-2.5-pro-preview-tts`)。

| # | 区分 | 1作品(Std+Adv=1セット)あたり | 出典・導出 |
|---|---|---|---|
| 1 | 文脈・感情情報生成(LLM、gpt-6-luna、level単位1 call) | 猿の手 **0.268円**(Std 0.1243+Adv 0.1438)、メロス **0.272円**(0.1222+0.1495)。cost log基準では4 call初回計0.65円(≒0.16円/call)で、算定基準により0.27〜0.33円/セット | N1(`cost_jpy`)、T1(『cost log基準 約0.65円/4 call。単価式では0.92円=pricing snapshot差』) |
| 2 | 文脈・感情付きTTSの費用差 | **約+0.098円/TTS call**(入力token差のみ)。TTS call/セット=猿の手 約32.6〜33.8、メロス約21.4〜22.2(clip数×k)。→ **猿の手 +3.2〜3.3円、メロス +2.1〜2.2円** | T3: Trial ctx 837入力token/call(56 call平均)。P1/P2: 現行Z dialogue 214〜248入力token/call(cost_log集計: 猿の手Std 219・Adv 248、メロスStd 214・Adv 214)。差約+610 token×$1.0/M×160=+0.098円/call。出力token(音声長)は同等として差に含めない(Trial 56 call: 合計24.158円=入力7.5円+出力16.7円)。**EVAL_01の概算『+約0.08円/call』(式は未記載で再現未確認)より約2割高い** |
| 3 | Retry/Fallbackの発生率と期待費用 | 現行: dialogue 667 entry中 attempts≥2が22件(3.3%)、k_prod=1.019。ctx(Trial): k_ctx=56/53=1.057(猿の手・メロスAdv=1.0、メロスStd=1.3、NG clip 1[3 call])。新仕様のfallback(ctx 2回NG)発生は**1/53 clip(1.9%)**。期待fallback件数=猿の手 約0.6/セット・メロス約0.4/セット(Wilson 95%上限9.9%/clip→3.2/2.1件)。fallbackの3回目は従来style(入力token少=約0.098円安)。**期待費用差(k_ctx−k_prod)×clips×0.43円 = 猿の手 +0.5、メロス +0.3円**(区分2の『clips×k』に既に含む=二重計上しない)。cooldown自体は費用0(待機のみ) | T1(k_ctx)、EVAL N5、本書§2。実fallback率はPhase 2で再測(n=53で幅が広い) |
| 4 | Local Rewrite・ASR追加費用 | **LR=Z dialogueに未配線のため追加0円**(J-1の既定。配線する場合は別見積)。ASR=ctxでPrimary NGが増えるとSecondary(Azure 0.0700円/call)が増えうる。Trial実測: openai ASR 84 call=1.2826円(0.01527円/call)、Azure 2 call=0.1399円 → clipあたりASR約0.027円。現行比のASR増分はk差に比例(≲+0.1円/セット)。notes LLM再call=0(run内cache) | T1(provider別)、EXISTING_SPEC_CHECK §2(LR未配線) |
| 5 | Family Z 記事セットあたり総量産単価 | **現行(実測参考): 猿の手 run_sf_prod_01 = 46.82円**(writer 11.23+std_adjust 8.14+plan 0.42+support 0.44+kp 1.41+tts_b1b 11.78+tts_a2 13.24+再生成 0.16)。**新仕様の増分(1+2+3+4)= 猿の手 約+3.5〜3.8円、メロス 約+2.5〜3.0円**(EVAL_01の+1.80〜+3.26円より上振れ。理由=区分2の単価)。予測: 猿の手 約50.3〜50.6円/70円(約72%)、増分は目標の約5〜6%。メロスの完全セット実測は**未確認**(run_e2e_06は本文stageを再利用した部分実行で28.68円は全体ではない)。『Z 1生成セット』の構成はPM_GOVERNANCE 15-8の標準表に**行が無い**ため、Phase 2の原価測定で構成を明記してから追加する(15-9) | P1(e2e_stage_log `spent_jpy_cumulative`最終46.8174)、15-8/15-9 |
| 6 | 制作時間への影響 | (a)notes生成: 1 call 12〜26秒/level(Std/Adv並列で最長1 call分)。(b)ctx TTS clip生成: Trial平均9.7秒/clip(猿の手Std 9.25・Adv 8.80、メロスStd 12.28・Adv 9.53)。現行Z dialogueのclipあたり生成時間は**未確認**(cost_logに経過秒はあるが再集計未実施。差は入力token増のみのため軽微と推定するが未確認)。(c)fallback発生時のみ+600秒(clip内ブロック待機)。期待0.4〜0.6件/set=約4〜6分、Wilson上限2.1〜3.2件=約21〜32分。発生0の場合は影響0 | T1 N6、BUDGET_LOG_01、DESIGN_01 §C-5 |

**70円評価(15-9)**: 量産単価影響 **+約3.5〜3.8円/セット(猿の手。根拠=区分1〜4)。現行約46.8円→予測約50.3〜50.6円/目標70円**。+1円以上のため記録済み。予測が70円以内のため『重要な影響』ユーザー判断には該当しない。品質>Delivery>単価の順で、費用削減のための品質低下案は含まない。

## 2. 原価最適化(原則3。品質を下げない範囲)

- notes のrun内immutable cache(resume/`--only-clips`/再runでLLM再call 0)、中立note(追加call 0)、state永続によるresume時の再生成防止(started-but-unfinishedを消費済みとして3回上限を保証)=実装済み設計に含む。
- 検討したが採らないもの(品質変更・別Trialが必要): (a)notes LLMのモデルを安価にする(据置=Trial同一。別Trial)、(b)ctx promptの短縮(Prompt改変=不可)、(c)1 call複数level統合(Std/Advで本文が異なる)。
- 最大の変動要因=fallbackの600秒待機(費用ではなく時間)。

## 3. Phase 2 見積(正式Production runtime evidence。API有料。別委任)

| 項目 | 内訳 | 見積(円) | 出典 |
|---|---|---|---|
| E-1 正常経路 猿の手 Std+Adv | 現行TTS stage実測 25.02(tts_b1b 11.78+tts_a2 13.24)+新仕様増分(区分1〜4)3.5〜3.8 | **約29** | P1 |
| E-2 fallback(Std 1+Adv 1 clip、強制NG) | TTS 3 call×約0.45+ASR約0.05=約1.4/run×2 | 約2.9 | T3 0.4314円/call、ASR 0.0153円/call |
| E-3 resume(Std+Adv、強制NG+kill) | 同上(TTS総call=3/run) | 約2.9 | 同上 |
| E-4 3回NG(Std+Adv) | 同上 | 約2.9 | 同上 |
| notes LLM(E-2〜E-4の小規模run 6 level) | 約0.13〜0.16円×6(cache流用はしない=自然な経路を保つ) | 約0.9 | N1 |
| **小計(期待)** | | **約39** | |
| 予備20% | | 約8 | |
| **期待計** | | **約48円** | |
| 保守(E-1で自然retry/fallbackが数件、E-3を2回やり直し) | +約12 | 約60円 | |
| 天井(暴走疑いなしの上限見積) | Std/Adv全clipが1回ずつ再生成+E-1全体やり直しを含めても | 約75円 | |

- 全て300円以下(Fable自律枠)。Guardrail 200円。日次: 当日既使用約123円+案件A実費に対し+48円で1,000円/日を大きく下回る。
- Phase 1(実装+offline test)=**API 0円**。Phase 2のE-2〜E-4の強制NGは実TTS/ASRを実行した後にNG側へ上書きするため実費が発生する(上表に含む)。
- 使用モデル(25節: 評価用途の最新モデル原則): TTS=`gemini-2.5-pro-preview-tts`(Production Zと同一=比較条件・正式経路そのもの)、ASR=Production cascade(gpt-4o-mini-transcribe+Azure Secondary)、notes LLM=`gpt-6-luna`(Trialと同一。本番ラインのモデル選定は別判断)。最新でない場合の理由=本件はTrialではなくProduction配線であり、承認済みの正式経路モデルを使うため。
- 単価の鮮度: pricing_snapshot=`er118…:574〜581`の定数(2026-10-25時点のTrial採用値)。Phase 2実費は実cost logで置換する。

## 4. 時間・並列化(原則2)

| 作業 | 見込み | 並列 |
|---|---|---|
| Opus条件Aレビュー | 〜数十分 | Phase 1の(a)新module逐語移植+golden test、(f)evidence driver実装はレビューと並行して先行準備可(Production code編集は含まない範囲) |
| Phase 1 実装+offline test | 2〜3時間 | (a)(b)(c)(f)は並列、(d)(e)は後続 |
| Phase 2 | E-1約20〜25分(Std/Advは同一起動内で連続)、E-2〜E-4はcooldown律速で約12〜15分、全て並列 → 壁時間約25〜30分 | E-1とE-2〜E-4は別run dir・別process |
- fallbackの待機(clip内ブロック)の最適化案=deferral(NG clipを保留し他clipを先に処理、600秒後に戻る)。実装は複雑化し、期待発生が0.4〜0.6件/set(約4〜6分)のため、**Phase 1では実装せずPhase 2の実fallback率を測ってからFableが判断**(質の同等性は保たれる: 各clipのattempt列は不変)。
