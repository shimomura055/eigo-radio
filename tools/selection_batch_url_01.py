# -*- coding: utf-8 -*-
"""選定フォームの利用者向けURL発行 共通関数(SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_04、Opus M14)。

HR依頼書・報告でユーザーへ出す選定URLは、必ず本関数(issue_batch_url)経由で作る。
live smoke結果JSONを読み、(1)kind=batch (2)batch id一致 (3)status=PASS (4)asset_versionがローカルHEAD(form_logic.js)と一致
(5)test報告でない(allow_test=Trueの検証用途を除く)ときだけ ?batch=<id> のURLを返す。条件を満たさなければ例外(=URLを出せない)。
`?a=`単体URL(旧形式)は発行しない。"""
import json
import os
import re

BASE_DEFAULT = 'https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/'
_FORM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'user_test', 'selection_form_v3')


class UrlNotIssuable(Exception):
    pass


def _local_asset_version(form_dir):
    s = open(os.path.join(form_dir, 'form_logic.js'), encoding='utf-8').read()
    m = re.search(r"var ASSET_VERSION = '([^']+)'", s)
    return m.group(1) if m else None


def _id_re(form_dir):
    s = open(os.path.join(form_dir, 'form_logic.js'), encoding='utf-8').read()
    m = re.search(r"var BATCH_ID_RE = /(.+?)/;", s)
    return re.compile(m.group(1))


def issue_batch_url(batch_id, smoke_json_path, base=BASE_DEFAULT, form_dir=None, allow_test=False):
    form_dir = form_dir or _FORM_DIR
    if not _id_re(form_dir).match(batch_id or ''):
        raise UrlNotIssuable('batch id形式不正: %r' % (batch_id,))
    try:
        r = json.load(open(smoke_json_path, encoding='utf-8'))
    except Exception as e:  # noqa: BLE001
        raise UrlNotIssuable('smoke結果JSONを読めない: %s' % e)
    if r.get('schema') != 'eigo_radio_selection_live_smoke_v1':
        raise UrlNotIssuable('smoke結果JSONのschema不一致')
    if r.get('kind') != 'batch' or r.get('batch_id') != batch_id:
        raise UrlNotIssuable('smoke結果が対象batchのものでない(kind=%s id=%s)' % (r.get('kind'), r.get('batch_id')))
    if r.get('status') != 'PASS':
        raise UrlNotIssuable('live smokeがPASSでない: %s' % r.get('fail_reason'))
    av = _local_asset_version(form_dir)
    if r.get('asset_version') != av:
        raise UrlNotIssuable('smoke時のUI版(%s)がローカルHEAD(%s)と不一致 -> 再smoke要' % (r.get('asset_version'), av))
    if r.get('base_url') != base:
        raise UrlNotIssuable('smoke対象のbase_urlが違う')
    # test報告は利用者へ出さない(検証専用)
    idx_path = os.path.join(form_dir, 'data', 'batches', batch_id + '.json')
    try:
        doc = json.load(open(idx_path, encoding='utf-8'))
    except Exception as e:  # noqa: BLE001
        raise UrlNotIssuable('batchファイルを読めない: %s' % e)
    if doc.get('test') and not allow_test:
        raise UrlNotIssuable('test報告のURLは利用者へ提示しない(allow_test=Trueは検証用途のみ)')
    return base + 'index.html?batch=' + batch_id


if __name__ == '__main__':
    import sys
    try:
        print(issue_batch_url(sys.argv[1], sys.argv[2], allow_test=('--allow-test' in sys.argv)))
    except UrlNotIssuable as e:
        print('NOT ISSUABLE: %s' % e)
        sys.exit(2)
