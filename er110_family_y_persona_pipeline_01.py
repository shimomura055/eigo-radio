# -*- coding: utf-8 -*-
"""er110_family_y_persona_pipeline_01.py
FAMILY-Y-VOICES-DESIGN-01 委任_14 Phase B: Family Y「Persona選定〜Voice R0」6段階パイプライン(DEV/Trial専用module)。

設計: docs/research/FAMILY-Y-VOICES-DESIGN-01/REDESIGN_02/DESIGN_PROPOSAL_06.md(DESIGN_PROPOSAL_05 + OPUS_REVIEW_03 OF-Y5-01〜12反映)。
  S1 世界設定 -> S2 当事者の洗い出し -> S3 立場x主張の探索 -> S4 3 Voiceの組合せ選定 -> (決定論スロット割当)
  -> S5 Persona構築(+別callの自然さ検証、差戻し<=2) -> S6 Voice R0(Prompt複製・規則改訂) -> 構造タグ監視(1回だけ是正) -> 旧B Leakage Gate

位置づけ(重要):
  - **未配線のDEV/Trial module**。どのProduction runner・既存er110 moduleからもimportされない(testでGrep固定)。
    import時にAPI呼出0・ファイル副作用0。環境変数・flag・CLI引数でProduction挙動が変わる経路はない。
  - 既存 er110_family_y_text_trial_01.py / er110_family_y_persona_text_trial_01.py は**無変更**。本fileは
    API入口(y0.chat)・Leakage判定器(p.run_leak、13項目の定義は不変)・記号QA・局所書換の決定論検査(p.apply_rewrites)・
    英訳契約検査を呼出で再利用するのみ。Acceptance Gate(判定最大3回)は同じ構造で複製(rewrite promptだけ題材非依存化)。
  - 新しい合格基準・Validatorは作らない。決定論部分は『入力の整合確認』と『監視の記録』のみ。
"""
from __future__ import annotations

import difflib
import itertools
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor

import er003_audio_tts_asr_safety as safety
import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_text_trial_01 as y0
import er110_family_y_persona_text_trial_01 as p      # 既存DEV module(無変更)。Leakage判定器等を呼出で再利用

MANAGEMENT_ID = "FAMILY-Y-VOICES-DESIGN-01"
THEME_TAG = "FAMILY_Y_PERSONA_PIPELINE_01"
y0.THEME_TAG = THEME_TAG       # cost loggerのstageタグ(y0.chatがmodule変数を参照するため、本process内のみ差替え。pのimport後に設定)
MODEL_TOP = y0.MODEL_TOP        # gpt-6.1-sol(25節: 最新世代最上位系)
MODEL_CHEAP = y0.MODEL_CHEAP    # gpt-6-luna(Leakage判定器[M7校正済]・自然さ検証・構造タグ・網羅判定・E1)

