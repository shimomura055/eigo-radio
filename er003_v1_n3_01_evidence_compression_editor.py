# ============================================================
# er003_v1_n3_01_evidence_compression_editor.py
# ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06 Part A/B
# ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R
# ============================================================
# Evidence Compression 方式C(Lossless Editor)の正式Production実装。
# 通常WriterがFact-safeな記事を生成した後、この関数がspoken layerだけを
# 軽量化する(Research/Evidence Pack/VFL/Fact Ledger自体は変更しない)。
# EditorはWriterではない:「より良い記事に書き直す」のではなく、「意味を
# 保ったまま聴取負荷を下げる」工程として、許可された編集・禁止事項を
# 明示的なリストとして与える。
#
# 由来: ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03(script-only初回
# 実証)→ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-
# AB-04(方式B[Compression-aware Writer]との比較、方式C推奨)→
# ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05(方式CのB1
# MAJOR逸脱1件ずつ精査、VALIDATOR_FALSE_POSITIVEと判定)→本タスクで
# ユーザーが方式Cを正式採用、Production Writer pipelineへ配線。
#
# 2026-09-04追記(ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-
# AND-FINAL-CANDIDATE-AUDIO-21R): ER-011-NO18-A2-EVIDENCE-COMPRESSION-
# ABC-*-TRIAL-18/19/20(3パターン比較・n=5再現性・Precision拡張)を経て
# ユーザーが正式採用した「Pattern A: Representative Metric + Supporting
# Trend」+「Listener-Friendly Numeric Precision」を、既存方式Cの許可
# 編集リストへの追加ルールとしてProduction正式配線する。文言はTrial-18/
# 19/20で検証済みのものと完全に同一(er011_no18_a2_evidence_compression_
# extension_abc_trial_18.py::COMMON_PURPOSE_BLOCK_EN/PATTERN_A_BLOCK_JA、
# er011_no18_a2_evidence_compression_abc_precision_extension_trial_20.py::
# PRECISION_BLOCK_EN)を、No.18固有語を含まない一般Production仕様として
# ここへ複製する(Trial定義への実行時依存は作らない、Dangling Reference
# Check対応)。Pattern B/CはDEFERRED CANDIDATE/NOT REJECTEDのため未配線。

from __future__ import annotations

EVIDENCE_COMPRESSION_PURPOSE_BLOCK_EN = """【Compression Purpose Clarification -- applies to every pattern below】
The purpose of Evidence Compression is not to reduce the number of digits for its own
sake. It is to make sure that, once heard aloud, a listener can still follow the meaning
of the Evidence. When, within the same study, survey, or comparison, multiple different
Facts or metrics point in the same direction, and listing every individual number raises
listening load, consider a way to keep the presence, meaning, and direction of comparison
of each Fact while retaining only the minimum numbers necessary.

Fact safety always takes priority over ease of listening."""

PATTERN_A_REPRESENTATIVE_METRIC_SUPPORTING_TREND_BLOCK = """【追加ルール: Pattern A - Representative Metric + Supporting Trend】
同一の研究・調査・比較の中で、複数の異なる指標が同じ方向の結果を示している場合:
- すべての比較数値を列挙しなくてよい
- リスナーが結果の大きさを理解するために、最も代表性・説明力の高い指標を1つ選び、
  その指標の比較数値(絶対値)は保持してよい
- その他の指標についても、Factとしては本文に残すこと。ただし具体的な数値は省略し、
  "showed the same pattern" "was also lower" のようなtrend表現へ言い換えてよい
- 補助的な指標のFact自体を削除しないこと
- 2つ以上の異なるFactを、1つのFactであるかのように統合して書かないこと
- 相関を因果へ強めないこと
- 実際には「同じ傾向」と言えない指標同士を、同じ傾向として扱わないこと"""

