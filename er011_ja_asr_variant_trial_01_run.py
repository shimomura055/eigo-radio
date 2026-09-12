# ============================================================
# er011_ja_asr_variant_trial_01_run.py
# JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01 実行スクリプト
# ============================================================
# 自作テストセット(過去ログ外、(a)ひらがな⇔漢字/(b)ひらがな⇔カタカナ/
# (c)同音異表記/(d)送り仮名・活用形、+数字助数詞/長音表記ゆれ/句読点)と、
# 過去実データ(TRUE_CONTENT_MISMATCH記録+Human Review記録+過去PASS記録)
# を、baseline(現行Production、Resolverはdry-run stub=呼び出し回数のみ
# 計測・実際のLLM呼び出しなし)とCandidate B(fugashi+unidic-lite形態素
# 読みエンジン、¥0・LLM不要)で分類し、結果をJSONへ保存する。
from __future__ import annotations

import json
import sys

import er011_ja_asr_variant_trial_01 as trial

# ------------------------------------------------------------
# 自作テストセット(過去ログ外、自作)
# 各要素: canonical / asr / expected("PASS" or "MISMATCH") / category / note
# ------------------------------------------------------------
DATASET = []

def add(category, canonical, asr, expected, note=""):
    DATASET.append({"category": category, "canonical": canonical, "asr": asr,
                     "expected": expected, "note": note})

# --- (a) ひらがな⇔漢字: POSITIVE(同じ読み・同じ意味) ---
add("a_kanji_hiragana", "洗濯しても、時間が経つと何かが残る。", "洗濯しても、時間がたつと何かが残る。", "PASS", "経つ/たつ(報告事例そのもの)")
add("a_kanji_hiragana", "会議の前に準備を行います。", "会議の前に準備をおこないます。", "PASS", "行う/おこなう")
add("a_kanji_hiragana", "気持ちを表す言葉を選ぶ。", "気持ちをあらわす言葉を選ぶ。", "PASS", "表す/あらわす")
add("a_kanji_hiragana", "最後まで頑張ろうと決めた。", "最後までがんばろうと決めた。", "PASS", "頑張る/がんばる")
add("a_kanji_hiragana", "とても綺麗な景色が広がる。", "とてもきれいな景色が広がる。", "PASS", "綺麗/きれい")
add("a_kanji_hiragana", "簡単に出来ることから始める。", "簡単にできることから始める。", "PASS", "出来る/できる")
add("a_kanji_hiragana", "理由が分かる時が来る。", "理由がわかる時が来る。", "PASS", "分かる/わかる")
add("a_kanji_hiragana", "変化に気付く人は少ない。", "変化にきづく人は少ない。", "PASS", "気付く/きづく")
add("a_kanji_hiragana", "答えを見つける方法を探す。", "答えをみつける方法を探す。", "PASS", "見つける/みつける")
add("a_kanji_hiragana", "夕方頃に駅へ着く予定。", "夕方ころに駅へ着く予定。", "PASS", "頃/ころ(既知の限界カテゴリ、既存voicing許容で解決済みのはず)")
add("a_kanji_hiragana", "作業の後で少し休みます。", "作業のあとで少し休みます。", "PASS", "後/あと(既知の限界カテゴリ、既存Reading Resolverで解決済みのはず)")
add("a_kanji_hiragana", "一番好きな料理はカレーです。", "いちばん好きな料理はカレーです。", "PASS", "一番/いちばん")
# --- (a) NEGATIVE(表記ゆれに見えるが実際は別の語・別の読み) ---
add("a_kanji_hiragana", "時間が経つと何が残るのか。", "時間が勝つと何が残るのか。", "MISMATCH", "経つ(たつ)/勝つ(かつ)、別の語")
add("a_kanji_hiragana", "作業の後で少し休みます。", "作業の前で少し休みます。", "MISMATCH", "後(あと)/前(まえ)、別の語")
add("a_kanji_hiragana", "理由が分かる時が来る。", "理由が別れる時が来る。", "MISMATCH", "分かる(わかる)/別れる(わかれる)、別の語")
add("a_kanji_hiragana", "答えを見つける方法を探す。", "答えを見捨てる方法を探す。", "MISMATCH", "見つける/見捨てる、別の語")

