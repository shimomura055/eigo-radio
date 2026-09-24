# structure_map.md — Story structure preservation(目視、段落単位)

## 下水道 (A-1 Advanced → A-2 Standard)

| # | Advanced(A-1)段落要旨 | Standard(A-2)対応段落 | Reveal/比喩/Endingか | 同一位置 |
|---|---|---|---|---|
| 1 | Title: “Merger”? Not Towns, but Household Wastewater | 同一Title(一字一句同じ) | Hookの一部 | ○ |
| 2 | Opening: "merger"という語から町の合併を連想させ、実は家庭排水(トイレ・台所・風呂の水)の統合だと反転 | 同一構成、"not municipalities"→"not towns"のみ語彙差 | Opening Hook/Reveal | ○ |
| 3 | 一部自治体が老朽下水道を合併浄化槽へ切替検討中(全廃ではない、地域選択) | 同一構成、"municipalities"→"municipalities, or town governments"と説明語追加(A2向け語彙補助) | Context | ○ |
| 4 | 中心比喩1: 下水道=町の地下の見えない大動脈 | 同一位置・同一比喩(artery)、構文簡略化のみ | 中心比喩1 | ○ |
| 5 | 問題: 管の老朽化で発見・修理が困難、規模も大きくなりがち | 同一構成、"Since..."の従属節を"...so..."の等位接続へ分割 | 山場の前段 | ○ |
| 6 | 解決策: 合併浄化槽(家近くの小施設、トイレ+台所+風呂水を処理) | 同一構成、同一Fact | 山場 | ○ |
| 7 | 中心比喩2: 町に1台の巨大洗濯機 vs 家ごとの小さな洗濯機 | 同一位置・同一比喩、一字一句ほぼ同じ | 中心比喩2(面白さの核) | ○ |
| 8 | 留保: 浄化槽も設置・点検・清掃が必要、暮らしの裏側が変わる | 同一構成、同一Fact | 留保情報 | ○ |
| 9 | Ending: 設備を大きくしなくても便利さは守れる、下水道の未来は身近な場所へ | 同一構成、同一結論、"aging"→"old"のみ語彙差 | Ending | ○ |

- Reveal(“合併”＝家庭排水という反転)・中心比喩1(大動脈)・中心比喩2(洗濯機)・Endingの意味、いずれも段落位置・順序ともにAdvancedと完全一致。
- 要約化・Fact削除・新Fact追加は検出されず(fact_diff_machine.json sewer_A1_to_A2: numbers_missing/added=[]、proper_nouns差分は文頭大文字の誤検出["Since"消失は従属節→等位接続への構文変化によるもの、"We"追加は命令文→"We turn on..."への主語補完によるもの。いずれもFactではなく構文簡略化])。
- Story順序変更なし、段落の統合・分割もなし(9段落→9段落、1:1対応)。

## Meta AI Call (Advanced Baseline → B-1 Standard)

| # | Advanced段落要旨 | Standard(B-1)対応段落 | Reveal/比喩/Endingか | 同一位置 |
|---|---|---|---|---|
| 1 | Title: “Hello, I’m AI” — A Human Was Behind the AI Phone Call | 同一Title(一字一句同じ、改変禁止Baseline通り) | Hookの一部 | ○ |
| 2 | Opening: AIが電話を代行する便利な未来のサービス、というMetaの構想 | 同一構成、"convenient"→"useful"、"only needs to explain"→"only has to say"の語彙簡略化のみ | Opening Hook | ○ |
| 3 | 主役紹介: Muse(Metaの個人向けAIエージェント) | 同一構成、Fact同一。**"The lead role was Muse"→"The main part was Muse"**へ変更 | 主役紹介(舞台メタファーの一部) | ○(位置は同一だが下記注記あり) |
| 4 | 転換: 舞台裏をのぞくと意外な光景 | 一字一句同一 | Revealへの導入 | ○ |
| 5 | Reveal: 社内試験で人間の契約スタッフ(”human concierges”)が通話の一部を担当 | 一字一句同一("some parts of the calls"含め完全一致) | Reveal(核心Fact) | ○ |
| 6 | 看板は"AI電話代行"だが実は人間が担当、代役(understudy)の枠組み | 同一構成、"out front"→"outside"のみ語彙差 | Reveal補強/中心比喩の枠組み | ○ |
| 7 | 中心比喩: ピアノの中に隠れた演奏者 | 一字一句同一 | 中心比喩(面白さの核) | ○ |
| 8 | 人間が手伝うこと自体は自然、というクッション | 同一構成、"fill in the parts"→"do the parts"の語彙差 | 留保情報 | ○ |
| 9 | プライバシー懸念(後半の必要情報として) | 同一Fact、1文を2文に分割("raised privacy concerns, including..."→"raised privacy concerns. They worried that...") | Privacy(後半必要情報) | ○ |
| 10 | Reuters確認・Meta幹部が機能を一時停止 | 一字一句同一 | 事実確認 | ○ |
| 11 | Ending: 舞台の上/幕の後ろ、誰が話し誰が隠れているか | 一字一句同一 | Ending | ○ |

- Reveal(P5)・中心比喩(P7)・Endingの意味(P11)は、段落位置・語順ともにAdvancedと完全一致。要約化・Fact削除・新Fact追加は検出されず(fact_diff_machine.json meta_advanced_to_B1: numbers_missing/added=[]、proper_nouns差分は"They"/"This"の文頭大文字誤検出のみでFactではない)。
- **注記(比喩の精度に関する軽微な観察、Story崩れには該当しない)**: P3で"The lead role was Muse"(主役=Museという明確な舞台メタファー語)が"The main part was Muse"へ変更されている。"part"は演劇の役を指す語としても一般的に使われる(例: "play a part")ため、舞台メタファーの枠組み自体は維持されているが、"lead role"ほど明示的に「主役」を指す語ではない。これはStory構造・Reveal・Endingの位置には影響しないため本Trialの禁止事項(比喩削除・Story順序変更)には該当しないと判断したが、事実として記録する。

## Story崩れ判定

- 下水道・Meta ともに Reveal / 中心比喩 / Ending いずれも消失・順序変更・要約化は検出されなかった。STOP条件(「A2化するとStoryが大幅に崩れる」)には該当しない。
- ただしlevel_metrics.md(word count/avg sentence length/subordinator比率)が示す通り、両記事ともAdvanced→Standardの変化幅は小さく(下水道: avg words/sent 13.62→13.48、subordinator/100w 3.11→2.75。Meta: avg words/sent 13.2→12.5、subordinator/100w 4.55→4.31)、Story保持を優先した結果、簡略化の程度が浅い可能性がある。これはStory崩れの逆側の懸念(簡略化不足)であり、機械指標のみでは判断できないため、事実として報告する(§15 未解決)。
