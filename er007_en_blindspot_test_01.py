# ============================================================
# er007_en_blindspot_test_01.py
# ER-007-EN-ASR-EFFECTIVENESS-AUDIT-01 Part 5-6: English ASR Validatorの
# blind spot実証。実際のNo.4-6 canonical text(short/medium/long)を土台に、
# ASR transcript側へ仮想的な誤りを構成し、実際のProduction Validator
# (classify_asr_match)へ直接通す。新規TTS/ASRは一切呼ばない。
# ============================================================
import json
import sys

sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary_asr


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check(label, canonical, asr_text, expect_pass_forbidden=True):
    r = val.classify_asr_match(canonical, asr_text)
    is_entity_like = secondary_asr.is_entity_like_mismatch(r)
    verdict_ok = (not r.should_pass) if expect_pass_forbidden else r.should_pass
    status = "OK(期待通り)" if verdict_ok else "FAIL(期待に反する)"
    print(f"\n[{label}] {status}")
    print(f"  classification={r.classification} should_pass={r.should_pass} should_retry={r.should_retry}")
    print(f"  reason: {r.reason[:220]}")
    if r.protected.content_word_diffs:
        print(f"  content_word_diffs: {r.protected.content_word_diffs}")
    print(f"  is_entity_like_mismatch: {is_entity_like}")
    return {"label": label, "classification": r.classification, "should_pass": r.should_pass,
            "should_retry": r.should_retry, "is_entity_like": is_entity_like, "verdict_ok": verdict_ok}


# ============================================================
# 実データ: No.4/5/6のcanonical text(short/medium/long)
# ============================================================
# LONG: No.4 B1 full_story_part2(統計密度の高い長文segment、原文)
N4_LONG = (
    "The results showed a clear change in the sales mix. After three months, fruit and vegetable "
    "sales rose by 1.71 standard deviations, equal to about 6,170 portions per store each week. "
    "After six months, the increase reached 2.42 standard deviations, or about 9,820 portions per "
    "store each week.\n\nSnack sales fell by 1.05 standard deviations after three months. That was "
    "about 1,359 fewer portions per store each week. At six months, snack sales were still lower, "
    "but the result was not statistically significant.\n\nThere was also an important limit. Total "
    "sales for the whole store did not change significantly. The new layout appeared to change what "
    "people bought, rather than how much the store sold overall.\n\nA related survey of 150 women "
    "found that fruit and vegetable purchases increased in households using the intervention stores, "
    "while they decreased in comparison households. However, the study did not find a significant "
    "effect on snack purchases."
)
# MEDIUM: No.5 B1 point_one_body(中程度の長さ)
N5_MEDIUM = (
    "Design can make a policy clear without a sign. Some places offer no Wi-Fi, play loud music, "
    "or use less comfortable chairs to discourage work. PTPs choose the opposite: dependable Wi-Fi, "
    "enough power outlets, useful furniture, controlled noise, and daily offers."
)
# SHORT: No.6 point_one_heading相当(短いsegment)
N6_SHORT = "A small action in a powerless wait"


