# ER-010 No.9 Final Closeout

**管理ID**: ER-010-NO9-FINAL-APPROVAL-CLOSEOUT-AND-FULL-STATUS-AUDIT-28
**日付**: 2026-09-02
**目的**: No.9(pool_n9_tip_screens、"Tip Screen"記事)の開発全体を、ユーザー最終承認の記録と同時にRepository evidenceから完全棚卸しし、No.10以降の開発が参照できるSSOT補助資料として保全する。本文書はDECISION_LOG.md/OPEN_ITEMS.md/CURRENT_SPEC.mdを代替しない(それらが引き続き一次SSOT)。本文書はNo.9という1テーマの開発経緯を横断的に要約した二次資料。

---

## 1. No.9概要

- **テーマ**: "Why the Tip Screen Always Suggests More Than You Meant to Give" → 最終版タイトル "When the Tip Screen Starts the Negotiation"(A2)。飲食店・タクシーの決済画面が提案するチップ候補が、客の判断にどう影響するかを扱う記事。
- **出力先**: `er006_output/pool_pilot_01/pool_n9_tip_screens/{a2,b1b}/`
- **開発期間**: 2026-08-29(ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02、Writer品質是正の発端)〜2026-09-02(本Closeout)
- **関連management ID**: 24件(下記4節Final Status一覧参照)、うちProduction仕様への正式変更を伴うもの17件、診断専用4件、User Decision記録専用3件

## 2. A2/B1最終asset

| Level | ファイル | Duration | sha256 | Clipping | 状態 |
|---|---|---|---|---|---|
| A2 | `er006_output/pool_pilot_01/pool_n9_tip_screens/a2/assembled/English_Your_Way_A2_POOL_N9_TIP_SCREENS.wav` | 354.162秒 | `a07210c5722fad64e9d21c4b1d787d903400545dec0c142b3b91f656164e4946` | 無し | **FINAL USER APPROVED**(2026-09-02) |
| B1 | `er006_output/pool_pilot_01/pool_n9_tip_screens/b1b/assembled/English_Your_Way_B1B_POOL_N9_TIP_SCREENS.wav` | 335.754秒 | `9c7a1d6341c6dfc9d07b2ca8d435b66bb2b80b287ca5c2e83603c4bcb5b673ca` | 無し | **FINAL USER APPROVED**(2026-09-01初回承認、2026-09-02再確認) |

- A2 Key Phrase構成: 1=guilt tipping(既存asset)、2=default(Trial 21 Attempt 4のone-off固定asset)、3=push back(既存asset)、4=a catch(function-word reduction適用版、2026-09-02反映)、5=starting point(既存asset)
- Article lineage: `article.md`(A2/B1Bとも)は`sc.split_article_text()`独立再導出ハッシュと`parts.json`の8項目全一致を確認済み(OPEN-101)
- User Listening Artifact(最新): https://claude.ai/code/artifact/53a57e1a-ec73-40bd-ad5f-c89ada7dabcb

## 3. User Final Approval

- **No.9 A2 = FINAL USER APPROVED**(2026-09-02、ER-010-NO9-FINAL-APPROVAL-CLOSEOUT-AND-FULL-STATUS-AUDIT-28)。function-word reduction適用後の「a catch」・`default`のone-off固定assetを含む最終完成音声を対象とする。
- **No.9 B1 = FINAL USER APPROVED**(2026-09-01初回承認[ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18]、2026-09-02の本Closeoutで再確認・維持)。

## 4. No.9関連 全項目Status一覧(Final Status Table)

状態は指示書§6の正式status語彙(REJECTED/VALIDATED/USER_DECISION_REQUIRED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIRED/DEFERRED-NON-BLOCKING/RESOLVED-CLOSED/SUPERSEDED/ONE-OFF-USER-APPROVED/NOT_APPLICABLE)を使用する。

### A. Article / Writer / QA

