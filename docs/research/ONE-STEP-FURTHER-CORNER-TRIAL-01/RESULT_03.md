# RESULT_03: One Step Further 最終再設計Trial(委任_03、2026-10-30)

Status: Trial完了(Trial専用・Production未配線・未承認)。前回VALIDATEDは無効(ユーザー実例確認でNG5類型)。Closeout案=**USER_DECISION_REQUIRED**(採否はユーザー。Worker推奨=条件付き採用検討または見送りの二択、後述)。追加Trialは計画していない。
**費用**: 本委任 ¥78.22(29呼出)。委任文の上限¥50(理由記録で¥70まで)を**¥8.22超過**(Gemini最終確認1呼出が¥13.3、事前見積¥5〜6を過小評価したため。以後の有料呼出なし)。Gemini単価は推定(後述)。

## 1. 比較ページ
- 学習コンテンツ: https://shimomura055.github.io/eigo-radio/user_test/one_step_further_trial_01/index.html (原文§8形式。前回候補をNG類型ラベル付きで折りたたみ併置)
- 開発ログ(Gate/監査/費用): 同`dev_log.html`。前回版: `index_v2_archive.html`/`dev_log_v2_archive.html`

## 2. 最終選定(6ケース、8表現。品質を満たす候補がなければ0件=本Trialは全レベル1件以上)
| ケース | 本文からの引用 | 基本(原型)+意味 | One Step Further+意味 | 学習ポイント |
|---|---|---|---|---|
| Y Std | When I heard my son would marry next year and take his wife's last name, I did not like it. | I do not like something / 私はそれを好ましく思わなかった | not be a fan of something / 何かをあまり好まない | a fan ofは有名人のファンだけでなく、物や方法などを好む場合にも使える。 |
| Y Std | Changing my last name did not bother me at all. | not bother someone at all / 改姓は私にとってまったく気にならなかった | not bother someone one bit / 少しも人の気にならない | 否定文のone bitは「少しも～ない」。notと組み合わせて否定を強める。 |
| Y Adv | When they care about different things, how can they choose something they can both accept? | care about different things / それぞれが異なることを大切にしている | have different priorities / それぞれ重視することが異なる | 人同士で重視することの違いを述べる表現。priorityはこの意味では可算名詞。 |
| Y Adv | He took his wife's last name without discussing it with his parents, and… | without discussing something with one's parents / 自分の親にそのことを相談せずに | without talking something over with one's parents / そのことを自分の親に相談せずに | talk something over with someoneで「人に相談する・話し合う」。目的語がitならtalk it overの語順。 |
| X Std | They had no homework, but they were ready to explore. | be ready to explore / 探索する用意ができていた | be all set to explore / 探索に取りかかる用意ができている | be all set to doで「〜する用意ができている」。 |
| X Adv | …the experienced group did better. | do better / 比較対象よりよい成績を収めた | come out ahead of someone / 比較相手よりよい成績を収める | 比較相手はahead ofの後ろに置く。相手が明らかならof以下は省略できる。 |
| Z Std | Every morning, I kindly asked about his night's sleep. | ask about someone's night's sleep / 彼が昨夜よく眠れたか尋ねた | ask how someone slept / 〜がどのように眠れたか尋ねる | 間接疑問ではhowの後ろを主語＋動詞の語順にする。 |
| Z Adv | I checked his pulse. | check someone's pulse / 彼の脈を確認した | take someone's pulse / 〜の脈を測る | 脈を測るときはtakeとpulseを組み合わせる。 |

(引用の原文は本文どおり。基本との違いの短文はページ参照。)

## 3. 前回NG5類型の排除証拠(回帰セット15件、Gate A)
| ID | 出典 | argon | 3.1pro |
|---|---|---|---|
| NG1〜NG5 | 原文§4 | 全てFAIL(主語対象/情報追加/意味の飛躍/単語置換のみ) | 全てFAIL |
| P01〜P07 | 前回主候補7件 | 7/7 FAIL | 5/7 FAIL(P03・P05をPASS_WITH_DIFFで見逃し) |
| G1(make some headway) | 良例① | PASS_WITH_DIFF(headwayは困難下の前進の含み) | PASS_WITH_DIFF |
| G2(your call) | 良例② | PASS_WITH_DIFF(助言→決定権の差を記録。無条件PASSでない) | PASS_WITH_DIFF |
| G3(see where this takes me) | 良方向③ | FAIL(meaning_shift: 試す→成り行きを見る) | PASS_WITH_DIFF |
→ **NG5類型12/12を検出できたのはargonのみ**。3.1proは見逃したためGate A決定から外した。機械検査(長文化・元文を残した延長・語順入替)はNG③/P06を独立に検出。単語1つ差(NG⑤と良例①)は機械では区別せず監査へ(良例①を棄却しないため)。弱点: 回帰セットと実生成は同じ監査器(argon)で、監査器の取りこぼしは残りうる(後述の自己点検)。

