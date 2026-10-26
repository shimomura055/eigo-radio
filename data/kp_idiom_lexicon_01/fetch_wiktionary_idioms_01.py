# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01: Wiktionary `Category:English idioms` の見出し(タイトル文字列のみ)を取得し、
idioms.txt / meta.json を生成する。本文・定義・例文は取得しない。API費用0(Wikimedia公開API。User-Agent明記・逐次・rate制限順守)。
使い方: py data/kp_idiom_lexicon_01/fetch_wiktionary_idioms_01.py [--out-dir DIR] [--sleep 0.5]
出力: idioms.txt(1行1見出し・UTF-8・LF・Unicode順sort・重複なし) / meta.json(取得日時・件数・sha256・出典)。
runtimeは idioms.txt を読むだけ(er125_kp_rescue_production_01.load_idiom_lexicon)。sha256はmeta.jsonと突合し、不一致なら空表=救済しない(fail-closed)。"""
import argparse
import datetime
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://en.wiktionary.org/w/api.php"
CATEGORY = "Category:English idioms"
USER_AGENT = "eigo-radio-kp-rescue/1.0 (KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01; headword list only; contact: repo owner)"


def fetch_titles(category: str, sleep_s: float) -> tuple:
    titles, cont, calls = [], None, 0
    while True:
        q = {"action": "query", "list": "categorymembers", "cmtitle": category, "cmnamespace": "0", "cmlimit": "500",
             "format": "json", "formatversion": "2"}
        if cont:
            q["cmcontinue"] = cont
        req = urllib.request.Request(API + "?" + urllib.parse.urlencode(q), headers={"User-Agent": USER_AGENT})
        d = None
        for backoff in (0, 5, 20, 60, 120):          # 429/5xxは待って最大5回(同一リクエストの再試行。上限あり)
            time.sleep(backoff)
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    d = json.loads(r.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code not in (429, 500, 502, 503, 504):
                    raise
        if d is None:
            raise RuntimeError("Wiktionary API: retries exhausted (rate limited)")
        calls += 1
        titles += [m["title"] for m in d["query"]["categorymembers"]]
        cont = (d.get("continue") or {}).get("cmcontinue")
        if not cont:
            break
        time.sleep(sleep_s)
    return titles, calls


def sha_of_lines(lines) -> str:
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--sleep", type=float, default=0.5)
    a = ap.parse_args()
    titles, calls = fetch_titles(CATEGORY, a.sleep)
    uniq = sorted(set(t.strip() for t in titles if t.strip() and "\n" not in t))
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "idioms.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(uniq) + "\n")
    meta = {"source": "en.wiktionary.org " + CATEGORY, "api": "action=query&list=categorymembers (ns=0, titles only)",
            "license": "CC BY-SA 4.0 / GFDL (see ATTRIBUTION.md)", "fetched_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "api_calls": calls, "n_titles": len(uniq), "idioms_txt_sha256": sha_of_lines(uniq), "user_agent": USER_AGENT,
            "content": "headword titles only; no definitions/examples/page text"}
    with open(os.path.join(a.out_dir, "meta.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(meta, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
