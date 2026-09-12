#!/usr/bin/env python3
"""
er011_pm_agent_read_audit_01.py

PM運用ツール(read-only監査)。Production非関与。

目的: Claude開発Line(Fable/Sonnet/Opus/Haiku)のtranscript(JSONL)から、
Read/Grep/Glob/Bash呼び出しと、その結果文字数を機械集計し、
- どのAgentが、どの管理IDで、どのファイル(分類)を、何文字読んだか
- 同一ファイルの再読込(重複)がどこで起きているか
- Agent間(Fable→Sonnet→Opus)の重複読込量
を実測する。

入力:
- Sonnet/Opus/Haiku subagent転記: <TEMP>/claude/<project>/<session_id>/tasks/*.output (JSONL)
- Fable本体転記: ~/.claude/projects/<project>/<session_id>.jsonl (JSONL, isSidechain=false の行がFable本体)

出力:
- er011_output/pm_agent_read_audit_01/per_call.jsonl  (呼び出し単位の生データ)
- er011_output/pm_agent_read_audit_01/per_agent_task_summary.json (集計)
- er011_output/pm_agent_read_audit_01/summary.md (人間可読サマリ)

注意: これは実測ツールであり、tool_resultの文字数を「概算token」に変換する際は
文字数/2.2という粗い近似を使う(課金tokenではないと明記)。usage.input_tokens等の
実際のAPI課金token情報がmessage内にあればそれも別途記録する(assistant message
のusageフィールド、キャッシュ込み)。
"""
import json
import os
import re
import sys
import hashlib
from collections import defaultdict

# ---------------------------------------------------------------------------
# 対象転記ファイル(実測対象。ユーザー指示の代表タスクをカバーする既知セッションに限定)
# ---------------------------------------------------------------------------

TEMP_BASE = r"C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio"
PROJECTS_BASE = r"C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio"

# session_id -> label (何を代表するセッションか、レポート用)
TARGET_SESSIONS = {
    "294958fe-da6e-491c-8a02-4f864d8195c8": "current_session_2026-09-11_12",
    "a146ec25-1821-49c1-a6f2-3b7ad423406a": "prev_session_2026-09-10",
    "eba13a8b-6eec-4381-909a-3a2d71be7123": "older_session_opus_l2_examples",
}

# 個別に含める Opus task ファイル(agentId)。このセッションのtasksフォルダは
# 巨大(35MB)なので全件処理はせず、実Opus呼び出しの2件のみに限定する。
OPUS_TASK_WHITELIST = {
    "a15dd268df8bc04e5",  # FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01 (opus-consultant)
    "a2cf98b0e56f13ba1",  # FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01 (opus-consultant)
}

OUT_DIR = r"C:\Users\tensh\eigo-radio\er011_output\pm_agent_read_audit_01"

# ---------------------------------------------------------------------------
# ファイル分類
# ---------------------------------------------------------------------------

def classify_path(path):
    if not path:
        return "unknown"
    p = path.replace("\\", "/")
    pl = p.lower()
    if re.search(r'_history\.md$', pl):
        return "history"
    if re.search(r'/(current_spec|decision_log|open_items)\.md$', pl) or \
       re.match(r'^(current_spec|decision_log|open_items)\.md$', os.path.basename(pl)):
        return "ssot_huge"
    if re.search(r'_report\.md$', pl):
        return "report"
    if '/docs/pm/' in pl or pl.startswith('docs/pm/'):
        return "governance_pm_docs"
    if re.search(r'_output/', pl) and re.search(r'er0\d+', pl):
        return "trial_output"
    if re.search(r'\.claude[/\\]agents', pl) or '/.claude/agents' in pl:
        return "agent_definition"
    if re.match(r'^er0\d+[a-z0-9_]*\.py$', os.path.basename(pl)):
        return "production_code_er0x_py"
    if pl.endswith('.py'):
        return "other_py"
    if pl.endswith('.md'):
        return "other_md"
    if pl.endswith('.json') or pl.endswith('.jsonl'):
        return "other_json"
    return "other"


