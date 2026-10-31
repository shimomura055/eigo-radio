# -*- coding: utf-8 -*-
"""JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_01: 検証セット構築(API 0・決定論)。
出力: eval_set/articles.json, eval_set/items.json, eval_set/summary.json
入力: JA-GLOSS-NUANCE-01/data/{published_glosses_01,newgen_records_all_01}.json、user_test/*/enduser/data/article.json、
      git origin/main の gloss_alignment_prompt.txt(記事本文)、FX-UNTIDINESS-COMMENT4 old_entry.json(things left out)
T3(合成)は T3_SPECS に人手で書いた置換訳(件数明示)。個別辞書・特定語の例外ルールではなく、検証データの作成のみ。
"""
import json, os, re, subprocess, collections, html
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
OUT = os.path.join(ROOT, "docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/eval_set")
NU = os.path.join(ROOT, "docs/research/JA-GLOSS-NUANCE-01/data")
J = lambda p: json.load(open(p, encoding="utf-8"))


CJK = re.compile("[぀-ヿ一-鿿]")


def git_show(path):
    r = subprocess.run(["git", "show", "origin/main:" + path], cwd=ROOT, capture_output=True)
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower().replace("’", "'")).strip()


def split_sents(text):
    t = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?”])\s+(?=[A-Z“\"])", t) if s.strip()]


ARTICLES = {}


def add_article(key, level, sents, family):
    a = ARTICLES.setdefault(key, {"family": family})
    a[level] = sents


def ctx_for(key, level, sentence):
    sents = ARTICLES[key][level]
    ns = norm(sentence)
    idx = None
    for i, s in enumerate(sents):
        n = norm(s)
        if ns and (ns in n or n in ns):
            idx = i
            break
    if idx is None:
        for i, s in enumerate(sents):
            if ns[:40] and ns[:40] in norm(s):
                idx = i
                break
    if idx is None:
        return None, None, None
    return idx, " ".join(sents[max(0, idx - 2):idx]), " ".join(sents[idx + 1:idx + 3])


pub = J(os.path.join(NU, "published_glosses_01.json"))
LEVMAP = {"std": "Standard", "adv": "Advanced", "a2": "Standard", "b1b": "Advanced"}
art_dirs = {r["article"]: r["family"] for r in pub}
expl = {}
for key, fam in art_dirs.items():
    a = J(os.path.join(ROOT, "user_test", key, "enduser/data/article.json"))
    for lv in ("std", "adv"):
        L = a["levels"].get(lv)
        if not L:
            continue
        sents = []
        for p in L["parts"]:
            if p.get("kind") in ("topic", "story", "oneline", "comment", "preview"):
                for para in p.get("paragraphs", []):
                    for s in para:
                        t = html.unescape(re.sub(r"<[^>]+>", "", s.get("text") or ""))
                        if t and t not in sents and not CJK.search(t):
                            sents.append(t)
        add_article(key, lv, sents, fam)
        for v in L.get("vocab", []):
            d = {f["label"]: re.sub(r"<[^>]+>", "", f["html"]) for f in v["fields"]}
            expl[(key, lv, v["heading"])] = d.get("解説", "")

HELD_OUT_ARTICLES = {"family_x_jwst_mystery_emission_line_01", "family_x_moon_shrinking_reselect_01",
                     "family_y_production_surname_choice_01", "family_z_yuki_onna_01"}
T1_PUB = {45: "ユーザー原文§3: 本文は裁判の比喩。適切な訳は『評決』(ユーザー指摘)", 39: "同上(Standard側)",
          35: "ユーザー原文§3の例『culprit→原因』。責められる側のニュアンス(OPEN-630 CURRENT_STATE_01 §5-3 パターンH)"}
T4_PUB = {7: "『複雑な要素』= complications は『厄介な事情』の含み", 13: "frustrate: 探偵のたとえで『悩ませる』の含み", 18: "同上",
          34: "porous: 定義風の訳(『多孔質の』の定訳あり)", 36: "puzzling: 『不可解な』の含み",
          11: "turn something around: 『逆にする』は『好転させる』の含みを欠く可能性",
          19: "make room for: 『時間』に限定されるか", 3: "sponsored: 説明的な訳(『スポンサー付きの』)",
          25: "on the scale of: 『並みの規模』の妥当性", 68: "sink for ever: 比喩訳(永遠の眠り)の妥当性"}
