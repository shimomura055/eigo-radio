# TRIAL_PLAN_01 KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01(事前登録・PREREGISTRATION、2026-10-31)

本書は委任_02の本格Trialの**実行前登録**。成功基準・副作用基準・評価記事・ベースラインは、結果を見る前に本書で固定する(結果を見て基準を動かさない)。案の内容=`DESIGN_OPTIONS_01.md`、原因=`ROOT_CAUSE_01.md`。**どの案をTrialに載せるかはFable判定後に確定する**(本書は現時点の見込みの案セットを置く)。

## 0. 目的と最低達成条件(ユーザー原文§1・§7)

`put away`と`in the way`の**両方**が、(a)抽出され、(b)本文の意味で正しく認識され、(c)最終候補(N5のpick後の7件)に残る方式を、一般化できる形で実証する。特定表現のハードコード、記事固有のPrompt調整は不可(Prompt・規則に表現名を含めない。評価時の照合用regexは評価スクリプト内に限る)。

## 1. 比較アーム(同一入力・同一条件で同時比較)

| Arm | 層1 抽出(プール) | 層2 選定(pick規則) | 備考 |
|---|---|---|---|
| A0 | 現行: P7(fixture保存の本番出力)+B1(現行Prompt)+既存Gate | R0(現行pick) | ベースライン。B1はN回新規呼出 |
| A1 | E1: B1条件4・5除去・30個 | R0 | 層1単独の最小改善 |
| A2 | E2: 網羅列挙(上限40) | R0 | 層1のみ改善→層2が必要なことの再確認 |
| A3 | E2 | R2(出現回数昇格) | |
| A4 | E2 | R1(chunk_type昇格) | |
| A5 | E5: 辞書seed(LLM追加0) | R2 | |
| A6 | E6: E2∪E5 | R2 | |
| A7 | E6 | P4(SELにvalue軸を追加。SEL schema複製+追加1欄) | SEL追加callが必要(Trial複製promptで実行) |

- 層2のR0/R1/R2は同一SEL判定結果に対する決定論的な並べ替え(API 0)。したがって**SEL呼出はプール種別ごとに1回**(A0/A1/A2〜A4/A5/A6/A7の6プール)。同一反復(rep)内で全プールのSELを実行する。
- 複数案の同時比較: 反復ごとに全プールのSELを連続実行し、全アームのpickを同じSELラベルから再計算(アーム間のSEL揺れを混ぜない部分と、プールが違うことによるSEL文脈差を分けて記録=SEL一致率で測る)。
- 抽出probeで`E3`(句動詞pass)は`in the way`/`in sight`を拾えないこと、`E4`(分割)はE2に対する優位が観測されなかったことから、Trial初回では**除外**(結果次第でPhase 3で再検討)。

## 2. 評価記事(事前固定)

- **主評価(設計に使用済み、再現性を見る)**: Family X `untidiness_family_resource` Advanced(`untidi_b1b`)× **N=5反復**、Standard(`untidi_a2`)× **N=3反復**。両方の本文に`put away`と`in the way`を含む(`ev01/dict_seed_all_cases.json`で確認済み)。
- **held-out(設計に使用しない記事≥3、X/Y/Zを含む)**: `surname_b1b`(Y、Advanced)、`melos_a2`(Z、Standard。なお`melos_b1b`は本委任の抽出probeに使用済みで、a2は別本文)、`moon_b1b`(X、Advanced)。各 **N=2反復**。(各caseのFamilyは委任_02開始時に`er019/er121/er026`のfixture出典で再確認する。確認で別Familyだった場合は同Family内の別caseに差し替え、差替えは事前登録の逸脱として記録する。)
- 各caseのP7候補(`fixtures/n5_trial_replay_fixture_01.json` cases.<id>.base)は全アームで共通の保存値を使う(P7は無変更のため。P7の揺れは本Trialの変数にしない)。補完P7(Gate除外時の再選定)は評価対象外(documented limitation)。

## 3. 成功基準(事前登録。すべて満たしたアームのみ「最低達成条件を満たす」)

評価対象表現(主評価記事のみ、照合は評価スクリプト内のregex): `put away`系=`put away`/`put it away`/`put that away`/`putting something away`、`in the way`系=`in the way`/`something in the way`。

| ID | 基準 | 閾値 |
|---|---|---|
| S1 抽出 | 主評価の各反復(Adv 5+Std 3=8反復)で、両表現がプール(P7∪抽出∪Gate後)に存在 | 各表現 **≥7/8反復** |
| S2 意味 | S1で抽出され最終候補に残った項目を既存GEN5→VER5→CHK5に通し、`relation`がSAME/MODIFIER_DROPPED_OK、`gloss_ja`が本文語義に一致(Fable/委任者が本文を読んで確認、`put away`=しまう・片づける、`in the way`=邪魔になっている) | 対象の**100%** |
| S3 最終残存 | pick後の最終7件に両表現が残る | 各表現 **≥7/8反復** |
| S4 一般化 | held-out(3記事・計6反復)で、アーム最終7件のうち**ベースライン最終7件に無い新規入場項目**のうち、CHK5でSAME/MODIFIER_DROPPED_OK、かつ本文に存在し、Fableの目視で「塊として学ぶ価値あり」と判断された割合 | **≥80%** |
| S5 副次改善 | `leave out`(題名句`Leaving Things Out`と別の用法=`leave it out`系)と`in sight`の最終残存 | 報告のみ(基準化しない。ユーザー原文§3-4) |