# --- (b) ひらがな⇔カタカナ: POSITIVE ---
add("b_hiragana_katakana", "洗って乾かしても、においが残る。", "洗って乾かしても、ニオイが残る。", "PASS", "におい/ニオイ(報告事例そのもの)")
add("b_hiragana_katakana", "とてもきれいな花が咲いた。", "とてもキレイな花が咲いた。", "PASS", "きれい/キレイ")
add("b_hiragana_katakana", "これはすごい発見だと思う。", "これはスゴイ発見だと思う。", "PASS", "すごい/スゴイ")
add("b_hiragana_katakana", "本当にやばい状況だった。", "本当にヤバイ状況だった。", "PASS", "やばい/ヤバイ")
add("b_hiragana_katakana", "それはだめですよと言われた。", "それはダメですよと言われた。", "PASS", "だめ/ダメ")
add("b_hiragana_katakana", "それはうそでしょうと笑った。", "それはウソでしょうと笑った。", "PASS", "うそ/ウソ")
add("b_hiragana_katakana", "上達のこつをつかむまで練習した。", "上達のコツをつかむまで練習した。", "PASS", "こつ/コツ")
add("b_hiragana_katakana", "からだを動かす習慣をつける。", "カラダを動かす習慣をつける。", "PASS", "からだ/カラダ")
add("b_hiragana_katakana", "素直なきもちを伝えることが大切。", "素直なキモチを伝えることが大切。", "PASS", "きもち/キモチ")
add("b_hiragana_katakana", "独特なあじがするスープだった。", "独特なアジがするスープだった。", "PASS", "あじ/アジ")
add("b_hiragana_katakana", "秘密のたねを明かす時が来た。", "秘密のタネを明かす時が来た。", "PASS", "たね/タネ")
add("b_hiragana_katakana", "洗濯物の臭いが気になる。", "洗濯物のニオイが気になる。", "PASS", "臭い/ニオイ(漢字→カタカナ、報告事例の別パターン)")
# --- (b) NEGATIVE ---
add("b_hiragana_katakana", "本当にやばい状況だった。", "本当にやわい状況だった。", "MISMATCH", "やばい/やわい、別の語")
add("b_hiragana_katakana", "それはだめですよと言われた。", "それはためですよと言われた。", "MISMATCH", "だめ/ため、別の語")
add("b_hiragana_katakana", "それはうそでしょうと笑った。", "それはうわさでしょうと笑った。", "MISMATCH", "うそ/うわさ、別の語")
add("b_hiragana_katakana", "上達のこつをつかむまで練習した。", "上達のことをつかむまで練習した。", "MISMATCH", "こつ/こと、別の語")

