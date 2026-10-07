# -*- coding: utf-8 -*-
"""OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 Phase A: B3指示文バリアント(Trial専用DEV。Production経路ではない)。

- import時は何もしない。patched_b3_variant(variant) の with 内でのみ
  er019_family_x_storyline_b3_fact_selection_01.build_user_prompt を差し替え、終了時(例外含む)に必ず復元する。
- V0=現行(差し替えなし)。V1/V2/V3/V5/V6 は「現行userプロンプト(必要なら1箇所の置換) + 末尾に指示ブロック追記」。
- developer(system)メッセージ・JSON schema・Test定義は変更しない。
- 指示文は固有名・個別事例を含めない(過学習防止)。
"""
from __future__ import annotations

import contextlib
import hashlib

# 現行promptの該当句(er019 b3 USER_PROMPT_TEMPLATE 指示5内)。置換するvariantだけが使う。
BASE_PHRASE = "必要最小限のFactを簡潔にまとめた文章"

BLOCK_V1 = (
    "【Selected Factsの書き方: 主体・対象の保持】\n"
    "Selected Factsの各factは、台帳の文に書かれている「誰が(主体)」「誰に・何に(対象)」"
    "「数値や率が何に掛かるのか(掛かる先)」「方向を表す語(増える/減る、置き換える/撤回する等)」を、"
    "省略・再構成・別の語への置換をせずに書いてください。"
    "台帳の文で主体や対象が明示されていない場合は、補って書かず、台帳の文のとおり明示されないまま書いてください。"
    "この指示は「簡潔に」という指示より優先します(長くなっても構いません)。"
)

BLOCK_V2 = (
    "【Storyline行とbriefの構成: 単一因果】\n"
    "Storylineは、原因と結果が一つにつながる単一の因果を表す1文にしてください。"
    "別々のfactが持つ限定語・条件・範囲を1文の中で連結して一つの主張にしないでください。"
    "複数のfactを関係づける必要がある場合も、各factの主体と範囲が混ざらないよう、"
    "Selected Factsではfactごとに分けて書いてください。"
    "この指示は「簡潔に」という指示より優先します。"
)

# V5再定義(ユーザー決定2026-10-07, Opus M2): V3 + 未提示明記のみ。
# 旧案(逐語引用・fact_id・採用fact下限5・「採用の有無にかかわらず」・「簡潔に」句置換)は撤回。
BLOCK_V5_EXTRA = (
    "【未提示事項の明記】\n"
    "台帳に「未提示」「不明」「示されていない」「確認できない」と明記された事項"
    "(factの本文またはnumeric_scopeに書かれているもの)のうち、Storylineの主題に関わるものは、"
    "briefの末尾に「〜は示されていない」の形で明記してください。"
    "「〜とは書かない」という形の禁止notesは、この明記の対象に含めません。"
)

BLOCK_V6 = (
    "【最大簡潔モード】\n"
    "Selected Factsは、要点のみを短く書いてください。各factは1文以内とし、"
    "条件・補足・範囲の細部は、Storylineの理解に不可欠でない限り省いて構いません。"
    "言い換え・統合も自由です。この条件では、忠実さよりも簡潔さを優先します。"
)

# variant -> {"replace": [(old,new)...], "append": str}
VARIANTS = {
    "V0": {"replace": [], "append": ""},
    "V1": {"replace": [], "append": BLOCK_V1},
    "V2": {"replace": [], "append": BLOCK_V2},
    "V3": {"replace": [], "append": BLOCK_V1 + "\n\n" + BLOCK_V2},
    "V5": {
        "replace": [],
        "append": BLOCK_V1 + "\n\n" + BLOCK_V2 + "\n\n" + BLOCK_V5_EXTRA,
    },
    "V6": {
        "replace": [(BASE_PHRASE, "必要最小限のFactを、要点のみ短く言い換えてまとめた文章")],
        "append": BLOCK_V6,
    },
}
VARIANT_NAMES = tuple(VARIANTS)

# 固有名・テーマ語の禁止リスト(テストで検査)
FORBIDDEN_WORDS = [
    "Meta", "Muse", "Hormuz", "ホルムズ", "Trump", "トランプ", "衛星", "space", "Space", "宇宙",
    "下水", "AI", "海峡", "原油", "ロールバック", "20%", "20％", "米国", "日本", "松山",
]


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def _check_variant(variant: str) -> None:
    if variant not in VARIANTS:
        raise ValueError(f"variant不正: {variant!r} (許可: {VARIANT_NAMES})")


def instruction_sha(variant: str) -> str:
    _check_variant(variant)
    spec = VARIANTS[variant]
    material = "\n".join(f"{o}=>{n}" for o, n in spec["replace"]) + "\n---\n" + spec["append"]
    return sha256_text(material)


def apply_variant(base_prompt: str, variant: str) -> str:
    """現行promptにvariantを適用した全文を返す(純関数)。V0は恒等。"""
    _check_variant(variant)
    spec = VARIANTS[variant]
    out = base_prompt
    for old, new in spec["replace"]:
        if base_prompt.count(old) != 1:
            raise ValueError(f"置換対象句がpromptにちょうど1回存在しない: {old!r}")
        out = out.replace(old, new)
    if spec["append"]:
        out = out + "\n\n" + spec["append"]
    return out


@contextlib.contextmanager
def patched_b3_variant(variant: str, b3_module=None, sent_log=None):
    """with内だけ b3.build_user_prompt を差し替え。終了時(例外含む)に必ず元へ戻す。V0は差し替えなし(sent_log記録のみ)。"""
    _check_variant(variant)
    if b3_module is None:
        import er019_family_x_storyline_b3_fact_selection_01 as b3_module
    orig = b3_module.build_user_prompt
    try:
        if variant != "V0" or sent_log is not None:
            def wrapped(*a, **k):
                out = apply_variant(orig(*a, **k), variant)
                if sent_log is not None:
                    sent_log.append(sha256_text(out))
                return out
            b3_module.build_user_prompt = wrapped
        yield variant
    finally:
        b3_module.build_user_prompt = orig


def provenance(variant: str, full_prompt: str | None = None) -> dict:
    _check_variant(variant)
    return {
        "variant": variant,
        "instruction_sha256": instruction_sha(variant),
        "replace_pairs": [list(p) for p in VARIANTS[variant]["replace"]],
        "full_prompt_sha256": sha256_text(full_prompt) if full_prompt is not None else None,
    }
