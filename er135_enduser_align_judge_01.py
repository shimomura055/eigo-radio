# ============================================================
# er135_enduser_align_judge_01.py
# ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03A(2026-10-30): 英日連動の対応づけの『LLM確認』(M8)。**実装のみ。既定では呼ばれない(API 0)**。
# 目的: 埋め込みDPが候補として出したが、境界ずらし余裕などで安全側にnullとした群について、LLMが『この日本語はこの英文の訳として対応しているか』を
#   確認できたものだけを追加で点灯させる(Std点灯率の取りこぼし対策)。
# 安全設計: (1)LLMは新しい対応を作らない。DPが出した候補群(英文範囲, 日本語範囲)の可否(ok/ng)を答えるだけ。
#          (2)採用条件=DP候補 かつ cos>=judge_tau かつ 数字・固有名の整合 かつ LLMがok。(3)応答不正・件数不一致・model不一致は全て不採用(fail-closed)。
#          (4)呼出は judge を明示的に渡したときだけ(build_enduserの既定None、hookは渡さない)。実呼出は委任_03B(Fable判断・費用承認後)。
# LLM呼出は注入(llm(prompt)->str)。本委任ではmockのみ。
# ============================================================
from __future__ import annotations

import hashlib
import json
import re

import er006_model_routing_contract_01 as routing

PROCESS = "ENDUSER_JA_ALIGN_JUDGE"
MODEL = routing.SUPPORT_MODEL
JUDGE_TAU = 0.30            # DP候補のcos下限(これ未満は無関係な可能性が高く、LLMに聞かない)
MAX_PAIRS_PER_CALL = 12

PROMPT_HEAD = """あなたは英日対訳の校閲者です。下に、英語の段落(文に番号付け)とその日本語訳の段落(文に番号付け)を示します。
日本語訳は原文を要約・言い換えしている場合があります。「確認する対応」に挙げた組ごとに、
「その日本語(番号の文)は、その英語(番号の文)に対応する訳であり、他の文の内容を取り込んでいない」と言えるかを判定してください。

# 判定の基準
- ok=true: 日本語が、挙げた英語の文(複数なら全体)の内容を過不足なく言い換えている。語順や言い回しが違っていても、内容が同じなら ok。
- ok=false: 日本語の内容が英語の別の文に対応している、英語にない内容が日本語にある、英語の内容が日本語で欠けている、または判断できない。迷ったら false。
- 文体の好みや自然さだけを理由に false にしない。

"""
PROMPT_BODY = """
# 出力形式
JSONのみ(前後に文章やコードブロックを付けない)。「確認する対応」のすべての番号について1つずつ書く。
{"results": [{"id": 1, "ok": true}, {"id": 2, "ok": false}]}
"""
PROMPT_SHA256 = hashlib.sha256("␟".join([PROMPT_HEAD, PROMPT_BODY]).encode("utf-8")).hexdigest()


class JudgeError(ValueError):
    pass


def build_prompt(en_texts: list, ja_texts: list, pairs: list) -> str:
    """pairs=[(en_idx_list, (j0, j1))]。番号は1始まり。"""
    en = "\n".join(f"E{i + 1}. {t}" for i, t in enumerate(en_texts))
    ja = "\n".join(f"J{j + 1}. {t}" for j, t in enumerate(ja_texts))
    chk = "\n".join(f"{k}. 英語 " + "・".join(f"E{i + 1}" for i in ens) + " ↔ 日本語 " + ("・".join(f"J{j + 1}" for j in range(j0, j1))) for k, (ens, (j0, j1)) in enumerate(pairs, 1))
    return PROMPT_HEAD + "# 英語の段落\n" + en + "\n\n# 日本語訳の段落\n" + ja + "\n\n# 確認する対応\n" + chk + "\n" + PROMPT_BODY


def parse(text: str, n: int) -> list:
    """[bool]*n。全idが1..nで揃い、okがboolでなければ JudgeError(=全て不採用)。"""
    t = (text or "").strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, re.S)
    t = m.group(1) if m else t
    try:
        d = json.loads(t)
    except ValueError as e:
        raise JudgeError(f"JSONとして読めません: {e}") from e
    rs = d.get("results") if isinstance(d, dict) else None
    if not isinstance(rs, list) or len(rs) != n:
        raise JudgeError(f"resultsの件数が不一致(期待{n})")
    out = []
    for k, r in enumerate(rs, 1):
        if not isinstance(r, dict) or r.get("id") != k or not isinstance(r.get("ok"), bool):
            raise JudgeError(f"id/okが不正: {str(r)[:60]}")
        out.append(r["ok"])
    return out


def make_judge(llm):
    """judge(en_texts, ja_texts, pairs) -> [bool]*len(pairs)。llm(prompt)->str は必須(既定の実APIへ黙って落ちない)。
    1段落につき1 call(pairsが12を超えるときは分割)。応答不正は全pair不採用(再試行しない=費用を増やさない。再実行は次回build)。"""
    if llm is None:
        raise ValueError("judge llm が無い(実API既定へフォールバックしない)")
    stats = {"calls": 0, "pairs": 0, "ok": 0, "failures": []}

    def judge(en_texts, ja_texts, pairs):
        res = []
        for i in range(0, len(pairs), MAX_PAIRS_PER_CALL):
            chunk = pairs[i:i + MAX_PAIRS_PER_CALL]
            stats["calls"] += 1
            stats["pairs"] += len(chunk)
            try:
                got = parse(llm(build_prompt(en_texts, ja_texts, chunk)), len(chunk))
            except JudgeError as e:
                stats["failures"].append(str(e)[:80])
                got = [False] * len(chunk)
            stats["ok"] += sum(got)
            res += got
        return res
    judge.stats = stats
    return judge


class DefaultLLM:
    """実API用(gpt-6-luna、応答modelが期待と違えばModelContractError)。**本委任では使用しない・生成もしない**(委任_03Bで明示的に渡す)。"""

    class ModelContractError(RuntimeError):
        pass

    def __init__(self, client=None):
        self.client = client
        self.calls = []

    def __call__(self, prompt: str) -> str:
        import er003_kp_source_sentence_ja_01 as kpja
        model = routing.require_model(PROCESS, MODEL)
        if self.client is None:
            import er003_v1_b1_scaffold_01_generate as b1s
            self.client = b1s.get_client()
        text, response_model, usage, response_id = kpja._default_call_fn_factory(self.client, model)(prompt)
        self.calls.append({"response_model": response_model, "usage": usage, "response_id": response_id, "cost_jpy": kpja._cost_jpy(response_model, usage or {})})
        if response_model != model:
            raise self.ModelContractError(f"応答モデルが不一致(期待{model}/実際{response_model})。fallbackせずSTOP")
        return text
