# U1_U2_SECTION_PLAN_09 (AUW `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_09)

性質: read-only調査・実装計画。Production code / Prompt / SSOT / 既存ファイルは無変更。Git操作なし。有料API 0(JPY 0)。
到達上限Status: `PLAN_READY`(Fableが承認し、Opus条件Cレビュー要否を判断して委任_10で実装)。
作成: 2026-10-16(JST)。HEAD=`b010cb469`(branch `feat/auw-unified-asr-01`)。
証跡(scratchpad、repo外): `...\scratchpad\{u1_count.py,u1_out.txt,frozen_replay.py,scenarios.py,u1release_plugin.py,netguard.py}`。実験はすべて netguard(外部connect/DNS遮断)下、API 0。

---------------------------------------------------------------------------------------------------

## 0. 要約(責任者向け)

1. **U1(JA固有名詞差・類似度<0.4の事前除外)**: ユーザー正式承認の逐語は存在しない(根拠は下記§1-2)。ユーザー指示A-3に従い「承認済み統一仕様との不整合の実装修正」として、`U1_KEEP_C1_SIMILARITY_EXCLUSIONS` を `False` にする1行変更で是正できる(実装は既に完成済みで、既存testも解放時の動作を固定している)。Phase 0の保存データによる**frozen replay(API 0)では、解放で判定が変わるのは25行中2行(g7=類似度, g8=C1)のみで、2行ともSecondary正答=救済。誤PASS用のC群5行は解放後もNGのまま(誤受理0)**。数値・否定の保護差(P1)は解放後もSecondaryを呼ばずNG(12シナリオ実験で確認)。
2. **ただし A-3 が列挙していない除外が2つ残る**(`A3_LENGTH_NG`と`A4_C2_HOMOGRAPH`)。A-3の「実行要件」に含まれないため**触らない**計画にし、理由を§1-3(c)に記す。A4(C2)は2026-10-11にユーザーが逐語で採用した保護、A3(length)はA-2 #7「独立音声品質QA維持」に当たるため、Fableが異論なければ維持を推奨する。
3. **U2(`force_secondary`)**: `U2_FORCE_SECONDARY_SCOPE`定数は**どのコードからも参照されていない(死んだ定数)**。実際の挙動は `er003_v1_crosslevel_audio_02_common.py:364` の `force_secondary=True` の1箇所だけで、これは「LR後v1」専用ではなく**2026-08-26ユーザー承認(OPEN-66 Part C)の"minimal instruction fallback音声はSecondary必須"**という別規則が、A2の`_run_a2_minimal_fallback_attempt`に残っているもの。A2のLR再TTSは同関数を再利用するため、結果的に`force_secondary=True`が付く。B1のLR再TTSは標準Prompt経路なので付かない(=「A2だけ」は意図的なLR設計ではなく成立経緯の産物)。**推奨=(i)維持(全レベル拡大はしない)＋名称・SSOT記述の訂正**。根拠と代替案は§2。
4. **43行マトリクス**: 実音声検証済み35／部分(実音声＋未検証が混在)2／再利用・複製で追加ASR不要5／N/A 1。「新規生成が必要だが未検証」は**B-A2-01(Family B A2 narrator 見出し・Hook・Tension・Closing)**、「別Production不具合で検証不能」は**C-01のJA新規生成部分(OPEN-372=F4)**。B-A2-01の実音声取得計画を§3に記す(見積JPY 2〜4、約10〜15分、1回のみ)。**未確認項目を黙って除外していない**(§3-4)。

---------------------------------------------------------------------------------------------------

## 1. U1 計画(A-3)

### 1-1. (a) 現行除外ロジックの正確な動作

統一judgeの除外表(`er078_asr_unified_judge_01.py:111-118`、`SCG_EXCLUSIONS`):

| id | 段 | 言語 | 判定信号 | u1_gated | 定義行 |
|---|---|---|---|---|---|
| A1_NUMBER_DIFF | P1 | en,ja | value_guard=DIFF | いいえ | :112 |
| A2_NEGATION_DIFF | P1 | en,ja | negation_diff | いいえ | :113 |
| A3_LENGTH_NG | P2 | en,ja | length_ok=False | いいえ | :114 |
| A4_C2_HOMOGRAPH | P2 | ja | c2_homophone_candidate | いいえ | :115 |
| **A5_SIMILARITY_LT_0_4** | P2 | ja | similarity<0.4 | **はい** | :116 |
| **A6_C1_PROPER_NOUN_DIFF** | P2 | ja | c1_proper_noun_diff | **はい** | :117 |

- `u1_gated`=True の規則は `U1_KEEP_C1_SIMILARITY_EXCLUSIONS`(`:65`、現在True)がTrueの間だけ有効。`_exclusion_hit`(`:122-142`)の `:128-129` が `if rule.u1_gated and not U1_KEEP_...: continue`。Falseにすれば A5/A6 は評価されずに素通りし、Primary NGは `P3: Secondary 1回` へ進む(`:394-399` の `hit = _exclusion_hit(...)` が None になる)。
- **P1(保護差)は `_exclusion_hit` より前**: `:388-393`(値DIFF→`NG_PROTECTED`、否定差→`NG_PROTECTED`、`signals["protected_diff"]`→`NG_PROTECTED`)。u1_gatedとは無関係で、U1を解放しても影響を受けない。
- 適用言語: A5/A6は `("ja",)` のみ(`:116-117`)。EN adapter(`er006_secondary_asr_01.py:909`)も `c1_proper_noun_diff`/`similarity` signalを渡すが、除外表の langs が ja のみのためENでは無効(U1はJA限定)。
- JA adapter のsignals生成: `er007_ja_secondary_asr_01.py:548-573`。**TRUE_CONTENT_MISMATCH 時のみ** `similarity`(=`cls.similarity_ratio`)、`c1_proper_noun_diff`(`_scg_c1_reason`、`:446-456`)、`c2_homophone_candidate`(`:458`)、`protected_diff`(否定/数字)を設定。TCM以外のPrimary NG(`ASR_VALIDATION_UNCERTAIN`等)は元からP3(Secondary)へ進む(例: 実験P1・P2)。
- C1(`_scg_c1_reason`)が成立する差分の種類: `reading_dictionary_mismatch`(登録読み辞書との不一致)、`entity_like`(カタカナ/略語同士の差)、`latin_in_canonical_diff`(原稿側差分にラテン文字)。
- `SCG_MIN_SIMILARITY=0.4`: judge側 `:119`、adapter側 `er007_ja_secondary_asr_01.py:84`(parity testで突合済み)。
- 診断用の旧関数 `_scg_exclusion_reason`(`er007...:188-222`)は `scg_info["exclusion_reason"]` 表示用として残置。Secondaryが実際に走った場合 `exclusion_reason=None` に上書きされるため(`:640付近`)、解放後に診断表示が食い違うことはない。

### 1-2. (b) 2026-10-11承認の除外条件の原文と、A-2/A-3との不整合点

**原文(逐語・ファイル:行)**

1. `CURRENT_SPEC.md:2016`(SCGの行、見出し「**2026-10-11ユーザー承認 `APPROVED_FOR_PRODUCTION`**」):
   「**SCG不実行(従来の再生成へ)の除外条件**: (1)数字差、(2)否定の差(…)、(3)固有名詞(`entity_like`/辞書読み不一致/原稿側ラテン文字差分、C1)、(4)Primary-原稿の類似度0.4未満、(5)`length_ok=False`(…)、(6)同形異音語(…C2…)」。同行末尾: 「Phase 0救済14件中13件維持(g8[ガス→カス]はC1固有名詞除外により対象外=誤PASSではなく従来の再生成)。**ユーザー最終確認待ちの注記あり(g8 13/14の受入)**」。
