# REDETERMINATION_CHECK_01: 既決事項・是正済み事項の再確認(③ Secondary誤PASS対策・警告/試聴連動、④ 数値・否定の安全判定)

管理ID: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_07(2026-10-15、Read-only調査、費用JPY0、到達上限INVESTIGATION_COMPLETE)
実施内容: Grep/Readのみ。Trial・TTS/ASR API・test実行・仕様変更・SSOT編集は一切なし。

**調査の最重要結論(先に要約)**: ユーザーが「既に判断・是正した」と記憶している内容に近い**隣接する別件の決定・実装は実在する**(日本語SCG、否定保護、英語の数値Tier1表記差等価、警告ラベル、M1/F1など)。しかし、**統一フロー(10/12)の「③ 警告の試聴リスト連動」と「④ 数値S1の穴(日本語の漢数字、英語の`N%`値変更)」そのものを決定・是正した記録は、SSOT・Git・実装コードのいずれにも確認できなかった**。③④の中の「既に決定・実装済み」の部分は§0・§3で分離したので、それらは再質問不要。

## §0 冒頭表

| 項目 | 最終ユーザー決定 | 実装状況 | 残課題 |
|---|---|---|---|
| ③ Secondary誤PASS対策 | **日本語**: 2026-10-11 ユーザー正式承認(OPEN-258 SCG)=Secondary(Azure)単独のPASSは`EXACT_MATCH`/`NORMALIZED_MATCH`のみ。PHONETIC自動PASS・Whisper 2-of-3・Phrase Listなしは「採用しない」と明記。除外条件(数字差・否定差・固有名詞C1・類似度0.4未満・length NG・同形異音語C2)も承認。**英語**: 「Secondary PASS集合を日英で厳格集合に統一」は**決定記録なし**(10/12報告書D-3は未回答)。10/13の決定は別件(発音同等性の設計方針合意、OOV複数発音候補の承認)。 | **日本語=PRODUCTION_WIRED**(承認・実装・test75件PASS・実Azure/Primaryのruntime evidence・SSOT・merge `382c56c5`、10/12〜10/15の実run記録あり)。**英語**=既存Production(Tier3 corroboration等)は稼働中だが、統一フローの「厳格Secondary集合」は**未実装・未承認**。固有名詞のSecondary一致(S7)も統一フロー案のまま。 | (a)英語Secondary PASS集合(4ラベル/2ラベル)(D-3)、(b)固有名詞Secondary一致の扱い(D-11)。いずれも**ユーザー決定の記録なし**。 |
| ③ 警告・試聴連動 | **警告ラベル`PASS_WITH_WARNING`自体とaudit記録**は既存承認済み(Pattern C、Eq Layer 2026-09-07、M1 2026-10-13)。**「警告を最終試聴リストへ自動連動し、連動前は統一フローを有効化しない」(10/12 D-2)は決定記録なし**(UDR #18=未承認のまま)。 | ラベル付与とaudit/最終Artifact記録=**PRODUCTION_WIRED**(実run: `er011_output/attempt_history.jsonl` L12348/L12609/L13264にCONNECTED_SPEECH_PASS_WITH_WARNING、L13220にM1受理)。**警告を試聴リストへ自動で載せる処理は未実装**(本番コードにGrep該当0件)。 | 試聴リスト連動の実装と、導入前提にするか(D-2。推奨(a)実装先行、間に合わなければ(b)警告をNG扱い)。 |
| ④ 数値の安全判定 | **英語の数値Tier1等価(`20%`=`20 percent`等、Primary段)**: 2026-09-27ユーザー正式承認済み。**S1の穴の是正**(日本語の漢数字の値変更検出・英語`N%`値変更検出・表記差で正しい音声を落とさない): 10/12 D-4は**未回答**。10/13の日本語表記ゆれTrialも「採用判断なし」と明記。 | 英語=アラビア数字の不一致検出はPRODUCTION_WIRED。**ただし`25%`→`26%`型は検出の穴のまま**(`_is_number`=`tok.isdigit()`、コード変更なし)。日本語=`\d+`のみ(`er007_ja_asr_validator_01.py` L67)で**漢数字の値変更は検出せず、表記差(二/2等)は誤発火**もそのまま。日本語の値署名救済はTrial止まり(Production未配線、「VALIDATED」でもない)。 | 穴を是正するか・どの方式か(D-4、OPEN-287、JA-ASR判断1〜5=UDR #24)。**未是正であることが事実**。 |
| ④ 否定の安全判定 | **英語・日本語とも否定差はブロック**が正式仕様: 英語は既存承認(`protected_check`)、日本語は2026-10-11ユーザー承認(`protected_check_ja`+推奨4の否定マーカー ず/ません/ぬ/ざる/まい)。拡張(否定活用ギャップ等)は新規仕様候補として**保留**(D-19)。 | **PRODUCTION_WIRED**(英語: `er006_preprod_hardening_01_validation.py` L397/L673-676/L1072。日本語: `er007_ja_asr_validator_01.py` L263-266、`er007_ja_secondary_asr_01.py` L198-214)。Secondary転写にも同じ判定が適用。合成否定26/26ブロックはオフライン測定。 | 否定の**新規拡張**のみ未承認・保留。是正が必要な既存の穴は今回確認されず。 |

## §1 調査① Secondary誤PASS対策(5問)

### 「試聴連動」の定義(事実)
10/12報告書での「試聴連動」とは、`PASS_WITH_WARNING`(自動PASSするがASRでは確定できない型=固有名詞・最小対・表記差)を**最終試聴リスト(人間が耳で確認する一覧)へ自動で載せ、確認前に公開へ進めない**仕組みを指す(`er058_output/design/UNIFIED_FLOW_SPEC_V04.md` L145、L158-164)。既存のHuman Review queue(`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`)は「自動PASSできなかった音声」の行き先であり、`PASS_WITH_WARNING`は別物(PASS扱いで通る)。既存Productionでは警告は「audit/最終Artifactへ記録」まで(`CURRENT_SPEC.md` L2028)。

### Q1 Secondary PASSの自動採用条件は最終的に何と決まったか
- 日本語: `EXACT_MATCH`/`NORMALIZED_MATCH`のみ。2026-10-11ユーザー決定(`DECISION_LOG.md` L20567「V1方式=SCGをProduction採用…安全条件(PHONETIC_MATCH自動PASSなし・Whisper 2-of-3なし・Phrase Listなし…)」)。実装`er007_ja_secondary_asr_01.py` L83 `SCG_PASS_CLASSIFICATIONS`、判定L329-333。CURRENT_SPEC L2016(APPROVED_FOR_PRODUCTION、フラグ既定ON)。OPEN-258はCLOSED(PRODUCTION_WIRED 2026-10-11)(`OPEN_ITEMS.md` L760)。
- 英語: 統一フロー案「日英ともEXACT/NORMALIZEDのみ(U-3は(a)暫定)」(V04 L131)は**未承認**。選択肢(a)英語4/日本語2のまま (b)日英2+個別正規化 (c)日英4(`RECONCILIATION_FINAL_REPORT_01.md` D-3、推奨(b))は**未回答**。現行Productionの英語Secondaryは従来のCascade(`er006_secondary_asr_01.py`)(統一フロー案C-3が「緩い」と記述、V04 L219)。

### Q2 PASS_WITH_WARNINGと試聴連動は採用・実装済みか
- 警告ラベル: 採用・実装済み。英語Pattern C(`CONNECTED_SPEECH_PASS_WITH_WARNING`、`er006_preprod_hardening_01_validation.py` L1107/L1155、CURRENT_SPEC L2028)、Equivalence Layer D〜G(`..._EQUIVALENCE_PASS_WITH_WARNING`、CURRENT_SPEC L2029)、M1(`M1_MULTI_CANDIDATE_ACCEPT`、CURRENT_SPEC L2664-2670、2026-10-13承認、`er006_m1_multi_candidate_01.py` L15)。いずれも「blockingしないが警告をaudit/最終Artifactへ記録」。
- 試聴リストへの**自動連動**: 本番コードにGrep該当なし(`PASS_WITH_WARNING`を参照する非test・非Trialコードは検証器とM1のみ。リスト生成コードなし)。10/12のD-2(`RECONCILIATION_FINAL_REPORT_01.md` L152)/OPEN-286(`OPEN_ITEMS.md` L789、「これらが未充足の間は導入しない案」)は**未承認・未実装**。UDR #18(`docs/pm/USER_DECISION_REGISTER_01.md` L35)もUDR区分のまま。10/13の日本語表記ゆれTrialも「PASS_WITH_WARNING→最終試聴リスト(推奨)」としたが採用判断なし(`DECISION_LOG.md` L20771)。
- 分類: ラベル・記録=PRODUCTION_WIRED(個別承認機能)、自動連動=未承認・未実装。

### Q3 固有名詞・語尾脱落・同形異音などの危険ケースの扱い
| 型 | 決定済みの扱い(根拠) | 統一フロー案(未決) |
|---|---|---|
| 同形異音(日本語) | **C2を2026-10-11ユーザーが採用**、SCG対象から除外(`DECISION_LOG.md` L20567、`er007_ja_secondary_asr_01.py` L205-206)。V04 L109は「維持」 | 変更なし(維持案) |
| 固有名詞(日本語) | SCGはC1(entity_like等)で除外(CURRENT_SPEC L2016)。C1は「Fable採用・ユーザー個別承認の逐語なし」(V04 C-10) | C1廃止方向(D-10)、S7(Secondary一致でもPASS_WITH_WARNING+最終試聴)(D-11)=未回答 |
| 固有名詞(英語) | 既存: Tier3 corroboration(`SECONDARY_ASR_CORROBORATED_MATCH`、warning付き)、M1(2026-10-13承認、OOV複数発音候補、PASS_WITH_WARNING) | S7統一=未回答 |
| 語尾脱落(clip末尾欠損) | 決定なし。検出は別課題OPEN-341(USER_DECISION_REQUIRED、未実装)。ASRで区別不能(全ASRが原稿形で転写14/44本、`RECONCILIATION_FINAL_REPORT_01.md` L63) | 同左 |
| Pattern A/B/Cが最初の差分のみ判定 | F1(全差分点検)を2026-10-13ユーザー承認で実装(commit `7948bd78e`、`OPEN_ITEMS.md` L843)=WIRED_PENDING_RUNTIME_EVIDENCE | - |

### Q4 既存Validator・QA・Human Reviewのどこに反映されたか
- 日本語: `er007_ja_secondary_asr_01.py::evaluate_attempt_ja_with_cascade_detail`(Primary NG→SCG)。呼出元: `er003_v1_repro01_main_generate.py` L374、`er003_v1_n3_01_tts_generate.py` L651、`er003_v1_sing01_voice01_generate.py` L515/L563(`er053_output/open258_scg_production_wiring_01/CALLPATH_01.md`)。attempt消費なし、HR Lock/attempt上限/fallbackは不変(CURRENT_SPEC L2016)。
- 英語: `er006_secondary_asr_01.py::evaluate_attempt_with_cascade(_detail)`。呼出元: `er003_v1_crosslevel_audio_02_common.py` L348、`er003_v1_repro01_main_generate.py` L349、`er003_v1_sing01_news_tail_fix.py` L202、`er003_v1_sing01_point_headings_aoede.py` L126、`er003_v1_sing01_voice01_generate.py` L238、`er003_v1_n3_01_tts_generate.py` L146。
- Human Review: 不変(HR Lock・`record_human_approval`)。警告→試聴の新規連動はなし。

### Q5 実際のProduction正式経路で発火した証拠
- 日本語SCG: `er011_output/attempt_history.jsonl` L12583(2026-10-12 16:58、run_p8_wiring_01 a2 meaning_2、language=ja、`SECONDARY_CONFIRMED_PRIMARY_FALSE_NG`、1件)。導入時のruntime evidence: `er053_output/open258_scg_production_wiring_01/RUNTIME_EVIDENCE_02.md`(META wavでPrimary「出現」→Azure「出演」→PASS、4回中2回)。
- 英語警告: 同ファイル L12348(2026-10-12 full_story_part1_c14)ほか計3件が`CONNECTED_SPEECH_PASS_WITH_WARNING`。M1: L13220(2026-10-15 17:13、full_story_part1_c5、M1_MULTI_CANDIDATE_ACCEPT 1件)。`SECONDARY_ASR_CORROBORATED_MATCH`は39件(attempt_history)/106件(`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`)。`ASR_VALIDATION_UNCERTAIN`は779件/2537件。HR queue内`ASR_VALIDATION_UNCERTAIN`は72行(`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`)。
- 直近の例(委任_04報告引用): part1_c5 "Melos said."→"Nello said."がASR_VALIDATION_UNCERTAIN(Lock)。
- 統一フロー(Secondary厳格集合、S7、試聴連動)の発火証拠: **なし**(未実装)。

## §2 調査② 数値・否定の安全判定(6問)

### Q1 日本語の漢数字・算用数字の値一致/不一致は是正済みか
**未是正(Production)**。`er007_ja_asr_validator_01.py` L67 `_DIGIT_RE=\d+`、L242-266 `protected_check_ja`はアラビア数字のみ比較。git log: 10/12以降に同ファイルの変更なし(`git log --since=2026-10-12`に該当commitなし)。V04 L113-124の実測表(三人→四人は発火せず、二人↔2人は発火)は現状のまま。Trial(`DECISION_LOG.md` L20760-20776、`er066_output/ja_asr_orthographic_equivalence_01/REPORT_02.md` L63-64): 値署名で表記差を救済・値違いは不許容、敵対的反例74件の誤PASS 0だが、Statusは「Trial…Production=未配線、runtime evidenceなし、救済の有効性=PRELIMINARY」。**採用判断なし**(OPEN-287追記、`OPEN_ITEMS.md` L790)。副次的な既存欠陥OPEN-334(`3〜5日`vs`35日`がNORMALIZED_MATCH、`OPEN_ITEMS.md` L837)も未修正。
Production実run上のJA数値ゲート発火例: `er011_output/attempt_history.jsonl` L12833(2026-10-13)・L13161(2026-10-15)に`number_mismatch:[('', '10')]`によるSCG不実行(計4件)。

### Q2 英語の`%`/`percent`等の表記差・値変更は是正済みか
- 表記差(`20%`=`20 percent`): **Primary段は是正済み(承認済み)**。2026-09-27 English ASR Semantic Equivalence Layer(Tier1 `NUMERIC_EQUIVALENCE_MATCH`、`CURRENT_SPEC.md` L2022、`er006_preprod_hardening_01_validation.py` L378-380)。実run: `NUMERIC_EQUIVALENCE_MATCH` 47件(`er011_output/attempt_history.jsonl`)。ただし統一フロー案でSecondary単独判定にすると、この表記差で偽NGになる(V04 L138、2/6)。
- 値変更(`25%`→`26%`): **未是正**。`_is_number(tok)=tok.isdigit()`(同ファイル L622-623)により`25xpercentx`は数値扱いにならず、`number_mismatches`に掛からない(V04 L113、合成15件中4件を見逃し)。10/12以降の同ファイル変更はF1のみ(`7948bd78e`)で、この穴には触れていない。

### Q3 英語・日本語の否定表現保護は何が正式仕様か
- 英語: `_NEGATION_WORDS`(L397)、`protected_check`が差分範囲の否定語の有無を比較(L673-676)、不一致なら`TRUE_CONTENT_MISMATCH`(L1072)。Tier1 early-exitも否定ブロック時は発動しない(L1255-1270)。合成否定26/26ブロック(V04 L112、オフライン測定)。
- 日本語: `protected_check_ja`が`safety._has_negation_ja`で比較(`er007_ja_asr_validator_01.py` L263-266)。加えて2026-10-11承認の推奨4(ず/ません/ぬ/ざる/まい、形態素解析、`er007_ja_secondary_asr_01.py` L109-117/L149-214、CURRENT_SPEC L2016(2))。
- 拡張(否定活用ギャップ、英語の否定マーカー補強)は**新規仕様候補・保留**(`RECONCILIATION_FINAL_REPORT_01.md` D-19、V04 L100)。

### Q4 Primary/Secondaryそれぞれの判定で適用されるか
| | Primary | Secondary |
|---|---|---|
| 英語 | `classify_asr_match`内`protected_check`(数字=アラビア数字のみ、否定語) | Secondary転写にも`val.classify_asr_match(...)`(`er006_secondary_asr_01.py` L762/L786/L842/L879/L917)=同じprotected_check |
| 日本語 | `classify_ja_asr_match`内`protected_check_ja` | SCG実行前にPrimaryの差分で数字差・否定差・否定マーカー差を除外(`_scg_exclusion_reason`、L188-214)。さらにSecondary転写を`classify_ja_asr_match`で再判定(L329、protected_check_ja適用) |

### Q5 初回・retry・fallback・再生成の全経路に配線されているか
- 判定関数は各attemptの検証で共通に呼ばれる(呼出元は§1 Q4)。`CALLPATH_01.md`はSCG4呼出元がPrimary NG後の経路(初回・retry・fallback)を網羅すると記録。英語Tier1/Tier3は「初回attempt・fallback・post-slowdown再検証・Local Rewrite回復の全経路」(CURRENT_SPEC L2022)。
- 減速後(A2英語6%)の再検証はPrimary+homophone中心で、Secondary cascadeは`ASR_VALIDATION_UNCERTAIN`時の`_post_slowdown_cascade_rescue()`のみ(CURRENT_SPEC L2022、2026-10-12是正)。protected_check自体はclassify内のため減速後にも適用されるが、この点を直接確認したtest記録は**未確認**。
- 日本語LRは未対応のため再生成=同一Prompt/標準経路のみ。
- 全経路の網羅を1本のtestで確認した記録: **未確認**。

### Q6 テスト結果・runtime evidenceは存在するか
- 日本語SCG(数字/否定除外含む): SCG関連75件PASS(`er007_ja_scg_test_01`31+`er007_ja_scg_c2_neg_test_01`17+Phase 0回帰)、2026-10-11(`DECISION_LOG.md` L20567)。runtime evidence `er053_output/open258_scg_production_wiring_01/`。
- 日本語Trial(表記ゆれ値署名): `er066_ja_asr_orthographic_equivalence_01_test_01.py` 18件+`_test_02.py` 31件=49件PASS(`DECISION_LOG.md` L20775付近)。Trialのため配線なし。
- 05A是正: `er058_asr_tts_prodfix_01_test_01.py` 27件PASS(`DECISION_LOG.md` L20581)(数値・否定とは別件)。
- 英語数値/否定: テスト`er006_preprod_hardening_01_validation_test.py`・`er007_en_blindspot_test_01.py`が存在。**最新実行記録は未確認(今回testは実行していない)**。
- 数値・否定の自然発火runtime evidence: 日本語数値は上記L12833等4件。英語の`number_mismatch`系記録ファイルは複数存在(`er014_output/.../tts_generation_results.json`等)が内容精査は**未確認**。

## §3 4区分への分類(完了/未完の切り分け)

| 対象 | 区分 | 完了部分 | 未完部分 |
|---|---|---|---|
| JA Secondary Confirm Gate(厳格集合・除外条件・C1/C2/推奨4) | **PRODUCTION_WIRED** | 承認(2026-10-11)・実装・test75件・runtime evidence・SSOT・Git(merge 382c56c5) | OPEN-263(同形異音辞書の穴)等の候補のみ |
| 警告ラベル(Pattern C/Eq Layer/M1)とaudit記録 | **PRODUCTION_WIRED**(M1は配線済み・隔離evidence取得済みだが`PRODUCTION_WIRED`未宣言、UDR #52) | 承認・実装・実run記録 | 警告の試聴リスト自動連動 |
| 警告→最終試聴リスト自動連動 | 統一フロー案(未承認・未実装)。区分は**USER_DECISION_REQUIRED**(D-2、決定記録なし) | - | 実装とruntime evidence、前提にするかの決定 |
| 英語Secondary厳格集合(日英統一)・S7 | **USER_DECISION_REQUIRED**(D-3/D-11、決定記録なし) | JA側は決定済み | EN側 |
| 数値: 英語アラビア数字不一致検出・Tier1表記差等価 | **PRODUCTION_WIRED**(2026-09-27承認) | 同左 | `N%`値変更の穴 |
| 数値S1の穴の是正(JA漢数字・EN`N%`・表記差) | JA表記差=**Trial止まり(VALIDATEDではない、Status訂正済み)**。それ以外は**USER_DECISION_REQUIRED**(D-4、決定記録なし) | JA値署名Trial、反例74件誤PASS 0 | Production配線・採用判断・EN`N%` |
| 否定(EN/JA) | **PRODUCTION_WIRED** | 同左 | 新規拡張のみ(保留D-19) |

注: 「USER_DECISION_REQUIRED」は、SSOT・Git・コードを調べた結果、ユーザー決定の記録が見つからないことを意味する。ユーザーがSSOT外で決めていた場合は、本書の記録を示して確認すれば足りる(§6-1)。

## §4 10/12統一フローのProduction採用に本当に残る未決事項
(決定済み部分は除外: JA SCG一式、PHONETIC一括許容不可、cool-down現行維持の推奨は未回答だが05Aで通算3回化は是正済み、OPEN-270/271是正[D-18]、Azure費用計上[05A済])

| # | 未決事項 | なぜ未決か / 決定済みでない根拠 |
|---|---|---|
| 1 | D-1 導入範囲・順(推奨: Full Story英語先行、前提D-2〜D-4充足後) | UDR #18、OPEN-286。決定記録なし |
| 2 | D-2 試聴リスト連動を導入前提にするか+連動の実装 | 本番コードに連動処理なし。決定記録なし(OPEN-286「導入しない案」) |
| 3 | D-3 英語Secondary PASS集合(日本語は2ラベルで決定済み) | 英語側の回答なし |
| 4 | D-4 数値S1の是正(JA漢数字・EN`N%`・表記差)の採否と方式 | コード無変更を確認。OPEN-287/334、UDR #24。10/13 JA Trialは「採用判断なし」 |
| 5 | D-5 見出し・LR後原稿の追加保護 | OPEN-288。決定記録なし |
| 6 | D-7〜D-10、D-12、D-13、D-15(UNCERTAIN→HR、minimal撤去、LR位置づけ、C1廃止、6%減速案、Secondary選択、技術失敗扱い) | UDR #8/#18、OPEN-289〜291。決定記録なし(D-10のC2・推奨4維持は既決) |
| 7 | D-11 固有名詞Secondary一致の扱い(S7) | 決定記録なし |
| 8 | D-17 LR再TTS計数改修(導入必須条件にするか) | OPEN-286(3)。決定記録なし |
| 9 | D-6/D-16 KP単一PromptとTrial実施可否 | 推奨は追加Trial(数円)。決定記録なし |
| 10 | 保留D-19(新規仕様候補: 否定活用ギャップ等) | 新規仕様のため別判断 |

## §5 ChatGPTが未解決と再提示した理由の推定(事実ベース)
1. 10/12報告書(`RECONCILIATION_FINAL_REPORT_01.md` L3)・V04のStatusは`USER_DECISION_REQUIRED`で、その後も**D-1〜D-19に対するユーザー回答がSSOTに記録されていない**(`USER_DECISION_REGISTER_01.md` L35、`OPEN_ITEMS.md` L789-794、`DECISION_LOG.md` L20582)。ChatGPTがSSOTどおり未決と読むのは自然。
2. ユーザーが「判断した」と覚えているものに近い**隣接する決定**は実在する: (a)2026-10-11 JA SCG(厳格集合・否定マーカー・C2)の承認、(b)2026-10-12 05A「既存Production不具合の是正」(TTS総試行3回上限・Azure費用計上。③④とは別件)、(c)2026-10-13 発音同等性の設計方針合意と安全条件維持(否定・時制・数・重要語の置換/欠落)、(d)2026-10-13/14 M1・F1・OOV複数発音候補の承認(F1は承認時前提と実装の食い違い是正、M1はPASS_WITH_WARNING+audit trail)、(e)2026-10-13 JA表記ゆれTrial(Opus必須修正反映)。名前・目的が近く、③④の決定と混同されやすい。
3. それぞれの決定が「統一フロー」の項目に紐付けて記録されていない(UDR #18は10/12時点のまま、#41・#52は別行)。
4. 結果として、既決(JA SCG・否定保護・英語Tier1表記差等価・警告ラベル)と未決(D-2/D-3/D-4/D-11)を1表にまとめた記録がこれまで存在しなかった。本書§0・§3がその初版。

## §6 確認できなかった事項・矛盾
1. **ユーザー記憶との食い違い**: ③警告・試聴連動と④数値S1の是正は、SSOT・Git・コードのどれにも決定/是正の記録なし。チャット上の口頭決定でSSOT未反映の可能性は否定できないが、本調査では**確認できない**(推測でPASS扱いにしていない)。
2. V04 L100は「否定マーカー補強(推奨4)は新規仕様候補・未承認」と記述するが、CURRENT_SPEC L2016は日本語の推奨4を2026-10-11承認・配線済みと記述。V04が英語側拡張を指すなら矛盾は解消するが、原文は日本語既承認との区別が曖昧。
3. `USER_DECISION_REGISTER_01.md` L25は`RECONCILIATION_REPORT_01.md`を参照するが、実ファイル名は`RECONCILIATION_FINAL_REPORT_01.md`。
4. `docs/pm/OPUS_FINDINGS_LEDGER.md`にASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01(10/11〜10/12)のOpus所見(M1〜M7、M1〜M5)の行を確認できない(Grep 0件)。Opus総合レビュー本文は05B時点で未入手(`RECONCILIATION_FINAL_REPORT_01.md` L148)。
5. 英語数値/否定testの最新実行記録、減速後経路のprotected_checkを直接確認したtest、`er014_output`等の`number_mismatch`記録の内容は**未確認**。
6. `tools/stop_scope_check_01.py`は`--run-dir`必須でrun-dirのない本作業では実行不可(rc=2、usage)。read-onlyでAPI呼出0のため影響なし。
7. T-0: `check_delegation_prompt.py`はFAIL(保存文を要点圧縮した節で、必須の「事前指定Grep一覧+追記位置・更新位置の手順」「実行コマンド全文」節を欠くため)。FAILでも継続の規定どおり実施。保存ファイルは「ユーザー指示原文」節のみ逐語、他は要点保存。
