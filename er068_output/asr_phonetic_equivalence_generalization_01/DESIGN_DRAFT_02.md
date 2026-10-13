# DESIGN_DRAFT_02: 発音同等性に基づく一般化ASR判定方式(Opus条件A必須修正1〜4・推奨を反映した改訂版)

管理ID: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_02
**Status: `DESIGN_REVISED`(Opus必須修正反映済み)。** Production無変更・Production採用未承認・実装前。`CURRENT_SPEC.md`へは記載しない。
前版: `DESIGN_DRAFT_01.md`(本書は差分+改訂後の確定事項。変更のない節は01を参照)。再評価: `OFFLINE_EVAL_02.md`。
KPI provenance: 数値は `reuse`(既存転写・既存wav再評価)+`synthetic`(合成反例)。fresh Production初回path E2E値: No。費用JPY0・新規API呼出0・使用モデルなし。

---

## 0. 改訂差分一覧(Opusレビュー指摘 -> 反映箇所)

| Opus指摘 | 反映 | 反映箇所(本書) | 実装(Trial隔離) |
|---|---|---|---|
| **必須1** 基準を綴りから音素へ | 反映(DESIGN_REVISED) | §1・§3段(3) | `derived_phone_forms`/`phoneme_ok`/`m1_candidates`(音素基準、OOVのみ綴りfallback) |
| **必須2** 受理理由の限定 | 反映 | §2 | `ALLOWED_VARIANT_CLASSES`/`m1_try(restrict_reason=True)` |
| **必須3** 配置(Primary#1直後・Tier3前、fallbackはSecondary同意/HR、P2/S1/S2にも) | 反映(設計のみ) | §5 | (Production配線は別委任。未実装) |
| **必須4** V2は暫定保守ゲート、末尾欠損検出は別課題(OPEN-341) | 反映 | §4 | `v2_verdict`(位置づけのみ変更、コード無変更) |
| 推奨 所有格正規化+PASS_WITH_WARNING+audit trail | 反映 | §6 | `normalize_possessive`/`m1_try`の`audit_trail` |
| 推奨 対象限定(en-US narration/dialogue。KP・日本語除外) | 反映 | §7 | (設計のみ) |
| 推奨 `cascade_enabled`/`FEATURE_FLAG_SECONDARY_ASR_ENABLED`依存の明記 | 反映 | §7 | (設計のみ) |
| 推奨 OOV名(Melos)の正しい読み(OPEN-308)は範囲外 | 反映 | §7 | - |
| Q5 F1(最初の差のみ) | 別OPEN-340。M1は`_f1_guard_ok`で「置換後の文のF1経由PASS」を防ぐ | §8 | `_f1_guard_ok`+回帰test |
| Q5 F2 | 別OPEN-342 | §8 | M1側で除外済み(委任_01から不変) |
| Q6 優先順位 | 併記(採否はユーザー) | §9 | - |
| Q7 Eq Layerと統合しない | 反映(音素を引く共通関数のみ共有) | §10 | - |

---

## 1. 判定基準を「綴り」から「音素」へ(Opus必須1)

**旧(委任_01)**: ASRトークンを「canonical語から -s/-es を削った綴り」(`expected_spellings`)と同音の別綴りへ置換。綴りで語幹を作るため、母音・音節・語頭子音が違う語まで受理面に入っていた。実測(下表)で、Opus例6語は**旧基準ではすべて受理**(Moses<-moss、Hades<-haid、Torres<-tore、Giles<-guile、Jones<-Joan、Hayes<-Hey)。

**新**: 受理候補 `cand`(ASR語と同音の別綴り)は、canonical語 `c` の**音素列**から次のいずれかの形に**音素レベルで一致**する場合のみ採る(`derived_phone_forms`)。
| 規則 | 音素列 | 対応する承認済みPattern |
|---|---|---|
| exact | P(c) | 厳密一致(純粋同音) |
| drop_final_S_or_Z | P(c)から語末の /S/ または /Z/ を**1つだけ**除く | Pattern A |
| drop_ed | `-ed`語の語末 /T/ /D/(または /IH D/)を除く | Pattern B |
| add_s | P(c)+/S/ /Z/ /IH Z/ | Pattern C |
- **固有名詞(entity_like)は代表発音(CMUの先頭登録)のみ**、一般語は全変種のいずれか一致(Productionの `entity_word_arpabet_primary_match` / `homophone_arpabet_equivalent` と同基準)。
- 次語が歯擦音始まりという条件は、置換後の文を既存`classify_asr_match`へ流す際にPattern A自身が要求する(新しい条件を足さない)。
- **canonical語がCMU未収録(OOV。例 `Melos`)の場合のみ**、従来の語幹綴り基準へ戻す(`basis=oov_spelling_fallback`、audit trailに記録)。G2Pは未導入のためOOVの音素は推定しない。**この扱いはUSER_DECISION_REQUIRED(4)**(§11)。
- CMU収録canonical語は**綴り基準へ戻らない**。cand側がCMU未収録なら音素を確認できないため不受理。

**Opus例6語のCMU照合(既存`_cmu_variants`=CMU辞書の実測。Opus注の「未照合」を解消)**:
| canonical | ASR綴り | canonicalのCMU(全変種) | ASR綴りのCMU | 旧(綴り基準、01) | 新(音素基準) |
|---|---|---|---|---|---|
| Moses | moss | M OW Z AH S / M OW Z IH S | M AO S | 受理(候補`mos`) | **不受理**(母音・音節が違う) |
| Hades | haid | HH EY D IY Z / HH EY D Z | HH EY D | 受理(候補`hade`) | **不受理**(固有名詞は代表発音=/IY Z/を含む形のみ。語末/Z/だけを除いた列にならない)。注: 一般語扱い(全変種)なら変種2=HH EY D Zで一致するが、固有名詞は代表発音のみ |
| Torres | tore | T AO R EH Z | T AO R | 受理(`torr`/`torre`) | **不受理**(/EH Z/=音節欠落) |
| Giles | guile | JH AY L Z | G AY L | 受理(`gile`) | **不受理**(語頭子音 JH vs G) |
| Jones | Joan | JH OW N Z | JH OW N | 受理(`jone`) | **受理**(P(Joan)=P(Jones)から/Z/を除いた列=真に同一) |
| Hayes | Hey | HH EY Z | HH EY | 受理(`hay`/`haye`) | **受理**(同上) |

`Jones`<-`Joan`・`Hayes`<-`Hey` のような**真に同一音素列**の同音綴りは残る(Pattern A自身が `Hayes said` <- `Hay said` を綴りで受理する既存の性質[OPEN-330]と整合)。受理面の明示的な露出として、ユーザー判断(§11(1))に含める。

## 2. 置換後の文がPASSした「理由」の限定(Opus必須2)

M1の受理は、置換後の文に対する既存`classify_asr_match`の分類が次に限る:
`EXACT_MATCH` / `NORMALIZED_MATCH`(=純粋同音)、`CONNECTED_SPEECH_ACCEPT` / `CONNECTED_SPEECH_PASS_WITH_WARNING` / `CONNECTED_SPEECH_RESEGMENTATION`(=Pattern A/B/C)。
**除外**: `HIGH_SIMILARITY_SAFE`・`NUMERIC_EQUIVALENCE_MATCH`・`HOMOPHONE_EQUIVALENT`(固有名詞差分。F2)等を理由とする受理。理由: `_is_benign_plural_pair`を通る類似度経路は、歯擦音が続かない文脈(例 `Mello called`)の真の/z/欠落を受理し得て、原則2-4(連結発音と単語単体の読みを混同しない)に反する。
除外した旧受理11件(HIGH_SIMILARITY_SAFE 8・NUMERIC 3)の1件ずつの確認は`OFFLINE_EVAL_02.md` §3。

## 3. 7段構造(01 §3の変更点のみ)
- 段(3)音素同等性: **音素列比較**(§1)。同音綴り候補=`homophone_class`(ASR語の同音綴り)∩`expected_spellings`(語幹綴りの候補空間)∩音素基準(`phoneme_ok`)。
- 段(5)既存ルール一貫適用: 置換後の文を既存判定へ流し、**受理理由が§2の集合**であること。
- 段(6)安全条件: 01の4節+**F1ガード**(置換後の文とcanonicalの全差分領域が、M1が置換したトークンを含む領域に限られること。`_f1_guard_ok`)。

## 4. 末尾完全性確認V2の位置づけ(Opus必須4)

- **V2は「M1導入時の暫定的な保守ゲート」**(落ちてもHR行きで悪化しない)。V2をM1だけに課すと、`Melo`(Production既存のPattern A経路でPASS)は末尾確認なし・`Mello`(M1経路)は末尾確認あり=**逆向きの非対称**(`Melo`はPASS、`Mello`はHR)が生じる。これは意図した恒久仕様ではなく、暫定期間の副作用として明記する。
- **末尾欠損の検出は、PASSする全経路に関わる別課題**として**OPEN-341**へ切り出す(M1専用の恒久仕様にしない)。恒久的な方向(全経路へ広げるか、forced alignment等を使うか)はユーザー判断(§11(2))。
- 閾値余裕の薄さ: Production健全wav最大(b1b)は閾値-30dBに対し-30.44dB(差0.44dB)。閾値の根拠は**減速後wav検証20本のみ**。**誤HR増(健全wavが閾値を超えてHRに落ちる)の懸念**がある。誤HRはHR増(運用コスト)で安全側だが、V2をProduction採用する場合は閾値の再較正とHR増の見積りが必要(未実施)。
- V2'の再評価でも増分0(`OFFLINE_EVAL_02.md` §2)だが、合成切詰wav依存(元の末尾無音も除去されるため検出が容易な可能性)で一般的保証ではない(01と同じ限界)。

## 5. 配置(Opus必須3)

**旧案(01)**: `_step_alternate_pass`隣(`er006_secondary_asr_01.py` L739付近)。**問題**: L739はTier3(L598〜)と`force_secondary`(L704)の**後**にしか到達しない。(a)Tier3(Azure)呼出削減の主張が成立しない。(b)fallback音声はSecondary同意必須の既存仕様(Part C)をM1救済が素通りする(既存`_step_alternate_pass`も同じ抜け穴)。

**新案**:
1. M1は**Primary#1判定直後・Tier3の前**(`cls`が`ASR_VALIDATION_UNCERTAIN`となった直後、ローカル処理・API費用0)に置く。これでTier3(Azure corroboration)呼出が実際に減り得る。
2. **fallback(`force_secondary=True`)で救済した場合は、Secondary同意を要求する**(Part Cと同じ。同意しなければHRへ)。M1救済のみで最終PASSにしない。
3. **P2/S1/S2各段**(`_step_alternate_pass(cls_p2/cls_s1/cls_s2)`呼出箇所。L764/L795/L826付近)にも同じ関数を入れる(段ごとに同じ判定思想)。
4. 全経路は`evaluate_attempt_with_cascade[_detail]`を共有するため同時に効く(R1 Std減速前/R2 Std減速後[`_post_slowdown_cascade_rescue`のUNCERTAIN入口]/R3 Advanced/R4 初回/R5 retry・fallback・regeneration/R6 LR後再検証。01 §5の表のとおり)。
5. **Production変更は別委任(Opus条件A済み。実装前に内容変更があればFableが再レビュー判断)+ユーザー承認後。本委任は未実装。**

## 6. 所有格・PASS_WITH_WARNING・audit trail(推奨)
- 所有格 `'s`→`s` の正規化(`Mello's`→`Mellos`)をASR/canonical両方へ同じ関数で適用(`normalize_possessive`)。M1経路のみ。
- **M1受理は`PASS_WITH_WARNING`相当**とし、`ClassificationResult`へ audit trail(`original_asr`[正規化前]、`normalized_asr`、`acceptance_reason`=置換後の既存分類、置換の(from,to,基準[phoneme/oov_spelling_fallback],音素規則)、`possessive_normalized`)を付与する(additive key。Trialの`m1["audit_trail"]`で試作済み)。
- 初出時1回HR・承認後は自動、の運用要否はユーザー判断(§11(4))。

## 7. 対象範囲・flag依存・範囲外(推奨)
- **対象: en-US narration/dialogue**(英語のFULL_STORY本文等のASR判定)。Key Phrase・日本語は対象外(入口条件で除外)。
- **`cascade_enabled`/`FEATURE_FLAG_SECONDARY_ASR_ENABLED`依存は意図どおり**: cascade無効時は既存と同じくM1も走らない(cascade機構の一部として扱う)。
- **OOV名(Melos)の正しい読み(OPEN-308、期待MEE-lahs対実TTS不一致)の確認は本機構の範囲外**。本機構は「ASRが同じ音素列を別綴りで書いた」ことの正規化であり、TTSの発音そのものの正否は判定しない。

## 8. F1/F2との関係
- **F1(Pattern Aは最初の食い違い語だけ見る。`er006_preprod_hardening_01_validation.py` L1076付近)**: 承認時前提(差は1か所)と実装の食い違い=安全上の不備で、M1より優先度が高い(Opus)。是正は判定を厳しくする方向のみだが**既存成果物の判定がPASS→NGに変わり得る**ためユーザー報告のうえ別OPEN(**OPEN-340**)で先行。M1自体はUNCERTAIN限定のためF1を受け継ぐ経路はほぼ無い(L1096/L1101で先に返る)が、**「置換後の文がF1経由でPASSしない」ことを`_f1_guard_ok`+回帰testで担保**(`Delegation02PhonemeBasis.test_replaced_sentence_does_not_pass_via_f1_first_diff_only`)。
- **F2(固有名詞の代表発音基準と`HOMOPHONE_EQUIVALENT`経路の不整合)**: M1側では除外済み。Production是正は**OPEN-342**。

## 9. 優先順位(Opus Q6。採否はユーザー)
実データで救済されるのはMelosのみで効果は小さい。Opus推奨順: **R1(上流対策=語末歯擦音名+歯擦音始まり動詞を避ける、Production化判断) > F1是正 > 修正版M1**(約200行の一貫性是正として優先度低)。本設計は併記のみで、順位の採否はユーザー。

## 10. Eq Layerとの関係(Opus Q7)
Equivalence Layerとは入口・根拠が異なる(Eq Layerは独立ASR corroboration必須・`TRUE_CONTENT_MISMATCH`入口、M1はUNCERTAIN入口・ASRテキストのみ)ため**統合しない**。音素を引く共通関数(CMU参照`word_phones`等)のみ共有候補。

## 11. ユーザー判断候補(Opus後)
1. 優先順位 R1/F1/M1(上記§9)。
2. 暫定期間の非対称(V2をM1のみ。`Melo`=PASS/`Mello`=HR)を許容するか、末尾確認を全経路へ広げる別OPEN(OPEN-341)を先に立てるか。
3. F1是正(OPEN-340)の承認(既存成果物の判定がPASS→NGになり得る)。
4. CMU未収録名(Melos等)で綴り基準へ戻すことを許容するか(=実データ上のMelos救済はこのfallback経由のみ。許容しないと救済は0)+初出時1回HR運用の要否。

## 12. Opus論点への回答(DESIGN_DRAFT_01 §8、転記)
1. **等基準の方向**: (a)Pattern Aの基準を同音へ広げる案を、音素基準+理由限定で受理面を絞って採る(54語プローブ: 旧17語/38綴り→新10語/21綴り。OOVのMelos以外はすべて音素列が真に同一)。(b)Pattern A自体の厳格化は承認済み仕様の変更=別判断(ユーザー)。
2. **配置**: §5。
3. **V2の十分性**: 暫定保守ゲート(§4)。恒久策は別OPEN-341。
4. **増分誤PASS基準**: V1'は増分28(REJECTED)、V2'は0(合成依存、一般的保証ではない)。
5. **F1**: 別OPEN-340(§8)。
6. **F2**: 別OPEN-342。
7. **PASS_WITH_WARNING+audit trail**: 反映(§6)。初出1回HRの要否はユーザー判断。
8. **stem+規則的-s/別の実在語**: 音素基準で別語(Moses/moss等)は排除。真に同一音素列(Joan/Hey)は残り、受理面として明示(§1)。
9. **Eq Layer境界**: 統合しない(§10)。
10. **評価の十分性**: 実データ上の救済はMelosのみ(OOV fallback経由)。一般化の実データ効果は未実証(OPEN-335のHR verdict保存が前提)。

## 付: 未検証事項
01の未検証事項(自然発生末尾欠損・Melos以外の実データ救済・Production統合後のTier3削減効果)に加え: V2の閾値余裕0.44dB・減速後20本のみ(誤HR増の定量未実施)、`HIGH_SIMILARITY_SAFE`除外が実運用のMelos救済率に与える影響(実データ上、旧11件が不受理へ)。
