# ============================================================
# er003_v1_n3_01_advanced_adaptation_generate.py
# NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01
# ============================================================
# Advanced(Natural English Adaptation、CEFR B1、APPROVED_FOR_PRODUCTION)を
# 実際に生成するProductionモジュール。日本語の完成Entertainment記事
# (Original→R1→R2、本モジュールの入力は完成済みR2テキストのみ。R2生成
# 自体の配線は本タスク範囲外、CURRENT_SPEC.md行828 WIRING INCOMPLETE)
# から、CEFR B1向けのNatural English Adaptation記事を生成する単一責務の
# 生成関数を提供する。
#
# Prompt本文: `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`のarm3(Natural English、
# er015_output/news_ja_to_en_adaptation_trial_01/arms/arm3/prompt_
# developer.txt・出典er015_news_ja_to_en_adaptation_trial_01.py内の
# DEVELOPER/COMMON_BLOCK/ARM3_BLOCK定数)を逐語で流用する。ただし
# COMMON_BLOCKの「Preserve...」列挙(6項目)は、Meta記事(AI電話の裏に
# 人間、という特定記事のAngle)に固有のhard codingだったため、記事非依存の
# 一般形(opening expectation / reversal / central metaphor or
# storytelling device / order of information / ending)へ置換する
# (ADVANCED_COMMON_BLOCK_PREFIX/ADVANCED_COMMON_BLOCK_SUFFIXは元の
# COMMON_BLOCKの前後を一字一句保持し、中間の6項目bulletだけを
# ADVANCED_GENERAL_PRESERVE_BULLETSへ置換した構成)。DEVELOPER/ARM3_BLOCKは
# 完全に無変更(逐語)。sha256はこの3定数(DEVELOPER+PREFIX+SUFFIX+
# ARM3_BLOCK、置換された一般形bulletを除く「変更されていない部分」のみ)
# を対象にコード内定数で固定し、import時にfail-closedでassertする。
# Trial file(er015_news_ja_to_en_adaptation_trial_01.py)との一致確認は
# `er003_v1_n3_01_advanced_adaptation_generate_test_01.py`で行う
# (Trial scriptのimportはテストのみ、本Production moduleは一切importしない)。
#
# 既存Production contract(`# `Title+Main Story+ちょうど2つの`### `節+
# `## In one line`)は、`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`
# (er017_news_entertainment_production_line_trial_01.py CONTRACT_LINES、
# 出典は既存Production `er003_v1_n3_01_articles_generate.py`
# COMMON_BLOCK_TEMPLATE【記事構成】節の構造要件[Title/Main Story/
# ###×2/In One Line]、`er002_ja_free_markdown_restore_r2.
# validate_point_structure`が実際に検証する構造と一致))と全く同じ文言を
# 「区切られた接尾ブロック」(ADVANCED_CONTRACT_SUFFIX_LINES)として、
# Adaptation本文指示(COMMON_BLOCK/ARM3_BLOCK)の後・日本語記事本文の前に
# 追加する(Adaptation本文指示自体は一切変更しない)。
#
# API呼び出し・retry: `er003_v1_en_direct_vfl_01_generate`(vfl01)の
# `run_writer_with_technical_retry()`(既存primitive、構造Gate付きretry、
# NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01で追加した後方互換developer
# 引数を使用)をそのまま使う。fallbackモデルは既存Production
# (`er006_model_routing_contract_01.PROCESS_MODEL_MAP`)に定義が無いため
# 実装しない。model routing: `routing.require_model(
# "NATURAL_ENGLISH_ADAPTATION", routing.WRITER_MODEL)`。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_n3_01_advanced_adaptation_generate.py \
#       --ja-file <path> --out-dir <dir>
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from dataclasses import dataclass, field

from dotenv import load_dotenv

import er003_v1_en_direct_vfl_01_generate as vfl01
import er006_model_routing_contract_01 as routing

load_dotenv()

PROCESS_LABEL = "NATURAL_ENGLISH_ADAPTATION"

