# -*- coding: utf-8 -*-
"""
PM-TOKEN-EFFICIENCY-T1-OPEN-ITEMS-RESTRUCTURE-01

Deterministic verification that OPEN_ITEMS.md's giant-row restructuring
(Status-summary body + verbatim history moved to OPEN_ITEMS_HISTORY.md) is
lossless: for every split cell / header block, concatenating the moved
history text with the kept body text (in original left-to-right order),
after whitespace/newline normalization, reproduces the original text
character-for-character. Also cross-checks that occurrence counts of
management IDs / OPEN numbers / dates / URLs / file paths are unchanged
between the original file and the new body+history combined (after
excluding the small set of intentionally-added structural strings, which
are enumerated exactly below rather than inferred).

Original ("before") text is read from git HEAD (the pre-restructure commit
state on disk at task start), not from a separate backup file.

Usage: python er011_open_items_restructure_verify_01.py
Writes results JSON to er011_output/open_items_restructure_01/verify_result.json
"""
import re
import json
import subprocess
import sys
import os

REPO = os.path.dirname(os.path.abspath(__file__))
os.chdir(REPO)

CELL_LABELS = ['ID', '内容', '状態', '種類', 'Blocking', '次Action', '次Action(続き)']

WS_RE = re.compile(r'\s+')


def normalize(s):
    return WS_RE.sub('', s)


def git_show_original():
    # The commit that was HEAD before this restructuring task's own commit.
    # We look it up via git log for OPEN_ITEMS.md's previous version relative
    # to the current worktree by using 'HEAD' if this script runs BEFORE the
    # restructuring commit, otherwise the caller must pass a ref via argv.
    ref = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
    out = subprocess.run(['git', 'show', f'{ref}:OPEN_ITEMS.md'],
                          capture_output=True, cwd=REPO)
    if out.returncode != 0:
        raise SystemExit(f'git show failed: {out.stderr.decode("utf-8", "replace")}')
    return out.stdout.decode('utf-8')


def load_manifest():
    with open('er011_output/open_items_restructure_01/manifest.json', encoding='utf-8') as f:
        return json.load(f)


def extract_history_section(history_text, heading):
    pat = re.compile(r'^## ' + re.escape(heading) + r'\n', re.M)
    m = pat.search(history_text)
    if not m:
        return None
    start = m.end()
    m2 = re.search(r'^## ', history_text[start:], re.M)
    end = start + m2.start() if m2 else len(history_text)
    return history_text[start:end]


def extract_history_subsection(section_text, label, method):
    heading = f'### {label}欄(旧、split method={method})\n'
    idx = section_text.find(heading)
    if idx == -1:
        return None
    start = idx + len(heading)
    m2 = re.search(r'^### ', section_text[start:], re.M)
    end = start + m2.start() if m2 else len(section_text)
    return section_text[start:end]


def split_row_cells(row_text):
    s = row_text.strip()
    leading_pipe = s.startswith('|')
    trailing_pipe = s.endswith('|')
    inner = s[1:] if leading_pipe else s
    if trailing_pipe:
        inner = inner[:-1]
    return inner.split('|')


