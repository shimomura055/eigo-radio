# DESIGN_01 日本語キャプション Production配線(asset rev01-i)

承認済み仕様: ユーザー原文(`docs/pm/delegation_log/2026-10-31_ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01_USER.md`)= A案(既定ON+ON/OFF切替)、APPROVED_FOR_PRODUCTION。追加デザインTrial・仕様拡張なし。現状把握は`CURRENT_STATE_01.md`。

## 1. 方式
新asset `enduser_page_assets/rev01-i/{index.html,app.js,style.css,ASSET_SHA256.json}` を、`enduser_page_assets/build_rev01i_01.py`(委任_02でresearch側から移設) で rev01-h から機械的に派生(各置換は出現1回をassert。rev01-h本体は不変)。
- Trial(`build_caption_trial_01.py`)から**移植**: `capUpdate`(点灯中の日本語群`activeG`のtextContentを`#jcapT`へ。群なし/日本語なし/KP・Vocab個別再生中=空=誤表示しない)、`jaLight`末尾とrender末尾からの呼出、`.jcap`のCSS(位置=固定再生バー内`.row2`直下、14px/スマホ13.5px、min-height 3.1em、max-height 5.4em縦スクロール、`--bar-h` 176/168px)。外観・位置・文字サイズはTrialと同一。
- Trialから**移植しない**: 黄色Trial帯、noindex、現行版リンク、Trial専用の記事data参照(`SRC/BASE`、`data-src/lv/prod`)、`?lv=`のprodLink更新。
- **追加**(原文2-2のみ): ①ON/OFFボタン`#capToggle`を固定再生バーの`.skips`内(±10秒ボタンの左隣。±10秒の位置は不変)に配置。既存`.skips button`の見た目に合わせ、幅72px以上・高さ40px(既存36pxより大きい)、ON時は淡青の押下表示、`aria-pressed`。ラベル`字幕 ON/OFF`(`aria-label`=「日本語キャプション(字幕)の表示切替」)。ラベルを短くした理由=320px幅で既存の現在位置ラベル(`全体`等)が潰れないため(実測: `キャプション ON`では`全.`に省略された)。②初期ON: `<body class="capon">`をindex.htmlに静的記述(JS実行前から表示=切替時のちらつき無し)。`#jcap`もindex.htmlに静的に置く(JS挿入によるレイアウト変動なし)。③OFF=`body.capoff`で`.jcap`が`display:none`(DOMからは非表示=高さ0)、`--bar-h`がrev01-h既定値(112px)へ戻る=固定バーと本文末尾の余白(`body padding-bottom = --bar-h+24px`)が解放され余白残り0(rev01-hと同じ構造)。④切替は`classList`とボタン文言/URL更新のみ。`audio`・`currentTime`・`play/pause`・点灯state(`selectedSid`/`activeG`)には触れない。OFF中も`capUpdate`は動く(ONへ戻すと現在の訳を即表示)。
- 設定保持: 既存のUI状態管理は**URLクエリのみ**(レベル=`setLevel`が`history.replaceState`で`?lv=`、起動時`Q.get('lv')`。`localStorage`/`sessionStorage`使用0件=Grep実測)。同方式に揃え、`?caption=0|1`を`replaceState`で書き、起動時に`Q.get('caption')!=='0'`で復元(Trialの`?caption=`と互換)。再読込・レベル切替・同タブ内の再表示で保持。`localStorage`は不採用(既存が持たないものを新設しない=最もシンプル)。副作用: 別記事を開き直す/URLを`?caption`なしで開くと既定ON(レベル選択と同じ挙動)。

## 2. 影響範囲
| 区分 | file | 変更 |
|---|---|---|
| 新規 | `enduser_page_assets/rev01-i/*`(4) | rev01-h+CAP1-CAP5(manifest `edits`に記録) |
| 新規 | `docs/research/ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01/tools/{build_rev01i_01,observe_caption_prod_01,diff_gate_rev01i_01}.py`、`evidence_01/`、`CURRENT_STATE_01.md`、本書 | 派生script・観測・差分Gate・証跡 |
| 変更 | `er135_enduser_rules_01.py:12,22` | `ASSET_BUILD_ID="rev01-i"`、`ASSET_TRANSLATION_KINDS`に`rev01-i`追加(rev01-hと同一種別) |
| 変更(test) | `er135_enduser_align_test_01.py:423`、`er135_enduser_vocab_audio_test_01.py:153-154`、`er135_enduser_page_test_01.py` T11 | rev01-i固定へ。T11はderive(rev01-h)一致+`build_rev01i`出力とrev01-i一致を検査 |
| 不変 | `er135_enduser_page_01.py`(本体。`ASSET_DIR`は`ASSET_BUILD_ID`参照)、X/Y/Z runner(`er019_family_x_listening_page_01.py`/`er121_*`/`er026_*`のhook)、`er135_enduser_page_verify_01.py`、`rev01-h/e/f/g`(履歴として残置)、音声・本文・翻訳・sync・Prompt | rev切替だけで配線(下記3) |
英日ハイライト(rev01-f)・英文クリック=選択のみ(rev01-h)・再生ロジックは`app.js`の既存関数を一切書換えない(追加2行の`capUpdate()`呼出のみ。jaLight/render本体は無変更)。

