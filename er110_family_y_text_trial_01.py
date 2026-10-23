# -*- coding: utf-8 -*-
"""er110_family_y_text_trial_01.py
FAMILY-Y-VOICES-DESIGN-01 委任_04: Family Y(Voices型)統合Trial -- Phase 0〜2 テキスト段階の **DEV/Trial専用** module。

位置づけ(重要):
  - Family Yは未採用(Production採用はユーザー判断待ち)。本moduleは**どのProduction runnerからも参照されない**
    (参照0はtestでGrep固定: test_no_production_reference)。環境変数・flag・CLI引数でProduction挙動が変わる経路もない。
  - Family X/Zの.py・Prompt・閾値・辞書は変更しない。X共有部品(Research/Ledger/B3/注記producer/Fact Lock関数/
    忠実英訳/A2簡易化/Risk Flagger)は**読取り呼出しのみ**(import先は無変更)。Y固有の差分はこのfileに置く。
  - 新しい合格基準・Validatorは追加しない。Leakage Check/Acceptance Gateは旧B承認済み項目の日本語移植、
    決定論モニタ(monitors)は記録専用でGateにしない(S4)。

構成:
  Y-B3(視点候補)→ Voice Card(6〜7項目 + 決定論 not_my_point)→ Y版R0 → X流R1/R2のY版 →
  Leakage Check(日本語)→ 局所書き換え(M5)→ Acceptance Gate → 忠実英訳/A2簡易化(X共有関数)
"""
from __future__ import annotations

import datetime
import json
import os
import re
import time

import er003_audio_tts_asr_safety as safety
import er005_cost_logger as cl
import er019_family_x_ja_writer_o_r1_r2_01 as jaw
import er053_family_x_factlock_ja_writer_01 as w1

MANAGEMENT_ID = "FAMILY-Y-VOICES-DESIGN-01"
THEME_TAG = "FAMILY_Y_TEXT_TRIAL_01"
CHAIN_METHOD = "Y-TRIAL-R0-R1-R2"
MODEL_TOP = "gpt-6.1-sol"          # 25節: 最新世代最上位系(Production Writerと同じ)。本番ラインのモデル選定は別判断
MODEL_CHEAP = "gpt-6-luna"         # 校正データ作成(翻訳)・M7判定器比較のみ。理由は各runtime evidenceに記録

# --- Voice固定(ユーザー決定2026-10-23: 性別・登場順の自動割当は不採用。Family Yの固定仕様) ---
VOICE_SLOTS = ("voice_1", "voice_2", "voice_3")
TTS_VOICE_FIXED = {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"}
VOICE_GENDER = {"voice_1": "男性", "voice_2": "女性", "voice_3": "男性"}   # 声質との整合(人物設計の制約)
PARA_ROLES = ("lead", "voice_1", "voice_2", "voice_3", "final")            # 段落index 0..4
SEGMENT_IDS = tuple(f"full_story_part{i}" for i in range(1, 6))


class YStop(RuntimeError):
    """Y Trialの安全停止(本文を手で直さない)。code=LEAKAGE_RESIDUAL_STOP / CONTRACT_STOP / SYMBOL_STOP / REWRITE_STOP 等。"""

    def __init__(self, code: str, message: str, payload=None):
        super().__init__(f"[STOP] {code}: {message}")
        self.code, self.payload = code, payload


class ProvenanceViolation(RuntimeError):
    pass


_sleep = time.sleep


# ============================================================
# API呼出(単一入口。model不一致はSTOP。cost loggerのstageタグ付き)
# ============================================================
def chat(client, *, model: str, effort: str, user: str, stage: str, developer: str | None = None,
         schema: dict | None = None, retries: int = 2):
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
        except Exception as e:  # noqa: BLE001  一時エラーは最大2回再試行(X call_astraと同方式)
            last = e
            _sleep(3 * (i + 1))
    raise RuntimeError(f"{stage}: API失敗(再試行{retries}回後): {last!r}")


def resp_meta(resp) -> dict:
    u = getattr(resp, "usage", None)
    return {"response_id": getattr(resp, "id", None), "model": getattr(resp, "model", None),
            "usage": {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None)}}


# ============================================================
# 文章の構造(日本語原稿 = タイトル1行 + 本文ちょうど5段落)
# ============================================================
FIRST_PERSON_RE = re.compile(r"(私|わたし|僕|ぼく|俺|おれ|あたし)")
LEAD_BAD_RE = re.compile(r"(取材|話を聞い|聞いてみ|インタビュー|直撃)")
LABEL_START_RE = re.compile(r"^\s*(?:#|【|リード|Voice|ボイス|人物|語り手|[A-Cａ-ｃＡ-Ｃ]さん[:：])")
SENT_SPLIT_RE = re.compile(r"(?<=[。！？!?])")
# Voice段落の数字モニタ(記録専用): 算用数字、または数量を表す漢数字+単位
NUM_RE = re.compile(r"[0-9０-９]+|[〇一二三四五六七八九十百千万]+(?:年|か月|ヶ月|カ月|ケ月|歳|人|回|割|パーセント|円|時間|分間?|日|週間?|台|件|校|度|本|倍)")
DESU_MASU_RE = re.compile(r"(です|ます|でした|ました|でしょう)(?:[。！？]|$|[」])")


def parse_article(text: str) -> dict:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", (text or "").strip()) if b.strip()]
    title = blocks[0] if blocks else ""
    return {"title": title, "paragraphs": blocks[1:]}


def render_article(title: str, paragraphs: list) -> str:
    return title.strip() + "\n\n" + "\n\n".join(p.strip() for p in paragraphs) + "\n"


def check_contract(parsed: dict) -> dict:
    """5段落契約と話者取り違え防止の決定論確認(M2)。違反リストを返す(例外は投げない)。"""
    v = []
    ps = parsed["paragraphs"]
    if not parsed["title"] or "\n" in parsed["title"]:
        v.append("TITLE_BLOCK_INVALID(タイトルが1行でない/空)")
    if len(ps) != 5:
        v.append(f"PARAGRAPH_COUNT={len(ps)}(5段落でない)")
        return {"ok": False, "violations": v}
    for i, p in enumerate(ps):
        if LABEL_START_RE.match(p):
            v.append(f"LABEL_AT_PARAGRAPH_START: 段落{i + 1}")
        if "\n" in p:
            v.append(f"PARAGRAPH_HAS_NEWLINE: 段落{i + 1}")
    for i in (1, 2, 3):
        if not FIRST_PERSON_RE.search(ps[i]):
            v.append(f"VOICE_NO_FIRST_PERSON: 段落{i + 1}({PARA_ROLES[i]})に一人称なし")
    for i in (0, 4):
        if FIRST_PERSON_RE.match(ps[i][:4]):
            v.append(f"NARRATOR_STARTS_WITH_FIRST_PERSON: 段落{i + 1}({PARA_ROLES[i]})")
    return {"ok": not v, "violations": v}


