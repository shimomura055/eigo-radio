# EVIDENCE_01 — 選定UI 2階層化の実装・公開・公開URL実操作検証(SELECTION-UI-TWO-TIER-01、API 0、費用0)

設計=DESIGN_01.md。原文=`docs/pm/delegation_log/2026-10-31_SELECTION-UI-TWO-TIER-01_USER.md` §5(12項目)。**Status=実装・公開・公開URL実操作PASS(PRODUCTION_WIREDはFable判定)**。UI版`sel-v3-rev05-a`。選定ロジック(form_logic.js純関数)・候補データ・Production制作経路は無変更。

## 1. 公開URL(検証用test batch。ユーザー向け報告URLではない。index.json latest=null のまま)
ベース: `https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/`
- トップ(18セット=9記事): `index.html?batch=twotier-a-18sets-test`
- 個別 Standard例: `index.html?batch=twotier-a-18sets-test&set=moon_shrinking__a2` / Advanced例: `index.html?batch=twotier-a-18sets-test&set=moon_shrinking__b1b`
- 別batch(5セット、同一セットを含む): `index.html?batch=twotier-b-5sets-test`

## 2. 原文§5の12項目との対応(全項目 公開URL上・PC 1280x900 + mobile 390x844 touch、各33チェックPASS)
| 原文§5 | 検証項目(下表) | 結果 |
|---|---|---|
| 1 トップは一覧のみ | 1, 1b | PASS(PC/mobile) |
| 2 Std/Advクリックで個別ページ | 2, 2b, 2d | PASS |
| 3 上のTopへ戻る | 3 | PASS |
| 4 下のTopへ戻る | 4, 4a | PASS |
| 5 選択・コメントの保持 | 5, 13 | PASS |
| 6 個別Done→トップ更新 | 6 | PASS |
| 7 変更でDone解除 | 7 | PASS |
| 8 18セットDone→1回の一括コピー | 8a-8e(17/18拒否+未完了一覧、遷移、コピー) | PASS |
| 9 Claude受領18/18 | TT-A er128 confirm-batch --dry-run n=18 | PASS |
| 10 別batch非混在 | 10a-10c | PASS |
| 11 PC/スマホ操作 | 11a(ボタン高さ52px・幅>=120)+全項目を両viewで実操作 | PASS |
| 12 Regression | node selection_form_logic_test_01.js ALL PASS 86(うち新規05 two-tier contract) / sub04_tools_test 9 OK / er128_form_readable_restore_test PASS | PASS |

