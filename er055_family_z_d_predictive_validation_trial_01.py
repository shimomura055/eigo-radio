# ============================================================
# er055_family_z_d_predictive_validation_trial_01.py
# 管理ID: FAMILY-Z-STORY-D-PREDICTIVE-VALIDATION-TRIAL-01 (委任_01)
# ============================================================
# 目的: D(短編化適性)評価が英語Storyの完成品質を予測できるかを検証するため、
# 『蜘蛛の糸』(L13)と『檸檬』(L11)を「同一条件」で英語Story化する Trial 専用driver。
#
# 位置づけ: DEV/Trial専用(到達上限VALIDATED)。Production非参照・非変更。
#   - 既存方式 = FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02
#     (er018_fiction_external_seed_selection_criteria_trial_02.py)の
#     Seed生成(call_seed) -> 英語Story生成(generate_story, A2/280-420語)。
#     ER-026 runner(Family Z)自体はText Writerを持たず、Trial-02の成果物を
#     canonical化するだけ(METHOD_REUSE_01.md参照)。
#   - Prompt/schema/語数定数は Trial-02 / e_axis から AST で「逐語抽出」する
#     (import しない = load_dotenv等の副作用なし、差分0を構造的に保証)。
#   - 音声/TTS/Assembly/KP/Comment/Preview 等は一切生成しない。
# Blind: Dスコア・比較Trial結果・過去評価・screening/PHASE_C_* は一切読まない
#   (assert_not_sealed が読込を拒否)。両作品でPrompt/パラメータ同一
#   (差分は原作本文とタイトル・著者のみ)。
# real は --approved-budget-jpy と --model の明示が必須(無ければ拒否)。
# ============================================================
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
MANAGEMENT_ID = "FAMILY-Z-STORY-D-PREDICTIVE-VALIDATION-TRIAL-01"
SRC_DIR = os.path.join(ROOT, "er054_output", "family_z_story_pool_trial_01", "sources")
OUT_BASE = os.path.join(ROOT, "er055_output", "family_z_d_predictive_validation_trial_01")
PRICING_SNAPSHOT = os.path.join(ROOT, "er005_output", "cost_baseline_01", "pricing_snapshot.json")
TRIAL02_PATH = os.path.join(ROOT, "er018_fiction_external_seed_selection_criteria_trial_02.py")
EAXIS_PATH = os.path.join(ROOT, "er018_fiction_story_dna_e_axis_redesign_01.py")
USD_JPY = 160.0
CAP_FACTOR = 1.5

# 作品定義。差分は原作本文とタイトル・著者のみ(Dスコア等は一切持たせない)。
WORKS = {
    "L13": {"title_ja": "蜘蛛の糸", "author_ja": "芥川龍之介", "title_en_hint": "The Spider's Thread"},
    "L11": {"title_ja": "檸檬", "author_ja": "梶井基次郎", "title_en_hint": "Lemon"},
}
WORK_ORDER = ("L13", "L11")

# 許可モデル(明示指定必須。Production routing key は触らない)
ALLOWED_MODELS = ("gpt-5.6-luna", "gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra")
SEED_EFFORT = "medium"   # Trial-02 call_seed と同一
STORY_EFFORT = "high"    # Trial-02 step_story と同一
STORY_MAX_ATTEMPTS = 2   # Trial-02 call_with_retry(max_attempts=2) と同一

# Blind: 読込禁止パターン(パスに含まれたら拒否)
SEALED_DENY = (
    "SEALED_", "PHASE_C_", "PHASE_D_", "PAST_COMPARISON", "SCORE_TABLE", "ANALYSIS_01",
    "family_z_story_quality_model_comparison_trial_01", "/screening/", "RESULT_01",
    "SCREENING_TABLE", "STORY_POOL_0", "rights_data",
)
# Prompt本文に混入してはならない語(Dスコア・評価結果の漏洩検知)
LEAK_TOKENS = ("短編化適性", "D=88", "D=47", "D-score", "Dスコア", "SEALED", "PHASE_C", "PAST_COMPARISON",
               "extractability", "loss_severity")

