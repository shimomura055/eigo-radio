# ============================================================
# er013_family_c_future_trial_08_run.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08
# ============================================================
# 目的: 5テーマ(home_robots/bci/memory/digital_twins/language)の自由生成
# Trialドライバ。flow(テーマごと): 中心アイデア1-3案+選定(LLM1回)
# -> Writer(v8契約、マーカー技術的retry最大1回=合計最大2回)
# -> Fact Safety 3層(CURRENT FACT 0件ならFact Checker A'の呼び出し自体を
#    skip、Plausibility Bridge/Imagined Futureの軽判定は従来どおり実施)
# -> 補助Story Spark評価(6軸)+人物数決定的カウント -> 比較Artifact。
#
# 既存er013_family_c_future_*_01〜07.py・er013_output/family_c_future_
# trial_01〜07*/は一切変更しない(read-only importでの再利用のみ)。
# SSOT・Git操作もこのファイルからは行わない。**Production採用・配線では
# ない**(Gate 1材料までのTrial、最大Status: VALIDATED)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er013_family_c_future_trial_08_run.py \
#       --themes home_robots,bci,memory,digital_twins,language \
#       --level a2 --budget-jpy 137.71
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er013_family_c_future_eval_08 as eval8
import er013_family_c_future_provocation_08 as prov8
import er013_family_c_future_qa_01 as fcq1
import er013_family_c_future_qa_02 as fcq2
import er013_family_c_future_safety_06 as safety6
import er013_family_c_future_trial_06_run as trial06  # read-onlyでの再利用(home_robots/bciのtheme_label_en・inspiration_note・費用集計)
import er013_family_c_future_writer_08 as writer8
import er003_v1_en_direct_vfl_01_generate as vfl01

# ------------------------------------------------------------
# 費用ガード
# ------------------------------------------------------------
FAMILY_C_RESIDUAL_HARD_CAP_JPY = 137.71  # 委任文記載、変更不可(Family C残額ハード上限)
PER_RUN_SOFT_TARGET_JPY = 35.0  # 委任文の想定合計目安(5記事合計¥20-35)、超過は警告のみ

MAX_WRITER_ATTEMPTS = 2  # 原則1回+マーカー崩れ時の技術的retry最大1回(委任文の「大量再生成禁止」)
WRITER_REASONING_EFFORT = vfl01.REASONING_EFFORT  # "high"(記事本文の質を優先)
JUDGE_REASONING_EFFORT = "medium"  # 中心アイデア/補助評価/Safety軽判定はmediumでコスト抑制

# ------------------------------------------------------------
# テーマ設定(home_robots/bciはtrial06.THEME_CONFIGのtheme_label_en/
# inspiration_noteのみ再利用し、ledgerは今回使わない[CURRENT FACT完全禁止の
# ためledgerをWriterへ渡す必要がない]。新テーマ3本は新規定義)。
# ------------------------------------------------------------
THEME_ORDER = ["home_robots", "bci", "memory", "digital_twins", "language"]