def main():
    original_text = git_show_original()
    original_lines = original_text.splitlines(keepends=True)

    with open('OPEN_ITEMS.md', encoding='utf-8') as f:
        new_body_lines = f.readlines()
    with open('OPEN_ITEMS_HISTORY.md', encoding='utf-8') as f:
        history_text = f.read()

    manifest = load_manifest()

    results = {'header': {}, 'rows': {}, 'summary': {}}
    mismatches = []

    # ---- HEADER check ----
    header_meta = manifest['header']
    orig_start, orig_end = header_meta['history_lines'].split('-')
    orig_history_original = ''.join(original_lines[int(orig_start) - 1:int(orig_end)])
    hist_section = extract_history_section(history_text, 'HEADER_HISTORY')
    ok = hist_section is not None and normalize(hist_section) == normalize(orig_history_original)
    results['header'] = {
        'orig_len': len(orig_history_original),
        'extracted_len': len(hist_section) if hist_section else 0,
        'match': ok,
    }
    if not ok:
        mismatches.append('HEADER_HISTORY')

    # kept header (lines 1-65) must appear unchanged (after stripping the
    # one intentionally-added SSOT note block) inside new body's start.
    orig_kept = ''.join(original_lines[0:65])
    new_body_full = ''.join(new_body_lines)
    table_marker_idx = new_body_full.find('| ID | 内容 | 状態 | 種類 | Blocking | 次Action |')
    new_head_region = new_body_full[:table_marker_idx] if table_marker_idx != -1 else new_body_full
    # remove the two intentionally-added structural note blocks (exact,
    # known strings) before comparing, since they are authorized additions
    # (not original content) per the task design instructions.
    new_head_region_no_notes = re.sub(
        r'\n> \*\*本ファイルの位置づけ\*\*: OPEN_ITEMS\.mdは未確定事項の唯一の管理場所である.*?'
        r'切り出し先である。\n', '', new_head_region, flags=re.S)
    new_head_region_no_notes = re.sub(
        r'\*\*履歴全文\(直前の記録・その前の記録・さらに前の記録、'
        r'PM-CLOSEOUT-CONSOLIDATION-70以前の全件、原文のまま移動\): '
        r'`OPEN_ITEMS_HISTORY\.md#HEADER_HISTORY`参照\*\*\n', '', new_head_region_no_notes)
    ok2 = normalize(orig_kept) in normalize(new_head_region_no_notes)
    results['header']['kept_head_contained'] = ok2
    if not ok2:
        mismatches.append('HEADER_KEPT_1_65')

    # ---- ROW checks ----
    new_row_by_line = {}
    for line in new_body_lines:
        pass
    # build line-number indexed map for new body (same physical line count/order
    # is preserved except content changes on target lines)
    new_row_index_by_oid = {}
    for i, line in enumerate(new_body_lines):
        if line.startswith('| OPEN-'):
            m = re.match(r'\| (OPEN-\d+) \|', line)
            if m:
                new_row_index_by_oid[m.group(1)] = i

    for oid, meta in manifest['rows'].items():
        ln = meta['line']
        orig_row = original_lines[ln - 1].rstrip('\n')
        if oid not in new_row_index_by_oid:
            mismatches.append(f'{oid}:NOT_FOUND_IN_NEW_BODY')
            results['rows'][oid] = {'row_match': False, 'cells': [], 'error': 'row not found in new body'}
            continue
        new_row = new_body_lines[new_row_index_by_oid[oid]].rstrip('\n')
        orig_cells = split_row_cells(orig_row)
        new_cells = split_row_cells(new_row)
        hist_section_row = extract_history_section(history_text, oid)
        cell_results = []
        row_ok = True
        for i, orig_cell in enumerate(orig_cells):
            if i == 0:
                new_cell = new_cells[i] if i < len(new_cells) else ''
                cok = normalize(new_cell) == normalize(orig_cell)
                cell_results.append({'cell': i, 'label': 'ID', 'match': cok})
                row_ok = row_ok and cok
                continue
            label = CELL_LABELS[i] if i < len(CELL_LABELS) else f'col{i}'
            split_meta = next((c for c in meta['cells_split'] if c['label'] == label), None)
            new_cell = new_cells[i] if i < len(new_cells) else ''
            # strip the trailing pointer note from the last cell before comparing
            new_cell_stripped = re.sub(
                r'\s*\(履歴全文: `OPEN_ITEMS_HISTORY\.md#' + re.escape(oid) + r'`\)\s*$',
                '', new_cell)
            if split_meta is None:
                cok = normalize(new_cell_stripped) == normalize(orig_cell)
                cell_results.append({'cell': i, 'label': label, 'match': cok, 'split': False})
                row_ok = row_ok and cok
            else:
                method = split_meta['method']
                hist_sub = extract_history_subsection(hist_section_row, label, method) if hist_section_row else None
                recon = (hist_sub or '') + new_cell_stripped
                cok = normalize(recon) == normalize(orig_cell)
                cell_results.append({'cell': i, 'label': label, 'match': cok, 'split': True,
                                      'orig_len': len(orig_cell), 'hist_len': len(hist_sub or ''),
                                      'body_len': len(new_cell_stripped)})
                row_ok = row_ok and cok
        results['rows'][oid] = {'row_match': row_ok, 'cells': cell_results}
        if not row_ok:
            mismatches.append(oid)

    # ---- Global ID/date/URL/filepath count check ----
    ID_RE = re.compile(r'\bOPEN-\d+\b')
    MGMT_ID_RE = re.compile(r'\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,}\b')
    DATE_RE = re.compile(r'\b20\d\d-\d\d-\d\d\b')
    URL_RE = re.compile(r'https?://\S+')
    PATH_RE = re.compile(r'`[A-Za-z0-9_./\\-]+\.(?:py|json|jsonl|md|txt|wav|html|csv)`')

    def counts(text):
        return {
            'OPEN-xxx': len(ID_RE.findall(text)),
            'mgmt_id': len(MGMT_ID_RE.findall(text)),
            'date': len(DATE_RE.findall(text)),
            'url': len(URL_RE.findall(text)),
            'filepath': len(PATH_RE.findall(text)),
        }

    orig_counts = counts(original_text)

    # Known added strings (exact, enumerated) removed before counting the
    # "new files combined" side, so the comparison is apples-to-apples.
    added_row_notes = []
    for oid in manifest['rows']:
        added_row_notes.append(f' (履歴全文: `OPEN_ITEMS_HISTORY.md#{oid}`)')
    new_body_text = new_body_full
    # Remove the SSOT note block (delimited by the fixed marker text) and the
    # header pointer line, and each row's pointer note, by regex (structural,
    # known-fixed content only).
    new_body_no_notes = re.sub(
        r'\n> \*\*本ファイルの位置づけ\*\*: OPEN_ITEMS\.mdは未確定事項の唯一の管理場所である.*?'
        r'切り出し先である。\n', '', new_body_text, flags=re.S)
    new_body_no_notes = re.sub(
        r'\*\*履歴全文\(直前の記録・その前の記録・さらに前の記録、'
        r'PM-CLOSEOUT-CONSOLIDATION-70以前の全件、原文のまま移動\): '
        r'`OPEN_ITEMS_HISTORY\.md#HEADER_HISTORY`参照\*\*\n', '', new_body_no_notes)
    for note in added_row_notes:
        new_body_no_notes = new_body_no_notes.replace(note, '')

    history_no_headings = re.sub(r'^#.*\n', '', history_text, flags=re.M)
    history_no_boilerplate = re.sub(
        r'> \*\*本ファイルの位置づけ\*\*: 未確定事項の管理場所は引き続き.*?対応する。\n',
        '', history_no_headings, flags=re.S)

    combined_new = new_body_no_notes + history_no_boilerplate
    new_counts = counts(combined_new)

    results['summary']['counts_original'] = orig_counts
    results['summary']['counts_new_combined_minus_added_notes'] = new_counts
    results['summary']['counts_match'] = orig_counts == new_counts

    results['summary']['mismatches'] = mismatches
    results['summary']['total_rows_checked'] = len(manifest['rows'])
    results['summary']['total_rows_ok'] = sum(1 for oid in manifest['rows'] if results['rows'][oid]['row_match'])
    results['summary']['header_ok'] = results['header']['match'] and results['header']['kept_head_contained']
    results['summary']['ALL_PASS'] = (len(mismatches) == 0) and results['summary']['counts_match']

    os.makedirs('er011_output/open_items_restructure_01', exist_ok=True)
    with open('er011_output/open_items_restructure_01/verify_result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(json.dumps(results['summary'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
