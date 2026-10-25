# -*- coding: utf-8 -*-
"""er121_family_y_text_core_01.py
FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02A: Family Y 正式Production「テキストcore」(Closing/Gate lane)。

位置づけ(重要):
  - Family Y正式Productionのテキスト側core。DEV/Trial module(er110_family_y_*)は **importしない**(DEVのモジュール差替え・
    alias・予算skipをProductionへ持ち込まない)。DEVの関数は「展開移植」し、Prompt/判定基準の文言は一字も変えない
    (DEVとの一致はtestで固定: Prompt 02 byte一致+sha、入力block、schema、決定論検査、判定器prompt)。
  - import時にAPI呼出0・ファイル副作用0。環境変数・CLI・設定dictで挙動が変わる経路はない(本moduleにCLIは無い)。
  - 正式runner(02B: er121_family_y_runner_01.py)は produce_article(…) でこのmoduleを呼ぶ(委任_02C: 記事全体=Voice生成+Voice Gate+Lead+人物紹介+Closing+組立)。
    routing keyは02Bがer006へ登録する。未登録のままcallすると require_model が ModelContractViolation を送出する(fail-closed。API呼出の前)。
    produce_articleは最初のAPI呼出の前に全routing keyを preflight_routes で照合する(生成途中で未登録に当たって費用だけ発生するのを防ぐ)。
  - Closing一般化方式=Prompt 02(sha 4713ceff…)+gpt-6.1-sol/high(ユーザー正式採用 USER §2-2)。Prompt 03化・意味変更なし。
  - 『宅配の再配達』のみ案B固定注入(USER §2-3)。registry外のslugは必ず一般化方式。
  - M-1(Opus): Tension判定promptの欠落定義(「上記と同じ意味」の参照先)を逐語展開して補う。判定基準の文言は変えない。
"""
from __future__ import annotations

import glob
import hashlib
import itertools
import json
import os
import re
import unicodedata

import er003_audio_tts_asr_safety as safety
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er053_family_x_factlock_ja_writer_01 as w1

MANAGEMENT_ID = "FAMILY-Y-PRODUCTION-LAUNCH-01"
THEME_TAG = "FAMILY_Y_PRODUCTION_01"
STATUS = "FAMILY_Y_PRODUCTION"            # DEV側の DEV_TRIAL_ONLY と区別する(誤認防止)
SLOTS = ("voice_1", "voice_2", "voice_3")

# ============================================================
# Routing(DESIGN_02 §routing で確定。er006への登録は02Bが行う。ここは「期待値」の表)
# ============================================================
ROUTE = {
    "FAMILY_Y_CLOSING_GENERATE": {"model": "gpt-6.1-sol", "effort": "high"},
    "FAMILY_Y_CLOSING_REWRITE": {"model": "gpt-6.1-sol", "effort": "medium"},
    "FAMILY_Y_LEAK_JUDGE": {"model": "gpt-6-luna", "effort": "high"},
    "FAMILY_Y_VOICE_GENERATE": {"model": "gpt-6.1-sol", "effort": "high"},
    "FAMILY_Y_VOICE_REWRITE": {"model": "gpt-6.1-sol", "effort": "medium"},
    "FAMILY_Y_LEAD_GENERATE": {"model": "gpt-6.1-sol", "effort": "high"},
    "FAMILY_Y_PERSONA_INTRO": {"model": "gpt-6.1-sol", "effort": "high"},
}


# 委任_02C追加: Voice生成の出典対応付番・構造タグ(DEV実在意見ベース方式のluna判定call、effort medium)。
# 02Bがer006へ登録するまでは別表(ROUTE本体のdrift test[02B所有]を壊さないため)。登録後はROUTEへ統合してよい。
ROUTE_AUX = {
    "FAMILY_Y_VOICE_PROVENANCE_MAP": {"model": "gpt-6-luna", "effort": "medium"},
    "FAMILY_Y_VOICE_STRUCTURE_TAG": {"model": "gpt-6-luna", "effort": "medium"},
}


def _route_entry(route_key: str) -> dict:
    ent = ROUTE.get(route_key) or ROUTE_AUX.get(route_key)
    if ent is None:
        raise routing.ModelContractViolation(f"未知のY route key: {route_key}")
    return ent


def preflight_routes(keys) -> list:
    """API呼出の前に、これから使うrouting keyが全てer006へ登録済みで期待modelと一致することを確認する(未登録/不一致は ModelContractViolation)。"""
    out = []
    for k in keys:
        ent = _route_entry(k)
        routing.require_model(k, ent["model"])
        out.append({"routing_key": k, "model": ent["model"], "effort": ent["effort"]})
    return out


class YStop(RuntimeError):
    """Y Productionの安全停止(本文を手で直さない)。"""

    def __init__(self, code: str, message: str, payload=None):
        super().__init__(f"[STOP] {code}: {message}")
        self.code, self.payload = code, payload


class ProvenanceViolation(RuntimeError):
    pass


_sleep = None  # testで差替え可能(None=time.sleep)


def _do_sleep(sec: float):
    import time
    (_sleep or time.sleep)(sec)


def chat(client, *, route_key: str, user: str, stage: str, developer: str | None = None, schema: dict | None = None, retries: int = 2, guard=None):
    """単一のAPI入口。routing契約を**API呼出の前に**照合(未登録/不一致はModelContractViolation=fail-closed)し、
    返却modelが期待と合わなければSTOP。client未注入(None)は例外(API遮断harnessの担保)。
    guard(stage): runnerの予算guard等。API呼出の前(routing照合の後)に1回だけ呼ぶ。例外ならAPIを呼ばない。"""
    if client is None:
        raise RuntimeError("[NO_CLIENT] clientが注入されていません")
    ent = _route_entry(route_key)
    model, effort = ent["model"], ent["effort"]
    routing.require_model(route_key, model)
    if guard is not None:
        guard(stage)
    inp = []
    if developer:
        inp.append({"role": "developer", "content": developer})
    inp.append({"role": "user", "content": user})
    kw = dict(model=model, reasoning={"effort": effort}, input=inp)
    if schema:
        kw["text"] = {"format": {"type": "json_schema", **schema}}
    last = None
    for i in range(1 + retries):
        try:
            with cl.logging_context(THEME_TAG, stage):
                resp = client.responses.create(**kw)
            if not str(getattr(resp, "model", "")).startswith(model):
                raise ProvenanceViolation(f"[STOP] {stage}: 返却modelが{model}で始まらない: {getattr(resp, 'model', None)}")
            return resp
        except ProvenanceViolation:
            raise
        except Exception as e:  # noqa: BLE001  一時エラーのみ再試行(最大2回)
            last = e
            _do_sleep(3 * (i + 1))
    raise RuntimeError(f"{stage}: API失敗(再試行{retries}回後): {last!r}")


def resp_meta(resp) -> dict:
    u = getattr(resp, "usage", None)
    return {"response_id": getattr(resp, "id", None), "model": getattr(resp, "model", None),
            "usage": {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None)}}


# ============================================================
# 検査語(DEVの正規表現と同一。testでpattern一致を固定)
# ============================================================
FIRST_PERSON_RE = re.compile(r"(私|わたし|僕|ぼく|俺|おれ|あたし)")
LEAD_BAD_RE = re.compile(r"(取材|話を聞い|聞いてみ|インタビュー|直撃)")
LABEL_START_RE = re.compile(r"^\s*(?:#|【|リード|Voice|ボイス|人物|語り手|[A-Cａ-ｃＡ-Ｃ]さん[:：])")
SENT_SPLIT_RE = re.compile(r"(?<=[。！？!?])")
DESU_MASU_RE = re.compile(r"(です|ます|でした|ました|でしょう)(?:[。！？]|$|[」])")
AI_ANNOUNCE_RE = re.compile(r"(実在|公開されている|公開された|ネットなど|組み立てた|組み立て|AI|人工知能|複数の意見をもと|特定の人の話)")
OBVIOUS_RE = re.compile(r"(立場(や暮らし)?(に)?(よって|ごとに|が違|で違)|人それぞれ|答えが(分か|違|割れ)|考え(方)?が(違|異な|分か)|大事にしたい(もの|こと)は(違|異な))")
DIGIT_RE = re.compile(r"[0-9０-９]")
CLOSING_RANGE = (175, 245)
MAX_SENT = 55


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _read_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _fin(raw: str) -> tuple:
    clean = w1.clean_ja_for_next(raw)
    final = w1.postprocess_ja(clean).strip()
    return final, safety.detect_prohibited_symbols(final, language="ja")


def check_closing(text: str) -> dict:
    """Closing決定論検査(DEV rev.check_closingの移植。175〜245字・1文55字以内・「？」終わり等)。"""
    v = []
    t = (text or "").strip()
    if not t:
        return {"ok": False, "violations": ["EMPTY"]}
    if "\n" in t:
        v.append("MULTI_PARAGRAPH")
    if FIRST_PERSON_RE.search(t):
        v.append("HAS_FIRST_PERSON")
    if LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    if LEAD_BAD_RE.search(t):
        v.append("HAS_INTERVIEWER_EXPRESSION")
    if DIGIT_RE.search(t):
        v.append("HAS_DIGIT")
    if DESU_MASU_RE.search(t):
        v.append("DESU_MASU")
    if AI_ANNOUNCE_RE.search(t):
        v.append("HAS_AI_EDIT_ANNOUNCEMENT")
    if OBVIOUS_RE.search(t):
        v.append("OBVIOUS_CONCLUSION_PHRASE")
    if not re.search(r"[？?]\s*$", t):
        v.append("NOT_ENDING_WITH_QUESTION")
    if not (CLOSING_RANGE[0] <= len(t) <= CLOSING_RANGE[1]):
        v.append(f"LENGTH={len(t)}")
    if any(len(s) > MAX_SENT for s in SENT_SPLIT_RE.split(t) if s.strip()):
        v.append("SENTENCE_TOO_LONG")
    return {"ok": not v, "violations": v}


# ============================================================
# Prompt 02(byte一致コピー + sha照合。testとruntimeの両方)
# ============================================================
PROMPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er121_prompts", "closing_general_02.txt")
PROMPT_SHA256 = "4713ceff2dd00a2f67eb9313ae9e206a4a3236c5b158e624c10ccf6fc20e5f07"
PROMPT_VERSION = "02"
RULES_MARKER = "【最終パートの書き方】"
RULES_END_MARKER = "出力はJSONのみ"


def load_prompt_parts(path: str = None) -> dict:
    raw = _read_bytes(path or PROMPT_FILE).replace(bytes([13, 10]), bytes([10]))      # CRLF変換差でshaが変わらないようLF正規化(DEVと同一)
    text = raw.decode("utf-8")
    m = re.match(r"=====DEVELOPER=====\n(.*?)\n=====USER=====\n(.*)\Z", text, re.S)
    if not m:
        raise YStop("PROMPT_FORMAT", "prompt fileの形式が想定と違います")
    sha = hashlib.sha256(raw).hexdigest()
    if sha != PROMPT_SHA256:
        raise YStop("PROMPT_SHA_MISMATCH", f"{sha} != {PROMPT_SHA256}(Prompt 02から変更されています。Prompt 03化はユーザー判断)")
    return {"developer": m.group(1).strip(), "user_template": m.group(2).rstrip("\n"), "sha256": sha}


def closing_rules_section(parts: dict) -> str:
    """Prompt 02の【最終パートの書き方】節を逐語で切り出す(M-2: 書換え規則はPrompt 02の規則を使う。旧B骨格は使わない)。"""
    u = parts["user_template"]
    i = u.index(RULES_MARKER)
    j = u.index(RULES_END_MARKER, i)
    return u[i:j].rstrip("\n")


# ============================================================
# 入力(テーマ情報+Persona 3+Voice本文 3)。DEV normalize_input/render_blocks/build_promptの移植
# ============================================================
def normalize_input(question: str, premise: str, distinctions: list, personas: list, voices: dict) -> dict:
    return {"question": question, "premise": premise, "distinctions": distinctions,
            "personas": [{"role": x["role"], "sketch": x["sketch"], "stake": x["stake"]} for x in personas],
            "voices": {s: voices[s].strip() for s in SLOTS}}


def render_blocks(inp: dict) -> dict:
    ds = "\n".join(f"- {x['term_ja']}: {x['definition_ja']}" for x in inp["distinctions"])
    theme = (f"【テーマ・論点】{inp['question']}\n【前提と範囲】{inp['premise']}\n【用語の意味】\n{ds}")
    persona = "【3人の人物像】\n" + "\n".join(
        f"- 人物{i + 1}: {x['role']}。{x['sketch']} 大事にしていること: {x['stake']}" for i, x in enumerate(inp["personas"]))
    voice = "\n\n".join(f"【人物{i + 1}の語り】\n{inp['voices'][s]}" for i, s in enumerate(SLOTS))
    return {"@@THEME_BLOCK@@": theme, "@@PERSONA_BLOCK@@": persona, "@@VOICE_BLOCK@@": voice}


def build_prompt(inp: dict, parts: dict = None) -> dict:
    parts = parts or load_prompt_parts()
    user = parts["user_template"]
    for k, v in render_blocks(inp).items():
        user = user.replace(k, v)
    if "@@" in user:
        raise YStop("PROMPT_PLACEHOLDER", "未置換のplaceholderが残っています")
    return {"developer": parts["developer"], "user": user, "prompt_sha256": parts["sha256"], "user_sha256": w1.sha_text(user)}


# ============================================================
# 出力schema(DEVと同一)・決定論検査・再生成(1回)・CLOSING_GENERAL_CONTRACT_STOP
# ============================================================
_QUOTES = {"type": "array", "items": {"type": "string"}}
SCHEMA = {"name": "family_y_closing_general", "strict": True, "schema": {
    "type": "object", "additionalProperties": False,
    "required": ["observations", "candidates", "selected_id", "selection_reason", "closing_ja"],
    "properties": {
        "observations": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["kind", "note", "evidence_quotes"],
            "properties": {"kind": {"type": "string", "enum": ["共通点", "相違点", "矛盾", "意外性"]}, "note": {"type": "string"}, "evidence_quotes": _QUOTES}}},
        "candidates": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["id", "new_view", "evidence_quotes", "deepens", "listener_question", "pitfall"],
            "properties": {"id": {"type": "string"}, "new_view": {"type": "string"}, "evidence_quotes": _QUOTES, "deepens": {"type": "string"},
                           "listener_question": {"type": "string"}, "pitfall": {"type": "string"}}}},
        "selected_id": {"type": "string"},
        "selection_reason": {"type": "string"},
        "closing_ja": {"type": "string"},
    }}}

_PROBLEM_JA = {
    "EMPTY": "closing_ja が空でした。最終パートの本文を書いてください。",
    "MULTI_PARAGRAPH": "改行が入っていました。最終パートは改行なしの1段落にしてください。",
    "HAS_FIRST_PERSON": "一人称(私・俺・僕・わたし)が入っていました。語り手の声で、一人称を使わずに書いてください。",
    "LABEL_AT_START": "冒頭にラベルのような言葉が入っていました。ラベルや見出しは書かず、本文から始めてください。",
    "HAS_INTERVIEWER_EXPRESSION": "取材者がいるような言い方(取材した、話を聞いた等)が入っていました。使わないでください。",
    "HAS_DIGIT": "算用数字が入っていました。数字は使わず、言葉で書いてください。",
    "DESU_MASU": "です・ます調が入っていました。話し言葉の常体で書いてください。",
    "HAS_AI_EDIT_ANNOUNCEMENT": "編集やAIについて断る文言が入っていました。本文だけを書いてください。",
    "OBVIOUS_CONCLUSION_PHRASE": "「人によって違う」のような当然の結論で終える言い方が入っていました。避けてください。",
    "NOT_ENDING_WITH_QUESTION": "文末が「？」で終わっていませんでした。最後は聞き手への問い1つで、文末を「？」にしてください。",
    "SENTENCE_TOO_LONG": "1文が長すぎる箇所がありました。1文は45字以内に区切ってください。",
}


