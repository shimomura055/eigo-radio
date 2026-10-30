# ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 現状調査(委任_01、2026-10-30、API 0・コード変更0)

原文=docs/pm/delegation_log/2026-10-30_ENDUSER-EN-JA-LINKED-HIGHLIGHT-01_USER.md。以下はfile:line付きの実測。

## 1. End Userページの構造(再生・ハイライト)
- asset=`enduser_page_assets/rev01-e/{app.js,index.html,style.css}`(ASSET_SHA256.json固定)。`derive_assets_01.py`がDEV(`user_test/dev_enduser_page_01/`)にEDITS許可リストだけを適用して機械派生(`derive_assets_01.py:30-`)。`ASSET_BUILD_ID="rev01-e"`は`er135_enduser_rules_01.py:12`、`ASSET_DIR`は`er135_enduser_page_01.py:38`。
- 英語文=`<span class="sent" data-sid>`(`app.js:23-31` sentHtml)。`sentEls[sid]`(`app.js:112-113`)。
- 既存の更新点は**`highlight(sid)`1関数**(`app.js:223-236`): `.sent.on`の付替え+自動スクロール。呼出元は`tick()`(`app.js:251` `highlight(findActive(gt()))`)のみで、クリック再生(`seekSentence`→`playFull`→`tick`)、自動進行(rAF `loop`)、シーク(`#seek`/±10秒/`seeked`イベント→`tick`)、レベル切替(`loadSync`→`highlight(null)`)がすべてここへ集約される。よって**連動の追加点は`highlight()`の1箇所**で足りる。
- 日本語訳=`trHtml(p)`(`app.js:33-37`)が`p.ja`(段落文字列の配列)を`<div class="tr"><p>…</p></div>`として本文直後(glossの後)に出す。**文単位の構造はない**(段落の素のテキスト)。CSS=`style.css:44-45`(`.tr`)。ハイライト色=`style.css:35-36`(`.sent.on{background:var(--on);box-shadow:0 0 0 3px var(--on)}`)。
- 検査=`er135_enduser_page_verify_01.py`(Playwright PC1280+モバイル390x844。項目A〜K,Z。F=ハイライト追従・文クリック・シーク、G=連続再生、C=訳ブロック=approved data)。

## 2. EN↔JA対応情報の現状(結論: 文単位の対応情報は**どこにも存在しない**)
- adapter(`er135_enduser_page_01.py:625-669` attach_translations): 訳は**段落単位**。X=承認済み日本語原稿(`ja_writer/revision2.md`等)の段落をstory行の英語段落数と1:1で割付(段落数不一致はSTOP)。Y=devページ`<details>日本語の元原稿`の1ブロック(Voice単位1段落)。付与対象は`kind==story`のみ(`:644`、story以外にJAがあればSTOP)。
- 英語文のIDは`sid`(例`std_14-s007`)で、syncの時間範囲(`sync_<lv>.json`)と1:1。JA側に文ID・文境界は無い。`HL_SENTENCE_*`(`er_learning_highlight_01.py:279`、Y Std V1紹介のsplit3の件=PLAN_04B_01.md:70)は**英語文内の学習項目ハイライトの文番号**の仕組みでEN↔JA対応とは無関係(再利用不可)。
- 生成側(X: ja_writer→英語Std/Adv、Y: 日本語原稿→英語)は文対応を出力しない(Std/Advで英語の文分割が異なり、日本語は共通)。生成時に対応を得るにはWriter Prompt変更が要り、既存記事には効かない=不採用。

## 3. 訳が存在する範囲(translation_coverage、build_info実測)
| Family | 訳の有無 | 備考 |
|---|---|---|
| X | story(Part 1-3)のみ有り。Comment 1-4・Topic・Preview・In One Lineは**無し**(`none_approved_translation_hidden`) | 日本語原稿に対応段落が無い |
| Y | story(Lead/Voice紹介/Voice/Closing)のみ有り。Comment・Topic・Previewは無し | |
| Z | **全て無し**(story含む)。5既公開dir中メロス/藪の中とも`translated=0` | EN原作のZ(Open Window等)にはJA本文自体が無い。JA原作(メロス/藪の中/雪女)も日本語は表示していない |

