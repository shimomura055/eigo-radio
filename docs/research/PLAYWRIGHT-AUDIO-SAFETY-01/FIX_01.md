# PLAYWRIGHT-AUDIO-SAFETY-01 FIX_01(修正内容。API 0・Production生成経路の判定ロジック変更なし)

## 1. 何を作ったか
`tools/playwright_safe_01.py`(新規・共通helper)+ `tools/playwright_safe_01_test_01.py`(14 test)。既存 script は
`from playwright.sync_api import sync_playwright` を `from playwright_safe_01 import sync_playwright` に**1行置換**するだけで、`with sync_playwright() as p:` 以降は無変更で動く(drop-in)。

| ユーザー要望 | helperの対策 |
|---|---|
| 2 音声が不要なtestで音を出さない | (a) 全ページにinit script: `HTMLMediaElement.play` 時に `muted=true / volume=0` を強制し、解除・音量上げも無効化(**WebKit/Firefoxにも効く=今回の原因経路**)。(b) Chromiumは `--mute-audio` を明示(Playwright既定と二重化)。(c) headless強制(`headless=False` は `PW_SAFE_ALLOW_HEADED=1` が無い限りheadlessへ)。(d) `play()` 自体は動くため `currentTime`/`timeupdate` 依存の既存testは維持(無音で同じ結果)。(e) 再生を全く使わないscript 10本は `sync_playwright_noplay`(`play()` をno-op化)。(f) 実音声が必要なtestだけ `allow_audio=True` **かつ** env `PW_SAFE_ALLOW_AUDIO=1` の二重明示でのみ解除(警告log)。 |
| 3 終了/異常終了で確実にbrowser・子processが消える | (a) try/finally+`with` で browser close、(b) `atexit` と signal(SIGINT/SIGTERM/SIGBREAK)、(c) **Windows console ctrl handler**(Ctrl+C/Ctrl+Break/閉じる/ログオフ/シャットダウンで別threadから即Playwright木をkill。PythonのSIGBREAKはmain threadが `time.sleep`/asyncio待機中だと届かないため)、(d) **Job Object(KILL_ON_JOB_CLOSE)**: pythonが `taskkill /F` 等で強制終了されても、Playwright driver/browser子孫がOSにより必ず消える、(e) 終了時に子孫のPlaywright系(`ms-playwright`配下・driver)を走査し残存をkill、(f) 起動時に「親が死んだ孤児の ms-playwright browser」を回収。 |
| 4 長時間継続させない | (a) 全体hard timeout(既定600秒。`sync_playwright(hard_timeout_s=…)` / env `PW_SAFE_HARD_TIMEOUT_S`)。超過でbrowser木をkillし rc=124 で終了。(b) page操作timeout(既定30000ms=Playwright既定と同じ。`page_timeout_ms` / env `PW_SAFE_PAGE_TIMEOUT_MS`)。(c) 起動時に**同一command lineの別python processを検出したら rc=75で中止**(env `PW_SAFE_ALLOW_DUP=1` で許可。同一script別引数は警告のみ=並列実行は可)。 |

## 2. 移行範囲(全Playwright script)
- Python 89本(`migrate_playwright_imports_01.py`で機械置換・冪等): `git grep "from playwright.sync_api import sync_playwright"` の残存 **0**(delegation_log除く)。うち再生を使わない10本は `sync_playwright_noplay`、他79本は無音(mute)。置換後の全89本が自身の位置で `playwright_safe_01` をimportできることを `check_migrated_imports_01.py` で確認(89/89)。
- 生CDP `*.mjs` 10本(`--headless=new` の実Chromeをspawn): `--mute-audio` と `--autoplay-policy=user-gesture-required` を追加し、`process.on('exit')` で必ずChromeをkill(`patch_mjs_headless_chrome_01.py`・冪等、`node --check` 全PASS)。
- `observe_caption_prod_01.py`(今回の主因script)を個別強化(`patch_observe_caption_01.py`): `--hard-timeout-s`(既定1800秒=54 combo規模でも足りる値)・`run_view` の browser close を `try/finally` 化。観測ロジック・チェック項目は無変更。
- **Production生成経路**: `er135_enduser_page_verify_01.py`(`er135_enduser_page_01.py build/verify-only` が呼ぶ「公開ページの再生検証」)も import 行を置換した(**判定ロジック・閾値・出力は無変更**、起動引数とtimeout/終了保証のみ)。この検証が従来どおり通ることを `er135_enduser_page_test_01.py`(121 test OK)と実機 observe(pc/mobile/chromium・webkit)で確認。

## 3. 動作の変化(Fableへの注意)
- 修正前は `er135 verify` が10分超でも無限に待てたが、**修正後は1プロセスのPlaywright使用が600秒を超えると rc=124 で停止**(通常の1記事verifyは2〜数分)。長い正当runは env `PW_SAFE_HARD_TIMEOUT_S` で延長。
- **同一command lineの二重起動はrc=75で中止**(同じ記事を同じ引数で並行して2回走らせない)。引数が違う並列は従来どおり可。
- 音声は無音になるが `play()`/`currentTime` は進むため、既存の同期・字幕・seek検証は同じ結果になる(実機: Chromium pc/mobile 4 combo 全PASS・WebKit pc std PASS)。

## 4. 残るリスク(正直に)
- WebKit は Windows の Audio Session 自体は作る(Active)が、media要素の `muted/volume` 強制により既定デバイスの実出力peakは無音基準(2.3e-10)だった。最初のplay前にmutedを強制しているため初期のもれはないが、WebKit固有APIで `muted` 強制をすり抜ける再生経路(例: `MediaSource`+WebAudio直接出力)が将来入ると鳴りうる。`AudioNode.connect(destination)` のno-op化は入れてある。
- Job Object は Win8+のネストJob前提(Win11で動作確認)。作成失敗時は警告ログのみで他の保証(atexit/signal/ctrl handler/hard timeout)は残る。
- Firefox 用の音量pref(`media.volume_scale=0`)は未使用・未テスト(repo内にFirefox利用なし)。

## 5. sonnet-worker.md への追記提案(実編集はFable承認後。本タスクでは編集していない)
> ### Playwright/ブラウザ自動操作(2026-10-31 PLAYWRIGHT-AUDIO-SAFETY-01)
> - Playwrightを使うscriptは `from playwright_safe_01 import sync_playwright`(`tools/playwright_safe_01.py`)経由を必須とする。`from playwright.sync_api import sync_playwright` を直接使わない。
> - 既定は無音(init script+`--mute-audio`)・headless・hard timeout 600秒・同一コマンド二重起動禁止。音声が必要なtestだけ `allow_audio=True` と env `PW_SAFE_ALLOW_AUDIO=1` を明示(ユーザーが聴く用途に限る)。音声不要なtestは `sync_playwright_noplay`。
> - 長時間runは `hard_timeout_s` を明示し、background起動時はPIDを記録して完了後に `ms-playwright` 配下の残存processが0であることを確認する。生CDPのChrome(`--headless=new`)をspawnする場合も `--mute-audio` を付け、exit時にkillする。
