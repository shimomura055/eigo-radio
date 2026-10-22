# er109_pattern_catalog_md_01.py
# pattern_probe_01.json(er109_pattern_probe_01.py の出力)から PATTERN_CATALOG_01.md の表を生成する(手書き転記ミス防止)。API 0。
# 分類(A/B/C/D/E)の定義はドキュメント冒頭に出力。分類は『既存承認仕様の範囲』を根拠に本ファイルのCLASS表で固定(判断はFable確認事項)。
import json
import sys

SRC = "docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/pattern_probe_01.json"
OUT = "docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/PATTERN_CATALOG_01.md"

# id -> (class, 根拠・未対応の理由・対策)
CLASS = {
    "N11": ("B", "承認済みの複合序数正規化(val._convert_compound_ordinal_words)でclassifyはPASSなのに、非KPの最終ANDゲートの値atom(er021 _tier1_atoms)が`twenty first`を20+literalと解釈し`21st`と値DIFF→NG_PROTECTED(実judgeで再現)。層間不整合の不具合"),
    "H04": ("B", "承認済み同音救済(ER-008-15)が1語テキストでは到達不能: val:1133 のratio<0.4判定(TTS_FAILURE)が同音判定(val:1193)より先。KP英語の12.6%(83/660)が1語"),
    "H13": ("B", "同上(1語テキスト)"),
    "H19": ("B", "同上(1語テキスト)"),
    "M06": ("B", "承認済みPNMH-01多語同音(er094)が短文で到達不能(同じratio<0.4)"),
    "N20": ("B/C境界", "Tier1は『時刻』を謳うが`five thirty`<->`5:30`は未パース(_tier1_atomsがfive=literal/30=number)。承認文言の再確認要(Fable)"),
    "N21": ("B/C境界", "Tier1『時刻』の`o'clock`<->`5:00`未パース。同上"),
    "N26": ("B/C境界", "Tier1『通貨』の`$5.50`<->`five dollars and fifty cents`未パース(セント語)。同上"),
    "N15": ("C", "年代`90s`/`nineties`はTier1の列挙外(列挙: 数値/通貨/%/年/時刻/分数/ローマ数字/略語)"),
    "N29": ("C", "数詞+'s(`2's`/`two's`)。one's<->1's と同型"),
    "N02": ("C", "ユーザー必須例。`one's`はTier1/値ガードでliteral1語、`1's`はnumber atom=対応なし→DIFF(AZURE_ITN_IMPACT_01 §2)。KPは保護解除済みでもclassify_asr_matchが数字<->語を同値化しない(val:313 単独oneは変換しない+Tier1はKey Phrase非適用)"),
    "C02": ("C", "they're/their/there: 承認済み同音救済は内容語1:1のみ(stopwordは対象外 val:742)。contraction展開は展開後に既存が一致する場合のみ"),
    "C03": ("C", "同上"), "C04": ("C", "同上(you're/your)"), "C05": ("C", "同上(who's/whose)"),
    "M07": ("C", "stopword(by)を含む同音。PNMH-01は固有名詞ByUs型。一般語by/buyは対象外"),
    "H09": ("C", "否定語noの同音異表記(know)。『発音同一=同等』を適用すると否定保護との関係でユーザー判断(Opus Q)"),
    "A05": ("C", "`&`<->and: 記号読み未対応(承認済みは通り種別略語のみ val:77)"),
    "A06": ("C", "`+`<->plus"), "A07": ("C", "`°`<->degrees"), "A08": ("C", "`vs.`<->versus"),
    "A10": ("C", "`Dr.`<->doctor"), "A11": ("C", "`St.`<->Saint(承認済みはstreet->st方向のみ)"),
    "A13": ("C", "OK<->okay(1語はratio<0.4でも不達)"), "A14": ("C", "etc.<->et cetera"),
    "A15": ("C", "CMU辞書のtv変種=television(辞書quirk)。TTSの実読みは音声依存。要Opus確認"),
    "T04": ("C", "OK<->okay"),
    "M08": ("C", "ice cream/I scream型(oronym)は承認済み多語同音条件(1:n・単一文字token禁止)の外。er109も同値にしない=新規救済範囲(ユーザー判断)"),
    "H10": ("E", "analyseがCMU未登録=判定不能(fail-closed)。対策=CMU補完辞書/Ledger(別判断)"),
    "H14": ("E", "tyre(T AY1 R)とtire(T AY1 ER0)がCMU音素表記上で不一致=CMU限界。同値化しない(残存偽NG)"),
    "A21": ("E", "`°C`(単位記号)未対応"), "A22": ("E", "月名略語(Jan.)未対応(月名と通常語の衝突)"),
    "M15": ("A", "cannot<->can not: 承認済みdespaced規則/negation_diff正規化で対応済み(er109は不要)"),
    "T08": ("E", "`No. 1`(番号略語)は否定語noと衝突するためer109は未対応。本文はTier1でPASS(KPは非適用)"),
    "N30": ("D", "値は同じだが読み(a hundred/one hundred)が違う。既存はPASSさせる(承認済み値等価)。同等にするかではなく現状維持"),
    "A23": ("A", "CMUのus変種(Y UW EH S)と既存の大小無視により国名US/代名詞usは既存で同一視(承認済み挙動)。注意事項としてOpusへ"),
}
KP_ONLY_FAIL_C = "C-KP"   # 本文(Tier1)はPASS、KP/Whisper票で不合格


