# JA-GLOSS-QUALITY-ALARM-TRIAL-01 HR警告表示 DEV試作の設計 (HR_UI_MOCK_DESIGN_01)

管理ID=JA-GLOSS-QUALITY-ALARM-TRIAL-01 / OPEN-636 / 委任_01(設計のみ。実装は委任_02)。DEV/Trial専用。**ProductionのHR画面(`user_test/selection_form_v3/`)は無変更**。
ユーザー原文§5(想定表示・UI原則)。現行HR画面の構造は CURRENT_STATE_01.md §2。

## 1. 想定表示(ユーザー原文§5の再現)

候補行(現行)の「日本語訳」行の**直下**に、警告対象の項目だけ次のブロックを足す:

```
Key Phrase：verdict            (現行の表現ラベル。変更しない)
 [正式訳] 結論                  (現行の日本語訳行。変更しない)
 🔴 訳語の確認を推奨             (赤字・太字。1行見出し)
 本文では裁判の比喩が使われているため、「◯◯」の方が文脈に適している可能性があります。   (reason_ja、60字以内)
 改善候補：◯◯                  (suggestionが空でないときだけ)
```
(◯◯はモデルが出した文言。表示例の『評決』はユーザー原文の例であり、Luna出力がそうなる保証はない。実出力を表示する。)

## 2. 複製方式(現行の見た目・操作を変えない)

| 項目 | 設計 |
|---|---|
| 置き場所 | 新規dir `user_test/selection_form_v3_qalarm_dev/`(`index.html`・`form_logic.js`・`data/`)。公開URL(DEV)=`https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3_qalarm_dev/index.html?a=<slug>__<level>` |
| `form_logic.js` | **バイト同一のコピー**(sha256をProductionと一致させて記録)。署名・照合コード・コピー文・Done判定・ロック規則は一切変更しない |
| `index.html` | Productionからのコピー+**差分は2点のみ**: (a) `.qa-alarm` のCSS数行、(b) 候補行描画 `groupHtml` 内で、`it.quality_alarm && it.quality_alarm.warn` のときだけ警告ブロックのHTMLを日本語訳行の直後に追加する1関数。警告なしの項目は**現行とバイト同一のDOM** |
| データ | `data/<slug>__<level>__prod.json` のコピー+各候補に任意フィールド `quality_alarm: {warn, reason_ja, suggestion, severity, rule}` を付加(Trialの保存済み出力から決定論的に付与。**表示時のAPI呼出0**) |
| 差分検証 | (1)`form_logic.js` sha256一致 (2)警告なしの全項目で、DEVとProductionの候補行HTMLが同一(node/jsdomで比較) (3)同じ選択操作でコピー文・照合コード・Done署名が**DEVとProductionで一致** (4)`git diff`で `user_test/selection_form_v3/` が無変更 |
| 隔離 | 記事枠の一覧 `data/articles.json` はDEV dirの別ファイル(Production一覧に追記しない)。Production `articles.json`・End Userページ・runnerから参照しない |

## 3. UI原則との対応表(ユーザー原文§5)

| UI原則 | 設計での担保 |
|---|---|
| 警告は問題が疑われる項目だけ | 閾値規則(DESIGN_OPTIONS_01 §3)を通ったwarn=trueのみ描画。それ以外はDOMを追加しない |
| 警告理由は短く具体的 | reason_ja<=60字(schemaとプロンプトで指定。コード側でも60字超は切詰めず「警告を出さない」ではなく**そのまま表示**し、超過件数を記録して評価) |
| 改善候補は有用な場合のみ | suggestionが非空のときだけ「改善候補：」行を描画 |
| 通常の承認操作を妨げない | 警告はチェックボックス・Done・コピーの有効/無効に影響しない(disabledにしない、確認ダイアログなし、警告の既読操作なし)。警告を理由にした送信ブロックはしない |
| 修正しない場合は元の訳を維持 | 警告は表示のみ。データ・コピー文・確定内容に入れない(`itemRecord`/`buildText`は無変更)。修正はこれまでどおり自由コメントで指示 |
| 正常な項目に不要な表示を追加しない | 警告なしの項目はDOM同一。サマリ行・件数バッジは既定で出さない(任意で `?qa=count` のとき上部に「訳語の確認を推奨：N件」を出す。既定OFF) |

## 4. 表示仕様(案)
- 色: 見出しは既存 `.kpwarn` の赤(#ad4938)系、太字。背景は薄い赤(#fdf0ee)の枠(既存 `.flag` の黄色バッジとは別。警告の優先度を区別)。
- 文言: 見出し固定「🔴 訳語の確認を推奨」。reasonは「…可能性があります」型(断定しない。モデル出力のままだが、プロンプトで断定を避けるよう指示)。
- モバイル: `.flag` と同様に折返し可(`white-space:normal; overflow-wrap:anywhere`)。
- アクセシビリティ: `role="note"`、絵文字は装飾(`aria-hidden`)、見出し文字で意味が伝わる。
- 比較表示: `?qa=off` でProductionと同じ表示(A/B確認用)。

## 5. 試作で確認すること(委任_02の完了条件)
1. 想定表示どおりに描画される(PCとモバイル幅のスクリーンショット、既存 `browser_check_0x.mjs` 型のブラウザ確認)。
2. 警告のある記事枠(untidiness b1b の verdict、moon b1b の culprit/radius 等、実データ)と警告のない枠の両方で、操作(選択・Done・コピー・リセット)が現行と同一に動く。
3. 上記§2の差分検証4点がPASS。
4. 実Trial出力から付与した警告の件数(1 levelあたり)を測り、確認負担(警告件数/12候補)を報告。
5. DEV URLを報告(ユーザー原文§8-5)。

## 6. Production分離・将来の配線(本Trialでは実施しない)
- 本試作の `quality_alarm` はDEV dirのみ。Production `export_form_data_01.py`・候補docへは追加しない。
- 正式採用(ユーザー承認)後に初めて、export側で `quality_alarm`(表示専用・署名外)を追加し、フォームの描画差分を取り込む設計。確定内容の保護(`PROTECTED_ITEM_FIELDS`、er128_kp_confirmed_content_01.py:91)に触れない。
- 既存の「難易度表示」(表示専用の参考情報)と同型。先例: CURRENT_STATE_01.md §2-3。
