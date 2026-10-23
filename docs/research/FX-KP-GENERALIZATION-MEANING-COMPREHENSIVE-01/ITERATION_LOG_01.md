# ITERATION_LOG_01: Trial反復履歴(委任_02)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 2026-10-23 / 証跡=`er112_output/kp_gm_trial_01/`(runs/・runs_v1/・paid_calls.jsonl・judge/・fable_sampling_list.md)
方針: 同じ方向の漫然反復をしない。各反復は『観測→原因仮説→変更→再測定』を1ブロックで記録。生成=`gpt-6-luna`(本番同一)。費用は`paid_calls.jsonl`の実測(出典)。

## #0 初版(v1)の測定
- 構成: A-1初版(規則5 a/an/the許容)+A-2+A-3 v1+共有。実データ26unit×rep1。
- 観測(`runs_v1/`): `draw that line`→**`draw the line`**(ユーザー明示例の`draw a line`にならない)。`pulled him under`→`pull someone under`、`sentenced him to death`→`sentence someone to death`は成功。一方 `brace yourself for` と `reach for your wallet` が一般化されない例、`bound to the protein`→`bind to`でINVALID(1 unit)。
- 原因仮説: (1)『標準見出し形が定冠詞なら the』の例外文(cross that line→cross the line)が、LLMの『draw the lineが標準イディオム』という知識を呼んだ。(2)規則5の『迷えば置換しない』が規則3(your→one's)の判断にも波及。(3)規則5の例文が時制変化を含み、受動分詞の原形化を誘発。
- 判断: (1)(2)を修正。(3)はbaselineでも発生するか不明のため先に切り分け(下記#1)。

## #1 A-1 v2(今回の最終A-1)
- 変更: (a)規則5(a)を**a/anのみ**に(theは使わない。Opus OF-03(1)の『the許容』からユーザー明示例優先で変更。validator表も`{a, an}`)。(b)規則5末尾に『置換しない判断は規則5の対象語にだけ適用。規則3(人称・所有格)は従来基準で判断し、控えめにしない』を追加。(c)validatorの『直後がブロック語』に接続詞のthat(so that nobody…/that the…)を追加(テストで穴を発見: `so a nobody noticed`がTrueだった)。
- 測定(実データ`a1_c`×rep1〜3+合成): `draw that line`→`draw a line` **6/6**(baseline再生成 0/6、記録済みprod 0/2)。`pulled him under`→`pull someone under` 5/5、`sentenced him to death`→`sentence someone to death` 5/5(baseline 0/3, 0/3)。合成肯定 **14/14**(baseline 0/7)、合成否定(固定表現・that advice・lose her job等) **20/20保持**(baseline 10/10)。
- baseline切り分け: `bound to the protein`のINVALIDは**baselineでも発生**(再生成3rep中 rep1・rep2は1回目attemptがINVALID→retryでPASS、rep3は2回ともINVALID。attempt単位 4/6)。A-1は3rep×2attempt=6/6。A-1由来の追加悪化かは**n不足で判定不能**。既存defect(`bound`を`bind`へ原形化→validator却下)として記録。`reach for your wallet`の非一般化はbaselineも同率(base_c 1/6、A-1 1/6)。`brace yourself for`はbase_c 0/3、A-1 1/3(n=3で判定不能。記録済みprodは一般化済み)=A-1由来の弱い悪化の可能性として残存リスクに記録。
- 副作用(正常KP): 正常item key一致 base_c 58/60 / a1_c 52/54(差分は同じ2件`a time lag`・`a blanket ban`で、規則1の揺れ=baselineと同一)。

## #2 A-2(gloss語義方針)の効果測定 → 採用推奨せず
- 観測: A-1のみ(`a1g`、現行gloss Prompt)で `draw a line`→「一線を引く」、`pull someone under`→「人を水中に引きずり込む」と『その』『彼』の逐語訳が自動的に消えた(機械指標: 『その/彼』混入 prod 2/78 → a1g・a12 0)。Judge(Sonnet、難例gloss): sense_ok prod 37/37 / a1g 26/26 / a12 62/63、逐語(literal)判定は**全armで0件**(OF-07の定義では現行glossに逐語は検出されなかった)。
- A-2が悪化させた例(a12): `draw a line`が「線を引く」「区別をつける」へ(字義寄り/ずれ)、`keep someone company`→「人と一緒に過ごす」(Judge sense_ok=0、prodは「人の相手をする」)。`reach for one's wallet`の字義glossはA-2でも不変(本文が字義的に読めるためJudgeも逐語としない)。
- 判断(憲章1: 必要十分で止める): **A-2は実証的な利得が無く、悪化例がある**。A-1(一般化)が『その』問題の本質的原因だった(ROOT_CAUSE (a)→(c)の連鎖)ので、gloss Prompt変更は不要と判断。

## #3 A-3(Adv説明)の反復: v1→v2→v3
- v1(OF-05反映の2行追加): 難例E(Sonnet) PASS a123s 71% vs a12 74%(差なし)。`draw a line`は『what is acceptable』型が残る/日本語glossが「区別をつける」だとそれに引きずられる。
- v2(辞書的中心義・一般語・状況を書かない): A-1のみitems(`a1gE2`)でも `draw a line`は3/3 『set a limit ... what is acceptable/allowed』。原因仮説修正: 記事の話題ではなく**慣用句`draw the line`の辞書的代表義(許容限界)をLLMが既定に選ぶ**。
- v3(評価的条件[許される/期待される/正しい等]を表現自体が持たない限り足さない、と一般化+検証セット外の対比例): `draw a line`は3/3で『acceptable』消失(『make a clear distinction between two things』『show where one thing ends and another begins』『set a limit or show a clear difference』)=ユーザー期待『establish a clear boundary or limit』に近づいた。
- ただし汎用指標は動かず: E2(核心義のみ・単一義、Sonnet) a1gE0 67% / E2 79% / E3 71%(n=42、差は統計的に有意でない)。**2者Judge(Sonnet+Sol)の両方PASS**: a1gE0 26/42=62% / a1gE3 27/42=64%。Judgeは字義的な物理動作の説明(pull someone under→『below the water』)まで『水に限定』と判定するなど厳しすぎる行があり、E2は粗い指標。
- 判断: **A-3 v3は『ユーザー例は直るが、汎用的な改善は未実証』**。費用はほぼ0(説明1callのPrompt追記のみ)だがPROMPT_SHA256が変わる=承認済みB仕様の変更。採用はユーザー判断(推奨=A-1と切り離し、必要なら別途確認Trial)。

## #4 Std/Adv整合(共有arm)
- 決定論共有(`a123s`): 実データで共有が働いたのは5件のみ(同一run・同一used_form)。P判定(Std gloss vs Adv説明の語義一致)は共有なしでも **a1g 4/4・a12 9/9 が100%**、baseline(prod) 5/7(2者Judge)。改善はA-1(同じ一般形を両レベルが受け取る)で足りており、共有機構は不要(憲章1)。

## #5 停止判断
- A-1は基準を満たした(ユーザー§5 項目1〜3・8)。A-2/共有は効果なし→撤去。A-3は目的例には効くが汎用効果は未実証→これ以上の反復は費用対効果が低いため、結果を提示してFable判断へ。費用=約69円(上限80円内)。
