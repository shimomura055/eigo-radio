# -*- coding: utf-8 -*-
"""er053_family_x_factlock_ja_writer_01.py
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1(追加のみ、2026-10-10)。新Writer W-1 の Production module(先行作成)。

**どのProduction runnerからも呼ばれない**(C2で配線)。C1では新規ファイルとして置くだけ。
W-1 = 注記済みB3 → R0[Luna gpt-6-luna, Fact Lockブロック, effort=high, 単発] → 記号QA → R1[Astra gpt-6-astra, effort=high]
      → R2[Astra, 入力=R1の生出力] → 後処理 → ja_writer/revision2.md  (DESIGN_03 2節)

移植契約(DESIGN_03 2-2 / 15-2): Trial(er052_factlock_writer_trial_01_run.py / er052_factlock_astra_e2e_runner_01.py)の
Prompt定数・regex・関数を**byte-identical**に移植した(下の「移植元:」コメント付きブロック)。Trial moduleはimportしない
(同一性はtest内でのみTrial moduleを読んで機械証明)。許容差(それ以外の差は不許可):
  [F11 call_astra] (1) cl.logging_context(TRIAL_ID,…) の TRIAL_ID → THEME_TAG
                   (2) ASTRA_MODELの出所: 関数先頭に routing.require_model("FAMILY_X_FACTLOCK_REVISE", ASTRA_MODEL) を追加(API call前)
                   (3) time.sleep(0 if os.environ.get("E2E_STUB") else 3 * (i + 1)) → time.sleep(3 * (i + 1))(隠れswitch E2E_STUB削除)
  [F8 clean_ja_for_next] Trialは er052 fl.strip_tags を関数内importで呼ぶ → 本module内の同一strip_tagsを呼ぶ(import行とfl.接頭辞のみ)
  [F2/F3等] 差なし。
Production既存資産(E1〜E4)は er019_family_x_ja_writer_o_r1_r2_01 から参照(無変更・sha固定でdrift検知)。

禁止: 注記なしB3の入力(入口は validate_annotated_b3 のみ)・fallback/switch/環境変数/CLI引数(test T-13で固定)。
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import time

import er003_audio_tts_asr_safety as safety
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er019_family_x_ja_writer_o_r1_r2_01 as jaw

THEME_TAG = "FAMILY_X_FACTLOCK_W1_PRODUCTION_01"
CHAIN_METHOD = "W-1"
CHAIN_METHOD_DETAIL = "factlock_r0_luna__astra_r1_r2_independent"
R0_MODEL = "gpt-6-luna"          # routing key FAMILY_X_FACTLOCK_R0(リテラル固定。jaw.call_freshは流用しない)
R0_EFFORT = "high"
ASTRA_MODEL = "gpt-6-astra"      # routing key FAMILY_X_FACTLOCK_REVISE
ASTRA_EFFORT = "high"


class ProvenanceViolation(RuntimeError):
    pass


class TagLeak(RuntimeError):
    pass


class JASymbolCheckStopError(RuntimeError):
    """記号QA(音声化禁止記号)が1回のやり直し後も残った(STOP。本文を手で直さない)。"""

    def __init__(self, stage: str, message: str, rejected_text: str, findings: list):
        super().__init__(message)
        self.stage, self.rejected_text, self.findings = stage, rejected_text, findings


# ---- 移植元: er052_factlock_astra_e2e_runner_01.py (USER_TMPL=系列Xユーザーメッセージ逐語。変更禁止) ----
USER_TMPL = "以下の記事:\n\n{body}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。"

# ---- 移植元: er052_factlock_writer_trial_01_run.py(Fact Lock R0ブロック・タグ正規表現) ----
MUSTFIX_PRIORITY = "事実確認の修正指示がある場合はそれを最優先し、直すか削る。"
FACTLOCK_R0_BLOCK_HEAD = (
    "\n\n【出典タグの規則(Fact Lock)】\n"
    "この記事は、上のニュース欄に書かれた事実だけを材料にします。ニュース欄の各事実の行頭には"
    "【事実1】【事実2】のような番号が付いています。\n"
    "1. 世界について何かを断定する文(出来事・数値・人物の発言や行動・原因・結果・比較・時期など)は、"
    "文末の句点の直後に、根拠にした事実の番号を【事実1】のように付けてください。複数の事実を使った文は"
    "【事実1,事実2】のようにします。番号はニュース欄にあるものだけを使い、新しい番号を作らないでください。"
    "タイトルには番号を付けないでください。\n"
    "2. 問いかけ・感想・読者への語りかけ・つなぎの文には番号は不要です。ただし、これらの文でも"
    "ニュース欄にない新しい事実を断定しないでください。"
    "暮らしとのつながりは、問いかけや「〜かもしれない」の形で示し、具体的な事実を断定しないでください。\n"
    "3. ニュース欄に書かれていないことは書かないでください。背景知識や常識による補足もしません。"
    "書かれていないことについて「〜かどうかは分かっていない」と述べるのは構いませんが、"
    "分からないことを推測で埋めないでください。\n"
    "4. 事実の範囲(誰が・どこで・いつ・どの集団か)、確かさ(提案か決定か、懸念か事実か)、方向"
    "(増える・減るなど)を、ニュース欄の記述より強くしたり広げたりしないでください。"
    "ニュース欄に「〜ではない」「断定しない」とあることは守ってください。"
    "ニュース欄が触れていない点(誰が・いつ・何人・理由・結果)を、「〜しなかった」「〜はない」「唯一」「初めて」"
    "などと断定して埋めないでください。\n"
    "5. 数字の規則: ニュース欄で【中核数値】と印の付いた数字だけを、記事で使えます。タイトルでも使えますが、"
    "タイトルにはタグを付けません。書き方はニュース欄の表記のままにし"
    "(丸め・単位の換算・「約」「およそ」などの追加や削除・比較値の自分での計算をしない)、本文の文には必ず番号を付けます。"
    "【周辺数値】と印の付いた数字は書かないでください。ただし、【周辺数値】を含む事柄は、数字を省いて述べてよいです"
    "(例: 番号を書かずに「ロシアの衛星」、日付の代わりにニュース欄にある「同日」「翌日」)。"
    "禁じるのは、数字の大きさを「大きく」「急に」「多数」などの言葉で表すことだけです。"
    "ニュース欄に印の無い数字は使いません。"
    "【中核数値】【周辺数値】の印そのものは記事に書かないでください。\n"
)
FACTLOCK_R0_BLOCK_TAIL = "\n7. " + MUSTFIX_PRIORITY
TAG_RE = re.compile(r"【事実\s*\d+(?:\s*[,、，・]\s*(?:事実\s*)?\d+)*】")
BROAD_TAG_RE = re.compile(r"【\s*[FＦ事実][^】\n]{0,30}】")
MARK_RE = re.compile(r"【(?:中核数値|周辺数値)】")
FACT_LINE_RE = re.compile(r"^\s*(?:-|・)\s*【事実(\d+)】\s*(.*)$")

# ---- 移植元: er052_factlock_astra_e2e_runner_01.py (タグ残存・R0復唱の検出regex) ----
TAG_LEAK_RE = re.compile(r"【\s*(?:事実|[FＦ]|中核数値|周辺数値)[^】\n]{0,30}】")
ECHO_RE = re.compile(r"これ[、,]?\s*ちょっと\s*面白くない[？?]")

# ---- 移植元: er052_factlock_writer_trial_01_run.py ----


def strip_tags(text: str) -> str:
    """出典タグ(と、Writerが誤って書き写した数値印)を除去する。行末空白を整える。"""
    t = TAG_RE.sub("", text or "")
    t = BROAD_TAG_RE.sub("", t)
    t = MARK_RE.sub("", t)
    return "\n".join(l.rstrip() for l in t.split("\n"))


def parse_annotated_facts(brief_text: str) -> dict:
    """注記版brief(## Selected Facts 配下の『- 【F1】本文』行)から {F1: 本文} を返す。数値印は除去。"""
    facts, in_facts = {}, False
    for line in brief_text.split("\n"):
        if line.strip().startswith("## Selected Facts"):
            in_facts = True
            continue
        if not in_facts:
            continue
        m = FACT_LINE_RE.match(line)
        if m:
            facts[f"F{m.group(1)}"] = MARK_RE.sub("", m.group(2)).strip()
    return facts


def build_r0_block(an3_block: str) -> str:
    """AN3(CONCRETENESS_CONTROL_AN3_BLOCK)の第1文(数字・時刻の抑制)を Fact Lock 数字規則(5)で置換し、
    第2文(固有名詞)は逐語で保持する。AN3の2行目が取れなければ ValueError。"""
    lines = (an3_block or "").strip("\n").split("\n")
    proper = [l for l in lines if l.startswith("人名・企業名・地名")]
    if len(proper) != 1:
        raise ValueError("AN3ブロックの固有名詞文が特定できない")
    return FACTLOCK_R0_BLOCK_HEAD + "6. " + proper[0] + FACTLOCK_R0_BLOCK_TAIL


# ---- 移植元: er052_factlock_astra_e2e_runner_01.py ----


def strip_markdown(raw: str) -> str:
    """er052_step2_astra_r3_01_run.strip_markdown と同一(テストで同一性を確認)。"""
    out = []
    for ln in raw.replace("\r\n", "\n").split("\n"):
        s = ln.rstrip()
        if re.fullmatch(r"\s*(-{3,}|\*{3,}|_{3,})\s*", s):
            continue
        s = re.sub(r"^\s{0,3}#{1,6}\s*", "", s)
        s = re.sub(r"^\s*[-*+]\s+", "", s)
        s = s.replace("**", "").replace("__", "")
        out.append(s)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def dash_to_comma(t: str) -> str:
    return re.sub(r"[—―]{1,3}", "、", t)


def postprocess_ja(raw: str) -> str:
    """(e) Astra出力の後処理(決定論): strip_markdown -> 「……」「…」を文末は「。」文中は「、」 -> 「——」を「、」。"""
    import er003_audio_tts_asr_safety as safety
    return dash_to_comma(safety.normalize_ellipsis_pause_ja(strip_markdown(raw)))


def assert_no_tag_leak(text: str) -> str:
    if TAG_LEAK_RE.search(text or ""):
        raise TagLeak(f"タグ類が残存: {TAG_LEAK_RE.findall(text)[:3]}")
    return text


def clean_ja_for_next(text: str) -> str:
    """(c) 【事実N】等の除去の単一経路。初回生成・B1回復・EN段手前の全てがここを通る。残存があればTagLeak。
    ニュース本文に元からある「【速報】」等はタグではないので残す(残存「【」の件数は測定として r0_meta に記録)。"""
    return assert_no_tag_leak(strip_tags(text))


def detect_r0_echo(text: str) -> dict:
    """(b) OPEN-175 R0冒頭復唱の検出のみ(修正しない)。タイトル行(最初の非空行)を除いた本文で判定。"""
    lines = [l for l in (text or "").split("\n") if l.strip()]
    body = "\n".join(lines[1:])
    return {"echo_anywhere": bool(ECHO_RE.search(body)), "echo_in_head120": bool(ECHO_RE.search(body[:120])), "n": len(ECHO_RE.findall(body))}


def parse_brief_md(text: str):
    """er052_open233_polysemy_nb_dev_01.parse_brief_md と同一仕様(テストで同一性を確認)。"""
    text = text.replace("\r\n", "\n")      # 実ファイルがCRLFでも親(dev.parse_brief_md はtext mode読込でLF化)と同じ結果にする
    h1, h2 = "## Storyline\n", "\n## Selected Facts\n"
    if h1 not in text or h2 not in text:
        raise ValueError("brief-mdが『## Storyline』『## Selected Facts』形式でない")
    storyline, facts = text.split(h1, 1)[1].split(h2, 1)
    storyline, facts = storyline.strip(), facts.strip("\n")
    if not storyline or not facts.strip():
        raise ValueError("brief-mdのStorylineまたはFactsが空")
    return storyline, facts


def call_astra(client, user: str, stage: str, retries: int = 2):
    routing.require_model("FAMILY_X_FACTLOCK_REVISE", ASTRA_MODEL)   # 許容差(2): API call前のfail-closed(Trialは require_model_or_override)
    import er005_cost_logger as cl
    last = None
    for i in range(1 + retries):
        try:
            with cl.logging_context(THEME_TAG, stage):   # service_tier指定なし(Standard同期)、previous_response_id/developerなし
                resp = client.responses.create(model=ASTRA_MODEL, reasoning={"effort": "high"}, input=[{"role": "user", "content": user}])
            if not str(getattr(resp, "model", "")).startswith(ASTRA_MODEL):
                raise ProvenanceViolation(f"[STOP] Astra段のmodelが{ASTRA_MODEL}で始まらない: {getattr(resp, 'model', None)}")
            return resp
        except ProvenanceViolation:
            raise
        except Exception as e:  # noqa: BLE001  一時エラーは最大2回再試行
            last = e
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"Astra API失敗(再試行{retries}回後): {last!r}")


