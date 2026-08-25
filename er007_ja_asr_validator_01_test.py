# ============================================================
# er007_ja_asr_validator_01_test.py
# ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01 Part D:
# Positive/Negative fixture(実データ+構成データ)。
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
]

# ------------------------------------------------------------
# Entity-like(固有名詞/略語のASR表記ゆれ、Cascade対象になるべき)
# ------------------------------------------------------------
ENTITY_LIKE_FIXTURES = [
    {"name": "カタカナ固有名詞のASR表記ゆれ(スラッジ->スラッシ)",
     "canonical": "解約を難しくする壁は、「スラッジ」と考えられます。",
     "asr": "解約を難しくする壁は、「スラッシ」と考えられます。"},
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

    if all_failures:
        print(f"\n{len(all_failures)}件のfixtureが期待通りに分類されなかった: {all_failures}")
    else:
        print(f"\nOK: 全{len(POSITIVE_FIXTURES)+len(NEGATIVE_FIXTURES)+len(ENTITY_LIKE_FIXTURES)}件のfixtureが期待通りに分類された")