def _bigrams(s: str) -> set:
    s = re.sub(r"[\s、。「」！？,.　]", "", s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def monitors(parsed: dict, tagged_paragraphs: list | None = None) -> dict:
    """決定論モニタ(S4、記録専用・Gateにしない・追加費用0)。"""
    ps = parsed["paragraphs"]
    out = {"note": "記録専用。合否に使わない(S4)", "n_paragraphs": len(ps), "chars_per_paragraph": [len(p) for p in ps],
           "chars_body_total": sum(len(p) for p in ps)}
    if len(ps) == 5:
        out["voice_numbers"] = {PARA_ROLES[i]: NUM_RE.findall(ps[i]) for i in (1, 2, 3)}
        out["first_person_count"] = {PARA_ROLES[i]: len(FIRST_PERSON_RE.findall(ps[i])) for i in (1, 2, 3)}
        fb = _bigrams(ps[4])
        out["final_vs_voice_bigram_overlap"] = {
            PARA_ROLES[i]: round(len(fb & _bigrams(ps[i])) / max(1, len(fb | _bigrams(ps[i]))), 3) for i in (1, 2, 3)}
        out["lead_has_shuzai_expression"] = LEAD_BAD_RE.findall(ps[0])
        out["desu_masu_endings"] = {PARA_ROLES[i]: len(DESU_MASU_RE.findall(ps[i])) for i in range(5)}
        out["sentence_count"] = {PARA_ROLES[i]: len([s for s in SENT_SPLIT_RE.split(ps[i]) if s.strip()]) for i in range(5)}
    if tagged_paragraphs is not None and len(tagged_paragraphs) == 5:
        out["fact_tags_per_paragraph"] = {PARA_ROLES[i]: len(w1.TAG_RE.findall(tagged_paragraphs[i])) for i in range(5)}
    return out


# ============================================================
# Y-B3(視点候補)と Voice Card
# ============================================================
CAST_SCHEMA = {
    "name": "family_y_cast_candidates",
    "strict": True,
    "schema": {
        "type": "object", "additionalProperties": False, "required": ["voices", "common_ground", "independence_note"],
        "properties": {
            "common_ground": {"type": "string"},
            "independence_note": {"type": "string"},
            "voices": {
                "type": "array", "minItems": 3, "maxItems": 3,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["slot", "gender", "age_band", "person_label", "difference_axis", "viewpoint_oneline",
                                 "background_fact_id"],
                    "properties": {
                        "slot": {"type": "string", "enum": list(VOICE_SLOTS)},
                        "gender": {"type": "string", "enum": ["男性", "女性"]},
                        "age_band": {"type": "string", "enum": ["20代", "30代", "40代", "50代", "60代以上"]},
                        "person_label": {"type": "string"},
                        "difference_axis": {"type": "string", "enum": ["経験", "利害", "価値観", "優先順位"]},
                        "viewpoint_oneline": {"type": "string"},
                        "background_fact_id": {"type": ["string", "null"]},
                    },
                },
            },
        },
    },
}

