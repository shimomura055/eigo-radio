# -*- coding: utf-8 -*-
"""FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01 DEV専用。AI島Std日本語Comment 1-4のAfter(Z方式入力構成)を各1回生成。
Production関数(a2gen.run_support_text / 役割文定数 / er062定数)をimportするだけで、既存ファイルは書き換えない。
出力は本ディレクトリのafter_generation_log_01.jsonのみ。音声化なし。"""
import os, sys, json, re, hashlib, concurrent.futures as cf
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv
load_dotenv()
import er003_v1_iran01_a2_generate as a2gen
import er019_family_x_audio_plan_01 as plan
import er006_model_routing_contract_01 as routing
import er062_family_z_writer_01 as zw
import er062_family_z_structure_01 as st

OUT = "docs/research/FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01"
SRC = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/a2"
parts = json.load(open(f"{SRC}/parts.json", encoding="utf-8"))
P = {1: parts["part1"], 2: parts["part2"], 3: parts["part3"]}
before = json.load(open(f"{SRC}/a2_support_texts.json", encoding="utf-8"))

# ニュース向け適用: Zの結末段落目印(到着/城門等、Story固有)の代わりに、結論・留保段落の目印を使う。
NEWS_CONCLUSION_MARKER_RE = re.compile(r"\b(even so|still,|in short|overall|in conclusion|too soon|do(?:es)? not show|proof)\b", re.I)


def limit_part3_news(part3: str) -> str:
    """Z limit_comment3_part(先頭約25%・最低2段落)と同じ割合/最低段落定数(zw.COMMENT3_FACT_*)を使い、
    結論・留保段落(NEWS_CONCLUSION_MARKER_RE)以降を除外(最低1段落は残す)。"""
    paras = [p for p in part3.split("\n\n") if p.strip()]
    k = max(zw.COMMENT3_FACT_MIN_PARAGRAPHS, int(round(len(paras) * zw.COMMENT3_FACT_RATIO)))
    head = paras[:min(k, len(paras))]
    for i, p in enumerate(head):
        if NEWS_CONCLUSION_MARKER_RE.search(p):
            head = head[:max(i, 1)]
            break
    return "\n\n".join(head)


# Zの入力構成(er062_family_z_writer_01.py:1256-1260)のラベル・参照範囲。NOT_NEWS_NOTE(物語向け注記)は付けない。
CTX = {
    1: f"【本文(これから聞く部分)】\n{P[1]}",
    2: f"【すでに聞いた本文(前半)】\n{P[1]}\n\n【これから聞く本文(後半)】\n{P[2]}",
    3: f"【すでに聞いた本文(前半)】\n{P[1]}\n\n{P[2]}\n\n【これから聞く本文(後半)】\n{limit_part3_news(P[3])}",
    # Comment4: Z方式にComment4は無い。X固有役割(FAMILY_X_A2_COMMENT_4_ROLE)・参照範囲(全文)を維持し、ラベルのみZ流の『すでに聞いた本文』表記。方式差の効果は測れない(実質再サンプル)。
    4: f"【すでに聞いた本文(全体)】\n{P[1]}\n\n{P[2]}\n\n{P[3]}",
}
ROLE = {1: a2gen.COMMENT_1_ROLE, 2: a2gen.COMMENT_2_ROLE, 3: a2gen.COMMENT_2_ROLE, 4: plan.FAMILY_X_A2_COMMENT_4_ROLE}


class Rec:
    """usage取得用の薄いproxy(送信内容は不変)。"""
    def __init__(self, c): self.c = c; self.usages = []; self.responses = self
    def create(self, **kw):
        r = self.c.responses.create(**kw)
        u = getattr(r, "usage", None)
        self.usages.append({"model": getattr(r, "model", None), "in": getattr(u, "input_tokens", None), "out": getattr(u, "output_tokens", None)})
        return r


def main():
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    client = Rec(a2gen.get_client())

    def gen(n):
        rc = Rec(client.c)
        r = a2gen.run_support_text(rc, ROLE[n], CTX[n], model=model)
        return n, r, rc.usages
    res = {}
    with cf.ThreadPoolExecutor(4) as ex:
        for n, r, u in ex.map(gen, (1, 2, 3, 4)):
            res[n] = (r, u)
    usages = [x for n in res for x in res[n][1]]
    inp = sum(u["in"] or 0 for u in usages); out = sum(u["out"] or 0 for u in usages)
    jpy = (inp * 0.10 + out * 0.50) / 1e6 * 160
    log = {
        "managed_id": "FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01", "model_routing": model,
        "response_models": sorted({u["model"] for u in usages if u["model"]}),
        "params": "reasoning.effort=a2gen.REASONING_EFFORT(Production同一)、temperature/seed指定なし(Production同一)。developer message=a2gen.SUPPORT_DEVELOPER_MESSAGE",
        "input_source": {"parts": f"{SRC}/parts.json", "parts_sha256": hashlib.sha256(open(f'{SRC}/parts.json','rb').read()).hexdigest()},
        "comments": {}, "calls": len(usages), "in_tokens": inp, "out_tokens": out, "est_jpy": round(jpy, 4),
        "cost_basis": "pricing_snapshot gpt-6-luna in0.10/out0.50 USD per M x160",
    }
    for n in (1, 2, 3, 4):
        r, u = res[n]
        txt = r.get("text")
        log["comments"][f"comment_{n}"] = {
            "status": r["status"], "text": txt, "before_text": before[f"comment_{n}"],
            "role_const": {1: "a2gen.COMMENT_1_ROLE", 2: "a2gen.COMMENT_2_ROLE", 3: "a2gen.COMMENT_2_ROLE(Z流)", 4: "plan.FAMILY_X_A2_COMMENT_4_ROLE"}[n],
            "context_block": CTX[n], "full_prompt": r["prompt"], "attempts": r["attempts"], "usage": u,
            "info_lint_codes_not_applied_as_gate(Z lint_support_text、物語向け語禁止を含むため参考表示のみ)": st.lint_support_text(txt or "", "ja", "none", allow_listen_instruction_as_warn=True),
        }
    json.dump(log, open(f"{OUT}/after_generation_log_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for n in (1, 2, 3, 4):
        print(n, log["comments"][f"comment_{n}"]["status"], log["comments"][f"comment_{n}"]["text"])
    print("cost_jpy", log["est_jpy"], "calls", log["calls"])


if __name__ == "__main__":
    main()
