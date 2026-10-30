# EVIDENCE_04 — 選定UI是正の実装・公開・公開URL実操作検証(委任_04、API 0、費用0)

設計=DESIGN_03.md(+Opus条件付き可 M1〜M14をFable全採用)・GAP_ANALYSIS_03.md。原文=`docs/pm/delegation_log/2026-10-30_SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01_USER_02_REOPEN.md` §3①〜④・§4 A/B/C・§5・§6 と当初原文`..._USER.md`(:51-139)。
**Status(OPEN-620 II選定UI) = 実装・公開・公開URL実操作PASS、Fable独立受入待ち**(ACCEPTEDではない)。承認済みの選定基準・選定数(①ちょうど3件)・候補生成仕様・Production Prompt・Vocabulary音声・記事Production経路は無変更(差分0、末尾「差分検査」)。

## 1. 公開URL(いずれも検証用 test batch。ユーザーへ提示する報告URLではない)
ベース: `https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/`
- シナリオA(18セット=9記事x Standard/Advanced): `index.html?batch=sub04-a-18sets-test`
- シナリオB(5セット=3記事): `index.html?batch=sub04-b-5sets-test`
- 別batch分離/シナリオC(3セット): `index.html?batch=sub04-c-overlap-test`
- `data/batches/index.json` の `latest` は**検証後に null へ戻し済み**(live確認: `"latest": null`)。= パラメータ無しURLは「対象の報告が指定されていません」(下記smoke kind=none PASS)。**実報告のbatchはFableが publish tool で作成**する(§6)。test batchは`test:true`で一覧に出ない。
- 画面上の `UI版 sel-v3-rev04-a`(= `window.__ASSET_VERSION` = form_logic.js `ASSET_VERSION`)。

## 2. 当初要求R1〜R5と完成機能の対応(GAP_ANALYSIS_03.md R1〜R5)
| 要求 | 完成機能(ファイル:行は実装時点) | 公開URL実操作の証拠 |
|---|---|---|
| R1 対象=今回の報告の記事・レベルのみ(§3①、過去記事を混在させない・報告単位管理) | `data/batches/<id>.json`(1報告=1ファイル)+`?batch=<id>`。batch不明/未解決=**記事を出さない**(全35枠フォールバック廃止、`gate()` index.html init)。members=**stem完全一致のみ**・1件でも未解決→エラー画面(部分表示禁止=M1)。状態キー`eigo-kp-form-v3:b:<id>`(報告ごと分離、旧キーは読まず残置)。`?dev=all`のみ開発用全枠(赤帯・キー`eigo-kp-form-v3:dev`)。resolveBatch/resolveRoute/storeKey=form_logic.js | A: chips=18・記事9のみ(猿の手/ダミー/slot混入なし)、B: chips=5・記事3、C/M1: member欠落→`#gate`・chip0、別batch(A)を開いても同stemがC入力と混ざらない、localStorageキーが`eigo-kp-form-v3:b:<id>`のみ |
| R2 一覧・進捗・Done・移動(§3②) | 進捗(対象記事N/セットM/Done n/M/バー)・記事行チップ(未完了/Done/要再確認)・「次の未完了へ」・**モバイル固定フッタ(Done n/M・次の未完了へ・一括コピー)**・選択数ミニカウンタ(sticky)・`scroll-padding`でDone/フッタ重なり回避。既存のDone署名/①ちょうど3件/残り全選択ロジックは無変更 | A: Done 0/18→18/18、17/18時点コピー拒否+未完了1件列挙、C: 「次の未完了へ」で未完了へ移動、未完了一覧ボタンで該当セットへ移動 |
| R3 Done管理(条件充足時のみ・変更で自動解除・切替/リロードで保持) | 既存doneSig/doneStatus維持。ゲート(`BS`限定)撤廃で常時表示 | C: Done後の選定変更→chip `st-stale`・進捗2/3・再コピー拒否→再選定→再Doneで3/3、コメント編集→要再確認→再Done、リロードでDone 3/3・コメント保持 |
| R4 一括コピー(§3④ 最重要) | 全Done時のみ1クリックで全セット+コメントを1データ(既存BATCH1形式・無変更)。コピー前に**欠落・重複・順序検査**(`batchCopyStems`: SET連番・stem==members)。拒否時の未完了一覧は**フッタ直上**に表示(M12)。成功は緑バナー。クリップボード失敗時は手動コピー用textarea | A: 18 SET・連番・stem一意・フレーズ/単語コメント36個が各1回・全体コメント4個・END合計18件・`er128 confirm-batch --dry-run` rc=0 n=18。B: 5 SET。C: 編集後コメントのみ(旧0・新1)。コピー全文=`sub04_copy_A_pc.txt`(18SET/388行)・`sub04_copy_B_*.txt` ほか |
| R5 フレーズ欄直下/単語欄直下の独立コメント欄(§3③) | `boxPhrase`/`boxWord`(フレーズ候補直下/単語候補直下)+全体コメント。batch限定を撤廃(`?dev=all`でも同じ描画経路)。コピー内は各SETの「自由コメント」に`【フレーズ】/【単語】/【追加指示(全体)】`(AIF1 m8互換のまま) | A: 配置順 候補→フレーズコメント→単語候補→単語コメント→全体→Done(getBoundingClientRect)、各セットで独立入力・切替保持(セット1へ戻って P-/W-/G- 値が残る)、コピーに全て1回ずつ |