# 既知の巨大SSOT/History/Governanceファイル名(Bashコマンド内の言及検出用)
KNOWN_FILENAME_PATTERNS = [
    (r'CURRENT_SPEC\.md', 'ssot_huge'),
    (r'DECISION_LOG\.md', 'ssot_huge'),
    (r'OPEN_ITEMS_HISTORY\.md', 'history'),
    (r'OPEN_ITEMS\.md', 'ssot_huge'),
    (r'PM_GOVERNANCE\.md', 'governance_pm_docs'),
    (r'ACTIVE_TASK\.md', 'governance_pm_docs'),
    (r'PM_BRIEF\.md', 'governance_pm_docs'),
    (r'RESULT_PACKET\.md', 'governance_pm_docs'),
    (r'MODEL_ROUTING_TRIAL_LOG\.md', 'governance_pm_docs'),
    (r'HISTORY_INDEX\.md', 'history'),
    (r'[A-Za-z0-9\-]+_REPORT\.md', 'report'),
    (r'er0\d+[A-Za-z0-9_]*\.py', 'production_code_er0x_py'),
    (r'er0\d+[a-z0-9_]*_output/[^\s"\']*', 'trial_output'),
]
KNOWN_FILENAME_RE = [(re.compile(pat), cat) for pat, cat in KNOWN_FILENAME_PATTERNS]

BASH_READ_CMD_RE = re.compile(
    r'\b(cat|type|head|tail|sed\s+-n|Get-Content|less|more)\b', re.IGNORECASE)


def bash_command_read_targets(command):
    """Bashコマンド文字列から、読込対象らしきファイル参照を抽出し分類する。
    戻り値: (is_read_like: bool, matched_categories: list[str], matched_files: list[str])
    完全なshell解析ではなく正規表現ベースの近似(既知の限界としてREPORTに明記)。
    """
    if not command:
        return False, [], []
    is_read_like = bool(BASH_READ_CMD_RE.search(command)) or ' grep ' in (' ' + command)
    matches = []
    cats = []
    for rx, cat in KNOWN_FILENAME_RE:
        for m in rx.finditer(command):
            matches.append(m.group(0))
            cats.append(cat)
    return is_read_like, cats, matches


def tool_result_text_len(content):
    """tool_result content (list or str) から文字数を算出。"""
    if content is None:
        return 0
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        total = 0
        for c in content:
            if isinstance(c, dict):
                if c.get('type') == 'text':
                    total += len(c.get('text', '') or '')
                elif 'text' in c:
                    total += len(c.get('text', '') or '')
        return total
    return 0


MGMT_ID_RE = re.compile(r'管理ID[:：]\s*`?([A-Za-z0-9][A-Za-z0-9\-]{5,120})')


def extract_mgmt_id(text):
    if not text:
        return None
    m = MGMT_ID_RE.search(text)
    if m:
        return m.group(1).strip()
    return None


def first_user_text(message):
    content = message.get('content')
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict) and c.get('type') == 'text':
                parts.append(c.get('text', ''))
            elif isinstance(c, str):
                parts.append(c)
        return '\n'.join(parts)
    return ''


# ---------------------------------------------------------------------------
# コアパーサ: 1つの .output (subagent) または .jsonl (Fable本体) を処理
# ---------------------------------------------------------------------------

