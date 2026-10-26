# PREREGISTERED_CRITERIA_01 — 事前登録(全編通しTrial。TTS生成・ASR・指標の観測前に固定)

管理ID: FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 / 固定日: 2026-10-26(委任_01、TTSもLLM結果の評価も未観測)。
Round 1/2 の `PREREGISTERED_CRITERIA_02.md`(指標・leakage定義・Status写像の考え方)を継承する。**承認済み品質基準・Gateは変更しない**(ユーザー原文§4)。本書は評価の追加定義であり、Production基準の変更ではない。
Opus条件Aレビューで指摘が入った場合は、本書を**生成前に**改訂して再固定する(生成後に変更しない)。

## 1. 比較設計

- 比較は **Trial通し版 vs 公開済みProduction通し版**(作品×レベル4組)。Production側は既存の1 take(Round 2の `base` arm のような追加takeは作らない=費用と時間の最小化。ユーザー原文§6)。
- したがって「take間の自然ゆれ」は本Trial内では直接測れない。**自然ゆれの目安は Round 2 の実測**(Production原音 ① と base_t1 の差、`er118_output/fz_dialogue_context_tts_trial_01/analysis.json` と `…_02/<work>/analysis.json`)を、委任_02の**生成前に**一度だけ集計して固定値(各指標の |log比| の中央値と90%点)として `er118_output/fz_full_episode_trial_01/noise_band_r2.json` に保存し、以後更新しない。
- 個別セリフの機械指標の方向(↑↓)を作品全体で事前宣言する根拠は弱い(Round 2で正方向完全分離 4/15・逆向き 2/15)ため、**本Trialの機械指標は「個別clipの効果判定」ではなく「分布・外れ値・安定性の観測」に使う**。効果の有無はユーザー試聴が決める。

## 2. 基本品質(C): Status判定に使う条件(blocking)

ユーザー原文§4Cに対応。全て**Trial版の全セリフ**(猿の手Std15+Adv17、メロスStd10+Adv11 = 53 clip)について。

| ID | 条件 | 測り方(既存関数) |
|---|---|---|
| C1 | 全53 clipの最終statusがOK(Production ASRカスケードPASS)。Advは**速度後ASR再検証を含むProduction外側ループ**で確定 | `generate_with_a2_slowdown_outer_loop` / `generate_voice_body_wide_margin` の結果(`tts_generation_results`相当) |
| C2 | ASR逐語一致: 最終採用attemptの転写がセリフ本文と正規化後一致(読み飛ばし・言い直し・不自然な反復なし) | `t.verbatim_check(asr_text, canonical_text)` + Production repetition QA(`repetition_qa_checked`) |
| C3 | 文脈情報の音声混入なし: `leakage_final.flagged == 0`。途中attemptを含む `leakage_any_attempt` は別に全件報告(隠さない) | `t.leakage_check` / `leakage_all_attempts`(Round 2のOpus M1定義) |
| C4 | `comparison_valid`: 最終採用attemptが minimal_fallback でなく、実送信promptのshaが期待値と一致、`request_full.json`保存 | `t.comparison_validity`(Round 2と同じ) |
| C5 | 音声結合・ポーズ・音量: (i)組立ハーネスの自己検証(Production原clipで再組立→Production組立wavと timeline part列・duration・サンプル差が一致、DESIGN_01 §3)に合格 (ii)Trial組立のheadroom safety valveの作動回数がProduction組立以下 (iii)通しwavにクリップ(peak>0.99)なし | `run_assembly` 戻り値 `timeline.headroom` / 自己検証report |
| C6 | 既存の必須音声品質Gate: `a63.run_audio_gate` をtrial_run_dirに適用(API 0であることを実装時に確認)し、Productionと同じ判定(shared_gate PASS、audio_text_deviation増加なし) | `er063.run_audio_gate`(実装時に実行可否を確認。不可なら理由を記録しC6を「未実施」と明記=PASS扱いにしない) |
| C7 | 隔離: Production保護store・Production run音声/結果/timeline・公開mp3/htmlのsha256が生成前後で不変、`safe_write`違反0 | `snapshot_protected`拡張(DESIGN_01 §3) |
| C8 | 費用の記録: raw_usage_log.jsonlからの実費集計がある。Guardrail(100円)超過時は暴走疑い(無意味な反復・原因不明の増加)でないことを記録 | `compute_cost_jpy_so_far` |

**Status写像**(Round 2 PREREGISTERED_CRITERIA_02 §3 と同形):

| 機械状態 | Status |
|---|---|
| C1〜C7 のいずれかが不成立(C6は「未実施」も不成立扱い) | **REJECTED候補**(下位ラベル `TRIAL_FAILED_QUALITY`)。不成立の内容を示し、Fableが再生成/方式転換を判断(自動反復しない) |
| C1〜C7 すべて成立(C8は記録) | **USER_DECISION_REQUIRED(試聴判断待ち)**。**機械指標だけで VALIDATED とは言わない** |
| ユーザーが通しで聴いて「改善」 | VALIDATED(限定)。Production採用ではない(採用は別承認) |
| ユーザーが「改善が不安定」「効果なし/悪化」 | REJECTED(下位ラベル `TRIAL_COMPLETE_NO_EFFECT` / 現行維持か別方式転換をFableが進言) |

