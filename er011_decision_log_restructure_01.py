# -*- coding: utf-8 -*-
"""
PM-TOKEN-EFFICIENCY-T3A-DECISION-LOG-RESTRUCTURE-01

Deterministic, content-preserving restructuring of DECISION_LOG.md.

DECISION_LOG.md has two distinct regions:

1. Header region (original lines 1-200): a title, a management-ID label
   ("ER-PM-001"), and a reverse-chronological *chain* of 13
   "**最終更新...**"-prefixed update paragraphs (newest first, each a
   single physical line for the 12 most recent, the 13th/oldest one
   wrapped across many lines), followed by a small static footnote
   ("**区分について...**") and a "---" separator.

2. Body region (original lines 201-11499): 231 chronological entries,
   each starting with a "## <management ID>: <title>" heading (in
   ascending date order, oldest first), followed by a final small
   "## 参照元" footer section.

This script performs a *lossless, verbatim* split:

- Header: keep only the single newest chain entry in DECISION_LOG.md;
  move the other 12 (older) chain entries verbatim to
  DECISION_LOG_HISTORY.md under a "## ER-PM-001_CHAIN" section, in
  their original order. Add one fixed pointer-note line in the body
  (the only new prose in the whole operation).
- Body: keep the most recent KEEP_N_ENTRIES chronological entries
  verbatim in DECISION_LOG.md (in original order), plus the "## 参照元"
  footer (always kept). Move the older (231 - KEEP_N_ENTRIES) entries
  verbatim, in original order, to DECISION_LOG_HISTORY.md.
- Insert one new "## 索引(Index): 全Decisionエントリ一覧" section in
  DECISION_LOG.md body, listing every one of the 231 entries by its
  *original, verbatim* heading text plus a pointer to whether it is
  kept in-body or moved to DECISION_LOG_HISTORY.md. No summarization:
  each index line reuses the entry's own original heading text.

No text is deleted, reworded, or summarized. Every original line ends
up in exactly one of {DECISION_LOG.md, DECISION_LOG_HISTORY.md}
(except the small set of enumerated new pointer/index strings, which
are additions, not replacements).

A manifest (er011_output/decision_log_restructure_01/manifest.json) is
written recording exact line ranges moved, for use by the companion
verification script (er011_decision_log_restructure_verify_01.py).

Usage: python er011_decision_log_restructure_01.py
"""
import json
import os
import re

REPO = os.path.dirname(os.path.abspath(__file__))
os.chdir(REPO)

SRC = 'DECISION_LOG.md'
BODY_OUT = 'DECISION_LOG.md'
HISTORY_OUT = 'DECISION_LOG_HISTORY.md'
MANIFEST_DIR = 'er011_output/decision_log_restructure_01'
MANIFEST_PATH = os.path.join(MANIFEST_DIR, 'manifest.json')

KEEP_N_ENTRIES = 25  # most recent chronological entries kept verbatim in body

CHAIN_POINTER_NOTE = (
    '**履歴全文(直前の記録・その前の記録、以下さらに前の記録、'
    '合計12件、原文のまま移動): `DECISION_LOG_HISTORY.md`の'
    '`## ER-PM-001_CHAIN`節参照**\n'
)

HISTORY_HEADER = (
    '# DECISION_LOG_HISTORY — DECISION_LOG.mdの履歴全文(切り出し)\n'
    '\n'
    '> **本ファイルの位置づけ**: 確定した意思決定の管理場所は引き続き'
    '`DECISION_LOG.md`のみである。本ファイルは`DECISION_LOG.md`が'
    '肥大化したため、古いエントリ(ER-PM-001ヘッダーチェーンの旧12件、'
    'および本体の古い決定エントリ)の**履歴全文をそのまま**切り出した'
    '先であり、別の管理場所ではない。要約・言い換え・削除は一切行って'
    'いない(原文のまま)。\n'
    '\n'
    '---\n'
    '\n'
)


def extract_id(heading_line):
    # heading_line looks like "## <ID>: <title...>\n"
    body = heading_line[3:].rstrip('\n')
    return body.split(':', 1)[0].strip()


def extract_title_block(lines, start_idx):
    """Return the verbatim heading text (heading line + any wrapped
    continuation lines) up to (not including) the first blank line,
    used only for the Index (no summarization: exact original text)."""
    end = start_idx + 1
    while end < len(lines) and lines[end].strip() != '':
        end += 1
    return ''.join(lines[start_idx:end])