| 項目 | 分類 | 何が目的・問題だったか | Trial結果 | User Decision | 最終Status | Production実装 | Runtime evidence | CURRENT_SPEC | DECISION_LOG | OPEN_ITEMS | Git |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Ledger Deviation Checker v2 | Checker再設計 | 過剰検知(paraphrase等をMAJOR誤判定) | 9/9危険fixture検知維持、B1 3→0/A2 3→1 MAJOR | 正式採用 | PRODUCTION_WIRED | `run_deviation_check()` v2 | No.9実データ2回連続LEDGER_COMPLIANT | ✓行あり | ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02 | — | e7c35a6 |
| Human Review Lock STOPPED承認確認漏れ | バグ修正 | `_segment_gate_status()`がSTOPPED状態を承認確認対象外にしていた | — | ユーザー承認方針確認の上修正 | RESOLVED/CLOSED | `_segment_gate_status()` | 既存回帰テストPASS維持 | ✓行あり | ER-009-N1-AUDIO-STAGE-01 | — | 24c3a18 |
| Key Phrase括弧禁止(本番経路欠落) | バグ修正 | research10専用moduleのみ実装、本番共有validatorに未実装 | test 3件追加 | 修正実施 | PRODUCTION_WIRED | `validate_min_unit_selection()` | 既存test 144件PASS | ✓行あり(2行) | ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03 | — | 678f38e |
| Topic Pool No.10〜20更新 | データ更新 | No.9実態反映・ユーザー指定リストへ更新 | — | 正式反映 | DECIDED | `POOL_TOPIC_MASTER.md` | — | 対象外(別ファイル) | ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03 | — | 678f38e |
| Writer品質原因切り分け(Meaning First等) | Trial診断 | Point Two survey readout調の原因特定 | 6/6 LEDGER_COMPLIANT、仮説A確定 | Production配線せず | VALIDATED→SUPERSEDED | 配線なし(Trial限定) | Trial診断のみ | 対象外 | ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03 | OPEN-91(→REJECTED) | 678f38e |
| Diagnostic Full Retry | 新機構 | Point Overlap flag時の単純全文retryが浅い | Household実発火確認、A/B比較3/3 vs 0/3でDiagnostic採用 | 正式採用 | PRODUCTION_WIRED | `build_diagnostic_retry_prompt()` | Household実発火(overlap 0.414→収束) | ✓行あり(302行埋込) | ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14 | — | 4063e3f, ca82fce, 94ec819 |
| Meaning First(独立原則) | Writer原則候補 | Storytelling Firstと重複 | — | REJECTED(Storytelling First内で充足) | REJECTED | 未実装 | — | 対象外 | ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06 | OPEN-91 RESOLVED/CLOSED | 0d2b634 |
| Storytelling First | Writer原則 | 調査レポート調の解消 | No.9実データでDiagnostic Full Retry実発火・収束確認 | APPROVED_FOR_PRODUCTION | PRODUCTION_WIRED | `COMMON_BLOCK_TEMPLATE` | No.9 A2 Point One 0.464→0.219(retry後) | ✓行あり | ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06 | OPEN-95 RESOLVED/CLOSED | 0d2b634 |
| No Jargon | Writer原則 | 専門用語(regression discontinuity等)の平易化 | 同上 | APPROVED_FOR_PRODUCTION | PRODUCTION_WIRED | `COMMON_BLOCK_TEMPLATE` | 同上 | ✓行あり | ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06 | OPEN-90 RESOLVED/CLOSED(上流解決) | 0d2b634 |
| Evidence-bounded Interpretation | Writer原則 | 解釈文のscope/causality/certainty逸脱防止 | Trial-05で考案、Dangling状態から正式化 | APPROVED_FOR_PRODUCTION | PRODUCTION_WIRED(範囲外限界を実データ2回確認) | `COMMON_BLOCK_TEMPLATE` | Evidence説明文自体のscope拡張は対象外という限界を確認 | ✓行あり | ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09 | — | fe1f2a3 |
| Hook-aware Deviation Checker | Checker拡張 | 語りかけ文の過剰検知緩和 | 危険fixture 3種で偽陰性無し | APPROVED_FOR_PRODUCTION | PRODUCTION_WIRED | `run_deviation_check(hook_aware=True)` | No.9タイトル"Always"を正しくMAJOR判定(Hookでも緩和対象外) | ✓行あり | ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09 | — | fe1f2a3 |
| Local Rewrite(単発) | 局所修正機構 | MAJOR検出時の文単位修正 | No.9でAttempt1解消 3件実証 | APPROVED_FOR_PRODUCTION | SUPERSEDED(→Loop化) | `er010_ledger_local_rewrite_09.py` | No.9 A2でMAJOR3件Attempt1解消 | ✓行あり(Loop化前提として記載) | ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09 | — | fe1f2a3 |
| Local Rewrite Loop(最大3cycle) | 局所修正機構 | 単発Local Rewriteが検知漏れの新規MAJORに対応不可だった | cycle2分岐を回帰testで実証、No.9新候補はcycle1で収束 | ユーザー正式拡張指示 | PRODUCTION_WIRED | `MAX_REWRITE_CYCLES`ループ | No.9 A2 cycle1でMAJOR1件解消・LEDGER_COMPLIANT | ✓行あり | ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10 | OPEN-98 CLOSED/REMOVE | 98994c7 |
| Numeric Compression(Evidence Compression Editor側) | 既存仕様確認 | Editor側圧縮機能の起源確認 | Case A確定(2026-08-26から既存) | 変更なし | PRODUCTION_WIRED(既存のまま、No.9で再確認) | 既存 | — | 既存行のまま(追記不要と判断) | ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09 | — | fe1f2a3 |
| Key Phrase専門語回避基準(独立spec) | spec候補 | 高度専門語の優先度回避を独立仕様化するか | — | 新規spec不要、No Jargonで上流解決 | RESOLVED/CLOSED | 未実装(不要と判断) | — | 対象外 | ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09 | OPEN-90 | fe1f2a3 |
| Formatting禁止(絵文字・太字Markdown) | Writer原則+fail-safe | ER-010-06版でemoji/bold再発、既存QA gate範囲外 | ER-010-11版で0件確認 | ユーザー正式決定 | PRODUCTION_WIRED(**2026-09-02、CURRENT_SPEC記録漏れを本Closeoutで補完**) | prompt禁止+`normalize_article_formatting()` | ER-010-11版A2/B1B両方emoji/bold 0件 | ✓行あり(**今回追加**) | ER-010-NO9-FORMAT-PRODUCTION-AND-FACT-REVIEW-11 | OPEN-99 RESOLVED/CLOSED | 32be1c6 |
| Fact Checker運用変更(FAIL=blocking/REVIEW_REQUIRED=advisory) | Policy変更 | REVIEW_REQUIREDが過剰にNo.9をSTOPさせていた+FAILの未block実装漏れ発見 | mock4件PASS | ユーザー正式決定 | PRODUCTION_WIRED | `run_one_pattern()`のFAIL分岐追加 | No.9実データでREVIEW_REQUIRED非block確認 | ✓行あり(Fact Safety行に統合) | ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12 | OPEN-97 RESOLVED/CLOSED | 6e8a534 |
| Point Two数字羅列問題(Numeric Compression対象範囲) | 診断のみ | [F-011]/[F-012]/[F-013]異なる意味の数字5値が圧縮対象外 | Case 2 SPEC_TOO_WEAK確定 | 現時点で追加対応せず | DEFERRED/NON-BLOCKING | 未実装(意図的) | — | 対象外(仕様変更なしのため) | ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12 | OPEN-100 | 6e8a534 |
| EVIDENCE_COMPRESSION_BLOCK(方式B、Compression-aware Writer) | 既存不使用コード再確認 | Point専用の強い数字圧縮指示が眠っている | — | 再有効化しない(過去にcausal drift実証済み) | REJECTED(既存判断維持) | コード存在するが`evidence_compression=False`既定のまま不使用 | — | 対象外 | ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12 | — | 6e8a534 |

