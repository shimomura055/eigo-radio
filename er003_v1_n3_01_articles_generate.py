# ============================================================
# er003_v1_n3_01_articles_generate.py
# ER-003-A2-B1-N3-01: 3テーマ横展開 B1-B/A2記事生成(共通Ledgerから)
# ============================================================
# ER-003-IRAN-A2-B1-01のCOMMON_BLOCK_TEMPLATE(Hanshin masterによる
# スタイル参照+Verified Fact Ledgerのみを事実源とするDirect Generation
# 方式)を一般化し、任意のtopic/ledgerに対してB1-B(直接生成、B2経由
# しない)とA2(V2改1)をそれぞれ独立したWriter呼び出しで生成する。
# B1-BのDifficulty Control原則は、今回のN3-01spec 7〜9節の記述を
# そのままinstructionへ翻訳したもので、新しいhard ruleは追加しない
# (一文語数上限・CEFR外語彙禁止・受動態禁止等は設けない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_n3_01_articles_generate.py
from __future__ import annotations

import json
import os
import re
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_evidence_compression_editor as ec_editor
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er008_point_overlap_qa_18 as overlap_qa
import er008_point_regenerate_19 as point_regen
import er008_shared_point_blueprint_01 as blueprint_mod
import er009_diagnostic_full_retry_modules_12 as diagnostic_mod

load_dotenv()

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

# ER-006-MODEL-ROUTING-CONTRACT-01 / 追補(SSOT迂回防止): B1/A2 Writer・Writer
# Fact Check・Deviation CheckはApproved Model(Luna)をSSOTから取得し、各API call
# の引数へ直接`routing.require_model(...)`をinlineで埋め込む(モジュール変数へ
# 事前計算して使い回さない)。これにより、call siteを見ればfail-closed検証を
# 経由しているかがgrep一発で分かり、新しいcall siteがこれを経由せず追加された
# 場合はstatic auditで検出できる。上のMODEL変数自体はこのファイル内のAPI call
# では一切使われていない(死んでいる)。ER-009-N1-POINT-RETRY-ROUTING-
# GOVERNANCE-10(2026-08-30)時点でvfl01.MODELの参照元をrouting.WRITER_MODEL
# (Luna)へ張り替え済みのため、現在はLuna系譜になっている(旧: Sol系譜)。


def _writer_process(label: str) -> str:
    return "B1_WRITER" if label == "B1B" else "A2_WRITER"

POINT_TARGET_LOWER = 30
POINT_TARGET_UPPER = 60
POINT_TOLERANCE_LOWER = 25
POINT_TOLERANCE_UPPER = 70
TOTAL_SOFT_LOWER = 280
TOTAL_SOFT_UPPER = 420

