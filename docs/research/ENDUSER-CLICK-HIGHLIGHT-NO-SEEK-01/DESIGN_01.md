# DESIGN_01 (ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01 委任_01 Part 3、2026-10-30) 英文クリック=選択ハイライトのみ(seek/play/pauseなし)

仕様正本 = docs/pm/delegation_log/2026-10-30_ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01_USER.md §1(:A)・§3。現状=CURRENT_STATE_01.md。コード変更0・API 0(本書は設計のみ。実装=委任_02)。

## 0. 11-8線引き
- 範囲内: 承認済みクリック仕様の実装(asset app.js/style.css)、既存verify(`er135_enduser_page_verify_01.py` F/M7)の整合修正、版固定test更新、Regression、既公開dirの再produce(API 0)。
- 範囲外(実装せずFableへ報告): 翻訳仕様変更、新学習機能、音声・本文の変更、asset以外のUI変更、`.sent`のキーボード操作性追加(現状ない=新機能)、日本語側`.jhl`クリックでの英文選択(新機能)、DEV rev01-eページ(`user_test/dev_enduser_page_01`、不変)。

## 1. 動作仕様(ユーザー原文§1 A + 競合規則)
(a) クリック: クリックした英文`.sent`を`on`、`ja_align`で対応する日本語群`.jhl`を`on`。`audio.play/pause/currentTime`を一切呼ばない。
(b) 再生中(`!A.paused`): 自動ハイライト優先。クリック直後に一瞬選択を描いてよいが、次の`tick`(rAFで毎フレーム)で`findActive(gt())`に戻る=選択は保持しない。
(c) 停止中・一時停止中(`A.paused`): 選択を維持。pause/seeked/timeupdate由来の`tick`が選択を消さない(現行はここで位置の文に上書きしてしまう=:285の`highlight(ga)`)。`ended`後(paused=true)も同様。
(d) 日本語未確定(`ja_align`無し/`g.ja==null`/Preview訳未描画等): 英文のみ点灯、日本語は点灯しない(現行`jaLight`の`sidToG[sid]||null`をそのまま利用。安全側不変)。
(e) 再生・一時停止・再開・シーク・停止・±10秒・ここから再生ボタン・KP/Vocabulary音声は不変。

## 2. 状態機械
状態変数(追加は1つ): `selectedSid`(null | sid)。既存: `activeSid`(表示中のEN)、`activeG`(表示中のJA群)。`is_playing = !A.paused`、`last_auto_id = findActive(gt())`(都度計算)。

```
            click(.sent, sidあり)                       tick()
   ┌──────────────────────────────────────┐  ┌──────────────────────────────┐
   ▼                                          │  │                                │
[AUTO]  is_playing:                          [SEL]  paused かつ selectedSid≠null:
 表示 = last_auto_id (EN) + その群(JA)         表示 = selectedSid (EN) + sidToG[selectedSid] (JA, null群なら無点灯)
   │ click & paused ─────────────────────────▶ selectedSid = sid ; highlight(sid)
   │ click & playing ─▶ highlight(sid)を描くのみ(selectedSidは保存しない) ─▶ 次tickで last_auto_id へ(=AUTOのまま)
   ▲ SEL --- 再生開始(play/playingイベント or tickで!A.paused検知) → selectedSid=null → AUTO
   ▲ SEL --- ユーザー位置操作(#seek input / #back10 / #fwd10 / ここから再生 / 全体再生 / 停止ボタン / setLevel / KP・Vocab再生) → selectedSid=null → AUTO(位置由来の表示へ)
```
`tick()`の変更点(唯一の分岐): `if (sync.length){ …ga…; highlight(A.paused && selectedSid ? selectedSid : ga); }`。ただし`jaHold`は`selectedSid`有効時は`null`に固定(選択の日本語を隙間保持で上書きしない)。`__EUP.active`は表示中ENのsid(選択時は選択sid)を返す(verifyの`_consistent`がそのまま使える)。`selectedSid`も`__EUP.sel`として露出(検証用、読取専用)。
- `highlight()`の再生中スクロール条件(`!A.paused`)は停止中選択では発火しない=クリックでページが勝手にスクロールしない(現行の停止時挙動と同じ)。
- 同期データ未取得(`syncKind==='none'`)でも、`sentEls`は存在し`sidToG`は`ja_align`のみ依存 → クリックガードから`syncKind`条件を外す(選択は同期データ不要)。tickの`sync.length`ガードにより同期無しでは自動ハイライトが無く、選択のみ表示される。
- 同じ文の再クリック: トグルにはしない(原文は「ハイライトする」のみ。仕様外のため選択維持。解除は再生/位置操作)。※解釈。Fable確認事項。
- 位置操作で選択解除する点は原文に明記が無い隣接解釈(原文は「停止中・一時停止中:クリックした文の英日ハイライトを維持」のみ)。シーク後も選択を残すと、位置と表示が乖離して誤解を招くため解除を推奨。Fable確認事項(判断候補ではなくB=承認範囲内の実装整理)。

