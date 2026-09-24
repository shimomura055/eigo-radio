# ============================================================
# er015_news_meta_english_only_trial_01.py
# NEWS-META-ENGLISH-ONLY-TRIAL-01 (ユーザー指示、2026-09-24)
# ============================================================
# 目的: Meta Muse/AI電話記事のEntertainment性低下の主因が「英語化」なのか
# 「Production構造contract」なのかを切り分けるため、今回は「英語化だけ」を
# 単離するTrial。入力は`NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`条件2の
# 日本語素材(2文・209字)をそのまま逐語使用し、Web Search/Ledger/追加Source
# は一切使わない。維持するもの: Theme/元情報/Entertainment Promptの思想/
# Original->R1->R2/Luna/effort high/previous_response_id連鎖/Revision指示
# の意味/Fact safety。変えるのは出力言語(日本語->英語)だけ。
#
# Production構造(Point One/Point Two/`###`/`## In one line`/280-420語
# target/B1構造/Verified Fact Ledger/Ledger Deviation Gate/Parser/
# Structure Validator/Key Phrase/Audio/Scaffold/TTS/Assembly)は一切
# 入れない。出力はTitle+Body only。R3は生成しない。新規Editorial ruleは
# 追加しない。Production実装ではない。
#
# 依存(いずれも無変更・import再利用のみ):
#   - er003_v1_en_direct_vfl_01_generate (vfl01): get_client, WRITER_MODEL, REASONING_EFFORT
#   - er005_cost_logger (cl): usage log install/logging_context
#   - er015_news_core_idea_editorial_trial_01 (er015base): response_meta,
#     _load_pricing, _price, USD_TO_JPY
#   - er015_news_iterative_entertainment_trial_02 (trial02): call_fresh,
#     call_with_previous_response_id(previous_response_id連鎖の実装、無変更)
#   - er015_news_original_baseline_repro_01 (repro01): WRITER_MODEL, WRITER_EFFORT
#
# 英語Prompt本体・R1/R2指示文はFable固定(delegation_log記載)。本ファイルは
# それを定数として保持するのみで、生成ロジックは既存Trialと同一パターン
# (previous_response_idで直前応答に連鎖、userメッセージとして修正指示文
# のみを送る)。
#
# サブコマンド(引数のみ、単一エントリポイント):
#   --stages 0,1,2 --out-dir <OUT>   : Stage別生成(冪等、--forceで再生成)
#   --assemble-only --out-dir <OUT>  : 生成済みStageからtitles/metrics/
#                                       fact_diff_machine/prompt_echo/
#                                       comparison.md/cost.jsonを組み立て
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base
import er015_news_iterative_entertainment_trial_02 as trial02
import er015_news_original_baseline_repro_01 as repro01

THEME_TAG = "NEWS_META_ENGLISH_ONLY_TRIAL_01"

WRITER_MODEL = repro01.WRITER_MODEL
WRITER_EFFORT = repro01.WRITER_EFFORT

# ------------------------------------------------------------
# 入力素材(NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01条件2、逐語。sha256で
# 一致確認する。日本語のまま使用し、翻訳しない[News]欄用)。
# ------------------------------------------------------------
COND2_SOURCE_PATH = os.path.join(
    "er015_output", "news_meta_source_volume_format_trial_01", "inputs", "cond2.md")
COND2_EXPECTED_SHA256 = (
    "4a2d9f899cc6083eb46cd006d8df1fdb02db10c23bdce020b7d6ee58bf903ecb")

# ------------------------------------------------------------
# 英語Prompt(Fable固定、delegation_log記載の文単位対応。P7の思想を維持し、
# Production構造contract[Point One/### /## In one line/280-420語target等]
# は一切含まない。[News]欄は条件2素材を日本語のまま逐語で挿入する。
# ------------------------------------------------------------
DEVELOPER_MESSAGE_EN = (
    "You are a writer who explains the news clearly and makes it enjoyable to read.")

