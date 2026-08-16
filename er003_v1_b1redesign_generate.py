# ============================================================
# er003_v1_b1redesign_generate.py
# ER-003-B1-REDESIGN-TEST-01: IRAN01固定でB1 News EnglishのDifficulty
# Calibration(B1-A / B1-B、Scaffoldなし・TTSなし)
# ============================================================
# 新しいResearch・新しいFact Ledgerは作らない。既存IRAN01の
# 共通Fact Ledger・B2既存本文(Story Core)・A2既存本文(参考のみ)を
# 固定して使用する。B2/A2本文は一切書き換えない。
#
# B1-A: Minimal Cognitive Load Reduction(従来B1路線、明らかに負荷の
#       高い箇所のみ限定的に修正)
# B1-B: Reduced Cognitive Load / Natural News(A2のCognitive Load
#       Reductionの考え方をB1向けに弱めて適用した本命候補)
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1redesign_generate.py

from __future__ import annotations

import json
import os

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_iran01_articles_generate as gen

OUT_DIR = "er003_output/b1redesign_test_01/IRAN01"
B2_PATH = f"{gen.OUT_DIR}/b2/article.md"
A2_PATH = f"{gen.OUT_DIR}/a2/article.md"
LEDGER_PATH = gen.LEDGER_TEXT_PATH
TOPIC = gen.TOPIC

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

POINT_TARGET_LOWER, POINT_TARGET_UPPER = 30, 60
POINT_TOLERANCE_LOWER, POINT_TOLERANCE_UPPER = 25, 70


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


COMMON_INSTRUCTION = """このB2記事と同じFact・central story・chronology・attributionを保ったまま、
以下の方針でB1版のNews English本文を新たに書いてください。

【記事構成(B2と同じ形式、厳守)】
1. Title(#見出し)
2. Main Story(本文、複数段落)
3. Markdownの「###」見出しをちょうど2つ(Point One相当、Point Two相当)
4. 「## In one line…」見出しの後に結びの英文(1〜2文)

【B1共通方針(重要)】
- Adult-news Englishを維持する。大人向けニュースとして自然であること。
  教材調・子供向け英語・teacher-likeな説明文にしない。
- Vocabulary: 従来B1の考え方を基本的に踏襲するが、「B1 vocabularyのみ」
  という機械的なhard ruleにはしない。sanctions/sovereignty/Strait of
  Hormuz/ceasefire/diplomatic relations等、ニュース理解に不可欠な重要語は、
  無理に不自然な簡単語へ置き換えず残してよい。その代わり、難しい
  キーワードの周辺構文を易しくする。
- Grammar: passive voice/relative clause/present perfect/subordinate
  clauseそのものを禁止しない。ただし、複数の文法処理を一文にnestedさせて
  Listening負荷を高くしない。制御対象は「grammar itemの有無」ではなく
  「grammar processing load」である。
- 以下のような機械的hard limitは一切設定しない: 一文○語以下、使用語彙○語
  以内、relative clause禁止、passive禁止、一文一Fact絶対、CEFR word list
  外禁止。平均文長等は事後のdiagnostic metricとして測るのみで、生成時の
  hard ruleにはしない。
- B2記事の各文を1対1で単純に易しい語へ置換しない。難しい箇所は、同じ
  Fact/Story Coreからpassage単位で組み直してよい。
- Fact Ledgerに存在しない新しいcausal relationship/motive/interpretation/
  chronologyを追加しない。
- 主要Fact・central story・chronology・attributionはB2と変更しないが、
  Listening easeのためにFactの提示順を変えてもよい。

【Point One / Point Two】
既存ガイド(target 30〜60語、tolerance 25〜70語)を使用する。Pointは
第二の本文にしない。役割はbackground/implication/another angle/useful
context等であり、本文の単純な再説明にしない。新規に書いてよい。

【In One Line】
本文に対応する形で新規に書く。単なるタイトルの言い換えや情報過多に
しない。
"""

B1_A_INSTRUCTION = """【B1-A固有の方針: Minimal Cognitive Load Reduction】
基本思想: 従来のB1らしい自然なニュース英文を基本として維持する。ただし、
Listeningで明らかに処理しづらい箇所だけ修正する。simple subordinate
clause等は自然なら残してよい。

主な操作(必要な箇所にのみ適用、機械的に全文へ適用しない):
1. Heavy clauseのみ分割: 複数clauseが重なり、Listening時に構造保持が
   難しい場合のみ文を分割する。
2. Long-distance dependencyを必要時のみ短縮: 主語と動詞が遠すぎる場合や、
   長い挿入句がある場合に限り再構築する。
3. Difficult nominalizationを必要時のみ動詞化: ニュースとして自然なら
   nominalization(名詞化表現)を残してよい。理解を阻害するものだけ
   動詞表現へ変更する。
4. Logical relationを必要時のみ明示: 因果・対比・timelineがListeningで
   取りづらいところのみ、But/At the same time/Earlier/For now等を使用
   する。機械的にtransitionを増やさない。
5. Story structureはB2を比較的多く維持する: B2のNarrative flowを大きく
   再設計しない。ただしsentence-by-sentence単純置換にはしない。必要なら
   passage単位で軽くrebuildしてよい。

今回のA/B比較における位置づけ: conservative / lighter intervention。"""

