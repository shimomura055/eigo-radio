# ER-005-SOURCE-RETRIEVER-01
# 非AI Source Retriever成立性検証。
# 通常HTTP取得 + HTML本文抽出(BeautifulSoup、AI/外部有料API不使用)のみで、
# Evidence Pack作成に十分な本文を取得できるかを検証する。
from __future__ import annotations

import json
import os
import time

import requests
from bs4 import BeautifulSoup

OUT_DIR = "er005_output/source_retriever_01"
os.makedirs(OUT_DIR, exist_ok=True)

TARGET_URL = ("https://www.frontiersin.org/journals/psychology/articles/"
              "10.3389/fpsyg.2026.1794353/full")

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def fetch_and_extract(url: str) -> dict:
    t0 = time.time()
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    elapsed = round(time.time() - t0, 3)

    meta = {
        "url": url,
        "final_url": resp.url,
        "redirected": resp.url != url,
        "http_status": resp.status_code,
        "elapsed_seconds": elapsed,
        "content_length_bytes": len(resp.content),
        "content_type": resp.headers.get("content-type"),
        "external_api_cost_usd": 0.0,
        "ai_token_cost_usd": 0.0,
        "search_cost_usd": 0.0,
    }

    if resp.status_code != 200:
        meta["extraction_status"] = "HTTP_ERROR"
        return meta

    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.find("title")
    meta["page_title"] = title_tag.text.strip() if title_tag else None

    main = soup.select_one("main.ArticleDetailsV4__main") or soup.find("main") or soup.find("article")
    if main is None:
        meta["extraction_status"] = "MAIN_CONTENT_CONTAINER_NOT_FOUND"
        return meta

    for tag in main.select("script, style, nav, footer, aside"):
        tag.decompose()

    text = main.get_text(separator="\n", strip=True)
    tables = main.find_all("table")

    meta["extraction_status"] = "OK"
    meta["container_selector_used"] = "main.ArticleDetailsV4__main"
    meta["extracted_text_length_chars"] = len(text)
    meta["table_count"] = len(tables)
    meta["extracted_text"] = text

    return meta


if __name__ == "__main__":
    result = fetch_and_extract(TARGET_URL)
    with open(f"{OUT_DIR}/retrieval_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"status={result.get('extraction_status')} "
          f"text_len={result.get('extracted_text_length_chars')} "
          f"tables={result.get('table_count')}")
