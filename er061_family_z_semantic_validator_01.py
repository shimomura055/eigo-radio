"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_04A: Family Z 意味保持Validator。

旧「人物名検査」(er026 check_character_name_rule / restore_character_names)を
superseded とし、名前の有無ではなく「人物の役割・関係 / 重要出来事 / 因果 / 順序 /
結末 / 魅力」の保持で検証する(DECISION_LOG 2026-10-12決定)。Family Z一般仕様
(story_key非依存)。権利Gate(Z-1)・外国人名ルール(項目4)は維持する。

構成:
  - validator_anchors: 原作・Seedのみから作成(新稿を見る前)、sha256凍結
  - 第1層(決定論): hard FAILは高精度項目のみ(禁止結末family/外国人名ルール/主要アンカー全欠落)
  - 第2層(LLM, routing FAMILY_Z_SEMANTIC_JUDGE=gpt-6-luna, JSON schema strict):
        項目別 preserved/altered/missing、evidence_quote逐語検証、FAIL時は再判定1回(2回一致でFAIL)
  - 食い違い(第1層FAIL x 第2層非FAIL等)= NEEDS_REVIEW -> STOP(自動では通さない)
  - Std用追加: Adv同一本文判定(>=50%でFAIL)/平均文長soft gate(WARN)/段落数・順序一致
  - revalidate_after_local_rewrite: Local Rewrite後の第1層再実行+差分記録
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import warnings

import er006_model_routing_contract_01 as routing

JUDGE_ROUTING_KEY = "FAMILY_Z_SEMANTIC_JUDGE"
SEED_DIR = "er026_output/family_z_production_e2e_01/melos/seed"
VALIDATOR_DIR = "er026_output/family_z_production_e2e_01/melos/validator"
ANCHORS_PATH = f"{VALIDATOR_DIR}/anchors.json"
CALIBRATION_PATH = "er060_output/melos_production_e2e_01/validator_calibration_01.json"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0  # er005_cost_logger / er018と同一値
CALIBRATION_CAP_JPY = 8.0
SCHEMA_VERSION = "er061_validator_result_v1"

STD_IDENTICAL_FAIL_RATIO = 0.50      # M8: 一致文率 >= 50% でFAIL
STD_AVG_SENTENCE_LEN_MAX_RATIO = 0.85  # soft gate(WARN)
ENDING_SCAN_PARAGRAPHS = 3           # 禁止結末familyは末尾N段落だけを走査(高精度化)

CATEGORIES = ("role_relation", "event", "causality", "sequence", "ending", "charm", "added_fact")
STATUSES = ("preserved", "altered", "missing")
SEVERITIES = ("none", "minor", "major")


class AnchorsIntegrityError(RuntimeError):
    pass


class JudgeBudgetExceeded(RuntimeError):
    pass


class JudgeModelMismatch(RuntimeError):
    pass


# ============================================================
# helpers
# ============================================================
def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _canonical_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def split_paragraphs(text: str) -> list:
    """Markdown見出し行(#...)を除いた段落(空行区切り)のリスト。"""
    paras = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n")):
        lines = [ln for ln in block.split("\n") if not ln.strip().startswith("#")]
        p = " ".join(ln.strip() for ln in lines).strip()
        if p:
            paras.append(p)
    return paras


def split_sentences(text: str) -> list:
    sents = []
    for p in split_paragraphs(text):
        for s in re.split(r"(?<=[.!?])[\"”’']?\s+", p):
            s = s.strip()
            if s:
                sents.append(s)
    return sents


def _norm_quote_text(s: str) -> str:
    s = (s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
          .replace("—", "-").replace("–", "-").replace("…", "..."))
    s = s.replace("*", "").replace("_", " ")
    return re.sub(r"\s+", " ", s).strip().casefold()


def _norm_sentence(s: str) -> str:
    s = _norm_quote_text(s)
    s = re.sub(r"[^\w\s']", "", s)
    return re.sub(r"\s+", " ", s).strip()


def quote_is_verbatim(quote: str, candidate_text: str) -> bool:
    """evidence_quoteが候補本文に逐語(表記ゆれ=引用符/空白/大小/Markdown強調のみ正規化)で存在するか。"""
    q = _norm_quote_text(quote or "")
    if len(q) < 3:
        return False
    return q in _norm_quote_text(candidate_text)