T3_SPECS = {
    1: "口笛を吹く", 2: "助言を無視する", 4: "加速させる", 24: "ざっと目を通す", 26: "前者", 38: "～に点を加える",
    46: "弁護士", 49: "～の上に置いて", 63: "領主", 70: "中くらいの大きさ", 73: "実行", 72: "これほどの信頼を失う",
    10: "広げる", 17: "天候の", 29: "熱を逃がす", 30: "運動する", 32: "ほぼ正確である", 56: "相対的な",
    57: "喜んで受け入れる", 59: "人を後押しする", 77: "雪", 82: "離婚した",
}
items = []


def pub_item(r, gloss, tier, label, note, severity=None, src=None, synth_of=None):
    key, lv = r["article"], r["level"]
    idx, cb, ca = ctx_for(key, lv, r["sentence_en"])
    return {
        "expression": r["heading"], "current_ja": gloss, "sentence_en": r["sentence_en"], "context_before": cb,
        "context_after": ca, "sentence_found_in_article": idx is not None, "article_key": key, "level": LEVMAP[lv],
        "family": r["family"], "existing_explanation_ja": expl.get((key, lv, r["heading"]), ""),
        "existing_sentence_ja": r["sentence_ja"], "source": src, "tier": tier, "label": label, "severity": severity,
        "note": note, "synthetic_of": synth_of, "split": "held_out" if key in HELD_OUT_ARTICLES else "dev",
        "item_kind": "vocab(published)",
    }


for i, r in enumerate(pub):
    if i in T1_PUB:
        items.append(pub_item(r, r["gloss_ja"], "T1", "problem", T1_PUB[i], "major" if i in (39, 45) else "minor",
                              "ユーザー指摘(原文§3)+公開ページ article.json"))
    elif i in T4_PUB:
        items.append(pub_item(r, r["gloss_ja"], "T4", "hold", T4_PUB[i], None, "公開済み(HR承認)・agent事前所見のみ"))
    else:
        items.append(pub_item(r, r["gloss_ja"], "T2", "normal", "HR承認済み・公開済みで修正指示なし(正常と推定)", None,
                              "公開ページ article.json(HR承認済み)"))
for i, g in T3_SPECS.items():
    r = pub[i]
    items.append(pub_item(r, g, "T3", "problem", "合成: 承認済み正常訳『%s』を意味の異なる訳へ置換" % r["gloss_ja"], "major",
                          "合成(人手作成)", synth_of=r["gloss_ja"]))

nw = J(os.path.join(NU, "newgen_records_all_01.json"))
prompts = subprocess.run(["git", "ls-tree", "-r", "origin/main", "--name-only"], cwd=ROOT,
                         capture_output=True).stdout.decode("utf-8").splitlines()
prompts = [p for p in prompts if p.endswith("gloss_alignment_prompt.txt")]


def run_article(run):
    cands = [p for p in prompts if p.startswith(run + "/")]
    if not cands:
        return None
    t = git_show(sorted(cands)[0])
    if not t or "【記事本文(参考)】" not in t:
        return None
    return t.split("【記事本文(参考)】", 1)[1].strip()


def fam_of(run):
    return {"er019_output": "X", "er121_output": "Y", "er026_output": "Z"}.get(run.split("/")[0], "?")


