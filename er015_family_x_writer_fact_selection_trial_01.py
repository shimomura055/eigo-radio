# ============================================================
# er015_family_x_writer_fact_selection_trial_01.py
# NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-01 (Fable設計、2026-09-26)
# ============================================================
# 目的: 複数Source Researchの情報量を確保しつつ、Writerへ情報を見せすぎて
# 「情報詰め込み型」になる問題を、B案(Selected Fact Brief)で防げるかを
# 検証するTrial専用スクリプト。**Production実装ではない。Trialのみ、
# 最大VALIDATED、Production変更禁止(文章生成まで)。**
#
# 変数は「Writerへ見せる情報量・形式」だけ。Writer Prompt本体(P7、developer
# message)・model/effort・Original->R1->R2のRevision指示・Adaptation
# prompt本体(語彙ルールv2込み)は3条件で完全同一。差分は[ニュース]欄へ
# 挿入する素材(writer_input.md)のみ。
#
# テーマ: Meta Muse AI電話代行「人間コンシェルジュ」(NEWS-ITERATIVE-
# ENTERTAINMENT-TRIAL-02のArticle Aと同一実世界テーマ)。
#
# 3条件:
#   control        - 過去Meta baseline(2-B)の短い素材(2-3文)をそのまま使用
#                     (`er015_news_iterative_entertainment_trial_02.MATERIAL_A`
#                     を無変更で再利用)
#   a_full_ledger  - Full Fact Ledger(既存`er012_output/
#                     e_family_two_level_wiring_01/meta/ledger/
#                     verified_fact_ledger.txt`、18件)をそのまま提示
#   b_selected_brief - 同じFull Ledgerのうち、事前に選んだ1本のStoryline
#                     (「AI電話の裏で人間が電話していた」という開示問題/
#                     プライバシー懸念/機能停止のstoryline)に必要な7件へ
#                     絞ったBriefのみを提示(選択・除外理由は
#                     `research/b_selected_fact_brief.md`に記録)
#
# 生成: Original->R1->R2(P7 prompt、`er015_news_iterative_entertainment_
# trial_01.REVISION_INSTRUCTIONS`のr1/r2キーを逐語使用、previous_response_id
# 連鎖は`er015_news_iterative_entertainment_trial_02`のcall_fresh/
# call_with_previous_response_idをそのまま再利用)。
#
# English Adaptation: `er003_v1_n3_01_advanced_adaptation_generate.py`の
# Natural English Adaptationプロンプト定数(DEVELOPER/COMMON_BLOCK_PREFIX/
# GENERAL_PRESERVE_BULLETS/COMMON_BLOCK_SUFFIX/ARM3_BLOCK/語彙ルールv2)を
# import・逐語流用するが、Production Contract接尾ブロック(### x2必須)は
# **使わない**。代わりに本Trial専用の接尾ブロック(TRIAL_ADAPTATION_SUFFIX、
# `## In one line`はあるが`### `見出し2つの要求はない。長さは
# 「Full story + In one line 全体で280-420 words、見出し・箇条書きなし、
# 水増し禁止」)を新規に定義して使う。Production module
# (er003_v1_n3_01_advanced_adaptation_generate.build_prompt)自体は一切
# importせず変更もしない(定数のみimport)。
#
# API呼び出し: vfl01.get_client() / vfl01.run_writer_no_search()を使用
# (Advanced Production同様、構造Gateはこちらでは使わない。###見出しを
# 要求しない設計のため、restore_r2.validate_point_structureのGateは
# 本Trialの出力形式と一致しないので使用しない)。
#
# サブコマンド:
#   prep     --out-dir <OUT>  (research/sources.md, research/full_ledger.md,
#              research/b_selected_fact_brief.md, {cond}/writer_input.md を書出す)
#   run      --out-dir <OUT> --condition control|a_full_ledger|b_selected_brief [--force]
#              (Original->R1->R2)
#   adapt    --out-dir <OUT> --condition <cond> [--force] (English Adaptation)
#   observe  --out-dir <OUT>  (語数・文字数・段落数の機械集計)
#   factdiff --out-dir <OUT>  (Fact ID別キーワードヒットによる機械補助、
#              最終判定はSonnetが目視で行いREPORTへ記入)
#   cost     --out-dir <OUT>
#
# 冪等性: 各段階のファイルが既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adapt
import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base
import er015_news_iterative_entertainment_trial_01 as trial01
import er015_news_iterative_entertainment_trial_02 as trial02
import er015_news_original_baseline_repro_01 as repro01

