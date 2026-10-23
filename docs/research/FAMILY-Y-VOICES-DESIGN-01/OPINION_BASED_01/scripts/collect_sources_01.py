"""FYT13 Phase1 収集script(DEV/Trial専用。API 0、HTTP GETのみ)。
Seed 5URLと、みらい議会の法案ページ配下の全トピックページを取得し、sources/ に保存する(sources/ はgit管理外)。
使い方: .venv の python で本scriptを実行(cwd任意)。出力: sources/*.txt, sources/mirai_topics/*.txt, mirai_topics/_ops_v2.json
"""
import os, re, json, time, collections, datetime, requests
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "sources")
H = {"User-Agent": "Mozilla/5.0 (research; eigo-radio FYT13 phase1)"}
SEEDS = {
    "1_mirai_topic_seed": "https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/f447d968-a542-4683-b8a6-a9c24e330aa4",
    "1_mirai_bill": "https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe",
    "2_tbs_p1": "https://newsdig.tbs.co.jp/articles/-/2618789?display=1",
    "2_tbs_p2": "https://newsdig.tbs.co.jp/articles/-/2618789?page=2",
    "2_tbs_p3": "https://newsdig.tbs.co.jp/articles/-/2618789?page=3",
    "2_tbs_p4": "https://newsdig.tbs.co.jp/articles/-/2618789?page=4",
    "3_saito": "https://note.com/saito_n_lab/n/n8cc240dc6f57",
    "4_exbridge": "https://exbridge.jp/vibeblog/2026-10-08-kconsensus-kodomo-sns-polis.html",
    "5_line": "https://note.com/linesurveys_jp/n/ne5a9dcf3eb81",
}
BILL = "/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/"


def to_text(html):
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript"]):
        t.decompose()
    return re.sub(r"\n\s*\n+", "\n", s.get_text("\n"))


def save(name, url, r):
    txt = to_text(r.text)
    head = f"URL {url}\nFETCHED {datetime.datetime.now().astimezone().isoformat(timespec='seconds')}\nHTTP {r.status_code}\nCHARS {len(txt)}\n"
    os.makedirs(os.path.dirname(os.path.join(OUT, name)), exist_ok=True)
    open(os.path.join(OUT, name + ".txt"), "w", encoding="utf-8").write(head + txt)
    return txt


def main():
    os.makedirs(os.path.join(OUT, "mirai_topics"), exist_ok=True)
    for k, u in SEEDS.items():
        r = requests.get(u, headers=H, timeout=30)
        save(k, u, r)
        print(k, r.status_code)
    cur = "cfc02f51-5057-4dc0-8504-c832e76cbdbe"  # トピック一覧の先頭(法案ページから辿れる1件目)
    seen, idx, ops = [], {}, []
    cnt = collections.Counter()
    while cur and cur not in seen:
        u = "https://gikai.team-mir.ai" + BILL + cur
        r = requests.get(u, headers=H, timeout=30)
        n = len(seen) + 1
        txt = save(f"mirai_topics/{n:03d}_{cur[:8]}", u, r)
        L = txt.split("\n")
        title = L[0].split(" - ")[0]
        for i, l in enumerate(L):
            if l != "“":
                continue
            k = i + 1
            tx = []
            while k < len(L) and L[k] != "インタビューレポートを読む":
                tx.append(L[k]); k += 1
            m, blk = i - 1, []
            while m >= 0 and L[m] != "すべて" and len(blk) < 6:
                blk.append(L[m]); m -= 1
            blk = [b for b in blk[::-1] if b != "インタビューレポートを読む"]
            st = next((j for j, b in enumerate(blk) if b in ("期待", "懸念")), None)
            if st is None:
                continue
            rest = blk[st + 1:]
            cnt[n] += 1
            ops.append({"id": f"MR-T{n:03d}-{cnt[n]:02d}", "topic": n, "topic_title": title, "url": u, "ai_label": blk[st - 1] if st else "",
                        "stance": blk[st], "attr": "/".join(rest[:-1]), "date": rest[-1] if rest else "", "text": "\n".join(tx)})
        seen.append(cur)
        nx = re.findall(r'href="' + re.escape(BILL) + r'([0-9a-f-]{36})"[^>]*>次のトピック', r.text)
        cur = nx[0] if nx else None
        time.sleep(0.3)
    json.dump(ops, open(os.path.join(OUT, "mirai_topics", "_ops_v2.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("topics", len(seen), "opinions", len(ops))


if __name__ == "__main__":
    main()
