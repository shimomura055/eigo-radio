# -*- coding: utf-8 -*-
"""検証ケース(probe)54件の生成スクリプト(委任_02でM6反映: 48件->54件)。出力=kpg04_probes.json。API 0。
種別: ARG_PERSON_THING / FIXED_PRONOUN / SENSE_SHIFT / OBJECT_OMIT_OK / MODIFIER_DROPPABLE / MODIFIER_ESSENTIAL / ALREADY_CORRECT / FREE_COMBINATION(各6件)
      + SLOT_SENSE(someone/somethingで語義が変わる型。委任_02 M6で6件追加)。GEN対象=FREE_COMBINATION以外の48件。
既知の失敗2例(hear it out / take points away from)とは語句を変えた同型の例を含む(過適合の検出用)。ok=許容形、ng=既知のNG形(どちらでもなければREVIEW=実読)。
M5: 訳の採点用に gloss_ok_kw(正しい語義のキーワード) / gloss_bad_kw(誤語義のキーワード) / gloss_mod_kw(削った修飾語の意味が訳に残るか。mod_wordが形に無い時のみ適用)を事前登録、
    評価器の感度確認用に ok_gloss / ng_gloss(正しい訳/誤った訳)、誤理由注入版(P0i)用に wrong_reason_ja(上流の誤った語義の塊の理由)を持つ。
M6: someone/somethingで語義が変わる型を追加、OO2はtake up somethingのみ許容、実在しないME誤り形をもっともらしい罠に差替え、AP2の競合確認(note)。"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
P = []


def add(id, type, span, sentence, context, ok, ng, note):
    P.append(dict(id=id, type=type, span=span, sentence=sentence, context=context, ok=ok, ng=ng, note=note))


# AP: 人/物の取違え(見出し形の標準的な目的語タイプ)
add("AP1", "ARG_PERSON_THING", "hear her out", "The coach asked the board to hear her out before making a decision.", "The coach was upset about the team's loss. The coach asked the board to hear her out before making a decision.", ["hear someone out"], ["hear something out"], "目的語が人")
add("AP2", "ARG_PERSON_THING", "see it off", "The whole town came to see it off.", "The old ship was leaving the port for the last time. The whole town came to see it off.", ["see someone off"], ["see something off"],
    "擬人化された物(船)。見出し標準は人=見送る(see someone off)。競合確認: see something off=撃退する/退ける(別語義)も辞書にあるが、本文は『見送る』語義なのでsomeone側が本文語義と一致。要Fable確認項目")
add("AP3", "ARG_PERSON_THING", "worked it out", "They worked it out after a long talk.", "The two neighbors had argued about the fence for years. They worked it out after a long talk.", ["work something out", "work it out"], ["work someone out"], "解決する(it=問題・物事)。work someone outは『(人)を理解する』の別語義。旧AP3(sit through)は末尾slotが表示規約で除去されるため人/物の別を測れず差替え(委任_02)")
add("AP4", "ARG_PERSON_THING", "talked him into joining", "She talked him into joining the club.", "Tom had never liked sports. She talked him into joining the club.", ["talk someone into"], ["talk something into"], "人")
add("AP5", "ARG_PERSON_THING", "let him down", "She felt she had let him down.", "The project failed at the last minute. She felt she had let him down.", ["let someone down"], ["let something down"], "人")
add("AP6", "ARG_PERSON_THING", "shake it off", "After the bad news, she tried to shake it off.", "The test results were worse than expected. After the bad news, she tried to shake it off.", ["shake something off"], ["shake someone off"], "物・事を取る見出し")
# PF: 慣用表現に固定されたit
add("PF1", "FIXED_PRONOUN", "took it out on", "She took it out on her little brother.", "She had a terrible day at work. She took it out on her little brother.", ["take it out on"], ["take something out on"], "固定のit")
add("PF2", "FIXED_PRONOUN", "make it up to", "I will make it up to you.", "I missed your birthday party. I will make it up to you.", ["make it up to"], ["make something up to"], "固定のit")
add("PF3", "FIXED_PRONOUN", "has it in for", "She always has it in for new employees.", "The office is tense these days. She always has it in for new employees.", ["have it in for"], ["have something in for"], "固定のit")
add("PF4", "FIXED_PRONOUN", "called it a day", "We were tired, so we called it a day.", "We had been painting the fence since morning. We were tired, so we called it a day.", ["call it a day"], ["call something a day"], "固定のit")
add("PF5", "FIXED_PRONOUN", "going to lose it", "I think he is going to lose it.", "The noise had been going on for hours. I think he is going to lose it.", ["lose it"], ["lose something"], "固定のit(=我を忘れる)")
add("PF6", "FIXED_PRONOUN", "go for it", "Just go for it!", "You have trained for months. Just go for it!", ["go for it"], ["go for something"], "固定のit(go for somethingは別語義)")
# SS: 目的語・前置詞・目的語名詞の除去で語義が変わる
add("SS1", "SENSE_SHIFT", "took two points away from", "The judges took two points away from the team for being late.", "The contest had strict rules. The judges took two points away from the team for being late.", ["take something away from"], ["take away from"], "減点する。take away from(損なう)は別見出し")
add("SS2", "SENSE_SHIFT", "took up space", "Her old books took up space on the shelf.", "The shelf was full. Her old books took up space on the shelf.", ["take up space"], ["take up"], "take upは語義が不定(始める等)になる")
add("SS3", "SENSE_SHIFT", "came to terms with", "He finally came to terms with the loss.", "It took him many months. He finally came to terms with the loss.", ["come to terms with"], ["come to terms"], "withを落とすと別語義(合意に達する)")
add("SS4", "SENSE_SHIFT", "looked down on her neighbors", "She looked down on her neighbors.", "Nobody liked her attitude. She looked down on her neighbors.", ["look down on"], ["look down"], "onを落とすと別語義")
add("SS5", "SENSE_SHIFT", "picked up the pace", "The runners picked up the pace near the end.", "The race was slow at first. The runners picked up the pace near the end.", ["pick up the pace"], ["pick up"], "paceを落とすと語義が不定")
add("SS6", "SENSE_SHIFT", "took the edge off", "A quick snack took the edge off her hunger.", "She had skipped lunch. A quick snack took the edge off her hunger.", ["take the edge off"], ["take off", "take something off"], "慣用表現")
# OO: 目的語を省略しても同語義(許容)。OO2のみ『take up something』だけ許容(裸のtake upは語義不定=M6)
add("OO1", "OBJECT_OMIT_OK", "carried out the plan", "They carried out the plan last week.", "The team had worked on it for months. They carried out the plan last week.", ["carry out", "carry something out"], [], "")
add("OO2", "OBJECT_OMIT_OK", "take up painting", "He decided to take up painting last spring.", "He wanted a new hobby. He decided to take up painting last spring.", ["take up something", "take something up", "take up painting"], ["take up"], "趣味を始める語義。裸のtake upは語義が不定(占める/始める/引き受ける)になるため不可。末尾slotは表示規約(strip_trailing_slot)で必ず除去されるので『take up something』は生成不能=本文の形を保つ(take up painting)のが安全側の正解(委任_02 M6の趣旨を規約に合わせて明確化)")
add("OO3", "OBJECT_OMIT_OK", "narrow down the options", "We need to narrow down the options.", "There are too many choices. We need to narrow down the options.", ["narrow down", "narrow something down"], [], "")
add("OO4", "OBJECT_OMIT_OK", "tightened up the rules", "The school tightened up the rules this year.", "There had been many problems. The school tightened up the rules this year.", ["tighten up", "tighten something up"], [], "")
add("OO5", "OBJECT_OMIT_OK", "looked into the matter", "He looked into the matter carefully.", "A customer had complained. He looked into the matter carefully.", ["look into", "look into something"], [], "")
add("OO6", "OBJECT_OMIT_OK", "sorted out the problem", "They sorted out the problem quickly.", "The machine had stopped working. They sorted out the problem quickly.", ["sort out", "sort something out"], [], "")
# MO: 修飾語を削ってよい
add("MO1", "MODIFIER_DROPPABLE", "set a lower limit", "The company set a lower limit on spending.", "Costs had grown too fast. The company set a lower limit on spending.", ["set a limit", "set a lower limit"], [], "ユーザー指定の許容例")
add("MO2", "MODIFIER_DROPPABLE", "took an unexpected turn", "The story took an unexpected turn.", "The novel began as a love story. The story took an unexpected turn.", ["take a turn", "take an unexpected turn"], [], "ユーザー指定の許容例")
add("MO3", "MODIFIER_DROPPABLE", "took good care of", "She took good care of the garden.", "The garden had been neglected for years. She took good care of the garden.", ["take care of", "take good care of"], [], "ユーザー指定の許容例")
add("MO4", "MODIFIER_DROPPABLE", "made a quick decision", "He made a quick decision.", "There was no time to think. He made a quick decision.", ["make a decision", "make a quick decision"], [], "")
add("MO5", "MODIFIER_DROPPABLE", "paid close attention to", "The teacher paid close attention to the details.", "The exam was coming soon. The teacher paid close attention to the details.", ["pay attention to", "pay close attention to"], [], "")
add("MO6", "MODIFIER_DROPPABLE", "played a key role in", "She played a key role in the project.", "The project was a success. She played a key role in the project.", ["play a role in", "play a key role in"], [], "")
# ME: 修飾語を削ると意味が変わる(委任_02 M6: ME2/ME4/ME5を、実際に生成されうるもっともらしい誤り形(修飾語を落として別語義)へ差替え)
add("ME1", "MODIFIER_ESSENTIAL", "broke new ground in", "The team broke new ground in cancer research.", "The results surprised many doctors. The team broke new ground in cancer research.", ["break new ground in", "break new ground"], ["break ground in", "break ground"], "newを落とすと別語義(着工)")
add("ME2", "MODIFIER_ESSENTIAL", "made a big deal of", "She made a big deal of the small mistake.", "Everyone else had already forgotten it. She made a big deal of the small mistake.", ["make a big deal of", "make a big deal out of"], ["make a deal of", "make a deal"], "bigを落とすと『取引する』系の別語義になる")
add("ME3", "MODIFIER_ESSENTIAL", "turned a blind eye to", "The manager turned a blind eye to the problem.", "Everyone knew about it. The manager turned a blind eye to the problem.", ["turn a blind eye to"], ["turn an eye to", "turn eye to"], "")
add("ME4", "MODIFIER_ESSENTIAL", "give her a big hand", "The host asked the crowd to give her a big hand.", "The singer had just finished her last song. The host asked the crowd to give her a big hand.", ["give someone a big hand"], ["give someone a hand"], "bigを落とすと『手伝う』の別語義(a big hand=拍手)")
add("ME5", "MODIFIER_ESSENTIAL", "took a back seat to", "Safety took a back seat to speed at the factory.", "The managers wanted faster output. Safety took a back seat to speed at the factory.", ["take a back seat to", "take a back seat"], ["take a seat", "take a seat to"], "backを落とすと別語義(席に着く)")
add("ME6", "MODIFIER_ESSENTIAL", "in hot water", "The mayor is in hot water over the new tax.", "People are angry in the city. The mayor is in hot water over the new tax.", ["in hot water"], ["in water"], "")
# OK: すでに正しく一般化できる(壊さないことの確認)
add("OK1", "ALREADY_CORRECT", "walked me through the steps", "She walked me through the steps.", "I had never used the machine. She walked me through the steps.", ["walk someone through"], ["walk something through"], "")
add("OK2", "ALREADY_CORRECT", "set the numbers aside", "He set the numbers aside for now.", "The report was almost finished. He set the numbers aside for now.", ["set something aside"], [], "")
add("OK3", "ALREADY_CORRECT", "keep the costs down", "We will keep the costs down this year.", "Prices are rising everywhere. We will keep the costs down this year.", ["keep something down"], [], "")
add("OK4", "ALREADY_CORRECT", "turned the usual steps around", "The cook turned the usual steps around.", "The recipe was old. The cook turned the usual steps around.", ["turn something around"], [], "")
add("OK5", "ALREADY_CORRECT", "in the event of a delay", "In the event of a delay, please call us.", "Trains are sometimes late. In the event of a delay, please call us.", ["in the event of"], [], "")
add("OK6", "ALREADY_CORRECT", "break the ice", "A small joke can break the ice at a party.", "Nobody was talking to anyone. A small joke can break the ice at a party.", ["break the ice"], [], "")
# SO: someone/somethingで語義が変わる型(委任_02 M6追加)。本文語義に合う方だけがok
add("SO1", "SLOT_SENSE", "put up our guests", "We put up our guests in the spare room.", "Friends came to visit for the weekend. We put up our guests in the spare room.", ["put someone up"], ["put something up"], "泊める(人)。put something up=建てる・掲げる")
add("SO2", "SLOT_SENSE", "brought up her children", "She brought up her children in a small village.", "She wanted a quiet life. She brought up her children in a small village.", ["bring someone up"], ["bring something up"], "育てる(人)。bring something up=話題に出す")
add("SO3", "SLOT_SENSE", "see the project through", "They promised to see the project through.", "The work was hard and slow. They promised to see the project through.", ["see something through"], ["see someone through"], "やり遂げる(物・事)。see someone through=人を支える")
add("SO4", "SLOT_SENSE", "see her through the illness", "Her friends promised to see her through the illness.", "The treatment lasted a year. Her friends promised to see her through the illness.", ["see someone through"], ["see something through"], "(人)を支えて乗り切らせる。see something through=やり遂げる")
add("SO5", "SLOT_SENSE", "put up the tent", "They put up the tent before dark.", "The camp site was empty. They put up the tent before dark.", ["put something up"], ["put someone up"], "建てる(物)。put someone up=泊める")
add("SO6", "SLOT_SENSE", "bring up the issue", "She decided to bring up the issue at the meeting.", "Nobody wanted to talk about money. She decided to bring up the issue at the meeting.", ["bring something up"], ["bring someone up"], "話題に出す(事)。bring someone up=育てる")
# FC: 自由な組合せ(選定段で落とされるべき。SEL probe用。GEN対象外)
for i, (sp, se, cx) in enumerate([
        ("wiped the kitchen table", "She wiped the kitchen table with a damp cloth.", "The meal was over. She wiped the kitchen table with a damp cloth."),
        ("wrote a short report", "He wrote a short report on Friday.", "The boss wanted a summary. He wrote a short report on Friday."),
        ("opened the red door", "They opened the red door slowly.", "The hallway was dark. They opened the red door slowly."),
        ("a faint signal", "The lab measured a faint signal.", "The instrument was very sensitive. The lab measured a faint signal."),
        ("a very small number", "Only a very small number of people came.", "The weather was bad. Only a very small number of people came."),
        ("kept a notebook in the drawer", "She kept a notebook in the drawer.", "Her desk was tidy. She kept a notebook in the drawer.")], 1):
    add(f"FC{i}", "FREE_COMBINATION", sp, se, cx, [], [], "選定段(SEL)で落とされるべき(GEN対象外)")

# ---- M5: 事前登録メタ(結果を見る前に固定)。ok_gloss/ng_gloss=評価器感度確認用の正しい訳/誤った訳。gloss_ok_kw/gloss_bad_kw=訳の決定論採点(any-of正規表現)。wrong_reason_ja=P0i(誤理由注入)
META = {
    "AP1": dict(ok_gloss="(人)の言い分を最後まで聞く", ng_gloss="(人)の言い分を最後まで聞く", ok_kw=["最後まで", "言い分", "話を聞"], bad_kw=[]),
    "AP2": dict(ok_gloss="(人)を見送る", ng_gloss="(物)を撃退する・退ける", ok_kw=["見送"], bad_kw=["撃退", "追い払", "退け"]),
    "AP3": dict(ok_gloss="〜を解決する・うまく片付ける", ng_gloss="(人)を理解する", ok_kw=["解決", "片付", "決着", "うまく", "打開", "折り合"], bad_kw=["理解", "見抜"]),
    "AP4": dict(ok_gloss="(人)を説得して〜させる", ng_gloss="(物)を説得して〜させる", ok_kw=["説得", "させる", "丸め込", "仕向"], bad_kw=["話し合", "相談"]),
    "AP5": dict(ok_gloss="(人)を失望させる・期待を裏切る", ng_gloss="(物)を失望させる", ok_kw=["失望", "がっかり", "裏切", "期待に"], bad_kw=["降ろ", "下ろ"]),
    "AP6": dict(ok_gloss="〜を振り払う・気にしないようにする", ng_gloss="(人)を振り払う", ok_kw=["振り払", "払いのけ", "振り切", "気にしない", "忘れ", "乗り越"], bad_kw=["揺れ", "揺ら"]),
    "PF1": dict(ok_gloss="〜に八つ当たりする", ng_gloss="(物)を〜に持ち出す", ok_kw=["八つ当たり", "当たり散ら", "やつあたり"], bad_kw=["取り出", "外に出"]),
    "PF2": dict(ok_gloss="〜に埋め合わせをする", ng_gloss="(物)を〜にでっち上げる", ok_kw=["埋め合わせ", "償", "穴埋め"], bad_kw=["作り上げ", "でっち上げ"]),
    "PF3": dict(ok_gloss="〜を目の敵にする・恨みを持つ", ng_gloss="(物)を〜に持っている", ok_kw=["恨", "目の敵", "敵意", "目をつけ", "いじめ", "嫌"], bad_kw=[]),
    "PF4": dict(ok_gloss="今日はここまでにする・切り上げる", ng_gloss="(物)を一日と呼ぶ", ok_kw=["切り上げ", "終わり", "やめ", "打ち切", "ここまで", "終え"], bad_kw=[]),
    "PF5": dict(ok_gloss="我を忘れる・キレる", ng_gloss="(物)を失くす", ok_kw=["我を忘れ", "キレ", "取り乱", "かんしゃく", "冷静さを失", "切れ"], bad_kw=["失くす", "なくす", "紛失"]),
    "PF6": dict(ok_gloss="思い切ってやってみる・挑戦する", ng_gloss="(物)を狙う・選ぶ", ok_kw=["思い切って", "挑戦", "やってみ", "頑張", "全力", "試し"], bad_kw=[]),
    "SS1": dict(ok_gloss="〜から…を差し引く・減点する", ng_gloss="〜の価値や効果を損なう", ok_kw=["差し引", "減点", "引く", "引き"], bad_kw=["損な", "価値", "効果", "台無し"]),
    "SS2": dict(ok_gloss="場所を取る・占める", ng_gloss="〜を始める・引き受ける", ok_kw=["場所", "スペース", "占め", "取る", "ふさ"], bad_kw=["始め", "開始", "引き受"]),
    "SS3": dict(ok_gloss="〜を受け入れる・折り合いをつける", ng_gloss="合意に達する", ok_kw=["受け入れ", "折り合", "向き合", "納得", "整理"], bad_kw=["合意", "協定"]),
    "SS4": dict(ok_gloss="〜を見下す", ng_gloss="下を見る・見下ろす", ok_kw=["見下す", "見下し", "軽蔑", "見くび", "馬鹿に", "見下げ"], bad_kw=["見下ろ", "下を見"]),
    "SS5": dict(ok_gloss="ペースを上げる", ng_gloss="〜を拾い上げる", ok_kw=["ペース", "速", "上げ"], bad_kw=["拾"]),
    "SS6": dict(ok_gloss="〜の厳しさ・勢いを和らげる", ng_gloss="〜を脱ぐ・離陸する", ok_kw=["和らげ", "やわらげ", "軽減", "鈍", "緩和"], bad_kw=["脱ぐ", "外す", "離陸"]),
    "OO1": dict(ok_gloss="〜を実行する", ng_gloss="〜を運び出す", ok_kw=["実行", "行う", "遂行", "実施", "やり遂げ"], bad_kw=["運び出"]),
    "OO2": dict(ok_gloss="〜を(趣味などとして)始める", ng_gloss="場所を占める", ok_kw=["始め", "習い", "趣味", "手を出"], bad_kw=["占め", "場所"]),
    "OO3": dict(ok_gloss="〜を絞り込む", ng_gloss="〜を絞り込む", ok_kw=["絞", "狭め"], bad_kw=[]),
    "OO4": dict(ok_gloss="〜を厳しくする・引き締める", ng_gloss="〜を厳しくする", ok_kw=["厳しく", "引き締", "強化", "厳格", "厳重"], bad_kw=[]),
    "OO5": dict(ok_gloss="〜を調べる・調査する", ng_gloss="〜を調べる", ok_kw=["調べ", "調査", "検討", "究明"], bad_kw=["のぞ", "見入"]),
    "OO6": dict(ok_gloss="〜を解決する・整理する", ng_gloss="〜を解決する", ok_kw=["解決", "整理", "片付", "処理"], bad_kw=[]),
    "MO1": dict(ok_gloss="制限を設ける", ng_gloss="下限を設ける", ok_kw=["制限", "上限", "限度", "設ける", "設定", "限界"], bad_kw=[], mod_word="lower", mod_ja_kw=["下限", "低い", "下げ", "より低"]),
    "MO2": dict(ok_gloss="展開する・方向が変わる", ng_gloss="予想外の展開になる", ok_kw=["展開", "方向", "変わ", "転", "進"], bad_kw=[], mod_word="unexpected", mod_ja_kw=["予想外", "意外", "思いがけ", "予期せ"]),
    "MO3": dict(ok_gloss="〜の世話をする・面倒を見る", ng_gloss="〜をよく世話する", ok_kw=["世話", "面倒", "手入れ", "管理", "気を配"], bad_kw=[], mod_word="good", mod_ja_kw=["よく", "丁寧", "しっかり", "十分", "大切に"]),
    "MO4": dict(ok_gloss="決断する", ng_gloss="素早く決断する", ok_kw=["決断", "決定", "決め", "判断"], bad_kw=[], mod_word="quick", mod_ja_kw=["素早", "すばやく", "迅速", "即座", "急いで"]),
    "MO5": dict(ok_gloss="〜に注意を払う", ng_gloss="〜に細心の注意を払う", ok_kw=["注意", "気を配", "目を配", "注目"], bad_kw=[], mod_word="close", mod_ja_kw=["細心", "綿密", "よく", "十分に", "注意深"]),
    "MO6": dict(ok_gloss="〜で役割を果たす", ng_gloss="〜で重要な役割を果たす", ok_kw=["役割", "役目", "一役"], bad_kw=[], mod_word="key", mod_ja_kw=["重要", "主要", "鍵", "大きな"]),
    "ME1": dict(ok_gloss="〜で新境地を開く・先駆けとなる", ng_gloss="〜で着工する", ok_kw=["新境地", "開拓", "新しい分野", "先駆", "新た", "新しい"], bad_kw=["着工", "起工", "地面"]),
    "ME2": dict(ok_gloss="〜を大げさに騒ぎ立てる", ng_gloss="〜を取引する", ok_kw=["大げさ", "大騒ぎ", "重大視", "騒ぎ立", "大問題"], bad_kw=["取引", "契約", "商談"]),
    "ME3": dict(ok_gloss="〜を見て見ぬふりをする", ng_gloss="〜に目を向ける", ok_kw=["見て見ぬ", "目をつぶ", "無視", "見逃"], bad_kw=[]),
    "ME4": dict(ok_gloss="(人)に盛大な拍手を送る", ng_gloss="(人)を手伝う", ok_kw=["拍手", "喝采"], bad_kw=["手伝", "助け", "手を貸"]),
    "ME5": dict(ok_gloss="〜に対して後回しにされる・脇に回る", ng_gloss="席に着く", ok_kw=["後回し", "後ろに回", "二の次", "控え", "脇役", "一歩引", "優先度が低"], bad_kw=["座", "席に"]),
    "ME6": dict(ok_gloss="困った立場にいる", ng_gloss="水の中にいる", ok_kw=["困った", "窮地", "苦境", "トラブル", "立場", "厄介"], bad_kw=["熱い", "お湯"]),
    "OK1": dict(ok_gloss="(人)に〜を順を追って説明する", ng_gloss="(物)を順を追って説明する", ok_kw=["順を追", "説明", "案内", "手順"], bad_kw=[]),
    "OK2": dict(ok_gloss="〜を脇に置く・取っておく", ng_gloss="〜を脇に置く", ok_kw=["脇", "取っておく", "とっておく", "保留", "置いておく", "後回し", "わきに", "別にして"], bad_kw=[]),
    "OK3": dict(ok_gloss="〜を低く抑える", ng_gloss="〜を低く抑える", ok_kw=["抑え", "低く", "抑制", "下げ"], bad_kw=[]),
    "OK4": dict(ok_gloss="〜を逆にする・好転させる", ng_gloss="〜を逆にする", ok_kw=["逆", "好転", "転換", "反転", "向きを変", "裏返"], bad_kw=[]),
    "OK5": dict(ok_gloss="〜の場合には", ng_gloss="〜の場合には", ok_kw=["場合", "際"], bad_kw=[]),
    "OK6": dict(ok_gloss="緊張をほぐす・打ち解ける", ng_gloss="氷を割る", ok_kw=["打ち解け", "ほぐ", "雰囲気", "和ま", "ぎこちなさ", "場を"], bad_kw=["割る", "氷を"]),
    "SO1": dict(ok_gloss="(人)を泊める", ng_gloss="(物)を建てる・掲げる", ok_kw=["泊め", "宿泊"], bad_kw=["建て", "立て", "掲げ"]),
    "SO2": dict(ok_gloss="(人)を育てる", ng_gloss="(事)を話題に出す", ok_kw=["育て"], bad_kw=["話題", "持ち出"]),
    "SO3": dict(ok_gloss="〜を最後までやり遂げる", ng_gloss="(人)を支えて乗り切らせる", ok_kw=["やり遂げ", "最後まで", "完遂", "貫", "成し遂げ"], bad_kw=["支え", "乗り切らせ"]),
    "SO4": dict(ok_gloss="(人)を支えて乗り切らせる", ng_gloss="〜を最後までやり遂げる", ok_kw=["乗り切", "支え", "助け", "乗り越え"], bad_kw=["やり遂げ"]),
    "SO5": dict(ok_gloss="〜を建てる・張る・掲げる", ng_gloss="(人)を泊める", ok_kw=["建て", "立て", "張", "掲げ", "設置"], bad_kw=["泊め"]),
    "SO6": dict(ok_gloss="〜を話題に出す・持ち出す", ng_gloss="(人)を育てる", ok_kw=["持ち出", "話題", "言い出", "提起", "切り出"], bad_kw=["育て"]),
}
WRONG_REASON = {   # 上流(塊判定)が誤った語義を理由に書いた場合の再現(P0i)。TRIAL-02 untidi_a2のSEL理由『価値や効果を損なう』と同型
    "SS1": "take something away fromで価値や効果を損なう(take away fromの語義)", "SS2": "take upで(趣味・仕事を)始める意味の句動詞",
    "SS3": "come to termsで合意に達する意味の慣用句", "SS4": "look downで下を見る・見下ろす意味の句動詞",
    "SO3": "see someone throughで人を最後まで支える意味の句動詞", "SO2": "bring upで話題を持ち出す意味の句動詞",
    "ME1": "break groundで工事に着手する意味の慣用句", "AP2": "see off somethingで脅威・攻撃を撃退する意味の句動詞",
    "PF6": "go for somethingで何かを選ぶ・狙う意味の句動詞", "AP6": "shake someoneで人を振り払う意味の句動詞",
}
for p in P:
    m = META.get(p["id"])
    if m:
        p.update(ok_gloss=m["ok_gloss"], ng_gloss=m["ng_gloss"], gloss_ok_kw=m["ok_kw"], gloss_bad_kw=m["bad_kw"])
        if m.get("mod_word"):
            p.update(mod_word=m["mod_word"], gloss_mod_kw=m["mod_ja_kw"])
    if p["id"] in WRONG_REASON:
        p["wrong_reason_ja"] = WRONG_REASON[p["id"]]

if __name__ == "__main__":
    out = os.path.join(HERE, "kpg04_probes.json")
    json.dump(P, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    bad = [p["id"] for p in P if p["span"].lower() not in p["sentence"].lower() or p["sentence"] not in p["context"]]
    nogloss = [p["id"] for p in P if p["type"] != "FREE_COMBINATION" and "gloss_ok_kw" not in p]
    print(len(P), "probes; span/sentence不整合:", bad, "; gloss未登録:", nogloss, "; 注入対象:", sum(1 for p in P if p.get("wrong_reason_ja")))