B1_B_INSTRUCTION = """【B1-B固有の方針: Reduced Cognitive Load / Natural News(本命候補)】
基本思想: A2 V2改1で有効だった「Listening時に一度に処理する情報量を
減らす」という考え方をB1へ適用する。ただしA2ほど大胆に簡略化しない。
ニュースの情報量・自然さをより多く保持する。今回のA/B比較における
位置づけ: stronger listening-first intervention。

Difficulty Control:
1. Clause Density: 一文へ複数のFact/condition/contrast/attributionを
   詰め込みすぎない。基本イメージはone main idea + limited supporting
   detail。複雑なら2文以上へ分ける。
2. Long-distance dependency: Listening時に文頭情報を長く保持させない。
   長い挿入修飾やnested structureを積極的に分割する。例えば
   "The agreement, announced after several days of talks involving
   officials from both countries, could..." のような構造で負荷が高い
   場合、"Officials from the two countries held talks for several days.
   After those talks, they announced an agreement. The agreement
   could..." のように再構築してよい。ただし実際の記事Factに存在しない
   内容・因果を追加しない。
3. Abstract Noun Chains: 名詞化が連続してListening負荷を上げる場合は、
   必要に応じて動詞表現へ戻す(例: "the easing of sanctions" →
   "ease sanctions")。ただし機械的変換ruleにはしない。自然さとの
   バランスを見る。
4. Explicit Logical Flow: B2では文脈から推論させる因果・対比・timelineを、
   B1では必要に応じて少し明示する(But/At the same time/Earlier/That
   matters because.../For now...等)。ただし教科書的にtransitionを
   多用しない。
5. Concept Density: 短いpassageに複数の新概念を詰め込まない。一つの
   まとまりでは、one central idea + limited supporting detail程度を
   基本とする。異なる論点は順番に提示する。
6. Difficult Passage Rebuilding: B2の各sentenceを1対1で簡単にrewrite
   しない。難しい部分については、同じFact/Story Coreから、B1として
   passageそのものを組み直してよい。ただしFact Ledgerに存在しない、
   causal relationship/motive/interpretation/chronologyを追加しない。

【A2との境界(重要、A2そのものにしない)】
B1で維持したいもの: 自然なAdult-news feel、主要Factの情報量、必要な
ニュース語彙、一定程度の複文、一定程度の抽象表現、B1として意味のある
Listening challenge。
A2がより強く行うこと(B1-Bではそこまでしない): Cognitive Load
Reduction、Concept simplification、information selection、difficult
passage rebuilding、explicitness。

参考として、同じ記事のA2 V2改1版(このA2本文はB1-Bが目指す簡略化の
「上限」の参考例であり、これをコピー・模倣してはいけない。B1-Bは
これよりも情報量・複文・自然さを多く保つべき)を以下に示す。

【A2記事全文(参考、模倣禁止)】
{a2_full_text}
"""


def build_prompt(label: str, b2_full_text: str, ledger_text: str, specific_instruction: str) -> str:
    return f"""以下は、今回のB1 News English Difficulty Calibration検証のベースとなる、
既存のB2 Natural English記事全文です(Story Core、書き換え禁止)。

【B2記事全文】
{b2_full_text}

【今回のテーマ】
{TOPIC}

【Verified Fact Ledger(唯一のFact source of truth、新しいFactの追加禁止)】
{ledger_text}

{COMMON_INSTRUCTION}

{specific_instruction}
"""


def run_one_variant(client, label: str, prompt: str, ledger_text: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"[B1REDESIGN] {label}: writer呼び出し開始...")
    writer_result = vfl01.run_writer_with_technical_retry(client, prompt)
    with open(f"{out_dir}/audit/writer_attempts.json", "w", encoding="utf-8") as f:
        json.dump(writer_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if writer_result["status"] != "STRUCTURE_PASS" or not writer_result.get("raw_text"):
        print(f"[B1REDESIGN] {label}: writer失敗 status={writer_result['status']}")
        return {"label": label, "status": writer_result["status"], "article_text": None}

    article_text = writer_result["raw_text"].strip()
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)

    metrics = gen.compute_metrics(article_text)
    section_wc = gen.sf1r1.section_word_counts(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": POINT_TARGET_LOWER <= section_wc["point_one"] <= POINT_TARGET_UPPER,
        "point_one_within_tolerance": POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= POINT_TOLERANCE_UPPER,
        "point_two_within_target": POINT_TARGET_LOWER <= section_wc["point_two"] <= POINT_TARGET_UPPER,
        "point_two_within_tolerance": POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= POINT_TOLERANCE_UPPER,
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    print(f"[B1REDESIGN] {label}: metrics={metrics} sections={section_wc}")

    print(f"[B1REDESIGN] {label}: Ledger Deviation Check開始...")
    deviation_result = vfl01.run_deviation_check(client, ledger_text, article_text)
    print(f"[B1REDESIGN] {label}: deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    client = vfl01.get_client()

    b2_text = load_text(B2_PATH)
    a2_text = load_text(A2_PATH)
    ledger_text = load_text(LEDGER_PATH)

    results = {}

    prompt_a = build_prompt("B1-A", b2_text, ledger_text, B1_A_INSTRUCTION)
    results["B1-A"] = run_one_variant(client, "B1-A", prompt_a, ledger_text, f"{OUT_DIR}/b1_a")

    prompt_b = build_prompt("B1-B", b2_text, ledger_text, B1_B_INSTRUCTION.format(a2_full_text=a2_text))
    results["B1-B"] = run_one_variant(client, "B1-B", prompt_b, ledger_text, f"{OUT_DIR}/b1_b")

    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in results.items()},
                   f, ensure_ascii=False, indent=2, default=str)
    print("[B1REDESIGN] 完了。")
    for label, r in results.items():
        print(f"  {label}: status={r.get('status')} ledger_status={r.get('ledger_status')}")


if __name__ == "__main__":
    main()
