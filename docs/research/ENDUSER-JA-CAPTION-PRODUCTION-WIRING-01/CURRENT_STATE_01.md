# CURRENT_STATE_01 日本語キャプション Production配線(ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01 委任_01)

基準commit: origin/main 3a0bf398f。ユーザー原文: `docs/pm/delegation_log/2026-10-31_ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01_USER.md`。Trial成果: `docs/research/ENDUSER-JA-CAPTION-TRIAL-01/`(OPEN-628)。

## 1. asset revが決まる流れ(rev01-h -> 公開dir)
| 段 | 場所(file:line) | 内容 |
|---|---|---|
| rev決定(単一点) | `er135_enduser_rules_01.py:12` `ASSET_BUILD_ID = "rev01-h"` | 現行assetのbuild id。これだけが「現行rev」 |
| asset dir | `er135_enduser_page_01.py:42` `ASSET_DIR = ROOT/"enduser_page_assets"/R.ASSET_BUILD_ID` | `check_assets`(:1288)がmanifest(`ASSET_SHA256.json`)のsha256・禁止語(`er135_enduser_rules_01.py:34` FORBIDDEN_ASSET)を検査 |
| 書出し | `er135_enduser_page_01.py:1308` `write_enduser_page` | `ASSET_FILES=(index.html,app.js,style.css)`(:43)を`<dir>/enduser/`へLFで原子的にswap。`build_info.asset_build`は:1013、`assets/files`のshaは:1341-1342で記録 |
| 訳の描画種別 | `er135_enduser_rules_01.py:22` `ASSET_TRANSLATION_KINDS[ASSET_BUILD_ID]`、`er135_enduser_page_01.py:820` | 現行assetが描画できるpart種別のみ生成対象 |
| 検査 | `er135_enduser_page_01.py:1415-1422` `verify_consistency` | `public_dir`のasset shaを**現行ASSET_DIR**と照合。`FROZEN_ASSET_DIRS`(:45)の凍結dirだけ旧assetで照合。=ASSET_BUILD_ID更新後、旧assetのままの公開dirは`verify_consistency`が不合格になる(旧assetが「気づかれず残る」ことはない) |
| asset生成 | `enduser_page_assets/derive_assets_01.py`(DEV rev01-e->rev01-h)。rev01-iは`docs/research/ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01/tools/build_rev01i_01.py`(rev01-hからの機械的派生) | rev01-e/f/g/hは残置(履歴) |

## 2. 公開済みEnd Userページ(`enduser/index.html` build-id実測、origin/main時点)
rev01-h配線済み = **9dir**(ユーザー原文の「対象9記事」と一致。数の差分なし):
| Family | dir | build-id |
|---|---|---|
| X | user_test/family_x_ai_chat_sponsored_persuasion_01 | rev01-h |
| X | user_test/family_x_jwst_mystery_emission_line_01 | rev01-h |
| X | user_test/family_x_meta_waddle_world_01 | rev01-h |
| X | user_test/family_x_moon_shrinking_reselect_01 | rev01-h |
| X | user_test/family_x_untidiness_family_resource_01 | rev01-h |
| Y | user_test/family_y_production_redelivery_fee_03 | rev01-h |
| Y | user_test/family_y_production_surname_choice_01 | rev01-h |
| Z | user_test/family_z_melos_kphr_evidence_r3 | rev01-h |
| Z | user_test/family_z_yuki_onna_01 | rev01-h |

対象外(凍結・不採用): `user_test/family_z_in_a_grove_01`(rev01-e。`er135_enduser_page_01.py:45` FROZEN_ASSET_DIRS。藪の中=不採用・保存のみ)。公開管理方針どおり更新しない。
Trial用の別dir `user_test/enduser_caption_trial_01/`(noindex、cap-trial-01)は公開記事ではないTrial資産。委任_02で扱いをFableが決める(Productionからの参照なし)。
他のuser_test配下(138dir中、上記10以外)は`enduser/`を持たない(Family A/B/C等。対象外)。

## 3. enduser同期が再実行される経路(retry/fallback/regeneration/resume)
全経路が`eu.hook_run`(`er135_enduser_page_01.py:1822`)=`produce_enduser`->`verify_consistency`->Playwright検証 を通り、assetは**常に現行ASSET_DIR**から書かれる。したがって`ASSET_BUILD_ID`更新だけで以下すべてに自動適用される(個別配線不要)。
| Family | 呼出点(file:line) | 再実行される状況 |
|---|---|---|
| X | `er019_family_x_listening_page_01.py:255-270` `build_enduser_after_page`(`eu.hook_run` :262)、main :287 | 新規記事の正式入口。dev index.html出力後に毎回呼ぶ。同CLIの再実行=resume/再生成(失敗時rc=5でdev HTML・既存enduser/不変) |
| Y | `er121_family_y_runner_01.py:1381-1391` `_build_enduser_page`、`stage_page_verify` :1404、呼出 :1422 | `--stages ...page_verify`の再実行(retry/resume/再生成後のpages->page_verify)ごとに再生成。公開dirへは`er135_enduser_page_01.py:1852` `publish_copy`(旧enduserは公開dir外backupへ退避しrollback可) |
| Z | `er026_family_z_fiction_production_runner_01.py:2778-2785` `_build_enduser_page`、`stage_page_verify` :2790、呼出 :2835 | 同上(Zはpages_dir=公開dirへ直書き)。再実行時は`provision_shell,gate,assemble,pages,page_verify`を1起動(OPEN-480) |
retry/fallback/Local Rewrite/segment再生成でdev HTMLが変わっても、`page_verify`段の`_build_enduser_page`が最新dev HTML+現行assetからenduserを作り直す。キャッシュ(sha256)により翻訳/埋め込みAPIは再実行されない(API 0。`er135_enduser_page_01.py:1368`付近の`align_cache_dir`/`translate_cache_dir`)。
既公開dirの一括更新は前回(ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01 委任_02)と同手順: `er135_enduser_page_01.py produce --dev-dir <公開dir> ...`(API 0)+差分Gate+公開(`docs/research/ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01/evidence_02/ech_produce.py` / `tools/ech02_diff_gate_01.py`)。今回の差分Gateは`docs/research/ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01/tools/diff_gate_rev01i_01.py`(style.css追加を許可、asset=rev01-i照合)。

## 4. 設定保持(既存UI状態管理)の実測
`enduser_page_assets/rev01-h/app.js`: レベルは`setLevel`で`history.replaceState`により`?lv=`をURLに書く(:333)、起動時は`Q.get('lv')`で復元(:342)。`localStorage`/`sessionStorage`は**使用なし**(Grep 0件)。=既存はURLクエリ方式のみ。キャプションも同方式(`?caption=0|1`)に揃える(DESIGN_01)。

## 5. 既存test資産(version固定の所在)
`er135_enduser_align_test_01.py:423`、`er135_enduser_vocab_audio_test_01.py:153-154`、`er135_enduser_page_test_01.py` T11_Assets(derive結果とasset一致)が`ASSET_BUILD_ID`をrev固定で検査。`tools/ech02_diff_gate_01.py`はrev01-h固定(前回タスク専用・今回は新gate)。