### B. Article → Audio lineage

| 項目 | 分類 | 何が目的・問題だったか | Trial結果 | User Decision | 最終Status | Production実装 | Runtime evidence | CURRENT_SPEC | DECISION_LOG | OPEN_ITEMS | Git |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Article/Audio lineage不整合 | バグ調査 | diagnostic版とProduction正式pathが分岐、B1B本文が安全確認済みテキストと不一致 | Case B確定→正式pathの単一実行で解消 | 正式path実行を承認 | RESOLVED/CLOSED | `run_writer_stage_baseline()`正式OUT_DIR実行 | A2/B1Bとも8項目ハッシュ完全一致確認 | ✓行あり(次項と統合) | ER-010-NO9-ARTICLE-AUDIO-PRODUCTION-WIRING-14 | OPEN-101 | f1ee48e |
| Article→Audio Production SSOT明文化 | Governance | diagnostic検証後の正式反映手順が文書化されていなかった | — | 正式明文化 | DECIDED | CURRENT_SPEC.md新規行 | — | ✓行あり | ER-010-NO9-ARTICLE-AUDIO-PRODUCTION-WIRING-14 | OPEN-101 | f1ee48e |

### C. Audio / TTS / Validator

| 項目 | 分類 | 何が目的・問題だったか | Trial結果 | User Decision | 最終Status | Production実装 | Runtime evidence | CURRENT_SPEC | DECISION_LOG | OPEN_ITEMS | Git |
|---|---|---|---|---|---|---|---|---|---|---|---|
| compound-number TTS-safe bug(`tts_safe_number_words_en()`) | バグ修正 | ハイフン複合数の後半のみ誤って算用数字化、canonical text破損 | 診断→修正承認 | ユーザー正式承認 | RESOLVED/CLOSED | 正規表現に`(?<!-)`追加 | A2/B1とも`point_two`が1回目でPASS(修正前3回ともSTOPPED) | 変更不要と判断(実装バグのみ) | ER-010-NO9-TTS-NUMBER-WORDS-BUGFIX-AND-AUDIO-RETRY-16 | OPEN-102 | 5aec5e3 |
| Japanese meaning validator kana bug(`protected_check_ja()`) | バグ修正 | 漢字canonical×全ひらがなASRで語境界分断・偽陰性 | 回帰fixture35件PASS | ユーザー承認のうえ`approve_regenerate()` | RESOLVED/CLOSED | 全文読み比較の安全網追加 | meaning_4が実際にPASS | 変更不要(実装バグのみ) | ER-010-NO9-A2-KEYPHRASE-AUDIO-ISSUES-103-104-17 | OPEN-104 | 05647b6 |
| Key Phrase Minimal instruction(基本文言) | 既存仕様の踏襲 | Full Story向け重量級instructionが極小textに不適合 | Trial-19でopt out VALIDATED/default REJECTED(単発) | 一般化を承認 | PRODUCTION_WIRED | `KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT` | 複数実TTSで確認 | ✓行あり | ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19 | OPEN-103(`default`除く) | d8579ac |
| Key Phrase Minimal→English Lock retry構成(合計最大4) | Production配線 | 一般Key Phrase向けretry構成の正式化 | Case A実TTS+境界モックで遷移確認 | ユーザー正式採用 | PRODUCTION_WIRED | `generate_key_phrase_component_verified()` | push back Minimal Attempt2 PASS、モックでFallback実遷移確認 | ✓行あり | ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22 | OPEN-103(`default`除外) | 8503226 |
| review_lock二重会計バグ(guarded_generateネスト) | バグ修正 | 同一TTS試行がcumulative_tts_attemptsへ2重記録 | 回帰test2件追加 | 純粋バグとして修正 | RESOLVED/CLOSED | reentrancy guard(`_ACTIVE_GUARDED_OUT_PATHS`) | cumulative=6(修正前)→3(修正後)を実確認 | ✓行あり(Human Review Cost Guard行に統合) | ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19 | OPEN-105 | d8579ac |
| `default` Minimal-only Trial | Trial(default固有) | duration anomaly解消狙い | 単発試行でTTS_FAILURE("Dieselt")、Mini-Trial 20-R2で3/3誤発音再現 | Production採用せず | REJECTED(`default`固有の解決策として) | 未採用 | — | 対象外 | ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-MINI-TRIAL-20-R2 | OPEN-103 | 107cd9c |
| `default` English Lock Trial | Trial(default固有) | 非英語発話の解消狙い | 4/4attempt不合格 | Production採用せず | REJECTED(`default`固有の解決策として。**一般Key Phrase向けEnglish Lockとは別目的、混同しないこと**) | 未採用(`default`には) | — | 対象外 | ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21 | OPEN-103 | b9fef10 |
| `default` one-off fixed asset(Trial 21 Attempt 4) | one-off例外 | 一般仕様で解決不能な`default`をNo.9限定で回避 | machine判定はTTS_FAILUREのまま | ユーザー正式採用(2026-09-01) | **ONE-OFF USER APPROVED**(2026-09-02完成音声最終承認によりA2側は完全解消) | `human_approved_segments.json`経由でGate通過 | 完成episode中で実ASR再確認("2. デフォルト..."正しく認識) | 対象外(No.9限定例外、一般仕様は無変更) | ER-010-NO9-A2-ATTEMPT4-ONEOFF-FINAL-AUDIO-25 | OPEN-103(恒久課題は継続) | 30d4f84 |
| `default`固定音声資産探索(本文抽出候補3件) | 候補提示 | Trial 21以外の代替素材の探索 | 3候補ともProduction ASRに文頭誤認識、断定不可 | 不採用 | REJECTED(採用されず) | 未採用 | — | 対象外 | ER-010-NO9-A2-DEFAULT-FIXED-ASSET-FINALIZATION-23-R1 | OPEN-103 | 1c3940f |
| Function-word/article reduction(Key Phrase英語pronunciation) | 新規safeguard | 「a catch」の冠詞"a"過剰強調 | Trial 26でAttempt1 PASS、「a」0.28→0.07秒 | ユーザー正式採用(一般Production仕様) | PRODUCTION_WIRED | `KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`(CORE+SUFFIX) | 実Production path 7fixture全PASS、「a catch」0.08秒(旧比29%) | ✓行あり | ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1 | OPEN-106 RESOLVED/CLOSED | b209ddb |
| 「a catch」冠詞強調Trial(隔離、Production未配線時点) | Trial | 診断+隔離Trial | Attempt1 machine PASS | 良好、一般採用はユーザー判断へ | VALIDATED→SUPERSEDED(27-R1で一般採用) | Trial専用script | Trial版envelope改善確認 | 対象外(Trial時点) | ER-010-NO9-A2-KEYPHRASE-ARTICLE-REDUCTION-DIAGNOSTIC-AND-TRIAL-26 | OPEN-106(→CLOSED) | a4b4b63 |
| Key Phrase発音品質(3条件、既存Cross-level仕様) | 既存仕様(No.9由来ではない) | Meaning/Phoneme integrity/Phrase grouping | — | 既存DECIDED(2026-08-12) | DECIDED(No.9作業全体の土台として継続利用) | 既存 | — | ✓既存行 | (No.9以前、Cross-level仕様) | — | (No.9以前) |