def klass(r):
    if r["id"] in CLASS:
        return CLASS[r["id"]]
    if not r["same_pron_expected"]:
        return ("D", "発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例)")
    if r["body_final_after_value_gate"] and r["kp_P"] and r["whisper_vote"]:
        return ("A", "既存で対応済み(全経路PASS)")
    if r["body_final_after_value_gate"] and not (r["kp_P"] and r["whisper_vote"]):
        return (KP_ONLY_FAIL_C, "本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲")
    return ("C", "既存は不合格(要個別確認)")


PREAMBLE = """# PATTERN_CATALOG_01(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01、2026-10-22。API 0・Production無編集)

生成: `er109_pattern_catalog_md_01.py`(入力=`pattern_probe_01.json`=`er109_pattern_probe_01.py`の実行結果)。ユーザー例示は下限であり、本表は体系的な洗い出し(数/所有格・短縮形/同音異綴/語境界/略語・記号/ハイフン・句読点・大小/ASR自動整形)の代表例149件。

## 凡例
- 判定列は、本文P=本文role(FULL_STORY)のProduction相当経路(`classify_asr_match(segment_id)`+同音救済+**非KPの最終ANDゲート**[承認済みequivalence_basisは本物のjudgeと同じくskip])、KP-P=Key Phrase(`kp1_en`)のP/S票相当、Whisper票=`er104._classify`。M1/CS Equivalence/Tier3は再現していない(wav/Azure/凍結候補が要るため。近似層でありここでの対象外)。
- **er109**=提案層(未配線プロトタイプ)。CMU音素列(ストレス無視)と閉じた記号・略語表で同値判定。未登録語・解析不能・欠落/付加は同値にしない(fail-closed)。
- 分類: **A**=既存で対応済み(全経路PASS)、**B**=既存承認仕様の不具合(承認済み規則の意図する範囲なのに、実装/層間の不整合や到達不能でNG。自律修正可・次委任)、**B/C境界**=承認文言の再確認が必要、**C**=新規救済範囲(Trial->VALIDATED->ユーザー採用判断。**C-KP**=本文は既存Tier1でPASSだがKP/Whisper票はTier1非適用[承認済み仕様]のため不合格、KPへの拡張=新規救済範囲)、**D**=発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例、NGのまま)、**E**=CMU辞書の限界・未対応記号で判定不能(同値化しない=残存偽NG)。
- 偽PASSリスク欄は設計案(DESIGN_PROPOSAL_01.md §3)の負例評価を参照: 提案層による新規誤同値は負例35(カタログ)+KP 3,049+本文3,749(機械生成)で**0**。

## 集計
{SUMMARY}

## 表
"""