2. `DECISION_LOG.md:20574`「ユーザー決定(逐語要旨)」: 「V1方式=SCG(Secondary Confirm Gate)をProduction採用(`APPROVED_FOR_PRODUCTION`)、**C2(同形異音語ガード)・推奨4(否定マーカー除外)も採用**、安全条件(PHONETIC_MATCH自動PASSなし・Whisper 2-of-3なし・Phrase Listなし・Human Review Lock/attempt上限/英語不変・NG/UNAVAILABLEは従来動作)」。→ **ユーザー決定の逐語要旨にC1(固有名詞)と類似度0.4は含まれない**。同エントリ末尾: 「**USER_DECISION_REQUIRED**: g8(ガス→カス)を救済しない13/14のまま受入するかのユーザー最終確認」。この確認に対する回答はDECISION_LOG内に見当たらない(Grep `g8` は同エントリのみ)。
3. C1の導入元: `er053_output/open258_scg_production_wiring_01/OPUS_REVIEW_01.md:6`(「必須1(C1) 固有名詞除外の欠落…Fable判断で実施する項目」)。副作用の記録: 同 `OPUS_REVIEW_FOLLOWUP_01.md:18`(「g8…がC1…でSCG対象外になり、本番条件の救済は14件->13件。…除外の絞り込み(例: 濁点のみ差のentity_likeは対象に残す)は新しい仕様判断のため実装していない」)。→ C1は**Opus必須1をFableが採用して実装した安全側の追加**で、ユーザー個別承認の逐語は無い。
4. 類似度<0.4: Phase 0の「既存除外(数字/否定/ratio<0.4/echo)」(`er053_output/open258_phase0_trial_01/RESULT_01.md` §(3))の引継ぎ。Phase 0自身が「ratio<0.4は…1〜3文字の短いkey phraseでは正しい発音でも類似度が0になり得て救済を妨げる(要観察)」「g7 湿度…Azure転写は原稿と一致」「ユーザー判断事項(iv)短文でのratio<0.4除外の扱い」(§(8))と記録。(iv)への正式回答もDECISION_LOG内に見当たらない。
5. 食い違いの既知記録: `docs/research/ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01/REDETERMINATION_CHECK_01.md:12`(「除外条件(数字差・否定差・固有名詞C1・類似度0.4未満・length NG・同形異音語C2)も承認」)と`:35`(「C1は『Fable採用・ユーザー個別承認の逐語なし』(V04 C-10)」「C1廃止方向(D-10)…未回答」)が矛盾。`DESIGN_02_ADDENDUM_01.md:137-140`(§11 U1)も同じ事実を記載。

**A-2/A-3との不整合点**

| # | 現行 | 統一仕様(A-2/A-3) | 不整合 |
|---|---|---|---|
| 1 | C1/類似度<0.4のPrimary NGは Secondary不呼出で`NG_EXCLUDED`→再生成 | A-2 #2「Primary NGなら、不一致の種類・大きさにかかわらず原則Secondary」 | 直接矛盾 |
| 2 | 同上 | A-2 太字「**Primaryの差が大きいという理由だけでSecondaryを省略…しない**」 | A5(類似度<0.4=差が大きい)は文字通りこれに該当 |
| 3 | 同上 | A-3「固有名詞差でもPrimary NGならSecondary確認／低類似度でも…」 | 直接矛盾 |
| 4 | 実害の実測 | 同上 | 保存データで正当なSecondary PASSを拒否した実例あり(g7: Primary「死図塔」→Azure「湿度」PASS、g8: Primary「カス」→Azure「ガス」PASS。いずれも§1-5の frozen replay で再現) |

**判定**: C1・類似度0.4は「ユーザー逐語承認の無い、Fable/Opus採用の安全側追加」で、現行の統一仕様と矛盾する。ユーザー指示A-3に従い「実装修正」として是正対象(新たなユーザー質問は不要)。

### 1-3. (c) 最小変更案と、保たれるもの

**最小変更(委任_10で実施する案)**

| # | 変更 | 場所 | 規模 |
|---|---|---|---|
| 1 | `U1_KEEP_C1_SIMILARITY_EXCLUSIONS = True` → `False`。コメントを「U1是正(A-3、2026-10-16ユーザー指示)…ロールバック=Trueへ戻す1行」に更新 | `er078_asr_unified_judge_01.py:65` | 1行 |
| 2 | (任意・推奨)`U2_FORCE_SECONDARY_SCOPE`の扱いは§2の結論に従う(死んだ定数の整理) | `:66` | 1〜2行 |
| 3 | α testの更新(下表) | 4 file | 約12 test |
| 4 | 診断表示: 解放後も `scg_info["exclusion_reason"]` は「Secondary実行時はNone」(既存動作)で変更不要 | - | 0 |
| 5 | **A5/A6のExclusionRule行は残置**(ロールバック＝`True`へ戻すだけで旧動作に復帰、`test_u1_flag_releases...`が両状態を固定) | - | 0 |

- **静的監査 allowlist 影響: なし**。`er078_asr_unified_wiring_static_audit_01.py` はU1/u1_gated/exclusion定数を参照していない(Grep 0件)。entrypoint→呼出点の列挙(35 entry)は判定器の呼出点であり、除外表の中身には依存しない。
- 実行確認済み(API 0): `U1=False` を差し込んだ状態で関連11 file(382 test)を実行 → **失敗14件(うち2件はU1無関係の既存失敗)**。差分の12件が下記α。

**α/β分類(`U1=False`差し込み実験の実測)**

| 分類 | test | 現行の固定内容 | 解放後の扱い |
|---|---|---|---|
| α(更新) | `er078_asr_unified_judge_01_test_01.py::test_p2_exclusions_table`(A5/A6部分) | `:119-122` A5/A6がNG_EXCLUDED | A5/A6のassertを「`U1=True`をmonkeypatchした時のみNG_EXCLUDED」へ。A3/A4部分は不変 |
| α | 同 `::test_u1_flag_releases_a5_a6_in_one_line` | `:127` が定数==Trueを前提 | 前提を`False`へ(以降の挙動assertは不変で正) |
| α | `er078_asr_unified_ja_wiring_test_01.py::test_u1_constants_unchanged` | `:207` `U1==True and U2=="A2_ONLY"` | U1==False(U2は§2の結論による) |
| α | 同 `::test_c1_proper_noun_and_low_similarity_excluded_u1_current` | `:210-222` C1/類似度でNG_EXCLUDED | 「Secondary呼出あり」へ反転(または`U1=True`をmonkeypatchして旧動作を固定) |
| α | `er007_ja_scg_test_01.py::ScgJudgementTests::test_e_similarity_below_0_4_not_executed` | 旧SCG時代の「類似度<0.4でAzure不呼出」(adapter経由で解放の影響を受ける) | 反転、または`U1=True`固定のロールバック検証へ |
| α | 同 `OpusReviewFixTests::test_c1_dictionary_reading_mismatch_not_executed` | C1(登録読み辞書不一致)でAzure不呼出 | 同上 |
| α | 同 `::test_c1_entity_like_diff_in_mixed_diffs_not_executed` | C1(混在差分のentity_like)でAzure不呼出 | 同上 |
| α | `er007_ja_scg_phase0_regression_test_01.py::Phase0Regression::test_g7_short_text_similarity_below_0_4_not_executed` | g7を「除外」と期待 | 「g7はSecondary→PASS_WITH_WARNING」へ |
| α | 同 `::test_rescue_success_7_groups_pass`・`::test_every_row_matches_phase0_secondary_pass_judgement` | 救済13件固定(g8除外) | 救済15(13+g7+g8)へ。期待値は§1-5のreplayで確定済み |
| α | 同 `ProductionConditionRegression::test_g8_excluded_by_implementation_not_fixture`・`::test_rescue_and_c_group_under_production_conditions` | g8 NOT_APPLIED / 13件 | g8はPASS_WITH_WARNING、15件、**C群5件は不変にNG(β部分)** |
| **β(期待値変更禁止)** | 上記tests内の **C群5行がNG(誤PASS 0)**、`er078_asr_value_guard_01_test_01.py`(9例)、`test_p1_*`(値DIFF/否定差でSecondary不呼出)、`test_u1_flag_releases...`内の「A3(length)はU1と無関係に維持」、`er007_ja_scg_c2_neg_test_01.py`(C2・否定マーカー)、`er078_asr_unified_judge_01_test_01.py` 全体のP1/P3/最終ANDゲート/Secondary障害系 | 最終判定の安全性そのもの | 変更不可。解放後もPASSであることがAcceptance |
| 既存失敗(U1無関係) | `er007_ja_secondary_asr_01_test.py::test_koro_kanji_variant_confirmed_by_reading_candidates` / `::test_single_engine_repetition_does_not_confirm_orthographic_variant` | HEAD `b010cb469` で`U1=True`でも失敗(`PHONETIC_MATCH`≠`ORTHOGRAPHIC_VARIANT_CONFIRMED`) | U1とは別問題(§5 候補). 触らない |

