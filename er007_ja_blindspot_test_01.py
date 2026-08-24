# ============================================================
# er007_ja_blindspot_test_01.py
# ER-007-EVIDENCE-WORDCOUNT-JA-ASR-EFFECTIVENESS-AUDIT-01 Part B-5:
# 長い日本語segmentのValidator(prefix substring + length)が、実際の
# canonical textに対する各種の意味的な誤り(1文字誤り/語の置換/数字誤り/
# 否定脱落/フレーズ脱落/フレーズ追加)を検知できるかを検証する。
# 新規TTS/ASRは一切呼ばない(既存の検証関数ロジックへ、構成した仮想
# ASR textを直接通すのみ)。
# ============================================================
import sys
sys.path.insert(0, ".")
import er003_v1_n3_01_tts_generate as tts_gen  # expected_substring_ja


def verify_ja_long_segment(canonical_text: str, asr_text: str, max_extra_chars: int = 40) -> dict:
    """A2長文Japanese segment(generate_narration_snippet_verified_strict
    のja分岐、および事実上ASR_UNCERTAINで終わるphonetic fallback込み)が
    実際に行っている判定をそのまま再現する。"""
    expected_substring = tts_gen.expected_substring_ja(canonical_text)
    max_len = len(canonical_text) + max_extra_chars
    substring_ok = expected_substring.lower() in asr_text.lower()
    length_ok = len(asr_text) <= max_len
    verified = substring_ok and length_ok
    # phonetic fallback: canonical_text > 30文字なら常にASR_UNCERTAIN(no-op)
    phonetic_would_help = len(canonical_text) <= 30
    return {
        "expected_substring": expected_substring, "substring_ok": substring_ok,
        "length_ok": length_ok, "asr_len": len(asr_text), "max_len": max_len,
        "verified": verified, "phonetic_fallback_could_help": phonetic_would_help,
        "FINAL_CAUGHT": verified is False,  # PASSしてしまう=誤りを見逃す
    }


# comment_2(66文字、A2/Subscriptions実データ)を土台にする
BASE = ("解約を難しくする壁は、「スラッジ」と考えられます。では、FTCがこの問題を変えるために"
        "作ったルールは、その後どうなったのでしょうか。")

CASES = [
    ("1文字/1音の誤り(「スラッジ」→「スラッシ」)", BASE.replace("スラッジ", "スラッシ")),
    ("語の置換(「FTC」→「FCC」)", BASE.replace("FTC", "FCC")),
    ("数字の誤り(該当なし→比較のため「2024年に」を追加した誤り変種で代替: 年が別の年に)",
     BASE.replace("その後どうなったのでしょうか", "2025年にどうなったのでしょうか")),
    ("否定の脱落(「変えるために」→「変えないために」への否定追加、逆方向の脱落も同様に検知漏れになりうることを示す変種)",
     BASE.replace("変えるために", "変えないために")),
    ("文中フレーズの脱落(「その後どうなったのでしょうか」を削除)",
     BASE.replace("は、その後どうなったのでしょうか。", "は。")),
    ("文中フレーズの追加(無関係な一文を追加)",
     BASE.replace("考えられます。", "考えられます。これは深刻な問題です。")),
    ("実例そのもの: 「やめにくくする」→「やめにくかする」(comment_3実データより)",
     None),  # 下で別途処理
]

# 実際に本番で発生したcomment_3の実例を追加
COMMENT_3_CANONICAL = (
    "このニュースは、定期サービスをやめにくくする仕組みと、それを変えようとした"
    "ルールが裁判で取り消された流れを伝えています。次は、解約の負担を手続きの"
    "最初から最後まで見ていきます。そして、研究者が複雑な解約の流れをどう"
    "調べたのかを聞きます。"
)
COMMENT_3_ASR_ACTUAL_FAILURE = (
    "このニュースは、定期サービスをやめにくかする仕組みと、それを変えようとした"
    "ルールが裁判で取り消された流れを伝えています。次は解約の負担を手続きの"
    "最初から最後まで見ていきます。そして、研究者が複雑な解約の流れをどう"
    "調べたのかを聞きます。"
)

if __name__ == "__main__":
    print("=== BASE(comment_2実データ)を使った6カテゴリ検証 ===")
    for label, variant in CASES[:-1]:
        r = verify_ja_long_segment(BASE, variant)
        status = "見逃す(誤ってPASS)" if r["verified"] else "検知(PASSしない)"
        print(f"\n[{label}]")
        print(f"  variant: {variant!r}")
        print(f"  expected_substring: {r['expected_substring']!r} substring_ok={r['substring_ok']} "
              f"length_ok={r['length_ok']} (asr_len={r['asr_len']} vs max_len={r['max_len']})")
        print(f"  => {status}")

    print("\n=== 実例: comment_3の実際の失敗ケース(「やめにくくする」→「やめにくかする」) ===")
    r = verify_ja_long_segment(COMMENT_3_CANONICAL, COMMENT_3_ASR_ACTUAL_FAILURE)
    status = "見逃す(誤ってPASS)" if r["verified"] else "検知(PASSしない)"
    print(f"  expected_substring: {r['expected_substring']!r} substring_ok={r['substring_ok']} "
          f"length_ok={r['length_ok']} (asr_len={r['asr_len']} vs max_len={r['max_len']})")
    print(f"  => {status}")
    print(f"  (実際の本番ログでもverified=True, asr_verified=trueとして採用されていたことは前タスクで確認済み)")
