# -*- coding: utf-8 -*-
"""
PM-TOKEN-EFFICIENCY-T3A-DECISION-LOG-RESTRUCTURE-01

Deterministic verification that DECISION_LOG.md's restructuring
(recent-body + verbatim-history-split via er011_decision_log_restructure_01.py)
is lossless:

(i) Reconstruction: concatenating DECISION_LOG_HISTORY.md's moved chunks
    with DECISION_LOG.md's kept chunks (per the manifest's exact line
    ranges), after removing the enumerated known-added strings (pointer
    note, index section, history header/section boilerplate) and after
    whitespace normalization, reproduces the original (git HEAD)
    DECISION_LOG.md character-for-character.
(ii) Entry count: 231 content entries + 13 header chain entries + 1
     footer, matches manifest's kept+moved counts.
(iii) Global counts of management IDs, dates, URLs, and file paths are
      unchanged between the original and the new body+history combined
      (after excluding the enumerated added strings).

Original ("before") text is read from git HEAD, not from a backup file.

Usage: python er011_decision_log_restructure_verify_01.py [ref]
Writes results JSON to
er011_output/decision_log_restructure_01/verify_result.json
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
os.chdir(REPO)

MANIFEST_PATH = 'er011_output/decision_log_restructure_01/manifest.json'
RESULT_PATH = 'er011_output/decision_log_restructure_01/verify_result.json'

WS_RE = re.compile(r'\s+')


def normalize(s):
    return WS_RE.sub('', s)


def git_show_original(ref):
    out = subprocess.run(['git', 'show', f'{ref}:DECISION_LOG.md'],
                          capture_output=True, cwd=REPO)
    if out.returncode != 0:
        raise SystemExit(f'git show failed: {out.stderr.decode("utf-8", "replace")}')
    return out.stdout.decode('utf-8')


def load_manifest():
    with open(MANIFEST_PATH, encoding='utf-8') as f:
        return json.load(f)


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
    original_text = git_show_original(ref)
    original_lines = original_text.splitlines(keepends=True)

    with open('DECISION_LOG.md', encoding='utf-8') as f:
        new_body_text = f.read()
    with open('DECISION_LOG_HISTORY.md', encoding='utf-8') as f:
        history_text = f.read()

    manifest = load_manifest()
    added = manifest['added_strings']

    results = {'checks': {}, 'summary': {}}
    mismatches = []

    # ---- (i) reconstruction check, built directly from manifest line ranges
    #      against the ORIGINAL file (independent of how the new files are
    #      internally organized) ----
    def seg(lines_range):
        start, end = lines_range
        return ''.join(original_lines[start - 1:end])

    recon_parts = []
    h = manifest['header']
    recon_parts.append(seg(h['pre_chain_lines']))
    recon_parts.append(seg(h['newest_chain_entry_lines']))
    recon_parts.append(seg(h['older_chain_region_lines']))
    recon_parts.append(seg(h['post_chain_footnote_lines']))
    for e in manifest['moved_entries']:
        recon_parts.append(seg(e['lines']))
    for e in manifest['kept_entries']:
        recon_parts.append(seg(e['lines']))
    recon_parts.append(seg(manifest['footer_lines']))
    reconstructed_from_manifest = ''.join(recon_parts)

    ok_manifest_recon = normalize(reconstructed_from_manifest) == normalize(original_text)
    results['checks']['manifest_line_ranges_reconstruct_original'] = ok_manifest_recon
    if not ok_manifest_recon:
        mismatches.append('MANIFEST_LINE_RANGES_RECONSTRUCT_ORIGINAL')

    # ---- (i-b) reconstruction check using the ACTUAL new files on disk,
    #      by stripping the known-added strings and re-normalizing ----
    new_body_no_added = new_body_text.replace(added['chain_pointer_note'], '')
    new_body_no_added = new_body_no_added.replace(added['index_section'], '')

    history_no_added = history_text.replace(added['history_header'], '')
    history_no_added = history_no_added.replace(added['history_chain_section_heading'], '')
    history_no_added = history_no_added.replace(added['history_chain_trailing_sep'], '', 1)

    # The body, with the index section and pointer note removed, should equal:
    #   pre_chain + newest_chain_entry + post_chain_footnote + kept_entries + footer
    # The history, with header/section boilerplate removed, should equal:
    #   older_chain_region + moved_entries
    combined_actual = new_body_no_added + history_no_added
    # order differs from the original file order (moved entries relocated),
    # so compare as normalized *sets* is unsafe (order matters for a real
    # diff) -- instead verify by re-ordering: body-without-index contains
    # [pre,newest,footnote,kept*,footer] and history-without-boilerplate
    # contains [older_chain, moved*]; reassemble in ORIGINAL order and compare.
    reassembled_original_order = (
        seg(h['pre_chain_lines']) + seg(h['newest_chain_entry_lines'])
    )
    # find where these pieces are inside new_body_no_added / history_no_added
    # by direct verbatim containment checks per chunk (robust to exact
    # concatenation-boundary whitespace) rather than trying to slice strings.
    def contains_norm(haystack, needle):
        return normalize(needle) in normalize(haystack)

    per_chunk_checks = {}
    per_chunk_checks['pre_chain'] = contains_norm(new_body_no_added, seg(h['pre_chain_lines']))
    per_chunk_checks['newest_chain_entry'] = contains_norm(new_body_no_added, seg(h['newest_chain_entry_lines']))
    per_chunk_checks['post_chain_footnote'] = contains_norm(new_body_no_added, seg(h['post_chain_footnote_lines']))
    per_chunk_checks['footer'] = contains_norm(new_body_no_added, seg(manifest['footer_lines']))
    per_chunk_checks['older_chain_region'] = contains_norm(history_no_added, seg(h['older_chain_region_lines']))

    for i, e in enumerate(manifest['kept_entries']):
        # index-prefixed key: some early-era headings reuse the same ID
        # text multiple times (verbatim, not a bug), so the key must be
        # unique per entry (by position), not just by ID, or duplicate
        # IDs would silently overwrite/hide an earlier entry's check.
        per_chunk_checks[f"kept:{i}:{e['id']}:{e['lines'][0]}"] = contains_norm(
            new_body_no_added, seg(e['lines']))
    for i, e in enumerate(manifest['moved_entries']):
        per_chunk_checks[f"moved:{i}:{e['id']}:{e['lines'][0]}"] = contains_norm(
            history_no_added, seg(e['lines']))

    all_chunks_ok = all(per_chunk_checks.values())
    results['checks']['all_chunks_present_verbatim_in_correct_file'] = all_chunks_ok
    results['checks']['chunk_count'] = len(per_chunk_checks)
    if not all_chunks_ok:
        mismatches.extend([k for k, v in per_chunk_checks.items() if not v])

    # normalized total-length sanity check (combined actual, minus known
    # additions, should equal original in normalized length)
    len_ok = len(normalize(combined_actual)) == len(normalize(original_text))
    results['checks']['normalized_length_match'] = len_ok
    results['checks']['normalized_len_original'] = len(normalize(original_text))
    results['checks']['normalized_len_combined_actual_minus_added'] = len(normalize(combined_actual))
    if not len_ok:
        mismatches.append('NORMALIZED_LENGTH_MISMATCH')

    # ---- (ii) entry counts ----
    results['checks']['content_entries_total'] = manifest['content_entries_total']
    results['checks']['content_entries_total_ok'] = manifest['content_entries_total'] == 231
    results['checks']['kept_count'] = len(manifest['kept_entries'])
    results['checks']['moved_count'] = len(manifest['moved_entries'])
    results['checks']['kept_plus_moved_ok'] = (
        len(manifest['kept_entries']) + len(manifest['moved_entries'])
        == manifest['content_entries_total']
    )
    if not results['checks']['content_entries_total_ok']:
        mismatches.append('CONTENT_ENTRIES_TOTAL')
    if not results['checks']['kept_plus_moved_ok']:
        mismatches.append('KEPT_PLUS_MOVED_COUNT')

    # ---- (iii) global ID / date / URL / filepath counts ----
    MGMT_ID_RE = re.compile(r'\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,}\b')
    OPEN_ID_RE = re.compile(r'\bOPEN-\d+\b')
    DATE_RE = re.compile(r'\b20\d\d-\d\d-\d\d\b')
    URL_RE = re.compile(r'https?://\S+')
    PATH_RE = re.compile(r'`[A-Za-z0-9_./\\-]+\.(?:py|json|jsonl|md|txt|wav|html|csv)`')

    def counts(text):
        return {
            'mgmt_id': len(MGMT_ID_RE.findall(text)),
            'OPEN-xxx': len(OPEN_ID_RE.findall(text)),
            'date': len(DATE_RE.findall(text)),
            'url': len(URL_RE.findall(text)),
            'filepath': len(PATH_RE.findall(text)),
        }

    orig_counts = counts(original_text)
    new_counts = counts(new_body_no_added + history_no_added)
    results['summary']['counts_original'] = orig_counts
    results['summary']['counts_new_combined_minus_added'] = new_counts
    counts_match = orig_counts == new_counts
    results['summary']['counts_match'] = counts_match
    if not counts_match:
        mismatches.append('GLOBAL_COUNTS_MISMATCH')

    # ---- size summary ----
    results['summary']['original_chars'] = len(original_text)
    results['summary']['new_body_chars'] = len(new_body_text)
    results['summary']['new_history_chars'] = len(history_text)
    results['summary']['body_reduction_pct'] = round(
        100 * (1 - len(new_body_text) / len(original_text)), 1)

    results['summary']['mismatches'] = mismatches
    results['summary']['ALL_PASS'] = len(mismatches) == 0

    os.makedirs(os.path.dirname(RESULT_PATH), exist_ok=True)
    with open(RESULT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(json.dumps(results['summary'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
