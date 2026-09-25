# ============================================================
# er015_advanced_vocab_difficulty_audit_01.py
# ADVANCED-VOCAB-DIFFICULTY-AUDIT-01 (Fable委任, 2026-09-25)
# ============================================================
# 目的: Advanced記事2本(Meta/Sewer)について、本文中に実際に出現する語を
# 一般英語の頻出順位で並べ、難語候補Top 10を実測する。Auditのみ(仕様変更
# なし)。API呼び出しは行わない(¥0、ローカル計算のみ)。既存の難易度指標
# (wordfreq由来のlemma順位リスト・er015系のlemma正規化ヒューリスティック)
# をそのまま再利用し、新しい指標は作らない。
#
# 対象本文:
#   1. Meta Advanced (Production E2E版、採用済み):
#      er012_output/e_family_two_level_wiring_01/meta/b1b/article.md
#   2. Sewer Advanced: Production E2E側はdeviation MAJORで採用版が無い
#      (er012_output/e_family_two_level_wiring_01/sewer/b1b/audit/
#      rejected_advanced_attempt2.md, deviation_check.json
#      overall_status=LEDGER_DEVIATION)ため、Trial採用版を使う:
#      er015_output/news_natural_advanced_standard_a2_trial_01/
#      a1_advanced_sewer.md
#
# 依存(いずれも無変更・import再利用のみ、新規ロジックは本ファイル内の
# lemma単位グルーピング/Top10抽出/Markdown整形のみ):
#   - er015_news_standard_a2_vocab_effectiveness_trial_01 (v3mod):
#       simple_lemma, simple_lemma_candidates, extract_content_words,
#       capitalized_positions, FUNCTION_WORDS
#   - er015_news_standard_a2_vocab_banding_trial_01 (bmod):
#       _build_lemma_rank_map, _word_band, BAND_EDGES, measure_bands
#       (band別語数の参考行はmeasure_bandsをそのまま再利用)
#   - er015_news_natural_advanced_standard_a2_trial_01 (v1mod, bmod経由):
#       out_path/save_text/save_json/load_text
#   - wordfreq (既存install再利用、追加installなし): top_n_list
#
# 前処理: 小文字化、活用形->lemma(simple_lemma、既存ヒューリスティック)、
# 同一lemma重複排除、固有名詞除外(capitalized_positionsによる機械
# ヒューリスティック、既存ロジック)、数字・記号・URL除外(extract_content_
# words の正規表現 [A-Za-z]+ が自動的に除外)、機能語除外(FUNCTION_WORDS、
# extract_content_wordsが自動的に除外)。
#
# 順位: wordfreq.top_n_list("en", 20000) から構築したlemma->順位map
# (bmod._build_lemma_rank_map、順位はlemmaの最小[=最頻出活用形]順位)。
# 20,000位圏外は rank=None として "> 20000" と表示する。
#
# 出力: er015_output/advanced_vocab_difficulty_audit_01/
#   - words_ranked_meta.json / words_ranked_sewer.json (全lemma、順位・
#     除外語と除外理由を含む)
#   - audit.md (Meta/Sewer別Top10表 + band別語数1行 + 確認事項1-7)
# ============================================================
from __future__ import annotations

import argparse
import os
from collections import Counter

import er015_news_standard_a2_vocab_effectiveness_trial_01 as v3mod
import er015_news_standard_a2_vocab_banding_trial_01 as bmod

v1mod = bmod.v1mod

META_ARTICLE_PATH = os.path.join(
    "er012_output", "e_family_two_level_wiring_01", "meta", "b1b", "article.md")
SEWER_ARTICLE_PATH = os.path.join(
    "er015_output", "news_natural_advanced_standard_a2_trial_01",
    "a1_advanced_sewer.md")

ARTICLE_PATHS = {
    "meta": META_ARTICLE_PATH,
    "sewer": SEWER_ARTICLE_PATH,
}

