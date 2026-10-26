# BUILD_03 — 委任_03 `_03` 先行公開ページの構成(API 0・費用0)
## 構成と決定
- URL: https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/index.html
- **Adv通し音声は作らない**: 正式CLI(`er121_family_y_runner_01.py --help`)に level限定の引数は無く(`--stages`/`--only-segments`のみ)、`stage_gate`(`er121_family_y_runner_01.py` stage_gate)と`stage_assemble`は全level(a2,b1b)を対象にするため、Std 2 segmentのHR待ち(委任_02のL2/L3でrc=2・`FAMILY_Y_GATE_BLOCK`)の間は組立もpagesも走らない。委任文のとおり組立せず、正式CLIの再起動もしていない(rc=2の再実行は情報を増やさないため。起動0回)。
- 代わりに、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_page_03.py --segments-only` で、run dir全体をscratchへ複製したうえで既存関数(`load_y_sources`→`apply_y_gain`→`build_b1_key_phrase_blocks`、組立の部品。通し音声・timelineは作らない)により**通し版と同じgainを掛けたAdv segment**をmp3化して個別再生。run dirは読み取りのみ(後述)。Intro/Notification/Outro/番号は省略。
- 順序(Y構成): Welcome→Topic intro→Preview intro→Preview→KP intro→KP1-3→Full story intro→Comment 1→Lead→(紹介n→Voice n)×3→Comment 3→Closing。Comment 2なし。
## ページ節
1. 状況(`#status`)/2. Voice 1〜3旧新比較(`#compare`: 旧`_02`の`adv_*`のVoice行mp3を`compare_old/`へ複製、新=gain適用済みPD06版、WPM前後(`wpm_01.json`)、WPM全表、部位別Style前後表(`regen_evidence_01.json`)。S9未評価・ユーザー判断項目と明記)/3. Advanced修正版(`#advanced`、19 segment・約279.1秒)/4. Std承認待ち2 segment(`#std_hr`、6 take個別再生+OpenAI/Azure転写+台本との語句差)/5. Std通過16 segment(`#std_ok`、素の音声・音量調整前)。
## コマンド全文
- `.venv\Scripts\python.exe docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_page_03.py --segments-only`(API 0。ffmpegはimageio_ffmpeg同梱)
- 検査: scratch `/tmp/vf.py` 相当(VERIFY_03.md)。`stop_scope_check_01.py --managed-id FAMILY-Y-STYLE-PROFILE-FIX-01 --run-dir er121_output/family_y_production_01/redelivery_fee/run_style_fix_01 --out docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/stop_check_03.json`
## 成果物
`user_test/family_y_production_redelivery_fee_03/`: `index.html`、`audio/adv_00..18.mp3`(19)、`compare_old/adv_voice{1,2,3}_old_default.mp3`(3)、`std_hr/std_{y_voice_1,preview}_take{1,2,3}.mp3`(6)、`std_ok/*.mp3`(16)、`build_summary_03.json`。サイズ約9MB。
## run dir読み取り専用の確認
初回の試走でAdv Gate検査が`b1b/audit/key_phrase_source_gate.json`(Gate副産物)をrun dirへ書いたため、直ちに削除して原状へ戻し、以後はrunを丸ごとscratchへ複製して実行(最終build後 `find run -newermt` で新規更新0を確認)。旧`_01`/`_02`は無変更。
