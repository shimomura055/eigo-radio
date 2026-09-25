# ============================================================
# er003_v1_n3_01_standard_a2_generate.py
# NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01
# ============================================================
# Standard A2 v5(6,000語ライン+自然さ優先Prompt)をユーザーが正式採用
# (`APPROVED_FOR_PRODUCTION`、2026-09-25)したことを受けて実装する
# Productionモジュール。Advanced(Natural English Adaptation、CEFR B1)の
# 記事本文を入力として、CEFR A2向けのStandard版を生成する単一責務の
# 生成関数を提供する。
#
# 重要(未接続の事実、Gate 3参照): 本モジュール自体は「Advanced→
# Standard A2」の1生成呼び出しのみを実装する。日本語Entertainment記事
# (Original→R1→R2)→Advanced(Natural English Adaptation)という正式
# Production初回経路は、2026-09-25時点でCURRENT_SPEC.md上に存在しない
# (OPEN-177(1)参照。両工程ともTrialスクリプトのみで、Production module化
# されていない)。そのため本モジュールはどのrunnerからも呼ばれていない
# 「未接続」状態である。既存Production経路(B-Family Voices A2/B1、
# `er012_b_family_production_runner_01.py`等)はVerified Fact Ledger
# 必須の英語主体News生成経路であり、本Family(日本語Entertainment記事の
# 英語適応)とは入力・構造が異なるため接続先が存在しない。
#
# Prompt本文: ユーザーが2026-09-25に正式採用したv5 Prompt
# (`er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/
# prompt_standard_v5_6000.txt`)と一字一句同一(改行コードはCRLFだが、
# 内容は無変更)。STANDARD_A2_PROMPT_SHA256は、DEVELOPER/USER TEMPLATE
# 定数からTrial fileと同じ形式のテキストを再構成し、改行をLFへ正規化した
# 上でのsha256(理由: Windows上のTrial fileはCRLF保存だが、Pythonの
# 複数行文字列リテラルはLF固定であり、CRLF/LFの差はPrompt内容の差では
# ないため正規化して比較する)。このsha256一致検証は
# `er003_v1_n3_01_standard_a2_generate_test_01.py`で行う。Production実行
# 経路(本モジュールの通常呼び出し)はTrial fileにもTrialスクリプトにも
# 一切依存しない(定数はすべて本モジュール内にハードコードされている)。
#
# API呼び出し・retry・cost計算は、既存Production経路が実際に使っている
# 関数/設定をそのまま再利用する(重複実装しない):
#   - `er003_v1_en_direct_vfl_01_generate`(vfl01).get_client() / .MODEL
#     (= `er006_model_routing_contract_01.WRITER_MODEL`、B1/A2 Writerと
#     同一のApproved Model)。vfl01は`er012_b_family_production_runner_01.py`
#     や`er003_v1_n3_01_articles_generate.py`が実際にimportして使っている
#     既存Production依存モジュールである(ファイル名に"vfl_01"を含むが
#     Trial専用ではない)。
#   - vfl01.run_writer_no_search(): developer/userメッセージでの単発
#     Responses API呼び出し。空応答はRuntimeErrorを送出する既存関数。
#   - retry方針: run_writer_no_search()が空応答で例外を送出した場合のみ、
#     同一Promptで1回だけ再試行する(max_retries=1既定)。この
#     「空出力→1回再試行」方針は、既存Trial
#     (`er015_news_natural_advanced_standard_a2_trial_01._call_and_record`)
#     が採用している方針と同一だが、Trial importはせず本モジュール内に
#     独立実装する(delegation: Trial scriptをProductionからimportしない)。
#     fallbackモデルは既存Production(`er006_model_routing_contract_01.
#     PROCESS_MODEL_MAP`)に定義が無いため実装しない。
#   - model routing: `routing.require_model("STANDARD_A2_ADAPTATION",
#     routing.WRITER_MODEL)`(本タスクでPROCESS_MODEL_MAPへ新規追加。
#     値はWRITER_MODELと同一で新規モデル追加ではない)。
#   - cost計算: `er012_b_family_production_runner_01._load_pricing()`と
#     同一ロジック(pricing snapshot参照)を本モジュール内に独立実装する
#     (同一ファイル`er005_output/cost_baseline_01/pricing_snapshot.json`、
#     USD_JPY=160.0を再利用、重複ではなく既存Production runnerと同じ
#     計算式の踏襲)。
#
# 機械チェック(Ledgerを使わない簡易版、本モジュール内で独立実装。
# 既存Trialの`_fact_tokens`/`_strip_title`と同じ正規表現ベースの設計方針を
# 踏襲するが、Trial importはしない):
#   - タイトル行の存在(1行目が空でないこと)
#   - Advanced→Standardで数字トークン・固有名詞候補(文中で大文字始まりの
#     語)が追加/欠落していないか(diff、失敗しても自動で本文修正はしない)
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_n3_01_standard_a2_generate.py \
#       --advanced-file <path> --out-dir <dir>
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field