SLOTS = ("voice_1", "voice_2", "voice_3")
SLOT_GENDER = {"voice_1": "男性", "voice_2": "女性", "voice_3": "男性"}       # 固定TTS Voice(er110_family_y_text_trial_01.py:39)。変更はユーザー判断
TTS_VOICE = {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"}
REWORK_LIMIT = 2


class PipelineStop(RuntimeError):
    def __init__(self, code: str, message: str, payload=None):
        super().__init__(f"[STOP] {code}: {message}")
        self.code, self.payload = code, payload


# ============================================================
# 小道具: strict JSON schema
# ============================================================
def _obj(**props) -> dict:
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


_STR = {"type": "string"}
_BOOL = {"type": "boolean"}
_INT = {"type": "integer"}


def _arr(item) -> dict:
    return {"type": "array", "items": item}


def _enum(*vals) -> dict:
    return {"type": "string", "enum": list(vals)}


def _schema(name: str, **props) -> dict:
    return {"name": name, "strict": True, "schema": _obj(**props)}


KIND_VALUES = ("要求", "拒否", "不安", "怒り", "願望", "あきらめ", "思い込み", "自己都合", "矛盾した本音", "その他")
SELFISH_KINDS = ("自己都合", "怒り", "矛盾した本音")        # 『立場ごとに1件以上は自己都合・感情的反発・矛盾のいずれか』
RATIONALITY_VALUES = ("筋が通る", "本人なりの理屈", "感情先行", "思い込みを含む")
GENDER_INTRINSIC = ("男性", "女性", "不問")

# 構造タグのラベル集合(OF-Y5-06: 事前固定。『自嘲・告白で締める』を含む)
OPENING_TYPES = ("自分の状況・立場の描写から", "出来事・場面の描写から", "感情・本音の吐露から", "主張・意見の表明から", "問いかけから", "言い訳・弁明から", "その他")
DEVELOPMENT_TYPES = ("主張から具体例へ", "具体例から感情を経て主張へ", "感情から具体例へ", "経験の時系列", "問いを重ねて考える",
                     "自分への突っ込みと本音を行き来する", "その他")
CLOSING_TYPES = ("自嘲・告白で締める", "問いを残して締める", "約束・要求で締める", "主張を言い切って締める", "場面・情景で締める", "迷いを残して締める", "その他")

SCHEMA_S1 = _schema(
    "yp_world_frame",
    question_ja=_STR, title_ja=_STR,
    setting=_obj(country=_STR, institution_type=_STR, population=_STR, era=_STR),
    status_quo=_arr(_obj(id=_STR, text_ja=_STR, basis=_STR)),
    shared_premise_ja=_STR,
    premise_variants=_arr(_obj(id=_STR, label_ja=_STR, description_ja=_STR, effect_on_issue_ja=_STR)),
    fact_scopes=_obj(domestic=_arr(_STR), foreign_reference_only=_arr(_STR), out_of_scope=_arr(_STR)),
    distinctions=_arr(_obj(term_ja=_STR, definition_ja=_STR)),
    unverified=_arr(_STR), self_check_ja=_arr(_STR))

SCHEMA_S2 = _schema(
    "yp_stakeholders",
    stakeholders=_arr(_obj(id=_STR, who_ja=_STR, contact_point_ja=_STR, stakes_ja=_STR, is_primary=_BOOL, why_would_speak_ja=_STR)),
    primary_parties_excluded=_arr(_obj(who_ja=_STR, reason_ja=_STR)))

SCHEMA_COVERAGE = _schema(
    "yp_primary_coverage",
    items=_arr(_obj(listed_party_ja=_STR, covered=_BOOL, matched_stakeholder_ids=_arr(_STR), note_ja=_STR)))

SCHEMA_S3 = _schema(
    "yp_claim_seeds",
    claim_seeds=_arr(_obj(
        stakeholder_id=_STR,
        claims=_arr(_obj(claim_ja=_STR, kind=_enum(*KIND_VALUES), origin_ja=_STR, rationality=_enum(*RATIONALITY_VALUES),
                         self_contradiction_ja=_STR, factual_risk=_enum("yes", "no"), necessity_note_ja=_STR)))))

_MEMBER = _obj(stakeholder_id=_STR, claim_id=_STR, gender_intrinsic=_enum(*GENDER_INTRINSIC), gender_intrinsic_reason_ja=_STR)
SCHEMA_S4 = _schema(
    "yp_trio_selection",
    candidate_trios=_arr(_obj(trio_id=_enum("T1", "T2", "T3"), members=_arr(_MEMBER), reason_A_ja=_STR, reason_B_ja=_STR, reason_C_ja=_STR,
                              diversity_note_ja=_STR, listener_note_ja=_STR, strongest_objection_ja=_STR)),
    selected_trio_id=_enum("T1", "T2", "T3"), why_not_others_ja=_STR)

SCHEMA_S5 = _schema(
    "yp_persona_sheet",
    age=_INT, gender=_STR, role_ja=_STR, daily_life_ja=_STR, world_variant=_STR, contact_point_ja=_STR,
    experiences_ja=_arr(_STR), troubles_ja=_STR, wishes_honest_ja=_STR, wishes_public_ja=_STR, emotion_habit_ja=_STR, values_ja=_STR,
    interests_ja=_STR, contradiction_or_weakness_ja=_STR,
    speech_style=_obj(first_person=_STR, sentence_length_pattern_ja=_STR, question_back_frequency_ja=_STR, assertion_or_hedging_ja=_STR,
                      vocabulary_layer_ja=_STR),
    entry_mood_ja=_STR, identity_cue_ja=_STR, claim_core_ja=_STR, why_this_person_says_this_ja=_STR,
    known_fact_id=_STR, known_fact_usage_ja=_STR)

SCHEMA_NATURAL = _schema(
    "yp_naturalness",
    most_unnatural_point_ja=_STR, would_listener_feel_wrong=_BOOL, reason_ja=_STR, verdict=_enum("natural", "adjust_claim", "replace_person"))

SCHEMA_STRUCTURE = _schema(
    "yp_structure_tags",
    voices=_arr(_obj(voice=_enum(*SLOTS), opening_type=_enum(*OPENING_TYPES), development_type=_enum(*DEVELOPMENT_TYPES),
                     closing_type=_enum(*CLOSING_TYPES), evidence_ja=_STR)))

SCHEMA_REEVAL_C = _schema("yp_reeval_c", reason_C_ja=_STR, diversity_note_ja=_STR)

SCHEMA_E1_EXTRACT = _schema("yp_e1_extract", items=_arr(_obj(label=_STR, main_point=_STR)))
SCHEMA_E1_MATCH = _schema("yp_e1_match", items=_arr(_obj(label=_STR, verdict=_enum("MATCH", "PARTIAL", "NO"), reason=_STR)))


# ============================================================
# 呼出ラッパ(y0.chatの単一入口を再利用。call記録つき)
# ============================================================
class Ctx:
    def __init__(self, client, out_dir: str, tag: str = ""):
        self.client, self.out_dir, self.tag = client, out_dir, tag
        self.calls: list = []

    def sub(self, *parts) -> str:
        d = os.path.join(self.out_dir, *parts)
        os.makedirs(os.path.dirname(d) if os.path.splitext(d)[1] else d, exist_ok=True)
        return d


def call_json(ctx: Ctx, *, stage: str, model: str, effort: str, developer: str, user: str, schema: dict) -> dict:
    resp = y0.chat(ctx.client, model=model, effort=effort, user=user, developer=developer, schema=schema, stage=f"ypl_{stage}")
    text = getattr(resp, "output_text", None)
    if not text or not text.strip():
        raise PipelineStop("EMPTY_RESPONSE", stage)
    meta = {"stage": stage, "model": model, "effort": effort, **y0.resp_meta(resp), "prompt_sha256": w1.sha_text(user)}
    ctx.calls.append(meta)
    return {"parsed": json.loads(text), "meta": meta}


def call_text(ctx: Ctx, *, stage: str, model: str, effort: str, developer: str, user: str) -> tuple:
    resp = y0.chat(ctx.client, model=model, effort=effort, user=user, developer=developer, stage=f"ypl_{stage}")
    meta = {"stage": stage, "model": model, "effort": effort, **y0.resp_meta(resp), "prompt_sha256": w1.sha_text(user)}
    ctx.calls.append(meta)
    return resp.output_text.strip(), meta


def cached_json(path: str, fn):
    """既存artifactがあれば再利用(二重課金防止)。"""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    out = fn()
    w1.wj(path, out)
    return out


# ============================================================
# Ledgerの整形(S1の入力。題材のVoice割当情報は渡さない)
# ============================================================
def office_ledger_facts(raw: str) -> str:
    """editorial_b_voices_trial_06 のLedgerから、Fact本文のみを抜く(旧Voice割当・タグ・『固定席側/フリーアドレス側』の注記は除く。LLM 0 call)。"""
    start = raw.find("=== VOICE_1_EVIDENCE")
    body = raw[start:] if start >= 0 else raw
    blocks = re.split(r"\n(?=\[(?:VOICE_1_EVIDENCE|VOICE_2_EVIDENCE|CROSS_REFERENCE)\])", body)
    out = []
    for b in blocks:
        m = re.match(r"\[(?:VOICE_1_EVIDENCE|VOICE_2_EVIDENCE|CROSS_REFERENCE)\]\s*([0-9A-Za-z\-]+)\s*(?:\(fact_\d+[^)]*\))?\s*:?\s*(.*)", b, re.S)
        if not m:
            continue
        fid, rest = m.group(1), m.group(2)
        main = re.split(r"\n\s*(?:source|counter_or_limitation|verification):", rest)[0]
        lim = re.search(r"counter_or_limitation:\s*(.*?)(?=\n\s*verification:|\Z)", rest, re.S)
        text = "".join(x.strip() for x in main.split("\n"))
        text = re.sub(r"[(（][^()（）]*VOICE_[12]_EVIDENCE[^()（）]*[)）]", "", text)       # 旧Voice割当への言及を除く
        limit = "".join(x.strip() for x in lim.group(1).split("\n")) if lim else ""
        out.append(f"{fid}: {text}" + (f"(限界: {limit})" if limit else ""))
    return "\n".join(out)


def school_ledger_facts(raw: str) -> str:
    """school_phone_banのLedger(research_ledger/verified_fact_ledger.txt)から、[VERIFIED] ID: 本文 と scope のみを抜く。"""
    out = []
    for b in re.split(r"\n\s*\n", raw):
        m = re.match(r"\[VERIFIED\]\s*([A-Z0-9\-]+):\s*(.*)", b.strip(), re.S)
        if not m:
            continue
        lines = m.group(2).split("\n")
        scope = re.search(r"scope:\s*(.*)", b)
        head = lines[0].strip()
        out.append(f"{m.group(1)}: {head}" + (f"(対象: {scope.group(1).strip()})" if scope else ""))
    return "\n".join(out)


# ============================================================
# S1 世界設定
# ============================================================
S1_DEVELOPER = "あなたは、複数の人物が語るラジオ読み物の編集者です。人物を考える前に、記事で扱う争点の『世界設定』だけを確定します。"


def build_s1_prompt(topic_ja: str, facts: str) -> str:
    return f"""次のテーマについて、記事で扱う争点の「世界設定」を確定してください。読者は日本の英語学習者で、登場する人は日本で暮らす人です。人物はまだ考えません。

テーマ: {topic_ja}

【調査済みの事実(Research台帳。各行の頭が根拠ID)】
{facts}

【作り方】
- question_ja: 争点を「〜するか」の1文で。具体的な規則・行為と、現状からの変化がわかる形にする。
- title_ja: 日本語タイトル(25字以内、争点が分かり、「それぞれの声」で終わる)。
- setting: 国・地域、制度や組織の種類、対象者、時代。
- status_quo: 現行の実態を5〜8件。各件にid(SQ1, SQ2…)、text_ja(1文)、basis(根拠の台帳ID。複数ならカンマ区切り。根拠がなければ「なし」)。台帳にない実態は書かない。外国の事例を入れる場合は、text_jaに「外国の事例」と明記する(日本の実態として書かない)。
- shared_premise_ja: 3人に共通の前提を100字以内で。聞いて一度で分かる言い方にする。
- premise_variants: 人物ごとに前提が異なってよい点(例: 学校の種類・雇用形態)と、その違いが争点に与える影響。なければ空配列。人物が後から勝手に発明してはならないので、ここで宣言する。
- fact_scopes: 台帳IDを domestic(日本の実態)/foreign_reference_only(外国の事例。国による違いの対照にだけ使える)/out_of_scope に分ける。
- distinctions: 混同しやすい区分の定義(例: 似た言葉の使い分け)。争点を語る人が取り違えやすい点を3つ程度。
- unverified: 確認できていない点。
- self_check_ja: 国・制度・対象者の混同がないか、3問程度の自己点検と結論。

重要: 外国の制度・調査を、日本の一般的な状況として書かない。実態の根拠が弱い争点なら、根拠のある争点へ見直してよい(その理由をself_check_jaに書く)。"""


def validate_world_frame(wf: dict, ledger_ids: set) -> list:
    errs = []
    for k in ("question_ja", "title_ja", "shared_premise_ja"):
        if not wf.get(k):
            errs.append(f"S1_EMPTY:{k}")
    if len(wf.get("shared_premise_ja", "")) > 110:
        errs.append("S1_PREMISE_GT100")
    sq = wf.get("status_quo") or []
    if len(sq) < 3:
        errs.append("S1_STATUS_QUO_LT3")
    ids = [x["id"] for x in sq]
    if len(set(ids)) != len(ids):
        errs.append("S1_STATUS_QUO_ID_DUP")
    foreign = set(wf.get("fact_scopes", {}).get("foreign_reference_only", []))
    for x in sq:
        if not x.get("basis"):
            errs.append(f"S1_NO_BASIS:{x['id']}")
        used = {b.strip() for b in re.split(r"[,、]", x.get("basis", "")) if b.strip()}
        if used and used <= foreign and "外国" not in x.get("text_ja", ""):
            errs.append(f"S1_STATUS_QUO_ONLY_FOREIGN_BASIS:{x['id']}")
    if not wf.get("self_check_ja"):
        errs.append("S1_NO_SELF_CHECK")
    return errs


def stage_s1(ctx: Ctx, topic_ja: str, facts: str, ledger_ids: set) -> dict:
    r = call_json(ctx, stage="s1", model=MODEL_TOP, effort="high", developer=S1_DEVELOPER, user=build_s1_prompt(topic_ja, facts), schema=SCHEMA_S1)
    wf = r["parsed"]
    return {"world_frame": wf, "validation_errors": validate_world_frame(wf, ledger_ids), "meta": r["meta"]}


# 承認済み世界設定(school_phone_ban。WORLD_SETTING_01.md を構造化出力形式へ転記。OF-Y5-09: 以降の工程はこちらを使う)
SCHOOL_WORLD_FRAME_APPROVED = {
    "question_ja": "日本の高校で、今は授業中だけ使えないスマホを、休み時間や昼休みを含む校内全体で使わないことにするか。",
    "title_ja": "休み時間もスマホを使わない学校、それぞれの声",
    "setting": {"country": "日本", "institution_type": "高校(全日制・定時制)", "population": "高校生と、その家族・学校の大人たち", "era": "現在"},
    "status_quo": [
        {"id": "SQ1", "text_ja": "国の通知は、高校については校内での携帯電話の使用を制限すべきという考え方を示している(持ち込み禁止ではなく校内使用の制限)。", "basis": "JP-03"},
        {"id": "SQ2", "text_ja": "高校の運用は、持ち込みは認めたうえで授業中だけ禁止にする学校が多く、校内使用を一律に禁止する学校は少数である(埼玉県2014年調査: 全日制は授業中のみ83校・校内使用禁止38校、定時制は授業中のみ22校・校内使用禁止2校)。", "basis": "埼玉県教委2014調査"},
        {"id": "SQ3", "text_ja": "登校時にスマホを預かって下校時に返す運用は、通知では小学校・中学校の配慮措置として例示されたもので、高校の項にはない。埼玉県の高校では実施0校だった。", "basis": "通知本文,埼玉県教委2014調査"},
        {"id": "SQ4", "text_ja": "オランダは授業中の使用を認めない運用をとっている(外国の事例。国による違いの対照)。", "basis": "NL-01"},
        {"id": "SQ5", "text_ja": "定時制には働きながら通う生徒がいる。", "basis": "埼玉県教委2014調査(定時制25校の区分)"},
    ],
    "shared_premise_ja": "日本の高校で、スマホの持ち込みは認めたまま、授業中だけでなく休み時間や昼休みも校内では使わないことにするかどうか。",
    "premise_variants": [
        {"id": "full_time", "label_ja": "全日制の高校", "description_ja": "昼間に通う高校。休み時間・昼休みがあり、放課後は家や部活。",
         "effect_on_issue_ja": "休み時間の友達との連絡や、放課後の家族との連絡の取り方が変わる。"},
        {"id": "part_time", "label_ja": "夜間の定時制の高校", "description_ja": "昼に働いて夜に通う生徒がいる。授業の合間に短い休み時間がある。",
         "effect_on_issue_ja": "仕事の連絡を受ける時間が休み時間に限られ、休み時間の使用禁止が仕事に直接当たる。"},
    ],
    "fact_scopes": {"domestic": ["JP-03"], "foreign_reference_only": ["NL-01", "FR-01", "FR-02", "EN-01", "STUDY-01", "STUDY-04"], "out_of_scope": ["OECD-01", "OECD-02", "JP-01", "JP-02"]},
    "distinctions": [
        {"term_ja": "持ち込み禁止", "definition_ja": "学校にスマホを持ってこさせないこと。今回の争点ではない。"},
        {"term_ja": "校内使用禁止", "definition_ja": "持ち込みは認めたうえで、休み時間・昼休みを含めて校内では使わないこと。今回の争点。"},
        {"term_ja": "授業中のみ禁止", "definition_ja": "持ち込みを認め、授業中だけ使えないこと。現在の多くの高校の運用。"},
        {"term_ja": "預かり・返却", "definition_ja": "登校後に学校が預かり、下校時に返すこと。通知では小中の配慮措置の例で、高校では実施の確認がない。今回の争点ではない。"},
    ],
    "unverified": ["実データは埼玉県2014年の1県・公立のみ。近年・他県で高校が終日回収を採った例は確認できていない。"],
    "self_check_ja": ["国・制度・対象者: 日本の高校。外国の事例はオランダのみ対照に使い、日本の実態として書いていない。",
                      "規則の混同: 持ち込み禁止・授業中のみ禁止・校内使用禁止・預かり返却を区別した(distinctions)。",
                      "対象者: 全日制と夜間定時制の違いをpremise_variantsで先に宣言した。"],
}


def compare_s1_to_approved(generated: dict, approved: dict) -> dict:
    """OF-Y5-09: S1(LLM)出力を承認済み設定と照合する観測(Gateにしない)。決定論の機械照合のみ。意味の差は報告者が読む。"""
    g = json.dumps(generated, ensure_ascii=False)
    checks = {
        "country_is_japan": generated.get("setting", {}).get("country", "").startswith("日本"),
        "mentions_break_or_campus_wide_use": any(w in generated.get("question_ja", "") for w in ("休み時間", "昼休み", "校内")),
        "question_not_all_day_collection": not any(w in generated.get("question_ja", "") for w in ("朝に預か", "終日", "回収")),
        "declares_part_time_variant": any(("定時制" in v.get("label_ja", "") + v.get("description_ja", "")) for v in generated.get("premise_variants", [])),
        "has_distinctions_ge3": len(generated.get("distinctions", [])) >= 3,
        "distinguishes_carry_ban_vs_use": ("持ち込み" in g or "持込" in g) and ("使用" in g),
        "foreign_facts_separated": bool(generated.get("fact_scopes", {}).get("foreign_reference_only")),
        "foreign_fr_not_in_domestic": not any(i.startswith(("FR-", "EN-", "NL-", "STUDY")) for i in generated.get("fact_scopes", {}).get("domestic", [])),
        "status_quo_mentions_hs_not_collected": ("預かり" in g or "回収" in g) and ("高校" in g),
    }
    return {"checks": checks, "n_pass": sum(1 for v in checks.values() if v), "n_total": len(checks),
            "approved_question": approved["question_ja"], "generated_question": generated.get("question_ja")}


# ============================================================
# S2 当事者の洗い出し
# ============================================================
S2_DEVELOPER = "あなたは、複数の人物が語るラジオ読み物の編集者です。ある争点について、当事者になり得る立場を幅広く洗い出します。選ぶことも評価することもしません。"


def world_frame_for_prompt(wf: dict) -> str:
    sq = "\n".join(f"- {x['id']}: {x['text_ja']}" for x in wf["status_quo"])
    pv = "\n".join(f"- {v['id']}({v['label_ja']}): {v['description_ja']} / 争点への影響: {v['effect_on_issue_ja']}" for v in wf.get("premise_variants", [])) or "(なし。全員同一前提)"
    ds = "\n".join(f"- {d['term_ja']}: {d['definition_ja']}" for d in wf.get("distinctions", []))
    return (f"争点: {wf['question_ja']}\n国・対象: {wf['setting']['country']} / {wf['setting']['institution_type']} / {wf['setting']['population']}\n"
            f"現行の実態:\n{sq}\n人物ごとに異なってよい前提:\n{pv}\n区別の定義:\n{ds}\n共通の前提: {wf['shared_premise_ja']}")


def build_s2_prompt(wf: dict) -> str:
    return f"""次の争点について、「誰がこの争点の当事者になり得るか」を洗い出してください。

【世界設定】
{world_frame_for_prompt(wf)}

【洗い出し方】
- 直接の当事者・間接の当事者・制度側・周辺に分けて考え、最初から3人に絞らず、8件以上12件以内の立場を挙げる。賛成・反対のラベルは付けない。
- 各立場: id(S01, S02…)、who_ja(年齢層と、生活・役割を一言)、contact_point_ja(この争点・規則が、その人の日々の何に作用するか。具体的に1〜2文)、stakes_ja(得るもの・失うもの・負うもの)、is_primary(規則の対象者本人・実施運用者・直接影響を受ける家族/同居者/第三者のいずれかならtrue)、why_would_speak_ja(この人がこの争点について語る自然な理由)。
- 当事者の型(対象者本人・実施運用者・家族・直接コストを負う第三者・制度設計側など)は、考える観点のヒントであり必須の枠ではない。該当なしは理由を挙げなくてよい。
- 主要当事者を候補に入れない場合に限り、primary_parties_excluded に who_ja と reason_ja(根拠)を書く。除外理由として使えないもの: 声・年齢・音声化・既に使った型・記事の都合。
- 想起しやすい立場だけに偏らない。現実にこの争点の影響を受ける人を、生活の側から探す。"""


def validate_stakeholders(obj: dict) -> list:
    errs = []
    sh = obj.get("stakeholders") or []
    if len(sh) < 8:
        errs.append(f"S2_COUNT_LT8:{len(sh)}")
    ids = [x["id"] for x in sh]
    if len(set(ids)) != len(ids):
        errs.append("S2_ID_DUP")
    if not any(x["is_primary"] for x in sh):
        errs.append("S2_NO_PRIMARY")
    for x in obj.get("primary_parties_excluded") or []:
        if not x.get("reason_ja"):
            errs.append("S2_EXCLUSION_NO_REASON")
    for x in sh:
        for k in ("who_ja", "contact_point_ja", "stakes_ja", "why_would_speak_ja"):
            if not x.get(k):
                errs.append(f"S2_EMPTY:{x['id']}:{k}")
    return errs


def stage_s2(ctx: Ctx, wf: dict) -> dict:
    """件数<8・主要当事者なし・根拠なき除外は、1回だけやり直す(DESIGN_PROPOSAL_05 §3)。残ればSTOP。"""
    user = build_s2_prompt(wf)
    hist = []
    for k in (1, 2):
        r = call_json(ctx, stage="s2" + ("" if k == 1 else "_redo"), model=MODEL_TOP, effort="medium", developer=S2_DEVELOPER, user=user, schema=SCHEMA_S2)
        errs = validate_stakeholders(r["parsed"])
        hist.append({"try": k, "errors": errs, "meta": r["meta"]})
        if not errs:
            return {**r["parsed"], "validation_errors": [], "history": hist}
        user = user + "\n\n【前回の出力の問題(今回は避ける)】\n" + "\n".join(f"- {e}" for e in errs)
    raise PipelineStop("S2_INVALID", f"S2が2回条件を満たさない {hist[-1]['errors']}", hist)


COVERAGE_DEVELOPER = "あなたは判定者です。事前に固定された主要当事者リストの各項目が、洗い出された立場(stakeholders)に含まれているかを、根拠つきで判定します。"


def build_coverage_prompt(listed: list, stakeholders: list) -> str:
    st = "\n".join(f"{x['id']}: {x['who_ja']}｜接点: {x['contact_point_ja']}" for x in stakeholders)
    ls = "\n".join(f"- {x}" for x in listed)
    return f"""【洗い出された立場】
{st}

【事前に固定された主要当事者リスト】
{ls}

リストの各項目ごとに、洗い出された立場の中にその項目に実質的に当たる立場があればcovered=true、matched_stakeholder_idsにそのid、note_jaに理由(1文)。当たる立場がなければcovered=false。表現が違っても同じ実質の立場なら当たるとする(完全一致は求めない)。リストにない立場は評価しない。"""


def stage_coverage(ctx: Ctx, listed: list, stakeholders: list) -> dict:
    r = call_json(ctx, stage="s2_coverage", model=MODEL_CHEAP, effort="medium", developer=COVERAGE_DEVELOPER,
                  user=build_coverage_prompt(listed, stakeholders), schema=SCHEMA_COVERAGE)
    items = r["parsed"]["items"]
    n = sum(1 for x in items if x["covered"])
    return {"listed": listed, "items": items, "n_covered": n, "n_listed": len(listed), "meta": r["meta"]}


# ============================================================
# S3 立場ごとの主張探索(台帳Factは入力にしない)
# ============================================================
S3_DEVELOPER = "あなたは、複数の人物が語るラジオ読み物の編集者です。各立場の人が、その争点について言い得る主張の種を探索します。選ばず、評価もしません。"


def stakeholders_for_prompt(sh: list) -> str:
    return "\n".join(f"{x['id']}: {x['who_ja']}｜接点: {x['contact_point_ja']}｜利害: {x['stakes_ja']}" for x in sh)


def build_s3_prompt(wf: dict, sh: list) -> str:
    return f"""次の争点について、各立場の人が言い得る主張の種を探索してください。

【世界設定】
{world_frame_for_prompt(wf)}

【立場の一覧】
{stakeholders_for_prompt(sh)}

【探索の仕方】
- 立場ごとに3〜4件の主張を挙げる(stakeholder_idは上のidを使う)。同じ立場から相反する主張が出てよい。
- claim_ja: 本人の言葉で一文(セリフではなく主張の方向。数字・実在の固有名詞は使わない)。
- kind: 要求/拒否/不安/怒り/願望/あきらめ/思い込み/自己都合/矛盾した本音/その他。立場ごとに2種類以上にし、うち1件以上は「自己都合・怒り・矛盾した本音」のいずれかにする。
- origin_ja: その主張が、本人の経験・利害・感情・価値観のどこから生じるか(1〜2文。立場の接点・利害につなげる)。
- rationality: 筋が通る/本人なりの理屈/感情先行/思い込みを含む。合理的・客観的に正しくなくてよい。感情的な反発・自己中心的な願望・思い込み・矛盾を含めてよい。
- self_contradiction_ja: 本人の中の矛盾があれば書く(なければ空文字)。
- factual_risk: 「現行の実態」にない制度・統計・事実の断定を含むならyes。制度や事実を誤って説明する主張は作らない(本人の推測・印象として語れる範囲にする)。
- necessity_note_ja: origin_jaが立場の接点・利害に接続している理由(1文)。
- 人物固有のセリフ・エピソード(誰が何を言った等)は作らない。"""


def number_claims(obj: dict) -> list:
    """claim_seedsを平坦化し、決定論でid(<stakeholder_id>_c<k>)を振る。"""
    flat = []
    for cs in obj["claim_seeds"]:
        for k, c in enumerate(cs["claims"], 1):
            flat.append({**c, "id": f"{cs['stakeholder_id']}_c{k}", "stakeholder_id": cs["stakeholder_id"]})
    return flat


def validate_claims(flat: list, stakeholder_ids: list) -> dict:
    errs, warns = [], []
    by = {}
    for c in flat:
        by.setdefault(c["stakeholder_id"], []).append(c)
    for sid in stakeholder_ids:
        cs = by.get(sid, [])
        if len(cs) < 3:
            errs.append(f"S3_LT3:{sid}:{len(cs)}")
            continue
        if any(not c["origin_ja"] for c in cs):
            errs.append(f"S3_NO_ORIGIN:{sid}")
        if len({c["kind"] for c in cs}) < 2:
            warns.append(f"S3_KIND_LT2:{sid}")
        if not any(c["kind"] in SELFISH_KINDS for c in cs):
            warns.append(f"S3_NO_SELFISH_OR_CONTRADICTION:{sid}")
    for sid in by:
        if sid not in stakeholder_ids:
            errs.append(f"S3_UNKNOWN_STAKEHOLDER:{sid}")
    return {"errors": errs, "warnings": warns}


def stage_s3(ctx: Ctx, wf: dict, sh: list) -> dict:
    user = build_s3_prompt(wf, sh)
    ids = [x["id"] for x in sh]
    hist = []
    for k in (1, 2):
        r = call_json(ctx, stage="s3" + ("" if k == 1 else "_redo"), model=MODEL_TOP, effort="medium", developer=S3_DEVELOPER, user=user, schema=SCHEMA_S3)
        flat = number_claims(r["parsed"])
        v = validate_claims(flat, ids)
        hist.append({"try": k, **v, "meta": r["meta"]})
        if not v["errors"]:
            eligible = [c for c in flat if c["factual_risk"] == "no"]
            return {"claims": flat, "n_claims": len(flat), "n_factual_risk_yes": len(flat) - len(eligible),
                    "excluded_factual_risk_ids": [c["id"] for c in flat if c["factual_risk"] == "yes"], "warnings": v["warnings"], "history": hist}
        user = user + "\n\n【前回の出力の問題(今回は避ける)】\n" + "\n".join(f"- {e}" for e in v["errors"])
    raise PipelineStop("S3_INVALID", f"S3が2回条件を満たさない {hist[-1]['errors']}", hist)


# ============================================================
# S4 3 Voiceの組合せ選定
# ============================================================
S4_DEVELOPER = "あなたは、複数の人物が語るラジオ読み物の編集者です。洗い出した立場と主張の種から、3人の組合せを選びます。反論も自分で検討します。"


def build_s4_prompt(wf: dict, sh: list, eligible_claims: list, extra: str = "") -> str:
    by = {}
    for c in eligible_claims:
        by.setdefault(c["stakeholder_id"], []).append(c)
    blocks = []
    for x in sh:
        cl = by.get(x["id"], [])
        if not cl:
            continue
        cs = "\n".join(f"    - {c['id']}[{c['kind']}/{c['rationality']}]: {c['claim_ja']}｜出所: {c['origin_ja']}" for c in cl)
        blocks.append(f"{x['id']}: {x['who_ja']}\n  接点: {x['contact_point_ja']}\n  利害: {x['stakes_ja']}\n  主張の種:\n{cs}")
    return f"""次の争点について、3人(Voice)の組合せを選んでください。3人は、それぞれ自分の暮らしから、同じ争点について一人称で語ります。

【世界設定】
{world_frame_for_prompt(wf)}

【立場と主張の種(事実の断定を含むものは除外済み)】
{chr(10).join(blocks)}

【選び方】
- 評価の3軸: A 当事者性(この人がこの争点を語る自然な理由があるか)/ B 主張の必然性(この人の経験・利害・感情・価値観から、この主張が生まれることに納得できるか)/ C 組合せ価値(3人を聞くと、単独では得られない何が生まれるか)。加えて視点の多様性、聞き手の理解しやすさ。
- 互いに異なる候補の組(T1, T2, T3)を3つ出す。各組は異なる3つの立場から1つずつ、その立場の主張の種を1つ選ぶ(claim_idは上のidを使う)。組どうしは少なくとも1人は異なる立場にする。
- 各組に: reason_A_ja(当事者性。選んだ立場のcontact_pointを『』で原文のまま引用して説明)/ reason_B_ja(主張の必然性。選んだ主張のoriginを『』で原文のまま引用して説明)/ reason_C_ja(組合せ価値。対立・発見・面白さを具体的に1〜2文)/ diversity_note_ja(向きの分布が2対1になっていないか、型の繰り返しになっていないか、感情・矛盾の出方が3人で同型でないか)/ listener_note_ja(聞き手の理解しやすさ)/ strongest_objection_ja(『この人がこの主張をするのは不自然』と言える最大の反論と、それでも採る理由)。
- 各メンバーのgender_intrinsic: その立場であることから性別が決まるなら「男性」または「女性」、決まらないなら「不問」。理由をgender_intrinsic_reason_jaに。性別を選定の基準にしない(この項目は記録用)。
- 賛成・反対の役割を機械的に割り当てない。単に異なる意見を3つ揃えるための不自然な人物選定をしない。特定の型(家族/現場/第三者など)に毎回収束しない。
- 最後に、最も良い1組をselected_trio_idに選び、why_not_others_jaに他の2組を選ばなかった理由を書く。
{extra}"""


def lcs_len(a: str, b: str) -> int:
    return difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b)).size


