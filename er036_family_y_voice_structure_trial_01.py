# ============================================================
# er036_family_y_voice_structure_trial_01.py
# FAMILY-Y-VOICE-STRUCTURE-TRIAL-01(ユーザー承認済みTrial、Production配線なし)
# ============================================================
# 目的: Family Y(将来Voices系、CURRENT_SPEC.md L1196「Family Yは将来Voices系を
# 想定した別Family」)の改善Trial。ユーザーが見えている4課題(Voiceによる
# Fact言い直し/後半の抽象論化/Voice間の差の弱さ/記事解説に聞こえる問題)を、
# Fact Selection→Voice Fact Assignment→Angle/Stakeholder先決め→Voice Writer
# (Fact is context, not script)→Family X既存R1→R2 Revisionの適用で改善
# できるかを、既存Family B記事(ai_hiring 3V A2)を対象に検証する。
#
# 既存Family X/Family B/共有moduleのコード・Promptは一切変更しない(import・
# 関数呼び出しによる流用のみ)。詳細な既存仕様確認は
# docs/pm/design_family_y_voice_structure_trial_01.md §1参照。
#
# 費用抑制(Trial限定判断、設計書§5): 新規呼び出し(Voice Fact Assignment/
# Voice Writer/LLM評価)はreasoning_effort="medium"を明示指定する
# (Production既定の"high"はTrial予算¥40の範囲内に収めるため使わない)。
from __future__ import annotations

import argparse
import json
import os
import re
import time

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er012_b_family_production_runner_01 as b1runner  # Production, 読み取り専用import(cost計測)
import er012_b_family_voices_a2_production_01 as a2prod  # Production, 読み取り専用import(言語原則引用)
import er012_b_family_voices_writer_generic_01 as bvoices  # Production, 読み取り専用import(leakage/overlap/parser)
import er019_family_x_ja_writer_o_r1_r2_01 as fx_r1r2  # Family X既存R1→R2(逐語再利用、無変更import)
import er019_family_x_storyline_b3_fact_selection_01 as storyline_b3  # Family X既存Fact Selection(無変更import)

TRIAL_TAG = "FAMILY_Y_VOICE_STRUCTURE_TRIAL_01"
TRIAL_MODEL = routing.WRITER_MODEL  # "gpt-5.6-luna"。previous_response_id連鎖(R1→R2)を
# fx_r1r2.call_fresh/call_with_previous_response_idと共有するため、Voice Writer初回呼び出しも
# 同一modelを使う(fx_r1r2内部はWRITER_MODEL固定のため、呼び出し元も揃える必要がある)。
TRIAL_EFFORT = "medium"  # 設計書§5(費用抑制、Trial限定)

# 使用記事(新規テーマ選定はしない、ユーザー指定の既存Family B記事)。
DEFAULT_TOPIC_JA = (
    "2026年9月時点、多くの企業が採用選考の一部にAI(応募書類の自動スクリーニング、"
    "適性・性格の自動スコアリング、動画面接での表情・話し方の自動評価など)を"
    "取り入れつつある。この記事の中心テーマは、『企業は採用選考にAIを使うべきか』"
    "の賛否をどちらか一つに決めることではなく、この同じ状況について、全く異なる"
    "利害・責任・経験を持つ3人(実際にAIによって評価される応募者[Applicant]、"
    "実際にAIツールを業務で使う採用担当・人事責任者[Recruiter・Hiring Manager]、"
    "そして採用にかかるコスト・速度・会社の存続そのものに個人として責任を負う"
    "経営者[Business Owner])が、それぞれ何を経験し、何を大切にし、何を心配し、"
    "何を守ろうとしているのかを描くことである(er012_b_voices_3v_a2_user_test_01.py "
    "TOPIC_JA_3Vより逐語転記、新規テーマ選定ではない)。"
)
VOICE_STAKEHOLDERS = (
    ("voice_1", "Applicant(応募者。AIスクリーニングを受ける側)"),
    ("voice_2", "Recruiter / Hiring Manager(採用担当・人事責任者。実際にAIツールを使う側)"),
    ("voice_3", "Business Owner(経営者。採用のコスト・速度・会社の存続に責任を負う側)"),
)


