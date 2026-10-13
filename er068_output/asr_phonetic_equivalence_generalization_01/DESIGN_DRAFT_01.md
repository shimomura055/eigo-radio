# DESIGN_DRAFT_01: 発音同等性に基づく一般化ASR判定方式(設計草案、Opus条件Aレビュー用)

管理ID: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01
**Status: `DESIGN_DRAFT`(Opus独立技術レビュー条件A待ち)。Production無変更・Production採用未承認・実装前。** 本書は設計草案であり、`CURRENT_SPEC.md`へは記載しない。
関連: `docs/pm/design_principles/connected_speech_proper_noun_phonetic_equivalence_2026-10-13.md`(上位原則)、`GAP_MAP_01.md`(既存機構との対応)、`OFFLINE_EVAL_01.md`(read-only検証)。
KPI provenance: 数値はすべて `reuse`(既存転写・既存wav再評価)+`synthetic`(合成反例)。fresh Production初回path E2E値: No。費用JPY0・新規API呼出0・使用モデルなし。

---

## 0. 結論の要約(先に)

1. **主軸の推奨 = 方式M1「ASR側のCMU確認済み同音綴り正規化 → 既存Pattern A/B/C・厳密一致へ帰着」**(Pattern Aの綴り比較を、新しい受理基準を作らずに音素同等性へ一般化する)。Eq Layerの入口拡張(OPEN-122(4))とTrial音韻判定の説明付きHR化は、M1の**補助**であり、別判断。
2. **ASRテキストだけの方式(V1)は採用候補から外す(`REJECTED`候補)**。理由: 既存Pattern A比の誤PASS増分が**28件**(`said`語末を70〜220ms切詰めた合成音声。ASR転写がintactと同一=`mello said`/`mellow said`/`mellos said`のため区別不能)。委任文の規則(Pattern A比増分>0は採用候補から外す)に該当。
3. **M1 + 末尾完全性の独立確認(V2)は、同じデータで増分0**。ただし(a)切詰wavは「発話末削除+8ms fade」で元の末尾無音も失われる合成物であり検出が実際より容易な可能性、(b)B2/B4の一部は末尾チェックを通過、(c)自然発生した末尾欠損の真値付きwavが無い、のため**一般的保証ではない(未検証)**。V2の採否は`USER_DECISION_REQUIRED`(Opusレビュー後)。
4. **受理面が広がる**(構成プローブ: s終わり固有名詞54語中17語で、Pattern Aが受理する綴りに38個の同音綴りが追加される。`Jones`←`Joan`、`Hayes`←`Hey`、`Torres`←`Tore`等、語末sが元から無い別の実在語・別名も含む)。これは「同じ音素列には同じ判定」というユーザー原則の帰結だが、**誤PASS露出の増分**であり、既存Pattern Aの性質(OPEN-330)の延長。Opus/ユーザーの判断対象。
5. 実データ(HR queue・telemetry・run_e2e_02)では、M1が新たに救済する対象は**Melosの`Mello/Mellow/Mellos/Mellows`のみ**(Melos以外0件)。一般化は機構として働くが、**実データ上の効果はMelos以外で未実証**(OPEN-335: HR verdict未保存)。

---

## 1. 既存機構の再利用・拡張点(新機構を作らない)

### 1-1. 候補3案の比較