def quote_hits(reason: str, sources: list, min_len: int = 8) -> int:
    return sum(1 for s in sources if lcs_len(reason, s) >= min_len)


def validate_s4(obj: dict, sh: list, eligible_claims: list) -> dict:
    errs = []
    shd = {x["id"]: x for x in sh}
    cld = {c["id"]: c for c in eligible_claims}
    trios = obj.get("candidate_trios") or []
    if len(trios) != 3 or len({t["trio_id"] for t in trios}) != 3:
        errs.append("S4_NOT_3_DISTINCT_TRIOS")
    sets = []
    for t in trios:
        ms = t["members"]
        if len(ms) != 3:
            errs.append(f"S4_MEMBERS_NE3:{t['trio_id']}")
            continue
        sids = [m["stakeholder_id"] for m in ms]
        if len(set(sids)) != 3:
            errs.append(f"S4_SAME_STAKEHOLDER:{t['trio_id']}")
        for m in ms:
            if m["stakeholder_id"] not in shd:
                errs.append(f"S4_UNKNOWN_STAKEHOLDER:{m['stakeholder_id']}")
            c = cld.get(m["claim_id"])
            if not c:
                errs.append(f"S4_CLAIM_NOT_ELIGIBLE:{m['claim_id']}")
            elif c["stakeholder_id"] != m["stakeholder_id"]:
                errs.append(f"S4_CLAIM_STAKEHOLDER_MISMATCH:{m['claim_id']}")
        sets.append(frozenset(sids))
    if len(sets) == 3 and len(set(sets)) < 3:
        errs.append("S4_TRIOS_NOT_DISTINCT")
    sel = next((t for t in trios if t["trio_id"] == obj.get("selected_trio_id")), None)
    cites = {}
    if not sel:
        errs.append("S4_SELECTED_MISSING")
    else:
        cp = [shd[m["stakeholder_id"]]["contact_point_ja"] for m in sel["members"] if m["stakeholder_id"] in shd]
        org = [cld[m["claim_id"]]["origin_ja"] for m in sel["members"] if m["claim_id"] in cld]
        cites = {"A_contact_point_quotes": quote_hits(sel["reason_A_ja"], cp), "B_origin_quotes": quote_hits(sel["reason_B_ja"], org)}
        if cites["A_contact_point_quotes"] < 2:
            errs.append(f"S4_REASON_A_QUOTES_LT2:{cites['A_contact_point_quotes']}")
        if cites["B_origin_quotes"] < 2:
            errs.append(f"S4_REASON_B_QUOTES_LT2:{cites['B_origin_quotes']}")
        if not sel.get("strongest_objection_ja"):
            errs.append("S4_NO_OBJECTION")
    return {"errors": errs, "citations": cites}


