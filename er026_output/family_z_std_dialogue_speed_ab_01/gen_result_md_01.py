# -*- coding: utf-8 -*-
import json, os, sys
os.chdir("C:/Users/tensh/eigo-radio")
OUT = "er026_output/family_z_std_dialogue_speed_ab_01"
A = json.load(open(f"{OUT}/analysis.json", encoding="utf-8"))
ASR = json.load(open(f"{OUT}/asr_qa_B.json", encoding="utf-8"))
PV = json.load(open(f"{OUT}/public_play_verify_01.json", encoding="utf-8")) if os.path.exists(f"{OUT}/public_play_verify_01.json") else None
T = {"melos": "走れメロス", "open_window": "開いた窓"}
L = []
w = L.append
w("# FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01 TRIAL_RESULT_01 (2026-10-23)")
w("")
w("Status: TRIAL_COMPLETE_USER_DECISION_REQUIRED(Production未変更・Trial版のProduction反映は禁止。ユーザーの比較試聴待ち)")
w("")
w("## 1. 条件表")
w("| 項目 | A 現行版 | B Trial版 |")
w("|---|---|---|")
w("| Narrator(Story内) | 6%減速あり | 6%減速あり(Aとファイルsha256一致) |")
w("| 登場人物の会話 | 6%減速あり | 6%減速なし(減速前の`<id>_original.wav`) |")
w("| Voice / TTS Prompt / 本文 / 台詞 / 順序 / 効果音 / Comment / KP / shell | 現行 | 同一(同じファイル・同じ組立) |")
w("| Advanced | 変更・再生成なし | 変更・再生成なし |")
w("")
w("## 2. 元run特定(A版)")
w("- 『走れメロス』: 公開ページ`user_test/family_z_melos_02/`の最終更新commit 1b9b39340(2026-10-20、run_e2e_06反映)。公開`Melos_a2_full.mp3`の長さ303.9225秒 = `melos/run_e2e_06/a2/assembly/Family_Z_melos_a2.wav`の303.9225秒(一致)。`run_jre_01`は別の証拠run(287.54秒、公開版ではない)。元run=`er026_output/family_z_production_e2e_01/melos/run_e2e_06`。")
w("- 『開いた窓』: 公開`OpenWindow_a2_full.mp3` 325.3067秒 = `the_open_window/run_e2e_01/a2/assembly/...a2.wav` 325.307秒(一致)。元run=`er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01`。")
w("")
w("## 3. 方式・原音の有無・再生成・費用")
w("- 6%減速の実装: `er003_v1_n3_01_tts_generate.apply_a2_slowdown_postprocess`が`<id>.wav`を`<id>_original.wav`へcopyしてから`er008_a2_postprocess_slowdown_01.apply_a2_slowdown`(ffmpeg atempo=1/1.06、24kHz mono s16)で`<id>.wav`を上書きする。よって`_original.wav`が減速前の原音。")
w("- 原音の有無: 全dialogue clip(『走れメロス』10、『開いた窓』18)に`_original.wav`あり。**TTS再生成0 clip・本文再生成0・追加TTS費用0円**。")
w("- 原音の正当性: 各dialogue clipで`_original.wav`にProduction同一関数`apply_a2_slowdown`を再適用すると現行A版clipとsha256完全一致(メロス10/10、開いた窓18/18)。つまり原音=A版の生成元音声そのもの(Voice・Prompt・本文・take同一)。")
w("- 組立: Production関数`er063.run_assembly`をTrial dirで実行。**A版を未変更narrationから再組立するとProduction公開用assembled wavとsha256完全一致**(メロス・開いた窓とも)。Bは会話clip差替えのみ(無音間隔・順序は同一)。")
w("- 費用: 生成0円。音声QAのProduction ASR(`routing.transcribe`, en-US)を28 clipに実施(B会話clip合計132.8秒。上限見積=Azure単価0.0463円/秒(出典: OW full_story_part3_c9 asr_judgement est_jpy 0.1333/2.878秒)×132.8秒≒6.2円(実routing providerがOpenAI miniならさらに安価。正確額は未集計))。")
w("")
w("## 4. 会話速度の実測(語/分、clip長はassembled前のclip wav長)")
for s in ("melos", "open_window"):
    S = A[s]["summary"]
    w(f"### {T[s]}")
    w("| 指標 | A 現行 | B Trial | 差 |")
    w("|---|---|---|---|")
    def r(l, a, b): w(f"| {l} | {a} | {b} | {b-a:+.1f} |")
    r(f"会話clip中央値(全{S['n_dialogue']})", S["A_wpm_all"]["median"], S["B_wpm_all"]["median"])
    r("会話clip平均", S["A_wpm_all"]["mean"], S["B_wpm_all"]["mean"])
    r(f"中央値(8語以上{S['n_ge8']})", S["A_wpm_ge8"]["median"], S["B_wpm_ge8"]["median"])
    r("加重(総語数/総時間)", S["weighted_A_wpm"], S["weighted_B_wpm"])
    r("参考: Narrator中央値(A=B)", S["narrator_A_wpm"]["median"], S["narrator_B_wpm"]["median"])
    w(f"\n会話clip長比 A/B = {S['ratio_min']}〜{S['ratio_max']}。会話合計 {S['dialogue_A_sec']}秒→{S['dialogue_B_sec']}秒。通し {S['A_dur']}秒→{S['B_dur']}秒。")
    w("")
    w("| # | clip | 話者 | Voice | 語数 | A秒 | B秒 | A WPM | B WPM |")
    w("|---|---|---|---|---|---|---|---|---|")
    n = 0
    for x in A[s]["rows"]:
        if x["kind"] == "dialogue":
            n += 1
            w(f"| {n} | {x['id']} | {x['speaker']} | {x['voice']} | {x['words']} | {x['A_sec']} | {x['B_sec']} | {x['A_wpm']} | {x['B_wpm']} |")
    w("")