from dotenv import load_dotenv

import er003_v1_en_direct_vfl_01_generate as vfl01
import er006_model_routing_contract_01 as routing

load_dotenv()

PROCESS_LABEL = "STANDARD_A2_ADAPTATION"

# ------------------------------------------------------------
# Prompt定数(v5、ユーザー正式採用、2026-09-25、逐語)
# ------------------------------------------------------------
STANDARD_A2_DEVELOPER = (
    "You are an editor who rewrites English feature articles for learners "
    "of English at CEFR A2 level, while keeping the article just as "
    "enjoyable as the original."
)

STANDARD_A2_PROMPT_V5 = """Rewrite this entire article for CEFR A2 learners.
Simplify the English, not the story.

Rebuild the sentences. Do not just replace difficult words. Write every sentence again using simpler grammar and shorter structures.
Aim for an average sentence length of about 9–11 words across the whole article. Some sentences may be longer or shorter; do not force every sentence to the same length.
Use mostly one main idea per sentence. Split long clauses. Do not pack a cause, an extra detail, an exception, and a result into one sentence.
Prefer words within roughly the 6,000 most common English words.
If a word is clearly outside that range, replace it when a simpler natural alternative exists.
Do not force a replacement if it makes the sentence less natural or changes the meaning.
Proper names are excluded from this rule.
Essential technical terms may remain when a simpler equivalent would lose important meaning.
Do not add an explanation for a hard word; make the sentence around it simple instead.
Keep the metaphor words when they are simple enough for A2 learners (for example, stage, backstage, lead role, curtain).

Preserve the same story structure, the same interesting angle, the same surprise in the same place, the important metaphor or storytelling device, the same order of information, the same selection of facts, and the same ending logic.
Do not turn the article into a summary.
Do not remove an entertaining detail only because it is harder to express. Say it in simpler English instead.
Do not add new facts, new explanations, or new general observations.
Keep every fact exactly as it is: names, numbers, who did what, cause and effect, the order of events, negations, limitations, and words of scope such as "some" or "all".

The result must still sound natural when read aloud. Do not write like a children's book, and do not write a flat list of short sentences.

Output only the English title and the English body.

[Article]
{advanced_article}"""

# LF正規化済み("DEVELOPER:\n"+DEVELOPER+"\n\n"+"USER TEMPLATE (...):\n"+USER_TEMPLATE)
# のsha256。er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/
# prompt_standard_v5_6000.txt(CRLF保存)をLF正規化して読み込んだ場合と
# 一致することをテストで確認する。
STANDARD_A2_PROMPT_SHA256 = "cbb72357449dea9bcf0912c55aaf7e5b8ea52f6e157c37ae71180768dc13c589"


def reconstruct_prompt_file_text() -> str:
    """DEVELOPER/USER TEMPLATE定数からTrial file形式(LF正規化後)のテキストを
    再構成する。sha256照合専用(テストから呼ばれる)。Production実行経路
    (build_prompt/generate_standard_a2)では呼ばれない。"""
    return (
        "DEVELOPER:\n" + STANDARD_A2_DEVELOPER + "\n\n"
        "USER TEMPLATE ({advanced_article} is substituted):\n" +
        STANDARD_A2_PROMPT_V5
    )


def _assert_prompt_sha256() -> None:
    actual = hashlib.sha256(reconstruct_prompt_file_text().encode("utf-8")).hexdigest()
    if actual != STANDARD_A2_PROMPT_SHA256:
        raise RuntimeError(
            "[STOP] STANDARD_A2_PROMPT_SHA256 mismatch: "
            f"expected={STANDARD_A2_PROMPT_SHA256} actual={actual}. "
            "Prompt定数がv5正式採用テキストと一致しません。"
        )


_assert_prompt_sha256()  # import時にfail-closedで検証する


def build_prompt(advanced_article: str) -> str:
    return STANDARD_A2_PROMPT_V5.format(advanced_article=advanced_article)


# ------------------------------------------------------------
# cost計算(er012_b_family_production_runner_01._load_pricing()と
# 同一ロジック、独立実装)
# ------------------------------------------------------------
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0


