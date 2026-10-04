# Opus独立レビュー#10: OPEN-233 Stage 2「重大検出の降格」への確認構造(条件A、2026-10-04)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_68で保存)
(1) レビューの位置づけ: PM_GOVERNANCE 11-3 条件A(Stage 2の降格権限に対する確認構造=新しい処理フロー設計)。
レビュー対象: `docs/pm/design_open233_stage2_safety_downgrade_01.md`(委任_67)、`docs/pm/opus_packet_open233_stage2_safety_downgrade_01.md`
抽出元: 依頼文=委任_68の委任文末尾「Opusへの依頼」節(Fableによる要旨。Opus subagentへ実際に送られた全文はこの委任文には含まれておらず、実行層は未確認)。Opus報告文=委任_68の委任文末尾に逐語で貼られた全文(本文は改変していない)。
性質: 読み取り専用の独立レビュー。Production採用可否は判断していない。

## (2) 依頼文(逐語。委任_68の委任文末尾の節)

[Fableがopus-consultantへ送った依頼。論点1〜8: 1.単独LLM判定による降格とSafety KPIの両立 2.案S1の同一prompt 2回目の独立性/F5型promptの是非 3.より単純・決定論的な構造((i)basis非none要求 (ii)MAJOR降格不可 (iii)Safety-critical登録文のみ降格不可 (iv)理由欄追加) 4.過剰Major・不要Rewrite・Human Review 5.費用 6.cycle/Recheck/floor_verify/既存2-of-2との整合 7.Production配線時の矛盾 8.Stage 1 recall欠落。packet: `docs/pm/opus_packet_open233_stage2_safety_downgrade_01.md`、設計書: `docs/pm/design_open233_stage2_safety_downgrade_01.md`。]

## (3) Opus独立技術レビュー全文(逐語、委任_68の委任文末尾から)

# Opus独立技術レビュー#10(条件A): OPEN-233 Stage 2「重大検出の降格」への確認構造

## 結論
- **必要/不要**: 対策は**必要**。今の作りでは、1回のLLM判定だけで重大(MAJOR)を合格へ下げられ、その後の確認がない。runner 6771行で、Stage 2に入るのはStage 1のMAJORだけと確認した。つまり、Stage 2に入る指摘はすべて「重大の降格候補」である。
- **推奨構造**: 案S1(同じprompt・同じ入力の2回目を呼び、2回とも非BLOCKINGのときだけ降格する)を**3点修正して**採るのが最も単純で妥当。ただし、Sonnet案のまま追認はしない。
  1. **2回目の比較基準**: Sonnet案の`llm_materiality`ではなく、2回目の`run_stage2`の**最終`materiality`**で比べる(根拠は論点6)。
  2. **既存NORMAL群2-of-2の扱い**: Production候補の構成から外す(論点6・7)。
  3. **Safety KPIの測り方**: Stage 1を代替投入した条件付きの値と、代替なしの通し(end-to-end)の値を分けて報告する(論点8)。
- **Fableへの判断材料**: 論点3(i)の「`basis`非noneの要求」は、schemaの意味からみて成り立たない(論点3)。

## 12観点(要点のみ)
1. **必要性**: 必要。理由は上記のとおり。
2. **単純さ**: 検討した代替案(論点3の(i)〜(iv)と派生案)はいずれも効かないか、Rewriteが急増する。S1が最も単純。
3. **既存処理の利用**: `run_stage2`の呼び直しで足りる。既存2-of-2の関数と同じ比較方法を使えばよい。
4. **前段情報の喪失**: **ある**。Stage 2のpromptには、Checkerのissue・flag(`dev`)が渡っていない(calibration 649-671行の入力構成で確認)。Stage 2はB3の「so」による因果の問題を自力で見つけ直す必要があり、浅い推論の回(306/262 tokens)に見落とす。これが非決定性が現れる経路と考えられる(推測)。ただし、issueをStage 2へ渡すとBLOCKING寄りに誘導され(priming)、降格68件の較正全体が変わる。そのため今回は推奨せず、記録だけにとどめる。
5. **不要なLLM処理**: 追加は1回目が非BLOCKINGのときだけ。最小限である。
6. **非決定性**: 増えない。降格を許す条件が「2回とも一致」になるため、結果は安全側に収束する。
7. **Human Review**: 増える経路は「2回目だけBLOCKING → Rewrite → Escalation」。とくにcycle 2以降は、残りcycleが少なくSTAGE4に直結しうる(論点4)。
8. **不要Rewrite**: 率q次第。未測定。
9. **費用**: 小さい(論点5)。
10. **retry/fallbackとの整合**: 2回目のAPI失敗をBLOCKINGにするのは、既存の`*_api_failure_failclosed`と同じ向きで整合する。
11. **失敗時の安全側**: 安全側に倒れる。
12. **再発防止になるか**: Stage 2の偶発的なブレ全般に効くので、個別パッチではない。ただし、rubricが常に誤る型(B3のV5で2/2)と、Stage 1の取りこぼしには効かない。

