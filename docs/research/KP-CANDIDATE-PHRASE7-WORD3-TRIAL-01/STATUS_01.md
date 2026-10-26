# STATUS_01 (KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01、2026-10-26)

## 1. Status案(DEV実行層の提案。最終判定=Fable/ユーザー)
**判断候補(Trialとして VALIDATED でも REJECTED でもない中間。ユーザー判断が必要な採否)**
根拠: DESIGN_01 §8(API実行前に固定・sha256=`DESIGN_01.sha256`)の事前基準に照らした結果。
| 事前基準 | 結果 | 判定 |
|---|---|---|
| (1) 12 runの自Y件数 median≥6 かつ min≥5 | median 5.5・min 3(Y≥6は6/12 run)。**judge基準では median 6・min 5で充足** | **不充足(自ルーブリック基準)** |
| (2) 単語Yが1件以上あるlevelが6中≥4 | 6/6 | 充足 |
| (3) フレーズY率が現行から10pt超低下しない | 62%(36/58) vs 61%(20/33) | 充足 |
| (4) filler(N)割合が現行+10pt以内 | 4%(4/94) vs 21%(8/38) | 充足(改善) |
| (5) Gateの Production同一適用 | Production関数import・DefaultOffIsolation型test PASS・Production差分0 | 充足 |
REJECTED条件(Y median<5 / フレーズY率-10pt超 / filler+10pt超)はいずれも非該当。(1)のみ未達のため事前規則により「判断候補」。
**ユーザー原文の核心への回答**: 『10件要求で数合わせによる品質低下を起こさず、有用候補を6〜7件程度確保できるか』
- 数合わせ品質低下: **起きていない**(N割合は現行21%→4%、フレーズY率は同等)。ただし猿の手Advancedのみフレーズ枠が記事固有句で埋まる傾向(§COMPARISON 2)。
- 6〜7件の確保: 『有用』を**Y+B(境界を含む)**とすれば12/12 runで6件以上(min 6・median 7.5・max 9)。**厳格Yのみ**では6/12 run(median 5.5・min 3)。現行は厳格Y median 4・Y+B median 5.5(0/6 levelでY≥6)。
- 主な効果は単語の純増(各run 3件・うち自Y 平均2.2件)であり、フレーズは増えない(P7は平均5.4件しか返さない)。

## 2. 追加Trial要否
必要十分な品質の確認という観点では、追加Trialは不要と考える(Charter 1)。残る不確実性(§4)は『採用の可否』ではなく『有用の閾値(Y/B)の定義』と『文学作品Advancedの扱い』というユーザー判断事項。追加Trialを行う場合は、(a)P7要求数を5に下げた変種、(b)Y(Family Y)記事1本、が候補だが、いずれも判断前に必須ではない。

## 3. Production採用時の変更点(採用提案の素案。採用の提案そのものはFable/ユーザー。VALIDATED相当でもProduction実装へは自動移行しない)
- Prompt: 現行Prompt 2(call1・3件)とPrompt 2-V(call2・最大5件)を、P7(フレーズ最大7、sha256先頭=`2e93019300f960e5…/7a9c47a01410bd9f…`(P7/W3))とW3(単語最大3)に置換。Prompt 2は条件1〜5と最終確認文を無変更で流用(P7はPrompt 2から冒頭の件数文と条件6のみ置換)。**Production Promptの変更に当たるためユーザー正式承認が必要**(CLAUDE.md禁止事項: 承認済みPrompt変更)。sha固定test(`er105`/`er119_kp_prompt_2v`)の更新も伴う。
- call数: 選定2 call(現行と同数。P7→W3の直列)。canonicalization/gloss/RQAは件数増(平均7.25→8.4件)で入力が増えるのみ。
- HR表示・候補数仕様: 最終候補が最大10件(Trial最大9件)となり `KP_CANDIDATE_MAX=8` 仕様(`er119_kp_human_review_01.py:49`)と不整合。表示件数・shortfall定義の見直しが必要。また候補順(フレーズ→単語)のままだと、AI推奨(先頭3件=KP、Advは先頭5件=単語解説vocab、`er119_kp_human_review_01.py:550-551`)では**単語が自動採用に届かない**(単語は6位以降)ため、『単語枠』の扱い(HRで単語を選べる区分表示、Advのvocab5件への単語組入れ規則)が採用仕様として別途必要。
- 単価影響: +¥0.19/level、約+¥0.4/記事セット(目標¥70の約0.5%)。時間: 並列起動条件下で平均+25秒/level(参考)。
- 隔離: 本Trialのモジュール(`er124_kp_phrase_word_trial_01.py`)はProduction経路へ到達しない。Production採用時は単一flag読取関数+既定OFFの11-7限定例外は**Promptを直接編集する性質のため適用不可**(11-7(2))。正式採用は Offline Trial→VALIDATED→ユーザー正式採用→Production実装の経路。

## 4. 一般化できる範囲/未確認
- 一般化できる: (a)Family X 2記事・Z 1作品の計6 level・各2回で、W3は3件/回の単語を安定して返し、Production Gate(CMU・canonicalization・gloss・RQA)を単語に追加改変なしで通過した (b)P7はフレーズ品質を落とさず、N(数合わせ型)割合は現行より低い (c)費用増は小さい。
- 未確認: (a)Y(Family Y)記事での挙動(Yは平易な説明文で慣用句が少ない可能性。猿の手Advで見られた『フレーズ枠が記事固有句で埋まる』傾向が出るか)。(b)n=6 level×2回で、現行側は1回のみ(現行の分散未測定)。(c)自ルーブリックの主観性(judgeとは67%一致、judgeが甘い)。(d)人間(ユーザー)が『有用』と認める閾値(Y/Bのどこまで)。(e)HR運用での単語枠の見せ方。(f)実音声・公開記事への影響(本Trial範囲外)。
- Family Y(机上): `er121_family_y_runner_01.py:540-569` がX/Zと同じ `er119_kp_wiring.run_kp_with_review`→`generate_candidates` を呼ぶため、P7/W3の注入点(select_fn/vocab_call_fn)は同じ。ただしY正式KP経路の一般化配線は未了(OPEN-484)。Z特有(SRC D1・人称整合)は本Trialで猿の手に実適用(44候補全てsrc_d1=PASS、gloss_hr_pending=0)し問題なし。

## 5. 残る判断候補(OPEN新規の11-8分類: ユーザー判断要)
1. P7→W3方式をProduction仕様候補とするか(Prompt変更・候補数/HR仕様変更を伴うため正式採用判断)。
2. 『有用候補6〜7件』の判定基準(厳格Y基準か、境界Bを含むか)。
3. 採用する場合の単語枠の扱い(HR表示区分、Advのvocab5件・Stdの扱い、AI推奨順)。
4. 文学作品(Z)Advancedでフレーズ枠が記事固有句に偏る傾向への対処(P7要求数5への縮小 or 現状許容)。