# ============================================================
# validator_anchors(原作・Seedのみから作成、新稿を見る前、sha凍結)
# ============================================================
# 以下は seed.json(seed_elements 0-5)と primary_text_excerpt.md(原作の冒頭・クライマックス・
# 結末の逐語引用)だけを根拠に作成した定数。候補稿(Writer出力)は一切参照していない。
_ANCHOR_SPEC = [
    # --- 人物の役割・関係 ---
    {"id": "R1", "category": "role_relation", "seed_element_index": 0, "order": 1, "required": True,
     "concept_family": ["melos", "shepherd"],
     "description_en": "Melos is a simple shepherd (not a politician) who bravely speaks out against the tyrant.",
     "description_ja": "メロスは政治がわからぬ村の牧人で、暴君に直接異を唱える主人公。"},
    {"id": "R2", "category": "role_relation", "seed_element_index": 0, "order": 2, "required": True,
     "concept_family": ["ruler", "king", "tyrant"],
     "description_en": "The ruler is a tyrant (fearful of enemies) who executes people on suspicion, without fair trials.",
     "description_ja": "王は人を疑い、公正な裁きなしに処刑する邪智暴虐の暴君。"},
    {"id": "R3", "category": "role_relation", "seed_element_index": 1, "order": 3, "required": True,
     "concept_family": ["friend", "hostage"],
     "description_en": "Melos has a close friend who stays behind as a hostage in his place and trusts him; the friend relationship (mutual trust) is the emotional core.",
     "description_ja": "メロスには身代わり人質として残り、彼を信じる親友がいる。この友という関係(相互の信頼)が物語の核。"},
    # --- 重要出来事(順序付き) ---
    {"id": "E1", "category": "event", "seed_element_index": 0, "order": 4, "required": True,
     "concept_family": ["die", "death", "execut", "sentence", "kill"],
     "description_en": "Melos denounces the tyrant and is sentenced to death.",
     "description_ja": "メロスが暴君を批判し、死刑を宣告される。"},
    {"id": "E2", "category": "event", "seed_element_index": 1, "order": 5, "required": True,
     "concept_family": ["wedding", "sister", "three days", "3 days", "days"],
     "description_en": "Melos is granted three days to attend his sister's wedding, with his friend held hostage until he returns.",
     "description_ja": "妹の結婚式に出るため3日間の猶予を得て、その間は友が人質に残る。"},
    {"id": "E3", "category": "event", "seed_element_index": 3, "order": 6, "required": True,
     "concept_family": ["river", "flood", "water", "bandit", "attacker", "robber", "men", "stick"],
     "description_en": "On the way back, obstacles (a flooded/wild river and attackers/bandits) delay and weaken him.",
     "description_ja": "帰路で川(増水)や襲撃者などの障害に遭い、遅れて消耗する。"},
    {"id": "E4", "category": "event", "seed_element_index": 4, "order": 7, "required": True,
     "concept_family": ["give up", "rest", "stay alive", "wanted to", "cannot", "can't", "exhaust", "hide", "forget", "fell", "weak"],
     "description_en": "At his lowest point, exhausted, Melos is tempted to give up and let his friend die.",
     "description_ja": "どん底で疲れ果て、友を見捨てて諦めたくなる誘惑に陥る。"},
    {"id": "E5", "category": "event", "seed_element_index": 4, "order": 8, "required": True,
     "concept_family": ["promise", "trust", "remember", "word", "waiting"],
     "description_en": "He revives and recommits to his promise through trust in his friend.",
     "description_ja": "友への信頼と約束を思い出して立ち上がり、再び走り出す。"},
    {"id": "E6", "category": "event", "seed_element_index": 5, "order": 9, "required": True,
     "concept_family": ["in time", "sunset", "sun", "stop", "wait", "square", "gate", "execution", "sword", "guard", "i'm here", "i am here"],
     "description_en": "Melos arrives at the execution ground just in time, at the last moment.",
     "description_ja": "メロスが刑場に処刑の直前、ぎりぎりで間に合う。"},
    # --- 因果 ---
    {"id": "C1", "category": "causality", "seed_element_index": 0, "order": 10, "required": False,
     "concept_family": [],
     "description_en": "Cause->effect: Melos's open denunciation of the tyrant is why he is sentenced to death (the tyrant's cruelty comes first; Melos reacts to it).",
     "description_ja": "因果: 暴君の悪行に怒ったメロスが直接批判したことが死刑宣告の原因(暴君の悪行が先、メロスの批判はそれへの反応)。"},
    {"id": "C2", "category": "causality", "seed_element_index": 1, "order": 11, "required": False,
     "concept_family": [],
     "description_en": "Cause->effect: the friend voluntarily stays as hostage out of trust, which is what makes Melos's promise life-or-death (if he fails to return, the friend dies).",
     "description_ja": "因果: 友が信頼から自ら人質に残ることで、メロスが戻れなければ友が死ぬという約束の重みが生まれる。"},
    {"id": "C3", "category": "causality", "seed_element_index": 4, "order": 12, "required": False,
     "concept_family": [],
     "description_en": "Cause->effect: Melos recovers his resolve because he remembers his friend's trust and his own promise (not because of fear or outside force).",
     "description_ja": "因果: メロスが立ち直るのは、友の信頼と自分の約束を思い出したから(恐れや外圧のためではない)。"},
    {"id": "C4", "category": "causality", "seed_element_index": 5, "order": 13, "required": False,
     "concept_family": [],
     "description_en": "Cause->effect: Melos keeping his promise and the two friends' mutual loyalty is what saves the friend and moves the ruler to change.",
     "description_ja": "因果: メロスが約束を守り二人が互いに信じ抜いたことが、友の救出と王の心の変化(改心)の原因。"},
    # --- 順序 ---
    {"id": "S1", "category": "sequence", "seed_element_index": -1, "order": 14, "required": False,
     "concept_family": [],
     "description_en": "Overall order of events: denounces tyrant/sentenced -> three-day grace with friend as hostage -> journey back with obstacles (river, attackers) -> exhaustion and temptation to give up -> renewed resolve -> arrival just in time -> friend freed and ruler changed.",
     "description_ja": "全体の順序: 批判・死刑宣告 -> 3日の猶予と友の人質 -> 帰路の障害(川・襲撃) -> 疲労と諦めの誘惑 -> 立ち直り -> 間に合う -> 友の救出と王の改心。"},
    # --- 結末 ---
    {"id": "N1", "category": "ending", "seed_element_index": 5, "order": 15, "required": True,
     "concept_family": ["free", "let them", "both", "changed", "fair trial", "join", "trust"],
     "description_en": "Ending: Melos is in time, the friend is freed (nobody dies), and the ruler is moved by their loyalty and mutual trust and changes his heart.",
     "description_ja": "結末: 間に合い、友は解放され(誰も死なない)、王は二人の信実に心を動かされて改心する。"},
    # --- 魅力 ---
    {"id": "M1", "category": "charm", "seed_element_index": 4, "order": 16, "required": False,
     "concept_family": [],
     "description_en": "Charm: the theme that trust and loyalty between friends is real and stronger than the tyrant's cynicism; an emotional low point followed by a hopeful, moving finish.",
     "description_ja": "魅力: 友情・信実は空虚な妄想ではなく暴君の疑いより強いという主題と、どん底からの感動的な立ち直り。"},
    {"id": "M2", "category": "charm", "seed_element_index": 2, "order": 17, "required": False,
     "concept_family": [],
     "description_en": "Charm: the race against time/the setting sun (deadline tension) as Melos runs back to the city.",
     "description_ja": "魅力: 日没までに間に合うかという時間との競走の緊迫感。"},
    # --- 新Fact追加なし ---
    {"id": "X1", "category": "added_fact", "seed_element_index": -1, "order": 18, "required": False,
     "concept_family": [],
     "description_en": "No major new facts/events/characters invented that change the story (e.g., supernatural helpers, new relatives, extra villains, different motives). Simplification and re-wording are fine.",
     "description_ja": "物語を変えるような重大な新Fact(超自然の助け手、新たな親族、追加の敵、別の動機など)が捏造されていないこと。簡略化・言い換えは許容。"},
]