## 論点1〜8

**1. 単独判定の降格とSafety KPIの両立**
- 単独LLM判定のまま見逃し0を保証することはできない。
- ただし、決定論で0を保証することも、このパイプラインでは原理的に不可能である。Stage 1自体がLLMで、取りこぼしがある(B3は代替投入)。
- よって、KPIの「0件」は確率的に極小化する目標として扱うしかない。これを§5候補2としてユーザー確認に回すのは正しい。
- 支配的なリスクはStage 2ではなくStage 1のrecallである。S1を入れるだけで「Safetyは解決」と報告してはならない。

**2. 同じpromptで2回呼ぶ独立性**
- 同じclaimについては、2回の判定はほぼ独立とみてよい(V7bは診断で10/10 BLOCKING、実flowでは1/3。偶発的なブレと矛盾しない)。
- しかし、claim全体で平均すると見逃し率は「p_iの2乗の平均」になり、「平均pの2乗」以上になる。p_iが大きい境界claim(B3のR3'''で15%)では残りが大きく、p_iが1に近い系統的な誤り(V5)にはS1は無力である。系統誤りはrubricの較正(既存のSafety-critical回帰)で捕まえる役割分担になる。
- 2回目にF5型のprompt(Checkerの指摘を仮説として示す形)を使う案は推奨しない。理由は次の3点。
  - priming(prompt中の示唆が判定を誘導すること)でBLOCKINGが増え、qが上がる。Primary KPIに反する。
  - 新しいpromptには再較正が要る。
  - 1回目と2回目で基準が変わり、判定の意味が混ざる。
- 補足: S1の2回目は対象claimだけのbatchになり、1回目とpromptが異なる。そのため独立性はわずかに上がる。許容してよいが、ログに残すこと。

**3. より単純・決定論的な構造の評価**
- **(i) 降格に「`basis`非none+hintか理由が非空」を要求する案: 非推奨。**
  - schemaの`basis`は「Ledgerとの不一致の根拠」を表す列挙値である(`ledger_claim`/…/`unsupported_relationship`/`none`、stage2_production_01.py 136-142行)。正当なACCEPTABLEでは、`basis=none`・hint空が自然な出力になる。
  - したがってこの条件は「MAJORはACCEPTABLEへ降格不可」とほぼ同じになり、rep24のACCEPTABLE 45件の多くがRewriteへ回る見込み(推測)。
  - さらに、過去の見逃し8件はQUALITYだった(R3''' 4件、V5で2件、A2A3-0の2件)ので、この条件では防げない。
  - 事実で確かめるなら、既存の475 instanceを¥0で再集計し、正当な降格のうち`basis=none`の割合を確認できる。
- **(ii) MAJORは降格不可: 不採用で妥当。**
- **(iii) Safety-critical登録文だけ降格不可: 不可。** 評価セットの正解ラベルに依存した過学習で、Productionでは意味を持たない。
- **(iv) Stage 2のschemaに理由欄を追加**
  - Stage 2はTrial側のpromptなので、Checkerの制約の対象外とは解釈しうる。最終判断はユーザー。
  - ただし、出力形式を変えると推論の挙動が変わりうるため、再較正が必要。
  - 理由欄は観測性(後から理由を確認できること)を上げるだけで、安全装置にはならない。LLMはもっともらしい理由を書けるからである。降格可否の条件に使うことは推奨しない。
