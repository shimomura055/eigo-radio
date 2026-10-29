import json,sys,http.server,threading,functools,os
from playwright.sync_api import sync_playwright
S=sys.argv[1]; F=S+'/form'
idx={"schema":"eigo_radio_selection_index_v1","default":"surname__a2","articles":[
 {"slug":"surname","level":"a2","level_label":"Standard","name":"夫が妻の姓を選ぶとき","data":"data/a2.json"},
 {"slug":"surname","level":"b1b","level_label":"Advanced","name":"夫が妻の姓を選ぶとき","data":"data/b1b.json"}]}
json.dump(idx,open(F+'/data/articles.json','w',encoding='utf-8'),ensure_ascii=False)
h=functools.partial(http.server.SimpleHTTPRequestHandler,directory=F)
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),h); port=srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
out={}
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':430,'height':900})
    pg.goto(f'http://127.0.0.1:{port}/index.html'); pg.wait_for_timeout(1500)
    for i,lv in enumerate(('a2','b1b')):
        pg.select_option('select',str(i)); pg.wait_for_timeout(800)
        el=pg.query_selector('#nuances')
        out[lv]={'h':pg.inner_text('#nuanceH'),'notice':pg.inner_text('#nuanceNotice'),'text':el.inner_text()}
        el.screenshot(path=f'{S}/form_nuance_{lv}.png')
        # adopt/reject radios present
        out[lv]['radios']=pg.eval_on_selector_all('input[data-nuance]','e=>e.map(x=>x.dataset.nuance)')
    b.close()
json.dump(out,open(S+'/form_out.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