## 4. 副作用基準(事前登録。1つでも超過=そのアームはVALIDATED不可)

| ID | 基準 | 閾値 |
|---|---|---|
| N1 本文に無い表現 | 最終7件に本文一致しない項目 | **0件**(既存Gate`span_in_text`/`make_b1_gate`で落ちること。落ちずに最終に残れば不合格) |
| N2 易しい表現の増加 | 最終7件の新規入場項目のうち、SEL難易度easy ∧ 本文出現<3 ∧ chunk_typeがfixed_phrase/collocation の項目 | 1記事levelあたり **≤1件** |
| N3 他KPの押し出し | ベースライン最終7件のうち、アーム最終7件に無い項目 | 1記事levelあたり **≤2件**。かつ公開済みのHR選定(untidi: `turn into an interrogation`・`hear it out`)は**必ず残る** |
| N4 SEL安定性 | 共通候補(ベースライン・アームの両プールにある候補)のcls/keepの一致率 | **≥90%** |
| N5 意味の不適切な表現 | 最終7件のうちGEN5/VER5/CHK5でrelationがSAME系でない項目 | アーム最終7件で **0件**(ただしGen/Ver/Chkが機能して除外した結果の最終のみを数える) |
| N6 費用・時間 | 追加費用 / 追加処理時間(1 level) | **≤ +¥1.5 / ≤ +40秒**(並列化で隠れる分は除く。記事セット=Std+Adv換算で+¥3以内=70円目標の約4%以内) |
| N7 retry負荷 | JSON途切れ再試行・技術失敗の回数 | 呼出総数の **≤5%**(probe実績: 1/33程度) |

## 5. 判定規則(事前登録)

- S1〜S4とN1〜N7を満たすアームが1つ以上: **VALIDATED候補**(Production採用は別途ユーザー判断)。複数あれば費用が最小のアームを推奨候補とし、全アームの表を提示。
- どれも満たさない: 失敗要因(S/N別)を分析し、**Phase 3**(アーム再設計: Prompt文面ではなく工程構成の見直しを含む。例: E2の件数枠・SEL value軸の定義・pick規則の組合せ)を同一委任内で実施。同方向の微調整の反復はしない。
- 改善見込みが尽きた: `REJECTED`または`USER_DECISION_REQUIRED`(状況・原因・試行・代替案・見込み・推奨を付ける)。

## 6. 実行設計(並列化・手順)

- 1反復の流れ(記事level単位): B1(現行)・E1・E2を**独立呼出**(同一本文、並列可)→ E5(API 0)→ 各プールを`collect_pool`+既存Gate(`make_b1_gate`)で構築→ SEL(プールごと)→ pick規則(R0/R1/R2/P4)を再計算 → 最終候補の和集合(重複排除)にGEN5/VER5/CHK5を**一度だけ**実行しアーム間で共有(同一候補はキャッシュ)。
- 並列化: (a) 反復内の抽出3呼出は並列可、(b) 記事level間は独立で2プロセス並列(300秒窓≤2起動・150秒以上間隔のrunner規則を守る)、(c) N5はthread並列にしない(`er138` N5Ctx docstring: er125 contextvar・cost logger globalを共有するため)ので、1プロセス内の逐次/並列はプロセス内の抽出呼出のみ。
- 実時間見込み: 1反復 約130秒(B1 12+E2 35+SEL 6プール×約20)、主評価N=8反復+held-out 6反復=14反復÷2プロセス+GEN/VER/CHK(最終候補和集合 約12件/level×約20秒) → 約45〜60分(Phase 1+2)。
- 実装先: `docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01/tools/`の新規script(`probe_extract_01.py`の`p_L1`/`p_L3`、`dict_seed_probe_01.py`の`find()`、`pool_pick_probe_01.py`のpick規則を関数化)。結果=`ev02/`(新設しない既存の`ev01/`と同階層に委任_02の結果を置くか、同ディレクトリの`ev02/`で区別する=委任_02で決める)。

## 7. 費用見積(案ごと・合計・上限提案)

実測単価: B1 ¥0.15〜0.22、E2(L3)¥0.28〜0.35、E1(L2)¥0.17〜0.25、SEL(14〜40件)¥0.27〜0.50(`docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/CURRENT_STATE_01.md:96`のN5実測 B1 0.16+SEL 0.27+GEN5 0.36+VER5 0.80+CHK5 2.30=¥3.88/level)。

