# comparison_table (NEWS-R2-TO-HOOK-TRIAL-01)

## 表1: R2タイトル / Existing・Reference Hook / 旧方式(Topic概要→Hook) / 新方式(R2記事→Hook)

| Article | R2タイトル | Existing/Reference Hook | 旧方式Luna | 旧方式Terra | 旧方式Sol | Luna from R2 | Terra from R2 | Sol from R2 |
|---|---|---|---|---|---|---|---|---|
| sewer | “合併”するのは町じゃない？　下水道の大引っ越し作戦 | Referenceなし(下水道は既存Trialに対応するReference Hookが存在しない。R2タイトルを比較対象とする) | 旧方式なし(下水道は旧Hook比較Trial対象外) | 旧方式なし(下水道は旧Hook比較Trial対象外) | 旧方式なし(下水道は旧Hook比較Trial対象外) | 町に一つの巨大な洗濯機を、家ごとに分けるって？ | 町の地下の大動脈、家のそばへ引っ越せる？ | 町の巨大な洗濯機を、家ごとに置き直すってどういうこと？ |
| ai_phone | 「もしもし、AIです」――その声の裏で、人間が代役を務めていた | AIに店への電話を頼んだら、裏では人間が話していた？ | 電話対応をAIに任せても、人間は必要？ | AI電話でも、難しい場面は人が支える？ | AIの電話代行を人間が補うって不思議じゃない？ | AIに任せた電話、実は人間が話していたら？ | AIに任せた電話、実は誰が話していたと思う？ | AIに任せた電話を、実は人間が聞いていたら？ |
| travel_bag | 旅行バッグ満員事件、犯人は服ではなく「服が連れてきた空気」 | 旅行の荷物は、なぜ毎回バッグいっぱいになる？ | 旅行の荷物は、減らすより圧縮して運ぶ？ | 荷物を減らせなくても、旅のストレスは減らせる？ | 旅行荷物、減らすより圧縮するのが人気なのはなぜ？ | 服を何枚か入れただけで満員になるバッグ、実は空気も一緒に詰めてる？ | バッグを満員にしていたのは、服ではなく空気かも？ | 旅行バッグを満員にした犯人、服が連れてきた空気かも？ |

## 表2: used_angle_ja

| Article | Model | used_angle_ja |
|---|---|---|
| sewer | luna | 町全体の大きな水処理の仕組みを、家ごとの小さな洗濯機に分けるたとえを使いました。 |
| sewer | terra | 古くなった下水道を延命する代わりに、家の近くで水を処理する仕組みへ変えるという見方を使いました。 |
| sewer | sol | 町全体の下水処理を巨大な洗濯機、合併浄化槽を家ごとの小さな洗濯機にたとえた場面を使いました。 |
| ai_phone | luna | AIがひとりで演じているように見える電話の裏で、人間の契約スタッフが代役を務めていた場面を使いました。 |
| ai_phone | terra | AI電話代行の試験で、一部の通話を人間の契約スタッフが担当していたという舞台裏を使いました。 |
| ai_phone | sol | AI電話代行の舞台裏で、人間の契約スタッフが通話を担当していた場面を使いました。 |
| travel_bag | luna | 服のふくらみの中にある空気を、服が連れてきた同伴者として捉える見方を使いました。 |
| travel_bag | terra | 服そのものではなく、服のふくらみに含まれる空気がバッグ内のスペースを占めているという見方を使いました。 |
| travel_bag | sol | 服そのものではなく、服のふくらみに含まれる空気が場所を取っているという見方を使いました。 |

## 表3: 機械統計(観察事実のみ)

| Article | Model | 文字数 | ？終端 | でしょうか含有 | R2タイトル一致率 | Fact機械一致 |
|---|---|---|---|---|---|---|
| sewer | luna | 23 | True | False | 0.163 | True |
| sewer | terra | 20 | True | False | 0.304 | True |
| sewer | sol | 27 | True | False | 0.151 | True |
| ai_phone | luna | 21 | True | False | 0.346 | True |
| ai_phone | terra | 22 | True | False | 0.264 | True |
| ai_phone | sol | 22 | True | False | 0.34 | True |
| travel_bag | luna | 33 | True | False | 0.226 | True |
| travel_bag | terra | 24 | True | False | 0.491 | True |
| travel_bag | sol | 26 | True | False | 0.655 | True |
