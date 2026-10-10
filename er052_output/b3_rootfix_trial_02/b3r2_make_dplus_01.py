# -*- coding: utf-8 -*-
"""D-plus-single-call 腕の Trial専用B3 Promptコピーを、Production module(未改変)から文字列置換で生成する。
Production fileは読むだけ(不変)。置換は全て「ちょうど1回出現」をassertする。出力: b3r2_b3_dplus_01.py と PROMPT_DIFF_01.md(diff自動生成)。
API呼び出しなし。"""
import os, sys, hashlib, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import b3r2_sepcall_01 as SEP   # 手順6の定義(STEP6_RULES)の単一ソース。D-plusとSeparate-callで逐語同一にする
SRC = os.path.join(REPO, "er019_family_x_storyline_b3_fact_selection_01.py")
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "dplus"      # dplus | roleonly(役割宣言+欄ラベル分離のみ・number_ranksなし)
assert VARIANT in ("dplus", "roleonly"), VARIANT
DST = os.path.join(HERE, "b3r2_b3_dplus_01.py" if VARIANT == "dplus" else "b3r2_b3_roleonly_01.py")
DIFF = os.path.join(HERE, "PROMPT_DIFF_02.md" if VARIANT == "dplus" else "PROMPT_DIFF_ROLEONLY_02.md")

src = open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
out = src
R = []


def rep(old, new, tag):
    global out
    assert out.count(old) == 1, (tag, out.count(old))
    out = out.replace(old, new)
    R.append(tag)


rep('THEME_TAG = "NEWS_FAMILY_X_B3_FACT_SELECTION_PRODUCTION_01"', 'THEME_TAG = "B3R2_DPLUS_TRIAL_02"' if VARIANT == "dplus" else 'THEME_TAG = "B3R2_ROLEONLY_TRIAL_02"', "THEME_TAG")

# (1) Ledgerの読み方(役割宣言)
rep("【Full Fact Ledger】\n{ledger_text}\n\nあなたの仕事は次の5つです。",
    "【Full Fact Ledger】\n{ledger_text}\n\n"
    "【Ledgerの読み方】\n"
    "各Factは「Fact本文」(ID行の文と、scope・conditions・numeric_value・date_or_periodなどの欄)と、「Writerへの制約」(notes_for_writer・ambiguity_noteの欄。`制約(…)`と表記されることがあります)に分かれています。\n"
    "- Fact本文は、Fact選択とStorylineの材料です。\n"
    "- Writerへの制約は、のちに記事を書く工程が守るガードレールです。Storylineやselected_fact_briefの内容・文言として転記・言い換えしないでください(「〜しない」「〜と断定しない」などの指示調の文を入れない)。Storylineには事実の記述だけを書き、制約に反する断定をしないでください。制約そのものは、システムが選択Factに対応づけて別途Writerへ渡します。\n\n"
    + ("あなたの仕事は次の6つです。" if VARIANT == "dplus" else "あなたの仕事は次の5つです。"), "role_declaration+count")

# (2) Storyline手順
rep("2. 決定したStorylineを1行の日本語で明示してください(これが後工程でWriterへ渡すテーマ文としてそのまま使われます)。",
    "2. 決定したStorylineを1行の日本語で明示してください(これが後工程でWriterへ渡すテーマ文としてそのまま使われます)。Storylineには、Fact本文に基づく事実の記述だけを書き、注意・禁止・書き方の指示は含めないでください。",
    "step2_storyline_role")

