"""narrative_elements_v1 の機械カウント手順(暫定、ユーザー未承認)。
使い方: python narrative_count.py <JA本文.md> [<比較後JA本文.md>]
API・LLM不使用(正規表現と辞書のみ)。辞書・正規表現は narrative_elements_v1.md の付録と同一。
"""
import re, sys, difflib, json

SENT_SPLIT = re.compile(r'(?<=[。！？!?])')
PAT = {
    'hook_q': r'[？?]|ますよね|ですよね|でしょうか|思い浮かべ|想像|たとえば|もし|ある日',
    'hook_surprise': r'意外|驚|なぜ|実は|ところが|まさか|謎|ミステリー',
    'scene': r'(舞台|現場|電話口|画面|港|海峡|空|夜|朝|窓|部屋|目の前|手元|街|道|扉|幕|裏側|舞台裏|机|海|波|船)',
    'scene_verb': r'(ていた|ました|でした|ている|ていく|出てき|広が|並ん|響い|見え|開い|閉じ|立って|持って)',
    'twist': r'^(ところが|しかし|ただ、|ただし|でも|だが|それでも|ただ、ここで|ここで|とはいえ|一方)',
    'frame_words': r'(舞台|幕|出演者|主役|物語|ミステリー|旅|地図|謎|劇|看板|鍵|戸締まり|扉|カーテン)',
    'comment': r'(考えさせる|思います|でしょう|ではないでしょうか|大事なのは|大切なのは|ポイントは|気になり|面白い|意外|感じ|見ておきたい|注目)',
    'metaphor': r'(ようだ|ような|ように|みたい|たとえ|いわば|まるで|のよう)',
    'question': r'([？?]|ますよね|ですよね|でしょうか|でしょう？|ですか。)',
}

def clean(md):
    lines = [l.rstrip() for l in md.splitlines()]
    return lines

def parse(md):
    """タイトル(先頭行)・段落・文に分解。返り値: title, paras(list[list[str]])"""
    paras_raw = [p.strip() for p in re.split(r'\n\s*\n', md.strip()) if p.strip()]
    title = paras_raw[0].lstrip('# ').strip()
    paras = []
    for p in paras_raw[1:]:
        if p.startswith('## '):  # 一行要約見出しは本文に含めない
            continue
        sents = [s.strip() for s in SENT_SPLIT.split(p.replace('\n', '')) if s.strip()]
        paras.append(sents)
    return title, paras

def count(md):
    title, paras = parse(md)
    flat = [(pi, s) for pi, p in enumerate(paras) for s in p]
    first = ' '.join(paras[0]) if paras else ''
    last = ' '.join(paras[-1]) if paras else ''
    k40 = max(3, int(len(flat) * 0.4))
    head, tail = ' '.join(s for _, s in flat[:k40]), ' '.join(s for _, s in flat[-3:])
    inst = {}  # element -> list of sentence strings (instance = 1 sentence、Hook/語り枠は記事1件)
    inst['hook'] = [first] if (re.search(PAT['hook_q'], first) or re.search(PAT['hook_surprise'], title + first)) else []
    inst['scene'] = [s for _, s in flat if re.search(PAT['scene'], s) and re.search(PAT['scene_verb'], s) and not re.search(r'\d', s)]
    inst['twist'] = [s for _, s in flat if re.search(PAT['twist'], s)]
    fw_head = set(re.findall(PAT['frame_words'], title + head))
    fw_tail = set(re.findall(PAT['frame_words'], tail))
    inst['frame'] = [f'{sorted(fw_head & fw_tail)}'] if (fw_head & fw_tail) else []
    inst['comment'] = [s for _, s in flat if re.search(PAT['comment'], s)]
    inst['comment_echo'] = [f'{sorted(fw_head & fw_tail)}'] if (inst['comment'] and (fw_head & fw_tail) and re.search(PAT['comment'], tail)) else []
    inst['metaphor'] = [s for _, s in flat if re.search(PAT['metaphor'], s) or re.search(PAT['frame_words'], s)]
    inst['question'] = [s for _, s in flat if re.search(PAT['question'], s)]
    return dict(title=title, n_sent=len(flat), n_para=len(paras), inst=inst)

def align(before_sents, after_sents):
    """文の対応付け: 完全一致=unchanged、類似度>=0.6=modified、対応なし=deleted"""
    res = {}
    for b in before_sents:
        if b in after_sents:
            res[b] = 'unchanged'; continue
        best = max((difflib.SequenceMatcher(None, b, a).ratio() for a in after_sents), default=0)
        res[b] = 'modified' if best >= 0.6 else 'deleted'
    return res

def retention(md_before, md_after):
    cb, ca = count(md_before), count(md_after)
    sb = [s for p in parse(md_before)[1] for s in p]
    sa = [s for p in parse(md_after)[1] for s in p]
    al = align(sb, sa)
    out = {'n_sent_before': len(sb), 'n_sent_after': len(sa),
           'changed_ratio': round(sum(v == 'modified' for v in al.values()) / max(1, len(sb)), 3),
           'deleted_ratio': round(sum(v == 'deleted' for v in al.values()) / max(1, len(sb)), 3), 'elements': {}}
    for e, lst in cb['inst'].items():
        n = len(lst)
        if e in ('hook', 'frame', 'comment_echo'):  # 記事単位要素: 後にも成立していれば保持
            kept = 1 if (n and ca['inst'][e]) else 0
            strict = kept
        else:
            # modifiedは「後の文にも同要素の正規表現が残る」場合のみ保持と数える(別文化で要素が消えたらdeleted扱い)
            kept_m = 0
            for s in lst:
                if al[s] == 'unchanged':
                    kept_m += 1
                elif al[s] == 'modified':
                    cand = max(sa, key=lambda a: difflib.SequenceMatcher(None, s, a).ratio())
                    if cand in ca['inst'][e]:
                        kept_m += 1
            kept = kept_m
            strict = sum(1 for s in lst if al[s] == 'unchanged')
        out['elements'][e] = {'before': n, 'after': len(ca['inst'][e]), 'kept': kept, 'kept_strict': strict,
                              'retention': (round(kept / n, 3) if n else None), 'retention_strict': (round(strict / n, 3) if n else None)}
    return out

if __name__ == '__main__':
    a = open(sys.argv[1], encoding='utf8').read()
    if len(sys.argv) > 2:
        b = open(sys.argv[2], encoding='utf8').read()
        print(json.dumps(retention(a, b), ensure_ascii=False, indent=1))
    else:
        c = count(a)
        print(json.dumps({'title': c['title'], 'n_sent': c['n_sent'], 'n_para': c['n_para'],
                          'counts': {k: len(v) for k, v in c['inst'].items()}}, ensure_ascii=False))
