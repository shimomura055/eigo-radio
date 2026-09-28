# ============================================================
# er047_tts_fixed_shell_number_three_five_retrial_01_page_01.py
# TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01(Trial、Production実装なし)
# ============================================================
# er047_tts_fixed_shell_number_three_five_retrial_01.pyの実行結果
# (retrial_results.json)と、既決Champion(TRIAL-02、
# er043_output/.../champion_trial_results.json)のnum_one/num_two/num_four
# 採用音声(reuse、新規TTS/ASR呼び出しなし)を読み込み、
# (1)wav→mp3変換・One→Five連結音声(採用One/Two/Four固定+Three/Five
# take単位)、(2)比較用index.htmlを生成する。mp3変換・wav連結は既存
# `er040_tts_fixed_shell_master_champion_trial_01_page_01.wav_to_mp3`/
# `concat_wavs`をそのままimportして流用する(独自の再実装をしない)。
# F0簡易proxyも`er043_tts_fixed_shell_master_champion_trial_02_page_01.
# estimate_pitch_trend`をそのままimportして流用する。
# GitHub Pages配布専用(`user_test/fixed_shell_three_five_retrial_01/`)。
# Production側は一切変更しない(読み取りのみ)。
from __future__ import annotations

import json
import os

import er040_tts_fixed_shell_master_champion_trial_01 as champ1
import er040_tts_fixed_shell_master_champion_trial_01_page_01 as page1
import er043_tts_fixed_shell_master_champion_trial_02_page_01 as champ2_page

RETRIAL_RESULTS_PATH = "er047_output/tts_fixed_shell_number_three_five_retrial_01/retrial_results.json"
ADOPTED_RESULTS_PATH = "er043_output/tts_fixed_shell_master_champion_trial_02/champion_trial_results.json"
OUT_DIR = "er047_output/tts_fixed_shell_number_three_five_retrial_01"
PAGE_DIR = "user_test/fixed_shell_three_five_retrial_01"

# 既決Champion(ユーザー決定、design doc §2で確定した左/中/右→A/B/C対応)。
ADOPTED_PHRASES = {"num_one": "C", "num_two": "B", "num_four": "C"}
ADOPTED_ORDER = ["num_one", "num_two", "num_four"]
STYLE_SYSTEMS = ["B", "C"]
TARGET_PHRASES = ["num_three", "num_five"]
TAKES = [1, 2, 3, 4]


def _fmt(v) -> str:
    return "" if v is None else str(v)


