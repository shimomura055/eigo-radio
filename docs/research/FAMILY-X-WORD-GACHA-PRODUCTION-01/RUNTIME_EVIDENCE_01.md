# RUNTIME_EVIDENCE_01 (FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_01, 2026-10-24) 【途中状態: Std完成・Adv全編はHR Lockで未組立】

## 起動履歴(すべて同一HEAD 00815e4d8、`TTS_EXECUTION_MODE=STANDARD`、`.venv\Scripts\python.exe`、各起動前 stop_scope_check rc=0=stop_check_*.json)
| # | 起動 | 結果 |
|---|---|---|
| 1 | `er019_family_x_entertainment_production_runner_01.py --theme <theme.txt> --slug word_gacha --out-dir er019_output/word_gacha/run_wg_01 --run-label run_wg_01 --budget-jpy 60 --stage all` (JST約17:54-18:03) | rc=0。Research→Ledger→B3→W-1 R0-R2→Advanced→Standard→RF。37.71円 |
| 2 | `er019_family_x_audio_production_runner_01.py --slug word_gacha --run run_wg_01 --level both --stage all --budget-jpy 60` (JST 18:03-18:29、cooldown600秒含む) | rc=0。plan/scaffold/tts完了。52.32円 |
| 3 | 同 `--stage assemble` | rc=0だがAdvは`BLOCKED_STYLE_PROFILE_GATE`(full_story_part3 STOPPED→FINAL_STYLE_RECORD_MISSING)、Stdは組立OK |
再起動0・approve_regenerate未実行・Gate迂回なし。

## text
Research gpt-6-luna、Ledger VERIFIED 13/AMBIGUOUS 0/REJECTED 0。B3(Min2)採用F03・F06、丸め overlay OK。W-1 R0→R1→R2、Advanced/Standard。RF issues=9(review queue保存)。費用37.706円(research 10.98/ledger 3.83/B3 7.65/writer 12.45/adv 0.39/std 0.44/RF約1.9)。事実検査=FACT_CHECK_01.md(混同禁止3点クリア、創作0)。

## audio(出力=er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/)
- Standard(a2): 11/11 segment OK、assemble OK 320.08秒、clipping無し、HR Lock 17件すべてRESOLVED、累計TTS>1: full_story_part3(2)・kp1_en(2)。PASS_WITH_WARNING 3件(事後試聴、非ブロッキング)。KP: pass it by / spark curiosity / by heart(KP英語3clip OK、KP3-ASR投票evidence 3/3)。
- Advanced(b1b): 9/10 segment OK、**full_story_part3=STOPPED/HUMAN_REVIEW_REQUIRED**(3回TTS試行すべてPrimary=ASR_VALIDATION_UNCERTAIN[「gacha」を「gotcha」と認識、他は全文一致]+Secondary(Azure)=TRUE_CONTENT_MISMATCH[句読点区切りで文が混線する脱落様出力]=NG_BOTH)。他のHR Lock 14件RESOLVED。累計TTS>1: in_one_line(2)。KP: star power / spark curiosity / tug at its sleeve(3clip OK)。
- 固有名詞アラーム: 0件(entity table 3件、うち証拠使用可1件。UR・Jackpotは weak)。「gacha」は実体表に載らず(一般語/借用語扱い)、PNAP受理境界の外。
- style_profile=fx_20261017、tts_backend=speech_metadata_flash_lite、KP gloss alignment flag=ON(source=default、EIGO_KP_GLOSS_ALIGNMENT未設定)、X2p'/G3は不使用。
- 費用: text 37.71 + audio 52.32 = 90.03円(上限100円内、目標70円は超過)。audio内訳 openai 2.59/gemini 17.60/openai_asr 4.64/azure 27.48。Adv part3の3回試行+cooldown600秒が主因(Azure Secondary費用)。

## 未完了(Fableへ)
Adv full_story_part3のHR Lock解除(approve_regenerate等はFable/人間権限)→Adv assemble→試聴ページ(`er019_nws2_final_page_01.py`)→page_verify→UDR登録・OPEN登録・DECISION_LOGは未実施。
