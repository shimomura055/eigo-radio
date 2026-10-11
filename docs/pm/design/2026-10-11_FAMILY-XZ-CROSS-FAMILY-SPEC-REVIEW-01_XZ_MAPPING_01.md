# FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01 Phase 2: X→Z横展開 対応表・A〜E分類・P0〜P2・ユーザー判断事項

- 管理ID: FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01 委任_03(Sonnet実行層、2026-10-11)。作業時点origin/main HEAD f595ba08
- 性格: 調査・比較・提案のみ。コード/Prompt/Routing/SSOT/Trial成果物の変更なし、API費用0円。**本書は正式SSOTではない。推奨は提案であり、採否はユーザー**
- 入力: X_INVENTORY_01(101項目)・Z_INVENTORY_01・委任ログ_01/_02。A〜E・P0〜P2の定義はユーザー元指示を逐語保存した `..._USER_INSTRUCTION_01.md` のとおり(自作していない)
- 機械可読版: 同名 `.json`(rows[]: x_item_id, area, z_status, classification, priority, rationale, depends_on, user_decision_ref)

## 0. 要約

- 対応行: 101件(Family X固有60+共通層31+GOVERNANCE 10)。Z固有ギャップ4件(ZG-01〜04)は別表(101件外)
- 分類別件数(101件): A:既に共通=19 / B:横展開推奨=14 / C:条件付き=17 / D:対象外=39 / E:判断保留=12
- 主対象91件(Family X固有60+共通31)の分類: A=11 / B=14 / C=17 / D=39 / E=10(GOVERNANCE 10件はA 8件『共通で適用済み』と簡略化、E 2件=7-08/11-03)
- 優先度: P0=12件 / P1=21件 / P2=10件(A・D=優先度対象外 58件)。P0のうちZ TTS/Assembly配線(OPEN-185)が前提=11件、前提なし=1件(6-03 4+1 runner統合のみ)
- ユーザー判断事項: 13件(§5)。未確認事項: 23件(§6)
- 最重要: Zは『text工程のみ実装、PRODUCTION_WIREDではない』。X→Z横展開の多くはZ TTS/Assembly配線(OPEN-185、UD-01)が前提。Xの未完了Wiring(J2/E2/F1.5)をZ展開の完了済み前提にしない

### Status確認結果(作業時点、SSOT/Gitで確認)

| 仕様 | 確認結果 |
|---|---|
| Sol E案(B3/R0/R1/R2=gpt-6.1-sol) | PRODUCTION_WIRED(merge adb15c30、SSOT 2823d0ea。CURRENT_SPEC/DECISION_LOG記載)。ただしZに該当工程なし(3-02=D) |
| SCG(OPEN-258) | 実装はmain merge済み(382c56c5、origin/mainに含む)。**SSOT(CURRENT_SPEC/DECISION_LOG『SCG』0件、OPEN_ITEMS OPEN-258行は旧Status『DESIGN_READY_FOR_REVIEW』)は未反映**。本書は『main merge済み・SSOT未反映』と記載し、SSOTベースのPRODUCTION_WIREDとは書かない |
| J2/E2_UPBEAT/F1.5(Tone) | APPROVED_FOR_PRODUCTION(2026-10-11、ユーザー指示)。SSOT未記録・main未merge(feature/coffee-new-tone-01にStyle配線commit 24acf9f4のみ、有料E2Eはuser判断待ち)=approved-but-unwired。Zへの適用承認は無い |
| Role Style J3/E2(TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02) | PRODUCTION_WIRED(X、2026-09-28)。Tone Trial『E2_UPBEAT』とは別物 |
| Z Production | text工程のみ実装(commit 42b43772)。TTS/AssemblyはNotImplementedError。PRODUCTION_WIREDではない。Phase A設計(55cb58ed)は設計のみ・未承認論点あり |

## 1. 分類・優先度の定義(ユーザー元指示そのまま)

| 分類 | 意味 |
|---|---|
| A：既に共通 | Family Zに同等仕様が正式実装済み |
| B：横展開推奨 | Family Zにも適用する価値が高い |
| C：条件付き | Family Z向けの調整・検証が必要 |
| D：対象外 | Family X固有でFamily Zに適用しない |
| E：判断保留 | 仕様や実装の確認が不足 |

- P0：品質・安全性・重大な不整合の防止 / P1：ユーザー体験・記事品質の改善 / P2：効率化・保守性改善(元指示にA/Dの優先度定義は無い=A/Dは『-』、未定義)
- z_status語彙: 実装あり/一部/なし/共有module経由/意図的差異/未確認(『なし』=Zに該当実装なし)
- 注: A『正式実装済み』=Z側に同等仕様が承認・実装済みの意味。Z全体はPRODUCTION_WIREDではない

## 2. 優先順の提案サマリ(PM判断影響順)

1. すぐ横展開すべき(B): 4+1 KP runner統合(6-03、P0、前提なし)。Z TTS/Assembly配線(UD-01)と同時に共有module呼出し(ASR/retry/HRR/Audio Validation/Master Store/headroom)
2. Z向け調整が必要(C): 記号QA(3-05)、3分割+Comment4(5-01/02)、Role Style/Flash-Lite(7-01/03,6-06)、Tone(7-04/05)、固定phrase(7-06)、SCG(8-07)、速度(4-04)、fallback(10-02)
3. 横展開すべきでない(D): Research/Fact Ledger/B3/W-1/Sol E案/Advanced英訳/50-25-25比率/Voice割当/見出し系(Z固有の価値=原作忠実・外部Seed方式を損なう)
4. 判断保留(E): KP DB Hybrid(UD-06)、EN意味等価性・resume・試聴ページ等の未確認

## 3. X→Z対応表(12領域)

### 領域1. Research・Fact抽出・Fact Ledger

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 1-01 | Research(web_search)+独立Verification / PRODUCTION_WIRED(SHARED) | 意図的差異 | D | - | 外部Seed方式(CURRENT_SPEC Family Z 1/3、2026-09-26)でZに該当工程なし。Research不在 |  |  |
| 1-02 | Verified Fact Ledger(verified_fact_ledger.txt) / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | 外部Seed方式(CURRENT_SPEC Family Z 1/3、2026-09-26)でZに該当工程なし。原文が一次資料、Fact Ledger不要(Phase A §5) |  |  |
| 1-03 | AMBIGUOUS Fact扱い / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Fact Ledgerが無いためAMBIGUOUS Fact概念が不要 |  |  |
| 1-04 | Ledger parser(決定論) / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Ledger自体がZに無い |  |  |
| 1-05 | Fact台帳の明確化(上流対策)設計 OPEN-237 / OPEN_UNAPPROVED(FAMILY_X) | なし | D | - | X側OPEN(未承認)・Fact Ledger上流対策。Zに無関係 |  |  |
| 1-06 | Trial driver側 --theme パス文字列混入の影響 OPEN-240 / OPEN_UNAPPROVED(FAMILY_X) | なし | D | - | X Trial driver固有OPEN |  |  |