def parse_transcript(path, source_label, agent_id_hint=None, fable_mode=False):
    """
    戻り値: list of call-dict (per_call.jsonl 用のレコード)
    fable_mode=True の場合、isSidechain=true の行(=subagentの内部)はスキップし、
    Fable自身のtool_use/tool_resultとTask委任のみを拾う。
    """
    records = []
    mgmt_id = None
    model_seen = set()
    pending_tool_use = {}  # tool_use_id -> {"name":..., "input":..., "line_idx":...}

    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return records

    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(d, dict):
            continue

        is_sidechain = d.get('isSidechain', False)
        if fable_mode and is_sidechain:
            # Fable本体モードでは、subagent内部行はスキップ(別途subagent転記で処理)
            continue
        if (not fable_mode) and not is_sidechain:
            continue

        dtype = d.get('type')

        if dtype == 'user':
            msg = d.get('message', {})
            txt = first_user_text(msg)
            found = extract_mgmt_id(txt)
            if found:
                # Fable本体/長いsubagent転記は複数タスクをまたぐことがあるため、
                # 新しい「管理ID:」宣言が出るたびに更新する(直近の宣言を適用)。
                mgmt_id = found

        if dtype == 'assistant':
            msg = d.get('message', {})
            model = msg.get('model')
            if model:
                model_seen.add(model)
            content = msg.get('content', [])
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get('type') == 'tool_use':
                        tool_use_id = c.get('id')
                        pending_tool_use[tool_use_id] = {
                            'name': c.get('name'),
                            'input': c.get('input', {}),
                            'line_idx': idx,
                            'timestamp': d.get('timestamp'),
                        }
                    elif isinstance(c, dict) and c.get('type') == 'text':
                        # Task delegation text sometimes appears as plain text before tool_use;
                        # not needed for read audit.
                        pass

        if dtype == 'user':
            msg = d.get('message', {})
            content = msg.get('content')
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get('type') == 'tool_result':
                        tool_use_id = c.get('tool_use_id')
                        result_len = tool_result_text_len(c.get('content'))
                        tu = pending_tool_use.pop(tool_use_id, None)
                        if tu is None:
                            continue
                        name = tu['name']
                        tinput = tu['input'] or {}
                        rec = {
                            'source_label': source_label,
                            'agent_id': agent_id_hint,
                            'mgmt_id': mgmt_id,
                            'model': sorted(model_seen)[0] if model_seen else None,
                            'tool': name,
                            'timestamp': d.get('timestamp'),
                            'result_chars': result_len,
                        }
                        if name == 'Read':
                            fp = tinput.get('file_path')
                            offset = tinput.get('offset')
                            limit = tinput.get('limit')
                            rec['file_path'] = fp
                            rec['offset'] = offset
                            rec['limit'] = limit
                            rec['is_full_read'] = (offset is None and limit is None)
                            rec['category'] = classify_path(fp)
                            rec['dedup_key'] = json.dumps(
                                ['READ', fp, offset, limit], ensure_ascii=False)
                            rec['file_key'] = fp
                        elif name == 'Grep':
                            pat = tinput.get('pattern')
                            gpath = tinput.get('path')
                            omode = tinput.get('output_mode')
                            rec['pattern'] = pat
                            rec['path'] = gpath
                            rec['output_mode'] = omode
                            rec['category'] = classify_path(gpath) if gpath else 'unknown'
                            rec['dedup_key'] = json.dumps(
                                ['GREP', pat, gpath, omode], ensure_ascii=False)
                            rec['file_key'] = gpath
                        elif name == 'Glob':
                            pat = tinput.get('pattern')
                            gpath = tinput.get('path')
                            rec['pattern'] = pat
                            rec['path'] = gpath
                            rec['category'] = 'glob'
                            rec['dedup_key'] = json.dumps(
                                ['GLOB', pat, gpath], ensure_ascii=False)
                            rec['file_key'] = gpath or pat
                        elif name == 'Bash':
                            cmd = tinput.get('command', '')
                            is_read_like, cats, matched_files = bash_command_read_targets(cmd)
                            rec['command'] = cmd[:300]
                            rec['is_read_like'] = is_read_like
                            primary_cat = cats[0] if cats else ('bash_other_readlike' if is_read_like else 'bash_nonread')
                            rec['category'] = primary_cat
                            rec['matched_files'] = matched_files[:5]
                            cmd_hash = hashlib.sha1(cmd.encode('utf-8', 'ignore')).hexdigest()[:12]
                            rec['dedup_key'] = json.dumps(['BASH', cmd_hash], ensure_ascii=False)
                            rec['file_key'] = matched_files[0] if matched_files else None
                        else:
                            # Other tools (Write, Edit, Task, etc.) - not a "read"; skip from read audit
                            # but Task tool_use captures delegation prompt size -> record separately.
                            if name == 'Agent':
                                # Fable -> Sonnet/Opus/Haiku 委任(SDK内部名は"Agent"、
                                # ユーザー向け表記のTask toolに相当)
                                prompt = tinput.get('prompt', '') or tinput.get('description', '')
                                rec['category'] = 'task_delegation_prompt'
                                rec['delegation_chars'] = len(prompt)
                                rec['subagent_type'] = tinput.get('subagent_type')
                                found_mgmt = extract_mgmt_id(prompt)
                                rec['delegation_mgmt_id'] = found_mgmt
                                rec['dedup_key'] = json.dumps(['AGENT_DELEGATION', hashlib.sha1(prompt.encode('utf-8','ignore')).hexdigest()[:12]], ensure_ascii=False)
                                records.append(rec)
                                if found_mgmt:
                                    # 以降のFable側の読込(次の委任まで)もこの管理IDの文脈として扱う
                                    mgmt_id = found_mgmt
                            continue
                        records.append(rec)
    return records


