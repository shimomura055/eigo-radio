# ============================================================
# er007_ja_asr_validator_01_test.py
# ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01 Part D:
# Positive/Negative fixture(実データ+構成データ)。
# ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part C: 濁点/半濁点の有無だけが
# 異なる読みゆれ(phonetic_uncertain)のPositive/境界fixtureを追加。
# ============================================================
from __future__ import annotations

import sys
sys.path.insert(0, ".")
import er007_ja_asr_validator_01 as javal

# ------------------------------------------------------------
# POSITIVE: 実データ(No.1系Production、旧方式でverified=trueだった実例)
# ------------------------------------------------------------
POSITIVE_FIXTURES = [
    {"name": "完全一致(句読点のみ差、実データpool_benches japanese_title)",
     "canonical": "公共のベンチ、なぜ今見直されているのか",
     "asr": "公共のベンチ、なぜ今見直されているのか？"},
    {"name": "漢字/ひらがな表記ゆれ(いす/椅子、実データpreview)",
     "canonical": "街にあるベンチは、ただのいすなのでしょうか。",
     "asr": "街にあるベンチは、ただの椅子なのでしょうか。"},
    {"name": "読点の有無(実データcomment_1)",
     "canonical": "高齢者にとって、ベンチがどんな役割を持つのかに注目して聞いてください。",
     "asr": "高齢者にとってベンチがどんな役割を持つのかに注目して聞いてください。"},
    {"name": "同音異字(後半/公判、実データpool_benches_pilot_02 comment_2。"
             "旧方式でverified=trueだった実例。「こうはん」で完全同音)",
     "canonical": "では後半では、公共の場所は通り過ぎるためだけでなく",
     "asr": "では、公判では、公共の場所は通り過ぎるためだけでなく"},
    {"name": "誰/だれの表記ゆれ(実データcomment_3)",
     "canonical": "人とのつながりや、だれがその場所にいられるかにも関係する",
     "asr": "人とのつながりや誰がその場所にいられるかにも関係する"},
    {"name": "様々/さまざまの表記ゆれ(実データpreview)",
     "canonical": "さまざまな意見があります",
     "asr": "様々な意見があります"},
    {"name": "得ます/えますの表記ゆれ(実データcomment_3、pool_benches_luna)",
     "canonical": "立ち止まって過ごす場所にもなり得ます",
     "asr": "立ち止まって過ごす場所にもなりえます"},
    {"name": "安全な数字表記差(全角/半角)",
     "canonical": "28件の記事を分析した",
     "asr": "２８件の記事を分析した"},
    {"name": "軽微なASR句読点挿入位置ゆれ(実データcomment_4)",
     "canonical": "ここまで、公共の場所で生まれる小さな交流と、ベンチの形だけでなく実際の使われ方を確かめることについて聞きました。",
     "asr": "ここまで公共の場所で生まれる小さな交流と、ベンチの形だけでなく、実際の使われ方を確かめることについて聞きました。"},
    {"name": "助数詞「つ」直前の漢数字/算用数字ゆれ(二つ/2つ、"
             "ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07、"
             "実データNo.7 A2 comment_4のASR不一致に由来)",
     "canonical": "では、この二つの動きについて、英語のまとめを聞いてみましょう。",
     "asr": "では、この2つの動きについて、英語のまとめを聞いてみましょう。"},
]

# ------------------------------------------------------------
# NEGATIVE: 前タスクのBlind Spot 6カテゴリ+追加必須ケース
# ------------------------------------------------------------
BASE = ("解約を難しくする壁は、「スラッジ」と考えられます。では、FTCがこの問題を変えるために"
        "作ったルールは、その後どうなったのでしょうか。")

