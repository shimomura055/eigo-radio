# ============================================================
# er015_family_x_writer_fact_selection_trial_02.py
# NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-02 (Fable設計、2026-09-26)
# ============================================================
# 目的: NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-01のB(Selected Fact
# Brief、7 Fact)でも、「Factとして正しいが中心Storylineと直接つながらない
# 情報」(従業員約半数・opt-out等)が残っていた問題を受け、より厳格な2つの
# Fact選定基準——B2(因果必須基準、目安4-6件)/B3(最小核基準、目安3-5件)
# ——でBriefを作り直し、Control(現状相当)・B1(Trial-01のB)と比較する
# 検証専用Trialスクリプト。**Production実装ではない。Trialのみ、最大
# VALIDATED、文章生成まで。Production Prompt/module変更禁止。**
#
# Writer Prompt本体(P7、developer message)・model/effort・
# Original->R1->R2のRevision指示・English Adaptation prompt本体
# (語彙ルールv2込み・Trial専用接尾ブロック)は、Trial-01と完全同一
# (`er015_family_x_writer_fact_selection_trial_01`の定数・関数を逐語
# import・流用。Production module自体は変更しない)。差分は
# [ニュース]欄へ挿入する素材(writer_input.md)のみ(= Fact選定の違いのみ)。
#
# Control(過去Meta baseline 2-3文)とB1(Trial-01のb_selected_brief、
# 7 Fact)は**新規生成しない**。Trial-01の出力ディレクトリからそのまま
# コピーして再掲する(コピー元パスをSOURCE_NOTE.mdに記録)。
#
# 4条件:
#   control    - Trial-01 control/ をそのまま再掲(コピーのみ)
#   b1         - Trial-01 b_selected_brief/ をそのまま再掲(コピーのみ、
#                ディレクトリ名のみ b1 に変更)
#   b2_causal  - 因果必須基準(そのFactがないと中心Storylineの
#                「なぜ→何が起きた→その結果どうなった」が成立しないもの
#                だけ残す)で選定したBrief(目安4-6件、実際5件)
#   b3_minimal - 最小核基準(そのFactを1つ除くとStorylineの意味・因果・
#                結論のいずれかが明確に壊れるものだけ残す)で選定した
#                Brief(目安3-5件、実際4件)
#
# 新規API呼び出しはb2_causal/b3_minimalのみ(各Original->R1->R2->
# Adaptationの4 call、計8 call)。Control/B1は0 call(再掲のみ)。
#
# サブコマンド:
#   prep      --out-dir <OUT>  (research/full_ledger.md, fact_selection_
#              b2.md, fact_selection_b3.md, {b2_causal,b3_minimal}/
#              writer_input.md・prompt_writer.txt, {control,b1}/を
#              Trial-01からコピー)
#   run       --out-dir <OUT> --condition b2_causal|b3_minimal [--force]
#              (Original->R1->R2。er015_family_x_writer_fact_selection_
#              trial_01.cmd_run をそのまま呼び出す=条件名に依存しない汎用実装)
#   adapt     --out-dir <OUT> --condition b2_causal|b3_minimal [--force]
#              (English Adaptation。同様にtrial_01.cmd_adaptを呼び出す)
#   observe   --out-dir <OUT>  (4条件、語数・段落数・見出し・箇条書きの機械集計)
#   factdiff  --out-dir <OUT>  (4条件、Fact ID別キーワードヒットの機械補助、
#              最終判定はSonnetが目視でREPORTへ記入)
#   cost      --out-dir <OUT>  (b2_causal/b3_minimalの新規call分のみ集計)
#
# 冪等性: 各段階のファイルが既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re
import shutil

import er005_cost_logger as cl
import er015_family_x_writer_fact_selection_trial_01 as fw1
import er015_news_core_idea_editorial_trial_01 as er015base

THEME_TAG = "NEWS_FAMILY_X_WRITER_FACT_SELECTION_TRIAL_02"

TRIAL01_OUT_DIR = os.path.join("er015_output", "family_x_writer_fact_selection_trial_01")

# Trial-01からそのまま再掲するディレクトリ(コピー元 -> コピー先)
COPY_FORWARD = {
    "control": os.path.join(TRIAL01_OUT_DIR, "control"),
    "b1": os.path.join(TRIAL01_OUT_DIR, "b_selected_brief"),
}

NEW_CONDITIONS = ["b2_causal", "b3_minimal"]
ALL_CONDITIONS = ["control", "b1", "b2_causal", "b3_minimal"]

