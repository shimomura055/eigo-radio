# Topic Selection User Evaluation Dataset

機械参照用: `docs/pm/topic_selection_user_eval_dataset.json`(同内容)。

## metadata

```
evaluator: User(shimomura055)
scale: 1-10
threshold_note: 5以上=現時点では採用可能相当
evaluation_target: Topic + 現在付いているHook の総合評価(素材だけの評価ではない)
caveat: 5未満でもHookの付け方によって点数が上がる可能性がある。score<5→当該Topic類型を検索除外、のような機械利用は禁止
usage: Search教師データとして使用可(素材が弱い/Hookが弱い/両方弱いを区別する教師データ)
production_status: Production scoring ruleとしては未承認(NOT_APPROVED)
prompt_injection: Hook生成・Selection Promptへ本datasetの点数・Hook・Reference Hookを直接投入することは禁止(汚染防止)
management_id: NEWS-HOOK-MODEL-COMPARISON-01(保存時)
source_management_ids:
  dataset_r: TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02(Reference 20)
  dataset_a: NEWS-HOOK-MODEL-COMPARISON-01
  dataset_b: NEWS-HOOK-MODEL-COMPARISON-01
recorded_at: 2026-09-24
production_selection_rule_warning: このUser Scoreから新しいProduction Selection Rule(「商品記事除外」「芸能除外」「5点以下カテゴリ検索除外」等)を自動生成することを禁止する。あくまで次のSearch Trial設計に使うEvidence。
```

## Dataset R: Reference 20件(ChatGPT作成)

| item_no | topic_ja | hook_ja | user_score | source_trial |
|---|---|---|---|---|
| 1 | MetaのAI「Muse」が電話代行の一部を人間スタッフに担当させる実験 | AIに店への電話を頼んだら、裏では人間が話していた？ | 8 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 2 | AI企業トップが国連安保理で「AIが人間の制御を超える可能性」を議論 | AIの危険を話し合う場所が、ついに国連安保理になったのはなぜ？ | 4 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 3 | 米中首脳会談でAI・貿易・安全保障が主要テーマに | アメリカと中国は、なぜAIで"別々の世界"を作ろうとしている？ | 7 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 4 | AIが癌治療を大きく変えるという期待と医師側の慎重論 | AIは本当に"癌を治す"ところまで来ている？ | 8 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 5 | 世界初、宇宙飛行中に診断用X線撮影に成功 | 宇宙で骨折したら、どうやって病院に行く？ | 5 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 6 | WHOが避妊方法について新推奨、将来の男性用避妊法にも言及 | 避妊は、なぜ今も女性側の負担が大きい？ | 3 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 7 | 日本で「秋になっていびきが増えた」と答える人が多い調査 | 秋になると、いびきが増える人がいるのはなぜ？ | 6 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 8 | 日本で「睡眠障害」が診療科名として標榜可能に | 眠れないだけで、病院に行っていいの？ | 7 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 9 | 大谷翔平が負傷者リストから約2週間ぶりに復帰予定 | トップ選手は"完全に治る"まで待たずに、どう復帰を決める？ | 6 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 10 | Threadsで「20年使えるカレンダー」を18年後に見返した投稿が14万回超表示 | 20年前の"未来"を今見ると、何が一番変わって見える？ | 7 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 11 | ローソンの「おかず1種類だけ」一点突破弁当がSNSで賛否 | おかずが1種類しかない弁当は、"貧しい"のか"合理的"なのか？ | 7 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 12 | 無印良品の小型保冷バッグがSNS・口コミで人気 | なぜ今、"小さい保冷バッグ"が欲しい人が増えている？ | 5 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 13 | 旅行用の圧縮ポーチが人気 | 旅行の荷物は、なぜ毎回バッグいっぱいになる？ | 7 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 14 | 帝国ホテルの高級感あるエコバッグが話題 | ただのエコバッグに、人はなぜ"高級感"を求める？ | 8 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 15 | XのAI界隈で「Jev」という意思決定特化型AIが急速に話題化 | AIは"大きく賢くする"より、仕事を一つに絞った方が速い？ | 5 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 16 | 日本香堂が日本の香文化ベースの香水をパリで世界展開 | 日本の"お香"は、なぜ海外では香水になる？ | 6 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 17 | ゲーム『アニモ』スマホ版配信開始、クロスプレイ対応 | ゲームはもう"どのゲーム機を持っているか"を気にしなくなる？ | 4 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 18 | 米倉涼子が映画イベントで「指パッチン」のギネス記録 | "指パッチン"にも世界記録がある？ | 4 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 19 | 旅行業界で「安さだけでは選ばれない」消費行動変化を議論 | 旅行は安いほどいい――ではなくなっている？ | 5 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |
| 20 | 職場などに人工クラゲ水槽を置くサービス | オフィスに"偽物のクラゲ"を置くと、本当に癒やされる？ | 7 | TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Reference 20) |

