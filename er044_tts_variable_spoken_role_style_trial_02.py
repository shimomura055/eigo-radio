# ============================================================
# er044_tts_variable_spoken_role_style_trial_02.py
# TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02(Trial、Production実装なし)
# ============================================================
# 性質: Trial専用script。Production正式path(er0*.py既存ファイル)は
# 一切変更しない。既存Production TTS関数(voice01/news_tail_fix/n3_tts)を
# style_prefix_override引数付きでそのまま呼ぶ(EN側)。JA側は
# er038_tts_all_spoken_role_style_trial_01.generate_ja_role_style
# (Task Bが実装済み、変更禁止・importのみ)をそのまま再利用する。
#
# 詳細根拠: docs/pm/design_tts_variable_spoken_role_style_trial_02.md
#
# 重要な発見(§1-2): delegationが「J0=現状」と想定した日本語style
# 「落ち着いた、自然な話し言葉で」は、実は現行Productionには一切配線
# されていない(Task Bが導入したTrial限定の新規style)。現行Production
# JAは常にp9a.JAPANESE_STYLE_PREFIX(長文instruction)を使う(style
# override機構自体が存在しない)。本scriptのJ0はこの実測値を採用する
# (真のProduction現状)。
#
# --stage all/run_tts_stage全体は本scriptには実装しない(前回インシデント
# 再発防止)。segment×pattern単位の直接関数呼び出しのみを提供する。
from __future__ import annotations

import argparse
import contextlib
import hashlib
import html
import json
import os
import re
import shutil
import wave

try:
    import lameenc
    _HAS_LAMEENC = True
except ImportError:
    _HAS_LAMEENC = False

import er002_common as common
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er019_family_x_audio_production_runner_01 as fx_runner
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er038_tts_all_spoken_role_style_trial_01 as t01

MANAGEMENT_ID = "TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02"

# ------------------------------------------------------------
# JA J0(真のProduction現状、design doc §2で実測確認、逐語)
# ------------------------------------------------------------
import er003_b1_p9a_audio as p9a  # noqa: E402

J0_STYLE_JA = p9a.JAPANESE_STYLE_PREFIX  # Production実値そのまま参照(改変しない)

J_PATTERN_STYLES = {
    "J0": J0_STYLE_JA,
    "J1": "落ち着いた、自然な話し言葉で。意味の流れに合わせて軽く抑揚をつけてください。",
    "J2": "落ち着いた、自然な話し言葉で。強調点や話の転換に応じて抑揚をつけてください。大げさにしないでください。",
    "J3": "落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。"
          "演技がかった話し方は避けてください。",
}
for _p, _s in J_PATTERN_STYLES.items():
    if _p != "J0":
        common.assert_no_wpm_specification(_s)

E_PATTERN_STYLES = {
    "FULL_STORY": {
        "E0": "calm, steady news narration",
        "E1": "calm, steady news narration, with a touch of natural inflection that follows the meaning.",
        "E2": "calm, steady news narration with natural emphasis at key points and turns; not dramatic.",
        "E3": "calm, steady news narration, naturally expressive at key points, contrasts, and the "
              "conclusion; understated, not theatrical.",
    },
    "IN_ONE_LINE": {
        "E0": "concise, clear",
        "E1": "concise, clear, with a natural closing tone.",
        "E2": "concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.",
        "E3": "concise, clear, with a slightly more expressive, confident closing landing; understated, "
              "not theatrical.",
    },
    "TOPIC_INTRO": {
        "E0": "brief, clear, engaging news topic introduction",
        "E1": "brief, clear, engaging news topic introduction, with a touch of natural lift.",
        "E2": "brief, clear, engaging news topic introduction with natural emphasis on the topic; not "
              "dramatic.",
        "E3": "brief, clear, engaging news topic introduction, naturally expressive but understated; not "
              "theatrical, not a trailer voice.",
    },
}
for _role, _pmap in E_PATTERN_STYLES.items():
    for _p, _s in _pmap.items():
        common.assert_no_wpm_specification(_s)

JA_SEGMENTS_REQUIRED = ("preview", "comment_1", "comment_2")
JA_SEGMENTS_OPTIONAL = ("comment_3", "comment_4")
EN_SEGMENTS_REQUIRED = ("full_story_part1", "in_one_line")
EN_SEGMENTS_OPTIONAL = ("topic_intro",)