THEME_TAG = "NEWS_FAMILY_X_WRITER_FACT_SELECTION_TRIAL_01"
WRITER_MODEL = repro01.WRITER_MODEL
WRITER_EFFORT = repro01.WRITER_EFFORT
DEVELOPER_MESSAGE = repro01.DEVELOPER_MESSAGE

# 3条件で完全同一のテーマ行(trial02のArticle Aと同一文言、無変更)。
THEME_LINE = trial02.THEME_LINE["A"]

# r1/r2のみ使用(trial01/02と逐語同一の指示文)。
REVISION_INSTRUCTIONS = {"r1": trial01.REVISION_INSTRUCTIONS["r1"],
                          "r2": trial01.REVISION_INSTRUCTIONS["r2"]}

LEDGER_PATH = ("er012_output/e_family_two_level_wiring_01/meta/ledger/"
               "verified_fact_ledger.txt")
LEDGER_REUSE_SOURCE_PATH = ("er012_output/e_family_two_level_wiring_01/meta/"
                             "ledger/reuse_source.json")

CONDITIONS = ["control", "a_full_ledger", "b_selected_brief"]

# B条件: 事前に選んだStoryline「AI電話の裏で人間が電話していた」(開示問題/
# プライバシー懸念/機能停止)に必要と判断したFact ID(7件)。
SELECTED_FACT_IDS = [
    "MUSE-003", "MUSE-006", "MUSE-007", "MUSE-008", "MUSE-009",
    "MUSE-010", "MUSE-018",
]

SELECTION_REASONS = {
    "MUSE-003": "Museの電話機能が具体的に何をする機能か(前提)を示す。これが"
                "無いと「電話の裏に人間」という驚きの対象が読者に伝わらない。",
    "MUSE-006": "Storylineの核となる事実そのもの(一部の電話依頼を人間の"
                "エージェントが引き継いで処理していた)。",
    "MUSE-007": "「ごく一部の実験」ではなく従業員の約半数に有効化された規模"
                "であったことを示し、話の実在感・スケール感を支える。",
    "MUSE-008": "なぜ人間が裏で電話するようになったか(AIだと分かると切ら"
                "れる問題)という「理由」を示し、単なる暴露で終わらせず"
                "因果を持たせる。",
    "MUSE-009": "Storylineの核である「開示問題・プライバシー懸念」を直接"
                "構成する事実。",
    "MUSE-010": "Storylineの結末(Meta幹部が問題を認め機能を一時停止した)。"
                "開示問題が実際にどう扱われたかを示す。",
    "MUSE-018": "ガードレール事実。「一般ユーザー全員の通話に人間が紛れて"
                "いた」という誇張・Fact driftを防ぐため、確認範囲が主に"
                "従業員向け内部テストであることを明示する必要がある。",
}

