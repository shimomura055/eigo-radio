# -*- coding: utf-8 -*-
"""委任_03 P3/P4 記事モードのマニフェスト生成(ラベルは読まない。casebank_01.jsonのarticles/cases[*].article_full_textの『パス』だけ使う)。
出力: ../casebank/p3_manifest_01.json  (role: arm_new_ja / arm_new_en / arm_old_ja / arm_old_en / dev_known / holdout_known)
 - arm_*: factlock_astra_e2e_trial_01 の新旧各腕の最終JA(revision2)とEN Advanced(b1b)。台帳は記事run直下のresearch_ledger。
 - dev_known: 既知重大(dev側ケース)を含む元記事。保留側ケースを含む記事は使わない(holdout_knownへ)。
     ai_control_p2rep2_cyc0 は、Checker cycle0 の Rewrite後EN本文(rf_5qddqw『84%』の挿入を含む)を抽出した派生記事。
 - holdout_known: 保留側の既知重大を含む元記事(P4で1回のみ使う。P3では使わない)。台帳はblindケースに載っている全台帳を使う。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CB = os.path.join(HERE, "..", "casebank")


def main():
    d = json.load(open(os.path.join(CB, "casebank_01.json"), encoding="utf-8"))
    cases = {c["case_id"]: c for c in d["cases"]}
    man = []
    for a in d["articles"]:
        for ver, role_suffix in (("JA_R2", "ja"), ("EN_Adv_b1b", "en")):
            f = a["files"].get(ver)
            if not f:
                continue
            man.append(dict(article_id="%s_%s_%s" % (a["theme"], a["arm"], role_suffix), role="arm_%s_%s" % (a["arm"], role_suffix),
                            theme=a["theme"], arm=a["arm"], lang=role_suffix.upper(), article_path=f["path"], ledger_path=a["ledger"]))
    # dev既知重大の元記事(保留側ケースを含まないもののみ)
    ext_dir = CB
    ext = os.path.join(ext_dir, "p3_article_ai_control_p2rep2_cyc0_01.md")
    if not os.path.exists(ext):
        src = os.path.join(REPO, "er052_output/open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2/checker/runs/meta_run03_advanced.json")
        j = json.load(open(src, encoding="utf-8"))
        open(ext, "w", encoding="utf-8").write(j["cycles"][0]["en_text_after_rewrite"])
    def rel(p):
        return os.path.relpath(p, REPO).replace("\\", "/")
    man.append(dict(article_id="dev_meta_p2rep2_b1b", role="dev_known", theme="meta", arm="allfact_p2rep2", lang="EN",
                    article_path=cases["rf_sq5c2g"]["article_full_text"], ledger_case="rf_sq5c2g", ledger_split="dev"))
    man.append(dict(article_id="dev_space_p2rep2_b1b", role="dev_known", theme="space_weapons", arm="allfact_p2rep2", lang="EN",
                    article_path=cases["rf_apqtyt"]["article_full_text"], ledger_case="rf_apqtyt", ledger_split="dev"))
    man.append(dict(article_id="dev_ai_control_p2rep2_cyc0", role="dev_known", theme="ai_control", arm="allfact_p2rep2_cyc0_rewrite", lang="EN",
                    article_path=rel(ext), ledger_case="rf_5qddqw", ledger_split="dev"))
    hold = [("holdout_meta_refresh_run03_b1b", "rf_y84g5r", "meta"), ("holdout_ai_control_jb9k_b1b", "rf_emcgyx", "ai_control"),
            ("holdout_space_p2rep2_ja", "rf_hdr8y4", "space_weapons"), ("holdout_ai_control_p2rep1_b1b", "rf_7suvyn", "ai_control"),
            ("holdout_hormuz_T0M0rep2_b1b", "rf_665ga9", "hormuz"), ("holdout_hormuz_an3_b1b", "rf_t9nxuv", "hormuz"),
            ("holdout_hormuz_b3div_run02_b1b", "rf_p4mtyd", "hormuz")]
    for aid, cid, theme in hold:
        man.append(dict(article_id=aid, role="holdout_known", theme=theme, arm="known_incident_source", lang=cases[cid]["lang"],
                        article_path=cases[cid]["article_full_text"], ledger_case=cid, ledger_split="holdout"))
    for m in man:
        assert os.path.isfile(os.path.join(REPO, m["article_path"])), m
        if "ledger_path" in m:
            assert os.path.isfile(os.path.join(REPO, m["ledger_path"])), m
    json.dump(man, open(os.path.join(CB, "p3_manifest_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(m["role"] for m in man), len(man))


if __name__ == "__main__":
    main()