THEME_CONFIG_08 = {
    "home_robots": {
        "theme_label_en": trial06.THEME_CONFIG["home_robots"]["theme_label_en"],
        "topic_ja_placeholder": trial06.THEME_CONFIG["home_robots"]["topic_ja_placeholder"],
        "inspiration_note": trial06.THEME_CONFIG["home_robots"]["inspiration_note"],
    },
    "bci": {
        "theme_label_en": trial06.THEME_CONFIG["bci"]["theme_label_en"],
        "topic_ja_placeholder": trial06.THEME_CONFIG["bci"]["topic_ja_placeholder"],
        "inspiration_note": trial06.THEME_CONFIG["bci"]["inspiration_note"],
    },
    "memory": {
        "theme_label_en": "the future of memory",
        "topic_ja_placeholder": "記憶の外部化・編集技術(future of memory)",
        "inspiration_note": (
            "A perfect memory is not comforting just because it never fades. It can be "
            "unsettling because it removes the quiet, natural work of forgetting -- and "
            "forgetting is often how a person moves on, forgives, or lets go of an old "
            "version of themselves."
        ),
    },
    "digital_twins": {
        "theme_label_en": "digital twins of ourselves",
        "topic_ja_placeholder": "自分自身のデジタルツイン(digital twins of ourselves)",
        "inspiration_note": (
            "A digital twin is not unsettling because it might get something wrong about "
            "a person. It can be unsettling because it might get something right -- "
            "reflecting back a version of someone they were not ready to see, or letting "
            "other people quietly prefer talking to the twin instead."
        ),
    },
    "language": {
        "theme_label_en": "the future of language",
        "topic_ja_placeholder": "リアルタイム翻訳・言語の未来(future of language)",
        "inspiration_note": (
            "Real-time translation does not just remove a barrier between languages. It "
            "can quietly remove the small, deliberate effort of choosing how to say "
            "something in someone else's language -- and that effort was often where real "
            "connection happened."
        ),
    },
}


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def budget_guard(stage_label: str, log_path: str, hard_cap_jpy: float, soft_target_jpy: float) -> dict:
    """総額ガード: trial_08全体(5テーマ合算、単一log_pathへappendされる)が
    ハード上限を超えたらここでSTOPする(各API呼び出し直後、次の段へ進む前に
    毎回チェックする)。"""
    total = trial06.compute_cost_jpy_for_log(log_path)
    print(f"[budget_guard][{stage_label}] Trial-08合算={total['total_jpy']} JPY "
          f"(ハード上限{hard_cap_jpy}, 目安{soft_target_jpy})")
    if total["total_jpy"] > hard_cap_jpy:
        raise RuntimeError(
            f"[budget_guard][{stage_label}] Trial-08合算 {total['total_jpy']} JPY が"
            f"Family C残額ハード上限{hard_cap_jpy} JPYを超過しました。"
            "STOP(以降のAPI呼び出しは行わない)。")
    if total["total_jpy"] > soft_target_jpy:
        print(f"[budget_guard][{stage_label}] 警告: 目安予算{soft_target_jpy} JPYを超過"
              "(ハード上限内のため続行、目安超過として記録)。")
    return total


# ------------------------------------------------------------
# Stage 1: 中心アイデア1-3案+選定(LLM 1呼び出し)
# ------------------------------------------------------------
def stage_core_idea(client, theme_id: str, theme_dir: str, theme_cfg: dict,
                     log_path: str, hard_cap: float, soft_target: float) -> dict:
    prompt = prov8.build_core_idea_prompt(theme_cfg["theme_label_en"], theme_cfg["inspiration_note"])
    save_text(f"{theme_dir}/core_idea_prompt.txt", prompt)
    model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="Trial-08: 自由生成Core Provocation(1-3案+選定)にA2_WRITER Approved "
                         "Model(Luna)を転用(新規process未定義、コスト影響なし、DEV/Trial限定)")
    with cl.logging_context(theme_id, "core_idea"):
        result = prov8.generate_core_idea(client, model, JUDGE_REASONING_EFFORT, prompt)
    selection = prov8.select_core_idea(result["parsed"])
    save_json(f"{theme_dir}/core_idea.json", {
        "parsed": result["parsed"], "selection": selection,
        "model": result["model"], "response_id": result["response_id"],
    })
    budget_guard("after_core_idea", log_path, hard_cap, soft_target)
    return selection


# ------------------------------------------------------------
# Stage 2: Writer(v8契約、マーカー技術的retryのみ最大1回)
# ------------------------------------------------------------
def generate_writer_with_marker_retry(client, theme_id: str, theme_dir: str, prompt: str) -> tuple:
    model = routing.require_model("A2_WRITER", routing.WRITER_MODEL)
    attempts = []
    for attempt in range(1, MAX_WRITER_ATTEMPTS + 1):
        with cl.logging_context(theme_id, f"writer_attempt{attempt}"):
            result = writer8.generate_family_c_article_v8(
                client, model=model, reasoning_effort=WRITER_REASONING_EFFORT, prompt=prompt)
        text_no_meta = fcq2.strip_meta_blocks(result["raw_text"])
        imagined_check = fcq1.validate_markers_balanced(text_no_meta)
        fact_check_balance = fcq2.validate_fact_markers_balanced(text_no_meta)
        balanced = imagined_check["balanced"] and fact_check_balance["balanced"]
        attempts.append({"attempt": attempt, "imagined_check": imagined_check,
                          "fact_check_balance": fact_check_balance, "response_id": result["response_id"]})
        if balanced:
            save_json(f"{theme_dir}/writer_attempts.json", attempts)
            return result["raw_text"], attempts
        print(f"[{theme_id}] Writer attempt {attempt}: マーカー不整合(technical retry)"
              f" imagined={imagined_check} fact={fact_check_balance}")
    save_json(f"{theme_dir}/writer_attempts.json", attempts)
    raise RuntimeError(f"マーカー整合の取れたWriter出力が{MAX_WRITER_ATTEMPTS}回の技術的試行でも"
                        "得られませんでした。STOP(NG_REVIEW_REQUIRED)。")


