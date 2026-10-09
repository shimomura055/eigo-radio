# -*- coding: utf-8 -*-
"""HUMAN_CHECK_E2E_01.md を生成する(API呼出なし、runs配下は読み取りのみ)。
本文は runs/<theme>/<arm>/ の成果物をそのまま埋め込む(手編集なし)。質問文はこのscriptに書いてある。"""
import json
import os
import random
import re

BASE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(os.path.dirname(BASE), "runs")


def rd(*p):
    with open(os.path.join(RUNS, *p), encoding="utf-8") as f:
        return f.read().rstrip()


def ledger_entries(theme, ids):
    t = rd(theme, "shared", "ledger.txt")
    parts = re.split(r"\n\s*\n", t)
    d = {}
    for p in parts:
        m = re.match(r"\[[A-Z]+\] ([\w-]+):", p)
        if m:
            d[m.group(1)] = p
    return "\n\n".join(d[i] for i in ids)


def block(title, text):
    return f"#### {title}\n\n```text\n{text}\n```\n"


def main():
    L = []
    A = L.append
    A("""# HUMAN_CHECK_E2E_01 v2: ユーザー人間確認パック(FACTLOCK-ASTRA-E2E-TRIAL-01、委任_15で作成・委任_16でv2、2026-10-09)

位置づけ: Trial/DEV(Production変更なし、VALIDATED/APPROVED_FOR_PRODUCTION未宣言)。**ラベルはSonnetの暫定推測で、本パックの目的はその境界例をあなたが確定すること。**
腕名は開示している。旧腕=Luna Writer(Production相当経路)、新腕=Fact Lock+gpt-6-astra(R0→Astra R1→R2)。両腕とも**同じ台帳・同じB3(新腕は注記版)**から作った本文である。R1は載せない。
**v2の変更点(委任_16)**: 事実確認3記事(2〜5節)はそのまま。**6節に『面白さ』の比較(pairwise)3対を追加**。6節だけは腕名・順序を伏せ(A/B表記)、対応表は `eval/_private/PAIRWISE_MAP_01.json` に置いた(回答前に開かない)。
本文は成果物のまま(手直しなし)。STOP記事の『採用されなかった本文』は、そのrunでは出荷されなかった本文である(別枠で、判定線には入らない)。

## 0. 回答の仕方(三択)
各質問に **重大 / 軽微 / 問題なし** のどれか1語で答えてください(迷う場合は『判断不能』も可)。基準は次の通り(`docs/pm/open233_materiality_criteria_2026-10-03.md`の要約)。
- **重大**: 台帳と食い違う事実の断定で、読者が事実関係を重く取り違えるもの(数量・主体・否定の反転など)。
- **軽微**: 核心は保たれるが、範囲・確からしさ・主体の拡張や一般化、言い回しの精度低下があるもの。**因果の付与(台帳に無い原因・目的の追加)は事前登録上、軽微に分類済み**(あなたの2026-10-08注記で『潜在的リスク』)。
- **問題なし**: 台帳に整合、または修辞・導入のhookで新しい事実を足していないもの。
回答が重大になった場合、その文が最終本文に残っていた腕は『出荷本文の重大見逃し』になり、事前登録2-1の要確認フラグ・総合判定に影響します(EVAL_E2E_01.md 3-3節)。

## 1. 推奨3記事と理由(Fable提示の候補を採用し、理由を付与)
| 候補 | 推奨理由 | 評価への影響 |
|---|---|---|
| **byd_recall** | 新腕のJA最終本文にだけ『見出し・冒頭が無留保で現象を描写』の境界(w2が人間確認候補とした唯一の出荷本文の境界)があり、旧腕には同種が無い。**あなたの回答が重大なら、新腕の要確認フラグ(事前登録2-1)が立つ唯一の候補**。新腕EN Standard STOPの起点も同記事のJA文(目的表現)。 | 2-1 要確認フラグ、軽微JA列 |
| **openai_copyright** | 新腕はB1回復(Trial 3回目)後にEN Adv STOP。STOP根拠は『見出し一般化』で軽微判定。さらに回復前の本文に『主体の取り違え』の字面(重大寄りの境界)がある。旧腕には同型の主体曖昧(出荷前に再生成で消えた)。STOP妥当性の判断に直結。 | EN STOP率、B1の純効果 |
| **central_bank_mortgage** | 新腕はR0(JA段)でSTOP。STOP根拠3件がすべて『軽微/重大の境界』。ここが重大なら『妥当なSTOP』、軽微なら『過剰ブロック』となり、人手介入必要率の読みが変わる。旧腕は同じ台帳で完走・指摘0。注記(30年固定=周辺扱い)の副作用の疑いもある。 | 人手介入必要率の解釈、B3注記の副作用 |
""")
    A("""**workerの推奨(参考)**: w1(meta/hormuz/space_weapons)=space_weapons(不在・秘匿の断定と単複差が基準解釈に依存)/meta旧のrejected本文1件。w2(small_bag/byd/central)=byd_recall(新旧)、central_bank_mortgage新(R0 STOPの境界2件)、small_bag旧(軽微3件の残存とSTOP)。w3(openai/semiconductor/streaming)=openai新Adv(CMI主体と見出し)、semiconductor新Adv(B3 qualifier文)、streaming旧Std(Rewrite後本文)。
Fable候補との一致: byd_recall(w2)、central_bank_mortgage(w2)、openai_copyright(w3)は一致。w1のspace_weaponsは**共通の基準質問**として5節に1問だけ載せた。残り6テーマ(meta・hormuz・space_weapons・small_bag・semiconductor・streaming)の本文は `runs/USER_PACK_E2E_01.md`(JA)、`runs/USER_PACK_E2E_EN_01.md`(EN)を参照。
""")

    # ---------------- byd_recall
    A("\n---\n\n## 2. byd_recall(BYDブレーキペダル部品リコール)\n")
    A("台帳(関連項目のみ。全文は `runs/byd_recall/shared/ledger.txt`):\n\n```text\n" +
      ledger_entries("byd_recall", ["BYD-RECALL-05", "BYD-RECALL-06", "BYD-RECALL-07", "BYD-RECALL-11"]) + "\n```\n")
    A(block("旧腕 JA最終(Luna。案B[JA再確認]で再生成した後の本文。EN StandardでSTOP、Advancedは出荷)", rd("byd_recall", "old", "ja_writer", "revision2.md")))
    A(block("新腕 JA最終(Astra R2)", rd("byd_recall", "new", "ja_writer", "revision2.md")))
    A("""**質問(byd_recall)**

| # | 腕 | 該当文 | 台帳 | 何が境界か | 回答(重大/軽微/問題なし) |
|---|---|---|---|---|---|
| B-1 | 新 | 見出し『踏んでないのに「ブレーキ中！」、車の赤ランプ、まさかの“ひとり実況”』と冒頭の会話(『ブレーキ、踏んでます！』『いや、踏んでませんけど？』『赤いランプが全力アピール』) | BYD-RECALL-07(極端な場合に限位垫が脱落したとき、ペダルを踏んでいなくても制動灯が点灯し続ける**可能性**) | 本文の中段では『極端な場合…おそれがある』と留保しているが、見出し・冒頭は無留保で現象が起きているように描いている。w2は軽微(境界)、人間確認候補。 | |
| B-2 | 新 | 『つまり、足はブレーキを踏んでいないのに、ランプだけが「踏んでます！」と実況を続けてしまう状態。』 | BYD-RECALL-07 | 『おそれ』が取れ、常にそうなる状態のように読めるか。 | |
| B-3 | 新 | 『BYDは認定販売店を通じ、対象の部品を改善後のものへ無料で交換します。…いわば車の“ひとり実況”を止め、操作と合図の食い違いを防ぐための対策です。』 | BYD-RECALL-11(無料交換のみ。交換の目的・効果の記載なし) | 交換の目的・効果の追加(因果の付与=事前登録上は軽微)。**この文が新腕EN Standard STOPの起点**(ENで『will stop/prevent』と効果の断定に強まった)。 | |
| B-4 | 新 | 『現場と広報の連絡が取れていません。運転手としては「その発表、私を通してもらえますか」と言いたくなるところです。』 | なし(修辞) | ペダルとランプの食い違いを組織内の連絡不全にたとえた比喩。事実の断定に読めるか(Checkerはこの文のEN訳をBLOCKING、人間側ラベルは偽陽性としてRewrite不要)。 | |
| B-5 | 旧 | 『極端な場合にはパッドが外れ、ペダルを踏んでいないのにブレーキランプがつき続けることがあります。』 | BYD-RECALL-07 | 『可能性』が『ことがあります』に強まったか(w2低確信)。 | |
| B-6 | 旧 | 『道路上の「送信ミス」を防ぐための部品交換。』 | BYD-RECALL-11 | 交換の目的・効果の追加(因果の付与)。旧腕EN StandardはこのJA由来でSTOP。 | |
""")

    # ---------------- openai
    A("\n---\n\n## 3. openai_copyright(USA TODAY傘下の法人 対 OpenAI 著作権訴訟)\n")
    A("台帳(関連項目のみ。全文は `runs/openai_copyright/shared/ledger.txt`):\n\n```text\n" +
      ledger_entries("openai_copyright", ["F4", "F6"]) + "\n```\n")
    A(block("旧腕 JA最終(Luna。案B[JA再確認]を1回経て完走、EN Adv/Std出荷)", rd("openai_copyright", "old", "ja_writer", "revision2.md")))
    A(block("新腕 JA最終(Astra R2、B1回復後。記事としてはEN Adv STOPのため未出荷)", rd("openai_copyright", "new", "ja_writer", "revision2.md")))
    A(block("(参考)新腕 B1前のJA R2(採用されなかった本文。B1の起点となった)", rd("openai_copyright", "new", "ja_writer_prev_b1", "revision2.md")))
    A("""**質問(openai_copyright)**

| # | 腕 | 該当文 | 台帳 | 何が境界か | 回答(重大/軽微/問題なし) |
|---|---|---|---|---|---|
| O-1 | 新(最終JA) | 見出し『2億5,000万ドル超、そのうえ「モデル破棄」も。AI訴訟は財布だけでは終わらない』 | F6(本件訴状の請求) | 『AI訴訟』が本件でなくAI訴訟全般に読めるか(本文は『OpenAIを提訴』『今回のAI訴訟』と特定)。**この見出しがEN Adv STOPの根拠**(B1が1記事1回のため回復せず)。w3は軽微。 | |
| O-2 | 新(B1前、採用されず) | 『さらに、モデルの出力が記事を複製したり、組み直したりしたほか、著作権管理情報も取り除いたとしています。』 | F4(原告は、**OpenAI**が著作権管理情報を除去したと主張) | 文法上、除去の主体が『モデルの出力』に見える(主体の取り違えの字面。重大の定義(2)に当たりうる)。w3は軽微(境界)。**B1の発火理由**。 | |
| O-3 | 旧(最終JA) | 『さらに、モデルの出力で記事を複製したり、内容を組み直したりし、著作権管理情報も取り除いたと訴えている。』 | F4 | O-2と同型の主語の省略があるが、直前の文で主体がOpenAIと明示されている。同じ基準で見たときの判断をそろえるための対照。 | |
""")

    # ---------------- central
    A("\n---\n\n## 4. central_bank_mortgage(FOMC利上げと住宅ローン金利)\n")
    A("台帳(関連項目のみ。全文は `runs/central_bank_mortgage/shared/ledger.txt`):\n\n```text\n" +
      ledger_entries("central_bank_mortgage", ["F002", "F006", "F007"]) + "\n```\n")
    A(block("旧腕 JA最終(Luna。完走、FC指摘0、EN Adv/Std出荷)", rd("central_bank_mortgage", "old", "ja_writer", "revision2.md")))
    rej = json.loads(rd("central_bank_mortgage", "new", "new_writer", "r0_stop.json"))["rejected_text"]
    A(block("新腕 JA段R0(**採用されなかった本文**: must-fix後のattempt2。R0段でSTOP、Astra R1/R2には進まず。【事N】はR0の事実タグで、通常は後段で除去される)", rej))
    A("""**質問(central_bank_mortgage)**。新腕のR0 attempt1の文は本文が保存されておらず、FCの指摘引用のみで再現している。

| # | 腕 | 該当文 | 台帳 | 何が境界か | 回答(重大/軽微/問題なし) |
|---|---|---|---|---|---|
| C-1 | 新(attempt1、FC引用) | 『APが示した固定型の住宅ローン金利の全米平均は、5.98％から7.40％へ上昇しました。』 | F007(**30年固定**の全米平均。15年固定は6.73%[F006]) | 『30年固定』が『固定型』全般に広がり、15年固定を含む平均に読めうる。数値自体は正しい。w2は軽微(境界)。**STOPの第1要因**(初回FC MAJOR)。 | |
| C-2 | 新(attempt2、上の本文) | 『APが比較した長期固定ローンの全米平均金利は、5.98％から7.40％へ上昇しました。』 | F007 | 『30年固定』が『長期固定ローン』になった。C-1より絞れているが15年固定を含みうる。FCは前回指摘の未解消と判定。 | |
| C-3 | 新(attempt2、上の本文) | 『政策金利の目標を0.25ポイント引き上げ、3.75％から4.00％にしました。』 | F002(目標**レンジ**を0.25pt引き上げ、新レンジ3.75～4.00%) | 『レンジ』が落ち、単一の目標が3.75→4.00%に動いたように読めうる。引き上げ幅0.25ptと新水準は台帳どおり。w2は軽微(境界)。**STOPの確定要因**(再生成で新たにMAJOR)。初回attempt1は『目標レンジ』と書いて合格していた。 | |
| C-4 | 旧(最終JA、対照) | 『三十年固定型の全米平均金利は、2月下旬の5.98％から、10月8日には7.40％へ上昇しました。』と『政策金利を0.25ポイント引き上げ、3.75％から4.00％の範囲にしました。』 | F007・F002 | 旧腕は『三十年固定型』『範囲』と明記して指摘0。C-1〜C-3の判断をそろえるための対照(回答は『問題なし』想定だが、確認してください)。 | |
""")

    # ---------------- optional space_weapons
    A("\n---\n\n## 5. 共通の基準質問(space_weapons、任意・1問)\n")
    A(f"""台帳 F-001: 『…米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。』 notes_for_writer: 『米国が軌道上兵器の配備を公式に認めた』までは使用可能。**具体的なシステム名・攻撃能力・標的は推測で補わない**。(台帳は『非公開』『伏せられている』とは書いていない。)

本件の最大の『重大寄りの境界』は、**台帳が「補わない」と指示しただけの事柄を、本文が「示されていない/伏せられている/秘密」と断定している**ことです。両腕の出荷本文に同型があり、基準(6)を字義通りに当てると重大になりうるため、worker(w1)は『軽微』としつつ確信度0.5で保留しました。

| # | 腕 | 該当文 | 回答(重大/軽微/問題なし) |
|---|---|---|---|
| S-1 | 新(JA最終) | 見出し『宇宙兵器、必殺技は秘密。でも「住所」は公開された』/『性能表は伏せたまま』/『具体的なシステム名も攻撃能力も示されていない』(ENの『remain secret』『have not been given』等4箇所に伝播) | |
| S-2 | 旧(JA最終) | 『ただし、装置の名前も、具体的な攻撃能力も明らかにされていません。』(ENの『have not been made public』に伝播) | |

S-1とS-2を**同じ判断**にするかどうかが論点です(両腕とも出荷本文に残っているので、重大とすると両腕に等しく入り、新旧の差には効きませんが、『出荷本文の重大見逃し0』という前提が崩れます)。
""")
    # ---------------- pairwise(面白さ)
    PAIRS = [
        ("space_weapons", "宇宙兵器(米国の軌道上兵器配備の公式認定)"),
        ("streaming_price", "動画配信の値上げ"),
        ("small_bag", "ミニバッグのトレンド"),
    ]
    rng = random.Random(20261009)
    pmap = {}
    A("\n---\n\n## 6. 面白さの比較(pairwise、腕名を伏せたA/B。3対、約10分)\n")
    A("""**目的**: 事実の安全とは別に、**どちらの記事のほうが聞いて/読んで面白いか**を判断してください(音声ラジオ用の台本としての面白さ)。観点は『冒頭で引き込まれるか』『例え・言い回しが効いているか』『最後まで読ませるか』『分かりやすさ』。長さや文体の違いも含めた**総合の印象**で選んで構いません。
各対の本文は同じテーマ・同じ台帳(事実)から作られています。A/Bの順序は対ごとにランダムで、**どちらが新腕か旧腕かは伏せています**(対応表は `eval/_private/PAIRWISE_MAP_01.json`。回答後に照合)。(P-1は5節で見た文面から腕を推測できる可能性があります。推測は気にせず印象で選んでください。文体・長さの違いで腕が推測できる点は既知の盲検の限界です。)
回答は各対で ①面白さ(A / B / 差なし)、②事実の不安(『なし』、または不安な文を引用)、③一言理由(任意)。台帳は各テーマの `runs/<theme>/shared/ledger.txt` を参照できます。
""")
    for i, (theme, label) in enumerate(PAIRS, 1):
        arms = ["new", "old"]
        rng.shuffle(arms)
        a_arm, b_arm = arms
        pmap[f"P-{i}"] = {"theme": theme, "A": a_arm, "B": b_arm, "source": f"runs/{theme}/<arm>/ja_writer/revision2.md"}
        A(f"### P-{i}. {theme}({label})\n\n台帳: `runs/{theme}/shared/ledger.txt`\n")
        A(block(f"P-{i} 記事A", rd(theme, a_arm, "ja_writer", "revision2.md")))
        A(block(f"P-{i} 記事B", rd(theme, b_arm, "ja_writer", "revision2.md")))
        A(f"""| 対 | ①面白さ(A / B / 差なし) | ②事実の不安(なし/該当文の引用) | ③一言理由(任意) |
|---|---|---|---|
| P-{i} | | | |
""")
    os.makedirs(os.path.join(BASE, "_private"), exist_ok=True)
    with open(os.path.join(BASE, "_private", "PAIRWISE_MAP_01.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"seed": 20261009, "note": "A/B順序のランダム化の対応表。回答前に開かない。本文は成果物のまま(手直しなし)", "pairs": pmap}, f, ensure_ascii=False, indent=2)
    A("""
**面白さの総括(任意)**: 3対を通して新旧のどちらが好みか、気づいた違い(長さ、例え、テンポ)があれば自由記述: ________
""")
    A("""
## 7. 回答後にFableが行うこと(あなたの作業ではない)
- 回答は `confirmed_by=user_<日付>` で `eval/labels_merged.jsonl` の該当行に**追記**する(元ラベルは保存)。
- 6節(面白さ)の回答は MAP と照合して新旧に戻し、EVALの『面白さ』欄に記録する(人間1名の暫定pairwise)。事実の不安の引用は境界例として別途ラベル追記する。
- 事前登録2-1の要確認フラグ(B-1)、STOP妥当性(O-1・C-1〜C-3)、基準解釈(S-1・S-2)をEVAL_E2E_01.md 2節・3節の機械判定に反映するかをFableが判断する。
- 判定線の最終判定・VALIDATED・APPROVED_FOR_PRODUCTION は、本パックの回答だけでは宣言しない。
""")
    out = os.path.join(BASE, "HUMAN_CHECK_E2E_01.md")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print("wrote", out, os.path.getsize(out))


if __name__ == "__main__":
    main()