## 3. 結果表(実測。`live_result_pc.json` / `live_result_mobile.json`、ログ`live_*.log`)
| 項目 | PC 観測 | PC | mobile 観測 | mobile |
|---|---|---|---|---|
| 1 トップ: 一覧のみ(記事9・セット18)、個別フォーム非表示 | form_hidden=True visible_form_controls=0 progress=対象記事 9件 セット 18 Done 0 / 18 報告: twotier-a | PASS | form_hidden=True visible_form_controls=0 progress=対象記事 9件 セット 18 Done 0 / 18 報告: twotier-a | PASS |
| 1b チップ文言Standard/Advanced | ['Advanced', 'Standard'] | PASS | ['Advanced', 'Standard'] | PASS |
| 2 Standardクリックで個別ページ(moon_shrinking__a2) | url=_form_v3/index.html?batch=twotier-a-18sets-test&set=moon_shrinking__a2 cur=選択中：月は少しずつ縮 | PASS | url=_form_v3/index.html?batch=twotier-a-18sets-test&set=moon_shrinking__a2 cur=選択中：月は少しずつ縮 | PASS |
| 2b Advancedクリックで個別ページ(moon_shrinking__b1b) | 選択中：月は少しずつ縮んでいる？｜Advanced（2 / 18） | PASS | 選択中：月は少しずつ縮んでいる？｜Advanced（2 / 18） | PASS |
| 2c 個別ページの順序: 上Top→タイトル/レベル→フレーズ→フレーズコメント→単語→単語コメント→全体→Done→下Top | [['topBack1', 97], ['curbar', 163], ['candPhrase', 488], ['boxPhrase', 1159], ['candWord', | PASS | [['topBack1', 79], ['curbar', 145], ['candPhrase', 605], ['boxPhrase', 1344], ['candWord', | PASS |
| 11a Topへ戻るボタンが押しやすいサイズ(高さ>=44, 幅>=120) | [[858, 52], [858, 52]] | PASS | [[344, 52], [344, 52]] | PASS |
| 4a 最下部で下のTopへ戻るボタンが画面内 |  | PASS |  | PASS |
| 3 上のTopへ戻る→同batchのトップ | est/selection_form_v3/index.html?batch=twotier-a-18sets-test | PASS | est/selection_form_v3/index.html?batch=twotier-a-18sets-test | PASS |
| 4 下のTopへ戻る→同batchのトップ | est/selection_form_v3/index.html?batch=twotier-a-18sets-test | PASS | est/selection_form_v3/index.html?batch=twotier-a-18sets-test | PASS |
| 5 選択(フレーズ/単語)とコメント3種がページ移動後も保持 | sel=3 | PASS | sel=3 | PASS |
| 12a 既存: 残りをすべて選択ボタンが個別ページに存在(①3件で有効) |  | PASS |  | PASS |
| 6 個別でDone→トップの進捗とチップが更新(Done 1/18) | prog=(1, 18) cls=chip st-done / このセットは Done です。 | PASS | prog=(1, 18) cls=chip st-done / このセットは Done です。 | PASS |
| 7 Done後に選択変更→Done解除(個別表示・トップ0/18・チップ未完了) | 内容変更のため未完了に戻りました。内容を確認して、もう一度Doneを押してくださ / (0, 18) / chip st-stale | PASS | 内容変更のため未完了に戻りました。内容を確認して、もう一度Doneを押してくださ / (0, 18) / chip st-stale | PASS |
| 13 ブラウザ戻る→トップ(進捗維持)/進む→個別(入力維持)/個別再読み込み(選択・コメント・Done維持) | back=True fwd=True reload=True | PASS | back=True fwd=True reload=True | PASS |
| 2d URL直接オープンで指定セットのフォーム表示 | 選択中：月は少しずつ縮んでいる？｜Advanced（2 / 18） | PASS | 選択中：月は少しずつ縮んでいる？｜Advanced（2 / 18） | PASS |
| 14 無効URL安全案内: 存在しないセット | 指定されたセットは、この報告の対象にありません URLのセット指定（no_such__a2）が正しくないか、別の報告のセットです。 Topへ戻る（twotier | PASS | 指定されたセットは、この報告の対象にありません URLのセット指定（no_such__a2）が正しくないか、別の報告のセットです。 Topへ戻る（twotier | PASS |
| 14 無効URL安全案内: 別batchに無いセット | 指定されたセットは、この報告の対象にありません URLのセット指定（ai_chat_sponsored_persuasion__a2）が正しくないか、別の報告の | PASS | 指定されたセットは、この報告の対象にありません URLのセット指定（ai_chat_sponsored_persuasion__a2）が正しくないか、別の報告の | PASS |
| 14 無効URL安全案内: 不正batch | 報告IDの形式が正しくありません 報告IDは英小文字・数字・_・- のみ（3〜64文字）です。 現在開ける報告はありません。 | PASS | 報告IDの形式が正しくありません 報告IDは英小文字・数字・_・- のみ（3〜64文字）です。 現在開ける報告はありません。 | PASS |
| 14 無効URL安全案内: batch無し | 対象の報告が指定されていません 選定は「報告ごとのリンク（?batch=報告ID）」から開きます。過去の記事を含む全記事は表示しません。 現在開ける報告はありま | PASS | 対象の報告が指定されていません 選定は「報告ごとのリンク（?batch=報告ID）」から開きます。過去の記事を含む全記事は表示しません。 現在開ける報告はありま | PASS |
| 8a 17/18時点の進捗 | (17, 18) | PASS | (17, 18) | PASS |
| 8b 未完了時は一括コピー拒否+未完了一覧(1件) | 閉じる 未完了のセットが1件あるため、コピーしていません。 雪女(Yuki-Onna)｜Advanced ① Key Phraseはちょうど3件必要です(現在0件)。 | PASS | 閉じる 未完了のセットが1件あるため、コピーしていません。 雪女(Yuki-Onna)｜Advanced ① Key Phraseはちょうど3件必要です(現在0件)。 | PASS |
| 8c 未完了一覧→該当個別ページへ遷移 | v3/index.html?batch=twotier-a-18sets-test&set=yuki_onna__b1b | PASS | v3/index.html?batch=twotier-a-18sets-test&set=yuki_onna__b1b | PASS |
| 8d 18/18 Done | (18, 18) | PASS | (18, 18) | PASS |
| 8e 個別ページには一括コピー/固定フッタを出さない(ページ毎コピー方式にしない) | visible=0 | PASS | visible=0 | PASS |
| TT-A 18セット: 一括コピー=SET 18件・連番・stem一意 | sets=18 | PASS | sets=18 | PASS |
| TT-A 18セット: ヘッダ バッチ=twotier-a-18sets-test と END 合計18件 |  | PASS |  | PASS |
| TT-A 18セット: フレーズ/単語コメントが各セット1回ずつ(欠落0・重複0) | p=[1, 1, 1] w=[1, 1, 1] | PASS | p=[1, 1, 1] w=[1, 1, 1] | PASS |
| TT-A 18セット: コピー成功の表示(フッタ直上) | 閉じる 18件（全SET＋コメント）をコピーしました。Claudeへそのまま貼り付けてください。 | PASS | 閉じる 18件（全SET＋コメント）をコピーしました。Claudeへそのまま貼り付けてください。 | PASS |
| TT-A 18セット: er128 confirm-batch --dry-run で受入(全18件) | rc=0 n=18 batch=twotier-a-18sets-test  | PASS | rc=0 n=18 batch=twotier-a-18sets-test  | PASS |
| 10a 別batch(B)はA入力と非混在: Done 0/5・セット5 | (0, 5) | PASS | (0, 5) | PASS |
| 10b 同一セット(moon_shrinking__a2)でもBのフォームは空で、localStorageキーがbatch別 | keys=['eigo-kp-form-v3:b:twotier-a-18sets-test'] | PASS | keys=['eigo-kp-form-v3:b:twotier-a-18sets-test'] | PASS |
| 10c Bで入力後もAの同セットは元のコメントのまま | P-moon_shrinking__a2 | PASS | P-moon_shrinking__a2 | PASS |
| 15 JSエラー0 | [] | PASS | [] | PASS |

観測欄の一部が文字化けして見えるのはPlaywright出力のcp932表示のため(JSON自体はUTF-8、判定ロジックは文字列比較で実施)。

## 4. live smoke(publish前ゲート。`tools/selection_form_live_smoke_01.py`を2階層UIへ更新)
`smoke_twotier-a-18sets-test.json` / `smoke_twotier-b-5sets-test.json` = PASS(トップに個別フォーム無し・チップ数==members・固定フッタ・UI版一致・個別ページにコメント欄/上下Top/フッタ非表示・pageerror 0)。

## 5. スクリーンショット(`shots/`)
T1_top(トップ)/T2_set_top・T2_set_full(個別・最上部の「Topへ戻る」)/T3_set_bottom(最下部の「Topへ戻る」)/T4_top_done1/T5_invalid/T6_copy_refused/T7_top_18done/T8_batchB_set/TT-A_18セット_copy_ok。各`_pc`/`_mobile`。

## 6. 副次修正・影響
- スマホ(390px)で候補の`.flag`(nowrap)が横overflowし、レイアウトviewportが468pxに拡大して上下ボタンのタップが不安定だった(rev04から存在)。`white-space:normal`へ(表示のみ)。
- `tools/selection_form_live_smoke_01.py`を2階層UIへ更新(旧smokeはトップにコメント欄を要求し新UIでFAILするため)。旧検証script`sub02a_verify.py`/`sub04_verify.py`は旧1ページUI用の履歴証跡で、新UIでは再実行不可(`sub04_verify.Ctx/copy_checks/er128_dry`は本検証が再利用)。
- 旧リンク`?batch=<id>&a=<key>`は`set`同義で個別ページとして開く(互換)。
- 無変更確認: form_logic.js(版文字列以外)・data/*.json・Production Prompt/制作経路・Vocabulary音声・Family A/B/C: 差分0(`git diff 92a4e79c3..HEAD --stat`参照)。
- 既知の旧テスト失敗(form1_selection_form_v3_test_01.py 5件)はsparse worktreeにfixtureが無いための環境要因で、本変更前(stash)と同一件数・同一内容(baseline比較済み)。