# --- (c) 同音異表記(異なる漢字・同じ読み・同義/慣用的に交換可能) ---
add("c_homophone_kanji", "休日は音楽を聞く時間が長い。", "休日は音楽を聴く時間が長い。", "PASS", "聞く/聴く(きく)")
add("c_homophone_kanji", "来週、友人に会う約束をした。", "来週、友人に逢う約束をした。", "PASS", "会う/逢う(あう)")
add("c_homophone_kanji", "新しい未来を作る取り組み。", "新しい未来を創る取り組み。", "PASS", "作る/創る(つくる)")
add("c_homophone_kanji", "心が暖かい言葉をもらった。", "心が温かい言葉をもらった。", "PASS", "暖かい/温かい(あたたかい)")
add("c_homophone_kanji", "考え方を変える力になる。", "考え方を換える力になる。", "PASS", "変える/換える(かえる)")
add("c_homophone_kanji", "到着がとても早い便を選んだ。", "到着がとても速い便を選んだ。", "PASS", "早い/速い(はやい)")
add("c_homophone_kanji", "画面に写す方法を説明する。", "画面に映す方法を説明する。", "PASS", "写す/映す(うつす)")
add("c_homophone_kanji", "薬がよく効く体質だと聞いた。", "薬がよく利く体質だと聞いた。", "PASS", "効く/利く(きく)")
add("c_homophone_kanji", "試験に望む姿勢を整える。", "試験に臨む姿勢を整える。", "PASS", "望む/臨む(のぞむ)")
add("c_homophone_kanji", "道を尋ねる観光客が多い。", "道を訊ねる観光客が多い。", "PASS", "尋ねる/訊ねる(たずねる)")
# --- (c) NEGATIVE(同音に見えるが実際は読みが異なる、または内容が異なる) ---
add("c_homophone_kanji", "部屋の湿度が高いと感じる。", "部屋の死図塔が高いと感じる。", "MISMATCH", "湿度(しつど)/死図塔(しずとう)、実データ抽出の真ASR誤り")
add("c_homophone_kanji", "新しい意識を持つ社員が増えた。", "新しい移植を持つ社員が増えた。", "MISMATCH", "意識(いしき)/移植(いしょく)、別の読み")
add("c_homophone_kanji", "豊富な経験を持つ講師が担当。", "豊富な敬遠を持つ講師が担当。", "MISMATCH", "経験(けいけん)/敬遠(けいえん)、別の読み")
add("c_homophone_kanji", "毎朝の対応が求められる仕事。", "毎朝の体操が求められる仕事。", "MISMATCH", "対応(たいおう)/体操(たいそう)、別の読み")

# --- (d) 送り仮名・活用形・一般的な表記差 ---
add("d_okurigana", "来月の会議を行ないます。", "来月の会議を行います。", "PASS", "行なう/行う")
add("d_okurigana", "気持ちを表わす方法を考える。", "気持ちを表す方法を考える。", "PASS", "表わす/表す")
add("d_okurigana", "小さな変化が起こる理由。", "小さな変化が起る理由。", "PASS", "起こる/起る")
add("d_okurigana", "参加を申し込む方法を確認する。", "参加を申込む方法を確認する。", "PASS", "申し込む/申込む")
add("d_okurigana", "課題に取り組む姿勢を見せる。", "課題に取組む姿勢を見せる。", "PASS", "取り組む/取組む")
add("d_okurigana", "週末に買い物へ行く予定。", "週末に買物へ行く予定。", "PASS", "買い物/買物")
add("d_okurigana", "来月引っ越す予定だと聞いた。", "来月引越す予定だと聞いた。", "PASS", "引っ越す/引越す")
add("d_okurigana", "じっくり話し合う時間を持つ。", "じっくり話合う時間を持つ。", "PASS", "話し合う/話合う")
add("d_okurigana", "すぐに立ち上がる選手を見た。", "すぐに立上がる選手を見た。", "PASS", "立ち上がる/立上がる")
add("d_okurigana", "まる一か月の休みを取った。", "丸一ヶ月の休みを取った。", "PASS", "まる一か月/丸一ヶ月(実データ抽出)")
# --- (d) NEGATIVE ---
add("d_okurigana", "来月の会議を行います。", "来月の会議を行きません。", "MISMATCH", "行う(肯定)/行かない(否定)、別内容")
add("d_okurigana", "すぐに立ち上がる選手を見た。", "すぐに立ち止まる選手を見た。", "MISMATCH", "立ち上がる/立ち止まる、別の語")
add("d_okurigana", "じっくり話し合う時間を持つ。", "じっくり話し終わる時間を持つ。", "MISMATCH", "話し合う/話し終わる、別の語")
add("d_okurigana", "洗濯しても、しばられず自由になれる感じの匂い。",
    "洗濯しても、縛られる、自由になれる感じの匂い。", "MISMATCH", "しばられず(否定)/縛られる(肯定)、実データ抽出の真内容差")