NEGATIVE_FIXTURES = [
    {"name": "1文字/1音の誤り(実例: やめにくくする→やめにくかする)",
     "canonical": "定期サービスをやめにくくする仕組み",
     "asr": "定期サービスをやめにくかする仕組み"},
    {"name": "FTC->FCC(略語の置換、意味が変わる)",
     "canonical": BASE, "asr": BASE.replace("FTC", "FCC")},
    {"name": "数字変更(150->140)",
     "canonical": "150人の女性を対象とした調査",
     "asr": "140人の女性を対象とした調査"},
    {"name": "日付変更(2020年->2021年)",
     "canonical": "2020年の大統領選挙の結果を待つ有権者",
     "asr": "2021年の大統領選挙の結果を待つ有権者"},
    {"name": "否定反転(変えるために->変えないために)",
     "canonical": BASE, "asr": BASE.replace("変えるために", "変えないために")},
    {"name": "content word置換(増加->減少)",
     "canonical": "果物と野菜の購入が増加しました",
     "asr": "果物と野菜の購入が減少しました"},
    {"name": "content word置換(増えた->減った、タスク仕様の明示ケース)",
     "canonical": "利用者の数が増えたという結果でした",
     "asr": "利用者の数が減ったという結果でした"},
    {"name": "数字変更(15->50、タスク仕様の明示ケース)",
     "canonical": "アンケートには15人が回答しました",
     "asr": "アンケートには50人が回答しました"},
    {"name": "phrase omission(中間の一文を削除)",
     "canonical": "このニュースは、定期サービスをやめにくくする仕組みと、それを変えようとしたルールが裁判で取り消された流れを伝えています。次は、解約の負担を手続きの最初から最後まで見ていきます。",
     "asr": "このニュースは、定期サービスをやめにくくする仕組みを伝えています。次は、解約の負担を手続きの最初から最後まで見ていきます。"},
    {"name": "phrase addition(無関係な一文を追加)",
     "canonical": "解約を難しくする壁は、「スラッジ」と考えられます。",
     "asr": "解約を難しくする壁は、「スラッジ」と考えられます。これは深刻な社会問題です。"},
    {"name": "long segment中間部変更(comment_3実データ土台、中間のFTC関連部分を別内容に差し替え)",
     "canonical": "このニュースは、定期サービスをやめにくくする仕組みと、それを変えようとしたルールが裁判で取り消された流れを伝えています。次は、解約の負担を手続きの最初から最後まで見ていきます。そして、研究者が複雑な解約の流れをどう調べたのかを聞きます。",
     "asr": "このニュースは、定期サービスをやめにくくする仕組みと、それを変えようとしたルールが裁判で取り消された流れを伝えています。次は、業界全体の売り上げについて詳しく見ていきます。そして、研究者が複雑な解約の流れをどう調べたのかを聞きます。"},
    {"name": "文頭・文末だけ一致して中間が異なる(対照テスト)",
     "canonical": "このニュースは、定期サービスをやめにくくする仕組みについて伝えています。研究者が複雑な解約の流れをどう調べたのかを聞きます。",
     "asr": "このニュースは、まったく別の話題である気候変動と再生可能エネルギーの動向について伝えています。研究者が複雑な解約の流れをどう調べたのかを聞きます。"},
    {"name": "助数詞つき漢数字の数量違い(二つ->3つ、"
             "ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07、"
             "同値正規化が数量そのものの違いまで許容しないことの確認)",
     "canonical": "では、この二つの動きについて、英語のまとめを聞いてみましょう。",
     "asr": "では、この3つの動きについて、英語のまとめを聞いてみましょう。"},
    {"name": "「二十」は助数詞「つ」正規化の対象外(二十->2、"
             "ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07、"
             "一般化しすぎていないことの確認)",
     "canonical": "参加者は二十人ほど集まりました。",
     "asr": "参加者は2人ほど集まりました。"},
    {"name": "助数詞が異なると同値扱いしない(二回->2つ、"
             "ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07、"
             "回と つ を混同しないことの確認)",
     "canonical": "この点については二回説明しました。",
     "asr": "この点については2つ説明しました。"},
]

# ------------------------------------------------------------
# Entity-like(固有名詞/略語のASR表記ゆれ、Cascade対象になるべき)
# ------------------------------------------------------------
ENTITY_LIKE_FIXTURES = [
    {"name": "カタカナ固有名詞のASR表記ゆれ(スラッジ->スラッシ)",
     "canonical": "解約を難しくする壁は、「スラッジ」と考えられます。",
     "asr": "解約を難しくする壁は、「スラッシ」と考えられます。"},
]

