管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01(OPEN-517)。Opus必須レビュー(PM_GOVERNANCE 11-3 条件C: 重要変更=既存ASR最終ゲートの挙動変更のProduction適用提案前)。読み取り専用。日本語で報告。

## 背景
承認済み安全条件(CURRENT_SPEC.md:2855「最終ANDゲート: 採用しようとする転写…すべてに値ガードDIFF・否定差が無いことを独立に再確認する。重大内容差(数値・否定)を警告だけで解放する仕様にはしない」)に対し、現行実装は`PHONETIC_MATCH`/`READING_RESOLVED_MATCH`に`equivalence_basis="READING_MATCH"`を付与し(er007_ja_secondary_asr_01.py:427,603)、er078_asr_unified_judge_01.py:68-73の`APPROVED_EQUIVALENCE_BASES`に含まれるため:526-530で最終ゲートがskipされる。実音声で「89,000 vs 原稿8,900」「三日間↔三日目」「3~5日↔35日」等がPASSする誤PASSが確認された(N-3 16/30件のうち値・否定矛盾型はこの経路)。skipの出自はSonnet実装時の設計判断(IMPLEMENTATION_02b.md:19)で、個別のユーザー承認原文は未発見。

Sonnet成果物(C:\Users\tensh\eigo-radio\docs\research\JA-ASR-FALSE-NG-ROOT-CAUSE-01\): OPEN517_DESIGN_01.md / OPEN517_PREREGISTERED_01.md / OPEN517_EVAL_01.md / OPUS_REVIEW_REQUEST_01_OPEN517.md / proto_value_gate_fix_03.py / eval_open517_api0_03.py(v1/v2 protoは不合格版として凍結保持)。
関連Production code(無変更): er078_asr_unified_judge_01.py、er078_asr_value_guard_01.py(`is_irregular_sig`等)、er007_ja_asr_validator_01.py(:441,502)、er007_ja_secondary_asr_01.py、er066系Trialの期待読み表`_cands`。

是正案: F1=READING_MATCHのPrimary PASSにも既存の最終ゲート分岐を適用(値DIFF・否定差=NG_PROTECTED、AMBIGUOUS=P3 Secondaryへ降格。Production差分はAPPROVEDから"READING_MATCH"を除く1行)。F2(必須)=相手側atom(値n,助数詞c)の期待読み(er066 `_cands`)と完全一致するかな列だけをatom表層へ置換してから値ガードへ渡す汎用規則(閉集合除外なし。「一番/一度」は等価表記統一で扱い「一番↔二番」の値違いは隠さない。期待読みにない「さんにち」「いちふん」は統一されずNG)。適用はPrimary PASS(READING_MATCH)の最終ゲートのみ。
API 0再評価(771件、2回実行で決定的): 正常attemptのNG化/降格0(143件)、既知負例9/9がPASS以外(NG_PROTECTED 8・DEMOTE 1)、月題転写の追加誤PASS「8000九百本超」も検出、非READING_MATCH経路の変化0、NG→PASS 0、警告喪失0。判定変化13件(F1 PASS→NG 10、F2警告追加3=みっかかん/しがつ/しちがつ PASS→PASS_WITH_WARNING非ブロッキング)。版履歴: F2 v1(閉集合)は正例6件誤NG、v2(期待読み表)は警告喪失8・P1解除6の副作用、v3で全基準合格(同一コーパスで再設計=未知データ汎化未確認)。取りこぼし(値ガードで原理的に検出不能): 同形異音7・助詞誤読3・「七晩↔七番」(「晩」が助数詞表になくUNKNOWN素通し)・N3-07(Candidate E近音=OPEN-333へ)・N3-24。影響: JA経路X/Z/Y/legacy共通、PASS→NG_PROTECTEDで次slotのTTS再生成(retry消費)、実attempt 421でのretry/HR増0。

## レビューしてほしい論点
1. F1が「承認済み安全条件への回復(不具合是正)」として妥当か、それとも承認済み挙動(READING_MATCH skip)の変更=ユーザー承認事項か。IMPLEMENTATION_02b:19の設計判断の性格(ユーザー承認の有無)の読み。
2. F2(期待読みによるかな→atom統一)の安全性: 誤って値違いを等価にしてしまう経路(例: 期待読み表の衝突、連濁・音便、複数atom並び、否定語の近接)はないか。「晩」等の助数詞表外のUNKNOWN素通しを是正に含めるべきか(範囲拡大のリスク)。
3. 同一コーパスでの再設計(v1→v3)による過適合の懸念と、適用前に必要な追加検証(未知データ、X/Z/Y別の実attempt、legacy)の必要十分な範囲。
4. 運用影響: PASS→NG_PROTECTEDで再生成が増える条件、HR Lock到達率、既存run dirの再判定(過去公開物の遡及要否=遡及しない前提の妥当性)。
5. Production適用の手順(期待読み表の移設+parity test、`unify_kana_numerals`追加、judge最終ゲートでのF2適用、既存test更新、回帰)の抜け。F2の警告3件(PASS→PASS_WITH_WARNING)を残すべきか。
6. OPEN517_PREREGISTERED_01の基準の過不足。

## 出力形式
必須修正(M-n)/推奨(R-n)/問題なし確認(C-n)/ユーザー確認が必要と考える点(理由付き)/Production適用着手可否の総合所見。断定できない点は「未確認」。