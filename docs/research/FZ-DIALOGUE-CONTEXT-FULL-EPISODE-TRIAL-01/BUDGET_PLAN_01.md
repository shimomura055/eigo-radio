# BUDGET_PLAN_01 — 費用・時間見積と量産想定原価の算式(FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_01、API 0)

出典: `er118_output/fz_full_episode_trial_01/budget_plan.json`(`py er118_fz_full_episode_trial_01.py budget` で再生成。見積式は Round 2 と同一の `er118_fz_dialogue_context_tts_trial_01.est_tts_jpy`、単価実測は `BUDGET_LOG_02.md`)。
対象53セリフ(棚卸 `INVENTORY_01.md`)。ユーザー原文§6「必要費用が承認済み枠を超えるなら超過実行せず報告」に対し、**Fable自律枠(案件300円以下、PM_GOVERNANCE 7-7)に十分収まる**。

## 1. Trial実支出の見積(セリフのみ新規生成、1 take、地の文は再利用)

| 作品/レベル | セリフ数 | TTS ctx(1 call/clip, 円) | TTS 現行styleの同clip(円) | Style追加分の増分(円) | Production実績 call/clip |
|---|---|---|---|---|---|
| 猿の手 Std | 15 | 6.655 | 5.468 | 1.188 | 1.000 |
| 猿の手 Adv | 17 | 6.567 | 5.291 | 1.277 | 1.059 |
| メロス Std | 10 | 4.469 | 3.683 | 0.786 | 1.000 |
| メロス Adv | 11 | 4.522 | 3.682 | 0.841 | 1.000 |
| **計** | **53** | **22.213** | 18.124 | **4.089** | 1.019 |

- 見積式: 入力 = prompt文字数/4.5 token、出力 = 原音秒×25 token/秒×1.05。ctx prompt文字数 = CONTEXTブロック(決定論部)+350字(LLM由来行の見込み、Round 2と同一)。
- Round 2 実測単価(`BUDGET_LOG_02.md`): Gemini TTS 26.20円/50 call = 0.524円/call、ASR(OpenAI+Azure)1.60円/50 clip = 0.032円/call、感情LLM 約0.097円/call。Round 2 は1clip平均が長い(作品選定のため)ため、本Trialの見積は式で再計算(1 call 平均 0.42円)。
- **感情情報LLM(Phase 1a、本委任)**: 4 call(作品×レベル各1)× 約0.1円 = 約0.4円(上限5円Guardrail)。

| シナリオ(委任_02全体) | call/clip | TTS | ASR | LLM | 合計(円) |
|---|---|---|---|---|---|
| 期待値(Round 2実測 50/48) | 1.042 | 23.14 | 1.77 | 0.39 | **25.3** |
| 保守(Productionより高い再生成を想定) | 1.25 | 27.77 | 2.12 | 0.39 | **30.3** |
| 天井(全clipがretry上限=通算3回) | 3.0 | 66.64 | 5.09 | 0.39 | **72.1** |

- Adv(28 clip)は Production と同じ「速度後ASR再検証つき外側ループ」で生成するため、速度後ASRが各clip +1回(約0.03円×28×call/clip = 約1円)加わる。上表の保守値に含めて**約31円、天井で約75円**。
- **全シナリオが 300円(Fable自律枠)以下、日次1,000円にも収まる(当日JST既使用約79円 + 最大約75円 = 約154円)**。削減案(レベルを1つに絞る等)は**不要**(削減すると§3「Std/Advの区別」とユーザー原文§2③に反する)。
- 上限(委任_02の個別Guardrail案): 100円(天井75円+余裕)。到達・接近時はT-3定型文に従う。暴走疑い(同一clipの無意味な反復等)のみSTOP。

## 2. 時間の見込み(委任_02)