def main():
    with open(SRC, encoding='utf-8') as f:
        original_text = f.read()
    lines = original_text.splitlines(keepends=True)

    # ---- locate structural boundaries ----
    heading_idx = [i for i, l in enumerate(lines) if l.startswith('## ')]
    first_heading = heading_idx[0]  # start of body region (content entries)
    footer_idx = heading_idx[-1]    # "## 参照元"
    assert lines[footer_idx].strip() == '## 参照元', lines[footer_idx]

    chain_starts = [i for i, l in enumerate(lines) if l.startswith('**最終更新')]
    assert len(chain_starts) == 13, f'expected 13 chain entries, found {len(chain_starts)}'
    kubun_idx = [i for i, l in enumerate(lines) if l.startswith('**区分について')]
    assert len(kubun_idx) == 1
    kubun_idx = kubun_idx[0]

    # ---- header split ----
    pre_chain = lines[0:chain_starts[0]]          # title, blank, ER-PM-001 label
    newest_chain_entry = lines[chain_starts[0]:chain_starts[1]]
    older_chain_region = lines[chain_starts[1]:kubun_idx]   # 12 older chain entries, verbatim
    post_chain_footnote = lines[kubun_idx:first_heading]     # 区分について ... --- ... blank

    # ---- body content entries (excluding footer) ----
    content_entries = []  # list of dict(id, start, end) 0-based [start,end)
    for i, idx in enumerate(heading_idx[:-1]):  # exclude footer heading itself
        end = heading_idx[i + 1]
        content_entries.append({
            'id': extract_id(lines[idx]),
            'start': idx,
            'end': end,
        })
    assert len(content_entries) == 231, len(content_entries)

    kept_entries = content_entries[-KEEP_N_ENTRIES:]
    moved_entries = content_entries[:-KEEP_N_ENTRIES]

    # ---- build Index section (verbatim heading text per entry, no summarization) ----
    index_lines = [
        '## 索引(Index): 全Decisionエントリ一覧\n',
        '\n',
        '> 以下は全231件の決定エントリを原文タイトル(見出し行、原文のまま)で'
        '列挙した索引である。要約は行っていない。「本ファイル内」は本体に'
        '残る直近' + str(KEEP_N_ENTRIES) + '件、「履歴」は`DECISION_LOG_HISTORY.md`'
        'へ原文のまま移動した件を指す。管理IDでのGrepはどちらのファイルに'
        'あっても直接ヒットする。\n',
        '\n',
    ]
    for e in moved_entries:
        title_block = extract_title_block(lines, e['start']).rstrip('\n')
        index_lines.append(f"- [履歴] {title_block}\n")
    for e in kept_entries:
        title_block = extract_title_block(lines, e['start']).rstrip('\n')
        index_lines.append(f"- [本ファイル内] {title_block}\n")
    index_lines.append('\n---\n\n')

    # ---- assemble new DECISION_LOG.md ----
    new_body_parts = []
    new_body_parts.extend(pre_chain)
    new_body_parts.extend(newest_chain_entry)
    new_body_parts.append(CHAIN_POINTER_NOTE)
    new_body_parts.extend(post_chain_footnote)
    new_body_parts.extend(index_lines)
    for e in kept_entries:
        new_body_parts.extend(lines[e['start']:e['end']])
    new_body_parts.extend(lines[footer_idx:])  # "## 参照元" ... end of file

    new_body_text = ''.join(new_body_parts)

    # ---- assemble DECISION_LOG_HISTORY.md ----
    history_parts = [HISTORY_HEADER]
    history_parts.append('## ER-PM-001_CHAIN\n\n')
    history_parts.extend(older_chain_region)
    history_parts.append('\n---\n\n')
    for e in moved_entries:
        history_parts.extend(lines[e['start']:e['end']])
    history_text = ''.join(history_parts)

    with open(BODY_OUT, 'w', encoding='utf-8', newline='') as f:
        f.write(new_body_text)
    with open(HISTORY_OUT, 'w', encoding='utf-8', newline='') as f:
        f.write(history_text)

    # ---- manifest ----
    manifest = {
        'source_char_len': len(original_text),
        'keep_n_entries': KEEP_N_ENTRIES,
        'header': {
            'pre_chain_lines': [1, chain_starts[0]],
            'newest_chain_entry_lines': [chain_starts[0] + 1, chain_starts[1]],
            'older_chain_region_lines': [chain_starts[1] + 1, kubun_idx],
            'post_chain_footnote_lines': [kubun_idx + 1, first_heading],
        },
        'content_entries_total': len(content_entries),
        'kept_entries': [
            {'id': e['id'], 'lines': [e['start'] + 1, e['end']]} for e in kept_entries
        ],
        'moved_entries': [
            {'id': e['id'], 'lines': [e['start'] + 1, e['end']]} for e in moved_entries
        ],
        'footer_lines': [footer_idx + 1, len(lines)],
        'added_strings': {
            'chain_pointer_note': CHAIN_POINTER_NOTE,
            'history_header': HISTORY_HEADER,
            'history_chain_section_heading': '## ER-PM-001_CHAIN\n\n',
            'history_chain_trailing_sep': '\n---\n\n',
            'index_section': ''.join(index_lines),
        },
        'new_body_char_len': len(new_body_text),
        'new_history_char_len': len(history_text),
    }
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print('original:', len(original_text))
    print('new body:', len(new_body_text))
    print('new history:', len(history_text))
    print('reduction: {:.1f}%'.format(100 * (1 - len(new_body_text) / len(original_text))))


if __name__ == '__main__':
    main()