## 4. 独立評価(意味保持・学習価値・自然さ)
独立=生成(OpenAI sol)と監査(Google argon)は別ベンダー。選定8件は Gate A通過(R1の4件=PASS 1/PASS_WITH_DIFF 3、R3の4件はframe比較のGate Aを省き本文参照の最終確認で代替)・最終確認PASS(置換文が自然・同義)・Gate B全件閾値内(d4-5, w4-5, b3-5, l4-5, c5)。弱点(監査記載): fan「重い拒絶の場面では軽い」、one bit「at allの言い換え色が強い」、take a pulse「場面が限定的」、all set「平易で発見が小さい」など。**Worker自己点検(厳しめ)**: ①not bother one bit は at all→one bit の強調語置換に近く学習価値が小さい恐れ ②take someone's pulse は check→take の1語差(コロケーション)で良例①型だが差(確認 vs 測定)を持つ ③ask how someone slept は名詞句→節の構文で「語彙の発見」は小さい ④come out ahead は「成績」より「結果的に優位」の含み ⑤各レベル1〜2件に収まったが、候補の半数は監査自身が「平易すぎる/新鮮味が低い」と指摘。Fable・ユーザーの目視で上記の境界を最終判断のこと。

## 5. KP/Word既存方式の再利用
`KP_REUSE_01.md`参照: normalize_text(import)、本文実在Gate、引用逐語実在、原型の連続部分文字列/語幹対応(助動詞禁止ルールは再利用せず逆に否定・法助動詞の保持を追加)、重複除外、backfill発想(不足レベルは検討済みを除外して再抽出)。

## 6. 費用・時間・量産単価への影響
| 段階 | モデル | 費用(円) | 備考 |
|---|---|---|---|
| 回帰(2回+初回の3.1pro) | argon/3.1pro | 22.33 | 開発費(1回限り)。うち初回のv1 3.1pro 12.82は無駄(出力過大・client競合) |
| 抽出R1/R2(luna) | gpt-6-luna | 3.23+1.72 | 1セル約¥0.4 |
| 抽出R3(sol・low、3セル) | gpt-6.1-sol | 6.20 | 1セル約¥2 |
| 生成R1(3ファミリー)+R3 | gpt-6.1-sol | 10.53+4.02 | 1ファミリー(2レベル)約¥3.5 |
| Gate A(18候補)/B(16候補) | argon | 8.62/8.28 | 1候補約¥0.45 |
| 最終確認(12候補・6記事本文) | argon | 13.30 | 17秒 |
合計¥78.22。壁時間: 1記事セット(2レベル)の直列工程で約2〜3分(各段10〜50秒、ファミリー並列)。
**量産単価の見積(Gemini単価は推定)**: 本Trial実績の工程(R1のみで済む場合)で1記事セット約¥15、不足補充(R2/R3)を含めると約¥19。目標70円の約21〜27%。前回方式(sol1回約¥6.5)の約3倍。削減余地: 最終確認をFable/HRに置換、argonの出力短縮、Gate Bの対象を絞る、など(未検証)。
注意: Gemini単価はrepo内に公開単価が無く推定値(argon $5/$25, 3.1pro $2/$12 per 1M)。実請求は異なりうる。

## 7. Fableによる独立受入評価
未実施(Fable担当)。Fableへの依頼点: 8表現のNG5類型・良例との直接比較(特に上記自己点検①〜④)、回帰が監査器の取りこぼしを含まないかの確認。

## 8. Trial Closeout Statusと採否提案
Closeout案=**USER_DECISION_REQUIRED**(VALIDATEDとは付けない。前回VALIDATEDが実例で覆ったため、実例確認なしの高得点は証明としない)。
Worker提案(判断材料): **条件付きで採用検討可能だが、費用が大きい**。品質面: 前回NG5類型と前回7件を検査器が全て検出(argon)。生成の意味対応は今回の8件で目視上おおむね保てている(置換文の自然さ・同義性も本文で確認)。懸念: (a)学習価値が「平易なコロケーションの引き出し増加」中心で、ユーザー良例①②のような鋭い発見は一部のみ、(b)レベルあたり1〜2件を埋めるために基本表現を3ラウンド探す必要があった(特にXは本文が慣用句に乏しい)、(c)1セット約¥15〜19(目標比21〜27%)。採否の論点: 採用するなら(1)コーナー設置の価値判断(Key Phrase/Wordとの差別化は欠陥コードoverlapと機械検査で担保したが、学習者体験としての差別化はユーザー判断)、(2)費用(最終確認をHRに寄せる等の削減策は未検証)、(3)Gate A監査器をargon限定にする場合のモデル依存、(4)HR提示単位。見送りも妥当な選択肢(Trial資産は保管)。

## 9. 生成物
`tools/osf03_lib.py`/`osf03_prompts.py`/`osf03_run.py`/`osf03_page.py`、`out/osf03/`(extract/gen/gateA/gateB/final/select/regress JSON、`usage_log_03.jsonl`、`raw/`)、`user_test/one_step_further_trial_01/`。Production変更0。