## Dataset A: ChatGPT API Search 20件

| item_no | topic_ja | hook_ja | user_score | generated_by |
|---|---|---|---|---|
| 1 | AIに何を食べるか相談する人が増え、スナック選びまで変化 | 今日のおやつまでAIに決めてもらう時代が来ている？ | 6 | ChatGPT API Search |
| 2 | MetaのAIエージェント「Muse」が買い物・旅行予約などを代行 | 検索する代わりに、AIに「全部やって」と頼む時代になる？ | 5 | ChatGPT API Search |
| 3 | カメラを外したスマートグラスをMetaが投入 | スマートグラスから「カメラ」を外したら、逆に売れる？ | 5 | ChatGPT API Search |
| 4 | AIエージェントが豪州政府サイトへ不正アクセス | AIが自分で政府サイトに侵入する時代、誰が責任を取る？ | 5 | ChatGPT API Search |
| 5 | ペットの気持ちをAIで推測する首輪型デバイス | 犬や猫の「今の気分」、AIなら本当に分かる？ | 6 | ChatGPT API Search |
| 6 | 秋になっていびきが増えた人が多いという調査 | 秋になると、いびきが増える人がいるのはなぜ？ | 5 | ChatGPT API Search |
| 7 | おにぎりブーム沈静化後も売れる店の仕掛け | ただのおにぎりなのに、「わざわざ買いに行く店」は何が違う？ | 5 | ChatGPT API Search |
| 8 | 国道を題材にしたトレーディングカードが約10分で完売 | 国道に「レアカード」を作ったら、10分で売り切れた？ | 4 | ChatGPT API Search |
| 9 | 会社の水・ティッシュを持ち帰る社員への対応 | 会社のティッシュを家に持ち帰るのは、どこから「盗み」になる？ | 7 | ChatGPT API Search |
| 10 | 若手とベテランの間で職場の距離が広がる問題 | 職場で「仲良くしない若者」は、本当に冷たいのか？ | 4 | ChatGPT API Search |
| 11 | メールの返信忘れをAIで防ぐ活用法 | メールを返し忘れる人ほど、AIに任せた方がいい？ | 4 | ChatGPT API Search |
| 12 | JCOM障害でネットだけでなくサポート窓口もつながりにくく | ネットが落ちたとき、「問い合わせ先までつながらない」のはなぜ？ | 4 | ChatGPT API Search |
| 13 | Appleがロンドンにライブ会場を開設 | Appleはなぜ、音楽配信会社なのに「ライブ会場」まで作る？ | 3 | ChatGPT API Search |
| 14 | アジア大会の競歩コースにカラス約1000羽、鷹匠を投入 | 競歩大会を守るために、1000羽のカラスと「タカ」が戦う？ | 5 | ChatGPT API Search |
| 15 | クマが海を泳いで無人島へ上陸 | クマは海を泳いで、島まで渡れる？ | 3 | ChatGPT API Search |
| 16 | 「ダチョウが逃げた」と通報、実際は体長約2mのエミュー | 街に「ダチョウ」が出たと思ったら、別の鳥だった？ | 4 | ChatGPT API Search |
| 17 | チーターの赤ちゃんを見るため約1700人が行列 | 赤ちゃんチーターを見るために、なぜ1700人も並ぶ？ | 4 | ChatGPT API Search |
| 18 | 台風後に観光客が一気に戻る「リベンジ観光」 | 雨で潰れた休日、人は次の日に「取り返すように」出かける？ | 3 | ChatGPT API Search |
| 19 | カラスの巣は枝だけでなくハンガーなども利用 | カラスの巣をあまり見かけないのは、どこに隠しているから？ | 3 | ChatGPT API Search |
| 20 | 中国の若者で交際・恋愛を避ける傾向 | 恋愛まで「コスパが悪い」と思う若者が増えている？ | 5 | ChatGPT API Search |

