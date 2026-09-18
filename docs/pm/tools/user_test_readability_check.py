"""user_test_readability_check.py

USER-TEST-SCRIPT-READABILITY-PROD-01 Phase A の runtime確認用E2Eチェッカー。
既存 `docs/pm/tools/user_test_page_e2e_check.py` の5点チェック(ラベル不在・
Key Phrase 2列・Standard/Advanced表示・Play進行・script/KP/Comment存在)に加え、
本タスクで追加した表示(水色Key Phraseハイライト・日本語訳section・Standard
Comment再掲のグレー表示・Advanced Comment訳)をDOM assertionとして検証する。

対象は `--tsv` の記事一覧から (article_id, level, src) を解決し、
`--translations` 配下の `index.json`/`kp_mapping.json`/`translation_ja.json`
と突き合わせて期待値(mapped件数・翻訳section数等)を算出したうえで、
`--base` (例 http://localhost:8765 または githack中継URL) 上の
`user_test/unified.html?src=...&level=...&en=...&ja=...` を実際に開いて検証する。

翻訳asset(kp_mapping.json/translation_ja.json)が存在しない(src,level)組は
「regression確認」(既存表示が壊れていないことのみ確認)に切り替える。

使い方:
  python docs/pm/tools/user_test_readability_check.py \
      --base http://localhost:8765 \
      --tsv docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv \
      --translations user_test/translations \
      --out docs/pm/closeout_136_e2e/script_readability_prod_01/phase_a/e2e_result.json \
      --screenshots docs/pm/closeout_136_e2e/script_readability_prod_01/phase_a \
      [--only-with-assets] [--play-wait-seconds 4]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse as up
from pathlib import Path

LABEL_RE = re.compile(r"^(English|英語|EN|日本語|日本語gloss|JA)\s*[:：]", re.IGNORECASE)


def parse_tsv(path: str) -> list[dict]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        cols = line.split("\t")
        row = dict(zip(header, cols))
        rows.append(row)
    return rows


def parse_qs_from_unified_url(u: str) -> dict:
    parsed = up.urlparse(u)
    qs = up.parse_qs(parsed.query)
    return {k: v[0] for k, v in qs.items()}


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


def build_unified_url(base: str, src: str, level: str, en: str, ja: str) -> str:
    q = up.urlencode({"src": src, "level": level, "en": en, "ja": ja})
    return f"{base.rstrip('/')}/user_test/unified.html?{q}"


def check_one(page, name: str, url: str, expect: dict, screenshot_dir: str | None,
              play_wait_seconds: float, mobile: bool, strict_play_seek: bool = True) -> dict:
    result: dict = {"name": name, "url": url, "checks": {}, "reasons": [], "expect": expect,
                     "informational_reasons": []}
    console_errors: list[str] = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        if dismiss_githack_interstitial(page):
            result["githack_interstitial_dismissed"] = True
        page.wait_for_function(
            "() => document.querySelector('#content .card h2') || document.querySelector('#content .error')",
            timeout=20000,
        )
        if page.query_selector("#content .error"):
            err_text = page.eval_on_selector("#content .error", "el => el.textContent")
            raise RuntimeError(f"unified.html表示エラー: {err_text}")
        # enhanceReadability()はcontent描画後にasync fetchするため、
        # translation sectionが増えるまで少し待つ(存在しないケースはtimeoutして続行)
        try:
            page.wait_for_timeout(600)
            page.wait_for_function(
                "() => document.querySelector('.trans-section') || true", timeout=3000
            )
        except Exception:
            pass
    except Exception as e:
        result["status"] = "FAIL"
        result["reasons"].append(f"page load/content待機に失敗: {e}")
        return result

    # --- 既存5点 ---
    eyebrow = page.eval_on_selector("#eyebrow", "el => el.textContent") or ""
    has_standard_or_advanced = bool(re.search(r"Standard|Advanced", eyebrow))
    has_bare_level = bool(re.search(r"\bA2\b|\bB1B?\b", eyebrow))
    header_ok = has_standard_or_advanced and not has_bare_level
    result["checks"]["header_standard_advanced"] = {"eyebrow_text": eyebrow, "pass": header_ok}
    if not header_ok:
        result["reasons"].append(f"ヘッダーがStandard/Advanced表示になっていない: {eyebrow!r}")

    kp_items = page.eval_on_selector_all(
        ".kpitem",
        "els => els.map(el => ({b: el.querySelector('b')?.textContent || '', "
        "span: el.querySelector('span')?.textContent || ''}))",
    )
    kp_count = len(kp_items)
    label_hits = [it for it in kp_items if LABEL_RE.search(it["b"].strip()) or LABEL_RE.search(it["span"].strip())]
    both_cols_filled = all(it["b"].strip() and it["span"].strip() for it in kp_items)
    kp_ok = kp_count > 0 and not label_hits and both_cols_filled
    result["checks"]["key_phrases_two_column_no_label"] = {
        "kp_count": kp_count, "label_hits": label_hits, "both_columns_filled": both_cols_filled, "pass": kp_ok,
    }
    if not kp_ok:
        result["reasons"].append(f"Key Phrase表示チェック失敗 kp_count={kp_count} label_hits={label_hits}")

    card_titles = page.eval_on_selector_all("#content .card h2", "els => els.map(el => el.textContent)")
    comment_count = page.eval_on_selector_all(".comment", "els => els.length")
    has_kp_card = any("Key Phrase" in t for t in card_titles)
    has_script_card = any(re.search(r"Full Script|Full Story", t) for t in card_titles)
    structure_ok = has_kp_card and has_script_card and comment_count > 0
    result["checks"]["structure_present"] = {
        "card_titles": card_titles, "comment_count": comment_count,
        "has_kp_card": has_kp_card, "has_script_card": has_script_card, "pass": structure_ok,
    }
    if not structure_ok:
        result["reasons"].append(f"必須構造欠落: kp_card={has_kp_card}, script_card={has_script_card}, comment_count={comment_count}")

    # --- 追加: 水色ハイライト数 ---
    hl_count = page.eval_on_selector_all("mark.kp-hl", "els => els.length")
    expect_hl = expect.get("expect_highlight_count")
    if expect_hl is not None:
        hl_ok = hl_count == expect_hl
        result["checks"]["highlight_count"] = {"actual": hl_count, "expected": expect_hl, "pass": hl_ok}
        if not hl_ok:
            result["reasons"].append(f"ハイライト数不一致: actual={hl_count} expected={expect_hl}")
        if hl_count > 0:
            hl_style = page.eval_on_selector("mark.kp-hl", "el => getComputedStyle(el).backgroundColor")
            result["checks"]["highlight_style"] = {"backgroundColor": hl_style}
    else:
        result["checks"]["highlight_count"] = {"actual": hl_count, "expected": None, "pass": True}

    # --- 追加: 翻訳section ---
    trans_present = page.query_selector(".trans-section") is not None
    expect_trans = expect.get("expect_translation")
    if expect_trans is not None:
        trans_ok = trans_present == expect_trans
        result["checks"]["translation_section"] = {"present": trans_present, "expected": expect_trans, "pass": trans_ok}
        if not trans_ok:
            result["reasons"].append(f"翻訳section存在チェック不一致: present={trans_present} expected={expect_trans}")
    else:
        result["checks"]["translation_section"] = {"present": trans_present, "expected": None, "pass": True}

    if trans_present:
        repost_count = page.eval_on_selector_all(".jacomment-repost", "els => els.length")
        repost_style = None
        if repost_count:
            repost_style = page.eval_on_selector(
                ".jacomment-repost", "el => ({color: getComputedStyle(el).color, background: getComputedStyle(el).backgroundColor})"
            )
        trans_h3_count = page.eval_on_selector_all(".trans-section h3", "els => els.length")
        result["checks"]["translation_detail"] = {
            "repost_count": repost_count, "repost_style": repost_style, "translated_heading_count": trans_h3_count,
        }
        exp_repost = expect.get("expect_repost_count")
        if exp_repost is not None and repost_count != exp_repost:
            result["reasons"].append(f"Comment再掲件数不一致: actual={repost_count} expected={exp_repost}")

    # --- 追加: 横スクロールなし ---
    scroll_info = page.evaluate("() => ({scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth})")
    no_hscroll = scroll_info["scrollWidth"] <= scroll_info["clientWidth"] + 2
    result["checks"]["no_horizontal_scroll"] = {**scroll_info, "pass": no_hscroll}
    if not no_hscroll:
        result["reasons"].append(f"横スクロールが発生: {scroll_info}")

    # --- Play/Seek ---
    play_result = {"before": None, "after": None, "pass": False}
    try:
        before = page.eval_on_selector("#episode", "a => ({currentTime: a.currentTime, paused: a.paused, error: a.error && a.error.code})")
        page.eval_on_selector("#episode", "a => { a.play().catch(()=>{}); return true; }")
        page.wait_for_timeout(int(play_wait_seconds * 1000))
        after = page.eval_on_selector("#episode", "a => ({currentTime: a.currentTime, paused: a.paused, error: a.error && a.error.code, readyState: a.readyState})")
        play_result["before"], play_result["after"] = before, after
        play_result["pass"] = after["error"] is None and after["currentTime"] > before["currentTime"] and after["paused"] is False
    except Exception as e:
        result["reasons"].append(f"Play確認に失敗: {e}")
    result["checks"]["play_progresses"] = play_result
    if not play_result["pass"]:
        msg = f"Playが進行しなかった: {play_result}"
        (result["reasons"] if strict_play_seek else result["informational_reasons"]).append(msg)

    seek_result = {"pass": False}
    try:
        page.eval_on_selector("#episode", "a => { a.currentTime = 60; a.play().catch(()=>{}); return true; }")
        page.wait_for_timeout(800)
        cur = page.eval_on_selector("#episode", "a => a.currentTime")
        seek_result["currentTime_after_seek"] = cur
        seek_result["pass"] = cur >= 59.5
    except Exception as e:
        seek_result["error"] = str(e)
    result["checks"]["seek"] = seek_result
    if not seek_result["pass"]:
        msg = f"Seek確認に失敗: {seek_result}"
        (result["reasons"] if strict_play_seek else result["informational_reasons"]).append(msg)

    # 「Failed to load resource: ... 404」はtranslation_ja.json/kp_mapping.jsonの
    # 存在確認fetch(意図的なprobe、資産が無いlevelでは仕様どおり404になる)由来の
    # ブラウザ標準診断メッセージであり、JS実行時エラーではないため除外する
    # (spec: assetが無い場合は「エラー表示なし、console.warnのみ」)。
    real_js_errors = [e for e in console_errors if "Failed to load resource" not in e]
    js_errors_ok = len(real_js_errors) == 0
    result["checks"]["no_js_errors"] = {
        "console_errors": console_errors[:10], "real_js_errors": real_js_errors[:10], "pass": js_errors_ok,
    }
    if not js_errors_ok:
        result["reasons"].append(f"console errorあり: {real_js_errors[:5]}")

    if screenshot_dir:
        Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
        shot_path = str(Path(screenshot_dir) / f"{name}{'_mobile' if mobile else '_pc'}.png")
        try:
            page.screenshot(path=shot_path, full_page=True)
            result["screenshot"] = shot_path
        except Exception as e:
            result["reasons"].append(f"screenshot取得に失敗: {e}")

    result["status"] = "PASS" if not result["reasons"] else "FAIL"
    return result


def build_expect(tdir: Path, article_id: str, lvl: str) -> tuple[dict, bool, bool]:
    mapping_path = tdir / (article_id or "") / lvl / "kp_mapping.json"
    trans_path = tdir / (article_id or "") / lvl / "translation_ja.json"
    has_mapping = mapping_path.is_file()
    has_trans = trans_path.is_file()
    expect: dict = {}
    if has_mapping:
        mp = json.loads(mapping_path.read_text(encoding="utf-8"))
        expect["expect_highlight_count"] = sum(
            (k.get("occurrences") or 0) for k in mp["key_phrases"] if k.get("mapping_type") != "UNRESOLVED"
        )
    if has_trans:
        td = json.loads(trans_path.read_text(encoding="utf-8"))
        expect["expect_translation"] = True
        expect["expect_repost_count"] = sum(
            1 for s in td.get("sections", []) if s.get("type") in ("existing_comment_repost", "reprint")
        )
    else:
        expect["expect_translation"] = False
    return expect, has_mapping, has_trans


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default=None, help="--tsv/--index使用時は必須。--urls-fromでは不要(実URLをそのまま使う)")
    ap.add_argument("--tsv", default=None,
                     help="記事一覧TSV(標準モード)。--indexと併用不可、どちらか一方を指定")
    ap.add_argument("--index", default=None,
                     help="user_test/translations/index.jsonを正としてsrcを解決するモード"
                          "(TSVのURLがまだ更新されていない場合のPhase Cローカル確認用)")
    ap.add_argument("--urls-from", default=None,
                     help="TSVのstandard_url/advanced_urlを実URLのまま(--baseで置換せず)開いて"
                          "公開runtime確認するモード(Phase C-10)。--full-checkで指定した"
                          "(article_id:level)のみPC+mobile+Play/Seekまで厳密判定し、"
                          "それ以外はPCのみ・Play/Seekは参考情報(overall判定に含めない)とする。")
    ap.add_argument("--full-check", default=None,
                     help="--urls-from使用時、厳密フルチェック対象を'article_id:level,...'形式で指定")
    ap.add_argument("--translations", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--screenshots", default=None)
    ap.add_argument("--only-with-assets", action="store_true",
                     help="translation_ja.json/kp_mapping.jsonが両方存在する(src,level)のみ実行")
    ap.add_argument("--play-wait-seconds", type=float, default=4.0)
    args = ap.parse_args()
    if not args.tsv and not args.index and not args.urls_from:
        raise SystemExit("--tsv / --index / --urls-from のいずれかを指定してください")
    if not args.urls_from and not args.base:
        raise SystemExit("--tsv/--indexモードでは--baseが必須です")

    from playwright.sync_api import sync_playwright

    tdir = Path(args.translations)
    index_path = tdir / "index.json"
    index_data = json.loads(index_path.read_text(encoding="utf-8"))
    index_by_key = {(it["src"], it["level"]): it for it in index_data["items"]}

    full_check_set = set()
    if args.full_check:
        for tok in args.full_check.split(","):
            tok = tok.strip()
            if tok:
                full_check_set.add(tuple(tok.split(":")))

    targets = []
    if args.urls_from:
        rows = parse_tsv(args.urls_from)
        for row in rows:
            for col, level in (("standard_url", "A2"), ("advanced_url", "B1")):
                u = row.get(col, "").strip()
                if not u:
                    continue
                qs = parse_qs_from_unified_url(u)
                src = qs.get("src", "")
                lvl = qs.get("level", level).upper()
                item = index_by_key.get((src, lvl))
                article_id = item["article_id"] if item else None
                expect, has_mapping, has_trans = build_expect(tdir, article_id or "", lvl)
                if args.only_with_assets and not (has_mapping and has_trans):
                    continue
                name = f"{article_id or 'unknown'}_{lvl}"
                is_full = (article_id, lvl) in full_check_set
                targets.append({"name": name, "url": u, "level": lvl, "expect": expect,
                                 "has_mapping": has_mapping, "has_trans": has_trans, "full_check": is_full})
    elif args.index:
        # index.json正 (article_id/level/src)を直接使う。en/jaは表示title用の
        # 装飾文字列に過ぎず判定に影響しないため、translation_ja.jsonのarticle
        # フィールド(なければarticle_id)を流用する。
        for it in index_data["items"]:
            article_id = it["article_id"]
            lvl = it["level"]
            src = it["src"]
            trans_path = tdir / article_id / lvl / "translation_ja.json"
            en = article_id
            if trans_path.is_file():
                td_peek = json.loads(trans_path.read_text(encoding="utf-8"))
                en = td_peek.get("article") or article_id
            ja = ""
            expect, has_mapping, has_trans = build_expect(tdir, article_id, lvl)
            if args.only_with_assets and not (has_mapping and has_trans):
                continue
            name = f"{article_id}_{lvl}"
            targets.append({"name": name, "src": src, "level": lvl, "en": en, "ja": ja, "expect": expect,
                             "has_mapping": has_mapping, "has_trans": has_trans})
    else:
        rows = parse_tsv(args.tsv)
        for row in rows:
            for col, level in (("standard_url", "A2"), ("advanced_url", "B1")):
                u = row.get(col, "").strip()
                if not u:
                    continue
                qs = parse_qs_from_unified_url(u)
                src = qs.get("src", "")
                lvl = qs.get("level", level).upper()
                en = qs.get("en", "")
                ja = qs.get("ja", "")
                item = index_by_key.get((src, lvl))
                article_id = item["article_id"] if item else None
                expect, has_mapping, has_trans = build_expect(tdir, article_id or "", lvl)
                if args.only_with_assets and not (has_mapping and has_trans):
                    continue
                name = f"{article_id or 'unknown'}_{lvl}"
                targets.append({"name": name, "src": src, "level": lvl, "en": en, "ja": ja, "expect": expect,
                                 "has_mapping": has_mapping, "has_trans": has_trans})

    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for viewport, mobile in ((  {"width": 1280, "height": 800}, False), ({"width": 390, "height": 844}, True)):
            context = browser.new_context(viewport=viewport)
            for t in targets:
                if mobile and args.urls_from and not t.get("full_check"):
                    continue  # urls-fromモード: full-check対象外はPCのみ
                if "url" in t:
                    url = t["url"]
                else:
                    url = build_unified_url(args.base, t["src"], t["level"], t["en"], t["ja"])
                strict = True
                if args.urls_from:
                    strict = bool(t.get("full_check"))
                page = context.new_page()
                page.set_default_timeout(20000)
                key = t["name"] + ("_mobile" if mobile else "_pc")
                try:
                    results[key] = check_one(page, t["name"], url, t["expect"], args.screenshots,
                                              args.play_wait_seconds, mobile, strict_play_seek=strict)
                finally:
                    page.close()
                r = results[key]
                print(f"[{r['status']}] {key}", flush=True)
                for reason in r.get("reasons", []):
                    print(f"    - {reason}", flush=True)
                Path(args.out).write_text(json.dumps({"overall": "IN_PROGRESS", "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
            context.close()
        browser.close()

    all_pass = all(r["status"] == "PASS" for r in results.values())
    summary = {"overall": "PASS" if all_pass else "FAIL", "results": results}
    Path(args.out).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"overall: {summary['overall']}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
