# TRIAL_REPORT_02 STANDARD-KP-JA-TTS-STYLE-TRIAL-02 委任_01(Offline Trial。Production採用なし)

## 0. サマリ
- 7 Style x 5 Phrase = 35音声。J3(Coffee完成版既存wav)・P5(Trial-01既存wav)は再利用、P6〜P10を新規25 call生成(全OK、retry 0、失敗 0)。
- 実費 約JPY1.05(TTS 0.946 + ASR 0.105。`cost_actual.json`)。上限JPY10・見積1.46内。
- 試聴ページ: https://shimomura055.github.io/eigo-radio/user_test/coffee_std_kp_ja_style_trial_02/index.html (「すぐに」先頭、7列)。
- 注意すべき事実: P6・P7の「生豆」(kp2)がASRで TRUE_CONTENT_MISMATCH(P6=「生米」、P7=「斜め」)。P5・P8・P9・P10・J3は一致。1 Takeのため発音揺らぎかStyle影響かは分離不可。聴感で要確認。
- Status分類案: USER_DECISION_REQUIRED(ユーザー試聴待ち)。VALIDATED/採用の判定はしない。

## 1. 再利用音声の出典・条件一致
- J3: Coffee完成版run `er019_output/.../coffee_prices__run_m2p0_n01_01/a2/audit/tts_generation_results.json`のwav。style_prefix shaがユーザー提示J3文と一致(`ae68e3e6…`)。wav記録shaと実shaが5件一致(`J3_reuse/source_sha.json`)。mp3はTrial-01 mp3のcopy(10件中5件、cmp一致)。
- P5: `er057_output/std_kp_ja_style_trial_01/P5/`のwav。P5 Prompt shaはスクリプト内・Trial-01 results.jsonl・委任文(ユーザー提示)で3者一致 `b4af59b5…`(`evidence/dry_run.json`、`evidence/prompts_sha.json`)。mp3はTrial-01 mp3のcopy(cmp一致、`P5_reuse/source_sha.json`)。
- 生成条件: Aoede / gemini-3.8-flash-lite-tts / speech_metadata_flash_lite / 同一trim margin 0.35s / 同一ASR経路。前回scriptのコピーで、Style定義以外の差なし。比較上の差: J3は完成版生成時(別日・Production経路)の音声、P5は別session生成。いずれも1 Takeで生成ゆらぎを含む。
- P6〜P10のPromptはユーザー提示文と逐語一致(`evidence/prompts_sha.json`の全Style verbatim_match=true)。

## 2. 7x5 比較(参考値。F0 std[半音] / 長さ[秒] / ASR)
| Phrase | J3 | P5 | P6 | P7 | P8 | P9 | P10 |
|---|---|---|---|---|---|---|---|
| 1 大喜びする | 4.16/1.72 | 2.13/1.71 ○ | 3.72/1.63 ○ | 3.12/1.59 ○ | 4.21/1.73 ○ | 2.69/1.76 ○ | 3.24/1.67 ○ |
| 2 生豆 | 2.14/1.40 | 0.82/1.27 ○ | 2.59/1.29 x「生米」 | 0.94/1.09 x「斜め」 | 2.66/1.20 ○ | 1.98/1.37 ○ | 1.60/1.46 ○ |
| 3 すぐに | 3.22/1.21 | 2.48/1.00 ○ | 2.94/1.12 ○ | 2.48/1.05 ○ | 2.28/1.12 ○ | 1.43/1.12 ○ | 4.50/1.17 ○ |
| 4 インタビューをもとにした | 2.07/1.95 | 3.64/2.07 ○ | 2.26/2.04 ○ | 3.08/1.92 ○ | 4.06/2.12 ○ | 2.98/1.93 ○ | 3.39/2.13 ○ |
| 5 時間がかかる | 3.53/1.71 | 2.90/1.64 ○(句点) | 0.72/1.52 ○(句点) | 2.53/1.59 ○(句点) | 3.54/1.60 ○ | 0.84/1.40 ○(句点) | 2.96/1.63 ○ |
(○=ASR EXACT/NORMALIZED一致、x=TRUE_CONTENT_MISMATCH。J3のASRは完成版記録。表はF0 std/長さ。出典`objective_metrics.json`、`asr_results.jsonl`)

Style平均(5 Phrase): 
| Style | 長さ | F0 std | F0 range(p10-p90) | RMS dyn dB | 無音比 |
|---|---|---|---|---|---|
| J3 | 1.598 | 3.02 | 6.88 | 18.8 | 0.338 |
| P5 | 1.538 | 2.39 | 5.37 | 15.1 | 0.410 |
| P6 | 1.520 | 2.45 | 6.26 | 16.5 | 0.372 |
| P7 | 1.448 | 2.43 | 5.55 | 15.6 | 0.411 |
| P8 | 1.554 | 3.35 | 7.66 | 15.1 | 0.376 |
| P9 | 1.516 | 1.98 | 4.60 | 14.3 | 0.391 |
| P10 | 1.612 | 3.14 | 8.13 | 16.4 | 0.380 |
注: F0大＝感情的、F0小＝自然とは判定しない。F0は自己相関法の簡易推定。参考値であり聴感の代替ではない。

