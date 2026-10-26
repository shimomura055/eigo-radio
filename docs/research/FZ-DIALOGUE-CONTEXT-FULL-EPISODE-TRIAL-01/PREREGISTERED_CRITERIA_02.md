# PREREGISTERED_CRITERIA_02 — 事前登録の改訂(Opus条件A M-5/M-7/M-8/R-7 反映。セリフTTS生成・ASR・指標の観測前に固定)

管理ID: FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 / 固定日: 2026-10-26(委任_02、**生成前**。固定の証明=このファイルを含む生成前commitの時刻)。
`PREREGISTERED_CRITERIA_01.md` を継承し、以下の項目だけを**置換/追加**する(記載のない項目は01のまま)。承認済み品質基準・Gateは変更しない(ユーザー原文§4)。本書固定後は、観測結果を見て変更しない。

## 1. 置換する条件(blocking。対象=セリフ53 clip)

| ID | 02での定義(01から置換) | 根拠 |
|---|---|---|
| C1 | 各clipの最終statusがOK(Production ASRカスケードPASS系。Advは速度後ASR再検証つき外側ループで確定)。**NG件数の扱いは §3 の閾値** | Opus M-8 |
| C2 | **Production ASRカスケードの最終判定がPASS系(= 生成関数の最終status==OK)、かつ repetition QA 実施済み(`repetition_qa_checked==true`)**。`token_equal`/`token_similarity`(`t.verbatim_check`)は**観測値として全clip報告**し、blockingには使わない | Opus M-7(Productionが合格とする ORTHOGRAPHIC_EQUIVALENT_MATCH / CMU同音 / Secondary救済 / PASS_WITH_WARNING を不合格にすると、ユーザー承認なしの品質基準引上げ=Charter原則1違反) |
| C3 | `leakage_final.flagged == 0`(Trial固有リスクなのでblocking維持)。`leakage_any_attempt`は別に全件報告。**flagged時の手順(§2)** | Opus M-7 |
| C4 | `comparison_valid`(最終attemptがminimal_fallbackでなく、実送信promptのshaが期待値と一致、`request_full.json`保存)— 01のまま | — |
| C5 | (i) 組立ハーネス自己検証(Production原clipで再組立し、Production組立wavとtimeline・gain_report・headroom・サンプル完全一致)に**生成前に**合格 — **4単位とも合格済み**(`<unit>/selfcheck.json`、wav_max_abs_diff=0.0) (ii) **01の「headroom作動回数≦Production」を置換**: Trial組立後に、`gain_report.target_rms`がProductionと一致 / dialogue以外の全labelのgain値(gain・rms_after・peak_after)がProductionと一致 / `headroom.scalar`がProductionと一致 の**3点すべて**(どれか1つでも違えばSTOP)、かつ `story_clips[0]` が非dialogue (iii) 通しwavのpeak ≤ 0.99 | Opus M-5 |
| C6 | `a63.run_audio_gate` を **trial_run_dir** に適用(API 0)してshared_gate==PASS。**未実施・例外は不成立**(PASS扱いにしない)。入力は M-1〜M-4 の方式で構築(Trial dialogue entryは `build_entry` で作成、pathは全てOUT_ROOT配下、Production `_original.wav`は除去) | Opus M-2/M-3, R-7(d) |
| C7 | 隔離: (a) Production run dir(2作品)・公開page dir(2作品)を**全ファイルtree-hash**で生成前後に比較して差分0 (b) 共有store(PROTECTED_STORES/TREES)の差分は、差分ファイル内に本Trial出力先(`er118_output/fz_full_episode_trial_01`)が含まれれば**本Trial由来=汚染=不成立**、含まれなければ他agent由来の外部変更として記録のみ (c) repo mtime走査でZ Production dir/Z公開ページ配下のヒット0 (d) `safe_write`/`assert_out_root`違反0、hardlink/symlink0 | Opus M-1/M-4, R-1 |
| C8 | 費用記録(01のまま)。実費は `raw_usage_log.jsonl` のprovider別実績を正とする(R-6(a)) | Opus R-6 |

## 2. C3 flagged時の手順(M-7、生成前固定)

1. `leakage_final.flagged==true` のclipは**採用保留**(`hold_pending_fable_listen`)。組立入力にはProduction原音を置き、ページ・チャプターに「現行音声(Trial生成は保留中)」と明示する。
2. 生成後、flagged clip を**RESULT_PACKETに列挙**する(clip_id・ASR転写・余分token・CONTEXTだけにある語)。
3. Fableが当該clipを聴いて次を記録する: `cleared`(ASRの幻聴で文脈語は発話されていない) / `confirmed_leak`(文脈語が発話されている)。記録先 `er118_output/fz_full_episode_trial_01/<work>/<level>/fable_clearance.json`(`{clip_id: cleared|confirmed_leak}`)。
4. `cleared` は再組立(API 0)で採用に切替える。`confirmed_leak` は NG に加算する。Fable未記録の間は『保留』のまま、Status候補は `PHASE1B_DONE_HOLD_PENDING_FABLE_LISTEN` とする。

## 3. NG clipの扱い(M-8、Fable決定、生成前固定)

- **NG音声は絶対に採用しない**(clipごとの別ディレクトリで生成し、OK + C2〜C4成立 + 保留なしのclipだけを trial_run_dir へcopy。組立前にdialogue wavのshaと採用済み結果のshaの一致をassert)。
- 通し版の該当箇所には**Production原音**を置き、ページとチャプターに「この箇所は現行音声(Trial生成NG)」と明示する(欠番の無音は没入感評価を壊すので採らない)。
- NG件数は「NG率」「再生成率」として報告する(N5)。
- **NG数の定義** `n_ng` = status!=OK または `repetition_qa_checked`でない または `comparison_valid==false` のclip数(+Fableが`confirmed_leak`と記録したclip数)。保留(§2)は `n_hold` として別掲。
- **Status写像**(01 §2 の写像を置換):

