# DESIGN_01 — 選定UI 2階層化(SELECTION-UI-TWO-TIER-01、API 0、費用0)
原文=`docs/pm/delegation_log/2026-10-31_SELECTION-UI-TWO-TIER-01_USER.md` §2/§3/§4。親=OPEN-620(II)。変更は表示UI・遷移のみ(選定ロジック=form_logic.jsの純ロジック、候補データ、Production制作経路は無変更)。

## 方式: 共通テンプレート(index.html 1枚)+URLパラメータ
| 画面 | URL | 内容 |
|---|---|---|
| トップ | `index.html?batch=<id>` | 対象記事N/セットM・Done n/M・進捗バー・記事行(Standard/Advancedの**リンク**+Done/未完了/要再確認)・次の未完了へ・一括コピー(全Done時のみ。未完了時は拒否+未完了一覧)。**個別フォームは出さない**(`#setForm` hidden) |
| 個別 | `index.html?batch=<id>&set=<slug>__<level>` (例 `set=moon_shrinking__a2`) | 最上部「Topへ戻る」→タイトル・レベル→候補フレーズ→フレーズコメント→候補単語→単語コメント→文法(既存)→追加指示(全体)→Done→(このセットのリセット)→最下部「Topへ戻る」。固定フッタ・一括コピーは出さない(ページ毎コピーにしない) |
| 開発用 | `?dev=all` / `?dev=all&set=` | 従来どおり(赤帯、キー`eigo-kp-form-v3:dev`)。Topへ戻る=`?dev=all` |
| 旧 | `?batch=<id>&a=<key>` | `a`を`set`と同義で受理(旧リンクの互換) |

## 維持するもの
localStorageキー`eigo-kp-form-v3:b:<id>`・セット単位の読み直し保存・Done署名/自動解除・batch分離・コピー書式(BATCH1/SET/件数=N/sha10)・①ちょうど3件・残りすべて選択・`?dev=all`・gate画面(batch無し/不正/未解決)。トップと個別は別ページ遷移だが状態はlocalStorageなので、遷移・戻る・再読み込みで保持される。bfcache復帰は`pageshow`で再描画。

## 無効URL
存在しないset/別batchのset → gate画面「指定されたセットは、この報告の対象にありません」+同batchの「Topへ戻る」リンク。不正batch/batch無しは従来のgate。

## 付随修正(スマホ操作性)
候補の`.flag`(nowrap)が390px幅で横overflow(レイアウトviewport 468px化→上下ボタンのタップが不安定)していたため`white-space:normal`へ。表示のみ。

## 版
ASSET_VERSION `sel-v3-rev04-a`→`sel-v3-rev05-a`(publish/smoke/URL発行ツールは版一致を要求)。