def stage_writer(client, theme_id: str, theme_dir: str, theme_cfg: dict, core_provocation: str,
                  log_path: str, hard_cap: float, soft_target: float) -> dict:
    prompt = writer8.build_family_c_writer_v8_prompt(
        core_provocation=core_provocation, theme_label=theme_cfg["theme_label_en"])
    save_text(f"{theme_dir}/writer_prompt.txt", prompt)
    article_text, attempts = generate_writer_with_marker_retry(client, theme_id, theme_dir, prompt)
    save_text(f"{theme_dir}/writer_raw_article.txt", article_text)
    layers = safety6.extract_layers(article_text)
    save_text(f"{theme_dir}/reader_facing_article.txt", layers["reader_text"])
    word_count = len(layers["reader_text"].split())
    fact_count = len(layers["fact_blocks"])
    save_json(f"{theme_dir}/word_count.json", {
        "word_count": word_count, "target": writer8.WORD_TARGET,
        "acceptable_range": list(writer8.WORD_ACCEPTABLE_RANGE),
        "within_acceptable_range": writer8.WORD_ACCEPTABLE_RANGE[0] <= word_count <= writer8.WORD_ACCEPTABLE_RANGE[1],
        "current_fact_marker_count": fact_count,
    })
    budget_guard("after_writer", log_path, hard_cap, soft_target)
    return {"article_text": article_text, "layers": layers, "word_count": word_count, "fact_count": fact_count}


# ------------------------------------------------------------
# Stage 3: Fact Safety 3層(CURRENT FACT 0件ならFact Checker A'をskip)
# ------------------------------------------------------------
_CURRENT_FACT_LEAK_PATTERNS = [
    r"\bin (19|20)\d{2}\b", r"\baccording to\b", r"\bstud(y|ies)\b", r"\bresearch(er|ers)?\b",
    r"\bsurvey(s|ed)?\b", r"\breport(s|ed)?\b", r"\b\d+(\.\d+)?\s?(million|billion|percent|%)\b",
]
_LEAK_RE = [re.compile(p, re.IGNORECASE) for p in _CURRENT_FACT_LEAK_PATTERNS]


def scan_current_fact_leak(reader_text: str) -> dict:
    """マーカー無しで現在事実が本文に紛れ込んでいないかの決定的grep(参考記録)。
    Fact Safety 3層のLLM軽判定を置き換えるものではない(追加の機械的確認)。"""
    hits = []
    for rx in _LEAK_RE:
        for m in rx.finditer(reader_text):
            hits.append({"pattern": rx.pattern, "match": m.group(0)})
    return {"leak_hits": hits, "leak_count": len(hits)}


def stage_safety(client, theme_id: str, theme_dir: str, theme_cfg: dict, layers: dict,
                  log_path: str, hard_cap: float, soft_target: float) -> dict:
    judge_model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="Trial-08: Plausibility Bridge/Imagined Future軽判定にA2_WRITER Approved "
                         "Model(Luna)を転用(新規process未定義、コスト影響なし、DEV/Trial限定)")
    fact_blocks = layers["fact_blocks"]
    if not fact_blocks:
        current_fact_result = {
            "skipped": True,
            "reason": "CURRENT FACT 0件(Trial-08限定skip)。Fact Checker A'の形式実行を行わない"
                      "(safety_06.run_current_fact_layerは無編集のまま、本run側で呼び出し自体をskip)。",
            "layer_pass": True,
        }
    else:
        with cl.logging_context(theme_id, "safety_current_fact_check"):
            current_fact_result = safety6.run_current_fact_layer(
                client, theme_id, theme_cfg["topic_ja_placeholder"], fact_blocks, "")
    with cl.logging_context(theme_id, "safety_plausibility_bridge"):
        bridge_result = safety6.run_plausibility_bridge_layer(
            client, judge_model, JUDGE_REASONING_EFFORT, layers["bridge_text"])
    with cl.logging_context(theme_id, "safety_imagined_future"):
        imagined_result = safety6.run_imagined_future_layer(
            client, judge_model, JUDGE_REASONING_EFFORT, layers["imagined_blocks"])
    overall_pass = current_fact_result["layer_pass"] and bridge_result["layer_pass"] and imagined_result["layer_pass"]
    leak_scan = scan_current_fact_leak(layers["reader_text"])
    result = {
        "current_fact_layer": current_fact_result,
        "plausibility_bridge_layer": bridge_result,
        "imagined_future_layer": imagined_result,
        "overall_pass": overall_pass,
        "current_fact_leak_scan": leak_scan,
    }
    save_json(f"{theme_dir}/safety_result.json", result)
    budget_guard("after_safety", log_path, hard_cap, soft_target)
    return result