# 入力tok推定(実測: 日本語は約1.0tok/文字 + Prompt枠。委任_01で上限×1.5)
TOK_PER_CHAR = 1.0
SEED_TEMPLATE_TOK = 700       # developer + template + conversion plan
STORY_INPUT_TOK = 900         # Trial-02 実測 799〜849
SEED_OUT_TOK_POINT = 1500     # Trial-02実測 431〜541(短い摘要入力)。全文入力でreasoning増を見込む
STORY_OUT_TOK_POINT = 2000    # Trial-02実測 833〜1500


class SealedAccessError(RuntimeError):
    pass


def assert_not_sealed(path: str) -> str:
    p = str(path).replace("\\", "/")
    for n in SEALED_DENY:
        if n.lower() in p.lower():
            raise SealedAccessError(f"STOP(Blind): 封印対象(Dスコア/過去評価/比較結果)の読込は禁止: {path}")
    return path


def read_text_guarded(path: str) -> str:
    assert_not_sealed(path)
    with open(path, encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------
# 既存方式の定数をASTで逐語抽出(import しない)
# ------------------------------------------------------------
def _extract_literals(py_path: str, names: tuple) -> dict:
    with open(py_path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            nm = node.targets[0].id
            if nm in names:
                found[nm] = ast.literal_eval(node.value)
    missing = [n for n in names if n not in found]
    if missing:
        raise RuntimeError(f"既存方式の定数が抽出できません({py_path}): {missing}")
    return found


_T02 = _extract_literals(TRIAL02_PATH, ("SEED_DEVELOPER_MESSAGE", "SEED_USER_TEMPLATE", "SEED_JSON_SCHEMA",
                                        "STORY_PROMPT_TEMPLATE"))
_EA = _extract_literals(EAXIS_PATH, ("COMMON_PRINCIPLES", "MAX_CHARACTERS", "WORD_TARGET",
                                     "WORD_ACCEPTABLE_RANGE", "WRITER_DEVELOPER_MESSAGE"))

SEED_DEVELOPER_MESSAGE = _T02["SEED_DEVELOPER_MESSAGE"]
SEED_USER_TEMPLATE_BRIEF = _T02["SEED_USER_TEMPLATE"]      # 既存方式(editor brief入力)そのまま
SEED_JSON_SCHEMA = _T02["SEED_JSON_SCHEMA"]
STORY_PROMPT_TEMPLATE = _T02["STORY_PROMPT_TEMPLATE"]
WRITER_DEVELOPER_MESSAGE = _EA["WRITER_DEVELOPER_MESSAGE"]
COMMON_PRINCIPLES = _EA["COMMON_PRINCIPLES"]
MAX_CHARACTERS = _EA["MAX_CHARACTERS"]
WORD_TARGET = _EA["WORD_TARGET"]
WORD_RANGE = tuple(_EA["WORD_ACCEPTABLE_RANGE"])

# 【逸脱1(要ユーザー判断)】原作全文入力モード用: brief見出し行のみ差し替え。他は逐語。
_BRIEF_HEADER = ("[Source brief -- written by the editor, in their own words, not quoted from\n"
                 "the original]")
_RAW_HEADER = ("[Original text -- the full public-domain source text, in its original language "
               "(Japanese). Title: {title} / Author: {author}]")
assert _BRIEF_HEADER in SEED_USER_TEMPLATE_BRIEF, "既存方式のSeed templateの見出しが想定と異なる"
SEED_USER_TEMPLATE_RAW = SEED_USER_TEMPLATE_BRIEF.replace(_BRIEF_HEADER, _RAW_HEADER)

# 全作品共通のconversion plan(raw-textモード用。作品固有の情報を含めない)
NEUTRAL_CONVERSION_PLAN = (
    "Keep this as a faithful, simplified retelling of the original work, not an unrelated new "
    "story. Keep the original setting, the central event, the main turning point, the ending and "
    "the lingering feeling of the original. Keep the original point of view (first person if the "
    "original is first person, third person if it is third person). Per this family's naming "
    "rule, only the protagonist may have a personal name; refer to every other person through "
    "their role or their relationship to the protagonist. You may simplify or compress minor "
    "episodes and long descriptions. Around 300-350 words, A2 level for an English learner."
)


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# 原作の取得と権利ゲート(済みの再確認、オフライン)
# ------------------------------------------------------------
def load_source(wid: str) -> dict:
    d = os.path.join(SRC_DIR, wid)
    text = read_text_guarded(os.path.join(d, "text_plain.txt")).strip() + "\n"
    manifest = json.loads(read_text_guarded(os.path.join(d, "fetch_manifest.json")))
    card_html = read_text_guarded(os.path.join(d, "card.html"))
    return {"text": text, "manifest": manifest, "card_html": card_html, "dir": d}


def check_rights(wid: str, src: dict) -> dict:
    """青空文庫作品カードの没年から日本PD(没後70年経過)を機械照合。失敗はSTOP。"""
    card = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", src["card_html"]))
    m = re.search(r"没年：\s*(\d{4})-", card)
    if not m:
        raise RuntimeError(f"RIGHTS_GATE_FAIL({wid}): 作品カードから没年を取得できない")
    death_year = int(m.group(1))
    pub = re.search(r"初出：[^0-9]*?(\d{4})", card)
    files = {f["role"]: f for f in src["manifest"]["files"]}
    ok_http = all(f.get("ok") and f.get("http_status") == 200 for f in src["manifest"]["files"])
    pd_ok = (2026 - death_year) > 70
    if not (ok_http and pd_ok):
        raise RuntimeError(f"RIGHTS_GATE_FAIL({wid}): http_ok={ok_http} death_year={death_year}")
    return {
        "source": "aozora.gr.jp", "card_url": files["card"]["url"], "text_url": files["text"]["url"],
        "fetched_at": files["text"]["fetched_at"], "text_sha256_manifest": files["text"].get("sha256"),
        "author_death_year": death_year, "first_published_year": int(pub.group(1)) if pub else None,
        "japan_pd_life_plus_70": pd_ok, "gate": "PASS",
        "note": "原語(日本語)原作ベース。権利は委任文で確認済みの再照合(オフライン)。",
    }


# ------------------------------------------------------------
# Prompt構築(2作品で共通。差分は原作本文とtitle/authorのみ)
# ------------------------------------------------------------
def build_seed_messages(seed_input: str, wid: str, src_text: str, brief: dict | None = None) -> tuple:
    w = WORKS[wid]
    if seed_input == "raw":
        user = SEED_USER_TEMPLATE_RAW.format(
            source_brief=src_text.strip(), conversion_plan=NEUTRAL_CONVERSION_PLAN,
            title=w["title_ja"], author=w["author_ja"])
    elif seed_input == "brief":
        if not brief or not brief.get("source_brief") or not brief.get("conversion_plan"):
            raise RuntimeError("brief mode requires source_brief/conversion_plan")
        user = SEED_USER_TEMPLATE_BRIEF.format(source_brief=brief["source_brief"],
                                               conversion_plan=brief["conversion_plan"])
    else:
        raise RuntimeError(f"unknown seed_input: {seed_input}")
    for tok in LEAK_TOKENS:
        if tok in user:
            raise RuntimeError(f"BLIND_LEAK: seed promptに禁止語 {tok!r}")
    return SEED_DEVELOPER_MESSAGE, user


def build_story_prompt(seed: dict) -> str:
    seed_elements_block = "\n".join(f"- {e}" for e in seed["seed_elements"])
    prompt = STORY_PROMPT_TEMPLATE.format(
        seed_elements_block=seed_elements_block, conversion_plan=seed["conversion_plan"],
        common_principles=COMMON_PRINCIPLES, max_characters=MAX_CHARACTERS,
        word_target=WORD_TARGET, range_low=WORD_RANGE[0], range_high=WORD_RANGE[1])
    for tok in LEAK_TOKENS:
        if tok in prompt:
            raise RuntimeError(f"BLIND_LEAK: story promptに禁止語 {tok!r}")
    return prompt


# ------------------------------------------------------------
# 価格・費用
# ------------------------------------------------------------
def load_prices(model: str) -> dict:
    with open(PRICING_SNAPSHOT, encoding="utf-8") as f:
        snap = json.load(f)
    pr = {e["meter"]: e["price"] for e in snap["prices"] if e.get("model") == model}
    for k in ("input_tokens", "cached_input_tokens", "output_tokens"):
        if k not in pr:
            raise RuntimeError(f"PricingNotFound: {model}/{k}")
    return pr


def cost_jpy(pr: dict, in_tok: int, cached: int, out_tok: int) -> float:
    usd = (max(in_tok - cached, 0) * pr["input_tokens"] + cached * pr["cached_input_tokens"]
           + out_tok * pr["output_tokens"]) / 1_000_000
    return usd * USD_JPY


def estimate(model: str, char_counts: dict) -> dict:
    pr = load_prices(model)
    rows, tp, tc = [], 0.0, 0.0
    for wid, n in char_counts.items():
        s_in = int(n * TOK_PER_CHAR) + SEED_TEMPLATE_TOK
        s = cost_jpy(pr, s_in, 0, SEED_OUT_TOK_POINT)
        w = cost_jpy(pr, STORY_INPUT_TOK, 0, STORY_OUT_TOK_POINT)
        rows.append({"work": wid, "seed_in_tok": s_in, "seed_out_tok": SEED_OUT_TOK_POINT,
                     "story_in_tok": STORY_INPUT_TOK, "story_out_tok": STORY_OUT_TOK_POINT,
                     "seed_jpy": round(s, 4), "story_jpy": round(w, 4), "point_jpy": round(s + w, 4)})
        tp += s + w
    return {"model": model, "rows": rows, "point_jpy": round(tp, 4), "cap_jpy": round(tp * CAP_FACTOR, 4),
            "cap_factor": CAP_FACTOR}


# ------------------------------------------------------------
# API呼出(real) / mock
# ------------------------------------------------------------
def _usage(resp) -> dict:
    u = getattr(resp, "usage", None)
    if u is None:
        return {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0}
    ind = getattr(u, "input_tokens_details", None)
    outd = getattr(u, "output_tokens_details", None)
    return {"input_tokens": getattr(u, "input_tokens", 0) or 0,
            "cached_input_tokens": (getattr(ind, "cached_tokens", 0) or 0) if ind else 0,
            "output_tokens": getattr(u, "output_tokens", 0) or 0,
            "reasoning_tokens": (getattr(outd, "reasoning_tokens", 0) or 0) if outd else 0}


class Runner:
    def __init__(self, mode: str, model: str, client=None):
        self.mode, self.model, self.client = mode, model, client

    def seed(self, dev_msg: str, user_msg: str) -> dict:
        t0 = time.time()
        if self.mode == "mock":
            parsed = {
                "original_summary": "[MOCK] summary sentence one. Two. Three.",
                "seed_elements": ["[MOCK] element A", "[MOCK] element B", "[MOCK] element C"],
                "discarded_elements": ["[MOCK] minor detail"],
                "conversion_plan": "[MOCK] Retell faithfully in simple English, about 350 words.",
            }
            return {"parsed": parsed, "model": self.model, "response_id": "mock",
                    "usage": {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0,
                              "reasoning_tokens": 0}, "elapsed_sec": round(time.time() - t0, 3)}
        resp = self.client.responses.create(
            model=self.model, reasoning={"effort": SEED_EFFORT},
            input=[{"role": "developer", "content": dev_msg}, {"role": "user", "content": user_msg}],
            text={"format": {"type": "json_schema", **SEED_JSON_SCHEMA}})
        if resp.model != self.model and not str(resp.model).startswith(self.model):
            raise RuntimeError(f"STOP: actual model_id={resp.model} != requested {self.model}")
        text = resp.output_text
        if not text or not text.strip():
            raise RuntimeError("seed: 応答が空です")
        return {"parsed": json.loads(text), "model": resp.model, "response_id": resp.id,
                "usage": _usage(resp), "elapsed_sec": round(time.time() - t0, 3)}

    def story(self, prompt: str) -> dict:
        t0 = time.time()
        if self.mode == "mock":
            body = " ".join(["mock"] * 350)
            return {"raw_text": f"### [MOCK] Title\n\n{body}\n", "model": self.model, "response_id": "mock",
                    "usage": {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0,
                              "reasoning_tokens": 0}, "elapsed_sec": round(time.time() - t0, 3)}
        resp = self.client.responses.create(
            model=self.model, reasoning={"effort": STORY_EFFORT},
            input=[{"role": "developer", "content": WRITER_DEVELOPER_MESSAGE},
                   {"role": "user", "content": prompt}])
        if resp.model != self.model and not str(resp.model).startswith(self.model):
            raise RuntimeError(f"STOP: actual model_id={resp.model} != requested {self.model}")
        text = resp.output_text
        if not text or not text.strip():
            raise RuntimeError("Story応答が空です")
        return {"raw_text": text, "model": resp.model, "response_id": resp.id,
                "usage": _usage(resp), "elapsed_sec": round(time.time() - t0, 3)}


def call_with_retry(fn, max_attempts: int = STORY_MAX_ATTEMPTS) -> tuple:
    """Trial-02 e_axis.call_with_retry と同一ロジック(同一条件再試行、空出力等のみ)。"""
    attempts, last = [], None
    for a in range(1, max_attempts + 1):
        try:
            r = fn()
            attempts.append({"attempt": a, "success": True})
            return r, attempts
        except (RuntimeError, ValueError, KeyError) as exc:
            if str(exc).startswith("STOP"):
                raise
            attempts.append({"attempt": a, "success": False, "error": str(exc)[:500]})
            last = exc
    raise RuntimeError(f"{max_attempts}回の試行でも成功しませんでした: {last}") from last


def strip_markdown_title(raw: str) -> tuple:
    m = re.match(r"^###\s+(.+?)\s*\n\n?", raw)
    if not m:
        return None, raw.strip() + "\n"
    return m.group(1).strip(), raw[m.end():].strip() + "\n"


def run_work(wid: str, runner: Runner, seed_input: str, out_dir: str, pr: dict,
             budget: dict, briefs: dict | None) -> dict:
    src = load_source(wid)
    rights = check_rights(wid, src)
    w = WORKS[wid]
    odir = os.path.join(out_dir, wid)
    os.makedirs(odir, exist_ok=True)
    dev_msg, user_msg = build_seed_messages(seed_input, wid, src["text"], (briefs or {}).get(wid))

    def guard(label, est_jpy):
        if runner.mode == "real" and budget["spent_jpy"] + est_jpy * CAP_FACTOR > budget["approved_jpy"]:
            raise RuntimeError(f"STOP(budget_guard:{label}): 累計{budget['spent_jpy']:.4f}+次callの上限"
                               f"{est_jpy * CAP_FACTOR:.4f} > 承認額{budget['approved_jpy']}")

    n = len(src["text"])
    guard(f"seed_{wid}", cost_jpy(pr, int(n * TOK_PER_CHAR) + SEED_TEMPLATE_TOK, 0, SEED_OUT_TOK_POINT))
    seed_res = runner.seed(dev_msg, user_msg)
    s_cost = cost_jpy(pr, seed_res["usage"]["input_tokens"], seed_res["usage"]["cached_input_tokens"],
                      seed_res["usage"]["output_tokens"])
    budget["spent_jpy"] += s_cost
    seed = dict(seed_res["parsed"])
    seed["title"] = w["title_ja"]
    seed["author"] = w["author_ja"]
    seed["rights_status"] = rights
    with open(os.path.join(odir, "seed.json"), "w", encoding="utf-8") as f:
        json.dump(seed, f, ensure_ascii=False, indent=2)

    story_prompt = build_story_prompt(seed)
    guard(f"story_{wid}", cost_jpy(pr, STORY_INPUT_TOK, 0, STORY_OUT_TOK_POINT))
    story_res, attempts = call_with_retry(lambda: runner.story(story_prompt))
    st_cost = cost_jpy(pr, story_res["usage"]["input_tokens"], story_res["usage"]["cached_input_tokens"],
                       story_res["usage"]["output_tokens"])
    budget["spent_jpy"] += st_cost
    raw = story_res["raw_text"].strip() + "\n"
    with open(os.path.join(odir, "story_en.md"), "w", encoding="utf-8") as f:
        f.write(raw)
    title_en, body = strip_markdown_title(raw)
    wc_body = len(body.split())
    wc_raw = len(raw.split())
    meta = {
        "management_id": MANAGEMENT_ID, "work_id": wid, "title_ja": w["title_ja"], "author_ja": w["author_ja"],
        "mode": runner.mode, "seed_input_mode": seed_input,
        "requested_model": runner.model, "actual_model_seed": seed_res["model"],
        "actual_model_story": story_res["model"],
        "reasoning_effort": {"seed": SEED_EFFORT, "story": STORY_EFFORT},
        "story_max_attempts": STORY_MAX_ATTEMPTS, "story_attempts": attempts,
        "source": {"path": os.path.relpath(src["dir"], ROOT).replace("\\", "/") + "/text_plain.txt",
                   "chars": n, "sha256": sha256(src["text"])},
        "rights": rights,
        "prompt_sha256": {"seed_developer": sha256(dev_msg), "seed_user": sha256(user_msg),
                          "story_developer": sha256(WRITER_DEVELOPER_MESSAGE),
                          "story_user": sha256(story_prompt)},
        "developer_messages": {"seed": dev_msg, "story": WRITER_DEVELOPER_MESSAGE},
        "usage": {"seed": seed_res["usage"], "story": story_res["usage"]},
        "elapsed_sec": {"seed": seed_res["elapsed_sec"], "story": story_res["elapsed_sec"]},
        "response_id": {"seed": seed_res["response_id"], "story": story_res["response_id"]},
        "cost_jpy": {"seed": round(s_cost, 6), "story": round(st_cost, 6), "total": round(s_cost + st_cost, 6),
                     "usd_jpy": USD_JPY},
        "word_count": {"body_excl_title": wc_body, "raw_incl_title": wc_raw,
                       "accept_range": list(WORD_RANGE),
                       "in_range": WORD_RANGE[0] <= wc_body <= WORD_RANGE[1]},
        "english_title": title_en,
        "blind": "Dスコア・比較Trial結果・過去評価はSeed/Writerへ不使用、deny guard有効",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "regeneration": "なし(語数範囲外でも再生成しない。既存の空出力retryのみ)",
    }
    with open(os.path.join(odir, "seed_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(user_msg)
    with open(os.path.join(odir, "story_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(story_prompt)
    with open(os.path.join(odir, "run_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("mock", "real"), default="mock")
    ap.add_argument("--model", default=None, help=f"real必須。許可: {ALLOWED_MODELS}")
    ap.add_argument("--approved-budget-jpy", type=float, default=None)
    ap.add_argument("--seed-input", choices=("raw", "brief"), default="raw")
    ap.add_argument("--brief-dir", default=None, help="brief mode: <ID>.json(source_brief/conversion_plan)")
    ap.add_argument("--works", default=",".join(WORK_ORDER))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--estimate-only", action="store_true")
    a = ap.parse_args(argv)

    works = [x.strip() for x in a.works.split(",") if x.strip()]
    for x in works:
        if x not in WORKS:
            print(f"unknown work {x}")
            return 2
    model = a.model or "gpt-6-luna"
    if model not in ALLOWED_MODELS:
        print(f"STOP: model {model} は許可リスト外: {ALLOWED_MODELS}")
        return 2
    chars = {w: len(load_source(w)["text"]) for w in works}
    est = estimate(model, chars)
    if a.estimate_only:
        print(json.dumps(est, ensure_ascii=False, indent=2))
        return 0

    if a.mode == "real":
        if a.approved_budget_jpy is None or a.approved_budget_jpy <= 0:
            print("STOP: real は --approved-budget-jpy(>0)が必須(ユーザー承認額)")
            return 2
        if a.model is None:
            print("STOP: real は --model の明示が必須")
            return 2
        if est["cap_jpy"] > a.approved_budget_jpy:
            print(f"STOP: 上限見積{est['cap_jpy']}円 > 承認額{a.approved_budget_jpy}円")
            return 2
        from dotenv import load_dotenv  # realのみ。値は表示しない
        load_dotenv(os.path.join(ROOT, ".env"))
        from openai import OpenAI  # realのみ遅延import(.env等は読まない。環境変数のキーを使用)
        client = OpenAI()
    else:
        client = None

    out_dir = a.out_dir or (os.path.join(OUT_BASE, "mock_run") if a.mode == "mock" else OUT_BASE)
    briefs = None
    if a.seed_input == "brief":
        if not a.brief_dir:
            print("STOP: brief mode は --brief-dir 必須")
            return 2
        briefs = {w: json.loads(read_text_guarded(os.path.join(a.brief_dir, f"{w}.json"))) for w in works}
    pr = load_prices(model)
    budget = {"spent_jpy": 0.0, "approved_jpy": a.approved_budget_jpy or 0.0}
    runner = Runner(a.mode, model, client)
    metas = []
    for w in works:
        m = run_work(w, runner, a.seed_input, out_dir, pr, budget, briefs)
        metas.append(m)
        print(f"[{w}] model={m['actual_model_story']} words={m['word_count']['body_excl_title']} "
              f"in_range={m['word_count']['in_range']} cost_jpy={m['cost_jpy']['total']}")
    print(f"spent_jpy={budget['spent_jpy']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