def stage_s4(ctx: Ctx, wf: dict, sh: list, claims: list) -> dict:
    eligible = [c for c in claims if c["factual_risk"] == "no"]
    extra = ""
    hist = []
    for k in (1, 2):
        r = call_json(ctx, stage="s4" + ("" if k == 1 else "_redo"), model=MODEL_TOP, effort="high", developer=S4_DEVELOPER,
                      user=build_s4_prompt(wf, sh, eligible, extra), schema=SCHEMA_S4)
        v = validate_s4(r["parsed"], sh, eligible)
        hist.append({"try": k, **v, "meta": r["meta"]})
        if not v["errors"]:
            return {**r["parsed"], "validation": v, "history": hist}
        extra = "\n【前回の出力の問題(今回は避ける)】\n" + "\n".join(f"- {e}" for e in v["errors"]) + "\n理由(reason_A/B)では、選んだ各メンバーのcontact_point/originを『』で原文のまま引用すること。"
    raise PipelineStop("S4_INVALID", f"S4が2回条件を満たさない {hist[-1]['errors']}", hist)


def assign_slots(members: list) -> dict | None:
    """OF-Y5-01: 決定論のスロット割当。性別が確定している人物(gender_intrinsic)を先に置き、『不問』には空きスロットの性別を付与する。
    S4メンバー順の辞書順で最初に成立する割当を採る。成立しなければNone(手作業で直さず報告)。"""
    for perm in itertools.permutations(range(3)):
        ok = all(m["gender_intrinsic"] in ("不問", SLOT_GENDER[SLOTS[perm[i]]]) for i, m in enumerate(members))
        if ok:
            return {SLOTS[perm[i]]: {**m, "assigned_gender": SLOT_GENDER[SLOTS[perm[i]]]} for i, m in enumerate(members)}
    return None