_EN_SEGMENT_ROLE = {
    "full_story_part1": "FULL_STORY", "full_story_part2": "FULL_STORY", "full_story_part3": "FULL_STORY",
    "in_one_line": "IN_ONE_LINE", "topic_intro": "TOPIC_INTRO",
}

# ------------------------------------------------------------
# J0/E0 reuse元(design doc §1-1/§1-3、read-onlyでコピーするのみ)
# ------------------------------------------------------------
J0_REUSE_SOURCE_DIR = (
    "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/"
    "hormuz__run_06_flashlite_full_kp/a2/narration")
E0_REUSE_SOURCE_DIR = "er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/narration"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _reuse_copy(src: str, dst: str, style_used: str, role: str, canonical_text: str, note: str) -> dict:
    if not os.path.exists(src):
        return {"status": "STOPPED", "reason": f"reuse対象の音声が見つかりません: {src}"}
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    return {
        "status": "OK", "reused": True, "reused_from": src, "path": dst,
        "style_prefix_used": style_used, "role": role, "canonical_text": canonical_text,
        "sha256": _sha256(dst), "note": note,
    }


@contextlib.contextmanager
def trial_master_audio_store(root_dir: str):
    """t01.trial_master_audio_store()と同一機構(Production Storeは
    一切読み書きしない、本Trial専用path)。t01側の実装をそのまま使う。"""
    with t01.trial_master_audio_store(root_dir):
        yield


# ------------------------------------------------------------
# JA generation(J1-J3のみ、J0はreuse)
# ------------------------------------------------------------
def generate_ja_pattern_segment(text: str, out_path: str, pattern: str, tts_backend: str,
                                 known_key_phrase_terms=None) -> dict:
    style = J_PATTERN_STYLES[pattern]
    with cl.segment_context(f"vr2_{pattern}"):
        r = t01.generate_ja_role_style(
            text, out_path, style, "Aoede", n3_tts._generate_a2_japanese_minimal_instruction,
            tts_backend, max_extra_chars=40, known_key_phrase_terms=known_key_phrase_terms)
    r["canonical_text"] = text
    r["style_prefix_used"] = style
    r["pattern"] = pattern
    return r


# ------------------------------------------------------------
# EN generation(E1-E3のみ、E0はreuse)
# ------------------------------------------------------------
def generate_en_pattern_segment(segment_name: str, text: str, out_path: str, pattern: str,
                                 tts_backend: str) -> dict:
    role = _EN_SEGMENT_ROLE[segment_name]
    style = E_PATTERN_STYLES[role][pattern]
    with cl.segment_context(f"vr2_{pattern}"):
        if segment_name == "topic_intro":
            r = voice01.generate_charon_english(
                n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text)), out_path,
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(
                    "topic_intro"),
                enable_pronunciation_resolver=True, style_prefix_override=style, tts_backend=tts_backend)
        else:
            disfluency_qa = (segment_name == "in_one_line")
            r = news_tail_fix.generate_news_narration_wide_margin(
                n3_tts.tts_safe_news_en(text), out_path,
                disfluency_qa=disfluency_qa,
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(
                    segment_name),
                enable_repetition_qa=(segment_name in fx_runner._BODY_SEGMENT_NAMES),
                enable_pronunciation_resolver=True, style_prefix_override=style, tts_backend=tts_backend)
    r["canonical_text"] = text
    r["style_prefix_used"] = style
    r["pattern"] = pattern
    r["role"] = role
    return r


# ------------------------------------------------------------
# Orchestration(segment×pattern単位、部分実行のみ)
# ------------------------------------------------------------
def run_ja_segment(theme_out_dir: str, segment_name: str, patterns: list, tts_backend: str) -> dict:
    out_dir = f"{theme_out_dir}/a2"
    narration_dir = f"{out_dir}/narration_vr2"
    os.makedirs(narration_dir, exist_ok=True)
    support = load_json(f"{theme_out_dir}/a2/a2_support_texts.json")
    text = support[segment_name]
    results = {}
    trial_store_dir = f"{theme_out_dir}/master_store"
    with trial_master_audio_store(trial_store_dir):
        for pattern in patterns:
            out_path = f"{narration_dir}/{segment_name}_{pattern}.wav"
            if pattern == "J0":
                src = f"{J0_REUSE_SOURCE_DIR}/{segment_name}.wav"
                results[pattern] = _reuse_copy(
                    src, out_path, J0_STYLE_JA, "PREVIEW" if segment_name == "preview" else "COMMENT",
                    text,
                    "真のProduction現状音声をread-onlyでreuse(design doc §1-3、"
                    "hormuz__run_06_flashlite_full_kp、asr_verified=true実測確認済み、"
                    "style override機構自体が現行Productionに存在しないため生成コード"
                    "パスは実質同一)。")
            else:
                results[pattern] = generate_ja_pattern_segment(text, out_path, pattern, tts_backend)
    return {"segment": segment_name, "language": "ja", "results": results}