# ---------------------------------------------------------------------------
# メイン集計
# ---------------------------------------------------------------------------

def find_subagent_files(session_id):
    tdir = os.path.join(TEMP_BASE, session_id, 'tasks')
    if not os.path.isdir(tdir):
        return []
    out = []
    for fn in os.listdir(tdir):
        if fn.endswith('.output'):
            fp = os.path.join(tdir, fn)
            if os.path.getsize(fp) == 0:
                continue
            out.append(fp)
    return out


def main():
    all_records = []

    for session_id, label in TARGET_SESSIONS.items():
        subfiles = find_subagent_files(session_id)
        if session_id == "eba13a8b-6eec-4381-909a-3a2d71be7123":
            # 巨大セッション: Opus実呼び出し2件のみに限定(理由: er011スクリプトdocstring参照)
            subfiles = [f for f in subfiles
                        if os.path.splitext(os.path.basename(f))[0] in OPUS_TASK_WHITELIST]
        for fp in subfiles:
            agent_id = os.path.splitext(os.path.basename(fp))[0]
            recs = parse_transcript(fp, f"subagent:{label}", agent_id_hint=agent_id, fable_mode=False)
            all_records.extend(recs)

        # Fable本体(メインセッションjsonl)
        main_jsonl = os.path.join(PROJECTS_BASE, f"{session_id}.jsonl")
        if os.path.isfile(main_jsonl):
            recs = parse_transcript(main_jsonl, f"fable:{label}", agent_id_hint="fable", fable_mode=True)
            all_records.extend(recs)

    # per_call.jsonl 書き出し
    os.makedirs(OUT_DIR, exist_ok=True)
    per_call_path = os.path.join(OUT_DIR, 'per_call.jsonl')
    with open(per_call_path, 'w', encoding='utf-8') as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    # ---- 集計: per_agent_task_summary ----
    # グループ: (mgmt_id, source_label) -> stats
    by_task_agent = defaultdict(lambda: {
        'total_chars': 0, 'calls': 0, 'by_category': defaultdict(int),
        'by_tool': defaultdict(int), 'full_reads': 0, 'partial_reads': 0,
        'delegation_chars': 0,
    })

    # ファイルレベル再読込判定用: (mgmt_id, file_key or dedup file identity) -> list of (timestamp, source_label, chars)
    file_occurrences = defaultdict(list)

    for r in all_records:
        mgmt = r.get('mgmt_id') or 'UNKNOWN_MGMT_ID'
        src = r.get('source_label')
        key = (mgmt, src)
        agg = by_task_agent[key]
        if r.get('category') == 'task_delegation_prompt':
            agg['delegation_chars'] += r.get('delegation_chars', 0)
            agg['calls'] += 1
            continue
        chars = r.get('result_chars', 0)
        agg['total_chars'] += chars
        agg['calls'] += 1
        agg['by_category'][r.get('category', 'unknown')] += chars
        agg['by_tool'][r.get('tool')] += chars
        if r.get('tool') == 'Read':
            if r.get('is_full_read'):
                agg['full_reads'] += 1
            else:
                agg['partial_reads'] += 1

        fk = r.get('file_key')
        if fk:
            norm_fk = fk.replace('\\', '/').lower()
            occ_key = (mgmt, norm_fk)
            file_occurrences[occ_key].append({
                'timestamp': r.get('timestamp'),
                'source_label': src,
                'chars': chars,
                'tool': r.get('tool'),
                'category': r.get('category'),
            })

    # 重複読込(同一mgmt_id内・同一ファイルキーの2回目以降)
    duplicate_chars_by_task = defaultdict(int)
    cross_agent_duplicate_chars_by_task = defaultdict(int)
    reread_examples = []

    for (mgmt, fk), occs in file_occurrences.items():
        if len(occs) <= 1:
            continue
        occs_sorted = sorted(occs, key=lambda o: (o['timestamp'] or ''))
        first_src = occs_sorted[0]['source_label']
        dup_chars_this_file = 0
        cross_dup_chars_this_file = 0
        for o in occs_sorted[1:]:
            dup_chars_this_file += o['chars']
            if o['source_label'] != first_src:
                cross_dup_chars_this_file += o['chars']
        duplicate_chars_by_task[mgmt] += dup_chars_this_file
        cross_agent_duplicate_chars_by_task[mgmt] += cross_dup_chars_this_file
        if dup_chars_this_file > 500:
            reread_examples.append({
                'mgmt_id': mgmt,
                'file_key': fk,
                'occurrences': len(occs_sorted),
                'sources': [o['source_label'] for o in occs_sorted],
                'total_dup_chars': dup_chars_this_file,
                'cross_agent_dup_chars': cross_dup_chars_this_file,
            })

    reread_examples.sort(key=lambda x: -x['total_dup_chars'])

    # JSON化用に defaultdict -> dict
    summary_out = {}
    for (mgmt, src), agg in by_task_agent.items():
        summary_out.setdefault(mgmt, {})[src] = {
            'total_chars': agg['total_chars'],
            'approx_tokens': round(agg['total_chars'] / 2.2),
            'calls': agg['calls'],
            'by_category_chars': dict(agg['by_category']),
            'by_tool_chars': dict(agg['by_tool']),
            'full_reads': agg['full_reads'],
            'partial_reads': agg['partial_reads'],
            'delegation_chars_sent_to_subagents': agg['delegation_chars'],
        }

    for mgmt in summary_out:
        summary_out[mgmt]['_duplicate_chars_within_task'] = duplicate_chars_by_task.get(mgmt, 0)
        summary_out[mgmt]['_cross_agent_duplicate_chars_within_task'] = cross_agent_duplicate_chars_by_task.get(mgmt, 0)

    with open(os.path.join(OUT_DIR, 'per_agent_task_summary.json'), 'w', encoding='utf-8') as f:
        json.dump({
            'by_mgmt_id': summary_out,
            'top_reread_files': reread_examples[:40],
        }, f, ensure_ascii=False, indent=2)

    # ---- summary.md ----
    lines = []
    lines.append('# er011_pm_agent_read_audit_01 — 実測サマリ (Phase 1)')
    lines.append('')
    lines.append(f'総呼び出し件数(read系): {sum(1 for r in all_records if r.get("category")!="task_delegation_prompt")}')
    lines.append(f'総委任(Task)件数: {sum(1 for r in all_records if r.get("category")=="task_delegation_prompt")}')
    total_chars_all = sum(r.get('result_chars', 0) for r in all_records if r.get('category') != 'task_delegation_prompt')
    lines.append(f'総読込文字数(全ソース合算、Fable+Sonnet+Opus): {total_chars_all:,} 字 (概算 {round(total_chars_all/2.2):,} token)')
    lines.append('')
    lines.append('## 管理ID別サマリ(上位、総読込文字数順)')
    mgmt_totals = []
    for mgmt, per_src in summary_out.items():
        t = sum(v['total_chars'] for k, v in per_src.items() if isinstance(v, dict) and 'total_chars' in v)
        mgmt_totals.append((mgmt, t))
    mgmt_totals.sort(key=lambda x: -x[1])
    for mgmt, t in mgmt_totals[:25]:
        lines.append(f'- {mgmt}: {t:,} 字')
        for src, v in summary_out[mgmt].items():
            if not isinstance(v, dict) or 'total_chars' not in v:
                continue
            lines.append(f'    - {src}: {v["total_chars"]:,} 字 ({v["calls"]}回呼び出し, full_read={v["full_reads"]}, partial={v["partial_reads"]}, delegation_sent={v["delegation_chars_sent_to_subagents"]:,}字)')
        dup = summary_out[mgmt].get('_duplicate_chars_within_task', 0)
        cross = summary_out[mgmt].get('_cross_agent_duplicate_chars_within_task', 0)
        lines.append(f'    - 重複読込(同一ファイル再読込)文字数: {dup:,} / うちAgent間重複: {cross:,}')
    lines.append('')
    lines.append('## 再読込(同一管理ID内・同一ファイル)上位40件')
    for ex in reread_examples[:40]:
        lines.append(f"- [{ex['mgmt_id']}] {ex['file_key']} — {ex['occurrences']}回読込, 重複{ex['total_dup_chars']:,}字(Agent間重複{ex['cross_agent_dup_chars']:,}字), sources={ex['sources']}")

    with open(os.path.join(OUT_DIR, 'summary.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Wrote {len(all_records)} records to {per_call_path}")
    print(f"Summary: {os.path.join(OUT_DIR, 'summary.md')}")


if __name__ == '__main__':
    main()
