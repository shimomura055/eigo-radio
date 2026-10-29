# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-DEV-REVISION-01: 復元した DEV データ(user_test/dev_enduser_page_01/data/*.json)に
改修用フィールドを追加する(API 0 / 音声は読み取りのみ・再生成なし / Production不変)。冪等。
 - parts[].ja / ja_source : 日本語訳(Full Story=承認済み日本語原稿 revision2.md の対応段落 / 英語Comment・In One Line=DEV訳(未承認))
 - parts[].glossary       : 本文直下の意味一覧(下線対象 + KP + Vocab、重複なし)
 - kp parts[].kp[].en_audio : KP区間mp3内の「最初の英語発話」の開始/終了秒(silencedetectで実測)
"""
import json, os, re, subprocess, difflib, hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
DATA = os.path.join(ROOT, 'user_test', 'dev_enduser_page_01', 'data')
FF = os.path.join(ROOT, '.venv', 'Lib', 'site-packages', 'imageio_ffmpeg', 'binaries', 'ffmpeg-win-x86_64-v7.1.exe')
JA_SRC = {
    'ai_island': 'er019_output/ai_island_temple/run_form_prod_01/ja_writer/revision2.md',
    'moon': 'er019_output/moon_shrinking/run_reselect_01/ja_writer/revision2.md',
}
JA = re.compile(r'[ぁ-んァ-ヶ一-龠]')

# DEV訳(未承認): 承認済み日本語原稿に対応段落が存在しない英語 Comment / In One Line のみ。英文の意味・事実を保持。
DEV_TR = {
    ('ai_island', 'adv', 'Comment 1'): ['頼まれていないのに、あるAIが何をしようとするかに注目して聞いてください。'],
    ('ai_island', 'adv', 'Comment 2'): ['あるAIは、頼まれてもいないのに自分で障害物コースを作りました。その経験は、AIたちが新しい課題に取り組むときに役立つのでしょうか。'],
    ('ai_island', 'adv', 'Comment 3'): ['島は1時間ごとにリセットされますが、AIたちはメモを残しておくことができます。島を経験したAIは、あとの塔づくりの課題でより良い結果を出しました。次の話では、以前の経験が新しい島での出来事とどうつながっているかに注目して聞いてください。'],
    ('ai_island', 'adv', 'Comment 4'): ['島はリセットされましたが、AIたちは書き残したものを持ち続けることができました。結果は、保存された情報がある面で重要だったことを示していますが、遊びそのものがAIを向上させたことの証明にはなりません。それでは、ここまでの要点をまとめましょう。'],
    ('ai_island', 'adv', 'In One Line'): ['島での経験があるAIエージェントは塔づくりで良い成績を収め、あるエージェントの記憶から技法を取り除くと、塔の平均数が減りました。保存された発見は、のちの塔づくりに役立つかもしれませんが、この結果は、遊びそのものが性能を高めることを証明するものではありません。'],
    ('ai_island', 'std', 'In One Line'): ['島での経験があるAIは、塔づくりで良い成績を収めました。あるAIの保存していた方法を取り除くと、塔の平均数が減りました。保存された発見はのちの塔づくりに役立つかもしれませんが、この結果は、遊びそのものがAIを向上させることを証明するものではありません。'],
    ('moon', 'adv', 'Comment 1'): ['聞きながら、研究チームがどのように月の表面を調べたかに注目してください。'],
    ('moon', 'adv', 'Comment 2'): ['月面の崖は、研究チームが月がどれだけ縮んだかを見積もる手がかりになりました。しかし、その見積もりは月の歴史全体を対象にしているのでしょうか。'],
    ('moon', 'adv', 'Comment 3'): ['しわの地図が示すのは歴史の後のほうの時期の収縮であり、一方モデルは月の歴史全体を対象にしているため、両者の数字はそのまま比べられるものではありません。次は、この違いと、月の砕けた岩の層が果たしたかもしれない役割を、話がどう掘り下げるかに注目して聞いてください。'],
    ('moon', 'adv', 'Comment 4'): ['月面の崖は、月が時間とともにどう変化したかについて、科学者たちに手がかりを与えました。同時に、月がどのように冷えたのかという疑問も生まれました。それでは、ここまでの要点をまとめましょう。'],
    ('moon', 'adv', 'In One Line'): ['研究者たちは8,900本を超える月面の崖を地図にまとめ、月は歴史の後のほうの時期に42〜46メートル縮んだと推定しました。これは誕生以来の総収縮量ではなく、すき間の多い厚い岩の層が冷却を遅らせた可能性があり、それがモデルの予測するより大きな収縮の説明の一つになりえます。'],
}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def speech_blocks(path, d=0.2, noise='-40dB'):
    o = subprocess.run([FF, '-hide_banner', '-i', path, '-af', 'silencedetect=noise=%s:d=%s' % (noise, d), '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', o)
    dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    sil, st = [], None
    for m in re.finditer(r'silence_(start|end): ([\d.]+)', o):
        if m[1] == 'start':
            st = float(m[2])
        else:
            sil.append((st, float(m[2])))
    sp, t = [], 0.0
    for s, e in sil:
        if s > t + 0.02:
            sp.append((t, s))
        t = e
    if dur > t + 0.02:
        sp.append((t, dur))
    return [b for b in sp if b[1] - b[0] >= 0.25]


def plain(h):
    return re.sub(r'<[^>]+>', '', h)


def norm(s):
    s = s.lower().strip()
    return re.sub(r'^(the|a|an)\s+', '', s)


def build(aid):
    path = os.path.join(DATA, aid + '.json')
    art = json.load(open(path, encoding='utf-8'))
    src_dir = os.path.join(ROOT, art['source_page'].rsplit('/', 1)[0])
    ja_path = os.path.join(ROOT, JA_SRC[aid])
    ja_paras = [x.strip() for x in open(ja_path, encoding='utf-8').read().strip().split('\n\n')][1:]   # 先頭=日本語タイトル
    report = dict(article=aid, ja_manuscript=JA_SRC[aid], ja_manuscript_sha256=sha(ja_path), levels={})
    for lv, L in art['levels'].items():
        rep = dict(approved_ja_blocks=0, approved_ja_paragraphs=0, dev_tr_blocks=0, native_ja_blocks=0, glossary={}, kp_audio={})
        parts = L['parts']
        # ---- 日本語訳 ----
        stories = [p for p in parts if p['kind'] == 'story']
        need = sum(len(p['paragraphs']) for p in stories)
        assert need == len(ja_paras), (aid, lv, need, len(ja_paras))
        k = 0
        for p in stories:
            n = len(p['paragraphs'])
            p['ja'] = ja_paras[k:k + n]
            k += n
            p['ja_source'] = 'approved_ja_manuscript'
            rep['approved_ja_blocks'] += 1
            rep['approved_ja_paragraphs'] += n
        for p in parts:
            if p['kind'] in ('comment', 'oneline'):
                en = JA.search(''.join(s['text'] for pa in p['paragraphs'] for s in pa)) is None
                if not en:
                    p.pop('ja', None)
                    p.pop('ja_source', None)
                    rep['native_ja_blocks'] += 1   # 既に日本語本文 -> 訳不要
                    continue
                t = DEV_TR[(aid, lv, p['label'])]
                assert len(t) == len(p['paragraphs']), (aid, lv, p['label'])
                p['ja'] = t
                p['ja_source'] = 'dev_translation_unapproved'
                rep['dev_tr_blocks'] += 1
        # ---- 意味一覧 ----
        vocab = L['vocab']
        for v in vocab:
            f = {x['label']: x['html'] for x in v['fields']}
            v['_quote'] = plain(f.get('本文の英文', '')).lower()
            v['_mean'] = plain(f.get('本文中の意味', '')).strip()
        seen, used_v = set(), set()
        for p in parts:
            p.pop('glossary', None)
            if p['kind'] not in ('story', 'oneline'):
                continue
            hs = [s['html'] for pa in p['paragraphs'] for s in pa]
            spans = []
            for h in hs:
                for m in re.finditer(r'<(span|strong) class="(lk\d)" data-hl="(p_\w+)">(.*?)</\1>', h):
                    spans.append((m[3], m[2], plain(m[4])))
            ents = []
            lk3 = [(w.split('＝')[0].strip(), w.split('＝')[1].strip()) for w in p.get('meanings', [])]
            used_m = set()
            for key, lk, txt in spans:
                if key in seen:
                    continue
                if lk in ('lk1', 'lk2'):
                    cand = [i for i, v in enumerate(vocab) if txt.lower() in v['_quote']]
                    assert len(cand) >= 1, (aid, lv, txt)
                    i = cand[0]
                    ents.append(dict(key=key, lk=lk, en=vocab[i]['heading'], ja=vocab[i]['_mean'], vi=i, form=txt))
                    used_v.add(i)
                else:
                    best, bi = 0, None
                    for j, (e, jm) in enumerate(lk3):
                        r = difflib.SequenceMatcher(None, norm(txt), norm(e)).ratio()
                        if r > best:
                            best, bi = r, j
                    assert best >= 0.8 and bi not in used_m, (aid, lv, txt, best, lk3)
                    used_m.add(bi)
                    ents.append(dict(key=key, lk=lk, en=(lk3[bi][0][:1].lower() + lk3[bi][0][1:]) if txt[:1].islower() else lk3[bi][0], ja=lk3[bi][1], vi=None, form=txt))
                seen.add(key)
            assert used_m == set(range(len(lk3))), (aid, lv, p['label'], 'meanings not all used', lk3)
            if ents:
                p['glossary'] = ents
            rep['glossary'][p['label']] = [(e['en'], e['ja'], e['vi']) for e in ents]
        assert used_v == set(range(len(vocab))), (aid, lv, 'vocab not all placed', used_v)
        for v in vocab:
            v.pop('_quote', None)
            v.pop('_mean', None)
        kp_heads = [kk['en'] for p in parts if p['kind'] == 'kp' for kk in p['kp']]
        glos = [e['en'] for p in parts for e in p.get('glossary', [])]
        for h in kp_heads:
            assert h in glos, ('KP not in glossary', aid, lv, h)
        assert len(glos) == len(set(glos)), ('duplicate glossary', glos)
        # ---- KP 英語のみ区間 ----
        for p in parts:
            if p['kind'] != 'kp':
                continue
            b = speech_blocks(os.path.join(src_dir, p['seg']))
            assert len(b) == 4, (aid, lv, p['label'], b)      # [番号, 英語, (日本語意味|英語解説), 英語(再掲)]
            s, e = b[1]
            ea = dict(start=round(max(0.0, s - 0.08), 3), end=round(e + 0.15, 3),
                      method='silencedetect -40dB d=0.2: 発話ブロック2番目=最初の英語発話(番号→英語→意味または英語解説→英語再掲の構成)')
            for kk in p['kp']:
                kk['en_audio'] = ea
            rep['kp_audio'][p['label']] = dict(blocks=[(round(x, 3), round(y, 3)) for x, y in b], chosen=[ea['start'], ea['end']], seg_dur=p['dur'])
        report['levels'][lv] = rep
    json.dump(art, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return report


if __name__ == '__main__':
    out = [build(aid) for aid in ('ai_island', 'moon')]
    json.dump(out, open(os.path.join(ROOT, 'docs', 'research', 'END-USER-LISTENING-PAGE-PROTOTYPE-01', 'rev_build_report_01.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for r in out:
        for lv, x in r['levels'].items():
            print(r['article'], lv, {k: v for k, v in x.items() if k not in ('glossary', 'kp_audio')})
            for lab, g in x['glossary'].items():
                print('   ', lab, g)
            for lab, g in x['kp_audio'].items():
                print('   ', lab, g['chosen'], g['blocks'])