# P7各文の英訳(文ごとの対応。prompt_alignment.mdへそのまま転記する)。
P7_SENTENCE_EN = {
    "s1": ('Turn the news below into a piece you might share with a friend, '
           'the way you\'d say "Hey, isn\'t this kind of interesting?"'),
    "s2": ("From the news, pick not the most surprising fact but the single most "
           "interesting way of looking at it, and build the piece around that. "
           "Use mainly the facts needed for that viewpoint; do not try to cover "
           "the whole story."),
    "s3a": ("Keep the tone natural and light. Do not write like a newspaper, "
            "a government document, or a school textbook."),
    "s3b": ("Rephrase difficult content in short, simple English. Aim for a "
            "level that a learner of English can understand by listening to "
            "it once."),
    "s4": ("If the news might look like something specific to a distant place "
           "only, show its connection to the reader's own life or to a larger "
           "social change, just once. But you don't need to force the story "
           "to feel bigger than it is."),
    "s5": "Stick strictly to the facts. Do not add fictional events or quotes.",
    "theme": ("Theme: I asked an AI to call a store for me, and it turned out "
              "a human was secretly on the line."),
    "length": "Length: about 350–450 words.",
    "output": "Output only the title and the body. Write in English.",
}

MATERIAL_JA = (
    "Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント"
    "「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する"
    "「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿"
    "で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、"
    "Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。"
)


def build_user_prompt_en() -> str:
    p = P7_SENTENCE_EN
    body = "\n\n".join([
        p["s1"],
        p["s2"],
        p["s3a"] + " " + p["s3b"],
        p["s4"],
        p["s5"],
        p["theme"],
        p["length"],
        p["output"],
    ])
    return body + "\n\n[News]\n" + MATERIAL_JA


USER_PROMPT_EN = build_user_prompt_en()

# R1/R2指示(英語。意味は既存P7/R2 Revision指示[trial01.REVISION_INSTRUCTIONS]
# と同一。日本語逐語も併記して保存する)。
REVISION_INSTRUCTIONS_EN = {
    "r1": "Revise this article to make it more entertaining, without changing the facts.",
    "r2": "Revise this article to make it even more entertaining, without changing the facts.",
}
REVISION_INSTRUCTIONS_JA_REFERENCE = {
    "r1": "この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。",
    "r2": "この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。",
}

STAGE_KEY = {0: "original", 1: "r1", 2: "r2"}
STAGE_FILE = {0: "en_original.md", 1: "en_revision1.md", 2: "en_revision2.md"}

# Fact機械観測用: 条件2素材(日本語)の対訳語として事前承認済みの語(委任文記載)。
ALLOWED_REFERENCE_TOKENS = {
    "Meta", "Muse", "Reuters", "Human", "Concierge", "Contract", "Staff",
    "Privacy", "Rolled", "Back", "New", "York", "September", "NEW", "YORK",
}

NUMBER_RE = re.compile(r"\d[\d,\.]*")
CAP_WORD_RE = re.compile(r"\b[A-Z][A-Za-z]*\b")
QUOTE_RE = re.compile(r'["“]([^"”]{1,200})["”]')

ECHO_PATTERNS = [
    r"Isn't this",
    r"kind of interesting",
    r"Here's something interesting",
    r"これ、ちょっと面白くない",
]


# ------------------------------------------------------------
# 共通ヘルパー
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


def _sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


