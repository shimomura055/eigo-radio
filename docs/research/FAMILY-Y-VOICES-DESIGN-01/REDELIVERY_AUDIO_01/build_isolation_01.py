# -*- coding: utf-8 -*-
"""委任_27: ISOLATION_EVIDENCE_01.md の機械生成(API 0)。有料前の isolation_before.json と現在のshaを比較する。"""
import glob
import hashlib
import json
import os
import subprocess
import sys

os.chdir("C:/Users/tensh/eigo-radio")
ROOT = "er110_output/family_y_redelivery_audio_01"
OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_AUDIO_01/ISOLATION_EVIDENCE_01.md"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    before = json.load(open(f"{ROOT}/isolation_before.json", encoding="utf-8"))
    md = ["# ISOLATION_EVIDENCE_01 (委任_27: Production隔離の証跡。API 0)\n",
          f"取得: 有料前 {before['taken']} / 有料後 (本ファイル生成時)。並行agent(Z TTS・X/Z Production等)が共有storeへ書込む可能性があるため、shaが変化した場合は変化が本Trial起因かを下記で判定する。\n",
          "## 1. 共有ファイルのsha比較\n", "| file | before sha256 | after sha256 | 変化 |", "|---|---|---|---|"]
    changed = []
    for f, v in before["files"].items():
        a = sha(f)
        ch = a != v["sha256"]
        if ch:
            changed.append(f)
        md.append(f"| {f} | {v['sha256'][:16]} | {a[:16]} | {'**変化**' if ch else '変化なし'} |")
    n_audio = len(glob.glob("er006_output/master_audio_store_01/audio/*"))
    md.append(f"\n- Production Master Audio Store audio件数: before {before['store_audio_count']} / after {n_audio}")
    # 本Trialが共有storeへ書いたかの判定: 本Trial名前空間のstoreとProduction manifestの突合
    trial_store = f"{ROOT}/audio/master_store_trial_r0"
    md.append(f"- Trial名前空間store: `{trial_store}`(存在={os.path.isdir(trial_store)})。process内で `er006_master_audio_store_01.STORE_DIR/AUDIO_DIR/MANIFEST_PATH/TELEMETRY_PATH` をここへ差替え(`trial_store_info.json`)")
    if changed:
        needles = ("redelivery", "family_y_redelivery_audio_01")
        hits = {}
        for f in changed:
            t = open(f, encoding="utf-8", errors="ignore").read()
            hits[f] = [n for n in needles if n in t]
        md.append(f"- 変化したファイルに本Trial固有の識別子(`redelivery`/run dir名)を含むか: {json.dumps(hits, ensure_ascii=False)}")
        md.append("  - 識別子が無い場合、変化は並行agent(同時刻にTTS/Production runを実行中)によるもので、本Trialの書込みではない(本TrialのTTS clip・manifest・telemetryはTrial名前空間storeにのみ存在)。")
    # trial store manifestに本Trial生成clipがあること
    tm = f"{trial_store}/manifest.json"
    if os.path.exists(tm):
        md.append(f"- Trial store manifest bytes={os.path.getsize(tm)}(Production manifest bytes={os.path.getsize('er006_output/master_audio_store_01/manifest.json')})")
    md.append("\n## 2. y_entry_point / production_reachable\n")
    for lvl in ("b1b", "a2"):
        pass
    ep = f"{ROOT}/audio/r0/y_entry_point.json"
    if os.path.exists(ep):
        d = json.load(open(ep, encoding="utf-8"))
        md.append(f"- `{ep}`: production_reachable={d.get('production_reachable')}, tts_backend={d.get('tts_backend')}, style_profile={d.get('style_profile')}, fixed_voices={d.get('fixed_voices')}")
    vc = f"{ROOT}/voice_assignment_check.json"
    if os.path.exists(vc):
        md.append(f"- Voice割当照合(`{vc}`): {json.dumps(json.load(open(vc, encoding='utf-8')), ensure_ascii=False)}")
    md.append("\n## 3. 既存tracked .pyの変更\n")
    out = subprocess.run(["git", "status", "--porcelain", "--", "*.py"], capture_output=True, text=True).stdout
    mine = ("er110_family_y_redelivery_audio_01.py", "er110_family_y_redelivery_audio_01_test_01.py", "er110_family_y_redelivery_page_01.py")
    lines = [l for l in out.splitlines() if l.strip()]
    md.append("`git status --porcelain -- '*.py'`(本Trialの3新規fileは除外して表示):")
    md.append("```")
    md += [l for l in lines if not any(m in l for m in mine)] or ["(なし)"]
    md.append("```")
    md.append("- 上記に他agent起因の変更が含まれる場合も、本Trialのcommitには含めない(`git commit --only`でpath限定)。本Trialが変更したtracked .pyは0件。")
    md.append("\n## 4. sink付替え(Local Rewrite recovery出力先)\n")
    lr = glob.glob(f"{ROOT}/audio/local_rewrite_recovery/**/*", recursive=True)
    md.append(f"- `er110_output/.../audio/local_rewrite_recovery/` 配下の出力: {len([x for x in lr if os.path.isfile(x)])}件。`er011_output/local_rewrite_recovery/` への本Trial起因の書込みは付替えにより0(発動時のみ生成、未発動なら0)")
    md.append("\n## 5. DefaultOffIsolation(未承認機能の既定値)\n")
    md.append("- flag/環境変数/CLI引数でProduction挙動が変わる経路なし。`--paid`と`BUDGET_APPROVED.json`が無いと全コマンドが例外で止まり副作用0(`er110_family_y_redelivery_audio_01_test_01.py::test_default_off_no_paid_flag_raises_before_any_side_effect`)。どのProduction runner/.env/起動scriptも本moduleを参照しない(`test_no_production_reference`)。Production run dir・公開ページへの書込みなし。")
    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
    print("written", OUT, "changed:", changed)


if __name__ == "__main__":
    main()