# ============================================================
# 以下はProduction新規部分(Trialのcommand-line/subprocess構造はB移植しない)
# ============================================================
def sha_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rdt(p: str) -> str:
    """Trial rdt と同一(text mode: CRLF->LF)。Astraへ渡す文章の読込に使う。"""
    with open(p, encoding="utf-8") as f:
        return f.read()


def wt(p: str, text: str) -> None:
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    tmp = f"{p}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, p)


def wj(p: str, obj) -> None:
    wt(p, json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def tag_ids(tag: str) -> list:
    return [f"F{n}" for n in re.findall(r"(\d+)", tag)]


def extract_title(article_text: str) -> str:
    """jaw._extract_title と同一規則。"""
    for line in article_text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    lines = [l for l in article_text.splitlines() if l.strip()]
    return lines[0].strip() if lines else ""


def build_r0_prompt(storyline_line: str, brief_facts_text: str) -> str:
    """R0 user prompt(純関数)。Trialの `fl.apply_factlock_patches()` 適用下の `jaw.build_original_prompt(storyline, facts)` と
    文字列完全一致(test: golden fixture)。構成: R0_PROMPT([テーマ]行差替) + [ニュース] + 記号予防ブロック + Fact Lockブロック
    (AN3第1文を数字規則5で置換、第2文[固有名詞]は逐語保持)。must-fix引数は持たない(Checker起点要素は撤去)。"""
    lines = jaw.R0_PROMPT.split("\n")
    new_lines = [f"テーマ：{storyline_line}" if line.startswith("テーマ：") else line for line in lines]
    prompt = "\n".join(new_lines)
    prompt += "\n\n[ニュース]\n" + brief_facts_text
    prompt += jaw.SYMBOL_PREVENTION_BLOCK_JA
    prompt += build_r0_block(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)
    return prompt


def build_r0_symbol_regen_prompt(storyline_line: str, brief_facts_text: str, findings: list) -> str:
    """R0の記号QA再生成Prompt = build_r0_prompt() + "\\n\\n" + 既存violation note(新規文言なし)。"""
    return build_r0_prompt(storyline_line, brief_facts_text) + "\n\n" + safety.build_symbol_violation_prompt_note(findings)


def call_luna_r0(client, user: str, stage: str):
    """R0単発: developer=DEVELOPER_MESSAGE, user=prompt, effort=high。previous_response_id無し。
    API call前に routing.require_model(FAMILY_X_FACTLOCK_R0)(リテラル固定の gpt-6-luna と一致しなければ ModelContractViolation)。"""
    model = routing.require_model("FAMILY_X_FACTLOCK_R0", R0_MODEL)
    with cl.logging_context(THEME_TAG, stage):
        return client.responses.create(
            model=model, reasoning={"effort": R0_EFFORT},
            input=[{"role": "developer", "content": jaw.DEVELOPER_MESSAGE}, {"role": "user", "content": user}])


def _resp_meta(resp) -> dict:
    u = getattr(resp, "usage", None)
    return {"response_id": getattr(resp, "id", None), "model": getattr(resp, "model", None),
            "usage": {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None)}}


