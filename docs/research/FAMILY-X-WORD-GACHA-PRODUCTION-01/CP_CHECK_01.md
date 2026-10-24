# CP_CHECK_01 (FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_01, 2026-10-24)

## §A 着手時確認
1. 正式初回Production経路: text=`er019_family_x_entertainment_production_runner_01.py --stage all`(Research→Ledger→B3→W-1 Writer R0-R2→Advanced→Standard)、audio=`er019_family_x_audio_production_runner_01.py --level both --stage all`(plan/scaffold/tts/assemble)。直近X Production(FAMILY-X-NEWS-2ARTICLES-E2E-02 uk_train_speaker_playback run_nws_02、`er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/entry_point.json`: runner=er019_family_x_audio_production_runner_01.py、tts_backend=speech_metadata_flash_lite、style_profile=fx_20261017)と同一経路・同一既定。slug=word_gacha、run=run_wg_01。
2. 仕様: CURRENT_SPECの該当節(Family X Production経路 W-1/RF、Entertainment、音声構造、KP、PNAP、中核数値丸め)は既配線(HEAD 00815e4d8)。runnerを既定引数で使い、本作固有のPrompt/機構/例外は追加しない(--themeにユーザー承認の混同禁止3点を記した、E2E-02と同形式)。
3. KP: A-1・課題②(所有格一般化)はPRODUCTION_WIRED(X/Z)=自動適用。課題①X2p'(UDR #179未回答)・G3は未承認=適用なし。X2p'は`er112_kp_gm_trial_0*.py`のDEV/Trial専用で、Production import graph(159ファイル)に含まれない(graph.txt中のer112該当0)。環境変数`EIGO_KP_GLOSS_ALIGNMENT`は未設定(既定、kill switch非発動)。DEV flagはONにしない。
4. ASR/TTS/retry/fallback/HR現行仕様。ASR数値・時刻修正のcommit d6d17562b(OPEN-487)/7d4ec5bc4(OPEN-491)/1d104d711(OPEN-494)は`git merge-base --is-ancestor`でHEAD(00815e4d8)に含まれることを確認。
5. 作業ツリー: X Production経路のimport graph(2 runner + er_user_listening_page_common_01.py起点、159ファイル)のうち`git status --porcelain`でM/D/??のあるものは**0件**(他agent差分は`CURRENT_SPEC.md`・docs/research・er0*_output等のみで経路外=記録のみ)。
6. 日次予算: BUDGET_PLAN_01.md参照。
7. 旧テーマ「AIも『一人で正しいより、みんなで間違えたい』?」: repo内Grep(逐語句2種、er0*_output含む全体)で着手痕跡0(ユーザー原文保存ファイル自身のみ該当)。`er019_output`に該当slugなし。着手なし・費用0。
8. STOP確認: `tools/stop_scope_check_01.py --managed-id FAMILY-X-WORD-GACHA-PRODUCTION-01` rc=0(stop_check_00.json / stop_check_text.json)。
