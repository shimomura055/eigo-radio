# -*- coding: utf-8 -*-
"""任意ブロック方式A用の評価対象を作る(API非呼び出し)。space_weapons旧腕EN最終稿27文のうち22文を対象にし、
各文へSonnetが台帳から人手で事前対応付けしたFact(F-xxx)を割り当てる。Fact本文は台帳から逐語抽出。
mapping_quality/mapping_note は評価LLMへ渡さない監査用(run_eval_01.PASS_KEYS外)。人間既知・Checker情報の別ファイルは読まない。"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "factlock_astra_e2e_trial_01", "runs", "space_weapons")
ART = os.path.join(ROOT, "old", "b1b", "article.md")
LED = os.path.join(ROOT, "shared", "ledger.txt")

# 記事のうち「# 見出し」「## In one line」見出し行を除く本文を、人手で文分割(27文)。1,4,20,21,25は質問/断片/助言のため対象外(22文が対象)。
SENT = [
 "When you hear “space weapon,” do you picture a satellite being shot down?",
 "But the key to understanding this news is not how powerful the weapon is.",
 "It is its address.",
 "Is it on the ground or in orbit?",
 "Once we make that distinction, the story becomes much easier to follow.",
 "The U.S. Secretary of the Air Force said that the U.S. is putting “space-control weapons” in orbit to protect U.S. forces from hostile actions.",
 "An official U.S. government article describes this statement as the first public acknowledgment that the Space Force had put weapons in space.",
 "But the name of the device and exactly what it can do in an attack have not been made public.",
 "So we know the weapon’s address, but its details are still unclear.",
 "There is a past example of a weapon that destroys satellites.",
 "In 2021, Russia launched a missile from the ground and destroyed a satellite.",
 "This was a case of a weapon based on the ground being fired.",
 "The statement this time is about weapons themselves being put in orbit.",
 "“A weapon that destroys satellites” and “a weapon in orbit” are not necessarily the same thing.",
 "Also, the phrase “operations to counter actions in space” can have a broad meaning.",
 "The U.S. Space Force says it includes not only activity in satellite orbits, but also communication with satellites and activities carried out using equipment on the ground.",
 "In other words, whether or not there are weapons in space does not tell us the whole story of these operations.",
 "GPS, missile tracking, watching what is happening in space, and making satellite networks harder to damage are also missions of the Space Force.",
 "We need to think about the work of using and protecting satellites separately from putting weapons designed to attack in orbit.",
 "Does the Outer Space Treaty ban all space weapons?",
 "No.",
 "It bans putting nuclear weapons and other weapons of mass destruction in orbit, but it does not ban space weapons in general.",
 "That does not mean this deployment has been ruled legal, either.",
 "This rule alone does not let us make a judgment about this specific case.",
 "Before using the broad label “space weapon,” check its address, its mission, and what the treaty covers.",
 "Rather than deciding what happened in space right away, this news is more interesting to read if we start by sorting out the terms.",
 "The U.S. says it has placed weapons in orbit, though what they can do remains unclear.",
]
# index(0始まり) -> (fact_id, mapping_quality, note)  direct=文の主張が当該Factに直接対応 / partial=一部または語用法のみ対応 / weak=該当Factが乏しい枠組み文
MAP = {
 1: ("F-001", "weak", "枠組み文('住所'の比喩)。台帳に直接対応するFactなし、最寄りのF-001を割当"),
 2: ("F-001", "weak", "同上"),
 4: ("F-011", "weak", "地上/軌道の区別の効用という解釈文。最寄りとして用語定義F-011を割当"),
 5: ("F-001", "direct", "長官発言(軌道上space control weapons)"),
 6: ("F-001", "direct", "公式記事が初めて認めた発言として記録"),
 7: ("F-001", "partial", "『名称・攻撃能力が非公開』はFactに明記なし(notes_for_writer側にのみ『推測で補わない』)。不在断定型"),
 8: ("F-001", "partial", "'address'と'details unclear'の対比。Factは能力に触れない"),
 9: ("F-003", "partial", "『過去の衛星破壊兵器の例』はF-003(2021年ロシアASAT)"),
 10: ("F-003", "direct", "2021年、ロシア、地上発射、衛星破壊"),
 11: ("F-003", "direct", "地上発射型の直接上昇式ASAT"),
 12: ("F-001", "direct", "今回の発言=兵器そのものを軌道に配備"),
 13: ("F-003", "partial", "『衛星破壊兵器≠軌道上兵器』という区別はF-003のnotes_for_writer相当で、Fact本文には明記なし"),
 14: ("F-011", "partial", "『counter actions in space』の語義が広いこと=F-011のcounterspace定義"),
 15: ("F-011", "direct", "軌道・リンク・地上の各セグメント"),
 16: ("F-012", "partial", "『兵器の有無だけでは全体像にならない』はF-011/012の分類から導く解釈"),
 17: ("F-015", "direct", "GPS、ミサイル追跡、宇宙領域認識、レジリエンス"),
 18: ("F-015", "partial", "『使用・保護と攻撃兵器配備を分けて考える』はF-015の説明末尾に対応"),
 21: ("F-016", "direct", "第4条: 核・大量破壊兵器の軌道配備禁止、全面禁止ではない"),
 22: ("F-017", "partial", "『この配備が合法と決まったわけではない』はF-017の一般原則と個別事案判断の区別(Fact本文は第3条の義務のみ)"),
 23: ("F-017", "partial", "同上"),
 25: ("F-001", "weak", "締めの解釈文。最寄りのF-001を割当"),
 26: ("F-001", "direct", "米国が軌道上に兵器を配備と述べた/能力は不明"),
}
EXCLUDED = {0, 3, 19, 20, 24}

def facts():
    out = {}
    for blk in open(LED, encoding="utf-8").read().split("\n\n"):
        m = re.match(r"\[VERIFIED\] (F-\d+): (.*?)(\(\[[^\]]+\]\([^)]*\)\))?\n", blk + "\n", re.S)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out

def main():
    art = open(ART, encoding="utf-8").read()
    F = facts()
    items = []
    n = 0
    for i, s in enumerate(SENT):
        assert s in art, s
        if i in EXCLUDED:
            continue
        fid, q, note = MAP[i]
        n += 1
        items.append(dict(case_id="ob%02d" % n, fact=F[fid], target_sentence=s,
                          context_before=SENT[i - 1] if i > 0 else "", context_after=SENT[i + 1] if i + 1 < len(SENT) else "",
                          context_source="old/b1b/article.md 隣接文", sentence_index=i + 1, mapped_fact_id=fid,
                          mapping_quality=q, mapping_note=note))
    assert len(items) == 22
    with open(os.path.join(HERE, "optional_block_items_01.json"), "w", encoding="utf-8") as f:
        json.dump(dict(article=os.path.relpath(ART, HERE).replace("\\", "/"), ledger=os.path.relpath(LED, HERE).replace("\\", "/"),
                       method="OPTIONAL_BLOCK_01 方式A(Sonnetが台帳から人手で事前対応付け)", items=items), f, ensure_ascii=False, indent=1)
    print("ok", len(items), "quality:", {q: sum(1 for x in items if x["mapping_quality"] == q) for q in ("direct", "partial", "weak")})

if __name__ == "__main__":
    main()