| 案 | 内容 | 長所 | 短所(実測根拠) | 評価 |
|---|---|---|---|---|
| **A. Eq Layer入口拡張** | Equivalence Layer(`er011_connected_speech_equivalence_layer_production_01.py`)の入口を`TRUE_CONTENT_MISMATCH`限定から`ASR_VALIDATION_UNCERTAIN`(固有名詞・同音語)/減速後へ広げる | 音素水準+**独立ASR corroboration必須**で最も安全。承認済み機構の再利用 | (i)Melos型は独立ASR(Azure)も`Mellow`と書くためcorroboration不成立=**救済0件**でHRは減らない(CS_AUDIT)。(ii)OOV固有名詞のG2P不在(`word_phones("melos")=None`)。(iii)減速後のflag未配線(OPEN-122(4))は承認範囲の拡張=別仕様判断 | 同音異綴り問題の**主軸には不適**(別途OPEN-122(4)として独立に判断) |
| **B. Pattern Aの綴り比較を音素比較へ一般化(=M1)** | ASR側トークンを、CMUで**確認済みの同音**(代表発音、固有名詞)/全変種一致(一般語)の別綴りのうち承認済みPattern/厳密一致が期待する綴りへ置換し、置換後の文を**既存判定**(`classify_asr_match`)へそのまま流す | 新しい受理基準を作らない(一貫性公理のみ)。Melo/Mello非対称の直接解消。全経路が共通して通る判定の内側=**6経路同時適用**。辞書駆動でMelos hardcode不能。追加ASR呼出0 | text-onlyは末尾切詰で増分誤PASS(28)。受理面拡大。既存Pattern Aの穴(first-diff-only、語幹末s)を継承しない部分と継承する部分あり(4節) | **推奨(V2=末尾完全性確認付きで)** |
| **C. Trial音韻判定`three_way_with_flags`を主軸** | 説明付きHR候補化のみ(自動許容なし) | 安全(増分0)。HR確認の説明が付く | HR件数を減らさない(確認時間の短縮のみ、OFFLINE_EVAL §1-2のHR候補は延べ24件)。ユーザー原則「同じ現象に同じ判定」に応えない(Melo=PASS/Mello=HRの非対称が残る) | M1の補助(診断情報)としてのみ使用 |

**推奨: B(M1)を主軸、末尾完全性の独立確認(V2)を必須条件に、Cの説明付きHR候補(M2)を診断・降格先として併用。Eq Layer入口拡張(A)は独立判断(OPEN-122(4))。**

### 1-2. M1の再利用する既存部品
- `val.classify_asr_match`(`protected_check`・entity gate・Pattern A/B/C・Tier1・HIGH_SIMILARITY等)を**そのまま呼ぶ**(M1は置換した文を流すだけ)。
- CMU(`pronouncing`)・保守基準(固有名詞=代表発音、一般語=全変種)は`er008_asr_variant_hardening_15_homophone_en.py`と同じ基準を踏襲。
- Trial音韻判定(`er065_..._p2_phon.py` `explain_diff`/`risk_flags`)はM2(診断)で再利用。新機構は「ASR側同音綴りの正規化」+「末尾完全性確認」のみ。

---

## 2. 発音確認の手段

| 手段 | 位置づけ | 本設計での扱い |
|---|---|---|
| CMU Pronouncing Dictionary(`pronouncing`) | 一般語は実発音を概ね反映。固有名詞は偶然・不正確な登録あり(`Tse`の実例) | 一般語=全変種のいずれか一致(既存`homophone_arpabet_equivalent`と同基準)。**固有名詞(entity_like差分)=代表(先頭)発音一致のみ**(既存`entity_word_arpabet_primary_match`と同基準) |
| 確認済み発音辞書・Pronunciation Ledger | Ledgerは`confidence=low`(辞書推定)をTTS注入対象外としている | `confidence`が確認済み相当のエントリのみ「確認済み」と扱う案(本草案では未実装・未検証)。`melos`(期待読みMEE-lahsと実TTSが不一致=OPEN-308、low)は確認済みと扱わない |
| stem+規則的-s(`mellos`←CMU収録`mello`+Z) | 推定ではなくCMU確認済みstemへの規則的接尾辞 | `cmu_stem+regular_s`と**根拠を記録**して許容(stemがCMU収録の場合のみ)。stemがCMU未収録なら音素を推定しない(M1は発火せず既存判定) |
| G2P(`g2p_en`等) | **未導入**。新規依存(PyPI依存・ライセンス・依存パッケージ=未確認) | **使わない**。OOV stemの音素推定は「確認済み」と認めない(推定を許容根拠にすると偽の同等性を作る)。G2P導入はユーザー承認+Trial+Opusの別判断(PHASE2_REPORT_02) |
| canonical側の音素推定(`derived_stem_s`) | 綴りからの推定(R2) | **M1は使わない**(canonical側の音素は参照せず、ASR側が確認済みCMU語であることだけに依存)。M2の診断のみ使用 |

