# PLAY_VERIFY_05: 公開ページのPlaywright実再生検証(委任_11、Std V1=B2言い換え後の最終テイク差替え版)
URL: https://shimomura055.github.io/eigo-radio/user_test/family_y_trial_03/index.html (commit dd42be6b4公開後)
証跡: `er110_output/family_y_persona_trial_01/audio/it3/play_verify_05.json`(Chromium、`er110_family_y_persona_audio_play_verify_01.py`)。
結果(再実行): HTTP 200 / audio要素42本(Adv 25[通し1+パート別24]+Std 17[パート別])すべて再生OK(plays_ok=42, failed=0)、seek_ok_all=true、Adv通し342.07秒、HTTP>=400なし、console error 0、file://なし、Trialラベル表示、タブ切替OK、KP表6。(初回実行はGitHub Pages反映直後に`std_part_02.mp3`が一時503で41/42だったが、再実行で解消。コード・ページ変更なし。)
範囲の限定: **Standard全編通しは未作成**(人物1がHR Lock、`AUDIO_QA_05.md`)。Stdタブの人物1パート(`std_part_04.mp3`)は最終テイク(attempt8)に差替え済みで「人間確認待ちのテイク」と明示。標準ページ検査: Advanced `no_internal_info_in_script`がY見出し`One Voice:`を誤検知する既存FAIL(共通regex無変更)は委任_10と同じ。