if VARIANT == "dplus":
    # (3) 手順6 数値ランク
    STEP6 = (
        "\n6. 採用したFactそれぞれについて、そのFact本文(ID行の文)に書かれている数字・日付の表記を1つずつ洗い出し、number_ranksへ中核(core)か周辺(peripheral)の別とともに記載してください。\n"
        + SEP.STEP6_RULES
    )
    rep("Selected Fact Briefは記事本文そのものではなく、Writerへの素材です。\n\n【採用Fact数についての注意】",
        "Selected Fact Briefは記事本文そのものではなく、Writerへの素材です。" + STEP6 + "\n【採用Fact数についての注意】", "step6_number_ranks")

    # (4) 出力説明
    rep("- recheck_note: 採用Fact数が6件以上の場合のみ記入。5件以下の場合はnull。",
        "- recheck_note: 採用Fact数が6件以上の場合のみ記入。5件以下の場合はnull。\n- number_ranks: 手順6の結果(採用Factの数字・日付の表記ごとに fact_id・surface・kind・role)。数字が1つも無い場合は空配列。", "output_desc")
    rep("【重要】fact_idは、上記Full Ledgerに実在するfact_idのみを使用してください。Ledgerに存在しないfact_idを作り出さないでください。",
        "【重要】fact_idは、上記Full Ledgerに実在するfact_idのみを使用してください。Ledgerに存在しないfact_idを作り出さないでください。number_ranksのfact_idは採用したFactのみ、surfaceは当該Factのfact本文に実在する表記のみとしてください。", "important")

    # (5) schema
    rep('            "recheck_note": {"type": ["string", "null"]},\n        },',
        '            "recheck_note": {"type": ["string", "null"]},\n'
        '            "number_ranks": {\n'
        '                "type": "array",\n'
        '                "items": {\n'
        '                    "type": "object",\n'
        '                    "properties": {\n'
        '                        "fact_id": {"type": "string"},\n'
        '                        "surface": {"type": "string"},\n'
        '                        "kind": {"type": "string", "enum": ["magnitude", "date_time", "range", "year", "ordinal", "name_embedded"]},\n'
        '                        "role": {"type": "string", "enum": ["core", "peripheral"]},\n'
        '                    },\n'
        '                    "required": ["fact_id", "surface", "kind", "role"],\n'
        '                    "additionalProperties": False,\n'
        '                },\n'
        '            },\n'
        '        },', "schema_props")
    rep('"selected_fact_brief", "recheck_note",\n        ],', '"selected_fact_brief", "recheck_note", "number_ranks",\n        ],', "schema_required")

# (6) 入力整形(promptへ渡す台帳テキストのみ。ID抽出・検証は元の台帳で行う)
rep("def build_user_prompt(topic: str, ledger_text: str) -> str:\n    return USER_PROMPT_TEMPLATE.format(\n        topic=topic, ledger_text=ledger_text,",
    'SHAPE_MODE = "sep"   # "sep"=制約欄を制約(…)ラベルへ置換 / "none"=台帳そのまま(D-plus-min腕用)\n'
    "SHAPE_LABELS = ((\"  notes_for_writer:\", \"  制約(notes_for_writer):\"), (\"  ambiguity_note:\", \"  制約(ambiguity_note):\"))\n\n\n"
    "def shape_ledger_for_b3(ledger_text: str) -> str:\n"
    "    \"\"\"Fact本文と制約を欄ラベルで役割分離して見せる。ID行(`[VERIFIED] ID:`)の形式・欄の値は不変(ラベルのみ置換)。\"\"\"\n"
    "    if SHAPE_MODE != \"sep\":\n        return ledger_text\n"
    "    out = ledger_text\n    for a, b in SHAPE_LABELS:\n        out = out.replace(\"\\n\" + a, \"\\n\" + b)\n    return out\n\n\n"
    "def build_user_prompt(topic: str, ledger_text: str) -> str:\n    return USER_PROMPT_TEMPLATE.format(\n        topic=topic, ledger_text=shape_ledger_for_b3(ledger_text),", "shape_ledger")

if VARIANT == "dplus":
    # (7) 検証: number_ranksのhardエラー(UNKNOWN/未選択/surface不在/不正値/重複)を技術retry対象に、flagsは報告のみ
    rep("def validate_selection_output(parsed: dict, ledger_fact_ids: list) -> list:",
        "import os as _os, sys as _sys\n_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))\nimport b3r2_rank_01 as _rank\n\n\n"
        "def validate_selection_output(parsed: dict, ledger_fact_ids: list, ledger_text: str = None) -> list:", "validate_sig")
    rep('    if len(selected_ids) >= 6 and not (parsed.get("recheck_note") or "").strip():\n        errors.append("RECHECK_NOTE_MISSING_FOR_6_OR_MORE_SELECTED")\n    return errors',
        '    if len(selected_ids) >= 6 and not (parsed.get("recheck_note") or "").strip():\n        errors.append("RECHECK_NOTE_MISSING_FOR_6_OR_MORE_SELECTED")\n'
        '    if ledger_text is not None and not unknown_selected:\n'
        '        nv = _rank.validate_number_ranks(parsed.get("number_ranks"), ledger_text, selected_ids, parsed.get("selected_storyline"))\n'
        '        errors.extend("NUMBER_RANKS_" + e for e in nv["errors"])\n'
        '        parsed["_number_rank_flags"] = nv["flags"]\n'
        '    return errors', "validate_body")
    rep("errors = validate_selection_output(result[\"parsed\"], ledger_fact_ids)",
        "errors = validate_selection_output(result[\"parsed\"], ledger_fact_ids, ledger_text)", "validate_call")