## 3. 「すぐに」詳細(P5比、機械指標のみ。聴感は未実施)
- P5: 1.00s / F0 std 2.48 / F0 range 6.67 / RMS dyn 20.2 / 無音比0.51。
- P6: 1.12s / 2.94 / 7.60 / 22.1 / 0.454 -- P5よりF0幅・音量変動がやや大きい(指標上は「少し抑揚が増えた可能性」。感情かどうかは言えない)。
- P7: 1.05s / 2.48 / 6.80 / 17.2 / 0.505 -- P5とほぼ同等、音量変動は小さい(指標上はP5との差が小さい)。
- P8: 1.12s / 2.28 / 5.56 / 17.8 / 0.50 -- F0幅はP5以下。
- P9: 1.12s / 1.43 / 2.45 / 16.5 / 0.537 -- 最も平坦(指標上。聴感で棒読みかは別途)。
- P10: 1.17s / 4.50 / 12.95 / 28.2 / 0.451 -- 指標上は最大変動で、J3(3.22/8.63/20.6)を上回る。「すぐに」の不要な感情が再発しているかは聴感で要確認。
- J3: 1.21s / 3.22 / 8.63 / 20.6 / 0.47。

## 4. P5との差(指標で言える/言えない)
- 言える: P6は5 Phrase平均でP5よりF0 range(+0.9st)・RMS dyn(+1.4dB)・無音比低下(0.41→0.37)=やや抑揚が増える方向。P7は平均でP5とほぼ同等(長さが短い1.45s、無音比同じ)。P9は最も平坦、P8/P10は変動が大きくJ3に近い/超える。
- 言えない: 自然さ・温かみ・感情過多の有無・棒読み感は機械指標では判定不可。ユーザー試聴で判断。
- 1 Takeのため、Style差と生成ゆらぎは分離できない(例: P6 kp5のF0 std 0.72はP6の傾向か揺らぎか不明)。

## 5. ASR
25件中 EXACT 20、NORMALIZED(句点付き)3(P6/P7/P9のkp5)、TRUE_CONTENT_MISMATCH 2(P6 kp2「生米」、P7 kp2「斜め」)。不一致の再生成はしていない(委任の25 call枠・Trial趣旨のため。再生成するかはFable判断)。

## 6. 推奨(Fable判断材料。聴感代替ではない)
- 中心候補P6・P7。ただし両者とも「生豆」でASR不一致があり、聴感で発音を確認してから判断するのが安全。P7はP5に近く(安全側)、P6はP5より抑揚が増える方向(機械指標)。
- P8(ニュース風)はASR全一致で指標上の変動はJ3に近い。P9は平坦で「P5より抑揚」目的に合わない可能性。P10は「すぐに」の変動が最大で感情再発リスク。

## 7. 費用
25 call / retry 0 / 失敗 0 / TTS JPY0.946 + ASR JPY0.105 = 約JPY1.05(見積TTS1.46)。

## 8. 共有state不変・Dangling
`evidence/shared_state_sha_before.json`/`_after.json`、`evidence/protected_sha_before.txt`/`_after.txt`、`evidence/git_status_*.txt`、`evidence/dangling_ref_check.txt` 参照。

### 共有state不変の結果
- 保護対象(Coffee完成版user_test/coffee_m2p0_n01_final_03・元run dir・Trial-01 output・Trial-01 page)のsha一覧380件、git status差分: 実行前後で完全一致(`protected_sha_*.txt`、`git_status_*.txt`。元run dirの既存未追跡/変更はTrial-02以前からで不変)。
- 共有state(`shared_state_sha_before/after.json`)は3ファイルのshaが変化し1ファイルが追加された(human_review_queue.jsonl、attempt_history.jsonl、en_asr telemetry、`er011_output/local_rewrite_recovery/run_kgcpw_z_e2e_01/...`)。本Trialのscriptはこれらを読取(sha計算)のみで書込まない(grepで確認可能)。追加ファイルのpathが並行タスクKGCPW 委任_04の`run_kgcpw_z_e2e_01`であり、並行run由来と判断(本Trial起因ではない)。
- 注: T-0 check_delegation_prompt はFAIL(委任文保存時の見出し構成が「事前指定Grep一覧」「実行コマンド全文」の節名と不一致のため)。記録用でブロッキングではない。