_FORBIDDEN_ENDINGS = [
    {"id": "FE1_too_late",
     "description_ja": "間に合わない結末(末尾段落で'too late'等)",
     "patterns": [r"\btoo late\b", r"\b(?:came|arrived|got there|was|were) late\b",
                  r"\bhad already (?:fallen|been executed|been killed|died|ended)\b"]},
    {"id": "FE2_friend_dies",
     "description_ja": "友が死ぬ/処刑される結末(末尾段落)",
     "patterns": [r"\b(?:friend|man) (?:was|had been) (?:killed|executed|dead)\b",
                  r"\b(?:friend|man) (?:died|lay dead|lay still)\b",
                  r"\b(?:both|them both|the two (?:men|friends)) (?:were|was) (?:killed|executed)\b"]},
    {"id": "FE3_ruler_unchanged",
     "description_ja": "王が改心しない/約束を反故にする結末(末尾段落)",
     "patterns": [r"\bthe (?:ruler|king|tyrant) (?:refused|did not (?:change|listen|forgive|free|release)|did nothing|never changed)\b",
                  r"\bnothing (?:has|had) changed\b",
                  r"\btrust is for fools\b"]},
]

_FOREIGN_NAME_RULES = {
    # 外国人名ルール(項目4): 本文では First/Last の一方だけを使う。フルネームを含む場合はFAIL。
    # Melosの物語ではMelos(単名)のみで、フルネーム表記の対象人物は無い。他storyでは
    # full_nameをここへ追加する(例: {"full_name": "Eugene Aram", "short_forms": ["Aram"]})。
    "full_names": [],
    "rule_ref": "CURRENT_SPEC.md Family Z 項目4(Fiction共通の外国人名ルール)",
}


def build_validator_anchors(seed_dir: str = SEED_DIR) -> dict:
    """原作・Seedのみからanchorsを組み立てる(候補稿は引数に取らない=構造的に新稿を見られない)。"""
    seed_sha = sha256_file(os.path.join(seed_dir, "seed.json"))
    primary_sha = sha256_file(os.path.join(seed_dir, "primary_text_excerpt.md"))
    doc = {
        "schema_version": "er061_validator_anchors_v1",
        "story_key": "melos",
        "seed_sha256": seed_sha,
        "primary_text_excerpt_sha256": primary_sha,
        "anchors": [dict(a) for a in _ANCHOR_SPEC],
        "forbidden_endings": json.loads(json.dumps(_FORBIDDEN_ENDINGS, ensure_ascii=False)),
        "ending_scan_paragraphs": ENDING_SCAN_PARAGRAPHS,
        "foreign_name_rules": json.loads(json.dumps(_FOREIGN_NAME_RULES, ensure_ascii=False)),
        "name_policy": "固有名詞(Melos以外)の登場は必須としない。名前の有無だけでPASS/FAILしない。",
        "created_before_candidate": True,
    }
    doc["sha256_self"] = sha256_text(_canonical_json(doc))
    return doc


def _verify_self_sha(doc: dict) -> bool:
    body = {k: v for k, v in doc.items() if k != "sha256_self"}
    return sha256_text(_canonical_json(body)) == doc.get("sha256_self")


def freeze_anchors(path: str = ANCHORS_PATH, seed_dir: str = SEED_DIR) -> dict:
    """anchors.jsonを凍結作成。既存ファイルがあれば上書きせず、内容shaが一致することだけ検証する。"""
    built = build_validator_anchors(seed_dir)
    if os.path.exists(path):
        existing = load_anchors(path, seed_dir)
        if existing["sha256_self"] != built["sha256_self"]:
            raise AnchorsIntegrityError(
                "凍結済みanchorsと再構築結果のshaが不一致(凍結済みを上書きしない)。")
        return existing
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(built, f, ensure_ascii=False, indent=2)
    return built


def load_anchors(path: str = ANCHORS_PATH, seed_dir: str = SEED_DIR) -> dict:
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    if not _verify_self_sha(doc):
        raise AnchorsIntegrityError("anchors.json の sha256_self が不一致(改ざん/編集の疑い)。")
    if doc.get("seed_sha256") != sha256_file(os.path.join(seed_dir, "seed.json")):
        raise AnchorsIntegrityError("anchorsのseed_sha256が現行seed.jsonと不一致。")
    if doc.get("created_before_candidate") is not True:
        raise AnchorsIntegrityError("created_before_candidate が True でない。")
    return doc


# ============================================================
# 第1層(決定論)
# ============================================================
def _kw_hit(keyword: str, text_lc: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(keyword.lower()), text_lc) is not None


def layer1_check(text: str, anchors: dict) -> dict:
    """決定論検査。hard FAILは高精度項目(禁止結末/外国人名/主要アンカー全欠落)のみ。順序は判定しない。"""
    paras = split_paragraphs(text)
    text_lc = _norm_quote_text(text)
    hard, warns = [], []
    anchor_hits = {}
    checkable = [a for a in anchors["anchors"] if a.get("concept_family")]
    for a in checkable:
        anchor_hits[a["id"]] = [k for k in a["concept_family"] if _kw_hit(k, text_lc)]
    required = [a for a in checkable if a.get("required")]
    missing_required = [a["id"] for a in required if not anchor_hits[a["id"]]]
    if required and len(missing_required) == len(required):
        hard.append({"id": "ALL_REQUIRED_ANCHORS_MISSING", "detail": missing_required})
    else:
        for aid in missing_required:
            warns.append({"id": "ANCHOR_KEYWORDS_MISSING", "detail": aid})
    # 禁止結末family(末尾N段落のみ走査)
    n_scan = anchors.get("ending_scan_paragraphs", ENDING_SCAN_PARAGRAPHS)
    tail_lc = _norm_quote_text(" ".join(paras[-n_scan:]))
    for fe in anchors.get("forbidden_endings", []):
        for pat in fe["patterns"]:
            m = re.search(pat, tail_lc)
            if m:
                hard.append({"id": f"FORBIDDEN_ENDING:{fe['id']}", "detail": m.group(0)})
                break
    # 外国人名ルール(フルネーム使用はFAIL)
    for rule in anchors.get("foreign_name_rules", {}).get("full_names", []):
        if re.search(r"(?<![a-z])" + re.escape(rule["full_name"].lower()) + r"(?![a-z])", text_lc):
            hard.append({"id": "FOREIGN_NAME_RULE_VIOLATION", "detail": rule["full_name"]})
    if not _kw_hit("melos", text_lc):
        warns.append({"id": "PROTAGONIST_NAME_ABSENT", "detail": "Melos"})
    verdict = "FAIL" if hard else ("WARN" if warns else "PASS")
    return {"verdict": verdict, "hard_fails": hard, "warns": warns, "anchor_hits": anchor_hits,
            "paragraph_count": len(paras)}