# (8) 2回失敗時の例外にattempts_logを添付(Trialの集計用。挙動=2回試行しSTOPは不変)
rep('    raise RuntimeError(\n        "[STOP] Storyline+B3 Fact Selection: 2回試行しても技術的に有効な出力を得られませんでした。"\n        f" attempts_log={attempts_log} last_exc={last_exc}"\n    )',
    '    _err = RuntimeError(\n        "[STOP] Storyline+B3 Fact Selection: 2回試行しても技術的に有効な出力を得られませんでした。"\n        f" attempts_log={attempts_log} last_exc={last_exc}"\n    )\n    _err.attempts_log = attempts_log\n    raise _err', "stop_attach_attempts_log")

LABEL = "D-plus-single-call腕" if VARIANT == "dplus" else "役割宣言のみ腕(number_ranksなし)"
open(DST, "w", encoding="utf-8", newline="\n").write(
    f"# Trial専用コピー(B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02 {LABEL})。Production moduleからb3r2_make_dplus_01.py {VARIANT} が文字列置換で生成。Production fileは不変。\n" + out)

sha = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()
dst_text = open(DST, encoding="utf-8", newline="").read()
d = "".join(difflib.unified_diff(src.splitlines(True), out.splitlines(True), "Production(er019_family_x_storyline_b3_fact_selection_01.py)", f"Trial({os.path.basename(DST)}, 先頭コメント1行除く)", n=1))
adds = ("(1)【Ledgerの読み方】役割宣言(U1: 制約を選択の参考にしてよい旨は削除済み) (2)手順2末尾に「事実の記述だけ・指示を含めない」 (3)入力整形 shape_ledger_for_b3(欄ラベルのみ置換: notes_for_writer→制約(notes_for_writer)、ambiguity_note→制約(ambiguity_note)。値・ID行は不変) (4)2回失敗時のRuntimeErrorにattempts_logを添付(挙動は不変)"
        if VARIANT == "roleonly" else
        "(1)【Ledgerの読み方】役割宣言(U1: 制約を選択の参考にしてよい旨は削除済み) (2)手順2末尾に「事実の記述だけ・指示を含めない」 (3)手順6 数値ランク(定義=b3r2_sepcall_01.STEP6_RULESと逐語同一) (4)出力説明とschemaにnumber_ranks(最後尾) (5)入力整形 shape_ledger_for_b3 (6)number_ranksの技術検証をvalidate_selection_outputへ追加(hard=未知/未選択fact_id・surfaceがFactに無い(数字境界つき)・不正値・重複→既存の1回retry対象、flags=報告のみ) (7)2回失敗時のRuntimeErrorにattempts_logを添付(挙動は不変)")
md = (f"# PROMPT_DIFF({LABEL}): Trial専用B3 Prompt(Productionとの差分。unified diff逐語。自動生成、委任_02)\n"
      f"- Production module sha256={sha(src)}\n- Trialコピー sha256={sha(dst_text)}\n"
      f"- 置換箇所(各ちょうど1回出現をassert): {', '.join(R)}\n"
      "- 不変: DEVELOPER_MESSAGE / FACT_TEST_DEFINITIONS_JA / 手順1,3,4,5の文言 / 採用Fact数注意 / fact_tests・selected_fact_ids・selected_fact_brief・recheck_note の schema項目 / retry機構(1回のみ)。削除した既存手順・schema項目は無い。\n"
      f"- 追加: {adds}\n"
      "- THEME_TAGはcost logger用ラベルのみ変更。\n\n## unified diff\n```diff\n" + d + "```\n")
open(DIFF, "w", encoding="utf-8", newline="\n").write(md)
print("generated", DST, sha(dst_text)); print("replacements", R)
