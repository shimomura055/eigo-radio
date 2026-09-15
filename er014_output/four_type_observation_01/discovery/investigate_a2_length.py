# ============================================================
# er014_output/four_type_observation_01/discovery/investigate_a2_length.py
# 管理ID: USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY (Part 2: A2長さ調査)
# ============================================================
# 目的: Discovery A2記事(discovery/a2/article.md)が600語超級であるにも
# かかわらず「完成」と報告された経緯を、既存コード(CURRENT_SPEC.md/
# er003_discovery_focus_staged_production_01.py/
# er003_v1_n3_01_articles_generate.py)の実装を根拠に調査する。API呼び出し
# は一切行わない(決定的なテキスト解析のみ)。
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

DISCOVERY_DIR = "er014_output/four_type_observation_01/discovery"
A2_ARTICLE_PATH = f"{DISCOVERY_DIR}/a2/article.md"
A2_RUN_SUMMARY_PATH = f"{DISCOVERY_DIR}/a2/run_summary.json"
OUT_MD_PATH = f"{DISCOVERY_DIR}/a2_length_investigation.md"


# 既存の公式word_count算出ロジック(er003_v1_en_direct_ab_01_generate.
# compute_word_count、er003_v1_n3_01_articles_generate.compute_metricsが
# 内部で呼ぶものと完全同一のロジックをここへ複製して使う。新Validatorでは
# なく、既存の算出方法をそのまま再現する読み取り専用の診断)。
def compute_word_count_official(text: str) -> int:
    body = re.sub(r"^#{1,6}\s*.*$", "", text, flags=re.MULTILINE)
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", body)
    return len(words)


def compute_word_count_whole_file_naive(text: str) -> int:
    return len(text.split())