THEMES = [
    {
        "theme_id": "hanshin",
        "topic": ("2026年8月16日、マツダスタジアムで行われた広島東洋カープ対阪神タイガース戦。"
                   "阪神は初回の佐藤輝明の2ランホームランで先制し、先発伊原陵人が5回2安打1失点と"
                   "試合を作り、7回・8回にも加点して8-1で完勝した。広島の得点は5回のモンテロの"
                   "ソロホームラン1点のみだった。"),
        "ledger_path": "er003_output/n3_01/hanshin/research/verified_fact_ledger.txt",
        "out_dir": "er003_output/n3_01/hanshin",
    },
    {
        "theme_id": "health",
        "topic": ("睡眠・運動・食事における「小さな改善」が健康的な寿命の延びと関連していたという"
                   "2026年の大規模観察研究(University of Sydney、UK Biobankコホート約6万人、"
                   "eClinicalMedicine誌掲載)。1日5分の睡眠延長・2分の運動増加・野菜半皿分の"
                   "改善の組み合わせが、統計モデル上、約1年分の健康寿命の延びと関連していた。"),
        "ledger_path": "er003_output/n3_01/health/research/verified_fact_ledger.txt",
        "out_dir": "er003_output/n3_01/health",
    },
    {
        "theme_id": "household",
        "topic": ("冷蔵庫のクリスパードロワー(野菜室)には低湿度・高湿度の2種類があり、正しく"
                   "使い分けると食品が長持ちする。高湿度は葉物野菜がしおれるのを防ぎ、低湿度は"
                   "果物が放出するエチレンガスを逃がして周囲の食品が早く傷むのを防ぐ。"
                   "(Iowa State University Extension and Outreach等の情報に基づく)"),
        "ledger_path": "er003_output/n3_01/household/research/verified_fact_ledger.txt",
        "out_dir": "er003_output/n3_01/household",
    },
]


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ER-003-IRAN-A2-B1-01のCOMMON_BLOCK_TEMPLATEを一般化(topicを引数化した以外は無変更)
COMMON_BLOCK_TEMPLATE = """以下は、私が良いと評価している日本語記事です。

【マスター記事】

{hanshin_master_full_text}

【今回のテーマ】

{topic}

この阪神記事が良いのは、全体の概要を面白く展開し、ポイントでは本文とは別の切り口から解説し、
最後に一言でまとめることで、聞き手が飽きない設計になっている点です。

このセンスを活かして、今回のテーマの記事全文をMarkdownで書いてください。

阪神や野球固有の表現をコピーするのではなく、今回の題材に合う表現を使ってください。

【記事構成(重要)】
以下の構成で書いてください:
1. Title(#見出し)
2. Main Story(本文、複数段落)
3. ポイント部分: Markdownの「###」見出しをちょうど2つ置いてください(Point One相当、Point Two相当)
   【重要・見出しテキストの制約】この「###」見出しの文字列自体には、
   "Point One"・"Point Two"・"Point 1"・"Point 2"・「第一に」・「第二に」
   といった番号ラベルを含めないでください。番号は本文の音声化時に
   専用のNotification音で表現する仕様(ER-003-POINT-NOTIFICATION-01)
   のため、見出しはその内容だけを短く言い表すフレーズにしてください
   (良い例: "A pattern, not a final cause" / 悪い例: "Point Two: A
   pattern, not a final cause")。1つ目・2つ目という並び順そのものは
   見出しの登場順で伝わるため、ラベルとして書く必要はありません。
4. In One Line相当の結び(「## In one line…」のような見出しの後に1〜2文の結び)

【Main Storyの役割(重要)】
Main Storyでは、何が起きるのか・誰が対象か・どのような仕組みか・現在どういう状態か、という
中心ストーリーの核心だけを伝えてください。以下は、Point One/Point Twoで扱うべき内容であり、
Main Storyへ必要以上に入れないでください:
- 背景・周辺的な詳細
- 補助的な数値
- 別角度の解釈
- deeper implications
これらを詰め込むためにMain Storyを不自然に長くしないでください。

【Point One / Point Twoの役割(重要、Point Balance原則)】
Point One・Point Twoは、本文の再説明ではなく、以下のいずれかを短く提示する場所です:
- 本文とは別の切り口
- 示唆
- 背景
- 心理
- 社会的含意
- 別の因果
- 実生活上の解釈
- 意味づけ
- ニュースから読み取れる別の示唆
- 聞き手が「なるほど」と思える補助線

【最重要・言い換えによる重複の禁止(ER-008-N8-FINAL-CLOSEOUT-24で強化)】
Main Storyで既に説明した中心的なlogic・結論を、語彙や言い回しだけを変えて
もう一度説明することは、たとえ表面上の単語が違っていても「本文の再説明」に
該当し、禁止です(例: 本文が「早く並ぶ方が損失が小さいから合理的」という
非対称リスクの論理を説明した後、Pointで同じ非対称リスクの論理を別の単語で
繰り返すことは禁止。Pointは、その論理を前提とした上で「では、なぜ人は
それに従うのか(心理)」「それが広がるとどうなるか(社会的含意)」等、
本文が触れていない一段先の内容へ進んでください)。

【生成手順(推奨)】
Point One・Point Twoを書く前に、まずMain Storyで既に説明した中心的な論点・
結論を自分の中で特定してください。Point One・Point Twoでは、その論点の
言い換えを避け、その論点を前提として一段深める内容(上記リストのいずれか)
だけを書いてください。

禁止:
- 本文の長い再説明
- 本文の中心的なlogic・結論の言い換えによる再説明
- Fact Ledgerの詳細を網羅的に再掲すること
- Point内で新しい第二の本文を作ること
- Point One・Point Two同士が互いに同じ役割(同じ切り口)を担うこと(両方とも
  異なる役割を持たせてください)
- Verified Fact Ledgerに無い新しいFactの追加(Point Balanceのための深掘りも、
  Ledgerの範囲内で行ってください)

Point One・Point Twoの長さの目標は、それぞれ30〜60語、許容範囲は25〜70語です(hard capでは
ありません)。この範囲から外れる場合、なぜその長さが必要か、targetへ収めると何を失うかを、
後で説明できるように意識して書いてください。語数合わせのために内容や自然さを壊さないでください。

【記事全体の長さについて】
記事全体の総語数は、280〜420語程度を観察用の目安としてよいですが、hard capではありません。
今回最も重要なのは中心ストーリーを明確に伝えることであり、語数に合わせるための不自然な削除・
追加はしないでください。

【Spoken-first原則(数字の扱い)】
A. Fact Ledgerにある数字を恣意的に削らない。あなたが行うのは、聞いて理解しやすい形で数字を
   どう表面化するかという編集判断であり、Factを捨てることではない
B. 正確な数値そのものが本質でない場合、rose/fell/collapsed/eased等、変化の方向性を優先してよい
C. Exactnessが不要な場合は丸めてよい。ただし丸めによって意味が変わらないこと
D. 一つの文、または一つの短い意味ブロックで、聞き手が同時に比較しなければならない主要数字は
   原則2つ以内とする(記事全体でのhard capではない)
E. 単位を連続させすぎない
F. Fact Ledgerでnumber_classification: ANCHORと印のある数値は、本記事の核心的データであり、
   丸めすぎて意味が消えないよう注意する
G. exactness_requirement: EXACT_REQUIREDと印のある数値(スコア・日付・記録・研究結果の主要数値・
   安全性に関わる閾値等)は、精度自体が意味を持つため、正確な値を保持する

【今回のFact源について(重要)】
今回は、あなた自身によるWeb検索や新しい具体的事実の追加を行わないでください。
以下のVerified Fact Ledgerだけを事実源として使用してください。

{verified_ledger_text}

【Fact Ledger使用上の制約】
- Verified Fact Ledgerにない具体的Factを追加しないでください
- confirmed factと、観察研究の相関関係("associated with")を混同しないでください。
  "was associated with"を"causes"や"prevents"に変換しないでください
- 個人への具体的な推奨・診断・治療指示(健康テーマの場合)や、危険な使用法の推奨(家事テーマの
  場合)を行わないでください
- 「この記事で使わない、または確認できなかった情報」に列挙された内容は、本文・Pointいずれにも
  詳しく書き込まないでください
- 複数のFactを物語として自然にまとめてもかまいませんが、Fact同士の関係(誰が・何を・いつ・
  どの範囲で)を変えないでください
{shared_point_blueprint_block}{evidence_compression_block}"""


