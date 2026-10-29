# SSOT_DIFF_01 (FZ-DIALOGUE-LR-ADOPTION-01 委任_02 成果。SSOT本体は未編集。委任_03で一括反映する提案差分)

根拠: ユーザー正式決定 2026-10-29 (Zセリフ LR採用=APPROVED_FOR_PRODUCTION)。実装=委任_02(本commit)。配線状態は委任_03のE1/E3 runtime evidence後に PRODUCTION_WIRED とする(現状=実装済み・offline test PASS・実音声evidence待ち)。

## 1. CURRENT_SPEC.md
- :3161 (基本フロー) 変更なし(LRあり部位=Zセリフを含むようになる)。
- :3171 (Z_DLG_CTX 行) 置換:
  `| Z_DLG_CTX(2、Zセリフ) | ctx Style(文脈・感情付き)2回 | ②NG後・③前に180秒 | 従来Dialogue Style(style_prefix_override=None) | **あり(2026-10-29 APPROVED_FOR_PRODUCTION。最大1回・深さ1・入力=現サイクル同一shaのASR内容不一致NG転写[新しい順・確定内容と重なる転写は除外]・候補は確定内容と重なるものを除外)** | 6/2回 | LR後③'NG→Lock→TERMINAL_NG→HR/STOP(rc=2) |`
- :3172 (Z_DLG_LEGACY 行): 独立行を削除し、`Z_DLG_LEGACY=旧Z_DLG_CTX(LRなし・3/3/1)の履歴(2026-10-26〜10-29)。ROW_MAPPING_01.md参照`の注記へ。
- :3179 置換: `JA短文Style・LRなし / Zセリフ: JAはLRなし(③NGでLock+日本語HRQ)。Zセリフは文脈・感情Style2回→180秒→従来Dialogue 1回→LR(最大1回)→①'②'ctx→180秒→③'従来Dialogue→HR(最大TTS6・LR1・待機2)。Zセリフモデルはgemini-2.5-pro-preview-tts不変。`
- :1652 (履歴注記): 末尾の【履歴】注記に `Z dialogueのLRは2026-10-29に正式採用(UDR-TRA-1・OPEN-528 Deferred(1)はsupersede)。「Z dialogueにLocal Rewriteは未配線」「3回NG→HR直行」は履歴` を追記。
- :1659 周辺 (D-1既知事項): 変更なし。

## 2. DECISION_LOG.md (追記案)
`2026-10-29 FZ-DIALOGUE-LR-ADOPTION-01: ZセリフにLR(最大1回)を正式採用。最大TTS6・LR1・待機2(180秒x2)。UDR-TRA-1(Z dialogue LRなし)・OPEN-528 Deferred(1)をsupersede。実装=er122 state v2(phase B1/LR/B2)+er063 外側guard+er127 Profile(Z_DLG_CTX 3,(3,),LEGACY_DIALOGUE,True,6,6,2)+er129 確定内容事前保護(candidate_filter)。既定OFFのflag無し(Profile定義が唯一のスイッチ)。`

## 3. OPEN_ITEMS.md
- OPEN-602: Status「実装完了(委任_02)・実音声evidence待ち(委任_03 E1/E3)」へ。分類=修正へ進む。
- OPEN-528 Deferred(1): `supersede(2026-10-29 ユーザー正式採用)`。
- 新規(候補): 技術STOPがB1最終で起きた場合、再実行しても同じ技術STOPで止まる(X/Yと同形・approve_regenerate後に再開)。分類=実害なし(Secondary復旧後のresume)。
- 新規(候補): Adv後処理(減速後再検証)の技術STOPはB1内でLR・HRに入らずIN_PROGRESSに残る。分類=実害なし。

## 4. PM_GOVERNANCE.md §30 (HR到達経路の報告ルール)
- :3763 付近「適用例(初回)=…LR対象外=Z dialogueは未配線[CURRENT_SPEC:3178]、正常通過と判定」に注記: `2026-10-29以降はZ dialogueもLR対象。この適用例は採用前の履歴であり、以後のZセリフHRはLR発動/非発動(LR不可=NO_USABLE_LR_INPUT/NO_CANDIDATE/確定内容保護)を必須項目4に記載する`。
- §30-2 項目4の文言「対象外/未配線/上限到達のいずれか」に `LR不可(入力なし・確定内容と重なる・候補全滅)` を例示追加。

## 5. HR page / er131 / er133 文言
- 該当する「Zセリフ LRなし/未配線」文言のGrep結果: er131/er132/er133 に該当記述なし(実装側の追加修正不要)。ページ文言の変更が必要か否かは委任_03で公開ページ再生成時に確認。