| 項目 | 内訳 | 1反復 |
|---|---|---|
| 抽出 | B1 0.18(A0)+E1 0.2(A1)+E2 0.32(A2〜A4,A6,A7) | ¥0.70 |
| SEL(プールごと1回) | A0 0.27、A1 0.30、A2〜A4 0.50、A5 0.40、A6 0.60 | ¥2.07 |
| SEL value軸(A7) | E6プールのSEL複製1回(untidiのみ) | ¥0.60 |
| GEN5/VER5/CHK5 | **ベースライン最終7件はfixtureの保存結果を再利用(API 0)。新規入場項目のみ**(約5件/level×約¥0.5/件=約¥2.5〜3/level)。同一候補は反復間・アーム間でキャッシュ共有 | level単位(反復ごとではない) |

| 段階 | 内容 | 見積 |
|---|---|---|
| **A案別の費用(参考、層1+SELのみ/反復)** | A0 ¥0.45、A1 ¥0.50、A2〜A4 ¥0.82(共有)、A5 ¥0.40、A6 ¥0.92、A7 +¥0.60 | — |
| **Phase 1** | untidi Adv N=5+Std N=3=8反復×(0.70+2.07+0.60)=¥27 + GEN/VER/CHK 2level×¥3=¥6 | **約¥33** |
| **Phase 2** | held-out 3記事×N=2=6反復×(0.70+2.07)=¥17 + GEN/VER/CHK 3level×¥3=¥9 | **約¥26** |
| **Phase 3(再設計・再Trial、予備)** | Phase 1相当の1回分 | **約¥33** |
| 合計(Phase 1+2+3) | | **約¥92** |

- 上限提案: **委任_02 個別Cap ¥105**(見積¥92+約15%のマージン)。Phase別止め線(累計): Phase 1=¥38、Phase 2=¥68、Phase 3=¥100。各止め線の**前に**残額・改善見込みをFableへ報告(原文§5「予算不足で停止・翌日持越しは不可」を守るため、¥92見積で足りない見込みが出た時点で事前申告)。Phase 1のみで基準を満たし、Phase 3が不要となれば実費は約¥59(Phase 1+2)。
- 見積の不確実性: GEN5/VER5/CHK5は新規入場項目数に比例(上記は約5件/levelの仮定。E2のkeepが17〜20件に増える場合は入場項目が増える)。E2のSEL件数が40→50に増えるとSEL単価が約+¥0.1。日次¥1,000/日(JST)への影響=他委任の本日費用はFableが把握(本委任_01は¥9.45)。
- 費用を下げる設計: (a) 層2のR0/R1/R2はAPI 0、(b) A5(辞書)は抽出LLM 0、(c) A7(SEL value軸)をuntidiに限定、(d) GEN/VER/CHKは新規入場項目のみ・キャッシュ共有、(e) probeで劣後が確認されたE3・E4は初回除外。
- 量産単価への影響(Trialで採用された場合の見込み): E2系=+約¥0.4/level(+約¥0.8/記事セット=Std+Adv、70円目標の約1.1%)。E5/A5=+約¥0.3/level。

## 8. Production分離

- 全コードは`docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01/tools/`にあり、Production module(`er138_*`・`er105_*`・`er119_*`)を**import専用で読み取り**(無編集)。新規flag・設定dict・環境変数・起動script・`.env`は追加しない(Productionに到達する経路を作らない)。
- 差込点`er119_kp_candidates_01.py:505`の`n5_pool_fn`は既存の注入引数だが、本Trialでは使わない(本Trialは配線せず、pool/SEL/pickを直接呼ぶ)。Production配線は、VALIDATED後にユーザーが正式採用した場合の別委任。
- 検証: 委任終了時に`git diff --name-only origin/main`が`docs/`配下のみであること、`grep`でProduction module名の変更が無いことをRESULT_PACKETに記録。
- Family A/B/Cは対象外(触れない)。

## 9. 記録・Closeout

- 追加/更新: `OPEN_ITEMS.md`の当該OPEN行(Trial・未承認・既定OFFのProduction無配線)。CURRENT_SPEC/DECISION_LOGは、VALIDATED後のユーザー採用判断まで変更しない(本Trialは未承認Trialで仕様化されない)。過去Trial(KP-GENERALIZATION-N5-PRODUCTION-WIRING-01、KP-N5-PHRASE-COVERAGE-AUDIT-01)との差分は`ROOT_CAUSE_01.md`・`DESIGN_OPTIONS_01.md`に明記。
- 関連する独立修正(原文§6): ①上限7件超過の候補脱落の記録化=P1(挙動不変、他案と独立)、②`gets heated`型の救済後QA再判定=OPEN-633(Fable予約、修正済み・push待ち)、③`things left out`の訳=OPEN-634(Fable予約、修正済み)。本Trialはこれらと混同せず、N5抽出改善とは別系統として維持する。