# ============================================================
# ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03/ER-008-FALLBACK-
# TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04: Evidence
# Compression(script-only候補、opt-in、Writer方式=Compression-aware
# Writer)。Research/Evidence Pack/VFL/Fact Checkは一切変更せず、spoken
# layer(実際に読み上げられる文章)だけを対象に、理解に不要な固有名詞・
# 数字を減らす方針を試す。既定(evidence_compression_block未指定=空
# 文字列)ではCOMMON_BLOCK_TEMPLATEと完全に同一で、Production Writer
# の挙動には一切影響しない。
#
# AB-04追記: 初回検証(ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03)
# のNo.7 B1 candidateで、出典名・数字を削った結果、元のcorrelational
# evidenceより踏み込んだ因果的表現("...because some offices are
# questioning the human cost of desk sharing"等)が新規に混入する
# drift が実際に発生した。これを防ぐため、Fact safety不変条件を明示的な
# 禁止リストとして追加した。
# ============================================================
EVIDENCE_COMPRESSION_BLOCK = """
【Evidence Compression(今回の記事にのみ適用する追加方針)】
方針: "Evidence is thick backstage, light on air." Fact自体はVerified Fact
Ledgerの範囲内で自由に参照してよく、Fact Checkのために裏側では厚く保持され
ます。ただし、実際に読み上げられる文章(spoken script)では、理解に必要
でない限り、以下を極力減らしてください:
- 企業名・調査会社名・研究機関名・メディア名・イベント名
- 研究が行われた年(記事全体で起きている出来事の時系列そのものに必要な
  年は除く)
- 聞き手の理解に不要なpercentage・sample size・方法論の詳細
- 意味がほぼ重複する複数の近似した数値の並列(例: 2つの比較を両方とも
  読み上げる必要が本当にあるか)

固有名詞の判断基準: 「この名前を音声で聞くことで、リスナーの理解が実質的
に改善するか」を基準にしてください。改善しない場合は、"a survey"
"several companies" "one report" のように一般化してください。固有名詞を
ゼロにすること自体は目的ではありません。

数字の判断基準: 数字を全て削除する必要はありません。ただし、1つのPoint
の中で複数の数字が連続し、リスナーの注意が意味ではなく数値の記憶へ向いて
しまう状態は避けてください。2つの比較数値の組を両方とも読み上げるより、
"workers with assigned desks were more likely to report both belonging
and better focus"のように、傾向を示す1文へ圧縮できないか検討してください。
一方、トレンドの大きさ・方向そのものを理解するために必要な核心的な比較
(例: 56% → 40% → 約1/3のような時系列を伴う比較)は必要に応じて残して
ください。機械的な「数字は最大N個まで」のような硬いルールは今回課しません。

一方、以下は削らずに残してください:
- Storyの核心そのもの
- 驚くべき規模・変化の大きさ(surprising scale)
- トレンドの方向性
- 因果関係の範囲(相関を因果と混同させない、Fact Checkの制約は継続)
- 不確実性の表現(「関連が見られた」等、断定を避ける表現)
- 読み手が誤解しないために必要な情報

【Fact safety(絶対に変更してはいけないもの、最優先)】
Evidenceを減らす作業のなかで、以下を一切変更しないでください。数字や
固有名詞を削った結果、埋め合わせるように主張を強めることは禁止します:
- 相関(correlation)を因果(causation)へ変えないこと("was associated
  with"を"causes"/"leads to"/"because"のような断定へ言い換えない)
- 不確実性の表現(hedging)を削らないこと("a connection, not proof"の
  ような限定は、具体的な数字・出典名を削ってもそのまま残すこと)
- 主張が及ぶ範囲(scope)を広げないこと(「一部の企業」を「多くの企業」
  「企業全体」のように広げない)
- 比較の向き(どちらが大きい/多いか)を変えないこと
- 否定の有無を変えないこと
- 出来事の時系列の前後関係を変えないこと
- 新しいFactや新しい因果関係を作り出さないこと
"""


