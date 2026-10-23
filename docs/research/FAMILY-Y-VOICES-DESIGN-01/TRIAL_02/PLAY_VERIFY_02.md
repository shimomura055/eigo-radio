# PLAY_VERIFY_02: 公開ページのPlaywright実再生検証(途中経過版)
URL: https://shimomura055.github.io/eigo-radio/user_test/family_y_trial_02/index.html (commit d87b32303公開後)
証跡: `er110_output/family_y_persona_trial_01/audio/it2/play_verify.json`(Chromium、`er110_family_y_persona_audio_play_verify_01.py`)
結果: HTTP 200 / audio要素18本すべて再生OK(plays_ok=18, failed=0)/ シークOK / HTTP>=400なし / consoleエラーなし / file://参照なし / Trialラベル表示 / Std・Advタブ切替OK。
範囲の限定: 全編通し音声がAdv・Stdとも未作成のため、「全編フル再生」は検証対象外(NOT_APPLICABLE)。検証したのはパート別音声のみ。