# ------------------------------------------------------------
# generate: --stages 0,1,2
# ------------------------------------------------------------
def cmd_generate(out_dir: str, stages: list, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)

    # STOP条件チェック: 条件2素材を正確に再利用できるか(sha256一致)
    actual_sha256 = _sha256_of_file(COND2_SOURCE_PATH)
    if actual_sha256 != COND2_EXPECTED_SHA256:
        stop = {
            "stop_reason": "条件2素材を正確に再利用できない(sha256不一致)",
            "expected_sha256": COND2_EXPECTED_SHA256,
            "actual_sha256": actual_sha256,
            "source_path": COND2_SOURCE_PATH,
        }
        save_json(out_path(out_dir, "stop_reason.json"), stop)
        print(f"[STOP] sha256 mismatch: expected={COND2_EXPECTED_SHA256} actual={actual_sha256}")
        raise SystemExit(1)

    # 入力保存(逐語コピー)
    save_text(out_path(out_dir, "input_cond2.md"), load_text(COND2_SOURCE_PATH))
    save_json(out_path(out_dir, "input_cond2_sha256.json"), {
        "source_path": COND2_SOURCE_PATH,
        "expected_sha256": COND2_EXPECTED_SHA256,
        "actual_sha256": actual_sha256,
        "match": actual_sha256 == COND2_EXPECTED_SHA256,
    })

    # Prompt保存
    save_text(out_path(out_dir, "prompt_developer.txt"), DEVELOPER_MESSAGE_EN)
    save_text(out_path(out_dir, "prompt_user_stage0.txt"), USER_PROMPT_EN)
    save_text(out_path(out_dir, "prompt_r1.txt"),
              "English (sent to API):\n" + REVISION_INSTRUCTIONS_EN["r1"] +
              "\n\nJapanese (reference, not sent, same meaning as prior VALIDATED R1):\n" +
              REVISION_INSTRUCTIONS_JA_REFERENCE["r1"])
    save_text(out_path(out_dir, "prompt_r2.txt"),
              "English (sent to API):\n" + REVISION_INSTRUCTIONS_EN["r2"] +
              "\n\nJapanese (reference, not sent, same meaning as prior VALIDATED R2):\n" +
              REVISION_INSTRUCTIONS_JA_REFERENCE["r2"])
    _write_prompt_alignment(out_path(out_dir, "prompt_alignment.md"))

    install_logger(out_dir)
    client = vfl01.get_client()

    prev_id = None
    for stage in stages:
        stage_key = STAGE_KEY[stage]
        article_path = out_path(out_dir, STAGE_FILE[stage])
        meta_path = out_path(out_dir, f"api_meta_stage{stage}.json")
        if os.path.exists(article_path) and not force:
            print(f"[SKIP] existing: {article_path}")
            if os.path.exists(meta_path):
                prev_id = load_json(meta_path).get("response_id", prev_id)
            continue
        if stage == 0:
            response = trial02.call_fresh(
                client, DEVELOPER_MESSAGE_EN, USER_PROMPT_EN, WRITER_EFFORT,
                f"en_only_{stage_key}")
            prompt_for_meta = USER_PROMPT_EN
        else:
            instruction = REVISION_INSTRUCTIONS_EN[stage_key]
            response = trial02.call_with_previous_response_id(
                client, instruction, WRITER_EFFORT, prev_id, f"en_only_{stage_key}")
            prompt_for_meta = instruction
        text = response.output_text.strip()
        meta = er015base.response_meta(
            response, prompt_for_meta, DEVELOPER_MESSAGE_EN,
            extra={"stage": stage_key, "effort_requested": WRITER_EFFORT,
                   "chain_method": "fresh" if stage == 0 else "previous_response_id",
                   "previous_response_id": prev_id if stage != 0 else None},
        )
        save_text(article_path, text)
        save_json(meta_path, meta)
        prev_id = response.id
        print(f"[OK] stage{stage}({stage_key}): {len(text)}字/chars "
              f"model={meta['response_model_actual']} id={response.id}")


