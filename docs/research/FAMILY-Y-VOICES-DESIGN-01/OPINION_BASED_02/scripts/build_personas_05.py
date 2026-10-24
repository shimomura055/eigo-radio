# -*- coding: utf-8 -*-
"""PERSONAS_05.md を THEME_DATA_02.json と VOICES_02.json から生成する(API 0)。転記表は機械生成なので、Sheet・声一覧と食い違わない。"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
T = json.load(open(os.path.join(OUT, "THEME_DATA_02.json"), encoding="utf-8"))
VJ = json.load(open(os.path.join(OUT, "VOICES_02.json"), encoding="utf-8"))
V = {v["id"]: v for v in VJ["voices"]}
S = VJ["sources"]
NAME = {"voice_1": ("One Voice", "V1"), "voice_2": ("Another Voice", "V2"), "voice_3": ("A Third Voice", "V3")}


def dt(s):
    return s.split('〜')[0][:7] if s[:1].isdigit() else '日付未確認'


def table(slot):
    sh = T["sheets"][slot]
    rows = ["| 経験欄ID | 種別 | 内容(Sheetの文) | 根拠の声ID(立場・日付・権利区分) | 集約関係 |", "|---|---|---|---|---|"]
    for x in sh["experiences"]:
        src = "; ".join(f"{i}({V[i]['stance']}・{dt(S[V[i]['src']]['date'])}・{S[V[i]['src']]['rights']})" for i in x["source_ids"])
        rel = "単独" if len(x["source_ids"]) == 1 else "集約(複数の別人の声。どの声のどの要素かは下の対応で追える)"
        rows.append(f"| {x['id']} | {'出来事' if x['kind'] == 'E' else '意見'} | {x['text_ja']} | {src} | {rel} |")
    return "\n".join(rows)


def main():
    L = []
    L.append("# PERSONAS_05 (委任_24: 実在の声から選んだ3 Persona。THEME_DATA_02.jsonの人間可読版)\n")
    L.append("作成: 2026-10-24。API 0。選定の材料は`AXIS_ANALYSIS_03.md` §3の評価表、根拠の声は`SOURCE_LOG_02.md`/`VOICES_02.json`。**3 Personaはすべて集約Persona(実在の特定個人ではない)**。実在の声の属性は変えず、補った表現は口調・一人称・性別ラベル(声の聞き分け用)だけで、欄に『補った』『推定』と明記している。機械可読版=`THEME_DATA_02.json`(`scripts/build_theme_data_02.py`で生成)、テスト=`er110_family_y_opinion_based_03_test_01.py`(23件PASS)。\n")
    L.append("## 1. 選定した3 Personaと『この人物だから、この意見になる』\n")
    L.append("| | V1 現役の宅配ドライバー | V2 共働きで家を空ける時間が長い受取人 | V3 受け取り方を自分で整えている受取人 |\n|---|---|---|---|")
    L.append("| 立場 | 再配達の料金を受取人から取る形には**反対**(配送料の全体・夜の配達の見直しが筋) | 有料化の前に**配達側の運用(時間指定の遵守・届く日時の事前通知)が先**=条件付き反対 | 有料化に**賛成**。ただし受け取りの環境を整えてから、くり返し不在の人から=条件付き賛成 |")
    L.append("| 感情の癖 | 淡々と事実を置く。悲しい・腹が立つ、と短く言ってすぐ仕事の話に戻る | 納得いかない気持ちを口にし、すぐ配達員の事情を足し、自分に問い返す | 公平かどうかにこだわり、すぐ『営業所が近い人の言い分かもしれない』と自分を相対化する |")
    L.append("| この人物だから | 不在のつらさを一番知る当人が、それでも客に請求する形に反対するのは、つらさの原因を『会社の仕組み・夜の配達』に見ているから(RV-55)。自分の仕事が理由に使われる側にいる | 夫婦とも仕事で日中不在がちなうえ、時間指定が守られず不在票が入った経験が重なると、自分が『不在にした側』にされることに引っかかる。配達員の大変さは分かるので葛藤が残る(RV-08・RV-07) | 再配達を出さないよう手間をかけているので、何度も頼む人と同じ料金は不公平と感じる(RV-11・RV-40〜42)。一方で、営業所/ロッカーが使いにくい経験(RV-26)から『整備が先』と言う。恵まれた側かもという引け目(RV-42)が自然に出る |")
    L.append("| 冒頭の型 | 自分の状況・立場の描写から | 感情・本音の吐露から | 出来事・場面の描写から |")
    L.append("| 結びの型 | やり方への具体的な注文(配送料の全体・夜の指定時間) | 自分に向けた問い返しで、決めきれない気持ちのまま終える | 自分の側の引け目を一言添えて終える |")
    L.append("| 根拠の声(立場/経験) | 立場: RV-55・RV-56 / 経験: RV-57・RV-58・RV-59 | 立場: RV-08・RV-63・RV-64 / 経験・気持ち: RV-07・RV-65・RV-24 | 立場: RV-11・RV-40・RV-41・RV-42 / 経験: RV-26・RV-34・RV-54・RV-66・RV-16・RV-09・RV-15・RV-19 |")
    L.append("| 一人称・性別(補った表現) | 私・男性(出典に性別なし。聞き分け用に補った) | わたし・女性(出典の『旦那』から推定) | 僕・男性(出典に性別なし。聞き分け用に補った) |")
    L.append("\n※ 3人の主張は部分的に重なる(『配達側・仕組みが先』はV1・V2・V3に共通)。ユーザー原文§4の『部分的な重なりは許容』に従い、重なりを消すために意見を歪めていない。TTS slotは、V1・V3が男性、V2が女性(音声段階では男性2人に別の声を割り当てる宿題。本Trialは文章のみ)。\n")
    for slot in ("voice_1", "voice_2", "voice_3"):
        sh = T["sheets"][slot]
        nm, v = NAME[slot]
        L.append(f"## 2-{v[1]}. {v} {T['who_ja'][slot]}({nm})の転記表\n")
        L.append(f"- 役割・属性: {sh['role_ja']}(`age_label`: {sh['age_label']})")
        L.append(f"- 人物像: {sh['persona_sketch_ja']}")
        L.append(f"- 切実なこと: {sh['stake_ja']} / 困りごと: {sh['troubles_ja']}")
        L.append(f"- 感情の癖: {sh['emotion_habit_ja']}")
        L.append(f"- 矛盾・弱さ(出典に根拠があるもののみ): {sh['contradiction_or_weakness_ja']}")
        L.append(f"- 許容される自己告白の範囲: 経験欄(E)の出来事を一つか二つだけ。欄にない出来事・会話・人物は足さない。『自分はこう考える』『こうなりそうで心配』は意見欄(O)の範囲で。`identity_cue`=『{sh['identity_cue_ja']}』")
        L.append(f"- `relevant_terms`(渡す用語定義): {', '.join(sh['relevant_terms'])}")
        L.append(f"- 話し方: 一人称『{sh['speech_style']['first_person']}』。{sh['speech_style']['sentence_length_pattern_ja']}。断言/留保: {sh['speech_style']['assertion_or_hedging_ja']}")
        L.append(f"- 芯(`claim_core_ja`): {sh['claim_core_ja']}\n")
        L.append(table(slot))
        L.append("")
    L.append("## 3. 声の使い方の制約(欄に明記済み・testで固定)\n")
    L.append("1. **出典にない出来事・体験・発言を足さない**(経験欄=Eにある出来事だけ。Eが少ないV2・V3の意見欄は仮定・意見の形)。")
    L.append("2. **数字・数量表現を使わない**(Voice Prompt規則9)。回数は『くり返し』『最初の不在は大目に見る』と言い換え済み。Sheet全文でtestが数字0を確認。")
    L.append("3. **個人ブログ・noteの固有の言い回しを写さない**(R2+: RV-55〜59)。Sheetの文はすべて自分の言葉の要約で、逐語抜粋は`VOICES_02.json`にだけある。")
    L.append("4. **世界設定の定義は、そのPersonaの`relevant_terms`だけ渡す**(前回run_03の教訓)。定義文はPersona本文に現れない(testで固定)。")
    L.append("5. 統計・調査(『配達員の約75%が賛成』等)は一切Sheetに入れていない。")
    L.append("6. 2017年・2019年の声(RV-39〜51、V3のRV-40〜42ほか)は『気持ち・事情』の材料に限り、当時の報道に依存する内容は使っていない。\n")
    L.append("## 4. 実在の声との距離・集約の度合い(誠実な注記)\n")
    L.append("- **V1は2人の別のドライバーの集約**: 立場(反対・筋違い・運賃で)=RV-55(note、現役宅配ドライバー)、現場の経験(不在持ち戻りが減った、急かし電話、何分も待てない)=RV-57・58・59(軽貨物ドライバーのブログ)。両者に『現役の宅配(軽貨物)ドライバー』という属性の共通点はあるが、同一人物ではない。")
    L.append("- **V3は別人の声の集約**: 公平感=RV-11・RV-40・RV-41、『営業所が近い人の言い分』の引け目=RV-42、使いにくさ=RV-26(ロッカー/営業所)。RV-26の文脈は『手渡しの有料化・置き配標準化』(隣接する制度論)で、再配達料金そのものではない。V3の再配達有料化への賛成の根拠はRV-11・RV-40〜42に置き、RV-26は『受取手段の使いにくさ』の経験としてのみ使った。")
    L.append("- **V2はRV-08(夫婦とも就労)を軸**に、気持ちの材料としてRV-07(リモート勤務)・RV-65(在宅なのに不在票)の一般化を足した。V2に『在宅勤務』は書いていない(RV-07・RV-65は、家にいる日があっても、という『心配』の意見欄TWO_eに限定)。")
    L.append("- **ユーザー参考例との差**: ドライバー=有料化支持ではなく『反対寄り』を採用した(AXIS_ANALYSIS_03 §4。ドライバー本人の声は割れており、賛成側は2件で3件基準に届かない)。\n")
    L.append("## 5. 確認してほしい点(Fable/Opus)\n")
    L.append("1. 『ドライバー=反対寄り』は参考例と逆向き。実在の声に従った判断で妥当か(賛成ドライバーはRV-28・RV-37の2件のみで、V2/V3と重なる賛成側の立場が強くなる)。")
    L.append("2. V1が全項目R2+(個人ブログ・note)のみを根拠にしている(`tbs_only`相当の印が全項目に付く)。Trial内(DEV/Trial限定)では問題ないが、**公開・商用化の前にはR2+の扱い(許諾 or 他の声への置換)が必要**。")
    L.append("3. Voice Prompt規則9(数量表現禁止)と、回数が論点のテーマとの相性(PROMPT_DIFF_05 §3)。")
    L.append("4. 立場の幅が反対〜条件付き賛成に収まり、全面賛成の声(RV-17・39・46等の『居留守は腹が立つ』型)を立てていない。『不自然に異なる結論を3つ作らない』に従った結果だが、多様性・面白さの評価で不足とされる可能性がある。")
    open(os.path.join(OUT, "PERSONAS_05.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("OK")


if __name__ == "__main__":
    main()
