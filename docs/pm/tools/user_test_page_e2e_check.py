"""user_test_page_e2e_check.py

ユーザー試聴ページ(unified.html経由)の表示フォーマット恒久ルールを
機械的にDOM assertionとして検証する再利用可能なE2Eチェッカー。

管理ID: USER-TEST-REVIEW-PAGE-FORMAT-RULE-01(2026-09-17新設)。
PM_GOVERNANCE.md 2節Gate 7補足(n)「ユーザー試聴ページ表示フォーマット」の
恒久チェッカーとして参照される。

検証項目(5項目、1つでもFAILならそのURLはstatus=FAILとして扱う):
  (i)   Key Phrases領域に `English:`/`英語:`/`EN:`/`日本語:`/`日本語gloss:`/
        `JA:` 等のラベル文字列が残っていないこと
  (ii)  Key Phraseが英語列・日本語列の2列形式(kpitem要素数>0かつ
        各itemが英語相当のb要素+日本語相当のspan要素を持つ)であること
  (iii) ヘッダー(eyebrow)にA2/B1ではなくStandard/Advancedが表示されて
        いること(A2/B1の単独表示が残っていないこと)
  (iv)  Playが実際に開始し、一定時間後にcurrentTimeが進んでいること
  (v)   script(Full Script/Full Story)・Key Phrases・Comment要素が
        正常に表示されていること

既存の受入判定(Gate 7 (a)〜(m)・13項目監査)を置き換えるものではなく、
これらに加えて満たすべき追加要件の機械化である。

使い方:
  python docs/pm/tools/user_test_page_e2e_check.py \
      --urls-file <name<TAB>url を1行ずつ書いたファイル> \
      --out <結果JSON出力先> \
      [--screenshot-dir <スクリーンショット保存先ディレクトリ>] \
      [--play-wait-seconds 4]

urls-fileの各行は `name<TAB>url` 形式(nameは結果キー・screenshotファイル名に
使う識別子、url未指定の行・空行・#始まりはスキップ)。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

LABEL_RE = r"^(English|英語|EN|日本語|日本語gloss|JA)\s*[:：]"


def parse_urls_file(path: str) -> list[tuple[str, str]]:
    items = []
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" in line:
            name, url = line.split("\t", 1)
        elif " " in line:
            name, url = line.split(" ", 1)
        else:
            name, url = line, line
        name, url = name.strip(), url.strip()
        if name and url:
            items.append((name, url))
    return items


def check_one(page, name: str, url: str, screenshot_dir: str | None,
              play_wait_seconds: float) -> dict:
    result: dict = {"name": name, "url": url, "checks": {}, "reasons": []}
    console_errors: list[str] = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    try:
        page.goto(url, wait_until="load", timeout=30000)
        page.wait_for_selector("#content .card", timeout=15000)
    except Exception as e:  # noqa: BLE001
        result["status"] = "FAIL"
        result["reasons"].append(f"page load/content待機に失敗: {e}")
        return result

    # (iii) ヘッダー表示
    eyebrow = page.eval_on_selector("#eyebrow", "el => el.textContent") or ""
    has_standard_or_advanced = bool(re.search(r"Standard|Advanced", eyebrow))
    has_bare_level = bool(re.search(r"\bA2\b|\bB1B?\b", eyebrow))
    header_ok = has_standard_or_advanced and not has_bare_level
    result["checks"]["header_standard_advanced"] = {
        "eyebrow_text": eyebrow, "pass": header_ok,
    }
    if not header_ok:
        result["reasons"].append(f"ヘッダーがStandard/Advanced表示になっていない: {eyebrow!r}")

    # Key Phrases領域
    kp_items = page.eval_on_selector_all(
        ".kpitem",
        "els => els.map(el => ({b: el.querySelector('b')?.textContent || '', "
        "span: el.querySelector('span')?.textContent || ''}))",
    )
    kp_count = len(kp_items)
    label_re = re.compile(LABEL_RE, re.IGNORECASE)
    label_hits = [
        item for item in kp_items
        if label_re.search(item["b"].strip()) or label_re.search(item["span"].strip())
    ]
    both_cols_filled = all(item["b"].strip() and item["span"].strip() for item in kp_items)
    kp_ok = kp_count > 0 and not label_hits and both_cols_filled
    result["checks"]["key_phrases_two_column_no_label"] = {
        "kp_count": kp_count, "label_hits": label_hits,
        "both_columns_filled": both_cols_filled, "pass": kp_ok,
    }
    if not kp_ok:
        if kp_count == 0:
            result["reasons"].append("Key Phrase要素(.kpitem)が0件")
        if label_hits:
            result["reasons"].append(f"Key Phraseにラベル文字列が残存: {label_hits}")
        if not both_cols_filled:
            result["reasons"].append("Key Phraseの英語列/日本語列のいずれかが空の項目がある")

    # (v) script/Key Phrases/Comment要素の存在
    card_titles = page.eval_on_selector_all(
        "#content .card h2", "els => els.map(el => el.textContent)"
    )
    comment_count = page.eval_on_selector_all(".comment", "els => els.length")
    has_kp_card = any("Key Phrase" in t for t in card_titles)
    has_script_card = any(re.search(r"Full Script|Full Story", t) for t in card_titles)
    structure_ok = has_kp_card and has_script_card and comment_count > 0
    result["checks"]["structure_present"] = {
        "card_titles": card_titles, "comment_count": comment_count,
        "has_kp_card": has_kp_card, "has_script_card": has_script_card,
        "pass": structure_ok,
    }
    if not structure_ok:
        result["reasons"].append(
            f"必須構造欠落: kp_card={has_kp_card}, script_card={has_script_card}, "
            f"comment_count={comment_count}"
        )

    # (iv) Play実行確認
    play_result = {"before": None, "after": None, "pass": False}
    try:
        before = page.eval_on_selector(
            "#episode",
            "a => ({currentTime: a.currentTime, paused: a.paused, error: a.error && a.error.code})",
        )
        page.eval_on_selector("#episode", "a => a.play()")
        page.wait_for_timeout(int(play_wait_seconds * 1000))
        after = page.eval_on_selector(
            "#episode",
            "a => ({currentTime: a.currentTime, paused: a.paused, error: a.error && a.error.code, "
            "readyState: a.readyState})",
        )
        play_result["before"], play_result["after"] = before, after
        play_result["pass"] = (
            after["error"] is None and after["currentTime"] > before["currentTime"]
            and after["paused"] is False
        )
    except Exception as e:  # noqa: BLE001
        result["reasons"].append(f"Play確認に失敗: {e}")
    result["checks"]["play_progresses"] = play_result
    if not play_result["pass"]:
        result["reasons"].append(f"Playが進行しなかった: {play_result}")

    result["console_errors"] = console_errors[:10]

    if screenshot_dir:
        Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
        shot_path = str(Path(screenshot_dir) / f"{name}.png")
        try:
            page.screenshot(path=shot_path, full_page=True)
            result["screenshot"] = shot_path
        except Exception as e:  # noqa: BLE001
            result["reasons"].append(f"screenshot取得に失敗: {e}")

    result["status"] = "PASS" if not result["reasons"] else "FAIL"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--urls-file", required=True, help="name<TAB>url を1行ずつ書いたファイル")
    ap.add_argument("--out", required=True, help="結果JSON出力先パス")
    ap.add_argument("--screenshot-dir", default=None, help="スクリーンショット保存先ディレクトリ")
    ap.add_argument("--play-wait-seconds", type=float, default=4.0)
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    items = parse_urls_file(args.urls_file)
    if not items:
        print("urls-fileに有効な行がありません", file=sys.stderr)
        return 1

    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, url in items:
            page = browser.new_page()
            try:
                results[name] = check_one(
                    page, name, url, args.screenshot_dir, args.play_wait_seconds
                )
            finally:
                page.close()
        browser.close()

    all_pass = all(r["status"] == "PASS" for r in results.values())
    summary = {"overall": "PASS" if all_pass else "FAIL", "results": results}
    Path(args.out).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for name, r in results.items():
        print(f"[{r['status']}] {name}: {r['url']}")
        for reason in r.get("reasons", []):
            print(f"    - {reason}")
    print(f"overall: {summary['overall']}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