def main() -> None:
    with open(A2_ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()

    official_wc = compute_word_count_official(article_text)
    whole_file_wc = compute_word_count_whole_file_naive(article_text)

    run_summary = {}
    if os.path.exists(A2_RUN_SUMMARY_PATH):
        with open(A2_RUN_SUMMARY_PATH, encoding="utf-8") as f:
            run_summary = json.load(f)
    generation_time_wc = run_summary.get("word_count")

    TOTAL_SOFT_LOWER = 280
    TOTAL_SOFT_UPPER = 420

    report = {
        "task_id": "USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "a2_article_path": A2_ARTICLE_PATH,
        "word_count_official_body_only_excl_headings": official_wc,
        "word_count_whole_file_naive_incl_headings": whole_file_wc,
        "word_count_at_generation_time_run_summary_json": generation_time_wc,
        "total_soft_lower": TOTAL_SOFT_LOWER,
        "total_soft_upper": TOTAL_SOFT_UPPER,
        "current_vs_soft_upper_ratio": round(official_wc / TOTAL_SOFT_UPPER, 3),
        "over_soft_upper_by_words": official_wc - TOTAL_SOFT_UPPER,
    }

    md_lines = []
    md_lines.append("# Discovery A2 長さ調査(USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY Part 2)\n")
    md_lines.append(f"生成日時: {report['generated_at']}\n")
    md_lines.append("\n## 1. 現在のA2記事word count(正確な値)\n")
    md_lines.append(
        f"- 公式ロジック(`er003_v1_en_direct_ab_01_generate.py::compute_word_count`、"
        f"見出し[`#`行]を除外した本文のみ、`er003_v1_n3_01_articles_generate.py::compute_metrics`"
        f"が内部で使うのと完全同一のロジック)で算出: **{official_wc}語**\n")
    md_lines.append(f"- 参考(素朴な空白区切り、見出し込み全文): {whole_file_wc}語\n")
    md_lines.append(
        f"- 記事生成時点(`a2/run_summary.json`、Stage 1-3完了直後、F002/F009等のLocal Rewrite適用前)の"
        f"記録値: {generation_time_wc}語(その後のLocal Rewrite[F002 operator escalation等]で本文が"
        f"わずかに変化し、現在値{official_wc}語との差が生じている)\n")

    md_lines.append("\n## 2. 既存仕様上の根拠(soft target/hard capの有無)\n")
    md_lines.append(
        "### 2-1. CEFR-A2一般仕様(CURRENT_SPEC.md 541行目、ER-003-A2-SPEC-FREEZE-01、`DECIDED`)\n")
    md_lines.append(
        "> 全体語数 | 上限なし。**総語数を意図的に削らない**(B1と同等程度の主要情報量を保持) | "
        "上限なし(明示的にhard limitを設けない設計) | 上限なし(記録のみ、gateなし)\n\n"
        "この行は「全体語数に上限を設けない」ことを**意図的な設計**として明記した正式`DECIDED`仕様であり、"
        "実装漏れやバグではない。A2 Writer prompt本体(`er003_v1_n3_01_articles_generate.py`の"
        "`A2_KAI1_INSTRUCTION`)にも、総語数を積極的に削らない旨の指示が含まれる。\n")
    md_lines.append(
        "### 2-2. `TOTAL_SOFT_LOWER`/`TOTAL_SOFT_UPPER`(`er003_v1_n3_01_articles_generate.py` "
        "62-63行目)\n")
    md_lines.append(
        f"コード上には`TOTAL_SOFT_LOWER = {TOTAL_SOFT_LOWER}`・`TOTAL_SOFT_UPPER = {TOTAL_SOFT_UPPER}`という"
        "定数が存在し、非staged `run_one_pattern()`(同ファイル1018-1031行目、1197-1204行目の2箇所)では"
        "`length_report.json`へ`total_within_soft_range`(bool)として記録される。**ただしこれはgate/"
        "retryトリガーではなく、記録のみの診断フィールドであり、超過時にコンソール警告や完成報告への"
        "明示を行う実装は無い**(この2箇所とも、計算後に`print`されるのは`metrics`/`sections`の値のみで、"
        "`total_within_soft_range`がFalseであることを理由にした追加のprint/警告分岐は存在しない)。\n")
    md_lines.append(
        "### 2-3. Discovery Focus S2(staged production、本タスクのA2生成経路)の扱い\n")
    md_lines.append(
        "`er003_discovery_focus_staged_production_01.py::run_one_pattern_staged_discovery_focus()`は、"
        "Stage 1(Main Story)を`prod_gen.build_prompt(common_block, meta[\"instruction\"])`"
        "(=`A2_KAI1_INSTRUCTION`、非staged経路と同一命令文、総語数の上限指示なし)で生成し、Stage 3で"
        "Point One/Point Two各30-60語(許容25-70語、`POINT_TARGET_LOWER/UPPER`)の目標のみを課す。"
        "**Main Story本文(記事の大半を占める部分)には長さの目標が一切設定されていない。**さらに、"
        "`run_one_pattern_staged_discovery_focus()`内の最終結果構築(770-789行目)では"
        "`metrics = prod_gen.compute_metrics(article_text)`のみを呼び、非staged経路にある"
        "`length_report`(`total_within_soft_range`込み)の計算・保存(`metrics.json`/`length_report.json`"
        "書き出し)を一切行わない。実際、`discovery/a2/`ディレクトリには`metrics.json`も`length_report.json`"
        "も存在しない(`run_summary.json`にword_countのみ記録)。\n")

    md_lines.append("\n## 3. なぜ600語超級が「完成」と報告できたか(原因・gap)\n")
    md_lines.append(
        "1. **A2の全体語数には、そもそも公式のsoft target/hard capが存在しない**(2-1、`DECIDED`かつ意図的"
        "な設計)。したがって「上限を超えた」という判定自体が既存仕様上は成立しない。\n"
        "2. コード内に`TOTAL_SOFT_LOWER/UPPER`(280-420語)という診断定数は存在するが、(a)Discovery "
        "Focus S2のstaged生成経路では計算・記録すらされておらず、(b)計算される非staged経路でも"
        "record-onlyであり、超過時にconsole警告や完成報告への反映を行うコードが存在しない。\n"
        "3. 上記2点の結果、Stage 1-3完走・Fact Checker PASS・Ledger Deviation PASS・Point Overlap QA "
        "PASSという既存の各QAが全てPASSした時点で`status=\"OK\"`が返り、word_countはそのまま"
        "`run_summary.json`へ記録されるだけで、どのQAも「これは長い」という判定・警告を一切出さない。"
        "そのため、Fact/Ledger/Overlap各QAの観点では正当に「完成」であり、\"長さ\"という別軸のチェックが"
        "既存仕様に存在しないまま完成報告に至った。\n")

    md_lines.append("\n## 4. 「大幅超過時にユーザーへ明示」運用の既存仕様との整合判定\n")
    md_lines.append(
        "**未規定。** CURRENT_SPEC.mdのA2「全体語数」行(2-1)は「上限なし」を明記するのみで、"
        "超過時(あるいは非常に長い場合)にユーザーへ明示する運用契約は記載が無い。コード側にも"
        "(2-2/2-3で確認した通り)超過検知→警告print→完成報告への反映、という経路は存在しない。"
        "したがって「目安を大幅超過した場合は完成報告時に必ずユーザーへ明示する」という運用は、"
        "**既存仕様と矛盾はしないが、既存仕様として規定されてもいない**(新規の運用ルールとして"
        "追加する場合はユーザー判断が必要、Prompt/Validator変更は本タスクの禁止事項のため未実装)。\n")

    md_lines.append("\n## 5. 既存仕様内での自然な短縮可能性の判断\n")
    md_lines.append(
        f"現在の公式word count={official_wc}語は、コード内`TOTAL_SOFT_UPPER`({TOTAL_SOFT_UPPER}語)の"
        f"約{report['current_vs_soft_upper_ratio']}倍({report['over_soft_upper_by_words']}語超過)。"
        "しかし、この`TOTAL_SOFT_UPPER`はDiscovery Focus S2の生成経路(Main Story Writer prompt="
        "`A2_KAI1_INSTRUCTION`)には一切配線されておらず、Writer promptは逆に「総語数を意図的に削らない」"
        "と明記している(2-1)。すなわち、Discovery Focus S2には「既存の生成が実際に目指している/"
        "収束しやすいMain Story総語数のtarget」自体が存在しない。委任文の短縮候補生成条件"
        "(「既定のlength targetが存在し、同一Ledgerで再生成すれば目安内に収まる見込みがあるなら」)を"
        "満たす根拠が無い。既存経路を無変更のまま同一Ledgerで再実行しても、Main Story Writer promptに"
        "短縮を指示する仕組みが無いため、長さが目安内に収まる保証・見込みは無く(むしろ現状のprompt設計"
        "は非決定的な単なる再ロールに過ぎない)、これを「既存仕様内での自然な短縮」として実行するのは"
        "根拠薄弱と判断する。\n")
    md_lines.append(
        "**結論: 短縮候補は生成しない(STOP)。** 新しいlength仕様(Main Story本文へのsoft target配線、"
        "またはrigid hard cap)を追加すればDiscovery Focus S2でも短縮を狙えるが、これは本タスクの禁止"
        "事項(新Validator/新length仕様の追加、Prompt変更)に該当するため、本タスクでは実装しない。"
        "選択肢はユーザー判断に委ねる: (a) 現状の「A2全体語数には上限を設けない」既存`DECIDED`仕様を"
        "維持し、今回の604語はこの仕様の正常な結果として受け入れる、(b) Discovery Focus S2のMain Story "
        "Writerへも`TOTAL_SOFT_LOWER/UPPER`相当のsoft target(diagnostic、hard gateにはしない)を新規に"
        "配線するようProduction変更を正式検討する(要`APPROVED_FOR_PRODUCTION`)、(c) 完成報告の運用"
        "ルールとして「word countが目安を大幅超過した場合は完成報告時に明示する」を新たに追加する"
        "(Prompt/Validator変更を伴わない運用ルールのみの追加として、ユーザー承認があれば低リスク)。\n")

    md_lines.append("\n## 6. 根拠ファイル・行番号一覧\n")
    md_lines.append("- `CURRENT_SPEC.md` 541行目(A2全体語数=上限なし、`DECIDED`)\n")
    md_lines.append(
        "- `er003_v1_n3_01_articles_generate.py` 62-63行目(`TOTAL_SOFT_LOWER/UPPER`定義)、"
        "1018-1031行目・1197-1204行目(非staged経路のlength_report計算・保存、record-only)、"
        "606-615行目(`compute_metrics`)\n")
    md_lines.append(
        "- `er003_v1_en_direct_ab_01_generate.py` 77-80行目(`compute_word_count`公式ロジック)\n")
    md_lines.append(
        "- `er003_discovery_focus_staged_production_01.py` 92-94行目(`LEVELS`、A2は"
        "`A2_KAI1_INSTRUCTION`をそのまま使用)、156-165行目(Stage 1 Main Story Writer、length_report相当"
        "の計算なし)、461-462行目(Stage 3 Point One/Twoのみtargetがある)、770-789行目"
        "(`run_one_pattern_staged_discovery_focus`最終結果構築、`length_report`/`metrics.json`/"
        "`length_report.json`を生成しない)\n")
    md_lines.append(
        f"- 実測: `{A2_ARTICLE_PATH}`(現在の公式word_count={official_wc})、`{A2_RUN_SUMMARY_PATH}`"
        f"(生成時点word_count={generation_time_wc})、`discovery/a2/metrics.json`・"
        "`discovery/a2/length_report.json`は存在しない(staged経路が生成しないため)\n")

    with open(OUT_MD_PATH, "w", encoding="utf-8") as f:
        f.writelines(md_lines)
    with open(f"{DISCOVERY_DIR}/a2_length_investigation_data.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[A2-LENGTH-INVESTIGATION] official_word_count={official_wc} "
          f"(soft_range={TOTAL_SOFT_LOWER}-{TOTAL_SOFT_UPPER}, ratio={report['current_vs_soft_upper_ratio']}) "
          f"-> {OUT_MD_PATH}")


if __name__ == "__main__":
    main()
