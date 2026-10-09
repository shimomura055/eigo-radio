# -*- coding: utf-8 -*-
"""D0 決定論・方向語/不在断定cue/数量の検出器(API不要・費用0円)。DEV専用Risk Flagger。
Flagを立てるだけ。合否判定しない・Rewriteしない・自動修正しない。
入力unit: dict(unit_id, facts=[{fact_id,text}], sentences=[{sid,text,before,after}])
出力: Flag(dict)のlist。
"""
import re

# 方向語グループ。side "W"=撤回・停止・巻き戻し側 / "R"=復元・再開・元に戻す側。
# 台帳Factの側と記事文の側が対立(Fact=Wのみ・文=Rのみ、またはその逆)したらFlag。
# 語彙は directional_misread_trial_01/population_01.md の語彙を拡張(撤回/ロールバック/停止/復元/再開 ...)。
GROUPS = {
    "rollback反転": {
        "W": ["ロールバック", "撤回", "停止", "中止", "取り下げ", "取りやめ", "取り止め", "見送り", "無効化", "凍結",
              "廃止", "撤廃", "差し戻し", "巻き戻", "棚上げ", "一時停止", "打ち切り",
              "roll back", "rolled back", "rollback", "rolling back", "withdraw", "withdrew", "withdrawn", "suspend",
              "halt", "pause", "cancel", "revoke", "scrap", "put on hold", "on hold", "shelve", "discontinue",
              "disable", "deactivate", "pull the plug", "walked back", "walk back", "called off", "backed out"],
        "R": ["復元", "復活", "再導入", "再開", "元に戻", "以前の状態", "もとに戻", "復旧", "再有効", "再び有効",
              "再稼働", "戻しました", "戻した", "戻す", "再掲", "再投入",
              "restore", "restored", "restoring", "put back", "putting back", "reinstate", "reinstated",
              "bring back", "brought back", "resume", "resumed", "reintroduce", "re-introduce", "re-enable",
              "reenable", "reactivate", "relaunch", "reopen", "the way it had been", "back to normal",
              "went back to", "returned to", "revert"],
    },
    "増減反転": {
        "W": ["減少", "低下", "下落", "縮小", "引き下げ", "値下げ", "削減", "急落", "減った", "下がった",
              "decrease", "decline", "fell", "drop", "reduce", "lower", "shrink", "shrank"],
        "R": ["増加", "上昇", "拡大", "引き上げ", "値上げ", "増額", "急騰", "増えた", "上がった",
              "increase", "rise", "rose", "grew", "grow", "raise", "higher", "expand", "surge"],
    },
    "許可禁止反転": {
        "W": ["禁止", "却下", "否決", "拒否", "不許可", "認めない", "ban", "prohibit", "reject",
              "deny", "denied", "forbid", "block", "refuse"],
        "R": ["許可", "承認", "可決", "認める", "認めた", "解禁", "解除", "allow", "permit", "approve",
              "authorize", "lift", "legalize"],
    },
}
# 日本語は部分一致、英語は語頭一致(語境界の前側のみ。活用語尾を許容)

ABSENCE_CUES = [
    "公表されていない", "明らかにされていない", "確認されていない", "報告されていない", "存在しない", "起きていない",
    "なかった", "一度もない", "まだない", "示されていない", "分かっていない", "わかっていない", "判明していない",
    "not been made public", "has not been", "have not been", "has not reported", "have not reported",
    "no one has", "nobody has", "no evidence", "never ", "has not ", "have not ", "did not", "not yet",
    "nor has", "nor have", "not reported", "undisclosed", "not disclosed", "not been disclosed",
]

_STOP_EN = set("the a an of to in on at for and or but is are was were be been it its this that these those with as by from "
               "their his her they he she we you i not no has have had will would can could may might also than then "
               "there about into over after before during under which who whom what when where why how more most".split())
_num_re = re.compile(r"\d[\d,]*\.?\d*")
_cap_re = re.compile(r"\b[A-Z][A-Za-z0-9\-]{2,}\b")
_ja_tok_re = re.compile(r"[ァ-ヴー]{2,}|[一-龥]{2,}|[A-Za-z][A-Za-z0-9\-]{2,}")


def _norm(s):
    return (s or "").replace("　", " ").lower()


def side_hits(text, group):
    """textに含まれるW/R側の語。戻り値 dict(W=[...], R=[...])。"""
    t = _norm(text)
    out = {"W": [], "R": []}
    for side in ("W", "R"):
        for w in GROUPS[group][side]:
            wl = w.lower()
            if re.search(r"[a-z]", wl):
                if re.search(r"(?<![a-z])" + re.escape(wl), t):
                    out[side].append(w)
            elif wl in t:
                out[side].append(w)
    return out


