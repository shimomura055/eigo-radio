# ユーザー判断資料: OPEN-233 Stage 1 ループ2停止(委任_15、2026-10-05、¥0)

管理ID OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01。Status=`USER_DECISION_REQUIRED`。Trial(DEV)、Production未変更、`APPROVED_FOR_PRODUCTION`ではない。E2E(最終出口まで通した全体評価)は未実施。累計費用¥139.71/枠¥238(残¥98.29)。

## §1 到達点(KPI 3項目 x 測定経路[provenance] x 結果)
| KPI | provenance | 結果 | E2E値か |
|---|---|---|---|
| Human Review 0件 | 未測定(E2E未実施) | 値なし。Opus#17指摘どおりBLOCKING率0.10(n=2/20)は過小の疑いで見込み値として使わない | No(未測定) |
| 重大Fact見逃し0(Safety、gold 6件) | fresh(Stage 1のみ、G arm 33 run=r3 medium+r5 medium+否定案a)。Stage 2以降は未通過。混合構成(r3 medium+r5 high)の値は段階A保存結果(frozen、high)からの推測 | r3 M 16/18合格、r5 M 15/18未達(A4-0 0/3)、∪M 17/18(A4-0の1/3を両経路が見逃し)、hold-out 9/9、neg5 3/3、欠落ID 0%。混合構成∪18/18は未fresh測定(推測) | No(Stage 1限定の条件付きKPI) |
| Cost 平均追加+¥2/記事以内 | Stage 1=fresh実測(medium/medium ¥0.843/run、high同mix ¥1.394/run)+混合は合算推測¥1.23/run。Stage 2=線形fit(候補0〜10)の外挿=推測 | (iii)見込み: 差し引き0で+¥2.06〜2.7(Stage 1+Stage 2のみ)、Rewrite等を加え差し引き上限¥0.55でも≈+¥2.1〜3.0(Fable判定値)=未達の見込み | No(推測、E2E未測定) |

## §2 費用構造
- Stage 1(同一33 run mix、fresh実測): r3 high ¥0.609→medium ¥0.447、r5 high ¥0.785→medium ¥0.395、合計 high ¥1.394→medium ¥0.843。採用構成(r3 medium+r5 high)は合算推測 ¥0.447+¥0.785=約¥1.23/run(high/high比-12%、-¥0.16/run)。主因はoutput token約9割(r5 reasoning 68%)。
- 候補数: NORMAL候補∪=21.83/記事(r3 21.5、r5 6.5。案a後の見込み20.0、段階A 24.0)。
- Stage 2(ユーザー承認済み構成、不変): 費用は候補数比例。1件≈¥0.064+固定≈¥0.1。候補21.8件で≈¥1.5、fit範囲内の10件でも≈¥0.83(Fable記載値)。
- (iii)見込み計算(推測): Stage 1 ¥1.23 + Stage 2 ¥0.83〜1.5 = ¥2.06〜2.7。これは差し引き0(V4A実費を差し引かない)の場合で、Rewrite・Recheck・出口3'-R全文(Rewrite発生記事のみ約¥0.45、平均約¥0.22)を加える前の値。差し引き上限¥0.55(V4A実費仮置き¥0.12〜0.55の上限)を適用しても、後段加算を含めFable判定では≈+¥2.1〜3.0(後段加算の内訳は再計算していない、E2E実測で確定する)。
- E2E計画書の1 run見積(推測): 約¥3.1/run(2.4〜4.3)、rep30実測¥0.57/run。