**「保たれるもの」の確認**(実験: `scenarios.py`、`U1_KEEP` True/False 各12シナリオ、Azureはmock、API 0)

| 保つべき要件 | 実測(U1=False) |
|---|---|
| 数値保護差(N1: 3人→4人、Azureが原稿一致でも) | `NG_PROTECTED p1_value_diff`、Azure呼出0 |
| 否定保護差(N2: 縛られず→縛られる / N3: 眠くならない→なる) | `NG_PROTECTED`(`p1_protected_diff:negation_marker_diff` / `p1_negation_diff`)、Azure呼出0 |
| 低類似度でSecondaryが原稿を支持(S1) | `PASS_WITH_WARNING secondary_confirmed`(Azure 1回) |
| 低類似度でSecondaryも外れ(S2) | `NG_BOTH secondary_not_accepted` |
| 固有名詞差でSecondary正答(P1, P7) | `PASS_WITH_WARNING`(P1はU1=Trueでも既にPASS: Primary UNCERTAIN経路) |
| 固有名詞差でSecondaryも誤り(P2, P5, P6: AKB48型の人名誤認識) | `NG_BOTH`(誤受理なし) |
| length NG | 不変(`A3_LENGTH_NG`は`u1_gated`でない。test `:131-133`)。**維持を推奨**: lengthは独立のAND(`length_ok`)で、SecondaryがPASSでも最終的に不合格になるため無駄なAzure呼出を避けるだけの規則。A-2 #7「独立音声品質QA維持」に該当 |
| C2同形異音語 | 不変(`A4_C2_HOMOGRAPH`)。**維持を推奨**: 2026-10-11にユーザーが逐語で採用した保護(`DECISION_LOG.md:20574`「C2…も採用」)。Azureは原稿の漢字表記と一致しても読み違いを区別できないため、Secondaryが「原稿を正当に支持」できない。A-3の「実行要件」にも挙がっていない |
| 独立QA(disfluency/repetition/値・否定の最終ANDゲート) | 影響なし(解放はP2除外表のみ。`:355-370`の最終ANDゲート、Secondary転写に対する値ガード/否定ガード`:455-460`は無変更) |
| Pronunciation Ledger / JA Validator整合 | 下記 |

**Pronunciation Ledger / JA Validator整合**
- **JAには `pronunciation_ledger`(`er025`系)の判定連携が無い**(`er007_ja_secondary_asr_01.py`・`er007_ja_asr_validator_01.py` を Grep `ledger|er025|pronunciation` → 0件)。Pronunciation LedgerはENのPhrase List/hint(`er006_secondary_asr_01.py` `ledger_phrases`)用で、JAのSecondaryはPhrase Listなし固定(`phrase_list_hash=""`、`er007...:582`)。→ 解放がLedger側に影響する経路は無い。
- JA側の読み保護は `expected_readings`(登録読み辞書、`er007_ja_asr_validator_01.py:203-321`)。Secondary判定も `classify_ja_asr_match(canon, stext, expected_readings=…, allow_reading_resolver=False)` を使う(`er007...:604-606`)ため、辞書登録トークンの読みは**Secondary転写にも同じ辞書基準**で適用される。受理は `EXACT_MATCH`/`NORMALIZED_MATCH`(`SCG_PASS_CLASSIFICATIONS`、`er007...:83`)のみ＋2エンジン確認の`ORTHOGRAPHIC_VARIANT_CONFIRMED`。
- 残る要検証点(委任_10のunit testで固定): Latin原稿語(例 `Meta`)で、Secondaryが**ラテン表記のまま原稿と完全一致**(P3)した場合のみPASS。Secondaryが`メタ`と返す場合はNG_BOTH(P4)。つまり「読みが正しいかをAzureの表記で判定している」点は旧SCG(2026-10-11承認)と同じ構造で、新たな緩みではない(ただしC1が止めていた最後の砦が無くなる=§1-4のリスク)。

### 1-4. (d) 誤受理リスク評価

**Secondary PASSで救済される条件(コード照合)**
1. Secondary転写(Azure ja-JP、連続認識、Phrase Listなし、1 wav 1回、`SecondaryCache`キー=(sha256,engine,lang,phrase_hash=""))に対し、
2. 値ガード/否定ガードがDIFFでない(`judge.py:455-460`、DIFFなら`NG_BOTH`)、
3. `classify_ja_asr_match(原稿, Secondary転写, allow_reading_resolver=False)` が **EXACT/NORMALIZED**(＋2エンジン確認のORTHOGRAPHIC_VARIANT_CONFIRMED)、
4. `final_and_gate`(値/否定の再確認)通過 → `PASS_WITH_WARNING`(`SECONDARY_CONFIRMED`)＋事後試聴リスト登録。
- JAには Connected Speech Equivalence 層が無い(ENのみ)ので「CS MIXED時の扱い」は対象外。

**固有名詞差/低類似度のclipがSecondary PASSになりうる現実的ケース(保存データ)**

| ケース | 出典 | Primary | Secondary | 解放後の判定 | 評価 |
|---|---|---|---|---|---|
| g8 「熟すと出るガス」 | Phase 0 fixture(`er007_ja_scg_phase0_fixture_01.jsonl`) | 「じくすと出るカス」(C1 entity_like) | Azure正答(NORMALIZED_MATCH)、whisper small/medium両方も原稿一致 | PASS_WITH_WARNING | **正当な救済**(Phase 0の救済7群の一つ。除外による13/14は未承認のまま) |
| g7 「湿度」 | 同 | 「死図塔」(類似度0) | Azure「湿度」、whisper small一致 | PASS_WITH_WARNING | **正当な救済** |
| C群5行(TTS誤り代理: 縛られず/体内時計/証拠だと/名所…旅程/形になり始める) | 同 | TCM | Azureも原稿外れ | NG(解放後も) | 誤受理0 |
| AKB48人名clip 2件 | `evidence_06/ja_old_vs_new/compare_api0.json` | 伊藤評価/近藤作 等(人名誤認識) | Azure実呼出でも人名不一致 | `NG_BOTH`(既に除外されず実Secondary済み) | 人名誤りはSecondaryが保護している実例 |
| AKB48 title 1件、ブルルクル(ja_hr attempt3) | `evidence_06/ja/runner_execute.json`・`evidence_06b/ja_hr/attempt_history.jsonl` | A6除外 | 未実行(保存Secondary無し) | 不明 → §1-5の「保存wav＋live Azure」で確認 | 要確認(約JPY 1) |
| Melos japanese_title attempt1〜5 | `er026_output/family_z_production_e2e_01/melos/run_e2e_01/a2/narration/attempts/japanese_title_attempt*.json` | Primaryが韓国語(Hangul)転写「시리에 매우스」(類似度0.0、A5) | 不明(保存無し。wavは存在) | 不明 → live Azureで確認 | 低類似度の典型。Primaryの言語誤認識か実際のTTS不良かを分けられる |

