"""F班(委任_06F) 実ブラウザ検証(playwright/chromium)。pages出力をローカルHTTPで開き、PC(1280)とスマホ(375/390, DPR2/3)で
①二重下線/②下線/③下線の見え方をDOM計測(computed style)+スクリーンショット+画素解析で記録する。API 0。
用法: browser_check_s23f_01.py --out <json> --shots <dir> NAME=path/to/index.html [NAME=...]
"""
import argparse, functools, http.server, json, os, re, socketserver, threading, io
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright_noplay as sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

VIEWPORTS = [("pc1280", 1280, 900, 1), ("sp375_dpr3", 375, 812, 3), ("sp390_dpr2", 390, 844, 2)]


def serve(root):
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
    h.log_message = lambda *a, **k: None
    srv = socketserver.TCPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def diff_bands(png_a, png_b):
    """装飾あり/なしの同一要素の画素差分行(=下線の行)の連続グループ数を数える。lk1=2本、lk2/lk3=1本のはず。"""
    from PIL import Image, ImageChops
    a = Image.open(io.BytesIO(png_a)).convert("L")
    b = Image.open(io.BytesIO(png_b)).convert("L")
    if a.size != b.size:
        return [], a.size[1]
    d = ImageChops.difference(a, b).point(lambda v: 255 if v > 60 else 0)
    w, h = d.size
    px = d.load()
    rows = [sum(1 for x in range(w) if px[x, y]) / w for y in range(h)]
    out, inb = [], False
    for y, r in enumerate(rows):
        if r >= 0.5:
            if inb and y - out[-1][1] <= 1:
                out[-1][1] = y
            else:
                out.append([y, y])
            inb = True
        else:
            inb = False
    return out, h


JS_STYLE = """(el)=>{const c=getComputedStyle(el);const p=getComputedStyle(el.parentElement);
 return {tag:el.tagName,cls:el.className,text:el.textContent,hl:el.getAttribute('data-hl'),title:el.getAttribute('title'),
 decoLine:c.textDecorationLine,decoStyle:c.textDecorationStyle,decoThickness:c.textDecorationThickness,underlineOffset:c.textUnderlineOffset,fontWeight:c.fontWeight,fontSize:c.fontSize,color:c.color,bg:c.backgroundColor,bgImage:c.backgroundImage,
 pFontSize:p.fontSize,pColor:p.color,pFontWeight:p.fontWeight,rects:el.getClientRects().length}}"""


def check(page, name, vp, shots):
    res = {"viewport": vp}
    info = {}
    for k in ("lk1", "lk2", "lk3"):
        els = page.query_selector_all(f"[data-hl].{k}")
        info[k] = {"count": len(els)}
        if els:
            info[k]["style"] = page.evaluate(JS_STYLE, els[0])
            # 単一行のものを優先してスクショ+画素解析
            pick = None
            for e in els:
                if page.evaluate("(el)=>el.getClientRects().length", e) == 1:
                    pick = e; break
            pick = pick or els[0]
            pick.scroll_into_view_if_needed()
            r = pick.bounding_box()
            if r:
                clip = {"x": max(r["x"] - 4, 0), "y": r["y"] - 2, "width": min(r["width"] + 8, 700), "height": r["height"] + 10}
                png = page.screenshot(clip=clip)
                page.evaluate("(el)=>{el.dataset._td=el.style.textDecoration;el.style.setProperty('text-decoration','none','important')}", pick)
                png_nd = page.screenshot(clip=clip)
                page.evaluate("(el)=>{el.style.removeProperty('text-decoration');if(el.dataset._td)el.style.textDecoration=el.dataset._td;delete el.dataset._td}", pick)
                b, h = diff_bands(png, png_nd)
                info[k]["underline_bands_px"] = b
                info[k]["underline_band_count"] = len(b)
                fn = f"{shots}/{name}_{vp}_{k}.png"
                with open(fn, "wb") as f:
                    f.write(png)
                info[k]["shot"] = os.path.basename(fn)
            info[k]["wrapped_rect_count"] = page.evaluate("(el)=>el.getClientRects().length", pick)
    res["classes"] = info
    body = page.evaluate("document.body.innerText")
    res["innerText_has_pause"] = "⏸" in body
    res["innerText_has_data_attr_like"] = bool(re.search(r"data-hl|lk1|lk2|lk3|HL_", body))
    res["lk_legend"] = page.evaluate("[...document.querySelectorAll('p.lk-legend')].map(e=>e.innerText)")
    res["lk_meaning_li"] = page.evaluate("[...document.querySelectorAll('ul.lk-meaning li')].map(e=>e.innerText)")
    res["pause_inside_hl"] = page.evaluate("[...document.querySelectorAll('[data-hl]')].filter(e=>e.textContent.includes('⏸')).length")
    res["horizontal_overflow"] = page.evaluate("document.documentElement.scrollWidth>window.innerWidth+1")
    # コピーテキスト相当(選択->toString)
    res["copy_has_extra"] = page.evaluate("""()=>{const r=document.createRange();const e=document.querySelector('[data-hl]');if(!e)return null;
        r.selectNodeContents(e.parentElement);const s=r.toString();return /[⏸■□●○◆◇▲▼]/.test(s)}""")
    # 同じ段落内で改行/句読点が装飾で変わっていないこと: 装飾剥がし後のtextContent == 装飾あり textContent
    res["strip_equal"] = page.evaluate("""()=>{const out=[];for(const p of document.querySelectorAll('.script, td, p')){
        if(!p.querySelector('[data-hl]'))continue;const a=p.textContent;const c=p.cloneNode(true);
        c.querySelectorAll('[data-hl]').forEach(e=>e.replaceWith(document.createTextNode(e.textContent)));out.push(a===c.textContent)}
        return {n:out.length,all_equal:out.every(x=>x)}}""")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--shots", required=True)
    ap.add_argument("pages", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.shots, exist_ok=True)
    results = {}
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for spec in a.pages:
            name, path = spec.split("=", 1)
            path = os.path.abspath(path)
            root = os.path.dirname(path)
            srv = serve(root)
            url = f"http://127.0.0.1:{srv.server_address[1]}/{os.path.basename(path)}"
            results[name] = {"url_path": path}
            for vp, w, h, dpr in VIEWPORTS:
                ctx = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=dpr)
                pg = ctx.new_page()
                pg.goto(url, wait_until="load")
                results[name][vp] = check(pg, name, vp, a.shots)
                if vp == "sp390_dpr2" or vp == "pc1280":
                    pg.screenshot(path=f"{a.shots}/{name}_{vp}_top.jpg", type="jpeg", quality=55, clip={"x": 0, "y": 0, "width": w, "height": min(h, 700)})
                ctx.close()
            srv.shutdown()
        br.close()
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("saved", a.out)


main()
