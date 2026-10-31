# Fable抜き取り用ブラインドシート(20件)。本文系(story/comment/preview/oneline/title)から、第1判定=6を10件+≠6を10件の無作為(seed固定)。回答キーは別file。
import json, random, pathlib
D = pathlib.Path(__file__).parent
rows = [r for r in json.load(open(D/'judged_p1.json', encoding='utf8')) if r['cat'] != 0 and r['ttype'] in ('story', 'comment', 'preview', 'oneline')]
rnd = random.Random(31415)
sel = rnd.sample([r for r in rows if r['cat'] == 6], 10) + rnd.sample([r for r in rows if r['cat'] != 6], 10)
rnd.shuffle(sel)
with open(D/'FABLE_BLIND_SHEET_20.md', 'w', encoding='utf8') as w:
    w.write("# Fable抜き取り用ブラインドシート(20件)\n\n各件について、COMPARISON_RUBRIC_01.md §2の分類(1〜6)と§3の重大度を判定してください。Family/Level/ja_source/第1判定は伏せてあります。回答キーは `FABLE_BLIND_KEY_20.json`(判定後に開く)。\n\n")
    for n, r in enumerate(sel, 1):
        w.write(f"## F{n:02d} [{r['ttype']}]\nEN: {r['en']}\nJA: {r['ja']}\n判定: 分類=__ 重大度=__\n\n")
json.dump([dict(id=f'F{n:02d}', pid=r['pid'], article=r['article'], level=r['level'], ttype=r['ttype'], ja_source=r['ja_source'], loc=r['loc'], cat_p1=r['cat'], sev_p1=r['sev'], note=r['note']) for n, r in enumerate(sel, 1)], open(D/'FABLE_BLIND_KEY_20.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
