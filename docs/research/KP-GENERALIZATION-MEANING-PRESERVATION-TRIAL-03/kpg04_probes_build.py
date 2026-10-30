# -*- coding: utf-8 -*-
"""検証ケース(probe)48件の生成スクリプト。出力=kpg04_probes.json。API 0。
種別: ARG_PERSON_THING / FIXED_PRONOUN / SENSE_SHIFT / OBJECT_OMIT_OK / MODIFIER_DROPPABLE / MODIFIER_ESSENTIAL / ALREADY_CORRECT / FREE_COMBINATION(各6件)
既知の失敗2例(hear it out / take points away from)とは語句を変えた同型の例を含む(過適合の検出用)。ok=許容形、ng=既知のNG形(どちらでもなければREVIEW=実読)。"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
P = []


def add(id, type, span, sentence, context, ok, ng, note):
    P.append(dict(id=id, type=type, span=span, sentence=sentence, context=context, ok=ok, ng=ng, note=note))


# AP: 人/物の取違え(見出し形の標準的な目的語タイプ)
add("AP1", "ARG_PERSON_THING", "hear her out", "The coach asked the board to hear her out before making a decision.", "The coach was upset about the team's loss. The coach asked the board to hear her out before making a decision.", ["hear someone out"], ["hear something out"], "目的語が人")
add("AP2", "ARG_PERSON_THING", "see it off", "The whole town came to see it off.", "The old ship was leaving the port for the last time. The whole town came to see it off.", ["see someone off"], ["see something off"], "擬人化された物(船)。見出し標準は人")
add("AP3", "ARG_PERSON_THING", "sat through the whole lecture", "He sat through the whole lecture without taking a single note.", "The lecture lasted three hours. He sat through the whole lecture without taking a single note.", ["sit through something"], ["sit through someone"], "物・出来事を取る見出し")
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
# OO: 目的語を省略しても同語義(許容)
add("OO1", "OBJECT_OMIT_OK", "carried out the plan", "They carried out the plan last week.", "The team had worked on it for months. They carried out the plan last week.", ["carry out", "carry something out"], [], "")
add("OO2", "OBJECT_OMIT_OK", "take up painting", "He decided to take up painting last spring.", "He wanted a new hobby. He decided to take up painting last spring.", ["take up", "take up something"], [], "趣味を始める語義")
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
# ME: 修飾語を削ると意味が変わる
add("ME1", "MODIFIER_ESSENTIAL", "broke new ground in", "The team broke new ground in cancer research.", "The results surprised many doctors. The team broke new ground in cancer research.", ["break new ground in", "break new ground"], ["break ground in", "break ground"], "newを落とすと別語義(着工)")
add("ME2", "MODIFIER_ESSENTIAL", "in the long run", "In the long run, saving money pays off.", "Many people spend everything they earn. In the long run, saving money pays off.", ["in the long run"], ["in the run"], "")
add("ME3", "MODIFIER_ESSENTIAL", "turned a blind eye to", "The manager turned a blind eye to the problem.", "Everyone knew about it. The manager turned a blind eye to the problem.", ["turn a blind eye to"], ["turn an eye to", "turn eye to"], "")
add("ME4", "MODIFIER_ESSENTIAL", "gave him a hard time", "She gave him a hard time about the mistake.", "He had forgotten the meeting. She gave him a hard time about the mistake.", ["give someone a hard time"], ["give someone a time"], "")
add("ME5", "MODIFIER_ESSENTIAL", "has a sweet tooth", "He has a sweet tooth.", "He eats cake every day. He has a sweet tooth.", ["have a sweet tooth"], ["have a tooth"], "")
add("ME6", "MODIFIER_ESSENTIAL", "in hot water", "The mayor is in hot water over the new tax.", "People are angry in the city. The mayor is in hot water over the new tax.", ["in hot water"], ["in water"], "")
# OK0: すでに正しく一般化できる(壊さないことの確認)
add("OK1", "ALREADY_CORRECT", "walked me through the steps", "She walked me through the steps.", "I had never used the machine. She walked me through the steps.", ["walk someone through"], ["walk something through"], "")
add("OK2", "ALREADY_CORRECT", "set the numbers aside", "He set the numbers aside for now.", "The report was almost finished. He set the numbers aside for now.", ["set something aside"], [], "")
add("OK3", "ALREADY_CORRECT", "keep the costs down", "We will keep the costs down this year.", "Prices are rising everywhere. We will keep the costs down this year.", ["keep something down"], [], "")
add("OK4", "ALREADY_CORRECT", "turned the usual steps around", "The cook turned the usual steps around.", "The recipe was old. The cook turned the usual steps around.", ["turn something around"], [], "")
add("OK5", "ALREADY_CORRECT", "in the event of a delay", "In the event of a delay, please call us.", "Trains are sometimes late. In the event of a delay, please call us.", ["in the event of"], [], "")
add("OK6", "ALREADY_CORRECT", "break the ice", "A small joke can break the ice at a party.", "Nobody was talking to anyone. A small joke can break the ice at a party.", ["break the ice"], [], "")
# FC: 自由な組合せ(選定段で落とされるべき。SEL probe用。GEN probe対象外)
for i, (sp, se, cx) in enumerate([
        ("wiped the kitchen table", "She wiped the kitchen table with a damp cloth.", "The meal was over. She wiped the kitchen table with a damp cloth."),
        ("wrote a short report", "He wrote a short report on Friday.", "The boss wanted a summary. He wrote a short report on Friday."),
        ("opened the red door", "They opened the red door slowly.", "The hallway was dark. They opened the red door slowly."),
        ("a faint signal", "The lab measured a faint signal.", "The instrument was very sensitive. The lab measured a faint signal."),
        ("a very small number", "Only a very small number of people came.", "The weather was bad. Only a very small number of people came."),
        ("kept a notebook in the drawer", "She kept a notebook in the drawer.", "Her desk was tidy. She kept a notebook in the drawer.")], 1):
    add(f"FC{i}", "FREE_COMBINATION", sp, se, cx, [], [], "選定段(SEL)で落とされるべき(GEN対象外)")

if __name__ == "__main__":
    out = os.path.join(HERE, "kpg04_probes.json")
    json.dump(P, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    bad = [p["id"] for p in P if p["span"].lower() not in p["sentence"].lower() or p["sentence"] not in p["context"]]
    print(len(P), "probes; span/sentence不整合:", bad)