def verbatim_shas() -> dict:
    """移植元Prompt定数・regexのsha256(runtime_evidenceへ記録。DESIGN_03 2-2 の A/B 項目)。"""
    return {
        "USER_TMPL": sha_text(USER_TMPL), "FACTLOCK_R0_BLOCK_HEAD": sha_text(FACTLOCK_R0_BLOCK_HEAD),
        "FACTLOCK_R0_BLOCK_TAIL": sha_text(FACTLOCK_R0_BLOCK_TAIL), "MUSTFIX_PRIORITY": sha_text(MUSTFIX_PRIORITY),
        "R0_BLOCK": sha_text(build_r0_block(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)),
        "TAG_RE": sha_text(TAG_RE.pattern), "BROAD_TAG_RE": sha_text(BROAD_TAG_RE.pattern), "MARK_RE": sha_text(MARK_RE.pattern),
        "TAG_LEAK_RE": sha_text(TAG_LEAK_RE.pattern), "ECHO_RE": sha_text(ECHO_RE.pattern),
        "R0_PROMPT": sha_text(jaw.R0_PROMPT), "DEVELOPER_MESSAGE": sha_text(jaw.DEVELOPER_MESSAGE),
        "SYMBOL_PREVENTION_BLOCK_JA": sha_text(jaw.SYMBOL_PREVENTION_BLOCK_JA),
        "CONCRETENESS_CONTROL_AN3_BLOCK": sha_text(jaw.CONCRETENESS_CONTROL_AN3_BLOCK),
    }