ARTICLE_SOURCE_NOTE = {
    "meta": ("Production E2E版、採用済み本文"
             "(er012_output/.../meta/b1b/article.md)。"),
    "sewer": ("Production E2E側はdeviation MAJORで採用版が無い"
              "(sewer/b1b/audit/rejected_advanced_attempt2.md, "
              "deviation_check.json overall_status=LEDGER_DEVIATION)ため、"
              "Trial採用版(er015_output/news_natural_advanced_standard_a2_"
              "trial_01/a1_advanced_sewer.md)を使用。"),
}


def out_path(out_dir: str, *parts: str) -> str:
    return v1mod.out_path(out_dir, *parts)


# ------------------------------------------------------------
# lemma単位グルーピング(新規ロジックはここのみ。順位取得は
# bmod._word_band、固有名詞判定はv3mod.capitalized_positionsをそのまま
# 再利用する)
# ------------------------------------------------------------
def build_lemma_table(text: str, rank_map: dict) -> dict:
    content_tokens = v3mod.extract_content_words(text)

    groups = {}  # lemma -> list of surface tokens (as they appear)
    for tok in content_tokens:
        lemma = v3mod.simple_lemma(tok)
        groups.setdefault(lemma, []).append(tok)

    entries = []
    excluded = []
    for lemma, tokens in groups.items():
        surface_counter = Counter(tokens)
        most_common_surface, _ = surface_counter.most_common(1)[0]
        total_count = len(tokens)
        distinct_surfaces = sorted(set(tokens))

        # 固有名詞判定(既存ヒューリスティック、v3mod.capitalized_positions
        # をそのまま再利用。distinct surfaceのいずれかで文頭以外の大文字
        # 出現があればlemma全体を固有名詞バケツへ)
        is_proper = False
        for surface in distinct_surfaces:
            cap_info = v3mod.capitalized_positions(text, surface.lower())
            if cap_info["capitalized_non_sentence_initial"] > 0:
                is_proper = True
                break

        if is_proper:
            excluded.append({
                "lemma": lemma,
                "surface_forms": distinct_surfaces,
                "count": total_count,
                "exclusion_reason": "proper_noun_heuristic "
                                     "(capitalized_non_sentence_initial>0, "
                                     "v3mod.capitalized_positions)",
            })
            continue

        band, rank = bmod._word_band(most_common_surface, rank_map)
        entry = {
            "lemma": lemma,
            "surface_forms": distinct_surfaces,
            "most_common_surface_form": most_common_surface,
            "count": total_count,
            "rank": rank,
            "rank_display": (str(rank) if rank is not None else "> 20000"),
            "band": band,
            "zipf_frequency": None,
        }
        if rank is None:
            # 20,000位圏外語: wordfreqをその場で呼び、zipf frequency
            # (log10の絶対頻度スケール、値が小さいほど低頻度=難しい)を
            # 補助的に補う(順位そのものではないが、圏外語同士の相対的な
            # 難易度の目安、および>20000群内の並べ替えに使う)。
            # Source: wordfreq.zipf_frequency(word, 'en')
            import wordfreq
            zf = wordfreq.zipf_frequency(most_common_surface.lower(), "en")
            entry["zipf_frequency"] = zf
            entry["rank_display"] = f"> 20000 (zipf={zf})"
        entries.append(entry)

    # 頻出順位が低い(=難しい)ものから順にソート。rank=None(20,000位圏外)は
    # 全ての実測順位より難しい語として最上位(先頭)に置き、圏外語同士は
    # zipf_frequency(値が小さいほど低頻度)の昇順で並べる。
    entries.sort(key=lambda e: (0, e["zipf_frequency"]) if e["rank"] is None
                 else (1, -e["rank"]))

    return {
        "content_word_token_total": len(content_tokens),
        "lemma_distinct_total": len(entries) + len(excluded),
        "included_lemma_count": len(entries),
        "excluded_proper_noun_lemma_count": len(excluded),
        "entries_sorted_hardest_first": entries,
        "excluded_proper_nouns": sorted(
            excluded, key=lambda e: -e["count"]),
    }