G2Pなしで成立する範囲=「ASRが書いた綴りがCMU収録語(またはCMU収録stem+規則的s)」。OOV綴りの転写(例 `Mellus`、`melloset`)は対象外→既存判定のまま(誤許容回避)。

---

## 3. 7段構造の各段の入出力と判定表

| 段 | 入力 | 処理 | 出力 | 実装(Trial隔離プロトタイプ `er068_..._offline.py`) |
|---|---|---|---|---|
| (1) 差分検出 | canonical, asr | トークン差分(difflib、全差分) | 差分領域リスト | `P.tokens`+`difflib.SequenceMatcher`(`m1_candidates`)。**全差分領域を見る**(Pattern Aのfirst-diffのみを補う) |
| (2) 発音確認 | 差分トークン | CMU確認済み発音の有無・根拠(`cmu`/`cmu_stem+regular_s`/`none`)、固有名詞は代表発音のみ | 発音+根拠 | `homophone_class(token, primary_only=)` |
| (3) 音素同等性 | ASR語の発音 | 同じ音素列の別綴りの集合 | 同音綴り候補 | CMU逆引き(代表発音/全変種)。承認済みPattern/厳密一致が期待する綴り(`expected_spellings`)との交差のみを採る |
| (4) 区別診断 | 候補+周辺 | 同音異綴り / 連結(融合・弱化・脱落) / 再分割を区別 | 診断ラベル | M1=同音異綴り→**既存Pattern(融合型)へ帰着**。M2=`explain_diff`が連結/再分割/voicingを診断(自動許容しない) |
| (5) 既存ルール一貫適用 | 置換後の文 | `val.classify_asr_match`を**そのまま**呼ぶ | 既存判定 | `prod_judge(canonical, asr2)`。PASSならACCEPT_M1(新受理基準なし) |
| (6) 安全条件 | — | 下記4節 | 受理/降格 | `protected_check`(既存)・Production判定がPASSを返すことが必須・末尾確認(V2) |
| (7) 根拠不十分 | — | 説明不能・OOV・確認不能は無条件PASSにしない | 既存判定/HR | DEFER_*(既存判定のまま) |

### 判定表(出力ラベル)

| ラベル | 意味 | 自動PASS | 備考 |
|---|---|---|---|
| EXACT | 綴り一致 | (既存) | 本機構の対象外 |
| PROD_PASS_UNCHANGED | Productionが既にPASS | (既存) | **判定を変えない**(F1のように既存の誤PASSも変えない) |
| ACCEPT_M1 | 同音綴り正規化後、既存判定がPASS | 条件付き(V2: 末尾確認OKのみ。警告付きPASS+audit trailを推奨、Opus論点) | Melo/Mello非対称の解消 |
| HR_CANDIDATE_EXPLAINED | 音素水準で連結発音と説明できるが自動受理しない | しない | HR件数は減らさず、確認時間を短縮 |
| HR_CANDIDATE_RISK_FLAGGED | 同上+否定/数/時制/辞書語別語化のフラグあり | しない | 警告併記 |
| HR_CANDIDATE_TAIL_UNCONFIRMED/SUSPECT | M1成立だが末尾完全性が確認不能/疑い | しない | V2の降格先 |
| DEFER_PROTECTED_FAIL | 数字・否定の不一致(`protected_check`不通過) | しない | 本機構を適用しない |
| DEFER_NOT_EXPLAINED | 連結発音で説明不能・OOV・音素証拠なし | しない | 既存判定へ委譲(判定を変えない) |

---

## 4. 安全条件