### D. Governance / PM

| 項目 | 分類 | 何が目的・問題だったか | Trial結果 | User Decision | 最終Status | Production実装 | Runtime evidence | CURRENT_SPEC | DECISION_LOG | OPEN_ITEMS | Git |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Audio+Full Script提示ルール適用範囲拡張 | Governance | 単発試聴リンクにも全script掲載を明示適用 | — | ユーザー正式指示 | DECIDED | Artifact構築手順 | B1 Artifact是正で反映 | ✓行あり(既存2026-08-29行への追記) | ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18 | — | 9f036a6 |
| 仕様Lifecycle・Dangling Reference Check正式導入 | Governance | Trial結果とProduction採用の混同事故(OPEN-95)の再発防止 | — | ユーザー正式指示 | DECIDED | PROJECT_INDEX.md「仕様Lifecycle」節 | 本Closeout自体がこのCheckを実施 | 対象外(PROJECT_INDEX.md) | ER-010-N1-SPEC-LIFECYCLE-PRODUCTION-GATE-04 | OPEN-95 | 77e2b02 |
| No.9 A2 Final Approval | User Decision | A2完成音声の最終試聴承認 | — | **FINAL USER APPROVED**(2026-09-02) | FINAL USER APPROVED/CLOSED | — | 354.162秒、sha256確認済み | 対象外 | ER-010-NO9-FINAL-APPROVAL-CLOSEOUT-AND-FULL-STATUS-AUDIT-28 | OPEN-103更新 | (本commit) |
| No.9 B1 Final Approval | User Decision | B1完成音声の最終試聴承認(再確認) | — | **FINAL USER APPROVED**(2026-09-01初回、2026-09-02再確認) | FINAL USER APPROVED/CLOSED | — | 335.754秒、sha256確認済み | 対象外 | ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18 / 本Closeout | — | (本commit) |

