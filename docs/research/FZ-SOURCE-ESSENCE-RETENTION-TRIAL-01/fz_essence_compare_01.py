# -*- coding: utf-8 -*-
"""比較原稿の機械生成(LLM呼出0): COMPARISON_01.md(告げ口心臓)/COMPARISON_02.md(Phase 2、完成版 vs Trial)。"""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, HERE)
import fz_essence_metrics_01 as m   # noqa: E402

T = "er026_output/family_z_dev_trials/fz_essence_01"
P = "er026_output/family_z_production_e2e_01"
rd = lambda p: open(p, encoding="utf-8").read().strip()


def mline(p):
    x = m.metrics(open(p, encoding="utf-8").read())
    return (f"語数{x['words']} / 段落{x['paragraphs']} / 平均文長{x['avg_sentence_len']} / 地の文 一人称語{x['fp_narration']}・三人称語{x['tp_narration']}・you{x['you_narration']}")


def section(title, p):
    return f"### {title}\n\n`{p}`  ({mline(p)})\n\n" + rd(p) + "\n"


def phase1():
    tth = f"{P}/the_tell_tale_heart/run_sf_prod_01/writer"
    src = rd("er026_seeds/the_tell_tale_heart/story.md")
    paras = [x for x in re.split(r"\n\s*\n", src) if x.strip()]
    out = ["# COMPARISON_01: 『告げ口心臓』Advanced 比較原稿(Fable盲検7観点の読み合わせ用)", "",
           "作成: 2026-10-25 / 生成: 機械(LLM呼出0)。**公開版・現行完成版は不変**。観点: 1語り口 2心理 3緊張 4心臓音 5自白 6因果 7テンポ(各0/1/2)。",
           "読む順の推奨: 原作抜粋 → 現行Adv(三人称・ユーザーNG) → Trial Adv s1/s2(一人称) → Trial Std。", "",
           "## A. 原作(抜粋: 冒頭・8夜目の心臓音・結末)", "", *[x.strip() + "\n" for x in (paras[:2] + paras[-3:])],
           "## B. 現行(ユーザーNG)", "", section("現行Adv(r2、三人称)", f"{tth}/r2.md"), section("現行Std(std、一人称へ偶然復帰)", f"{tth}/std.md"),
           "## C. Trial(案A=narration_voice欄+Narration行+REVISE置換。DEV Seed。Production不変)", ""]
    for k in (1, 2):
        out += [f"#### Trial サンプル{k}", "", section(f"Trial Adv s{k}(r2)", f"{T}/the_tell_tale_heart/1b_s{k}/writer/r2.md"),
                section(f"Trial Std s{k}(std)", f"{T}/the_tell_tale_heart/1b_s{k}/writer/std.md")]
    out += ["## D. 参考: R0(一人称・Production)", "", section("Production r0", f"{tth}/r0.md")]
    open(f"{HERE}/COMPARISON_01.md", "w", encoding="utf-8").write("\n".join(out))


def phase2():
    out = ["# COMPARISON_02: Phase 2 既存Z作品の完成版 vs Trial(副作用確認。Fable読み用)", "",
           "完成版=`run_sf_prod_01`のAdv(r2)/Std。Trial=narration_voice欄(DEV Seed)付き案A、各1サンプル。公開版は不変。", ""]
    for s, title in (("the_gift_of_the_magi", "賢者の贈り物"), ("the_open_window", "開いた窓"), ("the_monkeys_paw", "猿の手")):
        out += [f"## {title} ({s})", ""]
        out += [section("完成版 Adv", f"{P}/{s}/run_sf_prod_01/writer/r2.md"), section("Trial Adv", f"{T}/{s}/p2_s1/writer/r2.md"),
                section("完成版 Std", f"{P}/{s}/run_sf_prod_01/writer/std.md"), section("Trial Std", f"{T}/{s}/p2_s1/writer/std.md")]
    open(f"{HERE}/COMPARISON_02.md", "w", encoding="utf-8").write("\n".join(out))


if __name__ == "__main__":
    phase1()
    phase2()
    print("ok")
