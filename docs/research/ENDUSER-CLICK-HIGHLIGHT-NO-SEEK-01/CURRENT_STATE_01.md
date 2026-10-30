# CURRENT_STATE_01 (ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01 委任_01 Part 3、2026-10-30) 現状調査(読み取りのみ・コード変更0・API 0)

調査対象 = origin/main 058b38adb の `enduser_page_assets/rev01-f/app.js`(359行、現行ASSET_BUILD_ID)。rev01-g(03B作成途中版、別worktree 1d0607f30、参照のみ)も差分確認。

## 1. 英文クリック処理(現行=クリックでその文から再生)
| 項目 | 所在(rev01-f/app.js) | 内容 |
|---|---|---|
| クリックハンドラ(委譲) | :331-333 `$('content').addEventListener('click', …)` | `.sent`を`closest`し、`button`上でなく`syncKind !== 'none'`なら `seekSentence(se.dataset.sid)` を呼び`return` |
| seek+play本体 | :289-292 `seekSentence(sid)` → `playFull(r.start)`(:217) | `mode='full'; ensureSrc(main); withMeta(()=>{A.currentTime=at; playNow();})`。**再生中でも停止中でも必ず再生開始**(停止・一時停止中なら再生が始まる=廃止対象) |
| 同期データ未取得時 | :333 `syncKind !== 'none'` | sync_<lv>.json 取得失敗時はクリックが何もしない(選択表示もできない) |
| クリック対象の外見 | style.css:35 `.sent{cursor:pointer;…}` / :36 `.sent.on{background;box-shadow}` | ハイライトclassは`on`(英文`.sent.on`、日本語`.jhl.on`:106-107) |

## 2. 自動ハイライト(timeupdate相当)
- イベント: :353 `pause/seeked/timeupdate/loadedmetadata/durationchange → tick`、:352 `play/playing → kick`(rAFループ :293-294 `loop`: 再生中は毎フレーム`tick`、停止で0)、:354 `ended → tick`。
- `tick()` :276-288: `if (sync.length){ var ga = findActive(gt()); jaHold = ga ? null : gapGroup(gt()); highlight(ga); }`。つまり**停止中・一時停止中でも、pause/seeked/timeupdateのたびに現在位置の文へ`highlight()`し直す**(位置で決まる状態。選択状態を持たない)。
- `findActive` :269-274(二分探索)、`highlight(sid)` :255-267(`activeSid`更新、`.sent.on`付け替え、再生中のみ`scrollIntoView`)。`__EUP`(検証用フック) :287 に `active/jg/paused/mode/gt`。
- 英日連動: `jaLight(sid)` :243-250。`sidToG[sid]`(:133、`ja_align`の`g.ja`がnullでない群のみ登録)→`jgEls[g]`の`.jhl`に`on`。`sid`が非nullで`sidToG`に無い(=null群/対応未確定/ja_align無し)場合は`g=null`で**日本語は一切点灯しない(安全側)**。`sid=null`(文と文の間)のみ`jaHold`(同一群に挟まれた2秒未満の隙間)で維持。

## 3. モバイル・キーボード
- touch専用ハンドラなし。タップは`click`として上記:331に到達。`touchmove`/`wheel`は`lastUserScroll`記録のみ(:356、自動スクロール抑止用)。
- 英文`.sent`は`<span>`で`tabindex`/`role`なし(:24-30 `sentHtml`)=**キーボードで英文を選択・クリックする経路は現状ない**。キーボードの再生操作は`#pp`等のbuttonのみ。→ 今回の変更でキーボード経路は追加しない(新機能。範囲外)。