EXCLUSION_REASONS = {
    "MUSE-001": "Museの発表自体(日時・展開地域)はStorylineの前提説明として"
                "必須ではない(電話機能の存在はMUSE-003で足りる)。",
    "MUSE-002": "メール送信・旅行予約・交渉等の一般機能列挙は開示問題/"
                "プライバシー懸念のStorylineに不要な情報量。",
    "MUSE-004": "「2026年8月から従業員に試させ、公開後に段階展開」という"
                "内部タイムライン詳細は、開示問題の結論(MUSE-010)に対して"
                "必須ではない。",
    "MUSE-005": "通話後に記録・要約を返す設計は、プライバシー懸念(MUSE-009)"
                "と近いが、Storylineの核(人間が電話していたこと自体)への"
                "追加情報としては不要。",
    "MUSE-011": "人間処理時の成功率95〜98%という性能指標は、開示問題/"
                "プライバシー懸念のStorylineとは別の切り口(性能比較)であり、"
                "詰め込みを避けるため除外。",
    "MUSE-012": "人種に関する不適切発言の個別事例は、それ自体が別の"
                "Storyline(品質管理問題)であり、開示問題のStorylineに"
                "混ぜると焦点がぼやけるため除外。",
    "MUSE-013": "Meta広報の説明(テスト目的・従業員の反応)は、開示問題の"
                "core storylineに必須ではなくバランス情報のため除外(A条件"
                "[Full Ledger]では引き続き提示され、A/B比較の対象となる)。",
    "MUSE-014": "将来の一般公開方針(AMBIGUOUS、断定禁止)は、今回のStoryline"
                "(現時点で起きた開示問題)の結末には不要な将来情報。",
    "MUSE-015": "Muse Secure VMという技術設計の詳細は、開示問題の"
                "Storylineには不要(除外例として仕様に明記されている項目)。",
    "MUSE-016": "ダウンロード数(250万件超)は普及規模の指標であり、開示"
                "問題のStorylineとは無関係な情報量のため除外。",
    "MUSE-017": "10年前のFacebook Messenger「M」の逸話は興味深い文脈だが、"
                "今回の1本のStorylineに絞る上では必須ではないため除外。",
}


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


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


# ------------------------------------------------------------
# Ledgerパース(Fact ID -> ブロックテキスト)
# ------------------------------------------------------------
FACT_HEADER_RE = re.compile(r"^\[(?:VERIFIED|AMBIGUOUS[^\]]*)\]\s+(MUSE-\d+):", re.MULTILINE)


def parse_ledger_blocks(ledger_text: str) -> dict:
    matches = list(FACT_HEADER_RE.finditer(ledger_text))
    blocks = {}
    for i, m in enumerate(matches):
        fact_id = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(ledger_text)
        blocks[fact_id] = ledger_text[start:end].strip("\n")
    return blocks


def build_selected_brief_material(ledger_text: str) -> str:
    blocks = parse_ledger_blocks(ledger_text)
    parts = [blocks[fid] for fid in SELECTED_FACT_IDS if fid in blocks]
    return "\n\n".join(parts)


# ------------------------------------------------------------
# Prompt構築(P7、テーマ行差し替え+[ニュース]欄へ素材挿入。3条件で
# テーマ行・本文指示は完全同一、素材(material)のみ異なる)
# ------------------------------------------------------------
def build_writer_prompt(material: str) -> str:
    base = repro01.R0_PROMPT
    lines = base.split("\n")
    new_lines = [THEME_LINE if l.startswith("テーマ：") else l for l in lines]
    prompt = "\n".join(new_lines)
    prompt += "\n\n[ニュース]\n" + material
    return prompt


