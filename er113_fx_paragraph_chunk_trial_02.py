# -*- coding: utf-8 -*-
"""FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_03 (DEV/Trial専用、TTS 0・API 0)。
既存B_r1/B_r2のchunk wav(er113_output/.../gen)を、段落間追加無音0.2秒で再組立(B0.2)し、同一計測(M4分解/WPM/境界音量差/整列)を行い、
試聴ページ(A/B0/B0.2主表示、旧B0.5とA_r2/B_r2は折りたたみ)を更新する。新しい音声加工は無し(01のcompute_b_artifacts等を再利用)。
ASRはローカルfaster-whisperのみ(API呼出なし)。"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er113_fx_paragraph_chunk_trial_01 as m1  # noqa: E402

OUT = m1.OUT_DIR
PAUSE = 0.2
AUD = f"{m1.PAGE_DIR}/audio"


def main():
    from faster_whisper import WhisperModel
    before = m1.snapshot_protected()
    parts_json = m1.load_json(f"{m1.A_LEVEL_DIR}/parts.json")
    mw = m1._mw()
    words = {n: mw.count_primary(parts_json[f"part{n}"]) for n in m1.PARTS}
    old = m1.load_json(f"{OUT}/measure_01.json")
    out = {"pause_seconds": PAUSE, "variants": {}, "alignment": {}, "decomposition": {}, "boundary": {}}
    arts = {}
    for arm in ("B_r1", "B_r2"):
        fmt = f"{OUT}/gen/{arm}_{{chunk_id}}/b1b/narration/full_story_part{{part}}.wav"
        arts[arm] = m1.compute_b_artifacts(fmt, f"{OUT}/postprocess", PAUSE, with_full=(arm == "B_r1"))
    fmt = f"{OUT}/gen/B_r1_{{chunk_id}}/b1b/narration/full_story_part{{part}}.wav"
    b0 = m1.compute_b_artifacts(fmt, f"{OUT}/postprocess", 0.0, with_full=True)
    variants_mono = {"B02_r1": arts["B_r1"]["_mono"], "B02_r2": arts["B_r2"]["_mono"]}
    model = WhisperModel("small", device="cpu", compute_type="int8")
    for vn, mono in variants_mono.items():
        pm = {}
        for n in m1.PARTS:
            pm[f"part{n}"] = m1.measure_wav(mono[n], m1.SR24, words[n])
            wp = f"{OUT}/postprocess/align/{vn}_part{n}.wav"
            m1._write_wav24(wp, mono[n])
            out["alignment"].setdefault(vn, {})[str(n)] = m1.measure_alignment(model, os.path.join(ROOT, wp), parts_json[f"part{n}"])
        out["variants"][vn] = {"parts": {k: {kk: vv for kk, vv in v.items() if kk != "pauses_300_detail"} for k, v in pm.items()},
                               "total": m1._agg_wpm(pm)}
    allal = dict(old["alignment"])
    allal.update(out["alignment"])
    for x, y in [("A", "B02_r1"), ("B0_r1", "B02_r1"), ("B_r1", "B02_r1"), ("A_r2", "B02_r1"), ("A", "B02_r2"), ("A_r2", "B02_r2"),
                 ("B0_r2", "B02_r2"), ("B02_r1", "B02_r2")]:
        out["decomposition"][f"{x}->{y}"] = m1.m4_decompose(allal[x], allal[y])
    out["boundary"]["B02_r1_all_chunk_boundaries_db"] = arts["B_r1"]["boundary_jump_db_all_chunks"]
    out["boundary"]["B02_r2_all_chunk_boundaries_db"] = arts["B_r2"]["boundary_jump_db_all_chunks"]
    out["boundary"]["B02_r1_chunk_gains"] = {f"part{n}": arts["B_r1"]["parts"][f"part{n}"]["gains_per_chunk"] for n in m1.PARTS}
    out["boundary"]["A_part_boundaries_db"] = old["boundary"]["A_part_boundaries_db"]
    out["full_episode_b02_r1"] = arts["B_r1"]["full_episode_b"]
    out["full_episode_b0_r1"] = b0["full_episode_b"]
    out["integrity"] = {vn: {n: {"all_paragraphs_aligned": a["all_paragraphs_aligned"], "match_ratio": a["match_ratio"], "asr_words": a["asr_words"],
                                 "ref_words": a["ref_words"], "asr_over_ref": round(a["asr_words"] / a["ref_words"], 4)} for n, a in al.items()}
                        for vn, al in allal.items() if vn in ("A", "B_r1", "B0_r1", "B02_r1", "B02_r2")}
    chk = m1.compute_b_artifacts(fmt, f"{OUT}/postprocess", 0.5, with_full=False)
    out["sanity_pause05_reproduces_measure01"] = {n: [chk["parts"][f"part{n}"]["measure"]["duration_s"], old["variants"]["B_r1"]["parts"][f"part{n}"]["duration_s"]] for n in m1.PARTS}
    out["tts_calls"] = 0
    out["protected_changed"] = m1.diff_snapshots(before, m1.snapshot_protected())
    m1.save_json(f"{OUT}/measure_02.json", out)
    res = {"B02": arts["B_r1"]["_stereo"], "B0": b0["_stereo"], "B02_r2": arts["B_r2"]["_stereo"], "a": m1.a_artifacts(), "out": out, "old": old}
    build_page(res)
    print(json.dumps({k: out["variants"][k]["total"] for k in out["variants"]}, ensure_ascii=False))
    print(json.dumps({k: {kk: v["total"][kk] for kk in ("d_dur", "d_speech", "d_gap", "d_ends")} for k, v in out["decomposition"].items()}))
    print(out["integrity"])
    print(out["sanity_pause05_reproduces_measure01"], out["protected_changed"])


def build_page(res):
    out, old = res["out"], res["old"]

    def mp3(name, arr, br="96k"):
        m1._write_mp3(arr, f"{AUD}/{name}.mp3", br=br)
        return f"audio/{name}.mp3"

    def cell(src):
        return f"<audio controls preload='none' src='{src}'></audio>"
    rows = []
    for n in m1.PARTS:
        rows.append(f"<tr><td><b>本文{n}</b></td><td class='play'>{cell(f'audio/A_part{n}.mp3')}</td><td class='play'>{cell(f'audio/B0_part{n}.mp3')}</td>"
                    f"<td class='play'>{cell(mp3(f'B02_part{n}', res['B02']['parts'][n]))}</td></tr>")
    rows.append(f"<tr><td><b>本文全体</b><br><span class='sec'>本文1+2+3</span></td><td class='play'>{cell('audio/A_body.mp3')}</td>"
                f"<td class='play'>{cell('audio/B0_body.mp3')}</td><td class='play'>{cell(mp3('B02_body', res['B02']['body']))}</td></tr>")
    rows.append(f"<tr><td><b>Advanced通し</b><br><span class='sec'>Intro〜Outro。本文のみ差替え</span></td><td class='play'>{cell('audio/A_full.mp3')}</td>"
                f"<td class='play'>{cell(mp3('B0_full', res['B0']['full'], '128k'))}</td><td class='play'>{cell(mp3('B02_full', res['B02']['full'], '128k'))}</td></tr>")
    o = old["variants"]

    def line(nm, t):
        return f"<tr><td>{nm}</td><td>{t['duration_s']}</td><td>{t['total_wpm']}</td><td>{t['articulation_wpm_300']}</td></tr>"
    table = ("<table style='width:auto'><thead><tr><th>方式</th><th>本文の長さ(秒)</th><th>全体WPM</th><th>実発話WPM(無音除く)</th></tr></thead><tbody>"
             + line("A 現行", o["A"]["total"]) + line("B0 追加無音なし", o["B0_r1"]["total"]) + line("B0.2 追加0.2秒", out["variants"]["B02_r1"]["total"])
             + line("(参考)旧B 0.5秒", o["B_r1"]["total"]) + "</tbody></table>")
    ref_rows = ""
    for tag, lab in (("B", "旧B(0.5秒)"), ("A_r2", "A_r2 現行方式の別take"), ("B_r2", "旧B_r2(0.5秒、Bの別take)")):
        ref_rows += f"<tr><td>{lab}</td>" + "".join(f"<td class='play'>{cell(f'audio/{tag}_part{n}.mp3')}</td>" for n in m1.PARTS) + "</tr>"
    ref_rows += "<tr><td>B0.2_r2(別take、0.2秒)</td>" + "".join(f"<td class='play'>{cell(mp3(f'B02r2_part{n}', res['B02_r2']['parts'][n]))}</td>" for n in m1.PARTS) + "</tr>"
    html_doc = ("<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Family X 段落Chunk Trial 0.2秒版 比較試聴</title>"
                f"<meta name='viewport' content='width=device-width, initial-scale=1'><style>{m1._PAGE_CSS}</style></head><body>"
                "<h1>Family X『英国の電車マナー』Advanced 段落Chunk 比較試聴(0.2秒版・Trial)</h1>"
                "<div class='note'><b>状態: Trial(Production採用ではありません)</b>。対象=Advanced本文(本文1・2・3、約140秒)。<br>"
                "<b>A</b>=現在の完成音声(本文1つ=1回の読み上げ) / <b>B0</b>=段落ごとに読み上げ、段落の間に追加の間なし / "
                "<b>B0.2(新)</b>=段落ごとに読み上げ、段落の間に0.2秒を追加。"
                "B0とB0.2は同じ音声を使い、間の長さだけが違います(読み上げの追加費用なし)。文章・声・設定は全て同一です。<br>"
                "聴いていただきたい点: 速さ(Aより遅く感じるか) / 段落の間の自然さ(0.2秒で十分か) / 声や抑揚が段落ごとに変わって聞こえないか / 音量の差。"
                "<br>※Aは過去に選ばれた1回分、B0/B0.2は新規の1回分で、読み上げごとの偶然の差が混ざります(折りたたみに別takeあり)。</div>"
                f"<table><thead><tr><th>区間</th><th>A 現行</th><th>B0 追加なし</th><th>B0.2(新) +0.2秒</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"
                f"<h2>速さの目安(本文3パート合計)</h2>{table}"
                "<p class='sec'>実発話WPM=1分あたりの語数(間を除く)。B0とB0.2は同一音声のため実発話WPMは同じで、全体WPMだけが間の分だけ変わります。</p>"
                "<details><summary><b>参考: 旧B(0.5秒)と別take</b></summary><table><thead><tr><th>方式</th><th>本文1</th><th>本文2</th><th>本文3</th></tr></thead><tbody>"
                f"{ref_rows}</tbody></table></details>"
                "</body></html>")
    with open(os.path.join(ROOT, m1.PAGE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_doc)


if __name__ == "__main__":
    main()