def run_en_segment(theme_out_dir: str, segment_name: str, patterns: list, tts_backend: str) -> dict:
    out_dir = f"{theme_out_dir}/b1b"
    narration_dir = f"{out_dir}/narration_vr2"
    os.makedirs(narration_dir, exist_ok=True)
    parts = load_json(f"{theme_out_dir}/b1b/parts.json")
    if segment_name == "topic_intro":
        text = f"Today's topic is {parts['title']}."
    else:
        text = parts[{"full_story_part1": "part1", "in_one_line": "in_one_line"}[segment_name]]
    role = _EN_SEGMENT_ROLE[segment_name]
    results = {}
    trial_store_dir = f"{theme_out_dir}/master_store"
    with trial_master_audio_store(trial_store_dir):
        for pattern in patterns:
            out_path = f"{narration_dir}/{segment_name}_{pattern}.wav"
            if pattern == "E0":
                src = f"{E0_REUSE_SOURCE_DIR}/{segment_name}.wav"
                results[pattern] = _reuse_copy(
                    src, out_path, E_PATTERN_STYLES[role]["E0"], role, text,
                    "TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01(Task B、er038)b1b出力をread-onlyで"
                    "reuse(design doc §1-1、style値がProduction FAMILY_X_ROLE_STYLE_EN["
                    f"{role!r}]と完全一致することを実測確認済み、"
                    "en_pronunciation_resolver_info.hints_applied=false実測確認済み)。")
            else:
                results[pattern] = generate_en_pattern_segment(segment_name, text, out_path, pattern, tts_backend)
    return {"segment": segment_name, "language": "en", "results": results}


# ------------------------------------------------------------
# 修正1回目(delegation _02、2026-09-28): Task B Trial値の参考列追加
# ------------------------------------------------------------
# ユーザーが基準点として述べた「現状=『落ち着いた、自然な話し言葉で』は
# 抑揚不足」の"落ち着いた、自然な話し言葉で"は、実はTask B
# (TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01、er038)がTrial限定で導入した値
# であり、本Trial02がJ0として採用した真のProduction現状
# (p9a.JAPANESE_STYLE_PREFIX)とは異なる。比較の連続性のため、Task B側の
# JA音声(preview/comment_1〜4)をread-onlyでreuseし、試聴ページへ
# 「参考: Task B Trial値」列として追加する。新規TTS/ASR呼び出しは
# 一切行わない(API支出0)。J1〜J3・E0〜E3・J0/E0のreuse元は変更しない。
TASKB_JA_STYLE = "落ち着いた、自然な話し言葉で"
TASKB_MANAGEMENT_ID = "TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01"
TASKB_REFERENCE_SOURCE_DIR = "er038_output/tts_all_spoken_role_style_trial_01/hormuz/a2"
TASKB_REFERENCE_AUDIT_PATH = f"{TASKB_REFERENCE_SOURCE_DIR}/audit/tts_generation_results.json"
TASKB_JA_REFERENCE_SEGMENTS = ("preview", "comment_1", "comment_2", "comment_3", "comment_4")


def wav_to_mp3(wav_path: str, mp3_path: str, bitrate: int = 128) -> bool:
    """lameencでwav→mp3変換する(ffmpeg不要、er040_*_page_01.pyと同一手法)。
    エンコーダが無い環境ではFalseを返し、呼び出し側がフォールバックする。"""
    if not _HAS_LAMEENC:
        return False
    with wave.open(wav_path, "rb") as w:
        channels = w.getnchannels()
        framerate = w.getframerate()
        frames = w.readframes(w.getnframes())
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bitrate)
    encoder.set_in_sample_rate(framerate)
    encoder.set_channels(channels)
    encoder.set_quality(2)
    data = encoder.encode(frames)
    data += encoder.flush()
    os.makedirs(os.path.dirname(mp3_path) or ".", exist_ok=True)
    with open(mp3_path, "wb") as f:
        f.write(data)
    return True