# ------------------------------------------------------------
# Stage 4: 補助Story Spark評価(6軸)+人物数決定的カウント
# ------------------------------------------------------------
def stage_eval(client, theme_id: str, theme_dir: str, core_provocation: str, reader_text: str,
                log_path: str, hard_cap: float, soft_target: float) -> dict:
    prompt = eval8.build_eval_prompt(core_provocation, reader_text)
    save_text(f"{theme_dir}/eval_prompt.txt", prompt)
    model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="Trial-08: 補助Story Spark評価(6軸)にA2_WRITER Approved Model(Luna)を転用"
                         "(新規process未定義、コスト影響なし、DEV/Trial限定)")
    with cl.logging_context(theme_id, "story_eval"):
        eval_result = eval8.run_story_eval(client, model, JUDGE_REASONING_EFFORT, prompt)
    character_count = eval8.count_characters_heuristic(reader_text)
    listening_metrics = eval8.compute_listening_metrics(reader_text)
    combined = {"eval": eval_result, "character_count": character_count, "listening_metrics": listening_metrics}
    save_json(f"{theme_dir}/eval_result.json", combined)
    budget_guard("after_eval", log_path, hard_cap, soft_target)
    return combined


# ------------------------------------------------------------
# 1テーマをフルパイプラインで処理
# ------------------------------------------------------------
def process_one_theme(client, theme_id_for_log: str, theme_slug: str, out_root: str, theme_cfg: dict,
                       log_path: str, hard_cap: float, soft_target: float) -> dict:
    theme_id = theme_id_for_log  # cl.logging_context向けラベル(cost logのユニーク性確保)
    theme_dir = f"{out_root}/{theme_slug}"  # 出力ディレクトリは委任文どおりplainなテーマ名
    selection = stage_core_idea(client, theme_id, theme_dir, theme_cfg, log_path, hard_cap, soft_target)
    core_provocation = selection["selected"]["core_provocation"]
    writer_out = stage_writer(client, theme_id, theme_dir, theme_cfg, core_provocation,
                               log_path, hard_cap, soft_target)
    safety_result = stage_safety(client, theme_id, theme_dir, theme_cfg, writer_out["layers"],
                                  log_path, hard_cap, soft_target)
    eval_out = stage_eval(client, theme_id, theme_dir, core_provocation, writer_out["layers"]["reader_text"],
                           log_path, hard_cap, soft_target)
    return {
        "theme_cfg": theme_cfg, "selection": selection, "writer_out": writer_out,
        "safety_result": safety_result, "eval_out": eval_out,
    }


# ------------------------------------------------------------
# 比較Artifact(Title/Article全文/word count/登場人物数/Core Provocation 1行のみ)
# ------------------------------------------------------------
def extract_title_if_present(reader_text: str) -> tuple:
    """先頭行が短く(12語以下)、文末記号で終わっていなければタイトル行とみなす
    (ヒューリスティック。Writerへは『タイトルは物語に資する場合のみ、短く』とだけ
    指示しているため、タイトルの有無自体が結果として記録される)。"""
    lines = reader_text.strip().splitlines()
    if not lines:
        return None, reader_text
    first = lines[0].strip()
    rest = "\n".join(lines[1:]).strip()
    if rest and first and 1 <= len(first.split()) <= 12 and not first.endswith((".", "!", "?", ",")):
        return first, rest
    return None, reader_text


V7_REFERENCE_LINKS = {
    "Trial-07 home_robots (index)": "../family_c_future_trial_07/index.html",
    "Trial-07 bci (index)": "../family_c_future_trial_07/bci/index.html",
}


def _html_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_comparison_md(out_dir: str, results_by_theme: dict) -> None:
    md = ["# Trial-08 -- Freeform 5-theme Core Provocation Trial\n",
          "Trial専用、Production採用ではない。最大Status: VALIDATED。\n"]
    for theme_id, result in results_by_theme.items():
        reader_text = result["writer_out"]["layers"]["reader_text"]
        title, body = extract_title_if_present(reader_text)
        md.append(f"\n## {theme_id}\n")
        md.append(f"**Title**: {title or '(untitled)'}\n")
        md.append(f"**Core Provocation**: {result['selection']['selected']['core_provocation']}\n")
        md.append(f"word_count={result['writer_out']['word_count']} / "
                   f"characters(heuristic)={result['eval_out']['character_count']['estimated_total_characters']}\n")
        md.append("```\n" + body + "\n```\n")
    save_text(f"{out_dir}/comparison.md", "\n".join(md))


