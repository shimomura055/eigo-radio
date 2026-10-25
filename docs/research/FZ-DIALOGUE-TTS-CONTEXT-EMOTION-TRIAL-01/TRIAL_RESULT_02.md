# TRIAL_RESULT_02 — 追加2作品(開いた窓・猿の手)のセリフ音声: 現行方式 vs 文脈・感情追加(Phase 1b、委任_05)

状態: Trial(DEV専用、Production変更0)。Production採用ではない。ユーザー試聴前の提出資料。詳細な機械指標=`EVAL_02.md`、実費=`BUDGET_LOG_02.md`。

## 1. 試聴URL
https://shimomura055.github.io/eigo-radio/user_test/fz_dialogue_context_trial_02/index.html (2作品×8セリフ。A=現行方式[本番最終音声]/B=改善方式[ctx_t1]/A'=現行方式の別take[base_t1]/B'=改善方式の別take[ctx_t2]。本文・場面感情の短い説明・前後文脈つき。noindex。前回『賢者の贈り物』ページ `.../fz_dialogue_context_trial_01/index.html` へリンク)。音量は揃えてあります。

## 2. 対象と感情レビュー(Fable決定の反映)
16件: 開いた窓 8(accept 8、うちNO_EXPLICIT_CUE 2は状態行なし)/猿の手 8(accept 7、discard 1=part2_c6は中立)。選定理由=`SELECTION_02.md`。

## 3. ユーザー原文§4の5項目への機械所見(聴感は試聴で判断)
1. 抑揚・演技の改善: 機械指標で期待方向に**完全分離した件は 開いた窓 2/5、猿の手 1/5**(賢者 1/5)。逆向きの完全分離が各1件。声の抑揚が文脈で改善したと言える機械証拠は弱い。聴感判断はユーザー。
2. 自然さ・過剰演技: 過剰演技監視は4件とも疑いなし(F0幅が1.5倍超となったclipなし)。自然さは機械では測れず試聴に残す。
3. 本文一致・混入: ASR逐語一致 ctx 32/32 take(2作品×8×2)、leakage(最終・全attempt)0、comparison_valid 48/48。猿の手の2件(part2_c2:ctx_t2 3.86秒、part3_c1:ctx_t2 4.29秒)は①側より長くneeds_listen。転写は本文と一致し、ゆっくり読みと見られるが試聴で確認要。
4. 2takeでの安定: ctx 2take間の差が小さく再現性が高いのは正方向分離4件のうち3件(3作品15件中)。分離しなかった多くのclipは2takeの差が大きく、効果は**一部のclipのみ**で安定。
5. 特徴: `EVAL_02.md` §5(事前登録外)。要約=明確な1語の手がかり(murmured/calmly/smile)で出ることがあるが、同じ明確な手がかりでも出ない件があり、短文(4語前後)の話速は不安定。下げ方向(静・穏・悲)は動くが逆にも出る/上げ方向(急ぎ・明るさ・笑い)は分離しにくい。

## 4. 3作品横断(賢者 Round 1 + 本Round)
| 作品 | 主指標 正方向完全分離 | 逆向き | (e)安定監視 | 事前登録の写像 |
|---|---|---|---|---|
| 賢者 | 1/5 | 0 | 不成立 | REJECTED候補(d=機械的に効果なし) |
| 開いた窓 | 2/5 | 1 | 不成立 | REJECTED候補(d=保留) |
| 猿の手 | 1/5 | 1 | 不成立 | REJECTED候補(d=機械的に効果なし) |
| 合計(追加分析) | 4/15 | 2 | - | - |
(a)(b)(c)(f)(g)は3作品とも成立。事前登録の基準は変更していない。

## 5. Status候補
- 事前登録の機械写像: 2作品とも (e)不成立 → **REJECTED(下位ラベル TRIAL_FAILED_QUALITY相当)**。(d)機械的効果は 開いた窓 保留・猿の手 効果なし(補助証拠)。
- 到達上限はVALIDATED(限定)の候補提示まで。ユーザー試聴で「改善」ならVALIDATED(限定)、「悪化・効果なし」ならREJECTED(TRIAL_COMPLETE_NO_EFFECT)。Statusの確定はFable/ユーザー。
- 留意: 3作品とも(e)がF0幅で不成立で、中立条件(猿の手part2_c6)でも不成立。(e)の判定幅が指標の自然なゆれより狭い可能性があるが、事前登録は変更していない(基準変更はユーザー承認事項)。
- 費用: 実費 27.99円/30円(Production化した場合の量産単価影響は`TRIAL_RESULT_01.md` §6の概算を参照。未試算分あり)。

## 6. ユーザー試聴の論点
(1) 開いた窓 part1_c10(つぶやき)・part3_c11(落ち着いた作り話)・猿の手 part1_c15(微笑み)で、Bが場面に合う声か (2) 逆向きの part3_c9(開いた窓 calmly)・猿の手 part2_c10(恐れ)でBが不自然か (3) 猿の手 part2_c2/part3_c1 の B' が遅すぎ・不自然でないか (4) A と A'、B と B' の違い(偶然のゆれ)と A/B の違いの大小 (5) 全体として、文脈・感情を足す価値を感じるか。

## 7. Fable評価欄
(空欄 — Fable記入)

## 8. SSOT・Git
SSOT本体は未編集(X委任_01が編集権保有)。追記文案は`docs/pm/RESULT_PACKET_FZDC5.md`。コード/証跡: `er118_fz_dialogue_context_tts_trial_01.py`、`er118_output/fz_dialogue_context_tts_trial_02/`。
