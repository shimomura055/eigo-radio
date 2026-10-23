# PLAY_VERIFY_04: 公開ページのPlaywright実再生検証(委任_10、Advanced完成・Standard人物1保留版)
URL: https://shimomura055.github.io/eigo-radio/user_test/family_y_trial_03/index.html (commit 3868bc37c公開後)
証跡: `er110_output/family_y_persona_trial_01/audio/it3/play_verify_04.json`(Chromium、`er110_family_y_persona_audio_play_verify_01.py`)。
結果: HTTP 200 / audio要素42本(Adv 25本[通し1+パート別24、Key Phrase 6本含む]+Std 17本[パート別、Key Phrase 6本含む])すべて再生OK(plays_ok=42, failed=0)、seek_ok_all=true、Adv全編通し 342.07秒(`audio/adv_full.mp3`)、HTTP>=400なし、console error 0、file://参照なし、Trialラベル表示、Std/Advタブ切替OK、KP表6。
範囲の限定: **Standard全編通しは未作成**(人物1がHR Lock、`AUDIO_QA_04.md`)。Stdはパート別のみ(人物1は「人間確認待ちのテイク」と明示)。
標準ページ検査(`it3/page_standard_check.json`): Advanced対象。11項目中10 PASS(全編再生・再生順・Preview/Full Story・Comment・Key Phrase 3行・no_file_scheme・no_A2_B1_label・audio_files_exist)。**1項目FAIL**: `Advanced:no_internal_info_in_script`が、設計済みの見出し読み上げ(`One Voice: The bad guy at breakfast`等、Y design [USER_03]の公式見出し)を`Voice:`パターン(X/Z用の内部情報検出regex、`er_user_listening_page_common_01.py:126`)で誤検知。共通moduleは無変更・検査の回避もしていない(Fable判断候補: Y見出しをregexの例外とするかの整理)。