# ------------------------------------------------------------
# PHONETIC_UNCERTAIN(濁点/半濁点の有無だけが異なる読みゆれ、Cascade対象に
# なるべき。ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part B)
# ------------------------------------------------------------
PHONETIC_UNCERTAIN_FIXTURES = [
    {"name": "頃/ころ(実データ、verify_ja_cascade_production_on.pyのsmoke testで実際に発生した実例。"
             "kakasiが「頃」を文脈なしで連濁形「ごろ」と読み、canonical側の「ころ」の読みと一致しなかった"
             "ため旧実装ではTRUE_CONTENT_MISMATCH→即TTS retryになっていた)",
     "canonical": ("今回のニュースは、結果を待っているときに、なぜ同じページを何度も開いてしまうのかという話です。"
                   "結果がまだ分からない場面では、情報を確かめる行動が気になってくることがあります。"
                   "研究を通して、こうした行動がどのような場面で起きやすいのかを見ていきます。"
                   "聞き終わるころには、待っている間に確認したくなる理由について、どんなことが分かっているのかが分かります。"),
     "asr": ("今回のニュースは、結果を待っているときに、なぜ同じページを何度も開いてしまうのか、という話です。"
             "結果がまだわからない場面では、情報を確かめる行動が気になってくることがあります。"
             "研究を通して、こうした行動がどのような場面で起きやすいのかを見ていきます。"
             "聞き終わる頃には、待っている間に確認したくなる理由について、どんなことがわかっているのかがわかります。")},
    {"name": "頃/ごろ(逆方向。kakasiの「頃」既定読みが元々「ごろ」のため、この向きは新規のvoicing"
             "許容チェックを使わずとも既存のreading_equal(完全一致)でPHONETIC_MATCHになる確認用ケース)",
     "canonical": "宿題が終わる頃に電話します。",
     "asr": "宿題が終わるごろに電話します。"},
]

# ------------------------------------------------------------
# PHONETIC_UNCERTAIN境界ケース(濁点許容チェックの一般性・安全性を確認する
# 目的別の合成テスト。実在の「頃」に依存しないメカニズム自体の検証)
# ------------------------------------------------------------
def check_voicing_mechanism_generalization():
    """_reading_equal_allowing_voicingが「頃」という文字列へのハードコード
    ではなく、清音化(NFD分解+結合文字除去)による一般的な比較であることを、
    「頃」を一切含まない合成ペアで直接確認する(か/が、さ/ざ、た/だ、は/ば、
    は/ぱの5行)。"""
    pairs_should_be_voicing_equal = [
        ("かける", "がける"), ("さくら", "ざくら"), ("たいこ", "だいこ"),
        ("はんこ", "ばんこ"), ("はんこ", "ぱんこ"),
    ]
    failures = []
    for a, b in pairs_should_be_voicing_equal:
        ok = javal._reading_equal_allowing_voicing(a, b)
        status = "OK" if ok else "FAIL"
        print(f"[{status}] _reading_equal_allowing_voicing({a!r}, {b!r}) = {ok} (期待: True)")
        if not ok:
            failures.append(f"{a}/{b}")
    # 清音化しても一致しない(=無関係な語)場合はFalseのままである安全側の確認
    unrelated_pairs = [("ねこ", "いぬ"), ("かける", "とめる")]
    for a, b in unrelated_pairs:
        ok = javal._reading_equal_allowing_voicing(a, b)
        status = "OK" if not ok else "FAIL"
        print(f"[{status}] _reading_equal_allowing_voicing({a!r}, {b!r}) = {ok} (期待: False)")
        if ok:
            failures.append(f"{a}/{b}(無関係語なのにTrueになった)")
    return failures


# ------------------------------------------------------------
# PHONETIC_UNCERTAINの既知のトレードオフ(安全側であることの確認用。
# 「意味は誤PASSしない(should_pass=Falseのまま)が、Cascadeへ余分に
# 回ることがある」既知の限界を記録する。STOP条件[真の内容誤りの誤PASS]
# には該当しないことをここで直接確認する)
# ------------------------------------------------------------
KNOWN_TRADEOFF_FIXTURES = [
    {"name": "柿/鍵(清音化後にたまたま一致する、意味の異なる実在語同士。"
             "should_pass=Falseのまま(誤PASSしない)が、TRUE_CONTENT_MISMATCHではなく"
             "ASR_VALIDATION_UNCERTAIN(Cascade対象)になる既知のトレードオフ)",
     "canonical": "テーブルの上には柿が置いてありました。",
     "asr": "テーブルの上には鍵が置いてありました。"},
]

# ------------------------------------------------------------
# PHONETIC_UNCERTAINが過剰適用されない境界確認(「漢字なら全部Cascade」に
# なっていないことの確認。月の「つき」(名詞)/「がつ」(暦月の接尾)は
# 清音化しても一致しない=別のモーラ構成のため、除外されて当然)
# ------------------------------------------------------------
NOT_PHONETIC_UNCERTAIN_FIXTURES = [
    {"name": "月(つき/がつ、清音化しても一致しない別読みのため対象外。"
             "「漢字の異読みなら何でもCascade」になっていないことの確認)",
     "canonical": "夜空に浮かぶ丸いつきを見上げた。",
     "asr": "夜空に浮かぶ丸い月を見上げた。"},
]