## 3. 検証結果(公開URL上、PC 1280x900 + mobile 390x844 touch)
| 検証 | 結果 | 証跡 |
|---|---|---|
| 公開URL実操作E2E 全シナリオ(A/B/C x PC/mobile) | **103/103 PASS**(fail 0) | `sub04_verify_live_result.json`、スクショ`sub04_shots/`(A_open/A_comment_boxes/A_reject_17of18/A_all_done/A_copy_ok、B_open/B_copy_ok、C_reject_unfinished/C_stale_reject/C_footer_bottom/C_M1_error/C_M2_stale/C_M5_legacy、各_pc/_mobile) |
| 追加live再実行(A,B、コピー全文保存) | 46/46 PASS | `sub04_copy_{A,B}_{pc,mobile}.txt` |
| ローカル(同スクリプト、公開前) | 103/103 PASS | (本ファイルのみ記録) |
| live smoke batch x3 | 全PASS(Pages反映待ち291秒を自動poll) | `sub04_smoke_sub04-{a-18sets,b-5sets,c-overlap}-test.json`、`sub04_shots/smoke_batch_*` |
| live smoke latest(M7 stage2: promote→パラメータ無しURLの解決) | PASS(URLが`?batch=<id>`へ固定) | `sub04_smoke_latest_sub04-a.json`、`sub04_shots/smoke_latest_*`。検証のため test batch Aを**一時的に**latestへ→直後に`--clear-latest`で原状復帰(commit 84f23352→01f82358) |
| live smoke none(latest未設定の公開状態) | PASS(記事0・「対象の報告が指定されていません」) | `sub04_smoke_none.json` |
| M1 member欠落→エラー画面 | PASS(PC/mobile) | `C_M1_error_*` |
| M2 パラメータ無し→latest解決・URL固定・リロード同報告/最新でないidで「最新の報告ではありません」帯 | PASS | `C_M2_stale_*`(index.jsonをroute差替えで再現) |
| M5 旧`?a=`のみ→記事を出さず「旧形式のリンク」/`?batch+?a`でaが対象外→明示 | PASS | `C_M5_legacy_*` |
| M6 不正id(`../`)拒否・存在しないid→「見つかりません」 | PASS | E2E C |
| M10 公開時sha記録とUIの不一致→帯(live: 不一致なし=帯非表示確認)・同id別内容の再publish拒否 | PASS | sub04_tools_test.py `test_03`、live `shaBanner` hidden |
| M12 モバイル: 未完了一覧がフッタ直上で画面内/本文末尾がフッタに隠れない/入力フォーカス中はフッタ非表示(キーボード重なり回避) | PASS(`pointer:coarse`のみ。実機ソフトキーボードは未実測=制約) | `C_reject_unfinished_mobile.png`、`C_footer_bottom_mobile.png` |
| M13 UI版一致(live ASSET_VERSION == ローカルHEAD) | smoke全件で検査・PASS | smoke JSON `asset_version` |
| M14 URL発行共通関数 `issue_batch_url`(smoke PASS+id一致+UI版一致+base_url一致+非test のときだけ`?batch=`URLを返す。`?a=`は発行不可) | 4+5件 test PASS | `sub04_tools_test.py` 9件OK |
| node test(form_logic.js) | **ALL PASS 85**(既存73+新規12: id正規表現/resolveBatch stem完全一致・部分表示禁止/prototype key/storeKey名前空間/resolveRoute/listBatches/shaMismatches/batchCopyStems/ASSET_VERSION/index.html契約) | `selection_form_logic_test_01.js` |
| er128 test | 83件(既存76+新規7 TestRestoreBatchFile)。**errors=3は変更前と同一**(cmudict未導入の環境エラー: TestEndToEndRealConfirm 3件、sparse検証環境) | 同上 |
| form1_selection_form_v3_test_01 | 変更前後で失敗集合同一(F2+E3。sparse検証環境で未追跡入力が無い分。主環境の既知FAIL4件=OPEN-613とは環境差で件数が異なる)。※`fetch(`個数の静的検査2箇所を2→4へ更新(同一オリジン静的data 4種=articles.json/<article>.json/batches/index.json/batches/<id>.json、外部URLなしを併せて検査) | 同上 |
| publish tool否定系 | 不正id/重複/空/緩い一致/欠落/未commit data/同id別内容/smoke未PASS・id不一致・UI版不一致・kind違い・test報告のlatest化を全て拒否、拒否時はbatchファイルを書かない | `sub04_tools_test.py` |