## §3 試した手段と結果
| 手段 | 結果 |
|---|---|
| coverage_union(r3 3'-R+r5 5-lite、2経路和集合)+F3/H1 | 検出構造は成立(∪M 18/18はhigh時)。ただし費用がStage 1 ¥1.39/run(high) |
| 否定案a(否定検査の誤発火是正) | 決定論149件→9件、真の極性不一致0。NORMAL候補24.0→約20。採用 |
| r5-V(r5をr3のSUPPORTED単位のみ検証に縮小) | 能力テストM 10〜12/18(基準17/18未達)。費用は0.14〜0.29/runで安いが検出が不足、不採用 |
| G(reasoning effort引下げ) | r3 mediumは合格(16/18)で採用。r5 mediumはA4-0 0/3・M 15/18で不採用(highへ戻す)。lowは未実施(medium未達のため情報価値小) |
| (A)2層化(triage) | 分析のみ(Opus#17)。削減はNORMAL約¥0.47のみ、triageが第2のStage 1化。ループ2では主軸不適、条件付き保留 |

## §4 選択肢
| 選択肢 | 内容 | 費用 | 期間 | リスク | 得られる情報 |
|---|---|---|---|---|---|
| 【A】先に基準を決めて止まる | いまSTOPし、(1)KPI基準点((iii)の差し引き額を、E2E内のshadow実測で確定するか、差し引き0か)と(2)Cost許容(平均+¥2厳守か、Cost Cap +¥3以内なら可か)を先に決める。可なら【B】へ。不可なら本管理IDをTrial結果(Safety達成・Cost未達)でClose | ¥0 | 即日(回答のみ) | 基準を緩める方向の決定は実質KPI変更になる。決めずに進むとE2E¥62が基準未達で無駄になりうる | KPI定義の確定(以降の判定がぶれない) |
| 【B】E2E 20 run | 採用構成(r3 medium+r5 high+否定案a)でE2E 20 run(≈¥62、48〜86、残¥98.29)を実行し、Human Review・実費・shadow V4A費用を実測。Recheck新仕様(約150〜200行)の実装を伴う | ≈¥62(+実装¥0) | 実装+実行で1〜2委任 | 見込みでは(iii)でも+¥2超の公算大(¥3.1/run見込み)。実測が基準未達なら¥62が基準確認のみに終わる。残予算が¥約36に減る | Human Review 0の実測(唯一)、(iii)差し引き額の実測、E2E Safety、Stage 2負荷の実測 |
| 【C】ループ3 | 新構造設計+Opus#18+Trial+E2E | 残¥98.29では完走困難 | 長い | Opus#17分析では費用に効くのはLLM呼び出し自体の低廉化のみ。予算超過。非推奨 | 新構造の費用 |
| 【D】Stage 2出力短縮 | Opus#17別案2(Stage 2の1候補あたり出力551tokを判定+短い理由へ短縮)を検討対象に加える。ユーザー承認済み構成の変更になる(Bと併用可) | 検討¥0、効果測定は別途有料 | 別管理ID | Stage 2は承認済み構成のため変更にユーザー承認が必要。品質影響は未測定 | Stage 2費用の削減余地(候補比例の係数低減) |

## §5 Fable推奨
A→(可なら)B+D検討。
1. 見込みが基準未達なのは、構成の不備というより「基準点(iii)・Cost許容・Stage 2費用」というユーザー判断事項に依存するため、先に基準を決める方が¥62の無駄打ちを避けられる。
2. Human Review 0はE2Eでしか測れないが、基準が決まらないと実測値の合否判定ができない。
3. Stage 1側の削減は試し切った(r5-V不採用・G部分採用)ため、残る費用削減はStage 2側(承認済み構成)で、これはユーザー判断が要る。

## §6 ユーザーが答える質問(Yes/No)
- Q1. KPI基準点を(iii)(新フロー配線後Production−現行Production、差し引きは現行Stage 1のV4A実費のみ)として採用し、差し引き額をE2E内のshadow実測で確定してよいか。(No=差し引き0で判定)
- Q2. Cost許容は「平均追加+¥2/記事を厳守」のままでよいか。(No=Cost Cap +¥3以内なら可とする)
- Q3. E2E 20 run(≈¥62、残¥98.29、Recheck新仕様の実装を伴う)を実行してよいか。
- Q4. Stage 2出力短縮(Opus#17別案2、承認済み構成の変更)を検討対象に加えてよいか。
- Q5. 本管理IDをCloseする場合の最終Statusは、VALIDATED不可のため`TRIAL_RESULT: SAFETY_MET_COST_UNMET`(Safety=Stage 1限定の条件付き達成、Cost=未達見込み、Human Review=未測定)の表記でよいか。

## §7 停止時点の自己確認(PM_GOVERNANCE 24-3、Closeout項目27〜30。本管理IDはCloseではなくUSER_DECISION_REQUIRED停止のため「停止時点の自己確認」)
| 項目 | 確認結果 | 判定 |
|---|---|---|
| 27 重要Opus警告が全てCLOSEOUT_CONFIRMEDまたはREJECTED | 台帳OF-001〜037を1件ずつ確認(`OPUS_FINDINGS_LEDGER.md`末尾の分布: 対応済9・部分13・未対応2・対象外13)。CLOSEOUT_CONFIRMED遷移はE2E未実施のため0件。OPEN残は台帳末尾に列挙 | 未達(停止中のためClose不可と明示) |
| 28 KPIにprovenance(6区分・件数)とE2E自己確認(Yes/No) | §1表: Human Review=未測定/No、Safety=fresh(Stage 1のみ、G arm 33 run)+frozen(段階A high、混合構成の推測)/No、Cost=fresh(Stage 1)+推測(Stage 2 fit外挿)/No。「E2E達成」の表記なし。production_formal_path・manual_substitution・syntheticの経路は今回なし | OK |
| 28b 条件付き値とE2E値の混在なし | Safety値はStage 1限定の条件付きKPIと明記。E2E値は0件 | OK |
| 29 Safety未解決項目が独立Open ID・再開条件・ユーザー承認を持つか | OF-018: 独立Open IDなし(台帳OPENのみ、本管理ID行進捗に今回追記)・ユーザー承認なし。(A)2層化条件付き保留(OF-026/027): 本管理ID行に再開条件(absence型3条件+proxy約¥5〜8)あり、独立Open IDなし。CURRENT_SPEC L2413 Stage 1プレースホルダ: OPEN_ITEMSで個別追跡されておらず、本管理ID行の進捗へ今回追記(配線時に確定)。PRODUCTION-WIRING-01: 配線STOP中として`OPEN_ITEMS.md`に明記済み | 不備あり(OF-018・プレースホルダは独立Open ID未設定。Fable判断要) |
| 29b defer同等語の未処理なし | 「条件付き保留」「別管理」「配線時に扱う」の使用箇所は上記の管理場所(本管理ID行・台帳・WIRING-01行)に残る。3条件(Open ID・再開条件・ユーザー明示承認)を全て満たすのは未確認、上行の通り不備候補 | 一部不備 |
| 30 条件付きVALIDATEDをProduction採用提案の材料にしていないか | 採用提案はしていない。Status表記は`USER_DECISION_REQUIRED`(Close時案: `TRIAL_RESULT: SAFETY_MET_COST_UNMET`)。VALIDATED単独表記なし | OK |
