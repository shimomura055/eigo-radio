# OFFLINE_EVAL_02: 音素基準・受理理由限定へ改訂したM1の既存データ read-only 再評価

管理ID: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_02 / 費用 JPY0 / 新規API呼出 0 / 使用モデル: なし(CMU辞書・ローカルDSPのみ、最新モデル原則の対象外=モデル不使用) / Production無変更
KPI provenance: 数値はすべて `reuse`(既存転写・既存wav再評価)+`synthetic`(合成反例)。fresh Production初回path E2E値: No。
データ: 委任_01と**同一**(実データ=HR queue+er021 telemetry先頭7155行+Melos run_e2e_02、合成反例、減速前後対、一般語2語窓)。生成: `offline_eval_02.json`(全レコード)、`OFFLINE_EVAL_02_auto.md`(自動生成表、01と同形式)、`analysis_02.json`(01対02の差分・11件・プローブ)。
比較: **V1'**=改訂M1(音素基準+受理理由限定+F1ガード+所有格、ASRテキストのみ)、**V2'**=V1'+末尾暫定ゲート(Opus必須4: 暫定保守ゲート)。01のV1/V2と対比。

## 1. 評価A(正常音声の誤NG削減)と評価B(誤PASS増分)

| 指標 | 委任_01 V1 | **V1'** | 委任_01 V2 | **V2'** |
|---|---|---|---|---|
| 評価A 実データ系(real_pairs_612・general_2word_fusion/control・melos_takes_alone・control_synth_intact・reeval_post_slowdown_primary、n=1030、V0 PASS 213)の新規ACCEPT | 68 | **64** | 40 | **41** |
| 評価A 正常想定の全データセット(n=1483、V0 PASS 438) | 116 | **114** | 40 | **41** |
| **評価B 誤PASS増分**(欠陥363件、既存誤PASS V0=179。Pattern A比の増分) | 28 | **28** | 0 | **0** |
| 増分の内訳 | defect_synth_tail_trunc 28 | defect_synth_tail_trunc 28 | - | - |
| Melos以外の新規ACCEPT | 0 | **0** | 0 | **0** |

- 判定規則(委任文): Pattern A比増分>0は採用候補から外す。**V1'は増分28 → `REJECTED`(ASRテキストだけの方式は不可)**。増分は`said`語末を70〜220ms切詰めた合成音声(転写がintactと同一で区別不能)で、改訂でも不変。
- **V2'は増分0 → `USER_DECISION_REQUIRED`**(根拠: 増分0は合成切詰wav依存で一般的保証ではない。実データの救済は**Melosのみ**で、かつ**OOV fallback経由のみ**[§4]。V2は暫定保守ゲート[DESIGN_DRAFT_02 §4]で、`Melo`=PASS/`Mello`=HRの逆向き非対称が出る。閾値余裕0.44dB[B1B健全wav最大-30.44dB vs -30dB]・減速後20本のみ=誤HR増の懸念。優先順位はOpus推奨R1>F1>M1)。
- 01→02の判定変化(全レコード): ACCEPT_M1→説明付きHR候補 7、ACCEPT_M1→DEFER 4(いずれも§3の除外11件)、説明付きHR候補→ACCEPT_M1 9(いずれも**所有格正規化**による: `Mello's said`/`Mello's called`等。受理理由はEXACT 2・NORMALIZED 7。PASS_WITH_WARNING+audit trailで原綴りを保持)。
- 評価A 内訳(`OFFLINE_EVAL_02_auto.md` §1-1): 新規ACCEPTの正規化はすべて `melos` canonical(`mello/mellow/mellos/mellows`←`melo/melos`)、基準は **oov_spelling_fallback**(Melosは CMU 未収録)。**CMU収録名での新規ACCEPT=0**(実データに存在しない)。