# ------------------------------------------------------------
# Prompt定数(NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 arm3、逐語+一般形置換)
# ------------------------------------------------------------
ADVANCED_DEVELOPER = (
    "You are an editor who adapts finished Japanese feature articles into "
    "natural English for listeners who are learning English."
)

# 元COMMON_BLOCK(trial定数)の「Preserve...」bulletより前の部分。無変更(逐語)。
ADVANCED_COMMON_BLOCK_PREFIX = (
    "Adapt the Japanese article below into English.\n"
    "\n"
    "Do not rewrite the article from scratch. Do not add new ideas, claims, "
    "background, general observations, examples, or facts that are not in "
    "the Japanese article. Preserve the Japanese article's editorial angle, "
    "structure, and sense of surprise:\n"
)

# 記事非依存の一般形(delegation D2: opening expectation / reversal /
# central metaphor or storytelling device / order of information /
# ending)。元trialのMeta記事固有6bullet(AI電話/人間/コンシェルジュ等の
# 具体的な語)を置換した部分(ここのみ新規、逐語ではない)。
ADVANCED_GENERAL_PRESERVE_BULLETS = (
    "- the opening expectation the article sets up at the beginning;\n"
    "- the reversal or turn partway through the story;\n"
    "- the central metaphor or storytelling device the article uses;\n"
    "- the order in which information and details are revealed;\n"
    "- the ending and how it resolves or lands the story.\n"
)

# 元COMMON_BLOCK(trial定数)の「Preserve...」bulletより後の部分。無変更(逐語)。
ADVANCED_COMMON_BLOCK_SUFFIX = (
    "Keep every fact exactly as in the Japanese article. Use short, simple "
    "English that a learner could understand by listening once.\n"
    "\n"
    "Output only the English title and the English body."
)

# arm3(NATURAL ENGLISH)block。無変更(逐語)。
ADVANCED_ARM3_BLOCK = (
    "Adaptation level: NATURAL ENGLISH.\n"
    "Make the piece read like a natural English news feature. Keep the "
    "central metaphor, the theme, the facts, the selection of information, "
    "and the conclusion. You may reorder, merge, or reshape paragraphs, and "
    "adjust the wording of metaphors where English needs it. Still add "
    "nothing that is not in the Japanese article."
)