1. **`protected_check`通過後にのみ適用**: M1は`val.classify_asr_match`の判定が`ASR_VALIDATION_UNCERTAIN`(固有名詞・同音語のみの差)の場合に限る。`TRUE_CONTENT_MISMATCH`(内容語の差)は**覆い隠さない**(Eq Layer入口の別問題)。数字・否定の不一致は`DEFER_PROTECTED_FAIL`。
2. **置換は、Productionがフラグした差分語のみ**に限る(機能語や無関係な語への副作用を排除)。
3. **新しい受理基準を作らない**: 置換後の文を既存判定へ流し、既存判定がPASSの場合のみACCEPT。ただし**固有名詞差分に対して`HOMOPHONE_EQUIVALENT`(CMU全変種一致)でPASSとなる経路は受理根拠にしない**(F2: 代表発音のみの保守基準を回避させない)→M2のHR候補止まり。
4. **`risk_flags`**(否定・数・時制/語尾・辞書語別語化): M2側でフラグがあれば説明付きでも自動受理しない(Trialで既存)。
5. **末尾完全性の独立確認(V2)**: ASRテキストは末尾切詰を区別できない(offlineで増分28件を実測)。**末尾完全性の独立確認が必要**(要否の結論=必要)。最小プロトタイプ=末尾50msの最大フレームRMSが、clipのp95フレームRMS比-30dB以下(閾値はProduction健全wav97本のみから決定、切詰wavでは調整していない)。**限界(未検証)**: 合成切詰が末尾無音も除去する・B2/B4の一部は未検出・自然発生欠損の真値wavなし。より堅い代替=forced alignment/Azure Pronunciation Assessment(未導入、費用未確認、OPEN-327の次Trial候補)。
6. **音響の摩擦区間長は許容の根拠にしない**(AUC=0.74で単独gate不可、REJECTED)。
7. **文脈付きASR結合は許容根拠にしない**(C-c REJECTED)。
8. 既存のretry/fallback/regeneration上限・cool-down・HR Lock・Slowdown Gate・予算ガードを**変更・回避しない**。M1は追加ASR呼出を行わず、むしろTier3(Azure)呼出を減らし得る。
9. 既存の穴(F1: Pattern Aはfirst-diffのみ)は、M1がUNCERTAIN限定(複数の無関係差分があればTRUE_CONTENT_MISMATCHになりM1対象外)のため継承しないが、**既存のPattern A経路そのものには残る**(本設計は変更しない。OPEN-339サブ項目)。

---

## 5. 6経路すべてへの適用方法と「減速前後で判定思想が変わらない」担保

**配置案(推奨)**: 共有cascade内の`_step_alternate_pass`(`er006_secondary_asr_01.py` L423、呼出 L739/L764/L795)の隣に`_step_phonetic_pattern_equivalence(cls, canonical, asr, wav_path)`を追加する案(**Production変更はOpus条件A+ユーザー承認後の別委任。本委任では未実装**)。全経路は`evaluate_attempt_with_cascade[_detail]`を共有するため同時に効く:

| 経路 | 呼出点(既存) | M1が効く理由 |
|---|---|---|
| R1 Std減速前 / R4 初回 / R5 retry・fallback・regeneration | `secondary_asr.evaluate_attempt_with_cascade`(`er003_v1_crosslevel_audio_02_common.py` L348、`er003_v1_repro01_main_generate.py` L349、`er012_b_family_voices_production_01.py` L549ほか) | 各attemptのPrimary/Secondaryがcascade内で判定される |
| R2 **Std減速後** | `apply_a2_slowdown_postprocess`(`er003_v1_n3_01_tts_generate.py` L169)→`_post_slowdown_cascade_rescue` L117→`evaluate_attempt_with_cascade_detail`(UNCERTAINのみ) | M1の対象=UNCERTAIN(固有名詞・同音語のみの差)であり、rescueの入口条件と**一致**する(Eq Layerとは違いdead wiringにならない)。**減速後に対象外となるTRUE_CONTENT_MISMATCHはM1も対象外**(OPEN-122(4)の別問題、同じ区別を維持) |
| R3 Advanced | `er003_v1_sing01_news_tail_fix.py` L202、`er003_v1_sing01_voice01_generate.py` L238 | 同上 |
| R6 LR後再検証 | `run_local_rewrite_recovery`(er020 L686)後の再TTS+ASR=上記と同じcascade | 同上 |

