# GOVERNANCE_PROPOSAL_04 — 選定UI「公開URLでの実操作」を受入条件にするための運用規則(文案のみ)

位置づけ: **文案のみ**。`docs/pm/PM_GOVERNANCE.md`本体・委任テンプレ・Closeout Checkは**Fable承認後に反映**(本委任では未編集)。ユーザー判断事項ではない(受入側不備の是正=PM_GOVERNANCE 11-8、Fable所管。DESIGN_03 §6)。

## 背景(再発した根本原因)
OPEN-620(II)選定UIは「コード実装+fixture/ローカルtestのPASS」でACCEPTEDにされたが、(a)公開側に `batch` が供給されず(`articles.json.batch` 無し)、(b)状態が単一グローバルで、(c)機能が batch 有無に依存して**ユーザーが開く公開URLでは操作できなかった**(GAP_ANALYSIS_03)。設計準拠・test PASSは目的適合の根拠にならない(sandwich-pm.md手順4-2)。

## 追加規則案(最小)
1. **選定URLは共通関数経由のみ(M14)**: HR依頼書・報告でユーザーへ出す選定フォームURLは `tools/selection_batch_url_01.py: issue_batch_url(batch_id, smoke_json)` の戻り値だけを使う。関数は「live smoke結果JSONが ①kind=batch ②id一致 ③status=PASS ④UI版(ASSET_VERSION)がローカルHEADと一致 ⑤base_url一致 ⑥test報告でない」ときだけURLを返す(満たさなければ例外=URLを出せない)。**`?a=`単体URL(旧形式)・手組みURLの提示を禁止**。`gen_hr*.py` 等のタスク別ツールは本関数を呼ぶ。
2. **公開は2段階(M7)**: `tools/publish_selection_batch_01.py stage1`(batchファイル+index登録・latest不変)→push→`?batch=<id>` のlive smoke PASS→`promote`(latest更新)→パラメータ無しURLの解決をlive smoke。smoke未PASSのidはlatestに載せず、ユーザーにも出さない。
3. **完了/受入条件(選定UI・選定URLを含む成果物)**: コード・fixture・ローカルtestのみでACCEPTEDにしない。**公開URL上のlive smoke PASS(最新batch)+PC/mobile実操作スクショ+(一括コピーを使う場合)クリップボード内容の `er128 confirm-batch --dry-run` 受入**を証拠とする。`index.html`/`form_logic.js` を変更した委任の完了条件に「最新batchへのlive smoke PASS」を含める。
4. **公開済みbatch idの不変性(M10)**: 同idでmembers/データsha256が変わる再publishは拒否。更新は新id。UIは記録shaと不一致なら「データが更新されました」を表示。
5. **Fable独立受入**: 公開URLを自分で開く(PC+mobile)。委任側の実測スクショと乖離があれば不合格。

## 委任テンプレ追記案(「HR/選定UIを含む委任」節)
- 成果物欄に `選定URL(?batch=<id>)` と `live smoke結果JSON path`・`ASSET_VERSION` を必須記載。
- 禁止: `?a=` 単体URLの提示、smoke未PASS/テスト報告(test:true)のURL提示。
- RESULT_PACKET(3)に「公開URLで何を実操作して確認したか(PC/mobile)」を1行。

## Closeout Check追記案
- [ ] 選定UI/URLを含むタスク: 提示URLは `issue_batch_url` の戻り値か(手組み・`?a=`でないか)
- [ ] live smoke JSON(kind=batch, status=PASS, asset_version=HEAD)が保存されているか
- [ ] 公開URL実操作スクショ(PC/mobile)・クリップボード→er128 dry受入が証跡にあるか

## 影響範囲・費用
文案のみ。追加費用0・量産単価影響0。既存`gen_hr*.py`の呼出差替えは各担当dir(他worker編集中のものは対象外)ごとに別途(一覧は EVIDENCE_04.md「旧`?a=`リンク一覧」節)。