**保存データの集計(API 0、`u1_count.py`。重複除去後の一意レコード29件。JA scg_info/asr_judgement形式のみ対象)**

| 区分 | 件数 |
|---|---|
| 旧SCG: Secondary実施 → PASS | 5 |
| 旧SCG: Secondary実施 → NG | 10 |
| 旧SCG除外: 数字差(number_mismatch、**P1 保護差=U1と無関係**) | 9 |
| **U1対象: 類似度<0.4** | 2(Melos title、Hangul転写。代表例を上表) |
| **U1対象: entity_like(C1)** | 1(ブルルクル `ヴ->ブ`、ja_hr attempt3) |
| **U1対象: 統一judgeのA6_C1_PROPER_NOUN_DIFF** | 2(AKB48 title、ブルルクル slot3。上のentity_likeと同一事象を含む) |
| A4(C2)除外 | 0(保存データ内に該当無し) |

→ **U1が実際に作用した保存事象は合計約5件**。Phase 0(25行中2行)を足しても少数で、解放で増えるSecondary呼出は1記事セット当たり1回未満と見積もれる。

**リスク評価**
- 最大の理論リスク: 「Azureが原稿側の綴りへ丸める(固有名詞で確率的に正答側へ寄る)」＝TTSの読み誤りを見逃す。実測は Phase 0 C群 0/5、frozen replay 0/25、AKB48 の人名でAzureも誤り(NG_BOTH×2)=Secondaryが保護している。標本は小さい(N=25＋少数)ため断定はせず、**PASS_WITH_WARNING→事後試聴リスト**(A-2 #3/#4、非ブロッキング)が最終の砦になる。
- Latin原稿語(C1の`latin_in_canonical_diff`)は、Secondaryが**ラテン表記で完全一致**したときのみPASS(P3)。AzureがJAでラテン綴りを返す頻度は低く、返した場合は「英語読みで発話された」ことの証拠でもあるため、実害は限定的と評価。
- 費用: Secondary 1回 = 音声秒×単価(`judge.py:est_jpy_for_seconds`、1.0 USD/h×160=0.0444 JPY/秒)。5〜20秒clipで 約JPY 0.27〜0.89/回。想定増分は 記事セット当たり<0.5円(目標70円の約1%未満)で、回避される再生成(TTS＋ASR 約0.1〜0.3円＋待ち120〜170秒/回、`RESULT_01.md` §(5))で一部相殺される。

### 1-5. (e) Regression計画

**KPI測定経路の区分**: frozen=保存済みresults cache/fixture replay(API 0)、fresh=実音声(API有料)。

**(e-1) frozen replay(API 0、実施済みの予備結果)**
- 方法: Phase 0 fixture 25行(`er007_ja_scg_phase0_fixture_01.jsonl`、Azure転写保存済み)を、Production関数 `ja.evaluate_attempt_ja_with_cascade_detail`(Primary＝保存転写、Azure＝fixture転写のmock)に、`U1=True`／`False`で各1回通し、判定差分を全件集計(`frozen_replay.py`、netguard下)。
- **結果**: 全25行。**差分は2行のみ**: `g8_kp4_ja_charon_a1`(NG_EXCLUDED A6 → PASS_WITH_WARNING secondary_confirmed)、`g7_meaning_4_a1`(NG_EXCLUDED A5 → PASS_WITH_WARNING secondary_confirmed)。verified数 13→15、Azure呼出 21→23。**C群(TTS誤り代理5行)で解放後にverifiedとなった行 = なし(0)**。旧PASS→新NG = 0(OF-AUW-11の「PASS→NG全件確認」を満たす)。
- 委任_10で追加する範囲: (i)同replayを正式なtestとして固定(`er007_ja_scg_phase0_regression_test_01.py`のα更新と一体)、(ii)`evidence_06/ja_old_vs_new/compare_api0.json` 10件、`evidence_06b`のJA attempt、`er011_output/attempt_history.jsonl`のJA TCM行を `U1=True/False` で全件replay(Secondary保存あり行のみ。保存無し行は(e-2))。判定差分は「PASS→NG 0」「NG_EXCLUDED→NG_BOTH/PWW のみ」を確認。

**(e-2) 保存wav＋live Azure(有料・小額。Fableの許可が必要)**
- 対象: U1で新たにSecondaryが走る保存wav 約8本: Melos japanese_title attempt1〜5 のうちA5該当(2〜5本)、AKB48 title 1本、ja_hr comment_1 attempt3(ブルルクル)1本。TTS・Primaryは再実行せず、**Azure STT 1回/本のみ**。
- 見積: 平均8秒×0.0444円/秒 ≒ JPY 0.36/本 → 8本で **約JPY 3**(上限JPY 4、秒切上げ込み)。所要約5分。1回のみ・再起動なし。判定ルールは判定器そのもの(adapter)を呼ぶ。出力: 各wavの「Azure転写／判定／正答or誤受理(試聴 or 原稿一致で確認)」。誤受理が出た場合は即停止してFableへ報告。
- コマンド案(委任_10で実装): `.venv\Scripts\python.exe er078_auw_runtime_evidence_09.py u1replay --execute --budget-jpy 4`(06bのharness `begin()/finish()` に準拠し、`TTS_EXECUTION_MODE=STANDARD`は不要=TTSなし)。STOPセンチネル: `er058_output/unified_all_roles_production_wiring_01/evidence_09/u1replay/STOP`。実行前に `tools/stop_scope_check_01.py --managed-id ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 --run-dir <上記> --out …` を実行しrc=0を確認。

**(e-3) fresh 実音声(JA 1〜3 clip。任意・Fable判断)**
- 目的: 解放後のProduction正式経路(Z/X/legacy runnerのJA入口)で、固有名詞を含むJA clipが `PASS_WITH_WARNING`→試聴リスト登録まで通ること。06bの`xrun`/`lega`と同様、Production関数を実呼出し。
- 見積: TTS(0.0243円/秒)＋Primary ASR(0.0047円/秒)＋Azure(0.0444円/秒)＝約0.07円/秒 → 8秒×3clip ≒ **JPY 1.7〜2.5**。(固有名詞を含むJA文2〜3本。AKB48型のヒント付き原稿)。実行は(e-2)で誤受理0を確認した後。

**(e-4) 既存test**: §1-3のα更新後、netguard付きで関連11 file＋AUW中核12 file(411 passed が基準)＋静的監査15 passed＋後方互換53 passed＋flag OFF経路3 passed を再実行し、β不変・新規失敗0を確認。

### 1-6. (f) Opus条件Cレビューに渡す論点

1. **除外撤去の安全性**: C1(entity_like/辞書読み不一致/Latin原稿語)をすべて外してよいか。「Secondaryが原稿綴りへ丸める」リスクに対し、PASS_WITH_WARNING＋事後試聴リストが十分な砦か。frozen replay 0/25・Phase 0 C群 0/5・AKB48 NG_BOTH×2 の標本で足りるか。
2. **除外の線引き**: A3(length)・A4(C2)を維持したままA-3の「実行要件」を満たすと解釈してよいか(A-2 #7「独立音声品質QA維持」との関係、C2はユーザー逐語採用)。
3. **Latin原稿語／`reading_dictionary_mismatch`**: 解放後、登録読み辞書(`expected_readings`)の違反がSecondaryのEXACT/NORMALIZED判定で素通りしないか。JAに Pronunciation Ledger 連携が無い点の扱い。
4. **ロールバック設計**: 定数1行＋規則行残置で足りるか。α/β test分離が妥当か。3回上限・cool-down・circuit breaker・費用(Secondary呼出増)との整合。
5. **frozen replayの代表性**: Phase 0のSecondary結果は2026-10-11時点のAzure。現行でも同結果が出るか(→(e-2)のlive Azureで補強)。

---------------------------------------------------------------------------------------------------

## 2. U2 調査(A-4)

### 2-1. 現行コードの事実(Grep全repo `*.py`、`force_secondary=True`)

| 箇所 | 内容 |
|---|---|
| `er003_v1_crosslevel_audio_02_common.py:364` | `_run_a2_minimal_fallback_attempt` 内の `secondary_asr.evaluate_attempt_with_cascade(..., force_secondary=True, ...)`。**Production唯一**の`force_secondary=True`呼出 |
| `er003_v1_crosslevel_audio_02_common.py:189` | A2 segmentの通常fallbackループ(`generate_english_segment_with_fallback`)が同関数を呼ぶ |
| `er003_v1_crosslevel_audio_02_common.py:409-413` | **A2のLocal Rewrite再TTS(`_retts_fn`)も同関数を呼ぶ**(`attempt_ctx={"script_version": "v1", …}`) |
| `er003_v1_sing01_voice01_generate.py:363`・`er003_v1_sing01_news_tail_fix.py:372` | B1系のLR再TTSは `script_version="v1"` のみ渡し、`force_secondary`は**渡さない**(標準Prompt経路) |
| `er006_secondary_asr_01.py:921` / `judge.py:213,379-382,483-486` | 引数→`AttemptCtx.force_secondary`→「Primary PASSでもSecondary必須」→両エンジン合意なら`PASS`(`force_secondary_agreed`、警告なし。LR後は`LR_REWRITTEN`が付く) |
| `er078_asr_unified_judge_01.py:66` `U2_FORCE_SECONDARY_SCOPE = "A2_ONLY"` | **どのコードからも参照されない**(参照は`er078_asr_unified_ja_wiring_test_01.py:207`のassertのみ)。=制御していない名目上の定数 |
| `er014_output/…/finalize_a2_pipeline.py:176`(別名script) | Production外のDEV script |

### 2-2. 成立経緯(原文・ファイル:行)

1. **発端(2026-08-26、ユーザー承認済み)**: `DECISION_LOG_HISTORY.md:4922-4930`「**Secondary ASR必須化の実装**: …`force_secondary`引数(既定False)を追加。standard path…は無変更・追加コストゼロ。fallback path 2箇所(`generate_key_phrase_component_verified`の内部fallbackループ、`er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback`のfallbackループ)へ`force_secondary=True`を配線し、PrimaryがPASSしてもSecondaryが同意しない限り自動PASSしないようにした」。承認: `OPEN_ITEMS.md:246`(OPEN-66)「2026-08-26追記(ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04 Part A〜D、**ユーザー承認済み**)」。
2. **実害(根拠となった事故)**: `CURRENT_SPEC.md:1933`「fallback(minimal instruction)経由で生成された英語音声は、Primary ASRの結果に関係なくSecondary ASR(Azure)による確認を必須化した…**No.7 A2 point_one_headingで実際に発生した『Primaryは正常認識・Secondaryは全く別内容』という誤PASS事故の再発を防ぐ暫定対策**(fallback自体の根本原因見直しはOPEN-66・OPEN-67参照)」。状態は`PRODUCTION_WIRED`(2026-08-26)。
3. **KP側は後に撤去**: `git show 8503226c2`(2026-09-01、ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK…)で、Key Phrase fallbackループの`force_secondary=True`が、KPのretry構成の再設計(ユーザー正式決定)に伴い削除された。以後Production内で残るのはA2 segmentのminimal fallbackだけ。→ 「A2だけ」は**意図的な限定ではなく、KP再設計で他が消えた後の残存**。
4. **AUWでの取り扱い**: `OPUS_REVIEW_A_01_VERBATIM.md:76-79`(OF-AUW-06)「`force_secondary=True`の箇所はProduction内で`er003_v1_crosslevel_audio_02_common.py:351`(A2 minimal経由)だけです。voice01:359とnews_tail_fix:368のLR再TTSには適用されていません。設計:326は全LR v1へ適用します。…原文§6/§2/§5と競合…**U(ユーザー判断)へ格上げ**…回答までの暫定はA2だけ現行維持、B1は統一判定と`LR_REWRITTEN`のWARNINGのみ。推奨は『LR v1はPrimary PASSでもSecondaryで確認(A)』」。→ `DESIGN_02_ADDENDUM_01.md:113-115`(§5)・`:141-143`(§11 U2)・`CURRENT_SPEC.md:2685`・`USER_DECISION_REGISTER_01.md` #84。
5. **関連**: `OPEN_ITEMS.md:791`(OPEN-288)「見出し(`point_headings_aoede`)は…元からforce_secondaryが無く…Primary単独PASSを見逃しうる。LR後原稿は`raw bean→robbing`型(Coffee #5)の見逃しがある。案(提案のみ): 見出し・LR後のみ最低限PASS_WITH_WARNING…(+Secondary確認)(D-5)」(`APPROVED`ではない)。`OPEN_ITEMS.md:886`(OPEN-377)「スコア表記『8–1』とASR『8 to 1』の等価(fallback routeの`force_secondary`でNGになる)」＝force_secondaryが実運用で正当なPrimary PASSを落とす実例。

### 2-3. 品質・安全上の根拠 / 統一仕様との関係

- **根拠(あり)**: minimal instruction fallbackは、標準Prompt／voice／速度の再生成が尽きた後の**最終手段**で、Prompt指示が最小のためTTSが原稿から外れる確率が高く、かつPrimary ASR(gpt-4o-mini-transcribe)が「原稿に寄せて」正常認識してしまう事故が実際に起きた(No.7 A2)。この経路はA2だけに残っている。
- **LR後v1にも付く理由**: A2のLR再TTSがminimal fallback attempt関数を再利用しているため(§2-1)。LR後は書換え文(音韻調整)を意図的に読ませるため、Primary単独PASSの見逃し(OPEN-288のCoffee #5 `raw bean→robbing`)にも一定の根拠はあるが、**B1のLRには付けていない**。
- **統一仕様との関係**: A-2 #1「Primary PASSなら採用」の例外で、A-2 #7「独立音声品質QA維持」の範疇と解釈できる(新規例外ではなく2026-08-26承認済みの既存例外が残存)。ただし (a)名目定数`U2_FORCE_SECONDARY_SCOPE`が実体と無関係、(b)`CURRENT_SPEC.md:2685`「LR後v1=標準Prompt・force_secondary=True」は**A2では事実と異なる**(A2のLR再TTSはminimal Prompt経路)、(c)`CURRENT_SPEC.md:1933`は「fallback音声は全てSecondary必須」と書くがKP側は2026-09-01に撤去済み(記述が現状より広い)、という**記述の不整合**がある。

### 2-4. 結論案(Sonnet推奨)

| 案 | 内容 | 評価 |
|---|---|---|
| **(i) 維持(推奨)** | A2 minimal fallback(LR再TTS含む)の`force_secondary=True`を**そのまま維持**。B1へは拡大しない。同時に**記述を実態へ訂正**(定数コメント/`CURRENT_SPEC.md:2685`・`:1933`の注記、U2を「LR規則」ではなく「2026-08-26承認のfallback音声Secondary必須」と再定義)。`U2_FORCE_SECONDARY_SCOPE`は死んだ定数のため削除またはコメント化(testは`:207`のassertを更新) | 動作変更ゼロ・Production挙動不変・ユーザー再質問不要(既存承認済み規則の整理)。A-4 #5「例外維持が必要なら理由・範囲・影響を報告」を満たす |
| (ii) 例外撤廃 | A2のforce_secondaryも外す(全レベルPrimary PASS→採用) | 2026-08-26に実害が出た保護を、新たな根拠データ無しに外すことになる。A-4 #4「不要な旧例外なら…整理」の「不要」の根拠が示せない。OPEN-377(8–1)のような偽陽性は別途(値ガードEQUAL拡張=新仕様候補)で解くべき |
| (iii) 全レベル拡大 | B1のLR/fallbackにも適用 | **推奨しない**(A-4太字: 根拠なく全レベルへ拡大してはならない)。OPEN-288の根拠データ(Coffee #5)は**Fable/ユーザー判断の仕様候補**であり、本委任では実装しない |

- **追加費用の試算**: (i)は変更なしのため追加0。参考: 現行のforce_secondary発火＝A2 minimal fallback attempt 1回につきAzure 1回(5〜25秒＝約JPY 0.22〜1.11)。(iii)にした場合の上限見積は「B1のLR再TTS(slot3 NG後の稀な事象)×Azure 1回」＝1記事セット当たり<0.1円(LR自体が稀)だが、**根拠のない拡大のため推奨しない**。
- **独立問題の候補**: 上記(a)(b)(c)の記述不整合は§5へ。

---------------------------------------------------------------------------------------------------

## 3. 43行マトリクス 5区分再整理(A-5)

出典: `APPLICABILITY_MATRIX_01.csv`(43行)、`RUNTIME_EVIDENCE_06.md` §12-10/§13-10/§15-5、`CLOSEOUT_PLAN_07.md` §4(条件1・2・4・9)。「半実音声」(故障/転写の注入)は実音声に含めず注記。

### 3-1. 区分表

| 区分 | 件数 | row_id |
|---|---|---|
| **1. 実音声で検証済み** | **35** | X-B1-01,02,03,04,05,07 / X-A2-01〜08 / Z-B1-01,02,03 / Z-A2-01〜05 / Z-ALL-01,02 / A-B1-01〜04 / A-A2-01,02,03 / B-B1-01 / XC-01,02,03 |
| **1/2/5 の混在(部分)** | **2** | **B-A2-01**(Voice A/B本文＝free_address経路は実音声[06b `brun`]、**narrator見出し・Hook・Tension・Closingは新規topic経路で未実行**→区分2)、**C-01**(narrator/device/brother/charon_english/voice本文は実音声[06b `crun`]、**Comment1-3(JA)＋JA title新規TTSは到達不能**→区分5) |
| **2. 新規生成が必要だが未検証** | 1行(の一部) | **B-A2-01 のnarrator部分**(§3-2〜3-3) |
| **3. 再利用・複製で追加ASR不要(仕様どおり)** | **5** | X-B1-06(注①)、X-B1-08、X-B1-09、X-A2-09、Z-ALL-03 |
| **4. 正式仕様上のN/A** | **1** | Y-00(Production TTS経路なし。`RUNTIME_EVIDENCE_06.md` §13-10、`CURRENT_SPEC` L1543-1553) |
| **5. 別Production不具合で検証不能** | 1行(の一部) | **C-01のJA新規生成部分**(OPEN-372=F4: Family C runnerがJA Comment/titleの新規TTSをen固定でしか呼べず、`reuse_from`時の`.ok.meta.json`も複製されない。**AUWの実装漏れではなくB案件[FCJ]**) |

合計: 35＋2(混在)＋5＋1＝43 ✓(`RUNTIME_EVIDENCE_06.md` §13-10「37＋5＋0＋1」と一致: 37＝35＋B-A2-01・C-01)。

注① X-B1-06(Key Phrase英語 phrase、Family X B1)は§13-10で「再利用・複製」に分類済み。X入口での新規生成は未実行で、**同一leaf(`generate_key_phrase_component_verified`＝4回構成)は Z-ALL-01(`kp4`実音声)・X-A2-07(`xkpen`)で検証済み**。Fableは「X-B1-06＝区分3(同一leafは他入口で実音声)」で良いか確認されたい(区分1へ繰上げる場合は`kp4`相当をX入口で1本追加)。

半実音声の注記(区分1の中で、故障/転写の注入を含む項目): Dialogue外側ループ(減速出力の差替)、技術STOP(Secondary mock障害)、非ラテン救済の否定/数値(Primary非ラテン転写の注入)、導出失敗(registry例外の注入)、再利用DIFF(cache entryを意図構成)。narrator A2外側ループは07bで実音声(通算3回＋cool-down 600.004秒→`NG_BOTH`→HR Lock)。

### 3-2. B-A2-01 の未検証内訳(Production経路の事実)

- Family B A2 には2つのProduction経路がある: (a)`main_a2`＝free_address。`run_tts_a2`(`er012_b_family_production_runner_01.py:1455-1500`)が**Voice A/B本文のみ新規TTS**、他segment(topic_intro〜in_one_line)は`A2_SEGMENTS_TO_REUSE`(`:1335-1339`)で承認済みbyte再利用。(b)`main_a2_2v_new_topic`＝新規topic。`run_tts_a2_2v_new_topic`(`:1706-1757`)が**narrator見出し(`generate_narrator_heading_with_a2_slowdown`)・Hook＝`full_story_part1/2`・Tension＝`tension_body`・Closing＝`in_one_line`(`generate_narration_wide_margin_with_a2_slowdown`)を新規TTS**。
- 06bの`brun`は(a)を実行(`main_a2 all a2`)。(b)のnarrator系は未実行。ただし両関数は共有helper `n3_tts.generate_a2_segment_with_slowdown`／`generate_with_a2_slowdown_outer_loop`→`news_tail_fix.generate_news_narration_wide_margin` の薄いラッパで、このhelperは X-A2-05/06・Z-A2-01・A-A2-02・07b(narrator外側ループ、`full_story_part1_c3`)で実音声検証済み。
- したがって**未検証はFamily Bの入口(`er012_b_family_voices_a2_production_01.py:738-757` の2ラッパ＋`run_tts_a2_2v_new_topic`の呼出引数)**。引数差は `disfluency_qa=(name=="in_one_line")`、`enable_connected_speech_equivalence_layer`/`enable_repetition_qa`=(part1,part2 True／tension・in_one_line False)、見出しは`first_words(…,3)`・`max_extra_chars=20`・`A2_ENGLISH_STYLE_PREFIX_SLOWER`・`disfluency_qa=True`。

### 3-3. 実音声取得の実行計画(B-A2-01 narrator: 見出し・Hook・Tension・Closing)

- 新規 `er078_auw_runtime_evidence_09.py`(委任_10で作成。06bの`begin()/finish()`harness＝全API呼出前のSTOP/予算確認＋SDK wrapper費用記録、隔離出力を踏襲)の `bnarr` part。
- 方式(推奨): `run_tts_a2_2v_new_topic`全体は`shared_narration.ensure_all_shared_narration_a2`(固定shell)＋topic_intro(Charon)＋Voice A/B本文を含み不要なTTSが増えるため、**Production関数 `a2prod.generate_narrator_heading_with_a2_slowdown` と `a2prod.generate_narration_wide_margin_with_a2_slowdown` を `run_tts_a2_2v_new_topic` と同一引数で直接呼ぶ**(06bの`head`/`bb1`と同じ粒度)。
  - 見出し 1本: 数値を含む例(`Why prices fell 8.7 percent in one month`、06b `head_numeric`と同系)。
  - Hook(`full_story_part1`相当) 1本(CS層＋Repetition QA True)、Tension(`tension_body`相当) 1本(False/False)、Closing(`in_one_line`相当) 1本(`disfluency_qa=True`)。原稿は各15〜40語の自然文(通常はPrimary PASS)。
  - 確認項目: `status=OK`、`asr_judgement`の記録(state/primary/value_guard)、`slowdown_applied`、`tts_generation_results.json`への`asr_judgement`、試聴リスト導出、費用記録、Master Store/共有state不変(`shared_state_unchanged`)。
  - 強制NG(Secondary経路)は**この入口では行わない**: narrator固有のNG→HRは07bで実音声済みで、再度cool-down(600秒)を踏むため。Primary NG→Secondary→PASS_WITH_WARNINGは同helperのX-A2-05/06・Z-A2-01で実音声済み。
- コマンド(案): `cd C:\Users\tensh\eigo-radio; $env:TTS_EXECUTION_MODE='STANDARD'; .venv\Scripts\python.exe er078_auw_runtime_evidence_09.py bnarr --execute --budget-jpy 5`。実行前に `tools/stop_scope_check_01.py --managed-id ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 --run-dir er058_output/unified_all_roles_production_wiring_01/evidence_09/bnarr --out …/stop_check_prepaid.json` が rc=0 であること。STOPセンチネル: `evidence_09/bnarr/STOP`(配置のみ、削除・回避しない)。
- 見積: 4〜5 clip。TTS 0.0243円/秒×(約8〜20秒)＋減速後Primary ASR×2(0.0047円/秒)→ 1 clip 約0.4〜0.7円 → **合計 約JPY 2〜4**(上限JPY 5、停止規則JPY 4.5)。所要約10〜15分(1clip 約90〜120秒、cool-downに入らない前提。万一NGでCS有効roleの最終attempt前に入る場合は`timeout 1500`)。**1回のみ・再起動は委任文で明示許可された場合のみ**。
- 同時に実施する「区分1」の裏付け補強(任意): X-B1-06のX入口 `kp4` 1本(約JPY 0.7)。
- Family C JA(C-01の区分5)は本計画の対象外(FCJ案件。OPEN-372解消後に`crun`相当を再実施)。依存関係として記録。

### 3-4. 「黙って除外していない」ことの自己確認

- 43行すべてに区分を付した(上表。35＋2＋5＋1)。
- 未充足条件(`CLOSEOUT_PLAN_07.md` §4): 条件1・2・4・9の残＝**B-A2-01のnarrator(本計画の対象)とC-01のJA新規生成(区分5、OPEN-372依存)**。条件12(merge)・15(Fable独立照合)も別途未充足のまま。
- 本計画の区分5(C-01 JA)は「AUW実装漏れ」ではなく別Production不具合として記録したうえで、**AUWのProduction Wiring受入条件(条件1・2・4・9)から除外しない**。`PRODUCTION_WIRED`宣言前に、(1)B-A2-01 narrator実音声、(2)OPEN-372是正後のC-01 JA実音声、が必要であることを明記する。
- 区分3の5行は「仕様どおり判定なし」だが、X-B1-06のみ注①の確認事項を残した。

---------------------------------------------------------------------------------------------------

## 4. Opus台帳(`docs/pm/OPUS_FINDINGS_LEDGER.md`、記載のみ・状態遷移なし)

Grep `OF-AUW` の関連ID(状態は台帳の現記載):
- **OF-AUW-06**(`:336`、LR後v1のforce_secondary、`USER_DECISION_PENDING`)＝U2。
- OF-AUW-08(`:338`、JA受理集合縮小・ORTHOGRAPHIC_VARIANT_CONFIRMED、`FABLE_ADOPTED`)＝JAの受理集合(U1解放後もEXACT/NORMALIZED＋2エンジン確認のみ)。
- OF-AUW-11(`:341`、PASS→NG全件確認、`FABLE_ADOPTED`)＝U1解放のRegression受入基準(旧PASS→新NG=0)。
- OF-AUW-01(`:331`、値ガード)・OF-AUW-03(`:333`、引継ぎ再判定)＝U1解放後も保護差を維持する根拠。
- OF-AUW-17(`:347`、新ラベルの下流allowlist)＝解放後に新規ラベルは増えない(既存`SECONDARY_CONFIRMED`のみ)ため追加作業なしの見込み。
- C1/類似度に直接該当する台帳エントリ: **無し**(C1はOPEN-258の`OPUS_REVIEW_01.md`必須1が出典で、`OF-AUW-*`台帳外)。委任文が参照する`OF-AUW-C-01/02`(06c)も台帳に未登録。

---------------------------------------------------------------------------------------------------

## 5. 新規発見の独立問題(OPEN候補、記載のみ・実装しない)

1. **`U2_FORCE_SECONDARY_SCOPE`は死んだ定数**(`judge.py:66`、参照はtest `:207`のみ)。名目と実体が不一致(§2)。
2. **SSOT記述の不整合**: (a)`CURRENT_SPEC.md:2685`「LR後v1=標準Prompt・force_secondary=True」はA2では不正確(A2のLR再TTSはminimal fallback attempt関数＝`er003_v1_crosslevel_audio_02_common.py:409-413`)。(b)`CURRENT_SPEC.md:1933`の「fallback音声は全てSecondary必須」はKP側が2026-09-01(`8503226c2`)に撤去済みで現状より広い。
3. **U1: `reading_dictionary_mismatch`/Latin原稿語のunit test不足**: 解放後、登録読み辞書違反がSecondaryのEXACT判定で素通りしないことを確認する負例testが無い(§1-3の「残る要検証点」。委任_10で追加)。
4. **既存失敗2件**: `er007_ja_secondary_asr_01_test.py::test_koro_kanji_variant_confirmed_by_reading_candidates`・`::test_single_engine_repetition_does_not_confirm_orthographic_variant`がHEAD `b010cb469`でU1に関係なく失敗(`PHONETIC_MATCH`≠`ORTHOGRAPHIC_VARIANT_CONFIRMED`)。AUWのOF-AUW-08(R+)との関係・main側での状態は**未調査**。
5. **Melos japanese_title(Family Z)のPrimary転写がHangul**(`japanese_title_attempt3…json`: `asr_text="시리에 매우스"`、similarity 0.0、attempt1〜5が存在): Primary ASRの言語誤認識か、TTSが日本語を発話できていないか未判別。U1の(e-2) live Azureで切り分けられるが、TTS側の不具合なら別案件(OPEN-372と同種の「JA TTS言語固定」の可能性は**推測**)。
6. **A3(length)・A4(C2)の扱い**: A-2「不一致の種類・大きさにかかわらず原則Secondary」の文言上は除外表の全規則が対象に見えるが、A-3の実行要件はC1・類似度のみ。本計画はA3/A4維持としたため、Fableの解釈確認事項(新仕様候補ではなく解釈確認)。

---------------------------------------------------------------------------------------------------

## 6. 次委任(委任_10)の実行順序と見積(承認後)

| 順 | 作業 | 費用 | 時間 | 並列 |
|---|---|---|---|---|
| 1 | Opus条件Cレビュー(§1-6) | - | Fable判断 | - |
| 2 | U1: 定数1行＋α test更新＋frozen replayのtest化＋負例追加(Latin/辞書読み) | 0 | 約40分 | A |
| 3 | U2: 定数整理＋SSOT注記訂正(コード挙動不変) | 0 | 約15分 | A(2と独立) |
| 4 | (e-2) 保存wav＋live Azure 約8本 | 約JPY 3 | 約10分 | B(2・3と独立。実行はコード変更前でも可＝判定器は現行を呼ぶため`U1=True/False`両方をscript内で切替) |
| 5 | B-A2-01 narrator 4〜5 clip 実音声 | 約JPY 2〜4 | 約15分 | B(4と独立。API別、同時でなければrate limitなし) |
| 6 | 全関連test再実行、Dangling/Grep、commit | 0 | 約20分 | - |

合計費用見積: **JPY 5〜7**(目標70円/記事セットとは別枠の開発費。当日開発費1,000円内、AUW当日既使用約JPY 1.3＋本計画0)。

---------------------------------------------------------------------------------------------------

## 7. SSOT追記文案(次委任で使用。本委任では編集しない)

### 7-1. DECISION_LOG.md(末尾追記)
- 2026-10-16 | ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_10 **U1是正**(承認済み仕様への実装修正、新仕様ではない): ユーザー指示A-3「現在のU1(REGISTER #83)は、ユーザー正式承認済み統一仕様との不整合として扱う…固有名詞差でもPrimary NGならSecondary確認／低類似度でも…／数値・否定等の保護差、独立QAは例外として維持」に従い、`er078_asr_unified_judge_01.py:65` `U1_KEEP_C1_SIMILARITY_EXCLUSIONS`を`False`へ(1行)。A5(類似度<0.4)・A6(C1固有名詞差)はPrimary NGでもSecondary 1回に回る。維持=P1(値DIFF・否定差)・A3(length NG)・A4(C2同形異音語、2026-10-11ユーザー逐語採用)・最終ANDゲート・独立QA。根拠=2026-10-11のC1は`OPUS_REVIEW_01.md`必須1のFable採用でユーザー個別承認の逐語なし(`REDETERMINATION_CHECK_01.md:35`)、類似度0.4はPhase 0の既存除外(要観察と記録、`RESULT_01.md` §(3))。frozen replay: 25行中差分2行(g7,g8、いずれもSecondary正答)、C群誤PASS 0、旧PASS→新NG 0。ロールバック=定数を`True`へ戻す1行。
- 2026-10-16 | 同 **U2整理**(コード挙動不変): `force_secondary=True`は`er003_v1_crosslevel_audio_02_common.py:364`(A2 minimal fallback、LR再TTS含む)の1箇所のみ。起源=2026-08-26ユーザー承認(OPEN-66 Part C、No.7 A2誤PASS事故)で、LR固有の規則ではない。B1へは拡大しない。`U2_FORCE_SECONDARY_SCOPE`定数は未参照のため[削除/コメント化]。

### 7-2. CURRENT_SPEC.md(統一ASR判定仕様の節、`:2688`「暫定値」行の置換案)
- 「**U1(是正済み)**: JAのC1固有名詞差・類似度<0.4はPrimary NGでもSecondary 1回へ回す(`U1_KEEP_C1_SIMILARITY_EXCLUSIONS=False`)。保護差(数値・否定)・length NG・C2同形異音語・独立QAは従来どおりSecondary不呼出で維持。**U2**: `force_secondary`は2026-08-26承認の『minimal instruction fallback音声はSecondary必須』(OPEN-66)であり、現行はA2 minimal fallback(LR再TTS含む)のみ。B1へは拡大しない。」
- `:2685`「LR後v1=標準Prompt・1 attempt・`force_secondary=True`(U2暫定)」→「LR後v1: B1=標準Prompt・1 attempt・Secondary必須なし／A2=minimal fallback attempt(2026-08-26のSecondary必須が継続)」。
- `:1933`への注記(既存行は書換えず追記): 「KP側の`force_secondary=True`は2026-09-01(`8503226c2`)に撤去済み。現行はA2 minimal fallbackのみ」。

### 7-3. OPEN_ITEMS.md
- 新規OPEN候補(§5-1〜5-6)を1行ずつ起票候補として列挙(OPEN番号は次委任のSSOT編集権者が採番)。
- OPEN-371(U4)・OPEN-372(F4=区分5の依存)・OPEN-373(再利用時値ガード偽陽性)は本計画で変更なし。OPEN-372の備考に「C-01のJA新規生成部分は43行マトリクス区分5」を追記。
- `USER_DECISION_REGISTER_01.md` #83(U1)は「**指示A-3により実装修正扱い(USER_DECISION_REQUIRED解除)**」、#84(U2)は「維持・記述訂正」へ更新(正式なユーザー判断の再質問はしない)。

---------------------------------------------------------------------------------------------------

## 8. 受入記録

1. 当初目的(ユーザー原文、委任文逐語): A-3「現在のU1（REGISTER #83）は、ユーザー正式承認済み統一仕様との不整合として扱う。現在の固有名詞差・類似度0.4未満等によるSecondary事前除外を調査し、承認済み共通ルールに合わせて是正する。…これは新仕様Trialではなく、承認済み仕様への実装修正である」／A-4「U2（REGISTER #84）について、A2_ONLYの既存例外の意味・成立経緯・品質上の必要性を確認する。…Primary PASS時のSecondary強制照合を、根拠なく全レベルへ拡大してはならない」／A-5「43行マトリクスを次の区分で再整理する。…特にFamily B A2 narratorの見出し・Hook・Tension・Closingの必要な実音声確認を実施する。…全SectionのProduction Wiring受入条件から未確認項目を黙って除外しない」。
2. 最終成果物: 本書 `er058_output/unified_all_roles_production_wiring_01/U1_U2_SECTION_PLAN_09.md`(新規・未追跡)、`docs/pm/RESULT_PACKET_AUW9.md`、`docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_09.md`(+`_check.json`)。
3. 証拠: §1-1(コード行)、§1-2(SSOT原文)、§1-3(`U1=False`差し込み実験: 関連11 file 382 test、失敗14件＝α12＋既存2)、§1-4(保存データ集計29件)、§1-5(frozen replay 25行: 差分2行、C群誤PASS 0)、§2(原文・コード照合)、§3(マトリクス43行区分)。
4. 一致・不一致: A-3(是正計画)＝一致(frozen replay・シナリオ実験で保護差維持と誤受理0を実測)。A-4(成立経緯・根拠調査・結論案)＝一致。**A-5の「実音声確認を実施する」は、本委任がread-only(API 0)のため「実行計画の作成」まで**(実音声取得は委任_10)＝**意図的な不一致(範囲外)**。A3/A4を触らない点はA-3の列挙範囲に合わせた解釈(§5-6でFableへ確認事項として明示)。
5. 判定: `PLAN_READY`(Opus条件Cレビュー要否はFable判断)。実装・実音声・Production変更は未実施。