def build_common_block(master_full_text: str, topic: str, verified_ledger_text: str,
                        shared_point_blueprint_block: str = "", evidence_compression: bool = False) -> str:
    """shared_point_blueprint_blockは、A2/B1 Point Structure Semantic
    Alignment(Shared Point Blueprint)導入タスクで追加したオプション引数。
    evidence_compressionは、ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03
    Part Bで追加したオプション引数(script-only candidate生成専用)。
    いずれも既定値(""/False)の場合は旧来のCOMMON_BLOCK_TEMPLATEと完全に
    同一テキストになり、後方互換を保つ(未使用のTopicへは一切影響しない、
    Production既定は無変更)。"""
    block = f"\n{shared_point_blueprint_block}\n" if shared_point_blueprint_block else ""
    ec_block = EVIDENCE_COMPRESSION_BLOCK if evidence_compression else ""
    return COMMON_BLOCK_TEMPLATE.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        shared_point_blueprint_block=block,
        evidence_compression_block=ec_block,
    )


# ============================================================
# B1-B: 直接生成(B2経由しない)。N3-01 spec 7〜9節の記述をそのまま
# instructionへ翻訳したもの。新しいhard ruleは追加しない。
# ============================================================
B1_B_DIRECT_INSTRUCTION = """Write this directly as a B1-level English news story for listening \
(do NOT write a B2 version first and simplify it — write B1 English directly from the Fact Ledger).

Basic idea: keep the natural feel of adult news English, while reducing how much information the \
listener has to process at once while listening.

Apply these principles as guidance, not as mechanical hard rules:

Clause Density: Don't pack multiple facts, conditions, contrasts, or attributions into a single \
sentence. Prefer one main idea plus limited supporting detail per sentence.

Long-distance Dependency: Don't make the listener hold information from the start of a sentence for \
too long. Split long inserted clauses or nested structures where it helps listening.

Abstract Noun Chains: Where it would block understanding, turn nominalizations back into verb \
phrases (for example, prefer "ease sanctions" over "sanctions relief") — but do this as a judgment \
call, not a mechanical conversion rule.

Logical Flow: Where needed, make logical relationships explicit with connectors such as "But," "At \
the same time," "Earlier," "For now," "That matters because..." — but don't mechanically add more \
transitions than the passage needs.

Concept Density: Don't introduce multiple new concepts in a short passage.

Passage Rebuilding: Don't do a simple 1:1 rewrite of source-style sentences. You may rebuild passages \
freely from the same Fact / Story Core to make them work as B1 English, as long as you add no facts, \
causes, intentions, or evaluations that aren't in the Fact Ledger.

Vocabulary / Grammar: There is no B1-word-list hard rule. Keep important words needed for the topic. \
Passive voice, relative clauses, present perfect, and subordinate clauses are all allowed when they \
read naturally — the target is grammar PROCESSING LOAD, not banning specific grammar items.

Do not add any of these new hard limits: a maximum words-per-sentence rule, a ban on any specific \
CEFR-external vocabulary, a ban on passive voice or relative clauses, or a strict one-fact-per-sentence \
rule. Average sentence length may be recorded as a diagnostic, not enforced as a rule.

The result should sound clearly easier to follow while listening than a B2 news story, while still \
sounding like real adult news English — not simplified "textbook" English."""

A2_KAI1_INSTRUCTION = """Write this as an A2-level English news story for listening. The listener should be able to understand the main events and why they matter even if their English is still limited. Present information in a clear sequence, make relationships between events explicit, and avoid making the listener hold several ideas in mind at once. Use simple, natural English and explain difficult concepts in an everyday way. Rebuild difficult parts freely rather than trying to preserve sophisticated sentence structures or phrasing.

Preserve the core explanatory logic and decision rule established by the Verified Fact Ledger. You may simplify wording, sentence structure, examples, and presentation order, but do not replace the Ledger's underlying mechanism or decision rule with an easier shortcut, category, causal explanation, or rule of thumb that the Ledger does not support or explicitly rejects. Simplify how the listener understands the idea, not what the idea means.

Keep each step of the story mentally light. Introduce one main idea at a time, and do not ask the listener to connect several facts, conditions, or contrasts inside the same sentence or short passage. When a sentence carries more than one important idea, separate those ideas and explain them in a simpler order. Prefer clear cause-and-result or before-and-after relationships over compressed explanation.

Keep the story interesting and adult in subject matter. It should sound like real spoken news, not children's English or a classroom exercise. This should be a genuinely different, separately-optimized narrative from the B1 version, not a lightly-reworded copy of it — build it fresh from the same Fact Ledger and Story Core, selecting and simplifying information more aggressively than B1 does."""


def build_prompt(common_block: str, instruction: str) -> str:
    return common_block + "\n【難易度指示】\n" + instruction


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")


def compute_metrics(text: str) -> dict:
    flat = " ".join(line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))
    word_count = ab01.compute_word_count(flat)
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(flat) if s.strip()]
    sentence_count = len(sentences) if sentences else 1
    sentence_lengths = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences] or [word_count]
    avg_len = round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0
    max_len = max(sentence_lengths) if sentence_lengths else 0
    return {"word_count": word_count, "sentence_count": sentence_count,
            "avg_sentence_length": avg_len, "max_sentence_length": max_len}