# ============================================================
# Std追加チェック
# ============================================================
def _avg_sentence_len(sents: list) -> float:
    return (sum(len(s.split()) for s in sents) / len(sents)) if sents else 0.0


def _anchor_first_paragraph(text: str, anchors: dict) -> dict:
    paras = [_norm_quote_text(p) for p in split_paragraphs(text)]
    out = {}
    for a in anchors["anchors"]:
        if not a.get("concept_family"):
            continue
        for i, p in enumerate(paras):
            if any(_kw_hit(k, p) for k in a["concept_family"]):
                out[a["id"]] = i
                break
    return out


def std_vs_adv_checks(adv_text: str, std_text: str, anchors: dict | None = None) -> dict:
    """Standard用追加検査。Advと同一本文判定(FAIL)、平均文長soft gate(WARN)、段落数・順序一致。"""
    adv_s, std_s = split_sentences(adv_text), split_sentences(std_text)
    adv_set = {_norm_sentence(s) for s in adv_s}
    same = sum(1 for s in std_s if _norm_sentence(s) in adv_set)
    ratio = (same / len(std_s)) if std_s else 0.0
    adv_len, std_len = _avg_sentence_len(adv_s), _avg_sentence_len(std_s)
    adv_pc, std_pc = len(split_paragraphs(adv_text)), len(split_paragraphs(std_text))
    fails, warns = [], []
    if ratio >= STD_IDENTICAL_FAIL_RATIO:
        fails.append({"id": "STD_IDENTICAL_TO_ADV", "detail": f"identical_sentence_ratio={ratio:.3f}"})
    if adv_len and std_len > adv_len * STD_AVG_SENTENCE_LEN_MAX_RATIO:
        warns.append({"id": "STD_AVG_SENTENCE_LEN_NOT_SHORTER",
                      "detail": f"std={std_len:.2f} adv={adv_len:.2f} limit={adv_len * STD_AVG_SENTENCE_LEN_MAX_RATIO:.2f}"})
    if adv_pc != std_pc:
        fails.append({"id": "STD_PARAGRAPH_COUNT_MISMATCH", "detail": f"adv={adv_pc} std={std_pc}"})
    inversions = None
    if anchors is not None:
        a_pos, s_pos = _anchor_first_paragraph(adv_text, anchors), _anchor_first_paragraph(std_text, anchors)
        common = [k for k in a_pos if k in s_pos]
        inv = 0
        for i in range(len(common)):
            for j in range(i + 1, len(common)):
                da, ds = a_pos[common[i]] - a_pos[common[j]], s_pos[common[i]] - s_pos[common[j]]
                if da * ds < 0:
                    inv += 1
        inversions = inv
        if inv:
            warns.append({"id": "STD_ANCHOR_ORDER_DIFFERS_FROM_ADV", "detail": f"inversions={inv}"})
    verdict = "FAIL" if fails else ("WARN" if warns else "PASS")
    return {"verdict": verdict, "fails": fails, "warns": warns,
            "identical_sentence_ratio": round(ratio, 4), "std_sentence_count": len(std_s),
            "avg_sentence_len_adv": round(adv_len, 3), "avg_sentence_len_std": round(std_len, 3),
            "paragraph_count_adv": adv_pc, "paragraph_count_std": std_pc,
            "paragraph_count_match": adv_pc == std_pc, "anchor_order_inversions": inversions}


# ============================================================
# 第2層(LLM judge)
# ============================================================
JUDGE_SCHEMA = {
    "name": "family_z_semantic_judge",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "anchor_id": {"type": "string"},
                        "category": {"type": "string", "enum": list(CATEGORIES)},
                        "status": {"type": "string", "enum": list(STATUSES)},
                        "severity": {"type": "string", "enum": list(SEVERITIES)},
                        "evidence_quote": {"type": "string"},
                        "note": {"type": "string"},
                    },
                    "required": ["anchor_id", "category", "status", "severity", "evidence_quote", "note"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}

JUDGE_DEVELOPER_MESSAGE = """You are a strict but fair literary-adaptation fidelity judge for an English-learner audio story program.
You compare a CANDIDATE English adaptation against the ORIGINAL work (Japanese key passages + a structured seed summary).
Judge ONLY whether the candidate preserves the story's meaning: character roles and relationships, key events, cause-and-effect, order of events, the ending, and the original's charm.

Rules:
- Personal names are NOT required. Using role words ("the ruler", "his friend") instead of names is fine and must NOT be penalised. Simplified language, shortening, re-wording and omission of minor details are fine.
- Return EXACTLY ONE item per anchor, using the given anchor_id and its category (copy both exactly).
- status: "preserved" (meaning kept), "altered" (present but meaning changed/reversed/contradicted), "missing" (absent).
- severity: "none" if preserved; "minor" for small drift that does not change the story's point; "major" only when the central meaning is changed, reversed, or lost (e.g., the friend relationship disappears, the ending changes, a key event is absent, cause and effect are reversed, major invented facts alter the story).
- evidence_quote: copy a short span (3-25 words) EXACTLY, character for character, from the CANDIDATE text that supports your judgement (for "preserved" the passage that preserves it; for "altered" the passage that changes it). For "missing" use the nearest relevant passage if one exists, otherwise an empty string. Never invent or paraphrase a quote.
- For the added_fact anchor (X1): "preserved" means NO major new facts were invented; "altered" means major new facts/events/characters were added (quote one).
- note: one short sentence (Japanese or English) explaining the judgement.
"""