def build_taskb_reference_data(theme_out_dir: str, page_dir: str) -> dict:
    """Task B(er038)のJA音声(style=「落ち着いた、自然な話し言葉で」)を
    read-onlyでreuseし、参考列用データを作る。新規TTS/ASR呼び出しは
    一切行わない(既存wavのコピー+mp3変換のみ)。"""
    audit = load_json(TASKB_REFERENCE_AUDIT_PATH)
    segs = audit["segments"]
    ref_dir = f"{theme_out_dir}/reference_taskb"
    os.makedirs(ref_dir, exist_ok=True)
    data = {}
    for name in TASKB_JA_REFERENCE_SEGMENTS:
        s = segs.get(name)
        if s is None or s.get("status") != "OK":
            data[name] = {"status": "NOT_AVAILABLE", "reason": "Task B出力に該当segmentのOK音声が無い"}
            continue
        style_used = s.get("style_prefix_used")
        if style_used != TASKB_JA_STYLE:
            data[name] = {
                "status": "NOT_AVAILABLE",
                "reason": f"Task B側のstyleが想定と不一致(実測={style_used!r})、参考音声を追加しない",
            }
            continue
        src_wav = s["path"]
        dst_wav = f"{ref_dir}/{name}_taskb.wav"
        shutil.copyfile(src_wav, dst_wav)
        mp3_name = f"reference_taskb_{name}.mp3"
        mp3_path = f"{page_dir}/{mp3_name}"
        converted = wav_to_mp3(dst_wav, mp3_path)
        data[name] = {
            "status": "OK",
            "style_prefix_used": style_used,
            "duration_seconds": s["trim_info"]["trimmed_duration_seconds"],
            "asr_text": s.get("asr_text"),
            "canonical_text": s.get("canonical_text"),
            "reused_from": src_wav,
            "sha256": s.get("sha256"),
            "audio_file": mp3_name if converted else None,
            "source_management_id": TASKB_MANAGEMENT_ID,
        }
    save_json(f"{ref_dir}/reference_data.json", data)
    return data


_J0_LABEL_OLD = "<b>J0</b>"
_J0_LABEL_NEW = "<b>J0=現行Production(長文instruction)</b>"

_TASKB_NOTE_HTML = """
<div class="note">
<b>参考列(Task B Trial値)について</b>: ユーザーが以前に試聴し「現状=『落ち着いた、
自然な話し言葉で』は抑揚不足」と述べた基準点の音声は、実はTask B(<code>TTS-ALL-
SPOKEN-ROLE-STYLE-TRIAL-01</code>)がTrial限定で導入した値であり、Productionには
配線されていません。本ページのJ0は真のProduction現状(長文instruction、上記
「重要な発見」参照)であり、ユーザーが以前聴いたTask B値とは異なります。比較の
連続性のため、下表A(日本語)の各segment行に、Task B側の音声を「参考: Task B
Trial値」列として追加しました(新規TTS/ASR呼び出しなし、既存音声のread-only
reuseのみ)。
</div>
"""


def _build_reference_cell_html(segment_name: str, entry: dict) -> str:
    if entry.get("status") != "OK":
        return (f"<td rowspan='4' style='max-width:220px;font-size:11px'>"
                f"参考音声なし: {html.escape(entry.get('reason', ''))}</td>")
    style_html = html.escape(entry["style_prefix_used"])
    asr_html = html.escape(entry.get("asr_text") or "")
    audio_html = (
        f"<audio controls preload='none' style='width:200px'>"
        f"<source src='{entry['audio_file']}' type='audio/mpeg'></audio>"
        if entry.get("audio_file") else "(mp3変換不可、参照のみ)")
    return (
        "<td rowspan='4' style='max-width:220px;font-size:11px'>"
        f"<b>参考: Task B Trial値</b>(<code>{TASKB_MANAGEMENT_ID}</code>、Production未配線)<br>"
        f"Style(全文): <pre style='white-space:pre-wrap;margin:0;font-size:11px'>{style_html}</pre>"
        f"ASR(実測): {asr_html}<br>Duration: {entry['duration_seconds']}s<br>"
        f"{audio_html}"
        "</td>")


