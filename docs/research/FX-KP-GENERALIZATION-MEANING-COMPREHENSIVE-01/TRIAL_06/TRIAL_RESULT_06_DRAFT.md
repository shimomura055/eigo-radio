# TRIAL_RESULT_06_DRAFT: X2p'補強Trial 実行結果(委任_31、ラベル待ち。PASS/FAIL判定は未実施=Fable/Opus)

Status: **EXECUTED_PENDING_LABELS**(最終Status[REJECTED/VALIDATED/USER_DECISION_REQUIRED]はFable判定後)。Production配線なし。

## 1. 実行事実(機械的)
- 構成: P案(本番相当 full-level・1 level全KP 1 call・rules_fulltext・prior・retry上限2)。arm=B0p(現行`ga.align_glosses`)/X2pp(X2p')。X2p' Promptは無変更(PROMPT_DIFF: なし)。
- 実行: HC 9KP x rep1,2 x 2arm / R 7KP x X2pp x 1 / S2 54評価KP(生成対象161KP、sibling 107)x 2arm x 1。計102 call、**19.306円**(見積20.99円・cap 28円以下)。全group ALIGN_PASS、retry(attempts>1) 0、JSON失敗 0、HALT(実質)なし。
- Production hash start/end: **一致**(`production_hash_start.txt`/`_end.txt`、diff空)。
- 詳細: `METRICS_06.md`、`BUDGET_LOG_T6_01.md`。

## 2. 記録項目(ユーザー確認6項目)
1. 本番構成での効果再現: Stage 2 54評価KP(+sibling 107生成)で、B0p/X2ppの文字列。strict PASS/THIN/FAIL/FAIL_LIT分布 = **ラベル待ち**: B0p [ ] / X2pp [ ]。
2. 新難例9件(HC、rep1,2): 文字列の変化(事実のみ): 9KP中、B0pとX2ppで文字列が両rep一致=`jump into action`のみ、`one's face harden`はX2pp両rep同一(B0pは別表現)。他はrep間・arm間で差。判定 = **ラベル待ち**。
3. 過剰解釈: 対照 `sheltered from the rain` = B0p「雨を避けている」「雨をしのげる」/ X2pp「雨をしのいでいる」「雨をしのいで」。解釈訳化の有無 = **ラベル待ち**(盲検表に含む)。
4. 通常KP品質維持: Stage 2 PASS->THIN/FAIL件数 = **ラベル後に `agree` で再計算**。
5. 実測単価: 下表(METRICS_06.md)。
6. X/Y/Z適用可能性: 下記。
- 実測(Stage 2、本番構成、33 level): B0p 4.281円(0.0266円/KP、wall/level 12.8s、出力tok 228/KP、reasoning 146/KP) / X2pp 11.337円(0.0704円/KP、wall/level 38.6s、出力tok 761/KP、reasoning 639/KP)。X2pp/B0p=2.6倍。1記事セット(約10KP、sibling込み)換算: B0p 0.27円 -> X2pp 0.70円(増分約0.44円=70円目標の0.6%)。level当たりwall増分約25.8s(2 worker並列実行下の値。単独実行より長い可能性あり、参考)。見積(外挿)に対し実測は低い: X2pp見積15.17円→実測11.34円。
- record-only持ち込み検出(`neg_in_gloss_not_in_kp`、評価KP出力): B0p 2件(`keep one's eyes on them`「目を離さない」x2、定訳ゆえ偽陽性)、X2pp 5件(`keep one's eyes on them` x2、`feel borrowed`「自分のものではないように感じる」、`behind the scenes`「表に出ずに」、`fill in`「足りないところを補う」[「足りない」への偽陽性])。**regexの偽陽性を含む。合否に使わない**。内訳はFableが盲検ラベル後に確認。
- X/Y/Z: Xは本Trialの主対象(S2はXが主、Z小説KPも一部含む)。ZはHCにZ小説5KP(`keep one's eyes on them`/`legs fail someone`/`one's face harden`/`sheltered from the rain`/`smile through one's tears`)を含み別集計可(`blind_06b_key.json`のsetはHC。Z小説KPは盲検表のkey名で識別)。Yは`er110_family_y_*`にalign_glosses呼出なし(Grep: er110系にgloss生成経路なし)。Y音声Trialは共通の`keywords_canonicalized.json`を読み`xr._assert_no_gloss_alignment_hr`で検査するのみ=gloss生成は共通KP段(`er003_v1_n3_01_scaffold_generate.py:539 align_glosses`系)に依存。Yへ適用する場合の経路はOPEN-484(Y Production化時の必須受入条件)と同じ共通KP段への配線になる(実装なし、事実のみ)。

## 3. 判定基準(TRIAL_DESIGN_07 §3、出力前に固定済み)との照合欄(ラベル後に記入)
| 基準 | 結果 |
|---|---|
| (b) HC: X2pp FAIL系<=B0p、B0p=PASS->X2pp<=THIN 0、THIN<=B0p+1、持ち込み検出が増えない | [ ] |
| (b') R退行: X2pp FAIL系0・THIN<=2 | [ ] |
| (c) Stage2: PASS->FAIL系0、PASS->THIN<=2/54(厳しい側)、全itemADOPT(HR=0)、持ち込み検出<=3 | 全group ALIGN_PASS=達成。他は[ ] |
| 総合Status | [ ] |

## 4. ラベル付け手順
1. 盲検表 `TRIAL_06/blind_06b.md`(51行・100文字列、うち継承ラベル44)をFableと別context(Opus)で、`OPUS_EVAL_REQUEST_06.md`に従いラベル付け。labelsは `{"<行>:<列>":"PASS|THIN|FAIL|FAIL_LIT"}` のJSON。
2. 集計: `py er112_kp_gm_trial_06_blind2.py agree --labels1 <fable.json> --labels2 <opus.json>`(厳しい方採用、arm別分布、B0p=PASS->X2pp<=THIN、Stage 2のB0最良[B0_t4+B0p]基準のPASS->THIN/FAIL・改善件数)。単価・時間: `py er112_kp_gm_trial_06_blind2.py metrics`。