# ------------------------------------------------------------
# prep: research/sources.md, research/full_ledger.md,
#       research/b_selected_fact_brief.md, {cond}/writer_input.md
# ------------------------------------------------------------
def cmd_prep(args):
    out_dir = args.out_dir
    ledger_text = load_text(LEDGER_PATH)
    reuse_source = json.loads(load_text(LEDGER_REUSE_SOURCE_PATH))

    save_text(out_path(out_dir, "research", "full_ledger.md"), ledger_text)

    sources_lines = [
        "# Research Source(NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-01)",
        "",
        "## 再利用元(新規Research構築なし、費用0円)",
        f"- Ledger本体: `{LEDGER_PATH}`",
        f"- 元の構築元(reuse_source.json): `{reuse_source['reused_from']}` "
        f"(sha256={reuse_source['sha256']})",
        "- Fact事実確認補助: `er012_output/e_family_two_level_wiring_01/"
        "meta/fact/meta_fact_scope.md`(「一部の通話(call単位)」scope確定"
        "の一次情報引用、既存)",
        "",
        "## 一次情報URL(Ledger内引用、重複除去)",
    ]
    urls = sorted(set(re.findall(r"\((https?://[^\)]+)\)", ledger_text)))
    for u in urls:
        sources_lines.append(f"- {u}")
    save_text(out_path(out_dir, "research", "sources.md"), "\n".join(sources_lines) + "\n")

    blocks = parse_ledger_blocks(ledger_text)
    all_ids = list(blocks.keys())
    brief_lines = [
        "# b_selected_fact_brief.md",
        "",
        "## Storyline(事前選定)",
        "「AI電話の裏で人間が電話していた」(開示問題・プライバシー懸念・"
        "機能一時停止という結末を持つ1本のStoryline)。",
        "",
        f"## Full Ledger Fact数: {len(all_ids)}件 / 選定数: {len(SELECTED_FACT_IDS)}件",
        "",
        "## 選定Fact(理由付き)",
    ]
    for fid in SELECTED_FACT_IDS:
        brief_lines.append(f"### {fid}")
        brief_lines.append(f"選定理由: {SELECTION_REASONS[fid]}")
        brief_lines.append("")
        brief_lines.append(blocks[fid])
        brief_lines.append("")
    brief_lines.append("## 除外Fact(理由付き)")
    for fid in all_ids:
        if fid in SELECTED_FACT_IDS:
            continue
        reason = EXCLUSION_REASONS.get(fid, "(理由未記載)")
        brief_lines.append(f"- {fid}: {reason}")
    save_text(out_path(out_dir, "research", "b_selected_fact_brief.md"),
               "\n".join(brief_lines) + "\n")

    material = {
        "control": trial02.MATERIAL_A,
        "a_full_ledger": ledger_text,
        "b_selected_brief": build_selected_brief_material(ledger_text),
    }
    for cond in CONDITIONS:
        save_text(out_path(out_dir, cond, "writer_input.md"), material[cond])
        save_text(out_path(out_dir, cond, "prompt_writer.txt"),
                   build_writer_prompt(material[cond]))
    print("[OK] prep: research/sources.md, research/full_ledger.md, "
          "research/b_selected_fact_brief.md, {cond}/writer_input.md written")


