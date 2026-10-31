# V安全試験セット構築(TRIAL_PLAN_02 §6)。公開訳(ev03 pool)の1文だけを改変した対訳unitを作る。実行前に固定してcommit。API 0。
import json, os, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
pool = json.load(open(os.path.join(D, "ev03", "pool_all_generated_03.json"), encoding="utf-8"))
EDITS = [  # (type, slug-prefix, level, part, sid-suffix, old, new)
 ("number", "family_x_ai_chat", "adv", "adv_15", "s016", "40.7%", "14.7%"),
 ("number", "family_x_ai_chat", "adv", "adv_17", "s030", "9.5%", "95%"),
 ("number", "family_x_moon", "std", "std_20", "s061", "8,900", "800"),
 ("number", "family_x_moon", "adv", "adv_20", "s047", "42〜46メートル", "42〜64メートル"),
 ("number", "family_y_production_redelivery", "adv", "adv_13", "s003", "3人", "2人"),
 ("inversion", "family_x_ai_chat", "adv", "adv_20", "s046", "明確には減らなかった", "明確に減った"),
 ("inversion", "family_x_jwst", "std", "std_21", "s060", "天体は確認されなかった", "天体が確認された"),
 ("inversion", "family_x_moon", "adv", "adv_17", "s032", "数値は直接比較できません", "数値は直接比較できます"),
 ("inversion", "family_x_moon", "adv", "adv_15", "s018", "どれほど縮んだか", "どれほど膨らんだか"),
 ("inversion", "family_x_jwst", "adv", "adv_17", "s032", "画像には対応する物体は写っていなかった", "画像には対応する物体が写っていた"),
 ("omission", "family_x_ai_chat", "std", "std_21", "s052", "広告を見た後でも人々が", "人々が"),
 ("omission", "family_x_moon", "std", "std_20", "s062", "隙間の多い厚い岩石層が冷却を遅らせ、モデルがはるかに大きな縮小を予測する理由の説明にもなる可能性がある。", ""),
 ("omission", "family_x_jwst", "std", "std_21", "s061", "となったが、その発生源を特定するにはさらなる観測が必要だ", "となった"),
 ("omission", "family_x_ai_chat", "adv", "adv_20", "s047", "広告に気づいた後でも", ""),
 ("omission", "family_x_moon", "adv", "adv_05", "s003", "また、月がどのように冷えたのかを理解するうえで、どのような手がかりになる可能性があるのでしょうか。", ""),
 ("mixin", "family_x_moon", "adv", "adv_15", "s019", "その推定は月の歴史全体", "その推定は厚い岩石層の影響も含めて月の歴史全体"),
 ("mixin", "family_x_ai_chat", "adv", "adv_17", "s031", "選択が明確に", "売り込みに気づいた9.5%の人の選択が明確に"),
 ("mixin", "family_x_jwst", "adv", "adv_19", "s045", "原因は不明で", "JWSTの深い画像でも原因は不明で"),
 ("mixin", "family_y_production_redelivery", "adv", "adv_05", "s002", "配達の流れと、", "配達の流れと、再配達に料金を取る案を含め、"),
 ("mixin", "family_x_moon", "adv", "adv_13", "s004", "月面をどのように調査したか", "月面の崖をどのように調べて8,900か所を地図にしたか"),
]
units = []
for i, (ty, slugp, lv, part, sidsuf, old, new) in enumerate(EDITS):
    rows = [r for r in pool if r["dir"].startswith(slugp) and r["level"] == lv and r["part"] == part]
    assert rows, (slugp, lv, part)
    slug = rows[0]["dir"]; pairs = []; target = None
    for r in rows:
        ja = r["ja"]
        if r["sid"].endswith("-" + sidsuf):
            assert old in ja, (slugp, part, sidsuf, old, ja)
            ja = ja.replace(old, new, 1); target = r["sid"]
        pairs.append({"sid": r["sid"], "en": r["en"], "ja": ja})
    assert target
    units.append({"id": f"V{i+1:02d}", "type": ty, "slug": slug, "level": lv, "part": part, "target_sid": target, "pairs": pairs})
json.dump({"units": units}, open(os.path.join(D, "ev05_vsafety", "vsafety_set_03.json") if os.path.isdir(os.path.join(D, "ev05_vsafety")) else sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(units), {t: sum(1 for u in units if u["type"] == t) for t in ("number", "inversion", "omission", "mixin")})