# ============================================================
# ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19 Item 3: Point-only
# regeneration(Point One/TwoがFull Storyの言い換えになっているsegmentだけ
# を、記事全体を作り直さずに差し替える)
# ============================================================
# Point One/Twoの役割(CURRENT_SPEC.md「Full Storyの役割」節):
# 「Full Storyだけでニュースの核心が分かる。Point One/Twoは深掘り・背景・
# 意味付けとし、Full Storyの代替にしない」を英語化したもの。
POINT_ROLE_SPEC_EN = (
    "Point One and Point Two exist to go deeper than the Full Story: they add "
    "background, interpretation, or meaning a listener would not get from the Full "
    "Story alone. They must not simply restate or summarize the Full Story's core logic."
)


def build_diagnostic_retry_prompt(original_prompt: str, previous_article_text: str,
                                   point_overlap: dict) -> str:
    """Diagnostic section を含む retry prompt を build する。

    前回の記事・Point overlap スコア・shared words・簡易診断を
    NG例として prompt に追加する。Evidence/VFL固定で全文再生成させる。"""
    sections = split_common_sections_for_point_qa(previous_article_text)
    if sections is None:
        return original_prompt

    diagnostic_section, _ = diagnostic_mod.build_diagnostic_section(
        sections["full_story"],
        point_overlap["point_one"],
        point_overlap["point_two"],
    )

    return original_prompt + "\n\n" + diagnostic_section


def split_common_sections_for_point_qa(article_text: str) -> dict | None:
    """run_one_patternが生成するarticle_text(Title + Main Story + ###
    Point見出し×2 + ## In one line、COMMON_BLOCK_TEMPLATE共通構造)から、
    Full Story本文とPoint One/Twoの見出し・本文を抽出する。想定構造で
    ない場合はNoneを返す(呼び出し側はQAをスキップする、既存のwriter
    structure validator[restore_r2.validate_point_structure]が本来の
    構造検証を別途担うため、ここでは新しいhard failureを追加しない)。"""
    h3_matches = list(re.finditer(r"^###\s+(.+?)\s*$", article_text, flags=re.MULTILINE))
    if len(h3_matches) != 2:
        return None
    title_match = re.match(r"^#\s+.+?\s*\n", article_text)
    full_story_start = title_match.end() if title_match else 0
    in_one_line_match = re.search(r"^##\s+In one line", article_text, flags=re.MULTILINE)
    point_two_end = in_one_line_match.start() if in_one_line_match else len(article_text)
    return {
        "full_story": article_text[full_story_start:h3_matches[0].start()].strip(),
        "point_one_heading": h3_matches[0].group(1).strip(),
        "point_one_body": article_text[h3_matches[0].end():h3_matches[1].start()].strip(),
        "point_two_heading": h3_matches[1].group(1).strip(),
        "point_two_body": article_text[h3_matches[1].end():point_two_end].strip(),
    }


# ER-008-N8-FINAL-QA-HARDENING-21 Item 6: Point-only regeneration
# (er008_point_regenerate_19.regenerate_point_only)は、No.8の実データ
# 検証でVerified Fact Ledgerに無い新しい主張("American Airlinesの搭乗
# 順違反への罰則"等)を作り出す実例が確認された。Point-onlyの局所書き換え
# はFull Story/他方のPoint/Fact Ledgerとの整合性チェックが薄く、Fact
# Checker頼みの二段構えになってしまっていたため、Production自動経路
# から外す(PRODUCTION_WIRED扱いを撤回、CURRENT_SPEC.md/DECISION_LOG.md
# 参照)。
#
# 「記事全体Writerを再実行し、overlap QA、NGならretry最大2回、それでも
# NGなら自動継続せずNG/REVIEW_REQUIREDとして報告する」という暫定
# Production方式は、Writerの実測コスト(No.8実測: writer_a2単体で約$1.5、
# 複数回のretryを含む)を踏まえると、overlap NG発生率次第では1記事あたり
# コストが数倍に増える可能性があり、実装前にユーザー承認が必要な項目
# として現時点ではSTOPしている(ER-008-N8-FINAL-QA-HARDENING-21 Item 6
# 報告参照)。そのため、このflagがFalseの間は「NGを検出したら、本文は
# 一切書き換えずreport上でNG/REVIEW_REQUIREDとして残す」という、暫定
# 方式の中で追加コストが一切発生しない最も安全側のサブセットのみを実行
# する(regenerate_point_only()自体は呼び出されない)。
POINT_ONLY_REGENERATION_ENABLED = False