- **派生案**
  - reasoning tokensが少ない回だけ2回目を呼ぶ案: n=2の相関しか根拠がなく、閾値を決める根拠もないので、単独の引き金にはしない。将来、費用を下げる候補にとどめる。
  - 「QUALITYまでしか降格させない」案: 過去の見逃しがQUALITYなので無効。

**4. 過剰Major・不要Rewrite・Human Review**
- 「判定基準は増やさない」という主張は正しい。ただし、qの分だけRewriteは確実に増える。
- 増えたRewriteは、Recheckで新しいMAJORが出たり周回が延びたりする経路になる。B3もrep24では、cycle 2で「so→and」の後に再びMAJORが出ている。
- qは**cycle 1とcycle 2以降に分けて**測るべき。後半cycleでは、Rewriteが増えるとSTAGE4/Human Reviewに直結する。
- 測定は実装前の限定測定(約30 call、約¥4)を推奨する。ただし実施前に、STOP閾値を決めておくこと(例: 追加Rewrite率と、そこからEscalationへ進む率の上限)。
- ¥0の予備見積もりとして、既存ログで同じclaimを複数rep観測しているものの判定ゆらぎ率も参考になる(V7bは3 repのみなので弱い)。

**5. 費用**
- 試算は妥当。最悪でも68件をすべて個別に呼んで約¥0.33/記事。Rewriteの追加を足しても+¥2以内に収まる見込み。
- cacheは、Ledgerと本文の部分が共通の前置き(prefix)になる場合に効く(prompt templateの順序次第)。rep25実測ではcached 0だった。
- 注意: ¥2の枠は、floor_verify・L6・Recheckなどの追加分の**合計**に対する上限である。S1単独の数字で枠を満たしたとみなさないこと。

**6. cycle/Recheck/floor_verify/既存2-of-2との整合**
- **対象集合が互いに重ならないという整理は正しい。** floor_verifyで解放済みのclaimは、すでにLLMの非BLOCKING判定が2回そろっているので、除外は妥当。
- **比較基準はSonnet案と逆にする(重要)。**
  - Opus#8の落とし穴(2回目に`apply_floor`が再適用され、常にBLOCKINGになる)は、floorが発火するclaimの話である。S1の対象(1回目`floor_reason=None`、同じ`dev`)では、2回目もfloorは発火しない。floorは引き上げ専用だからである(run_stage2 2830行)。
  - 一方、hook-aware降格・disclosure-gap降格(2877-2890行)は、「BLOCKINGを決定論で下げる」処理である。`llm_materiality`で比べると、これらで下げるべき2回目のBLOCKINGを保持してしまい、過剰BLOCKINGになる。
  - よって、**2回目の最終`materiality`で比べ、2回目に`floor_reason`がfloor由来の値になったら異常としてログに残す**のが正しい。既存2-of-2もこの方式(2945行)である。
- **既存NORMAL群2-of-2は廃止(または既定OFF)を推奨。**
  - 適用条件が評価用の正解ラベル(`instance_id ∈ NORMAL_GROUP_INSTANCE_IDS`)に依存しており、Productionへは移せない。
  - Trialで測るHuman Review・過剰Majorの数字を、その分だけ良く見せている可能性がある。
  - ラベルなしで一般化すると「BLOCKINGが残るには2回一致が必要」となり、S1の「降格するには2回一致が必要」と正面から矛盾する。安全側に統一すれば、「2回の判定が割れたらBLOCKING」の1規則に集約される。
  - 外した構成で、NORMAL群の過剰Majorを測り直すべき。

**7. Production配線時の矛盾**
- **ACCEPTABLE_STAGE1経路(6732行)にS1は不要。** Stage 1にMAJORが無い経路で、降格が起きないためである。これは論点8(Stage 1 recall)の領域になる。
- **ProductionにStage 2が無いなら、現状のProductionは「MAJORは必ずLocal Rewrite」という最も厳しい構成**と読める。er003は未確認のため推測。
- したがって、整理の原則は次のとおり。
  - Stage 2(降格権限)をProductionへ移すときは、S1と一体で移す。Stage 2単体を移すと、Productionの安全性が今より下がる。
  - NORMAL群2-of-2は移さない。