def slot_feasible_for(member: dict, slot: str) -> bool:
    return member["gender_intrinsic"] in ("不問", SLOT_GENDER[slot])


# ============================================================
# S5 Persona構築 + 自然さ検証(別call)
# ============================================================
S5_DEVELOPER = "あなたは、複数の人物が語るラジオ読み物の編集者です。ある立場の実在しそうな一人の人物を、生活・経験・利害から具体的に設計します。台詞は書きません。"


def build_s5_prompt(wf: dict, stakeholder: dict, claim: dict, assigned_gender: str, others_claims: list, avoid_first_persons: list = None) -> str:
    sq = "\n".join(f"- {x['id']}: {x['text_ja']}" for x in wf["status_quo"])
    pv = "\n".join(f"- {v['id']}({v['label_ja']}): {v['description_ja']}" for v in wf.get("premise_variants", [])) or "(なし。world_variantは common とする)"
    oc = "\n".join(f"- {c}" for c in others_claims)
    avoid = (f"\n- first_personは次のいずれとも重ならないものにする: {'、'.join(avoid_first_persons)}" if avoid_first_persons else "")
    return f"""次の立場と主張の種を持つ、実在しそうな具体的な一人の人物を設計してください。この人は、ラジオで自分の暮らしから一人称で語ります。

【世界設定】
{world_frame_for_prompt(wf)}
現行の実態のID一覧(known_fact_idに選べる):
{sq}

【この人の立場】
{stakeholder['who_ja']}
この争点との接点: {stakeholder['contact_point_ja']}
利害: {stakeholder['stakes_ja']}

【この人の主張の種(方向性。セリフにしない)】
{claim['claim_ja']}
出所: {claim['origin_ja']}

【他の2人の主張(重複を避けるためだけに参照)】
{oc}

【設計の規則】
- gender は「{assigned_gender}」に固定(音声の都合)。年齢は立場から自然な年齢にする(誘導しない)。
- world_variant は次のid、または common:
{pv}
- experiences_ja: この人の具体的な経験を2つ以内(物・場所・相手の言葉・自分の動きが分かる形。実在の固有名詞・数字は使わない)。
- troubles_ja / wishes_honest_ja(本音)/ wishes_public_ja(建前)/ emotion_habit_ja(感情の癖)/ values_ja / interests_ja(利害)。
- contradiction_or_weakness_ja: 矛盾や弱さを、人物の属性として持たせる(語りに出すかどうかは問わない)。
- speech_style: 英訳しても残る特徴。first_person(一人称)、sentence_length_pattern_ja(文の長さの型)、question_back_frequency_ja、assertion_or_hedging_ja(断言/留保)、vocabulary_layer_ja(語彙の層)。{avoid}
- entry_mood_ja: 語り出す時の心の状態(例: 言い訳から/怒りから/戸惑いから/ぼやきから)。
- identity_cue_ja: 聞き手が冒頭で、この人がどんな人か自然に分かる手がかり(仕事・立場・家族などを出来事や状況として。自己紹介文にしない)。
- claim_core_ja: この人が言いたいことの芯(方向性。セリフではなく、数字・実在名を含めない。固定しすぎない)。
- why_this_person_says_this_ja: この人の生活・経験・利害から、その主張が生まれる道筋を3〜5文で。
- known_fact_id: この人が知っていてよい世の中の事実を、現行の実態のIDから最大1つ選ぶ(なければ空文字)。known_fact_usage_ja: どう触れるか(本人が主語の伝聞・印象として1文だけ。数字・調査名を出さない。論証に使わない)。なければ空文字。
- 痛み・失敗・矛盾を語りに出すことは必須にしない。この人らしい感情の出方にする。"""


NATURAL_DEVELOPER = "あなたは、ラジオの聞き手の立場の批評者です。人物の設計メモを読み、その人がその主張を語ることの不自然さを探します。"


def build_natural_prompt(wf: dict, sheet: dict, stakeholder_who: str) -> str:
    """OF-Y5-07: 別callで『最も不自然な点を必ず1つ挙げ、聞き手に違和感を与えるか』を判定する。因果説明(why_this_person_says_this)は見せない。"""
    ex = "\n".join(f"- {e}" for e in sheet["experiences_ja"])
    return f"""次の人物が、ラジオで「{wf['question_ja']}」について語ります。

【人物】{stakeholder_who}({sheet['age']}歳、{sheet['gender']}、{sheet['role_ja']})
生活: {sheet['daily_life_ja']}
この争点との接点: {sheet['contact_point_ja']}
経験:
{ex}
本音: {sheet['wishes_honest_ja']} / 建前: {sheet['wishes_public_ja']}
利害: {sheet['interests_ja']}
語りたいことの芯: {sheet['claim_core_ja']}

【やること】
1. この人がこの芯を語ることについて、最も不自然な点を必ず1つ挙げる(most_unnatural_point_ja)。
2. その不自然さが、聞き手に「この人がそれを言うのは変だ」という違和感を与えるほどか(would_listener_feel_wrong)を判定し、理由を書く。細かい点なら違和感ではない。
3. verdict: 違和感がなければ natural。違和感があり、この人のまま芯だけ直せば自然になるなら adjust_claim。この人がその争点を語ること自体が不自然なら replace_person。"""


def validate_sheet(sheet: dict, wf: dict, assigned_gender: str) -> list:
    errs = []
    pvs = {v["id"] for v in wf.get("premise_variants", [])} | {"common"}
    if sheet["world_variant"] not in pvs:
        errs.append(f"S5_WORLD_VARIANT_UNDECLARED:{sheet['world_variant']}")
    if sheet["gender"] != assigned_gender:
        errs.append(f"S5_GENDER_MISMATCH:{sheet['gender']}!={assigned_gender}")
    if len(sheet["experiences_ja"]) > 2:
        errs.append("S5_EXPERIENCES_GT2")
    if re.search(r"[0-9０-９]", sheet["claim_core_ja"]) or p.NUM_RE.search(sheet["claim_core_ja"]):
        errs.append("S5_CLAIM_CORE_HAS_NUMBER")
    for k in ("claim_core_ja", "why_this_person_says_this_ja", "entry_mood_ja", "identity_cue_ja"):
        if not sheet.get(k):
            errs.append(f"S5_EMPTY:{k}")
    if not sheet["speech_style"]["first_person"] or len(sheet["speech_style"]["first_person"]) > 4:
        errs.append("S5_FIRST_PERSON_INVALID")
    sqids = {x["id"] for x in wf["status_quo"]}
    if sheet["known_fact_id"] and sheet["known_fact_id"] not in sqids:
        errs.append(f"S5_KNOWN_FACT_NOT_IN_STATUS_QUO:{sheet['known_fact_id']}")
    return errs


def age_band(age: int) -> str:
    return "10代" if age < 20 else f"{age // 10 * 10}代"


def check_overlaps(sheets: dict) -> dict:
    """OF-Y5-01: 一人称・年齢帯の3人重複の決定論確認(記録。一人称の重複は呼出側で後の人物のS5を1回やり直す)。"""
    fps = {s: sheets[s]["speech_style"]["first_person"] for s in SLOTS}
    bands = {s: age_band(sheets[s]["age"]) for s in SLOTS}
    dup_fp = sorted({v for v in fps.values() if list(fps.values()).count(v) > 1})
    return {"first_persons": fps, "age_bands": bands, "first_person_duplicates": dup_fp, "all_same_age_band": len(set(bands.values())) == 1,
            "under_18": [s for s in SLOTS if sheets[s]["age"] < 18]}


def build_s5_for(ctx: Ctx, wf: dict, slot: str, member: dict, sh_by: dict, cl_by: dict, others: list, avoid_fp: list = None, tag: str = "") -> dict:
    stk, clm = sh_by[member["stakeholder_id"]], cl_by[member["claim_id"]]
    gender = member.get("assigned_gender") or SLOT_GENDER[slot]
    r = call_json(ctx, stage=f"s5_{slot}{tag}", model=MODEL_TOP, effort="high", developer=S5_DEVELOPER,
                  user=build_s5_prompt(wf, stk, clm, gender, others, avoid_fp), schema=SCHEMA_S5)
    sheet = r["parsed"]
    nat = call_json(ctx, stage=f"s5_natural_{slot}{tag}", model=MODEL_CHEAP, effort="medium", developer=NATURAL_DEVELOPER,
                    user=build_natural_prompt(wf, sheet, stk["who_ja"]), schema=SCHEMA_NATURAL)
    return {"slot": slot, "stakeholder_id": member["stakeholder_id"], "claim_id": member["claim_id"], "gender_intrinsic": member["gender_intrinsic"],
            "assigned_gender": gender, "sheet": sheet, "validation_errors": validate_sheet(sheet, wf, gender), "naturalness": nat["parsed"],
            "meta": [r["meta"], nat["meta"]]}


def next_claim_same_stakeholder(claims: list, stakeholder_id: str, used_ids: set) -> dict | None:
    for c in claims:
        if c["stakeholder_id"] == stakeholder_id and c["factual_risk"] == "no" and c["id"] not in used_ids:
            return c
    return None


def next_replacement_member(s4: dict, current: dict, slot: str, used_stakeholders: set, used_claims: set, claims: list) -> dict | None:
    """差戻し(replace_person): S4の次点の組合せ(選ばれなかった候補)から、未使用の立場の人を順に探す。スロットの性別に合うものだけ。"""
    cld = {c["id"]: c for c in claims}
    for t in s4["candidate_trios"]:
        if t["trio_id"] == s4["selected_trio_id"]:
            continue
        for m in t["members"]:
            if m["stakeholder_id"] in used_stakeholders or m["claim_id"] in used_claims or m["claim_id"] not in cld:
                continue
            if slot_feasible_for(m, slot):
                return dict(m)
    return None


