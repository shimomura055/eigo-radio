# Opus独立技術レビュー: OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01(条件A、2026-10-06、read-only、¥0)/対象: docs/pm/design_open233_floor_selectivity_01.md/Fable判断は末尾

## (1) 結論

対策は必要。ただしfloorだけを変える設計(案1〜5)は根本対策として不十分。不要24件の中心は(i)の17件で、Stage 1が`changed_*`フラグを付けたこと自体が誤り(Ledgerに対応記述が無い=absenceなのに"変更した"フラグを付けている)。

- 【確認】Stage 1フラグ定義(coverage_checker L193-203)は「Ledgerと異なる値にする/反転」=変更前の値がある前提。
- 【確認】R3 promptは「少しでも疑いがあればCANDIDATE」(L208, L225)で、absenceなら`unsupported_new_claim`だけを付ける規則がない。
- 【確認】Production checkerの`HOOK_CLAUSE`(er003 L570-599)に相当する緩和がcoverage checkerにない→比喩・修辞・「not X but Y」がcomparison/negationとして発火(RCA L29)。

根本原因はフラグ生成側、floor側は二次的。

doc分析の構造的弱点【確認】: `issue_type`はLLMの日本語issue文を正規表現判定(script L84-100)、`CONTRA_RE`が広すぎる/(i)(ii)振り分けも正規表現のみ(L207-215)/原因(iii)=0は`assign_cause`に分岐がないため構造的に0。

## (2) 推奨構造「cite-to-fire」

発火条件を「Ledger側に変更された対応値が実在すること」にする。

- 数字=現行決定論維持(正当3/4)。
- 時期=承認済み`time_only` verify(L2759, L2868-2885)をそのまま使用。
- 主体・否定・比較=Stage 1が変更されたLedger記述を逐語引用できた場合だけ発火、引用実在は決定論検証、引用不能は`unsupported_new_claim`としてStage 2判定に任せる。
- 【確認】既存`apply_floor_cited`/`floor_cited_eligible`(L2443-2502、委任_14 B-2)が反実仮想記録として¥0実装済み、新部品不要。
- 【推測】ただし現行は英語4文字以上の語の重なり判定で、Ledgerが日本語のため数値以外はほぼ一致しない可能性→保存済み記録値をreplayで先に評価。
- 因果(Tier0)の「so」1件は語彙設計の別問題。
- 1/3達成見込み【推測】: (i)17件が外れれば約17件で半減、1/3はfloor単独では不明、RECLASSIFY-02の候補減と合わせて評価。
- 目標再確認: 誤BLOCKINGの害(不要Rewrite・追加cycle、Stage 3費用8runで¥6.1)と誤解放の害(Safety喪失)は非対称→件数目標よりgold取りこぼし0を優先。

## (3) リスクR1〜R3

- R1: 根本原因はフラグ生成側。doc §2「Checker候補過多とは独立」は仕組みの説明として正しいが件数には当てはまらない(35件はr3候補過多が母数、RCA L40)。
- R2: 案1/5は個別当て込み(LLM issue文の正規表現・英語anchor正規表現・HC-011専用規則[script L147]・固有名詞除外リスト)。【確認】doc自身のhold-outが§4/§5「案1は6/6維持」に反する: SC gold b1b(No.23と同文)はin-sampleでは強制重大だがhold-out(rep30)ではLLM非BLOCKING・issue_type unclearで案1は非強制(集計md L69)=見逃し。LLM文言の揺れで判定反転=非決定性増。さらに案1は時期を承認済みverifyに通さず非重大化し現行より安全性低下。
- R3: 【確認】案2で追加確認へ回る正当はNo.5とNo.23(集計md L24, L36, L54、doc §5の「No.21」は誤り)。No.23はLLM BLOCKINGのため`floor_verify_target`対象外(L2878)で残る→実際に危険はNo.5の1件。verifyはStage 2と同じモデル(L3010)で誤りが相関、委任_61で方向反転がverifyで解放され比較を決定論へ戻した経緯(L2760)→主体・比較へverify拡張は塞いだ穴の再開。
- 案4のS1【確認】: 対象「非BLOCKING∧MAJOR∧未解放」(L4026-4033)、coverage checkerはseverity常にMAJOR(L909)→事実上非BLOCKING全件。S1は2回目BLOCKINGなら重大へ戻す(L4073-4083)が同rubric再サンプル(L4055)に過ぎず、No.5/21を拾えるのは揺れ分だけ【推測】。案4は正当6件中2件を失いうる。S1はTrial専用・既定OFF(OPEN_ITEMS L727(4))。非推奨。

## (4) リスクR4〜R6

