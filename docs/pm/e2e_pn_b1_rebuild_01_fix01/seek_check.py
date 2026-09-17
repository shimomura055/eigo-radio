import json
from playwright.sync_api import sync_playwright

URL = ("https://rawcdn.githack.com/shimomura055/eigo-radio/"
       "7ea8bd7ac3f3cab60890057cac82a08b68ac619e/user_test/unified.html?"
       "src=er012_output/personalized_news_b1_rebuild_01/audio/b1_2v_fix01/player.html"
       "&level=B1&en=One%20Feed%2C%20Two%20Very%20Different%20Experiences"
       "&ja=%E4%B8%80%E3%81%A4%E3%81%AE%E3%83%95%E3%82%A3%E3%83%BC%E3%83%89%E3%80%81"
       "%E4%BA%8C%E3%81%A4%E3%81%AE%E5%85%A8%E3%81%8F%E9%81%95%E3%81%86%E7%B5%8C%E9%A8%93")

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(20000)
    page.goto(URL, wait_until="domcontentloaded")
    try:
        btn = page.query_selector("form button.url-action-button")
        if btn:
            btn.click()
            page.wait_for_load_state("load", timeout=8000)
    except Exception:
        pass
    page.wait_for_function(
        "() => document.querySelector('#content .card h2') || document.querySelector('#content .error')",
        timeout=20000)
    page.eval_on_selector("#episode", "a => { a.currentTime = 60; a.play().catch(()=>{}); return true; }")
    page.wait_for_timeout(1500)
    after = page.eval_on_selector(
        "#episode",
        "a => ({currentTime: a.currentTime, paused: a.paused, error: a.error && a.error.code, duration: a.duration})")
    full_text = page.eval_on_selector("#content", "el => el.textContent")
    result = {
        "seek_after": after,
        "contains_he_has": "fit the few minutes he has" in full_text,
        "contains_his_personalized_feed": "relies on his personalized feed" in full_text,
        "contains_her_feed_closing_in": "worries her feed is closing in" in full_text,
        "contains_deleted_clause": "I worry I may miss something important" in full_text,
        "contains_do_not_want": "I do not want to sort through everything myself" in full_text,
        "contains_she_has": "fit the few minutes she has" in full_text,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    with open("docs/pm/e2e_pn_b1_rebuild_01_fix01/seek_and_text_check.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    context.close()
    browser.close()
