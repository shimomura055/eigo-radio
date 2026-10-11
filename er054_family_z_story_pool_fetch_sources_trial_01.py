# -*- coding: utf-8 -*-
"""FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 Phase B: 一次資料の無料HTTP取得(Trial専用)。

- LLM/有料API不使用。ダウンロード物は「信頼しないデータ」として
  er054_output/family_z_story_pool_trial_01/sources/<ID>/ にのみ保存し、
  解釈はテキスト抽出(正規表現)のみ。実行は `python -I` で行う。
- 作品別に独立dirへ書くため並列(スレッド)実行可、同一ファイル書込みなし。
- Production(er026等)から参照されない。ファイル名に trial を含む。
"""
import hashlib, html, json, re, sys, datetime, os, time
from concurrent.futures import ThreadPoolExecutor
import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er054_output", "family_z_story_pool_trial_01", "sources")
UA = {"User-Agent": "eigo-radio-trial/1.0 (rights screening; contact: repo owner)"}
AZ = "https://www.aozora.gr.jp/cards/"

# role: card=図書カード, text=本文, aux=権利/事実確認用の補助資料
WORKS = {
  "L01": [("card", AZ+"000035/card1567.html"), ("text", AZ+"000035/files/1567_14913.html"),
          ("aux", "https://ja.wikipedia.org/wiki/%E8%B5%B0%E3%82%8C%E3%83%A1%E3%83%AD%E3%82%B9")],
  "L02": [("card", AZ+"000879/card127.html"),  ("text", AZ+"000879/files/127_15260.html")],
  "L03": [("card", AZ+"000081/card1927.html"), ("text", AZ+"000081/files/1927_17906.html")],
  "L04": [("card", "https://www.gutenberg.org/ebooks/55283"),
          ("text", "https://www.gutenberg.org/ebooks/55283.txt.utf-8"),
          ("aux", "https://en.wikipedia.org/wiki/The_Bet_(short_story)")],
  "L05": [("card", AZ+"000074/card423.html"),  ("text", AZ+"000074/files/423_504.html")],
  "L06": [("card", "https://www.gutenberg.org/ebooks/2397"),
          ("text", "https://www.gutenberg.org/ebooks/2397.txt.utf-8"),
          ("aux", "https://en.wikipedia.org/wiki/The_Story_of_My_Life_(biography)")],
  "L07": [("card", AZ+"000119/card624.html"),  ("text", AZ+"000119/files/624_14544.html"),
          ("aux", "https://ja.wikipedia.org/wiki/%E5%B1%B1%E6%9C%88%E8%A8%98")],
  "L08": [("card", AZ+"000129/card45245.html"), ("text", AZ+"000129/files/45245_22007.html")],
  "L09": [("card", AZ+"000879/card43016.html"), ("text", AZ+"000879/files/43016_16836.html"),
          ("aux", "https://ja.wikipedia.org/wiki/%E3%83%88%E3%83%AD%E3%83%84%E3%82%B3")],
  "L10": [("card", AZ+"000081/card1925.html"), ("text", AZ+"000081/files/1925_17912.html")],
  # 比較Trial委任_02で追加(L11〜L13)
  "L11": [("card", AZ+"000074/card424.html"),  ("text", AZ+"000074/files/424_19826.html")],
  "L12": [("card", AZ+"000148/card799.html"),  ("text", AZ+"000148/files/799_14972.html")],
  "L13": [("card", AZ+"000879/card92.html"),   ("text", AZ+"000879/files/92_14545.html")],
}
# 全作品共通の補助(ルール根拠資料)
COMMON_AUX = [("aux", "https://en.wikipedia.org/wiki/Copyright_law_of_Japan")]