def run_point_overlap_qa_and_regenerate(client, article_text: str, verified_ledger_text: str,
                                          model: str, reasoning_effort: str, out_dir: str) -> dict:
    """Point One/TwoそれぞれについてFull Storyとの意味重複(lexical
    overlap、暫定閾値0.40)をチェックする。POINT_ONLY_REGENERATION_ENABLED
    がTrueの場合のみ、flagされたPointに対しPoint-only regenerationを行う
    (現在は無効化されている、上記コメント参照)。Falseの間は検出のみ行い
    (monitoring)、本文は変更しない。Full Story・他方のPoint・Fact
    Checker/Ledger Deviation Checkは変更しない(記事全体の再生成は行わ
    ない)。戻り値のpatched_article_textを、呼び出し側がその後のFact
    Checker/Deviation Checkへそのまま渡す(regenerateされたPointも既存の
    安全確認プロセスを通る)。"""
    sections = split_common_sections_for_point_qa(article_text)
    if sections is None:
        return {"status": "SKIPPED", "reason": "想定構造(###見出し2つ)が見つからないためQAをスキップしました",
                "patched_article_text": article_text}

    patched_text = article_text
    report = {}
    for key, label_name, other_key in (("point_one", "Point One", "point_two_body"),
                                         ("point_two", "Point Two", "point_one_body")):
        body = sections[f"{key}_body"]
        overlap = overlap_qa.flag_possible_paraphrase(body, sections["full_story"])
        entry = {"before_overlap": overlap, "applied": False}
        if overlap["flagged"]:
            ng_reason = (f"Lexical overlap with Full Story = {overlap['overlap_ratio']} "
                         f"(threshold {overlap['threshold']}), shared content words: {overlap['shared_words']}. "
                         "This Point is likely restating the Full Story's logic instead of adding a new angle.")
            if not POINT_ONLY_REGENERATION_ENABLED:
                entry["regenerate_status"] = "NG_REVIEW_REQUIRED"
                entry["reason"] = (
                    "Point-only regenerationはER-008-N8-FINAL-QA-HARDENING-21で"
                    "Production自動経路から外されている(新Fact fabricationの実例が"
                    "あったため)。本文は変更せず、Human Reviewでの確認対象として"
                    "記録するのみ。")
            else:
                regen_result = point_regen.regenerate_point_only(
                    client, label_name, body, sections["full_story"], sections[other_key],
                    verified_ledger_text, ng_reason, POINT_ROLE_SPEC_EN,
                    model=model, reasoning_effort=reasoning_effort)
                entry["regenerate_status"] = regen_result["status"]
                entry["regenerate_attempts_count"] = len(regen_result.get("attempts") or [])
                entry["regenerate_validation"] = regen_result.get("validation")
                if regen_result["status"] == "OK":
                    patched_text = patched_text.replace(body, regen_result["new_text"], 1)
                    entry["applied"] = True
                    entry["new_text"] = regen_result["new_text"]
        report[key] = entry

    with open(f"{out_dir}/point_overlap_qa.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    return {"status": "OK", "patched_article_text": patched_text, "report": report}


# ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22:
# Point overlap NG時の正式暫定Production方式。Point-only regeneration
# (Pointの一部だけを書き換える方式)はER-21で新Fact fabricationの実例が
# あったためProduction自動経路から撤去済み(POINT_ONLY_REGENERATION_
# ENABLED=False、上記参照)。代わりに、overlapがflagされた場合は記事
# 全体をWriterから再生成する(最大2回)。Pointだけを差し替えないことで、
# Full Story/Point One/Point Two/In One Line間の内部整合をWriterに
# 保たせる。TTSより前(Assembleより前)の工程だけで完結するため、この
# retryによるTTS/ASR追加費用は発生しない。再実行するのはWriter→
# Evidence Compression→Point overlap QAの3工程のみ。Fact Checker・
# Ledger Deviation Check・Directional Fact Precheckは、retryループが
# 終わり最終的に採用が確定した記事に対して一度だけ実行する(Research/
# Evidence Pack/VFL自体はWriterへの入力でありretry対象外)。2回retryして
# もなおNGの場合は自動続行せず、status="NG_REVIEW_REQUIRED"を返し、
# Fact Checker以降は実行しない(そのままではAssembleへ進めない)。
POINT_OVERLAP_ARTICLE_RETRY_MAX = 2


def _generate_and_compress_article(client, theme_id: str, label: str, prompt: str, out_dir: str,
                                    apply_evidence_compression: bool, model: str) -> dict:
    """Writer呼び出し+(有効な場合)Evidence Compression Editorまでを1回分
    実行するヘルパー。run_one_patternの初回生成、およびPoint overlap NG
    retry時の「記事全体再生成」の両方から共通で呼ばれる。"""
    print(f"[N3-01][{theme_id}] {label}: writer呼び出し開始...")
    writer_result = vfl01.run_writer_with_technical_retry(client, prompt, model=model)
    with open(f"{out_dir}/audit/writer_attempts.json", "w", encoding="utf-8") as f:
        json.dump(writer_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if writer_result["status"] != "STRUCTURE_PASS" or not writer_result.get("raw_text"):
        print(f"[N3-01][{theme_id}] {label}: writer失敗 status={writer_result['status']}")
        return {"status": writer_result["status"], "article_text": None}

    article_text, fact_usage_report = blueprint_mod.extract_trailing_metadata_block(
        writer_result["raw_text"].strip())
    if fact_usage_report is not None:
        with open(f"{out_dir}/audit/fact_usage_report.json", "w", encoding="utf-8") as f:
            json.dump(fact_usage_report, f, ensure_ascii=False, indent=2)

    evidence_compression_applied = False
    if apply_evidence_compression:
        with open(f"{out_dir}/audit/pre_editor_article.md", "w", encoding="utf-8") as f:
            f.write(article_text)
        print(f"[N3-01][{theme_id}] {label}: Evidence Compression(Lossless Editor)呼び出し開始...")
        editor_result = ec_editor.run_lossless_editor(client, article_text, model=model)
        with open(f"{out_dir}/audit/evidence_compression_editor_raw.json", "w", encoding="utf-8") as f:
            json.dump(editor_result, f, ensure_ascii=False, indent=2, default=str)
        if editor_result.get("raw_text"):
            article_text = editor_result["raw_text"]
            evidence_compression_applied = True
        print(f"[N3-01][{theme_id}] {label}: Evidence Compression完了。"
              f"response_id={editor_result.get('response_id')}")

    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)

    return {"status": "OK", "article_text": article_text, "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied}


def run_one_pattern(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,
                     topic: str, out_dir: str, apply_evidence_compression: bool = True,
                     apply_directional_fact_precheck: bool = True) -> dict:
    """apply_evidence_compression(既定True、ER-008-EVIDENCE-COMPRESSION-
    PROD-AND-N7-AUDIO-06でProduction既定へ昇格): WriterがFact-safeな記事
    を生成した直後、Lossless Editor(方式C、er003_v1_n3_01_evidence_
    compression_editor.py)でspoken layerだけを軽量化する。Research/
    Evidence Pack/VFL/Fact Ledger自体は変更しない。EditorはWriterでは
    なく、意味を保ったまま聴取負荷を下げるだけの工程(禁止事項は
    er003_v1_n3_01_evidence_compression_editor.py参照)。Editor適用後の
    テキストに対してmetrics/Fact Check/Ledger Deviationを実行するため、
    既存の安全確認プロセスがそのままEditor出力にも適用される。DEV/test
    でOFFにしたい場合はFalseを渡す(Production既定はTrue)。"""
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    writer_model = routing.require_model(_writer_process(label), routing.WRITER_MODEL)
    gen = _generate_and_compress_article(client, theme_id, label, prompt, out_dir,
                                          apply_evidence_compression, writer_model)
    if gen["status"] != "OK":
        return {"label": label, "status": gen["status"], "article_text": None}
    article_text = gen["article_text"]
    fact_usage_report = gen["fact_usage_report"]
    evidence_compression_applied = gen["evidence_compression_applied"]

    # ER-22 + ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-WIRING-13:
    # Point overlap NG時は記事全体をWriterから再生成する(最大
    # POINT_OVERLAP_ARTICLE_RETRY_MAX回)。Diagnostic Full Retry により、
    # retry時は前回の記事・overlap score・shared words・簡易診断を
    # NG例として prompt へ追加し、Evidence/VFL固定で全文再生成させる。
    # retry対象はWriter+Evidence Compression+overlap再チェックのみで、
    # Fact Checker/Ledger Deviationはループの外(最終確定後)で一度だけ実行。
    overlap_retry_log = []
    retry_attempt = 0
    while True:
        print(f"[N3-01][{theme_id}] {label}: Point-Full Story重複QA開始"
              f"(retry {retry_attempt}/{POINT_OVERLAP_ARTICLE_RETRY_MAX})...")
        point_qa_result = run_point_overlap_qa_and_regenerate(
            client, article_text, verified_ledger_text, model=writer_model,
            reasoning_effort=REASONING_EFFORT, out_dir=out_dir)
        still_flagged = point_qa_result["status"] == "OK" and any(
            entry["before_overlap"]["flagged"] for entry in point_qa_result.get("report", {}).values())
        log_entry = {
            "attempt": retry_attempt, "qa_status": point_qa_result["status"], "flagged": still_flagged,
            "report": point_qa_result.get("report")}
        overlap_retry_log.append(log_entry)
        if not still_flagged or retry_attempt >= POINT_OVERLAP_ARTICLE_RETRY_MAX:
            break
        retry_attempt += 1
        print(f"[N3-01][{theme_id}] {label}: Point overlap NG。Diagnostic Full Retry により、"
              f"診断情報を含む prompt で全文再生成します"
              f"(article retry {retry_attempt}/{POINT_OVERLAP_ARTICLE_RETRY_MAX})...")

        # Diagnostic section を build
        point_overlap_result = {
            "point_one": point_qa_result["report"]["point_one"]["before_overlap"],
            "point_two": point_qa_result["report"]["point_two"]["before_overlap"],
        }
        diagnostic_prompt = build_diagnostic_retry_prompt(prompt, article_text, point_overlap_result)
        log_entry["diagnostic_used"] = {
            "point_one_score": point_overlap_result["point_one"]["overlap_ratio"],
            "point_one_flagged": point_overlap_result["point_one"]["flagged"],
            "point_two_score": point_overlap_result["point_two"]["overlap_ratio"],
            "point_two_flagged": point_overlap_result["point_two"]["flagged"],
        }

        gen = _generate_and_compress_article(client, theme_id, label, diagnostic_prompt, out_dir,
                                              apply_evidence_compression, writer_model)
        if gen["status"] != "OK":
            print(f"[N3-01][{theme_id}] {label}: article retry中にwriterが失敗しました status={gen['status']}")
            overlap_retry_log.append({"attempt": retry_attempt, "qa_status": "WRITER_FAILED_DURING_RETRY"})
            break
        article_text = gen["article_text"]
        fact_usage_report = gen["fact_usage_report"]
        evidence_compression_applied = gen["evidence_compression_applied"]

    with open(f"{out_dir}/point_overlap_article_retry_log.json", "w", encoding="utf-8") as f:
        json.dump(overlap_retry_log, f, ensure_ascii=False, indent=2, default=str)

    point_overlap_qa_applied = False  # Point-only regeneration自体は撤去済み(常にFalse)
    if overlap_retry_log[-1].get("flagged"):
        print(f"[N3-01][{theme_id}] {label}: Point overlapが{POINT_OVERLAP_ARTICLE_RETRY_MAX}回の記事全体"
              f"再生成後もNGのままでした。自動続行せずNG_REVIEW_REQUIREDとして報告します"
              f"(Fact Checker以降は実行しません)。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "point_overlap_article_retry_attempts": retry_attempt,
            "point_overlap_final_report": overlap_retry_log[-1].get("report"),
            "evidence_compression_applied": evidence_compression_applied,
            "fact_usage_report": fact_usage_report,
            "point_overlap_qa_applied": point_overlap_qa_applied,
        }
    print(f"[N3-01][{theme_id}] {label}: Point-Full Story重複QA完了(overlapなし、"
          f"記事全体retry {retry_attempt}回で解消)。")

    metrics = compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": POINT_TARGET_LOWER <= section_wc["point_one"] <= POINT_TARGET_UPPER,
        "point_one_within_tolerance": POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= POINT_TOLERANCE_UPPER,
        "point_two_within_target": POINT_TARGET_LOWER <= section_wc["point_two"] <= POINT_TARGET_UPPER,
        "point_two_within_tolerance": POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= POINT_TOLERANCE_UPPER,
        "total_within_soft_range": TOTAL_SOFT_LOWER <= metrics["word_count"] <= TOTAL_SOFT_UPPER,
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    print(f"[N3-01][{theme_id}] {label}: metrics={metrics} sections={section_wc}")

    print(f"[N3-01][{theme_id}] {label}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[N3-01][{theme_id}] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    print(f"[N3-01][{theme_id}] {label}: ledger逸脱チェック開始...")
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text,
        model=routing.require_model(_writer_process(label), routing.WRITER_MODEL))
    print(f"[N3-01][{theme_id}] {label}: deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    directional_precheck_status = None
    if apply_directional_fact_precheck:
        print(f"[N3-01][{theme_id}] {label}: 比較方向Fact事前チェック(暫定、"
              f"ER-008-DIRECTIONAL-FACT-PRECHECK-08)開始...")
        vfl_path = f"{os.path.dirname(out_dir)}/research/stage_b3_vfl.json"
        directional_result = dfp.audit_article_directional_facts(
            article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[N3-01][{theme_id}] {label}: 比較方向Fact事前チェック完了。"
              f"overall_status={directional_precheck_status}"
              + ("(POTENTIAL_DIRECTION_REVERSALあり、詳細はdirectional_fact_precheck.jsonを確認)"
                 if directional_precheck_status == "POTENTIAL_DIRECTION_REVERSAL" else ""))

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "fact_usage_report": fact_usage_report,
        "evidence_compression_applied": evidence_compression_applied,
        "point_overlap_qa_applied": point_overlap_qa_applied,
        "point_overlap_article_retry_attempts": retry_attempt,
        "directional_fact_precheck_status": directional_precheck_status,
    }


def run_theme(client, master_full_text: str, theme: dict, blueprint=None) -> dict:
    """blueprint(er008_shared_point_blueprint_01.SharedPointBlueprint)を
    渡すと、A2/B1それぞれのprompt末尾へBlueprint制約が挿入される
    (levelごとにrender_blueprint_for_writerでA2/B1向けの文言を分ける)。
    Noneの場合(既定)は旧来の呼び出しと完全に同一の挙動になる。"""
    theme_id = theme["theme_id"]
    verified_ledger_text = load_text(theme["ledger_path"])

    results = {}
    for label, instruction, out_dir in [
        ("B1B", B1_B_DIRECT_INSTRUCTION, f"{theme['out_dir']}/b1b"),
        ("A2", A2_KAI1_INSTRUCTION, f"{theme['out_dir']}/a2"),
    ]:
        blueprint_block = ""
        if blueprint is not None:
            level = "b1" if label == "B1B" else "a2"
            blueprint_block = blueprint_mod.render_blueprint_for_writer(blueprint, level)
        common_block = build_common_block(master_full_text, theme["topic"], verified_ledger_text,
                                           shared_point_blueprint_block=blueprint_block)
        prompt = build_prompt(common_block, instruction)
        result = run_one_pattern(client, theme_id, label, prompt, verified_ledger_text, theme["topic"], out_dir)
        results[label] = result

    with open(f"{theme['out_dir']}/articles_run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in results.items()},
                   f, ensure_ascii=False, indent=2, default=str)
    print(f"[N3-01][{theme_id}] 完了。")
    for label, r in results.items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')}")
    return results


def main():
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()

    all_results = {}
    for theme in THEMES:
        os.makedirs(theme["out_dir"], exist_ok=True)
        all_results[theme["theme_id"]] = run_theme(client, master_full_text, theme)

    print("[N3-01] 全テーマ完了。")


if __name__ == "__main__":
    main()