LISTENER_FRIENDLY_NUMERIC_PRECISION_BLOCK = """【追加ルール: 全Pattern共通 - Listener-Friendly Numeric Precision】

This rule applies AFTER each Pattern's own rule above has already decided which
numeric Facts to keep. First, decide whether a numeric value is worth retaining at
all, following the Pattern-specific rule above. Then, for values you keep, decide how
much precision the listener actually needs, following this rule. Do not conflate the
two decisions.

When a numeric value is worth keeping, preserve only as much precision as the
listener needs to understand its meaning.

Prefer simpler rounded values when extra decimal precision does not materially
affect:
- the direction of the comparison
- the magnitude that matters to the story
- an important threshold
- the interpretation of the evidence
- the distinction between materially different values

Do not remove decimals mechanically.

Keep decimal precision when rounding would:
- hide a meaningful difference
- cross or obscure an important threshold
- distort a small-scale measurement
- change the interpretation
- make two meaningfully different values appear equivalent
- reduce factual fidelity in a way relevant to the listener

When rounding is appropriate, use listener-friendly expressions such as "about",
"roughly", "nearly", etc. where suitable.

Most important: Rounding is NOT permission to merge separate facts, metrics,
groups, time points, survey questions, or experimental outcomes. Each retained
numeric expression must remain attributable to its original Fact / metric in the
Fact Ledger. Never combine separate Facts merely because their rounded values
become numerically similar. Before rounding, verify that each numeric expression
can still be traced to a single, specific Fact / metric / group / time point /
survey question. Do not combine numbers from different Facts or different
metrics (for example, an attention-score value and a processing-speed value)
into a single shared rounded expression, even if their rounded values happen to
look similar or identical.

The goal is not to remove decimal places. The goal is to use the least precision
necessary for accurate spoken understanding.

This is a judgment rule, not a mechanical one. Do NOT apply any fixed rule such as
"always drop decimals," "always round to a whole number," "always keep one decimal
place," or "always use two significant figures." Decide based on what each specific
number means in context.

For general guidance only (not a fixed instruction for this specific article):
decimal precision is more likely to matter for values such as small percentages
(for example 1.2% vs 1.8%), small absolute differences (for example 4.8 vs 5.2),
sub-one units (for example 0.3 seconds), multipliers (for example 1.5 times),
values near a meaningful threshold, or small differences that are themselves the
finding. These are illustrative examples of the general principle only, not
article-specific instructions."""

EVIDENCE_COMPRESSION_EDITOR_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioの記事Editorです。既に完成しているPodcast台本(Markdown)を、"
    "意味を一切変えない範囲だけで軽量に編集します。新しいFactの追加や、主張の強さを"
    "変えることは禁止です。"
)

_EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE_BASE = """【編集対象のPodcast台本(Markdown、そのまま編集してください)】
{article_text}

【編集方針: Evidence Compression(Lossless Editing)】
方針: "Evidence is thick backstage, light on air." 以下の許可された編集だけを行い、
実際に読み上げられる文章(spoken layer)の負荷を軽くしてください。

【許可される編集】
- 不要な出典名の削除(企業名・調査会社名・研究機関名・メディア名・イベント名を、
  "a survey" "some companies" "one report" 等へ一般化する。ただし、その固有名詞を
  聞くこと自体がStory理解に必要な場合は残してよい)
- 近似・重複する数字の削減(意味が変わらない範囲で、複数の似た数値の並列を
  1つの傾向表現へ圧縮する。ただし、56% → 40% → 約1/3のような、トレンドの
  大きさ・方向そのものを理解するために必要な核心的な比較は残す)
- 学習者の理解に不要な日付・数値の削減・一般化(ER-008-N8-FINAL-CONTENT-
  COMPRESSION-RETRY-22で追加。例えば「発表した日付」と「実際に始まった日付」の
  ように複数の日付が並ぶ場合や、聴取理解に不要な細かい数値がある場合、本当に
  必要なものだけを残し、残りは削除するか"earlier this year"のように一般化する。
  「日付は必ず1個にする」「数字は必ず削る」という機械的なhard ruleではない。
  以下のいずれかに該当する日付・数値は残してよい: (a) 出来事の前後関係(どちらが
  先に起きたか)の理解に必要、(b) ニュースの核心(何が・いつ変わったか)を伝える
  のに必要、(c) Factの特定や裏付け(のちに聞き手や編集者が元の出来事を特定できる
  こと)に必要。判断に迷う場合はFact safetyを優先し、残す方を選ぶこと。日付・
  数値を一般化・削除しても、下記【絶対に行ってはいけない編集】の時系列
  (temporal direction)や比較の向きは変えないこと(例: 2つの日付のうち片方だけを
  残す場合、残す方の日付が「どちらが先か」を誤解させる書き方にしない)
- 学習者の理解に不要な地名・空港名・施設名等の一般化(ER-008-N8-FINAL-
  PRODUCTION-HARDENING-23で追加。例えば正式なfull nameの空港名・施設名が
  記事中に登場する場合、"Dallas Fort Worth International Airport"のような
  詳細な正式名称を、"Dallas Fort Worth"やより一般的な"a major U.S. airport"
  "one airport"のような表現へ短縮・一般化してよい。これも「地名は必ず削除
  する」という機械的なhard ruleではない。以下のいずれかに該当する場合は、
  詳細な地名・施設名を残してよい: (a) その場所自体がニュースの主体・核心
  であり、どこで起きた出来事かを理解することがStory理解に必要、(b) 学習者
  にとって聞き取り練習として意味のある固有名詞である、(c) Factの特定や
  裏付けに必要。判断に迷う場合はFact safetyを優先し、残す方を選ぶこと。
  地名・施設名を一般化・削除しても、その場所が指す地理的な意味(どこの国・
  都市か等)や、出来事の主体・事実関係を変えないこと
- spoken wordingの簡素化(同じ意味をより自然に短く言い換える)

数字は機械的に削除しないでください。変化の大きさ・方向そのものがStory理解に
必要な比較は残してください。

【絶対に行ってはいけない編集(Fact safety、最優先)】
- Factの追加
- Factの削除
- 相関(correlation)を因果(causation)へ変えること("was associated with"を
  "causes"/"leads to"/"because"のような断定へ言い換えない)
- certainty(確からしさ)を強めること
- 不確実性の表現(uncertainty/hedging、例: "a connection, not proof")を削ること
- 主張が及ぶ範囲(scope)を広げること(「一部の企業」を「多くの企業」「企業全体」
  のように広げない)
- 否定(negation)の有無を変えること
- 比較の向き(comparison direction、どちらが大きい/多いか)を変えること
- 出来事の時系列の前後関係(temporal direction)を変えること
- Point One/Point Twoの意味・役割(本文とは別の切り口を示す)を変えること
- Storyの論旨・構成を書き換えること(Title・Main Story・###見出し2つ・
  In One Lineの構成は維持する)

EditorはWriterではありません。「より良い記事に自由に書き直す」のではなく、
「意味を保ったまま聴取負荷を下げる」ことだけを行ってください。

【出力形式】
編集後の記事全文を、入力と全く同じMarkdown構造(# Title、Main Story、###見出し
2つ、## In one lineの結び)で出力してください。説明文やコメントは付けず、
編集後の記事本文だけを出力してください。"""

_EC_FORBIDDEN_EDITS_MARKER = "【絶対に行ってはいけない編集(Fact safety、最優先)】"
assert _EC_FORBIDDEN_EDITS_MARKER in _EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE_BASE, \
    "Evidence Compression Editor Promptのmarkerが見つかりません(構造変更を検知)"

_EC_PATTERN_A_PRECISION_INSERTION = (
    EVIDENCE_COMPRESSION_PURPOSE_BLOCK_EN + "\n\n"
    + PATTERN_A_REPRESENTATIVE_METRIC_SUPPORTING_TREND_BLOCK + "\n\n"
    + LISTENER_FRIENDLY_NUMERIC_PRECISION_BLOCK + "\n\n"
)

EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE = _EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE_BASE.replace(
    _EC_FORBIDDEN_EDITS_MARKER, _EC_PATTERN_A_PRECISION_INSERTION + _EC_FORBIDDEN_EDITS_MARKER)


def run_lossless_editor(client, article_text: str, model: str) -> dict:
    """Baselineの記事本文(article_text)を渡し、Evidence Compression
    (方式C、Lossless Editing)を適用した編集後テキストを返す。
    Research/Evidence Pack/VFL/Fact Ledgerには一切触れない(article_text
    のみを入出力とする)。

    2026-09-04(ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-
    FINAL-CANDIDATE-AUDIO-21R): ユーザー正式採用のPattern A(Representative
    Metric + Supporting Trend)+ Listener-Friendly Numeric Precisionが
    EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATEへ常時組み込まれているため、
    本関数のcall site(初回生成・Diagnostic Full Retryとも共通の
    _generate_and_compress_article()経由)は変更不要。"""
    prompt = EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text=article_text)
    resp = client.responses.create(
        model=model,
        reasoning={"effort": "medium"},
        input=[{"role": "developer", "content": EVIDENCE_COMPRESSION_EDITOR_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    edited_text = resp.output_text.strip()
    return {
        "prompt": prompt, "raw_text": edited_text, "model": resp.model, "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
    }
