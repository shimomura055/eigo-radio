# CURRENT_SPEC — 現在有効な正式仕様

**管理ID: ER-PM-001**
**最終更新: 2026-09-13(第32弾、PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-
PRODUCTION-WIRING-01/PM-CLOSEOUT-CONSOLIDATION-117、PM委任文標準の
Production配線)**: PM委任文標準(D-2、`docs/pm/PM_GOVERNANCE.md` 11節、
2026-09-13ユーザー正式採用[施策1]、Gate 3結果に応じて`PRODUCTION_WIRED`
または`APPROVED_FOR_PRODUCTION`[未充足項目明記])を配線した。PM運用
ルールのみでProduction機能仕様・コード・Promptの変更は伴わない。詳細は
`DECISION_LOG.md` `PM-CLOSEOUT-CONSOLIDATION-117`エントリ参照。
**最終更新(直前の記録): 2026-09-10(第31弾、PM-CLOSEOUT-CONSOLIDATION-65、3V[3声Voice
方式]のAPPROVED_FOR_PRODUCTION反映)**: ユーザー正式決定(2026-09-10)に
より、`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01`(3V、3声Voice方式)の
状態を`VALIDATED`→**`APPROVED_FOR_PRODUCTION`**へ更新した(「## B-Family
(Voices)Editorial Type」節の3V行のみ更新、仕様本文の追加・変更なし)。
ただし**`PRODUCTION_WIRED`ではない**(配線完了条件・残存課題は
`OPEN_ITEMS.md`OPEN-120行参照)。今回の3V記事自体はTrial記事として
closeout、4V(4声Voice方式)は`DEFERRED`、2V(2声Voice方式)/3V追加の
Production実運用確認1本ずつを計画登録した(詳細はDECISION_LOG.md
`PM-CLOSEOUT-CONSOLIDATION-65`エントリ参照)。
**最終更新(直前の記録): 2026-09-09(第30弾、PM-CLOSEOUT-CONSOLIDATION-56、3V Audio
Trial VALIDATED closeoutのSSOT反映)**: ユーザー正式決定(B-3V-4=(a)、
3V完成episode試聴OK)により、`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-
TRIAL-01`(Trial-02版基準、3声・16 segment・Audio Validation Gate
両経路PASS・実測356.6秒)をGate1=**VALIDATED**として新規closeout
Report(`EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01-CLOSEOUT_
REPORT.md`)で確定した。VALIDATEDはTrial範囲の技術的成立を意味する
のみで、Production採用(`APPROVED_FOR_PRODUCTION`)は別途ユーザー判断
のまま(配線に必要な5項目[registry可変voice数シグネチャ・Gate辞書
point_three登録・Comment 3V Contract化・mode/level命名・Voice 3
(Schedar)本採用格上げ承認]は未実装で継続提示)。「## B-Family
(Voices)Editorial Type」節へ3V(人物Voice)の状態行を1行追加した。
既存のB1/A2 Production配線(`PRODUCTION_WIRED`済み部分)への変更は
ない。Production/Prompt本体の変更はゼロ。詳細は`DECISION_LOG.md`
`PM-CLOSEOUT-CONSOLIDATION-56`エントリ・`OPEN_ITEMS.md`OPEN-120行
参照。
**最終更新(直前の記録): 2026-09-09(第29弾、PM-CLOSEOUT-CONSOLIDATION-47、A3-UDR-3/
D2-UDR-1現行案不承認のSSOT反映)**: ユーザー正式決定により、News Focus
Module+Point Role hint(A3-UDR-3、Trial-06)・Discovery/Why Layer3 Focus
Module(D2-UDR-1、Trial-07)は、いずれもGate1=`VALIDATED(Trial)`のStatus
自体は保持しつつ、**現行Production採用案は不承認**(News: focus_hint NG率
50%はProduction採用水準ではない、Discovery: REVIEW_REQUIRED率約5倍増加・
Point多様性低下、両者とも既存仕様全体との重複・競合整理が未了)と確定
した。Focus Module/Point Roleという考え方自体はREJECTEDではなく、既存
仕様全体を俯瞰する再改善を実施する(PM/Reconciliation Gate`FAMILY-A-
POINT-QUALITY-CONTROL-RECONCILIATION-GATE-01`を最優先、その後A3-UDR-3・
D2-UDR-1それぞれの再改善Trialへ)。「## 通常News(Major/Daily News)
Reference仕様」節の「News固有の視点付与層」行、「## Discovery/Why
(Pool型)」節の「Layer3 Focus Module」行を更新した。既存のMajor/Daily
Gate 6項目・Trend Gate 6条件・Trend Synthesis仕様(`PRODUCTION_WIRED`
済み部分)への変更はない。Production/Prompt本体の変更はゼロ。詳細は
`DECISION_LOG.md` `PM-CLOSEOUT-CONSOLIDATION-47`エントリ・
`OPEN_ITEMS.md`OPEN-135/112/120/136/138行参照。
**最終更新(直前の記録): 2026-09-09(第28弾、PM-CLOSEOUT-CONSOLIDATION-43、A2 Trend
end-to-end B1B level完走のSSOT反映)**: `FAMILY-A-COMPLETION-A2-TREND-
END-TO-END-01_REPORT.md`§9により、Trend Synthesis記事がA2level・B1B
level両方でTTS→Assembly→Audio Validation Gate→player完走した。B1B
Key Phrase 5(「形になり始める」)は承認済み経路での再生成1回も
`TRUE_CONTENT_MISMATCH`で不合格となり、既存Key Phrase選定経路で新候補
`work to do`/「まだ取り組むべき課題」へ差し替え(Redundancy QA PASS)。
「## News Editorial Mode(Trend Synthesis)」節へ「theme→artifact連続性」
行を追加した。既存仕様(Focus Module・Engagement Block・retry/
fallback整合)への変更はなし。詳細は`DECISION_LOG.md`
`PM-CLOSEOUT-CONSOLIDATION-43`エントリ・`OPEN_ITEMS.md`OPEN-135/112行、
`FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01_REPORT.md`§9参照。
**最終更新(直前の記録): 2026-09-09(第27弾、PM-CLOSEOUT-CONSOLIDATION-41、Editorial
Type routing[2軸判定]・Discovery/Why[Pool型]正式化のSSOT反映)**:
ユーザー正式決定に基づき、A Family(Discovery/Why + News[Major/Daily] +
Trend Synthesis)のうちある題材がどのEditorial Typeとして書かれるべきかを
決める上流のType routingを、新設「## Editorial Type Routing(2軸判定)」
節へ正式反映した(軸A=中心的主張の最近性依存・軸B=独立Signal集約依存、
tie-break primitive=依存構造読み、判定=手動+run summary記録、自動判定は
`OPEN-130`として引き続き`DEFERRED`)。Discovery/Whyについては、既承認
「Pool型(Evergreen、特定の1件の最近の出来事に非依存)」の正式化として
新設「## Discovery/Why(Pool型)」節(最小)へ、対象定義・Layer3 Focus
Moduleの状態(`VALIDATED`、`FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-
TRIAL-07`で追加検証中)・D3派生5項目(いずれも`DEFERRED`/保留)を記録
した。既存のMajor/Daily Gate 6項目・Trend Gate 6条件・Trend Synthesis
仕様への変更はない(2軸判定は上流のType routingであり下流Gateを代替・
変更しない)。詳細は`DECISION_LOG.md` `PM-CLOSEOUT-CONSOLIDATION-41`
エントリ・`OPEN_ITEMS.md`OPEN-130/135/112行、`FAMILY-A-COMPLETION-A4-
DISCOVERY-DESIGN-02_REPORT.md`参照。
**最終更新(直前の記録): 2026-09-09(第26弾、PM-CLOSEOUT-CONSOLIDATION-40、A2 Trend
end-to-end[A2 level完走]反映)**: `FAMILY-A-COMPLETION-A2-TREND-END-TO-
END-01_REPORT.md`§8により、Trend Synthesis記事のA2 levelが配線済み
Production関数のみ(TTS→Assembly→Audio Validation Gate→player)で完走
した。「## News Editorial Mode(Trend Synthesis)」節へ、A2日本語タイトル
供給方式(既存前例踏襲、直訳定数の人手供給が正式initial path)の1行を
追加した。B1B側はKey Phrase 5日本語音声のGate BLOCKEDのまま変更なし
(ユーザー承認待ち)。既存仕様(Focus Module・Engagement Block・retry/
fallback整合)への変更はなし(既存前例の適用のみ)。詳細は`DECISION_LOG.md`
`PM-CLOSEOUT-CONSOLIDATION-40`エントリ・`OPEN_ITEMS.md`OPEN-112/135/137
行、`FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01_REPORT.md`参照。
**最終更新(直前の記録): 2026-09-09(第25弾、PM-CLOSEOUT-CONSOLIDATION-34、OPEN-112 G1の
Fable最終受入=`PRODUCTION_WIRED`確定)**: 前弾(CONSOLIDATION-33)で
「`PRODUCTION_WIRED`候補(Fable受入待ち)」としていたG1(Diagnostic Full
Retry診断promptへ前回Point One/Two実本文を渡す回帰修正、commit
`8596f34`)を、Fableが承認済み挙動(ER-009-N1-DIAGNOSTIC-FULL-RETRY-
CLOSEOUT-14)への回帰修正として正式受入し、「Fact Safety(共通)」節
Diagnostic Full Retry行の状態表記を`PRODUCTION_WIRED`(確定)へ更新した。
Point Overlap問題自体は未解決のまま(`OPEN_ITEMS.md`OPEN-134行の観測
Exit条件へ継続統合、Runtime evidence[Hanshin B1B/A2]を観測run #1・#2
として`er011_output/point_overlap_observation_log.jsonl`へ記録済み)。
詳細は`DECISION_LOG.md` `PM-CLOSEOUT-CONSOLIDATION-34`エントリ・
`OPEN_ITEMS.md`OPEN-112/120/132/134行、`OPEN-112-DIAGNOSTIC-RETRY-
POINT-BODY-REGRESSION-FIX-01_REPORT.md`・`EDITORIAL-B-FAMILY-VOICES-
4V-ARTICLE-TRIAL-01_REPORT.md`参照。
**最終更新(直前の記録): 2026-09-09(第24弾、PM-CLOSEOUT-CONSOLIDATION-33、
OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01のGate 3配線+
CURRENT_SPEC訂正)**: ユーザー正式決定(A-UDR-20=(i))に基づき、G1
(Diagnostic Full Retry診断promptへ前回Point One/Two本文を渡す)を
承認済み挙動(ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14)への回帰修正
としてGate 3配線した(commit `8596f34`、詳細は「Fact Safety(共通)」節
Diagnostic Full Retry行へ追記)。あわせてユーザー正式決定(A-UDR-21=(ii))
に基づき、「Point One対Point Twoのlexical overlap検査(追加ペア)」行
(ER-011-NO18)の前回注記(「実装未確認・OPEN-133で追跡」)を、cross_
point_overlapのstill_flagged統合は「未実装・`DEFERRED`」へ実態に合わせて
訂正した(将来実装するかどうかは別途判断、OPEN-133)。詳細は
`DECISION_LOG.md` `PM-CLOSEOUT-CONSOLIDATION-33`エントリ・`OPEN_ITEMS.md`
OPEN-112/133/134/120行、`OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-
REGRESSION-FIX-01_REPORT.md`参照。
**最終更新(直前の記録): 2026-09-09(第23弾、PM-CLOSEOUT-CONSOLIDATION-32、
FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05結果のSSOT注記反映)**: 「Point
One対Point Twoのlexical overlap検査(追加ペア)」行(ER-011-NO18-
PRODUCTION-SPEC-IMPROVEMENT-01、`DECIDED`/`PRODUCTION_WIRED`)へ、
「※実装未確認・OPEN-133で追跡(2026-09-09)」の注記のみを追加した
(既存記載自体は変更しない)。Trial-05のGate 4静的diff監査で、承認済み
のcross_point_overlap関連retry判定統合がProductionコードで実装未確認
であることを新規発見し、`OPEN_ITEMS.md`へ`OPEN-133`
(`USER_DECISION_REQUIRED`)として登録したことに伴う注記。あわせて
Diagnostic Full Retryの前回Point本文埋め込み漏れ(G1)は実装漏れ
[承認済み範囲内]と確定したが、こちらはProduction/Prompt自体の記述
変更ではないため本ファイルへの記載追加は行っていない。詳細は
`DECISION_LOG.md` `PM-CLOSEOUT-CONSOLIDATION-32`エントリ・
`OPEN_ITEMS.md` OPEN-112/133/134行、
`FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05_REPORT.md`参照。
**最終更新: 2026-09-09(第22弾、PM-CLOSEOUT-CONSOLIDATION-31、OPEN-131
Fact Checker A'抽出ロジック修正版のFable受入)**: 「## B-Family(Voices)
Editorial Type」節「Fact Checker `REVIEW_REQUIRED`」行を、
`OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02`(`build_voice_attribution_
block()`をタグ行から次の空行/`[`開始行/`===`開始行の直前までの塊単位
抽出へ修正、関数シグネチャ・fail-closed挙動・ルール文言は不変)の内容へ
更新した。Statusは`PRODUCTION_WIRED(opt-in、Phase 2で既定接続)`のまま
維持し、この修正版を正式なProduction実装とする(commit `a865411`)。
修正後の完全blockでのruntime evidenceでは、B1は不変(PASS/unsupported
0件)だが、A2はPASS→REVIEW_REQUIRED(unsupported2件)へ変化した(切り
詰めblockの下で見えていなかった適正な検出[TP]の回復であり、false
accept新規発生ではない)。詳細は`DECISION_LOG.md`
`PM-CLOSEOUT-CONSOLIDATION-31`エントリ・`OPEN_ITEMS.md` OPEN-131行、
`OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02_REPORT.md`参照。
**最終更新: 2026-09-09(第21弾、PM-CLOSEOUT-CONSOLIDATION-29、OPEN-131
ユーザー正式決定)**: 「## B-Family(Voices)Editorial Type」節の「Fact
Checker `REVIEW_REQUIRED`」行のStatusを`PRODUCTION_WIRED候補(Fable受入
待ち)`から`PRODUCTION_WIRED(opt-in、Phase 2で既定接続)`へ更新した(仕様
内容自体は無変更)。B-Family Production既定stageへの自動接続はPhase 2
Writer配線時に実施する方針とし、新規Open Item`OPEN-132`(Phase 2 Writer
配線時必須チェックリスト)で追跡する。詳細は`DECISION_LOG.md`
`PM-CLOSEOUT-CONSOLIDATION-29`エントリ・`OPEN_ITEMS.md` OPEN-131/
OPEN-132行参照。
**最終更新: 2026-09-09(第20弾、PM-CLOSEOUT-CONSOLIDATION-28、OPEN-129
Fable受入+OPEN-131スコープ注記)**: 「## B-Family(Voices)Editorial Type」
節の「OPEN-129整合」行のStatusを`PRODUCTION_WIRED候補(Fable受入待ち)`
から`PRODUCTION_WIRED`(opt-in、2026-09-09 Fable受入、commit `2814ed5`/
`34fe8dd`)へ更新した(仕様内容自体は無変更、mandatory化は引き続き
未承認)。「Fact Checker `REVIEW_REQUIRED`」行はFableが精査した結果、
共有Fact Checker・registry・runner opt-in入口への配線は完了しているが、
B-Family Production runnerの既定パイプラインがPhase 2 Writer配線保留の
ためFact Checkerを既定stageとして呼んでおらず「Production正式初回path
での既定実行」には至っていないため、Status表記(`PRODUCTION_WIRED候補
[Fable受入待ち]`)は変更していない(スコープ注記のみ、詳細は
`OPEN_ITEMS.md` OPEN-131行参照)。詳細は`DECISION_LOG.md`
`PM-CLOSEOUT-CONSOLIDATION-28`エントリ参照。
**最終更新: 2026-09-09(第19弾、OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-
PRODUCTION-WIRING-01・OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-
PRODUCTION-WIRING-01、Sonnet配線・Fable受入待ち)**: 「## B-Family
(Voices)Editorial Type」節の2行を更新した。(1) Fact Checker
`REVIEW_REQUIRED`行: 候補A'(Voice別evidenceタグ+opt-inルール)を
`er012_b_family_editorial_type_registry_01.py::fact_attribution_mode`
(既定OFF、`family=="B"`のコードレベルgating)として配線。ON時、実記事2本
でverdict REVIEW_REQUIRED→PASS(unsupported claims 5/6件→0件)へ改善、
Local Rewrite後も帰属維持を実出力で確認(費用¥10.24)。(2) OPEN-129整合
行: 共有Audio Validation Gate(`verify_episode_audio_validation_gate()`)
へ`required_structure`のopt-in引数(既定OFF)を追加し、family+level複合
キーの期待構造(正本は生成側)と実segment集合を突合できるようにした
(delete/voice_swap/extra検知、reorder対象外)。既存完成episode12/12で
false reject 0、4経路×5ケースで検知12/12(費用¥0)。いずれも既定OFF・
mandatory化なし、A-Family経路は無変更(byte一致テストで固定)。両者とも
Status`PRODUCTION_WIRED候補(Fable受入待ち)`。詳細は`OPEN_ITEMS.md`
OPEN-131/OPEN-129行、`DECISION_LOG.md`該当エントリ、`OPEN-131-MULTI-
VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01_REPORT.md`・`OPEN-129-AUDIO-
GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01_REPORT.md`参照。
同じ共有Audio Validation Gate内には、2026-09-18に`KEY-PHRASE-SOURCE-
CONSISTENCY-GATE-01`(Key Phrase source整合Gate、`PRODUCTION_WIRED`)も
追加されている(詳細は「Key Phrase」節「Key Phrase source整合Gate
(OPEN-170再発防止)」行を参照)。
**最終更新: 2026-09-09(第18弾、PM-CLOSEOUT-CONSOLIDATION-25、Fable最終
受入)**: 「## B-Family(Voices)Editorial Type」節「Production経路」行の
状態表記を`PRODUCTION_WIRED`(Gate 3、Fable受入待ち)から`PRODUCTION_WIRED`
(2026-09-09 Fable最終受入、commit `2b2f266`/`2fbeee3`)へ更新した(仕様
内容自体の変更なし)。詳細は`OPEN_ITEMS.md` OPEN-120行、`DECISION_LOG.md`
`PM-CLOSEOUT-CONSOLIDATION-25`エントリ参照。
**最終更新: 2026-09-09(第17弾、EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-
WIRING-01、Gate 3配線)**: ユーザー承認(2026-09-09、`APPROVED_FOR_
PRODUCTION`)に基づき、B-Family A2(「フリーアドレス vs 固定席」A2、
`stay put`新版採用)をProduction正式経路へ配線した。新設「## B-Family
(Voices)Editorial Type」節を参照(構造・voice・slowdown・Comment言語・
日本語タイトル・Gate対象化・11語超許容は今回限り・Fact Checker運用注記・
OPEN-129整合を記載)。詳細は`OPEN_ITEMS.md` OPEN-120/OPEN-129行、
`DECISION_LOG.md`該当エントリ、`EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-
WIRING-01_REPORT.md`参照。
**最終更新: 2026-09-08(第16弾、PM-CLOSEOUT-CONSOLIDATION-22、ユーザー決定
A-UDR-8/9/10反映)**: 「## 通常News(Major/Daily News)Reference仕様」節の
「Reference記事の正式指定」を更新した。**Household(冷蔵庫クリスパー)を
同系列referenceから除外**(単一起点イベントを持たず通常News対象外、
別Editorial Type[Discovery/Why系]候補として別途整理、通常Newsの定義を
Householdに合わせて広げない、A-UDR-9)。Health=「単一起点研究発表がある
場合はMajor/Dailyとして扱う」境界規則を1行追記(`DECIDED`ではなく
**運用方針・設計Trial段階**と明記、Major/Daily Gateの非対称性は現状許容、
myth-correction候補は保留、A-UDR-10)。News固有層設計案(Focus Module+
Major/Daily Gate)はユーザー承認、Hanshin Ledger固定でFocus Moduleなし/
ありのA2/B1比較Trial(`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-
TRIAL-02`)へ進む(A-UDR-8、内容は本節では規定しない、配線はユーザー
判断前に行わない)。将来のMode自動判定には排他的・再現可能な判定ロジック
が必要という点をOpen Item化(`OPEN_ITEMS.md` OPEN-130)。詳細は
`DECISION_LOG.md` `PM-CLOSEOUT-CONSOLIDATION-22`エントリ参照。
**最終更新: 2026-09-08(第15弾、FAMILY-A-DAILY-NEWS-REFERENCE-
FORMALIZATION-01、ユーザー決定A-UDR-5)**: 既にDECIDED/PRODUCTION_WIRED
済みの既存A2/B1共通骨格(11パート構造・Writer共通経路・Point Balance・
Fact Safety・Spoken-first数値原則・Comment Contract・Key Phrase
Contract・Audio構造)が通常News(Major/Daily News)にもそのまま適用
されることを、新設「## 通常News(Major/Daily News)Reference仕様」節
(「## News Editorial Mode(Trend Synthesis)」節の直後)へ正式反映した。
Hanshin(`ER-003-A2-B1-N3-01`、Health/Household含む)を構造・Writer・
Fact Safety・音声のreference実装として正式指定、ADD03(イラン)/A02
(英SNS)は題材・音声構造referenceに限定(本文生成コードパス・完成音声は
非再利用、B1-A方式はobsolete)。News固有層(Layer3 Focus Module・Mode
判定基準)は内容を書かず「未設計・設計Trial起票済み
(`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01`、Lane A-2)」とだけ
明記。Trend Synthesis専用仕様は本節へ混在させていない。Gate 4 Dangling
Reference Check実施、参照管理IDはすべて既存CURRENT_SPEC/DECISION_LOG内
に存在することを確認(詳細は`FAMILY-A-DAILY-NEWS-REFERENCE-
FORMALIZATION-01_REPORT.md`参照)。
**最終更新: 2026-09-08(第14弾、PM-CLOSEOUT-CONSOLIDATION-19、Fable Gate 7
最終受入)**: Fableが`OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01_
REPORT.md`(§1〜§11、修正指示1回目への対応[A2新規run2回目でstatus=OK
到達・B1B Key Phrase Redundancy PASSまで完走]を含む)をGate 7で照合し、
Trend Synthesis modeを`PRODUCTION_WIRED`として正式受入した。下記
「## News Editorial Mode(Trend Synthesis)」節の該当6行を
`PRODUCTION_WIRED候補(Fable受入待ち)`から`PRODUCTION_WIRED`へ更新した
(内容自体は無変更)。据え置き4件(Mode判定自動化・News Ledger自動供給・
Reference Digest追加検証・Diagnostic Full Retry診断語彙拡張)はTrial
候補として継続、Point Overlap ratioのrun間分散(0.31〜0.66)を対策未実装の
観測事項として記録した(いずれも`USER_DECISION_REQUIRED`候補、実装なし)。
詳細は`OPEN_ITEMS.md`OPEN-112行、DECISION_LOG.md
`PM-CLOSEOUT-CONSOLIDATION-19`エントリ参照。
**最終更新: 2026-09-08(第13弾、PM-CLOSEOUT-CONSOLIDATION-18、参照のみ・
仕様変更なし)**: Lane B A2完成Trial(`EDITORIAL-B-FAMILY-VOICES-A2-FREE-
ADDRESS-COMPLETION-TRIAL-01/02`、Trial-02=VALIDATED、試聴・承認待ち)、
Lane A-3通常News仕様書き起こし案(`FAMILY-A-DAILY-NEWS-SPEC-DRAFT-01`)、
Voice割当決定(4V/3V、Schedar/Sulafatはユーザー承認で正式候補へ格上げ)、
`docs/pm/PM_GOVERNANCE.md`9節への「並列Lane報告の補足」追記をSSOTへ反映
した。いずれも調査・設計・文書運用ルールのみでコード・Prompt・本仕様書の
変更を伴わず、採用判断は`USER_DECISION_REQUIRED`のままSTOP。詳細は
`OPEN_ITEMS.md`OPEN-112行・OPEN-120行、DECISION_LOG.md
`PM-CLOSEOUT-CONSOLIDATION-18`エントリ参照。
**最終更新: 2026-09-08(第12弾、OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-
WIRING-01、Gate 3配線)**: ユーザー承認(`APPROVED_FOR_PRODUCTION`)に基づき、
Trend Synthesis modeをProduction Writer正式初回経路(`er006_pool_pilot_
01_writer.py::run_writer_for_theme()`→`er003_v1_n3_01_articles_
generate.py::run_one_pattern()`)へ配線した。`build_common_block()`へ
後方互換オプション引数`editorial_type_module_block`(既定`""`、既存出力
バイト単位不変をgolden-masterテストで固定)を追加し、Focus Module・
Engagement/Storytelling原則(いずれもTrial VALIDATED済みの内容を無変更で
採用、施策2[Reference Digest]は含めない)をTrend Synthesis限定で注入
可能にした。既存retry/fallback機構(Diagnostic Full Retry・Evidence
Compression Editor・Point Overlap QA・Fact Checker・Ledger Deviation
Checker)は無変更のままmode非依存で機能することを実runtime evidence
(正しいTheme 2 Ledgerで生成、B1B`status=OK`・A2は既存Loop Budget上限内で
`NG_REVIEW_REQUIRED`)で確認。詳細は新設「## News Editorial Mode(Trend
Synthesis)」節・`OPEN_ITEMS.md`OPEN-112行・`OPEN-112-TREND-SYNTHESIS-
MODE-PRODUCTION-WIRING-01_REPORT.md`参照。Mode判定自動化・Ledger自動
供給・Reference Digest追加検証・Retry語彙拡張は仕様化していない(Open
Item継続)。runtime evidence取得時に別テーマ(Iran/Hormuz)を誤って
「Theme 2」として使用する作業ミスがあり、費用上限¥100を超過した経緯を
Reportへ開示している。
**最終更新: 2026-09-08(第11弾、PM-CLOSEOUT-CONSOLIDATION-17、参照のみ・
仕様変更なし)**: Lane A 3件(`FAMILY-A-TREND-SYNTHESIS-PRODUCTION-
READINESS-01`、`FAMILY-A-DISCOVERY-DEFERRED-CLASSIFICATION-01`、
`FAMILY-A-LEGACY-NEWS-ASSET-SURVEY-01`)とLane B(`EDITORIAL-B-FAMILY-
VOICES-PHASE1-5-3V-4V-INTEGRATED-DESIGN-TRIAL-03`、3V/4V統合設計、
Gate 1=`VALIDATED`[Trial範囲内])をSSOTへ反映した。いずれも調査・設計のみ
でコード・Prompt・本仕様書の変更を伴わず、採用判断は`USER_DECISION_
REQUIRED`のままSTOP。Lane BのB-5で、既存Audio Validation Gateが「構造上
あるべきsegment数」との一致を検証しない新規failure modeを発見し、新規
`OPEN-129`として登録した(`USER_DECISION_REQUIRED`)。voice候補6種
(Algieba/Erinome/Schedar/Sulafat/Aoede/Charon)の試聴用artifact
(`er012_output/editorial_b_voices_phase1_5_3v_4v_integrated_trial_03/
voice_samples_review.html`)を作成した。詳細は`OPEN_ITEMS.md`OPEN-112行・
OPEN-120行・OPEN-129行、DECISION_LOG.md`PM-CLOSEOUT-CONSOLIDATION-17`
エントリ参照。
**最終更新: 2026-09-08(第10弾、PM-CLOSEOUT-CONSOLIDATION-16、参照のみ・
仕様変更なし)**: Lane A(`FAMILY-A-BRANCH-FACT-CHECK-02`、Discovery/News/
Trend Synthesis枝別事実確認、読み取り専用)とLane B(`EDITORIAL-B-FAMILY-
VOICES-PHASE1-5-FOUR-VOICES-STRUCTURE-DESIGN-TRIAL-02`、4 Voices構造設計
Trial、S1推奨・Gate 1=`VALIDATED`)を相互独立に並行実施しSSOTへ反映した。
いずれもコード・Prompt・本仕様書の変更を伴わず、両Laneとも採用判断は
`USER_DECISION_REQUIRED`のままSTOP。詳細は`OPEN_ITEMS.md`OPEN-112行・
OPEN-120行、DECISION_LOG.md`PM-CLOSEOUT-CONSOLIDATION-16`エントリ、
`FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`、`EDITORIAL-B-FAMILY-VOICES-
PHASE1-5-FOUR-VOICES-STRUCTURE-DESIGN-TRIAL-02_REPORT.md`参照。
**最終更新: 2026-09-08(第9弾、PM-CLOSEOUT-CONSOLIDATION-15、参照のみ・
仕様変更なし)**: Lane A(`FAMILY-A-DESIGN-FIX-INVENTORY-01`、Family A設計FIX
状況の読み取り専用棚卸し、結論`PARTIAL`)とLane B(`EDITORIAL-B-FAMILY-VOICES-
PHASE1-5-FOUR-VOICES-AXIS-DESIGN-TRIAL-01`、4 Voices選定軸設計Trial、案A推奨・
`VALIDATED`)をSSOTへ反映した。いずれもコード・Prompt・本仕様書の変更を伴わず、
両Laneとも採用判断は`USER_DECISION_REQUIRED`のままSTOP。詳細は`OPEN_ITEMS.md`
OPEN-120行・OPEN-112行、DECISION_LOG.md`PM-CLOSEOUT-CONSOLIDATION-15`エントリ、
`FAMILY-A-DESIGN-FIX-INVENTORY-01_REPORT.md`、`EDITORIAL-B-FAMILY-VOICES-
PHASE1-5-FOUR-VOICES-AXIS-DESIGN-TRIAL-01_REPORT.md`参照。
**最終更新: 2026-09-08(第8弾、PM-CLOSEOUT-CONSOLIDATION-13、OPEN-127/
OPEN-128 Fable受入)**: 第7弾で配線したOPEN-127(em dashトークナイズ)・
OPEN-128(方式D局所ASR確認2段判定)を、Fableが Gate 3(14項目)・
Gate 4表・runtime evidence(OPEN-127: TP10/10・Voice B負例4/4是正、
OPEN-128: 確定TP8/8・確定FP0/15・全23件ASR呼び出し1回・Standard同期
TTS実発火1件¥0.483)・project-wide regression(collected=2184、
passed=2181、既知3件のみ)・ASR失敗時挙動が現行仕様(§6)と同一
(新規fail-open/fail-closed設計なし)・既存AND gate/retry loop/Human
Review Lock無変更(diff確認)を照合し、両件を`PRODUCTION_WIRED`として
正式受入した(commit OPEN-127=`602f1f5`、OPEN-128=`05bbeca`)。
Production採用範囲・acoustic threshold(sim0.85/run0.12秒)は第7弾から
無変更。詳細は`OPEN_ITEMS.md`OPEN-127/OPEN-128行、DECISION_LOG.md
`PM-CLOSEOUT-CONSOLIDATION-13`エントリ参照。
**最終更新: 2026-09-08(第7弾、OPEN-127/OPEN-128 Production配線完了)**:
ユーザー承認(2026-09-08、`APPROVED_FOR_PRODUCTION`)に基づき、共有module
`er011_open121_repetition_qa_production_01.py`へ2件を配線した。
**OPEN-127**: `_normalize_tokens()`へem dash(—, U+2014)のみを空白へ
置換する1行(`re.sub("—", " ", text)`)を追加(candidate1a、en dash
[–]・hyphen[-]は対象外)。Runtime evidence: 既知真の重複10/10で
flagged=True維持、Voice B意図的並行構文(phase1_02 point_two
attempt1-3+trial_08)4/4でflagged=False是正。**OPEN-128**: 方式D
(`analyze_profile_d_long_lag()`)へ、acoustic flag後の局所ASR語句一致度
確認(`confirm_by_local_asr_overlap()`新規、overlap_ratio>=0.5 OR
lcs_words>=3、方式Aと同一の`transcribe_verbatim()`結果を共有し二重ASR
実行を回避)を追加した2段判定を配線。acoustic threshold(sim 0.85/run
0.12秒)は無変更。Runtime evidence: 確定TP8/8・確定FP0/15、全23件で
ASR呼び出し1回、Standard同期TTS実発火1件(¥0.483、上限¥20以内)。
既存AND gate・retry loop・Human Review Lockの分岐・意味は無変更(diff
確認済み)。ASR失敗時の挙動は方式A単体と同一(既存仕様通り、新規fail-
open/fail-closed設計は追加していない)。回帰テスト: 新規`er011_open128_
method_d_local_asr_confirm_production_wiring_01_test_01.py`(9件)+
`er011_open121_repetition_qa_production_wiring_01_test_01.py`の
`EmDashTokenBoundaryTests`(4件)、既存30件含め全PASS。project-wide
regression(`run_project_regression.py`、collected=2184、passed=2181、
failed=3[既知の無関係failureのみ、新規failureゼロ])。詳細は
`OPEN-127-EM-DASH-TOKEN-BOUNDARY-PRODUCTION-WIRING-01_REPORT.md`・
`OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01_REPORT.md`
参照(Gate 3/Gate 4結果を含む、`PRODUCTION_WIRED`確定はFable最終受入
待ち)。
**最終更新: 2026-09-08(第6弾、PM-CLOSEOUT-CONSOLIDATION-11、B-Family Phase 1
Fable受入+Trial A/B起票結果の統合)**: ユーザー決定(Voice B意図的反復
"do not need … do not need"は正常、Gate停止は誤検知、Phase 1は既存Human
Approval経路で通してよい)に基づき、B-Family Production Path Phase 1
(`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01`)のpoint_two
attempt1を`asm.record_human_approval()`で承認記録し、Assembly完了
(305.135秒、peak 0.89571、clipping False)。Fable受入判定:
**`PRODUCTION_WIRED`(Phase 1スコープ)**。スコープ注記: B-Family(Voices)の
音声Production経路(既存承認済み記事→Voice A/B/Narrator固定・Tension
slot・Key Phrase位置・Comment 1〜4確定版Contract・A-Family同規約の安全
機構→Assembly)のみで、記事生成(Writer)・Key Phrase選定は範囲外、一人称
"I"の機械保証はPhase 2保留。あわせてOPEN-121既存15件flagは試聴確認により
全件false positiveと確定した(方式D Production閾値は無変更)。別管理IDの
2件のTrialを統合: **Trial A**(`TTS-REPETITION-QA-INTENTIONAL-REPEAT-
FALSE-POSITIVE-TRIAL-01`、OPEN-127)は共有module`_normalize_tokens()`の
em dashトークナイズ不備によるfalse positiveを特定し、候補1a(em dashを
空白へ置換する1行修正)がTP10/10・FP0/4・回帰12/12で`VALIDATED`、
Production配線は未実装・`USER_DECISION_REQUIRED`。**Trial B**
(`OPEN-121-METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01`、OPEN-128)は方式D
誤flag低減の4候補を検証し、候補c(局所ASR語句一致度による二段確認)が
TP8/8・FP0/15で`VALIDATED`(推奨)、候補a/b/dはいずれも`REJECTED`、
Production配線は未実装・`USER_DECISION_REQUIRED`。本ファイル
[Production正式仕様]への実質的なコード配線・仕様変更はゼロ(SSOT状態
更新・Fable受入判定のみ、Trial候補の配線は含まない)。詳細はDECISION_
LOG.md `PM-CLOSEOUT-CONSOLIDATION-11`エントリ、
`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md`、
`TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01_REPORT.md`、
`OPEN-121-METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01_REPORT.md`参照)。
**最終更新: 2026-09-08(第5弾、PM-CLOSEOUT-CONSOLIDATION-09、Phase 1修正結果・
OPEN-121 flag23件試聴artifact・OPEN-124分類の統合)**: B-Family Production
Path Phase 1(`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01`修正指示
1回目対応)をLane B新規4ファイルで実装済み(共有ファイル無変更、単体テスト14件・
project-wide regression既知3件failureのみでPASS)。`phase1_02`(OPEN-121/122
安全機構適用版)は`point_two`(Voice B)が著者意図の反復句を共有module
`er011_open121_repetition_qa_production_01.py`のem dash tokenizationが誤検出し
flagged=Trueを3回連続でAssembly`GATE_BLOCKED`となったため、
`APPROVED_FOR_PRODUCTION`未配線のまま受入保留(`USER_DECISION_REQUIRED`、
選択肢a/b/c)。OPEN-121方式D flag対象23件の標準フォーマット試聴artifact
(`er011_output/method_d_flag23_review_01/player.html`)を作成し証拠ベース一次
分類(真の重複8/誤flag可能性高14/判断困難1)を提示、最終分類はユーザー試聴待ち。
OPEN-124未追跡285件(実ファイル1,003件・約2,870MB)の分類を実施(削除・commit・
`.gitignore`変更は一切なし)、新規`USER_DECISION_REQUIRED`候補4点(`.gitignore`
方針統一/削除候補/commit漏れ候補commit可否/Trial evidence削除可否)を提示。
本ファイル[Production正式仕様]への実質的なコード配線・仕様変更はゼロ(SSOT状態
更新・分類のみ)。詳細はDECISION_LOG.md `PM-CLOSEOUT-CONSOLIDATION-09`エントリ、
`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md`、
`OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01_REPORT.md`、
`OPEN-124-UNTRACKED-FILES-CLASSIFICATION-01_REPORT.md`参照)。**最終更新:
2026-09-08(第4弾、PM-CLOSEOUT-CONSOLIDATION-08、ユーザーが2026-09-08にPM-CLOSEOUT-CONSOLIDATION-07報告後さらに追加で決定した6点[1. Theme2 A2 rerun_04最終承認・Theme2完成音声(A2/B1)close/2. OPEN-121方式D閾値現状維持・flag対象23件試聴確認方針/3. OPEN-126 close/4. OPEN-124整理タスク起票(分類のみ、削除なし)/5. OPEN-125低優先保留/6. OPEN-119・OPEN-122・OPEN-118・OPEN-112本体残件は据え置き]を記録した。**1**: Theme 2 A2 rerun_04(`er011_output/open112_trend_theme2_b_final_audio_rerun_04/a2/`、24.1%→about 24%版)をユーザーが試聴し「音声・修正版とも問題なし」として最終承認(`APPROVED_FOR_PRODUCTION`、rerun_02のa2は置き換え、rerun_02自体は履歴として保持)。これによりTheme 2 A2/B1完成音声(OPEN-112行の対象)はclose、OPEN-112本体残件(Discovery 4-layer・Engagement根底指示・News Ledger自動Research経由)は据え置きのまま維持(状態を「Theme 2音声: CLOSED / 本体残件: DEFERRED」と分離表現)。**2**: OPEN-121の方式D Production既定閾値(run≥0.12秒)は現状維持(変更しない)。既存flag対象23件を試聴確認し3分類(真の重複/正常音声への誤flag/判断困難)に整理する方針とし、自動再生成・閾値変更はしない(試聴artifactは別タスク`OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01`で作成中)。**3**: OPEN-126(A2/B1独立Editorによる表現差)は新たな対策を導入せずclose。**4**: OPEN-124(古い未追跡ファイル)は整理タスク(`OPEN-124-UNTRACKED-FILES-CLASSIFICATION-01`)を起票、分類・正体確認のみ・削除は今回行わずnon-blocking(削除等が必要な場合は別途`USER_DECISION_REQUIRED`)。**5**: OPEN-125(TTS Retry分類の見出しラベル誤区分)は低優先で保留、Trial着手せず維持。**6**: OPEN-119(Key Phrase経路以外への適用範囲拡大)・OPEN-122(Key Phrase経路等への適用範囲拡大)・OPEN-118(gloss LLM QA新設)・OPEN-112本体残件は、いずれも追加Trial・Production変更なしで据え置き。本ファイル[Production正式仕様]への実質的なコード配線・仕様変更はゼロ(SSOT状態更新・Artifact承認のみ)。詳細はDECISION_LOG.md `PM-CLOSEOUT-CONSOLIDATION-08`エントリ参照)。**最終更新: 2026-09-08(第3弾、PM-CLOSEOUT-CONSOLIDATION-07、ユーザーが2026-09-08に追加で決定した5点[1. Theme2 B1 rerun_04正式採用・rerun_03置き換え/2. B-Family Phase1先行承認(実装は別タスクで進行中、本エントリでは触れない)/3. Theme2 A2「24.1%」は共通配線+実データ圧縮確認により仕様問題としてclose(A2専用patchなし)、B1同方式でArtifact最小修正/4. 過去完成物への遡及修正は不要/5. OPEN-126は24.1%問題と独立な論点として維持]を記録した。**1**: Theme 2 B1完成音声はrerun_04(`er011_output/open112_trend_theme2_b_final_audio_rerun_04/b1b/`)を正式採用しrerun_03を置き換える(rerun_03は削除せず履歴として保持)。**3**: `run_lossless_editor()`がlevel/genre引数を持たない共通コードであることをコード根拠(呼び出しチェーン含む)で確認し、実際に完成音声化されたA2草稿へ現行Production Editorを無変更のまま1回適用して「24.1%」→「about 24%」への圧縮を実データ(¥0.26)で確認、**仕様問題としてclose**(A2専用patch・A2専用ルールは追加せず)。あわせてB1 rerun_04と同一手順でA2側もArtifact最小修正を実施(`.../rerun_04/a2/`、対象1segment[`full_story_part1`]のみ再生成・他69ファイルはsha256 byte-for-byte reuse、player_a2.html生成、Gate 7全PASS)、到達Status=`USER_FINAL_AUDIO_REVIEW_REQUIRED`(A2は試聴未実施)。**4**: Health「8.1年」等の過去完成物への遡及修正は不要、そのまま保持。**5**: OPEN-126-INDEPENDENCE-REEVALUATION-01(read-only)により、強化配線後・同一記事・同一Fact(24.3%)でB1/A2の粒度が割れる実データ1件を確認し、24.1%問題(配線前の古いArtifact残存)とは独立な論点として維持と判定(選択肢1/2/3のUSER_DECISION_REQUIREDは変更なし)。本ファイル[Production正式仕様]への実質的なコード配線・仕様変更はいずれもゼロ(Artifact修正・登録判断のみ)。詳細はDECISION_LOG.md `PM-CLOSEOUT-CONSOLIDATION-07`エントリ、`OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01_REPORT.md`、`OPEN-126-INDEPENDENCE-REEVALUATION-01_REPORT.md`参照)。2026-09-08(第2弾、PM-CLOSEOUT-CONSOLIDATION-06、ユーザーが2026-09-08に追加で決定した4点[A. Voices Comment Contract(1〜4)採用+"the question"禁止句1行追加/B. B-Family Production経路の設計案作成のみ(実装なし)/C. Theme 2 B1 Numeric Precision(OPEN-112)は選択肢A採用(決定的置換、対象2segmentのみTTS再生成+再Assembly)/D. 遡及点検起票・レベル間数字粒度差論点の登録のみ]を記録した。**A**: Voices Comment Contract全体を`APPROVED_FOR_PRODUCTION`(未配線)、"the question"漏出対策の禁止句をComment 1 Contractへ追加しGate 1`VALIDATED`(n=3漏出0/3)、Production wiringは未実施(詳細はOPEN_ITEMS.md OPEN-120行、`EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11_REPORT.md`)。**B**: B-Family Production経路の設計案(Phase 1 Lane B内/Phase 2 Lane A共有Writer後方互換引数)を作成したが実装ゼロ(`EDITORIAL-B-FAMILY-PRODUCTION-PATH-DESIGN-01_REPORT.md`)。同Reportは、直前(第1弾)のこの節にあった「(1)は既存共有Production関数`point_headings.generate()`が満たす」という記述がNarrator見出し部分のみ正しく、Voice A/B本文側の声指定はこの関数の対象外である点を**要修正候補として指摘した(本タスクでは本文修正せず、設計案レビュー待ちとしてこの注記のみ追加)**。**C**: OPEN-112 Theme 2 B1の"25.2%"/"44.7%"を決定的置換し対象2segmentのみ再TTS・再Assembly(`er011_output/open112_trend_theme2_b_final_audio_rerun_04/`、duration339.594秒・peak0.75511・clipping false)、標準フォーマットplayer.html Gate 7全PASS、到達Status=`USER_FINAL_AUDIO_REVIEW_REQUIRED`(OPEN_ITEMS.md OPEN-112行、`OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04_REPORT.md`)。**D**: 完成episode 8本の読み取り専用遡及点検でTheme 2 A2「24.1%」の新規残存を発見(`NUMERIC-PRECISION-RETROACTIVE-AUDIT-01_REPORT.md`)、レベル間数字粒度差論点は新規OPEN-126へ登録のみ(実装せず)。本ファイル[Production正式仕様]への実質的なコード配線・仕様変更はいずれもゼロ。詳細はDECISION_LOG.md `PM-CLOSEOUT-CONSOLIDATION-06`エントリ参照)。2026-09-08(PM-CLOSEOUT-CONSOLIDATION-05、ユーザーが2026-09-08にB-Family[Voices]のTrial-09完成episodeを試聴し、`APPROVED_FOR_PRODUCTION`と正式決定した4項目[(1) Voice A=Algieba/Voice B=Erinome/Narrator見出し=Aoede固定、(2) Tension slot「Where the Difference Comes From」の正式構造への追加、(3) Key Phrase位置=Preview直後(現状維持)、(4) Voice A/Bの一人称"I"記述]を記録した。ただし配線先となるB-Family Production正式経路自体が現時点で一切存在しない(Trial番号付きファイルのみ)ため、本ファイル[Production正式仕様]への実質的なコード配線・仕様変更はゼロ(配線待ち、Production経路未設計。(1)は既存共有Production関数`point_headings.generate()`がすでに満たすため追加配線不要、(3)は変更対象なし、(2)はLane B側ファイルのみで技術的に実装可能だが呼び出し元となるB-Family Production runtimeが不在のため未実装、(4)はLane A共有Writerへのeditorial Type Module導入が前提のため未着手)。採用4項目はGate 3を満たし`PRODUCTION_WIRED`になるまでcloseしない。→PRODUCTION_WIRED(Phase 1、2026-09-08、PM-CLOSEOUT-CONSOLIDATION-11、`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01`のPhase 1スコープ[音声Production経路のみ]でFable受入。一人称"I"の機械保証はPhase 2保留のため4項目全体のcloseではない)。詳細はOPEN_ITEMS.md OPEN-120行、DECISION_LOG.md `PM-CLOSEOUT-CONSOLIDATION-05`エントリ、`EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FIX-TRIAL-10_REPORT.md`参照)。2026-09-07(OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01、ユーザーが2026-09-07に`APPROVED_FOR_PRODUCTION`と正式決定した範囲(英語ASR照合経路全体、A2/B1本文に限定しないKey Phrase英語経路を含む共通正規化層)で、標準contraction展開(否定保持のみ、"want to"⇔"wanna"等の口語的縮約[方式iv]は不採用)をOPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01_REPORT.md §13(VALIDATED)から`er006_preprod_hardening_01_validation.py::classify_asr_match()`へ配線した(既存分類本体は`_classify_asr_match_core()`として無変更のまま温存し、外側の薄いラッパーとして追加、`normalize_text()`/`tokenize()`は無変更、新規opt-inフラグは追加せず全既存呼び出し元へ共通適用)。Runtime evidence: 既知false reject(Trial-08 P3 point_two、3回STOPPED実例)を実Production関数で3/3救済、既存Regression fixture(POSITIVE29+AMBIGUOUS2+NEGATIVE28)無回帰、Key Phrase英語経路(実preserved KP音声5件+合成2件)で想定外挙動0件、wanna系(OPEN-122 Trial-01実データ)は非救済のまま維持確認、新規単体テスト19件PASS、`run_project_regression.py`無回帰(collected=2157・failed=3[既知の無関係failure]・errors=0)。Git操作は未実施(Fableが統合commit、`PRODUCTION_WIRED`の正式宣言はcommit後)。詳細は「Audio Production Pipeline」節「Transcript Style Normalization」行、OPEN_ITEMS.md OPEN-123行、DECISION_LOG.md該当エントリ、`OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01_REPORT.md`参照)。2026-09-07(OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01、ユーザーが2026-09-07に`APPROVED_FOR_PRODUCTION`と正式決定した範囲(A2/B1英語本文segment[full_story_part1/2・point_one・point_two]のみ)で、TTS反復幻聴検知(Trial-01/02でVALIDATEDとなった方式A[n-gram句・文単位反復検知、min_words>=3、canonical crosscheck付き]+方式D[スペクトルself-similarity、min_lag=1.0秒、top-k類似度優先]+方式D'[方式Dと同一の対数スペクトル自己相関primitiveを共有する派生プロファイル、lag0.5〜2.0秒・run長優先、B1 FSP1型false start検知])を新規[er011_open121_repetition_qa_production_01.py](er011_open121_repetition_qa_production_01.py)へ移植し、新規opt-inフラグ`enable_repetition_qa`(既定False)で`er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()`・`er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback()`・`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin()`・`er003_v1_n3_01_tts_generate.py`(A2/B1本文4segmentループのみ)へ配線した。方式D・D'は同一の類似度行列を1回だけ計算して2プロファイルで再利用する設計へ統合(検知ロジック自体は無変更)。既存`er008_disfluency_qa_18.apply_disfluency_gate()`と同一のANDゲートパターンで接続し、新規retry・新規Cost Guardは追加していない。**Runtime evidence**: 既知陽性3件(Theme2 A2 Point Two/In One Line[保全済attempt]・B1 FSP1 false start[保全済])をTP3/3で検知(Point Two/In One Lineは方式A+D、B1 FSP1は方式D'のみが検知、想定通りの役割分担)、Trial-02陰性代表EN10件をFP0/10で確認、Theme2 B1`full_story_part1`をProduction関数でStandard同期実再生成しstatus=OK・repetition_qa_checked=True・flagged=False(既存のPASS音声・player.htmlは上書きせず新ディレクトリへ保存、episode再Assemblyは未実施)、cost実測¥3.64。既存回帰(`run_project_regression.py`、collected=2138・failed=3[既知の無関係failure]・errors=0)・新規単体テスト26件PASS。**未配線**: gap<0.5秒の即座の言い直し(Trial-01方式C-v2)はOPEN_ITEMS.md OPEN-121行へ追跡項目として記録(今回は実装しない)。**Git操作は未実施**(Fableが統合commit、`PRODUCTION_WIRED`の正式宣言はcommit後)。詳細は「Audio Production Pipeline」節「TTS Repetition/False Start QA」行、OPEN_ITEMS.md OPEN-121行、DECISION_LOG.md該当エントリ、`OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01_REPORT.md`参照)。2026-09-07(OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01、ユーザーが2026-09-07に`APPROVED_FOR_PRODUCTION`と正式決定した範囲(A2/B1英語本文segment[full_story_part1/2・point_one・point_two]のみ)で、Connected Speech Equivalence Layer(Trial-01/02でVALIDATED、音韻環境カテゴリA〜G+独立ASR corroboration)を`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail()`へ新規opt-inフラグ`enable_connected_speech_equivalence_layer`(既定False)で配線した。既存3パターンValidatorのUNCLASSIFIED fallthrough後段のみで発火し、Key Phrase・日本語・他segmentへは一切波及しない(既存`enable_non_latin_cascade`[OPEN-119]と同じ設計パターン)。**Runtime evidence(Standard同期、実API、¥3.34)**: A2 Flagship("showed strong"保全音声)がACCEPT(カテゴリA/B/C、corroboration 2/2)、B1実本文1件は通常NORMALIZED_MATCHでLayer不発火・Trial-01実音声による合成fallthroughはACCEPT、敵対的陰性対照2件(N1・T2N4)は非accept。既存回帰(`run_project_regression.py`、collected=2112・failed=3[既知の無関係failure]・errors=0)・関連単体テスト計142件・新規16件、いずれもPASS(新規kwargs追加に伴い既存2ファイルのmock signatureを更新)。**Git操作は未実施**(Lane B commit権保持中のためFableが統合commit、`PRODUCTION_WIRED`の正式宣言はcommit後)。詳細は「Audio Production Pipeline」節「Connected Speech Equivalence Layer」行、OPEN_ITEMS.md OPEN-122行、DECISION_LOG.md該当エントリ、`OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01_REPORT.md`参照)。2026-09-07(ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01、ユーザーが2026-09-07に`APPROVED_FOR_PRODUCTION`と正式決定した2件(B1 Preview分量原則[2〜3文程度の短い導入、旧Preview比の相対指定・hard word-count gate・固定文数は含めない]・Numeric Precision共通原則[聞き取りやすさを優先し意味を損なわない範囲では概数を基本とする、精度保持は意味がある場合のみ、A2/B1/B2共通でレベル別ルールにはしない])を、B1 Preview Prompt(`er003_v1_b1_scaffold_01_generate.py::PREVIEW_ROLE`)・Evidence Compression Editor(`er003_v1_n3_01_evidence_compression_editor.py`)・Writer共通Prompt(`er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`「Spoken-first原則(数字の扱い)」C項)へ`PRODUCTION_WIRED`まで配線した。Theme 2 B1/A2でProduction正式経路のRuntime evidenceを取得(Preview: 旧4文/67語/405字→新2文/46語/253字、A2 Preview従来どおり2文/85字。Numeric: 25.2%→about 25%・44.7%→about 45%等の概数化、Ledger Deviation Checker=両レベル`LEDGER_COMPLIANT`)。既存回帰(`run_project_regression.py`、collected=2110、failed=3は既知の無関係failureとgit stashで切り分け確認済み)・新規単体テストとも問題なし。詳細は「Cross-level仕様」節「Preview原則」行・「Evidence Compression Editor(方式C)追加ルール」行、DECISION_LOG.md該当エントリ、`ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01_REPORT.md`参照)。2026-09-04(ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23、ユーザー正式採用済みの2点(A2 `tight_speech_only()` removal・Key Phrase trim safety margin 0.30秒)を量産Production仕様として恒久的に配線した(いずれも`PRODUCTION_WIRED`)。**(1) A2 tight_speech_only() removal**: `er003_v1_n3_01_assemble.py::load_a2_sources()`から、Key Phrase英語音声への`tight_speech_only()`再crop呼び出しを削除(B1は元々未使用のため無変更)。初回Assembly・retry/reassembly・regenerationは全てこの唯一の関数を経由するため、この1箇所の変更で正式後続経路すべてに整合して反映される(単体テストで固定)。**(2) Key Phrase trim margin 0.30秒のcache identity保証**: `er006_audio_cost_pilot_02_shared_narration.py::ensure_key_phrase_english_component()`のMasterAudioKeyへ`KEY_PHRASE_TRIM_POLICY_VERSION`("v2_margin030")を追加。旧0.20秒時代([2026-08-17〜09-02]生成)の既存Key Phrase Master資産99件すべてが、versioningなしでは新規リクエストへ誤ってcache hitしうる状態だったことを確認し、version文字列を含めることで解消(新旧で異なるmaster_audio_idとなり自然にcache miss、正しく0.30秒で再生成される)。No.18 Key Phrase 5「be powered off」の既承認0.30秒資産は新versionキーへ移行済み(sha256一致、無駄な再TTSなし)。**runtime evidence**: 新規Key Phraseテキストでの実Production経路呼び出しで`trailing_margin_retained_seconds=0.3`を確認。No.18 A2をコード変更後の`stage_assemble_a2()`(monkeypatch不使用)で再Assemblyし、ユーザー承認済み21R候補音声とsha256完全一致(byte-for-byte同一、351.824秒・peak 0.93346・clipping無し)を確認、Trial-15条件での候補音声と正式Production挙動が完全に一致することを実証した。単体テスト12件PASS、既存regressionにも影響なし。詳細はDECISION_LOG.md該当項目参照)。2026-09-04(ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R、ユーザーが正式採用したEvidence Compression拡張仕様「Pattern A(Representative Metric + Supporting Trend)+ Listener-Friendly Numeric Precision」を、既存Evidence Compression Editor[方式C]のPromptへProduction正式配線した(`PRODUCTION_WIRED`、単体テスト9件PASS、既存regressionにも影響なし)。No.18 A2/B1を実Production経路(Writerは既存承認済み出力を再利用、Evidence Compression以降は全て実関数)で再生成し、両レベルでPattern A+Precisionの実発火(99.71/108.95→about 100/about 109、processing speedはtrend表現化)・Ledger Deviation Check=LEDGER_COMPLIANT(両レベル0件)を確認。A2初回はEditorが選んだ研究者氏名がASR誤認識を誘発しHuman Review Lockへ到達したが、実Production経路を再実行(Editorの非決定性により氏名を一般化する変種を取得)することで解消し、Fact Checker=PASS・Ledger=LEDGER_COMPLIANT・Directional Fact Precheck=PASSで再生成に成功した(丸め対象の数値部分は初回・再試行とも一貫して正確に発話されていたことを確認済み)。既存の再利用可能な音声パーツ(Support/Key Phrase/変更のないsegment)はテキスト一致を確認したうえでbyte-for-byte再利用し、実際にテキストが変わったsegmentのみ再TTSした。A2最終候補音声は、ユーザー試聴承認済みのTrial-15条件(tight_speech_only()の一時的な恒等関数化)で組み立てた(Production正式コードは無変更、0.30秒trim marginのKey Phrase 5資産をsha256一致で確認)。A2 351.824秒・B1 357.964秒、いずれもclipping無し。A2は`FINAL CANDIDATE READY FOR USER LISTENING`(tight_speech_only removal自体はユーザー試聴・正式承認まで`PRODUCTION_WIRED`へ昇格しない)。Pattern B/Cは`DEFERRED CANDIDATE / NOT REJECTED`のまま。詳細はDECISION_LOG.md該当項目参照)。2026-09-03(ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08、ユーザー正式決定によりOPEN-107のEnding-Clarity fallbackをProductionから撤回し(`WITHDRAWN`)、B1 Connected Speech Validator(ASR差分をconnected speech[歯擦音連続/破裂音連続/再分節]として説明可能なら誤発音と扱わない)とA2 Reading Resolver(辞書候補+限定LLM選択による読み解決、A2専用)を正式配線した(`PRODUCTION_WIRED`)。Dangling Reference Check完了(Ending-Clarity fallbackはProduction経路から一切参照されない、historical recordとしてファイルは保持)。既存regression 57+35件全PASS、新規regression 15件全PASS。No.18 A2/B1 Audio Stageを新仕様下で最初から通し直し、OPEN-110の対象2segment(B1 `comment_2`/`comment_3`)・OPEN-111の対象segment(A2 `comment_1`)がいずれも実際のProduction TTS/ASR出力に対して新Validatorで解決することを確認、**No.18 A2/B1が今回初めて両レベルとも完成**(B1 351.324秒・A2 347.338秒、いずれもclipping無し)。詳細はDECISION_LOG.md該当項目参照)。2026-09-02(ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04、「Ending-Clarity Fallback」行を更新: 検出ロジックの一般化[y→ies不規則複数形・複数語replace diffの語単位分解]とB1 Comment segment[`voice01.generate_charon_english`経路]への配線拡張を行い[regression 20件PASS]、実Production経路での初めての実発火をB1`comment_2`で直接確認(`PRODUCTION_WIRED`、前回session caveat解消)。「Cross-level仕様」節へ新規行「Cross-Level Consistency Check」を追加(A2/B1いずれかの仕様変更時、もう一方への影響確認を必須化するSSOT運用ルール)。詳細はDECISION_LOG.md該当項目参照)。2026-09-02(ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03、ユーザー正式承認によりOPEN-107のEnding-Clarity fallback[通常segmentは変更せず、通常retry後も語尾脱落NGが継続したsegmentだけへ適用]をB1 News本文5segmentのProduction正式経路へ配線([Audio Production Pipeline]節「Ending-Clarity Fallback」行、`PRODUCTION_WIRED`、regression 13件PASS)。No.18 B1BのPoint One本文2文をユーザー指定の個別文言へ差し替え、既存公式QA工程[Point Overlap/Value QA・Fact Checker・Ledger Deviation・Directional Fact Precheck]を再実行し全てnon-blockingで通過、Support/Key Phraseも新article.mdから再生成しPASS。No.18 Audio Stage(同期TTS)を実行した結果、B1は13segment中11件・A2は14segment中13件がOKだったが、B1 `comment_2`/`comment_3`(2回のretryでも解消しない新規TTS content-accuracy失敗、OPEN-110として新規記録)、A2 `full_story_part1`(STOPPED)がAudio Validation Gateにより正しくepisode assemblyをblockした。加えて、A2記事本文がLedger精密化前の記述(Pewの「約4割」丸め表現・出典で確認できない"hard-to-resist habit"という評価)を含んだままであることを新たに発見し(OPEN-109として新規記録)、A2 Audioの最終化は保留した。詳細はDECISION_LOG.md該当項目参照)。2026-09-02(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01、No.18で発見された3件の問題(Key Phraseの文脈依存人称表現・Key Phrase 5件相互の意味重複・PointがOverlap QAをPASSしても新しい価値を持たない場合がある)を、個別のNo.18記事修正ではなく汎用Production仕様として改善した。**(1) Key Phrase人称代名詞・所有格の一般化**: canonicalizationへ`generalize_person_dependent_reference`カテゴリ・`qa_person_reference_generalized`QAフィールドを追加(閉じた語彙集合による1対1置換のみ許可)。**(2) Key Phrase Set Redundancy QA**: 新規モジュール`er011_key_phrase_set_redundancy_qa_01.py`、5件相互の意味・使用場面・文法/構文学習価値・記事内概念の4観点重複判定、NG時は選定からやり直す(最大2回)。**(3) Point Role Planning + Point Value QA**: 新規モジュール`er011_point_role_value_planning_01.py`、Point生成前にrole/new_listener_takeaway/evidence_anchor/why_it_matters等を計画させ、生成後に6項目(留保のみ構成でない・Full Story言い換えでない・他方のPoint言い換えでない・だから何なのか説明・記事固有・新価値追加)を判定、既存のDiagnostic Full Retryへ統合。Point One対Point Twoのlexical overlap検査も追加。全て`PRODUCTION_WIRED`、単体テスト125件PASS。No.18記事本文への個別ハードコードは一切なし。改善後の仕様からNo.18 A2/B1を実際に再生成し(`pool_n18_notifications_specfix_v2`)、B1B初回候補でPoint Value QAが実際にNGを検出しretryで解消する実例を確認(旧仕様ではlexical overlap 0.379<0.40のため見逃されていたはず)。OPEN-107(`opened`のTTS誤発音)はProductionと分離したDiagnostic Trial(`er011_open107_opened_tts_diagnostic_trial_01.py`)で原因範囲を診断し、失敗が特定の語・フレーズではなく「完全な一文としての文レベルprosody」に起因すること(短い断片は12/12正解、完全な一文は6件中2件で誤発音)を実データで確認したが、Production仕様への反映はユーザー未承認のためUSER_DECISION_REQUIREDのまま。詳細はDECISION_LOG.md該当項目参照)。2026-09-01(ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22、ユーザー正式決定によりKey Phrase英語Component生成のretry構成を「標準経路[ENGLISH_STYLE_PREFIX]→minimal fallback、合計上限3回共有」から「Minimal instruction[Primary、最大2回]→English language lock付きMinimal[Fallback、最大2回]、合計最大4回」へ全面置き換え、`er003_v1_repro01_main_generate.py::generate_key_phrase_component_verified()`をProduction正式初回経路として再実装した[`PRODUCTION_WIRED`、Key Phrase英語Componentのみに適用、他segmentのTTS retry上限3回は無変更]。`default`はこの一般仕様から個別例外として分離し、OPEN-103は`DEFERRED / NON-BLOCKING`[No.9では個別asset候補をユーザー提示、後述]。詳細は「Key Phrase」節・DECISION_LOG.md参照)。2026-09-01(ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19、「Human Review Cost Guard(Review Lock機構)」行にOPEN-105[guarded_generateネスト二重会計バグ]の修正を追記、`PRODUCTION_WIRED`のまま維持。Key Phrase英語音声のMinimal instruction Trial[OPEN-103]は実施したがProduction仕様へは反映していない[ユーザー承認前のため、DECISION_LOG.md参照])。2026-09-01(ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12、「Fact Safety(共通)」行を改定し、Fact Checker `verdict="REVIEW_REQUIRED"`を原則non-blocking advisoryとする運用をユーザー正式決定・Production実装[`er003_v1_n3_01_articles_generate.py::run_one_pattern()`に`verdict=="FAIL"`時のみblockingとする分岐を追加、従来はFAILであってもstatus判定に一切使われていなかった実装漏れを修正]。No.9 Point解説の数字羅列問題は診断のみ実施しCase 2 SPEC_TOO_WEAKと判定[USER_DECISION_REQUIRED、OPEN-100参照]、新仕様は未実装)。2026-08-29(ER-008-N8-CLOSEOUT-GOVERNANCE-25、Fact Checker retry capは既存実装のまま安全と確認、Production全体retry/regenerate/polling上限の横断監査を実施し発見した1件の不整合[TTS日本語分岐のcapハードコード]を修正、No.8のPoint OneをHuman Approved exceptionとして正式記録、cost報告を円ベース[1USD=160円]へ統一、今後の試聴Artifactへ全script掲載を標準化。ER-008-N8-FINAL-CLOSEOUT-24、地名/施設名CompressionをNo.8へ正式反映・再Assemble完了、Writer Point Balance promptを言い換え重複禁止で強化[実API A/B比較で効果確認]、共有cost計算モジュールの単価バグ修正、A2 In One Line速度は現状維持で確定、Stephen Reicher発音はユーザー確認によりPASS確定)**

**追記(2026-09-12、PM-CLOSEOUT-CONSOLIDATION-95-OPEN-121-SYMMETRIC-NORMALIZATION-
WIRING-TRIAL-12-A2-ASSEMBLY-AND-SSOT、OPEN-121対称正規化Production配線[ハイフン境界+
0〜999拡張])**: `_normalize_tokens()`(canonical側)・`_normalize_token_numeric_equiv()`
(ASR側)を、(i)ハイフン境界の対称正規化(em/en dashは常に空白、ハイフンは英字/数字が
隣接する境界のみ空白、digit-digit境界["10-15"等の範囲表記]は除外)+(ii)数詞↔算用数字の
同値化を2〜12専用辞書から0〜999へ拡張(Production既承認・稼働中のASR Validator実装
[`er006_preprod_hardening_01_validation.py`の`_ONES`/`_TENS`/`_words_to_number`]を
再利用、重複実装なし)、へ置き換えた。判定閾値(`canonical_repeat_count>=2`)・方式D/D'の
閾値自体は無変更。%/percent同値化・序数(first〜ninety-ninth)は引き続き対象外。ユーザー
`APPROVED_FOR_PRODUCTION`(2026-09-12)、実装・回帰テスト67件PASS済み(`OPEN-121-
REPETITION-QA-SYMMETRIC-NORMALIZATION-PRODUCTION-WIRING-01_REPORT.md`)。続く本
タスクで、Trial-12 A2既存take(`full_story_part1`、標準attempt1)を、ユーザー承認根拠
(DECISION_LOG PM-CLOSEOUT-CONSOLIDATION-94エントリ、Gate3最低限確認14項目
「Trial-12 A2既存takeの¥0再判定/PASS時のA2 Assembly/標準player更新」)に基づき
`review_lock_state.json`をRESOLVED/OKへ、`tts_generation_results.json`をOKへ更新した
(¥0、実際のattempt1音声へ`evaluate_repetition_qa()`を再実行し独立に確認済み)。**A2
Assembly(`stage_assemble_a2`)は未完了**: 実行した結果、A2必須6% slowdown post-process
未適用のため`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`(`full_story_part1=VALIDATED
(MISSING_MANDATORY_A2_SLOWDOWN)`)で正しくブロックされることを実データで確認した。
既存Production関数`apply_a2_slowdown_postprocess()`はtime-stretch自体はローカル無料
(ffmpeg)だが、内蔵の安全再検証としてPrimary ASR(`er006_asr_provider_routing_01.
transcribe`、有料)を1回呼び出す設計であり、本タスクの¥0/API呼び出し禁止制約と衝突する
ため独自判断で省略・代替せず`USER_DECISION_REQUIRED`としてSTOPした。A2 Assembly・
標準player再生成・`PRODUCTION_WIRED`宣言はいずれも未実施(詳細はOPEN_ITEMS.md
OPEN-121行、DECISION_LOG.md該当エントリ参照)。

**追記(2026-09-12、PM-CLOSEOUT-CONSOLIDATION-96、Gate 3完了・`PRODUCTION_WIRED`)**:
Fable許可(小額・上限¥50、内蔵Primary ASR再検証1回のみ、¥0代替・安全再検証の省略は
不可)に基づき、既存Production関数`apply_a2_slowdown_postprocess()`(無変更)をRESOLVED
採用済みの`full_story_part1`へ適用した(6% time-stretch、実測比率1.0595、内蔵Primary ASR
再検証PASS=`NORMALIZED_MATCH`、実測費用¥1未満相当)。post-slowdown音声への
`evaluate_repetition_qa()`再判定(ローカルfaster-whisper、¥0)でもflagged=False
(canon_count=2)を確認し、対称正規化が実際にA2 Assemblyへ渡る最終音声上で発火することを
実証した。続けて`stage_assemble_a2()`を実行し、Gate OFF/opt-in ON両経路とも**PASS**
(duration=327.24秒、peak=0.89889、clipping=False)。標準player
(`er011_wake_before_alarm_trial12_std_player_01.py`)を完成episode audio付きへ更新した。
Gate 3の13項目チェックリストが全て充足したため、対称正規化(ハイフン境界+数詞0〜999拡張)を
**`PRODUCTION_WIRED`**とする。詳細はOPEN_ITEMS.md OPEN-121行、DECISION_LOG.md
`PM-CLOSEOUT-CONSOLIDATION-96`エントリ参照。

**2026-09-06(KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01、ユーザーが
2026-09-06に`APPROVED_FOR_PRODUCTION`と正式決定した2件をProduction正式
初回経路へ`PRODUCTION_WIRED`まで配線した。**(1) Key Phrase日本語gloss
表示用/TTS用分離**: `keywords_canonicalized.json`のschemaへ新フィールド
`japanese_gloss_tts`を追加(`er003_key_words_canonicalization.py::
merge_canonicalization_result()`が`convert_display_gloss_to_tts_text()`
で決定論的に導出、LLM不使用)。表示用`japanese_gloss`は辞書的な
「～」「〜」表記を許容するよう選定Prompt規約Bのgloss側禁止を撤回し
(`WITHDRAWN`、「…」等その他placeholder記号禁止・key_phrase側規約は維持)、
TTS呼び出し(`er003_v1_n3_01_tts_generate.py`)は新関数
`resolve_key_phrase_ja_gloss_tts()`経由で必ず`japanese_gloss_tts`を使う
(表示用フィールドはTTSへ渡らない、旧artifactはfallbackで規則導出)。
**(2) 数値placeholder型の回避**: 「～％」のように数値を補わないと成立
しない句・glossはTTS側で変換して救済せず、選定Prompt側で回避誘導する
1文を追加した。いずれも既存のplaceholder gate・review_lock・TTS retry
cascade・Master Audio Store cache identityとの整合を確認済み(ゲートは
弱めていない)。Theme 2 B1(Trial-12記事)でProduction正式経路のRuntime
evidenceを取得(「なになに」変換の実発火・数値placeholder型のgate
ブロックともに実証、TTS Standard同期・model_id記録)。詳細はDECISION_
LOG.md該当項目・`KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01_
REPORT.md`参照)**

**2026-09-06(KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01、ユーザーが
2026-09-06に選択肢a(選定Prompt1〜2文追加+Human Review基準1文追加、
LLM追加QA・Validator新設・blacklist・過去397件の再生成は不採用)を
`APPROVED_FOR_PRODUCTION`と正式決定した仕様を`PRODUCTION_WIRED`まで
配線した(**問題2**)。診断(`KEYPHRASE-JA-GLOSS-NATURALNESS-DIAGNOSTIC-
01_REPORT.md`)は、タスク依頼の前提「new normal→新常態」が実データと
異なる(実際のgloss確定値は一貫して「新しい当たり前」)ことを確認した
上で、選定Prompt(`b1_p2_keywords_l_prompt_template.txt`、A2/B1共有)が
「短く自然な日本語グロス」という一語以外に学習者向け平易さ・直訳調
回避の具体基準を持たず、Validator・Redundancy QA・Human Reviewの
いずれも訳語の自然さを判定しない構造的空白(原因分類A+C+D)を発見した。
選定Promptの既存「短く自然な日本語グロス」文の直後へ「日本語グロスは、
辞書的に正しいだけでなく、日本人の英語学習者が聞いてすぐ意味を理解
できる、自然で平易な現代日本語にしてください。直訳調や、「常態」
「是正」のような過度に硬い報道語・漢語、一般的な学習者には伝わりにくい
表現は避けてください。」の2文を追加(既存の規約A/B・数値placeholder
回避文は無変更)、CURRENT_SPEC.md「QA / Human Review」節へ日本語gloss
自然さの人間判断基準1項目を追加した(blacklist化せず)。単体テスト1件
追加(`er003_test_b1_p2.py`、49件全PASS)。Runtime evidence(Theme 2
B1・A2各1回、Production正式選定→canonicalization→Redundancy QA経路、
`er011_output/kp_ja_gloss_naturalness_prod_wiring_01/`)で、直前配線
(KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01)出力との比較により
悪化事例が無いことを確認した(B1「self-directed travel」のglossが
硬めの漢語「自分主導の旅行」から平易な「自分で決める旅行」へ変化する
方向性を確認したが、選定候補自体が試行毎に変わるためN=1の限定的観察)。
Open Item新規登録OPEN-118を即`RESOLVED / PRODUCTION_WIRED`。LLM追加QA
導入は必要性が実データで確認された場合の別Trialとして`USER_DECISION_
REQUIRED`のまま残す。詳細はDECISION_LOG.md該当項目・`KEYPHRASE-JA-GLOSS-
NATURALNESS-PROD-WIRING-01_REPORT.md`参照)**

このファイルには、**現在正式に採用されている仕様だけ**を書く。経緯・
比較検討・却下案は書かない(→[DECISION_LOG.md](DECISION_LOG.md)/
[HISTORY_INDEX.md](HISTORY_INDEX.md))。未確定事項は書かない
(→[OPEN_ITEMS.md](OPEN_ITEMS.md))。

各項目は最低限、**管理ID／現在値／状態／根拠Decision／最終更新日**を持つ。

---

## Product(番組仕様)

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| サービス名 | English Your Way | `DECIDED`(2026-08-17再確認: 現行B1コード`er003_v1_sing01_voice01_generate.py`のWelcomeナレーション文言"Welcome to English Your Way."で継続使用を確認、改称の証拠なし) | ER-003-B1-P9A系 | 2026-08-07 |
| 対象ユーザー | 日本語話者の英語学習者(リスニング中心) | `DECIDED` | ER-003-B1系 | 2026-08-07 |
| 番組構成(19パート) | `HISTORICAL`(P-series、Point構造導入前のシェル)。Intro→Welcome→Topic Intro→Japanese Title→notification1→Preview Intro→Point解説→Preview→notification2→Key Phrases Intro→Key Phrase×5→notification3→Full Story Intro→Full Story→Outro。**Comment 1〜4・Point One/Two・Point Notification・In One Lineを含んでおらず、現行の11-part content構造+Point Notification/Voice構成とは一致しない。** 現行の全体構成は本ファイル内の複数箇所(CEFR-A2/B1構造・音声仕様節の11パート構造、B1 Voice構成節、Cross-level仕様節のPoint Notification/pause各項目)に分散して記載されており、単一の更新済みN-part一覧はまだ存在しない(2026-08-17 SoT Consistency Cleanupで判明、統合は今回のスコープ外) | ER-003-REPRO-01/02(A02・ADD03で再現確認済み、ただしPoint構造導入前) | 2026-08-09(`HISTORICAL`化: 2026-08-17) |
| Key Phrasesセクション構成 | 番号→英語→日本語訳→英語(反復) | `DECIDED` | ER-003-B1-P9A系 | 2026-08-07 |

## CEFR(A2 / B1 / B2 比較)

**注意(2026-08-17追記、ER-003-B1-A2-SPEC-FREEZE-01/SCOPE-FIX-01)**: 下表の
CEFR-B1列は、A01/A02/ADD03(P-series)で使われた初期の「B1専用簡略英文」
設計を記録したものであり、**現在のProduction標準ではない**。B1の現行
正式仕様は、Verified Fact LedgerからB1専用Writerで独立生成した
natural spoken news English(B2と同一テキストではなく、B2よりlistening
loadを下げつつA2ほど強くは簡略化しない独自の本文)+Support
(Preview/Comment1-4)の言語・役割で作る設計へ更新された(下記
「B1(独立生成Natural Spoken News English)」節を参照)。下表のCEFR-B1列は
`HISTORICAL`として保持し、既存のP-series記事(A01/A02/ADD03のCEFR-B1)の
記録としてのみ有効とする。

**LAUNCH_SCOPE(2026-08-17、ER-003-B1-B2-SCOPE-FIX-01)**: 初期Launchの
対象レベルは**A2/B1の2レベル**であり、**CEFR-B2は`OUT_OF_INITIAL_SCOPE`**
(初期サービス中核から外す。廃止ではなく、future expansion candidate /
internal comparison・reference / historical experiment・referenceという
位置づけへ変更。詳細はDECISION_LOGの該当Decisionを参照)。下表のCEFR-B2列は、
研究・比較参照用の記録として保持する。

| 項目 | CEFR-A2(`LAUNCH_SCOPE: IN`) | CEFR-B1(`HISTORICAL`、P-series専用。現行B1仕様は下記節を参照。`LAUNCH_SCOPE: IN`) | CEFR-B2(`LAUNCH_SCOPE: OUT_OF_INITIAL_SCOPE`) |
|---|---|---|---|
| status | `DECIDED`(2026-08-12、ER-003-A2-SPEC-FREEZE-01。詳細経緯は[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)) | `DECIDED` | `DECIDED`(テキストのみ。初期Launch対象外。音声化は[OPEN_ITEMS](OPEN_ITEMS.md)参照) |
| vocabulary | 可能な範囲で平易な一般語を優先(定性的方針)。**厳密なCEFR語彙数上限・wordlistは意図的に設けない**(正式wordlist不在でLLM判定が不安定なため、数値ルール化は`REJECTED`) | 定性的指示のみ("mostly common, everyday vocabulary... a B1 learner already knows")、wordlist参照コードなし | 定性的指示のみ("主に一般的なB2以下の語彙")、wordlist参照コードなし |
| 平均文長 | 11語以下(生成方針。B1/B2同様、機械的gateとしては未実装) | ≤15語(`B1_TARGET_AVG_WORDS_PER_SENTENCE`、**診断のみ、gateではない**) | ≤19語(`B2_MAX_AVG_WORDS_PER_SENTENCE`、**実際のgate**) |
| 最長文 | 18語以下(生成方針) | 24語(`B1_MAX_SENTENCE_WORD_COUNT`、診断のみ) | 32語(`B2_MAX_SENTENCE_WORD_COUNT`、実際のgate) |
| 全体語数 | 上限なし。**総語数を意図的に削らない**(B1と同等程度の主要情報量を保持) | 上限なし(明示的にhard limitを設けない設計) | 上限なし(記録のみ、gateなし) |
| 1文1アイデア | 原則1文1メッセージ | 定性的指示あり("Prefer one idea per sentence") | 規定なし |
| 等位接続・従属節 | 関係詞節は原則回避、分詞構文を避ける、複雑な受動態を避ける | 定性的指示のみ("avoid long subordinate clauses")、数値上限なし | 規定なし |
| 関係詞 | 原則回避 | 規定なし | 規定なし |
| 受動態 | 複雑な受動態は避ける(単純な受動態は許容) | 規定なし | 規定なし |
| 完了形・進行形 | 完了形等の複雑構造は必要最小限 | 規定なし | 規定なし |
| 助動詞 | 規定なし | 規定なし | 規定なし |
| 固有名詞 | 密度低減の数値目標は設けない(`REJECTED`、通常の編集判断に委ねる) | 保持可(周辺文は簡単に) | 理解に必要な場合のみ |
| 数字・金額・日付・% | 原則1文1数字。年齢範囲・スコア・時間帯・日付(月+日+年)は1つの意味単位として例外扱い | CEFR別の簡略化ルールなし(音声制作段階のMFA/ASR対応のみ)。**2026-09-07追記**: Numeric Precisionの既定(概数を基本、精度保持は意味がある場合のみ)も同じくCEFR別ルールではなくA2/B1/B2共通の単一原則である(詳細は「Cross-level仕様」節「Evidence Compression Editor(方式C)追加ルール」行・Writer共通Prompt「Spoken-first原則(数字の扱い)」C項参照、ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01) | 同左 |
| 専門語 | 規定なし(B1に準ずる想定) | 理解に必要なら保持可 | 理解に不可欠なら残してよい |
| タイトル | 固定構造(`# Title`)のみ、CEFR別の語数・語彙制限なし | 固定構造(`# Title`)のみ、CEFR別の語数・語彙制限なし | 同左 |
| 生成元 | `HISTORICAL`表記に注意: 「Natural English Source」はP-series(A01/A02/ADD03)のマスターテキスト経由の生成方式を指す。N3以降の新規記事(Hanshin/Health/Household等)は、Natural English Sourceという中間master textの段階を経ず、**Verified Fact Ledgerから直接**A2 Writerを1回呼び出して生成する(B1/B2本文を入力にしない、という原則自体はP-series/N3とも共通)。詳細はB1節「News本文の生成方式」を参照 | Natural English Sourceから独立生成(P-series) | Natural English Sourceから独立生成(P-series) |
| Spoken-first | `ADOPTED`。主語・動詞を早く出す、長い前置詞句・名詞句を文頭に置きすぎない、文末まで聞かないと意味が確定しない構造を避ける。厳格なsyntax validatorにはしない(style原則として運用) | 規定なし | 規定なし |
| Full Storyの役割 | Full Storyだけでニュースの核心が分かる。Point One/Twoは深掘り・背景・意味付けとし、Full Storyの代替にしない | 規定なし(Full Story=本編そのもの) | 規定なし |
| 本文品質要件 | **Simple AND Natural**(平易さと自然さを両立、どちらかを犠牲にしない) | 規定なし | 規定なし |
| Naturalness QA | 本文生成後、独立工程としてGrammar/Idiomaticity/News narration naturalness/Meaning preservation/A2 suitability/Spoken-firstの6観点を確認する方針を採用(`PASS`/`REVISE`/`HUMAN_REVIEW`、大規模自動化は未実装、詳細は本ファイル「A2構造・音声」節) | 規定なし | 規定なし |

根拠: `er003_v1_translator_briefs/b1_p1_prompt_template.txt`、
`er003_b1_article.py`、`er003_v1_translator_briefs/b2_adapter_prompt_template.txt`、
`er003_b2_adapter.py`、[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)(2026-08-09)、
ER-003-A2-01〜03・ER-003-A2-STRUCT-02〜05・ER-003-A2-SPEC-FREEZE-01(2026-08-12)。

**`levels.py`のA2/B1/B2数値(vocab 1,000語/620-700語等)は、
`generate_test.py`/`tts_test.py`という無関係な別番組専用の値であり、
このCEFR表には一切採用していない。**

## CEFR-A2 構造・音声仕様

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 全体構造(11パート) | Preview→Key Phrases→Comment1→Full Story Part1→Comment2→Full Story Part2→Comment3→Point One→Point Two→Comment4→In One Line | `DECIDED` | ER-003-A2-STRUCT-02〜04、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| Comment 1の役割 | Listening Focus(次に何を聞くかを示す、答えは言わない)。長さ目安: 原則1文 | `DECIDED` | 同上 | 2026-08-12 |
| Comment 2の役割 | Mid-story Recovery + Next Question(Part1の要点を1点回収し、Part2への問いを提示)。長さ目安: 1〜2文 | `DECIDED` | 同上 | 2026-08-12 |
| Comment 3の役割 | Story Meaning + Bridge to Points(Full Story全体の論点整理、Pointsへの橋渡し)。長さ目安: 2〜3文 | `DECIDED` | 同上 | 2026-08-12 |
| Comment 4の役割 | Point Recovery + Bridge to In One Line(Pointsの意味を回収しIn One Lineへつなぐ)。長さ目安: 2〜3文。「英語一文でまとめます」とは言わず、実際の3文構成と整合する自然な文言を使う | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-01、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| Comment文言の一般化範囲 | 役割・判断基準のみを一般化し、具体的な文言は記事ごとに新規作成する(A02の文言をA01/ADD03へ機械的に流用しない、3記事で重複文言ゼロを確認済み) | `DECIDED` | ER-003-A2-STRUCT-04 | 2026-08-09 |
| Full Story分割 | 機械的な50:50分割は禁止。原則2ブロック。分割位置の優先順位: ①意味上の転換点 ②時系列上の転換点 ③問題→例外 ④発表→反応 ⑤What happened→What happened next / Why it matters | `DECIDED` | ER-003-A2-STRUCT-02〜04 | 2026-08-09 |
| In One Lineの構成 | 中心1文(要約)+英語の短い補足2文程度(B1相当のセクション密度)。「In One Line」は中心1文を指す語で、セクション全体を1文に限定しない。補足文はFull Story/Points既出情報のみを使い、新規factを追加しない | `DECIDED` | ER-003-A2-STRUCT-05 | 2026-08-09 |
| In One Line見出しのTTS | 見出し文字列("In One Line")を実際にTTS inputへ含めて発話させる(Point One/Twoと同じ方式)。instructionのみで発話させる方式は不使用 | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-04(3/3で安定動作確認)、ER-003-A2-AUDIO-AB-01(完成音声で確認) | 2026-08-12 |
| A2英語ナレーション速度 | 約135 WPMを**目安**として採用(hard constraintではない)。対象: Full Story Part1/2・Point One/Two・In One Lineの英語segmentのみ(日本語・Key Phrase・効果音・無音は除外)。数値達成のため不自然な間・単語単位の発話・pitch/rhythm崩壊を起こさない。segmentごとのWPMばらつきは許容し、最終的な自然さはユーザー試聴を優先する。制御手段はTTS自身の明示的speed parameterが存在しないため、prompt/style instructionによる誘導を使用(post-processing time-stretchは未使用)。**同一instructionでもsegmentごとに反応が異なり、指示を強めても必ずしも遅くならない(非単調)ことを確認済み** | `DECIDED`(目安として) | ER-003-A2-AUDIO-AB-01(A02でA/B比較、ユーザー承認) | 2026-08-12 |
| B1/B2音声速度 | 現行の自然な読み上げ速度を維持。明示的なWPM targetは新設しない | `DECIDED` | ER-003-A2-SPEC-FREEZE-01(ユーザー判断) | 2026-08-12 |
| Naturalness QAフロー | `A2生成 → 独立したNaturalness QA(Grammar/Idiomaticity/News narration naturalness/Meaning preservation/A2 suitability/Spoken-firstの6観点) → 必要箇所のみ修正 → re-QA`。判定は`PASS`/`REVISE`/`HUMAN_REVIEW`の3状態。生成モデル自身への自己確認にはしない(生成とQAを分離する) | `DECIDED`(方針として。大規模自動実装はまだ) | ER-003-CROSSLEVEL-AUDIO-04、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| Key Phrase選定(A2) | A2最終本文から改めて選定する(B1 Key Phraseの機械的流用はしない)。方式は既存のStrategy L(Listening Blocker Ranking)+Canonicalization+minimum sufficient+semantic safeguardsをそのまま使用(A2専用の新方式は作らない) | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-02(A01/ADD03で新規選定を実施) | 2026-08-10 |
| Key Phrase source整合Gate(OPEN-170再発防止) | 2026-09-18発見のFree-Address A2/AI Hiring A2不整合(本文平易化・B1→A2翻案後にKey Phrase資産が追従更新されていなかった)の再発防止として2 Gateを実装。**Gate (a)**: Assembly直前に`keywords_canonicalized.json`各項目の`source_span`(無ければ`source_sentence`)が当該Assemblyの現行本文に実在するかを`er003_key_phrase_source_gate_01.check_key_phrase_source_presence()`(大小文字・apostrophe種・HTML entity・ダッシュ種・連続空白を正規化した部分文字列一致)で機械確認し、1件でも不在なら`RuntimeError("KEY_PHRASE_SOURCE_MISSING: ...")`でepisode assemblyを中止する。共有Audio Validation Gate(`er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`、新設ラッパー`verify_key_phrase_source_gate()`)へ組み込み、既存の`blocked`判定を通過した場合のみ実行する(独立したRuntimeError種別)。本文は呼び出し側がin-memoryのarticle_text(推奨、Family C production runner等)を明示的に渡すか、未指定時は`out_dir/article.md`→`out_dir/article_normalized.txt`の順でfallback解決する。**FIX-01(Fable差し戻し1回目、2026-09-18)でfail-closed化**: Gate (a)の適用要否は「当該episodeがKey Phrase segmentを持つか」で判定する(`tts_generation_results.json`の`key_phrases`が非空、または`key_phrases/keywords_canonicalized.json`が存在)。該当する場合はもはやsilentlyスキップしない——asset不在は`RuntimeError("KEY_PHRASE_SOURCE_GATE_ASSET_MISSING: ...")`、本文解決不能は`RuntimeError("KEY_PHRASE_SOURCE_GATE_ARTICLE_TEXT_UNAVAILABLE: ...")`で停止する。Key Phraseを持たないepisode(fixture等)のみ`out_dir/audit/key_phrase_source_gate.json`に`{"status":"NOT_APPLICABLE"}`を記録して続行する(理由を残す、silent skipとは異なる)。この単一の共有関数はNews/B-Family(2V・3V A2/B1)/Family C/Family A Trend/Discoveryの全Production Assembly入口から共通で呼ばれるため、Family別の個別配線コピーは作っていない。実Assembly経路(`verify_key_phrase_source_gate(out_dir, level)`、Family Cのみ`article_text=`明示)を20 canonical out_dirに対し直接実行し20/20 PASS(NOT_APPLICABLE 0件)、旧2 asset(旧Free-Address A2/旧AI Hiring A2)はtrue positive FAILを再確認した(evidence: `docs/pm/closeout_136_e2e/key_phrase_source_gate_01/gate_a_canonical20_via_wrapper.json`)。**Gate (b)**: 他記事(または旧run)からKey Phraseを流用する経路(`reuse_key_phrases_a2`等)は、`er003_key_phrase_source_gate_01.assert_key_phrase_reuse_source_matches()`で供給元本文と流用先本文のsha256一致を常時必須化し、不一致なら`RuntimeError("KEY_PHRASE_REUSE_SOURCE_MISMATCH: ...")`で流用を中止する(流用しない)。`er012_b_family_voices_a2_production_01.reuse_key_phrases_a2()`の`target_article_text`は**FIX-01でfail-closed化**——未指定時にGate (b)を無効化する経路は廃止し、`narration_dir`の親ディレクトリ配下の`article.md`から流用先本文を自動解決する。それも無く本文を解決できない場合は`RuntimeError("KEY_PHRASE_REUSE_TARGET_TEXT_UNAVAILABLE: ...")`で流用不可とする(Gate (b)を迂回できる経路を残さない)。唯一の実呼び出し元(`er012_b_voices_3v_a2_user_test_01.py`、AI Hiring A2事故の発生経路そのもの)は既に`target_article_text`を明示している。`er012_b_family_production_runner_01.py`の`reuse_key_phrases`/`reuse_key_phrases_3v`/`reuse_approved_a2_assets`は、供給元/流用先本文のsha256比較による`[TEXT_HASH_MISMATCH]`という同等のfail-closed機構(引数省略で無効化できない、常時必須)を実装済みであることをコード確認済み(行番号はDECISION_LOG FIX-01節参照)。旧形式asset(`source_span`/`source_sentence`いずれも欠落)は本Gate導入時点の20 canonical assetには存在せず未発見(該当時は`reason="NO_SOURCE_FIELD_AVAILABLE"`でFAIL報告のみ、自動PASS化はしない、扱いは`USER_DECISION_REQUIRED`候補として別途報告)。費用¥0(ローカル文字列比較・sha256比較のみ、API呼び出しなし) | `PRODUCTION_WIRED` | KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01(ユーザー正式決定2026-09-18、OPEN-170採用) | 2026-09-18 |
| Core Explanatory Logic Preservation | A2生成指示(`A2_KAI1_INSTRUCTION`)へ追加した原則:「Preserve the core explanatory logic and decision rule established by the Verified Fact Ledger. You may simplify wording, sentence structure, examples, and presentation order, but do not replace the Ledger's underlying mechanism or decision rule with an easier shortcut, category, causal explanation, or rule of thumb that the Ledger does not support or explicitly rejects. Simplify how the listener understands the idea, not what the idea means.」語彙・文構造・具体例・提示順序の簡略化は許容するが、Ledgerが規定した判断軸・仕組みを、Ledgerが支持しない/明示的に否定するショートカット・分類・因果関係・経験則へ置き換えない。ジャンル固有の具体例(例: Household記事のfruit/vegetable)はこの一般原則のprompt本文へhard-codeしない | `DECIDED` | ER-003-N3-ROOT-FIX-01(instruction追加)、ER-003-N3-ROOT-FIX-VERIFY-01(3ジャンル検証、ユーザー承認) | 2026-08-17 |
| Topic introのTTS入力(`title_tts`、任意フィールド) | `generate_a2_segments()`(`er003_v1_n3_01_tts_generate.py`)のtopic_intro TTS入力は既定で`parts['title']`(表示・記事本文・canonical[ASR照合対象]と同一)を使うが、`parts.json`へ任意フィールド`title_tts`(TTS入力専用の言い換え、例: タイトル中のcolonをperiodへ置換し不自然なprosody区切りを回避)を追加した場合のみ`parts.get('title_tts', parts['title'])`でTTS入力にそれを使う。表示・記事本文・canonical(`results['topic_intro']['canonical_text']`)は常に`parts['title']`のまま不変。既存Key Phrase`japanese_gloss`/`japanese_gloss_tts`分離(`convert_display_gloss_to_tts_text`)と同型の設計で、`title_tts`未設定の既存テーマ・既存runは完全無変更(後方互換)。B1側(`generate_b1_segments`相当)には同等フィールドは未実装(A2のみ実装、B1は未対応。B1はTopic introに相当するJapanese title読み上げ自体を持たないため、必要になった時点で同型フィールドの追加要否を判断する) | `PRODUCTION_WIRED` | USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06(Space Weapons A2実運用、regression 2896件PASS) | 2026-09-17 |

## B1(独立生成Natural Spoken News English) — 2026-08-17新設、2026-08-17確定(SCOPE-FIX-01)

**B1/B2関係の確定(2026-08-17、ER-003-B1-B2-SCOPE-FIX-01でユーザーDecision)**:
前回のSoT Consistency Cleanupで`NEEDS_CONFIRMATION`としていたB1/B2の
関係は、以下の通り確定した。**B1はB2と同一テキストを共有しない。**
B1は、Verified Fact LedgerからB1専用のWriterで独立して英文を生成する
(A2と対称的な関係。同じLedgerを共有し、別々のWriterで独立生成する
という点でA2/B1は同格)。既存の`B1_B_DIRECT_INSTRUCTION`の思想
(natural spoken news English、adult tone、A2ほど強く簡略化しない、
B2相当の難しい英文よりListening Loadを下げる、Clause Density/Concept
Density/Long-distance Dependencyを抑える、hardなCEFR語彙・文長制限は
設けない)を、そのままB1 News本文の正式仕様とする。「B1 = B2本文 +
Support」という理解は誤りであり、正式には採用しない。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 基本方針 | B1のNews本文(Full Story Part1/2・Point One・Point Two・In One Line)は、Verified Fact LedgerからB1専用のWriterで独立生成する。目標は: natural spoken news English、adult tone、A2ほど強く簡略化しない、B2相当の難しい英文よりlisteningで追いやすい、Clause Density/Concept Density/Long-distance Dependency等を抑える。hardなCEFR語彙制限・文長制限は設けない。B1の難易度差は、この独立生成された本文自体と、Supportの言語(easy English)・役割の両方で作る(Supportだけで難易度差を作るのではない) | `DECIDED` | ER-003-B1-B2-SCOPE-FIX-01(ユーザーDecision)、ER-003-A2-B1-N3-01(`B1_B_DIRECT_INSTRUCTION`の実装・検証) | 2026-08-17 |
| A2との関係 | A2とB1は同一のVerified Fact Ledgerを共有するが、別Writerでそれぞれ独立生成する。B1は自然なニュース英語を維持しながらB2相当よりListening Loadを下げる。A2はCognitive Load Reductionをより強く適用し、one idea at a timeへの再構成等を行う。両者ともLedgerのFact/Core Logic(A2 Core Explanatory Logic Preservationと同じ原則)を維持する | `DECIDED` | ER-003-B1-B2-SCOPE-FIX-01 | 2026-08-17 |
| News本文の生成方式 | Verified Fact Ledgerから直接1回のWriter呼び出しでNatural English本文を生成する(「B1-B Direct Generation」)。B2を別段階として先に生成し、それをB1へ流用する旧来の2段階パイプラインは使用しない。過去のP-series記事(A01/A02/ADD03)ではCEFR-B2が別途独立生成されているが、これは旧アーキテクチャの記録であり、新規記事のNews本文生成方式ではない | `DECIDED` | ER-003-A2-B1-N3-01(3ジャンル横展開で採用・検証) | 2026-08-17 |
| B1-B Direction Control原則 | 診断的原則であり、新しいhard ruleは追加しない: Clause Density(1文1主要アイデア+限定的な補足情報)、Long-distance Dependency(長い挿入節は分割)、Abstract Noun Chains(名詞化表現は聞き取りを妨げる場合のみ動詞化、機械的ルール化しない)、Logical Flow(必要な箇所のみ明示的接続詞)、Concept Density(新概念を詰め込みすぎない)、Passage Rebuilding(同じFact/Story Coreから自由に構成し直してよいが、Ledgerにない事実・因果・意図・評価を追加しない)。禁止する新規hard rule: 1文語数上限、CEFR外語彙禁止、受動態禁止、1文1事実の強制。平均文長は診断記録のみで、gateとして強制しない | `DECIDED` | ER-003-A2-B1-N3-01 §7-9 | 2026-08-17 |

**命名ルール(ユーザー向け名称=B1、内部ID=b1b、2026-09-15追記、
PM-CLOSEOUT-CONSOLIDATION-135)**: 記事レベル「B1」に言及するユーザー向け
文言(REPORT本文・RESULT_PACKET・player HTML・PM_BRIEF等)では常に「B1」を
使い、「B1B」「B1-B」は使わない。内部識別子(ディレクトリ名`b1b`/dict
key/定数名/CLI引数/article_id等)は引き続き既存のまま(`b1b`、
`B1_B_DIRECT_INSTRUCTION`等)でよく、renameしない。ユーザー向け文中で
内部IDへ触れる必要がある場合のみ「B1(internal id: b1b)」のように小さく
併記してよい(必須ではない)。「B1-B」という名前自体の由来は、
2026-08-17 ER-003-B1-B2-SCOPE-FIX-01で確定した「B1-A方式(旧2段階、
廃止)」対「B1-B方式(Direct Generation、正式採用)」比較Trialの名残
(844行参照、歴史的記述としてそのまま残す)であり、B1-A廃止後はユーザー
向けに区別する意味はない。既存の`docs/pm/PM_GOVERNANCE.md` 9-9節
(2026-09-13)の命名ルールと同一方針であり、新方針ではなく具体例の追加
(詳細: `docs/pm/b1b_naming_investigation.md`)。

### B1 Support(Preview / Comment 1-4)

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 対象要素 | Preview、Comment 1〜4を平易な英語で提供する | `DECIDED` | ER-003-B1-NOVEL-AUDIO-01系 | 2026-08-17 |
| Support Englishの難易度目標 | B1本文と同等の難易度は目指さない。目的はNatural English本文を理解するためのListening Navigationであり、Support自体を新しい学習課題にしない。原則: first-listenで理解しやすい、one simple idea at a time、familiar everyday wording、compressed/abstract explanationを避ける、adult tone維持 | `DECIDED` | 同上 | 2026-08-17 |
| Comment役割(C1〜C4) | A2で確立した役割をそのまま維持し、言語だけをJapanese→easy Englishへ変更する。C1: Listening Focus。C2: Mid-story Recovery + Next Question。C3: Story Meaning + Bridge to Points(Point One/Twoの具体的見出し・答えは先出ししない)。C4: Point Recovery + Bridge to In One Line(「英語一文でまとめます」等、In One Lineの文数を断定する表現は使わない) | `DECIDED` | ER-003-B1-NOVEL-AUDIO-01系、ER-003-CROSSLEVEL-AUDIO-01(C3/C4の役割定義はA2と共通起源)、ER-003-A2-B1-N3-01(3ジャンルで再現確認) | 2026-08-17 |

### B1 Key Phrase

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 提示順序 | English → Japanese → English(反復)を正式仕様とする。英英説明(English-only definition)へは変更しない | `DECIDED` | ER-003-B1-NOVEL-AUDIO-01系、ER-003-A2-B1-N3-01(3ジャンルで再現) | 2026-08-17 |
| 採用理由 | 難語の英英説明はそれ自体が新しい理解負荷になる、section長文化を防ぐ、意味理解の確実性を優先するため | `DECIDED` | 同上 | 2026-08-17 |
| 選定方式 | Strategy L(Listening Blocker Ranking)+ Canonicalization。B1本文確定後、B1自身の本文から選定する(A2 Key Phraseの流用はしない) | `DECIDED` | Key Phrase節と共通方針 | 2026-08-17 |

### B1 Voice構成

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| Navigator/Support(Charon) | Welcome、Topic intro、Preview intro/Preview、Key Phrases intro/番号/日本語訳、Full Story intro、Comment 1〜4、Outro | `DECIDED` | ER-003-B1-NOVEL-AUDIO-01-VOICE系(module: `er003_v1_sing01_voice01_generate.py`)、ER-003-A2-B1-N3-01(3ジャンルで再現確認) | 2026-08-17 |
| News Content(Aoede) | Full Story Part1/2、Point One/Twoのsemantic heading・本文、In One Line、Key Phrase英語Component | `DECIDED` | 同上 | 2026-08-17 |
| 検証範囲 | 上記配置は、`er003_v1_sing01_voice01_generate.py`(Voice役割再配置モジュール)およびER-003-A2-B1-N3-01での3ジャンル(Sports/Health/Household)横展開で実際に生成・音声確認済みの最新配置を記載している。過去の暫定版(labels_v2/labels_fixなど中間試作)は反映していない | `DECIDED` | 同上 | 2026-08-17 |

### B1日本語使用範囲

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 原則 | Key Phraseの日本語訳のみ日本語を使用する。Title・Preview・Comment・section narration等へA2由来の日本語spoken textを残さない。A2 Audio Shellの「役割」(Comment役割、Point構造等)は継承するが、A2固有の日本語spoken textそのものは継承しない | `DECIDED` | ER-003-B1-NOVEL-AUDIO-01系(日本語残存Shell要素の英語化) | 2026-08-17 |

## B-Family(Voices)Editorial Type — 2026-09-09新設(EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01)

B-Family(Voices)は、A-Family(11パート構造)とは別の物理構造(5区切り:
Hook/Voice A/Voice B/Tension/Closing)を持つEditorial Type。B1は
`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01`で既に
`PRODUCTION_WIRED`(Phase 1スコープ、一人称"I"の機械保証はPhase 2保留、
詳細はDECISION_LOG.md該当エントリ・同Report参照)。本節はA2版の正式
仕様(2026-09-09ユーザー決定、`APPROVED_FOR_PRODUCTION`)を追記する。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 物理構造 | B1と同一の5区切り(Hook/Voice A/Voice B/Tension/Closing)。11パートへの組み替えは行わない | `PRODUCTION_WIRED` | EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02(B-A2-1) | 2026-09-09 |
| Voice割当 | Voice A=Algieba/Voice B=Erinome/Narrator見出し=Aoede(B1と同一、`er012_b_family_editorial_type_registry_01.py::VOICE_ASSIGNMENT`を共有) | `PRODUCTION_WIRED` | 同上(B-A2-3) | 2026-09-09 |
| Voice A/B・本文系segmentの速度 | 標準A2の既存6% slowdown仕様(`A2_ENGLISH_STYLE_PREFIX_SLOWER`+`apply_a2_slowdown_postprocess()`、無変更)を、Voice A/B本文(`point_one`/`point_two`)を含む全英語segment(Narrator見出し・Hook Part1/2・Tension・Closing)へ適用する | `PRODUCTION_WIRED` | EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04(B-A2-9への回答) | 2026-09-09 |
| Comment 1-4・Preview | 役割定義(FINALIZE-11 Comment Contract)はB1と共有、出力言語のみ標準A2規約(日本語・Aoede、`a2gen.run_support_text`/`n3_tts.generate_a2_japanese_with_reading_safety`)へ変更(B1はCharon英語のまま無変更) | `PRODUCTION_WIRED` | 同上(B-A2-6) | 2026-09-09 |
| 日本語タイトル | 標準A2既存規約(Topic intro英語タイトル直後にJapanese title[Aoede、日本語]を追加、原文タイトルの直訳のみ・新規主張数字は追加しない)を適用。テキストは記事ごとにregistryへ人手で登録する(標準A2の`JAPANESE_TITLES`辞書と同じパターン)。**既存固定記事経路(free_address、`main_a2()`)では従来どおりこの固定辞書登録方式を使う。新規topic経路(`main_a2_2v()`)では、下記「新規topic A2 Production経路」行のとおりconfig供給方式を使う(併記、既存行は削除しない)** | `PRODUCTION_WIRED` | EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03(B-2) | 2026-09-09 |
| Key Phrase | 選定(used_form/日本語gloss)はB1 Phase 1と同一。英語Componentは既存Master Audio Store経由(Aoede)、日本語glossのみ標準A2 Aoede経路で生成。**既存固定記事経路(free_address、`main_a2()`)では従来どおりこの方式(B1 KP dirの`reuse_key_phrases_a2()`)を使う。新規topic経路(`main_a2_2v()`)では、下記「新規topic A2 Production経路」行のとおりA2自身の本文から選定する方式を使う(併記、既存行は削除しない)** | `PRODUCTION_WIRED` | EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02(B-A2-5) | 2026-09-09 |
| 新規topic A2 Production経路(Ledger直接A2 Writer/Key Phrase=A2本文から選定/日本語タイトル=config供給) | ユーザー正式決定(2026-09-17、`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B`): (1) A2生成方式=Verified Fact Ledger→A2 Writer直接生成(B1完成記事への翻案[`run_writer_adapt`]は不採用、Family横断共通化原則に整合)。実装: `er012_b_family_voices_writer_generic_01.py::run_writer_stage_generic()`へ`instruction`引数を追加(既定None=従来どおり`gen.B1_B_DIRECT_INSTRUCTION`、B-Family新規topic A2は`er003_v1_n3_01_articles_generate.py::A2_KAI1_INSTRUCTION`[A-Family全体で既に共有されているLedger直接生成用A2難易度instruction]を明示指定)、`label="A2"`指定で`_writer_process()`がA2_WRITERへ正しくrouting。既存B1呼び出し元(`main_b1_2v()`/`main_b1_3v()`)は引数省略のためbyte単位で無変更。(2) Key Phrase=A2自身の確定本文から選定(B1 Key Phrase流用禁止)。実装: `er012_b_family_voices_a2_production_01.py::run_key_phrases_a2_from_own_text()`(既存共有primitive`sc.run_key_phrases(process="A2_SUPPORT")`を新規呼び出し、`reuse_key_phrases_a2()`[B1 KP dirコピー専用]とは別関数、schemaは既存consumer[`load_a2_sources_for_b_family`/`row_info_a2`]と完全一致)。(3) 日本語タイトル=記事生成時にconfig/引数で供給(固定辞書登録は不要な一般化)。実装: `generate_japanese_title_for_new_topic(japanese_title_text, out_path)`(既存`generate_japanese_title()`[固定辞書専用]は無変更のまま維持)。正式入口: `er012_b_family_production_runner_01.py::main_a2_2v()`(`level="a2_2v"`、`write_new_theme`/`comment`/`key_phrases`/`japanese_title`/`voice_check`/`tts`/`assemble`/`player`/`all`各stage、theme_moduleが`THEME_CONFIG`+`JAPANESE_TITLE_A2`をexport)。全英語segment(Narrator見出し・Hook Part1/2・Tension・Closing含む)への既存6% slowdown適用は`generate_narrator_heading_with_a2_slowdown()`/`generate_narration_wide_margin_with_a2_slowdown()`(既存`point_headings.generate`/`news_tail_fix.generate_news_narration_wide_margin`+`n3_tts.apply_a2_slowdown_postprocess`の合成、新規TTS/ASR/time-stretchロジックなし)で新規実装。Trial/DEV script非import(新規test`er012_b_family_voices_a2_new_topic_production_01_test_01.py`で確認)。Personalized News A2 runtime実行(topic「パーソナライズされたニュース」、Ledger再利用[Research実行なし]、Writer 3 attempts、Fact Checker verdict PASS→PASS→REVIEW_REQUIRED、Ledger Deviation Checker全attempt LEDGER_COMPLIANT、総語数410語)で、Comment Contract・Key Phrase(5件選定・REDUNDANCY_PASS)・日本語タイトル・Voice A/B・Hook/Tension/Closing・Narrator見出しの音声生成まで到達したが、Narrator見出し2件(`point_one_heading`/`point_two_heading`、"One Voice:"/"Another Voice:"という接続句がASR文字起こしで欠落するclassification=`ASR_VALIDATION_UNCERTAIN`)がHuman Review Lockへ滞留し、Audio Validation Gateが正しく完成episodeの組み立てをブロックした(override無し、Gate緩和なし)。Analytical Leakage Check残存flag(voice_a/voice_b、3 attempt上限到達)も既存B1/3V仕様と同型のUSER_DECISION_REQUIRED候補として記録(継承ではなくA2独立QAでの新規検出)。**追記(`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01`、2026-09-17): Narrator見出しHuman Review Lockの原因はretry/fallback policyの不整合と判明した。旧`generate_narrator_heading_with_a2_slowdown()`は`point_headings.generate()`(standardとminimal fallbackが単一attempts_logループ内にあり、secondary_asr側がstop_retrying=Trueを返すとfallbackへ到達せず即座に終了する設計、`er003_v1_sing01_point_headings_aoede.py`)を直接呼んでいたが、承認済みfree_address経路(`er003_v1_n3_01_tts_generate.py` 834-845行目)のNarrator見出しはstandard経路とminimal instruction fallback経路が明確に分離された`n3_tts.generate_a2_segment_with_slowdown()`(内部で`c.generate_english_segment_with_fallback()`を呼び、standard側が早期終了してもfallback側は独立予算で必ず試行される)を使っており、両者が異なるpolicyだった。是正: `generate_narrator_heading_with_a2_slowdown()`を後者(承認済みfree_address経路と同一の呼び出しパターン、expected_substring=`first_words(text,3)`/max_extra_chars=20/style_prefix_override=`A2_ENGLISH_STYLE_PREFIX_SLOWER`/disfluency_qa=True)へ統一(`er012_b_family_voices_a2_production_01.py`、新規TTS/ASR/time-stretchロジック追加なし)。是正後、`review_lock.approve_regenerate()`(既存Human Review Lock機構の正規手続き)で見出し2件のみ再実行し、`point_one_heading`=OK(standard 1回目でNORMALIZED_MATCH)、`point_two_heading`=OK(standard不合格→fallback[minimal instruction]でNORMALIZED_MATCH、想定どおりfallbackが機能)。他segmentは再生成せず既存OK音声を再利用。Assembly/Gate=OK(duration=359.264s、peak=0.89034、clipping=False)、player.html+web export(episode.mp3+segments 35件)完了、rawcdn unified.html E2E再生(Playwright、currentTime進行/paused=false/readyState=4/error=null/seek/Key Phrase表示)を実機確認。Analytical Leakage残存flagは既存B1/3V PARTIAL前例と同じ扱いで記事完成をブロックしない(ユーザー試聴時の確認事項として提示)。詳細`docs/pm/RESULT_PACKET_PN_A2_PHASE_B_FIX1.md`。** | `PRODUCTION_WIRED`(新規topic A2 E2E配線・retry policy整合・Personalized News A2 episode生成/Gate/player/web export/E2E再生確認まで全て完了・regression 2893/2896 PASS[既知FAIL3件のみ、新規追加2件含め全PASS]。記事内容としての最終OKはユーザー試聴待ち、USER_TEST_READY確定扱いにはしない)。**2026-09-17追記(USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01)**: 本経路で生成された初回記事(Personalized News A2)はユーザー試聴の結果、個別文言ではなくVoices構造の根本問題(VoiceがSurvey/統計/外部Evidenceを引用、各Voiceの立場がぼやける)を理由に品質NGと判定された(`REJECTED_AS_CURRENT_OUTPUT`、仕様見直しは`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-REVIEW-01`で継続審議中)。この判定は**本行の基盤Status`PRODUCTION_WIRED`を変更しない**(実装配線と、生成された記事1本の品質は別軸で管理する)。詳細: `OPEN_ITEMS.md` OPEN-151行、`DECISION_LOG.md`の`USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01`エントリ。 | PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B-FIX-01 | 2026-09-17 |
| Audio Validation Gate level | 標準"A2"文字列ではなく`"B_FAMILY_A2"`を使う(標準"A2"のPoint本文向けslowdown必須チェックが、名前が同じだが別物であるVoice A/B本文へ誤爆するため)。`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`へ標準A2と同一の対象segment集合(`in_one_line`/`point_one_heading`/`point_two_heading`)で`"B_FAMILY_A2"`キーを登録(共有`er003_v1_n3_01_assemble.py`、この1エントリ追加のみ) | `PRODUCTION_WIRED` | 同上、EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01(Gate 3 item7) | 2026-09-09 |
| 語数・文長(今回限りの許容) | 11語超の文18/38・18語超の文2/38(Voice B・Closing各1文)を、新しい上限を設けずそのまま許容した(今回1記事限りの実測値記録であり、恒久的な新CEFR-A2数値ルールではない) | `USER_DECISION_REQUIRED`扱いではなく今回限りの運用注記(恒久ルール化はしない) | EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02(B-A2-5) | 2026-09-09 |
| Fact Checker `REVIEW_REQUIRED`(複合Voice帰属) | 候補A'(Ledger側`VOICE_n_EVIDENCE`タグ+「Voice本文は出典明記不要(ただし事実誤り・実在人物引用は従来どおり検証)」のopt-inルール)をProduction配線した。`er012_b_family_editorial_type_registry_01.py::fact_attribution_mode`(既定OFF、`family=="B"`のコードレベルgating)。`build_voice_attribution_block()`はタグ行から開始し、次に現れる空行/`[`開始行/`===`開始行の直前までを1エントリとして抽出する(fact本文の継続行・source/URL/counter_or_limitation/verificationを含む塊単位抽出。旧実装はタグの乗る物理1行のみを抽出しevidence本体を欠落させていたが、`OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02`で修正済み、関数シグネチャ・fail-closed挙動・ルール文言は不変)。ON時、実記事2本(B1/A2)でverdict REVIEW_REQUIRED→PASS、unsupported_specific_claims 5/6件→0件へ改善(修正後の完全blockでのruntime evidence実測、B1は不変。**A2は同修正によりPASS→REVIEW_REQUIRED[unsupported2件]へ変化**——Tension段落[Voice本文以外の地の文]の免除対象外claimが、切り詰めblockの下で見えていなかった適正な検出として回復したものであり、false accept新規発生ではない)。Local Rewrite後も帰属維持を実出力で確認 | `PRODUCTION_WIRED(opt-in、Phase 2で既定接続)`(2026-09-09ユーザー正式決定、PM-CLOSEOUT-CONSOLIDATION-29。抽出ロジックのMULTILINE-FIX-02修正版はPM-CLOSEOUT-CONSOLIDATION-31でFable受入)。スコープ: 共有Fact Checker/registry/runner opt-in入口配線済み、A-Family既定OFF・無影響(commit `3c3d7a0`/`34fe8dd`/`a865411`)。B-Family Production既定stage(Writer→Fact Checker A'→後続)への自動接続はPhase 2 Writer配線時に実施(deferred、`OPEN-132`で追跡、既定接続時はMULTILINE-FIX-02版が前提) | OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01、OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02 | 2026-09-09 |
| OPEN-129整合 | 共有Audio Validation Gate(`er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`)へ、`required_structure: dict \| None = None`のopt-in引数(既定OFF)を追加し、family+level複合キーの期待構造(正本はB-Family=`er012_b_family_editorial_type_registry_01.py::build_required_structure()`、A-Family=同ファイルの新規`derive_a_family_required_structure()`)と実`tts_generation_results.json`を突合(delete/voice_swap/extra segment検知、reorderは対象外)できるようにした。既存3呼び出し元(`load_b1_sources`/`load_a2_sources`/`load_a2_sources_for_b_family`)は無変更(引数省略のまま)。既存完成episode12/12でfalse reject 0、4経路×5ケースで検知12/12(runtime evidence実測) | `PRODUCTION_WIRED`(opt-in、2026-09-09 Fable受入、commit `2814ed5`/`34fe8dd`)、opt-in導入のみ・**mandatory化は未承認**(3V/4V Trialと次回A-Family Production run実績後に別判断) | OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01 | 2026-09-09 |
| Production経路 | `er012_b_family_editorial_type_registry_01.py`(A2設定`get_editorial_type_a2()`)・`er012_b_family_voices_a2_production_01.py`(Writer/Comment/日本語タイトル/Key Phrase/Voice A/B slowdown TTS/Assembly loader・timeline)・`er012_b_family_production_runner_01.py`(`level="a2"`分岐、Trialスクリプトは一切importしない) | `PRODUCTION_WIRED`(2026-09-09 Fable最終受入、commit `2b2f266`/`2fbeee3`) | EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01 | 2026-09-09 |
| 3V(人物Voice、Voice 1/2/3=Algieba/Erinome/Schedar) | 3声版(6区切り: Hook/3 Voices/Tension/Closing)をTrialスクリプトで検証。required_structure 3V・Comment 3V文言・Audio Validation Gate両経路(既定OFF/opt-in ON)PASS・negative control検知・Fact A' 2/2 PASS・Analytical Leakage 0・Distinctness 1.0/0.933・実測尺356.6秒(2V比+約17%)。ユーザー試聴により**VALIDATED**(Trial)としてcloseoutした **追記(2026-09-13、EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01-STAGE2-STAGE3、PM-CLOSEOUT-CONSOLIDATION-104)**: B-Family Voices 3V限定のFact Safety保守版ゲート(段階1/段階2、`voice_fact_safety_gate_mode`、既定OFF、`family=="B"`限定opt-in)を`er012_b_family_voices_writer_generic_01.py`/`er012_b_family_editorial_type_registry_01.py`へ実装した。常に厳格5フラグは`changed_causality`版(委任文中の`changed_fact`表記は転記誤り、実装が正)。Voice内数字の「必須」要求撤廃(2-D、上限規定は不変)も同時実装。offline Regression(Production関数)で実データ5/6改善・false accept 0件を確認したが、実生成1本(Stage3)では本ゲート自体は0件発火のため効果を直接観測できず、Gate1=`USER_DECISION_REQUIRED`(Fable判定、2026-09-13)。制度名の字面除外`_VOICE_GATE_INSTITUTIONS`はテーマ依存ハードコード辞書であり汎用性に限界がある。2-D単独では`leak_evidence_subject`型Leakageは防げないことも判明した。Trial継続の承認であり`APPROVED_FOR_PRODUCTION`格上げではない(既定OFFのままcommit)。詳細: `EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md`。 | `APPROVED_FOR_PRODUCTION`(未配線、2026-09-10ユーザー正式決定)。**`PRODUCTION_WIRED`ではない**(Trial実装のみ、Production module・registryは無変更。配線完了条件(a)〜(k)は`OPEN_ITEMS.md`OPEN-120行参照。配線に必要な5項目[registry可変voice数シグネチャ・Gate辞書point_three登録・Comment 3V Contract化・mode/level命名・Schedar本採用格上げ承認]は未実装。(2026-09-14ユーザー正式決定) Production Writerを2/3 Voices可変へ一般化: `APPROVED_FOR_PRODUCTION`(未配線、OPEN-151でGate 3追跡)) | EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01-CLOSEOUT、PM-CLOSEOUT-CONSOLIDATION-65 | 2026-09-10 |
| 2/3可変Writer配線結果(OPEN-151) | `er012_b_family_voices_writer_generic_01.py::make_theme_config()`をvoice_cards 2件(2V)/3件(3V)可変で受け付けるよう一般化(1件・4件は引き続き拒否、external_constraintは3V限定・2V指定時ValueError)。3V時は改修前コード(`git show HEAD`版)と同一入力に対しbyte単位で同一の`build_focus_module_block_3v`/`build_candidate_template`/Leakage schema・prompt/`build_ledger_fragment_visible_voices_only`/theme_config dict出力を確認(オフライン、11テスト)、かつ`run_ledger_deviation_and_local_rewrite`・`_generate_and_compress_article_3v`等の共有関数はsource文字列も無変更。2V専用に`build_focus_module_block_2v`(5区切り、Trial-07由来の承認済み2V構造原則をテーマ非依存へ切り出し、3V専用の一人称"I"指示・外部制約統合パターンは含めない)・`run_fact_check_a_prime_2v`(num_visible_voices=2)・`run_overlap_monitoring_2v`(4値)・2V版Leakage schema/prompt(`leak_binary_camp_split`/`leak_tension_constraint_integration`を除外)・`run_voices_pattern_2v`/`run_pipeline_2v`を新規実装。`er012_b_family_production_runner_01.py`に2V新規topic正式入口`main_b1_2v()`(`level="b1_2v"`、`write_new_theme`stageのみ、既存`main`/`main_a2`/`main_b1_3v`は無変更)を追加。registry可変voice数(`build_required_structure(level, voice_a, voice_b, voice_c=None)`)・Gate辞書(`B1_REQUIRED_SEGMENTS`/`B1_3V_REQUIRED_SEGMENTS`)は本タスク以前から2V/3V双方に対応済みと確認(無変更)。Comment Contract(`registry.COMMENT_ROLES`)はvoice数非依存の共有定義であり2V/3Vで分岐なし(ただし新規topic Writer-only入口自体はComment未接続、3Vの既存スコープと同一の限界)。2V runtime evidence: topic「Is personalized news good for us?」(personalizationの便利さ・relevance vs filter bubble/worldview narrowing/editorial controlの双方が成立するよう設計)、Research→Verification(web_search、VERIFIED 18/AMBIGUOUS 1/REJECTED 0)→VOICE_1/2_EVIDENCEタグ付きLedger→Writer最大3 attempts(Leakage Check是正retry、Fact Checker verdict PASS→PASS→REVIEW_REQUIRED、Ledger Deviation Checker全attemptでLEDGER_COMPLIANT・deviations 0につき3V保守版Fact Safetyゲートは判定対象なし=未発火、Local Rewrite・OPEN-141 diff QAも同理由で未発火)、総語数395語(soft target 320〜380よりやや超過、hard capではないため許容)。Voices Production 1生成セット総原価=¥99.01(Research/Ledger¥46.98+Writer/QA/Gate/retry¥52.03、TTS未実行のため¥0)。関連回帰: 新規11+33テスト、`er012*_test_*.py`174件、`er011*_test_*.py`266件、全件2668件中2665件PASS(既知FAIL3件のみ、新規FAILなし)。**Status: `PARTIAL`**(2026-09-14 Fable照合訂正。Sonnet報告はPRODUCTION_WIREDだったが、未充足3点: Comment Contract整合[新規topic入口でComment未接続、3Vと同じ限界]/Gate辞書整合[3V保守版Fact Safetyゲートが2Vの5区切り構造で構造的に不発]/2V記事はREVIEW_REQUIRED+残存flagで3attempt上限到達。2V新規topic正式Writer入口・3V regressionなし・registry可変voice数・retry/fallback整合は確認済み。TTS配線は本タスクの承認範囲外のため未実施のまま)。詳細: `EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01_REPORT.md`。 **追記(EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02、2026-09-14、ユーザー方針[Comment接続/Gate 2V対応/残存指摘個別修正]に基づく実施)**: (5-1)Comment Contract配線=✓。`er012_b_family_production_runner_01.py`に`run_comment_contract_for_new_theme()`を新規追加し、`main_b1_2v()`/`main_b1_3v()`のwrite_new_theme stageから、Writerパイプライン(retry・Local Rewrite込み)確定後の最終article_text/sectionsに対してのみComment 1-4+Preview(既存承認済みregistry Comment Contract、run_scaffold()/run_scaffold_3v()と同一Role・呼び出し方法、無変更)+Ledger Deviation Check(Comment Contract検証)を接続(status!="OK"時はスキップし記録)。(5-2)Fact Safetyゲート2V/3V一般化=✓。`_apply_b_family_voice_safety_gate`/`_voice_gate_locate_section`/`_voice_gate_stage1_eligible`を、3V(6区切り)優先検出→検出不可時のみ2V(5区切り)として再検出するよう一般化(段階1/2の判定ロジック・安全基準は無変更、構造読み取りのみ一般化)。3V側は改修前[HEAD]と改修後で`_apply_b_family_voice_safety_gate`の挙動(出力)が完全一致することを新規テストで確認(byteではなくbehavior不変性)、2V側は新規4テストで実際に降格が発火することを確認(段階1/段階2いずれも)。(5-3)2V記事「Is personalized news good for us?」の残存指摘個別修正=既存Ledger再利用+同一write_new_theme経路で再生成(Research再実行なし)。結果、Fact Checker verdict=PASS(前回REVIEW_REQUIREDから改善)、Ledger Deviation Checker=LEDGER_COMPLIANT(deviations=0)、Comment Contract検証もLEDGER_COMPLIANT。ただしAnalytical Leakage Check(voice_b/tension)は3 attempts上限到達後も flagged項目が残存(retry上限変更・Gate基準変更は禁止のため、既存corrective retry機構で解消しきれなかった構造的限界として記録、3V側にも同型の「3attempt上限で残存flagはUSER_DECISION_REQUIRED候補として記録」という既存仕様がある)。3V regression: 新規9テスト(Comment Contract配線契約4件+Gate 2V/3V一般化4件+Dangling Reference 2件、うち3V behavior不変性1件)全てPASS、既存`ThreeVoiceByteInvarianceAgainstHeadTests`は`_apply_b_family_voice_safety_gate`を対象から除外(意図的にsource変更したため)した上で全件PASS、`er012*_test_*.py`184件/`er011*_test_*.py`266件/全件2699件中2696件PASS(既知FAIL3件のみ、新規FAILなし)。2V clean runtime evidence: `er014_output/four_type_observation_01/voices/run2_clean/`(model_id=gpt-5.6-luna、374語、Comment 1-4+Preview全てstatus=OK)。費用: Voices Production 1生成セット総原価=¥140.39(Research/Ledger¥46.98再利用+Writer/Comment/QA/Gate/retry¥93.41実測)。**Status: `PARTIAL`**(Sonnet自己申告、2026-09-14。15項目中14項目は✓、項目7[cleanな2V runtime evidence]のみAnalytical Leakage Check残存flagにより完全クリーンではないため`PARTIAL`のまま。Comment Contract整合・Gate辞書2V/3V整合の2点は前回からの未充足事項を解消)。詳細: `EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02_REPORT.md`。 | EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01/-02 | 2026-09-14 |
| Writer原則: 体験claimの根拠付け(B-Family Voices共通、Voice数・テーマ非依存の恒久原則) | Voice本文で、その人物自身の体験として語る箇所において、数値・制度・他者の具体的な行動を事実として断定する場合は、必ずVerified Fact Ledgerに直接のevidenceがあるものに限る。Ledgerに直接の根拠がない事柄(自分自身の評判・信用が具体的にどうなるか、他社の具体的な訴訟の帰結、規制当局の具体的な運用実態など、まだ起きていない・確認されていない結果)は、確定した事実として書かず、その人物が実際に抱いている体験・感情・判断として書く。既存Fact Safety(Verified Fact Ledger)・「Research is backstage. People are on stage.」原則の一般化可能な拡張であり、3V(Person-Voice版Trial-02で先行適用)に限らず、2V・4V等Voice数・テーマに依存しないB-Family Voices Writer共通原則として確定する | `DECIDED`(恒久Writer原則として確定。Production Writer配線[Phase 2]自体は別途、本行は原則の確定のみ) | ユーザー決定2026-09-12(EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04-GENERALIZATION-AND-REGRESSION) | 2026-09-12 |
| Writer原則: Voiceの立場境界(A/C/F、B-Family Voices共通、Voice数・テーマ非依存の恒久原則) | Personalized News A2のユーザー試聴NG(Voiceが調査・統計を語る[問題A]、各Voiceの立場が曖昧[問題B])を受け、`docs/pm/RESULT_PACKET_VOICES_SPEC_REVIEW_01.md`の候補A〜Fのうちユーザーが以下を`APPROVED_FOR_PRODUCTION`として正式承認した(2026-09-17)。**A**: 各Voiceは自分自身の経験・価値観・立場に徹する。**C**: Voice内で使う具体的な数字は、原則としてその人物自身の経験に属する数値(自分が実際に経験した回数・期間・費用等)のみ許可し、survey/report/study等の外部統計をVoice自身の論証材料にしない。**F**: 反対側(他のVoice)が中心的に抱えている懸念・反論は、Voice本文ではなく別Voiceまたは既存Tension(「共通前提→分岐点→非対称性」の3段構造、design.md B-7)が引き受ける役割であることを明文化する。**E**: 自分の立場の中の迷い・葛藤(nuance)を書くことは許容するが、相手側が中心的に抱えている論点そのものまで自分のVoiceに抱え込ませない。候補B(Narrator/Evidenceレイヤー新設)・候補D(1 Voice=1 Primary Positionの恒久ルール化)は不採用。**Acceptance Gate(追加承認)**: Analytical Leakage Checkへ「立場越境」検知field`leak_position_blur`(Voice数非依存の共通field、`VOICE_LEAKAGE_FIELDS`経由で2V/3V双方のVoiceセクションへ自動適用)を新設した。MAX_WRITER_ATTEMPTS(3)到達後もLeakage flagged項目が残存する場合、`run_pipeline_2v()`/`run_pipeline_3v()`が`final_result["leakage_residual"]=True`+`final_result["status"]="LEAKAGE_RESIDUAL_STOP"`を記録し、`main_a2_2v()`/`main_b1_2v()`/`main_b1_3v()`のwrite_new_theme stageは(既存の`final_result.get("status")=="OK"`判定により)後続stage(comment/key_phrases/japanese_title/voice_check/tts/assemble/player)へ進めず終了する(既存B1/3V「前例踏襲でPARTIAL扱いとしユーザー試聴へ進める」運用は本行以降廃止、前例踏襲だけを理由に残存flag記事をユーザー試聴へ流さない)。MAX_ATTEMPTS自体・既存Gate基準(`voice_fact_safety_gate_mode`既定OFF等)は変更しない。**Fact attribution A'との関係**: `fact_attribution_mode`(既定OFF)は本行と方向性が異なる(A'は将来Voiceへ統計の帰属を許す設計思想、Cは統計そのものをVoiceの論証材料にしない制約)。A'は引き続き既定OFFのまま据え置き、将来ONにする場合はCとの両立条件(統計を扱うVoiceにのみ限定適用する等)を別途設計する(現状未設計)。実装: `er012_b_family_voices_writer_generic_01.py`のVoice rules(3V/2V共通template内Evidence段落・新規「Voiceは自分の経験・立場に徹すること」段落)・Tension役割文言(F明文化)・禁止事項まとめ・`_voice_card_block_text()`(数字許可条件をLedger evidenceのうち本人経験由来のみへ限定)・Leakage schema/prompt/corrective note(2V/3V)・`run_pipeline_2v`/`run_pipeline_3v`(Acceptance Gate)。詳細runtime evidence・regression・PRODUCTION_WIRED判定は`docs/pm/RESULT_PACKET_VOICES_SPEC_01.md`参照。**2026-09-17追記(closeout、`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01-CLOSEOUT`)**: Personalized News A2新版(`docs/pm/RESULT_PACKET_VOICES_SPEC_01.md`6節、SHA `a54d0201`のplayer)をユーザーが試聴し正式承認(`USER_TEST_READY`、記事の再生成・修正はしない)。ユーザー指摘: 肯定派Voiceに「I still worry an important story could be left out.」という相手側の中心懸念を取り込む表現が残存するが、当該記事は今回許容(OPEN-167で継続検討、本行の仕様は変更しない)。PN B1はOPEN-166(Ledger鮮度)として分離、本行のwiring条件から除外。 | `PRODUCTION_WIRED`(2026-09-17ユーザー正式決定、根拠=`docs/pm/RESULT_PACKET_VOICES_SPEC_01.md`10節+`docs/pm/RESULT_PACKET_VOICES_SPEC_01_CLOSEOUT.md`確認(1)a〜i。PN B1はOPEN-166[Ledger鮮度]として分離、本行のwiring条件から除外。ユーザー指摘[肯定派Voiceの相手側懸念取り込み]はOPEN-167で継続検討、本行の仕様は変更しない) | B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01(ユーザー正式承認2026-09-17)、B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01-CLOSEOUT | 2026-09-17 |
| Tension任意パターン: 外部制約統合(3人以上のVoice構成向け、任意適用) | Tensionの「共通前提→分岐点→非対称性」の3段構造(design.md B-7)に続けて、規制・監査・制度等の外部制約(fairness/bias/accountability/law/compliance)を、3人(以上)それぞれの選択肢を制約する実質的な力として統合する4段目のパターン(3V Person-Voice版Trial-02の`leak_tension_constraint_integration`基準に対応)。**3V共通の必須恒久ルールにはしない**。「3人のVoiceだけでは単純な陣営分解ができず、Ledger上、規制・監査・制度等の外部制約が重要な場合に使える構成パターンの1つ」として、Ledger内容・テーマごとにFableが任意適用を判断する(design.md自身が本パターンの記事本文レベル検証を「未実施」と明記しており、1記事[AI採用選考]でのGate1通過のみでは恒久ルール化の十分な根拠にならないため) | `DECIDED`(任意パターンとして確定、恒久ルール化はしない。今後のN増しで再現性・必要性が確認できた場合に恒久ルール化の要否を改めて判断する) | ユーザー決定2026-09-12(EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04-GENERALIZATION-AND-REGRESSION) | 2026-09-12 |
| 3V Fact Safety保守版ゲート(`voice_fact_safety_gate_mode`) | 段階1/2の条件(一人称・certainty系flagのみ、または第三者主語なしでrole合成のみ)に一致するMAJORのみMINORへ再分類する保守版ゲート(判定基準・prompt本体・`MAX_REWRITE_CYCLES`等は無変更)を、B-Family 3V Production経路(`er012_b_family_editorial_type_registry_01.py::VOICE_FACT_SAFETY_GATE_MODE_DEFAULT`)で既定ONへ切替した。A-Family経路はこのフラグ・関連関数(`er012_b_family_voices_writer_generic_01.py::_apply_b_family_voice_safety_gate()`)を一切参照しない(grepで無影響を再確認済み) | `APPROVED_FOR_PRODUCTION`(配線実装済み、Gate3項目4/6[Production runtimeでの実発火・runtime evidence]は次のB-Family実記事生成時の自然発火待ち、OPEN-145と同じ扱い) | ユーザー正式判断2026-09-13(PM-CLOSEOUT-CONSOLIDATION-105)原文「1. 3V Fact Safety: 追加Trialは不要です。offlineでは有効性が確認できているため、次のB-Family実記事生成時に自然発火した場合にruntime evidenceを取得・確認する方針としてください。」、詳細`OPEN-141-TARGET-SENTENCE-DIFF-QA-PRODUCTION-WIRING-01_REPORT.md` | 2026-09-13 |

**Production不整合の修正記録(2026-09-15、PM-CLOSEOUT-CONSOLIDATION-134、
USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES)**: 一人称"I"は上記OPEN-151行
記載のとおり2026-09-08ユーザー正式決定済みの`APPROVED_FOR_PRODUCTION`
仕様であり、本節の追記は**仕様自体の変更ではない**。2V用Writer
template(`er012_b_family_voices_writer_generic_01.py::COMMON_INTRO_
AND_STRUCTURE_BLOCK_TEMPLATE_2V`)に、3V用テンプレートには存在する
【人称】指示block・禁止事項1行が丸ごと欠落しており、既存Prompt実装が
承認済み仕様を反映できていなかったProduction不整合を発見・修正した
(diff +13行、3V関数・3Vテンプレートは無変更)。テスト44件+関連回帰
185件PASS実測。修正後、新規topicで既存2V正式経路を3回試行しr3で記事
確定・音声化まで到達(pov_check機械確認で一人称化成功)。詳細:
`USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02_REPORT.md`4節、OPEN-151行、
`docs/pm/RESULT_PACKET_FIX02_VOICES.md`/`_2.md`。commit `ccf43e8c`。

**最終更新: 2026-09-13(PM-CLOSEOUT-CONSOLIDATION-105、3V Fact Safety保守版ゲート既定ON化)、2026-09-09(EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01、
Gate 3配線)**: ユーザー承認(2026-09-09、`APPROVED_FOR_PRODUCTION`)に
基づき、B-Family A2(「フリーアドレス vs 固定席」A2、Trial-02/03/04で
VALIDATED済みの内容)をProduction正式経路へ配線した。Trial runner 3本
(`er012_editorial_b_voices_a2_trial02_writer.py`/`..._trial02_runner.py`/
`er012_b_voices_a2_cross_audit_fix_03_runner.py`/`er012_b_voices_a2_
slowdown_keyphrase_regen_04_runner.py`)に分散していたA2経路を、Phase 1
Production module群(registry・新規`er012_b_family_voices_a2_production_
01.py`・既存runnerへの`level="a2"`分岐)へ統合し、Trialスクリプトを一切
importしない構成にした(Point Overlap/Analytical Leakage Check等の
monitoring専用QAも含め全文転記、byte一致テストで確認)。既存B1経路
(`level="b1"`既定、既存関数は無変更)は挙動不変(既存14テストPASS+今回
追加19テストPASS)。共有ファイルへの変更は`er003_v1_n3_01_assemble.py`の
Gate辞書1エントリ追加のみ。Runtime evidence: ユーザー承認済み
(`er012_output/editorial_b_voices_a2_free_address_04/`)のVoice A/B本文
(`point_one`/`point_two`)を正式Production関数で実際に再TTS(A2 slowdown
6%適用・OPEN-121/122安全機構有効・ASR verified)、他13segment+Key Phrase
5件は承認済みbyteをsha256照合のうえ再利用(Key Phrase「stay put」新版
[v2]がsha256一致で使用されていることを確認)。完成episode
(`er012_output/editorial_b_family_voices_a2_production_wiring_01/`、
duration=350.493秒・peak=0.95049・clipping=False)・標準player.html
(Gate 7 (a)〜(l))を生成、費用¥15.76(上限¥100以内)。project-wide
regression(`run_project_regression.py`)は新規19テスト追加以外の差分
なし。詳細は`EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01_
REPORT.md`参照(`PRODUCTION_WIRED`確定はFable最終受入待ち)。

## Editorial Type Routing(2軸判定) — 2026-09-09新設(ユーザー決定、PM-CLOSEOUT-CONSOLIDATION-41)

A Family(Discovery/Why + News[Major/Daily] + Trend Synthesis)のうち、
ある題材がどのEditorial Typeとして書かれるべきかを決める**上流のType
routing**を正式化した(ユーザー正式決定、2026-09-09、根拠:
`FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-02_REPORT.md`§1.2/§4 D1)。
2軸判定+単一のtie-break primitiveを採用する。

**軸A(最近性依存)**: その記事の中心的主張の妥当性が、日付・最近性に
依存するか。
**軸B(独立Signal集約依存)**: その中心的主張が、複数の独立したSignal
(出来事・観測・データ点)の集約に依存するか(軸Bは軸A=Yesの場合のみ
問う)。

| 軸A | 軸B | 判定 |
|---|---|---|
| Yes | No | Major/Daily News |
| Yes | Yes | Trend Synthesis |
| No | (問わない) | Discovery/Why |

**tie-break primitive(単一規則)**: 軸A・軸Bいずれの判定に迷う場合も、
「その要素(発表日/個々のSignal)を実際に取り除いた場合、記事の中心的
主張が崩れる(別の記事になる)か」という依存構造読みの単一の問いへ
還元して判定する。表面的な言葉遣い(変化を示唆する語など)だけで判定
しない。

**上流routingと下流Gateの分離**: 2軸判定は「どのGateを適用すべきか」
を決めるための上流工程(Editorial Type routing)であり、既存のMajor/
Daily Gate 6項目・Trend Gate 6条件(下流工程、型決定後に「その型として
成立しているか」を確認するチェックリスト)を代替・変更するものではない。
2軸判定を通過した後、既存の型別Gateをそのまま適用する。

**Discovery=Pool型の正式化**: `POOL_TOPIC_MASTER.md`の承認済み定義
(Evergreen、特定の1件の最近の出来事に非依存)は、2軸判定の軸A=Noの
必要条件を満たすように設計されている(既決定義の論理的帰結)。これに
より、Pool型記事はDiscovery/Why型として扱う運用を正式化する(既決
事項A-UDR-9[Household=Discovery/Why]・A-UDR-10[Health=Major/Daily]を
引き継ぐ)。`POOL_TOPIC_MASTER.md`自体の語彙・列定義は変更しない
(参照のみ)。

**判定方式・記録**: 判定は手動判定(人間が記事着手前に軸A/軸Bを判定
する)とし、判定結果を記事のrun summaryへ記録する(Trend Synthesis
mode判定の`run_metadata.json`記録機構と同型)。これを正式initial path
とする。**自動判定(記事内容から軸A/軸Bを自動推定する処理)は実装しない
(`OPEN_ITEMS.md` OPEN-130として引き続き`DEFERRED`)**。

**机上検証**: POOL_TOPIC_MASTER 20件+既存記事6件、計26件で¥0机上検証を
実施した。判定不能率0/26。素朴な表面的読み(タイブレーク未適用)の
場合、POOL No.5/7/12/14/17の5件がTrend方向へ誤判定されうる曖昧事例
として残る(タイブレークを厳密に適用すればDiscovery/Whyへ収束すると
考えられるが、実記事化しての再検証は未実施)。詳細は
`FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-02_REPORT.md`§2参照。

## News Editorial Mode(Trend Synthesis) — 2026-09-08新設(OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01)

A Family(Discovery/Why + News)のうち、News配下に「Trend Synthesis」という
Editorial Modeを正式にProduction Writerへ配線した(ユーザー承認、
2026-09-08、`APPROVED_FOR_PRODUCTION`)。Trend Synthesisは、単発の
出来事(Major/Daily News)ではなく、複数の独立したSignalが積み重なって
示す変化そのものを扱う記事タイプ。Discovery側(4-layer構造・Layer3
Focus Module採否・Engagement根底指示のDiscoveryへの適用)は本Decisionの
対象外であり、据え置きのまま(§DECISION_LOG.md該当エントリ参照)。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 配線方式 | `er003_v1_n3_01_articles_generate.py::build_common_block()`へ後方互換オプション引数`editorial_type_module_block: str = ""`を追加し、`COMMON_BLOCK_TEMPLATE`内(【Spoken-first原則(数字の扱い)】直前)に対応する`{editorial_type_module_block}`placeholderを追加した。既定値`""`の場合、既存A-Family全出力はバイト単位で不変(単体テストで固定)。Trial専用の`.replace()`アンカー置換方式には依存しない | `PRODUCTION_WIRED`(配線のみ、Gate 3詳細は`OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01_REPORT.md`) | 同上 | 2026-09-08 |
| Mode指定方式 | `er006_pool_pilot_01_writer.py::run_writer_for_theme()`(Production Writer正式初回経路)へ`editorial_mode: str \| None = None`引数を追加。`gen.resolve_editorial_type_module_block(editorial_mode)`が既知のmode文字列(現状`"trend_synthesis"`のみ)をModule本文へ解決し、未知の値はfail-closedで`ValueError`。Mode判定(記事内容から自動でmodeを推定する処理)は実装していない(人間が呼び出し時に明示的に渡す) | `PRODUCTION_WIRED`(手動指定のみ、自動判定は未実装) | 同上 | 2026-09-08 |
| Focus Module内容 | `TREND_SYNTHESIS_FOCUS_MODULE_BLOCK`(OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09でVALIDATED、内容無変更で正式採用)。Main Storyでの個々Signal列挙禁止・Trend overclaim禁止・Point One/TwoでのSignal意味づけ分担・Point TwoでのCounter-signal/limitation優先検討・evidence strength混同禁止・mixed明示 | `PRODUCTION_WIRED` | 同上 | 2026-09-08 |
| Engagement/Storytelling原則 | `TREND_SYNTHESIS_ENGAGEMENT_BLOCK`(OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10施策1でVALIDATED、内容無変更で正式採用)。時系列列挙型Main Story禁止+反転・対比・矛盾等の技法検討。**Trend Synthesis mode限定の採用であり、Discovery等他Editorial Typeの根底Promptへは適用しない**。施策2(Reference Digest)は今回のスコープに含めない(効果不明瞭、`USER_DECISION_REQUIRED`継続、OPEN_ITEMS残件) | `PRODUCTION_WIRED`(Trend Synthesis限定) | 同上 | 2026-09-08 |
| retry/fallback整合 | Diagnostic Full Retry(`build_diagnostic_retry_prompt()`)はoriginal_prompt(Focus Module込み)へ診断sectionを追加するだけで、`COMMON_BLOCK_TEMPLATE`/`build_common_block()`を再呼び出ししないため、retry後もmodeは自動的に保持される。Evidence Compression Editor・Point Overlap QA・Fact Checker・Ledger Deviation Checkerはいずれも生成済み記事テキストのみを操作し、prompt再構築を行わないためmode非依存で無変更のまま機能する | `PRODUCTION_WIRED`(既存機構の無変更利用、コード追跡+単体テスト+実runtime evidenceで確認) | 同上 | 2026-09-08 |
| Research/Ledger供給経路 | Production Writerへの入力Ledgerは、既存の承認済みTheme 2 Ledger(手動作成・手動修正)をファイルとしてそのまま使う手順が正式initial path。既存自動Research pipelineの出力形式との互換性は**未検証(不明)**。自動供給経路への統合は今回配線しない(`USER_DECISION_REQUIRED`、OPEN_ITEMS残件) | `USER_DECISION_REQUIRED`(現状=手動供給のみ) | 同上 | 2026-09-08 |
| Trend Gate・Mode判定の記録 | Trend Gate 6条件+Mode判定2問チェックリストの判定は自動化せず、`run_writer_for_theme(..., trend_gate_checklist=...)`で渡された**手動判定結果**を、`run_metadata.json`(新規ファイル、既存`articles_run_summary.json`のschemaは変更しない)へそのまま記録する仕組みのみ実装した | `PRODUCTION_WIRED`(記録のみ、自動判定なし) | 同上 | 2026-09-08 |
| 据え置き4件 | Mode判定自動化・News Ledger自動供給・Reference Digest・Diagnostic Full Retry診断語彙拡張は、いずれも今回の配線の必須条件ではないため仕様化していない(Open Item/Trial候補として残置、下記OPEN_ITEMS.md OPEN-112行参照) | `USER_DECISION_REQUIRED`(defer継続) | 同上 | 2026-09-08 |
| A2日本語タイトル供給 | `generate_a2_segments`(`er003_v1_n3_01_tts_generate.py`)が要求する日本語タイトルは、モジュール内ハードコード辞書`JAPANESE_TITLES`(既存3テーマのみ登録)から取得する設計。新規テーマでは既存前例(`EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03_REPORT.md`B-2)に倣い、英語タイトルの直訳(新しい主張・数字を追加しない)を人手作成し`tts_gen.JAPANESE_TITLES.update({theme_id: ...})`で実行時登録する方式を正式initial pathとする。自動翻訳・専用QAは新設しない(A-Family全体の共通gap、Trend固有ではない) | `DECIDED`(直訳の人手供給を正式initial pathとして採用。自動化はOPEN-137として`DEFERRED`) | `FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01_REPORT.md`§8.1/§8.9 | 2026-09-09 |
| theme→artifact連続性 | A2 level(§8)・B1B level(§9)ともにTTS→Assembly→Audio Validation Gate(既定OFF/opt-in ON両方)→標準player完走を確認し、theme→artifact連続性(人手介在3箇所=Mode判定・Ledger供給・日本語タイトル供給を除く)を実証済み(2026-09-09)。B1B Key Phrase 5は既存Key Phrase選定経路での差し替え(`work to do`/「まだ取り組むべき課題」)を経て完走 | `DECIDED`(実証完了、Fable受入=Gate 3「article→audio連続性」evidence充足) | `FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01_REPORT.md`§9 | 2026-09-09 |

## 通常News(Major/Daily News)Reference仕様 — 2026-09-08新設(ユーザー決定A-UDR-5、FAMILY-A-DAILY-NEWS-REFERENCE-FORMALIZATION-01)

A Family(Discovery/Why + News)のうち、Trend Synthesisではない通常
News(Major/Daily News)について、既にDECIDED/PRODUCTION_WIRED済みの
既存A2/B1共通骨格(11パート構造・Writer共通経路・Point Balance・Fact
Safety・Spoken-first数値原則・Comment Contract・Key Phrase Contract・
Audio構造)がそのまま適用されることを正式化した(ユーザー承認、
2026-09-08、A-UDR-5)。以下は本節固有の新規仕様ではなく、既存各節への
参照+「通常Newsに適用される」ことの明記であり、内容自体は各参照先
節が正本(重複転記しない)。B1-A等のobsolete仕様、Trend Synthesis専用
仕様(Focus Module・Engagement原則・Trend Gate等)は本節へ混ぜない。

| 適用対象 | 参照先(CURRENT_SPEC.md内) | 状態 | 根拠管理ID |
|---|---|---|---|
| 全体構造(11パート) | 「CEFR-A2構造・音声仕様」節、「B1」節 | `DECIDED` | ER-003-A2-STRUCT-02〜04、ER-003-A2-SPEC-FREEZE-01 |
| Writer共通経路(`COMMON_BLOCK_TEMPLATE`) | 上記に同じ(News専用のWriter分岐は存在しない) | `DECIDED` | ER-003-A2-B1-N3-01 |
| B1本文生成方式(B1-B Direct Generation) | 「B1(独立生成Natural Spoken News English)」節 | `DECIDED` | ER-003-B1-B2-SCOPE-FIX-01 |
| Point Balance | 「Cross-level仕様」節 | `VALIDATED across Sports/Health/Household` | ER-003-A2-B1-N3-01、ER-003-SPOKEN-FIRST-03 |
| Fact Safety(Verified Fact Ledger→Fact Checker→Ledger Deviation Checker v2) | 「Cross-level仕様」節 | `DECIDED`(`PRODUCTION_WIRED`) | ER-003-A2-B1-N3-01、ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02、ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12 |
| Spoken-first数値原則 | 「Cross-level仕様」節 | `DECIDED` | ER-003-A2-B1-N3-01 §14、ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01 |
| Comment Contract(C1〜C4) | 「CEFR-A2構造・音声仕様」節、「B1」節 | `DECIDED` | ER-003-A2-STRUCT-02〜04、ER-003-B1-NOVEL-AUDIO-01系 |
| Key Phrase Contract | 「Key Phrase」節 | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-02、ER-003-B1-NOVEL-AUDIO-01系 |
| Audio構造(Point Notification/pause/SFX/TTS安全機構/Assembly) | 「Cross-level仕様」節、「Audio Assembly」節 | `DECIDED` | ER-003-POINT-NOTIFICATION-01、ER-003-A2-B1-N3-01 |
| News固有の視点付与層(Layer3 News Focus Module+Point Role hint、Mode判定基準) | (本節では規定しない、内容は書かない)。比較Trial-06(Hanshin Ledger固定、focus_hint NG率50%[3/6] vs baseline NG率100%[6/6])完了 | `VALIDATED(Trial)`止まり。**現行Production採用案は2026-09-09ユーザー決定により不承認**(NG率50%はProduction採用水準ではない、既存仕様全体との重複・競合整理未了)。考え方自体はREJECTEDではなく再改善中(A3-UDR-3の再改善、PM/Reconciliation Gate完了後に着手) | FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06(Trial)、OPEN-112行/OPEN-135行(2026-09-09ユーザー決定、再改善中) |
| News記事(日本語Entertainment読み物)のEntertainment生成方式 | (本節[通常News=英語A2/B1構造]の対象外。Trial P7方式[日本語800〜1000字、Verified Fact Ledger不使用]固有の正式仕様として本行に記載する)。方式定義(Production上の意味): 1. Original generation(P7 Promptで初回記事を生成) 2. Entertainment revision(逐語:「この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。」) 3. Further entertainment revision(逐語:「この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。」) 4. **2回目revision(上記3)の結果を最終記事として使用する**。3回目以降のrevision(Trial呼称R3)はProduction標準に含めない(Trial実施の事実としてのみEvidence保存)。model=`gpt-5.6-luna`(`er006_model_routing_contract_01.WRITER_MODEL`と同一値)・reasoning effort=`high`・OpenAI Responses API `previous_response_id`連鎖(userメッセージは修正指示文のみ、developerメッセージは会話文脈に既存のため再送しない)。Trial内呼称との対応(仕様名ではない注記): Trial呼称`R1`=Entertainment revision、`R2`=Further entertainment revision、`R3`=Production標準に含まれないTrial限定呼称。**配線先Production経路: 未確定**(2026-09-24 Phase 0 recon: 日本語Entertainment読み物記事[本方式]を生成する既存Production経路はCURRENT_SPEC上に存在しない[該当なし]。ER-002系Japanese生成経路は2026-08-06付でER-003アーキテクチャへ全面移行済みの`HISTORICAL`。既存Production Writer経路[B-Family Voices A2/B1、`er012_b_family_production_runner_01.py`等]はVerified Fact Ledger必須・Focus Module・Voice Cards・`MAX_WRITER_ATTEMPTS=3`retry・Analytical Leakage Check等のGate群を持つ英語主体の生成経路であり、本方式[Ledgerなし・単純な修正指示連鎖]とは構造が異なる。新規Production module設計要否はFable/ユーザー判断待ち)。Evidence(逐語Prompt・12記事全文・比較判断根拠): `docs/evidence/news_iterative_r2_adoption_2026-09-24/` | `PRODUCTION_WIRED`(配線、2026-09-26 Fable Gate 3判定)。記事品質はユーザー確認を代替しない。**経緯(2026-09-24ユーザー正式採用時点)**: 当初`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`(未充足: 配線先Production経路の確定・実装・retry/fallback/regeneration整合・Validator・音声化前Article出力・Production runtime evidence・regression/integration PASS。**追記(2026-09-25、`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`)**: 日本語R2自体の自動生成[Original→R1→R2]は引き続き未配線[本行のまま]だが、その「完成品」を受け取る入口は`er012_e_family_entertainment_two_level_runner_01.py`(`--ja-article <完成R2ファイルpath> --slug <slug>`)として定義・実装済み[path+sha256+由来管理IDをentry_point.jsonへ記録]。当面は人手で選んだ完成R2ファイルをこの入口へ渡す運用)。**追記(2026-09-26、`NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01`、ユーザー確定事項に基づきB3配線と同時にJA Writer自動生成配線を実施)**: 「配線先Production経路: 未確定」は解消。正式フローを`Research→Full Fact Ledger→AIが中心Storylineを1つ決定→B3(4テスト)→Selected Fact Brief→Writer(本方式Original→R1→R2)→Advanced→Standard`とし、Research→Full Fact Ledgerの直後に新設「Storyline決定+B3 Fact選定(LLM 1 call)」ステージ(`er019_family_x_storyline_b3_fact_selection_01.py`、Full Ledgerを入力に中心Storylineを1つ決定し、B3の4テスト[Test1:削除してもStoryline理解可能か→YESなら原則除外/Test2:他Factとの因果に実際に使われるか→NOなら原則除外/Test3:Storyline上の重要な「なぜ?」に必要か→NOなら原則除外/Test4:「面白い/具体的/数字がある/珍しい/補足として便利」だけで残していないか→YESなら原則除外]を全FactへLLM 1 callで適用し、Selected Fact Brief[目安3〜5件、6件以上はrecheck_note必須]を出力)を追加した。本方式(Original→R1→R2)のP7 Prompt・developer message・Revision指示(r1/r2)は`er019_family_x_ja_writer_o_r1_r2_01.py`へ逐語移設(sha256一致をtestで検証)し、Writerへの入力素材(旧: Sonnetが手書きした2〜3文の中立素材)をSelected Fact Briefへ置換、「テーマ：」行はB3が決定したStorylineの1行へ置換した(P7本体・語数目安・出力形式・Revision方式自体は無変更)。正式入口`er019_family_x_entertainment_production_runner_01.py`(`--theme <Research起点topic> --slug <slug> --out-dir <dir> --stage research|ledger|storyline_b3|writer|advanced|standard|all --stop-after <既定standard>`)がResearch/Full Ledger/Storyline+B3/JA Writer/Advanced/Standardを一気通貫実行する(scaffold/TTS/assemble/player関連の関数は本runnerに一切実装されておらず、Standard完成で構造的にMandatory STOPする)。Meta「Muse human concierge」でRuntime evidence取得済み(`er019_output/family_x_b3_production_wiring_01/run_01/`、詳細は`NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01_REPORT.md`)。**追記(2026-09-26、Fable Gate 3最終判定)**: Gate 3 24/24項目充足、配線Statusを`PRODUCTION_WIRED`へ更新した(記事品質のユーザー確認を代替しない)。生成された記事(R2/Advanced/Standard)は引き続きユーザー確認待ち(Mandatory STOP、音声化・scaffold等の後工程は未実施、`OPEN_ITEMS.md` OPEN-183)。**追記(2026-09-27、`NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01`、Fable Gate 3判定)**: JA Original/R2の各段へFull Ledger照合Fact Check+must-fix retry+issue persistenceを`er019_family_x_ja_writer_o_r1_r2_01.py`(`JAFactCheckStopError`)へ配線し、`PRODUCTION_WIRED`(Stage 1)。English側(`er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage`)にもmust-fix retry+origin判定(JA由来なら`JARecheckRequiredError`でSTOP、盲目retryなし)を実装。Meta run_02・Hormuz run_02の実API runtime evidenceで実発火を確認(Hormuz run_01で英語Advanced段まで伝播していたLedger外一般化をJA段で捕捉・解消)。新規unit test 77件PASS、全体regression1291/1292 PASS(残り1件は本タスクで正当に編集済みの未commit差分検知のみ)。英訳段(Advanced/Standard)Promptへのmust-fix受け口追加のみで、Prompt本文自体は無変更。commit`6087e764`。詳細`docs/pm/RESULT_PACKET_FXJ.md`、`DECISION_LOG.md`同管理IDエントリ。 | `NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`(2026-09-24)、`NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01`(2026-09-27、JA段Fact Check+must-fix retry配線、Stage 1)、関連Trial: `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01`/`NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02`、DECISION_LOG.md同管理IDエントリ、`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`(入口定義追記)、`NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01`(2026-09-26、Storyline決定+B3 Fact選定[LLM 1 call]新設・JA Writer自動生成配線・正式runner実装) |
| Entertainment英語版生成方式(Advanced) | Advanced = Natural English Adaptation。Target level = CEFR B1。日本語完成Entertainment記事(Original→R1→R2のR2)→Natural English Adaptation(`NEWS-JA-TO-EN-ADAPTATION-TRIAL-01` arm3 Prompt、developer/共通block/NATURAL ENGLISH arm block)。Editorial structure/angle/metaphor/surprise/endingを維持。新規Fact・一般論の追加禁止。Production module: `er003_v1_n3_01_advanced_adaptation_generate.py`(`generate_advanced_adaptation()`)。Prompt本文はarm3のDEVELOPER/ARM3_BLOCKを逐語のまま使用し、COMMON_BLOCKの記事固有「Preserve…」6bullet(Meta固有angle)のみ記事非依存の一般形5項目(opening expectation/reversal/central metaphor or storytelling device/order of information/ending)へ置換(`ADVANCED_UNCHANGED_PORTION_SHA256`でDEVELOPER/PREFIX/SUFFIX/ARM3_BLOCKの逐語性をimport時assert)。既存Production contract(`# `Title+Main Story+ちょうど2つの`### `節+`## In one line`、出典`er003_v1_n3_01_articles_generate.py`【記事構成】節/`er002_ja_free_markdown_restore_r2.validate_point_structure`)を接尾ブロックとして付与(方式は`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`のCONTRACT_LINESと同一文言)。API呼び出しは`er003_v1_en_direct_vfl_01_generate.run_writer_with_technical_retry()`(構造Gate付きretry、後方互換`developer`引数を追加)、model routing=`PROCESS_MODEL_MAP["NATURAL_ENGLISH_ADAPTATION"]=WRITER_MODEL`(新規追加)。**追記(2026-09-26、`ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01`)**: Advanced語彙ルールv2(一般英語頻度順位約12,000位超を原則平易化候補、A[易しい既知語から意味推測可能な形態・複合語]/B[日本語に定着した外来語]/C[固有名詞・引用符内の実際の呼称]/D[置換すると意味精度・自然さを損なう不可欠語]の4例外、Topic Core Word例外なし・Metaphor専用ルールなし)を`ADVANCED_VOCAB_RULE_V2_BLOCK`としてPrompt本体(ARM3_BLOCKの後、Production contract接尾ブロックの前)へ追加した(Standard v5と同型、`ADVANCED_VOCAB_RULE_V2_SHA256`でimport時assert)。候補語リスト・順位付き改稿passは行わない(方式(i)、モデル自身の語感に依存する直接生成。方式(ii)[改稿pass追加]の要否は次回以降の通常Production Runでの観察後に判断、OPEN-182)。retry(構造Gate)・deviation MAJOR時の再生成はいずれも同一`build_prompt()`を再利用するため自動的に同一ルールが適用される(`docs/pm/recon_advanced_vocab_v2_wiring_01.md`)。v3(Trial-02、Topic Core Word例外+Metaphor専用ルール)はユーザーによりREJECTED、Productionへ一切含まない。**追記(2026-09-27、`NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01`、Fable Gate 3判定、`PRODUCTION_WIRED`)**: 見出し境界Contract(Section boundary rule、`docs/pm/design_family_x_section_segmentation_spec_01.md`§3.1)を`ADVANCED_SECTION_BOUNDARY_CONTRACT`として独立ブロックでPrompt本体へ追加(sha256`bba08c02...`、既存`ADVANCED_VOCAB_RULE_V2_BLOCK`等は不変)。見出し直後に新内容を開始しBridge/予告文は見出し前に置くことを許容する構造。small_bag run_02で先取り0件・Fact tokens一致・両レベルdeviation COMPLIANTを確認、Meta正常ケース回帰でover-correctionなし、Hormuz run_02でも境界OK。設計doc§5の追加mechanism要否条件A〜Dはいずれも非該当。commit`9cec45f1`。 | `APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`(2026-09-24ユーザー正式承認。2026-09-25`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`でProduction module実装・runner配線・Sewer/Meta実runtime evidence取得済み[Meta b1bはE2E完走、Sewerはdeviation check STOPで停止]。**追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`)**: Sewerは元Source不在のためProduction E2E代表記事から除外(ユーザー正式決定)、代表記事はMetaのみとする(詳細OPEN-177(10)、DECISION_LOG.md該当エントリ)。Gate 3全項目未充足のため`PRODUCTION_WIRED`ではない。**追記(2026-09-26、`ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01`)**: Advanced語彙ルールv2をProduction Prompt本体へ組み込み、Production正式経路でMeta記事(`ai_phone_revision2.md`)からAdvanced 1本を実際に生成しruntime evidence取得済み(`er003_output/advanced_vocab_v2_wiring_01/`)。ただしこれは語彙ルール単体のwiring追加であり、Advanced自体の`WIRING INCOMPLETE`状態(Gate 3全項目)は本タスクのスコープ外のため変更しない) | `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`(Meta)、`NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01`(下水道で再現確認)、`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`(2026-09-25、Production module実装・Gate 3判定)、`ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01`(2026-09-26、v2語彙ルール組み込み、v3 REJECTED確定)、`NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01`(2026-09-26、ユーザー正式決定によりAdvancedへの一律14,000語Band等の新設は不採用、既存`ADVANCED_VOCAB_RULE_V2_BLOCK`をそのまま使う方針を確認)、`NEWS-FAMILY-X-SECTION-SEGMENTATION-SPEC-DESIGN-01`(2026-09-27、見出し境界の一般仕様設計doc)、`NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01`(2026-09-27、Advanced見出し境界Contract配線、Fable Gate 3判定`PRODUCTION_WIRED`) |
| Entertainment英語版生成方式(Standard/A2) | Standard = v5「6,000語ライン+自然さ優先」Prompt(頻出上位約6,000語以内は原則そのまま使用可・必要に応じてKey Words/Phrases側で学習補助/6,000語を超える語は、より簡単で自然な表現がある場合は置換を強く優先するが、置換が英文の自然さ・意味を損なう場合は強制しない/固有名詞は別扱い/不可欠な専門語は簡単な代替で意味が失われる場合は残してよい/難語の説明を本文へ追加してStoryを膨らませない)。**「6,000語超を必ず置換」ではない**(例: septic tank/wastewater/artery等は必要語として残り得る。municipalitiesのように自然な簡単語へ置換できる難語は優先的に平易化)。入力はAdvanced(Natural English Adaptation、CEFR B1)の記事本文。Production module: `er003_v1_n3_01_standard_a2_generate.py`(`generate_standard_a2()`、Prompt定数`STANDARD_A2_DEVELOPER`/`STANDARD_A2_PROMPT_V5`、sha256 assert `STANDARD_A2_PROMPT_SHA256`)。**2026-09-25更新(`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`)**: v5 user promptの末尾「Output only…」の直前に構造保持行`Keep the same Markdown structure (the "# " title, the two "### " sections, and the final "## In one line" section); do not add or remove sections.`を追加(語彙・簡略化指示は無変更、`STANDARD_A2_PROMPT_SHA256`更新)。API呼び出しは`er003_v1_en_direct_vfl_01_generate.run_writer_with_technical_retry()`(構造Gate付きretry、Advanced段と統一。旧: `run_writer_no_search()`への独自retry)、model routing=`PROCESS_MODEL_MAP["STANDARD_A2_ADAPTATION"]=WRITER_MODEL`。v1 `REJECTED`(簡略化不十分)/v2 `NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`(到達`VALIDATED`、superseded)/v3 `VALIDATED`(下水道単体)/v4 `REJECTED`(難語→難語置換の再現、頻度帯設計を撤回)/v5 `VALIDATED`(`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01`、Fable参考評価=必要語保持・不自然置換なし・2記事再現)→ユーザーが2026-09-25正式採用。**追記(2026-09-26、`NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01`、ユーザー正式決定)**: v5の文構造簡易化(現行維持)に加え、**firmな6,000語Bandを追加**する。Band除外条件は(1)固有名詞、(2)推測容易な派生語・複合語、(3)日本語として定着している語、の3種のみ(現行v5の"roughly"/"prefer"という弱い表現・単一の「必要語は残してよい」表現から、この3条件へ強度・明確化)。6,000語超でも、無理に置換するとStory・Fact・自然さが崩れる主題語(Topic Core Word、例: sewer/septic等)は、理想形ではないがTrial結果上の現実的運用として残してよい。**不採用**: 10,000語Band/Advanced側の一律14,000語Band/生成後のA/B/C/D単語単位事後置換パス/Promptへの個別語ハードコード(`"flush" into "use"`等の個別例示)のいずれも採用しない。Advancedは一律Bandを新設せず、既存の完成後Vocabulary difficulty adjustment仕様(`ADVANCED_VOCAB_RULE_V2_BLOCK`、`ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01`で`PRODUCTION_WIRED`済み)をそのまま使う。この決定により、`STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01`のS-1(v5維持を採用、Generation-First版は不採用)/S-2(A/B/C/D事後置換パスは外す、Advanced v2ブロックは無変更)/S-3(個別語例示は一般表現へ、Promptへの個別語ハードコードはしない)、および`NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01`のVB-1(Band単独では難易度差が出ないためv5構文簡易化との組合せを採用)/VB-2(v5文再構築+firm 6,000 Band+3除外条件の組合せをユーザーが直接承認、追加Trialなしで採用)/VB-3(主題語はBand例外として保持する既定挙動を採用)は、いずれもユーザー決定済み(上書き)として整理する。Production Prompt文言自体への実装(`STANDARD_A2_PROMPT_V5`書き換え・sha256更新)は`APPROVED_FOR_PRODUCTION`段階であり、配線・runtime evidence取得は未実施(Phase 0事前調査のみ、`docs/pm/recon_vocab_level_production_wiring_01.md`)。**追記(2026-09-27、`NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01`Stage 2、Fable Gate 3判定)**: `STANDARD_A2_PROMPT_V5`の語彙段落を、firm 6,000語Band+3除外条件(固有名詞/推測容易な派生・複合語/日本語定着語、個別語例なし)の生成一体型(事後の一語置換ではない)Prompt文言へ置換した(sha256`cbe73fc4...`、旧`ff860ab6...`)。あわせて`NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01`により見出し境界維持文(design doc§3.2)を追加。Meta run_01 Standard再生成(正式path、COMPLIANT、語数-3.3%、Advanced無変更・v2ブロックsha256不変)、Hormuz run_02(COMPLIANT、+3.8%、境界OK)でruntime evidence取得済み。**観察(正直に記載)**: Hormuzで6k超残存語12語中、固有名詞3語を除く9語(flashy/withdrawal/crude/disliked/Reuters/curtain/shipments/blockade/tanker)が置換されず不変。Fact/Story/構造/語数の受入条件は満たすが、「firm」Bandの実効性はサンプル2記事の限定的証跡(`OPEN_ITEMS.md` OPEN-190)。10,000語Band・Advanced側一律14,000語Band・生成後の単語単位事後置換パス・Promptへの個別語ハードコードはいずれも不採用のまま。commit`e7311d37`。詳細`docs/pm/RESULT_PACKET_S2.md`、`NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01_REPORT.md`§3.2。この語彙・境界実装部分は`PRODUCTION_WIRED`。ただし本行が示す全体E2E downstream(scaffold/TTS/Assembly/Audio Validation Gate/player)の`WIRING INCOMPLETE`状態はそれ自体変更なし(別途Gate 3判定待ち、OPEN-177(10)参照)。 | `APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`(2026-09-25ユーザー正式採用。`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`でAdvanced→Standard→downstream[scaffold/Key Phrase/TTS/Assembly/Audio Validation Gate/player]のProduction正式経路(`er012_e_family_entertainment_two_level_runner_01.py`)へ接続・実runtime evidence取得済み[Meta a2は既存Audio Validation GateがHuman Review Lock対象[外来語"Meta"]segmentによりAssembly段でblock、Sewerはdeviation check STOPのため未到達]。Gate 3全項目未充足のため`PRODUCTION_WIRED`ではない) | `NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01`(v5到達、supporting: v1〜v4の各管理ID)、`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01`(2026-09-25、Production module実装・Gate 3判定)、`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`(2026-09-25、downstream配線・Gate 3再判定)、`NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01`(2026-09-26、firm 6,000語Band+3除外条件をユーザー正式決定、配線未実施)、`NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01`(2026-09-27、Stage 2配線完了・Fable Gate 3判定`PRODUCTION_WIRED`)、`NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01`(2026-09-27、境界維持文配線)、OPEN-177、OPEN-190(新規) |

### Reference記事の正式指定

- **Hanshin(`ER-003-A2-B1-N3-01`)**: 上表の構造・Writer・Fact Safety・
  音声実装のreference実装として正式指定する(`DECIDED`、根拠: ユーザー
  決定A-UDR-5、`FAMILY-A-DAILY-NEWS-REFERENCE-FORMALIZATION-01`)。同一
  管理ID内のHealth(Small Habits, Longer Lives)は同系列のreferenceとして
  併記する(構造・Writer・Fact Safety・音声実装のreference価値のみ、
  ER-003-A2-B1-N3-01)。**Household(crisper drawer)は通常Newsの同系列
  referenceから除外する**(2026-09-08ユーザー決定A-UDR-9、
  `FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01`で新規発見)。理由:
  Householdは単一起点イベント(特定の発表・発生事象)を持たない題材であり、
  通常News(Major/Daily News)の対象として扱わない。Householdは別
  Editorial Type(Discovery/Why系)候補として別途整理する(通常Newsの
  定義をHouseholdに合わせて広げない)。
- **Health(単一起点研究発表がある場合の扱い)**: Healthのうち、単一の
  研究発表(起点となる1つの発表・論文・調査結果)がある場合は、Major/
  Dailyの通常News(Major/Daily News)として扱う(2026-09-08ユーザー決定
  A-UDR-10、`DECIDED`ではなく**運用方針(設計Trial段階)**、根拠:
  `FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01_REPORT.md`)。Major/
  Daily Gateの非対称性(消去法的な判定基準であること)は現状許容する。
  myth-correction候補(通説訂正型)の扱いは保留(`USER_DECISION_REQUIRED`
  継続)。将来Mode自動判定を実装する場合は対称性ではなく排他的・再現
  可能な判定ロジックが必要になる点はOpen Itemとして保持する
  (OPEN_ITEMS.md OPEN-130)。
- **ADD03(イラン/ホルムズ海峡)・A02(英国SNS門限)**: 題材・音声構造の
  referenceに限定する(11パート構造・Preview日本語のみ・Key Phrase
  発話順序の起源としての参考価値のみ、ER-003-A2-STRUCT-02〜04、
  ER-003-A2-SPEC-FREEZE-01)。本文生成コードパス(`er003_v1_iran01_*.py`
  等P-series専用スクリプト)・完成音声は再利用しない。ADD03/A02が使用
  していたB1生成方式(B1-A、B2から派生させる旧2段階方式)は下記のとおり
  obsolete。

### 通常News仕様に含めない(obsolete除外)

以下は既存のREJECTED/置換記録により、通常News仕様には含めない。

| obsolete対象 | 置換先(現行仕様) | 根拠管理ID |
|---|---|---|
| B1-A方式(B2から派生させる旧2段階B1生成パイプライン) | B1-B Direct Generation(Verified Fact Ledgerから直接独立生成) | ER-003-B1-B2-SCOPE-FIX-01(2026-08-17) |
| P-series専用Writer/Audioスクリプト(`er003_v1_iran01_articles_generate.py`等、ADD03/A02専用one-off) | `COMMON_BLOCK_TEMPLATE`(全テーマ共通Writer) | DECISION_LOG.md 5711行、ER-003-A2-B1-N3-01 |
| Natural English Source方式(B2先行生成→B1流用の生成元) | Verified Fact Ledgerから各レベル独立生成(A2/B1とも同格) | 「CEFR(A2/B1/B2比較)」節「生成元」行(`HISTORICAL`表記) |
| 旧Preview分量(4文/67語程度) | 2〜3文程度の短い導入(soft guidance、hard word-count gateなし) | ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01 |
| 旧Key Phrase trim margin 0.20秒 | 0.30秒(cache identity保証付き) | ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23 |
| ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02/WRITER-ARCH-01の設計内容 | 参考資料としてのみ扱う(正式仕様として採用しない) | OPEN-112行(2026-09-04ユーザー決定) |

### Trend Synthesisとの境界

News Focus Module(Trend Synthesis variant)固有のPrompt文言・Counter-
signal/limitation必須化ルール・Trend成立条件・Evidence Strength分類
タグ語彙・Trend Memory・Engagement/Storytelling原則・Reference Digest
は、本節(通常News)には含めない。これらは「## News Editorial Mode
(Trend Synthesis)」節(別Editorial Mode)を参照。

## Family X Writer — Concreteness Control(AN3-T0) — 2026-09-28新設(ユーザー正式決定、`FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01`)

**Status**: `PRODUCTION_WIRED`(2026-09-29、Fable Gate 3=Meta run_03、
`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§E2E Meta run_03。
根拠evidence: `er019_output/family_x_refresh_e2e_01/meta/run_03/
runtime_evidence.json`の`concreteness_an3_block_sha256=
067030ff53ecb76a4d1477a3deace07b3e1fac438a33cb873edbe045cf6927fe`が
Hormuz run_02/03・Meta run_03で一致、AN3-T0 Prompt不変を実測確認)。
2026-09-28ユーザー正式決定により`APPROVED_FOR_PRODUCTION`
(配線完了・Fable Gate 3判定待ち)。Family X JA Original Writer Prompt
(`er019_family_x_ja_writer_o_r1_r2_01.py::build_original_prompt()`)へ、
数字・時刻・固有名詞に関する定性的な抑制指示(AN3=A3+N2、`FAMILY-XY-
CONCRETENESS-CONTROL-TRIAL-01/02`から逐語移設)を`CONCRETENESS_CONTROL_
AN3_BLOCK`として追加した。R1/R2側にはreminder等の追加instructionは付与しない(2026-09-28ユーザー
正式決定。当初Production Wiring時に追加した`CONCRETENESS_CONTROL_AN3_
REMINDER_JA`はTrial-02で検証されていない未Trial追加仕様だったため削除。
AN3はOriginal側のみ[Trial-02=`er039`実測時と同一条件]。R1/R2は既存
Revision指示[`REVISION_INSTRUCTIONS["r1"/"r2"]`]のみ)。

**ユーザー正式思想(逐語)**: 「細かい数字・時刻・過度な精度は極力使わず、
記事理解に本当に必要な数字だけ最小限残す。固有名詞も同様に、理解上
必要なものだけ残す。」**「数字を0にする」とは絶対に定義しない。**
AN2よりAN3を選んだ理由は「0件だから」ではなく「実本文で必要情報を
残しながら不要な具体性をより強く落とせたため」。

**適用path**: `er019_family_x_entertainment_production_runner_01.py`
経由のFamily X JA Writer全経路(通常Original・Original Fact Check
must-fix retry・Original音声記号must-fix retry・通常R1/R2・R2 Fact
Check must-fix retry・R2音声記号must-fix retry・previous_response_id
失敗時のfallback_full_text・`--regenerate-stage writer`)が対象
(全経路が`build_original_prompt()`または3箇所のR1/R2パターンの
いずれかを必ず通る、設計書`docs/pm/design_family_x_concreteness_
an3_t0_production_wiring_01.md` §1a)。**Advanced化(English)Promptは
本タスクで一切変更しない**(`ADVANCED_VOCAB_RULE_V2_BLOCK`は無変更、
Trial限定の英語側抑制追記T1はProductionへ混入禁止)。

**成功条件・QA方針**: 数値カウンタ(Arabic数字・漢数字とも)を成功条件
にしない。既存のLedger Deviation Check(`vfl01.run_deviation_check()`、
Essential Fact・因果関係のMAJOR Deviation判定)を主判定とする。
OPEN-20(固有名詞密度の数値目標REJECTED)とは対象が異なり非衝突
(OPEN-20は数値目標・一般ルール化を却下したものであり、AN3は定性的な
編集方針指示であり数値目標を含まない、設計書§1c)。

**確認用再生成(実API、2026-09-28)**: 専用out-dir
`er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/{hormuz,meta}/`
にてHormuz・Metaの2記事をJA(Original→R1→R2)+Advanced(English)まで
正式path(writer/advanced段階のみ、TTS/ASRなし)で再生成した。
`runtime_evidence.json`に`concreteness_an3_block_sha256`が2記事とも
記録され、`jaw.verbatim_shas()`の値と一致(reminder削除は
`FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md`§16
[2026-09-28、ユーザー決定]参照)。JA Fact Check最終status: Hormuz
Original`LEDGER_COMPLIANT`(1発)・R2`LEDGER_COMPLIANT`(既存1回must-fix
retryでMAJOR解消)、Meta Original`LEDGER_COMPLIANT`(既存1回must-fix
retryでMAJOR解消)・R2`LEDGER_COMPLIANT`(1発)。Advanced Englishも
Meta`LEDGER_COMPLIANT`(1発)、Hormuzは既存Advanced deviation must-fix
retryでMAJOR解消後`LEDGER_COMPLIANT`。費用実測合計¥14.031(上限¥15内)。
既存test(`er019*_test_*.py`143件・`er037*_test_*.py`12件・
`er039*_test_*.py`17件)全PASS、新規test(`er019_family_x_concreteness_
an3_t0_production_wiring_01_test_01.py`17件)全PASS。詳細
`FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md`。

**新規発見(本タスクのスコープ外、修正せず報告のみ)**: Hormuz Advanced
生成で、`h3_count==2`構造Gate([Auto-retry付き])はPASSしたが、その
後段の`split_article_text()`(Main Story導入部の段落数2以上を要求する
既存チェック、自動retry機構なし)に2回連続で失敗した。Meta側は1発で
PASSしたためAN3固有の系統的問題と断定できない(n=1の偶発的な生成
ばらつきの可能性が高い)。この失敗はTTS準備専用の`parts.json`生成に
留まり、Fact Check・Prompt sha256等の本節の証拠には影響しない。詳細
設計書§8-4。

## Discovery/Why(Pool型) — 2026-09-09新設(ユーザー決定、PM-CLOSEOUT-CONSOLIDATION-41、最小節)

A Family(Discovery/Why + News[Major/Daily] + Trend Synthesis)のうち、
Discovery/Why型の対象定義・現状を記録する最小節。判定ロジック自体は
「## Editorial Type Routing(2軸判定)」節を参照(重複転記しない)。

| 項目 | 現在値 | 状態 | 根拠管理ID |
|---|---|---|---|
| 対象定義 | Pool型(Evergreen、特定の1件の最近の出来事に非依存、`POOL_TOPIC_MASTER.md`定義=2軸判定の軸A=Noの正式化) | `DECIDED`(2026-09-09) | FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-02_REPORT.md |
| Layer3 Focus Module(`DISCOVERY_FOCUS_MODULE_BLOCK`) | Trial-05でVALIDATED(A2/B1、既存Point Role hint機構の流用、バイト等価配線案)。Household既存Ledger再利用によるN=3 Article-only Trial-07完了(Gate1=Sonnet推奨`VALIDATED`、REVIEW_REQUIRED率baseline比約5倍増加・Point多様性低下を確認) | `VALIDATED(Trial)`止まり。**現行Production採用案は2026-09-09ユーザー決定により不承認**(REVIEW_REQUIRED増加・Point多様性低下、Ledger注記案は自動採用しない)。考え方自体はREJECTEDではなく再改善中(D2-UDR-1の再改善、Household Ledger FACT-03再検証`HOUSEHOLD-LEDGER-FACT-03-REVERIFICATION-01`と並行) | ER-011-DISCOVERY-4LAYER-TRIAL-05(既存)、FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-TRIAL-07(完了)、OPEN-135行/OPEN-138行(2026-09-09ユーザー決定、再改善中) |
| Discovery固有Research方式(説明源優先順位ガイドライン) | LLM呼び出しを追加しない、既存Ledger構造・タグ体系に従属する優先順位ガイドライン案(未承認候補) | `DEFERRED`(D3) | FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-02_REPORT.md §3/§4 D3 |
| Point Role hint(Discovery版) | Trial-03の接続パターンは技術的に転用可能と考えられるが、Discoveryでのruntime効果は未検証 | `DEFERRED`(D3) | 同上 |
| Engagement/Storytelling原則のDiscoveryへの適用 | Trend Synthesis側でのみA/B検証済み(Trial-10/11)、Discovery側の実施記録なし | `DEFERRED`(D3) | 同上 |
| myth-correction(通説訂正型) | Newsからの除外は確定しない、Discoveryへの追加は候補のまま | `USER_DECISION_REQUIRED`(継続) | 同上 |
| Ledger Deviation Checker専用カテゴリ新設要否 | 既存タグの流用で対応する現行運用を変更しない | `DEFERRED`(D3) | 同上 |
| 保険文(取扱説明書的な断定回避表現)運用注記(2026-09-10) | 保険文抑制Prompt制約案(Part B案1、`cautionary_constrained`)はProduction不採用のまま(2026-09-10ユーザー正式決定、上記Focus Module行参照)。Focus Module Part A本体単独運用で取扱説明書的・保険文的表現が出た場合は、追加Prompt対策Trialを行わず、Human Reviewで目視修正したうえで発生率を観測・記録する(仕様変更ではなく運用方針) | `DECIDED`(運用方針、仕様ではない) | PM-CLOSEOUT-CONSOLIDATION-70(ユーザーA-3回答)、OPEN-135行 |

## Production記事生成コストの報告方式(2026-09-14ユーザー正式決定)

Production記事生成コストの報告方式はPM_GOVERNANCE 15-8(Production 1生成
セット総原価主指標、50:50配賦禁止)に従う。2026-09-14ユーザー正式決定、
運用仕様として追跡。

## Discovery Focus S2(Production、FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01、2026-09-13)

ユーザー正式承認(`APPROVED_FOR_PRODUCTION`、2026-09-13、
`FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01_REPORT.md`推奨案=分割方式P1)に
基づき、Discovery Focus S2(Focusを先に決める→Main Storyを確定する→その
Main Story本文を見てPoint Role Planning→Point生成)をProduction配線した。
実装先: `er003_discovery_focus_staged_production_01.py`(新規モジュール)、
opt-in `editorial_mode="discovery_focus_staged"`(`er003_v1_n3_01_articles_
generate.EDITORIAL_TYPE_MODULE_BLOCKS`へ`DISCOVERY_FOCUS_MODULE_PART_A_BLOCK`
として正式登録)。既存`run_one_pattern`(News Major/Daily/Trend Synthesis/
現行Discovery非staged)は無変更のまま(案P1、バイト不変)。

**正式処理順**: Focus解決 → Stage 1 Main Story生成+Stage 1 QA(Fact Checker
A' → Ledger Deviation+Local Rewrite → Directional Fact Precheck
non-blocking) → [blocking時、`STAGE1_MAX_REGENERATIONS`回までStage 1
再生成] → Stage 2 Point Role Planning(確定Main Story本文を入力、角度hint
なし) → Stage 3 Point生成+Evidence Compression(Points本文のみ)+結合 →
Point Overlap QA/Point Value QA(NG時はStage 2-3のみ再実行、
`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`既存値) → 記事全体Fact Checker A'/
Ledger Deviation+Local Rewrite(+差分QA、OPEN-141既定ON)/Directional
Fact Precheck → OK/NG_REVIEW_REQUIRED確定。

**retry単位・しきい値**: 通常retryはStage 2-3のみ(Main Story固定)。
`STAGE1_MAX_REGENERATIONS=1`(ユーザー確定案1)。Stage 1再生成は以下いずれか
の場合のみ発動する例外的経路: (a)記事全体Ledger Deviation MAJORが
`locate_target_sentence`でMain Story側に位置しLocal Rewrite上限
(`MAX_REWRITE_CYCLES=3`)でも未解決、(b)Stage 2-3再実行が
`POINT_OVERLAP_ARTICLE_RETRY_MAX`回を尽くしてもNGのままの最終フォール
バック、(c)記事全体Fact Checker FAIL(Fact Checker FAIL locus=案(ii)簡略
ルール、Stage2-3 exhaustion後のみStage1へescalate)。いずれも尽きれば
NG_REVIEW_REQUIRED(fail-closed)。

**Main Story固定原則**: Stage 2からStage 3を通じてMain Story本文(Stage 1
確定範囲)は原則不変。ただし既存の安全装置(Ledger Deviation Check+Local
Rewrite、差分QA)がMain Story側1文のMAJOR逸脱を局所修正する場合は例外として
許容する(Stage 1再生成[全文書き直し]とLocal Rewrite[局所修正]は区別し、
後者は既存安全装置の通常動作として扱う)。

**Focus Module本文の採用範囲(重要、既存USER_DECISIONとの関係)**:
`DISCOVERY_FOCUS_MODULE_PART_A_BLOCK`の本文自体は、OPEN-112-A-FAMILY-
4LAYER-PROMPT-DESIGN-TRIAL-05で検証済みのFocus Module Part Aと一字一句
同一である。このFocus Module本文を、Household Ledgerでの現行非staged
`run_one_pattern`単発生成へ一般適用することは、上記「Discovery/Why(Pool型)」
節のとおり2026-09-09ユーザー決定によりProduction不採用のまま(Trial-07で
REVIEW_REQUIRED増加・Point多様性低下を確認、再改善中/未決)。今回の
Production採用は、この一般適用可否とは別軸であり、S2 Staged Generation
との組み合わせでの実測結果(`er011_output/discovery_focus_s2_full_trial_01/`、
Gate 1判定`VALIDATED`)を根拠とした`editorial_mode="discovery_focus_staged"`
限定のopt-inにすぎない。

**Trial専用ファイルの扱い**: `er011_discovery_focus_s2_full_trial_01.py`/
`er011_discovery_focus_part_a_standalone_trial_01_run.py`/
`er011_discovery_stage3_rule_adjustment_trial_09.py`はarchive目的でGitに
残置するが、Production側(`er003_discovery_focus_staged_production_01.py`/
`er003_v1_n3_01_articles_generate.py`)からのimport・参照は一切ない
(Gate 4 Dangling Reference Check該当ゼロ、Grep実測件数は同管理ID
RESULT_PACKET参照)。

Gate 3 runtime evidence(実施結果・費用・commitの詳細)は
`FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01_REPORT.md`参照。

2026-09-14 正常系runtime evidence(`er011_output/discovery_s2_production_
runtime_evidence_02/`)で通常LedgerによるA2完走を確認し、Gate 3全項目
充足によりPRODUCTION_WIRED確定。詳細:
`FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01_REPORT.md`。

## Family C(Future Story)Production — 2026-09-16新設(FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01委任A)

ユーザー正式決定(2026-09-16、Trial-11/12の3 episode[Memory B1/Digital
Twins A2/Digital Twins B1]試聴OK)により、Family C(Future Story)で
Trial検証していた以下2仕様を`APPROVED_FOR_PRODUCTION`とし、Family C正式
Production経路へ配線した(Family A/Bへは横展開しない)。

**対象要素**: Family C(`er013_family_c_future_*`/`er013_family_c_episode_*`
系列)のStory本文TTS分割(segmentation)、およびA2 Comment 1〜3の生成
Prompt/Contract。

**仕様A: Story TTS segmentation原則**(承認原則、運用目安であり
hard capではない): 同一Voiceの自然な連続性を優先する/不要な短segmentを
避ける/Voice変更点では分割する/Comment挿入位置・scene・semantic
boundaryを考慮する/word countだけで機械的に細分化しない/概ね100語以内を
運用目安とし120語を大きく超えない/150〜200語級の長segmentは避ける/
Voice境界による不可避な短segmentは許容する。語数目安
(target_words=100/soft_max_words=120/hard_avoid_words=150)は生成を
ブロックしない。soft_max超過はwarning記録のみ、hard_avoid超過は複数段落に
またがる場合のみ最も近い段落境界へ自動分割し、単一段落で分割不能な場合は
warning記録のみで生成は継続する。記事固有のVoice/scene boundary・
Comment挿入位置は呼び出し側(記事ごとのProduction設定)が指定し、本原則が
固定値で上書きすることはない。

**仕様B: A2 Comment理解ガイド型Contract**(Family C A2限定、B1へは
適用しない): 「聞いてみましょう」「耳を澄ませましょう」等の聞く行為
だけを促すメタナレーションではなく、次の英語理解に必要な具体的context
(現在の場所・状況/人物関係/場面転換/次の英文理解に重要な行動/選択・
対立点)を、必要なものだけ簡潔な日本語(2〜3文・80〜110字程度)で提供する。
禁止・回避: 「聞いてみましょう」「耳を傾けて」「耳を澄ませて」
「注目してみましょう」「これからどうなるでしょう」等の言い回し、雰囲気
だけの抽象的誘導、無内容な予告、結末の先出し、StoryにないFact追加、
不要な長文化。B1 Commentは本Contractを一切参照せず、既存B1 Support経路
(`er003_v1_b1_scaffold_01_generate`、「B1 Support(Preview / Comment
1-4)」節)をそのまま使用する(誤適用防止をコード構造で担保)。

**Production経路**:
- 共通module: `er013_family_c_production_01.py`
  - `plan_story_segments()`(仕様Aの正式実装、`build_flat_voice_chunks()`/
    `classify_quote_voice_window()`/`split_paragraph_by_quotes()`と組み
    合わせて使用)
  - `FAMILY_C_A2_COMMENT_ROLE_JA_1/2/3`・`check_a2_comment_quality()`・
    `generate_family_c_a2_comment()`(仕様Bの正式実装。初回生成・retry・
    regeneration・fallbackのいずれも本関数を経由し、禁止語句検出時は
    同一Contractで内部的に再生成する)
  - `guard_a2_only()`(B1誤適用防止の構造的ガード)
  - Trial script(`er013_family_c_episode_trial_1[012]_*.py`)を一切
    import・参照しない
- runner: `er013_family_c_production_runner_01.py`(A2/B1を`--level`で
  分岐、記事設定は`er013_output/family_c_production/<article>/
  article_config.json`から読み込み、記事固有のVoice keyword・scene
  boundary・Comment content facts等を固定値で上書きしない)。
  `--plan-only`/`--comments-only --no-tts`に加え、フラグ無し呼び出しで
  全体生成経路(Story TTS→ASR整合→Comment→Assembly→Audio Validation
  Gate→player→web_delivery)を実行する。Story TTSは`tts_call_for_voice()`
  経由で既存Production関数(narrator=`generate_narration_snippet_
  verified_strict`、device=`generate_charon_english`、その他は
  article_config `voice_tts_names`で指定したvoice_nameで
  `generate_voice_body_wide_margin`)へ分岐し、いずれも内部にASR検証+
  attempt cascadeを内包する。resumeは`.ok`+`tts_text`のsha256一致判定
  (`resumable_reuse()`)、regenerationは`--only-segments <id>...`が
  該当segmentのwav/.ok/metaのみ削除して強制再生成する
  (`purge_segment_outputs()`)。ASRキャッシュは音声sha256一致時のみ再利用
  (`get_or_run_asr()`、名前のみキャッシュ不使用)。B1経路はA2 Comment
  理解ガイド型Contract(`fam_c.generate_family_c_a2_comment`)を構造的に
  一切呼ばない(`run_comments_stage_a2`はlevel=="a2"分岐からのみ呼ばれる、
  Grep実測で確認)。Key Phrase選定等のcontent curationおよび
  reuse_from/共有Production資産のいずれにも存在しないasset素材の
  from-scratch生成は本Wiring委任のスコープ外(明示的エラーで停止する
  設計、静かに諦めない)。
- test: `er013_family_c_production_test_01.py`

**Status**: `APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`(2026-09-16、
差し戻し1回目時点。根拠: `docs/pm/RESULT_PACKET_WIRING_FAMILY_C.md`
「## 差し戻し1回目」節、`DECISION_LOG.md` `FAMILY-C-SEGMENT-COMMENT-
PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01`エントリ)。**経緯**: 初回
委任(commit `a04c9221`/`0156ceea`)時点のrunnerは`--plan-only`/
`--comments-only --no-tts`のみを実装しており、Story TTS本体(初回生成/
retry/fallback/regeneration/resume)がProduction経路に存在しなかった
ため、Fable受入照合により`PRODUCTION_WIRED`判定を一旦`APPROVED_FOR_
PRODUCTION / WIRING_INCOMPLETE`へ差し戻した。差し戻し1回目で全体生成
経路(上記runner欄)を実装し、Memory A2でresume全体生成(TTS全segment
skip、ASRキャッシュ全件hit、Gate PASS、生成episode wavがTrial-11承認
済みepisode wavとsha256完全一致[316.569秒]、費用¥0)のruntime evidence
を取得した。B1経路がA2 Contractを呼ばないことはGrepで構造確認済み。
**不足**: `--only-segments story_002`によるregeneration(実TTS発火)の
live runtime evidenceは本セッション内で未取得。2回試行したが、いずれも
既存Production TTS関数(`generate_charon_english`、Gemini Batch API
経由)への実呼び出し自体は発生した(CPU使用時間の推移から確認、ネット
ワークI/O待ちで停止していたわけではない)ものの、Batch APIの応答が
90分・15分(2回目)を経過しても完了せず、費用記録(`raw_usage_log.jsonl`)
も一切生成されなかったため、安全側に倒しプロセスを終了した。regeneration
の**コード実装**(`purge_segment_outputs()`が対象segmentのwav/.ok/meta
のみ削除して強制再生成をtriggerすること、`tts_call_for_voice()`が
voice種別ごとに正しい既存Production関数へ分岐すること)は決定的単体
テスト(モック使用)でPASS済みだが、実際にstory_002.wavが再生成され
Gateが再PASSする一連の**live**証跡は未取得(Batch TTS APIの当日の
レイテンシという既存インフラ側の外部要因、本委任のコード欠陥ではない)。
詳細な数値・テスト結果・完了判定12項目チェック表は
`docs/pm/RESULT_PACKET_WIRING_FAMILY_C.md`「## 差し戻し1回目」節参照。
Twins A2「The door opened.」(3語segment、Voice境界+scene boundary保持
のための意図的単独segment)は2026-09-16ユーザー正式決定により現状維持で
採用(追加再TTS・Comment位置変更なし)。

日付: 2026-09-16。

## Family X(Entertainment News)音声構造 — 2026-09-26新設(ユーザー確定ルールのSSOT記録、`PM-USER-DECISIONS-SSOT-CONSOLIDATION-04`)

**Status**: 本節は2026-09-26にユーザーが確定した、Family X(日本語
Entertainment読み物、Original→R1→R2→Advanced→Standardの生成方式。
既存節「News記事(日本語Entertainment読み物)のEntertainment生成方式」
`CURRENT_SPEC.md` L828-830参照)の後工程(3分割・Comment配置・音声
Assembly)仕様である。**追記(2026-09-27、`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01`Stage 1)**:
配線: runner実装済み、runtime evidence取得中。`er019_family_x_audio_plan_01.py`
(article.md分割+Family X用Comment3/4 role+segment順序plan)/
`er019_family_x_audio_production_runner_01.py`(CLI runner、plan/scaffold/
tts/assemble stage、既存Production低レベル関数[`voice01.
generate_charon_english`/`news_tail_fix.generate_news_narration_wide_
margin`/`crosslevel_common.generate_english_segment_with_fallback`/
`n3_tts.generate_a2_japanese_with_reading_safety`等]をそのまま呼ぶのみ、
既存Production module無変更)を実装、unit test 25件PASS、Meta dry-run
(`er019_output/family_x_b3_production_wiring_01/run_01`入力、`--dry-run`、
API呼び出しゼロ)まで完了(commit`32430691`)。実API runtime evidence
(TTS/Assembly実行)はStage 3で取得中。**解釈注記(Stage 1解釈、試聴後に
見直し可)**: 本文2/3の見出しは本文segment内で読み上げる(見出しを
独立segment化しない)。**更新(2026-09-27、`NEWS-FAMILY-X-AUDIO-
PRODUCTION-WIRING-01`Stage 3c、runtime evidenceに基づき見直し)**:
Stage 3bのHormuz実行で、見出し句と本文冒頭の反復をrepetition QA/ASRが
誤検知しHUMAN_REVIEW_REQUIREDへ到達する事象を実測したため、上記解釈を
「見出しを独立sub-segment(`full_story_part2_heading`/
`full_story_part3_heading`、plan_role=HEADING_READOUT)として本文2/3の
直前に分離する」へ変更した(構造・順序・効果音方針そのものは無変更)。
実装はFamily A既存の`point_one_heading`機構(B1B=Aoede経由の
`point_headings.generate()`、A2=`generate_a2_segment_with_slowdown`)を
そのまま再利用し、新規TTS経路は作っていない。見出し→本文間のpauseも
Family A既存定数(`HEADING_TO_BODY_PAUSE_SECONDS_B1`/
`POINT_EXPLANATION_PAUSE_SECONDS`、いずれも0.7秒)を再利用する。
Hormuz実測では、分離後の`full_story_part3`が両level(A2/B1B)とも1回の
試行でクリーンにOK(Stage 3bはB1BのみLocal Rewriteを要した)となり、
故障モード解消の直接的な証拠を得た。対象runner
(`er019_family_x_audio_production_runner_01.py`)のunit testは25→32件
(7件追加)、32/32 PASS。Stage 3dで、この構造のMeta run_01 B1B
(`family_x_b3_production_wiring_01__run_01`)実データでのAssembly完走
(全segment OK、`assembled/Family_X_Audio_B1_FAMILY_X_B3_PRODUCTION_
WIRING_01.wav`・player.html生成済み)を確認した。詳細
`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md`Stage 3c/3d。
ユーザー決定=`APPROVED_FOR_PRODUCTION`。**Status(2026-09-29、Fable Gate 3
判定)**: `PRODUCTION_WIRED`(Meta run_03のruntime evidenceに基づく、
`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§E2E Meta run_03)。
ただし下記項目1(見出し独立sub-segment/HEADING_READOUT)は**W1(2026-09-29)
で撤去済み**であり、現行Production経路は項目6「新記事構造」を参照
(HEADING_READOUTを使わない構造が現行、本項目1の旧記述は履歴として残す)。
Family A
(News Major/Daily/Trend Synthesis)の既存音声仕様(Point One/Two直前
Notification音、Comment役割C1〜C4等)はFamily Aのまま無変更であり、
以下はFamily X固有の差分としてのみ適用する。

1. **音声構造・効果音(SE-1 CLOSED)**: Family Xの構造は
   Comment1 → 本文1 → Comment2 → 本文2 → Comment3 → 本文3 →
   Comment4 → In One Line とし、Commentで自然につなぐ設計を採用する。
   Point One/Two用Notification音はFamily Xでは使用しない。本文1/2/3の
   前後・In One Line前にも新しい効果音は追加しない(現時点では本文以降
   の効果音なし)。まずこの状態で音声化し、ユーザー試聴で「区切りが弱い」
   「流れが分かりにくい」等の問題が実際に出た場合のみ、効果音追加を
   再検討する(`DECIDED`、`APPROVED_FOR_PRODUCTION`。SE-1はCLOSED、
   追加Trial不要、以後USER_DECISION_REQUIREDとして再掲しない)。
2. **本文1/2/3の区切り定義**: 本文1=タイトル+1つ目の見出し直前まで/
   本文2=1つ目の見出し+2つ目の見出し直前まで/本文3=2つ目の見出し+
   In One Line直前まで/In One Line=別枠。Comment配置はComment→本文1→
   Comment→本文2→Comment→本文3→Comment→In One Lineを基準とする
   (`DECIDED`)。50%/25%/25%は理想目安であり、**Validator/Gate化しない**
   (Production記事で明らかなアンバランスが多発した場合のみ再検討する。
   この比率を理由に追加Trial・自動補正を開始しない)。
3. **Section Segmentation(見出し境界)Contract**: 見出しがある場合、その
   見出しで扱う新しい論点・新しいFact・新しい役割の開始文は原則として
   見出しの後に置く(見出し前で次Sectionの具体内容を実質的に開始しない。
   単なるBridge・予告文までは禁止しない)。**追記(2026-09-27、
   `NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01`、Fable
   Gate 3判定、`PRODUCTION_WIRED`)**: 一般Contract(方式A、
   `docs/pm/design_family_x_section_segmentation_spec_01.md`§3.1/§3.2)を
   Advanced(`ADVANCED_SECTION_BOUNDARY_CONTRACT`独立ブロック)/Standard
   (`STANDARD_A2_SECTION_PRESERVE_SENTENCE`境界維持1文)双方のPromptへ
   適用済み(commit`9cec45f1`/`e7311d37`)。small_bag/Meta/Hormuz run_02で
   先取り0件・Fact tokens一致・deviation COMPLIANT・over-correctionなしを
   確認(詳細`CURRENT_SPEC.md`L829/830の該当追記、
   `NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01_REPORT.md`)。
4. **Fact Check方針(実装・配線済み、Stage 1)**: JA Original生成後+JA R2
   確定後のダブルチェック(Full Ledger照合、JA側が正しい場合のみ英訳
   工程でmust-fix retry、JA R2が誤っている場合はJA側へ差し戻し、issue
   persistence込み)を`er019_family_x_ja_writer_o_r1_r2_01.py`
   (`JAFactCheckStopError`)・`er012_e_family_entertainment_two_level_
   runner_01.py`(`JARecheckRequiredError`)へ実装・配線した(**追記
   2026-09-27、`NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01`、Fable
   Gate 3判定、`PRODUCTION_WIRED`**、commit`6087e764`)。Meta/Hormuz
   run_02の実API runtime evidenceで実発火を確認(Hormuz run_01で英語
   Advanced段まで伝播していたLedger外一般化をJA段で捕捉・解消)。固定費
   約¥2.20/記事・latency約110秒(改善候補は`OPEN_ITEMS.md` OPEN-189)。
   関連: `OPEN_ITEMS.md` OPEN-187(`CLOSED`)、OPEN-189。
5. **ja_source MAJOR時の暫定retry拡張(案B、`APPROVED_FOR_PRODUCTION`・
   Gate 3待ち、2026-09-29追記、`FAMILY-X-REFRESH-E2E-PRODUCTION-
   WIRING-01`W6)**: English側(Advanced/Standard)のDeviation Checkが
   `origin=ja_source`のMAJORを検出した場合、従来は`JARecheckRequired
   Error`で即STOPしていた(fail-closed、「安全≠成功」原則どおり)。
   これに加え、**暫定的なProduction retry拡張**として、その具体的な
   指摘をJA Writer O(`er019_family_x_ja_writer_o_r1_r2_01.run_ja_
   writer_o_r1_r2`)のOriginal段へmust-fixとして差し戻し、JAを
   Original→R1→R2→Fact Checkの全体で**1回だけ**再生成し、Advanced/
   Standardを再実行する経路を`er012_e_family_entertainment_two_level_
   runner_01.py::run_writer_stage()`(薄いwrapper)へ配線した。**JA差し
   戻し1回後もMAJORならSTOPする**(fail-closed原則は維持、無限retry
   はしない。Advanced/Standard合計でJA再生成は1回、Standard段での発生
   も同じ枠を消費)。Checker Prompt本体(`DEVIATION_PROMPT_TEMPLATE`等)・
   severity判定基準・Ledger/Deviation設計・JA Writer Prompt本文は本拡張
   で一切変更していない(既存`build_must_fix_block`機構の再利用のみ)。
   本対応は**Checker過剰品質問題の正式解決ではなく暫定的な運用拡張**
   であり、Checker(Ledger/Deviation Check)自体の再設計は`OPEN_ITEMS.md`
   OPEN-233として`DEFERRED (non-blocking)`(GPT-6 Trial/Production
   Routing判断後に再開)。ユーザー明示決定(2026-09-29)により
   `APPROVED_FOR_PRODUCTION`。**Status(2026-09-29、Fable Gate 3判定)**:
   `PRODUCTION_WIRED`(Meta run_03のWriter段runtime evidenceで、
   Standard段origin=translation MAJOR→must-fix retry1回で解消、
   Advanced段は初回`LEDGER_COMPLIANT`で案B自体は非発動という実データを
   確認。Hormuz run_03では発動しAdvanced段でCOMPLIANTへ解消した実績も
   ある)。**暫定retry拡張であり、Checker(Ledger/Deviation Check)過剰
   品質問題の正式解決ではない**旨は維持する(OPEN-233参照)。詳細:
   `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§W6/§E2E Meta
   run_03、`docs/pm/design_family_x_refresh_e2e_production_wiring_01.md`
   §9-W6、`DECISION_LOG.md`同日エントリ。
6. **新記事構造(途中Heading廃止・忠実英訳・段落境界3分割・Comment1→
   本文1→Comment2→本文2→Comment3→本文3→Comment4→In One Line・
   Heading Readout撤去・In One Line短文、`APPROVED_FOR_PRODUCTION`→
   `PRODUCTION_WIRED`、2026-09-29追記、`FAMILY-X-REFRESH-E2E-PRODUCTION-
   WIRING-01`W1、Fable Gate 3判定)**: `FAMILY-X-TRANSLATION-SEGMENTATION-
   NO-HEADING-TRIAL-01`(Trial、`er045_*`)で検証した、見出し生成指示を
   除いた忠実英訳+段落境界のみでの決定論的3分割(`split_family_x_
   article_text_v2()`)+短いIn One Lineを、`er003_v1_n3_01_advanced_
   adaptation_generate.py`(`generate_family_x_faithful_translation()`/
   `generate_family_x_in_one_line()`)・`er003_v1_n3_01_scaffold_
   generate.py`(`split_family_x_article_text_v2()`)・
   `er003_v1_n3_01_standard_a2_generate.py`(`generate_family_x_standard_
   a2_no_heading()`)・`er012_e_family_entertainment_two_level_runner_
   01.py`(`run_writer_stage()`切替+`_family_x_ensure_split_or_paragraph_
   retry()`新設)・`er019_family_x_audio_plan_01.py`/`er019_family_x_
   audio_production_runner_01.py`(v2 split・v2 segment順序、Heading
   Readout sub-segment撤去)へ配線した。旧`split_article_text()`
   (Family A本体が現役利用)は無変更のまま残置し、Family X経路からは
   構造的に到達不能であることをAST解析ベースのテスト(`test_run_writer_
   stage_family_x_path_never_calls_old_split_article_text`)で確認
   (OPEN-228の解消根拠)。Advanced/Standard段落数不足時は共通ヘルパーで
   1回だけmust-fix再生成し、それでも3分割不能ならSTOP(fail-closed、
   既存retry軸とは独立)。Meta run_03のruntime evidence(`timeline.json`:
   Comment1→Full Story Part1→Comment2→Part2→Comment3→Part3→Comment4→
   In One Line、`Heading`ラベル0件、`HEADING_READOUT`/`NG_ACCEPTED_
   AFTER_RETRY`grep0件)でStandard/Advanced双方の完成を確認。詳細:
   `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§W1/§E2E Meta
   run_03、`FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_
   REPORT.md`。

**運用上の既知制約(2026-09-29追記、コード未変更、OPEN-234)**: 音声生成
runner(`er019_family_x_audio_production_runner_01.py`)の`source_dir`は
`--slug`/`--run`のみから`er019_output/{slug}/{run}`として導出され、
JA/writer段の`--out-dir`(例: `er019_output/family_x_refresh_e2e_01/
{slug}/{run}`)と不一致の場合、Audio段実行前に該当ディレクトリ一式を
`er019_output/{slug}/{run}`へ手動コピーする必要がある(コード変更なし、
Hormuz/Meta run_03で実施済みの運用)。恒久対応(CLI引数追加等)の要否は
ユーザー判断(詳細`OPEN_ITEMS.md` OPEN-234)。

根拠: ユーザー決定(2026-09-26、`PM-USER-DECISIONS-SSOT-CONSOLIDATION-04`)。
2026-09-27追記の配線根拠: `NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01`、
`NEWS-FAMILY-X-SECTION-SEGMENTATION-SPEC-DESIGN-01`、
`NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01`、
`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01`(Stage 1)。
2026-09-29追記(5)の根拠: ユーザー明示決定(`FAMILY-X-REFRESH-E2E-
PRODUCTION-WIRING-01`W6、案B採用)。2026-09-29追記(6)の根拠:
`FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01`(Trial検証)、
`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`W1(Production配線)・
Fable Gate 3判定(Meta run_03)。

## Family Z(Fiction)— 2026-09-26新設(ユーザー確定ルールのSSOT記録、`FICTION-FAMILY-Z-PRODUCTION-E2E-01`)

**Status(旧表記、2026-09-26以前)**: 本節の内容(1〜7)は2026-09-26に
ユーザーが逐語で確定したProduction仕様である。ただしProduction配線
自体は**未実装**(Phase 0[read-only事前調査]完了のみ、
`USER_DECISION_REQUIRED`。理由: 権利論点[下記1-8-2参照]および構造論点
[Family Cとの関係・Connected Speech segment_id規約・In One Line新規
設計]が未解決)。Trial結果(`VALIDATED`等)をこの仕様の`PRODUCTION_WIRED`
と誤認しないこと。

**Status(2026-09-27同期)**: 仕様(1)〜(4)[Z-1権利Gate/Z-2/Z-3/Z-4]は
`APPROVED_FOR_PRODUCTION`(2026-09-26決着、`OPEN_ITEMS.md` OPEN-185・
`DECISION_LOG.md`参照)。Production wiring: テキスト工程 WIRING IN
PROGRESS(2026-09-27着手)、音声工程は読み解決Phase 2後。
`PRODUCTION_WIRED`ではない。**Family Z Writer/音声経路の新設時に、
TTS記号正規化(`PRODUCTION_WIRED`)と読み解決resolver
(`APPROVED_FOR_PRODUCTION`、Phase 2実装中)を必須適用する。**

1. **Family定義**: Fiction系を既存Future Family(Family C=Future Story)
   から独立させ、**Family Z = Fiction**(Literature/Public Domain文学・
   Real Story・Historical True Crime)とする。基本方式は外部Seed方式で
   あり、AI完全自由創作を標準方式にしない。Family Yは将来Voices系を
   想定した別Familyであり、Family Zとは分離管理する。
   **既存記述との相互参照**: `DECISION_LOG.md`
   `PM-USER-VALIDATION-DIRECTION-RECORD-01`(9324行付近)が記録する
   「Future→Fiction再定義は未確定」は、本Family Z新設により整理される
   (Family C=Future Story個別の再定義ではなく、Fiction専用の新Family
   Zを別途新設する方針。Family Cの位置づけ自体は無変更)。
2. **Story内容の基本方針**: 元作品・元エピソードを無理に変更しない
   (人物名変更・舞台変更・結末変更・不要な設定変更をしない。知って
   いる物語を英語で聞く体験にも価値がある)。許容する編集は、尺に
   収めるための脇筋削除・登場人物整理・背景説明圧縮・心理描写圧縮・
   重複場面削除のみ。中心Story・因果関係・重要な人物関係・結末・
   原作の魅力を壊さない。
3. **Seed必須条件**(4項目、Seedは以下すべて満たすこと): (a)
   Original/primary textを直接確認できる、(b)**日本国内でPublic Domain、
   または日本国内で適法に利用可能であること**(米国PDは必須条件にしない。
   海外向け配信・提供を将来行う場合のみ、その対象法域のrights確認を
   追加する。原作がPDでも、現代の第三者翻訳・英訳・挿絵等は別著作物
   として扱い、権利未確認のものは流用しない。Family Zのadaptationは、
   確認済み原文/正式Seedから自前生成する)、(c)短編化しても中心Story
   を保持できる、(d)Story品質基準4項目中原則3項目以上を満たす。検索
   要約だけをSeedにしない。一次資料を確認できない候補はNG。
   **旧: 「日本法+米国法双方で利用可能」(2026-09-26
   `FICTION-FAMILY-Z-RIGHTS-RECHECK-01`で根拠記載なしと確認、同日
   ユーザー決定[日本人向け・日本国内向けサービスであるため、米国PDを
   必須条件にしない]で上記(b)へ置換。走れメロスは日本でPD確認済み
   のため初回Family Z E2E対象として継続、差し替え不要)。**
   **rights記録ブロックの説明**: Seedのrights記録には、日本国内status
   (必須条件)に加えて、米国等の他法域のstatusを**条件ではなく記録
   事項として**残す(例: 走れメロスはURAA回復により2035年末まで米国
   保護の可能性があるが、これは法的最終判断ではなく記録事項であり、
   日本国内向けサービスとしてのSeed採否には影響しない)。
4. **Fiction共通の外国人名ルール(正式)**: 外国人の人名は本文中では
   First name/Last nameのどちらか一方だけを使用する(例: Eugene Aram
   → Aram、Richard Houseman → Houseman、Daniel Clarke → Clarke。
   First name側への統一も可)。例外(フルネーム可)は、(i)同姓人物が
   複数いて区別不能、(ii)片方だけでは事実関係が曖昧、(iii)固有名称
   としてフルネーム自体が重要、のいずれかに該当する場合のみ。単なる
   慣習でフルネームを使わない。適用実績: 「The Second Skeleton」
   (`er018_output/fiction_real_story_and_true_crime_trial_01/
   true_crime/story.md`)への追従修正(commit `6c0b0e02`、意味・Fact
   不変、Daniel Clarke/Eugene Aram/Richard Houseman → Clarke/Aram/
   Houseman)。
5. **Story Type metadata**: `story_type`フィールドを持つ。
   `literature`(Literature/Fiction)= UI表示なし・音声冒頭追加なし。
   `real_story`= UI「REAL STORY」表示・音声冒頭に固定文言"This is a
   true story."を追加。`true_crime`= UI「TRUE CRIME」表示・音声冒頭に
   固定文言"This is a true crime story."を追加。Writer本文へこの説明
   文自体を書かせず、Production側がmetadataに基づき自動的にUI表示・
   音声introを切り替える。
6. **TTS**: Family Zでも既承認TTS Production仕様
   (`TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01`、本
   CURRENT_SPEC.md該当節)をそのまま使用する。attempt1→即時attempt2→
   10分cool-down→attempt3→NGならLocal Rewrite+Natural English QA
   (Luna 1 call)。Connected Speechは5 role(Full Story/Comment/
   Preview/Topic intro/In One Line)へ適用し、Heading readout/Key
   Phraseへは適用しない。
7. **PRODUCTION_WIRED条件**: 以下すべてを満たすこと。Production正式
   初回path/retry・fallback・regeneration経路が存在すること、
   story_type分岐・外国人名ルール・TTS仕様(上記6)が実装されている
   こと、runtime evidence・tests・CURRENT_SPEC/DECISION_LOG/
   OPEN_ITEMS反映・Git commit・Dangling Reference Checkが揃っている
   こと。Trial script(text生成のみ)だけで成立した場合は
   `PRODUCTION_WIRED`と認めない。

**追記(2026-09-26、ユーザー正式決定、`PM-USER-DECISIONS-SSOT-CONSOLIDATION-02`、OPEN-185の構造論点(2)(3)(4)を解消)**:
- **Z-2(Family CとFamily Zの関係)**: Family Z専用runner(新設)を作るが、
  Family C既存関数(`plan_story_segments()`等)を再利用する方式とする。
  `APPROVED_FOR_PRODUCTION`。Family C本体を不要に変更しない。
- **Z-3(In One Line)**: 既存In One Line Promptを、Fiction向けに最小変更
  して流用する。`APPROVED_FOR_PRODUCTION`。新しい独立機構を追加で作らない。
- **Z-4(Story本文とDialogue Voice)**: Story本文は単一canonical text
  (Voiceごとに複製しない)。ただしDialogue部分(会話文)は、既に承認済み
  のspeaker/male-female Voice assignmentルールに従う。`APPROVED_FOR_
  PRODUCTION`。既存Voiceルールを再利用し、新しいVoice仕様を作らない。
  **参照先(Fable確認結果、2026-09-26)**: Family C(Future Story)で
  運用実績のあるDialogue Voice割当機構 — narrator=Aoede、登場人物台詞=
  Erinome/Charon等を`classify_quote_voice_window()`(話者判定、
  `er013_family_c_production_01.py` L66-95、引用符前後windowのキーワード
  一致で判定)で割り当て、記事ごとに`voice_tts_names`で人物→Voiceを
  指定する(DECISION_LOG `USER-TEST-FINAL-AUDIO-BATCH-06` 委任B/C、
  Status=`VALIDATED`[Trial]、既知課題OPEN-156[引用符境界またぎ誤判定、
  `classify_quote_voice_window`は当該修正の汎用化版]、性別印象はSSOT
  未記載のためピッチ推定で代替した経緯あり[DECISION_LOG該当エントリ
  7826行付近])。Family ZはZ-2の方針どおりこの既存関数を再利用し、
  新しいVoice仕様を作らない。ユーザーが別ルールを意図している場合は
  訂正を受け付ける。
- 上記によりOPEN-185の未決論点(2)(3)(4)は解消。残るのは(1)権利論点
  (走れメロス米国著作権status)のみで、別管理ID
  `FICTION-FAMILY-Z-RIGHTS-RECHECK-01`で確認中。Production配線
  (`PRODUCTION_WIRED`)は未着手のまま。
- **Seed必須条件(a)の運用整理(F-4、`FICTION-REAL-STORY-AND-TRUE-CRIME-
  TRIAL-01`、ユーザー正式決定)**: 上記項目3(a)「Original/primary textを
  直接確認できる」には、(a)本文を直接確認できる、(b)出所が明確、(c)
  rightsを確認できる、(d)当該資料にないFactを他の要約から継ぎ足さない、
  の4条件を満たすPD犯罪記録集(例: Newgate Calendar系)を含めてよい
  (`The Second Skeleton`はNewgate Calendar系代替Source[Camden Pelham
  "The Chronicles of Crime"]を使用済み)。「一次資料以外は絶対NG」という
  より狭い読み方をしていた場合は、本4条件による整理へ読み替える(旧来の
  厳格な読み方自体を否定するものではなく、PD記録集が上記4条件を満たす
  場合の扱いを明確化する追記)。
- **外国人名ルール(項目4)の適用範囲確認(F-3、`FICTION-REAL-STORY-AND-
  TRUE-CRIME-TRIAL-01`、ユーザー正式決定)**: 同Trialでは「True Crimeは
  事実改変なしを優先し実名を全保持する」という代替案がFable推奨として
  `FICTION-REAL-STORY-AND-TRUE-CRIME-TRIAL-01_REPORT.md`にのみ記録されて
  いたが、本SSOT(CURRENT_SPEC/OPEN_ITEMS/DECISION_LOG)には未反映のまま
  だった。ユーザーは今回、この代替案を**不採用**とし、True Crimeを含む
  全Story Typeへ本項目4の外国人名ルール(原則First/Last一方のみ、例外は
  3条件)を適用することを確定した(superseded by Family Z人名ルール、
  2026-09-26)。

**Phase 0事前調査結果(事実記録、判断はしない)**:
`docs/pm/recon_family_z_production_e2e_01.md`(commit `5284391b`)参照。
要旨: (a)現行E2E候補「走れメロス」(太宰治、1940年公表・1948年没)は
Trial-02の権利確認が日本法のみで、米国法(URAA)ではCornell Public
Domainチャートに基づく判定で2035年末まで保護の可能性が高い
(2036年PD)。(b)Fiction専用のProduction entry pointは存在せず、最も
近い既存機構はFamily C(`plan_story_segments()`/A2 Comment仕様B/
Key Phrase共有module/Assembly〜player経路)だが、Family Cは"Future
Story"専用設計であり、In One Line相当のsegmentがFamily Cに存在しない。
(c)`story_type`フィールド・外国人名ルールの自動チェックは既存コード
に存在しない。(d)`er020_tts_retry_local_rewrite_01.py`の
`resolve_narrative_role()`はsegment_id完全一致判定のため、Family C
既存の命名規約(`story_001`等)ではConnected Speechが適用されない
(Family Zで新設する場合も、segment_id命名を規約に合わせるかresolver
側へパターン追加するかの判断が必要)。

日付: 2026-09-26。

## Family体系(2026-09-27ユーザー決定、`PM-FAMILY-SYSTEM-MIGRATION-ABC-TO-XYZ-2026-09-27`)

**Status**: ユーザー決定のSSOT反映(2026-09-27)。コード変更・Production挙動変更は伴わない。

- **Active Production Family = X/Y/Z**。開発中心は現時点でFamily X
  (Entertainment News)とFamily Z(Fiction)。Family Yは将来Voices系を
  想定した別Familyであり(本ファイル「Family Z(Fiction)」節参照)、着手済み
  実装は存在しないため、不要にFamily Yの新規開発を始めない。
- **Legacy/Backup = Family A/B/C**(本節より前に定義された既存Family。News
  Major/Daily・Trend Synthesis・Discovery/Why等のFamily A Editorial Type、
  B-Family(Voices)、Family C(Future Story)を含む)。Family A/B/Cは今後の
  Active Production Familyではなく、バックアップ・過去資産として保持する
  だけとし、以後は以下4条件に従う。
  1. Family A/B/Cを最新仕様へ追従させない。
  2. Family A/B/C向けに新規実装を行わない。
  3. Family A/B/CをRegression対象として無理に更新しない。
  4. 必要であればread-onlyの参照元として使うだけとする(例: Family Z
     Z-2/Z-4がFamily C既存関数`plan_story_segments()`/
     `classify_quote_voice_window()`を再利用する場合等)。
- **Family C「Writer出力Validator(Layer 2)新設」(`OPEN_ITEMS.md`
  OPEN-191)は、上記2により実施不要(legacy化)と確定した**
  (`OPEN_ITEMS.md`当該行のStatus更新参照)。
- **共有module(共通機構)の扱い**: `er003_audio_tts_asr_safety.py`の
  TTS記号正規化Layer 1・3・4、Key Phrase共有module等、Active Production
  Family側で共通利用できる形の共有moduleを優先する。その変更が結果的に
  Family A/B/Cの経路へも及ぶ場合、共有層側の変更自体は妨げない。ただし
  Family A/B/C個別のコード(Writer/QA/Validator等の固有モジュール)は
  個別に新規変更しない。**注記**: `TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-
  PRODUCTION-WIRING-01`Phase 2(commit`19e638b5`)は本決定より前に実施済み
  であり、Family A本文Writer・Family C Writerへの禁止記号Prompt予防
  (Layer 1)追加を含むが、これは本決定以前の変更のためロールバックせず、
  legacy側への最後の追従として扱う(詳細は`DECISION_LOG.md`
  `PM-FAMILY-SYSTEM-MIGRATION-ABC-TO-XYZ-2026-09-27`エントリ参照)。
- 既存のFamily A/B/C仕様記述(本ファイル内の該当節、B-Family(Voices)/
  News Editorial Mode/通常News/Discovery/Family C(Future Story)等)は、
  削除・書き換えを行わず**legacy仕様(参照用)**として残置する。
- 根拠: ユーザー決定(2026-09-27、
  `PM-FAMILY-SYSTEM-MIGRATION-ABC-TO-XYZ-2026-09-27`)。

## Cross-level仕様(A2/B1/B2共通)

以下はA2の検証で発見・試作したが、**特定レベル固有ではなく番組全体
(A2/B1/B2)に適用する編集・音声品質原則**として正式化したもの。
既存のB1/B2完成音声を今回一括で再生成することはしない。今後の新規
生成・再assemble時から適用する。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| Preview原則 | ニュース全体のテーマ・問題意識・聞く価値・最後まで聞きたくなる問いを示す。後続本文で聞かせたい具体的な答え・詳細な数字・重要な転換点や結論を先出ししない。A2ではComment1/2がListening Focusとして機能するよう、Previewとの情報重複を特に避ける。**2026-09-07追記(ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01)**: B1 Preview(`er003_v1_b1_scaffold_01_generate.py::PREVIEW_ROLE`、`er003_v1_n3_01_scaffold_generate.py`が`b1s.PREVIEW_ROLE`として再利用する現行B1 Preview生成経路)へ、「Previewは2〜3文程度の短い導入にしてください。要点を先出ししすぎず、この回で何を聞くのかが自然に伝わる内容を優先してください(記事の内容により多少の増減は許容します)」という分量段落を追加した(soft guidance、hard word-count gateではない、旧Previewとの相対指定[「現行の1/2〜1/3」等]や「必ず2文」のような固定文数は含めない)。既存の先出し禁止・turning point非開示・Comment1/2重複回避の原則は無変更。Theme 2 B1記事でのRuntime evidence(Production正式経路、実API呼び出し)で2文・46語・253字のPreviewが生成されることを確認した(旧Preview[同一記事・同一Comment1/2で以前実測]は4文・67語・405字)。A2側のPreview仕様(2文程度、80〜110字目安)は本タスクでは無変更、同一記事のA2 Previewを1件実際に再生成し従来どおり(2文・85字)であることを確認した(A2/B1は別モジュール・別定数のため、この変更はB1にのみ影響する) | `DECIDED`(`PRODUCTION_WIRED`) | ER-003-CROSSLEVEL-AUDIO-01/02(A01/A02/ADD03の3記事で再現確認)、ER-003-A2-SPEC-FREEZE-01、ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01(B1分量段落、ユーザー`APPROVED_FOR_PRODUCTION`2026-09-07) | 2026-08-12、2026-09-07追記 |
| 日本語解説・Comment文での制作内部ラベル禁止 | 日本語のComment/解説文(A2 Comment1〜4・Preview・japanese_title、B1 Support等)では、「Part 1」「Point 2」のような制作内部のsegment名・章番号ラベルを使わない。「物語の前半」「後半」「最初に紹介した内容」等、リスナーが単独で理解できる自然な日本語へ言い換える。No.4(pool_n4_supermarket)のA2 comment_2で、内部ラベル「Part 1」がそのまま残った結果、TTSは正しく発話していたにもかかわらずJapanese ASRが恒久的に不一致になりHuman Reviewへ滞留する実例が発生したことを受けて明文化した。今後の新規生成に適用し、既存の完成済みトピックへの一括遡及適用はしない(OPEN-68の既存方針に準拠)。機械的な検出・記録は下記QA/Human Review節の「日本語canonical textの外来語/制作内部ラベル検出」を参照 | `DECIDED` | ER-009-JA-FOREIGN-TOKEN-GATE-01 | 2026-08-26 |
| Key Phrase発音品質(3条件) | 以下3条件を同時に満たす: (1) Meaning/contextual prosody(本文での意味に合ったイントネーション・stress) (2) Phoneme integrity(語末子音等の必要音素を自然に保持) (3) Phrase grouping(単語ごとに分断せず1つの意味単位として自然に読む)。個別単語パッチではなくこの共通原則で生成する。機械QAだけで自然さPASSとせず、主観的音声品質はユーザー判断を最終とする | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-04(Come on/Go ahead/Brent crude oil)、ER-003-A2-AUDIO-AB-01(A02の5件へ適用、ユーザー承認)、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| 英語見出しのTTS方式 | Point One/Point Two/In One Line等の英語見出しは、見出し文字列そのものをTTS inputへ渡し、英語として自然に読ませる。「見出しを渡さずinstructionだけで発話させる」方式は使用しない | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-04 | 2026-08-12 |
| ポーズ(「ポイント解説」→Preview) | 0.7秒 | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-01/02(3記事で再現) | 2026-08-12 |
| ポーズ(Point One→Point Two) | 0.8秒 | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-03提案、ER-003-A2-AUDIO-AB-01で実装・確認 | 2026-08-12 |
| ポーズ(In One Line→Outro) | 0.8秒 | `DECIDED` | 同上 | 2026-08-12 |
| ポーズ(A2 Comment、英語→日本語) | 1.0秒 | `DECIDED` | ER-003-A2-AUDIO-01以降、無変更 | 2026-08-12 |
| ポーズ(A2 Comment、日本語→英語) | 0.8秒 | `DECIDED` | 同上 | 2026-08-12 |
| Comment前後の効果音 | 専用効果音は入れない(ポーズのみ) | `DECIDED` | ER-003-A2-AUDIO-01以降、無変更 | 2026-08-12 |
| Outro音量 | 最新の減衰方針(Introへのgain matching後、心理音響ベースの追加減衰を2段適用、単純な振幅比ではなく人間聴覚上のバランスを優先)を共通mix ruleとして採用。既存B1/B2完成音声は一括再生成しない | `DECIDED`(方針として) | ER-003-CROSSLEVEL-AUDIO-01〜04、ER-003-A2-AUDIO-AB-01、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| Point Notification | Point OneとPoint Twoの直前に、専用のNotification音(`universfield-new-notification-07-210334.mp3`、既存のKey Phrase/Full Story Notificationとは別音源、A2/B1共通)を挿入する。Point番号を音声で明言しない(「Point One.」「第一に」等は不使用)。Notification→semantic heading→本文の順で、Notification直後に追加の余白は入れない(Notification音源自体の余韻をそのまま使う) | `DECIDED` | ER-003-POINT-NOTIFICATION-01、ER-003-A2-B1-N3-01(Sports/Health/Householdで無修正のまま安定動作を確認) | 2026-08-17 |
| Point semantic heading | Point One/Twoの本文直前に、その回答・視点を要約する短い見出し(記事生成プロンプトが返す`###`見出しをそのまま使用、追加のLLM呼び出しは不要)を置く。見出し文字列は実際にTTS inputへ含めて発話させる(英語見出しのTTS方式と同じ考え方)。B1は見出し・本文ともAoede、A2も見出し・本文とも既存の単一Aoede構成を維持する | `DECIDED` | ER-003-A2-POINT-HEADING-AUDIO-01(A2)、ER-003-B1-NOVEL-AUDIO-01-VOICE系(B1)、ER-003-A2-B1-N3-01(3ジャンルで再現) | 2026-08-17 |
| Point Balance(長さの扱い) | 目標30〜60語、許容25〜70語を**診断的な目安**として使う。hard capにはしない。PointをMain Storyの反復("第二の本編")にせず、別角度・背景・意味・示唆を短く示す、という役割基準を優先判断とする | `VALIDATED across Sports/Health/Household`(hard ruleへの昇格はしない) | ER-003-SPOKEN-FIRST-03(A02単独で検証)、ER-003-A2-B1-N3-01(3ジャンルでこの目標範囲内に自然収束することを確認、hard capとしては未採用のまま) | 2026-08-17 |
| Point Balance(言い換えによる重複の禁止・強化) | Writer prompt(`COMMON_BLOCK_TEMPLATE`、`er003_v1_n3_01_articles_generate.py`)へ、(1) Main Storyの中心的なlogic・結論を語彙だけ変えて再説明することの明示的禁止、(2) Pointが追加すべき内容の具体例拡張(切り口/示唆/背景/**心理/社会的含意/別の因果/実生活上の解釈**/意味づけ)、(3) 「Pointを書く前にMain Storyの主要論点を特定し、それを避けて構成する」という生成手順、(4) Point One・Point Two同士が異なる役割を持つことの明示、を追加した。新Fact追加禁止・Ledger範囲内・既存の長さ目標(30-60/25-70語)は無変更。No.8実Topic/実Verified Fact Ledgerを使った実Writer API A/B比較(各条件n=4、`er008_n8_point_prompt_ab_24.py`)で、Point-Full Story lexical overlap率(`er008_point_overlap_qa_18.lexical_overlap_ratio`)の平均が0.293→0.244へ低下、overlap QA閾値(0.40)超過による要retry率が25%(4件中1件)→0%(4件中0件)へ低下した(サンプル数が小さいため傾向の確認に留まる)。定性的にも、旧prompt条件の高overlap事例(overlap=0.538)はFull Storyの電子ゲート機能説明をほぼ再掲していたのに対し、新prompt条件では同じFactに対し「これは航空会社自身の自己申告であり、独立した効果検証は示されていない」という一段深めた視点を新Fact追加なしで加えていた | `PRODUCTION_WIRED`(prompt反映済み、テスト`er008_n8_point_prompt_strengthen_24_test_01.py`8件PASS、実API A/B比較で効果を確認) | ER-008-N8-FINAL-CLOSEOUT-24 | 2026-08-29 |
| Spoken-first Number Treatment | Verified Fact Ledgerは常にexact factを保持する。spoken narrative側は、精度自体に意味がない数字を、丸め(round)・概数化(approximate)・方向化(directionalize)してListening easeを優先してよい。分類は2軸: Importance(`ANCHOR`/`SUPPORTING`/`DISPENSABLE`)、Exactness(`EXACT_REQUIRED`/`APPROXIMATE_OK`/`DIRECTION_ONLY`)。スコア・日付・記録・健康研究の結果・安全閾値など、精度そのものが意味を持つ数字はEXACT_REQUIREDのまま維持する | `DECIDED` | ER-003-A2-B1-N3-01 §14(A2/B1双方へ適用、3ジャンルで運用確認) | 2026-08-17 |
| Fact Safety(共通) | Verified Fact Ledger(記事ごとに1つ、A2/B1で共有)→独立Fact Checker(web検索付き、`PASS`/`REVIEW_REQUIRED`/`FAIL`の3値)→Ledger Deviation Check(`LEDGER_COMPLIANT`/`LEDGER_DEVIATION`)の3段構成を、A2/B1双方の標準QAとして使う。Supportは新しいFactを追加しない。特に scope expansion・causal strengthening・policy/pilotの混同・unsupported comparison・invented connectionを避ける。**2026-09-01正式改定(ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12、ユーザー正式Decision)**: Fact Checkerのverdict="REVIEW_REQUIRED"(fact_checker_prompt_template_r3.txtの定義=「確認できない具体的主張、解釈、引用風表現など(矛盾とまでは言えない)」)は、**原則non-blocking advisory**として扱う。記事生成・QA工程は継続し(status判定に使わない)、内容(`fact_qa.json`のcontradictions/unsupported_specific_claims/notes)はそのまま記録した上で、最終artifact提示時に「Fact Checker参考指摘」として記事本文とは別に簡潔にユーザーへ提示する(指摘箇所・理由・明確なFact errorか/scope・interpretation・certainty nuanceかを明記、学習者向け本文へは混ぜない)。verdict="FAIL"(同テンプレート定義=「信頼できる情報と明確に矛盾する」、明確なFact error・unsupported number・actorの誤り・事実関係の逆転・強いunsupported causality・重大なscope distortion・安全性上重大な誤りに相当)は引き続き**blocking**。**Production実装**: 従来コードはverdict(REVIEW_REQUIRED/FAILとも)を`fact_qa.json`へ記録するのみでstatus判定に一切使っておらず、FAILであっても自動的にはblockingになっていなかった実装漏れが判明したため、`er003_v1_n3_01_articles_generate.py::run_one_pattern()`にverdict=="FAIL"時のみ`NG_REVIEW_REQUIRED`を返しLedger逸脱チェック以降を実行しない分岐を追加した(Ledger Deviation Checker MAJOR残存・Point overlap未解消と同じfail-closedパターン)。REVIEW_REQUIRED/PASSは従来通りLedger逸脱チェックへ継続する(回帰テスト`er010_no9_factcheck_policy_and_point_compression_diagnostic_12_test_01.py`4件で分岐を確認)。**役割の区別**: Fact Checkerは独立Web検索によるexternal factとの整合性判定、Ledger Deviation CheckerはVerified Fact Ledgerとの整合性判定であり、両者のMAJOR/blocking判定を混同しない(Fact Checker REVIEW_REQUIREDはLedger Deviation CheckerのMAJORとは独立で、Local Rewrite Loopのトリガーにもならない、既存の意図的な設計) | `DECIDED`(`PRODUCTION_WIRED`、2026-09-01) | ER-003-A2-B1-N3-01、ER-003-N3-ROOT-FIX-01/VERIFY-01、ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12(non-blocking advisory化・FAIL blocking実装) | 2026-09-01 |
| Ledger canonical_en_spelling(日本語固有名詞の公式英語表記) | Failure mode: 「日本語情報源由来のLedgerに日本語表記しかない固有名詞(人名・チーム/組織名・地名・施設名等)を、Writerが実行ごとに推測でローマ字化し、Fact Checkerに到達しなければ検出されない」(`FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-TRIAL-DESIGN-01`で定義)。対策としてVerified Fact Ledgerへ、任意フィールドとして`canonical_en_spelling: <日本語表記> = <English>`行を追加できる(既存Ledger[この行が無いもの]・英語一次情報源テーマ[Health/Household等]には一切影響しない=非発火)。**Research/Ledger作成の実態**: 現状、News Ledger作成は自動Pythonパイプラインではなく、Ledger作成担当(Sonnet)がWebSearch/WebFetchで手動作成する運用である(上記「News Editorial Mode」節「Research/Ledger供給経路」行と同じ実態、`FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-TRIAL-DESIGN-01`1-2節で確認済み。`generate_test.py`のNAME_GLOSSARY機構は無関係な別番組専用スクリプトの死蔵コードであり現行Production経路には存在しない)。よって本項目は「存在する自動パイプラインへの自動フック」ではなく、(1)Ledger作成時に呼び出す再利用可能な関数群(`er011_open146_ledger_canonical_en_spelling_production_01.py`: 固有名詞抽出[Web検索を使わない通常LLM呼び出し1回]→公式英語表記confirmation[既存Production関数`r3.make_writer_research_fn()`を無改変で再利用したWeb検索1回]→Ledgerへの追記)の提供、(2)次回News Ledger作成時からこれらを使うことをSOPとして明記、の2点で構成される。**Writerへの伝達**: `build_common_block()`/`COMMON_BLOCK_TEMPLATE`自体は無改変のまま、Ledgerテキストに`canonical_en_spelling:`行がある場合のみ「記載があればその英語表記をそのまま使用し、自己判断で別のローマ字表記を作らないこと」という1文をLedgerテキスト自体へ追記する(`append_canonical_spelling_instruction_if_present()`、`er003_v1_n3_01_articles_generate.py::run_theme()`のLedger読み込み直後に配線。行が無い場合はbyte不変)。**Fact Checkerへの伝達**: `r3.build_fact_check_prompt()`へ後方互換オプション引数`canonical_spelling_block`(既定""、OPEN-131の`voice_attribution_block`と同型パターン)を追加し、Ledgerにcanonical_en_spelling行がある場合のみ「記事本文の固有名詞表記がLedger記載の公式英語表記と一致するか確認する」照合項目を追加した(既定""でFact Checkerプロンプトはbyte不変、verdict語彙`PASS`/`REVIEW_REQUIRED`/`FAIL`・判定閾値は無変更)。**検証**: `FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15`で実測(条件F、N=6・60箇所)人名綴り一致率100%(条件A〜E統合33.1%不一致→条件F 0%不一致、Fisher p=6.31×10⁻⁷)、Point Overlap Gate指標・fact利用率・Fact Checker到達率の悪化なし。**未完了(Gate 3)**: 本配線でのrealAPI runtime evidence(実News Production run)は次回News生成時に取得予定(新規記事テーマはPM_GOVERNANCE.md 13節に基づきユーザーが選定してから着手)。既存Production Ledger(`er003_output/n3_01/*/research/verified_fact_ledger.txt`等)への遡及適用は行っていない(`USER_DECISION_REQUIRED`、次回Ledger作成時から適用) | `PRODUCTION_WIRED`(配線実装・オフライン回帰テストは完了。2026-09-13、PM-CLOSEOUT-CONSOLIDATION-101、Fable判定でNews Family実発火2件[Trial-15/16]+Gate3チェックリスト12/13充足を根拠に`APPROVED_FOR_PRODUCTION`から格上げ。他Family[Discovery/Trend Synthesis/B-Family Voices等]は自然N増しで継続観測、詳細は`OPEN_ITEMS.md`OPEN-146行・`DECISION_LOG.md`該当エントリ参照) | ユーザー決定2026-09-12「#12 A-Family/News Ledger公式英語表記のProduction採用⇒採用」、`FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15`(VALIDATED)、`FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-TRIAL-DESIGN-01`、`OPEN-146-LEDGER-CANONICAL-EN-SPELLING-PRODUCTION-WIRING-01` | 2026-09-13 |
| Ledger Deviation Checker v2(判定基準の再設計) | 旧判定(Ledger文言とのlexical/scope的な厳密一致を暗黙に重視)は、意味を変えないparaphrase・A2/B1向け簡略化・Evidence間のbridge sentence・一般的な情景描写までMAJORとして誤検知していたことがNo.9実データで判明した。`changed_fact`/`changed_scope`/`changed_causality`/`changed_certainty`/`changed_number`/`changed_actor`/`changed_negation`/`changed_comparison`/`changed_time`/`unsupported_new_claim`の10種類の意味上のFact差分のいずれかが明確にtrueの場合のみseverityをMAJORにできる(全てfalseならMINORへpost-hoc自動降格、overall_statusはprogram側でMAJOR残存有無から再計算しモデルの自己申告に依存しない)よう`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`のprompt/schemaを再設計した。自然なparaphrase・出典名の一般化・意味を変えない情景描写・bridge sentenceは、MINOR/MAJORいずれにも該当しない(deviationとして報告しない)。関数シグネチャ・戻り値の主要キー(`parsed.deviations`/`parsed.overall_status`)は既存Production呼び出し側と後方互換。意図的に危険な9種のfixture(数値/主体/scope/因果/確信度/否定/比較/時期/新規主張の改変)は全てMAJOR検知を維持することを確認済み(`er009_ledger_deviation_recalibration_02_test.py`) | `PRODUCTION_WIRED` | ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02 | 2026-08-29 |
| ジャンル再現性 | 上記のScaffold役割・Point Notification・semantic heading・Voice分離・difficulty区別・Full Audio組み立て・Fact Safetyの一式が、Sports(Hanshin)・Health(Small Habits, Longer Lives)・Everyday Practical(Household crisper drawer)の3ジャンルで無修正のまま機能することを確認した | `DECIDED`(validation evidenceとして) | ER-003-A2-B1-N3-01 | 2026-08-17 |
| Cross-Level Consistency Check(A2/B1片側修正の禁止) | No.18で、B1のみVerified Fact Ledgerを精密化(OPEN-108)した後、共有Ledgerを使うA2側が旧Ledger由来の不正確な記述("hard-to-resist habit"等)を残したまま一定期間放置される事例(OPEN-109)が発生した。再発防止として、以下を正式ルール化する。**対象領域**: Research/Verified Fact Ledger、Writer共通仕様、Support生成仕様、Key Phrase仕様、QA/Validator仕様、TTS retry/fallback仕様、TTS共通仕様、Fact Checker運用。**ルール**: 上記いずれかをA2/B1どちらか一方について変更した場合、変更者は変更完了時点で必ずもう一方のレベルへの影響有無を明示的に確認する。影響がある場合(例: 共有Ledgerの内容変更、共有Prompt/Validator/fallbackコードの変更)は両レベルへ反映し両方を再QAしてからcloseする。影響が無い場合(例: 片方のレベル専用segment・専用voice経路のみに閉じた変更)は、なぜ影響しないかをcommit message・DECISION_LOGへ明記する。**片側だけ修正してCloseすることは禁止**(もう一方のレベルへの影響確認自体を省略した状態でのclose不可)。本ルールはSSOT運用ルールであり、自動チェックコードは現時点で未実装(→OPEN_ITEMS.md、将来的な静的監査の余地) | `DECIDED` | ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04 | 2026-09-02 |

これらのポーズ・共通定数は、現状B1組立スクリプト側で記事ごとに
個別定義されている(一元化された共通定数モジュールはまだない)。
共通定数化そのものは今回のスコープに含めない([OPEN_ITEMS.md](OPEN_ITEMS.md)参照)。

### Audio Implementation Detail(実装詳細、サービス仕様ではない)

以下はAudio生成パイプラインの実装詳細であり、番組の聞こえ方・サービス
仕様そのものを変更するものではない。理由・比較検討は[DECISION_LOG.md](DECISION_LOG.md)の
「Implementation Hardening」区分を参照。

| 項目 | 現在値 | 根拠Decision |
|---|---|---|
| English Key Phrase trim safety margin | **0.30秒**(Key Phrase専用、A2/B1共通。2026-08-17に0.08→0.20秒、2026-09-03に0.20→0.30秒へユーザー正式決定のうえ拡大した。他segment[Preview/Comment/Title等]には波及しない。他segmentの既定値は0.08秒ではなく、2026-08-21のER-005-E2E-TTS-ANALYSIS-FIX-01でNARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS=0.35秒へ変更済み[本行は従来「0.08秒のまま」と誤って記載されていたstaleな記述を訂正]。Primary[Minimal instruction]・Fallback[English language lock]の両方が`repro01.generate_key_phrase_component_verified()`内で同一定数を明示的に渡す[`er011_no18_tight_speech_and_trim030_production_wiring_23_test_01.py`で固定]) | ER-003-N3-ROOT-FIX-01、ER-011-NO18-KEYPHRASE-TRIM-030-PRODUCTION-WIRING-12、ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23 |
| A2 Key Phrase英語音声のAssembly時re-crop | **行わない**(`er003_v1_n3_01_assemble.py::load_a2_sources()`はKey Phrase英語音声[`kp{rank}_en.wav`]をgeneration-timeの状態のままAssemblyへ渡す。旧仕様は`tight_speech_only()`で語頭・語末を再cropしており、これがgeneration-timeに確保した0.30秒marginを事実上打ち消し、No.18 A2 Key Phrase 5「be powered off」で語末の無声摩擦音/f/がmargin無しでAssembleされる原因になっていた[Trial-15で発見、ユーザーが試聴のうえ正式承認]。B1側[`load_b1_sources()`]は元々この再cropを行っておらず[ER-008-N7-BASELINE-RESET-AND-MIDDLE-DEFER-01]、この変更でA2もB1と同じ挙動に揃う。`tight_speech_only()`の関数定義自体[`er003_b1_p7c_audio.py`]は他script参照があるため削除しない) | ER-011-NO18-A2-TIGHT-SPEECH-ONLY-REMOVAL-TRIAL-15(検証)、ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R(候補音声で先行使用、Trial条件scoped)、ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23(Production正式配線) |
| Key Phrase Master Audio Storeのcache identityとtrim policy | Key Phrase英語ComponentのMasterAudioKey(`er006_audio_cost_pilot_02_shared_narration.py::ensure_key_phrase_english_component()`)の`style_instruction_version`に、trim marginのpolicy version(`KEY_PHRASE_TRIM_POLICY_VERSION`、現在値`"v2_margin030"`)を含める。`MasterAudioKey.EQUALITY_FIELDS`は生成時のsafety marginそのものを識別子に含まないため、このversion文字列を含めない場合、0.20秒時代([2026-08-17〜09-02]に生成された既存99件、いずれも`audio_processing_version`/`style_instruction_version`="v1")の資産が、0.30秒への変更後も同一textの新規リクエストへ誤ってcache hitしうる状態だったことを本タスクで確認した。今後`KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS`を変更する場合は、このversion文字列も必ず更新すること(さもないと同じ問題が再発する)。No.18 Key Phrase 5「be powered off」の既に0.30秒版へ昇格済み・ユーザー承認済みの資産は、新versionのキーへ移行済み(同一sha256で継続利用、無駄な再TTSなし) | ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23 |
| TTS style instruction責務分離 | 共通style instructionに、Point One/Point Two/In One Lineを読み上げさせる指示(`POINT_LABEL_FIDELITY_RULE`)を無条件に含めない(既定で除外、必要な一括生成呼び出し元だけが明示的に有効化できるopt-in設計)。現行コードベースにfull-program一括TTS呼び出し元は存在しない | ER-003-N3-ROOT-FIX-01 |
| 短いJapanese phraseのminimal instruction fallback | 標準経路(JAPANESE_STYLE_PREFIXを使った生成)が既定回数不合格の場合、最小限instructionへ自動フォールバックする(英語Key Phraseに既存の仕組みと同じ考え方を日本語の短いフレーズにも拡張)。標準経路が成功している場合は追加呼び出しなし。標準経路が不合格を繰り返す場合のみ、fallback分のTTS/ASR呼び出しが追加発生する | ER-003-N3-ROOT-FIX-01 |
| TTS/ASR normalization共通部品 | `er003_audio_tts_asr_safety.py`をAudio共通安全部品として位置づける。ただし2026-08-17時点で、ER-003-A2-B1-N3-01/FIX-01で発見・実装した個別のnormalization処理(curly quote正規化、Markdown太字除去、数字表記ゆれ吸収、Key Phrase複合語対応等)の一部は、まだこの共通モジュールへ統合されておらず、N3専用スクリプト(`er003_v1_n3_01_tts_generate.py`)内に留まっている。**未統合**(→[OPEN_ITEMS.md](OPEN_ITEMS.md)) | ER-003-A2-B1-N3-01、ER-003-A2-B1-N3-01-FIX-01 |
| TTS Instruction/Spoken Text分離(Structured Separation) | **目的**: Gemini TTSが時々、style instruction(話し方の指示)を読み上げ対象の本文と混同し、instruction自体を発話・パラフレーズしようとする(instruction leakage、`INVALID_ARGUMENT`エラーや異常長hallucinationとして観測)。この混同を防ぐため、TTSへ渡す入力(`er003_b1_p4c_audio.build_tts_prompt(text, style_prefix)`)を、`=== STYLE INSTRUCTIONS (do not speak) ===`/`=== TEXT TO SPEAK ===`という明示的なdelimiterで区切る構造(Structured Separation)にする。**期待動作**: style_prefix(話し方の指示、voice/speaker/tone/pacing/narration characterの要求含む)とtext(実際に読み上げる本文)は、どちらも内容・語数・意味を一切変更しない。変更するのは区切り方のみ。standard path・fallback path(minimal instruction)の両方に同じ原則を適用する。**禁止事項**: style instruction本文・speaker指定・voice・tone・pacing要求・narration character・spoken text本文を変更すること(区切り方以外の変更は本Decisionのスコープ外)。Gemini公式`system_instruction`フィールドは、TTSでの対応が公式ドキュメントに記載されておらず実機でも不安定(500 INTERNAL)なため採用しない | ER-005-AUDIO-INSTRUCTION-SEPARATION-01 |
| Gemini 3.8 Flash-Lite TTS(`speech_metadata`構造化方式)の位置づけ | **`APPROVED_FOR_PRODUCTION`(2026-09-27、ユーザー正式決定)。ただし`PRODUCTION_WIRED`ではない**(Gate 3の配線・回帰・runtime evidence全項目完了までは現行Production方式[上記Structured Separation、gemini-2.5-pro-preview-tts/gemini-3.1-flash-tts-preview]のまま稼働継続する。現時点でコード・SDK・API呼び出しの変更は一切無い)。**採用範囲(段階導入)**: Family Xのみ先行(Hormuz等Family X経路限定)。Family A/B/C(legacy)は新規配線対象外。Family Z(TTS未実装)はFamily X完了後に別判断、今は配線しない。**role別style**: Stage3の最小6-role案(TOPIC_INTRO/PREVIEW/COMMENT/FULL_STORY/HEADING_READOUT/IN_ONE_LINE、`TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01_REPORT.md`§22.3)を初期Production仕様として採用(抑揚・トーン最適化は別Trialとして後日)。実測根拠: Family X Hormuz B1B 1記事全12segmentでinstruction leakage/hallucination 0件・retry率7.7%、ユーザー試聴「自然で問題なし(抑揚・トーンは今後詰める)」。**Production Wiringで必須確認(Gate 3)**: Phase 1(opt-in配線、¥0)+
Phase 2(2026-09-28、実API呼び出しあり、実測費用¥55.90)で16項目中14件
完了。**SDK**: Production `.venv`のgoogle-genaiを2.11.0→2.25.0へ実際に
導入済み(rollback実演込み、requirements-ci.txtも2.25.0へ統一)。
**実e2e実測(Hormuz B1B全12segment、`speech_metadata_flash_lite`)**:
12/12 segment OK、実際のmodel_id`gemini-3.8-flash-lite-tts`をraw_usage_log
で確認、費用¥10.78。`full_story_part1`でAct One/Two/Three digit読みを
実際に再現(TRUE_CONTENT_MISMATCH、既存600秒cool-down機構で自己解決)。
Human Review Lock到達0件、429エラー0件。**JA側`speech_metadata`初実測**
(Meta A2 japanese_title、1segment、PASS、費用¥0.27)。**公平な1回完成
cost比較実測**(同一記事・同一12segment、Flash-Lite¥10.78 vs 現行モデル
¥44.85、現行モデル側のretry率がこの実測ではむしろ高かった)。**Phase 3
(2026-09-28、実測費用約¥30.79)でGate 3残2項目を解消し16項目全16件完了**:
A2主記事13segment全件をFlash-Liteで新規e2e実行(13/13 OK・¥10.49、既存
6% slowdown post-processそのまま適用しslowdown後ASR再検証も全件PASS、
現行モデル音声とのB/A duration比較で総尺約12%短いことを確認)。並列2
プロセス(Hormuz B1B再実行+Meta B1B同時起動)で429エラー0件を実測
(Meta 12/12初回一発OK、Hormuz側`full_story_part1`はAct One/Two/Three
digit読み再現[Trial N=1→Phase2 N=2→Phase3 N=3以上]に対し既存の事前
承認済みLocal Rewrite Recovery機構[全backend共通]が実際に発火し自己
解決、rate limitとは無関係と確認)。あわせてFlash-Lite backendへ既存
英語経路と同じ`http_options.timeout`/`language_code`を明示する小修正
(¥0、unit test追加)を実施。`PRODUCTION_WIRED`はMandatory Opus L2
レビュー後にFableが判定する。配線設計は`docs/pm/design_flash_lite_
family_x_wiring_01.md`(Phase 0)、実測詳細は`TTS-GEMINI-3.8-FLASH-LITE-
PRODUCTION-WIRING-FAMILY-X-01_REPORT.md`Phase 2/3節を参照。**FAMILY-X-02
(2026-09-28、前ID Opus L2所見反映+ユーザー確定仕様、`WIRING IN
PROGRESS`)で以下を確定仕様化**: **B-1(実行方式)**: Flash-Lite経路も
既存Production実行方式contract(`er006_batch_tts_wiring_01.resolve_tts_
execution_mode`/`TTS_EXECUTION_MODE`環境変数、既定BATCH)と同じ分岐点を
通す(`make_speech_metadata_batch_call_fn`新設)。Gemini Batch APIで
speech_metadataが受理されることを1 item実測で確認済み(SUCCEEDED、
pcm 175024 bytes、¥0.06未満)。「Batch未対応」前提のfail-closed設計には
しない。**B-2(6-role style)**: Standard(A2)/Advanced(B1B)**両方**の
基本仕様(前ID「A2はrole別style非対応」は撤回)。Standard固有の速度調整
仕様(既承認`A2_SLOWER_PACE_INSTRUCTION`+6% time-stretch post-process)は
6-role styleと連結し維持する(post-processは無変更)。JA segmentは
既存styleテキストを流用(変更なし)。**C(Flash-Lite統一)**: Family X内で
Key Phrase(shared_narration経由の固定shell+KP English/Japanese
Component)も含めFlash-Liteへ統一(`--tts-backend speech_metadata_flash_
lite`指定時)。Master Audio Store key(`tts_model_id`)が既にモデルを
区別するため、既存Structured Separation資産とは別キーで共存する
(既存entry無変更)。共有モデルを残さざるを得ない箇所は本Phaseでは
発見されなかった(STOP無し)。**D(既存不足の是正)**: (1)fallback
(minimal instruction)発火時、`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`を
実配線(以前は未配線のまま長い legacy instructionを転用していた)。
(2)Production SDK version pin新設(`requirements-production-genai-pin.txt`、
google-genai==2.25.0、Production向けrequirementsファイルは本Phaseで
初めて新設。Production `.venv`全体[100パッケージ]の完全固定は別スコープ
として意図的に対象外)。(3)FULL_STORY経路(news_tail_fix)へ
`semantic_equivalence_info`のtelemetry surfacing追加(attempts_log/
top-level戻り値)。(4)既知baseline件数を実測更新(下記run_project_
regression節参照)。既定backend自体はFAMILY-X-02でも変更しない(切替は
明示指定のまま、既定切替はFable/ユーザー判断待ち)。**修正3回目
(2026-09-28、Opus L2所見反映)**: shell固定segment(welcome/preview_intro/
key_phrases_intro/full_story_intro/num_one〜five)は、Flash-Lite backend
選択時のみ`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`("natural, clear,
conversational")をstyleとして使用する(新規style文言の考案なし、既定
backendは無変更)。fallback(技術的失敗時のminimal instruction)経路も、
`voice01.generate_charon_english`・`point_headings.generate`・
`repro01.generate_english_component_minimal_instruction`の3経路全てで
Flash-Lite backend時は同じ短いstyleを使う(以前の記載「実配線(→3本のうち
1本のみ)」は過大だったため訂正)。共有narration(shell/Key Phrase含む)が
1件でも不合格の場合、`er019_family_x_audio_production_runner_01.py`が
Assemblyへ進む前に停止する(`SharedNarrationBlockedError`/`BLOCKED_
SHARED_NARRATION_NOT_OK`)。Batch経路の費用もbudget guardへ算入される。
バッチ実行の想定所要時間: 実測91〜171秒/item、Family X 1レベル約31 call
(概算50〜90分、両レベル2〜3時間)。正式リリース前のFamily X実行は同期
実行(`TTS_EXECUTION_MODE=STANDARD`)を推奨。既定`tts_backend`
("structured_separation")はFamily A/B/C含め無変更のまま(`--tts-backend
speech_metadata_flash_lite`明示時のみFlash-Lite経路)。検証: Hormuz
run_06 shell 9件×2レベル実API再生成でnum_two含め全件status=OK確認、
Assembly再実行(両レベル)成功。commit`ee280e76`。Fable Gate 3判定:
`PRODUCTION_WIRED`(2026-09-28、スコープ: Family X runnerで`--tts-backend
speech_metadata_flash_lite`明示時の経路[主記事+Key Phrase音声+共有
ナレーション、同期/バッチ実行、Standard/Advanced 6-role+Standard速度
調整]が配線済み。既定`tts_backend`は未変更[structured_separation]、
既定切替は別途ユーザー判断)。詳細
`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_REPORT.md` | TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01(§14-§23)、TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01(Phase 0/1/2/3)、TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02 |
| 短い日本語segmentのASR検証: 発音ベースPhonetic Validation | **目的**: 短く文脈のない日本語Key Phrase/gloss(例:「内在化問題」)は、Azure STTが同音の一般語(例:「内在課問題」)へ書き起こすことがあり、実際には正しく発話されている音声を漢字表記の不一致だけでTTS再生成していた。**期待動作**: `er003_audio_tts_asr_safety.validate_japanese_short_segment_match()`が、EXACT_MATCH/NORMALIZED_MATCH/PHONETIC_MATCH(読みが完全一致、漢字表記は不問)/TRUE_CONTENT_MISMATCH/ASR_UNCERTAINの5分類を返す。EXACT_MATCH・NORMALIZED_MATCH・PHONETIC_MATCHは採用しTTS retryしない。TRUE_CONTENT_MISMATCHはTTS retry候補。ASR_UNCERTAIN(読みが近いが完全一致ではない等、機械的に断定できない)は「TTSが誤っている」と断定せず、既存audioを保持したまま既存fallback/reviewへ委ねる(無条件TTS再生成はしない)。適用対象は`JAPANESE_SHORT_SEGMENT_MAX_CHARS`(30文字)以下の短いsegmentのみ(長文Narrationには適用しない)。**禁止事項**: 数字の実質的な違い・否定の有無・主要語の欠落・明らかに異なる発音・無関係な発話・hallucinationをPHONETIC_MATCHで吸収すること。個別専門用語のwhitelist(1対1のハードコード)を主方式にすること | ER-005-JA-SHORT-ASR-PHONETIC-01 |
| TTS生成の同一segment総試行回数上限 | **3回**(初回を含め最大3回。「初回+3 retry」ではない。4回目以降は絶対にTTS生成しない)。`er011_human_review_lock_01.PRODUCTION_MAX_TTS_ATTEMPTS`をSSOTとし、Production全7関数(`generate_narration_snippet_verified_strict`/`generate_charon_english`/`generate_charon_japanese`/`generate_news_narration_wide_margin`/point_headings `generate`/`generate_english_segment_with_fallback`/`generate_a2_japanese_with_fallback`)の`max_attempts`既定値がこれを参照する。**標準経路+minimal instruction fallback経路の2段構成を持つ3関数(`generate_charon_japanese`/`generate_a2_japanese_with_fallback`/`generate_english_segment_with_fallback`)の内訳は、標準**2回**(`er011_human_review_lock_01.PRODUCTION_STANDARD_TTS_ATTEMPTS`)+fallback**1回**(`PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS`)=合計3回に固定する**(ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25、2026-09-04ユーザー正式決定)。**旧設計の不具合**: 2026-08-28時点の旧設計(ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part B)は「標準経路にmax_attempts回すべてを使わせ、fallbackには残り予算(`max_attempts−標準経路の消費試行数`)のみを渡す」というものだったが、標準経路が早期returnせず最後まで回ると`標準経路の消費試行数==max_attempts`に必ず一致するため、fallback予算が構造的に常に0になり、minimal instruction fallbackが実質的に一度も発火しない不具合があった(日本語側で実Production incident 2件を確認、英語Key Phrase側の同種不具合[下記OPEN-103参照、現在はRESOLVED]と同根)。新設計は、標準経路に渡す`max_attempts`をstandard_attempts(既定2)に固定することで解決する。**FINAL-26改訂(2026-09-04、ユーザー正式決定・上記25の方針を撤回)**: wiring-25では「callerがmax_attemptsに6・10等を明示的に渡す既存呼び出し元(`er006_audio_cost_pilot_02_shared_narration.py::ensure_fixed_japanese_segment`[6]、`generate_charon_japanese_with_reading_safety`/`generate_a2_japanese_with_reading_safety`[既定6]、`er003_v1_iran01_b1_kp_homophone_fix.py`の一回限りscript[10]等)の総予算は縮小しない」としていたが、これは「対象Production経路は例外なくTOTAL3回上限に統一する」というユーザー再確認済み正式仕様と矛盾するため撤回した。対象3関数(`generate_charon_japanese`/`generate_a2_japanese_with_fallback`/`generate_english_segment_with_fallback`)は、関数内部でcallerが渡した`max_attempts`を`min(max_attempts, PRODUCTION_MAX_TTS_ATTEMPTS)`により無条件でクランプする。callerがどの値(6・10等)を渡しても、標準2回+fallback1回=TOTAL3回を超えて発火する余地は構造的に存在しない(上記の呼び出し元すべてを含め例外なし)。**例外(2026-09-01追記、ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22、ユーザー正式決定)**: `generate_key_phrase_component_verified`(英語Key Phrase Component専用)はこのSSOT・今回の2+1分割の対象外とし、合計上限**4回**(`KEY_PHRASE_MINIMAL_MAX_ATTEMPTS`=2+`KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS`=2、`KEY_PHRASE_TOTAL_MAX_ATTEMPTS`)を独立して使う(標準経路+fallback経路の2段構成ではなくPrimary+Fallbackがそれぞれ独立予算のため、今回の不具合の対象外だった)。詳細は「Key Phrase」節「英語Component生成方式(Production正式retry構成)」を参照 | `PRODUCTION_WIRED` | ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15(ユーザー正式決定、3回のSSOT)、ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22(Key Phrase英語Componentのみ4回への例外、ユーザー正式決定)、ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25(標準2+fallback1の内訳固定、ユーザー正式決定)、ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-FINAL-26(caller指定max_attempts[6・10等]によらずTOTAL3回へ無条件クランプ、実TTS/実ASR runtime evidence取得、ユーザー正式決定) |
| 固有名詞ASR不一致の自動PASS条件 | ASR結果同士が収束していることだけでは自動PASSしない(「ASR consensus ≠ pronunciation verification」)。(A) canonical綴り・ASR候補の両方がCMU Pronouncing Dictionaryに存在し、代表(先頭)発音が完全一致する場合のみ自動PASS(`PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`、Perplexity lookup不要・コストゼロ)。(B) CMU辞書に無い外国由来固有名詞は、Pronunciation Ledgerをlookup(cache miss時のみPerplexityで1回research、記事横断でcache再利用)するが、その情報は自動PASSの根拠にはせず、Human Reviewパッケージ(canonical spelling/expected pronunciation/IPA/source/Primary・Secondary ASR結果/実音声)を充実させるためだけに使う。IPA→ARPAbet変換による近似自動PASSは行わない(外国語音韻情報の欠落による誤PASSを避けるため)。**2026-08-28追記**: (B)を「外部発音根拠とTTS実音声の自動照合によるAUTO PASS」へ格上げする案を検討したが、それを安全に行う軽量な既存手段が無いためSTOPし未実装(OPEN-83、DECISION_LOG参照)。(B)は引き続きHuman Review行きのまま。Perplexity研究プロンプトのみ、本人・公式情報源を優先するよう改善した(Human Reviewパッケージの質向上目的、PASS判断には使わない)。**2026-08-28追記2(ER-008-N8-HUMAN-APPROVAL-AND-PROPER-NOUN-PRONUNCIATION-SPEC-16、`APPROVED_FOR_PRODUCTION`)**: 固有名詞の発音判定基準を、「本人・原語としての唯一の厳密発音」ではなく「英語学習コンテンツ(eigo-radio)として許容できる英語圏での発音」へユーザー承認のもと変更した。新しい判定優先順位: (1)本人自身の英語での発音 → (2)公式プロフィール・所属組織・公式イベント等で確認できる英語発音 → (3)信頼できる情報源で確認できる一般的な英語圏発音 → (4)複数の英語圏発音が実際に認められる場合は、単一の正解ではなく許容発音集合として保持する。TTS音声がこの許容発音集合のいずれかに十分一致すればPASSとして扱ってよい(原語の唯一の厳密発音との一致は必須条件にしない)。実例: No.8 B1 `point_two`の人名`Kristie Tse`は、Pronunciation Ledger調査で`/ˈkrɪsti tsiː/`(tsee系)・tsay系・see系の複数候補が挙がっており、ユーザーが実音声を試聴し「seeに近い」英語圏の許容発音候補に含まれると判断してHuman Approvedとした(広東語としての最厳密発音との一致を理由にしたのではない)。**現時点はコード実装ではなくHuman Reviewでの判断基準の変更のみ**(record_human_approval()による個別承認)。Cascadeの自動判定ロジックへこの基準を組み込む実装は行っておらず、将来の自動照合(OPEN-83)でこの基準を採用する方針だけを記録している。**2026-08-29追記(ER-23、固有名詞Human Review表示ルールを新設)**: No.8 B1 "Stephen Reicher"の発音再検証で、Pronunciation Ledgerのconfidence="high"の唯一の根拠が英国covid公聴会の**テキスト書き起こし**(音声ではない)だったことが判明し、テキスト書き起こしは本人が名前を訂正して名乗った事実は伝えても発音の音そのものは伝えないため、根拠として不十分と判断した(confidenceを"medium"へ手動訂正)。恒久対策として次の2点を実装した: (1) `er006_pronunciation_research_01.py`のPerplexity調査プロンプトへ「confidence="high"は本人の音声ソース(インタビュー音声・動画等)が確認できた場合のみ、テキスト書き起こしのみ・二次情報源のみの場合はmedium以下」という基準を追加。(2) `er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail()`で、Pronunciation Ledger lookup/researchが失敗(None)した場合にそのspanをHuman Reviewパッケージから黙って省略していた既存の欠落(silent drop)を修正し、失敗時も`confidence="unconfirmed"`の明示的なentryを必ず残すようにした。**固有名詞についてユーザーへHuman Reviewを依頼する場合、試聴画面・報告には必ず(a)表記、(b)IPA(信頼できる場合)、(c)IPAが確定不能ならその旨、(d)英語話者向けpronunciation guide、(e)発音根拠source、(f)confidenceを表示する**、という運用ルールを正式化した(ユーザーに「正しい発音の基準」が無いまま試聴判断を求めない)。単体テスト1件(`er006_secondary_asr_01_test.py::test_case_b_unresolved_entity_research_failure_still_reports_unconfirmed`)で確認済み | `PRODUCTION_WIRED`(表示ルール・confidence基準) | ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15、ER-008-N8-HUMAN-APPROVAL-AND-PROPER-NOUN-PRONUNCIATION-SPEC-16、ER-008-N8-FINAL-PRODUCTION-HARDENING-23 |
| 日本語表記ゆれ(漢字/かな)のCascade内自動PASS条件 | `ORTHOGRAPHIC_VARIANT_CONFIRMED`: 「ASRが同じ表記を何回書いたか」ではなく、「ASR側の漢字spanが辞書上持ちうる正当な読み候補の中に、canonical側の期待読みが含まれるか」を各ステップ個別に確認し、かつ異なる2エンジン(OpenAI/Azure)以上がその状態に到達した場合のみPASSする。既知の限界: 「頃」のように単漢字として複数の読み(ころ/ごろ等)が辞書上正当とされる文字は、テキストのみからは実際に発話された読みを完全には確定できない(音声を伴わない原理的な限界、OPEN_ITEMS.md参照) | ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 |
| 英語homophone(同音異義語)のCascade内自動PASS条件 | `HOMOPHONE_EQUIVALENT`: canonical/ASRの単一語置換差について、CMU Pronouncing DictionaryのARPAbet音素列が完全一致する場合のみcascade対象とする(即blind TTS retryしない)。Secondary(または2回目のASR)側の結果が、(a)canonical文字一致、または(b)同じくARPAbet完全一致のいずれかを満たした場合のみPASSする(「他に問題が見つからなかった」という消極的な理由ではPASSしない)。辞書に無い語向けの小さな閉じた補完テーブルを併設(2026-08-28時点で空、必要時に追記) | ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 |

### 可変segment Role Style(J3/E2)— Status: `PRODUCTION_WIRED`(2026-09-29、Fable Gate 3=Meta run_03。`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§E2E Meta run_03、runtime evidence: japanese_title/preview/comment/full_story/in_one_lineのstyle_prefixがJ3文言「落ち着いた、自然な話し言葉で…」、full_story/in_one_lineが英語版E2文言で実測一致)

ユーザーが2026-09-28に、`TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02`の可変segment
Role Style比較結果から、日本語=**J3**・英語=**E2**を`APPROVED_FOR_PRODUCTION`と
正式決定し、**同日中に`TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`(Phase B)
で正式経路へ配線した**(Status: `APPROVED_FOR_PRODUCTION`(配線完了・Opus L2
レビュー+Fable Gate 3判定待ち)。`PRODUCTION_WIRED`はGate 3判定後)。
**適用範囲(配線後の確定値)**: JA=Family X **Standard(A2)**のpreview/
comment_1〜4、および**japanese_title**(W3、Opus L2所見MAJOR-1是正で
同一A2記事内のstyle混在を解消するため追加)。**2026-09-29追記(W5、
`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`)**: Standard Key Phraseの
**日本語意味(`japanese_meaning`)**にもJ3を適用することをユーザーが
`APPROVED_FOR_PRODUCTION`と正式決定した(下記「Key Phrase 音声構造」節
参照、`_role_style_ja()`と同一関数・同一backendゲート経由で配線済み)。
固定Master phraseは引き続き対象外。
EN=`FAMILY_X_ROLE_STYLE_EN`のTOPIC_INTRO/FULL_STORY/IN_ONE_LINEの3roleを
E0からE2へ値更新(Role定数はlevel非依存のためStandard/Advanced両方のEN
segmentへ適用される。PREVIEW/COMMENT/HEADING_READOUTはE2未検証のため不変
[E0のまま])。固定Master phrase(welcome/preview_intro/key_phrases_intro/
full_story_intro/num_one〜five/point_explanation)には適用しない(下記
「固定フレーズ Champion」節を参照、別トラック)。**backendゲート**: JA(J3)は
EN 6-roleと同一条件=`--tts-backend speech_metadata_flash_lite`明示時のみ有効。
既定backend(`structured_separation`)ではJA/ENとも従来挙動のまま無変更
(Family A/B/Cは無影響)。**方式**: J3は長文`JAPANESE_STYLE_PREFIX`を**置換**
する(Trial-02[er044]と同一方式、併記ではない)。**J3(日本語、逐語)**:
「落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに
抑揚をつけてください。演技がかった話し方は避けてください。」。**E2(英語、
逐語)**: FULL_STORY="calm, steady news narration with natural emphasis at
key points and turns; not dramatic."/IN_ONE_LINE="concise, clear, landing
naturally as a settled conclusion; not flat, not dramatic."/TOPIC_INTRO=
"brief, clear, engaging news topic introduction with natural emphasis on the
topic; not dramatic."。**実装箇所**: `er003_b1_p9a_audio.py`
`generate_narration_snippet()`のja分岐をen分岐と対称化
(`style_prefix_override or JAPANESE_STYLE_PREFIX`、既定None=従来挙動)、
`er003_v1_n3_01_tts_generate.py`の`generate_a2_japanese_with_reading_safety`/
`with_fallback`へ`style_prefix_override`引数追加(fallback[minimal
instruction]経路は不変)、`er033_tts_flash_lite_family_x_styles_01.py`へ
`FAMILY_X_ROLE_STYLE_JA`定数追加+`FAMILY_X_ROLE_STYLE_EN`のE2値更新、
`er019_family_x_audio_production_runner_01.py`の`generate_family_x_a2_
segments()`へ`_role_style_ja()`(EN`_role_style()`と対称なbackendゲート)を
新設しpreview/comment_1〜4のみへ配線。**runtime evidence**: `p9a.generate_
narration_snippet()`の戻り値dictへ`style_prefix`(実文字列)を追加、既存audit
(`tts_generation_results.json`)へ記録される。**Regression**: Hormuz(既存
Flash-Lite run読み込み、記事text再生成なし)でStandard JA 5segment
(preview/comment_1〜4)・Advanced EN 6segment(topic_intro/full_story_part1〜
2[+heading2件]/in_one_line)・Standard EN 2segment(full_story_part1/
in_one_line、slower指示との重畳実測)を専用out-dirへ部分実行で確認生成。
証拠: `er019_output/family_x_audio_production_wiring_01/variable_role_style_
wiring_regression_01/hormuz/audit/confirmation_regen_results.json`。
Production Master Audio Store(`er006_output/master_audio_store_01/
manifest.json`)は本配線・確認生成の前後でsha256不変(可変segmentはStore
対象外、設計書§2(d))。 |
出典: `TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_REPORT.md`§4、
`docs/pm/design_tts_variable_spoken_role_style_trial_02.md`§4-4、
`docs/pm/design_tts_variable_role_style_production_wiring_01.md`、
`TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_REPORT.md`、
`PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01`(DECISION_LOG.md) |
2026-09-28 |

### 固定フレーズ Champion — Status: `PRODUCTION_WIRED`(2026-09-29、Fable Gate 3=Meta run_03。`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§E2E Meta run_03、runtime evidence: a2 `shared_narration`10件全て`reused=true`、`master_audio_id`が下記対応表と完全一致[welcome `aa130472d437ac80b7cdd474`含む]、TTS call 0)

ユーザーが2026-09-28に、`TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02`の試聴
結果から固定phrase(全記事共通・文言固定のTTS要素)8件のChampionを正式決定
し、2026-09-29にnum_three/num_fiveの残り2件(`TTS-FIXED-SHELL-NUMBER-
THREE-FIVE-RETRIAL-01`、er047、take選定)も正式決定した。これにより10
phrase全件のChampionが確定した(**未確定は残っていない**)。試聴ページ
(`user_test/fixed_shell_champion_trial_02/index.html`)の表ヘッダ列順(左=
Baseline/Candidate A[現行Production Master]、中=Candidate B、右=
Candidate C)から列位置を確定した対応表:

| phrase | candidate | style全文 | model/voice |
|---|---|---|---|
| welcome | A(現行Master継続) | "既存Production v2_flash_lite_short_style(FALLBACK[0])" | gemini-3.8-flash-lite-tts/Charon |
| preview_intro | C | "natural, clear, conversational" | gemini-3.8-flash-lite-tts/Charon |
| key_phrases_intro | C | "natural, clear, conversational" | gemini-3.8-flash-lite-tts/Charon |
| full_story_intro | C | "natural, clear, conversational, unhurried pace, with a brief pause before continuing" | gemini-3.8-flash-lite-tts/Charon |
| num_one | C | "measured, matter-of-fact delivery, consistent energy and tempo for every word, plain falling pitch at the end, spoken as a flat statement, not a question" | gemini-3.8-flash-lite-tts/Charon |
| num_two | B | "calm, steady, declarative tone, even volume and pace across the set, ending each word with a clear falling pitch, stated plainly, never rising like a question" | gemini-3.8-flash-lite-tts/Charon |
| num_three | B take1(2026-09-29確定) | num_twoと同一Style系統B("calm, steady, declarative tone, even volume and pace across the set, ending each word with a clear falling pitch, stated plainly, never rising like a question"、文言のみ"Three.") | gemini-3.8-flash-lite-tts/Charon |
| num_four | C | "measured, matter-of-fact delivery, consistent energy and tempo for every word, plain falling pitch at the end, spoken as a flat statement, not a question" | gemini-3.8-flash-lite-tts/Charon |
| num_five | B take1(2026-09-29確定) | num_twoと同一Style系統B(同上、文言のみ"Five.") | gemini-3.8-flash-lite-tts/Charon |
| point_explanation(JA) | B | "自然な抑揚をつけて、はっきりと落ち着いた調子で話す" | gemini-3.8-flash-lite-tts/Charon |

**2026-09-29追記**: num_three/num_fiveは、採用済みOne(C)/Two(B)/Four(C)と
同model(Flash-Lite)・同voice(Charon)・同Style系統(B/C既存定数)でのB系統
4take・C系統4take再Trial(16take中OK7)の結果から、ユーザーがそれぞれ
B take1を正式選定した(詳細take一覧・不合格9takeの記録は
`TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01_REPORT.md`、
`er047_output/tts_fixed_shell_number_three_five_retrial_01/
retrial_results.json`参照)。**登録状況**: welcome除く9 phrase(preview_
intro/key_phrases_intro/full_story_intro/num_one/num_two/num_three/
num_four/num_five/point_explanation)は`FAMILY-X-REFRESH-E2E-PRODUCTION-
WIRING-01`(W2、commit`2ecb0c64`)でProduction Master Audio Storeへ
`v3_champion_2026_09_29`として正式登録済み(TTS 0回・reuse確認済み)。
welcomeはA(現行Master継続)のため登録不要。**現行Productionの実際の
生成呼び出しは未配線のまま**(Master登録済みだが呼び出し元の実配線・E2E
Gate通過は別管理ID`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`のW4以降)。
詳細対応表・style全文は`user_test/fixed_shell_champion_trial_02/index.html`、
`er043_output/tts_fixed_shell_master_champion_trial_02/
champion_trial_results.json`を参照。 |
出典: `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_REPORT.md`、
`TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01_REPORT.md`、
`PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01`・
`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`(DECISION_LOG.md、2026-09-29
エントリ) |
2026-09-29 |

## Key Phrase

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 選定方式 | Strategy L (Listening Blocker Ranking) | `DECIDED` | ER-003-P2I(commit `e33f227`) | 2026-07-xx |
| 件数 | 5件/記事 | `DECIDED` | ER-003-P2I | 2026-07-xx |
| 語数範囲 | 1〜5語(`key_phrase`) | `DECIDED` | ER-003-KP-02-R1(commit `5a94db0`) | 2026-08-08 |
| 選定元 | `HISTORICAL`表記に注意: 「各記事自身のCEFR-B1本文」は、A2が存在する前の単一レベル(B1のみ)時代の記述。**現行はレベルごとに、そのレベル自身の最終確定本文から独立選定する**(A2はA2最終本文から、B1はB1最終本文から。CEFR-A2構造・音声仕様節「Key Phrase選定(A2)」、B1 Key Phrase節を参照)。他レベルのKey Phraseを機械的に流用しない、という原則自体はP-series/現行とも共通 | `DECIDED` | ER-003-REPRO-01-KP(commit `46aa2e8`、当時はB1のみ)。現行の per-level選定はER-003-CROSSLEVEL-AUDIO-02(A2)・ER-003-B1-NOVEL-AUDIO-01系(B1) | 2026-08-08(per-level化: 2026-08-10前後) |
| 後処理 | Pedagogical Phrase Canonicalization(`source_span`→`display_phrase`→`key_phrase`→`used_form`) | `DECIDED` | ER-003-KP-01(commit `e607d26`) | 2026-08-08 |
| Canonicalization原則 | 「最小」ではなく「最小十分」 | `DECIDED` | ER-003-KP-02(commit `8856264`) | 2026-08-08 |
| QAモデル | 3状態(`CANONICALIZATION_PASS`/`REVIEW_REQUIRED`/`INVALID`)、11 QAフィールド | `DECIDED` | ER-003-KP-01→KP-02→KP-02-R1 | 2026-08-08 |
| Traceability定義 | 「source_spanから説明可能な正規化で導出できる」こと。文字通りの部分文字列一致は不要 | `DECIDED` | ER-003-KP-02-R1 | 2026-08-08 |
| human review条件 | いずれかのQAフィールドがFAILならREVIEW_REQUIRED、自動retryなし、人間承認で採用可 | `DECIDED` | ER-003-KP-01→KP-02 | 2026-08-08 |
| `used_form`/`key_phrase`の関係 | 現状100%重複(技術的負債として記録、整理はしない) | `DECIDED`(整理しない方針が決定事項) | ユーザー指示(2026-08-08、KP-02-R1承認時) | 2026-08-08 |
| 英語Component生成方式(Production正式retry構成) | Trial-19→Mini-Trial-20-R2→Trial-21の実データを経てユーザーが正式採用。**Primary**: Minimal instruction(`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`、"Speak the following short phrase aloud naturally and clearly..."、final consonant保持・phrase一体感・1回のみ発話等の既存pronunciation safeguardを含む)で最大2回(`KEY_PHRASE_MINIMAL_MAX_ATTEMPTS`)。**Fallback**: Primary 2回ともNGの場合のみ、Minimal instruction全文の末尾へ"Pronounce the phrase specifically as an English word or phrase, using English pronunciation throughout — not as a Japanese, Chinese, or other non-English reading of it."を追加した`KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`(既存文言は置換しない、AND条件で追加)で最大2回(`KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS`)。**合計最大4回**(`KEY_PHRASE_TOTAL_MAX_ATTEMPTS`、上記「TTS生成の同一segment総試行回数上限」の一般則[3回]に対するKey Phrase専用の明示的な例外)。いずれかの段でPASSした時点で即終了し、後続attemptは実行しない。旧来の標準経路(`ENGLISH_STYLE_PREFIX`起点)は、この関数からは完全に離脱した(他segmentでは`ENGLISH_STYLE_PREFIX`/旧`MINIMAL_INSTRUCTION_PREFIX`自体は無変更のまま使用継続)。実装は`er003_v1_repro01_main_generate.py::generate_key_phrase_component_verified()`(`@review_lock.guarded_generate("en")`のまま、内部で`generate_narration_snippet_verified_strict`をstyle_prefix_overrideだけ差し替えて2段呼び出す設計、OPEN-105のreentrancy guardにより二重会計は発生しない) | `DECIDED`(`PRODUCTION_WIRED`) | ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19→MINI-TRIAL-20-R2→ENGLISH-LOCK-FALLBACK-TRIAL-21(検証)→ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22(ユーザー正式採用・Production配線) | 2026-09-01 |
| `default`(No.9 A2 kp2_en)個別例外 | 上記の一般Production retry構成の対象から除外する(ユーザー正式決定)。Minimal単体・Minimal+English Lock併用のいずれも計8attempt中8回とも発話言語が英語からずれる失敗(日本語カタカナ「デフォルト」/中国語「默认」/誤スペル"defaut")を実証済みで、一般仕様をこの1語のためにこれ以上複雑化しない。No.9では個別のfixed asset候補として扱う(OPEN-103参照、Claude Codeが単独で正式採用はしない) | `DEFERRED / NON-BLOCKING`(2026-09-01、ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22) | ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21(REJECTED判定)→ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22(個別例外化・ユーザー正式決定) | 2026-09-01 |
| Function-word/article reduction(Key Phrase英語pronunciation) | No.9 A2「a catch」で冠詞"a"が独立した強勢語のように強く・長く発音される問題(Trial 26で診断・改善確認)を受け、ユーザーが正式採用。**short English function words such as articles should normally be reduced in natural connected speech: brief, light, unstressed, and smoothly connected to the following content word. They must not be omitted or made inaudible.**(`FUNCTION_WORD_REDUCTION_SUFFIX`、Trial 26で検証した文言を一字一句そのまま複製)を、`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`(= `KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT` + 本suffix)の末尾へAND方式で追加した(既存文言は一切削除・変更しない)。`KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`はこの`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`を起点に構築されるため、**Primary(Minimal)・Fallback(English Lock)の両方へ自動的に適用される**(定義を分岐させていないため、Fallback側でだけ原則が欠落するDangling Referenceは構造的に発生しない)。「a catch」固有のhardcodeではなく、article/短いfunction word全般への一般原則(冠詞を省略・無音化することは禁止、既存のfinal consonant保持・phrase一体感・自然さ・1回のみ発話・over-emphasis禁止の各safeguardは全て維持)。実Production path(`generate_key_phrase_component_verified()`、Trial専用scriptではない)から「a catch」を実際に生成し、No.9 A2の`kp4_en.wav`を差し替えてA2 episodeを再Assemblyした。article/function-word fixture(a chance/an idea/the answer)・非function-word系の既存Key Phrase(guilt tipping/push back/starting point)でも実Production pathでregression確認済み(詳細はDECISION_LOG.md該当項目参照) | `DECIDED`(`PRODUCTION_WIRED`) | ER-010-NO9-A2-KEYPHRASE-ARTICLE-REDUCTION-DIAGNOSTIC-AND-TRIAL-26(検証・ユーザー承認)→ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1(ユーザー正式採用・Production配線・No.9 A2反映) | 2026-09-02 |
| 人称代名詞・所有格の一般化(Canonicalization) | No.18 B1で「catch their attention」「a piece of your attention」のように、本文中の特定の人物に依存した人称表現(your/their/his/her/its/our/you/they/he/she等)がKey Phraseとしてそのまま採用され、単独の学習教材として再利用しにくい問題が発見された。原因は、既存のcanonicalization「文脈限定語の除去」ルールが除去(削除)のみを対象とし、辞書的な一般形への**置換**を一度も指示していなかったこと。ユーザーが正式決定し、`er003_key_words_canonicalization.py`へ新しい変換カテゴリ`generalize_person_dependent_reference`を追加した: 閉じた語彙集合(my/your/his/her/its/their/our/you/they/he/she/yourself等 → one's/someone's/somebody's/someone/somebody/one/oneself)による1対1のトークン置換のみを許可する構造的validator(`_is_valid_person_generalization`、既存のsource_span連続部分文字列というRule7とは別の、明示的に許可された例外パス)。新QAフィールド`qa_person_reference_generalized`を追加。**ただし特定の代名詞を含むこと自体が意味・用法として必要な場合は機械的に変換しない**(canonicalizationプロンプトに明記、機械的hard ruleにはしない)。記事固有のハードコードではなく、閉じた語彙集合による一般規則(単体テスト6件で「their」→「someone's」等の正しい置換を許可し、集合外の置換・語数不一致・無関係語の変更・不正なreasonタグを全て拒否することを確認済み) | `DECIDED`(`PRODUCTION_WIRED`) | ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01(発見・ユーザー正式決定・実装、No.18 specfix_v2 A2/B1実データでcanonicalization pipeline自体の正常動作を確認。この回では人称代名詞を含む候補が選ばれなかったため実際の置換発火は未観測、単体テストで安全性を確認済み)。**2026-09-27追記(`KEYPHRASE-PERSON-DEPENDENT-REFERENCE-GENERALIZATION-WIRING-FIX-01`)**: Family Z Melos runで初発火。LLM自己申告QA`qa_traceable_contiguous_span`のPASS条件に人称一般化が未反映だったQA定義側ギャップを、決定論的後処理+prompt template追記で整合(新仕様ではない、既存資産照合=分類A)。既存145件再判定で14件FAIL→PASS(全て正当な一般化)、Family X 4件無変化=無回帰) | 2026-09-02(初発火整合: 2026-09-27) |
| Key Phrase Set Redundancy QA(5件相互の意味重複) | No.18 B1で「catch their attention」(注意を引く)と「a piece of your attention」(注意の一部を奪う)という、字面は異なるが意味・学習目的が実質同一の候補が両方選ばれた。既存QAは各候補をsource_span/display_phraseとの関係でのみ個別に検証し、5件相互の重複は一度も評価していなかった(選定プロンプトの「汎用性」基準は候補同士を比較しない)。ユーザーが正式決定し、新規モジュール`er011_key_phrase_set_redundancy_qa_01.py`を追加した: canonicalization完了後の5件について、意味(meaning)・使用場面(usage_context)・文法/構文上の学習価値(grammatical_teaching_value)・記事内で担う概念(conceptual_role)の4観点でC(5,2)=10ペア全てをLLMが判定する専用QA工程。1つでも`is_near_duplicate=true`のペアがあれば`REDUNDANCY_NG`とし、`er003_v1_n3_01_scaffold_generate.py::run_key_phrases()`がKey Phrase選定(方式L)からやり直す(最大`KEY_PHRASE_REDUNDANCY_RETRY_MAX`=2回、既存の`POINT_OVERLAP_ARTICLE_RETRY_MAX`と同じ値をそのまま踏襲、新しい上限を独自に発明しない)。retry時は前回の重複判定結果を選定promptへ診断メモとして追加する(記事本文は変更しない、選定+canonicalization+redundancy QAの3工程のみ再実行)。上限まで再試行してもNGが残る場合は、既存のKey Phrase QA運用(REVIEW_REQUIRED=自動不採用・人間確認後に採用可)にならい、本文は変更せず`NG_REVIEW_REQUIRED`として報告する。No.18 specfix_v2実データ(A2/B1双方)で実際に稼働し、全10ペアともPASS(`REDUNDANCY_PASS`)を確認 | `DECIDED`(`PRODUCTION_WIRED`) | ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01(発見・ユーザー正式決定・実装・No.18 specfix_v2実データで稼働確認) | 2026-09-02 |
| 日本語グロス(`ja_gloss`)のPrompt規約A/B | 2026-09-06、ユーザーが2026-09-06に承認した3判断のうち判断4(規約A・規約Bを採用、**規約Cは不採用**)を`PRODUCTION_WIRED`。**アーキテクチャ上の発見**: `japanese_gloss`はcanonicalization工程(`er003_key_words_canonicalization.py`)では一切生成・変更されない(常に選定工程からのpass-through)。実際の生成元は選定Prompt`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`(`er003_b1_p2_keywords.py`経由でB1・A2[`er003_v1_iran01_a2_generate.py`が同一関数を再利用]の両方が共有する)。B2レベルは別ファイル`b2_key_words_production_l_prompt_template.txt`を使うため今回は対象外(指示範囲外、変更していない)。ER-011-...-02で先にcanonicalization prompt(`b1_p2_keywords_canonicalization_prompt_template.txt`)へ規約B(key_phraseの「～」「〜」「…」プレースホルダー禁止)のみ配線したが、gloss自体には効果が無いことをRuntime evidenceで実証した。ER-011-...-03で選定Prompt本体(`b1_p2_keywords_l_prompt_template.txt`)へ、**規約A**(日本語グロスの数字は算用数字ではなく漢数字で書く)と**規約B**(日本語グロスに「～」「〜」「…」を使わず、目的語省略の言い切り形[例: 「示す、指し示す」]へ書き換える)を最小限の2文で追加した(既存の選定基準・3条件は無変更)。**規約C(短い機能語終端のKey Phrase回避、Trial-17 Track Cで検証)は不採用**、選定Promptへ追加していない。実プロダクション経路(選定→canonicalization)をTrial-13 B1記事に対し2回実行し、規約B(placeholder除去)は実際のLLM出力で確認済み(Trial-13原本「～を示す、～を指し示す」→本タスク実行で「示す、示唆する」)。規約A(漢数字化)は、この2回の実行では数字を含むgloss候補が偶然選ばれなかったため直接観測できなかったが、同一文言をTrial-17 Track Cで実証済み(「中央値は約2泊」→「中央値は約二泊」)。**Prompt文言による指示であり決定的Validatorではないため、遵守は確率的である**(決定的gloss品質チェック`_JA_GLOSS_PARENTHETICAL_RE`はプレースホルダー文字・数字表記までは検証しない)。Validator PASS率・canonicalization QA PASS率のいずれも規約追加前後で劣化は確認されなかった。**2026-09-06追記(KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01)**: 上記規約Bのうち**gloss側の「～」「〜」禁止はユーザーが2026-09-06に正式撤回した**(`WITHDRAWN`、詳細は次行「日本語gloss表示用/TTS用分離」参照)。「…」等その他placeholder記号の禁止、規約A(漢数字)、canonicalization prompt側のkey_phrase(英語)に対する「～」「〜」「…」禁止(この行の直前の記述どおり)はいずれも無変更のまま維持する | `DECIDED`(`PRODUCTION_WIRED`、規約Cは`REJECTED`、規約Bのgloss側「～」「〜」禁止は`WITHDRAWN`) | ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02(発見・規約B[key_phraseスコープ]配線)→03(規約A/B[gloss側]を選定Promptへ配線・Runtime evidence)→KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01(gloss側「～」「〜」禁止の撤回) | 2026-09-06 |
| Key Phrase日本語gloss 表示用/TTS用分離 | ユーザーが2026-09-06に`APPROVED_FOR_PRODUCTION`と正式決定した仕様を`PRODUCTION_WIRED`まで配線(根拠: Phase 1 `OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-01_REPORT.md`、Phase 2 `OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02_REPORT.md`、`OPEN-117-KEYPHRASE-TILDE-GATE-RECHECK-01_REPORT.md`)。**表示用**(`japanese_gloss`、既存フィールド、選定Promptがそのまま生成)は辞書的な「～」「〜」表記を許容する(上記行のとおり規約Bのgloss側「～」「〜」禁止は撤回、「…」等その他placeholder記号の禁止・key_phrase側の規約は維持)。**TTS用**(新フィールド`japanese_gloss_tts`、`keywords_canonicalized.json`のitemへ追加)は、`er003_key_words_canonicalization.py::convert_display_gloss_to_tts_text()`が`merge_canonicalization_result()`内で`japanese_gloss`から決定論的な規則変換のみで導出する(LLM不使用、正規表現`(?:^|(?<=、))[～〜]`を「なになに」へ置換)。**変換対象**は文頭または読点「、」直後の「～」「〜」のみ(例: 「～を示す」→「なになにを示す」)。**変換対象外**(数値placeholder型「ソロ旅行を～％とする」、範囲表記「中～高強度」等の文中位置、および「…」)は無変換のまま既存の`er003_audio_tts_asr_safety.detect_gloss_placeholder_notation`ゲートへそのまま渡し、従来どおりTTS呼び出し前にブロックさせる(ゲート自体は無変更、弱めていない)。TTS呼び出し側(`er003_v1_n3_01_tts_generate.py::generate_b1_segments()`/`generate_a2_segments()`)は、`resolve_key_phrase_ja_gloss_tts(item)`経由で`japanese_gloss_tts`を`generate_charon_japanese_with_reading_safety()`/`generate_a2_japanese_with_reading_safety()`へ渡す(表示用`japanese_gloss`はTTSへ一切渡らない)。**後方互換**: `japanese_gloss_tts`フィールドが存在しない旧artifact(本仕様配線前に生成された`keywords_canonicalized.json`)に対しては、`resolve_key_phrase_ja_gloss_tts()`が表示用`japanese_gloss`から同じ規則でその場導出するfallbackを持つ(`japanese_gloss_tts_fallback_derived`として記録)。**Master Audio Store**: 英語Key Phrase Component(`ensure_key_phrase_english_component`)は`canonical_text=used_form`(英語)のみをキーに使い、日本語gloss分離の影響を受けない。日本語Key Phrase glossはStore非対象(`generate_charon_japanese_with_reading_safety`等はStore経由ではなく都度生成、review_lockのみでguard)のため、cache identity設計との矛盾なし(コード再確認済み)。**retry/fallback/regeneration**: 選定retry(Redundancy QA、最大2回)・TTS標準/fallback retry・review_lock・Assembly側Audio Validation Gateのいずれも`japanese_gloss_tts`を一貫して使う経路であり、既存の安全装置を独自に緩和していない。**表示側**(player html等)は表示用`japanese_gloss`を使い続ける(TTS用フィールドを表示に使う既存Production表示コンポーネントは無い、コード確認済み)。**Runtime evidence**(2026-09-06、Standard同期、`er011_output/kp_display_tts_separation_prod_wiring_01/`): Theme 2 B1(Trial-12 article.md)でProduction正式経路(選定→canonicalization→redundancy QA、いずれもPASS)を1回実行、選定5件は「～」「〜」を含むglossが無かったため(natural_conversion_fired=false)、既知gloss「～と完全には一致しない」で同じProduction関数経路を直接駆動し「なになにと完全には一致しない」への変換発火とTTS(attempt2でPHONETIC_MATCH、verified=true)を実証。数値placeholder型「ソロ旅行を～％とする」は無変換のままgateでSTOPPED(TTS API呼び出し0件、wavファイル生成なし)を実証。model_id=`gemini-3.1-flash-tts-preview`、`tts_execution_mode=STANDARD`をraw_usage_log.jsonlで確認。`keywords_canonicalized.json`の全itemに`japanese_gloss`/`japanese_gloss_tts`の両方が保存されていることを確認 | `DECIDED`(`PRODUCTION_WIRED`) | KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01(ユーザー`APPROVED_FOR_PRODUCTION`→本タスクで`PRODUCTION_WIRED`まで配線) | 2026-09-06 |
| Key Phrase 数値placeholder型の回避(選定Prompt) | ユーザーが2026-09-06に`APPROVED_FOR_PRODUCTION`と正式決定。「～％」のように数値を補わないと意味が成立しない句・日本語グロス(例: 「ソロ旅行を～％とする」)は、TTS側で変換して救済しない(数値placeholder型は「なになに」変換規則の対象外のまま、既存gateでブロックし続ける)。代わりに、選定側でそのような不完全表現を選ばないよう誘導する。選定Prompt`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`(A2/B1共有)へ「数値を補わないと意味が成立しない句・日本語グロス(数値の穴埋めを必要とする不完全な表現)は選ばない、それ単体で意味が成立する句・グロスを選ぶ」旨の1文を追加した(canonicalizationは`japanese_gloss`を生成しないため、canonicalization promptへの追加変更は不要と判断)。retry(選定からやり直すKey Phrase Set Redundancy QA retry)でも同じ選定Promptが使われるため整合する。Prompt文言による誘導であり決定的Validatorではないため遵守は確率的、最終的な安全性は既存gate(`detect_gloss_placeholder_notation`)が担保する | `DECIDED`(`PRODUCTION_WIRED`) | KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01 | 2026-09-06 |
| Key Phrase日本語glossの自然さ基準(選定Prompt) | 診断(`KEYPHRASE-JA-GLOSS-NATURALNESS-DIAGNOSTIC-01_REPORT.md`)で、選定Prompt`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`(A2/B1共有)には「短く自然な日本語グロス」という一語以外に、学習者向け平易さ・直訳調回避・硬い報道語/漢語回避の具体基準が無く、Validator(`er003_key_words_min_unit.py::validate_min_unit_selection`)・Key Phrase Set Redundancy QA・Human Reviewのいずれも訳語の自然さを判定しない構造的空白(原因分類A+C+Dの複合)が確認された。**前提訂正**: タスク依頼の前提「new normal→新常態」は実データ検証の結果誤りと判明(実際のgloss確定値は一貫して「新しい当たり前」、「新常態」は無関係な既存の英語Key Phrase TTS言語ロック不具合のASR書き起こしのみ)。ユーザーが2026-09-06に選択肢a(Prompt1〜2文追加+Human Review基準1文追加。LLM追加QA・Validator新設・blacklist・過去397件の再生成は行わない)を`APPROVED_FOR_PRODUCTION`と正式決定し、選定Promptの既存の「短く自然な日本語グロス」文の直後へ新パラグラフとして「日本語グロスは、辞書的に正しいだけでなく、日本人の英語学習者が聞いてすぐ意味を理解できる、自然で平易な現代日本語にしてください。直訳調や、「常態」「是正」のような過度に硬い報道語・漢語、一般的な学習者には伝わりにくい表現は避けてください。」の2文を追加した(既存の規約A[漢数字化]・規約B[「…」等placeholder禁止・「～」「〜」は許容]・数値placeholder回避文はいずれも無変更のまま維持、個別語の列挙は例示2語のみでblacklist化していない)。retry(選定からやり直すKey Phrase Set Redundancy QA retry、最大2回)でも同じ選定Promptが使われるため整合する。Prompt文言による指示であり決定的Validatorではないため、遵守は確率的である。単体テスト2件追加(`er003_test_b1_p2.py::test_template_contains_gloss_naturalness_guidance`)、既存の規約A/B文言の維持も同テストで再確認。**Runtime evidence**(2026-09-06、`er011_output/kp_ja_gloss_naturalness_prod_wiring_01/`): Theme 2 B1・A2(Trial-12記事)それぞれでProduction正式経路(選定→canonicalization→Key Phrase Set Redundancy QA、いずれもPASS)を1回実行し、選定5件×2レベルの英語Key Phrase・表示用/TTS用glossを取得。直前配線(KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01)の出力と比較した結果、悪化事例は確認されなかった(B1「self-directed travel」のglossが旧Prompt出力「自分主導の旅行」[硬めの漢語「主導」]から新Prompt出力「自分で決める旅行」[平易な言い切り]へ変化する等、方向性としては硬さを避ける傾向を確認したが、選定される候補自体がAttempt毎に異なるためN=1の限定的な観察であり、確率的遵守である旨を明記する)。学習価値(3条件)の劣化は確認されなかった | `DECIDED`(`PRODUCTION_WIRED`) | KEYPHRASE-JA-GLOSS-NATURALNESS-DIAGNOSTIC-01(診断)→KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01(ユーザー正式採用・Production配線) | 2026-09-06 |
| Key Phrase日本語glossの括弧内別訳・専門用語・補足の併記禁止(選定Prompt) | `OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01`で、Theme 2 A2/B1が独立に"median"を選び、日本語glossへ括弧書き補足(B1「データの真ん中の値（中央値）」、A2「真ん中の値（中央値）」)を含めたため、既存の構造Hard Requirement Validator(`er003_key_words_min_unit.py::validate_min_unit_selection`、無変更)が`KEY_WORDS_STRUCTURE_INVALID`と判定し、選定は`max_attempts=1`のためcanonicalization以降に到達せずSTOPした事象が発生した。ユーザーが2026-09-06に`APPROVED_FOR_PRODUCTION`と正式決定し、選定Prompt(`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`、A2/B1共有)の自然さ基準パラグラフの直後へ新パラグラフとして「日本語グロスには、括弧（　）を使って別の訳し方・専門用語・補足情報を書き添えないでください。音声だけで聞いてそのまま意味が伝わる、平易な言い換えだけの一文にしてください。」の2文を追加した(特定語の列挙はせずblacklist化しない、既存の規約A/B・数値placeholder回避文・自然さ基準はいずれも無変更のまま維持)。retry(選定からやり直すKey Phrase Set Redundancy QA retry、最大2回)でも同じ選定Promptが使われるため整合する。既存Validator(`_JA_GLOSS_PARENTHETICAL_RE`、全角/半角括弧検知)は無変更のまま維持し、本Prompt追加はそのValidatorが拒否する前にモデル側で自発的に回避させる目的。単体テスト1件追加(`er003_test_b1_p2.py::test_template_contains_parenthetical_gloss_prohibition`)、既存49件+新規1件=50件PASS。`run_project_regression.py`(collected=2110、failed=3、失敗3件は既知の無関係failureで`git stash`比較により本タスクと無関係と確認済み)。**Runtime evidence**(2026-09-06、`er011_output/kp_ja_gloss_no_parenthetical_prod_wiring_01/`): Theme 2 B1・A2(Trial-12記事、Trial-13で使用したarticle.mdとdiffで内容一致確認済み)それぞれでProduction正式経路(`sc.run_key_phrases`、選定→canonicalization→Key Phrase Set Redundancy QA、無変更)を1回実行した。両レベルとも選定は構造Validatorを通過(`KEY_WORDS_STRUCTURE_PASS`)し、選定5件×2レベルのいずれのja_glossにも括弧(全角/半角とも)が一切含まれなかった(`any_parenthetical_in_selection=false`)。B1 rank3で再び"median"が選定されたが、今回のglossは「真ん中の値」(括弧補足なし、簡潔な言い換えのみ)で構造Validatorを通過した。canonicalization後もjapanese_gloss/japanese_gloss_tts双方が選定時のglossと同一のまま維持され、平易さも直前配線(KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01)の水準を保っていることを確認した(悪化事例なし)。実費$0.0329(約¥5.3、選定+canonicalization+redundancy QA計6件のLLM呼び出し、`er005_output/cost_baseline_01/pricing_snapshot.json`公式単価×実測usage) | `DECIDED`(`PRODUCTION_WIRED`) | KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01(ユーザー正式採用・Production配線、`OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01`で発見した事象への対策) | 2026-09-06 |
| Family X選定方式(DB Hybrid、Primary/Fallback) | ユーザーが2026-09-27に、Family X(News Entertainment)通常記事のKey Phrase選定方式として、KEY-PHRASE-DB-HYBRID-TRIAL-04(er029、baseline commit`57b61273`、12本文12/12 structural PASS)を`VALIDATED`→**`APPROVED_FOR_PRODUCTION`**と正式決定した。**Primary=DB Hybrid方式**(決定論的DB候補生成[CEFR-J/NGSL/Wiktionary/wordfreq、新規DB不使用]+compact shortlist promptでStrategy L選定gateを1回呼ぶ、本文全文はLLMへ送らない)、**Fallback=現行Strategy L全文方式**(本文全体をprompt送信する既存方式、無変更のまま維持)。Production module: `er030_key_phrase_db_hybrid_core_01.py`(Core、candidate generation/shortlist組み立て。Trial-04[`er029_key_phrase_db_hybrid_trial_04_stage1.py`+`er029_key_phrase_db_hybrid_trial_04_run.py::run_stage1_and_shortlist_v4`]の内容を関数名の"_v4"接尾辞のみ除去して複製した**ロジック無変更**の昇格、12本文で等価性を固定回帰化。er023/er027/er028[群1DB抽出・Wiktionary lookup・possessive noise除去・context mismatch検出等]は既存資産としてそのまま依存)+`er030_key_phrase_db_hybrid_selector_01.py`(Selector、compact shortlistから既存Production Strategy L選定gate`er003_key_words_production.run_production_selection_gate`[schema/model/validator一切無変更]を1回呼ぶ)。**責務分離**: DB HybridはStage 1候補生成+shortlist+Strategy L選定gate1回呼び出しの「軽量prompt版」であり、選定gate自体・canonicalization(`er003_key_words_canonicalization.py`)・Key Phrase Set Redundancy QA・source整合Gate(`KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01`)はいずれも既存Production資産を無変更のまま共有する(DB Hybrid/Strategy Lいずれの経路でも同一のcanonicalization/Gateを通る)。**Fallback発火条件**(`er030_key_phrase_db_hybrid_selector_01.DbHybridFailure`、修正1回目[Opus L2所見反映、2026-09-27]で改訂): (1) `SHORTLIST_TOO_SMALL`(shortlist総数<12、または`phrase_included_count+important_noun_included_count`<5、Trial-04実測12本文[全件total20〜24・phrase+important最小7]から導出、API呼び出し前に判定、費用ゼロ、fallback可)、(2) 選定gateの既存status非PASS(`KEY_WORDS_STRUCTURE_INVALID`/`TECHNICAL_GENERATION_FAILED`/`PARSE_FAILED`、既存validator無変更、fallback可)、(3) `SELECTOR_EXCEPTION`(Stage1/DB読込/Wiktionary API等の例外、fallback可)、(4) `SOURCE_SPAN_NOT_IN_RAW_ARTICLE`(選定PASS直後、`er003_key_phrase_source_gate_01.normalize_text`基準でitemのsource_span/source_sentenceが生article_textに実在しない、fallback可)、(5) `MODEL_CONTRACT_VIOLATION`(応答モデルが承認済みモデルと不一致、**fallback不可・STOP**、fallback先でも同じ契約違反が再発しうるため)。1呼び出しあたりのcost guard(¥5.0)超過は、PASS済み結果であればもはや失敗条件化せず`cost_guard_exceeded=true`を記録するのみ(より高価な全文方式への再課金を避ける、Fable決定)。記事単位の累積コスト上限超過(`KP_ARTICLE_COST_CAP_JPY`既定¥15.0、`run_key_phrases`スコープでdb_hybrid分を積算)は`KP_ARTICLE_COST_CAP_EXCEEDED`で**fallbackせずSTOP**。`DbHybridFailure`は`fallback_allowed`フラグ(既定True)を持ち、Falseの場合`_run_key_phrase_selection_db_hybrid_with_fallback`はfallbackせず再raiseする。**Telemetry**: `er030_output/kp_backend_telemetry_01/telemetry.jsonl`(既定strategy_l経路も含め`run_key_phrase_selection`の全呼び出しで1行記録[修正1回目でlegacy経路の記録漏れを解消]。各行は`spec_id`/`article_id`/`level`/`requested_backend`/`backend_used`/`final_status`/`fallback_triggered`/`fallback_reason_code`/`model_id`/`cost_jpy`/`synthetic`[bool、強制failure注入runの区別]を持つ。旧11行[新方式導入前のtest/evidence実行分]は`telemetry_bootstrap_evidence_2026-09-27.jsonl`へ退避)。**Per-article traceability**(修正1回目、B2新設): db_hybrid成功時も`{kp_dir}/keywords_runtime_metadata.json`へ`kp_backend`/`kp_backend_used`/`fallback_reason_code`/cost/model_id/attempt詳細を追記型で記録(fallback時は「db_hybridを試して失敗した事実」も残す)。`er019_family_x_audio_production_runner_01.py::run_theme_scaffold()`の`result[level]`/`entry_point.json`にも`kp_backend_used`を反映。**配線**: `er003_v1_n3_01_scaffold_generate.py::run_key_phrase_selection()`/`run_key_phrases()`にopt-in引数`kp_backend`(既定`"strategy_l"`、Family X以外の全既存呼び出し元[Family A/B/C/News/Z、B-Family等]は無変更)を追加。Family Xのみ`er019_family_x_audio_production_runner_01.py::run_theme_scaffold()`の既定値を`"db_hybrid"`にし、KP呼び出し(`sc.run_key_phrases(..., kp_backend=kp_backend)`)へ渡す。retry(Key Phrase Set Redundancy QA retry、最大2回)でも同じ`kp_backend`が一貫して使われる。**rollback**: `kp_backend`既定値(1箇所、`run_theme_scaffold`の関数引数既定値)を`"strategy_l"`へ戻すだけで即座に旧方式へ全面復帰可能(Trial記録`er027/er028/er029`はいずれも無変更のまま)。**test**: `er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`(Phase 1時点15件→修正1回目[Opus L2所見反映]で**32件**、全PASS、API呼び出し費用¥0。Core等価性[12本文]・bug A〜E再発なし・Family X 6本文の機械screening無回帰[Trial-04 REPORT §3実測shortlist件数と一致・ユーザー例示語保持を固定回帰化]・SHORTLIST_TOO_SMALL fallback発火・legacy既定不変・dispatch確認に加え、修正1回目でS1[12本文prompt文字列完全一致]・S3[source span不整合検知]・S4[cost guard/記事累積cost cap]・S6(a)[Trial run scriptとのbyte一致]・B1[legacy経路telemetry]・B2[per-article traceability]・B3[モデル契約違反時のfail-closed STOP]を追加。S2でWiktionary lookupをfake化し実行時間506秒→約221秒に短縮[実測値検証目的のtestのみ実API維持])。`run_project_regression.py`(詳細は`KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_REPORT.md`参照)。**Runtime evidence**(2026-09-27、`er030_output/family_x_kp_db_hybrid_evidence_01/`、実Production共有入口`sc.run_key_phrases(kp_backend="db_hybrid")`を実行、既存Production artifact不変更): Meta A2/B1B・Hormuz A2/B1Bの4記事で選定→canonicalization→Redundancy QAが全てPASS(model_id`gpt-5.6-luna`[ER-006-MODEL-ROUTING-CONTRACT-01経由]、選定実測費用合計JPY 9.2517[db_hybrid選定分のみ、canonicalization/redundancy QAは既存Production側が元々cost計測していないため対象外]、fallback非発火)。Hormuz A2で追加1回、cost guardを一時的にJPY 0.0001へ強制injectしてCOST_GUARD_EXCEEDEDを2回実際に発火させ、Strategy L全文方式へ実fallback(選定→canonicalization→Redundancy QA、全てPASS)することを実測した(Redundancy QA retryループ内でも同一のfallback経路が機能することを確認)。**Gate 3(article→audio連続性等)完了までは`PRODUCTION_WIRED`にしない**(判定はFable)。共有KP層(`er003_v1_n3_01_scaffold_generate.py`、Family A/B/C/News/Z全ての共有Production入口)の変更を伴うため、Mandatory Opus L2レビュー対象。**修正1回目**(2026-09-27、Opus L2所見反映、¥0): BLOCKER 3件(B1 telemetry観測性/B2 per-article traceability/B3 routing違反のfallback吸収)・SHOULD_FIX 8件(S1 prompt文字列一致実測/S2 Wiktionary lookup fake化/S3 source span照合/S4 cost guard意味論改訂+記事単位cost cap/S5 shortlist二条件化/S6(a) Trial run scriptからのutil移設/S7 実測値整合/S8 shortlist cache)へ対応(詳細は`KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_REPORT.md`§7・§8)。**post-fix runtime evidence**(2026-09-27、修正1回目後、`er030_output/family_x_kp_db_hybrid_evidence_02/`、Hormuz A2 1記事・実測JPY 2.6010): 実Production共有入口`sc.run_key_phrases(kp_backend="db_hybrid")`経由でB1(telemetry新schema、`synthetic=false`)・B2(`keywords_runtime_metadata.json`への`kp_backend_*`追記型merge)・S3(source span照合、非発火=正常)・S4(cost意味論、記事累積JPY 2.601≪上限JPY 15.0で未超過)・S5(shortlist=20≥12、phrase+important=12≥5)・model_id(`gpt-5.6-luna`、routing contract経由)をいずれも実測確認した(Key Phrase Set Redundancy QA retryが1回発火し2回目でPASS)。B3(routing契約違反時のfallback不可STOP)は課金を伴わないため既存mock test`ModelContractViolationStopsWithoutFallbackTests`の再実行で再確認(実API呼び出しなし)。詳細`KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_REPORT.md`§12。Sonnetは`PRODUCTION_WIRED`を単独宣言しない(最終判定はFable/ユーザー) | **`PRODUCTION_WIRED`**(Family X限定、Primary=DB Hybrid/Fallback=Strategy L。Fable Gate 3判定2026-09-27、Opus L2 BLOCKER 3件は修正1回目で解消済み、post-fix runtime evidence[commit`bc7d9bb8`]までGate 3全項目充足) | KEY-PHRASE-DB-HYBRID-TRIAL-04(検証・ユーザー`VALIDATED`→`APPROVED_FOR_PRODUCTION`)→KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01(Production module昇格・opt-in配線・test・runtime evidence、Phase 1)→同管理ID(修正1回目、Opus L2所見反映) | 2026-09-27 |
| Key Phrase選定LLM出力契約(Source Reference Contract、候補ID方式、Family X/Family Z共通Core) | ユーザーが2026-09-28に、KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06(`VALIDATED`)の候補ID方式を**Family X / Family Z共通Core contractとして`APPROVED_FOR_PRODUCTION`**と正式決定。selector LLM出力から`source_sentence`/`source_span`の自由記述を除去し、`source_candidate_id`(必須、当該呼び出しのshortlist候補IDのみ、JSON Schema enum制約)と`surface_echo`(任意的性質、非ブロッキングの取り違え検知専用、正誤判定には使わない)のみを出力させる。Python側が`source_candidate_id`→Stage 1候補(`surface_form`/`context_sentence_id`)→`source_sentence`(`sentence_reference[context_sentence_id]`)/`source_span`(`surface_form`)を決定論的に復元し、既存Production validator(`p2g.validate_min_unit_selection`)・canonicalization・Source Consistency Gate(`KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01`)を無変更のまま通す。Family X既存DB Hybrid配線(`er030_key_phrase_db_hybrid_selector_01.py::run_db_hybrid_selection`)へ実適用し、v1 baseline(候補生成・shortlist内容)は無変更のまま維持した(既存equivalence testで確認)。**Production module**: `er030_key_phrase_db_hybrid_source_reference_contract_01.py`(新設、候補ID割当・schema派生・prompt構築・API呼び出し・決定論的復元・gate orchestrationを実装、Trial実装`er034_..._contract.py`は無変更のまま残す)。`family_profile`引数(既定`"family_x"`)をFamily別最終選定ルールの差込点として新設、`"family_z"`は`NotImplementedError`(**Family Z DB Hybrid Core v2全体の採用は本管理IDの対象外・未決定のまま、`er026_*`text runnerは無変更**)。**Stage 1 `source_span`意味論整理**: `er030_key_phrase_db_hybrid_core_01.py`に新設した`_normalize_important_noun_candidate_source_span()`が、`important_noun_phrase_candidate`(`repeated_compound_noun_heuristic`)カテゴリのみ(このカテゴリの候補dictの`source_span`が「短い句」ではなく「その句が最初に出現した文全体」を保持するバグをTrial-06で発見)、`source_span`をsurface_form相当(短い句)へ補正し、旧「文全体」の値を新規`legacy_sentence_text`(deprecated)へ退避する(**`er027_key_phrase_db_hybrid_trial_02_stage1.py`自体は無変更、v1 baseline`er029`・Trial記録`er027`/`er028`・v2`er032`は一切影響を受けない、migration不要**)。downstream参照を全列挙し、旧「文全体」意味論への依存が既存コードに一切無いことを確認済み(`attach_compact_context`はsurface_form等で本文検索するのみでsource_spanを見ない)。**telemetry/backward compatible passthrough**: `keywords_runtime_metadata.json`(db_hybrid選定固有)へ`source_reference_contract`(`"candidate_id_v1"`)/`family_profile`/`candidate_mismatch_suspected_count`等を追加。`er003_key_words_canonicalization.py::merge_canonicalization_result()`は、選定itemに`source_reference_contract`/`source_candidate_id`/`surface_echo`/`candidate_mismatch_suspected`が**存在する場合のみ**`keywords_canonicalized.json`へそのままpassthroughする(これらのフィールドを持たない既存経路[Strategy L]の出力は完全に無変更)。`er003_v1_n3_01_scaffold_generate.py`の`_log_kp_backend_telemetry()`全呼び出し箇所へ`source_reference_contract`タグを追加し、db_hybrid成功時は`"candidate_id_v1"`、Strategy L(既定経路・fallback経路とも)は`"free_text_strategy_l"`を記録することで両contractの混在を`telemetry.jsonl`上で観測可能にした。**test**: 新規`er030_key_phrase_db_hybrid_source_reference_contract_01_test.py`(27件、候補ID復元決定論・Family別ガード・Stage 1整理regression・canonicalization passthrough・fallback contract混在telemetry等)、既存`er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`(32件、2件のmock対象を新しい呼び出し先へ更新)、`er034_..._trial_06_test.py`(21件、無変更)、`er003_test_key_words_canonicalization.py`(66件)、計146件全PASS(¥0)。**runtime evidence**(実Production共有入口`sc.run_key_phrases(kp_backend="db_hybrid")`経由、既存Production artifact非上書き、`er030_output/family_x_kp_source_reference_contract_evidence_01/`): Hormuz A2・Meta A2・Meta B1B・Hormuz B1B(Family X regression確認)+twins A2×3・Melos A2×3(quote-heavy、Trial-05/06の根本原因だった引用符コピーバグの再発なしを実データで確認)の計10回実行が全て`KEY_WORDS_STRUCTURE_PASS`・`candidate_mismatch_suspected_count=0`・`source_reference_contract="candidate_id_v1"`・model_id`gpt-5.6-luna`(実測)。強制`SHORTLIST_TOO_SMALL`注入によるfallback(Strategy L)実発火1回で、telemetryに`source_reference_contract="free_text_strategy_l"`が記録され両contractの混在が観測できることを確認した。**test修正時の事故開示**: 実装切替に伴うtest更新が後追いになり、2件のtestが旧呼び出し先をmockしたまま実際にOpenAI APIを2回呼び出し実測¥20.7826を消費した事故が発生(直ちに修正・再発防止、詳細REPORT §0)。**修正1回目(2026-09-28、Opus L2所見反映)**: SF-3として、`surface_echo`はJSON Schema strict mode制約によりschema上は必須プロパティだが、判定(PASS/FAIL)上は非ブロッキングであり取り違え検知専用の参考情報である(真実源にしない)ことを明確化した。N2として、Family ZのDB Hybrid系を将来Production配線する場合は`er030_key_phrase_db_hybrid_source_reference_contract_01`経由が規範として必須(旧`source_sentence`/`source_span`自由記述のコピー方式は禁止)であることを明記する。あわせてSF-1(surface_form/context_sentence_id独立決定に起因するsource_span不整合の補正・fail-closed化)・SF-2(死んだmockガード復活)・SF-4(display_phraseとの弱いlemma一致比較の追加)・SF-5(surface_form欠落時の旧fallback廃止)・SF-6(重複candidate_id選択の計測)・SF-7(family_profile検査の早期化)を実装した(詳細`KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01_REPORT.md`§10-11)。既存evidence10記事のオフライン再検証で、これらの修正が実データの復元結果(source_span/source_sentence/candidate_mismatch_suspected)を一切変えないことを確認済み(新規API呼び出しなし、¥0)。**Fable Gate 3判定: `PRODUCTION_WIRED`(2026-09-28、根拠: Opus L2所見反映`9fa6f388`+SSOT反映`b2736e13`/`b63fb35d`、既定backendやFamily Z runnerは未変更)** | **`PRODUCTION_WIRED`**(2026-09-28、Fable Gate 3判定。Family X配線+Family Z共通仕様、Family Z runnerは未配線のまま対象外) | KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06(設計レビュー・Trial実装・ユーザー`VALIDATED`→`APPROVED_FOR_PRODUCTION`)→KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01(Production配線) | 2026-09-28 |
| **4+1構成(Key Phrase 5枠=重要語・重要表現4+Topic Phrase/Word 1)** | ユーザーが2026-09-28に`APPROVED_FOR_PRODUCTION`と正式決定。Key Phrase 5枠を「重要語・重要表現4("important")+Topic Phrase/Word 1("topic")」構成へ変更。Topic定義(ユーザー逐語): 「汎用性・一般的な学習重要度は必ずしも高くないが、その記事に特有であり、事前に意味・用法・音を理解しておくことで本文全体を追いやすくなるワードまたはフレーズ」、中心質問「この語・表現を事前に理解していると、この記事の本文を明確に追いやすくなるか?」。固有名詞枠ではない・例示hard-code禁止(ユーザー明示)。本変更はA2/B1・Editorial Familyを横断する共通Key Phrase仕様であり、Family/3V専用仕様の新設ではない(既存「Family固有Key Phrase仕様を新設しない」STOP条件と非競合、ユーザー明示)。**実装**: `key_phrase_role`(enum`important`/`topic`)を共通schema`er003_key_words_min_unit._ITEM_SCHEMA_PROPERTIES`へ1箇所追加し、`er003_key_words_production.py`(`_ITEM_SCHEMA_PROPERTIES`同一オブジェクト参照)経由でStrategy L(B1/A2/Family Z/Family X fallback共通)、`er030_key_phrase_db_hybrid_source_reference_contract_01.build_item_schema_properties()`経由でDB Hybrid(Family X Primary)の両schemaへ自動伝播。選定Prompt`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`(A2/B1・両経路共有の唯一のファイル)へTopic追記文言1箇所(ユーザー定義の逐語+「候補区分[重要語/phrase/word]とは独立した選定後の役割ラベルである」旨の1文、例示・優先カテゴリのhard-codeなし)を追加。**構造Validator**: `er003_key_words_min_unit.validate_min_unit_selection()`へ(1)per-item enum妥当性チェック、(2)`expected_item_count==PRODUCTION_ITEM_COUNT_UNCHANGED`(5、本番経路のみ)の場合に限定したtopic=1件・important=4件の集計検証を追加(B2研究版10件はガード対象外)。不成立は既存`KEY_WORDS_STRUCTURE_INVALID`へそのまま合流(新しいstatus値・新しい分岐点は作らない)。DB Hybrid側は`er030_key_phrase_db_hybrid_selector_01.py`のINVALID発火箇所へ、telemetry識別専用の`detail_reason_code="ROLE_STRUCTURE_INVALID"`タグを追加(分岐先・`fallback_allowed`既定値は無変更)。**canonicalization passthrough**: `er003_key_words_canonicalization.merge_canonicalization_result()`のpassthroughリストへ`key_phrase_role`を追加(存在する場合のみ引き継ぐ、旧artifact[フィールド欠落]は後方互換)。**追加表示用データ**: DB Hybrid経路のみ、`db_hybrid_stage1_debug.json`/`shortlist_with_ids`から選ばれなかった候補を新規`kp_auxiliary_candidates.json`(件数上限なし・shortlist出現順・「未検証・参考候補」フラグ付き)へ構造化保持、`keywords_runtime_metadata.json`へ`selection_contract="4plus1_v1"`/`role_counts`/`auxiliary_candidate_count`を追加。Strategy L経路は`auxiliary_candidates: null`+`auxiliary_candidates_reason: "not_available_strategy_l"`を記録(表示件数・UI配置はユーザー判断待ち、本Phaseでは実装しない)。新規UI実装なし、追加LLM callなし(既存selector call内で処理)、Redundancy QA/source consistency gate/TTS reading copy/TTS本体は無改修(既存ロジックがtopic/important区分を見ずに動作するため)。**test**: 新規`er003_test_key_words_min_unit_4plus1_01.py`(修正1回目でOpus L2所見S3によりrename、既存命名規約`er0NNN_test_*.py`に統一。27件、schema伝播・4+1 validator PASS/FAIL・B2 10件ガード・canonicalization passthrough・DB Hybrid reason_code合流の白箱確認・Strategy L structure invalid→既存retry経路合流・retry 2回目到達報告・S1 role_counts観測性・DB Hybrid backup_item補完3種・N7定数等価性)、既存test 4ファイル(`er003_test_key_words_min_unit.py`/`er003_test_p2i_production.py`/`er003_test_b1_p2.py`/`er030_key_phrase_db_hybrid_source_reference_contract_01_test.py`、Opus L2所見S7によりファイル数を是正)のfixtureへ`key_phrase_role`を追加(non-breaking)。

**修正1回目(2026-09-28、ユーザー既決事項+Opus L2所見S1〜S7/N1/N7反映)**: (1)Strategy L経路`_run_key_phrase_selection_strategy_l`の`max_attempts`を`1`固定から`prod.MAX_PRODUCTION_RETRY_ATTEMPTS`(=2)へ変更。2回目到達時は`keywords_runtime_metadata.json`/telemetryへ`strategy_l_attempts`/`retry_reached_second_attempt`を記録しprintでも明示(報告必須)。(2)DB Hybrid経路(Family X Primary)のみ、selector schemaへ`backup_item`(important役割の予備候補1件、必須プロパティ・常に返す)を追加。topicが欠損(0件)または単独で無効(構造・候補ID検証で無効)かつそれ以外は全item健全な場合にのみ、Python側(`er030_key_phrase_db_hybrid_source_reference_contract_01.run_source_reference_contract_gate`内`_identify_topic_backup_substitution_target`)がbackup_itemを5件目として`key_phrase_role="important"`で機械的に置換し(`topic_requirement_satisfied_via_backup=True`で`validate_min_unit_selection`のtopic=1件要求のみをスキップして再検証、他の判定は無変更)、`topic_slot_filled_by_backup`/`backup_substitution_reason`をruntime_metadata/telemetryへ記録。曖昧なケース(topic複数返却・target以外にも問題あり・backup候補ID重複/解決不能)は既存のINVALID→fallback経路へそのまま委ねる(新候補生成ロジックは作らない)。Strategy L側schemaは無変更。(3)DB Hybrid guidance文言(`_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`)へbackup_item指示1段落追加、共有Prompt(`b1_p2_keywords_l_prompt_template.txt`)のTopic段落へ「該当する語・表現が見当たらない場合でもtopicを空にせず最善候補を選ぶ」旨の1文追加(S6により「残り4個は上記の基準に従って選んでください」への参照形へ縮約、候補区分列挙も「候補の種類・区分」へ一般化)。(4)「5個のうち少なくとも1個は重要語区分から」という既存guidance文言(`er030_key_phrase_db_hybrid_source_reference_contract_01.py`)は無変更のまま、topic由来の1件で充足可(ユーザー決定、機械検証は元々存在せずguidanceのみのため実装変更なし)。(5)Strategy L runner_up(5枠外候補)契約は引き続き未実装、OPEN-211を`DEFERRED`(将来のUI設計時に再検討)へ更新。(6)Opus L2所見: S1(Strategy L telemetryがINVALID時に`role_counts: null`になる観測性欠落)是正、S2(evidence実行がProduction telemetryへ`synthetic=false`混入)是正、S3(新規test rename・件数照合meta-test不変条件回復)是正、S4(`er034_..._trial_06_test.py`fixtureへ`key_phrase_role`追加)是正、S5(`er003_key_words_production.py`にtest専用・4+1非対応の1行コメント追加)是正、S6(Prompt再掲の縮約・一般化)是正、S7(REPORT/SPEC記載の既存testファイル数是正)是正、N1(`detail_reason_code`判定が`item_reasons`も参照するよう是正)反映、N7(`PRODUCTION_ITEM_COUNT_UNCHANGED==PRODUCTION_ITEM_COUNT`等価性test追加)反映。検証: 新規test27件+既存test4ファイルfixture更新全PASS(計331件)、`run_project_regression.py`(failed=7・errors=2、委任文の既知baselineと一致、機能regression0件)、実データ(DB Hybrid meta_a2実測¥1.1945・Strategy L melos_a2、いずれも`synthetic=True`、実行時は双方とも1回目でPASSし今回はretry/backup補完は発火せず、双方の機構は単体test[27件中6件が該当]で確認)。詳細: `KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_REPORT.md`「修正1回目」節。**runtime evidence**(`er035_output/kp_4plus1_evidence_01/`、実測selection cost合計¥4.8383): Family X News(Meta/Hormuz、DB Hybrid)4記事+Family Z Fiction(Melos)・legacy Family C(twins)・legacy Family B(Voices)計4記事(Strategy L)+forced fallback1件の計9件全てが`role_counts`={important:4, topic:1}で`KEY_WORDS_STRUCTURE_PASS`に到達。DB Hybrid 4件全てでTopic該当語がStage1 shortlistの既存候補区分(重要な単語・単語群候補、またはphrase候補)から選ばれ、専用のTopic候補区分は存在しないことを確認(Phase A設計書の予測どおり)。Topic Phraseはいずれも固有名詞ではなかった(固有名詞偏りなし)。Important 4件は同記事の旧Production 5件と概念的に高い重複(3〜5/5)を保ち品質劣化は未観測。melos_a2は評価中に2回失敗(1回は既存source_sentence整合性チェック起因で4+1と無関係、1回は`topic=2件`のrole構成不成立で4+1 validatorが実際に機能した例)、3回目でPASS(Strategy L経路`run_production_selection_gate`の`max_attempts=1`固定[本タスク以前からの既存挙動]により、`run_key_phrases`単位では自動retryされない)。**Fable Gate 3判定: `PRODUCTION_WIRED`(2026-09-28、スコープ: 共通Key Phrase経路[Strategy L/DB Hybrid両経路・全Family]の4+1構成、DB Hybrid backup補完、Strategy L retry 2回+2回目報告、runner-up DEFERRED[OPEN-211]。根拠: commit`0e6744e0`/`0cb59383`、Opus L2[BLOCKER 0、S1〜S7/N1/N7反映]、evidence9記事+差分evidence_02、test27件+regression baseline一致)** | **`PRODUCTION_WIRED`**(2026-09-28、Fable Gate 3判定。共通Key Phrase経路[Strategy L/DB Hybrid・全Family]の4+1構成、runner-upはOPEN-211で`DEFERRED`) | KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(Phase A設計・Fable判断→Phase B最小実装+検証evidence) | 2026-09-28 |

### Key Phrase 音声構造(Standard/Advanced 共通骨格)— Status: `PRODUCTION_WIRED`(2026-09-29、Fable Gate 3=Meta run_03。`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§E2E Meta run_03、runtime evidence: Advanced KP全5rankで`explanation.voice="Aoede"`・Variant B文言・`phrase_repeat`が`english`と同一sha256、Standard全5rankで`japanese_meaning.style_prefix`=J3文言。W4/W5で配線済み)

ユーザーが2026-09-29に、Key Phraseセクションの音声構造をStandard/
Advanced共通の骨格として正式決定した(逐語決定文は`DECISION_LOG.md`
同日エントリ参照、解釈・拡張はしない)。**共通骨格**: 両レベルとも
「英語Phraseを最初と最後にもう一度聞く」構造にし、中間部分のみレベル別
に変える。

| レベル | 構造 | 中間部分 |
|---|---|---|
| Standard(A2/B1) | 英語Phrase→**日本語意味(J3)**→英語Phrase | 日本語意味(`japanese_gloss`/`japanese_gloss_tts`、既存「Key Phrasesセクション構成」行[番号→英語→日本語訳→英語]と同一内容。**2026-09-29追記(W5)**: 音声StyleはJ3[`_role_style_ja()`、上記「可変segment Role Style」節と同一関数・同一backendゲート]を`APPROVED_FOR_PRODUCTION`として正式適用、配線済み) |
| Advanced(B1B) | 英語Phrase→**英語解説(Variant B)**→英語Phrase | 英語解説(`KEY_PHRASE_EXPLANATION_EN`、text仕様は次節「Advanced Key Phrase 英語解説」、音声StyleはVariant B採用) |

**付帯条件(ユーザー決定、逐語)**: 最後の英語Phraseは最初と同じcanonical
Phraseを使用し、追加の別文言・別候補は作らない。Standard側の既存構造は
壊さず、対応関係を明確に保つ。retry/fallback/cache/Master Storeのいずれ
の経路でも、最初と最後のPhraseが同一canonical text・同一正式音源/生成
条件になること(既存Master Audio Store cache identity設計と整合させる)。
**コスト**: Advancedで英語Phraseがもう1回再生される分について、既存
Phrase音源のreuseで済むかを配線時(W4)に実測し、reuse可能なら量産API
コスト増として数えない(reuse不可[新規生成callが必要]の場合は増分として
明示する、ユーザー要求)。**この決定により、Advanced KP Assembly順序に
関するUSER_DECISION_REQUIREDは解消した**(次節「Advanced Key Phrase
英語解説」の音声Styleに関するUSER_DECISION_REQUIREDも、本決定で
Variant B採用のため併せて解消)。**配線**: `FAMILY-X-REFRESH-E2E-
PRODUCTION-WIRING-01`のW4(Advanced英語解説)・W5(Standard日本語意味へ
のJ3適用+Opus L2所見是正[KP解説fail-closed、cache text/style_version
guard])で実施済み。**`PRODUCTION_WIRED`(2026-09-29、Fable Gate 3=Meta
run_03のruntime evidence)。** | 出典:
`DECISION_LOG.md`(2026-09-29エントリ、`FAMILY-X-REFRESH-E2E-PRODUCTION-
WIRING-01`) | 2026-09-29 |

### Advanced Key Phrase 英語解説(text仕様)— Status: `PRODUCTION_WIRED`(2026-09-29、Fable Gate 3=Meta run_03。text仕様は2026-09-28ユーザー正式決定、音声Style[Variant B]は2026-09-29決定、配線はW4[`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`]、`PRODUCTION_WIRED`化は上記「Key Phrase 音声構造」節と同一のGate 3判定による)

ユーザーが2026-09-28に、Advanced(B1B)Key Phraseの英語解説**text仕様**(KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02のB候補: 同一の英語Key Phrase+平易な英語解説を追加する方式)を`APPROVED_FOR_PRODUCTION`と正式決定した。**要点**: (1) 英語Key Phrase自体は既存選定結果(Strategy L/DB Hybrid、4+1構成含む)を変更せず流用する、(2) 解説文はKEY-PHRASE-LEVEL-SPEC-TRIAL-01で定義した`explanation_en`の仕様文をそのまま逐語再利用する、(3) 語数上限は目安15語、新規Factの追加はしない(記事本文に存在する情報の範囲内で言い換える)、(4) 決定論的チェック3種(語数・新規Fact混入・重複表現)はGate候補として検討中だが未確定。**Role**: `KEY_PHRASE_EXPLANATION_EN`という名称のRoleを想定していた。**2026-09-29追記(配線完了、`PRODUCTION_WIRED`)**: Family X(`er019_family_x_audio_production_runner_01.py`)のAdvanced(B1B)経路へ`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`W4/W5で正式配線した(既存`japanese_gloss`/`japanese_gloss_tts`とは別の新フィールドとして追加、Standard[A2]側は引き続き日本語意味のまま無変更)。**「B-Family」節(Family B、Voices)のKey Phraseは対象外・無変更のまま**(旧文中の「B-Family」節参照は別Familyであり本追記の対象ではない、Family XとFamily Bを混同しないこと)。**音声Style**: `KEY_PHRASE_EXPLANATION_EN`の音声Styleは、KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03(Before「clear, precise, explanatory」/After「clear, precise, unhurried」比較)→`KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04`(中間3案A/B/C比較、Bは「clear, precise, at a measured pace, without dragging」)を経て、ユーザーが2026-09-29に**Variant B「clear, precise, at a measured pace, without dragging」を正式採用**と決定した(`DECIDED`、`USER_DECISION_REQUIRED`は解消)。上位の音声構造決定(前節「Key Phrase 音声構造(Standard/Advanced 共通骨格)」)と併せて参照し、重複記述はしない。 | 出典: KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02(text仕様B候補・ユーザー正式採用)、KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03/`TRIAL-04`(音声Style比較Trial)、`DECISION_LOG.md`2026-09-29エントリ(Variant B正式採用・音声構造決定) | 2026-09-29 |

## Preview

**適用範囲の注意(2026-08-17追記)**: 本節は**A2、および旧P-series B1**の
Preview仕様を記す。**現行B1(Support-based Natural English)のPreviewは
本節と異なり、平易な英語・Charon voice**である(B1 Support節を参照)。
本節を「A2/B1共通のPreview実装仕様」と読まないこと(Cross-level仕様節の
「Preview原則」は言語・voiceによらない編集原則であり、本節の技術仕様
[言語・TTS model・voice]とは別レイヤー)。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 言語 | 日本語のみ(A2、および旧P-series B1) | `DECIDED` | ER-003-B1-P9A-R1(英語Key Phrase埋め込み方式は不採用) | 2026-08-07 |
| TTS model | `gemini-3.1-flash-tts-preview` | `DECIDED` | ER-003-B1-P7A(commit `b4f871f`) | 2026-08-06 |
| 採用理由 | 旧モデル(2.5)で「激しい」→「げきせつな」等の誤読が発生し、3.1で解消を確認 | `DECIDED` | ER-003-B1-P7A | 2026-08-06 |
| voice | Aoede(A2、および旧P-series B1)。**現行B1はCharon**(B1 Voice構成節を参照) | `DECIDED` | ER-003-B1-P7A以降 | 2026-08-06 |
| 生成方式 | 単一TTS call(chunk分割なし) | `DECIDED` | ER-003-B1-P7A | 2026-08-06 |
| Key Phrase埋め込み | しない(Full Story側のみで扱う) | `DECIDED` | ER-003-B1-P9A-R1以降 | 2026-08-07 |
| モデル分離 | Preview(3.1)とFull Story(2.5)の設定を分離、片方の変更が他方に波及しない設計 | `DECIDED`、`ModelIsolationTests`で固定確認済み | ER-003-B1-P8A | 2026-08-07 |
| 承認フロー | ①台本(日本語テキスト)をチャットで提示→ユーザー承認→②その台本のまま音声生成→③音声試聴→ユーザー承認。台本確定後の勝手な再生成・変更はしない | `DECIDED` | ER-003-REPRO-01/02-PREVIEW系 | 2026-08-08〜09 |
| A2 Preview長さ | No.8実測(157文字・4文・28.6秒)がユーザーから「長い」と指摘され、theme/problem/value/questionの4要素を律儀に別文で書き並べない、2文程度・80〜110字程度を目安とする指示へPrompt(`PREVIEW_ROLE`、`er003_v1_iran01_a2_generate.py`)を更新した。絶対文字数を固定するhard limitではなく目安(多少の増減は許容、150字・4文を超える長いPreviewは避ける)。No.8実データ(実際のarticle.md・comment_1/2テキスト)を使い、本番のPrompt/model/context経由で新規生成した結果157字→74字(2文)を確認(runtime evidence)。**2026-08-29追記(ER-20)**: No.8本編のPreview音声を実際にこの短縮テキストで再TTS・Assembleし、完成版へ反映済み(下記Artifactで試聴可能) | `DECIDED`(`PRODUCTION_WIRED`、No.8完成版へ反映済み) | ER-008-N8-QA-CONTENT-SPEED-HARDENING-18(トライアル提示・ユーザー試聴)→ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19(ユーザー正式採用・Prompt配線)→ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20(No.8完成版へ反映) | 2026-08-29 |
| B1 Preview話し方 | No.8実測でB1 PreviewのWPM(184.5)が他のCharon segment(topic_intro 143.9・comment_1〜4は148.1〜173.5)より明確に速いことを判明させた(現状調査、実測値)。原因はPreviewだけを遅くする専用instructionが存在しなかったこと(全segment共通の`ENGLISH_STYLE_PREFIX`のみ)。A2の`A2_ENGLISH_STYLE_PREFIX_SLOWER`と同じ「自然言語のみ、数値WPM指定はしない」方針で、Preview専用の`B1_PREVIEW_STYLE_PREFIX_CALM`("calm, clear, unhurried tone"指示)を新設し、`generate_charon_english`の`style_prefix_override`引数(既存の汎用パラメータ、新規追加ではない)経由でPreview呼び出しのみに適用した(topic_intro/comment_1-4は無変更)。ユーザーが比較試聴の上、正式採用 | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N8-QA-CONTENT-SPEED-HARDENING-18(現状調査・比較試作・ユーザー試聴)→ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19(Production配線) | 2026-08-29 |
| B1 Comment 1-4話し方 | ユーザーが正式決定し、Previewで採用済みの`B1_PREVIEW_STYLE_PREFIX_CALM`("calm, clear, unhurried"instruction、`er003_v1_n3_01_tts_generate.py`)をComment 1-4にも適用するようPreview/Comment共通ループへ配線した(`generate_b1_segments()`のpreview/comment_1〜4ループで`style_prefix_override`・`disfluency_qa=True`を全件へ適用)。定数コメントの"this introduction"という限定文言は"this"という汎用文言へ変更(Comment適用に合わせた最小修正)。WPM固定値・数値speed指定は新設しない(`assert_no_wpm_specification`で保証、既存のまま)。No.8実データで実際にComment 1-4を再TTS・ASR再検証し、実測WPM: preview=154.5(旧184.5)/comment_1=181.8/comment_2=143.0/comment_3=148.6/comment_4=153.6を確認(いずれもPreviewと極端な乖離なし、comment_1は14語の短文のためWPM分散が大きい)。全件disfluency QA(flagged=false)・ASR verified=trueを確認 | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19(現状調査)→ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20(ユーザー正式決定・Production配線・No.8実データで実証) | 2026-08-29 |

## Full Story

**適用範囲の注意(2026-08-17追記)**: 「chunk構成(3chunk)」はP-seriesの
パイプライン(単一のFull StoryをTTS 1呼び出し内で3分割生成)を指す
`HISTORICAL`情報。N3以降はFull Story Part1/Part2をそれぞれ独立した
1回のWriter/TTS呼び出しで生成し、3chunk分割は行わない。TTS model
(`gemini-2.5-pro-preview-tts`)・voice(Aoede)は、N3のFull Story Part1/2・
Point One/Two・In One Line(=News Content)でも同一の値が使われており、
この2項目はP-series/N3を通じて現在も有効。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| TTS model | `gemini-2.5-pro-preview-tts` | `DECIDED`(凍結仕様、N3のNews Contentでも継続使用を確認) | ER-003-B1-P4D〜P8A | 2026-08-06以前 |
| voice | Aoede(News Content。B1のNavigator/Support要素はCharon、B1 Voice構成節を参照) | `DECIDED` | 同上 | 同上 |
| chunk構成 | `HISTORICAL`(P-series専用、3chunk)。N3以降はPart1/Part2をそれぞれ単一呼び出しで生成し、chunk分割はしない | `DECIDED`(P-seriesの凍結仕様として) | ER-003-B1-P4D〜P8A | 同上 |
| 内容QA retry | 3試行1セット(`run_tts_content_attempts`) | `DECIDED` | ER-003-B1-P8A系 | 2026-08-07 |
| 短文ナレーション生成 | 前後文脈のない短いフレーズは専用の最小限instructionで生成 | `DECIDED` | ER-003-B1-P9A-R1(commit `d41e4fe`) | 2026-08-07 |
| strict ASR検証 | 部分一致 + ASR文字数上限(期待文字数+少数の余裕)の両方を確認 | `DECIDED` | A02 meaning_5発見を機に追加 | 2026-08-08 |
| minimal instruction fallback | 標準経路が規定回数(既定6回)不合格の場合、最小限instructionへ自動フォールバック(短文ナレーションに適用)。**2026-09-01追記(ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22)**: 英語Key Phrase Component(`generate_key_phrase_component_verified`)は、この標準経路[ENGLISH_STYLE_PREFIX]起点の構成をユーザー正式決定により離脱し、「Key Phrase」節の専用retry構成(Minimal instruction[Primary]→English language lock付きMinimal[Fallback])を使う。本行の記述は短文ナレーション(`generate_narration_snippet_verified_strict`の直接呼び出し元、例: `stage_c_generate_new_narrations()`等)にのみ引き続き適用される。**2026-08-26更新(ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04)**: fallback(minimal instruction)経由で生成された英語音声は、Primary ASRの結果に関係なくSecondary ASR(Azure)による確認を必須化した(`er006_secondary_asr_01.py::evaluate_attempt_with_cascade(force_secondary=True)`)。standard path側は無変更・追加コストなし。No.7 A2 point_one_headingで実際に発生した「Primaryは正常認識・Secondaryは全く別内容」という誤PASS事故の再発を防ぐ暫定対策(fallback自体の根本原因見直しはOPEN-66・OPEN-67参照、`DEFERRED / AFTER USER VALIDATION`) | `DECIDED`(fallback導入)、`PRODUCTION_WIRED`(Secondary ASR必須化、2026-08-26) | ER-003-REPRO-01-MAIN(導入)、ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04(Secondary必須化) | 2026-08-08(導入)、2026-08-26(Secondary必須化) |
| Dynamics処理 | **不使用**(scalar gainのみ、compressorやDynamics3は使わない) | `DECIDED` | `er003_b1_p9a_audio.py`にコード内コメントで明記 | 2026-08-07 |
| Evidence Compression(方式C、Lossless Editor) | 通常WriterがFact-safeな記事を生成した直後(`er003_v1_n3_01_articles_generate.py::run_one_pattern()`内)、Lossless Editor(`er003_v1_n3_01_evidence_compression_editor.py`)がspoken layerだけを軽量化する。許可: 不要な出典名(企業・調査会社・研究機関・メディア・イベント名)の削除・一般化、重複/近似数字の圧縮(ただしトレンドの大きさ・方向そのものを理解するために必要な核心的比較は残す)、冗長なEvidence説明の簡素化。禁止: Fact追加・削除、correlation→causation、certainty強化、uncertainty/hedging削除、scope拡張、negation変更、comparison direction変更、temporal direction変更、Point意味変更、Story論旨変更。Research/Evidence Pack/VFL/Fact Ledger自体は変更しない。Editor適用後のテキストに既存のFact Check/Ledger Deviation Checkをそのまま適用する(同じ安全確認プロセスを再利用)。`apply_evidence_compression`引数(`run_one_pattern`)/`apply_evidence_compression_editor`引数(`run_writer_for_theme`)、既定`True`(Production既定で有効)、DEV/testでOFFにしたい場合のみ`False`を渡す。**2026-08-29追記(ER-22、日付・数値も圧縮対象に追加)**: ユーザーが方向転換し、学習者の理解に不要な日付・数値も圧縮対象へ追加した(「日付は必ず1個」「数字は必ず削る」という機械的hard ruleにはしない。時系列理解・ニュースの核心・Fact特定に必要な日付・数値は残してよい、判断に迷う場合はFact safetyを優先し残す)。No.8実データで検証: April 14(発表日)とJune 8(9ゲート開設・確認日)のうち、Editorは一貫してJune 8を残しApril 14を"earlier this year"へ一般化した(A2/B1とも)。ただしEditor呼び出しの生成結果には日付とは無関係な副作用(B1でStephen Reicher/Kristie Tseという既存承認済み実名を"one/another psychologist"へ一般化)が混在しており、これは採用せず、日付部分のみ手動で反映した(実名は維持、OPEN-84参照)。Editor呼び出しは1回ごとに指示範囲外のテキストも変わりうることが実データで判明したため、当面はEditor出力を無条件採用せず差分レビューする運用とする。**2026-08-29追記(ER-23、地名・施設名も圧縮対象に追加)**: ユーザーが正式決定し、学習者の理解に不要な地名・空港名・施設名の一般化も許可編集リストへ追加した(同じく「地名は必ず削除」というhard ruleにはしない、地理的意味・事実関係を変えない範囲で判断)。No.8実データで検証: Editorは"Dallas Fort Worth International Airport"をA2/B1とも一貫して"Dallas Fort Worth"へ短縮する判断をした。ただしこの変更をNo.8へ反映する前提条件(Fact Check PASS)を満たせなかった(Fact Check再実行が地名圧縮とは無関係な既存記述4件に対し`REVIEW_REQUIRED`を返した。ベースラインはPASSだったため、live web検索を伴うFact Checkerの非決定性が原因と考えられる、OPEN-92参照)。そのためNo.8のarticle.md/parts.json/音声への適用は見送り、候補内容のみ`{a2,b1b}/audit/evidence_compression_locations_23_candidate.json`に記録した(OPEN-84参照)。**2026-08-29追記(ER-24、No.8へ正式反映)**: ユーザーが「地名圧縮自体がFact Checkエラーを起こしたものではない」と整理し、無関係なFact Check結果だけでblockしない方針を確定させたため、A2 full_story_part2・B1 full_story_part2/in_one_lineの計3segmentへ実際に反映した(`er008_n8_location_compression_24.py`)。適用後の確認Fact Check/Deviationでも新たに検出された指摘はいずれも地名圧縮とは無関係な既存の表現上の懸念(flight attendants帰属・"more controlled digital process"の運用効果への言い過ぎ等、編集前の原文でも同一に成立する懸念)であり、地名圧縮自体が新たなFact問題を生んだものではないと判断した。3segmentを再TTS・ASR再検証(全件`asr_verified=true`)し、Audio Validation Gateを経てA2/B1を再Assemble(A2 359.7秒/B1 318.5秒、いずれもclipping無し)、完成版へ反映済み | `DECIDED`(`PRODUCTION_WIRED`、日付・数値・地名・施設名ルールを含む。No.8自体への地名圧縮適用も完了) | ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03(script-only初回実証)→ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04(方式B比較・方式C推奨・Fact safety不変条件追加)→ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05(方式C MAJOR精査)→ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06(ユーザー正式採用・Production配線)→ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22(日付・数値も対象化、No.8実データで検証)→ER-008-N8-FINAL-PRODUCTION-HARDENING-23(地名・施設名も対象化、No.8実データで検証・Fact Check非決定性を発見)→ER-008-N8-FINAL-CLOSEOUT-24(No.8へ正式反映・再Assemble完了) | 2026-08-26(2026-08-29追記) |
| A2 Key Phrase pause(番号→phrase間) | A2のみ、番号読み上げ→Key Phrase本体の間を、既存の`KEY_PHRASE_INTERNAL_PAUSE_SECONDS`(0.4秒)より合計+0.2秒長くする(`A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS`、`er003_v1_n3_01_assemble.py`)。B1は無変更(0.4秒のまま)。No.7実音声で実測: 各Key Phraseで約0.61〜0.67秒(元Baseline実測の約0.41〜0.47秒からおよそ+0.2秒) | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N7-CONTENT-AUDIO-QA-02(+0.1秒)→ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06(さらに+0.1秒、合計+0.2秒) | 2026-08-26 |
| A2英語ナレーション速度指示 | A2の英語spoken content(Full Story Part1/2・Point One/Two見出し・本文・In One Line)にのみ、既存のENGLISH_STYLE_PREFIX(emotion/prosody指示)の末尾へ自然言語の追加指示("Speak at a slightly slower, relaxed pace than natural adult narration, while keeping the delivery smooth, conversational, and natural. Do not exaggerate pauses or sound instructional.")を付与する(`A2_ENGLISH_STYLE_PREFIX_SLOWER`、`er003_v1_n3_01_tts_generate.py`)。数値WPM指定・speed factor指定はしない(`assert_no_wpm_specification`で保証)。B1・fallback(minimal instruction)経路には適用しない。No.7での実測: 新旧で使用テキストが完全に異なる(Method C適用+Writerの新規生成)ため単純比較はできないが、平均WPMは138.8→141.5とむしろ微増しており、この指示だけで明確な減速効果は確認できなかった(そのまま報告、追加のprompt再調整はしていない) | `DECIDED`(`PRODUCTION_WIRED`、効果は限定的と判明) | ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06 | 2026-08-26 |
| A2英語ナレーション速度(post-processing time-stretch) | 自然言語Prompt(上記行)がsame-text条件下でも安定して機能しない([OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-71〜74参照、ER-008-A2-SPEED-SAME-TEXT-ABC-09でB/CともAより速くなることを確認)ことを受け、既存の完成音声そのものをFFmpeg `atempo`フィルタ(pitch-preserving time-stretch、単純なsample-rate変更[pitchが下がる]ではない)で事後的に減速する方式を検証(ER-008-A2-TIMESTRETCH-ABC-10、No.7 A2 Full Story Part 1で3%/6%/9%比較、pitch実質不変・ASR内容破損なしを確認)した上で、**ユーザーが試聴の上6%を正式採用**した(ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11)。`er008_a2_postprocess_slowdown_01.py`(`apply_a2_slowdown`、既定6%)を新設し、`er003_v1_n3_01_tts_generate.py::generate_a2_segments()`の`generate_a2_segment_with_slowdown()`経由でA2英語7segment(point_one_heading/point_two_heading/full_story_part1/full_story_part2/point_one/point_two/in_one_line)全てへ配線した。**既存の自然言語「わずかに遅く」instruction(`A2_ENGLISH_STYLE_PREFIX_SLOWER`)は引き続き使用する**(ユーザーが承認した音声は instruction込みの音声への6% time-stretchであり、instructionを除去したものではないため)。time-stretch前の通常ペース音声は`{name}_original.wav`として保持し、Middle等で現状より速い読み上げが必要な場合にTTS再生成なしで再利用できる。post-process後の音声を実際にASRで再検証し、不一致の場合は最大3回まで通常ペースから取り直すretry機構を持つ(実運用でpost-process後にのみASR不一致が生じる事象を発見、retryで解消することを確認済み、[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-76)。No.7 A2の7segment全てを実データで再生成し、Audio Validation Gateを実PASSで再assemble済み。比較Artifact: https://claude.ai/code/artifact/6efa0f4c-79a8-4d1e-a3ae-8c81d853a53d | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-A2-TIMESTRETCH-ABC-10(検証)、ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11(ユーザー承認・Production配線) | 2026-08-26 |
| Storytelling First(Production初回Writer正式原則) | No.9試聴でWriterが「調査レポート的」(Evidence・数値を項目的に読み上げる)になる問題が指摘され、独立Trial(`er009_writer_trial_diagnostic_04/05.py`、`er009_n1_full_writer_ledger_integration_08.py`)で改善を確認していたが、ユーザー正式承認・Production初回Writerへの実装無しにDiagnostic Full Retryのprompt文言だけが先行して`Preserve Storytelling First.`を参照する不整合([OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-95、Dangling Reference)が生じていた。ユーザーが正式に`APPROVED_FOR_PRODUCTION`と決定し、「Factを登場順にただ読み上げず、まず聞き手に何を持ち帰ってほしいかを決め、Hook/Meaning/Evidence/Interpretationを自然なspoken passageとして織り交ぜる。Evidenceは物語を支えるために使い、Evidence自体を主役にしない」という指示を`er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`(全テーマ共通のProduction初回Writer prompt)へ正式に追加した。既存のMain Story/Point One/Point Two/In One Line構造、Point Balance原則、Spoken-first数値原則、Fact Ledger制約はいずれも変更していない。**Meaning Firstは独立原則としては`REJECTED`**(Storytelling First内の「聞き手に何を持ち帰ってほしいか決める」要素で十分とユーザーが判断、[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-91) | `DECIDED`(`PRODUCTION_WIRED`、Writer prompt本体への実装完了。個別記事のLedger Deviation有無は記事ごとに別途QAで判定する、下記No.9実データ参照) | ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03(問題発見・Trial)→ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06(正式採用・Production実装・No.9実データで検証) | 2026-08-31 |
| No Jargon(learner-facing本文全体、Production初回Writer正式原則) | No.9でKey Phraseだけでなく本文中でも"regression discontinuity"のような高度な統計・学術手法名が使われる懸念があったため、Storytelling Firstと同時にユーザーが正式`APPROVED_FOR_PRODUCTION`と決定した。Main Story・Point One・Point Two・In One Lineを含む記事本文全体で、聞いただけでは理解しにくい専門用語・学術的な手法名をそのまま使わず、研究者が実際に何と何を比較したのか・なぜその比較から判断できるのかを平易なspoken Englishで説明するよう`COMMON_BLOCK_TEMPLATE`へ明記した(Factを変えない・因果を強めない・scope/certainty/比較の方向を変えないことは維持)。**Key Phrase専門語回避基準(OPEN-90)とは別仕様**であり、両者を混同しないことも明記した(OPEN-90は2026-08-31、ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09でNo Jargonによる上流解決として`RESOLVED / CLOSED`) | `DECIDED`(`PRODUCTION_WIRED`、Writer prompt本体への実装完了) | ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03(問題発見)→ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06(正式採用・Production実装・No.9実データで検証) | 2026-08-31 |
| Evidence-bounded Interpretation(Production初回Writer正式原則) | Trial(`er009_writer_trial_diagnostic_05.py`)でStorytelling First/No Jargonと組み合わせて考案されたが、正式なユーザー承認・Production実装は無いまま未報告のTrial専用ruleに留まっていた(ER-010-NO9-SPECIFICATION-RECONCILIATION-08監査で発見)。ユーザーが正式に`APPROVED_FOR_PRODUCTION`と決定し、`er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`(No Jargon節の直後)へ、「解釈・示唆・締めの一言(Interpretation)を書く場合、その内容はVerified Fact Ledgerが確立したscope・causality・certaintyを超えない。特定集団の結果を広い集団へ一般化しない。一度限りの結果を"always"/"every time"のような一般的断定にしない。確信が持てない場合はより小さく安全な表現にするか省く」という指示を追加した。既存のFact Ledger制約・Fact safety不変条件はいずれも変更していない。**Production初回runtime確認(No.9実データ、ER-010-09)**: B1のFact Checkerが「Rutgers記事は『高級店』限定の統計を、記事は『米国の飲食店全体』へ一般化している」という**Interpretation文ではなく本文中のEvidence説明文における**scope拡張を指摘した(REVIEW_REQUIRED)。これは本指示が明示的に対象とする「解釈・示唆・締めの一言」の範囲外であり、**Evidence説明文自体のscope拡張までは防げないという実証された限界**として正直に記録する(Ledger Deviation Checker側では検知されず、Fact Checkerが独立に捕捉した)**2026-08-31追記(ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10、追加runtime確認・対象外範囲の再確認)**: Local Rewrite Loop化後のNo.9新候補で、Fact CheckerがA2・B1Bとも新たに、(1)Haggag and Paci論文が直接検証したのは推奨額全体を上げることの因果効果であり「最初の数字がアンカーになる」という心理メカニズムそのものは論文が識別していない(causality/mechanismの言い過ぎ)、(2)Rutgers報告の「最上級店」限定を「米国の飲食店全体」へ一般化している(scope拡張)、(3)(B1Bのみ)タクシー研究の効果をレストラン画面へ直接一般化している(scope拡張)、という3件を指摘した。前回同様、これらはいずれも「解釈・示唆・締めの一言」ではなく本文中のEvidence説明文で発生しており、Ledger Deviation Checkerでも検知されず、Fact Checkerが独立に捕捉した。**Evidence文自体のcausality/scope拡張までは防げないという限界が、2回連続の独立したNo.9生成データで再確認された**(単発の偶然ではなく、本指示の文言上の対象範囲[解釈・示唆・締めの一言]に起因する構造的な限界と考えられる) | `APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`(Writer prompt本体への実装完了。Evidence文自体のscope拡張は対象外という限界を実データで確認済み) | ER-009-N1-STORYTELLING-LEDGER-TRIAL-05(Trial、未報告)→ER-010-NO9-SPECIFICATION-RECONCILIATION-08(発見・比較表提示)→ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09(ユーザー正式採用・Production実装・No.9実データで検証) | 2026-08-31 |
| Formatting禁止(絵文字・不要な太字Markdown、Production初回Writer正式原則) | No.9(ER-010-06版候補)のタイトルに絵文字(💳)・本文各所に太字Markdown(`**13 million**`等)が出現し、既存QA gate(Ledger Deviation Checker/Fact Checker/Point Overlap QA/Directional Fact Precheck)のいずれもこの書式問題を検知対象にしていなかったことが判明した(OPEN-99)。`er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`へ絵文字・不要な太字禁止の明示指示を追加し、新設した`normalize_article_formatting()`(全絵文字・Markdown太字記法・複数スペース圧縮の除去)をWriter出力後・Local Rewrite後の2箇所の呼び出し経路(`_generate_and_compress_article()`内、Local Rewrite Loop内)へ配線した(prompt側禁止指示+fail-safe自動削除の二重対策)。No.9新候補(ER-010-11版)のA2/B1B双方で絵文字・太字とも0件を確認(**2026-09-02追記**: CURRENT_SPEC.mdへの記録漏れをER-010-NO9-FINAL-APPROVAL-CLOSEOUT-AND-FULL-STATUS-AUDIT-28で発見・修正。実装[`COMMON_BLOCK_TEMPLATE`のprompt行168・`normalize_article_formatting()`定義行434・呼び出し行632/871]自体は2026-09-01時点で既にPRODUCTION_WIRED済みであり、ユーザー承認済み・Production wired済みの事実の記録漏れのみを今回補完した。新仕様の追加ではない) | `DECIDED`(`PRODUCTION_WIRED`、`FormattingNormalizationTests`6件PASS) | ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10(発見・OPEN-99記録)→ER-010-NO9-FORMAT-PRODUCTION-AND-FACT-REVIEW-11(実装・Production配線)→ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12(No.9新候補runtime確認・OPEN-99 CLOSE)→ER-010-NO9-FINAL-APPROVAL-CLOSEOUT-AND-FULL-STATUS-AUDIT-28(CURRENT_SPEC記録漏れ補完) | 2026-09-01(実装)、2026-09-02(記録補完) |
| Hook-aware Deviation Checker(Ledger Deviation Checker v2への追加ロジック) | Trial(`er009_writer_trial_diagnostic_05.py`)で、Ledger Deviation Checker v2が語りかけ・場面描写のHook文を過剰検知する懸念に対する緩和ロジックとして考案されたが、正式なユーザー承認・Production実装は無いまま未報告のTrial専用ロジックに留まっていた(ER-010-NO9-SPECIFICATION-RECONCILIATION-08監査で発見)。ユーザーが正式に`APPROVED_FOR_PRODUCTION`と決定し、`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check(hook_aware=True)`として実装した。語りかけ・場面描写として機能し、Ledger内で既に確認済みの状況を会話的に言い換えているだけで、新しい具体的Factを追加していない一文に限り、`changed_scope`/`changed_comparison`の2種類だけを緩和対象とする。それ以外の8種類のフラグ(`changed_fact`/`changed_causality`/`changed_certainty`/`changed_number`/`changed_actor`/`changed_negation`/`changed_time`/`unsupported_new_claim`)は、Hookであっても常に通常通り検査する(Hookだから何を書いてもよいわけではない、過去の危険Hook fixture 3種で偽陰性が無いことをTrial-05実データで確認済み)。`hook_aware`引数は既定`False`で、Production呼び出し側(`er003_v1_n3_01_articles_generate.py::run_one_pattern()`)のみ明示的に`hook_aware=True`を渡す(他のDEV/Trial呼び出し元の挙動は無変更)。**Production初回runtime確認(No.9実データ、ER-010-09)**: A2のタイトル"Why the Tip Screen Always Suggests More Than You Meant to Give"を`treated_as_hook: true`と判定しつつ、"Always"という絶対語をchanged_certaintyとして正しくMAJOR判定した(Hookとして緩和されるのはscope/comparisonのみという設計通りの動作を実データで確認)。**新たに判明した限界(正直に記録)**: この"Always"の指摘は、記事生成直後の初回Hook-aware判定(3件MAJOR検出、タイトルは含まれず)では出ず、局所Rewrite後の最終全文再判定でのみ出現した。同一チェッカー・ほぼ同一本文に対する2回の独立LLM呼び出し間で判定結果が変わりうる(Fact Checkerの非決定性[OPEN-92]と同種の現象がLedger Deviation Checkerでも観測された)。設計通りfail-closedで`NG_REVIEW_REQUIRED`として正しく検知・報告されたため実害は無いが、新規Open Itemとして記録する(OPEN-98)**2026-08-31追記(ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10、Local Rewrite Loop化後のNo.9新候補runtime確認)**: Local Rewrite Loop化後に再生成したNo.9新候補(`er010_output/no9_local_rewrite_loop_final_10/`)では、A2の初回Hook-aware判定でMAJOR1件のみを検出し、局所Rewrite後の全体再判定は`LEDGER_COMPLIANT`(MAJOR/MINORとも0件)に到達した。前回(ER-010-09)観測されたタイトルの"Always"新規MAJOR化は今回は再現しなかった(OPEN-98はユーザー判断によりCLOSED/REMOVE、単発の判定揺らぎとして独立追跡はしない)。B1BはMINOR1件(`changed_time`、Hookとしては扱われず通常の説明文として判定)のみで、こちらもMAJORは0件だった | `APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`(危険Hook fixtureへの安全性はTrial-05で確認済み、Production実runtimeでの動作[Hook判定+Fact Safety両立]も確認済み) | ER-009-N1-STORYTELLING-LEDGER-TRIAL-05(Trial、未報告)→ER-010-NO9-SPECIFICATION-RECONCILIATION-08(発見・比較表提示)→ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09(ユーザー正式採用・Production実装・No.9実データで検証) | 2026-08-31 |
| Ledger Deviation MAJOR時の局所Rewrite(Local Rewrite) | Trial(`er009_n1_full_writer_ledger_integration_08.py`)で自動Rewriteパイプラインが実装されたが、実行時にMAJORが一度も発生せず(A2/B1とも初回`LEDGER_COMPLIANT`)、自動Rewriteループ自体が一度も実際に発火した実績が無いまま未報告のTrial専用実装に留まっていた(ER-010-NO9-SPECIFICATION-RECONCILIATION-08監査で発見。「NG→修正→再PASS」の既存実動作確認は、この自動パイプラインではなく、人間が手で書いた文を使った別のTrial[`er009_ledger_generalization_boundary_06.py`]によるもので、両者は別物)。ユーザーが正式に`APPROVED_FOR_PRODUCTION`と決定し、新規モジュール`er010_ledger_local_rewrite_09.py`(Trial-08のREWRITE_SYSTEM_PROMPT・3段階escalating attempt[Attempt1=issue提示、Attempt2=flags/explanation追加、Attempt3=scope-safe fallback]・`locate_target_sentence()`[exact substring→word-overlap>=0.25 fallback]をそのまま踏襲、新しい上限は作らない)として実装し、`er003_v1_n3_01_articles_generate.py::run_one_pattern()`のLedger Deviation Check(Hook-aware)直後に配線した。対象はMAJORのみ(MINORは対象外)、修正は当該文(前後の文をcontextとして参照するのみ)に限定し、記事全体は再生成しない。最大`MAX_REWRITE_ATTEMPTS=3`回試行しても解消しない場合はPASS扱いにせず、`human_review_required=True`として記録した上で記事全体を`NG_REVIEW_REQUIRED`として返す(無限retry禁止、MAJOR残存の黙示PASSを許さない)。**Production初回runtime実発火確認(No.9実データ、ER-010-09、待望のfirst evidence)**: A2で初回Hook-aware判定がMAJOR3件を検出し、3件全てが**Attempt1で解消**した実例を確認した。例: Before "The rides were very similar, so the researchers could compare passengers who saw different menus."(未確認の方法論的前提を断定)→After "The researchers used the fare threshold to compare passengers who saw different menus."(Attempt1、`LEDGER_COMPLIANT`)。他2件も同様にAttempt1で解消(詳細は`er010_output/no9_production_integration_final_09/a2/audit/local_rewrite_results.json`)。ただし局所Rewrite後の最終全文再判定で、局所Rewrite対象ではなかったタイトルの"Always"が新たにMAJORとして検出され(上記Hook-aware Deviation Checkerの限界[OPEN-98]参照)、記事全体としては`NG_REVIEW_REQUIRED`のまま出荷していない(設計通りfail-closed、Directional Fact Precheckも未実行)**2026-08-31追記(ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10、Local Rewrite Loop化・cycle上限を跨いだ再帰的修復への拡張)**: 従来は「局所Rewrite→記事全体を1回だけ再判定」で終了し、その再判定で修正対象ではなかった箇所に新規MAJORが見つかっても対応しない設計だった(実際にER-010-09版のNo.9 A2で、タイトルの"Always"が局所Rewrite後の最終再判定でのみ新規MAJOR化する実例が発生した)。ユーザーがこれを正式に指摘し、「全体再Checkで新規MAJORが見つかった場合も、上限cycleまで再度局所Rewriteする」設計への拡張を承認した。`er010_ledger_local_rewrite_09.py`へ`MAX_REWRITE_CYCLES = MAX_REWRITE_ATTEMPTS`(=3)を追加し、`er003_v1_n3_01_articles_generate.py::run_one_pattern()`のLocal Rewrite呼び出しを`while major_items and cycle < MAX_REWRITE_CYCLES`のループへ書き換えた。**cycle上限は新しい値を独自に発明したものではなく、既存承認済みの文単位試行上限MAX_REWRITE_ATTEMPTS(Trial-08由来、3回)を、記事全体cycleという別次元にもそのまま適用したもの**(ユーザーがER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10で明示的に許可)。対象はMAJORのみ、cycle上限に達してもMAJORが残る場合は無限retryせず`NG_REVIEW_REQUIRED`のまま返す(既存のfail-closed設計を維持)。回帰テスト(`er010_n9_production_integration_09_test_01.py`)に、cycle1で解消しなかった別文がcycle2で新規MAJORとして検出され解消されるシナリオ、およびcycle上限まで使い切ってもMAJORが残るexhaustionシナリオを追加し、いずれもPASS。**Production初回runtime確認(No.9新候補、ER-010-10)**: A2で初回Hook-aware判定がMAJOR1件を検出し、局所Rewrite cycle1・Attempt1で解消、全体再判定で`LEDGER_COMPLIANT`(MAJOR/MINORとも0件)に到達した。前回(ER-010-09)観測されたような「cycle2への突入(新規MAJOR再発)」は今回のNo.9では自然発生しなかったが、そのロジック自体は上記の模擬回帰テストで実証済みである。**新たに判明した限界**: このLoopはLedger Deviation Checkerが検出するMAJORのみを対象とし、Fact Checker(live web検索)が独立に指摘するscope/causality/certaintyの懸念(下記Evidence-bounded Interpretation行のNo.9実データ参照)には一切対応しない(Fact Checker REVIEW_REQUIREDはこのLoopのトリガーになっていない、既存の意図的な設計)**2026-09-05追記(OPEN-113-POINT-CONTEXT-PRODUCTION-WIRING-AND-NO18-B1-REGEN-04、ユーザー正式採用、Point-context-only方式のProduction配線)**: OPEN-113(Local Rewrite後の同一Point内意味重複、No.18 B1 Trialで発見)についてTrial-01〜03で検証した結果、Trial-03の「対象文が属するPoint全体をRewriteモデルへ参考contextとして追加するだけ(Rule文言・System Prompt・Retry回数・Ledger再チェック方法は一切変更しない)」という単一変数案がVALIDATEDとなり、ユーザーが正式採用した。`er010_ledger_local_rewrite_09.py`へ`extract_point_context()`(見出し行で記事をsectionへ区切る汎用実装、Main Story/Point One/Point Two/In One Lineいずれも同一ロジックで扱い、Point One/Twoに限定しない)を追加し、`REWRITE_ATTEMPT{1,2,3}_TEMPLATE`へ「参考情報のみ」のPoint contextブロックを追加、`rewrite_ng_item()`の引数に`point_context`を追加した。`er003_v1_n3_01_articles_generate.py::run_one_pattern()`のLocal Rewriteループで対象文所属sectionを取得して渡すようにし、所属section特定に失敗した場合のみ旧来の前後1文へfallbackする。既存のREWRITE_SYSTEM_PROMPT・各attempt指示文言・Retry上限・Ledger再チェック呼び出し方法・DELETE機能(元々なし)はいずれも一字一句変更していない。実Production関数を直接呼び出すRegression(`er011_open113_production_wiring_regression_04.py`、Trial-01〜03と同一の3fixture/4項目)で、既知の重複ケース(No.18 B1)を含む全4項目がattempt1で意味重複なく解決し、Point contextが実際に渡されたことを記録した(`point_context_found=true`)。全文再判定で2件に一時的なMAJORが出たが、記事・Rewrite文を変えない追加の全文再判定1回で再現せず(`LEDGER_COMPLIANT`)、Rewrite対象文とは無関係な既存Ledger Deviation Checkerの判定揺れ(下記関連Open Item参照)によるものと確認した。No.18 B1を実Production経路(`er006_pool_pilot_01_writer.py::run_writer_for_theme`が呼ぶ`gen.run_one_pattern`と同一呼び出し、4層Promptは不使用)で再生成した結果はLedger COMPLIANT・Local Rewrite自体は不発火(新規MAJORが発生しなかったため。既知の重複問題はそもそも4層Prompt Trial[`er011_open112_a_family_4layer_prompt_trial_05.py`]の出力でのみ観測されたものであり、現行Production系譜には元々存在しなかったことを示唆する)。A2は再生成せず、既存承認済みartifactは無変更のまま維持した(コード変更は`major_items`が空でない場合のみ実行される分岐内に限定され、A2側の通常生成に副作用がないことをコード構造上確認、かつA2水準のfixture[No.9 2件・No.18 A2 1件]もRegressionでPASS)。追加API callなし(既存の呼び出し回数計算式のまま、Point context分のprompt token増加のみで実測1回あたり平均約75語)。既存回帰テスト`er010_n9_production_integration_09_test_01.py`に新規テスト5件(`extract_point_context()`のsection特定、Point context表示・System Prompt不変の確認)を追加、33件全PASS。プロジェクト全体回帰(`run_project_regression.py`)は2075件中2072 PASS、残り3件(`er003_test_bad`の意図的fixture・`er003_test_p2j_investigate`のOPEN-77既知meta-test集計バグ2件)は本タスク変更前から存在する無関係failureであることをgit stashで確認済み **追記(2026-09-13、OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-COMMON-BASE-TRIAL-01 Phase B、PM-CLOSEOUT-CONSOLIDATION-104)**: `locate_target_sentence()`へtarget-sentence-matching受理ロジックをopt-in(既定OFF)で追加した(Trial実装、Production自動経路への配線・既定ON化は未実施、`USER_DECISION_REQUIRED`のまま)。既定OFF時はbyte一致で無変更(既存89件テスト回帰PASS実測)。あわせて、副次的に発見した`split_sentences()`の見出し行混入バグ(`resolved=True`と記録されながら本文が書き換わっていないサイレント失敗)を修正した。これは既存仕様(Local Rewriteが「対象文を書き換える」という既存の意味)を変更しない整合性修正であり、Fable自律範囲として`APPROVED_FOR_PRODUCTION`(Production採用)とした(既存89件+新規22件テスト回帰PASS、ユーザー拒否可)。差分QA案I(Fact Checker A'+Ledger Deviation Checker再投入)はTrial専用スクリプト実装のみでProduction自動経路へは未配線(`USER_DECISION_REQUIRED`)。詳細: `OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-COMMON-BASE-TRIAL-01_REPORT.md`Phase B節。 | `APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`(実装完了、Production初回runtimeでMAJOR3件全件のAttempt1解消を実証。ただし局所Rewrite範囲外の新規MAJORでNG_REVIEW_REQUIREDに至った実例もあり、「Rewriteすれば必ずPASSする」という意味の保証ではない。**2026-09-05追記**: Point-context-only拡張も`PRODUCTION_WIRED`、実Production関数によるcontrolled runtime fixtureで実発火・重複解消・Ledger compliantを確認済み)。**2026-09-13追記(PM-CLOSEOUT-CONSOLIDATION-105、ユーザー正式判断、OPEN-141)**: target-sentence-matching(`er010_ledger_local_rewrite_09.py::rewrite_ng_item(use_target_sentence_matching=True)`、window全体ではなく対象文自身に紐づくdeviationのみで受理判定)をA-Family(`er003_v1_n3_01_articles_generate.py`)・B-Family(`er012_b_family_voices_writer_generic_01.py::run_ledger_deviation_and_local_rewrite()`)の両呼び出し元で既定ONへ切替した(`PRODUCTION_WIRED`)。あわせて、Local Rewrite受理直後に差分QA案I(対象文±1文をFact Checker A'+Ledger Deviation Checkerへ再投入、`run_diff_qa_for_accepted_rewrite()`/`apply_diff_qa_to_resolved_rewrite()`、同ファイル)を配線した。verdict扱い: Fact Checker A'のverdict=`FAIL`またはLedger再評価=`LEDGER_DEVIATION`のみ不受理(既存human_review_required/cycleへ合流、新規機構なし)、`REVIEW_REQUIRED`は記録のみで通過(既存Fact Checker A'運用方針と同一)。Point Overlap rule-based再計算(`er008_point_overlap_qa_18.recompute_point_overlap_for_target_sentence()`)も同時配線(¥0)。`DIFF_QA_CALLS_PER_ITEM=1`(既存`MAX_REWRITE_CYCLES`/`MAX_REWRITE_ATTEMPTS`と独立の別軸カウンタ)。詳細`OPEN-141-TARGET-SENTENCE-DIFF-QA-PRODUCTION-WIRING-01_REPORT.md`) | ER-009-N1-FULL-WRITER-LEDGER-INTEGRATION-08(Trial、自動ループ未発火)→ER-009-LEDGER-GENERALIZATION-BOUNDARY-06(手動Rewriteの間接的Checker耐性実証)→ER-010-NO9-SPECIFICATION-RECONCILIATION-08(発見・比較表提示)→ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09(ユーザー正式採用・Production実装・No.9実データで初実発火確認)→OPEN-113-LOCAL-REWRITE-CONTRACT-TIGHTENING-TRIAL-01/HIERARCHICAL-CONTRACT-TRIAL-02(重複問題発見・REJECTED)→OPEN-113-POINT-CONTEXT-ONLY-TRIAL-AND-POSTCHECK-INTEGRATION-AUDIT-03(VALIDATED)→OPEN-113-POINT-CONTEXT-PRODUCTION-WIRING-AND-NO18-B1-REGEN-04(ユーザー正式採用・Production配線・No.18 B1再生成) | 2026-08-31(初版)、2026-09-05(Point-context-only拡張) |

## Audio Assembly

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 複数箇所編集の順序 | 時系列で**後ろから前へ**適用(insert2→insert1→title_trim等) | `DECIDED` | ER-003-B1-P7C(バグ発見)〜P9A-R1/R2で徹底 | 2026-08-07 |
| 境界検出 | MFA(Montreal Forced Aligner)を優先、RMSは補助のみ | `DECIDED` | プロジェクト全体方針(P3W以降) | - |
| 数字・日付境界 | MFA単独で確定せず、必ずASRまたは他の診断で裏付ける | `DECIDED` | ER-003-B1-P9A-R2("England 1–2 Argentina"語順バグを機に確立) | 2026-08-07 |
| notification2挿入 | Full Story内2箇所(Today's Points直前、In One Line直前) | `DECIDED` | ER-003-REPRO-01/02-MAIN | 2026-08-08〜09 |
| 音量調整 | scalar RMS基準(他要素は平均RMSへ、OutroはIntro基準RMSへ一致)。A01のみ追加の聴感補正(約-5.85dB)を適用、A02/ADD03には適用していない。**2026-09-06訂正(ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01、OPEN-115で発見)**: 旧記述「Preview/Bodyは無調整のアンカー」は実装(`er003_v1_n3_01_assemble.py::apply_a2_gain`/`apply_b1_gain`)と一致していなかった。実際にはPreviewのみgain=1.0で無調整(Comment等と同じRMSアンカーとして使われるだけ)であり、Body(`full_story_part1`等)は他segmentと同様に`compute_gain_for_target_rms(max_peak=0.95)`でgain適用される | `DECIDED`(訂正反映) | ER-003-B1-P9A系/ER-003-REPRO-01-MAIN | 2026-08-07〜08、2026-09-06訂正 |
| Assembly最終段ヘッドルーム安全弁 | `apply_a2_gain`/`apply_b1_gain`の各segmentは24kHz mono時点で`compute_gain_for_target_rms(max_peak=0.95)`によりpeak<=0.95に制限されるが、直後の`mono_24k_to_stereo_target()`(`resample_poly`による24kHz→48kHzアップサンプリング)はゲイン制御の外にあり、内容依存で最大+8.9%程度のオーバーシュートを起こしうる(実測: Trial-13 A2 `Point One`で0.95000→1.03502、OPEN-115・計測-16で確定)。`assemble_with_timeline()`はnp.concatenateのみ(重ね合わせ無し)のため、完成ミックス全体のpeakは常にseq中いずれかのpieceのpeakと一致する。この構造を利用し、`stage_assemble_a2`/`stage_assemble_b1`が呼ぶ共通関数`apply_headroom_safety_valve()`で、完成ミックスのpeakが`HEADROOM_PEAK_THRESHOLD`(既定0.98)を超えたときだけ、エピソード全体へ一律スカラーgain(`閾値/peak`)を掛けて閾値以内へ収める(相対バランスは維持)。閾値以下なら一切変更しない(byte同一)。適用有無・適用前後peak・スカラー値・原因piece名は`gain_report.json`より前に`headroom_report.json`(および`run_summary_assemble.json`)へ必ず記録する(静かに救済しない)。安全弁適用後もなおpeakが1.0を超える異常時は、`write_wav_float()`のクリッピング防止assertより前に、原因pieceを含むドメイン例外(`RuntimeError`、`ASSEMBLY_HEADROOM_SAFETY_VALVE_INSUFFICIENT`)で停止する(`write_wav_float()`側のassertは最後の砦として維持)。`gain_report.json`/`timeline.json`/`headroom_report.json`はいずれも`write_wav_float()`より前に書き出す(診断性改善、書き出し失敗時にも証跡が残る) | `PRODUCTION_WIRED` | ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01(採用根拠: Opus診断-14・計測-16・OPEN-115、ユーザー承認2026-09-06) | 2026-09-06 |
| No.8完成版 再Assemble(ER-20) | 今回のProduction配線(disfluency QA/Point overlap QA/Comment内部ラベル二重防御/A2 slowdown invariant gate/A2 Preview短縮/B1 Preview・Comment calm style)を反映するため、No.8の変更segmentのみ再TTS(A2: preview。B1: preview・comment_1〜4)し、他segmentは既存のVALIDATED/HUMAN_APPROVED音声(point_two等)をそのまま再利用した上で、`stage_assemble_b1`/`stage_assemble_a2`を実行して完成版を再Assembleした。Audio Validation Gate(A2 slowdown invariant含む)は両レベルともPASS。A2: duration 360.97秒(6:01)・peak 0.854・clipping無し。B1: duration 327.51秒(5:28)・peak 0.825・clipping無し。ユーザー最終試聴用Artifact: https://claude.ai/code/artifact/ddedda51-daee-44c4-9e3a-88212deb30b1 | `USER_FINAL_REVIEW`(ユーザー最終試聴待ち) | ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20 | 2026-08-29 |
| No.8完成版 再Assemble(ER-21) | disfluency QA資産-記録紐付けの恒久修正(kp2 "uneven choice"の実修正)・Key Phrase 1 gloss括弧禁止修正を反映するため、影響segmentのみ再TTS(A2: kp2_english・meaning_1[kp1 gloss]、他は無料ローカル再検査でクリーン確認のみでTTS再生成なし)し、`stage_assemble_b1`/`stage_assemble_a2`を再実行した。新設したdisfluency QA必須証跡チェック・asset hash staleness チェックを含め、Audio Validation Gateは両レベルともPASS。A2: duration 359.34秒(5:59)・peak 0.854・clipping無し。B1: duration 327.51秒(5:28、ER-20から変更なし)・peak 0.825・clipping無し。kp2_en.wavは本番経路で再生成後、disfluency QA flagged=false・ASR EXACT_MATCHを確認(実際にAssembleへ採用されたファイルそのものであることをGate通過時点のhash一致で保証)。ユーザー最終試聴用Artifact(更新): 同一URL | `USER_FINAL_REVIEW`(ユーザー最終試聴待ち) | ER-008-N8-FINAL-QA-HARDENING-21 | 2026-08-29 |
| No.8完成版 再Assemble(ER-22) | "wait"意味衝突修正・Evidence Compression日付ルール適用のため、影響4segment(A2/B1とも full_story_part1・full_story_part2)のみ再TTS・ASR再検証した(`er008_n8_wait_and_date_fix_retts_22.py`)。この過程で2件の未発見バグ(ASR検証のcontraction誤検知、A2 slowdown post-process後のsha256未更新)と1件の固有名詞TTS発音誤り(B1"Stephen Reicher"、下記2項目参照)を実データで発見・修正した。修正後、`stage_assemble_b1`/`stage_assemble_a2`を再実行しAudio Validation Gateは両レベルともPASS。A2: duration 357.145秒(5:57)・peak 0.90634・clipping無し。B1: duration 323.314秒(5:23)・peak 0.89835・clipping無し。ユーザー最終試聴用Artifact(更新): 同一URL | `USER_FINAL_REVIEW`(ユーザー最終試聴待ち) | ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22 | 2026-08-29 |
| ASR検証のcontraction(短縮形)対応 | No.8 B1 full_story_part2の実データで、TTSが自然に"They are"を"They're"と発話しただけで3回中3回ともTRUE_CONTENT_MISMATCH誤判定になる事象を発見した。原因は`er006_preprod_hardening_01_validation.py::normalize_text()`がアポストロフィを空白へ置換するため"they're"が"they"+"re"の2 tokenへ分かれ、canonical側の展開形"are"は既にstopwordだが短縮形の残骸"re"はstopword集合に無く、内容の変化が無いのに孤立したcontent_word_diffとして検出されていたこと。`_STOPWORDS`へ"re"を追加して修正(実データで確認できた範囲に限定、"will"/"have"由来の"'ll"/"'ve"はreplace型diffになるため別対応が必要でOPEN-90として保留)。この修正はNo.8限定ではなく、ASR検証を使う全segment・全記事に影響する共通の安全側修正 | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22 | 2026-08-29 |
| B1固有名詞発音safe-reading("Stephen Reicher"→"Riker") | No.8 B1 full_story_part1で、独立した4回のASR(OpenAI Primary×2、Azure Secondary×2)すべてが心理学者名"Stephen Reicher"を一貫して"Steven Reichert"に近い形で書き起こした。既存の固有名詞発音調査機構(Pronunciation Ledger research)が本人による発音訂正記録を含む外部ソースを調査し、正しい発音はIPA `/ˈraɪkər/`("RY-ker"、Star Trekの"Riker"と同じ発音)と高確信度で判明した。4回全てが同じ方向で一貫して誤ったことから単発のASR誤認識ではなくTTS自体の発音誤りと判断し、ER-010の日付safe-reading("April 28"→"April twenty eighth")と同じ設計思想で、記事本文の表示用綴り(article.md/parts.json)は"Stephen Reicher"のまま変更せず、TTS入力・ASR比較対象のテキストにのみ適用する`tts_safe_name_pronunciation_en()`を新設し`tts_safe_news_en()`へ配線した。適用後1回目の生成で`asr_verified=True`(ASR: "Stephen Riker"、完全一致)を確認 | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22 | 2026-08-29 |

## QA / Human Review

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| Evidence Compression Editor(方式C)追加ルール: Pattern A + Listener-Friendly Numeric Precision | 既存方式C(Lossless Editor、`er003_v1_n3_01_evidence_compression_editor.py`)のPromptへ、Trial-18/19/20で検証した文言をそのまま追加した(No.18固有語のhardcodeなし、全テーマ共通の一般Production仕様)。**Pattern A: Representative Metric + Supporting Trend**: 同一研究・調査内で複数指標が同じ方向を示す場合、最も代表性の高い指標1つの比較数値(絶対値)だけを保持してよく、その他の指標はFactとして残しつつ具体数値を省き"showed the same pattern"等のtrend表現へ言い換えてよい(補助Fact削除禁止・Fact統合禁止)。**Listener-Friendly Numeric Precision**(全Pattern共通、Pattern自身の判断の後に適用): 残す価値があると判断した数値について、意味(比較方向・story上の大きさ・閾値・解釈・値同士の区別)が変わらない場合のみ、より単純な概数を優先してよい。小数の機械的削除は禁止、丸めが意味のある差・閾値・小規模測定・解釈・区別を損なう場合は小数を保持する。最重要制約: 丸めは異なるFact・指標・group・time point・survey質問・実験結果の統合を許可しない(丸め後も各数値は元のFact/指標へ追跡可能であること)。既存の絶対禁止事項(Fact追加/削除禁止・correlation→causation禁止・certainty強化禁止・scope拡大禁止等)は無変更。単体テスト9件(`er011_no18_evidence_compression_a_precision_21r_test_01.py`)でProduction Prompt内の文言一致・順序・既存禁止事項の維持・call site(`_generate_and_compress_article()`が初回生成・Diagnostic Full Retry双方から共通で呼ばれる単一箇所であること)を固定。**Production runtime evidence**: No.18 A2/B1を実Production経路(`er003_v1_n3_01_articles_generate.py::run_one_pattern()`、Writerは既存承認済み出力を再利用、Evidence Compression以降は全て実関数)で再生成し、両レベルで実際にPattern A+Precisionが発火(例: 99.71/108.95→about 100/about 109、processing speedはtrend表現化)、Ledger Deviation Check=`LEDGER_COMPLIANT`(0件、両レベル)、Directional Fact Precheck=A2`PASS`/B1 1件`DIRECTION_REVIEW_REQUIRED`(F-005/F-006とは無関係な既存の2018年調査文、non-blocking)、Fact Checker=A2`PASS`/B1`REVIEW_REQUIRED`(non-blocking advisory)を確認。**Pattern B(Conclusion-First/Numeric Necessity Test)・Pattern C(Listener-Friendly Numeric Re-expression)は未採用**(`DEFERRED CANDIDATE / NOT REJECTED`、Trial-18/19/20の記録を保持し将来再検討可能)。No.9 OPEN-100(3設問survey構造でのnumeric羅列問題)は本仕様では解消しない(Pattern Aは2条件比較の代表指標選定を想定した設計であり、OPEN-100の3設問構造には構造的に対応しない、`DEFERRED / NON-BLOCKING`のまま)。**2026-09-07追記(ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01)**: 上記Listener-Friendly Numeric Precisionルール(文言は無変更のまま維持)を補強する新規追加ブロック`NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK`を追加した(既存ブロックの後に挿入、既存ブロック自体は書き換えない)。原則: 「聞き取りやすさを優先し、意味を損なわない範囲では概数を基本とする。小数点以下を保持するのは、その精度自体が記事の意味・比較・判断に必要な場合に限る」。通常は25.2%→about 25%、44.7%→about 45%、89.6%→about 90%のように概数化することが既定であり、閾値の前後が論点になっている場合(例: 49.5%と50.5%の僅差自体が意味を持つ場合)・年次変化や比較差を精密に扱う必要がある場合・小数を落とすと結論が変わる場合は小数を保持する。この既定はCEFRレベル(A2/B1/B2)に関わらず共通であり、レベル別の別ルールではない。同一原則の1文をWriter共通Prompt(`er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`「Spoken-first原則(数字の扱い)」C項)へも追加した。単体テスト9件(`er011_no18_evidence_compression_a_precision_21r_test_01.py`)は既存ブロックの verbatim一致・順序を引き続き確認しPASS(新規追加ブロックの挿入位置は既存ブロックの直後・禁止事項markerの直前)。**Production runtime evidence(Theme 2 B1/A2、`er011_output/preview_role_numeric_precision_wiring_01/`)**: 実際のTheme2 B1 Pre-editor Writer出力(Trial-12の実生成物、再生成せず再利用)を新Prompt下のEvidence Compression Editor(実Production関数`run_lossless_editor()`)へ1回通し、25.2%→about 25%・44.7%→about 45%・24.3%(旧: trend表現化)→about one quarterへ既定どおり概数化されることを確認した(観光庁調査由来の「約90%」「約80%」はLedger原本が既に近似値のため不変、Fact fidelityとして正しい)。A2側も同一原則で25.2%→about 25%・44.7%→about 45%・52.4%→about 52%・24.1%→about 24%(旧: 24.1%のまま未丸め)へ概数化されることを確認した。編集後テキストに対しProduction正式Ledger Deviation Checker(`hook_aware=True`)を実行し、B1=`LEDGER_COMPLIANT`(0件)、A2=`LEDGER_COMPLIANT`(MINOR 1件、`changed_number=false`、丸めとは無関係な確信度ニュアンスの指摘)を確認した(丸め自体がchanged_numberとして誤検知されないことを実データで確認)。精度保持側の判断(既存ブロックが変更されていないこと)は、Trial-20の既存fixture(`er011_output/no18_a2_evidence_compression_abc_precision_extension_trial_20/article_pattern_b_precision_01.md`、99.71/108.95が丸めずそのまま保持された実例)で確認した(新規API呼び出しは行っていない) | `DECIDED`(`PRODUCTION_WIRED`) | ER-011-NO18-A2-EVIDENCE-COMPRESSION-EXTENSION-ABC-TRIAL-18〜ABC-PRECISION-EXTENSION-TRIAL-20(検証)→ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R(ユーザー正式採用・Production配線)→ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01(レベル非依存の既定を明確化する追加ブロック、ユーザー`APPROVED_FOR_PRODUCTION`2026-09-07) | 2026-09-04、2026-09-07追記 |
| ASR診断 | **2026-08-25更新(ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01)**: 現行仕様: 英語・日本語ともPrimary ASR=OpenAI `gpt-4o-mini-transcribe`(2言語で統一)、AzureはSecondary ASR Cascade(entity-like mismatch検出時のみ、英語はPhrase List付き)として両言語で使用する。SSOTは[er006_asr_provider_routing_01.py](er006_asr_provider_routing_01.py)。決定はASR単独では下さない(Validator・Secondary ASR Cascade・Human Reviewを含む複数段階で判断する) | `DECIDED` | ER-006-AUDIO-COST-PILOT-02(英語Routing切替)、ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(日本語Routing切替) | 2026-08-25 |
| ASR一致と発音品質の関係 | ASR transcript一致(EXACT_MATCH/NORMALIZED_MATCH等)は「書き起こしテキストが正しい」ことの確認であり、「人間が聞いて自然・正確な発音である」ことの証明ではない。ASR一致=発音品質PASSと**扱わない**(ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: Key Phrase "hostile architecture"でASRは正しく書き起こしていたが、ユーザー試聴では語頭/h/が/p/様に聞こえるという実例で確認。詳細は[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-44) | `DECIDED` | ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01 | 2026-08-22 |
| hallucination対応 | strict検証+minimal instruction fallbackで自動検出・自動吸収(A02で2件実績)。**根本原因は未解明のまま** | `DECIDED`(運用方針)、原因は`UNDER_REVIEW`ではなく未解明のまま保留 | ER-003-REPRO-01-MAIN | 2026-08-08 |
| ASR homophone ambiguity対応 | strict検証が規定回数不合格でも、TTS自体が正常な可能性がある場合はretryを打ち切り、`PROVISIONALLY_ACCEPTED_REQUIRES_HUMAN_REVIEW`→ユーザー試聴後`ACCEPTED_AFTER_HUMAN_REVIEW`という2段階の人間確認フローを使う | `DECIDED`(ADD03 meaning_3で初適用・確定) | ER-003-REPRO-02-MAIN/FINAL | 2026-08-09 |
| 最終人間試聴 | 機械QA全合格でも「完成」「量産再現性合格」とは判断せず、必ずユーザー試聴を経る | `DECIDED` | 全ステージで一貫 | - |
| 量産再現性判定 | A. 量産候補として採用可能(A02・ADD03の2記事連続成功に基づく)。ただし完全自動化ではなく最終人間試聴を必須ゲートとして維持 | `DECIDED` | ER-003-REPRO-FINAL(commit `c4a762c`) | 2026-08-09 |
| Audio Validation Gate(Assembly直前の検証ゲート) | Production assembly(`er003_v1_n3_01_assemble.py::load_b1_sources`/`load_a2_sources`)は、実行直前に`verify_episode_audio_validation_gate()`で、そのrunの`tts_generation_results.json`に記録された全segment(Full Story/Point見出し・本文/Preview/Comment/In One Line/Key Phrase英日、ファイルに存在する全て)を検査する。各segmentはVALIDATED(status=OK)/HUMAN_APPROVED(ASR_VALIDATION_UNCERTAINだがcanonical_text一致の明示的承認記録あり、`record_human_approval()`で記録)/UNVALIDATED/STOPPEDへ正規化され、VALIDATED・HUMAN_APPROVED以外が1件でもあればepisode assembly全体を`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`として中止する。ファイルが存在するだけでは採用条件を満たさない(「とりあえず最後のWAVを使う」の禁止)。既存の`tts_generation_results.json`を正とし、新しいmanifestファイルは作らない(重複実装回避)。適用範囲は現行Production経路(本ファイルが読むtheme)のみ、legacy/experimental scriptは対象外。**2026-08-28修正(ER-008-N8-HUMAN-APPROVAL-AND-PROPER-NOUN-PRONUNCIATION-SPEC-16)**: `_segment_gate_status()`が、ER-011で後から追加された`status=HUMAN_REVIEW_LOCKED`を認識しておらず(実装当時は未存在のstatus値)、承認記録があってもUNVALIDATEDへ落ちてassemblyを止め続けるバグを発見・修正した。`HUMAN_REVIEW_LOCKED`を`ASR_VALIDATION_UNCERTAIN`と同じ承認確認分岐に含め、No.8で実データにより承認済み3 segmentがHUMAN_APPROVEDとして正しく通過することを確認済み | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N7-CONTENT-AUDIO-QA-02(Key Phrase限定の原型`verify_key_phrase_audio_integrity`)、ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05(全segmentへ一般化・Production配線)、ER-008-N8-HUMAN-APPROVAL-AND-PROPER-NOUN-PRONUNCIATION-SPEC-16(HUMAN_REVIEW_LOCKED対応バグ修正) | 2026-08-26(2026-08-28修正) |
| Interim directional fact precheck for user-validation phase(比較方向Fact事前チェック、暫定) | [er008_directional_fact_precheck_08.py](er008_directional_fact_precheck_08.py)の`audit_article_directional_facts()`を、`er003_v1_n3_01_articles_generate.py::run_one_pattern()`(Fact Check/Ledger Deviation Checkの直後)へ既定Trueで配線した。more/fewer、at least/at most、increase/decrease等の比較方向反転(No.7 B1 Point Twoで実際に発生、[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-71)を、rule-based(新規LLM callなし)で検知する**暫定策**。判定はMATCH/POTENTIAL_DIRECTION_REVERSAL/DIRECTION_REVIEW_REQUIRED/NOT_APPLICABLEの4分類、結果は`audit/directional_fact_precheck.json`へ記録する。article生成自体は自動でblockしない(`assert_no_directional_reversal()`という明示的なgate関数を別途用意、完成候補宣言プロセスへの組み込みは今回未実施)。**既知の限界**: 「比率」とその逆数に近い量(例: 従業員・デスク比率 対 従業員1人あたりのデスク数)のように主語が逆数関係にあるFactは、表層的な語の比較だけでは正しく判定できない(実データ検証で、誤りだった旧No.7 B1本文をMATCH、修正済みの正しい本文をWARNと判定し、正誤を区別できなかったことを確認済み)。この暫定策は**OPEN-72(構造化comparator等による本格対策)を根本解決するものではなく**、OPEN-72は`DEFERRED / AFTER USER VALIDATION`のまま維持する。既存22テーマへの横断適用は今回未実施(新規生成分のみ既定で有効)。**本チェックは補助的な警告機能であり、Fact方向の安全性を保証するものではない**(POTENTIAL_DIRECTION_REVERSALが出ないことをもって「方向誤りが無い」と結論しないこと) | `DECIDED`(`PRODUCTION_WIRED`、暫定策) | ER-008-DIRECTIONAL-FACT-PRECHECK-08(fixture 23件全PASS、No.7 B1/A2実データで実証) | 2026-08-26 |
| 日本語canonical textの外来語/制作内部ラベル検出(4分類ゲート) | No.4(pool_n4_supermarket)のA2 comment_2で、制作内部の章番号ラベル「Part 1」がリスナー向け日本語にそのまま残り("Part 1では、店が…")、TTS自体は正しく「パート1」と発話していたが、Japanese ASRが文中の英字表記をローマ字のまま書き起こすことがほぼ無いためcanonical textと恒久的に不一致になり、Human Reviewへ滞留していた(14回の試行全てで再現)。根本原因はASR/TTS側の不具合ではなく編集上の問題(制作都合の内部ラベルをリスナー向け日本語に残した)と判明したことを受け、`er003_audio_tts_asr_safety.classify_foreign_tokens_in_japanese_text()`を新設した。日本語canonical text中の英字・数字混じりのトークンを、TTS呼び出し前に(1)NEEDS_JAPANESE_PARAPHRASE(「Part 1」等の制作内部ラベル、自然な日本語へ言い換えるべき)/(2)READING_DICTIONARY(定着した略語・固有名詞、`DEFAULT_JA_READING_DICTIONARY`に登録済みなら機械的に対応可)/(3)ENGLISH_PRONUNCIATION(その記事のKey Phrase英語表現[used_form]そのもの、呼び出し側が`known_key_phrase_terms`を渡した場合のみ判定)/(4)HUMAN_REVIEW(上記いずれにも機械的な確信を持って分類できないもの)の4分類へ振り分ける(rule-based、新規LLM呼び出しなし、OPEN-72/ER-008-DIRECTIONAL-FACT-PRECHECK-08と同じ「確信が持てない場合は無理に自動判定しない」思想)。過検知でProduction全体を止めないため、TTS呼び出し自体をブロックするのはカテゴリ4(HUMAN_REVIEW)のみに限定し(既存の`detect_gloss_placeholder_notation()`と同じ設計)、カテゴリ1〜3は検出・記録のみに留めて生成は継続する。HUMAN_REVIEW判定時は既存のASR Cascade human_review_queue.jsonlと同じ思想で`er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`へ記録し、TTS呼び出し自体を行わずSTOPPEDで止める。`er003_v1_n3_01_tts_generate.py`の日本語TTS入口2箇所(B1: `generate_charon_japanese_with_reading_safety()`、A2: `generate_a2_japanese_with_reading_safety()`、後者はminimal instruction fallback経路も内包するため1箇所のチェックで両経路をカバーする)へ配線した。既存のKey Phrase日本語gloss呼び出し(B1 kp_ja_charon・A2 meaning_N)は`known_key_phrase_terms=[used_form]`を渡すよう更新済み。No.4 A2の全Japanese文言(preview/comment_1〜4/japanese_title/Key Phrase gloss5件)へ実行した結果、修正前はcomment_2の「Part 1」1件のみNEEDS_JAPANESE_PARAPHRASEとして検出され、他は0件。comment_2修正後は全segmentで検出0件を確認した。**追記(2026-09-12、ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01)**: 日本語canonical text向け読み方辞書(`DEFAULT_JA_READING_DICTIONARY`)へ、ユーザー承認によりAI/IT/EV/IoT/DX/GPS/SNS/PC/GDP/EU/NASA/AR/VR/ESG/NFTの15略語を追加登録した。Gate判定ロジック自体(`classify_foreign_tokens_in_japanese_text`/`apply_repetition_qa_gate`とは別モジュール)は無変更。既存単体テスト17件全PASS。Trend記事(`family_a_trend_ai_manufacturing_prod_run_01`)A2で本Gateにより停止していた7segmentのHUMAN_REVIEWが解消し、TTS再開・Assembly完成まで到達した(詳細は`ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01_REPORT.md`、OPEN_ITEMS.md OPEN-135行参照)。**追記(2026-09-25、NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b、`DECIDED`/`PRODUCTION_WIRED`)**: 従来、READING_DICTIONARY分類findingの確定読み(例: 「Meta」→「メタ」)はfindingとして記録されるだけで、TTS入力にもASR照合(`er007_ja_asr_validator_01.classify_ja_asr_match`)にも一切使われず、「Meta」vs「メタン」のような差がentity_likeヒューリスティックに該当しASR Cascade(最大4回の追加ASR、TTS再生成なし)の偶然一致で無条件PASSしてしまう欠落があった(Meta a2 comment_3で実際に発生・`OPEN_ITEMS.md` OPEN-177参照)。`classify_foreign_tokens_in_japanese_text()`のREADING_DICTIONARY findingへ構造化フィールド`"reading"`を追加し、`expected_readings: dict | None = None`(既定None、完全後方互換)という新規オプション引数を、`generate_charon_japanese_with_reading_safety()`/`generate_a2_japanese_with_reading_safety()`/`generate_a2_japanese_with_fallback()`(`er003_v1_n3_01_tts_generate.py`)、`generate_charon_japanese()`(`er003_v1_sing01_voice01_generate.py`、B1)、`generate_narration_snippet_verified_strict()`のja分岐のみ(`er003_v1_repro01_main_generate.py`、英語分岐は無変更)、`evaluate_attempt_ja_with_cascade()`/`_detail()`(`er007_ja_secondary_asr_01.py`、Primary#1・#2・Secondary#1・#2の全ステップへ転送)、`classify_ja_asr_match()`→`protected_check_ja()`(`er007_ja_asr_validator_01.py`)の9関数へ素通し配線した。`protected_check_ja()`内、辞書登録トークン単体のopcode差分に限り(既存の`entity_like`/`phonetic_uncertain`ヒューリスティックより先に)登録読みと直接照合し、一致すれば許容差、不一致なら`cascade_eligible=False`を強制して既存の`TRUE_CONTENT_MISMATCH`→retry(standard 2回→fallback 1回、合計上限3回)→Human Review Lockへそのまま合流させる(新Gate・新上限・新ログ経路は作らない、設計は`docs/pm/recon_reading_validation_wiring_01.md`)。unit/integration test 63件全PASS(mismatch/match/長音差/Latinそのまま/未登録語regression含む)、既存unittest discover(`*_test_01.py`)1052件全PASS(既存mockシグネチャ1件[`er011_open121_repetition_qa_production_wiring_01_test_01.py`]を`expected_readings`受け取り対応に修正)。Production初回path実runtime evidence(実API、Meta a2 comment_3実データ、`TTS_EXECUTION_MODE=STANDARD`、standard_attempts=1で1回のみTTS実行): ASRが実際に「メタ」(登録読みと完全一致)を書き起こし`PHONETIC_MATCH`でPASS、費用¥2.40(2 API call、上限¥5内)、`er012_output/reading_validation_evidence_01/runtime_evidence.json`。現行Meta a2 artifact(`er012_output/e_family_two_level_wiring_01/meta/`)自体は再生成していない(次回そのsegmentが再生成された場合のみ本チェックが適用される)。Cascadeが1回一致で無条件PASSする構造・中間ASR結果[Primary#2/Secondary#1/#2]が成果物JSONに残らない監査ギャップは本実装のスコープ外、`OPEN_ITEMS.md` OPEN-181で別途起票。 | `DECIDED`(`PRODUCTION_WIRED`) | ER-009-JA-FOREIGN-TOKEN-GATE-01(受入テスト13件全PASS[er009_ja_foreign_token_gate_01_test_01.py]、No.4実データで実証・comment_2修正後にAudio Validation Gate実PASS)、ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01(辞書15語追加、2026-09-12)、NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b(expected reading ASR照合配線、2026-09-25) | 2026-08-26 |
| 英語固有名詞ASR表記揺れの軽量音韻類似度チェック(entity phonetic corroboration) | 既存のentity_only_diffs判定(`er006_preprod_hardening_01_validation.py::classify_asr_match()`、固有名詞らしき語のみの音訳差)は、「retryを打ち切る」設計はあったが「自動PASSさせる」設計が無く、実際には正しく発話されている固有名詞(No.5 pool_n5_cafes B1 full_story_part1の"L. Mimoun and A. Gruen")がHuman Reviewへ滞留していた。全記事・全固有名詞への一律research工程は追加せず(コスト増回避)、`aggregate_entity_only_phonetic_corroboration()`を新設した: 複数の独立したTTS take(同一canonical_textに対する別々の生成)で観測されたASR書き起こし候補を集約し、pure PythonのSoundex実装(`soundex_en()`、新規外部依存なし)+文字列類似度+文字数差+語頭一致による軽量な音韻類似度チェックで、「同一固有名詞の表記揺れ」と判定できる場合のみ`ASR_VALIDATION_UNCERTAIN_PHONETIC_ACCEPTED`として自動採用する。保守的側に倒す設計: (1)数字・否定・非固有名詞内容語の差を含むtakeはそのtake単体を判断材料から除外する(全体は拒否しない)、(2)同じ誤認識が複数回**繰り返し**観測される場合(多様性の裏付けが無い)は自動PASSしない(soundexだけでは"Robert"/"Rupert"のような無関係な別の実在人名同士を区別できないため、これを緩和する設計)、(3)単発観測(裏付け無し)は複数回観測時より厳しい閾値を要求する、(4)canonical/ASR両方の語数が一致する候補のみを判定対象にする(語数不一致[例: "Neukölln"→"new Cologne"]は別の単語への丸ごと置換の疑いが強いため対象外)。`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin()`(B1 Full Story等の長尺英語News本文生成)へ配線し、entity-only mismatchの場合は既存のmax_attempts上限内でretryを継続して複数takeの証拠を集めるようにした(コスト上限は既存のまま拡張していない)。**既知の限界(正直に記録)**: soundexベースの軽量チェックは実在する別名同士の完全な区別を理論上保証しない。本チェックはretry・Human Review滞留を減らすための補助的最適化であり、既存の必須プロセス(最終的なユーザー試聴)がこの限界に対する最終的な安全網であり続ける | `DECIDED`(`PRODUCTION_WIRED`) | ER-010-ENTITY-PHONETIC-CORROBORATION-01(受入テスト22件全PASS[er010_entity_phonetic_corroboration_01_test_01.py]、No.5実データ[full_story_part1]で実証・Audio Validation Gate実PASS) | 2026-08-27 |
| 複合序数("twenty eighth"型)の正規化バグ修正 | No.5 full_story_part2の日付発話形修正("April 28, 2026,"→"April twenty eighth, 2026,")作業中に、`normalize_text()`の数値正規化パイプラインが、十の位の単語("twenty")と一の位の序数語("eighth")から成る複合序数を正しく1つの序数("28th")へ変換できず、独立した2つのcardinal/ordinal変換ステップがそれぞれ"20"と"8th"へ別々に変換してしまい、"20 8th"という無関係な2トークンへ分裂する実バグを発見した(TTSは実際には正しく"28th"と発話していたにもかかわらず、この正規化バグのせいでASR検証が常に不合格になっていた)。OPEN-58(複合基数のハイフン誤変換)と同じ教訓を踏まえ、汎用的な書き換えはせず、「十の位の単語+一の位の序数語」という閉じた具体的パターンのみを対象にした専用の変換ステップ(`_convert_compound_ordinal_words()`)を、既存のcardinal/ordinal変換より先に実行する形で追加した。スペース区切り("twenty eighth")・ハイフン区切り("twenty-eighth")の両方に対応する | `DECIDED`(`PRODUCTION_WIRED`) | ER-010-DATE-SPOKEN-FORM-POINT-FIX-01(受入テスト7件全PASS、No.5実データで実証) | 2026-08-27 |
| 重要な日付・数字のTTS入力前チェック(検討したが今回は不採用) | No.5 full_story_part2で、正しい"April 28"がTTSにより複数回にわたり"April 26"と発話される事象(ASRの表記揺れではなく、12回中一貫して"26"になる実データから、genuine TTS mispronunciationと判断)が発生した。再発防止として「桁の大きい年号+日付の組み合わせをWriter/Support生成後・TTS前に検出しHuman Review相当のフラグを立てる軽量チェック」の追加を検討したが、今回は実装を見送った。理由: (1) 発生頻度・条件(なぜこの特定の日付表現でTTSが誤読するのか)が未解明で、汎用的な検出ルールを今の時点で設計すると過検知/過剰実装(OPEN-58と同じ教訓)のリスクが高い、(2) 今回発見した個別事象(No.5のこの1箇所)はpoint fix(発話安全形への言い換え)で解決済みであり、緊急に一般化する必要性が低い。今回は個別のpoint fixのみ採用し、一般的な検出ゲートは見送ったことを明記する(必要になった時点でOPEN item化した上で改めて検討する) | `DEFERRED`(不採用、Open Item化) | ER-010-DATE-SPOKEN-FORM-POINT-FIX-01 Part D、OPEN-78 | 2026-08-27 |
| Human Review Cost Guard(Review Lock機構) | No.5(pool_n5_cafes)のB1修正作業中、Human Review Queueへ到達した(または繰り返しSTOPPEDになった)segment(full_story_part1/2)に対し、同じ生成スクリプト(`er009_pool_n5_b1_fix_01.py`)を手動で繰り返し実行してしまい、full_story_part1でTTS 18回・ASR 59回、full_story_part2でTTS 12回という異常なAPI消費が発生した。原因は(1)呼び出し側スクリプトが結果を無条件に上書きし過去の試行履歴・Human Review到達状態を引き継がない設計だったこと、(2)Human Review Queueへ到達した後もそれを検知して新規TTS/ASR呼び出しをブロックする仕組みが存在しなかったこと。`er011_human_review_lock_01.py`を新設し、segment単位のReview Lock状態(`AUTO_PROCESSING`/`HUMAN_REVIEW_REQUIRED`/`HUMAN_APPROVED`/`REGENERATE_APPROVED`/`RESOLVED`)を、narration wavパス(".../<theme>/<level>/narration/<segment>.wav")から機械的に導出したキーで管理する(呼び出し側の関数シグネチャは一切変更しない設計)。`HUMAN_REVIEW_REQUIRED`(cascadeがHuman Reviewへ回した場合、または規定回数STOPPEDで打ち切った場合)または`HUMAN_APPROVED`(既存の`record_human_approval()`と連携)の状態にあるsegmentは、明示的な`approve_regenerate()`呼び出し(`REGENERATE_APPROVED`への遷移、対話的オペレーター操作でのみ到達する経路)が無い限り、TTS/ASR呼び出しを一切行わず既存状態をそのまま返す(0 API call)。`REGENERATE_APPROVED`は次の1回の呼び出しだけで自動的に消費され(`RESOLVED`または`HUMAN_REVIEW_REQUIRED`へ遷移)、「同じスクリプトをもう一度実行しただけ」では再解除されない。台本(text)が変わった場合はSHA256ハッシュの不一致により自動的に新しいバージョンとして扱われ、過去のlockは無効になる(既存の`record_human_approval()`のtext変更時無効化と同じ設計)。累積TTS試行数(既定上限15)・累積ASR呼び出し数(既定上限60)を超えた場合、`REGENERATE_APPROVED`中でも強制的に`HUMAN_REVIEW_REQUIRED`へ固定するbudget guardを第二防衛線として持つ(第一防衛線はHUMAN_REVIEW_REQUIRED到達時点での即時ブロック)。Human Review Queue(英語`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`・日本語`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`)への重複投入も防止する(同一segment・同一canonical_textなら既存entryを再利用)。既存のtts_generation_results.json(segment単位で上書きされる正)は変更せず、別途append-onlyのattempt history(`er011_output/attempt_history.jsonl`)へ記録する。**配線箇所**: 英語側5関数(`er003_v1_sing01_voice01_generate.py::generate_charon_english`、`er003_v1_sing01_point_headings_aoede.py::generate`、`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin`、`er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict`[en/ja共通]・`generate_key_phrase_component_verified`)、日本語側は`generate_narration_snippet_verified_strict`のja分岐と`er003_v1_sing01_voice01_generate.py::generate_charon_japanese`。fallback経路を持つ合成関数(`generate_english_segment_with_fallback`・`generate_a2_japanese_with_fallback`)は、standard経路が`HUMAN_REVIEW_LOCKED`を返した場合にfallbackへ進まないよう明示的に早期returnする(fallbackは未ガードの直接TTS/ASR呼び出しのため)。**既知の適用範囲外**: A2 6% slowdown retry(`generate_a2_segment_with_slowdown`)は内側の関数が`status=OK`を返した後に別途post-process検証で取り直す既存の正当な設計のため、`RESOLVED`状態はブロック対象にしていない(ブロックすると既存の正当なretryを壊すため)。**2026-09-01修正(OPEN-105、ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19)**: `generate_key_phrase_component_verified()`(`@review_lock.guarded_generate("en")`)が内部で`generate_narration_snippet_verified_strict()`(`@review_lock.guarded_generate_with_language_arg`)を直接呼び出すネスト構造のため、同一out_pathに対しcheck_before_generation/record_outcomeが2重に実行され、実TTS試行3回がcumulative_tts_attempts=6として記録される二重会計バグを発見・修正した(`er011_output/attempt_history.jsonl`の同一timestamp2エントリで実データ確認)。fallback_budgetの算出(`standard.get("attempts_log")`を直接参照)はこのバグの影響を受けておらず、影響は永続化されるcumulative_tts_attempts/cumulative_asr_calls(累積budget guardの判定材料)のみに限定される。修正は`guarded_generate`/`guarded_generate_with_language_arg`へモジュール共有のreentrancy guard(`_ACTIVE_GUARDED_OUT_PATHS`、同一out_pathに対する外側呼び出しが進行中の場合、内側の呼び出しはcheck/recordをスキップしfnへ直接委譲する)を追加する形で行い、呼び出し側の関数シグネチャ・fallback_budget計算・他の4つのguarded_generate利用箇所(charon英語/日本語・point_headings・news_tail_fix)は無変更(重複するネスト構造を持たないため元々影響を受けていなかったことを確認済み)。回帰テスト2件追加(`test_nested_guarded_calls_do_not_double_count_attempts`・`test_nested_guarded_calls_inner_check_is_skipped_not_reevaluated`、実デコレータ2枚を重ねて再現)、既存15件(同ファイル)・crosslevel TTS cap回帰1件・No.9 Production integration回帰28件、いずれもPASSのまま。実TTS/ASR呼び出しをforced-failureへ差し替えた上で`er003_v1_repro01_main_generate.generate_key_phrase_component_verified()`本体を実際に呼び出すintegration checkでも、修正後はcumulative_tts_attempts=3(修正前は6相当)であることを実行時確認した(API課金ゼロ) | `DECIDED`(`PRODUCTION_WIRED`) | ER-011-HUMAN-REVIEW-COST-GUARD-01(受入テスト9件全PASS[er011_human_review_lock_01_test_01.py]、No.5 full_story_part1相当のシナリオを実際の本番関数で再現し0 API callを実証)、ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19(OPEN-105二重会計バグ修正) | 2026-08-27(2026-09-01修正) |
| TTS attempt音声の保全(上書きせず個別保存、診断性改善) | ユーザー正式承認(2026-09-06、`APPROVED_FOR_PRODUCTION`)。背景: `KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01`(OPEN-119)で、既存のTTS retry cascadeが同一`out_path`をattemptごとに無条件上書きする設計のため、Human Review Lockへ到達したsegmentのattempt 1〜3の音声が消失し診断を妨げたことが判明した。仕様: `er011_human_review_lock_01.py::save_tts_attempt_audio(out_path, route_label, metadata)`を新設し、各TTS attemptで`out_path`へ実際に書き込まれた音声を、上書きせず`<out_pathのnarrationディレクトリ>/attempts/<segment_id>_attempt<N>_<route_slug>.wav`+同名`.json`(ASR raw出力・分類・instruction種別・model_id・voice・`tts_execution_mode`・timestamp等)として個別保存する。`out_path`(既存の最終成果物パス)自体は一切書き込まず読み取るだけであり、最終成果物のパス・内容・Assembly挙動は無変更(sha256完全一致で確認済み)。attempt番号はsegment_id単位でattempts/配下の既存ファイルをスキャンして最大値+1を採番するグローバル単調増加方式のため、(1)Key Phrase Primary(Minimal)→Fallback(English Lock)のように同一out_pathへ複数stageが順にTTS呼び出しを行う場合でも番号が衝突せず、(2)`REGENERATE_APPROVED`による再生成でも過去のattempt音声を上書きせず番号が継続する。out_pathがReview Lockの標準的な".../<theme>/<level>/narration/<segment>.wav"命名規約に従わない場合(単体テストのダミーパス等)は、Review Lock本体と同じ安全側の判断で保存自体をスキップする。**配線箇所**: review_lockが管理する既存7 guarded関数のTTS retryループ本体8箇所——`generate_narration_snippet_verified_strict`(`er003_v1_repro01_main_generate.py`、Key Phrase Primary/Fallback両stage・Full Story/Preview/News等の標準経路・A2英語/日本語standard経路を含め共通経由)・`generate_charon_english`(`er003_v1_sing01_voice01_generate.py`)・`generate_charon_japanese`(同、standard/fallback各loop)・`generate_news_narration_wide_margin`(`er003_v1_sing01_news_tail_fix.py`)・`point_headings.generate`(`er003_v1_sing01_point_headings_aoede.py`)・`generate_english_segment_with_fallback`のfallback loop(`er003_v1_crosslevel_audio_02_common.py`)・`generate_a2_japanese_with_fallback`のfallback loop(`er003_v1_n3_01_tts_generate.py`)——のいずれも、ASR結果が確定した直後に`save_tts_attempt_audio()`を呼び、返却パスを当該`attempts_log`/`fallback_attempts_log`エントリへ`attempt_audio_path`として記録する(`record_outcome()`の既存`last_attempts_log`永続化経路経由でreview_lock台帳へも自動的に引き継がれる、`record_outcome()`自体は無変更)。容量: 1 segmentあたり最大3〜4attempt×数秒wav(小容量)、既存の出力dir構成・`*.wav`のgitignore方針と矛盾しない。保持ポリシー(採用take確定後の削除・一定期間後のcleanup)は今回未導入(全attempt音声を無期限保持する)。retry/fallback/regeneration整合: Minimal→English lock・標準2回+fallback1回・`REGENERATE_APPROVED`後の再生成・Master Audio Store経由の英語Componentのいずれでも動作することを確認済み(Master Audio Storeのcache identityは無変更)。新規単体テスト9件PASS(`er011_tts_attempt_audio_retention_wiring_01_test.py`、複数attempt個別ファイル保持・最終成果物sha256不変・review_lock記録・単一attempt・REGENERATE後の番号継続を実証)、既存回帰70件(review_lock・TTS retry・Key Phrase・disfluency fallback)PASS | `DECIDED`(`PRODUCTION_WIRED`) | ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01 | 2026-09-06 |
| 英語Key Phrase Component検証: Primary ASR逐語書き起こしprompt+非ラテン文字時のSecondary再判定Cascade(false rejection対策) | ユーザー正式承認(2026-09-06、`APPROVED_FOR_PRODUCTION`)。背景: OPEN-119(`KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01`)で、TTSは英語で正しく発話しているのに、Primary ASR(OpenAI`gpt-4o-mini-transcribe`、`language=en`)が「新常態」等の非英語文字列へ意味変換しfalse rejectする事象が確定した。`KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-TRIAL-01`で対策(b: prompt付与)がfalse rejection率57.1%→0%、対策(c: b+非ラテン文字Cascade)も0%(false accept 0件)とVALIDATEDされたことを受け、対策(c)を**英語Key Phrase Component経路(`generate_key_phrase_component_verified`)に限定して**Production配線した(本文segment・Point見出し・Preview等の他の英語ASR経路には一切展開していない)。**適用範囲の限定方法**: (1)`er006_asr_provider_routing_01.py::transcribe()`/`_transcribe_openai_mini()`へ`prompt`引数を追加(既定`None`、渡した場合のみOpenAI APIへ転送)。(2)`er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()`へ`asr_prompt`(既定`None`)・`enable_non_latin_cascade`(既定`False`)引数を追加し、`language=="en"`の場合のみ`asr_prompt`を`routing.transcribe()`へ転送する。(3)`generate_key_phrase_component_verified()`のPrimary(Minimal)・Fallback(English Lock)両呼び出しのみが、新規定数`KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT`(Trialで検証した文言をそのまま複製、canonical phrase自体は含めない)と`enable_non_latin_cascade=True`を明示的に渡す。**Cascade実装**: `er006_secondary_asr_01.py`へ`non_latin_dominance_info()`/`is_non_latin_dominant_mismatch()`(ラテン文字とCJK/かな/ハングル文字を数え、CJK比率>=`NON_LATIN_DOMINANT_THRESHOLD`=0.5[両方0ならFalse]を非ラテン文字主体と判定)を新設。`evaluate_attempt_with_cascade_detail()`へ`enable_non_latin_cascade`引数(既定`False`)を追加し、Trueかつ`cascade_enabled`かつ不合格(`verified=False`)かつASR出力が非ラテン文字主体の場合のみ、既存Secondary ASR関数(`get_full_text_via_azure_stt_with_phrase_list`)を1回呼び`classify_asr_match`で再判定する(既存の`entity_like`/`homophone_candidate`限定のCascade発動条件・数字ゲート・否定ゲート・homophone判定・Connected Speech Validatorの判定順序はいずれも無変更)。Secondaryでも不一致ならreject維持。`evaluate_attempt_with_cascade()`(3-tuple互換ラッパー)へ`detail_out`引数(既定`None`、渡すとCascade詳細[steps/`cascade_invoked`/`non_latin_cascade_invoked`]をin-placeで取得できる、戻り値のtuple形状は無変更)も追加した。**attempt保存への記録**: `save_tts_attempt_audio()`のmetadataへ`asr_prompt_applied`/`non_latin_cascade_enabled`/`non_latin_cascade_invoked`/`cascade_invoked`/`cascade_steps`(Secondary raw出力含む)を追加(英語Key Phrase Component経路以外は全てFalse/Noneのまま記録され、適用範囲限定の裏付けとなる)。**Master Audio Store cache identity**: 無変更(ASR設定は音声内容そのものに影響しないため、`MasterAudioKey`は従来通りtext/voice/model/style基準のまま)。**新規テスト**: `er006_secondary_asr_01_test.py`へ9件追加(非ラテン文字閾値境界、Cascade既定Falseで不発動、Secondary一致でPASS、Secondary不一致でreject維持、ラテン文字のみ誤表記[cashless型]では不発動、Trial陰性対照3件[「新常態」/「デフォルト」/「new formal」]のraw出力をfixture化しfalse accept 0件を確認、`detail_out`動作確認)。`er006_asr_provider_routing_01_test.py`へ2件追加(prompt既定None・明示指定時のみ転送)。新規`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`5件(適用範囲限定[本文相当のデフォルト呼び出しにpromptが渡らない・日本語分岐は無関係であること]・`generate_key_phrase_component_verified`のPrimary/Fallback両方が実際にprompt/フラグを転送していることの配線確認)。既存回帰: `er006_preprod_hardening_01_validation_test.py`57件・`er008_asr_variant_hardening_15_homophone_en_test.py`6件・`er006_secondary_asr_01_test.py`既存20件・`er011_human_review_lock_01_test_01.py`18件・`er011_tts_attempt_audio_retention_wiring_01_test.py`9件(新規kwargs追加に伴いテスト側mock signatureを更新)、いずれもPASS。`run_project_regression.py`(collected=2109、failed=3、失敗3件は本タスク以前から存在する既知の無関係failure[`er003_test_bad`の意図的self-check・`er003_test_p2j_investigate`のOPEN-77既知meta-test集計3件]であることをgit stashでの前後比較[baseline/candidateとも collected=2104/2109・failed=3で同一]により確認済み)。**Runtime evidence**(Standard同期、実API・小額): Production経路(`generate_key_phrase_component_verified`)で「new normal」「cashless」を実生成し、いずれもPrimary ASR(prompt付き)がattempt1で正しい英語書き起こしとなりPASS(Cascade不要)。陰性(既存のTrial生成済み音声、日本語TTSで「新常態」を発話)を実際のProduction Cascade関数へ直接投入し、prompt付きPrimaryでも`心状態`のまま非ラテン文字優勢のためSecondary Cascadeが実発動、Secondary(Azure)も`Xinjio Tai.`で不一致のままreject維持(false accept 0)を確認。出力先`er011_output/kp_en_asr_false_rejection_prod_wiring_01/`、player.html(file:///形式) | `DECIDED`(`PRODUCTION_WIRED`、適用範囲は英語Key Phrase Component経路限定。本文segment等の他の英語ASR経路への展開は別途ユーザー判断が必要な未決事項として`OPEN_ITEMS.md`のOPEN-119行に残す) | KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01(Trial: KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-TRIAL-01、診断: KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01) | 2026-09-06 |
| Disfluency QA(短文segmentのpartial repetition検知) | No.8 A2 Key Phrase 2("uneven choice")のTTSクリップに"uneven, uneven choice"という部分的な言い直しが実在したが、Production ASR(OpenAI/Azure)は"Uneven choice."と平滑化して書き起こし、既存Validatorをすり抜けていた(ASR smoothing問題)。無料・ローカル実行のfaster-whisper(追加API課金なし)によるword-level verbatim再文字起こしで、隣接する同一単語の完全一致repetitionのみを検知する`er008_disfluency_qa_18.py`を新設し、Key Phrase英語Component(`generate_key_phrase_component_verified`)・A2/B1 Point見出し(`generate_a2_segment_with_slowdown`経由/`point_headings.generate`)・A2/B1 In One Line(`generate_a2_segment_with_slowdown`経由/`generate_news_narration_wide_margin`)・B1 Preview(`generate_charon_english`)へ配線した(既定`disfluency_qa=False`、上記の対象segment呼び出しのみ`True`)。flag時はHuman Reviewを第一選択にせず、既存のTTS retry loop内で「verified=False」として扱い自動的にTTSを取り直す(既存の総試行回数上限3回のbudget内で消費、新規retry予算は追加していない)。上限到達後は既存のSTOPPED→`er011_human_review_lock_01`のHUMAN_REVIEW_REQUIRED自動遷移にそのまま合流する(新しいHuman Review経路は実装していない)。**既知の限界**: 「同一単語まるごとの繰り返し」のみ検知でき、B1 Previewで報告された"Wh, why does..."のような単語の一部分だけの言い直し(partial word)は、word-level ASRの性質上検知できない(2種類の独立したfaster-whisperモデル[small/tiny]で再検証したが証拠なし、OPEN-86参照)。**2026-08-29追記(ER-21、恒久修正)**: 「PRODUCTION_WIREDと報告済みなのに実際の完成版音声にdisfluencyが残る」という事故がNo.8のkp2("uneven choice")自体で再発した。根本原因は3つ: (1)`disfluency_checked`/`disfluency_evidence`がattempts_log内にしか記録されず、segment記録のtop-levelへ昇格されていなかった、(2)Assemble Gate(`verify_episode_audio_validation_gate`)がstatus=="OK"しか見ておらずdisfluency QAの証跡を一切確認していなかった、(3)Master Audio Store(`er006_master_audio_store_01.get_or_generate`)のcache hit reuseが生成時のQA証跡を運ばず最小限dictしか返さなかった。kp2_en.wav自体もdisfluency QA配線(bef70c1)より約1日前に生成された旧assetで、配線後も同じmasterがcache hit再利用され続けていた。恒久対策として3層を実装: (A)上記6箇所の生成関数すべてで`disfluency_checked`/`disfluency_evidence`をtop-levelへ昇格、(B)Assemble Gateへ`_segment_missing_mandatory_disfluency_qa(name, entry, level)`を追加し、レベル別の必須対象(B1: preview/comment_1-4/in_one_line/point_one_heading/point_two_heading、A2: in_one_line/point_one_heading/point_two_heading[preview/commentは日本語のため対象外]、Key Phrase英語は両レベル共通)についてtop-levelの`disfluency_checked is True`が無ければfail-closedでblockする(A2/B1でmandatory segmentが異なる点を実装中に発見・修正済み、レベル非依存にすると恒久的にA2 Gateが通らなくなるバグだった)、(C)Master Audio Storeのmanifestへ`qa_evidence`(sha256/asr_verified/asr_text/disfluency_checked/disfluency_evidence)を保存し、reused=True側にも復元する。加えて`_segment_asset_hash_stale()`(記録済みsha256と実ファイルの突き合わせ)をGateへ追加し、JSON記録とファイル実体が手動操作等でズレるケースも検知できるようにした。No.8実データでは、この新Gateにより過去生成された全English mandatory segment(A2/B1合計21件)が一旦block対象になったが、無料・ローカルのfaster-whisper再検査(`er008_n8_disfluency_backfill_21.py`)でkp2以外は全てクリーンと確認しbackfill(追加TTS/API課金ゼロ)、kp2のみ実際に反復ありと再確認され本番経路で再生成(disfluency flagged=false, ASR EXACT_MATCH)。修正後、Gate・完成版再Assembleとも両レベルPASSを確認(実音声確認まで完了、runtime evidence)。回帰テスト`er008_n8_qa_hardening_21_gate_test_01.py`・`er006_master_audio_store_01_test.py::test_reuse_carries_forward_qa_evidence`を追加 | `DECIDED`(`PRODUCTION_WIRED`、資産-記録紐付けまで確認済み) | ER-008-N8-QA-CONTENT-SPEED-HARDENING-18(検知ロジック開発・No.8実データで実証)→ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19(Production配線、実際のKey Phrase再生成呼び出し[No.8 kp2]でruntime evidence確認)→ER-008-N8-FINAL-QA-HARDENING-21(資産-記録紐付けの恒久修正、No.8完成版で実音声確認済み) | 2026-08-29 |
| TTS Repetition/False Start QA(OPEN-121、逐語句・文単位のまるごと反復[Point Two/In One Line型]+partial-word false start型[B1 FSP1型]の追加検知、**A2/B1英語本文segment限定**) | ユーザー正式承認(2026-09-07、`APPROVED_FOR_PRODUCTION`、範囲=**A2/B1英語本文segment[`full_story_part1`/`full_story_part2`/`point_one`/`point_two`]のProduction正式経路のみ**。Key Phrase・日本語segment・comment/preview/title/in_one_line等の他segmentは対象外)。OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-01/02(`VALIDATED`)で検証済みの3方式(方式A[n-gram句・文単位反復検知、非隣接spanをcanonical crosscheckで意図的反復と区別、min_words>=3]・方式D[対数スペクトル自己相関のself-similarity、min_lag=1.0秒・top-k類似度優先・sim閾値0.85・決定閾値run長0.12秒]・方式D'[方式Dと同一の計算primitiveを共有する派生プロファイル、lag0.5〜2.0秒・run長優先・sim閾値0.7・決定閾値run長0.6秒、B1 FSP1型のようなfalse start/aborted restartを検知])を無変更で新規[er011_open121_repetition_qa_production_01.py](er011_open121_repetition_qa_production_01.py)へ移植した。**統合スペクトル計算**: 方式D・D'は同一音声に対し独立に対数スペクトル自己相関(FFTフレーム計算)を行うと同じ計算を2回行う非効率があったため(Trial-02 §4/§7-5)、`compute_shared_self_similarity()`で類似度行列を1回だけ計算し、`analyze_profile_d_long_lag()`/`analyze_profile_d_prime_short_lag()`の2プロファイルへ再利用する設計(検知ロジック[閾値・探索アルゴリズム]自体は無変更、計算の重複のみを解消)。**配線箇所**: 新規opt-inフラグ`enable_repetition_qa`(既定`False`、既存`enable_connected_speech_equivalence_layer`[OPEN-122]と同一の設計パターン)を`er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()`(英語分岐のみ)・`er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback()`(標準・fallback両経路)・`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin()`へ追加し、既存`er008_disfluency_qa_18.apply_disfluency_gate()`と同一のANDゲート(`apply_repetition_qa_gate()`)で接続した。`er003_v1_n3_01_tts_generate.py::generate_a2_segments()`/`generate_b1_segments()`の本文4segmentループのみが明示的に`True`を渡す(既定`False`のため引数を渡さない全既存呼び出し元[Key Phrase`generate_key_phrase_component_verified()`・日本語`ja_secondary`・comment/preview/title・in_one_line等]は無変更、`inspect.getsource`によるソースコード直接確認テストで実証)。新規retry回数・新規Cost Guardは一切追加していない(方式A/D/D'はいずれもローカルCPU計算のみで追加API課金ゼロ、既存`review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`予算内でretryが自動発生し、上限到達後は既存のSTOPPED→Human Review Lock自動遷移にそのまま合流する)。**境界値monitoring**: `evaluate_repetition_qa()`はflag/非flagにかかわらず方式D/D'それぞれの最大run長・lag・similarityを常に戻り値へ含める(`repetition_qa_evidence`としてattempts_log/save_tts_attempt_audioのメタデータへ記録、後から閾値再校正できるようにする設計)。D'の陽性最小run(0.7秒)と陰性最大run(0.5秒、`a2_comment_3`)のマージン0.2秒はTrial-02較正値のまま維持。**未配線**: gap<0.5秒の即座の言い直し(Trial-01方式C-v2)は本タスクでは配線していない(OPEN_ITEMS.md OPEN-121行へ追跡項目として記録)。**Runtime evidence**: (a)既知陽性3件(Theme2 A2 Point Two/In One Line[保全済attempt]・B1 FSP1 false start[保全済])をTP3/3で検知(Point Two/In One Lineは方式A+D、B1 FSP1は方式D'のみが検知、想定通りの役割分担を実データで再確認)。(b)Trial-02陰性セットのEN代表10件をFP0/10で確認。(c)Theme2 B1`full_story_part1`(false startが実在した原本と同一canonical text)を配線後のProduction関数`generate_news_narration_wide_margin(enable_repetition_qa=True)`でStandard同期・実TTS/実ASRにより再生成し、status=OK・asr_verified=True・repetition_qa_checked=True・flagged=False(方式D'run長0.33秒、閾値0.6秒未満)を確認。既存のPASS音声・player.htmlは上書きせず新ディレクトリ`er011_output/open121_tts_repetition_qa_production_wiring_01/theme2_b1_fsp1_regen/`へ保存(episode全体の再Assemblyは今回行っていない)。cost実測¥3.64。証跡: `er011_output/open121_tts_repetition_qa_production_wiring_01/`(`known_positive_negative_result.json`・`theme2_b1_fsp1_regen/run_summary.json`)。**Regression**: `run_project_regression.py`(collected=2138、passed=2135、failed=3[本タスク以前から存在する既知の無関係failure、OPEN-122時点[collected=2112]と同一件数]、errors=0)。既存`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`(5件)・`er011_tts_attempt_audio_retention_wiring_01_test.py`(9件)は新規kwarg追加後も無変更でPASS。新規[er011_open121_repetition_qa_production_wiring_01_test_01.py](er011_open121_repetition_qa_production_wiring_01_test_01.py)26件(unittest.TestCase形式、`run_project_regression.py`のglobパターンに収集される)全PASS。**Git操作完了**(commit`e6c2f37`、main反映済み。`PRODUCTION_WIRED`確定、Fable最終受入2026-09-07、根拠`PM-LANE-A-PRODUCTION-WIRED-FINAL-ACCEPTANCE-AUDIT-01_REPORT.md`)。詳細: `OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01_REPORT.md`。**追記(2026-09-08、OPEN-127/OPEN-128 Production配線)**: 同module`_normalize_tokens()`へem dash(—)のみ空白へ置換する1行(OPEN-127、候補1a)、方式D(`analyze_profile_d_long_lag()`)へacoustic flag後の局所ASR語句一致度確認2段判定(OPEN-128、候補c、`confirm_by_local_asr_overlap()`新規、方式Aと`transcribe_verbatim()`結果を共有し二重ASR回避)を追加配線した。方式A/D/D'の既存判定ロジック・acoustic threshold(sim0.85/run0.12秒)自体は無変更。詳細は`OPEN-127-EM-DASH-TOKEN-BOUNDARY-PRODUCTION-WIRING-01_REPORT.md`・`OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01_REPORT.md`参照。**追記(2026-09-12、OPEN-121数字↔数詞同値化)**: `_normalize_tokens()`(canonical側)・`detect_ngram_repetition()`(ASR側)は、比較前に綴り小数(two〜twelve)↔算用数字の同値化を行う(判定閾値`canonical_repeat_count>=2`・方式D/D'の閾値自体は無変更、"%"/"percent"は対象外)。ユーザー`APPROVED_FOR_PRODUCTION`(2026-09-12)、実装・回帰テストPASS済みだがGate 3(Production runtimeでの実発火)未完了のため`PRODUCTION_WIRED`は未宣言。詳細は`OPEN_ITEMS.md`OPEN-121行、`OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01_REPORT.md`参照。 **追記(2026-09-13、OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01、PM-CLOSEOUT-CONSOLIDATION-104、Gate 3検証完了)**: 方式D'(false start/aborted restart型検知、lag0.5〜2.0秒・run長優先探索・決定閾値run≥0.6秒)は2026-09-07のcommit`e6c2f37`で方式A/Dと共に既にA2/B1英語本文4segment(`full_story_part1/2`・`point_one`・`point_two`)へ実装・配線済みだったことを独立検証で確認した。Trial-02テストセット56件のProduction実装での再現(TP6/6・FP0/50、報告済みFP0/39の上位集合)、既存76テストPASS(67+9)、project-wide regression(collected=2438/passed=2435/failed=3[既知無関係])、A2/B1本文4segment遡及スキャン144件(D'固有の未知false positiveは0件。新規flag6件の内訳は2件が既知バグの独立再確認・3件が既存記載の"%"/"percent"等ギャップに起因する低重要度誤検知疑い・1件はローカルASR精度低下が疑われるデータ不整合)、実機runtime evidence(¥2.71、非flag判定確認)をすべて実施し、2026-09-13ユーザー承認内容(`VALIDATED`→`APPROVED_FOR_PRODUCTION`、TP6/6・FP0/39・追加課金ゼロ・重複なし)と実挙動の一致を確認した。SSOT/Git/Dangling Reference Check(統合タスクPM-CLOSEOUT-CONSOLIDATION-104で実施)を含むGate 3全14項目の充足を確認したため、方式D'は`PRODUCTION_WIRED`(2026-09-13ユーザー承認`APPROVED_FOR_PRODUCTION`に基づく)として正式確定する。閾値・実装は無変更。詳細: `OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01_REPORT.md`。**追記(2026-09-13、OPEN-121-METHOD-C-V2-INTEGRATION-TRIAL-01)**: 方式C-v2(gap<0.5秒即時言い直し検知)を同一module(`er011_open121_repetition_qa_production_01.py`)へ試作期統合Trialとして実装した(新規opt-inフラグ`enable_method_c_v2`、既定`False`、既存4呼び出し元は本引数を一切渡さず既定OFF不変性を維持、Trial専用モジュールは非参照)。Trial-01結果(TP2/2・FP0/26)をProduction統合実装でも再現、遡及コーパス144件の近似分析で新規flag0件(既存方式の部分集合)。Production採用(`APPROVED_FOR_PRODUCTION`)は対象外・別途ユーザー判断待ち(既定OFFのため現行Productionへの影響ゼロ)。詳細: `OPEN-121-METHOD-C-V2-INTEGRATION-TRIAL-01_REPORT.md`。 | `PRODUCTION_WIRED`(commit`e6c2f37`、範囲限定[A2/B1英語本文segment]、Fable最終受入2026-09-07)。OPEN-127/OPEN-128は配線完了・Fable受入待ち(§末尾changelog参照)。数字↔数詞同値化(2026-09-12)は`APPROVED_FOR_PRODUCTION`実装済み・Gate 3進行中(未配線ではなく既存共有moduleへの内部修正のため経路自体は既存のまま、runtime evidence待ち)。方式D'は2026-09-13`PRODUCTION_WIRED`確定(Gate3全14項目充足、OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01)。**方式C-v2は2026-09-13ユーザー正式判断(PM-CLOSEOUT-CONSOLIDATION-105)によりStatus=`REJECTED_FOR_PRODUCTION`でClose**(Trial自体は`VALIDATED`のまま、原文「検証の結果、既存A+D'構成に対する追加価値が不足しているためProduction不採用」[既存方式Aに対する追加検出が実測0件、追加ASR呼び出し・latency増に見合わない]、「Trial失敗」ではない)。コードは`er011_open121_repetition_qa_production_01.py`に`enable_method_c_v2`既定OFF・opt-inのまま削除せず残し、Production呼び出し元4箇所は引き続きこの引数を渡さない(grep再確認済み) | OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-01/02(Trial・VALIDATED判定)、OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01(Production配線・Runtime evidence取得、commit`e6c2f37`で反映済み)、PM-LANE-A-PRODUCTION-WIRED-FINAL-ACCEPTANCE-AUDIT-01(Fable最終受入監査)、OPEN-127-EM-DASH-TOKEN-BOUNDARY-PRODUCTION-WIRING-01、OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01 | 2026-09-07/2026-09-08 |
| Point One/TwoとFull Storyの意味重複検知+Point-only regeneration | No.8のPoint One(A2/B1とも)がFull Story既出のロジックをほぼそのまま言い換えているだけで、「Point One/TwoはFull Storyの代替にしない」という既存原則に反していた(検知するValidatorが存在しなかった)。ローカルlexical overlap(stopword除去後の内容語のoverlap coefficient、Point基準の一方向指標)による第1段階検知(`er008_point_overlap_qa_18.py`、暫定閾値0.40、新規API呼び出しなし)を、`er003_v1_n3_01_articles_generate.py::run_one_pattern()`内(Evidence Compression後・Fact Checker前)へ配線した。flag時は記事全体を再生成せず、NGになったPoint 1件だけを、Verified Fact Ledger・確定済みFull Story・他方のPoint本文をcontextとして固定して渡すLLM呼び出し(`er008_point_regenerate_19.py::regenerate_point_only()`)で差し替える。禁止事項(Full Story論理の言い換え・新Fact追加・causal/certainty/scope drift)を明示し、再生成後はFull Story・他方のPointとの重複再チェック(いずれもNGなら最大2回retry)で合格したもののみ記事へ反映する。差し替え後のarticle_textはそのまま既存のFact Checker/Ledger Deviation Checkを通る(regenerateされたPointも既存の安全確認プロセスの対象になる)。No.8 B1実データで検証: Point One(Full Storyとのoverlap 0.481、flag)を再生成し、overlap 0.188(Full Story)・0.094(他方のPoint)まで低下、内容も「小さなコストvs大きな損失」という元のロジックから「秩序の公平性への不信」という別の心理的角度へ実際に変わったことを確認(runtime evidence)。**既知の限界**: 「本当に新しい切り口か」の意味的判定・「新Factが追加されていないか」の意味的判定は自動化しておらず(後者は内容語の出現有無による弱いヒューリスティックのみ)、Fact整合の最終確認は引き続き人間判断が必要。**2026-08-29追記(ER-20、実データで既知の限界が実際に発生)**: No.8のPoint One(A2/B1とも、閾値0.40でflag)に対しPoint-only regenerationを実行したところ、生成された新テキストに検証済みFact Ledgerに無い主張(例:「American Airlinesが順番外搭乗に罰則を導入」「United Airlinesが搭乗改善策を試験中」)が含まれ、後続のFact CheckerがREVIEW_REQUIREDと判定した(overlap自体は0.542→0.188/0.4→0.4台まで改善したが、Fact安全性が崩れた)。この結果は採用せず、Point Oneは元のテキストへ差し戻し、Fact Checker PASS・Ledger COMPLIANTを再確認した(No.8は重複flagが残ったまま出荷)。これはユーザーが指示した監視項目「新Factを追加していないか」が実際に発生した実例であり、`regenerate_point_only()`の自動検証(overlap再チェックのみ)だけでは不十分であることが実データで確認された。恒久対策(例: 再生成後に必ずFact Checkerを自動実行し、REVIEW_REQUIRED/FAILなら自動的に元テキストへ差し戻す)は今回実装しておらず、`MONITORING`(実ユーザー検証中の監視対象)として維持する。**2026-08-29追記(ER-21、PRODUCTION_WIRED撤回)**: ユーザー判断により、Point-only regeneration(`regenerate_point_only()`)自体をProduction自動経路から外した。`er003_v1_n3_01_articles_generate.py::POINT_ONLY_REGENERATION_ENABLED = False`(既定)により、`run_point_overlap_qa_and_regenerate()`はoverlap検知(monitoring)のみ行い、flag時も本文を一切書き換えず`NG_REVIEW_REQUIRED`として記録するだけになった(regenerate_point_only()自体は呼び出されない、回帰テストで無効化中はLLM呼び出しが0件であることを確認済み[`er008_n3_01_point_qa_wiring_19_test_01.py`])。overlap検知(lexical overlap、閾値0.40)自体は`MONITORING`として引き続き稼働する。暫定Production方式として「記事全体Writerを再実行、overlap再QA、NGなら最大2回retry、それでもNGならNG/REVIEW_REQUIRED」が提案されているが、Writer実測コスト(No.8実測: writer_a2単独で約$1.50)を踏まえるとoverlap NG発生率次第でコストが数倍化する可能性があり、実装前にユーザー承認が必要と判断し、今回はwiringまで到達していない(OPEN-88参照)。**2026-08-29追記(ER-22、Writer full retry正式実装)**: ユーザーが正式暫定仕様として決定し、`run_one_pattern()`内に`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`のretryループを実装した。overlapがflagされた場合、Pointだけを差し替えず記事全体をWriterから再生成し(`_generate_and_compress_article()`ヘルパーへ共通化、Writer→Evidence Compression→Point overlap再チェックの3工程のみ再実行)、最大2回retryしても解消しなければ`status="NG_REVIEW_REQUIRED"`を返しFact Checker/Ledger Deviation/Directional Precheckは実行しない(TTS前完結・追加TTS/ASR費用なし・不要なFact Checker呼び出しも防止)。mock LLMによる単体テスト(`er008_n8_point_overlap_article_retry_22_test_01.py`)で、retry成功パス(2回目のWriter呼び出しでoverlap解消・article.mdへ保存)と、maxretry後のNG_REVIEW_REQUIREDパス(Fact Checker/Ledger Deviation呼び出し0回)の両方を確認済み。ただし実LLM呼び出しによるend-to-end runtime evidenceは未取得(No.8自体は既存の承認済み記事内容を保持するため、この記事に対して実際にWriterを再実行してはいない、OPEN-88参照)。**2026-08-29追記(ER-23、実runtime evidence取得・PRODUCTION_WIRED昇格)**: `er008_n8_point_overlap_writer_retry_realapi_23.py`により、実OpenAI Writer API・No.8 A2の実プロンプト・実Verified Fact Ledgerを使ったend-to-end検証を実施した。初回(fixture記事、無償)でoverlap NGと判定→retry 1回で実Writerが記事全体を再生成→Point overlap QA(決定的なlexical overlap判定、LLM不使用)がoverlap解消を確認→設計通り実Fact Checker・実Ledger Deviation Checkが1回だけ呼ばれる、という流れを実データで確認し、Point-only regenerationが呼ばれないことも確認した(実測コスト$0.7861/retry1回、内訳: Writer再生成約$0.11・Fact Checker約$0.4753・Ledger Deviation約$0.2033)。OPEN-88はCLOSEし、Writer full retry機構を`PRODUCTION_WIRED`へ昇格する。**2026-08-29追記(ER-25、No.8のPoint overlap記録整理)**: No.8はWriter full retry機構(ER-22〜23)の導入前に生成された記事であり、現行閾値0.40を適用するとB1 Point One(ER-19時点実測overlap 0.481)が超過している。No.8はこの状態のままユーザーが最終試聴し、内容を正式承認したが、この承認は現行Production経路が要求する`Point overlap gate PASS`(overlap<0.40への収束)とは扱わず、**No.8限定のHuman Approved exception**として正式記録する: "No.8 was generated before the current Point overlap production rule. B1 Point One exceeds the current 0.40 threshold, but the user completed final listening review and explicitly approved No.8 as a one-off Human Approved exception. This exception must not be used for future production articles." 今後の記事生成ではこの例外を自動適用せず、現行Production(閾値0.40・強化済みWriter prompt・Writer全体retry最大2回・それでもNGならNG_REVIEW_REQUIRED)をそのまま適用する。**2026-08-31追記(ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14、Diagnostic Full Retry正式採用)**: Writer full retry に加え、Diagnostic Full Retry 機構を正式採用した。Point overlap >= 0.40 でflag時、単純な記事全体再生成ではなく、診断情報（前回記事、overlap score、shared words、簡易分類）を prompt に組み込んで再生成する。診断情報生成は機械的（LLM不要、overlap_qa.flag_possible_paraphrase()が返した shared_words から keyword-bucket classify: _EVIDENCE_WORDS / _IMPLICATION_WORDS / _CAUSE_WORDS、fallback: generic semantic restatement）で追加費用ゼロ。ただしWriter全文Retryには Luna API call コストが発生（実測: Retry1 ¥0.44、Retry2 ¥0.38、合計¥0.82/Household theme、input各3430トークン + output 1422/1142トークン実測）。またLedger Deviation checkが最終candidateに対して実施される（実測¥0.55、input 1402 + output 2521トークン）。Diagnostic Retry 1回の追加費用合計 ≈ ¥0.99（Writer Retry1 ¥0.44 + Ledger check ¥0.55）。Diagnostic Retry 2回まで使った場合 ≈ ¥1.37（Writer Retry1+2 ¥0.82 + Ledger check ¥0.55）。Diagnostic section は Evidence Pack/VFL 固定で全文再生成を指示。流れ: Writer(初回) → Evidence Compression → Point overlap check(>= 0.40?) → Diagnostic section build → Diagnostic prompt → Writer(retry 1-2) → overlap check → if still flagged & retry < 2: loop else: NG_REVIEW_REQUIRED。A/B試験: Point Role Planning (0/3 PASS) vs Diagnostic Full Retry (3/3 PASS)。No.9 A2 A2 runtime 実装検証: Point overlap < 0.40 を確認。実装験証: diagnostic_mod import・build_diagnostic_retry_prompt関数・retry loop への Diagnostic comment をコード確認。3 themes Regression test: Hanshin/Health は Ledger データ不足により Writer が記事生成不可（Diagnostic Retry 非関連の既存問題）。Household で実発火確認（Point One overlap 0.414 で flag、diagnostic_used = true、Retry prompt に診断情報組み込み実行）。Ledger MAJOR = 0 達成（原文 "growing frustration" を "strong consumer resistance" へ修正、MINOR 0 確認）。**2026-08-31追記(ER-010-N1-WRITER-PRINCIPLES-STATUS-AUDIT-03、記録訂正)**: このテキスト置換は実際のNo.9本番記事(`er006_output/pool_pilot_01/pool_n9_tip_screens/{a2,b1b}/article.md`)には適用されておらず(該当フレーズは一切出現しない)、無関係な独立診断script・別theme_idのDiagnostic Full Retry検証用テスト記事に対する変更だったと判明した。No.9自体が`LEDGER_COMPLIANT`であるという結論は実際の`ledger_deviation.json`(A2: 0件、B1: MINOR 2件、本置換とは無関係)により別途確認済みで変更しないが、「本番記事へこの修正を適用してMINOR 0を達成した」という記述は誤りとして訂正する。**2026-08-31追記(ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10、Status維持の正式再確認)**: ユーザーが本ラウンドで明示的に、Diagnostic Full Retryを`PRODUCTION_WIRED`のまま維持することを再決定した。今回のNo.9新候補生成でもA2/B1ともPoint Overlapが初回でPASS(retry 0/2)したため、この機構自体は発火しなかったが、「今回発火しなかった」ことを理由に保留・未配線扱いへは戻さない(仕様採用・Production配線・Trial実績・fail-closed設計はいずれも変更なしで維持)。 Production 配線完全・実runtime 発火確認・Retry上限2維持・Point-only regeneration非使用・Luna model routing確認済み | `PRODUCTION_WIRED`（実装完全・runtime 発火確認・acceptance criteria 全達成）。**2026-09-09追記(OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01、G1回帰修正)**: `build_diagnostic_section()`(`er009_diagnostic_full_retry_modules_12.py`)が前回Point One/Two本文をハードコードされたプレースホルダー文字列のままWriterへ渡していた実装漏れ(module化時の配線漏れ、`FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05`のReconciliation Checkで発見)を、本節が元々承認していた設計(検証済みscript`er009_n1_diagnostic_full_retry_production_12.py`が実際に渡していた前回Point本文)へ復元した。`previous_point_one_text`/`previous_point_two_text`引数を追加し、唯一のProduction呼び出し元`build_diagnostic_retry_prompt()`が既に抽出済みの本文を渡すよう修正(閾値・Loop Budget・retry判定ロジックは無変更)。Runtime evidence(Production正式初回path`run_writer_for_theme`、mode指定なし、Hanshin Ledger)でB1B/A2ともDiagnostic Full Retry実発火・診断promptに実本文を確認(¥24.14)。commit `8596f34`。**2026-09-09追記(PM-CLOSEOUT-CONSOLIDATION-34、Fable最終受入)**: Fableが本G1修正を承認済み挙動(ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14)への回帰修正として正式受入した。状態: `PRODUCTION_WIRED`(確定、候補ではない)。Point Overlap問題自体は未解決のまま(`OPEN_ITEMS.md`OPEN-134行の観測Exit条件へ継続統合)。詳細は`OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01_REPORT.md`参照 | ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-WIRING-13 → ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14 → OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01 | 2026-08-31(2026-09-09 G1修正) |
| Point One対Point Twoのlexical overlap検査(追加ペア) | 従来の`run_point_overlap_qa_and_regenerate()`はPoint One/TwoそれぞれとFull Storyとのoverlapしか検査せず、Point One対Point Two自体は一度も評価していなかった。No.18のように、Full Storyとは重複していなくても互いに同じ内容のPoint同士は検知できない構造的な穴だった。ユーザーが正式決定し、同一の`overlap_qa.flag_possible_paraphrase()`(閾値0.40、新規関数は作らない)をPoint One⇔Point Two間にも双方向で追加適用した。既存のFull Story対Point One/Twoチェックと同じ`still_flagged`判定・同じDiagnostic Full Retryループへ統合する、という決定自体は`DECIDED`だが、**この`still_flagged`統合(cross_point_overlapをretry判定へ含めること)は現時点で未実装・`DEFERRED`と訂正する(2026-09-09、A-UDR-21、OPEN-133)**。FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05のGate 4静的diff監査で、`run_one_pattern()`の`lexical_flagged`が`cross_point_overlap`を含んでいないこと(=承認済み設計と実装の不一致)が確認された。実装するかどうかの判断は別途行う(実装は今回行わない) | `DECIDED`(統合方針)/`DEFERRED`(cross_point_overlapのstill_flagged統合の実装、OPEN-133) | ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01 | 2026-09-02(2026-09-09 A-UDR-21で訂正) |
| Point Role Planning + Point Value QA(新しい価値の要求) | No.18 A2のPoint Two(「特定の対象・条件での傾向であり、全員には当てはまらない」「医療的な依存症を診断するものではない」)は、既存のPoint Overlap QA(lexical overlap)をPASSしたが、内容は一般的な留保のみで構成されており、聞き手への新しい理解・示唆を何も加えていなかった。原因は、既存のPoint Balance prompt(`COMMON_BLOCK_TEMPLATE`)が「Pointが何を書いてよいか」は列挙する一方、「留保・免責事項だけでPoint枠を構成してはいけない」「新しい価値を加えなければならない」を一度も明示しておらず、既存QAも語彙的な重複だけを見て意味的な「新しい価値」の有無を判定していなかったこと。ユーザーが正式決定し、2段構成の一般仕様を追加した: **(1) Point Role Planning**(新規モジュール`er011_point_role_value_planning_01.py::run_point_role_planning()`) — Full Article Writer呼び出しの直前に、Verified Fact Ledgerに基づいてPoint One/Twoそれぞれの`role`/`new_listener_takeaway`/`evidence_anchor`/`why_it_matters`/`must_not_overlap_with_full_story`/`must_not_overlap_with_other_point`を明示的に計画させる小さな独立JSON呼び出し。結果を`build_role_planning_block()`でWriter promptへ挿入する(初回生成・Diagnostic Full Retryの各attemptで毎回再計画する、前回の計画を使い回さない)。**(2) Point Value QA**(`run_point_value_qa()`) — 生成後、実際のPoint本文に対し独立したLLM呼び出しで6項目(`qa_not_caveat_only`/`qa_not_full_story_paraphrase`/`qa_not_other_point_paraphrase`/`qa_explains_why_it_matters`/`qa_specific_not_generic`/`qa_adds_new_value`)を判定する。1件でもFAILなら`status="NG"`とし、既存のPoint Overlap QAのlexical flag(`lexical_flagged`)とOR条件で`still_flagged`を構成し、同一のDiagnostic Full Retryループ(`POINT_OVERLAP_ARTICLE_RETRY_MAX`=2、既存の値をそのまま再利用)へ統合する。retry時は`point_planning.build_value_qa_diagnostic_note()`が生成した診断メモを、既存のlexical overlap診断section(`diagnostic_mod.build_diagnostic_section()`、無変更)の直後に追加する。`COMMON_BLOCK_TEMPLATE`本体にも「Pointが実際に新しい価値を持つこと」節を追加し、禁止事項(留保のみ構成・Full Story言い換え・他方のPoint言い換え・「だから何なのか」不在・一般論・新価値なし)を明記した。**Production初回runtime確認(No.18 specfix_v2実データ)**: B1Bの初回候補でPoint Value QAが実際にNGを検出した(Point Oneが`qa_not_full_story_paraphrase`/`qa_adds_new_value`でFAIL、lexical overlapは0.379で旧閾値0.40未満のためPASSしていたはずの内容)。Diagnostic Full Retry(Point Role Planning再計画込み)が発火し、retry 1回でPoint Value QA・lexical overlapとも解消した。これは、旧仕様(lexical overlapのみ)では見逃されていたはずの実例を新QAが実際に捕捉した最初のruntime証拠である。A2は初回からPoint Value QA PASS、lexical overlap(Point Two対Full Story=0.629)のみでflagされ、同様にDiagnostic Full Retryで1回で解消した | `DECIDED`(`PRODUCTION_WIRED`、No.18 specfix_v2実データでB1B初回NG検出→retry解消の実runtime証拠を確認) | ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01 | 2026-09-02 |
| Comment内部ラベル漏れの二重防御 | No.8 B1 Comment 2に"In Part 2, ..."という制作内部の構造ラベルがリスナー向け英語canonical textへそのまま残っていた事故を受け、(A)発生源除去: Comment生成のcontext文字列・role prompt(`COMMENT_1_ROLE`〜`COMMENT_4_ROLE`、A2/B1双方の該当ファイル)から"Part 1/Part 2/Full Story Part 1/2"等を除去し、「前半/後半」等の非構造的表現へ変更、出力への制約文を明示的に追加。(B)第二の防御線: `er003_audio_tts_asr_safety.detect_internal_production_labels_in_english_text()`を新設し(数字・ローマ数字・英単語序数[One〜Five/First〜Fifth]を伴う"Part/Point/Comment/Section/Step/Chapter"を検出、rule-based・追加API呼び出しなし)、`generate_charon_english()`(A2/B1共通のCharon英語生成関数)のTTS呼び出し前に配線した。検出時はTTS自体を呼ばずSTOPPED(Human Review待ち)として扱う。No.8実データでComment 2(A2)を再生成し、新Validatorで`findings: []`(検出0件)を確認、"in part because"等の自然文は誤検知しないことをテストで確認済み。**2026-08-29訂正(ER-20)**: 前回(ER-19)の報告は「A2/B1とも再生成・検出0件を確認」としていたが、これは誤りだった。実際にはB1側のcanonical text(`b1_support_texts.json`のcomment_2)に"In Part 2, what is American Airlines doing to manage this behavior?"という内部ラベルが**修正されないまま残っていた**。ER-20でNo.8完成版のComment 1-4話し方変更に伴いcomment_2を実際に再生成した際、新Validatorがこれを正しく検出・STOPPEDでブロックしたことで発覚した(Validator自体は設計通り正しく機能していた、漏れていたのは「実際のテキスト修正の反映」の方)。"In the second half, what is American Airlines doing to manage this behavior?"へ言い換え(A2 comment_2修正時の"物語の前半では"と同じ、内部ラベルを一般的な時系列表現へ置き換えるだけの最小修正)、再生成してASR verified=true・disfluency flagged=falseを確認、No.8完成版へ反映した | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N8-QA-CONTENT-SPEED-HARDENING-18(Prompt修正・Validator新設・A2実データで再生成・実証)→ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19(regression再確認の上PRODUCTION_WIRED昇格、ただしB1側の実反映漏れは未発見のまま)→ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20(B1側の未修正を発見・修正・No.8完成版へ反映) | 2026-08-29 |
| A2 6% slowdown 必須post-process invariant gate | No.8 A2 point_one_headingが、Human Review Lock経由で承認された結果、6% time-stretchという必須post-processを一度も受けないままVALIDATED扱いでAssembleへ到達していた事故を受けた恒久対策。横断調査の結果、A2の他のmandatory post-process(silence trim・Assembly時のloudness/gain正規化)は、どの経路を通っても必ず実行される設計(trimは各TTS生成関数の内部処理・gainはAssembly時に全segment一律適用)であるため同種の抜け道は無く、抜け道が存在したのは「TTS成功後に別途実行される6% slowdown」という設計上唯一の条件付きpost-processだけと判明した(大規模なArchitecture変更は不要と判断)。`er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`に、A2レベルのみ`A2_SLOWDOWN_TARGET_SEGMENTS`の各segmentについて`tts_generation_results.json`の`slowdown_applied`フィールド(第一evidence)、無ければ`{name}_original.wav`の現存(第二evidence、既存の「resume」系scriptがslowdown_appliedを記録し損ねていた既存データとの後方互換用)のいずれかを要求する invariant チェックを追加した。どちらも無ければAssembleをEPISODE_BLOCKED_BY_AUDIO_VALIDATIONとしてblockする(Human Review経路・REGENERATE_APPROVED再挑戦経路を含め、経路によらず一律適用、bypassは設けない)。No.8のpoint_one_heading相当ケース(status=OKだがslowdown_appliedもoriginal.wavも無い)をfixtureで再現しblockされることを確認、かつNo.8の実データ(過去の「resume」経由segmentがoriginal.wavのみ持つケース含む)ではPASSすることを確認 | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19(横断調査・invariant gate新設・No.8実データ双方[fixture再現/実データPASS]で実証) | 2026-08-29 |
| Key Phrase日本語glossの括弧書き禁止 | No.8 A2のKey Phrase 1 gloss「搭乗前に列に並ぶ人（俗称）」のような括弧書き補足は、音声のみで読み上げられるgloss(ja_gloss/japanese_gloss)としては不自然で、音声にすると意味の理解を助けない(同一Key Phraseに対するB1側のgloss「ゲート前で早く並ぶ乗客を指す俗称」は既に自然文だった、OPEN-85)。発生源はKey Phrase選定段階(`er003_key_words_research10.py`が読み込むP2選定prompt、L/P/U全戦略共通)の`ja_gloss`指示で、`er003_key_words_canonicalization.py`はglossを素通しするだけと判明した。3つのprompt template(`er003_v1_translator_briefs/b2_key_words_research10_{l,p,u}_prompt_template.txt`)へ「ja_glossは音声のみで読み上げられる、括弧書きの補足は避け、読み上げただけで意味が成立する自然な一文にする」指示を追加し、A2/B1で共通適用されるようにした。機械的Validatorも新設: `validate_research10_selection()`へ全角/半角括弧検知(`_JA_GLOSS_PARENTHETICAL_RE`)を追加し、生成結果に括弧が含まれる場合は既存の構造検証失敗経路(自動retry)へ合流する(新規API呼び出しは追加していない、既存validatorの拡張のみ)。No.8のA2 Key Phrase 1 glossを「ゲート前で早く並ぶ乗客を指す俗称」(B1と表現統一)へ手動修正し、本番経路(`generate_a2_japanese_with_reading_safety`)で再TTS・ASR再検証(verified=true)を確認 | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N8-FINAL-QA-HARDENING-21(発生源特定・Prompt修正・Validator新設[回帰テスト`er003_test_key_words_research10.py`]・No.8実データで再生成・実証、OPEN-85 CLOSE) | 2026-08-29 |
| Human Review Lock: STOPPED状態への承認確認漏れ修正 | `er003_v1_n3_01_assemble.py::_segment_gate_status()`が、`record_human_approval()`による人間承認確認を`ASR_VALIDATION_UNCERTAIN`/`HUMAN_REVIEW_LOCKED`の2状態にしか適用しておらず、3回retry終端の`STOPPED`状態(ER-011のHuman Review Lockが最も高頻度で到達する終端状態)は常に無条件でblockされ続ける実バグを、No.9のStandard同期TTS実行(B1 full_story_part1[ASR_VALIDATION_UNCERTAIN]、B1/A2 point_two・A2 full_story_part1[いずれもSTOPPED、実際のASR文字起こしを記事本文と照合し「78%」表記等の記法差にすぎないと確認済み]がHuman Review Lockへ到達)で発見した。`_segment_gate_status()`の承認確認対象へ`STOPPED`を追加(承認が無ければ従来通り`STOPPED`のままblock、承認記録があり`canonical_text_sha256`が一致する場合のみ`HUMAN_APPROVED`)。既存のAudio Validation Gate回帰テスト(`er008_audio_validation_gate_05_test.py`10件、`er008_a2_slowdown_invariant_19_test_01.py`等)は全PASSのまま(未承認STOPPEDは引き続きblockされることを確認)。あわせて、A2 full_story_part1/point_twoは標準ペース生成自体がSTOPPEDしたため6% slowdown post-processが未適用だった状態(`slowdown_applied`未記録)を、承認済みtakeへ`apply_a2_slowdown_postprocess()`を適用して正しく解消した(point_twoはpost-slowdown ASR再検証もPASS、full_story_part1はpost-slowdown後も同種の記法差でASR再検証はUNCERTAINだが、既存の承認[canonical_text一致]がそのまま有効なため`slowdown_applied=True`の記録と合わせてGateを通過) | `PRODUCTION_WIRED` | ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02(Audio段階、No.9実データで発見・修正) | 2026-08-30 |
| Key Phrase日本語glossの括弧書き禁止(本番経路への再配線、ER-008-N8-FINAL-QA-HARDENING-21の記載修正) | ER-008-N8-FINAL-QA-HARDENING-21は「A2/B1で共通適用されるようにした」「OPEN-85 CLOSE」と記録していたが、No.9で同じ括弧書きgloss(A2「回帰不連続デザイン（分析手法）」・B1「回帰不連続デザイン（研究手法）」)が再発したため調査した結果、この記載は誤りだったと判明した。実際に修正されたのは`er003_key_words_research10.py::validate_research10_selection()`(P2G研究比較専用、テスト・旧preflight系からのみ呼ばれる)のみで、現行A2/B1本番経路(`er003_v1_a2_kp_select_generate.py`/`er003_b1_p2_keywords.py`→`er003_key_words_production.py::validate_production_selection()`)が実際に共有利用する`er003_key_words_min_unit.py::validate_min_unit_selection()`には一度も括弧検知が実装されていなかった(ja_glossの生成元はKey Phrase選定段階の`ja_gloss`フィールドで、後続のcanonicalization工程は素通しするのみと確認)。本番共有validatorへ括弧検知(`_JA_GLOSS_PARENTHETICAL_RE`、全角/半角括弧とも検知)を追加し、あわせて本番selection prompt template(`b2_key_words_production_l_prompt_template.txt`)にも同種の禁止指示文を追加した(research10のprompt文言と同じ趣旨、ただし本番prompt既存の「研究」等の語を含む既存テストと衝突しないよう例示語を調整) | `PRODUCTION_WIRED` | ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03(No.9実データで再発を発見・本番経路の欠落を特定・修正、回帰テスト3件追加[`er003_test_key_words_min_unit.py`]、`run_project_regression.py`1957件収集1953件PASS[既知の無関係な4件失敗のみ、新規失敗無し]) | 2026-08-30 |
| Key Phrase日本語glossの自然さ(Human Review基準) | 診断(`KEYPHRASE-JA-GLOSS-NATURALNESS-DIAGNOSTIC-01_REPORT.md`)で、Human Review/最終試聴の正式基準(本節)には、訳語の自然さ・学習者にとっての分かりやすさを判定基準として明文化した箇所が存在しないことが確認された(ASR一致・発音品質・固有名詞発音の扱いが中心で、gloss訳語自体の自然さは対象外だった)。ユーザーが2026-09-06に`APPROVED_FOR_PRODUCTION`と正式決定し、Human Review基準へ以下の1項目を追加する: 「日本語glossが、自然で平易かつ学習者が直感的に理解できる表現か。意味が正しくても、不自然な直訳・過度に硬い表現・一般的でない訳語ならReview対象。」機械的Validator・blacklistは新設しない(引き続き人間の主観判断による基準であり、上記「日本語グロスに数字を含める場合は…」等の決定的Validatorとは異なる)。選定Prompt側の自然さ基準(前述「Key Phrase日本語glossの自然さ基準(選定Prompt)」行)と対になる、量産時の最終防波堤としての明文化 | `DECIDED`(`PRODUCTION_WIRED`) | KEYPHRASE-JA-GLOSS-NATURALNESS-DIAGNOSTIC-01(診断)→KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01(ユーザー正式採用・SSOT配線) | 2026-09-06 |
| TTS retry: 10分cool-down + Local Rewrite + Natural English QA(Human Review Lock手前の回復経路)+ Connected Speech 5-role適用範囲 | ユーザー正式承認(2026-09-26、`APPROVED_FOR_PRODUCTION`)。仕様: (1)既存のTTS初回/retry(`PRODUCTION_MAX_TTS_ATTEMPTS`=3、attempt1即時→attempt2即時→attempt3の直前のみ固定600秒cool-down[実sleep])で3回とも不合格の場合、Human Review Lock到達前に、問題span周辺のみをLuna(`gpt-5.6-luna`)でLocal Rewrite(意味保持/role保持/Fact非矛盾/前後文脈/Natural English/局所性/非全文の7 Gate、うちNatural English GateはTTSが通ることと英語として自然であることを独立に判定する専用Gate)し、全Gate PASSの候補のみ再TTS(1回、cool-downなし)する。再TTSがASR PASSなら`RESOLVED_BY_LOCAL_REWRITE`としてstatus="OK"のまま確定し(Human Review Lockへは進まない)、失敗時のみ従来通りHUMAN_REVIEW_REQUIREDへ進む。(2)Connected Speech(OPEN-122 Equivalence Layer)適用範囲は、Full Story(本文、Point本文含む)/Comment/Preview/Topic intro/In One Lineの5 roleのみに適用し、Heading readout(Point見出し)・Key Phraseには適用しない。role→適用判定は単一のSSOT関数`er020_tts_retry_local_rewrite_01.connected_speech_enabled_for(segment_id)`に集約し、各Production呼び出し元(`er003_v1_n3_01_tts_generate.py`)はこれを参照する(経路ごとの個別ハードコード条件式は書かない)。cool-down/Local Rewrite回復も同じ判定でゲートする。実装は`er020_tts_retry_local_rewrite_01.py`(Production module)、配線先は`er003_v1_sing01_voice01_generate.generate_charon_english`(Comment/Preview/Topic intro)・`er003_v1_sing01_news_tail_fix.generate_news_narration_wide_margin`(Full Story/In One Line)の2関数(B1経路)。**修正1回目(2026-09-26、Fable差し戻し対応)でA2経路も同水準へ配線した**: `er003_v1_crosslevel_audio_02_common.generate_english_segment_with_fallback`のfallback(minimal instruction)経路(標準2回+fallback1回=総予算3回の実質最終attempt)へ、同じ`er020_tts_retry_local_rewrite_01.maybe_cooldown_before_attempt()`/`run_local_rewrite_recovery()`(複製実装ではなく同一module関数)を配線した。あわせて、A2 topic_intro呼び出し(`er003_v1_n3_01_tts_generate.py::generate_a2_segments`)が`enable_connected_speech_equivalence_layer`引数自体を渡していなかった漏れ(role差による非適用)も修正し、`connected_speech_enabled_for("topic_intro")`を参照するようにした。**既知の構造的事実(Gapではなく、B1/A2の記事構成自体の違い)**: A2のPreview/Comment(1-4)は英語ナレーションとして存在せず(`generate_a2_japanese_with_reading_safety`経由の日本語音声)、この2 roleはA2側にはそもそも適用対象が無い。A2で実際に英語として存在し適用されるのはFull Story(Point本文含む)/Topic intro/In One Lineの3 role。runtime evidence(`er020_output/tts_local_rewrite_production_wiring_01/a2/`)でcool-down実測(600.004秒)・Local Rewrite候補生成/QA(Luna)・再TTS・ASR再検証まで実際に発火することを確認した(結果は`HUMAN_REVIEW_LOCKED_RETTS_FAILED`到達1件・追加trialでも同終端。Local Rewrite自体の起動・Luna呼び出し・状態遷移は正しく動作、詳細はREPORT参照)。 | `PRODUCTION_WIRED`(2026-09-26、Fable Gate判定、B1・A2両経路。**ユーザー確定(2026-09-26、`PM-USER-DECISIONS-SSOT-CONSOLIDATION-02`)**: Fable判定`PRODUCTION_WIRED`にユーザー異議なし、確定) | TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01(Trial系譜: TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01/TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02) | 2026-09-26 |

## Audio Production Pipeline(ER-006、Pool/N3 Production基盤)

ER-006の一連のタスク(AUDIO-COST-OPTIMIZATION-01→AUDIO-COST-PILOT-02→
PRONUNCIATION-LEDGER-SECONDARY-ASR-01→AUDIO-RETRY-CASCADE-PROD-01→
VALIDATOR-NUMERIC-COST-RECONCILE-01)で決定・実装したAudio生成
パイプラインの実装アーキテクチャを、本節でProduction標準として正式化
する。**番組の聞こえ方・言語仕様(voice/style/spoken text/TTS model)は
一切変更しない**(実装方式のみの変更、Cross-level仕様節の内容と矛盾
しない)。本節はDrift Prevention(将来のcommitが気づかず古い実装へ
後退しないようにする)を主目的とし、実装状況を機械的に確認する
Static Audit: [er006_audio_cost_spec_fix_01_static_audit.py](er006_audio_cost_spec_fix_01_static_audit.py)。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| Article→Audio Production SSOT(No.9 lineage修復で明文化) | No.9のような`erXXX_n1_production_integration_01.py`型のTheme別Production driverでは、**Writer StageとAudio Stageは単一の共有ディレクトリ(`OUT_DIR`)を介して直結する**設計であり、両者の間に別途promotion/copy工程は存在しない(存在しないこと自体は仕様の欠陥ではない)。`run_writer_stage_baseline()`(`er006_pool_pilot_01_writer.run_writer_for_theme()`経由で`gen.run_one_pattern()`を`OUT_DIR/{a2,b1b}/`へ直接書き込む)→`run_support_stage_baseline()`(`OUT_DIR/{a2,b1b}/article.md`を都度読み直しparts.json/Support/Key Phrasesを再導出)→`run_audio_stage()`(同じ`OUT_DIR`のparts.json等を読む)という一直線のpipelineが、そのまま「正式final article確定→正式Production保存先→Audio input」のSSOTである。**`er010_no9_*.py`等の診断/実験用driver scriptは、意図的に別の隔離された`out_dir`(例: `er010_output/no9_.../`)へ出力する設計であり、これらは正式`OUT_DIR`を一切書き換えない**。診断で確認した改善(prompt変更・Formatting仕様追加等、コード自体への変更を除く)を正式candidateへ反映したい場合は、**手動コピーやpromotion専用関数を使わず、Writer/Support Stageの該当関数を正式`OUT_DIR`に対して直接再実行する**(ER-010-NO9-ARTICLE-AUDIO-PRODUCTION-WIRING-14で、No.9 A2/B1Bについてこの手順を実施し、article.md↔parts.json[Audio実入力]の正規化hashが全section一致することを確認済み) | `DECIDED` | ER-010-NO9-ARTICLE-AUDIO-PRODUCTION-WIRING-14(OPEN-101 Root Cause特定・解消) | 2026-09-01 |
| Gemini TTS実装方式(Batch API) | **Batch API(`client.batches.create()`)をProduction標準として採用・実配線済み**。新設[er006_batch_tts_wiring_01.py](er006_batch_tts_wiring_01.py)(既存の`tts_call_fn(prompt) -> bytes`という呼び出し形状を保つdrop-in factory、`make_batch_tts_call_fn(model, voice)`)を、Production TTS生成6箇所(下記「Production TTS/ASR call site一覧」参照)すべてへ配線した(`er003_v1_crosslevel_audio_02_common.py`は自身でcall_fnを構築せず`repro01`の配線済み関数を再利用するため直接変更なしで対象に含まれる)。1 Batch job = 1 itemの設計(Batch料金割引はitem数に関わらずper-request適用されるためコスト効果は完全に得られる。複数item一括投入用のAPI`submit_batch_multi`/`wait_for_batch_multi`は将来の最適化余地として同モジュール内に用意したが未使用)。voice/style instruction/Structured Separation/spoken text/pacingは無変更、ASR-first Retry Cascade・Validator・Master Audio Storeも無変更(TTS呼び出しの中身だけをStandardからBatchへ差し替え)。**実API最小確認済み**(2026-08-22、代表segment2件[英語Key Phrase"opt out"・日本語gloss「参加・適用を断る」]、既存の承認済み本番文言を再利用、専用出力先へ書き込み既存完成音声には非接触): 実際のProduction call site経由でBatch job計5件が全てSUCCEEDED、既存のtrim/hallucination検知/ASR検証(OpenAI Primary英語・Azure日本語)を通過して最終的に両segmentともstatus=OK。実測コスト削減率50.02%(Batch実費$0.003376 vs Standard換算$0.006755、詳細は`er006_output/tts_batch_wiring_01_smoke/cost_comparison.json`)。**運用上の注意点(新たに判明)**: 1 Batch jobの完了待ちは実測91〜167秒/件で、Standard(通常数秒)より大幅に遅い。ASR不一致でretryが発生するsegmentでは、retry回数分この待ち時間が積み重なる(実測: 英語segmentが4回attemptで522秒)。総生成コストは下がるが総生成時間は増える可能性があるため、量産運用時は監視すること。**注記(2026-09-06、PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01)**: Batch APIは正式リリース後の実量産における正式TTS方式。正式リリース前(DEV/Trial/診断/Production正式経路を使ったruntime確認/完成候補生成/回帰等)はStandard同期を既定とする(PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01、2026-09-06、正本は`docs/pm/PM_GOVERNANCE.md` 7節)。Standard同期使用はProduction正式経路であることを否定しない。**実行モード切替(2026-09-06、ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01、`PRODUCTION_WIRED`)**: 上記のBatch/Standard切替は、`make_batch_tts_call_fn()`内の環境変数`TTS_EXECUTION_MODE`(値`BATCH`/`STANDARD`、大文字小文字非依存、既定`BATCH`、それ以外の値は静かにBATCHへ落とさずValueErrorで即停止)による1箇所の分岐で行う(monkeypatch不要、Production call site6箇所・voice・style instruction・retry cascade・Validator・Master Audio Storeは無変更)。`STANDARD`時は`er003_b1_p7a_audio.make_tts_call_fn_for_model(model, voice)`(無ければ`er002_gemini_client.make_tts_call_fn`)を返す。選択されたモードは`tts_execution_mode`フィールドとして記録する(Batch経路は`er006_batch_tts_wiring_01.py::_record()`、Standard経路[TTSのみ、text呼び出しは対象外]は`er005_cost_logger.py::_patch_gemini()`、いずれも既存キーは変更しない追加)。Master Audio Storeのcache identityにはモードを含めない(同一canonical text・voice・trim policyであれば同一modelのため音声品質は同等、既存資産の再利用を維持する設計判断)。実API確認済み(2026-09-06、Key Phrase英語"opt out"、専用出力先`er011_output/tts_execution_mode_switch_wiring_01/`): `STANDARD`は実際に`client.models.generate_content`を2attempt(3.185秒・2.727秒)呼び出しstatus=OK・ASR検証PASS・ログに`tts_execution_mode=STANDARD`を記録、既定(未設定)は実際に`client.batches.create`を4attempt(80〜156秒/件、既存の91〜167秒レンジと整合)呼び出しログに`tts_execution_mode=BATCH`を記録(この回のASR内容検証は非決定性によりSTOPPEDだったが、これは配線とは無関係な既知のTTS/ASR run-to-run変動であり、Batch経路自体が実際に実行されたことは確認済み) | `DECIDED` / `WIRED` | ER-006-AUDIO-COST-OPTIMIZATION-01(50%オフ完走確認)、ER-006-AUDIO-COST-SPEC-FIX-01(方針の正式化)、ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01(Production実配線・実API確認)、ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01(環境変数切替の配線・実API確認) | 2026-08-22 |
| Batch Failure Handling | Batch job単位の成功(`state.endswith("SUCCEEDED")`)を個別item(segment)の成功と同一視しない。`er006_batch_tts_wiring_01.py`が、応答内item(現状1 job=1 itemのためitem 0のみ)ごとにsuccess/API error/empty result/invalid audio/missing responseの5分類で判定し、success以外は例外を送出する(fail-closed、Standardへの暗黙fallbackなし)。既存の技術的retry機構(`common._call_tts_with_retry`)が、失敗時に新しいBatch jobを再投入する形で「失敗したitemのみのretry」を実現している(job全体の無条件再投入ではなく、失敗した1 itemがそのまま次のjobの唯一のitemになる設計) | `DECIDED` / `WIRED` | ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01 | 2026-08-22 |
| Master Audio Store | 固定/完全一致で再利用可能な音声(Welcome/Outro等の共通ナレーション、Key Phrase英語Component等)は、[er006_master_audio_store_01.py](er006_master_audio_store_01.py)経由で生成・再利用する。Keyは言語・レベル(nullable)・speaker voice・TTS model・style instruction hash/version・instruction path・canonical text hash(sha256)・processing version・sample rate/channelsの組で構成し、条件が一致しない音声を誤って再利用しない。B1/A2ともsegment生成の最上流(`generate_b1_segments()`/`generate_a2_segments()`)で`ensure_all_shared_narration_b1()`/`ensure_all_shared_narration_a2()`を呼び、Storeのlookupを経由しない無条件の毎回TTS再生成をしない | `DECIDED` | ER-006-AUDIO-COST-PILOT-02(最小実装・配線) | 2026-08-22 |
| Primary ASR Routing | **2026-08-25更新**: 英語・日本語ともOpenAI `gpt-4o-mini-transcribe`(Primary)。言語別構成のSSOTは[er006_asr_provider_routing_01.py](er006_asr_provider_routing_01.py)(`ASR_ROUTING`/`require_asr_route()`/`transcribe()`)であり、Production leaf pathはこのSSOT経由で呼び出す(未登録言語はfail-closedで例外送出、暗黙のAzureへのfallbackは禁止)。**旧`er006_model_routing_contract_01.py`の`ASR_PROVIDER`定数(`"azure"`固定)は、実際のASR呼び出し経路からは参照されておらず、本Routing SSOTが正である**(Model Routing Contract節を参照) | `DECIDED` | ER-006-AUDIO-COST-PILOT-02(英語Primary切替、実測: STOPPED 7→3件、attempt数110→79、Audio実費¥306→¥199/pair)、ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(日本語Primary切替、実測cost-82%・latency-70%projection、n=14実音声品質確認) | 2026-08-25 |
| Validator(数値正規化含む一般化仕様) | [er006_preprod_hardening_01_validation.py](er006_preprod_hardening_01_validation.py)の`classify_asr_match()`/`normalize_text()`/`normalize_numeric()`を、全Production Audio QAの標準Validatorとして固定する。安全に吸収してよい表記ゆれ: street/St.等のUSPS通り種別略語(canonical側テキストを基準に判定、Saint固有名詞との曖昧性はcanonical-anchored設計で解消)、綴り数字↔算用数字(cardinal)、桁区切りカンマ、小数点、パーセント記号、通貨記号、序数(third以降。first/secondは副詞用法との曖昧性のため対象外)、日付文脈直後の序数接尾辞のみ、規則的な単数形/複数形の語尾差(result/results等、閉じた語尾パターン[-s/-es]のみ、無関係語の誤同一視を避けるため長さ・語尾形状を厳格に限定)。**数式表記の正規化**(2026-08-24、ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01で追加、本タスクで正式採用): Markdown italic変数表記(`*b*`)、`=`/`is equal to`/`was equal to`↔"equals"、`<`↔"less than"、`>`↔"greater than"、`×`・数字に挟まれた`x`↔"times"、Unicode上付き指数(`10⁻¹⁶`)・ASCIIキャレット指数(`10^-16`)↔話し言葉("N to the minus/negative M(th)?")。指数はxexpx(正)/xexpnegxマーカーで底・符号・桁を保持したまま区別し、Unicode上付き文字は`strip_diacritics()`のNFKD分解で情報が失われる前(`normalize_text()`の先頭)で処理する。**絶対にPASSさせてはならない差**(regression test固定): 数値が異なる(2≠3等)、時刻表記artifact(three≠3:00)、序数と基数の取り違え(28≠28th)、通貨/パーセント記号の欠落(5≠$5、5≠5%)、年の違い(2023≠2024)、否定の有無の違い、指数の符号・桁違い(10⁻¹⁶≠10⁻⁶、10⁻¹⁶≠10¹⁶)、小数値違い(0.90≠0.09)、係数違い(2×10⁻¹⁶≠2×10⁻¹⁵)、無関係な複数形の誤同一視(cats≠dogs)。記事個別のwhitelist(固有名詞の1対1ハードコード等)は使わない。Regression fixture: [er006_preprod_hardening_01_validation_test.py](er006_preprod_hardening_01_validation_test.py)(POSITIVE/AMBIGUOUS/NEGATIVE、計55件[既存32件+数式・複数形23件]、2026-08-24時点で全PASS確認済み)。**英語厳密同音の数字ゲート例外**(2026-09-06、ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02/03で`PRODUCTION_WIRED`、ユーザー承認判断3・Approach2): `normalize_numeric()`/`normalize_text()`へ`convert_cardinals: bool = True`引数を追加(既定は従来通り、既存呼び出しは無変更)。`classify_asr_match()`の数字保護ゲートで、唯一の不合格理由がalignment-safe(cardinal変換によるtoken数変化なし)な1対1の数字語置換であり、かつcardinal変換前の生語同士がCMU Pronouncing DictionaryのARPAbet完全一致(`er008_asr_variant_hardening_15_homophone_en.homophone_arpabet_equivalent()`を再利用、新辞書追加なし)の場合のみ、新分類`HOMOPHONE_MATCH_NUMBER_EXCEPTION`(`should_pass=True`、`VALID_CLASSIFICATIONS`に追加)としてPASSする(近似音・別発音はPASSしない)。`evaluate_attempt()`経由の初回・retry・fallback全経路へ呼び出し側コード変更なしで自動配線される。緩いローカル判定(Approach1)はTrial-17で構造的に不健全と実証済みのため不採用。 | `DECIDED`(`PRODUCTION_WIRED`) | ER-006-AUDIO-COST-PILOT-02(street/St.方針転換)、ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01(数値正規化の一般化、序数バグ修正)、ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01(数式表記・複数形正規化の実装)、ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01(正式採用)、ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02/03(HOMOPHONE_MATCH_NUMBER_EXCEPTION追加・Production配線) | 2026-09-06 |
| Validator(日本語) | **2026-08-25新設、同日ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01で拡張**: [er007_ja_asr_validator_01.py](er007_ja_asr_validator_01.py)の`classify_ja_asr_match()`を、日本語Production Audio QAの標準Validatorとして採用(旧「文頭prefix一致+文字数チェック」方式を置き換え)。文字単位の全文sequence diff(`difflib.SequenceMatcher`)を取り、opcode単位で数字/否定マーカー/固有名詞らしさ(カタカナ列・英字acronym、`entity_like`)/濁点・半濁点の有無だけが異なる読みゆれ(`phonetic_uncertain`、清音化[NFD正規化+結合文字除去]による比較、「頃」のkakasi読み判定限界[goro/koro]対応)/読み完全一致(pykakasi、diff span前後4文字を文脈として付加してから比較)を個別判定する。5分類: EXACT_MATCH/NORMALIZED_MATCH/PHONETIC_MATCH(読み完全一致)/ASR_VALIDATION_UNCERTAIN(`entity_like`または`phonetic_uncertain`のみの差、Cascade対象)/TRUE_CONTENT_MISMATCH。**安全性**: `phonetic_uncertain`はCascade対象への分類のみに影響し、`should_pass`を直接Trueにはしない(誤PASSは構造的に発生しない)。**既知の残存限界**: (1)孤立漢字の異読み分岐のうち清音/濁音の関係にない異読み(例: 「後」のあと/のち)は依然未解消、(2)清音化後に偶然一致する意味の異なる実在語ペア(例: 柿/鍵)はCascadeへ余分に回りうる(誤PASSはしない、コスト増のみ)。**助数詞「つ」数字正規化**(2026-08-26、ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07で追加): 助数詞「つ」の直前に来る単独漢数字(一〜九)だけを算用数字へ揃える`normalize_kanji_counter_numerals_ja()`(`er003_audio_tts_asr_safety.py`)を`normalize_ja()`へ組み込んだ(例:"二つ"↔"2つ"を同値とする)。「二十」「二回」等、助数詞「つ」が続かない漢数字は対象外のまま(一般化しない、既存の数字保護は弱めない)。canonical textをASR表記に合わせて書き換えるのではなく、Validator側の同値正規化で吸収する方針を優先する(No.7 A2 comment_4で実証: canonical「二つ」・ASR「2つ」が`NORMALIZED_MATCH`でPASS)。**助数詞リストへの一般化(縮小版)**(2026-09-06、ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02/03で`PRODUCTION_WIRED`、ユーザー承認判断2): `_KANJI_COUNTER_RE`の対象助数詞を「つ」限定から、閉じたリスト(つ/泊/回/件/年/時間/か月/週/歳)の直前の単独漢数字(一〜九)へ拡張した。**「日」「人」は意図的に除外**する(「三日坊主」のような不規則読みの慣用句が「3日坊主」へ変換されるとkakasiが数字を音声化せず全文ひらがなASRとの読み一致フォールバックが壊れる実regressionが確認されたため。「人」も「一人/二人」の不規則読みで同型のリスクを持つため予防的に除外)。この関数は`normalize_ja()`(全文Validator)と`er003_audio_tts_asr_safety.validate_japanese_short_segment_match()`(短seg Validator)の共有部品のため、両経路へ自動配線される。Regression fixture: [er007_ja_asr_validator_01_test.py](er007_ja_asr_validator_01_test.py)(30件+voicingメカニズム一般性確認7項目、全PASS)、[er003_test_audio_tts_asr_safety.py](er003_test_audio_tts_asr_safety.py)の`JapaneseShortSegmentPhoneticMatchTests`(短いsegment用、同じ正規化を適用) | `DECIDED`(`PRODUCTION_WIRED`) | ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01、ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01(濁点/半濁点許容の追加)、ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07(助数詞数字正規化の追加)、ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02/03(助数詞リストの一般化・縮小版・Production配線) | 2026-09-06 |
| Pronunciation Ledger | 固有名詞の発音情報(Perplexity調査結果)を[er006_pronunciation_ledger_01.py](er006_pronunciation_ledger_01.py)でsurface+entity_typeをキーにcacheする。cache hitの場合は再調査(Perplexity再クエリ)を行わない。Perplexityへのクエリは、機械的に「1トピック1リクエスト」へまとめてはならない(個別/少数クエリのほうが品質が高いことを実測で確認済み、まとめるとconfidence low・hint空欄になる劣化を確認)。**Production配線範囲の明確化**: 現在Productionへ配線されているのは、Ledgerから取得した発音候補をSecondary ASRのPhrase List(`ledger_phrases`)へ渡す経路のみ(下記TTS Pronunciation Hintは未配線、次項参照) | `DECIDED(ASR側配線)` | ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01、ER-006-AUDIO-RETRY-CASCADE-PROD-01(Production 6箇所への配線) | 2026-08-22 |
| TTS Pronunciation Hint | [er006_pronunciation_tts_injection_01.py](er006_pronunciation_tts_injection_01.py)の`augment_style_prefix_with_pronunciation()`(発音ヒントをmeta/style instructionへ注入、読み上げ対象のspoken text本文自体は一切変更しない設計)は、Production基盤として保持する。個別語のphonetic respelling/whitelistは基本方式にしない。**ただし現時点でProduction 6箇所のTTS生成呼び出しには未配線**(A/Bテスト用script`er006_pronunciation_ab_01_run.py`でのみ使用実績あり)。理由: 最難関ケース"Ottoni"でのA/B検証(ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01)で、TTS発音ヒント注入の確実な改善効果を実証できなかった(mixed/負の結果)ため、Production TTS生成への強制配線は見送っている。基盤としては維持しつつ、配線判断は追加検証待ちの状態を正直に記録する(→[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-47) | `DECIDED(基盤として保持)` / `NOT_WIRED(TTS生成側)` | ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01(A/B検証、mixed/負の結果) | 2026-08-22 |
| ASR-first Retry Policy(固有名詞ASR不確実性、英語) | 固有名詞のASR不一致が疑われる場合、**TTSを即座に再生成しない**。以下の順序でASR側の再検証を先に尽くす: ①OpenAI Primary ASR #1 → ②Primary #2(必要時) → ③Azure Secondary ASR + Phrase List #1(entity-like mismatch検出時のみ) → ④Secondary #2(必要時) → ⑤それでも未解決ならHuman Review行き。実装は[er006_secondary_asr_01.py](er006_secondary_asr_01.py)の`evaluate_attempt_with_cascade()`(`CASCADE_CONFIG`: max_primary_attempts=2, max_secondary_attempts=2)。「Primary ASR FAIL→即Gemini TTS再生成」という旧経路への後退を禁止する。**`FEATURE_FLAG_SECONDARY_ASR_ENABLED`は2026-08-24付でProduction既定`True`(ON)** (ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01。旧OFF状態はOPEN-48で「追加検証待ち」としていたが、実No.6 Sweeny audio 2件[B1/A2]でCascadeが正しく起動しTTS再生成0件でHuman Reviewへ到達することを実音声で確認、既存Ottoni/Boavida系mock fixtureおよび数値/true content mismatch fixtureで真の内容誤りが誤PASSされないことも確認した上で有効化)。Production call site 6箇所は全て`cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED`という形で呼び出し時にモジュール定数を参照するため、この1箇所のフラグ変更のみで全call siteへ反映される | `DECIDED` / `WIRED(ON)` | ER-006-AUDIO-RETRY-CASCADE-PROD-01(Production 6箇所へ配線、3 Topic実測でtrue content誤PASS 0件、new savings+¥128.4)、ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01(feature flag ON化) | 2026-08-24 |
| ASR-first Retry Policy(固有名詞ASR不確実性、日本語) | **2026-08-25新設**: 英語と同じ思想を日本語へ適用。固有名詞・略語らしき語のみのASR不一致(entity-like)が疑われる場合、TTSを即座に再生成せず①OpenAI Primary ASR #1 → ②Primary #2(必要時) → ③Azure Secondary ASR #1(entity-like mismatch検出時のみ) → ④Secondary #2(必要時) → ⑤それでも未解決ならHuman Review行きの順で再検証する。実装は[er007_ja_secondary_asr_01.py](er007_ja_secondary_asr_01.py)の`evaluate_attempt_ja_with_cascade()`(`CASCADE_CONFIG_JA`: max_primary_attempts=2, max_secondary_attempts=2)。`FEATURE_FLAG_JA_PRIMARY_OPENAI`はProduction既定`True`(ON、Cascade自体も有効)。Production call site 3箇所(`er003_v1_repro01_main_generate.py`のJapanese分岐、`er003_v1_sing01_voice01_generate.py`、`er003_v1_n3_01_tts_generate.py`)は全て`cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI`という形でモジュール定数を参照する。実音声smoke test([verify_ja_cascade_production_on.py](verify_ja_cascade_production_on.py))でProduction call siteと同一の呼び出し方によりOpenAI Primaryが実際に呼ばれ分類が破綻しないことを確認済み。**2026-08-25追記(ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01)**: Cascadeが`stop_retrying=True`(Cascadeを尽くしても未解決)を返した後、`er003_v1_sing01_voice01_generate.py`・`er003_v1_n3_01_tts_generate.py`の自前retry loopがこれを無視してTTS再生成を続けるbugを修正した(`er003_v1_repro01_main_generate.py`は元々正しく短絡していた)。修正後はmock test([er007_ja_tts_retry_path_fix_test_01.py](er007_ja_tts_retry_path_fix_test_01.py))でTTS生成回数が1回で打ち切られることを確認済み | `DECIDED` / `WIRED(ON)` | ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01、ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01(stop_retrying無視bug修正) | 2026-08-25 |
| TTS Retry条件(絞り込み) | TTS音声の再生成(regenerate)は、以下に該当する場合のみ行う: 真の内容誤り(true content mismatch)、数値/年/日付の意味的な違い、否定の有無の違い、重要語の欠落・追加、TTS技術的失敗(hallucination・INVALID_ARGUMENT等)、Human Reviewで実際の音声誤りと確認された場合。**固有名詞のASR表記ゆれのみを理由とした繰り返しTTS再生成は行わない**(上記ASR-first Retry Policyでのre-verificationを先に尽くす) | `DECIDED` | ER-006-AUDIO-RETRY-CASCADE-PROD-01 | 2026-08-22 |
| English ASR Semantic Equivalence Layer(OPEN-186、数値/通貨/%/年/時刻/分数/ローマ数字/略語のTier1値等価+規則的複数形・固有名詞のTier3 corroboration救済) | ユーザー正式承認(`APPROVED_FOR_PRODUCTION`、2026-09-27)。`er006_preprod_hardening_01_validation.py::classify_asr_match()`ラッパー冒頭に、role gating(5role: Full Story/Comment/Preview/Topic intro/In One Line、Key Phrase/Heading非適用、判定はer020`resolve_narrative_role()`を再利用)付きTier1 early-exit(`NUMERIC_EQUIVALENCE_MATCH`)を追加。Tier3(規則的複数形・固有名詞のみの1トークン差、Secondary ASR corroboration必須)は`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail()`のConnected Speech Equivalence Layer後段に配線(`SECONDARY_ASR_CORROBORATED_MATCH`、warning付き)。**適用箇所(B1/A2の英語本文segment生成、初回attempt・fallback・post-slowdown再検証・Local Rewrite回復の全経路)**: `voice01.generate_charon_english()`/`news_tail_fix.generate_news_narration_wide_margin()`(B1 Full Story part1/2/3・Point・In One Line)/`crosslevel_audio_02_common.generate_english_segment_with_fallback()`(A2標準経路+`_run_a2_minimal_fallback_attempt()`fallback経路)/`repro01.generate_narration_snippet_verified_strict()`/`er003_v1_n3_01_tts_generate.py::apply_a2_slowdown_postprocess()`。既知Gapなし(legacy単発resume script[`er008_n8_a2_resume_01.py`/`er008_n8_b1_resume_01.py`]のみ対象外、実際の(再)生成は上記配線済み経路を経由)。Runtime evidence: B1実probe5/5救済(初回4件+Full Story 1件)+対照1件非救済、A2実probe2件救済(fallback予算0でもattempt1でPASS)、実測合計¥4.21(初回¥2.72+修正1回目¥0.97+修正2回目¥0.52、詳細は各節)。詳細`EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01_REPORT.md`。**Fable Gate 3判定(2026-09-27)**: `APPROVED_FOR_PRODUCTION / WIRING COMPLETE(runtime)`。全経路配線・retry/fallback整合・test PASS・runtime evidence取得済みだが、Phase B(規則的複数形・固有名詞corroboration)のlive発火telemetryは未観測(mock検証+Meta run_01での偶発的発火1件のみ)のため、`PRODUCTION_WIRED`の最終判定はPhase B live telemetry取得後とする(取得予定: Family X音声化Stage 3)。**追記(2026-09-28、`EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02`、Phase 2実装、ユーザー承認`APPROVED_FOR_PRODUCTION`)**: Phase A Tier1の判定方式を「セグメント全体atom数完全一致(all-or-nothing)」から、既存の完全一致判定をまず試み、一致しない場合のみ`difflib.SequenceMatcher(autojunk=False)`による**diff-anchored比較**へ進む方式へ変更した(`tier1_numeric_equivalence()`内部実装のみ、シグネチャ・呼び出し側は無変更)。非equalな各opは**strict版Tier1合成規則**(差分atomはliteralのみ/両側の英数字内容が`re.sub(r"[^a-z0-9]","",…)`で完全一致/op数上限`_TIER1_MAX_ABSORBED_PUNCT_OPS=3`・atom比率上限`_TIER1_MAX_ABSORBED_PUNCT_ATOM_RATIO=0.2`)の閉じた基準を1つでも満たさなければ即座に全体非等価(best-effort禁止)。これにより打点略語(U.S.↔US)・meridiem略記(a.m.↔am)・hyphenated numeric/alphanumeric entity(15-minute↔15 minute、COVID-19↔COVID 19)等、無関係な1箇所のpunctuation差が同一segment内の他の正しい数値等価判定を道連れにする構造的脆弱性を解消した。あわせて分類A技術修正: 月名文脈限定の裸digit序数接尾辞吸収(`_MONTHS`/`_DATE_ORDINAL_RE`をer021側へ移設しer006が参照、複製ではなく共通化)、序数語(third等、`_ORDINAL_WORDS`も同様に共通化)の認識(基数atomとはordinalフラグで区別、負例"28 vs 28th"は保護維持)、"per cent"(2語表記)対応、数値語runが前後の"and"を飲み込むparser bug修正、単独ローマ数字"V"/"X"の締める方向の安全化(閉じたラベル語[Act/Part/Chapter/Section/Phase/Version等]直後限定、"Model X"↔"Model 10"のような衝突を防止)。新しい意味等価カテゴリの追加ではなく、既存Phase Aスコープ内の実装是正+アルゴリズム変更(false acceptの境界は拡張していない)。`'s`由来の単独"s"の無視処理は引き続きDEFERRED。詳細: `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT.md`Phase 2節、`docs/pm/design_en_asr_orthographic_equivalence_coverage_02.md`。**修正1回目(2026-09-28、Opus L3 BLOCKER-1反映)**: `_closed_punctuation_diff_ok()`へ句読点atom必須条件+句読点atom除外後atom数minが1以下の条件を追加し、分かち書き差・アポストロフィ差単独の吸収を防止。`'s`由来の単独`s`無視処理は引き続きDEFERRED(未実装)。Tier1 early-exitへdiff_anchored=True時限定の否定語二重防御を追加。既存の比較アルゴリズム[diff-anchored]自体は無変更だが、atom化ロジックは分類A修正の範囲で変更されている(ローマ数字安全化により従来PASSしていた一部組合せが安全側で非等価になる副作用を含む)。insert/delete[片側空]は不吸収のまま・op上限3件のままであり、句読点欠落全般への「構造的耐性」という表現は過大(実務上のカバレッジは限定的)。**重要な注記**: "not able"/"notable"等はTier1層では正しく非等価(false accept 0)判定だが、実配線経路の最終should_passは既存baseline側の独立した`despaced()`正規化(本修正の変更範囲外)により別途PASSする場合がある(従来からの既存挙動、本修正が新たに開けた穴ではない)。検証: 新規/既存33件+既存29件計62 unittest全PASS、telemetry汚染隔離(母数4,977不変)、project-wide regression collected=3506 failed=9 errors=2(全件本タスク無関係と個別確認済み)。commit`7af9b22f`。Fable Gate 3判定: `PRODUCTION_WIRED`(2026-09-28、スコープ: strict版Tier1合成規則[句読点atom必須+片側結合1語条件+否定語二重防御]と分類A技術修正。`'s`はDEFERRED)。 | `APPROVED_FOR_PRODUCTION`(Phase A実装是正+strict版Tier1合成規則を実装完了。`PRODUCTION_WIRED`はPhase B live telemetry取得後+本Phase 2のOpus L3診断・Fable Gate 3判定後) | EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01(Trial・VALIDATED)、EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(Production配線、commit`014bb9e5`/`81530e4e`/`b5a132e1`)、EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(strict版Tier1合成規則Phase 2実装、修正1回目Opus L3 BLOCKER-1反映、commit`7af9b22f`) | 2026-09-28 |
| Human Review Route | Cascadeを尽くしても未解決の固有名詞/ASR不確実性ケースは、API呼び出しを重ねてSTOPPEDにし続けるのではなく、Human Review queueへ送る。Queueは最低限以下を保持する: canonical text、audio、発音メタデータ(Pronunciation Ledgerのhint)、Primary ASR transcripts、Secondary ASR transcripts、判定理由(classification/reason)。ログ実装: `HUMAN_REVIEW_LOG_PATH`(`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`)。ユーザー提示形式は`docs/pm/PM_GOVERNANCE.md` 9-12節に従う(2026-09-17) | `DECIDED` | ER-006-AUDIO-RETRY-CASCADE-PROD-01 | 2026-08-22 |
| Production TTS/ASR call site一覧 | `er003_v1_crosslevel_audio_02_common.py`、`er003_v1_repro01_main_generate.py`(2箇所)、`er003_v1_sing01_news_tail_fix.py`、`er003_v1_sing01_point_headings_aoede.py`、`er003_v1_sing01_voice01_generate.py`、`er003_v1_n3_01_tts_generate.py`の計6ファイルが、本節のASR Routing/Validator/Pronunciation Ledger(ASR側)/ASR-first Retry Policyを実際に配線しているProduction leaf pathである。Legacy/experimental script(A/Bテスト用`er006_batch_ab_01_generate.py`・`er006_pronunciation_ab_01_run.py`等)はProduction scope外であり、上記経路とは区別する。**2026-08-25更新**: このうち日本語分岐を持つ`er003_v1_repro01_main_generate.py`(`generate_narration_snippet_verified_strict`のJapanese分岐)、`er003_v1_sing01_voice01_generate.py`(`generate_charon_japanese`)、`er003_v1_n3_01_tts_generate.py`(`generate_a2_japanese_with_fallback`)の3ファイルへ、日本語Validator+Cascade(`er007_ja_asr_validator_01.py`/`er007_ja_secondary_asr_01.py`)を配線した(ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01) | `DECIDED`(範囲の明確化) | ER-006-AUDIO-COST-SPEC-FIX-01(Static Audit対象範囲の確定)、ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(日本語3箇所への配線) | 2026-08-25 |
| Fact Checker retry cap | `er002_ja_web_research_r3.py::run_fact_checker_with_gates()`(`MAX_FACT_CHECK_ATTEMPTS=2`)は、初回呼び出し+技術的失敗(Web検索が1回も使われなかった、またはJSON解析/スキーマ不適合)時のみ最大1回の技術再試行を行う設計であり、**verdict(PASS/REVIEW_REQUIRED/FAIL)を理由に再試行することは無い**(パースに成功した時点でverdictの値に関わらず即座に結果を返す)。「PASSが出るまで自動的に再試行する」経路はコード上存在しない。Ledger Deviation Check(`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`)も同様にretryロジック自体が無く、記事ごとに1回だけ呼ばれる。ユーザーが提案した基本方針「初回+retry最大2回、その後STOP」よりも現行実装(初回+技術的失敗時最大1回)の方が厳格であるため、追加のcap実装は不要と判断した。regression test(`er008_n8_fact_check_retry_cap_25_test.py`)で、PASS/REVIEW_REQUIRED/FAILいずれのverdictでも呼び出しが1回で確定すること、技術的失敗時のretryが引き続き上限内に収まることを固定した | `DECIDED`(追加実装不要、既存実装のまま安全と確認) | ER-008-N8-CLOSEOUT-GOVERNANCE-25 | 2026-08-29 |
| Production全体 retry/regenerate/polling上限の横断監査 | TTS生成(標準+fallback、A2/B1・英語/日本語全経路)、ASR Cascade(Primary/Secondary)、Writer技術的retry、Point overlap記事全体retry、Evidence Compression、Research/Verification/Ledger Deviation、Assembly前のAudio Validation Gate、Human Review Lock、Gemini Batch jobポーリング、および全`while True`/`while not`を横断監査した。**結論: 上限が全く無い経路は0件**(全て数値cap・壁時計timeout・単発呼び出し・線形固定長シーケンスのいずれかで有界)。Assembly Audio Validation Gateは異常時に例外を送出して完全停止する設計(自動retryなし)で、これは意図通りの安全設計と確認した。Human Review Lockは明示的な人間の承認(`approve_regenerate()`)なしに自動再処理されない設計であることも確認した。**監査で発見し修正した不整合**: `er003_v1_crosslevel_audio_02_common.py::generate_text_segments()`の日本語segment分岐が、Production SSOT(`er011_human_review_lock_01.py::PRODUCTION_MAX_TTS_ATTEMPTS=3`)の2倍にあたる`max_attempts=6`をハードコードしていた(無限ではないが、他の全Production call siteと不整合な独自capだった)。SSOT定数を明示的に参照するよう修正し(`review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`)、regression test(`er008_crosslevel_audio_02_tts_cap_25_test.py`)で固定した。**対象外と判断し変更しなかったもの**: `er003_v1_a2_audio_02_generate.py::stage_generate_v2_segments()`も同じ`max_attempts=6`ハードコードを持つが、これはCURRENT_SPEC.mdのProduction TTS/ASR call site一覧に含まれない一回限りのKey Phrase試作用スクリプトであり、上限自体は有限(無限retryではない)ため、Production整合性の観点では低優先の技術的負債として現状維持とした(OPEN_ITEMS.md参照) | `DECIDED`(横断監査完了、発見した1件の不整合は修正済み) | ER-008-N8-CLOSEOUT-GOVERNANCE-25 | 2026-08-29 |
| Ending-Clarity Fallback(OPEN-107、旧仕様) | **`WITHDRAWN`(2026-09-03、ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08、ユーザー正式決定)**。下記「B1 Connected Speech Validator」に置き換えられ、Production仕様から撤回された。`er003_v1_n3_01_tts_generate.py`は`er011_ending_clarity_fallback_01.py`を一切importしなくなり(import文・call site 2箇所とも削除、代わりに`voice01.generate_charon_english`/`news_tail_fix.generate_news_narration_wide_margin`を直接呼ぶ)、Dangling Reference Checkで現在のProduction経路から一切参照されないことを確認済み。`er011_ending_clarity_fallback_01.py`自体・そのunit test(`er011_ending_clarity_fallback_01_test.py`、20件PASS)はhistorical recordとして削除せず保持する(ファイル冒頭にWITHDRAWN注記を追加)。撤回理由: `opened to`型の語尾脱落は、追加TTS再生成を伴うfallbackではなく、下記Connected Speech Validatorによる「そもそもTTS誤発音ではなく自然なconnected speech」という直接的な再判定のほうが、リスク・コストとも小さく本質的な解決になるとユーザーが判断したため。以下は撤回前の履歴(参考として保持): ユーザー正式承認(`APPROVED_FOR_PRODUCTION`)。B1のNews本文5segment(`full_story_part1/2`・`point_one`・`point_two`・`in_one_line`、`news_tail_fix.generate_news_narration_wide_margin`経路)に対し、新規`er011_ending_clarity_fallback_01.py`の`generate_news_narration_with_ending_clarity_fallback()`を配線した(`er003_v1_n3_01_tts_generate.py::generate_b1_segments()`のcall siteのみ、A2側の並行関数[`generate_english_segment_with_fallback`]は今回配線対象外)。**設計**: (1)通常instruction+通常retry(`news_tail_fix.py`本体は無変更、`.__wrapped__`経由でreview_lockを1回だけ外側に統合)を1回実行、PASSなら即返す(fallback不使用)。(2)NGだった場合のみ、最終ASR結果に対し既存`er006_preprod_hardening_01_validation.classify_asr_match()`の`content_word_diffs`を流用した一般化語尾脱落検出(`detect_ending_loss_diffs()`、規則的屈折語尾[-ed/-s/-ing等]の脱落のみを対象、特定語[`opened`等]へのhardcodeなし)を行い、検出時のみ`p9a.ENGLISH_STYLE_PREFIX`を一時的にEnding-Clarity instruction(AND方式追加、既存instruction置換なし、文言: "Pronounce grammatical endings and final sounds clearly enough to remain audible, without exaggerating them or disrupting the natural rhythm of the sentence.")へ差し替えて最大2回追加retryし、呼び出し後は必ず元へ復元する。fallback PASS時のみそのsegmentを差し替え、他の正常segmentは一切再生成しない。**Regression**: `er011_ending_clarity_fallback_01_test.py`(10項目の受入テスト、normal PASS/NG→retry PASS/NG→retry NG→fallback発火/fallback PASS→差し替え/fallback NG→既存STOP/他segment不可侵/attempt count正確/assembly対象asset正確/`opened`hardcodeなし/fallback常時適用なし、計13 test、全PASS)、既存`er011_human_review_lock_01_test_01.py`(18件)回帰も無変更のままPASS。**Runtime evidence**: 実Production call site(`er003_v1_n3_01_tts_generate.generate_b1_segments()`)経由のNo.18本番Audio Stage実行、および実wrapper関数を直接呼ぶ独立runtime evidence run(計4回、`er011_no18_open107_runtime_evidence_03.py`)のいずれも、通常経路が初回PASSしfallbackは1回も発火しなかった(=常時適用でないことの実証、fallback自体の実発火は本sessionでは自然発生せず、実API発火evidenceは前回session[ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02、cond6、同一の下位TTS関数`generate_news_narration_wide_margin`をmonkeypatch経由で使用、2/2 real PASS]に基づく)。A2側は今回配線対象外(OPEN_ITEMS.md参照、将来検討)。**2026-09-02追記(ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04)**: (1)検出ロジックを一般化(`detect_ending_loss_diffs()`が、不規則複数形y→ies変化[study/studies等、"studies"へのhardcodeなし、別語[cities/city]でも一般性を回帰確認]・content_word_diffsが複数語にまたがるreplace型diffである場合[語単位に分解して各語を判定]の2点を追加でカバー)。(2)配線範囲をB1のPreview/Comment1-4(`voice01.generate_charon_english`経路)へ拡張(新規`generate_charon_english_with_ending_clarity_fallback()`、`style_prefix_override`引数を直接AND追加できるためp9a.ENGLISH_STYLE_PREFIXのmonkeypatch不要という、News本文版より単純な実装)。これは、B1 `comment_2`("The studies suggest..."→ASR"The study suggests...")がOPEN-107の対象パターン(語尾脱落)であるのに、Comment segmentがNews本文loopと別経路だったため配線漏れでfallbackへ到達できていなかったことが判明したため(regression test 7件追加、既存13件と合わせ計20件PASS)。**実Production call site経由での初めての実発火確認**: 上記配線後、`comment_2`を実際にProduction経路で再生成した結果、通常3attempt全NG(同一の"studies"→"study"パターン)→`ending_clarity_trigger_check`が`{"canonical_word": "studies", "asr_word": "study", "dropped_suffix": "ies"}`を正しく検出→fallback(Ending-Clarity instruction付与)が実際に2attempt発火(`ending_clarity_fallback_used=True`)。ただしfallback 2attemptとも同一の"study"(単数形)発話が継続し、このsegment自体はfallbackでも解消せず`STOPPED`のまま(OPEN-110参照、Ending-Clarity instructionが有効な場合とそうでない場合があることの実証にもなった)。この結果は「fallbackが常時適用でない」ことと「fallbackが実Production経路で正しく発火する」ことの両方を、本session内の実API呼び出しで直接確認した初めてのrunning evidenceである(前回Trialへの依拠から脱却) | `WITHDRAWN`(2026-09-03、ユーザー正式決定によりProduction仕様から撤回。下記B1 Connected Speech Validatorに置き換え) | ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03、ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04(検出汎用化・Comment配線拡張・実発火確認、いずれも撤回済み)、ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08(撤回) | 2026-09-03 |
| B1 Connected Speech Validator(OPEN-107/OPEN-110、ASR差分をconnected speechとして許容する判定) | ユーザー正式承認(`APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`)。新規[er011_b1_connected_speech_validator_01.py](er011_b1_connected_speech_validator_01.py)(ロジックはER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07でVALIDATED判定済みのTrialから無変更で移植)を、B1英語Validatorの中心関数`er006_preprod_hardening_01_validation.py::classify_asr_match()`へ配線した(2箇所: (1)固有名詞以外の内容語diff[`non_entity_diffs`]がTRUE_CONTENT_MISMATCHへ直行する箇所の直前、(2)内容語diffが検出されずratioが閾値未満の最終fallback箇所の直前[規則的な単数/複数語尾差を許容する既存`_is_benign_plural_pair()`に吸収され`non_entity_diffs`まで到達しないPattern C[survey→surveys型]のケースを救済するために必要と判明])。**判定パターン(3種、ユーザー承認範囲に限定、拡張しない)**: Pattern A(歯擦音連続、例: studies/z/+suggest/s/)・Pattern B(破裂音連続、例: opened/d/+to/t/)は`CONNECTED_SPEECH_ACCEPT`(should_pass=True、警告なし)。Pattern C(再分節、例: survey+suggest/s/→surveys suggest)は`CONNECTED_SPEECH_PASS_WITH_WARNING`(should_pass=True、blockingしないがwarningを保持しaudit/最終Artifactへ記録)。いずれの判定にも該当しない場合は既存のTRUE_CONTENT_MISMATCH等をそのまま維持する(false accept時のfall through、新しい音韻パターンの追加は行わない)。**fail-safe**: `classify_connected_speech()`は既存の`protected_check()`(数字/否定保護)を通過した後にのみ呼ばれ、ASR文字列の単純な語単位比較のみで判定するため、数値・否定の不一致を誤って許容することはない。**Regression**: 既存English Validator fixture 57件全PASS(cats/dogsのような無関係な語置換が誤ってPatternに該当しないことを含む)、新規[er011_no18_connected_speech_reading_resolver_wiring_08_test.py](er011_no18_connected_speech_reading_resolver_wiring_08_test.py)8項目(studies suggest型/opened to型/survey suggest型のACCEPT・PASS_WITH_WARNING分類確認、無関係語置換・無関係挿入・子音条件不成立の3件で誤って許容しないことの確認、ACCEPT/PASS_WITH_WARNINGの区別確認、Ending-Clarity fallbackがProduction経路からimportされていないことの確認)全PASS。**Runtime evidence**: No.18本番Audio Stage実行(2026-09-03、`er011_no18_connected_speech_reading_resolver_scoped_retry_08.py`経由でreview_lock.approve_regenerate()付与後、Production正式関数`voice01.generate_charon_english()`を実際に呼び出し)で、B1 `comment_2`("The studies suggest..."→ASR"The study suggests...")が`CONNECTED_SPEECH_ACCEPT`(Pattern A)としてPASS、B1 `comment_3`("...the survey...suggest..."→ASR"...the surveys...suggest...")が`CONNECTED_SPEECH_PASS_WITH_WARNING`(Pattern C)としてPASSすることを実際のTTS/ASR出力に対して確認した(OPEN-110の対象2segmentがこれで解消、詳細はOPEN_ITEMS.md OPEN-110参照)。B1 episodeはこれにより初めて完成しAssembly成功(351.324秒、clipping無し) | `DECIDED` / `PRODUCTION_WIRED` | ER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07(Trial・VALIDATED判定)、ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08(Production配線・実発火確認) | 2026-09-03 |
| Connected Speech Equivalence Layer(OPEN-122、既存3パターンの外側[UNCLASSIFIED]を音韻環境カテゴリA〜G+独立ASR corroborationで判定する拡張レイヤー、**A2/B1英語本文segment限定**) | ユーザー正式承認(2026-09-07、`APPROVED_FOR_PRODUCTION`、範囲=**A2/B1英語本文segment[`full_story_part1`/`full_story_part2`/`point_one`/`point_two`]のProduction正式ASR/Validator経路のみ**。Key Phrase・日本語segment・comment/preview等の他segmentは対象外)。Trial-01/02(`CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-01/02_REPORT.md`、VALIDATED)の判定ロジック(音素prefix脱落/assimilation検出+ARPAbetカテゴリA〜G分類+独立ASR corroboration、単一証拠のみでは絶対にacceptしない安全設計)を無変更で新規[er011_connected_speech_equivalence_layer_production_01.py](er011_connected_speech_equivalence_layer_production_01.py)へ移植した。**配線箇所**: `er011_b1_connected_speech_validator_01.py`(既存3パターン)のUNCLASSIFIED fallthrough後段として、`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail()`へ新規opt-inフラグ`enable_connected_speech_equivalence_layer`(既定`False`、既存`enable_non_latin_cascade`[OPEN-119]と同じ設計パターン)を追加。`classify_asr_match()`がTRUE_CONTENT_MISMATCHかつ`protected_check()`通過済み(数字/否定の真の不一致ではない)の場合のみ、まずSecondary/local ASR無しの安価な事前判定(音韻環境カテゴリ該当有無のみ)を行い、候補である場合のみSecondary Azure(`get_full_text_via_azure_stt_with_phrase_list`、既存関数を再利用)+local faster-whisper(`er008_disfluency_qa_18.transcribe_verbatim`、既存関数を再利用、無料)を1回ずつ追加実行してcorroboration判定する(コストガード: fallthroughかつカテゴリ候補時のみ追加ASR課金が発生)。corroboration>=1件かつカテゴリA/B/Cは`CONNECTED_SPEECH_EQUIVALENCE_ACCEPT`、D/E/F/Gは`CONNECTED_SPEECH_EQUIVALENCE_PASS_WITH_WARNING`(いずれも`should_pass=True`)、corroboration 0件は`EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE`、独立ASR同士が食い違う場合は`EQUIVALENCE_LAYER_MIXED_EVIDENCE_INSUFFICIENT`でいずれも非accept(既存`TRUE_CONTENT_MISMATCH`を維持、診断情報のみ`connected_speech_info`へ付与し事後監査可能にする)。**適用範囲の限定方法**(OPEN-119と同じ設計): 呼び出し元(`er003_v1_n3_01_tts_generate.py::generate_a2_segments()`/`generate_b1_segments()`のfull_story_part1/2・point_one・point_two各ループのみ)から`er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback()`/`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin()`/`er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()`まで新規kwargを明示的に`True`で貫通させる(既定`False`のため引数を渡さない全既存呼び出し元[Key Phrase`generate_key_phrase_component_verified`・日本語`ja_secondary`・comment/preview/title等]は無変更)。既存retry/regeneration/fallback機構(`review_lock.guarded_generate`・`REGENERATE_APPROVED`・Minimal instruction fallback・Cost Guard)とは独立に、いずれの経路でも同一の`classify_asr_match`→Cascadeを通る設計のため整合済み。**A2 6% time-stretch後の独立再検証経路(`apply_a2_slowdown_postprocess`、`classify_asr_match`を直接呼ぶだけの別コードパス)には今回配線していない**(スコープ外、既存のslowdown retry機構[最大3回の取り直し]で吸収されるため安全上の懸念は低いが、Layerの恩恵を受けない既知のギャップとして記録)。**Runtime evidence(Standard同期、実API、実測合計¥3.34)**: (1)A2 Flagship("showed strong"、OPEN-112 Theme2診断の保全音声)を実際のProduction Cascade関数(`evaluate_attempt_with_cascade`)へ投入し`CONNECTED_SPEECH_EQUIVALENCE_ACCEPT`(カテゴリA/B/C該当、Secondary/local corroboration 2/2)を確認。(2)B1実本文1件(hanshinテーマ`point_two_body`)をStandard同期で実生成し、`NORMALIZED_MATCH`(ハイフン表記差のみ)でLayer不発火のまま合格することを確認(通常時の無介入を実証)。加えてTrial-01実音声(`P6_dont_you.wav`、"want"の実発話)を再利用し、Primary ASR文字列のみ"want"→"wan"へ意図的に差し替えた合成fallthroughを構成、Secondary/localは実音声への実ASR実行により`CONNECTED_SPEECH_EQUIVALENCE_ACCEPT`(カテゴリA/B/C/F、corroboration 2/2)を確認。(3)敵対的陰性対照2件(Trial-01 N1[claimed"showed"・実発話"show"、Flagshipと同一音韻環境]・Trial-02 T2N4[claimed"turned"・実発話"turn"、SecondaryがcanonicalへMIXEDに誤支持])を実際のProduction Cascade経路へ投入し、いずれも非accept(`TRUE_CONTENT_MISMATCH`のまま)を確認(false accept 0/2)。**Regression**: `run_project_regression.py`(collected=2112、failed=3[`er003_test_bad`の意図的self-check・`er003_test_p2j_investigate`のOPEN-77既知meta-test集計、いずれも本タスク以前から存在する既知の無関係failure]、errors=0)、`er006_preprod_hardening_01_validation_test.py`57件・`er006_secondary_asr_01_test.py`29件・`er011_no18_connected_speech_reading_resolver_wiring_08_test.py`15件・`er011_tts_attempt_audio_retention_wiring_01_test.py`9件・`er011_human_review_lock_01_test_01.py`18件・`er007_ja_secondary_asr_01_test.py`9件・`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`5件、いずれもPASS(新規kwargs追加に伴い`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`・`er011_tts_attempt_audio_retention_wiring_01_test.py`のmock signatureを更新、KP経路が新規フラグを一切渡さないことのassertionも追加)。新規[er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py](er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py)16件PASS(判定ロジック本体・Cascade配線・KP/日本語が範囲外であることの直接確認を含む)。**Key Phrase/日本語が範囲外である証拠**: `generate_key_phrase_component_verified()`のソースコードが新規kwargを一切含まないことをテストで直接確認、`er007_ja_secondary_asr_01.py`が本Equivalence Layerモジュールを一切importしていないことをテストで直接確認。**Git操作完了**(commit`3297d1b`、main反映済み。`PRODUCTION_WIRED`確定、Fable最終受入2026-09-07、根拠`PM-LANE-A-PRODUCTION-WIRED-FINAL-ACCEPTANCE-AUDIT-01_REPORT.md`)。詳細: `OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01_REPORT.md` | `PRODUCTION_WIRED`(commit`3297d1b`、範囲限定[A2/B1英語本文segment]、Fable最終受入2026-09-07) | CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-01/02(Trial・VALIDATED判定)、OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01(Production配線・Runtime evidence取得、commit`3297d1b`で反映済み)、PM-LANE-A-PRODUCTION-WIRED-FINAL-ACCEPTANCE-AUDIT-01(Fable最終受入監査) | 2026-09-07 |
| Transcript Style Normalization(OPEN-123、標準contraction展開[否定保持のみ]を英語ASR照合の共通正規化層として採用、**適用範囲は英語ASR照合経路全体[Key Phrase英語経路を含む]であり、A2/B1本文に限定しない**) | ユーザー正式承認(2026-09-07、`APPROVED_FOR_PRODUCTION`)。採用元は`OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01_REPORT.md`§13(VALIDATED)。`er006_preprod_hardening_01_validation.py::classify_asr_match()`を薄いラッパーへ変更(既存の分類本体は`_classify_asr_match_core()`として無変更のまま温存)し、should_pass=False(≒TRUE_CONTENT_MISMATCH等の非PASS)の場合のみ、新規`expand_standard_contractions()`("don't"⇔"do not"等**否定を保持したまま展開するペアのみ**、`can`⇔`can't`のような否定反転・"want to"⇔"wanna"等の口語的縮約[方式iv]はユーザー決定により不採用)をcanonical/ASR両テキストへ適用し、展開後に既存Validator(`_classify_asr_match_core`)が実際にPASSと判定した場合のみ新規classification`TRANSCRIPT_STYLE_NORMALIZED_MATCH`(should_pass=True)を返す(展開で何も変わらない、または展開後もPASSしない場合はbaselineをそのまま返す=false accept 0を構造的に保証)。`normalize_text()`/`tokenize()`は無変更。新規opt-inフラグは追加していない(=`classify_asr_match()`の全既存呼び出し元[A2/B1本文・Key Phrase英語経路・homophone/数字ゲート・Cascade層]へ自動的に共通適用される)。日本語経路(`er007_ja_secondary_asr_01.py`/`er007_ja_asr_validator_01.py`)は本モジュールを一切importしておらず無影響(ソース確認済み)。**Runtime evidence**: 既知false reject(Trial-08 P3 point_two、3回STOPPED実例)を保全音声+実Primary ASR結果で実Production関数(`classify_asr_match`/`evaluate_attempt_with_cascade_detail`)へ投入し3/3救済(追加ASR呼び出し無し)、既存Regression fixture(POSITIVE29+AMBIGUOUS2+NEGATIVE28)無回帰(NEGATIVE28件は非救済のまま)、Key Phrase英語経路(実preserved KP音声5件で既存PASS維持を確認、contraction入りKey Phraseの実データが無いため合成2件[音声は実物流用、text組のみ合成、明記]で救済/非救済とも想定通りを確認、想定外挙動は0件)、wanna系(OPEN-122 Trial-01の実測音声P6再利用)は本層では非救済のまま維持を確認(OPEN-122 Equivalence Layerで救済されるかは別層)。新規単体テスト19件PASS、`run_project_regression.py`無回帰(collected=2157・failed=3[既知の無関係failure]・errors=0)。**Git操作完了**(commit`9f25f7d`、main反映済み。`PRODUCTION_WIRED`確定、Fable最終受入2026-09-07、根拠`PM-LANE-A-PRODUCTION-WIRED-FINAL-ACCEPTANCE-AUDIT-01_REPORT.md`)。b05型のSecondary/Local書き起こし非対称性の調査・Key Phrase経路への追加展開範囲拡大等は`OPEN_ITEMS.md` OPEN-123行の未決事項として継続。詳細は`OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01_REPORT.md`参照。 | `PRODUCTION_WIRED`(commit`9f25f7d`、Fable最終受入2026-09-07) | OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01(Trial・VALIDATED判定)、OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01(Production配線・Runtime evidence取得、commit`9f25f7d`で反映済み)、PM-LANE-A-PRODUCTION-WIRED-FINAL-ACCEPTANCE-AUDIT-01(Fable最終受入監査) | 2026-09-07 |
| A2 Reading Resolver(OPEN-111、辞書候補+限定LLM選択による読み解決) | ユーザー正式承認(`APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`)。A2(日本語)専用、B1へは一切適用しない。新規[er011_a2_reading_resolver_01.py](er011_a2_reading_resolver_01.py)(ロジックはER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07でVALIDATED判定済みのTrialから無変更で移植)を、日本語Validator`er007_ja_asr_validator_01.py::classify_ja_asr_match()`へ配線した(既存の`whole_text_reading_equal`/`_reading_equal_allowing_voicing`による全文読み一致救済[漢字/ひらがな script差の吸収]が失敗した場合にのみ呼ぶ、同じ設計思想の延長)。**方式**: canonical/ASR双方をpykakasiで機械かな変換→差分位置を`difflib`で検出→差分に含まれる漢字1文字についてpykakasi内蔵辞書(kanwadict)から読み候補一覧を取得(個別語のhardcodeなし)→LLM(Approved SUPPORT_MODEL)に全文文脈と候補一覧のみを渡し、JSON Schema `enum`で候補外を選択不能に制約した上で1つ選ばせる(自由生成不可)→再比較。resolved_matchが厳密にTrueの場合のみ`READING_RESOLVED_MATCH`(should_pass=True)とし、それ以外(候補なし/LLM異常応答/候補外/例外/再比較後も不一致)はいずれも一律non-passとして既存のTRUE_CONTENT_MISMATCH処理へfall throughする(fail-safe)。`er007_ja_asr_validator_01.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED`(既定`True`)でON/OFF切替可能(既存の`FEATURE_FLAG_SECONDARY_ASR_ENABLED`等と同じ設計パターン)。**Regression**: 既存Japanese Validator fixture 35件全PASS(「月」つき/がつfixtureは、Reading Resolverが辞書候補+文脈から正しく「つき」を解決できることを示す新しい趣旨のfixtureへ更新)、新規wiring_08_test.py 7項目(後→あと解決、完全一致segmentでResolver未発火、候補外応答/候補なし/LLM例外の3種のfail-safe確認、読み問題でない真の内容誤りがREADING_RESOLVED_MATCHにならないことの確認、B1側からimportされていないことの確認)全PASS。**Runtime evidence**: No.18本番Audio Stage実行(2026-09-03、review_lock.approve_regenerate()付与後、Production正式関数`generate_a2_japanese_with_reading_safety()`経由)で、A2 `comment_1`(「...通知音のあとに...」→ASR「...通知音の後に...」)が`READING_RESOLVED_MATCH`としてPASSすることを実際のTTS/ASR出力に対して確認した(標準経路attempt 2でresolver発火・解決、OPEN-111が解消、詳細はOPEN_ITEMS.md OPEN-111参照)。A2 episodeはこれにより初めて完成しAssembly成功(347.338秒、clipping無し)。**コスト実測**: Reading Resolver呼び出し分のみで¥0.03(2 API呼び出し、`responses.create`/`gpt-5.6-luna`)、No.18 A2/B1 Audio Stage全体(全segment再生成+scoped retry)で¥51.18(90 API呼び出し、TTS/ASR含む) | `DECIDED` / `PRODUCTION_WIRED` | ER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07(Trial・VALIDATED判定)、ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08(Production配線・実発火確認) | 2026-09-03 |
| JA ASR表記ゆれ一般化Variant Layer(OPEN-145、形態素解析ベース読みエンジン+正規化層による追加型[additive]チェック) | ユーザー正式決定(2026-09-12、`APPROVED_FOR_PRODUCTION`)。A2(日本語)専用、B1へは一切適用しない。JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01(初回+修正1回目+修正2回目、`VALIDATED`)で検証されたCandidate B/C/D-1/D-2を、新規Production module[er011_ja_asr_variant_layer_01.py](er011_ja_asr_variant_layer_01.py)へ統合・移設した(Trial専用ファイルからは一切importしない)。**対象**: (a)かな⇔漢字の辞書未登録読み・(b)かな⇔カタカナ・(c)同音異表記・(d)送り仮名等の一般的表記差(以上Candidate B、fugashi+unidic-lite形態素解析ベースの全文読み一致)、カタカナ語末長音符の省略差(3モーラ以上の外来語のみ対象)・助数詞「ヶ月/ヵ月/カ月→か月」表記統一(Candidate C)、漢数字の位取り[十/百/千/万]を含む一般正規化(既存の閉じた助数詞リストのみ対象、「日」「人」は引き続き対象外、Candidate D-1)、voicing許容Cascade(`ASR_VALIDATION_UNCERTAIN`、根拠が`phonetic_uncertain`のみで`entity_like`を含まない場合に限る)の形態素解析ベース厳密一致による`PHONETIC_MATCH`引き上げ(Candidate D-2)。**設計原則(追加型)**: 既存のpykakasiベース判定・Cascade・数字/否定保護・entity_like判定は一切変更しない。既存判定がPASS/Cascade確定した経路には一切触れないため、regressionが構造的に発生しない。**配線箇所**: (1)Candidate B/C/D-1は`er007_ja_asr_validator_01.py::classify_ja_asr_match()`内の2箇所[既存Resolver(LLM)呼び出し直前/数字のみの不一致(否定不一致を伴わない場合に限る)による保護落ち直前、いずれも`try_rescue_before_resolver()`を呼ぶ]、(2)Candidate D-2は`er007_ja_secondary_asr_01.py`のA2 Cascade呼び出し元(`evaluate_attempt_ja_with_cascade_detail()`、Primary#1/#2・Secondary#1/#2の4箇所)から`try_upgrade_voicing_cascade()`を呼ぶpost-processingとして配線した(既存関数自身の`ASR_VALIDATION_UNCERTAIN`という返り値の意味は変更せず、Cascade呼び出し元の判断に委ねる既存設計を維持するため)。**feature flag**: `er011_ja_asr_variant_layer_01.FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED`(既定`True`)。**fail-safe**: `fugashi`/`unidic-lite`のimportに失敗した場合、モジュールimport時点でこのflagを強制的に`False`へ落とし`warnings.warn`で警告する(既存のpykakasiベース判定のみで継続、既存Productionを止めない)。依存は`.venv`へインストール済み(`fugashi`/`unidic-lite`/`jaconv`)だが、リポジトリ直下に配布用の`requirements.txt`が存在しないため追記していない(`requirements-ci.txt`はCI test infra専用でProduction依存を表さない、既存の運用方針どおり)。**Regression**: Trial fixtureの自作82件+実データ161件をProduction関数経由で再評価し82/82・実データ既知過去MISMATCH7件中5件PASS化・過去PASS72件中真のregression0件(flag ON/OFF比較、flag OFFは配線前と完全一致)を実測、既存`er007_ja_asr_validator_01_test.py`(POSITIVE10/NEGATIVE15/ENTITY_LIKE1/PHONETIC_UNCERTAIN2/WHOLE_TEXT系5/KNOWN_TRADEOFF1、「月/つき」1件はLLM必須のためAPI支出禁止によりskip)・`er011_no18_connected_speech_reading_resolver_wiring_08_test.py`(#10/#14/#15関連)全PASS、`run_project_regression.py`(collected=2322、failed=3、既知の無関係failureのみ、本タスクによる新規failureなし)。詳細・runtime evidence・Gate 3判定は[OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01_REPORT.md](OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01_REPORT.md)参照 | `APPROVED_FOR_PRODUCTION`(実装済み、Gate 3進行中、`PRODUCTION_WIRED`は未宣言) | JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01(Trial・VALIDATED判定)、OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01(Production配線) | 2026-09-12 |

### Cost定義(Audio Production)

ER-006以降のAudio Cost報告は、以下4区分を共通言語として使う
(過去の報告で「実費」「想定コスト」等の曖昧な語を単一の数字として
混同していた反省を踏まえる、ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01
で初めて明確化)。

| 用語 | 定義 | 現在の基準値(1 Topic=B1+A2 pair) | 備考 |
|---|---|---|---|
| Historical Actual | 実際に支払われた金額(過去ログの実測合計そのもの) | ログごとに異なる(単一の固定値なし) | `er005_cost_logger.py`の`raw_usage_log.jsonl`から集計 |
| Clean Production Cost | 全工程が初回attemptで成功した場合に必要な費用(retry・研究・Cascade等の追加費用を一切含まない理論下限) | ¥65.14/pair | ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01で再構築 |
| Expected Conditional Waste | 条件付きで発生しうる追加費用の期待値(Primary ASR #2、Secondary ASR Cascade、Pronunciation Research、TTS retry等) | ¥46.03/pair | 実測1.68倍のTTS/ASR retry・Pronunciation Research実測cache miss率・Secondary ASR保守的estimateを合成 |
| Expected Production Cost | Clean Production Cost + Expected Conditional Waste | ¥111.17/pair | **この値はestimateを含む進化中のbaselineであり、恒久的な固定値ではない**。特にSecondary ASR Cascade発動率(1回/topic、ESTIMATE)はランダムサンプル未検証のまま(→[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-49) |

**過去の報告値との関係**: ER-006-AUDIO-COST-PILOT-02の¥106.4/pairと
ER-006-AUDIO-RETRY-CASCADE-PROD-01の¥113.0/pairは、いずれも今後
参照しない(前者はPronunciation/Cascade費用未計上、後者は根拠の薄い
仮定「1.3回/topic」を使用していた)。¥111.17/pairが現時点の正である。

### コスト報告の通貨ルール(2026-08-29、ER-008-N8-CLOSEOUT-GOVERNANCE-25で正式化)

ユーザー決定により、Claudeがユーザーへ提示するコスト(意思決定用の主表示)は
**円ベースを基本とする**(1 USD = 160円換算、`er005_stage7_cost_compute.py::USD_TO_JPY`が
SSOT)。対象は少なくとも LLM(Writer/Fact Checker/Ledger Deviation等)・Research・
TTS・ASR・retry/regeneration単価・月次試算・A2/B1 pair単価・100/500/1000記事規模の
試算を含む。ドルは括弧併記してよいが、**ドルだけの報告は禁止**。例:
「約0.8円/retry(約$0.005)」「約17.8円/記事」。

**既存の実装状況**: Audio Production系の一部スクリプト
(`er006_pool_pilot_01_cost_time_compute.py`、`compute_topic_cost.py`)は元々
`USD_JPY = 160.0`/`USD_TO_JPY = 160`を個別に定義済みで、上記の¥111.17/pair等の
数値はすでにこのレートで円換算されている。共通cost計算モジュール
`er005_stage7_cost_compute.py`(ER-006モデル移行後の単価バグをER-24で修正した
モジュール、`record_cost()`はUSDのみ返す)には為替換算が無かったため、ER-25で
`USD_TO_JPY = 160.0`定数と`usd_to_jpy(usd)`ヘルパーを追加し、このモジュールを
円換算のSSOTとした。**計算ロジック自体(単価表・トークン集計)は変更していない**
(表示層への円換算追加のみ、既存のUSD建て戻り値・既存呼び出し元の挙動は無変更)。
今後、新規に作成するコスト集計・報告コード/ドキュメントは、この
`USD_TO_JPY`定数を参照して円表示を主表示とすること。

## TTS記号正規化(全Family共通) — 2026-09-27新設・Fable判定`PRODUCTION_WIRED`
(`TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01`、Family C Layer 2は例外)

TTS読み上げに不適切な記号(canonical textには残すが、TTSへ渡す直前にのみ
機械的に処理する対象)を全Family共通で扱う基本原則・採用ルールを本節で
正式化する。**canonical text自体(記事本文・Key Phrase gloss等の保存データ)
は変更しない**(TTS直前の使い捨てNormalizerでのみ処理し、副作用を後段へ
残さない)。

**基本原則**: (1) 生成前のPrompt予防(Layer 1、Writer/選定Promptで対象記号を
そもそも使わないよう指示)→(2) Writer出力に対するValidator+既存retryループ
への統合(Layer 2、Family A/X/Key Phraseの既存retry予算内で検知・再生成)→
(3) TTS直前の決定論的Normalizer(Layer 3、`er003_audio_tts_asr_safety.py`、
LLM不使用の規則変換)→(4) TTS直前の決定論的Gate(Layer 4、
`symbol_gate_requires_stop`、未変換の残存記号を検出しSTOP、既存Audio
Validation Gate/Human Review Lockへ合流)の3層(実質4層)構成とする。

**採用ルール一覧**:
- 波ダッシュ「〜」「～」: 位置に関わらず**全て**「なになに」へ機械的に変換
  する(Key Phrase glossを含む)。**2026-09-06 OPEN-117決定(文頭・読点直後
  のみ変換)は本タスクにより全位置ルールへ拡張・統合された**(下記「拡張前
  の記述」注記および`OPEN_ITEMS.md` OPEN-117参照、旧記述は上書きせず残す)。
- 「…」「……」: 文末相当なら句点「。」、それ以外は読点「、」へ変換する。
- コロン「:」「：」・セミコロン「;」「；」: 句点へ変換する(数字直前直後は
  対象外、時刻表記等を保護)。**2026-09-27追記(修正1回目、`TTS-SYMBOL-
  NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01`)**: 時刻表記(H:MM、時
  1〜2桁+分ちょうど2桁、後続のa.m./p.m./AM/PM等の有無は不問)のコロンは
  数値表記として無変換のまま許容し、TTS直前の残存記号Gate(Layer 4、
  `detect_prohibited_symbols`)も同じ条件でこれをSTOP対象として検出しない
  (Family X Hormuz`full_story_part2`の"11:04 a.m."が誤ってSTOPしていた
  実例に対応)。比率表記("3:1"等、分がちょうど2桁ではない表記)への一般化
  は行わない(比率表記は分が単桁になりがちなため対象外になりやすいが、
  分がちょうど2桁の比率表記[例:"1:20"]は許容対象に含まれてしまう。厳密に
  比率表記そのものを判別しているわけではない)。**2026-09-27追記(修正2回目、
  同管理ID、Opus L2所見反映)**: (1) 上記の時刻表記コロン許容は全角コロン
  「：」・全角数字にも対応する(`_JA_COLON_SEMICOLON_RE`の数字直前直後
  除外条件[半角/全角とも]と定義を一致させた)。(2) 許容したコロンはSTOPし
  ないが、Gateの検出結果には`TIME_COLON_ALLOWED_OBSERVE`というobserve
  専用カテゴリとして記録を残す(`symbol_gate_requires_stop()`はこの
  カテゴリをブロックしない)。(3) Writer出力直後のValidator(Layer 2)が
  NG理由をPromptへ追記する`build_symbol_violation_prompt_note()`は、
  STOP対象カテゴリのみを列挙するようフィルタし、英語%/$/¥の既存observe
  (`NUMERIC_SYMBOL_OBSERVE`)・上記時刻コロンobserveのいずれも、Writerへ
  「直せ」と誤って伝えないようにした。(4) JA側Layer 1 Prompt
  (`er019_family_x_ja_writer_o_r1_r2_01.SYMBOL_PREVENTION_BLOCK_JA`)へ
  「時刻は『午前11時4分』のように日本語で書く(数字とコロンの記号表記は
  使わない)」を明記し、EN側Layer 1 Prompt
  (`er003_v1_n3_01_articles_generate.py`のコロン禁止文)へ「時刻表記の
  コロンは例外的に使ってよい」を明記して、Prompt指示と実際の
  Normalizer/Gate仕様の不一致を解消した。JA本文はcanonical text自体が
  時刻を日本語表記で書く前提のため、JA側Normalizer/GateにEN同様の時刻
  コロン許容を新設する対応(SF-1(b))は不採用とした(JA本文でH:MM表記が
  生成されること自体をPromptで防ぐ方針、詳細`DECISION_LOG.md`同管理ID
  エントリ参照)。
- 英語%/$/¥: Writer Prompt予防のみ(自然語[percent/dollars等]での表記を
  指示)。Validatorは検出・ログのみで生成を止めない(既存retry予算を消費
  しない)。
- URL・email・絵文字・Markdown記号: 禁止(Prompt予防+Gate検出)。
- 括弧・スラッシュ: 禁止(Prompt予防+Gate検出)。
- 省略形は通常の読み(TTS自然発話に委ねる、追加ルールなし)。

**pause機構**: 上記の句読点置換(コロン/セミコロン→句点、「…」→句点/読点)を
TTSのpause(間)表現として正式採用する。`<short pause>`等の明示的pauseタグは
本タスクで観測のみ実施し(fixture 2件、意図せぬ3回目呼び出し込み約¥0.46)、
**採用していない**(観測結果はSTOP項目として記録のみ、Production化しない)。

**対象経路**: Family A本文Writer(Point Overlap article retry)・Key Phrase
選定(Redundancy QA retry)・Family X `ja_writer`(JA Fact Check must-fix
retry)・Family B/C共有TTS層(Layer 1・3・4)。Family Bは日本語segmentが
存在しないため対象外。**例外**: Family C Layer 2(Writer-output Validator、
`er013_family_c_future_writer_08.py`/`_08_b1.py`対象)は、Family A/Xのような
既存Writer-output retryループがFamily Cの実Writerに存在しないため未実装
(Prompt予防[Layer 1]+Normalizer[Layer 3]+Gate[Layer 4]のみ適用。新規OPEN
項目として`OPEN_ITEMS.md`で追跡、詳細は同REPORT §8・§9)。

**Family Z Writer実装時の必須適用**: Family Z(Fiction)のProduction Writerを
実装する際は、上記Prompt予防+Normalizer+Gateの3層(実質4層)を同様に適用
することを必須とする(未着手、`CURRENT_SPEC.md`「Family Z(Fiction)」節参照)。

**拡張前の記述(旧、上書きせず参考として残す)**: OPEN-117の下、
「Key Phrase日本語gloss 表示用/TTS用分離」行(本ファイル「Key Phrase」節)
には、2026-09-06時点の実装として「変換対象は文頭または読点『、』直後の
『～』『〜』のみ、数値placeholder型・範囲表記中の文中位置は無変換のまま
既存gateへ渡す」という記述が残っている。この記述は**2026-09-27時点では
拡張前の履歴**であり、実際の変換ルールは上記「全位置」ルールへ置き換え
られている(Key Phrase gloss側の「〜/～は許容」という表示用/TTS用の
非対称緩和も撤回済み)。当該行自体は履歴として上書きしない。

詳細・runtime evidence・費用・回帰確認は
`TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01_REPORT.md`参照。

## 固有名詞読み解決(JA/EN共通) — 2026-09-27新設・Status: **`PRODUCTION_WIRED`**
(実装済み・実データrunning evidence取得済み、Fable Gate 3判定2026-09-27で確定。
Phase 2`PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01`[commit
`323a18a7`でcloseout]+Phase 3`PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-
WIRING-AND-JA-VALIDATOR-PUNCT-01`[commit`eb7825d7`、Opus L2 BLOCKERなし]。
残穴はOPEN-203[A2 fallback経路resolver_info未伝播、ユーザー判断待ち]として
継続追跡)

Phase 1 recon(`docs/pm/recon_pronunciation_resolution_01.md`)で確認された
「JA: `DEFAULT_JA_READING_DICTIONARY`(静的・手動追加のみ)+Foreign Token
Gateで未登録語は無条件HUMAN_REVIEW」「EN: Pronunciation Ledger/Researchは
実装済みだがProduction初回TTS経路からは一度も呼ばれていなかった」という
2つのギャップに対し、JA/EN共通core(`er025_entity_pronunciation_resolver_
core_01.py`)を新設し両言語のProduction TTS入口へ配線した(Phase 2)。
必須Opus L2レビューでBLOCKER-1/2を検出し、Sonnet修正1回目でこれを是正した
(詳細・照合表は`PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_
REPORT.md`§14-16)。

**確定内容(Phase 2、Opus L2 BLOCKER是正込み)**:
- Ledger検索(`er006_pronunciation_ledger_01.get_hint_for_text`/
  `get_low_confidence_entries_for_text`)は、surfaceがASCII(英数字主体)の
  場合は語境界一致、非ASCII(漢字・アクセント付きラテン文字等)は部分一致
  とする(`_surface_matches_text()`)。是正前は語境界なしの部分一致であり、
  ASR Secondary Cascade由来の短い誤entry(surface="plus"/"mini"/"ganis"等)
  が無関係な語(surplus/minister/organisation等)へ誤爆する経路があった。
- TTS発音注入経路(`augment_style_prefix_with_pronunciation`)は、ASR
  Secondary Cascade Human Review packaging専用のentity_type
  `cascade_unresolved_entity`(`er006_pronunciation_ledger_01.
  CASCADE_UNRESOLVED_ENTITY_TYPE`)を対象に含まない
  (`exclude_entity_types`引数、`apply_tts_injection_filter=True`)。ASR
  Secondary CascadeのPhrase List用途では引き続き含まれる(用途ごとに
  `exclude_entity_types`/`apply_tts_injection_filter`引数で制御、呼び出し元
  シグネチャは無変更)。
- 本番Ledger(`er006_output/pronunciation_ledger_01/ledger.json`)内の
  上記誤entryは削除ではなく`tts_injection_disabled=true`+
  `tts_injection_disabled_reason`による隔離フラグで分離した
  (`set_tts_injection_disabled()`、`get_hint_for_text(...,
  apply_tts_injection_filter=True)`で除外)。
- LedgerKeyへ`source_context`を一般機構として追加した(`(surface,
  source_context)`の組がキー、既定`source_context=""`は既存呼び出し元と
  完全後方互換)。同一綴りが文脈により異なる読みを持つ場合(例:
  "Dionysius"が史実表記と特定作品の確定読みで異なる)に対応する。
- `seed_work_canon_reading(surface, ja_katakana, en_hint, source_context,
  sources)`(`er025_entity_pronunciation_resolver_core_01.py`)により、
  作品固有の確定読みをWeb lookupを介さず`resolution_method="work_canon"`・
  `confidence="high"`として事前登録できる(一般機構、特定作品のハード
  コードではない)。
- Negative cache: web lookupを実際に呼んだが未解決だった語は
  `JA_NEGATIVE_CACHE_COOLDOWN_SECONDS`(6時間)の間、再lookupしない
  (`NEGATIVE_CACHE_RESOLUTION_METHOD`)。
- Run単位のJA web lookup上限: 1プロセス(記事1本のtts stage呼び出し相当)
  あたり最大`MAX_JA_WEB_LOOKUP_CALLS_PER_RUN=5`回。上限到達後は
  fail-safe側(未解決・HUMAN_REVIEW)へ倒れる。
- テスト用web lookup禁止スイッチ: `ALLOW_PRONUNCIATION_WEB_LOOKUP`環境変数
  (既定"1"、"0"で無効化)+`disable_web_lookup_for_test()`(contextmanager)。
  既存test(`er006_kp5_canonical_bug_01_test.py`等)が意図せず実APIを呼び
  本番Ledgerへ書き込む問題を防止する。
- `ledger_health_check()`(`er006_pronunciation_ledger_01.py`)により、
  `cascade_unresolved_entity`型でcanonical_spellingがsurfaceと乖離する
  entryや、`tts_injection_disabled`のentry一覧を機械的に検出できる
  (read-only)。
- telemetry: `er025_output/pronunciation_resolution_core_telemetry_01/
  telemetry.jsonl`(best-effort、書き込み失敗時も本処理は継続)。

**別Phase(本Phaseの範囲外、ユーザー既決)**: JA確定読みをTTSへ直接供給する
方式は別Phaseとする。現状はForeign Token Gate解除+ASR期待読み
(`expected_readings`)の付与のみで、実際にGemini TTSが発話する音自体は
変わらない。Melos(`source_context="family_z_melos"`)のruntime evidenceで、
resolverが正しく"work_canon"読み(ディオニス)を解決してもGemini TTSは
その場で英語ふうの読み(ディオニシウス系)を発話し、seedした読みが実際の
発話には反映されなかったことを実測確認した(`OPEN_ITEMS.md`参照)。

**Production配線範囲**: EN側resolver(`resolve_and_augment_en_style_
prefix`)が実際に配線されているのは`generate_narration_snippet_verified_
strict`(A2英語標準+fallback、Key Phrase Componentを含む全EN経路)、
`generate_english_component_minimal_instruction`(B1 scaffold/
crosslevel/news_tail_fix等が呼ぶ、opt-in、Phase 3で標準分岐+Local
Rewrite recoveryにも配線完了)、`generate_charon_english`(B1B、
`voice01`経由、opt-in、Phase 3でLocal Rewrite recovery+技術的fallback
にも配線完了)である(いずれも`enable_pronunciation_resolver=True`を
渡すFamily Xのみ有効化のopt-in方式)。既知の限界: A2英語本文の自前
fallback経路(`crosslevel_common.generate_english_segment_with_
fallback()`)は、fallback結果へ`en_pronunciation_resolver_info`を
伝播しない(`OPEN-203`参照、resolver自体は発火するがtelemetryから
hit有無を追跡しづらいのみで音声・Gate合否には影響しない)。

**Phase 3追記(2026-09-27、`PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-
WIRING-AND-JA-VALIDATOR-PUNCT-01`)**: B1B側`generate_charon_english`・
`generate_news_narration_wide_margin`双方の標準分岐+Local Rewrite
recovery(retry cascadeの後段)+技術的fallbackへresolver telemetryを
一貫して転送するよう修正(`_local_rewrite_recovery_for_charon_english`/
`_local_rewrite_recovery_for_news_narration`が`en_pronunciation_
resolver_info`を保持・転送し、技術的fallbackでは`augment_style_prefix_
with_cached_hits()`でcache済みhitsのみを再利用し新規web lookupは発生
させない)。EN web lookupにもrun単位上限
`MAX_EN_WEB_LOOKUP_CALLS_PER_RUN=5`をJA同様に新設。JA ASR Validator
(`er007_ja_asr_validator_01.py`)の引用符・ellipsis正規化ギャップを
修正(OPEN-199是正)。いずれもFamily X Stage 3e実runtime(2026-09-27、
ユーザー承認済みLock解除9segment)でPASS実例を確認済み(Hormuz A2/B1B
`full_story_part2`・Meta A2`japanese_title`等)。詳細は
`PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-
PUNCT-01_REPORT.md`、`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_
REPORT.md`「## Stage 3e」参照。

**Phase 4追記(2026-09-28、`PRONUNCIATION-RESOLUTION-PHASE-4-A2-
FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01`、ユーザー承認2026-09-28。
Fable Gate 3判定: `PRODUCTION_WIRED`(2026-09-28、根拠: Opus L2所見
反映`535bb391`/`f8d5887c`+OPEN-208登録。ただしA-1のLedger surface条件
[`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION`]はProduction既定OFF
のまま`DEFERRED`/`NOT_ADOPTED`、OPEN-208で継続監視)**:
- **A-2(OPEN-203是正)**: A2英語本文fallback経路
  (`crosslevel_common._run_a2_minimal_fallback_attempt()`)が
  `repro01.generate_english_component_minimal_instruction()`を呼ぶ際に
  `enable_pronunciation_resolver=True`を渡すよう修正した(標準経路
  [`generate_narration_snippet_verified_strict`]がlanguage=="en"で
  既に無条件配線済み[Phase 2]という既存方針に合わせ、新規opt-inフラグは
  追加していない。legacy呼び出し元[B1 scaffold/iran01/sing01等]は
  この関数を直接呼ばないため無変更)。あわせて`fallback_attempts_log`
  各entryと最終STOPPED結果のtop-level(`fallback_en_pronunciation_
  resolver_info`)へも`en_pronunciation_resolver_info`を伝播するように
  した(修正前はfallback経路で情報が戻り値へ一切現れなかった)。
- **A-1(ASR `entity_like`判定の一般化、安全側classification/cascade
  対象の拡張。自動acceptにはしない)**: 従来の「本文中で大文字始まり」
  ヒューリスティック(`capitalized_flags`)に加え、(b)小文字外来語
  (非ASCII文字を含む語、例: "minaudière"、`loanword_flags()`)を
  `entity_like`に含める(`er006_preprod_hardening_01_validation.py`)。
  効果は「entity不一致がTRUE_CONTENT_MISMATCHへ格上げされず、既存の
  entity_only→ASR_VALIDATION_UNCERTAIN→cascade/Human Review経路へ回る」
  までであり、数値/否定/一般内容語のTRUE_CONTENT_MISMATCH検出力は無変更。
  **(a)Pronunciation Ledger登録済みsurface条件は、修正1回目
  (ユーザー判断2026-09-28)によりProduction既定`OFF`
  (`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION = False`)。Status:
  `DEFERRED / NOT_ADOPTED`(将来S1/量産telemetryで「必要」かつ「安全な
  追加条件でfalse accept非増加」の証拠が出たら再検討。関数
  `ledger_registered_entity_flags()`自体は同形一般語ガード付きのまま
  read-only診断ヘルパーとして実装は残すが、フラグがTrueにならない限り
  分類経路[`_classify_asr_match_core()`のentity_tokens合流箇所]には
  到達せず、Ledgerディスク読込[`get_low_confidence_entries_for_text()`
  経由の`_load()`]もこの経路からは発生しない。Ledger自体は読み解決/
  Resolverでは引き続き使用し、この分類目的のフラグとは独立)。**
- **S3(修正1回目、observability専用の追加キー)**: `protected_check()`の
  `content_word_diffs[*]`へ`entity_like_source`(entity_like=Trueの根拠
  カテゴリ`capitalized`/`loanword`のsorted list、Ledger条件OFFの間は
  `ledger`が出現することはない)を追加し、`aggregate_entity_like_sources()`
  ヘルパー経由でer021 telemetry record・cascade各step
  (`er006_secondary_asr_01.py`の`primary_1`/`primary_2`/`secondary_1`/
  `secondary_2`/`tier3_corroboration_secondary`/`non_latin_secondary`/
  `secondary_forced`)・human_review_queueレコードへadditive keyとして
  伝播する(既存キー・分類結果自体は無変更)。
- **N1(既存自動PASS機構への影響の明記)**: entity_like判定の一般化
  (A-1(b)、および将来Ledger条件を再有効化した場合の(a))は、
  `is_entity_like_mismatch()`/cascade起動条件(`evaluate_attempt_with_
  cascade_detail`)だけでなく、CMU辞書ARPAbet完全一致による既存自動PASS
  機構(`er006_secondary_asr_01._case_a_entity_pass()`、`PROPER_NOUN_
  ENTITY_ARPABET_CONFIRMED`)の入力域も同時に広げる。entity_like判定の
  対象が広がるほど、この自動PASS機構へ到達しうる差分の母集団も広がる
  (ARPAbet完全一致という強いgate自体は変更していないが、gateの手前に
  来る候補数が増える点に留意)。
- **N2/N3(evidence記述の是正・記録)**: 初回commit(535bb391)のruntime
  evidence(`er025_output/phase4_evidence_01/`)は、Human Review Lock
  機構([_has_valid_narration_layout()](er011_human_review_lock_01.py)
  が構造的にFalseを返すパス配置)・segment_id role gateの両方を意図的に
  無効化した状態で取得したものであり、通常のProduction経路の初回lookup
  発火点([ALLOW_PRONUNCIATION_WEB_LOOKUP]既定`"1"`)を経由していない
  ことをここに明記する(evidence自体の結論[resolver hookが呼ばれ情報が
  伝播すること]は変わらないが、Lock/role gate無効化という前提条件を
  Opus L2レビュー向けに明示する)。
- runtime evidence: small_bag A2 `full_story_part2`の実canonical text
  (Stage 3eで観測されたkhaite/minaudière同時誤認識)を使い、(1)A-2
  fallback resolverの実発火(実TTS1回+実ASR、Guardrail¥15内。cache-only
  +`cascade_unresolved_entity`除外設計によりkhaite/altuzarra自体は今回も
  注入されないが、resolverが呼ばれ情報が伝播することを確認)、(2)A-1に
  よる再分類(この実transcriptがTRUE_CONTENT_MISMATCH→ASR_VALIDATION_
  UNCERTAINへ変わることをunit testで確認)の両方を実測した。
- S1(修正1回目、¥0・read-only): 既存telemetry/human_review_queueの
  全NG記録(canonical/ASR保持分、denominator=4115)を現行コード(Ledger
  条件OFF)でオフライン再判定した結果、entity_like反転
  (TRUE_CONTENT_MISMATCH→ASR_VALIDATION_UNCERTAIN)は20件、そのうち
  `_case_a_entity_pass`でPASS化しうる件数は0件、loanword根拠のみによる
  反転(一般語誤りが隠れるリスクの保守的な注意フラグ)は0件だった
  (`er025_phase4_s1_offline_reclassification_01.py`、出力`er025_output/
  phase4_s1_offline_01/`)。
- 詳細・呼び出しチェーン表・fixture結果・Gate 3チェックリスト・Opus所見
  照合表・再実行候補は`PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-
  WIRING-AND-ASR-ENTITY-LIKE-01_REPORT.md`(初回+修正1回目)参照。

詳細・runtime evidence・費用・回帰確認は
`PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_REPORT.md`
(Phase 2)、`PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-
VALIDATOR-PUNCT-01_REPORT.md`(Phase 3)参照。

## 試聴Artifact(ユーザー提示用ページ)仕様 — 2026-08-29新設(ER-008-N8-CLOSEOUT-GOVERNANCE-25)

| 項目 | 内容 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 全script掲載の必須化 | 今後、ユーザーへ試聴用Artifactを提示する場合、実際に放送される全segmentのscript(発話される文言そのもの)を同じページへ全文掲載することを標準仕様とする。対象segmentの一覧(A2/B1それぞれ、`er003_v1_n3_01_assemble.py`の`build_a2_timeline()`/`build_b1_timeline()`が実際に組み立てる順序をそのまま反映)は[er008_listening_artifact_script_standard_25.py](er008_listening_artifact_script_standard_25.py)の`A2_REQUIRED_SEGMENTS`/`B1_REQUIRED_SEGMENTS`で定義する。Intro/Outroジングル・Notification効果音・pause(silence)はscript本文を持たないため対象外。今後の試聴Artifact生成scriptは、公開前に`check_full_script_coverage()`で欠落が無いことを確認すること。fixture test([er008_listening_artifact_script_standard_25_test.py](er008_listening_artifact_script_standard_25_test.py))で、1 segmentでも欠落するとFAILすることを確認済み | `DECIDED`(標準仕様として新設、既存No.8 Artifactは既にA2/B1とも全script掲載済みで手動確認では要件を満たしているが、本モジュールによる機械的checkは今回のNo.8 Artifactへは未配線。次回以降の新規Artifact生成scriptへ組み込むこと) | ER-008-N8-CLOSEOUT-GOVERNANCE-25 | 2026-08-29 |
| 固有名詞Human Review表示(試聴Artifact内、該当時) | 試聴Artifactが固有名詞のHuman Review対象を含む場合、既存ルール(ER-23、QA / Human Review節参照)どおり、IPA・pronunciation guide・発音根拠source・confidence・「IPA確定不能」の明示を試聴Artifact上にも表示する | `DECIDED`(既存ルールの再確認、変更なし) | ER-008-N8-FINAL-PRODUCTION-HARDENING-23 | 2026-08-29 |
| 適用範囲(単発の試聴リンクも対象) | 「全script掲載の必須化」は、正式なNo.8/No.9等の試聴Artifactに限らず、ユーザーから「この音声はどこで聞ける?」等、完成音声の確認・試聴・承認のために単発で作成する試聴リンクにも同様に適用する。完成音声だけを提示し、full script(実際にその音声が読み上げる全segmentの本文、放送順)を欠いた提示は不可とする | `DECIDED`(ユーザーが明示的に再確認・適用範囲拡張を指示。No.9 B1試聴Artifactでscript欠落のまま提示していたことを機に発覚) | ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18 | 2026-09-01 |
| 試聴player標準フォーマット(Source列削除/Script列拡幅/個別`<audio>`拡幅) | ユーザーがTrial-09のplayer形式(`er012_output/editorial_b_voices_trial_09_audio/player.html`、Gate 7 (a)〜(l)準拠)を、完成音声/Trial音声レビューの標準フォーマットとして採用した(2026-09-08)。正式な列・CSS仕様は本ファイルへ新設せず、共通module`audio_review_player.py`と`docs/pm/PM_GOVERNANCE.md` Gate 7 (l)を参照する | `DECIDED`(既存player生成箇所を共通module化、正式仕様節は本ファイルに新設しない方針) | PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11 | 2026-09-08 |

## Model Routing Contract

Single Source of Truth: [er006_model_routing_contract_01.py](er006_model_routing_contract_01.py)
(`PROCESS_MODEL_MAP`/`PROCESS_PROVIDER_MAP`、`require_model()`/`require_provider()`)。

| Process | Approved Model/Provider | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| Query Planning | GPT-5.6 Luna | `DECIDED` | ER-005以前から(gather_topic.py) | - |
| Topic Selection | GPT-5.6 Luna | `DECIDED` | ER-005以前から | - |
| Evidence Pack / VFL / Verification | GPT-5.6 Luna | `DECIDED` | ER-006-POOL-PILOT-01(新規構築時から) | 2026-08-21 |
| Exception Search | Perplexity Search API | `DECIDED` | ER-006-POOL-PILOT-01 | 2026-08-21 |
| B1 Writer / A2 Writer(Deviation Check含む) | GPT-5.6 Luna | `DECIDED`(Solから変更) | ER-006-MODEL-ROUTING-CONTRACT-01 | 2026-08-22 |
| Writer Fact Check | GPT-5.6 Luna | `DECIDED`(Solから変更) | ER-006-MODEL-ROUTING-CONTRACT-01 | 2026-08-22 |
| B1 Support / A2 Support(Key Phrase選定・正規化含む) | GPT-5.6 Luna | `DECIDED`(Solから変更) | ER-006-MODEL-ROUTING-CONTRACT-01 | 2026-08-22 |
| Support Fact Check | GPT-5.6 Luna | `DECIDED` | ER-005-SUPPORT-COST-QUALITY-01系実装をER-006 Pool Pilotで採用、ER-006-MODEL-ROUTING-CONTRACT-01で正式契約化 | 2026-08-22 |
| TTS | Gemini `gemini-2.5-pro-preview-tts`(英語)/`gemini-3.1-flash-tts-preview`(日本語)。呼び出し方式はBatch API(`client.batches.create()`)がApproved方式であり、**Production call site全6箇所へ実配線済み**(詳細はAudio Production Pipeline節「Gemini TTS実装方式」)。**注記(2026-09-06、PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01)**: Batch APIは正式リリース後の実量産における正式TTS方式。正式リリース前(DEV/Trial/診断/Production正式経路を使ったruntime確認/完成候補生成/回帰等)はStandard同期を既定とする(PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01、2026-09-06、正本は`docs/pm/PM_GOVERNANCE.md` 7節)。Standard同期使用はProduction正式経路であることを否定しない。**実行モード切替(2026-09-06、ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01、`PRODUCTION_WIRED`)**: 環境変数`TTS_EXECUTION_MODE`(`BATCH`/`STANDARD`、既定`BATCH`)で切替。詳細・実API確認結果はAudio Production Pipeline節「Gemini TTS実装方式」参照 | `DECIDED` / `WIRED` | プロジェクト全体方針(model)、ER-006-AUDIO-COST-SPEC-FIX-01(Batch方式の正式化)、ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01(Production実配線)、ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01(環境変数切替の配線) | 2026-08-22 |
| ASR / Audio QA | **2026-08-25更新: 英語・日本語ともOpenAI `gpt-4o-mini-transcribe`(Primary)、AzureはSecondary Cascade用**。SSOTは[er006_asr_provider_routing_01.py](er006_asr_provider_routing_01.py)(`ASR_ROUTING`/`require_asr_route()`)であり、本Routing Contractの`ASR_PROVIDER`定数(`"azure"`固定)は既存test互換のためのみ残す未配線の値である(詳細はAudio Production Pipeline節「Primary ASR Routing」) | `DECIDED` | ER-006-AUDIO-COST-PILOT-02、ER-006-AUDIO-COST-SPEC-FIX-01(Contract表への反映)、ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(日本語Primary切替) | 2026-08-25 |

**Fail-Closed契約**: 上記いずれの工程も、規定外Model/Providerが指定された場合、または
Model未指定でSDK defaultへ落ちる場合は、API call実行前に`ModelContractViolation`を
送出する(fallbackとして高価なmodelへ自動昇格しない)。Regression test:
[er006_model_routing_contract_01_test.py](er006_model_routing_contract_01_test.py)、
Static audit: [er006_model_routing_contract_01_static_audit.py](er006_model_routing_contract_01_static_audit.py)。

**適用範囲の注記**: Writer/Support系のSSOT配線は、production到達可能な呼び出し箇所
(N3/Pool pipeline: `er003_v1_n3_01_articles_generate.py`・
`er003_v1_n3_01_scaffold_generate.py`・`er006_pool_pilot_01_*.py`)にのみ適用した。
Translation pipeline・CEFR/spoken-first系の過去の実験タスク等、この契約の対象外と
した箇所は、既存のSol既定値のまま変更していない(該当箇所は
ER-006-MODEL-ROUTING-CONTRACT-01完了報告のAudit一覧を参照)。

**Ledger Deviation Checker: GPT-6モデルTrial結果(2026-09-29、
GPT6-MODEL-COMPARISON-TRIAL-01)**: 本Contract表(Model Routing Contract)の
上記Approved Modelは無変更(`gpt-5.6-luna`のまま、Production routing未変更)。
Trial(84 call実測、`er050_gpt6_checker_comparison_trial_01.py`、
`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`をContract非経由で
model引数のみ差し替えて実行)の結果、`gpt-6-luna`はChecker(Ledger Deviation
Checker)の**採用候補**としてユーザーが次工程(OPEN-233 Checker再設計)へ進める
ことを決定した(Trial Status=`VALIDATED`。**`APPROVED_FOR_PRODUCTION`ではない**、
Routing変更は別途ユーザー判断)。単価は`gpt-5.6-luna`より安い(2026-10-05訂正: 「正確に半額」は誤り、Input/Cachedは半額だが出力単価は$0.50 vs $1.20で半額ではない)
(Input $0.10/Cached $0.01/Cache writes $0.125/Output $0.50 vs $0.20/$0.02/
$0.25/$1.20、Standard tier、一次ソース`https://platform.openai.com/docs/pricing`
2026-09-29確認)。`gpt-6-sol`は互換性probe(1 call)SUCCESSだが本比較は保留
(追加Trial・大量callは行わない)。`gpt-6-astra`は対象外。詳細:
`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§Closeout、
`docs/pm/design_gpt6_model_comparison_trial_01.md`§10。

## OPEN-233 Self-Recovery Flow — 重大/軽微/問題なしの線引き(2026-10-03ユーザー正式採用、`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`未達)

**Status**: `APPROVED_FOR_PRODUCTION`(人間ユーザー決定、2026-10-03、2回目。`DECISION_LOG.md`末尾エントリ、`OPEN-233-SELF-RECOVERY-TRIAL-01`委任_55)。**`PRODUCTION_WIRED`ではない**(Self-Recovery Flow自体がProduction未接続。再較正は(a)で不合格があり、Fable判断待ち。下記)[2026-10-04注記、委任_64: A4-1は委任_57で再ラベル済み(Safety-critical登録8→5)・再較正合格で解決済み]。以下の基準は、Self-Recovery FlowをProductionへ接続する際に、Stage 2判定・正解ラベル・Safety-critical登録へ適用する。

**ユーザー原文(逐語)**:

- **重大**
  - 英語学習者に事実関係の重大な誤解を与えるもの
- **軽微**
  - 事実関係の核心は保たれているが、表現の精度が少し落ちるもの
- **問題なし**
  - 確認済みFactから自然に導ける描写・推論で、新しい具体的事実を追加しないもの

例として、すでにユーザー判断済みの以下を必ず基準にしてください。

- `Also, some calls needed user information to continue.`
  → 軽微
- `They enjoyed AI's convenience, but a human was on the other end. They did not realize it.`
  → 問題なし
- `Just after the charge plan disappeared, prices began to fall.`
  → 軽微

特に、条件付き→断定を一律Majorにしない/自然な推論は否定形だけでなく肯定形も許容/「迷ったら重大」に機械的に寄せず、重大な誤解になるかで判断、という方向へ合わせる。ただし、数値・主体・否定・比較・時期などの機械的な安全装置については、今回の採用内容だけを理由に緩めない(ユーザー原文)。

**適用先(Trial/検証用モジュール、Production正式path[`er003*`・`er009*`・`er010*`・`er012*`・`er019*`]は無変更、`git grep`で`er052_open233`のimportが0件であることを確認済み)**:

- Stage 2 body判定: `MISCONCEPTION_PRINCIPLE_TEXT_V7`(`er052_open233_self_recovery_stage2_calibration_01.py`、V6へ追記、V4〜V6は定数として残す)。runnerの`BODY_RUBRIC_DEFAULT`はV7(2026-10-04注記: 現在はV7b、委任_60、下記)。Stage 2 production既定の`MATERIALITY_RUBRIC_V7`は「迷えばBLOCKING」を「重大な誤解になるかで決める」へ置換(旧版は残す)。
- 正解ラベル(設計書§7-0-iter33): Meta-1/Meta-2=QUALITY、MUSE-HC-012「They enjoyed…」=ACCEPTABLE、HF-009「prices began to fall」=QUALITY(旧ラベルは「旧」として残す)。
- Safety-critical登録: `SAFETY_CRITICAL_SUB_IDS`(r3d)から Meta-1/Meta-2 を除外(8件→6件)。runnerの`SAFETY_CRITICAL_CLAIM_DEFS`では`expected: "QUALITY"`の過剰品質監視用として残し、`detect_safety_critical_misdowngrades`・`residual_at_pass`の対象外とした。
- **不変の機械的な安全装置**: `FLOOR_FLAGS`(changed_actor/number/negation/comparison/time)によるfloor、precheck、主体置換ガード、`MAX_CYCLES`、Hook専用rubric(V3/V4)、`DISCLOSURE_GAP_NEGATION_RE`(否定形限定)。注意: K19(`prices began to fall`)はユーザー決定でQUALITYだが、`changed_comparison`のfloorが不変のため、Checkerがcomparisonフラグを立てた実行ではLLM判定がQUALITYでもfloorでBLOCKINGに引き上げられる(floorをK19から外すかはユーザー判断事項、未決)。

**再較正の結果(委任_55、Stage 2単体、n=2、26 call、¥4.3666、`er052_output/open233_safety_control_03/results_01.json`)**: (a)Safety-critical 6claim: **A4-1が2/2 ACCEPTABLE(誤降格2件、不合格)**、他5claim(B3・B4-a・A2A3-0・A4-0・A5-0)は全て2/2 BLOCKING。(b)Safety12(er009 9フラグ)=誤降格0/18。(c)Hormuz許容5/NG5: 従来(V6)と合否が同じ(許容5=false BLOCK 0、NG5=false PASS 0)。(d)新しい例3件=期待どおり2/2(例1 QUALITY、例2 ACCEPTABLE、K19 QUALITY)。(e)K16・K20(B4-a型)=2/2 BLOCKING(A2A3-0・B4-aは(a)で2/2 BLOCKING)。(f)負例K11・K12・K13=false BLOCK 0(2/2 ACCEPTABLE)。A4-1の原因切り分け(診断、n=1×7変種、¥2.1157、rubricの修正ではない): V7の(2)「自然な推論」の段落、または判定済みの例2行の、どちらか単独でA4-1をACCEPTABLEへ寄せる(`ablation_a41/`)。A4-1の対象文(`people who thought they were speaking with AI were actually speaking with human staff`と`That was what people thought as they spoke.`)は、ユーザー決定の例2・K23と同じ型であり、A4-1のSafety-critical(BLOCKING)ラベル自体が新しい線引きと食い違っている可能性がある(ラベルの扱いまたはV7の(2)の範囲はFable/ユーザー判断事項で、本委任は修正していない)。

**Production配線時の確認**: 本線引き・rubric V7・句読点差対策(`OPEN-233-A1-PROD`)は、Self-Recovery FlowのProduction配線時に`docs/pm/PM_GOVERNANCE.md` 11-3節の条件C(重要変更のProduction採用提案前のOpus独立技術レビュー)で併せて確認する。再較正の不合格(上記A4-1、委任_57で解消済み)が解消されるまで`PRODUCTION_WIRED`としない。古い日本語から英語を再生成するProduction経路(`er012_e_family_entertainment_two_level_runner_01.py`L361・365・403〜404、er019 entertainment runner L358〜397)は、再生成後のChecker(`run_deviation_check`)で必ず再検査されることを接続仕様に明記する(ユーザー決定2026-10-03、英語だけ修正する方針の維持)。

【2026-10-06 ユーザー決定・配線中】floorは数字(changed_number)のみに縮小、Checker新仕様(Ledger食い違い/具体的新事実/4観点照合)を正式採用。APPROVED_FOR_PRODUCTION、PRODUCTION_WIRED未(OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01)。正式仕様文は配線完了後に更新。【委任_04(2026-10-06)実装完了・E2E未】再分類(合流前filter、effort=medium固定)・`FLOOR_MODE=number_only`・`PRECHECK_MODE=number_only`・承認構成定数`OPEN233_APPROVED_FLOW_SWITCHES`をrunnerへ実装(既定は旧挙動、test 59件・回帰922件PASS)。PRODUCTION_WIRED未(E2E・runtime evidence後に判定)。【2026-10-06 9/20 run E2E完了(REPORT §81)】新仕様9 run E2E完走・正式集計済み(真の重大見逃し1/重大検出3、Human Review 0)、PRODUCTION_WIRED未(残11 runはユーザー総合レビュー待ち)。【2026-10-06 ユーザー決定・注記のみ】E2Eは9/20で一旦停止(残11 runは明示再開まで待機)、PRODUCTION_WIRED未。HC-012見逃しの直接原因は数字以外floor廃止ではない(旧floor全ONでも不発火、Fable訂正、REPORT §81-6/§81-10)。見逃し対策設計=OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(設計段階)。

### OPEN-233 時期の機械判定の追加確認による解放(案1を時期のみへ縮小、2026-10-04ユーザー正式判断[5回目=選択肢3]、`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`ではない、委任_60・委任_61)

**Status(委任_61更新)**: 追加確認による解放対象は**時期(`changed_time`)のみ**(2026-10-04ユーザー決定[5回目=選択肢3]、`APPROVED_FOR_PRODUCTION`、`DECISION_LOG.md`末尾エントリ)。**比較・方向(`changed_comparison`)・主体・数値・否定は決定論でBLOCKING維持**(1つでもtrueなら追加確認の対象外、理由コード`out_of_scope_flag:<flag名>`)。`prices began to fall`型の過剰Majorは受容(ユーザー決定)。委任_60の単体確認で方向反転S1が解放されたため、比較・方向は対象から除外した。自己修復機構本体がProduction未接続のため`PRODUCTION_WIRED`ではない。検証用runner(`er052_open233_self_recovery_flow_runner_01.py`)へ実装済み(スイッチ`FLOOR_VERIFY_MODE`既定`off`、CLI`--floor-verify-mode time_only`。旧`comparison_time`は廃止、指定すると`ValueError`)。単体安全確認PASS・V7b再較正PASS(下記)。少数flow確認・29件横断(1回)は次工程(委任_62)で、次Trial(10本)は禁止継続。

- **対象縮小の仕様(委任_61)**: 対象=Stage 2のLLM判定が非BLOCKINGで、`apply_floor`だけがBLOCKINGへ昇格させた指摘のうち、trueのfloorフラグが`changed_time`のみのもの。解放条件(追加確認2回とも非BLOCKINGかつ引用が関連factブロックの逐語)・BLOCKING固定条件(1回でもBLOCKING/API失敗/schema不一致/引用不備)・`dev`不変・2-of-2降格の除外・cycleごと再評価は委任_60のまま。比較用のCONFIRMED規則`floor_verify_comparison_numbers`は呼ばれない(未使用、関数のみ残置)。確認promptから比較・方向の記述を外した。
- **単体安全確認(`er052_open233_floor_verify_unit_check_02.py`、`er052_output/open233_floor_verify_unit_check_02/`、費用¥5.0099、69 call): **PASS(重大期待・対象外の解放0)**。重大期待5ケース×2版(決定論CONFIRMED版[確認callなし、5/5でBLOCKING固定]/非抽出版[確認callが実際に動く、各n=5×確認2回=10 call×5ケース=50 call、50/50がBLOCKING、解放0])。対象外確認: 方向反転(`changed_comparison`)と主体+時期は`out_of_scope_flag`で対象外(確認callなし、BLOCKING維持)。解放期待(参考値): B2 0/3・K15 1/3・K17 2/3(確認ラベルは18/18が非BLOCKINGだが、引用が逐語でない試行がBLOCKING固定となり、B2は3/3が固定=保守側)。**
- **V7b再較正(`er052_open233_element_trial_safety_control_06.py`、`er052_output/open233_safety_control_04/`、n=2、費用¥4.3753、24 call): **PASS**。(a)Safety-critical 5件の誤降格0、(b)Safety12 0/18、(c)Hormuz許容5/NG5はV6と同じ判定(false BLOCK 0・false PASS 0)、(d)例1=QUALITY・例2=ACCEPTABLE・K19=QUALITY(期待どおり)、(e)K16・K20=BLOCKING、(f)false BLOCK 0。**
- **整合(委任_61): 再較正はStage 2 rubric単体の確認で追加確認を含まない。単体確認(追加確認、時期のみ)と合わせ、「時期以外(比較・方向・主体・数値・否定)のfloorはLLM判定に関係なく決定論でBLOCKING維持」「時期は追加確認2回(逐語引用必須)で解放可能だが、重大期待ケースは確認でもBLOCKINGのまま解放されない」が両立している。V7bのStage 2判定は重大なものをBLOCKINGと判定する(a/b/e)ため、追加確認の前提(LLM=非BLOCKINGでfloorだけがBLOCKING)に該当する本物の重大ケースは、まずStage 2の段階で既にBLOCKINGである。**
- **以下は委任_60時点の記述(比較・方向を対象に含めていた旧仕様。委任_61で時期のみへ縮小したため旧)**:

- **仕組みの要点**: (1)対象=Stage 2のLLM判定が非BLOCKINGで、`apply_floor`(deterministic floor)だけがBLOCKINGへ昇格させた指摘のうち、trueのfloorフラグが`changed_comparison`/`changed_time`のみのもの。`changed_actor`/`changed_number`/`changed_negation`が1つでもtrueなら対象外(従来どおり決定論でBLOCKING確定)、precheck floorも対象外。(2)決定論の不一致確認(CONFIRMED、維持方向のみ): claimの日付・時刻・期間(time)/数値つき比較(comparison)が関連factブロックに無ければ確認を呼ばずBLOCKING維持。CONFIRMED以外も自動解放はせず確認へ進む(自動解放[文字一致・上昇/下落語の有無]は実装しない)。(3)追加確認: 対象claim 1件ごとに独立のcall 2回(`run_floor_verify_call`、Stage 2と同じモデル・設定、Checkerの指摘を「検証すべき仮説」として提示、`ledger_citation`逐語引用を要求)。(4)解放条件: 2回とも非BLOCKINGで、引用が関連factブロックの逐語であるときだけ、最終値=Stage 2と確認2回のうち最も重い非BLOCKING値。1回でもBLOCKING・API失敗・schema不一致・引用が空/非逐語・関連factブロックなし(確認不能)はBLOCKING固定。`dev`のフラグは書き換えない(`floor_verify`フィールドに記録)。(5)相互作用: 解放済みclaimは2-of-2の降格対象から外す、cycleごと・Recheck由来も同じ経路で再評価(解放状態を引き継がない)、既存のhook降格・disclosure_gap降格のガード条件は不変。
- **判定原則文の整合(V7b)**: V7(3)「数値・主体・否定・比較・時期の差は…明確にBLOCKING」を、基底R3(e)に揃え「数値・主体・否定・比較・時期について、Ledgerと矛盾する重大な変更(数値の改変、主体の取り違え、否定の反転、方向の反転、時期の取り違え)は…BLOCKING。方向・時期のニュアンスの差で事実関係の核心が保たれているものはこの限りではない」へ(`MISCONCEPTION_PRINCIPLE_TEXT_V7B`、V7は定数として残す。`BODY_RUBRIC_DEFAULT`=V7b。Production配線時用の`s2p._V7B_NEW_TIEBREAK`/`MATERIALITY_RUBRIC_V7B`は追加済みだが、runnerからは使われない)。再較正(`er052_open233_element_trial_safety_control_05.py`系)は**単体確認STOPのため未実施**。
- **動機の整理**(ユーザー指示§5、追加のユーザー判断なし): 動機の帰属(確認済みの事象に理由づけを添える)=軽微/動機の創作(台帳にない意図・仕組みを新事実として作る)=重大。設計書§0-2を更新、criteria docへ節を追加。V7(1)(イ)へ「仕組み・意図」は追加していない(既存より厳しくしない)。Stage 2 production rubricのQUALITY行「動機の帰属」は現行flowで未使用のため未変更(`OPEN-233-A1-PROD`の配線時整合項目)。
- **単体安全確認の結果(2026-10-04、`er052_open233_floor_verify_unit_check_01.py`、`er052_output/open233_floor_verify_unit_check_01/`、費用¥2.336、23 call)**: **STOP**。重大期待の合成ケースS1「After the plan was withdrawn, oil prices fell.」(HF-009、`changed_comparison`)が、trial2で確認2回とも非BLOCKING(QUALITY)となり解放された(受入条件「重大ラベルを1件でも解放したらSTOP」に該当。測定は打ち切り、修正は重ねていない)。解放期待ケース: K19=3/3解放、B4「Names…」=2/3解放、B2「vanished overnight」=0/3(引用が逐語でないためBLOCKING固定)。S2(K16型)以降は未実行。
- **Production配線時の確認**: 案1の追加確認・V7b・動機の整理は、自己修復機構本体のProduction配線時に、新しい線引き・句読点差対策・説明文混入の後段分離・英語だけ修正する方針と一体で追跡する(`OPEN-233-A1-PROD`)。単体確認がPASSするまで案1は有効化しない。

**Trial確認結果(2026-10-04、rep23/rep24、委任_62〜64、Fable照合判断。ユーザー決定ではなく、仕様本文は変更しない)**: rep23(少数実flow、6 instance×n=2、¥7.9137)・rep24(29件横断1回、38 instance-run、¥16.7238、Phase累計¥572.8515)を、承認済み対策(P-strict-closed=`APPROVED_FOR_PRODUCTION`[ユーザー決定[3回目]2026-10-04]・句読点差対策・英語だけ修正・時期のみの追加確認・V7b)をすべて有効にしたTrial専用構成で実施した。安全項目=PASS(真の重大見逃し0・重大ケースの誤解放0・日本語変更0・例外0。rep24 B3 s1の`residual_at_pass`残存はsentinelの位置目印のみで、因果「So」はcycle1でBLOCKING検出→「and」へ修正→cycle2 ACCEPTABLEと解消済み)。注意項目=不要Rewrite(rep24 21.43%でiteration 7と同率、neg3のBLOCKING claimはK16型でLLM・floor双方が重大判定のため不要と断定できない、neg3除外8.3%同率)・Human Review(STAGE4 7→2、いずれもSafety-criticalのfail-closed、B3 0/2→1/2は末尾`...`省略の照合不能で安全側)・過剰Major(Stage 2 BLOCKING 39→35、floor単独4→4、軽微以下の疑い3件はchanged_actorでユーザー決定[4回目]の受容範囲)。未発火項目=時期のみの追加確認・P-strict-closedの採用側は、rep23/rep24の実flowで発火機会がなく(対象claimはLLMも重大判定、またはfail-closed棄却)、解放側・採用側の実flow検証は未達(単体確認のみ)で、次Trialで観測する。自己修復機構本体はProduction未接続で、新しい線引き(V7b)・句読点差対策・説明文混入の後段分離(P-strict-closed、`APPROVED_FOR_PRODUCTION`)・英語だけ修正・時期のみの追加確認はいずれも`PRODUCTION_WIRED`ではない(`OPEN-233-A1-PROD`で一体追跡)。**次Trial(5記事×Standard/Advanced=10本)は開始しない(ユーザーGO待ち)**。ユーザー判断待ち: (A)Checker範囲の切断型の照合許容、(B)changed_actor floor単独の受容継続、(C)次TrialのGO。Closeout必須確認8項目の結果: `docs/pm/open233_closeout_check_2026-10-04.md`。

### OPEN-233 Trial Closeout・Production正式採用(2026-10-05ユーザー決定、`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`)

**Status**: 対象仕様=`APPROVED_FOR_PRODUCTION`(人間ユーザー決定)。**`PRODUCTION_WIRED`ではない**(配線の完了条件1〜12達成後のみ)。ユーザー決定原文(逐語)・Fable評価は`DECISION_LOG.md`の2026-10-05エントリ(`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`)が正本。

- **Trial結果**: rep30 `VALIDATED(条件付き: Stage 1はfrozen再利用31 run/V0差替え3 run/fresh 3 call[4 run]。E2E Safety KPIではない。出典`docs/pm/rep30_stage1_provenance_01.md`)`(29ケース・38 run・Human Review 0・重大見逃し0・平均¥0.573/run・rep24比+¥0.13/run・不要Rewrite 3/14、worst +¥3.135[1/38 run、報告対象])。
- **採用対象**: ユーザー列挙22項目(`DECISION_LOG.md`参照)+rep30有効構成のスイッチ全体:
  - HANDOFF_MODE=violation_span / VS_MATCH_EXT / VS_EXPLAIN_SPLIT(+Q, U-2(1)) / JA_MODE=english_only / V7b / FLOOR_VERIFY_MODE=time_only
  - VS_SENTENCE_RESTORE(L6、focus_absentは本文全体判定) / CAUSAL_FLOOR known6+issue_actor / STAGE2_SECOND_OPINION(S1) / RECHECK_MERGE_UNRESOLVED(N1') / STRUCTURAL_ELEMENT_REWRITE / STRUCTURAL_PAIRS_TO_RECHECK
  - ACTOR_GUARD_MODE=ag1_strict+related_fact欠落時Ledger全体fallback+同義語表 / 件数一致index別集約 / prior_issues現行本文
  - STAGE4_ALLOWLIST / LADDER_LOCATION_CARRY(B') / REWRITE_REVERT_GUARD(A2) / SPAN_FALLBACK_CHAIN(D+carry list) / JUDGE_ONLY_CYCLE_AFTER_CAP(G) / LAST_RESORT_DELETE(T)
  - MATERIALITY_BLOCKING_PIN / STAGE2_VERDICT_REUSE_NONBLOCKING / STAGE2_SIBLING_LOCATIONS_CYCLE1 / degenerate是正
- **配線しない(REJECTED/OFF)**: F1(品質regen条件の緩和) / 確認役(STAGE2_DOWNGRADE_VERIFY) / N3'(RECHECK_BEFORE_AFTER_PAIRS) / G_L(TIER0_G_L_ENABLED) / NORMAL群2-of-2(STAGE2_NORMAL_TWO_OF_TWO) / CAUSAL_FLOOR_VOCAB=inventory / A1 / C / E1 / E2 / F2。
- **Cost KPI(2026-10-05更新)**: 平均追加費用を主要KPIとして継続監視(基準不変)。1記事/runで¥3超は必ず報告・記録。¥3超だけを理由に自動STOP・KPI FAILとはしない。従来の単発+¥3/記事Capは撤回。
- **残る正当なHuman Review経路(許可リスト4種)**: blocking_confirmed_unlocatable_after_cap / blocking_structural_after_ladder / post_T_new_blocking / api_failure。
- **合流・運用**: 既存`OPEN-233-A1-PROD`束は本決定の採用対象に合流。追加N増しTrialは行わず、Production運用中の問題は個別改善する。
- 詳細: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §63。

### OPEN-233 Self-Recovery Production Flow仕様(`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`は完了条件1〜12達成後、2026-10-05、委任_09、`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`)

**【2026-10-05追記(委任_18)KPI例外】Cost KPI(平均追加+¥2/Standard+Advanced 1セット以内)のみ、今回のOPEN-233についてユーザーが例外承認した(`DECISION_LOG.md` 2026-10-05「E2E-ACCEPTANCE-01」の理由1〜5を参照、本管理ID限定)。Safety KPI(重大Fact見逃し0件)とHuman Review/USER_DECISION_REQUIRED 0件は不変。Cost未達は解決済みとせず`OPEN-233-COST-REDUCTION-01`で継続。E2E PASS時の到達Statusは`VALIDATED`まで(Production未反映、`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`の自動付与なし)。**

承認済み内容(`DECISION_LOG.md` 2026-10-05ユーザー決定、`docs/pm/production_wiring_gap_open233_01.md` §1/§7 Fable評価、`docs/pm/opus_l2_review_open233_production_wiring_15.md`[Opus#15])のみを記す。新仕様ではない。**未配線**(Production未変更)。詳細・根拠: `docs/pm/production_wiring_report_open233_01.md`。

1. **位置づけ・入口条件**: Production正式初回path(Ledger+英語本文+日本語本文+family profileを入力とする)。Feature flagで制御、Production初期値OFF、family単位で有効化、順序はP3/P4→P5→P1/P2。P6は配線対象外(監視専用)。(Opus#15論点10、Gap文書§7)
2. **Stage 1 Checker**: A構成(`gpt-6-luna`+rep30 frozen出力を生成したV4A系構成、CORRECTION-02)。**詳細定義は委任_08の`docs/pm/rep30_stage1_provenance_01.md` §7で確定後に転記(プレースホルダ)**。**【2026-10-05追記(委任_18、E2E-ACCEPTANCE-01)】上記プレースホルダは「Trial E2E最終確認中(Stage 1=coverage_union: r3 medium+r5 high+否定案a、Recheck=変更単位+前後1単位+出口3'-R全文、Production未反映)」へ読み替える。Production仕様としての確定はfresh E2E PASSとユーザーのProduction採用承認後(`OPEN-233-SPEC-STAGE1-PLACEHOLDER-01`)。**昇格ルール(`severity_final`)は選別に使わない。`severity=="MAJOR"`のみStage 2へ渡し、MINORは渡さない。Stage 1が非検出でもprecheck結果をログする。(Opus#15 F2、DECISION_LOG 2026-10-05)
3. **Model/Routing**: Self-Recovery経路(Stage 1/Stage 2/S1/floor_verify/Rewrite/Recheck)は`gpt-6-luna`。Model Routing Contractに新processを追加し`require_model`経由で呼ぶ。モデル不可時はfail-closedで`api_failure`とし、`gpt-5.6-luna`へ自動切替しない。Writerは不変。(Opus#15 K7)
4. **Stage 2 materiality**: V7b(正本=`er052_open233_self_recovery_stage2_calibration_01.py` `RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B` L612。`stage2_production` moduleの`MATERIALITY_RUBRIC_V7B`は別物で使わない)。決定論floor 5種+因果known6+issue_actor。時期(time_only)のみ追加確認2回の逐語一致で解放(FLOOR_VERIFY_MODE=time_only、2026-10-04決定)。S1第2意見は2回一致で降格、割れたらBLOCKING(`floor_verify`で解放済みclaimは除外)。BLOCKING固定(本文不変なら再判定で覆さない)。非BLOCKINGの2-of-2一致は再利用(span集合完全一致のみ)。兄弟箇所(同fact_id)は決定論列挙し、cycle 1のStage 2 batchへ入れる(Rewriteへは渡さない)。「AI1回で重大→問題なし」となる構造は禁止。(Opus#15論点10)
5. **span解決**: L0〜L6、P-strict-closed(2026-10-04ユーザー決定[3回目])、句読点差許容、説明文混入の分解(Q/U-2(1))、L6完結文復元(focus_absentは本文全体判定)。prior_issuesは現行本文を使う。
6. **Rewrite ladder**: 水準①語句・③文・④段落(⑥はOFF)。english_only(日本語本文は不変)。actor_guardはAG1-strict+related_fact欠落時Ledger全体fallback+同義語表。構造要素はdelete禁止→書き換え。位置座標の引継ぎ(B′: 同一箇所の再BLOCKINGで前levelの上位から開始)。振動検出(A2、REWRITE_REVERT_GUARD)。degenerateは試行失敗として一段上へ昇段。
7. **Recheck**: 全文Recheck。N1′(未解消priorは次cycleのStage 2へ渡す)。件数一致index別集約。構造要素はbefore/afterを対にして渡す(STRUCTURAL_PAIRS_TO_RECHECK)。carry list: 位置特定不能BLOCKINGは書き換えず位置を再取得し、listが空でない間はPASS禁止。
8. **cycle定義**: MAX_CYCLES=2+条件付きcycle 3。上限後は判定専用cycle(Stage 2+S1、Rewriteなし、JUDGE_ONLY_CYCLE_AFTER_CAP)。T(最終手段=構造要素以外の該当文delete+全文Recheck、1記事1回)。Tを含め本文変更が計4回になりうる(Opus#15 K1、開示事項)。
9. **Human Review出口(許可リスト4種)**: `blocking_confirmed_unlocatable_after_cap` / `blocking_structural_after_ladder`(構造要素∧ladder④実試行の検証付き) / `post_T_new_blocking` / `api_failure`。sub_reason必須(`t_already_used`/`t_delete_failed`/`t_disabled`/`cap_no_t`等)。4種以外はAssertionErrorで安全側STOP。familyごとの終端への写し方: P1/P2は`RuntimeError("[STOP] <reason>")`、P3/P4は`NG_REVIEW_REQUIRED`、P5は戻り値flag。(Opus#15 Safety hole 3、論点10)
10. **Family X固有**: Self-Recovery経路ではmust-fix全文再生成を廃止。ladder④/T後に`split_family_x_article_text_v2`の段落数ガードを行い、NGはRewrite不成立として ladderを一段上げる。逸脱チェック前の段落数retryは残す。`JARecheckRequiredError`はenglish_only+全文Recheck必須に置換(ja_source件数を監査ログでmonitor)。**開示**: 日本語側の誤りは残る(K4、Opus#15)。
11. **retry/fallback/regeneration**: 新本文は同じ入口へfresh Stage 1から入り直す。全文再生成時は位置履歴とT使用回数をリセットする。費用は累積して報告する。
12. **Trial依存禁止**: Production module(新規`er0XX_self_recovery_flow_01.py`、番号は実装時に採番)は`er050`/`er051`/`er052_*`をimportしない(`git grep`で機械検査)。Trial runnerの新moduleへの切替は別タスク。
13. **Cost KPI**: 平均追加費用+¥2/記事以内(KPI値不変)。Productionでの「追加」の基準=現行Production 1記事費用(委任_04c算出: JA側Checker+loop 平均¥2.77/中央値¥2.50、n=8。EN側Checkerは未分離=未確認)。¥3超のrunは必ず報告・記録し、¥3超のみで自動STOP/FAILにはしない(単発Capは2026-10-05撤回)。
14. **配線しない(REJECTED/OFF)**: F1 / 確認役 / N3′ / G_L / NORMAL群2-of-2 / CAUSAL_FLOOR_VOCAB=inventory / A1 / C / E1 / E2 / F2 / CHECKER_SPANS_MODE=violation_spans / Trial計測専用コード。
15. **完了条件1〜12**(`DECISION_LOG.md` 2026-10-05ユーザー決定が正本): (1)Production正式初回path配線 (2)retry/fallback/regeneration整合 (3)Trial専用依存なし (4)Production runtime evidence (5)Regression/integration PASS (6)actual routing/model確認 (7)CURRENT_SPEC更新 (8)DECISION_LOG更新 (9)OPEN_ITEMS更新/close (10)Git commit/push (11)ユーザー承認内容とProduction挙動一致 (12)Dangling Referenceなし。1つでも欠ければ`APPROVED_FOR_PRODUCTION`のまま。**runtime evidence計画(Phase 2)**: 既存テーマの再生成+STOP実例+P3/P4/P5各1+Safety fixture 3+クリーンPASS 1件以上+¥0 fixture。新規記事は不要。

## ユーザーテストWeb表示仕様・配信経路(2026-09-18新設、USER-TEST-SCRIPT-READABILITY-PROD-01/USER-TEST-HOSTING-GITHUB-PAGES-01)

**表示仕様**: Key Phraseハイライトは`user_test/unified.html`の
`applyKeyPhraseHighlight`が`kp_mapping.json`の`matched_text`を大小文字・
apostrophe種のみ許容する決定論的完全一致検索で本文(`p.script`)に適用し、
水色`mark.kp-hl`(`#dff2fb`)で表示する。表層差(語形変化・人称一般化等)が
ある場合は`mapping_type`(exact/tense/inflection/function_word等)に
分類し、`matched_text`は常に本文の実際の表記に追従させる(Key Phrase
一覧の見出し語[`phrase`]と本文表記が乖離してもハイライト側は本文優先。
分類定義2026-09-18確定: exact=文字列として実出現形と一致/non-exact=
時制・活用・人称一般化等により表層形が異なるがsource対応が一意に確認
できるもの/unresolved=対応不能・曖昧。全100 Key Phrase実測: exact74・
non_exact26[tense14・function_word7・inflection5]・unresolved0)。
日本語訳は`translation_ja.json`から`.trans-section`として描画し、
Standardの既存Comment再掲(`type: reprint`または
`existing_comment_repost`)はグレー(`color:#5b6472`/
`background:#f2f3f5`)+「既存Comment(再掲、翻訳ではありません)」ラベル
付きで表示、Advancedの英語Commentは通常の翻訳文として表示する。
Status: `PRODUCTION_WIRED`(2026-09-18、USER-TEST-SCRIPT-READABILITY-
PROD-01、20 level全件で公開runtime E2E確認済み)。

**配信経路**: ユーザーテストWeb Hosting=**GitHub Pages**
(`https://shimomura055.github.io/eigo-radio/`、リポジトリ`main`ブランチ・
root配信、`.nojekyll`あり)。**GitHub Pagesはユーザー自身の操作により
有効化された(ユーザー確認済み事実、2026-09-18、`PM-GOVERNANCE-
DISTRIBUTION-PATH-PAGES-01`)**。Source/Branch設定の実施時期・詳細設定
内容そのものはSSOT未記録だが、稼働確認は2026-09-18時点で完了している
(`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01_pages_precheck.md`
参照)。正式入口URL(stable、
commitごとに変更不要)=
`https://shimomura055.github.io/eigo-radio/user_test/articles_2026_0918.html`。
個別記事URL=
`https://shimomura055.github.io/eigo-radio/user_test/unified.html?src=<src>&level=<lvl>&en=<en>&ja=<ja>`
(固定SHA不要、常に最新main。実測deploy遅延: push→反映まで約83秒
[2026-09-18実測、commit`ddad09a1`]、`Cache-Control: max-age=600`により
更新直後最大10分程度のCDNキャッシュが残る可能性あり)。
`rawcdn.githack.com`/`raw.githack.com`は正式ユーザーテスト配信経路として
使用しない(過去commitの証跡としてのみDecision Log等に残存する)。
Status: `PRODUCTION_WIRED`(2026-09-18、USER-TEST-HOSTING-GITHUB-PAGES-01、
判定条件[Pages runtime E2E全PASS・rawgit警告0件・Dangling Reference
Check PASS・canonical sha256無変更]を全て充足した場合のみ。詳細:
`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`の`## Phase E`節)。

## Topic Selection量産初期運用方針(Production仕様ではない、DECIDED / OPERATING_POLICY_ONLY、2026-09-25ユーザー決定)

管理ID: `TOPIC-DISCOVERY-MANUAL-SELECTION-OPERATING-POLICY-01`(記録のみ、
Production Search実装・自動選定ロジック・フォームUI・rerank実装は一切
含まない)。既存`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`・
OPEN-178/179・既存Topic Discovery Trial結果を上書きしない。

1. **完全自動化は未実施**: AI単独のTopic Selection精度が未安定なため、
   数十件の教師例でPromptを複雑化せず、実運用で数百件規模のユーザー
   選定データを蓄積してから自動化精度を高める。
2. **量産初期の基本フロー**: AIが複数の定点Sensorサイトを巡回→各サイト
   原則3記事程度+日本トップ3件+世界トップ3件を候補へ→AIが候補ごとに
   Hook/仮タイトル・概要・切口を提示→ユーザーがフォーム等で10記事程度を
   選定→AIが記事生成。ユーザー対応不可時はAI自動選定fallbackを将来
   用意する。選定実績を蓄積し十分なデータ後に完全自動化を再検討する。
   フォーム仕様・実行タイミング・自動化条件は未設計。
3. **学習データ**: 選択された候補(Positive)と、候補に出たが未選択
   (Negative)の両方を保存する。数百例蓄積後に改善する。
4. **Sensorサイト候補**(Poolは今後変更可、恒久固定仕様ではない): 海外
   404 Media/Oddity Central/PsyPost/Axios/Semafor/Ars Technica。国内
   GIGAZINE/ナゾロジー/デイリーポータルZ/カラパイア/Togetter/
   ITmedia NEWS/東洋経済オンライン。除外済み: Know Your Meme/
   まいどなニュース/Jタウンネット。
5. **候補抽出の優先順位**: 優先1はサイト自身の人気・注目シグナル
   (24時間ランキング/Access Ranking/Most Read/Popular/Editor's Pick/
   Top Stories等)を入口にする。優先2は無ければAIが直近記事から判断
   (Hookの強さ/一般読者への広さ/Self relevance/「え、そうなの？」感/
   自然なAngle展開/話したくなるか/日本人読者との接点/教育的説明で
   終わらないか)。人気ランキングをそのまま採用せず、その中から
   eigo-radio向け候補を選ぶ。
6. **直近性**: 原則直近24時間中心。更新頻度が低い媒体・Evergreen媒体・
   非常に強い題材の扱いは後日。厳格な24時間ルールをProduction仕様として
   固定しない。
7. **タイトル/Hookの固有名詞方針**: 不要な固有名詞を避ける(例: freeeが
   止まったら？→給料日に会計ソフトが止まったら、会社はどうなる？/
   美味しんぼの海原雄山→昔の人気漫画の"厳しい名物キャラ"、今なら
   カスハラ？/GoogleがAIデータセンターを宇宙へ→AIデータセンターは、
   ついに宇宙へ行く？)。理由: 固有名詞を知らない読者は自分に関係ないと
   判断しやすい。完全禁止ではなくTrump/ChatGPT/iPhone/大谷翔平のように
   広い認知・集客力がある場合は可。判断原則: その固有名詞を知らなくても
   Topicの魅力が伝わるか。
8. **Topic Discovery思想**: 記事は完成TopicではなくSeed。Source発見→
   面白いAngle→必要なら追加検索→一般人との接点→Hook/Topic Package化。
   記事タイトルをそのまま採用しない。Big News→自分事へ/科学→驚き・
   人間との接点へ/Tech→技術説明ではなく生活変化へ/SNS→Fact Sourceでは
   なくTopic Sensor/小ネタ→可愛い・珍しいで終わらずWhyへ。
9. **日本/世界トップニュース枠**: 毎回日本3件+世界3件を候補に追加し、
   Sensorサイトの取りこぼしを補完する。Big Newsもそのまま採用せず
   「なぜ一般人に関係するのか」までAngle化する。
10. **今回確認できた好例12件**(固定ルールや少数Teacherだけで過学習
    させない): 悪い言葉でも、笑えると集中を邪魔しなくなる？/人は
    「いいね」より「イマイチ」に流されやすい？/自己主張が強い人ほど
    リーダーになる。でも実力とは別？/憧れの車中泊、実際にやったら
    一睡もできなかった？/イランは戦争を終わらせる道筋を米国に示した？/
    40年間禁止だったサッカー観戦中のビールが復活する？/アルツハイマーの
    兆候は、検査で見つかる7年前から脳に出ている？/量子コンピュータが
    来る前に、暗号をもっと速く破る方法が見つかった？/火事なのに、鳥は
    炎へ向かって飛んでいく？/金星は、自分の月を食べてしまった？/
    AIデータセンターを宇宙へ？/80歳まで住宅ローンを払うのが普通に
    なる？。
11. **未決**(勝手に仕様化・実装しない、詳細はOPEN-180): フォーム具体
    設計/入力タイミング/候補件数の正式値/選定件数の正式値/自動選定
    fallback条件/完全自動化へ移行する件数・基準/Sensor巡回頻度/
    24時間条件の厳密性/人気ランキング取得方式/保存schema/自動学習・
    rerank実装方式。

## 参照元

[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)、
[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)、
[ER-003-REPRO_BASELINE.md](ER-003-REPRO_BASELINE.md)、
[ER-003_PIPELINE_CROSS_CUTTING_RULES.md](ER-003_PIPELINE_CROSS_CUTTING_RULES.md)、
[ER-003-B1_P8A-P9A_AUDIT_REPORT.md](ER-003-B1_P8A-P9A_AUDIT_REPORT.md)、
[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)(A2の検証経緯、CURRENT_SPEC昇格後は履歴記録として保持)、
[ER-003-CROSSLEVEL-AUDIO-01_REPORT.md](ER-003-CROSSLEVEL-AUDIO-01_REPORT.md)、
[ER-003-CROSSLEVEL-AUDIO-02_REPORT.md](ER-003-CROSSLEVEL-AUDIO-02_REPORT.md)、
[ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md)、
[ER-003-CROSSLEVEL-AUDIO-04_REPORT.md](ER-003-CROSSLEVEL-AUDIO-04_REPORT.md)、
[ER-003-A2-AUDIO-AB-01_REPORT.md](ER-003-A2-AUDIO-AB-01_REPORT.md)、
[ER-003-A2-SPEC-FREEZE-01_REPORT.md](ER-003-A2-SPEC-FREEZE-01_REPORT.md)、
ER-003-B1-NOVEL-AUDIO-01系レポート(Support English化・Voice役割再配置)、
ER-003-A2-B1-N3-01完了報告(3ジャンル横展開: Hanshin/Health/Household)、
ER-003-A2-B1-N3-01-FIX-01完了報告、ER-003-N3-RCA-01完了報告、
ER-003-N3-ROOT-FIX-01完了報告(Key Phrase trim margin・TTS instruction責務分離・A2 Core Logic Preservation)、
ER-003-N3-ROOT-FIX-VERIFY-01完了報告(3ジャンルでのA2 Core Logic Preservation検証)、
ER-003-B1-A2-SPEC-FREEZE-01-R1完了報告(SoT内部整合性クリーンアップ)、
ER-003-B1-B2-SCOPE-FIX-01完了報告(B1生成仕様確定・B2 Launch Scope整理)、
ER-006-AUDIO-COST-OPTIMIZATION-01完了報告(Batch/Master Audio/ASR代替の調査)、
ER-006-AUDIO-COST-PILOT-02完了報告(ASR Provider Routing・Master Audio最小実装)、
ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01完了報告(発音Ledger・Secondary ASR)、
ER-006-AUDIO-RETRY-CASCADE-PROD-01完了報告(Cascade Production配線)、
ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01完了報告(Validator一般化・Cost再構築)、
ER-006-AUDIO-COST-SPEC-FIX-01完了報告(本節・Model Routing Contract更新のSSOT統合)、
ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01完了報告(Gemini TTS Batch API実配線・ASR旧記述整合化)、
[DECISION_LOG.md](DECISION_LOG.md)