def run():
    results = []

    print("=" * 70)
    print("5-1. Content word置換(意味のある語の入れ替え)")
    print("=" * 70)
    results.append(check(
        "5-1a increase->decrease(No.4 LONG中間)",
        N4_LONG,
        N4_LONG.replace("sales rose by 1.71", "sales fell by 1.71").replace(
            "reached 2.42", "dropped to 2.42")))
    results.append(check(
        "5-1b customers->retailers相当(No.5 MEDIUM、'places'->'chains')",
        N5_MEDIUM,
        N5_MEDIUM.replace("Some places offer no Wi-Fi", "Some chains offer no Wi-Fi")))

    print("\n" + "=" * 70)
    print("5-2. 数字誤り")
    print("=" * 70)
    results.append(check(
        "5-2a 25->15相当(No.4 LONG、150->140 women)",
        N4_LONG, N4_LONG.replace("150 women", "140 women")))
    results.append(check(
        "5-2b 70%->17%相当(standard deviations値の変更、1.71->1.17)",
        N4_LONG, N4_LONG.replace("rose by 1.71 standard deviations", "rose by 1.17 standard deviations")))

    print("\n" + "=" * 70)
    print("5-3. 否定反転")
    print("=" * 70)
    results.append(check(
        "5-3a did not->did(No.4 LONG、'did not find a significant effect'->'did find a significant effect')",
        N4_LONG,
        N4_LONG.replace("did not find a significant effect", "did find a significant effect")))
    results.append(check(
        "5-3b no clear effect反転相当(No.4 LONG、'did not change significantly'->'did change significantly')",
        N4_LONG,
        N4_LONG.replace("did not change significantly", "did change significantly")))

    print("\n" + "=" * 70)
    print("5-4. 文中フレーズの脱落(長いsegmentの中間から1文削除)")
    print("=" * 70)
    n4_dropped = N4_LONG.replace(
        "There was also an important limit. Total sales for the whole store did not change "
        "significantly. The new layout appeared to change what people bought, rather than how "
        "much the store sold overall.\n\n", "")
    results.append(check("5-4 中間の1段落(3文)を丸ごと削除(No.4 LONG)", N4_LONG, n4_dropped))

    print("\n" + "=" * 70)
    print("5-5. 文中フレーズの追加")
    print("=" * 70)
    n4_added = N4_LONG.replace(
        "The new layout appeared to change what people bought, rather than how much the store sold overall.",
        "The new layout appeared to change what people bought, rather than how much the store sold "
        "overall. Experts say this could double within a year.")
    results.append(check("5-5 canonicalにない一文を中間へ追加(No.4 LONG)", N4_LONG, n4_added))

    print("\n" + "=" * 70)
    print("5-6. 文頭・文末のみ保持、中間を大きく変更(対照テスト)")
    print("=" * 70)
    n4_words = N4_LONG.split()
    prefix = " ".join(n4_words[:6])
    suffix = " ".join(n4_words[-6:])
    fabricated_middle = ("Researchers instead report that customer satisfaction dropped sharply "
                          "and several stores closed early due to unrelated staffing shortages "
                          "unconnected to any layout change")
    n4_prefix_suffix_only = f"{prefix} {fabricated_middle} {suffix}"
    results.append(check("5-6 文頭6語+文末6語のみ一致、中間は無関係な内容に総入れ替え(No.4 LONG)",
                          N4_LONG, n4_prefix_suffix_only))

    print("\n" + "=" * 70)
    print("5-7. 固有名詞orthographic uncertainty(Sweeny/Ottoni系、entity-like判定確認)")
    print("=" * 70)
    sweeny_canonical = ("A 2025 longitudinal study by Howell and Sweeny, published in *Emotion*, "
                         "followed three groups over periods ranging from several weeks to several months.")
    results.append(check(
        "5-7a Sweeny->Sweeney(ASR表記ゆれ、entity-likeでCascade対象になるべき)",
        sweeny_canonical, sweeny_canonical.replace("Sweeny", "Sweeney"),
        expect_pass_forbidden=True))  # should_pass=Falseだが、is_entity_like=Trueであるべき

    ottoni_canonical = "Ottoni and colleagues published a study in 2016."
    results.append(check(
        "5-7b Ottoni->A Tony(実際に観測されたASR誤認識パターン、entity-like)",
        ottoni_canonical, "A Tony and colleagues published a study in 2016.",
        expect_pass_forbidden=True))

    print("\n" + "=" * 70)
    print("5-8. 真の固有名詞違い(orthographic uncertaintyとして誤って救済されないこと)")
    print("=" * 70)
    results.append(check(
        "5-8a Sweeny(canonical)->実在の別人名Johnson(全く別の実在姓)",
        sweeny_canonical, sweeny_canonical.replace("Sweeny", "Johnson"),
        expect_pass_forbidden=True))
    results.append(check(
        "5-8b Ottoni(canonical)->実在の別姓Martinez",
        ottoni_canonical, "Martinez and colleagues published a study in 2016.",
        expect_pass_forbidden=True))
    boavida_canonical = "A separate review by Boavida and colleagues in 2023 examined 28 articles."
    results.append(check(
        "5-8c Boavida(canonical)->実在の別都市名Barcelona(地名文脈で置換、地理的に別物)",
        boavida_canonical, boavida_canonical.replace("Boavida", "Barcelona"),
        expect_pass_forbidden=True))

    return results


def run_length_comparison():
    """Part 6: 同じ種類の誤り(content word置換)をshort/medium/longへ入れ、
    判定の希釈が起きないか確認する。"""
    print("\n" + "=" * 70)
    print("Part 6: Segment長による性能差(同一種類の誤りをshort/medium/longへ)")
    print("=" * 70)
    results = []
    results.append(check(
        "6-short: N6_SHORT 'powerless'->'powerful'(反対語、短いsegment)",
        N6_SHORT, N6_SHORT.replace("powerless", "powerful")))
    results.append(check(
        "6-medium: N5_MEDIUM 'discourage'->'encourage'(反対語、中程度segment)",
        N5_MEDIUM, N5_MEDIUM.replace("discourage work", "encourage work")))
    results.append(check(
        "6-long: N4_LONG 'increased'->'decreased'(反対語、長いsegment、全体に対する語数比率は最小)",
        N4_LONG, N4_LONG.replace("purchases increased in households", "purchases decreased in households")))
    return results


if __name__ == "__main__":
    all_results = run()
    length_results = run_length_comparison()
    all_results += length_results

    n_ok = sum(1 for r in all_results if r["verdict_ok"])
    print(f"\n\n{'='*70}\nSUMMARY: {n_ok}/{len(all_results)} テストが期待通りの結果")
    for r in all_results:
        mark = "OK" if r["verdict_ok"] else "**FAIL**"
        print(f"  [{mark}] {r['label']}: classification={r['classification']} should_pass={r['should_pass']} entity_like={r['is_entity_like']}")

    with open("er006_output/pool_pilot_01/evidence_density_ab_01/en_blindspot_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print("\nEN_BLINDSPOT_TEST_DONE")