# --- 数字・助数詞(既存正規化のカバー範囲確認、過去ログ外の新規例) ---
add("numeral_counter", "りんごを三つ買って帰った。", "りんごを3つ買って帰った。", "PASS", "三つ/3つ")
add("numeral_counter", "会議は五回に分けて行う。", "会議は5回に分けて行う。", "PASS", "五回/5回")
add("numeral_counter", "その仕事は十件を超えた。", "その仕事は10件を超えた。", "PASS", "十件/10件")
add("numeral_counter", "六週間かけて完成させた。", "6週間かけて完成させた。", "PASS", "六週間/6週間")
add("numeral_counter", "参加者は八歳から募集する。", "参加者は8歳から募集する。", "PASS", "八歳/8歳")
add("numeral_counter", "休みはまる一か月続いた。", "休みはまる1か月続いた。", "PASS", "一か月/1か月")
add("numeral_counter", "りんごを三つ買って帰った。", "りんごを4つ買って帰った。", "MISMATCH", "数量自体が違う(3/4)")
add("numeral_counter", "その仕事は十件を超えた。", "その仕事は100件を超えた。", "MISMATCH", "数量自体が違う(10/100)")

# --- カタカナ語の長音表記ゆれ ---
add("katakana_choonpu", "新しいコンピューターを使う。", "新しいコンピュータを使う。", "PASS", "コンピューター/コンピュータ")
add("katakana_choonpu", "サーバーが停止したと連絡が来た。", "サーバが停止したと連絡が来た。", "PASS", "サーバー/サーバ")
add("katakana_choonpu", "ユーザーの体験を高める工夫。", "ユーザの体験を高める工夫。", "PASS", "ユーザー/ユーザ")
add("katakana_choonpu", "チームのメンバーを集める。", "チームのメンバを集める。", "PASS", "メンバー/メンバ")
add("katakana_choonpu", "新しいカテゴリーを追加した。", "新しいカテゴリを追加した。", "PASS", "カテゴリー/カテゴリ")
add("katakana_choonpu", "バスのドライバーが待っている。", "バスのドライバが待っている。", "PASS", "ドライバー/ドライバ")
add("katakana_choonpu", "新しいコンピューターを使う。", "新しいコミューターを使う。", "MISMATCH", "コンピューター/コミューター、別の語")
add("katakana_choonpu", "サーバーが停止したと連絡が来た。", "サーブが停止したと連絡が来た。", "MISMATCH", "サーバー/サーブ、別の語")

# --- 句読点・記号 ---
add("punctuation", "素晴らしい結果でした！", "素晴らしい結果でした", "PASS", "感嘆符の有無")
add("punctuation", "パン・牛乳・卵を買う。", "パン牛乳卵を買う。", "PASS", "中点の有無")
add("punctuation", "明日は…晴れるでしょう。", "明日は晴れるでしょう。", "PASS", "三点リーダの有無")
add("punctuation", "会議(午後)に出席する予定。", "会議に出席する予定。", "MISMATCH", "括弧内の情報が脱落(午後という内容が消えている)")

# --- 複数読みの選択誤り(文脈依存の多義漢字、既知の限界カテゴリ) ---
add("multi_reading_ambiguous", "いちにちじゅう家で過ごした。", "一日中家で過ごした。", "PASS", "一日中(いちにちじゅう)")
add("multi_reading_ambiguous", "料理がじょうずな人が多い。", "料理が上手な人が多い。", "PASS", "上手(じょうず)")

# ------------------------------------------------------------
# 実行
# ------------------------------------------------------------