def stage_s5(ctx: Ctx, wf: dict, sh: list, claims: list, s4: dict) -> dict:
    sh_by = {x["id"]: x for x in sh}
    cl_by = {c["id"]: c for c in claims}
    sel = next(t for t in s4["candidate_trios"] if t["trio_id"] == s4["selected_trio_id"])
    assign = assign_slots(sel["members"])
    if assign is None:
        raise PipelineStop("SLOT_ASSIGNMENT_INFEASIBLE",
                           f"選定trioの性別確定人物が固定Voice(男・女・男)に割当不能: {[m['gender_intrinsic'] for m in sel['members']]}(声セット変更はユーザー判断。手作業で直さない)", sel)
    members = dict(assign)

    def others_of(slot):
        return [cl_by[members[o]["claim_id"]]["claim_ja"] for o in SLOTS if o != slot]

    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {s: ex.submit(build_s5_for, ctx, wf, s, members[s], sh_by, cl_by, others_of(s)) for s in SLOTS}
        built = {s: f.result() for s, f in futs.items()}
    log = {"assignment": {s: {k: members[s][k] for k in ("stakeholder_id", "claim_id", "gender_intrinsic", "assigned_gender")} for s in SLOTS},
           "initial": {s: {"naturalness": built[s]["naturalness"], "errors": built[s]["validation_errors"]} for s in SLOTS}, "rework": []}
    # 一人称の重複: 後の人物のS5を1回だけやり直す(差戻しの回数には数えない)
    ov = check_overlaps({s: built[s]["sheet"] for s in SLOTS})
    if ov["first_person_duplicates"]:
        later = [s for s in SLOTS if ov["first_persons"][s] in ov["first_person_duplicates"]][-1]
        avoid = [ov["first_persons"][o] for o in SLOTS if o != later]
        built[later] = build_s5_for(ctx, wf, later, members[later], sh_by, cl_by, others_of(later), avoid_fp=avoid, tag="_fp")
        log["first_person_redo"] = {"slot": later, "avoid": avoid}
    reworks = 0
    used_claims = {members[s]["claim_id"] for s in SLOTS}
    used_stk = {members[s]["stakeholder_id"] for s in SLOTS}
    while reworks < REWORK_LIMIT:
        bad = [s for s in SLOTS if built[s]["naturalness"]["verdict"] != "natural" or built[s]["validation_errors"]]
        if not bad:
            break
        s = bad[0]
        verdict = built[s]["naturalness"]["verdict"] if built[s]["naturalness"]["verdict"] != "natural" else "adjust_claim"
        newm = None
        kind = verdict
        if verdict == "adjust_claim":
            c = next_claim_same_stakeholder(claims, members[s]["stakeholder_id"], used_claims)
            if c:
                newm = {**members[s], "claim_id": c["id"]}
            else:
                kind = "replace_person"
        if kind == "replace_person":
            newm = next_replacement_member(s4, members[s], s, used_stk - {members[s]["stakeholder_id"]}, used_claims, claims)
            if newm:
                newm["assigned_gender"] = SLOT_GENDER[s]
        if newm is None:
            log["rework"].append({"slot": s, "kind": kind, "result": "NO_CANDIDATE"})
            break
        reworks += 1
        used_claims.discard(members[s]["claim_id"])
        used_stk.discard(members[s]["stakeholder_id"])
        members[s] = newm
        used_claims.add(newm["claim_id"])
        used_stk.add(newm["stakeholder_id"])
        built[s] = build_s5_for(ctx, wf, s, members[s], sh_by, cl_by, others_of(s), tag=f"_rw{reworks}")
        log["rework"].append({"slot": s, "kind": kind, "new_stakeholder_id": newm["stakeholder_id"], "new_claim_id": newm["claim_id"],
                              "naturalness": built[s]["naturalness"], "errors": built[s]["validation_errors"]})
    remaining = [s for s in SLOTS if built[s]["naturalness"]["verdict"] != "natural" or built[s]["validation_errors"]]
    ov = check_overlaps({s: built[s]["sheet"] for s in SLOTS})
    reeval_c = None
    if reworks:
        sums = "\n".join(f"- {s}: {sh_by[members[s]['stakeholder_id']]['who_ja']}｜芯: {built[s]['sheet']['claim_core_ja']}" for s in SLOTS)
        r = call_json(ctx, stage="s4_reeval_c", model=MODEL_TOP, effort="medium", developer=S4_DEVELOPER,
                      user=f"差戻しで人物が変わりました。次の3人の組合せ価値(C)と視点の多様性を再評価してください。\n争点: {wf['question_ja']}\n{sums}", schema=SCHEMA_REEVAL_C)
        reeval_c = r["parsed"]
    result = {"members": {s: {k: members[s][k] for k in ("stakeholder_id", "claim_id", "gender_intrinsic")} for s in SLOTS},
              "personas": {s: built[s] for s in SLOTS}, "log": log, "rework_count": reworks, "naturalness_flags_total": sum(1 for s in SLOTS if log["initial"][s]["naturalness"]["verdict"] != "natural"),
              "overlaps": ov, "remaining_unnatural_or_invalid": remaining, "reeval_C": reeval_c}
    if remaining:
        w1.wj(os.path.join(ctx.out_dir, "s5_personas_FAILED.json"), result)
        raise PipelineStop("REWORK_LIMIT_EXCEEDED", f"差戻し{reworks}回後も不自然/検証違反が残る: {remaining}(工程原因をFableへ報告。手作業で直さない)", result)
    return result


# ============================================================
# S6 一人称Voice R0
# ============================================================
VOICE_DEVELOPER = p.VOICE_DEVELOPER

# 旧VOICE_PROMPT_TMPL(er110_family_y_persona_text_trial_01.py:243-267)の複製+改訂。撤去: 規則2(語りの順序)・規則4の『核は1つ…締めで核に戻る』・規則6の『ためらい多くても1か所』・
# 規則8(締めの型)・規則14(他の人の領分)。残置: 規則1・3(身元手がかり、位置は冒頭3文に緩和)・5(具体論)・9〜13(一般化禁止・事実の扱い・数字実在名禁止・役割語禁止・記号禁止)。
VOICE_PROMPT_TMPL = """次の人物「本人」が、ラジオで自分の考えを語る、一人称の語りを1段落だけ書いてください。

テーマ: @@QUESTION@@
【3人に共通の前提(この前提で語る)】
@@PREMISE@@
【区別の定義(取り違えない)】
@@DISTINCTIONS@@

【人物(Persona。本文に全項目を説明しない。背景は言い方・内容・感情に自然に現れればよい)】
@@SHEET@@

【語りの作り方(厳守)】
1. 約260〜300字。話し言葉の常体(「〜だ」「〜なんだ」「〜と思う」「〜だよね」など)。「です・ます」調にしない。新聞・教材のような文章にしない。
2. 冒頭の3文以内に、この人物がどんな人か(仕事・立場・家族など)が聞き手に自然に分かる手がかりを入れる。手がかり: @@CUE@@。「私は〜の者です」「〜をしています」のような自己紹介の文は書かない。
3. 本人として、自由に主観的に語る。調査や事実の説明・言い換えにしない。理屈の正しさより「この人が本当にそう言いそうか」を優先する。複数の本音が混ざってよい。聞き終えた人が「この人は何を言いたいのか」を一言で言えるようにする。語り出しの気持ちは「語り出しの気分」に従い、語りの順序や結び方は決めずに、この人の話し方から自然に決める。
4. 具体論: 人物の経験から1つ、多くても2つだけを選び、出来事を並べ立てず、1つの場面を少し細かく(物・場所・相手の言葉・自分の動き)描く。抽象名詞(責任・価値・判断・根拠・余地・視点・基準など)で言い換えない。1文に抽象名詞は2つまで。
5. 気持ちが動くところがあれば、感情の名前を並べず、言い方・行為・間に出す。
6. 「話し方」(文の長さ・問い返し・断言/留保・語彙)を、実際の文に反映する。自分や聞き手への問いかけの文は、文末を「？」にする。
7. 世の中の出来事の扱い: 人物が書けるのは、本人が見たり聞いたり経験した個別の出来事(「この前」「ある子が」「同僚が」など)だけ。「多くの人が〜」「最近は〜が増えている」のような、頻度・傾向・原因の一般化は、下の「知っている事実」にない限り書かない。人の気持ちや考え方を推測で述べるときは、「〜と思う」「〜気がする」のように本人の推測だと分かる形にする。
8. 事実を使う場合は、本人が主語の伝聞・印象で1文だけ、数字・調査名・年月を使わず、論証の根拠にしない(主張は事実がなくても成立し、事実は補助の一言)。「調査では〜」「〜という結果が出ている」のように、調査・研究・報告が主語の文は書かない。@@FACT@@
9. 数字(算用数字・漢数字の数量表現)を使わない。実在の人名・組織名・製品名・出来事を出さない。Personaにない出来事(誰が何と言った、何があった)を新しく作らない。感覚的な細部の補足は可。
10. 役割語(〜じゃ、〜わよ、〜ぜ等)・方言の演出・擬音・過度な感嘆・泣き笑い・「！」の連発をしない。比喩は多くても1つ。
11. 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。

出力はこの人物の語りの本文のみ(見出し・ラベル・説明なし。1段落)。"""


def render_persona(sheet: dict, who_ja: str) -> str:
    ss = sheet["speech_style"]
    ex = "\n".join(f"  - {e}" for e in sheet["experiences_ja"])
    return (f"人物: {who_ja}(声は{sheet['gender']}の成人。一人称は「{ss['first_person']}」。{sheet['age']}歳)\n役割・生活: {sheet['role_ja']}。{sheet['daily_life_ja']}\n"
            f"この争点との接点: {sheet['contact_point_ja']}\n経験:\n{ex}\n困りごと: {sheet['troubles_ja']}\n本音: {sheet['wishes_honest_ja']} / 建前: {sheet['wishes_public_ja']}\n"
            f"感情の癖: {sheet['emotion_habit_ja']}\n大切にしていること: {sheet['values_ja']}\n利害: {sheet['interests_ja']}\n矛盾・弱さ: {sheet['contradiction_or_weakness_ja']}\n"
            f"話し方(英語にしても残る型):\n  - 文の長さ: {ss['sentence_length_pattern_ja']}\n  - 問い返し: {ss['question_back_frequency_ja']}\n  - 断言/留保: {ss['assertion_or_hedging_ja']}\n"
            f"  - 語彙の層: {ss['vocabulary_layer_ja']}\n語り出しの気分: {sheet['entry_mood_ja']}\nこの人が言いたいことの芯(方向性。そのまま読み上げず、本人の言葉で): {sheet['claim_core_ja']}")