def augment_page_with_taskb_reference_column(page_path: str, reference_data: dict) -> None:
    """試聴ページindex.htmlの表A(日本語)のみへ、Task B参考列を追加する。
    表B(英語本文)・その他section・head/style等は一切変更しない。
    行を新規に組み立てるのではなく、既存の1ページ全体を文字列として読み込み、
    表Aの<tr>単位で正規表現分割して挿入するだけの最小差分アプローチを取る
    (Section Bを誤って書き換えるリスクを避けるため、表A開始位置は
    '<h2>A. 日本語'〜'<h2>B. 英語本文'の間に限定する)。"""
    with open(page_path, encoding="utf-8") as f:
        content = f.read()

    marker_a = "<h2>A. 日本語"
    marker_b = "<h2>B. 英語本文"
    idx_a = content.index(marker_a)
    idx_b = content.index(marker_b, idx_a)
    section_a = content[idx_a:idx_b]

    table_match = re.search(r"<table class='seg'>.*?</table>", section_a, re.S)
    if table_match is None:
        raise AssertionError("表A(<table class='seg'>)が見つかりません")
    table_html = table_match.group(0)
    rows = re.findall(r"<tr>.*?</tr>", table_html, re.S)
    if len(rows) != 1 + len(TASKB_JA_REFERENCE_SEGMENTS) * 4:
        raise AssertionError(
            f"表Aの行数が想定外(header+segment*4想定): got={len(rows)}")

    header_row = rows[0]
    header_row_new = header_row.replace(
        "</tr>", "<th>参考: Task B Trial値(Production未配線)</th></tr>")

    data_rows_new = []
    for seg_idx, segment_name in enumerate(TASKB_JA_REFERENCE_SEGMENTS):
        chunk = rows[1 + seg_idx * 4: 1 + seg_idx * 4 + 4]
        entry = reference_data.get(segment_name, {"status": "NOT_AVAILABLE", "reason": "no data"})
        ref_cell = _build_reference_cell_html(segment_name, entry)
        for pattern_idx, row_html in enumerate(chunk):
            row_html = row_html.replace(_J0_LABEL_OLD, _J0_LABEL_NEW)
            if pattern_idx == 0:
                row_html = row_html.replace("</tr>", ref_cell + "</tr>")
            data_rows_new.append(row_html)

    table_html_new = "".join([header_row_new] + data_rows_new)
    table_html_new = f"<table class='seg'>{table_html_new}</table>"

    section_a_new = section_a.replace(table_match.group(0), table_html_new, 1)
    content_new = content[:idx_a] + section_a_new + content[idx_b:]

    # 冒頭の<div class="finding">...</div>(重要な発見)の直後にTask B参考列の
    # 説明段落を追加する(表Aより前、ページ全体content内で検索する。
    # finding divはidx_aより前に存在する)。
    finding_match = re.search(r'<div class="finding">.*?</div>', content_new, re.S)
    if finding_match is None:
        raise AssertionError('<div class="finding">...</div>が見つかりません')
    finding_end = finding_match.end()
    content_new = content_new[:finding_end] + _TASKB_NOTE_HTML + content_new[finding_end:]

    with open(page_path, "w", encoding="utf-8") as f:
        f.write(content_new)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-run", required=True)
    parser.add_argument("--segment", required=True,
                         help="1つのsegment_id(preview/comment_1..4/full_story_part1/in_one_line/topic_intro)")
    parser.add_argument("--language", required=True, choices=("ja", "en"))
    parser.add_argument("--patterns", required=True, help="カンマ区切り(例: J1,J2,J3 または E0,E1,E2,E3)")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--tts-backend", default="speech_metadata_flash_lite",
                         choices=("structured_separation", "speech_metadata_flash_lite"))
    parser.add_argument("--budget-jpy", type=float, required=True)
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    cl.install(f"{args.out_dir}/raw_usage_log.jsonl")
    patterns = [p.strip() for p in args.patterns.split(",") if p.strip()]

    with cl.logging_context("tts_variable_spoken_role_style_trial_02", "tts"):
        if args.language == "ja":
            summary = run_ja_segment(args.out_dir, args.segment, patterns, args.tts_backend)
        else:
            summary = run_en_segment(args.out_dir, args.segment, patterns, args.tts_backend)

    result_path = f"{args.out_dir}/results/{args.language}_{args.segment}.json"
    save_json(result_path, summary)
    fx_runner.assert_budget_ok(args.out_dir, args.budget_jpy, f"after {args.language}:{args.segment}")

    final_jpy, by_provider = fx_runner.compute_cost_jpy_so_far(f"{args.out_dir}/raw_usage_log.jsonl")
    print(f"[ER044-TRIAL] segment={args.segment} language={args.language} patterns={patterns} "
          f"累計費用(JPY)={final_jpy:.2f} by_provider={by_provider}")
    print(f"[ER044-TRIAL] result saved: {result_path}")


if __name__ == "__main__":
    main()
