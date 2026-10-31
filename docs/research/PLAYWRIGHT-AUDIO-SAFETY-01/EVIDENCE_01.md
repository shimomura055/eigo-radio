# PLAYWRIGHT-AUDIO-SAFETY-01 EVIDENCE_01(検証結果。API 0。実行日2026-10-31 JST)

証跡置き場: `docs/research/PLAYWRIGHT-AUDIO-SAFETY-01/evidence_01/`

## 0. 即時緩和(手順0)
開始時 `tools/disk_guard_01.py --hook` = `OK free=66.0GB`。`tools/stop_scope_check_01.py --managed-id PLAYWRIGHT-AUDIO-SAFETY-01` = rc=0(stop=false)。
稼働process列挙(Win32_Process、python/pythonw/chrome/chromium/msedge/headless_shell、cmdlineに observe_caption_prod_01 / playwright / ms-playwright): **該当 0 件**(残存なし=killしたprocess 0。範囲外のpython=range_server・http.server・ユーザーのChrome/WebView2は触れていない)。作業終了時も `ms-playwright` 配下process = 0。

## 1. 単体・統合test(`tools/playwright_safe_01_test_01.py`、実Chromium/WebKit起動、14 test、2回連続 OK)
`evidence_01/unit_test_output.txt`:
- 起動引数: `--mute-audio` 含有・headless・autoplay policy(既定user-gesture-required、呼出側指定は維持・block_playは強制)・headed要求のheadless強制・`allow_audio` の二重明示。
- 実ブラウザの実cmdline(Win32_Process): メインprocessに `--mute-audio`・`--autoplay-policy=no-user-gesture-required`・headless を確認。
- media要素: `a.muted=false; a.volume=1; play()` 後も `muted=true, volume=0`、かつ `paused=false, currentTime>0.5`(**再生は進む=既存testの時間依存は維持**)。WebKitでも同じ。
- `block_play=True`: `play()` が no-op(`paused=true, currentTime=0, __pwSafePlayCalls=1`)。
- **通常終了/例外終了/強制終了(`taskkill /F` でpython本体のみ)/Ctrl+Break/hard timeout の各後に、ブラウザ・driver子孫が 0**(PID生存確認)。強制終了はJob Object、Ctrl+Breakはconsole ctrl handler(stderrに `console ctrl event`)。
- hard timeout(`hard_timeout_s=5`): rc=124・20秒以内に終了・子孫0・stderrに `HARD TIMEOUT`。
- 重複起動: 同一cmdlineの2本目が rc=75・stderrに `DUPLICATE`。

## 2. 全script移行の整合
- `evidence_01/migrated_imports_check.txt`: 置換89本 `import_ok=89 bad=0 noplay=10`、`from playwright.sync_api import sync_playwright` 残存 0。
- 生CDP `*.mjs` 10本: `node --check` 全PASS(`--mute-audio` 追加・exit hook追加)。
- 既存test: `er135_enduser_page_test_01.py`(121 test OK、verify moduleの静的検査含む)・`er135_enduser_align_test_01.py`(48 OK)・`er132_lr_overlay_pages_01_test_01.py` rc=0。

## 3. 実機: 修正版 observe を1記事(family_z_melos_kphr_evidence_r3、ローカル `user_test`)で実行
`measure_observe_run_01.py` が実行前/中(4秒ごと)/後にprocessを採取。
### 3-1 Chromium(pc+mobile × std+adv、4 combo、125.6秒、rc=0) — `observe_run_measure.json` / `observe_run/observe.json`
- 全4 combo PASS(`playing_8s.all_playing=true`、字幕=ハイライト一致 `playing_cap_equals_jhl_on` 含む全check PASS)=機能維持。
- 実行前: Playwright系process **0**、chrome系 **33**(ユーザーChrome等)→ 実行中: Playwright系 5〜6 → 実行後: Playwright系 **0**、chrome系 **33**(ユーザーのChromeは影響なし)。
- ブラウザ本体process 4個(browser起動4回)すべて、Win32_Process cmdline に `--mute-audio` と headless を含む(`browser_main_processes`)。
### 3-2 WebKit(今回の原因経路、pc std 1 combo、36.2秒、rc=0) — `observe_run_webkit_measure.json` / `observe_run_webkit/observe.json`
- PASS。実行前後のPlaywright系process 0→0。
- **実行中9回サンプルした Windows 既定デバイスの実出力peak = 全て 2.32830644e-10(無音基準)**。同時に `WebKitWebProcess` のAudio Sessionは Active(session peakは0.016=音量適用前のデータ)=**再生は進んでいるが、デバイスには出ていない**。旧方式の同条件(音量-66dBFSの試験音)は 8.2e-4 を出力(`audio_root_cause_probe.json`)。

## 4. 原因の機械確認(`audio_root_cause_probe.json`)
旧方式(素のPlaywright)と修正版helperの Chromium/WebKit を、実質聞こえない試験音(-66dBFS)で比較: 旧Chromium=無音(Playwright既定の `--mute-audio`)、**旧WebKit=デバイスへ実出力(peak 8.2e-4)**、修正版は両方無音。詳細は ROOT_CAUSE_01.md。

## 5. 限界・未確認
- 「音が鳴らない」の機械確認は、(a)起動cmdlineの `--mute-audio`、(b)ページ内 `muted/volume` 強制、(c)Windows既定デバイスの実出力peakが無音基準、の3点で行った(耳での確認ではない)。ユーザーの元の事象を正確に再現して鳴らす実験は、再度音を出す危険があるため行っていない(試験音は-66dBFS・数秒のみ)。
- ユーザー側で音が鳴った厳密な時刻は未取得(推定: 17:35〜17:52のWebKit run。ROOT_CAUSE_01.md)。
- 実機検証は1記事(Z melos)のみ。9記事×全viewの再走はしていない(helperは記事に依存しない)。