## 3. 観測指標(補助。Statusを自動決定しない)

### 3-1 Round 2 から流用(clip単位、加工前の原音で測る)
`t.analyze_wav` の `articulation_wpm_300`(調音話速)、`f0.median_hz`、`f0.range_semitones_p10_p90`(F0幅)、`rms_dbfs`(揃える前RMS)、`duration_s`、`max_mid_pause_s`。Production対応clipとのペア比較(log比)。

### 3-2 本Trial新規(観測前に定義)

| ID | 指標 | 定義 | フラグ |
|---|---|---|---|
| N1 | **話者内ばらつき** | 同一話者(同一作品×レベル、clip数≥3の話者のみ)の ctx clip 間で、(a)調音話速の変動係数CV (b)F0中央値の標準偏差(半音) を算出。Production同話者clip間の同指標と比較 | `unstable_speaker` = ctx側が Production側の **2倍超** かつ 絶対増分が (a)CV +0.05超 または (b)+1.0半音超 のとき。**needs_listen(聴感確認)であり REJECT条件ではない**(感情で変動するのは想定内) |
| N2 | **不自然な速度変化・長ポーズ** | (a)clip内 ≥300ms無音のうち最長が **700msを超える** clip数(Round 2の `pause_300` 検出を利用)(b)調音話速がProduction対応clipの **0.6〜1.6倍の外** (c)duration が Production対応clipの `length_listen_flag`(1.4倍超かつ+0.6秒超、Round 2定義) | (a)が Production側に無くTrial側にある clip、(b)(c) を `needs_listen` として全件列挙 |
| N3 | **地の文→セリフの境界RMS段差** | 通し組立wavのtimelineで、セリフclip先頭300msのRMS(dBFS)と直前の地の文clip末尾300msのRMSの差の絶対値、セリフclip末尾300msと直後の地の文clip先頭300msの差(無音は除いたclip内の窓)。Trial版とProduction版で同じ境界を比較 | 段差が Production比 **+3 dB超** の境界数と全境界数を報告。`needs_listen` |
| N4 | **感情の強弱での効果差** | Fable accept済みの感情情報あり(ACCEPTED相当)clip群 vs 感情なし(NO_EXPLICIT_CUE/DISCARD)clip群で、3-1の各指標の |log比| の中央値を比較。自然ゆれの目安は §1 のR2固定値。事前予測: 感情ありのほうが |log比| が大きい(ただし予測が外れても結果として報告) | 参考のみ |
| N5 | **初回成功率・再生成** | clipごとの TTS call数(`tts_generations_used`)、初回(1 call)でOKになった割合、再生成clip一覧、NG→OKの理由、Production実績(54 call/53 clip=1.019)との差 | 量産想定コストの入力(BUDGET_PLAN_01 §3) |
| N6 | **時間** | clip別・作品×レベル別の生成壁時計、LLM 1 callの所要、再生成による追加時間 | 同上 |

## 4. 人手評価項目(機械で代替しない。ユーザー原文§4A・§4B)

試聴ページ(DESIGN_01 §4)に、次を評価観点として明記する。Fable独立評価は同じ観点で行うが、聴感の最終判断はユーザー。

A. 表現品質: ①セリフの感情が場面に合っているか ②感情表現が過剰でないか ③前後のセリフと演技がつながっているか ④地の文からセリフへの切り替わりが自然か ⑤通しで聴いたとき現行版より没入感が増すか。
B. 安定性: ⑥同一人物の演技に大きなばらつきがないか ⑦感情の強いセリフと弱いセリフで効果がどう異なるか ⑧文脈指示で不自然な速度変化・長いポーズがないか(N1〜N3は⑥⑧の機械的な補助)。

## 5. 費用・時間の測定項目(ユーザー原文§5。実Trial支出と量産想定原価は別表)

(1)感情・文脈情報の生成費用(LLM実費) (2)追加Style指示によるTTS費用増分(同clipの現行style見積との差 + 実測input token差) (3)セリフの初回生成成功率 (4)品質NG件数・再生成回数 (5)再生成を含むセリフTTS総費用 (6)従来方式に対する1記事セット当たりの推定増加額(`BUDGET_PLAN_01.md` §3の式) (7)完成までの所要時間への影響。70円/記事セットに対する増分の比と、超過する場合の概算円を結論に書く。

## 6. 事前に認識しているリスク

- 短文(1〜4語)は話速・F0が不安定(Round 2 EVAL_02 §5)。猿の手Advに1語/2語が4件、Stdに2語が2件。N2を満たさない可能性が高く、**needs_listenに載せるだけでSTATUS条件にしない**。
- メロスのProduction clipは前run再利用(`reused_from_previous_run`)で、ASR判定が `asr_judgement_inherited`。Production側の「確定音声」の質は同じだが、ペア比較は新規生成clipとの比較であることを報告に明記。
- 「通しで聴くと没入感が増すか」は機械指標にならない。Trial版の秒数がProductionとずれる点(DESIGN_01 §3の差)は評価に影響しうるので、ページに併記する。
- Round 2では速度後ASR再検証をしていなかったため、Advの再生成回数・初回成功率はRound 2より悪く出る可能性がある(Production同等の厳格化による。方式の悪化ではない)。