def rec_item(term, gloss_pat, run_pat, tier, label, note, severity, src, split, force_gloss=None):
    for r in nw:
        if r["key_phrase"].lower() == term and (gloss_pat is None or r["gloss"] == gloss_pat) and run_pat in r["run"]:
            body = run_article(r["run"])
            if not body:
                continue
            parts = r["run"].split("/")
            if parts[-1] in LEVMAP:
                slug, lv = parts[-2], LEVMAP[parts[-1]]
            else:  # level無しのrun dir(Z melos等)はAdvanced扱い(記録上b1b)
                slug, lv = parts[-1], "Advanced"
            lk = "adv" if lv == "Advanced" else "std"
            key = "rec:" + slug
            add_article(key, lk, split_sents(body), fam_of(r["run"]))
            sent = r["source_sentence"]
            idx, cb, ca = ctx_for(key, lk, sent)
            return {"expression": r["key_phrase"], "current_ja": force_gloss or r["gloss"], "sentence_en": sent,
                    "context_before": cb, "context_after": ca, "sentence_found_in_article": idx is not None,
                    "article_key": key, "level": lv, "family": fam_of(r["run"]), "existing_explanation_ja": "",
                    "existing_sentence_ja": "", "source": src + " / " + r["run"], "tier": tier, "label": label,
                    "severity": severity, "note": note, "synthetic_of": None, "split": split,
                    "item_kind": "kp_candidate(record)"}
    return None


EXTRA = [
    ("charge", "非難", "untidiness_family_resource__run_fx4_01/a2", "T1", "problem", "ユーザー原文§3の例『charge→非難』。本文は裁判のたとえで『罪状・容疑』の含み", "major", "ユーザー指摘(原文§3)+記録", "dev", None),
    ("radius", "中心から外側までの長さ", "moon_shrinking__run_reselect_01/b1b", "T1", "problem", "ユーザー原文§3の例。定訳『半径』があるのに定義文へ言い換え(パターンD)", "minor", "ユーザー指摘(原文§3)+記録", "held_out", None),
    ("equivalent width", "等価幅", "jwst_mystery_emission_line__run_fx4_01/a2", "T1", "problem", "ユーザーHR回答(2026-10-30、confirmed_selection history gloss_before→『等価幅』): 専門用語の定訳を使っていない", "minor", "HR修正記録(er019_output/.../jwst.../key_phrases/confirmed_selection.json history)", "held_out", "光の線の特徴を表す幅"),
    ("equivalent width", "等価幅", "jwst_mystery_emission_line__run_fx4_01/a2", "T1", "problem", "同上(修正前の別版)", "minor", "HR修正記録(同上)", "held_out", "スペクトル線の強さを示す等価幅"),
    ("exception", "一般の決まりに当てはまらない場合", "uk_train_speaker_playback", "T4", "hold", "定訳『例外』あり→定義文化(パターンD)。ただし文脈で『例外的に許される場合』は自然とも言える", None, "OPEN-630 survey", "dev", None),
    ("shepherd", "羊の世話をする人", "melos", "T4", "hold", "定訳『羊飼い』あり→定義文化(パターンD)", None, "OPEN-630 survey", "dev", None),
    ("insulation", "熱を逃がしにくくするもの", "moon_shrinking__run_reselect_01/b1b", "T4", "hold", "定訳『断熱(材)』あり→定義文化", None, "OPEN-630 survey", "held_out", None),
    ("campaign", "呼びかけ運動", "uk_train_speaker_playback", "T4", "hold", "『キャンペーン』定着語あり→言い換え", None, "OPEN-630 survey", "dev", None),
    ("errand", "用事を済ませる外出", "redelivery_fee", "T4", "hold", "『用事・お使い』定訳→定義文化", None, "OPEN-630 survey", "dev", None),
    ("account", "話", "meta_waddle_world", "T4", "hold", "account=『(出来事の)記述・報告』→一般語『話』", None, "OPEN-630 survey", "dev", None),
    ("investigation", "調査", "jwst_mystery_emission_line__run_fx4_01/a2", "T4", "hold", "探偵のたとえで『捜査』の含み", None, "OPEN-630 survey", "held_out", None),
]
miss = []
for term, g, rp, tier, label, note, sev, src, split, fg in EXTRA:
    it = rec_item(term, g, rp, tier, label, note, sev, src, split, force_gloss=fg)
    if it:
        items.append(it)
    else:
        miss.append((term, rp))