def _write_prompt_alignment(path: str) -> None:
    p = P7_SENTENCE_EN
    rows = [
        ("以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。",
         p["s1"], "(対応そのまま、差異なし)"),
        ("ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。"
         "その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。",
         p["s2"], "(対応そのまま、差異なし)"),
        ("語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。",
         p["s3a"], "(対応そのまま、差異なし)"),
        ("難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、"
         "音声で一度聞いて理解できる程度を目安にします。",
         p["s3b"], "(「日本語」→「English」、読者を「日本語学習中の外国人」→"
         "「Englishの学習者」に対応させた。情報量・目安は同一)"),
        ("遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化との"
         "つながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。",
         p["s4"], "(対応そのまま、差異なし)"),
        ("事実関係は厳守し、架空の出来事や発言は加えません。",
         p["s5"], "(対応そのまま、差異なし)"),
        ("テーマ：MetaのAI電話代行が、通話の一部を裏で人間スタッフに担当させる実験を行っている",
         p["theme"], "(PRODUCTION-LINE-TRIAL-01のTheme英訳から括弧内補足を除いたもの。"
         "情報量は前回日本語テーマ文と同一)"),
        ("長さ：800～1000字",
         p["length"], "[差異] 800〜1000字(日本語)の英語換算としてFable判断で"
         "about 350-450 wordsとした(Production 280-420語targetとは別、"
         "文字数→語数換算のみ)"),
        ("出力はタイトルと本文のみ。",
         p["output"], "[差異] 出力形式指定は同一意味。Write in Englishを"
         "追加して出力言語を明示した(Production構造contractの追加ではない)"),
    ]
    lines = ["# Prompt対照表(NEWS-META-ENGLISH-ONLY-TRIAL-01)", "",
             "| P7(日本語) | 英訳(本Trial) | 差異メモ |", "|---|---|---|"]
    for ja, en, note in rows:
        lines.append(f"| {ja} | {en} | {note} |")
    lines += ["", "## developer message",
              f"- 日本語(P7): あなたは日本語のニュースを分かりやすく面白く伝える書き手です。",
              f"- 英語(本Trial): {DEVELOPER_MESSAGE_EN}",
              "", "## [News]欄",
              "- 条件2素材は日本語のまま逐語で挿入(翻訳しない、素材を変えない)。",
              "", "## R1/R2 Revision指示",
              f"- R1英語: {REVISION_INSTRUCTIONS_EN['r1']}",
              f"- R1日本語(参考、既存VALIDATED指示と同一意味): {REVISION_INSTRUCTIONS_JA_REFERENCE['r1']}",
              f"- R2英語: {REVISION_INSTRUCTIONS_EN['r2']}",
              f"- R2日本語(参考、既存VALIDATED指示と同一意味): {REVISION_INSTRUCTIONS_JA_REFERENCE['r2']}"]
    save_text(path, "\n".join(lines))


# ------------------------------------------------------------
# assemble-only
# ------------------------------------------------------------
def _load_stage_texts(out_dir: str) -> dict:
    texts = {}
    for stage, fname in STAGE_FILE.items():
        p = out_path(out_dir, fname)
        if os.path.exists(p):
            texts[STAGE_KEY[stage]] = load_text(p)
    return texts


def _first_line_title(text: str) -> str:
    for line in text.split("\n"):
        line = line.strip()
        if line:
            return line.lstrip("#").strip()
    return ""


def _word_count(text: str) -> int:
    return len(text.split())


def _fact_diff_for_stage(text: str) -> dict:
    numbers = sorted(set(NUMBER_RE.findall(text)))
    cap_words = sorted(set(CAP_WORD_RE.findall(text)))
    quotes = QUOTE_RE.findall(text)
    cap_words_not_reference = [w for w in cap_words if w not in ALLOWED_REFERENCE_TOKENS]
    return {
        "numbers": numbers,
        "capitalized_words": cap_words,
        "capitalized_words_not_in_reference_list": cap_words_not_reference,
        "quoted_spans": quotes,
    }


def _prompt_echo_for_stage(text: str) -> dict:
    hits = {}
    for pat in ECHO_PATTERNS:
        hits[pat] = bool(re.search(pat, text, flags=re.IGNORECASE))
    return hits


