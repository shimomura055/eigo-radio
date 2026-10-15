# DESIGN_01: ASR/TTS統一判定・数値保護是正・全Section Production Wiring 実装設計書

管理ID: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_01(Phase 1〜2、2026-10-15)
性質: Read-only調査+設計文書。Productionコード/Prompt/flag/test/SSOT/`user_test/`は無変更、有料API 0、費用JPY0。
Status: 管理ID全体=`APPROVED_FOR_PRODUCTION`(ユーザー正式決定2026-10-15)。本書の到達上限=`DESIGN_READY_FOR_OPUS_A`(11-3条件A=新しい処理フロー、Opus独立技術レビュー待ち)。`PRODUCTION_WIRED`ではない。
基準commit: `233c0cb4d`(行番号は同commit時点)。使用モデル: コード読解のみ(API 0、評価系モデル使用なし)。
照合した既決資料: `docs/research/ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01/REDETERMINATION_CHECK_01.md`、`er058_output/design/UNIFIED_FLOW_SPEC_V04.md`(特に L36-52, L56-79, L95-127, L129-145, L147-170, 8章 D-1〜D-19)、`CURRENT_SPEC.md` L1543-1580(Family体系)・L1712(TTS総試行3回)・L2014-2030、`docs/pm/PM_GOVERNANCE.md` L179-272(2-0, Gate 1〜7)。

---

## 0. 先に結論(PM向け)

1. **実装の最小点**: ASR判定の呼出点は、Production全体で **EN 7箇所+JA 4箇所=計11箇所(7ファイル)** に集約できる(§3.1の裏取り)。判定ロジックは2関数(`er006_secondary_asr_01.evaluate_attempt_with_cascade_detail` と `er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail`)に集中しているため、**新規の共通判定モジュールを作り、この2関数を薄いadapterに置換する**方式を推奨する(呼出側の署名は維持)。これで全Family(X/Z/legacy A/B/C)・全Sectionに同一判定が及ぶ。
2. **数値S1の是正**: 値と単位で比較する共通ガード(新規`er078_asr_value_guard_01`)を作り、英語は既存Tier1の数値atom(`er021`)とValidatorの`_is_number`欠陥(`N%`等を数値扱いしない)を、日本語は10/13 JA Trialの値署名(`er066`のStage 1相当のみ)を再利用する。ユーザー提示9例はtest caseに固定する(§5.7)。「十分」は機械的に同値化せず、文脈マーカー(「十分間」等の閉集合)がある場合のみ同値、それ以外は曖昧扱い(自動同値化しない)とする。
3. **競合(STOP候補)**: 承認範囲内で解消できる案を付けて13群を列挙した(§6)。**ユーザー確認を推奨するのは1問のみ**: 日本語の固有名詞差(C1)・類似度0.4未満の不一致を、今回の「不一致の種類によらず原則Secondary」でSecondaryへ回してよいか(10/11ユーザー承認の除外条件の扱い)。暫定実装は現行維持(除外表をデータ化し、確認後に1行で解放可能)で、実装はこの回答を待たずに進められる。
4. **実API費用の見積**: runtime evidenceは既存音声・保存転写の再判定を最優先し、新規実API(TTS/ASR)は **約JPY8(見積幅JPY5〜15、上限案JPY15・hard stop JPY20)**(§9)。
5. **実装分割**: 委任_02(共通判定+数値S1+Unit、JPY0)→委任_03(EN配線)→委任_04(JA配線+試聴リスト)→委任_05(A2減速・Dialogue汎化+KP)→委任_06(runtime evidence)→委任_07(SSOT/Gate 3・4・7)。各段で既存test全回帰(§10)。
6. 本書は新たなTrialを必要としない。Trial候補が出た場合は承認なしに開始しない(§6 C-A, C-L)。

---

## 1. 承認仕様の要約(ユーザー原文を逐語引用し、既存で充足/変更要/新規を付す)

判定凡例: **充足**=既存Productionで満たされている(変更不要)/ **変更要**=既存機構の変更・拡張が必要/ **新規**=現状に存在しない機構。根拠は`ファイル:行`。

### 1-A. 原文§2 基本フロー

| # | 原文(逐語) | 判定 | 根拠・備考 |
|---|---|---|---|
| 2-1 | 「TTS生成① → Primary ASR → NGならSecondary ASR」「両方NGの場合：TTS再生成② → Primary ASR → NGならSecondary ASR」「両方NGの場合：TTS再生成③ → Primary ASR → NGならSecondary ASR」「3回とも不合格の場合、既存の安全条件に従いLocal RewriteまたはHuman Reviewへ進む。」 | **変更要** | 現行は標準2+minimal1(`er011_human_review_lock_01.py:80-104`)。EN Cascade尽きは再生成せずHR直行(`er006_secondary_asr_01.py:947-949` `stop_retrying=True`)。3回上限自体は`PRODUCTION_MAX_TTS_ATTEMPTS=3`(L80)・05A通算化(`er003_v1_n3_01_tts_generate.py:341-378`)で充足 |
| 2-2 | 「Primary PASSなら、その時点でASR合格。Secondaryは不要。」 | **充足**(例外のみ変更要) | EN: `er006_secondary_asr_01.py:812-818`(verified→return、Secondary不呼出)。JA: `er007_ja_secondary_asr_01.py:412`(`not cls.should_pass`のみSCG)。例外=`force_secondary`(minimal経由、`er003_v1_crosslevel_audio_02_common.py:341-351`/`er006_secondary_asr_01.py:779`)はminimal撤去に伴い整理(LR後v1のみ維持、§6 C-D) |
| 2-3 | 「Primary NGなら、不一致の種類によらず原則Secondaryを実行する。」 | **変更要** | EN: `cascade_eligible = is_entity_like_mismatch or is_homophone_candidate_mismatch`(`er006_secondary_asr_01.py:812`)が数値・否定・通常内容語差をCascade対象外にしている。JA: SCG除外条件(`er007_ja_secondary_asr_01.py:188-216`)。いずれも§6 C-Aで整理 |
| 2-4 | 「Primary NG・Secondary PASSなら、**PASS_WITH_WARNINGとして採用**する。」 | **変更要** | JA SCGは`SECONDARY_CONFIRMED_PRIMARY_FALSE_NG`で通常PASS扱い(`er007_ja_secondary_asr_01.py:82,429-437`、警告記録なし)。EN Tier3は`SECONDARY_ASR_CORROBORATED_MATCH`(warning付きだが試聴連動なし、`er021_*:47`)。CS/Eq層/M1のみ`PASS_WITH_WARNING`相当(`er006_secondary_asr_01.py:645-648`、`_m1_accept` L211-220) |
| 2-5 | 「PASS_WITH_WARNINGはユーザーの事前承認を求めず、自動採用する。」 | **充足**(現行も事前承認なし)+非ブロック性を明文化 | 既存`PASS_WITH_WARNING`は`status=OK`でAssembly Gateを通過(`er003_v1_n3_01_assemble.py` verify_episode_audio_validation_gate)。新設リストは**非ブロッキング**(§4-6) |
| 2-6 | 「WARNING音声はユーザーが事後試聴できるリストへ自動登録する。」 | **新規** | 本番コードにGrep該当0件(REDETERMINATION_CHECK_01 §1 Q2)。`user_test/asr_misread_listen_01`は05Bの一回限り静的ページ(Trial)で、生成コードは本番にない。生成元候補: `er019:2092 build_player_html`、`er063:1312 build_listening_page_html` |
| 2-7 | 「Primary・Secondary両方NGなら次のTTS再生成へ進む。」 | **変更要** | 2-1参照。UNCERTAIN直行HR(D-7)を置換 |
| 2-8 | 「Secondaryが障害・利用不能の場合、PASS扱いせず、既存の安全な障害処理へ進む。」 | **変更要**(言語間不整合の解消) | JA: `UNAVAILABLE`→従来動作(再生成、`er007_ja_secondary_asr_01.py:312-316`)。EN: step内`text None`でCascade継続→最終HR(`er006_secondary_asr_01.py:877-948`)。統一処理は§4-4 |
| 2-9 | 「同じ音声に対するSecondaryの重複API呼び出しを防ぐ。」 | **新規** | EN単一音声で最大6箇所からAzure呼出(`er006_secondary_asr_01.py:405,700,760,784,876,914`)。キャッシュなし。§4-5 |
| 2-10 | 「各TTS再生成では、原則として原稿・Prompt・モデル・Voice・速度を維持する。」 | **変更要** | 標準2+minimal1(attempt3でPrompt変更、`er003_v1_crosslevel_audio_02_common.py:79-130,301-360`、`er003_v1_n3_01_tts_generate.py:584-700`、`er003_v1_sing01_point_headings_aoede.py:77-100`)。KPは4回(MINIMAL2+ENGLISH_LOCK2、`er003_v1_repro01_main_generate.py:761-830`)=Section固有例外で維持(§6 C-B) |
| 2-11 | 「既存の無音・反復・言語違い・異常長・発音品質等の独立QAは維持する。」 | **充足**(維持) | disfluency/Repetition QA(AND)・異常長(`detect_duration_anomaly`)・symbol gate。本設計は触らない |
| 2-12 | 「既存のHuman Review Lock、承認・停止・予算上限は維持する。」 | **充足**(維持) | `er011_human_review_lock_01.py:68-69,297,355`、STOP sentinel(`er063:863`)。WARNINGはHR queueへ入れない |

### 1-B. 原文§3 数値保護の設計是正

| # | 原文(逐語) | 判定 | 根拠・備考 |
|---|---|---|---|
| 3-1 | 「**表記ではなく、数値の値と単位で比較できる仕組みに是正する。**」 | **新規**(共通ガード)+**変更要**(Validator) | JA `_DIGIT_RE=\d+`(`er007_ja_asr_validator_01.py:67`)、EN `_is_number=isdigit()`(`er006_preprod_hardening_01_validation.py:622-623`) |
| 3-2 | 必須の正例・負例9行(三人/3人、三人/四人、三十人/30人、三十人/40人、十分/10分、100円/百円、20%/20 percent、20%/30%、25%/26%) | **新規**(test caseに固定、§5.7) | 現行実測(V04 L115-124): 三人→四人は見逃し、二人↔2人は誤発火、25%→26%は穴 |
| 3-3 | 「既存の英語Tier1数値等価・日本語表記ゆれ正規化・数値Validatorを優先的に再利用する。」 | 再利用方針(§5.3) | Tier1=`er021_en_asr_semantic_equivalence_production_01.py:394-698`、JA=`er066_ja_asr_orthographic_equivalence_01_trial.py:23-112`(Trial、Stage 1のみ昇格) |
| 3-4 | 「数値の異値を単純なSecondary文字起こし一致だけで誤PASSさせない。」 | **新規** | 保護差(値/否定)は**Secondary不呼出+最終ANDゲート**(§4-3) |
| 3-5 | 「否定の有無・意味の反転に対する既存の保護は維持する。」 | **充足** | EN `protected_check` L673-676、JA `protected_check_ja` L263-266+SCG推奨4(`er007_ja_secondary_asr_01.py:109-214`) |
| 3-6 | 「漢数字・算用数字・数詞・助数詞・単位・割合の値を比較する。」 | **新規** | §5 |
| 3-7 | 「曖昧な読みの数値表現は、文脈を無視して機械的に同値化しない。」 | **新規** | `AMBIGUOUS_RE`(`er066_*_trial.py:45-51`)+閉集合マーカーのみ同値(§5.5) |
| 3-8 | 「数値を含むだけでSecondaryを一律禁止する旧来の過剰制限は撤廃する。」 | **変更要** | JA: `number_mismatches`非空でSCG不実行(`er007_ja_secondary_asr_01.py:197-198`)。表記差のみでも発火(実run `attempt_history.jsonl` L12833,L13161)。EN: 数値差はCascade対象外(L812) |
| 3-9 | 「既存の正規化仕様と競合・重複させない。」 | 設計制約 | 既存`normalize_numeric`(EN L335-401)・`normalize_ja`・Tier1を再実装せず呼び出す。重複排除の対応表は§5.4 |
| 3-10 | 「対象の初回・retry・fallback・regeneration経路で同じ判定を使用する。」 | **変更要** | 判定点11箇所(§3.1)を共通adapter化 |
| 3-11 | 「数値・否定などの明確な重大内容差を誤採用しないことを優先」「保護すべき差異を警告だけで無条件に解放する仕様にはしない」 | **新規**(優先規定) | 保護差は警告でも解放しない(§4-3、§6 C-J) |

### 1-C. 原文§4 Connected Speech・M1の再利用

| # | 原文(逐語) | 判定 | 根拠・備考 |
|---|---|---|---|
| 4-1 | 「B1 Connected Speech Validator / Connected Speech Equivalence Layer / M1 OOV Multi-Pronunciation / F1残差検査 / Pronunciation Ledger / 既存の音韻・同音語判定」を再利用 | **充足**(Primary側判定として維持) | B1=`er011_b1_connected_speech_validator_01.py:240`、Eq層=`er011_connected_speech_equivalence_layer_production_01.py:215`+`er006_secondary_asr_01.py:622-660`、M1=`er006_m1_multi_candidate_01.py:485`(全cascade段へ配線済みcommit `94fb0c03f`)、F1=`er006_preprod_hardening_01_validation.py:958`(commit `7948bd78e`) |
| 4-2 | 「`Melos said.` の2026年10月14日の実音声検証は重要なRegression基準」(Full Story相当12/12、Dialogue・見出し相当12/12、M1新規救済21観測、M1起因の誤受理0件) | Regression基準として固定 | `er077_output/m1_oov_multi_pronunciation_01/EVIDENCE_RUN_01.md` §2(12/12,12/12,21件,誤受理0)。再現は保存転写から(API 0、§8-3) |
| 4-3 | 「必要なRoleへ共有機構として適用」 | **変更要**(適用漏れの解消) | M1は`m1_enabled=True`既定で全英語経路に有効。Tier1/CS層/LRは5role限定(`er020:124-175`、`er021:43-45`)、見出し/KPは明示除外。今回は**値ガードのみ全Section**、Tier1/CS層gateは不変(§6 C-G) |
| 4-4 | 「自然な発音を許容することと、別の語・意味変更を無条件に許容することを混同しない。」 | **充足**(維持) | M1: 凍結候補のみ・矛盾拒否・ASR後付け候補なし(EVIDENCE_RUN_01 §2)。最終ANDゲート(値/否定)で更に多重化 |

### 1-D. 原文§5 適用範囲とSection固有例外

| # | 原文(逐語) | 判定 | 根拠・備考 |
|---|---|---|---|
| 5-0 | 「英語・日本語の全Family、Productionで生成する全音声Sectionを対象とする。」「Role一覧をProductionの実装・SSOTから洗い出し、適用漏れがないことを確認する。」 | **変更要** | §3(全43行マトリクス、11判定点の裏取り) |
| 5-1 | 「**Key Phrase**：学習対象の英語表現は変更しない。既存Minimal Prompt／English Language Lockとの整合を確認。全体のTTS3回仕様との競合は整理する。」 | **充足**(既存例外維持)+競合整理 | 4回構成=2026-09-01ユーザー正式決定(`er011_human_review_lock_01.py:99-103`コメント)。判定のみ統一し構造は維持(§6 C-B) |
| 5-2 | 「**日本語Local Rewrite**：現行の英語用機構を機械的に流用しない。安全な実装が成立していない場合はHuman Reviewへ進める。」 | **充足** | JA leafにLR呼出なし(`er003_v1_n3_01_tts_generate.py:584-700`、`er003_v1_sing01_voice01_generate.py:434-580`にrun_local_rewrite_recoveryなし)。`identify_ng_span`が日本語でfound=False(`JA_LOCAL_REWRITE_APPLICABILITY_01.md`)。3NG→STOPPED→HR Lock |
| 5-3 | 「**見出し・短文**：独立したQA・意味保護を維持する。」 | **充足**+**変更要**(見出しのminimal2撤去) | 見出し=標準1+minimal2(`er003_v1_sing01_point_headings_aoede.py:77-100`)。OPEN-288 D-5(§6 C-D) |
| 5-4 | 「**A2の6%減速**：減速前後のASR検証・再生成回数・音声品質が整合すること。」 | **変更要** | 05A通算3共有は済(`n3_tts.py:341-378`)。減速後再検証の判定を統一(`apply_a2_slowdown_postprocess` L172-282)。Dialogue(Std)/Voices A2は外側ループなし(§3 Z-A2-02, B-A2-01)=不整合を解消 |
| 5-5 | 「**Dialogue**：複数Voiceの区分・話者帰属・既存Segment構造を維持する。」 | **充足**(維持) | 判定のみ差し替え。`er063:298-377`の話者帰属Gate・voice割当は不変 |
| 5-6 | 「新しいSection固有の例外を実装都合で勝手に増やさない。」 | 設計制約 | 例外表(§3の列「Section固有例外」)は既存のみ。新規例外ゼロ |