## 4. パート別の共通/個別
- 英文は全パート共通の`sentHtml(p)`(:24)で`.sent[data-sid]`を出力。使用箇所: Preview(:81)、Story(:76, :102)、Comment(:100)、In One Line(:105)。クリックは**`#content`への単一の委譲ハンドラ1つ(:331)**=パート別実装なし。
- 日本語訳: `trHtml`(:33)+`jaHtml`。rev01-fはstory/comment/oneline(`R.ASSET_TRANSLATION_KINDS` er135_enduser_rules_01.py:22)。**Previewはrev01-fでは訳を描画しない**(:81に`trHtml`なし)。rev01-g(03B)で`trHtml(p)`追加(diff :81)。LINK_KINDS=story/preview/comment/oneline(er135_enduser_page_01.py:819)。
- 英日対応データ(`ja_align`)が無いパート/文: `sidToG`未登録 → 英文のみ点灯、日本語は点灯しない(現行から不変の安全側)。Vocabulary/KPのbutton類は`.sent`を含まない(クリック対象外)。
- rev01-g差分(参照のみ): `mode='vocab'`(Vocabulary単体音声)、`playVocab/endVocab`、Preview訳。クリック処理(:331付近)は未変更の見込み(03B完了時に再確認)。

## 5. asset版管理と再produce経路
- 版: `er135_enduser_rules_01.py:12 ASSET_BUILD_ID="rev01-f"`、`er135_enduser_page_01.py:42 ASSET_DIR`、:45 `FROZEN_ASSET_DIRS={"family_z_in_a_grove_01":"rev01-e"}`、:1352-1358 verifyは凍結dirのみ旧assetで検証。`build_info.asset_build`に記録(:980)。
- asset生成: `enduser_page_assets/derive_assets_01.py`(DEV rev01-e `user_test/dev_enduser_page_01/*`を許可リストEDITSで機械的派生。DEVは読み取りのみ・不変、各editは旧文字列がちょうど1回)。ASSET_SHA256.json(+test T-ASSET-DIFF)で改変検出。
- 再produce: runner(X: er019_family_x_listening_page_01.py、Y: er121_family_y_runner_01.py:1381 `_build_enduser_page`、Z: er026_family_z_fiction_production_runner_01.py)がpages段で`er135_enduser_page_01`を呼ぶ → **新規生成・retry/resume/regeneration後のpages再実行は常に現行ASSET_DIR(=ASSET_BUILD_ID)から出力**。既公開dirへは`er135_enduser_page_01.py publish-copy`(:1701。enduser/だけcopy、dev index.html・音声は不変、copy先でverify+Playwright、失敗時は元へ戻す)。
- したがって**ASSET_BUILD_IDを新版へ上げるだけで、X/Y/Z×Std/Advの全6経路の新規生成・再生成に自動適用**される(Family別重複実装は不要)。既公開9dirへは再produce(API 0)で反映。

## 6. 既存verifyのクリック前提項目(要整合)
`er135_enduser_page_verify_01.py`(Playwright、PC 1280x900 + モバイル390x844 UA/has_touch :28-29):
- :273-277 F `sentence_click_plays_from_sentence` — **クリック→再生開始を期待**(新仕様で反転が必要)。
- :466-479 J3 / :484-496 J3b — 一時停止(`aud.pause()`)後にクリック→450ms待って`_consistent`(英日点灯がデータ通り)。**新仕様でもそのまま成立の見込み**(停止中の選択維持)。
- :539-546 M7 — `first_sid`をクリック→`#pp`を押して「一時停止」と見なす。**クリックで再生が始まる前提のため、新仕様では`#pp`が「再生開始」になりM7の意味が逆転する(修正必須)**。
- :523-536 J5(シーク/±10秒)は`#seek`/`#back10`系でクリック非依存。G系(:305-329)は`.btns .seek.from/stop`(ここから再生/停止ボタン)でクリック非依存。
- static test: `er135_enduser_align_test_01.py:423`(`ASSET_BUILD_ID=="rev01-f"`)、:437-440/:480/:485(app.js/style.cssをASSET_BUILD_IDで読む)、`er135_enduser_link_test_01.py:208-210` — 版上げ時にこの版固定assertを新版へ更新。
- Playwright基盤: 既存(importable)。新規ブラウザ基盤は不要。