# ------------------------------------------------------------
# run: Original -> R1 -> R2 (条件ごと)
# ------------------------------------------------------------
def cmd_run(args):
    out_dir = args.out_dir
    cond = args.condition
    cond_dir = out_path(out_dir, cond)
    install_logger(out_dir)
    client = vfl01.get_client()

    prompt_path = out_path(cond_dir, "prompt_writer.txt")
    if not os.path.exists(prompt_path):
        raise RuntimeError(f"[STOP] prepを先に実行してください: {prompt_path} が存在しません")
    prompt = load_text(prompt_path)

    api_meta_path = out_path(cond_dir, "api_meta.json")
    api_meta = json.loads(load_text(api_meta_path)) if os.path.exists(api_meta_path) else {}

    chain_path = out_path(out_dir, "chain.json")
    chain = json.loads(load_text(chain_path)) if os.path.exists(chain_path) else {"conditions": {}}
    chain.setdefault("conditions", {})
    cond_chain = chain["conditions"].get(cond, {"chain_method": None, "stages": []})

    original_path = out_path(cond_dir, "original.md")
    if os.path.exists(original_path) and not args.force:
        print(f"[SKIP] 既存出力あり(--forceなし): {original_path}")
        prev_id = api_meta["original"]["response_id"]
        prev_text = load_text(original_path)
    else:
        response = trial02.call_fresh(client, DEVELOPER_MESSAGE, prompt, WRITER_EFFORT,
                                       f"{cond}_original")
        text = response.output_text.strip()
        meta = er015base.response_meta(
            response, prompt, DEVELOPER_MESSAGE,
            extra={"condition": cond, "stage": "original", "effort_requested": WRITER_EFFORT},
        )
        save_text(original_path, text)
        api_meta["original"] = meta
        save_json(api_meta_path, api_meta)
        cond_chain["stages"] = [s for s in cond_chain["stages"] if s["stage"] != "original"]
        cond_chain["stages"].append({"stage": "original", "response_id": response.id, "model": response.model})
        chain["conditions"][cond] = cond_chain
        save_json(chain_path, chain)
        prev_id = response.id
        prev_text = text
        print(f"[OK] {cond}_original: {len(text)}字 model={meta['response_model_actual']} id={response.id}")

    chain_method = cond_chain.get("chain_method")
    for stage_key in ["r1", "r2"]:
        stage_path = out_path(cond_dir, f"{stage_key}.md")
        instruction = REVISION_INSTRUCTIONS[stage_key]

        if os.path.exists(stage_path) and not args.force:
            print(f"[SKIP] 既存出力あり(--forceなし): {stage_path}")
            prev_text = load_text(stage_path)
            m = api_meta.get(stage_key)
            if m:
                prev_id = m.get("response_id", prev_id)
                chain_method = m.get("chain_method", chain_method)
            continue

        response = None
        used_method = None
        if chain_method != "fallback_full_text":
            try:
                response = trial02.call_with_previous_response_id(
                    client, instruction, WRITER_EFFORT, prev_id, f"{cond}_{stage_key}",
                )
                used_method = "previous_response_id"
            except Exception as e:  # noqa: BLE001 - 技術的失敗時のみフォールバック
                print(f"[WARN] previous_response_id失敗、フォールバックへ切替({cond}_{stage_key}): {e}")
                response = None

        if response is None:
            fallback_user = f"以下の記事:\n\n{prev_text}\n\n{instruction}"
            response = trial02.call_fresh(client, DEVELOPER_MESSAGE, fallback_user, WRITER_EFFORT,
                                           f"{cond}_{stage_key}")
            used_method = "fallback_full_text"

        chain_method = used_method
        text = response.output_text.strip()
        meta = er015base.response_meta(
            response, instruction, DEVELOPER_MESSAGE,
            extra={
                "condition": cond, "stage": stage_key, "effort_requested": WRITER_EFFORT,
                "chain_method": used_method,
                "previous_response_id_used": prev_id if used_method == "previous_response_id" else None,
            },
        )
        save_text(stage_path, text)
        api_meta[stage_key] = meta
        save_json(api_meta_path, api_meta)
        cond_chain["stages"] = [s for s in cond_chain["stages"] if s["stage"] != stage_key]
        cond_chain["stages"].append({
            "stage": stage_key, "response_id": response.id, "model": response.model,
            "chain_method": used_method,
        })
        cond_chain["chain_method"] = chain_method
        chain["conditions"][cond] = cond_chain
        save_json(chain_path, chain)

        prev_id = response.id
        prev_text = text
        print(f"[OK] {cond}_{stage_key}: {len(text)}字 model={meta['response_model_actual']} "
              f"chain_method={used_method}")


# ------------------------------------------------------------
# Adaptation: 語彙ルールv2込みのAdaptation本文指示(Production定数を
# 逐語import)+ Trial専用の接尾ブロック(contract suffixなし・
# ## In one lineあり)
# ------------------------------------------------------------
TRIAL_ADAPTATION_SUFFIX_LINES = [
    "Write in English.",
    "Length: about 280-420 words in total, counting the full story and the "
    "\"## In one line\" section together.",
    "Format (Markdown): start with \"# \" followed by the title; then the "
    "full story as continuous prose paragraphs (no subheadings, no bullet "
    "points, no numbered lists); then a final section headed exactly "
    "\"## In one line\" containing one sentence.",
    "Do not pad or add filler sentences just to reach the word count.",
]
TRIAL_ADAPTATION_SUFFIX = "\n".join(TRIAL_ADAPTATION_SUFFIX_LINES)


def build_adaptation_prompt(ja_article_text: str) -> str:
    common_block_general = (
        adapt.ADVANCED_COMMON_BLOCK_PREFIX + adapt.ADVANCED_GENERAL_PRESERVE_BULLETS +
        adapt.ADVANCED_COMMON_BLOCK_SUFFIX
    )
    return (
        common_block_general + "\n\n" + adapt.ADVANCED_ARM3_BLOCK + "\n\n" +
        adapt.ADVANCED_VOCAB_RULE_V2_BLOCK + "\n\n" +
        TRIAL_ADAPTATION_SUFFIX + "\n\n[Japanese article]\n" + ja_article_text
    )