| 機械状態 | Status候補 |
|---|---|
| C5/C6/C7のいずれか不成立(C6の未実施を含む)、または `n_ng >= 3`(53 clip中、約5.7%以上) | **REJECTED候補**(下位ラベル `TRIAL_FAILED_QUALITY`/方式不安定)。Fableへ報告(ページは作る)。自動反復しない |
| C5/C6/C7成立 かつ `n_ng <= 2` かつ `n_hold == 0` | **PHASE1B_DONE_USER_LISTENING_PENDING**(`n_ng>0`なら『記録付き成立』)。機械指標だけでVALIDATEDとは言わない |
| C5/C6/C7成立 かつ `n_ng <= 2` かつ `n_hold >= 1`(Fable未記録) | `PHASE1B_DONE_HOLD_PENDING_FABLE_LISTEN`(保留のまま報告) |
| ユーザー通し試聴後 | 01 §2 と同じ(改善→VALIDATED(限定) / 不安定・効果なし→REJECTED) |

## 4. 観測指標の運用改訂(R-7)

- **自然ゆれ固定値**: `er118_output/fz_full_episode_trial_01/noise_band_r2.json`(Round 1/2の同style別take対Production原音 24ペアの |ln比| の中央値・90%点)を**生成前に作成**。sha256 = `f720991856bd547c6a9387b12835360fbba2f220bee15cadea1fc1ef8c9adbd3`。以後更新しない。result/analysisにこのshaを記録する。
- **N1(話者内ばらつき)**: 「フラグ率」を見出しにしない。話者ごとの値(Trial側・Production側のCV・F0中央値SD)を**両側とも全件併記**する。`unstable_speaker`判定(01の定義)は列として残すが `needs_listen` の補助に留める(話者あたり3〜5 clipのCV比は偶然で2倍を超えやすい)。
- **N2(a)(b)(c)・N3**: Trial/Productionの**両側を同じ段階の音声**で測る。clip指標は加工前の原音(Std=生成wav / Adv=生成の`_original.wav`。Productionも同じ段階)、N3は組立後wav(Trial組立wav vs 自己検証で一致を確認した再組立Production wav)。
- **N4/N5/N6**: 01のまま。N5のkは `raw_usage_log.jsonl` のprovider別実績を正とする(R-6(a)(b))。ASR費用はclip当たりの実測で割る(定数0.032円を使わない)。
- **費用(R-6)**: Δ/setは幅で示す(k_prod=1.019版 / Round 2 base arm実測k版)。感情情報レビューの自動化費用は『未計上(要設計)』とし0円扱いにしない。

## 5. 追加で固定する運用条件

- **Std会話へのctx付与は今回が初めて**(Round 1/2はAdvのみ)。試行リスクとして明記する(R-9)。Advの再生成回数・初回成功率はRound 2より悪く出る可能性がある(Production同等の速度後ASR再検証を含むため。方式の悪化ではない。Round 2との再生成率比較は条件が違う)。
- **起動条件**: 生成中は他のProduction runを起動しない。並行するY委任_03の書込みによる共有storeの差分は C7(b)の帰属判定で『他agent由来』と区別する。Z Production dir/公開pageに差分が出れば即STOP。
- **Guardrail**: scope=Phase 1b・100円(PHASE1_GO.json、`scope="Phase 1b"`、`cap_jpy=100`)。到達時は暴走疑いの有無を確認し報告(T-3)。
- 外部停止・原因不明のrc≠0が2回続いたら再起動せずSTOP。起動間隔≥150秒、各unit 1起動、同一コマンドの5分3回禁止。

## 6. 改訂履歴(観測後改訂1件: M-5(3)。委任_03、Fable案A採用)

- **改訂時刻**: 2026-10-26 09:54:05 JST(commit時刻は `git log` を正とする。メロス生成前に固定)。
- **改訂内容(M-5(3))**: 「`headroom.scalar`がProductionと一致」を次に置換する。「`headroom.scalar`の差が生じても、(i)原因がTrial dialogue clipのサンプル間ピークのみ(非dialogue clipのgain/peakは不変、Production側は安全弁非作動)、(ii)Production安全弁(閾値0.98・全編一律scalar)の設計どおりの作動、(iii)差が0.1 dB以内、の3点を満たす場合は『記録付き成立』とし、実測scalar・dB差・原因clipを交絡として全報告に明記する」。M-5(1)(target_rms一致)・(2)(非dialogue gain一致)・story_clips[0]非dialogue は不変。
- **理由**: M-5はProduction規則・品質基準ではなくTrialの比較条件ガード(Fable設定)。安全弁は全編一律scalarで相対音量を変えない。Opus前提「会話peak≦0.95<0.98」が猿の手Advで崩れた(Trial clip part2_c10の24k→48k変換後サンプル間ピーク0.9834>0.98)。take入替(結果を見て試行を選ぶ)は不可、評価不能扱いは過剰。
- **観測済み範囲(改訂時点)**: 猿の手Std/Adv セリフ32 clipの生成と生成時採用判定(32/32初回OK)、猿の手Stdの組立と機械指標`analysis.json`(STOP直後に自動生成済み。M-5(3)改訂は音量scalarのみに依存し、指標値に依存しない)、猿の手Advの組立でM-5(3)不一致を観測(Trial scalar 0.99656 / Prod 1.0 = -0.030 dB)。**未観測**: メロス生成・メロス組立・猿の手Advの機械指標・ユーザー試聴。
- **開示義務**: EVAL/TRIAL_RESULT/ユーザー報告で『観測後改訂1件(M-5(3))』として必ず開示する。