CARD_SCHEMA = {
    "name": "family_y_voice_cards",
    "strict": True,
    "schema": {
        "type": "object", "additionalProperties": False, "required": ["cards"],
        "properties": {
            "cards": {
                "type": "array", "minItems": 3, "maxItems": 3,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["slot", "gender", "person_label", "situation_and_scene", "concern", "stake", "constraint",
                                 "background_fact_ids"],
                    "properties": {
                        "slot": {"type": "string", "enum": list(VOICE_SLOTS)},
                        "gender": {"type": "string", "enum": ["男性", "女性"]},
                        "person_label": {"type": "string"},
                        "situation_and_scene": {"type": "string"},
                        "concern": {"type": "string"},
                        "stake": {"type": "string"},
                        "constraint": {"type": "string"},
                        "background_fact_ids": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        },
    },
}

CAST_DEVELOPER = "あなたは、複数の人物の語りで構成するラジオ読み物の編集者です。人物の設計だけを行い、記事本文は書きません。"


def build_cast_prompt(topic: str, storyline: str, facts: dict) -> str:
    facts_block = "\n".join(f"{fid}: {txt}" for fid, txt in facts.items())
    voice_lines = "\n".join(
        f"- {s}: 再生される声は{VOICE_GENDER[s]}の成人の声(TTS固定割当)。{VOICE_GENDER[s]}の人物にする。" for s in VOICE_SLOTS)
    return f"""次のテーマについて、「同じ問題が、人によってこんなに違って見える」ことを、それぞれ自分の言葉で語る3人の人物の候補を決めてください。記事本文は書かないでください。

テーマ: {topic}
中心となる見方: {storyline}

【材料(確認済みの事実。人物の背景として使えるのは、このF番号の事実だけ)】
{facts_block}

【3人の人物に対する条件】
{voice_lines}
- 3人はそれぞれ別々の生活・仕事・立場を持つ、具体的な一人の人物にしてください。「効率」「規則」のような抽象的な立場の代弁者にしてはいけません。
- 賛成・反対・中立を機械的に1人ずつ割り当てる必要はありません。3人が、経験・利害・価値観・優先順位のうち違う軸で、実質的に別の論点を中心に考える人物にしてください(difference_axisに、その人物を最も特徴づける軸を1つ選ぶ)。
- 3人の中心の論点が意味のうえで重ならないようにしてください。同じ主張を言い換えただけの2人は不可です。
- 声は成人の声で再生されるため、子ども・未成年の本人は避け、20代以上の人物にしてください。
- 性別と役割を安易に結びつけないでください(性別は声の割当で決まっているだけです)。
- 実在の人名・組織名・製品名は使わないでください。person_labelは「中学校で国語を教える教員」のような職業・立場のラベルにします。
- background_fact_idは、その人物が生活の中でふれていそうな事実を上のF番号から最大1つ選びます(なければnull)。3人で同じF番号を使わないでください。
- common_groundには、3人が本当は同じように望んでいること(共通前提)を1文で書きます。
- independence_noteには、3人がなぜ互いに独立した別々の論点を持つのかを1〜2文で書きます。"""


def build_card_prompt(topic: str, cast: dict, facts: dict) -> str:
    lines = []
    for v in cast["voices"]:
        fid = v["background_fact_id"]
        ftxt = facts.get(fid, "") if fid else ""
        lines.append(f"- {v['slot']}: {v['gender']} / {v['age_band']} / {v['person_label']} / 軸={v['difference_axis']} / "
                     f"見方={v['viewpoint_oneline']} / 背景事実={fid or 'なし'} {ftxt}")
    cast_block = "\n".join(lines)
    return f"""次の人物候補から、3人それぞれの「人物カード」を作ってください。記事本文は書かないでください。カードは、後で記事の書き手がその人物の声で一人称の語りを書くための設計メモです。

テーマ: {topic}
共通前提: {cast['common_ground']}

【人物候補】
{cast_block}

【各カードの項目(この7項目だけ)】
- slot, gender, person_label: 候補のとおり(変更しない)。
- situation_and_scene: その人物の具体的な状況と、日常の一場面(今日この人が実際にしていること・目にしていること)を2〜3文で。外側から人物を紹介する書き方ではなく、場面そのものを書く。
- concern: その人物が一番気にかけていること。1文。
- stake: その人物が守りたいもの・賭けているもの。1文。concernと同じ言葉の言い換えにしない。
- constraint: その人物の判断を縛っているもの(時間・立場・責任・気持ちなど)。1文。
- background_fact_ids: 候補の背景事実のF番号を、あればそのまま1件だけ配列で。なければ空配列。

【禁止】
- 数値・統計・制度の名前・他者の具体的な行動の記述をカードに書かない(数字は算用数字も漢数字の数量も使わない)。
- 実在の人名・組織名・製品名・出来事を書かない。
- 3人のconcern同士、stake同士が意味のうえで重ならないこと。
- 賛成・反対の陣営に寄せた書き方をしない(迷いや複雑な気持ちは書いてよい)。"""


def validate_cast(cast: dict, fact_ids: set) -> list:
    errs = []
    voices = cast.get("voices") or []
    if sorted(v.get("slot") for v in voices) != sorted(VOICE_SLOTS):
        errs.append("CAST_SLOTS_MISMATCH")
    used = []
    for v in voices:
        if v.get("gender") != VOICE_GENDER.get(v.get("slot")):
            errs.append(f"CAST_GENDER_MISMATCH:{v.get('slot')}:{v.get('gender')}!={VOICE_GENDER.get(v.get('slot'))}")
        fid = v.get("background_fact_id")
        if fid:
            if fid not in fact_ids:
                errs.append(f"CAST_FACT_UNKNOWN:{fid}")
            used.append(fid)
    if len(used) != len(set(used)):
        errs.append("CAST_FACT_DUPLICATE")
    return errs


def validate_cards(cards_obj: dict, fact_ids: set) -> list:
    """スキーマ水準の決定論整合確認(新Validatorではない): slot/性別/fact id重複なし/concern・stake同一でない/数値欄なし。"""
    errs = []
    cards = cards_obj.get("cards") or []
    if sorted(c.get("slot") for c in cards) != sorted(VOICE_SLOTS):
        errs.append("CARD_SLOTS_MISMATCH")
    used = []
    for c in cards:
        s = c.get("slot")
        if c.get("gender") != VOICE_GENDER.get(s):
            errs.append(f"CARD_GENDER_MISMATCH:{s}")
        ids = c.get("background_fact_ids") or []
        if len(ids) > 1:
            errs.append(f"CARD_FACT_IDS_GT1:{s}")
        for i in ids:
            if i not in fact_ids:
                errs.append(f"CARD_FACT_UNKNOWN:{s}:{i}")
            used.append(i)
        for k in ("situation_and_scene", "concern", "stake", "constraint"):
            if not (c.get(k) or "").strip():
                errs.append(f"CARD_EMPTY:{s}:{k}")
            elif re.search(r"[0-9０-９]", c[k]) or NUM_RE.search(c[k]):
                errs.append(f"CARD_HAS_NUMBER:{s}:{k}")
        if (c.get("concern") or "").strip() == (c.get("stake") or "").strip():
            errs.append(f"CARD_CONCERN_EQ_STAKE:{s}")
    if len(used) != len(set(used)):
        errs.append("CARD_FACT_DUPLICATE")
    concerns = [(c.get("concern") or "").strip() for c in cards]
    if len(set(concerns)) != len(concerns):
        errs.append("CARD_CONCERN_DUPLICATE")
    return errs


def derive_not_my_point(cards_obj: dict) -> dict:
    """S1: not_my_pointはAIに書かせず、他2人のcardのconcernから決定論で生成する。"""
    by = {c["slot"]: c for c in cards_obj["cards"]}
    return {s: [by[o]["concern"] for o in VOICE_SLOTS if o != s] for s in VOICE_SLOTS}


def render_card(card: dict, idx: int, not_my_point: list) -> str:
    fids = card.get("background_fact_ids") or []
    fact_line = ("、".join(f"【事実{re.sub(r'[^0-9]', '', f)}】" for f in fids) + "の範囲でだけ、世界のこと(制度・出来事)に1回までふれてよい(数字は使わない)") if fids else "世界のこと(制度・統計・出来事)にはふれない"
    nmp = "\n".join(f"  - {x}" for x in not_my_point)
    return (f"【人物カード{idx}({idx + 1}段落目)】\n"
            f"性別: {card['gender']}(声も{card['gender']}の成人の声で再生される)\n"
            f"人物: {card['person_label']}\n"
            f"状況と具体的な場面: {card['situation_and_scene']}\n"
            f"一番気にかけていること: {card['concern']}\n"
            f"守りたいもの・賭けているもの: {card['stake']}\n"
            f"判断を縛るもの: {card['constraint']}\n"
            f"世界のこと: {fact_line}\n"
            f"この人物の中心の論点にしないこと(他の2人が中心に抱えている):\n{nmp}")


# ============================================================
# Y版 Writer Prompt(R0 / R1 / R2)
# ============================================================
Y_DEVELOPER_MESSAGE = ("あなたは日本語のラジオ読み物の書き手です。同じ問題を、暮らしも立場も違う3人の人物がそれぞれ自分の言葉で語る"
                       "構成で、聞いて分かりやすく、続きが聞きたくなる文章を書きます。")

Y_R0_HEAD = """以下の材料で、「同じ問題が、人によってこんなに違って見える」ことが伝わる読み物を書いてください。聞き手が「この3人の話、続きが聞きたい」と思うことが目標です。3人は調査結果の説明者ではなく、それぞれ自分の生活の中から、自分の気持ち・判断・迷いを自由に語る一人の人間です。

テーマ：@@STORYLINE@@

【出力の形式(厳守)】
1行目にタイトル、空行1つ、続いて本文ちょうど5段落。段落と段落の間は空行1つ。見出し・番号・ラベル(「リード」「Voice」「Aさん」など)は書きません。本文は次の5段落で、この順序です。
・1段落目 リード(語り手の声、約110字): 具体的な場面か問いから始め、これから3人の声を聞くことを自然に予告します。3人それぞれの結論や立場の詳細は先に言いません。統計・企業名は入れません。結論を先取りしません。「取材した」「話を聞いた」など実在の取材者がいるような言い方はしません(「こんな3人がいる」と置きます)。
・2〜4段落目 人物の語り(各約190字): 人物カード1〜3の順に、その人物本人が一人称「私」で語ります。冒頭の1文で、誰がどんな状況かが分かるようにします(「〜な人は」のように外側から紹介する文では始めず、具体的な場面から始める)。自分の感情・判断・迷いを自分の言葉で語ってください。迷いや複雑な気持ちは書いてかまいません。解決策や提案は語りません。
・5段落目 最終パート(語り手の声、約220字): 次の順序で、地の文のひと続きとして書きます(「第1に」などのラベルは書かない)。(1)共通前提: 3人とも本当は同じことを望んでいる、という出発点。(2)分岐点: なぜ答えが分かれるのかを、何を賭けているかの違いとして示す(3人の発言の再掲や要約はしない)。(3)非対称性: 3人の事情の間にある力関係や重さの違い。この後に、(4)締めを1つだけ置きます。締めは次の3型から1つ選びます(型の名前は書かない): 未決の問いをそっと残す / 具体的な場面に戻る(リードの場面の焼き直しにしない) / 3人の関係を短い一言で言う。要約・勝者の決定・解決策・新しい事実は書きません。3人を単純な2対1の陣営に分けません。

【文体】
全体を、友人に話しかけるような話し言葉の常体(「〜だ」「〜なんだ」「〜と思う」「〜だよね」など)で書きます。「です・ます」調にはしません。新聞・行政資料・学校教材のような文章にはしません。難しい内容は短く簡単な日本語に言い換え、日本語を勉強している外国人が音声で一度聞いて理解できる程度を目安にします。長さは全体で800〜1000字。

【2種類の内容と出典の違い(最重要)】
この文章には、出典の違う2種類の内容があります。
(a) 人物スコープ: 人物本人の状況・気持ち・判断・身の回りのこと。出典は上の「人物カード」だけです。出典タグ(【事実N】)は付けません。ただし、実在の人名・組織名・製品名・出来事は書かず、数値や、他の人の具体的な行動を新しく作りません。カードに書かれていない具体的な経験談(誰が何と言った、何があった)を創作しません。
(b) 世界スコープ: 制度・統計・他者や組織の具体的な行動・出来事。出典は下の[ニュース]欄の事実だけです。下の「出典タグの規則」は、この世界スコープの文にだけ適用します。人物の語り(2〜4段落目)では、世界スコープの文は1段落につき最大1文とし、人物カードの「世界のこと」で許されている事実の範囲に限ります。
人物の語りの段落(2〜4段落目)では、数字(算用数字・漢数字の数量表現)を使いません。リードと最終パートで数字を使う場合は、出典タグの規則に従います。

@@CARDS@@
"""

Y_R0_TAIL = """

【上の出典タグの規則の適用範囲(再掲)】
出典タグの規則は「世界スコープ」の文だけに適用します。人物スコープの文(人物カードに基づく本人の状況・気持ち・判断)には、タグを付けず、「ニュース欄にないことは書かない」という規則も適用しません(カードの範囲で書いてください)。ただし人物の語りの中でも、ニュース欄やカードにない具体的な事実(数値、制度、他の人の行動、出来事)を新しく断定してはいけません。

出力はタイトルと本文のみ。
"""

# R1/R2: XのUSER_TMPL(w1.USER_TMPL)の逐語 + Voice文脈向けの追加1段落のみ(差分はUSER_TMPL_Y_ADDITION。X Promptは無変更)
USER_TMPL_Y_ADDITION = ("\n\n構成は変えないでください。本文はちょうど5段落で、1段落目は語り手のリード、2〜4段落目は3人の人物がそれぞれ「私」で語る段落、"
                        "5段落目は語り手の最終段落です。段落の統合・分割・追加・削除・順序変更をしないでください。各人物の立場・一人称・話し言葉の常体・"
                        "迷いの表現は保ってください。")
USER_TMPL_Y = w1.USER_TMPL + USER_TMPL_Y_ADDITION


def build_y_r0_prompt(storyline: str, news_text: str, cards_obj: dict, rounding_overlay=None) -> str:
    import er095_b3_core_number_rounding_01 as rounding
    nmp = derive_not_my_point(cards_obj)
    by = {c["slot"]: c for c in cards_obj["cards"]}
    cards_block = "\n\n".join(render_card(by[s], i + 1, nmp[s]) for i, s in enumerate(VOICE_SLOTS))
    head = Y_R0_HEAD.replace("@@STORYLINE@@", storyline).replace("@@CARDS@@", cards_block)
    prompt = head + "\n[ニュース]\n" + news_text
    prompt += jaw.SYMBOL_PREVENTION_BLOCK_JA
    prompt += w1.build_r0_block(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)
    prompt += Y_R0_TAIL
    return rounding.apply_rule8(prompt, rounding_overlay)


# 対策弱化アーム(A0)用: 比較評価専用。Y版R0の安全装置(数字禁止・not_my_point・世界スコープ規則・Fact Lock)を外した最小Prompt。
def build_y_r0_light_prompt(storyline: str, news_text: str, cards_obj: dict) -> str:
    by = {c["slot"]: c for c in cards_obj["cards"]}
    blocks = []
    for i, s in enumerate(VOICE_SLOTS):
        c = by[s]
        blocks.append(f"【人物{i + 1}】{c['gender']}。{c['person_label']}。\n状況: {c['situation_and_scene']}\n気にかけていること: {c['concern']}\n守りたいもの: {c['stake']}\n縛るもの: {c['constraint']}")
    return (f"以下の3人の人物をもとに、「同じ問題が、人によってこんなに違って見える」ことが伝わる読み物を書いてください。\n\nテーマ：{storyline}\n\n"
            "出力は、1行目にタイトル、空行1つ、続いて本文ちょうど5段落(段落の間は空行1つ)。1段落目は語り手の導入、2〜4段落目は人物1〜3がそれぞれ「私」で語る段落、"
            "5段落目は語り手の最後のまとめです。人物は、自分の気持ち・意見・判断を、その人の言葉で自由に語ってください。話し言葉の常体で、全体で800〜1000字。\n\n"
            + "\n\n".join(blocks) + "\n\n[参考のニュース]\n" + news_text + jaw.SYMBOL_PREVENTION_BLOCK_JA + "\n出力はタイトルと本文のみ。\n")


# ============================================================
# Leakage Check(旧B承認済み項目の日本語移植。Voice 7項目 / 最終パート=旧Tension 6項目)
# ============================================================
VOICE_LEAKAGE_FIELDS = ("leak_evidence_subject", "leak_numbers_foreground", "leak_narrator_analysis",
                        "leak_unknowable_analysis", "leak_discovery_syntax", "leak_evidence_memorable", "leak_position_blur")
TENSION_LEAKAGE_FIELDS = ("leak_evidence_subject", "leak_numbers_foreground", "leak_discovery_syntax",
                          "leak_evidence_memorable", "leak_tension_reverts_to_research", "leak_binary_camp_split")
LEAK_SECTIONS = {"voice_1": VOICE_LEAKAGE_FIELDS, "voice_2": VOICE_LEAKAGE_FIELDS, "voice_3": VOICE_LEAKAGE_FIELDS,
                 "tension": TENSION_LEAKAGE_FIELDS}
LEAK_PARA_INDEX = {"voice_1": 1, "voice_2": 2, "voice_3": 3, "tension": 4}

LEAKAGE_DEVELOPER_JA = (
    "あなたは「Voices(複数の人物がそれぞれ自分の言葉で語る)」型記事のVoiceセクションとTensionセクションを審査する、"
    "厳格なEditorial QA判定者です。それぞれのセクションが、実在しうる当事者(人)の経験・価値観・必要・心配として書かれているか、"
    "あるいは調査結果・データを整理して説明する文章、語り手の外側からの要約、Writer自身の解決策提案、単純な2対1分割に戻っていないかを、"
    "各セクション指定の基準についてPASS/FAILで判定してください。各基準についてPASSは『問題なし』、FAILは『その問題が実際に本文に存在する』"
    "ことを意味します。FAILの場合は、該当する原文の一節をquoted_evidenceにそのまま引用してください(複数箇所ある場合は代表的な1〜2箇所)。"
    "PASSの場合はquoted_evidenceを空文字列にしてください。")


def leakage_schema() -> dict:
    def item(fields):
        props = {f: {"type": "string", "enum": ["PASS", "FAIL"]} for f in fields}
        props["reasoning"] = {"type": "string"}
        props["quoted_evidence"] = {"type": "string"}
        return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}
    return {"name": "family_y_leakage_check_ja", "strict": True,
            "schema": {"type": "object", "properties": {k: item(v) for k, v in LEAK_SECTIONS.items()},
                       "required": list(LEAK_SECTIONS), "additionalProperties": False}}


def build_leakage_prompt(sections: dict, language_note: str = "日本語") -> str:
    return f"""以下は、ある Voices型記事(3人の人物がそれぞれ一人称で語る)の4つのセクション本文(Voice 1〜3/最終パート[Tension])です(本文の言語: {language_note})。それぞれについて、指定された項目を判定してください(それぞれPASS/FAIL)。

【Voice 1〜3に共通で適用する7項目】
- leak_evidence_subject: 文の主語が、調査・研究・データ・割合・報告になっている文が無い場合PASS
- leak_numbers_foreground: 具体的な数字が、その人物自身の経験に属する数値であり、かつその人の経験の描写より前面に出ていない場合PASS(数字が0個、またはその人物自身の経験に属する数字が1個だけ実感として自然に織り込まれている場合はPASS。調査・報告・研究等、本人の経験に属さない外部統計をVoice内で論証材料として使っている場合はFAIL)
- leak_narrator_analysis: 語り手が、Voiceの人物を外側から分析・要約していない場合PASS
- leak_unknowable_analysis: その人物自身が実際に考え・言いそうにない、外部の分析的視点を、その人のPerspectiveとして書いていない場合PASS
- leak_discovery_syntax: 「〜が明らかになった」「〜という傾向がある」のような、発見・傾向を報じる記事の文構造へ戻っていない場合PASS
- leak_evidence_memorable: 調査や事実よりも、その人物の経験・感情の方が記憶に残る書き方になっている場合PASS
- leak_position_blur: このVoiceが、自分の立場の中の迷い・葛藤(nuance)の範囲を超えて、他のVoice(相手側)が中心的に抱えている懸念・反論そのものを、自分の中心的な主張として代弁していない場合PASS(相手側の中心論点をこのVoiceが実質的に引き受けてしまっている場合はFAIL)

いずれのVoiceについても、他のVoiceと同一の基準で判定してください(特定の立場が抽象的な代弁者の解説になっている場合は、leak_evidence_subject/leak_narrator_analysis/leak_discovery_syntaxのいずれかでFAILとしてください)。

【最終パート(Tension)に適用する6項目】
- leak_evidence_subject / leak_discovery_syntax / leak_evidence_memorable: 上記と同じ意味(最終パート本文に対して判定)
- leak_numbers_foreground(最終パート用): 具体的な数字・比較結果が、3人の合理性を制約する力の描写より前面に出ていない場合PASS(1人の経験ではなく複数人の力関係を扱うため、Voice用の「本人の経験に属する数値」限定はここでは適用しない)
- leak_tension_reverts_to_research: 最終パートの中心が、3人がなぜ違う答えに至るのかの掘り下げになっており、調査・研究データそのものの説明・比較へ戻っていない場合PASS
- leak_binary_camp_split: 最終パートが3人を単純に対称的な2対1の陣営へ分けて描いていない場合PASS(分けている場合FAIL)

reasoningには、判定理由を1〜2文の日本語で書いてください。FAILの場合はquoted_evidenceに該当する原文を引用してください。PASSの場合quoted_evidenceは空文字列にしてください。

【Voice 1本文】
{sections['voice_1']}

【Voice 2本文】
{sections['voice_2']}

【Voice 3本文】
{sections['voice_3']}

【最終パート(Tension)本文】
{sections['tension']}
"""


def sections_from_paragraphs(paragraphs: list) -> dict:
    return {"voice_1": paragraphs[1], "voice_2": paragraphs[2], "voice_3": paragraphs[3], "tension": paragraphs[4]}


def run_leakage_check(client, sections: dict, *, model: str, effort: str, stage: str, language_note: str = "日本語") -> dict:
    prompt = build_leakage_prompt(sections, language_note)
    resp = chat(client, model=model, effort=effort, user=prompt, developer=LEAKAGE_DEVELOPER_JA, schema=leakage_schema(), stage=stage)
    text = getattr(resp, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Leakage Check応答が空")
    parsed = json.loads(text)
    flagged = []
    for sec, fields in LEAK_SECTIONS.items():
        it = parsed[sec]
        fails = [f for f in fields if it[f] == "FAIL"]
        if fails:
            flagged.append({"section": sec, "paragraph_index": LEAK_PARA_INDEX[sec], "fail_fields": fails,
                            "reasoning": it["reasoning"], "quoted_evidence": it["quoted_evidence"]})
    return {"model": model, "effort": effort, "meta": resp_meta(resp), "prompt_sha256": w1.sha_text(prompt), "parsed": parsed,
            "flagged_items": flagged, "any_flagged": bool(flagged),
            "fail_field_counts": {f: sum(1 for x in flagged if f in x["fail_fields"]) for f in
                                  sorted({f for x in flagged for f in x["fail_fields"]})},
            "n_fail_fields": sum(len(x["fail_fields"]) for x in flagged)}


# ============================================================
# 局所書き換え(M5)
# ============================================================
REWRITE_SCHEMA = {
    "name": "family_y_local_rewrite", "strict": True,
    "schema": {"type": "object", "additionalProperties": False, "required": ["rewrites"],
               "properties": {"rewrites": {"type": "array", "items": {
                   "type": "object", "additionalProperties": False, "required": ["paragraph_index", "text"],
                   "properties": {"paragraph_index": {"type": "integer"}, "text": {"type": "string"}}}}}},
}

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


def build_rewrite_prompt(paragraphs: list, title: str, flagged: list, cards_obj: dict, *, facts_text: str | None, r0_tags: bool) -> str:
    by = {c["slot"]: c for c in cards_obj["cards"]}
    nmp = derive_not_my_point(cards_obj)
    blocks = []
    for f in flagged:
        i = f["paragraph_index"]
        role = PARA_ROLES[i]
        probs = "\n".join(f"  - {x}: {FIELD_MEANING_JA.get(x, x)}" for x in f["fail_fields"])
        card = ""
        if role in by:
            card = "\n" + render_card(by[role], VOICE_SLOTS.index(role) + 1, nmp[role])
        blocks.append(f"■ 書き換える段落: {i + 1}段落目({'最終パート(語り手)' if role == 'final' else '人物の語り' })\n"
                      f"現在の本文:\n{paragraphs[i]}\n指摘された問題:\n{probs}\n指摘の理由: {f['reasoning']}\n問題の箇所: {f['quoted_evidence']}{card}")
    full = "\n\n".join(f"[{i + 1}段落目]\n{p}" for i, p in enumerate(paragraphs))
    tag_rule = ""
    if r0_tags and facts_text:
        tag_rule = ("\n- 世界のこと(制度・出来事・他者や組織の行動)を述べる文には、文末の句点の直後に【事実N】を付けてください(Nは下のニュース欄の番号だけ)。"
                    "人物本人の状況・気持ち・判断の文にはタグを付けません。\n\n[ニュース]\n" + facts_text)
    return f"""次の記事(タイトル: {title})の、指定した段落だけを書き換えてください。他の段落は読み取り専用です。

【記事全体(文脈。読み取り専用)】
{full}

{chr(10).join(blocks)}

【書き換えの規則】
- 指摘された問題だけを直し、その段落の役割(誰が話すか・何を語るか)・長さ(元の段落の±20%)・話し言葉の常体・一人称を保つ。
- 人物の語りの段落は、その人物本人が「私」で語り、冒頭の1文で誰がどんな状況か分かる。数字(算用数字・漢数字の数量表現)を使わない。調査・統計・制度の説明をしない。他の人物の中心の論点を自分の中心の主張にしない。迷いや複雑な気持ちは残してよい。解決策・提案は語らない。
- 最終パートは「共通前提→分岐点(何を賭けているかの違い)→非対称性→締め1つ」。各人物の再要約・時系列の反復・解決策・新しい事実を書かない。
- 実在の人名・組織名・製品名を新しく出さない。カードにない具体的な経験談・数値・他者の行動を創作しない。
- 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。{tag_rule}

出力はJSON: 書き換えた段落ごとに {{"paragraph_index": 段落番号(1始まり), "text": 書き換え後の段落本文}}。指定した段落以外は出力しない。"""


def apply_local_rewrite(paragraphs: list, rewrites: list, flagged_indices: set, *, allow_tags: bool, valid_fact_nums: set | None = None) -> tuple:
    """書き換え結果の差込は**決定論**。flag段落以外はbyte固定。書き換え後の文章に決定論検査(Fact Lockタグ・clean_ja_for_next・
    postprocess_ja・記号QA)を通す。戻り値=(new_paragraphs, details)。検査失敗は details['errors']。"""
    new = list(paragraphs)
    errors, applied = [], []
    got = set()
    for r in rewrites:
        idx = int(r["paragraph_index"]) - 1
        got.add(idx)
        if idx not in flagged_indices:
            errors.append(f"REWRITE_OUT_OF_SCOPE:段落{idx + 1}")
            continue
        raw = r["text"] or ""
        if allow_tags and valid_fact_nums is not None:
            used = {int(n) for m in w1.TAG_RE.finditer(raw) for n in re.findall(r"\d+", m.group(0))}
            if used - valid_fact_nums:
                errors.append(f"REWRITE_UNKNOWN_FACT_TAG:段落{idx + 1}:{sorted(used - valid_fact_nums)}")
        try:
            clean = w1.clean_ja_for_next(raw)
        except w1.TagLeak as e:
            errors.append(f"REWRITE_TAG_LEAK:段落{idx + 1}:{e}")
            continue
        post = w1.postprocess_ja(clean).strip()
        if "\n" in post or not post:
            errors.append(f"REWRITE_NOT_SINGLE_PARAGRAPH:段落{idx + 1}")
            continue
        sym = safety.detect_prohibited_symbols(post, language="ja")
        if safety.symbol_gate_requires_stop(sym):
            errors.append(f"REWRITE_SYMBOL:段落{idx + 1}:{sym}")
            continue
        new[idx] = post
        applied.append(idx + 1)
    if got != flagged_indices:
        errors.append(f"REWRITE_INDEX_SET_MISMATCH: got={sorted(i + 1 for i in got)} expected={sorted(i + 1 for i in flagged_indices)}")
    return new, {"applied_paragraphs": applied, "errors": errors}


def run_gate(client, *, stage: str, title: str, paragraphs: list, cards_obj: dict, out_dir: str, judge_model: str, judge_effort: str,
             rewrite_model: str = MODEL_TOP, rewrite_effort: str = "medium", r0_tags: bool = False, facts_text: str | None = None,
             valid_fact_nums: set | None = None, max_judgements: int = 3) -> dict:
    """Leakage Check → 局所書き換え → 全文再判定(判定最大3回=初回+書き換え2回)→ 残存はLEAKAGE_RESIDUAL_STOP(全文書き直しへ戻さない)。
    Acceptance Gate: status != PASS の原稿は後続へ流さない(呼出側で final_paragraphs を使うのはPASSのみ)。"""
    os.makedirs(out_dir, exist_ok=True)
    history, cur = [], list(paragraphs)
    status = None
    prev_flag_by_para = None
    for attempt in range(1, max_judgements + 1):
        check = run_leakage_check(client, sections_from_paragraphs(cur), model=judge_model, effort=judge_effort,
                                  stage=f"{stage}_leak{attempt}")
        flagged_paras = {f["paragraph_index"] for f in check["flagged_items"]}
        noise = None
        if prev_flag_by_para is not None:
            # 判定ノイズ記録(M5-d): 書き換えていない段落で、前回PASS→今回FAIL(またはその逆)になったもの
            rewritten = set(history[-1].get("rewritten_paragraphs") or [])
            noise = sorted(i + 1 for i in range(1, 5) if (i + 1) not in rewritten and ((i in prev_flag_by_para) != (i in flagged_paras)))
        entry = {"attempt": attempt, "article_sha256": w1.sha_text(render_article(title, cur)), "check": check,
                 "judgement_noise_unchanged_paragraphs": noise}
        w1.wt(os.path.join(out_dir, f"article_before_judgement{attempt}.md"), render_article(title, cur))
        w1.wj(os.path.join(out_dir, f"leak_check_{attempt}.json"), check)
        history.append(entry)
        prev_flag_by_para = flagged_paras
        if not check["any_flagged"]:
            status = "PASS"
            break
        if attempt == max_judgements:
            status = "LEAKAGE_RESIDUAL_STOP"
            break
        idxs = {f["paragraph_index"] for f in check["flagged_items"]}
        prompt = build_rewrite_prompt(cur, title, check["flagged_items"], cards_obj, facts_text=facts_text, r0_tags=r0_tags)
        new = None
        for rw_try in (1, 2):    # 決定論検査失敗時のみ1回再生成(Xの記号QA再生成と同方式)。判定回数には数えない
            resp = chat(client, model=rewrite_model, effort=rewrite_effort, user=prompt, developer=REWRITE_DEVELOPER, schema=REWRITE_SCHEMA,
                        stage=f"{stage}_rewrite{attempt}" + ("" if rw_try == 1 else "_retry"))
            rws = json.loads(resp.output_text)["rewrites"]
            new, det = apply_local_rewrite(cur, rws, idxs, allow_tags=r0_tags, valid_fact_nums=valid_fact_nums)
            entry.setdefault("rewrite_calls", []).append({"try": rw_try, "meta": resp_meta(resp), "details": det,
                                                          "raw_rewrites": rws})
            if not det["errors"]:
                break
            new = None
        if new is None:
            entry["rewritten_paragraphs"] = []
            status = "REWRITE_STOP"
            w1.wj(os.path.join(out_dir, "gate_result.json"), {"status": status, "history": history})
            raise YStop("REWRITE_STOP", f"{stage}: 局所書き換えの決定論検査に2回失敗(全文書き直しへは戻さない)", history)
        # byte固定の確認: flag段落以外は無変更
        for i in range(5):
            if i not in {j for j in idxs} and new[i] != cur[i]:
                raise YStop("REWRITE_BYTE_FIX_VIOLATION", f"{stage}: flag外の段落{i + 1}が変化")
        entry["rewritten_paragraphs"] = sorted(i + 1 for i in idxs)
        # 一人称保持の確認(S6)
        entry["first_person_kept_after_rewrite"] = {f"段落{i + 1}": bool(FIRST_PERSON_RE.search(new[i])) for i in idxs if i in (1, 2, 3)}
        w1.wt(os.path.join(out_dir, f"article_after_rewrite{attempt}.md"), render_article(title, new))
        cur = new
        c = check_contract({"title": title, "paragraphs": cur})
        if not c["ok"]:
            raise YStop("CONTRACT_STOP", f"{stage}: 書き換え後に5段落契約違反 {c['violations']}", history)
    result = {"stage": stage, "status": status, "n_judgements": len(history), "history": history,
              "final_article_sha256": w1.sha_text(render_article(title, cur)),
              "first_judgement_flagged": history[0]["check"]["any_flagged"],
              "first_judgement_fail_field_counts": history[0]["check"]["fail_field_counts"],
              "first_judgement_n_fail_fields": history[0]["check"]["n_fail_fields"]}
    w1.wj(os.path.join(out_dir, "gate_result.json"), result)
    w1.wt(os.path.join(out_dir, "article_final.md"), render_article(title, cur))
    result["final_paragraphs"] = cur
    return result


# ============================================================
# Writer(R0 / R1 / R2、raw chain)
# ============================================================
def _finalize_ja(raw: str) -> tuple:
    """タグ除去(単一経路)→ postprocess_ja → 記号QA。戻り値=(final_text, symbol_findings)。"""
    clean = w1.clean_ja_for_next(raw)
    final = w1.postprocess_ja(clean).strip() + "\n"
    return final, safety.detect_prohibited_symbols(final, language="ja")


def _stage_problems(final: str, symbol_findings: list) -> list:
    probs = []
    c = check_contract(parse_article(final))
    probs += c["violations"]
    if safety.symbol_gate_requires_stop(symbol_findings):
        probs.append(f"SYMBOL: {symbol_findings}")
    return probs


def generate_r0(client, *, prompt: str, out_dir: str, model: str = MODEL_TOP) -> dict:
    """R0単発(effort=high)。契約違反(5段落/話者)または記号QA違反は**1回だけ**再生成、残ればSTOP。"""
    os.makedirs(out_dir, exist_ok=True)
    calls, probs_hist = [], []
    cur_prompt = prompt
    for k in (1, 2):
        resp = chat(client, model=model, effort="high", user=cur_prompt, developer=Y_DEVELOPER_MESSAGE, stage="y_r0" + ("" if k == 1 else "_regen"))
        raw = resp.output_text.strip()
        calls.append({**resp_meta(resp), "prompt_sha256": w1.sha_text(cur_prompt)})
        w1.wt(os.path.join(out_dir, f"r0_with_tags_try{k}.md"), raw)
        try:
            final, sym = _finalize_ja(raw)
            probs = _stage_problems(final, sym)
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK: {e}"]
        probs_hist.append(probs)
        if not probs:
            tagged = [b.strip() for b in re.split(r"\n\s*\n", raw) if b.strip()][1:]
            w1.wt(os.path.join(out_dir, "r0_with_tags.md"), raw + "\n")
            w1.wt(os.path.join(out_dir, "r0_final.md"), final)
            tags_used = sorted({t for m in w1.TAG_RE.finditer(raw) for t in w1.tag_ids(m.group(0))})
            ev = {"calls": calls, "problems_per_try": probs_hist, "tags_used": tags_used, "tagged_paragraphs": tagged,
                  "r0_sha256": w1.sha_text(final)}
            w1.wj(os.path.join(out_dir, "r0_meta.json"), ev)
            return {"final": final, "raw": raw, "tagged_paragraphs": tagged, "meta": ev}
        if k == 1:
            note = "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {p}" for p in probs)
            cur_prompt = prompt + note
    w1.wt(os.path.join(out_dir, "rejected_r0.md"), raw)
    raise YStop("CONTRACT_STOP" if not any(p.startswith("SYMBOL") for p in probs_hist[-1]) else "SYMBOL_STOP",
                f"R0: 再生成後も問題が残りました {probs_hist[-1]}", probs_hist)


def generate_revision(client, *, src_text: str, stage: str, out_dir: str, model: str = MODEL_TOP) -> dict:
    """R1/R2(effort=high、入力=前段の出力のみ)。X流のUSER_TMPL + Y追加1段落。問題があれば同一入力で1回だけ再実行、残ればSTOP。"""
    user = USER_TMPL_Y.format(body=src_text.strip())
    calls, hist = [], []
    for k in (1, 2):
        resp = chat(client, model=model, effort="high", user=user, stage=f"y_{stage}" + ("" if k == 1 else "_rerun"))
        raw = (resp.output_text or "").strip()
        calls.append({**resp_meta(resp), "user_sha256": w1.sha_text(user)})
        w1.wt(os.path.join(out_dir, f"{stage}_raw_try{k}.md"), raw)
        try:
            final, sym = _finalize_ja(raw)
            probs = _stage_problems(final, sym)
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK: {e}"]
        hist.append(probs)
        if not probs:
            w1.wt(os.path.join(out_dir, f"{stage}_final.md"), final)
            w1.wj(os.path.join(out_dir, f"{stage}_meta.json"), {"calls": calls, "problems_per_try": hist, "sha256": w1.sha_text(final)})
            return {"final": final, "raw": raw, "calls": calls}
    raise YStop("CONTRACT_STOP", f"{stage}: 同一入力の再実行後も問題が残りました {hist[-1]}", hist)


# ============================================================
# 英語段階(Phase 2)の決定論確認(M2)と一人称保持率
# ============================================================
EN_FIRST_PERSON_RE = re.compile(r"\b(I|I'm|I've|I'd|I'll|my|me|mine|myself)\b")
EN_NUM_RE = re.compile(r"\b\d[\d,\.]*\b|\b(one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty|forty|fifty|hundred|thousand|percent|half)\b", re.I)


def split_en_article(text: str) -> dict:
    """英語記事(# Title / 本文段落 / ## In one line)を分解。"""
    t = (text or "").strip()
    m = re.match(r"^#\s+(.+?)\s*\n+(.*)$", t, re.S)
    title, rest = (m.group(1), m.group(2)) if m else ("", t)
    iol = ""
    mm = re.search(r"\n##\s*In one line\s*\n(.*)$", "\n" + rest, re.S | re.I)
    if mm:
        iol = mm.group(1).strip()
        rest = ("\n" + rest)[: mm.start()].strip()
    paras = [b.strip() for b in re.split(r"\n\s*\n", rest) if b.strip()]
    return {"title": title, "paragraphs": paras, "in_one_line": iol}


def check_en_contract(text: str) -> dict:
    s = split_en_article(text)
    ps, v = s["paragraphs"], []
    if not s["title"]:
        v.append("EN_NO_TITLE")
    if len(ps) != 5:
        v.append(f"EN_PARAGRAPH_COUNT={len(ps)}")
        return {"ok": False, "violations": v, "split": s}
    if not s["in_one_line"]:
        v.append("EN_NO_IN_ONE_LINE")
    for i in (1, 2, 3):
        if not EN_FIRST_PERSON_RE.search(ps[i]):
            v.append(f"EN_VOICE_NO_FIRST_PERSON: paragraph {i + 1}")
    for i in (0, 4):
        if re.match(r"^(I|I'm|I've|My|Me)\b", ps[i]):
            v.append(f"EN_NARRATOR_STARTS_WITH_FIRST_PERSON: paragraph {i + 1}")
    return {"ok": not v, "violations": v, "split": s}


def en_monitors(text: str) -> dict:
    s = split_en_article(text)
    ps = s["paragraphs"]
    out = {"note": "記録専用(S3/S4)", "n_paragraphs": len(ps), "words_per_paragraph": [len(p.split()) for p in ps],
           "words_total_body": sum(len(p.split()) for p in ps), "in_one_line_words": len(s["in_one_line"].split())}
    if len(ps) == 5:
        out["first_person_tokens"] = {PARA_ROLES[i]: len(EN_FIRST_PERSON_RE.findall(ps[i])) for i in range(5)}
        out["first_person_per_sentence_voice"] = {
            PARA_ROLES[i]: round(len(EN_FIRST_PERSON_RE.findall(ps[i])) / max(1, len(re.findall(r"[.!?](?:\s|$)", ps[i]))), 2) for i in (1, 2, 3)}
        out["voice_number_tokens"] = {PARA_ROLES[i]: [m.group(0) for m in EN_NUM_RE.finditer(ps[i])] for i in (1, 2, 3)}
    return out


# ============================================================
# 学習支援構造のY用role(Comment 1〜3。Comment 4は生成しない=ユーザー決定)。Xのrole定数は無変更。
#   Comment 1 = Xの COMMENT_1_ROLE を**そのまま**使う(呼出側で参照)。Comment 2/3 はY用に新規(「第1部・第2部」前提文言を除去)。
# ============================================================
_LABEL_BAN = ("【重要・出力への制約】出力する文章自体に\"Part 1\"・\"Part 2\"・\"Full Story\"のような\n"
              "制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を意識しません。")
_C2_COMMON = ("役割: 導入で聞いた問いの核心を1点だけ短く回収し、これから3人の違う人物が語ることを予告します。"
              "3人の立場や結論を先に言ってはいけません。新しいFactを追加しないでください。")
_C3_COMMON = ("役割: 3人の語りを聞いたうえで、「なぜ同じ問題が、それぞれにこんなに違って見えるのか」へ聞き手の視点を移します。"
              "誰が正しいかを言わず、結論を先に言ってはいけません。3人の発言を再要約しないでください。新しいFactを追加しないでください。")
Y_COMMENT_2_ROLE = {
    "b1b": ("あなたはPodcastのナビゲーターです。リスナーは導入部分(リード)をすでに聞き終わり、これから3人の人物が順番に自分の言葉で語るのを聞きます。"
            "その間に流す、Comment 2(役割: Lead Recovery + Bridge to the Three Voices)を書いてください。\n\n"
            + _C2_COMMON + "1〜2文にしてください。\n\n" + _LABEL_BAN),
    "a2": ("あなたはPodcastのナビゲーターです。リスナーは導入部分(リード)をすでに聞き終わり、これから3人の人物が順番に自分の言葉で語るのを聞きます。"
           "その間に流す、Comment 2(役割: Lead Recovery + Bridge to the Three Voices)を日本語で書いてください。\n\n"
           + _C2_COMMON + "易しい日本語で1〜2文にしてください。\n\n" + _LABEL_BAN),
}
Y_COMMENT_3_ROLE = {
    "b1b": ("あなたはPodcastのナビゲーターです。リスナーは3人の人物の語りをすべて聞き終わり、これから語り手のまとめの段落を聞きます。"
            "その間に流す、Comment 3(役割: Shift to Why They Differ)を書いてください。\n\n"
            + _C3_COMMON + "易しい英語で2〜3文にしてください。\n\n" + _LABEL_BAN),
    "a2": ("あなたはPodcastのナビゲーターです。リスナーは3人の人物の語りをすべて聞き終わり、これから語り手のまとめの段落を聞きます。"
           "その間に流す、Comment 3(役割: Shift to Why They Differ)を日本語で書いてください。\n\n"
           + _C3_COMMON + "易しい日本語で2〜3文にしてください。\n\n" + _LABEL_BAN),
}


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