def cmd_adapt(args):
    out_dir = args.out_dir
    cond = args.condition
    cond_dir = out_path(out_dir, cond)
    install_logger(out_dir)
    client = vfl01.get_client()

    english_path = out_path(cond_dir, "english.md")
    if os.path.exists(english_path) and not args.force:
        print(f"[SKIP] 既存出力あり(--forceなし): {english_path}")
        return

    r2_path = out_path(cond_dir, "r2.md")
    ja_text = load_text(r2_path)
    prompt = build_adaptation_prompt(ja_text)
    save_text(out_path(cond_dir, "prompt_adaptation.txt"), prompt)

    with cl.logging_context(THEME_TAG, f"{cond}_english"):
        result = vfl01.run_writer_no_search(client, prompt, model=WRITER_MODEL,
                                             developer=adapt.ADVANCED_DEVELOPER)
    text = result["raw_text"].strip()
    save_text(english_path, text)

    api_meta_path = out_path(cond_dir, "api_meta.json")
    api_meta = json.loads(load_text(api_meta_path)) if os.path.exists(api_meta_path) else {}
    api_meta["english"] = {
        "prompt": prompt,
        "developer_message": adapt.ADVANCED_DEVELOPER,
        "model_requested": WRITER_MODEL,
        "response_model_actual": result["model"],
        "response_id": result["response_id"],
        "usage": result.get("usage"),
    }
    save_json(api_meta_path, api_meta)
    print(f"[OK] {cond}_english: {len(text)}字 model={result['model']} id={result['response_id']}")


# ------------------------------------------------------------
# observe: 語数・文字数・段落数の機械集計
# ------------------------------------------------------------
def _word_count_en(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9''-]+", text))