| 工程 | 見込み | 並列化 |
|---|---|---|
| Opus条件A反映・実装・test | 40〜60分 | Fable→Opus待ち中に実装を先行できない(新フロー設計のため)。ただし評価script・ページbuilderは並行実装可 |
| 生成(53 clip、Round 2実測 約12秒/clip→約11分、Adv速度後ASRで+) | 約15〜20分 | 作品×レベル4単位は独立。ただしRate limit/再現性のため2並列まで(Round 2の「別作品は27秒間隔で順次」を踏まえ、同時起動は避け間隔≥150秒) |
| 組立・解析・ページ | 20分(API 0) | 4単位並列可 |
| 評価・Fable独立評価 | 20分 | - |

## 3. 実Trial支出と通常量産時の想定原価の区別(ユーザー原文§5)

| 区分 | 実Trial支出(本Trialで発生) | 通常量産の想定原価(Trial実測から算出) |
|---|---|---|
| 地の文・Intro/Preview/KP/Comment | 0(既存音声を再利用) | 0増分(方式は変更しない) |
| セリフTTS(1 take) | 53 clip×実測 call/clip | **n_clip×(k_ctx×c_ctx − k_prod×c_base)**、k=実測 call/clip |
| 追加Style分 | 入力token増(上表) | **Σ n_clip×(c_ctx−c_base)** |
| 感情LLM | 4 call | 1記事セット(Std+Adv)=**2 call×0.097円** |
| 再生成 | 実測再生成回数 | k_ctx−k_prod の実測差×(c_ctx+ASR) |
| 人手/AIレビュー(感情情報accept/discard) | Fable確認(API 0) | **量産では自動化が必要**(要新規設計。Trialでは時間のみ計測) |

量産想定増分の算式(1記事セット = Std+Adv、**委任_02で実測k・時間を代入**):

```
Δコスト/set = Σ_level n_dialogue × [ (k_ctx − k_prod) × (c_base + c_asr) + k_ctx × (c_ctx − c_base) ] + 2 × c_llm
  k_ctx  : 本Trialの実測 TTS call / clip(再生成を含む。作品×レベル別と全体)
  k_prod : Production実績 call/clip(猿の手/メロス= 54 call/53 clip = 1.019、INVENTORY_01)
  c_base : 現行styleの1 call TTS費用(上表)    c_ctx : ctxの1 call TTS費用    c_asr = 0.032円
  c_llm  : 0.097円(Round 2実測)
評価: 70円/set に対する比 = Δコスト/set ÷ 70(超過するなら 70+Δ の円)
```

- 先取りの参考値(再生成差ゼロの下限): 猿の手 set = Σ n×(c_ctx−c_base) ≈ 1.19+1.28 = **2.5円** + LLM 0.19 = **約2.7円/set**。メロス set ≈ 0.79+0.84+0.19 = **約1.8円/set**。k_ctx=1.25(k_prodより+0.23)の場合は 猿の手 +3.5円・メロス +2.4円を加え、**約6円/set・約4円/set**。いずれも「追加Style費用0.1〜0.2円」ではなく、再生成増加と作品のセリフ量(32 vs 21)で変わる点を委任_02で実測する。
- 本表の通常量産原価は「Z set全体の現行原価」を前提にしない(70円/setの内訳はTrial対象外)。**Δのみを算出し、70円に対する比で評価する**(Production全体原価の再計算はユーザー原文の範囲外)。
- Production reuse(Master Store/reuse key)との関係: Production dialogueのreuse keyは style hashを含まない(`production_reuse_key_for`、Round 1 EVAL_01 §2)。本Trialは Trial専用key(managed_id・arm・take・style sha)で隔離し、Productionのreuseを一切使わない/汚さない。量産化する場合のreuse key拡張は別承認事項。
- **時間への影響の測定**: (a)clip単位 elapsed_s(result.json) (b)作品×レベルの生成壁時計 (c)再生成による追加時間 (d)LLM 1 call の所要(Phase 1a実測)。量産では LLM 2 call は直列でも各十数秒、TTSは+0〜数%と見込むが**実測で置換**。