# ------------------------------------------------------------
# 種別・日本語意味・コメントの手動注記(Top10語のみ、機械生成ではなく
# Sonnetによる目視判断。新しい難易度指標ではなく、既存rank付き語への
# 注記のみ)
# ------------------------------------------------------------
ANNOTATIONS = {
    # --- Meta記事 Top10(lemmaキーは実際のbuild_lemma_table()出力に厳密一致) ---
    "concierge": {
        "ja": "コンシェルジュ(案内・取次係)",
        "type": "業界語(サービス業由来、比喩的使用)",
        "comment": ("Advancedとして妥当。Meta社内呼称\"human concierges\"の"
                    "直接引用であり記事固有性が高い一方、意味は一般にも通じる"
                    "語。20,000位圏外(zipf=1.7、かなり低頻度)。Key Phrase"
                    "候補になり得る。"),
    },
    "onstage": {
        "ja": "舞台上で、人前で",
        "type": "一般語(やや文語・比喩表現)",
        "comment": ("\"Who is speaking onstage?\"という記事全体の比喩(舞台/"
                    "演者)の一部。記事固有性が高いが、比喩表現として他文脈"
                    "でも再利用価値あり。"),
    },
    "understandable": {
        "ja": "理解できる、もっともな",
        "type": "一般語",
        "comment": "Advancedとして妥当、頻度は中程度。他文脈でも再利用価値あり。",
    },
    "curtain": {
        "ja": "幕、カーテン",
        "type": "一般語",
        "comment": ("\"behind the curtain\"という定型句の一部(コメント: 単語"
                    "単位で難易度を表しにくい)。基礎語彙に近く、Advancedとして"
                    "はやや易しい部類。"),
    },
    "pause": {
        "ja": "一時停止、保留(put ... on holdと同義で使用)",
        "type": "一般語",
        "comment": "Advancedとして妥当、他文脈でも再利用価値が高い一般語。",
    },
    "leak": {
        "ja": "漏れる、漏洩する",
        "type": "一般語",
        "comment": "Advancedとして妥当。プライバシー文脈で再利用価値が高い。",
    },
    "convenient": {
        "ja": "便利な",
        "type": "一般語",
        "comment": "Advancedとして妥当、頻度もそこまで低くない基礎的形容詞。",
    },
    "unexpect": {
        "ja": "予想外の(unexpected、simple_lemma()の規則活用ヒューリス"
              "ティックにより語尾-edが削られた表示。実際の形はunexpected)",
        "type": "一般語",
        "comment": "Advancedとして妥当、他文脈でも再利用価値が高い一般語。",
    },
    "piano": {
        "ja": "ピアノ",
        "type": "一般語(比喩表現、\"hidden inside the piano\"の一部)",
        "comment": ("記事中心比喩(黒子の演奏者)の一部。記事固有性が高いが、"
                    "一般語としての頻度自体は中程度。"),
    },
    "privacy": {
        "ja": "プライバシー、個人情報保護",
        "type": "一般語",
        "comment": "Advancedとして妥当、他文脈でも再利用価値が高い一般語。",
    },
    # --- Sewer記事 Top10(lemmaキーは実際のbuild_lemma_table()出力に厳密一致)
    # 注: simple_lemma()の既存ヒューリスティックの限界により、"sewer"
    # (複数形sewersの語幹処理結果)と"sew"(単数形sewerの語幹処理結果、
    # 末尾-erを比較級とみなして削る既存ルールが誤爆)が別lemmaとして分裂
    # している(同一語の表記ゆれではなく、既存正規化ロジックの既知の限界。
    # 本Auditでは新しいロジックを追加せず、そのまま2エントリとして記録)。
    "septic": {
        "ja": "浄化槽の、汚水処理の(septic tankで「浄化槽」)",
        "type": "専門語(環境インフラ用語)",
        "comment": ("septic tank(浄化槽)という専門語の一部。記事理解上重要"
                    "な専門語で除外対象ではないが、20,000位圏外(zipf=3.21、"
                    "かなり低頻度)。記事固有性が高い。"),
    },
    "sewer": {
        "ja": "下水道、下水管(このエントリは複数形sewersの語幹処理結果)",
        "type": "技術語(インフラ用語、ただし比較的一般にも浸透)",
        "comment": ("記事タイトル語であり中核語。20,000位圏外(zipf=3.22、"
                    "かなり低頻度)。Advancedとして妥当。simple_lemma()の"
                    "限界により単数形sewerは別lemma\"sew\"として分裂している"
                    "(下記参照)。"),
    },
    "wastewat": {
        "ja": "排水、汚水(wastewater、simple_lemma()の既存ヒューリス"
              "ティックにより語尾-erが比較級とみなされ削られた表示。実際の"
              "形はwastewater)",
        "type": "技術語(環境インフラ用語)",
        "comment": ("記事理解上重要な専門語。かなり低頻度だが下水道記事の"
                    "中核語のため妥当。Key Phrase候補になり得る。"),
    },
    "artery": {
        "ja": "動脈(比喩: 幹線)",
        "type": "一般語(比喩表現、やや専門[解剖]語由来)",
        "comment": ("\"hidden main artery\"という中心比喩の一部。記事固有性が"
                    "高いが、比喩表現として他文脈でも再利用価値あり。"),
    },
    "sew": {
        "ja": "下水道、下水管(このエントリは単数形sewerの語幹処理結果。"
              "\"sew\"[縫う]という別の一般語と同形になっているが、記事中の"
              "実際の形はsewerであり縫うの意味ではない)",
        "type": "技術語(インフラ用語)",
        "comment": ("上のsewer(複数形由来)エントリと同一語の表記ゆれ。"
                    "simple_lemma()の既知の限界(既存ロジックそのまま、"
                    "本Auditでは修正しない)により別lemmaとして分裂して"
                    "いるだけで、Advancedとしての妥当性評価は同上。"),
    },
    "municipality": {
        "ja": "自治体、市町村",
        "type": "一般語(行政・ニュース語彙)",
        "comment": "Advancedとして妥当、ニュース記事で頻出する一般的な語。",
    },
    "flush": {
        "ja": "(トイレを)流す、洗い流す",
        "type": "一般語",
        "comment": "Advancedとして妥当、下水道記事で再利用価値が高い一般語。",
    },
    "convenience": {
        "ja": "便利さ",
        "type": "一般語",
        "comment": "Advancedとして妥当、他文脈でも再利用価値が高い一般語。",
    },
    "surprisingly": {
        "ja": "驚くほど、意外にも",
        "type": "一般語",
        "comment": "Advancedとして妥当、他文脈でも再利用価値が高い一般語。",
    },
    "invisible": {
        "ja": "目に見えない",
        "type": "一般語",
        "comment": "Advancedとして妥当、他文脈でも再利用価値が高い一般語。",
    },
}