### 領域2. Fact選択・Storyline・B3

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 2-01 | storyline_b3(Storyline1行+Fact選定、4テスト) / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Z許容編集は脇筋削除等のみ(Story内容方針2)。Fact選択・B3は機械移植しない(元指示5) |  |  |
| 2-02 | 決定論B3 producer(D-det v2+D-full assembler) / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Z許容編集は脇筋削除等のみ(Story内容方針2)。Fact選択・B3は機械移植しない(元指示5) |  |  |
| 2-03 | 注記済みB3入力契約 V1〜V10(fail-closed) / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Z許容編集は脇筋削除等のみ(Story内容方針2)。Fact選択・B3は機械移植しない(元指示5) |  |  |
| 2-04 | B3再選定時のU-1 STOPと下流再生成 OPEN-249 / OPEN_UNAPPROVED(FAMILY_X) | なし | D | - | X B3再選定固有OPEN |  |  |
| 2-05 | Fact数・Fact選定の品質ゲート / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Z許容編集は脇筋削除等のみ(Story内容方針2)。Fact選択・B3は機械移植しない(元指示5) |  |  |

### 領域3. 日本語記事生成 R0/R1/R2

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 3-01 | W-1 Writer(R0 Fact Lock→R1→R2) / PRODUCTION_WIRED(FAMILY_X) | なし | D | - | W-1はX日本語記事Writer。Z本文は英語canonical text。ZのStory圧縮Writerは別物(ZG-02) |  |  |
| 3-02 | 日本語記事モデル配置E案(B3/R0/R1/R2=gpt-6.1-sol) / PRODUCTION_WIRED(FAMILY_X) | なし | D | - | Sol E案はX記事のB3/R0/R1/R2工程。Zにこの工程が無い。Z Preview/Commentはrouting A2_WRITER(gpt-6-luna) |  |  |
| 3-03 | 旧配置 R0=gpt-6-luna / R1・R2=gpt-6-astra / SUPERSEDED_REMOVED(FAMILY_X) | なし | D | - | SUPERSEDED(旧配置)。現行仕様として扱わない |  |  |
| 3-04 | U-1(W-1来歴のないJA再利用禁止)/U-2(単体CLI封鎖) / PRODUCTION_WIRED(FAMILY_X) | なし | D | - | X W-1来歴ガード。Z Preview/Comment/In One LineにJA再利用経路なし |  |  |
| 3-05 | 音声化禁止記号QA(案A) / PRODUCTION_WIRED(FAMILY_X) | 一部 | C | P0 | CURRENT_SPEC L2126『Z Writer実装時はTTS記号正規化(Prompt予防+Normalizer+Gate)必須』。Z Preview/Comment/In One LineもTTS入力。Z側の記号QA呼出しは未確認 | OPEN-185 Z TTS/Assembly配線 | UD-02 |
| 3-06 | Concreteness Control(AN3-T0) / PRODUCTION_WIRED(FAMILY_X) | なし | D | - | X日本語記事Writer固有(AN3-T0) |  |  |
| 3-07 | Prompt sha・verbatim固定 / PRODUCTION_WIRED(FAMILY_X) | 未確認 | E | P2 | Z promptはer026内定数。sha/verbatim固定の有無を未確認 |  |  |
| 3-08 | 生成段階の禁止記号予防 OPEN-261 / OPEN_UNAPPROVED(FAMILY_X) | なし | E | P2 | X OPEN-261(未承認)。TTS入力全般に波及し得るため、X側結論後にZ要否を再評価 | X側OPEN-261結論 |  |
| 3-09 | 記号QAが句読点重複『、。』を検出しない OPEN-262 / OPEN_UNAPPROVED(FAMILY_X) | なし | E | P2 | X OPEN-262(未承認)。記号QA共通部の穴。X側結論後にZ要否を再評価 | X側OPEN-262結論 |  |
| 3-10 | JA R2がENでの修正・削除に追随しない OPEN-239 / OPEN_UNAPPROVED(FAMILY_X) | なし | D | - | X JA/EN二重管理固有OPEN |  |  |
| 3-11 | 旧JA Writer O→R1→R2(+JA Fact Check/差し戻し) / SUPERSEDED_REMOVED(FAMILY_X) | なし | D | - | SUPERSEDED(撤去済み) |  |  |
| 3-12 | 日本語記事OKマスター(HUMAN_APPROVED_QUALITY_MASTER) / RECORD_ONLY(FAMILY_X) | なし | D | - | X記事OKマスター(記録) |  |  |

### 領域4. 英語化・難易度調整

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 4-01 | Advanced(B1B)忠実英訳(見出し生成なし) / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Z英語化工程なし(現代英訳は流用不可、Seed要件)。B1BはZに存在せずPhase A §3gもZ対象外 |  |  |
| 4-02 | M1(a) In one line(Advanced限定・無条件ON) / PRODUCTION_WIRED(FAMILY_X) | 実装あり | A | - | Z-3 In One Line(EN、Z所有prompt)実装済み(er026、run_01)。Z全体はPRODUCTION_WIREDではない |  |  |
| 4-03 | Standard(A2)Level調整 / PRODUCTION_WIRED(SHARED) | 共有module経由 | A | - | ZはA2のみ(scaffold a2gen共有)。A2限定の明示決定記録は未確認(UD-12) |  | UD-12 |
| 4-04 | Standardの英語6%減速 / PRODUCTION_WIRED(SHARED) | なし | C | P1 | 共有apply_a2_slowdown_postprocess。Z TTS未実装。Dialogue多声clipへの6%減速要否はZ固有決定が未確認 | OPEN-185 Z TTS/Assembly配線 | UD-08 |
| 4-05 | 翻訳段のLedger Deviation Check/M1(b)/G3 / SUPERSEDED_REMOVED(FAMILY_X) | なし | D | - | SUPERSEDED |  |  |
| 4-06 | 翻訳段の事実NG(主体取違え・複数形化等) OPEN-243 / OPEN_UNAPPROVED(FAMILY_X) | なし | D | - | X翻訳段OPEN-243(未承認) |  |  |

### 領域5. 記事構造・Comment・Preview・In One Line

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 5-01 | 新記事構造(途中Heading廃止・段落境界3分割) / PRODUCTION_WIRED(FAMILY_X) | なし | C | P1 | Phase A案(55cb58ed)3分割 body1=story001-006/body2=007/body3=008 境界(6,7)。未承認・未実装。X比率50/25/25は移植しない | OPEN-185 Z TTS/Assembly配線 | UD-03 |
| 5-02 | Comment 4本 / PRODUCTION_WIRED(FAMILY_X) | 一部 | C | P1 | Z=Comment1のみ実装(Family C呼出)。Comment2-4未実装、Comment4はZ所有新prompt案(未承認) | OPEN-185 Z TTS/Assembly配線 | UD-03 |
| 5-03 | Preview(Standard=日本語/Advanced=英語) / PRODUCTION_WIRED(SHARED) | 実装あり | A | - | Z Preview(JA、Z所有prompt)実装済み(er026) |  |  |
| 5-04 | In One Line(短文) / PRODUCTION_WIRED(FAMILY_X) | 実装あり | A | - | Z In One Line実装済み(Z-3)。Xは短文・Advanced限定、Zは別prompt |  |  |
| 5-05 | 本文1/2/3比率(50/25/25) / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Z語数は原作忠実の115/133/135(Phase A案)。X 50/25/25は機械移植しない |  |  |
| 5-06 | 段落数不足の1回must-fix再生成 / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Z本文はcanonical固定でLLM再生成しない |  |  |
| 5-07 | Section Segmentation(見出し境界)Contract / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | X固有契約(途中Heading)。Zの見出し読み上げ無し(案)の決定記録は未確認だがZに無関係 |  |  |
| 5-08 | 見出し独立sub-segment(HEADING_READOUT) / SUPERSEDED_REMOVED(FAMILY_X) | なし | D | - | SUPERSEDED |  |  |
| 5-09 | 音声runnerのsource_dir導出 OPEN-234 / OPEN_UNAPPROVED(FAMILY_X) | なし | D | - | X OPEN-234固有 |  |  |

