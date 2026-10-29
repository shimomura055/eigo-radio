# -*- coding: utf-8 -*-
"""Family X 標準 公開試聴ページ builder(SLOT-23-CONSUMER-DESIGN-01 委任_04C。`tools/build_aif3_listening_page_01.py`を昇格・AI島固有文言を除去して引数化)。

新規記事の正式入口(API 0)。入力=Production runner(X)のrun dir(assemble/Gate通過済み)。共通builder `er_user_listening_page_common_01.render_standard_page` と
学習ブロック `er120_part2_wiring_01.public_study_html`(Part 1[Advanced、およびマーク付きStandard]+Part 2)を使う。
確定レコードに`display_spec`(新表示仕様のマーク)があるlevelは、本文ハイライト(①太字+二重下線 / ②太字+下線 / ③下線のみ+訳リスト)を出す。
無いlevel=従来と同じ描画(ハイライト・凡例・CSS追加なし)。

出力前に必須でPASSすること(1つでも落ちたら index.html を出力しない):
 (1) 本文ハイライトの解決(ISSUE=HighlightStop。部分適用なし) (2) `check_page(public)`(⏸/chunk-mark 0を含む) (3) G3 `verify_highlights`(装飾・③訳・本文不変・public混入)
 (4) vocab対象level(Advanced・マーク付きStandard)は当該level節の Part 1 がちょうど1個、対象外levelは0個 (5) Part 2(文法)の確定↔part2_result↔study_text↔ページ節の4者一致。
使い方: py er019_family_x_listening_page_01.py --slug <slug> --run-name <run> --web <出力dir> [--intro-note <追記文>]
旧per-article公開ページscript(`er019_*page*.py` 14本)は遡及なし=未改修で、display_spec付きrunを処理しようとすると`er019_x_page_guard_01`がSTOPする。"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

esc = html.escape
RUN_ROOT_DEFAULT = "er019_output/family_x_audio_production_wiring_01"
SOURCE_ROOT_DEFAULT = "er019_output"
LEVEL_SPECS = (("a2", "std", "Standard"), ("b1b", "adv", "Advanced"))   # (level, page id, 表示名)。再生順=Standard→Advanced


class PageStop(RuntimeError):
    """ページを出力しない(fail-closed)。メッセージに原因コードを含む。"""


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def rt(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def _ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def to_mp3(x, sr, out, br="96k"):
    import soundfile as sf
    tmp = out + ".tmp.wav"
    sf.write(tmp, x, sr)
    subprocess.run([_ffmpeg(), "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, out], check=True)
    os.remove(tmp)


def _unit_key(part_label: str):
    m = re.match(r"Full Story Part ([123])", part_label)
    if m:
        return f"full_story_part{m.group(1)}"
    return "in_one_line" if part_label.startswith("In One Line") else None


_DELIM_HTML_RE = re.compile(r"[ \t]*={5,}[ \t]*(?=</p>)")
_DELIM_TAIL_RE = re.compile(r"\n?={5,}[ \t\r\n]*$")

def strip_trailing_delim(text: str) -> str:
    """OPEN-591 第1段: LLM終端区切り`=====`(連続=5個以上のみの終端)を表示時にstrip。
    HTML(`... =====</p>`)とmarkdown末尾の両方。`=====ITEM`等の非終端・`=====`無し入力は不変。"""
    text = _DELIM_HTML_RE.sub("", text)
    return _DELIM_TAIL_RE.sub("", text)


def level_data(R, uc, hl, run, source_dir, level, key, label, ja_title, slug, hres, jobs):
    """1level分の行データ。音声のmp3変換はjobsへ積むだけ(全検査PASS後に実行)。"""
    import soundfile as sf
    base = f"{run}/{level}"
    summ = rj(f"{base}/run_summary_assemble.json")
    if summ.get("status") != "OK":
        raise PageStop(f"X_PAGE_ASSEMBLE_NOT_OK: {level} assemble status={summ.get('status')}")
    x, sr = sf.read(summ["out_path"], dtype="float32")
    full = f"{slug}_{label.lower()}.mp3"
    jobs.append((x, sr, full, "128k"))
    timeline = rj(f"{base}/audit/timeline.json")
    parts = rj(f"{base}/parts.json")
    support = rj(f"{base}/{'b1_support_texts.json' if level == 'b1b' else 'a2_support_texts.json'}")
    # LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 B3(UD-1): 公開ページの表示本文へLR後の英文を反映(派生overlay)。
    import er132_lr_overlay_pages_01 as _er132
    parts, support = _er132.overlay_level_dir_units(base, parts, support)
    _lr = _er132.level_ledger(run, level, level_dir=base)
    import er133_report_marks_01 as _rm   # 委任_11(ユーザー原文_02 §4): 試聴ページの⏸(実Chunk境界)・LR赤・Fallback濃青の共通表示部品
    _events = _rm.load_events(run, level, level_dir=base)
    _plans = uc.load_chunk_plans(f"{base}/audit/chunk_plan_{level}.json")
    kp = rj(f"{base}/key_phrases/keywords_canonicalized.json")
    kp_by_rank = {i["rank"]: i for i in kp["items"]}
    expl = {}
    if level == "b1b":
        tts = rj(f"{base}/audit/tts_generation_results.json")
        expl = {int(r): {"explanation": (v.get("explanation") or {}).get("explanation_text")} for r, v in (tts.get("key_phrases") or {}).items()}
    rows, script_texts = [], []
    for e in timeline:
        part = e["part"]
        if part.startswith("pause_"):
            continue
        s, dur = e["start_seconds"], e["duration_seconds"]
        fn = f"{key}_{len(rows):02d}.mp3"
        jobs.append((x[int(round(s * sr)): int(round((s + dur) * sr))], sr, fn, "96k"))
        info = R._row_info_family_x(part, level, parts, support, f"{base}/narration", kp_by_rank, ja_title, kp_explanations_by_rank=expl or None)
        if part.startswith("Topic intro"):   # 委任_11(Fable補足(2)): ページが表示するtopic_introのLR後の英文を採用音声と一致させる(表示=採用音声)
            info = dict(info, text=_er132.display_text_of_clip(_lr, "topic_intro", info["text"]))
        if part.startswith("Key Phrase "):
            it = kp_by_rank[int(part.split(" ")[-1])]
            _rk = it["rank"]
            if level == "b1b":
                _cells = [it["used_form"], expl[_rk]["explanation"]]
                _cm = {0: _rm.marks_for(_events, _cells[0], ids=(f"kp{_rk}_en",), whole=True), 1: _rm.marks_for(_events, _cells[1], ids=(f"kp{_rk}_explanation",), whole=True)}
                blocks = [uc.kp_block(["英語", "英語での解説"], _cells, {i: m for i, m in _cm.items() if m}, _rm.notes_of(_cm.values()))]
            else:
                _cells = [it["used_form"], it["japanese_gloss"]]
                _cm = {0: _rm.marks_for(_events, _cells[0], ids=(f"kp{_rk}_en",), whole=True), 1: _rm.marks_for(_events, _cells[1], ids=(f"kp{_rk}_japanese_meaning",), whole=True)}
                blocks = [uc.kp_block(["英語", "日本語の意味"], _cells, {i: m for i, m in _cm.items() if m}, _rm.notes_of(_cm.values()))]
        elif info["sfx"]:
            blocks = ["<span class='sec'>効果音・音楽(読み上げなし)</span>"]
        elif info["voice"] is None or info["text"].startswith("(共有固定"):
            blocks = ["<span class='sec'>定型の案内音声</span>"]
        else:
            uk = _unit_key(part)
            hls = hl.highlights_for_text(hres, uk, 0) if (hres is not None and uk) else None
            _fs = re.match(r"full_story_part\d+$", uk or "")
            _clip_ids = () if _fs else tuple(os.path.splitext(os.path.basename(p))[0] for p in ([info["audio"]] if isinstance(info.get("audio"), str) else list(info.get("audio") or ())))
            _mk = _rm.marks_for(_events, info["text"], ids=_clip_ids, block=uk if _fs else None, whole=not _fs)
            _cts = _er132.chunk_texts_overlaid(_lr, _plans.get(uk)) if _fs else None   # ⏸=実TTS Chunk境界(chunk planの記録位置)にだけ
            blocks = [uc.script_block(info["text"], _cts, highlights=hls or None, marks=_mk)]
            script_texts.append(info["text"])
            if hres is not None and uk:
                ml = hl.meaning_list_html(hl.meanings_for_unit(hres, uk))   # ③の訳リスト(当該Partの台本セル直後、div.script/table/h2の外)
                if ml:
                    blocks.append(ml)
        rows.append({"part": part, "start": s, "dur": dur, "src": f"audio/{fn}", "blocks": blocks})
    return {"summ": summ, "full": full, "duration": x.shape[0] / sr, "rows": rows, "parts": parts, "kp": kp, "script_texts": script_texts}


def build_page(slug: str, run_name: str, web: str, *, run_root: str = RUN_ROOT_DEFAULT, source_root: str = SOURCE_ROOT_DEFAULT,
               ja_title: str | None = None, intro_note: str = "", levels=LEVEL_SPECS) -> dict:
    """ページを生成して `<web>/index.html` に書く。いずれかの必須検査が落ちたら PageStop(index.htmlは書かない)。戻り値=検査結果の要約。"""
    import er019_family_x_audio_production_runner_01 as R
    import er120_part2_wiring_01 as p2w
    import er_learning_highlight_01 as hl
    import er_user_listening_page_common_01 as uc

    run = f"{run_root}/{slug}__{run_name}"
    source_dir = f"{source_root}/{slug}/{run_name}"
    web_aud = os.path.join(web, "audio")
    if ja_title is None:
        ja_title = R.derive_japanese_title(source_dir)["japanese_title"]
    jobs: list = []
    lv_out, info, hres_by_level, vocab_levels = [], {}, {}, []
    for level, lid, label in levels:
        try:
            hres = R.resolve_x_highlights(run, level, source_dir=source_dir)   # display_spec無し=None(従来描画)。ISSUE=HighlightStop
        except (R.HighlightStop, ValueError) as exc:
            raise PageStop(str(exc)) from exc
        hres_by_level[level] = hres
        d = level_data(R, uc, hl, run, source_dir, level, lid, label, ja_title, slug, hres, jobs)
        article_text = rt(f"{source_dir}/{level}/article.md")
        study = p2w.public_study_html(run, article_text, level=level)
        if hres is not None:   # 表示範囲外の③訳(HL_MEANING_ONLY)は節末(表の後)に置く
            study = hl.meaning_list_html(hl.meanings_for_unit(hres, None)) + study
        if R.part1_enabled(run, level):
            vocab_levels.append(level)
        info[level] = d
        lv_out.append({"id": lid, "label": label, "full_src": f"audio/{d['full']}", "duration": d["duration"], "rows": d["rows"], "study_html": study})
    marked = [lv for lv, r in hres_by_level.items() if r is not None]
    aux = ["<details class='aux'><summary>制作情報</summary><ul>"]
    for level, _lid, lab in levels:
        sp = f"{run}/{level}/key_phrases/confirmed_selection.json"
        sel = rj(sp) if os.path.exists(sp) else {}
        aux.append(f"<li>{lab}: 本文sha256={esc(hashlib.sha256(open(f'{source_dir}/{level}/article.md', 'rb').read()).hexdigest()[:16])}… / "
                   f"ユーザー確定 confirmation_id={esc(str(sel.get('confirmation_id') or '(旧run・確定記録なし)')[:19])} / "
                   f"文法={esc(str((sel.get('grammar') or {}).get('status')))} / 長さ={info[level]['duration']:.0f}秒</li>")
    aux.append("</ul></details>")
    pw = []
    for level, _lid, lab in levels:
        pp_ = f"{run}/{level}/audit/pass_with_warning_listening_list.json"
        lst = rj(pp_) if os.path.exists(pp_) else {"count": 0, "entries": []}
        # 委任_11(ユーザー原文_02 §4): LR行は非表示にせず共通表示部品の赤で表示する(audience区分による出し分けはしない)
        items = "".join(("<li style='color:#c00000'>" if "LR_REWRITTEN" in (e.get("warning_labels") or []) else "<li>")
                        + f"{esc(e.get('segment_id', ''))} / 期待={esc(str(e.get('canonical_text')))} / 一次ASR={esc(str(e.get('primary_text')))} / "
                        f"二次ASR={esc(str(e.get('secondary_text')))} / {esc(','.join(e.get('warning_labels') or []))}</li>" for e in lst.get("entries", []))
        pw.append(f"<h3>{lab}: 事後試聴リスト(PASS_WITH_WARNING) {lst.get('count', 0)}件</h3><ul>{items}</ul>")
    aux_html = "".join(aux) + "<h2 id='pww'>事後試聴リスト(PASS_WITH_WARNING、非ブロッキング)</h2>" + "".join(pw)
    _al_text, _al_html = R._khr().render_redundancy_alarms_all(run)     # D8: 重複アラーム(表示・記録のみ・非停止)。記録なし=空=従来とバイト同一
    if _al_text:
        print(_al_text, flush=True)
        aux_html += _al_html
    title = f"{ja_title or slug} 試聴ページ"
    intro = ("<div class='note'><b>状態: 完成版・ユーザー試聴待ち</b>(試聴PASSは未取得です)。上のリンクでレベルを切り替えられます。"
             + (("<br>" + esc(intro_note)) if intro_note else "") + "</div>")
    if marked:
        intro += hl.legend_html()
    import er133_report_marks_01 as _rm
    if any(("chunk-mark" in b or "rpt-" in b) for _lv in lv_out for _r in _lv["rows"] for b in _r["blocks"]):   # ⏸/赤/青が1つでもあるページだけ凡例1行
        intro += _rm.legend_html()
    page = uc.render_standard_page(title, lv_out, intro_html=intro, aux_html=aux_html)
    if marked:   # ハイライトを出すページだけHIGHLIGHT_CSSを足す(マーク無しページ=従来とバイト同一)
        page = page.replace("</head>", f"<style>{hl.HIGHLIGHT_CSS}</style></head>", 1)

    # ---- 必須検査(出力前) ----
    summary = {"slug": slug, "run": run_name, "marked_levels": marked, "vocab_levels": vocab_levels, "notices": {}, "redundancy_alarm_report": _al_text}
    cp = uc.check_page(page, levels=tuple(lab for _l, _i, lab in levels))
    if cp["overall"] != "PASS":
        raise PageStop("X_PAGE_CHECK_PAGE_FAIL: " + "; ".join(f"{k}:{v['detail']}" for k, v in cp["checks"].items() if not v["ok"])[:600])
    g3 = R._g3()   # er128系を直接importしない(runnerの遅延accessor)
    for level, lid, _lab in levels:
        section = uc.level_section_html(page, lid)
        hres = hres_by_level[level]
        if hres is not None:
            g = g3.verify_highlights(section, {"result": hres, "audience": "dev", "script_texts": info[level]["script_texts"]})
            if g["status"] == "FAIL":
                raise PageStop(f"X_PAGE_G3_FAIL({level}): " + "; ".join(f"{p['code']}:{p.get('candidate_id')}:{p['detail']}" for p in g["problems"][:8]))
            summary["notices"][level] = [n["code"] for n in hres.get("notices", [])]
        n1 = section.count(R.PART1_HEADING_MARK)
        if level in vocab_levels:   # 積極検出(M11): vocab対象levelはちょうど1個。0個(判断記録なし等)・2個はSTOP
            try:
                R.validate_part1_block_count(section, level, where="page")
            except RuntimeError as exc:
                raise PageStop(str(exc)) from exc
        elif n1:
            raise PageStop(f"X_PAGE_PART1_UNEXPECTED({level}): vocab対象外のlevel節にPart 1が{n1}個あります(マーク無しlevelはPart 1なし=遡及なし)")
        try:   # Part 2: 確定 <-> part2_result.json <-> study_text/*.md <-> ページの当該level節 の4者一致
            pp_in, plabel = R._part2_inputs_x(source_dir, level)
            sd = R._part2_study_dir(run, level)
            p2w.verify_outputs(sd, pp_in, plabel, level=level, next_command=R.part2_next_command(source_dir, level), where=f"page({level})",
                               md_path=f"{sd}/{p2w.g.PART2_FILE_STEM}.md", html_text=section)
        except (p2w.g.Part2Error, p2w.g.Part2InputError, ValueError) as exc:
            raise PageStop(f"X_PAGE_PART2_OUTPUT_MISMATCH({level}): {exc}") from exc
    # ---- 検査PASS後に初めて音声・ページを書く ----
    os.makedirs(web_aud, exist_ok=True)
    for x, sr, fn, br in jobs:
        to_mp3(x, sr, os.path.join(web_aud, fn), br=br)
    cp2 = uc.check_page(page, base_dir=web, levels=tuple(lab for _l, _i, lab in levels), audience="public")
    if cp2["overall"] != "PASS":
        raise PageStop("X_PAGE_CHECK_PAGE_FAIL(audio): " + "; ".join(f"{k}:{v['detail']}" for k, v in cp2["checks"].items() if not v["ok"])[:600])
    with open(os.path.join(web, "index.html"), "w", encoding="utf-8") as f:
        f.write(strip_trailing_delim(page))   # OPEN-591 第1段: 4者一致検査はstrip前HTMLで実施済。書出し直前の表示層でのみLLM終端`=====`をstrip
    summary["rows"] = {lab: (len(info[lv]["rows"]), round(info[lv]["duration"], 2)) for lv, _i, lab in levels}
    return summary


def build_enduser_after_page(slug: str, run_name: str, web: str, *, run_root: str = RUN_ROOT_DEFAULT, source_root: str = SOURCE_ROOT_DEFAULT) -> int:
    """End User向け視聴ページ(`<web>/enduser/`)を自動生成する(END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 WP-E。APPROVED_FOR_PRODUCTION、API 0)。
    開発者向け index.html の既存検査・書出しが完了した後にだけ呼ぶ。失敗(`ENDUSER_*`)でも開発者向け index.html と既存の enduser/ は変更しない(rc=5)。"""
    import er135_enduser_page_01 as eu
    run = f"{run_root}/{slug}__{run_name}"
    source_dir = f"{source_root}/{slug}/{run_name}"
    try:
        r = eu.hook_run(web, "x", run_dir=run, cache_dir=f"{run}/enduser_sync_cache", ja_manuscript=eu.find_x_ja_manuscript(source_dir),
                        result_json=f"{run}/enduser_page_result.json")
    except eu.EnduserPageStop as exc:
        print(f"[FAMILY-X-LISTENING-PAGE][ENDUSER_STOP] {exc.code}: {exc.message}")
        return 5
    print("enduser page written", r["enduser_dir"], {k: r[k] for k in ("consistency", "total_wall_s", "api_calls")})
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Family X 標準公開試聴ページ builder(新規記事の正式入口)")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--run-name", required=True)
    ap.add_argument("--web", required=True, help="出力dir(index.html と audio/*.mp3)")
    ap.add_argument("--run-root", default=RUN_ROOT_DEFAULT)
    ap.add_argument("--source-root", default=SOURCE_ROOT_DEFAULT)
    ap.add_argument("--intro-note", default="", help="冒頭の補足文(任意)")
    a = ap.parse_args(argv)
    os.chdir(ROOT)
    try:
        s = build_page(a.slug, a.run_name, a.web, run_root=a.run_root, source_root=a.source_root, intro_note=a.intro_note)
    except PageStop as exc:
        print(f"[FAMILY-X-LISTENING-PAGE][STOP] {exc}")
        return 3
    print("page written", a.web, s)
    return build_enduser_after_page(a.slug, a.run_name, a.web, run_root=a.run_root, source_root=a.source_root)


if __name__ == "__main__":
    sys.exit(main())