- Production側コードは今回読んでいない。

**8. Stage 1のrecall欠落**
- 範囲外にしてよいのは「S1の設計レビュー」としてだけ。KPI評価の範囲外にはできない。
- 必要なこと:
  - (a) Safety KPIを、代替投入ありの条件付き値と、代替なしの通しの値に分けて報告する。現状は`all_deviations_raw`に代替分が出ず、観測性に穴もある。
  - (b) Checker Promptを変えずに取れる手段をユーザー判断として提示する。候補は、Checkerを2回呼んでMAJORの和集合を取る(過剰Majorと費用が増え、「判定方法の変更」に当たるかはユーザー判断)、合格直前の検査の強化(委任_49の実測: Recheck MAJOR 3/8)。
- S1とは別の管理事項として明示的に残すこと。

## リスク
- S1後も、境界claim(B3型)の残りの見逃し率は「p_iの2乗」で、0にはならない。
- qによるRewrite・STAGE4の増加は未測定。
- NORMAL群2-of-2を外すと、Trialの過剰Majorの数字が悪化して見える可能性がある(実態が見えるようになるという意味)。

## 代替案(優先順)
1. 修正版S1(比較は最終materiality、NORMAL群2-of-2は除外、cycle別q測定とSTOP閾値の事前設定)。
2. 将来の候補(今回は推奨しない): Checkerのissueを渡す確認promptへ切り替え。

## 追加で読んだファイル(概算文字数)
- `docs\pm\opus_packet_open233_stage2_safety_downgrade_01.md`(約1.4万字、指定)
- `docs\pm\design_open233_stage2_safety_downgrade_01.md`(約1.2万字、指定)
- `er052_open233_self_recovery_stage2_calibration_01.py` 560-700行(約6千字): Stage 2の入力構成とV7b文言
- `er052_open233_self_recovery_flow_runner_01.py` 2689-2959行(約1.3万字)、6720-6830行(約6千字): 処理の適用順、既存2-of-2、挿入位置
- `er052_open233_self_recovery_stage2_production_01.py` のGrep結果(約2千字): `basis`の列挙値

## 十分に答えられなかった論点
- 論点7のProduction側(er003のDeviation→Local Rewrite経路)。コードは未読で、「ProductionにStage 2は無い」は依頼文の前提に依拠している。
- 論点3(i)の定量面(正当な降格のうち`basis=none`の割合)。既存ログの¥0再集計で確定できる。
- prompt templateの順序(cache prefixの成立)は未確認。

採用可否・Production採用の判断はしていません(人間ユーザーのみが決定)。実装・修正にも着手していません。

## (4) FableのPM評価

