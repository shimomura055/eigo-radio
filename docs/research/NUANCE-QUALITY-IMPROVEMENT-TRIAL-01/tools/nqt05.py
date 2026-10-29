# 改善Prompt v3: v2へ「断定しすぎ防止・補足事情の禁止・3要素の重複回避」を追加(独立監査で再発した欠陥への対処)。DEV/Trial専用。
import sys, os, json, time, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nqt01 as q, nqt02 as n2
ACC_FROM = "- 事実(語義・用法)は一般に認められた英語の用法に基づき、断定しすぎない。ネイティブが不自然と感じる英文を例として出さない。"
ACC_NEW = ACC_FROM + """
- 表現そのものの意味を超えて断定しない。『それ以上は望まない』『譲れない条件』『強い〜は求めない』『意図せず』のように、本文と表現の意味からは確定できない心理・意図・条件を、その表現の意味として書かない。含みうる場合は『〜と聞こえることがある』『文脈によっては〜』と可能性の言い方にする。
- 本文にない事情・理由・登場人物の立場を補って説明しない(誰がどうなるか、なぜそう思うか等を創作しない)。
## 重複回避
- point_ja(この文脈での働き・1文)、各comparisonのnote_ja(その文の差)、explanation_ja(そこから導かれる要点・使いどころ・日本語訳とのずれ)で、同じ趣旨の文を繰り返さない。"""
def build_new3(inputs, fixed=None):
    cur = q.er.build_gen_prompt(inputs); head = cur[:cur.index(q.MARK)]
    t = n2.new2_tail(); assert ACC_FROM in t
    return head + t.replace(ACC_FROM, ACC_NEW, 1).format(explen=q.EXPLEN[inputs["level"]], fixed=(q.FIX_TMPL.format(e=fixed) if fixed else ""))
if __name__ == "__main__":
    T = q.v02a.trial.load_targets(); client = q.v02a.get_client(); res = {}
    jobs = [(c, "NEW3", None) for c in q.CELLS]
    for r in ("", "_r2", "_r3"):
        jobs += [("y_surname_std", "NEW3FIX" + r, "at least a little"), ("y_surname_adv", "NEW3FIXAT" + r, "at least")]
    def w(cell, cond, fx):
        try:
            inputs = q.build_inputs_for(cell, T); t0 = time.time()
            d = q.er.run_candidate(inputs, call_fn=q.make_fn(client, f"{cell}_{cond}", override_prompt=build_new3(inputs, fx)), judge_fn=q.make_fn(client, f"{cell}_{cond}j", max_out=5000))
            d["trial_extra_issues"] = q.check_new_extras(d, inputs); d["wall_sec"] = round(time.time() - t0, 2); q._save(cell, cond, d); res[f"{cell}_{cond}"] = (d["status"], d["trial_extra_issues"], d["usage"]["cost_jpy"], d["wall_sec"])
        except Exception as e: res[f"{cell}_{cond}"] = repr(e)
    ths = [threading.Thread(target=w, args=j) for j in jobs]; [t.start() for t in ths]; [t.join() for t in ths]
    print(json.dumps(res, ensure_ascii=False, indent=0)); print("spent", round(q.spent(), 3))
