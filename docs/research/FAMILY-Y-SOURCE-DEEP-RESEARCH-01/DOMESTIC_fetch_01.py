"""FYDR1A 国内情報源調査用の取得helper(HTTP GETのみ・API 0・LLM 0)。
使い方:
  python DOMESTIC_fetch_01.py links URL [grep]      リンク一覧(タイトル・href)
  python DOMESTIC_fetch_01.py get URL [maxchars] [offset]  本文テキスト取得(全文はcache dirに保存、標準出力は先頭のみ)
  python DOMESTIC_fetch_01.py rec SITE N URL POSTED_AT METHOD SUMMARY EXCERPT...   sources_domestic/<SITE>_<N>.json を記録
UA: 自己申告の研究用UA(ブラウザ偽装・AI crawler名の詐称はしない)。間隔>=1.5秒。cacheは権利上commitしない(scratchpad)。"""
import sys, os, re, json, time, hashlib, datetime, requests
from bs4 import BeautifulSoup
H = {"User-Agent": "Mozilla/5.0 (compatible; eigo-radio-research/1.0)", "Accept-Language": "ja"}
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("FYDR_CACHE", os.path.join(HERE, "_cache_uncommitted"))
def dec(r):
    b = r.content
    for enc in ("utf-8", "cp932", "euc_jp"):
        try: return b.decode(enc)
        except Exception: pass
    return b.decode("utf-8", "replace")
def fetch(u, delay=1.6):
    time.sleep(delay)
    r = requests.get(u, headers=H, timeout=30)
    return r.status_code, dec(r)
def text_of(html):
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript", "nav", "footer", "header", "iframe"]): t.decompose()
    return re.sub(r"\n\s*\n+", "\n", s.get_text("\n"))
if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "links":
        code, html = fetch(sys.argv[2]); s = BeautifulSoup(html, "html.parser")
        g = sys.argv[3] if len(sys.argv) > 3 else ""
        print(code, s.title.get_text() if s.title else "")
        for a in s.find_all("a", href=True):
            t = a.get_text(" ", strip=True)
            if g and g not in a["href"] and g not in t: continue
            print(t[:80], "|", a["href"])
    elif cmd == "get":
        u = sys.argv[2]; mx = int(sys.argv[3]) if len(sys.argv) > 3 else 3000; off = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        code, html = fetch(u); tx = text_of(html)
        os.makedirs(CACHE, exist_ok=True)
        open(os.path.join(CACHE, hashlib.md5(u.encode()).hexdigest()[:10] + ".txt"), "w", encoding="utf-8").write(tx)
        print("HTTP", code, "chars", len(tx), "fetched", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
        print(tx[off:off + mx])
    elif cmd == "rec":
        site, n, u, posted, method, summary = sys.argv[2:8]; ex = sys.argv[8:]
        d = os.path.join(HERE, "sources_domestic"); os.makedirs(d, exist_ok=True)
        json.dump({"site": site, "url": u, "fetched_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                   "posted_at": posted, "method": method, "summary_by_researcher": summary, "short_excerpts": ex,
                   "note": "全文は保存しない(権利上)。summaryは調査者自身の要約、excerptsは短い逐語抜粋。"},
                  open(os.path.join(d, f"{site}_{n}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("saved", site, n)