def run_case(item):
    baseline_result, resolver_calls = trial.classify_with_baseline(item["canonical"], item["asr"])
    candidate_result = trial.classify_with_candidate_morph(item["canonical"], item["asr"])

    def summarize(r):
        return {"classification": r.classification, "should_pass": r.should_pass, "reason": r.reason}

    baseline_pass = baseline_result.should_pass
    candidate_pass = candidate_result.should_pass
    expected_pass = (item["expected"] == "PASS")

    return {
        **item,
        "baseline": summarize(baseline_result),
        "baseline_resolver_dry_run_calls": resolver_calls,
        "candidate_morph": summarize(candidate_result),
        "baseline_correct": baseline_pass == expected_pass,
        "candidate_correct": candidate_pass == expected_pass,
        "candidate_fixed_a_baseline_failure": (not (baseline_pass == expected_pass)) and (candidate_pass == expected_pass),
        "candidate_introduced_false_pass": (expected_pass is False) and (candidate_pass is True) and (baseline_pass is False),
        "candidate_broke_a_baseline_pass": (baseline_pass == expected_pass) and (candidate_pass != expected_pass),
    }


def main():
    results = [run_case(item) for item in DATASET]

    by_category = {}
    for r in results:
        by_category.setdefault(r["category"], []).append(r)

    summary = {}
    for cat, items in by_category.items():
        summary[cat] = {
            "n": len(items),
            "baseline_correct": sum(1 for i in items if i["baseline_correct"]),
            "candidate_correct": sum(1 for i in items if i["candidate_correct"]),
            "candidate_fixed": sum(1 for i in items if i["candidate_fixed_a_baseline_failure"]),
            "candidate_false_pass": sum(1 for i in items if i["candidate_introduced_false_pass"]),
            "candidate_broke": sum(1 for i in items if i["candidate_broke_a_baseline_pass"]),
            "baseline_resolver_dry_run_calls_total": sum(i["baseline_resolver_dry_run_calls"] for i in items),
        }

    totals = {
        "n": len(results),
        "baseline_correct": sum(1 for i in results if i["baseline_correct"]),
        "candidate_correct": sum(1 for i in results if i["candidate_correct"]),
        "candidate_fixed": sum(1 for i in results if i["candidate_fixed_a_baseline_failure"]),
        "candidate_false_pass": sum(1 for i in results if i["candidate_introduced_false_pass"]),
        "candidate_broke": sum(1 for i in results if i["candidate_broke_a_baseline_pass"]),
        "baseline_resolver_dry_run_calls_total": sum(i["baseline_resolver_dry_run_calls"] for i in results),
    }

    # Candidate A: 候補存在チェック(offline、LLM不要)
    candidate_a_checks = [
        trial.candidate_a_dry_candidate_check("経", "たつ"),
        trial.candidate_a_dry_candidate_check("行", "おこな"),
        trial.candidate_a_dry_candidate_check("表", "あらわ"),
        trial.candidate_a_dry_candidate_check("頑", "がん"),
        trial.candidate_a_dry_candidate_check("頃", "ころ"),
        trial.candidate_a_dry_candidate_check("後", "あと"),
        trial.candidate_a_dry_candidate_check("一", "いち"),
        trial.candidate_a_dry_candidate_check("聴", "き"),
        trial.candidate_a_dry_candidate_check("逢", "あ"),
        trial.candidate_a_dry_candidate_check("創", "つく"),
    ]

    output = {
        "dataset_size": len(DATASET),
        "results": results,
        "summary_by_category": summary,
        "totals": totals,
        "candidate_a_dry_candidate_checks": candidate_a_checks,
    }

    out_path = sys.argv[1] if len(sys.argv) > 1 else "er011_output/ja_asr_variant_trial_01/results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"dataset_size={len(DATASET)}")
    print(f"totals={totals}")
    for cat, s in summary.items():
        print(f"  {cat}: {s}")
    print(f"candidate_a_dry_candidate_checks={candidate_a_checks}")


if __name__ == "__main__":
    main()
