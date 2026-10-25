# PREREGISTERED_CRITERIA_02 — 事前登録(改訂。Opusレビュー M1〜M6反映後、LLM感情情報・TTS生成の観測前に固定)

固定日: 2026-10-25(委任_02。Phase 1a のLLM出力・Phase 1bのTTS生成は**いずれも未観測**の時点)。PREREGISTERED_CRITERIA_01 を置換する(01は履歴として残置。01のStatus体系 `TRIAL_COMPLETE_NO_EFFECT` / `TRIAL_FAILED_QUALITY` / `VALIDATED(限定)` は本書の写像に従う)。
以後、結果を見てから基準を動かさない。新たな必須Gate・数値Gateは作らない(ユーザー指示)。本書の数値は**観測・報告の区分**であり、Production Gateではない。
根拠: `OPUS_REVIEW_01.md` §1〜§6(M4: §6)。

## 1. 評価6項目(ユーザー指示)— 01から不変

感情表現 / 抑揚 / 会話の自然さ / 演出 / 聞き取りやすさ / 安定性。聴感の判定者はユーザー(AIに聴取手段は無い)。機械指標は参考であり、聴感の代替ではない。

## 2. 比較設計(arm構成と順序)

- 比較対象: **①**=Production既存take(`er026_output/.../run_sf_prod_01/b1b`の原音・最終音声。読み取りのみ) / **base**=①と同一style・新規1 take(`base_t1`) / **②**=ctx(`ctx_t1`、`ctx_t2`の2 take)。
- 実行順(同一セッション連続、Opus R1): `ctx_t1 → base_t1 → ctx_t2`(`gen-session`)。モデル更新・時間帯差は base と ①の差で検出する。
- ①側n=2 = {既存take, base_t1}、②側n=2 = {ctx_t1, ctx_t2}。
- 機械指標は**速度加工前の原音**で計測(Production Adv会話は生成後に約6%高速化[atempo=1.06]するが、全armで同一処理のため差の比較には影響しない)。試聴用の主音声は、Production同一実装(`er008.apply_a2_slowdown`, pct=`er063.Z_ADV_DIALOGUE_SLOWDOWN_PCT`)で加工した**最終相当音声**(Opus R2。API 0、加工後ASR再検証なし=限界として報告)。
- 試聴ページ: A=現行方式(Production既存の最終音声)/ B=改善方式(ctx_t1最終相当)/ A'=現行方式の別take(base_t1)/ B'=改善方式の別take(ctx_t2)。音量はtarget_rmsで揃える(本番でも各セリフは音量を揃える)。ページ注記: 「本番でも各セリフの音量は揃えられるため、音量の大小ではなく、声の柔らかさ・息づかい・速さ・抑揚で比べてください」。

## 3. Statusの3値と写像(Opus M4。ユーザー指示の3値のみ)

| 提出時点の機械状態 | Status | 備考 |
|---|---|---|
| (a)(b)(c)(e)(f)(g)がすべて成立 | **USER_DECISION_REQUIRED(試聴判断待ち)** | (d)の有無は下位ラベルに記録するだけで、提出可否を決めない |
| (a)(b)(c)(e)(f)のいずれかが不成立、または(g)費用超過 | **REJECTED**(下位ラベル `TRIAL_FAILED_QUALITY`) | 原因を示し、Style改訂の再Trial/方式転換をFableが判断(自動反復しない) |
| ユーザー試聴で「改善」 | **VALIDATED**(Production採用ではない) | 到達上限。量産化にはreuse key拡張・新Gate等が必要で別途承認 |
| ユーザー試聴で「悪化」「効果なし」 | **REJECTED**(下位ラベル `TRIAL_COMPLETE_NO_EFFECT` 等) | |

成立条件:
- (a) ②の全8件×2 takeで最終statusがOK(Production ASR検査PASS)かつASR転写が得られている。
- (b) leakage_final(最終採用attemptの転写)で `flagged` が0件。leakage_any_attempt(途中attemptを含む)は別に全件報告し、混入があった事実は隠さない。
- (c) 発音悪化なし = Production既存Gate(ASR一致)PASS。
- (d) **補助証拠(必須条件ではない)**: 主指標の機械的効果(§5)。
- (e) Madame(part2_c4)の安定監視で②両takeが①・baseの範囲±20%内(§5)。
- (f) 全②でcomparison_valid=true(最終採用attemptがminimal_fallbackでなく、実送信promptのshaが期待値と一致)かつrequest_full.jsonが保存済み。
- (g) 実費が個別Cap 30円以内(raw_usage_log.jsonlから集計)。