def run_group(label, fixtures, expect_should_pass):
    print(f"\n=== {label} ===")
    failures = []
    for fx in fixtures:
        r = javal.classify_ja_asr_match(fx["canonical"], fx["asr"])
        ok = (r.should_pass == expect_should_pass) if expect_should_pass is not None else True
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {fx['name']}: classification={r.classification} should_pass={r.should_pass} "
              f"ratio={r.similarity_ratio:.3f}")
        if r.protected.content_diffs:
            print(f"       content_diffs={r.protected.content_diffs}")
        if r.protected.number_mismatches or r.protected.negation_mismatches:
            print(f"       numbers={r.protected.number_mismatches} negation={r.protected.negation_mismatches}")
        if not ok:
            failures.append(fx["name"])
    return failures


if __name__ == "__main__":
    all_failures = []
    all_failures += run_group("POSITIVE fixtures (should_pass=True)", POSITIVE_FIXTURES, True)
    all_failures += run_group("NEGATIVE fixtures (should_pass=False, TRUE_CONTENT_MISMATCH)", NEGATIVE_FIXTURES, False)

    print("\n=== ENTITY_LIKE fixtures (should_pass=False だが entity_like=True で Cascade対象) ===")
    for fx in ENTITY_LIKE_FIXTURES:
        r = javal.classify_ja_asr_match(fx["canonical"], fx["asr"])
        is_entity = javal.is_entity_like_mismatch_ja(r)
        ok = (r.should_pass is False) and is_entity
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {fx['name']}: classification={r.classification} should_pass={r.should_pass} "
              f"is_entity_like={is_entity}")
        if not ok:
            all_failures.append(fx["name"])

    print("\n=== PHONETIC_UNCERTAIN fixtures (期待: TRUE_CONTENT_MISMATCHにならない=即TTS retryしない。"
          "should_pass=True[即PASS]/False[Cascade対象]のどちらも許容し、TTS retryに落ちないことだけを確認する) ===")
    for fx in PHONETIC_UNCERTAIN_FIXTURES:
        r = javal.classify_ja_asr_match(fx["canonical"], fx["asr"])
        ok = r.classification != "TRUE_CONTENT_MISMATCH"
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {fx['name']}: classification={r.classification} should_pass={r.should_pass}")
        if r.protected.content_diffs:
            print(f"       content_diffs={r.protected.content_diffs}")
        if not ok:
            all_failures.append(fx["name"])

    print("\n=== voicing許容メカニズムの一般性確認(「頃」専用ルールではないことの直接検証) ===")
    all_failures += check_voicing_mechanism_generalization()

    print("\n=== KNOWN_TRADEOFF fixtures (should_pass=Falseのまま=誤PASSしないことの確認。"
          "TRUE_CONTENT_MISMATCHにはならずCascadeへ回る既知のトレードオフ) ===")
    for fx in KNOWN_TRADEOFF_FIXTURES:
        r = javal.classify_ja_asr_match(fx["canonical"], fx["asr"])
        ok = r.should_pass is False  # 誤PASSしないことだけを厳格に確認する(分類先は問わない)
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {fx['name']}: classification={r.classification} should_pass={r.should_pass}")
        if not ok:
            all_failures.append(fx["name"])

    print("\n=== NOT_PHONETIC_UNCERTAIN fixtures (「漢字なら全部Cascade」になっていないことの確認) ===")
    for fx in NOT_PHONETIC_UNCERTAIN_FIXTURES:
        r = javal.classify_ja_asr_match(fx["canonical"], fx["asr"])
        ok = r.classification == "TRUE_CONTENT_MISMATCH"
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {fx['name']}: classification={r.classification} should_pass={r.should_pass}")
        if r.protected.content_diffs:
            print(f"       content_diffs={r.protected.content_diffs}")
        if not ok:
            all_failures.append(fx["name"])

    total = (len(POSITIVE_FIXTURES) + len(NEGATIVE_FIXTURES) + len(ENTITY_LIKE_FIXTURES)
             + len(PHONETIC_UNCERTAIN_FIXTURES) + len(KNOWN_TRADEOFF_FIXTURES) + len(NOT_PHONETIC_UNCERTAIN_FIXTURES))
    if all_failures:
        print(f"\n{len(all_failures)}件のfixture/checkが期待通りに分類されなかった: {all_failures}")
    else:
        print(f"\nOK: 全{total}件のfixture + voicingメカニズム一般性確認が期待通りに分類された")
