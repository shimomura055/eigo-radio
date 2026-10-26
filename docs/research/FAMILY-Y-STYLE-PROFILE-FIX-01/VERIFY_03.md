# VERIFY_03 — `_03` 先行公開ページの検査(委任_03、API 0)
| 項目 | 結果 | 根拠 |
|---|---|---|
| stop_scope_check(開始時) | rc=0 非停止 | `stop_check_03.json` |
| index.html・mp3存在/リンク | PASS | audio要素47(ユニーク44、compare節が本体行のmp3を再参照)、欠落0。mp3: audio 19・compare_old 3・std_hr 6・std_ok 16 |
| Advanced節 Comment 2不在 | PASS | `#advanced`〜`#std_hr`間に`Comment 2`/`comment_2` 0件(設計: `removed_by_spec`、`er121_family_y_audio_01.py` `_body_seq`) |
| Voice割当 | PASS | `voice_assignment.json` match=true(Voice1=Puck/Voice2=Zephyr/Voice3=Schedar)。Adv `tts_generation_results`のvoice実測=Puck/Zephyr/Schedar。Std Voice 2/3=Zephyr/Schedar、Std y_voice_1はreview lock中でvoice欄None(要求`y_tts_voice_requested`=Puck) |
| Algieba/v1cand混入 | 0件 | ページ本文grep |
| AI注意書き | PASS | `ys.check_y_page_notice` ok=True |
| 標準ページ検査`cp.check_page` | FAIL(想定内) | 通し再生/再生順script/Preview-Full story/KP表/内部情報検査は通し版を前提とする。先行公開(組立前)ページのため未達。委任_04で通し版追加後に再検査する(未達を隠さず記載) |
| run dir無変更 | PASS | 最終build後 `find run_style_fix_01 -newermt` 0件(初回試走でGate副産物`key_phrase_source_gate.json`が書かれ削除済み。BUILD_03.md) |
| 旧`_01`/`_02`無変更 | PASS | `git status`にdiffなし |
| HTTP 200(push後) | PASS | index.html および audio/adv_00,adv_12・compare_old/adv_voice1・std_hr/std_y_voice_1_take3・std_ok/y_voice_2 のmp3が200(Pages反映はpush後約6分) |