def _esc(v) -> str:
    s = _fmt(v)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_retrial_results() -> dict:
    with open(RETRIAL_RESULTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_adopted_one_two_four() -> dict:
    """採用済みOne/Two/Fourを既存TRIAL-02出力からそのまま読み込む
    (新規TTS/ASR呼び出しなし、¥0)。"""
    data = champ1.load_json(ADOPTED_RESULTS_PATH)
    adopted = {}
    for name, cand in ADOPTED_PHRASES.items():
        r = data["candidates"][cand][name]
        adopted[name] = r
    return adopted


def build_adopted_display(adopted: dict) -> dict:
    display = {}
    for name in ADOPTED_ORDER:
        r = adopted[name]
        wav_path = r.get("path")
        mp3_name = f"adopted_{name}.mp3"
        converted = (page1.wav_to_mp3(wav_path, f"{PAGE_DIR}/{mp3_name}")
                     if wav_path and os.path.exists(wav_path) else False)
        display[name] = {
            "candidate": ADOPTED_PHRASES[name],
            "style_prefix_used": r.get("style_prefix_used"),
            "model": (r.get("key") or {}).get("tts_model_id") or "gemini-3.8-flash-lite-tts",
            "voice": r.get("voice") or (r.get("key") or {}).get("speaker_voice") or "Charon",
            "asr_text": r.get("asr_text"),
            "duration_seconds": (r.get("metrics") or {}).get("duration_seconds"),
            "audio_file": mp3_name if converted else None,
            "wav_path": wav_path,
        }
    return display


def _attempt_entries(attempts_log: list, name: str, style: str, take: int) -> list:
    entries = []
    for a in attempts_log or []:
        wav_path = a.get("attempt_audio_path")
        exists = bool(wav_path and os.path.exists(wav_path))
        entry = {
            "attempt": a.get("attempt"),
            "asr_text": a.get("asr_text"),
            "audio_classification": a.get("audio_classification"),
            "verified": a.get("verified"),
            "wav_exists": exists,
            "wav_path": wav_path if exists else None,
        }
        if exists:
            metrics = champ2_page.measured_metrics_for(wav_path)
            entry["duration_seconds"] = metrics["duration_seconds"] if metrics else None
            mp3_name = f"{name}_style{style}_take{take}_attempt{a.get('attempt')}.mp3"
            converted = page1.wav_to_mp3(wav_path, f"{PAGE_DIR}/{mp3_name}")
            entry["audio_file"] = mp3_name if converted else None
            entry["pitch_trend"] = champ2_page.estimate_pitch_trend(wav_path).get("trend")
        else:
            entry["audio_file"] = None
            entry["duration_seconds"] = None
            entry["pitch_trend"] = None
        entries.append(entry)
    return entries


def build_retrial_table(results: dict) -> dict:
    """phrase -> style -> take(int) -> entry。entryは常に
    status/style_prefix_used/attempts(全attemptの音声・ASR結果)を持つ。
    OKの場合のみ最終合格音声(audio_file/duration_seconds/rms_dbfs/
    pitch_trend/wav_path)も追加する。"""
    os.makedirs(PAGE_DIR, exist_ok=True)
    table = {}
    for name in TARGET_PHRASES:
        table[name] = {}
        for style in STYLE_SYSTEMS:
            table[name][style] = {}
            phrase_style_results = results.get("phrases", {}).get(name, {}).get(style) or {}
            for take_str, r in sorted(phrase_style_results.items(), key=lambda kv: int(kv[0])):
                take = int(take_str)
                status = r.get("status")
                entry = {
                    "status": status,
                    "style_prefix_used": r.get("style_prefix_used"),
                    "attempts": _attempt_entries(r.get("attempts_log"), name, style, take),
                }
                if status == "OK":
                    wav_path = r.get("path")
                    if wav_path and os.path.exists(wav_path):
                        metrics = champ2_page.measured_metrics_for(wav_path)
                        entry["duration_seconds"] = metrics["duration_seconds"] if metrics else None
                        entry["rms_dbfs"] = metrics["rms_dbfs"] if metrics else None
                        mp3_name = f"{name}_style{style}_take{take}.mp3"
                        converted = page1.wav_to_mp3(wav_path, f"{PAGE_DIR}/{mp3_name}")
                        entry["audio_file"] = mp3_name if converted else None
                        entry["asr_text"] = r.get("asr_text")
                        entry["pitch_trend"] = champ2_page.estimate_pitch_trend(wav_path).get("trend")
                        entry["wav_path"] = wav_path
                elif status == "STOPPED":
                    entry["reason"] = r.get("reason")
                table[name][style][take] = entry
    return table


def build_sequences(table: dict, adopted_display: dict) -> list:
    """採用One/Two/Four(固定)+Three take k+Five take k(kごと、style系統
    ごと)を連結した参考mp3。ASR不合格takeを含む場合はunverified=Trueで
    明示する(Production登録候補ではない参考情報)。"""
    sequences = []
    fixed_wav_paths = [adopted_display[name]["wav_path"] for name in ADOPTED_ORDER]
    fixed_ok = all(p and os.path.exists(p) for p in fixed_wav_paths)

    for style in STYLE_SYSTEMS:
        for take in TAKES:
            three = table.get("num_three", {}).get(style, {}).get(take)
            five = table.get("num_five", {}).get(style, {}).get(take)
            if three is None or five is None:
                continue
            wav_paths = []
            included = []
            if fixed_ok:
                wav_paths.extend(fixed_wav_paths)
                included.extend((n, "OK(採用済reuse)") for n in ADOPTED_ORDER)
            else:
                included.extend((n, "MISSING") for n in ADOPTED_ORDER)

            unverified = False
            missing = False
            for label, entry in (("num_three", three), ("num_five", five)):
                if entry["status"] == "OK" and entry.get("wav_path") and os.path.exists(entry["wav_path"]):
                    wav_paths.append(entry["wav_path"])
                    included.append((label, "OK"))
                else:
                    first = (entry.get("attempts") or [None])[0]
                    if first and first.get("wav_exists") and first.get("wav_path"):
                        wav_paths.append(first["wav_path"])
                        included.append((label, "UNVERIFIED_ATTEMPT1(ASR未合格)"))
                        unverified = True
                    else:
                        included.append((label, "MISSING"))
                        missing = True

            out_wav = f"{OUT_DIR}/seq_style{style}_take{take}.wav"
            ok = page1.concat_wavs(wav_paths, out_wav) if wav_paths else False
            mp3_name = f"seq_style{style}_take{take}.mp3"
            audio_file = None
            if ok:
                converted = page1.wav_to_mp3(out_wav, f"{PAGE_DIR}/{mp3_name}")
                audio_file = mp3_name if converted else None
            sequences.append({
                "style": style, "take": take, "included": included,
                "unverified": unverified, "missing": missing,
                "included_count": len(wav_paths), "audio_file": audio_file,
            })
    return sequences


def build_html(adopted_display: dict, table: dict, sequences: list) -> str:
    adopted_html = []
    for name in ADOPTED_ORDER:
        e = adopted_display[name]
        audio_html = (f'<audio controls src="{e["audio_file"]}"></audio><br>'
                      if e.get("audio_file") else "(mp3変換不可)<br>")
        adopted_html.append(
            f'<div><b>{_esc(name)}</b>(採用candidate {_esc(e["candidate"])}、TRIAL-02からreuse、¥0)<br>'
            f'{audio_html}model={_esc(e["model"])}<br>voice={_esc(e["voice"])}<br>'
            f'<b>Style Prompt全文</b>: "{_esc(e["style_prefix_used"])}"<br>'
            f'duration={_fmt(e["duration_seconds"])}s<br>ASR="{_esc(e["asr_text"])}"</div>'
        )

    table_html = []
    for name in TARGET_PHRASES:
        for style in STYLE_SYSTEMS:
            style_text_shown = None
            take_cells = []
            for take in TAKES:
                entry = table[name][style].get(take)
                if entry is None:
                    take_cells.append(f'<td>take{take}: NOT_ATTEMPTED</td>')
                    continue
                style_text_shown = entry.get("style_prefix_used")
                if entry["status"] == "OK":
                    audio_html = (f'<audio controls src="{entry["audio_file"]}"></audio><br>'
                                  if entry.get("audio_file") else "(mp3変換不可)<br>")
                    pitch = entry.get("pitch_trend")
                    cell = (f'<b>take{take}: OK</b><br>{audio_html}'
                            f'duration={_fmt(entry.get("duration_seconds"))}s<br>'
                            f'rms={_fmt(entry.get("rms_dbfs"))}dBFS<br>'
                            f'pitch_trend={_esc(pitch) if pitch else "(判定不可)"}<br>'
                            f'ASR="{_esc(entry.get("asr_text"))}"<br>'
                            f'attempts={_fmt(len(entry.get("attempts") or []))}')
                else:
                    cell = (f'<b>take{take}: STOPPED(3attempt不合格、既存Human Review Lock)</b><br>'
                            f'reason={_esc(entry.get("reason"))}<br>'
                            f'<span style="color:#a00">Production登録不可(人間確認用)、以下は全attempt'
                            f'音声</span>')
                    attempt_rows = []
                    for a in entry.get("attempts") or []:
                        if a.get("wav_exists"):
                            a_audio = (f'<audio controls src="{a["audio_file"]}"></audio>'
                                       if a.get("audio_file") else "(mp3変換不可)")
                        else:
                            a_audio = "(音声未保存)"
                        pitch_a = a.get("pitch_trend")
                        attempt_rows.append(
                            f'<div style="margin-top:4px;padding-left:6px;border-left:2px solid #ccc">'
                            f'attempt{_fmt(a.get("attempt"))}: {a_audio}<br>'
                            f'ASR="{_esc(a.get("asr_text"))}" 分類={_esc(a.get("audio_classification"))} '
                            f'duration={_fmt(a.get("duration_seconds"))}s '
                            f'pitch_trend={_esc(pitch_a) if pitch_a else "(判定不可)"} '
                            f'{"検証済(verified)" if a.get("verified") else "未検証(unverified)"}</div>'
                        )
                    cell += "".join(attempt_rows)
                take_cells.append(f'<td style="min-width:220px">{cell}</td>')
            table_html.append(
                f'<tr><th>{_esc(name)}<br>style系統={_esc(style)}<br>'
                f'<small>{_esc(style_text_shown)}</small></th>{"".join(take_cells)}</tr>'
            )

    seq_html = []
    for s in sequences:
        included_desc = "、".join(f"{n}={st}" for n, st in s["included"])
        if s.get("audio_file"):
            audio_html = f'<audio controls src="{s["audio_file"]}"></audio>'
        else:
            audio_html = "(連結不可)"
        warn = ('<span style="color:#a00">未検証(ASR不合格)takeを含む参考音声であり、'
                'Production登録候補ではない。</span>' if s["unverified"] else
                '<span style="color:#080">One〜Five全てASR合格音声のみで構成。</span>')
        seq_html.append(
            f'<div><b>style系統{_esc(s["style"])} / take{s["take"]}</b>(収録{s["included_count"]}/5件): '
            f'{audio_html}<br>構成: {_esc(included_desc)}<br>{warn}</div>'
        )

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01 試聴比較</title>
<style>
body {{ font-family: sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; font-size: 13px; }}
th {{ background: #eee; }}
audio {{ width: 220px; }}
</style>
</head>
<body>
<h1>TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01: num_three / num_five 複数take試聴比較</h1>
<p>TRIAL-02でユーザーが既に決定したChampion(num_one=Candidate C系統、num_two=Candidate B系統、
num_four=Candidate C系統)と同一model(gemini-3.8-flash-lite-tts)・同一voice(Charon)・同一style文言で、
num_three/num_fiveのみ、B系統・C系統それぞれ4 takeずつ新規生成した。ASR不合格(STOPPED)takeも
音声が保存されていれば「Production登録不可(人間確認用)」として全attempt音声を掲載する
(OPEN-222: 極短数字語のFlash-Lite ASR厳格一致限界の既知課題)。ユーザーが試聴のうえ、
num_three/num_fiveそれぞれの良いtakeを選んでください。選定後のMaster登録・Production配線は別管理IDで実施予定。</p>
<h2>採用済みOne/Two/Four(TRIAL-02からreuse、参考)</h2>
{''.join(adopted_html)}
<h2>One→Five 連続比較(採用One/Two/Four 固定 + Three/Five take単位、style系統別)</h2>
{''.join(seq_html)}
<h2>num_three / num_five 各takeの詳細(Style Prompt全文表示)</h2>
<table>
<tr><th>Phrase / Style系統</th><th>take1</th><th>take2</th><th>take3</th><th>take4</th></tr>
{''.join(table_html)}
</table>
</body>
</html>
"""


def main() -> None:
    results = load_retrial_results()
    adopted = load_adopted_one_two_four()
    adopted_display = build_adopted_display(adopted)
    table = build_retrial_table(results)
    sequences = build_sequences(table, adopted_display)
    html = build_html(adopted_display, table, sequences)
    os.makedirs(PAGE_DIR, exist_ok=True)
    with open(f"{PAGE_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    with open(f"{OUT_DIR}/page_comparison_data.json", "w", encoding="utf-8") as f:
        json.dump({"adopted": adopted_display, "table": table, "sequences": sequences},
                   f, ensure_ascii=False, indent=2, default=str)
    print(f"[ER047-PAGE] wrote {PAGE_DIR}/index.html")


if __name__ == "__main__":
    main()