---

## 5. Production Wired仕様一覧

| Specification | Production initial | Retry/Fallback | Runtime | Tests | SSOT | Git | Final Status |
|---|---|---|---|---|---|---|---|
| Ledger Deviation Checker v2 | `run_deviation_check()` | 適用外(1回判定) | No.9実データ2回連続確認 | 受入test6件+fixture9件 | ✓ | e7c35a6 | PRODUCTION_WIRED |
| Key Phrase括弧禁止 | `validate_min_unit_selection()` | 適用外 | — | 3件追加、144件PASS | ✓ | 678f38e | PRODUCTION_WIRED |
| Diagnostic Full Retry | `run_one_pattern()`内 | 記事全体retry最大2 | Household実発火 | 3/3合格、A/B比較 | ✓(302行) | 4063e3f他 | PRODUCTION_WIRED |
| Storytelling First | `COMMON_BLOCK_TEMPLATE` | 適用外(prompt原則) | No.9実データ | regression1953/1957 | ✓ | 0d2b634 | PRODUCTION_WIRED |
| No Jargon | `COMMON_BLOCK_TEMPLATE` | 適用外 | No.9実データ | 同上 | ✓ | 0d2b634 | PRODUCTION_WIRED |
| Evidence-bounded Interpretation | `COMMON_BLOCK_TEMPLATE` | 適用外 | No.9実データ2回 | test19件 | ✓ | fe1f2a3 | PRODUCTION_WIRED |
| Hook-aware Deviation Checker | `run_deviation_check(hook_aware=True)` | 適用外 | No.9タイトルMAJOR判定確認 | 同上test群 | ✓ | fe1f2a3 | PRODUCTION_WIRED |
| Local Rewrite Loop(最大3cycle) | `run_one_pattern()`内whileループ | cycle最大3、文単位最大3attempt | No.9 cycle1収束実証、cycle2は回帰testで実証 | test21件(+3) | ✓ | 98994c7 | PRODUCTION_WIRED |
| Formatting禁止(絵文字・太字) | `COMMON_BLOCK_TEMPLATE`+`normalize_article_formatting()` | 適用外(fail-safe2箇所) | ER-010-11版0件確認 | test6件 | ✓(**今回追加**) | 32be1c6 | PRODUCTION_WIRED |
| Fact Checker policy(FAIL blocking) | `run_one_pattern()`FAIL分岐 | 適用外 | No.9実データREVIEW_REQUIRED非block確認 | mock4件 | ✓ | 6e8a534 | PRODUCTION_WIRED |
| Key Phrase Minimal→English Lock retry | `generate_key_phrase_component_verified()` | Primary最大2→Fallback最大2(計4) | 実TTS+境界モック確認 | 18件 | ✓ | 8503226 | PRODUCTION_WIRED |
| Function-word/article reduction | `KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX` | Primary/Fallback両方(自動継承) | 実Production 7fixture | 27件(既存18+新規9) | ✓ | b209ddb | PRODUCTION_WIRED |
| review_lock reentrancy guard | `guarded_generate`/`guarded_generate_with_language_arg` | 適用外 | cumulative_tts_attempts実測確認 | 2件追加(15件中) | ✓ | d8579ac | RESOLVED/CLOSED(bug fix) |
| Human Review Lock STOPPED承認確認 | `_segment_gate_status()` | 適用外 | — | 既存回帰維持 | ✓ | 24c3a18 | RESOLVED/CLOSED(bug fix) |
| compound-number TTS-safe bug fix | `tts_safe_number_words_en()` | 適用外 | A2/B1 point_two 1回目PASS | test16件 | 記述不要(実装バグのみ) | 5aec5e3 | RESOLVED/CLOSED(bug fix) |
| Japanese meaning validator kana bug fix | `protected_check_ja()` | 適用外 | meaning_4 PASS実証 | fixture35件 | 記述不要(実装バグのみ) | 05647b6 | RESOLVED/CLOSED(bug fix) |