# ------------------------------------------------------------
# 語彙ルール v2(ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01、2026-09-26、
# ユーザー正式決定によりAPPROVED_FOR_PRODUCTION)
# ------------------------------------------------------------
# 出典: `er015_output/advanced_vocab_rule_trial_01/v2/
# prompt_advanced_vocab_rule_v2_meta.txt`(fix01のv2、"v2の文言を正とする"
# というユーザー決定に基づく逐語ベース)。Trial(v1/v2)は「既存Advanced本文+
# 順位付き候補語リストを渡す改稿pass」だったが、本Production組み込みは
# 方式(i)(Standard v5と同型、Adaptation prompt本体へルール文言を追加する
# 直接生成、候補語リストなし=モデル自身の語感に依存)を暫定採用した
# (判断根拠: `docs/pm/recon_advanced_vocab_v2_wiring_01.md`、(ii)[改稿pass
# 追加]の要否は次回以降の通常Production Runでの観察後に判断、OPEN_ITEMS
# 残置)。v2固有の追加(引用符内の実際の呼称の扱い、C[固有名詞]の一種として
# 明確化)は含む。v3(Trial-02、Topic Core Word例外+Metaphor専用ルール)は
# ユーザーによりREJECTEDのため一切含まない。
#
# 逐語部分からの調整(候補語リスト/decisions出力schemaに依存する記述の
# 除去のみ、判定基準の文言自体は変更していない):
#   - 「Words that appear inside quotation marks...」段落から、
#     「even if it appears in the candidate list below」と「and mark it
#     "KEEP -- proper noun", explaining in reasoning that...」を除去した
#     (直接生成にはcandidate語リストもdecisions出力もないため)。
#   - decisions出力schema・candidate語リスト・BORDERLINE等の出力形式指示は
#     含めない(直接生成であり、改稿passのような語ごとの判定出力を要求
#     しないため)。
ADVANCED_VOCAB_RULE_V2_BLOCK = (
    "Vocabulary difficulty rule: words that rank below roughly the top "
    "12,000 most frequent general English words are, in principle, "
    "candidates for simplification. This is NOT a mechanical ban list. As "
    "with the existing Standard-level vocabulary policy, simplification "
    "should be strongly preferred only when a simpler, natural expression "
    "exists without harming meaning or naturalness; it must not be forced "
    "when it would.\n"
    "\n"
    "A word ranked beyond ~12,000 may still be KEPT (not simplified) if one "
    "of these applies:\n"
    "A. Its meaning can easily be guessed from an already-easy word it is "
    "built from (for example: \"onstage\" = on + stage, \"wastewater\" = "
    "waste + water, \"understandable\" = understand + -able). Do not "
    "exclude a word just because it LOOKS decomposable if the meaning "
    "cannot actually be guessed that way.\n"
    "B. It is a word that has become well established in Japanese, and its "
    "meaning can easily be guessed from its English pronunciation (for "
    "example: piano, curtain, privacy). Simply having a katakana spelling "
    "is not enough -- the word must be an established, commonly understood "
    "Japanese word, easily connected to its English sound.\n"
    "C. It is a proper noun (a person's name, a company or product name, a "
    "place name).\n"
    "D. Replacing it with an easier word would clearly hurt meaning "
    "precision or the naturalness of the English -- it is indispensable. Do "
    "not keep a word only because \"it is a technical term\" -- if a "
    "simple, natural, meaning-preserving substitute exists, simplify it.\n"
    "\n"
    "Words that appear inside quotation marks in the article, and titles, "
    "designations, or nicknames that a specific person or organization is "
    "reported to have actually used (for example, if the article states "
    "that Meta called certain workers \"human concierges\", the word "
    "\"concierges\" here is part of that reported fact, not an ordinary "
    "vocabulary choice) are facts of the article. Do not simplify such a "
    "word; treat it under exception C (a proper noun / quoted "
    "designation).\n"
    "\n"
    "Do NOT use \"it is part of a fixed expression / idiom\" as its own "
    "exception category. (For example, if \"curtain\" in \"behind the "
    "curtain\" is kept, the reason must be B [established Japanese "
    "loanword], never \"it is part of an idiom.\") A word inside a fixed "
    "expression that is still hard to guess should be judged normally, "
    "exactly like any other word."
)

ADVANCED_VOCAB_RULE_V2_SHA256 = (
    "d536f4b8a7780771232a95d35611606262d8041371ad8d0a1a4563b7948fb581"
)


def _compute_vocab_rule_v2_sha256() -> str:
    return hashlib.sha256(ADVANCED_VOCAB_RULE_V2_BLOCK.encode("utf-8")).hexdigest()


def _assert_vocab_rule_v2_sha256() -> None:
    actual = _compute_vocab_rule_v2_sha256()
    if actual != ADVANCED_VOCAB_RULE_V2_SHA256:
        raise RuntimeError(
            "[STOP] ADVANCED_VOCAB_RULE_V2_SHA256 mismatch: "
            f"expected={ADVANCED_VOCAB_RULE_V2_SHA256} actual={actual}. "
            "ADVANCED_VOCAB_RULE_V2_BLOCKがv2正式決定テキストと一致しません。"
        )


# Production contract接尾ブロック(NEWS-ENTERTAINMENT-PRODUCTION-LINE-
# TRIAL-01 CONTRACT_LINESと一字一句同一。出典コメント参照)。
ADVANCED_CONTRACT_SUFFIX_LINES = [
    "Write in English.",
    "Length: about 280–420 words in total.",
    "Format (Markdown): start with \"# \" followed by the title; then the "
    "main story; then exactly two \"### \" subsections, each 30–60 "
    "words, with headings that describe their content in your own words "
    "(do not use labels like \"Point One\"); then a final section headed "
    "exactly \"## In one line\" containing one sentence.",
]
ADVANCED_CONTRACT_SUFFIX = "\n".join(ADVANCED_CONTRACT_SUFFIX_LINES)