# ============================================================
# Step 0: 入力読み込み・Fact Ledgerアダプタ(データ整形のみ、Family X関数は無変更)
# ============================================================
def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


_ENTRY_HEADER_RE = re.compile(
    r"^\[(VOICE_(\d)_EVIDENCE|CROSS_REFERENCE)\]\s+\S+\(([A-Za-z0-9_\-]+)\):\s*(.*)$"
)


def parse_ledger_entries(ledger_fragment: str) -> list:
    """Family B Verified Fact Ledger([TAG] id(fact_id): text 形式、続く
    indented行はsource/counter_or_limitation/verification)を、
    {fact_id, voice_tag, text, verification}のリストへパースする(本Trial専用
    データ整形。Family X/Family Bの既存関数・Promptは一切変更しない)。"""
    lines = ledger_fragment.splitlines()
    entries = []
    i = 0
    n = len(lines)
    while i < n:
        m = _ENTRY_HEADER_RE.match(lines[i])
        if not m:
            i += 1
            continue
        voice_tag = m.group(2)  # "1"/"2"/"3" or None(CROSS_REFERENCE)
        fact_id = m.group(3)
        text_parts = [m.group(4)]
        i += 1
        while i < n and lines[i].strip() != "" and not lines[i].startswith("  "):
            text_parts.append(lines[i].strip())
            i += 1
        fact_text = " ".join(p.strip() for p in text_parts if p.strip())
        verification = None
        while i < n and (lines[i].startswith("  ") or lines[i].strip() == ""):
            vm = re.search(r"verification:\s*(\w+)", lines[i])
            if vm:
                verification = vm.group(1)
            blank = lines[i].strip() == ""
            i += 1
            if blank:
                break
        entries.append({
            "fact_id": fact_id, "voice_tag": voice_tag, "text": fact_text,
            "verification": verification,
        })
    return entries


def build_family_x_compatible_ledger_text(raw_ledger_text: str, num_visible_voices: int = 3) -> tuple:
    """設計書§1のデータ橋渡し: (a) Family B既存
    build_ledger_fragment_visible_voices_only()(無変更import)でVoice 4分を
    除外し、(b) CONFIRMEDな各factを、Family X storyline_b3が要求する
    `[VERIFIED] fact_id: text`形式へ変換する。戻り値: (ledger_text_for_family_x,
    fact_entries[voice_tag付き, CONFIRMEDのみ])。"""
    fragment = bvoices.build_ledger_fragment_visible_voices_only(
        raw_ledger_text, num_visible_voices=num_visible_voices)
    entries = parse_ledger_entries(fragment)
    confirmed = [e for e in entries if e["verification"] == "CONFIRMED"]
    lines = [f"[VERIFIED] {e['fact_id']}: {e['text']}" for e in confirmed]
    return "\n".join(lines), confirmed


# ============================================================
# Step 1: Fact Selection(Family X既存 storyline_b3.run_storyline_b3_selection、無変更import)
# ============================================================
def run_step1_fact_selection(client, topic_ja: str, ledger_text_family_x: str, out_dir: str) -> dict:
    result = storyline_b3.run_storyline_b3_selection(
        client, topic=topic_ja, ledger_text=ledger_text_family_x,
        model=TRIAL_MODEL, effort=TRIAL_EFFORT,
    )
    save_json(f"{out_dir}/step1_fact_selection.json", result)
    return result


# ============================================================
# Step 2: Voice Fact Assignment + Angle/Stakeholder(新規、本Trial固有、LLM 1 call)
# ============================================================
VOICE_ASSIGNMENT_DEVELOPER_MESSAGE = (
    "You assign a small set of already-selected facts to three first-person Voices in a "
    "'Voices/Perspective' style article. Each Voice represents one stakeholder. Your job is only "
    "to decide, for each Voice: which 1-2 facts (from the selected set only) they may use as "
    "background context, their stakeholder label, and their angle (what they personally look at "
    "in this situation). You do not write any article text."
)