def build_judge_user_message(anchors: dict, source_info: dict, candidate_text: str) -> str:
    anchor_lines = [f'- anchor_id={a["id"]} category={a["category"]}: {a["description_en"]}'
                    for a in anchors["anchors"]]
    return (
        "[ORIGINAL: structured seed summary]\n"
        f'{source_info["original_summary"]}\n\n'
        "[ORIGINAL: seed elements]\n"
        + "\n".join(f"{i + 1}. {e}" for i, e in enumerate(source_info["seed_elements"])) + "\n\n"
        "[ORIGINAL: Japanese key passages (verbatim from the source work)]\n"
        f'{source_info["primary_text"]}\n\n'
        "[ANCHORS TO JUDGE (one item each)]\n" + "\n".join(anchor_lines) + "\n\n"
        "[CANDIDATE ENGLISH TEXT]\n"
        f"{candidate_text}\n"
    )


def load_source_info(seed_dir: str = SEED_DIR) -> dict:
    with open(os.path.join(seed_dir, "seed.json"), encoding="utf-8") as f:
        seed = json.load(f)
    with open(os.path.join(seed_dir, "primary_text_excerpt.md"), encoding="utf-8") as f:
        primary = f.read()
    return {"original_summary": seed["original_summary"], "seed_elements": seed["seed_elements"],
            "primary_text": primary}


def _load_pricing(model: str) -> dict:
    with open(PRICING_SNAPSHOT_PATH, encoding="utf-8") as f:
        snap = json.load(f)
    pr = {}
    for e in snap["prices"]:
        if e.get("provider") == "openai" and e.get("model") == model and e.get("tier", "Standard") == "Standard":
            pr[e["meter"]] = e["price"]
    for m in ("input_tokens", "cached_input_tokens", "output_tokens"):
        if m not in pr:
            raise routing.PricingNotFoundError(f"[STOP] 単価未登録model: openai/{model} meter={m}")
    return pr


class CostTracker:
    """第2層のAPI費用を実測(response.usage x pricing_snapshot)し、上限超過見込みでSTOPする。"""

    def __init__(self, cap_jpy: float = CALIBRATION_CAP_JPY, est_per_call_jpy: float = 0.6):
        self.cap_jpy, self.est_per_call_jpy = cap_jpy, est_per_call_jpy
        self.total_jpy = 0.0
        self.input_tokens = self.cached_tokens = self.output_tokens = 0
        self.calls = 0

    def check_before(self, label: str = "") -> None:
        if self.total_jpy + self.est_per_call_jpy > self.cap_jpy:
            raise JudgeBudgetExceeded(
                f"FAMILY_Z_VALIDATOR_BUDGET_STOP: label={label!r} total={self.total_jpy:.4f} "
                f"est={self.est_per_call_jpy} cap={self.cap_jpy}")

    def add(self, model: str, usage) -> float:
        pr = _load_pricing(model)
        inp = getattr(usage, "input_tokens", 0) or 0
        out = getattr(usage, "output_tokens", 0) or 0
        det = getattr(usage, "input_tokens_details", None)
        cached = (getattr(det, "cached_tokens", 0) or 0) if det is not None else 0
        usd = (max(inp - cached, 0) / 1e6) * pr["input_tokens"] + (cached / 1e6) * pr["cached_input_tokens"] \
            + (out / 1e6) * pr["output_tokens"]
        jpy = usd * USD_JPY
        self.total_jpy += jpy
        self.input_tokens += inp
        self.cached_tokens += cached
        self.output_tokens += out
        self.calls += 1
        return jpy

    def as_dict(self) -> dict:
        return {"total_jpy": round(self.total_jpy, 4), "calls": self.calls, "cap_jpy": self.cap_jpy,
                "input_tokens": self.input_tokens, "cached_input_tokens": self.cached_tokens,
                "output_tokens": self.output_tokens}


def get_openai_client():
    from dotenv import load_dotenv
    load_dotenv()
    from openai import OpenAI
    return OpenAI()


def _call_judge(client, anchors: dict, source_info: dict, candidate_text: str, tracker: CostTracker) -> dict:
    model = routing.PROCESS_MODEL_MAP[JUDGE_ROUTING_KEY]
    routing.require_model(JUDGE_ROUTING_KEY, model)
    tracker.check_before("semantic_judge")
    response = client.responses.create(
        model=model, reasoning={"effort": "medium"},
        input=[{"role": "developer", "content": JUDGE_DEVELOPER_MESSAGE},
               {"role": "user", "content": build_judge_user_message(anchors, source_info, candidate_text)}],
        text={"format": {"type": "json_schema", **JUDGE_SCHEMA}},
    )
    actual = getattr(response, "model", None) or model
    if not (actual == model or str(actual).startswith(model + "-")):
        raise JudgeModelMismatch(f"actual model {actual!r} != requested {model!r}")
    cost = tracker.add(model, response.usage)
    return {"requested_model": model, "actual_model_id": actual, "response_id": getattr(response, "id", None),
            "output_text": response.output_text, "cost_jpy": round(cost, 5),
            "usage": {"input_tokens": getattr(response.usage, "input_tokens", 0),
                      "output_tokens": getattr(response.usage, "output_tokens", 0)}}