old = J(os.path.join(ROOT, "docs/research/FX-UNTIDINESS-COMMENT4-JA-GLOSS-FIX-01/ev01/retranslate/old_entry.json"))
KEY = "family_x_untidiness_family_resource_01"
tl = {"expression": "things left out", "current_ja": "省かれたもの",
      "sentence_en": "The story asks us to look at things left out with care, because they may have a purpose.",
      "article_key": KEY, "level": "Advanced", "family": "X", "existing_explanation_ja": "",
      "existing_sentence_ja": old["old_entry"]["ja"][0],
      "source": "ユーザー指摘(原文§3・OPEN-631 J4)。FX-UNTIDINESS-COMMENT4-JA-GLOSS-FIX-01/ev01/retranslate/old_entry.json(修正前の日本語訳)",
      "tier": "T1", "label": "problem", "severity": "major",
      "note": "本文では『出しっぱなしのもの』(leave things out=出したままにしておく)。『省かれたもの』は omitted の意味に誤読(ユーザー指摘)",
      "synthetic_of": None, "split": "dev", "item_kind": "comment_translation"}
idx, cb, ca = ctx_for(KEY, "adv", tl["sentence_en"])
tl["context_before"], tl["context_after"], tl["sentence_found_in_article"] = cb or "", ca or "", idx is not None
items.append(tl)

for n, it in enumerate(items):
    it["id"] = "JAQ-%s-%03d" % (it["tier"], n)
os.makedirs(OUT, exist_ok=True)
json.dump(items, open(os.path.join(OUT, "items.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
arts = {}
for k, v in ARTICLES.items():
    arts[k] = {lv: " ".join(v[lv]) for lv in ("std", "adv") if lv in v}
    arts[k]["family"] = v["family"]
json.dump(arts, open(os.path.join(OUT, "articles.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
c = collections.Counter((i["tier"], i["split"]) for i in items)
fam = collections.Counter((i["tier"], i["family"], i["level"]) for i in items)
summ = {"total": len(items), "by_tier_split": {"%s|%s" % k: v for k, v in sorted(c.items())},
        "by_tier_family_level": {"%s|%s|%s" % k: v for k, v in sorted(fam.items())}, "missing_extra": miss,
        "sentence_not_found": [i["id"] for i in items if not i["sentence_found_in_article"]]}
json.dump(summ, open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(summ, ensure_ascii=False, indent=1))


# ---- 検査バッチ(view A/B)。同じ表現が1つのバッチに2回入らないようにする(T3と置換元の正常訳、equivalent widthの2版)。
# view A = T3以外の全項目(正常の採点はAのみ)。view B = T3(+equivalent widthの2版目)+置換元ではない正常項目(filler: 自然な混在にするため入れる。Bでの採点対象外)。
batches = collections.OrderedDict()
by_group = collections.defaultdict(list)
for it in items:
    by_group[(it["split"], it["article_key"], it["level"])].append(it)
for (sp, ak, lv), L in by_group.items():
    a_ids, b_scored, b_fill = [], [], []
    seen_expr = set()
    t3_expr = {i["expression"] for i in L if i["tier"] == "T3"}
    for i in L:
        if i["tier"] == "T3":
            b_scored.append(i["id"]); continue
        if i["tier"] == "T1" and i["expression"] in seen_expr:   # 同じ表現の2版目はBへ
            b_scored.append(i["id"]); continue
        a_ids.append(i["id"]); seen_expr.add(i["expression"])
        if i["expression"] not in t3_expr and i["tier"] == "T2":
            b_fill.append(i["id"])
    base = "%s|%s|%s" % (sp, ak, lv)
    if a_ids:
        batches[base + "|A"] = {"split": sp, "article_key": ak, "level": lv, "view": "A", "item_ids": a_ids, "scored_ids": a_ids}
    if b_scored:
        batches[base + "|B"] = {"split": sp, "article_key": ak, "level": lv, "view": "B", "item_ids": b_scored + b_fill, "scored_ids": b_scored}
json.dump(batches, open(os.path.join(OUT, "batches.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
nb = collections.Counter((b["split"], b["view"]) for b in batches.values())
print("batches:", dict(nb), "total", len(batches))
assert all(len({items_by_id["expression"] for items_by_id in [x for x in items if x["id"] in b["item_ids"]]}) == len(b["item_ids"]) for b in batches.values()), "expression重複"
