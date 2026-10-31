# RUNTIME_EVIDENCE_01(ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01 委任_02、2026-10-31)

証跡dir=`docs/research/ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01/evidence_02/`(以下 `ev/`)。API呼出0(下記2)。runner rc=0だけでなく、runner出力dirに対するobserve(M-3期待値)とverify CAP検査群(M-5)を併せて証拠とした。

## 1. 切替と公開
- 切替commit: `e25f16293`(`er135_enduser_rules_01.py:12` ASSET_BUILD_ID=rev01-i)と再produce commit `77babf1c5`(公開9dir)を**同一push**(`4df50f8bf`)で反映。origin/mainに「切替済み・dir未更新」の中間状態は存在しない。push時刻=2026-10-31 17:15:15 JST。
- 対象dirはpush直前のorigin/main merge後に `user_test/*/enduser/build_info.json` の `asset_build != rev01-i` を動的列挙: 凍結 `family_z_in_a_grove_01`(rev01-e、既存の公開管理方針)を除く**9dir**(X5/Y2/Z2)。再列挙で残0(`ev/diff_gate_out.jsonl`、merge後`verify-consistency` 9/9 ok)。
- 公開URLの`meta[name=build-id]`: push後 17:23:27 に9/9 rev01-i(Pages反映約8分。`ev/` ではなくscratch `bid_log.txt`、結果は本書6)。

## 2. API 0の証明(再produce・runner)
- 構造的担保: 全produce・runnerを `capw_run.py`/`runner_shim.py`(`ev/produce/`・`ev/runner/`)経由で実行。APIキーはダミー値・`.env`非読込・HTTPS_PROXYをdead proxy(127.0.0.1:9、localhostのみNO_PROXY)に設定=キャッシュミスがあれば呼出が失敗し課金0。全件rc=0=全キャッシュヒット。
- 結果の証拠: 各dirの`build_info.json`(cost.api_calls=0, translate_api_calls=0, embedding_api_calls=0, embedding_tokens=0, translate/embedding_cost_jpy=0.0, judge.calls=0)。`ev/diff_gate_out.jsonl`の`api0`欄(9dir)・`ev/runner/{x,y,z}_build_info.json`・`ev/produce/produce_*_result.json`(`api_calls`/`generated_translation.api_calls`/`ja_align.embedding.api_calls`)。embedding cached_hits=X/Y 213〜295(Zは翻訳無しで0)、judge cache_hits=0〜6。
- 結論: 再produce9回(+pilot x_meta 1回)・runner3回のAI API呼出=0、開発実費=0円(ローカルCPUのみ)。

## 3. M-2 diff gate(厳格化後)9/9 OK
`tools/diff_gate_rev01i_01.py`: 変更許可=`enduser/{app.js,style.css,index.html,build_info.json}`の4fileのみ(各dir changed=4)。`data/article.json`はbyte一致必須(改行差のみ許容)・`translation_changes`=0。app.js/style.cssはrev01-iと一致、index.htmlは旧index.html+patch_html(rev01-i)と一致。sync_*.json・音声・dev index.htmlは不変(`ev/diff_gate_out.jsonl`)。

## 4. 6経路(X/Y/Z × Std/Adv)の正式runner発火(`ev/runner/`)
正式runner(`er019_family_x_listening_page_01`/`er121_family_y_runner_01 --stages pages,page_verify`/`er026_family_z_fiction_production_runner_01 --stages pages,page_verify`)を既存run dir・**rev01-h時代のpages dir**に対して起動(起動間隔≥150秒、`ev/runner/launch_epochs.txt`・`status_runner.txt`、stop_scope_check rc=0=`ev/stop_checks/`)。各runnerは1起動でStd/Adv両方のenduser(hook_run: `er019:262`/`er121:1388`/`er026:2784`)を生成。

| 経路 | runner rc | hook_run browser verify(PC+mobile) | CAP検査群(M-5) | 出力dirのasset_build | observe(runner出力dir x PC/スマホ/320 x Std/Adv) |
|---|---|---|---|---|---|
| X ai_chat_sponsored_persuasion | 0 (16:47:37-16:52:55) | TOTAL 298 NG 0 | 28項目 OK 0 NG | rev01-h -> rev01-i | 6組 PASS |
| Y surname_choice run_02 | 0 (16:52:55-16:58:28) | TOTAL 296 NG 0 | 28項目 OK 0 NG | rev01-h -> rev01-i | 6組 PASS |
| Z yuki_onna run_yo_prod_01 | 0 (16:58:28-17:05:37) | TOTAL 292 NG 0 | 28項目 OK 0 NG | rev01-h -> rev01-i | 6組 PASS |