- R4: 【確認】OPEN_ITEMS L727「比較/方向/主体/数値/否定は決定論維持」。案1/5は決定論のまま発火範囲を狭める=承認済み挙動の縮小で実質的に線引き変更、ユーザー承認要。案2/3/4は明確に線引き変更。cite-to-fireも発火条件変更で承認要。Stage 1 prompt/schema変更はRCA案D相当で承認要。
- R5: RECLASSIFY-02を先に評価すべき(母集団・フラグ分布が変わり本docの件数は無効になりうる)。【推測】RECLASSIFY-02の「Ledger食い違い/具体的新事実」区分はcite-to-fireとほぼ同じ問い→「Ledger食い違い」候補だけでfloor発火すればfloor側に新規則不要の可能性。
- R6: 「複数フラグ同時true」は不採用【確認】(複合4件No.6/16/19/27は全て不要ラベル)。RCA案C(verify拡張)はR3のとおり。最小変更はcite-to-fire。

## (5) 代替案(優先順)

1. RECLASSIFY-02区分をfloor発火条件に使う(時期以外は「Ledger食い違い」候補でだけ発火、既存データ再利用、新LLM処理不要)。
2. cite-to-fire(Stage 1 schemaに変更されたLedger記述の逐語引用を追加、実在を決定論検証)。
3. Stage 1 prompt補正(RCA案D: absenceは`changed_*`を付けず`unsupported_new_claim`、Hookの扱い明記。recall測定要、OF-001)。

案1/5と案4は推奨しない。条件A該当。

- ユーザー承認要: (a)floor発火条件の変更すべて、(b)Stage 1 prompt/schema変更、(c)有料Trial。
- 承認不要: 時期の承認済みverify流用、¥0 replay。

## (6) 限定Trial案への意見

段階0(¥0)を先に:
- (0a)35件とRECLASSIFY-02保存出力を突き合わせ残件数と区分ラベル確認。
- (0b)保存instance結果の`apply_floor_cited`反実仮想値を35件+SC gold全件で集計。
- (0c)合否はSC gold/hold-outのgold取りこぼし0を最優先、35件推測ラベルは副次指標。
- (0d)正当6+判断不能5(計11件)のラベルをFable/ユーザーが確認。

段階1(有料)はverify拡張(案2)選択時のみ(委任_61方向反転再現ケースとNo.5を必須合否)。cite-to-fire/Stage 1変更選択時は段階1を「Stage 1再実行+gold recall測定」へ置換。

順序: RECLASSIFY-02評価→段階0→設計確定→ユーザー承認→段階1。

参照: runner L779, L2432-2502, L2759-2761, L2868-2885, L2984-2999, L4023-4088/coverage_checker L193-231, L909/er003 L570-599/rca L29, L40, L61-73/OPEN_ITEMS L727。未読: RECLASSIFY-02 design・REPORT §78、`apply_floor_cited`値の実記録有無。

## Fable判断

「Fable判断(2026-10-06、Opus条件Aレビュー後): Status=USER_DECISION_REQUIRED。根拠: (1)Sonnet案(最有望=案2+案5、根本原因=floor側の重大性判定不在)とOpus(根本原因=Stage 1 `changed_*`フラグ生成側のabsence/contra混同、案1/5は正規表現による個別当て込みで過適合、案4は正当2件を失いうる、推奨=RECLASSIFY-02区分のfloor発火条件への流用>cite-to-fire>Stage 1 prompt補正)で重要な結論が対立。(2)Fable検証【確認】: hold-out(rep30、集計md L69)で案1はneg3 gold(時期floor・LLM非BLOCKING)を非強制=見逃し(案1 6/6維持はin-sample限定)/集計scriptの`assign_cause`(L207-215)に原因(iii)分岐がなく(iii)=0は構造的/doc §5のNo.21記述は表(No.23)と不一致。(3)案1〜5・cite-to-fireのいずれも承認済み線引きOPEN-233-A1-PROD(`APPROVED_FOR_PRODUCTION`・未配線、時期のみverify・比較/主体/数字/否定は決定論維持)の変更に当たりユーザー承認事項=ユーザー指定STOP条件『Production仕様変更が必要』に該当。(4)floor側のみの精緻化で正当6件を守りつつ半減する見込みは、in-sampleでは案1/5=14件だがhold-outで1件見逃しのため未確立。Fable評価: Opusの根本原因指摘(フラグ生成側)と順序(RECLASSIFY-02評価→¥0段階0→設計確定→ユーザー承認→有料段階1)を妥当と判断し、ユーザーへ提示。Production未変更、有料Trial未実施、gold不変。」