def build_voice_prompt(wf: dict, sheet: dict, who_ja: str, emphasize_entry_mood: bool = False) -> str:
    fact = "知っている事実はない。調査・統計・制度・他の国や組織の動きにはふれない(個人の出来事と感覚だけで語る)。"
    if sheet["known_fact_id"]:
        t = next((x["text_ja"] for x in wf["status_quo"] if x["id"] == sheet["known_fact_id"]), "")
        fact = f"この人が知っていてよい事実は次の1つだけ(補助): {t} 使い方: {sheet['known_fact_usage_ja']}"
    ds = "\n".join(f"- {d['term_ja']}: {d['definition_ja']}" for d in wf.get("distinctions", [])) or "(なし)"
    prompt = (VOICE_PROMPT_TMPL.replace("@@QUESTION@@", wf["question_ja"]).replace("@@PREMISE@@", wf["shared_premise_ja"]).replace("@@DISTINCTIONS@@", ds)
              .replace("@@SHEET@@", render_persona(sheet, who_ja)).replace("@@CUE@@", sheet["identity_cue_ja"]).replace("@@FACT@@", fact))
    if emphasize_entry_mood:
        prompt += (f"\n\n【今回の追加指示】この人の語り出しの気分「{sheet['entry_mood_ja']}」を、語り出し・展開・結びの全体に強く反映する。"
                   "他の人の語りと似た起伏にならないよう、この人の話し方と気分から出てくる流れにする。")
    return prompt


def check_voice_pl(text: str, first_person: str) -> list:
    v = []
    t = (text or "").strip()
    if not t:
        v.append("EMPTY")
    if "\n" in t:
        v.append("MULTI_PARAGRAPH")
    if p.LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    if first_person not in t:
        v.append(f"NO_FIRST_PERSON:{first_person}")
    return v


def voice_monitors_pl(text: str, first_person: str) -> dict:
    sents = [s for s in p.SENT_SPLIT_RE.split(text) if s.strip()]
    lens = [len(s) for s in sents]
    return {"note": "記録専用。合否に使わない", "chars": len(text), "sentences": len(sents), "mean_sentence_chars": round(sum(lens) / max(1, len(lens)), 1),
            "max_sentence_chars": max(lens) if lens else 0, "numbers": p.NUM_RE.findall(text), "exclamations": text.count("！") + text.count("!"),
            "question_marks": text.count("？") + text.count("?"), "role_words": p.ROLE_WORD_RE.findall(text), "interview_expr": p.INTERVIEW_RE.findall(text),
            "self_intro_pattern": bool(re.search(r"(者です|をしています|と申します|ものです)", "".join(sents[:3]))),
            "first_person_count": text.count(first_person), "ends_with_question": bool(re.search(r"[？?]\s*$", text.strip())),
            "last_sentence": sents[-1].strip() if sents else ""}


def generate_voice_pl(ctx: Ctx, wf: dict, slot: str, sheet: dict, who_ja: str, *, emphasize: bool = False, tag: str = "") -> dict:
    """Voice 1本を別callで生成。構造契約/記号QA違反は1回だけ再生成(既存y0/pと同じ)、残ればSTOP。"""
    prompt = build_voice_prompt(wf, sheet, who_ja, emphasize)
    fp = sheet["speech_style"]["first_person"]
    cur, hist, calls = prompt, [], []
    for k in (1, 2):
        raw, meta = call_text(ctx, stage=f"s6_{slot}{tag}" + ("" if k == 1 else "_regen"), model=MODEL_TOP, effort="high", developer=VOICE_DEVELOPER, user=cur)
        calls.append(meta)
        probs = []
        try:
            final, sym = p._fin(raw)
            probs += check_voice_pl(final, fp)
            if safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
            if {t for m in w1.TAG_RE.finditer(raw) for t in w1.tag_ids(m.group(0))}:
                probs.append("UNEXPECTED_FACT_TAG")
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK:{e}"]
        hist.append(probs)
        if not probs:
            return {"slot": slot, "text": final, "raw": raw, "calls": calls, "problems_per_try": hist, "monitors": voice_monitors_pl(final, fp),
                    "prompt_sha256": w1.sha_text(prompt)}
        if k == 1:
            cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {x}" for x in probs)
    raise y0.YStop("VOICE_CONTRACT_STOP", f"{slot}: 再生成後も契約違反 {hist[-1]}", hist)


# ---- 構造タグ監視(OF-Y5-06) ----
STRUCTURE_DEVELOPER = "あなたは、語りの構造を分類する判定者です。各語りの内容の良し悪しは評価せず、与えられたラベル集合から構造の型を選びます。"


def build_structure_prompt(texts: dict) -> str:
    body = "\n\n".join(f"【{s}】\n{texts[s]}" for s in SLOTS)
    return (f"次の3つの語り(それぞれ別の人物の一人称)について、構造の型を分類してください。\n\n{body}\n\n"
            f"opening_type(冒頭の型)の選択肢: {' / '.join(OPENING_TYPES)}\ndevelopment_type(展開の型)の選択肢: {' / '.join(DEVELOPMENT_TYPES)}\n"
            f"closing_type(締めの型)の選択肢: {' / '.join(CLOSING_TYPES)}\nevidence_ja に、各分類の根拠となる冒頭・締めの短い引用を書く。")


def structure_fire(tags: dict) -> dict:
    """OF-Y5-06: 発火条件=『展開の型が一致 かつ 冒頭型か締め型のどちらかが一致』(締め型の違いだけでは『異なる』とみなさない)。
    『その他』同士の一致は一致としない。発火したら、最初の該当ペアの後の方のVoice1本だけを再生成対象にする。"""
    pairs = []
    for a, b in itertools.combinations(SLOTS, 2):
        ta, tb = tags[a], tags[b]

        def same(k):
            return ta[k] == tb[k] and ta[k] != "その他"
        dev, op, cl = same("development_type"), same("opening_type"), same("closing_type")
        if dev and (op or cl):
            pairs.append({"pair": [a, b], "development": dev, "opening": op, "closing": cl})
    return {"fired": bool(pairs), "pairs": pairs, "regenerate_slot": pairs[0]["pair"][1] if pairs else None}


def tag_structure(ctx: Ctx, texts: dict, stage: str) -> dict:
    r = call_json(ctx, stage=stage, model=MODEL_CHEAP, effort="medium", developer=STRUCTURE_DEVELOPER, user=build_structure_prompt(texts), schema=SCHEMA_STRUCTURE)
    tags = {v["voice"]: v for v in r["parsed"]["voices"]}
    if set(tags) != set(SLOTS):
        raise PipelineStop("STRUCTURE_TAG_INCOMPLETE", str(sorted(tags)))
    return {"tags": tags, "fire": structure_fire(tags), "meta": r["meta"]}


# ---- Leakage Gate(既存と同じ構造。判定器p.run_leakは呼出で再利用、rewrite promptのみ題材非依存) ----
def build_voice_rewrite_prompt_pl(texts: dict, flagged: list, wf: dict, personas: dict) -> str:
    blocks = []
    for f in flagged:
        s = f["section"]
        probs = "\n".join(f"  - {x}: {y0.FIELD_MEANING_JA.get(x, x)}" for x in f["fail_fields"])
        blocks.append(f"■ 書き換える語り: {s}\n現在の本文:\n{texts[s]}\n指摘された問題:\n{probs}\n指摘の理由: {f['reasoning']}\n問題の箇所: {f['quoted_evidence']}\n\n【この人物のPersona】\n{personas[s]}")
    others = "\n\n".join(f"[{s}]\n{t}" for s, t in texts.items())
    return f"""次のVoices型記事の、指定した語りだけを書き換えてください。他の語りは読み取り専用です。

【3人に共通の前提】{wf['shared_premise_ja']}

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


TENSION_RULES_PL = """- 語り手(ナレーター)の声。一人称(私・俺・僕・わたし)は使わない。話し言葉の常体。
- 骨格(地の文のひと続きで。「第1に」などのラベルは書かない): (1)3人が共通して望んでいること(1文。抽象語でまとめず、3人の具体的な場面を入れて言う) → (2)3人の違いを、「いつ・どこで困るか」と「何を守りたいか」を、聞き手が覚えている具体物で対比する(3人の主張を順番に要約し直すのではなく、違いの軸として一続きの文にする) → (3)どこが食い違い、どこが重なるか(1〜2文) → (4)締めを1つだけ。
- 締めは、聞き手が自分の生活から答えられる具体的な問いにする(聞き手の暮らしの具体的な場面で答えられる問い)。問いの文末は「？」にする。「責任」「価値」「判断」などの抽象名詞を主語にした問いは書かない。結論・教訓・解決策・勝者の決定はしない。
- 1文は45字以内。1文に抽象名詞(責任・価値・判断・根拠・余地・視点・基準・立場・意味など)は2つまで。二重否定を使わない。哲学的な一般化をしない。
- 新しい事実・数字・出来事を足さない。3人を単純な2対1の陣営に分けない。「取材した」「話を聞いた」など実在の取材者がいるような言い方をしない。
- 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。"""


def build_tension_prompt_pl(voices: dict, wf: dict, objects_hint: str = "") -> str:
    vs = "\n\n".join(f"【人物{i + 1}の語り】\n{voices[s]}" for i, s in enumerate(SLOTS))
    return (f"3人の人物が、次の同じ争点について、それぞれの暮らしから意見を語り終えました。語り手として、最後の1パート(Tension+Closing)を書いてください。\n\n"
            f"【争点】{wf['question_ja']}\n【3人に共通の前提】{wf['shared_premise_ja']}\n\n{vs}\n\n【書き方】\n{TENSION_RULES_PL}\n- 長さ: 約200〜240字、1段落。\n"
            "- 対比に使う具体物は、3人の本文に出てきたものを優先して使う。\n\n出力は最終パートの本文のみ(見出し・ラベルなし)。")


def build_tension_rewrite_prompt_pl(voices: dict, tension: str, flagged: list) -> str:
    f = flagged[0]
    probs = "\n".join(f"  - {x}: {y0.FIELD_MEANING_JA.get(x, x)}" for x in f["fail_fields"])
    vs = "\n\n".join(f"[{s}]\n{t}" for s, t in voices.items())
    return f"""次の最終パート(語り手の声)だけを、指摘された問題を直して書き換えてください。3人の語りは読み取り専用です。

