# KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 Fable独立受入 (2026-10-31)

結論: **ACCEPTED、Status=PRODUCTION_WIRED(全6経路 X/Y/Z x Std/Adv、2026-10-31)**。

## 1. 当初目的
ユーザーが正式採用したN5方式(Trial 03方式B)を、全Family・全レベルの正式Production経路へ配線し、意味・用法・日本語訳の正確性を維持してPRODUCTION_WIREDに到達させる。新Trial・新基準・新Gate追加は目的でない(原文:96)。

## 2. 要求された最終状態(ユーザー原文逐語、`docs/pm/delegation_log/2026-10-30_KP-GENERALIZATION-N5-PRODUCTION-WIRING-01_USER.md`)
- :7 「**採用方式：Trial 03 方式B（N5）**」
- :9 「**Status：APPROVED_FOR_PRODUCTION**」
- :11 「**最終到達目標：PRODUCTION_WIRED**」
- :19 「ユーザーは、Trial 03の品質結果、良質候補の脱落、残存する境界例、量産単価への影響を確認したうえで、**N5の正式Production採用を承認した。**」
- :96 「ここでの目的は、新しい基準でTrialをやり直すことではなく、**承認されたN5の挙動を正式経路でも再現すること**である。」
- :120 「全6経路で必要条件が満たされた場合のみPRODUCTION_WIREDとする。」
- :174 「**最終目標：ユーザーが正式採用したN5方式が、全Family・全レベルの正式Production経路で確実に動作し、意味・用法・日本語訳の正確性を維持した状態でPRODUCTION_WIREDに到達すること。**」

## 3. 実際に生成・残存した最終成果物
- 成功経路: X/Y/Z x Std/Adv の6経路で、`er119_kp_candidates_01.py`の合流点2か所から`er138_kp_n5_generalization_01.py`(方式id `N5@T3-2026-10-30`、flag/kill switchなし=既定ON)が走り、N5付き候補doc(`kp_candidates*.json`、`n5`欄・`japanese_gloss`==`n5.gloss_ja`)を出力。commits 3d404cfc6(委任_02)/728d80d60(委任_03)/2384cdd81(委任_04)/55d613a48(委任_05)。
- 失敗経路: N5技術失敗は`canonicalization_N5_TECHNICAL_FAILURE`/`n5_select_failed`として外側retryへ。外側retry尽きは`OUTER_RETRY_EXHAUSTED`で候補0、契約違反はSTOP rc=2。**N5なし候補は出力しない(旧方式へ戻らない)**。実run確認=X a2 injection(外側retry 1->2で回復、N5なし候補0、EVIDENCE_03 §5-1)、SEL_DEFERRED再判定callの失敗もtest2件で同経路を確認(§10-3)。

## 4. 証拠(file:line・観測値)
- EVIDENCE_03 §1: J2是正(Trial入力条件の再現、包含相手が非keepの場合のみSEL再判定=SEL_DEFERRED)。Trial 19ケースのL1選定exact一致(`ev03/j2_part1_result.json`)。④は決定論検証で保持(`ev03/j2_part2_result.json`)。実run 10L1中3件でdeferral発火(`ev03/j2_deferral_in_real_runs.json`)。
- §3(M10 3level, 公式`generate_candidates`): 既存Gate喪失0件。§4A①②③④⑤喪失なし。
- §10-1 / `ev03/m10/analysis.txt`(4level、基準`ev03/m10_thresholds_fixed.md`同一): Trial生存候補28 -> 同span保持13、N5 drop 2、**既存Gate喪失1件(`gets heated`、canonicalization_qa=救済後未検査fail-closed、N5無関係)=1/28=3.6%(基準15%以下)**。
- §4/§5: 正式runner CLIでX/Y/Z x a2/b1b再証拠、技術失敗injection・Y/Z再選定round・resume実走。
- §9: 12必須項目充足。⑪は`ev03/p11_fixture_result_02.json`(正式関数`_gate_chain`経路、`n5_gloss_ja_after`==`japanese_gloss_after`=「人をぞっとさせ、強い恐怖を感じさせる」、旧値は`n5.person_repair.gloss_before`のみ)。
- `er119_kp_candidates_01.py:341`: 人称整合書換時の`x["n5"]["gloss_ja"]=x.get("japanese_gloss")`(不変条件`japanese_gloss==n5.gloss_ja`の是正、委任_05)。
- `er138_kp_n5_generalization_01.py:1289`: `select(..., label="SEL_DEFERRED")`、失敗は`N5TechnicalFailure`で外側retryへ伝播(§10-3、test PASS)。
- §10-5: check_decision_quality status=OK。tests: er138系93件(wiring33+generalization60)PASS。
- 開発実費: 委任_02 ¥73.38 + 委任_03 ¥63.57 + 委任_04 ¥7.98 + 委任_05 ¥0.07 = 約¥145.0(JST日次の下限集計は§10-4)。

## 5. 目的要件との一致・不一致(項目ごと)
| 要件 | 判定 |
|---|---|
| 採用=方式B(N5)そのもの(:7,:9) | 一致。方式id `N5@T3-2026-10-30`。D/E1L/E4/N2は配線なし(:21) |
| 全6経路(X/Y/Z x Std/Adv)で動作(:120,:174) | 一致。EVIDENCE_02/03で6経路runtime evidence |
| 正式経路でN5の挙動を再現、新基準・新Gate追加なし(:96) | 一致。新Gate/Prompt/閾値追加0、flagなし。SEL_DEFERRED=Trial入力条件の再現(11-8範囲内是正、Trial差分として記録) |
| 意味・用法・日本語訳の正確性維持(:174) | 一致。§4A①②④⑤保持、③は生成時に正しく処理、n5.gloss_ja同期(不変条件是正) |
| 既存Gate維持 | 一致(喪失1/28=3.6%、N5無関係の既存fail-closed) |
| 失敗終了時に不整合成果物を残さない | 一致(N5なし候補を出さない、候補0/STOP) |
| 12必須項目 | 一致(①〜⑫。⑪はfixture確認、自然発生0件は注記) |
| 量産単価 | N5段 X 6.92/Y 8.90/Z 5.58円 /記事セット(Trial見積6.28円)。承認済みTrial想定内 |
不一致: なし(下記未確認事項は注記であり不一致ではない)。

## 6. 最終受入判定と理由
**ACCEPTED、PRODUCTION_WIRED(全6経路、2026-10-31)**。ユーザー原文:120の「全6経路で必要条件が満たされた」を、上記の実run証拠とfixture/test証拠で確認した。未確認事項は品質・安全に影響せず、観測0または非決定性に起因するため受入を妨げない。旧UDR #228は本採用に統合・解消済み(`docs/pm/USER_DECISION_REGISTER_01.md:620`)、Dangling Reference 0を確認。

判定整合: 重大NG=なし

## 未確認事項
1. ⑪人称書換のN5 gloss更新は自然発生0件(全7docで`n5_gloss_rewritten=0`)。正式関数経路のfixtureで確認。
2. X b1bの是正後再証拠はrunner CLIでなく公式`generate_candidates`経路のM10 untidi_b1b。
3. ③`kept his eyes on them`はLLM非決定性により毎回は生成されない(生成された回は正しく処理)。
4. SEL_DEFERRED限界: 包含相手がkeepだが後段QAで落ちる場合、supersetは復活しない(観測0)。