# ------------------------------------------------------------
# B2(因果必須基準、5件)/ B3(最小核基準、4件)の選定Fact ID
# ------------------------------------------------------------
B2_SELECTED_FACT_IDS = ["MUSE-003", "MUSE-006", "MUSE-008", "MUSE-009", "MUSE-010"]
B3_SELECTED_FACT_IDS = ["MUSE-006", "MUSE-008", "MUSE-009", "MUSE-010"]

SELECTED_FACT_IDS = {"b2_causal": B2_SELECTED_FACT_IDS, "b3_minimal": B3_SELECTED_FACT_IDS}

# Core Storyline(Trial-01 B1の中心を基準、固定文として押し付けない):
# Museが電話代行する→AIだと気付かれると切られることがある→人間スタッフへ
# 引き渡す→人間介在によるprivacy/disclosure問題→Metaが機能を一旦戻す。
CORE_STORYLINE = (
    "Museが電話代行する→AIだと気付かれると切られることがある→人間スタッフへ"
    "引き渡す→人間介在によるprivacy/disclosure問題→Metaが機能を一旦戻す。"
)

# 全18 Factについての4テスト結果("YES"/"NO")+ B2/B3採否 + 理由。
# Test1: 消しても中心Storylineを理解できるか(YES→除外)
# Test2: 別Factとの因果に使われているか(NO→除外)
# Test3: ないと重要な「なぜ?」が理解できなくなるか(NO→除外)
# Test4: 面白い・具体的・数字があるだけで残していないか(YES→除外)
FACT_TESTS = {
    "MUSE-001": {
        "summary": "Muse発表(9/8、地域)",
        "t1": "YES", "t2": "NO", "t3": "NO", "t4": "YES",
        "b2": "除外", "b3": "除外",
        "reason": "発表日・展開地域は背景説明であり、因果チェーン(なぜ→何が"
                  "起きた→結果)のどの段にも使われない。原則除外(背景として"
                  "正しいだけ)に該当。",
    },
    "MUSE-002": {
        "summary": "一般機能列挙(メール送信/旅行予約/交渉等)",
        "t1": "YES", "t2": "NO", "t3": "NO", "t4": "YES",
        "b2": "除外", "b3": "除外",
        "reason": "電話代行以外の一般機能列挙であり、開示・プライバシー問題の"
                  "Storylineには無関係。詰め込みの典型例として除外。",
    },
    "MUSE-003": {
        "summary": "電話機能の中身(ヘアカット予約/在庫確認/見積り)",
        "t1": "YESに近いが境界的(MUSE-006自体が「電話依頼」という語で"
              "行為の存在を伝えるため、理論上は除外可能)",
        "t2": "NO(後続の因果[008/009/010]には具体例そのものは使われない)",
        "t3": "NO(『なぜ人間が必要だったか』の理解には不要)",
        "t4": "YESに近い(具体的な作業例という色付け)",
        "b2": "採用", "b3": "除外",
        "reason": "B2(因果必須、やや広め)では『何が起きたか』の段を具体的に"
                  "裏付ける最小限の情報として採用(Test1がぎりぎりYESの境界"
                  "Factと明記した上での採用判断)。B3(最小核、1件でも欠けると"
                  "壊れるかを問う最も厳しい基準)では、MUSE-006の文言だけで"
                  "『電話依頼が人間へ引き渡された』という核は壊れないため除外。",
    },
    "MUSE-004": {
        "summary": "内部テスト開始時期(8月〜、公開後の段階展開)",
        "t1": "YES", "t2": "NO", "t3": "NO", "t4": "YES",
        "b2": "除外", "b3": "除外",
        "reason": "内部タイムラインの詳細であり、因果チェーンの成立に不要。",
    },
    "MUSE-005": {
        "summary": "通話後に記録・要約を利用者へ返す設計",
        "t1": "YES", "t2": "NO", "t3": "NO", "t4": "YES",
        "b2": "除外", "b3": "除外",
        "reason": "プライバシー懸念(MUSE-009)と隣接するが別トピック(通話後の"
                  "要約設計)であり、核の因果チェーンには使われない。",
    },
    "MUSE-006": {
        "summary": "人間コンシェルジュへの引き渡し(core)",
        "t1": "NO(これを消すと『何が起きたか』自体が消える)",
        "t2": "YES(008の結果として発生し、009/010の前提になる)",
        "t3": "YES", "t4": "NO",
        "b2": "採用", "b3": "採用",
        "reason": "Storylineの核である「AI電話の一部を人間が引き継いだ」"
                  "という事実そのもの。因果チェーンの中心ノード。",
    },
    "MUSE-007": {
        "summary": "規模(従業員約半数・オプトアウト可)",
        "t1": "YES", "t2": "NO(010の根拠として明記されているのは"
              "『開示不足』であり、規模の大きさではない)",
        "t3": "NO", "t4": "YES(具体的な数字があるだけ)",
        "b2": "除外", "b3": "除外",
        "reason": "ユーザー指定の再評価対象。規模・opt-outの有無は中心"
                  "Storyline(なぜ切られたか→人間交代→プライバシー問題→"
                  "ロールバック)の因果には使われておらず、除外(Trial-01の"
                  "B1では採用していたが、本Trialでより厳格な基準を適用した"
                  "結果、除外に変更)。",
    },
    "MUSE-008": {
        "summary": "AIだとバレると切られる(理由・core)",
        "t1": "NO", "t2": "YES(006[人間への引き渡し]の直接の原因)",
        "t3": "YES", "t4": "NO",
        "b2": "採用", "b3": "採用",
        "reason": "『なぜ』人間が電話を引き継ぐようになったかを説明する"
                  "因果の起点。これがないと006が唐突になる。",
    },
    "MUSE-009": {
        "summary": "プライバシー・機微情報共有への懸念(core)",
        "t1": "NO", "t2": "YES(006の結果として発生し、010の前提になる)",
        "t3": "YES", "t4": "NO",
        "b2": "採用", "b3": "採用",
        "reason": "人間介在の結果として生じた開示・プライバシー問題そのもの。"
                  "これがないと010(ロールバック)の理由が説明できない。",
    },
    "MUSE-010": {
        "summary": "副社長が問題を認めロールバック(結論・core)",
        "t1": "NO", "t2": "YES(009の直接の結果)",
        "t3": "YES", "t4": "NO",
        "b2": "採用", "b3": "採用",
        "reason": "Storylineの結末。これがないと『その結果どうなったか』が"
                  "宙に浮く。",
    },
    "MUSE-011": {
        "summary": "人間処理時の成功率95〜98%",
        "t1": "YES", "t2": "NO", "t3": "NO", "t4": "YES",
        "b2": "除外", "b3": "除外",
        "reason": "性能指標であり開示・プライバシーの因果チェーンとは別の"
                  "切り口。除外(Trial-01B1でも除外済み、方針継続)。",
    },
    "MUSE-012": {
        "summary": "人種に関する不適切発言の個別事例",
        "t1": "YES", "t2": "NO(010が根拠とするのは開示不足であり、この"
              "個別事例ではない)",
        "t3": "NO", "t4": "YES(1件の具体的事例)",
        "b2": "除外", "b3": "除外",
        "reason": "品質管理問題という別Storylineであり、開示・プライバシー"
                  "問題の核心因果には使われていない。",
    },
    "MUSE-013": {
        "summary": "Meta広報コメント(テスト目的・従業員反応が肯定的)",
        "t1": "YES", "t2": "NO", "t3": "NO", "t4": "YES(広報スピン)",
        "b2": "除外", "b3": "除外",
        "reason": "Meta側の説明・スピンであり、核の因果チェーンの成立には"
                  "不要。",
    },
    "MUSE-014": {
        "summary": "将来の一般公開方針(AMBIGUOUS)",
        "t1": "YES", "t2": "NO(010の結論[ロールバック]自体は014なしで"
              "完結する)",
        "t3": "NO", "t4": "YES寄り(未確定の将来情報)",
        "b2": "除外", "b3": "除外",
        "reason": "AMBIGUOUSかつ将来情報であり、核Storyline(過去に起きた"
                  "開示問題とその帰結)の理解に必須ではない。断定禁止の"
                  "リスクも避けるため除外。",
    },
    "MUSE-015": {
        "summary": "Muse Secure VM(技術設計)",
        "t1": "YES", "t2": "NO", "t3": "NO", "t4": "YES",
        "b2": "除外", "b3": "除外",
        "reason": "技術設計の詳細であり因果チェーンに無関係。",
    },
    "MUSE-016": {
        "summary": "ダウンロード数250万件超",
        "t1": "YES", "t2": "NO", "t3": "NO", "t4": "YES",
        "b2": "除外", "b3": "除外",
        "reason": "普及規模の指標であり因果チェーンに無関係。",
    },
    "MUSE-017": {
        "summary": "Facebook Messenger「M」の逸話(10年前)",
        "t1": "YES", "t2": "NO", "t3": "NO", "t4": "YES(興味深いが背景)",
        "b2": "除外", "b3": "除外",
        "reason": "過去の別事例という背景情報であり、今回のStorylineの"
                  "因果チェーンには使われない。",
    },
    "MUSE-018": {
        "summary": "スコープ注意(確認範囲は主に従業員向け内部テスト)",
        "t1": "YES", "t2": "NO(因果チェーンのどのノードの原因にも結果にも"
              "ならない)",
        "t3": "NO(『なぜ』の理解ではなく『どこまで確認されているか』という"
              "確度の注記)", "t4": "NO寄りだが一度だけ使われる注記",
        "b2": "除外", "b3": "除外",
        "reason": "Trial-01のB1では『誇張・Fact drift防止』の目的で採用して"
                  "いたが、本Trialの4テストを厳格に適用すると、核の因果"
                  "チェーン自体には使われない(除外条件『Storyline理解に"
                  "必須でない』に該当)。**留意点(既知のトレードオフ)**: "
                  "この注記を外すと、Writerが『一般ユーザー全員の通話に人間が"
                  "紛れていた』のように過度に一般化する具体的リスクがある。"
                  "本Trialでは意図的にこのリスクを許容し、実際の生成結果で"
                  "過度な一般化(Fact drift)が起きるかどうかをcomparison.md"
                  "で客観的に観察する設計とした。",
    },
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


def build_selected_brief_material(ledger_text: str, fact_ids: list) -> str:
    blocks = fw1.parse_ledger_blocks(ledger_text)
    parts = [blocks[fid] for fid in fact_ids if fid in blocks]
    return "\n\n".join(parts)


def write_fact_selection_md(out_dir: str, cond: str, fact_ids: list, criterion_name: str,
                             criterion_desc: str, target_desc: str) -> None:
    fname_tag = "b2" if cond == "b2_causal" else "b3"
    lines = [
        f"# fact_selection_{fname_tag}.md",
        "",
        f"## 基準: {criterion_name}",
        criterion_desc,
        "",
        f"## Core Storyline(参照、固定文として押し付けない)",
        CORE_STORYLINE,
        "",
        f"## 目安: {target_desc} / 実際の選定数: {len(fact_ids)}件",
        "",
        "## Full Ledger(18 Fact)全件の4テスト結果とB2/B3採否",
        "",
        "| Fact ID | 要旨 | Test1(消しても理解可?) | Test2(因果に使用?) | "
        "Test3(『なぜ』に必要?) | Test4(面白い/数字だけ?) | B2採否 | B3採否 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for fid, t in FACT_TESTS.items():
        lines.append(
            f"| {fid} | {t['summary']} | {t['t1']} | {t['t2']} | {t['t3']} | "
            f"{t['t4']} | {t['b2']} | {t['b3']} |"
        )
    lines.append("")
    lines.append(f"## {criterion_name}: 採否理由(Fact ID別)")
    for fid, t in FACT_TESTS.items():
        verdict_key = "b2" if cond == "b2_causal" else "b3"
        lines.append(f"### {fid}({t[verdict_key]})")
        lines.append(t["reason"])
        lines.append("")
    save_text(out_path(out_dir, f"fact_selection_{fname_tag}.md"),
               "\n".join(lines) + "\n")


def cmd_prep(args):
    out_dir = args.out_dir

    # --- Control / B1 の再掲(コピーのみ、新規生成なし) ---
    source_note_lines = [
        "# SOURCE_NOTE.md(Control / B1 再掲元)",
        "",
        "本ディレクトリのcontrol/・b1/は、"
        "NEWS-FAMILY-X-WRITER-FACT-SELECTION-TRIAL-01の出力をそのまま"
        "コピーしたものであり、新規生成は一切行っていない(API呼び出し0件、"
        "費用¥0)。",
        "",
    ]
    for cond, src_rel in COPY_FORWARD.items():
        dst_dir = out_path(out_dir, cond)
        if os.path.exists(dst_dir) and not args.force:
            print(f"[SKIP] 既存あり(--forceなし): {dst_dir}")
        else:
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(src_rel, dst_dir)
            print(f"[OK] copy {src_rel} -> {dst_dir}")
        source_note_lines.append(f"- {cond}/ <- `{src_rel}/`(Trial-01、無変更コピー)")
    save_text(out_path(out_dir, "SOURCE_NOTE.md"), "\n".join(source_note_lines) + "\n")

    # --- research/full_ledger.md(既存Ledgerの再掲、新規Research構築なし) ---
    ledger_text = load_text(fw1.LEDGER_PATH)
    save_text(out_path(out_dir, "research", "full_ledger.md"), ledger_text)

    # --- fact_selection_b2.md / fact_selection_b3.md ---
    write_fact_selection_md(
        out_dir, "b2_causal", B2_SELECTED_FACT_IDS,
        "B2: 因果必須基準",
        "そのFactがないと中心Storylineの『なぜ→何が起きた→その結果どうなった』"
        "が成立しないものだけ残す。",
        "4-6件",
    )
    write_fact_selection_md(
        out_dir, "b3_minimal", B3_SELECTED_FACT_IDS,
        "B3: 最小核基準",
        "そのFactを1つ除くとStorylineの意味・因果・結論のいずれかが"
        "明確に壊れるFactだけ残す。『あると豊かになる』ではKEEPしない。",
        "3-5件",
    )

    # --- {b2_causal,b3_minimal}/writer_input.md, prompt_writer.txt ---
    for cond in NEW_CONDITIONS:
        material = build_selected_brief_material(ledger_text, SELECTED_FACT_IDS[cond])
        save_text(out_path(out_dir, cond, "writer_input.md"), material)
        save_text(out_path(out_dir, cond, "prompt_writer.txt"),
                   fw1.build_writer_prompt(material))
    print("[OK] prep: research/full_ledger.md, fact_selection_{b2,b3}.md, "
          "{b2_causal,b3_minimal}/writer_input.md, control/, b1/ written")


# ------------------------------------------------------------
# run / adapt: Trial-01の汎用実装(条件名に依存しない)をそのまま呼び出す
# ------------------------------------------------------------
def cmd_run(args):
    fw1.cmd_run(args)


def cmd_adapt(args):
    fw1.cmd_adapt(args)


# ------------------------------------------------------------
# observe: 4条件、語数・段落数・見出し・箇条書きの機械集計
# ------------------------------------------------------------
def cmd_observe(args):
    out_dir = args.out_dir
    result = {}
    for cond in ALL_CONDITIONS:
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
                "paragraph_count": fw1._paragraph_count(text),
            }
            if stage == "english":
                entry[stage]["word_count"] = fw1._word_count_en(text)
                entry[stage]["heading_count"] = fw1._heading_count(text)
                entry[stage]["bullet_count"] = fw1._bullet_count(text)
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
# factdiff: 4条件、Fact ID別キーワードヒットの機械補助(最終判定はSonnet目視)
# ------------------------------------------------------------
def cmd_factdiff(args):
    out_dir = args.out_dir
    result = {}
    for cond in ALL_CONDITIONS:
        cond_dir = out_path(out_dir, cond)
        cond_result = {}
        for stage, fname in [("r2", "r2.md"), ("english", "english.md")]:
            p = out_path(cond_dir, fname)
            if not os.path.exists(p):
                continue
            text = load_text(p)
            hits = {}
            for fid, kws in fw1.FACT_KEYWORDS.items():
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
# cost: b2_causal/b3_minimalの新規call分のみ(control/b1は0 call)
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
    # 注: writer段階(original/r1/r2)はfw1.cmd_run経由でtrial02.call_fresh/
    # call_with_previous_response_idを再利用しており、これらは内部で
    # trial02自身のTHEME_TAG("NEWS_ITERATIVE_ENTERTAINMENT_TRIAL_02")で
    # ログする。Adaptation段階はfw1.cmd_adapt経由のためfw1自身のTHEME_TAG
    # ("NEWS_FAMILY_X_WRITER_FACT_SELECTION_TRIAL_01")でログする。この
    # raw_usage_log.jsonl自体は本Trial専用out_dirにのみ書かれるため、
    # 該当し得る全themeを対象に含める。
    entries = [e for e in entries
               if e.get("theme") in (THEME_TAG, "NEWS_ITERATIVE_ENTERTAINMENT_TRIAL_02",
                                      fw1.THEME_TAG)]

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
        "note": "control/b1はTrial-01出力のコピー再掲であり新規API呼び出し"
                "0件・費用¥0。ここに集計されるのはb2_causal/b3_minimalの"
                "新規call分のみ。",
    }
    save_json(out_path(out_dir, "cost.json"), result)
    print(f"[OK] cost: total_jpy={result['total_jpy']} total_calls={result['total_calls']}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_prep = sub.add_parser("prep")
    p_prep.add_argument("--out-dir", required=True)
    p_prep.add_argument("--force", action="store_true")
    p_prep.set_defaults(func=cmd_prep)

    p_run = sub.add_parser("run")
    p_run.add_argument("--out-dir", required=True)
    p_run.add_argument("--condition", required=True, choices=NEW_CONDITIONS)
    p_run.add_argument("--force", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_adapt = sub.add_parser("adapt")
    p_adapt.add_argument("--out-dir", required=True)
    p_adapt.add_argument("--condition", required=True, choices=NEW_CONDITIONS)
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