### 1-E. 原文§6 Local Rewrite・Human Review

| # | 原文(逐語) | 判定 | 根拠・備考 |
|---|---|---|---|
| 6-1 | 「TTS3回の不合格後は、既存のLocal Rewrite回復機構を利用する。」「英語：意味・Fact・role・前後文脈・局所性・全文性を保持できる場合のみLocal Rewriteを許容。」 | **充足**(Gate 7候補QA既存)+**変更要**(発火位置) | `er020:686-752`(7 Gate: 局所性`check_locality`L497、全文性`validate_candidate_is_full_segment`L351、数値保存`check_numeric_preservation`L276)。発火位置はcascade尽きでもあった(`crosslevel` L247-262, L292)→3NG後に整理 |
| 6-2 | 「日本語：現時点では原則Human Review。」 | **充足** | 5-2 |
| 6-3 | 「Key Phrase：学習対象の表現を別表現に置き換えない。」 | **充足** | `er020:117 NON_APPLICABLE_SEGMENT_IDS`(見出し)・`_KEY_PHRASE_PATTERN`→KEY_PHRASE=LR対象外(`connected_speech_enabled_for` L162-167) |
| 6-4 | 「原稿の問題ではなくASR誤認と推定される場合は、安易に原稿を書き換えない。」 | **新規**(LR発火条件) | 現行は`stop_retrying`(UNCERTAIN)でもLR発火(`crosslevel` L247-262)。「両エンジン合意誤読のみ」に絞る(§4-7、D-9(b)) |
| 6-5 | 「Rewrite後は同じ統一ASR判定を適用。」 | **変更要** | LR再TTSがminimal経由(`crosslevel` L392 `_retts_fn`→L301 `_run_a2_minimal_fallback_attempt`)。統一判定+標準Promptへ |
| 6-6 | 「Rewriteの発火・再TTS回数を正しく計数し、累積上限を守る。」 | **変更要** | LR再TTS未計数(V04 D-17、Coffee記録4/実際5)。`record_outcome`計数に加算(§4-7) |
| 6-7 | 「既存のHuman Review承認を回避・解除してはならない。」 | **充足**(維持) | `er011_human_review_lock_01.py:297-353` |

### 1-F. 原文§7 実装上の重点事項

| # | 原文(逐語) | 判定 | 根拠・備考 |
|---|---|---|---|
| 7-1 | 「Primary／Secondary判定を共通化し、Role別の重複実装を避ける。」 | **新規** | `er078_asr_unified_judge_01`(§4) |
| 7-2 | 「既存Cascadeと新統一フローを整理し、同一音声へのAzure二重呼び出しを防ぐ。」 | **新規** | §4-5(sha256キャッシュ) |
| 7-3 | 「ASR結果・判定理由・WARNING・コスト・所要時間を監査可能にする。」 | **変更要** | `attempts_detail`(`er011_human_review_lock_01.py:212-234`、委任_04A)に`asr_judgement`をadditive追加(§4-6) |
| 7-4 | 「PASS_WITH_WARNINGの最終試聴リストへの自動連動を完成させる。」 | **新規** | §4-6 |
| 7-5 | 「Production初回だけでなく、retry／fallback／regeneration／Local Rewrite後の経路まで整合させる。」 | **変更要** | 判定点11箇所すべてadapter化(§3.1) |
| 7-6 | 「DEV／Trial専用スクリプトへの実装で終わらせない。」 | 設計制約 | `er078_*`はProduction leafからimport(Trial/DEV scriptには配線しない) |
| 7-7 | 「既存の正常な動作を壊さず、ロールバック可能性を確保する。」 | 設計制約 | commit単位ロールバック(§7、flag不要=承認済み) |

---

## 2. 既存資産マップ

凡例: 配線先=Production到達経路。「評価記録」=実run/Trial/テスト記録。EN/JAは言語別。

### 2-A. 英語