def _load_pricing():
    with open(PRICING_SNAPSHOT_PATH, encoding="utf-8") as f:
        prices = json.load(f)["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == "Standard")
    return price


def _compute_cost_jpy(price_fn, model: str, input_tokens: int, cached_tokens: int,
                       output_tokens: int) -> tuple:
    billable_in = max((input_tokens or 0) - (cached_tokens or 0), 0)
    cost_usd = 0.0
    try:
        in_price = price_fn("openai", model, "input_tokens")
        cost_usd += (billable_in / 1_000_000) * in_price
    except StopIteration:
        pass
    if cached_tokens:
        try:
            cached_price = price_fn("openai", model, "cached_input_tokens")
            cost_usd += (cached_tokens / 1_000_000) * cached_price
        except StopIteration:
            pass
    if output_tokens:
        try:
            out_price = price_fn("openai", model, "output_tokens")
            cost_usd += (output_tokens / 1_000_000) * out_price
        except StopIteration:
            pass
    cost_jpy = cost_usd * USD_JPY
    return round(cost_usd, 6), round(cost_jpy, 4)


# ------------------------------------------------------------
# 機械チェック(Ledger不要の簡易版、独立実装)
# ------------------------------------------------------------
def strip_title(text: str) -> tuple:
    lines = (text or "").strip().splitlines()
    title = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip()
    return title, body


def extract_fact_tokens(text: str) -> dict:
    _, body = strip_title(text)
    numbers = sorted(set(re.findall(r"\b\d[\d,]*\b", body)))
    proper_nouns = sorted(set(re.findall(r"\b[A-Z][a-z]+\b", body)))
    return {"numbers": numbers, "proper_nouns": proper_nouns}


def run_checks(advanced_text: str, standard_text: str) -> dict:
    """数字・固有名詞候補の追加/欠落、タイトル行の存在を確認する
    (Ledger不要の簡易diff、自動で本文修正はしない)。"""
    checks_failed = []
    title, _ = strip_title(standard_text)
    if not title:
        checks_failed.append("MISSING_TITLE")

    adv_tokens = extract_fact_tokens(advanced_text)
    std_tokens = extract_fact_tokens(standard_text)

    numbers_missing = sorted(set(adv_tokens["numbers"]) - set(std_tokens["numbers"]))
    numbers_added = sorted(set(std_tokens["numbers"]) - set(adv_tokens["numbers"]))
    if numbers_missing:
        checks_failed.append("NUMBERS_MISSING")
    if numbers_added:
        checks_failed.append("NUMBERS_ADDED")

    proper_nouns_missing = sorted(set(adv_tokens["proper_nouns"]) - set(std_tokens["proper_nouns"]))
    # 固有名詞候補は簡易平易化(例: 一般名詞化)でも増減し得るため、
    # 欠落のみ記録し、失敗判定はしない(delegation: 6,000語超を必ず
    # 置換ではない/自然な平易化は許容)。追加は完全に新規の固有名詞
    # 導入である可能性があるため記録する。
    proper_nouns_added = sorted(set(std_tokens["proper_nouns"]) - set(adv_tokens["proper_nouns"]))

    return {
        "title": title,
        "checks_failed": checks_failed,
        "numbers_missing": numbers_missing,
        "numbers_added": numbers_added,
        "proper_nouns_missing_observed_only": proper_nouns_missing,
        "proper_nouns_added_observed_only": proper_nouns_added,
    }


# ------------------------------------------------------------
# 生成関数
# ------------------------------------------------------------
@dataclass
class StandardA2Result:
    text: str
    model_id_actual: str
    model_id_requested: str
    response_id: str
    usage: dict
    cost_usd: float
    cost_jpy: float
    attempts: int
    retried: bool
    fallback_detected: bool
    elapsed_seconds: float
    checks: dict = field(default_factory=dict)


def generate_standard_a2(advanced_text: str, *, client=None, model: str | None = None,
                          effort: str = "high", max_retries: int = 1) -> StandardA2Result:
    """Advanced(CEFR B1 Natural English Adaptation)記事本文からStandard
    (CEFR A2、v5 6,000語ライン+自然さ優先)版を生成する。

    API呼び出しは`vfl01.run_writer_no_search()`(既存Production依存
    モジュール)を再利用する。空応答は`vfl01.run_writer_no_search()`が
    RuntimeErrorを送出するため、それを捕捉してmax_retries回まで同一
    Promptで再試行する(既定1回)。fallbackモデルは定義しない
    (`routing.PROCESS_MODEL_MAP`に定義が無いため)。

    `effort`引数は`vfl01.REASONING_EFFORT`(= "high"、既存Production
    Writer/Support共通のreasoning effort)との整合を起動時に確認する
    ためだけに使う。vfl01.run_writer_no_search()はeffort引数を持たず
    モジュール既定のREASONING_EFFORTを常に使うため、呼び出し前に
    `effort`が`vfl01.REASONING_EFFORT`と一致することをassertする
    (不一致の場合はvfl01側のグローバル設定を勝手に書き換えず、
    ValueErrorとしてSTOPする)。
    """
    if effort != vfl01.REASONING_EFFORT:
        raise ValueError(
            f"[STOP] effort='{effort}'はvfl01.REASONING_EFFORT='{vfl01.REASONING_EFFORT}'と"
            "不一致です。vfl01.run_writer_no_search()はeffort引数を取らずモジュール既定値を"
            "常に使うため、呼び出し側で異なるeffortを指定することはできません。"
        )
    if client is None:
        client = vfl01.get_client()
    requested_model = model or routing.require_model(PROCESS_LABEL, routing.WRITER_MODEL)

    prompt = build_prompt(advanced_text)
    price_fn = _load_pricing()

    attempts = 0
    retried = False
    last_error = None
    result = None
    t0 = time.time()
    for attempt in range(1, max_retries + 2):  # 初回+max_retries回
        attempts = attempt
        try:
            result = vfl01.run_writer_no_search(
                client, prompt, model=requested_model, developer=STANDARD_A2_DEVELOPER)
            break
        except Exception as e:  # noqa: BLE001 - 既存run_writer_no_searchの例外方針に合わせる
            last_error = e
            if attempt < max_retries + 1:
                retried = True
                time.sleep(2)
                continue
            raise RuntimeError(
                f"[STANDARD_A2_ADAPTATION] {max_retries + 1}回試行しても生成に失敗しました: "
                f"{type(e).__name__}: {e}"
            ) from e
    elapsed = round(time.time() - t0, 3)

    text = result["raw_text"]
    model_actual = result["model"]
    response_id = result["response_id"]

    # ER-006-MODEL-ROUTING-CONTRACT-01: fallback未定義のため、実際の応答
    # modelがrequested_modelと異なる場合は観測のみ行い(fallback_detected)、
    # 自動修正・別呼び出しは行わない。
    fallback_detected = (model_actual != requested_model)

    # usage(トークン数)はvfl01.run_writer_no_search()の戻り値(本タスクで
    # 追加した"usage"キー、既存キーは無変更のbackward compatible拡張)から
    # 取得する。
    usage_dict = result.get("usage") or {}
    input_tokens = usage_dict.get("input_tokens")
    cached_tokens = usage_dict.get("cached_input_tokens")
    output_tokens = usage_dict.get("output_tokens")

    cost_usd, cost_jpy = _compute_cost_jpy(
        price_fn, model_actual, input_tokens or 0, cached_tokens or 0, output_tokens or 0)

    checks = run_checks(advanced_text, text)

    return StandardA2Result(
        text=text,
        model_id_actual=model_actual,
        model_id_requested=requested_model,
        response_id=response_id,
        usage=usage_dict,
        cost_usd=cost_usd,
        cost_jpy=cost_jpy,
        attempts=attempts,
        retried=retried,
        fallback_detected=fallback_detected,
        elapsed_seconds=elapsed,
        checks=checks,
    )


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--advanced-file", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-retries", type=int, default=1)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    with open(args.advanced_file, encoding="utf-8") as f:
        advanced_text = f.read()
    advanced_sha256 = hashlib.sha256(advanced_text.encode("utf-8")).hexdigest()

    client = vfl01.get_client()
    result = generate_standard_a2(advanced_text, client=client, max_retries=args.max_retries)

    out_text_path = os.path.join(args.out_dir, "standard_a2.md")
    out_evidence_path = os.path.join(args.out_dir, "runtime_evidence.json")

    with open(out_text_path, "w", encoding="utf-8") as f:
        f.write(result.text)

    evidence = {
        "stage": "standard_a2",
        "process_label": PROCESS_LABEL,
        "advanced_file": args.advanced_file,
        "advanced_sha256": advanced_sha256,
        "prompt_sha256": STANDARD_A2_PROMPT_SHA256,
        "model_id_requested": result.model_id_requested,
        "model_id_actual": result.model_id_actual,
        "fallback_detected": result.fallback_detected,
        "response_id": result.response_id,
        "effort_requested": "high",
        "usage": result.usage,
        "cost_usd": result.cost_usd,
        "cost_jpy": result.cost_jpy,
        "attempts": result.attempts,
        "retried": result.retried,
        "elapsed_seconds": result.elapsed_seconds,
        "checks": result.checks,
    }
    with open(out_evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2, default=str)

    print(f"[OK] standard_a2 written: {out_text_path}")
    print(f"[OK] runtime_evidence written: {out_evidence_path}")
    print(f"[COST] cost_jpy={result.cost_jpy} model_actual={result.model_id_actual} "
          f"attempts={result.attempts} retried={result.retried} "
          f"fallback_detected={result.fallback_detected}")
    print(f"[CHECKS] checks_failed={result.checks.get('checks_failed')}")


if __name__ == "__main__":
    main()