def _paragraph_count(text: str) -> int:
    paras = [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    return len(paras)


def _heading_count(text: str) -> int:
    return len(re.findall(r"^#{1,6}\s", text, re.MULTILINE))


def _bullet_count(text: str) -> int:
    return len(re.findall(r"^\s*[-*]\s", text, re.MULTILINE))


def cmd_observe(args):
    out_dir = args.out_dir
    result = {}
    for cond in CONDITIONS:
        cond_dir = out_path(out_dir, cond)
        entry = {}
        for stage, fname in [("writer_input", "writer_input.md"), ("original", "original.md"),
                              ("r1", "r1.md"), ("r2", "r2.md"), ("english", "english.md")]:
            p = out_path(cond_dir, fname)
            if not os.path.exists(p):
                continue
            text = load_text(p)
            entry[stage] = {
                "char_count": len(text),
                "paragraph_count": _paragraph_count(text),
            }
            if stage == "english":
                entry[stage]["word_count"] = _word_count_en(text)
                entry[stage]["heading_count"] = _heading_count(text)
                entry[stage]["bullet_count"] = _bullet_count(text)
                entry[stage]["has_in_one_line"] = ("## In one line" in text)
        result[cond] = entry
    save_json(out_path(out_dir, "observation_machine.json"), result)
    for cond, entry in result.items():
        eng = entry.get("english", {})
        r2 = entry.get("r2", {})
        print(f"[OK] {cond}: r2_chars={r2.get('char_count')} "
              f"english_words={eng.get('word_count')} "
              f"headings={eng.get('heading_count')} bullets={eng.get('bullet_count')} "
              f"in_one_line={eng.get('has_in_one_line')}")


# ------------------------------------------------------------
# factdiff: Fact ID別キーワードヒットによる機械補助(最終判定はSonnet目視)
# ------------------------------------------------------------
FACT_KEYWORDS = {
    "MUSE-001": ["9月8日", "iOS", "Android", "muse.ai", "発表"],
    "MUSE-002": ["メール送信", "旅行予約", "ブラウザ操作", "フォーム入力", "交渉"],
    "MUSE-003": ["ヘアカット", "店舗在庫", "見積もり", "事業者へ電話"],
    "MUSE-004": ["8月から", "段階的", "内部投稿"],
    "MUSE-005": ["記録と要約", "会話の記録"],
    "MUSE-006": ["human concierge", "人間コンシェルジュ", "引き渡", "訓練を受けた"],
    "MUSE-007": ["半数", "オプトアウト", "約50%", "50パーセント"],
    "MUSE-008": ["切る", "切られ", "AIだと", "hangs up", "通話を切"],
    "MUSE-009": ["プライバシー", "個人情報", "機微", "漏えい", "懸念"],
    "MUSE-010": ["ロールバック", "rolled back", "副社長", "一時的に", "取りやめ"],
    "MUSE-011": ["95", "98", "成功率"],
    "MUSE-012": ["人種", "不適切な発言", "差別"],
    "MUSE-013": ["Daniel Roberts", "広報", "圧倒的に肯定的"],
    "MUSE-014": ["一般公開", "商業者と協力", "適切な開示"],
    "MUSE-015": ["Secure VM", "Sentinel", "仮想マシン"],
    "MUSE-016": ["250万", "ダウンロード数", "Sensor Tower"],
    "MUSE-017": ["Facebook Messenger", "「M」", "70%", "10年前"],
    "MUSE-018": ["一般ユーザー", "確定できない", "従業員向けの内部テスト"],
}


def cmd_factdiff(args):
    out_dir = args.out_dir
    result = {}
    for cond in CONDITIONS:
        cond_dir = out_path(out_dir, cond)
        cond_result = {}
        for stage, fname in [("r2", "r2.md"), ("english", "english.md")]:
            p = out_path(cond_dir, fname)
            if not os.path.exists(p):
                continue
            text = load_text(p)
            hits = {}
            for fid, kws in FACT_KEYWORDS.items():
                hit_kws = [kw for kw in kws if kw in text]
                if hit_kws:
                    hits[fid] = hit_kws
            cond_result[stage] = hits
        result[cond] = cond_result
    save_json(out_path(out_dir, "fact_diff_machine.json"), result)
    for cond, cr in result.items():
        for stage, hits in cr.items():
            print(f"[OK] {cond}/{stage}: fact_hits={sorted(hits.keys())}")


# ------------------------------------------------------------
# cost
# ------------------------------------------------------------
def cmd_cost(args):
    out_dir = args.out_dir
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
    # 注: writer段階(original/r1/r2)は`trial02.call_fresh`/
    # `call_with_previous_response_id`を再利用しており、これらは内部で
    # trial02自身のTHEME_TAG("NEWS_ITERATIVE_ENTERTAINMENT_TRIAL_02")で
    # ログする(呼び出し元のTHEME_TAGへは影響しない、trial02側の実装)。
    # このraw_usage_log.jsonl自体は本Trial専用out_dirにのみ書かれるため、
    # themeでの絞り込みはせず、このファイル内の全エントリを対象とする。
    entries = [e for e in entries
               if e.get("theme") in (THEME_TAG, "NEWS_ITERATIVE_ENTERTAINMENT_TRIAL_02")]

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
            "output_tokens": ot, "usd": round(usd, 6),
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
    }
    save_json(out_path(out_dir, "cost.json"), result)
    print(f"[OK] cost: total_jpy={result['total_jpy']} total_calls={result['total_calls']}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_prep = sub.add_parser("prep")
    p_prep.add_argument("--out-dir", required=True)
    p_prep.set_defaults(func=cmd_prep)

    p_run = sub.add_parser("run")
    p_run.add_argument("--out-dir", required=True)
    p_run.add_argument("--condition", required=True, choices=CONDITIONS)
    p_run.add_argument("--force", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_adapt = sub.add_parser("adapt")
    p_adapt.add_argument("--out-dir", required=True)
    p_adapt.add_argument("--condition", required=True, choices=CONDITIONS)
    p_adapt.add_argument("--force", action="store_true")
    p_adapt.set_defaults(func=cmd_adapt)

    p_ob = sub.add_parser("observe")
    p_ob.add_argument("--out-dir", required=True)
    p_ob.set_defaults(func=cmd_observe)

    p_fd = sub.add_parser("factdiff")
    p_fd.add_argument("--out-dir", required=True)
    p_fd.set_defaults(func=cmd_factdiff)

    p_cost = sub.add_parser("cost")
    p_cost.add_argument("--out-dir", required=True)
    p_cost.set_defaults(func=cmd_cost)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
