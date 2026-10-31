# RESULT_PACKET_JTA_01A(JA-TRANSLATION-LITERALNESS-AUDIT-01 委任_01A、2026-10-31、調査のみ・API 0・コード/仕様変更0)

容量: disk_guard OK(free 67.1GB)。STOP: stop_scope_check rc=0。

## 結論
1. **R2を流用している(新規翻訳なし)**。story部の「日本語」は英語の訳ではなく日本語原稿R2(`ja_writer/revision2.md`)の段落そのもの(`ja_source=approved_ja_manuscript`、sha256 `5a89d246…6227`が`ja_writer/runtime_evidence.json`・`build_info.json`と一致、LLM呼出0)。生成順=JA R0→R1→R2→Advanced英語(忠実英訳)→Standard英語(Advanced英語のA2書き直し。R2は入力に無い)。
2. 問題①: 日本語は2文(うち断片)、Std英語がA2規則で3文に分割。情報欠落・追加なし(ja_align g5/g6も意味どおり)。問題②: 「偏りを感じなかった人も…」は英語`std_17-s031`の訳(台帳F11一致)。ユーザー提示の英文はs028-s030でs031が欠け、点灯群g5=[s030,s031]が2文にまたがるための見かけの不一致(ユーザー実画面は未確認)。
3. **承認済みの逐語訳/意訳・要約禁止仕様は存在しない**(SSOT3ファイル `逐語訳`/`意訳`=0件)。逐語訳を含むユーザー原文は逆方向(KP日本語意味: 機械的逐語訳を強制しない)。近い承認済み=忠実英訳(JA→EN段落単位、CURRENT_SPEC.md:1406、PRODUCTION_WIRED)、承認済み原稿のみ表示(2026-10-29 USER:56-63)、生成訳の追加省略禁止Prompt(`er135_enduser_translate_01.py:41-43`)。配線漏れではなく仕様未定義。
4. 実測: X Std story 英214文 vs 日171文(文数一致段落34%、Adv83%)、Y Std 19%(Adv69%)、Z/生成訳70-83%。
5. Validator範囲: 承認済み原稿=段落数一致のみ(`er135_enduser_page_01.py:638-643`)。対訳照合(欠落/追加)は生成訳のみ(`translate_01.py:56`)。旧Deviation Check撤去済み、RFは非Blocking・Fact台帳基準。

## 判定整合
重大NG=なし(調査のみ、ユーザー提示物なし) / 主因=設計(JA原本・EN派生・Std文再分割)+検査欠如+仕様未定義 / 是正対象=委任_01B+ユーザー判断後 / STOP理由=なし / 提示=証拠のみ

## RESULT_PACKET 4行
(1) 既存仕様整合: CURRENT_SPEC.md:1406-1412,1185-1196,3287-3301,2112 / DECISION_LOG.md:12680-12690,12967,22943 / OPEN_ITEMS OPEN-618/634/638/243/230 / USER原文 2026-10-29 PRODUCTION-WIRING USER:56-63・2026-10-30 LINKED USER:35-40・USER_02:40,120-136。
(2) 未承認機能の既定値: 本委任でProduction変更0・flag追加0(調査+SSOT記録のみ)。確認=変更ファイルが docs/ と OPEN_ITEMS.md のみ。
(3) 失敗終了時の最終成果物: 失敗終了なし。成果物=docs/research/JA-TRANSLATION-LITERALNESS-AUDIT-01/{SPEC_HISTORY_01,PATH_TRACE_01,ROOT_CAUSE_01,RESULT_PACKET_JTA_01A}.md。目的適合: ユーザー原文§3(調査①)・§4(調査②)・§7(調査⑤)に回答。§5(全水準棚卸し)・§6(実データ意味照合)は委任_01B。ユーザー原文は保存済み(delegation_log/2026-10-31_JA-TRANSLATION-LITERALNESS-AUDIT-01_USER.md)。
(4) 撤去・残置: 撤去0。残置の旧Deviation Check撤去記録を確認のみ(CURRENT_SPEC.md:1194)。`grep 逐語訳|意訳` SSOT3=0。

## 未確認
ユーザーが問題②を見た実画面/クリック位置、承認済み原稿(X/Y story)の意味レベル全件照合(01B)、品質アラームTrial(OPEN-636)の検証セットに承認済み原稿が含まれるか、過去のSSOT未記録の口頭指示。

## 判断候補
なし(調査のみ)。参考: 改善案P1〜P5(ROOT_CAUSE_01.md §3)は新仕様/承認済み仕様変更を含むため、01B完了後にFableがD(真に新しい判断)として整理。分類=修正へ進む(要ユーザー判断後)。

## 次の一手
原因仮説=「JA原本・EN派生・Std文再分割×検査欠如」。観測=文数一致率(PATH_TRACE_01.md §4)。次: 01Bで意味照合の全件結果を得て、P4(決定論警告)の影響確定→方針をユーザーへ(見込み: 影響範囲確定は高、是正方式の確定はユーザー判断依存)。