# sha256対象: 「変更されていない部分」のみ(DEVELOPER+PREFIX+SUFFIX+
# ARM3_BLOCK)。一般形bulletとcontract suffixはdelegationで明示的に
# 新規追加/置換された部分のため対象外(テストでその差分も別途確認する)。
# 値は本ファイル作成時に実測して埋め込んだ固定literal(下の
# _assert_unchanged_portion_sha256()がimport時にfail-closedで再計算と
# 比較する。一致しなければ定数がPrompt本文とズレていることを意味し、
# importそのものを失敗させる)。
ADVANCED_UNCHANGED_PORTION_SHA256 = (
    "05ce1a296b7239fcbd141e5bc9909aa11e8136c1e845e39d149f0c75e5203e00"
)


def _unchanged_portion_text() -> str:
    return (
        "DEVELOPER:\n" + ADVANCED_DEVELOPER + "\n\n"
        "COMMON_BLOCK_PREFIX:\n" + ADVANCED_COMMON_BLOCK_PREFIX + "\n\n"
        "COMMON_BLOCK_SUFFIX:\n" + ADVANCED_COMMON_BLOCK_SUFFIX + "\n\n"
        "ARM3_BLOCK:\n" + ADVANCED_ARM3_BLOCK
    )


def _compute_unchanged_portion_sha256() -> str:
    return hashlib.sha256(_unchanged_portion_text().encode("utf-8")).hexdigest()


def _assert_unchanged_portion_sha256() -> None:
    actual = _compute_unchanged_portion_sha256()
    if actual != ADVANCED_UNCHANGED_PORTION_SHA256:
        raise RuntimeError(
            "[STOP] ADVANCED_UNCHANGED_PORTION_SHA256 mismatch: "
            f"expected={ADVANCED_UNCHANGED_PORTION_SHA256} actual={actual}. "
            "DEVELOPER/COMMON_BLOCK_PREFIX/COMMON_BLOCK_SUFFIX/ARM3_BLOCKのいずれかが"
            "NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 arm3の逐語部分と一致しません。"
        )


_assert_unchanged_portion_sha256()  # import時にfail-closedで検証する
_assert_vocab_rule_v2_sha256()  # import時にfail-closedで検証する


def build_prompt(ja_article_text: str) -> str:
    common_block_general = (
        ADVANCED_COMMON_BLOCK_PREFIX + ADVANCED_GENERAL_PRESERVE_BULLETS +
        ADVANCED_COMMON_BLOCK_SUFFIX
    )
    return (
        common_block_general + "\n\n" + ADVANCED_ARM3_BLOCK + "\n\n" +
        ADVANCED_VOCAB_RULE_V2_BLOCK + "\n\n" +
        ADVANCED_CONTRACT_SUFFIX + "\n\n[Japanese article]\n" + ja_article_text
    )


# ------------------------------------------------------------
# cost計算(er003_v1_n3_01_standard_a2_generate.pyと同一ロジック、
# 独立実装。同じpricing snapshot/USD_JPYを踏襲する)
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
# 生成関数
# ------------------------------------------------------------
@dataclass
class AdvancedAdaptationResult:
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
    structure_status: str
    elapsed_seconds: float
    attempts_detail: list = field(default_factory=list)