## 3. retry/fallback/regeneration/resume整合・旧asset残存ゼロ
- 全経路(X `er019_family_x_listening_page_01.py:262`/Y `er121_family_y_runner_01.py:1388`/Z `er026_..._runner_01.py:2784`)が`eu.hook_run`->`write_enduser_page`->`ASSET_DIR`(=`ASSET_BUILD_ID`)を通る(CURRENT_STATE_01 3節)。`ASSET_BUILD_ID`の1行更新で新規製作・retry・regeneration・resume・Z再完成段(`provision_shell,gate,assemble,pages,page_verify`)後の`page_verify`段すべてがrev01-iを書く。runner側の個別配線・flag・条件分岐は無い(DEV/Trial専用経路ではない)。
- 旧assetを参照し続けるdirが残らない方法: `ASSET_BUILD_ID`更新後は`verify_consistency`(`er135_enduser_page_01.py:1415-1422`)がrev01-hのままの公開dirを不合格にする(`FROZEN_ASSET_DIRS`の`family_z_in_a_grove_01`のみ例外)。**委任_02の一括再同期手順**(前回ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01と同形): 公開9dirそれぞれで`er135_enduser_page_01.py produce --family .. --dev-dir <公開dir> --run-dir .. --cache-dir <既存enduser_sync_cache>`(API 0。翻訳/埋め込みはキャッシュ再利用)->`diff_gate_rev01i_01.py <dir>...`(許可=app.js/style.css/index.html/build_info.json/article.json、sync・音声・dev HTML不変、既存ja不変)->全9dirの`verify_consistency`+Playwright(`er135_enduser_page_verify_01.py`)+本件`observe_caption_prod_01.py`->公開URL実操作->Fable受入。最後に`grep -l 'rev01-h' user_test/*/enduser/index.html`が0件(凍結dirはrev01-e)であること、`build_info.json`の`asset_build`が全9dirでrev01-iであることを確認。
- 副作用なし確認: 公開dirのsync_*.json/音声/dev index.htmlは再produceでも不変(前回gateで実証済みの手順を踏襲)。

## 4. テスト計画
1. 既存: `er135_enduser_*_test_01.py`全件・`er136_nuance_abolition_test_01.py`(asset版固定を更新したうえで)、`er135_enduser_page_verify_01.py`(sentence_click F/M7・jhl・J・K等のPlaywright 270項目)を既公開3記事(X meta_waddle_world / Y surname_choice / Z melos_kphr_evidence_r3)のrev01-i生成物で実行。失敗はrev01-hでの結果との差分で判定。
2. 追加: `observe_caption_prod_01.py`(PC1280/スマホ390/狭幅320 x X・Y・Z x Std・Adv)= 初期ON、OFFで領域解放(`jcap`高さ0・`--bar-h`復帰・余白=rev01-h同一)、ONで現在の訳表示、再生中更新(`.jhl.on`一致、バー高さ一定=0〜2行でちらつき/レイアウト変動なし。委任_02のOpus R-1/R-2で訂正: 委任_01の記述「バー高さ不変」は観測[1行以下162.4/2行176.4px]と矛盾していた。原因=`*{box-sizing:border-box}`で`.jcap{min-height:3.1em}`がpadding/borderを含み1行分しか確保できていなかった。`min-height:calc(3.1em + 14px)`[スマホ+12px]で是正。最大占有[`--bar-h:176px`/スマホ168px]は不変。Trialとの差=0〜1行時にバーが+12〜14px高いのみ)、停止/一時停止中クリック選択、再生中クリックで位置不変、シーク/+-10秒/ここから再生、KP/Vocab個別音声、日本語なし文=空欄、長文、切替で再生位置・状態不変、`?caption=0`再読込・レベル切替で保持、ボタンサイズ/viewport内、console/HTTPエラー0。
3. 静的: `build_rev01i_01`の出現1回assert、manifest sha整合(`check_assets`)、FORBIDDEN_ASSET(`dummy`等)不検出(`er135_enduser_page_test_01`で実行)。
4. 全6経路の正式runner発火証拠・公開9URL実操作は委任_02(本委任は共通asset+ローカル検証まで)。

## 5. 範囲外(提案のみ)
キャプション位置/サイズ/配色の変更、領域縮小の工夫、新機能。Trial dir(`user_test/enduser_caption_trial_01/`)の撤去要否は委任_02でFable判断(Production非参照)。