### 領域6. Key Phrases・解説・レベル別仕様

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 6-01 | Key Phrase選定: DB Hybrid(Primary)/Strategy L(Fall / PRODUCTION_WIRED(FAMILY_X) | 未適用(Strategy L) | E | P1 | Z DB HybridはTrial『不十分』(Melos1本)、Core v2修正後Z採用は未決定。family_profile='family_z'はNotImplementedError(er030)。意図的差異の記録なし |  | UD-06 |
| 6-02 | KP選定LLM出力契約(Source Reference Contract、候補ID方式) / PRODUCTION_WIRED(SHARED) | なし(Z runner未配線) | C | P1 | Contractは『X/Z共通Core』APPROVED(2026-09-28)だがZ runner未配線。DB Hybrid採否に連動(N2: Z DB Hybrid配線は候補ID必須) | UD-06の結論 | UD-06 |
| 6-03 | 4+1構成(重要語4+Topic Phrase/Word 1) / PRODUCTION_WIRED(SHARED) | 一部 | B | P0 | 4+1 APPROVED。Z run_01は4+1導入前schemaで非互換。er035_output/kp_4plus1_evidence_01/melos_a2はPASS。runner統合のみ(新仕様決定不要) |  |  |
| 6-04 | KP音声構造(共通骨格: 英語Phrase→中間→英語Phrase) / PRODUCTION_WIRED(FAMILY_X) | なし | B | P1 | KP音声構造は共有assembler/scaffold。Z TTS/Assembly実装時に共有moduleを呼ぶ | OPEN-185 Z TTS/Assembly配線 |  |
| 6-05 | Advanced Key Phrase英語解説(text仕様+Aoede/Variant B s / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Advanced(B1B)限定。ZはA2のみでPhase A §3g対象外 |  |  |
| 6-06 | Standard Key Phrase日本語意味へのJ3適用 / PRODUCTION_WIRED(FAMILY_X) | なし | C | P1 | Z Standard KP日本語意味へのJ3適用はresolver拡張とFlash-Lite既定が前提(設計案のみ) | OPEN-185 Z TTS/Assembly配線 | UD-04 |
| 6-07 | KP日本語gloss規約(表示用/TTS用分離・数値placeholder回避・括弧併記禁止・自 / PRODUCTION_WIRED(SHARED) | 共有module経由 | A | - | scaffold.run_key_phrases(A2)が共有。Z run_01は4+1前schema(6-03参照) |  |  |
| 6-08 | KP英語Component生成(Minimal instruction+English Lock / PRODUCTION_WIRED(SHARED) | 共有module経由 | A | - | er003共有KP英語Component(Zはrun_key_phrases経由) |  |  |
| 6-09 | Strategy L(Listening Blocker Ranking)/5件/1〜5語 / PRODUCTION_WIRED(SHARED) | 実装あり | A | - | ZのKey PhraseはStrategy L経路(run_01) |  |  |

### 領域7. 音声Voice・Style・TTS・速度

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 7-01 | TTS backend: speech_metadata_flash_lite / gemini / PRODUCTION_WIRED(FAMILY_X) | なし | C | P1 | backendは共有moduleだが配線ゲートはX tts_backend明示。Z適用は設計案のみ、既定未決。Z多声Dialogueとの整合要検証 | OPEN-185 Z TTS/Assembly配線 | UD-04 |
| 7-02 | Voice割当(Charon/Aoede) / PRODUCTION_WIRED(FAMILY_X) | 意図的差異 | D | - | Z-4 Dialogue Voice(narrator=Aoede/dialogue=Erinome/Charon等)。X Charon/Aoede割当は移植しない |  |  |
| 7-03 | Role Style 現行: JA=J3 / EN=E2 / PRODUCTION_WIRED(FAMILY_X) | なし | C | P1 | Z設計案: Preview/Comment=J3、Full Story/In One Line=E2。resolver拡張が前提。名称『E2』はRole Style(TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02、2026-09-28)でTone Trial E2_UPBEATと別 | OPEN-185 Z TTS/Assembly配線 | UD-04,UD-05 |
| 7-04 | 新Tone: J2(JA明るく親しみやすい)/E2(EN upbeat、Preview・Comm / IN_PROGRESS(FAMILY_X) | なし | C | P1 | J2/E2_UPBEATはAPPROVED_FOR_PRODUCTION(2026-10-11、X Coffee E2E指示内)だがSSOT未記録・main未merge(feature/coffee-new-tone-01はStyle配線のみ、有料E2Eはuser判断待ち)。Zへの適用承認は無い | OPEN-185 Z TTS/Assembly配線; X側Tone配線・E2E完了 | UD-07 |
| 7-05 | 新Tone: Full Story F1.5 / IN_PROGRESS(FAMILY_X) | なし | C | P1 | F1.5は同上(approved-but-unwired)。Z Full StoryはDialogue多声clipで、X単一narrator前提のToneは再検証要 | X側Tone配線・E2E完了 | UD-07 |
| 7-06 | 固定フレーズChampion(10 phrase) / PRODUCTION_WIRED(FAMILY_X) | なし | C | P1 | Phase A §3e: 汎用Master Storeでlookup(Z固有登録不要)。num_three/num_fiveがSSOT未確定と委任文(B take1)で食い違い | OPEN-185 Z TTS/Assembly配線 | UD-10 |
| 7-07 | 音量・ヘッドルーム(RMS正規化+最終段安全弁) / PRODUCTION_WIRED(SHARED) | なし | B | P1 | 共有er003_v1_n3_01_assemble。Z stage_assemble実装時に共有gain/headroomを呼ぶ(個別実装不要) | OPEN-185 Z TTS/Assembly配線 |  |
| 7-08 | TTS Batch/Standard同期の実行方式 / UNCONFIRMED(GOVERNANCE) | 未確認 | E | P2 | TTS実行方式(Batch/同期)の管理は運用側。Z runnerの実行方式は未確認 |  |  |
| 7-09 | Tone Trial: 旧日本語好評価音源の特定 / RECORD_ONLY(FAMILY_X) | なし | D | - | Tone Trial記録(RECORD_ONLY) |  |  |

### 領域8. ASR・読み誤り・再生成・SCG

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 8-01 | 日本語ASR Validator+Secondary ASR Cascade / PRODUCTION_WIRED(SHARED) | なし | B | P0 | 日本語ASR Validator+Secondary ASR共有module。Z JA segment(Preview/Comment1)にTTS後検証が必要。Z stage_tts未実装 | OPEN-185 Z TTS/Assembly配線 | UD-09 |
| 8-02 | 英語ASR: Secondary ASR Cascade(Azure+Phrase List)・ / PRODUCTION_WIRED(SHARED) | なし | B | P0 | 英語ASR Cascade共有。Zの短いDialogue clipでのPhrase List運用は実装時確認 | OPEN-185 Z TTS/Assembly配線 |  |
| 8-03 | English ASR Semantic Equivalence Layer(Tier1数値等価 / PRODUCTION_WIRED(SHARED) | 未確認 | E | P0 | ZでのEN Semantic Equivalence適用は未確認(Z inventory 3-8)。P0は暫定(TTS品質Gate) | OPEN-185 Z TTS/Assembly配線 |  |
| 8-04 | A2 Reading Resolver(OPEN-111) / PRODUCTION_WIRED(SHARED) | 未確認 | E | P1 | A2 JA Reading ResolverのZ JA segment適用は未確認(ZはER025 resolver family_z_melosを別途実装済み) | OPEN-185 Z TTS/Assembly配線 |  |
| 8-05 | Pronunciation Ledger(ASR側配線のみ) / PRODUCTION_WIRED(SHARED) | 一部 | B | P1 | er025 resolver(source_context=family_z_melos)実装済み。ASR Phrase List側配線・Gemini TTS反映は別Phase課題 | OPEN-185 Z TTS/Assembly配線 |  |
| 8-06 | TTS Pronunciation Hint(style/metaへの発音ヒント注入) / NOT_WIRED_FOUNDATION(SHARED) | なし | E | P2 | X側もNOT_WIRED_FOUNDATION(配線見送り)。Zの人物名読みTTS反映要否はX側判断後 | X側Hint配線判断 |  |
| 8-07 | SCG(Secondary Confirm Gate、日本語) / IN_PROGRESS(SHARED) | なし | C | P1 | SCG実装はmain merge済み(382c56c5)。ただしSSOT(CURRENT_SPEC/DECISION_LOG/OPEN-258行)は未反映のため本書ではSSOTベースの『PRODUCTION_WIRED』と書かない。ZのJA segmentはPreview/Comment1と少量。適用要否と再生成コストは要判断 | OPEN-185 Z TTS/Assembly配線; SCGのSSOT反映 | UD-09 |
| 8-08 | OPEN-258 Phase 0 Trial(V1方式) / VALIDATED_TRIAL_ONLY(SHARED) | なし | D | - | Trial記録(VALIDATED_TRIAL_ONLY)。仕様ではない |  |  |
| 8-09 | TTS retry: 10分cool-down+Local Rewrite+Natural En / PRODUCTION_WIRED(SHARED) | なし | B | P0 | 共有er020(attempt1→即時2→10分cool-down→3→Local Rewrite+Natural English QA)。Z未配線。Connected Speech 5roleはresolve_narrative_roleがfull_story_part1/2/3完全一致のためZ 8 voice-clipは対象外(known_gap) | OPEN-185 Z TTS/Assembly配線 | UD-05 |
| 8-10 | Local Rewrite 全文性検証(位置非依存、OPEN-256) / PRODUCTION_WIRED(SHARED) | なし | B | P0 | 共有全文性検証。Local Rewrite時のVoice assignment保持はruntime evidence未取得(Phase A『確認要』) | OPEN-185 Z TTS/Assembly配線 |  |
| 8-11 | Human Review Route(未解決ASR不確実性の送り先) / PRODUCTION_WIRED(SHARED) | なし | B | P0 | 共有er011 human_review_lock。Z未配線 | OPEN-185 Z TTS/Assembly配線 |  |
| 8-12 | 未承認候補: OPEN-257/259/260 / OPEN_UNAPPROVED(SHARED) | なし | E | P2 | X側OPEN-257/259/260(未承認)。X結論後にZ要否を再評価 | X側OPEN結論 |  |

### 領域9. Validator・品質Gate・Review Queue

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 9-01 | Risk Flagger 4条件(non-blocking) / PRODUCTION_WIRED(FAMILY_X) | 未確認 | C | P2 | Risk FlaggerはX(英語記事Fact)向け。ZはSeed原文で事実誤り型リスクが低い可能性があるがZ適用有無は未確認。Z用criteria再設計が必要 |  | UD-11 |
| 9-02 | RFの非Blocking契約・例外・状態 / PRODUCTION_WIRED(FAMILY_X) | 未確認 | C | P2 | RF非Blocking契約はX(英語記事Fact)向け。ZはSeed原文で事実誤り型リスクが低い可能性があるがZ適用有無は未確認。Z用criteria再設計が必要 |  | UD-11 |
| 9-03 | Review Queue(post_en) / PRODUCTION_WIRED(FAMILY_X) | 未確認 | C | P2 | Review QueueはX(英語記事Fact)向け。ZはSeed原文で事実誤り型リスクが低い可能性があるがZ適用有無は未確認。Z用criteria再設計が必要 |  | UD-11 |
| 9-04 | TTS前3者照合guard(ensure_rf_record) / PRODUCTION_WIRED(FAMILY_X) | 未確認 | C | P2 | TTS前3者照合guardはX(英語記事Fact)向け。ZはSeed原文で事実誤り型リスクが低い可能性があるがZ適用有無は未確認。Z用criteria再設計が必要 | OPEN-185 Z TTS/Assembly配線 | UD-11 |
| 9-05 | 旧Fact Checker/Ledger Deviation/must-fix/JA差し戻し(案 / SUPERSEDED_REMOVED(FAMILY_X) | なし | D | - | SUPERSEDED |  |  |
| 9-06 | 技術QA(旧Fact Checkerとは別、維持) / PRODUCTION_WIRED(SHARED) | 一部 | B | P0 | Zはstory_type/人名/語数/rights gate/KP redundancy QAを実装済み。ASR・headroom・記号・TTS technical retry等の共有QAはZ TTS配線時に呼ぶ | OPEN-185 Z TTS/Assembly配線 |  |
| 9-07 | Audio Validation Gate(episode音声検証) / PRODUCTION_WIRED(SHARED) | なし | B | P0 | 共有verify_episode_audio_validation_gate。Z stage_assemble/Audio Validation未実装 | OPEN-185 Z TTS/Assembly配線 |  |
| 9-08 | PM運用Gate 1〜7・Closeout Mandatory Check(PM層ルール) / OPERATIONAL_RULE(GOVERNANCE) | 共有module経由 | A | - | GOVERNANCE: Family非依存 |  |  |
| 9-09 | 全回帰suite既存36 failed OPEN-252 / OPEN_UNAPPROVED(FAMILY_X) | なし | D | - | X側テスト負債OPEN-252 |  |  |

### 領域10. retry・fallback・regeneration・resume

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 10-01 | TTS attempt上限(Production=3) / PRODUCTION_WIRED(SHARED) | なし | B | P0 | 共有TTS attempt上限3(assert固定)。Z TTS未配線 | OPEN-185 Z TTS/Assembly配線 |  |
| 10-02 | fallback(minimal instruction / EN fallback style / PRODUCTION_WIRED(FAMILY_X) | なし | C | P1 | fallback styleはX EN fallback('natural, clear, conversational')。Z多声Dialogueでの妥当性は要検証。voice切替fallbackはX側も未確認 | OPEN-185 Z TTS/Assembly配線 |  |
| 10-03 | Local Rewrite(retry系の最終段) / RECORD_ONLY(SHARED) | なし | D | - | 8-09/8-10参照のみ(重複) |  |  |
| 10-04 | regenerate-stage(runner別) / PRODUCTION_WIRED(FAMILY_X) | 未確認 | E | P1 | Z runnerのstage再実行機構は未確認(コード全読未実施) |  |  |
| 10-05 | resume(既存成果物の再利用) / PRODUCTION_WIRED(FAMILY_X) | 未確認 | E | P1 | Z runnerのresumeは未確認(Z inventory 10) |  |  |
| 10-06 | PASS済み成果物の不要再実行・上書き禁止 / OPERATIONAL_RULE(GOVERNANCE) | 共有module経由 | A | - | GOVERNANCE |  |  |
| 10-07 | retry上限一覧(個別) / PRODUCTION_WIRED(SHARED) | 一部 | B | P0 | ZはPreview/In One Line max_attempts=2実装済み。TTS側retryは共有(未配線) | OPEN-185 Z TTS/Assembly配線 |  |
| 10-08 | segmentのretry_count累計表示不整合 OPEN-254 / OPEN_UNAPPROVED(FAMILY_X) | なし | D | - | X OPEN-254(表示不整合) |  |  |

### 領域11. 音声Assembly・Master Store・試聴ページ

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 11-01 | 音声runner(plan→scaffold→tts→assemble→player) / PRODUCTION_WIRED(FAMILY_X) | 一部 | D | - | X専用audio runner。Zは専用runner er026(Z-2承認)。stage_tts/stage_assembleはNotImplementedError(=ZG-01) |  |  |
| 11-02 | Master Audio Store(固定phrase・KP phrase reuse) / PRODUCTION_WIRED(SHARED) | なし | B | P1 | 汎用Master Storeでfixed phrase lookup(Family固有登録不要、Phase A §3e)。Zの可変clipは対象外 | OPEN-185 Z TTS/Assembly配線 |  |
| 11-03 | 試聴・配布経路(GitHub Pages user_test) / OPERATIONAL_RULE(GOVERNANCE) | 未確認 | E | P1 | Z試聴ページ生成経路は未確認(Z inventory 3-11)。共有audio_review_player.py利用想定 | OPEN-185 Z TTS/Assembly配線 |  |
| 11-04 | Gate 7(音声artifact受入チェックリスト (a)〜(n)) / OPERATIONAL_RULE(GOVERNANCE) | 共有module経由 | A | - | GOVERNANCE(Gate 7チェックリスト) |  |  |
| 11-05 | META完成音声の公開判断 / RECORD_ONLY(FAMILY_X) | なし | D | - | X META公開判断記録 |  |  |

### 領域12. コスト・runtime管理・運用ルール

| X item | X名 / X Status(scope) | Z現状 | 分類 | 優先 | 根拠(1行) | 依存 | 判断 |
|---|---|---|---|---|---|---|---|
| 12-01 | pricing_snapshot.json(単価台帳、fail-closed) / PRODUCTION_WIRED(SHARED) | 共有module経由 | A | - | 共有pricing_snapshot |  |  |
| 12-02 | er009 PRICING_USD_PER_M表 / PRODUCTION_WIRED(SHARED) | 共有module経由 | A | - | 共有er009 |  |  |
| 12-03 | 予算ガード(assert_budget_ok/BudgetCheckStop) / PRODUCTION_WIRED(SHARED) | 実装あり | A | - | er026 budget guard(Cap 200円/WARN 150円)実装済み |  |  |
| 12-04 | cost.json(stage別・provider別・RF Level別) / PRODUCTION_WIRED(FAMILY_X) | 実装あり | A | - | Z run_01 cost.json出力(LLM実測約0.46円)。RF Level別はZに無関係 |  |  |
| 12-05 | 1記事セット費用(E案)見積 / RECORD_ONLY(FAMILY_X) | なし | D | - | X E案費用見積(記録) |  |  |
| 12-06 | 運用: ACTIVE_TASK/RESULT_PACKET/委任ログ・委任文標準 / OPERATIONAL_RULE(GOVERNANCE) | 共有module経由 | A | - | GOVERNANCE: Family非依存で適用済み(PM_GOVERNANCE) |  |  |
| 12-07 | 最新モデル原則(開発・評価用途) / OPERATIONAL_RULE(GOVERNANCE) | 共有module経由 | A | - | GOVERNANCE: Family非依存で適用済み(PM_GOVERNANCE) |  |  |
| 12-08 | Git自律処理方針 / OPERATIONAL_RULE(GOVERNANCE) | 共有module経由 | A | - | GOVERNANCE: Family非依存で適用済み(PM_GOVERNANCE) |  |  |
| 12-09 | 開発時間最小化・並列実行原則/Opus独立レビューGate/Existing Spec Chec / OPERATIONAL_RULE(GOVERNANCE) | 共有module経由 | A | - | GOVERNANCE: Family非依存で適用済み(PM_GOVERNANCE) |  |  |
| 12-10 | コスト報告ルール(15)・予算Cap・TTS実行方式別管理 / OPERATIONAL_RULE(GOVERNANCE) | 共有module経由 | A | - | GOVERNANCE: Family非依存で適用済み(PM_GOVERNANCE) |  |  |
| 12-11 | ASTRA請求照合 OPEN-246 / 費用機構周辺OPEN / OPEN_UNAPPROVED(FAMILY_X) | なし | D | - | X ASTRA請求照合OPEN-246 |  |  |

### Z固有ギャップ(X一覧外、分類=Z-GAP)

| id | 内容 | Z現状 | 優先 | 備考 | 判断 |
|---|---|---|---|---|---|
| ZG-01 | TTS stage/Assembly/Audio Validation/試聴ページ(OPEN-185、stage_tts/stage_assembleはNotImplementedError) | 未実装 | P0 | ZのPRODUCTION_WIRED前提。X→Z横展開の多くが依存 | UD-01 |
| ZG-02 | Z Production Writer(Story圧縮)+記号QA必須(CURRENT_SPEC L2126) | 未実装 | P0 | Melosは既存er018 Trial story.mdを入力。量産するならWriter必須 | UD-02 |
| ZG-03 | Seed選定のProduction化(仕様なし)+PM_GOVERNANCE 13節(テーマはユーザー選択) | 未整備 | P1 | 運用フロー未定義 | UD-02 |
| ZG-04 | Topic intro生成・Melos以外のStory(registryはmelosのみ) | 未実装 | P2 | ID定義のみ |  |

## 4. 横展開推奨リスト(P0/P1/P2、概算規模・費用感)

規模: S=数時間・1ファイル内、M=複数ファイル+テスト、L=複数stage+runtime検証。費用は根拠資料のある範囲のみ(Phase A §5: Z一回限りE2E約30-40円、Guardrail案60円、恒常差分Comment+1 call約+3円/記事)。その他の有料runtimeは見積なし(実行しない)。

### P0(品質・安全性・重大な不整合の防止)

| item | 内容 | 規模 | 有料runtime(見積のみ) | 依存 |
|---|---|---|---|---|
| 3-05 | 音声化禁止記号QA(案A) | M | なし(Normalizer+Gate、決定論) | OPEN-185 Z TTS/Assembly配線 |
| 6-03 | 4+1構成(重要語4+Topic Phrase/Word 1) | S-M | なし(er035 evidence既存)。runner統合後のZ run再実行は約0.5円級(run_01 LLM実測0.46円) | なし |
| 8-01 | 日本語ASR Validator+Secondary ASR Cascade | M | ZTTS配線E2Eに含む(個別見積なし) | OPEN-185 Z TTS/Assembly配線 |
| 8-02 | 英語ASR: Secondary ASR Cascade(Azure+Phras | M | 同上 | OPEN-185 Z TTS/Assembly配線 |
| 8-03 | English ASR Semantic Equivalence Layer(T | S(確認後) | なし | OPEN-185 Z TTS/Assembly配線 |
| 8-09 | TTS retry: 10分cool-down+Local Rewrite+Na | M | ZTTS配線E2Eに含む | OPEN-185 Z TTS/Assembly配線 |
| 8-10 | Local Rewrite 全文性検証(位置非依存、OPEN-256) | S-M | 同上 | OPEN-185 Z TTS/Assembly配線 |
| 8-11 | Human Review Route(未解決ASR不確実性の送り先) | S | なし | OPEN-185 Z TTS/Assembly配線 |
| 9-06 | 技術QA(旧Fact Checkerとは別、維持) | L(集約) | 個別見積なし | OPEN-185 Z TTS/Assembly配線 |
| 9-07 | Audio Validation Gate(episode音声検証) | M | ZTTS配線E2Eに含む | OPEN-185 Z TTS/Assembly配線 |
| 10-01 | TTS attempt上限(Production=3) | S | なし | OPEN-185 Z TTS/Assembly配線 |
| 10-07 | retry上限一覧(個別) | S | なし | OPEN-185 Z TTS/Assembly配線 |
| ZG-01 | Z TTS/Assembly/Audio Validation/試聴ページ(上記の前提) | L | 一回限り約30-40円(Guardrail60円)、Phase A §5見積 | UD-01 |
| ZG-02 | Z Production Writer | L | 未見積 | UD-02 |

### P1(体験・記事品質)

| item | 内容 | 規模(推定) | 必要なTrial | 依存/判断 |
|---|---|---|---|---|
| 4-04 | Standardの英語6%減速 | M | 要(Z用音声Trial) | OPEN-185 Z TTS/Assembly配線 / UD-08 |
| 5-01 | 新記事構造(途中Heading廃止・段落境界3分割) | M | 要(Z用音声Trial) | OPEN-185 Z TTS/Assembly配線 / UD-03 |
| 5-02 | Comment 4本 | M | 要(Z用音声Trial) | OPEN-185 Z TTS/Assembly配線 / UD-03 |
| 6-01 | Key Phrase選定: DB Hybrid(Primary)/Strateg | M | 不要/確認のみ | - / UD-06 |
| 6-02 | KP選定LLM出力契約(Source Reference Contract、候補 | M | 不要/確認のみ | UD-06の結論 / UD-06 |
| 6-04 | KP音声構造(共通骨格: 英語Phrase→中間→英語Phrase) | M | 不要/確認のみ | OPEN-185 Z TTS/Assembly配線 / - |
| 6-06 | Standard Key Phrase日本語意味へのJ3適用 | M | 要(Z用音声Trial) | OPEN-185 Z TTS/Assembly配線 / UD-04 |
| 7-01 | TTS backend: speech_metadata_flash_lite  | M | 要(Z用音声Trial) | OPEN-185 Z TTS/Assembly配線 / UD-04 |
| 7-03 | Role Style 現行: JA=J3 / EN=E2 | M | 要(Z用音声Trial) | OPEN-185 Z TTS/Assembly配線 / UD-04,UD-05 |
| 7-04 | 新Tone: J2(JA明るく親しみやすい)/E2(EN upbeat、Prev | M | 要(Z用音声Trial) | OPEN-185 Z TTS/Assembly配線; X側Tone配線・E2E完了 / UD-07 |
| 7-05 | 新Tone: Full Story F1.5 | M | 要(Z用音声Trial) | X側Tone配線・E2E完了 / UD-07 |
| 7-06 | 固定フレーズChampion(10 phrase) | M | 要(Z用音声Trial) | OPEN-185 Z TTS/Assembly配線 / UD-10 |
| 7-07 | 音量・ヘッドルーム(RMS正規化+最終段安全弁) | M | 不要/確認のみ | OPEN-185 Z TTS/Assembly配線 / - |
| 8-04 | A2 Reading Resolver(OPEN-111) | M | 不要/確認のみ | OPEN-185 Z TTS/Assembly配線 / - |
| 8-05 | Pronunciation Ledger(ASR側配線のみ) | M | 不要/確認のみ | OPEN-185 Z TTS/Assembly配線 / - |
| 8-07 | SCG(Secondary Confirm Gate、日本語) | M | 要(Z用音声Trial) | OPEN-185 Z TTS/Assembly配線; SCGのSSOT反映 / UD-09 |
| 10-02 | fallback(minimal instruction / EN fallba | M | 要(Z用音声Trial) | OPEN-185 Z TTS/Assembly配線 / - |
| 10-04 | regenerate-stage(runner別) | M | 不要/確認のみ | - / - |
| 10-05 | resume(既存成果物の再利用) | M | 不要/確認のみ | - / - |
| 11-02 | Master Audio Store(固定phrase・KP phrase re | M | 不要/確認のみ | OPEN-185 Z TTS/Assembly配線 / - |
| 11-03 | 試聴・配布経路(GitHub Pages user_test) | M | 不要/確認のみ | OPEN-185 Z TTS/Assembly配線 / - |

### P2(効率化・保守性)

| item | 内容 | 備考 |
|---|---|---|
| 3-07 | Prompt sha・verbatim固定 | 未確認/E: Z promptはer026内定数。sha/verbatim固定の有無を未確認 |
| 3-08 | 生成段階の禁止記号予防 OPEN-261 | なし/E: X OPEN-261(未承認)。TTS入力全般に波及し得るため、X側結論後にZ要否を再評価 |
| 3-09 | 記号QAが句読点重複『、。』を検出しない OPEN-262 | なし/E: X OPEN-262(未承認)。記号QA共通部の穴。X側結論後にZ要否を再評価 |
| 7-08 | TTS Batch/Standard同期の実行方式 | 未確認/E: TTS実行方式(Batch/同期)の管理は運用側。Z runnerの実行方式は未確認 |
| 8-06 | TTS Pronunciation Hint(style/metaへの発音ヒント注入) | なし/E: X側もNOT_WIRED_FOUNDATION(配線見送り)。Zの人物名読みTTS反映要否はX側判断後 |
| 8-12 | 未承認候補: OPEN-257/259/260 | なし/E: X側OPEN-257/259/260(未承認)。X結論後にZ要否を再評価 |
| 9-01 | Risk Flagger 4条件(non-blocking) | 未確認/C: Risk FlaggerはX(英語記事Fact)向け。ZはSeed原文で事実誤り型リスクが低い可能性があるがZ適用有無は |
| 9-02 | RFの非Blocking契約・例外・状態 | 未確認/C: RF非Blocking契約はX(英語記事Fact)向け。ZはSeed原文で事実誤り型リスクが低い可能性があるがZ適用有無 |
| 9-03 | Review Queue(post_en) | 未確認/C: Review QueueはX(英語記事Fact)向け。ZはSeed原文で事実誤り型リスクが低い可能性があるがZ適用有無は |
| 9-04 | TTS前3者照合guard(ensure_rf_record) | 未確認/C: TTS前3者照合guardはX(英語記事Fact)向け。ZはSeed原文で事実誤り型リスクが低い可能性があるがZ適用有無 |

## 5. ユーザー判断事項(重要度順、推奨は提案)

### UD-01 Z Production配線(TTS/Assembly、OPEN-185)の着手と横展開の順序
- 選択肢: (a) まずZ TTS/Assemblyを既承認仕様のまま最小配線し、その後に横展開を段階適用 / (b) 横展開仕様を先に決めてZ配線と同時実装 / (c) Z配線自体を保留
- 推奨案: (a)
- 推奨理由: P0 12件中11件がZ TTS配線を前提とし、仕様未決のまま同時実装すると手戻りが大きい。Z Phase A設計の一回限りE2E見積は約30-40円(Guardrail案60円)
- 影響: Q: Z音声品質Gateの有無を決める / C: 一回限り約30-40円(Phase A §5見積、本書は実行せず) / D: Z量産開始時期を左右 / Safety: Gate無し配線は不可
- 依存: なし(最上流)

### UD-02 Z Production Writer(Story圧縮)・Seed選定・記号QAを今回の対象に含めるか
- 選択肢: (a) Writer/Seed選定を別管理IDで先に仕様化 / (b) 当面はMelos1本(Trial story.md入力)のままZ配線のみ進め量産は後回し / (c) AI創作へ戻す(非推奨: 標準方式にしないと2026-09-26決定済み)
- 推奨案: (b)→(a)
- 推奨理由: Melosは既存Trial story.mdを入力にでき、Z配線(UD-01)の検証には足りる。量産にはWriter+記号QA(CURRENT_SPEC L2126必須)とSeed選定プロセスが要る。新規テーマ選定はPM_GOVERNANCE 13節でユーザー選択
- 影響: Q: Story圧縮品質 / C: Writer実装後に別途見積 / D: Melos以外のStory量産可否 / Safety: 記号QA必須
- 依存: UD-01

### UD-03 Z記事構造: Phase A設計(3分割body1/2/3+Comment1-4、Comment4はZ所有新prompt)の採否
- 選択肢: (a) Phase A案採用(境界(6,7)、Dialogue clipを跨がない) / (b) 現行Z構造(Comment1のみ・本文1塊+8 clip)のまま / (c) 別境界でTrial
- 推奨案: (a)をZ固有境界で条件付き採用(Xの50/25/25は移植しない)
- 推奨理由: Xと聴取体験を揃える価値はあるが、Zは原作忠実・短尺(約280-420語)でXと文量が異なる。Comment4は新promptのためTrial要
- 影響: Q: 体験の統一 / C: Comment+1 call(約+3円/記事、Phase A概算) / D: Comment2-4実装+Trial / Safety: 低
- 依存: UD-01

### UD-04 Role Style(J3/E2)+Flash-Lite TTS backendのZ適用と既定backend
- 選択肢: (a) Zもspeech_metadata_flash_lite+J3/E2へ(Preview/Comment=J3、Full Story/In One Line=E2) / (b) Zは従来TTS経路を維持 / (c) 一部segmentのみ
- 推奨案: (a)をTrial後に
- 推奨理由: Z Dialogue多声clipでの効果は未検証。共有module適用でXと品質基準を揃えられるが、backend既定は未決でZ専用Trial(音声)が必要。Role Style『E2』とTone『E2_UPBEAT』は別物(管理ID付きで区別)
- 影響: Q: 音声表現 / C: Flash-Lite=1 segment約0.86円級(Phase A参照値)、Trial費用は別途見積 / D: UD-05と連動 / Safety: backend差し替えはASR Gate再検証要
- 依存: UD-01, UD-05

### UD-05 共有resolve_narrative_role()の拡張(Zの8 voice-clipをConnected Speech/Role対象にする)
- 選択肢: (a) Z segment_id向け正規表現を共有moduleに追加 / (b) Z専用resolverを別実装(共有を触らない) / (c) 拡張せずZはConnected Speech対象外を許容
- 推奨案: (b)または(a)をregressionつきで
- 推奨理由: 共有module変更は他Family(X/Y)への影響を伴う。Zの8 voice-clipがConnected Speech対象外のまま(known_gap)だと、Xと自然さ品質が乖離する
- 影響: Q: 音声自然さ / C: S-M規模、有料runtime小 / D: 他Family回帰テスト要 / Safety: 共有module誤変更リスク(影響範囲明示要)
- 依存: UD-01

### UD-06 Key Phrase DB HybridのZ採用 vs Strategy L維持(意図的差異として記録)
- 選択肢: (a) Z Strategy L維持を意図的差異として決定・記録 / (b) Core v2でZ再Trialし採否判断 / (c) 即採用(非推奨: Melos1本で『不十分』)
- 推奨案: (a)を当面、(b)は4+1 runner統合後
- 推奨理由: ZのTrialは不十分で採用根拠が無い。Source Reference Contract(共通Core)は配線不要。4+1統合(P0)を先に済ませて安定させる
- 影響: Q: KP選定精度 / C: DB Hybrid追加は再Trial有料 / D: 後回し可 / Safety: 候補ID方式必須(N2)
- 依存: なし

### UD-07 Tone J2(JA)/E2_UPBEAT(EN Preview・Comment)/F1.5(Full Story)のZ適用
- 選択肢: (a) X側Production配線・有料E2E完了を待ち、その結果を見てZ適用を再判断 / (b) 並行してZ向けTone Trial / (c) Z適用しない
- 推奨案: (a)
- 推奨理由: J2/E2_UPBEAT/F1.5はAPPROVED_FOR_PRODUCTIONだがX Coffee記事向け。X側は未配線(SSOT未記録、main未merge)で、Zへの承認ではない。X配線の前提をZ展開の完了済み前提にしてはならない(元指示5)
- 影響: Q: 声のトーン / C: Trialは有料(Z用は見積未取得) / D: X完了待ち / Safety: version guard bump等でX側と衝突しない順序管理
- 依存: X側Tone配線・E2E完了, UD-04

### UD-08 Zの音声速度(A2 6%減速、Aoede/Dialogue声へ適用するか)
- 選択肢: (a) A2 6%減速をZにも適用 / (b) Z固有の速度決定を別途Trial / (c) 減速なし
- 推奨案: (b)
- 推奨理由: Zの速度は『Melos音声style/速度のZ固有決定は未確認』。X/Aと同じ6%をDialogueに機械適用すると物語の間合いを損なう懸念(Z固有価値)
- 影響: Q: 聴取速度 / C: 小(Trial 1回) / D: Z TTS後 / Safety: 低
- 依存: UD-01

### UD-09 日本語ASR/SCG(OPEN-258)のZ適用範囲(Z JA segment=Preview/Comment1)
- 選択肢: (a) 共有module経由でZ JA segmentにも適用 / (b) Zは英語ASRのみ(JAは対象外) / (c) JAもZ TTS配線時にTrial
- 推奨案: (a)
- 推奨理由: SCG実装はmain merge済みだがSSOT未反映。ZのJAは少量で追加費用は小さい見込み。SSOT反映後に最終確認
- 影響: Q: JA読み誤り防止 / C: SCG追加ASR費用はJA量依存で小 / D: 小 / Safety: 誤読防止
- 依存: UD-01, SCGのSSOT反映

### UD-10 固定phrase num_three/num_fiveのChampion値(CURRENT_SPECは『未確定』、委任文はB take1)
- 選択肢: (a) 継続Trial(TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01)の結論を待つ / (b) B take1を暫定採用 / (c) Zでは番号phraseを使わない
- 推奨案: (a)
- 推奨理由: SSOT未確定のものをZで先に固定するとXと二重基準になる。他固定phrase(welcome等)は決定済み
- 影響: Q: 固定phrase一貫性 / C: なし / D: 低 / Safety: 低
- 依存: UD-01

### UD-11 Risk Flagger/Review QueueのZ適用
- 選択肢: (a) Zは適用しない(Seed原文のため)を意図的差異として記録 / (b) Z用criteria(原作乖離・名前表記)で再設計 / (c) そのまま適用
- 推奨案: (a)
- 推奨理由: RFはX英語記事のFact誤り検出向け。Zは原文が正でFact Ledgerが無く、移植は価値が低くZ固有の価値(原作忠実)に合わない。ただしZ用の原作乖離チェックは別途要検討
- 影響: Q: 低リスクで安定 / C: (b)はTrial有料 / D: 後回し可 / Safety: 非Blocking
- 依存: なし

### UD-12 難易度A2限定(Advanced/B1Bを作らない)を意図的差異として明示決定するか
- 選択肢: (a) A2限定を正式に記録 / (b) B1B版もZで検討
- 推奨案: (a)
- 推奨理由: Zには現状A2しか無く決定記録が無い(未整備)。決めないとAdvanced KP解説等の横展開判断が曖昧になる
- 影響: Q: 低 / C: なし / D: 低 / Safety: 低
- 依存: なし

### UD-13 Opus L2(Phase A §6、実装後1回)の実施
- 選択肢: (a) Z配線実装後にPM_GOVERNANCE 11-3に従って実施 / (b) 省略
- 推奨案: (a)
- 推奨理由: Z配線は新しい構造・処理フロー(条件A該当)。必須Opusレビューはユーザー承認Gateではないが、費用がかかるため実施タイミングの共有のみ
- 影響: Q: 高 / C: Opus 1回分 / D: 小 / Safety: 高
- 依存: UD-01実装後

## 6. 未確認事項(推測で埋めない)

X一覧15件+Z側8件=計23件。

| id | 内容 | 確認方法(Grep対象) | 担当 |
|---|---|---|---|
| X-U01 | FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01の進捗(SSOT/委任ログに記録なし。branch feature/coffee-new-tone-01に24acf9f4=Style配線commit 1件を確認) | git log main..origin/feature/coffee-new-tone-01、docs/pm/delegation_log Grep | Fable/Sonnet |
| X-U02 | J2/E2/F1.5のAPPROVED_FOR_PRODUCTION決定文のSSOT記録(DECISION_LOGはTrial記録止まり) | DECISION_LOG.md Grep『J2』『F1.5』、ユーザー逐語確認 | Fable(SSOT更新) |
| X-U03 | SCGのSSOT反映(main merge済み382c56c5、CURRENT_SPEC/DECISION_LOGに『SCG』0件、OPEN-258行は旧Status) | OPEN_ITEMS.md OPEN-258行・CURRENT_SPEC Grep | 別agent(Closeout)/Fable |
| X-U04 | TTS Pronunciation Hintが現在もProduction未配線か | Grep augment_style_prefix_with_pronunciation | Sonnet |
| X-U05 | X audio runnerのTTS実行方式(Standard同期かBatchか) | er019_family_x_audio_production_runner_01.py Grep | Sonnet |
| X-U06 | Standard(A2)側の全segment voice名明細 | audio runner plan出力・er019 Grep | Sonnet |
| X-U07 | voice切替fallbackの仕様・実装(minimal instruction fallbackは確認済) | Grep fallback voice | Sonnet |
| X-U08 | SFX行(Intro/Notification)の現行構造上の役割(SE-1との関係) | CURRENT_SPEC SE-1 Grep | Sonnet |
| X-U09 | Section Segmentation Contract(5-07)の途中Heading廃止後の有効性 | CURRENT_SPEC 5-07関連Grep | Sonnet |
| X-U10 | Production parse_ledgerとTrial側FIX01の実装同一性 | er053/er019 parse_ledger差分比較 | Sonnet |
| X-U11 | OPEN-243/235/236/238/239/246/250の最新Close状況 | OPEN_ITEMS.md各行Status Grep | Sonnet(read-only) |
| X-U12 | E案1記事セット費用(約63.5円)のSSOT記載有無 | COST_PER_ARTICLE_SET_E_VS_A_01.md/CURRENT_SPEC Grep | Sonnet |
| X-U13 | CURRENT_SPEC L1971『gpt-5.6-luna』表記とWRITER_MODEL=gpt-6-lunaの整合更新 | CURRENT_SPEC L1971周辺・routing Grep | Fable(SSOT) |
| X-U14 | Family Zにおける共有componentの利用状況(委任_02で一部解消: 上記Z列参照) | er026 import Grep | 解消済(Z一覧参照) |
| X-U15 | KP 4+1構成(6-03)のGate3判定の行内明示 | CURRENT_SPEC 4+1行・設計書Grep | Sonnet |
| Z-U01 | 難易度A2限定の意図的決定記録/B1B方針(=UD-12) | DECISION_LOG Grep『Family Z』『A2』 | Fable/ユーザー |
| Z-U02 | Risk Flagger・B3 annotation・Research系のZ適用有無 | er026 Grep er053 import(0件なら未適用) | Sonnet |
| Z-U03 | Z試聴ページ生成経路、量産cadence、Z記事あたりコスト基準 | er026・docs/pm/design_family_z... §5-B・REPORT_LEDGER Grep | Sonnet/Fable |
| Z-U04 | Phase A設計(55cb58ed)のユーザー承認有無とPhase B以降の計画 | DECISION_LOG/OPEN_ITEMS Grep『55cb58ed』『FAMILY-Z-MELOS』(Z一覧はエントリ無しと確認済) | Fable |
| Z-U05 | Z runnerのresume機構(コード全読は未実施) | er026 Grep resume/--stage | Sonnet |
| Z-U06 | Zでの英語ASR意味等価性・Secondary ASR適用 | er026 stage_tts設計・er006/er021 Grep | Sonnet |
| Z-U07 | Zの日本語セグメント(Preview/Comment)のA2 Reading Resolver・記号QA適用 | er026 Grep resolver/normalize | Sonnet |
| Z-U08 | Melos音声style/速度のZ固有決定 | CURRENT_SPEC Family Z 7項・Phase A §3 Grep | Sonnet |

## 7. 既存Open Item・進行中作業との関係

- OPEN-185(Z配線、PRODUCTION_WIRED未達)=本書の最大前提。OPEN-202/211(Z拡大時再判断)・OPEN-241(routing、Z反映済み)
- approved-but-unwired: J2/E2_UPBEAT/F1.5(X Coffee E2E、user判断待ち)。SCG=main merge済み・SSOT反映待ち(別agent進行)。Z展開はこれらの完了を前提にしない
- 重複開発・仕様競合の注意: Role Style『E2』とTone『E2_UPBEAT』の名称衝突、Zへの共有module変更(resolve_narrative_role)は他Family影響、Phase A設計(55cb58ed)とSSOT未反映状態の整合
- 新共通仕様名は作成していない(Dangling Reference対象なし)

## 8. 元指示との差異・満たせなかった点

- A/D分類のP付与: 元指示に定義なし(『-』、Fable判断要)
- 元指示③『各候補に必要Trial』: P1は推定(Z用音声Trialの要否のみ)。精密なTrial計画は未作成(未定義)
- 各項目の『X正式仕様とStatus』は X_INVENTORY_01参照(本書は要約のみ)。『横展開時の具体変更点・リスク』は根拠欄とUD欄に要約し、項目別詳細は未展開
- 元指示⑥『現状サマリ(非エンジニア向け)』は Z_INVENTORY_01 §0・本書§0を参照(再執筆なし)
