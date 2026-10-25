# -*- coding: utf-8 -*-
"""er121_family_y_text_core_01.py
FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02A: Family Y 正式Production「テキストcore」(Closing/Gate lane)。

位置づけ(重要):
  - Family Y正式Productionのテキスト側core。DEV/Trial module(er110_family_y_*)は **importしない**(DEVのモジュール差替え・
    alias・予算skipをProductionへ持ち込まない)。DEVの関数は「展開移植」し、Prompt/判定基準の文言は一字も変えない
    (DEVとの一致はtestで固定: Prompt 02 byte一致+sha、入力block、schema、決定論検査、判定器prompt)。
  - import時にAPI呼出0・ファイル副作用0。環境変数・CLI・設定dictで挙動が変わる経路はない(本moduleにCLIは無い)。
  - 本moduleはまだ正式runner(02B: er121_family_y_runner_01.py)から接続されていない。routing keyは02Bがer006へ登録する。
    未登録のままcallすると require_model が ModelContractViolation を送出する(fail-closed。API呼出の前)。
  - Closing一般化方式=Prompt 02(sha 4713ceff…)+gpt-6.1-sol/high(ユーザー正式採用 USER §2-2)。Prompt 03化・意味変更なし。
  - 『宅配の再配達』のみ案B固定注入(USER §2-3)。registry外のslugは必ず一般化方式。
  - M-1(Opus): Tension判定promptの欠落定義(「上記と同じ意味」の参照先)を逐語展開して補う。判定基準の文言は変えない。
"""
from __future__ import annotations

import hashlib
import json
import os
import re

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
    if route_key not in ROUTE:
        raise routing.ModelContractViolation(f"未知のY route key: {route_key}")
    model, effort = ROUTE[route_key]["model"], ROUTE[route_key]["effort"]
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


def split_leadintro_flags(chk: dict) -> dict:
    app, na = [], []
    for it in chk["flagged_items"]:
        ap = [x for x in it["fail_fields"] if x not in LEADINTRO_NA_FIELDS]
        nn = [x for x in it["fail_fields"] if x in LEADINTRO_NA_FIELDS]
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
             shared_premise: str = "", personas_text: dict = None, first_persons: dict = None, max_judgements: int = 3, allow_rewrite: bool = True, guard=None) -> dict:
    """Leakage判定 → 局所書換え → 再判定(判定最大3回=初回+書換え2回)。残ればLEAKAGE_RESIDUAL_STOP(全文書き直しに戻さない)。
    judge/rewriteの履歴を gate_history として全保存。allow_rewrite=False(案B固定)は判定1回のみでFAILならSTOP(書換えない)。"""
    os.makedirs(out_dir, exist_ok=True)
    cur = dict(texts)
    history, status = [], None
    for attempt in range(1, (max_judgements if allow_rewrite else 1) + 1):
        chk = run_leak(client, kind, cur, stage=f"{stage}_leak{attempt}", guard=guard)
        w1.wj(os.path.join(out_dir, f"leak_check_{attempt}.json"), chk)
        entry = {"attempt": attempt, "sha256": {k: w1.sha_text(v) for k, v in cur.items()}, "check": chk}
        history.append(entry)
        if not chk["any_flagged"]:
            status = "PASS"
            break
        if not allow_rewrite or attempt == max_judgements:
            status = "LEAKAGE_RESIDUAL_STOP"
            break
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
            gate = {"status": "PASS", "n_judgements": 1, "rewritten": False, "source": "reused_prior_pass_record"}
        else:
            r = run_gate(client, kind="tension", stage="yp_closing_fixed", texts={"tension": text}, out_dir=gate_dir, voices_ctx=voices, allow_rewrite=False, guard=guard)
            if r["status"] != "PASS":
                raise YStop("FIXED_CLOSING_GATE_FAIL", "案B(ユーザー承認本文)がLeakage判定でFAIL。書換えず停止(同一本文の判定再試行で通さない)", r["history"])
            gate = {"status": "PASS", "n_judgements": r["n_judgements"], "rewritten": False, "source": "judged_this_run"}
        final = load_gated_or_stop(gate_dir)["tension"]
        if final != text:
            raise YStop("FIXED_CLOSING_MUTATED", "固定注入本文が変更されている")
        rec = {"source": "fixed_user_approved", "general_method_used": False, "slug": slug, "approval_ref": ent["approval_ref"],
               "text_sha256": ent["text_sha256"], "registry_sha256": registry_sha(), "theme_package_sha256": theme_package_sha256,
               "voice_r0_sha256": voice_r0_sha256, "generation_sha256": ent["text_sha256"], "final_sha256": w1.sha_text(final),
               "rewritten": False, "gate": gate, "model_id": None, "routing_key": None, "prompt_sha256": None,
               "note": "案B固定注入。Prompt 02による一般化生成は使っていない(受入条件3は別記事の一般化経路evidenceで担保)"}
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