【3人の語り(読み取り専用)】
{vs}

現在の最終パート:
{tension}
指摘された問題:
{probs}
指摘の理由: {f['reasoning']}
問題の箇所: {f['quoted_evidence']}

【書き換えの規則】
{TENSION_RULES_PL}
- 指摘された問題だけを直し、長さ(元の±20%)・話し言葉の常体を保つ。

出力はJSON: {{"section": "tension", "text": 書き換え後の本文}} を1件だけ含む rewrites 配列。"""


def run_gate_pl(ctx: Ctx, *, kind: str, stage: str, texts: dict, out_dir: str, wf: dict, personas_text: dict = None, voices_ctx: dict = None,
                first_persons: dict = None, max_judgements: int = 3) -> dict:
    """Leakage Check(p.run_leak=旧B13項目の判定器、定義不変)-> 局所書き換え -> 再判定(判定最大3回)。残ればLEAKAGE_RESIDUAL_STOP。
    p.run_gateと同じ構造。違いはrewrite promptが題材非依存であることだけ。"""
    os.makedirs(out_dir, exist_ok=True)
    cur = dict(texts)
    history, status = [], None
    pseudo = {s: {"first_person": (first_persons or {}).get(s, "")} for s in SLOTS}
    for attempt in range(1, max_judgements + 1):
        chk = p.run_leak(ctx.client, kind, cur, model=MODEL_CHEAP, effort="high", stage=f"ypl_{stage}_leak{attempt}")
        w1.wj(os.path.join(out_dir, f"leak_check_{attempt}.json"), chk)
        entry = {"attempt": attempt, "sha256": {k: w1.sha_text(v) for k, v in cur.items()}, "check": chk}
        history.append(entry)
        if not chk["any_flagged"]:
            status = "PASS"
            break
        if attempt == max_judgements:
            status = "LEAKAGE_RESIDUAL_STOP"
            break
        keys = {f["section"] for f in chk["flagged_items"]}
        new = None
        for rw_try in (1, 2):
            if kind == "voices":
                prompt = build_voice_rewrite_prompt_pl(cur, chk["flagged_items"], wf, personas_text)
            else:
                prompt = build_tension_rewrite_prompt_pl(voices_ctx, cur["tension"], chk["flagged_items"])
            resp = y0.chat(ctx.client, model=MODEL_TOP, effort="medium", user=prompt, developer=p.REWRITE_DEVELOPER, schema=p.REWRITE_SCHEMA,
                           stage=f"ypl_{stage}_rewrite{attempt}" + ("" if rw_try == 1 else "_retry"))
            rws = json.loads(resp.output_text)["rewrites"]
            new, det = p.apply_rewrites(cur, rws, keys, sheets=pseudo, tension=(kind == "tension"))
            entry.setdefault("rewrite_calls", []).append({"try": rw_try, "meta": y0.resp_meta(resp), "details": det, "raw_rewrites": rws})
            if not det["errors"]:
                break
            new = None
        if new is None:
            w1.wj(os.path.join(out_dir, "gate_result.json"), {"status": "REWRITE_STOP", "history": history})
            raise y0.YStop("REWRITE_STOP", f"{stage}: 局所書き換えの決定論検査に2回失敗", history)
        for k in cur:
            if k not in keys and new[k] != cur[k]:
                raise y0.YStop("REWRITE_BYTE_FIX_VIOLATION", f"{stage}: flag外の{k}が変化")
        entry["rewritten"] = sorted(keys)
        cur = new
    result = {"stage": stage, "kind": kind, "status": status, "n_judgements": len(history), "history": history,
              "first_judgement_flagged": history[0]["check"]["any_flagged"], "first_judgement_n_fail_fields": history[0]["check"]["n_fail_fields"],
              "final_sha256": {k: w1.sha_text(v) for k, v in cur.items()}}
    w1.wj(os.path.join(out_dir, "gate_result.json"), result)
    w1.wj(os.path.join(out_dir, "final_texts.json"), cur)
    result["final_texts"] = cur
    return result


def stage_voices(ctx: Ctx, wf: dict, s5: dict, sh_by: dict, out_dir: str) -> dict:
    """S6: Voice x3(並列)-> 構造タグ(監視。発火なら該当1本だけ1回再生成)-> Leakage Gate。"""
    pers = {s: s5["personas"][s]["sheet"] for s in SLOTS}
    who = {s: sh_by[s5["members"][s]["stakeholder_id"]]["who_ja"] for s in SLOTS}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {s: ex.submit(generate_voice_pl, ctx, wf, s, pers[s], who[s]) for s in SLOTS}
        gen = {s: f.result() for s, f in futs.items()}
    texts = {s: gen[s]["text"] for s in SLOTS}
    tag1 = tag_structure(ctx, texts, "s6_structure1")
    regen = None
    tag2 = None
    if tag1["fire"]["fired"]:
        s = tag1["fire"]["regenerate_slot"]
        g2 = generate_voice_pl(ctx, wf, s, pers[s], who[s], emphasize=True, tag="_structregen")
        regen = {"slot": s, "before": texts[s], "after": g2["text"], "monitors": g2["monitors"]}
        texts[s] = g2["text"]
        gen[s] = g2
        tag2 = tag_structure(ctx, texts, "s6_structure2")      # 記録のみ(2回目の是正はしない)
    personas_text = {s: render_persona(pers[s], who[s]) for s in SLOTS}
    fps = {s: pers[s]["speech_style"]["first_person"] for s in SLOTS}
    gate = run_gate_pl(ctx, kind="voices", stage="voices_gate", texts=texts, out_dir=os.path.join(out_dir, "gate_voices"), wf=wf,
                       personas_text=personas_text, first_persons=fps)
    return {"generated": {s: {k: v for k, v in gen[s].items() if k != "raw"} for s in SLOTS}, "structure_tags_before": tag1, "structure_regen": regen,
            "structure_tags_after": tag2, "gate": {k: v for k, v in gate.items() if k != "history"}, "gate_history_n": gate["n_judgements"],
            "final_voices": gate["final_texts"], "gate_status": gate["status"]}


def stage_tension(ctx: Ctx, wf: dict, voices: dict, out_dir: str) -> dict:
    prompt = build_tension_prompt_pl(voices, wf)
    cur, hist = prompt, []
    final = ""
    for k in (1, 2):
        raw, meta = call_text(ctx, stage="tension" + ("" if k == 1 else "_regen"), model=MODEL_TOP, effort="high", developer=p.TENSION_DEVELOPER, user=cur)
        probs = []
        try:
            final, sym = p._fin(raw)
            probs += p.check_tension(final)["violations"]
            if safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK:{e}"]
        hist.append(probs)
        if not probs:
            break
        cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {x}" for x in probs)
    else:
        raise y0.YStop("TENSION_CONTRACT_STOP", f"tension: 再生成後も契約違反 {hist[-1]}", hist)
    gate = run_gate_pl(ctx, kind="tension", stage="tension_gate", texts={"tension": final}, out_dir=os.path.join(out_dir, "gate_tension"), wf=wf, voices_ctx=voices)
    return {"tension_raw_checked": final, "tension_monitors": p.tension_monitors(gate["final_texts"]["tension"]), "gate_status": gate["status"],
            "n_judgements": gate["n_judgements"], "final_tension": gate["final_texts"]["tension"]}


def load_gate_pass_or_stop(gate_dir: str) -> dict:
    """Acceptance Gate: PASS以外は後続へ流さない(p.load_gated_or_stopを呼出)。"""
    return p.load_gated_or_stop(gate_dir)


# ============================================================
# E1 主張抽出(英語Std。OF-Y5-02。観測のみ・Gateにしない)
# ============================================================
def e1_claims(ctx: Ctx, voices: dict, intended: dict, lang: str, tag: str) -> dict:
    labels = ["X", "Y", "Z"]
    order = list(SLOTS)
    import random
    random.Random(7).shuffle(order)
    blocks = "\n\n".join(f"[{lab}]\n{voices[s]}" for lab, s in zip(labels, order))
    ex = call_json(ctx, stage=f"e1_extract_{tag}", model=MODEL_CHEAP, effort="low", developer="You are a careful reader.",
                   user=f"Below are three first-person monologues from three different people ({lang}). For each, write ONE sentence in English: the single thing the speaker most wants to say. Use only what is in the text.\n\n{blocks}",
                   schema=SCHEMA_E1_EXTRACT)
    by = {x["label"]: x["main_point"] for x in ex["parsed"]["items"]}
    intended_s = "\n".join(f"[{lab}] intended core (Japanese): {intended[s]}\n[{lab}] extracted: {by.get(lab, '')}" for lab, s in zip(labels, order))
    mt = call_json(ctx, stage=f"e1_match_{tag}", model=MODEL_CHEAP, effort="low", developer="You are a careful judge.",
                   user="For each person, judge whether the extracted one-sentence point captures the intended core (MATCH = same main claim; PARTIAL = related but misses or blurs the core; NO = different).\n\n" + intended_s,
                   schema=SCHEMA_E1_MATCH)
    verdict = {}
    for lab, s in zip(labels, order):
        v = next((x for x in mt["parsed"]["items"] if x["label"] == lab), {})
        verdict[s] = {"extracted": by.get(lab), "verdict": v.get("verdict"), "reason": v.get("reason")}
    return {"order": order, "per_voice": verdict, "match_count": sum(1 for v in verdict.values() if v["verdict"] == "MATCH")}


# ============================================================
# 英訳の指示(Y wrapper。題材非依存化。X関数は呼出のみ)
# ============================================================
def y_contrast_must_fix_pl() -> list:
    return [{"fact_id": "", "claim_in_article": "", "issue": "KEEP_SPEAKER_CONTRAST",
             "explanation": ("Paragraphs 1, 2 and 3 are spoken by three different people in the first person, and paragraph 4 is a narrator. "
                             "Keep each speaker's sentence-length contrast, hesitations, questions-back and directness (blunt short sentences versus "
                             "slower flowing ones), and keep who is speaking, even when you simplify the English. "
                             "Do not even out the rhythm across the paragraphs or turn them into a neutral explanation. "
                             "Keep each speaker's concrete objects and workplace or home words rather than abstract wording.")}]


def now_iso() -> str:
    return y0.now_iso()
