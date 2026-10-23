# -*- coding: utf-8 -*-
"""TRIAL_03 T-1: 世界設定の事実確認用の少額web検索(Perplexity sonar-pro、最大2 call)。DEV/Trial専用。1 call = 1 query、リトライなし。"""
import json, os, sys, time
import requests
from dotenv import load_dotenv
import er005_cost_logger as cl

load_dotenv()
OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_03/world_search"
os.makedirs(OUT, exist_ok=True)
cl.install(f"{OUT}/raw_usage_log.jsonl")

Q = {
 "q1": ("日本の学校で、スマートフォン・携帯電話の扱いを次の4つに区別して、実態と出典(URL・発行日)を示してください。"
        "(a)学校への持込禁止 (b)校内での使用制限 (c)授業中のみ使用禁止 (d)登校時に学校が生徒全員から預かり、下校時に返却する運用(朝回収・放課後返却)。"
        "特に(d)について、実際に行っている学校・自治体・教育委員会の公的資料や報道の例と、それが小学校・中学校・高等学校(全日制・定時制)のどの学校種で行われているかを示してください。"
        "文部科学省などの全国調査で、学校種別の持込・預かりの割合が分かるものがあれば数値と出典を示してください。"
        "推測は書かず、確認できない点は『確認できない』と明記してください。"),
 "q2": ("日本の定時制高校(夜間)で、生徒のスマートフォン・携帯電話の校内での扱い(持込、授業中の使用、預かりの有無)の実態を、公的資料や報道の出典(URL・発行日)つきで示してください。"
        "働きながら通う生徒が仕事の連絡のため、休憩時間などに使うことを認めている例や、全日制高校と定時制高校で扱いが異なる例があれば示してください。"
        "推測は書かず、確認できない点は『確認できない』と明記してください。"),
}

def run(qid, model="sonar-pro"):
    fp = f"{OUT}/{qid}.json"
    if os.path.exists(fp):
        print("skip (exists)", qid); return
    key = os.getenv("PERPLEXITY_API_KEY")
    t0 = time.time()
    r = requests.post("https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model, "max_tokens": 1800, "messages": [{"role": "user", "content": Q[qid]}]}, timeout=90)
    el = round(time.time() - t0, 3)
    if r.status_code != 200:
        cl.record({"provider": "perplexity", "api": "world_setting_search", "model_id": model, "attempt_number": 1, "success": False,
                   "elapsed_seconds": el, "usage_source": "N/A_FAILED_CALL", "http_status": r.status_code})
        print("FAILED", r.status_code, r.text[:300]); sys.exit(2)
    d = r.json(); u = d.get("usage", {})
    cl.record({"provider": "perplexity", "api": "world_setting_search", "model_id": d.get("model"), "attempt_number": 1, "success": True,
               "elapsed_seconds": el, "usage_source": "OFFICIAL_API_RESPONSE", "http_status": 200,
               "input_tokens": u.get("prompt_tokens"), "output_tokens": u.get("completion_tokens"), "total_tokens": u.get("total_tokens")})
    json.dump({"query": Q[qid], "model": d.get("model"), "answer": d["choices"][0]["message"]["content"], "citations": d.get("citations", []),
               "search_results": d.get("search_results", []), "usage": u}, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(qid, "OK", u, "cites", len(d.get("citations", [])))

if __name__ == "__main__":
    run(sys.argv[1])