## 6. REJECTEDになったTrial一覧

| Trial | 狙い | 結果 | Rejection reason | 後続で何に置換されたか |
|---|---|---|---|---|
| Meaning First(独立原則) | Point Two等のsurvey readout調解消 | 6/6 LEDGER_COMPLIANT達成、有効ではあった | Storytelling First内の要素で十分とユーザー判断、独立ruleは重複と判断 | Storytelling First(APPROVED_FOR_PRODUCTION) |
| `default` Minimal-only Trial | duration anomaly解消 | duration anomaly解消したがASRが"Dieselt"(単発)、Mini-Trial 20-R2で3/3 content失敗を再現(デフォルト/デフォルト/默认) | content-accuracy失敗(非英語発話)が新たな失敗モードとして残存 | English Lock Trial(次項) |
| `default` English Lock Fallback Trial | 非英語発話の解消 | Minimal2回+English Lock2回、4/4とも不合格(デフォルト×2/defaut/デフォルト) | English Lockを追加しても非英語発話モードが再発 | 一般仕様(Minimal→English Lock)は`default`以外へ正式採用、`default`自体はone-off固定asset(Attempt 4)へ切替 |
| `default`固定音声資産探索(本文抽出3候補) | 新規TTS無しでの代替素材確保 | ローカルASRは"default"検出も、Production ASRが文頭に誤認識語を付加、断定不可 | 判断材料不足でユーザーへ提示のみ、採用されず | Trial 21 Attempt 4のone-off採用(前々からの候補) |
| EVIDENCE_COMPRESSION_BLOCK(方式B)再有効化検討 | Point Two数字羅列の直接抑制 | 過去にcausal drift副作用が実証済み(No.7 B1候補) | Fact safety上のリスクが数字圧縮効果より優先 | 方式C(Evidence Compression Editor)を維持、Point Two自体はOPEN-100としてDEFERRED |

