# -*- coding: utf-8 -*-
"""選定フォームv3 報告(batch)の公開ツール(SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_04、DESIGN_03 1-8節 + Opus M1/M6/M7/M9/M10/M14)。

2段階publish(M7):
  stage1  : 検査(members=articles.jsonのdata stem完全一致・validateArticle相当・重複/空拒否・id正規表現)
            -> data/batches/<id>.json と data/batches/index.json(登録のみ。latest不変)を原子的に書出し
            -> (--push)対象2ファイルだけcommit/push
            -> 公開URL ?batch=<id> のlive smoke(tools/selection_form_live_smoke_01.py)。PASSするまで latest に載せない。
            URLを利用者へ出すのは tools/selection_batch_url_01.issue_batch_url(smoke PASS必須)経由のみ。
  promote : smoke PASS(id一致・ASSET_VERSION一致)を確認してから index.json の latest を更新(--push)
            -> パラメータ無しURLの解決をlive smoke。test報告はlatestにしない(--allow-test-latest は検証用途のみ)。
            --clear-latest で latest を外す(検証後の原状復帰)。
公開済みidの不変性(M10): membersまたは各member data sha256が異なる同id再publishは拒否(新idを使う)。
smoke失敗時は原因診断(Pages未反映/JS版不一致/データ欠落)をJSONに残して非0終了(自動再pollはsmoke側の --wait-sec)。API呼出0。"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FORM_REL = 'user_test/selection_form_v3'
BASE_DEFAULT = 'https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/'
TRAILER = 'Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>'


class PublishError(Exception):
    pass


def git(repo, *a, check=True):
    r = subprocess.run(['git', '-C', repo] + list(a), capture_output=True)
    if check and r.returncode != 0:
        raise PublishError('git %s failed: %s' % (' '.join(a), r.stderr.decode('utf-8', 'replace')[:300]))
    return r


def form_logic_src(form_dir):
    return open(os.path.join(form_dir, 'form_logic.js'), encoding='utf-8').read()


def id_regex(form_dir):
    m = re.search(r"var BATCH_ID_RE = /(.+?)/;", form_logic_src(form_dir))
    if not m:
        raise PublishError('form_logic.js にBATCH_ID_REが無い')
    return re.compile(m.group(1))


def asset_version(form_dir):
    m = re.search(r"var ASSET_VERSION = '([^']+)'", form_logic_src(form_dir))
    return m.group(1) if m else None


def norm_sha(path):
    b = open(path, 'rb').read().replace(b'\r\n', b'\n')
    return hashlib.sha256(b).hexdigest()


def blob_sha(repo, rel):
    r = git(repo, 'show', 'HEAD:' + rel, check=False)
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None


def stem_of(a):
    return re.sub(r'\.json$', '', str(a.get('data') or '').split('/')[-1])


def write_json_atomic(path, obj):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, path)


def validate_article_node(form_dir, data_paths):
    """form_logic.js の validateArticle で全memberを検査(UIと同一ロジック)"""
    js = ("const FL=require(process.argv[1]);const fs=require('fs');const out={};"
          "for(const p of process.argv.slice(2)){try{out[p]=FL.validateArticle(JSON.parse(fs.readFileSync(p,'utf8')))}catch(e){out[p]=['parse:'+e.message]}}"
          "console.log(JSON.stringify(out))")
    r = subprocess.run(['node', '-e', js, os.path.join(form_dir, 'form_logic.js')] + data_paths, capture_output=True)
    if r.returncode != 0:
        raise PublishError('node validateArticle failed: ' + r.stderr.decode('utf-8', 'replace')[:300])
    return json.loads(r.stdout.decode('utf-8'))


def load_index(path):
    if os.path.exists(path):
        d = json.load(open(path, encoding='utf-8'))
        if d.get('schema') != 'eigo_radio_batch_index_v1':
            raise PublishError('batches/index.json のschema不一致')
        return d
    return {'schema': 'eigo_radio_batch_index_v1', 'latest': None, 'batches': []}


def build_doc(repo, form_dir, bid, date, report_ref, members, test):
    rx = id_regex(form_dir)
    if not rx.match(bid or ''):
        raise PublishError('batch id形式不正(UI/er128と同一の正規表現): %r' % (bid,))
    if not members:
        raise PublishError('members が空')
    if len(set(members)) != len(members):
        raise PublishError('members に重複: ' + ','.join(sorted({m for m in members if members.count(m) > 1})))
    idx = json.load(open(os.path.join(form_dir, 'data', 'articles.json'), encoding='utf-8'))
    by_stem = {}
    for a in idx['articles']:
        if a.get('data'):
            by_stem[stem_of(a)] = a
    missing = [m for m in members if m not in by_stem]
    if missing:
        raise PublishError('members がarticles.jsonのdata stemに完全一致しない(slug一致・slug__level緩和なし): ' + ','.join(missing))
    keys = [by_stem[m]['slug'] + '__' + by_stem[m]['level'] for m in members]
    if len(set(keys)) != len(keys):
        raise PublishError('members の状態キー(slug__level)が重複')
    paths = [os.path.join(form_dir, 'data', by_stem[m]['data'].split('/')[-1]) for m in members]
    for p in paths:
        if not os.path.exists(p):
            raise PublishError('dataファイルが無い: ' + p)
    ve = validate_article_node(form_dir, paths)
    bad = {k: v for k, v in ve.items() if v}
    if bad:
        raise PublishError('validateArticle NG: ' + json.dumps(bad, ensure_ascii=False)[:300])
    shas = {}
    for m, p in zip(members, paths):
        rel = FORM_REL + '/data/' + os.path.basename(p)
        n = norm_sha(p)
        b = blob_sha(repo, rel)
        if b is None:
            raise PublishError('dataがgit未追跡(HEADに無い): ' + rel)
        if b != n:
            raise PublishError('dataが未commitの変更を含む(HEADのblobと不一致): ' + rel)
        shas[m] = n
    return {'schema': 'eigo_radio_batch_v1', 'id': bid, 'date': date, 'report_ref': report_ref, 'test': bool(test), 'members': list(members),
            'member_sha256': shas, 'created': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'asset_version': asset_version(form_dir)}


def commit_push(repo, files, msg, push):
    git(repo, 'add', '--', *files)
    st = git(repo, 'diff', '--cached', '--name-only').stdout.decode().split()
    extra = [x for x in st if x not in files]
    if extra:
        raise PublishError('想定外のstaged: ' + ','.join(extra))
    if not st:
        return 'no-change'
    git(repo, 'commit', '-m', msg + '\n\n' + TRAILER)
    if push:
        r = git(repo, 'push', 'origin', 'HEAD:main', check=False)
        if r.returncode != 0:
            git(repo, 'fetch', 'origin', 'main')
            rb = git(repo, 'rebase', 'origin/main', check=False)
            if rb.returncode != 0:
                git(repo, 'rebase', '--abort', check=False)
                raise PublishError('push rejected & rebase conflict(解決せず停止): ' + rb.stderr.decode('utf-8', 'replace')[:200])
            git(repo, 'push', 'origin', 'HEAD:main')
    return git(repo, 'rev-parse', 'HEAD').stdout.decode().strip()


def cmd_stage1(a):
    repo = a.repo
    form_dir = os.path.join(repo, FORM_REL)
    bdir = os.path.join(form_dir, 'data', 'batches')
    os.makedirs(bdir, exist_ok=True)
    members = [m.strip() for m in a.members.split(',') if m.strip()]
    doc = build_doc(repo, form_dir, a.id, a.date, a.report_ref, members, a.test)
    bpath = os.path.join(bdir, a.id + '.json')
    ipath = os.path.join(bdir, 'index.json')
    idx = load_index(ipath)
    if os.path.exists(bpath):
        old = json.load(open(bpath, encoding='utf-8'))
        if old.get('members') != doc['members'] or old.get('member_sha256') != doc['member_sha256'] or old.get('test') != doc['test']:
            raise PublishError('公開済みidと内容(members/データsha/test)が異なる。新しいidを使ってください(M10 不変性): ' + a.id)
        doc['created'] = old.get('created', doc['created'])
    write_json_atomic(bpath, doc)
    ent = {'id': a.id, 'date': a.date, 'report_ref': a.report_ref, 'n_sets': len(members), 'test': bool(a.test)}
    idx['batches'] = [b for b in idx['batches'] if b.get('id') != a.id] + [ent]
    write_json_atomic(ipath, idx)
    files = [FORM_REL + '/data/batches/' + a.id + '.json', FORM_REL + '/data/batches/index.json']
    res = {'stage': 'stage1', 'id': a.id, 'n_sets': len(members), 'files': files, 'latest': idx.get('latest')}
    if a.push:
        res['commit'] = commit_push(repo, files, a.msg or ('選定フォーム報告batch公開(stage1・latest不変): ' + a.id), True)
    print(json.dumps(res, ensure_ascii=False))
    return 0


def read_smoke(path, bid, av):
    r = json.load(open(path, encoding='utf-8'))
    if r.get('kind') != 'batch' or r.get('batch_id') != bid:
        raise PublishError('smoke結果が対象batchのものでない')
    if r.get('status') != 'PASS':
        raise PublishError('smoke未PASS: ' + str(r.get('fail_reason')))
    if r.get('asset_version') != av:
        raise PublishError('smoke時のUI版がローカルHEADと不一致')
    return r


def cmd_promote(a):
    repo = a.repo
    form_dir = os.path.join(repo, FORM_REL)
    ipath = os.path.join(form_dir, 'data', 'batches', 'index.json')
    idx = load_index(ipath)
    files = [FORM_REL + '/data/batches/index.json']
    if a.clear_latest:
        idx['latest'] = None
        write_json_atomic(ipath, idx)
        msg = a.msg or '選定フォーム: latest解除(検証後の原状復帰)'
    else:
        ent = next((b for b in idx['batches'] if b.get('id') == a.id), None)
        if not ent:
            raise PublishError('indexに未登録のid(先にstage1): ' + a.id)
        if ent.get('test') and not a.allow_test_latest:
            raise PublishError('test報告はlatestにしない')
        read_smoke(a.smoke_json, a.id, asset_version(form_dir))
        idx['latest'] = a.id
        write_json_atomic(ipath, idx)
        msg = a.msg or ('選定フォーム: latest更新(stage2・smoke PASS確認済み): ' + a.id)
    res = {'stage': 'promote', 'id': a.id, 'latest': idx['latest']}
    if a.push:
        res['commit'] = commit_push(repo, files, msg, True)
    print(json.dumps(res, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', default=os.path.abspath(os.path.join(HERE, '..')))
    sub = ap.add_subparsers(dest='cmd', required=True)
    s1 = sub.add_parser('stage1')
    s1.add_argument('--id', required=True)
    s1.add_argument('--date', required=True)
    s1.add_argument('--report-ref', required=True)
    s1.add_argument('--members', required=True, help='data stemのカンマ区切り(articles.jsonのdataファイル名stemに完全一致)')
    s1.add_argument('--test', action='store_true')
    s1.add_argument('--push', action='store_true')
    s1.add_argument('--msg', default='')
    s1.set_defaults(fn=cmd_stage1)
    s2 = sub.add_parser('promote')
    s2.add_argument('--id', default='')
    s2.add_argument('--smoke-json', default='')
    s2.add_argument('--allow-test-latest', action='store_true')
    s2.add_argument('--clear-latest', action='store_true')
    s2.add_argument('--push', action='store_true')
    s2.add_argument('--msg', default='')
    s2.set_defaults(fn=cmd_promote)
    a = ap.parse_args()
    try:
        return a.fn(a)
    except PublishError as e:
        print('PUBLISH ERROR: %s' % e)
        return 2


if __name__ == '__main__':
    sys.exit(main())
