# FX4委任_03: 旧AIF2(ニュアンス欄付き)回答のうち、ニュアンス=不採用(0件)の8件を、選定内容を変えずに現行AIF1形式のreadableへ機械変換する使い捨てtool。
# 検証: (1)旧er128(git a39acf3bf^)のrestoreでAIF2照合コード・データ版・選定を完全検証 (2)ニュアンス決定=reject(不採用)であること
#      (3)選定(区分別candidate_id・文法・コメント)から現行make_codeでAIF1コードを再計算 (4)現行restoreでの復元payloadが旧payloadとニュアンス欄以外で一致
import sys, os, re, json, hashlib, importlib.util, subprocess
sys.path.insert(0, os.getcwd())
import er128_form_readable_restore_01 as new
blob = subprocess.run(['git','show','a39acf3bf^:er128_form_readable_restore_01.py'],capture_output=True).stdout
spec = importlib.util.spec_from_loader('er128_old', loader=None); old = importlib.util.module_from_spec(spec); old.__file__ = os.path.abspath('er128_form_readable_restore_01.py')
exec(compile(blob.decode('utf-8'),'er128_old','exec'), old.__dict__)
D = 'docs/research/FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01/confirm_03/'
DATA = 'user_test/selection_form_v3/data'
rep = {'old_module_blob_sha256': hashlib.sha256(blob).hexdigest(), 'old_commit': 'a39acf3bf^', 'items': []}
for s in ['untidiness_family_resource','ai_chat_sponsored_persuasion','meta_waddle_world','jwst_mystery_emission_line']:
    for lv in ['a2','b1b']:
        src = f'{D}paste_{s}__{lv}.txt'
        t = open(src, encoding='utf-8').read()
        p_old, notes_old = old.restore(t, DATA, lambda stem,d6: old.git_history_lookup(stem,d6,DATA))
        nuance = (p_old.get('selection') or {}).get('nuance')
        assert nuance and nuance.get('decision') in ('reject','rejected','none','不採用') or p_old.get('nuance_status') in ('reject','rejected'), (s,lv,nuance,p_old.get('nuance_status'))
        sel = p_old['selection']
        sel_ids = [(1,i['candidate_id']) for i in sel['key_phrase']] + [(2,i['candidate_id']) for i in sel['extra_explanation']] + [(3,i['candidate_id']) for i in sel['meaning_display']]
        gram = [(g.get('candidate_id') or g['id'], g.get('explanation_sha256') or '') for g in sel['grammar']]
        m = list(old.CODE_RE.finditer(t)) if False else list(re.finditer(r'AIF2-([A-Za-z0-9_]+)-([0-9a-f]{6})-', t))[-1]
        stem, d6 = m.group(1), m.group(2)
        dpath = os.path.join(DATA, stem + '.json')
        raw = open(dpath,'rb').read()
        if new.d6_of_bytes(raw) != d6:
            raw = new.git_history_lookup(stem, d6, DATA); assert raw is not None and new.d6_of_bytes(raw) == d6, ('data版がd6と不一致(履歴にも無し)', stem)
        d = json.loads(raw.decode('utf-8'))
        code1 = new.make_code(stem, d, d6, sel_ids, gram, p_old.get('comment') or '')
        # ニュアンス節除去 + コード差替え
        t2 = re.sub(r'ニュアンス解説：不採用\n【ニュアンス全文】.*?【ニュアンスここまで】\n\n', '', t, flags=re.S)
        assert t2 != t
        t2 = re.sub(r'AIF2-[A-Za-z0-9_\-]+', code1, t2)
        out = f'{D}paste_aif1_{s}__{lv}.txt'
        open(out,'w',encoding='utf-8',newline='\n').write(t2)
        p_new, notes_new = new.restore(t2, DATA, lambda stem,d6: new.git_history_lookup(stem,d6,DATA))
        def strip(p):
            q = json.loads(json.dumps(p)); q.pop('restore_meta',None); q.pop('nuance_status',None); q.pop('schema_minor',None); q['selection'].pop('nuance',None); return q
        same = strip(p_old) == strip(p_new)
        rep['items'].append({'slug_level': f'{s}__{lv}', 'old_code': m.group(0)[:0] or re.search(r'AIF2-\S+', t).group(0), 'new_code': code1, 'nuance_decision': nuance, 'selection_equal_except_nuance': same,
                             'kp': [(i['term'], i['ja_gloss']) for i in sel['key_phrase']], 'out': out})
        print(s, lv, 'OK' if same else 'DIFF', code1)
        assert same
json.dump(rep, open(D + 'aif2_to_aif1_conversion_report.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