def generate_advanced_adaptation(ja_article_text: str, *, client=None, model: str | None = None,
                                  max_attempts: int = 2) -> AdvancedAdaptationResult:
    """日本語完成Entertainment記事(R2)本文からAdvanced(CEFR B1、Natural
    English Adaptation)版を生成する。

    API呼び出しは`vfl01.run_writer_with_technical_retry()`(既存Production
    primitive)を再利用する。この関数は内部で`restore_r2.
    validate_point_structure()`によるcontract構造Gate(###見出しちょうど
    2つ、各body非空)付きretryを行う(max_attempts回、既定2=初回+1回)。
    fallbackモデルは定義しない(`routing.PROCESS_MODEL_MAP`に定義が無いため)。
    """
    if client is None:
        client = vfl01.get_client()
    requested_model = model or routing.require_model(PROCESS_LABEL, routing.WRITER_MODEL)

    prompt = build_prompt(ja_article_text)
    price_fn = _load_pricing()

    t0 = time.time()
    result = vfl01.run_writer_with_technical_retry(
        client, prompt, max_attempts=max_attempts, model=requested_model,
        developer=ADVANCED_DEVELOPER)
    elapsed = round(time.time() - t0, 3)

    if result["status"] not in ("STRUCTURE_PASS", "STRUCTURE_INVALID"):
        raise RuntimeError(
            f"[NATURAL_ENGLISH_ADAPTATION] {max_attempts}回試行しても生成に失敗しました: "
            f"status={result['status']} attempts={result['attempts']}"
        )
    if result["status"] != "STRUCTURE_PASS":
        raise RuntimeError(
            f"[NATURAL_ENGLISH_ADAPTATION] {max_attempts}回試行してもcontract構造"
            f"(### 見出しちょうど2つ)を満たせませんでした: attempts={result['attempts']}"
        )

    text = result["raw_text"]
    model_actual = result["model"]
    response_id = result["response_id"]
    attempts_detail = result["attempts"]
    attempts_count = len(attempts_detail)
    retried = attempts_count > 1

    fallback_detected = (model_actual != requested_model)

    usage_dict = result.get("usage") or {}
    input_tokens = usage_dict.get("input_tokens")
    cached_tokens = usage_dict.get("cached_input_tokens")
    output_tokens = usage_dict.get("output_tokens")

    cost_usd, cost_jpy = _compute_cost_jpy(
        price_fn, model_actual, input_tokens or 0, cached_tokens or 0, output_tokens or 0)

    return AdvancedAdaptationResult(
        text=text,
        model_id_actual=model_actual,
        model_id_requested=requested_model,
        response_id=response_id,
        usage=usage_dict,
        cost_usd=cost_usd,
        cost_jpy=cost_jpy,
        attempts=attempts_count,
        retried=retried,
        fallback_detected=fallback_detected,
        structure_status=result["status"],
        elapsed_seconds=elapsed,
        attempts_detail=[{k: v for k, v in a.items() if k != "raw_text"} for a in attempts_detail],
    )


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ja-file", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-attempts", type=int, default=2)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    with open(args.ja_file, encoding="utf-8") as f:
        ja_text = f.read()
    ja_sha256 = hashlib.sha256(ja_text.encode("utf-8")).hexdigest()

    client = vfl01.get_client()
    result = generate_advanced_adaptation(ja_text, client=client, max_attempts=args.max_attempts)

    out_text_path = os.path.join(args.out_dir, "advanced_adaptation.md")
    out_evidence_path = os.path.join(args.out_dir, "runtime_evidence.json")

    with open(out_text_path, "w", encoding="utf-8") as f:
        f.write(result.text)

    evidence = {
        "stage": "advanced_adaptation",
        "process_label": PROCESS_LABEL,
        "ja_file": args.ja_file,
        "ja_sha256": ja_sha256,
        "prompt_unchanged_portion_sha256": ADVANCED_UNCHANGED_PORTION_SHA256,
        "model_id_requested": result.model_id_requested,
        "model_id_actual": result.model_id_actual,
        "fallback_detected": result.fallback_detected,
        "response_id": result.response_id,
        "structure_status": result.structure_status,
        "usage": result.usage,
        "cost_usd": result.cost_usd,
        "cost_jpy": result.cost_jpy,
        "attempts": result.attempts,
        "retried": result.retried,
        "elapsed_seconds": result.elapsed_seconds,
        "attempts_detail": result.attempts_detail,
    }
    with open(out_evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2, default=str)

    print(f"[OK] advanced_adaptation written: {out_text_path}")
    print(f"[OK] runtime_evidence written: {out_evidence_path}")
    print(f"[COST] cost_jpy={result.cost_jpy} model_actual={result.model_id_actual} "
          f"attempts={result.attempts} retried={result.retried} "
          f"fallback_detected={result.fallback_detected}")


if __name__ == "__main__":
    main()