## Dataset B: Luna最新17件

| item_no | topic_ja | hook_ja | user_score | generated_by |
|---|---|---|---|---|
| 1 | 立川談春、なりすまし投資勧誘に注意喚起 | 本人に見える投資勧誘、信じる前に確認を——立川談春が「無視して」と呼びかけた理由。 | 3 | Luna |
| 2 | 9月も汗ばむ暑さ、10月に秋の空気 | 9月はまだ半袖、10月には秋服？衣替えの正解が「カレンダー通り」にならない理由。 | 4 | Luna |
| 3 | 防災グッズ「さりげなく備える」売上1.3倍 | 防災グッズは隠す時代から「普段使い」へ？売れ行きが伸びる用品の共通点。 | 4 | Luna |
| 4 | 玄関ドアに100均フック収納 | 玄関ドアが収納場所に変わる？100均フックで「置き場所がない」を解決する4つの使い方。 | 2 | Luna |
| 5 | 丸亀製麺10/1限定半額 | 丸亀製麺の釜揚げうどんが190円から——10月1日だけ半額になる理由。 | 1 | Luna |
| 6 | AIで鋼製シャフト疲労寿命予測 | 40分かかる解析を約15秒に？ | 2 | Luna |
| 7 | 2000体エージェント「Fuga v2」 | AIを1体ではなく2000体動かす？ | 3 | Luna |
| 8 | 100均マグネットでミニ紙袋収納 | 捨てるはずのミニ紙袋が壁収納に？ | 2 | Luna |
| 9 | コールマン小さめバッグがSNSで「ちょうどいい」 | リュックほど大げさでなく、水筒は入る——「小さめバッグ」がちょうどいい理由。 | 4 | Luna |
| 10 | シャインマスカットはいつまで買える？ | シャインマスカットは、秋ならいつでも旬とは限らない？ | 2 | Luna |
| 11 | ローソン今週の新商品・一点突破弁当等 | 肉に振り切った弁当から海鮮焼そばまで——今週は「全部盛り」が目立つ。 | 3 | Luna |
| 12 | トイレに木板DIYでスマホ置き場 | トイレの「ちょい置き」を5分DIY | 2 | Luna |
| 13 | 井上和香、インフルは大人の方がつらい | 子どもより大人のほうがつらい？インフルエンザから回復して感じた「ダメージ」。 | 3 | Luna |
| 14 | ローソン先行・森永こだわり食感 | 今日は「カリッ」、別の日は「ザクザク」 | 3 | Luna |
| 15 | 明治ミルクチョコのエコバッグ付録 | 明治のチョコが食べ物ではなく付録に？ | 3 | Luna |
| 16 | Driver Booster 14 | ゲームが起動しない原因を「DLL不足」から直す | 1 | Luna |
| 17 | HDMI 2.2「Ultra 96」国内初 | 映像ケーブルが最大96Gbps対応へ | 1 | Luna |

## 集計(観察事実のみ。傾向解釈・除外ルール化はしない)

| dataset | n | mean_score | count_score>=5 |
|---|---|---|---|
| R(Reference20) | 20 | 5.95 | 16 |
| A(ChatGPT API Search20) | 20 | 4.5 | 10 |
| B(Luna最新17) | 17 | 2.53 | 0 |