## 4. er128受入結果(Claude側で正しく受領できること)
A(18セット)・B(5セット)・C(3セット)のクリップボード全文を `er128_form_readable_restore_01.py confirm-batch --from-readable-batch <text> --articles-json <data/articles.json> --dry-run` に入力 → いずれも rc=0・n=SET数・`dry_run=true`(本確定せず)。**batch解決は新経路**(articles.jsonにbatchキー無し→貼付ヘッダ`バッチ=<id>`→`data/batches/<id>.json`のmembers完全一致検査)。既存`--articles-json`のbatchキー経路は無変更(TestRestoreBatch全PASS)。

## 5. 旧`?a=`単体リンク(再発行はFable)
公開フォームは`?a=`のみのリンクでは記事を出さず「旧形式のリンクです」+(あれば)最新報告へのリンクを表示する(M5)。リポジトリ内(origin/main)で旧形式のURLを記載している文書:
| 文書 | 更新日 | 旧URL |
|---|---|---|
| docs/research/FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01/HR_REQUEST_01.md / HR_REQUEST_02.md | 10-29 / 10-30 | ②散らかり/④AI説得広告/⑨Meta Waddle World/⑭JWST の `?a=<slug>__a2|b1b` 各2(計8セット) |
| docs/research/FAMILY-Z-YUKI-ONNA-PRODUCTION-01/HR_REQUEST_01.md / HR_REQUEST_02.md | 10-30 | `index.html?a=yuki_onna__a2` / `__b1b` |
| docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/RESUME_06.md | 10-28 | `index.html?a=in_a_grove__a2` |
| docs/research/AI-ISLAND-FORM-PRODUCTION-01/FORM_RESELECT_01.md | 10-27 | `?a=ai_island_temple__a2` |
| docs/research/KP-DIFFICULTY-4LEVEL-DISPLAY-01/EVIDENCE_05.md | 10-30 | `?a=the_tell_tale_heart__a2|b1b`(他に`?a=kpd05_…`) |
| OPEN_ITEMS.md(記述内) | - | 上記の参照 |
どれが「公開中・未回答のHR依頼」かはSSOT/ユーザー応答状況に依存し本委任では特定していない(Fableが確認)。**再発行**: 該当セットを含む実報告batchを `tools/publish_selection_batch_01.py` で作成→`issue_batch_url` でURL化(`gen_hr*.py`等の呼出差替えは他worker担当dirのため本委任では未実施。担当dir内で`?a=`を組む箇所は上記文書の生成元(HR依頼書生成コード)が該当し、一覧のみ)。

## 6. Fableへの運用手順(実報告のbatch公開)
1. `py tools/publish_selection_batch_01.py stage1 --id <id> --date YYYY-MM-DD --report-ref <ref> --members <data stem,...> --push`(members=`data/*.json`のファイル名stem。例 `moon_shrinking__b1b__prod`。test:trueを付けない)
2. `py tools/selection_form_live_smoke_01.py --kind batch --id <id> --members <N> --out <smoke.json>`(Pages反映まで自動poll。FAILなら原因診断がJSONに入る)
3. PASS後 `py tools/publish_selection_batch_01.py promote --id <id> --smoke-json <smoke.json> --push` → `selection_form_live_smoke_01.py --kind latest ...`
4. ユーザー提示URLは `py -c "from selection_batch_url_01 import issue_batch_url; print(issue_batch_url('<id>','<smoke.json>'))"`(`?batch=<id>`)。文案=GOVERNANCE_PROPOSAL_04.md。

## 7. 差分検査(Vocabulary音声・Production経路に影響なし)
本委任の変更ファイル(commit 8324c7d4b/84f23352/01f82358d + 本evidence commit): `user_test/selection_form_v3/{index.html,form_logic.js,data/batches/*}`、`er128_form_readable_restore_01.py`(追加のみ=削除は`restore_batch`シグネチャ1行へ`batches_dir=None`追加)、`export_form_data_01.py`(`--set-batch`にDEPRECATED警告2行)、tests、`tools/{publish_selection_batch_01,selection_batch_url_01,selection_form_live_smoke_01}.py`、docs。`er137*`/`er019*`/`er121*`/`er063*`/`er026*`/`er120*`/Prompt/routing/pricing/vocab への差分 grep = 0(`git show --name-only`で確認)。API呼出0・費用0。

## 8. 制約・未実測
- 実機(iOS/Android)ソフトキーボードは未実測(Chromiumのtouch emulation+`pointer:coarse`分岐のみ)。フッタ非表示ロジックで重なり回避を設計。
- Pages反映遅延は最大約5分(A初回291秒)。publish toolは`--wait-sec`で自動poll、タイムアウト時は原因診断(JS版不一致/データ欠落)付きでFAIL。
- 記事名(articles.jsonの`name`)に「Production候補・7+5 evidence」等の旧ラベルが付く枠(再配達手数料/メロス等)はUI一覧にそのまま出る(articles.json側の表示名の問題。本委任では不変。要望があれば別途名称整備)。