observe集計=`ev/observe_runner_summary.md`(18組 PASS 18、error 0、build-id rev01-i 18)。runnerのretry/fallback/regeneration分岐は別(本書7)。
副作用の記録: runnerは主worktreeの既存run dirに`enduser_page_result*.json`・`e2e_stage_log.jsonl`・`run_launch_log.jsonl`・`page_verify_local.json`等を書く(正式runnerの通常動作。`ev/runner/snap_before.json`/`snap_after.json`: 新規0・削除0・変更100[内62=音声mp3の再copyでmtimeのみ、size変化14=ログ/結果json・Y pages/enduserのasset])。

## 5. R-5 resume(rev01-h時代のrun dirの再実行)
- runnerのstage選択は明示CLIのみで、状態に基づくstage skip無し(`er121_family_y_runner_01.py:_select_stages`〜1655、`er026`同形、Xは`er019:255-266 build_enduser_after_page`が常にindex書出し後に実行)。enduserの生成は Y=`stage_page_verify`内(`er121:1404-1422`)・Z=`stage_page_verify`内(`er026:2790-2835`)・X=builder末尾。したがって `page_verify`を含む再実行は必ず現行assetで書き直す。
- 実証: 上記3 runner起動前の`verify-consistency`は rev01-h pages dir 3件すべて rc=3(`ENDUSER_ASSET_MISMATCH: asset_build=rev01-h が現行asset(rev01-i)と不一致`、`ev/r5_before_resume_verify_consistency.txt`)。runner再実行後は全て rev01-i・consistency ok。`page_verify`を含めずpagesだけ再実行した場合にenduserがrev01-hのまま残る経路は、`publish-copy`が rc=3で停止し公開dirは変更されない(`ev/r5_publish_copy_rev01h_pagesdir_rejected.txt`)=旧版が公開へ漏れない。

## 6. 公開URL実操作(M-4)
- push 17:15:15 -> 公開9/9のbuild-id=rev01-i確認 17:23:27(10分以内に反映、再試行不要)。
- chromium: 9dir x Std/Adv x PC(1280)/スマホ(390)/狭幅(320) = **54組 PASS 54**(`ev/observe_public_summary.md`、console/HTTP error 0、build-id rev01-i 54/54)。観測した文3,003、キャプション有り2,517、**空欄が期待値の文486**(`ja_align`由来の期待値と全文一致)、再生中サンプル4,320(キャプション=点灯日本語の不一致0)。
- 公開URLでのブラウザ検証全項目(`er135_enduser_page_01.py verify-only --base-url`、CAP検査群を含む): 9dir中8dirが TOTAL 278-298 NG 0。X meta_waddle_worldのみ初回 NG 1(`G adv_continues_across_part_boundary`)。→原因は本書8、単独再実行で TOTAL 298 NG 0(`ev/` は scratch `pubverify/`、要約=本書8)。
- WebKit(iOS近似): 本書9。
- 空き領域・再生位置: OFFでバー高113px・本文余白は23px(rev01-hと同一、54/54)。ON時バー高=PC 176.4px・スマホ172.8px(0〜2行で一定。R-1)。3行以上の訳は最大5.4emまで拡張しスクロール(Trialと同じ上限。観測した文のうち 307/3,003 が3行以上でバーが伸びる=これは承認済みTrialの挙動)。
- R-8(320px・再生中のnowLabel): 初期の`全体`は省略されないが、再生中・KP再生中・Vocab再生中の`全体 · Key Phrase 1`/`全体 · Full Story Part 1`/`全体 · Preview`は幅66-67pxに収まらず省略表示(52状態)。390px以上は省略0。表示位置・操作・再生には影響しない(装飾的な省略)。`ev/observe_public_summary.md`の末尾に全状態。

## 7. retry/fallback/regeneration/resume整合
`ASSET_BUILD_ID`1行でX/Y/Z全経路(hook_run→ASSET_DIR)が rev01-i を書く(個別flag・分岐なし)。retry/regeneration/Z完成段の`page_verify`段は`_build_enduser_page`/`hook_run`が常に最新dev HTML+現行assetから作り直す。旧asset残存は`verify_consistency`(`er135_enduser_page_01.py:1453-1457/:1511-1515`)が不合格にし、publish-copy・Z完成段の公開前に止まる。本書5で resume 3経路・publish停止を実証。