def _noop():
    return None


def run_w1_writer(out_dir: str, client=None, budget_check=None) -> dict:
    """W-1 を実行し、out_dir/ja_writer/ に original.md / revision1.md / revision2.md / runtime_evidence.json
    (+ factlock/ 以下の生ファイル)を書く。

    入口は **注記済みB3の契約検証(validate_annotated_b3)のみ**。契約違反は API呼出前に AnnotatedB3ContractViolation(STOP)。
    注記なしB3を渡す経路・switch・fallbackは存在しない。
    budget_check: 呼出側が渡す予算ガード(例: efam.assert_budget_ok のラッパ)。R0前・R1前・R2前・R2再実行後に呼ぶ(例外は伝播)。
    戻り値: {"ja_text", "title", "runtime_evidence", "paths"}"""
    from er053_b3_annotation_contract_01 import validate_annotated_b3   # 遅延import(循環回避)

    annotated = validate_annotated_b3(out_dir)                          # 失敗なら課金前にSTOP
    storyline, facts_text = parse_brief_md(annotated.annotated_md_text)   # 入力は注記済みmdをparse_brief_mdした結果に限定
    budget_check = budget_check or _noop
    # model contractはAPI call前に確認(R0/Astra共に)
    routing.require_model("FAMILY_X_FACTLOCK_R0", R0_MODEL)
    routing.require_model("FAMILY_X_FACTLOCK_REVISE", ASTRA_MODEL)
    if client is None:
        client = jaw.vfl01.get_client()
    d = os.path.join(out_dir, "ja_writer")
    fdir = os.path.join(d, "factlock")
    ev = {"chain_method": CHAIN_METHOD, "chain_method_detail": CHAIN_METHOD_DETAIL,
          "annotated_md_sha256": annotated.annotated_md_sha256, "annotation_manifest_producer": annotated.producer,
          "annotated_md_path": annotated.annotated_md_path, "verbatim_shas": verbatim_shas(), "symbol_qa": {},
          "started": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}

    # ---------------- R0 (Luna, Fact Lock) ----------------
    budget_check()
    prompt0 = build_r0_prompt(storyline, facts_text)
    resp0 = call_luna_r0(client, prompt0, "w1_r0")
    text0 = resp0.output_text.strip()
    r0_calls = [{"stage": "w1_r0", **_resp_meta(resp0), "prompt_sha256": sha_text(prompt0)}]
    # 記号QA(Layer2)。判定はタグ除去**前**のタグ付きR0本文。1回だけ再生成、残ればSTOP
    f0 = safety.detect_prohibited_symbols(text0, language="ja")
    ev["symbol_qa"]["r0"] = {"findings_first": f0, "regenerated": False}
    if safety.symbol_gate_requires_stop(f0):
        print(f"[W1][r0] 音声化禁止記号を検出。1回だけ再生成します(count={len(f0)})...")
        budget_check()
        prompt0b = build_r0_symbol_regen_prompt(storyline, facts_text, f0)
        resp0b = call_luna_r0(client, prompt0b, "w1_r0_symbol_regen")
        text0b = resp0b.output_text.strip()
        r0_calls.append({"stage": "w1_r0_symbol_regen", **_resp_meta(resp0b), "prompt_sha256": sha_text(prompt0b)})
        f0b = safety.detect_prohibited_symbols(text0b, language="ja")
        ev["symbol_qa"]["r0"].update({"regenerated": True, "findings_after": f0b, "pre_regen_response_id": r0_calls[0]["response_id"]})
        if safety.symbol_gate_requires_stop(f0b):
            wt(os.path.join(d, "audit", "rejected_w1_r0_symbol.md"), text0b)
            raise JASymbolCheckStopError("r0_symbol", "[STOP] JA_SYMBOL_CHECK_STOP: W-1 R0音声化禁止記号Check、"
                                         f"再生成後も禁止記号が残りました(findings={f0b})。本文を手で直さずSTOPします。", text0b, f0b)
        text0 = text0b
    for c in r0_calls:                     # model_id requested/returned を記録(不一致は記録のみ。新規STOP条件は追加しない)
        c["model_requested"] = R0_MODEL
        c["model_mismatch"] = bool(c["model"]) and not str(c["model"]).startswith(R0_MODEL)
    clean0 = clean_ja_for_next(text0).strip() + "\n"          # タグ除去の単一経路(残存はTagLeak=STOP)
    wt(os.path.join(fdir, "r0_with_tags.md"), text0)
    wt(os.path.join(fdir, "r0.md"), clean0)
    tags_used = sorted({t for m in TAG_RE.finditer(text0) for t in tag_ids(m.group(0))})
    r0_meta = {"writer_calls": r0_calls, "tags_used": tags_used, "marks_echoed": len(MARK_RE.findall(text0)),
               "facts_in_brief": list(parse_annotated_facts(annotated.annotated_md_text)), "r0_echo": detect_r0_echo(clean0),
               "r0_sha256": sha_text(clean0), "factlock_r0_block_sha256": sha_text(build_r0_block(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)),
               "r0_prompt_sha256": sha_text(prompt0)}
    wj(os.path.join(fdir, "r0_meta.json"), r0_meta)

    # ---------------- R1 / R2 (Astra) ----------------
    def astra_stage(which: str, src_path: str, stage_tag: str):
        src = rdt(src_path)
        user = USER_TMPL.format(body=src.strip())
        t0 = time.time()
        resp = call_astra(client, user, stage_tag)
        raw = (resp.output_text or "").strip()
        p = postprocess_ja(raw)
        meta = {"requested_model": ASTRA_MODEL, "model": resp.model, "reasoning": {"effort": ASTRA_EFFORT},
                "previous_response_id_used": False, "developer_message": None, "service_tier": None,
                "user_message_sha256": sha_text(user), "response_id": resp.id, "sec": round(time.time() - t0, 1),
                "output_chars": len(raw),
                "usage": {"input_tokens": getattr(resp.usage, "input_tokens", None),
                          "output_tokens": getattr(resp.usage, "output_tokens", None)}}
        return raw, p, meta

    budget_check()
    raw1, p1, m1 = astra_stage("r1", os.path.join(fdir, "r0.md"), "w1_astra_r1")
    wt(os.path.join(fdir, "r1.raw.md"), raw1)                  # R2の入力=R1の生出力(後処理前)。ファイル往復でCRLF->LFもTrialと同一
    wj(os.path.join(fdir, "r1.response.json"), m1)
    wt(os.path.join(fdir, "r1.p1.md"), p1)

    budget_check()                                              # R1/R2間
    raw2, p2, m2 = astra_stage("r2", os.path.join(fdir, "r1.raw.md"), "w1_astra_r2")
    wt(os.path.join(fdir, "r2.raw.md"), raw2)
    wj(os.path.join(fdir, "r2.response.json"), m2)
    final = clean_ja_for_next(p2)                               # 後処理+タグ除去後の最終文(TagLeakならSTOP)
    # Astra段の記号QA=案A: 判定は最終文。禁止記号が残れば R2 のみ同一R1生出力で1回だけ再実行。残ればSTOP。両response_idを記録
    f2 = safety.detect_prohibited_symbols(final, language="ja")
    ev["symbol_qa"]["r2"] = {"method": "A_rerun_r2_once_same_r1_raw", "findings_first": f2, "rerun": False,
                             "response_ids": [m2["response_id"]]}
    r2_meta_all = [m2]
    if safety.symbol_gate_requires_stop(f2):
        print(f"[W1][r2] 音声化禁止記号を検出。R2のみ同一R1生出力で1回だけ再実行します(count={len(f2)})...")
        wt(os.path.join(fdir, "r2.first.raw.md"), raw2)
        wt(os.path.join(fdir, "r2.first.final_rejected.md"), final)
        budget_check()                                          # やり直し前
        raw2b, p2b, m2b = astra_stage("r2", os.path.join(fdir, "r1.raw.md"), "w1_astra_r2_symbol_rerun")
        wt(os.path.join(fdir, "r2.rerun.raw.md"), raw2b)
        wj(os.path.join(fdir, "r2.rerun.response.json"), m2b)
        r2_meta_all.append(m2b)
        final_b = clean_ja_for_next(p2b)
        f2b = safety.detect_prohibited_symbols(final_b, language="ja")
        ev["symbol_qa"]["r2"].update({"rerun": True, "findings_after": f2b, "response_ids": [m2["response_id"], m2b["response_id"]]})
        budget_check()                                          # やり直し後
        if safety.symbol_gate_requires_stop(f2b):
            wt(os.path.join(d, "audit", "rejected_w1_r2_symbol.md"), final_b)
            raise JASymbolCheckStopError("r2_symbol", "[STOP] JA_SYMBOL_CHECK_STOP: W-1 R2(Astra)音声化禁止記号Check、"
                                         f"同一入力での再実行後も禁止記号が残りました(findings={f2b})。本文を手で直さずSTOPします。", final_b, f2b)
        final, p2, m2 = final_b, p2b, m2b

    # Astra返却model不一致はSTOP(call_astra内で検査済み。ここでは記録)
    for m in r2_meta_all + [m1]:
        m["model_mismatch"] = not str(m["model"] or "").startswith(ASTRA_MODEL)
    echo = detect_r0_echo(final)
    wt(os.path.join(d, "original.md"), clean0)
    wt(os.path.join(d, "revision1.md"), p1)
    wt(os.path.join(d, "revision2.md"), final)                  # = 下流(EN翻訳)が読む
    ev.update({"original": {"model": r0_calls[-1]["model"], "response_id": r0_calls[-1]["response_id"],
                            "model_requested": R0_MODEL, "r0_calls": r0_calls},
               "r1": m1, "r2": m2, "r2_all_attempts": r2_meta_all, "r2_echo_after_revision": echo,
               "title": extract_title(final), "ja_text_sha256": sha_text(final), "finished":
               datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")})
    wj(os.path.join(d, "runtime_evidence.json"), ev)
    return {"ja_text": final, "title": ev["title"], "runtime_evidence": ev,
            "paths": {"revision2": os.path.join(d, "revision2.md"), "runtime_evidence": os.path.join(d, "runtime_evidence.json")}}