**減速前後で判定思想が変わらないことの担保**:
1. 判定関数`design_judge(canonical, asr)`は**入力に経路・減速・role・engineを持たない純関数**(test固定: `SlowdownAndRouteInvariance`)。
2. 同一転写の対は必ず同一判定(offline: 減速前後の転写が同一の15対で**15/15一致**)。転写が異なる場合の揺れは判定器ではなくASR揺れ(全34対で群一致 V0=29/34、V1=26/34)。
3. 実装時は、減速前後で同じ関数を呼ぶ**呼出点の静的test**(`_step_phonetic_pattern_equivalence`が`_post_slowdown_cascade_rescue`から到達可能であること)を追加する(実装委任の受入条件)。
4. 末尾確認(V2)は**減速後の最終wav**で行う(6%伸長後でも健全wavは通る: reeval_post_slowdown 20 wavで確認、ただし20件のみ)。

---

## 6. Melos専用hardcodeでないことの担保(綴り個別登録の禁止)

1. 機構は**辞書駆動**: 置換候補は(a)ASRトークンのCMU同音綴り集合、(b)canonical語から機械的に導く承認済みPattern/厳密一致の期待綴り(`expected_spellings`: -s/-es/-ies/-ed除去、-s/-es付加)の**交差のみ**。個別の綴りを列挙する設定・辞書・allow-listを持たない。
2. test固定: 機構関数のソースに`melos`/`mello`/`mellow`/`melo`の**文字列リテラルが無い**ことを検証(`NoHardcodeAndIsolation.test_no_melos_literals_in_mechanism_source`)。
3. Melos以外の名前(`Carlos`/`Giles`/`Lucas`等、CMU収録stemを持つ名前)に同じ機構で効くことをtest固定。
4. 受理面プローブ(54語)で「Melos以外にも機構が働く」ことと、その**露出増分**を定量化(OFFLINE_EVAL §5)。
5. 設計上、作品単位allow-list(綴りの個別登録)は本機構の**外**(OPEN-327/331の別判断。「その名前の語末s脱落リスクを許容する方針決定」と等価)。

---

## 7. 実装規模・影響範囲・回帰test計画・費用見積

- **実装規模(実装委任時の見積り、本委任では未実装)**: 新規module約200行(`homophone_class`/`expected_spellings`/`m1_candidates`/`m1_try`/末尾確認、Trialプロトタイプから移植)+共有cascadeへの1関数追加+`ClassificationResult`にadditive key(`phonetic_equivalence_info`、観測性=OPEN-328と整合)。**既存判定コード(Pattern A/B/C・protected_check・Eq Layer)は無変更**。影響範囲=共有cascade経由の全英語narration経路(Key Phrase・日本語は対象外にできる)。
- **回帰test計画**: 既存 er065回帰32件・er026 CS監査12件・er026減速後16件・Eq Layer production wiring(ALL PASS)・er011全体(295件中292 PASS、3件失敗は本件無関係の既存prompt byte-parity)が**不変**であること。実装時は`ProductionCharacterization`(`Mello`未受理を固定しているtest)を**意図的に反転**して更新する(「この固定が崩れたら是正が入った合図」)。新規: er068 test 23件(本委任)をProduction版へ移す+全6経路の呼出点静的test。
- **今回のoffline検証の限界**: 実データでの救済はMelosのみ(Melos以外0)。評価Bの真値は合成/proxy中心でHR verdict実データなし(OPEN-335)。実際に語末sを落とした音声(R1の核心)の真値wavなし。
- **費用**: 本委任=JPY0(有料API 0)。M1自体は追加ASR呼出なし(ローカル辞書+ローカルDSP)=**運用費増なし**、Tier3(Azure)呼出が減る可能性(定量化は未確認)。有料検証が必要になる場合(自然末尾欠損の実測、forced alignment/Pronunciation Assessment)は**実行せず**見積のみ: Pronunciation Assessmentの単価は**未確認**(未導入、プロジェクト未使用)。既存の参照単価(出典: `er065_output/short_clip_asr_context_trial_01/TRIAL_REPORT_01.md`・PHASE2_REPORT_02): Azure STT約JPY0.044/音声秒、OpenAI `gpt-4o-mini-transcribe`約JPY0.004/秒(**音声入力単価は未確認**、実計上は約JPY0.0052/秒、usage画面照合要)。
- **時間**: 実装委任=Sonnet1回+回帰+Opusレビュー。並列化: M1実装とEq Layer入口拡張判断(OPEN-122(4))は独立で並列可。