EXTRA = """

## カタログ外(代表を実測せず、設計上の扱いだけを記す)
| 型 | 例 | 扱い |
|---|---|---|
| 範囲・ハイフン付き数 | `10-20 minutes`/`ten to twenty` | er109は解析不能(number_unparsed)=同値にしない。`to`/`through`の読みが一意でないため新規救済しない |
| 長い数字列・電話番号・桁0始まり | `555-0123` | 解析不能(long_digit_string_ambiguous/number_leading_zero)=同値にしない |
| 日付(スラッシュ・月名略語) | `3/4/2026`/`Jan. 5` | 未対応。月名略語は通常語と衝突(may/mar/sat)。C候補(要判断)かE |
| ローマ数字 | `Henry VIII` | 既存Tier1(5 role)。er109は対象外 |
| 単位記号 | `20°C`/`m²` | `km`/`lb(s)`/`oz`/`mph`は表にあるが`°C`等は未対応(E) |
| 省略・口語 | `gonna`/`wanna`/`'cause`/`y'all`/`kinda` | 発音が異なる(CMU)=D。`want to`<->`wanna`は2026-09-07ユーザー不採用 |
| filler除去・言い直し | `um, I think` | 脱落=発音一致ではない。既存disfluency QAの管轄でD |
| 国名/代名詞 `US`/`us` | `the US` / `the us` | CMUのus変種(Y UW EH S)と既存の大小無視で既存が同一視(承認済み挙動、Opus注意事項) |
| CMU音素表記の差 | `tyre`/`tire`(R vs ER) | E: 辞書限界。同値にしない(残存偽NG)。補完辞書は別判断 |
| 固有名詞の表記ゆれ | `Kristie`/`Christie` | 既存G9(代表発音のみ・entity_like)を尊重。er109は固有名詞(canonical側大文字始まり)を代表発音のみで比較 |
| 4桁を年と読むか数と読むか | `2024` | 年読み(twenty twenty four)と基数読み(two thousand ...)の両候補のどれか一致で同値 |
"""


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    lines = ["| ID | 区分 | 期待文 / ASR転写 | 本文P(最終ゲート後) | KP-P | Whisper票 | er109 | 分類 | 根拠・対策 |", "|---|---|---|---|---|---|---|---|---|"]
    from collections import Counter
    cnt = Counter()
    for r in d["rows"]:
        k, why = klass(r)
        cnt[k] += 1
        mark = lambda b: "PASS" if b else "NG"
        body = mark(r["body_final_after_value_gate"]) + (f"({r['body_P_label']})" if r["body_P"] else "")
        lines.append(f"| {r['id']} | {r['cat']} | `{r['canonical']}` / `{r['asr']}` | {body} | {mark(r['kp_P'])} | {mark(r['whisper_vote'])} | "
                     f"{'同値' if r['er109'] else '非同値'}({r['er109_reason'][:24]}) | {k} | {why} |")
    sm = d["summary"]
    summary = (f"- 正例(同一発音、n={sm['pos']['er109'][1]}): 本文P(最終ゲート後) {sm['pos']['body_final_after_value_gate'][0]}、KP-P {sm['pos']['kp_P'][0]}、"
               f"Whisper票 {sm['pos']['whisper_vote'][0]}、**er109 {sm['pos']['er109'][0]}**\n"
               f"- 負例(発音が異なる、n={sm['neg']['er109'][1]}): 既存の誤PASS {sm['neg']['body_final_after_value_gate'][0]}(N30: 値は同じで読みだけ違う=承認済み値等価)、"
               f"**er109の誤同値 {sm['neg']['er109'][0]}**\n"
               f"- 分類件数: " + ", ".join(f"{k}={v}" for k, v in sorted(cnt.items())) + "\n")
    open(OUT, "w", encoding="utf-8", newline="\n").write(PREAMBLE.replace("{SUMMARY}", summary) + "\n".join(lines) + "\n" + EXTRA)
    print(dict(cnt))


if __name__ == "__main__":
    main()