## 4. leakage定義(Opus M1)

- 本文tokenとASR tokenを `difflib.SequenceMatcher(autojunk=False)` で整列し、insert/replaceでASR側が余分に持つtokenを抽出。
- `flagged` = 余分tokenの連続長≥2、または余分tokenのいずれかが「CONTEXTにだけある語」(CONTEXTブロックにあり本文に無い語)。
- `needs_listen` = 余分tokenが1つでもある(観測項目)。長さ補助: ②の長さ > 1.4×median(①, base) かつ差が+0.6秒超なら `needs_listen`。
- 全attemptのASRを検査し、`leakage_any_attempt` と `leakage_final` を分ける。baseにも同じ検査を適用(期待値0)。
- `flagged` は混入の疑い。確定は転写と音声長の確認(Fable)とユーザー試聴。

## 5. 主指標と期待方向(clipごとに1つ。結果を見る前に固定)

| clip | 主指標(加工前の原音) | 期待方向(②) | 根拠(原文) |
|---|---|---|---|
| part2_c7 (祈り・ささやき) | 揃える前RMS(rms_dbfs) | ↓ | `she whispered.` |
| part3_c4 (涙ながらの笑顔) | 調音話速(articulation_wpm_300) | ↓ | `smiling through tears` |
| part3_c8 (Jim、穏やか) | 調音話速 | ↓ | `smiled gently` |
| part3_c2 (動揺→必死の説明) | 調音話速 | ↑ | `Della rushed toward him.` |
| part3_c6 (喜び) | F0中央値(median_hz) | ↑ | `Look!` + 場面 |
| part2_c2 / part2_c5 | 方向なし(過剰監視) | ②両takeのF0幅(p10-p90半音) > 1.5×max(①,base) なら過剰演技疑い | `caught her breath` / `shut her eyes` |
| part2_c4 (Madame、対照) | 安定監視 | 長さ・調音話速・F0幅・RMS(線形)のすべてで ②両takeが①・baseの[min×0.8, max×1.2]内 | 感情・演出の明記なし |

- **「take間差を超える」= 完全分離**: ②の2値がいずれも、①側の2値(既存take, base_t1)より期待方向側にある(「↓」なら max(②) < min(①))。逆向きの完全分離も記録する。帰無仮説(②と①が区別できない)の下で1件が完全分離する確率は1/6。
- 方向あり5件のうち **3件以上で完全分離 = 「効果あり(機械的)」**(偶然の確率 約3.6%)、**1件以下 = 「機械的には効果なし」**、**2件 = 保留**。いずれも補助証拠で、ユーザー試聴に代わらない。
- F0はプロトタイプの自己相関推定で粗い指標。聴感の代替ではない。RMSは揃える前の値(試聴ページは音量を揃える)で、dev側の指標。

## 6. Fable独立評価の手順

1. `py er118_fz_dialogue_context_tts_trial_01.py analyze`(API 0)で `analysis.json`(`evaluation` ブロック: separation / overact_watch / stability_watch / conditions_abcefg / leakage_any_attempt_clips / needs_listen_clips / status_candidate)と最終相当音声・試聴ページを得る。
2. leakageのflagged/needs_listen clipは、転写と音声長を確認し、混入と判断すれば「②NG」として報告。
3. 感情情報(LLM)の創作疑いは `llm/emotion_review.json` のFable判定と `EMOTION_CANDIDATES_01.md` で確認済みであることを前提にする。
4. 結論は「②が①より優れる」と断定せず、機械的に観測できた事実とユーザー試聴の観点を件別に提示する。
5. Production ASR再検証(速度加工後)で静かな発話が落ちる可能性は**未検証の限界**として報告に必ず書く。

## 7. 事前に認識しているリスクと対応

CONTEXT読み上げ(M1/M3) / 既存styleの「Avoid becoming passive, flat」「wider vocal range」との衝突(CONTEXT_TAILの限定的優先順位、追加のみ。①の文字列は不変) / LLM感情情報の創作・強度語(M6、Fableレビュー) / 中立fallbackが平板化を指示してしまう問題(M2、状態行自体を出さない) / take揺れ(対照base・n=2・完全分離) / 再利用分離(sink隔離、Trial専用reuse key、protected snapshot、repo全体mtime走査) / 費用(arm構成: ②×2 take+base×1 take、約16円、retry予備込み約19.5円、Cap 30円)。

## 8. 任意枠(今回は実施しない)

Opus O1: A/B伏せ切替、決定論のみのarm②'(LLM感情を使わない)は、②の効果確認後に別検討(Fable判断。約+5円)。