def build_index_html(out_dir: str, results_by_theme: dict) -> None:
    parts = ["""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Family C Trial-08 -- Freeform 5-theme</title></head>
<body style="font-family: sans-serif; max-width: 900px; margin: 2em auto; line-height: 1.6;">
<h1>Family C Trial-08 -- Freeform 5-theme Core Provocation Trial</h1>
<p><strong>Status: Trial only, NOT Production-approved (max Status: VALIDATED).</strong></p>
"""]
    for theme_id, result in results_by_theme.items():
        reader_text = result["writer_out"]["layers"]["reader_text"]
        title, body = extract_title_if_present(reader_text)
        cp = result["selection"]["selected"]["core_provocation"]
        wc = result["writer_out"]["word_count"]
        char_count = result["eval_out"]["character_count"]["estimated_total_characters"]
        parts.append("<div style='border:1px solid #ccc; padding:1em; margin-bottom:1.5em;'>")
        parts.append(f"<h2>{_html_escape(theme_id)}</h2>")
        parts.append(f"<p><strong>Title:</strong> {_html_escape(title or '(untitled)')}</p>")
        parts.append(f"<p><strong>Core Provocation:</strong> {_html_escape(cp)}</p>")
        parts.append(f"<p>word_count={wc} | characters(heuristic)={char_count}</p>")
        parts.append(f"<pre style='white-space: pre-wrap;'>{_html_escape(body)}</pre>")
        parts.append("</div>")

    parts.append("<h3>Reference: Trial-07 home_robots / bci (not regenerated)</h3><ul>")
    for label, path in V7_REFERENCE_LINKS.items():
        parts.append(f"<li><a href='{path}'>{_html_escape(label)}</a></li>")
    parts.append("</ul>")
    parts.append("<h3>Links</h3><ul>")
    parts.append("<li><a href='comparison.md'>comparison.md (full text of all 5 articles)</a></li>")
    parts.append("<li><a href='cost_summary.json'>cost_summary.json</a></li>")
    parts.append("</ul></body></html>")
    save_text(f"{out_dir}/index.html", "\n".join(parts))


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--themes", type=str, required=True,
                         help="comma-separated subset/order of: " + ",".join(THEME_ORDER))
    parser.add_argument("--level", choices=["a2"], default="a2")
    parser.add_argument("--budget-jpy", type=float, default=FAMILY_C_RESIDUAL_HARD_CAP_JPY)
    args = parser.parse_args()

    themes = [t.strip() for t in args.themes.split(",") if t.strip()]
    unknown = [t for t in themes if t not in THEME_CONFIG_08]
    if unknown:
        raise SystemExit(f"未知のテーマ: {unknown}(有効: {THEME_ORDER})")

    hard_cap = min(args.budget_jpy, FAMILY_C_RESIDUAL_HARD_CAP_JPY)

    out_root = "er013_output/family_c_future_trial_08"
    log_path = f"{out_root}/raw_usage_log.jsonl"
    cl.install(log_path)

    budget_guard("start", log_path, hard_cap, PER_RUN_SOFT_TARGET_JPY)

    client = vfl01.get_client()

    results_by_theme = {}
    for theme_id in themes:
        theme_id_for_log = f"family_c_future_trial_08_{theme_id}"
        results_by_theme[theme_id] = process_one_theme(
            client, theme_id_for_log, theme_id, out_root, THEME_CONFIG_08[theme_id],
            log_path, hard_cap, PER_RUN_SOFT_TARGET_JPY)
        print(f"[trial_08][{theme_id}] DONE. word_count={results_by_theme[theme_id]['writer_out']['word_count']} "
              f"fact_count={results_by_theme[theme_id]['writer_out']['fact_count']} "
              f"safety_overall_pass={results_by_theme[theme_id]['safety_result']['overall_pass']}")

    build_comparison_md(out_root, results_by_theme)
    build_index_html(out_root, results_by_theme)

    final_cost = trial06.compute_cost_jpy_for_log(log_path)
    save_json(f"{out_root}/cost_summary.json", final_cost)
    print(f"[trial_08] ALL DONE. themes={themes} cost={final_cost}")


if __name__ == "__main__":
    main()