| 機能 | モジュール・関数(ファイル:行) | 配線先(呼出元) | test | 評価記録・状態 |
|---|---|---|---|---|
| Primary ASR | `er006_asr_provider_routing_01.transcribe`(OpenAI gpt-4o-mini-transcribe) | 判定点7箇所(§3.1) | - | PRODUCTION_WIRED |
| 判定本体 | `er006_preprod_hardening_01_validation.classify_asr_match`(L1192、wrapper)/`_classify_asr_match_core`(L980)/`protected_check`(L646) | 全EN判定点 | `er006_preprod_hardening_01_validation_test.py`(55件) | PRODUCTION_WIRED |
| 数値(正規化) | `normalize_numeric`(L335)。`%/$/小数`を`xpercentx/xdollarx/xdecimalpointx`マーカーへ。`20%`=`20 percent`は全roleで正規化により同一token | 全EN | 同上 | **穴**: `_is_number=isdigit()`(L622)がマーカー付きtokenを数値扱いしない→`25%→26%`は`number_mismatches`に掛からず内容語差分化(V04 L113) |
| 数値Tier1 | `er021_en_asr_semantic_equivalence_production_01.tier1_numeric_equivalence`(L635)、atom抽出`_tier1_atoms`(L394)、`atoms_public`(L624) | `classify_asr_match`冒頭、5role限定(`FIVE_ROLES_APPLICABLE` L43) | `er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`(62件) | PRODUCTION_WIRED(2026-09-27承認、NUMERIC_EQUIVALENCE_MATCH実run47件) |
| 否定 | `_NEGATION_WORDS`(L397)、`protected_check` L673-676、Tier1 diff-anchored二重防御(L1209-1220) | 全EN | 同55件 | PRODUCTION_WIRED。合成否定26/26ブロック |
| Connected Speech(B1) | `er011_b1_connected_speech_validator_01.classify_connected_speech`(L240)+F1`_f1_refine_residual_kind`(`validation.py` L958) | `_classify_asr_match_core` | `er011_b1_connected_speech_validator_01_f1_test_01.py` | PRODUCTION_WIRED(F1=`7948bd78e`、WIRED_PENDING_RUNTIME_EVIDENCE) |
| CS Equivalence Layer | `er011_connected_speech_equivalence_layer_production_01.classify_connected_speech_equivalence`(L215)、呼出`er006_secondary_asr_01.py:622-690`(Azure `L405`+local whisper small) | `enable_connected_speech_equivalence_layer`(5role+bvoices既定True) | `er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py` | PRODUCTION_WIRED。`..._PASS_WITH_WARNING`実run3件 |
| Tier3(固有名詞等のSecondary corroboration) | `er006_secondary_asr_01.py:~690-750`(Azure `L700`) | Tier1と同じrole限定 | er021 test | PRODUCTION_WIRED。`SECONDARY_ASR_CORROBORATED_MATCH` 39件(attempt_history)/106件(telemetry) |
| M1 OOV複数発音 | `er006_m1_multi_candidate_01.m1_multi_candidate_judge`(L485)、`freeze_candidates`(L248)。呼出`er006_secondary_asr_01.py:_m1_try`(L192)/`_m1_accept`(L211) | 全cascade段(`m1_enabled=True`既定) | `er077_m1_oov_multi_pronunciation_01_test_01.py`(14件)+配線22件(`94fb0c03f`) | 2026-10-13承認。隔離evidence取得済み。`PRODUCTION_WIRED`宣言未(UDR #52) |
| Pronunciation Ledger | `er006_pronunciation_ledger_01`(`get_hint_for_text`)、`ledger_phrases`をAzure PhraseListへ | 各leaf | - | PRODUCTION_WIRED |
| Secondary(Azure) | `get_full_text_via_azure_stt_with_phrase_list`(`er006_secondary_asr_01.py:70`) | 6箇所(L405/700/760/784/876/914) | - | 1音声あたり最大6回(重複) |
| 4段Cascade | `evaluate_attempt_with_cascade_detail`(L535-981): Primary#2→Secondary#1→#2、尽きたら`human_review_required=True, stop_retrying=True`(L947-949) | `cascade_eligible`(L812)=entity-like/homophone候補のみ | `er006_retry_cascade_prod_01_eval.py` | PRODUCTION_WIRED(COST_GUARD $0.05/segment L243) |
| 非ラテンCascade(KP) | `enable_non_latin_cascade`(L756) | KP英語のみ | KP test | PRODUCTION_WIRED |
| force_secondary | L779-811(Primary PASSでもAzure必須) | A2 minimal(`crosslevel` L341-351)のみ | - | PRODUCTION_WIRED |
| TTS retry/LR | leaf: `voice01.generate_charon_english`(L47)、`news_tail_fix.generate_news_narration_wide_margin`(L61)、`crosslevel.generate_english_segment_with_fallback`(L79)、`bvoices.generate_voice_body_wide_margin`(L479)、`repro01.generate_narration_snippet_verified_strict`(L196)、`point_headings.generate`(L60)。LR=`er020.run_local_rewrite_recovery`(L686) | §3 | `er020_tts_retry_local_rewrite_fullseg_test_01.py` | LR位置: voice01 L359/news_tail_fix L368/crosslevel L411 |
| HR Lock | `er011_human_review_lock_01.py` `check_before_generation`(L297)/`record_outcome`(L355)/累積15回・ASR60回(L68-69) | `@guarded_generate` | 既存 | PRODUCTION_WIRED |
| cool-down | `er020.maybe_cooldown_before_attempt`(L63): CS有効roleの最終attempt前に600秒 | `repro01` L325等 | 05A test(`er058_asr_tts_prodfix_01_test_01.py` 27件) | D-14(c)現行維持 |

### 2-B. 日本語

| 機能 | モジュール・関数(ファイル:行) | 配線先 | test | 評価記録・状態 |
|---|---|---|---|---|
| Primary | `er007_ja_asr_validator_01.classify_ja_asr_match`(+Variant層`er011_ja_asr_variant_layer_01`、Reading Resolver) | JA判定点4箇所 | `er007_ja_asr_validator_01_test.py` | PRODUCTION_WIRED |
| 数値 | `_DIGIT_RE=\d+`(`er007_ja_asr_validator_01.py:67`)、`protected_check_ja`(L242)の数字branch(L255-262) | 全JA | - | **穴**: 漢数字値変更を見逃し、表記差(二/2,十分/10分,百/100,％/パーセント)で誤発火(V04 L115-124) |
| 否定 | `safety._has_negation_ja`、L263-266。SCG推奨4: ず/ません/ぬ/ざる/まい(`er007_ja_secondary_asr_01.py:109-214`) | 全JA | `er007_ja_scg_c2_neg_test_01.py`(17件) | 2026-10-11承認、PRODUCTION_WIRED |
| SCG(Secondary Confirm Gate) | `_run_scg_secondary_confirm`(L302)、除外`_scg_exclusion_reason`(L188)、呼出L412-437。PASS=`SCG_PASS_CLASSIFICATIONS=(EXACT,NORMALIZED)`(L83) | Primary=`TRUE_CONTENT_MISMATCH`のみ | `er007_ja_scg_test_01.py`(46関数)、`er007_ja_scg_phase0_regression_test_01.py` | 2026-10-11承認、PRODUCTION_WIRED、merge `382c56c5`。実run `attempt_history.jsonl` L12583 |
| JA Cascade(entity-like UNCERTAIN) | L440-: Primary#2→Azure#1→#2、ORTHOGRAPHIC_VARIANT_CONFIRMED | UNCERTAINのみ | - | PRODUCTION_WIRED |
| 値署名(表記ゆれ) | **Trial**: `er066_ja_asr_orthographic_equivalence_01_trial.py`(`find_spans` L85、`_to_value` L66、`COUNTERS` L29、`AMBIGUOUS_RE` L45、`value_form` L101、`trial_judge` L441) | **未配線**(Productionからimportされない) | `er066_*_test_01.py`(18)+`_test_02.py`(31) | Trial。敵対的反例74件の誤PASS 0、**採用判断なし**(OPEN-287) |
| LR | **なし**(機械流用不可) | - | - | 3NG→STOPPED→HR |
| 試聴(警告) | **なし** | - | - | - |

### 2-C. 共通(Cascade/HR/LR/試聴)

- 通算TTS上限: `PRODUCTION_MAX_TTS_ATTEMPTS=3`(`er011_human_review_lock_01.py:80`、CURRENT_SPEC L1712)。05Aで`generate_a2_segment_with_slowdown`の外側ループと通算共有(`n3_tts.py:341-378`)。
- 記録: `er011_output/attempt_history.jsonl`(キー: run_id/timestamp/theme_id/level/segment_id/language/canonical_text_sha256/action/tts_attempts_this_call/asr_calls_this_call/cumulative_*/result_status/human_review_reached/final_lock_state/budget_guard_triggered/duration_seconds、新しい行は+`semantic_equivalence`,`attempts_detail`)。HR queue: `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(キー: timestamp/canonical_text/wav_path/steps/cost_guard_triggered/final_status)。
- 試聴リスト相当: 本番に存在しない(§1 2-6)。Family Xは`er019:2092 build_player_html`、Zは`er063:1312 build_listening_page_html`と`er026 stage_pages`がそれぞれ独立のページ生成。

---

## 3. 全Family×言語×Section適用マトリクス

マトリクス本体(43行・16列)は`APPLICABILITY_MATRIX_01.csv`と同一内容。以下に全文を掲載する。Active Familyは**X/Z**(Yは実装なし)、**Legacy A/B/C**は専用変更なしで共有leaf経由に自動波及(CURRENT_SPEC L1543-1580、L1558「Regression対象として無理に更新しない」、L1565「共有moduleの変更は妨げない」)。

### 3.1 Role漏れ裏取り方法(Production runnerのTTS呼出箇所から)

手順と結果(本委任で実施、Read-only):

1. **ASR判定点を全数列挙**: 主要10ファイルで`\.transcribe(` / `classify_asr_match(` / `classify_ja_asr_match(` / `evaluate_attempt(_ja)_with_cascade(_detail)(`をGrepした(コマンドは本書末尾§12)。ASR→判定が行われる箇所は**11箇所**に集約:

| # | 言語 | 判定点(ファイル:行) | 経由するleaf |
|---|---|---|---|
| J1 | EN | `er003_v1_sing01_voice01_generate.py:232/238` | `generate_charon_english`(Topic intro/Preview/Comment/固定shell) |
| J2 | EN | `er003_v1_sing01_news_tail_fix.py:186/202` | `generate_news_narration_wide_margin`(Full Story/Point/In One Line/Z Adv narrator) |
| J3 | EN | `er003_v1_crosslevel_audio_02_common.py:334/348` | A2 minimal fallback+LR再TTS(`_run_a2_minimal_fallback_attempt`)。標準経路はJ5へ委譲 |
| J4 | EN | `er012_b_family_voices_production_01.py:546/549` | `generate_voice_body_wide_margin`(Dialogue/Voices本文) |
| J5 | EN/JA | `er003_v1_repro01_main_generate.py:340/349(EN)/374(JA)` | `generate_narration_snippet_verified_strict`(KP英語・KP解説・A2標準EN・A2標準JA) |
| J6 | EN | `er003_v1_sing01_point_headings_aoede.py:121/126` | 見出し(legacy A/B/C) |
| J7 | EN | `er003_v1_n3_01_tts_generate.py:186/196`、`:146` | `apply_a2_slowdown_postprocess`の減速後再検証+`_post_slowdown_cascade_rescue` |
| J8 | JA | `er003_v1_n3_01_tts_generate.py:647/651` | `generate_a2_japanese_with_fallback`のminimal分岐 |
| J9 | JA | `er003_v1_sing01_voice01_generate.py:508/515` | `generate_charon_japanese`標準 |
| J10 | JA | `er003_v1_sing01_voice01_generate.py:561/563` | `generate_charon_japanese`minimal |
| (J5-JA) | JA | `repro01:374`(上記J5に含む) | A2標準JA(preview/comment/japanese_title/KP意味) |

   (EN=J1,J2,J3,J4,J5-EN,J6,J7の7、JA=J5-JA,J8,J9,J10の4。計11)
   `er019_family_x_audio_production_runner_01.py`・`er063_family_z_audio_01.py`・`er006_audio_cost_pilot_02_shared_narration.py`・`er012_b_family_voices_a2_production_01.py`には**ASR直接呼出が0件**(全てleaf経由)であることもGrepで確認した。
2. **runner側のTTS呼出を全数列挙**: X runner(`er019:839,856,891,1026,1059,1215,1226,1244,1268,1339,1347`)、Z(`er063:real_generators` L606-702 = narrator/dialogue/topic_intro/preview/comment/japanese_title/kp_en/kp_ja/kp_expl_en)、legacy(`n3_tts.py:981,996,1016,1032,1064,1073,1133,1142,1149,1160,1177,1211,1219`、`er012_b_family_voices_production_01.run_tts_3v` L829、`er012_b_family_voices_a2_production_01.py:696,738,744`、`er013_family_c_production_runner_01.py:246,367`)。各呼出は§3の各行にleaf名と共に記載し、**どの行もJ1〜J10のいずれかに到達する**ことを確認(到達しないleafは0)。
3. **逆引き**: leaf 6種(voice01.generate_charon_english / news_tail_fix.wide_margin / crosslevel.fallback / bvoices.wide_margin / repro01.strict / point_headings.generate)+JA 3種(generate_a2_japanese_with_fallback / generate_charon_japanese / ...with_reading_safety)の全callerをGrepし、runner側列挙と突合(`er019_family_x_variable_role_style_wiring_01_confirmation_regen_01.py`等の過去one-off scriptは対象外=Production正式経路でない)。
4. **実装段での自動裏取り(委任_02で作成)**: 静的監査test(AST)`er078_asr_unified_wiring_static_audit_01.py`を新設し、Production moduleに「`routing.transcribe(` → `evaluate_attempt_*`の直接併用」が残っていないこと、および判定点11箇所が全て`er078_asr_unified_judge_01`を経由することを機械検査する(Gate 4 Dangling Reference Checkの一部)。

**Role一覧(漏れ確認の結果)**: Topic intro / Preview / Comment 1-4 / Full Story part1-3(+Z clip `full_story_part{n}_c{k}`) / Point one-two本文 / Point見出し / In One Line / Key Phrase英語 / KP英語解説 / KP日本語意味 / Japanese title / Dialogue(複数Voice) / 固定shell(Master Store) / A2 6%減速後再検証 / LR再TTS。SSOT側の根拠: `er020:resolve_narrative_role` L124-150(FULL_STORY/COMMENT/PREVIEW/TOPIC_INTRO/IN_ONE_LINE/HEADING_READOUT/KEY_PHRASE)、`er019_family_x_audio_plan_01.py:277-361`(X順序V2)、`er063:166-210 FAMILY_Z_ROLE_STYLE`(Z role key 14件)。いずれもマトリクスの行に対応。**未確認**: 現在のProductionで未使用のlegacy individual scripts(過去one-off)に残る旧leaf呼出(対象外と判断)。

### 3.2 マトリクス全文

| row_id | family | level | section_role | segment_ids | lang | leaf_generator(file:function) | runner_call_site(file:line) | current_primary | current_secondary | current_retry_structure | current_numeric_negation | section_specific_exception | unified_behavior_after | change_points | evidence_method |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| X-B1-01 | X(Active) | B1B(Advanced) | Topic intro | topic_intro | EN(Charon) | er003_v1_sing01_voice01_generate.py:generate_charon_english(L47,評価L232-248) | er019_family_x_audio_production_runner_01.py:839 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回(技術失敗時のみminimal切替)、3回目直前に600秒cool-down(CS有効role)、尽きたらLR→HR。cascade尽き(UNCERTAIN)は即LR/HR | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | なし(5roleのTier1/CS/LR対象) | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | 共通: er078_asr_value_guard_01(新)+er078_asr_unified_judge_01(新)+secondary結果キャッシュ+er078_pass_with_warning_registry_01(新)。voice01 L238のevaluate_attempt_with_cascade→unified_judge adapter。LR再TTS計数(L359) | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-B1-02 | X(Active) | B1B(Advanced) | Preview | preview | EN(Charon) | voice01.generate_charon_english | er019:856 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回(技術失敗時のみminimal切替)、3回目直前に600秒cool-down(CS有効role)、尽きたらLR→HR。cascade尽き(UNCERTAIN)は即LR/HR | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | disfluency QA維持 | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | X-B1-01と同一関数(追加変更なし) | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-B1-03 | X(Active) | B1B(Advanced) | Comment 1-4 | comment_1..comment_4 | EN(Charon) | voice01.generate_charon_english | er019:856 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回(技術失敗時のみminimal切替)、3回目直前に600秒cool-down(CS有効role)、尽きたらLR→HR。cascade尽き(UNCERTAIN)は即LR/HR | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | disfluency QA維持 | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | X-B1-01と同一関数 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-B1-04 | X(Active) | B1B(Advanced) | Full Story part1-3 | full_story_part1..3 | EN(Aoede) | er003_v1_sing01_news_tail_fix.py:generate_news_narration_wide_margin(L61,評価L186-212,LR L368) | er019:891 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回(技術失敗時のみminimal切替)、3回目直前に600秒cool-down(CS有効role)、尽きたらLR→HR。cascade尽き(UNCERTAIN)は即LR/HR+Repetition QA | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | Repetition QA(AND)維持。重複内容語はLRのlocality Gate | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | news_tail_fix L202のcascade呼出→adapter。LR再TTS計数 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-B1-05 | X(Active) | B1B(Advanced) | In One Line | in_one_line | EN(Aoede) | news_tail_fix.generate_news_narration_wide_margin | er019:891(name=in_one_line) | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回(技術失敗時のみminimal切替)、3回目直前に600秒cool-down(CS有効role)、尽きたらLR→HR。cascade尽き(UNCERTAIN)は即LR/HR | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | disfluency QA維持 | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | X-B1-04と同一関数 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-B1-06 | X(Active) | B1B(Advanced) | Key Phrase 英語 | kp{rank}_english | EN(Aoede) | er003_v1_repro01_main_generate.py:generate_key_phrase_component_verified(L761)→generate_narration_snippet_verified_strict(L196,評価L340-352) | er019:1026 (shared_narration.ensure_key_phrase_english_component=Master Store経由) | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用)+KP用asr_prompt(翻訳させない) | 非ラテン主体のPrimary不合格時のみAzure1回(enable_non_latin_cascade)+上記4段Cascade | MINIMAL2+ENGLISH_LOCK2=計4回(2026-09-01ユーザー正式決定)。LRなし。Master Store hit時はASR 0 | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | 学習対象英語を変更しない/Minimal Prompt/English Language Lock/LR対象外/Tier1・CS層非適用(明示除外) | KP既存例外(4回構成・Prompt切替・LRなし)を維持したまま判定のみ統一(Primary NG→Secondary 1回→WARNING採用)。3回仕様への一本化はUSER確認(競合一覧C-B) | repro01 L349のcascade→adapter(enable_non_latin_cascade維持)。Prompt切替構造は不変 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9)(Melos K2/ENGLISH_LOCKの既存KP転写含む) |
| X-B1-07 | X(Active) | B1B(Advanced) | Key Phrase 英語解説 | kp{rank}_explanation_en | EN(Aoede) | er019_family_x_audio_production_runner_01.py:generate_key_phrase_explanation_en_verified(L690)→repro01.generate_narration_snippet_verified_strict | er019:1059 | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用) | 非ラテン主体のPrimary不合格時のみAzure1回(enable_non_latin_cascade)+上記4段Cascade | max_attempts=2(L700)。text-gate status!=OKはTTS/ASR 0でSTOPPED | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | KP解説(Tier1/CS層/LR非適用)。text-gate STOPPED(0 API)維持 | 同上。ただしLRなし(3NG→HR)(attempt数は2のまま=競合C-B(ii)) | repro01評価点のadapter化のみ | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-B1-08 | X(Active) | B1B(Advanced) | KP phrase_repeat(末尾再掲) | kp{rank}_phrase_repeat | EN | (新規生成なし。en_rの複製) | er019:1081-1082 | (英語Phrase音声と同一wav/sha256) | (同左) | (なし) | (同左) | 複製のみ | N/A(KP英語の判定結果を継承。警告は元segmentの1件として登録、複製行は重複登録しない) | registry側で複製sha256を重複排除 | unit(registry重複排除) |
| X-B1-09 | X(Active) | B1B(Advanced) | 固定shell(Welcome/Preview intro/KP intro/Full story intro/Outro系) | welcome等(FIXED_SHARED) | EN(Charon) | er006_audio_cost_pilot_02_shared_narration.py:ensure_fixed_english_segment→voice01.generate_charon_english | er019:831(ensure_all_shared_narration_b1) | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | Master Store hitならTTS/ASR 0。未生成時のみ標準3回 | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | Master Store reuse(同一key再利用) | 判定は同一(生成時のみ適用)。reuse時は再判定なし(既存仕様) | 変更は共通adapterのみ。reuse経路無変更 | 既存Master hitでAPI0を確認(DefaultOff不要) |
| X-A2-01 | X(Active) | A2(Standard) | Topic intro | topic_intro | EN(Aoede) | er003_v1_crosslevel_audio_02_common.py:generate_english_segment_with_fallback(L79) | er019:1215 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry)。minimalはforce_secondary(Azure必須,L344-351) | 標準2+minimal1(minimalはforce_secondary=Azure必須)、cool-down、LR(minimal経由で再TTS)→HR | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | 5role(Tier1/CS/LR)。A2 6%減速非対象 | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR。minimal fallbackは内容NGの再試行から撤去(同一Prompt)→D-8(a) | crosslevel: 標準2+minimal1定数(PRODUCTION_STANDARD/MINIMAL)の再定義、_run_a2_minimal_fallback_attempt(L301-360)/LR _retts_fn(L392)の再TTSを標準Prompt経由へ、L348 cascade→adapter | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-A2-02 | X(Active) | A2(Standard) | Japanese title | japanese_title | JA(Aoede) | er003_v1_n3_01_tts_generate.py:generate_a2_japanese_with_reading_safety(L704)→generate_a2_japanese_with_fallback(L584,評価L647-660) | er019:1226 | OpenAI mini-transcribe→classify_ja_asr_match(+Variant層+Reading Resolver) | Primary=TRUE_CONTENT_MISMATCH時のみSCG(Azure1回、PASS=EXACT/NORMALIZEDのみ、除外=数字差/否定/類似度<0.4/C1/C2/否定マーカー/length NG)。entity-like UNCERTAINはCascade | 標準2+minimal1、JAにLRなし→STOPPED→HR Lock | protected_check_ja: _DIGIT_RE=\d+のみ(三人→四人を見逃し、二人↔2人で誤発火)。否定=_has_negation_ja+SCG推奨4マーカー | JA LRなし(機械流用不可)→HR | TTS①→Primary判定→NGなら[値差/否定差/否定マーカー差/C2/length NG=Secondaryなし]→Azure1回(sha256キャッシュ)→EXACT/NORMALIZED(値等価正規化後を含む)でPASS_WITH_WARNING+試聴リスト→両NGは再生成(最大3)→3NGでHR(LRなし) | n3_tts L651のja cascade→adapter。minimal撤去 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-A2-03 | X(Active) | A2(Standard) | Preview | preview | JA(Aoede) | n3_tts.generate_a2_japanese_with_reading_safety | er019:1244 | OpenAI mini-transcribe→classify_ja_asr_match(+Variant層+Reading Resolver) | Primary=TRUE_CONTENT_MISMATCH時のみSCG(Azure1回、PASS=EXACT/NORMALIZEDのみ、除外=数字差/否定/類似度<0.4/C1/C2/否定マーカー/length NG)。entity-like UNCERTAINはCascade | 標準2+minimal1、JAにLRなし→STOPPED→HR Lock | protected_check_ja: _DIGIT_RE=\d+のみ(三人→四人を見逃し、二人↔2人で誤発火)。否定=_has_negation_ja+SCG推奨4マーカー | JA LRなし | TTS①→Primary判定→NGなら[値差/否定差/否定マーカー差/C2/length NG=Secondaryなし]→Azure1回(sha256キャッシュ)→EXACT/NORMALIZED(値等価正規化後を含む)でPASS_WITH_WARNING+試聴リスト→両NGは再生成(最大3)→3NGでHR(LRなし) | 同上 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-A2-04 | X(Active) | A2(Standard) | Comment 1-4 | comment_1..4 | JA(Aoede) | n3_tts.generate_a2_japanese_with_reading_safety | er019:1244 | OpenAI mini-transcribe→classify_ja_asr_match(+Variant層+Reading Resolver) | Primary=TRUE_CONTENT_MISMATCH時のみSCG(Azure1回、PASS=EXACT/NORMALIZEDのみ、除外=数字差/否定/類似度<0.4/C1/C2/否定マーカー/length NG)。entity-like UNCERTAINはCascade | 標準2+minimal1、JAにLRなし→STOPPED→HR Lock | protected_check_ja: _DIGIT_RE=\d+のみ(三人→四人を見逃し、二人↔2人で誤発火)。否定=_has_negation_ja+SCG推奨4マーカー | JA LRなし | TTS①→Primary判定→NGなら[値差/否定差/否定マーカー差/C2/length NG=Secondaryなし]→Azure1回(sha256キャッシュ)→EXACT/NORMALIZED(値等価正規化後を含む)でPASS_WITH_WARNING+試聴リスト→両NGは再生成(最大3)→3NGでHR(LRなし) | 同上 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-A2-05 | X(Active) | A2(Standard) | Full Story part1-3 | full_story_part1..3 | EN(Aoede,6%減速) | n3_tts.generate_a2_segment_with_slowdown(L283)→c.generate_english_segment_with_fallback+apply_a2_slowdown_postprocess(L172-282) | er019:1268 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1)。減速後は classify+homophone+post_slowdown_cascade_rescue(UNCERTAINのみ) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 内側3回+減速後再検証、外側最大3(05Aで通算TTS 3に共有) | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | A2 6%減速(2026-08 ER-008承認): 減速後ASR再検証必須。original.wav保持 | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR。減速前後ともunified_judge。外側ループは通算3回(B0案)。減速後の最終音声をWARNING登録 | n3_tts L186-196(post-slowdown classify)/L146(cascade rescue)→unified_judge(同一関数)。B0/B'選択はOpus論点 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-A2-06 | X(Active) | A2(Standard) | In One Line | in_one_line | EN(Aoede,6%減速) | n3_tts.generate_a2_segment_with_slowdown | er019:1268 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 同X-A2-05 | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | A2 6%減速+disfluency QA | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | X-A2-05と同一関数 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-A2-07 | X(Active) | A2(Standard) | Key Phrase 英語 | kp{rank}_english | EN(Aoede) | repro01.generate_key_phrase_component_verified | er019:1339 | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用) | 非ラテン主体のPrimary不合格時のみAzure1回(enable_non_latin_cascade)+上記4段Cascade | 計4回 | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | KP既存例外維持 | X-B1-06と同じ | 同X-B1-06 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-A2-08 | X(Active) | A2(Standard) | Key Phrase 日本語意味 | meaning_{i} | JA(Aoede) | n3_tts.generate_a2_japanese_with_reading_safety | er019:1347 | OpenAI mini-transcribe→classify_ja_asr_match(+Variant層+Reading Resolver) | Primary=TRUE_CONTENT_MISMATCH時のみSCG(Azure1回、PASS=EXACT/NORMALIZEDのみ、除外=数字差/否定/類似度<0.4/C1/C2/否定マーカー/length NG)。entity-like UNCERTAINはCascade | 標準2+minimal1、JAにLRなし→STOPPED→HR Lock | protected_check_ja: _DIGIT_RE=\d+のみ(三人→四人を見逃し、二人↔2人で誤発火)。否定=_has_negation_ja+SCG推奨4マーカー | known_key_phrase_terms維持。JA LRなし | TTS①→Primary判定→NGなら[値差/否定差/否定マーカー差/C2/length NG=Secondaryなし]→Azure1回(sha256キャッシュ)→EXACT/NORMALIZED(値等価正規化後を含む)でPASS_WITH_WARNING+試聴リスト→両NGは再生成(最大3)→3NGでHR(LRなし) | X-A2-02と同一関数 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| X-A2-09 | X(Active) | A2(Standard) | 固定shell(EN/JA) | welcome等+point_explanation(A2のみ日本語) | EN/JA | shared_narration.ensure_fixed_english_segment / ensure_fixed_japanese_segment(→voice01.generate_charon_japanese max_attempts=6→3クランプ) | er019:1204(ensure_all_shared_narration_a2) | EN/JA各P | EN/JA各S | Master Store hitならAPI0 | 同上 | Master Store reuse | 判定は同一(生成時のみ) | 共通adapterのみ | 既存Master hitでAPI0 |
| Z-B1-01 | Z(Active) | B1B(Advanced) | Narrator Full Story clip | full_story_part{n}_c{k} | EN(Aoede) | news_tail_fix.generate_news_narration_wide_margin | er063_family_z_audio_01.py:624(real_generators.narrator) | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1)(role=FULL_STORY[_FAMILY_Z_STORY_CLIP_PATTERN]) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回(技術失敗時のみminimal切替)、3回目直前に600秒cool-down(CS有効role)、尽きたらLR→HR。cascade尽き(UNCERTAIN)は即LR/HR+Repetition QA | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | Z固有Style(N01)。固有名詞Melos=M1対象 | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | wide_margin共通adapter | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9)。Melos said. 12/12・M1 21観測はer077 evidence_01/clip_results.jsonの保存転写で再判定(API0) |
| Z-A2-01 | Z(Active) | A2(Standard) | Narrator Full Story clip | full_story_part{n}_c{k} | EN(Aoede,6%) | n3_tts.generate_a2_segment_with_slowdown | er063:628 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | X-A2-05同 | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | 6%減速+Z Style(N01、PD8_A2SLOW撤去済み) | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | X-A2-05と同一 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| Z-B1-02 | Z(Active) | B1B(Advanced) | Dialogue(複数Voice) | full_story_part{n}_c{k}(speaker別voice) | EN(per-speaker) | er012_b_family_voices_production_01.py:generate_voice_body_wide_margin(L479,評価L546-560) | er063:642(dialogue) | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用)(segment_id未渡し) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回(失敗時minimal fallbackへ切替L537)。CS層default True。LRなし | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | 話者区分(speaker→voice)・既存Segment構造維持。Dialogue独自LRなし | 同上。ただしLRなし(3NG→HR)(話者境界は不変) | bvoices L549のcascade→adapter。segment_id渡し(role gate)の有無は§6 C-G | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| Z-A2-02 | Z(Active) | A2(Standard) | Dialogue(複数Voice) | full_story_part{n}_c{k} | EN(per-speaker,6%) | bvoices.generate_voice_body_wide_margin + n3_tts.apply_a2_slowdown_postprocess(L172) | er063:636-640 | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回→減速→減速後再検証1回のみ(外側ループなし=不整合) | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | A2 6%減速+Voice A/B Std Style | 同上。ただしLRなし(3NG→HR)。減速後NGも通算3回の枠で再生成されるよう外側ループ汎化(generate_a2_segment_with_slowdownにgen_fn引数) | er063 dialogue(std)にouter loop適用。apply_a2_slowdown_postprocessのunified_judge化 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9)(mock) |
| Z-B1-03 | Z(Active) | B1B(Advanced) | Topic intro / Preview / Comment | topic_intro/preview/comment_k | EN(Charon/Aoede) | voice01.generate_charon_english | er063:645(charon_en) | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回(技術失敗時のみminimal切替)、3回目直前に600秒cool-down(CS有効role)、尽きたらLR→HR。cascade尽き(UNCERTAIN)は即LR/HR | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | Z固有Style(E1/E2_UPBEAT/X_TOPIC_INTRO) | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | X-B1-01同 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| Z-A2-03 | Z(Active) | A2(Standard) | Topic intro | topic_intro | EN(Aoede) | crosslevel.generate_english_segment_with_fallback | er063:654 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準2+minimal1(minimalはforce_secondary=Azure必須)、cool-down、LR(minimal経由で再TTS)→HR | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | 5role | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | X-A2-01同 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| Z-A2-04 | Z(Active) | A2(Standard) | Preview / Comment / Japanese title | preview/comment_k/japanese_title | JA(Aoede) | n3_tts.generate_a2_japanese_with_reading_safety | er063:660(ja_simple) | OpenAI mini-transcribe→classify_ja_asr_match(+Variant層+Reading Resolver) | Primary=TRUE_CONTENT_MISMATCH時のみSCG(Azure1回、PASS=EXACT/NORMALIZEDのみ、除外=数字差/否定/類似度<0.4/C1/C2/否定マーカー/length NG)。entity-like UNCERTAINはCascade | 標準2+minimal1、JAにLRなし→STOPPED→HR Lock | protected_check_ja: _DIGIT_RE=\d+のみ(三人→四人を見逃し、二人↔2人で誤発火)。否定=_has_negation_ja+SCG推奨4マーカー | JA LRなし。Z固有Style R2/J3 | TTS①→Primary判定→NGなら[値差/否定差/否定マーカー差/C2/length NG=Secondaryなし]→Azure1回(sha256キャッシュ)→EXACT/NORMALIZED(値等価正規化後を含む)でPASS_WITH_WARNING+試聴リスト→両NGは再生成(最大3)→3NGでHR(LRなし) | X-A2-02同 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| Z-ALL-01 | Z(Active) | B1B/A2 | Key Phrase 英語 | kp{rank}_en | EN(Aoede) | repro01.generate_narration_snippet_verified_strict(K2 primary2+ENGLISH_LOCK2) | er063:669-683(kp_en) | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用) | 非ラテン主体のPrimary不合格時のみAzure1回(enable_non_latin_cascade)+上記4段Cascade | 計4回 | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | KP既存例外維持(K2 Style/ENGLISH_LOCK) | X-B1-06同 | 同 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| Z-ALL-02 | Z(Active) | B1B | Key Phrase 英語解説 | kp{rank}_explanation_en | EN | er019.generate_key_phrase_explanation_en_verified | er063:688(kp_expl_en) | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用) | 非ラテン主体のPrimary不合格時のみAzure1回(enable_non_latin_cascade)+上記4段Cascade | max_attempts=2 | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | KP既存例外 | X-B1-07同 | 同 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| Z-A2-05 | Z(Active) | A2(Standard) | Key Phrase 日本語意味 | meaning_{i} | JA(Aoede) | n3_tts.generate_a2_japanese_with_reading_safety | er063:692(kp_ja) | OpenAI mini-transcribe→classify_ja_asr_match(+Variant層+Reading Resolver) | Primary=TRUE_CONTENT_MISMATCH時のみSCG(Azure1回、PASS=EXACT/NORMALIZEDのみ、除外=数字差/否定/類似度<0.4/C1/C2/否定マーカー/length NG)。entity-like UNCERTAINはCascade | 標準2+minimal1、JAにLRなし→STOPPED→HR Lock | protected_check_ja: _DIGIT_RE=\d+のみ(三人→四人を見逃し、二人↔2人で誤発火)。否定=_has_negation_ja+SCG推奨4マーカー | M2 Style。known_key_phrase_terms | TTS①→Primary判定→NGなら[値差/否定差/否定マーカー差/C2/length NG=Secondaryなし]→Azure1回(sha256キャッシュ)→EXACT/NORMALIZED(値等価正規化後を含む)でPASS_WITH_WARNING+試聴リスト→両NGは再生成(最大3)→3NGでHR(LRなし) | X-A2-08同 | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| Z-ALL-03 | Z(Active) | B1B/A2 | SHELL(固定共有資産) | welcome等 | EN/JA | (copy。Master Store書込なし) | er063 SHELL=copy | N/A | N/A | N/A | N/A | 既存Master/共有資産の読取コピーのみ | N/A(生成/判定なし) | なし | 不要 |
| Y-00 | Y(Active名目・実装なし) | - | (Production TTS経路なし) | - | - | (未実装) | - | - | - | - | - | CURRENT_SPEC L1543-1553: 着手済み実装なし・新規開発しない | N/A(将来のY実装は共有leaf経由で自動適用) | なし | 不要 |
| A-B1-01 | A(Legacy) | B1 | Topic intro/Preview/Comment1-4 | topic_intro/preview/comment_k | EN(Charon) | voice01.generate_charon_english | er003_v1_n3_01_tts_generate.py:981,996 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回(技術失敗時のみminimal切替)、3回目直前に600秒cool-down(CS有効role)、尽きたらLR→HR。cascade尽き(UNCERTAIN)は即LR/HR | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | legacy(Family A/B/C)は専用変更なし・共有moduleの変更が自動波及(CURRENT_SPEC L1565)。Regression対象として更新しない(L1558) | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | X-B1-01の共有関数で自動適用 | Integration(mock)のみ(新規実音声なし) |
| A-B1-02 | A(Legacy) | B1 | Point見出し(point_one_heading/point_two_heading) | point_one_heading,point_two_heading | EN(Aoede) | er003_v1_sing01_point_headings_aoede.py:generate(L60-130,評価L121-135) | n3_tts:1016 | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用) | cascadeのみ(force_secondaryなし) | 標準1+minimal2(minimal_after=max(1,3//2)=1)。LRなし。見出しはPrimary PASSでSecondary確認されない | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | legacy(Family A/B/C)は専用変更なし・共有moduleの変更が自動波及(CURRENT_SPEC L1565)。Regression対象として更新しない(L1558)。見出し/短文の独立QA(disfluency)維持 | 同上。ただしLRなし(3NG→HR)。minimal2→同一Prompt(OPEN-288 D-5)。見出しの追加保護は競合C-D(a) | point_headings L126のcascade→adapter。minimal切替(L77-100)の撤去/整理 | Integration(mock)+見出し既存転写 |
| A-B1-03 | A(Legacy) | B1 | Point one/two・Full Story・In One Line | point_one,point_two,full_story_part1..,in_one_line | EN(Aoede) | news_tail_fix.generate_news_narration_wide_margin | n3_tts:1032 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回(技術失敗時のみminimal切替)、3回目直前に600秒cool-down(CS有効role)、尽きたらLR→HR。cascade尽き(UNCERTAIN)は即LR/HR | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | legacy(Family A/B/C)は専用変更なし・共有moduleの変更が自動波及(CURRENT_SPEC L1565)。Regression対象として更新しない(L1558) | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | X-B1-04同 | Integration(mock) |
| A-B1-04 | A(Legacy) | B1 | Key Phrase 英語/日本語 | kp{rank}_english/kp{rank}_japanese | EN+JA | ensure_key_phrase_english_component(n3_tts:1064)/generate_charon_japanese_with_reading_safety(L420,n3_tts:1073→voice01.generate_charon_japanese L434-580) | n3_tts:1064,1073 | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用) / OpenAI mini-transcribe→classify_ja_asr_match(+Variant層+Reading Resolver) | 非ラテン主体のPrimary不合格時のみAzure1回(enable_non_latin_cascade)+上記4段Cascade / Primary=TRUE_CONTENT_MISMATCH時のみSCG(Azure1回、PASS=EXACT/NORMALIZEDのみ、除外=数字差/否定/類似度<0.4/C1/C2/否定マーカー/length NG)。entity-like UNCERTAINはCascade | EN計4回 / JA標準2+minimal1 | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS / protected_check_ja: _DIGIT_RE=\d+のみ(三人→四人を見逃し、二人↔2人で誤発火)。否定=_has_negation_ja+SCG推奨4マーカー | legacy(Family A/B/C)は専用変更なし・共有moduleの変更が自動波及(CURRENT_SPEC L1565)。Regression対象として更新しない(L1558)。KP既存例外維持 | EN:X-B1-06 / JA:X-A2-08同 | 同上 | Integration(mock) |
| A-A2-01 | A(Legacy) | A2 | Topic intro / Japanese title / Preview / Comment1-4 | topic_intro,japanese_title,preview,comment_k | EN+JA | crosslevel.generate_english_segment_with_fallback / n3_tts.generate_a2_japanese_with_reading_safety | n3_tts:1133,1142,1149 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) / OpenAI mini-transcribe→classify_ja_asr_match(+Variant層+Reading Resolver) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) / Primary=TRUE_CONTENT_MISMATCH時のみSCG(Azure1回、PASS=EXACT/NORMALIZEDのみ、除外=数字差/否定/類似度<0.4/C1/C2/否定マーカー/length NG)。entity-like UNCERTAINはCascade | 標準2+minimal1(minimalはforce_secondary=Azure必須)、cool-down、LR(minimal経由で再TTS)→HR / 標準2+minimal1、JAにLRなし→STOPPED→HR Lock | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS / protected_check_ja: _DIGIT_RE=\d+のみ(三人→四人を見逃し、二人↔2人で誤発火)。否定=_has_negation_ja+SCG推奨4マーカー | legacy(Family A/B/C)は専用変更なし・共有moduleの変更が自動波及(CURRENT_SPEC L1565)。Regression対象として更新しない(L1558) | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR / TTS①→Primary判定→NGなら[値差/否定差/否定マーカー差/C2/length NG=Secondaryなし]→Azure1回(sha256キャッシュ)→EXACT/NORMALIZED(値等価正規化後を含む)でPASS_WITH_WARNING+試聴リスト→両NGは再生成(最大3)→3NGでHR(LRなし) | X-A2-01/02同 | Integration(mock) |
| A-A2-02 | A(Legacy) | A2 | Point見出し/Point one-two/Full Story/In One Line(6%減速) | point_*_heading,point_one,point_two,full_story_part1..,in_one_line | EN(Aoede,6%) | n3_tts.generate_a2_segment_with_slowdown | n3_tts:1160,1177 | OpenAI mini-transcribe→classify_asr_match(+Tier1[5role]+B1 CS+Eq層[CSflag]+F1+M1) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | X-A2-05同 | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | legacy(Family A/B/C)は専用変更なし・共有moduleの変更が自動波及(CURRENT_SPEC L1565)。Regression対象として更新しない(L1558)。A2_SLOWDOWN_TARGET_SEGMENTS(L111) | TTS①→Primary判定(既存全層)→NGなら[値差/否定差=保護差なら再生成、Secondaryなし]→Azure1回(sha256キャッシュ、PhraseListなし)→Secondary PASSでPASS_WITH_WARNING採用+試聴リスト登録→両NGは同一Prompt/Voice/速度で再生成(最大3)→3NGでLR(合意誤読のみ、Fact/局所性Gate)またはHR | X-A2-05同 | Integration(mock) |
| A-A2-03 | A(Legacy) | A2 | Key Phrase 英語/日本語意味 | kp{rank}_english,kp{rank}_japanese_meaning | EN+JA | ensure_key_phrase_english_component / generate_a2_japanese_with_reading_safety | n3_tts:1211,1219 | 同上 | 同上 | 同上 | 同上 | legacy(Family A/B/C)は専用変更なし・共有moduleの変更が自動波及(CURRENT_SPEC L1565)。Regression対象として更新しない(L1558) | 同上 | 同上 | Integration(mock) |
| B-B1-01 | B(Legacy,Voices) | B1 | Voice A/B(/C)本文・Narrator | voice_a/voice_b/voice_c body等 | EN(per-speaker) | er012_b_family_voices_production_01.py:generate_voice_body_wide_margin + run_tts_3v(L829) | er012_b_family_voices_production_01.py:run_tts_3v | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回 | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | legacy(Family A/B/C)は専用変更なし・共有moduleの変更が自動波及(CURRENT_SPEC L1565)。Regression対象として更新しない(L1558)。話者区分維持 | 同上。ただしLRなし(3NG→HR) | bvoices共有adapter(Z-B1-02同) | Integration(mock) |
| B-A2-01 | B(Legacy,Voices) | A2 | Voice本文・Narrator見出し・Hook/Tension/Closing(6%減速) | voice本文等 | EN(per-speaker,6%) | er012_b_family_voices_a2_production_01.py:generate_voice_body_wide_margin_with_a2_slowdown(L696)/generate_narrator_heading_with_a2_slowdown(L738)/generate_narration_wide_margin_with_a2_slowdown(L744) | er012_b_family_production_runner_01.py(a2prod) | OpenAI mini-transcribe→classify_asr_match(+F1+M1。segment_id未渡しでTier1/role gate非適用) | entity-like/homophone候補のみ4段Cascade(Primary#2→Azure[PhraseList]x2)+Tier3/CS層Azure。数値/否定/通常内容語差は対象外(blind TTS retry) | 標準3回→減速→再検証1回のみ(外側ループなし) | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | legacy(Family A/B/C)は専用変更なし・共有moduleの変更が自動波及(CURRENT_SPEC L1565)。Regression対象として更新しない(L1558)。B-Family Voices A2 6%(CURRENT_SPEC B-Family節) | 同上。ただしLRなし(3NG→HR)+外側ループ汎化(Z-A2-02同) | a2_production wrapper→汎化loop | Integration(mock) |
| C-01 | C(Legacy,Future Story) | A2(B1相当含む) | Comment1-3(JA)・Narrator(strict)・charon_english・voice本文 | comment_k,narrator | JA+EN | er013_family_c_production_01.py:generate_family_c_a2_comment(L460)+repro01.generate_narration_snippet_verified_strict+voice01.generate_charon_english+bvoices.generate_voice_body_wide_margin | er013_family_c_production_runner_01.py:246,367 | 共有leaf経由(上記各行と同一) | 同左 | 同左 | 同左 | legacy(Family A/B/C)は専用変更なし・共有moduleの変更が自動波及(CURRENT_SPEC L1565)。Regression対象として更新しない(L1558) | 共有leaf経由で自動適用 | 共有leafの変更のみ | Integration(mock) |
| XC-01 | 全Family | 全level | A2 6%減速後 post-slowdown 再検証(共通) | A2_SLOWDOWN_TARGET_SEGMENTS等 | EN | n3_tts.apply_a2_slowdown_postprocess(L172-282)+_post_slowdown_cascade_rescue(L120-170) | n3_tts L186-196, L146 | classify_asr_match(segment_id=name)+homophone | UNCERTAIN時のみ共有Cascade | 外側ループ最大3(通算TTS 3共有、05A) | protected_check: _is_number=isdigit()のみ(N%/$/小数/指数=別tokenで25%→26%を数値差と認識しない穴)。否定=_NEGATION_WORDS | A2 6%減速 | unified_judge同一関数(Primary→Secondary→WARNING) | apply_a2_slowdown_postprocess内の再検証をunified_judgeへ | 既存音声/既存転写の再判定(API0)+Integration(mock engine)+実API最小runtime(DESIGN §9) |
| XC-02 | 全Family | EN Full Story等5role | Local Rewrite回復(EN) | 5role | EN | er020_tts_retry_local_rewrite_01.py:run_local_rewrite_recovery(L686)/resolve_narrative_role(L124) | voice01 L359 / news_tail_fix L368 / crosslevel L411 | (再TTS後は各leafの評価) | (同左) | LR 1回/segment。再TTSは標準leaf(max_attempts=1)またはminimal(crosslevel)。再TTS回数は未計数(Coffee記録4/実際5) | (同左) | NON_APPLICABLE=見出し/KP。JA未対応 | 発火条件を『両エンジン合意誤読のみ』に絞る(案)。再TTS=統一judge+累積計数に加算。LR後v1はPrimary PASSでもSecondary確認(force_secondary維持) | retts計数をrecord_outcomeへ | mock+既存LR実例(Coffee/Melos) |
| XC-03 | 全Family | 全level | Human Review Lock/累積ガード | 全segment | EN/JA | er011_human_review_lock_01.py:check_before_generation(L297)/record_outcome(L355)、MAX_CUMULATIVE_TTS_ATTEMPTS=15/ASR=60(L68-69) | 各leaf @guarded_generate | - | - | - | - | 承認・解除は回避しない | 不変(WARNINGはHR queueへ入れない/別リスト) | ASR呼出計数にSecondary 1回を反映 | 既存test+Integration |

---

## 4. 統一判定の設計

### 4-1. モジュール構成(新規3+監査test1。既存2関数をadapter化)

| 区分 | ファイル(新規は`er078_`、prefix未使用を確認) | 役割 |
|---|---|---|
| 新規 | `er078_asr_value_guard_01.py` | 値と単位の比較(EN/JA)。`extract_values(text, lang)`、`compare_values(canonical, other, lang) -> ValueVerdict`、`normalize_values_for_diff(c, a, lang)`。Primary判定内(`protected_check*`)と最終ANDゲートの**両方**から呼ぶ唯一の数値比較実装 |
| 新規 | `er078_asr_unified_judge_01.py` | `judge_audio(...)`(状態機械)、`SecondaryCache`、`JudgeResult`。Role別の重複実装を持たない |
| 新規 | `er078_pass_with_warning_registry_01.py` | WARNING試聴リスト生成(`collect_warnings`/`write_listening_list`/`render_html_section`) |
| 新規(test) | `er078_asr_unified_wiring_static_audit_01.py` | 判定点11箇所が統一judgeを経由することのAST検査(Gate 4) |
| adapter化 | `er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`(L535-981)/`evaluate_attempt_with_cascade`(L417) | 署名維持。内部で`judge_audio`へ委譲。返り値タプル`(verified, stop_retrying, classification)`と`detail_out`は後方互換 |
| adapter化 | `er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail`(L383-)/`evaluate_attempt_ja_with_cascade`(L516) | 同上 |

**adapter方式を推奨する理由**: ASR判定の呼出点11箇所のうち、`evaluate_attempt_*`の呼出署名(約50ファイルの旧呼出元を含む)を変えずに済む。呼出側(leaf)の変更は「attempt文脈(slot番号・script版・is_last_slot)の受渡し」と「`asr_judgement`のattempts_logへの追記」「cascade由来`stop_retrying`によるHR直行の撤去」に限定できる(§7)。代替案(11箇所へ個別にinline実装)は重複実装になり§7-1「Role別の重複実装を避ける」に反するため不採用。

### 4-2. 入出力(擬似署名。実装は委任_02)

```text
judge_audio(*, role: str|None, lang: 'en'|'ja', canonical_text: str, wav_path: str,
            primary_text: str|None, primary_cls: ClassificationResult,   # 既存Primary側層を通した結果
            attempt_ctx: AttemptCtx,        # segment_key, script_version('v0'|'v1'), slot(1..3), is_last_slot, length_ok
            cache: SecondaryCache, expected_readings=None, ledger_phrases=None,
            force_secondary: bool=False)   # LR後v1のみTrue(既存force_secondary保護の継続)
  -> JudgeResult(
       state: 'PASS'|'PASS_WITH_WARNING'|'NG_PROTECTED'|'NG_EXCLUDED'|'NG_BOTH'|'NG_SECONDARY_UNAVAILABLE'|'NG_PRIMARY_ASR_FAILURE',
       verified: bool, reason_code: str, classification: <旧互換ClassificationResult>,
       warnings: list[Warning], primary: dict, secondary: dict, value_guard: dict, negation_guard: dict,
       cost: {asr_calls, azure_seconds, est_jpy}, timing: {...}, human_review_required: bool)
```
`verified`は旧`verified_content`相当(leaf側でlength/disfluency/repetition QAをANDする既存構造は不変)。`stop_retrying`はadapterが`False`固定で返す(`should_stop_retrying`の同一signature×3打切りは通算3回上限と重なるため実質無効、関数自体は維持)。

### 4-3. 状態機械(role・言語共通。1音声=1 attemptごと)

```text
[leaf] TTS(slot k=1..3, 同一原稿/Prompt/model/voice/速度)
   │ 技術失敗(400/空応答/発話区間検出失敗/異常長) ── 現行どおりattempt消費 → 次slot(§6 C-D(15))
   ▼
[leaf] Safety QA 前段(symbol gate, 異常長)             ※ disfluency/repetition/lengthは既存どおり最後にAND
   ▼
Primary ASR (OpenAI)  ── 取得失敗(None) → NG_PRIMARY_ASR_FAILURE(現行TTS_FAILURE分類のまま次slot)
   ▼
P-chain(既存層を現行順で全て): Tier1[5role] → baseline classify → contraction → B1 CS(+F1) → Eq層[CS flag]
        → Tier3 → CMU Case A/homophone → M1(凍結候補)       ※Eq層/Tier3のAzure補強は共有SecondaryCacheを使用(重複呼出なし)
   │
   ├─ Primary PASS ──► 最終ANDゲート(§4-3b) ──► PASS または PASS_WITH_WARNING(警告ラベルの場合)   [Secondaryなし]
   │
   └─ Primary NG
        ├─ (P1) 保護差あり: 値DIFF/値AMBIGUOUS(未解決)/否定差/JA否定マーカー差 ─► NG_PROTECTED  [Secondary不呼出、次slot]
        ├─ (P2) 除外表に該当(JA: C2同形異音候補、length NG ※C1/類似度<0.4は§6 C-A5)         ─► NG_EXCLUDED  [Secondary不呼出、次slot]
        └─ (P3) 上記以外 ─► Secondary(Azure) 1回 [SecondaryCache: wav sha256+lang+phrase_hash]
              ├─ 取得不能(None/例外/空/timeout、ASR API再試行≤1後) ─► NG_SECONDARY_UNAVAILABLE [PASS不可。次slot。同一segmentで2回続いたらHR_TECHで残slot打切り]
              ├─ Secondary転写に保護差(値DIFF/否定) ─► NG_BOTH [次slot]
              ├─ Secondary PASS(言語別許容集合・§4-3c) かつ 最終ANDゲートOK ─► PASS_WITH_WARNING(secondary_confirmed)
              └─ それ以外 ─► NG_BOTH [次slot]
slot k==3 で NG:  EN → LR gate(§4-7) / JA・KP・見出し・Dialogue・LR不成立 → STOPPED → HR Lock(既存 record_outcome)
```

**(4-3b) 最終ANDゲート**: 採用しようとする転写(Primary/Secondary/M1・Tier3等の根拠転写すべて)に対し、`value_guard.compare_values(canonical, text)`が`DIFF`でないこと、かつ否定ガードが差を示さないことを**独立に再確認**する。層(Tier1/Eq層/M1/Tier3/SCG)のどこが緩んでも、値・否定の重大差はここで止まる(多重防御)。ゲートNGの場合は`NG_PROTECTED`(警告にも解放しない、原文§3末尾)。

**(4-3c) Secondary PASS許容集合**(§6 C-I): 言語別の既存承認集合を維持する。JA=`EXACT_MATCH/NORMALIZED_MATCH`のみ(2026-10-11承認、`er007_ja_secondary_asr_01.py:83`。**値等価正規化後の一致も`NORMALIZED_MATCH`相当として含む**)。EN=Primaryと同じ分類器で**Secondary転写**を判定し`should_pass`となるもの(`EXACT/NORMALIZED/TRANSCRIPT_STYLE_NORMALIZED/NUMERIC_EQUIVALENCE/HIGH_SIMILARITY_SAFE`+CMU Case A+M1(Secondary転写)。現行Cascade L876-948が受理していた集合を超えない)。PHONETIC一括許容は採用しない(V04 L126)。

**(4-3d) 現行との差分(重要)**:
- 数値・否定・通常内容語差で`cascade_eligible=False`だったEN経路(L812)は、通常内容語差のみSecondary対象に**拡大**、数値/否定の保護差は従来どおり対象外(=安全側不変)。
- EN Cascade尽き(4段全NG)で`stop_retrying=True`+HR直行(L947-949)は**撤去**し、次slotへ(両NG→再生成)。
- `ASR_VALIDATION_UNCERTAIN`でのLR発火(`crosslevel` L247-262)は、§4-7の「合意誤読のみ」へ絞る。

### 4-4. Secondary障害時の処理(原文「PASS扱いせず、既存の安全な障害処理へ進む」)
現行は言語間で不整合(JA=再生成、EN=Cascade継続→HR)。統一: **PASS不可**・次slot(attempt消費)・`secondary_unavailable=true`を記録。TTS無駄打ち防止として、**同一segmentでSecondary取得不能が2回続いたら残slotを使わずHR_TECH**(現行EN「cascade尽き→HR直行」の安全側の精神を維持)。Secondary障害を含むNGは**LR発火の根拠にしない**(インフラ障害で原稿を書換えない)。

### 4-5. Secondary重複呼出防止
- `SecondaryCache`キー=`(sha256(wav bytes), engine, lang, phrase_list_hash)`。EN=Azure(現行どおりLedger PhraseList。`get_full_text_via_azure_stt_with_phrase_list`)、JA=Azure(`_azure_stt_strict`、Phrase Listなし)を**それぞれ既存関数のまま**キャッシュ経由で1回化。
- 現状EN最大6箇所(`er006_secondary_asr_01.py:405` CS Eq層/`:700` Tier3/`:760` 非ラテン/`:784` forced/`:876` S#1/`:914` S#2)とJA(`_run_scg_secondary_confirm` L302、Cascade Azure#1/#2)を**全て`SecondaryCache.get`経由**にする。Primary#2(同一音声のOpenAI再転写)とS#2は廃止(統一フローはPrimary 1回+Secondary 1回)。
- 検証: mock Azureでtier3+Eq層+非ラテン+forcedを全て発火させる入力でもcall_count==1(§8)。ASR呼出数(`asr_calls_this_call`)はSecondary 1回を計上し累積上限60に反映。
- 再生成(新しいwav)はsha256が変わるため別音声として扱う(重複ではない)。A2減速前後も別wav。

### 4-6. 監査recordと試聴リスト
**監査record**(既存`attempts_log`/`tts_generation_results.json`/`attempt_history.jsonl`へ**additive**。新ファイル形式は作らない): 
`asr_judgement = {state, reason_code, slot, script_version, audio_sha256, primary:{engine,model,text,classification,labels[]}, secondary:{called,cached,engine,text,classification,error,unavailable}, value_guard:{verdict,canon_atoms,asr_atoms}, negation_guard:{...}, warnings:[{type,detail}], cost:{openai_asr_calls,azure_calls,azure_seconds,est_jpy}, timing:{primary_s,secondary_s,total_s}}`。`build_attempts_detail`(`er011_human_review_lock_01.py:212`)へ`asr_judgement`を追加、`append_attempt_history_event`(L237)で`ASR_JUDGEMENT`イベントを1行記録。

**WARNINGの種類**(試聴リストの`warning_type`): `SECONDARY_CONFIRMED`(Primary NG・Secondary PASS)、`CONNECTED_SPEECH`/`CS_EQUIVALENCE`、`M1_MULTI_CANDIDATE`、`SECONDARY_CORROBORATED`(Tier3)、`JA_NUMERIC_IRREGULAR_READING`(値同値だが不規則読みを含む、V04/er066 `is_irregular_sig`)、`NUMERIC_AMBIGUOUS_SURFACE`(「十分」等の曖昧表層でSecondaryがEXACT)、`LR_REWRITTEN`(LR後v1=原稿が変わった音声)。過去実績ベースの件数見込み(attempt_history):SECONDARY_CORROBORATED 39件、CS 3件、M1 1件、SCG 1件=過去全run合計で約44件(1記事あたり少数)。

**試聴リスト**:
- 出力: `<level_out_dir>/audit/pass_with_warning_listening_list.json`(`tts_generation_results.json`と同階層)を、TTS stage終了時とページ生成時に**`tts_generation_results.json`から再導出**(別store・二重管理なし。冪等)。1行= `{segment_id, level, label, canonical_text, adopted_wav, adopted_sha256, original_wav(減速前)、primary_text, secondary_text, warning_type, reason, slot, script_version, rewrite_diff(LRのみ), cost}`。KP phrase_repeatのような複製行はsha256で重複排除。
- 採用音声との一致: リストの`adopted_sha256`が最終Assembly入力wavのsha256と一致することをregistryが検査(A2は減速後wav)。
- ページ連動(事後試聴): X=`er019_family_x_audio_production_runner_01.py:2092 build_player_html`、Z=`er063_family_z_audio_01.py:1312 build_listening_page_html`(+`er026 stage_pages`)に「WARNING音声 試聴リスト(自動採用・事後確認用)」節を追加。**legacy A/B/CのページはJSONのみ生成(ページ更新なし)**(§6 C-F)。
- **非ブロッキング**: Assembly Gate(`verify_episode_audio_validation_gate`)・公開可否は変えない。HR queue(`human_review_queue.jsonl`)にはWARNINGを入れない(PASS扱いのため)。ユーザー事前承認は求めない(原文§2)。
- Master Store reuse(KP英語・固定shell): 再利用音声が元のWARNINGを持つ場合に備え、`store.get_or_generate`のmanifest entryへ`asr_judgement`をadditiveに保存し、reuse時にresult dictへ復元する(要確認事項: 現行manifestのスキーマ、`er006_output/master_audio_store_01/manifest.json`)。

### 4-7. Local Rewrite・Human Reviewの統合
- **発火条件(EN、全て必須)**: ①slot 3 NG(または保護差でない) ②role∈5 role(既存`connected_speech_enabled_for`) ③`lr_used==0` ④3回のNGにSecondary障害を含まない ⑤**両エンジン合意誤読**: Primary転写とSecondary転写の、canonicalに対する差分spanが同一(`identify_ng_span`(`er020:180`)の`canonical_changed_words`が一致)。エンジンごとに異なる転写(例: Mello/Mallow)はASR不安定と推定してLRせずHR(原文§6「ASR誤認と推定される場合は書き換えない」、V04 D-9(b)/R3)。⑥既存7 Gate(局所性・全文性・数値保存・Fact等)を通過。
- **JA・KP・見出し・Dialogue**: LRなし、3NG→HR(原文§5-2, 6-2, 6-3)。
- **LR後v1**: 再TTS=標準Prompt(minimal不使用)・**1 attempt**(現行`max_attempts=1`維持)。判定は統一judge+`force_secondary=True`(LR後v1はPrimary PASSでもSecondary確認=既存保護の継続、V04 2-7(A)、D-5)。PASS時は`LR_REWRITTEN`として必ずPASS_WITH_WARNING。v1がNGならHR(2回目LR禁止)。
- **計数**: `tts_attempts_v1`(LR再TTS)を`review_lock.record_outcome`の`tts_attempts_this_call`/`cumulative_tts_attempts`へ加算(現状は未計数、D-17)。LR LLM呼出もcost loggerに従う。通算上限(15/60)超過は既存の`budget_guard_triggered`でHR。
- **HR Lockは不変**: `check_before_generation`(L297)・承認・`REGENERATE_APPROVED`を回避しない。HR queue entry(`_log_human_review`)は**最終slotのNG時のみ**(adapterが`attempt_ctx.is_last_slot`で判定)書く。

### 4-8. A2 6%減速との整合(§6 C-L)
- **B0案(本設計の推奨・第1段)**: 現行構造(内側=減速前判定、`apply_a2_slowdown_postprocess`=減速後判定、外側最大3・通算TTS 3共有、05A)を維持し、**両段の判定を同一`judge_audio`にする**。減速前後は別wavなのでSecondary重複にならない。最終採用音声=減速後wav(リストにも`original_wav`併記)。
- Dialogue(Std)/Voices A2(`er063:636-640`、`er012_b_family_voices_a2_production_01.py:696-752`)は外側ループがなく減速後NG=即STOPPED(再生成なし)。`generate_a2_segment_with_slowdown`に`gen_fn`引数を足して同じ外側ループ(通算3)を適用する(新しい例外ではなく既存A2全体の整合)。
- **B′案(最終音声のみ検証、V04 D-12(c))は第2段候補**: 構造変更が大きく、OPEN-76/270の再整理を伴うため本タスクでは採用せずOpus論点とする。

### 4-9. 既存Cascade各段の扱い(整理表)
| 既存段 | 統一後 |
|---|---|
| Primary#1 | 維持(P-chain全層) |
| Primary#2(同一音声OpenAI再転写) | 廃止(統一フローはPrimary 1回) |
| CS Eq層のAzure+local whisper small | 維持(Primary側explain層)。Azureは共有キャッシュ、local whisperは0円で維持 |
| Tier3(固有名詞等corroboration) | 維持。Azureは共有キャッシュ。ラベル`SECONDARY_ASR_CORROBORATED_MATCH`はWARNING化+リスト登録 |
| 非ラテン主体Cascade(KP) | トリガー意味維持(Primary非ラテン→Secondary)。「Primary NGは原則Secondary」に包含され、共有キャッシュ |
| force_secondary | LR後v1のみ維持(minimal撤去に伴い他では消滅) |
| Secondary#1/#2(PhraseList) | Secondary 1回(PhraseListは現行Ledger phrasesを維持、C-I)に統合 |
| M1 | Primary/Secondary両転写に維持(凍結候補、矛盾拒否) |
| COST_GUARD($0.05/segment L243) | 維持(segment ASR費用上限。Secondary 1回化で余裕増) |
| `human_review_required` at cascade尽き | 撤去(次slotへ)。slot3 NGで初めてHR |

---

## 5. 数値S1是正の設計

### 5-1. 比較の定義
`compare_values(canonical, other, lang) -> ValueVerdict ∈ {NO_VALUES, EQUAL, DIFF, AMBIGUOUS}`。両テキストから**順序付き**の値atom列を抽出し、`(値, 単位種別)`が全位置で一致=EQUAL、個数または値または単位種別が違う(欠落・追加を含む)=DIFF、曖昧表層が解決できない=AMBIGUOUS、両方に値なし=NO_VALUES。表記(漢数字/算用数字/全角/桁区切り/`%`/`percent`/`パーセント`)は比較に影響しない。

### 5-2. 日本語(再利用元: `er066_ja_asr_orthographic_equivalence_01_trial.py`のStage 1のみ)
- 抽出: NFKC→`SPAN_RE`(`_NUM_RE`=算用数字・3桁区切りカンマ・漢数字文法`_KGRAMMAR` L62-63+`COUNTERS` 30種: 人/日/円/%・パーセント/分/時間/年/歳/回/件/倍…, L29-37)。`_to_value`(L66)が漢数字を厳格文法(千百十の順、万の前に数字必須)で整数化。未知の助数詞は変換しない(fail-safe、L28)。
- 範囲・列挙: `3〜5日` は2atom(3,日)(5,日)として順序保持し、`35日`(35,日)とは**DIFF**(OPEN-334=`normalize_ja`の区切り除去による桁結合誤PASS、`OPEN_ITEMS.md` L837、を本ガードで塞ぐ)。
- 曖昧: `AMBIGUOUS_RE`(L45-51: 十分/三日月/一時/一月/一分/N分の・分厘・分割)。**閉集合の文脈マーカー**が同一名詞句にある場合のみ時間読みと確定し同値扱いにする: {`十分間`,`十分後`,`十分前`,`十分ほど`,`十分ぐらい`,`十分くらい`,`十分程度`,`十分おき`,`十分ごと`}(「十分な/に/だ/で」「以上/以内」は含めない=機械的同値化をしない)。確定できなければAMBIGUOUS。
- 取込み範囲(昇格するもの/しないもの): **昇格**=`find_spans/_to_value/COUNTERS/AMBIGUOUS_RE/value_form`相当(値署名)。**昇格しない**=Stage 1'(`opaque_form`置換+既存判定)の拡張、Stage 2(読み展開`reading_expansions`)、Candidate E veto(`candidate_e_veto`、OPEN-333)。今回のユーザー承認(原文§3「日本語表記ゆれ正規化を優先的に再利用」)は値と単位の比較までと解し、読み展開は範囲外(§6 C-K)。
- 配線: `protected_check_ja`の`_DIGIT_RE`分岐(`er007_ja_asr_validator_01.py:255-262`)を`compare_values`に置換。EQUAL→数値差とみなさず、両文の数値スパンを`<値:助数詞>`へ置換した形(`value_form`)で既存の`normalize_ja`比較を行い、残りが一致すれば`NORMALIZED_MATCH`相当(新ラベル`NUMERIC_VALUE_EQUIVALENT_MATCH`、不規則読み(`is_irregular_sig`)を含む署名は`warning=true`)としてPrimaryでPASS。DIFF→`number_mismatches`に値ペアを記録(既存挙動・既存test `er007_ja_scg_test_01.py:106 test_d_number_mismatch_not_executed`(150人→140人)はそのまま妥当)。AMBIGUOUS→`number_ambiguous`として未解決=保護差扱い(Secondaryには回さない。ただしSecondary転写が**原稿と同一表層(EXACT)**の場合に限りP3で扱う、下記5-5)。

### 5-3. 英語(再利用元: Tier1 atom + `normalize_numeric`)
- 抽出: `er021_en_asr_semantic_equivalence_production_01._tier1_atoms`(L394)のnumber/time atom(`_mk_number`: value=Fraction、currency、percent、ordinal)のみ(literal atomは除く)。ここに英語数詞語(`twenty five`)・`N%`・`N percent`・通貨・小数・序数・時刻・分数・ローマ数字が既に含まれる。
- 欠陥修正: `_is_number(tok)=tok.isdigit()`(`validation.py:622`)を、`normalize_numeric`が生成するマーカー付きtoken(`\d+(?:x(?:percent|dollar|decimalpoint)x\d*)*`、指数マーカー含む)も数値と認識するよう拡張。これで`25xpercentx`vs`26xpercentx`が`number_mismatches`に入る(現状は内容語差分扱い=Secondary解放の穴)。**5≠$5、5≠5%、28≠28th、2023≠2024、0.90≠0.09**等のSSOT固定の絶対不許容(`CURRENT_SPEC.md` L2014付近、55件regression)は維持/強化。
- Tier1のrole gate(5role)は**変更しない**。`compare_values`はrole非依存の新ガードとして全Section(見出し/KP/Dialogue含む)に適用(§6 C-G)。値が等価なだけで新たにPASSを増やす経路は追加しない(EN表記差の吸収は既存`normalize_numeric`+Tier1に委ねる=重複させない)。

### 5-4. 既存仕様との統合(重複排除の対応表)
| 既存 | 扱い |
|---|---|
| EN `normalize_numeric`(`validation.py:335`) | そのまま使用(再実装しない) |
| EN Tier1(`er021`) | atom抽出関数を呼ぶのみ。gate/early-exit挙動は不変 |
| EN `protected_check`の`_is_number` | マーカー付きtoken認識を追加(唯一の英語側コード修正) |
| JA `_DIGIT_RE`分岐 | `compare_values`へ置換(重複する数字抽出を廃止) |
| JA Trial値署名(`er066`) | Stage 1相当を`er078_asr_value_guard_01`へ移設(Trialファイルは無変更。Production→Trial importは作らない) |
| SCG除外の`number_mismatch` | `compare_values==DIFF`のときのみ除外。表記差だけでは除外しない(=旧過剰制限の撤廃) |
| 最終ANDゲート | 全層の後段で`compare_values`を再確認(Primary/Secondary/M1/Tier3の採用転写すべて) |

### 5-5. Primary/Secondary両方での適用と否定保護
- Primary: P-chain内(`protected_check*`)と最終ANDゲートの2箇所。Secondary: Secondary転写にも同じ`compare_values`+否定ガード。
- 「十分(10分の意味)」の扱い: Primaryが`10分`でcanonicalが`十分待ちました`(マーカーなし)→AMBIGUOUS=自動同値化しない。Secondaryが原稿と同一表層`十分待ちました`(EXACT)を返した場合のみPASS_WITH_WARNING(`NUMERIC_AMBIGUOUS_SURFACE`、読みが「じゅうぶん/じっぷん」のどちらかはASRで区別できないため人が試聴)。
- 否定: EN=`_NEGATION_WORDS`差(`protected_check` L673-676)、JA=`_has_negation_ja`+SCG推奨4マーカー(`er007_ja_secondary_asr_01.py:109-214`、ず/ません/ぬ/ざる/まい)。Primary NGで否定差があればP1でSecondary不呼出、Secondary転写に否定差があればNG_BOTH。新規拡張(否定活用ギャップ等)はD-19保留のまま追加しない。

### 5-6. 副作用と限界
- Primary側のASR数値誤認(TTSは正しいがASRが`26`と書く)は保護差としてSecondaryを呼ばず再生成になる=不要再生成が残る。頻度は実測が必要(現行JAで数値ゲート発火4件、`attempt_history.jsonl` L12833/L13161)。OPEN項目として記録し、Production運用後のtelemetry(`NG_PROTECTED`件数)で評価(新規Trialは起こさない)。
- JAの不規則読み(三日=さんにち等)は値が同じでもTTS誤読をASRが算用数字で書くと見えない→警告+試聴リストで補償。

### 5-7. ユーザー提示9例のtest case(固定。`er078_asr_value_guard_01_test_01.py`)
| # | 言語 | canonical | ASR | 期待ガード判定 | 期待する統一フロー上の結果 |
|---|---|---|---|---|---|
| 1 | JA | 三人で行きました。 | 3人で行きました。 | EQUAL | Primaryで`NUMERIC_VALUE_EQUIVALENT_MATCH`PASS(Secondary不呼出) |
| 2 | JA | 三人で行きました。 | 四人で行きました。 | DIFF | `NG_PROTECTED`、**Azure call_count==0**、再生成 |
| 3 | JA | 三十人が来ました。 | 30人が来ました。 | EQUAL | PASS |
| 4 | JA | 三十人が来ました。 | 40人が来ました。 | DIFF | `NG_PROTECTED`、Azure 0 |
| 5a | JA | 十分待ちました。 | 10分待ちました。 | AMBIGUOUS | 自動同値化しない。`NG_PROTECTED`相当(Secondary不呼出)。Secondaryを呼ぶ経路でもASR転写`10分`ではPASSせず、原稿同一表層のEXACTのみWARNING |
| 5b | JA | 十分間待ちました。 | 10分間待ちました。 | EQUAL(閉集合マーカー`十分間`) | PASS |
| 5c | JA | 三十分待ちました。 | 30分待ちました。 | EQUAL(数字直前の十は曖昧語でない) | PASS |
| 6 | JA | 100円でした。 | 百円でした。 | EQUAL | PASS |
| 7a | EN | The rate is 20% today. | The rate is 20 percent today. | EQUAL | PASS(既存`normalize_numeric`/Tier1) |
| 7b | JA | 20％の人が来ました。 | 20パーセントの人が来ました。 | EQUAL | PASS |
| 8 | EN/JA | 20% / 20％ | 30% / 30％ | DIFF | `NG_PROTECTED`、Azure 0 |
| 9 | EN/JA | 25% / 25％ | 26% / 26％ | DIFF | `NG_PROTECTED`、Azure 0(現行は穴) |
追加固定: `3〜5日`vs`35日`=DIFF(OPEN-334)、`3人`vs`3日`(助数詞違い)=DIFF、`2026年`vs`二千二十六年`=EQUAL、`3,000円`vs`三千円`=EQUAL、`5`vs`$5`/`5%`=DIFF、`28`vs`28th`=DIFF、`1.5倍`vs`1.6倍`=DIFF、欠落(`三人`vs数字なし)=DIFF、追加(数字なし vs `三人`)=DIFF、否定(`眠くならない`vs`眠くなる`、EN `can`/`cannot`、`not`有無)=P1でSecondary不呼出。

---

## 6. 競合一覧(STOP候補)

判定凡例: **R**=承認範囲内で解消可能(案あり、実装を進めてよい)/ **R+**=今回の明示指示が後発のため解消可能だが、旧ユーザー決定の置換としてFableがDECISION_LOGに原文転記・記録する(Gate 2)/ **U**=ユーザー判断が必要(STOP候補)。

| ID | 競合(承認仕様 vs 既存承認仕様) | 判定 | 解消案(根拠) |
|---|---|---|---|
| **C-A** | (a) 日本語SCGの既存除外条件(2026-10-11ユーザー承認: 数字差・否定差・固有名詞C1・類似度<0.4・length NG・同形異音C2、`CURRENT_SPEC.md` L2016) vs 今回「不一致の種類によらず原則Secondary」「Secondary PASS→採用」 | 分解して判定 | **A1 数字差**: 値DIFFのみ除外へ縮小(表記差は除外しない)=**R**(原文§3の撤廃指示)。**A2 否定差・否定マーカー差**: 維持=**R**(原文§3「否定の既存保護は維持」)。**A3 length NG**: 維持=**R**(Secondaryで救えてもlength ANDで不合格、コスト短絡のみ)。**A4 C2同形異音**: 維持を提案(Azureが原稿の漢字表記と一致しても読み違いを区別できず誤PASS、V04 L109)=**R+**(10/11ユーザー採用例外であり、今回の「原則」の例外として残す。FableがDECISION_LOGに「原則の例外として維持」と明記)。**A5 類似度<0.4 / A6 固有名詞C1**: 10/11承認の除外条件を今回の一般原則が上書きするか=**U(1問のみ)**。暫定実装=現行維持(除外表`SCG_EXCLUSIONS`をデータ化、承認後は1行で解放+C1はPASS_WITH_WARNING(S7)化)。推奨=解放(試聴リストが整備されるため) |
| **C-B** | (b) Key Phrase: 現行4回(MINIMAL×2+ENGLISH_LOCK×2、2026-09-01正式決定)・解説2回・Tier1/CS層/LR非適用(明示除外) vs 全体TTS3回・Prompt維持 | **R(3回へ揃える。委任_02a OF-AUW-12確認: 3回仕様のユーザー決定逐語なし・Trial値max_attempts=2の継承。DESIGN_02_ADDENDUM_01 §9)** | 原文§5「Section固有の既存例外は維持」に従い構造は維持し**判定のみ統一**(Primary NG→Secondary→WARNING)。3回単一Prompt化(D-6, OPEN-289)は新規仕様判断になるため**本タスクでは行わない**(=要判断を発生させない)。KP解説の2回(`er019:700`)も維持。KPで保護するのは学習対象英語の不変=LR対象外維持 |
| **C-C** | (c) 現行Cascadeの試行回数・LR発火条件 vs 新フロー: (i)Cascade尽き→HR直行(ER-008)と「両NG→再生成」 (ii)標準2+minimal1(2026-09-04正式決定)と「Prompt維持」 (iii)cool-down 600s (iv)LR発火(UNCERTAINでも発火) (v)LR再TTS計数 (vi)累積15/60とSecondary増 | (i)(ii)=**R+**、(iii)=**R**、(iv)(v)(vi)=**R** | (i)今回指示(原文§2)が後発・明示。(ii)内容NG再試行は同一Prompt、技術失敗(400/空応答)も同一Prompt再試行に統一(minimalはLR再TTSからも撤去、OPEN-274)。旧決定(2026-09-04)の置換としてDECISION_LOGへ原文転記。(iii)D-14(c)現行維持(3回目直前600秒、CS有効roleのみ)=証拠取得の所要時間に影響(§9)。(iv)§4-7。(v)§4-7。(vi)Primary#2/S#2廃止でASR呼出は減る方向 |
| **C-D** | (d) V04 D-1〜D-19の本指示による決定状況(下表) | 下表 | |
| **C-E** | (e) 日本語LRの現状 | **R** | 現状JA leafにLR呼出なし=原文§5-2/6-2「原則HR」と一致。3NG→STOPPED→HR Lock(`record_outcome`)。変更不要 |
| **C-F** | 「全Family」 vs Family体系決定(CURRENT_SPEC L1543-1580: Active=X/Y/Z、A/B/Cはlegacyで新規実装・追従更新しない、共有moduleの変更は妨げない) | **R** | 共有leaf/adapterの変更が自動波及するため判定はlegacy A/B/Cにも適用される(専用コードは変更しない)。Yは実装なし(N/A)。legacyの試聴ページ更新はせず`audit/*.json`のみ(L1556の趣旨)。ユーザーがlegacyのページ表示まで要求する場合のみ追加確認 |
| **C-G** | Tier1/CS層/LRのrole gate(5role限定、見出し・KP明示除外、`er020:117`、`er021:43`)と「全Section」「必要なRoleへ共有機構として適用」 | **R** | **値ガード(新機構)のみ全Section**に適用し、既存gate(Tier1/CS層/LR)は不変。M1は既に全英語経路(`m1_enabled=True`)。Dialogue/見出し/KPは`segment_id`未渡しでTier1非適用だが値ガードはrole非依存のため問題なし。CS層の見出し/KP拡張は不要(Melos見出し相当12/12はM1のみで達成) |
| **C-H** | PASS_WITH_WARNING運用: 10/12 V04 2-6/D-2「確認前に公開へ進めない」 vs 今回「事前承認不要・自動採用・事後試聴」 | **R+** | 今回のユーザー決定が優先(非ブロッキング)。ただし「安全≠成功」原則(`PM_GOVERNANCE.md` 6節)との関係を踏まえ、**保護差(値/否定)は警告で解放しない**設計(§4-3b)で整合を取る。ユーザー指示原文全文をDECISION_LOGに転記(Gate 2) |
| **C-I** | D-3 Secondary PASS集合の非対称(EN 4ラベル/JA 2ラベル)とPhraseList | **R**(Opus論点3) | 言語別既存承認集合を維持(§4-3c)。JAは10/11承認の2ラベルを上書きしない。表記差は値ガードの正規化でNORMALIZED相当に引上げ(V04 D-3(b)の「2ラベル+個別正規化」と同方向)。EN Secondaryは現行Ledger PhraseListを維持(独立性の観点はOpus論点) |
| **C-J** | 数値保護 vs 「Secondary PASSなら採用」 | **R** | 原文§3末尾の優先規定(「重大内容差を誤採用しないことを優先」)で解消: 保護差は**Secondary不呼出+最終ANDゲート**。副作用(ASR誤認による不要再生成)は§5-6 |
| **C-K** | JA Trial(`er066`: 「Productionからimportされない/ユーザー承認(APPROVED_FOR_PRODUCTION)までProductionへ入れてはならない」、OPEN-287=採用判断なし)のProduction昇格 | **R+** | 今回の原文§3「日本語表記ゆれ正規化を優先的に再利用」を承認と解し、**Stage 1(値署名)のみ**を`er078_asr_value_guard_01`へ移設(Trial無変更)。読み展開(S1'/S2)・Candidate E veto(OPEN-333)は昇格しない。FableがOPEN-287更新時に「今回承認範囲の包含」を明記 |
| **C-L** | A2 6%減速: B0(現構造維持+判定統一)/B′(最終音声のみ検証、D-12(c)) | **R**(B0)/Opus論点 | 第1段=B0。B′は構造変更が大きく新規仕様判断になりうるため本タスクでは採用しない(記録のみ) |
| **C-M** | 通算TTS上限SSOT(CURRENT_SPEC L1712「初回含め最大3回」)とLR再TTS 1回 | **R** | LR再TTSは既存どおり別枠1回(現行`max_attempts=1`維持)として明示的に計数(通算上限15/ASR60に含める)。SSOT文言(L1712)に「LR再TTSを除く」注記を実装段で追記 |

### (C-D) D-5〜D-19 の決定状況(本指示後)
| ID | 内容(V04 8章) | 状態 | 扱い |
|---|---|---|---|
| D-1 | 導入範囲・順 | **決定**(全Family・全Section) | 実装順はFable判断(§10) |
| D-2 | 試聴リスト連動を前提とするか | **決定**(連動を同時に完成、非ブロッキング) | §4-6 |
| D-3 | Secondary PASS集合 | **未決のまま実質R案**(C-I) | 言語別既存集合維持 |
| D-4 | S1是正 | **決定**(原文§3) | §5 |
| D-5 | 見出し・LR後v1の追加保護 | **一部決定**(§5-3「見出し・短文は独立QA・意味保護維持」) | LR後v1=force_secondary維持、見出しは現行(force_secondaryなし)維持+minimal2撤去=OPEN-288の主旨 |
| D-6 | KP単一Prompt | **不要化**(KP構造維持、C-B) | 追加Trial不要 |
| D-7 | UNCERTAIN→HR直行廃止 | **決定**(両NG→再生成)。C-C(i) | |
| D-8 | minimal撤去範囲 | **実質決定**(「Prompt維持」)。C-C(ii) | 技術失敗時も同一Prompt再試行 |
| D-9 | LR位置づけ・日本語 | **決定**(EN: 3NG後+ASR誤認は書換えない、JA: HR) | §4-7 |
| D-10 | C1廃止/C2維持 | **未決**(C-A5/A6=U) | 暫定現行維持 |
| D-11 | 固有名詞Secondary一致の扱い | **実質決定**(Secondary PASS→WARNING一般則に包含) | C1がUで残る |
| D-12 | 6%減速案 | **未決**(整合要求のみ) | B0(C-L) |
| D-13 | Secondary選択(Azure/local medium) | **未決**(指示なし) | Azure維持、local medium採用しない |
| D-14 | cool-down | **未決** | 現行維持(3回目直前600秒) |
| D-15 | 技術失敗・ASR障害 | **一部決定**(Secondary障害はPASS不可) | TTS技術失敗は現行どおりattempt消費(attempt外化は新規仕様判断のため保留) |
| D-16 | Trial実施可否 | **決定**(新規Trial不要) | |
| D-17 | LR再TTS計数 | **決定**(必須) | §4-7 |
| D-18 | 解消済み | 変更なし | OPEN-285/282-284は別件 |
| D-19 | 保留(否定拡張等) | **保留継続** | 追加しない |

---

## 7. 変更箇所一覧

ロールバック: 承認済みのためflagは作らない(委任文)。**各変更をcommit単位に分け`git revert <hash>`で戻せる**ようにする(段ごとにcommit。新規モジュールは配線commitまでimportされないため、配線commitのrevertだけで現行挙動に戻る)。配線commit以前の新規モジュール追加は無影響。

| # | ファイル:関数 | 変更種別 | 内容 | commit段 |
|---|---|---|---|---|
| 1 | 新規`er078_asr_value_guard_01.py` | 新規 | §5。EN=`er021._tier1_atoms`呼出、JA=`er066`Stage 1相当を移設 | 02 |
| 2 | 新規`er078_asr_unified_judge_01.py` | 新規 | §4。`judge_audio`/`SecondaryCache`/`JudgeResult` | 02 |
| 3 | 新規`er078_pass_with_warning_registry_01.py` | 新規 | §4-6 | 02 |
| 4 | `er006_preprod_hardening_01_validation.py:_is_number`(L622) | 変更 | マーカー付き数値tokenの認識追加(55件regression固定) | 03 |
| 5 | `er007_ja_asr_validator_01.py:protected_check_ja`(L255-262)、`_DIGIT_RE`(L67) | 変更 | 数字branchを`compare_values`へ | 04 |
| 6 | `er006_secondary_asr_01.py:evaluate_attempt_with_cascade_detail`(L535-981)、`:evaluate_attempt_with_cascade`(L417)、`:get_full_text_via_azure_stt_with_phrase_list`(L70)呼出6箇所 | 変更(adapter化) | `cascade_eligible`(L812)撤去、4段→Secondary 1回、cascade尽きHR直行(L947-949)撤去、Azure呼出をSecondaryCache経由、force_secondaryをLR後v1用に限定 | 03 |
| 7 | `er007_ja_secondary_asr_01.py:_scg_exclusion_reason`(L188)、`_run_scg_secondary_confirm`(L302)、`evaluate_attempt_ja_with_cascade_detail`(L383-)、JA Cascade(L440-) | 変更(adapter化) | 数字除外→値ガード、`SCG_EXCLUSIONS`データ化、PASS時にWARNING記録、Azure二重(SCG+Cascade)をキャッシュ化 | 04 |
| 8 | `er003_v1_sing01_voice01_generate.py:generate_charon_english`(L238, LR L359)、`generate_charon_japanese`(L434-、L515/L563) | 変更 | attempt_ctx受渡し、`asr_judgement`記録、cascade由来stop_retrying撤去、LR再TTS計数、minimal撤去(JA) | 03/04 |
| 9 | `er003_v1_sing01_news_tail_fix.py:generate_news_narration_wide_margin`(L202, LR L368) | 変更 | 同上 | 03 |
| 10 | `er003_v1_crosslevel_audio_02_common.py:generate_english_segment_with_fallback`(L79)、`_run_a2_minimal_fallback_attempt`(L301)、`_retts_fn`(L392) | 変更 | minimal分岐撤去(標準Prompt 3回)、force_secondary(L344-351)をLR後v1のみ、LR発火条件(L247-262,L292) | 03 |
| 11 | `er003_v1_repro01_main_generate.py:generate_narration_snippet_verified_strict`(L349/L374)、`generate_key_phrase_component_verified`(L761) | 変更 | judge経由。KPの4回構成・Prompt切替は不変 | 03/04 |
| 12 | `er003_v1_sing01_point_headings_aoede.py:generate`(L77-100,L126) | 変更 | minimal2→同一Prompt。judge経由 | 03 |
| 13 | `er012_b_family_voices_production_01.py:generate_voice_body_wide_margin`(L479, L537-560) | 変更 | judge経由、minimal fallback(L537)整理 | 03 |
| 14 | `er003_v1_n3_01_tts_generate.py:apply_a2_slowdown_postprocess`(L172)、`_post_slowdown_cascade_rescue`(L120)、`generate_a2_segment_with_slowdown`(L283)、`generate_a2_japanese_with_fallback`(L584) | 変更 | 減速後judge統一、外側ループ`gen_fn`汎化、JA minimal整理 | 05 |
| 15 | `er063_family_z_audio_01.py:real_generators.dialogue`(L636-642) / `er012_b_family_voices_a2_production_01.py:696-752` | 変更 | Dialogue(Std)/Voices A2に外側ループ適用 | 05 |
| 16 | `er011_human_review_lock_01.py`(`PRODUCTION_STANDARD/MINIMAL_*`定数L100-104、`build_attempts_detail`L212、`record_outcome`L355) | 変更 | 定数意味の再定義(+assert整合)、`asr_judgement`追加、LR再TTS計数 | 03 |
| 17 | `er020_tts_retry_local_rewrite_01.py:run_local_rewrite_recovery`(L686)入口 | 変更 | 合意誤読ガード(§4-7⑤)、結果にretts計数 | 03 |
| 18 | `er019_family_x_audio_production_runner_01.py:build_player_html`(L2092)、`er063_family_z_audio_01.py:build_listening_page_html`(L1312)/`er026...stage_pages`(L1407) | 変更 | WARNING試聴リスト節 | 04 |
| 19 | test: `er007_ja_scg_test_01.py`ほか(§8) | 更新+新規 | 期待値が旧仕様(表記差でSCG不実行)を固定していればGrepして更新/撤去 | 各段 |
| 20 | SSOT: `CURRENT_SPEC.md`(L1692付近TTS上限注記、判定仕様)、`DECISION_LOG.md`(ユーザー指示原文全文)、`OPEN_ITEMS.md`(OPEN-286〜291・333・334更新) | 実装段最後 | 実態反映 | 07 |

撤去・整理されるもの(旧規則・旧検査): EN `cascade_eligible`ゲート、4段Cascade(Primary#2/Secondary#2)、cascade尽きHR直行、`force_secondary`(minimal用)、JA数字除外(`\d+`)、minimal fallback(内容NG再試行・LR再TTS)、見出し標準1+minimal2。残置: KPの4回構成、C2/否定マーカー除外、cool-down、COST_GUARD、同一signature打切り関数。撤去後は静的Grep(§8-4)で旧識別子の残存を検査する。

---

## 8. test計画

### 8-1. Unit(API 0、mock engine)
| test | 内容 | 件数目安 |
|---|---|---|
| `er078_asr_value_guard_01_test_01.py` | §5-7の9例(+5a/5b/5c)+追加固定ケース、EN/JA、否定、曖昧マーカー閉集合、Fraction/桁区切り/範囲 | 40+ |
| `er078_asr_unified_judge_01_test_01.py` | 状態機械全分岐(P0/P1/P2/P3/S0〜S3/slot3)、Secondary障害(None/例外/空/timeout)→PASS不可・LR不可・2連続でHR_TECH、保護差でSecondary call_count==0、WARNING採用、最終ANDゲート(Tier1/M1/Tier3経由でもDIFFは止まる)、`force_secondary`(LR後v1) | 30+ |
| 重複防止 | tier3+Eq層+非ラテン+forced+S#を全部発火させてもAzure call_count==1。JA SCG+Cascadeでも1。別wav(再生成/減速後)は別呼出 | 6 |
| 上限 | 通算TTS≤3(LR再TTS別枠1)、無限retryなし、累積15/ASR60でHR、COST_GUARD | 6 |
| registry | `tts_generation_results.json`→listing導出、sha256一致検査、重複排除、LR_REWRITTEN、減速後original_wav | 8 |
| 静的監査 | `er078_asr_unified_wiring_static_audit_01.py`: 判定点11箇所がjudge経由、旧識別子(`cascade_eligible`等)残存0 | 3 |

### 8-2. Integration(mock TTS/ASR。各Family runnerの全経路)
経路×Family: **初回/retry(slot2)/fallback(技術失敗)/regeneration(slot3)/LR後v1/A2減速後**。方式: leaf関数の`routing.transcribe`・TTS呼出(`p9a.generate_narration_snippet`)・`get_full_text_via_azure_stt_with_phrase_list`/`_azure_stt_strict`をmock(既存`er007_ja_scg_test_01.py`のmock方式)。X: `er019 --dry-run`系+leaf直、Z: `ctx.hooks["tts_generators"]`+`wrap_generators_with_budget`(既存mock harness、`er026_output/.../evidence_12A/run_stoptest_01_mock__*`の方式)。legacy A/B/Cは共有leafをlegacy呼出パスで1ケースずつ。マトリクス43行のうち生成を伴う行は全行を最低1シナリオでカバーし、カバレッジ表をtest出力に出す。

### 8-3. Regression
| 基準 | 方法(API要否) |
|---|---|
| `Melos said.` Full Story相当12/12・Dialogue/見出し相当12/12・M1新規救済21観測・M1誤受理0 | `er077_output/m1_oov_multi_pronunciation_01/evidence_01/clip_results.json`(36観測、保存転写)を**統一judgeで再判定**する`er078_melos_regression_replay_01.py`を作成(**API 0**。CMU辞書・ledger_snapshot.jsonで凍結)。期待: 12/12, 12/12, M1受理21, 誤受理0。出典: `EVIDENCE_RUN_01.md` §2。※「21観測」の元データは同ファイルに存在することを確認 |
| 既存test全回帰 | `er006_preprod_hardening_01_validation_test.py`(55件、絶対不許容差を含む)、`er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`(62)、`er007_ja_scg_test_01.py`(46関数)+`er007_ja_scg_c2_neg_test_01.py`(17)+`er007_ja_scg_phase0_regression_test_01.py`、`er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py`、`er011_b1_connected_speech_validator_01_f1_test_01.py`、`er077_m1_oov_multi_pronunciation_01_test_01.py`(14)+配線22件、`er058_asr_tts_prodfix_01_test_01.py`(27)、`er066_*_test_01.py`(18)+`_test_02.py`(31、Trial無変更の確認)、`er020_tts_retry_local_rewrite_fullseg_test_01.py`、`tools/stop_scope_check_01_test_01.py`。**本委任では未実行**(実行すると`er021 telemetry`等の追跡ファイルを更新する副作用があり、無関係差分を作るため。実装段で実行し結果を記録) |
| 更新対象test | Grepで特定した「旧仕様を期待値に固定している」箇所(例: 表記差でSCG不実行を期待するtest、cascade尽きHR直行、minimal3回目を期待するtest)を更新/撤去(不整合な出力を期待値としてassertしない) |
| 新旧挙動差の定量 | 保存済み転写(`attempt_history.jsonl`のattempts_detail、`er021 telemetry.jsonl` 2537件、HR queue 72行、`er069` results)を新旧judgeで再判定し、PASS→NGに変わる件(保護差)とNG→PASSに変わる件(WARNING)を件数表にする(API 0)。誤PASS(新規)0・Regression悪化0が受入条件 |

### 8-4. 旧ルール撤去の残存検査
`rg -n "cascade_eligible|human_review_required.*True.*stop_retrying|_DIGIT_RE.*number_mismatches|minimal_after|PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS"`(Production module)を実装後に再Grepし、意図して残す識別子(KP定数等)以外が0であることをRESULT_PACKETに記載。

---

## 9. runtime evidence計画

**方針**: 既存音声・保存転写を最優先(API 0)。Production正式path(各runnerの`--only-clips`/leaf関数)で必要最小限の実API。新規Trial・フルE2Eは行わない。実行は`tools/stop_scope_check_01.py`(rc=3なら停止)、`TTS_EXECUTION_MODE=STANDARD`明示、`--budget`/BudgetGuard指定、1コマンド1回(自動再試行ラッパ禁止)。

単価の根拠(既存実績): TTS(Flash-Lite、短文≒2〜4秒)¥0.062/clip・OpenAI ASR ≈¥0.01/短clip・Azure ¥0.0444/秒(1回ごと秒切上げ、SCG_AZURE登録単価$1.0/h×160円、`er007_ja_secondary_asr_01.py:88-91`)。出典: `er077_output/m1_oov_multi_pronunciation_01/evidence_01/cost_01.json`(36観測: TTS¥0.7447/12clip、ASR¥2.5988[OpenAI42回+Azure25回])。長文Full Story相当は別途(下表で明記)。

| ID | シナリオ | Production経路 | 再利用 | 新規API(call数×単価) | 見積JPY | 合格基準 |
|---|---|---|---|---|---|---|
| R0 | 全シナリオの事前検証 | 判定関数(adapter) | 保存転写(Melos 36観測、attempt_history、telemetry) | 0 | 0 | 新旧再判定表。誤PASS新規0 |
| R1 | EN: Primary NG→Secondary PASS→PASS_WITH_WARNING→リスト(Melos said.) | `er026`/`er063` real_generators(narrator)を`--only-clips full_story_part1_c5`(std・adv) | Melos wav24本(`evidence_01/gen/wav`、ローカル存在確認済み、git未追跡)で事前にAPI 0確認 | TTS ≤3×2=6(¥0.37)、OpenAI ASR ≤6(¥0.06)、Azure ≤6≒2s(¥0.53。dedupで実際は≤2) | **約1.0** | WARNING採用1件以上+リスト出現+sha一致+Azure重複0。Primaryが偶然PASSする場合は録音済みwavをTTS stubで差し替え(ASRのみ) |
| R2 | JA: Primary NG→SCG PASS→WARNING→リスト | X runner A2 JA(`--only-clips`相当、preview等短文)。自然発火が無い場合は既知の誤認例を注入 | JA既知NG転写(`attempt_history.jsonl` L12583)で判定のみ事前確認 | TTS 3(¥0.19)、OpenAI ASR 3(¥0.03)、Azure 3×約3s(¥0.4) | **約0.7** | WARNING採用+リスト+`SECONDARY_CONFIRMED`記録 |
| R3 | 数値異値の不採用(EN 25%→26%、JA 三人→四人) | leaf関数(各1)+保護差ではSecondary不呼出の確認 | 既存wav+canonical差替え(TTS再利用)。JA三人は新規TTS 1 | OpenAI ASR 2、TTS 1(¥0.06)、Azure 0(保護差のため) | **約0.1** | NG_PROTECTED、Azure call_count==0、最終成果物にPASSなし |
| R4 | 両NG×3→EN LR(合意誤読)/JA HR | leaf(`voice01.generate_charon_english`/`n3_tts` JA)。TTSは録音wav差替えhook、ASR/Secondaryは実API | 既存NG wav(誤りが再現するもの) | OpenAI ASR 3、Azure 3(≒¥0.4)、LR LLM(候補生成+QA)約2呼出(見積¥3、単価は`er005_cost_logger`要確認)、LR再TTS 1(¥0.06) | **約3.5** | slot≤3、LR発火1回、再TTS計数+1、JAはHR queue1行、cool-down待機(600s)は`maybe_cooldown_before_attempt`に`sleep_fn`注入のtest-onlyで回避しない=実時間10分を許容するか、CS無効roleで実施(要Fable判断、§12) |
| R5 | Secondary障害時の処理 | leaf+Azure endpoint不正(timeout短縮)で故意障害 | 録音wav | OpenAI ASR 2、Azure 0課金 | **約0.05** | PASS不可・次slot・2連続でHR_TECH |
| R6 | A2 6%減速(EN)・Dialogue Std外側ループ | `generate_a2_segment_with_slowdown`/Z dialogue(std)を`--only-clips`(短い1clip) | 録音wav | TTS ≤3(¥0.2)、ASR ≤6(¥0.2)、Azure ≤3(¥0.4) | **約0.8** | 減速前後とも統一judge、通算TTS≤3、original_wav保持、リスト登録(減速後wav) |
| R7 | Family別の初回正常系回帰(X/Z各1clip: Preview/Comment JA、Topic intro EN) | 各runner `--only-clips` | - | TTS 6(¥0.4)、ASR 12(¥0.2) | **約0.6** | 既存と同等にPASS、Secondary不呼出、API異常なし |
| R8 | 試聴リストページ(X player/Z page) | `build_player_html`/`build_listening_page_html` | R1〜R6の出力 | 0(Playwright --local) | 0 | リスト節表示・音声再生・`file://`なし |
| 合計 | | | | | **約6.8〜8(見積幅¥5〜15、予算案¥15・hard stop¥20)** | |

- 日次開発費上限(¥1,000/JST、7-9)に対し十分小さい。70円/記事セット(15-9)への影響評価: Secondary 1回化とPrimary#2/S#2廃止でASR呼出は減る方向、PASS_WITH_WARNING増による再生成減で量産費は低下見込み(要計測、R7の1clip単価でtelemetry取得)。
- **未確認**: R1でPrimary NGが自然発火する確率(Melos 12takeで標準8/12がNG=約67%/take、3 slot独立なら全PASS確率≈4%)。LR LLM単価。R4のcool-down実時間(10分)の扱い。

---

## 10. 実装分割案

| 委任 | 範囲 | 受入条件 | 費用 | 見積時間 |
|---|---|---|---|---|
| **_02** 共通判定+数値S1+Unit | §7 #1〜#3、#4(EN `_is_number`)、#5(JA数字branch)の**モジュール・単体のみ**(leaf配線なし)。test: §8-1(value_guard 40+、judge 30+、dedup 6、registry 8) | 新規test全PASS+既存test全回帰PASS(特に55件・SCG 63件)。Production到達経路の挙動不変(未配線)をGrepで確認。9例固定 | JPY0 | 約4h(並列: value_guard/registry/judge skeleton) |
| **_03** EN配線 | #6、#8(voice01 EN)、#9、#10、#11(EN)、#12、#13、#16、#17。minimal撤去、LR条件・計数、Secondary 1回化 | Integration(EN全経路)PASS、Melos replay 12/12・12/12・21・0、新旧再判定表で新規誤PASS 0 | JPY0 | 約5h |
| **_04** JA配線+試聴リスト | #5配線、#7、#8(voice01 JA)、#11(JA)、#14(JA部)、#18(ページ) | JA Integration PASS、SCG既存63件回帰、registry・ページ(Playwright --local)PASS | JPY0 | 約4h |
| **_05** A2減速・Dialogue汎化+KP整合 | #14、#15、KP経路のjudge統合確認 | A2減速前後Integration、Dialogue(Std)外側ループ通算3、KP4回構成不変のtest | JPY0 | 約3h |
| **_06** runtime evidence | §9 R1〜R8 | R1〜R8の合格基準、費用実績≤予算案、証跡は`er058_output/unified_all_roles_production_wiring_01/`配下(既存構造) | JPY約7〜15 | 約3h(cool-down待機含む) |
| **_07** SSOT・Gate | CURRENT_SPEC/DECISION_LOG(原文全文)/OPEN_ITEMS更新、Dangling Reference Check(Gate 4)、commit/push/merge確認、Fable Gate 3/4/7受入 | 必須受入条件15項のうち実施可能分を全て証跡付きで確認。1項目でも未確認ならPRODUCTION_WIREDと報告しない | JPY0 | 約2h |

並列化: _02内で3モジュールは独立。_03と_04は同一ファイルを触らない部分(EN/JA)が多いが`er011_human_review_lock_01.py`(#16)・`n3_tts`が共通のため、_03で共通部(#16,#17)を先に確定→_04並行が現実的(理由明示: 同一ファイル競合)。各段の直前にSTOP helper、TTS/ASR実APIは_06のみ。

---

## 11. Opus条件A(新しい処理フロー)レビューへ渡す論点

1. **保護差の扱い(最重要)**: 値DIFF/否定差のPrimary NGで**Secondaryを呼ばず再生成**する案(本設計)と、Secondaryを呼んで**両エンジンの一致を条件にする**案(B)の比較。誤PASS(致命)vs 不要再生成/費用。最終ANDゲートの多重化は十分か。AMBIGUOUS(「十分」等)の扱い(Secondary EXACTのみWARNING)は妥当か。
2. **adapter方式の妥当性**: 2関数の内部置換で11判定点(約50ファイルの旧呼出元を含む)に波及する設計の回帰リスク。署名・返り値互換、`detail_out`、HR queue記録の維持。inline方式との比較。
3. **Secondary設計**: 言語別許容集合の維持(C-I)、EN PhraseList維持(Secondaryが原稿へ寄る独立性リスク)vs 無し、sha256キャッシュの粒度、Primary#2/S#2廃止の影響、Secondary障害時の「2連続でHR_TECH」ルール。
4. **「両NG→再生成」への置換**: Cascade尽きHR直行(ER-008)の廃止が固有名詞・ASR不安定型(Melos等)で引き起こす再生成コスト・cool-down(600s×3)・HR到達の変化。C-C(i)(ii)の旧決定置換の扱い。
5. **LR発火条件の絞り込み(合意誤読のみ)**: 判定式(差分spanの一致)の妥当性、LR後v1のforce_secondary、LR再TTSの標準Prompt化、再TTS計数、JA/KP/見出し/Dialogueの非LR維持。
6. **A2 6%減速**: B0(第1段)で十分か。Dialogue(Std)/Voices A2への外側ループ汎化が既存仕様(OPEN-76/270)と矛盾しないか。B′の要否。
7. **値ガード**: JA Trial(Stage 1)昇格の範囲(読み展開を含めない判断)、閉集合マーカー、不規則読みのWARNING化、EN `_is_number`拡張がTier1・55件regressionに与える影響、`3〜5日`等のOPEN-334の同時解消の妥当性。
8. **WARNINGリスト設計**: `tts_generation_results.json`からの導出(二重管理なし)、非ブロッキング(安全≠成功原則との整合)、Master Store reuse時の警告継承、legacy Familyはjsonのみとする線引き。

---

## 12. 付録: 実行した調査コマンド・確認できなかった事項

### 12-1. 実行コマンド(Read-only)
`tools/stop_scope_check_01.py --managed-id ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 --run-dir er058_output/unified_all_roles_production_wiring_01`(rc=0、非停止、applicable空)/ T-0 `check_delegation_prompt.py`(FAIL: 必須節「事前指定Grep一覧+追記位置・更新位置の手順」不足[委任文は「事前指定Read一覧」]、警告: TTS_EXECUTION_MODE/budget言及なし[設計段・TTSなし]、FAILでも継続)/ `rg -l "TTS_EXECUTION_MODE|def stage_tts|tts_generation_results" --type py`/ `rg -l "evaluate_attempt_with_cascade|evaluate_attempt_ja_with_cascade" --type py`/ 主要10ファイルでの`\.transcribe(|classify_asr_match(|classify_ja_asr_match(|evaluate_attempt(_ja)?_with_cascade(_detail)?(`のGrep(§3.1)/ `git log --oneline --since=2026-10-10 -- er006_preprod_hardening_01_validation.py er007_ja_secondary_asr_01.py er007_ja_asr_validator_01.py er006_secondary_asr_01.py`(94fb0c03f M1配線 / 7948bd78e F1 / d40cfbc7d 05A / 690cb7b7e 04A / 93c99da80 C2・推奨4 / 6b054b522 / c9ca93ee9 SCG)/ `git status --porcelain -- er058_output/unified_all_roles_production_wiring_01 docs/pm/delegation_log`。

### 12-2. 確認できなかった事項・前提
1. **テスト未実行**: 既存testは本委任で実行していない(telemetry等の追跡ファイルを更新する副作用を避けるため)。件数は`def test`のGrep/既存SSOT記載値であり、最新PASS状態は実装段で確認する。
2. **「21観測」の根拠**: `EVIDENCE_RUN_01.md` §2に「全21件の受理」と記載(Full Story相当9+Dialogue相当12)を確認。CS_Equivalenceや誤受理0の再現は保存転写の再判定で行う計画で、本委任では再現していない。
3. **legacy individual scripts**(過去one-off)に残る旧leaf呼出は対象外と判断(Production正式経路ではない)。Family C/Eのrunner詳細(`er013_family_c_production_runner_01.py`、`er012_e_family_entertainment_two_level_runner_01.py`)は共有leaf呼出であることをGrepで確認したが、全行は列挙していない。
4. **Master Store manifestのスキーマ**(警告継承のため`asr_judgement`を保存できるか)は未確認。
5. **LR LLM単価・R4のcool-down実時間の扱い**(10分待機を許容するか、CS無効roleで検証するか)はFable判断が必要。
6. **英語のTTS技術失敗のattempt外化**(V04 D-15(a))は本指示で決定されていないため設計に含めない。現行(attempt消費)を維持。
7. 行番号は`233c0cb4d`時点。実装段で再確認する。
8. 10/12のUSER_DECISION_REGISTER #18/#24と本指示の関係(登録の更新)はSSOT段(委任_07)で扱う。
