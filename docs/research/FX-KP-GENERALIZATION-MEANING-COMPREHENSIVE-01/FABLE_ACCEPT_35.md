# FABLE_ACCEPT_35: 委任_35 X2p' XYZ共通 Production Wiring のFable受入記録(2026-10-24、委任_36、API 0・コード変更0)

## 判定(Fable、そのまま記録)
- 委任_35(docs/pm/RESULT_PACKET_KPGM35.md、PROD_WIRING_EVIDENCE_10.md、QUALITY_CHECK_35.md、CP_CHECK_35.md)をユーザー原文(USER_10)§3・§5の条件と照合:
  1. 正式初回経路での適用 = X正式入口`run_key_phrase_canonicalization`・Z正式`--stage kp`で全KP `meaning_stage=applied`
  2. retry・fallback・regeneration・resume整合 = WC-04混在batch 2 call / WC-06 prior再掲・HR / WC-07型喪失→安全停止
  3. 後続工程整合 = 新3欄はTTS・表示へ出さず、既存validator同一
  4. er112非依存 = WC-11
  5. 既存仕様不変 = 旧builder・schema・developer sha不変。A-1・②・gloss再整合は別責務で無変更
- runtime evidence 8項目(入口・model_id gpt-6-luna・Prompt sha・入出力対応・発火・test全回帰0/0・retry整合・Family別Status)すべて記録あり。
- 品質: `draw a line` = Std「一線を引く」/ Adv「境目をはっきりさせる」(字義訳解消、意味誤り0、字義が正解のKPの比喩化0)。
- 費用: gloss単価 +0.574円(X) / +0.424円(Z)。記事セットは承認時見込み(+0.44〜0.5円)の範囲内。

**判定: X = PRODUCTION_WIRED、Z = PRODUCTION_WIRED(Fable受入2026-10-24)。Y = COMMON_IMPLEMENTED_NOT_PRODUCTION_WIRED(OPEN-484、正式入口未存在)。記事B = USER_LISTENING_PENDING(最終試聴はユーザー判断)。**

## 監視指標
CURRENT_SPECの記録のみ指標「align費用0.6円/記事セット」「level所要60秒」の新基準案(1.0円/90秒、n=4暫定)はユーザー確認待ち(UDR #187、非blocking)。CURRENT_SPECの値は変更しない。

## 逸脱の記録
実装中にpatch script誤爆でProduction fileを一時破損 → commit前にSyntaxErrorで検出 → HEADから復元・再適用。旧builder source hash不変を確認。再発防止 = patch scriptは対象行をassertしてから書く。
