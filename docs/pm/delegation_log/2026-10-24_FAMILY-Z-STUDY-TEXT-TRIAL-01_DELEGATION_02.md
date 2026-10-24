FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_02(Fableから、API 0): Trial-01(commit e3285a2d1)のFable独立評価とStatusを記録し、UDR登録・DECISION_LOG・commit/push。

## Fable独立評価(逐語で `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/FABLE_EVAL_01.md` に記録)
- A 整合性: PASS。引用6件は逐語一致(機械照合)、日本語訳・文法説明に誤りなし、創作なし。catch sight ofの「次の行動を思いつくきっかけ」は原作・本文の流れ(鏡を見て髪を売る決心)に沿った軽い解釈で許容。
- B 学習価値: Part 1=中(hand downの「過去分詞=関係節の短縮」、catch one's breathの「just long enough to do」は音声解説と重複せず有用。ただし「なぜ学習上重要か」が薄く、catch sight ofは自明)。Part 2=良(場所の倒置の選定・説明・効果は妥当。同文のwhose/使役makeに触れていないのは惜しい)。Part 3=弱(worthy of/worthは品詞差の説明で「ニュアンス」ではなく、B1目標のAdvanced学習者に対する価値が低い。本文にはshabby、Nothing showy, nothing unnecessary、foolish↔wisestの皮肉など上位候補があった。「0個でもよい」より「1つ選ぶ」方向に寄った)。Part 4=可(自然だが作品固有の要素に触れない一般論)。
- C Production適性: 形式・構造は1回で充足、費用0.23円/レベル(1記事セット約0.5円=70円目標の0.7%)、人手確認は約10分/レベル(機械照合で引用はカバー可、日本語訳・文法・ニュアンスの妥当性は人手)。N=1のため安定性は未検証。
- **Status(Fable): USER_DECISION_REQUIRED**(VALIDATEDにしない理由: ユーザーが重視した文法・ニュアンスのうち、ニュアンス解説が「学習価値の高い」水準に達していない。REJECTEDにしない理由: 整合性に誤りなし、文法解説は良、形式は一発で充足、費用は無視できる水準で、改善余地はPrompt側の選定基準・観点指示で見込みがある)。
- 改善見込み(Fable): Part 3の選定基準(Advanced学習者が見落としやすい差のみ・基礎語の品詞比較不可・候補を挙げてから選ぶ)とPart 1の「なぜ重要か」観点の明示は、一発生成の原則を崩さずに入れられる。2段階生成は原則とのトレードオフのため推奨しない。

## 作業
1. 上記をFABLE_EVAL_01.mdに保存。EVAL_01.mdに「Fable判定」節を追記(要Fable確認2点への回答: 解釈=許容、worthy/worth=ニュアンス解説としては弱)。
2. `docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR(件名=Family Z学習テキスト解説Trialの次工程。選択肢=(A)Prompt改善版(Part 3選定基準・Part 1観点)で別作品『猿の手』『二十年後』を含むN=3の一発生成Trial(約1円) / (B)現Promptのまま N=3で再現性のみ確認(約1円) / (C)中止。Fable推奨=A。理由=費用は無視でき、弱点がPromptの選定基準に帰着する見込みが高い。採用判断・Production化は別途)。OPEN-497に Status=USER_DECISION_REQUIRED とUDR番号を追記。DECISION_LOG 1エントリ(Trial-01実施・Fable評価・UDR)。
3. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_02.md`(Nは先頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_02」を含むAgent呼出の0始まり通番、直近467以降)。
4. Git: `git status`でindex確認→`git commit --only`→`git push origin HEAD:main`(他agent X/ZのSSOT差分を巻き込まない=一時index方式)。禁止操作(add -A/-u/-f/-N、amend、rebase、force push、stash、clean、reset --hard、checkout -f)。secret grep 0件。
5. handback: UDR番号、commit hash、raw URL。