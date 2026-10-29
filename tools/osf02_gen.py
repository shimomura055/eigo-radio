# ONE-STEP-FURTHER-CORNER-TRIAL-01 委任_02: DEV/Trial専用。Production code/Promptをimport・編集しない。osf01_genの関数を再利用し、費用ログは別ファイル(usage_log_02.jsonl)。
# 使い方: OSF_PAID=1 py osf02_gen.py gen <v3|v2|c3> <model> <tag> [cell...]  /  OSF_PAID=1 py osf02_gen.py pointfix
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osf01_gen as g
g.USAGE = os.path.join(g.OUT, "usage_log_02.jsonl"); g.CAP_JPY = 40.0   # 本委任の追加上限(通常30、理由記録で40)
_LV_OLD = "- レベル差: Standardは日常会話で使える平易な表現(基本表現はA2、発展表現はB1程度まで)。Advancedは議論・仕事・ニュースにも応用できる表現(B1〜B2)。同じ記事の別レベルとは違う表現を選ぶ必要はないが、レベルに合った選定をする。"
_LV_V3 = ("- レベル差(厳守): Standardは日常会話で使える平易な表現に限る。核表現は短い定型句・句動詞(目安: 3〜4語以内、各語が中学〜高校初級の語彙)で、発展文も12語前後まで。"
          "抽象的・論述的・書き言葉寄りの表現(例: come to terms with / make a case for / take into account のように議論や文章で使うもの)はStandardでは選ばない。"
          "基本表現との差が一読で分かることを優先する。Advancedは議論・仕事・ニュースにも応用できる表現(B1〜B2)。同じ記事の別レベルとは違う表現を選ぶ必要はないが、レベルに合った選定をする。\n"
          "- 自然さ(厳守): 発展文は、ネイティブが日常で実際に言う自然な文にする。直訳調・硬い言い回し・不自然な代名詞や語順の文(核表現を文に入れるために目的語や代名詞を無理に作った形)は避け、核表現が自然に使われる最も普通の文型で示す。")
assert _LV_OLD in g.PROMPTS["v2"]
g.PROMPTS["v3"] = g.PROMPTS["v2"].replace(_LV_OLD, _LV_V3)
_S4 = "4. 4条件を満たす最良の候補を1つ、さらに独立して価値のある別の候補があれば2つ目を選ぶ。2つ目は価値が1つ目と同程度に高いときだけ。品質の低い候補で2件に増やさない(1件で良い)。"
assert _S4 in g.PROMPTS["v3"]
c3 = g.PROMPTS["v3"].replace(_S4, "4. 条件を満たす候補を、互いに別の核表現・別の場面で必ず3つ選び、価値の高い順に並べる(rank=1が最良)。self_scoresは厳しく自己採点する。")
c3 = c3.replace("- itemsは1〜2件。", "- itemsは必ず3件。")
c3 = c3.replace('"self_check": {{', '"rank": 1, "self_scores": {{"learning_value": 1, "level_fit": 1, "natural": 1}}, "self_check": {{')
assert c3 != g.PROMPTS["v3"] and '"rank"' in c3
g.PROMPTS["c3"] = c3

PF = """あなたは日本人の英語学習者向け教材の編集者です。下の「One Step Further」項目について、独立監査の指摘を直してください。
# 記事(英文)
{body}
# 現在の項目(JSON)
{item}
# 監査の指摘
{issues}
# 直し方
- 核表現(core_expression)は変えない。指摘が示す点(説明の回りくどさ・誇張・本文にない記述・発展文が長く核を取り出しにくい点)だけを直す。
- point_jaは2〜3文・130字以内。使い方と、言い過ぎ・間違えやすい点があれば簡潔に。topic_hook_jaは本文に書かれていることだけを根拠にする(本文で明記されていない行動・心理を断定しない)。
- further_en/further_jaが長すぎる場合は、同じ核表現で短い自然な文にしてよい。
- 出力はJSONのみ(現在の項目と同じ全フィールド。self_checkも含める)。"""
PFJOBS = {"x_adv": ("have something to show for", ["「労力に見合う」ほど十分な成果があるとは限らない(言い過ぎ注意)。説明で成果の量を言い過ぎない", "発展文が長く、核の表現を取り出して覚えにくい"], "x_adv__v2__s1"),
          "z_std": ("let something show", ["「にじみ出るままにする」は、letの説明としてやや回りくどい", "本文の最初の笑顔は、不安を隠す行動とは明記されていない(着想文を本文の記述だけにする)"], "z_std__v2__s1")}
def pointfix():
    import threading
    T = g._load_nt().load_targets(); client = g.get_client(); res = {}
    def one(cell, iss, src):
        inp = g.inputs_for(cell, T); d = json.load(open(os.path.join(g.OUT, src + ".json"), encoding="utf-8"))
        it = [i for i in d["result"]["items"] if PFJOBS[cell][0] in i["core_expression"]][0]
        pr = PF.format(body=inp["body"], item=json.dumps(it, ensure_ascii=False, indent=1), issues="\n".join("- " + x for x in iss))
        text, m, ud, c, el = g.call(client, "gpt-6.1-sol", pr, f"{cell}__pointfix__s1", max_out=6000)
        fixed = g.parse(text)
        json.dump({"cell": cell, "model": m, "usage": ud, "cost_jpy": c, "elapsed_sec": el, "before": it, "after": fixed}, open(os.path.join(g.OUT, f"{cell}__pointfix__s1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        res[cell] = {"cost": c, "sec": el}
    ths = [threading.Thread(target=one, args=(c, v[1], v[2])) for c, v in PFJOBS.items()]
    [t.start() for t in ths]; [t.join() for t in ths]; print(res, "spent", round(g.spent(), 3))
if __name__ == "__main__":
    if sys.argv[1] == "pointfix": pointfix()
    elif sys.argv[1] == "prompt":
        i = g.inputs_for(sys.argv[3]); print(g.build_prompt(i, sys.argv[2]))
    else: g.main()