def evaluate_judgement(parsed, anchors: dict, candidate_text: str) -> dict:
    """judge応答の妥当性(coverage/enum/引用の逐語性)を決定論検証し、項目別に分類する。
    捏造引用(候補本文に逐語存在しない)・coverage欠落は valid=False(=NEEDS_REVIEW側)。"""
    items = parsed.get("items") if isinstance(parsed, dict) else None
    if not isinstance(items, list):
        return {"valid": False, "invalid_reasons": ["items_not_list"], "items": [], "verdict": None,
                "fail_items": [], "warn_items": []}
    invalid = []
    by_id = {a["id"]: a for a in anchors["anchors"]}
    seen = set()
    norm_items = []
    for it in items:
        aid = it.get("anchor_id")
        if aid not in by_id:
            invalid.append(f"unknown_anchor_id:{aid}")
            continue
        if aid in seen:
            invalid.append(f"duplicate_anchor_id:{aid}")
            continue
        seen.add(aid)
        if it.get("category") != by_id[aid]["category"]:
            invalid.append(f"category_mismatch:{aid}")
        if it.get("status") not in STATUSES or it.get("severity") not in SEVERITIES:
            invalid.append(f"bad_enum:{aid}")
            continue
        quote = it.get("evidence_quote") or ""
        verified = quote_is_verbatim(quote, candidate_text)
        # preserved/altered は逐語引用が必須。missing は「無いこと」を引用できないため空文字を許容
        # (引用がある場合は検証し、捏造なら無効)。
        if it["status"] in ("preserved", "altered") and not verified:
            invalid.append(f"evidence_quote_not_verbatim:{aid}")
        if it["status"] == "missing" and quote.strip() and not verified:
            invalid.append(f"evidence_quote_not_verbatim:{aid}")
        if it["status"] == "preserved" and it["severity"] != "none":
            invalid.append(f"preserved_with_severity:{aid}")
        norm_items.append({**it, "quote_verified": verified})
    for aid in by_id:
        if aid not in seen:
            invalid.append(f"coverage_missing:{aid}")
    if invalid:
        return {"valid": False, "invalid_reasons": invalid, "items": norm_items, "verdict": None,
                "fail_items": [], "warn_items": []}
    fail_items = [i for i in norm_items if i["status"] != "preserved" and i["severity"] == "major"]
    warn_items = [i for i in norm_items if i["status"] != "preserved" and i["severity"] != "major"]
    verdict = "FAIL" if fail_items else ("WARN" if warn_items else "PASS")
    return {"valid": True, "invalid_reasons": [], "items": norm_items, "verdict": verdict,
            "fail_items": fail_items, "warn_items": warn_items}


def _valid_judgement(client, anchors, source_info, candidate_text, tracker, max_invalid_retries=1):
    records = []
    for attempt in range(1 + max_invalid_retries):
        raw = _call_judge(client, anchors, source_info, candidate_text, tracker)
        try:
            parsed = json.loads(raw["output_text"])
        except (TypeError, ValueError):
            parsed = None
        if parsed is None:
            ev = {"valid": False, "invalid_reasons": ["json_parse_error"], "items": [], "verdict": None,
                  "fail_items": [], "warn_items": []}
        else:
            ev = evaluate_judgement(parsed, anchors, candidate_text)
        rec = {"attempt": attempt + 1,
               **{k: raw[k] for k in ("requested_model", "actual_model_id", "response_id", "cost_jpy", "usage")},
               **ev}
        records.append(rec)
        if ev["valid"]:
            return rec, records
    return None, records


def layer2_check(client, anchors: dict, source_info: dict, candidate_text: str, tracker: CostTracker,
                 max_invalid_retries: int = 1) -> dict:
    """第2層。FAIL時は再判定1回、2回一致(カテゴリ重複あり)でFAIL、不一致はNEEDS_REVIEW。"""
    j1, recs = _valid_judgement(client, anchors, source_info, candidate_text, tracker, max_invalid_retries)
    out = {"judgements": recs, "confirmed": None, "fail_items": [], "warn_items": [], "reasons": []}
    if j1 is None:
        out.update(verdict="NEEDS_REVIEW", reasons=["judge応答が無効(引用不一致/coverage欠落等)が上限回数続いた"])
        return out
    if j1["verdict"] in ("PASS", "WARN"):
        out.update(verdict=j1["verdict"], warn_items=j1["warn_items"])
        return out
    j2, recs2 = _valid_judgement(client, anchors, source_info, candidate_text, tracker, max_invalid_retries)
    out["judgements"] = recs + recs2
    if j2 is None:
        out.update(verdict="NEEDS_REVIEW", confirmed=False, fail_items=j1["fail_items"],
                   reasons=["再判定の応答が無効"])
        return out
    cats1 = {i["category"] for i in j1["fail_items"]}
    cats2 = {i["category"] for i in j2["fail_items"]}
    if j2["verdict"] == "FAIL" and (cats1 & cats2):
        out.update(verdict="FAIL", confirmed=True, fail_items=j1["fail_items"],
                   warn_items=j1["warn_items"], confirmed_categories=sorted(cats1 & cats2))
    else:
        out.update(verdict="NEEDS_REVIEW", confirmed=False, fail_items=j1["fail_items"],
                   reasons=[f"再判定が不一致: 1回目FAIL{sorted(cats1)} / 2回目{j2['verdict']}{sorted(cats2)}"])
    return out


# ============================================================
# 統合
# ============================================================
def combine_verdicts(l1: dict, l2: dict | None, std: dict | None) -> tuple:
    reasons = []
    std_fail = std is not None and std["verdict"] == "FAIL"
    if std_fail:
        reasons += [f"std:{f['id']}" for f in std["fails"]]
    if l2 is None:  # 第2層未実施(第1層のみ)
        verdict = "FAIL" if std_fail else l1["verdict"]
        if l1["verdict"] == "FAIL":
            reasons += [f"layer1:{h['id']}" for h in l1["hard_fails"]]
        return verdict, reasons
    v1, v2 = l1["verdict"], l2["verdict"]
    if v2 == "NEEDS_REVIEW":
        verdict = "NEEDS_REVIEW"
        reasons += l2.get("reasons", [])
    elif v1 == "FAIL" and v2 != "FAIL":
        verdict = "NEEDS_REVIEW"
        reasons.append(f"第1層FAILと第2層{v2}が食い違い(自動では通さない)")
        reasons += [f"layer1:{h['id']}" for h in l1["hard_fails"]]
    elif v1 == "FAIL" or v2 == "FAIL":
        verdict = "FAIL"
        if v1 == "FAIL":
            reasons += [f"layer1:{h['id']}" for h in l1["hard_fails"]]
        if v2 == "FAIL":
            reasons += [f"layer2:{i['category']}:{i['anchor_id']}" for i in l2["fail_items"]]
    elif v1 == "WARN" or v2 == "WARN":
        verdict = "WARN"
    else:
        verdict = "PASS"
    if std_fail and verdict in ("PASS", "WARN"):
        verdict = "FAIL"
    elif std is not None and std["verdict"] == "WARN" and verdict == "PASS":
        verdict = "WARN"
    return verdict, reasons