def explain_problem(code: str) -> str:
    if code in _PROBLEM_JA:
        return _PROBLEM_JA[code]
    if code.startswith("LENGTH="):
        return f"本文の長さが{code[7:]}字でした。約190〜230字の範囲に収めてください。"
    if code.startswith("CANDIDATES_COUNT="):
        return "候補の切り口の数が3〜5個の範囲ではありませんでした。3〜5個にしてください。"
    if code == "CANDIDATE_ID_DUP":
        return "候補の id が重複していました。候補ごとに別の id を付けてください。"
    if code == "SELECTED_ID_NOT_IN_CANDIDATES":
        return "selected_id が候補の id にありませんでした。候補の id から選んでください。"
    if code == "NO_OBSERVATIONS":
        return "観察の欄が空でした。語りの中から見つかった観察を書いてください。"
    if code.startswith("TAG_LEAK:"):
        return "本文に内部用のタグのような表記が入っていました。本文だけを書いてください。"
    if code.startswith("SYMBOL:"):
        return "使えない記号(括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字など)が入っていました。使わずに書いてください。"
    return f"本文に問題がありました({code})。ルールを見直して書き直してください。"


def _squash(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def check_structure(obj: dict) -> list:
    v = []
    cands = obj.get("candidates") or []
    ids = [c.get("id") for c in cands]
    if not (3 <= len(cands) <= 5):
        v.append(f"CANDIDATES_COUNT={len(cands)}")
    if len(set(ids)) != len(ids):
        v.append("CANDIDATE_ID_DUP")
    if obj.get("selected_id") not in ids:
        v.append("SELECTED_ID_NOT_IN_CANDIDATES")
    if not (obj.get("observations") or []):
        v.append("NO_OBSERVATIONS")
    return v


def grounding_report(obj: dict, voices: dict) -> dict:
    """根拠引用が語りの本文に実在するか(記録専用。合否に使わない)。"""
    body = _squash("".join(voices[s] for s in SLOTS))
    qs = [q for o in obj.get("observations", []) for q in o["evidence_quotes"]] + [q for c in obj.get("candidates", []) for q in c["evidence_quotes"]]
    found = [q for q in qs if _squash(q) and _squash(q) in body]
    return {"n_quotes": len(qs), "n_verbatim": len(found), "missing": [q for q in qs if q not in found][:12]}


def generate_closing_general(client, inp: dict, out_dir: str, *, parts: dict = None, guard=None) -> dict:
    """Prompt 02で1生成(+決定論検査違反時のみ再生成1回)。残れば CLOSING_GENERAL_CONTRACT_STOP。
    Gateはここでは通さない(run_closing_gateで通す)。"""
    os.makedirs(out_dir, exist_ok=True)
    pr = build_prompt(inp, parts)
    w1.wt(os.path.join(out_dir, "prompt_developer.txt"), pr["developer"])
    w1.wt(os.path.join(out_dir, "prompt_user.txt"), pr["user"])
    hist, calls, cur, obj, final = [], [], pr["user"], None, ""
    for k in (1, 2):
        resp = chat(client, route_key="FAMILY_Y_CLOSING_GENERATE", user=cur, developer=pr["developer"], schema=SCHEMA,
                    stage="yp_closing_gen" + ("" if k == 1 else "_regen"), guard=guard)
        calls.append({**resp_meta(resp), "user_sha256": w1.sha_text(cur)})
        obj = json.loads(resp.output_text)
        w1.wj(os.path.join(out_dir, f"analysis_try{k}.json"), obj)
        probs = check_structure(obj)
        final = ""
        try:
            final, sym = _fin(obj.get("closing_ja", ""))
            probs += check_closing(final)["violations"]
            if safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
        except w1.TagLeak as e:
            probs.append(f"TAG_LEAK:{e}")
        hist.append(probs)
        if not probs:
            break
        if k == 1:
            cur = pr["user"] + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {explain_problem(x)}" for x in probs)
    else:
        w1.wj(os.path.join(out_dir, "gen_meta.json"), {"calls": calls, "problems_per_try": hist, "status": "CONTRACT_STOP"})
        raise YStop("CLOSING_GENERAL_CONTRACT_STOP", f"再生成後も契約違反 {hist[-1]}", hist)
    w1.wj(os.path.join(out_dir, "analysis_final.json"), obj)
    w1.wj(os.path.join(out_dir, "grounding_report.json"), grounding_report(obj, inp["voices"]))
    meta = {"calls": calls, "problems_per_try": hist, "status": "DONE", "chars": len(final), "prompt_sha256": pr["prompt_sha256"],
            "user_sha256": pr["user_sha256"], "selected_id": obj["selected_id"], "gen_sha256": w1.sha_text(final)}
    w1.wj(os.path.join(out_dir, "gen_meta.json"), meta)
    selected = next(c for c in obj["candidates"] if c["id"] == obj["selected_id"])
    return {"text": final, "meta": meta, "selected": selected, "analysis": obj}


# ============================================================
# Leakage判定(旧B承認13項目の日本語移植。Voice 7項目 / 最終パート6項目)
# 判定基準の文言はDEVと一字も変えない。M-1: Tension用promptは『上記と同じ意味』の参照先(3項目の定義)を逐語展開する。
# ============================================================
VOICE_FIELDS = ("leak_evidence_subject", "leak_numbers_foreground", "leak_narrator_analysis",
                "leak_unknowable_analysis", "leak_discovery_syntax", "leak_evidence_memorable", "leak_position_blur")
TENSION_FIELDS = ("leak_evidence_subject", "leak_numbers_foreground", "leak_discovery_syntax",
                  "leak_evidence_memorable", "leak_tension_reverts_to_research", "leak_binary_camp_split")

LEAKAGE_DEVELOPER_JA = (
    "あなたは「Voices(複数の人物がそれぞれ自分の言葉で語る)」型記事のVoiceセクションとTensionセクションを審査する、"
    "厳格なEditorial QA判定者です。それぞれのセクションが、実在しうる当事者(人)の経験・価値観・必要・心配として書かれているか、"
    "あるいは調査結果・データを整理して説明する文章、語り手の外側からの要約、Writer自身の解決策提案、単純な2対1分割に戻っていないかを、"
    "各セクション指定の基準についてPASS/FAILで判定してください。各基準についてPASSは『問題なし』、FAILは『その問題が実際に本文に存在する』"
    "ことを意味します。FAILの場合は、該当する原文の一節をquoted_evidenceにそのまま引用してください(複数箇所ある場合は代表的な1〜2箇所)。"
    "PASSの場合はquoted_evidenceを空文字列にしてください。")

_VOICE_ITEMS = """【Voice 1〜3に共通で適用する7項目】
- leak_evidence_subject: 文の主語が、調査・研究・データ・割合・報告になっている文が無い場合PASS
- leak_numbers_foreground: 具体的な数字が、その人物自身の経験に属する数値であり、かつその人の経験の描写より前面に出ていない場合PASS(数字が0個、またはその人物自身の経験に属する数字が1個だけ実感として自然に織り込まれている場合はPASS。調査・報告・研究等、本人の経験に属さない外部統計をVoice内で論証材料として使っている場合はFAIL)
- leak_narrator_analysis: 語り手が、Voiceの人物を外側から分析・要約していない場合PASS
- leak_unknowable_analysis: その人物自身が実際に考え・言いそうにない、外部の分析的視点を、その人のPerspectiveとして書いていない場合PASS
- leak_discovery_syntax: 「〜が明らかになった」「〜という傾向がある」のような、発見・傾向を報じる記事の文構造へ戻っていない場合PASS
- leak_evidence_memorable: 調査や事実よりも、その人物の経験・感情の方が記憶に残る書き方になっている場合PASS
- leak_position_blur: このVoiceが、自分の立場の中の迷い・葛藤(nuance)の範囲を超えて、他のVoice(相手側)が中心的に抱えている懸念・反論そのものを、自分の中心的な主張として代弁していない場合PASS(相手側の中心論点をこのVoiceが実質的に引き受けてしまっている場合はFAIL)

いずれのVoiceについても、他のVoiceと同一の基準で判定してください(特定の立場が抽象的な代弁者の解説になっている場合は、leak_evidence_subject/leak_narrator_analysis/leak_discovery_syntaxのいずれかでFAILとしてください)。
"""

# DEV版(M-1の欠陥を含む原文。DEV差分testの比較元として保持。Productionでは使わない)
_TENSION_ITEMS_DEV_ORIGINAL = """【最終パート(Tension)に適用する6項目】
- leak_evidence_subject / leak_discovery_syntax / leak_evidence_memorable: 上記と同じ意味(最終パート本文に対して判定)
- leak_numbers_foreground(最終パート用): 具体的な数字・比較結果が、3人の合理性を制約する力の描写より前面に出ていない場合PASS(1人の経験ではなく複数人の力関係を扱うため、Voice用の「本人の経験に属する数値」限定はここでは適用しない)
- leak_tension_reverts_to_research: 最終パートの中心が、3人がなぜ違う答えに至るのかの掘り下げになっており、調査・研究データそのものの説明・比較へ戻っていない場合PASS
- leak_binary_camp_split: 最終パートが3人を単純に対称的な2対1の陣営へ分けて描いていない場合PASS(分けている場合FAIL)
"""
_REF_LINE = "- leak_evidence_subject / leak_discovery_syntax / leak_evidence_memorable: 上記と同じ意味(最終パート本文に対して判定)\n"


def _voice_item_line(name: str) -> str:
    for ln in _VOICE_ITEMS.split("\n"):
        if ln.startswith(f"- {name}:"):
            return ln + "\n"
    raise YStop("LEAK_ITEM_DEF_MISSING", name)


# 『上記と同じ意味』の参照先(Voice用の定義)を、そのままの文言で展開する。展開以外の変更なし。
_REF_EXPANDED = (_voice_item_line("leak_evidence_subject") + _voice_item_line("leak_discovery_syntax") + _voice_item_line("leak_evidence_memorable")
                 + "(上の3項目は、最終パート本文に対して判定する)\n")
_TENSION_ITEMS = _TENSION_ITEMS_DEV_ORIGINAL.replace(_REF_LINE, _REF_EXPANDED)
assert _TENSION_ITEMS != _TENSION_ITEMS_DEV_ORIGINAL

_FOOT = "\nreasoningには、判定理由を1〜2文の日本語で書いてください。FAILの場合はquoted_evidenceに該当する原文を引用してください。PASSの場合quoted_evidenceは空文字列にしてください。\n"


def leak_sections_for(kind: str) -> dict:
    if kind == "voices":
        return {s: VOICE_FIELDS for s in SLOTS}
    if kind == "tension":
        return {"tension": TENSION_FIELDS}
    raise ValueError(kind)


def leak_schema_for(kind: str) -> dict:
    secs = leak_sections_for(kind)

    def item(fields):
        props = {f: {"type": "string", "enum": ["PASS", "FAIL"]} for f in fields}
        props["reasoning"] = {"type": "string"}
        props["quoted_evidence"] = {"type": "string"}
        return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}
    return {"name": f"family_y_persona_leakage_{kind}", "strict": True,
            "schema": {"type": "object", "properties": {k: item(v) for k, v in secs.items()}, "required": list(secs), "additionalProperties": False}}


def build_leak_prompt(kind: str, sections: dict, language_note: str = "日本語") -> str:
    if kind == "voices":
        head = (f"以下は、ある Voices型記事(3人の人物がそれぞれ一人称で語る)の3つのVoiceセクション本文です(本文の言語: {language_note})。"
                "それぞれについて、指定された項目を判定してください(それぞれPASS/FAIL)。\n\n" + _VOICE_ITEMS + _FOOT)
        body = "\n".join(f"【Voice {i + 1}本文】\n{sections[s]}\n" for i, s in enumerate(SLOTS))
    else:
        head = (f"以下は、ある Voices型記事(3人の人物がそれぞれ一人称で語った後の)最終パート[Tension]の本文です(本文の言語: {language_note})。"
                "指定された項目を判定してください(それぞれPASS/FAIL)。\n\n" + _TENSION_ITEMS + _FOOT)
        body = f"【最終パート(Tension)本文】\n{sections['tension']}\n"
    return head + "\n" + body