## 3. 実装の入れ物(asset版管理)
- 新asset `rev01-h` = `rev01-g`(03B完了後、そのASSET_SHA256確定版)を基に、`derive_assets_01.py`へEDIT(許可リスト方式、旧文字列ちょうど1回)を追加して派生。変更箇所: `app.js`の(1)状態変数`selectedSid`(2)クリックハンドラ(:331-333 → `selectSentence(sid)`: `if(A.paused){selectedSid=sid;highlight(sid);}else{highlight(sid);}`、`seekSentence`削除)(3)`tick`の分岐(4)解除点(`playing`イベント・`#seek`/`#back10`/`#fwd10`/`playFull`/`playKp`/`playVocab`/`setLevel`で`selectedSid=null`)。`style.css`は原則変更なし(`.sent`の`cursor:pointer`は選択操作として維持)。`index.html`変更なし。DEV rev01-eは不変。
- 03B完了前にrev01-hを作らない(rev01-g確定と`ASSET_BUILD_ID`競合を避ける)。委任_02の着手条件=03B完了・rev01-gが origin/main に反映済み。
- `er135_enduser_rules_01.py ASSET_BUILD_ID`→"rev01-h"、`ASSET_TRANSLATION_KINDS`に"rev01-h"行追加(rev01-gと同じ種別)。版固定test(`er135_enduser_align_test_01.py:423` 等)を更新。
- 全6経路: X/Y/Zのrunnerはpages段で`ASSET_DIR`(=ASSET_BUILD_ID)から出力 → **ASSET_BUILD_ID更新のみでX/Y/Z×Std/Advの新規生成・retry/resume/regeneration後のpages再実行に自動適用**。既公開9dirは`publish-copy`(または再produce)で反映(音声・dev index.html不変、API 0)。Family別の重複実装なし。