def validate_semantic_preservation(candidate_text: str, level: str, *, client=None, anchors: dict | None = None,
                                   adv_text: str | None = None, tracker: CostTracker | None = None,
                                   source_info: dict | None = None, out_dir: str | None = None) -> dict:
    """04B/統合向け公開API。level: 'b1b'(Advanced)/'a2'(Standard)。
    adv_textを渡し level=='a2' のときStd追加検査も行う。client=Noneなら第1層のみ(layer2はNone)。
    戻り値のverdictがFAIL/NEEDS_REVIEWの場合 stop_required=True(自動では通さない)。"""
    if level not in ("a2", "b1b"):
        raise ValueError("level must be 'a2' or 'b1b'")
    anchors = anchors or load_anchors()
    l1 = layer1_check(candidate_text, anchors)
    std = std_vs_adv_checks(adv_text, candidate_text, anchors) if (level == "a2" and adv_text is not None) else None
    l2 = None
    tracker = tracker or CostTracker()
    start = (tracker.total_jpy, tracker.input_tokens, tracker.cached_tokens, tracker.output_tokens)  # 共有trackerでも本検証分だけ報告
    if client is not None:
        l2 = layer2_check(client, anchors, source_info or load_source_info(), candidate_text, tracker)
    verdict, reasons = combine_verdicts(l1, l2, std)
    actual_ids = sorted({j["actual_model_id"] for j in (l2 or {}).get("judgements", [])})
    result = {
        "schema_version": SCHEMA_VERSION, "story_key": anchors.get("story_key"), "level": level,
        "candidate_sha256": sha256_text(candidate_text), "anchors_sha256": anchors["sha256_self"],
        "layer1": l1, "layer2": l2, "std_checks": std,
        "verdict": verdict, "stop_required": verdict in ("FAIL", "NEEDS_REVIEW"), "reasons": reasons,
        "model": {"routing_key": JUDGE_ROUTING_KEY, "requested": routing.PROCESS_MODEL_MAP[JUDGE_ROUTING_KEY],
                  "actual_model_ids": actual_ids},
        "usage_total": {"input_tokens": tracker.input_tokens - start[1],
                        "cached_input_tokens": tracker.cached_tokens - start[2],
                        "output_tokens": tracker.output_tokens - start[3]},
        "cost_jpy": round(tracker.total_jpy - start[0], 4),
    }
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "validator_result.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        with open(os.path.join(out_dir, "validator_summary.md"), "w", encoding="utf-8") as f:
            f.write(render_summary(result))
    return result


def render_summary(result: dict) -> str:
    lines = [f"# Validator結果 ({result['story_key']} / level={result['level']})", "",
             f"- 最終verdict: **{result['verdict']}** (stop_required={result['stop_required']})",
             f"- candidate_sha256: {result['candidate_sha256'][:16]}... / anchors_sha256: {result['anchors_sha256'][:16]}...",
             f"- 第1層: {result['layer1']['verdict']} hard_fails={[h['id'] for h in result['layer1']['hard_fails']]} "
             f"warns={[w['id'] for w in result['layer1']['warns']]}"]
    l2 = result.get("layer2")
    if l2:
        lines.append(f"- 第2層: {l2['verdict']} (confirmed={l2['confirmed']}, judge呼出={len(l2['judgements'])}回)")
        for it in l2.get("fail_items", []):
            lines.append(f"  - FAIL {it['category']}/{it['anchor_id']}: {it['status']} 「{it['evidence_quote']}」 {it['note']}")
        for it in l2.get("warn_items", []):
            lines.append(f"  - WARN {it['category']}/{it['anchor_id']}: {it['status']} {it['note']}")
        for r in l2.get("reasons", []):
            lines.append(f"  - 理由: {r}")
    else:
        lines.append("- 第2層: 未実施")
    if result.get("std_checks"):
        s = result["std_checks"]
        lines.append(f"- Std検査: {s['verdict']} 同一文率={s['identical_sentence_ratio']} 段落数 adv={s['paragraph_count_adv']}/std={s['paragraph_count_std']} "
                     f"平均文長 adv={s['avg_sentence_len_adv']}/std={s['avg_sentence_len_std']}")
    lines.append(f"- model: requested={result['model']['requested']} actual={result['model']['actual_model_ids']}")
    lines.append(f"- 費用: ¥{result['cost_jpy']} / usage={result['usage_total']}")
    if result["reasons"]:
        lines.append(f"- 理由: {result['reasons']}")
    return "\n".join(lines) + "\n"


# ============================================================
# Local Rewrite後の再検証
# ============================================================
def revalidate_after_local_rewrite(text_before: str, text_after: str, anchors: dict | None = None) -> dict:
    """Local Rewrite採択後の再検証(M6)。書換後全文で第1層を再実行し、差分を記録する。
    第1層FAIL -> verdict=FAIL(呼出側はSTOP)。第2層は実施しない(必要なら全文再検証を別途実行)。"""
    anchors = anchors or load_anchors()
    l1_before, l1_after = layer1_check(text_before, anchors), layer1_check(text_after, anchors)
    sb, sa = split_sentences(text_before), split_sentences(text_after)
    sm = difflib.SequenceMatcher(a=sb, b=sa, autojunk=False)
    removed, added = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op in ("replace", "delete"):
            removed += sb[i1:i2]
        if op in ("replace", "insert"):
            added += sa[j1:j2]
    verdict = l1_after["verdict"]
    regressed = l1_before["verdict"] != "FAIL" and l1_after["verdict"] == "FAIL"
    return {"verdict": verdict, "stop_required": verdict == "FAIL",
            "regressed_to_fail": regressed, "layer1_before": l1_before, "layer1_after": l1_after,
            "diff": {"removed_sentences": removed, "added_sentences": added,
                     "identical": text_before == text_after,
                     "before_sha256": sha256_text(text_before), "after_sha256": sha256_text(text_after)},
            "layer2_performed": False}


