# TRIAL_RESULT_01 (FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_02 Phase 2、DEV/Trial専用・Production変更0)

状態: **Sonnet所見としてのStatus候補=USER_DECISION_REQUIRED(客観指標は成立、主観品質[声質の一貫性・接続の自然さ]はユーザー試聴待ち)**。最終Status判定はFable独立評価+ユーザー試聴。Production採用ではない(`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`付与なし、新flagなし)。
原文=`docs/pm/delegation_log/2026-10-25_FX-PARAGRAPH-CHUNK-TTS-TRIAL-01_USER.md`、設計=`DESIGN_01.md`(§11にOpus条件A反映・事前宣言)、Opusレビュー=`OPUS_REVIEW_01.md`。
データ=`er113_output/fx_paragraph_chunk_trial_01/measure_01.json`(全数値)・`gen_result_01.json`(chunk別Gate)・`isolation_01.json`・`ledger_preflight_01.json`。

## 0. 実施概要

- 対象: Family X『英国の電車マナー』Advanced(`b1b`)本文1・2・3(428語、10段落=4+3+3)。
- 生成: 1 launch・直列・再起動0。JST 2026-10-25 07:26:10〜07:31:06(約4分56秒)。arm=B_r1(段落10chunk)→A_r2(現行方式のpart全体3call再生成)→B_r2(Bの別take)。全23 chunk/part status=OK、**HR Lock 0・条件差異chunk 0**。
- 使用モデル: TTS=gemini-3.8-flash-lite-tts/Aoede(A同一。最新モデル原則の例外理由=A/B条件同一性)、ASR=既存Gate(OpenAI primary→Azure secondary)。評価用LLMは使用せず(ローカル計測のみ)。Styleは A記録のstyle_prefix(sha256 `3a680861e4d9…`)と全chunkで一致(`style_prefix_equals_A_style=true`)。
- B主表示take=**B_r1(生成前にDESIGN_01 §11で事前固定)**。A_r2/B_r2は参考(ページでは折りたたみ)。BとB0(追加無音なし)は同格で並置。

## 1. 段落単位Chunk化で音質は改善したか(§9-1)

- **客観指標(既存Gate)**: B_r1 10/10、B_r2 10/10(1件retry後OK)、A_r2 3/3 すべて ASR Gate OK(NORMALIZED_MATCH/EXACT_MATCH/NUMERIC_EQUIVALENCE_MATCH)、Repetition QA実施済み・指摘0、Connected Speech層は発火せず(cool-down 0秒、Local Rewrite 0、minimal_fallback 0、固有名詞hint/research 0)。chunk別一覧は `measure_01.json`の`gate`と試聴ページ。
- retry: B_r2_p2_2のみattempt 1がASR NG(「£1,000」を一次ASRが読み誤り、secondary Azureが「1000 lbs」と読み`NG_BOTH/secondary_value_diff`)→attempt 2でOK(既存retry規則どおり)。他は全て1 attempt。
- **音質が「改善したか」は客観指標では判定不能**(新しい品質基準は追加しない)。発音の正確性はGate同等、抑揚・声質の一貫性・接続の自然さは**ユーザー試聴待ち**。過去P6B不合格理由(chunk間声質差)の機械的な代理指標は設けない(参考として境界の音量差のみ§3に記載)。
- 所見(推測を含まない範囲): 段落が短い方がASR判定対象が短くなるため、不一致時の再生成単価は下がる設計だが、今回の実測ではretryはB_r2の1件のみで差を論じるには標本不足。

## 2. 発話速度は遅くなったか(§9-2)

本文3 part合計(428語)。各variantを同じRMS正規化(target_rms 0.09149)後、同一方法で測定。

| variant | 全長s | total WPM | art500 WPM | art300 WPM | 中間ポーズ≥500ms 個数/合計s |
|---|---|---|---|---|---|
| A(承認済み) | 139.92 | 183.5 | 197.7 | 211.5 | 17 / 10.04 |
| A_r2(現行方式の新規take) | 135.76 | 189.2 | 202.8 | 215.3 | 16 / 9.14 |
| **B_r1(+0.5秒、主表示)** | 149.98 | 171.2 | 190.9 | 201.7 | 20 / 15.45 |
| B0_r1(追加無音なし) | 146.48 | 175.3 | 190.2 | 201.7 | 19 / 11.46 |
| B_r2(+0.5秒) | 151.72 | 169.3 | 187.7 | 197.0 | 32個(300ms) |
| B0_r2 | 148.22 | 173.3 | 187.7 | 197.0 | — |