def numbers(text):
    res = set()
    for m in _num_re.findall(text or ""):
        m = m.replace(",", "").rstrip(".")
        if m:
            res.add(m)
    return res


def content_tokens(text):
    """固有名詞・数値・カタカナ/漢字語・英単語(非ストップ)の集合。文とFactの対応付けの近似用。"""
    toks = set()
    for m in _cap_re.findall(text or ""):
        toks.add(m.lower())
    for m in _ja_tok_re.findall(text or ""):
        m = m.lower()
        if m not in _STOP_EN:
            toks.add(m)
    toks |= {"#" + n for n in numbers(text)}
    return toks


def overlap_score(sentence, fact):
    a, b = content_tokens(sentence), content_tokens(fact)
    if not a or not b:
        return 0.0
    return len(a & b) / float(min(len(a), len(b)))


def map_facts(sentence, facts, top_k=3, min_score=0.0):
    """文に最も近いFactを top_k 件返す: [(score, fact)]。固有名詞・数値の重なりで近似(0円)。"""
    scored = sorted(((overlap_score(sentence, f["text"]), f) for f in facts), key=lambda x: -x[0])
    return [(s, f) for s, f in scored[:top_k] if s >= min_score]


def _mk(unit, sent, typ, fact_ids, conf, severity, question, basis, detector="d0"):
    return dict(unit_id=unit["unit_id"], sentence_id=sent["sid"], sentence=sent["text"], type=typ,
                fact_ids=list(fact_ids), confidence=round(conf, 2), severity=severity, question=question,
                basis=basis, detector=detector)


def detect(unit, top_k=3, align_min=0.15):
    """unit内の全文を走査してFlagを返す。"""
    flags = []
    facts = unit["facts"]
    for sent in unit["sentences"]:
        text = sent["text"]
        mapped = map_facts(text, facts, top_k=top_k)
        # 台帳が1件のみ(casebank)の場合は対応付けを強制採用。複数の場合は重なり>=align_minのみ。
        cand = [(s, f) for s, f in mapped if (len(facts) == 1 or s >= align_min)]
        for group in GROUPS:
            sh = side_hits(text, group)
            typ = "rollback反転" if group == "rollback反転" else "その他"
            for s, f in cand:
                fh = side_hits(f["text"], group)
                conf = 0.7 if (s >= 0.3 or len(facts) == 1) else 0.5
                if fh["W"] and not fh["R"] and sh["R"] and not sh["W"]:
                    flags.append(_mk(
                        unit, sent, typ, [f["fact_id"]], conf, "重大",
                        "台帳は『%s』(停止・撤回・巻き戻し側)なのに、この文は『%s』(復元・再開側)と読めます。向きは台帳どおりですか。"
                        % (",".join(fh["W"][:2]), ",".join(sh["R"][:2])),
                        "dir:%s W(fact)=%s R(sent)=%s align=%.2f" % (group, fh["W"][:3], sh["R"][:3], s)))
                elif fh["R"] and not fh["W"] and sh["W"] and not sh["R"]:
                    flags.append(_mk(
                        unit, sent, typ, [f["fact_id"]], conf, "重大",
                        "台帳は『%s』(復元・再開側)なのに、この文は『%s』(停止・撤回側)と読めます。向きは台帳どおりですか。"
                        % (",".join(fh["R"][:2]), ",".join(sh["W"][:2])),
                        "dir:%s R(fact)=%s W(sent)=%s align=%.2f" % (group, fh["R"][:3], sh["W"][:3], s)))
        # 不在断定cue(台帳に不在と書かれていない不在断定の疑い)
        tl = " " + _norm(text) + " "
        hits = [c for c in ABSENCE_CUES if c.lower() in tl]
        if hits:
            fid = [f["fact_id"] for s, f in cand[:1]]
            flags.append(_mk(unit, sent, "不在断定", fid, 0.35, "重大",
                             "この文は『ない・未公表』と断定しています。台帳にその不在を支える記述はありますか(台帳の記述と食い違っていませんか)。",
                             "absence_cue=%s" % hits[:3]))
        # 数量: 文中の数値が対応Factの数値集合にない
        sn = numbers(text)
        if sn and cand:
            fnums = set()
            for s, f in cand:
                fnums |= numbers(f["text"])
            extra = sorted(n for n in sn if n not in fnums and len(n) >= 2)
            if extra and fnums:
                flags.append(_mk(unit, sent, "数量時系列", [f["fact_id"] for s, f in cand[:1]], 0.3, "重大",
                                 "文中の数値(%s)が台帳の対応Factにありません。数量・日付は台帳どおりですか。" % ",".join(extra[:3]),
                                 "numbers_not_in_fact=%s" % extra[:3]))
    return flags