## 2. 末尾暫定ゲート(V2')の較正・検出率(01と同じ。コード無変更)
- 健全wav: Production a2 narration 48本(最大 rel_tail -38.23dB)、b1b narration 49本(**最大 -30.44dB、閾値-30dBとの差0.44dB**)。全て tail_ok。
- 合成切詰wav(defect_synth_tail_trunc、150観測=12 wav): 9 wavで検出、syn_B2_trunc140・syn_B4_trunc140・syn_B4_trunc70 の3 wavは未検出(01と同じ。V2'増分0はこの合成セットのみ=一般的保証ではない)。
- 注意(未検証): 合成切詰は元の末尾無音も同時に除去するため検出が容易な可能性。自然発生の末尾欠損の真値wavは無い。**この限界を理由に、V2は暫定保守ゲートであり、末尾欠損の恒久検出は別OPEN-341**。

## 3. 除外した旧受理11件(HIGH_SIMILARITY_SAFE 8・NUMERIC 3)の1件ずつの確認(Opus必須2)

すべてcanonical語=`melos`(CMU未収録=OOV)。列「音素基準+理由限定(V1')」が現在の判定、「音素基準・理由制限なしの場合」「旧(01)の理由」は参考。「Production自身の判定」はすべて `ASR_VALIDATION_UNCERTAIN`(M1適用前)。

| # | データ | 1件 | ASR綴り→置換 | 旧(01)の受理理由 | 音素/OOV基準で受理されるか(理由制限なし) | **V1'(理由限定後)** |
|---|---|---|---|---|---|---|
| 1 | real_pairs rp177 | `...Brown water r...`(長文) | mellow→melo | HIGH_SIMILARITY_SAFE | 受理(OOV fallback。次語`searched`=歯擦音始まりだが、長文で他の差分もあり局所Pattern Aでなく類似度理由で通過) | **説明付きHR候補** |
| 2 | rp178 | `...One grabbed hi...` | mello→melo | HIGH_SIMILARITY_SAFE | 受理 | **説明付きHR候補** |
| 3 | rp182 | `...hands held out for the chains...` | mello→melo | HIGH_SIMILARITY_SAFE | 受理 | **DEFER(既存判定のまま=UNCERTAIN)** |
| 4 | rp575 | `...Brown water r...` | mellow→melo | HIGH_SIMILARITY_SAFE | 受理 | **説明付きHR候補** |
| 5 | rp576 | 同上 | mello→melo | HIGH_SIMILARITY_SAFE | 受理 | **説明付きHR候補** |
| 6 | rp577 | 同上(句読点違い) | mellow→melo | HIGH_SIMILARITY_SAFE | 受理 | **説明付きHR候補** |
| 7 | rp596 | `...sister's laugh rose...` | mellows→melos | NUMERIC_EQUIVALENCE_MATCH | 理由制限だけなら受理されるが、**F1ガードで不受理**(置換と無関係な他の差分が残る) | **DEFER** |
| 8 | rp600 | `...hands held out for the chains...` | mello→melo | HIGH_SIMILARITY_SAFE | 受理 | **DEFER** |
| 9 | rp601 | 同上 | mellos→melos | NUMERIC_EQUIVALENCE_MATCH | 受理 | **説明付きHR候補** |
| 10 | slowdown run_e2e_02:...c1:2:12689:post | 同上 | mello→melo | HIGH_SIMILARITY_SAFE | 受理 | **DEFER** |
| 11 | slowdown ...c1:3:12692:pre | 同上 | mellos→melos | NUMERIC_EQUIVALENCE_MATCH | 受理 | **説明付きHR候補** |

読み取り: 11件中10件は、理由制限を外せば(OOV fallback基準では)受理されてしまう=**受理の分かれ目は音素基準ではなく受理理由の限定(必須2)**(残る1件rp596はF1ガードで不受理)。次語は searched/struck(歯擦音始まり)・drank/listened(非歯擦音)が混在し、いずれも長文中の他の差分と合わさってPattern A/純粋同音ではなく類似度/数値同値理由で通過していたもの。11件とも真値は`unknown`(HR待ち。OPEN-335: HR verdict未保存)で、正常か否かの真値はない。**11件の再救済要否は、ユーザー判断(DESIGN_DRAFT_02 §11(4))と実データのHR verdict保存に依存**。詳細は`analysis_02.json`の`excluded11_full`。

## 4. 実データ上の救済の実態
- 新規ACCEPT(V1')の正規化(from→to←canonical、基準、件数): mello→melo←melos(oov_spelling_fallback)55、mellos→melos←melos 40、mellow→melo←melos 30、mellows→melos←melos 17(重複を含む全データセット延べ)。**CMU収録canonicalでの実データ上の新規ACCEPTは0**。
- したがって「Opusが指摘した音素の違う語(Moses/moss等)の受理」は実データには現れず、改訂の効果は**受理面(構成プローブ)の縮小**として現れる(§5)。実データ上の救済はMelosのみ・OOV fallback依存(USER_DECISION_REQUIRED(4))。

## 5. 受理面プローブ(54語×歯擦音始まり動詞6語、構成のみ・真値なし)の再計算

| | 01(綴り基準) | **02(音素基準)** |
|---|---|---|
| 追加の同音綴りがある名前数 | 17語 | **10語** |
| 追加綴り延べ | 38個 | **21個** |

02で残る追加綴り(「真に同一音素列か」: 全件 **Yes**=P(綴り)=P(名前)から語末/S/または/Z/を1つだけ除いた列。CMU代表発音で照合):
| 名前 | 追加の同音綴り | 名前のCMU | 綴りのCMU | 真に同一音素列 |
|---|---|---|---|---|
| Carlos | carlough, carlow, karlow | K AA R L OW S | K AA R L OW | Yes |
| Lucas | lucca, luka | L UW K AH S | L UW K AH | Yes |
| Jones | joan | JH OW N Z | JH OW N | Yes |
| Wells | welle | W EH L Z | W EH L | Yes |
| Mills | mil, mille | M IH L Z | M IH L | Yes |
| Hayes | haigh, hey | HH EY Z | HH EY | Yes |
| Santos | santow | S AE N T OW S | S AE N T OW | Yes |
| Silvas | cilva, sylva | S IH L V AH Z | S IH L V AH | Yes |
| Haynes | hahne, hain, hane, heyn, heyne | HH EY N Z | HH EY N | Yes |
| Melos(OOV) | mello, mellow | (CMU未収録) | M EH L OW | n/a(OOV fallback=綴り基準) |

→ 旧で入っていた別音素の語(Moses<-moss、Torres<-tore、Giles<-guile、Hades<-haid 等)は消えた。残るのは、同じ音素列を持つ別実在語・別名(Jones<-Joan、Hayes<-Hey 等)で、Pattern A自身の性質(OPEN-330)の延長。ユーザー判断の対象(§11(1))。

## 6. 減速前後の判定一致(Std 6%減速)
- 同一転写の対: 15対で判定一致 **15/15**(判定はcanonicalと転写の純関数、減速・経路・role・engineを入力に持たない。テスト固定)。
- 全34対でのPASS/HR/DEFER群一致: V1'=26/34(01と同じ。不一致は減速でASR転写自体が変わるため=判定器でなくASR揺れ)。
- 注意: 減速前後は同一wav対ではなく同一take対。

## 7. 回帰・state guard
- er068 test: **32 passed**(委任_01の23件のうちGiles/Guile 1件を音素基準へ更新+新規9件)。
- er065回帰 32件 OK、er026 CS監査 12件 OK、er011 Eq Layer production wiring ALL PASS。
- 実行しなかった共有ファイル追記系(er026 post_slowdown rescue test、`run_project_regression --pattern er011*`)は委任文どおり未実行。
- state guard(9ファイル、実行前後sha256/行数): 全て不変(`state_guard_02.json`、`state_guard_start_02.json`/`state_guard_end_02.json`)。

## 8. 結論(Status)
| 方式 | Status | 根拠 |
|---|---|---|
| V1'(ASRテキストのみ、音素基準・理由限定) | **REJECTED** | Pattern A比の誤PASS増分28(末尾切詰、転写がintactと同一で区別不能) |
| V2'(+末尾暫定ゲート) | **USER_DECISION_REQUIRED** | 増分0(合成依存)。実データ救済はMelosのみ(OOV fallback経由)。暫定非対称・閾値余裕0.44dB・減速後20本のみ=誤HR増懸念。優先順位はOpus推奨 R1>F1>M1 |
| 設計 | **DESIGN_REVISED(Opus必須修正反映済み)** | DESIGN_DRAFT_02.md |
Production採用宣言なし。ユーザー判断4件(DESIGN_DRAFT_02 §11)は追加探索せず報告。
