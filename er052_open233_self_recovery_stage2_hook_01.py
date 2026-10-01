# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_stage2_hook_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, 委任_17)
# ============================================================
# 目的: 委任_16 B-2で「Title/Hook演出許容原則」を既存Stage2 rubric
# (RUBRIC_R3_TRIPLE_PRIME)へ追記して同一batch call内に混在させたところ、
# Safety-critical claim(bgroup_B3)がQUALITYへ誤降格するprompt priming
# (原則文がプロンプト中に存在するだけで、条件上は無関係なclaimの判定にも
# 寛容化バイアスが波及する現象)が実測された(design書§6-4/REPORT§16)。
# 本ファイルは、Title/Hookに位置するclaimの再評価を**完全に別のPrompt・
# 別のAPI call**として分離した「Hook専用Stage2」を実装する。本文
# (body/in_one_line)のclaimは引き続き
# er052_open233_self_recovery_stage2_calibration_01.RUBRIC_R3_TRIPLE_PRIME
# (本ファイルは一切参照・変更しない)で判定される。両者が同一callへ
# 混在しないことが、prompt priming遮断の構造的保証である。
#
# 入力設計(委任文§3 A-2): Ledger全文+source context(JA原文参考)+
# タイトル・hook段落のみ(本文全体・対象claimを含む段落±1段落のような
# 広い文脈は渡さない、意図的な縮小)+対象claim配列。schema=materiality/
# basis/rewrite_kind/rewrite_hint(既存Stage2 productionと同一フィールド、
# er052_open233_self_recovery_stage2_production_01._ITEM_PROPSを再利用)。
#
# 重要な設計制約(既存er052系Trialと同一原則):
# - Production code(er003/er006/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録する。
# - 既存er052_open233_self_recovery_stage2_production_01.py/
#   stage2_calibration_01.pyは変更しない(read-onlyで定数・関数を再利用
#   するのみ)。
from __future__ import annotations

import json
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_stage2_production_01 as s2p

HOOK_DEVELOPER_MESSAGE = (
    "あなたはVerified Fact LedgerとFact Safetyの独立監査担当(Second Judge)です。"
    "これは記事のTitle/Hook(冒頭の演出・場面描写)に位置するclaimのみを対象とした専用評価です。"
    "一次チェッカー(Stage 1)が既にBLOCKING-candidateとして検出した、Title/Hookに位置するclaimに"
    "ついて、読者を引きつける演出として自然に許容できる範囲か、本当にProductionを止めるべき"
    "material errorかを、あなた自身の判断で再評価してください。"
)

# ------------------------------------------------------------
# HOOK_RUBRIC(委任_17 A-2、委任文§2の原則文どおり)。「迷う場合は発明の
# 有無で判定し、発明がなければQUALITY」という委任文の指示を明記する
# (tie-breakを固定し、判定のブレを抑える)。
# ------------------------------------------------------------
HOOK_RUBRIC = """【Hook専用 materiality判定基準(委任_17、Title/Hookに位置するclaimのみに適用)】
Title・Hookは読者を引きつけるための演出の場です。確認済みのFactから人間が自然に導ける
情景描写・呼びかけ・比喩・誇張のない強調は、QUALITYまたはACCEPTABLEとして扱い、
Rewriteの対象にしないでください。
以下のいずれかに明確に該当する場合のみBLOCKINGとしてください:
(a) Ledgerに無い新しい具体的な人物・数字・出来事・行動・仕組みを発明している。
(b) Ledgerのclaim/scope/numeric_value/date_or_period/conditionsのいずれかと矛盾している。
(c) Ledgerが記録した事実と逆方向の因果を述べている。
(d) 主体(actor)・数値(number)・否定(negation)・比較(comparison)・時期(time)のいずれかに
    ついて、Ledgerと矛盾する重大な変更を加えている。
上記(a)〜(d)のどれに該当するか迷う場合は、「新しい具体的な事実の発明があるかどうか」だけを
判断基準にしてください。発明が無ければQUALITYとしてください(演出目的の誇張のない強調・
情景描写・呼びかけであること自体を理由にBLOCKINGにしないでください)。"""

