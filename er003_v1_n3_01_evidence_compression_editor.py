# ============================================================
# er003_v1_n3_01_evidence_compression_editor.py
# ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06 Part A/B
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

from __future__ import annotations

EVIDENCE_COMPRESSION_EDITOR_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioの記事Editorです。既に完成しているPodcast台本(Markdown)を、"
    "意味を一切変えない範囲だけで軽量に編集します。新しいFactの追加や、主張の強さを"
    "変えることは禁止です。"
)

EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE = """【編集対象のPodcast台本(Markdown、そのまま編集してください)】
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
- 冗長なEvidence説明の削減
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


def run_lossless_editor(client, article_text: str, model: str) -> dict:
    """Baselineの記事本文(article_text)を渡し、Evidence Compression
    (方式C、Lossless Editing)を適用した編集後テキストを返す。
    Research/Evidence Pack/VFL/Fact Ledgerには一切触れない(article_text
    のみを入出力とする)。"""
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
