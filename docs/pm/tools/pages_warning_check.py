"""pages_warning_check.py

USER-TEST-HOSTING-GITHUB-PAGES-01 Phase E-5(c)。
GitHub Pages正式URL(Landing + 代表記事)を**新規browser context**
(cookie/storage無し、raw.githack.com依存のproxyを経由しないパスであることを
実データで確認する目的)で開き、以下を機械確認する:
  1. ページ本文に「One more step」「Open the page」「githack」「rawgit」の
     文字列が含まれないこと(rawgit.hack interstitial警告が出ていないこと)。
  2. `page.url()`のhostが`shimomura055.github.io`のままであること
     (githack proxyへリダイレクトされていないこと)。
  3. ページロード中に発生した全リクエストのhost一覧を記録し、
     `rawcdn.githack.com`/`raw.githack.com`/`rawgit`関連hostへのリクエストが
     0件であること(許容host: shimomura055.github.io、
     raw.githubusercontent.com[wake_before_alarmの音声絶対URL]、その他は列挙)。
  4. 主要resource(JSON/HTML/mp3)のレスポンスstatus・Content-Typeを記録する
     (MIME/CORS問題の有無確認)。

使い方:
  python docs/pm/tools/pages_warning_check.py \
      --urls "https://shimomura055.github.io/eigo-radio/user_test/articles_2026_0918.html" \
      --urls-from docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv \
      --pick "free_address:A2,ai_hiring:A2,personalized_news:B1,home_robots:A2" \
      --out docs/pm/closeout_136_e2e/script_readability_prod_01/phase_e/pages_warning_check.json
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json

WARNING_STRINGS = ["One more step", "Open the page", "githack", "rawgit"]
ALLOWED_HOSTS_DEFAULT = {"shimomura055.github.io", "raw.githubusercontent.com"}


def parse_tsv(path: str) -> list[dict]:
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        rows.append(dict(zip(header, line.split("\t"))))
    return rows


# article_idキーワード -> title_en部分文字列(srcパスにarticle_idが含まれない記事があるため、
# title_enでのマッチングを併用する)
KEYWORD_TITLE_HINTS = {
    "free_address": "Free-Address",
    "ai_hiring": "AI Helps Choose",
    "personalized_news": "Feed",
    "home_robots": "Home Robots",
    "tiny_bags": "Tiny Bags",
    "young_travelers": "Young Travelers",
    "convenience_ai": "Convenience-Store",
    "memory": "Memory",
    "digital_twins": "Digital Twins",
    "wake_before_alarm": "Wake",
}


def pick_urls_from_tsv(rows: list[dict], pick_spec: str) -> list[tuple[str, str]]:
    """pick_spec: 'free_address:A2,ai_hiring:A2,...' -> [(name, url), ...]
    まずsrcクエリにキーワードが含まれるか確認し、含まれない場合は
    KEYWORD_TITLE_HINTSでtitle_en部分一致にフォールバックする
    (src pathにarticle_idキーワードが含まれない記事[free_address/ai_hiring/
    personalized_news/home_robots等]が存在するため)。
    """
    out = []
    for token in pick_spec.split(","):
        token = token.strip()
        if not token:
            continue
        keyword, level = token.split(":")
        level = level.strip().upper()
        keyword = keyword.strip()
        found = None
        for row in rows:
            url = row["standard_url"] if level == "A2" else row["advanced_url"]
            qs = parse_qs(urlparse(url).query)
            src = qs.get("src", [""])[0]
            lvl = qs.get("level", [""])[0]
            if lvl.upper() != level:
                continue
            if keyword in src:
                found = url
                break
            hint = KEYWORD_TITLE_HINTS.get(keyword)
            if hint and hint.lower() in row.get("title_en", "").lower():
                found = url
                break
        out.append((f"{keyword}_{level}", found))
    return out


def check_page(context, name: str, url: str, allowed_hosts: set[str]) -> dict:
    page = context.new_page()
    request_hosts: dict[str, int] = {}
    resource_records: list[dict] = []

    def on_request(req):
        host = urlparse(req.url).netloc
        request_hosts[host] = request_hosts.get(host, 0) + 1

    def on_response(resp):
        url_l = resp.url.lower()
        if url_l.endswith(".json") or url_l.endswith(".html") or url_l.endswith(".mp3"):
            try:
                ctype = resp.headers.get("content-type", "")
            except Exception:
                ctype = ""
            resource_records.append({
                "url": resp.url,
                "status": resp.status,
                "content_type": ctype,
            })

    page.on("request", on_request)
    page.on("response", on_response)

    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    result: dict = {"name": name, "requested_url": url}
    try:
        page.goto(url, wait_until="networkidle", timeout=25000)
    except Exception as e:
        result["goto_error"] = str(e)
        try:
            page.wait_for_timeout(3000)
        except Exception:
            pass

    body_text = ""
    try:
        body_text = page.evaluate("() => document.body ? document.body.innerText : ''")
    except Exception:
        pass

    warning_hits = [w for w in WARNING_STRINGS if w.lower() in body_text.lower()]
    final_url = page.url
    final_host = urlparse(final_url).netloc

    disallowed_hosts = sorted(
        h for h in request_hosts.keys()
        if h and h not in allowed_hosts
    )
    githack_hits = [h for h in request_hosts.keys() if "githack" in h.lower() or "rawgit" in h.lower()]

    result.update({
        "final_url": final_url,
        "final_host": final_host,
        "final_host_ok": final_host == "shimomura055.github.io",
        "warning_string_hits": warning_hits,
        "warning_free": len(warning_hits) == 0,
        "request_hosts": request_hosts,
        "disallowed_hosts": disallowed_hosts,
        "githack_or_rawgit_hosts": githack_hits,
        "githack_count": sum(v for h, v in request_hosts.items() if "githack" in h.lower() or "rawgit" in h.lower()),
        "resource_records": resource_records,
        "console_errors": [e for e in console_errors if "Failed to load resource" not in e][:10],
    })
    page.close()
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--urls", action="append", default=[], help="直接指定するURL(複数指定可)")
    ap.add_argument("--urls-from", default=None, help="TSVパス(--pickと併用)")
    ap.add_argument("--pick", default=None, help="'keyword:LEVEL,keyword:LEVEL,...' 形式")
    ap.add_argument("--out", required=True)
    ap.add_argument("--allowed-hosts", default=",".join(ALLOWED_HOSTS_DEFAULT))
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    allowed_hosts = set(h.strip() for h in args.allowed_hosts.split(",") if h.strip())

    targets: list[tuple[str, str]] = [(f"direct_{i}", u) for i, u in enumerate(args.urls)]
    if args.urls_from and args.pick:
        rows = parse_tsv(args.urls_from)
        targets.extend(pick_urls_from_tsv(rows, args.pick))

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, url in targets:
            if not url:
                results.append({"name": name, "error": "url_not_found_in_tsv"})
                continue
            # 新規browser context(cookie/storage無し)= 新規セッション相当
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            r = check_page(context, name, url, allowed_hosts)
            results.append(r)
            context.close()
        browser.close()

    reasons = []
    for r in results:
        if r.get("error"):
            reasons.append(f"{r['name']}: {r['error']}")
            continue
        if not r.get("warning_free", False):
            reasons.append(f"{r['name']}: 警告文字列検出 {r.get('warning_string_hits')}")
        if not r.get("final_host_ok", False):
            reasons.append(f"{r['name']}: final_host不一致 {r.get('final_host')}")
        if r.get("githack_count", 0) > 0:
            reasons.append(f"{r['name']}: githack/rawgit host検出 {r.get('githack_or_rawgit_hosts')}")
        # 許容外host(githack/rawgit以外)はFAIL要因にせず、resultsのdisallowed_hostsとして
        # 記録するのみ(レポート側で目視確認する。例: フォント/画像等の無害な外部hostの可能性)。

    status = "PASS" if not reasons else "FAIL"
    out = {"status": status, "reasons": reasons, "results": results}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"status: {status}")
    for r in reasons:
        print(f"  - {r}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
