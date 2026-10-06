# -*- coding: utf-8 -*-
# TRIAL-04 L2(P4_paraphrase) 内容ラベル(Sonnet仮ラベル=人手確認前)。出力: eval/t04l2_labels.json。凡例はt04_labels.pyと同じ。
import json
from pathlib import Path

P = "P4_paraphrase"
L = {}
old = json.loads(Path(__file__).with_name("t04_labels.json").read_text(encoding="utf-8"))
for k, v in old.items():  # 既存notes禁止文の内容ラベル(副指標用。パターン非依存)は再利用
    if k.endswith("/existing"):
        L[k] = v


def add(slug, fid, match, typ, why, fab=False, vague=False):
    L["%s/%s/%s" % (P, slug, fid)] = {"match": match, "type": typ, "fab": fab, "vague": vague, "why": why}


# ---- 対象 ----
add("meta", "MUSE-HC-012", "P", "-", "当面提供されない状態は示すが、否定軸は『完全廃止ではない』(時期軸)。機能の復活・再提供の否定が無い")
add("meta", "MUSE-HC-014", "N", "-", "条件付き公開↔無条件公開の段階。既知誤読(改善の対象)とは別")
add("hormuz", "HF-007", "Y", "-", "方針を投稿で示した段階・実施未完了。途中経過と最終状態の取り違えを禁じる")
add("sewer", "F-011", "Y", "-", "方針案への意見募集段階。決定ではない(既存notesと同趣旨=重複)")
add("ai_control", "EVID-004", "Y", "-", "促されれば落とせた/促されず自発的ではない(既存notesと同趣旨=重複)")
add("ai_control", "EVID-006", "Y", "-", "架空シナリオ。実在の技術者への脅迫ではない(既存notesと同趣旨=重複)")
# ---- 対象外(core) ----
add("hormuz", "HF-001", "-", "V", "再確認(維持すべき)↔免除の実施。決定の段階反転")
add("hormuz", "HF-002", "-", "V", "投稿で求めた段階↔徴収済み")
add("hormuz", "HF-004", "-", "H", "試算↔確定額。情報の確からしさ(対象外の型)")
add("space_weapons", "F-014", "-", "V", "打上げ計画発表↔配備済み")
add("sewer", "F-008", "-", "D", "残存↔すべて無くなった。主題結論を変えるほどではなく不自然寄り")
add("sewer", "F-013", "-", "V", "縮小計画の策定↔実際に縮小")
add("ai_control", "EVID-001", "-", "V", "管理評価↔実際の仕事での完遂")
add("ai_control", "EVID-002", "-", "V", "模擬↔実在企業への攻撃")
add("ai_control", "EVID-005", "-", "D", "『報告されなかった』↔『漏えいさせた』。報告有無の違い寄りで変質止まり")
add("ai_control", "EVID-007", "-", "V", "評価構成↔商用環境")
add("ai_control", "EVID-008", "-", "V", "脱出を試みなかった↔自ら脱出した")
add("ai_control", "EVID-009", "-", "V", "模擬認識↔現実の攻撃意図")
add("ai_control", "EVID-010", "-", "V", "内部評価中↔実運用環境")
add("ai_control", "EVID-011", "-", "V", "開始時の接続有無")
add("ai_control", "CONTROL-002", "-", "V", "将来の枠組み↔現行システムが三要素を満たした")
# ---- holdout ----
add("A02", "POL-01", "-", "V", "計画↔施行済み(holdout対象)")
add("A02", "PILOT-01", "-", "D", "全309世帯↔夜間curfew群だけ。主題への影響小")
add("A02", "PILOT-02", "-", "V", "希望に基づく配分↔無作為割付")
add("A02", "PILOT-03", "-", "X", "Rが不自然(night-curfew群が309世帯になった)")
add("A02", "PILOT-05", "-", "H", "介入対象範囲の違いだけ(範囲限定)")
for fid, t, w in [("F001", "D", "編集傾向↔販売実績(同型の繰り返し)"), ("F002", "D", "編集記事↔消費者行動"), ("F003", "D", "編集↔消費者市場"), ("F004", "D", "編集↔消費者行動"),
                  ("F005", "D", "編集↔消費者行動"), ("F006", "D", "編集↔消費者普及"), ("F007", "D", "編集の説明↔消費者の選択"), ("F008", "D", "設計説明↔消費者の実使用"),
                  ("F009", "H", "『完全に消えたのではない』は主題外・不自然"), ("F010", "D", "見解の紹介↔実使用"), ("F015", "V", "検索数↔購入(確認済み購入でない)"),
                  ("F016", "D", "有名人着用↔一般普及"), ("F017", "D", "有名人着用↔一般普及")]:
    add("small_bag", fid, "-", t, w)
add("A01", "F008", "-", "V", "クロスの主体の取り違え")
L["%s/gate" % P] = {"label": "軸ずれ", "why": "'ロールバックした'=当面提供されない状態は示すが、機能そのものの復活・再提供の否定が無く、否定軸は『完全廃止ではない』(時期軸)。誤禁止表現(復元ではない型)は無い"}
Path(__file__).with_name("t04l2_labels.json").write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