def run_leak(client, kind: str, sections: dict, *, stage: str, language_note: str = "日本語", guard=None) -> dict:
    prompt = build_leak_prompt(kind, sections, language_note)
    resp = chat(client, route_key="FAMILY_Y_LEAK_JUDGE", user=prompt, developer=LEAKAGE_DEVELOPER_JA, schema=leak_schema_for(kind), stage=stage, guard=guard)
    text = getattr(resp, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Leakage Check応答が空")
    parsed = json.loads(text)
    flagged = []
    for sec, fields in leak_sections_for(kind).items():
        it = parsed[sec]
        fails = [f for f in fields if it[f] == "FAIL"]
        if fails:
            flagged.append({"section": sec, "fail_fields": fails, "reasoning": it["reasoning"], "quoted_evidence": it["quoted_evidence"]})
    return {"kind": kind, "route_key": "FAMILY_Y_LEAK_JUDGE", "model": ROUTE["FAMILY_Y_LEAK_JUDGE"]["model"], "effort": ROUTE["FAMILY_Y_LEAK_JUDGE"]["effort"],
            "meta": resp_meta(resp), "prompt_sha256": w1.sha_text(prompt), "parsed": parsed,
            "flagged_items": flagged, "any_flagged": bool(flagged), "n_fail_fields": sum(len(x["fail_fields"]) for x in flagged)}


# Lead/人物紹介はTension専用2項目を適用外とする補助適用(承認済みGateの定義は変更しない)
LEADINTRO_NA_FIELDS = ("leak_tension_reverts_to_research", "leak_binary_camp_split")


# 委任_02C(Fable判断 OT-28, 2026-10-25): Lead/人物紹介はナレーター文。Voice用の leak_evidence_memorable(人物の経験・感情の具体性)は
# 性質上適合しないため非適用。承認済みGate定義の変更ではなく、Y固有の新パート(Lead/紹介)への適用範囲の確定。
LEADINTRO_NA_FIELDS_PROD = LEADINTRO_NA_FIELDS + ("leak_evidence_memorable",)


def split_leadintro_flags(chk: dict, na_fields: tuple = None) -> dict:
    na_fields = LEADINTRO_NA_FIELDS if na_fields is None else na_fields
    app, na = [], []
    for it in chk["flagged_items"]:
        ap = [x for x in it["fail_fields"] if x not in na_fields]
        nn = [x for x in it["fail_fields"] if x in na_fields]
        if ap:
            app.append({**it, "fail_fields": ap})
        if nn:
            na.append({**it, "fail_fields": nn})
    return {"applicable_flagged": app, "not_applicable_flagged": na}


# ============================================================
# 局所書換え
# ============================================================
FIELD_MEANING_JA = {
    "leak_evidence_subject": "調査・データ・割合などが文の主語になっている",
    "leak_numbers_foreground": "数字が本人の経験より前面に出ている/外部統計を論証に使っている",
    "leak_narrator_analysis": "人物を外側から分析・要約する語りになっている",
    "leak_unknowable_analysis": "その人物が言いそうにない分析的な視点を語っている",
    "leak_discovery_syntax": "発見・傾向を報じる記事のような文構造になっている",
    "leak_evidence_memorable": "経験や感情より、調査や事実の方が印象に残る",
    "leak_position_blur": "他の人物が中心に抱える懸念・反論を自分の主張として語っている",
    "leak_tension_reverts_to_research": "調査・データの説明や比較に戻っている",
    "leak_binary_camp_split": "3人を単純な2対1の陣営に分けて描いている",
}
REWRITE_DEVELOPER = "あなたは日本語ラジオ読み物の編集者です。指定された段落だけを、指摘された問題を直して書き換えます。他の段落には一切触れません。"
REWRITE_SCHEMA = {"name": "family_y_persona_rewrite", "strict": True,
                  "schema": {"type": "object", "additionalProperties": False, "required": ["rewrites"],
                             "properties": {"rewrites": {"type": "array", "items": {
                                 "type": "object", "additionalProperties": False, "required": ["section", "text"],
                                 "properties": {"section": {"type": "string"}, "text": {"type": "string"}}}}}}}


def build_voice_rewrite_prompt(texts: dict, flagged: list, shared_premise: str, personas_text: dict) -> str:
    """題材非依存のVoice書換えprompt(DEV build_voice_rewrite_prompt_plの移植。共通前提・Personaは入力から)。"""
    blocks = []
    for f in flagged:
        s = f["section"]
        probs = "\n".join(f"  - {x}: {FIELD_MEANING_JA.get(x, x)}" for x in f["fail_fields"])
        blocks.append(f"■ 書き換える語り: {s}\n現在の本文:\n{texts[s]}\n指摘された問題:\n{probs}\n指摘の理由: {f['reasoning']}\n問題の箇所: {f['quoted_evidence']}\n\n【この人物のPersona】\n{personas_text[s]}")
    others = "\n\n".join(f"[{s}]\n{t}" for s, t in texts.items())
    return f"""次のVoices型記事の、指定した語りだけを書き換えてください。他の語りは読み取り専用です。

【3人に共通の前提】{shared_premise}

【3人の語り全体(文脈。読み取り専用)】
{others}

{chr(10).join(blocks)}

【書き換えの規則】
- 指摘された問題だけを直し、その人物の一人称・話し方・語り出しの気分・冒頭3文以内の身元の手がかり・長さ(元の±20%)・話し言葉の常体を保つ。
- 指摘箇所が「調査・研究・報告が主語の文」「報じるような文構造」「外部統計を論証に使う文」の場合は、削除するか、Personaに許容事実があるときだけ本人が主語の伝聞・印象の1文(数字・調査名・年月なし、論証に使わない)にする。
- 人物が書けるのは本人が経験した個別の出来事だけ。頻度・傾向・原因の一般化を足さない。数字(算用数字・漢数字の数量表現)を使わない。
- 他の人物の中心の論点を自分の中心の主張にしない。迷いや複雑な気持ちは残してよい。
- 実在の人名・組織名・製品名を新しく出さない。Personaにない出来事を創作しない。
- 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。

出力はJSON: 書き換えた語りごとに {{"section": 語りの名前(例 voice_1), "text": 書き換え後の本文}}。指定した語り以外は出力しない。"""


def build_closing_rewrite_prompt(voices: dict, tension: str, flagged: list, selected: dict, rules_section: str) -> str:
    """M-2: 最終パートの局所書換えprompt。規則はPrompt 02の【最終パートの書き方】節を逐語使用(旧B骨格は使わない)。
    選定済みの切り口(new_view+evidence_quotes)を保たせ、指摘箇所だけを直させる。"""
    f = flagged[0]
    probs = "\n".join(f"  - {x}: {FIELD_MEANING_JA.get(x, x)}" for x in f["fail_fields"])
    vs = "\n\n".join(f"[{s}]\n{t}" for s, t in voices.items())
    quotes = "\n".join(f"  - {q}" for q in selected.get("evidence_quotes", []))
    return f"""次の最終パート(語り手の声)だけを、指摘された問題を直して書き換えてください。3人の語りは読み取り専用です。

【3人の語り(読み取り専用)】
{vs}

【この最終パートで示す切り口(書き換え後も必ず保つ。別の内容にすり替えない)】
新しい見方: {selected.get('new_view', '')}
根拠にしている語りの一節:
{quotes}

現在の最終パート:
{tension}
指摘された問題:
{probs}
指摘の理由: {f['reasoning']}
問題の箇所: {f['quoted_evidence']}

{rules_section}
- 上の書き方の規則に従ったうえで、指摘された問題の箇所を含む文だけを直す。それ以外の文は、一字も変えずそのまま残す(誰の言葉として述べているかも変えない)。切り口と最後の問いの内容も保つ。

出力はJSON: {{"section": "tension", "text": 書き換え後の本文}} を1件だけ含む rewrites 配列。"""


def _sentences(t: str) -> list:
    return [x for x in SENT_SPLIT_RE.split(t or "") if x.strip()]


def _overlaps(sent: str, quote: str, min_common: int = 12) -> bool:
    a, b = _squash(sent), _squash(quote)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    import difflib
    m = difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
    return m.size >= min_common


def rewrite_scope_check(before: str, after: str, quoted: list) -> dict:
    """M-2『指摘箇所だけ直す』の決定論確認。判定器が引用した箇所(quoted_evidence)を含む文以外は、書換え後も一字違わず同じ順序で残ること。
    引用箇所を本文中に特定できないときは検査できないため checked=False(記録のみ。実運用ではこの場合も書換え後に再判定+check_closingを通す)。"""
    bs = _sentences(before)
    target = {i for i, x in enumerate(bs) if any(_overlaps(x, q) for q in quoted if q)}
    if not target:
        return {"checked": False, "reason": "quote_not_located", "violations": []}
    after_s = _sentences(after)
    pos, bad = -1, []
    for i, x in enumerate(bs):
        if i in target:
            continue
        try:
            j = after_s.index(x, pos + 1)
        except ValueError:
            bad.append(i)
            continue
        pos = j
    return {"checked": True, "target_sentence_idx": sorted(target), "violations": bad}


def apply_rewrites(cur: dict, rewrites: list, flagged_keys: set, *, kind: str, first_persons: dict = None, quoted_by_section: dict = None) -> tuple:
    """局所書換えの決定論検査。tension=check_closing全項目+記号検査(M-2: 一人称検査だけでは通さない)。voices=1段落・一人称・ラベルなし。"""
    new = dict(cur)
    errors, applied, got, scope_checks = [], [], set(), {}
    for r in rewrites:
        s = r["section"]
        got.add(s)
        if s not in flagged_keys:
            errors.append(f"REWRITE_OUT_OF_SCOPE:{s}")
            continue
        try:
            final, sym = _fin(r["text"] or "")
        except w1.TagLeak as e:
            errors.append(f"REWRITE_TAG_LEAK:{s}:{e}")
            continue
        if not final or "\n" in final:
            errors.append(f"REWRITE_NOT_SINGLE_PARAGRAPH:{s}")
            continue
        if safety.symbol_gate_requires_stop(sym):
            errors.append(f"REWRITE_SYMBOL:{s}:{sym}")
            continue
        if kind == "tension":
            c = check_closing(final)
            if not c["ok"]:
                errors.append(f"REWRITE_CLOSING_CHECK:{c['violations']}")
                continue
            sc = rewrite_scope_check(cur[s], final, (quoted_by_section or {}).get(s, []))
            scope_checks[s] = sc
            if sc["violations"]:
                errors.append(f"REWRITE_SCOPE_VIOLATION:{s}:{sc['violations']}")
                continue
        else:
            fp = (first_persons or {}).get(s, "")
            if LABEL_START_RE.match(final) or (fp and fp not in final):
                errors.append(f"REWRITE_CONTRACT:{s}")
                continue
        new[s] = final
        applied.append(s)
    if got != flagged_keys:
        errors.append(f"REWRITE_SET_MISMATCH: got={sorted(got)} expected={sorted(flagged_keys)}")
    return new, {"applied": applied, "errors": errors, "scope_checks": scope_checks}


def run_gate(client, *, kind: str, stage: str, texts: dict, out_dir: str, voices_ctx: dict = None, selected: dict = None, rules_section: str = None,
             shared_premise: str = "", personas_text: dict = None, first_persons: dict = None, max_judgements: int = 3, allow_rewrite: bool = True,
             rejudge_without_rewrite: bool = False, guard=None) -> dict:
    """Leakage判定 → 局所書換え → 再判定(判定最大3回=初回+書換え2回)。残ればLEAKAGE_RESIDUAL_STOP(全文書き直しに戻さない)。
    judge/rewriteの履歴を gate_history として全保存。allow_rewrite=False は判定1回のみでFAILならSTOP(書換えない。再利用Voice用)。
    rejudge_without_rewrite=True(案B固定。USER_02 ②『既存の局所修正・再判定機構を利用』+承認本文の保護): 本文は書換えず、同一本文を最大max_judgements回判定する
    (初回PASSなら即終了。FAILは再判定し、3回判定後もFAILならLEAKAGE_RESIDUAL_STOP=公開しない)。書換えcall・本文変更は常に0。"""
    os.makedirs(out_dir, exist_ok=True)
    cur = dict(texts)
    history, status = [], None
    if rejudge_without_rewrite and allow_rewrite:
        raise YStop("GATE_MODE_CONFLICT", "rejudge_without_rewrite(案B固定=書換えなし)はallow_rewrite=Falseと併用する")
    for attempt in range(1, (max_judgements if (allow_rewrite or rejudge_without_rewrite) else 1) + 1):
        chk = run_leak(client, kind, cur, stage=f"{stage}_leak{attempt}", guard=guard)
        w1.wj(os.path.join(out_dir, f"leak_check_{attempt}.json"), chk)
        entry = {"attempt": attempt, "sha256": {k: w1.sha_text(v) for k, v in cur.items()}, "check": chk}
        history.append(entry)
        if not chk["any_flagged"]:
            status = "PASS"
            break
        if attempt == max_judgements or (not allow_rewrite and not rejudge_without_rewrite):
            status = "LEAKAGE_RESIDUAL_STOP"
            break
        if rejudge_without_rewrite:        # 書換えない: 同一本文を再判定(本文sha不変)
            continue
        keys = {f["section"] for f in chk["flagged_items"]}
        new = None
        for rw_try in (1, 2):
            if kind == "voices":
                prompt = build_voice_rewrite_prompt(cur, chk["flagged_items"], shared_premise, personas_text)
                rkey = "FAMILY_Y_VOICE_REWRITE"
            else:
                if selected is None or rules_section is None:
                    raise YStop("REWRITE_CONTEXT_MISSING", "Closing書換えには選定済み切り口とPrompt 02規則節が必要")
                prompt = build_closing_rewrite_prompt(voices_ctx, cur["tension"], chk["flagged_items"], selected, rules_section)
                rkey = "FAMILY_Y_CLOSING_REWRITE"
            resp = chat(client, route_key=rkey, user=prompt, developer=REWRITE_DEVELOPER, schema=REWRITE_SCHEMA,
                        stage=f"{stage}_rewrite{attempt}" + ("" if rw_try == 1 else "_retry"), guard=guard)
            rws = json.loads(resp.output_text)["rewrites"]
            quoted = {f["section"]: [f["quoted_evidence"]] for f in chk["flagged_items"]}
            new, det = apply_rewrites(cur, rws, keys, kind=kind, first_persons=first_persons, quoted_by_section=quoted)
            entry.setdefault("rewrite_calls", []).append({"try": rw_try, "route_key": rkey, "meta": resp_meta(resp), "prompt_sha256": w1.sha_text(prompt),
                                                          "details": det, "raw_rewrites": rws})
            if not det["errors"]:
                break
            new = None
        if new is None:
            w1.wj(os.path.join(out_dir, "gate_result.json"), {"status": "REWRITE_STOP", "history": history})
            raise YStop("REWRITE_STOP", f"{stage}: 局所書換えの決定論検査に2回失敗", history)
        for k in cur:
            if k not in keys and new[k] != cur[k]:
                raise YStop("REWRITE_BYTE_FIX_VIOLATION", f"{stage}: flag外の{k}が変化")
        entry["rewritten"] = sorted(keys)
        cur = new
    result = {"stage": stage, "kind": kind, "status": status, "n_judgements": len(history), "history": history,
              "first_judgement_flagged": history[0]["check"]["any_flagged"], "first_judgement_n_fail_fields": history[0]["check"]["n_fail_fields"],
              "final_sha256": {k: w1.sha_text(v) for k, v in cur.items()}, "rewritten": any("rewritten" in h for h in history)}
    w1.wj(os.path.join(out_dir, "gate_result.json"), result)
    if status == "PASS":
        w1.wj(os.path.join(out_dir, "final_texts.json"), cur)
    result["final_texts"] = cur
    return result


def load_gated_or_stop(gate_dir: str) -> dict:
    """Acceptance Gate: Gate結果がPASSでない本文は後続へ流さない。"""
    gp = os.path.join(gate_dir, "gate_result.json")
    if not os.path.exists(gp):
        raise YStop("GATE_RESULT_MISSING", f"{gate_dir}: gate_result.jsonがありません")
    st = _read_json(gp).get("status")
    if st != "PASS":
        raise YStop("ACCEPTANCE_GATE_NOT_PASSED", f"{gate_dir}: Gate status={st}")
    return _read_json(os.path.join(gate_dir, "final_texts.json"))


# ============================================================
# 案B固定registry(R-1)。slug+Theme Package sha+Voice R0 sha+承認ref。env/CLI/設定dictで他記事へ流用不可。
# ============================================================
_B_TEXT = ("午前を指定した人の家にも、不在票が入っていた。受け取り方を選べる人には、再配達の料金は工夫を促す合図になる。"
           "でも、受け取る人が払うだけでは、配達の遅れや日時の知らせ方は変わらない。送料をいくらにして、運ぶ人にいくら回すかも、"
           "受け取る人の手では変えられない。あなたが家にいられず困ったとき、受け取り方は選べたか、届く日時は分かっていたか？"
           "その困りごとは、受け取る人に料金を求めて変えられることだろうか？")
FIXED_CLOSING_REGISTRY = {
    "redelivery_fee": {
        "text": _B_TEXT,
        "text_sha256": "26745165e33be3ea5cf4548f365c6d145862d94ad0201cc69695c0a954800e71",
        "theme_package_sha256": "f0d0af367950735bb0264162d3cb45e3ef330759d8077e9d6f9bb5c3dadf0288",
        "voice_r0_sha256": "566ebd97d7ba1c81dcaa64305c8e5f02228a44cf1b5aa64f5f0105b1e5498a89",
        "approval_ref": "docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md §2-3 (案B「料金は何を動かせるか」を当該記事のみ個別正式採用)",
        "canonical_text_ref": "docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_REVISION_01/REVISION_SCRIPT_01.md パート5 案B",
        "approved_on": "2026-10-25",
        "scope": "redelivery_fee のみ(他記事への流用不可)",
        "prior_gate_record": "er110_output/family_y_redelivery_audio_01/revision_01/closing_B/gate/gate_result.json",
    },
}


def registry_sha() -> str:
    return w1.sha_text(json.dumps(FIXED_CLOSING_REGISTRY, ensure_ascii=False, sort_keys=True))


def fixed_closing_lookup(slug: str, theme_package_sha256: str, voice_r0_sha256: str):
    """registry外のslug→None(一般化方式へ)。registry内でsha不一致→STOP(Voice/Package変更時は注入しない)。"""
    ent = FIXED_CLOSING_REGISTRY.get(slug)
    if ent is None:
        return None
    if w1.sha_text(ent["text"]) != ent["text_sha256"]:
        raise YStop("FIXED_CLOSING_TEXT_SHA_MISMATCH", "registryの案B本文がsha定数と一致しません")
    if theme_package_sha256 != ent["theme_package_sha256"] or voice_r0_sha256 != ent["voice_r0_sha256"]:
        raise YStop("FIXED_CLOSING_PROVENANCE_MISMATCH",
                    f"{slug}: Theme Package/Voice R0がregistry登録時と異なる(案Bは登録時のVoiceに紐付く。注入せず停止) "
                    f"pkg={theme_package_sha256[:12]} r0={voice_r0_sha256[:12]}")
    return ent


def reusable_prior_gate(ent: dict, tension_text: str, current_prompt_sha: str, path: str = None):
    """既存PASS記録の再利用(来歴検査付き)。判定promptが今回のProduction版と同一shaの場合のみ再利用可(M-1で変わった場合は再判定)。"""
    p = path or ent.get("prior_gate_record")
    if not p or not os.path.exists(p):
        return None
    d = _read_json(p)
    ok = (d.get("status") == "PASS" and d.get("kind") == "tension" and d.get("n_judgements") == 1
          and d.get("final_sha256", {}).get("tension") == w1.sha_text(tension_text)
          and d["history"][0]["check"].get("prompt_sha256") == current_prompt_sha)
    return d if ok else None


# ============================================================
# Closing stage: 固定注入 or 一般化 → Gate → Gate後検査 → closing_record
# ============================================================
FIXED_CLOSING_MAX_JUDGEMENTS = 3      # 案B(USER_02 ②): 既存の再判定機構の上限(判定≤3回)。書換えは行わない


def _fixed_closing_judgement_summary(history: list) -> list:
    """案Bの各判定の結果(closing_recordへ残す): 試行番号・本文sha(不変)・flag有無・FAIL項目数・FAIL項目・判定model/prompt sha。"""
    return [{"attempt": h.get("attempt", i), "tension_sha256": (h.get("sha256") or {}).get("tension"), "any_flagged": h["check"].get("any_flagged"),
             "n_fail_fields": h["check"].get("n_fail_fields"),
             "fail_fields": sorted({ff for f in h["check"].get("flagged_items") or [] for ff in f["fail_fields"]}),
             "model": h["check"].get("model"), "effort": h["check"].get("effort"), "prompt_sha256": h["check"].get("prompt_sha256")} for i, h in enumerate(history, start=1)]


def produce_closing(client, *, slug: str, inp: dict, theme_package_sha256: str, voice_r0_sha256: str, out_dir: str, parts: dict = None, guard=None) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    voices = {s: inp["voices"][s] for s in SLOTS}
    ent = fixed_closing_lookup(slug, theme_package_sha256, voice_r0_sha256)
    gate_dir = os.path.join(out_dir, "gate")
    if ent is not None:
        text = ent["text"]
        c = check_closing(text)
        if not c["ok"]:
            raise YStop("FIXED_CLOSING_CHECK_FAILED", f"案Bがcheck_closingに不適合: {c['violations']}")
        prior = reusable_prior_gate(ent, text, w1.sha_text(build_leak_prompt("tension", {"tension": text})))
        if prior is not None:
            os.makedirs(gate_dir, exist_ok=True)
            w1.wj(os.path.join(gate_dir, "gate_result.json"), {**{k: prior[k] for k in ("stage", "kind", "status", "n_judgements", "final_sha256")}, "reused_from": ent["prior_gate_record"]})
            w1.wj(os.path.join(gate_dir, "final_texts.json"), {"tension": text})
            gate = {"status": "PASS", "n_judgements": 1, "rewritten": False, "source": "reused_prior_pass_record", "judgements": _fixed_closing_judgement_summary(prior["history"])}
        else:
            r = run_gate(client, kind="tension", stage="yp_closing_fixed", texts={"tension": text}, out_dir=gate_dir, voices_ctx=voices,
                         allow_rewrite=False, rejudge_without_rewrite=True, max_judgements=FIXED_CLOSING_MAX_JUDGEMENTS, guard=guard)
            judgements = _fixed_closing_judgement_summary(r["history"])
            if r["status"] != "PASS":
                w1.wj(os.path.join(out_dir, "closing_record.json"), {"source": "fixed_user_approved", "status": "FIXED_CLOSING_RESIDUAL_FAIL", "slug": slug,
                                                                      "text_sha256": ent["text_sha256"], "n_judgements": r["n_judgements"], "judgements": judgements,
                                                                      "rewritten": False, "gate_history_dir": gate_dir})
                raise YStop("FIXED_CLOSING_RESIDUAL_FAIL", f"案B(ユーザー承認本文)が{r['n_judgements']}回の再判定後もLeakage判定でFAIL。承認本文は書換えず、記事は公開せず停止"
                                                           "(承認本文とGateの衝突=ユーザー判断。Gate緩和・Prompt変更・本文変更はしない)", r["history"])
            gate = {"status": "PASS", "n_judgements": r["n_judgements"], "rewritten": False, "source": "judged_this_run", "judgements": judgements}
        final = load_gated_or_stop(gate_dir)["tension"]
        if final != text:
            raise YStop("FIXED_CLOSING_MUTATED", "固定注入本文が変更されている")
        rec = {"source": "fixed_user_approved", "general_method_used": False, "slug": slug, "approval_ref": ent["approval_ref"],
               "text_sha256": ent["text_sha256"], "registry_sha256": registry_sha(), "theme_package_sha256": theme_package_sha256,
               "voice_r0_sha256": voice_r0_sha256, "generation_sha256": ent["text_sha256"], "final_sha256": w1.sha_text(final),
               "rewritten": False, "gate": gate, "n_judgements": gate["n_judgements"], "judgements": gate["judgements"], "model_id": None, "routing_key": None, "prompt_sha256": None,
               "note": "案B固定注入。Prompt 02による一般化生成は使っていない(受入条件3は別記事の一般化経路evidenceで担保)。"
                       "Gate: 既存の再判定機構(判定<=3回・本文書換えなし・残存FAILは公開せずFIXED_CLOSING_RESIDUAL_FAIL=STOP。USER_02 ②)"}
    else:
        parts = parts or load_prompt_parts()
        g = generate_closing_general(client, inp, os.path.join(out_dir, "gen"), parts=parts, guard=guard)
        r = run_gate(client, kind="tension", stage="yp_closing", texts={"tension": g["text"]}, out_dir=gate_dir, voices_ctx=voices,
                     selected=g["selected"], rules_section=closing_rules_section(parts), guard=guard)
        if r["status"] != "PASS":
            w1.wj(os.path.join(out_dir, "closing_record.json"), {"source": "general_prompt_02", "status": "LEAKAGE_RESIDUAL_STOP", "generation_sha256": g["meta"]["gen_sha256"],
                                                                  "gate_history_dir": gate_dir})
            raise YStop("LEAKAGE_RESIDUAL_STOP", "Closingが3判定後もLeakage判定でFAIL。暫定版は公開せず、JA稿とFAIL記録を保存して停止", r["history"])
        final = load_gated_or_stop(gate_dir)["tension"]
        post = check_closing(final)
        w1.wj(os.path.join(out_dir, "post_gate_check.json"), post)
        if not post["ok"]:
            raise YStop("CLOSING_POST_GATE_STOP", f"Gate後の検査違反 {post['violations']}", post)
        k = ROUTE["FAMILY_Y_CLOSING_GENERATE"]
        rec = {"source": "general_prompt_02", "general_method_used": True, "slug": slug, "routing_key": "FAMILY_Y_CLOSING_GENERATE",
               "model_id": g["meta"]["calls"][-1]["model"], "expected_model": k["model"], "effort": k["effort"],
               "prompt_version": PROMPT_VERSION, "prompt_sha256": g["meta"]["prompt_sha256"], "user_sha256": g["meta"]["user_sha256"],
               "selected_id": g["meta"]["selected_id"], "gen_calls": len(g["meta"]["calls"]), "generation_sha256": g["meta"]["gen_sha256"],
               "final_sha256": w1.sha_text(final), "rewritten": r["rewritten"], "gate": {"status": r["status"], "n_judgements": r["n_judgements"]},
               "gate_history_dir": gate_dir, "theme_package_sha256": theme_package_sha256, "voice_r0_sha256": voice_r0_sha256}
    rec["entry"] = {"module": "er121_family_y_text_core_01.py", "status": STATUS, "module_sha256": hashlib.sha256(_read_bytes(__file__)).hexdigest()}
    w1.wj(os.path.join(out_dir, "closing_record.json"), rec)
    w1.wt(os.path.join(out_dir, "closing_final.txt"), final + "\n")
    return {"text": final, "record": rec}


# ============================================================
# 委任_02C: 記事全体(Theme Package → Voice生成 → Voice Gate → Lead → 人物紹介 → 補助Gate → Closing → 組立)
# 原則: DEV(Trial)の実在意見ベース方式(opinion_based_01/02/03)・委任_28のLead/人物紹介を「展開移植」する。Promptは er121_prompts/ のbyte一致ファイル+sha固定。
#       テーマ固有のハードコード(Sheet・World frame・人物名・題材専用の検査語)はTheme Package(データ)へ移し、コードに題材名を持たない。
#       DEVとの一致は er121_family_y_text_core_article_test_01.py で固定(Prompt/定義文/決定論検査/schemaの出力一致)。
# ============================================================
PROMPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er121_prompts")
ARTICLE_PROMPTS = {
    "voice": ("voice_generate_02.txt", "48645f1de5fcf6efd3a9d758a0120aa97b37f656a074c9ea0c31d95c51ffcd5e"),
    "lead": ("lead_generate_01.txt", "76282235c4f089c56318a635c4af1e45001795e7c8b956480bcfacb307edef21"),
    "intro": ("persona_intro_01.txt", "787794d635587053d20a411aa98da70b00dc7a45bc182f1483c1ae6a7267afc4"),
}


def load_article_prompt(kind: str, path: str = None) -> dict:
    """voice/lead/intro のPromptファイルを読み、sha不一致はSTOP(CRLF変換差はLF正規化で吸収)。"""
    fn, sha_expected = ARTICLE_PROMPTS[kind]
    raw = _read_bytes(path or os.path.join(PROMPT_DIR, fn)).replace(bytes([13, 10]), bytes([10]))
    m = re.match(r"=====DEVELOPER=====\n(.*?)\n=====USER=====\n(.*)\Z", raw.decode("utf-8"), re.S)
    if not m:
        raise YStop("PROMPT_FORMAT", f"{fn}: prompt fileの形式が想定と違います")
    sha = hashlib.sha256(raw).hexdigest()
    if sha != sha_expected:
        raise YStop("PROMPT_SHA_MISMATCH", f"{fn}: {sha} != {sha_expected}(承認済みPromptから変更されています)")
    return {"developer": m.group(1).strip(), "user_template": m.group(2).rstrip("\n"), "sha256": sha, "file": fn, "kind": kind}


# ---- 小道具(DEV pipeline の strict JSON schema helper と同一) ----
def _s_obj(**props) -> dict:
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


_S_STR = {"type": "string"}
_S_BOOL = {"type": "boolean"}
_S_INT = {"type": "integer"}


def _s_arr(item) -> dict:
    return {"type": "array", "items": item}


def _s_enum(*vals) -> dict:
    return {"type": "string", "enum": list(vals)}


def _s_schema(name: str, **props) -> dict:
    return {"name": name, "strict": True, "schema": _s_obj(**props)}


def _json_resp(resp, stage: str):
    text = getattr(resp, "output_text", None)
    if not text or not text.strip():
        raise YStop("EMPTY_RESPONSE", stage)
    return json.loads(text)


def _model_ids(calls: list) -> list:
    return sorted({str(c.get("model")) for c in calls if c.get("model")})


# ============================================================
# Theme Package(DEV THEME_DATA形式。データ。コードに題材固有の値を持たない)
# ============================================================
OPENING_GUIDE = {
    "出来事・場面の描写から": "語り出しは、経験欄にある出来事を1つ、事実のまま短く置くことから始める(新しい場面・人物・会話は足さない)。",
    "感情・本音の吐露から": "語り出しは、この争点についての自分の気持ち・本音をそのまま口にすることから始める。他の誰かの言い分を打ち消す言い方(〜と言うけど、〜じゃなくて)で始めない。",
    "主張・意見の表明から": "語り出しは、自分の考えを最初の1文ではっきり言うことから始める。他の誰かの言い分を打ち消す言い方で始めない。",
    "自分の状況・立場の描写から": "語り出しは、自分がどんな立場の人で、この争点で何を判断する側(される側)にいるかを、短く置くことから始める(新しい場面・出来事・会話は足さない)。他の誰かの言い分を打ち消す言い方で始めない。",
}
REQUIRED_SHEET_KEYS = ("gender", "age_label", "role_ja", "daily_life_ja", "contact_point_ja", "persona_sketch_ja", "stake_ja", "arc_ja", "experiences",
                       "troubles_ja", "wishes_honest_ja", "wishes_public_ja", "emotion_habit_ja", "values_ja", "interests_ja", "contradiction_or_weakness_ja",
                       "speech_style", "entry_mood_ja", "opening_type", "identity_cue_ja", "claim_core_ja", "known_fact_id", "known_fact_usage_ja")
REQUIRED_WORLD_KEYS = ("question_ja", "title_ja", "shared_premise_ja", "distinctions")
REQUIRED_SPEECH_KEYS = ("first_person", "sentence_length_pattern_ja", "question_back_frequency_ja", "assertion_or_hedging_ja", "vocabulary_layer_ja")


def validate_theme_package(tp: dict) -> list:
    """Theme Packageの整合確認(LLM 0)。違反コードのlistを返す(空=適合)。DEV opinion_based_03.validate_theme を包含し、Production入力として必須の欄を足す。"""
    errs = []
    if not isinstance(tp, dict):
        return ["PACKAGE_NOT_DICT"]
    for k in ("theme_id", "world_frame", "sheets", "who_ja"):
        if k not in tp:
            errs.append(f"PACKAGE_MISSING:{k}")
    if errs:
        return errs
    wf = tp["world_frame"]
    for k in REQUIRED_WORLD_KEYS:
        if not wf.get(k):
            errs.append(f"WORLD_FRAME_MISSING:{k}")
    for d in wf.get("distinctions") or []:
        if not d.get("term_ja") or not d.get("definition_ja"):
            errs.append("DISTINCTION_INCOMPLETE")
    if set(tp["sheets"]) != set(SLOTS) or set(tp["who_ja"]) != set(SLOTS):
        errs.append("THEME_SLOTS_MISMATCH")
        return errs
    terms = {d.get("term_ja") for d in wf.get("distinctions") or []}
    for slot in SLOTS:
        sh = tp["sheets"][slot]
        if not tp["who_ja"][slot]:
            errs.append(f"WHO_EMPTY:{slot}")
        miss = [k for k in REQUIRED_SHEET_KEYS if k not in sh]
        if miss:
            errs.append(f"SHEET_MISSING_KEYS:{slot}:{miss}")
            continue
        miss2 = [k for k in REQUIRED_SPEECH_KEYS if not sh["speech_style"].get(k)]
        if miss2:
            errs.append(f"SPEECH_STYLE_MISSING:{slot}:{miss2}")
        if sh["opening_type"] not in OPENING_GUIDE:
            errs.append(f"UNKNOWN_OPENING_TYPE:{slot}:{sh['opening_type']}")
        bad = [t for t in (sh.get("relevant_terms") or []) if t not in terms]
        if bad:
            errs.append(f"RELEVANT_TERM_NOT_DEFINED:{slot}:{bad}")
        ids = [x.get("id") for x in sh["experiences"]]
        if len(set(ids)) != len(ids) or not ids:
            errs.append(f"EXPERIENCE_IDS:{slot}")
        for x in sh["experiences"]:
            if x.get("kind") not in ("E", "O") or not x.get("source_ids") or not x.get("text_ja"):
                errs.append(f"EXPERIENCE_FIELDS:{slot}:{x.get('id')}")
    return errs


def load_theme_package(src, path: str = None) -> dict:
    """src=dict(解析済み)またはpath(str)。shaは案B registryと同じ算出法(ファイルbytesのsha256)。
    dictのみでpathが無い場合はcanonical JSONのshaで代用し sha_method に明記する(registry照合は一致しないため案Bは注入されない=fail-closed)。"""
    if isinstance(src, (str, os.PathLike)):
        path = os.fspath(src)
        raw = _read_json(path)
    else:
        raw = src
    if path:
        sha, method = hashlib.sha256(_read_bytes(path)).hexdigest(), "file_bytes"
        if not isinstance(src, (str, os.PathLike)) and _read_json(path) != raw:
            raise YStop("THEME_PACKAGE_PATH_MISMATCH", f"渡されたTheme Packageがpath({path})の内容と一致しません")
    else:
        sha, method = w1.sha_text(json.dumps(raw, ensure_ascii=False, sort_keys=True)), "canonical_json"
    errs = validate_theme_package(raw)
    if errs:
        raise YStop("THEME_PACKAGE_INVALID", f"{errs[:8]}", errs)
    restricted = set(raw.get("restricted_voice_ids") or [])
    sheets = json.loads(json.dumps(raw["sheets"], ensure_ascii=False))
    for sh in sheets.values():
        for x in sh["experiences"]:
            x["r2plus_only"] = bool(x["source_ids"]) and all(i in restricted for i in x["source_ids"])
    theme = {"theme_id": raw["theme_id"], "world_frame": json.loads(json.dumps(raw["world_frame"], ensure_ascii=False)), "sheets": sheets,
             "who_ja": dict(raw["who_ja"]), "restricted_voice_ids": sorted(restricted),
             "lead_premise_ja": raw.get("lead_premise_ja"), "lead_scope_lines": raw.get("lead_scope_lines"),
             "intro_checks": raw.get("intro_checks"), "source_dir": raw.get("source_dir")}
    return {"theme": theme, "raw": raw, "sha256": sha, "sha_method": method, "path": path}


def closing_input_from_theme(theme: dict, voices: dict) -> dict:
    wf, sh = theme["world_frame"], theme["sheets"]
    return normalize_input(wf["question_ja"], wf["shared_premise_ja"], wf["distinctions"],
                           [{"role": sh[s]["role_ja"], "sketch": sh[s]["persona_sketch_ja"], "stake": sh[s]["stake_ja"]} for s in SLOTS],
                           {s: voices[s] for s in SLOTS})


def voices_sha256(voices: dict) -> str:
    return w1.sha_text(json.dumps({s: voices[s] for s in SLOTS}, ensure_ascii=False, sort_keys=True))


# ============================================================
# Voice生成(実在意見ベース方式。DEV opinion_based_01/02/03 の展開移植)
# ============================================================
def render_persona(sheet: dict, who_ja: str) -> str:
    """DEV render_persona_ob2 と同一。人物像を先に置き、主張の芯を最後に置く。"""
    ss = sheet["speech_style"]
    ex = "\n".join(f"  - [{x['id']}] ({'出来事を含む声' if x['kind'] == 'E' else '意見の声'}) {x['text_ja']}" for x in sheet["experiences"])
    return (f"人物: {who_ja}(声は{sheet['gender']}の{sheet['age_label']}。一人称は「{ss['first_person']}」)\n"
            f"人物像(最初にここを踏まえる): {sheet['persona_sketch_ja']}\n役割・生活: {sheet['role_ja']}。{sheet['daily_life_ja']}\n"
            f"この争点との接点: {sheet['contact_point_ja']}\nこの人にとって切実なこと: {sheet['stake_ja']}\n困りごと: {sheet['troubles_ja']}\n"
            f"感情の癖: {sheet['emotion_habit_ja']}\n大切にしていること: {sheet['values_ja']}\n"
            f"経験・意見(ここにある内容だけを材料にする):\n{ex}\n"
            f"本音: {sheet['wishes_honest_ja']} / 建前: {sheet['wishes_public_ja']}\n利害: {sheet['interests_ja']}\n矛盾・弱さ: {sheet['contradiction_or_weakness_ja']}\n"
            f"話し方(英語にしても残る型):\n  - 文の長さ: {ss['sentence_length_pattern_ja']}\n  - 問い返し: {ss['question_back_frequency_ja']}\n  - 断言/留保: {ss['assertion_or_hedging_ja']}\n"
            f"  - 語彙の層: {ss['vocabulary_layer_ja']}\n語り出しの気分: {sheet['entry_mood_ja']}\n語りの流れ(目安。そのまま読み上げない): {sheet['arc_ja']}\n"
            f"この人が言いたいことの芯(方向性。そのまま読み上げず、本人の言葉で): {sheet['claim_core_ja']}")


def build_voice_prompt(wf: dict, sheet: dict, who_ja: str, parts: dict, emphasize: bool = False) -> str:
    """DEV build_voice_prompt_ob(+ob3の relevant_terms 絞り込み)と同一。区別の定義は Sheet の relevant_terms にある用語だけ(未指定は全件)。"""
    terms = sheet.get("relevant_terms")
    dist = [d for d in wf.get("distinctions", []) if terms is None or d["term_ja"] in terms]
    ds = "\n".join(f"- {d['term_ja']}: {d['definition_ja']}" for d in dist) or "(なし)"
    fact = "知っている事実はない。調査・統計・制度・他の国や組織の動きにはふれない(経験・意見の欄の内容だけで語る)。"
    opening = f"冒頭の型(指定): {sheet['opening_type']}。{OPENING_GUIDE[sheet['opening_type']]} "
    prompt = (parts["user_template"].replace("@@QUESTION@@", wf["question_ja"]).replace("@@PREMISE@@", wf["shared_premise_ja"]).replace("@@DISTINCTIONS@@", ds)
              .replace("@@SHEET@@", render_persona(sheet, who_ja)).replace("@@CUE@@", sheet["identity_cue_ja"]).replace("@@FACT@@", fact)
              .replace("@@OPENING@@", opening))
    if emphasize:
        prompt += (f"\n\n【今回の追加指示】この人の語り出しの気分「{sheet['entry_mood_ja']}」と冒頭の型「{sheet['opening_type']}」を、語り出し・展開・結びの全体に強く反映する。"
                   "他の人の語りと似た起伏・結びにならないよう、この人の話し方と気分から出てくる流れにする。出典ルール(欄にない出来事を作らない)は変えない。")
    if "@@" in prompt:
        raise YStop("PROMPT_PLACEHOLDER", "Voice promptに未置換のplaceholderが残っています")
    return prompt


NUM_RE = re.compile(r"[0-9０-９]+|[〇一二三四五六七八九十百千万]+(?:年|か月|ヶ月|カ月|ケ月|歳|人|回|割|パーセント|円|時間|分間?|日|週間?|台|件|校|度|本|倍)")
ROLE_WORD_RE = re.compile(r"(〜じゃ|ですわ|あたくし|でござる|のじゃ|だぜ|だわよ)")
INTERVIEW_RE = re.compile(r"(取材|話を聞い|聞いてみ|インタビュー|直撃|we talked|we spoke)", re.I)


def check_voice(text: str, first_person: str) -> list:
    """Voice構造契約(DEV check_voice_pl と同一。1段落・一人称・ラベルなし)。新しい品質Validatorではない。"""
    v = []
    t = (text or "").strip()
    if not t:
        v.append("EMPTY")
    if "\n" in t:
        v.append("MULTI_PARAGRAPH")
    if LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    if first_person not in t:
        v.append(f"NO_FIRST_PERSON:{first_person}")
    return v


def voice_monitors(text: str, first_person: str) -> dict:
    sents = [s for s in SENT_SPLIT_RE.split(text) if s.strip()]
    lens = [len(s) for s in sents]
    return {"note": "記録専用。合否に使わない", "chars": len(text), "sentences": len(sents), "mean_sentence_chars": round(sum(lens) / max(1, len(lens)), 1),
            "max_sentence_chars": max(lens) if lens else 0, "numbers": NUM_RE.findall(text), "exclamations": text.count("！") + text.count("!"),
            "question_marks": text.count("？") + text.count("?"), "role_words": ROLE_WORD_RE.findall(text), "interview_expr": INTERVIEW_RE.findall(text),
            "self_intro_pattern": bool(re.search(r"(者です|をしています|と申します|ものです)", "".join(sents[:3]))),
            "first_person_count": text.count(first_person), "ends_with_question": bool(re.search(r"[？?]\s*$", text.strip())),
            "last_sentence": sents[-1].strip() if sents else ""}


def generate_voice(client, theme: dict, slot: str, parts: dict, *, extra: str = "", emphasize: bool = False, tag: str = "", guard=None) -> dict:
    """Voice 1本を別callで生成。構造契約/記号QA違反は1回だけ再生成、残れば VOICE_CONTRACT_STOP(DEV generate_voice_ob と同じ機構)。"""
    wf, sheet = theme["world_frame"], theme["sheets"][slot]
    prompt = build_voice_prompt(wf, sheet, theme["who_ja"][slot], parts, emphasize) + extra
    fp = sheet["speech_style"]["first_person"]
    cur, hist, calls = prompt, [], []
    for k in (1, 2):
        stage = f"yp_voice_{slot}{tag}" + ("" if k == 1 else "_regen")
        resp = chat(client, route_key="FAMILY_Y_VOICE_GENERATE", user=cur, developer=parts["developer"], stage=stage, guard=guard)
        raw = (getattr(resp, "output_text", None) or "").strip()
        calls.append({**resp_meta(resp), "stage": stage, "prompt_sha256": w1.sha_text(cur)})
        probs = []
        try:
            final, sym = _fin(raw)
            probs += check_voice(final, fp)
            if safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
            if {t for m in w1.TAG_RE.finditer(raw) for t in w1.tag_ids(m.group(0))}:
                probs.append("UNEXPECTED_FACT_TAG")
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK:{e}"]
        hist.append(probs)
        if not probs:
            return {"slot": slot, "text": final, "raw": raw, "calls": calls, "problems_per_try": hist, "monitors": voice_monitors(final, fp),
                    "prompt_sha256": w1.sha_text(prompt), "prompt": prompt}
        if k == 1:
            cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {x}" for x in probs)
    raise YStop("VOICE_CONTRACT_STOP", f"{slot}: 再生成後も契約違反 {hist[-1]}", hist)


# ---- 出典対応の付番+機械照合(DEV opinion_based_01 OF-Y6-07。luna。UNMAPPEDのVoiceだけ1回再生成。再生成後の残りは記録のみ) ----
EVENT_WORD_RE = re.compile(r"(この前|このあいだ|この間|先日|昨日|さっき|あの時|あのとき|ある日|あるとき|言われ|頼まれ|怒られ|叱られ|聞かれ|見られた|取り上げ|してくれ|してきた|してた|しちゃった|だった|でした|ていた|ました)")
PAST_END_RE = re.compile(r"た(?:[。？！]|$)")
PAST_EXCLUDE_RE = re.compile(r"(思った|感じた|気がした|分かった|わかった|知った|考えた|気づいた|気付いた|なった|だった。?$)")
HYPO_RE = re.compile(r"(もし|たら|なら(?!ない)|れば|かもしれ|かも|だろう|はず|べき|ほうがいい|ありそう|ないと)")
SUPP_KINDS = ("口調・言い回し", "感情の言い方", "年代・立場の手がかり", "仮定・意見の言い換え", "聞き手への呼びかけ・つなぎ", "なし")
MAP_DEVELOPER = "あなたは、語りの各文が、与えられた根拠メモのどの項目に基づくかを付番する検査者です。内容の良し悪しは評価せず、付番だけを行います。"
SCHEMA_MAP = _s_schema("yob_provenance_map", items=_s_arr(_s_obj(idx=_S_INT, source_ids=_s_arr(_S_STR), supplement_kinds=_s_arr(_s_enum(*SUPP_KINDS)), is_event_claim=_S_BOOL, note_ja=_S_STR)))


def event_like(sentence: str) -> bool:
    if EVENT_WORD_RE.search(sentence):
        return True
    return bool(PAST_END_RE.search(sentence) and not PAST_EXCLUDE_RE.search(sentence))


def split_sentences(text: str) -> list:
    return [s.strip() for s in SENT_SPLIT_RE.split(text) if s.strip()]


def build_map_prompt(sheet: dict, sentences: list) -> str:
    memo = "\n".join(f"- [{x['id']}] ({'出来事を含む声' if x['kind'] == 'E' else '意見の声'}) {x['text_ja']}" for x in sheet["experiences"])
    sup = "\n".join(f"- {k}" for k in SUPP_KINDS if k != "なし")
    body = "\n".join(f"{i}: {s}" for i, s in enumerate(sentences))
    return f"""次の語り(一人称)の各文について、根拠メモのどの項目に基づくかを付番してください。

【根拠メモ(この人物が語ってよい経験・意見)】
{memo}

【補った表現の種別(出典ではなく編集で足してよい範囲。人物・会話・出来事は含まない)】
{sup}

【語り(文ごとに番号付き)】
{body}

【付番の規則】
- すべての文を、idx=0から順に1件ずつ出力する。
- source_ids: その文の内容が基づく根拠メモのID(複数可)。根拠メモにない出来事・場面・人物・会話・数量を含む文には、無理にIDを付けず空配列にし、is_event_claim を true にする。
- supplement_kinds: 口調・感情の言い方・つなぎなど、出典を持たない補いが文に含まれるときに種別を付ける。補いがなければ「なし」だけを入れる。
- note_ja: 判断の根拠を一言で。"""


def check_mapping(slot: str, sheet: dict, sentences: list, parsed: dict) -> dict:
    """luna付番を機械照合。UNMAPPED = (許可リスト外のID) or (IDも補い種別もない) or (出来事らしい文でE-IDがなく仮定・意見の形でもない) or (is_event_claimでIDなし) or (付番漏れ)。"""
    allow = {x["id"] for x in sheet["experiences"]}
    ev = {x["id"] for x in sheet["experiences"] if x["kind"] == "E"}
    r2 = {x["id"] for x in sheet["experiences"] if x.get("r2plus_only")}
    by = {it["idx"]: it for it in parsed.get("items", [])}
    rows, unmapped, r2_rows = [], [], []
    for i, s in enumerate(sentences):
        it = by.get(i)
        reasons = []
        if it is None:
            ids, supp, claim = [], [], False
            reasons.append("NOT_LABELED")
        else:
            ids, supp, claim = list(it["source_ids"]), [k for k in it["supplement_kinds"] if k != "なし"], bool(it["is_event_claim"])
        bad = [x for x in ids if x not in allow]
        if bad:
            reasons.append("ID_NOT_IN_ALLOWLIST:" + ",".join(bad))
        ev_like = event_like(s)
        if it is not None and not ids and not supp:
            reasons.append("NO_ID_NO_SUPPLEMENT")
        if claim and not ids:
            reasons.append("EVENT_CLAIM_WITHOUT_ID")
        if ev_like and not (set(ids) & ev) and not HYPO_RE.search(s):
            reasons.append("EVENT_LIKE_WITHOUT_E_ID")
        verdict = "UNMAPPED" if reasons else ("補った表現のみ" if not ids else "OK")
        rows.append({"idx": i, "text": s, "source_ids": ids, "supplement_kinds": supp, "is_event_claim": claim, "event_like": ev_like, "reasons": reasons, "verdict": verdict,
                     "note": (it or {}).get("note_ja", "")})
        if reasons:
            unmapped.append(i)
        if ids and all(x in r2 for x in ids):
            r2_rows.append(i)
    return {"slot": slot, "n_sentences": len(sentences), "n_unmapped": len(unmapped), "unmapped_idx": unmapped, "r2plus_only_idx": r2_rows, "rows": rows}


def map_voice(client, theme: dict, slot: str, text: str, stage: str, guard=None) -> dict:
    sents = split_sentences(text)
    resp = chat(client, route_key="FAMILY_Y_VOICE_PROVENANCE_MAP", user=build_map_prompt(theme["sheets"][slot], sents), developer=MAP_DEVELOPER,
                schema=SCHEMA_MAP, stage=f"yp_vmap_{slot}_{stage}", guard=guard)
    res = check_mapping(slot, theme["sheets"][slot], sents, _json_resp(resp, f"map_{slot}_{stage}"))
    res["meta"], res["stage"] = resp_meta(resp), stage
    return res


def unmapped_extra(mp: dict) -> str:
    bad = "\n".join(f"- {mp['rows'][i]['text']}(理由: {','.join(mp['rows'][i]['reasons'])})" for i in mp["unmapped_idx"])
    return ("\n\n【前回の出力の問題(今回は避けてください)】\n次の文は、「経験・意見」欄にない出来事・場面・人物・会話を含むか、欄の項目に対応づけられませんでした。\n" + bad +
            "\n「経験・意見」欄にある内容だけで語り直してください。欄に出来事がない場合は、出来事を作らず、仮定・意見・感想の形にしてください。")


# ---- 構造タグ(DEV persona_pipeline OF-Y5-06。luna。発火なら該当1本だけ1回再生成。記録のみで合否に使わない) ----
OPENING_TYPES = ("自分の状況・立場の描写から", "出来事・場面の描写から", "感情・本音の吐露から", "主張・意見の表明から", "問いかけから", "言い訳・弁明から", "その他")
DEVELOPMENT_TYPES = ("主張から具体例へ", "具体例から感情を経て主張へ", "感情から具体例へ", "経験の時系列", "問いを重ねて考える", "自分への突っ込みと本音を行き来する", "その他")
CLOSING_TYPES = ("自嘲・告白で締める", "問いを残して締める", "約束・要求で締める", "主張を言い切って締める", "場面・情景で締める", "迷いを残して締める", "その他")
STRUCTURE_DEVELOPER = "あなたは、語りの構造を分類する判定者です。各語りの内容の良し悪しは評価せず、与えられたラベル集合から構造の型を選びます。"
SCHEMA_STRUCTURE = _s_schema("yp_structure_tags", voices=_s_arr(_s_obj(voice=_s_enum(*SLOTS), opening_type=_s_enum(*OPENING_TYPES), development_type=_s_enum(*DEVELOPMENT_TYPES),
                                                                       closing_type=_s_enum(*CLOSING_TYPES), evidence_ja=_S_STR)))


def build_structure_prompt(texts: dict) -> str:
    body = "\n\n".join(f"【{s}】\n{texts[s]}" for s in SLOTS)
    return (f"次の3つの語り(それぞれ別の人物の一人称)について、構造の型を分類してください。\n\n{body}\n\n"
            f"opening_type(冒頭の型)の選択肢: {' / '.join(OPENING_TYPES)}\ndevelopment_type(展開の型)の選択肢: {' / '.join(DEVELOPMENT_TYPES)}\n"
            f"closing_type(締めの型)の選択肢: {' / '.join(CLOSING_TYPES)}\nevidence_ja に、各分類の根拠となる冒頭・締めの短い引用を書く。")


def structure_fire(tags: dict) -> dict:
    """発火条件=『展開の型が一致 かつ 冒頭型か締め型のどちらかが一致』(『その他』同士は一致としない)。発火したら最初の該当ペアの後の方のVoice1本だけを再生成対象にする。"""
    pairs = []
    for a, b in itertools.combinations(SLOTS, 2):
        ta, tb = tags[a], tags[b]

        def same(k):
            return ta[k] == tb[k] and ta[k] != "その他"
        dev, op, cl = same("development_type"), same("opening_type"), same("closing_type")
        if dev and (op or cl):
            pairs.append({"pair": [a, b], "development": dev, "opening": op, "closing": cl})
    return {"fired": bool(pairs), "pairs": pairs, "regenerate_slot": pairs[0]["pair"][1] if pairs else None}


def tag_structure(client, texts: dict, stage: str, guard=None) -> dict:
    resp = chat(client, route_key="FAMILY_Y_VOICE_STRUCTURE_TAG", user=build_structure_prompt(texts), developer=STRUCTURE_DEVELOPER, schema=SCHEMA_STRUCTURE,
                stage=f"yp_{stage}", guard=guard)
    tags = {v["voice"]: v for v in _json_resp(resp, stage)["voices"]}
    if set(tags) != set(SLOTS):
        raise YStop("STRUCTURE_TAG_INCOMPLETE", str(sorted(tags)))
    return {"tags": tags, "fire": structure_fire(tags), "meta": resp_meta(resp)}


# ---- 同一主張の反復検出(DEV opinion_based_02。記録専用) ----
_REP_STRIP_RE = re.compile(r"[、。？！\s]")
_REP_FUNC_CHARS = set("はがをにのでともやてたしだねよかなへ")
REPEAT_OVERLAP_THRESHOLD = 0.30
CONTRAST_RE = re.compile(r"(でも|けど|けれど|ただ|それでも|いや、|とはいえ|かといって|だからって)")


def _rep_norm(s: str) -> str:
    return "".join(c for c in _REP_STRIP_RE.sub("", s) if c not in _REP_FUNC_CHARS)


def _rep_bigrams(s: str) -> set:
    return {s[i:i + 2] for i in range(len(s) - 1)}


def repetition_report(text: str, threshold: float = REPEAT_OVERLAP_THRESHOLD) -> dict:
    sents = split_sentences(text)
    grams = [_rep_bigrams(_rep_norm(s)) for s in sents]
    pairs = []
    for i in range(len(sents)):
        for j in range(i + 1, len(sents)):
            a, b = grams[i], grams[j]
            if len(a) < 4 or len(b) < 4:
                continue
            ov = len(a & b) / min(len(a), len(b))
            if ov >= threshold:
                pairs.append({"i": i, "j": j, "overlap": round(ov, 2), "a": sents[i], "b": sents[j]})
    return {"note": "記録専用。合否に使わない。1サンプルで較正した簡易判定(目視確認なしに結論に使わない)", "threshold": threshold, "n_sentences": len(sents),
            "n_repeat_pairs": len(pairs), "repeat_pairs": pairs, "contrast_turns": len(CONTRAST_RE.findall(text)),
            "last_vs_first_echo": bool(grams and len(grams[0]) >= 4 and len(grams[-1]) >= 4 and len(grams[0] & grams[-1]) / min(len(grams[0]), len(grams[-1])) >= threshold)}


# ============================================================
# Lead(委任_28 `generate_lead` の展開移植。AI編集説明なし。テーマ固有値はTheme Packageから)
# ============================================================
LEAD_RANGE = (115, 160)
INTRO_RANGE = (32, 62)
PREVIEW_RE = re.compile(r"(三人|三つの声|3人)")
IOL_RE = re.compile(r"(In one line|IN ONE LINE|ひとこと)", re.I)


def check_lead(text: str) -> dict:
    """Lead決定論検査(DEV rev.check_lead と同一。字数115〜160・一人称なし・AI編集説明なし・三人の予告あり等)。"""
    v = []
    t = (text or "").strip()
    if not t:
        v.append("EMPTY")
    if "\n" in t:
        v.append("MULTI_PARAGRAPH")
    if FIRST_PERSON_RE.search(t):
        v.append("HAS_FIRST_PERSON")
    if LEAD_BAD_RE.search(t):
        v.append("HAS_INTERVIEWER_EXPRESSION")
    if LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    if DIGIT_RE.search(t):
        v.append("HAS_DIGIT")
    if DESU_MASU_RE.search(t):
        v.append("DESU_MASU")
    if AI_ANNOUNCE_RE.search(t):
        v.append("HAS_AI_EDIT_ANNOUNCEMENT")
    if not PREVIEW_RE.search(t):
        v.append("NO_PREVIEW_OF_THREE_VOICES")
    if not (LEAD_RANGE[0] <= len(t) <= LEAD_RANGE[1]):
        v.append(f"LENGTH={len(t)}")
    if any(len(s) > MAX_SENT for s in SENT_SPLIT_RE.split(t) if s.strip()):
        v.append("SENTENCE_TOO_LONG")
    return {"ok": not v, "violations": v}


def lead_inputs(theme: dict) -> tuple:
    """Leadが使ってよい『テーマ』と『テーマの範囲』。Theme Packageの lead_premise_ja / lead_scope_lines があればそれ、無ければ
    争点の問い(question_ja)と用語の意味(distinctions)から機械的に作る(新しい事実を足さない)。"""
    wf = theme["world_frame"]
    premise = theme.get("lead_premise_ja") or wf["question_ja"]
    scope = list(theme.get("lead_scope_lines") or [f"{d['term_ja']}とは、{d['definition_ja']}" for d in wf["distinctions"]])
    src = "package" if (theme.get("lead_premise_ja") and theme.get("lead_scope_lines")) else "derived_from_world_frame"
    return premise, scope, src


def build_lead_prompt(premise: str, scope_lines: list, parts: dict) -> str:
    return parts["user_template"].replace("@@PREMISE@@", premise).replace("@@SCOPE@@", "\n".join(f"- {x}" for x in scope_lines))


def _gen_checked(client, *, route_key: str, prompt: str, developer: str, stage: str, checker, out_dir: str, name: str, guard=None) -> dict:
    """1 call(+契約違反時のみ再生成1回。DEV rev._gen_single と同方式)。残れば {NAME}_CONTRACT_STOP。"""
    os.makedirs(out_dir, exist_ok=True)
    w1.wt(os.path.join(out_dir, f"{name}_prompt.txt"), prompt)
    calls, hist, cur = [], [], prompt
    for k in (1, 2):
        st = stage + ("" if k == 1 else "_regen")
        resp = chat(client, route_key=route_key, user=cur, developer=developer, stage=st, guard=guard)
        raw = (getattr(resp, "output_text", None) or "").strip()
        calls.append({**resp_meta(resp), "stage": st, "prompt_sha256": w1.sha_text(cur)})
        w1.wt(os.path.join(out_dir, f"{name}_raw_try{k}.txt"), raw)
        probs = []
        try:
            final, sym = _fin(raw)
            probs += checker(final)["violations"]
            if safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK:{e}"]
        hist.append(probs)
        if not probs:
            meta = {"calls": calls, "problems_per_try": hist, "sha256": w1.sha_text(final), "chars": len(final), "prompt_sha256": w1.sha_text(prompt)}
            w1.wt(os.path.join(out_dir, f"{name}.txt"), final + "\n")
            w1.wj(os.path.join(out_dir, f"{name}_meta.json"), meta)
            return {"text": final, "meta": meta}
        if k == 1:
            cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {x}" for x in probs)
    w1.wj(os.path.join(out_dir, f"{name}_meta.json"), {"calls": calls, "problems_per_try": hist, "status": "CONTRACT_STOP"})
    raise YStop(f"{name.upper()}_CONTRACT_STOP", f"{name}: 再生成後も契約違反 {hist[-1]}", hist)


def generate_lead(client, theme: dict, out_dir: str, parts: dict, guard=None) -> dict:
    premise, scope, src = lead_inputs(theme)
    r = _gen_checked(client, route_key="FAMILY_Y_LEAD_GENERATE", prompt=build_lead_prompt(premise, scope, parts), developer=parts["developer"],
                     stage="yp_lead", checker=check_lead, out_dir=out_dir, name="lead", guard=guard)
    r["inputs_source"] = src
    return r


# ============================================================
# 人物紹介(委任_28 `generate_intros` の展開移植。3本を1 callで。本人の語りを読み取り専用で渡し、先取りを決定論で検査)
#   題材固有だった検査語(役割語の正規表現・具体物の語・主張先取り語)はTheme Package(intro_checks)へ。無ければ下の汎用導出(記録に mode を残す)。
# ============================================================
INTRO_SCHEMA = {"name": "family_y_voice_intros", "strict": True,
                "schema": {"type": "object", "additionalProperties": False, "required": list(SLOTS), "properties": {s: {"type": "string"} for s in SLOTS}}}
GENERIC_CLAIM_PATTERN = r"(賛成|反対|べきだ|べきでない|べきではない)"
_CJK_NON_HIRA = re.compile(r"[^぀-ゟ]")


def _norm_ja(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[\s　「」『』、。，．,.！？!?…・\-ー〜~()（）\[\]【】]", "", s)


def _shingles(s: str, n: int) -> set:
    t = _norm_ja(s)
    return {t[i:i + n] for i in range(len(t) - n + 1)}


def intro_spec(theme: dict, explicit: dict = None) -> dict:
    """人物紹介の検査仕様。explicit(再利用manifest)> theme['intro_checks'] > 汎用導出。"""
    ic = explicit or theme.get("intro_checks")
    wf, sheets = theme["world_frame"], theme["sheets"]
    if ic:
        for k in ("role_patterns", "object_words", "claim_pattern", "claim_words_prompt", "object_examples_prompt"):
            if k not in ic:
                raise YStop("THEME_PACKAGE_INVALID", f"intro_checks.{k}がありません")
        if set(ic["role_patterns"]) != set(SLOTS):
            raise YStop("THEME_PACKAGE_INVALID", "intro_checks.role_patternsが3 slotではありません")
        return {"mode": "explicit", "role_re": {s: re.compile(ic["role_patterns"][s]) for s in SLOTS}, "role_text": {s: sheets[s]["role_ja"] + " " + theme["who_ja"][s] for s in SLOTS},
                "object_words": tuple(ic["object_words"]), "claim_re": re.compile(ic["claim_pattern"]),
                "claim_prompt": ic["claim_words_prompt"], "object_prompt": ic["object_examples_prompt"]}
    objs = tuple(d["term_ja"] for d in wf["distinctions"] if d["term_ja"] not in wf["question_ja"])
    return {"mode": "derived", "role_re": None, "role_text": {s: sheets[s]["role_ja"] + " " + theme["who_ja"][s] for s in SLOTS}, "object_words": objs,
            "claim_re": re.compile(GENERIC_CLAIM_PATTERN), "claim_prompt": "「賛成」「反対」", "object_prompt": "・".join(objs) if objs else "その争点に関わる物や制度の名前"}


def _role_hint_match(role_text: str, intro: str) -> bool:
    for i in range(len(role_text) - 1):
        bg = role_text[i:i + 2]
        if bg in intro and _CJK_NON_HIRA.search(bg):
            return True
    return False


def check_intro(text: str, slot: str, voice_body: str, spec: dict) -> dict:
    """人物紹介の決定論検査(DEV rev.check_intro の移植。主張先取り語の禁止・本人語りとの10字連続一致なし・字数ほか)。"""
    v = []
    t = (text or "").strip()
    if not t:
        return {"ok": False, "violations": ["EMPTY"]}
    if "\n" in t:
        v.append("MULTI_LINE")
    if FIRST_PERSON_RE.search(t):
        v.append("HAS_FIRST_PERSON")
    if LEAD_BAD_RE.search(t):
        v.append("HAS_INTERVIEWER_EXPRESSION")
    if LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    if DIGIT_RE.search(t):
        v.append("HAS_DIGIT")
    if DESU_MASU_RE.search(t):
        v.append("DESU_MASU")
    if AI_ANNOUNCE_RE.search(t):
        v.append("HAS_AI_EDIT_ANNOUNCEMENT")
    if spec["claim_re"].search(t):
        v.append("FORESHADOWS_CLAIM_WORD")
    role_ok = bool(spec["role_re"][slot].search(t)) if spec["role_re"] else _role_hint_match(spec["role_text"][slot], t)
    if not role_ok:
        v.append("ROLE_NOT_CONVEYED")
    for w in spec["object_words"]:
        if w in t and w not in voice_body:
            v.append(f"INTRO_OBJECT_NOT_IN_OWN_VOICE:{w}")
    if _shingles(t, 10) & _shingles(voice_body, 10):
        v.append("COPIES_VOICE_BODY_10CHARS")
    if not (INTRO_RANGE[0] <= len(t) <= INTRO_RANGE[1]):
        v.append(f"LENGTH={len(t)}")
    return {"ok": not v, "violations": v}


def person_block(slot: str, sheets: dict, voices: dict) -> str:
    i = SLOTS.index(slot) + 1
    sh = sheets[slot]
    daily = re.sub(r"(\(出来事は経験欄にあるものだけ\)|（出来事は経験欄にあるものだけ）)", "", sh["daily_life_ja"]).strip()
    cue = re.sub(r"\(.*?\)", "", sh["identity_cue_ja"]).strip()
    return (f"【人物{i}】{sh['role_ja']}\n  暮らしの様子: {daily}\n  人物の出し方の目安: {cue}\n"
            f"  本人の語り(整合を取るための読み取り専用。内容を先取りしない): {voices[slot]}")


def build_intro_prompt(theme: dict, premise: str, voices: dict, parts: dict, spec: dict) -> str:
    persons = "\n\n".join(person_block(s, theme["sheets"], voices) for s in SLOTS)
    return (parts["user_template"].replace("@@PREMISE@@", premise).replace("@@PERSONS@@", persons)
            .replace("@@CLAIM_WORDS@@", spec["claim_prompt"]).replace("@@OBJECT_EXAMPLES@@", spec["object_prompt"]))


def generate_intros(client, theme: dict, voices: dict, out_dir: str, parts: dict, spec: dict, guard=None) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    premise, _scope, _src = lead_inputs(theme)
    prompt = build_intro_prompt(theme, premise, voices, parts, spec)
    w1.wt(os.path.join(out_dir, "intro_prompt.txt"), prompt)
    calls, hist, cur = [], [], prompt
    for k in (1, 2):
        st = "yp_intro" + ("" if k == 1 else "_regen")
        resp = chat(client, route_key="FAMILY_Y_PERSONA_INTRO", user=cur, developer=parts["developer"], schema=INTRO_SCHEMA, stage=st, guard=guard)
        raw = _json_resp(resp, st)
        calls.append({**resp_meta(resp), "stage": st, "prompt_sha256": w1.sha_text(cur)})
        w1.wj(os.path.join(out_dir, f"intro_raw_try{k}.json"), raw)
        probs, finals = [], {}
        for s in SLOTS:
            try:
                f, sym = _fin(raw.get(s, ""))
                finals[s] = f
                probs += [f"{s}:{x}" for x in check_intro(f, s, voices[s], spec)["violations"]]
                if safety.symbol_gate_requires_stop(sym):
                    probs.append(f"{s}:SYMBOL:{sym}")
            except w1.TagLeak as e:
                finals[s] = ""
                probs.append(f"{s}:TAG_LEAK:{e}")
        hist.append(probs)
        if not probs:
            meta = {"calls": calls, "problems_per_try": hist, "chars": {s: len(finals[s]) for s in SLOTS}, "prompt_sha256": w1.sha_text(prompt), "check_mode": spec["mode"]}
            w1.wj(os.path.join(out_dir, "intros.json"), finals)
            w1.wj(os.path.join(out_dir, "intro_meta.json"), meta)
            return {"intros": finals, "meta": meta}
        if k == 1:
            cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {x}" for x in probs)
    w1.wj(os.path.join(out_dir, "intro_meta.json"), {"calls": calls, "problems_per_try": hist, "status": "CONTRACT_STOP"})
    raise YStop("INTRO_CONTRACT_STOP", f"intro: 再生成後も契約違反 {hist[-1]}", hist)


def run_leadintro_gate(client, lead: str, intros: dict, out_dir: str, guard=None) -> dict:
    """Lead+人物紹介(ナレーター文)へのGate補助適用。既存Leakage判定(Tension項目セット)を1回当てる。適用範囲は LEADINTRO_NA_FIELDS_PROD(OT-28)。
    適用対象項目にFAILがあれば LEADINTRO_LEAKAGE_FLAGGED でSTOP(本文を手で直さない。再生成は呼出側の明示操作)。"""
    os.makedirs(out_dir, exist_ok=True)
    comb = "\n".join([lead] + [intros[s] for s in SLOTS])
    chk = run_leak(client, "tension", {"tension": comb}, stage="yp_leadintro_leak", guard=guard)
    res = split_leadintro_flags(chk, LEADINTRO_NA_FIELDS_PROD)
    rec = {"text_sha256": w1.sha_text(comb), "na_fields": list(LEADINTRO_NA_FIELDS_PROD), "applicable_flagged": res["applicable_flagged"],
           "not_applicable_flagged": res["not_applicable_flagged"], "any_flagged_raw": chk["any_flagged"], "prompt_sha256": chk["prompt_sha256"],
           "model": chk["model"], "meta": chk["meta"], "status": "PASS" if not res["applicable_flagged"] else "LEADINTRO_LEAKAGE_FLAGGED"}
    w1.wj(os.path.join(out_dir, "leak_check.json"), {**chk, "note": "Tension項目セットをLead+人物紹介(ナレーター文)へ補助適用"})
    w1.wj(os.path.join(out_dir, "applicable_result.json"), rec)
    if res["applicable_flagged"]:
        raise YStop("LEADINTRO_LEAKAGE_FLAGGED", str(res["applicable_flagged"]), res)
    return rec


# ============================================================
# 出典との連続一致(DEV rr.shingle_hits_ja の移植。日本語20字。Theme Packageの source_dir がある場合のみ検査=無ければ not_checked と明記)
# ============================================================
def shingle_hits_ja(text: str, src_texts: dict, n: int = 20) -> list:
    b = _norm_ja("\n".join(ln for ln in text.splitlines() if not ln.startswith("#")))
    sh = {b[i:i + n] for i in range(len(b) - n + 1)}
    hits = []
    for pth, t in src_texts.items():
        nt = _norm_ja(t)
        for k in sh:
            if k in nt:
                hits.append({"source": pth, "shingle": k})
                break
    return hits


def load_source_texts(src_dir: str) -> dict:
    out = {}
    for pth in glob.glob(src_dir + "/**/*", recursive=True):
        if os.path.isfile(pth):
            try:
                with open(pth, encoding="utf-8", errors="ignore") as f:
                    out[pth] = f.read()
            except OSError:
                pass
    return out


def verbatim_report(parts_texts: dict, source_dir) -> dict:
    if not source_dir or not os.path.isdir(source_dir):
        return {"checked": False, "reason": "source_dir未指定または存在しない(出典連続一致は未確認。公開前の権利確認で別途確認すること)", "source_dir": source_dir, "n_hits": 0, "hits": {}}
    srcs = load_source_texts(source_dir)
    hits = {k: shingle_hits_ja(t, srcs, 20) for k, t in parts_texts.items()}
    hits = {k: v for k, v in hits.items() if v}
    return {"checked": True, "source_dir": source_dir, "n_source_files": len(srcs), "n_hits": sum(len(v) for v in hits.values()), "hits": hits}


# ============================================================
# 既存R0(Trial生成のVoice本文・改訂Lead・人物紹介)を再利用入力として受け取る経路(E-1用)
# ============================================================
def parse_r0_article(text: str) -> dict:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    if len(blocks) != 8 or not blocks[0].startswith("# "):
        raise YStop("REUSE_MISMATCH", f"R0の形が想定と違います(blocks={len(blocks)})")
    heads = [blocks[2], blocks[4], blocks[6]]
    if heads != ["## One Voice", "## Another Voice", "## A Third Voice"]:
        raise YStop("REUSE_MISMATCH", f"R0の見出し順が想定と違います: {heads}")
    return {"title": blocks[0][2:].strip(), "disclosure": blocks[1], "voice_1": blocks[3], "voice_2": blocks[5], "voice_3": blocks[7]}


REUSE_SCHEMA = "y_reuse_v1"


def load_reuse(reuse, theme: dict, slug: str) -> dict:
    """reuse=manifest(dict)またはそのpath。Voice R0はbyte一致検証(R0 article↔Gate最終本文)のうえ採用する。Lead/人物紹介(任意)は本Productionの決定論検査を再度通す。"""
    man = _read_json(os.fspath(reuse)) if isinstance(reuse, (str, os.PathLike)) else reuse
    if man.get("schema") != REUSE_SCHEMA:
        raise YStop("REUSE_MISMATCH", f"manifestのschemaが{REUSE_SCHEMA}ではありません")
    if man.get("slug") != slug:
        raise YStop("REUSE_MISMATCH", f"manifest slug={man.get('slug')!r} != 実行slug={slug!r}")
    art = man["voice_r0_article"]
    raw_bytes = _read_bytes(art)
    r0 = parse_r0_article(raw_bytes.decode("utf-8").replace("\r\n", "\n"))
    if r0["title"] != theme["world_frame"]["title_ja"]:
        raise YStop("REUSE_MISMATCH", f"R0のtitle={r0['title']!r}がTheme Packageのtitle_jaと違います")
    gdir = man["voice_gate_dir"]
    gate = _read_json(os.path.join(gdir, "gate_result.json"))
    final = _read_json(os.path.join(gdir, "final_texts.json"))
    if gate.get("status") != "PASS":
        raise YStop("REUSE_MISMATCH", f"R0 Voice Gateが PASS ではありません({gate.get('status')})")
    voices = {}
    for s in SLOTS:
        if final[s].strip() != r0[s].strip():
            raise YStop("REUSE_MISMATCH", f"R0本文とGate最終本文がbyte一致しません: {s}")
        voices[s] = r0[s].strip()
    out = {"manifest": man, "voices": voices, "voice_r0_sha256": hashlib.sha256(raw_bytes).hexdigest(), "voice_r0_article": art, "gate_result": gate,
           "voice_gate_dir": gdir, "lead": None, "intros": None, "intro_checks": man.get("intro_checks"), "source_dir": man.get("source_dir")}
    if man.get("lead_file"):
        with open(man["lead_file"], encoding="utf-8") as f:
            out["lead"] = f.read().strip()
        out["lead_file_sha256"] = hashlib.sha256(_read_bytes(man["lead_file"])).hexdigest()
    if man.get("intros_file"):
        out["intros"] = {s: _read_json(man["intros_file"])[s].strip() for s in SLOTS}
        out["intros_file_sha256"] = hashlib.sha256(_read_bytes(man["intros_file"])).hexdigest()
    return out


def reusable_prior_voice_gate(gate: dict, voices: dict) -> bool:
    """既存のVoice Gate PASS記録を、来歴検査付きで再利用してよいか。最終判定が『この本文』に対するものでPASS、かつ判定promptが今回のProduction版と同一shaの場合のみ。"""
    try:
        h = gate["history"][-1]
        return bool(gate.get("status") == "PASS" and gate.get("kind") == "voices" and h["check"]["any_flagged"] is False
                    and h["sha256"] == {s: w1.sha_text(voices[s]) for s in SLOTS}
                    and h["check"].get("prompt_sha256") == w1.sha_text(build_leak_prompt("voices", voices)))
    except (KeyError, IndexError, TypeError):
        return False


# ============================================================
# Voice段(生成 → 出典対応 → UNMAPPED再生成 → 構造タグ → Voice Gate → 最終の出典対応[記録のみ]) / 再利用
# ============================================================
def _write_voices_partial(out_dir: str, texts: dict, note: str):
    """STOP時: 到達時点のVoice本文を残す(確定稿ではない。後続へ流さない)。"""
    try:
        w1.wj(os.path.join(out_dir, "voices_partial.json"), {"note": note, "status": "NOT_FINAL", "texts": texts})
    except Exception:  # noqa: BLE001
        pass


def produce_voices(client, *, theme: dict, out_dir: str, guard=None, parts: dict = None) -> dict:
    """Theme PackageのPersona SheetからVoice 1〜3を生成しVoice Gateを通す(DEV opinion_based run_pipeline の展開移植。Gate予算skipは移植しない)。"""
    os.makedirs(out_dir, exist_ok=True)
    parts = parts or load_article_prompt("voice")
    sheets, who, wf = theme["sheets"], theme["who_ja"], theme["world_frame"]
    personas_text = {s: render_persona(sheets[s], who[s]) for s in SLOTS}
    fps = {s: sheets[s]["speech_style"]["first_person"] for s in SLOTS}
    gen, maps, texts = {}, {}, {}
    try:
        for s in SLOTS:
            gen[s] = generate_voice(client, theme, s, parts, guard=guard)
            texts[s] = gen[s]["text"]
            w1.wt(os.path.join(out_dir, f"{s}_prompt.txt"), gen[s]["prompt"])
        for s in SLOTS:
            maps[s] = map_voice(client, theme, s, texts[s], "m1", guard=guard)
        regen_unmapped = {}
        for s in [x for x in SLOTS if maps[x]["n_unmapped"] > 0]:
            g2 = generate_voice(client, theme, s, parts, extra=unmapped_extra(maps[s]), tag="_unmapregen", guard=guard)
            m2 = map_voice(client, theme, s, g2["text"], "m2", guard=guard)
            regen_unmapped[s] = {"before": texts[s], "after": g2["text"], "n_unmapped_before": maps[s]["n_unmapped"], "n_unmapped_after": m2["n_unmapped"],
                                 "problems_per_try": g2["problems_per_try"]}
            texts[s], gen[s], maps[s] = g2["text"], g2, m2
        tag1 = tag_structure(client, texts, "vstruct1", guard=guard)
        struct_regen, tag2 = None, None
        if tag1["fire"]["fired"]:
            s = tag1["fire"]["regenerate_slot"]
            g3 = generate_voice(client, theme, s, parts, emphasize=True, tag="_structregen", guard=guard)
            m3 = map_voice(client, theme, s, g3["text"], "m3", guard=guard)
            struct_regen = {"slot": s, "before": texts[s], "after": g3["text"], "n_unmapped_after": m3["n_unmapped"]}
            texts[s], gen[s], maps[s] = g3["text"], g3, m3
            tag2 = tag_structure(client, texts, "vstruct2", guard=guard)       # 記録のみ(2回目の是正はしない)
        w1.wj(os.path.join(out_dir, "voices_generated.json"), texts)
        gate = run_gate(client, kind="voices", stage="yp_voices_gate", texts=texts, out_dir=os.path.join(out_dir, "gate_voices"),
                        shared_premise=wf["shared_premise_ja"], personas_text=personas_text, first_persons=fps, guard=guard)
    except YStop:
        _write_voices_partial(out_dir, texts, "Voice段のSTOP時点の本文。確定稿ではなく、後続(Lead/紹介/Closing)へは流さない")
        raise
    if gate["status"] != "PASS":
        _write_voices_partial(out_dir, texts, "Voice Gateが3判定後も残存FAIL。確定稿ではない")
        raise YStop("VOICE_RESIDUAL_STOP", "Voiceが3判定後もLeakage判定でFAIL。暫定版は公開せず、本文とFAIL記録を保存して停止", gate["history"])
    final = load_gated_or_stop(os.path.join(out_dir, "gate_voices"))
    final_maps = {s: map_voice(client, theme, s, final[s], "final", guard=guard) for s in SLOTS}        # 記録のみ(ここで再生成しない)
    calls = [c for s in SLOTS for c in gen[s]["calls"]]
    rec = {"source": "generated", "routing_key": "FAMILY_Y_VOICE_GENERATE", "expected_model": ROUTE["FAMILY_Y_VOICE_GENERATE"]["model"], "effort": ROUTE["FAMILY_Y_VOICE_GENERATE"]["effort"],
           "model_ids": _model_ids(calls), "prompt_file": parts["file"], "prompt_sha256": parts["sha256"],
           "per_slot": {s: {"user_prompt_sha256": gen[s]["prompt_sha256"], "n_calls": len(gen[s]["calls"]), "problems_per_try": gen[s]["problems_per_try"],
                            "monitors": gen[s]["monitors"], "repetition": repetition_report(final[s])} for s in SLOTS},
           "unmapped_regen": regen_unmapped, "map_routing_key": "FAMILY_Y_VOICE_PROVENANCE_MAP", "structure_routing_key": "FAMILY_Y_VOICE_STRUCTURE_TAG",
           "structure": {"tags_before": {k: v for k, v in tag1.items() if k != "meta"}, "regen": struct_regen, "tags_after": ({k: v for k, v in tag2.items() if k != "meta"} if tag2 else None)},
           "final_map_n_unmapped": {s: final_maps[s]["n_unmapped"] for s in SLOTS}, "final_map_r2plus_only_idx": {s: final_maps[s]["r2plus_only_idx"] for s in SLOTS},
           "gate": {"status": gate["status"], "n_judgements": gate["n_judgements"], "rewritten": gate["rewritten"], "source": "judged_this_run", "dir": os.path.join(out_dir, "gate_voices"),
                    "judge_routing_key": "FAMILY_Y_LEAK_JUDGE", "rewrite_routing_key": "FAMILY_Y_VOICE_REWRITE"},
           "final_sha256": {s: w1.sha_text(final[s]) for s in SLOTS}, "voices_sha256": voices_sha256(final)}
    w1.wj(os.path.join(out_dir, "voices_final.json"), final)
    w1.wj(os.path.join(out_dir, "voices_record.json"), rec)
    return {"voices": {s: final[s] for s in SLOTS}, "record": rec, "voice_r0_sha256": rec["voices_sha256"]}


def reuse_voices(client, *, theme: dict, reuse_info: dict, out_dir: str, guard=None) -> dict:
    """既存R0をbyte一致検証のうえ採用(Voice生成をskip)。Gateは来歴検査付きの既存PASS記録を再利用、使えなければ判定1回(書換えなし。FAILはSTOP)。"""
    os.makedirs(out_dir, exist_ok=True)
    voices = reuse_info["voices"]
    gdir = os.path.join(out_dir, "gate_voices")
    if reusable_prior_voice_gate(reuse_info["gate_result"], voices):
        os.makedirs(gdir, exist_ok=True)
        g = reuse_info["gate_result"]
        w1.wj(os.path.join(gdir, "gate_result.json"), {**{k: g[k] for k in ("stage", "kind", "status", "n_judgements", "final_sha256")}, "reused_from": reuse_info["voice_gate_dir"]})
        w1.wj(os.path.join(gdir, "final_texts.json"), voices)
        gate = {"status": "PASS", "n_judgements": g["n_judgements"], "rewritten": False, "source": "reused_prior_pass_record", "reused_from": reuse_info["voice_gate_dir"]}
    else:
        r = run_gate(client, kind="voices", stage="yp_voices_reused", texts=voices, out_dir=gdir, allow_rewrite=False, guard=guard,
                     shared_premise=theme["world_frame"]["shared_premise_ja"],
                     personas_text={s: render_persona(theme["sheets"][s], theme["who_ja"][s]) for s in SLOTS},
                     first_persons={s: theme["sheets"][s]["speech_style"]["first_person"] for s in SLOTS})
        if r["status"] != "PASS":
            raise YStop("REUSED_VOICE_GATE_FAIL", "再利用するR0本文が本Productionの判定promptでLeakage判定FAIL。書換えず(byte一致を守る)停止", r["history"])
        gate = {"status": "PASS", "n_judgements": r["n_judgements"], "rewritten": False, "source": "judged_this_run", "judge_routing_key": "FAMILY_Y_LEAK_JUDGE"}
    final = load_gated_or_stop(gdir)
    if {s: final[s] for s in SLOTS} != voices:
        raise YStop("REUSE_MISMATCH", "Gate最終本文が再利用R0とbyte一致しません")
    rec = {"source": "reused_r0", "voice_generation_used": False, "routing_key": None, "model_id": None, "prompt_sha256": None,
           "voice_r0_article": reuse_info["voice_r0_article"], "voice_r0_sha256": reuse_info["voice_r0_sha256"], "gate": gate,
           "final_sha256": {s: w1.sha_text(voices[s]) for s in SLOTS}, "voices_sha256": voices_sha256(voices),
           "note": "既存R0(Trial生成・Gate PASS・byte一致検証済み)を採用。Voice生成のProduction runtime evidenceではない(E-3 voices段で別途取得)"}
    w1.wj(os.path.join(out_dir, "voices_record.json"), rec)
    return {"voices": dict(voices), "record": rec, "voice_r0_sha256": reuse_info["voice_r0_sha256"]}


# ============================================================
# 記事組立(LLM 0)と契約検査
# ============================================================
def render_article_text(title: str, lead: str, intros: dict, voices: dict, closing: str) -> str:
    """タイトル1行 + 5パート(空行区切り)。Voiceパートは『紹介1行 + 改行 + 本人の語り』。In One Line・AI編集の開示文なし。"""
    paras = [lead.strip()] + [f"{intros[s].strip()}\n{voices[s].strip()}" for s in SLOTS] + [closing.strip()]
    return f"# {title.strip()}\n\n" + "\n\n".join(paras) + "\n"


def check_article_parts(lead: str, intros: dict, voices: dict, closing: str, first_persons: dict, expected_voices: dict) -> list:
    v = []
    narr = {"lead": lead, "closing": closing, **{f"intro_{s}": intros[s] for s in SLOTS}}
    for k, t in {**narr, **{f"voice_{s}": voices[s] for s in SLOTS}}.items():
        if IOL_RE.search(t):
            v.append(f"IN_ONE_LINE_PRESENT:{k}")
        if "\n" in t.strip():
            v.append(f"MULTI_LINE:{k}")
    for k, t in narr.items():
        if AI_ANNOUNCE_RE.search(t):
            v.append(f"HAS_AI_EDIT_ANNOUNCEMENT:{k}")
        if FIRST_PERSON_RE.match(t[:4]):
            v.append(f"NARRATOR_STARTS_WITH_FIRST_PERSON:{k}")
    for s in SLOTS:
        if first_persons[s] not in voices[s]:
            v.append(f"VOICE_NO_OWN_FIRST_PERSON:{s}")
        if voices[s] != expected_voices[s]:
            v.append(f"VOICE_CHANGED_AFTER_GATE:{s}")
        if FIRST_PERSON_RE.search(intros[s]):
            v.append(f"INTRO_HAS_FIRST_PERSON:{s}")
    return v


def _stage_cached(path: str, key: str, fn):
    """サブステージの完了結果を保存し、入力key(shaで来歴を固定)が一致すればAPI 0で再利用する(STOP後の再実行で費用を二重に払わない)。"""
    if os.path.exists(path):
        d = _read_json(path)
        if d.get("input_key") == key:
            return d["result"], True
    res = fn()
    w1.wj(path, {"input_key": key, "result": res})
    return res, False


def _key(**kw) -> str:
    return w1.sha_text(json.dumps(kw, ensure_ascii=False, sort_keys=True, default=str))


def _module_sha() -> str:
    return hashlib.sha256(_read_bytes(__file__)).hexdigest()


def produce_article(client, *, slug: str, theme_package, out_dir: str, guard=None, reuse=None, theme_package_path: str = None) -> dict:
    """Family Y 正式Productionの記事テキスト全体(JA 5パート)。runner(02B)から呼ぶI/F。
    theme_package: dict(解析済み)またはpath。案B registryのsha照合のため、dictを渡すときは theme_package_path も渡すこと(無ければsha_method=canonical_jsonとなり案Bは注入されない)。
    reuse: 再利用manifest(dict/path)。既存R0(Trial生成のVoice・Lead・人物紹介)をbyte一致検証して採用する(E-1)。None=全て新規生成。
    戻り値: {title, lead, intros, voices, closing, closing_record, records}。STOP時は YStop(.code)。最終成果物の状態は out_dir/article_status.json。"""
    os.makedirs(out_dir, exist_ok=True)
    status_path = os.path.join(out_dir, "article_status.json")
    w1.wj(status_path, {"status": "RUNNING", "slug": slug, "note": "実行中または異常終了(完了時はDONE/STOP/ERRORへ更新される。RUNNINGのまま残っていれば途中で強制終了)"})
    try:
        res = _produce_article(client, slug=slug, theme_package=theme_package, out_dir=out_dir, guard=guard, reuse=reuse, theme_package_path=theme_package_path)
        w1.wj(status_path, {"status": "DONE", "slug": slug, "article_record": os.path.join(out_dir, "article_record.json"), "stages": res["records"]["stages_done"]})
        return res
    except YStop as e:
        w1.wj(status_path, {"status": "STOP", "code": e.code, "message": str(e), "slug": slug, "note": "確定稿なし。到達時点の成果物は各サブディレクトリ(voices_partial.json等)を参照"})
        raise
    except Exception as e:  # noqa: BLE001  予算guard・routing未登録・API失敗など。古いDONE記録を残さない
        w1.wj(status_path, {"status": "ERROR", "error_type": type(e).__name__, "message": str(e)[:500], "slug": slug, "note": "確定稿なし。再開は同じ入力で再実行(完了済みサブステージはAPI 0で再利用)"})
        raise


def _produce_article(client, *, slug, theme_package, out_dir, guard, reuse, theme_package_path) -> dict:
    tpl = load_theme_package(theme_package, path=theme_package_path)
    theme, pkg_sha = tpl["theme"], tpl["sha256"]
    ri = load_reuse(reuse, theme, slug) if reuse is not None else None
    fixed = slug in FIXED_CLOSING_REGISTRY
    if fixed and ri is None:
        raise YStop("FIXED_CLOSING_REQUIRES_R0_REUSE", f"{slug}: 案B固定Closingは登録時のVoice R0に紐付く。新規生成のVoiceには注入できないため、API呼出の前に停止(reuse manifestでR0を渡す)")
    if fixed:
        fixed_closing_lookup(slug, pkg_sha, ri["voice_r0_sha256"])           # sha不一致はAPI呼出の前にSTOP
    lead_reused = bool(ri and ri["lead"])
    intros_reused = bool(ri and ri["intros"])
    keys = ["FAMILY_Y_LEAK_JUDGE"]
    if ri is None:
        keys += ["FAMILY_Y_VOICE_GENERATE", "FAMILY_Y_VOICE_PROVENANCE_MAP", "FAMILY_Y_VOICE_STRUCTURE_TAG", "FAMILY_Y_VOICE_REWRITE"]
    if not lead_reused:
        keys.append("FAMILY_Y_LEAD_GENERATE")
    if not intros_reused:
        keys.append("FAMILY_Y_PERSONA_INTRO")
    if not fixed:
        keys += ["FAMILY_Y_CLOSING_GENERATE", "FAMILY_Y_CLOSING_REWRITE"]
    route_pref = preflight_routes(keys)                                       # 最初のAPI呼出の前に全key照合(途中で未登録に当たって費用だけ発生するのを防ぐ)
    spec = intro_spec(theme, (ri or {}).get("intro_checks"))
    parts_v = load_article_prompt("voice") if ri is None else None
    parts_l = load_article_prompt("lead") if not lead_reused else None
    parts_i = load_article_prompt("intro") if not intros_reused else None
    common = dict(pkg=pkg_sha, slug=slug, module=_module_sha(), mgmt=MANAGEMENT_ID)
    reuse_key = _key(manifest=ri["manifest"], r0=ri["voice_r0_sha256"], lead=ri.get("lead_file_sha256"), intros=ri.get("intros_file_sha256")) if ri else None
    stages_done = []

    # ---- 1. Voice ----
    vkey = _key(stage="voices", reuse=reuse_key, prompt=(parts_v or {}).get("sha256"), **common)
    vres, vcached = _stage_cached(os.path.join(out_dir, "voices", "stage_voices.json"), vkey, lambda: (
        reuse_voices(client, theme=theme, reuse_info=ri, out_dir=os.path.join(out_dir, "voices"), guard=guard) if ri
        else produce_voices(client, theme=theme, out_dir=os.path.join(out_dir, "voices"), guard=guard, parts=parts_v)))
    voices, voice_r0_sha = vres["voices"], vres["voice_r0_sha256"]
    stages_done.append("voices(cached)" if vcached else "voices")

    # ---- 2. Lead + 人物紹介 + 補助Gate ----
    lkey = _key(stage="lead_intro", voices=voices_sha256(voices), reuse=reuse_key, lead=(parts_l or {}).get("sha256"), intro=(parts_i or {}).get("sha256"),
                spec=spec["mode"], **common)

    def _lead_intro():
        d = os.path.join(out_dir, "lead_intro")
        os.makedirs(d, exist_ok=True)
        if lead_reused:
            lead, lrec = ri["lead"], {"source": "reused", "file": ri["manifest"]["lead_file"], "file_sha256": ri["lead_file_sha256"], "sha256": w1.sha_text(ri["lead"])}
            c = check_lead(lead)
            if not c["ok"]:
                raise YStop("REUSED_TEXT_CHECK_FAILED", f"再利用Leadが本Productionの決定論検査に不適合: {c['violations']}", c)
        else:
            g = generate_lead(client, theme, os.path.join(d, "lead"), parts_l, guard=guard)
            lead = g["text"]
            lrec = {"source": "generated", "routing_key": "FAMILY_Y_LEAD_GENERATE", "expected_model": ROUTE["FAMILY_Y_LEAD_GENERATE"]["model"], "effort": ROUTE["FAMILY_Y_LEAD_GENERATE"]["effort"],
                    "model_ids": _model_ids(g["meta"]["calls"]), "prompt_file": parts_l["file"], "prompt_sha256": parts_l["sha256"], "user_prompt_sha256": g["meta"]["prompt_sha256"],
                    "inputs_source": g["inputs_source"], "n_calls": len(g["meta"]["calls"]), "sha256": w1.sha_text(lead)}
        if intros_reused:
            intros, irec = dict(ri["intros"]), {"source": "reused", "file": ri["manifest"]["intros_file"], "file_sha256": ri["intros_file_sha256"], "check_mode": spec["mode"]}
            bad = {s: check_intro(intros[s], s, voices[s], spec)["violations"] for s in SLOTS}
            bad = {s: x for s, x in bad.items() if x}
            if bad:
                raise YStop("REUSED_TEXT_CHECK_FAILED", f"再利用の人物紹介が本Productionの決定論検査に不適合: {bad}", bad)
        else:
            g = generate_intros(client, theme, voices, os.path.join(d, "intro"), parts_i, spec, guard=guard)
            intros = g["intros"]
            irec = {"source": "generated", "routing_key": "FAMILY_Y_PERSONA_INTRO", "expected_model": ROUTE["FAMILY_Y_PERSONA_INTRO"]["model"], "effort": ROUTE["FAMILY_Y_PERSONA_INTRO"]["effort"],
                    "model_ids": _model_ids(g["meta"]["calls"]), "prompt_file": parts_i["file"], "prompt_sha256": parts_i["sha256"], "user_prompt_sha256": g["meta"]["prompt_sha256"],
                    "check_mode": spec["mode"], "n_calls": len(g["meta"]["calls"])}
        irec["sha256"] = {s: w1.sha_text(intros[s]) for s in SLOTS}
        w1.wt(os.path.join(d, "lead_final.txt"), lead + "\n")
        w1.wj(os.path.join(d, "intros_final.json"), intros)
        gate = run_leadintro_gate(client, lead, intros, os.path.join(d, "gate"), guard=guard)
        return {"lead": lead, "intros": intros, "lead_record": lrec, "intro_record": irec, "gate_record": gate}

    lires, licached = _stage_cached(os.path.join(out_dir, "lead_intro", "stage_lead_intro.json"), lkey, _lead_intro)
    lead, intros = lires["lead"], lires["intros"]
    stages_done.append("lead_intro(cached)" if licached else "lead_intro")

    # ---- 3. Closing(案B固定注入 or Prompt 02一般化) ----
    inp = closing_input_from_theme(theme, voices)
    ckey = _key(stage="closing", voices=voices_sha256(voices), closing_prompt=PROMPT_SHA256, voice_r0=voice_r0_sha, **common)
    cres, ccached = _stage_cached(os.path.join(out_dir, "closing", "stage_closing.json"), ckey, lambda: produce_closing(
        client, slug=slug, inp=inp, theme_package_sha256=pkg_sha, voice_r0_sha256=voice_r0_sha, out_dir=os.path.join(out_dir, "closing"), guard=guard))
    closing, crec = cres["text"], cres["record"]
    stages_done.append("closing(cached)" if ccached else "closing")

    # ---- 4. 組立・契約検査・出典連続一致 ----
    fps = {s: theme["sheets"][s]["speech_style"]["first_person"] for s in SLOTS}
    errs = check_article_parts(lead, intros, voices, closing, fps, voices)
    title = theme["world_frame"]["title_ja"]
    text = render_article_text(title, lead, intros, voices, closing)
    w1.wt(os.path.join(out_dir, "article_assembled.md"), text)
    if errs:
        raise YStop("ARTICLE_ASSEMBLY_STOP", f"記事組立の契約違反 {errs}", errs)
    src_dir = (ri or {}).get("source_dir") or theme.get("source_dir")
    parts_texts = {"lead": lead, "closing": closing, **{f"intro_{s}": intros[s] for s in SLOTS}, **{f"voice_{s}": voices[s] for s in SLOTS}}
    verb = verbatim_report(parts_texts, src_dir)
    if verb["n_hits"]:
        w1.wj(os.path.join(out_dir, "verbatim_hits.json"), verb)
        raise YStop("SOURCE_VERBATIM_STOP", f"出典との連続一致(20字)が{verb['n_hits']}件。本文は確定しない(権利確認の対象)", verb)
    rec = {"management_id": MANAGEMENT_ID, "status": STATUS, "slug": slug, "theme_id": theme["theme_id"], "title": title,
           "theme_package_sha256": pkg_sha, "theme_package_sha_method": tpl["sha_method"], "theme_package_path": tpl["path"],
           "mode": "reused_r0" if ri else "generated", "routes_preflighted": route_pref,
           "stages_done": stages_done, "voices": vres["record"], "lead": lires["lead_record"], "intros": lires["intro_record"], "leadintro_gate": lires["gate_record"],
           "closing": crec, "verbatim": verb,
           "part_sha256": {k: w1.sha_text(t) for k, t in parts_texts.items()}, "article_sha256": w1.sha_text(text),
           "prompt_files": {"closing": {"file": os.path.basename(PROMPT_FILE), "sha256": PROMPT_SHA256},
                            **{k: {"file": ARTICLE_PROMPTS[k][0], "sha256": ARTICLE_PROMPTS[k][1]} for k in ARTICLE_PROMPTS}},
           "module": {"file": "er121_family_y_text_core_01.py", "sha256": common["module"]}}
    w1.wj(os.path.join(out_dir, "article_record.json"), rec)
    return {"title": title, "lead": lead, "intros": intros, "voices": voices, "closing": closing, "closing_record": crec,
            "records": {**rec, "stages_done": stages_done, "voice_generate": rec["voices"]}}
