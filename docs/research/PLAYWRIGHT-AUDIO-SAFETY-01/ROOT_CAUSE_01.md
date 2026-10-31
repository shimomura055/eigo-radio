# PLAYWRIGHT-AUDIO-SAFETY-01 ROOT_CAUSE_01(原因特定。API 0)

ユーザー原文: `docs/pm/delegation_log/2026-10-31_PLAYWRIGHT-AUDIO-SAFETY-01_USER.md`(逐語保存)。

## 結論(1行)
**音声を実際にWindowsへ出したのは、Playwright の WebKit(`observe_caption_prod_01.py --browser webkit`)。** Playwright 標準の headless Chromium は元々 `--mute-audio` が付くため無音で、WebKit だけが「mute 引数が無い」うえ、スクリプトが JS で `A.play()`・再生ボタン click・seek を繰り返して**複数作品を連続再生**していた。強制終了した瞬間に止まったのは、ブラウザ子processが親(python)と一緒に消えたため。

## 根拠(観測値)
1. **Playwright 既定**: `.venv/Lib/site-packages/playwright/driver/package/lib/coreBundle.js` の chromium 起動部に `if (options.headless) { push("--headless"); push("--hide-scrollbars","--mute-audio",...) }`(2か所)。旧方式の実cmdline: `evidence_01/old_style_launch_cmdline.json`(`has_mute_audio_by_playwright_default=true`)。→ Chromium headless は鳴らない。
2. **Windows Audio Session 実測**(`evidence_01/audio_root_cause_probe.json`、再現は `audio_root_cause_probe_01.py`。再生音は約-66dBFSの200Hz矩形波を数秒だけ=実質聞こえない。出力デバイスの実出力peak=`ENDPOINT_MASTER_METER`で判定):

| 条件 | ブラウザのAudio Session | 既定デバイスへの実出力peak(無音基準=2.3e-10) |
|---|---|---|
| 旧: 素のPlaywright Chromium headless | あり(Active)だが peak 0 | 2.3e-10(無音) |
| 旧: 素のPlaywright **WebKit** | **WebKitWebProcess Active** | **8.2e-4(実際にスピーカへ出力)** |
| 修正: helper経由 Chromium | なし | 2.3e-10(無音) |
| 修正: helper経由 WebKit(init scriptでmuted/volume強制) | Active(sessionは存在) | **2.3e-10(無音)** |

3. **WebKitを使う唯一のscript**: `git grep` で `webkit` を launch するのは `docs/research/ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01/tools/observe_caption_prod_01.py:35`(`--browser webkit` 選択時のみ。`choices=["chromium","webkit"]`)。他のPlaywright script 88本は Chromium。
4. **実行ログ**(caption worker の scratchpad `capw/`。mtime/内容):
   - `pub_webkit/observe.json`(mtime 17:38:46、`shots` 作成 17:35:20): browser=`webkit`、3作品(family_x_meta_waddle_world / family_y_production_surname_choice / family_z_melos_kphr_evidence_r3)×std/adv=**6 combo**、`playing_8s.all_playing=true` ×6、`kp_play` ×6、`vocab_play` ×5 → 1 combo あたり約23秒(推定: 8秒連続再生+seek+from-here+KP+Vocab のscript内待機合計)、**合計 約2分半(推定)の実音声を約3.5分で3作品ぶん連続再生**。
   - `pub_webkit_retry1/observe.json`(17:51:53): webkit 1 combo。
   - `pub_webkit2`(`obs_pub_webkit2.log` 17:52:13作成・0 byte、`observe.json` なし): **最後まで走らず中断された run**。ユーザーの「該当Pythonプロセスを終了した瞬間に音声が停止」と整合(推定。ユーザー側の厳密な発生時刻は記録なし)。
   - 同時間帯に `pub_pc` / `pub_mobile` / `pub_narrow`(Chromium、各9作品×2レベル=18 combo、17:25〜17:35)が並列実行されたが、これは無音(上記1.・2.)。
5. **ページ側の自動再生は無関係**: `enduser` ページ自体は読込時に再生しない(再生はscriptの `A.play()`・ボタンclick・`currentTime` 操作)。ただし観測scriptは `--autoplay-policy=no-user-gesture-required` を付け、JSの `play()` を許可していた(Chromium専用引数で、WebKitには効かない=WebKitはJS play()が通る)。

## 「なぜ止まらなかったか・長引いたか」(要望3・4の原因)
- `observe_caption_prod_01.py` は `run_view` 内で `br.close()` が最後の1行(try/finally外)。途中で例外が出ると browser が `with sync_playwright()` 終了まで残る。
- 全体timeout・重複起動検知なし。9作品×2レベル×3view を順次実行するため 10分近く走り、同じ処理が背景で再起動(webkit retry → webkit2)された。
- 親python が強制終了されたとき、Playwright の node driver 経由で browser を畳む保証は実装依存(Job Object等なし)。

## 取り扱い
- 他にPlaywright以外の自動ブラウザ: 生CDP `*.mjs` 10本(`--headless=new` の実Chrome。`--mute-audio` 無し)。再生は行わないフォーム確認だが、同種リスクがあるため `--mute-audio` を追加(FIX_01.md)。
