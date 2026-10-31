S=r'C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046/scratchpad'
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
U='https://shimomura055.github.io/eigo-radio/user_test/family_y_production_surname_choice_01/enduser/index.html'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':430,'height':900}); pg.goto(U); pg.wait_for_timeout(2500)
    for lv in ('std','adv'):
        try: pg.click(f'[data-lv="{lv}"]',timeout=2000)
        except Exception: pass
        pg.wait_for_timeout(500)
        print(lv, pg.eval_on_selector_all('#nuance .gr','els=>els.map(e=>[e.querySelector(".nh").textContent, Array.from(e.querySelectorAll("dt")).map(x=>x.textContent), e.querySelectorAll("dd strong.target-term").length])'))
    pg.locator('#nuance').screenshot(path=S+'/live_enduser_nuance.png')
    b.close()