(A行は、承認済みwavを他variantと同じ正規化後に測り直した値。委任_01の生wav値は183.5/201.3[art500]で、正規化によりart500がわずかに変わる)

### 閾値に依存しない分解(Opus M4。後者−前者、全長=Σ発話区間差+Σ段落境界gap差+両端差、恒等式残差0.0)

| 比較 | Δ全長s | Δ発話区間s | Δ段落境界gap s | Δ両端s | 後者が長い段落数 | 段落span比 |
|---|---|---|---|---|---|---|
| A→A_r2(Aのtake間ノイズ) | −4.16 | −3.30 | −0.56 | −0.30 | 3/10 | 0.974 |
| B_r1→B_r2(Bのtake間ノイズ) | +1.74 | +2.32 | −0.70 | +0.12 | 6/10 | 1.008 |
| **A→B_r1** | **+10.06** | **+7.70** | +2.56 | −0.20 | **10/10** | **1.073** |
| A→B0_r1 | +6.56 | +6.74 | −0.20 | +0.02 | 10/10 | 1.065 |
| A_r2→B_r1 | +14.22 | +11.00 | +3.12 | +0.10 | 10/10 | 1.104 |
| A→B_r2 | +11.80 | +10.02 | +1.86 | −0.08 | 8/10 | 1.078 |
| A_r2→B_r2 | +15.96 | +13.32 | +2.42 | +0.22 | 9/10 | 1.106 |

- **結論(断定可)**: 実発話速度もBは遅い。段落単位の発話区間(10対)で、A/A_r2×B_r1/B_r2の4対すべてでBが長い(平均span比1.073〜1.106、B_r1ではAに対し10段落すべてで長い)、かつart300(B−A、−9.8〜−18.3 WPM)も4対すべて同方向。判定ルール(両指標一致時のみ断定)を満たす。take間ノイズ(Aで約±3%、Bで約±1%)より大きい差。
- 全長の増加(A→B_r1 +10.1秒)の内訳: **発話区間の遅さ +7.7秒(約77%)**、段落境界gap +2.6秒(約25%)。B0(追加無音なし)でも+6.6秒(発話区間+6.7秒、gap−0.2秒)で、**B0の境界gapはAとほぼ同じ**(gap差−0.2秒)。つまり「見かけの減速」(ポーズ)よりも「実発話そのものの遅さ」が主因。
- 速度は遅くなるが、これが望ましい減速かどうか(「品質を犠牲にしない減速」)はユーザー試聴で判断。
- 限界(Opus M4/測定法): faster-whisperのword timestampには精度限界があり(先頭語start=0.0、語境界で前語end=次語startとなる0.0 gap等のartifact)、span/gap/head間の配分に誤差が入りうる。spanとgapの和は比較的頑健。断定は上記の両指標一致時のみとした。標本はBが2 take・Aが承認takeとA_r2の2 takeのみ。

## 3. 接続・音量の不自然さは発生したか(§9-3)

- 音量: chunkごとのscalar RMS正規化(gain 0.84〜1.30)。**peak頭打ち(gain上限適用)chunk=0**(B_r1/B_r2の全20 chunkで正規化後RMS=target±0.5%、post-gain peak<0.94を再計算で確認)。B全体組立のヘッドルーム弁は既存関数をそのまま通した(`full_episode_b.headroom`)。
- 境界の音量差診断(dB、次chunk先頭1秒RMS vs 前chunk末尾1秒RMS。R3、参考値・判定なし):
  - Aの既存part境界(承認済み、独立3call間): A: +2.83 / +7.80、A_r2: +8.28 / +6.45
  - B_r1の段落全9境界: +2.20, −0.89, +3.26, +3.64, +5.81, +3.30, +3.04, +3.77, +1.83(絶対値最大5.81)
  - B_r2の段落全9境界: +3.35, +1.76, +5.59, +1.08, +3.40, +5.35, +1.66, +1.95, +3.99(絶対値最大5.59)
  - 結論: Bの段落境界の音量差は、承認済みAのpart境界(最大7.8〜8.3dB)と同程度かそれより小さい。chunk別gainにより、segment単位1gainの場合の境界差(例B_r2 part1: +8.91dB)は抑えられている。