def cmd_assemble(out_dir: str) -> None:
    texts = _load_stage_texts(out_dir)
    if not texts:
        print("[STOP] no stage texts found; run --stages first")
        raise SystemExit(1)

    titles = {k: _first_line_title(v) for k, v in texts.items()}
    save_json(out_path(out_dir, "titles.json"), titles)

    metrics = {k: {"char_count": len(v), "word_count": _word_count(v),
                    "paragraph_count": len([p for p in v.split("\n\n") if p.strip()])}
               for k, v in texts.items()}
    save_json(out_path(out_dir, "metrics.json"), metrics)

    fact_diff = {k: _fact_diff_for_stage(v) for k, v in texts.items()}
    save_json(out_path(out_dir, "fact_diff_machine.json"), fact_diff)

    prompt_echo = {k: _prompt_echo_for_stage(v) for k, v in texts.items()}
    save_json(out_path(out_dir, "prompt_echo.json"), prompt_echo)

    # comparison.md(生成完了後にのみ、日本語条件2R2/PRODUCTION-LINE英語R2を参照)
    ja_r2_path = os.path.join(
        "er015_output", "news_meta_source_volume_format_trial_01", "cond2_revision2.md")
    prod_line_en_r2_path = os.path.join(
        "er017_output", "news_entertainment_production_line_trial_01", "stage2_r2.md")
    ja_r2 = load_text(ja_r2_path) if os.path.exists(ja_r2_path) else "(ファイルなし)"
    prod_line_en_r2 = (load_text(prod_line_en_r2_path)
                        if os.path.exists(prod_line_en_r2_path) else "(ファイルなし)")

    lines = ["# comparison.md (NEWS-META-ENGLISH-ONLY-TRIAL-01)", "",
             "## 日本語Baseline(NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01 条件2 R2)", "",
             ja_r2, "", "---", "",
             "## English Original(本Trial)", "", texts.get("original", "(未生成)"), "", "---", "",
             "## English R1(本Trial)", "", texts.get("r1", "(未生成)"), "", "---", "",
             "## English R2(本Trial)", "", texts.get("r2", "(未生成)"), "", "---", "",
             "## (参考)NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01 英語R2"
             "(Production構造contractあり、原因切り分けの参考のみ)", "",
             prod_line_en_r2, ""]
    save_text(out_path(out_dir, "comparison.md"), "\n".join(lines))

    # cost.json
    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    pricing = er015base._load_pricing()
    luna_in = er015base._price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = er015base._price(pricing, "openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = er015base._price(pricing, "openai", "gpt-5.6-luna", "output_tokens")

    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    # 注: trial02.call_fresh/call_with_previous_response_id(cmd_generateが
    # import再利用)は内部でtrial02自身のTHEME_TAGをcl.logging_contextへ
    # 渡すため、3 callはそのthemeでraw_usage_log.jsonlに記録される
    # (source_volume_format_trial_01と同一の既知挙動)。
    entries = [e for e in entries if e.get("theme") in (THEME_TAG, trial02.THEME_TAG)]

    per_call = []
    total_usd = 0.0
    total_input = total_output = total_cached = 0
    for e in entries:
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        billable_in = max(it - ct, 0)
        usd = 0.0
        if luna_in is not None:
            usd += (billable_in / 1_000_000) * luna_in
        if luna_cached is not None:
            usd += (ct / 1_000_000) * luna_cached
        if luna_out is not None:
            usd += (ot / 1_000_000) * luna_out
        per_call.append({
            "stage": e.get("stage"), "input_tokens": it, "cached_input_tokens": ct,
            "output_tokens": ot, "elapsed_seconds": e.get("elapsed_seconds"),
            "usd": round(usd, 6),
        })
        total_usd += usd
        total_input += it
        total_output += ot
        total_cached += ct

    result = {
        "theme": THEME_TAG,
        "total_calls": len(entries),
        "per_call": per_call,
        "total_input_tokens": total_input,
        "total_cached_input_tokens": total_cached,
        "total_output_tokens": total_output,
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * er015base.USD_TO_JPY, 2),
        "usd_to_jpy": er015base.USD_TO_JPY,
        "budget_jpy": 10,
        "within_budget": round(total_usd * er015base.USD_TO_JPY, 2) <= 10,
    }
    save_json(out_path(out_dir, "cost.json"), result)

    print(f"[OK] assemble complete: titles/metrics/fact_diff_machine/prompt_echo/"
          f"comparison.md/cost.json written. total_jpy={result['total_jpy']} "
          f"within_budget={result['within_budget']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--stages", default=None,
                         help="comma-separated stage numbers, e.g. 0,1,2")
    parser.add_argument("--assemble-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.assemble_only:
        cmd_assemble(args.out_dir)
    else:
        if not args.stages:
            parser.error("--stages is required unless --assemble-only is given")
        stages = [int(s) for s in args.stages.split(",")]
        cmd_generate(args.out_dir, stages, args.force)


if __name__ == "__main__":
    main()