## 8. 間欠NG(Opus指摘: NG0まで再実行を根拠にしない)
| 検査 | 原因(確定度) | 扱い |
|---|---|---|
| `V *_vocab_each_item_plays_own_audio_and_returns` | **検査側の競合(確定・再現)**: 製品の`endVocab()`は`mode='full'`+`pause()`を同期で行い、位置復帰`currentTime=at`は通し音声の`loadedmetadata`後(`app.js:233-236 withMeta`)。検査は`mode==='full'&&paused`だけを待って即`currentTime`を読むため復帰前の`t=0`を読む。`ev/repro_vocab_flake.py`: 通し音声応答の遅延0秒/1.5秒のどちらでも「現行の待ち条件の直後 t=0, readyState=0」→「metadata読込後 t=20.2/21.3(復帰済み)」。製品は正しく復帰する。 | 検査を「通し音声のmetadata読込完了(readyState>=1 かつ src が vocab_ でない)を待ってから位置判定」に是正(`er135_enduser_page_verify_01.py` V節)。是正後、再produce9回(初回)・runner3回・公開verify9回で vocab NG 0(1回で達成。反復して消したのではなく原因を確定して修正)。pilot x_meta(是正前)は1回NG(`ev/produce/x_meta_pilot_attempt1_tail.txt`)。 |
| `I *_glossary_links_open_the_expression` | **検査側の競合(推定。未再現)**: 旧判定は「scrollYが150ms間隔で2回同値=停止」だけで、smooth scrollの開始が遅れると開始前に判定終了し到達前の位置(top=874.7>0.8vh)を読む(rev01-hでも発生した事例のtop値)。`ev/repro_glossary_flake.py`でCPU 1x/6x/25x制限でも旧判定・新判定とも0 NG=再現できず。 | 判定を「目的の項目が開き、画面内に到達し、かつ停止」まで待つ(最大6秒、到達しなければNG)に是正。製品の最終到達位置は全試行で正(top=12px)。是正後の全実行(再produce9・runner3・公開verify9)で glossary NG 0。再発したら製品側として別OPEN(未再発)。 |
| `G adv_continues_across_part_boundary`(公開X meta、初回のみ) | **環境負荷(確定度:中)**: 公開URLの音声をライブ配信から取得する3並列のブラウザ検証+observeの同時実行中で再生がバッファ待ちになり、12秒待機内に境界+0.9秒へ進まない(gt=80.83、境界80.34)。単独再実行で TOTAL 298 NG 0。Production hook(ローカル配信)では全9回+3回で発生0。 | 検査の待機仕様は変更せず(ネットワーク待ちを隠さないため)、公開URL検証は負荷を分けて単独再実行で確認。全実行回は`ev/`と本書に記録。 |
| webkit observe 初回 melos adv | **observe側の起動競合(確定)**: `A.play()`の未処理拒否`AbortError`(WebKit)でキャプション更新サンプルが0。製品の`playNow`は`AbortError`を握りつぶす(`app.js:236`)。 | observeの`play()`を`.catch`+再生しなければ1回再試行に是正。1回目retryはPASS。 |
その他: `Page.evaluate: Target crashed`(chromiumの1回=メモリ圧、単独再実行で NG 0、記録のみ)。

## 9. WebKit(R-7)
`--browser webkit`(Playwright WebKit 26.6、モバイル390。iOS Safari実機ではない)、公開URL(X meta_waddle_world・Y surname_choice・Z melos_kphr_evidence_r3 x Std/Adv=6組)。**最終run 6/6 PASS**(`ev/observe_public_webkit_summary.md`、error 0、build-id rev01-i)。実行回の全記録: 初回run(`ev/observe_public_webkit_run1_initial`)は5/6 PASS・melos adv NG 1(原因=本書8のobserve起動競合)、是正前の単独retry(`ev/observe_public_webkit_retry1`)PASS、是正後の全6組run(`ev/observe_public_webkit_run2_final`)6/6 PASS(その間に起動後に結果ファイルを残さず終了したrunが1回あり=記録のみ)。

## 10. 新規検査の自己検証(陰性対照)
- キャプションを常に空にしたapp.js: CAP `click_stopped_caption_equals_ja_align_expected` が PC/モバイル x Std/Adv で NG 4。
- 旧CSS(`min-height:3.1em`、R-1以前): CAP `bar_height_constant_0_to_2_lines` が NG 4(初版の判定式は2行を比較対象から外して見逃したため、判定を「訳が2行以内の行」に是正して検出を確認)。いずれも`ev/negative_controls/`に保存。