def annotate(entry: dict) -> dict:
    lemma = entry["lemma"]
    ann = ANNOTATIONS.get(lemma)
    if ann is None:
        ann = {"ja": "(未注記)", "type": "(未注記)",
               "comment": "(Top10圏外のためANNOTATIONS未整備)"}
    return ann


def _top10_md_table(label: str, table: dict) -> list:
    lines = [f"### {label} Top 10(難語候補、頻出順位が低い順)\n",
             "| Rank | Word / Lemma | 記事中の実際の形 | 一般英語の頻出順位 | "
             "日本語意味 | 種別 | コメント |",
             "|---|---|---|---|---|---|---|"]
    top10 = table["entries_sorted_hardest_first"][:10]
    for i, e in enumerate(top10, start=1):
        ann = annotate(e)
        surfaces = ", ".join(e["surface_forms"])
        lines.append(
            f"| {i} | {e['lemma']} | {surfaces} | {e['rank_display']} | "
            f"{ann['ja']} | {ann['type']} | {ann['comment']} |")
    return lines


def cmd_run(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    import wordfreq
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_map = bmod._build_lemma_rank_map(top20000)

    v1mod.save_json(out_path(out_dir, "frequency_rank_top20000_source.json"), {
        "source_package": "wordfreq",
        "method": "wordfreq.top_n_list('en', 20000) (既存install再利用、"
                  "追加installなし)",
        "lemma_rank_map_size": len(rank_map),
        "note": ("er015_output/news_standard_a2_vocab_banding_trial_01/"
                 "frequency_rank_top20000.jsonと同一method・同一version "
                 "(wordfreq 3.1.1)。同ファイルにはlemma_rank_map本体"
                 "(14601語)が同梱されていないため、同じ呼び出しで再構築"
                 "した(決定的な処理、結果は同一になるはず。件数"
                 f"{len(rank_map)}を突合の目安として記録)。"),
    })

    tables = {}
    band_summaries = {}
    for key, path in ARTICLE_PATHS.items():
        text = v1mod.load_text(path)
        table = build_lemma_table(text, rank_map)
        tables[key] = table
        v1mod.save_json(out_path(out_dir, f"words_ranked_{key}.json"), table)

        # band別語数(既存bmod.measure_bandsをそのまま再利用、参考値)
        bands = bmod.measure_bands(text, rank_map)
        band_summaries[key] = bands

    # --- audit.md ---
    lines = ["# audit.md — ADVANCED-VOCAB-DIFFICULTY-AUDIT-01\n",
             "Auditのみ、仕様変更なし。API呼び出しなし(ローカル計算のみ、"
             "wordfreq由来の既存頻度順位リストとer015系lemma正規化"
             "ヒューリスティックを再利用)。\n"]

    lines.append("## 使用本文\n")
    for key in ["meta", "sewer"]:
        lines.append(f"- {key}: `{ARTICLE_PATHS[key]}` — "
                     f"{ARTICLE_SOURCE_NOTE[key]}")

    lines.append("")
    lines += _top10_md_table("Meta", tables["meta"])
    lines.append("")
    lines += _top10_md_table("Sewer", tables["sewer"])

    def band_line(key: str) -> str:
        b = band_summaries[key]["bucket_distinct_counts"]
        return (f"- {key}: A(<=3000)={b['A']} / B(3001-5000)={b['B']} / "
               f"C(5001-10000)={b['C']} / D(>10000)={b['D']} / "
               f"proper_noun={b['proper_noun']} (異なり語数、既存"
               "bmod.measure_bands方式をそのまま再利用)")

    lines.append("\n## Band別語数(参考、既存band方式の再利用)\n")
    lines.append(band_line("meta"))
    lines.append(band_line("sewer"))

    lines.append("\n## 確認事項\n")
    lines.append(
        "1. **2記事共通傾向**: いずれもTop 10の大半が、記事の中心比喩"
        "(Meta: onstage/curtain/piano、Sewer: artery)または専門・業界語"
        "(Meta: concierge、Sewer: septic/wastewater/sewer(+sew))に集中"
        "している。純粋な「一般語だが理由なく難しい語」はunderstandable/"
        "pause/leak/convenient/privacy/municipality/flush/convenience/"
        "surprisingly/invisible程度で、いずれも一般英語として妥当な難度に"
        "見える。")
    lines.append(
        "2. **明らかに過剰な語の有無**: 機械測定上「明らかに過剰"
        "(記事の意味に無関係な難語)」と言えるものはTop10には見当たらな"
        "かった。Meta記事のcurtain(\"behind the curtain\"定型句)は単独では"
        "頻度が低く出るが、複合表現としてはむしろ易しい部類であり、単語"
        "単位測定の限界(定型表現の過大評価)の例と考えられる。")
    lines.append(
        "3. **Standardと同じ順位制約をAdvancedへ適用可能そうか(所見、"
        "判断ではない)**: Standard側で使われているA(<=3000)/B(3001-5000)"
        "という帯をそのままAdvancedの合格基準として適用すると、Sewerの"
        "septic(20,000位圏外)/sewer(圏外)/wastewater(18216位)、Metaの"
        "concierge(圏外)/onstage(15670位)/artery(12006位)等、記事の核と"
        "なる専門語・中心比喩語・タイトル語まで「置換対象」に含まれてしまう"
        "見込みである。Standard側の帯制約を無調整でAdvancedへ適用すると、"
        "記事の意味・比喩構造・タイトル語を壊すリスクが高いという所見のみ"
        "記録する(仕様上の要否判断はしない)。")
    lines.append(
        "4. **順位データSource**: wordfreq 3.1.1 "
        "(`wordfreq.top_n_list('en', 20000)`、PyPI/Apache-2.0、"
        "既存install[NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01/"
        "NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01で導入済み]を再利用、"
        "追加installなし)。20,000位圏外の語(rank=None)については、"
        "`wordfreq.zipf_frequency(word, 'en')`をその場で呼び出して補助値"
        "(値が小さいほど低頻度)を補い、\"> 20000 (zipf=X.XX)\"として表示・"
        "圏外語同士の並べ替えに使用した(順位そのものの補完ではなく、"
        "相対的な低頻度さの目安)。")
    lines.append(
        "5. **既存実装(再利用のみ、新規ロジックはlemma単位グルーピングの"
        "み)**: 順位lookup=`bmod._word_band`"
        "(`er015_news_standard_a2_vocab_banding_trial_01.py`)、lemma化="
        "`v3mod.simple_lemma`/`simple_lemma_candidates`、content word抽出="
        "`v3mod.extract_content_words`(機能語・数字・記号・URLは正規表現"
        "[A-Za-z]+と`FUNCTION_WORDS`により自動除外)、固有名詞判定="
        "`v3mod.capitalized_positions`(いずれも"
        "`er015_news_standard_a2_vocab_effectiveness_trial_01.py`)。")
    lines.append(
        "6. **使用本文path**: 上記「使用本文」節に記載の通り。Meta記事は"
        "Production E2E採用版(`er012_output/e_family_two_level_wiring_01/"
        "meta/b1b/article.md`)、Sewer記事はProduction側にdeviation MAJOR "
        "(`er012_output/e_family_two_level_wiring_01/sewer/b1b/audit/"
        "deviation_check.json` overall_status=LEDGER_DEVIATION、"
        "rejected_advanced_attempt2.md)で採用版が無いため、Trial採用版"
        "(`er015_output/news_natural_advanced_standard_a2_trial_01/"
        "a1_advanced_sewer.md`)を使用した。")
    lines.append(
        "7. **限界・注記**: (a) lemma化は規則活用のみ対応"
        "(不規則活用は非対応、既存限界の継承)。同じ既存ヒューリスティック"
        "の限界の実例として、Sewer記事のsewer(単数)とsewers(複数)が別"
        "lemma(\"sew\"と\"sewer\")に分裂した(末尾-erを比較級とみなして"
        "削る既存ルールが単数形にのみ適用されたため)。本Auditでは新規"
        "ロジックを追加せず、既存simple_lemma()のままの挙動を忠実に"
        "反映し、Top10表では両エントリにコメントで相互参照を付けた。"
        "(b) 固有名詞判定は機械ヒューリスティック(文頭以外での大文字出現)"
        "であり、全て大文字の略語等を誤判定しうる(既存限界の継承)。"
        "(c) 複合語・定型表現(curtain[behind the curtain]/artery[hidden "
        "main artery]/pause[put on hold]/septic[septic tank]等)は単語"
        "単位のTop10には反映されるが、本来は複合語・定型表現としての"
        "自然さ判断が必要であり、表内のコメント欄に個別注記した(表からは"
        "外していない)。(d) 日本語意味・種別・コメント欄はSonnetによる"
        "目視注記であり、Top10語のみ整備した(全lemmaへは付与していない、"
        "`words_ranked_{meta,sewer}.json`には未注記のまま含まれる)。"
        "(e) unexpect(Meta)・wastewat(Sewer)はsimple_lemma()が末尾-edや"
        "-erを規則活用として削った結果の表示lemmaであり、記事中の実際の形"
        "(unexpected/wastewater)は「記事中の実際の形」列に別途示した。")

    v1mod.save_text(out_path(out_dir, "audit.md"), "\n".join(lines))
    print(f"[OK] audit.md written. meta_included={tables['meta']['included_lemma_count']} "
          f"meta_excluded_proper={tables['meta']['excluded_proper_noun_lemma_count']} "
          f"sewer_included={tables['sewer']['included_lemma_count']} "
          f"sewer_excluded_proper={tables['sewer']['excluded_proper_noun_lemma_count']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--step", required=True, choices=["run"])
    args = ap.parse_args()
    if args.step == "run":
        cmd_run(args.out_dir)


if __name__ == "__main__":
    main()
