# ============================================================
# er018_fiction_real_story_and_true_crime_trial_01_test_01.py
# 管理ID: FICTION-REAL-STORY-AND-TRUE-CRIME-TRIAL-01
# ============================================================
# オフライン(API呼び出し無し)でGate判定関数・語数チェック・SEEDS構造・
# True Crime用テンプレート分岐を確認するテスト。
#
# 実行方法(root直下):
#   .venv/Scripts/python.exe er018_fiction_real_story_and_true_crime_trial_01_test_01.py
# ============================================================
from __future__ import annotations

import er018_fiction_real_story_and_true_crime_trial_01 as target


def test_seeds_have_two_entries_real_and_true_crime():
    assert len(target.SEEDS) == 2
    keys = {s["key"] for s in target.SEEDS}
    assert keys == {"real_story_nellie_bly", "true_crime_eugene_aram"}


def test_all_seed_specs_have_required_keys():
    for seed_spec in target.SEEDS:
        missing = target.validate_seed_spec(seed_spec)
        assert missing == [], f"{seed_spec.get('key')}: 欠落キー={missing}"


def test_word_count_gate_280_420():
    assert target.check_word_count_ok(280) is True
    assert target.check_word_count_ok(420) is True
    assert target.check_word_count_ok(350) is True
    assert target.check_word_count_ok(279) is False
    assert target.check_word_count_ok(421) is False


def test_true_crime_uses_real_names_template_and_fiction_uses_role_only_template():
    fake_seed = {
        "seed_elements": ["element A", "element B"],
        "conversion_plan": "convert plan text",
    }
    real_story_prompt = target.build_story_prompt(fake_seed, "real_story_nellie_bly")
    true_crime_prompt = target.build_story_prompt(fake_seed, "true_crime_eugene_aram")

    # Fiction系(real_story)は「主人公のみ固有名」ルールの文言を含む
    assert "Only the main character (the protagonist) may be given a personal" in (
        real_story_prompt
    )
    # True Crimeは実名保持を明示する専用セクションを含み、上記の文言は含まない
    assert "Names -- keep the real ones" in true_crime_prompt
    assert "Only the main character (the protagonist) may be given a personal" not in (
        true_crime_prompt
    )
    assert "use the real names of the people involved exactly as given" in (
        true_crime_prompt
    )


def test_true_crime_keys_set_matches_seeds():
    # TRUE_CRIME_KEYSに含まれるkeyがSEEDSに実在すること(タイプミス防止)
    seed_keys = {s["key"] for s in target.SEEDS}
    assert target.TRUE_CRIME_KEYS.issubset(seed_keys)
    assert "true_crime_eugene_aram" in target.TRUE_CRIME_KEYS
    assert "real_story_nellie_bly" not in target.TRUE_CRIME_KEYS


def run_all():
    tests = [
        test_seeds_have_two_entries_real_and_true_crime,
        test_all_seed_specs_have_required_keys,
        test_word_count_gate_280_420,
        test_true_crime_uses_real_names_template_and_fiction_uses_role_only_template,
        test_true_crime_keys_set_matches_seeds,
    ]
    failures = []
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except AssertionError as exc:
            failures.append((t.__name__, str(exc)))
            print(f"[FAIL] {t.__name__}: {exc}")
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed.")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    run_all()
