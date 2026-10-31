# V安全試験セット構築(TRIAL_PLAN_02 §6)。公開訳(ev03 pool)の1文だけを改変した対訳unitを作る。実行前に固定してcommit。API 0。
import json, os, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
pool = json.load(open(os.path.join(D, "ev03", "pool_all_generated_03.json"), encoding="utf-8"))
EDITS = [  # セットB(subtle): 文脈由来の細部の混入・微妙な反転・修飾語の欠落・近接した数値。セットAが全件捕捉(天井)だったため識別力を上げる追加(実行前に固定)
 ("mixin", "family_x_moon", "adv", "adv_19", "s045", "月がどのように冷えたのかという疑問", "厚い岩石層が月の冷却をどう遅らせたのかという疑問"),
 ("mixin", "family_x_jwst", "adv", "adv_05", "s002", "宇宙から届いた信号", "宇宙から届いた繰り返し現れる信号"),
 ("mixin", "family_x_ai_chat", "adv", "adv_05", "s001", "スポンサー提供の商品を宣伝", "スポンサー提供の電子書籍を宣伝"),
 ("mixin", "family_y_production_redelivery", "adv", "adv_21", "s034", "同じ問題が", "同じ再配達料金の問題が"),
 ("mixin", "family_x_ai_chat", "adv", "adv_19", "s044", "推薦されている商品だけでなく", "推薦されている電子書籍だけでなく"),
 ("inversion", "family_x_moon", "adv", "adv_15", "s019", "月の歴史全体を対象としている", "月の歴史の一部だけを対象としている"),
 ("inversion", "family_x_ai_chat", "adv", "adv_15", "s017", "実際に売り込みに気づいた人", "実際に売り込みに気づかなかった人"),
 ("inversion", "family_x_moon", "adv", "adv_19", "s044", "どのように変化したかを", "どのように変化しなかったかを"),
 ("inversion", "family_y_production_redelivery", "adv", "adv_05", "s001", "それを待っている人だけでなく、ほかの人にも影響を及ぼすことがあります", "それを待っている人にしか影響しません"),
 ("inversion", "family_x_moon", "std", "std_20", "s062", "これだけではない", "これがすべてである"),
 ("omission", "family_x_ai_chat", "adv", "adv_17", "s030", "これまでに、", ""),
 ("omission", "family_x_ai_chat", "std", "std_21", "s051", "明確には下がりませんでした", "下がりませんでした"),
 ("omission", "family_x_moon", "adv", "adv_20", "s047", "8,900か所以上", "8,900か所"),
 ("omission", "family_x_jwst", "adv", "adv_19", "s044", "繰り返し現れる光の筋", "光の筋"),
 ("omission", "family_x_moon", "adv", "adv_17", "s032", "より後の時期に生じた縮小", "縮小"),
 ("number", "family_x_ai_chat", "adv", "adv_15", "s016", "40.7%", "40.1%"),
 ("number", "family_x_moon", "adv", "adv_20", "s047", "8,900", "8,500"),
 ("number", "family_x_moon", "std", "std_20", "s061", "42〜46メートル", "42〜48メートル"),
 ("number", "family_x_ai_chat", "adv", "adv_17", "s030", "9.5%", "9.6%"),
 ("number", "family_x_moon", "adv", "adv_20", "s047", "42〜46メートル", "41〜46メートル"),
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
    units.append({"id": f"W{i+1:02d}", "type": ty, "slug": slug, "level": lv, "part": part, "target_sid": target, "pairs": pairs})
json.dump({"units": units}, open(os.path.join(D, "ev05_vsafety", "vsafety_set_03b.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(units), {t: sum(1 for u in units if u["type"] == t) for t in ("number", "inversion", "omission", "mixin")})
