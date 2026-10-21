# PLAN_SUMMARY_01(v3 Fix): 固有名詞発音供給#133 ＋ 1語⇔複数語の同音救済 改善計画

管理ID: PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_03(2026-10-22) / **Status管理ラベル: `PLAN_FIXED_WAITING_ASR_SELECTION`**(計画Fix済み・Trial未実行・Production無変更・API 0・JPY0。ユーザーが承認したのは『計画v2の基本方針とTrial計画』であり、VALIDATED / APPROVED_FOR_PRODUCTION / PRODUCTION_WIREDではない。案Aの**Production採用は未承認**)。ユーザー原文の出典=`docs/pm/delegation_log/2026-10-22_PNMH-PLAN-FIX-AND-ASR-PASS-CONDITION-AUDIT-01_USER.md`(§2・§5・§6A。B側workerが保存)。


## Scope台帳(2026-10-22 委任_06追記、ユーザー§4再発防止)
**更新**: L1は2026-10-22にユーザーが`APPROVED_FOR_PRODUCTION`と正式採用(Status=APPROVED_FOR_PRODUCTION_WIRING_IN_PROGRESS、PRODUCTION_WIREDではない)。設計=`IMPLEMENTATION_DESIGN_01.md`。

| 課題 | Status | 担当工程 | 次の判断点 |
|---|---|---|---|
| L1 多語同音判定層 | 採用・配線中(A-1完了) | Sonnet(A-2)/Opus条件A/Cレビュー/Fable | Opusレビュー結果、X/Z別PRODUCTION_WIRED判定 |
| L2 固有名詞発音取得(UDR #133本体) | 計画策定中(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02) | 別agent B-1->Fable独立レビュー | ユーザー提出後の採否。Trial/実装は未承認 |
| KP両方PASS条件 | OPEN-440ユーザー回答待ち(未承認) | Fable(回答待ち) | ユーザー回答。本配線では不実装 |
| U5 既存の穴(AI->eye等) | ユーザー未回答 | Fable | 是正可否 |
| J7 公式日本語読み | ユーザー未回答 | Fable | 英語期待発音の根拠にしてよいか |
| GitHub Issue #133本文 | 取得不能(404)・未確認 | Fable | 取得手段/不要判断 |

## v3-1. 反映したユーザー判断(2026-10-22、原文に基づく範囲のみ)
| 判断(原文の要旨) | 計画への反映 |
|---|---|
| 計画v2の基本方針を承認 | Trial計画として案Aを採用(Production採用ではない) |
| 『ByUs ⇔ buy us / by us のように発音が同じなら、単語数・綴り・辞書上のストレス記号の違いでNGにしない』『ストレス記号を無視した音素列比較をTrial計画に採用』 | U2=採用(Trial計画)。ストレス無視・1語⇔連続2〜3語の音素列連結比較(CURRENT_SPEC:1839の拡張はTrialで検証する新仕様) |
| 『音素が異なる実際の誤発音はNG』『既存の誤PASS防止条件を維持』 | 近音/脱落/追加/OOV/数値否定/文字読み/略語ガードを全て維持(ケースN1〜N15・PH1・PH2、unit test 20件で固定) |
| 『`Bi-us`型は現行仕様に従いNG維持』 | U-BI=NG維持(CURRENT_SPEC:454整合)。V8ガード(2字tokenは閉じた機能語集合のみ)をTrial仕様に採用。ケースBI1/BI2=期待NOT_PASS |
| 『対象は原則全語、固有名詞らしい語は代表発音限定などv2の安全条件を維持』 | U1=全語+entity_likeは代表発音のみ。G5・V8・隣接spanのみ・辞書外=判定不能・数値/否定ガード先行を維持 |
| #133: 『辞書外・未解決の実際の不一致が発生した場合に調査する方式を継続検討』『全固有名詞を毎回調査する高コスト方式は採用しない』『CMU辞書に同綴りの別人名があることだけで公式発音が確定したと判断しない』『#133の既存Statusを維持し未承認事項を正式採用しない』 | L2縮小案(反応的調査)は**継続検討の候補**であり採用ではない。#133のStatus(UDR #133未回答)は変更しない。byUsの英語発音は**未確定**(下記リスク) |
| Trial: 『現在のASR比較結果を待つ』『新Primary/Secondary確定後に実施』『費用上限案50円』『現時点では実行・Production採用・配線は行わない』『無料の準備は先行可』 | U7=ASR確定後に実施する計画、Cap案JPY50。Trial実行はしない。無料準備(ケース表・unit test)を実施済み(v3-4) |

## v3-2. 残る未決事項(判断候補。ラベルはFable付与)
- **U5 既存の穴**(`AI→eye`・`us→u s`・`am→a m`・`Tse→sea`[現行でPASS]): 原文は『既存の誤PASS防止条件を維持する』とのみで、**是正可否には回答なし**。計画は『悪化させない』のみ(ケースEX1〜EX3・H1=KEEP)。是正は別判断事項として残す。
- **J7**: 権利者の公式日本語読み『バイアス』を英語の期待発音の根拠にしてよいか(未回答)。
- **GitHub Issue #133本文**: 取得不能(404)のまま未確認。
- **#133(UDR #133)のア/イ/ウ**: 未回答のまま(L2は別計画)。#134(Perplexity枠切れ)も未回答。
- **Trial Cap JPY50の最終確定**: 原文は『費用上限案は50円』。計画値としてCap JPY50で記載するが、実行直前の承認形態(7-7: 新仕様Trialは金額によらず承認)はFableが確認する。
- **リスク(byUsの英語発音は未確定)**: 現行の`Bias`救済は、CMU辞書に姓等として`byus`が収録され`bias`と同じ`B AY1 AH0 S`であることに依存しており、ブランド`byUs`の公式発音の確認ではない。案Aの`buy us`救済も同じ綴り辞書基盤に乗る。『CMU辞書に同綴りの別人名があることだけで公式発音が確定したとは判断しない』(ユーザー原文)に従い、byUsの英語発音は未確定とし、実際の発音が`bias`系でないと判明した場合は救済の根拠が変わる(Trial結果の解釈に反映)。

## v3-3. Trial実行条件(実施しない。ASR確定後の手順)
- **トリガー**: ASR 3方式比較(OPEN-438・UDR #136)に基づき、ユーザーが新Primary/Secondaryを確定して通知した時点(自動移行しない。確定前に有料APIを使わない)。
- **内容(P1)**: 構成音声**13本**(正例/近音/脱落/文字読み/`bi-us`型)のTTS生成+新Primary/Secondaryで再ASR、run_byus_01等の**既存wav約5本の再ASR**(TTS 0円)、層A(ASR生認識)・層B(救済)・層C(最終判定)を分離して集計。
- **費用**: 見積**約18〜28円**、**Cap案JPY50**(日次1,000円内)。上限のステータスはVALIDATED、Production採用は人間ユーザーのみ。
- **ASR確定時に差し替える条件チェックリスト**: `TRIAL_PLAN_01.md` §8(v2既存の7項目+再評価6点)をそのまま使用。v3追加の合格条件: Bi-us型(BI1/BI2/実音声`bi-us`)は層CでPASS 0、音素相違の実音声負例は誤PASS 0、ストレス差のみの正例は救済100%。
- 無料の先行分(O1): unit test(実施済)・目視レビュー用リスト(v2作成済)。

## v3-4. 無料先行準備の結果(API 0・JPY0)
- `test_proto_multiword_span_v3_01.py`: **20件PASS**(span 15件+文単位in-memory 5件、Production経路無変更・ファイル出力なし)。結果=`test_proto_multiword_span_v3_01_result.txt`。
- `TRIAL_CASES_01.json`: 30→**41件**(v2計画書にのみあったBI1/BI2/NX1/CS1-3/RS1/H1と、v3のBI3/PH1/PH2を追加)。v3方針での判定(`after_v3`)で**全41件が期待どおり**(NX1は『要審査』で、v2事前測定どおり`HOMOPHONE_MATCH_NUMBER_EXCEPTION`のPASS=目視審査項目として維持)。結果=`update_cases_v3_01_result.txt`。
- O0再適用(4,032ペア)は前提不変: `measure_v2_01.py`を再実行し`measure_v2_result_01.json`が保存済みと**バイト一致**(git差分0)。変化4ペア(`byus→buy us`)・PASS→NG 0。
- 既知の残存: `bias`⇔`by us`(機能語`by`)は音素が同一のため救済される(BI3)。区切って読まれた場合との区別は音素列だけでは不可。Trial層Cで要審査(DESIGN_OPTIONS §4-3)。

---
# 以下はv2本文(2026-10-21。履歴として保持。上のv3 Fixが優先)

# PLAN_SUMMARY_01(v2): 固有名詞発音供給#133 ＋ 1語⇔複数語の同音救済 改善計画(ユーザー指示§7の1〜11の順)

管理ID: PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_02 / Status管理ラベル: `PLAN_V2_PENDING_USER_FIX`(計画のみ・API 0・JPY0・Trial未実行・Production無変更。VALIDATED/APPROVED_FOR_PRODUCTIONではない)。詳細は同dirの`DESIGN_OPTIONS_01.md`/`TRIAL_PLAN_01.md`/`INVESTIGATION_01.md`/`REVIEW_QUESTIONS_01.md`。

## 1. 結論: 推奨する改善方式と理由
- 推奨=案A: ASR転写とcanonicalの**隣接した差分span**(片側1語/他方2〜3語)の音素列を連結して比較し、同じ音なら既存の同音(`HOMOPHONE_EQUIVALENT`)経路へ載せる。ストレス記号は無視、脱落/追加/辞書外/数値・否定/短い略語は救済しない、canonicalが固有名詞らしい語なら代表発音のみで比較する。
- 下流のコード(Secondary/retry/Human Review/M1等)は無改変、Family X/Z/Y共通、実行時API 0。
- 理由: byUs型の「正しい発音をNGにする」偽NGを1か所の純関数で消せ、新規の誤PASSは0(4,032ペア・ラベル付き544転写)。価値は**予防**(保存データ上は4,032ペア中4=0.10%、全て1記事由来)なので、計画・Trialは必要最小限に縮小した。

## 2. #133の現状と今回の改善との統合方針
- #133(リポジトリ内=UDR #133、OPEN-434)は**未回答**(ア/イ/ウ)。GitHub Issue #133本文は取得不能(404)のため**未確認**。
- 「判定(L1)」と「発音の供給(L2)」を別問題に分離。L1(案A)は#133を待たずに進められ、**(イ)現状維持＋案A追加**を推奨。
- L2(発音供給の反応的調査・negative cache等=旧B2)は**#133判断後の別計画**に分離(今回のFixに含めない)。

## 3. ByUsの正しい発音をどう取得・確定するか
- **AI単独では確定しない**。英語の公式発音は確認できず(PNEP K1)、権利者の公式日本語読み「バイアス」を根拠にしてよいかは**J7(未回答)**。
- 案Aは既存の1語⇔1語救済と同じ土台(CMU辞書の綴り発音: `byus`=`B AY1 AH0 S`=`bias`)に乗るだけで、公式発音の確認ではない。この限界を全文書に明記した。
- J7=認める→その読みを期待発音として確定、認めない→UNCONFIRMEDのまま(案Aの成立には影響しない)。

## 4. 1語⇔複数語をどう判定するか(具体例)
- `byUs`→`buy us`: 救済(音素`B AY AH S`が一致。**ストレス無視が必要**)。`byUs`→`by us`: 既存の空白差規則で救済済み。`onto`→`on to`、`already`→`all ready`: 救済。
- `byUs`→`bios`/`buys`/`bus`/`buy`(脱落)/`buy us an`(追加): 救済しない。`Melos`→`Mellow s`: 辞書外のため救済しない。`AI phone`→`iPhone`: 略語ガードで救済しない。
- `bias`→`Bi-us`(音節区切り): 案Aのままだと救済されCURRENT_SPEC:454(「Bi-usは引き続きNG」)と衝突。**ユーザー判断(U-BI)**。

## 5. 誤PASSをどう防止するか
- 音素列の完全一致のみ(近音・1音素差は不合格)。生token列で脱落/追加を検出、辞書外・variant過多は判定不能=救済しない、数値・否定ガードを先行、canonical側3字以上、1文字token禁止、離れた語は結合しない。
- 固有名詞らしい語は代表発音のみ(固有名詞に「代表発音のみ」とした既存の方針を多語spanでも守る)。
- 実測: 4,032ペアで判定が変わるのはbyUsの4ペアのみ、PASS→NG 0、新規誤PASS 0。判定挙動の変化4点(数字ゲート例外/M1矛盾拒否/connected-speech迂回/F1残差)は実測してテストに固定する。

## 6. 比較した代替案と採否理由
- 採=案A。不採=D(ASR同士の一致は発音確認ではない=承認済み仕様に反する)、E(Aの劣化版・証跡喪失)、F/G(綴り近似・名前別リスト)、H(LLM判定: 非決定・毎回費用)、I(音声直接の音素比較: 新規モデル・STOP実績)、B1/B3(原価悪化・誤発音隠蔽)、J(偽NGが残る=比較基準)。
- B2(発音供給の縮小版)は別計画、C(Writer併記)は保険(Writer原則の変更が要るため採らない)。

## 7. Fableの評価・指摘・反映結果
- Opus独立レビュー13件(OF-PNMH-R-01〜13、高2・中4・低7)を全て反映または調査(台帳に処置登録)。主な反映: (1)ストレス無視は既存1:1より緩い新仕様と明示、(2)`Bi-us`衝突と対策案の副作用計測、(3)固有名詞は代表発音限定、(4)判定挙動の変化4点を明記、(5)再適用対象を4,032ペアへ拡張、(6)有料Trialを48→13本に縮小。
- R-10(仕様1839の『Secondary要求』とコードの『Primary単独PASS』)は調査の結果**仕様文言とコードの不一致**(判定はFable)。新ルールは上乗せしない。

## 8. Trial計画と合格基準
- ケース表38件(合成30＋追加8、事前測定済み)、構成音声**13本**(正例/近音/脱落/文字読み/`bi-us`型)＋run_byus_01の既存wav約5本の再ASR(TTS 0円)。ASR生認識(層A)・救済(層B)・最終判定(層C)を分離。
- 合格: 正例の救済100%、新規誤PASS 0、PASS→NG 0、挙動変化4点が事前値どおり、実音声負例の誤PASS 0、費用Cap内、Production無変更。上限=VALIDATED(Production採用は人間ユーザーのみ)。

## 9. QCDへの影響(概算と不確実性)
- 量産単価: 実行時0円/記事、再試行削減は記事あたり0〜0.1円オーダーの微減(価値は予防)。B1相当(11〜16円/記事悪化)は採らない。
- 開発費: 有料Trial約**18〜28円**(Cap案JPY50、v1の約25〜40円/Cap100から縮小)。時間は数時間。納期: オフライン検証はASR確定を待たず先行可。
- 不確実性: 発生率は新Primary/Secondaryで変わる(保存データはAzureが主因)。再評価点6つをTRIAL_PLAN §8に明記。

## 10. 未解決事項・ユーザー判断が必要な事項(判断候補。ラベルはFable付与)
- **U2**: 案Aの採否(CURRENT_SPEC:1839の拡張。**ストレス無視・1語⇔複数語・3語まで**を含む)。推奨=採用方向でFix。
- **U-BI**: `Bi-us`型の合否ライン。推奨=不合格維持(CURRENT_SPEC:454整合、ガードV8)。
- **U1**: 適用範囲。推奨=全語に適用＋固有名詞らしい語は代表発音限定。
- **U7**: 有料Trialの実施とCap。推奨=ASR確定後にJPY50で承認を求める(新仕様のため金額によらず承認が必要)。
- **U5**: 既存の穴(AI→eye、us→u s、am→a m、Tse→sea[現行でPASS])を扱うか。推奨=今回は是正せず悪化させない。
- 未回答のまま進める確認: J7、UDR #133、#134(Perplexity枠切れ)、GitHub Issue #133本文。

## 11. ASR選定後に着手するTrialの準備状況
- 計画v2・再現script・測定json・ケース表・差替えチェックリスト(§8)は完成。**新Primary/Secondaryが未確定**(ASR 3方式比較のOPEN-438はユーザー判断UDR #136待ち)のため、有料Trialは開始しない。計画Fix後も自動移行しない。
- O1(unit test・目視レビュー用リスト)は計画Fix後にASR確定を待たず実施可。P1(有料)はASR確定＋ユーザー承認後。