## 7. RESOLVED/CLOSED bug一覧

| Bug | 発見経緯 | Root Cause | 修正 | Regression | Open Item |
|---|---|---|---|---|---|
| Human Review Lock STOPPED未承認確認 | No.9 Audio Stage実行中に発見 | `_segment_gate_status()`がSTOPPEDを承認確認対象外にしていた | STOPPEDを承認確認対象へ追加 | 既存gate test全PASS維持 | (専用ID無し、本エントリ内で解消) |
| Key Phrase括弧禁止の本番経路欠落 | ER-008-N8-FINAL-QA-HARDENING-21の誤記録発覚 | research10専用moduleのみに実装、本番共有validatorには未実装 | `validate_min_unit_selection()`へ括弧検知追加 | 3件追加、144件PASS | — |
| review_lock guarded_generateネスト二重会計 | OPEN-103監査中に偶然発見 | 内側/外側2つのguarded decoratorが同一試行を2回record_outcome | reentrancy guard追加 | 2件追加(15件PASS) | OPEN-105 RESOLVED/CLOSED |
| compound-number TTS-safe変換バグ | OPEN-102診断 | `\b`がハイフンの両側で成立、複合数後半のみ誤変換 | 否定後読み`(?<!-)`追加 | 16件追加PASS | OPEN-102 RESOLVED/CLOSED |
| 日本語ASR Validator script-mismatch window不整合 | OPEN-104診断 | 漢字canonical×全ひらがなASRで局所padding窓が語境界からずれる | 全文読み比較の安全網追加 | fixture35件PASS | OPEN-104 RESOLVED/CLOSED |

## 8. one-off exception一覧

| 対象 | 内容 | 理由 | 一般化しないことの明記 |
|---|---|---|---|
| `default`(No.9 A2 kp2_en) | Trial 21 ENGLISH_LOCK attempt=2(通し4回目)をNo.9 A2限定で採用。machine validator上は`TTS_FAILURE`のまま(書き換えず) | 一般Key Phrase retry仕様(Minimal→English Lock計4回)でも解決しない非決定的provider挙動のため、ユーザーが個別に試聴・承認 | CURRENT_SPEC.mdの「`default`個別例外」行に明記済み。他Key Phraseへは一切適用しない。将来同種の語が発生した場合も、まず一般仕様(Minimal→English Lock)を適用し、それでも解決しない場合のみ個別one-off検討 |

## 9. Runtime Evidence Summary

- Ledger Deviation Checker v2: No.9 A2/B1で2回連続`LEDGER_COMPLIANT`実測
- Diagnostic Full Retry: Household regressionテーマでoverlap 0.414→retry実発火を実測(No.9本番記事では初回PASSのため自然発火せず、機構自体は健全)
- Local Rewrite Loop: No.9 A2でMAJOR1件→cycle1・Attempt1で解消、`LEDGER_COMPLIANT`到達を実測
- Key Phrase Minimal→English Lock: "push back"実TTSでMinimal Attempt2 PASS実測、モックでFallback実遷移確認
- Function-word/article reduction: 実Production pathで7fixture(a catch/a chance/an idea/the answer/guilt tipping/push back/starting point)全PASS実測、「a catch」duration 1.011秒・「a」区間0.08秒実測
- compound-number bugfix: A2/B1の`point_two`が修正後1回目でPASS実測(修正前は3回ともSTOPPED)
- meaning_4 kana bugfix: 修正後実際にPASS実測
- No.9 A2/B1 Assembly: 354.162秒/335.754秒、いずれもclipping無しを実測

## 10. SSOT / Git