# ============================================================
# 旧名前検査の互換ラッパ(superseded)
# ============================================================
# SUPERSEDED: er026_family_z_fiction_production_runner_01.check_character_name_rule /
# restore_character_names は「Melos以外の人物名の登場を必須」とする旧仕様(項目2の名前検査部分)で、
# DECISION_LOG 2026-10-12により superseded。er026本体は(統合時に)本モジュールへ置換する。
# 旧関数は削除せず残置する。下記ラッパはer026側の差し替え前に呼ばれた場合の安全網。
def check_character_name_rule(body_text: str, anchors: dict | None = None) -> tuple:
    """[DEPRECATED/superseded] 旧(ok, missing_names)形を維持した互換ラッパ。
    名前の有無では判定せず、第1層のhard FAIL項目で判定する(missing=hard_fail id一覧)。"""
    warnings.warn(
        "check_character_name_rule is superseded by er061 validate_semantic_preservation "
        "(layer1_check); names are no longer required.", DeprecationWarning, stacklevel=2)
    l1 = layer1_check(body_text, anchors or load_anchors())
    ids = [h["id"] for h in l1["hard_fails"]]
    return (len(ids) == 0), ids


def restore_character_names(body_text: str) -> str:
    """[DEPRECATED/superseded] 名前の機械的復元は不採用(DECISION_LOG 2026-10-12)。
    警告を出した上で本文を一切変更せずに返す(旧挙動のRuntimeError経路も無効)。"""
    warnings.warn(
        "restore_character_names is superseded: mechanical name restoration is no longer adopted.",
        DeprecationWarning, stacklevel=2)
    return body_text


# ============================================================
# Calibration(実呼出)
# ============================================================
FIXTURE_DIR = "er061_fixtures"
FIXTURE_MANIFEST = f"{FIXTURE_DIR}/fixtures_manifest.json"
CALIBRATION_OUT_DIR = "er060_output/melos_production_e2e_01/validator_calibration_01"


def run_calibration(cap_jpy: float = CALIBRATION_CAP_JPY, client=None, fixture_ids=None) -> dict:
    client = client or get_openai_client()
    anchors = load_anchors()
    source_info = load_source_info()
    with open(FIXTURE_MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    tracker = CostTracker(cap_jpy=cap_jpy)
    rows, stopped = [], None
    os.makedirs(CALIBRATION_OUT_DIR, exist_ok=True)
    for fx in manifest["fixtures"]:
        if fixture_ids and fx["id"] not in fixture_ids:
            continue
        with open(os.path.join(FIXTURE_DIR, fx["file"]), encoding="utf-8") as f:
            text = f.read()
        before = tracker.total_jpy
        try:
            res = validate_semantic_preservation(
                text, "b1b", client=client, anchors=anchors, tracker=tracker, source_info=source_info,
                out_dir=os.path.join(CALIBRATION_OUT_DIR, fx["id"]))
        except JudgeBudgetExceeded as e:
            stopped = str(e)
            break
        l2 = res["layer2"]
        judgements = [{"attempt": j["attempt"], "valid": j["valid"], "verdict": j["verdict"],
                       "fail_categories": sorted({i["category"] for i in j["fail_items"]}),
                       "invalid_reasons": j["invalid_reasons"], "actual_model_id": j["actual_model_id"],
                       "cost_jpy": j["cost_jpy"]} for j in l2["judgements"]]
        fail_cats = sorted({i["category"] for i in l2["fail_items"]})
        if fx["expected_verdict"] == "PASS":
            ok = res["verdict"] in ("PASS", "WARN") and res["layer1"]["verdict"] != "FAIL" \
                and l2["verdict"] in ("PASS", "WARN")
        else:
            valid_js = [j for j in l2["judgements"] if j["valid"]]
            exp = set(fx["expected_categories"])
            ok = (res["verdict"] == "FAIL" and l2["verdict"] == "FAIL" and l2.get("confirmed") is True
                  and len(valid_js) >= 2
                  and all(j["verdict"] == "FAIL" and exp & {i["category"] for i in j["fail_items"]}
                          for j in valid_js[:2]))
        rows.append({"fixture": fx["id"], "description": fx["description"], "expected_verdict": fx["expected_verdict"],
                     "expected_categories_any_of": fx.get("expected_categories", []),
                     "final_verdict": res["verdict"], "layer1_verdict": res["layer1"]["verdict"],
                     "layer1_hard_fails": [h["id"] for h in res["layer1"]["hard_fails"]],
                     "layer2_verdict": l2["verdict"], "layer2_confirmed": l2.get("confirmed"),
                     "layer2_fail_categories": fail_cats, "judgements": judgements,
                     "cost_jpy": round(tracker.total_jpy - before, 4), "calibration_ok": bool(ok)})
    out = {"schema_version": "er061_calibration_v1", "date": "2026-10-12",
           "routing_key": JUDGE_ROUTING_KEY, "requested_model": routing.PROCESS_MODEL_MAP[JUDGE_ROUTING_KEY],
           "actual_model_ids": sorted({j["actual_model_id"] for r in rows for j in r["judgements"]}),
           "anchors_sha256": anchors["sha256_self"], "rows": rows, "stopped": stopped,
           "all_ok": (stopped is None and bool(rows) and all(r["calibration_ok"] for r in rows)),
           "cost": tracker.as_dict()}
    os.makedirs(os.path.dirname(CALIBRATION_PATH), exist_ok=True)
    with open(CALIBRATION_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze-anchors", action="store_true")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--cap-jpy", type=float, default=CALIBRATION_CAP_JPY)
    ap.add_argument("--fixtures", nargs="*")
    args = ap.parse_args()
    if args.freeze_anchors:
        a = freeze_anchors()
        print("anchors frozen:", ANCHORS_PATH, a["sha256_self"])
    if args.calibrate:
        out = run_calibration(args.cap_jpy, fixture_ids=args.fixtures)
        print(json.dumps({"all_ok": out["all_ok"], "cost": out["cost"], "stopped": out["stopped"],
                          "rows": [(r["fixture"], r["final_verdict"], r["layer2_fail_categories"], r["calibration_ok"])
                                   for r in out["rows"]]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