# ------------------------------------------------------------
# 委任_27 Part1-5(OPEN-233-SELF-RECOVERY-TRIAL-01、design書§0/§4-18):
# 重大誤解原則の追加(Hook専用)。HOOK_RUBRIC本文は変更せず新定数として
# 追加する(priming再測定の要件は本ファイルと同一、design書§4-18参照)。
# 本委任ではrun_stage2_hook_batchへ未配線(Hormuz要素は本文claimのため、
# Part2実測の対象外)。
# ------------------------------------------------------------
HOOK_MISCONCEPTION_PRINCIPLE_TEXT = """
【重大誤解原則(2026-10-01ユーザー指示、最初の問い)】
まず「この違いは英語学習者に記事の本質について重大な誤解を与えるか」を
判断してください。主要な意味・主体・方向・規模・時間軸を誤認させる場合
のみBLOCKINGとしてください。用語の近似・一般化・数値丸め・確認済み
Factから自然に導ける解釈や演出は、厳密には違うというだけの理由で
BLOCKINGにしないでください。"""

HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE = HOOK_RUBRIC + "\n" + HOOK_MISCONCEPTION_PRINCIPLE_TEXT

# ------------------------------------------------------------
# 委任_28 Part0-3(OPEN-233-SELF-RECOVERY-TRIAL-01、design書§0/§4-18続き):
# Hook許容基準のtie-break明文化。HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE
# 本文は変更せず(既存iteration証跡の再現性維持)、新定数として追加する。
# Meta要素Trial B(委任_28 Part2)で実測する。
# ------------------------------------------------------------
HOOK_TIEBREAK_TEXT = """
【Hook許容基準のtie-break明文化(委任_28、§0に基づく)】
確認済みのFactから自然に導ける、読者(受け手)側の体験描写・場面描写・
attention grabber・conversational restatement(元の出来事を平易に
言い換えるだけの表現)は許容してください(QUALITYまたはACCEPTABLE)。
BLOCKINGとするのは、Ledgerに無い未確認の具体的な人物・具体的な行動・
具体的な数字を新たに追加する場合、またはFactと逆方向の出来事を述べる
場合のみとしてください。"""

HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V2 = (
    HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE + "\n" + HOOK_TIEBREAK_TEXT
)

# ------------------------------------------------------------
# 委任_29 Part2(Meta要素Trial B実測でのfalse block是正、最小修正1回):
# V2実測(n=2〜3、er052_output/open233_element_trial_meta_hook_01/
# summary_meta_hook.json)で、許容群2件が毎回BLOCKINGになった(false
# block、委任文目標「許容・境界 全て非BLOCKING」未達)。
# - accept-4-scene-depiction(“Ring, ring. The phone connects, and for a
#   moment neither side lets on who is really speaking.”、2/2
#   BLOCKING)。basis=unsupported_relationship、rewrite_hint逐語:
#   「双方が意図的に身元を隠したという未確認の描写は避け…」
# - boundary-1-dramatization(“The surprise came halfway through the
#   call.”、2/2 BLOCKING)。rewrite_hint逐語: 「驚きが通話の途中で
#   起きたという未確認の時点描写を削り…」
# - accept-1-original-hook(実際に公開済みの記事本文そのもの、1/3
#   BLOCKING)。rewrite_hint逐語: 「会話の進行中に人間だと判明した
#   出来事まで描写しています。そのタイミングや驚きが実際にあったとは
#   確認できないため…」
# いずれも、確認済みの中心的な出来事(AIだと思っていたら実は人間
# だった)を読者に体験させるための自然な時間経過・雰囲気描写を、
# 「具体的で未確認の新しい行動・タイミングの発明」と誤認している
# (HOOK_TIEBREAK_TEXTの「体験描写・場面描写」という語だけでは、この
# 区別が曖昧だったと判断する)。是正は原則文のみを追加し(新しい例示は
# 最小限)、既存HOOK_TIEBREAK_TEXT本文は変更しない(既存証跡の再現性
# 維持)。
# ------------------------------------------------------------
HOOK_TIEBREAK_TEXT_V3 = HOOK_TIEBREAK_TEXT + """

【追加明確化(委任_29、Hook許容Trial実測でのfalse block是正、最小修正
1回)】
確認済みの中心的な出来事(例: AIが話していると思っていたら、実は人間
だった)を、電話がつながる・会話が進む・やがて気づく・驚きが訪れると
いった自然な時間の流れとして描写する場合は、「しばらくの間」「会話が
進むうちに」「通話の途中で」のようなおおまかな時間経過や、「どちらも
すぐには正体を明かさない」のような一般的な雰囲気描写を含んでいても、
Ledgerに無い新しい具体的な人物・数字・仕組みを発明しない限り許容して
ください(QUALITYまたはACCEPTABLE)。これは「いつ・どのように気づいた
か」という検証可能な新事実の追加ではなく、確認済みの出来事を読者に
体験させるための自然な演出の範囲内です。一方、特定の人物が意図的に
何らかの具体的な行動を取った(例: 台本を用意した、意図的に特定の
隠蔽工作をした)と、Ledgerに無い具体的な行動を新たに断定する場合は、
引き続きBLOCKINGとしてください。"""

HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V3 = (
    HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE + "\n" + HOOK_TIEBREAK_TEXT_V3
)

HOOK_BATCH_PROMPT_TEMPLATE = """これはStage 1が既にBLOCKING-candidateとして検出した、Title/Hookに
位置する複数claimの一括再評価です。Stage 1の判定理由(explanation/severity/10種類のフラグ)は
ここでは一切提示しません。以下のLedger全文・記事の日本語原文(参考)・Title/Hookの本文
(評価対象の範囲はここに限定します)・対象claim配列のみを見て、あなた自身の判断でclaimごとに
materialityを判定してください(claim間で互いに影響を与えず、各claimを独立に評価してください)。

【Verified Fact Ledger(全文)】
{verified_ledger_text}

【記事の日本語原文(参考、逸脱の発生源特定用。無ければ「(なし)」)】
{source_article_text}

【Title/Hook(評価対象の範囲はここに限定。本文の他の段落は判定に使わないでください)】
{title_hook_text}

【対象claim配列】
{claims_block}

{hook_rubric}
{rewrite_hint_instruction}

claim配列と同じ順序・同じ件数で、claim_indexを付けてmateriality/basis/rewrite_kind/rewrite_hintを
判定してください。"""

# schema=materiality/basis/rewrite_kind/rewrite_hint(委任文§3 A-2)。既存
# Stage2 productionの_ITEM_PROPS(基本フィールド定義)をそのまま再利用する
# (フィールド自体は変更しない、rubric本文のみがHook専用)。
_HOOK_ITEM_PROPS = dict(s2p._ITEM_PROPS)

HOOK_BATCH_JSON_SCHEMA = {
    "name": "open233_self_recovery_stage2_hook_batch_v1",
    "schema": {
        "type": "object",
        "properties": {
            "judgments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"claim_index": {"type": "integer"}, **_HOOK_ITEM_PROPS},
                    "required": ["claim_index", "materiality", "basis", "rewrite_kind", "rewrite_hint"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["judgments"],
        "additionalProperties": False,
    },
    "strict": True,
}


def run_stage2_hook_batch(client, verified_ledger_text: str, source_article_text: str | None,
                           title_hook_text: str, claims: list, model: str = s2p.MODEL,
                           hook_rubric_text: str = HOOK_RUBRIC) -> dict:
    """claims: list of dict{claim_text, origin, related_fact_id, ...}。
    委任文§3 A-2どおり、local_context(段落±1)は渡さない(Title/Hookの
    みへ入力を意図的に限定する)。

    委任_28 Part0-1(design書§0/§4-18): `hook_rubric_text`(既定
    `HOOK_RUBRIC`、本文不変)を追加した。既存呼び出し元は無変更のまま
    動作する。値を渡した場合のみ(例:
    `HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V2`)、そのrubric文字列を
    prompt本文とdeveloper向け参照の両方へ使う(重大誤解原則の実配線)。"""
    blocks = []
    for i, c in enumerate(claims):
        blocks.append(
            f"[claim_index={i}]\nclaim: {c['claim_text']}\n"
            f"origin: {c.get('origin') or '(不明)'}\n"
            f"related_fact_id: {c.get('related_fact_id') or '(不明)'}"
        )
    claims_block = "\n\n".join(blocks)
    prompt = HOOK_BATCH_PROMPT_TEMPLATE.format(
        verified_ledger_text=verified_ledger_text,
        source_article_text=source_article_text or "(なし)",
        title_hook_text=title_hook_text or "(なし)",
        claims_block=claims_block,
        hook_rubric=hook_rubric_text,
        rewrite_hint_instruction=s2p.REWRITE_HINT_INSTRUCTION,
    )
    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **HOOK_BATCH_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": HOOK_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = round(time.time() - t0, 3)
    parsed = json.loads(response.output_text)
    usage_dict = s2p._extract_usage(response)
    return {
        "prompt_sha256": s2p.sha256_text(prompt), "parsed": parsed, "model": response.model,
        "response_id": response.id, "usage": usage_dict,
        "cost_jpy": round(s2p.official_cost_jpy(usage_dict), 4), "elapsed_seconds": elapsed,
    }
