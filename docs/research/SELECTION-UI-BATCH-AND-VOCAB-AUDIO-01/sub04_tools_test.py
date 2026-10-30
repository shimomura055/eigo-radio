# -*- coding: utf-8 -*-
"""委任_04: publish tool / URL発行関数 / smoke結果読取の否定系test(Opus M1/M6/M7/M10/M14)。一時gitリポジトリ上で実行(公開物・本リポジトリは変更しない、API 0)。"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
FORM_REL = 'user_test/selection_form_v3'
sys.path.insert(0, os.path.join(REPO, 'tools'))
import publish_selection_batch_01 as P  # noqa: E402
import selection_batch_url_01 as U  # noqa: E402

STEMS = ['moon_shrinking__a2__prod', 'moon_shrinking__b1b__prod', 'melos__b1b__prod']


def run(*a, cwd=None):
    return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')


class PublishTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='sub04tools_')
        cls.repo = os.path.join(cls.tmp, 'r')
        fd = os.path.join(cls.repo, FORM_REL)
        os.makedirs(os.path.join(fd, 'data'))
        src = os.path.join(REPO, FORM_REL)
        for f in ('form_logic.js',):
            shutil.copy(os.path.join(src, f), fd)
        for s in STEMS:
            shutil.copy(os.path.join(src, 'data', s + '.json'), os.path.join(fd, 'data'))
        idx = json.load(open(os.path.join(src, 'data', 'articles.json'), encoding='utf-8'))
        idx['articles'] = [a for a in idx['articles'] if a.get('data') and os.path.basename(a['data'])[:-5] in STEMS]
        json.dump(idx, open(os.path.join(fd, 'data', 'articles.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        run('git', 'init', '-q', cls.repo)
        run('git', '-C', cls.repo, 'config', 'user.email', 't@t')
        run('git', '-C', cls.repo, 'config', 'user.name', 't')
        run('git', '-C', cls.repo, 'config', 'core.autocrlf', 'false')
        run('git', '-C', cls.repo, 'add', '-A')
        run('git', '-C', cls.repo, 'commit', '-q', '-m', 'base')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def cli(self, *args):
        r = run(sys.executable, os.path.join(REPO, 'tools', 'publish_selection_batch_01.py'), '--repo', self.repo, *args)
        return r.returncode, (r.stdout + r.stderr)

    def stage1(self, bid, members, *extra):
        return self.cli('stage1', '--id', bid, '--date', '2026-10-30', '--report-ref', 'x', '--members', ','.join(members), '--test', *extra)

    def test_01_normal_writes_batch_and_index_latest_unchanged(self):
        rc, out = self.stage1('t-normal-01', STEMS)
        self.assertEqual(rc, 0, out)
        fd = os.path.join(self.repo, FORM_REL, 'data', 'batches')
        doc = json.load(open(os.path.join(fd, 't-normal-01.json'), encoding='utf-8'))
        self.assertEqual(doc['members'], STEMS)
        self.assertEqual(set(doc['member_sha256']), set(STEMS))
        self.assertTrue(all(len(v) == 64 for v in doc['member_sha256'].values()))
        idx = json.load(open(os.path.join(fd, 'index.json'), encoding='utf-8'))
        self.assertIsNone(idx['latest'])
        self.assertEqual([b['id'] for b in idx['batches']], ['t-normal-01'])

    def test_02_bad_inputs_refused_and_nothing_written(self):
        fd = os.path.join(self.repo, FORM_REL, 'data', 'batches')
        before = set(os.listdir(fd)) if os.path.isdir(fd) else set()
        cases = [('../evil', STEMS), ('A-bad', STEMS), ('ab', STEMS), ('t-dup-001', [STEMS[0], STEMS[0]]), ('t-empty-1', []),
                 ('t-loose-01', ['moon_shrinking']), ('t-loose-02', ['moon_shrinking__a2']), ('t-miss-001', [STEMS[0], 'nosuch__a2__prod'])]
        for bid, ms in cases:
            rc, out = self.stage1(bid, ms)
            self.assertEqual(rc, 2, (bid, ms, out))
            self.assertIn('PUBLISH ERROR', out)
        after = set(os.listdir(fd)) if os.path.isdir(fd) else set()
        self.assertEqual(before, after, '拒否時にbatchファイルを書かない')

    def test_03_published_id_is_immutable(self):
        self.assertEqual(self.stage1('t-immut-01', STEMS[:2])[0], 0)
        self.assertEqual(self.stage1('t-immut-01', STEMS[:2])[0], 0, '同一内容の再実行は冪等')
        rc, out = self.stage1('t-immut-01', STEMS)
        self.assertEqual(rc, 2)
        self.assertIn('新しいid', out)

    def test_04_uncommitted_data_change_refused(self):
        p = os.path.join(self.repo, FORM_REL, 'data', STEMS[2] + '.json')
        orig = open(p, 'rb').read()
        try:
            open(p, 'wb').write(orig.replace(b'\n', b'\n ', 1))
            rc, out = self.stage1('t-dirty-01', STEMS)
            self.assertEqual(rc, 2, out)
            self.assertIn('未commit', out)
        finally:
            open(p, 'wb').write(orig)

    def test_05_promote_requires_passing_smoke_for_same_id_and_never_test_by_default(self):
        self.assertEqual(self.stage1('t-prom-001', STEMS)[0], 0)
        d = os.path.join(self.tmp, 'smoke')
        os.makedirs(d, exist_ok=True)
        av = P.asset_version(os.path.join(self.repo, FORM_REL))

        def smoke(**kw):
            r = {'schema': 'eigo_radio_selection_live_smoke_v1', 'kind': 'batch', 'batch_id': 't-prom-001', 'status': 'PASS', 'asset_version': av, 'base_url': P.BASE_DEFAULT}
            r.update(kw)
            p = os.path.join(d, 's%d.json' % len(os.listdir(d)))
            json.dump(r, open(p, 'w', encoding='utf-8'))
            return p
        # test報告はそもそもlatestにしない
        rc, out = self.cli('promote', '--id', 't-prom-001', '--smoke-json', smoke())
        self.assertEqual(rc, 2)
        self.assertIn('test報告はlatestにしない', out)
        # 非test報告を作る
        rc, out = self.cli('stage1', '--id', 't-real-001', '--date', '2026-10-30', '--report-ref', 'x', '--members', ','.join(STEMS))
        self.assertEqual(rc, 0, out)
        for bad in (dict(status='FAIL', fail_reason='x'), dict(batch_id='other-id'), dict(asset_version='old-version'), dict(kind='latest')):
            rc, out = self.cli('promote', '--id', 't-real-001', '--smoke-json', smoke(batch_id='t-real-001', **bad) if 'batch_id' not in bad else smoke(**bad))
            self.assertEqual(rc, 2, (bad, out))
        rc, out = self.cli('promote', '--id', 'not-in-index', '--smoke-json', smoke(batch_id='not-in-index'))
        self.assertEqual(rc, 2)
        idx = json.load(open(os.path.join(self.repo, FORM_REL, 'data', 'batches', 'index.json'), encoding='utf-8'))
        self.assertIsNone(idx['latest'], '未検証idはlatestに載らない')
        rc, out = self.cli('promote', '--id', 't-real-001', '--smoke-json', smoke(batch_id='t-real-001'))
        self.assertEqual(rc, 0, out)
        idx = json.load(open(os.path.join(self.repo, FORM_REL, 'data', 'batches', 'index.json'), encoding='utf-8'))
        self.assertEqual(idx['latest'], 't-real-001')
        rc, out = self.cli('promote', '--clear-latest')
        self.assertEqual(rc, 0, out)
        idx = json.load(open(os.path.join(self.repo, FORM_REL, 'data', 'batches', 'index.json'), encoding='utf-8'))
        self.assertIsNone(idx['latest'])


class UrlIssueTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='sub04url_')
        self.fd = os.path.join(self.tmp, 'form')
        os.makedirs(os.path.join(self.fd, 'data', 'batches'))
        shutil.copy(os.path.join(REPO, FORM_REL, 'form_logic.js'), self.fd)
        self.av = U._local_asset_version(self.fd)
        json.dump({'schema': 'eigo_radio_batch_v1', 'id': 'rep-real-1', 'members': ['a'], 'test': False}, open(os.path.join(self.fd, 'data', 'batches', 'rep-real-1.json'), 'w'))
        json.dump({'schema': 'eigo_radio_batch_v1', 'id': 'rep-test-1', 'members': ['a'], 'test': True}, open(os.path.join(self.fd, 'data', 'batches', 'rep-test-1.json'), 'w'))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def smoke(self, bid, **kw):
        r = {'schema': 'eigo_radio_selection_live_smoke_v1', 'kind': 'batch', 'batch_id': bid, 'status': 'PASS', 'asset_version': self.av, 'base_url': U.BASE_DEFAULT}
        r.update(kw)
        p = os.path.join(self.tmp, 's.json')
        json.dump(r, open(p, 'w'))
        return p

    def test_issues_batch_url_only_when_all_conditions_hold(self):
        self.assertEqual(U.issue_batch_url('rep-real-1', self.smoke('rep-real-1'), form_dir=self.fd), U.BASE_DEFAULT + 'index.html?batch=rep-real-1')

    def test_refuses_each_unmet_condition(self):
        bad = [('rep-real-1', dict(status='FAIL')), ('rep-real-1', dict(asset_version='old')), ('rep-real-1', dict(base_url='http://x/')), ('rep-real-1', dict(kind='latest')),
               ('rep-real-1', dict(schema='x')), ('rep-real-1', dict(batch_id='other-zz'))]
        for bid, kw in bad:
            with self.assertRaises(U.UrlNotIssuable, msg=str(kw)):
                U.issue_batch_url(bid, self.smoke(bid, **kw), form_dir=self.fd)
        for bid in ('../x', 'A-bad', ''):
            with self.assertRaises(U.UrlNotIssuable):
                U.issue_batch_url(bid, self.smoke('rep-real-1'), form_dir=self.fd)
        with self.assertRaises(U.UrlNotIssuable):
            U.issue_batch_url('rep-real-1', os.path.join(self.tmp, 'nonexistent.json'), form_dir=self.fd)

    def test_test_report_url_is_not_issued_to_users(self):
        with self.assertRaises(U.UrlNotIssuable):
            U.issue_batch_url('rep-test-1', self.smoke('rep-test-1'), form_dir=self.fd)
        self.assertIn('?batch=rep-test-1', U.issue_batch_url('rep-test-1', self.smoke('rep-test-1'), form_dir=self.fd, allow_test=True))

    def test_never_returns_legacy_a_url(self):
        u = U.issue_batch_url('rep-real-1', self.smoke('rep-real-1'), form_dir=self.fd)
        self.assertNotIn('?a=', u)


if __name__ == '__main__':
    unittest.main()