VOICE_ASSIGNMENT_JSON_SCHEMA = {
    "name": "voice_fact_assignment",
    "schema": {
        "type": "object",
        "properties": {
            "voices": {
                "type": "array",
                "minItems": 3, "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "voice_key": {"type": "string", "enum": ["voice_1", "voice_2", "voice_3"]},
                        "stakeholder": {"type": "string"},
                        "angle": {"type": "string"},
                        "fact_ids": {
                            "type": "array", "minItems": 1, "maxItems": 2,
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["voice_key", "stakeholder", "angle", "fact_ids"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["voices"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_voice_assignment_prompt(selected_fact_brief: str, selected_fact_ids: list) -> str:
    stakeholder_lines = "\n".join(f"- {k}: {label}" for k, label in VOICE_STAKEHOLDERS)
    return f"""【Selected Fact Brief(Step 1で選定済み、これ以外のFactは存在しないものとして扱うこと)】
{selected_fact_brief}

【選定済みfact_id一覧】
{", ".join(selected_fact_ids)}

【3つのVoice(固定、stakeholderの候補ラベル)】
{stakeholder_lines}

各Voiceについて、以下を決めてください(記事本文は書かない):
- stakeholder: 上記候補ラベルをそのまま使うか、内容に応じて自然な言い方に微調整してよい
- angle: このVoiceが自分の状況の中で何を見て、何を気にしているか(1〜2文、英語)
- fact_ids: 上記の選定済みfact_id一覧の中から、このVoiceが背景として使ってよいFactを
  原則1件、必要な場合のみ最大2件選ぶこと(全Voice共通の1セットを機械的に割り当てない。
  3つのVoiceの fact_ids の集合が完全に同一にならないようにすること)。
"""


def run_step2_voice_assignment(client, selected_fact_brief: str, selected_fact_ids: list, out_dir: str) -> dict:
    prompt = build_voice_assignment_prompt(selected_fact_brief, selected_fact_ids)
    response = client.responses.create(
        model=TRIAL_MODEL, reasoning={"effort": TRIAL_EFFORT},
        text={"format": {"type": "json_schema", **VOICE_ASSIGNMENT_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": VOICE_ASSIGNMENT_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    parsed = json.loads(response.output_text)
    result = {"parsed": parsed, "model": response.model, "response_id": response.id, "prompt": prompt}
    save_json(f"{out_dir}/step2_voice_fact_assignment.json", result)
    return result


def validate_voice_assignment(parsed: dict, selected_fact_ids: list) -> list:
    """技術的整合性エラー(空リスト=有効)。1 Voice=fact 1〜2件・選定済みfact_id
    のみ使用・全Voice同一fact集合の禁止、を検証する(単体testでも使用)。"""
    errors = []
    voices = parsed.get("voices") or []
    if len(voices) != 3:
        errors.append(f"VOICE_COUNT_NOT_3: {len(voices)}")
        return errors
    fact_id_set = set(selected_fact_ids)
    fact_sets = []
    for v in voices:
        fids = v.get("fact_ids") or []
        if not (1 <= len(fids) <= 2):
            errors.append(f"FACT_IDS_COUNT_OUT_OF_RANGE({v.get('voice_key')}): {fids}")
        unknown = [f for f in fids if f not in fact_id_set]
        if unknown:
            errors.append(f"UNKNOWN_FACT_ID({v.get('voice_key')}): {unknown}")
        fact_sets.append(frozenset(fids))
    if len(set(fact_sets)) == 1 and len(fact_sets) == 3:
        errors.append("ALL_VOICES_SAME_FACT_SET")
    return errors


# ============================================================
# Step 3/4/5: Voice Writer(新規、本Trial固有、最小Writer call。Family B
# a2prod.A2_KAI1_INSTRUCTION_PARA1_PARA3 / CORE_EXPLANATORY_LOGIC_PRESERVATION
# を逐語引用[import、無変更]。禁止語リストにはしない方針文のみ追加)。
# ============================================================
VOICE_WRITER_DEVELOPER_MESSAGE = (
    "You write a 'Voices/Perspective' style article: one shared Hook paragraph, three first-person "
    "Voice sections, one Tension section, and one Closing section. Output the full article now."
)

VOICE_WRITER_POLICY_BLOCK = """【本Trial固有の方針(FAMILY-Y-VOICE-STRUCTURE-TRIAL-01、禁止語リストではなく方針文)】
- Fact is context, not script: 各Voiceに割り当てられたFactは、その人がすでに知っている
  背景・出来事として自然に触れてよいが、Factそのものを解説し直す・引用し直すことが
  文章の中心になってはならない。中心は、その人の反応・懸念・期待・経験則である。
- Fact紹介から書き始めない: 「According to the report...」「The company said...」
  「The study found...」「A survey found that...」のような、調査・報告・データを
  主語にした文からVoiceを書き始めない方向で書くこと。内容上どうしても必要な場合を
  機械的に禁止するものではないが、基本方針として避けること。
- 最後まで具体的なStakeholder/状況を持つ: 各Voiceは、society/trust/the future/
  technology in generalのような大きな抽象論へ最後に逃げず、自分自身の具体的な
  状況・判断・懸念を最後まで保つこと(内容上必要ならこれらの言葉自体の使用を
  機械的に禁止しない)。
- Tension/Closingについても、単なる要約や「人による」という結び、Writer自身の
  解決策提案だけで終わらせないこと。3人の合理性がなぜ単純に足し合わさらないのかを
  具体的に描くこと。"""

VOICE_WRITER_OUTPUT_FORMAT = """【出力形式】
以下のMarkdown構造で、記事全文だけを出力してください(説明文・コメントは付けない)。
`# ` Title(1つ)
`## ` Hookの見出し(1つ、その直後にHook本文)
`### ` Voice 1の見出し(1つ、その直後にVoice 1本文、一人称"I")
`### ` Voice 2の見出し(1つ、その直後にVoice 2本文、一人称"I")
`### ` Voice 3の見出し(1つ、その直後にVoice 3本文、一人称"I")
`## ` Tensionの見出し(1つ、その直後にTension本文)
`## ` Closingの見出し(1つ、その直後にClosing本文)
(合計、`# `1つ+`##`/`###`見出し6つ)"""


def build_fact_context_block(assigned_voices: list, fact_by_id: dict) -> str:
    lines = []
    for v in assigned_voices:
        fact_lines = "; ".join(fact_by_id.get(fid, f"(fact_id {fid} not found)") for fid in v["fact_ids"])
        lines.append(
            f"- {v['voice_key']} ({v['stakeholder']}): angle = {v['angle']}\n"
            f"  assigned facts (context only, do not restate as a report): {fact_lines}"
        )
    return "\n".join(lines)


def build_voice_writer_prompt(topic_ja: str, selected_storyline: str, assigned_voices: list,
                               fact_by_id: dict) -> str:
    fact_context_block = build_fact_context_block(assigned_voices, fact_by_id)
    return f"""【テーマ(日本語、参考)】
{topic_ja}

【中心Storyline(Step 1で決定)】
{selected_storyline}

【Voiceごとの割当(Step 2で決定済み、fact_idはcontextであり本文に番号やIDを書かない)】
{fact_context_block}

{VOICE_WRITER_POLICY_BLOCK}

【言語原則(Family B既存Production言語原則、CURRENT_SPEC.md CEFR-A2節からの逐語引用)】
{a2prod.A2_KAI1_INSTRUCTION_PARA1_PARA3}

{a2prod.CORE_EXPLANATORY_LOGIC_PRESERVATION}

{VOICE_WRITER_OUTPUT_FORMAT}"""


def run_step34_voice_writer(client, topic_ja: str, selected_storyline: str, assigned_voices: list,
                             fact_by_id: dict, out_dir: str):
    prompt = build_voice_writer_prompt(topic_ja, selected_storyline, assigned_voices, fact_by_id)
    response = fx_r1r2.call_fresh(
        client, developer=VOICE_WRITER_DEVELOPER_MESSAGE, user=prompt,
        effort=TRIAL_EFFORT, stage="voice_writer_r1",
    )
    text = (response.output_text or "").strip()
    save_json(f"{out_dir}/step34_voice_writer_r1_raw.json", {
        "prompt": prompt, "text": text, "model": response.model, "response_id": response.id,
    })
    return response, text


# ============================================================
# Step 7: R1→R2(Family X既存Revision、無変更import)
# ============================================================
def run_r1_to_r2(client, r1_response, out_dir: str) -> dict:
    r1_resp = fx_r1r2.call_with_previous_response_id(
        client, user=fx_r1r2.REVISION_INSTRUCTIONS["r1"], effort=TRIAL_EFFORT,
        previous_response_id=r1_response.id, stage="r1",
    )
    r1_text = (r1_resp.output_text or "").strip()
    r2_resp = fx_r1r2.call_with_previous_response_id(
        client, user=fx_r1r2.REVISION_INSTRUCTIONS["r2"], effort=TRIAL_EFFORT,
        previous_response_id=r1_resp.id, stage="r2",
    )
    r2_text = (r2_resp.output_text or "").strip()
    result = {
        "r1_after_revision_text": r1_text, "r1_after_revision_response_id": r1_resp.id,
        "r2_text": r2_text, "r2_response_id": r2_resp.id,
        "revision_instructions_used": fx_r1r2.REVISION_INSTRUCTIONS,
        "note": ("Family X既存er019_family_x_ja_writer_o_r1_r2_01.pyのREVISION_INSTRUCTIONS"
                 "['r1']/['r2'](逐語、日本語指示文)+call_with_previous_response_id"
                 "(previous_response_id連鎖)をそのまま再利用した(設計書§1分類B参照)。"
                 "JA専用Fact Check/音声化禁止記号チェックは適用していない。"),
    }
    save_json(f"{out_dir}/step7_r1_to_r2.json", result)
    return result


# ============================================================
# 評価: 決定論的指標
# ============================================================
FACT_INTRO_OPENER_RE = re.compile(
    r"^(According to|The (study|report|survey|research|company|dashboard) (found|shows|showed|said|says)"
    r"|A (survey|study|report) (found|shows|showed)|Research (shows|found|showed)"
    r"|Reports? (show|shows|indicate|indicates)|Data (shows|show)|One (company|report)"
    r"|\d+%\s+of)",
    re.IGNORECASE,
)

ABSTRACTION_TERMS = (
    "society", "trust", "the future", "technology in general", "humanity",
    "in general", "the world", "everyone",
)


def first_sentence(text: str) -> str:
    m = re.search(r"[.!?]", text)
    return text[:m.start() + 1].strip() if m else text.strip()


def detect_fact_intro_opener(voice_body: str) -> bool:
    return bool(FACT_INTRO_OPENER_RE.match(first_sentence(voice_body)))


def find_abstraction_positions(text: str) -> list:
    lower = text.lower()
    n = len(lower) or 1
    hits = []
    for term in ABSTRACTION_TERMS:
        idx = 0
        while True:
            idx = lower.find(term, idx)
            if idx == -1:
                break
            hits.append({"term": term, "char_index": idx, "relative_position": round(idx / n, 3)})
            idx += len(term)
    return hits


def word_count(text: str) -> int:
    return len(text.split())


def run_deterministic_metrics(sections: dict, voice_fact_ids: dict | None) -> dict:
    voice_keys = ("voice_1", "voice_2", "voice_3")
    fact_intro_openers = {vk: detect_fact_intro_opener(sections[f"{vk}_body"]) for vk in voice_keys}
    abstraction = {
        key: find_abstraction_positions(sections[f"{key}_body" if key in voice_keys else key])
        for key in list(voice_keys) + ["tension_body", "closing_body"]
    }
    words = {
        key: word_count(sections[f"{key}_body" if key in voice_keys else key])
        for key in list(voice_keys) + ["hook_body", "tension_body", "closing_body"]
    }
    fact_overlap = None
    if voice_fact_ids:
        sets = {vk: frozenset(voice_fact_ids.get(vk, [])) for vk in voice_keys}
        pairs = {}
        for a in voice_keys:
            for b in voice_keys:
                if a < b:
                    pairs[f"{a}_vs_{b}"] = sorted(sets[a] & sets[b])
        fact_overlap = {
            "fact_ids_by_voice": {k: sorted(v) for k, v in sets.items()},
            "pairwise_shared_fact_ids": pairs,
            "any_shared": any(pairs.values()),
        }
    return {
        "fact_intro_openers": fact_intro_openers,
        "any_fact_intro_opener": any(fact_intro_openers.values()),
        "abstraction_term_positions": abstraction,
        "word_counts": words,
        "fact_id_overlap_between_voices": fact_overlap,
    }


# ============================================================
# 評価: Family B既存Leakage/Overlap(無変更import、Before/R1/R2共通で使用)
# ============================================================
def run_family_b_qa(client, sections: dict, out_dir: str, attempt_label: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    overlap = bvoices.run_overlap_monitoring_3v(sections, out_dir)
    leakage = bvoices.run_analytical_leakage_check_3v(
        client, sections, model=TRIAL_MODEL, reasoning_effort=TRIAL_EFFORT,
        out_dir=out_dir, attempt=attempt_label, external_constraint_enabled=False,
    )
    return {"overlap_monitoring_3v": overlap, "analytical_leakage_check_3v": leakage}


# ============================================================
# 評価: LLM rubric 1 call(4課題 x Before/R1/R2)
# ============================================================
CHALLENGE_KEYS = (
    "challenge_1_fact_restating", "challenge_2_voice_differentiation",
    "challenge_3_abstraction_drift", "challenge_4_person_not_explainer",
)

RUBRIC_JSON_SCHEMA = {
    "name": "family_y_voice_rubric_eval",
    "schema": {
        "type": "object",
        "properties": {
            stage: {
                "type": "object",
                "properties": {
                    k: {
                        "type": "object",
                        "properties": {
                            "score_1_to_5": {"type": "integer"},
                            "evidence_quote": {"type": "string"},
                        },
                        "required": ["score_1_to_5", "evidence_quote"],
                        "additionalProperties": False,
                    } for k in CHALLENGE_KEYS
                },
                "required": list(CHALLENGE_KEYS),
                "additionalProperties": False,
            } for stage in ("before", "r1", "r2")
        },
        "required": ["before", "r1", "r2"],
        "additionalProperties": False,
    },
    "strict": True,
}

RUBRIC_DEVELOPER_MESSAGE = (
    "You are an editorial QA rater comparing three versions (Before/R1/R2) of the same "
    "'Voices/Perspective' article on four known problems. For each version and each problem, give a "
    "score from 1 (problem is clearly present / severe) to 5 (problem is clearly resolved), and quote "
    "one short piece of evidence from that version's text."
)

RUBRIC_PROMPT_TEMPLATE = """4つの既知の課題について、Before/R1/R2それぞれを1〜5点で評価してください。

【課題定義】
- challenge_1_fact_restating: Voiceが調査・報告・データをFactとして解説し直していないか
  (1=強く言い直している、5=Factは背景に留まり本人の反応が中心)
- challenge_2_voice_differentiation: 3つのVoiceの違いが明確か
  (1=どのVoiceも似た内容・似た結論、5=立場・懸念・結論が明確に異なる)
- challenge_3_abstraction_drift: Tension/Closingが後半で大きな抽象論
  (society/trust/the future等)へ流れていないか
  (1=強く抽象論へ流れている、5=最後まで具体的な人物・状況を保っている)
- challenge_4_person_not_explainer: Voiceが「記事解説」ではなく「独立した人の発言」に
  聞こえるか(1=語り手による説明・要約に聞こえる、5=本人の発言に聞こえる)

【Before(既存Family B出力、比較対象)】
{before_text}

【R1(本Trial、Revision前)】
{r1_text}

【R2(本Trial、Family X既存R1→R2 Revision適用後)】
{r2_text}
"""


def run_rubric_eval(client, before_text: str, r1_text: str, r2_text: str, out_dir: str) -> dict:
    prompt = RUBRIC_PROMPT_TEMPLATE.format(before_text=before_text, r1_text=r1_text, r2_text=r2_text)
    response = client.responses.create(
        model=TRIAL_MODEL, reasoning={"effort": TRIAL_EFFORT},
        text={"format": {"type": "json_schema", **RUBRIC_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": RUBRIC_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    parsed = json.loads(response.output_text)
    result = {"parsed": parsed, "model": response.model, "response_id": response.id, "prompt": prompt}
    save_json(f"{out_dir}/rubric_eval.json", result)
    return result


# ============================================================
# main
# ============================================================
def assemble_markdown(sections: dict, title: str) -> str:
    return (
        f"# {title}\n\n"
        f"## {sections['hook_heading']}\n\n{sections['hook_body']}\n\n"
        f"### {sections['voice_1_heading']}\n\n{sections['voice_1_body']}\n\n"
        f"### {sections['voice_2_heading']}\n\n{sections['voice_2_body']}\n\n"
        f"### {sections['voice_3_heading']}\n\n{sections['voice_3_body']}\n\n"
        f"## {sections['tension_heading']}\n\n{sections['tension_body']}\n\n"
        f"## {sections['closing_heading']}\n\n{sections['closing_body']}\n"
    )


def parse_article_or_raise(article_text: str, label: str) -> dict:
    sections = bvoices.split_six_voice_sections(article_text)
    if sections is None:
        raise RuntimeError(f"[STOP] {label}: 6区切り構造(3V)の検出に失敗しました。article_text={article_text[:500]!r}")
    return sections


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--level", default="a2")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--budget-jpy", type=float, default=40.0)
    args = parser.parse_args()

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    cost_log_path = f"{out_dir}/audit/raw_usage_log.jsonl"
    cl.install(cost_log_path)

    from openai import OpenAI
    client = OpenAI()

    def budget_check(note: str):
        jpy, by_provider = b1runner.compute_cost_jpy_so_far(cost_log_path)
        print(f"[{TRIAL_TAG}][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
        if jpy > args.budget_jpy:
            raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {args.budget_jpy} JPY ({note})")
        return jpy

    # --- Before(既存Family B出力) ---
    before_parts = load_json(f"{args.source_dir}/{args.level}/parts.json")
    before_sections = before_parts["sections"]
    before_text = load_text(f"{args.source_dir}/{args.level}/article.md")
    save_json(f"{out_dir}/before_sections.json", before_sections)

    # --- 入力Fact Ledger ---
    raw_ledger_text = load_text(
        "er012_output/ai_screening_ledger_trial_01/research/verified_fact_ledger.txt")
    ledger_text_fx, confirmed_entries = build_family_x_compatible_ledger_text(raw_ledger_text)
    save_json(f"{out_dir}/ledger_adapter_output.json", {
        "ledger_text_for_family_x": ledger_text_fx, "confirmed_entries": confirmed_entries,
    })
    fact_by_id = {e["fact_id"]: e["text"] for e in confirmed_entries}

    # --- Step 1: Fact Selection(Family X既存、無変更) ---
    step1 = run_step1_fact_selection(client, DEFAULT_TOPIC_JA, ledger_text_fx, out_dir)
    budget_check("after step1 fact selection")
    selected_fact_ids = step1["parsed"]["selected_fact_ids"]
    selected_storyline = step1["parsed"]["selected_storyline"]
    selected_fact_brief = step1["parsed"]["selected_fact_brief"]

    # --- Step 2: Voice Fact Assignment + Angle/Stakeholder(新規) ---
    step2 = run_step2_voice_assignment(client, selected_fact_brief, selected_fact_ids, out_dir)
    budget_check("after step2 voice fact assignment")
    assignment_errors = validate_voice_assignment(step2["parsed"], selected_fact_ids)
    save_json(f"{out_dir}/step2_validation_errors.json", {"errors": assignment_errors})
    if assignment_errors:
        print(f"[{TRIAL_TAG}][WARN] Voice Fact Assignment validation errors: {assignment_errors}")
    assigned_voices = step2["parsed"]["voices"]
    voice_fact_ids = {v["voice_key"]: v["fact_ids"] for v in assigned_voices}

    # --- Step 3/4/5: Voice Writer(新規、R1初回応答) ---
    r1_response, r1_raw_text = run_step34_voice_writer(
        client, DEFAULT_TOPIC_JA, selected_storyline, assigned_voices, fact_by_id, out_dir)
    budget_check("after step3-5 voice writer (R1 draft)")
    r1_sections = parse_article_or_raise(r1_raw_text, "R1 draft")
    save_json(f"{out_dir}/r1_sections.json", r1_sections)

    # --- Step 7: R1→R2(Family X既存Revision) ---
    r1r2 = run_r1_to_r2(client, r1_response, out_dir)
    budget_check("after step7 r1->r2 revision")
    r2_sections = parse_article_or_raise(r1r2["r2_text"], "R2")
    save_json(f"{out_dir}/r2_sections.json", r2_sections)

    # --- 評価: 決定論的指標 ---
    metrics_before = run_deterministic_metrics(before_sections, None)
    metrics_r1 = run_deterministic_metrics(r1_sections, voice_fact_ids)
    metrics_r2 = run_deterministic_metrics(r2_sections, voice_fact_ids)
    save_json(f"{out_dir}/deterministic_metrics.json", {
        "before": metrics_before, "r1": metrics_r1, "r2": metrics_r2,
    })

    # --- 評価: Family B既存Leakage/Overlap ---
    qa_before = run_family_b_qa(client, before_sections, f"{out_dir}/qa_before", "before")
    budget_check("after family b qa (before)")
    qa_r1 = run_family_b_qa(client, r1_sections, f"{out_dir}/qa_r1", "r1")
    budget_check("after family b qa (r1)")
    qa_r2 = run_family_b_qa(client, r2_sections, f"{out_dir}/qa_r2", "r2")
    budget_check("after family b qa (r2)")

    # --- 評価: LLM rubric ---
    r1_full_text = assemble_markdown(r1_sections, before_parts.get("title", ""))
    r2_full_text = assemble_markdown(r2_sections, before_parts.get("title", ""))
    rubric = run_rubric_eval(client, before_text, r1_full_text, r2_full_text, out_dir)
    final_jpy = budget_check("final")

    summary = {
        "management_id": "FAMILY-Y-VOICE-STRUCTURE-TRIAL-01",
        "source_dir": args.source_dir, "level": args.level,
        "selected_storyline": selected_storyline, "selected_fact_ids": selected_fact_ids,
        "voice_assignment": assigned_voices, "assignment_validation_errors": assignment_errors,
        "cost_jpy_final": final_jpy,
        "deterministic_metrics": {"before": metrics_before, "r1": metrics_r1, "r2": metrics_r2},
        "family_b_qa": {
            "before": {"any_flagged": qa_before["analytical_leakage_check_3v"]["any_flagged"],
                       "overlap_any_flagged": qa_before["overlap_monitoring_3v"]["any_flagged"]},
            "r1": {"any_flagged": qa_r1["analytical_leakage_check_3v"]["any_flagged"],
                   "overlap_any_flagged": qa_r1["overlap_monitoring_3v"]["any_flagged"]},
            "r2": {"any_flagged": qa_r2["analytical_leakage_check_3v"]["any_flagged"],
                   "overlap_any_flagged": qa_r2["overlap_monitoring_3v"]["any_flagged"]},
        },
        "rubric_eval": rubric["parsed"],
    }
    save_json(f"{out_dir}/summary.json", summary)
    with open(f"{out_dir}/r1_article.md", "w", encoding="utf-8") as f:
        f.write(r1_full_text)
    with open(f"{out_dir}/r2_article.md", "w", encoding="utf-8") as f:
        f.write(r2_full_text)

    print(f"[{TRIAL_TAG}] 完了。summary={out_dir}/summary.json cost_jpy_final={final_jpy:.2f}")


if __name__ == "__main__":
    main()