def decode(raw, ctype):
    for enc in ("utf-8", "cp932"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace"), "utf-8(replace)"


def aozora_plain(t):
    m = re.search(r'<div class="main_text">(.*?)<div class="bibliographical_information">', t, re.S)
    body = m.group(1) if m else ""
    body = re.sub(r"<rp>.*?</rp>|<rt>.*?</rt>", "", body, flags=re.S)
    body = re.sub(r"<br\s*/?>", "\n", body)
    body = re.sub(r"</(p|div)>", "\n", body)
    body = re.sub(r"<[^>]+>", "", body)
    biblio = ""
    m2 = re.search(r'<div class="bibliographical_information">(.*?)</div>', t, re.S)
    if m2:
        biblio = html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>", "\n", m2.group(1)))).strip()
    return html.unescape(body).strip(), biblio, bool(m)


def fetch_one(wid, role, url):
    d = os.path.join(OUT, wid)
    os.makedirs(d, exist_ok=True)
    rec = {"role": role, "url": url, "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        r = None
        for attempt in range(1, 4):  # 取得失敗時は最大3回(間隔を空けて)再試行。試行回数は記録する
            rec["attempts"] = attempt
            try:
                r = requests.get(url, headers=UA, timeout=60)
                break
            except requests.RequestException as ex2:
                rec["last_attempt_error"] = f"{type(ex2).__name__}"
                if attempt == 3:
                    raise
                time.sleep(5 * attempt)
        rec["http_status"] = r.status_code
        rec["bytes"] = len(r.content)
        rec["sha256"] = hashlib.sha256(r.content).hexdigest()
        rec["content_type"] = r.headers.get("Content-Type")
        rec["ok"] = r.status_code == 200 and len(r.content) > 0
        name = {"card": "card", "text": "text_raw", "aux": "aux_" + hashlib.sha1(url.encode()).hexdigest()[:6]}[role]
        ext = ".txt" if url.endswith(".txt.utf-8") else ".html"
        with open(os.path.join(d, name + ext), "wb") as f:
            f.write(r.content)
        rec["saved_as"] = name + ext
        if rec["ok"]:
            t, enc = decode(r.content, rec["content_type"])
            rec["decoded_encoding"] = enc
            rec["decoded_chars"] = len(t)
            if role == "text":
                if "aozora.gr.jp" in url:
                    plain, biblio, found = aozora_plain(t)
                    rec["extract_method"] = "aozora main_text div, ruby(rp/rt) removed"
                    rec["main_text_div_found"] = found
                    rec["bibliographical_information"] = biblio
                else:
                    s = t.find("*** START OF"); e = t.find("*** END OF")
                    plain = t[s:e] if s >= 0 and e > s else t
                    rec["extract_method"] = "gutenberg START/END marker slice (whole ebook; story-level slicing is a Phase C step)"
                    rec["gutenberg_markers_found"] = s >= 0 and e > s
                plain = plain.replace("\r\n", "\n")
                with open(os.path.join(d, "text_plain.txt"), "w", encoding="utf-8", newline="\n") as f:
                    f.write(plain)
                rec["plain_chars"] = len(plain)
                rec["plain_chars_no_ws"] = len(re.sub(r"\s", "", plain))
                rec["plain_words_en"] = len(plain.split()) if "gutenberg" in url else None
                rec["plain_sha256"] = hashlib.sha256(plain.encode("utf-8")).hexdigest()
    except Exception as ex:  # 取得失敗は隠さず記録
        rec["ok"] = False
        rec["error"] = f"{type(ex).__name__}: {ex}"
    return rec


def run_work(wid):
    items = WORKS[wid] + COMMON_AUX
    recs = [fetch_one(wid, role, url) for role, url in items]
    man = {"work_id": wid, "trial": "FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01", "untrusted_data": True, "files": recs}
    with open(os.path.join(OUT, wid, "fetch_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=2)
    return wid, [(x["role"], x.get("http_status"), x.get("plain_chars") or x.get("decoded_chars"), x.get("error")) for x in recs]


if __name__ == "__main__":
    ids = sys.argv[1:] or sorted(WORKS)
    with ThreadPoolExecutor(max_workers=5) as ex:
        for wid, summ in ex.map(run_work, ids):
            print(wid, summ)