## 4. FROZEN_ASSET_DIRS(`family_z_in_a_grove_01`=rev01-e)の扱い(論点)
- 現状は凍結=旧assetで検証(er135_enduser_page_01.py:45,1352-1358)。この記事は2026-10-30にユーザーが作品として不採用(お蔵入り・リリースしない、OPEN-592、UDR #226)。原文§1「全Family・全レベルの正式Production」は**正式Production(公開・公開予定)の記事**を指すと読むのが自然で、不採用記事は対象外。
- 推奨(Fable確認): 凍結dirは変更せず残置(rev01-eのまま、クリック=再生のまま)。理由=非公開・リリースしない作品に新UIを当てる価値なし、凍結は過去証跡の保全。対案=凍結解除し再produce(API 0、しかし不採用作品への作業)。いずれも技術的には容易。Fableが「不採用記事=対象外」を受入条件に明記すれば足りる。最終判断はFable(ユーザー判断不要の見込み: 原文の目的=正式Production全経路。ただし『お蔵入り記事は対象外』の明示は受入記録へ)。

## 5. 既存verifyの修正要点(`er135_enduser_page_verify_01.py`)
- F:273-277 `sentence_click_plays_from_sentence` → `sentence_click_does_not_play_or_seek`: 停止中クリックで`paused`のまま・`currentTime`不変(±0.05s)・当該sidが`.sent.on`・`__EUP.sel==sid`。
- M7(:539-546): `first_sid`のクリックで再生が始まる前提を変更。手順を「`#pp`で再生→一時停止→再開」の順に再構成し、`onSent/onJhl`一致(`_consistent`)は維持。
- J3/J3b(:466-496)は維持(`aud.pause()`後クリック→450ms→`_consistent`)。ただし`wait_for_timeout`後も選択が維持されること(tickが消さないこと)を明示的に検証できる=従来より強い検査になる。
- 新規追加(下記§6の項目に対応)。
- 版固定test更新(`ASSET_BUILD_ID`比較、`R.ASSET_TRANSLATION_KINDS`)。

## 6. 検証計画(ユーザー原文§3の10項目)
| # | 原文項目 | 方式 | 備考 |
|---|---|---|---|
| 1 | 停止中クリック→英日点灯・再生なし | Playwright自動 | paused維持・currentTime不変・.sent.on/.jhl.on、null群の文は.jhl無点灯。Story/Comment/Preview/In One Line各partの先頭対応済み文 |
| 2 | 一時停止中クリック→位置不変・英日点灯 | Playwright自動 | 再生→pause→currentTime記録→クリック→不変(±0.05s) |
| 3 | 再生中クリック→シーク・中断なし | Playwright自動 | 再生中にクリック→`seeking`イベント0回(listener)・`paused`のまま・currentTimeが連続的に増加(巻き戻りなし) |
| 4 | 通常再生中の英日同期 | 既存F(`highlight_follows_playhead`)・J4/J6を維持 | 既存検査がそのまま |
| 5 | 再生/停止/一時停止/再開/シーク | 既存F/G/J5を維持 | 変更なし |
| 6 | 1対1でない/未確定で誤点灯しない | 自動: 既存J(null群・複数文1群のsid→`_consistent`)をクリック経路で再実行 | 1対多群(複数sid→1群)のクリックも検査 |
| 7 | PC/モバイル | 自動: 既存の2 viewport(PC 1280x900 / 390x844 `has_touch`)でtap(`page.tap`)を追加 | 手動: 実機iOS/Android実タップは推奨(任意)。長押しの文字選択と競合しないことを目視 |
| 8 | 正式Production経路 | 自動: 各経路の`build_info.asset_build=="rev01-h"`・app.js sha==ASSET_SHA256を6経路(+既公開9dir)で集計 | X/Y/Z×Std/Adv。Fable独立受入=Fable自身がlive URLでplaywright実行 |
| 9 | retry/fallback/regeneration/resume整合 | 自動: pages再実行(`--stages pages,page_verify`相当、API 0)後に`asset_build`/sha不変を確認。publish-copyの検査(copy先verify+Playwright) | 音声・dev index.html sha不変の確認を併記 |
| 10 | Regression/Validator/Integration | 自動: `er135_enduser_*_test_01.py`全件、`er135_enduser_page_verify_01.py`(全family dir)、live HTTP(音声200/206・console error 0) | PRODUCTION_WIRED判定は原文§3最終段の必須条件(runtime証拠・全経路・test・SSOT・Git・Fable独立受入)を満たしてから |
手動のみ: 実機モバイルの体感(任意)。他はPlaywright自動化可能(基盤既存)。

## 7. リスク・注意
- `tick`の分岐は`highlight`の既存`sid===activeSid`早期returnと相互作用: 選択後に再生開始→`selectedSid=null`→次tickで`findActive`へ復帰、`activeSid`が一致なら描画変更なし(問題なし)。`jaLight`も同様に`g===activeG`で早期return。
- 03B進行中のため`er135_*.py`・`enduser_page_assets/**`は本委任で未編集。rev01-gのクリック処理が03Bで変わっていないか、委任_02開始時にdiffで再確認する。
- 認識: クリックで再生が始まらなくなるため、利用者は再生開始を「ここから再生」ボタン/`#pp`で行う(ボタンは既存・不変)。
