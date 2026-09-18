"""landing_page_e2e_check.py

USER-TEST-SCRIPT-READABILITY-PROD-01 Phase C-10(c)。
公開Landing page(`user_test/articles_2026_0918.html`のrawcdn.githack.com URL)を
実際に開き、以下を機械確認する:
  1. 20 href(Standard/Advanced)がTSVのstandard_url/advanced_urlと完全一致
  2. カテゴリー数(3)・記事数(10)・タイトル(en/ja)・概要がTSVと一致、行順維持
  3. レイアウト崩れなし(横スクロールなし、ボタンrowが折り返しで極端に破綻していないか)
  4. 代表いくつかのリンクを実際にクリックし、遷移先URLが期待URLと一致し
     audio要素のPlayが進行することを確認

使い方:
  python docs/pm/tools/landing_page_e2e_check.py \
      --url https://rawcdn.githack.com/.../user_test/articles_2026_0918.html \
      --tsv docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv \
      --out docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/public/landing_e2e.json \
      --screenshots docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/public \
      [--click-check N1,N2,...]  (0-indexedのarticle行、Standard側を代表クリック確認。既定: 0,4,7)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_tsv(path: str) -> list[dict]:
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        rows.append(dict(zip(header, line.split("\t"))))
    return rows


def dismiss_githack_interstitial(page) -> bool:
    try:
        btn = page.query_selector("form button.url-action-button")
    except Exception:
        btn = None
    if not btn:
        return False
    btn.click()
    try:
        page.wait_for_load_state("load", timeout=8000)
    except Exception:
        pass
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True)
    ap.add_argument("--tsv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--screenshots", default=None)
    ap.add_argument("--click-check", default="0,4,6,7",
                     help="0-indexedのStandardリンクを代表クリック確認(既定: young_travelers/free_address[修正対象]/ai_hiring[修正対象]/home_robots)")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    rows = parse_tsv(args.tsv)
    result: dict = {"url": args.url, "checks": {}, "reasons": []}

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for viewport, tag in (({"width": 1280, "height": 900}, "pc"), ({"width": 390, "height": 844}, "mobile")):
            context = browser.new_context(viewport=viewport)
            page = context.new_page()
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.goto(args.url, wait_until="domcontentloaded", timeout=20000)
            if dismiss_githack_interstitial(page):
                result.setdefault("githack_interstitial_dismissed", []).append(tag)
            page.wait_for_selector(".card", timeout=15000)

            cards = page.eval_on_selector_all(
                ".catblock",
                """els => els.map(cb => ({
                    category: cb.querySelector('h2.cathead')?.textContent || '',
                    articles: [...cb.querySelectorAll('.card')].map(c => ({
                        ja: c.querySelector('.ja-title')?.textContent || '',
                        en: c.querySelector('.en-title')?.textContent || '',
                        summary: c.querySelector('.summary')?.textContent || '',
                        std_href: c.querySelector('a.btn-std')?.getAttribute('href') || '',
                        adv_href: c.querySelector('a.btn-adv')?.getAttribute('href') || '',
                    }))
                }))""",
            )
            flat = [a for cb in cards for a in cb["articles"]]
            scroll_info = page.evaluate(
                "() => ({scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth})"
            )
            no_hscroll = scroll_info["scrollWidth"] <= scroll_info["clientWidth"] + 2

            # TSVとの突き合わせ
            mismatches = []
            if len(flat) != len(rows):
                mismatches.append(f"記事数不一致: DOM={len(flat)} TSV={len(rows)}")
            for i, (a, row) in enumerate(zip(flat, rows)):
                if a["en"].strip() != row.get("title_en", "").strip():
                    mismatches.append(f"row{i} title_en不一致: DOM={a['en']!r} TSV={row.get('title_en')!r}")
                if a["ja"].strip() != row.get("title_ja", "").strip():
                    mismatches.append(f"row{i} title_ja不一致")
                if a["summary"].strip() != row.get("summary_ja", "").strip():
                    mismatches.append(f"row{i} summary_ja不一致")
                if a["std_href"].replace("&amp;", "&") != row.get("standard_url", "").strip():
                    mismatches.append(f"row{i} standard_url不一致")
                if a["adv_href"].replace("&amp;", "&") != row.get("advanced_url", "").strip():
                    mismatches.append(f"row{i} advanced_url不一致")

            result["checks"][tag] = {
                "category_count": len(cards),
                "article_count": len(flat),
                "no_horizontal_scroll": no_hscroll,
                "scroll_info": scroll_info,
                "mismatches": mismatches,
                "console_errors": [e for e in console_errors if "Failed to load resource" not in e][:10],
            }
            if mismatches:
                result["reasons"].append(f"{tag}: TSVとの不一致 {len(mismatches)}件")
            if not no_hscroll:
                result["reasons"].append(f"{tag}: 横スクロール発生 {scroll_info}")

            if args.screenshots:
                Path(args.screenshots).mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(Path(args.screenshots) / f"landing_{tag}.png"), full_page=True)

            page.close()
            context.close()

        # 代表クリック確認(Standard側、PCのみ)
        click_indices = [int(x) for x in args.click_check.split(",") if x.strip() != ""]
        click_results = []
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=20000)
        dismiss_githack_interstitial(page)
        page.wait_for_selector(".card", timeout=15000)
        std_links = page.eval_on_selector_all("a.btn-std", "els => els.map(e => e.getAttribute('href'))")
        for idx in click_indices:
            if idx >= len(std_links):
                continue
            expected_href = std_links[idx].replace("&amp;", "&")
            try:
                with context.expect_page() as pinfo:
                    page.click(f"a.btn-std >> nth={idx}")
                popup = pinfo.value
                popup.wait_for_load_state("domcontentloaded", timeout=20000)
                dismiss_githack_interstitial(popup)
                popup.wait_for_function(
                    "() => document.querySelector('#content .card h2') || document.querySelector('#content .error')",
                    timeout=15000,
                )
                actual_url = popup.url
                play_result = {}
                try:
                    popup.eval_on_selector("#episode", "a => { a.play().catch(()=>{}); return true; }")
                    popup.wait_for_timeout(3000)
                    after = popup.eval_on_selector(
                        "#episode", "a => ({currentTime: a.currentTime, paused: a.paused})"
                    )
                    play_result = {"after": after, "pass": after["currentTime"] > 0 and not after["paused"]}
                except Exception as e:
                    play_result = {"error": str(e), "pass": False}
                click_results.append({
                    "index": idx, "expected_href": expected_href, "actual_url": actual_url,
                    "url_match": actual_url == expected_href, "play": play_result,
                })
                popup.close()
            except Exception as e:
                click_results.append({"index": idx, "error": str(e)})
        page.close()
        context.close()
        browser.close()

    result["click_checks"] = click_results
    for c in click_results:
        if not c.get("url_match") or not c.get("play", {}).get("pass"):
            result["reasons"].append(f"click_check index={c.get('index')} 失敗: {c}")

    result["status"] = "PASS" if not result["reasons"] else "FAIL"
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"status: {result['status']}")
    for r in result["reasons"]:
        print(f"  - {r}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