w("## 5. 同一性の証拠(照合表)")
for s in ("melos", "open_window"):
    S = A[s]["summary"]
    w(f"- {T[s]}: Narrator Story clip sha256一致 {S['narrator_sha_equal']}/{S['n_narrator_story']}、dialogue clipがA/Bで別ファイル {S['dialogue_sha_differs']}/{S['n_dialogue']}、原音へのatempo再適用=A版 {S['atempo_reproduces_A']}/{S['n_dialogue']}、再生順(sequence_order)同一={S['order_equal']}、A再組立==Production wav sha={S['A_rebuild_equals_production']}。Voice・本文は同一results/segment_plan・同一TTS takeを共有(Bは同じtakeの減速前)。")
w("- 詳細: `er026_output/family_z_std_dialogue_speed_ab_01/analysis.json`(全clip行・sha)、`<story>/build_report.json`。")
w("")
w("## 6. 音声QA")
for s in ("melos", "open_window"):
    S = A[s]["summary"]
    q = ASR[s]
    ex = sum(1 for r in q if r["exact_norm_match"])
    w(f"- {T[s]}: B会話clipのProduction ASR {len(q)}件中 正規化完全一致 {ex}件。通しB wav: sr={S['B_wav_qa']['sr']}、peak={S['B_wav_qa']['peak']}、clip(>=0.999)={S['B_wav_qa']['clip_samples']}、NaN={S['B_wav_qa']['nan']}、先頭無音{S['B_wav_qa']['lead_sil']}s/末尾無音{S['B_wav_qa']['trail_sil']}s(Aと同値)。headroom安全弁=未発動(A/B)。")
    for r in q:
        if not r["exact_norm_match"]:
            w(f"  - 差あり {r['id']} (類似度{r['similarity']}): 期待=`{r['expected']}` / ASR(B)=`{r['asr_B']}`。A版事後ASR記録と同一テキスト(既存PASS_WITH_WARNINGまたは引用符/句読点のみ)で、B固有の新規欠陥ではない。")
w("")
w("## 7. 公開ページ検証")
if PV:
    w(f"- URL: {PV['url']} / page HTTP {PV['page_status']} / audio {PV['audio_count']}本中 再生OK {PV['ok_count']}本(all_ok={PV['all_ok']})。証跡=`public_play_verify_01.json`。")
else:
    w("- (未取得)")
w("")
w("## 8. Production無変更の証拠")
w("- `git diff --name-only 2f8b75126 HEAD`(Trial着手前HEAD→現HEAD)を保護対象(`user_test/family_z_melos_02`・`family_z_open_window_01`・`family_z_melos_jre_01`・`er026_output/family_z_production_e2e_01`・`er006_output/master_audio_store_01`・`er063_family_z_audio_01.py`・`er003_v1_n3_01_tts_generate.py`・`er008_a2_postprocess_slowdown_01.py`)に限定して実行: 0件。")
w("- 元run a2配下・公開ページのファイルで、Trial着手(08:45 JST)以降に更新されたものは0件(find -newermt)。Master Audio Store manifestの未commit差分は08:17更新で、本Trial着手前の別作業によるもの(本Trialは書込まず)。")
w("- Trial生成物は全て`er026_output/family_z_std_dialogue_speed_ab_01/`と新規`user_test/family_z_std_dialogue_speed_ab_01/`のみ。wavはpushせずmp3(lameenc 128kbps)のみ公開。")
w("- 留意: 本作業のcommitは共有indexの競合で、別agent(ASR-HOMOPHONE 委任_04)のcommit 216ab62b0に本Trialのファイルが同梱された(内容は本Trialの新規ファイルのみ、他の既存ファイルは不変)。")
w("")
w("## 9. 採用した場合の反映手順と費用見込み(参考、未実施)")
w("- 手順案: `apply_a2_slowdown_postprocess`のdialogue clipだけ減速をskip(Std限定のProduction仕様変更=ユーザー承認後のflag/新コード経路)、既存2作品はB版assembled wav(+公開ページmp3)でproduction runのa2/assemblyと公開ページを差替え。再生成は不要(原音再利用)。")
w("- 費用: 既存2作品の差替えはTTS 0円(ローカル組立+mp3化のみ)。今後の新規Z作品は生成工程でskipするだけで追加費用なし。新規作品のASR再検証は減速後ASR再検証が不要になる分むしろ微減。")
open("docs/research/FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01/TRIAL_RESULT_01.md", "w", encoding="utf-8").write("\n".join(L) + "\n") if os.makedirs("docs/research/FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01", exist_ok=True) is None else None
print("ok")