---

## 8. Opusレビューで問うべき論点(条件A)

1. **等基準の方向**: ユーザー原則「同じ音素列には同じ判定」を、(a)同音異綴りへPattern Aの基準を広げる(M1、受理面拡大: 54語中17語で38綴り追加)か、(b)既存Pattern Aにも独立証拠(corroboration)を課す=Melo/Melloを**揃って**厳格化するか。(b)は承認済みPattern Aの変更(新Production仕様、HR増)。どちらが妥当か、混合(固有名詞のみ厳格)はどうか。
2. **配置**: `classify_asr_match`のentity gate前(Pattern A直前)か、cascadeの`_step_alternate_pass`隣か。後者を推奨(分類関数の意味を変えず、全経路が共有)。Primary#1段階でM1を許すことの妥当性。
3. **末尾完全性確認(V2)の十分性**: エネルギー閾値方式は合成切詰の一部しか検出しない(B2/B4未検出あり)。forced alignment/Pronunciation Assessmentを必須にすべきか。自然な欠損の真値収集方法。
4. **増分誤PASSの許容基準**: V1の増分28(REJECTED候補)をV2で0にできるが、合成依存。Pattern A比増分0を「受入条件」とする場合の追加評価(自然欠損wav、実際のs脱落wav)をどう設計するか。
5. **F1(Pattern Aのfirst-diff-only)**: 同じ変更で後続差分も検査するか、別OPEN(OPEN-339サブ項目)か。M1はUNCERTAIN限定でF1を継承しないが、M1と無関係に既存の穴が残る。
6. **F2(固有名詞の代表発音基準と`HOMOPHONE_EQUIVALENT`の不整合)**: Production側を是正するか(新仕様/配線漏れの区別、21節)。
7. **`PASS_WITH_WARNING`+audit trail(初出は1回HR、承認後再登場は自動)**をM1のACCEPTに必須とするか。作品単位allow-list(OPEN-327/331)との関係。
8. **stem+規則的-s**(`Mellos`←CMU収録`mello`+Z)を「確認済み発音」と認めてよいか。同音綴りクラスに**別の実在語・別名**(Joan/Hey/Tore/Moss)が含まれる場合の抑止策(例: 固有名詞はcanonical語の語幹と同音であることのみ・一般語辞書との衝突を警告)が必要か。
9. **Eq Layer入口拡張(OPEN-122(4))との境界**: M1とEq Layerを「音素同等性」の単一モジュールに統合すべきか、別機構として併存すべきか。
10. 評価の十分性: 実データでの救済がMelosのみ(Melos以外0)で「一般化」を主張できるか。追加の実データ(OPEN-335のHR verdict保存)が前提か。

---

## 付: 未検証事項の一覧
- 自然発生したTTS末尾欠損・実際の語末s脱落音声に対するV2の検出力(未検証)
- Melos以外の実データでの救済効果(未検証。実データに存在しない)
- ledger confidenceを「確認済み」と扱う案(未実装・未検証)
- Production統合後の追加ASR呼出削減効果(未確認)
- G2P導入の依存・ライセンス・効果(未確認、導入しない前提)