- 段落境界のポーズ: B_r1(+0.5秒)の段落境界gapは平均約0.9秒(0.68〜1.24秒)、B0_r1は約0.46〜0.74秒、Aは約0.46〜0.84秒。B0がAに最も近い(ポーズの好みと見かけの減速をユーザーが切り分けられるよう並置)。
- 欠落・重複語: 結合後partへのASR整列でmatch_ratio 0.96〜1.00、全段落整列(`all_paragraphs_aligned=true`)。境界での語欠け・二重の機械検知は無し(whisper整列の精度範囲内)。
- 声質・話し方の一貫性(過去P6B不合格理由): **機械指標は設けず、ユーザー試聴で判断**(ページの観点リスト)。F0/spectral centroidの参考値は任意項目のため未実施。

## 4. Family Aのどの既存方式を再利用したか(§9-4)

- 音量: 各独立TTS出力ごとの同一target_rmsへのscalar gain(`compute_gain_for_target_rms`、peak≤0.95、CURRENT_SPEC:2099)。適用単位=段落chunk。target_rmsはA側`gain_report.json`の値(0.09149、他segmentのgain不変)。
- 接続: 承認済みFamily C/Z story clip接続の段落間0.5秒(narrator→narrator、`er013_family_c_production_runner_01.py:670`)+`np.concatenate`(crossfade・EQ・コンプなし)。Bは+0.5秒、B0は追加無音なし(trim margin残置のみ)。
- 自動trim: 生成関数内の既存`trim_english_keyword_silence`(margin 0.35秒上限、実残置0.24〜0.35秒)。
- 全体組立: 既存`build_family_x_b1_timeline`→`assemble_with_timeline`→`apply_headroom_safety_valve`(本文3 segmentのみB版へ差替え)。
- 新しい独自の音声加工は導入していない。

## 5. 費用・処理時間はどれだけ変化したか(§9-5)

| 項目 | A_r2(現行方式 part3call) | B_r1(段落10call) | B_r2(段落10call+retry1) |
|---|---|---|---|
| TTS call数 | 3 | 10 | 11 |
| ASR call(OpenAI/Azure) | 3 / 0 | 10 / 0 | 11 / 1 |
| 費用(raw_usage_log) | 3.98円 | 4.27円 | 5.64円(retry+Azure 0.80円含む) |
| 生成+検査所要(cool-down 0秒) | 96.1秒 | 102.1秒 | 106.2秒 |

- 3 arm合計実費 **13.89円**(Gemini 10.91円/OpenAI ASR 2.18円/Azure 0.80円)。見積12.6円に対し+10%(B_r2のretry+Azure分)、上限50円の28%。日次1,000円に対する当日加算=13.89円。
- **Production採用した場合の量産単価への影響(Advanced本文のみ)**: B_r1−A_r2=約+0.30円/take(+7.5%)、所要時間+約6秒。retryが入るとさらに増える(B_r2では+1.66円)が標本1件。70円/記事セット目標に対して約0.4〜1%相当(Advancedのみの試算。Standardへ適用する場合は別途。n小のため参考値)。
- 条件差異: 短chunk(p1_2、82文字)では`max_extra_chars=15`の長さ許容が相対的に緩い(約18%、part全体では約4%)。既存規則をそのまま適用した結果として記録(規則は変更していない)。

## 6. A/B試聴URL(§9-6)

https://shimomura055.github.io/eigo-radio/user_test/fx_paragraph_chunk_trial_01/index.html (公開後にHTTP 200確認。結果は`RESULT_PACKET_FXPC2.md`)。A(承認済み)/B(=B_r1、+0.5秒)/B0(=B_r1、追加無音なし)の本文1・2・3個別+本文全体+Advanced通し(A/B)、折りたたみでA_r2/B_r2、比較表付き。

## 7. Trial Closeout Status候補(§9-7、Sonnet所見)

**USER_DECISION_REQUIRED**(最終はFable独立評価+ユーザー試聴)。根拠:
- 客観面: 全Gate PASS・HR Lock 0・条件差異0・音量/境界の異常なし・ProductionStore不変。A比で**実発話が約7%遅くなる**(断定可)とともに、段落境界gapが増える(B)/Aと同程度(B0)。コスト増は小(+約0.3円/Advanced本文)。
- 判断不能面: 「音質が改善したか」「声質の一貫性・接続の自然さ(過去P6B不合格理由)」は機械指標で代替せずユーザー試聴で決める。VALIDATED/REJECTEDをSonnetが機械的に決めない。
- 撤退条件: chunk間声質差が確認された場合はREJECTED(DESIGN_01 §9)。Production採用へ自動移行しない。