## 4. 文数一致の実測(`tools/ejh01_count_rate_01.py`、JA文=。！？区切り、「」内除外)
| 記事/レベル | 段落ペア数 | EN文数=JA文数の段落 | EN文計 | JA文計 |
|---|---|---|---|---|
| X月 Std | 9 | 1 | 46 | 35 |
| X月 Adv | 9 | 9 | 35 | 35 |
| Y再配達 Std | 8 | 2 | 51 | 34 |
| Y再配達 Adv | 8 | 5 | 37 | 34 |
| Y姓 Std | 8 | 1 | 54 | 40 |
| Y姓 Adv | 8 | 6 | 42 | 40 |
→ 文数一致の順序対応だけでは**Std約15%・Adv約75%**しか成立しない。Std(英語が平易に文分割)は1対多(2文対1文が大半)が常態=意味対応づけが必須。ZはJA無し。

## 5. 対応づけの事前実測(API 0のプロトタイプ。`tools/ejh01_len_aligner_probe_01.py`)
- 単調DP(長さ比のlog差+1対多ペナルティ、1:1/1:2/2:1/2:2/1:3/3:1)で6組215グループを整列: 1:1=170、2:1=37、3:1=5、2:2=3、未対応0。X月Std Part 1(目視正解 s007|s008|s009+s010|s011|s012+s013)・Y再配達Std Voice 2は目視で全グループ正しい。
- **ただし誤対応を実測**: Y姓Std Voice 2末尾(`Someone said that was an old-fashioned way to think.`+`I think they were right.` ↔ `古い考えだと指摘されて、その通りだと思った。`、続く`I need to let my son go…`↔`私が子離れしないと…`)で、長さのみのDPは1文ずれた(`I think they were right.`↔`私が子離れしないといけないんだね。`)。**長さだけでは「誤った日本語をハイライトしない」を満たせない**=意味的検証が必要。
- 数字アンカー不一致は215グループ中0(数字は有効な安全装置だが数字を含む文が少ない)。

## 6. asset版管理・既存記事
- enduser/を持つ公開dirは5(X月reselect_01、Y再配達_03、Y姓_01、Zメロスr3、Z藪の中_01[作品不採用=保存のみ])。各dirに`app.js/index.html/style.css/build_info.json/data/`のコピー(asset_build=rev01-e)。`verify_consistency`は**現行ASSET_DIR**とのsha一致を要求(`er135_enduser_page_01.py:1221-1226`)。
- 前例: commit 7e5059293でrev01-eのapp.jsを(IRR表拡充で)更新し5dirのenduser/をAPI 0で再生成済み=「凍結」(Opus M2)は新build id + 一括再produceで運用可能。`produce --dev-dir <公開dir> --cache-dir <run>/enduser_sync_cache`は公開dir上のdev HTMLから再生成、ASRはキャッシュ(mp3 sha256同一なら0回。build_info.cost.api_calls=0実測)。
- hookは共通: X=`er019_family_x_listening_page_01.py:262`、Y=`er121_family_y_runner_01.py:1388`、Z=`er026_family_z_fiction_production_runner_01.py:2777`が**すべて`eu.hook_run`**を呼ぶ。→ adapter(`build_enduser`)側の追加で全Familyに自動適用、hook側変更は不要(JA原稿の引渡しはX=`find_x_ja_manuscript`、Y=`_ja_path`で既存)。
- 制作中: X 4記事・雪女は音声未了で進行中(別Worker)。X新記事はpages段でhookが走ると自動適用される(コード統合後)。

## 7. 他Workerとの競合
本委任は読取のみ。実装時の編集対象は`er135_enduser_*`・`enduser_page_assets/`・`derive_assets_01.py`のみで、NCA(er128)・KP Trial・Family X記事Workerの編集対象とは重ならない(hook側ファイル不変)。