- CURRENT_SPEC.md: No.9由来の新規行17件相当(統合行含む)、うち「Formatting禁止」1行は本Closeoutで記録漏れを補完
- DECISION_LOG.md: No.9関連エントリ25件(本Closeoutエントリ含む)
- OPEN_ITEMS.md: No.9由来Open Item 17件(OPEN-90〜106、うちOPEN-98は行削除)、現在残るのはOPEN-100・OPEN-103(いずれもDEFERRED/NON-BLOCKING)のみ
- Git: 本Closeoutのcommit SHAは完了報告参照。No.9関連commit historyは24件超(`git log --oneline | grep -iE "no9|n1-"`で確認可能)

## 11. Final Status Table(要約)

| 対象 | Final Status |
|---|---|
| No.9 A2 | FINAL USER APPROVED / CLOSED |
| No.9 B1 | FINAL USER APPROVED / CLOSED |
| No.9 DEVELOPMENT | CLOSED WITH DEFERRED OPEN ITEMS(OPEN-100, OPEN-103恒久課題) |

## 12. 将来再検討Trigger

- **OPEN-100(Point Two数字羅列)**: Editorial Type導入後、survey/numeric-heavy記事の発生率を見て(1)現状維持、(2)Point専用Numeric Compression再設計、(3)Spoken-first原則DのPoint専用strict適用、のいずれかを再評価
- **OPEN-103恒久課題(Gemini TTSの`default`誤発音)**: 他記事で同種の短い孤立語Key Phraseが再発した場合、一般仕様(Minimal→English Lock)をまず適用し、解決しなければNo.9同様の個別one-off対応を検討。`default`自体の一般解決手段は無し(provider挙動)
- **review_lockの二重デコレータ構造**: reentrancy guardで実害は防止済みだが、根本の「2つのguarded_generate系デコレータが1関数を二重にwrapする」構造自体は残る(technical debt、下記13節参照)
- **B1B audit trail不整合(2026-09-01観測、原因未特定)**: OPEN-101の正式path再実行により実務上は解消したが、Point Overlap Article Retry発火時のarticle.md書き込みタイミングの原因自体は未特定のまま。同種の事象が再発した場合は本件を参照

## 13. Technical Debt(報告のみ、今回refactorなし)

- **review_lock二重デコレータ**: `generate_key_phrase_component_verified()`(`@guarded_generate`)が内部で`generate_narration_snippet_verified_strict()`(`@guarded_generate_with_language_arg`)を直接呼ぶネスト構造自体は解消していない。reentrancy guardで二重会計という実害は防止済みだが、構造そのものの整理(片方のデコレータを外す等)は今回のスコープ外
- **EVIDENCE_COMPRESSION_BLOCK(方式B)未使用コード**: `evidence_compression`引数が常に`False`で呼ばれ続けており、方式Bのprompt定義自体はコード上に眠ったまま。再有効化しない方針だが、デッドコードとしての整理は今回未実施
- **B1B article.md書き込みタイミングの原因未特定**: 12節参照。実害は解消済みだが根本原因の特定は残課題

## 14. Cost / Latency影響

- Key Phrase英語Component: 一般仕様で最大4回(旧3回)、function-word reduction追加後も同上限(instruction文言追加のみ、attempt数上限は無変更)
- Diagnostic Full Retry: 発火時のみ追加費用(¥0.99〜¥1.37/記事、Household実測ベース)。No.9本番記事では発火せず追加費用なし
- Local Rewrite Loop: 発火時のみ追加費用。No.9 A2はcycle1のみで収束(Attempt1解消、追加費用は文単位1〜数回のLLM呼び出し分)
- Fact Checker policy変更: FAIL時は後続のLedger Deviation Check等をスキップするため、むしろコスト削減方向
- Formatting正規化: ローカル処理のみ、追加API費用なし

## 15. No.10以降に自動適用される仕様

Storytelling First・No Jargon・Evidence-bounded Interpretation・Hook-aware Deviation Checker・Local Rewrite Loop・Ledger Deviation Checker v2・Formatting禁止(絵文字・太字)・Fact Checker policy(FAIL=blocking/REVIEW_REQUIRED=advisory)・Key Phrase括弧禁止・Diagnostic Full Retry・Human Review Lock STOPPED承認確認・review_lock reentrancy guard・Key Phrase Minimal→English Lock retry構成・Function-word/article reduction — いずれも`COMMON_BLOCK_TEMPLATE`または共有Production moduleへの実装であり、No.9限定ではなく今後の全テーマ・全記事へ自動適用される。

## 16. No.9限定one-off(一般化してはいけないもの)

- `default`(No.9 A2 kp2_en)のTrial 21 Attempt 4固定asset。8節参照。