**Fable PM評価(2026-10-04、Opus独立レビュー#10。Fableが委任_68の委任文で指示した採否を、実行層[Sonnet]が逐語で転記し、PM_GOVERNANCE 11-3の8項目・STOP条件との照合を1行ずつ記録したもの)**

### (4-1) Fableの照合判断(委任_68の委任文から逐語。変更しない)

1. 対策S1(重大検出の降格は、独立2回目の判定も非BLOCKINGのときだけ許可。失敗はBLOCKING)は必要。Opus#10の3修正を採用: (i)2回目の比較は`run_stage2`の最終`materiality`で行い、2回目に`floor_reason`がfloor由来になったら異常としてログに残す、(ii)既存NORMAL群2-of-2(`apply_stage2_two_of_two`、正解ラベル依存・Production不可・向きが逆)はProduction候補の構成から外し既定OFFとする(外した構成でNORMAL群の過剰Majorを測り直す)、(iii)Safety KPIは「Stage 1代替投入ありの条件付き値」と「代替なしの通し値」を分けて報告する。
2. 2回目にF5型prompt(Checker指摘を仮説として示す)を使う案は採用しない(priming・再較正・基準混在)。Stage 2 promptにChecker issue/flagを渡す案も採用しない(記録のみ)。
3. 案(i)「`basis`非none要求」は不採用(schemaの意味上、正当なACCEPTABLEでも`basis=none`が自然。過去の見逃し8件はQUALITYで防げない)。¥0再集計で定量を確認して記録。(ii)MAJOR降格不可・(iii)Safety-critical登録文のみ降格不可・(iv)理由欄追加は不採用(理由欄は観測性のみ、安全装置にならない)。
4. qの限定測定はcycle 1/cycle 2以降に分けて実装前に行う。STOP閾値を事前設定: 追加Rewrite率(2回目だけBLOCKING)がcycle 1で30%超、またはcycle 2以降で20%超なら、S1の設計を見直す(自動実装へ進まない)。
5. S1はユーザー承認が必要(既存より厳しくする変更)。「重大見逃し0」を決定論で保証できない(Stage 1がLLM)点、KPIを確率的極小化として扱うかはSafety原則に関わるためユーザー判断(STOP条件該当)。
6. Stage 1 recall欠落はS1と別の管理事項として明示(Checker 2回和集合/合格直前検査強化は「判定方法の変更」に当たりうるためユーザー判断候補)。
7. Production配線原則: Stage 2(降格権限)をProductionへ移すときはS1と一体で移す。NORMAL群2-of-2は移さない。`OPEN-233-A1-PROD`へ記録。

### (4-2) PM_GOVERNANCE 11-3 照合(8項目、1行ずつ)

1. Claude案: 設計書案S1を採用するが、比較基準(llm_materiality→最終materiality)・NORMAL群2-of-2の扱い・Safety KPIの報告方法の3点をOpus指摘どおり修正(設計書§7/§8)。
2. Opusレビュー: 採用(3修正)。F5型prompt・Checker issue受け渡し・basis非none要求・MAJOR降格不可・Safety-critical登録文のみ降格不可・理由欄追加は不採用(根拠はOpus論点2・3)。Opusが「十分に答えられなかった」Production側(er003)・basis=none定量・cache prefixのうち、basis=noneの定量は¥0再集計(作業2)で確認。
3. CURRENT_SPEC: S1・NORMAL群2-of-2の既定OFF化はいずれも未承認のためCURRENT_SPECは編集しない。Stage 2はTrial側でありProduction仕様に含まれない。
4. DECISION_LOG: 末尾へ「Fable判断、ユーザー決定ではない」として記録(作業4)。ユーザー指示(2026-10-03「機械的な安全装置は今回の採用内容だけを理由に勝手に緩めない」、2026-10-04のKPI3点)と矛盾しない。
5. OPEN_ITEMS: OPEN-233行Statusを`USER_DECISION_REQUIRED`へ、`OPEN-233-A1-PROD`へS1一体配線・NORMAL群2-of-2非配線を記録。
6. ユーザー承認済み内容: 承認済みの範囲(Trial、P-strict-closed等)は変更しない。S1は既存より厳しくなる変更で未承認のため実装しない。
7. QCD: Q=重大見逃しp→p²(0にはならない)。C=Stage 2 2回目約¥0.14/call+Rewrite増分q依存(作業3で測定)、+¥2/記事枠の合計管理(floor_verify・L6・Recheck含む)。D=追加は1回目が非BLOCKINGのclaimのみ。
8. PM強制Gate: 条件A(Opus独立レビュー)は本#10で充足。次Trial開始なし、runner・Prompt・Production変更なし、`PRODUCTION_WIRED`にしない。

### (4-3) STOP条件該当(11-3「Opusレビュー後の進行判断」)

- 該当: 「Safety原則に関わる判断」(Safety KPI「重大Fact見逃し0件」を決定論で保証できず確率的極小化として扱うかどうか)。
- 該当: 「既存より厳しくする変更」(S1は降格の確認を増やし、既存よりRewriteが増えうる)。
- よって`USER_DECISION_REQUIRED`としてSTOPする。S1・NORMAL群2-of-2既定OFF化・Stage 1 recall対策の方向はユーザー判断後に実装する。

Production採用の可否は判断していない(人間ユーザーのみが承認する)。
